"""Pure Airline deterministic sealed-trace reconstruction.

This module verifies an already accepted in-memory trace. It is not transaction
re-execution: it performs no semantic rerun, Corridor execution, Ledger
recollection, Crypto collection, provider/network/Gemini call, package or file
I/O, or real-world effect. It creates no authority, permission, action, packet,
receipt, or FinalOutput and makes no Root-signature or signer-authentication
claim. This is Airline-domain code, not universal Hedgehog OS core.
"""

from __future__ import annotations

from collections.abc import Mapping
from dataclasses import dataclass

from hedgehog.domains.airline import crypto_artifact_seal_collector_v01 as crypto_collector
from hedgehog.domains.airline import crypto_artifact_seal_v01 as crypto_contracts
from hedgehog.domains.airline import transaction_artifact_ledger_v01 as ledger_contracts


MODULE_ID = "airline_sealed_trace_replay_v01"
SLICE_ID = "airline_sealed_trace_replay_v01_slice_b"
REPLAY_VERSION = "airline_sealed_trace_replay_v01"
REPLAY_ID_PREFIX = "airline_sealed_trace_replay_v01"
EXPECTED_IDENTITY_ROLE = (
    "verifier_contract_adapter_after_independent_ledger_audit"
)

STATUS_PASS = "PASS"
STATUS_FAIL_CLOSED = "FAIL_CLOSED"

MANIFEST_ARTIFACT_REF = "airline_crypto_artifact_seal_manifest_v01.json"
STORED_VERIFICATION_ARTIFACT_REF = (
    "airline_crypto_artifact_seal_verification_v01.json"
)

SOURCE_FILE_COUNT = 9
CRITICAL_PACKAGE_FILE_COUNT = 11
LEDGER_ENTRY_COUNT = 19
DEPENDENCY_EDGE_COUNT = 29
ROOT_FINAL_COUNT = 3
TIMELINE_ROW_COUNT = 19

ROOT_FINAL_ARTIFACT_TYPES = (
    ledger_contracts.ARTIFACT_CLIENT_ROOT_FINAL,
    ledger_contracts.ARTIFACT_AIRLINE_ROOT_FINAL,
    ledger_contracts.ARTIFACT_BANK_ROOT_FINAL,
)

PACKET_ARTIFACT_TYPES = (
    ledger_contracts.ARTIFACT_AIRLINE_OFFER_PACKET,
    ledger_contracts.ARTIFACT_AIRLINE_HOLD_PACKET,
    ledger_contracts.ARTIFACT_CLIENT_PURCHASE_INTENT,
    ledger_contracts.ARTIFACT_BANK_PAYMENT_AUTHORIZATION,
    ledger_contracts.ARTIFACT_AIRLINE_TICKET_ISSUE_INTENT,
)

RECEIPT_ARTIFACT_TYPES = (
    ledger_contracts.ARTIFACT_AIRLINE_OFFER_HOLD_RECEIPT,
    ledger_contracts.ARTIFACT_MOCK_TICKET_RECEIPT,
    ledger_contracts.ARTIFACT_MOCK_PURCHASE_RECEIPT,
)

REASON_PACKAGE_SNAPSHOT_WRONG_TYPE = "package_snapshot_wrong_type"
REASON_SOURCE_PACKAGE_REF_INVALID = "source_package_ref_invalid"
REASON_SOURCE_FILE_SNAPSHOT_MALFORMED = "source_file_snapshot_malformed"
REASON_SOURCE_FILE_ORDER_MISMATCH = "source_file_order_mismatch"
REASON_MANIFEST_ARTIFACT_REF_MISMATCH = "manifest_artifact_ref_mismatch"
REASON_MANIFEST_BYTES_MALFORMED = "manifest_bytes_malformed"
REASON_STORED_VERIFICATION_ARTIFACT_REF_MISMATCH = (
    "stored_verification_artifact_ref_mismatch"
)
REASON_STORED_VERIFICATION_BYTES_MALFORMED = (
    "stored_verification_bytes_malformed"
)
REASON_REPLAY_INPUT_WRONG_TYPE = "replay_input_wrong_type"
REASON_ACCEPTED_LEDGER_AUDIT_INVALID = "accepted_ledger_audit_invalid"
REASON_LEDGER_WRONG_TYPE = "ledger_wrong_type"
REASON_ENVELOPE_INVALID = "envelope_invalid"
REASON_STORED_VERIFICATION_INVALID = "stored_verification_invalid"
REASON_FRESH_ANCHORED_VERIFICATION_INVALID = (
    "fresh_anchored_verification_invalid"
)
REASON_EXPECTED_MANIFEST_CORE_HASH_INVALID = (
    "expected_manifest_core_hash_invalid"
)
REASON_EXPECTED_MANIFEST_CORE_HASH_MISMATCH = (
    "expected_manifest_core_hash_mismatch"
)
REASON_REPLAY_INPUT_IDENTITY_MISMATCH = "replay_input_identity_mismatch"
REASON_STORED_VERIFICATION_STATE_MISMATCH = (
    "stored_verification_state_mismatch"
)
REASON_FRESH_VERIFICATION_STATE_MISMATCH = (
    "fresh_verification_state_mismatch"
)
REASON_MANIFEST_IDENTITY_MISMATCH = "manifest_identity_mismatch"
REASON_LEDGER_GEOMETRY_MISMATCH = "ledger_geometry_mismatch"
REASON_LEDGER_INDEX_SEQUENCE_MISMATCH = "ledger_index_sequence_mismatch"
REASON_ARTIFACT_TYPE_SEQUENCE_MISMATCH = "artifact_type_sequence_mismatch"
REASON_ARTIFACT_ID_DUPLICATE = "artifact_id_duplicate"
REASON_ARTIFACT_REF_POSITION_MISMATCH = "artifact_ref_position_mismatch"
REASON_ARTIFACT_HASH_POSITION_MISMATCH = "artifact_hash_position_mismatch"
REASON_TRANSACTION_START_MISMATCH = "transaction_start_mismatch"
REASON_DEPENDENCY_MISSING = "dependency_missing"
REASON_DEPENDENCY_NOT_BACKWARD = "dependency_not_backward"
REASON_DEPENDENCY_SELF_REFERENCE = "dependency_self_reference"
REASON_DEPENDENCY_GRAPH_CYCLE = "dependency_graph_cycle"
REASON_DEPENDENCY_EDGE_COUNT_MISMATCH = "dependency_edge_count_mismatch"
REASON_ROOT_FINAL_SET_MISMATCH = "root_final_set_mismatch"
REASON_ROOT_OWNERSHIP_MISMATCH = "root_ownership_mismatch"
REASON_AUTHORITY_EVIDENCE_BOUNDARY_MISMATCH = (
    "authority_evidence_boundary_mismatch"
)
REASON_PACKET_LINEAGE_MISMATCH = "packet_lineage_mismatch"
REASON_RECEIPT_LINEAGE_MISMATCH = "receipt_lineage_mismatch"
REASON_TRANSACTION_IDENTITY_MISMATCH = "transaction_identity_mismatch"
REASON_SOURCE_REFS_MISMATCH = "source_refs_mismatch"
REASON_SECRET_BOUNDARY_MISMATCH = "secret_boundary_mismatch"
REASON_SOURCE_BYTES_CHANGED = "source_bytes_changed"
REASON_CRITICAL_PACKAGE_BYTES_CHANGED = "critical_package_bytes_changed"
REASON_POST_REPLAY_SNAPSHOT_CALL_COUNT_MISMATCH = (
    "post_replay_snapshot_call_count_mismatch"
)
REASON_ROOT_ATTESTATION_BOUNDARY_MISMATCH = (
    "root_attestation_boundary_mismatch"
)
REASON_NONZERO_REPLAY_COUNTER = "nonzero_replay_counter"
REASON_TIMELINE_ROW_INVALID = "timeline_row_invalid"
REASON_TIMELINE_INCOMPLETE = "timeline_incomplete"
REASON_REPLAY_REPORT_WRONG_TYPE = "replay_report_wrong_type"
REASON_REPLAY_REPORT_STATE_MISMATCH = "replay_report_state_mismatch"
REASON_MALFORMED_VALIDATION_ERRORS = "malformed_validation_errors"
REASON_UNKNOWN_VALIDATION_REASON = "unknown_validation_reason"

REPLAY_VALIDATION_REASON_ALLOWLIST = (
    REASON_PACKAGE_SNAPSHOT_WRONG_TYPE,
    REASON_SOURCE_PACKAGE_REF_INVALID,
    REASON_SOURCE_FILE_SNAPSHOT_MALFORMED,
    REASON_SOURCE_FILE_ORDER_MISMATCH,
    REASON_MANIFEST_ARTIFACT_REF_MISMATCH,
    REASON_MANIFEST_BYTES_MALFORMED,
    REASON_STORED_VERIFICATION_ARTIFACT_REF_MISMATCH,
    REASON_STORED_VERIFICATION_BYTES_MALFORMED,
    REASON_REPLAY_INPUT_WRONG_TYPE,
    REASON_ACCEPTED_LEDGER_AUDIT_INVALID,
    REASON_LEDGER_WRONG_TYPE,
    REASON_ENVELOPE_INVALID,
    REASON_STORED_VERIFICATION_INVALID,
    REASON_FRESH_ANCHORED_VERIFICATION_INVALID,
    REASON_EXPECTED_MANIFEST_CORE_HASH_INVALID,
    REASON_EXPECTED_MANIFEST_CORE_HASH_MISMATCH,
    REASON_REPLAY_INPUT_IDENTITY_MISMATCH,
    REASON_STORED_VERIFICATION_STATE_MISMATCH,
    REASON_FRESH_VERIFICATION_STATE_MISMATCH,
    REASON_MANIFEST_IDENTITY_MISMATCH,
    REASON_LEDGER_GEOMETRY_MISMATCH,
    REASON_LEDGER_INDEX_SEQUENCE_MISMATCH,
    REASON_ARTIFACT_TYPE_SEQUENCE_MISMATCH,
    REASON_ARTIFACT_ID_DUPLICATE,
    REASON_ARTIFACT_REF_POSITION_MISMATCH,
    REASON_ARTIFACT_HASH_POSITION_MISMATCH,
    REASON_TRANSACTION_START_MISMATCH,
    REASON_DEPENDENCY_MISSING,
    REASON_DEPENDENCY_NOT_BACKWARD,
    REASON_DEPENDENCY_SELF_REFERENCE,
    REASON_DEPENDENCY_GRAPH_CYCLE,
    REASON_DEPENDENCY_EDGE_COUNT_MISMATCH,
    REASON_ROOT_FINAL_SET_MISMATCH,
    REASON_ROOT_OWNERSHIP_MISMATCH,
    REASON_AUTHORITY_EVIDENCE_BOUNDARY_MISMATCH,
    REASON_PACKET_LINEAGE_MISMATCH,
    REASON_RECEIPT_LINEAGE_MISMATCH,
    REASON_TRANSACTION_IDENTITY_MISMATCH,
    REASON_SOURCE_REFS_MISMATCH,
    REASON_SECRET_BOUNDARY_MISMATCH,
    REASON_SOURCE_BYTES_CHANGED,
    REASON_CRITICAL_PACKAGE_BYTES_CHANGED,
    REASON_POST_REPLAY_SNAPSHOT_CALL_COUNT_MISMATCH,
    REASON_ROOT_ATTESTATION_BOUNDARY_MISMATCH,
    REASON_NONZERO_REPLAY_COUNTER,
    REASON_TIMELINE_ROW_INVALID,
    REASON_TIMELINE_INCOMPLETE,
    REASON_REPLAY_REPORT_WRONG_TYPE,
    REASON_REPLAY_REPORT_STATE_MISMATCH,
    REASON_MALFORMED_VALIDATION_ERRORS,
    REASON_UNKNOWN_VALIDATION_REASON,
)

VALIDATION_REPORT_FIELD_NAMES = (
    "validation_status",
    "validation_errors",
)

PACKAGE_SNAPSHOT_FIELD_NAMES = (
    "source_package_ref",
    "ordered_source_files",
    "manifest_artifact_ref",
    "manifest_bytes",
    "stored_verification_artifact_ref",
    "stored_verification_bytes",
)

REPLAY_INPUT_FIELD_NAMES = (
    "source_package_ref",
    "accepted_ledger_audit",
    "ledger_item",
    "envelope",
    "stored_verification_report",
    "fresh_anchored_verification_report",
    "expected_manifest_core_hash",
    "ordered_source_files",
)

TIMELINE_ROW_FIELD_NAMES = (
    "replay_index",
    "ledger_index",
    "event_time",
    "event_type",
    "artifact_type",
    "artifact_id",
    "artifact_hash",
    "root_owner",
    "created_by",
    "authority_class",
    "evidence_class",
    "depends_on",
    "dependency_count",
    "is_root_final",
    "selected_offer_id",
)

REPLAY_REPORT_FIELD_NAMES = (
    "replay_status",
    "replay_version",
    "replay_id",
    "source_package_ref",
    "transaction_id",
    "ledger_id",
    "manifest_core_hash",
    "expected_manifest_core_hash",
    "stored_verification_status",
    "fresh_anchored_verification_status",
    "stored_verification_contract_verified",
    "fresh_anchored_verification_contract_verified",
    "external_anchor_supplied",
    "external_anchor_verified",
    "signature_mode",
    "signature_verified",
    "integrity_verified",
    "continuity_verified",
    "ledger_verified",
    "manifest_binding_verified",
    "artifact_hashes_verified",
    "chain_order_verified",
    "dependency_graph_verified",
    "root_ownership_verified",
    "authority_evidence_boundaries_verified",
    "packet_lineage_verified",
    "receipt_lineage_verified",
    "transaction_identity_verified",
    "source_refs_verified",
    "secret_boundary_verified",
    "source_bytes_unchanged",
    "critical_package_bytes_unchanged",
    "timeline_complete",
    "root_attestation_required",
    "root_attestation_present",
    "source_file_count",
    "critical_package_file_count",
    "ledger_entry_count",
    "dependency_edge_count",
    "root_final_count",
    "client_root_final_count",
    "airline_root_final_count",
    "bank_root_final_count",
    "timeline_row_count",
    "ledger_audit_count",
    "anchored_verification_count",
    "post_replay_snapshot_provider_call_count",
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
    "reconstructed_timeline",
    "verification_errors",
)

_VERIFICATION_INTEGRITY_FLAG_FIELDS = (
    "canonicalization_profile_verified",
    "hash_algorithm_verified",
    "manifest_core_hash_verified",
    "ledger_document_byte_hash_verified",
    "artifact_hashes_verified",
    "chain_genesis_verified",
    "chain_order_verified",
    "chain_head_verified",
    "chain_tail_verified",
    "source_file_hashes_verified",
    "source_package_hash_verified",
    "ledger_geometry_verified",
    "root_ownership_verified",
    "authority_evidence_boundaries_verified",
    "secret_boundary_verified",
    "source_bytes_unchanged",
)

_VERIFICATION_ZERO_COUNTER_FIELDS = (
    "provider_call_count",
    "network_call_count",
    "gemini_call_count",
    "seal_created_authority_count",
    "seal_created_permission_count",
    "seal_created_action_count",
    "real_world_effects_count",
)

_REPORT_BOOLEAN_FIELDS = (
    "stored_verification_contract_verified",
    "fresh_anchored_verification_contract_verified",
    "external_anchor_supplied",
    "external_anchor_verified",
    "signature_verified",
    "integrity_verified",
    "continuity_verified",
    "ledger_verified",
    "manifest_binding_verified",
    "artifact_hashes_verified",
    "chain_order_verified",
    "dependency_graph_verified",
    "root_ownership_verified",
    "authority_evidence_boundaries_verified",
    "packet_lineage_verified",
    "receipt_lineage_verified",
    "transaction_identity_verified",
    "source_refs_verified",
    "secret_boundary_verified",
    "source_bytes_unchanged",
    "critical_package_bytes_unchanged",
    "timeline_complete",
    "root_attestation_required",
    "root_attestation_present",
)

_REPORT_COUNT_FIELDS = (
    "source_file_count",
    "critical_package_file_count",
    "ledger_entry_count",
    "dependency_edge_count",
    "root_final_count",
    "client_root_final_count",
    "airline_root_final_count",
    "bank_root_final_count",
    "timeline_row_count",
    "ledger_audit_count",
    "anchored_verification_count",
    "post_replay_snapshot_provider_call_count",
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
)

_REPORT_REQUIRED_TRUE_FIELDS = (
    "stored_verification_contract_verified",
    "fresh_anchored_verification_contract_verified",
    "external_anchor_supplied",
    "external_anchor_verified",
    "integrity_verified",
    "continuity_verified",
    "ledger_verified",
    "manifest_binding_verified",
    "artifact_hashes_verified",
    "chain_order_verified",
    "dependency_graph_verified",
    "root_ownership_verified",
    "authority_evidence_boundaries_verified",
    "packet_lineage_verified",
    "receipt_lineage_verified",
    "transaction_identity_verified",
    "source_refs_verified",
    "secret_boundary_verified",
    "source_bytes_unchanged",
    "critical_package_bytes_unchanged",
    "timeline_complete",
)

_REPORT_ZERO_COUNT_FIELDS = (
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
)

_KNOWN_STORED_VERIFICATION_STATUSES = (
    crypto_contracts.STATUS_SELF_CONSISTENT_UNANCHORED,
)

_KNOWN_FRESH_VERIFICATION_STATUSES = (
    crypto_contracts.STATUS_PASS,
    crypto_contracts.STATUS_FAIL_CLOSED,
    crypto_contracts.STATUS_SELF_CONSISTENT_UNANCHORED,
)

_FORBIDDEN_REPORT_IDENTITY_MARKERS = (
    "api_key",
    "credential",
    "raw_prompt",
    "raw_response",
    "secret",
    "0x",
)


def _append_reason(reasons: list[str], reason: str) -> None:
    if reason not in reasons:
        reasons.append(reason)


def _safe_string(value: object, *, allow_empty: bool = False) -> bool:
    if type(value) is not str or (not allow_empty and value == ""):
        return False
    return not any(0xD800 <= ord(character) <= 0xDFFF for character in value)


def _safe_report_identity_string(value: object) -> bool:
    if not _safe_string(value, allow_empty=True):
        return False
    if value == "":
        return True
    lowered = value.lower()
    return (
        "\n" not in value
        and "\r" not in value
        and not value.startswith("/")
        and "../" not in value
        and not any(
            marker in lowered
            for marker in _FORBIDDEN_REPORT_IDENTITY_MARKERS
        )
    )


def _valid_sha256(value: object) -> bool:
    try:
        return (
            crypto_contracts.validate_sha256_hex_v01(value).validation_status
            == STATUS_PASS
        )
    except (TypeError, AttributeError, ValueError, KeyError, IndexError, RecursionError):
        return False


def _valid_source_package_ref(value: object) -> bool:
    try:
        return (
            crypto_contracts.validate_airline_crypto_source_package_ref_v01(
                value,
            ).validation_status
            == STATUS_PASS
        )
    except (TypeError, AttributeError, ValueError, KeyError, IndexError, RecursionError):
        return False


def _freeze_source_rows(value: object) -> tuple[tuple[str, bytes], ...]:
    if type(value) is not tuple:
        return ()
    if any(
        type(row) is not tuple
        or len(row) != 2
        or type(row[0]) is not str
        or type(row[1]) is not bytes
        for row in value
    ):
        return ()
    return tuple((row[0], row[1]) for row in value)


def _source_rows_reasons(value: object) -> tuple[str, ...]:
    reasons: list[str] = []
    if type(value) is not tuple or len(value) != SOURCE_FILE_COUNT:
        _append_reason(reasons, REASON_SOURCE_FILE_SNAPSHOT_MALFORMED)
        return tuple(reasons)
    if any(
        type(row) is not tuple
        or len(row) != 2
        or type(row[0]) is not str
        or type(row[1]) is not bytes
        for row in value
    ):
        _append_reason(reasons, REASON_SOURCE_FILE_SNAPSHOT_MALFORMED)
        return tuple(reasons)
    refs = tuple(row[0] for row in value)
    if refs != crypto_contracts.REQUIRED_SOURCE_FILE_REFS:
        _append_reason(reasons, REASON_SOURCE_FILE_ORDER_MISMATCH)
    return tuple(reasons)


def _normalize_validation_errors(value: object) -> tuple[str, ...]:
    if type(value) is not tuple or any(type(reason) is not str for reason in value):
        return (REASON_MALFORMED_VALIDATION_ERRORS,)
    normalized: list[str] = []
    for reason in value:
        actual = (
            reason
            if reason in REPLAY_VALIDATION_REASON_ALLOWLIST
            else REASON_UNKNOWN_VALIDATION_REASON
        )
        _append_reason(normalized, actual)
    return tuple(normalized)


@dataclass(frozen=True)
class AirlineSealedTraceReplayValidationReportV01:
    validation_status: str
    validation_errors: tuple[str, ...]

    def __post_init__(self) -> None:
        errors = _normalize_validation_errors(self.validation_errors)
        object.__setattr__(self, "validation_errors", errors)
        object.__setattr__(
            self,
            "validation_status",
            STATUS_PASS if not errors else STATUS_FAIL_CLOSED,
        )


def build_airline_sealed_trace_replay_validation_report_v01(
    validation_errors: object = (),
) -> AirlineSealedTraceReplayValidationReportV01:
    return AirlineSealedTraceReplayValidationReportV01(
        validation_status=STATUS_FAIL_CLOSED,
        validation_errors=validation_errors,  # type: ignore[arg-type]
    )


@dataclass(frozen=True)
class AirlineSealedTraceReplayPackageSnapshotV01:
    source_package_ref: str
    ordered_source_files: tuple[tuple[str, bytes], ...]
    manifest_artifact_ref: str
    manifest_bytes: bytes
    stored_verification_artifact_ref: str
    stored_verification_bytes: bytes

    def __post_init__(self) -> None:
        manifest_bytes_were_exact = type(self.manifest_bytes) is bytes
        stored_verification_bytes_were_exact = (
            type(self.stored_verification_bytes) is bytes
        )
        object.__setattr__(
            self,
            "_manifest_bytes_were_exact_bytes",
            manifest_bytes_were_exact,
        )
        object.__setattr__(
            self,
            "_stored_verification_bytes_were_exact_bytes",
            stored_verification_bytes_were_exact,
        )
        object.__setattr__(
            self,
            "manifest_bytes",
            self.manifest_bytes if manifest_bytes_were_exact else b"",
        )
        object.__setattr__(
            self,
            "stored_verification_bytes",
            (
                self.stored_verification_bytes
                if stored_verification_bytes_were_exact
                else b""
            ),
        )
        object.__setattr__(
            self,
            "ordered_source_files",
            _freeze_source_rows(self.ordered_source_files),
        )


def validate_airline_sealed_trace_replay_package_snapshot_v01(
    snapshot: object,
) -> AirlineSealedTraceReplayValidationReportV01:
    reasons: list[str] = []
    try:
        if type(snapshot) is not AirlineSealedTraceReplayPackageSnapshotV01:
            return build_airline_sealed_trace_replay_validation_report_v01(
                (REASON_PACKAGE_SNAPSHOT_WRONG_TYPE,),
            )
        if not _valid_source_package_ref(snapshot.source_package_ref):
            _append_reason(reasons, REASON_SOURCE_PACKAGE_REF_INVALID)
        for reason in _source_rows_reasons(snapshot.ordered_source_files):
            _append_reason(reasons, reason)
        if (
            type(snapshot.manifest_artifact_ref) is not str
            or snapshot.manifest_artifact_ref != MANIFEST_ARTIFACT_REF
        ):
            _append_reason(reasons, REASON_MANIFEST_ARTIFACT_REF_MISMATCH)
        if (
            getattr(snapshot, "_manifest_bytes_were_exact_bytes", False)
            is not True
            or type(snapshot.manifest_bytes) is not bytes
        ):
            _append_reason(reasons, REASON_MANIFEST_BYTES_MALFORMED)
        if (
            type(snapshot.stored_verification_artifact_ref) is not str
            or snapshot.stored_verification_artifact_ref
            != STORED_VERIFICATION_ARTIFACT_REF
        ):
            _append_reason(
                reasons,
                REASON_STORED_VERIFICATION_ARTIFACT_REF_MISMATCH,
            )
        if (
            getattr(
                snapshot,
                "_stored_verification_bytes_were_exact_bytes",
                False,
            )
            is not True
            or type(snapshot.stored_verification_bytes) is not bytes
        ):
            _append_reason(
                reasons,
                REASON_STORED_VERIFICATION_BYTES_MALFORMED,
            )
    except (TypeError, AttributeError, ValueError, KeyError, IndexError, RecursionError):
        _append_reason(reasons, REASON_PACKAGE_SNAPSHOT_WRONG_TYPE)
    return build_airline_sealed_trace_replay_validation_report_v01(tuple(reasons))


def build_airline_sealed_trace_replay_package_snapshot_v01(
    *,
    source_package_ref: object,
    ordered_source_files: object,
    manifest_artifact_ref: object,
    manifest_bytes: object,
    stored_verification_artifact_ref: object,
    stored_verification_bytes: object,
) -> AirlineSealedTraceReplayPackageSnapshotV01:
    snapshot = AirlineSealedTraceReplayPackageSnapshotV01(
        source_package_ref=source_package_ref,  # type: ignore[arg-type]
        ordered_source_files=ordered_source_files,  # type: ignore[arg-type]
        manifest_artifact_ref=manifest_artifact_ref,  # type: ignore[arg-type]
        manifest_bytes=manifest_bytes,  # type: ignore[arg-type]
        stored_verification_artifact_ref=stored_verification_artifact_ref,  # type: ignore[arg-type]
        stored_verification_bytes=stored_verification_bytes,  # type: ignore[arg-type]
    )
    validation = validate_airline_sealed_trace_replay_package_snapshot_v01(
        snapshot,
    )
    if validation.validation_status != STATUS_PASS:
        raise ValueError(",".join(validation.validation_errors))
    return snapshot


@dataclass(frozen=True)
class AirlineSealedTraceReplayInputV01:
    source_package_ref: str
    accepted_ledger_audit: crypto_collector.AirlineCryptoArtifactSealAcceptedLedgerAuditV01
    ledger_item: ledger_contracts.AirlineTransactionArtifactLedgerV01
    envelope: crypto_contracts.AirlineCryptoArtifactSealEnvelopeV01
    stored_verification_report: crypto_contracts.AirlineCryptoArtifactSealVerificationReportV01
    fresh_anchored_verification_report: crypto_contracts.AirlineCryptoArtifactSealVerificationReportV01
    expected_manifest_core_hash: str
    ordered_source_files: tuple[tuple[str, bytes], ...]

    def __post_init__(self) -> None:
        object.__setattr__(
            self,
            "ordered_source_files",
            _freeze_source_rows(self.ordered_source_files),
        )


def _verification_report_contract_valid(report: object) -> bool:
    try:
        return (
            type(report)
            is crypto_contracts.AirlineCryptoArtifactSealVerificationReportV01
            and crypto_contracts.validate_airline_crypto_artifact_seal_verification_report_v01(
                report,
            ).validation_status
            == STATUS_PASS
        )
    except (TypeError, AttributeError, ValueError, KeyError, IndexError, RecursionError):
        return False


def _verification_internal_state_valid(report: object) -> bool:
    if type(report) is not crypto_contracts.AirlineCryptoArtifactSealVerificationReportV01:
        return False
    try:
        return (
            all(
                type(getattr(report, field_name)) is bool
                and getattr(report, field_name) is True
                for field_name in _VERIFICATION_INTEGRITY_FLAG_FIELDS
            )
            and all(
                type(getattr(report, field_name)) is int
                and getattr(report, field_name) == 0
                for field_name in _VERIFICATION_ZERO_COUNTER_FIELDS
            )
            and type(report.verification_errors) is tuple
            and report.verification_errors == ()
            and type(report.signature_mode) is str
            and report.signature_mode
            == crypto_contracts.SIGNATURE_MODE_UNSIGNED_PLACEHOLDER
            and type(report.signature_verified) is bool
            and report.signature_verified is False
        )
    except (TypeError, AttributeError, ValueError, KeyError, IndexError, RecursionError):
        return False


def _stored_verification_state_valid(report: object) -> bool:
    return (
        _verification_report_contract_valid(report)
        and _verification_internal_state_valid(report)
        and report.verification_status
        == crypto_contracts.STATUS_SELF_CONSISTENT_UNANCHORED
        and report.expected_manifest_core_hash is None
        and type(report.external_anchor_supplied) is bool
        and report.external_anchor_supplied is False
        and type(report.external_anchor_verified) is bool
        and report.external_anchor_verified is False
    )


def _fresh_verification_state_valid(
    report: object,
    expected_manifest_core_hash: object,
) -> bool:
    return (
        _verification_report_contract_valid(report)
        and _verification_internal_state_valid(report)
        and report.verification_status == STATUS_PASS
        and type(report.expected_manifest_core_hash) is str
        and report.expected_manifest_core_hash == expected_manifest_core_hash
        and type(report.external_anchor_supplied) is bool
        and report.external_anchor_supplied is True
        and type(report.external_anchor_verified) is bool
        and report.external_anchor_verified is True
    )


def _accepted_audit_valid(audit: object) -> bool:
    try:
        return (
            type(audit)
            is crypto_collector.AirlineCryptoArtifactSealAcceptedLedgerAuditV01
            and crypto_collector.validate_airline_crypto_artifact_seal_accepted_ledger_audit_v01(
                audit,
            ).validation_status
            == STATUS_PASS
        )
    except (TypeError, AttributeError, ValueError, KeyError, IndexError, RecursionError):
        return False


def _project_expected_identity_value_v01(
    value: object,
    active_ids: set[int],
) -> object:
    if value is None or type(value) in (bool, int, str):
        return value
    if type(value) is tuple:
        value_id = id(value)
        if value_id in active_ids:
            raise ValueError(REASON_LEDGER_GEOMETRY_MISMATCH)
        active_ids.add(value_id)
        projected = tuple(
            _project_expected_identity_value_v01(item, active_ids)
            for item in value
        )
        active_ids.remove(value_id)
        return projected
    if type(value) is ledger_contracts._FrozenDict:
        value_id = id(value)
        if value_id in active_ids:
            raise ValueError(REASON_LEDGER_GEOMETRY_MISMATCH)
        active_ids.add(value_id)
        projected_mapping: dict[str, object] = {}
        for key, item in value.items():
            if type(key) is not str:
                raise ValueError(REASON_LEDGER_GEOMETRY_MISMATCH)
            projected_mapping[key] = _project_expected_identity_value_v01(
                item,
                active_ids,
            )
        active_ids.remove(value_id)
        return projected_mapping
    raise ValueError(REASON_LEDGER_GEOMETRY_MISMATCH)


def _adapter_audit_ledger_coherent_v01(
    ledger_item: ledger_contracts.AirlineTransactionArtifactLedgerV01,
    accepted_audit: crypto_collector.AirlineCryptoArtifactSealAcceptedLedgerAuditV01,
) -> bool:
    try:
        entries = ledger_item.entries
        selected_offer_values = tuple(
            entry.canonical_hash_input["selected_offer_id"]
            for entry in entries
            if type(entry.canonical_hash_input) is ledger_contracts._FrozenDict
            and "selected_offer_id" in entry.canonical_hash_input
        )
        root_types = tuple(
            entry.artifact_type
            for entry in entries
            if entry.artifact_type in ROOT_FINAL_ARTIFACT_TYPES
        )
        return (
            accepted_audit.transaction_id == ledger_item.transaction_id
            and accepted_audit.ledger_id == ledger_item.ledger_id
            and accepted_audit.source_run_ref == ledger_item.source_run_ref
            and accepted_audit.source_causal_report_ref
            == ledger_item.source_causal_report_ref
            and accepted_audit.source_corridor_report_ref
            == ledger_item.source_corridor_report_ref
            and accepted_audit.actual_entry_count == len(entries) == LEDGER_ENTRY_COUNT
            and accepted_audit.actual_dependency_edge_count
            == sum(len(entry.depends_on) for entry in entries)
            == DEPENDENCY_EDGE_COUNT
            and accepted_audit.actual_root_final_count
            == len(root_types)
            == ROOT_FINAL_COUNT
            and accepted_audit.client_root_final_count
            == root_types.count(ledger_contracts.ARTIFACT_CLIENT_ROOT_FINAL)
            == 1
            and accepted_audit.airline_root_final_count
            == root_types.count(ledger_contracts.ARTIFACT_AIRLINE_ROOT_FINAL)
            == 1
            and accepted_audit.bank_root_final_count
            == root_types.count(ledger_contracts.ARTIFACT_BANK_ROOT_FINAL)
            == 1
            and accepted_audit.required_source_files
            == crypto_contracts.REQUIRED_SOURCE_FILE_REFS
            and accepted_audit.files_read_count == SOURCE_FILE_COUNT
            and accepted_audit.stored_validation_status
            == ledger_item.validation_status
            == STATUS_PASS
            and accepted_audit.stored_validation_errors
            == ledger_item.validation_errors
            == ()
            and selected_offer_values
            and all(
                type(value) is str
                and value == accepted_audit.selected_offer_id
                for value in selected_offer_values
            )
        )
    except (TypeError, AttributeError, ValueError, KeyError, IndexError, RecursionError):
        return False


def _build_expected_identity_adapter_impl_v01(
    *,
    ledger_item: object,
    accepted_ledger_audit: object,
) -> ledger_contracts.AirlineTransactionArtifactLedgerExpectedIdentityV01:
    if type(ledger_item) is not ledger_contracts.AirlineTransactionArtifactLedgerV01:
        raise ValueError(REASON_LEDGER_WRONG_TYPE)
    if not _accepted_audit_valid(accepted_ledger_audit):
        raise ValueError(REASON_ACCEPTED_LEDGER_AUDIT_INVALID)
    if not _adapter_audit_ledger_coherent_v01(
        ledger_item,
        accepted_ledger_audit,
    ):
        raise ValueError(REASON_REPLAY_INPUT_IDENTITY_MISMATCH)
    entries = ledger_item.entries
    if (
        type(entries) is not tuple
        or len(entries) != LEDGER_ENTRY_COUNT
        or any(
            type(entry)
            is not ledger_contracts.AirlineTransactionArtifactLedgerEntryV01
            for entry in entries
        )
        or tuple(entry.artifact_type for entry in entries)
        != ledger_contracts.EXPECTED_ARTIFACT_TYPE_SEQUENCE
        or len({entry.artifact_type for entry in entries}) != LEDGER_ENTRY_COUNT
    ):
        raise ValueError(REASON_LEDGER_GEOMETRY_MISMATCH)

    artifact_ids: dict[str, str] = {}
    source_validation_refs: dict[str, tuple[str, ...]] = {}
    auxiliary_refs: dict[str, tuple[str, ...]] = {}
    source_identity: dict[str, dict[str, object]] = {}
    for entry in entries:
        artifact_type = entry.artifact_type
        try:
            extra_keys = (
                ledger_contracts.CANONICAL_HASH_INPUT_EXTRA_KEYS_BY_ARTIFACT_TYPE[
                    artifact_type
                ]
            )
        except (TypeError, KeyError):
            raise ValueError(REASON_ARTIFACT_TYPE_SEQUENCE_MISMATCH) from None
        if (
            type(entry.canonical_hash_input) is not ledger_contracts._FrozenDict
            or any(key not in entry.canonical_hash_input for key in extra_keys)
            or entry.auxiliary_artifact_refs
            != ledger_contracts.EXPECTED_AUXILIARY_REFS_BY_ARTIFACT_TYPE[
                artifact_type
            ]
        ):
            raise ValueError(REASON_LEDGER_GEOMETRY_MISMATCH)
        artifact_ids[artifact_type] = entry.artifact_id
        source_validation_refs[artifact_type] = entry.source_validation_refs
        auxiliary_refs[artifact_type] = entry.auxiliary_artifact_refs
        source_identity[artifact_type] = {
            key: _project_expected_identity_value_v01(
                entry.canonical_hash_input[key],
                set(),
            )
            for key in extra_keys
        }
    expected_types = frozenset(ledger_contracts.EXPECTED_ARTIFACT_TYPE_SEQUENCE)
    if any(
        frozenset(mapping) != expected_types
        for mapping in (
            artifact_ids,
            source_validation_refs,
            auxiliary_refs,
            source_identity,
        )
    ):
        raise ValueError(REASON_LEDGER_GEOMETRY_MISMATCH)
    adapter = ledger_contracts.AirlineTransactionArtifactLedgerExpectedIdentityV01(
        expected_source_refs=(
            ledger_contracts.AirlineTransactionArtifactLedgerExpectedSourceRefsV01(
                source_run_ref=ledger_item.source_run_ref,
                source_causal_report_ref=ledger_item.source_causal_report_ref,
                source_corridor_report_ref=ledger_item.source_corridor_report_ref,
            )
        ),
        expected_artifact_ids=artifact_ids,
        expected_source_validation_refs_by_type=source_validation_refs,
        expected_auxiliary_artifact_refs_by_type=auxiliary_refs,
        expected_source_identity_fields_by_type=source_identity,
    )
    validation = ledger_contracts.validate_airline_transaction_artifact_ledger_v01(
        ledger_item,
        expected_identity=adapter,
    )
    if validation.validation_status != STATUS_PASS or validation.validation_errors != ():
        raise ValueError(REASON_LEDGER_GEOMETRY_MISMATCH)
    return adapter


def build_airline_sealed_trace_replay_expected_identity_adapter_v01(
    *,
    ledger_item: object,
    accepted_ledger_audit: object,
) -> ledger_contracts.AirlineTransactionArtifactLedgerExpectedIdentityV01:
    reason = REASON_LEDGER_GEOMETRY_MISMATCH
    try:
        return _build_expected_identity_adapter_impl_v01(
            ledger_item=ledger_item,
            accepted_ledger_audit=accepted_ledger_audit,
        )
    except ValueError as error:
        if (
            len(error.args) == 1
            and type(error.args[0]) is str
            and error.args[0] in REPLAY_VALIDATION_REASON_ALLOWLIST
        ):
            reason = error.args[0]
    except Exception:
        pass
    raise ValueError(reason) from None


def _ledger_validation_report(
    ledger_item: object,
    accepted_ledger_audit: object,
) -> object | None:
    try:
        adapter = build_airline_sealed_trace_replay_expected_identity_adapter_v01(
            ledger_item=ledger_item,
            accepted_ledger_audit=accepted_ledger_audit,
        )
        return ledger_contracts.validate_airline_transaction_artifact_ledger_v01(
            ledger_item,
            expected_identity=adapter,
        )
    except (TypeError, AttributeError, ValueError, KeyError, IndexError, RecursionError):
        return None


def _selected_offer_values(
    entries: object,
) -> tuple[str, ...] | None:
    if type(entries) is not tuple:
        return None
    values: list[str] = []
    try:
        for entry in entries:
            if type(entry) is not ledger_contracts.AirlineTransactionArtifactLedgerEntryV01:
                return None
            canonical = entry.canonical_hash_input
            if not isinstance(canonical, Mapping):
                return None
            if "selected_offer_id" not in canonical:
                continue
            value = canonical["selected_offer_id"]
            if type(value) is not str or value == "":
                return None
            if value not in values:
                values.append(value)
    except (TypeError, AttributeError, ValueError, KeyError, IndexError, RecursionError):
        return None
    return tuple(values)


def _ledger_direct_boundary_valid(
    ledger_item: ledger_contracts.AirlineTransactionArtifactLedgerV01,
) -> bool:
    try:
        if (
            type(ledger_item.validation_status) is not str
            or ledger_item.validation_status != STATUS_PASS
            or type(ledger_item.validation_errors) is not tuple
            or ledger_item.validation_errors != ()
        ):
            return False
        if any(
            type(getattr(ledger_item, field_name)) is not int
            or getattr(ledger_item, field_name) != 0
            for field_name in (
                "ledger_created_authority_count",
                "ledger_created_permission_count",
                "ledger_created_action_count",
                "provider_called_count",
                "network_used_count",
                "gemini_called_count",
                "real_world_effects_count",
            )
        ):
            return False
        if type(ledger_item.entries) is not tuple:
            return False
        return all(
            type(entry) is ledger_contracts.AirlineTransactionArtifactLedgerEntryV01
            and type(entry.raw_secret_included) is bool
            and entry.raw_secret_included is False
            and type(entry.raw_provider_text_included) is bool
            and entry.raw_provider_text_included is False
            and type(entry.ledger_created_authority) is bool
            and entry.ledger_created_authority is False
            and type(entry.ledger_created_permission) is bool
            and entry.ledger_created_permission is False
            and type(entry.ledger_created_action) is bool
            and entry.ledger_created_action is False
            and type(entry.real_world_effects_count) is int
            and entry.real_world_effects_count == 0
            for entry in ledger_item.entries
        )
    except (TypeError, AttributeError, ValueError, KeyError, IndexError, RecursionError):
        return False


def _source_package_binding_valid_v01(
    replay_input: AirlineSealedTraceReplayInputV01,
) -> bool:
    try:
        rebuilt_index = (
            crypto_contracts.build_airline_crypto_source_package_index_v01(
                transaction_id=(
                    replay_input.envelope.manifest_core.transaction_id
                ),
                ordered_source_files=replay_input.ordered_source_files,
            )
        )
        manifest_core = replay_input.envelope.manifest_core
        return (
            rebuilt_index.source_file_count == manifest_core.source_file_count
            and rebuilt_index.ordered_source_file_refs
            == manifest_core.ordered_source_file_refs
            and rebuilt_index.ordered_source_file_hashes
            == manifest_core.ordered_source_file_hashes
            and rebuilt_index.source_package_hash
            == manifest_core.source_package_hash
            and rebuilt_index.ledger_document_byte_hash
            == manifest_core.ledger_document_byte_hash
        )
    except (TypeError, AttributeError, ValueError, KeyError, IndexError, RecursionError):
        return False


def _input_validation_reasons(replay_input: object) -> tuple[str, ...]:
    reasons: list[str] = []
    try:
        if type(replay_input) is not AirlineSealedTraceReplayInputV01:
            return (REASON_REPLAY_INPUT_WRONG_TYPE,)
        if not _valid_source_package_ref(replay_input.source_package_ref):
            _append_reason(reasons, REASON_SOURCE_PACKAGE_REF_INVALID)
        source_row_reasons = _source_rows_reasons(
            replay_input.ordered_source_files,
        )
        for reason in source_row_reasons:
            _append_reason(reasons, reason)

        audit_valid = _accepted_audit_valid(replay_input.accepted_ledger_audit)
        if not audit_valid:
            _append_reason(reasons, REASON_ACCEPTED_LEDGER_AUDIT_INVALID)

        ledger_report = _ledger_validation_report(
            replay_input.ledger_item,
            replay_input.accepted_ledger_audit,
        )
        ledger_valid = False
        if type(replay_input.ledger_item) is not ledger_contracts.AirlineTransactionArtifactLedgerV01:
            _append_reason(reasons, REASON_LEDGER_WRONG_TYPE)
        elif (
            ledger_report is None
            or getattr(ledger_report, "validation_status", None) != STATUS_PASS
            or not _ledger_direct_boundary_valid(replay_input.ledger_item)
        ):
            _append_reason(reasons, REASON_LEDGER_GEOMETRY_MISMATCH)
        else:
            ledger_valid = True

        envelope_valid = False
        if type(replay_input.envelope) is crypto_contracts.AirlineCryptoArtifactSealEnvelopeV01:
            envelope_valid = (
                crypto_contracts.validate_airline_crypto_artifact_seal_envelope_contract_v01(
                    replay_input.envelope,
                ).validation_status
                == STATUS_PASS
            )
        if not envelope_valid:
            _append_reason(reasons, REASON_ENVELOPE_INVALID)
        if (
            not source_row_reasons
            and ledger_valid
            and envelope_valid
            and not _source_package_binding_valid_v01(replay_input)
        ):
            _append_reason(reasons, REASON_SOURCE_BYTES_CHANGED)

        stored_contract_valid = _verification_report_contract_valid(
            replay_input.stored_verification_report,
        )
        if not stored_contract_valid:
            _append_reason(reasons, REASON_STORED_VERIFICATION_INVALID)
        elif not _stored_verification_state_valid(
            replay_input.stored_verification_report,
        ):
            _append_reason(reasons, REASON_STORED_VERIFICATION_STATE_MISMATCH)
        if (
            type(replay_input.stored_verification_report)
            is crypto_contracts.AirlineCryptoArtifactSealVerificationReportV01
            and replay_input.stored_verification_report.source_bytes_unchanged
            is not True
        ):
            _append_reason(reasons, REASON_SOURCE_BYTES_CHANGED)

        fresh_contract_valid = _verification_report_contract_valid(
            replay_input.fresh_anchored_verification_report,
        )
        if not fresh_contract_valid:
            _append_reason(reasons, REASON_FRESH_ANCHORED_VERIFICATION_INVALID)
        if (
            type(replay_input.fresh_anchored_verification_report)
            is crypto_contracts.AirlineCryptoArtifactSealVerificationReportV01
            and replay_input.fresh_anchored_verification_report.source_bytes_unchanged
            is not True
        ):
            _append_reason(reasons, REASON_SOURCE_BYTES_CHANGED)

        if not _valid_sha256(replay_input.expected_manifest_core_hash):
            _append_reason(reasons, REASON_EXPECTED_MANIFEST_CORE_HASH_INVALID)
        elif fresh_contract_valid and not _fresh_verification_state_valid(
            replay_input.fresh_anchored_verification_report,
            replay_input.expected_manifest_core_hash,
        ):
            _append_reason(reasons, REASON_FRESH_VERIFICATION_STATE_MISMATCH)

        if envelope_valid:
            core = replay_input.envelope.manifest_core
            if (
                replay_input.source_package_ref != core.source_package_ref
                or tuple(row[0] for row in replay_input.ordered_source_files)
                != core.ordered_source_file_refs
            ):
                _append_reason(reasons, REASON_REPLAY_INPUT_IDENTITY_MISMATCH)
            if (
                replay_input.expected_manifest_core_hash
                != replay_input.envelope.manifest_core_hash
            ):
                _append_reason(
                    reasons,
                    REASON_EXPECTED_MANIFEST_CORE_HASH_MISMATCH,
                )

        if (
            envelope_valid
            and type(replay_input.ledger_item)
            is ledger_contracts.AirlineTransactionArtifactLedgerV01
        ):
            core = replay_input.envelope.manifest_core
            ledger_item = replay_input.ledger_item
            if (
                ledger_item.transaction_id != core.transaction_id
                or ledger_item.ledger_id != core.ledger_id
            ):
                _append_reason(reasons, REASON_MANIFEST_IDENTITY_MISMATCH)
            for report in (
                replay_input.stored_verification_report,
                replay_input.fresh_anchored_verification_report,
            ):
                if type(report) is crypto_contracts.AirlineCryptoArtifactSealVerificationReportV01 and (
                    report.transaction_id != core.transaction_id
                    or report.ledger_id != core.ledger_id
                    or report.manifest_core_hash
                    != replay_input.envelope.manifest_core_hash
                ):
                    _append_reason(reasons, REASON_REPLAY_INPUT_IDENTITY_MISMATCH)

        if (
            audit_valid
            and type(replay_input.ledger_item)
            is ledger_contracts.AirlineTransactionArtifactLedgerV01
        ):
            audit = replay_input.accepted_ledger_audit
            ledger_item = replay_input.ledger_item
            if (
                audit.ledger_id != ledger_item.ledger_id
                or audit.transaction_id != ledger_item.transaction_id
            ):
                _append_reason(reasons, REASON_REPLAY_INPUT_IDENTITY_MISMATCH)
            if (
                audit.source_run_ref != ledger_item.source_run_ref
                or audit.source_causal_report_ref
                != ledger_item.source_causal_report_ref
                or audit.source_corridor_report_ref
                != ledger_item.source_corridor_report_ref
            ):
                _append_reason(reasons, REASON_SOURCE_REFS_MISMATCH)
            if (
                audit.required_source_files
                != tuple(row[0] for row in replay_input.ordered_source_files)
                or audit.files_read_count != SOURCE_FILE_COUNT
            ):
                _append_reason(reasons, REASON_SOURCE_REFS_MISMATCH)
            if (
                audit.actual_entry_count != ledger_item.entry_count
                or audit.actual_dependency_edge_count
                != ledger_item.dependency_edge_count
                or audit.actual_root_final_count != ledger_item.root_final_count
            ):
                _append_reason(reasons, REASON_LEDGER_GEOMETRY_MISMATCH)
            selected = _selected_offer_values(ledger_item.entries)
            if selected is None or selected != (audit.selected_offer_id,):
                _append_reason(reasons, REASON_TRANSACTION_IDENTITY_MISMATCH)
    except (TypeError, AttributeError, ValueError, KeyError, IndexError, RecursionError):
        _append_reason(reasons, REASON_REPLAY_INPUT_WRONG_TYPE)
    return tuple(reasons)


def validate_airline_sealed_trace_replay_input_v01(
    replay_input: object,
) -> AirlineSealedTraceReplayValidationReportV01:
    return build_airline_sealed_trace_replay_validation_report_v01(
        _input_validation_reasons(replay_input),
    )


def build_airline_sealed_trace_replay_input_v01(
    *,
    source_package_ref: object,
    accepted_ledger_audit: object,
    ledger_item: object,
    envelope: object,
    stored_verification_report: object,
    fresh_anchored_verification_report: object,
    expected_manifest_core_hash: object,
    ordered_source_files: object,
) -> AirlineSealedTraceReplayInputV01:
    replay_input = AirlineSealedTraceReplayInputV01(
        source_package_ref=source_package_ref,  # type: ignore[arg-type]
        accepted_ledger_audit=accepted_ledger_audit,  # type: ignore[arg-type]
        ledger_item=ledger_item,  # type: ignore[arg-type]
        envelope=envelope,  # type: ignore[arg-type]
        stored_verification_report=stored_verification_report,  # type: ignore[arg-type]
        fresh_anchored_verification_report=fresh_anchored_verification_report,  # type: ignore[arg-type]
        expected_manifest_core_hash=expected_manifest_core_hash,  # type: ignore[arg-type]
        ordered_source_files=ordered_source_files,  # type: ignore[arg-type]
    )
    validation = validate_airline_sealed_trace_replay_input_v01(replay_input)
    if validation.validation_status != STATUS_PASS:
        raise ValueError(",".join(validation.validation_errors))
    return replay_input


@dataclass(frozen=True)
class AirlineSealedTraceReplayTimelineRowV01:
    replay_index: int
    ledger_index: int
    event_time: str
    event_type: str
    artifact_type: str
    artifact_id: str
    artifact_hash: str
    root_owner: str
    created_by: str
    authority_class: str
    evidence_class: str
    depends_on: tuple[str, ...]
    dependency_count: int
    is_root_final: bool
    selected_offer_id: str | None

    def __post_init__(self) -> None:
        depends_on = self.depends_on
        if type(depends_on) is not tuple or any(
            type(value) is not str for value in depends_on
        ):
            depends_on = ("",)
        else:
            depends_on = tuple(depends_on)
        object.__setattr__(self, "depends_on", depends_on)


def validate_airline_sealed_trace_replay_timeline_row_v01(
    row: object,
) -> AirlineSealedTraceReplayValidationReportV01:
    valid = True
    try:
        if type(row) is not AirlineSealedTraceReplayTimelineRowV01:
            valid = False
        else:
            valid = (
                type(row.replay_index) is int
                and type(row.ledger_index) is int
                and row.replay_index >= 0
                and row.replay_index == row.ledger_index
                and all(
                    _safe_string(getattr(row, field_name))
                    for field_name in (
                        "event_time",
                        "event_type",
                        "artifact_type",
                        "artifact_id",
                        "root_owner",
                        "created_by",
                        "authority_class",
                        "evidence_class",
                    )
                )
                and _valid_sha256(row.artifact_hash)
                and type(row.depends_on) is tuple
                and all(_safe_string(value) for value in row.depends_on)
                and len(set(row.depends_on)) == len(row.depends_on)
                and type(row.dependency_count) is int
                and row.dependency_count == len(row.depends_on)
                and type(row.is_root_final) is bool
                and row.is_root_final
                == (row.artifact_type in ROOT_FINAL_ARTIFACT_TYPES)
                and (
                    row.selected_offer_id is None
                    or _safe_string(row.selected_offer_id)
                )
            )
    except (TypeError, AttributeError, ValueError, KeyError, IndexError, RecursionError):
        valid = False
    return build_airline_sealed_trace_replay_validation_report_v01(
        () if valid else (REASON_TIMELINE_ROW_INVALID,),
    )


def airline_sealed_trace_replay_timeline_row_to_plain_dict_v01(
    row: AirlineSealedTraceReplayTimelineRowV01,
) -> dict[str, object]:
    validation = validate_airline_sealed_trace_replay_timeline_row_v01(row)
    if validation.validation_status != STATUS_PASS:
        raise ValueError(",".join(validation.validation_errors))
    return {
        "replay_index": row.replay_index,
        "ledger_index": row.ledger_index,
        "event_time": row.event_time,
        "event_type": row.event_type,
        "artifact_type": row.artifact_type,
        "artifact_id": row.artifact_id,
        "artifact_hash": row.artifact_hash,
        "root_owner": row.root_owner,
        "created_by": row.created_by,
        "authority_class": row.authority_class,
        "evidence_class": row.evidence_class,
        "depends_on": list(row.depends_on),
        "dependency_count": row.dependency_count,
        "is_root_final": row.is_root_final,
        "selected_offer_id": row.selected_offer_id,
    }


def _timeline_validation_reasons(
    replay_input: AirlineSealedTraceReplayInputV01,
) -> tuple[str, ...]:
    reasons: list[str] = []
    try:
        ledger_item = replay_input.ledger_item
        core = replay_input.envelope.manifest_core
        entries = ledger_item.entries
        if (
            type(entries) is not tuple
            or len(entries) != LEDGER_ENTRY_COUNT
            or any(
                type(entry)
                is not ledger_contracts.AirlineTransactionArtifactLedgerEntryV01
                for entry in entries
            )
        ):
            _append_reason(reasons, REASON_LEDGER_GEOMETRY_MISMATCH)
            return tuple(reasons)

        indexes = tuple(entry.ledger_index for entry in entries)
        if indexes != tuple(range(LEDGER_ENTRY_COUNT)) or any(
            type(index) is not int for index in indexes
        ):
            _append_reason(reasons, REASON_LEDGER_INDEX_SEQUENCE_MISMATCH)
        artifact_types = tuple(entry.artifact_type for entry in entries)
        if artifact_types != ledger_contracts.EXPECTED_ARTIFACT_TYPE_SEQUENCE:
            _append_reason(reasons, REASON_ARTIFACT_TYPE_SEQUENCE_MISMATCH)
        artifact_ids = tuple(entry.artifact_id for entry in entries)
        if any(not _safe_string(value) for value in artifact_ids) or len(
            set(artifact_ids),
        ) != len(artifact_ids):
            _append_reason(reasons, REASON_ARTIFACT_ID_DUPLICATE)

        transaction_start_entries = tuple(
            entry
            for entry in entries
            if entry.event_type == ledger_contracts.EVENT_TRANSACTION_STARTED
        )
        if (
            len(transaction_start_entries) != 1
            or entries[0].event_type != ledger_contracts.EVENT_TRANSACTION_STARTED
            or entries[0].artifact_type
            != ledger_contracts.ARTIFACT_TRANSACTION_SCOPE
        ):
            _append_reason(reasons, REASON_TRANSACTION_START_MISMATCH)

        manifest_refs = core.ordered_artifact_refs
        manifest_hashes = core.ordered_artifact_hashes
        if (
            type(manifest_refs) is not tuple
            or len(manifest_refs) != LEDGER_ENTRY_COUNT
            or manifest_refs != artifact_ids
        ):
            _append_reason(reasons, REASON_ARTIFACT_REF_POSITION_MISMATCH)
        if (
            type(manifest_hashes) is not tuple
            or len(manifest_hashes) != LEDGER_ENTRY_COUNT
            or any(not _valid_sha256(value) for value in manifest_hashes)
        ):
            _append_reason(reasons, REASON_ARTIFACT_HASH_POSITION_MISMATCH)

        id_to_index = {
            entry.artifact_id: entry.ledger_index
            for entry in entries
            if _safe_string(entry.artifact_id)
            and type(entry.ledger_index) is int
        }
        edge_count = 0
        for entry in entries:
            if type(entry.depends_on) is not tuple:
                _append_reason(reasons, REASON_DEPENDENCY_MISSING)
                continue
            edge_count += len(entry.depends_on)
            for dependency in entry.depends_on:
                if dependency == entry.artifact_id:
                    _append_reason(reasons, REASON_DEPENDENCY_SELF_REFERENCE)
                if dependency not in id_to_index:
                    _append_reason(reasons, REASON_DEPENDENCY_MISSING)
                elif id_to_index[dependency] >= entry.ledger_index:
                    _append_reason(reasons, REASON_DEPENDENCY_NOT_BACKWARD)
        if edge_count != DEPENDENCY_EDGE_COUNT:
            _append_reason(reasons, REASON_DEPENDENCY_EDGE_COUNT_MISMATCH)
        if _dependency_graph_has_cycle(entries):
            _append_reason(reasons, REASON_DEPENDENCY_GRAPH_CYCLE)

        observed_finals = tuple(
            entry.artifact_type
            for entry in entries
            if entry.artifact_type in ROOT_FINAL_ARTIFACT_TYPES
        )
        if observed_finals != ROOT_FINAL_ARTIFACT_TYPES:
            _append_reason(reasons, REASON_ROOT_FINAL_SET_MISMATCH)
        expected_final_owners = (
            ledger_contracts.CLIENT_ROOT_ID,
            ledger_contracts.AIRLINE_ROOT_ID,
            ledger_contracts.BANK_ROOT_ID,
        )
        observed_final_owners = tuple(
            entry.root_owner
            for entry in entries
            if entry.artifact_type in ROOT_FINAL_ARTIFACT_TYPES
        )
        if observed_final_owners != expected_final_owners:
            _append_reason(reasons, REASON_ROOT_OWNERSHIP_MISMATCH)
    except (TypeError, AttributeError, ValueError, KeyError, IndexError, RecursionError):
        _append_reason(reasons, REASON_TIMELINE_INCOMPLETE)
    return tuple(reasons)


def _dependency_graph_has_cycle(
    entries: tuple[ledger_contracts.AirlineTransactionArtifactLedgerEntryV01, ...],
) -> bool:
    try:
        dependencies = {
            entry.artifact_id: entry.depends_on
            for entry in entries
            if type(entry.artifact_id) is str and type(entry.depends_on) is tuple
        }
        visiting: set[str] = set()
        visited: set[str] = set()

        def visit(artifact_id: str) -> bool:
            if artifact_id in visiting:
                return True
            if artifact_id in visited:
                return False
            visiting.add(artifact_id)
            for dependency in dependencies.get(artifact_id, ()):
                if dependency in dependencies and visit(dependency):
                    return True
            visiting.remove(artifact_id)
            visited.add(artifact_id)
            return False

        return any(visit(artifact_id) for artifact_id in dependencies)
    except (TypeError, AttributeError, ValueError, KeyError, IndexError, RecursionError):
        return True


def build_airline_sealed_trace_replay_timeline_v01(
    replay_input: AirlineSealedTraceReplayInputV01,
) -> tuple[AirlineSealedTraceReplayTimelineRowV01, ...]:
    input_validation = validate_airline_sealed_trace_replay_input_v01(replay_input)
    if input_validation.validation_status != STATUS_PASS:
        raise ValueError(",".join(input_validation.validation_errors))
    reasons = _timeline_validation_reasons(replay_input)
    if reasons:
        raise ValueError(",".join(reasons))
    try:
        rows: list[AirlineSealedTraceReplayTimelineRowV01] = []
        for entry, artifact_hash in zip(
            replay_input.ledger_item.entries,
            replay_input.envelope.manifest_core.ordered_artifact_hashes,
            strict=True,
        ):
            canonical = entry.canonical_hash_input
            selected_offer_id = (
                canonical.get("selected_offer_id")
                if isinstance(canonical, Mapping)
                and type(canonical.get("selected_offer_id")) is str
                and canonical.get("selected_offer_id") != ""
                else None
            )
            row = AirlineSealedTraceReplayTimelineRowV01(
                replay_index=entry.ledger_index,
                ledger_index=entry.ledger_index,
                event_time=entry.event_time,
                event_type=entry.event_type,
                artifact_type=entry.artifact_type,
                artifact_id=entry.artifact_id,
                artifact_hash=artifact_hash,
                root_owner=entry.root_owner,
                created_by=entry.created_by,
                authority_class=entry.authority_class,
                evidence_class=entry.evidence_class,
                depends_on=entry.depends_on,
                dependency_count=len(entry.depends_on),
                is_root_final=entry.artifact_type in ROOT_FINAL_ARTIFACT_TYPES,
                selected_offer_id=selected_offer_id,
            )
            validation = validate_airline_sealed_trace_replay_timeline_row_v01(
                row,
            )
            if validation.validation_status != STATUS_PASS:
                raise ValueError(REASON_TIMELINE_ROW_INVALID)
            rows.append(row)
        result = tuple(rows)
        if len(result) != TIMELINE_ROW_COUNT:
            raise ValueError(REASON_TIMELINE_INCOMPLETE)
        return result
    except ValueError:
        raise ValueError(REASON_TIMELINE_INCOMPLETE) from None
    except (TypeError, AttributeError, KeyError, IndexError, RecursionError):
        raise ValueError(REASON_TIMELINE_INCOMPLETE) from None


@dataclass(frozen=True, init=False)
class AirlineSealedTraceReplayReportV01:
    replay_status: str
    replay_version: str
    replay_id: str
    source_package_ref: str
    transaction_id: str
    ledger_id: str
    manifest_core_hash: str
    expected_manifest_core_hash: str
    stored_verification_status: str
    fresh_anchored_verification_status: str
    stored_verification_contract_verified: bool
    fresh_anchored_verification_contract_verified: bool
    external_anchor_supplied: bool
    external_anchor_verified: bool
    signature_mode: str
    signature_verified: bool
    integrity_verified: bool
    continuity_verified: bool
    ledger_verified: bool
    manifest_binding_verified: bool
    artifact_hashes_verified: bool
    chain_order_verified: bool
    dependency_graph_verified: bool
    root_ownership_verified: bool
    authority_evidence_boundaries_verified: bool
    packet_lineage_verified: bool
    receipt_lineage_verified: bool
    transaction_identity_verified: bool
    source_refs_verified: bool
    secret_boundary_verified: bool
    source_bytes_unchanged: bool
    critical_package_bytes_unchanged: bool
    timeline_complete: bool
    root_attestation_required: bool
    root_attestation_present: bool
    source_file_count: int
    critical_package_file_count: int
    ledger_entry_count: int
    dependency_edge_count: int
    root_final_count: int
    client_root_final_count: int
    airline_root_final_count: int
    bank_root_final_count: int
    timeline_row_count: int
    ledger_audit_count: int
    anchored_verification_count: int
    post_replay_snapshot_provider_call_count: int
    transaction_rerun_count: int
    semantic_rerun_count: int
    corridor_rerun_count: int
    ledger_recollection_count: int
    crypto_collection_count: int
    provider_call_count: int
    network_call_count: int
    gemini_call_count: int
    replay_created_authority_count: int
    replay_created_permission_count: int
    replay_created_action_count: int
    replay_created_packet_count: int
    replay_created_receipt_count: int
    replay_created_final_output_count: int
    real_world_effects_count: int
    reconstructed_timeline: tuple[AirlineSealedTraceReplayTimelineRowV01, ...]
    verification_errors: tuple[str, ...]


def _report_timeline_intrinsically_valid_v01(
    report: AirlineSealedTraceReplayReportV01,
) -> bool:
    try:
        rows = report.reconstructed_timeline
        if (
            type(rows) is not tuple
            or len(rows) != TIMELINE_ROW_COUNT
            or any(
                type(row) is not AirlineSealedTraceReplayTimelineRowV01
                or validate_airline_sealed_trace_replay_timeline_row_v01(
                    row,
                ).validation_status
                != STATUS_PASS
                for row in rows
            )
        ):
            return False
        replay_indexes = tuple(row.replay_index for row in rows)
        ledger_indexes = tuple(row.ledger_index for row in rows)
        expected_indexes = tuple(range(TIMELINE_ROW_COUNT))
        if (
            replay_indexes != expected_indexes
            or ledger_indexes != expected_indexes
            or len(set(replay_indexes)) != TIMELINE_ROW_COUNT
            or len(set(ledger_indexes)) != TIMELINE_ROW_COUNT
        ):
            return False
        artifact_ids = tuple(row.artifact_id for row in rows)
        if len(set(artifact_ids)) != TIMELINE_ROW_COUNT:
            return False
        if tuple(row.artifact_type for row in rows) != (
            ledger_contracts.EXPECTED_ARTIFACT_TYPE_SEQUENCE
        ):
            return False
        if tuple(
            row.artifact_type for row in rows if row.is_root_final
        ) != ROOT_FINAL_ARTIFACT_TYPES:
            return False
        positions = {
            row.artifact_id: row.replay_index
            for row in rows
        }
        if sum(row.dependency_count for row in rows) != DEPENDENCY_EDGE_COUNT:
            return False
        return all(
            all(
                dependency in positions
                and positions[dependency] < row.replay_index
                for dependency in row.depends_on
            )
            for row in rows
        )
    except (TypeError, AttributeError, ValueError, KeyError, IndexError, RecursionError):
        return False


def _replay_report_pass_state(
    report: AirlineSealedTraceReplayReportV01,
    errors: tuple[str, ...],
) -> bool:
    try:
        return (
            errors == ()
            and getattr(
                report,
                "_constructed_by_replay_verifier_v01",
                False,
            )
            is True
            and report.replay_version == REPLAY_VERSION
            and report.replay_id
            == f"{REPLAY_ID_PREFIX}:{report.transaction_id}:{report.manifest_core_hash}"
            and _safe_string(report.source_package_ref)
            and _safe_string(report.transaction_id)
            and _safe_string(report.ledger_id)
            and _valid_sha256(report.manifest_core_hash)
            and report.expected_manifest_core_hash == report.manifest_core_hash
            and report.stored_verification_status
            == crypto_contracts.STATUS_SELF_CONSISTENT_UNANCHORED
            and report.fresh_anchored_verification_status == STATUS_PASS
            and all(
                type(getattr(report, field_name)) is bool
                and getattr(report, field_name) is True
                for field_name in _REPORT_REQUIRED_TRUE_FIELDS
            )
            and type(report.signature_mode) is str
            and report.signature_mode
            == crypto_contracts.SIGNATURE_MODE_UNSIGNED_PLACEHOLDER
            and type(report.signature_verified) is bool
            and report.signature_verified is False
            and type(report.root_attestation_required) is bool
            and report.root_attestation_required is False
            and type(report.root_attestation_present) is bool
            and report.root_attestation_present is False
            and type(report.source_file_count) is int
            and report.source_file_count == SOURCE_FILE_COUNT
            and type(report.critical_package_file_count) is int
            and report.critical_package_file_count == CRITICAL_PACKAGE_FILE_COUNT
            and type(report.ledger_entry_count) is int
            and report.ledger_entry_count == LEDGER_ENTRY_COUNT
            and type(report.dependency_edge_count) is int
            and report.dependency_edge_count == DEPENDENCY_EDGE_COUNT
            and type(report.root_final_count) is int
            and report.root_final_count == ROOT_FINAL_COUNT
            and type(report.client_root_final_count) is int
            and report.client_root_final_count == 1
            and type(report.airline_root_final_count) is int
            and report.airline_root_final_count == 1
            and type(report.bank_root_final_count) is int
            and report.bank_root_final_count == 1
            and type(report.timeline_row_count) is int
            and report.timeline_row_count == TIMELINE_ROW_COUNT
            and type(report.ledger_audit_count) is int
            and report.ledger_audit_count == 1
            and type(report.anchored_verification_count) is int
            and report.anchored_verification_count == 1
            and type(report.post_replay_snapshot_provider_call_count) is int
            and report.post_replay_snapshot_provider_call_count == 1
            and all(
                type(getattr(report, field_name)) is int
                and getattr(report, field_name) == 0
                for field_name in _REPORT_ZERO_COUNT_FIELDS
            )
            and _report_timeline_intrinsically_valid_v01(report)
        )
    except (TypeError, AttributeError, ValueError, KeyError, IndexError, RecursionError):
        return False


def validate_airline_sealed_trace_replay_report_v01(
    report: object,
) -> AirlineSealedTraceReplayValidationReportV01:
    reasons: list[str] = []
    try:
        if type(report) is not AirlineSealedTraceReplayReportV01:
            return build_airline_sealed_trace_replay_validation_report_v01(
                (REASON_REPLAY_REPORT_WRONG_TYPE,),
            )
        if getattr(
            report,
            "_constructed_by_replay_verifier_v01",
            False,
        ) is not True:
            _append_reason(reasons, REASON_REPLAY_REPORT_STATE_MISMATCH)
        if (
            type(report.verification_errors) is not tuple
            or report.verification_errors
            != _normalize_validation_errors(report.verification_errors)
        ):
            _append_reason(reasons, REASON_MALFORMED_VALIDATION_ERRORS)
        if report.replay_version != REPLAY_VERSION:
            _append_reason(reasons, REASON_REPLAY_REPORT_STATE_MISMATCH)
        expected_id = (
            f"{REPLAY_ID_PREFIX}:{report.transaction_id}:{report.manifest_core_hash}"
            if _safe_string(report.transaction_id)
            and _valid_sha256(report.manifest_core_hash)
            else ""
        )
        if report.replay_id != expected_id:
            _append_reason(reasons, REASON_REPLAY_REPORT_STATE_MISMATCH)
        if any(
            type(getattr(report, field_name)) is not bool
            for field_name in _REPORT_BOOLEAN_FIELDS
        ):
            _append_reason(reasons, REASON_REPLAY_REPORT_STATE_MISMATCH)
        if any(
            type(getattr(report, field_name)) is not int
            or getattr(report, field_name) < 0
            for field_name in _REPORT_COUNT_FIELDS
        ):
            _append_reason(reasons, REASON_REPLAY_REPORT_STATE_MISMATCH)
        for field_name in (
            "source_package_ref",
            "transaction_id",
            "ledger_id",
            "manifest_core_hash",
            "expected_manifest_core_hash",
            "stored_verification_status",
            "fresh_anchored_verification_status",
            "signature_mode",
        ):
            if not _safe_string(getattr(report, field_name), allow_empty=True):
                _append_reason(reasons, REASON_REPLAY_REPORT_STATE_MISMATCH)
        if (
            report.source_package_ref != ""
            and not _valid_source_package_ref(report.source_package_ref)
        ):
            _append_reason(reasons, REASON_REPLAY_REPORT_STATE_MISMATCH)
        if any(
            not _safe_report_identity_string(value)
            for value in (
                report.source_package_ref,
                report.transaction_id,
                report.ledger_id,
            )
        ):
            _append_reason(reasons, REASON_REPLAY_REPORT_STATE_MISMATCH)
        if (
            report.manifest_core_hash != ""
            and not _valid_sha256(report.manifest_core_hash)
        ):
            _append_reason(reasons, REASON_REPLAY_REPORT_STATE_MISMATCH)
        if (
            report.expected_manifest_core_hash != ""
            and not _valid_sha256(report.expected_manifest_core_hash)
        ):
            _append_reason(reasons, REASON_REPLAY_REPORT_STATE_MISMATCH)
        if report.stored_verification_status not in (
            "",
            *_KNOWN_STORED_VERIFICATION_STATUSES,
        ):
            _append_reason(reasons, REASON_REPLAY_REPORT_STATE_MISMATCH)
        if report.fresh_anchored_verification_status not in (
            "",
            *_KNOWN_FRESH_VERIFICATION_STATUSES,
        ):
            _append_reason(reasons, REASON_REPLAY_REPORT_STATE_MISMATCH)
        if report.signature_mode not in (
            "",
            crypto_contracts.SIGNATURE_MODE_UNSIGNED_PLACEHOLDER,
        ):
            _append_reason(reasons, REASON_REPLAY_REPORT_STATE_MISMATCH)
        if type(report.reconstructed_timeline) is not tuple or any(
            type(row) is not AirlineSealedTraceReplayTimelineRowV01
            or validate_airline_sealed_trace_replay_timeline_row_v01(
                row,
            ).validation_status
            != STATUS_PASS
            for row in report.reconstructed_timeline
        ):
            _append_reason(reasons, REASON_TIMELINE_ROW_INVALID)
        expected_status = (
            STATUS_PASS
            if _replay_report_pass_state(report, report.verification_errors)
            else STATUS_FAIL_CLOSED
        )
        if report.replay_status != expected_status:
            _append_reason(reasons, REASON_REPLAY_REPORT_STATE_MISMATCH)
        if report.replay_status == STATUS_FAIL_CLOSED and not report.verification_errors:
            _append_reason(reasons, REASON_REPLAY_REPORT_STATE_MISMATCH)
    except (TypeError, AttributeError, ValueError, KeyError, IndexError, RecursionError):
        _append_reason(reasons, REASON_REPLAY_REPORT_STATE_MISMATCH)
    return build_airline_sealed_trace_replay_validation_report_v01(tuple(reasons))


def airline_sealed_trace_replay_report_to_plain_dict_v01(
    report: AirlineSealedTraceReplayReportV01,
) -> dict[str, object]:
    validation = validate_airline_sealed_trace_replay_report_v01(report)
    if validation.validation_status != STATUS_PASS:
        raise ValueError(",".join(validation.validation_errors))
    return {
        "replay_status": report.replay_status,
        "replay_version": report.replay_version,
        "replay_id": report.replay_id,
        "source_package_ref": report.source_package_ref,
        "transaction_id": report.transaction_id,
        "ledger_id": report.ledger_id,
        "manifest_core_hash": report.manifest_core_hash,
        "expected_manifest_core_hash": report.expected_manifest_core_hash,
        "stored_verification_status": report.stored_verification_status,
        "fresh_anchored_verification_status": report.fresh_anchored_verification_status,
        "stored_verification_contract_verified": report.stored_verification_contract_verified,
        "fresh_anchored_verification_contract_verified": report.fresh_anchored_verification_contract_verified,
        "external_anchor_supplied": report.external_anchor_supplied,
        "external_anchor_verified": report.external_anchor_verified,
        "signature_mode": report.signature_mode,
        "signature_verified": report.signature_verified,
        "integrity_verified": report.integrity_verified,
        "continuity_verified": report.continuity_verified,
        "ledger_verified": report.ledger_verified,
        "manifest_binding_verified": report.manifest_binding_verified,
        "artifact_hashes_verified": report.artifact_hashes_verified,
        "chain_order_verified": report.chain_order_verified,
        "dependency_graph_verified": report.dependency_graph_verified,
        "root_ownership_verified": report.root_ownership_verified,
        "authority_evidence_boundaries_verified": report.authority_evidence_boundaries_verified,
        "packet_lineage_verified": report.packet_lineage_verified,
        "receipt_lineage_verified": report.receipt_lineage_verified,
        "transaction_identity_verified": report.transaction_identity_verified,
        "source_refs_verified": report.source_refs_verified,
        "secret_boundary_verified": report.secret_boundary_verified,
        "source_bytes_unchanged": report.source_bytes_unchanged,
        "critical_package_bytes_unchanged": report.critical_package_bytes_unchanged,
        "timeline_complete": report.timeline_complete,
        "root_attestation_required": report.root_attestation_required,
        "root_attestation_present": report.root_attestation_present,
        "source_file_count": report.source_file_count,
        "critical_package_file_count": report.critical_package_file_count,
        "ledger_entry_count": report.ledger_entry_count,
        "dependency_edge_count": report.dependency_edge_count,
        "root_final_count": report.root_final_count,
        "client_root_final_count": report.client_root_final_count,
        "airline_root_final_count": report.airline_root_final_count,
        "bank_root_final_count": report.bank_root_final_count,
        "timeline_row_count": report.timeline_row_count,
        "ledger_audit_count": report.ledger_audit_count,
        "anchored_verification_count": report.anchored_verification_count,
        "post_replay_snapshot_provider_call_count": report.post_replay_snapshot_provider_call_count,
        "transaction_rerun_count": report.transaction_rerun_count,
        "semantic_rerun_count": report.semantic_rerun_count,
        "corridor_rerun_count": report.corridor_rerun_count,
        "ledger_recollection_count": report.ledger_recollection_count,
        "crypto_collection_count": report.crypto_collection_count,
        "provider_call_count": report.provider_call_count,
        "network_call_count": report.network_call_count,
        "gemini_call_count": report.gemini_call_count,
        "replay_created_authority_count": report.replay_created_authority_count,
        "replay_created_permission_count": report.replay_created_permission_count,
        "replay_created_action_count": report.replay_created_action_count,
        "replay_created_packet_count": report.replay_created_packet_count,
        "replay_created_receipt_count": report.replay_created_receipt_count,
        "replay_created_final_output_count": report.replay_created_final_output_count,
        "real_world_effects_count": report.real_world_effects_count,
        "reconstructed_timeline": [
            airline_sealed_trace_replay_timeline_row_to_plain_dict_v01(row)
            for row in report.reconstructed_timeline
        ],
        "verification_errors": list(report.verification_errors),
    }


def _family_lineage_valid(
    entries: tuple[ledger_contracts.AirlineTransactionArtifactLedgerEntryV01, ...],
    artifact_types: tuple[str, ...],
) -> bool:
    positions = {entry.artifact_id: entry.ledger_index for entry in entries}
    family_entries = tuple(
        entry for entry in entries if entry.artifact_type in artifact_types
    )
    return (
        len(family_entries) == len(artifact_types)
        and tuple(entry.artifact_type for entry in family_entries) == artifact_types
        and all(
            all(
                dependency in positions
                and positions[dependency] < entry.ledger_index
                for dependency in entry.depends_on
            )
            for entry in family_entries
        )
    )


def _receipt_lineage_valid(
    entries: tuple[ledger_contracts.AirlineTransactionArtifactLedgerEntryV01, ...],
) -> bool:
    return _family_lineage_valid(entries, RECEIPT_ARTIFACT_TYPES) and all(
        entry.authority_class == ledger_contracts.AUTHORITY_EVIDENCE_ONLY_RECEIPT
        and entry.evidence_class == ledger_contracts.EVIDENCE_RECEIPT_ONLY
        for entry in entries
        if entry.artifact_type in RECEIPT_ARTIFACT_TYPES
    )


def _successful_report(
    replay_input: AirlineSealedTraceReplayInputV01,
    timeline: tuple[AirlineSealedTraceReplayTimelineRowV01, ...],
    *,
    critical_package_bytes_unchanged: bool,
    post_replay_snapshot_provider_call_count: int,
) -> AirlineSealedTraceReplayReportV01:
    input_validation = validate_airline_sealed_trace_replay_input_v01(
        replay_input,
    )
    if input_validation.validation_status != STATUS_PASS:
        return _failure_report(
            input_validation.validation_errors,
            replay_input,
        )
    if (
        type(timeline) is not tuple
        or any(
            type(row) is not AirlineSealedTraceReplayTimelineRowV01
            for row in timeline
        )
    ):
        return _failure_report((REASON_TIMELINE_INCOMPLETE,), replay_input)
    try:
        expected_timeline = build_airline_sealed_trace_replay_timeline_v01(
            replay_input,
        )
    except ValueError:
        return _failure_report((REASON_TIMELINE_INCOMPLETE,), replay_input)
    if timeline != expected_timeline:
        return _failure_report((REASON_TIMELINE_INCOMPLETE,), replay_input)
    if (
        type(critical_package_bytes_unchanged) is not bool
        or critical_package_bytes_unchanged is not True
    ):
        return _failure_report(
            (REASON_CRITICAL_PACKAGE_BYTES_CHANGED,),
            replay_input,
        )
    if (
        type(post_replay_snapshot_provider_call_count) is not int
        or post_replay_snapshot_provider_call_count != 1
    ):
        return _failure_report(
            (REASON_POST_REPLAY_SNAPSHOT_CALL_COUNT_MISMATCH,),
            replay_input,
        )

    audit = replay_input.accepted_ledger_audit
    ledger_item = replay_input.ledger_item
    envelope = replay_input.envelope
    stored = replay_input.stored_verification_report
    fresh = replay_input.fresh_anchored_verification_report
    entries = ledger_item.entries

    stored_contract = _verification_report_contract_valid(stored)
    fresh_contract = _verification_report_contract_valid(fresh)
    source_package_binding_valid = _source_package_binding_valid_v01(
        replay_input,
    )
    timeline_reasons = _timeline_validation_reasons(replay_input)
    dependency_valid = (
        not timeline_reasons
        and audit.dependencies_present is True
        and audit.dependencies_backward_only is True
        and audit.dependency_graph_acyclic is True
    )
    root_valid = (
        audit.root_ownership_valid is True
        and fresh.root_ownership_verified is True
        and audit.client_root_final_count == 1
        and audit.airline_root_final_count == 1
        and audit.bank_root_final_count == 1
    )
    boundary_valid = (
        audit.authority_evidence_boundaries_valid is True
        and fresh.authority_evidence_boundaries_verified is True
        and _ledger_direct_boundary_valid(ledger_item)
    )
    packet_valid = (
        _family_lineage_valid(entries, PACKET_ARTIFACT_TYPES)
        and audit.selected_offer_chain_consistent is True
    )
    receipt_valid = _receipt_lineage_valid(entries)
    identity_valid = (
        audit.transaction_identity_consistent is True
        and ledger_item.transaction_id == envelope.manifest_core.transaction_id
        and ledger_item.ledger_id == envelope.manifest_core.ledger_id
        and stored.transaction_id == ledger_item.transaction_id
        and fresh.transaction_id == ledger_item.transaction_id
        and stored.ledger_id == ledger_item.ledger_id
        and fresh.ledger_id == ledger_item.ledger_id
    )
    source_refs_valid = (
        audit.source_refs_consistent is True
        and audit.source_run_ref == ledger_item.source_run_ref
        and audit.source_causal_report_ref == ledger_item.source_causal_report_ref
        and audit.source_corridor_report_ref == ledger_item.source_corridor_report_ref
        and audit.required_source_files
        == tuple(row[0] for row in replay_input.ordered_source_files)
        == envelope.manifest_core.ordered_source_file_refs
    )
    secret_valid = (
        audit.secret_scan_passed is True
        and stored.secret_boundary_verified is True
        and fresh.secret_boundary_verified is True
        and all(
            entry.raw_secret_included is False
            and entry.raw_provider_text_included is False
            for entry in entries
        )
    )
    source_unchanged = (
        stored.source_bytes_unchanged is True
        and fresh.source_bytes_unchanged is True
        and source_package_binding_valid is True
    )
    manifest_binding = (
        identity_valid
        and tuple(entry.artifact_id for entry in entries)
        == envelope.manifest_core.ordered_artifact_refs
        and len(envelope.manifest_core.ordered_artifact_hashes)
        == LEDGER_ENTRY_COUNT
    )
    artifact_hashes_valid = (
        fresh.artifact_hashes_verified is True
        and len(envelope.manifest_core.ordered_artifact_hashes)
        == LEDGER_ENTRY_COUNT
        and all(
            _valid_sha256(value)
            for value in envelope.manifest_core.ordered_artifact_hashes
        )
    )
    chain_valid = (
        stored.chain_genesis_verified is True
        and stored.chain_order_verified is True
        and stored.chain_head_verified is True
        and stored.chain_tail_verified is True
        and fresh.chain_genesis_verified is True
        and fresh.chain_order_verified is True
        and fresh.chain_head_verified is True
        and fresh.chain_tail_verified is True
        and _valid_sha256(envelope.manifest_core.chain_genesis_hash)
        and _valid_sha256(envelope.manifest_core.chain_head_hash)
        and _valid_sha256(envelope.manifest_core.chain_tail_hash)
    )
    integrity = (
        stored_contract
        and fresh_contract
        and source_package_binding_valid is True
        and replay_input.expected_manifest_core_hash == envelope.manifest_core_hash
        and all(
            getattr(fresh, field_name) is True
            for field_name in _VERIFICATION_INTEGRITY_FLAG_FIELDS
        )
    )
    ledger_verified = (
        _accepted_audit_valid(audit)
        and ledger_item.validation_status == STATUS_PASS
        and ledger_item.validation_errors == ()
        and ledger_item.entry_count == LEDGER_ENTRY_COUNT
        and ledger_item.dependency_edge_count == DEPENDENCY_EDGE_COUNT
        and ledger_item.root_final_count == ROOT_FINAL_COUNT
    )
    timeline_complete = (
        len(timeline) == TIMELINE_ROW_COUNT
        and tuple(row.replay_index for row in timeline)
        == tuple(range(TIMELINE_ROW_COUNT))
        and all(
            validate_airline_sealed_trace_replay_timeline_row_v01(
                row,
            ).validation_status
            == STATUS_PASS
            for row in timeline
        )
    )
    continuity = (
        chain_valid
        and stored.source_package_hash_verified is True
        and fresh.source_package_hash_verified is True
        and source_package_binding_valid is True
        and dependency_valid
        and critical_package_bytes_unchanged
    )

    def emit_success() -> AirlineSealedTraceReplayReportV01:
        report = object.__new__(AirlineSealedTraceReplayReportV01)
        object.__setattr__(report, "_constructed_by_replay_verifier_v01", True)
        object.__setattr__(report, "replay_status", STATUS_FAIL_CLOSED)
        object.__setattr__(report, "replay_version", REPLAY_VERSION)
        object.__setattr__(
            report,
            "replay_id",
            (
                f"{REPLAY_ID_PREFIX}:{ledger_item.transaction_id}:"
                f"{envelope.manifest_core_hash}"
            ),
        )
        object.__setattr__(
            report,
            "source_package_ref",
            replay_input.source_package_ref,
        )
        object.__setattr__(report, "transaction_id", ledger_item.transaction_id)
        object.__setattr__(report, "ledger_id", ledger_item.ledger_id)
        object.__setattr__(
            report,
            "manifest_core_hash",
            envelope.manifest_core_hash,
        )
        object.__setattr__(
            report,
            "expected_manifest_core_hash",
            replay_input.expected_manifest_core_hash,
        )
        object.__setattr__(
            report,
            "stored_verification_status",
            stored.verification_status,
        )
        object.__setattr__(
            report,
            "fresh_anchored_verification_status",
            fresh.verification_status,
        )
        object.__setattr__(
            report,
            "stored_verification_contract_verified",
            stored_contract,
        )
        object.__setattr__(
            report,
            "fresh_anchored_verification_contract_verified",
            fresh_contract,
        )
        object.__setattr__(
            report,
            "external_anchor_supplied",
            fresh.external_anchor_supplied,
        )
        object.__setattr__(
            report,
            "external_anchor_verified",
            fresh.external_anchor_verified,
        )
        object.__setattr__(report, "signature_mode", fresh.signature_mode)
        object.__setattr__(report, "signature_verified", fresh.signature_verified)
        object.__setattr__(report, "integrity_verified", integrity)
        object.__setattr__(report, "continuity_verified", continuity)
        object.__setattr__(report, "ledger_verified", ledger_verified)
        object.__setattr__(report, "manifest_binding_verified", manifest_binding)
        object.__setattr__(report, "artifact_hashes_verified", artifact_hashes_valid)
        object.__setattr__(report, "chain_order_verified", chain_valid)
        object.__setattr__(report, "dependency_graph_verified", dependency_valid)
        object.__setattr__(report, "root_ownership_verified", root_valid)
        object.__setattr__(
            report,
            "authority_evidence_boundaries_verified",
            boundary_valid,
        )
        object.__setattr__(report, "packet_lineage_verified", packet_valid)
        object.__setattr__(report, "receipt_lineage_verified", receipt_valid)
        object.__setattr__(
            report,
            "transaction_identity_verified",
            identity_valid,
        )
        object.__setattr__(report, "source_refs_verified", source_refs_valid)
        object.__setattr__(report, "secret_boundary_verified", secret_valid)
        object.__setattr__(report, "source_bytes_unchanged", source_unchanged)
        object.__setattr__(
            report,
            "critical_package_bytes_unchanged",
            critical_package_bytes_unchanged,
        )
        object.__setattr__(report, "timeline_complete", timeline_complete)
        object.__setattr__(report, "root_attestation_required", False)
        object.__setattr__(report, "root_attestation_present", False)
        object.__setattr__(
            report,
            "source_file_count",
            len(replay_input.ordered_source_files),
        )
        object.__setattr__(
            report,
            "critical_package_file_count",
            CRITICAL_PACKAGE_FILE_COUNT,
        )
        object.__setattr__(report, "ledger_entry_count", len(entries))
        object.__setattr__(
            report,
            "dependency_edge_count",
            sum(len(entry.depends_on) for entry in entries),
        )
        object.__setattr__(
            report,
            "root_final_count",
            sum(
                1
                for entry in entries
                if entry.artifact_type in ROOT_FINAL_ARTIFACT_TYPES
            ),
        )
        object.__setattr__(
            report,
            "client_root_final_count",
            audit.client_root_final_count,
        )
        object.__setattr__(
            report,
            "airline_root_final_count",
            audit.airline_root_final_count,
        )
        object.__setattr__(
            report,
            "bank_root_final_count",
            audit.bank_root_final_count,
        )
        object.__setattr__(report, "timeline_row_count", len(timeline))
        object.__setattr__(report, "ledger_audit_count", 1)
        object.__setattr__(report, "anchored_verification_count", 1)
        object.__setattr__(
            report,
            "post_replay_snapshot_provider_call_count",
            post_replay_snapshot_provider_call_count,
        )
        object.__setattr__(report, "transaction_rerun_count", 0)
        object.__setattr__(report, "semantic_rerun_count", 0)
        object.__setattr__(report, "corridor_rerun_count", 0)
        object.__setattr__(report, "ledger_recollection_count", 0)
        object.__setattr__(report, "crypto_collection_count", 0)
        object.__setattr__(report, "provider_call_count", 0)
        object.__setattr__(report, "network_call_count", 0)
        object.__setattr__(report, "gemini_call_count", 0)
        object.__setattr__(report, "replay_created_authority_count", 0)
        object.__setattr__(report, "replay_created_permission_count", 0)
        object.__setattr__(report, "replay_created_action_count", 0)
        object.__setattr__(report, "replay_created_packet_count", 0)
        object.__setattr__(report, "replay_created_receipt_count", 0)
        object.__setattr__(report, "replay_created_final_output_count", 0)
        object.__setattr__(report, "real_world_effects_count", 0)
        object.__setattr__(report, "reconstructed_timeline", timeline)
        object.__setattr__(report, "verification_errors", ())
        return report

    report = emit_success()
    if not _replay_report_pass_state(report, ()):
        return _failure_report(
            (REASON_REPLAY_REPORT_STATE_MISMATCH,),
            replay_input,
        )
    object.__setattr__(report, "replay_status", STATUS_PASS)
    return report


def _failure_report(
    reasons: tuple[str, ...],
    replay_input: object,
) -> AirlineSealedTraceReplayReportV01:
    input_validation = validate_airline_sealed_trace_replay_input_v01(
        replay_input,
    )
    input_valid = input_validation.validation_status == STATUS_PASS
    source_package_ref = ""
    transaction_id = ""
    ledger_id = ""
    manifest_hash = ""
    expected_hash = ""
    stored_status = ""
    fresh_status = ""
    signature_mode = ""
    if input_valid and type(replay_input) is AirlineSealedTraceReplayInputV01:
        source_package_ref = replay_input.source_package_ref
        transaction_id = replay_input.ledger_item.transaction_id
        ledger_id = replay_input.ledger_item.ledger_id
        manifest_hash = replay_input.envelope.manifest_core_hash
        expected_hash = replay_input.expected_manifest_core_hash
        stored_status = replay_input.stored_verification_report.verification_status
        fresh_status = (
            replay_input.fresh_anchored_verification_report.verification_status
        )
        signature_mode = (
            replay_input.fresh_anchored_verification_report.signature_mode
        )
    normalized_reasons = _normalize_validation_errors(reasons)
    if not normalized_reasons:
        normalized_reasons = (REASON_REPLAY_REPORT_STATE_MISMATCH,)

    def emit_failure() -> AirlineSealedTraceReplayReportV01:
        report = object.__new__(AirlineSealedTraceReplayReportV01)
        object.__setattr__(report, "_constructed_by_replay_verifier_v01", True)
        object.__setattr__(report, "replay_status", STATUS_FAIL_CLOSED)
        object.__setattr__(report, "replay_version", REPLAY_VERSION)
        object.__setattr__(
            report,
            "replay_id",
            (
                f"{REPLAY_ID_PREFIX}:{transaction_id}:{manifest_hash}"
                if transaction_id and manifest_hash
                else ""
            ),
        )
        object.__setattr__(report, "source_package_ref", source_package_ref)
        object.__setattr__(report, "transaction_id", transaction_id)
        object.__setattr__(report, "ledger_id", ledger_id)
        object.__setattr__(report, "manifest_core_hash", manifest_hash)
        object.__setattr__(
            report,
            "expected_manifest_core_hash",
            expected_hash,
        )
        object.__setattr__(
            report,
            "stored_verification_status",
            stored_status,
        )
        object.__setattr__(
            report,
            "fresh_anchored_verification_status",
            fresh_status,
        )
        object.__setattr__(
            report,
            "stored_verification_contract_verified",
            False,
        )
        object.__setattr__(
            report,
            "fresh_anchored_verification_contract_verified",
            False,
        )
        object.__setattr__(report, "external_anchor_supplied", False)
        object.__setattr__(report, "external_anchor_verified", False)
        object.__setattr__(report, "signature_mode", signature_mode)
        object.__setattr__(report, "signature_verified", False)
        object.__setattr__(report, "integrity_verified", False)
        object.__setattr__(report, "continuity_verified", False)
        object.__setattr__(report, "ledger_verified", False)
        object.__setattr__(report, "manifest_binding_verified", False)
        object.__setattr__(report, "artifact_hashes_verified", False)
        object.__setattr__(report, "chain_order_verified", False)
        object.__setattr__(report, "dependency_graph_verified", False)
        object.__setattr__(report, "root_ownership_verified", False)
        object.__setattr__(
            report,
            "authority_evidence_boundaries_verified",
            False,
        )
        object.__setattr__(report, "packet_lineage_verified", False)
        object.__setattr__(report, "receipt_lineage_verified", False)
        object.__setattr__(report, "transaction_identity_verified", False)
        object.__setattr__(report, "source_refs_verified", False)
        object.__setattr__(report, "secret_boundary_verified", False)
        object.__setattr__(report, "source_bytes_unchanged", False)
        object.__setattr__(report, "critical_package_bytes_unchanged", False)
        object.__setattr__(report, "timeline_complete", False)
        object.__setattr__(report, "root_attestation_required", False)
        object.__setattr__(report, "root_attestation_present", False)
        object.__setattr__(report, "source_file_count", 0)
        object.__setattr__(report, "critical_package_file_count", 0)
        object.__setattr__(report, "ledger_entry_count", 0)
        object.__setattr__(report, "dependency_edge_count", 0)
        object.__setattr__(report, "root_final_count", 0)
        object.__setattr__(report, "client_root_final_count", 0)
        object.__setattr__(report, "airline_root_final_count", 0)
        object.__setattr__(report, "bank_root_final_count", 0)
        object.__setattr__(report, "timeline_row_count", 0)
        object.__setattr__(report, "ledger_audit_count", 0)
        object.__setattr__(report, "anchored_verification_count", 0)
        object.__setattr__(
            report,
            "post_replay_snapshot_provider_call_count",
            0,
        )
        object.__setattr__(report, "transaction_rerun_count", 0)
        object.__setattr__(report, "semantic_rerun_count", 0)
        object.__setattr__(report, "corridor_rerun_count", 0)
        object.__setattr__(report, "ledger_recollection_count", 0)
        object.__setattr__(report, "crypto_collection_count", 0)
        object.__setattr__(report, "provider_call_count", 0)
        object.__setattr__(report, "network_call_count", 0)
        object.__setattr__(report, "gemini_call_count", 0)
        object.__setattr__(report, "replay_created_authority_count", 0)
        object.__setattr__(report, "replay_created_permission_count", 0)
        object.__setattr__(report, "replay_created_action_count", 0)
        object.__setattr__(report, "replay_created_packet_count", 0)
        object.__setattr__(report, "replay_created_receipt_count", 0)
        object.__setattr__(report, "replay_created_final_output_count", 0)
        object.__setattr__(report, "real_world_effects_count", 0)
        object.__setattr__(report, "reconstructed_timeline", ())
        object.__setattr__(report, "verification_errors", normalized_reasons)
        return report

    return emit_failure()


def verify_airline_sealed_trace_replay_v01(
    replay_input: object,
    *,
    critical_package_bytes_unchanged: object,
    post_replay_snapshot_provider_call_count: object,
) -> AirlineSealedTraceReplayReportV01:
    reasons = list(_input_validation_reasons(replay_input))
    if type(critical_package_bytes_unchanged) is not bool or not critical_package_bytes_unchanged:
        _append_reason(reasons, REASON_CRITICAL_PACKAGE_BYTES_CHANGED)
    if (
        type(post_replay_snapshot_provider_call_count) is not int
        or post_replay_snapshot_provider_call_count != 1
    ):
        _append_reason(
            reasons,
            REASON_POST_REPLAY_SNAPSHOT_CALL_COUNT_MISMATCH,
        )
    if reasons or type(replay_input) is not AirlineSealedTraceReplayInputV01:
        return _failure_report(tuple(reasons), replay_input)
    try:
        timeline_reasons = _timeline_validation_reasons(replay_input)
        if timeline_reasons:
            return _failure_report(timeline_reasons, replay_input)
        timeline = build_airline_sealed_trace_replay_timeline_v01(replay_input)
        report = _successful_report(
            replay_input,
            timeline,
            critical_package_bytes_unchanged=critical_package_bytes_unchanged,
            post_replay_snapshot_provider_call_count=(
                post_replay_snapshot_provider_call_count
            ),
        )
        if report.replay_status != STATUS_PASS:
            return _failure_report(
                (
                    report.verification_errors
                    if report.verification_errors
                    else (REASON_REPLAY_REPORT_STATE_MISMATCH,)
                ),
                replay_input,
        )
        return report
    except ValueError:
        return _failure_report((REASON_TIMELINE_INCOMPLETE,), replay_input)
    except (TypeError, AttributeError, KeyError, IndexError, RecursionError):
        return _failure_report((REASON_TIMELINE_INCOMPLETE,), replay_input)
