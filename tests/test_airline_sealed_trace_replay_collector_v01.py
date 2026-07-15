from __future__ import annotations

import ast
import json
import traceback
from dataclasses import FrozenInstanceError, dataclass, fields, replace
from pathlib import Path

import pytest

from hedgehog.domains.airline import crypto_artifact_seal_collector_v01 as crypto_collector
from hedgehog.domains.airline import crypto_artifact_seal_v01 as crypto_contracts
from hedgehog.domains.airline import sealed_trace_replay_collector_v01 as collector
from hedgehog.domains.airline import sealed_trace_replay_v01 as replay_contracts
from hedgehog.domains.airline import transaction_artifact_ledger_collector_v01 as ledger_collector
from hedgehog.domains.airline import transaction_artifact_ledger_v01 as ledger_contracts
from tests import test_airline_transaction_artifact_ledger_collector_v01 as ledger_collector_test_helpers


MODULE_PATH = "hedgehog/domains/airline/sealed_trace_replay_collector_v01.py"
PACKAGE_REF = "airline_sealed_trace_replay_slice_c1_fixture"


@dataclass(frozen=True)
class CollectorFixture:
    offer_id: str
    ledger: ledger_contracts.AirlineTransactionArtifactLedgerV01
    fixture_identity: ledger_contracts.AirlineTransactionArtifactLedgerExpectedIdentityV01
    audit: crypto_collector.AirlineCryptoArtifactSealAcceptedLedgerAuditV01
    source_rows: tuple[tuple[str, bytes], ...]
    envelope: crypto_contracts.AirlineCryptoArtifactSealEnvelopeV01
    stored: crypto_contracts.AirlineCryptoArtifactSealVerificationReportV01
    snapshot: replay_contracts.AirlineSealedTraceReplayPackageSnapshotV01


def _json_bytes(value: object) -> bytes:
    return json.dumps(
        value,
        ensure_ascii=False,
        sort_keys=True,
        separators=(",", ":"),
        allow_nan=False,
    ).encode("utf-8")


def _accepted_audit(
    item: ledger_contracts.AirlineTransactionArtifactLedgerV01,
    offer_id: str,
    **changes: object,
) -> crypto_collector.AirlineCryptoArtifactSealAcceptedLedgerAuditV01:
    values: dict[str, object] = {
        "audit_id": crypto_collector.EXPECTED_LEDGER_AUDIT_ID,
        "audit_version": crypto_collector.EXPECTED_LEDGER_AUDIT_VERSION,
        "final_status": collector.STATUS_PASS,
        "required_source_files": crypto_contracts.REQUIRED_SOURCE_FILE_REFS,
        "files_read_count": replay_contracts.SOURCE_FILE_COUNT,
        "ledger_id": item.ledger_id,
        "transaction_id": item.transaction_id,
        "selected_offer_id": offer_id,
        "source_run_ref": item.source_run_ref,
        "source_causal_report_ref": item.source_causal_report_ref,
        "source_corridor_report_ref": item.source_corridor_report_ref,
        "actual_entry_count": replay_contracts.LEDGER_ENTRY_COUNT,
        "actual_dependency_edge_count": replay_contracts.DEPENDENCY_EDGE_COUNT,
        "actual_root_final_count": replay_contracts.ROOT_FINAL_COUNT,
        "client_root_final_count": 1,
        "airline_root_final_count": 1,
        "bank_root_final_count": 1,
        **{
            name: True for name in crypto_collector.ACCEPTED_AUDIT_BOOLEAN_FIELDS
        },
        "stored_validation_status": collector.STATUS_PASS,
        "stored_validation_errors": (),
        **{
            name: 0 for name in crypto_collector.ACCEPTED_AUDIT_ZERO_COUNTER_FIELDS
        },
        "validation_errors": (),
    }
    values.update(changes)
    return crypto_collector.AirlineCryptoArtifactSealAcceptedLedgerAuditV01(
        **values,  # type: ignore[arg-type]
    )


def _ledger_plain(
    item: ledger_contracts.AirlineTransactionArtifactLedgerV01,
    identity: ledger_contracts.AirlineTransactionArtifactLedgerExpectedIdentityV01,
) -> dict[str, object]:
    return crypto_collector.airline_crypto_artifact_seal_ledger_document_to_plain_dict_v01(
        item,
        expected_identity=identity,
    )


def _source_rows(
    item: ledger_contracts.AirlineTransactionArtifactLedgerV01,
    identity: ledger_contracts.AirlineTransactionArtifactLedgerExpectedIdentityV01,
    *,
    source_variant: str = "",
) -> tuple[tuple[str, bytes], ...]:
    rows: list[tuple[str, bytes]] = []
    for index, relative_ref in enumerate(crypto_contracts.REQUIRED_SOURCE_FILE_REFS):
        source_document = {
            "fixture_index": index,
            "offer_id": identity.expected_artifact_ids[
                ledger_contracts.ARTIFACT_VALIDATED_CANONICAL_SEMANTIC_EVIDENCE
            ],
            "source_file_ref": relative_ref,
            "transaction_id": item.transaction_id,
        }
        if source_variant and index == 1:
            source_document["source_variant"] = source_variant
        content = (
            _json_bytes(_ledger_plain(item, identity))
            if relative_ref == collector.LEDGER_SOURCE_ARTIFACT_REF
            else crypto_contracts.canonical_airline_crypto_json_bytes_v01(source_document)
        )
        rows.append((relative_ref, content))
    return tuple(rows)


def _manifest_plain(
    envelope: crypto_contracts.AirlineCryptoArtifactSealEnvelopeV01,
) -> dict[str, object]:
    return {
        "manifest_core": (
            crypto_contracts.airline_crypto_artifact_seal_manifest_core_to_plain_dict_v01(
                envelope.manifest_core,
            )
        ),
        "manifest_core_hash": envelope.manifest_core_hash,
        "signature": {
            "mode": envelope.signature.mode,
            "algorithm": envelope.signature.algorithm,
            "key_id": envelope.signature.key_id,
            "value": envelope.signature.value,
            "verified": envelope.signature.verified,
        },
    }


def _fixture(
    offer_id: str,
    package_ref: str = PACKAGE_REF,
    *,
    source_variant: str = "",
) -> CollectorFixture:
    item = ledger_contracts.build_airline_transaction_artifact_ledger_fixture_v01(
        offer_id=offer_id,
    )
    identity = (
        ledger_contracts.build_airline_transaction_artifact_ledger_fixture_expected_identity_v01(
            offer_id=offer_id,
        )
    )
    rows = _source_rows(item, identity, source_variant=source_variant)
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
    snapshot = replay_contracts.build_airline_sealed_trace_replay_package_snapshot_v01(
        source_package_ref=package_ref,
        ordered_source_files=rows,
        manifest_artifact_ref=replay_contracts.MANIFEST_ARTIFACT_REF,
        manifest_bytes=_json_bytes(_manifest_plain(envelope)),
        stored_verification_artifact_ref=(
            replay_contracts.STORED_VERIFICATION_ARTIFACT_REF
        ),
        stored_verification_bytes=_json_bytes(
            crypto_contracts.airline_crypto_artifact_seal_verification_report_to_plain_dict_v01(
                stored,
            ),
        ),
    )
    return CollectorFixture(
        offer_id=offer_id,
        ledger=item,
        fixture_identity=identity,
        audit=_accepted_audit(item, offer_id),
        source_rows=rows,
        envelope=envelope,
        stored=stored,
        snapshot=snapshot,
    )


def _source_derived_fixture(offer_id: str) -> CollectorFixture:
    source_bundle = (
        ledger_collector_test_helpers._source_bundle_from_public_causal_runtime(
            offer_id,
        )
    )
    item = ledger_collector.collect_airline_transaction_artifact_ledger_from_source_v01(
        source_bundle=source_bundle,
    )
    audit = _accepted_audit(item, offer_id)
    identity = (
        replay_contracts.build_airline_sealed_trace_replay_expected_identity_adapter_v01(
            ledger_item=item,
            accepted_ledger_audit=audit,
        )
    )
    package_ref = (
        "airline_sealed_trace_replay_c1_source_derived_a"
        if offer_id == ledger_contracts.OFFER_A_ID
        else "airline_sealed_trace_replay_c1_source_derived_b"
    )
    rows = _source_rows(item, identity)
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
    snapshot = replay_contracts.build_airline_sealed_trace_replay_package_snapshot_v01(
        source_package_ref=package_ref,
        ordered_source_files=rows,
        manifest_artifact_ref=replay_contracts.MANIFEST_ARTIFACT_REF,
        manifest_bytes=_json_bytes(_manifest_plain(envelope)),
        stored_verification_artifact_ref=(
            replay_contracts.STORED_VERIFICATION_ARTIFACT_REF
        ),
        stored_verification_bytes=_json_bytes(
            crypto_contracts.airline_crypto_artifact_seal_verification_report_to_plain_dict_v01(
                stored,
            ),
        ),
    )
    return CollectorFixture(
        offer_id=offer_id,
        ledger=item,
        fixture_identity=identity,
        audit=audit,
        source_rows=rows,
        envelope=envelope,
        stored=stored,
        snapshot=snapshot,
    )


def _collect(
    fixture: CollectorFixture,
    *,
    snapshot: object | None = None,
    audit: object | None = None,
    expected_hash: object | None = None,
    provider: object | None = None,
) -> replay_contracts.AirlineSealedTraceReplayReportV01:
    actual_snapshot = fixture.snapshot if snapshot is None else snapshot
    actual_provider = (
        (lambda: fixture.snapshot) if provider is None else provider
    )
    return collector.collect_airline_sealed_trace_replay_from_package_snapshot_v01(
        package_snapshot=actual_snapshot,
        accepted_ledger_audit=fixture.audit if audit is None else audit,
        expected_manifest_core_hash=(
            fixture.envelope.manifest_core_hash
            if expected_hash is None
            else expected_hash
        ),
        post_replay_snapshot_provider=actual_provider,
    )


def _assert_reason(reason: str, action: object) -> ValueError:
    with pytest.raises(ValueError) as captured:
        action()  # type: ignore[operator]
    error = captured.value
    assert type(error) is ValueError
    assert error.args == (reason,)
    assert error.__cause__ is None
    assert error.__context__ is None
    assert str(error) == reason
    assert reason in repr(error)
    assert error.args[0] in collector.REPLAY_COLLECTION_REASON_ALLOWLIST
    return error


def _assert_secret_free_error(error: ValueError) -> None:
    formatted = "".join(traceback.format_exception(error))
    for rendered in (
        str(error),
        repr(error),
        formatted,
        "".join(str(item) for item in error.args),
    ):
        assert "API_KEY=TOP_SECRET" not in rendered


def _snapshot_with_rows(
    fixture: CollectorFixture,
    rows: tuple[tuple[str, bytes], ...],
) -> replay_contracts.AirlineSealedTraceReplayPackageSnapshotV01:
    return replace(fixture.snapshot, ordered_source_files=rows)


def _snapshot_with_ledger_bytes(
    fixture: CollectorFixture,
    ledger_bytes: bytes,
) -> replay_contracts.AirlineSealedTraceReplayPackageSnapshotV01:
    rows = list(fixture.source_rows)
    rows[0] = (collector.LEDGER_SOURCE_ARTIFACT_REF, ledger_bytes)
    return _snapshot_with_rows(fixture, tuple(rows))


def _snapshot_with_manifest_plain(
    fixture: CollectorFixture,
    manifest_plain: object,
) -> replay_contracts.AirlineSealedTraceReplayPackageSnapshotV01:
    return replace(fixture.snapshot, manifest_bytes=_json_bytes(manifest_plain))


def _snapshot_with_stored_plain(
    fixture: CollectorFixture,
    stored_plain: object,
) -> replay_contracts.AirlineSealedTraceReplayPackageSnapshotV01:
    return replace(
        fixture.snapshot,
        stored_verification_bytes=_json_bytes(stored_plain),
    )


def test_reason_allowlist_is_exact_unique_and_immutable() -> None:
    expected = tuple(
        getattr(collector, name)
        for name in (
            "REASON_PACKAGE_SNAPSHOT_INVALID",
            "REASON_ACCEPTED_LEDGER_AUDIT_INVALID",
            "REASON_EXPECTED_MANIFEST_CORE_HASH_INVALID",
            "REASON_LEDGER_DOCUMENT_MISSING",
            "REASON_LEDGER_DOCUMENT_PARSE_FAILED",
            "REASON_LEDGER_DOCUMENT_FIELD_MISMATCH",
            "REASON_LEDGER_DOCUMENT_RECONSTRUCTION_FAILED",
            "REASON_LEDGER_DOCUMENT_PROJECTION_MISMATCH",
            "REASON_MANIFEST_DOCUMENT_PARSE_FAILED",
            "REASON_MANIFEST_DOCUMENT_FIELD_MISMATCH",
            "REASON_MANIFEST_DOCUMENT_RECONSTRUCTION_FAILED",
            "REASON_MANIFEST_DOCUMENT_PROJECTION_MISMATCH",
            "REASON_STORED_VERIFICATION_DOCUMENT_PARSE_FAILED",
            "REASON_STORED_VERIFICATION_DOCUMENT_FIELD_MISMATCH",
            "REASON_STORED_VERIFICATION_RECONSTRUCTION_FAILED",
            "REASON_STORED_VERIFICATION_PROJECTION_MISMATCH",
            "REASON_EXPECTED_IDENTITY_ADAPTER_FAILED",
            "REASON_LEDGER_VALIDATION_FAILED",
            "REASON_AUDIT_LEDGER_IDENTITY_MISMATCH",
            "REASON_FRESH_ANCHORED_VERIFICATION_FAILED",
            "REASON_REPLAY_INPUT_BUILD_FAILED",
            "REASON_TIMELINE_RECONSTRUCTION_FAILED",
            "REASON_POST_REPLAY_SNAPSHOT_PROVIDER_INVALID",
            "REASON_POST_REPLAY_SNAPSHOT_PROVIDER_FAILED",
            "REASON_POST_REPLAY_SNAPSHOT_WRONG_TYPE",
            "REASON_POST_REPLAY_SNAPSHOT_MISMATCH",
            "REASON_PURE_REPLAY_FAILED",
        )
    )
    assert collector.REPLAY_COLLECTION_REASON_ALLOWLIST == expected
    assert type(expected) is tuple
    assert len(expected) == len(set(expected))


@pytest.mark.parametrize(
    "offer_id",
    (ledger_contracts.OFFER_A_ID, ledger_contracts.OFFER_B_ID),
)
def test_offer_exact_package_collection_passes(offer_id: str) -> None:
    fixture = _fixture(offer_id)
    callback_count = 0

    def observe() -> object:
        nonlocal callback_count
        callback_count += 1
        return fixture.snapshot

    report = _collect(fixture, provider=observe)
    assert report.replay_status == collector.STATUS_PASS
    assert report.source_package_ref == fixture.snapshot.source_package_ref
    assert report.transaction_id == fixture.ledger.transaction_id
    assert report.ledger_id == fixture.ledger.ledger_id
    assert report.manifest_core_hash == fixture.envelope.manifest_core_hash
    assert report.expected_manifest_core_hash == fixture.envelope.manifest_core_hash
    assert report.replay_version == replay_contracts.REPLAY_VERSION
    assert report.replay_id == (
        replay_contracts.REPLAY_ID_PREFIX
        + ":"
        + fixture.ledger.transaction_id
        + ":"
        + fixture.envelope.manifest_core_hash
    )
    assert callback_count == 1
    assert report.reconstructed_timeline
    assert len(report.reconstructed_timeline) == 19
    assert (report.ledger_entry_count, report.dependency_edge_count, report.root_final_count) == (19, 29, 3)
    assert (report.source_file_count, report.critical_package_file_count) == (9, 11)
    assert report.stored_verification_status == crypto_contracts.STATUS_SELF_CONSISTENT_UNANCHORED
    assert report.fresh_anchored_verification_status == collector.STATUS_PASS
    assert report.external_anchor_supplied is True
    assert report.external_anchor_verified is True
    assert report.signature_verified is False
    assert report.source_bytes_unchanged is True
    assert report.critical_package_bytes_unchanged is True
    assert report.root_attestation_required is False
    assert report.root_attestation_present is False


@pytest.mark.parametrize(
    "sequence",
    (
        (ledger_contracts.OFFER_A_ID, ledger_contracts.OFFER_B_ID, ledger_contracts.OFFER_A_ID),
        (ledger_contracts.OFFER_B_ID, ledger_contracts.OFFER_A_ID, ledger_contracts.OFFER_B_ID),
    ),
)
def test_collection_isolation_and_determinism(sequence: tuple[str, ...]) -> None:
    reports = tuple(_collect(_fixture(offer_id)) for offer_id in sequence)
    assert reports[0] == reports[2]
    assert reports[0] != reports[1]
    assert reports[0].replay_id == reports[2].replay_id


@pytest.mark.parametrize(
    "offer_id",
    (ledger_contracts.OFFER_A_ID, ledger_contracts.OFFER_B_ID),
)
def test_exact_persisted_contract_reconstruction(offer_id: str) -> None:
    fixture = _fixture(offer_id)
    ledger_item, ledger_plain = collector._reconstruct_ledger(fixture.snapshot)
    envelope, manifest_plain = collector._reconstruct_envelope(
        fixture.snapshot,
        ledger_item,
    )
    stored, stored_plain = collector._reconstruct_stored_verification(
        fixture.snapshot,
        ledger_item,
        envelope,
    )
    assert type(ledger_item) is ledger_contracts.AirlineTransactionArtifactLedgerV01
    assert ledger_item == fixture.ledger
    assert ledger_plain == _ledger_plain(fixture.ledger, fixture.fixture_identity)
    assert envelope == fixture.envelope
    assert manifest_plain == _manifest_plain(fixture.envelope)
    assert stored == fixture.stored
    assert stored_plain == crypto_contracts.airline_crypto_artifact_seal_verification_report_to_plain_dict_v01(fixture.stored)


@pytest.mark.parametrize(
    "offer_id",
    (ledger_contracts.OFFER_A_ID, ledger_contracts.OFFER_B_ID),
)
def test_expected_identity_adapter_exact_coverage_and_validation(offer_id: str) -> None:
    fixture = _fixture(offer_id)
    reconstructed, _ = collector._reconstruct_ledger(fixture.snapshot)
    adapter = collector.build_airline_sealed_trace_replay_expected_identity_adapter_v01(
        ledger_item=reconstructed,
        accepted_ledger_audit=fixture.audit,
    )
    assert type(adapter) is ledger_contracts.AirlineTransactionArtifactLedgerExpectedIdentityV01
    assert collector.EXPECTED_IDENTITY_ROLE == "verifier_contract_adapter_after_independent_ledger_audit"
    assert tuple(adapter.expected_artifact_ids) == ledger_contracts.EXPECTED_ARTIFACT_TYPE_SEQUENCE
    assert len(adapter.expected_artifact_ids) == 19
    assert len(adapter.expected_source_validation_refs_by_type) == 19
    assert len(adapter.expected_auxiliary_artifact_refs_by_type) == 19
    assert len(adapter.expected_source_identity_fields_by_type) == 19
    for entry in reconstructed.entries:
        artifact_type = entry.artifact_type
        assert adapter.expected_artifact_ids[artifact_type] == entry.artifact_id
        assert adapter.expected_source_validation_refs_by_type[artifact_type] == entry.source_validation_refs
        assert adapter.expected_auxiliary_artifact_refs_by_type[artifact_type] == entry.auxiliary_artifact_refs
        assert tuple(adapter.expected_source_identity_fields_by_type[artifact_type]) == ledger_contracts.CANONICAL_HASH_INPUT_EXTRA_KEYS_BY_ARTIFACT_TYPE[artifact_type]
    validation = ledger_contracts.validate_airline_transaction_artifact_ledger_v01(
        reconstructed,
        expected_identity=adapter,
    )
    assert validation.validation_status == collector.STATUS_PASS


@pytest.mark.parametrize(
    "offer_id",
    (ledger_contracts.OFFER_A_ID, ledger_contracts.OFFER_B_ID),
)
def test_source_derived_c1_adapter_and_collection_pass(
    offer_id: str,
) -> None:
    fixture = _source_derived_fixture(offer_id)
    reconstructed, _ = collector._reconstruct_ledger(fixture.snapshot)
    canonical_adapter = (
        replay_contracts.build_airline_sealed_trace_replay_expected_identity_adapter_v01(
            ledger_item=reconstructed,
            accepted_ledger_audit=fixture.audit,
        )
    )
    compatibility_adapter = (
        collector.build_airline_sealed_trace_replay_expected_identity_adapter_v01(
            ledger_item=reconstructed,
            accepted_ledger_audit=fixture.audit,
        )
    )
    validation = ledger_contracts.validate_airline_transaction_artifact_ledger_v01(
        reconstructed,
        expected_identity=canonical_adapter,
    )
    report = _collect(fixture)

    assert collector.EXPECTED_IDENTITY_ROLE == replay_contracts.EXPECTED_IDENTITY_ROLE
    assert canonical_adapter == compatibility_adapter == fixture.fixture_identity
    assert validation.validation_status == collector.STATUS_PASS
    assert validation.validation_errors == ()
    assert report.replay_status == collector.STATUS_PASS
    assert len(report.reconstructed_timeline) == 19
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
    assert report.fresh_anchored_verification_status == collector.STATUS_PASS
    assert report.external_anchor_supplied is True
    assert report.external_anchor_verified is True
    assert report.signature_verified is False
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
def test_source_derived_c1_isolation_and_repeated_equality(
    sequence: tuple[str, ...],
) -> None:
    fixtures = tuple(_source_derived_fixture(offer_id) for offer_id in sequence)
    adapters = tuple(
        collector.build_airline_sealed_trace_replay_expected_identity_adapter_v01(
            ledger_item=fixture.ledger,
            accepted_ledger_audit=fixture.audit,
        )
        for fixture in fixtures
    )
    reports = tuple(_collect(fixture) for fixture in fixtures)
    projections = tuple(
        replay_contracts.airline_sealed_trace_replay_report_to_plain_dict_v01(
            report,
        )
        for report in reports
    )

    assert adapters[0] == adapters[2]
    assert reports[0] == reports[2]
    assert projections[0] == projections[2]
    assert reports[0] != reports[1]
    assert projections[0] is not projections[2]


def test_source_derived_c1_never_uses_fixture_default_identity(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    fixture = _source_derived_fixture(ledger_contracts.OFFER_B_ID)

    def forbidden_fixture_identity(*args: object, **kwargs: object) -> object:
        raise AssertionError("fixture_default_identity_forbidden")

    monkeypatch.setattr(
        ledger_contracts,
        "build_airline_transaction_artifact_ledger_fixture_expected_identity_v01",
        forbidden_fixture_identity,
    )
    assert _collect(fixture).replay_status == collector.STATUS_PASS


def test_success_calls_b2b_callback_and_pure_replay_once(monkeypatch: pytest.MonkeyPatch) -> None:
    fixture = _fixture(ledger_contracts.OFFER_A_ID)
    counts = {"b2b": 0, "callback": 0, "pure": 0}
    original_b2b = crypto_contracts.verify_airline_crypto_artifact_seal_v01
    original_pure = replay_contracts.verify_airline_sealed_trace_replay_v01

    def b2b(*args: object, **kwargs: object) -> object:
        counts["b2b"] += 1
        return original_b2b(*args, **kwargs)

    def pure(*args: object, **kwargs: object) -> object:
        counts["pure"] += 1
        return original_pure(*args, **kwargs)

    def observe() -> object:
        counts["callback"] += 1
        return fixture.snapshot

    monkeypatch.setattr(collector.crypto_contracts, "verify_airline_crypto_artifact_seal_v01", b2b)
    monkeypatch.setattr(collector.replay_contracts, "verify_airline_sealed_trace_replay_v01", pure)
    assert _collect(fixture, provider=observe).replay_status == collector.STATUS_PASS
    assert counts == {"b2b": 1, "callback": 1, "pure": 1}


def test_report_projection_is_independent_and_all_operation_counts_are_zero() -> None:
    report = _collect(_fixture(ledger_contracts.OFFER_A_ID))
    first = replay_contracts.airline_sealed_trace_replay_report_to_plain_dict_v01(report)
    second = replay_contracts.airline_sealed_trace_replay_report_to_plain_dict_v01(report)
    assert first == second
    assert first is not second
    first["reconstructed_timeline"][0]["depends_on"].append("changed")  # type: ignore[index,union-attr]
    assert first != second
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
        assert getattr(report, field_name) == 0
    with pytest.raises(FrozenInstanceError):
        report.source_package_ref = "changed"  # type: ignore[misc]


@pytest.mark.parametrize(
    ("snapshot", "audit", "anchor", "provider", "reason"),
    (
        (object(), None, None, None, collector.REASON_PACKAGE_SNAPSHOT_INVALID),
        (None, object(), None, None, collector.REASON_ACCEPTED_LEDGER_AUDIT_INVALID),
        (None, None, 1, None, collector.REASON_EXPECTED_MANIFEST_CORE_HASH_INVALID),
        (None, None, "bad", None, collector.REASON_EXPECTED_MANIFEST_CORE_HASH_INVALID),
        (None, None, None, object(), collector.REASON_POST_REPLAY_SNAPSHOT_PROVIDER_INVALID),
    ),
)
def test_input_gates_fail_before_collection(
    snapshot: object,
    audit: object,
    anchor: object,
    provider: object,
    reason: str,
) -> None:
    fixture = _fixture(ledger_contracts.OFFER_A_ID)
    actual_snapshot = fixture.snapshot if snapshot is None else snapshot
    actual_audit = fixture.audit if audit is None else audit
    actual_anchor = fixture.envelope.manifest_core_hash if anchor is None else anchor
    actual_provider = (lambda: fixture.snapshot) if provider is None else provider
    _assert_reason(
        reason,
        lambda: collector.collect_airline_sealed_trace_replay_from_package_snapshot_v01(
            package_snapshot=actual_snapshot,
            accepted_ledger_audit=actual_audit,
            expected_manifest_core_hash=actual_anchor,
            post_replay_snapshot_provider=actual_provider,
        ),
    )


def test_missing_anchor_stops_all_later_stages(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    fixture = _fixture(ledger_contracts.OFFER_A_ID)
    counts = {"b2b": 0, "callback": 0, "pure": 0}

    def b2b(*args: object, **kwargs: object) -> object:
        counts["b2b"] += 1
        return object()

    def observe() -> object:
        counts["callback"] += 1
        return fixture.snapshot

    def pure(*args: object, **kwargs: object) -> object:
        counts["pure"] += 1
        return object()

    monkeypatch.setattr(
        collector.crypto_contracts,
        "verify_airline_crypto_artifact_seal_v01",
        b2b,
    )
    monkeypatch.setattr(
        collector.replay_contracts,
        "verify_airline_sealed_trace_replay_v01",
        pure,
    )
    error = _assert_reason(
        collector.REASON_EXPECTED_MANIFEST_CORE_HASH_INVALID,
        lambda: collector.collect_airline_sealed_trace_replay_from_package_snapshot_v01(
            package_snapshot=fixture.snapshot,
            accepted_ledger_audit=fixture.audit,
            expected_manifest_core_hash=None,
            post_replay_snapshot_provider=observe,
        ),
    )
    _assert_secret_free_error(error)
    assert counts == {"b2b": 0, "callback": 0, "pure": 0}


@pytest.mark.parametrize(
    ("changes", "reason"),
    (
        ({"manifest_artifact_ref": "wrong.json"}, collector.REASON_PACKAGE_SNAPSHOT_INVALID),
        ({"stored_verification_artifact_ref": "wrong.json"}, collector.REASON_PACKAGE_SNAPSHOT_INVALID),
        ({"manifest_bytes": bytearray(b"x")}, collector.REASON_PACKAGE_SNAPSHOT_INVALID),
        ({"stored_verification_bytes": memoryview(b"x")}, collector.REASON_PACKAGE_SNAPSHOT_INVALID),
    ),
)
def test_invalid_snapshot_contract_fails_gate(changes: dict[str, object], reason: str) -> None:
    fixture = _fixture(ledger_contracts.OFFER_A_ID)
    invalid = replay_contracts.AirlineSealedTraceReplayPackageSnapshotV01(
        source_package_ref=fixture.snapshot.source_package_ref,
        ordered_source_files=fixture.snapshot.ordered_source_files,
        manifest_artifact_ref=changes.get("manifest_artifact_ref", fixture.snapshot.manifest_artifact_ref),  # type: ignore[arg-type]
        manifest_bytes=changes.get("manifest_bytes", fixture.snapshot.manifest_bytes),  # type: ignore[arg-type]
        stored_verification_artifact_ref=changes.get("stored_verification_artifact_ref", fixture.snapshot.stored_verification_artifact_ref),  # type: ignore[arg-type]
        stored_verification_bytes=changes.get("stored_verification_bytes", fixture.snapshot.stored_verification_bytes),  # type: ignore[arg-type]
    )
    _assert_reason(reason, lambda: _collect(fixture, snapshot=invalid))


@pytest.mark.parametrize(
    "audit_changes",
    (
        {"final_status": collector.STATUS_FAIL_CLOSED},
        {"required_source_files": tuple(reversed(crypto_contracts.REQUIRED_SOURCE_FILE_REFS))},
        {"actual_entry_count": 18},
        {"artifact_ids_unique": False},
        {"provider_call_count": 1},
    ),
)
def test_invalid_accepted_audit_fails_gate(audit_changes: dict[str, object]) -> None:
    fixture = _fixture(ledger_contracts.OFFER_A_ID)
    invalid = replace(fixture.audit, **audit_changes)
    _assert_reason(
        collector.REASON_ACCEPTED_LEDGER_AUDIT_INVALID,
        lambda: _collect(fixture, audit=invalid),
    )


@pytest.mark.parametrize(
    "ledger_bytes",
    (
        b"\xff",
        b"\xef\xbb\xbf{}",
        b"{",
        b'{"ledger_id":"a","ledger_id":"b"}',
        b"[]",
    ),
)
def test_ledger_parse_failures_are_stable(ledger_bytes: bytes) -> None:
    fixture = _fixture(ledger_contracts.OFFER_A_ID)
    snapshot = _snapshot_with_ledger_bytes(fixture, ledger_bytes)
    _assert_reason(
        collector.REASON_LEDGER_DOCUMENT_PARSE_FAILED,
        lambda: _collect(fixture, snapshot=snapshot),
    )


def test_private_ledger_reconstruction_rejects_missing_exact_row() -> None:
    fixture = _fixture(ledger_contracts.OFFER_A_ID)
    missing = replace(
        fixture.snapshot,
        ordered_source_files=fixture.snapshot.ordered_source_files[1:],
    )
    _assert_reason(
        collector.REASON_LEDGER_DOCUMENT_MISSING,
        lambda: collector._reconstruct_ledger(missing),
    )


def test_ledger_projection_mismatch_is_stable(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    fixture = _fixture(ledger_contracts.OFFER_A_ID)
    monkeypatch.setattr(collector, "_ledger_to_plain_dict", lambda item: {})
    _assert_reason(
        collector.REASON_LEDGER_DOCUMENT_PROJECTION_MISMATCH,
        lambda: collector._reconstruct_ledger(fixture.snapshot),
    )


@pytest.mark.parametrize(
    "mutator",
    (
        lambda plain: plain.pop("ledger_id"),
        lambda plain: plain.update({"extra": 1}),
        lambda plain: plain.update({"entries": {}}),
        lambda plain: plain["entries"][0].pop("artifact_id"),
        lambda plain: plain["entries"][0].update({"extra": 1}),
        lambda plain: plain["entries"][0].update({"depends_on": "bad"}),
    ),
)
def test_ledger_field_mutations_fail_closed(mutator: object) -> None:
    fixture = _fixture(ledger_contracts.OFFER_A_ID)
    plain = json.loads(fixture.source_rows[0][1])
    mutator(plain)  # type: ignore[operator]
    snapshot = _snapshot_with_ledger_bytes(fixture, _json_bytes(plain))
    _assert_reason(
        collector.REASON_LEDGER_DOCUMENT_FIELD_MISMATCH,
        lambda: _collect(fixture, snapshot=snapshot),
    )


@pytest.mark.parametrize("entry_delta", (-1, 1))
def test_ledger_geometry_mutations_fail_before_b2b(
    entry_delta: int,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    fixture = _fixture(ledger_contracts.OFFER_A_ID)
    plain = json.loads(fixture.source_rows[0][1])
    if entry_delta < 0:
        plain["entries"] = plain["entries"][:-1]
    else:
        extra = dict(plain["entries"][-1])
        extra["ledger_index"] = 19
        extra["artifact_id"] = "extra-artifact"
        plain["entries"].append(extra)
    snapshot = _snapshot_with_ledger_bytes(fixture, _json_bytes(plain))
    calls = 0

    def forbidden(*args: object, **kwargs: object) -> object:
        nonlocal calls
        calls += 1
        return fixture.stored

    monkeypatch.setattr(collector.crypto_contracts, "verify_airline_crypto_artifact_seal_v01", forbidden)
    with pytest.raises(ValueError):
        _collect(fixture, snapshot=snapshot)
    assert calls == 0


@pytest.mark.parametrize(
    "manifest_bytes",
    (b"\xff", b"\xef\xbb\xbf{}", b"{", b'{"x":1,"x":2}'),
)
def test_manifest_parse_failures_are_stable(manifest_bytes: bytes) -> None:
    fixture = _fixture(ledger_contracts.OFFER_A_ID)
    snapshot = replace(fixture.snapshot, manifest_bytes=manifest_bytes)
    _assert_reason(
        collector.REASON_MANIFEST_DOCUMENT_PARSE_FAILED,
        lambda: _collect(fixture, snapshot=snapshot),
    )


def test_parser_exception_details_are_not_retained() -> None:
    fixture = _fixture(ledger_contracts.OFFER_A_ID)
    ledger_error = _assert_reason(
        collector.REASON_LEDGER_DOCUMENT_PARSE_FAILED,
        lambda: _collect(
            fixture,
            snapshot=_snapshot_with_ledger_bytes(fixture, b"\xff"),
        ),
    )
    manifest_error = _assert_reason(
        collector.REASON_MANIFEST_DOCUMENT_PARSE_FAILED,
        lambda: _collect(
            fixture,
            snapshot=replace(fixture.snapshot, manifest_bytes=b"{"),
        ),
    )
    formatted = "".join(
        traceback.format_exception_only(ledger_error)
        + traceback.format_exception_only(manifest_error)
        + traceback.format_exception(ledger_error)
        + traceback.format_exception(manifest_error),
    )
    for forbidden in (
        "UnicodeDecodeError",
        "JSONDecodeError",
        "invalid start byte",
        "Expecting property name",
    ):
        assert forbidden not in formatted


@pytest.mark.parametrize(
    "mutator",
    (
        lambda plain: plain.pop("manifest_core"),
        lambda plain: plain.update({"extra": 1}),
        lambda plain: plain["manifest_core"].pop("seal_id"),
        lambda plain: plain["manifest_core"].update({"extra": 1}),
        lambda plain: plain["signature"].pop("mode"),
        lambda plain: plain["signature"].update({"extra": 1}),
    ),
)
def test_manifest_field_mutations_fail_closed(mutator: object) -> None:
    fixture = _fixture(ledger_contracts.OFFER_A_ID)
    plain = _manifest_plain(fixture.envelope)
    mutator(plain)  # type: ignore[operator]
    snapshot = _snapshot_with_manifest_plain(fixture, plain)
    _assert_reason(
        collector.REASON_MANIFEST_DOCUMENT_FIELD_MISMATCH,
        lambda: _collect(fixture, snapshot=snapshot),
    )


@pytest.mark.parametrize(
    "mutator",
    (
        lambda plain: plain.update({"manifest_core_hash": "0" * 64}),
        lambda plain: plain["manifest_core"].update({"transaction_id": "wrong"}),
        lambda plain: plain["manifest_core"].update({"ledger_id": "wrong"}),
        lambda plain: plain["manifest_core"].update({"source_package_ref": "wrong-package"}),
        lambda plain: plain["manifest_core"]["ordered_source_file_refs"].append("extra.json"),
        lambda plain: plain["manifest_core"]["ordered_artifact_refs"].append("extra-artifact"),
        lambda plain: plain["signature"].update({"verified": True}),
    ),
)
def test_manifest_contract_mutations_fail_closed(mutator: object) -> None:
    fixture = _fixture(ledger_contracts.OFFER_A_ID)
    plain = _manifest_plain(fixture.envelope)
    mutator(plain)  # type: ignore[operator]
    snapshot = _snapshot_with_manifest_plain(fixture, plain)
    _assert_reason(
        collector.REASON_MANIFEST_DOCUMENT_RECONSTRUCTION_FAILED,
        lambda: _collect(fixture, snapshot=snapshot),
    )


def test_manifest_projection_mismatch_is_stable(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    fixture = _fixture(ledger_contracts.OFFER_A_ID)
    ledger_item, _ = collector._reconstruct_ledger(fixture.snapshot)
    original = (
        crypto_contracts.airline_crypto_artifact_seal_manifest_core_to_plain_dict_v01
    )
    call_count = 0

    def count_calls(core: object) -> object:
        nonlocal call_count
        call_count += 1
        return original(core)  # type: ignore[arg-type]

    monkeypatch.setattr(
        collector.crypto_contracts,
        "airline_crypto_artifact_seal_manifest_core_to_plain_dict_v01",
        count_calls,
    )
    collector._reconstruct_envelope(fixture.snapshot, ledger_item)
    final_projection_call = call_count
    call_count = 0

    def mismatch_final_projection(core: object) -> object:
        nonlocal call_count
        call_count += 1
        if call_count == final_projection_call:
            return {}
        return original(core)  # type: ignore[arg-type]

    monkeypatch.setattr(
        collector.crypto_contracts,
        "airline_crypto_artifact_seal_manifest_core_to_plain_dict_v01",
        mismatch_final_projection,
    )
    _assert_reason(
        collector.REASON_MANIFEST_DOCUMENT_PROJECTION_MISMATCH,
        lambda: collector._reconstruct_envelope(fixture.snapshot, ledger_item),
    )


@pytest.mark.parametrize(
    "stored_bytes",
    (b"\xff", b"{", b'{"x":1,"x":2}'),
)
def test_stored_verification_parse_failures_are_stable(stored_bytes: bytes) -> None:
    fixture = _fixture(ledger_contracts.OFFER_A_ID)
    snapshot = replace(fixture.snapshot, stored_verification_bytes=stored_bytes)
    _assert_reason(
        collector.REASON_STORED_VERIFICATION_DOCUMENT_PARSE_FAILED,
        lambda: _collect(fixture, snapshot=snapshot),
    )


@pytest.mark.parametrize(
    "mutator",
    (
        lambda plain: plain.pop("verification_status"),
        lambda plain: plain.update({"extra": 1}),
        lambda plain: plain.update({"verification_errors": "bad"}),
    ),
)
def test_stored_verification_field_mutations_fail_closed(mutator: object) -> None:
    fixture = _fixture(ledger_contracts.OFFER_A_ID)
    plain = crypto_contracts.airline_crypto_artifact_seal_verification_report_to_plain_dict_v01(fixture.stored)
    mutator(plain)  # type: ignore[operator]
    snapshot = _snapshot_with_stored_plain(fixture, plain)
    _assert_reason(
        collector.REASON_STORED_VERIFICATION_DOCUMENT_FIELD_MISMATCH,
        lambda: _collect(fixture, snapshot=snapshot),
    )


@pytest.mark.parametrize(
    "changes",
    (
        {"verification_status": collector.STATUS_PASS},
        {"expected_manifest_core_hash": "0" * 64},
        {"external_anchor_supplied": True},
        {"signature_verified": True},
        {"artifact_hashes_verified": False},
        {"provider_call_count": 1},
        {"transaction_id": "wrong"},
    ),
)
def test_stored_verification_state_mutations_fail_closed(changes: dict[str, object]) -> None:
    fixture = _fixture(ledger_contracts.OFFER_A_ID)
    plain = crypto_contracts.airline_crypto_artifact_seal_verification_report_to_plain_dict_v01(fixture.stored)
    plain.update(changes)
    snapshot = _snapshot_with_stored_plain(fixture, plain)
    with pytest.raises(ValueError) as captured:
        _collect(fixture, snapshot=snapshot)
    assert captured.value.args[0] in (
        collector.REASON_STORED_VERIFICATION_RECONSTRUCTION_FAILED,
        collector.REASON_STORED_VERIFICATION_PROJECTION_MISMATCH,
    )


def test_stored_verification_projection_mismatch_is_stable(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    fixture = _fixture(ledger_contracts.OFFER_A_ID)
    ledger_item, _ = collector._reconstruct_ledger(fixture.snapshot)
    envelope, _ = collector._reconstruct_envelope(fixture.snapshot, ledger_item)
    monkeypatch.setattr(
        collector.crypto_contracts,
        "airline_crypto_artifact_seal_verification_report_to_plain_dict_v01",
        lambda report: {},
    )
    _assert_reason(
        collector.REASON_STORED_VERIFICATION_PROJECTION_MISMATCH,
        lambda: collector._reconstruct_stored_verification(
            fixture.snapshot,
            ledger_item,
            envelope,
        ),
    )


@pytest.mark.parametrize(
    "audit_changes",
    (
        {"ledger_id": "wrong"},
        {"transaction_id": "wrong"},
        {"source_run_ref": "wrong"},
        {"selected_offer_id": ledger_contracts.OFFER_B_ID},
    ),
)
def test_audit_ledger_coherence_mismatch_fails_before_b2b(
    audit_changes: dict[str, object],
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    fixture = _fixture(ledger_contracts.OFFER_A_ID)
    audit = replace(fixture.audit, **audit_changes)
    calls = 0

    def forbidden(*args: object, **kwargs: object) -> object:
        nonlocal calls
        calls += 1
        return fixture.stored

    monkeypatch.setattr(collector.crypto_contracts, "verify_airline_crypto_artifact_seal_v01", forbidden)
    _assert_reason(
        collector.REASON_AUDIT_LEDGER_IDENTITY_MISMATCH,
        lambda: _collect(fixture, audit=audit),
    )
    assert calls == 0


def test_adapter_rejects_missing_declared_extra_key() -> None:
    fixture = _fixture(ledger_contracts.OFFER_A_ID)
    entry = fixture.ledger.entries[5]
    canonical = dict(entry.canonical_hash_input)
    canonical.pop("selected_offer_id")
    changed_entry = replace(entry, canonical_hash_input=canonical)
    entries = list(fixture.ledger.entries)
    entries[5] = changed_entry
    changed_ledger = replace(fixture.ledger, entries=tuple(entries))
    _assert_reason(
        collector.REASON_EXPECTED_IDENTITY_ADAPTER_FAILED,
        lambda: collector.build_airline_sealed_trace_replay_expected_identity_adapter_v01(
            ledger_item=changed_ledger,
            accepted_ledger_audit=fixture.audit,
        ),
    )


@pytest.mark.parametrize("mutation", ("duplicate_type", "missing_entry", "bad_mapping"))
def test_adapter_rejects_incomplete_or_malformed_type_coverage(mutation: str) -> None:
    fixture = _fixture(ledger_contracts.OFFER_A_ID)
    entries = list(fixture.ledger.entries)
    if mutation == "duplicate_type":
        entries[1] = replace(
            entries[1],
            artifact_type=entries[0].artifact_type,
        )
    elif mutation == "missing_entry":
        entries = entries[:-1]
    else:
        entries[5] = replace(entries[5], canonical_hash_input=object())
    changed_ledger = replace(fixture.ledger, entries=tuple(entries))
    _assert_reason(
        collector.REASON_EXPECTED_IDENTITY_ADAPTER_FAILED,
        lambda: collector.build_airline_sealed_trace_replay_expected_identity_adapter_v01(
            ledger_item=changed_ledger,
            accepted_ledger_audit=fixture.audit,
        ),
    )


def test_adapter_rejects_audit_source_ref_mismatch() -> None:
    fixture = _fixture(ledger_contracts.OFFER_A_ID)
    changed_audit = replace(fixture.audit, source_run_ref="different-source-run")
    _assert_reason(
        collector.REASON_EXPECTED_IDENTITY_ADAPTER_FAILED,
        lambda: collector.build_airline_sealed_trace_replay_expected_identity_adapter_v01(
            ledger_item=fixture.ledger,
            accepted_ledger_audit=changed_audit,
        ),
    )


def test_initial_source_byte_change_stops_after_one_b2b(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    fixture = _fixture(ledger_contracts.OFFER_A_ID)
    rows = list(fixture.source_rows)
    relative_ref, content = rows[1]
    rows[1] = (relative_ref, content + b"x")
    changed_snapshot = replace(
        fixture.snapshot,
        ordered_source_files=tuple(rows),
    )
    counts = {"b2b": 0, "callback": 0}
    original = crypto_contracts.verify_airline_crypto_artifact_seal_v01

    def b2b(*args: object, **kwargs: object) -> object:
        counts["b2b"] += 1
        return original(*args, **kwargs)

    def observe() -> object:
        counts["callback"] += 1
        return changed_snapshot

    monkeypatch.setattr(
        collector.crypto_contracts,
        "verify_airline_crypto_artifact_seal_v01",
        b2b,
    )
    _assert_reason(
        collector.REASON_FRESH_ANCHORED_VERIFICATION_FAILED,
        lambda: _collect(
            fixture,
            snapshot=changed_snapshot,
            provider=observe,
        ),
    )
    assert counts == {"b2b": 1, "callback": 0}


def test_b2b_dependency_exception_is_stable_and_short_circuits(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    fixture = _fixture(ledger_contracts.OFFER_A_ID)
    counts = {"b2b": 0, "callback": 0, "pure": 0}

    def b2b(*args: object, **kwargs: object) -> object:
        counts["b2b"] += 1
        raise TypeError("API_KEY=TOP_SECRET")

    def observe() -> object:
        counts["callback"] += 1
        return fixture.snapshot

    def pure(*args: object, **kwargs: object) -> object:
        counts["pure"] += 1
        return object()

    monkeypatch.setattr(
        collector.crypto_contracts,
        "verify_airline_crypto_artifact_seal_v01",
        b2b,
    )
    monkeypatch.setattr(
        collector.replay_contracts,
        "verify_airline_sealed_trace_replay_v01",
        pure,
    )
    error = _assert_reason(
        collector.REASON_FRESH_ANCHORED_VERIFICATION_FAILED,
        lambda: _collect(fixture, provider=observe),
    )
    _assert_secret_free_error(error)
    assert counts == {"b2b": 1, "callback": 0, "pure": 0}


def test_wrong_valid_anchor_calls_b2b_once_and_not_callback(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    fixture = _fixture(ledger_contracts.OFFER_A_ID)
    counts = {"b2b": 0, "callback": 0}
    original = crypto_contracts.verify_airline_crypto_artifact_seal_v01

    def b2b(*args: object, **kwargs: object) -> object:
        counts["b2b"] += 1
        return original(*args, **kwargs)

    def observe() -> object:
        counts["callback"] += 1
        return fixture.snapshot

    monkeypatch.setattr(collector.crypto_contracts, "verify_airline_crypto_artifact_seal_v01", b2b)
    _assert_reason(
        collector.REASON_FRESH_ANCHORED_VERIFICATION_FAILED,
        lambda: _collect(fixture, expected_hash="0" * 64, provider=observe),
    )
    assert counts == {"b2b": 1, "callback": 0}


@pytest.mark.parametrize("fresh_result", (None, object()))
def test_fresh_b2b_invalid_result_short_circuits_callback(
    fresh_result: object,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    fixture = _fixture(ledger_contracts.OFFER_A_ID)
    callback_count = 0

    def b2b(*args: object, **kwargs: object) -> object:
        return fixture.stored if fresh_result is None else fresh_result

    def observe() -> object:
        nonlocal callback_count
        callback_count += 1
        return fixture.snapshot

    monkeypatch.setattr(collector.crypto_contracts, "verify_airline_crypto_artifact_seal_v01", b2b)
    _assert_reason(
        collector.REASON_FRESH_ANCHORED_VERIFICATION_FAILED,
        lambda: _collect(fixture, provider=observe),
    )
    assert callback_count == 0


def test_timeline_failure_short_circuits_callback(monkeypatch: pytest.MonkeyPatch) -> None:
    fixture = _fixture(ledger_contracts.OFFER_A_ID)
    callback_count = 0

    def fail_timeline(*args: object, **kwargs: object) -> object:
        raise ValueError("not-retained")

    def observe() -> object:
        nonlocal callback_count
        callback_count += 1
        return fixture.snapshot

    monkeypatch.setattr(collector.replay_contracts, "build_airline_sealed_trace_replay_timeline_v01", fail_timeline)
    _assert_reason(
        collector.REASON_TIMELINE_RECONSTRUCTION_FAILED,
        lambda: _collect(fixture, provider=observe),
    )
    assert callback_count == 0


@pytest.mark.parametrize(
    "mutation",
    (
        "objects",
        "swapped",
        "duplicate",
        "changed_hash",
        "changed_artifact_id",
        "changed_dependency",
        "list_container",
    ),
)
def test_malformed_collector_stage_timeline_stops_before_callback(
    mutation: str,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    fixture = _fixture(ledger_contracts.OFFER_A_ID)
    counts = {"callback": 0, "pure": 0}
    original = replay_contracts.build_airline_sealed_trace_replay_timeline_v01

    def malformed_timeline(replay_input: object) -> object:
        rows = list(original(replay_input))  # type: ignore[arg-type]
        if mutation == "objects":
            return tuple(object() for _ in range(19))
        if mutation == "swapped":
            rows[0], rows[1] = rows[1], rows[0]
        elif mutation == "duplicate":
            rows[1] = rows[0]
        elif mutation == "changed_hash":
            rows[5] = replace(rows[5], artifact_hash=rows[6].artifact_hash)
        elif mutation == "changed_artifact_id":
            rows[5] = replace(rows[5], artifact_id="different-artifact-id")
        elif mutation == "changed_dependency":
            row_index = 10
            additional_dependency = next(
                row.artifact_id
                for row in rows[:row_index]
                if row.artifact_id not in rows[row_index].depends_on
            )
            changed_dependencies = (
                *rows[row_index].depends_on,
                additional_dependency,
            )
            rows[row_index] = replace(
                rows[row_index],
                depends_on=changed_dependencies,
                dependency_count=len(changed_dependencies),
            )
        if mutation == "list_container":
            return rows
        return tuple(rows)

    def observe() -> object:
        counts["callback"] += 1
        return fixture.snapshot

    def pure(*args: object, **kwargs: object) -> object:
        counts["pure"] += 1
        return object()

    monkeypatch.setattr(
        collector.replay_contracts,
        "build_airline_sealed_trace_replay_timeline_v01",
        malformed_timeline,
    )
    monkeypatch.setattr(
        collector.replay_contracts,
        "verify_airline_sealed_trace_replay_v01",
        pure,
    )
    _assert_reason(
        collector.REASON_TIMELINE_RECONSTRUCTION_FAILED,
        lambda: _collect(fixture, provider=observe),
    )
    assert counts == {"callback": 0, "pure": 0}


def test_callback_exception_is_stable_and_called_once(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    fixture = _fixture(ledger_contracts.OFFER_A_ID)
    counts = {"callback": 0, "pure": 0}

    def observe() -> object:
        counts["callback"] += 1
        raise RuntimeError("API_KEY=TOP_SECRET")

    def pure(*args: object, **kwargs: object) -> object:
        counts["pure"] += 1
        return object()

    monkeypatch.setattr(
        collector.replay_contracts,
        "verify_airline_sealed_trace_replay_v01",
        pure,
    )
    error = _assert_reason(
        collector.REASON_POST_REPLAY_SNAPSHOT_PROVIDER_FAILED,
        lambda: _collect(fixture, provider=observe),
    )
    _assert_secret_free_error(error)
    assert counts == {"callback": 1, "pure": 0}


def test_callback_wrong_type_and_invalid_snapshot_fail_closed() -> None:
    fixture = _fixture(ledger_contracts.OFFER_A_ID)
    _assert_reason(
        collector.REASON_POST_REPLAY_SNAPSHOT_WRONG_TYPE,
        lambda: _collect(fixture, provider=lambda: object()),
    )
    invalid = replace(fixture.snapshot, manifest_artifact_ref="wrong.json")
    _assert_reason(
        collector.REASON_POST_REPLAY_SNAPSHOT_MISMATCH,
        lambda: _collect(fixture, provider=lambda: invalid),
    )


@pytest.mark.parametrize("target", ("source", "manifest", "stored", "package_ref"))
def test_post_snapshot_byte_or_identity_mutation_fails(target: str) -> None:
    fixture = _fixture(ledger_contracts.OFFER_A_ID)
    if target == "source":
        rows = list(fixture.source_rows)
        ref, content = rows[1]
        rows[1] = (ref, content + b"x")
        changed = replace(fixture.snapshot, ordered_source_files=tuple(rows))
    elif target == "manifest":
        changed = replace(fixture.snapshot, manifest_bytes=fixture.snapshot.manifest_bytes + b" ")
    elif target == "stored":
        changed = replace(fixture.snapshot, stored_verification_bytes=fixture.snapshot.stored_verification_bytes + b" ")
    else:
        changed = replace(fixture.snapshot, source_package_ref="different-package")
    _assert_reason(
        collector.REASON_POST_REPLAY_SNAPSHOT_MISMATCH,
        lambda: _collect(fixture, provider=lambda: changed),
    )


def test_callback_failure_prevents_pure_replay_call(monkeypatch: pytest.MonkeyPatch) -> None:
    fixture = _fixture(ledger_contracts.OFFER_A_ID)
    pure_count = 0

    def pure(*args: object, **kwargs: object) -> object:
        nonlocal pure_count
        pure_count += 1
        return object()

    monkeypatch.setattr(collector.replay_contracts, "verify_airline_sealed_trace_replay_v01", pure)
    _assert_reason(
        collector.REASON_POST_REPLAY_SNAPSHOT_WRONG_TYPE,
        lambda: _collect(fixture, provider=lambda: object()),
    )
    assert pure_count == 0


def test_pure_replay_dependency_exception_is_stable(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    fixture = _fixture(ledger_contracts.OFFER_A_ID)
    counts = {"b2b": 0, "callback": 0, "pure": 0}
    original_b2b = crypto_contracts.verify_airline_crypto_artifact_seal_v01

    def b2b(*args: object, **kwargs: object) -> object:
        counts["b2b"] += 1
        return original_b2b(*args, **kwargs)

    def observe() -> object:
        counts["callback"] += 1
        return fixture.snapshot

    def pure(*args: object, **kwargs: object) -> object:
        counts["pure"] += 1
        raise KeyError("API_KEY=TOP_SECRET")

    monkeypatch.setattr(
        collector.crypto_contracts,
        "verify_airline_crypto_artifact_seal_v01",
        b2b,
    )
    monkeypatch.setattr(
        collector.replay_contracts,
        "verify_airline_sealed_trace_replay_v01",
        pure,
    )
    error = _assert_reason(
        collector.REASON_PURE_REPLAY_FAILED,
        lambda: _collect(fixture, provider=observe),
    )
    _assert_secret_free_error(error)
    assert counts == {"b2b": 1, "callback": 1, "pure": 1}


def test_pure_replay_invalid_result_fails_closed(monkeypatch: pytest.MonkeyPatch) -> None:
    fixture = _fixture(ledger_contracts.OFFER_A_ID)
    monkeypatch.setattr(
        collector.replay_contracts,
        "verify_airline_sealed_trace_replay_v01",
        lambda *args, **kwargs: object(),
    )
    _assert_reason(
        collector.REASON_PURE_REPLAY_FAILED,
        lambda: _collect(fixture),
    )


@pytest.mark.parametrize(
    "binding_case",
    ("different_package_ref", "different_source_bytes"),
)
def test_foreign_valid_replay_report_fails_current_input_binding(
    binding_case: str,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    if binding_case == "different_package_ref":
        current = _fixture(
            ledger_contracts.OFFER_A_ID,
            package_ref="airline_sealed_trace_replay_current_fixture",
        )
        foreign = _fixture(
            ledger_contracts.OFFER_A_ID,
            package_ref="airline_sealed_trace_replay_foreign_fixture",
        )
    else:
        current = _fixture(ledger_contracts.OFFER_A_ID)
        foreign = _fixture(
            ledger_contracts.OFFER_A_ID,
            source_variant="foreign-source-bytes",
        )

    current_report = _collect(current)
    foreign_report = _collect(foreign)
    assert current.ledger == foreign.ledger
    assert current_report.reconstructed_timeline == foreign_report.reconstructed_timeline
    assert current.envelope.manifest_core_hash != foreign.envelope.manifest_core_hash
    assert current_report.replay_id != foreign_report.replay_id
    if binding_case == "different_package_ref":
        assert current.snapshot.source_package_ref != foreign.snapshot.source_package_ref
        assert current.source_rows == foreign.source_rows
    else:
        assert current.snapshot.source_package_ref == foreign.snapshot.source_package_ref
        assert current.source_rows != foreign.source_rows

    counts = {"b2b": 0, "callback": 0, "pure": 0}
    original_b2b = crypto_contracts.verify_airline_crypto_artifact_seal_v01

    def b2b(*args: object, **kwargs: object) -> object:
        counts["b2b"] += 1
        return original_b2b(*args, **kwargs)

    def observe() -> object:
        counts["callback"] += 1
        return current.snapshot

    def pure(*args: object, **kwargs: object) -> object:
        counts["pure"] += 1
        return foreign_report

    monkeypatch.setattr(
        collector.crypto_contracts,
        "verify_airline_crypto_artifact_seal_v01",
        b2b,
    )
    monkeypatch.setattr(
        collector.replay_contracts,
        "verify_airline_sealed_trace_replay_v01",
        pure,
    )
    _assert_reason(
        collector.REASON_PURE_REPLAY_FAILED,
        lambda: _collect(current, provider=observe),
    )
    assert counts == {"b2b": 1, "callback": 1, "pure": 1}


@pytest.mark.parametrize("value", (None, 1, "x", (), [], {}, object()))
def test_public_collector_does_not_leak_ordinary_shape_errors(value: object) -> None:
    _assert_reason(
        collector.REASON_PACKAGE_SNAPSHOT_INVALID,
        lambda: collector.collect_airline_sealed_trace_replay_from_package_snapshot_v01(
            package_snapshot=value,
            accepted_ledger_audit=value,
            expected_manifest_core_hash=value,
            post_replay_snapshot_provider=value,
        ),
    )


def test_static_module_boundary_and_exact_direct_calls() -> None:
    source = Path(MODULE_PATH).read_text(encoding="utf-8")
    tree = ast.parse(source)

    def import_roots(parsed_tree: ast.AST) -> set[str]:
        roots: set[str] = set()
        for node in ast.walk(parsed_tree):
            if isinstance(node, ast.Import):
                roots.update(alias.name.split(".", 1)[0] for alias in node.names)
            elif isinstance(node, ast.ImportFrom) and node.module is not None:
                roots.add(node.module.split(".", 1)[0])
        return roots

    imported_roots = import_roots(tree)
    probe_roots = import_roots(
        ast.parse(
            "from pathlib import Path\n"
            "from os import path\n"
            "from urllib.parse import urlparse\n",
        ),
    )
    assert {"pathlib", "os", "urllib"}.issubset(probe_roots)
    assert {
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
    }.isdisjoint(imported_roots)
    calls = [
        node.func.attr
        for node in ast.walk(tree)
        if isinstance(node, ast.Call) and isinstance(node.func, ast.Attribute)
    ]
    assert calls.count("verify_airline_crypto_artifact_seal_v01") == 1
    assert calls.count("build_airline_sealed_trace_replay_timeline_v01") == 1
    assert calls.count("verify_airline_sealed_trace_replay_v01") == 1
    assert calls.count(
        "build_airline_sealed_trace_replay_expected_identity_adapter_v01",
    ) == 1
    assert "_project_expected_identity_value" not in source
    assert (
        "_build_airline_sealed_trace_replay_expected_identity_adapter_impl_v01"
        not in source
    )
    forbidden = (
        "open(",
        ".tmp/",
        "collect_airline_transaction_artifact_ledger_audit_v01",
        "collect_airline_crypto_artifact_seal_from_source_bundle_v01",
        "build_airline_transaction_artifact_ledger_expected_identity_from_source_v01",
        "build_airline_transaction_artifact_ledger_fixture_expected_identity_v01",
        "SourceBundle",
        "root_artifact_attestation",
        "asdict",
        "repr(",
        "eval(",
        "exec(",
    )
    assert all(token not in source for token in forbidden)
    for node in tree.body:
        if isinstance(node, (ast.Assign, ast.AnnAssign)):
            assert not isinstance(node.value, (ast.List, ast.Dict, ast.Set))


def test_module_constants_and_no_runtime_source_bundle_claim() -> None:
    assert collector.MODULE_ID == "airline_sealed_trace_replay_collector_v01"
    assert collector.SLICE_ID == "airline_sealed_trace_replay_v01_slice_c1"
    assert collector.STATUS_PASS == replay_contracts.STATUS_PASS
    assert collector.STATUS_FAIL_CLOSED == replay_contracts.STATUS_FAIL_CLOSED
    assert collector.LEDGER_SOURCE_ARTIFACT_REF == crypto_contracts.REQUIRED_SOURCE_FILE_REFS[0]
    assert collector.MANIFEST_DOCUMENT_FIELD_NAMES == (
        "manifest_core",
        "manifest_core_hash",
        "signature",
    )
