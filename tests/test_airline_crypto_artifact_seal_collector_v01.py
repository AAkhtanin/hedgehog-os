from __future__ import annotations

import ast
import inspect
import json
from copy import deepcopy
from dataclasses import FrozenInstanceError, dataclass, replace
from types import MappingProxyType

import pytest

from hedgehog.domains.airline import crypto_artifact_seal_collector_v01 as collector
from hedgehog.domains.airline import crypto_artifact_seal_v01 as seal
from hedgehog.domains.airline import transaction_artifact_ledger_v01 as ledger
from tests import test_airline_transaction_artifact_ledger_collector_v01 as ledger_collector_helpers


MODULE_PATH = "hedgehog/domains/airline/crypto_artifact_seal_collector_v01.py"
PACKAGE_REF = "airline_crypto_slice_c1_fixture"


def _valid_a() -> ledger.AirlineTransactionArtifactLedgerV01:
    return ledger.build_valid_airline_transaction_artifact_ledger_offer_a_v01()


def _valid_b() -> ledger.AirlineTransactionArtifactLedgerV01:
    return ledger.build_valid_airline_transaction_artifact_ledger_offer_b_v01()


def _fixture_identity(
    offer_id: str,
) -> ledger.AirlineTransactionArtifactLedgerExpectedIdentityV01:
    return ledger.build_airline_transaction_artifact_ledger_fixture_expected_identity_v01(
        offer_id=offer_id,
    )


def _accepted_audit(
    item: ledger.AirlineTransactionArtifactLedgerV01,
    offer_id: str,
    **changes: object,
) -> collector.AirlineCryptoArtifactSealAcceptedLedgerAuditV01:
    values: dict[str, object] = {
        "audit_id": collector.EXPECTED_LEDGER_AUDIT_ID,
        "audit_version": collector.EXPECTED_LEDGER_AUDIT_VERSION,
        "final_status": collector.STATUS_PASS,
        "required_source_files": collector.REQUIRED_SOURCE_FILE_REFS,
        "files_read_count": 9,
        "ledger_id": item.ledger_id,
        "transaction_id": item.transaction_id,
        "selected_offer_id": offer_id,
        "source_run_ref": item.source_run_ref,
        "source_causal_report_ref": item.source_causal_report_ref,
        "source_corridor_report_ref": item.source_corridor_report_ref,
        "actual_entry_count": 19,
        "actual_dependency_edge_count": 29,
        "actual_root_final_count": 3,
        "client_root_final_count": 1,
        "airline_root_final_count": 1,
        "bank_root_final_count": 1,
        **{field_name: True for field_name in collector.ACCEPTED_AUDIT_BOOLEAN_FIELDS},
        "stored_validation_status": collector.STATUS_PASS,
        "stored_validation_errors": (),
        **{
            field_name: 0
            for field_name in collector.ACCEPTED_AUDIT_ZERO_COUNTER_FIELDS
        },
        "validation_errors": (),
    }
    values.update(changes)
    return collector.AirlineCryptoArtifactSealAcceptedLedgerAuditV01(
        **values,  # type: ignore[arg-type]
    )


def _ledger_bytes(
    item: ledger.AirlineTransactionArtifactLedgerV01,
    identity: ledger.AirlineTransactionArtifactLedgerExpectedIdentityV01,
    *,
    pretty: bool = False,
) -> bytes:
    plain = collector.airline_crypto_artifact_seal_ledger_document_to_plain_dict_v01(
        item,
        expected_identity=identity,
    )
    if pretty:
        text = json.dumps(plain, ensure_ascii=False, indent=2, sort_keys=True)
    else:
        text = json.dumps(
            plain,
            ensure_ascii=False,
            sort_keys=True,
            separators=(",", ":"),
        )
    return text.encode("utf-8")


def _source_rows(
    item: ledger.AirlineTransactionArtifactLedgerV01,
    identity: ledger.AirlineTransactionArtifactLedgerExpectedIdentityV01,
    *,
    pretty: bool = False,
) -> tuple[tuple[str, bytes], ...]:
    rows: list[tuple[str, bytes]] = []
    for index, ref in enumerate(collector.REQUIRED_SOURCE_FILE_REFS):
        if index == 0:
            content = _ledger_bytes(item, identity, pretty=pretty)
        else:
            content = seal.canonical_airline_crypto_json_bytes_v01(
                {
                    "source_file_ref": ref,
                    "transaction_id": item.transaction_id,
                },
            )
        rows.append((ref, content))
    return tuple(rows)


def _rows_with_ledger_object(
    rows: tuple[tuple[str, bytes], ...],
    payload: object,
    *,
    pretty: bool = False,
) -> tuple[tuple[str, bytes], ...]:
    changed = list(rows)
    changed[0] = (
        collector.REQUIRED_SOURCE_FILE_REFS[0],
        json.dumps(
            payload,
            ensure_ascii=False,
            indent=2 if pretty else None,
            sort_keys=True,
            separators=None if pretty else (",", ":"),
        ).encode("utf-8"),
    )
    return tuple(changed)


def _bundle(
    item: ledger.AirlineTransactionArtifactLedgerV01,
    offer_id: str,
    *,
    identity: ledger.AirlineTransactionArtifactLedgerExpectedIdentityV01 | None = None,
    audit: collector.AirlineCryptoArtifactSealAcceptedLedgerAuditV01 | None = None,
    before: tuple[tuple[str, bytes], ...] | None = None,
    after: tuple[tuple[str, bytes], ...] | None = None,
) -> collector.AirlineCryptoArtifactSealSourceBundleV01:
    actual_identity = identity or _fixture_identity(offer_id)
    actual_before = before or _source_rows(item, actual_identity)
    return collector.build_airline_crypto_artifact_seal_source_bundle_v01(
        source_bundle_id=f"airline_crypto_source_bundle:{offer_id}",
        source_package_ref=PACKAGE_REF,
        accepted_audit=audit or _accepted_audit(item, offer_id),
        ledger_item=item,
        expected_identity=actual_identity,
        ordered_source_files_before_audit=actual_before,
        ordered_source_files_after_audit=after or actual_before,
    )


def _report(
    bundle: object,
) -> collector.AirlineCryptoArtifactSealSourceBundleValidationReportV01:
    return collector.validate_airline_crypto_artifact_seal_source_bundle_v01(bundle)


def _assert_fail(
    bundle: object,
    reason: str,
) -> collector.AirlineCryptoArtifactSealSourceBundleValidationReportV01:
    report = _report(bundle)
    assert report.validation_status == collector.STATUS_FAIL_CLOSED
    assert reason in report.validation_errors
    return report


@pytest.mark.parametrize(
    ("item_factory", "offer_id"),
    ((_valid_a, ledger.OFFER_A_ID), (_valid_b, ledger.OFFER_B_ID)),
)
def test_accepted_audit_projection_passes_for_fixture_offers(
    item_factory,
    offer_id: str,
) -> None:
    report = collector.validate_airline_crypto_artifact_seal_accepted_ledger_audit_v01(
        _accepted_audit(item_factory(), offer_id),
    )
    assert report.validation_status == collector.STATUS_PASS
    assert report.validation_errors == ()


@pytest.mark.parametrize(
    ("item_factory", "offer_id"),
    ((_valid_a, ledger.OFFER_A_ID), (_valid_b, ledger.OFFER_B_ID)),
)
def test_fixture_source_bundles_pass_with_exact_geometry_and_lineage(
    item_factory,
    offer_id: str,
) -> None:
    item = item_factory()
    bundle = _bundle(item, offer_id)
    report = _report(bundle)
    assert report.validation_status == collector.STATUS_PASS
    assert all(
        getattr(report, field_name) is True
        for field_name in collector.SOURCE_BUNDLE_REPORT_BOOLEAN_FIELDS
    )
    assert (
        bundle.accepted_audit.actual_entry_count,
        bundle.accepted_audit.actual_dependency_edge_count,
        bundle.accepted_audit.actual_root_final_count,
    ) == (19, 29, 3)
    assert bundle.accepted_audit.selected_offer_id == offer_id
    assert bundle.accepted_audit.source_run_ref == item.source_run_ref


def test_semantic_causal_exact_source_bundle_passes() -> None:
    ledger_source = ledger_collector_helpers._source_bundle_from_public_causal_runtime(
        ledger.OFFER_A_ID,
    )
    identity = ledger_collector_helpers._expected_identity(ledger_source)
    item = ledger_collector_helpers._assert_collected_pass(ledger_source)
    hold = next(
        entry
        for entry in item.entries
        if entry.artifact_type == ledger.ARTIFACT_AIRLINE_HOLD_PACKET
    )
    assert hold.artifact_id.startswith("airline_hold_commit_packet:semantic_causal:")
    assert hold.canonical_hash_input["hold_id"].startswith("hold:semantic_causal:")
    bundle = _bundle(item, ledger.OFFER_A_ID, identity=identity)
    report = _report(bundle)
    assert report.validation_status == collector.STATUS_PASS
    assert bundle.expected_identity is identity
    assert bundle.ledger_item is item


@pytest.mark.parametrize("pretty", (False, True))
def test_compact_and_pretty_ledger_json_objects_match_typed_ledger(pretty: bool) -> None:
    item = _valid_a()
    identity = _fixture_identity(ledger.OFFER_A_ID)
    rows = _source_rows(item, identity, pretty=pretty)
    report = _report(
        _bundle(item, ledger.OFFER_A_ID, identity=identity, before=rows, after=rows),
    )
    assert report.validation_status == collector.STATUS_PASS
    assert report.ledger_document_matches_typed_ledger is True


def test_before_and_after_indexes_and_bytes_are_exactly_equal() -> None:
    bundle = _bundle(_valid_a(), ledger.OFFER_A_ID)
    report = _report(bundle)
    assert report.source_bytes_unchanged_after_audit is True
    assert report.source_indexes_equal is True
    before_index = seal.build_airline_crypto_source_package_index_v01(
        transaction_id=bundle.ledger_item.transaction_id,
        ordered_source_files=bundle.ordered_source_files_before_audit,
    )
    after_index = seal.build_airline_crypto_source_package_index_v01(
        transaction_id=bundle.ledger_item.transaction_id,
        ordered_source_files=bundle.ordered_source_files_after_audit,
    )
    assert before_index == after_index


def test_bundle_audit_and_report_are_deeply_immutable() -> None:
    bundle = _bundle(_valid_a(), ledger.OFFER_A_ID)
    report = _report(bundle)
    with pytest.raises(FrozenInstanceError):
        bundle.source_bundle_id = "changed"  # type: ignore[misc]
    with pytest.raises(FrozenInstanceError):
        bundle.accepted_audit.final_status = "changed"  # type: ignore[misc]
    with pytest.raises(FrozenInstanceError):
        report.validation_status = "changed"  # type: ignore[misc]
    assert type(bundle.ordered_source_files_before_audit) is tuple
    assert all(type(row) is tuple for row in bundle.ordered_source_files_before_audit)
    assert type(report.validation_errors) is tuple


def test_caller_list_mutation_cannot_change_audit_or_bundle() -> None:
    item = _valid_a()
    identity = _fixture_identity(ledger.OFFER_A_ID)
    required_files = list(collector.REQUIRED_SOURCE_FILE_REFS)
    stored_errors: list[str] = []
    validation_errors: list[str] = []
    audit = _accepted_audit(
        item,
        ledger.OFFER_A_ID,
        required_source_files=required_files,
        stored_validation_errors=stored_errors,
        validation_errors=validation_errors,
    )
    mutable_rows = list(_source_rows(item, identity))
    before = tuple(mutable_rows)
    bundle = _bundle(item, ledger.OFFER_A_ID, identity=identity, audit=audit, before=before)
    required_files.reverse()
    stored_errors.append("changed")
    validation_errors.append("changed")
    mutable_rows[0] = ("changed.json", b"changed")
    assert audit.required_source_files == collector.REQUIRED_SOURCE_FILE_REFS
    assert audit.stored_validation_errors == ()
    assert audit.validation_errors == ()
    assert bundle.ordered_source_files_before_audit[0] == before[0]


def test_a_b_a_and_b_a_b_source_bundle_state_isolation() -> None:
    a1 = _bundle(_valid_a(), ledger.OFFER_A_ID)
    b1 = _bundle(_valid_b(), ledger.OFFER_B_ID)
    a2 = _bundle(_valid_a(), ledger.OFFER_A_ID)
    b2 = _bundle(_valid_b(), ledger.OFFER_B_ID)
    a3 = _bundle(_valid_a(), ledger.OFFER_A_ID)
    b3 = _bundle(_valid_b(), ledger.OFFER_B_ID)
    assert a1 == a2 == a3
    assert b1 == b2 == b3
    assert a1 != b1


class _StringSubclass(str):
    pass


@pytest.mark.parametrize(
    ("changes", "reason"),
    (
        ({"audit_id": "wrong"}, collector.REASON_ACCEPTED_AUDIT_IDENTITY_MISMATCH),
        ({"audit_version": "wrong"}, collector.REASON_ACCEPTED_AUDIT_IDENTITY_MISMATCH),
        ({"final_status": collector.STATUS_FAIL_CLOSED}, collector.REASON_ACCEPTED_AUDIT_STATUS_MISMATCH),
        ({"final_status": _StringSubclass(collector.STATUS_PASS)}, collector.REASON_ACCEPTED_AUDIT_STATUS_MISMATCH),
        ({"required_source_files": tuple(reversed(collector.REQUIRED_SOURCE_FILE_REFS))}, collector.REASON_ACCEPTED_AUDIT_REQUIRED_FILES_MISMATCH),
        ({"files_read_count": True}, collector.REASON_ACCEPTED_AUDIT_REQUIRED_FILES_MISMATCH),
        ({"actual_entry_count": 18}, collector.REASON_ACCEPTED_AUDIT_GEOMETRY_MISMATCH),
        ({"actual_entry_count": 19.0}, collector.REASON_ACCEPTED_AUDIT_GEOMETRY_MISMATCH),
        ({"actual_dependency_edge_count": 28}, collector.REASON_ACCEPTED_AUDIT_GEOMETRY_MISMATCH),
        ({"actual_root_final_count": 2}, collector.REASON_ACCEPTED_AUDIT_GEOMETRY_MISMATCH),
        ({"client_root_final_count": 0}, collector.REASON_ACCEPTED_AUDIT_ROOT_FINAL_MISMATCH),
        ({"client_root_final_count": 2, "bank_root_final_count": 0}, collector.REASON_ACCEPTED_AUDIT_ROOT_FINAL_MISMATCH),
        ({"artifact_ids_unique": False}, collector.REASON_ACCEPTED_AUDIT_BOOLEAN_BOUNDARY_MISMATCH),
        ({"source_refs_consistent": 1}, collector.REASON_ACCEPTED_AUDIT_BOOLEAN_BOUNDARY_MISMATCH),
        ({"stored_validation_status": collector.STATUS_FAIL_CLOSED}, collector.REASON_ACCEPTED_AUDIT_STORED_VALIDATION_MISMATCH),
        ({"stored_validation_errors": ("failed",)}, collector.REASON_ACCEPTED_AUDIT_STORED_VALIDATION_MISMATCH),
        ({"stored_validation_errors": {}}, collector.REASON_ACCEPTED_AUDIT_STORED_VALIDATION_MISMATCH),
        ({"validation_errors": ("failed",)}, collector.REASON_ACCEPTED_AUDIT_VALIDATION_ERRORS_NOT_EMPTY),
        ({"validation_errors": {}}, collector.REASON_ACCEPTED_AUDIT_VALIDATION_ERRORS_NOT_EMPTY),
        ({"provider_call_count": 1}, collector.REASON_ACCEPTED_AUDIT_ZERO_COUNTER_MISMATCH),
        ({"network_call_count": 1}, collector.REASON_ACCEPTED_AUDIT_ZERO_COUNTER_MISMATCH),
        ({"gemini_call_count": 1}, collector.REASON_ACCEPTED_AUDIT_ZERO_COUNTER_MISMATCH),
        ({"provider_call_count": False}, collector.REASON_ACCEPTED_AUDIT_ZERO_COUNTER_MISMATCH),
        ({"audit_created_authority_count": 1}, collector.REASON_ACCEPTED_AUDIT_ZERO_COUNTER_MISMATCH),
        ({"audit_created_permission_count": 1}, collector.REASON_ACCEPTED_AUDIT_ZERO_COUNTER_MISMATCH),
        ({"audit_created_action_count": 1}, collector.REASON_ACCEPTED_AUDIT_ZERO_COUNTER_MISMATCH),
        ({"real_world_effects_count": 1}, collector.REASON_ACCEPTED_AUDIT_ZERO_COUNTER_MISMATCH),
    ),
)
def test_accepted_audit_fail_closed_matrix(changes: dict[str, object], reason: str) -> None:
    audit = _accepted_audit(_valid_a(), ledger.OFFER_A_ID, **changes)
    report = collector.validate_airline_crypto_artifact_seal_accepted_ledger_audit_v01(audit)
    assert report.validation_status == collector.STATUS_FAIL_CLOSED
    assert reason in report.validation_errors


def test_accepted_audit_wrong_type_fails_without_exception() -> None:
    report = collector.validate_airline_crypto_artifact_seal_accepted_ledger_audit_v01(object())
    assert report.validation_errors == (collector.REASON_ACCEPTED_AUDIT_WRONG_TYPE,)


def test_source_bundle_scalar_contract_failures() -> None:
    valid = _bundle(_valid_a(), ledger.OFFER_A_ID)
    _assert_fail(object(), collector.REASON_SOURCE_BUNDLE_WRONG_TYPE)
    _assert_fail(replace(valid, source_bundle_id=""), collector.REASON_SOURCE_BUNDLE_ID_INVALID)
    _assert_fail(replace(valid, source_package_ref="dir/package"), collector.REASON_SOURCE_PACKAGE_REF_INVALID)
    _assert_fail(replace(valid, accepted_audit=object()), collector.REASON_SOURCE_BUNDLE_AUDIT_INVALID)  # type: ignore[arg-type]
    _assert_fail(replace(valid, ledger_item=object()), collector.REASON_SOURCE_BUNDLE_LEDGER_WRONG_TYPE)  # type: ignore[arg-type]
    _assert_fail(replace(valid, expected_identity=None), collector.REASON_SOURCE_BUNDLE_EXPECTED_IDENTITY_WRONG_TYPE)  # type: ignore[arg-type]
    _assert_fail(replace(valid, expected_identity=object()), collector.REASON_SOURCE_BUNDLE_EXPECTED_IDENTITY_WRONG_TYPE)  # type: ignore[arg-type]


def test_contradictory_expected_identity_fails_ledger_validation() -> None:
    valid = _bundle(_valid_a(), ledger.OFFER_A_ID)
    wrong = _fixture_identity(ledger.OFFER_B_ID)
    _assert_fail(
        replace(valid, expected_identity=wrong),
        collector.REASON_SOURCE_BUNDLE_LEDGER_VALIDATION_FAILED,
    )


@pytest.mark.parametrize(
    "field_name",
    ("ledger_id", "transaction_id"),
)
def test_audit_ledger_identity_mismatch_fails(field_name: str) -> None:
    valid = _bundle(_valid_a(), ledger.OFFER_A_ID)
    audit = replace(valid.accepted_audit, **{field_name: "foreign"})
    _assert_fail(
        replace(valid, accepted_audit=audit),
        collector.REASON_SOURCE_BUNDLE_LEDGER_AUDIT_IDENTITY_MISMATCH,
    )


@pytest.mark.parametrize(
    "field_name",
    ("source_run_ref", "source_causal_report_ref", "source_corridor_report_ref"),
)
def test_audit_source_ref_mismatch_fails(field_name: str) -> None:
    valid = _bundle(_valid_a(), ledger.OFFER_A_ID)
    audit = replace(valid.accepted_audit, **{field_name: "foreign"})
    _assert_fail(
        replace(valid, accepted_audit=audit),
        collector.REASON_SOURCE_BUNDLE_SOURCE_REFS_MISMATCH,
    )


def test_audit_selected_offer_mismatch_fails() -> None:
    valid = _bundle(_valid_a(), ledger.OFFER_A_ID)
    audit = replace(valid.accepted_audit, selected_offer_id=ledger.OFFER_B_ID)
    _assert_fail(
        replace(valid, accepted_audit=audit),
        collector.REASON_SOURCE_BUNDLE_SELECTED_OFFER_MISMATCH,
    )


@pytest.mark.parametrize(
    ("target", "mutation", "reason"),
    (
        ("before", "missing", collector.REASON_SOURCE_SNAPSHOT_BEFORE_MALFORMED),
        ("before", "extra", collector.REASON_SOURCE_SNAPSHOT_BEFORE_MALFORMED),
        ("before", "reorder", collector.REASON_SOURCE_SNAPSHOT_FILE_ORDER_MISMATCH),
        ("after", "missing", collector.REASON_SOURCE_SNAPSHOT_AFTER_AUDIT_MALFORMED),
        ("after", "reorder", collector.REASON_SOURCE_SNAPSHOT_FILE_ORDER_MISMATCH),
        ("before", "outer_list", collector.REASON_SOURCE_SNAPSHOT_BEFORE_MALFORMED),
        ("before", "row_list", collector.REASON_SOURCE_SNAPSHOT_BEFORE_MALFORMED),
        ("before", "bytearray", collector.REASON_SOURCE_SNAPSHOT_BEFORE_MALFORMED),
        ("before", "str_subclass", collector.REASON_SOURCE_SNAPSHOT_BEFORE_MALFORMED),
    ),
)
def test_source_snapshot_shape_failures(target: str, mutation: str, reason: str) -> None:
    valid = _bundle(_valid_a(), ledger.OFFER_A_ID)
    rows: object = valid.ordered_source_files_before_audit
    mutable = list(rows)
    if mutation == "missing":
        rows = tuple(mutable[:-1])
    elif mutation == "extra":
        rows = tuple(mutable + [("extra.json", b"{}")])
    elif mutation == "reorder":
        mutable[0], mutable[1] = mutable[1], mutable[0]
        rows = tuple(mutable)
    elif mutation == "outer_list":
        rows = mutable
    elif mutation == "row_list":
        mutable[0] = list(mutable[0])  # type: ignore[assignment]
        rows = tuple(mutable)
    elif mutation == "bytearray":
        mutable[0] = (mutable[0][0], bytearray(mutable[0][1]))  # type: ignore[arg-type]
        rows = tuple(mutable)
    elif mutation == "str_subclass":
        mutable[0] = (_StringSubclass(mutable[0][0]), mutable[0][1])
        rows = tuple(mutable)
    changed = replace(
        valid,
        **{
            "ordered_source_files_before_audit" if target == "before" else "ordered_source_files_after_audit": rows,
        },
    )
    _assert_fail(changed, reason)


def test_changed_after_audit_byte_fails_bytes_and_index_coherence() -> None:
    valid = _bundle(_valid_a(), ledger.OFFER_A_ID)
    changed = list(valid.ordered_source_files_after_audit)
    changed[-1] = (changed[-1][0], changed[-1][1] + b"x")
    report = _assert_fail(
        replace(valid, ordered_source_files_after_audit=tuple(changed)),
        collector.REASON_SOURCE_SNAPSHOT_BYTES_CHANGED_DURING_AUDIT,
    )
    assert collector.REASON_SOURCE_SNAPSHOT_INDEX_MISMATCH in report.validation_errors


def test_changed_after_audit_ref_fails_file_order() -> None:
    valid = _bundle(_valid_a(), ledger.OFFER_A_ID)
    changed = list(valid.ordered_source_files_after_audit)
    changed[-1] = ("foreign.json", changed[-1][1])
    _assert_fail(
        replace(valid, ordered_source_files_after_audit=tuple(changed)),
        collector.REASON_SOURCE_SNAPSHOT_FILE_ORDER_MISMATCH,
    )


@pytest.mark.parametrize(
    "raw_bytes",
    (
        b"\xff",
        b'{"ledger_id":"a","ledger_id":"b"}',
        b"[]",
        b"1",
    ),
)
def test_malformed_ledger_document_bytes_fail_closed(raw_bytes: bytes) -> None:
    valid = _bundle(_valid_a(), ledger.OFFER_A_ID)
    changed = list(valid.ordered_source_files_before_audit)
    changed[0] = (changed[0][0], raw_bytes)
    rows = tuple(changed)
    _assert_fail(
        replace(
            valid,
            ordered_source_files_before_audit=rows,
            ordered_source_files_after_audit=rows,
        ),
        collector.REASON_LEDGER_DOCUMENT_MALFORMED_JSON,
    )


@pytest.mark.parametrize(
    "mutation",
    ("ledger_id", "transaction_id", "artifact_id", "canonical_hash_input"),
)
def test_parsed_ledger_object_mismatch_fails(mutation: str) -> None:
    item = _valid_a()
    identity = _fixture_identity(ledger.OFFER_A_ID)
    rows = _source_rows(item, identity)
    payload = collector.airline_crypto_artifact_seal_ledger_document_to_plain_dict_v01(
        item,
        expected_identity=identity,
    )
    payload = deepcopy(payload)
    if mutation in ("ledger_id", "transaction_id"):
        payload[mutation] = "foreign"
    elif mutation == "artifact_id":
        payload["entries"][0]["artifact_id"] = "foreign"  # type: ignore[index]
    else:
        payload["entries"][0]["canonical_hash_input"]["artifact_id"] = "foreign"  # type: ignore[index]
    changed_rows = _rows_with_ledger_object(rows, payload)
    _assert_fail(
        replace(
            _bundle(item, ledger.OFFER_A_ID, identity=identity),
            ordered_source_files_before_audit=changed_rows,
            ordered_source_files_after_audit=changed_rows,
        ),
        collector.REASON_LEDGER_DOCUMENT_OBJECT_MISMATCH,
    )


def test_typed_ledger_difference_fails_against_original_document_bytes() -> None:
    item_a = _valid_a()
    identity_a = _fixture_identity(ledger.OFFER_A_ID)
    rows_a = _source_rows(item_a, identity_a)
    item_b = _valid_b()
    identity_b = _fixture_identity(ledger.OFFER_B_ID)
    bundle_b = _bundle(item_b, ledger.OFFER_B_ID, identity=identity_b)
    changed = replace(
        bundle_b,
        ordered_source_files_before_audit=rows_a,
        ordered_source_files_after_audit=rows_a,
    )
    _assert_fail(changed, collector.REASON_LEDGER_DOCUMENT_OBJECT_MISMATCH)


def test_missing_ledger_document_row_is_reported() -> None:
    valid = _bundle(_valid_a(), ledger.OFFER_A_ID)
    rows = list(valid.ordered_source_files_before_audit)
    rows[0] = (rows[1][0], rows[0][1])
    changed_rows = tuple(rows)
    report = _assert_fail(
        replace(
            valid,
            ordered_source_files_before_audit=changed_rows,
            ordered_source_files_after_audit=changed_rows,
        ),
        collector.REASON_LEDGER_DOCUMENT_MISSING,
    )
    assert collector.REASON_SOURCE_SNAPSHOT_FILE_ORDER_MISMATCH in report.validation_errors


@dataclass(frozen=True)
class _ArbitraryDataclass:
    value: str


class _ArbitraryMapping(dict):
    pass


@pytest.mark.parametrize("unsupported", (_ArbitraryDataclass("x"), _ArbitraryMapping(x="y")))
def test_arbitrary_projection_values_are_rejected(unsupported: object) -> None:
    item = _valid_a()
    entry = item.entries[0]
    object.__setattr__(entry, "canonical_hash_input", unsupported)
    with pytest.raises(ValueError, match=collector.REASON_LEDGER_DOCUMENT_PROJECTION_FAILED):
        collector.airline_crypto_artifact_seal_ledger_document_to_plain_dict_v01(
            item,
            expected_identity=_fixture_identity(ledger.OFFER_A_ID),
        )


def test_projection_validation_does_not_mutate_ledger_or_source_bytes() -> None:
    item = _valid_a()
    identity = _fixture_identity(ledger.OFFER_A_ID)
    rows = _source_rows(item, identity)
    item_before = deepcopy(item)
    rows_before = tuple((ref, content) for ref, content in rows)
    bundle = _bundle(item, ledger.OFFER_A_ID, identity=identity, before=rows, after=rows)
    assert _report(bundle).validation_status == collector.STATUS_PASS
    assert item == item_before
    assert rows == rows_before


def test_source_bundle_builder_raises_stable_reason_for_invalid_input() -> None:
    item = _valid_a()
    identity = _fixture_identity(ledger.OFFER_A_ID)
    rows = _source_rows(item, identity)
    with pytest.raises(ValueError, match=collector.REASON_SOURCE_BUNDLE_ID_INVALID):
        collector.build_airline_crypto_artifact_seal_source_bundle_v01(
            source_bundle_id="",
            source_package_ref=PACKAGE_REF,
            accepted_audit=_accepted_audit(item, ledger.OFFER_A_ID),
            ledger_item=item,
            expected_identity=identity,
            ordered_source_files_before_audit=rows,
            ordered_source_files_after_audit=rows,
        )


def test_source_bundle_validation_report_derives_status_and_freezes_errors() -> None:
    valid = _report(_bundle(_valid_a(), ledger.OFFER_A_ID))
    changed = replace(valid, validation_status=collector.STATUS_PASS, ledger_valid=False)
    assert changed.validation_status == collector.STATUS_FAIL_CLOSED
    malformed = replace(valid, validation_errors={})  # type: ignore[arg-type]
    assert malformed.validation_status == collector.STATUS_FAIL_CLOSED
    assert malformed.validation_errors == (collector.REASON_MALFORMED_VALIDATION_ERRORS,)
    source_errors = [collector.REASON_SOURCE_BUNDLE_LEDGER_VALIDATION_FAILED]
    frozen = replace(valid, validation_errors=source_errors)
    source_errors.append("changed")
    assert frozen.validation_errors == (
        collector.REASON_SOURCE_BUNDLE_LEDGER_VALIDATION_FAILED,
    )


@pytest.mark.parametrize(
    "malformed",
    (None, {}, [], "bad", 1, object()),
)
def test_public_validators_never_leak_shape_exceptions(malformed: object) -> None:
    audit_report = collector.validate_airline_crypto_artifact_seal_accepted_ledger_audit_v01(
        malformed,
    )
    bundle_report = collector.validate_airline_crypto_artifact_seal_source_bundle_v01(
        malformed,
    )
    assert audit_report.validation_status == collector.STATUS_FAIL_CLOSED
    assert bundle_report.validation_status == collector.STATUS_FAIL_CLOSED


def test_static_production_import_boundary() -> None:
    tree = ast.parse(open(MODULE_PATH, encoding="utf-8").read())
    imports = []
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            imports.extend(alias.name for alias in node.names)
        elif isinstance(node, ast.ImportFrom):
            imports.append(node.module or "")
    allowed = {
        "__future__",
        "collections.abc",
        "dataclasses",
        "types",
        "typing",
        "hedgehog.domains.airline",
    }
    assert set(imports) <= allowed
    assert not any(name.startswith("demo") or name.startswith("tests") for name in imports)


def test_static_no_file_io_runtime_or_network_calls() -> None:
    tree = ast.parse(open(MODULE_PATH, encoding="utf-8").read())
    forbidden_calls = {
        "open",
        "read",
        "write",
        "Path",
        "collect_airline_transaction_artifact_ledger",
        "collect_airline_semantic_to_contract_causal_run_v01",
        "collect_airline_ticket_purchase_corridor_execution_result_v01",
    }
    call_names = {
        node.func.id
        for node in ast.walk(tree)
        if isinstance(node, ast.Call) and isinstance(node.func, ast.Name)
    }
    assert forbidden_calls.isdisjoint(call_names)


def test_static_no_manifest_envelope_or_b2b_verifier_invocation() -> None:
    source = open(MODULE_PATH, encoding="utf-8").read()
    tree = ast.parse(source)
    forbidden_attributes = {
        "build_airline_crypto_artifact_seal_manifest_core_v01",
        "build_airline_crypto_artifact_seal_envelope_v01",
        "verify_airline_crypto_artifact_seal_v01",
    }
    called_attributes = {
        node.func.attr
        for node in ast.walk(tree)
        if isinstance(node, ast.Call) and isinstance(node.func, ast.Attribute)
    }
    assert forbidden_attributes.isdisjoint(called_attributes)
    assert "AirlineCryptoArtifactSealVerificationReportV01" not in source


def test_static_no_mutable_module_global_registry() -> None:
    module = ast.parse(open(MODULE_PATH, encoding="utf-8").read())
    for node in module.body:
        if isinstance(node, (ast.Assign, ast.AnnAssign)):
            value = node.value
            assert not isinstance(value, (ast.List, ast.Dict, ast.Set))
            if isinstance(value, ast.Call):
                assert not (
                    isinstance(value.func, ast.Name)
                    and value.func.id in {"list", "dict", "set"}
                )


def test_static_public_module_has_no_collector_result_or_expected_anchor_surface() -> None:
    source = open(MODULE_PATH, encoding="utf-8").read()
    assert "expected_manifest_core_hash" not in source
    assert "post_collection_snapshot" not in source
    assert "CollectorResult" not in source
    assert "SELF_CONSISTENT_UNANCHORED" not in source
    assert "Replay" not in source


def test_contract_field_name_tuples_match_dataclass_fields() -> None:
    assert tuple(
        field.name
        for field in collector.AirlineCryptoArtifactSealAcceptedLedgerAuditV01.__dataclass_fields__.values()
    ) == collector.ACCEPTED_AUDIT_FIELD_NAMES
    assert tuple(
        field.name
        for field in collector.AirlineCryptoArtifactSealSourceBundleValidationReportV01.__dataclass_fields__.values()
    ) == collector.SOURCE_BUNDLE_VALIDATION_REPORT_FIELD_NAMES


def test_production_source_uses_only_ledger_contract_not_ledger_collector() -> None:
    source = inspect.getsource(collector)
    assert "transaction_artifact_ledger_collector_v01" not in source
    assert "semantic_to_contract" not in source
    assert "ticket_purchase_corridor" not in source

class _FilenameEqualityObject:
    def __init__(self, expected: str) -> None:
        self.expected = expected

    def __eq__(self, other: object) -> bool:
        return other == self.expected


def test_accepted_audit_requires_exact_string_source_file_refs() -> None:
    item = _valid_a()
    for malformed_refs in (
        tuple(
            _StringSubclass(ref)
            for ref in collector.REQUIRED_SOURCE_FILE_REFS
        ),
        tuple(
            _FilenameEqualityObject(ref)
            for ref in collector.REQUIRED_SOURCE_FILE_REFS
        ),
    ):
        audit = _accepted_audit(
            item,
            ledger.OFFER_A_ID,
            required_source_files=malformed_refs,
        )
        report = (
            collector
            .validate_airline_crypto_artifact_seal_accepted_ledger_audit_v01(
                audit,
            )
        )

        assert report.validation_status == collector.STATUS_FAIL_CLOSED
        assert (
            collector.REASON_ACCEPTED_AUDIT_REQUIRED_FILES_MISMATCH
            in report.validation_errors
        )


def test_invalid_source_snapshot_does_not_leave_mutable_backing_state() -> None:
    valid = _bundle(_valid_a(), ledger.OFFER_A_ID)
    mutable_before = list(valid.ordered_source_files_before_audit)

    invalid = replace(
        valid,
        ordered_source_files_before_audit=mutable_before,
    )

    assert invalid.ordered_source_files_before_audit == ()
    assert type(invalid.ordered_source_files_before_audit) is tuple

    mutable_before[0] = ("attacker.json", b"changed")

    assert invalid.ordered_source_files_before_audit == ()
    _assert_fail(
        invalid,
        collector.REASON_SOURCE_SNAPSHOT_BEFORE_MALFORMED,
    )
