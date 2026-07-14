from __future__ import annotations

import ast
import inspect
import json
from collections import Counter
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
    source_package_ref: str = PACKAGE_REF,
    identity: ledger.AirlineTransactionArtifactLedgerExpectedIdentityV01 | None = None,
    audit: collector.AirlineCryptoArtifactSealAcceptedLedgerAuditV01 | None = None,
    before: tuple[tuple[str, bytes], ...] | None = None,
    after: tuple[tuple[str, bytes], ...] | None = None,
) -> collector.AirlineCryptoArtifactSealSourceBundleV01:
    actual_identity = identity or _fixture_identity(offer_id)
    actual_before = before or _source_rows(item, actual_identity)
    return collector.build_airline_crypto_artifact_seal_source_bundle_v01(
        source_bundle_id=f"airline_crypto_source_bundle:{offer_id}",
        source_package_ref=source_package_ref,
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


def test_static_c2_uses_each_closed_collection_or_verification_call_once() -> None:
    source = open(MODULE_PATH, encoding="utf-8").read()
    tree = ast.parse(source)
    allowed_c2_attributes = {
        "build_airline_crypto_artifact_seal_manifest_core_v01",
        "build_airline_crypto_artifact_seal_envelope_v01",
        "verify_airline_crypto_artifact_seal_v01",
    }
    called_attributes = {
        node.func.attr
        for node in ast.walk(tree)
        if isinstance(node, ast.Call) and isinstance(node.func, ast.Attribute)
    }
    assert allowed_c2_attributes <= called_attributes
    counts = Counter(
        node.func.attr
        for node in ast.walk(tree)
        if isinstance(node, ast.Call) and isinstance(node.func, ast.Attribute)
    )
    assert all(counts[name] == 1 for name in allowed_c2_attributes)


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


def test_static_c2_surface_exists_without_later_slice_objects() -> None:
    source = open(MODULE_PATH, encoding="utf-8").read()
    tree = ast.parse(source)
    defined_names = {
        node.name
        for node in ast.walk(tree)
        if isinstance(node, (ast.ClassDef, ast.FunctionDef))
    }
    assert "AirlineCryptoArtifactSealCollectionResultV01" in defined_names
    assert "collect_airline_crypto_artifact_seal_from_source_bundle_v01" in defined_names
    assert "CryptoAudit" not in defined_names
    assert "CryptoWriter" not in defined_names
    assert "Replay" not in defined_names


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


def _collect_c2(
    bundle: collector.AirlineCryptoArtifactSealSourceBundleV01,
    *,
    callback: object | None = None,
    expected_anchor: object | None = None,
) -> collector.AirlineCryptoArtifactSealCollectionResultV01:
    actual_callback = callback or (
        lambda: bundle.ordered_source_files_after_audit
    )
    return collector.collect_airline_crypto_artifact_seal_from_source_bundle_v01(
        source_bundle=bundle,
        post_collection_snapshot_provider=actual_callback,
        expected_manifest_core_hash=expected_anchor,
    )


def _anchored_c2(
    bundle: collector.AirlineCryptoArtifactSealSourceBundleV01,
) -> collector.AirlineCryptoArtifactSealCollectionResultV01:
    unanchored = _collect_c2(bundle)
    return _collect_c2(
        bundle,
        expected_anchor=unanchored.manifest_core_hash,
    )


def _assert_collection_contract_pass(
    result: collector.AirlineCryptoArtifactSealCollectionResultV01,
) -> None:
    validation = collector.validate_airline_crypto_artifact_seal_collection_result_v01(
        result,
    )
    assert validation.validation_status == collector.STATUS_PASS
    assert validation.validation_errors == ()


def _semantic_causal_bundle(
) -> collector.AirlineCryptoArtifactSealSourceBundleV01:
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
    assert hold.artifact_id.startswith(
        "airline_hold_commit_packet:semantic_causal:",
    )
    assert hold.canonical_hash_input["hold_id"].startswith(
        "hold:semantic_causal:",
    )
    return _bundle(item, ledger.OFFER_A_ID, identity=identity)


@pytest.mark.parametrize(
    ("item_factory", "offer_id"),
    ((_valid_a, ledger.OFFER_A_ID), (_valid_b, ledger.OFFER_B_ID)),
)
def test_c2_fixture_offers_unanchored_and_anchored(
    item_factory,
    offer_id: str,
) -> None:
    bundle = _bundle(item_factory(), offer_id)
    unanchored = _collect_c2(bundle)
    anchored = _collect_c2(
        bundle,
        expected_anchor=unanchored.manifest_core_hash,
    )
    assert (
        unanchored.collection_status
        == collector.STATUS_SELF_CONSISTENT_UNANCHORED
    )
    assert unanchored.expected_manifest_core_hash is None
    assert anchored.collection_status == collector.STATUS_PASS
    assert anchored.expected_manifest_core_hash == anchored.manifest_core_hash
    assert anchored.verification_report is not None
    assert anchored.verification_report.external_anchor_supplied is True
    assert anchored.verification_report.external_anchor_verified is True
    assert anchored.verification_report.signature_verified is False
    _assert_collection_contract_pass(unanchored)
    _assert_collection_contract_pass(anchored)


def test_semantic_causal_c2_unanchored_and_anchored_preserve_lineage() -> None:
    bundle = _semantic_causal_bundle()
    unanchored = _collect_c2(bundle)
    anchored = _collect_c2(
        bundle,
        expected_anchor=unanchored.manifest_core_hash,
    )
    assert (
        unanchored.collection_status
        == collector.STATUS_SELF_CONSISTENT_UNANCHORED
    )
    assert anchored.collection_status == collector.STATUS_PASS
    assert anchored.manifest_core is not None
    assert (
        anchored.manifest_core.ledger_entry_count,
        anchored.manifest_core.dependency_edge_count,
        anchored.manifest_core.root_final_count,
    ) == (19, 29, 3)
    assert any(
        ref.startswith("airline_hold_commit_packet:semantic_causal:")
        for ref in anchored.manifest_core.ordered_artifact_refs
    )
    assert bundle.expected_identity.expected_source_identity_fields_by_type[
        ledger.ARTIFACT_AIRLINE_HOLD_PACKET
    ]["hold_id"].startswith("hold:semantic_causal:")


def test_c2_success_preserves_exact_duplicate_identity_and_hash_fields() -> None:
    bundle = _bundle(_valid_a(), ledger.OFFER_A_ID)
    result = _collect_c2(bundle)
    assert result.source_bundle_id == bundle.source_bundle_id
    assert result.source_package_ref == bundle.source_package_ref
    assert result.transaction_id == bundle.ledger_item.transaction_id
    assert result.ledger_id == bundle.ledger_item.ledger_id
    assert result.manifest_core is not None
    assert result.envelope is not None
    assert result.verification_report is not None
    assert (
        result.manifest_core_hash
        == result.envelope.manifest_core_hash
        == result.verification_report.manifest_core_hash
    )
    assert result.source_bytes_unchanged_after_audit is True
    assert result.source_bytes_unchanged_after_collection is True


def test_c2_success_has_exact_stage_and_zero_counters() -> None:
    result = _collect_c2(_bundle(_valid_a(), ledger.OFFER_A_ID))
    assert tuple(
        getattr(result, field_name)
        for field_name in collector.COLLECTION_STAGE_COUNT_FIELDS
    ) == (1, 1, 1, 1, 1)
    assert all(
        type(getattr(result, field_name)) is int
        and getattr(result, field_name) == 0
        for field_name in collector.COLLECTION_ZERO_COUNTER_FIELDS
    )


def test_c2_stage_order_is_manifest_envelope_callback_verifier(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    bundle = _bundle(_valid_a(), ledger.OFFER_A_ID)
    order: list[str] = []
    original_manifest = collector._collect_manifest_core_v01
    original_envelope = collector._collect_envelope_v01
    original_verify = collector._verify_collected_envelope_v01

    def manifest_wrapper(*args, **kwargs):
        order.append("manifest")
        return original_manifest(*args, **kwargs)

    def envelope_wrapper(*args, **kwargs):
        order.append("envelope")
        return original_envelope(*args, **kwargs)

    def callback():
        order.append("callback")
        return bundle.ordered_source_files_after_audit

    def verify_wrapper(*args, **kwargs):
        order.append("verify")
        return original_verify(*args, **kwargs)

    monkeypatch.setattr(collector, "_collect_manifest_core_v01", manifest_wrapper)
    monkeypatch.setattr(collector, "_collect_envelope_v01", envelope_wrapper)
    monkeypatch.setattr(collector, "_verify_collected_envelope_v01", verify_wrapper)
    result = _collect_c2(bundle, callback=callback)
    assert result.collection_status == collector.STATUS_SELF_CONSISTENT_UNANCHORED
    assert order == ["manifest", "envelope", "callback", "verify"]


def _contains_forbidden_plain_value(value: object) -> bool:
    if isinstance(
        value,
        (
            bytes,
            bytearray,
            MappingProxyType,
            ledger.AirlineTransactionArtifactLedgerV01,
            ledger.AirlineTransactionArtifactLedgerExpectedIdentityV01,
        ),
    ):
        return True
    if type(value) is dict:
        return any(
            _contains_forbidden_plain_value(key)
            or _contains_forbidden_plain_value(item)
            for key, item in value.items()
        )
    if type(value) is list:
        return any(_contains_forbidden_plain_value(item) for item in value)
    return False


@pytest.mark.parametrize("anchored", (False, True))
def test_collection_result_plain_projection_is_exact_and_json_safe(
    anchored: bool,
) -> None:
    bundle = _bundle(_valid_a(), ledger.OFFER_A_ID)
    result = _anchored_c2(bundle) if anchored else _collect_c2(bundle)
    plain = collector.airline_crypto_artifact_seal_collection_result_to_plain_dict_v01(
        result,
    )
    assert tuple(plain) == collector.COLLECTION_RESULT_FIELD_NAMES
    assert (
        seal.validate_airline_crypto_canonical_json_value_v01(plain).validation_status
        == seal.STATUS_PASS
    )
    assert not _contains_forbidden_plain_value(plain)
    assert "ledger_item" not in plain
    assert "expected_identity" not in plain
    assert "post_collection_snapshot_provider" not in plain


def test_collection_result_is_frozen_and_plain_projection_is_independent() -> None:
    result = _collect_c2(_bundle(_valid_a(), ledger.OFFER_A_ID))
    with pytest.raises(FrozenInstanceError):
        result.collection_status = "changed"  # type: ignore[misc]
    assert type(result.collection_errors) is tuple
    plain = collector.airline_crypto_artifact_seal_collection_result_to_plain_dict_v01(
        result,
    )
    plain["collection_status"] = "changed"
    assert result.collection_status == collector.STATUS_SELF_CONSISTENT_UNANCHORED


def test_repeated_collection_and_a_b_isolation_are_deterministic() -> None:
    a = _bundle(_valid_a(), ledger.OFFER_A_ID)
    b = _bundle(_valid_b(), ledger.OFFER_B_ID)
    a1, b1, a2, b2 = _collect_c2(a), _collect_c2(b), _collect_c2(a), _collect_c2(b)
    assert a1 == a2
    assert b1 == b2
    assert a1 != b1
    aa1, bb1, aa2, bb2 = _anchored_c2(a), _anchored_c2(b), _anchored_c2(a), _anchored_c2(b)
    assert aa1 == aa2
    assert bb1 == bb2
    assert aa1 != bb1


def test_collection_does_not_mutate_any_exact_source_object() -> None:
    bundle = _bundle(_valid_a(), ledger.OFFER_A_ID)
    bundle_before = deepcopy(bundle)
    ledger_before = deepcopy(bundle.ledger_item)
    identity_before = deepcopy(bundle.expected_identity)
    before_snapshot = bundle.ordered_source_files_before_audit
    after_snapshot = bundle.ordered_source_files_after_audit
    result = _collect_c2(bundle)
    assert bundle == bundle_before
    assert bundle.ledger_item == ledger_before
    assert bundle.expected_identity == identity_before
    assert bundle.ordered_source_files_before_audit == before_snapshot
    assert bundle.ordered_source_files_after_audit == after_snapshot
    assert result.manifest_core == result.envelope.manifest_core  # type: ignore[union-attr]
    assert result.envelope is not None
    assert result.verification_report is not None


def test_invalid_source_bundle_short_circuits_every_later_stage(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    calls = Counter()

    def forbidden(name: str):
        def invoke(*args, **kwargs):
            calls[name] += 1
            raise AssertionError(name)

        return invoke

    monkeypatch.setattr(collector, "_collect_manifest_core_v01", forbidden("manifest"))
    monkeypatch.setattr(collector, "_collect_envelope_v01", forbidden("envelope"))
    monkeypatch.setattr(collector, "_verify_collected_envelope_v01", forbidden("verify"))

    def callback():
        calls["callback"] += 1
        raise AssertionError("callback")

    result = collector.collect_airline_crypto_artifact_seal_from_source_bundle_v01(
        source_bundle=object(),
        post_collection_snapshot_provider=callback,
    )
    assert result.collection_status == collector.STATUS_FAIL_CLOSED
    assert tuple(
        getattr(result, field_name)
        for field_name in collector.COLLECTION_STAGE_COUNT_FIELDS
    ) == (1, 0, 0, 0, 0)
    assert calls == Counter()
    _assert_collection_contract_pass(result)


@pytest.mark.parametrize(
    "bundle_mutation",
    ("failed_audit", "wrong_identity", "changed_after_audit", "ledger_json"),
)
def test_invalid_c1_bundle_stops_before_collection_stages(
    bundle_mutation: str,
) -> None:
    valid = _bundle(_valid_a(), ledger.OFFER_A_ID)
    if bundle_mutation == "failed_audit":
        bundle = replace(
            valid,
            accepted_audit=replace(
                valid.accepted_audit,
                final_status=collector.STATUS_FAIL_CLOSED,
            ),
        )
    elif bundle_mutation == "wrong_identity":
        bundle = replace(valid, expected_identity=_fixture_identity(ledger.OFFER_B_ID))
    elif bundle_mutation == "changed_after_audit":
        changed = list(valid.ordered_source_files_after_audit)
        changed[-1] = (changed[-1][0], changed[-1][1] + b"changed")
        bundle = replace(
            valid,
            ordered_source_files_after_audit=tuple(changed),
        )
    else:
        changed = list(valid.ordered_source_files_before_audit)
        changed[0] = (changed[0][0], b"{}")
        bundle = replace(
            valid,
            ordered_source_files_before_audit=tuple(changed),
            ordered_source_files_after_audit=tuple(changed),
        )
    result = _collect_c2(bundle)
    assert result.collection_status == collector.STATUS_FAIL_CLOSED
    assert tuple(
        getattr(result, field_name)
        for field_name in collector.COLLECTION_STAGE_COUNT_FIELDS
    ) == (1, 0, 0, 0, 0)
    assert (
        collector.REASON_COLLECTION_SOURCE_BUNDLE_VALIDATION_FAILED
        in result.collection_errors
    )


def test_non_callable_callback_stops_before_manifest_collection() -> None:
    result = _collect_c2(
        _bundle(_valid_a(), ledger.OFFER_A_ID),
        callback=42,
    )
    assert result.collection_status == collector.STATUS_FAIL_CLOSED
    assert tuple(
        getattr(result, field_name)
        for field_name in collector.COLLECTION_STAGE_COUNT_FIELDS
    ) == (1, 0, 0, 0, 0)
    assert (
        collector.REASON_POST_COLLECTION_SNAPSHOT_PROVIDER_INVALID
        in result.collection_errors
    )


@pytest.mark.parametrize("exception_type", (ValueError, RuntimeError))
def test_callback_exception_is_sanitized_and_stops_before_verifier(
    exception_type,
) -> None:
    def callback():
        raise exception_type("private callback text")

    result = _collect_c2(
        _bundle(_valid_a(), ledger.OFFER_A_ID),
        callback=callback,
    )
    assert result.collection_status == collector.STATUS_FAIL_CLOSED
    assert tuple(
        getattr(result, field_name)
        for field_name in collector.COLLECTION_STAGE_COUNT_FIELDS
    ) == (1, 1, 1, 1, 0)
    assert result.collection_errors == (
        collector.REASON_POST_COLLECTION_SNAPSHOT_PROVIDER_FAILED,
    )
    assert "private callback text" not in repr(result)
    assert result.verification_report is None
    _assert_collection_contract_pass(result)


def test_callback_requiring_argument_fails_once_without_verification() -> None:
    calls = 0

    def callback(required):
        nonlocal calls
        calls += 1
        return required

    result = _collect_c2(
        _bundle(_valid_a(), ledger.OFFER_A_ID),
        callback=callback,
    )
    assert calls == 0
    assert result.post_collection_snapshot_provider_call_count == 1
    assert result.verification_count == 0
    assert result.collection_status == collector.STATUS_FAIL_CLOSED


def test_manifest_failure_stops_every_later_stage(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setattr(
        collector,
        "_collect_manifest_core_v01",
        lambda *args, **kwargs: (_ for _ in ()).throw(ValueError("private")),
    )
    result = _collect_c2(_bundle(_valid_a(), ledger.OFFER_A_ID))
    assert tuple(
        getattr(result, field_name)
        for field_name in collector.COLLECTION_STAGE_COUNT_FIELDS
    ) == (1, 1, 0, 0, 0)
    assert result.collection_errors == (
        collector.REASON_MANIFEST_CORE_COLLECTION_FAILED,
    )
    _assert_collection_contract_pass(result)


def test_envelope_failure_stops_callback_and_verifier(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setattr(
        collector,
        "_collect_envelope_v01",
        lambda *args, **kwargs: (_ for _ in ()).throw(RuntimeError("private")),
    )
    result = _collect_c2(_bundle(_valid_a(), ledger.OFFER_A_ID))
    assert tuple(
        getattr(result, field_name)
        for field_name in collector.COLLECTION_STAGE_COUNT_FIELDS
    ) == (1, 1, 1, 0, 0)
    assert result.collection_errors == (
        collector.REASON_ENVELOPE_COLLECTION_FAILED,
    )
    _assert_collection_contract_pass(result)


def test_verifier_exception_returns_honest_fail_closed_result(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setattr(
        collector,
        "_verify_collected_envelope_v01",
        lambda *args, **kwargs: (_ for _ in ()).throw(RuntimeError("private")),
    )
    result = _collect_c2(_bundle(_valid_a(), ledger.OFFER_A_ID))
    assert result.verification_count == 1
    assert result.verification_report is None
    assert result.collection_errors == (collector.REASON_VERIFICATION_CALL_FAILED,)
    _assert_collection_contract_pass(result)


class _TupleSubclass(tuple):
    pass


class _CustomEqualitySnapshot:
    def __eq__(self, other: object) -> bool:
        return True


@pytest.mark.parametrize(
    "mutation",
    (
        "list_outer",
        "tuple_subclass",
        "missing",
        "extra",
        "reordered",
        "list_row",
        "tuple_subclass_row",
        "str_subclass",
        "bytearray",
        "memoryview",
        "custom_equality",
        "changed_ref",
    ),
)
def test_malformed_post_collection_snapshot_is_not_repaired_and_is_verified_once(
    mutation: str,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    bundle = _bundle(_valid_a(), ledger.OFFER_A_ID)
    rows = list(bundle.ordered_source_files_after_audit)
    if mutation == "list_outer":
        observed: object = rows
    elif mutation == "tuple_subclass":
        observed = _TupleSubclass(rows)
    elif mutation == "missing":
        observed = tuple(rows[:-1])
    elif mutation == "extra":
        observed = tuple(rows + [("extra.json", b"{}")])
    elif mutation == "reordered":
        rows[0], rows[1] = rows[1], rows[0]
        observed = tuple(rows)
    elif mutation == "list_row":
        rows[0] = list(rows[0])  # type: ignore[assignment]
        observed = tuple(rows)
    elif mutation == "tuple_subclass_row":
        rows[0] = _TupleSubclass(rows[0])
        observed = tuple(rows)
    elif mutation == "str_subclass":
        rows[0] = (_StringSubclass(rows[0][0]), rows[0][1])
        observed = tuple(rows)
    elif mutation == "bytearray":
        rows[0] = (rows[0][0], bytearray(rows[0][1]))  # type: ignore[arg-type]
        observed = tuple(rows)
    elif mutation == "memoryview":
        rows[0] = (rows[0][0], memoryview(rows[0][1]))  # type: ignore[arg-type]
        observed = tuple(rows)
    elif mutation == "custom_equality":
        observed = _CustomEqualitySnapshot()
    else:
        rows[-1] = ("foreign.json", rows[-1][1])
        observed = tuple(rows)
    verify_calls = 0
    original_verify = collector._verify_collected_envelope_v01

    def verify_wrapper(*args, **kwargs):
        nonlocal verify_calls
        verify_calls += 1
        assert kwargs["ordered_source_files_after"] is observed
        return original_verify(*args, **kwargs)

    monkeypatch.setattr(collector, "_verify_collected_envelope_v01", verify_wrapper)
    result = _collect_c2(bundle, callback=lambda: observed)
    assert verify_calls == 1
    assert result.verification_count == 1
    assert result.collection_status == collector.STATUS_FAIL_CLOSED
    assert (
        collector.REASON_POST_COLLECTION_SNAPSHOT_MALFORMED
        in result.collection_errors
    )
    assert not hasattr(result, "post_collection_snapshot")
    _assert_collection_contract_pass(result)


def test_changed_post_collection_byte_runs_verifier_and_fails_closed() -> None:
    bundle = _bundle(_valid_a(), ledger.OFFER_A_ID)
    rows = list(bundle.ordered_source_files_after_audit)
    rows[-1] = (rows[-1][0], rows[-1][1] + b"changed")
    result = _collect_c2(bundle, callback=lambda: tuple(rows))
    assert result.verification_count == 1
    assert result.verification_report is not None
    assert result.verification_report.source_bytes_unchanged is False
    assert (
        collector.REASON_POST_COLLECTION_SOURCE_BYTES_CHANGED
        in result.collection_errors
    )
    assert collector.REASON_COLLECTION_VERIFICATION_FAILED in result.collection_errors
    _assert_collection_contract_pass(result)


@pytest.mark.parametrize("separate_copy", (False, True))
def test_exact_or_separately_copied_post_collection_tuple_passes(
    separate_copy: bool,
) -> None:
    bundle = _bundle(_valid_a(), ledger.OFFER_A_ID)
    observed = (
        tuple((ref, content) for ref, content in bundle.ordered_source_files_after_audit)
        if separate_copy
        else bundle.ordered_source_files_after_audit
    )
    result = _collect_c2(bundle, callback=lambda: observed)
    assert result.collection_status == collector.STATUS_SELF_CONSISTENT_UNANCHORED
    assert result.source_bytes_unchanged_after_collection is True


def test_mutable_callback_input_is_not_retained_or_exposed() -> None:
    bundle = _bundle(_valid_a(), ledger.OFFER_A_ID)
    temporary = list(bundle.ordered_source_files_after_audit)
    observed = tuple(temporary)
    result = _collect_c2(bundle, callback=lambda: observed)
    plain_before = collector.airline_crypto_artifact_seal_collection_result_to_plain_dict_v01(
        result,
    )
    temporary[0] = ("changed.json", b"changed")
    assert result.collection_status == collector.STATUS_SELF_CONSISTENT_UNANCHORED
    assert (
        collector.airline_crypto_artifact_seal_collection_result_to_plain_dict_v01(
            result,
        )
        == plain_before
    )
    assert not hasattr(result, "ordered_source_files_after_collection")


def test_missing_anchor_never_self_anchors() -> None:
    signature = inspect.signature(
        collector.collect_airline_crypto_artifact_seal_from_source_bundle_v01,
    )
    assert signature.parameters["expected_manifest_core_hash"].default is None
    result = _collect_c2(_bundle(_valid_a(), ledger.OFFER_A_ID))
    assert result.collection_status == collector.STATUS_SELF_CONSISTENT_UNANCHORED
    assert result.collection_status != collector.STATUS_PASS
    assert result.expected_manifest_core_hash is None
    assert result.verification_report.external_anchor_supplied is False  # type: ignore[union-attr]


@pytest.mark.parametrize(
    "anchor",
    (
        "0" * 64,
        "A" * 64,
        "0" * 63,
        b"0" * 64,
        _StringSubclass("0" * 64),
        _CustomEqualitySnapshot(),
    ),
)
def test_wrong_or_malformed_anchor_fails_closed_without_arbitrary_retention(
    anchor: object,
) -> None:
    result = _collect_c2(
        _bundle(_valid_a(), ledger.OFFER_A_ID),
        expected_anchor=anchor,
    )
    assert result.collection_status == collector.STATUS_FAIL_CLOSED
    assert result.verification_report is not None
    assert collector.REASON_COLLECTION_VERIFICATION_FAILED in result.collection_errors
    if type(anchor) is str and seal.validate_sha256_hex_v01(anchor).validation_status == seal.STATUS_PASS:
        assert result.expected_manifest_core_hash == anchor
    else:
        assert result.expected_manifest_core_hash is None
        assert repr(anchor) not in repr(result)


def test_coordinated_modified_package_fails_original_anchor_but_is_unanchored_without_it() -> None:
    original = _bundle(_valid_a(), ledger.OFFER_A_ID)
    original_result = _collect_c2(original)
    changed_rows = list(original.ordered_source_files_before_audit)
    changed_rows[-1] = (changed_rows[-1][0], changed_rows[-1][1] + b"changed")
    modified = _bundle(
        original.ledger_item,
        ledger.OFFER_A_ID,
        identity=original.expected_identity,
        before=tuple(changed_rows),
        after=tuple(changed_rows),
    )
    anchored = _collect_c2(
        modified,
        expected_anchor=original_result.manifest_core_hash,
    )
    unanchored = _collect_c2(modified)
    assert anchored.collection_status == collector.STATUS_FAIL_CLOSED
    assert anchored.verification_report is not None
    assert anchored.verification_report.external_anchor_verified is False
    assert (
        collector.REASON_COLLECTION_EXPECTED_ANCHOR_MISMATCH
        in anchored.collection_errors
    )
    assert (
        unanchored.collection_status
        == collector.STATUS_SELF_CONSISTENT_UNANCHORED
    )
    assert unanchored.collection_status != collector.STATUS_PASS
    assert modified.ordered_source_files_before_audit == tuple(changed_rows)


def test_collection_result_wrong_type_fails_contract_validation() -> None:
    report = collector.validate_airline_crypto_artifact_seal_collection_result_v01(
        object(),
    )
    assert report.validation_status == collector.STATUS_FAIL_CLOSED
    assert report.validation_errors == (collector.REASON_COLLECTION_RESULT_WRONG_TYPE,)


def test_direct_result_status_is_derived_from_complete_state() -> None:
    valid = _collect_c2(_bundle(_valid_a(), ledger.OFFER_A_ID))
    with_errors = replace(
        valid,
        collection_status=collector.STATUS_PASS,
        collection_errors=(collector.REASON_COLLECTION_VERIFICATION_FAILED,),
    )
    assert with_errors.collection_status == collector.STATUS_FAIL_CLOSED
    without_nested = replace(
        valid,
        collection_status=collector.STATUS_PASS,
        manifest_core=None,
        envelope=None,
        verification_report=None,
    )
    assert without_nested.collection_status == collector.STATUS_FAIL_CLOSED
    without_only_envelope = replace(
        valid,
        collection_status=collector.STATUS_PASS,
        envelope=None,
    )
    assert (
        without_only_envelope.collection_status
        == collector.STATUS_FAIL_CLOSED
    )
    assert (
        collector.validate_airline_crypto_artifact_seal_collection_result_v01(
            without_only_envelope,
        ).validation_status
        == collector.STATUS_FAIL_CLOSED
    )
    expected_present = replace(
        valid,
        expected_manifest_core_hash=valid.manifest_core_hash,
    )
    assert expected_present.collection_status == collector.STATUS_FAIL_CLOSED


def test_result_contract_rejects_duplicate_view_divergence() -> None:
    unanchored = _collect_c2(_bundle(_valid_a(), ledger.OFFER_A_ID))
    anchored = _anchored_c2(_bundle(_valid_a(), ledger.OFFER_A_ID))
    source_report = replace(
        unanchored.source_bundle_validation_report,
        source_bundle_id="foreign_bundle",
    )
    source_mismatch = replace(
        unanchored,
        source_bundle_validation_report=source_report,
    )
    assert (
        collector.validate_airline_crypto_artifact_seal_collection_result_v01(
            source_mismatch,
        ).validation_status
        == collector.STATUS_FAIL_CLOSED
    )
    wrong_expected = replace(
        anchored,
        expected_manifest_core_hash="0" * 64,
    )
    assert wrong_expected.collection_status == collector.STATUS_FAIL_CLOSED
    assert (
        collector.validate_airline_crypto_artifact_seal_collection_result_v01(
            wrong_expected,
        ).validation_status
        == collector.STATUS_FAIL_CLOSED
    )


def test_result_contract_rejects_manifest_envelope_and_report_identity_mismatch() -> None:
    a = _collect_c2(_bundle(_valid_a(), ledger.OFFER_A_ID))
    b = _collect_c2(_bundle(_valid_b(), ledger.OFFER_B_ID))
    envelope_mismatch = replace(a, envelope=b.envelope)
    assert envelope_mismatch.collection_status == collector.STATUS_FAIL_CLOSED
    assert (
        collector.validate_airline_crypto_artifact_seal_collection_result_v01(
            envelope_mismatch,
        ).validation_status
        == collector.STATUS_FAIL_CLOSED
    )
    report_mismatch = replace(a, verification_report=b.verification_report)
    assert report_mismatch.collection_status == collector.STATUS_FAIL_CLOSED
    assert (
        collector.validate_airline_crypto_artifact_seal_collection_result_v01(
            report_mismatch,
        ).validation_status
        == collector.STATUS_FAIL_CLOSED
    )


def test_result_contract_rejects_false_source_stability() -> None:
    valid = _collect_c2(_bundle(_valid_a(), ledger.OFFER_A_ID))
    changed = replace(valid, source_bytes_unchanged_after_audit=False)
    assert changed.collection_status == collector.STATUS_FAIL_CLOSED
    assert (
        collector.validate_airline_crypto_artifact_seal_collection_result_v01(
            changed,
        ).validation_status
        == collector.STATUS_FAIL_CLOSED
    )


@pytest.mark.parametrize(
    "changes",
    (
        {"source_bundle_validation_count": True},
        {"manifest_core_collection_count": 2},
        {"manifest_core_collection_count": 0, "envelope_collection_count": 1},
        {"provider_call_count": False},
        {"real_world_effects_count": 1},
    ),
)
def test_result_contract_rejects_stage_or_zero_counter_malformed_state(
    changes: dict[str, object],
) -> None:
    changed = replace(
        _collect_c2(_bundle(_valid_a(), ledger.OFFER_A_ID)),
        **changes,
    )
    assert changed.collection_status == collector.STATUS_FAIL_CLOSED
    assert (
        collector.validate_airline_crypto_artifact_seal_collection_result_v01(
            changed,
        ).validation_status
        == collector.STATUS_FAIL_CLOSED
    )


@pytest.mark.parametrize(
    ("errors", "expected"),
    (
        ({}, collector.REASON_COLLECTION_ERROR_CONTAINER_MALFORMED),
        (("unknown",), collector.REASON_COLLECTION_ERROR_CONTAINER_MALFORMED),
        (("\ud800",), collector.REASON_COLLECTION_ERROR_CONTAINER_MALFORMED),
    ),
)
def test_collection_error_container_is_closed_and_sanitized(
    errors: object,
    expected: str,
) -> None:
    valid = _collect_c2(_bundle(_valid_a(), ledger.OFFER_A_ID))
    changed = replace(valid, collection_errors=errors)
    assert changed.collection_status == collector.STATUS_FAIL_CLOSED
    assert changed.collection_errors == (expected,)
    assert (
        collector.validate_airline_crypto_artifact_seal_collection_result_v01(
            changed,
        ).validation_status
        == collector.STATUS_FAIL_CLOSED
    )


def test_collection_error_list_is_frozen_from_caller_mutation() -> None:
    valid = _collect_c2(_bundle(_valid_a(), ledger.OFFER_A_ID))
    errors = [collector.REASON_COLLECTION_VERIFICATION_FAILED]
    changed = replace(valid, collection_errors=errors)
    errors.append(collector.REASON_ENVELOPE_COLLECTION_FAILED)
    assert changed.collection_errors == (
        collector.REASON_COLLECTION_VERIFICATION_FAILED,
    )


def test_honest_fail_closed_results_are_contract_valid_and_json_safe() -> None:
    bundle = _bundle(_valid_a(), ledger.OFFER_A_ID)
    changed_rows = list(bundle.ordered_source_files_after_audit)
    changed_rows[-1] = (
        changed_rows[-1][0],
        changed_rows[-1][1] + b"changed",
    )
    source_changed = _collect_c2(
        bundle,
        callback=lambda: tuple(changed_rows),
    )
    wrong_anchor = _collect_c2(bundle, expected_anchor="0" * 64)

    def failed_callback():
        raise RuntimeError("private")

    callback_failed = _collect_c2(bundle, callback=failed_callback)
    for result in (source_changed, wrong_anchor, callback_failed):
        assert result.collection_status == collector.STATUS_FAIL_CLOSED
        _assert_collection_contract_pass(result)
        plain = collector.airline_crypto_artifact_seal_collection_result_to_plain_dict_v01(
            result,
        )
        assert plain["collection_status"] == collector.STATUS_FAIL_CLOSED
        assert (
            seal.validate_airline_crypto_canonical_json_value_v01(plain).validation_status
            == seal.STATUS_PASS
        )


@pytest.mark.parametrize("malformed", (None, {}, [], "bad", 1, object()))
def test_collection_result_validator_never_leaks_shape_exceptions(
    malformed: object,
) -> None:
    report = collector.validate_airline_crypto_artifact_seal_collection_result_v01(
        malformed,
    )
    assert report.validation_status == collector.STATUS_FAIL_CLOSED


def test_collection_result_field_names_match_exact_contract() -> None:
    assert tuple(
        collector.AirlineCryptoArtifactSealCollectionResultV01.__dataclass_fields__
    ) == collector.COLLECTION_RESULT_FIELD_NAMES


def test_static_c2_has_no_hardcoded_fixture_or_package_paths() -> None:
    source = open(MODULE_PATH, encoding="utf-8").read()
    assert ledger.OFFER_A_ID not in source
    assert ledger.OFFER_B_ID not in source
    assert ledger.TRANSACTION_ID not in source
    assert "airline_transaction_artifact_ledger_slice_e2_offline_f244512" not in source
    assert ".tmp/" not in source


def test_source_bundle_report_pass_requires_closed_nonempty_identity() -> None:
    valid = _report(_bundle(_valid_a(), ledger.OFFER_A_ID))
    invalid_identities = (
        ("", valid.source_package_ref),
        (valid.source_bundle_id, ""),
        (valid.source_bundle_id, "a/b"),
        (valid.source_bundle_id, "."),
    )
    for source_bundle_id, source_package_ref in invalid_identities:
        changed = replace(
            valid,
            source_bundle_id=source_bundle_id,
            source_package_ref=source_package_ref,
        )
        assert changed.validation_status == collector.STATUS_FAIL_CLOSED


def test_result_rejects_spliced_foreign_source_package_identity() -> None:
    original = _collect_c2(_bundle(_valid_a(), ledger.OFFER_A_ID))
    foreign = _collect_c2(
        _bundle(
            _valid_a(),
            ledger.OFFER_A_ID,
            source_package_ref="foreign_airline_crypto_package",
        ),
    )
    spliced = replace(
        original,
        transaction_id=foreign.transaction_id,
        ledger_id=foreign.ledger_id,
        manifest_core_hash=foreign.manifest_core_hash,
        manifest_core=foreign.manifest_core,
        envelope=foreign.envelope,
        verification_report=foreign.verification_report,
    )
    assert spliced.collection_status == collector.STATUS_FAIL_CLOSED
    validation = collector.validate_airline_crypto_artifact_seal_collection_result_v01(
        spliced,
    )
    assert validation.validation_status == collector.STATUS_FAIL_CLOSED
    assert collector.REASON_COLLECTION_IDENTITY_MISMATCH in validation.validation_errors


def test_wrong_type_nested_verification_report_is_discarded(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setattr(
        collector,
        "_verify_collected_envelope_v01",
        lambda *args, **kwargs: object(),
    )
    result = _collect_c2(_bundle(_valid_a(), ledger.OFFER_A_ID))
    assert result.collection_status == collector.STATUS_FAIL_CLOSED
    assert result.verification_report is None
    assert result.verification_count == 1
    assert result.collection_errors == (
        collector.REASON_VERIFICATION_REPORT_CONTRACT_INVALID,
        collector.REASON_VERIFICATION_REPORT_MISSING,
    )
    _assert_collection_contract_pass(result)
    collector.airline_crypto_artifact_seal_collection_result_to_plain_dict_v01(result)


def test_foreign_contract_valid_verification_report_is_discarded(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    foreign_report = _collect_c2(
        _bundle(_valid_b(), ledger.OFFER_B_ID),
    ).verification_report
    assert foreign_report is not None
    monkeypatch.setattr(
        collector,
        "_verify_collected_envelope_v01",
        lambda *args, **kwargs: foreign_report,
    )
    result = _collect_c2(_bundle(_valid_a(), ledger.OFFER_A_ID))
    assert result.collection_status == collector.STATUS_FAIL_CLOSED
    assert result.verification_report is None
    assert collector.REASON_COLLECTION_IDENTITY_MISMATCH in result.collection_errors
    assert collector.REASON_VERIFICATION_REPORT_MISSING in result.collection_errors
    _assert_collection_contract_pass(result)
    collector.airline_crypto_artifact_seal_collection_result_to_plain_dict_v01(result)


def test_nested_pass_cannot_replace_wrong_caller_anchor(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    bundle = _bundle(_valid_a(), ledger.OFFER_A_ID)
    correct = _anchored_c2(bundle)
    assert correct.verification_report is not None
    wrong_anchor = "0" * 64
    assert wrong_anchor != correct.manifest_core_hash
    monkeypatch.setattr(
        collector,
        "_verify_collected_envelope_v01",
        lambda *args, **kwargs: correct.verification_report,
    )
    result = _collect_c2(bundle, expected_anchor=wrong_anchor)
    assert result.collection_status == collector.STATUS_FAIL_CLOSED
    assert result.expected_manifest_core_hash == wrong_anchor
    assert result.verification_report is None
    assert (
        collector.REASON_COLLECTION_EXPECTED_ANCHOR_MISMATCH
        in result.collection_errors
    )
    assert collector.REASON_VERIFICATION_REPORT_MISSING in result.collection_errors
    _assert_collection_contract_pass(result)
    collector.airline_crypto_artifact_seal_collection_result_to_plain_dict_v01(result)


def test_correct_anchor_with_changed_source_is_not_anchor_mismatch() -> None:
    bundle = _bundle(_valid_a(), ledger.OFFER_A_ID)
    correct_anchor = _collect_c2(bundle).manifest_core_hash
    changed = list(bundle.ordered_source_files_after_audit)
    changed[-1] = (changed[-1][0], changed[-1][1] + b"changed")
    result = _collect_c2(
        bundle,
        callback=lambda: tuple(changed),
        expected_anchor=correct_anchor,
    )
    assert result.collection_status == collector.STATUS_FAIL_CLOSED
    assert result.verification_report is not None
    assert result.verification_report.expected_manifest_core_hash == correct_anchor
    assert (
        collector.REASON_POST_COLLECTION_SOURCE_BYTES_CHANGED
        in result.collection_errors
    )
    assert collector.REASON_COLLECTION_VERIFICATION_FAILED in result.collection_errors
    assert (
        collector.REASON_COLLECTION_EXPECTED_ANCHOR_MISMATCH
        not in result.collection_errors
    )


def test_successful_nested_report_cannot_hide_malformed_callback(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    bundle = _bundle(_valid_a(), ledger.OFFER_A_ID)
    successful_report = _collect_c2(bundle).verification_report
    assert successful_report is not None
    monkeypatch.setattr(
        collector,
        "_verify_collected_envelope_v01",
        lambda *args, **kwargs: successful_report,
    )
    result = _collect_c2(bundle, callback=lambda: [])
    assert result.collection_status == collector.STATUS_FAIL_CLOSED
    assert result.verification_report is None
    assert collector.REASON_POST_COLLECTION_SNAPSHOT_MALFORMED in result.collection_errors
    assert collector.REASON_COLLECTION_RESULT_FIELD_MISMATCH in result.collection_errors
    assert collector.REASON_VERIFICATION_REPORT_MISSING in result.collection_errors
    _assert_collection_contract_pass(result)
    collector.airline_crypto_artifact_seal_collection_result_to_plain_dict_v01(result)


def test_malformed_caller_anchor_cannot_become_unanchored_success(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    bundle = _bundle(_valid_a(), ledger.OFFER_A_ID)
    unanchored_report = _collect_c2(bundle).verification_report
    assert unanchored_report is not None
    monkeypatch.setattr(
        collector,
        "_verify_collected_envelope_v01",
        lambda *args, **kwargs: unanchored_report,
    )
    result = _collect_c2(bundle, expected_anchor="A" * 64)
    assert result.collection_status == collector.STATUS_FAIL_CLOSED
    assert result.expected_manifest_core_hash is None
    assert result.verification_report is None
    assert (
        collector.REASON_COLLECTION_EXPECTED_ANCHOR_MISMATCH
        in result.collection_errors
    )
    assert collector.REASON_VERIFICATION_REPORT_MISSING in result.collection_errors
    _assert_collection_contract_pass(result)
    collector.airline_crypto_artifact_seal_collection_result_to_plain_dict_v01(result)


@pytest.mark.parametrize(
    ("field_name", "foreign_value"),
    (
        ("source_bundle_id", "foreign_airline_crypto_source_bundle"),
        ("source_package_ref", "foreign_airline_crypto_source_package"),
    ),
)
def test_foreign_c1_report_identity_is_sanitized_before_manifest_collection(
    field_name: str,
    foreign_value: str,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    bundle = _bundle(_valid_a(), ledger.OFFER_A_ID)
    real_report = _report(bundle)
    foreign_report = replace(real_report, **{field_name: foreign_value})
    assert foreign_report.validation_status == collector.STATUS_PASS
    monkeypatch.setattr(
        collector,
        "validate_airline_crypto_artifact_seal_source_bundle_v01",
        lambda source_bundle: foreign_report,
    )
    result = _collect_c2(bundle)
    assert result.collection_status == collector.STATUS_FAIL_CLOSED
    assert result.source_bundle_id == bundle.source_bundle_id
    assert result.source_package_ref == bundle.source_package_ref
    assert tuple(
        getattr(result, name)
        for name in collector.COLLECTION_STAGE_COUNT_FIELDS
    ) == (1, 0, 0, 0, 0)
    assert (
        collector.REASON_COLLECTION_SOURCE_BUNDLE_VALIDATION_REPORT_MALFORMED
        in result.collection_errors
    )
    assert (
        collector.REASON_COLLECTION_SOURCE_BUNDLE_VALIDATION_FAILED
        in result.collection_errors
    )
    assert collector.REASON_COLLECTION_IDENTITY_MISMATCH in result.collection_errors
    _assert_collection_contract_pass(result)
    collector.airline_crypto_artifact_seal_collection_result_to_plain_dict_v01(result)


@pytest.mark.parametrize("foreign_kind", ("source_package_ref", "other_ledger"))
def test_foreign_manifest_identity_stops_before_envelope_collection(
    foreign_kind: str,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    bundle = _bundle(_valid_a(), ledger.OFFER_A_ID)
    if foreign_kind == "source_package_ref":
        foreign_manifest = _collect_c2(
            _bundle(
                _valid_a(),
                ledger.OFFER_A_ID,
                source_package_ref="foreign_airline_crypto_package",
            ),
        ).manifest_core
    else:
        foreign_manifest = _collect_c2(
            _bundle(_valid_b(), ledger.OFFER_B_ID),
        ).manifest_core
    assert foreign_manifest is not None
    callback_calls = 0

    def callback():
        nonlocal callback_calls
        callback_calls += 1
        return bundle.ordered_source_files_after_audit

    monkeypatch.setattr(
        collector,
        "_collect_manifest_core_v01",
        lambda *args, **kwargs: foreign_manifest,
    )
    result = _collect_c2(bundle, callback=callback)
    assert result.collection_status == collector.STATUS_FAIL_CLOSED
    assert result.manifest_core is None
    assert result.envelope is None
    assert result.verification_report is None
    assert callback_calls == 0
    assert tuple(
        getattr(result, name)
        for name in collector.COLLECTION_STAGE_COUNT_FIELDS
    ) == (1, 1, 0, 0, 0)
    assert result.collection_errors == (
        collector.REASON_MANIFEST_CORE_COLLECTION_FAILED,
    )
    _assert_collection_contract_pass(result)
    collector.airline_crypto_artifact_seal_collection_result_to_plain_dict_v01(result)


@pytest.mark.parametrize(
    "invalid_ref",
    (".", "..", "a/b", "a\\b", "/absolute"),
)
def test_invalid_source_package_ref_is_sanitized_and_serializable(
    invalid_ref: str,
) -> None:
    valid = _bundle(_valid_a(), ledger.OFFER_A_ID)
    invalid = replace(valid, source_package_ref=invalid_ref)
    c1_report = _report(invalid)
    assert c1_report.validation_status == collector.STATUS_FAIL_CLOSED
    assert c1_report.source_package_ref == ""
    result = _collect_c2(invalid)
    assert result.collection_status == collector.STATUS_FAIL_CLOSED
    assert result.source_package_ref == ""
    assert tuple(
        getattr(result, name)
        for name in collector.COLLECTION_STAGE_COUNT_FIELDS
    ) == (1, 0, 0, 0, 0)
    assert (
        collector.REASON_COLLECTION_SOURCE_BUNDLE_VALIDATION_FAILED
        in result.collection_errors
    )
    _assert_collection_contract_pass(result)
    plain = collector.airline_crypto_artifact_seal_collection_result_to_plain_dict_v01(
        result,
    )
    assert plain["source_package_ref"] == ""
