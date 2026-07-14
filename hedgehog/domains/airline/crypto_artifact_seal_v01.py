"""Airline Crypto Artifact Seal v0.1 strict primitives and contracts.

Airline Crypto Artifact Seal records cryptographic integrity and ordered
continuity of a declared Airline artifact set.

It does not prove semantic truth.
It does not grant permission.
It does not create authority.
It does not authorize or execute an action.
It does not create FinalOutput.
It does not authenticate a signer.
It does not provide confidentiality or encryption.

Slice B1 includes strict canonicalization, SHA-256 primitives, Ledger-entry
projections, ordered Ledger hash chains, and in-memory source-package byte
indexing. Slice B2a adds Manifest Core and unsigned Envelope contracts.
External-anchor verification, Verification Report, collectors, writers,
integration, audit, and Replay are not implemented here.
"""

from __future__ import annotations

import hashlib
import json
import re
from collections.abc import Mapping as MappingABC
from dataclasses import dataclass, is_dataclass
from enum import Enum
from types import MappingProxyType
from typing import Any, Mapping

from hedgehog.domains.airline import transaction_artifact_ledger_v01 as ledger_contracts


MODULE_ID = "airline_crypto_artifact_seal_v01"
SLICE_ID = "airline_crypto_artifact_seal_v01_slice_b1"
SLICE_B2A_ID = "airline_crypto_artifact_seal_v01_slice_b2a"
SEAL_VERSION = "airline_crypto_artifact_seal_v01"
CANONICALIZATION_PROFILE_ID = "hedgehog_airline_json_c14n_v01"
HASH_ALGORITHM = "SHA-256"
HASH_ENCODING = "lowercase_hex"
SIGNATURE_MODE_UNSIGNED_PLACEHOLDER = "UNSIGNED_PLACEHOLDER"
SIGNATURE_ALGORITHM_NONE = "NONE"

STATUS_PASS = "PASS"
STATUS_FAIL_CLOSED = "FAIL_CLOSED"
STATUS_SELF_CONSISTENT_UNANCHORED = "SELF_CONSISTENT_UNANCHORED"

DOMAIN_LEDGER_ENTRY = "hedgehog-airline-seal-v01:ledger-entry"
DOMAIN_CHAIN_GENESIS = "hedgehog-airline-seal-v01:chain-genesis"
DOMAIN_CHAIN_LINK = "hedgehog-airline-seal-v01:chain-link"
DOMAIN_SOURCE_PACKAGE_INDEX = "hedgehog-airline-seal-v01:source-package-index"
DOMAIN_MANIFEST_CORE = "hedgehog-airline-seal-v01:manifest-core"

REQUIRED_SOURCE_FILE_REFS = (
    "airline_transaction_artifact_ledger.json",
    "summary.json",
    "secret_scan.json",
    "semantic_to_contract_causal_run.json",
    "semantic_to_contract_bridge.json",
    "integrated_deterministic_airline_summary.json",
    "tri_party_airline_bsep_packet.json",
    "tri_party_airline_bsep_validation.json",
    "tri_party_airline_bsep_side_projections.json",
)

MANIFEST_CORE_FIELD_NAMES = (
    "seal_id",
    "seal_version",
    "transaction_id",
    "ledger_id",
    "source_package_ref",
    "canonicalization_profile_id",
    "hash_algorithm",
    "hash_encoding",
    "ledger_entry_count",
    "dependency_edge_count",
    "root_final_count",
    "ordered_artifact_refs",
    "ordered_artifact_hashes",
    "chain_genesis_hash",
    "chain_head_hash",
    "chain_tail_hash",
    "source_file_count",
    "ordered_source_file_refs",
    "ordered_source_file_hashes",
    "source_package_hash",
    "ledger_document_byte_hash",
    "previous_manifest_ref",
    "signature_placeholder_present",
    "signature_verified",
    "source_audit_status",
    "secret_scan_passed",
    "raw_secret_included",
    "seal_created_authority_count",
    "seal_created_permission_count",
    "seal_created_action_count",
    "real_world_effects_count",
)

SIGNED_INT64_MIN = -9223372036854775808
SIGNED_INT64_MAX = 9223372036854775807
SHA256_HEX_RE = re.compile(r"^[0-9a-f]{64}$")

REASON_EXPECTED_BYTES = "expected_exact_bytes"
REASON_EXPECTED_JSON_OBJECT = "expected_json_object"
REASON_UTF8_BOM = "utf8_bom_forbidden"
REASON_MALFORMED_UTF8 = "malformed_utf8"
REASON_MALFORMED_JSON = "malformed_json"
REASON_DUPLICATE_JSON_KEY = "duplicate_json_key"
REASON_JSON_CONSTANT_FORBIDDEN = "json_constant_forbidden"
REASON_NON_STRING_KEY = "non_string_key"
REASON_INTEGER_OUT_OF_RANGE = "integer_out_of_signed_64_bit_range"
REASON_FLOAT_FORBIDDEN = "float_forbidden"
REASON_BYTES_FORBIDDEN = "bytes_forbidden"
REASON_TUPLE_FORBIDDEN = "tuple_forbidden"
REASON_MAPPING_PROXY_FORBIDDEN = "mappingproxy_forbidden"
REASON_DATACLASS_FORBIDDEN = "dataclass_forbidden"
REASON_ENUM_FORBIDDEN = "enum_forbidden"
REASON_SET_FORBIDDEN = "set_forbidden"
REASON_ARBITRARY_OBJECT_FORBIDDEN = "arbitrary_object_forbidden"
REASON_LONE_SURROGATE = "lone_surrogate_forbidden"
REASON_CYCLIC_VALUE = "cyclic_value"
REASON_INVALID_SHA256_HEX = "invalid_sha256_hex"
REASON_MALFORMED_VALIDATION_ERRORS = "malformed_validation_errors"
REASON_EXPECTED_IDENTITY_WRONG_TYPE = "expected_identity_wrong_type"

REASON_MALFORMED_LEDGER = "malformed_ledger"
REASON_LEDGER_VALIDATION_FAILED = "ledger_validation_failed"
REASON_LEDGER_STORED_STATUS_FAILED = "ledger_stored_status_failed"
REASON_LEDGER_STORED_ERRORS_MALFORMED = "ledger_stored_errors_malformed"
REASON_LEDGER_GEOMETRY_MISMATCH = "ledger_geometry_mismatch"
REASON_LEDGER_ARTIFACT_SEQUENCE_MISMATCH = "ledger_artifact_sequence_mismatch"
REASON_LEDGER_ROOT_FINAL_SET_MISMATCH = "ledger_root_final_set_mismatch"
REASON_LEDGER_INDEX_MISMATCH = "ledger_index_mismatch"
REASON_LEDGER_TRANSACTION_MISMATCH = "ledger_transaction_mismatch"
REASON_LEDGER_DUPLICATE_ARTIFACT_REF = "ledger_duplicate_artifact_ref"
REASON_LEDGER_SOURCE_BOUNDARY_MISMATCH = "ledger_source_boundary_mismatch"
REASON_UNSUPPORTED_LEDGER_CANONICAL_SOURCE_VALUE = (
    "unsupported_ledger_canonical_source_value"
)
REASON_MALFORMED_PROJECTION = "malformed_projection"
REASON_PROJECTION_CANONICALIZATION_PROFILE_MISMATCH = (
    "projection_canonicalization_profile_mismatch"
)
REASON_PROJECTION_EMPTY_STRING_FIELD = "projection_empty_string_field"
REASON_PROJECTION_LEDGER_INDEX_MISMATCH = "projection_ledger_index_mismatch"
REASON_PROJECTION_MALFORMED_DEPENDS_ON = "projection_malformed_depends_on"
REASON_PROJECTION_CANONICAL_HASH_INPUT_MALFORMED = (
    "projection_canonical_hash_input_malformed"
)
REASON_PROJECTION_CANONICAL_HASH_INPUT_FIELD_MISMATCH = (
    "projection_canonical_hash_input_field_mismatch"
)

REASON_MALFORMED_SOURCE_PACKAGE_INPUT = "malformed_source_package_input"
REASON_SOURCE_PACKAGE_TRANSACTION_ID = "source_package_transaction_id_invalid"
REASON_SOURCE_PACKAGE_FILE_COUNT = "source_package_file_count_mismatch"
REASON_SOURCE_PACKAGE_FILE_ORDER = "source_package_file_order_mismatch"
REASON_SOURCE_PACKAGE_DUPLICATE_REF = "source_package_duplicate_ref"
REASON_SOURCE_PACKAGE_REF_INVALID = "source_package_ref_invalid"
REASON_SOURCE_PACKAGE_CONTENT_NOT_BYTES = "source_package_content_not_bytes"
REASON_MANIFEST_CORE_WRONG_TYPE = "manifest_core_wrong_type"
REASON_MANIFEST_SOURCE_PACKAGE_REF_MALFORMED = (
    "manifest_source_package_ref_malformed"
)
REASON_MANIFEST_VERSION_PROFILE_ALGORITHM_MISMATCH = (
    "manifest_version_profile_algorithm_mismatch"
)
REASON_MANIFEST_IDENTITY_MISMATCH = "manifest_identity_mismatch"
REASON_MANIFEST_LEDGER_GEOMETRY_MISMATCH = "manifest_ledger_geometry_mismatch"
REASON_MANIFEST_ARTIFACT_REF_HASH_GEOMETRY_MISMATCH = (
    "manifest_artifact_ref_hash_geometry_mismatch"
)
REASON_MANIFEST_INVALID_ARTIFACT_REF = "manifest_invalid_artifact_ref"
REASON_MANIFEST_DUPLICATE_ARTIFACT_REF = "manifest_duplicate_artifact_ref"
REASON_MANIFEST_INVALID_ARTIFACT_HASH = "manifest_invalid_artifact_hash"
REASON_MANIFEST_CHAIN_HASH_MISMATCH = "manifest_chain_hash_mismatch"
REASON_MANIFEST_SOURCE_REF_HASH_GEOMETRY_MISMATCH = (
    "manifest_source_ref_hash_geometry_mismatch"
)
REASON_MANIFEST_SOURCE_FILE_ORDER_MISMATCH = (
    "manifest_source_file_order_mismatch"
)
REASON_MANIFEST_DUPLICATE_SOURCE_REF = "manifest_duplicate_source_ref"
REASON_MANIFEST_INVALID_SOURCE_HASH = "manifest_invalid_source_hash"
REASON_MANIFEST_LEDGER_DOCUMENT_BYTE_HASH_MISMATCH = (
    "manifest_ledger_document_byte_hash_mismatch"
)
REASON_MANIFEST_PREVIOUS_REF_MISMATCH = "manifest_previous_ref_mismatch"
REASON_MANIFEST_SIGNATURE_FLAG_MISMATCH = "manifest_signature_flag_mismatch"
REASON_MANIFEST_SOURCE_AUDIT_STATUS_MISMATCH = (
    "manifest_source_audit_status_mismatch"
)
REASON_MANIFEST_SECRET_SCAN_BOUNDARY_MISMATCH = (
    "manifest_secret_scan_boundary_mismatch"
)
REASON_MANIFEST_NONZERO_COUNTER = "manifest_nonzero_counter"
REASON_SIGNATURE_PLACEHOLDER_WRONG_TYPE = "signature_placeholder_wrong_type"
REASON_SIGNATURE_PLACEHOLDER_FIELD_MISMATCH = (
    "signature_placeholder_field_mismatch"
)
REASON_MANIFEST_CORE_HASH_MISMATCH = "manifest_core_hash_mismatch"
REASON_ENVELOPE_MALFORMED = "envelope_malformed"


@dataclass(frozen=True)
class AirlineCryptoArtifactSealValidationReportV01:
    validation_status: str
    validation_errors: tuple[str, ...]

    def __post_init__(self) -> None:
        raw_errors = self.validation_errors
        if type(raw_errors) not in (tuple, list):
            errors = (REASON_MALFORMED_VALIDATION_ERRORS,)
        else:
            errors = _unique_reasons(raw_errors)
        object.__setattr__(
            self,
            "validation_status",
            STATUS_PASS if not errors else STATUS_FAIL_CLOSED,
        )
        object.__setattr__(self, "validation_errors", errors)


def build_airline_crypto_validation_report_v01(
    validation_errors: object,
) -> AirlineCryptoArtifactSealValidationReportV01:
    errors = (
        _unique_reasons(validation_errors)
        if type(validation_errors) in (tuple, list)
        else (REASON_MALFORMED_VALIDATION_ERRORS,)
    )
    return AirlineCryptoArtifactSealValidationReportV01(
        validation_status=STATUS_PASS if not errors else STATUS_FAIL_CLOSED,
        validation_errors=errors,
    )


@dataclass(frozen=True)
class AirlineCryptoLedgerEntrySealProjectionV01:
    canonicalization_profile_id: str
    ledger_id: str
    transaction_id: str
    ledger_index: int
    event_type: str
    artifact_type: str
    artifact_id: str
    root_owner: str
    created_by: str
    authority_class: str
    evidence_class: str
    depends_on: tuple[str, ...]
    canonical_hash_input: Mapping[str, object]

    def __post_init__(self) -> None:
        raw_depends_on = self.depends_on
        if type(raw_depends_on) not in (tuple, list) or any(
            type(ref) is not str or not ref for ref in raw_depends_on
        ):
            raise ValueError(REASON_PROJECTION_MALFORMED_DEPENDS_ON)
        object.__setattr__(self, "depends_on", tuple(raw_depends_on))
        object.__setattr__(
            self,
            "canonical_hash_input",
            _freeze_projected_json(self.canonical_hash_input, set()),
        )


@dataclass(frozen=True)
class AirlineCryptoLedgerEntryHashV01:
    ledger_index: int
    artifact_ref: str
    artifact_hash: str


@dataclass(frozen=True)
class AirlineCryptoLedgerChainLinkV01:
    ledger_index: int
    artifact_ref: str
    artifact_hash: str
    previous_chain_hash: str
    chain_hash: str


@dataclass(frozen=True)
class AirlineCryptoLedgerHashChainV01:
    ledger_id: str
    transaction_id: str
    artifact_count: int
    artifact_refs: tuple[str, ...]
    artifact_hashes: tuple[str, ...]
    chain_genesis_hash: str
    chain_head_hash: str
    chain_tail_hash: str
    chain_links: tuple[AirlineCryptoLedgerChainLinkV01, ...]

    def __post_init__(self) -> None:
        object.__setattr__(self, "artifact_refs", tuple(self.artifact_refs))
        object.__setattr__(self, "artifact_hashes", tuple(self.artifact_hashes))
        object.__setattr__(self, "chain_links", tuple(self.chain_links))


@dataclass(frozen=True)
class AirlineCryptoSourceFileHashV01:
    relative_ref: str
    sha256: str


@dataclass(frozen=True)
class AirlineCryptoSourcePackageIndexV01:
    transaction_id: str
    source_file_count: int
    ordered_source_file_refs: tuple[str, ...]
    ordered_source_file_hashes: tuple[str, ...]
    source_file_hash_records: tuple[AirlineCryptoSourceFileHashV01, ...]
    source_package_hash: str
    ledger_document_byte_hash: str

    def __post_init__(self) -> None:
        object.__setattr__(
            self,
            "ordered_source_file_refs",
            tuple(self.ordered_source_file_refs),
        )
        object.__setattr__(
            self,
            "ordered_source_file_hashes",
            tuple(self.ordered_source_file_hashes),
        )
        object.__setattr__(
            self,
            "source_file_hash_records",
            tuple(self.source_file_hash_records),
        )


@dataclass(frozen=True)
class AirlineCryptoArtifactSealManifestCoreV01:
    seal_id: str
    seal_version: str
    transaction_id: str
    ledger_id: str
    source_package_ref: str
    canonicalization_profile_id: str
    hash_algorithm: str
    hash_encoding: str
    ledger_entry_count: int
    dependency_edge_count: int
    root_final_count: int
    ordered_artifact_refs: tuple[str, ...]
    ordered_artifact_hashes: tuple[str, ...]
    chain_genesis_hash: str
    chain_head_hash: str
    chain_tail_hash: str
    source_file_count: int
    ordered_source_file_refs: tuple[str, ...]
    ordered_source_file_hashes: tuple[str, ...]
    source_package_hash: str
    ledger_document_byte_hash: str
    previous_manifest_ref: None
    signature_placeholder_present: bool
    signature_verified: bool
    source_audit_status: str
    secret_scan_passed: bool
    raw_secret_included: bool
    seal_created_authority_count: int
    seal_created_permission_count: int
    seal_created_action_count: int
    real_world_effects_count: int

    def __post_init__(self) -> None:
        object.__setattr__(
            self,
            "ordered_artifact_refs",
            _freeze_manifest_string_sequence(
                self.ordered_artifact_refs,
                REASON_MANIFEST_ARTIFACT_REF_HASH_GEOMETRY_MISMATCH,
            ),
        )
        object.__setattr__(
            self,
            "ordered_artifact_hashes",
            _freeze_manifest_string_sequence(
                self.ordered_artifact_hashes,
                REASON_MANIFEST_ARTIFACT_REF_HASH_GEOMETRY_MISMATCH,
            ),
        )
        object.__setattr__(
            self,
            "ordered_source_file_refs",
            _freeze_manifest_string_sequence(
                self.ordered_source_file_refs,
                REASON_MANIFEST_SOURCE_REF_HASH_GEOMETRY_MISMATCH,
            ),
        )
        object.__setattr__(
            self,
            "ordered_source_file_hashes",
            _freeze_manifest_string_sequence(
                self.ordered_source_file_hashes,
                REASON_MANIFEST_SOURCE_REF_HASH_GEOMETRY_MISMATCH,
            ),
        )


@dataclass(frozen=True)
class AirlineCryptoArtifactSealSignaturePlaceholderV01:
    mode: str
    algorithm: str
    key_id: str
    value: str
    verified: bool


@dataclass(frozen=True)
class AirlineCryptoArtifactSealEnvelopeV01:
    manifest_core: AirlineCryptoArtifactSealManifestCoreV01
    manifest_core_hash: str
    signature: AirlineCryptoArtifactSealSignaturePlaceholderV01


def validate_airline_crypto_canonical_json_value_v01(
    value: object,
) -> AirlineCryptoArtifactSealValidationReportV01:
    errors: list[str] = []
    _validate_canonical_value(value, errors, set())
    return build_airline_crypto_validation_report_v01(errors)


def canonical_airline_crypto_json_bytes_v01(value: object) -> bytes:
    report = validate_airline_crypto_canonical_json_value_v01(value)
    if report.validation_status != STATUS_PASS:
        raise ValueError(",".join(report.validation_errors))
    text = json.dumps(
        value,
        ensure_ascii=False,
        sort_keys=True,
        separators=(",", ":"),
        allow_nan=False,
    )
    return text.encode("utf-8", errors="strict")


def canonical_airline_crypto_json_text_v01(value: object) -> str:
    return canonical_airline_crypto_json_bytes_v01(value).decode("utf-8")


def parse_airline_crypto_json_object_bytes_v01(raw_bytes: bytes) -> dict[str, object]:
    if type(raw_bytes) is not bytes:
        raise ValueError(REASON_EXPECTED_BYTES)
    if raw_bytes.startswith(b"\xef\xbb\xbf"):
        raise ValueError(REASON_UTF8_BOM)
    try:
        text = raw_bytes.decode("utf-8", errors="strict")
    except UnicodeDecodeError as exc:
        raise ValueError(REASON_MALFORMED_UTF8) from exc
    try:
        parsed = json.loads(
            text,
            object_pairs_hook=_reject_duplicate_json_pairs,
            parse_constant=_reject_json_constant,
        )
    except json.JSONDecodeError as exc:
        raise ValueError(REASON_MALFORMED_JSON) from exc
    except ValueError:
        raise
    if type(parsed) is not dict:
        raise ValueError(REASON_EXPECTED_JSON_OBJECT)
    report = validate_airline_crypto_canonical_json_value_v01(parsed)
    if report.validation_status != STATUS_PASS:
        raise ValueError(",".join(report.validation_errors))
    return parsed


def sha256_hex_v01(exact_bytes: bytes) -> str:
    if type(exact_bytes) is not bytes:
        raise ValueError(REASON_EXPECTED_BYTES)
    return hashlib.sha256(exact_bytes).hexdigest()


def validate_sha256_hex_v01(
    value: object,
) -> AirlineCryptoArtifactSealValidationReportV01:
    if type(value) is not str or SHA256_HEX_RE.fullmatch(value) is None:
        return build_airline_crypto_validation_report_v01([REASON_INVALID_SHA256_HEX])
    return build_airline_crypto_validation_report_v01([])


def validate_airline_crypto_source_package_ref_v01(
    value: object,
) -> AirlineCryptoArtifactSealValidationReportV01:
    if not _valid_source_package_ref(value):
        return build_airline_crypto_validation_report_v01(
            [REASON_MANIFEST_SOURCE_PACKAGE_REF_MALFORMED],
        )
    return build_airline_crypto_validation_report_v01([])


def build_airline_crypto_ledger_entry_projections_v01(
    ledger_item: ledger_contracts.AirlineTransactionArtifactLedgerV01,
    *,
    expected_identity: (
        ledger_contracts.AirlineTransactionArtifactLedgerExpectedIdentityV01
        | None
    ) = None,
) -> tuple[AirlineCryptoLedgerEntrySealProjectionV01, ...]:
    _require_valid_accepted_ledger(
        ledger_item,
        expected_identity=expected_identity,
    )
    return tuple(
        AirlineCryptoLedgerEntrySealProjectionV01(
            canonicalization_profile_id=CANONICALIZATION_PROFILE_ID,
            ledger_id=ledger_item.ledger_id,
            transaction_id=entry.transaction_id,
            ledger_index=entry.ledger_index,
            event_type=entry.event_type,
            artifact_type=entry.artifact_type,
            artifact_id=entry.artifact_id,
            root_owner=entry.root_owner,
            created_by=entry.created_by,
            authority_class=entry.authority_class,
            evidence_class=entry.evidence_class,
            depends_on=entry.depends_on,
            canonical_hash_input=_plain_ledger_json_tree(entry.canonical_hash_input),
        )
        for entry in ledger_item.entries
    )


def airline_crypto_ledger_entry_projection_to_plain_dict_v01(
    projection: AirlineCryptoLedgerEntrySealProjectionV01,
) -> dict[str, object]:
    report = validate_airline_crypto_ledger_entry_projection_v01(projection)
    if report.validation_status != STATUS_PASS:
        raise ValueError(",".join(report.validation_errors))
    return {
        "canonicalization_profile_id": projection.canonicalization_profile_id,
        "ledger_id": projection.ledger_id,
        "transaction_id": projection.transaction_id,
        "ledger_index": projection.ledger_index,
        "event_type": projection.event_type,
        "artifact_type": projection.artifact_type,
        "artifact_id": projection.artifact_id,
        "root_owner": projection.root_owner,
        "created_by": projection.created_by,
        "authority_class": projection.authority_class,
        "evidence_class": projection.evidence_class,
        "depends_on": list(projection.depends_on),
        "canonical_hash_input": _plain_projection_json_tree(
            projection.canonical_hash_input,
            set(),
        ),
    }


def validate_airline_crypto_ledger_entry_projection_v01(
    projection: object,
) -> AirlineCryptoArtifactSealValidationReportV01:
    errors: list[str] = []
    if type(projection) is not AirlineCryptoLedgerEntrySealProjectionV01:
        return build_airline_crypto_validation_report_v01(
            [REASON_MALFORMED_PROJECTION],
        )
    if projection.canonicalization_profile_id != CANONICALIZATION_PROFILE_ID:
        _append(errors, REASON_PROJECTION_CANONICALIZATION_PROFILE_MISMATCH)
    for value in (
        projection.ledger_id,
        projection.transaction_id,
        projection.event_type,
        projection.artifact_type,
        projection.artifact_id,
        projection.root_owner,
        projection.created_by,
        projection.authority_class,
        projection.evidence_class,
    ):
        if type(value) is not str or not value:
            _append(errors, REASON_PROJECTION_EMPTY_STRING_FIELD)
        elif _contains_lone_surrogate(value):
            _append(errors, REASON_LONE_SURROGATE)
    if (
        type(projection.ledger_index) is not int
        or projection.ledger_index < 0
        or projection.ledger_index > 18
    ):
        _append(errors, REASON_PROJECTION_LEDGER_INDEX_MISMATCH)
    if (
        type(projection.depends_on) is not tuple
        or any(
            type(ref) is not str
            or not ref
            or _contains_lone_surrogate(ref)
            for ref in projection.depends_on
        )
    ):
        _append(errors, REASON_PROJECTION_MALFORMED_DEPENDS_ON)
    plain_input: object | None = None
    if type(projection.canonical_hash_input) not in (dict, MappingProxyType):
        _append(errors, REASON_PROJECTION_CANONICAL_HASH_INPUT_MALFORMED)
    else:
        try:
            plain_input = _plain_projection_json_tree(
                projection.canonical_hash_input,
                set(),
            )
        except ValueError as exc:
            _append(errors, str(exc))
        if plain_input is not None:
            report = validate_airline_crypto_canonical_json_value_v01(plain_input)
            for reason in report.validation_errors:
                _append(errors, reason)
            if isinstance(plain_input, dict):
                _append_projection_envelope_mismatch_errors(
                    projection,
                    plain_input,
                    errors,
                )
    return build_airline_crypto_validation_report_v01(errors)


def hash_airline_crypto_ledger_entry_projection_v01(
    projection: AirlineCryptoLedgerEntrySealProjectionV01,
) -> AirlineCryptoLedgerEntryHashV01:
    report = validate_airline_crypto_ledger_entry_projection_v01(projection)
    if report.validation_status != STATUS_PASS:
        raise ValueError(",".join(report.validation_errors))
    plain_projection = airline_crypto_ledger_entry_projection_to_plain_dict_v01(
        projection,
    )
    artifact_hash = sha256_hex_v01(
        canonical_airline_crypto_json_bytes_v01(
            {
                "domain": DOMAIN_LEDGER_ENTRY,
                "projection": plain_projection,
            },
        ),
    )
    return AirlineCryptoLedgerEntryHashV01(
        ledger_index=projection.ledger_index,
        artifact_ref=projection.artifact_id,
        artifact_hash=artifact_hash,
    )


def build_airline_crypto_ledger_hash_chain_v01(
    ledger_item: ledger_contracts.AirlineTransactionArtifactLedgerV01,
    *,
    expected_identity: (
        ledger_contracts.AirlineTransactionArtifactLedgerExpectedIdentityV01
        | None
    ) = None,
) -> AirlineCryptoLedgerHashChainV01:
    projections = build_airline_crypto_ledger_entry_projections_v01(
        ledger_item,
        expected_identity=expected_identity,
    )
    entry_hashes = tuple(
        hash_airline_crypto_ledger_entry_projection_v01(projection)
        for projection in projections
    )
    if len(entry_hashes) != 19:
        raise ValueError(REASON_LEDGER_GEOMETRY_MISMATCH)
    chain_genesis_hash = sha256_hex_v01(
        canonical_airline_crypto_json_bytes_v01(
            {
                "domain": DOMAIN_CHAIN_GENESIS,
                "ledger_id": ledger_item.ledger_id,
                "transaction_id": ledger_item.transaction_id,
                "artifact_count": 19,
            },
        ),
    )
    prior = chain_genesis_hash
    links: list[AirlineCryptoLedgerChainLinkV01] = []
    for expected_index, entry_hash in enumerate(entry_hashes):
        if entry_hash.ledger_index != expected_index:
            raise ValueError(REASON_LEDGER_INDEX_MISMATCH)
        chain_hash = sha256_hex_v01(
            canonical_airline_crypto_json_bytes_v01(
                {
                    "domain": DOMAIN_CHAIN_LINK,
                    "ledger_index": expected_index,
                    "previous_chain_hash": prior,
                    "artifact_hash": entry_hash.artifact_hash,
                },
            ),
        )
        links.append(
            AirlineCryptoLedgerChainLinkV01(
                ledger_index=expected_index,
                artifact_ref=entry_hash.artifact_ref,
                artifact_hash=entry_hash.artifact_hash,
                previous_chain_hash=prior,
                chain_hash=chain_hash,
            ),
        )
        prior = chain_hash
    artifact_refs = tuple(entry_hash.artifact_ref for entry_hash in entry_hashes)
    artifact_hash_values = tuple(
        entry_hash.artifact_hash for entry_hash in entry_hashes
    )
    if len(set(artifact_refs)) != len(artifact_refs):
        raise ValueError(REASON_LEDGER_DUPLICATE_ARTIFACT_REF)
    return AirlineCryptoLedgerHashChainV01(
        ledger_id=ledger_item.ledger_id,
        transaction_id=ledger_item.transaction_id,
        artifact_count=len(entry_hashes),
        artifact_refs=artifact_refs,
        artifact_hashes=artifact_hash_values,
        chain_genesis_hash=chain_genesis_hash,
        chain_head_hash=links[0].chain_hash,
        chain_tail_hash=links[-1].chain_hash,
        chain_links=tuple(links),
    )


def build_airline_crypto_source_package_index_v01(
    *,
    transaction_id: str,
    ordered_source_files: tuple[tuple[str, bytes], ...],
) -> AirlineCryptoSourcePackageIndexV01:
    if type(transaction_id) is not str or not transaction_id:
        raise ValueError(REASON_SOURCE_PACKAGE_TRANSACTION_ID)
    if type(ordered_source_files) is not tuple:
        raise ValueError(REASON_MALFORMED_SOURCE_PACKAGE_INPUT)
    if len(ordered_source_files) != len(REQUIRED_SOURCE_FILE_REFS):
        raise ValueError(REASON_SOURCE_PACKAGE_FILE_COUNT)
    records: list[AirlineCryptoSourceFileHashV01] = []
    seen_refs: set[str] = set()
    for index, row in enumerate(ordered_source_files):
        if type(row) is not tuple or len(row) != 2:
            raise ValueError(REASON_MALFORMED_SOURCE_PACKAGE_INPUT)
        relative_ref, exact_bytes = row
        if relative_ref != REQUIRED_SOURCE_FILE_REFS[index]:
            raise ValueError(REASON_SOURCE_PACKAGE_FILE_ORDER)
        if not _valid_source_ref(relative_ref):
            raise ValueError(REASON_SOURCE_PACKAGE_REF_INVALID)
        if relative_ref in seen_refs:
            raise ValueError(REASON_SOURCE_PACKAGE_DUPLICATE_REF)
        seen_refs.add(relative_ref)
        if type(exact_bytes) is not bytes:
            raise ValueError(REASON_SOURCE_PACKAGE_CONTENT_NOT_BYTES)
        records.append(
            AirlineCryptoSourceFileHashV01(
                relative_ref=relative_ref,
                sha256=sha256_hex_v01(exact_bytes),
            ),
        )
    refs = tuple(record.relative_ref for record in records)
    hashes = tuple(record.sha256 for record in records)
    if refs != REQUIRED_SOURCE_FILE_REFS:
        raise ValueError(REASON_SOURCE_PACKAGE_FILE_ORDER)
    if len(set(refs)) != len(refs):
        raise ValueError(REASON_SOURCE_PACKAGE_DUPLICATE_REF)
    source_package_hash = sha256_hex_v01(
        canonical_airline_crypto_json_bytes_v01(
            {
                "domain": DOMAIN_SOURCE_PACKAGE_INDEX,
                "transaction_id": transaction_id,
                "files": [
                    {
                        "relative_ref": record.relative_ref,
                        "sha256": record.sha256,
                    }
                    for record in records
                ],
            },
        ),
    )
    return AirlineCryptoSourcePackageIndexV01(
        transaction_id=transaction_id,
        source_file_count=len(records),
        ordered_source_file_refs=refs,
        ordered_source_file_hashes=hashes,
        source_file_hash_records=tuple(records),
        source_package_hash=source_package_hash,
        ledger_document_byte_hash=records[0].sha256,
    )


def build_airline_crypto_artifact_seal_manifest_core_v01(
    ledger_item: ledger_contracts.AirlineTransactionArtifactLedgerV01,
    *,
    ordered_source_files: tuple[tuple[str, bytes], ...],
    source_package_ref: str,
    source_audit_status: str,
    secret_scan_passed: bool,
    expected_identity: (
        ledger_contracts.AirlineTransactionArtifactLedgerExpectedIdentityV01
        | None
    ) = None,
) -> AirlineCryptoArtifactSealManifestCoreV01:
    ref_report = validate_airline_crypto_source_package_ref_v01(source_package_ref)
    if ref_report.validation_status != STATUS_PASS:
        raise ValueError(",".join(ref_report.validation_errors))
    if type(source_audit_status) is not str or source_audit_status != STATUS_PASS:
        raise ValueError(REASON_MANIFEST_SOURCE_AUDIT_STATUS_MISMATCH)
    if secret_scan_passed is not True:
        raise ValueError(REASON_MANIFEST_SECRET_SCAN_BOUNDARY_MISMATCH)
    chain = build_airline_crypto_ledger_hash_chain_v01(
        ledger_item,
        expected_identity=expected_identity,
    )
    source_index = build_airline_crypto_source_package_index_v01(
        transaction_id=chain.transaction_id,
        ordered_source_files=ordered_source_files,
    )
    if source_index.transaction_id != chain.transaction_id:
        raise ValueError(REASON_MANIFEST_IDENTITY_MISMATCH)
    actual_dependency_edges, actual_root_finals = _accepted_ledger_geometry(
        ledger_item,
    )
    core = AirlineCryptoArtifactSealManifestCoreV01(
        seal_id=f"{SEAL_VERSION}:{source_index.source_package_hash}",
        seal_version=SEAL_VERSION,
        transaction_id=chain.transaction_id,
        ledger_id=chain.ledger_id,
        source_package_ref=source_package_ref,
        canonicalization_profile_id=CANONICALIZATION_PROFILE_ID,
        hash_algorithm=HASH_ALGORITHM,
        hash_encoding=HASH_ENCODING,
        ledger_entry_count=chain.artifact_count,
        dependency_edge_count=actual_dependency_edges,
        root_final_count=actual_root_finals,
        ordered_artifact_refs=chain.artifact_refs,
        ordered_artifact_hashes=chain.artifact_hashes,
        chain_genesis_hash=chain.chain_genesis_hash,
        chain_head_hash=chain.chain_head_hash,
        chain_tail_hash=chain.chain_tail_hash,
        source_file_count=source_index.source_file_count,
        ordered_source_file_refs=source_index.ordered_source_file_refs,
        ordered_source_file_hashes=source_index.ordered_source_file_hashes,
        source_package_hash=source_index.source_package_hash,
        ledger_document_byte_hash=source_index.ledger_document_byte_hash,
        previous_manifest_ref=None,
        signature_placeholder_present=True,
        signature_verified=False,
        source_audit_status=STATUS_PASS,
        secret_scan_passed=True,
        raw_secret_included=False,
        seal_created_authority_count=0,
        seal_created_permission_count=0,
        seal_created_action_count=0,
        real_world_effects_count=0,
    )
    report = validate_airline_crypto_artifact_seal_manifest_core_v01(core)
    if report.validation_status != STATUS_PASS:
        raise ValueError(",".join(report.validation_errors))
    return core


def validate_airline_crypto_artifact_seal_manifest_core_v01(
    core: object,
) -> AirlineCryptoArtifactSealValidationReportV01:
    errors: list[str] = []
    if type(core) is not AirlineCryptoArtifactSealManifestCoreV01:
        return build_airline_crypto_validation_report_v01(
            [REASON_MANIFEST_CORE_WRONG_TYPE],
        )
    try:
        _append_manifest_core_errors(core, errors)
    except (TypeError, AttributeError, KeyError, IndexError, RecursionError, ValueError):
        _append(errors, REASON_MANIFEST_CORE_WRONG_TYPE)
    return build_airline_crypto_validation_report_v01(errors)


def airline_crypto_artifact_seal_manifest_core_to_plain_dict_v01(
    core: AirlineCryptoArtifactSealManifestCoreV01,
) -> dict[str, object]:
    report = validate_airline_crypto_artifact_seal_manifest_core_v01(core)
    if report.validation_status != STATUS_PASS:
        raise ValueError(",".join(report.validation_errors))
    return _manifest_core_plain_dict(core)


def hash_airline_crypto_artifact_seal_manifest_core_v01(
    core: AirlineCryptoArtifactSealManifestCoreV01,
) -> str:
    plain_core = airline_crypto_artifact_seal_manifest_core_to_plain_dict_v01(
        core,
    )
    return sha256_hex_v01(
        canonical_airline_crypto_json_bytes_v01(
            {
                "domain": DOMAIN_MANIFEST_CORE,
                "manifest_core": plain_core,
            },
        ),
    )


def build_airline_crypto_artifact_seal_signature_placeholder_v01() -> (
    AirlineCryptoArtifactSealSignaturePlaceholderV01
):
    return AirlineCryptoArtifactSealSignaturePlaceholderV01(
        mode=SIGNATURE_MODE_UNSIGNED_PLACEHOLDER,
        algorithm=SIGNATURE_ALGORITHM_NONE,
        key_id="",
        value="",
        verified=False,
    )


def validate_airline_crypto_artifact_seal_signature_placeholder_v01(
    signature: object,
) -> AirlineCryptoArtifactSealValidationReportV01:
    errors: list[str] = []
    if type(signature) is not AirlineCryptoArtifactSealSignaturePlaceholderV01:
        return build_airline_crypto_validation_report_v01(
            [REASON_SIGNATURE_PLACEHOLDER_WRONG_TYPE],
        )
    try:
        if (
            signature.mode != SIGNATURE_MODE_UNSIGNED_PLACEHOLDER
            or signature.algorithm != SIGNATURE_ALGORITHM_NONE
            or signature.key_id != ""
            or signature.value != ""
            or signature.verified is not False
        ):
            _append(errors, REASON_SIGNATURE_PLACEHOLDER_FIELD_MISMATCH)
        for value in (
            signature.mode,
            signature.algorithm,
            signature.key_id,
            signature.value,
        ):
            if type(value) is not str or _contains_lone_surrogate(value):
                _append(errors, REASON_SIGNATURE_PLACEHOLDER_FIELD_MISMATCH)
        if type(signature.verified) is not bool:
            _append(errors, REASON_SIGNATURE_PLACEHOLDER_FIELD_MISMATCH)
    except (TypeError, AttributeError, KeyError, IndexError, RecursionError, ValueError):
        _append(errors, REASON_SIGNATURE_PLACEHOLDER_FIELD_MISMATCH)
    return build_airline_crypto_validation_report_v01(errors)


def build_airline_crypto_artifact_seal_envelope_v01(
    manifest_core: AirlineCryptoArtifactSealManifestCoreV01,
) -> AirlineCryptoArtifactSealEnvelopeV01:
    report = validate_airline_crypto_artifact_seal_manifest_core_v01(
        manifest_core,
    )
    if report.validation_status != STATUS_PASS:
        raise ValueError(",".join(report.validation_errors))
    return AirlineCryptoArtifactSealEnvelopeV01(
        manifest_core=manifest_core,
        manifest_core_hash=hash_airline_crypto_artifact_seal_manifest_core_v01(
            manifest_core,
        ),
        signature=build_airline_crypto_artifact_seal_signature_placeholder_v01(),
    )


def validate_airline_crypto_artifact_seal_envelope_contract_v01(
    envelope: object,
) -> AirlineCryptoArtifactSealValidationReportV01:
    errors: list[str] = []
    if type(envelope) is not AirlineCryptoArtifactSealEnvelopeV01:
        return build_airline_crypto_validation_report_v01(
            [REASON_ENVELOPE_MALFORMED],
        )
    try:
        core_report = validate_airline_crypto_artifact_seal_manifest_core_v01(
            envelope.manifest_core,
        )
        for reason in core_report.validation_errors:
            _append(errors, reason)
        hash_report = validate_sha256_hex_v01(envelope.manifest_core_hash)
        if hash_report.validation_status != STATUS_PASS:
            _append(errors, REASON_INVALID_SHA256_HEX)
        elif (
            hash_airline_crypto_artifact_seal_manifest_core_v01(
                envelope.manifest_core,
            )
            != envelope.manifest_core_hash
        ):
            _append(errors, REASON_MANIFEST_CORE_HASH_MISMATCH)
        signature_report = (
            validate_airline_crypto_artifact_seal_signature_placeholder_v01(
                envelope.signature,
            )
        )
        for reason in signature_report.validation_errors:
            _append(errors, reason)
        if (
            envelope.manifest_core.signature_placeholder_present is not True
            or envelope.manifest_core.signature_verified is not False
            or (
                type(envelope.signature)
                is AirlineCryptoArtifactSealSignaturePlaceholderV01
                and envelope.signature.verified is not False
            )
        ):
            _append(errors, REASON_MANIFEST_SIGNATURE_FLAG_MISMATCH)
    except (TypeError, AttributeError, KeyError, IndexError, RecursionError, ValueError):
        _append(errors, REASON_ENVELOPE_MALFORMED)
    return build_airline_crypto_validation_report_v01(errors)


def _unique_reasons(reasons: tuple[str, ...] | list[str]) -> tuple[str, ...]:
    output: list[str] = []
    for reason in reasons:
        if type(reason) is str and reason and reason not in output:
            output.append(reason)
        elif type(reason) is not str or not reason:
            if REASON_MALFORMED_VALIDATION_ERRORS not in output:
                output.append(REASON_MALFORMED_VALIDATION_ERRORS)
    return tuple(output)


def _append(errors: list[str], reason: str) -> None:
    if reason not in errors:
        errors.append(reason)


def _freeze_manifest_string_sequence(value: object, reason: str) -> tuple[str, ...]:
    if type(value) not in (tuple, list):
        raise ValueError(reason)
    return tuple(value)


def _exact_zero(value: object) -> bool:
    return type(value) is int and value == 0


def _non_empty_string(value: object) -> bool:
    return type(value) is str and bool(value) and not _contains_lone_surrogate(value)


def _valid_source_package_ref(value: object) -> bool:
    if not _non_empty_string(value):
        return False
    assert type(value) is str
    if value in (".", ".."):
        return False
    if "/" in value or "\\" in value:
        return False
    if value.startswith("~"):
        return False
    if len(value) >= 2 and value[1] == ":":
        return False
    return True


def _accepted_ledger_geometry(
    ledger_item: ledger_contracts.AirlineTransactionArtifactLedgerV01,
) -> tuple[int, int]:
    entries = ledger_item.entries
    actual_dependency_edges = sum(len(entry.depends_on) for entry in entries)
    actual_root_finals = sum(
        1
        for entry in entries
        if entry.artifact_type
        in (
            ledger_contracts.ARTIFACT_CLIENT_ROOT_FINAL,
            ledger_contracts.ARTIFACT_AIRLINE_ROOT_FINAL,
            ledger_contracts.ARTIFACT_BANK_ROOT_FINAL,
        )
    )
    if actual_dependency_edges != 29 or actual_root_finals != 3:
        raise ValueError(REASON_MANIFEST_LEDGER_GEOMETRY_MISMATCH)
    return actual_dependency_edges, actual_root_finals


def _append_manifest_core_errors(
    core: AirlineCryptoArtifactSealManifestCoreV01,
    errors: list[str],
) -> None:
    if (
        core.seal_version != SEAL_VERSION
        or core.canonicalization_profile_id != CANONICALIZATION_PROFILE_ID
        or core.hash_algorithm != HASH_ALGORITHM
        or core.hash_encoding != HASH_ENCODING
    ):
        _append(errors, REASON_MANIFEST_VERSION_PROFILE_ALGORITHM_MISMATCH)
    for value in (core.transaction_id, core.ledger_id):
        if not _non_empty_string(value):
            _append(errors, REASON_MANIFEST_IDENTITY_MISMATCH)
    source_ref_report = validate_airline_crypto_source_package_ref_v01(
        core.source_package_ref,
    )
    for reason in source_ref_report.validation_errors:
        _append(errors, reason)
    if (
        type(core.source_package_hash) is not str
        or validate_sha256_hex_v01(core.source_package_hash).validation_status
        != STATUS_PASS
        or core.seal_id != f"{SEAL_VERSION}:{core.source_package_hash}"
    ):
        _append(errors, REASON_MANIFEST_IDENTITY_MISMATCH)
    if (
        type(core.ledger_entry_count) is not int
        or core.ledger_entry_count != 19
        or type(core.dependency_edge_count) is not int
        or core.dependency_edge_count != 29
        or type(core.root_final_count) is not int
        or core.root_final_count != 3
    ):
        _append(errors, REASON_MANIFEST_LEDGER_GEOMETRY_MISMATCH)
    if type(core.source_file_count) is not int or core.source_file_count != 9:
        _append(errors, REASON_MANIFEST_SOURCE_REF_HASH_GEOMETRY_MISMATCH)
    _append_artifact_binding_errors(core, errors)
    _append_source_binding_errors(core, errors)
    for digest in (
        core.chain_genesis_hash,
        core.chain_head_hash,
        core.chain_tail_hash,
    ):
        if validate_sha256_hex_v01(digest).validation_status != STATUS_PASS:
            _append(errors, REASON_MANIFEST_CHAIN_HASH_MISMATCH)
    if core.previous_manifest_ref is not None:
        _append(errors, REASON_MANIFEST_PREVIOUS_REF_MISMATCH)
    if (
        type(core.signature_placeholder_present) is not bool
        or core.signature_placeholder_present is not True
        or type(core.signature_verified) is not bool
        or core.signature_verified is not False
    ):
        _append(errors, REASON_MANIFEST_SIGNATURE_FLAG_MISMATCH)
    if core.source_audit_status != STATUS_PASS:
        _append(errors, REASON_MANIFEST_SOURCE_AUDIT_STATUS_MISMATCH)
    if (
        type(core.secret_scan_passed) is not bool
        or core.secret_scan_passed is not True
        or type(core.raw_secret_included) is not bool
        or core.raw_secret_included is not False
    ):
        _append(errors, REASON_MANIFEST_SECRET_SCAN_BOUNDARY_MISMATCH)
    if (
        not _exact_zero(core.seal_created_authority_count)
        or not _exact_zero(core.seal_created_permission_count)
        or not _exact_zero(core.seal_created_action_count)
        or not _exact_zero(core.real_world_effects_count)
    ):
        _append(errors, REASON_MANIFEST_NONZERO_COUNTER)
    plain = _manifest_core_plain_dict(core)
    if tuple(plain.keys()) != MANIFEST_CORE_FIELD_NAMES:
        _append(errors, REASON_MANIFEST_CORE_WRONG_TYPE)
    canonical_report = validate_airline_crypto_canonical_json_value_v01(plain)
    for reason in canonical_report.validation_errors:
        _append(errors, reason)


def _append_artifact_binding_errors(
    core: AirlineCryptoArtifactSealManifestCoreV01,
    errors: list[str],
) -> None:
    if (
        type(core.ordered_artifact_refs) is not tuple
        or type(core.ordered_artifact_hashes) is not tuple
        or len(core.ordered_artifact_refs) != 19
        or len(core.ordered_artifact_hashes) != 19
    ):
        _append(errors, REASON_MANIFEST_ARTIFACT_REF_HASH_GEOMETRY_MISMATCH)
        return
    if len(set(core.ordered_artifact_refs)) != len(core.ordered_artifact_refs):
        _append(errors, REASON_MANIFEST_DUPLICATE_ARTIFACT_REF)
    for ref in core.ordered_artifact_refs:
        if not _non_empty_string(ref):
            _append(errors, REASON_MANIFEST_INVALID_ARTIFACT_REF)
            break
    for artifact_hash in core.ordered_artifact_hashes:
        if validate_sha256_hex_v01(artifact_hash).validation_status != STATUS_PASS:
            _append(errors, REASON_MANIFEST_INVALID_ARTIFACT_HASH)
            break
    if (
        len(core.ordered_artifact_hashes) == 19
        and all(
            validate_sha256_hex_v01(value).validation_status == STATUS_PASS
            for value in core.ordered_artifact_hashes
        )
    ):
        expected_genesis, expected_head, expected_tail = _expected_chain_hashes(
            core,
        )
        if (
            core.chain_genesis_hash != expected_genesis
            or core.chain_head_hash != expected_head
            or core.chain_tail_hash != expected_tail
        ):
            _append(errors, REASON_MANIFEST_CHAIN_HASH_MISMATCH)


def _append_source_binding_errors(
    core: AirlineCryptoArtifactSealManifestCoreV01,
    errors: list[str],
) -> None:
    if (
        type(core.ordered_source_file_refs) is not tuple
        or type(core.ordered_source_file_hashes) is not tuple
        or len(core.ordered_source_file_refs) != len(REQUIRED_SOURCE_FILE_REFS)
        or len(core.ordered_source_file_hashes) != len(REQUIRED_SOURCE_FILE_REFS)
    ):
        _append(errors, REASON_MANIFEST_SOURCE_REF_HASH_GEOMETRY_MISMATCH)
        return
    if core.ordered_source_file_refs != REQUIRED_SOURCE_FILE_REFS:
        _append(errors, REASON_MANIFEST_SOURCE_FILE_ORDER_MISMATCH)
    if len(set(core.ordered_source_file_refs)) != len(core.ordered_source_file_refs):
        _append(errors, REASON_MANIFEST_DUPLICATE_SOURCE_REF)
    for source_hash in core.ordered_source_file_hashes:
        if validate_sha256_hex_v01(source_hash).validation_status != STATUS_PASS:
            _append(errors, REASON_MANIFEST_INVALID_SOURCE_HASH)
            break
    if validate_sha256_hex_v01(core.source_package_hash).validation_status != STATUS_PASS:
        _append(errors, REASON_MANIFEST_INVALID_SOURCE_HASH)
    if (
        validate_sha256_hex_v01(core.ledger_document_byte_hash).validation_status
        != STATUS_PASS
    ):
        _append(errors, REASON_MANIFEST_INVALID_SOURCE_HASH)
    elif (
        core.ordered_source_file_refs
        and core.ordered_source_file_refs[0]
        == "airline_transaction_artifact_ledger.json"
        and core.ledger_document_byte_hash != core.ordered_source_file_hashes[0]
    ):
        _append(errors, REASON_MANIFEST_LEDGER_DOCUMENT_BYTE_HASH_MISMATCH)
    if (
        core.ordered_source_file_refs == REQUIRED_SOURCE_FILE_REFS
        and len(core.ordered_source_file_hashes) == len(REQUIRED_SOURCE_FILE_REFS)
        and all(
            validate_sha256_hex_v01(value).validation_status == STATUS_PASS
            for value in core.ordered_source_file_hashes
        )
    ):
        expected_hash = _expected_source_package_hash_from_core(core)
        if core.source_package_hash != expected_hash:
            _append(errors, REASON_MANIFEST_INVALID_SOURCE_HASH)


def _manifest_core_plain_dict(
    core: AirlineCryptoArtifactSealManifestCoreV01,
) -> dict[str, object]:
    return {
        "seal_id": core.seal_id,
        "seal_version": core.seal_version,
        "transaction_id": core.transaction_id,
        "ledger_id": core.ledger_id,
        "source_package_ref": core.source_package_ref,
        "canonicalization_profile_id": core.canonicalization_profile_id,
        "hash_algorithm": core.hash_algorithm,
        "hash_encoding": core.hash_encoding,
        "ledger_entry_count": core.ledger_entry_count,
        "dependency_edge_count": core.dependency_edge_count,
        "root_final_count": core.root_final_count,
        "ordered_artifact_refs": list(core.ordered_artifact_refs),
        "ordered_artifact_hashes": list(core.ordered_artifact_hashes),
        "chain_genesis_hash": core.chain_genesis_hash,
        "chain_head_hash": core.chain_head_hash,
        "chain_tail_hash": core.chain_tail_hash,
        "source_file_count": core.source_file_count,
        "ordered_source_file_refs": list(core.ordered_source_file_refs),
        "ordered_source_file_hashes": list(core.ordered_source_file_hashes),
        "source_package_hash": core.source_package_hash,
        "ledger_document_byte_hash": core.ledger_document_byte_hash,
        "previous_manifest_ref": core.previous_manifest_ref,
        "signature_placeholder_present": core.signature_placeholder_present,
        "signature_verified": core.signature_verified,
        "source_audit_status": core.source_audit_status,
        "secret_scan_passed": core.secret_scan_passed,
        "raw_secret_included": core.raw_secret_included,
        "seal_created_authority_count": core.seal_created_authority_count,
        "seal_created_permission_count": core.seal_created_permission_count,
        "seal_created_action_count": core.seal_created_action_count,
        "real_world_effects_count": core.real_world_effects_count,
    }


def _expected_chain_hashes(
    core: AirlineCryptoArtifactSealManifestCoreV01,
) -> tuple[str, str, str]:
    genesis = sha256_hex_v01(
        canonical_airline_crypto_json_bytes_v01(
            {
                "domain": DOMAIN_CHAIN_GENESIS,
                "ledger_id": core.ledger_id,
                "transaction_id": core.transaction_id,
                "artifact_count": 19,
            },
        ),
    )
    prior = genesis
    first_link = ""
    for ledger_index, artifact_hash in enumerate(core.ordered_artifact_hashes):
        current = sha256_hex_v01(
            canonical_airline_crypto_json_bytes_v01(
                {
                    "domain": DOMAIN_CHAIN_LINK,
                    "ledger_index": ledger_index,
                    "previous_chain_hash": prior,
                    "artifact_hash": artifact_hash,
                },
            ),
        )
        if ledger_index == 0:
            first_link = current
        prior = current
    return genesis, first_link, prior


def _expected_source_package_hash_from_core(
    core: AirlineCryptoArtifactSealManifestCoreV01,
) -> str:
    return sha256_hex_v01(
        canonical_airline_crypto_json_bytes_v01(
            {
                "domain": DOMAIN_SOURCE_PACKAGE_INDEX,
                "transaction_id": core.transaction_id,
                "files": [
                    {
                        "relative_ref": relative_ref,
                        "sha256": source_hash,
                    }
                    for relative_ref, source_hash in zip(
                        core.ordered_source_file_refs,
                        core.ordered_source_file_hashes,
                    )
                ],
            },
        ),
    )


def _validate_canonical_value(
    value: object,
    errors: list[str],
    active_container_ids: set[int],
) -> None:
    if type(value) is bool or value is None:
        return
    if type(value) is str:
        if _contains_lone_surrogate(value):
            _append(errors, REASON_LONE_SURROGATE)
        return
    if type(value) is int:
        if value < SIGNED_INT64_MIN or value > SIGNED_INT64_MAX:
            _append(errors, REASON_INTEGER_OUT_OF_RANGE)
        return
    if type(value) is float:
        _append(errors, REASON_FLOAT_FORBIDDEN)
        return
    if type(value) in (bytes, bytearray):
        _append(errors, REASON_BYTES_FORBIDDEN)
        return
    if type(value) is tuple:
        _append(errors, REASON_TUPLE_FORBIDDEN)
        return
    if type(value) is MappingProxyType:
        _append(errors, REASON_MAPPING_PROXY_FORBIDDEN)
        return
    if type(value) in (set, frozenset):
        _append(errors, REASON_SET_FORBIDDEN)
        return
    if isinstance(value, Enum):
        _append(errors, REASON_ENUM_FORBIDDEN)
        return
    if is_dataclass(value) and not isinstance(value, type):
        _append(errors, REASON_DATACLASS_FORBIDDEN)
        return
    if type(value) is list:
        value_id = id(value)
        if value_id in active_container_ids:
            _append(errors, REASON_CYCLIC_VALUE)
            return
        active_container_ids.add(value_id)
        for item in value:
            _validate_canonical_value(item, errors, active_container_ids)
        active_container_ids.remove(value_id)
        return
    if type(value) is dict:
        value_id = id(value)
        if value_id in active_container_ids:
            _append(errors, REASON_CYCLIC_VALUE)
            return
        active_container_ids.add(value_id)
        for key, item in value.items():
            if type(key) is not str:
                _append(errors, REASON_NON_STRING_KEY)
            elif _contains_lone_surrogate(key):
                _append(errors, REASON_LONE_SURROGATE)
            _validate_canonical_value(item, errors, active_container_ids)
        active_container_ids.remove(value_id)
        return
    _append(errors, REASON_ARBITRARY_OBJECT_FORBIDDEN)


def _contains_lone_surrogate(value: str) -> bool:
    return any(0xD800 <= ord(character) <= 0xDFFF for character in value)


def _reject_duplicate_json_pairs(
    pairs: list[tuple[str, object]],
) -> dict[str, object]:
    output: dict[str, object] = {}
    for key, value in pairs:
        if key in output:
            raise ValueError(REASON_DUPLICATE_JSON_KEY)
        output[key] = value
    return output


def _reject_json_constant(value: str) -> None:
    raise ValueError(REASON_JSON_CONSTANT_FORBIDDEN)


def _freeze_projected_json(value: object, active_container_ids: set[int]) -> object:
    if type(value) is bool or value is None or type(value) in (str, int):
        return value
    if type(value) in (dict, MappingProxyType):
        value_id = id(value)
        if value_id in active_container_ids:
            raise ValueError(REASON_CYCLIC_VALUE)
        active_container_ids.add(value_id)
        frozen: dict[str, object] = {}
        for key, item in value.items():
            if type(key) is not str:
                raise ValueError(REASON_UNSUPPORTED_LEDGER_CANONICAL_SOURCE_VALUE)
            frozen[key] = _freeze_projected_json(item, active_container_ids)
        active_container_ids.remove(value_id)
        return MappingProxyType(frozen)
    if type(value) in (tuple, list):
        value_id = id(value)
        if value_id in active_container_ids:
            raise ValueError(REASON_CYCLIC_VALUE)
        active_container_ids.add(value_id)
        frozen_tuple = tuple(
            _freeze_projected_json(item, active_container_ids)
            for item in value
        )
        active_container_ids.remove(value_id)
        return frozen_tuple
    raise ValueError(REASON_UNSUPPORTED_LEDGER_CANONICAL_SOURCE_VALUE)


def _plain_ledger_json_tree(
    value: object,
    active_container_ids: set[int] | None = None,
) -> object:
    active = active_container_ids if active_container_ids is not None else set()
    if type(value) is bool or value is None or type(value) in (str, int):
        return value
    if type(value) is float:
        raise ValueError(REASON_FLOAT_FORBIDDEN)
    if type(value) in (bytes, bytearray):
        raise ValueError(REASON_BYTES_FORBIDDEN)
    if type(value) in (set, frozenset):
        raise ValueError(REASON_SET_FORBIDDEN)
    if isinstance(value, Enum):
        raise ValueError(REASON_ENUM_FORBIDDEN)
    if is_dataclass(value) and not isinstance(value, type):
        raise ValueError(REASON_DATACLASS_FORBIDDEN)
    if isinstance(value, MappingABC):
        value_id = id(value)
        if value_id in active:
            raise ValueError(REASON_CYCLIC_VALUE)
        active.add(value_id)
        output: dict[str, object] = {}
        for key, item in value.items():
            if type(key) is not str:
                raise ValueError(REASON_NON_STRING_KEY)
            output[key] = _plain_ledger_json_tree(item, active)
        active.remove(value_id)
        return output
    if type(value) in (tuple, list):
        value_id = id(value)
        if value_id in active:
            raise ValueError(REASON_CYCLIC_VALUE)
        active.add(value_id)
        output_list = [_plain_ledger_json_tree(item, active) for item in value]
        active.remove(value_id)
        return output_list
    raise ValueError(REASON_UNSUPPORTED_LEDGER_CANONICAL_SOURCE_VALUE)


def _plain_projection_json_tree(value: object, active_container_ids: set[int]) -> object:
    if type(value) is bool or value is None or type(value) in (str, int):
        return value
    if type(value) is float:
        raise ValueError(REASON_FLOAT_FORBIDDEN)
    if type(value) in (bytes, bytearray):
        raise ValueError(REASON_BYTES_FORBIDDEN)
    if type(value) in (set, frozenset):
        raise ValueError(REASON_SET_FORBIDDEN)
    if isinstance(value, Enum):
        raise ValueError(REASON_ENUM_FORBIDDEN)
    if is_dataclass(value) and not isinstance(value, type):
        raise ValueError(REASON_DATACLASS_FORBIDDEN)
    if type(value) in (dict, MappingProxyType):
        value_id = id(value)
        if value_id in active_container_ids:
            raise ValueError(REASON_CYCLIC_VALUE)
        active_container_ids.add(value_id)
        output: dict[str, object] = {}
        for key, item in value.items():
            if type(key) is not str:
                raise ValueError(REASON_NON_STRING_KEY)
            output[key] = _plain_projection_json_tree(item, active_container_ids)
        active_container_ids.remove(value_id)
        return output
    if type(value) in (tuple, list):
        value_id = id(value)
        if value_id in active_container_ids:
            raise ValueError(REASON_CYCLIC_VALUE)
        active_container_ids.add(value_id)
        output_list = [
            _plain_projection_json_tree(item, active_container_ids)
            for item in value
        ]
        active_container_ids.remove(value_id)
        return output_list
    raise ValueError(REASON_UNSUPPORTED_LEDGER_CANONICAL_SOURCE_VALUE)


def _require_valid_accepted_ledger(
    ledger_item: ledger_contracts.AirlineTransactionArtifactLedgerV01,
    *,
    expected_identity: (
        ledger_contracts.AirlineTransactionArtifactLedgerExpectedIdentityV01
        | None
    ) = None,
) -> None:
    errors: list[str] = []
    if type(ledger_item) is not ledger_contracts.AirlineTransactionArtifactLedgerV01:
        raise ValueError(REASON_MALFORMED_LEDGER)
    if (
        expected_identity is not None
        and type(expected_identity)
        is not ledger_contracts.AirlineTransactionArtifactLedgerExpectedIdentityV01
    ):
        raise ValueError(REASON_EXPECTED_IDENTITY_WRONG_TYPE)
    try:
        report = ledger_contracts.validate_airline_transaction_artifact_ledger_v01(
            ledger_item,
            expected_identity=expected_identity,
        )
    except (TypeError, AttributeError, ValueError, KeyError, IndexError, RecursionError) as exc:
        raise ValueError(REASON_LEDGER_VALIDATION_FAILED) from exc
    if report.validation_status != ledger_contracts.STATUS_PASS:
        _append(errors, REASON_LEDGER_VALIDATION_FAILED)
    if ledger_item.validation_status != ledger_contracts.STATUS_PASS:
        _append(errors, REASON_LEDGER_STORED_STATUS_FAILED)
    if ledger_item.validation_errors != ():
        _append(errors, REASON_LEDGER_STORED_ERRORS_MALFORMED)
    if errors:
        raise ValueError(",".join(errors))
    entries = ledger_item.entries
    if type(entries) is not tuple:
        _append(errors, REASON_LEDGER_GEOMETRY_MISMATCH)
    else:
        _append_ledger_shape_errors(ledger_item, entries, errors)
    if errors:
        raise ValueError(",".join(errors))


def _append_projection_envelope_mismatch_errors(
    projection: AirlineCryptoLedgerEntrySealProjectionV01,
    canonical_hash_input: dict[str, object],
    errors: list[str],
) -> None:
    expected = {
        "ledger_index": projection.ledger_index,
        "event_type": projection.event_type,
        "artifact_type": projection.artifact_type,
        "artifact_id": projection.artifact_id,
        "transaction_id": projection.transaction_id,
        "root_owner": projection.root_owner,
        "created_by": projection.created_by,
        "authority_class": projection.authority_class,
        "evidence_class": projection.evidence_class,
        "depends_on": list(projection.depends_on),
    }
    missing = object()
    for key, expected_value in expected.items():
        actual_value = canonical_hash_input.get(key, missing)
        if (
            actual_value is missing
            or type(actual_value) is not type(expected_value)
            or actual_value != expected_value
        ):
            _append(errors, REASON_PROJECTION_CANONICAL_HASH_INPUT_FIELD_MISMATCH)
            return


def _append_ledger_shape_errors(
    ledger_item: ledger_contracts.AirlineTransactionArtifactLedgerV01,
    entries: tuple[object, ...],
    errors: list[str],
) -> None:
    if (
        len(entries) != 19
        or ledger_item.entry_count != 19
        or ledger_item.dependency_edge_count != 29
        or ledger_item.root_final_count != 3
    ):
        _append(errors, REASON_LEDGER_GEOMETRY_MISMATCH)
    if not all(
        type(entry) is ledger_contracts.AirlineTransactionArtifactLedgerEntryV01
        for entry in entries
    ):
        _append(errors, REASON_MALFORMED_LEDGER)
        return
    typed_entries = tuple(entries)
    actual_edges = sum(len(entry.depends_on) for entry in typed_entries)
    root_final_types = tuple(
        entry.artifact_type
        for entry in typed_entries
        if entry.artifact_type
        in (
            ledger_contracts.ARTIFACT_CLIENT_ROOT_FINAL,
            ledger_contracts.ARTIFACT_AIRLINE_ROOT_FINAL,
            ledger_contracts.ARTIFACT_BANK_ROOT_FINAL,
        )
    )
    if actual_edges != 29 or len(root_final_types) != 3:
        _append(errors, REASON_LEDGER_GEOMETRY_MISMATCH)
    if (
        root_final_types.count(ledger_contracts.ARTIFACT_CLIENT_ROOT_FINAL) != 1
        or root_final_types.count(ledger_contracts.ARTIFACT_AIRLINE_ROOT_FINAL) != 1
        or root_final_types.count(ledger_contracts.ARTIFACT_BANK_ROOT_FINAL) != 1
    ):
        _append(errors, REASON_LEDGER_ROOT_FINAL_SET_MISMATCH)
    if (
        tuple(entry.artifact_type for entry in typed_entries)
        != ledger_contracts.EXPECTED_ARTIFACT_TYPE_SEQUENCE
    ):
        _append(errors, REASON_LEDGER_ARTIFACT_SEQUENCE_MISMATCH)
    if tuple(entry.ledger_index for entry in typed_entries) != tuple(range(19)):
        _append(errors, REASON_LEDGER_INDEX_MISMATCH)
    transaction_ids = {entry.transaction_id for entry in typed_entries}
    if transaction_ids != {ledger_item.transaction_id}:
        _append(errors, REASON_LEDGER_TRANSACTION_MISMATCH)
    artifact_ids = tuple(entry.artifact_id for entry in typed_entries)
    if len(set(artifact_ids)) != len(artifact_ids):
        _append(errors, REASON_LEDGER_DUPLICATE_ARTIFACT_REF)
    if (
        ledger_item.ledger_created_authority_count != 0
        or ledger_item.ledger_created_permission_count != 0
        or ledger_item.ledger_created_action_count != 0
        or ledger_item.provider_called_count != 0
        or ledger_item.network_used_count != 0
        or ledger_item.gemini_called_count != 0
        or ledger_item.real_world_effects_count != 0
    ):
        _append(errors, REASON_LEDGER_SOURCE_BOUNDARY_MISMATCH)
    for entry in typed_entries:
        if (
            entry.raw_secret_included is not False
            or entry.raw_provider_text_included is not False
            or entry.ledger_created_authority is not False
            or entry.ledger_created_permission is not False
            or entry.ledger_created_action is not False
            or entry.real_world_effects_count != 0
        ):
            _append(errors, REASON_LEDGER_SOURCE_BOUNDARY_MISMATCH)


def _valid_source_ref(value: str) -> bool:
    return (
        type(value) is str
        and value
        and value not in (".", "..")
        and "/" not in value
        and "\\" not in value
    )
