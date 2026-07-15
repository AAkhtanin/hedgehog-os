from __future__ import annotations

import ast
import inspect
import json
from dataclasses import FrozenInstanceError, dataclass, fields, replace
from pathlib import Path

import pytest

from hedgehog.domains.airline import crypto_artifact_seal_collector_v01 as crypto_collector
from hedgehog.domains.airline import crypto_artifact_seal_v01 as crypto_contracts
from hedgehog.domains.airline import sealed_trace_replay_v01 as replay
from hedgehog.domains.airline import transaction_artifact_ledger_collector_v01 as ledger_collector
from hedgehog.domains.airline import transaction_artifact_ledger_v01 as ledger_contracts
from tests import test_airline_transaction_artifact_ledger_collector_v01 as ledger_collector_test_helpers


MODULE_PATH = "hedgehog/domains/airline/sealed_trace_replay_v01.py"
PACKAGE_REF = "airline_sealed_trace_replay_slice_b_fixture"


@dataclass(frozen=True)
class ReplayFixture:
    offer_id: str
    ledger: ledger_contracts.AirlineTransactionArtifactLedgerV01
    rows: tuple[tuple[str, bytes], ...]
    audit: crypto_collector.AirlineCryptoArtifactSealAcceptedLedgerAuditV01
    envelope: crypto_contracts.AirlineCryptoArtifactSealEnvelopeV01
    stored: crypto_contracts.AirlineCryptoArtifactSealVerificationReportV01
    fresh: crypto_contracts.AirlineCryptoArtifactSealVerificationReportV01
    replay_input: replay.AirlineSealedTraceReplayInputV01


def _ledger(offer_id: str) -> ledger_contracts.AirlineTransactionArtifactLedgerV01:
    return ledger_contracts.build_airline_transaction_artifact_ledger_fixture_v01(
        offer_id=offer_id,
    )


def _identity(
    offer_id: str,
) -> ledger_contracts.AirlineTransactionArtifactLedgerExpectedIdentityV01:
    return ledger_contracts.build_airline_transaction_artifact_ledger_fixture_expected_identity_v01(
        offer_id=offer_id,
    )


def _source_rows(offer_id: str) -> tuple[tuple[str, bytes], ...]:
    return tuple(
        (
            ref,
            f"sealed-replay-slice-b:{offer_id}:{index}:{ref}".encode("utf-8"),
        )
        for index, ref in enumerate(crypto_contracts.REQUIRED_SOURCE_FILE_REFS)
    )


def _accepted_audit(
    item: ledger_contracts.AirlineTransactionArtifactLedgerV01,
    offer_id: str,
    **changes: object,
) -> crypto_collector.AirlineCryptoArtifactSealAcceptedLedgerAuditV01:
    values: dict[str, object] = {
        "audit_id": crypto_collector.EXPECTED_LEDGER_AUDIT_ID,
        "audit_version": crypto_collector.EXPECTED_LEDGER_AUDIT_VERSION,
        "final_status": crypto_collector.STATUS_PASS,
        "required_source_files": crypto_contracts.REQUIRED_SOURCE_FILE_REFS,
        "files_read_count": replay.SOURCE_FILE_COUNT,
        "ledger_id": item.ledger_id,
        "transaction_id": item.transaction_id,
        "selected_offer_id": offer_id,
        "source_run_ref": item.source_run_ref,
        "source_causal_report_ref": item.source_causal_report_ref,
        "source_corridor_report_ref": item.source_corridor_report_ref,
        "actual_entry_count": replay.LEDGER_ENTRY_COUNT,
        "actual_dependency_edge_count": replay.DEPENDENCY_EDGE_COUNT,
        "actual_root_final_count": replay.ROOT_FINAL_COUNT,
        "client_root_final_count": 1,
        "airline_root_final_count": 1,
        "bank_root_final_count": 1,
        **{
            field_name: True
            for field_name in crypto_collector.ACCEPTED_AUDIT_BOOLEAN_FIELDS
        },
        "stored_validation_status": crypto_collector.STATUS_PASS,
        "stored_validation_errors": (),
        **{
            field_name: 0
            for field_name in crypto_collector.ACCEPTED_AUDIT_ZERO_COUNTER_FIELDS
        },
        "validation_errors": (),
    }
    values.update(changes)
    return crypto_collector.AirlineCryptoArtifactSealAcceptedLedgerAuditV01(
        **values,  # type: ignore[arg-type]
    )


def _fixture(offer_id: str) -> ReplayFixture:
    item = _ledger(offer_id)
    identity = _identity(offer_id)
    rows = _source_rows(offer_id)
    core = crypto_contracts.build_airline_crypto_artifact_seal_manifest_core_v01(
        item,
        ordered_source_files=rows,
        source_package_ref=PACKAGE_REF,
        source_audit_status=crypto_contracts.STATUS_PASS,
        secret_scan_passed=True,
        expected_identity=identity,
    )
    envelope = crypto_contracts.build_airline_crypto_artifact_seal_envelope_v01(
        core,
    )
    stored = crypto_contracts.verify_airline_crypto_artifact_seal_v01(
        envelope,
        ledger_item=item,
        ordered_source_files_before=rows,
        ordered_source_files_after=rows,
        expected_source_package_ref=PACKAGE_REF,
        source_audit_status=crypto_contracts.STATUS_PASS,
        secret_scan_passed=True,
        expected_manifest_core_hash=None,
        expected_identity=identity,
    )
    fresh = crypto_contracts.verify_airline_crypto_artifact_seal_v01(
        envelope,
        ledger_item=item,
        ordered_source_files_before=rows,
        ordered_source_files_after=rows,
        expected_source_package_ref=PACKAGE_REF,
        source_audit_status=crypto_contracts.STATUS_PASS,
        secret_scan_passed=True,
        expected_manifest_core_hash=envelope.manifest_core_hash,
        expected_identity=identity,
    )
    audit = _accepted_audit(item, offer_id)
    replay_input = replay.build_airline_sealed_trace_replay_input_v01(
        source_package_ref=PACKAGE_REF,
        accepted_ledger_audit=audit,
        ledger_item=item,
        envelope=envelope,
        stored_verification_report=stored,
        fresh_anchored_verification_report=fresh,
        expected_manifest_core_hash=envelope.manifest_core_hash,
        ordered_source_files=rows,
    )
    return ReplayFixture(
        offer_id=offer_id,
        ledger=item,
        rows=rows,
        audit=audit,
        envelope=envelope,
        stored=stored,
        fresh=fresh,
        replay_input=replay_input,
    )


def _source_derived_fixture(offer_id: str) -> ReplayFixture:
    source_bundle = (
        ledger_collector_test_helpers._source_bundle_from_public_causal_runtime(
            offer_id,
        )
    )
    item = ledger_collector.collect_airline_transaction_artifact_ledger_from_source_v01(
        source_bundle=source_bundle,
    )
    audit = _accepted_audit(item, offer_id)
    identity = replay.build_airline_sealed_trace_replay_expected_identity_adapter_v01(
        ledger_item=item,
        accepted_ledger_audit=audit,
    )
    package_ref = (
        "airline_sealed_trace_replay_source_derived_a"
        if offer_id == ledger_contracts.OFFER_A_ID
        else "airline_sealed_trace_replay_source_derived_b"
    )
    ledger_bytes = crypto_contracts.canonical_airline_crypto_json_bytes_v01(
        crypto_collector.airline_crypto_artifact_seal_ledger_document_to_plain_dict_v01(
            item,
            expected_identity=identity,
        ),
    )
    rows = tuple(
        (
            relative_ref,
            ledger_bytes
            if index == 0
            else crypto_contracts.canonical_airline_crypto_json_bytes_v01(
                {
                    "offer_id": offer_id,
                    "source_file_index": index,
                    "source_file_ref": relative_ref,
                    "transaction_id": item.transaction_id,
                },
            ),
        )
        for index, relative_ref in enumerate(
            crypto_contracts.REQUIRED_SOURCE_FILE_REFS,
        )
    )
    core = crypto_contracts.build_airline_crypto_artifact_seal_manifest_core_v01(
        item,
        ordered_source_files=rows,
        source_package_ref=package_ref,
        source_audit_status=crypto_contracts.STATUS_PASS,
        secret_scan_passed=True,
        expected_identity=identity,
    )
    envelope = crypto_contracts.build_airline_crypto_artifact_seal_envelope_v01(
        core,
    )
    stored = crypto_contracts.verify_airline_crypto_artifact_seal_v01(
        envelope,
        ledger_item=item,
        ordered_source_files_before=rows,
        ordered_source_files_after=rows,
        expected_source_package_ref=package_ref,
        source_audit_status=crypto_contracts.STATUS_PASS,
        secret_scan_passed=True,
        expected_manifest_core_hash=None,
        expected_identity=identity,
    )
    fresh = crypto_contracts.verify_airline_crypto_artifact_seal_v01(
        envelope,
        ledger_item=item,
        ordered_source_files_before=rows,
        ordered_source_files_after=rows,
        expected_source_package_ref=package_ref,
        source_audit_status=crypto_contracts.STATUS_PASS,
        secret_scan_passed=True,
        expected_manifest_core_hash=envelope.manifest_core_hash,
        expected_identity=identity,
    )
    replay_input = replay.build_airline_sealed_trace_replay_input_v01(
        source_package_ref=package_ref,
        accepted_ledger_audit=audit,
        ledger_item=item,
        envelope=envelope,
        stored_verification_report=stored,
        fresh_anchored_verification_report=fresh,
        expected_manifest_core_hash=envelope.manifest_core_hash,
        ordered_source_files=rows,
    )
    return ReplayFixture(
        offer_id=offer_id,
        ledger=item,
        rows=rows,
        audit=audit,
        envelope=envelope,
        stored=stored,
        fresh=fresh,
        replay_input=replay_input,
    )


def _run(
    replay_input: object,
    *,
    critical_package_bytes_unchanged: object = True,
    post_replay_snapshot_provider_call_count: object = 1,
) -> replay.AirlineSealedTraceReplayReportV01:
    return replay.verify_airline_sealed_trace_replay_v01(
        replay_input,
        critical_package_bytes_unchanged=critical_package_bytes_unchanged,
        post_replay_snapshot_provider_call_count=(
            post_replay_snapshot_provider_call_count
        ),
    )


def _assert_fail(
    report: replay.AirlineSealedTraceReplayReportV01,
    reason: str | None = None,
) -> None:
    assert type(report) is replay.AirlineSealedTraceReplayReportV01
    assert report.replay_status == replay.STATUS_FAIL_CLOSED
    assert report.reconstructed_timeline == ()
    assert report.timeline_row_count == 0
    assert report.verification_errors
    if reason is not None:
        assert reason in report.verification_errors
    contract = replay.validate_airline_sealed_trace_replay_report_v01(report)
    assert contract.validation_status == replay.STATUS_PASS
    json.dumps(replay.airline_sealed_trace_replay_report_to_plain_dict_v01(report))


def _valid_report(offer_id: str) -> replay.AirlineSealedTraceReplayReportV01:
    report = _run(_fixture(offer_id).replay_input)
    assert report.replay_status == replay.STATUS_PASS
    return report


def _assert_report_replace_rejected(
    report: replay.AirlineSealedTraceReplayReportV01,
    **changes: object,
) -> None:
    try:
        changed = replace(report, **changes)
    except TypeError:
        return
    assert changed.replay_status == replay.STATUS_FAIL_CLOSED
    assert replay.REASON_REPLAY_REPORT_STATE_MISMATCH in (
        changed.verification_errors
    )
    assert (
        replay.validate_airline_sealed_trace_replay_report_v01(
            changed,
        ).validation_status
        == replay.STATUS_FAIL_CLOSED
    )
    with pytest.raises(ValueError):
        replay.airline_sealed_trace_replay_report_to_plain_dict_v01(changed)


def _forge_exact_dataclass(
    value: object,
    **changes: object,
) -> object:
    forged = object.__new__(type(value))
    for field in fields(value):
        object.__setattr__(
            forged,
            field.name,
            changes.get(field.name, getattr(value, field.name)),
        )
    return forged


@pytest.mark.parametrize(
    ("contract_type", "field_names"),
    (
        (
            replay.AirlineSealedTraceReplayValidationReportV01,
            replay.VALIDATION_REPORT_FIELD_NAMES,
        ),
        (
            replay.AirlineSealedTraceReplayPackageSnapshotV01,
            replay.PACKAGE_SNAPSHOT_FIELD_NAMES,
        ),
        (
            replay.AirlineSealedTraceReplayInputV01,
            replay.REPLAY_INPUT_FIELD_NAMES,
        ),
        (
            replay.AirlineSealedTraceReplayTimelineRowV01,
            replay.TIMELINE_ROW_FIELD_NAMES,
        ),
        (
            replay.AirlineSealedTraceReplayReportV01,
            replay.REPLAY_REPORT_FIELD_NAMES,
        ),
    ),
)
def test_field_name_surfaces_match_frozen_contracts(
    contract_type: type[object],
    field_names: tuple[str, ...],
) -> None:
    assert tuple(field.name for field in fields(contract_type)) == field_names
    assert type(field_names) is tuple


def test_replay_input_contract_remains_frozen_without_adapter_state() -> None:
    expected = (
        "source_package_ref",
        "accepted_ledger_audit",
        "ledger_item",
        "envelope",
        "stored_verification_report",
        "fresh_anchored_verification_report",
        "expected_manifest_core_hash",
        "ordered_source_files",
    )
    assert replay.REPLAY_INPUT_FIELD_NAMES == expected
    assert tuple(
        field.name for field in fields(replay.AirlineSealedTraceReplayInputV01)
    ) == expected
    assert "expected_identity" not in expected
    assert "callback" not in expected


def test_validation_report_derives_status_and_normalizes_errors() -> None:
    passed = replay.build_airline_sealed_trace_replay_validation_report_v01(())
    failed = replay.build_airline_sealed_trace_replay_validation_report_v01(
        (
            replay.REASON_LEDGER_WRONG_TYPE,
            replay.REASON_LEDGER_WRONG_TYPE,
            "caller_reason",
        ),
    )
    malformed = replay.build_airline_sealed_trace_replay_validation_report_v01(
        [replay.REASON_LEDGER_WRONG_TYPE],
    )
    assert passed.validation_status == replay.STATUS_PASS
    assert passed.validation_errors == ()
    assert failed.validation_status == replay.STATUS_FAIL_CLOSED
    assert failed.validation_errors == (
        replay.REASON_LEDGER_WRONG_TYPE,
        replay.REASON_UNKNOWN_VALIDATION_REASON,
    )
    assert malformed.validation_errors == (
        replay.REASON_MALFORMED_VALIDATION_ERRORS,
    )


def test_reason_allowlist_is_exact_unique_immutable_strings() -> None:
    assert type(replay.REPLAY_VALIDATION_REASON_ALLOWLIST) is tuple
    assert len(replay.REPLAY_VALIDATION_REASON_ALLOWLIST) == len(
        set(replay.REPLAY_VALIDATION_REASON_ALLOWLIST),
    )
    assert all(
        type(reason) is str and reason
        for reason in replay.REPLAY_VALIDATION_REASON_ALLOWLIST
    )


def _snapshot(**changes: object) -> replay.AirlineSealedTraceReplayPackageSnapshotV01:
    values: dict[str, object] = {
        "source_package_ref": PACKAGE_REF,
        "ordered_source_files": _source_rows(ledger_contracts.OFFER_A_ID),
        "manifest_artifact_ref": replay.MANIFEST_ARTIFACT_REF,
        "manifest_bytes": b"manifest",
        "stored_verification_artifact_ref": (
            replay.STORED_VERIFICATION_ARTIFACT_REF
        ),
        "stored_verification_bytes": b"verification",
    }
    values.update(changes)
    return replay.AirlineSealedTraceReplayPackageSnapshotV01(
        **values,  # type: ignore[arg-type]
    )


def test_valid_package_snapshot_is_deeply_immutable() -> None:
    snapshot = replay.build_airline_sealed_trace_replay_package_snapshot_v01(
        source_package_ref=PACKAGE_REF,
        ordered_source_files=_source_rows(ledger_contracts.OFFER_A_ID),
        manifest_artifact_ref=replay.MANIFEST_ARTIFACT_REF,
        manifest_bytes=b"manifest",
        stored_verification_artifact_ref=replay.STORED_VERIFICATION_ARTIFACT_REF,
        stored_verification_bytes=b"verification",
    )
    assert (
        replay.validate_airline_sealed_trace_replay_package_snapshot_v01(
            snapshot,
        ).validation_status
        == replay.STATUS_PASS
    )
    assert len(snapshot.ordered_source_files) == replay.SOURCE_FILE_COUNT
    with pytest.raises(FrozenInstanceError):
        snapshot.source_package_ref = "changed"  # type: ignore[misc]


@pytest.mark.parametrize(
    ("changes", "reason"),
    (
        ({"source_package_ref": "../bad"}, replay.REASON_SOURCE_PACKAGE_REF_INVALID),
        ({"ordered_source_files": []}, replay.REASON_SOURCE_FILE_SNAPSHOT_MALFORMED),
        ({"ordered_source_files": tuple(reversed(_source_rows(ledger_contracts.OFFER_A_ID)))}, replay.REASON_SOURCE_FILE_ORDER_MISMATCH),
        ({"ordered_source_files": _source_rows(ledger_contracts.OFFER_A_ID)[:-1]}, replay.REASON_SOURCE_FILE_SNAPSHOT_MALFORMED),
        ({"ordered_source_files": ((crypto_contracts.REQUIRED_SOURCE_FILE_REFS[0], bytearray(b"x")),) + _source_rows(ledger_contracts.OFFER_A_ID)[1:]}, replay.REASON_SOURCE_FILE_SNAPSHOT_MALFORMED),
        ({"ordered_source_files": ((crypto_contracts.REQUIRED_SOURCE_FILE_REFS[0], memoryview(b"x")),) + _source_rows(ledger_contracts.OFFER_A_ID)[1:]}, replay.REASON_SOURCE_FILE_SNAPSHOT_MALFORMED),
        ({"manifest_artifact_ref": "wrong.json"}, replay.REASON_MANIFEST_ARTIFACT_REF_MISMATCH),
        ({"manifest_bytes": bytearray(b"x")}, replay.REASON_MANIFEST_BYTES_MALFORMED),
        ({"stored_verification_artifact_ref": "wrong.json"}, replay.REASON_STORED_VERIFICATION_ARTIFACT_REF_MISMATCH),
        ({"stored_verification_bytes": memoryview(b"x")}, replay.REASON_STORED_VERIFICATION_BYTES_MALFORMED),
    ),
)
def test_package_snapshot_mutations_fail_closed(
    changes: dict[str, object],
    reason: str,
) -> None:
    snapshot = _snapshot(**changes)
    validation = replay.validate_airline_sealed_trace_replay_package_snapshot_v01(
        snapshot,
    )
    assert validation.validation_status == replay.STATUS_FAIL_CLOSED
    assert reason in validation.validation_errors


def test_wrong_package_snapshot_type_fails_closed() -> None:
    validation = replay.validate_airline_sealed_trace_replay_package_snapshot_v01(
        object(),
    )
    assert validation.validation_errors == (
        replay.REASON_PACKAGE_SNAPSHOT_WRONG_TYPE,
    )


def test_mutable_snapshot_rows_are_not_retained_or_repaired() -> None:
    caller_rows = list(_source_rows(ledger_contracts.OFFER_A_ID))
    snapshot = _snapshot(ordered_source_files=caller_rows)
    caller_rows.clear()
    assert snapshot.ordered_source_files == ()
    with pytest.raises(ValueError, match=replay.REASON_SOURCE_FILE_SNAPSHOT_MALFORMED):
        replay.build_airline_sealed_trace_replay_package_snapshot_v01(
            source_package_ref=PACKAGE_REF,
            ordered_source_files=list(_source_rows(ledger_contracts.OFFER_A_ID)),
            manifest_artifact_ref=replay.MANIFEST_ARTIFACT_REF,
            manifest_bytes=b"manifest",
            stored_verification_artifact_ref=(
                replay.STORED_VERIFICATION_ARTIFACT_REF
            ),
            stored_verification_bytes=b"verification",
        )


@pytest.mark.parametrize(
    ("field_name", "use_memoryview", "reason"),
    (
        (
            "manifest_bytes",
            False,
            replay.REASON_MANIFEST_BYTES_MALFORMED,
        ),
        (
            "stored_verification_bytes",
            False,
            replay.REASON_STORED_VERIFICATION_BYTES_MALFORMED,
        ),
        (
            "manifest_bytes",
            True,
            replay.REASON_MANIFEST_BYTES_MALFORMED,
        ),
        (
            "stored_verification_bytes",
            True,
            replay.REASON_STORED_VERIFICATION_BYTES_MALFORMED,
        ),
    ),
)
def test_malformed_snapshot_buffers_are_not_retained(
    field_name: str,
    use_memoryview: bool,
    reason: str,
) -> None:
    caller_buffer = bytearray(b"mutable-buffer")
    supplied: object = (
        memoryview(caller_buffer) if use_memoryview else caller_buffer
    )
    snapshot = _snapshot(**{field_name: supplied})
    caller_buffer[0] ^= 1
    assert getattr(snapshot, field_name) == b""
    assert type(getattr(snapshot, field_name)) is bytes
    assert getattr(snapshot, field_name) is not supplied
    validation = replay.validate_airline_sealed_trace_replay_package_snapshot_v01(
        snapshot,
    )
    assert validation.validation_status == replay.STATUS_FAIL_CLOSED
    assert validation.validation_errors == (reason,)


@pytest.mark.parametrize("offer_id", (ledger_contracts.OFFER_A_ID, ledger_contracts.OFFER_B_ID))
def test_valid_replay_input_and_pure_replay_pass(offer_id: str) -> None:
    fixture = _fixture(offer_id)
    validation = replay.validate_airline_sealed_trace_replay_input_v01(
        fixture.replay_input,
    )
    report = _run(fixture.replay_input)
    assert validation.validation_status == replay.STATUS_PASS
    assert report.replay_status == replay.STATUS_PASS
    assert report.verification_errors == ()
    assert (
        replay.validate_airline_sealed_trace_replay_report_v01(
            report,
        ).validation_status
        == replay.STATUS_PASS
    )


@pytest.mark.parametrize(
    "offer_id",
    (ledger_contracts.OFFER_A_ID, ledger_contracts.OFFER_B_ID),
)
def test_source_derived_expected_identity_continuity_passes(
    offer_id: str,
) -> None:
    fixture = _source_derived_fixture(offer_id)
    adapter = replay.build_airline_sealed_trace_replay_expected_identity_adapter_v01(
        ledger_item=fixture.ledger,
        accepted_ledger_audit=fixture.audit,
    )
    ledger_validation = (
        ledger_contracts.validate_airline_transaction_artifact_ledger_v01(
            fixture.ledger,
            expected_identity=adapter,
        )
    )
    input_validation = replay.validate_airline_sealed_trace_replay_input_v01(
        fixture.replay_input,
    )
    timeline = replay.build_airline_sealed_trace_replay_timeline_v01(
        fixture.replay_input,
    )
    report = _run(fixture.replay_input)

    assert replay.EXPECTED_IDENTITY_ROLE == (
        "verifier_contract_adapter_after_independent_ledger_audit"
    )
    assert ledger_validation.validation_status == replay.STATUS_PASS
    assert ledger_validation.validation_errors == ()
    assert input_validation.validation_status == replay.STATUS_PASS
    assert input_validation.validation_errors == ()
    assert len(timeline) == 19
    assert report.replay_status == replay.STATUS_PASS
    assert report.reconstructed_timeline == timeline
    assert (
        report.ledger_entry_count,
        report.dependency_edge_count,
        report.root_final_count,
    ) == (19, 29, 3)
    assert (
        report.source_file_count,
        report.critical_package_file_count,
    ) == (9, 11)
    assert report.stored_verification_status == (
        crypto_contracts.STATUS_SELF_CONSISTENT_UNANCHORED
    )
    assert report.fresh_anchored_verification_status == replay.STATUS_PASS
    assert report.signature_verified is False
    assert report.source_bytes_unchanged is True
    assert report.critical_package_bytes_unchanged is True
    for field_name in (
        "transaction_rerun_count",
        "semantic_rerun_count",
        "corridor_rerun_count",
        "ledger_recollection_count",
        "crypto_collection_count",
        "provider_call_count",
        "network_call_count",
        "gemini_call_count",
        "replay_created_authority_count",
        "replay_created_permission_count",
        "replay_created_action_count",
        "replay_created_packet_count",
        "replay_created_receipt_count",
        "replay_created_final_output_count",
        "real_world_effects_count",
    ):
        assert type(getattr(report, field_name)) is int
        assert getattr(report, field_name) == 0


@pytest.mark.parametrize(
    "sequence",
    (
        (
            ledger_contracts.OFFER_A_ID,
            ledger_contracts.OFFER_B_ID,
            ledger_contracts.OFFER_A_ID,
        ),
        (
            ledger_contracts.OFFER_B_ID,
            ledger_contracts.OFFER_A_ID,
            ledger_contracts.OFFER_B_ID,
        ),
    ),
)
def test_source_derived_offer_isolation_and_repeated_equality(
    sequence: tuple[str, ...],
) -> None:
    fixtures = tuple(_source_derived_fixture(offer_id) for offer_id in sequence)
    adapters = tuple(
        replay.build_airline_sealed_trace_replay_expected_identity_adapter_v01(
            ledger_item=fixture.ledger,
            accepted_ledger_audit=fixture.audit,
        )
        for fixture in fixtures
    )
    timelines = tuple(
        replay.build_airline_sealed_trace_replay_timeline_v01(
            fixture.replay_input,
        )
        for fixture in fixtures
    )
    reports = tuple(_run(fixture.replay_input) for fixture in fixtures)
    projections = tuple(
        replay.airline_sealed_trace_replay_report_to_plain_dict_v01(report)
        for report in reports
    )

    assert adapters[0] == adapters[2]
    assert timelines[0] == timelines[2]
    assert reports[0] == reports[2]
    assert projections[0] == projections[2]
    assert reports[0] != reports[1]
    assert projections[0] is not projections[2]


def test_source_derived_path_never_uses_fixture_default_identity(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    fixture = _source_derived_fixture(ledger_contracts.OFFER_A_ID)

    def forbidden_fixture_identity(*args: object, **kwargs: object) -> object:
        raise AssertionError("fixture_default_identity_forbidden")

    monkeypatch.setattr(
        ledger_contracts,
        "build_airline_transaction_artifact_ledger_fixture_expected_identity_v01",
        forbidden_fixture_identity,
    )
    assert (
        replay.validate_airline_sealed_trace_replay_input_v01(
            fixture.replay_input,
        ).validation_status
        == replay.STATUS_PASS
    )
    assert len(
        replay.build_airline_sealed_trace_replay_timeline_v01(
            fixture.replay_input,
        ),
    ) == 19
    assert _run(fixture.replay_input).replay_status == replay.STATUS_PASS


@pytest.mark.parametrize(
    "offer_id",
    (ledger_contracts.OFFER_A_ID, ledger_contracts.OFFER_B_ID),
)
@pytest.mark.parametrize("source_index", range(replay.SOURCE_FILE_COUNT))
def test_one_byte_source_mutation_breaks_manifest_binding(
    offer_id: str,
    source_index: int,
) -> None:
    fixture = _fixture(offer_id)
    changed_rows = list(fixture.rows)
    relative_ref, exact_bytes = changed_rows[source_index]
    changed_bytes = bytearray(exact_bytes)
    changed_bytes[-1] ^= 1
    changed_rows[source_index] = (relative_ref, bytes(changed_bytes))
    mutated_input = replace(
        fixture.replay_input,
        ordered_source_files=tuple(changed_rows),
    )
    validation = replay.validate_airline_sealed_trace_replay_input_v01(
        mutated_input,
    )
    assert validation.validation_status == replay.STATUS_FAIL_CLOSED
    assert replay.REASON_SOURCE_BYTES_CHANGED in validation.validation_errors
    report = _run(mutated_input)
    _assert_fail(report, replay.REASON_SOURCE_BYTES_CHANGED)


@pytest.mark.parametrize(
    "sequence",
    (
        (ledger_contracts.OFFER_A_ID, ledger_contracts.OFFER_B_ID, ledger_contracts.OFFER_A_ID),
        (ledger_contracts.OFFER_B_ID, ledger_contracts.OFFER_A_ID, ledger_contracts.OFFER_B_ID),
    ),
)
def test_offer_isolation_and_repeated_determinism(sequence: tuple[str, ...]) -> None:
    reports = tuple(_valid_report(offer_id) for offer_id in sequence)
    assert reports[0] == reports[2]
    assert reports[0] != reports[1]
    assert reports[0].replay_id == reports[2].replay_id
    assert reports[0].reconstructed_timeline == reports[2].reconstructed_timeline


@pytest.mark.parametrize("offer_id", (ledger_contracts.OFFER_A_ID, ledger_contracts.OFFER_B_ID))
def test_replay_geometry_order_bindings_and_lineage(offer_id: str) -> None:
    fixture = _fixture(offer_id)
    report = _run(fixture.replay_input)
    rows = report.reconstructed_timeline
    assert len(rows) == replay.TIMELINE_ROW_COUNT == 19
    assert tuple(row.replay_index for row in rows) == tuple(range(19))
    assert tuple(row.ledger_index for row in rows) == tuple(range(19))
    assert tuple(row.artifact_type for row in rows) == (
        ledger_contracts.EXPECTED_ARTIFACT_TYPE_SEQUENCE
    )
    assert tuple(row.artifact_id for row in rows) == (
        fixture.envelope.manifest_core.ordered_artifact_refs
    )
    assert tuple(row.artifact_hash for row in rows) == (
        fixture.envelope.manifest_core.ordered_artifact_hashes
    )
    assert sum(row.dependency_count for row in rows) == 29
    assert sum(row.is_root_final for row in rows) == 3
    assert tuple(
        row.root_owner for row in rows if row.is_root_final
    ) == (
        ledger_contracts.CLIENT_ROOT_ID,
        ledger_contracts.AIRLINE_ROOT_ID,
        ledger_contracts.BANK_ROOT_ID,
    )
    assert report.packet_lineage_verified is True
    assert report.receipt_lineage_verified is True
    selected = {row.selected_offer_id for row in rows if row.selected_offer_id}
    assert selected == {offer_id}
    assert any(row.selected_offer_id is None for row in rows)


@pytest.mark.parametrize("offer_id", (ledger_contracts.OFFER_A_ID, ledger_contracts.OFFER_B_ID))
def test_replay_verification_moments_and_all_derived_counters(offer_id: str) -> None:
    fixture = _fixture(offer_id)
    report = _run(fixture.replay_input)
    assert fixture.stored.verification_status == (
        crypto_contracts.STATUS_SELF_CONSISTENT_UNANCHORED
    )
    assert fixture.stored.expected_manifest_core_hash is None
    assert fixture.stored.external_anchor_supplied is False
    assert fixture.stored.external_anchor_verified is False
    assert fixture.fresh.verification_status == replay.STATUS_PASS
    assert fixture.fresh.external_anchor_supplied is True
    assert fixture.fresh.external_anchor_verified is True
    assert report.stored_verification_status == (
        crypto_contracts.STATUS_SELF_CONSISTENT_UNANCHORED
    )
    assert report.fresh_anchored_verification_status == replay.STATUS_PASS
    assert report.external_anchor_supplied is True
    assert report.external_anchor_verified is True
    assert report.signature_mode == crypto_contracts.SIGNATURE_MODE_UNSIGNED_PLACEHOLDER
    assert report.signature_verified is False
    assert report.source_file_count == 9
    assert report.critical_package_file_count == 11
    assert report.ledger_entry_count == 19
    assert report.dependency_edge_count == 29
    assert report.root_final_count == 3
    assert report.timeline_row_count == 19
    assert report.ledger_audit_count == 1
    assert report.anchored_verification_count == 1
    assert report.post_replay_snapshot_provider_call_count == 1
    for field_name in (
        "transaction_rerun_count",
        "semantic_rerun_count",
        "corridor_rerun_count",
        "ledger_recollection_count",
        "crypto_collection_count",
        "provider_call_count",
        "network_call_count",
        "gemini_call_count",
        "replay_created_authority_count",
        "replay_created_permission_count",
        "replay_created_action_count",
        "replay_created_packet_count",
        "replay_created_receipt_count",
        "replay_created_final_output_count",
        "real_world_effects_count",
    ):
        assert type(getattr(report, field_name)) is int
        assert getattr(report, field_name) == 0
    assert report.root_attestation_required is False
    assert report.root_attestation_present is False


@pytest.mark.parametrize("offer_id", (ledger_contracts.OFFER_A_ID, ledger_contracts.OFFER_B_ID))
def test_replay_id_and_plain_projections_are_deterministic_and_independent(
    offer_id: str,
) -> None:
    report = _valid_report(offer_id)
    assert report.replay_version == replay.REPLAY_VERSION
    assert report.replay_id == (
        f"{replay.REPLAY_ID_PREFIX}:{report.transaction_id}:"
        f"{report.manifest_core_hash}"
    )
    first = replay.airline_sealed_trace_replay_report_to_plain_dict_v01(report)
    second = replay.airline_sealed_trace_replay_report_to_plain_dict_v01(report)
    assert first == second
    assert first is not second
    assert first["reconstructed_timeline"] is not second["reconstructed_timeline"]
    assert getattr(report, "_constructed_by_replay_verifier_v01") is True
    assert "_construction_token" not in replay.REPLAY_REPORT_FIELD_NAMES
    assert "_construction_token" not in first
    assert "_constructed_by_replay_verifier_v01" not in first
    assert "_construction_token" not in repr(report)
    assert "_constructed_by_replay_verifier_v01" not in repr(report)
    first["reconstructed_timeline"][0]["depends_on"].append("mutation")  # type: ignore[index,union-attr]
    assert first != second
    json.dumps(second, allow_nan=False)
    assert not _contains_bytes(second)
    assert "private" not in json.dumps(second).lower()
    assert "raw_prompt" not in json.dumps(second).lower()
    assert "raw_response" not in json.dumps(second).lower()


def _contains_bytes(value: object) -> bool:
    if type(value) is bytes:
        return True
    if type(value) is list:
        return any(_contains_bytes(item) for item in value)
    if type(value) is dict:
        return any(_contains_bytes(item) for item in value.values())
    return False


def test_row_projection_is_fresh_json_safe_and_row_is_frozen() -> None:
    row = _valid_report(ledger_contracts.OFFER_A_ID).reconstructed_timeline[10]
    first = replay.airline_sealed_trace_replay_timeline_row_to_plain_dict_v01(row)
    second = replay.airline_sealed_trace_replay_timeline_row_to_plain_dict_v01(row)
    assert first == second
    assert first is not second
    assert first["depends_on"] is not second["depends_on"]
    json.dumps(first, allow_nan=False)
    with pytest.raises(FrozenInstanceError):
        row.artifact_id = "changed"  # type: ignore[misc]


def test_caller_list_cannot_back_timeline_or_errors() -> None:
    valid = _valid_report(ledger_contracts.OFFER_A_ID)
    caller_timeline = list(valid.reconstructed_timeline)
    caller_errors = [replay.REASON_TIMELINE_INCOMPLETE]
    with pytest.raises(TypeError):
        replace(
            valid,
            reconstructed_timeline=caller_timeline,  # type: ignore[arg-type]
            verification_errors=caller_errors,  # type: ignore[arg-type]
        )
    caller_timeline.clear()
    caller_errors.clear()
    assert len(valid.reconstructed_timeline) == replay.TIMELINE_ROW_COUNT
    assert valid.verification_errors == ()


@pytest.mark.parametrize(
    ("mutator", "reason"),
    (
        (lambda fixture: object(), replay.REASON_REPLAY_INPUT_WRONG_TYPE),
        (lambda fixture: replace(fixture.replay_input, accepted_ledger_audit=object()), replay.REASON_ACCEPTED_LEDGER_AUDIT_INVALID),
        (lambda fixture: replace(fixture.replay_input, ledger_item=object()), replay.REASON_LEDGER_WRONG_TYPE),
        (lambda fixture: replace(fixture.replay_input, envelope=object()), replay.REASON_ENVELOPE_INVALID),
        (lambda fixture: replace(fixture.replay_input, stored_verification_report=object()), replay.REASON_STORED_VERIFICATION_INVALID),
        (lambda fixture: replace(fixture.replay_input, fresh_anchored_verification_report=object()), replay.REASON_FRESH_ANCHORED_VERIFICATION_INVALID),
        (lambda fixture: replace(fixture.replay_input, expected_manifest_core_hash="bad"), replay.REASON_EXPECTED_MANIFEST_CORE_HASH_INVALID),
        (lambda fixture: replace(fixture.replay_input, expected_manifest_core_hash="0" * 64), replay.REASON_EXPECTED_MANIFEST_CORE_HASH_MISMATCH),
        (lambda fixture: replace(fixture.replay_input, source_package_ref="different_package"), replay.REASON_REPLAY_INPUT_IDENTITY_MISMATCH),
        (lambda fixture: replace(fixture.replay_input, ordered_source_files=tuple(reversed(fixture.rows))), replay.REASON_SOURCE_FILE_ORDER_MISMATCH),
        (lambda fixture: replace(fixture.replay_input, accepted_ledger_audit=replace(fixture.audit, required_source_files=tuple(reversed(fixture.audit.required_source_files)))), replay.REASON_ACCEPTED_LEDGER_AUDIT_INVALID),
        (lambda fixture: replace(fixture.replay_input, accepted_ledger_audit=replace(fixture.audit, actual_entry_count=18)), replay.REASON_ACCEPTED_LEDGER_AUDIT_INVALID),
    ),
)
def test_replay_input_mutations_fail_closed(
    mutator: object,
    reason: str,
) -> None:
    fixture = _fixture(ledger_contracts.OFFER_A_ID)
    mutated = mutator(fixture)  # type: ignore[operator]
    report = _run(mutated)
    _assert_fail(report, reason)


@pytest.mark.parametrize(
    "stored_mutator",
    (
        lambda fixture: fixture.fresh,
        lambda fixture: replace(fixture.stored, expected_manifest_core_hash="0" * 64),
        lambda fixture: replace(fixture.stored, external_anchor_supplied=True),
        lambda fixture: replace(fixture.stored, external_anchor_verified=True),
        lambda fixture: replace(fixture.stored, signature_verified=True),
        lambda fixture: replace(fixture.stored, artifact_hashes_verified=False),
        lambda fixture: replace(fixture.stored, provider_call_count=1),
        lambda fixture: replace(fixture.stored, network_call_count=1),
        lambda fixture: replace(fixture.stored, gemini_call_count=1),
        lambda fixture: replace(fixture.stored, real_world_effects_count=1),
        lambda fixture: replace(fixture.stored, transaction_id="different_transaction"),
    ),
)
def test_stored_verification_mutations_fail_closed(stored_mutator: object) -> None:
    fixture = _fixture(ledger_contracts.OFFER_A_ID)
    mutated = replace(
        fixture.replay_input,
        stored_verification_report=stored_mutator(fixture),  # type: ignore[operator]
    )
    _assert_fail(_run(mutated))


@pytest.mark.parametrize(
    "fresh_mutator",
    (
        lambda fixture: fixture.stored,
        lambda fixture: replace(fixture.fresh, expected_manifest_core_hash=None),
        lambda fixture: replace(fixture.fresh, expected_manifest_core_hash="0" * 64),
        lambda fixture: replace(fixture.fresh, external_anchor_supplied=False),
        lambda fixture: replace(fixture.fresh, external_anchor_verified=False),
        lambda fixture: replace(fixture.fresh, signature_verified=True),
        lambda fixture: replace(fixture.fresh, chain_order_verified=False),
        lambda fixture: replace(fixture.fresh, provider_call_count=1),
        lambda fixture: replace(fixture.fresh, network_call_count=1),
        lambda fixture: replace(fixture.fresh, gemini_call_count=1),
        lambda fixture: replace(fixture.fresh, real_world_effects_count=1),
        lambda fixture: replace(fixture.fresh, ledger_id="different_ledger"),
    ),
)
def test_fresh_verification_mutations_fail_closed(fresh_mutator: object) -> None:
    fixture = _fixture(ledger_contracts.OFFER_B_ID)
    mutated = replace(
        fixture.replay_input,
        fresh_anchored_verification_report=fresh_mutator(fixture),  # type: ignore[operator]
    )
    _assert_fail(_run(mutated))


def _replace_entry(
    item: ledger_contracts.AirlineTransactionArtifactLedgerV01,
    index: int,
    **changes: object,
) -> ledger_contracts.AirlineTransactionArtifactLedgerV01:
    entries = list(item.entries)
    entries[index] = replace(entries[index], **changes)
    return replace(item, entries=tuple(entries))


def _replace_entry_canonical(
    item: ledger_contracts.AirlineTransactionArtifactLedgerV01,
    index: int,
    canonical: dict[str, object],
) -> ledger_contracts.AirlineTransactionArtifactLedgerV01:
    return _replace_entry(
        item,
        index,
        canonical_hash_input=canonical,
    )


@pytest.mark.parametrize(
    ("field_name", "changed_value"),
    (
        ("transaction_id", "different-transaction"),
        ("ledger_id", "different-ledger"),
        ("source_run_ref", "source_run:different"),
        ("source_causal_report_ref", "source_causal_report:different"),
        ("source_corridor_report_ref", "source_corridor_report:different"),
        ("selected_offer_id", ledger_contracts.OFFER_B_ID),
        ("actual_entry_count", 18),
    ),
)
def test_source_derived_adapter_rejects_audit_ledger_disagreement(
    field_name: str,
    changed_value: object,
) -> None:
    fixture = _source_derived_fixture(ledger_contracts.OFFER_A_ID)
    changed_audit = replace(
        fixture.audit,
        **{field_name: changed_value},
    )
    with pytest.raises(ValueError) as captured:
        replay.build_airline_sealed_trace_replay_expected_identity_adapter_v01(
            ledger_item=fixture.ledger,
            accepted_ledger_audit=changed_audit,
        )
    assert captured.value.args[0] in replay.REPLAY_VALIDATION_REASON_ALLOWLIST


@pytest.mark.parametrize(
    "mutation",
    (
        "ledger_source_refs",
        "artifact_type",
        "artifact_id",
        "source_validation_refs",
        "auxiliary_artifact_refs",
        "missing_extra_key",
        "canonical_source_identity",
    ),
)
def test_source_derived_adapter_rejects_mutated_ledger_identity(
    mutation: str,
) -> None:
    fixture = _source_derived_fixture(ledger_contracts.OFFER_A_ID)
    item = fixture.ledger
    if mutation == "ledger_source_refs":
        changed = replace(item, source_run_ref="source_run:different")
    elif mutation == "artifact_type":
        changed = _replace_entry(
            item,
            1,
            artifact_type=item.entries[0].artifact_type,
        )
    elif mutation == "artifact_id":
        changed = _replace_entry(
            item,
            1,
            artifact_id=item.entries[1].artifact_id + ":changed",
        )
    elif mutation == "source_validation_refs":
        changed = _replace_entry(
            item,
            1,
            source_validation_refs=(
                *item.entries[1].source_validation_refs,
                "source_validation_ref:changed",
            ),
        )
    elif mutation == "auxiliary_artifact_refs":
        changed = _replace_entry(
            item,
            1,
            auxiliary_artifact_refs=("auxiliary_artifact_ref:changed",),
        )
    elif mutation == "missing_extra_key":
        canonical = dict(item.entries[5].canonical_hash_input)
        canonical.pop("selected_offer_id")
        changed = _replace_entry_canonical(item, 5, canonical)
    else:
        canonical = dict(item.entries[7].canonical_hash_input)
        canonical["amount"] = canonical["amount"] + 1  # type: ignore[operator]
        changed = _replace_entry_canonical(item, 7, canonical)

    with pytest.raises(ValueError) as captured:
        replay.build_airline_sealed_trace_replay_expected_identity_adapter_v01(
            ledger_item=changed,
            accepted_ledger_audit=fixture.audit,
        )
    assert captured.value.args[0] in replay.REPLAY_VALIDATION_REASON_ALLOWLIST


@pytest.mark.parametrize(
    "ledger_mutator",
    (
        lambda item: replace(item, entries=item.entries[:-1], entry_count=18),
        lambda item: replace(item, entries=item.entries + (item.entries[-1],), entry_count=20),
        lambda item: _replace_entry(item, 1, ledger_index=2),
        lambda item: _replace_entry(item, 1, ledger_index=True),
        lambda item: _replace_entry(item, 1, artifact_id=item.entries[0].artifact_id),
        lambda item: _replace_entry(item, 1, artifact_type=ledger_contracts.ARTIFACT_AIRLINE_BSEP_PROJECTION),
        lambda item: _replace_entry(item, 1, transaction_id="mixed"),
        lambda item: _replace_entry(item, 0, event_type=ledger_contracts.EVENT_BSEP_PROJECTION_CREATED),
        lambda item: _replace_entry(item, 10, depends_on=("missing",)),
        lambda item: _replace_entry(item, 0, depends_on=(item.entries[1].artifact_id,)),
        lambda item: _replace_entry(item, 1, depends_on=(item.entries[1].artifact_id,)),
        lambda item: _replace_entry(item, 16, artifact_type=ledger_contracts.ARTIFACT_CLIENT_PURCHASE_INTENT),
        lambda item: _replace_entry(item, 17, artifact_type=ledger_contracts.ARTIFACT_CLIENT_ROOT_FINAL),
        lambda item: replace(item, dependency_edge_count=28),
    ),
)
def test_ledger_and_timeline_mutations_return_no_partial_timeline(
    ledger_mutator: object,
) -> None:
    fixture = _fixture(ledger_contracts.OFFER_A_ID)
    mutated_ledger = ledger_mutator(fixture.ledger)  # type: ignore[operator]
    mutated_input = replace(fixture.replay_input, ledger_item=mutated_ledger)
    _assert_fail(_run(mutated_input))
    with pytest.raises(ValueError):
        replay.build_airline_sealed_trace_replay_timeline_v01(mutated_input)


def test_manifest_position_and_hash_mutations_fail_closed() -> None:
    fixture = _fixture(ledger_contracts.OFFER_A_ID)
    refs = list(fixture.envelope.manifest_core.ordered_artifact_refs)
    refs[0] = "different_artifact_ref"
    changed_ref_core = replace(
        fixture.envelope.manifest_core,
        ordered_artifact_refs=tuple(refs),
    )
    changed_ref_envelope = (
        crypto_contracts.build_airline_crypto_artifact_seal_envelope_v01(
            changed_ref_core,
        )
    )
    _assert_fail(
        _run(replace(fixture.replay_input, envelope=changed_ref_envelope)),
    )

    hashes = list(fixture.envelope.manifest_core.ordered_artifact_hashes)
    hashes[0] = "bad"
    changed_hash_core = replace(
        fixture.envelope.manifest_core,
        ordered_artifact_hashes=tuple(hashes),
    )
    changed_hash_envelope = replace(
        fixture.envelope,
        manifest_core=changed_hash_core,
    )
    _assert_fail(
        _run(replace(fixture.replay_input, envelope=changed_hash_envelope)),
        replay.REASON_ENVELOPE_INVALID,
    )


def test_timeline_row_mutations_fail_contract_validation() -> None:
    row = _valid_report(ledger_contracts.OFFER_A_ID).reconstructed_timeline[10]
    mutations = (
        replace(row, dependency_count=row.dependency_count + 1),
        replace(row, replay_index=row.replay_index + 1),
        replace(row, artifact_hash="bad"),
        replace(row, selected_offer_id=""),
        replace(row, replay_index=True),
        replace(row, is_root_final=not row.is_root_final),
        replace(row, depends_on=[]),  # type: ignore[arg-type]
    )
    for mutated in mutations:
        validation = replay.validate_airline_sealed_trace_replay_timeline_row_v01(
            mutated,
        )
        assert validation.validation_status == replay.STATUS_FAIL_CLOSED
        assert validation.validation_errors == (replay.REASON_TIMELINE_ROW_INVALID,)


@pytest.mark.parametrize(
    ("critical", "count", "reason"),
    (
        (False, 1, replay.REASON_CRITICAL_PACKAGE_BYTES_CHANGED),
        ("true", 1, replay.REASON_CRITICAL_PACKAGE_BYTES_CHANGED),
        (True, 0, replay.REASON_POST_REPLAY_SNAPSHOT_CALL_COUNT_MISMATCH),
        (True, 2, replay.REASON_POST_REPLAY_SNAPSHOT_CALL_COUNT_MISMATCH),
        (True, True, replay.REASON_POST_REPLAY_SNAPSHOT_CALL_COUNT_MISMATCH),
    ),
)
def test_lifecycle_evidence_mutations_fail_closed(
    critical: object,
    count: object,
    reason: str,
) -> None:
    fixture = _fixture(ledger_contracts.OFFER_A_ID)
    _assert_fail(
        _run(
            fixture.replay_input,
            critical_package_bytes_unchanged=critical,
            post_replay_snapshot_provider_call_count=count,
        ),
        reason,
    )


@pytest.mark.parametrize(
    ("field_name", "value"),
    (
        ("integrity_verified", False),
        ("timeline_row_count", 18),
        ("source_file_count", 8),
        ("root_attestation_present", True),
        ("signature_verified", True),
        ("transaction_rerun_count", 1),
        ("semantic_rerun_count", 1),
        ("corridor_rerun_count", 1),
        ("ledger_recollection_count", 1),
        ("crypto_collection_count", 1),
        ("provider_call_count", 1),
        ("network_call_count", 1),
        ("gemini_call_count", 1),
        ("replay_created_authority_count", 1),
        ("replay_created_permission_count", 1),
        ("replay_created_action_count", 1),
        ("replay_created_packet_count", 1),
        ("replay_created_receipt_count", 1),
        ("replay_created_final_output_count", 1),
        ("real_world_effects_count", 1),
        ("ledger_audit_count", True),
    ),
)
def test_direct_caller_pass_cannot_survive_contradictory_report_state(
    field_name: str,
    value: object,
) -> None:
    valid = _valid_report(ledger_contracts.OFFER_A_ID)
    _assert_report_replace_rejected(
        valid,
        replay_status=replay.STATUS_PASS,
        verification_errors=(),
        **{field_name: value},
    )


def test_direct_caller_pass_with_partial_timeline_fails_closed() -> None:
    valid = _valid_report(ledger_contracts.OFFER_A_ID)
    _assert_report_replace_rejected(
        valid,
        replay_status=replay.STATUS_PASS,
        reconstructed_timeline=valid.reconstructed_timeline[:-1],
        timeline_row_count=18,
        verification_errors=(),
    )


def test_direct_report_timeline_and_identity_mutations_are_not_trusted() -> None:
    valid = _valid_report(ledger_contracts.OFFER_A_ID)
    reversed_rows = tuple(reversed(valid.reconstructed_timeline))
    swapped_rows = list(valid.reconstructed_timeline)
    swapped_rows[0], swapped_rows[1] = swapped_rows[1], swapped_rows[0]
    duplicate_rows = list(valid.reconstructed_timeline)
    duplicate_rows[1] = duplicate_rows[0]
    changed_hash_rows = list(valid.reconstructed_timeline)
    changed_hash_rows[5] = replace(
        changed_hash_rows[5],
        artifact_hash=changed_hash_rows[6].artifact_hash,
    )
    other_hash = "0" * 64
    mutations = (
        {"reconstructed_timeline": reversed_rows},
        {"reconstructed_timeline": tuple(swapped_rows)},
        {"reconstructed_timeline": tuple(duplicate_rows)},
        {"reconstructed_timeline": tuple(changed_hash_rows)},
        {"source_package_ref": "../bad"},
        {"transaction_id": "different_transaction"},
        {"ledger_id": "different_ledger"},
        {
            "manifest_core_hash": other_hash,
            "expected_manifest_core_hash": other_hash,
        },
        {"integrity_verified": False},
        {"provider_call_count": 1},
    )
    for changes in mutations:
        _assert_report_replace_rejected(valid, **changes)


def test_direct_report_construction_without_private_marker_is_invalid() -> None:
    valid = _valid_report(ledger_contracts.OFFER_A_ID)
    public_values = {
        field.name: getattr(valid, field.name)
        for field in fields(replay.AirlineSealedTraceReplayReportV01)
    }
    with pytest.raises(TypeError):
        replay.AirlineSealedTraceReplayReportV01(
            **public_values,  # type: ignore[arg-type]
        )
    with pytest.raises(TypeError):
        replay.AirlineSealedTraceReplayReportV01(object())  # type: ignore[call-arg]
    direct = object.__new__(replay.AirlineSealedTraceReplayReportV01)
    assert (
        replay.validate_airline_sealed_trace_replay_report_v01(
            direct,
        ).validation_status
        == replay.STATUS_FAIL_CLOSED
    )


def test_report_construction_capability_is_not_publicly_reachable() -> None:
    source = Path(MODULE_PATH).read_text(encoding="utf-8")
    signature = inspect.signature(replay.AirlineSealedTraceReplayReportV01)
    assert not hasattr(replay, "_REPLAY_REPORT_CONSTRUCTION_TOKEN")
    assert "InitVar" not in source
    assert "_construction_token" not in source
    assert "REPLAY_REPORT_CONSTRUCTION_TOKEN" not in source
    assert all(
        "token" not in parameter_name.lower()
        and "capability" not in parameter_name.lower()
        for parameter_name in signature.parameters
    )


def test_private_success_path_revalidates_exact_timeline() -> None:
    fixture = _fixture(ledger_contracts.OFFER_A_ID)
    timeline = replay.build_airline_sealed_trace_replay_timeline_v01(
        fixture.replay_input,
    )
    report = replay._successful_report(
        fixture.replay_input,
        tuple(reversed(timeline)),
        critical_package_bytes_unchanged=True,
        post_replay_snapshot_provider_call_count=1,
    )
    _assert_fail(report, replay.REASON_TIMELINE_INCOMPLETE)


_FAILURE_IDENTITY_FIELDS = (
    "source_package_ref",
    "transaction_id",
    "ledger_id",
    "manifest_core_hash",
    "expected_manifest_core_hash",
    "stored_verification_status",
    "fresh_anchored_verification_status",
    "signature_mode",
)


def _assert_failure_identities_sanitized(
    report: replay.AirlineSealedTraceReplayReportV01,
    marker: str,
) -> None:
    assert report.replay_status == replay.STATUS_FAIL_CLOSED
    assert all(getattr(report, field_name) == "" for field_name in _FAILURE_IDENTITY_FIELDS)
    assert (
        replay.validate_airline_sealed_trace_replay_report_v01(
            report,
        ).validation_status
        == replay.STATUS_PASS
    )
    serialized = json.dumps(
        replay.airline_sealed_trace_replay_report_to_plain_dict_v01(report),
        allow_nan=False,
    )
    assert marker not in serialized


@pytest.mark.parametrize(
    "malformed_package_ref",
    (
        "../bad",
        "/tmp/secret",
        "line1\nline2",
        "API_KEY=secret",
    ),
)
def test_invalid_package_identity_is_discarded_from_honest_failure(
    malformed_package_ref: str,
) -> None:
    fixture = _fixture(ledger_contracts.OFFER_A_ID)
    report = _run(
        replace(
            fixture.replay_input,
            source_package_ref=malformed_package_ref,
        ),
    )
    _assert_failure_identities_sanitized(report, malformed_package_ref)


@pytest.mark.parametrize(
    ("target", "marker"),
    (
        ("ledger_transaction_id", "API_KEY=ledger-transaction"),
        ("ledger_id", "../ledger-id"),
        ("fresh_signature_mode", "credential=fresh-signature"),
        ("stored_verification_status", "raw_prompt=stored-status"),
    ),
)
def test_invalid_nested_identity_is_discarded_from_honest_failure(
    target: str,
    marker: str,
) -> None:
    fixture = _fixture(ledger_contracts.OFFER_A_ID)
    changes: dict[str, object]
    if target == "ledger_transaction_id":
        changes = {"ledger_item": replace(fixture.ledger, transaction_id=marker)}
    elif target == "ledger_id":
        changes = {"ledger_item": replace(fixture.ledger, ledger_id=marker)}
    elif target == "fresh_signature_mode":
        changes = {
            "fresh_anchored_verification_report": _forge_exact_dataclass(
                fixture.fresh,
                signature_mode=marker,
            ),
        }
    else:
        changes = {
            "stored_verification_report": _forge_exact_dataclass(
                fixture.stored,
                verification_status=marker,
            ),
        }
    report = _run(replace(fixture.replay_input, **changes))
    _assert_failure_identities_sanitized(report, marker)


def test_valid_identity_is_preserved_for_later_lifecycle_failure() -> None:
    fixture = _fixture(ledger_contracts.OFFER_A_ID)
    report = _run(
        fixture.replay_input,
        critical_package_bytes_unchanged=False,
    )
    _assert_fail(report, replay.REASON_CRITICAL_PACKAGE_BYTES_CHANGED)
    assert report.source_package_ref == fixture.replay_input.source_package_ref
    assert report.transaction_id == fixture.ledger.transaction_id
    assert report.ledger_id == fixture.ledger.ledger_id
    assert report.manifest_core_hash == fixture.envelope.manifest_core_hash
    assert report.expected_manifest_core_hash == fixture.envelope.manifest_core_hash
    assert (
        report.signature_mode
        == crypto_contracts.SIGNATURE_MODE_UNSIGNED_PLACEHOLDER
    )
    replay.airline_sealed_trace_replay_report_to_plain_dict_v01(report)


def test_report_error_normalization_and_honest_failure_projection() -> None:
    fixture = _fixture(ledger_contracts.OFFER_A_ID)
    honest_failure = _run(
        fixture.replay_input,
        critical_package_bytes_unchanged=False,
    )
    _assert_fail(
        honest_failure,
        replay.REASON_CRITICAL_PACKAGE_BYTES_CHANGED,
    )
    first = replay.airline_sealed_trace_replay_report_to_plain_dict_v01(
        honest_failure,
    )
    second = replay.airline_sealed_trace_replay_report_to_plain_dict_v01(
        honest_failure,
    )
    assert first == second
    assert first is not second


@pytest.mark.parametrize(
    "value",
    (
        None,
        1,
        "input",
        (),
        [],
        {},
        object(),
    ),
)
def test_public_validators_do_not_leak_on_ordinary_malformed_shapes(
    value: object,
) -> None:
    validators = (
        replay.validate_airline_sealed_trace_replay_package_snapshot_v01,
        replay.validate_airline_sealed_trace_replay_input_v01,
        replay.validate_airline_sealed_trace_replay_timeline_row_v01,
        replay.validate_airline_sealed_trace_replay_report_v01,
    )
    for validator in validators:
        report = validator(value)
        assert type(report) is replay.AirlineSealedTraceReplayValidationReportV01
        assert report.validation_status == replay.STATUS_FAIL_CLOSED
    _assert_fail(_run(value))


def test_production_module_static_boundary() -> None:
    source = Path(MODULE_PATH).read_text(encoding="utf-8")
    tree = ast.parse(source)
    forbidden_imports = {
        "pathlib",
        "os",
        "tempfile",
        "subprocess",
        "socket",
        "requests",
        "urllib",
        "random",
        "time",
        "uuid",
        "pickle",
    }
    imported_roots = {
        alias.name.split(".", 1)[0]
        for node in ast.walk(tree)
        if isinstance(node, (ast.Import, ast.ImportFrom))
        for alias in node.names
    }
    assert forbidden_imports.isdisjoint(imported_roots)
    forbidden_names = {
        "open",
        "eval",
        "exec",
        "asdict",
        "verify_airline_crypto_artifact_seal_v01",
        "collect_airline_transaction_artifact_ledger_audit_v01",
        "collect_airline_crypto_artifact_seal_v01",
    }
    called_names = {
        node.func.id
        for node in ast.walk(tree)
        if isinstance(node, ast.Call) and isinstance(node.func, ast.Name)
    }
    attribute_names = {
        node.attr for node in ast.walk(tree) if isinstance(node, ast.Attribute)
    }
    assert forbidden_names.isdisjoint(called_names | attribute_names)
    assert "root_artifact_attestation" not in source
    assert "str(exc)" not in source
    assert "repr(" not in source
    assert ".tmp/" not in source
    assert "29355a3b" not in source
    assert "1c04f0a" not in source
    assert "sealed_trace_replay_collector_v01" not in source
    assert "run_airline_sealed_trace_replay_v01" not in source
    assert "build_airline_sealed_trace_replay_expected_identity_adapter_v01" in source
    ledger_validation_calls = tuple(
        node
        for node in ast.walk(tree)
        if isinstance(node, ast.Call)
        and isinstance(node.func, ast.Attribute)
        and node.func.attr == "validate_airline_transaction_artifact_ledger_v01"
    )
    assert len(ledger_validation_calls) == 2
    assert all(
        any(keyword.arg == "expected_identity" for keyword in call.keywords)
        for call in ledger_validation_calls
    )
    for node in tree.body:
        if isinstance(node, (ast.Assign, ast.AnnAssign)):
            value = node.value
            assert not isinstance(value, (ast.List, ast.Dict, ast.Set))


def test_module_boundary_constants_and_source_sequences() -> None:
    assert replay.MODULE_ID == "airline_sealed_trace_replay_v01"
    assert replay.SLICE_ID == "airline_sealed_trace_replay_v01_slice_b"
    assert replay.REPLAY_VERSION == replay.REPLAY_ID_PREFIX
    assert replay.SOURCE_FILE_COUNT == len(crypto_contracts.REQUIRED_SOURCE_FILE_REFS) == 9
    assert replay.LEDGER_ENTRY_COUNT == len(ledger_contracts.EXPECTED_ARTIFACT_TYPE_SEQUENCE) == 19
    assert replay.DEPENDENCY_EDGE_COUNT == 29
    assert replay.ROOT_FINAL_COUNT == 3
    assert replay.CRITICAL_PACKAGE_FILE_COUNT == 11
