from __future__ import annotations

import ast
import inspect
import math
from copy import deepcopy
from dataclasses import dataclass, replace
from enum import Enum
from types import MappingProxyType

import pytest

from hedgehog.domains.airline import crypto_artifact_seal_v01 as seal
from hedgehog.domains.airline import transaction_artifact_ledger_v01 as ledger
from tests import test_airline_transaction_artifact_ledger_collector_v01 as collector_helpers


MODULE_PATH = "hedgehog/domains/airline/crypto_artifact_seal_v01.py"


def _valid_a() -> ledger.AirlineTransactionArtifactLedgerV01:
    return ledger.build_valid_airline_transaction_artifact_ledger_offer_a_v01()


def _valid_b() -> ledger.AirlineTransactionArtifactLedgerV01:
    return ledger.build_valid_airline_transaction_artifact_ledger_offer_b_v01()


def _replace_entry(
    item: ledger.AirlineTransactionArtifactLedgerV01,
    index: int,
    **changes: object,
) -> ledger.AirlineTransactionArtifactLedgerV01:
    entries = list(item.entries)
    entries[index] = replace(entries[index], **changes)
    return replace(item, entries=tuple(entries))


def _source_rows() -> tuple[tuple[str, bytes], ...]:
    return tuple(
        (ref, f"slice-b1-source:{ref}".encode("utf-8"))
        for ref in seal.REQUIRED_SOURCE_FILE_REFS
    )


def _manifest_source_package_ref() -> str:
    return "airline_crypto_b2a_source_package"


def _valid_manifest_core(
    item: ledger.AirlineTransactionArtifactLedgerV01 | None = None,
    *,
    ordered_source_files: tuple[tuple[str, bytes], ...] | None = None,
    expected_identity: (
        ledger.AirlineTransactionArtifactLedgerExpectedIdentityV01 | None
    ) = None,
) -> seal.AirlineCryptoArtifactSealManifestCoreV01:
    return seal.build_airline_crypto_artifact_seal_manifest_core_v01(
        item or _valid_a(),
        ordered_source_files=ordered_source_files or _source_rows(),
        source_package_ref=_manifest_source_package_ref(),
        source_audit_status=seal.STATUS_PASS,
        secret_scan_passed=True,
        expected_identity=expected_identity,
    )


def _valid_envelope() -> seal.AirlineCryptoArtifactSealEnvelopeV01:
    return seal.build_airline_crypto_artifact_seal_envelope_v01(
        _valid_manifest_core(),
    )


def _valid_verification(
    item: ledger.AirlineTransactionArtifactLedgerV01 | None = None,
    *,
    envelope: seal.AirlineCryptoArtifactSealEnvelopeV01 | None = None,
    rows_before: tuple[tuple[str, bytes], ...] | None = None,
    rows_after: tuple[tuple[str, bytes], ...] | None = None,
    expected_source_package_ref: object | None = None,
    expected_manifest_core_hash: object | None = None,
    expected_identity: (
        ledger.AirlineTransactionArtifactLedgerExpectedIdentityV01 | None
    ) = None,
) -> seal.AirlineCryptoArtifactSealVerificationReportV01:
    ledger_item = item or _valid_a()
    rows = rows_before or _source_rows()
    env = envelope or seal.build_airline_crypto_artifact_seal_envelope_v01(
        _valid_manifest_core(
            ledger_item,
            ordered_source_files=rows,
            expected_identity=expected_identity,
        ),
    )
    return seal.verify_airline_crypto_artifact_seal_v01(
        env,
        ledger_item=ledger_item,
        ordered_source_files_before=rows,
        ordered_source_files_after=rows_after or rows,
        expected_source_package_ref=(
            expected_source_package_ref
            if expected_source_package_ref is not None
            else _manifest_source_package_ref()
        ),
        source_audit_status=seal.STATUS_PASS,
        secret_scan_passed=True,
        expected_manifest_core_hash=expected_manifest_core_hash,
        expected_identity=expected_identity,
    )


def _valid_anchor_for(
    item: ledger.AirlineTransactionArtifactLedgerV01 | None = None,
    *,
    rows: tuple[tuple[str, bytes], ...] | None = None,
    expected_identity: (
        ledger.AirlineTransactionArtifactLedgerExpectedIdentityV01 | None
    ) = None,
) -> str:
    core = _valid_manifest_core(
        item or _valid_a(),
        ordered_source_files=rows or _source_rows(),
        expected_identity=expected_identity,
    )
    return seal.hash_airline_crypto_artifact_seal_manifest_core_v01(core)


def _assert_report_status(
    report: seal.AirlineCryptoArtifactSealVerificationReportV01,
    status: str,
) -> None:
    assert report.verification_status == status
    assert (
        seal.validate_airline_crypto_artifact_seal_verification_report_v01(
            report,
        ).validation_status
        == seal.STATUS_PASS
    )


def _assert_manifest_invalid(
    core: object,
    reason: str,
) -> None:
    report = seal.validate_airline_crypto_artifact_seal_manifest_core_v01(core)
    assert report.validation_status == seal.STATUS_FAIL_CLOSED
    assert reason in report.validation_errors


def _assert_envelope_invalid(
    envelope: object,
    reason: str,
) -> None:
    report = seal.validate_airline_crypto_artifact_seal_envelope_contract_v01(
        envelope,
    )
    assert report.validation_status == seal.STATUS_FAIL_CLOSED
    assert reason in report.validation_errors


def _assert_invalid_value(value: object, reason: str) -> None:
    report = seal.validate_airline_crypto_canonical_json_value_v01(value)
    assert report.validation_status == seal.STATUS_FAIL_CLOSED
    assert reason in report.validation_errors
    with pytest.raises(ValueError, match=reason):
        seal.canonical_airline_crypto_json_bytes_v01(value)


def _assert_build_chain_fails(
    item: ledger.AirlineTransactionArtifactLedgerV01,
    reason: str,
    *,
    expected_identity: (
        ledger.AirlineTransactionArtifactLedgerExpectedIdentityV01 | None
    ) = None,
) -> None:
    with pytest.raises(ValueError, match=reason):
        seal.build_airline_crypto_ledger_hash_chain_v01(
            item,
            expected_identity=expected_identity,
        )


def _mutable_json(value: object) -> object:
    if isinstance(value, MappingProxyType) or hasattr(value, "items"):
        return {key: _mutable_json(item) for key, item in value.items()}  # type: ignore[attr-defined]
    if type(value) is tuple:
        return tuple(_mutable_json(item) for item in value)
    if type(value) is list:
        return [_mutable_json(item) for item in value]
    return value


def _with_source_refs(
    item: ledger.AirlineTransactionArtifactLedgerV01,
    source_refs: ledger.AirlineTransactionArtifactLedgerExpectedSourceRefsV01,
) -> ledger.AirlineTransactionArtifactLedgerV01:
    entries = list(item.entries)
    transaction_entry = entries[0]
    canonical = _mutable_json(transaction_entry.canonical_hash_input)
    assert isinstance(canonical, dict)
    canonical["source_run_ref"] = source_refs.source_run_ref
    canonical["source_causal_report_ref"] = source_refs.source_causal_report_ref
    canonical["source_corridor_report_ref"] = source_refs.source_corridor_report_ref
    snapshot = canonical["source_snapshot"]
    assert isinstance(snapshot, dict)
    snapshot["source_run_ref"] = source_refs.source_run_ref
    snapshot["source_causal_report_ref"] = source_refs.source_causal_report_ref
    snapshot["source_corridor_report_ref"] = source_refs.source_corridor_report_ref
    entries[0] = replace(transaction_entry, canonical_hash_input=canonical)
    return replace(
        item,
        source_run_ref=source_refs.source_run_ref,
        source_causal_report_ref=source_refs.source_causal_report_ref,
        source_corridor_report_ref=source_refs.source_corridor_report_ref,
        entries=tuple(entries),
    )


def _expected_identity_for_source_refs(
    source_refs: ledger.AirlineTransactionArtifactLedgerExpectedSourceRefsV01,
) -> ledger.AirlineTransactionArtifactLedgerExpectedIdentityV01:
    return ledger.build_airline_transaction_artifact_ledger_fixture_expected_identity_v01(
        offer_id=ledger.OFFER_A_ID,
        expected_source_refs=source_refs,
    )


def _projection_with_plain_input(
    projection: seal.AirlineCryptoLedgerEntrySealProjectionV01,
) -> tuple[seal.AirlineCryptoLedgerEntrySealProjectionV01, dict[str, object]]:
    plain = seal.airline_crypto_ledger_entry_projection_to_plain_dict_v01(
        projection,
    )
    canonical = plain["canonical_hash_input"]
    assert isinstance(canonical, dict)
    return projection, canonical


def _unsafe_projection_with_canonical_input(
    projection: seal.AirlineCryptoLedgerEntrySealProjectionV01,
    canonical_hash_input: object,
) -> seal.AirlineCryptoLedgerEntrySealProjectionV01:
    new_projection = object.__new__(seal.AirlineCryptoLedgerEntrySealProjectionV01)
    for field_name in (
        "canonicalization_profile_id",
        "ledger_id",
        "transaction_id",
        "ledger_index",
        "event_type",
        "artifact_type",
        "artifact_id",
        "root_owner",
        "created_by",
        "authority_class",
        "evidence_class",
        "depends_on",
    ):
        object.__setattr__(new_projection, field_name, getattr(projection, field_name))
    object.__setattr__(new_projection, "canonical_hash_input", canonical_hash_input)
    return new_projection


def test_canonical_bytes_are_deterministic_for_same_value() -> None:
    value = {"z": [3, 2, 1], "a": {"text": "Paris"}}
    first = seal.canonical_airline_crypto_json_bytes_v01(value)
    assert first == seal.canonical_airline_crypto_json_bytes_v01(value)
    assert first == seal.canonical_airline_crypto_json_bytes_v01(deepcopy(value))


def test_dictionary_insertion_order_does_not_change_canonical_bytes() -> None:
    assert seal.canonical_airline_crypto_json_bytes_v01({"b": 2, "a": 1}) == (
        seal.canonical_airline_crypto_json_bytes_v01({"a": 1, "b": 2})
    )


def test_list_order_remains_significant() -> None:
    assert seal.canonical_airline_crypto_json_bytes_v01({"a": [1, 2]}) != (
        seal.canonical_airline_crypto_json_bytes_v01({"a": [2, 1]})
    )


def test_utf8_non_ascii_text_is_not_ascii_escaped() -> None:
    payload = seal.canonical_airline_crypto_json_bytes_v01({"city": "Tiranë"})
    assert "Tiranë".encode("utf-8") in payload
    assert b"\\u" not in payload


def test_canonical_bytes_have_no_bom_or_trailing_newline() -> None:
    payload = seal.canonical_airline_crypto_json_bytes_v01({"a": 1})
    assert not payload.startswith(b"\xef\xbb\xbf")
    assert not payload.endswith(b"\n")


def test_canonical_bytes_use_exact_compact_separators() -> None:
    assert seal.canonical_airline_crypto_json_bytes_v01(
        {"b": [True, None], "a": 1},
    ) == b'{"a":1,"b":[true,null]}'


def test_bool_remains_distinct_from_integer() -> None:
    assert seal.canonical_airline_crypto_json_bytes_v01({"x": True}) != (
        seal.canonical_airline_crypto_json_bytes_v01({"x": 1})
    )


@pytest.mark.parametrize(
    "value",
    (seal.SIGNED_INT64_MIN, seal.SIGNED_INT64_MAX),
)
def test_signed_64_bit_min_and_max_are_accepted(value: int) -> None:
    assert (
        seal.validate_airline_crypto_canonical_json_value_v01(value).validation_status
        == seal.STATUS_PASS
    )


@pytest.mark.parametrize(
    "value",
    (seal.SIGNED_INT64_MIN - 1, seal.SIGNED_INT64_MAX + 1),
)
def test_signed_64_bit_overflow_is_rejected(value: int) -> None:
    _assert_invalid_value(value, seal.REASON_INTEGER_OUT_OF_RANGE)


@pytest.mark.parametrize("value", (1.25, math.nan, math.inf, -math.inf))
def test_floats_nan_and_infinity_are_rejected(value: float) -> None:
    _assert_invalid_value(value, seal.REASON_FLOAT_FORBIDDEN)


def test_non_string_dict_key_is_rejected() -> None:
    _assert_invalid_value({1: "value"}, seal.REASON_NON_STRING_KEY)


def test_tuple_is_rejected_by_generic_canonicalizer() -> None:
    _assert_invalid_value(("a",), seal.REASON_TUPLE_FORBIDDEN)


def test_mapping_proxy_is_rejected_by_generic_canonicalizer() -> None:
    _assert_invalid_value(MappingProxyType({"a": 1}), seal.REASON_MAPPING_PROXY_FORBIDDEN)


@dataclass(frozen=True)
class _ExampleDataclass:
    value: int


def test_dataclass_is_rejected() -> None:
    _assert_invalid_value(_ExampleDataclass(1), seal.REASON_DATACLASS_FORBIDDEN)


class _ExampleEnum(Enum):
    VALUE = "value"


def test_enum_is_rejected() -> None:
    _assert_invalid_value(_ExampleEnum.VALUE, seal.REASON_ENUM_FORBIDDEN)


@pytest.mark.parametrize("value", (b"abc", bytearray(b"abc")))
def test_bytes_and_bytearray_are_rejected(value: object) -> None:
    _assert_invalid_value(value, seal.REASON_BYTES_FORBIDDEN)


@pytest.mark.parametrize("value", ({"a"}, frozenset({"a"})))
def test_sets_are_rejected(value: object) -> None:
    _assert_invalid_value(value, seal.REASON_SET_FORBIDDEN)


def test_arbitrary_object_is_rejected_without_str_or_repr_fallback() -> None:
    value = object()
    report = seal.validate_airline_crypto_canonical_json_value_v01(value)
    assert report.validation_errors == (seal.REASON_ARBITRARY_OBJECT_FORBIDDEN,)
    with pytest.raises(ValueError) as exc:
        seal.canonical_airline_crypto_json_bytes_v01(value)
    assert "object at" not in str(exc.value)


@pytest.mark.parametrize("value", ("\ud800", "\udc00"))
def test_lone_surrogates_are_rejected(value: str) -> None:
    _assert_invalid_value(value, seal.REASON_LONE_SURROGATE)


def test_cyclic_list_is_rejected() -> None:
    value: list[object] = []
    value.append(value)
    _assert_invalid_value(value, seal.REASON_CYCLIC_VALUE)


def test_cyclic_dict_is_rejected() -> None:
    value: dict[str, object] = {}
    value["self"] = value
    _assert_invalid_value(value, seal.REASON_CYCLIC_VALUE)


def test_canonical_validation_does_not_mutate_input() -> None:
    value = {"b": [2, {"a": "x"}]}
    before = deepcopy(value)
    seal.canonical_airline_crypto_json_bytes_v01(value)
    assert value == before


def test_validation_report_list_is_immutable_after_caller_mutation() -> None:
    errors = [seal.REASON_FLOAT_FORBIDDEN]
    report = seal.AirlineCryptoArtifactSealValidationReportV01(
        validation_status=seal.STATUS_PASS,
        validation_errors=errors,  # type: ignore[arg-type]
    )
    errors.append(seal.REASON_BYTES_FORBIDDEN)
    assert report.validation_status == seal.STATUS_FAIL_CLOSED
    assert report.validation_errors == (seal.REASON_FLOAT_FORBIDDEN,)


def test_validation_report_derives_fail_closed_from_non_empty_errors() -> None:
    report = seal.AirlineCryptoArtifactSealValidationReportV01(
        validation_status=seal.STATUS_PASS,
        validation_errors=(seal.REASON_FLOAT_FORBIDDEN,),
    )
    assert report.validation_status == seal.STATUS_FAIL_CLOSED


def test_validation_report_derives_pass_from_empty_errors() -> None:
    report = seal.AirlineCryptoArtifactSealValidationReportV01(
        validation_status=seal.STATUS_FAIL_CLOSED,
        validation_errors=(),
    )
    assert report.validation_status == seal.STATUS_PASS


def test_malformed_validation_errors_input_is_frozen_fail_closed() -> None:
    report = seal.AirlineCryptoArtifactSealValidationReportV01(
        validation_status=seal.STATUS_PASS,
        validation_errors="not-a-tuple",  # type: ignore[arg-type]
    )
    assert report.validation_status == seal.STATUS_FAIL_CLOSED
    assert report.validation_errors == (seal.REASON_MALFORMED_VALIDATION_ERRORS,)


def test_valid_utf8_json_object_bytes_are_accepted() -> None:
    parsed = seal.parse_airline_crypto_json_object_bytes_v01(b'{"b":[2],"a":"x"}')
    assert parsed == {"a": "x", "b": [2]}
    assert type(parsed) is dict
    assert type(parsed["b"]) is list


def test_malformed_utf8_is_rejected() -> None:
    with pytest.raises(ValueError, match=seal.REASON_MALFORMED_UTF8):
        seal.parse_airline_crypto_json_object_bytes_v01(b'{"x":"\xff"}')


def test_utf8_bom_is_rejected() -> None:
    with pytest.raises(ValueError, match=seal.REASON_UTF8_BOM):
        seal.parse_airline_crypto_json_object_bytes_v01(b'\xef\xbb\xbf{"a":1}')


def test_duplicate_top_level_key_is_rejected() -> None:
    with pytest.raises(ValueError, match=seal.REASON_DUPLICATE_JSON_KEY):
        seal.parse_airline_crypto_json_object_bytes_v01(b'{"a":1,"a":2}')


def test_duplicate_nested_key_is_rejected() -> None:
    with pytest.raises(ValueError, match=seal.REASON_DUPLICATE_JSON_KEY):
        seal.parse_airline_crypto_json_object_bytes_v01(b'{"a":{"b":1,"b":2}}')


@pytest.mark.parametrize("payload", (b"[1]", b'"x"', b"1", b"true", b"null"))
def test_non_object_json_roots_are_rejected(payload: bytes) -> None:
    with pytest.raises(ValueError, match=seal.REASON_EXPECTED_JSON_OBJECT):
        seal.parse_airline_crypto_json_object_bytes_v01(payload)


def test_trailing_json_data_is_rejected() -> None:
    with pytest.raises(ValueError, match=seal.REASON_MALFORMED_JSON):
        seal.parse_airline_crypto_json_object_bytes_v01(b'{"a":1}{"b":2}')


def test_malformed_json_syntax_has_stable_reason() -> None:
    with pytest.raises(ValueError, match=seal.REASON_MALFORMED_JSON):
        seal.parse_airline_crypto_json_object_bytes_v01(b"{")


@pytest.mark.parametrize("payload", (b'{"a":NaN}', b'{"a":Infinity}'))
def test_json_nan_and_infinity_are_rejected(payload: bytes) -> None:
    with pytest.raises(ValueError, match=seal.REASON_JSON_CONSTANT_FORBIDDEN):
        seal.parse_airline_crypto_json_object_bytes_v01(payload)


def test_sha256_empty_byte_known_vector_matches_standard_digest() -> None:
    assert seal.sha256_hex_v01(b"") == (
        "e3b0c44298fc1c149afbf4c8996fb924"
        "27ae41e4649b934ca495991b7852b855"
    )


def test_sha256_output_is_64_lowercase_hex() -> None:
    digest = seal.sha256_hex_v01(b"abc")
    assert len(digest) == 64
    assert digest == digest.lower()
    assert (
        seal.validate_sha256_hex_v01(digest).validation_status
        == seal.STATUS_PASS
    )


@pytest.mark.parametrize(
    "value",
    (
        "A" * 64,
        "g" * 64,
        "0" * 63,
        "0" * 65,
        "",
        None,
    ),
)
def test_malformed_sha256_digest_is_rejected(value: object) -> None:
    report = seal.validate_sha256_hex_v01(value)
    assert report.validation_status == seal.STATUS_FAIL_CLOSED
    assert seal.REASON_INVALID_SHA256_HEX in report.validation_errors


@pytest.mark.parametrize("value", ("abc", bytearray(b"abc")))
def test_sha256_input_must_be_exact_bytes(value: object) -> None:
    with pytest.raises(ValueError, match=seal.REASON_EXPECTED_BYTES):
        seal.sha256_hex_v01(value)  # type: ignore[arg-type]


def test_no_custom_algorithm_hmac_key_or_salt_parameters_exist() -> None:
    parameters = tuple(inspect.signature(seal.sha256_hex_v01).parameters)
    assert parameters == ("exact_bytes",)


@pytest.mark.parametrize("builder", (_valid_a, _valid_b))
def test_offer_ledgers_produce_19_projections_and_valid_chain(builder) -> None:
    item = builder()
    projections = seal.build_airline_crypto_ledger_entry_projections_v01(item)
    chain = seal.build_airline_crypto_ledger_hash_chain_v01(item)
    assert len(projections) == 19
    assert chain.artifact_count == 19
    assert len(chain.artifact_refs) == 19
    assert len(chain.artifact_hashes) == 19
    assert len(chain.chain_links) == 19


def test_fixture_offer_a_passes_with_expected_identity_omitted() -> None:
    projections = seal.build_airline_crypto_ledger_entry_projections_v01(_valid_a())
    chain = seal.build_airline_crypto_ledger_hash_chain_v01(_valid_a())
    assert len(projections) == 19
    assert chain.artifact_count == 19


def test_fixture_offer_b_passes_with_expected_identity_omitted() -> None:
    projections = seal.build_airline_crypto_ledger_entry_projections_v01(_valid_b())
    chain = seal.build_airline_crypto_ledger_hash_chain_v01(_valid_b())
    assert len(projections) == 19
    assert chain.artifact_count == 19


def test_changed_source_refs_require_matching_independent_expected_identity() -> None:
    source_refs = ledger.AirlineTransactionArtifactLedgerExpectedSourceRefsV01(
        source_run_ref="source_run:crypto_b1_custom",
        source_causal_report_ref="source_causal_report:crypto_b1_custom",
        source_corridor_report_ref="source_corridor_report:crypto_b1_custom",
    )
    item = _with_source_refs(_valid_a(), source_refs)
    matching_identity = _expected_identity_for_source_refs(source_refs)
    _assert_build_chain_fails(item, seal.REASON_LEDGER_VALIDATION_FAILED)
    projections = seal.build_airline_crypto_ledger_entry_projections_v01(
        item,
        expected_identity=matching_identity,
    )
    chain = seal.build_airline_crypto_ledger_hash_chain_v01(
        item,
        expected_identity=matching_identity,
    )
    assert len(projections) == 19
    assert chain.artifact_count == 19


def test_wrong_expected_identity_fails_closed() -> None:
    wrong_identity = ledger.build_airline_transaction_artifact_ledger_fixture_expected_identity_v01(
        offer_id=ledger.OFFER_B_ID,
    )
    _assert_build_chain_fails(
        _valid_a(),
        seal.REASON_LEDGER_VALIDATION_FAILED,
        expected_identity=wrong_identity,
    )


def test_wrong_expected_identity_type_fails_closed() -> None:
    with pytest.raises(ValueError, match=seal.REASON_EXPECTED_IDENTITY_WRONG_TYPE):
        seal.build_airline_crypto_ledger_hash_chain_v01(
            _valid_a(),
            expected_identity=object(),  # type: ignore[arg-type]
        )


def test_actual_public_causal_runtime_semantic_causal_hold_lineage_passes_b1() -> None:
    source_bundle = collector_helpers._source_bundle_from_public_causal_runtime(
        ledger.OFFER_A_ID,
    )
    source_identity = collector_helpers._expected_identity(source_bundle)
    item = collector_helpers._assert_collected_pass(source_bundle)
    assert item.validation_status == ledger.STATUS_PASS
    hold_entry = next(
        entry
        for entry in item.entries
        if entry.artifact_type == ledger.ARTIFACT_AIRLINE_HOLD_PACKET
    )
    assert hold_entry.artifact_id.startswith(
        "airline_hold_commit_packet:semantic_causal:",
    )
    assert hold_entry.canonical_hash_input["hold_id"].startswith(
        "hold:semantic_causal:",
    )
    projections = seal.build_airline_crypto_ledger_entry_projections_v01(
        item,
        expected_identity=source_identity,
    )
    chain = seal.build_airline_crypto_ledger_hash_chain_v01(
        item,
        expected_identity=source_identity,
    )
    hold_projection = next(
        projection
        for projection in projections
        if projection.artifact_type == ledger.ARTIFACT_AIRLINE_HOLD_PACKET
    )
    assert hold_projection.artifact_id == hold_entry.artifact_id
    assert hold_projection.canonical_hash_input["hold_id"] == (
        hold_entry.canonical_hash_input["hold_id"]
    )
    assert len(projections) == 19
    assert chain.artifact_count == 19


def test_actual_ledger_geometry_remains_19_29_3() -> None:
    item = _valid_a()
    report = ledger.validate_airline_transaction_artifact_ledger_v01(item)
    assert report.entry_count == 19
    assert report.dependency_edge_count == 29
    assert report.root_final_count == 3
    chain = seal.build_airline_crypto_ledger_hash_chain_v01(item)
    assert chain.artifact_count == 19


def test_exact_artifact_sequence_is_preserved_in_projections() -> None:
    projections = seal.build_airline_crypto_ledger_entry_projections_v01(_valid_a())
    assert tuple(p.artifact_type for p in projections) == ledger.EXPECTED_ARTIFACT_TYPE_SEQUENCE


def test_artifact_refs_hashes_and_indexes_are_positionally_bound() -> None:
    item = _valid_a()
    chain = seal.build_airline_crypto_ledger_hash_chain_v01(item)
    for index, link in enumerate(chain.chain_links):
        assert link.ledger_index == index
        assert link.artifact_ref == item.entries[index].artifact_id
        assert chain.artifact_refs[index] == link.artifact_ref
        assert chain.artifact_hashes[index] == link.artifact_hash


def test_chain_head_and_tail_bind_first_and_last_links() -> None:
    chain = seal.build_airline_crypto_ledger_hash_chain_v01(_valid_a())
    assert chain.chain_head_hash == chain.chain_links[0].chain_hash
    assert chain.chain_tail_hash == chain.chain_links[18].chain_hash


def test_changed_projection_field_changes_artifact_hash_and_downstream_link() -> None:
    projection = seal.build_airline_crypto_ledger_entry_projections_v01(_valid_a())[5]
    _, canonical = _projection_with_plain_input(projection)
    canonical["event_type"] = "changed_event_type"
    changed_projection = replace(
        projection,
        event_type="changed_event_type",
        canonical_hash_input=canonical,
    )
    original_hash = seal.hash_airline_crypto_ledger_entry_projection_v01(projection)
    changed_hash = seal.hash_airline_crypto_ledger_entry_projection_v01(changed_projection)
    assert changed_hash.artifact_hash != original_hash.artifact_hash
    chain = seal.build_airline_crypto_ledger_hash_chain_v01(_valid_a())
    changed_link_5 = seal.sha256_hex_v01(
        seal.canonical_airline_crypto_json_bytes_v01(
            {
                "domain": seal.DOMAIN_CHAIN_LINK,
                "ledger_index": 5,
                "previous_chain_hash": chain.chain_links[4].chain_hash,
                "artifact_hash": changed_hash.artifact_hash,
            },
        ),
    )
    assert changed_link_5 != chain.chain_links[5].chain_hash


def test_invalid_projection_wrong_canonicalization_profile_rejected_before_hashing() -> None:
    projection = seal.build_airline_crypto_ledger_entry_projections_v01(_valid_a())[0]
    invalid = replace(projection, canonicalization_profile_id="wrong")
    report = seal.validate_airline_crypto_ledger_entry_projection_v01(invalid)
    assert report.validation_status == seal.STATUS_FAIL_CLOSED
    assert seal.REASON_PROJECTION_CANONICALIZATION_PROFILE_MISMATCH in (
        report.validation_errors
    )
    with pytest.raises(
        ValueError,
        match=seal.REASON_PROJECTION_CANONICALIZATION_PROFILE_MISMATCH,
    ):
        seal.hash_airline_crypto_ledger_entry_projection_v01(invalid)


def test_invalid_projection_bool_ledger_index_rejected_before_hashing() -> None:
    projection = seal.build_airline_crypto_ledger_entry_projections_v01(_valid_a())[0]
    invalid = replace(projection, ledger_index=True)  # type: ignore[arg-type]
    report = seal.validate_airline_crypto_ledger_entry_projection_v01(invalid)
    assert seal.REASON_PROJECTION_LEDGER_INDEX_MISMATCH in report.validation_errors


def test_invalid_projection_out_of_range_ledger_index_rejected_before_hashing() -> None:
    projection = seal.build_airline_crypto_ledger_entry_projections_v01(_valid_a())[0]
    invalid = replace(projection, ledger_index=19)
    report = seal.validate_airline_crypto_ledger_entry_projection_v01(invalid)
    assert seal.REASON_PROJECTION_LEDGER_INDEX_MISMATCH in report.validation_errors


def test_invalid_projection_empty_artifact_id_rejected_before_hashing() -> None:
    projection = seal.build_airline_crypto_ledger_entry_projections_v01(_valid_a())[0]
    _, canonical = _projection_with_plain_input(projection)
    canonical["artifact_id"] = ""
    invalid = replace(projection, artifact_id="", canonical_hash_input=canonical)
    report = seal.validate_airline_crypto_ledger_entry_projection_v01(invalid)
    assert seal.REASON_PROJECTION_EMPTY_STRING_FIELD in report.validation_errors


def test_invalid_projection_canonical_envelope_mismatch_rejected() -> None:
    projection = seal.build_airline_crypto_ledger_entry_projections_v01(_valid_a())[0]
    _, canonical = _projection_with_plain_input(projection)
    canonical["artifact_id"] = "different"
    invalid = replace(projection, canonical_hash_input=canonical)
    report = seal.validate_airline_crypto_ledger_entry_projection_v01(invalid)
    assert seal.REASON_PROJECTION_CANONICAL_HASH_INPUT_FIELD_MISMATCH in (
        report.validation_errors
    )
    with pytest.raises(
        ValueError,
        match=seal.REASON_PROJECTION_CANONICAL_HASH_INPUT_FIELD_MISMATCH,
    ):
        seal.hash_airline_crypto_ledger_entry_projection_v01(invalid)


class _SimpleCustomMapping(dict):
    pass


def test_invalid_projection_custom_mapping_canonical_hash_input_rejected() -> None:
    projection = seal.build_airline_crypto_ledger_entry_projections_v01(_valid_a())[0]
    invalid = _unsafe_projection_with_canonical_input(
        projection,
        _SimpleCustomMapping({"artifact_id": projection.artifact_id}),
    )
    report = seal.validate_airline_crypto_ledger_entry_projection_v01(invalid)
    assert seal.REASON_PROJECTION_CANONICAL_HASH_INPUT_MALFORMED in (
        report.validation_errors
    )


def test_invalid_projection_cyclic_canonical_hash_input_rejected() -> None:
    projection = seal.build_airline_crypto_ledger_entry_projections_v01(_valid_a())[0]
    cyclic: dict[str, object] = {}
    cyclic["self"] = cyclic
    invalid = _unsafe_projection_with_canonical_input(projection, cyclic)
    report = seal.validate_airline_crypto_ledger_entry_projection_v01(invalid)
    assert seal.REASON_CYCLIC_VALUE in report.validation_errors


def test_deleted_entry_is_rejected() -> None:
    item = _valid_a()
    _assert_build_chain_fails(
        replace(item, entries=item.entries[:-1]),
        seal.REASON_LEDGER_VALIDATION_FAILED,
    )


def test_duplicated_entry_is_rejected() -> None:
    item = _valid_a()
    entries = list(item.entries)
    entries[18] = entries[17]
    _assert_build_chain_fails(
        replace(item, entries=tuple(entries)),
        seal.REASON_LEDGER_VALIDATION_FAILED,
    )


def test_reordered_entries_are_rejected() -> None:
    item = _valid_a()
    entries = list(item.entries)
    entries[1], entries[2] = entries[2], entries[1]
    _assert_build_chain_fails(
        replace(item, entries=tuple(entries)),
        seal.REASON_LEDGER_VALIDATION_FAILED,
    )


def test_wrong_transaction_is_rejected() -> None:
    _assert_build_chain_fails(
        _replace_entry(_valid_a(), 6, transaction_id="other"),
        seal.REASON_LEDGER_VALIDATION_FAILED,
    )


def test_wrong_dependency_is_rejected_by_committed_ledger_validation() -> None:
    _assert_build_chain_fails(
        _replace_entry(_valid_a(), 5, depends_on=("missing:artifact",)),
        seal.REASON_LEDGER_VALIDATION_FAILED,
    )


def test_wrong_root_owner_is_rejected_by_committed_ledger_validation() -> None:
    _assert_build_chain_fails(
        _replace_entry(_valid_a(), 11, root_owner=ledger.AIRLINE_ROOT_ID),
        seal.REASON_LEDGER_VALIDATION_FAILED,
    )


def test_receipt_as_permission_is_rejected() -> None:
    _assert_build_chain_fails(
        _replace_entry(_valid_a(), 14, authority_class="receipt_permission"),
        seal.REASON_LEDGER_VALIDATION_FAILED,
    )


def test_failed_ledger_status_is_rejected() -> None:
    _assert_build_chain_fails(
        replace(_valid_a(), validation_status=ledger.STATUS_FAIL_CLOSED),
        seal.REASON_LEDGER_VALIDATION_FAILED,
    )


def test_stored_count_lie_is_rejected_by_actual_recomputation() -> None:
    _assert_build_chain_fails(
        replace(_valid_a(), entry_count=999),
        seal.REASON_LEDGER_VALIDATION_FAILED,
    )


@pytest.mark.parametrize(
    "changes",
    (
        {"depends_on": None},
        {"transaction_id": ["not", "a", "string"]},
        {"artifact_id": {"not": "a string"}},
    ),
)
def test_malformed_ledger_values_fail_closed_without_raw_type_errors(
    changes: dict[str, object],
) -> None:
    item = _replace_entry(_valid_a(), 5, **changes)
    with pytest.raises(ValueError, match=seal.REASON_LEDGER_VALIDATION_FAILED):
        seal.build_airline_crypto_ledger_hash_chain_v01(item)


def test_source_ledger_is_unchanged_after_projection_and_chain() -> None:
    item = _valid_a()
    before = deepcopy(item)
    seal.build_airline_crypto_ledger_entry_projections_v01(item)
    seal.build_airline_crypto_ledger_hash_chain_v01(item)
    assert item == before


def test_projections_and_chain_are_deeply_immutable() -> None:
    projection = seal.build_airline_crypto_ledger_entry_projections_v01(_valid_a())[0]
    chain = seal.build_airline_crypto_ledger_hash_chain_v01(_valid_a())
    with pytest.raises(Exception):
        projection.canonical_hash_input["x"] = "y"  # type: ignore[index]
    with pytest.raises(Exception):
        projection.depends_on += ("x",)  # type: ignore[misc]
    with pytest.raises(Exception):
        chain.chain_links += (chain.chain_links[0],)  # type: ignore[misc]


def test_offer_a_b_a_chain_isolated() -> None:
    first = seal.build_airline_crypto_ledger_hash_chain_v01(_valid_a())
    middle = seal.build_airline_crypto_ledger_hash_chain_v01(_valid_b())
    last = seal.build_airline_crypto_ledger_hash_chain_v01(_valid_a())
    assert first == last
    assert first.chain_tail_hash != middle.chain_tail_hash


def test_offer_b_a_b_chain_isolated() -> None:
    first = seal.build_airline_crypto_ledger_hash_chain_v01(_valid_b())
    middle = seal.build_airline_crypto_ledger_hash_chain_v01(_valid_a())
    last = seal.build_airline_crypto_ledger_hash_chain_v01(_valid_b())
    assert first == last
    assert first.chain_tail_hash != middle.chain_tail_hash


def test_exact_nine_file_ordered_source_package_input_passes() -> None:
    index = seal.build_airline_crypto_source_package_index_v01(
        transaction_id=ledger.TRANSACTION_ID,
        ordered_source_files=_source_rows(),
    )
    assert index.source_file_count == 9
    assert index.ordered_source_file_refs == seal.REQUIRED_SOURCE_FILE_REFS
    assert len(index.ordered_source_file_hashes) == 9


def test_source_hashes_remain_positionally_paired() -> None:
    index = seal.build_airline_crypto_source_package_index_v01(
        transaction_id=ledger.TRANSACTION_ID,
        ordered_source_files=_source_rows(),
    )
    for position, record in enumerate(index.source_file_hash_records):
        assert record.relative_ref == index.ordered_source_file_refs[position]
        assert record.sha256 == index.ordered_source_file_hashes[position]


def test_ledger_document_byte_hash_equals_ledger_file_record() -> None:
    index = seal.build_airline_crypto_source_package_index_v01(
        transaction_id=ledger.TRANSACTION_ID,
        ordered_source_files=_source_rows(),
    )
    assert index.ledger_document_byte_hash == index.source_file_hash_records[0].sha256
    assert index.source_file_hash_records[0].relative_ref == (
        "airline_transaction_artifact_ledger.json"
    )


def test_changed_one_source_byte_changes_only_its_file_hash_and_package_hash() -> None:
    rows = _source_rows()
    baseline = seal.build_airline_crypto_source_package_index_v01(
        transaction_id=ledger.TRANSACTION_ID,
        ordered_source_files=rows,
    )
    changed_rows = list(rows)
    changed_rows[3] = (changed_rows[3][0], changed_rows[3][1] + b"x")
    changed = seal.build_airline_crypto_source_package_index_v01(
        transaction_id=ledger.TRANSACTION_ID,
        ordered_source_files=tuple(changed_rows),
    )
    changed_positions = [
        index
        for index, (left, right) in enumerate(
            zip(baseline.ordered_source_file_hashes, changed.ordered_source_file_hashes),
        )
        if left != right
    ]
    assert changed_positions == [3]
    assert changed.source_package_hash != baseline.source_package_hash


def test_missing_source_file_row_is_rejected() -> None:
    with pytest.raises(ValueError, match=seal.REASON_SOURCE_PACKAGE_FILE_COUNT):
        seal.build_airline_crypto_source_package_index_v01(
            transaction_id=ledger.TRANSACTION_ID,
            ordered_source_files=_source_rows()[:-1],
        )


def test_extra_source_file_row_is_rejected() -> None:
    with pytest.raises(ValueError, match=seal.REASON_SOURCE_PACKAGE_FILE_COUNT):
        seal.build_airline_crypto_source_package_index_v01(
            transaction_id=ledger.TRANSACTION_ID,
            ordered_source_files=_source_rows() + (("extra.json", b"x"),),
        )


def test_reordered_source_file_rows_are_rejected() -> None:
    rows = list(_source_rows())
    rows[0], rows[1] = rows[1], rows[0]
    with pytest.raises(ValueError, match=seal.REASON_SOURCE_PACKAGE_FILE_ORDER):
        seal.build_airline_crypto_source_package_index_v01(
            transaction_id=ledger.TRANSACTION_ID,
            ordered_source_files=tuple(rows),
        )


def test_duplicate_source_file_ref_is_rejected() -> None:
    rows = list(_source_rows())
    rows[1] = (rows[0][0], rows[1][1])
    with pytest.raises(ValueError, match=seal.REASON_SOURCE_PACKAGE_FILE_ORDER):
        seal.build_airline_crypto_source_package_index_v01(
            transaction_id=ledger.TRANSACTION_ID,
            ordered_source_files=tuple(rows),
        )


def test_path_containing_source_ref_is_rejected() -> None:
    rows = list(_source_rows())
    rows[0] = ("dir/airline_transaction_artifact_ledger.json", rows[0][1])
    with pytest.raises(ValueError, match=seal.REASON_SOURCE_PACKAGE_FILE_ORDER):
        seal.build_airline_crypto_source_package_index_v01(
            transaction_id=ledger.TRANSACTION_ID,
            ordered_source_files=tuple(rows),
        )


def test_non_bytes_source_content_is_rejected() -> None:
    rows = list(_source_rows())
    rows[0] = (rows[0][0], bytearray(rows[0][1]))  # type: ignore[assignment]
    with pytest.raises(ValueError, match=seal.REASON_SOURCE_PACKAGE_CONTENT_NOT_BYTES):
        seal.build_airline_crypto_source_package_index_v01(
            transaction_id=ledger.TRANSACTION_ID,
            ordered_source_files=tuple(rows),  # type: ignore[arg-type]
        )


def test_source_input_bytes_are_unchanged() -> None:
    rows = _source_rows()
    before = tuple((ref, bytes(payload)) for ref, payload in rows)
    seal.build_airline_crypto_source_package_index_v01(
        transaction_id=ledger.TRANSACTION_ID,
        ordered_source_files=rows,
    )
    assert rows == before


def test_returned_source_package_index_is_deeply_immutable() -> None:
    index = seal.build_airline_crypto_source_package_index_v01(
        transaction_id=ledger.TRANSACTION_ID,
        ordered_source_files=_source_rows(),
    )
    with pytest.raises(Exception):
        index.ordered_source_file_refs += ("x",)  # type: ignore[misc]
    with pytest.raises(Exception):
        index.source_file_hash_records += (index.source_file_hash_records[0],)  # type: ignore[misc]


def test_source_package_ref_validator_accepts_logical_basename_only() -> None:
    assert (
        seal.validate_airline_crypto_source_package_ref_v01(
            _manifest_source_package_ref(),
        ).validation_status
        == seal.STATUS_PASS
    )


@pytest.mark.parametrize(
    "value",
    ("", ".", "..", "/tmp/package", "dir/package", "C:\\package", "C:package", "\ud800"),
)
def test_source_package_ref_validator_rejects_path_like_values(value: object) -> None:
    report = seal.validate_airline_crypto_source_package_ref_v01(value)
    assert report.validation_status == seal.STATUS_FAIL_CLOSED
    assert seal.REASON_MANIFEST_SOURCE_PACKAGE_REF_MALFORMED in report.validation_errors


@pytest.mark.parametrize("builder", (_valid_a, _valid_b))
def test_fixture_manifest_core_and_envelope_are_valid(builder) -> None:
    core = _valid_manifest_core(builder())
    envelope = seal.build_airline_crypto_artifact_seal_envelope_v01(core)
    assert (
        seal.validate_airline_crypto_artifact_seal_manifest_core_v01(
            core,
        ).validation_status
        == seal.STATUS_PASS
    )
    assert (
        seal.validate_airline_crypto_artifact_seal_envelope_contract_v01(
            envelope,
        ).validation_status
        == seal.STATUS_PASS
    )
    assert core.ledger_entry_count == 19
    assert core.dependency_edge_count == 29
    assert core.root_final_count == 3
    assert len(core.ordered_artifact_refs) == 19
    assert len(core.ordered_source_file_refs) == 9


def test_manifest_core_uses_exact_chain_and_source_index_bindings() -> None:
    item = _valid_a()
    core = _valid_manifest_core(item)
    chain = seal.build_airline_crypto_ledger_hash_chain_v01(item)
    source_index = seal.build_airline_crypto_source_package_index_v01(
        transaction_id=item.transaction_id,
        ordered_source_files=_source_rows(),
    )
    assert core.ordered_artifact_refs == chain.artifact_refs
    assert core.ordered_artifact_hashes == chain.artifact_hashes
    assert core.chain_genesis_hash == chain.chain_genesis_hash
    assert core.chain_head_hash == chain.chain_head_hash
    assert core.chain_tail_hash == chain.chain_tail_hash
    assert core.ordered_source_file_refs == source_index.ordered_source_file_refs
    assert core.ordered_source_file_hashes == source_index.ordered_source_file_hashes
    assert core.ledger_document_byte_hash == source_index.ledger_document_byte_hash


def test_manifest_core_has_deterministic_identity_and_hash() -> None:
    core = _valid_manifest_core()
    digest = seal.hash_airline_crypto_artifact_seal_manifest_core_v01(core)
    assert core.seal_id == f"{seal.SEAL_VERSION}:{core.source_package_hash}"
    assert seal.validate_sha256_hex_v01(digest).validation_status == seal.STATUS_PASS
    assert digest == seal.hash_airline_crypto_artifact_seal_manifest_core_v01(core)


def test_manifest_core_plain_dict_has_exact_fields_and_no_self_hash() -> None:
    plain = seal.airline_crypto_artifact_seal_manifest_core_to_plain_dict_v01(
        _valid_manifest_core(),
    )
    assert tuple(plain.keys()) == seal.MANIFEST_CORE_FIELD_NAMES
    assert "manifest_core_hash" not in plain
    assert "signature" not in plain


def test_unsigned_signature_placeholder_is_exact_and_not_verified() -> None:
    signature = seal.build_airline_crypto_artifact_seal_signature_placeholder_v01()
    assert signature.mode == seal.SIGNATURE_MODE_UNSIGNED_PLACEHOLDER
    assert signature.algorithm == seal.SIGNATURE_ALGORITHM_NONE
    assert signature.key_id == ""
    assert signature.value == ""
    assert signature.verified is False
    assert (
        seal.validate_airline_crypto_artifact_seal_signature_placeholder_v01(
            signature,
        ).validation_status
        == seal.STATUS_PASS
    )


def test_envelope_builder_computes_digest_and_unsigned_placeholder() -> None:
    core = _valid_manifest_core()
    envelope = seal.build_airline_crypto_artifact_seal_envelope_v01(core)
    assert envelope.manifest_core == core
    assert envelope.manifest_core_hash == (
        seal.hash_airline_crypto_artifact_seal_manifest_core_v01(core)
    )
    assert envelope.signature == (
        seal.build_airline_crypto_artifact_seal_signature_placeholder_v01()
    )


def test_actual_semantic_causal_source_manifest_core_and_envelope_pass_b2a() -> None:
    source_bundle = collector_helpers._source_bundle_from_public_causal_runtime(
        ledger.OFFER_A_ID,
    )
    source_identity = collector_helpers._expected_identity(source_bundle)
    item = collector_helpers._assert_collected_pass(source_bundle)
    hold_entry = next(
        entry
        for entry in item.entries
        if entry.artifact_type == ledger.ARTIFACT_AIRLINE_HOLD_PACKET
    )
    assert hold_entry.artifact_id.startswith(
        "airline_hold_commit_packet:semantic_causal:",
    )
    core = _valid_manifest_core(item, expected_identity=source_identity)
    envelope = seal.build_airline_crypto_artifact_seal_envelope_v01(core)
    assert len(core.ordered_artifact_refs) == 19
    assert len(core.ordered_source_file_refs) == 9
    assert hold_entry.artifact_id in core.ordered_artifact_refs
    assert core.ledger_entry_count == 19
    assert core.dependency_edge_count == 29
    assert core.root_final_count == 3
    assert (
        seal.validate_airline_crypto_artifact_seal_manifest_core_v01(
            core,
        ).validation_status
        == seal.STATUS_PASS
    )
    assert (
        seal.validate_airline_crypto_artifact_seal_envelope_contract_v01(
            envelope,
        ).validation_status
        == seal.STATUS_PASS
    )


@pytest.mark.parametrize(
    ("kwargs", "reason"),
    (
        (
            {"source_package_ref": "dir/package"},
            seal.REASON_MANIFEST_SOURCE_PACKAGE_REF_MALFORMED,
        ),
        (
            {"source_audit_status": seal.STATUS_FAIL_CLOSED},
            seal.REASON_MANIFEST_SOURCE_AUDIT_STATUS_MISMATCH,
        ),
        (
            {"secret_scan_passed": False},
            seal.REASON_MANIFEST_SECRET_SCAN_BOUNDARY_MISMATCH,
        ),
    ),
)
def test_manifest_builder_rejects_bad_policy_inputs(
    kwargs: dict[str, object],
    reason: str,
) -> None:
    params = {
        "ordered_source_files": _source_rows(),
        "source_package_ref": _manifest_source_package_ref(),
        "source_audit_status": seal.STATUS_PASS,
        "secret_scan_passed": True,
    }
    params.update(kwargs)
    with pytest.raises(ValueError, match=reason):
        seal.build_airline_crypto_artifact_seal_manifest_core_v01(
            _valid_a(),
            **params,  # type: ignore[arg-type]
        )


def test_manifest_builder_rejects_wrong_expected_identity() -> None:
    wrong_identity = ledger.build_airline_transaction_artifact_ledger_fixture_expected_identity_v01(
        offer_id=ledger.OFFER_B_ID,
    )
    with pytest.raises(ValueError, match=seal.REASON_LEDGER_VALIDATION_FAILED):
        seal.build_airline_crypto_artifact_seal_manifest_core_v01(
            _valid_a(),
            ordered_source_files=_source_rows(),
            source_package_ref=_manifest_source_package_ref(),
            source_audit_status=seal.STATUS_PASS,
            secret_scan_passed=True,
            expected_identity=wrong_identity,
        )


def test_manifest_builder_rejects_reordered_source_files() -> None:
    rows = list(_source_rows())
    rows[0], rows[1] = rows[1], rows[0]
    with pytest.raises(ValueError, match=seal.REASON_SOURCE_PACKAGE_FILE_ORDER):
        seal.build_airline_crypto_artifact_seal_manifest_core_v01(
            _valid_a(),
            ordered_source_files=tuple(rows),
            source_package_ref=_manifest_source_package_ref(),
            source_audit_status=seal.STATUS_PASS,
            secret_scan_passed=True,
        )


def test_manifest_builder_rejects_ledger_transaction_mismatch() -> None:
    with pytest.raises(ValueError, match=seal.REASON_LEDGER_VALIDATION_FAILED):
        seal.build_airline_crypto_artifact_seal_manifest_core_v01(
            replace(_valid_a(), transaction_id="other"),
            ordered_source_files=_source_rows(),
            source_package_ref=_manifest_source_package_ref(),
            source_audit_status=seal.STATUS_PASS,
            secret_scan_passed=True,
        )


@pytest.mark.parametrize(
    ("field_name", "value", "reason"),
    (
        ("seal_version", "wrong", seal.REASON_MANIFEST_VERSION_PROFILE_ALGORITHM_MISMATCH),
        (
            "canonicalization_profile_id",
            "wrong",
            seal.REASON_MANIFEST_VERSION_PROFILE_ALGORITHM_MISMATCH,
        ),
        ("hash_algorithm", "MD5", seal.REASON_MANIFEST_VERSION_PROFILE_ALGORITHM_MISMATCH),
        ("hash_encoding", "base64", seal.REASON_MANIFEST_VERSION_PROFILE_ALGORITHM_MISMATCH),
        ("ledger_entry_count", 18, seal.REASON_MANIFEST_LEDGER_GEOMETRY_MISMATCH),
        ("dependency_edge_count", 28, seal.REASON_MANIFEST_LEDGER_GEOMETRY_MISMATCH),
        ("root_final_count", 2, seal.REASON_MANIFEST_LEDGER_GEOMETRY_MISMATCH),
        ("ledger_entry_count", True, seal.REASON_MANIFEST_LEDGER_GEOMETRY_MISMATCH),
        ("source_file_count", 8, seal.REASON_MANIFEST_SOURCE_REF_HASH_GEOMETRY_MISMATCH),
        ("previous_manifest_ref", "previous", seal.REASON_MANIFEST_PREVIOUS_REF_MISMATCH),
        ("signature_placeholder_present", False, seal.REASON_MANIFEST_SIGNATURE_FLAG_MISMATCH),
        ("signature_verified", True, seal.REASON_MANIFEST_SIGNATURE_FLAG_MISMATCH),
        ("source_audit_status", seal.STATUS_FAIL_CLOSED, seal.REASON_MANIFEST_SOURCE_AUDIT_STATUS_MISMATCH),
        ("secret_scan_passed", False, seal.REASON_MANIFEST_SECRET_SCAN_BOUNDARY_MISMATCH),
        ("raw_secret_included", True, seal.REASON_MANIFEST_SECRET_SCAN_BOUNDARY_MISMATCH),
        ("seal_created_authority_count", 1, seal.REASON_MANIFEST_NONZERO_COUNTER),
        ("seal_created_permission_count", 1, seal.REASON_MANIFEST_NONZERO_COUNTER),
        ("seal_created_action_count", 1, seal.REASON_MANIFEST_NONZERO_COUNTER),
        ("real_world_effects_count", 1, seal.REASON_MANIFEST_NONZERO_COUNTER),
        ("ledger_id", "bad\ud800", seal.REASON_MANIFEST_IDENTITY_MISMATCH),
    ),
)
def test_manifest_core_scalar_field_mutations_fail(
    field_name: str,
    value: object,
    reason: str,
) -> None:
    _assert_manifest_invalid(replace(_valid_manifest_core(), **{field_name: value}), reason)


def test_manifest_core_rejects_seal_id_not_derived_from_source_package_hash() -> None:
    _assert_manifest_invalid(
        replace(_valid_manifest_core(), seal_id="caller:selected"),
        seal.REASON_MANIFEST_IDENTITY_MISMATCH,
    )


@pytest.mark.parametrize(
    ("field_name", "value", "reason"),
    (
        (
            "ordered_artifact_refs",
            ("x",) * 18,
            seal.REASON_MANIFEST_ARTIFACT_REF_HASH_GEOMETRY_MISMATCH,
        ),
        (
            "ordered_artifact_hashes",
            ("0" * 64,) * 18,
            seal.REASON_MANIFEST_ARTIFACT_REF_HASH_GEOMETRY_MISMATCH,
        ),
        (
            "ordered_artifact_refs",
            ("",) + _valid_manifest_core().ordered_artifact_refs[1:],
            seal.REASON_MANIFEST_INVALID_ARTIFACT_REF,
        ),
        (
            "ordered_artifact_hashes",
            ("not-a-digest",) + _valid_manifest_core().ordered_artifact_hashes[1:],
            seal.REASON_MANIFEST_INVALID_ARTIFACT_HASH,
        ),
        ("chain_genesis_hash", "not-a-digest", seal.REASON_MANIFEST_CHAIN_HASH_MISMATCH),
        ("chain_head_hash", "not-a-digest", seal.REASON_MANIFEST_CHAIN_HASH_MISMATCH),
        ("chain_tail_hash", "not-a-digest", seal.REASON_MANIFEST_CHAIN_HASH_MISMATCH),
        (
            "ordered_source_file_hashes",
            ("0" * 64,) * 8,
            seal.REASON_MANIFEST_SOURCE_REF_HASH_GEOMETRY_MISMATCH,
        ),
        (
            "ordered_source_file_hashes",
            ("not-a-digest",) + _valid_manifest_core().ordered_source_file_hashes[1:],
            seal.REASON_MANIFEST_INVALID_SOURCE_HASH,
        ),
    ),
)
def test_manifest_core_sequence_and_digest_mutations_fail(
    field_name: str,
    value: object,
    reason: str,
) -> None:
    _assert_manifest_invalid(replace(_valid_manifest_core(), **{field_name: value}), reason)


def test_manifest_core_rejects_duplicate_artifact_ref() -> None:
    core = _valid_manifest_core()
    refs = list(core.ordered_artifact_refs)
    refs[1] = refs[0]
    _assert_manifest_invalid(
        replace(core, ordered_artifact_refs=tuple(refs)),
        seal.REASON_MANIFEST_DUPLICATE_ARTIFACT_REF,
    )


def test_manifest_core_rejects_reordered_source_refs() -> None:
    core = _valid_manifest_core()
    refs = list(core.ordered_source_file_refs)
    refs[0], refs[1] = refs[1], refs[0]
    _assert_manifest_invalid(
        replace(core, ordered_source_file_refs=tuple(refs)),
        seal.REASON_MANIFEST_SOURCE_FILE_ORDER_MISMATCH,
    )


def test_manifest_core_rejects_duplicate_source_ref() -> None:
    core = _valid_manifest_core()
    refs = list(core.ordered_source_file_refs)
    refs[1] = refs[0]
    _assert_manifest_invalid(
        replace(core, ordered_source_file_refs=tuple(refs)),
        seal.REASON_MANIFEST_DUPLICATE_SOURCE_REF,
    )


def test_manifest_core_rejects_source_ref_hash_length_mismatch() -> None:
    core = _valid_manifest_core()
    _assert_manifest_invalid(
        replace(core, ordered_source_file_refs=core.ordered_source_file_refs[:-1]),
        seal.REASON_MANIFEST_SOURCE_REF_HASH_GEOMETRY_MISMATCH,
    )


def test_manifest_core_rejects_wrong_source_package_hash_even_with_matching_seal_id() -> None:
    changed_hash = "1" * 64
    _assert_manifest_invalid(
        replace(
            _valid_manifest_core(),
            source_package_hash=changed_hash,
            seal_id=f"{seal.SEAL_VERSION}:{changed_hash}",
        ),
        seal.REASON_MANIFEST_INVALID_SOURCE_HASH,
    )


def test_manifest_core_rejects_wrong_ledger_document_byte_hash() -> None:
    _assert_manifest_invalid(
        replace(_valid_manifest_core(), ledger_document_byte_hash="1" * 64),
        seal.REASON_MANIFEST_LEDGER_DOCUMENT_BYTE_HASH_MISMATCH,
    )


def test_manifest_core_rejects_chain_hashes_not_recomputed_from_artifact_hashes() -> None:
    _assert_manifest_invalid(
        replace(_valid_manifest_core(), chain_tail_hash="1" * 64),
        seal.REASON_MANIFEST_CHAIN_HASH_MISMATCH,
    )


def test_manifest_core_hash_changes_when_any_valid_field_changes() -> None:
    core = _valid_manifest_core()
    changed = replace(core, source_package_ref="airline_crypto_b2a_other_package")
    assert (
        seal.hash_airline_crypto_artifact_seal_manifest_core_v01(changed)
        != seal.hash_airline_crypto_artifact_seal_manifest_core_v01(core)
    )


def test_one_source_byte_change_updates_manifest_identity_and_hash_only_for_that_file() -> None:
    baseline = _valid_manifest_core()
    rows = list(_source_rows())
    rows[4] = (rows[4][0], rows[4][1] + b"x")
    changed = _valid_manifest_core(ordered_source_files=tuple(rows))
    changed_positions = [
        index
        for index, (left, right) in enumerate(
            zip(baseline.ordered_source_file_hashes, changed.ordered_source_file_hashes),
        )
        if left != right
    ]
    assert changed_positions == [4]
    assert changed.source_package_hash != baseline.source_package_hash
    assert changed.seal_id != baseline.seal_id
    assert (
        seal.hash_airline_crypto_artifact_seal_manifest_core_v01(changed)
        != seal.hash_airline_crypto_artifact_seal_manifest_core_v01(baseline)
    )


@pytest.mark.parametrize(
    ("field_name", "value"),
    (
        ("mode", "SIGNED"),
        ("algorithm", "SHA256-RSA"),
        ("key_id", "key"),
        ("value", "signature"),
        ("verified", True),
    ),
)
def test_signature_placeholder_rejects_any_non_placeholder_value(
    field_name: str,
    value: object,
) -> None:
    signature = replace(
        seal.build_airline_crypto_artifact_seal_signature_placeholder_v01(),
        **{field_name: value},
    )
    report = seal.validate_airline_crypto_artifact_seal_signature_placeholder_v01(
        signature,
    )
    assert report.validation_status == seal.STATUS_FAIL_CLOSED
    assert seal.REASON_SIGNATURE_PLACEHOLDER_FIELD_MISMATCH in report.validation_errors


def test_signature_placeholder_wrong_type_fails_closed() -> None:
    report = seal.validate_airline_crypto_artifact_seal_signature_placeholder_v01(
        object(),
    )
    assert report.validation_status == seal.STATUS_FAIL_CLOSED
    assert seal.REASON_SIGNATURE_PLACEHOLDER_WRONG_TYPE in report.validation_errors


def test_envelope_wrong_type_fails_closed() -> None:
    _assert_envelope_invalid(object(), seal.REASON_ENVELOPE_MALFORMED)


def test_envelope_rejects_malformed_stored_manifest_core_hash() -> None:
    _assert_envelope_invalid(
        replace(_valid_envelope(), manifest_core_hash="not-a-digest"),
        seal.REASON_INVALID_SHA256_HEX,
    )


def test_envelope_rejects_stored_manifest_core_hash_mismatch() -> None:
    _assert_envelope_invalid(
        replace(_valid_envelope(), manifest_core_hash="1" * 64),
        seal.REASON_MANIFEST_CORE_HASH_MISMATCH,
    )


def test_envelope_rejects_invalid_manifest_core_inside_envelope() -> None:
    envelope = _valid_envelope()
    invalid_core = replace(envelope.manifest_core, source_audit_status="FAIL_CLOSED")
    _assert_envelope_invalid(
        replace(envelope, manifest_core=invalid_core),
        seal.REASON_MANIFEST_SOURCE_AUDIT_STATUS_MISMATCH,
    )


def test_envelope_rejects_invalid_signature_placeholder_inside_envelope() -> None:
    envelope = _valid_envelope()
    invalid_signature = replace(envelope.signature, verified=True)
    _assert_envelope_invalid(
        replace(envelope, signature=invalid_signature),
        seal.REASON_SIGNATURE_PLACEHOLDER_FIELD_MISMATCH,
    )


def test_envelope_builder_accepts_no_fake_digest_or_signature_parameters() -> None:
    parameters = tuple(
        inspect.signature(
            seal.build_airline_crypto_artifact_seal_envelope_v01,
        ).parameters
    )
    assert parameters == ("manifest_core",)


def test_manifest_core_envelope_and_signature_are_deeply_immutable() -> None:
    core = _valid_manifest_core()
    envelope = seal.build_airline_crypto_artifact_seal_envelope_v01(core)
    with pytest.raises(Exception):
        core.ordered_artifact_refs += ("x",)  # type: ignore[misc]
    with pytest.raises(Exception):
        envelope.manifest_core = core  # type: ignore[misc]
    with pytest.raises(Exception):
        envelope.signature.verified = True  # type: ignore[misc]


def test_manifest_core_freezes_caller_list_inputs() -> None:
    core = _valid_manifest_core()
    artifact_refs = list(core.ordered_artifact_refs)
    custom = replace(core, ordered_artifact_refs=artifact_refs)
    artifact_refs[0] = "mutated"
    assert custom.ordered_artifact_refs[0] == core.ordered_artifact_refs[0]
    assert type(custom.ordered_artifact_refs) is tuple


def test_manifest_core_rejects_mapping_as_ordered_array_input() -> None:
    with pytest.raises(
        ValueError,
        match=seal.REASON_MANIFEST_ARTIFACT_REF_HASH_GEOMETRY_MISMATCH,
    ):
        replace(_valid_manifest_core(), ordered_artifact_refs={"a": "b"})


def test_source_ledger_and_source_byte_rows_are_unchanged_by_manifest_build() -> None:
    item = _valid_a()
    rows = _source_rows()
    before_item = deepcopy(item)
    before_rows = tuple((ref, bytes(payload)) for ref, payload in rows)
    seal.build_airline_crypto_artifact_seal_manifest_core_v01(
        item,
        ordered_source_files=rows,
        source_package_ref=_manifest_source_package_ref(),
        source_audit_status=seal.STATUS_PASS,
        secret_scan_passed=True,
    )
    assert item == before_item
    assert rows == before_rows


def test_offer_a_and_b_manifest_core_hashes_are_deterministic_and_distinct() -> None:
    a_first = _valid_manifest_core(_valid_a())
    a_second = _valid_manifest_core(_valid_a())
    b_first = _valid_manifest_core(_valid_b())
    b_second = _valid_manifest_core(_valid_b())
    assert a_first == a_second
    assert b_first == b_second
    assert a_first.chain_tail_hash != b_first.chain_tail_hash
    assert (
        seal.hash_airline_crypto_artifact_seal_manifest_core_v01(a_first)
        != seal.hash_airline_crypto_artifact_seal_manifest_core_v01(b_first)
    )


def test_manifest_core_a_b_a_and_b_a_b_isolation() -> None:
    a_first = _valid_manifest_core(_valid_a())
    b_middle = _valid_manifest_core(_valid_b())
    a_last = _valid_manifest_core(_valid_a())
    assert a_first == a_last
    assert a_first != b_middle
    b_first = _valid_manifest_core(_valid_b())
    a_middle = _valid_manifest_core(_valid_a())
    b_last = _valid_manifest_core(_valid_b())
    assert b_first == b_last
    assert b_first != a_middle


@pytest.mark.parametrize(
    ("builder", "status", "anchored"),
    (
        (_valid_a, seal.STATUS_SELF_CONSISTENT_UNANCHORED, False),
        (_valid_b, seal.STATUS_SELF_CONSISTENT_UNANCHORED, False),
        (_valid_a, seal.STATUS_PASS, True),
        (_valid_b, seal.STATUS_PASS, True),
    ),
)
def test_fixture_offer_verification_statuses(
    builder,
    status: str,
    anchored: bool,
) -> None:
    item = builder()
    anchor = _valid_anchor_for(item) if anchored else None
    report = _valid_verification(item, expected_manifest_core_hash=anchor)
    _assert_report_status(report, status)
    assert report.ledger_geometry_verified is True
    assert report.root_ownership_verified is True
    assert report.authority_evidence_boundaries_verified is True
    assert report.secret_boundary_verified is True
    assert report.signature_mode == seal.SIGNATURE_MODE_UNSIGNED_PLACEHOLDER
    assert report.signature_verified is False
    assert report.provider_call_count == 0
    assert report.network_call_count == 0
    assert report.gemini_call_count == 0
    assert report.seal_created_authority_count == 0
    assert report.seal_created_permission_count == 0
    assert report.seal_created_action_count == 0
    assert report.real_world_effects_count == 0


def test_verification_report_plain_dict_exact_field_sequence_and_json_safe() -> None:
    report = _valid_verification(
        _valid_a(),
        expected_manifest_core_hash=_valid_anchor_for(_valid_a()),
    )
    plain = seal.airline_crypto_artifact_seal_verification_report_to_plain_dict_v01(
        report,
    )
    assert tuple(plain.keys()) == seal.VERIFICATION_REPORT_FIELD_NAMES
    assert plain["verification_errors"] == []
    assert (
        seal.validate_airline_crypto_canonical_json_value_v01(plain).validation_status
        == seal.STATUS_PASS
    )


def test_repeated_verification_is_deterministic() -> None:
    first = _valid_verification(_valid_a())
    second = _valid_verification(_valid_a())
    assert first == second


def test_verification_a_b_a_and_b_a_b_isolated() -> None:
    a_first = _valid_verification(_valid_a())
    b_middle = _valid_verification(_valid_b())
    a_last = _valid_verification(_valid_a())
    assert a_first == a_last
    assert a_first.manifest_core_hash != b_middle.manifest_core_hash
    b_first = _valid_verification(_valid_b())
    a_middle = _valid_verification(_valid_a())
    b_last = _valid_verification(_valid_b())
    assert b_first == b_last
    assert b_first.manifest_core_hash != a_middle.manifest_core_hash


def test_missing_anchor_never_returns_pass() -> None:
    report = _valid_verification(_valid_a())
    assert report.verification_status == seal.STATUS_SELF_CONSISTENT_UNANCHORED
    assert report.external_anchor_supplied is False
    assert report.external_anchor_verified is False


def test_envelope_stored_manifest_hash_is_not_used_as_implicit_anchor() -> None:
    envelope = _valid_envelope()
    report = _valid_verification(_valid_a(), envelope=envelope)
    assert envelope.manifest_core_hash == report.manifest_core_hash
    assert report.verification_status == seal.STATUS_SELF_CONSISTENT_UNANCHORED
    assert report.expected_manifest_core_hash is None


@pytest.mark.parametrize("anchor", ("1" * 64, "A" * 64, "0" * 63, b"0" * 64))
def test_wrong_or_malformed_anchor_fails_closed(anchor: object) -> None:
    report = _valid_verification(_valid_a(), expected_manifest_core_hash=anchor)
    assert report.verification_status == seal.STATUS_FAIL_CLOSED
    if anchor == "1" * 64:
        assert seal.REASON_VERIFICATION_EXTERNAL_ANCHOR_MISMATCH in (
            report.verification_errors
        )
        assert report.external_anchor_supplied is True
    else:
        assert seal.REASON_VERIFICATION_EXPECTED_ANCHOR_MALFORMED in (
            report.verification_errors
        )
        assert report.external_anchor_supplied is False


def test_str_subclass_and_custom_equality_anchor_are_rejected() -> None:
    class _AlwaysEqual:
        def __eq__(self, other: object) -> bool:
            return True

    str_subclass = type("AnchorStringSubclass", (str,), {})("0" * 64)
    for anchor in (str_subclass, _AlwaysEqual()):
        report = _valid_verification(
            _valid_a(),
            expected_manifest_core_hash=anchor,
        )
        assert report.verification_status == seal.STATUS_FAIL_CLOSED
        assert seal.REASON_VERIFICATION_EXPECTED_ANCHOR_MALFORMED in (
            report.verification_errors
        )


def test_wrong_envelope_type_returns_fail_closed_report() -> None:
    report = seal.verify_airline_crypto_artifact_seal_v01(
        object(),
        ledger_item=_valid_a(),
        ordered_source_files_before=_source_rows(),
        ordered_source_files_after=_source_rows(),
        expected_source_package_ref=_manifest_source_package_ref(),
        source_audit_status=seal.STATUS_PASS,
        secret_scan_passed=True,
    )
    assert report.verification_status == seal.STATUS_FAIL_CLOSED
    assert seal.REASON_VERIFICATION_ENVELOPE_CONTRACT_FAILED in (
        report.verification_errors
    )


def test_invalid_envelope_contract_returns_fail_closed_report() -> None:
    envelope = replace(_valid_envelope(), manifest_core_hash="1" * 64)
    report = _valid_verification(_valid_a(), envelope=envelope)
    assert report.verification_status == seal.STATUS_FAIL_CLOSED
    assert seal.REASON_VERIFICATION_ENVELOPE_CONTRACT_FAILED in (
        report.verification_errors
    )


def test_envelope_source_package_ref_mismatch_fails_against_independent_ref() -> None:
    report = _valid_verification(
        _valid_a(),
        expected_source_package_ref="different_package_ref",
    )
    assert report.verification_status == seal.STATUS_FAIL_CLOSED
    assert seal.REASON_VERIFICATION_MANIFEST_CORE_MISMATCH in report.verification_errors


def test_offer_b_envelope_fails_against_offer_a_ledger() -> None:
    envelope_b = seal.build_airline_crypto_artifact_seal_envelope_v01(
        _valid_manifest_core(_valid_b()),
    )
    report = _valid_verification(_valid_a(), envelope=envelope_b)
    assert report.verification_status == seal.STATUS_FAIL_CLOSED
    assert seal.REASON_VERIFICATION_ARTIFACT_HASHES_MISMATCH in (
        report.verification_errors
    )


@pytest.mark.parametrize(
    ("field_name", "value", "reason"),
    (
        ("ordered_artifact_hashes", ("1" * 64,) + _valid_manifest_core().ordered_artifact_hashes[1:], seal.REASON_VERIFICATION_ARTIFACT_HASHES_MISMATCH),
        ("chain_genesis_hash", "1" * 64, seal.REASON_VERIFICATION_CHAIN_MISMATCH),
        ("chain_head_hash", "1" * 64, seal.REASON_VERIFICATION_CHAIN_MISMATCH),
        ("chain_tail_hash", "1" * 64, seal.REASON_VERIFICATION_CHAIN_MISMATCH),
        ("ordered_source_file_hashes", ("1" * 64,) + _valid_manifest_core().ordered_source_file_hashes[1:], seal.REASON_VERIFICATION_SOURCE_FILE_HASHES_MISMATCH),
        ("source_package_hash", "1" * 64, seal.REASON_VERIFICATION_SOURCE_PACKAGE_HASH_MISMATCH),
        ("ledger_document_byte_hash", "1" * 64, seal.REASON_VERIFICATION_LEDGER_DOCUMENT_BYTE_HASH_MISMATCH),
        ("ledger_entry_count", 18, seal.REASON_VERIFICATION_LEDGER_GEOMETRY_MISMATCH),
    ),
)
def test_independent_data_mismatch_flags_fail_closed(
    field_name: str,
    value: object,
    reason: str,
) -> None:
    core = replace(_valid_manifest_core(), **{field_name: value})
    envelope = seal.AirlineCryptoArtifactSealEnvelopeV01(
        manifest_core=core,
        manifest_core_hash=(
            seal.hash_airline_crypto_artifact_seal_manifest_core_v01(core)
            if seal.validate_airline_crypto_artifact_seal_manifest_core_v01(
                core,
            ).validation_status
            == seal.STATUS_PASS
            else "0" * 64
        ),
        signature=seal.build_airline_crypto_artifact_seal_signature_placeholder_v01(),
    )
    report = _valid_verification(_valid_a(), envelope=envelope)
    assert report.verification_status == seal.STATUS_FAIL_CLOSED
    assert reason in report.verification_errors


def test_wrong_expected_identity_fails_verification() -> None:
    wrong_identity = ledger.build_airline_transaction_artifact_ledger_fixture_expected_identity_v01(
        offer_id=ledger.OFFER_B_ID,
    )
    report = _valid_verification(
        _valid_a(),
        envelope=_valid_envelope(),
        expected_identity=wrong_identity,
    )
    assert report.verification_status == seal.STATUS_FAIL_CLOSED
    assert seal.REASON_VERIFICATION_MANIFEST_REBUILD_FAILED in report.verification_errors


@pytest.mark.parametrize(
    ("source_audit_status", "secret_scan_passed", "reason"),
    (
        (seal.STATUS_FAIL_CLOSED, True, seal.REASON_VERIFICATION_SOURCE_AUDIT_STATUS_MISMATCH),
        (object(), True, seal.REASON_VERIFICATION_SOURCE_AUDIT_STATUS_MISMATCH),
        (seal.STATUS_PASS, False, seal.REASON_VERIFICATION_SECRET_SCAN_BOUNDARY_MISMATCH),
        (seal.STATUS_PASS, object(), seal.REASON_VERIFICATION_SECRET_SCAN_BOUNDARY_MISMATCH),
    ),
)
def test_source_audit_and_secret_scan_inputs_must_match(
    source_audit_status: object,
    secret_scan_passed: object,
    reason: str,
) -> None:
    report = seal.verify_airline_crypto_artifact_seal_v01(
        _valid_envelope(),
        ledger_item=_valid_a(),
        ordered_source_files_before=_source_rows(),
        ordered_source_files_after=_source_rows(),
        expected_source_package_ref=_manifest_source_package_ref(),
        source_audit_status=source_audit_status,
        secret_scan_passed=secret_scan_passed,
    )
    assert report.verification_status == seal.STATUS_FAIL_CLOSED
    assert reason in report.verification_errors


@pytest.mark.parametrize(
    ("before", "after", "reason"),
    (
        ([], _source_rows(), seal.REASON_VERIFICATION_SOURCE_SNAPSHOT_MALFORMED),
        (_source_rows(), [], seal.REASON_VERIFICATION_SOURCE_SNAPSHOT_MALFORMED),
        (_source_rows()[:-1], _source_rows()[:-1], seal.REASON_VERIFICATION_SOURCE_SNAPSHOT_MALFORMED),
        (_source_rows() + (("extra.json", b"x"),), _source_rows(), seal.REASON_VERIFICATION_SOURCE_SNAPSHOT_MALFORMED),
    ),
)
def test_source_snapshot_outer_shape_failures(
    before: object,
    after: object,
    reason: str,
) -> None:
    report = seal.verify_airline_crypto_artifact_seal_v01(
        _valid_envelope(),
        ledger_item=_valid_a(),
        ordered_source_files_before=before,
        ordered_source_files_after=after,
        expected_source_package_ref=_manifest_source_package_ref(),
        source_audit_status=seal.STATUS_PASS,
        secret_scan_passed=True,
    )
    assert report.verification_status == seal.STATUS_FAIL_CLOSED
    assert reason in report.verification_errors


def test_reordered_before_or_after_source_rows_fail_closed() -> None:
    for mutate_before in (True, False):
        before = list(_source_rows())
        after = list(_source_rows())
        target = before if mutate_before else after
        target[0], target[1] = target[1], target[0]
        report = seal.verify_airline_crypto_artifact_seal_v01(
            _valid_envelope(),
            ledger_item=_valid_a(),
            ordered_source_files_before=tuple(before),
            ordered_source_files_after=tuple(after),
            expected_source_package_ref=_manifest_source_package_ref(),
            source_audit_status=seal.STATUS_PASS,
            secret_scan_passed=True,
        )
        assert report.verification_status == seal.STATUS_FAIL_CLOSED
        assert seal.REASON_VERIFICATION_SOURCE_SNAPSHOT_MALFORMED in (
            report.verification_errors
        )


@pytest.mark.parametrize("mutate_before", (True, False))
def test_non_bytes_source_content_fails_closed(mutate_before: bool) -> None:
    before = list(_source_rows())
    after = list(_source_rows())
    target = before if mutate_before else after
    target[0] = (target[0][0], bytearray(target[0][1]))  # type: ignore[assignment]
    report = seal.verify_airline_crypto_artifact_seal_v01(
        _valid_envelope(),
        ledger_item=_valid_a(),
        ordered_source_files_before=tuple(before),  # type: ignore[arg-type]
        ordered_source_files_after=tuple(after),  # type: ignore[arg-type]
        expected_source_package_ref=_manifest_source_package_ref(),
        source_audit_status=seal.STATUS_PASS,
        secret_scan_passed=True,
    )
    assert report.verification_status == seal.STATUS_FAIL_CLOSED
    assert seal.REASON_VERIFICATION_SOURCE_SNAPSHOT_MALFORMED in (
        report.verification_errors
    )


def test_changed_after_source_byte_fails_closed_as_source_bytes_changed() -> None:
    after = list(_source_rows())
    after[0] = (after[0][0], after[0][1] + b"x")
    report = _valid_verification(_valid_a(), rows_after=tuple(after))
    assert report.verification_status == seal.STATUS_FAIL_CLOSED
    assert seal.REASON_VERIFICATION_SOURCE_BYTES_CHANGED in report.verification_errors
    assert report.source_bytes_unchanged is False


def test_changed_after_source_ref_fails_as_malformed_snapshot() -> None:
    after = list(_source_rows())
    after[0] = ("different.json", after[0][1])
    report = _valid_verification(_valid_a(), rows_after=tuple(after))
    assert report.verification_status == seal.STATUS_FAIL_CLOSED
    assert seal.REASON_VERIFICATION_SOURCE_SNAPSHOT_MALFORMED in (
        report.verification_errors
    )


def test_source_inputs_ledger_and_envelope_unchanged_after_verification() -> None:
    item = _valid_a()
    envelope = _valid_envelope()
    rows = _source_rows()
    before_item = deepcopy(item)
    before_envelope = deepcopy(envelope)
    before_rows = tuple((ref, bytes(payload)) for ref, payload in rows)
    _valid_verification(item, envelope=envelope, rows_before=rows)
    assert item == before_item
    assert envelope == before_envelope
    assert rows == before_rows


def test_coordinated_modified_package_fails_against_original_anchor() -> None:
    original_anchor = _valid_anchor_for(_valid_a())
    changed_rows = list(_source_rows())
    changed_rows[2] = (changed_rows[2][0], changed_rows[2][1] + b"changed")
    modified_core = _valid_manifest_core(ordered_source_files=tuple(changed_rows))
    modified_envelope = seal.build_airline_crypto_artifact_seal_envelope_v01(
        modified_core,
    )
    anchored = _valid_verification(
        _valid_a(),
        envelope=modified_envelope,
        rows_before=tuple(changed_rows),
        rows_after=tuple(changed_rows),
        expected_manifest_core_hash=original_anchor,
    )
    assert anchored.verification_status == seal.STATUS_FAIL_CLOSED
    assert anchored.external_anchor_supplied is True
    assert anchored.external_anchor_verified is False
    assert seal.REASON_VERIFICATION_EXTERNAL_ANCHOR_MISMATCH in (
        anchored.verification_errors
    )
    unanchored = _valid_verification(
        _valid_a(),
        envelope=modified_envelope,
        rows_before=tuple(changed_rows),
        rows_after=tuple(changed_rows),
    )
    assert unanchored.verification_status == seal.STATUS_SELF_CONSISTENT_UNANCHORED


def test_semantic_causal_exact_source_verification_unanchored_and_anchored() -> None:
    source_bundle = collector_helpers._source_bundle_from_public_causal_runtime(
        ledger.OFFER_A_ID,
    )
    source_identity = collector_helpers._expected_identity(source_bundle)
    item = collector_helpers._assert_collected_pass(source_bundle)
    hold_entry = next(
        entry
        for entry in item.entries
        if entry.artifact_type == ledger.ARTIFACT_AIRLINE_HOLD_PACKET
    )
    assert hold_entry.artifact_id.startswith(
        "airline_hold_commit_packet:semantic_causal:",
    )
    envelope = seal.build_airline_crypto_artifact_seal_envelope_v01(
        _valid_manifest_core(item, expected_identity=source_identity),
    )
    unanchored = _valid_verification(
        item,
        envelope=envelope,
        expected_identity=source_identity,
    )
    assert unanchored.verification_status == seal.STATUS_SELF_CONSISTENT_UNANCHORED
    assert unanchored.external_anchor_supplied is False
    anchored = _valid_verification(
        item,
        envelope=envelope,
        expected_identity=source_identity,
        expected_manifest_core_hash=envelope.manifest_core_hash,
    )
    assert anchored.verification_status == seal.STATUS_PASS
    assert anchored.external_anchor_supplied is True
    assert anchored.external_anchor_verified is True
    assert anchored.signature_verified is False


def test_verification_report_direct_status_derivation_and_errors() -> None:
    valid = _valid_verification(_valid_a(), expected_manifest_core_hash=_valid_anchor_for())
    direct = replace(
        valid,
        verification_status=seal.STATUS_PASS,
        verification_errors=(seal.REASON_VERIFICATION_CHAIN_MISMATCH,),
    )
    assert direct.verification_status == seal.STATUS_FAIL_CLOSED
    assert seal.REASON_VERIFICATION_CHAIN_MISMATCH in direct.verification_errors
    one_flag_false = replace(valid, chain_tail_verified=False)
    assert one_flag_false.verification_status == seal.STATUS_FAIL_CLOSED
    assert seal.REASON_VERIFICATION_REPORT_INTERNAL_CHECK_FAILED in (
        one_flag_false.verification_errors
    )
    unanchored = replace(
        valid,
        verification_status=seal.STATUS_PASS,
        expected_manifest_core_hash=None,
        external_anchor_supplied=False,
        external_anchor_verified=False,
    )
    assert unanchored.verification_status == seal.STATUS_SELF_CONSISTENT_UNANCHORED


def test_verification_report_rejects_anchor_state_inconsistency() -> None:
    valid = _valid_verification(_valid_a(), expected_manifest_core_hash=_valid_anchor_for())
    for invalid in (
        replace(valid, external_anchor_supplied=False, external_anchor_verified=True),
        replace(valid, external_anchor_supplied=False, expected_manifest_core_hash="0" * 64),
    ):
        assert invalid.verification_status == seal.STATUS_FAIL_CLOSED
        assert seal.REASON_VERIFICATION_REPORT_ANCHOR_STATE_MISMATCH in (
            invalid.verification_errors
        )


def test_verification_report_errors_are_frozen_and_malformed_container_fails() -> None:
    errors = [seal.REASON_VERIFICATION_CHAIN_MISMATCH]
    report = seal.AirlineCryptoArtifactSealVerificationReportV01(
        **{
            **seal.airline_crypto_artifact_seal_verification_report_to_plain_dict_v01(
                _valid_verification(_valid_a()),
            ),
            "verification_errors": errors,
        },
    )
    errors.append(seal.REASON_VERIFICATION_SOURCE_BYTES_CHANGED)
    assert report.verification_errors == (seal.REASON_VERIFICATION_CHAIN_MISMATCH,)
    malformed = seal.AirlineCryptoArtifactSealVerificationReportV01(
        **{
            **seal.airline_crypto_artifact_seal_verification_report_to_plain_dict_v01(
                _valid_verification(_valid_a()),
            ),
            "verification_errors": "bad",
        },
    )
    assert malformed.verification_status == seal.STATUS_FAIL_CLOSED
    assert seal.REASON_MALFORMED_VALIDATION_ERRORS in malformed.verification_errors


@pytest.mark.parametrize(
    ("field_name", "value", "reason"),
    (
        ("provider_call_count", True, seal.REASON_VERIFICATION_REPORT_ZERO_COUNTER_MISMATCH),
        ("network_call_count", 1, seal.REASON_VERIFICATION_REPORT_ZERO_COUNTER_MISMATCH),
        ("signature_verified", True, seal.REASON_VERIFICATION_SIGNATURE_BOUNDARY_MISMATCH),
        ("signature_mode", "SIGNED", seal.REASON_VERIFICATION_SIGNATURE_BOUNDARY_MISMATCH),
    ),
)
def test_verification_report_counter_and_signature_contract(
    field_name: str,
    value: object,
    reason: str,
) -> None:
    report = replace(_valid_verification(_valid_a()), **{field_name: value})
    assert report.verification_status == seal.STATUS_FAIL_CLOSED
    assert reason in report.verification_errors


def test_report_validator_wrong_type_and_no_exception_for_malformed_report() -> None:
    report = seal.validate_airline_crypto_artifact_seal_verification_report_v01(
        object(),
    )
    assert report.validation_status == seal.STATUS_FAIL_CLOSED
    assert seal.REASON_VERIFICATION_REPORT_WRONG_TYPE in report.validation_errors


def test_report_plain_projection_is_independent_json_safe_object() -> None:
    report = _valid_verification(_valid_a())
    plain = seal.airline_crypto_artifact_seal_verification_report_to_plain_dict_v01(
        report,
    )
    plain["verification_status"] = "mutated"
    assert report.verification_status == seal.STATUS_SELF_CONSISTENT_UNANCHORED


def test_verification_report_is_frozen() -> None:
    report = _valid_verification(_valid_a())
    with pytest.raises(Exception):
        report.verification_status = seal.STATUS_PASS  # type: ignore[misc]
    with pytest.raises(Exception):
        report.verification_errors += ("x",)  # type: ignore[misc]


def test_static_import_boundary_is_airline_domain_only() -> None:
    tree = ast.parse(open(MODULE_PATH, encoding="utf-8").read())
    imports: list[str] = []
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            imports.extend(alias.name for alias in node.names)
        elif isinstance(node, ast.ImportFrom):
            imports.append(node.module or "")
    forbidden = (
        "pathlib",
        "requests",
        "urllib",
        "httpx",
        "openai",
        "google.genai",
        "socket",
        "subprocess",
        "cryptography",
        "Crypto",
        "config",
        "demo",
        "tests",
        "transaction_artifact_ledger_collector_v01",
        "semantic_to_contract_causal_runtime_v01",
        "ticket_purchase_corridor_runtime_v01",
    )
    assert not any(any(name.startswith(item) for item in forbidden) for name in imports)
    assert "hashlib" in imports
    assert "json" in imports


def test_static_no_file_io_calls_or_replay_surface() -> None:
    source = open(MODULE_PATH, encoding="utf-8").read()
    tree = ast.parse(source)
    forbidden_calls = {"open", "read", "write"}
    for node in ast.walk(tree):
        if isinstance(node, ast.Call):
            if isinstance(node.func, ast.Name):
                assert node.func.id not in forbidden_calls
            if isinstance(node.func, ast.Attribute):
                assert node.func.attr not in forbidden_calls
        if isinstance(node, (ast.ClassDef, ast.FunctionDef, ast.AsyncFunctionDef)):
            assert "Replay" not in node.name
    assert "collector_v01" not in source
    assert "writer_v01" not in source


def test_static_no_signing_key_or_mutable_module_global_registry() -> None:
    source = open(MODULE_PATH, encoding="utf-8").read()
    tree = ast.parse(source)
    forbidden_definition_terms = (
        "private_key",
        "public_key",
        "hmac",
        "encrypt",
        "decrypt",
        "certificate",
    )
    for node in tree.body:
        if isinstance(node, (ast.ClassDef, ast.FunctionDef, ast.AsyncFunctionDef)):
            lowered = node.name.lower()
            assert not any(term in lowered for term in forbidden_definition_terms)
        if isinstance(node, ast.Assign):
            for target in node.targets:
                if isinstance(target, ast.Name):
                    assert target.id not in {
                        "MANIFEST_REGISTRY",
                        "CURRENT_LEDGER",
                        "CURRENT_TRANSACTION",
                        "CURRENT_CHAIN",
                        "CURRENT_MANIFEST",
                        "CURRENT_ENVELOPE",
                        "CURRENT_VERIFICATION_REPORT",
                        "CURRENT_EXPECTED_MANIFEST_CORE_HASH",
                        "TRUSTED_ANCHOR_REGISTRY",
                        "VERIFICATION_REGISTRY",
                        "SIGNATURE_REGISTRY",
                    }
            assert not isinstance(node.value, (ast.List, ast.Dict, ast.Set))


def test_static_universal_core_not_modified_by_this_slice() -> None:
    source = open(MODULE_PATH, encoding="utf-8").read()
    assert "hedgehog.crypto" not in source
    assert "from hedgehog import" not in source

def test_public_validation_report_builder_rejects_malformed_containers() -> None:
    for malformed in ("", {}, None):
        report = seal.build_airline_crypto_validation_report_v01(malformed)
        assert report.validation_status == seal.STATUS_FAIL_CLOSED
        assert report.validation_errors == (
            seal.REASON_MALFORMED_VALIDATION_ERRORS,
        )


def test_projection_constructor_rejects_string_depends_on() -> None:
    projection = seal.build_airline_crypto_ledger_entry_projections_v01(
        _valid_a(),
    )[0]
    with pytest.raises(
        ValueError,
        match=seal.REASON_PROJECTION_MALFORMED_DEPENDS_ON,
    ):
        replace(projection, depends_on="abc")


def test_projection_validator_rejects_lone_surrogate_in_outer_ledger_id() -> None:
    projection = seal.build_airline_crypto_ledger_entry_projections_v01(
        _valid_a(),
    )[0]
    invalid = replace(projection, ledger_id="bad\ud800")

    report = seal.validate_airline_crypto_ledger_entry_projection_v01(
        invalid,
    )

    assert report.validation_status == seal.STATUS_FAIL_CLOSED
    assert seal.REASON_LONE_SURROGATE in report.validation_errors

    with pytest.raises(ValueError, match=seal.REASON_LONE_SURROGATE):
        seal.hash_airline_crypto_ledger_entry_projection_v01(invalid)


def test_projection_envelope_comparison_keeps_bool_distinct_from_int() -> None:
    projection = seal.build_airline_crypto_ledger_entry_projections_v01(
        _valid_a(),
    )[0]
    _, canonical = _projection_with_plain_input(projection)
    canonical["ledger_index"] = False
    invalid = replace(
        projection,
        canonical_hash_input=canonical,
    )

    report = seal.validate_airline_crypto_ledger_entry_projection_v01(
        invalid,
    )

    assert report.validation_status == seal.STATUS_FAIL_CLOSED
    assert (
        seal.REASON_PROJECTION_CANONICAL_HASH_INPUT_FIELD_MISMATCH
        in report.validation_errors
    )

    with pytest.raises(
        ValueError,
        match=seal.REASON_PROJECTION_CANONICAL_HASH_INPUT_FIELD_MISMATCH,
    ):
        seal.hash_airline_crypto_ledger_entry_projection_v01(invalid)

def test_manifest_builder_requires_exact_source_audit_status_string() -> None:
    class _AlwaysPass:
        def __eq__(self, other: object) -> bool:
            return True

        def __ne__(self, other: object) -> bool:
            return False

    pass_subclass = type(
        "PassStringSubclass",
        (str,),
        {},
    )(seal.STATUS_PASS)

    for malformed in (_AlwaysPass(), pass_subclass):
        with pytest.raises(
            ValueError,
            match=seal.REASON_MANIFEST_SOURCE_AUDIT_STATUS_MISMATCH,
        ):
            seal.build_airline_crypto_artifact_seal_manifest_core_v01(
                _valid_a(),
                ordered_source_files=_source_rows(),
                source_package_ref=_manifest_source_package_ref(),
                source_audit_status=malformed,  # type: ignore[arg-type]
                secret_scan_passed=True,
            )


def test_report_anchor_verified_requires_expected_hash_to_equal_manifest_hash() -> None:
    valid = _valid_verification(
        _valid_a(),
        expected_manifest_core_hash=_valid_anchor_for(),
    )
    invalid = replace(valid, expected_manifest_core_hash="1" * 64)
    assert invalid.verification_status == seal.STATUS_FAIL_CLOSED
    assert seal.REASON_VERIFICATION_REPORT_ANCHOR_STATE_MISMATCH in invalid.verification_errors
    assert (
        seal.validate_airline_crypto_artifact_seal_verification_report_v01(invalid).validation_status
        == seal.STATUS_PASS
    )


def test_report_success_status_requires_nonempty_identity_and_valid_manifest_hash() -> None:
    valid = _valid_verification(
        _valid_a(),
        expected_manifest_core_hash=_valid_anchor_for(),
    )
    for invalid in (
        replace(valid, transaction_id=""),
        replace(valid, ledger_id=""),
        replace(valid, manifest_core_hash="not-a-digest"),
    ):
        assert invalid.verification_status == seal.STATUS_FAIL_CLOSED
        assert seal.REASON_VERIFICATION_REPORT_FIELD_MISMATCH in invalid.verification_errors
        assert (
            seal.validate_airline_crypto_artifact_seal_verification_report_v01(invalid).validation_status
            == seal.STATUS_PASS
        )


def test_report_signature_mode_requires_exact_string() -> None:
    valid = _valid_verification(_valid_a())
    subclass = type("SignatureModeSubclass", (str,), {})(
        seal.SIGNATURE_MODE_UNSIGNED_PLACEHOLDER,
    )
    invalid = replace(valid, signature_mode=subclass)
    assert invalid.verification_status == seal.STATUS_FAIL_CLOSED
    assert seal.REASON_VERIFICATION_SIGNATURE_BOUNDARY_MISMATCH in invalid.verification_errors


def test_unknown_and_non_unicode_verification_errors_normalize_to_malformed() -> None:
    valid = _valid_verification(_valid_a())
    for reason in ("unknown reason", "bad\ud800"):
        invalid = replace(valid, verification_errors=(reason,))
        assert invalid.verification_status == seal.STATUS_FAIL_CLOSED
        assert invalid.verification_errors == (
            seal.REASON_MALFORMED_VALIDATION_ERRORS,
        )
        plain = seal.airline_crypto_artifact_seal_verification_report_to_plain_dict_v01(
            invalid,
        )
        assert (
            seal.validate_airline_crypto_canonical_json_value_v01(plain).validation_status
            == seal.STATUS_PASS
        )


def test_source_byte_failure_report_is_contract_valid_and_json_safe() -> None:
    after = list(_source_rows())
    after[0] = (after[0][0], after[0][1] + b"x")
    report = _valid_verification(_valid_a(), rows_after=tuple(after))
    assert report.verification_status == seal.STATUS_FAIL_CLOSED
    assert report.external_anchor_verified is False
    assert (
        seal.validate_airline_crypto_artifact_seal_verification_report_v01(report).validation_status
        == seal.STATUS_PASS
    )
    plain = seal.airline_crypto_artifact_seal_verification_report_to_plain_dict_v01(report)
    assert seal.validate_airline_crypto_canonical_json_value_v01(plain).validation_status == seal.STATUS_PASS


def test_invalid_envelope_failure_report_is_contract_valid_and_json_safe() -> None:
    report = seal.verify_airline_crypto_artifact_seal_v01(
        object(),
        ledger_item=_valid_a(),
        ordered_source_files_before=_source_rows(),
        ordered_source_files_after=_source_rows(),
        expected_source_package_ref=_manifest_source_package_ref(),
        source_audit_status=seal.STATUS_PASS,
        secret_scan_passed=True,
        expected_manifest_core_hash=_valid_anchor_for(),
    )
    assert report.verification_status == seal.STATUS_FAIL_CLOSED
    assert report.external_anchor_verified is False
    assert (
        seal.validate_airline_crypto_artifact_seal_verification_report_v01(report).validation_status
        == seal.STATUS_PASS
    )
    plain = seal.airline_crypto_artifact_seal_verification_report_to_plain_dict_v01(report)
    assert seal.validate_airline_crypto_canonical_json_value_v01(plain).validation_status == seal.STATUS_PASS


def test_verifier_sanitizes_lone_surrogate_report_fields() -> None:
    envelope = replace(_valid_envelope(), manifest_core_hash="bad\ud800")
    report = _valid_verification(_valid_a(), envelope=envelope)
    assert report.verification_status == seal.STATUS_FAIL_CLOSED
    assert report.manifest_core_hash == ""
    plain = seal.airline_crypto_artifact_seal_verification_report_to_plain_dict_v01(report)
    assert seal.validate_airline_crypto_canonical_json_value_v01(plain).validation_status == seal.STATUS_PASS


def test_matching_anchor_is_not_marked_verified_when_internal_check_fails() -> None:
    anchor = _valid_anchor_for()
    after = list(_source_rows())
    after[0] = (after[0][0], after[0][1] + b"x")
    report = _valid_verification(
        _valid_a(),
        rows_after=tuple(after),
        expected_manifest_core_hash=anchor,
    )
    assert report.verification_status == seal.STATUS_FAIL_CLOSED
    assert report.external_anchor_supplied is True
    assert report.external_anchor_verified is False
