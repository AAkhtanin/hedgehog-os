from __future__ import annotations

from dataclasses import replace
from pathlib import Path

from hedgehog.domains.airline import ticket_purchase_corridor_runtime_v01 as runtime
from hedgehog.domains.airline import ticket_purchase_corridor_v01 as contracts


def _valid_report() -> runtime.AirlineTicketPurchaseCorridorRunReportV01:
    return runtime.collect_airline_ticket_purchase_corridor_state_machine_v01()


def _fixtures() -> dict[str, object]:
    return runtime._build_valid_fixture_bundle_v01()


def _b_context() -> contracts.AirlineTicketPurchaseContractContextV01:
    return contracts.AirlineTicketPurchaseContractContextV01(
        transaction_id=contracts.TRANSACTION_ID,
        offer_id="offer:mock_airline_al:PAR-LIM:002",
        hold_id="hold:mock_airline_al:002",
        amount=806,
        currency=contracts.CURRENCY,
        route_ref=contracts.ROUTE_REF,
        passenger_ref=contracts.PASSENGER_REF,
        max_amount=contracts.MAX_AMOUNT,
        merchant_ref=contracts.MERCHANT_REF,
    )


def _b_fixtures() -> dict[str, object]:
    fixtures = _fixtures()
    context = _b_context()
    fixtures["human_approval"] = replace(
        fixtures["human_approval"],
        selected_offer_id=context.offer_id,
    )
    fixtures["offer_packet"] = replace(
        fixtures["offer_packet"],
        offer_id=context.offer_id,
        amount=context.amount,
    )
    fixtures["hold_packet"] = replace(
        fixtures["hold_packet"],
        offer_id=context.offer_id,
        hold_id=context.hold_id,
        amount=context.amount,
    )
    fixtures["hold_receipt"] = replace(
        fixtures["hold_receipt"],
        offer_id=context.offer_id,
        hold_id=context.hold_id,
        amount=context.amount,
    )
    fixtures["purchase_intent"] = replace(
        fixtures["purchase_intent"],
        offer_id=context.offer_id,
        hold_id=context.hold_id,
        selected_amount=context.amount,
    )
    fixtures["authorization_ref"] = replace(
        fixtures["authorization_ref"],
        offer_id=context.offer_id,
        hold_id=context.hold_id,
        amount=context.amount,
    )
    fixtures["ticket_issue_intent"] = replace(
        fixtures["ticket_issue_intent"],
        offer_id=context.offer_id,
        hold_id=context.hold_id,
        amount=context.amount,
    )
    fixtures["ticket_receipt"] = replace(
        fixtures["ticket_receipt"],
        offer_id=context.offer_id,
        hold_id=context.hold_id,
        amount=context.amount,
    )
    return fixtures


def _run_with(**overrides: object) -> runtime.AirlineTicketPurchaseCorridorRunReportV01:
    fixtures = _fixtures()
    fixtures.update(overrides)
    return runtime._run_airline_ticket_purchase_corridor_state_machine_v01(
        fixtures,
    )


def _phase(
    report: runtime.AirlineTicketPurchaseCorridorRunReportV01,
    phase_id: str,
) -> runtime.AirlineCorridorPhaseResultV01:
    return next(phase for phase in report.phase_results if phase.phase_id == phase_id)


def test_valid_root_centered_corridor_state_machine_passes() -> None:
    report = _valid_report()

    assert report.final_status == runtime.STATUS_PASS
    assert report.failed_phase_id == ""
    assert report.return_to_root_id == ""
    assert report.validation_errors == ()
    accepted, errors = runtime.validate_airline_ticket_purchase_corridor_run_v01(
        report,
    )
    assert accepted is True
    assert errors == ()


def test_exact_five_phase_order_preserved() -> None:
    report = _valid_report()

    assert tuple(phase.phase_id for phase in report.phase_results) == (
        runtime.PHASE_AIRLINE_OFFER_HOLD,
        runtime.PHASE_CLIENT_PURCHASE_INTENT,
        runtime.PHASE_BANK_PAYMENT_AUTHORIZATION,
        runtime.PHASE_AIRLINE_TICKET_ISSUE,
        runtime.PHASE_CLIENT_COMPLETION,
    )
    assert report.counter_table["phase_count"] == 5


def test_all_states_use_one_transaction_id() -> None:
    report = _valid_report()

    assert report.transaction_id == contracts.TRANSACTION_ID
    assert all(
        phase.transaction_id == contracts.TRANSACTION_ID
        for phase in report.phase_results
    )
    assert all(
        transition.transaction_id == contracts.TRANSACTION_ID
        for transition in report.transitions
    )
    assert report.artifact_validation_summary["one_transaction_id"] == (
        contracts.TRANSACTION_ID
    )


def test_each_phase_has_side_specific_root_gate() -> None:
    report = _valid_report()

    assert _phase(report, runtime.PHASE_AIRLINE_OFFER_HOLD).relevant_root_id == (
        contracts.AIRLINE_ROOT_ID
    )
    assert _phase(report, runtime.PHASE_CLIENT_PURCHASE_INTENT).relevant_root_id == (
        contracts.CLIENT_ROOT_ID
    )
    assert _phase(report, runtime.PHASE_BANK_PAYMENT_AUTHORIZATION).relevant_root_id == (
        contracts.BANK_ROOT_ID
    )
    assert _phase(report, runtime.PHASE_AIRLINE_TICKET_ISSUE).relevant_root_id == (
        contracts.AIRLINE_ROOT_ID
    )
    assert _phase(report, runtime.PHASE_CLIENT_COMPLETION).relevant_root_id == (
        contracts.CLIENT_ROOT_ID
    )


def test_no_shared_or_fourth_root_created() -> None:
    counters = _valid_report().counter_table

    assert counters["shared_root_created_count"] == 0
    assert counters["fourth_root_created_count"] == 0
    assert counters["cross_root_authority_transfer_count"] == 0


def test_core_no_post_root_reasoning_validator_used_for_all_phases() -> None:
    report = _valid_report()

    assert report.counter_table["core_no_post_root_reasoning_validation_count"] == 5
    assert all(phase.core_corridor_guard_validated for phase in report.phase_results)


def test_core_domain_delegation_matrix_is_explicit() -> None:
    report = _valid_report()
    matrix = {row.check_id: row for row in report.core_domain_delegation_matrix}

    assert set(matrix) == {
        "no_post_root_reasoning",
        "corridor_deterministic_only",
        "root_phase_ownership",
        "ttl_and_expiry",
        "idempotency",
        "receipt_evidence_only",
        "airline_offer_hold_bindings",
        "airline_ticket_issue_bindings",
    }
    assert matrix["no_post_root_reasoning"].directly_delegated_to_core is True
    assert matrix["corridor_deterministic_only"].directly_delegated_to_core is True
    assert matrix["airline_offer_hold_bindings"].directly_delegated_to_core is False
    assert report.counter_table["core_delegated_check_count"] == 2
    assert report.counter_table["domain_projection_check_count"] == 6


def test_no_supplier_specific_core_fixture_used() -> None:
    report = _valid_report()

    assert report.counter_table["supplier_specific_core_fixture_used_count"] == 0
    source = Path(runtime.__file__).read_text(encoding="utf-8")
    assert "SUBJECT_" + "SUPPLIER_A" not in source
    assert "SUBJECT_" + "SUPPLIER_B" not in source
    assert "build_" + "supplier_a" not in source
    assert "supplier_a_" + "mock" not in source


def test_no_dishonest_airline_to_supplier_field_mapping() -> None:
    report = _valid_report()

    assert report.counter_table["dishonest_field_mapping_count"] == 0
    source = Path(runtime.__file__).read_text(encoding="utf-8")
    assert "payment_slot_ref" not in source
    assert "creditor_ref" not in source


def test_offer_hold_failure_blocks_all_later_phases() -> None:
    report = _run_with(
        hold_packet=replace(
            contracts.build_valid_airline_hold_commit_packet_v01(),
            expired=True,
        ),
    )

    assert report.final_status == runtime.STATUS_FAIL_CLOSED
    assert report.failed_phase_id == runtime.PHASE_AIRLINE_OFFER_HOLD
    assert report.return_to_root_id == contracts.AIRLINE_ROOT_ID
    assert all(
        phase.phase_status == runtime.STATUS_NOT_RUN
        for phase in report.phase_results[1:]
    )


def test_client_purchase_intent_failure_blocks_bank_and_ticket_phases() -> None:
    report = _run_with(
        purchase_intent=replace(
            contracts.build_valid_client_purchase_intent_v01(),
            selected_amount=contracts.MAX_AMOUNT + 1,
        ),
    )

    assert report.failed_phase_id == runtime.PHASE_CLIENT_PURCHASE_INTENT
    assert _phase(report, runtime.PHASE_BANK_PAYMENT_AUTHORIZATION).phase_status == (
        runtime.STATUS_NOT_RUN
    )
    assert _phase(report, runtime.PHASE_AIRLINE_TICKET_ISSUE).phase_status == (
        runtime.STATUS_NOT_RUN
    )


def test_bank_authorization_failure_blocks_ticket_phase() -> None:
    report = _run_with(
        authorization_ref=replace(
            contracts.build_valid_bank_payment_authorization_ref_v01(),
            expired=True,
        ),
    )

    assert report.failed_phase_id == runtime.PHASE_BANK_PAYMENT_AUTHORIZATION
    assert _phase(report, runtime.PHASE_AIRLINE_TICKET_ISSUE).phase_status == (
        runtime.STATUS_NOT_RUN
    )
    assert _phase(report, runtime.PHASE_CLIENT_COMPLETION).phase_status == (
        runtime.STATUS_NOT_RUN
    )


def test_airline_ticket_issue_failure_blocks_client_completion() -> None:
    report = _run_with(
        ticket_receipt=replace(
            contracts.build_valid_mock_ticket_receipt_v01(),
            real_ticket=True,
        ),
    )

    assert report.failed_phase_id == runtime.PHASE_AIRLINE_TICKET_ISSUE
    assert _phase(report, runtime.PHASE_CLIENT_COMPLETION).phase_status == (
        runtime.STATUS_NOT_RUN
    )


def test_later_phase_cannot_repair_earlier_failure() -> None:
    report = _run_with(
        hold_packet=replace(
            contracts.build_valid_airline_hold_commit_packet_v01(),
            expired=True,
        ),
        purchase_intent=contracts.build_valid_client_purchase_intent_v01(),
        authorization_ref=contracts.build_valid_bank_payment_authorization_ref_v01(),
    )

    assert report.failed_phase_id == runtime.PHASE_AIRLINE_OFFER_HOLD
    assert report.artifact_validation_summary[
        "later_phase_cannot_repair_earlier_failure"
    ] is True
    assert report.phase_results[1].phase_status == runtime.STATUS_NOT_RUN


def test_wrong_root_gate_returns_to_relevant_root() -> None:
    report = _run_with(
        client_purchase_gate=replace(
            contracts.build_valid_client_root_purchase_intent_gate_v01(),
            root_id=contracts.AIRLINE_ROOT_ID,
        ),
    )

    assert report.failed_phase_id == runtime.PHASE_CLIENT_PURCHASE_INTENT
    assert report.return_to_root_id == contracts.CLIENT_ROOT_ID
    assert contracts.REASON_WRONG_ROOT_OWNER in report.validation_errors


def test_airline_root_cannot_replace_client_root() -> None:
    report = _run_with(
        client_purchase_gate=replace(
            contracts.build_valid_client_root_purchase_intent_gate_v01(),
            root_id=contracts.AIRLINE_ROOT_ID,
        ),
    )

    assert report.failed_phase_id == runtime.PHASE_CLIENT_PURCHASE_INTENT
    assert report.return_to_root_id == contracts.CLIENT_ROOT_ID


def test_client_root_cannot_replace_bank_root() -> None:
    report = _run_with(
        bank_gate=replace(
            contracts.build_valid_bank_root_payment_authorization_gate_v01(),
            root_id=contracts.CLIENT_ROOT_ID,
        ),
    )

    assert report.failed_phase_id == runtime.PHASE_BANK_PAYMENT_AUTHORIZATION
    assert report.return_to_root_id == contracts.BANK_ROOT_ID


def test_bank_root_cannot_replace_airline_ticket_issue_root() -> None:
    report = _run_with(
        airline_ticket_gate=replace(
            contracts.build_valid_airline_root_ticket_issue_gate_v01(),
            root_id=contracts.BANK_ROOT_ID,
        ),
    )

    assert report.failed_phase_id == runtime.PHASE_AIRLINE_TICKET_ISSUE
    assert report.return_to_root_id == contracts.AIRLINE_ROOT_ID


def test_post_root_reasoning_restart_fails_closed() -> None:
    report = runtime._run_airline_ticket_purchase_corridor_state_machine_v01(
        _fixtures(),
        core_corridor_overrides={
            runtime.PHASE_AIRLINE_OFFER_HOLD: {
                "reasoning_restarted_after_root": True,
            },
        },
    )

    assert report.failed_phase_id == runtime.PHASE_AIRLINE_OFFER_HOLD
    assert report.final_status == runtime.STATUS_FAIL_CLOSED
    assert "reasoning_does_not_restart_after_root" in report.validation_errors


def test_receipts_are_observed_fixtures_not_runtime_created() -> None:
    report = _valid_report()

    assert report.counter_table["fixture_receipts_observed_count"] == 3
    assert report.counter_table["runtime_receipts_created_count"] == 0
    assert all(not phase.runtime_receipt_created for phase in report.phase_results)


def test_receipts_remain_evidence_only() -> None:
    report = _valid_report()

    assert report.receipt_boundary_summary["receipts_are_evidence_only"] is True
    assert report.receipt_boundary_summary["offer_hold_receipt_is_fixture"] is True
    assert report.counter_table["mock_ticket_receipt_validated_count"] == 1
    assert report.counter_table["mock_purchase_receipt_validated_count"] == 1


def test_cross_root_evidence_does_not_transfer_authority() -> None:
    report = _run_with(
        purchase_intent=replace(
            contracts.build_valid_client_purchase_intent_v01(),
            bank_authority_created=True,
        ),
    )

    assert report.final_status == runtime.STATUS_FAIL_CLOSED
    assert contracts.REASON_CROSS_ROOT_AUTHORITY_TRANSFER in report.validation_errors
    assert all(not phase.authority_transferred for phase in report.phase_results)


def test_human_approval_remains_evidence_for_client_root() -> None:
    report = _valid_report()
    client_phase = _phase(report, runtime.PHASE_CLIENT_PURCHASE_INTENT)

    assert client_phase.phase_status == runtime.STATUS_PASS
    assert contracts.build_valid_human_approval_evidence_ref_v01().evidence_only is True
    assert report.counter_table["client_root_phase_gate_pass_count"] == 2


def test_valid_mock_happy_path_has_zero_real_effects() -> None:
    report = _valid_report()

    assert report.counter_table["real_airline_api_called_count"] == 0
    assert report.counter_table["real_bank_api_called_count"] == 0
    assert report.counter_table["real_gds_api_called_count"] == 0
    assert report.counter_table["real_payment_executed_count"] == 0
    assert report.counter_table["real_ticket_issued_count"] == 0
    assert report.counter_table["real_booking_created_count"] == 0
    assert report.counter_table["real_world_effects_count"] == 0


def test_runtime_source_boundary() -> None:
    source = Path(runtime.__file__).read_text(encoding="utf-8")

    for forbidden in (
        "google.genai",
        "requests",
        "urllib",
        "openai",
        "subprocess",
        "import config",
        "provider_adapter",
        "run_tri_party_airline_live_semantic_lane",
        "run_tri_party_airline_ticket_purchase_mock_e2e",
        "build_" + "supplier_a",
        "SUBJECT_" + "SUPPLIER_A",
        "SUBJECT_" + "SUPPLIER_B",
        "ledger " + "implementation",
        "crypto " + "implementation",
        "replay " + "implementation",
        "production " + "ready",
        "public " + "auditor " + "ready",
    ):
        assert forbidden not in source
    assert "validate_corridor_no_post_root_reasoning_v01" in source
    assert "ContractFulfillmentCorridorV01" in source


def test_slice_c_counts_three_observed_fixture_receipts() -> None:
    report = _valid_report()

    assert report.counter_table["fixture_receipts_observed_count"] == 3
    assert report.receipt_boundary_summary["fixture_receipts_observed_count"] == 3
    assert report.receipt_boundary_summary["offer_hold_receipt_is_fixture"] is True
    assert report.receipt_boundary_summary["mock_ticket_receipt_is_fixture"] is True
    assert report.receipt_boundary_summary["mock_purchase_receipt_is_fixture"] is True
    assert report.counter_table["runtime_receipts_created_count"] == 0


def test_slice_c_phase_cannot_pass_when_validation_flag_false_without_reason() -> None:
    phase = runtime._phase_result(
        phase_index=1,
        phase_id=runtime.PHASE_AIRLINE_OFFER_HOLD,
        relevant_root_id=contracts.AIRLINE_ROOT_ID,
        root_gate_validated=False,
        core_corridor_guard_validated=True,
        domain_contracts_validated=True,
        evidence_refs_observed=(),
        reason_codes=(),
    )

    assert phase.phase_status == runtime.STATUS_FAIL_CLOSED
    assert runtime.REASON_ROOT_PHASE_GATE_VALIDATION_FAILED in phase.reason_codes


def test_slice_c_report_validator_rejects_wrong_failed_phase_id() -> None:
    report = _run_with(
        hold_packet=replace(
            contracts.build_valid_airline_hold_commit_packet_v01(),
            expired=True,
        ),
    )
    corrupted = replace(report, failed_phase_id=runtime.PHASE_CLIENT_PURCHASE_INTENT)
    accepted, errors = runtime.validate_airline_ticket_purchase_corridor_run_v01(
        corrupted,
    )

    assert accepted is False
    assert runtime.REASON_FAILED_PHASE_ID_MISMATCH in errors


def test_slice_c_report_validator_rejects_wrong_return_root() -> None:
    report = _run_with(
        hold_packet=replace(
            contracts.build_valid_airline_hold_commit_packet_v01(),
            expired=True,
        ),
    )
    corrupted = replace(report, return_to_root_id=contracts.CLIENT_ROOT_ID)
    accepted, errors = runtime.validate_airline_ticket_purchase_corridor_run_v01(
        corrupted,
    )

    assert accepted is False
    assert runtime.REASON_RETURN_TO_ROOT_ID_MISMATCH in errors


def test_slice_c_report_validator_rejects_pass_report_with_failed_phase() -> None:
    report = _valid_report()
    failed_phase = replace(
        report.phase_results[0],
        phase_status=runtime.STATUS_FAIL_CLOSED,
        reason_codes=("forced_failure",),
    )
    corrupted = replace(
        report,
        phase_results=(failed_phase,) + report.phase_results[1:],
    )
    accepted, errors = runtime.validate_airline_ticket_purchase_corridor_run_v01(
        corrupted,
    )

    assert accepted is False
    assert "pass_report_contains_failed_or_unrun_phase" in errors


def test_slice_c_report_validator_rejects_fail_report_with_later_pass_phase() -> None:
    report = _run_with(
        hold_packet=replace(
            contracts.build_valid_airline_hold_commit_packet_v01(),
            expired=True,
        ),
    )
    later_pass = replace(report.phase_results[1], phase_status=runtime.STATUS_PASS)
    corrupted = replace(
        report,
        phase_results=(report.phase_results[0], later_pass) + report.phase_results[2:],
    )
    accepted, errors = runtime.validate_airline_ticket_purchase_corridor_run_v01(
        corrupted,
    )

    assert accepted is False
    assert "later_phase_repaired_failure" in errors


def test_slice_c_report_validator_rejects_wrong_transition_shape() -> None:
    report = _valid_report()
    bad_transition = replace(
        report.transitions[0],
        from_phase_id=runtime.PHASE_BANK_PAYMENT_AUTHORIZATION,
    )
    corrupted = replace(
        report,
        transitions=(bad_transition,) + report.transitions[1:],
    )
    accepted, errors = runtime.validate_airline_ticket_purchase_corridor_run_v01(
        corrupted,
    )

    assert accepted is False
    assert runtime.REASON_TRANSITION_SHAPE_MISMATCH in errors


def test_slice_c_report_validator_rejects_wrong_phase_root() -> None:
    report = _valid_report()
    wrong_root_phase = replace(
        report.phase_results[0],
        relevant_root_id=contracts.CLIENT_ROOT_ID,
    )
    corrupted = replace(
        report,
        phase_results=(wrong_root_phase,) + report.phase_results[1:],
    )
    accepted, errors = runtime.validate_airline_ticket_purchase_corridor_run_v01(
        corrupted,
    )

    assert accepted is False
    assert runtime.REASON_PHASE_ROOT_MISMATCH in errors


def test_slice_c_report_validator_rejects_counter_drift() -> None:
    report = _valid_report()
    counters = dict(report.counter_table)
    counters["fixture_receipts_observed_count"] = 2
    corrupted = replace(report, counter_table=counters)
    accepted, errors = runtime.validate_airline_ticket_purchase_corridor_run_v01(
        corrupted,
    )

    assert accepted is False
    assert runtime.REASON_COUNTER_TABLE_MISMATCH in errors


def test_slice_c_report_validator_accepts_valid_pass_report() -> None:
    report = _valid_report()
    accepted, errors = runtime.validate_airline_ticket_purchase_corridor_run_v01(
        report,
    )

    assert accepted is True
    assert errors == ()


def test_slice_d_public_collector_accepts_valid_fixture_injection() -> None:
    report = runtime.collect_airline_ticket_purchase_corridor_state_machine_v01(
        fixtures=_fixtures(),
    )

    assert report.final_status == runtime.STATUS_PASS
    accepted, errors = runtime.validate_airline_ticket_purchase_corridor_run_v01(
        report,
    )
    assert accepted is True
    assert errors == ()


def test_slice_d_public_collector_rejects_invalid_fixture_injection() -> None:
    fixtures = _fixtures()
    fixtures["hold_packet"] = replace(fixtures["hold_packet"], expired=True)

    report = runtime.collect_airline_ticket_purchase_corridor_state_machine_v01(
        fixtures=fixtures,
    )

    assert report.final_status == runtime.STATUS_FAIL_CLOSED
    assert report.failed_phase_id == runtime.PHASE_AIRLINE_OFFER_HOLD
    assert contracts.REASON_EXPIRED_HOLD in report.validation_errors


def test_slice_d_public_collector_core_guard_override_fails_closed() -> None:
    report = runtime.collect_airline_ticket_purchase_corridor_state_machine_v01(
        fixtures=_fixtures(),
        core_corridor_overrides={
            runtime.PHASE_CLIENT_PURCHASE_INTENT: {
                "post_root_llm_reasoning_allowed": True,
            },
        },
    )

    assert report.final_status == runtime.STATUS_FAIL_CLOSED
    assert report.failed_phase_id == runtime.PHASE_CLIENT_PURCHASE_INTENT
    assert "no_post_root_llm_reasoning" in report.validation_errors


def test_slice_d_phase_derived_fields_are_consistent() -> None:
    report = _valid_report()

    for phase in report.phase_results:
        assert phase.phase_status == runtime.STATUS_PASS
        assert phase.return_to_relevant_root is False
        assert phase.later_phases_allowed is True

    failed = _run_with(
        hold_packet=replace(
            contracts.build_valid_airline_hold_commit_packet_v01(),
            expired=True,
        ),
    )
    assert failed.phase_results[0].phase_status == runtime.STATUS_FAIL_CLOSED
    assert failed.phase_results[0].return_to_relevant_root is True
    assert failed.phase_results[0].later_phases_allowed is False
    for phase in failed.phase_results[1:]:
        assert phase.phase_status == runtime.STATUS_NOT_RUN
        assert phase.return_to_relevant_root is False
        assert phase.later_phases_allowed is False


def test_slice_d_transition_derived_fields_are_consistent() -> None:
    report = _valid_report()

    for transition in report.transitions:
        assert transition.source_phase_passed is True
        assert transition.dependency_satisfied is True
        assert transition.transition_status == runtime.STATUS_PASS
        assert transition.reason_codes == ()

    failed = _run_with(
        purchase_intent=replace(
            contracts.build_valid_client_purchase_intent_v01(),
            selected_amount=contracts.MAX_AMOUNT + 1,
        ),
    )
    for transition in failed.transitions:
        source = failed.phase_results[transition.transition_index - 1]
        target = failed.phase_results[transition.transition_index]
        assert transition.source_phase_passed is (
            source.phase_status == runtime.STATUS_PASS
        )
        assert transition.dependency_satisfied is (
            source.phase_status == runtime.STATUS_PASS
            and target.phase_status != runtime.STATUS_NOT_RUN
        )
        if transition.transition_status != runtime.STATUS_PASS:
            assert transition.reason_codes == (
                f"dependency_not_satisfied:{source.phase_id}",
            )


def test_slice_d_tampered_derived_fields_are_rejected() -> None:
    report = _valid_report()

    bad_phase = replace(report.phase_results[0], later_phases_allowed=False)
    corrupted_phase_report = replace(
        report,
        phase_results=(bad_phase,) + report.phase_results[1:],
    )
    accepted, errors = runtime.validate_airline_ticket_purchase_corridor_run_v01(
        corrupted_phase_report,
    )
    assert accepted is False
    assert "phase_derived_field_mismatch" in errors

    bad_transition = replace(report.transitions[0], source_phase_passed=False)
    corrupted_transition_report = replace(
        report,
        transitions=(bad_transition,) + report.transitions[1:],
    )
    accepted, errors = runtime.validate_airline_ticket_purchase_corridor_run_v01(
        corrupted_transition_report,
    )
    assert accepted is False
    assert runtime.REASON_TRANSITION_SHAPE_MISMATCH in errors


def test_slice_d_pure_fixture_bundle_validator_accepts_valid_bundle() -> None:
    accepted, errors = (
        runtime.validate_airline_ticket_purchase_corridor_fixture_bundle_v01(
            _fixtures(),
        )
    )

    assert accepted is True
    assert errors == ()


def test_slice_d_pure_fixture_bundle_validator_rejects_invalid_bundle() -> None:
    fixtures = _fixtures()
    fixtures["authorization_ref"] = replace(
        fixtures["authorization_ref"],
        expired=True,
    )

    accepted, errors = (
        runtime.validate_airline_ticket_purchase_corridor_fixture_bundle_v01(
            fixtures,
        )
    )

    assert accepted is False
    assert contracts.REASON_EXPIRED_PAYMENT_AUTHORIZATION in errors


def test_slice_d_pure_fixture_bundle_validator_uses_core_guard_without_run_report() -> None:
    accepted, errors = (
        runtime.validate_airline_ticket_purchase_corridor_fixture_bundle_v01(
            _fixtures(),
            core_corridor_overrides={
                runtime.PHASE_AIRLINE_TICKET_ISSUE: {
                    "reasoning_restarted_after_root": True,
                },
            },
        )
    )

    assert accepted is False
    assert "reasoning_does_not_restart_after_root" in errors
    assert runtime.REASON_CORE_CORRIDOR_GUARD_VALIDATION_FAILED in errors


def test_corridor_report_is_bound_to_exact_projected_fixture_bundle() -> None:
    accepted, errors = (
        runtime
        .validate_airline_ticket_purchase_corridor_report_against_fixture_bundle_v01(
            _fixtures(),
            _valid_report(),
        )
    )

    assert accepted is True
    assert errors == ()


def test_corridor_report_wrong_phase_evidence_ref_rejected() -> None:
    report = _valid_report()
    bad_phase = replace(
        report.phase_results[0],
        evidence_refs_observed=("unrelated:offer_packet",),
    )
    corrupted = replace(
        report,
        phase_results=(bad_phase,) + report.phase_results[1:],
    )

    accepted, errors = (
        runtime
        .validate_airline_ticket_purchase_corridor_report_against_fixture_bundle_v01(
            _fixtures(),
            corrupted,
        )
    )

    assert accepted is False
    assert runtime.REASON_PHASE_EVIDENCE_REFS_MISMATCH in errors
    assert runtime.REASON_FIXTURE_REPORT_BINDING_FAILED in errors


def test_b_context_fixture_bundle_and_run_pass() -> None:
    accepted, errors = (
        runtime.validate_airline_ticket_purchase_corridor_fixture_bundle_v01(
            _b_fixtures(),
            contract_context=_b_context(),
        )
    )
    report = runtime.collect_airline_ticket_purchase_corridor_state_machine_v01(
        fixtures=_b_fixtures(),
        contract_context=_b_context(),
    )

    assert accepted is True
    assert errors == ()
    assert report.final_status == runtime.STATUS_PASS
    assert report.contract_context == _b_context()


def test_a_b_a_and_b_a_b_context_runs_remain_independent() -> None:
    original_constants = (
        contracts.OFFER_ID,
        contracts.HOLD_ID,
        contracts.AMOUNT,
    )

    a_first = runtime.collect_airline_ticket_purchase_corridor_state_machine_v01()
    b_first = runtime.collect_airline_ticket_purchase_corridor_state_machine_v01(
        fixtures=_b_fixtures(),
        contract_context=_b_context(),
    )
    a_second = runtime.collect_airline_ticket_purchase_corridor_state_machine_v01()
    b_second = runtime.collect_airline_ticket_purchase_corridor_state_machine_v01(
        fixtures=_b_fixtures(),
        contract_context=_b_context(),
    )

    assert a_first.final_status == runtime.STATUS_PASS
    assert b_first.final_status == runtime.STATUS_PASS
    assert a_second.final_status == runtime.STATUS_PASS
    assert b_second.final_status == runtime.STATUS_PASS
    assert a_first.contract_context.offer_id == contracts.OFFER_ID
    assert b_first.contract_context.offer_id == _b_context().offer_id
    assert a_second.contract_context.offer_id == contracts.OFFER_ID
    assert b_second.contract_context.offer_id == _b_context().offer_id
    assert (contracts.OFFER_ID, contracts.HOLD_ID, contracts.AMOUNT) == (
        original_constants
    )


def test_a_report_validates_after_b_collection_under_a_context() -> None:
    a_report = runtime.collect_airline_ticket_purchase_corridor_state_machine_v01()
    runtime.collect_airline_ticket_purchase_corridor_state_machine_v01(
        fixtures=_b_fixtures(),
        contract_context=_b_context(),
    )

    accepted, errors = (
        runtime.validate_airline_ticket_purchase_corridor_report_against_fixture_bundle_v01(
            _fixtures(),
            a_report,
            contract_context=a_report.contract_context,
        )
    )

    assert accepted is True
    assert errors == ()


def test_b_report_validates_after_a_collection_under_b_context() -> None:
    b_report = runtime.collect_airline_ticket_purchase_corridor_state_machine_v01(
        fixtures=_b_fixtures(),
        contract_context=_b_context(),
    )
    runtime.collect_airline_ticket_purchase_corridor_state_machine_v01()

    accepted, errors = (
        runtime.validate_airline_ticket_purchase_corridor_report_against_fixture_bundle_v01(
            _b_fixtures(),
            b_report,
            contract_context=b_report.contract_context,
        )
    )

    assert accepted is True
    assert errors == ()
