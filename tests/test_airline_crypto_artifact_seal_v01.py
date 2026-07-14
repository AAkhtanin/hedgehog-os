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
        "transaction_artifact_ledger_collector_v01",
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
    assert "AirlineCryptoArtifactSealManifestCoreV01" not in source
    assert "AirlineCryptoArtifactSealEnvelopeV01" not in source
    assert "AirlineCryptoArtifactSealVerificationReportV01" not in source
    assert "verify_airline_crypto_artifact_seal_v01" not in source


def test_static_no_signature_or_mutable_module_global_registry() -> None:
    source = open(MODULE_PATH, encoding="utf-8").read()
    tree = ast.parse(source)
    forbidden_definition_terms = (
        "signature",
        "private_key",
        "public_key",
        "hmac",
        "encrypt",
        "decrypt",
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

