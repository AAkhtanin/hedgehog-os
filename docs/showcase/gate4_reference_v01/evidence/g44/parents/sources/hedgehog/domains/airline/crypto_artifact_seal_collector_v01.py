"""Airline Crypto Artifact Seal v0.1 exact-source collector contracts.

Slice C1 validates one explicitly provided immutable source bundle. Slice C2
collects cryptographic integrity evidence from one accepted Airline source
bundle through one Manifest Core, one unsigned Envelope, one explicit
post-collection observation, and one pure B2b verification.

It does not discover source files or decide which package is authoritative.
It does not authenticate the provenance of an expected external anchor.
It does not prove semantic truth, create authority, grant permission, execute
an action, or create payment, ticket, booking, receipt, or FinalOutput.

An unanchored internally consistent result is not final PASS. An explicit
matching expected hash is caller-supplied trust input, not signer
authentication or PKI. Filesystem readers and writers, integration, audit,
anchor publication, signing, key management, and Replay remain unimplemented.
"""

from __future__ import annotations

from collections.abc import Mapping as MappingABC
from dataclasses import dataclass, fields, is_dataclass
from types import MappingProxyType
from typing import Callable, Mapping

from hedgehog.domains.airline import crypto_artifact_seal_v01 as seal_contracts
from hedgehog.domains.airline import transaction_artifact_ledger_v01 as ledger_contracts


MODULE_ID = "airline_crypto_artifact_seal_collector_v01"
SLICE_ID = "airline_crypto_artifact_seal_v01_slice_c1"
SLICE_C2_ID = "airline_crypto_artifact_seal_v01_slice_c2"

EXPECTED_LEDGER_AUDIT_ID = "airline_transaction_artifact_ledger_audit_v01"
EXPECTED_LEDGER_AUDIT_VERSION = "v0.1"

STATUS_PASS = seal_contracts.STATUS_PASS
STATUS_FAIL_CLOSED = seal_contracts.STATUS_FAIL_CLOSED
STATUS_SELF_CONSISTENT_UNANCHORED = (
    seal_contracts.STATUS_SELF_CONSISTENT_UNANCHORED
)
REQUIRED_SOURCE_FILE_REFS = seal_contracts.REQUIRED_SOURCE_FILE_REFS

AirlineCryptoPostCollectionSnapshotProviderV01 = Callable[[], object]

ACCEPTED_AUDIT_BOOLEAN_FIELDS = (
    "artifact_ids_unique",
    "ledger_indexes_contiguous",
    "artifact_type_sequence_valid",
    "dependencies_present",
    "dependencies_backward_only",
    "dependency_graph_acyclic",
    "root_final_set_valid",
    "root_ownership_valid",
    "authority_evidence_boundaries_valid",
    "canonical_hash_inputs_safe",
    "source_refs_consistent",
    "transaction_identity_consistent",
    "selected_offer_chain_consistent",
    "secret_scan_passed",
)

ACCEPTED_AUDIT_ZERO_COUNTER_FIELDS = (
    "audit_created_authority_count",
    "audit_created_permission_count",
    "audit_created_action_count",
    "semantic_rerun_count",
    "corridor_rerun_count",
    "ledger_collection_count",
    "provider_call_count",
    "network_call_count",
    "gemini_call_count",
    "crypto_operation_count",
    "replay_operation_count",
    "real_world_effects_count",
)

ACCEPTED_AUDIT_FIELD_NAMES = (
    "audit_id",
    "audit_version",
    "final_status",
    "required_source_files",
    "files_read_count",
    "ledger_id",
    "transaction_id",
    "selected_offer_id",
    "source_run_ref",
    "source_causal_report_ref",
    "source_corridor_report_ref",
    "actual_entry_count",
    "actual_dependency_edge_count",
    "actual_root_final_count",
    "client_root_final_count",
    "airline_root_final_count",
    "bank_root_final_count",
    *ACCEPTED_AUDIT_BOOLEAN_FIELDS,
    "stored_validation_status",
    "stored_validation_errors",
    *ACCEPTED_AUDIT_ZERO_COUNTER_FIELDS,
    "validation_errors",
)

SOURCE_BUNDLE_VALIDATION_REPORT_FIELD_NAMES = (
    "validation_status",
    "source_bundle_id",
    "source_package_ref",
    "accepted_audit_valid",
    "ledger_valid",
    "expected_identity_valid",
    "audit_ledger_identity_consistent",
    "audit_geometry_consistent",
    "source_refs_consistent",
    "selected_offer_consistent",
    "source_snapshot_before_valid",
    "source_snapshot_after_audit_valid",
    "source_file_order_consistent",
    "source_bytes_unchanged_after_audit",
    "source_indexes_equal",
    "ledger_document_matches_typed_ledger",
    "secret_boundary_valid",
    "runtime_boundary_valid",
    "validation_errors",
)

SOURCE_BUNDLE_REPORT_BOOLEAN_FIELDS = SOURCE_BUNDLE_VALIDATION_REPORT_FIELD_NAMES[3:-1]

COLLECTION_RESULT_FIELD_NAMES = (
    "collection_status",
    "source_bundle_id",
    "source_package_ref",
    "transaction_id",
    "ledger_id",
    "manifest_core_hash",
    "expected_manifest_core_hash",
    "source_bundle_validation_report",
    "manifest_core",
    "envelope",
    "verification_report",
    "source_bytes_unchanged_after_audit",
    "source_bytes_unchanged_after_collection",
    "source_bundle_validation_count",
    "manifest_core_collection_count",
    "envelope_collection_count",
    "post_collection_snapshot_provider_call_count",
    "verification_count",
    "audit_rerun_count",
    "ledger_recollection_count",
    "semantic_rerun_count",
    "corridor_rerun_count",
    "provider_call_count",
    "network_call_count",
    "gemini_call_count",
    "collector_created_authority_count",
    "collector_created_permission_count",
    "collector_created_action_count",
    "real_world_effects_count",
    "collection_errors",
)

COLLECTION_STAGE_COUNT_FIELDS = (
    "source_bundle_validation_count",
    "manifest_core_collection_count",
    "envelope_collection_count",
    "post_collection_snapshot_provider_call_count",
    "verification_count",
)

COLLECTION_ZERO_COUNTER_FIELDS = (
    "audit_rerun_count",
    "ledger_recollection_count",
    "semantic_rerun_count",
    "corridor_rerun_count",
    "provider_call_count",
    "network_call_count",
    "gemini_call_count",
    "collector_created_authority_count",
    "collector_created_permission_count",
    "collector_created_action_count",
    "real_world_effects_count",
)

REASON_ACCEPTED_AUDIT_WRONG_TYPE = "accepted_audit_wrong_type"
REASON_ACCEPTED_AUDIT_IDENTITY_MISMATCH = "accepted_audit_identity_mismatch"
REASON_ACCEPTED_AUDIT_STATUS_MISMATCH = "accepted_audit_status_mismatch"
REASON_ACCEPTED_AUDIT_REQUIRED_FILES_MISMATCH = (
    "accepted_audit_required_files_mismatch"
)
REASON_ACCEPTED_AUDIT_GEOMETRY_MISMATCH = "accepted_audit_geometry_mismatch"
REASON_ACCEPTED_AUDIT_ROOT_FINAL_MISMATCH = "accepted_audit_root_final_mismatch"
REASON_ACCEPTED_AUDIT_BOOLEAN_BOUNDARY_MISMATCH = (
    "accepted_audit_boolean_boundary_mismatch"
)
REASON_ACCEPTED_AUDIT_STORED_VALIDATION_MISMATCH = (
    "accepted_audit_stored_validation_mismatch"
)
REASON_ACCEPTED_AUDIT_VALIDATION_ERRORS_NOT_EMPTY = (
    "accepted_audit_validation_errors_not_empty"
)
REASON_ACCEPTED_AUDIT_ZERO_COUNTER_MISMATCH = (
    "accepted_audit_zero_counter_mismatch"
)
REASON_SOURCE_BUNDLE_WRONG_TYPE = "source_bundle_wrong_type"
REASON_SOURCE_BUNDLE_ID_INVALID = "source_bundle_id_invalid"
REASON_SOURCE_PACKAGE_REF_INVALID = "source_package_ref_invalid"
REASON_SOURCE_BUNDLE_AUDIT_INVALID = "source_bundle_audit_invalid"
REASON_SOURCE_BUNDLE_LEDGER_WRONG_TYPE = "source_bundle_ledger_wrong_type"
REASON_SOURCE_BUNDLE_EXPECTED_IDENTITY_WRONG_TYPE = (
    "source_bundle_expected_identity_wrong_type"
)
REASON_SOURCE_BUNDLE_LEDGER_VALIDATION_FAILED = (
    "source_bundle_ledger_validation_failed"
)
REASON_SOURCE_BUNDLE_LEDGER_AUDIT_IDENTITY_MISMATCH = (
    "source_bundle_ledger_audit_identity_mismatch"
)
REASON_SOURCE_BUNDLE_SOURCE_REFS_MISMATCH = "source_bundle_source_refs_mismatch"
REASON_SOURCE_BUNDLE_SELECTED_OFFER_MISMATCH = (
    "source_bundle_selected_offer_mismatch"
)
REASON_SOURCE_SNAPSHOT_BEFORE_MALFORMED = "source_snapshot_before_malformed"
REASON_SOURCE_SNAPSHOT_AFTER_AUDIT_MALFORMED = (
    "source_snapshot_after_audit_malformed"
)
REASON_SOURCE_SNAPSHOT_FILE_ORDER_MISMATCH = (
    "source_snapshot_file_order_mismatch"
)
REASON_SOURCE_SNAPSHOT_BYTES_CHANGED_DURING_AUDIT = (
    "source_snapshot_bytes_changed_during_audit"
)
REASON_SOURCE_SNAPSHOT_INDEX_MISMATCH = "source_snapshot_index_mismatch"
REASON_LEDGER_DOCUMENT_MISSING = "ledger_document_missing"
REASON_LEDGER_DOCUMENT_MALFORMED_JSON = "ledger_document_malformed_json"
REASON_LEDGER_DOCUMENT_OBJECT_MISMATCH = "ledger_document_object_mismatch"
REASON_LEDGER_DOCUMENT_PROJECTION_FAILED = "ledger_document_projection_failed"
REASON_SOURCE_BUNDLE_SECRET_BOUNDARY_MISMATCH = (
    "source_bundle_secret_boundary_mismatch"
)
REASON_SOURCE_BUNDLE_RUNTIME_BOUNDARY_MISMATCH = (
    "source_bundle_runtime_boundary_mismatch"
)
REASON_MALFORMED_VALIDATION_ERRORS = "malformed_validation_errors"

REASON_COLLECTION_RESULT_WRONG_TYPE = "collection_result_wrong_type"
REASON_COLLECTION_RESULT_FIELD_MISMATCH = "collection_result_field_mismatch"
REASON_COLLECTION_RESULT_STATUS_MISMATCH = "collection_result_status_mismatch"
REASON_COLLECTION_RESULT_STAGE_COUNT_MISMATCH = (
    "collection_result_stage_count_mismatch"
)
REASON_COLLECTION_RESULT_ZERO_COUNTER_MISMATCH = (
    "collection_result_zero_counter_mismatch"
)
REASON_COLLECTION_ERROR_CONTAINER_MALFORMED = (
    "collection_error_container_malformed"
)
REASON_COLLECTION_SOURCE_BUNDLE_VALIDATION_FAILED = (
    "source_bundle_validation_failed"
)
REASON_COLLECTION_SOURCE_BUNDLE_VALIDATION_REPORT_MALFORMED = (
    "source_bundle_validation_report_malformed"
)
REASON_POST_COLLECTION_SNAPSHOT_PROVIDER_INVALID = (
    "post_collection_snapshot_provider_invalid"
)
REASON_MANIFEST_CORE_COLLECTION_FAILED = "manifest_core_collection_failed"
REASON_ENVELOPE_COLLECTION_FAILED = "envelope_collection_failed"
REASON_POST_COLLECTION_SNAPSHOT_PROVIDER_FAILED = (
    "post_collection_snapshot_provider_failed"
)
REASON_POST_COLLECTION_SNAPSHOT_MALFORMED = (
    "post_collection_snapshot_malformed"
)
REASON_POST_COLLECTION_SOURCE_BYTES_CHANGED = (
    "post_collection_source_bytes_changed"
)
REASON_VERIFICATION_CALL_FAILED = "verification_call_failed"
REASON_VERIFICATION_REPORT_MISSING = "verification_report_missing"
REASON_VERIFICATION_REPORT_CONTRACT_INVALID = (
    "verification_report_contract_invalid"
)
REASON_COLLECTION_VERIFICATION_FAILED = "verification_failed"
REASON_COLLECTION_MANIFEST_ENVELOPE_MISMATCH = (
    "collection_manifest_envelope_mismatch"
)
REASON_COLLECTION_IDENTITY_MISMATCH = "collection_identity_mismatch"
REASON_COLLECTION_EXPECTED_ANCHOR_MISMATCH = (
    "collection_expected_anchor_mismatch"
)

COLLECTION_REASONS = (
    REASON_COLLECTION_RESULT_WRONG_TYPE,
    REASON_COLLECTION_RESULT_FIELD_MISMATCH,
    REASON_COLLECTION_RESULT_STATUS_MISMATCH,
    REASON_COLLECTION_RESULT_STAGE_COUNT_MISMATCH,
    REASON_COLLECTION_RESULT_ZERO_COUNTER_MISMATCH,
    REASON_COLLECTION_ERROR_CONTAINER_MALFORMED,
    REASON_COLLECTION_SOURCE_BUNDLE_VALIDATION_FAILED,
    REASON_COLLECTION_SOURCE_BUNDLE_VALIDATION_REPORT_MALFORMED,
    REASON_POST_COLLECTION_SNAPSHOT_PROVIDER_INVALID,
    REASON_MANIFEST_CORE_COLLECTION_FAILED,
    REASON_ENVELOPE_COLLECTION_FAILED,
    REASON_POST_COLLECTION_SNAPSHOT_PROVIDER_FAILED,
    REASON_POST_COLLECTION_SNAPSHOT_MALFORMED,
    REASON_POST_COLLECTION_SOURCE_BYTES_CHANGED,
    REASON_VERIFICATION_CALL_FAILED,
    REASON_VERIFICATION_REPORT_MISSING,
    REASON_VERIFICATION_REPORT_CONTRACT_INVALID,
    REASON_COLLECTION_VERIFICATION_FAILED,
    REASON_COLLECTION_MANIFEST_ENVELOPE_MISMATCH,
    REASON_COLLECTION_IDENTITY_MISMATCH,
    REASON_COLLECTION_EXPECTED_ANCHOR_MISMATCH,
)

VALIDATION_REASONS = (
    REASON_ACCEPTED_AUDIT_WRONG_TYPE,
    REASON_ACCEPTED_AUDIT_IDENTITY_MISMATCH,
    REASON_ACCEPTED_AUDIT_STATUS_MISMATCH,
    REASON_ACCEPTED_AUDIT_REQUIRED_FILES_MISMATCH,
    REASON_ACCEPTED_AUDIT_GEOMETRY_MISMATCH,
    REASON_ACCEPTED_AUDIT_ROOT_FINAL_MISMATCH,
    REASON_ACCEPTED_AUDIT_BOOLEAN_BOUNDARY_MISMATCH,
    REASON_ACCEPTED_AUDIT_STORED_VALIDATION_MISMATCH,
    REASON_ACCEPTED_AUDIT_VALIDATION_ERRORS_NOT_EMPTY,
    REASON_ACCEPTED_AUDIT_ZERO_COUNTER_MISMATCH,
    REASON_SOURCE_BUNDLE_WRONG_TYPE,
    REASON_SOURCE_BUNDLE_ID_INVALID,
    REASON_SOURCE_PACKAGE_REF_INVALID,
    REASON_SOURCE_BUNDLE_AUDIT_INVALID,
    REASON_SOURCE_BUNDLE_LEDGER_WRONG_TYPE,
    REASON_SOURCE_BUNDLE_EXPECTED_IDENTITY_WRONG_TYPE,
    REASON_SOURCE_BUNDLE_LEDGER_VALIDATION_FAILED,
    REASON_SOURCE_BUNDLE_LEDGER_AUDIT_IDENTITY_MISMATCH,
    REASON_SOURCE_BUNDLE_SOURCE_REFS_MISMATCH,
    REASON_SOURCE_BUNDLE_SELECTED_OFFER_MISMATCH,
    REASON_SOURCE_SNAPSHOT_BEFORE_MALFORMED,
    REASON_SOURCE_SNAPSHOT_AFTER_AUDIT_MALFORMED,
    REASON_SOURCE_SNAPSHOT_FILE_ORDER_MISMATCH,
    REASON_SOURCE_SNAPSHOT_BYTES_CHANGED_DURING_AUDIT,
    REASON_SOURCE_SNAPSHOT_INDEX_MISMATCH,
    REASON_LEDGER_DOCUMENT_MISSING,
    REASON_LEDGER_DOCUMENT_MALFORMED_JSON,
    REASON_LEDGER_DOCUMENT_OBJECT_MISMATCH,
    REASON_LEDGER_DOCUMENT_PROJECTION_FAILED,
    REASON_SOURCE_BUNDLE_SECRET_BOUNDARY_MISMATCH,
    REASON_SOURCE_BUNDLE_RUNTIME_BOUNDARY_MISMATCH,
    REASON_MALFORMED_VALIDATION_ERRORS,
)


@dataclass(frozen=True)
class AirlineCryptoArtifactSealAcceptedLedgerAuditV01:
    audit_id: str
    audit_version: str
    final_status: str
    required_source_files: tuple[str, ...]
    files_read_count: int
    ledger_id: str
    transaction_id: str
    selected_offer_id: str
    source_run_ref: str
    source_causal_report_ref: str
    source_corridor_report_ref: str
    actual_entry_count: int
    actual_dependency_edge_count: int
    actual_root_final_count: int
    client_root_final_count: int
    airline_root_final_count: int
    bank_root_final_count: int
    artifact_ids_unique: bool
    ledger_indexes_contiguous: bool
    artifact_type_sequence_valid: bool
    dependencies_present: bool
    dependencies_backward_only: bool
    dependency_graph_acyclic: bool
    root_final_set_valid: bool
    root_ownership_valid: bool
    authority_evidence_boundaries_valid: bool
    canonical_hash_inputs_safe: bool
    source_refs_consistent: bool
    transaction_identity_consistent: bool
    selected_offer_chain_consistent: bool
    secret_scan_passed: bool
    stored_validation_status: str
    stored_validation_errors: tuple[str, ...]
    audit_created_authority_count: int
    audit_created_permission_count: int
    audit_created_action_count: int
    semantic_rerun_count: int
    corridor_rerun_count: int
    ledger_collection_count: int
    provider_call_count: int
    network_call_count: int
    gemini_call_count: int
    crypto_operation_count: int
    replay_operation_count: int
    real_world_effects_count: int
    validation_errors: tuple[str, ...]

    def __post_init__(self) -> None:
        object.__setattr__(
            self,
            "required_source_files",
            _freeze_sequence_or_empty(self.required_source_files),
        )
        object.__setattr__(
            self,
            "stored_validation_errors",
            _freeze_errors(self.stored_validation_errors),
        )
        object.__setattr__(
            self,
            "validation_errors",
            _freeze_errors(self.validation_errors),
        )


@dataclass(frozen=True)
class AirlineCryptoArtifactSealSourceBundleV01:
    source_bundle_id: str
    source_package_ref: str
    accepted_audit: AirlineCryptoArtifactSealAcceptedLedgerAuditV01
    ledger_item: ledger_contracts.AirlineTransactionArtifactLedgerV01
    expected_identity: ledger_contracts.AirlineTransactionArtifactLedgerExpectedIdentityV01
    ordered_source_files_before_audit: tuple[tuple[str, bytes], ...]
    ordered_source_files_after_audit: tuple[tuple[str, bytes], ...]

    def __post_init__(self) -> None:
        before = _freeze_valid_snapshot(self.ordered_source_files_before_audit)
        after = _freeze_valid_snapshot(self.ordered_source_files_after_audit)
        object.__setattr__(
            self,
            "ordered_source_files_before_audit",
            before if before is not None else (),
        )
        object.__setattr__(
            self,
            "ordered_source_files_after_audit",
            after if after is not None else (),
        )


@dataclass(frozen=True)
class AirlineCryptoArtifactSealSourceBundleValidationReportV01:
    validation_status: str
    source_bundle_id: str
    source_package_ref: str
    accepted_audit_valid: bool
    ledger_valid: bool
    expected_identity_valid: bool
    audit_ledger_identity_consistent: bool
    audit_geometry_consistent: bool
    source_refs_consistent: bool
    selected_offer_consistent: bool
    source_snapshot_before_valid: bool
    source_snapshot_after_audit_valid: bool
    source_file_order_consistent: bool
    source_bytes_unchanged_after_audit: bool
    source_indexes_equal: bool
    ledger_document_matches_typed_ledger: bool
    secret_boundary_valid: bool
    runtime_boundary_valid: bool
    validation_errors: tuple[str, ...]

    def __post_init__(self) -> None:
        errors = _freeze_errors(self.validation_errors)
        identity_valid = _source_bundle_report_identity_valid(
            self.source_bundle_id,
            self.source_package_ref,
        )
        all_flags_true = all(
            type(getattr(self, field_name)) is bool
            and getattr(self, field_name) is True
            for field_name in SOURCE_BUNDLE_REPORT_BOOLEAN_FIELDS
        )
        object.__setattr__(self, "validation_errors", errors)
        object.__setattr__(
            self,
            "validation_status",
            (
                STATUS_PASS
                if not errors and identity_valid and all_flags_true
                else STATUS_FAIL_CLOSED
            ),
        )


@dataclass(frozen=True)
class AirlineCryptoArtifactSealCollectionResultV01:
    collection_status: str
    source_bundle_id: str
    source_package_ref: str
    transaction_id: str
    ledger_id: str
    manifest_core_hash: str
    expected_manifest_core_hash: str | None
    source_bundle_validation_report: (
        AirlineCryptoArtifactSealSourceBundleValidationReportV01
    )
    manifest_core: seal_contracts.AirlineCryptoArtifactSealManifestCoreV01 | None
    envelope: seal_contracts.AirlineCryptoArtifactSealEnvelopeV01 | None
    verification_report: (
        seal_contracts.AirlineCryptoArtifactSealVerificationReportV01 | None
    )
    source_bytes_unchanged_after_audit: bool
    source_bytes_unchanged_after_collection: bool
    source_bundle_validation_count: int
    manifest_core_collection_count: int
    envelope_collection_count: int
    post_collection_snapshot_provider_call_count: int
    verification_count: int
    audit_rerun_count: int
    ledger_recollection_count: int
    semantic_rerun_count: int
    corridor_rerun_count: int
    provider_call_count: int
    network_call_count: int
    gemini_call_count: int
    collector_created_authority_count: int
    collector_created_permission_count: int
    collector_created_action_count: int
    real_world_effects_count: int
    collection_errors: tuple[str, ...]

    def __post_init__(self) -> None:
        errors = _freeze_collection_errors(self.collection_errors)
        object.__setattr__(self, "collection_errors", errors)
        object.__setattr__(
            self,
            "collection_status",
            _derive_collection_status(self, errors),
        )


def validate_airline_crypto_artifact_seal_accepted_ledger_audit_v01(
    accepted_audit: object,
) -> seal_contracts.AirlineCryptoArtifactSealValidationReportV01:
    errors: list[str] = []
    try:
        if type(accepted_audit) is not AirlineCryptoArtifactSealAcceptedLedgerAuditV01:
            return seal_contracts.build_airline_crypto_validation_report_v01(
                [REASON_ACCEPTED_AUDIT_WRONG_TYPE],
            )
        if (
            type(accepted_audit.audit_id) is not str
            or accepted_audit.audit_id != EXPECTED_LEDGER_AUDIT_ID
            or type(accepted_audit.audit_version) is not str
            or accepted_audit.audit_version != EXPECTED_LEDGER_AUDIT_VERSION
        ):
            _append(errors, REASON_ACCEPTED_AUDIT_IDENTITY_MISMATCH)
        if type(accepted_audit.final_status) is not str or accepted_audit.final_status != STATUS_PASS:
            _append(errors, REASON_ACCEPTED_AUDIT_STATUS_MISMATCH)
        if (
            type(accepted_audit.required_source_files) is not tuple
            or any(
                type(ref) is not str
                for ref in accepted_audit.required_source_files
            )
            or accepted_audit.required_source_files != REQUIRED_SOURCE_FILE_REFS
        ):
            _append(errors, REASON_ACCEPTED_AUDIT_REQUIRED_FILES_MISMATCH)
        if not _exact_int_equal(accepted_audit.files_read_count, 9):
            _append(errors, REASON_ACCEPTED_AUDIT_REQUIRED_FILES_MISMATCH)
        for field_name in (
            "ledger_id",
            "transaction_id",
            "selected_offer_id",
            "source_run_ref",
            "source_causal_report_ref",
            "source_corridor_report_ref",
        ):
            if not _safe_non_empty_string(getattr(accepted_audit, field_name)):
                _append(errors, REASON_ACCEPTED_AUDIT_IDENTITY_MISMATCH)
        if not (
            _exact_int_equal(accepted_audit.actual_entry_count, 19)
            and _exact_int_equal(accepted_audit.actual_dependency_edge_count, 29)
            and _exact_int_equal(accepted_audit.actual_root_final_count, 3)
        ):
            _append(errors, REASON_ACCEPTED_AUDIT_GEOMETRY_MISMATCH)
        if not (
            _exact_int_equal(accepted_audit.client_root_final_count, 1)
            and _exact_int_equal(accepted_audit.airline_root_final_count, 1)
            and _exact_int_equal(accepted_audit.bank_root_final_count, 1)
        ):
            _append(errors, REASON_ACCEPTED_AUDIT_ROOT_FINAL_MISMATCH)
        if any(
            type(getattr(accepted_audit, field_name)) is not bool
            or getattr(accepted_audit, field_name) is not True
            for field_name in ACCEPTED_AUDIT_BOOLEAN_FIELDS
        ):
            _append(errors, REASON_ACCEPTED_AUDIT_BOOLEAN_BOUNDARY_MISMATCH)
        if (
            type(accepted_audit.stored_validation_status) is not str
            or accepted_audit.stored_validation_status != STATUS_PASS
            or type(accepted_audit.stored_validation_errors) is not tuple
            or accepted_audit.stored_validation_errors != ()
        ):
            _append(errors, REASON_ACCEPTED_AUDIT_STORED_VALIDATION_MISMATCH)
        if (
            type(accepted_audit.validation_errors) is not tuple
            or accepted_audit.validation_errors != ()
        ):
            _append(errors, REASON_ACCEPTED_AUDIT_VALIDATION_ERRORS_NOT_EMPTY)
        if any(
            not _exact_int_equal(getattr(accepted_audit, field_name), 0)
            for field_name in ACCEPTED_AUDIT_ZERO_COUNTER_FIELDS
        ):
            _append(errors, REASON_ACCEPTED_AUDIT_ZERO_COUNTER_MISMATCH)
    except (TypeError, AttributeError, ValueError, KeyError, IndexError, RecursionError):
        _append(errors, REASON_ACCEPTED_AUDIT_WRONG_TYPE)
    return seal_contracts.build_airline_crypto_validation_report_v01(errors)


def airline_crypto_artifact_seal_ledger_document_to_plain_dict_v01(
    ledger_item: ledger_contracts.AirlineTransactionArtifactLedgerV01,
    *,
    expected_identity: ledger_contracts.AirlineTransactionArtifactLedgerExpectedIdentityV01,
) -> dict[str, object]:
    try:
        valid, _ = _validate_accepted_ledger(
            ledger_item,
            expected_identity=expected_identity,
        )
        if not valid:
            raise ValueError(REASON_LEDGER_DOCUMENT_PROJECTION_FAILED)
        projected = _project_ledger_value(ledger_item, set())
        if type(projected) is not dict:
            raise ValueError(REASON_LEDGER_DOCUMENT_PROJECTION_FAILED)
        report = seal_contracts.validate_airline_crypto_canonical_json_value_v01(
            projected,
        )
        if report.validation_status != STATUS_PASS:
            raise ValueError(REASON_LEDGER_DOCUMENT_PROJECTION_FAILED)
        return projected
    except (TypeError, AttributeError, KeyError, IndexError, RecursionError) as exc:
        raise ValueError(REASON_LEDGER_DOCUMENT_PROJECTION_FAILED) from exc


def validate_airline_crypto_artifact_seal_source_bundle_v01(
    source_bundle: object,
) -> AirlineCryptoArtifactSealSourceBundleValidationReportV01:
    if type(source_bundle) is not AirlineCryptoArtifactSealSourceBundleV01:
        return _source_bundle_report(
            errors=(REASON_SOURCE_BUNDLE_WRONG_TYPE,),
        )

    errors: list[str] = []
    flags = {field_name: False for field_name in SOURCE_BUNDLE_REPORT_BOOLEAN_FIELDS}
    try:
        bundle_id_valid = _safe_non_empty_string(source_bundle.source_bundle_id)
        if not bundle_id_valid:
            _append(errors, REASON_SOURCE_BUNDLE_ID_INVALID)
        package_ref_report = seal_contracts.validate_airline_crypto_source_package_ref_v01(
            source_bundle.source_package_ref,
        )
        if package_ref_report.validation_status != STATUS_PASS:
            _append(errors, REASON_SOURCE_PACKAGE_REF_INVALID)

        audit_report = validate_airline_crypto_artifact_seal_accepted_ledger_audit_v01(
            source_bundle.accepted_audit,
        )
        flags["accepted_audit_valid"] = audit_report.validation_status == STATUS_PASS
        if not flags["accepted_audit_valid"]:
            _append(errors, REASON_SOURCE_BUNDLE_AUDIT_INVALID)

        flags["expected_identity_valid"] = (
            type(source_bundle.expected_identity)
            is ledger_contracts.AirlineTransactionArtifactLedgerExpectedIdentityV01
        )
        if not flags["expected_identity_valid"]:
            _append(errors, REASON_SOURCE_BUNDLE_EXPECTED_IDENTITY_WRONG_TYPE)

        if type(source_bundle.ledger_item) is not ledger_contracts.AirlineTransactionArtifactLedgerV01:
            _append(errors, REASON_SOURCE_BUNDLE_LEDGER_WRONG_TYPE)
            ledger_geometry = None
        elif flags["expected_identity_valid"]:
            flags["ledger_valid"], ledger_geometry = _validate_accepted_ledger(
                source_bundle.ledger_item,
                expected_identity=source_bundle.expected_identity,
            )
            if not flags["ledger_valid"]:
                _append(errors, REASON_SOURCE_BUNDLE_LEDGER_VALIDATION_FAILED)
        else:
            ledger_geometry = None

        before_shape, before_order = _validate_snapshot_shape(
            source_bundle.ordered_source_files_before_audit,
        )
        after_shape, after_order = _validate_snapshot_shape(
            source_bundle.ordered_source_files_after_audit,
        )
        flags["source_snapshot_before_valid"] = before_shape and before_order
        flags["source_snapshot_after_audit_valid"] = after_shape and after_order
        flags["source_file_order_consistent"] = before_order and after_order
        if not before_shape:
            _append(errors, REASON_SOURCE_SNAPSHOT_BEFORE_MALFORMED)
        if not after_shape:
            _append(errors, REASON_SOURCE_SNAPSHOT_AFTER_AUDIT_MALFORMED)
        if before_shape and after_shape and not flags["source_file_order_consistent"]:
            _append(errors, REASON_SOURCE_SNAPSHOT_FILE_ORDER_MISMATCH)

        before_index = None
        after_index = None
        if flags["ledger_valid"] and flags["source_snapshot_before_valid"]:
            before_index = seal_contracts.build_airline_crypto_source_package_index_v01(
                transaction_id=source_bundle.ledger_item.transaction_id,
                ordered_source_files=source_bundle.ordered_source_files_before_audit,
            )
        if flags["ledger_valid"] and flags["source_snapshot_after_audit_valid"]:
            after_index = seal_contracts.build_airline_crypto_source_package_index_v01(
                transaction_id=source_bundle.ledger_item.transaction_id,
                ordered_source_files=source_bundle.ordered_source_files_after_audit,
            )
        if flags["source_snapshot_before_valid"] and flags["source_snapshot_after_audit_valid"]:
            flags["source_bytes_unchanged_after_audit"] = (
                source_bundle.ordered_source_files_before_audit
                == source_bundle.ordered_source_files_after_audit
            )
            if not flags["source_bytes_unchanged_after_audit"]:
                _append(errors, REASON_SOURCE_SNAPSHOT_BYTES_CHANGED_DURING_AUDIT)
        if before_index is not None and after_index is not None:
            flags["source_indexes_equal"] = before_index == after_index
            if not flags["source_indexes_equal"]:
                _append(errors, REASON_SOURCE_SNAPSHOT_INDEX_MISMATCH)

        if flags["accepted_audit_valid"] and flags["ledger_valid"]:
            audit = source_bundle.accepted_audit
            item = source_bundle.ledger_item
            flags["audit_ledger_identity_consistent"] = (
                audit.ledger_id == item.ledger_id
                and audit.transaction_id == item.transaction_id
            )
            if not flags["audit_ledger_identity_consistent"]:
                _append(errors, REASON_SOURCE_BUNDLE_LEDGER_AUDIT_IDENTITY_MISMATCH)
            flags["audit_geometry_consistent"] = ledger_geometry == (
                audit.actual_entry_count,
                audit.actual_dependency_edge_count,
                audit.actual_root_final_count,
            )
            if not flags["audit_geometry_consistent"]:
                _append(errors, REASON_ACCEPTED_AUDIT_GEOMETRY_MISMATCH)
            flags["source_refs_consistent"] = _source_refs_match(
                audit,
                item,
                source_bundle.expected_identity,
            )
            if not flags["source_refs_consistent"]:
                _append(errors, REASON_SOURCE_BUNDLE_SOURCE_REFS_MISMATCH)
            flags["selected_offer_consistent"] = _selected_offer_matches(
                item,
                audit.selected_offer_id,
            )
            if not flags["selected_offer_consistent"]:
                _append(errors, REASON_SOURCE_BUNDLE_SELECTED_OFFER_MISMATCH)
            flags["secret_boundary_valid"] = _secret_boundary_valid(audit, item)
            if not flags["secret_boundary_valid"]:
                _append(errors, REASON_SOURCE_BUNDLE_SECRET_BOUNDARY_MISMATCH)
            flags["runtime_boundary_valid"] = _runtime_boundary_valid(audit, item)
            if not flags["runtime_boundary_valid"]:
                _append(errors, REASON_SOURCE_BUNDLE_RUNTIME_BOUNDARY_MISMATCH)

        if flags["ledger_valid"] and before_shape:
            flags["ledger_document_matches_typed_ledger"] = _ledger_document_matches(
                source_bundle.ledger_item,
                source_bundle.expected_identity,
                source_bundle.ordered_source_files_before_audit,
                errors,
            )
    except (TypeError, AttributeError, ValueError, KeyError, IndexError, RecursionError):
        _append(errors, REASON_SOURCE_BUNDLE_LEDGER_VALIDATION_FAILED)

    safe_source_bundle_id, safe_source_package_ref = _safe_source_bundle_identity(
        source_bundle,
    )
    return _source_bundle_report(
        source_bundle_id=safe_source_bundle_id,
        source_package_ref=safe_source_package_ref,
        flags=flags,
        errors=tuple(errors),
    )


def build_airline_crypto_artifact_seal_source_bundle_v01(
    *,
    source_bundle_id: str,
    source_package_ref: str,
    accepted_audit: AirlineCryptoArtifactSealAcceptedLedgerAuditV01,
    ledger_item: ledger_contracts.AirlineTransactionArtifactLedgerV01,
    expected_identity: ledger_contracts.AirlineTransactionArtifactLedgerExpectedIdentityV01,
    ordered_source_files_before_audit: tuple[tuple[str, bytes], ...],
    ordered_source_files_after_audit: tuple[tuple[str, bytes], ...],
) -> AirlineCryptoArtifactSealSourceBundleV01:
    bundle = AirlineCryptoArtifactSealSourceBundleV01(
        source_bundle_id=source_bundle_id,
        source_package_ref=source_package_ref,
        accepted_audit=accepted_audit,
        ledger_item=ledger_item,
        expected_identity=expected_identity,
        ordered_source_files_before_audit=ordered_source_files_before_audit,
        ordered_source_files_after_audit=ordered_source_files_after_audit,
    )
    report = validate_airline_crypto_artifact_seal_source_bundle_v01(bundle)
    if report.validation_status != STATUS_PASS:
        raise ValueError(report.validation_errors[0])
    return bundle


def validate_airline_crypto_artifact_seal_collection_result_v01(
    result: object,
) -> seal_contracts.AirlineCryptoArtifactSealValidationReportV01:
    errors: list[str] = []
    if type(result) is not AirlineCryptoArtifactSealCollectionResultV01:
        return seal_contracts.build_airline_crypto_validation_report_v01(
            [REASON_COLLECTION_RESULT_WRONG_TYPE],
        )
    try:
        if (
            type(result.collection_status) is not str
            or result.collection_status
            not in (
                STATUS_PASS,
                STATUS_FAIL_CLOSED,
                STATUS_SELF_CONSISTENT_UNANCHORED,
            )
            or type(result.collection_errors) is not tuple
            or result.collection_errors
            != _freeze_collection_errors(result.collection_errors)
        ):
            _append(errors, REASON_COLLECTION_ERROR_CONTAINER_MALFORMED)
        if not _collection_identity_strings_valid(result):
            _append(errors, REASON_COLLECTION_RESULT_FIELD_MISMATCH)
        for reason in _source_bundle_report_contract_errors(
            result.source_bundle_validation_report,
        ):
            _append(errors, reason)
        for reason in _collection_stage_contract_errors(result):
            _append(errors, reason)
        if any(
            not _exact_int_equal(getattr(result, field_name), 0)
            for field_name in COLLECTION_ZERO_COUNTER_FIELDS
        ):
            _append(errors, REASON_COLLECTION_RESULT_ZERO_COUNTER_MISMATCH)
        for reason in _collection_nested_contract_errors(result):
            _append(errors, reason)
        for reason in _collection_duplicate_coherence_errors(result):
            _append(errors, reason)
        expected_status = _derive_collection_status(
            result,
            result.collection_errors,
        )
        if result.collection_status != expected_status:
            _append(errors, REASON_COLLECTION_RESULT_STATUS_MISMATCH)
        if result.collection_status == STATUS_FAIL_CLOSED and not result.collection_errors:
            _append(errors, REASON_COLLECTION_RESULT_STATUS_MISMATCH)
        if (
            result.source_bundle_validation_report.validation_status
            != STATUS_PASS
            and REASON_COLLECTION_SOURCE_BUNDLE_VALIDATION_FAILED
            not in result.collection_errors
        ):
            _append(errors, REASON_COLLECTION_RESULT_FIELD_MISMATCH)
        if (
            result.verification_report is not None
            and result.verification_report.verification_status
            == STATUS_FAIL_CLOSED
            and REASON_COLLECTION_VERIFICATION_FAILED
            not in result.collection_errors
        ):
            _append(errors, REASON_COLLECTION_RESULT_FIELD_MISMATCH)
    except (TypeError, AttributeError, ValueError, KeyError, IndexError, RecursionError):
        _append(errors, REASON_COLLECTION_RESULT_FIELD_MISMATCH)
    return seal_contracts.build_airline_crypto_validation_report_v01(errors)


def airline_crypto_artifact_seal_collection_result_to_plain_dict_v01(
    result: AirlineCryptoArtifactSealCollectionResultV01,
) -> dict[str, object]:
    validation = validate_airline_crypto_artifact_seal_collection_result_v01(
        result,
    )
    if validation.validation_status != STATUS_PASS:
        raise ValueError(validation.validation_errors[0])
    plain = _collection_result_plain_dict_unchecked(result)
    if tuple(plain) != COLLECTION_RESULT_FIELD_NAMES:
        raise ValueError(REASON_COLLECTION_RESULT_FIELD_MISMATCH)
    canonical = seal_contracts.validate_airline_crypto_canonical_json_value_v01(
        plain,
    )
    if canonical.validation_status != STATUS_PASS:
        raise ValueError(REASON_COLLECTION_RESULT_FIELD_MISMATCH)
    return plain


def collect_airline_crypto_artifact_seal_from_source_bundle_v01(
    *,
    source_bundle: object,
    post_collection_snapshot_provider: object,
    expected_manifest_core_hash: object | None = None,
) -> AirlineCryptoArtifactSealCollectionResultV01:
    stage_counts = {
        field_name: 0 for field_name in COLLECTION_STAGE_COUNT_FIELDS
    }
    safe_expected_anchor = _safe_expected_anchor_for_result(
        expected_manifest_core_hash,
    )
    expected_anchor_input_malformed = (
        expected_manifest_core_hash is not None
        and safe_expected_anchor is None
    )
    stage_counts["source_bundle_validation_count"] = 1
    try:
        source_report = validate_airline_crypto_artifact_seal_source_bundle_v01(
            source_bundle,
        )
    except Exception:
        source_report = _source_bundle_report(
            errors=(REASON_SOURCE_BUNDLE_WRONG_TYPE,),
        )
        return _collection_result(
            source_report=source_report,
            stage_counts=stage_counts,
            expected_manifest_core_hash=safe_expected_anchor,
            errors=(
                REASON_COLLECTION_SOURCE_BUNDLE_VALIDATION_REPORT_MALFORMED,
                REASON_COLLECTION_SOURCE_BUNDLE_VALIDATION_FAILED,
            ),
        )
    source_report_errors = _source_bundle_report_contract_errors(source_report)
    if source_report_errors:
        source_report = _source_bundle_report(
            errors=(REASON_SOURCE_BUNDLE_WRONG_TYPE,),
        )
        return _collection_result(
            source_report=source_report,
            stage_counts=stage_counts,
            expected_manifest_core_hash=safe_expected_anchor,
            errors=(
                REASON_COLLECTION_SOURCE_BUNDLE_VALIDATION_REPORT_MALFORMED,
                REASON_COLLECTION_SOURCE_BUNDLE_VALIDATION_FAILED,
            ),
        )
    safe_source_bundle_id, safe_source_package_ref = _safe_source_bundle_identity(
        source_bundle,
    )
    if (
        source_report.source_bundle_id != safe_source_bundle_id
        or source_report.source_package_ref != safe_source_package_ref
    ):
        source_report = _source_bundle_report(
            source_bundle_id=safe_source_bundle_id,
            source_package_ref=safe_source_package_ref,
            errors=(REASON_SOURCE_BUNDLE_WRONG_TYPE,),
        )
        return _collection_result(
            source_report=source_report,
            stage_counts=stage_counts,
            expected_manifest_core_hash=safe_expected_anchor,
            errors=(
                REASON_COLLECTION_SOURCE_BUNDLE_VALIDATION_REPORT_MALFORMED,
                REASON_COLLECTION_SOURCE_BUNDLE_VALIDATION_FAILED,
                REASON_COLLECTION_IDENTITY_MISMATCH,
            ),
        )
    if (
        source_report.validation_status != STATUS_PASS
        or type(source_bundle) is not AirlineCryptoArtifactSealSourceBundleV01
    ):
        return _collection_result(
            source_report=source_report,
            stage_counts=stage_counts,
            expected_manifest_core_hash=safe_expected_anchor,
            errors=(REASON_COLLECTION_SOURCE_BUNDLE_VALIDATION_FAILED,),
        )
    if not callable(post_collection_snapshot_provider):
        return _collection_result(
            source_report=source_report,
            source_bundle=source_bundle,
            stage_counts=stage_counts,
            expected_manifest_core_hash=safe_expected_anchor,
            errors=(REASON_POST_COLLECTION_SNAPSHOT_PROVIDER_INVALID,),
        )

    source_bundle_id = source_bundle.source_bundle_id
    source_package_ref = source_bundle.source_package_ref
    accepted_audit = source_bundle.accepted_audit
    ledger_item = source_bundle.ledger_item
    expected_identity = source_bundle.expected_identity
    before_audit_snapshot = tuple(
        (ref, exact_bytes)
        for ref, exact_bytes in source_bundle.ordered_source_files_before_audit
    )
    after_audit_snapshot = tuple(
        (ref, exact_bytes)
        for ref, exact_bytes in source_bundle.ordered_source_files_after_audit
    )
    stage_counts["manifest_core_collection_count"] = 1
    try:
        manifest_core = _collect_manifest_core_v01(
            ledger_item,
            ordered_source_files=before_audit_snapshot,
            source_package_ref=source_package_ref,
            source_audit_status=accepted_audit.final_status,
            secret_scan_passed=accepted_audit.secret_scan_passed,
            expected_identity=expected_identity,
        )
        manifest_validation = (
            seal_contracts
            .validate_airline_crypto_artifact_seal_manifest_core_v01(
                manifest_core,
            )
        )
        if (
            type(manifest_core)
            is not seal_contracts.AirlineCryptoArtifactSealManifestCoreV01
            or manifest_validation.validation_status != STATUS_PASS
            or manifest_core.transaction_id != ledger_item.transaction_id
            or manifest_core.ledger_id != ledger_item.ledger_id
            or manifest_core.source_package_ref != source_package_ref
        ):
            raise ValueError(REASON_MANIFEST_CORE_COLLECTION_FAILED)
    except Exception:
        return _collection_result(
            source_report=source_report,
            source_bundle=source_bundle,
            stage_counts=stage_counts,
            expected_manifest_core_hash=safe_expected_anchor,
            errors=(REASON_MANIFEST_CORE_COLLECTION_FAILED,),
        )

    stage_counts["envelope_collection_count"] = 1
    try:
        envelope = _collect_envelope_v01(manifest_core)
        envelope_validation = (
            seal_contracts
            .validate_airline_crypto_artifact_seal_envelope_contract_v01(
                envelope,
            )
        )
        if (
            type(envelope)
            is not seal_contracts.AirlineCryptoArtifactSealEnvelopeV01
            or envelope_validation.validation_status != STATUS_PASS
        ):
            raise ValueError(REASON_ENVELOPE_COLLECTION_FAILED)
    except Exception:
        return _collection_result(
            source_report=source_report,
            source_bundle=source_bundle,
            manifest_core=manifest_core,
            stage_counts=stage_counts,
            expected_manifest_core_hash=safe_expected_anchor,
            errors=(REASON_ENVELOPE_COLLECTION_FAILED,),
        )
    if (
        envelope.manifest_core != manifest_core
        or envelope.manifest_core_hash
        != seal_contracts.hash_airline_crypto_artifact_seal_manifest_core_v01(
            manifest_core,
        )
    ):
        return _collection_result(
            source_report=source_report,
            source_bundle=source_bundle,
            manifest_core=manifest_core,
            stage_counts=stage_counts,
            expected_manifest_core_hash=safe_expected_anchor,
            errors=(REASON_COLLECTION_MANIFEST_ENVELOPE_MISMATCH,),
        )

    stage_counts["post_collection_snapshot_provider_call_count"] = 1
    try:
        observed_snapshot = post_collection_snapshot_provider()
    except Exception:
        return _collection_result(
            source_report=source_report,
            source_bundle=source_bundle,
            manifest_core=manifest_core,
            envelope=envelope,
            stage_counts=stage_counts,
            expected_manifest_core_hash=safe_expected_anchor,
            errors=(REASON_POST_COLLECTION_SNAPSHOT_PROVIDER_FAILED,),
        )

    snapshot_shape_valid, snapshot_order_valid = _validate_snapshot_shape(
        observed_snapshot,
    )
    snapshot_valid = snapshot_shape_valid and snapshot_order_valid
    if snapshot_valid:
        post_collection_snapshot: object = tuple(
            (ref, exact_bytes) for ref, exact_bytes in observed_snapshot
        )
    else:
        post_collection_snapshot = observed_snapshot
    source_bytes_unchanged_after_collection = bool(
        snapshot_valid
        and post_collection_snapshot == before_audit_snapshot
        and post_collection_snapshot == after_audit_snapshot
    )

    stage_counts["verification_count"] = 1
    try:
        verification_report = _verify_collected_envelope_v01(
            envelope,
            ledger_item=ledger_item,
            ordered_source_files_before=before_audit_snapshot,
            ordered_source_files_after=post_collection_snapshot,
            expected_source_package_ref=source_package_ref,
            source_audit_status=accepted_audit.final_status,
            secret_scan_passed=accepted_audit.secret_scan_passed,
            expected_manifest_core_hash=expected_manifest_core_hash,
            expected_identity=expected_identity,
        )
    except Exception:
        return _collection_result(
            source_report=source_report,
            source_bundle=source_bundle,
            manifest_core=manifest_core,
            envelope=envelope,
            stage_counts=stage_counts,
            expected_manifest_core_hash=safe_expected_anchor,
            source_bytes_unchanged_after_collection=(
                source_bytes_unchanged_after_collection
            ),
            errors=(REASON_VERIFICATION_CALL_FAILED,),
        )

    collection_errors: list[str] = []
    if not snapshot_valid:
        _append(collection_errors, REASON_POST_COLLECTION_SNAPSHOT_MALFORMED)
    elif not source_bytes_unchanged_after_collection:
        _append(collection_errors, REASON_POST_COLLECTION_SOURCE_BYTES_CHANGED)
    accepted_verification_report, verification_reasons = (
        _accepted_nested_verification_report_v01(
            verification_report,
            manifest_core=manifest_core,
            envelope=envelope,
            safe_expected_anchor=safe_expected_anchor,
            expected_anchor_input_malformed=expected_anchor_input_malformed,
            source_bytes_unchanged_after_collection=(
                source_bytes_unchanged_after_collection
            ),
        )
    )
    for reason in verification_reasons:
        _append(collection_errors, reason)
    if (
        accepted_verification_report is not None
        and accepted_verification_report.verification_status == STATUS_FAIL_CLOSED
    ):
        _append(collection_errors, REASON_COLLECTION_VERIFICATION_FAILED)
    if (
        safe_expected_anchor is not None
        and safe_expected_anchor != envelope.manifest_core_hash
    ):
        _append(collection_errors, REASON_COLLECTION_EXPECTED_ANCHOR_MISMATCH)
    return _collection_result(
        source_report=source_report,
        source_bundle=source_bundle,
        manifest_core=manifest_core,
        envelope=envelope,
        verification_report=accepted_verification_report,
        stage_counts=stage_counts,
        expected_manifest_core_hash=safe_expected_anchor,
        source_bytes_unchanged_after_collection=(
            source_bytes_unchanged_after_collection
        ),
        errors=tuple(collection_errors),
    )


def _collect_manifest_core_v01(
    ledger_item: ledger_contracts.AirlineTransactionArtifactLedgerV01,
    *,
    ordered_source_files: tuple[tuple[str, bytes], ...],
    source_package_ref: str,
    source_audit_status: str,
    secret_scan_passed: bool,
    expected_identity: ledger_contracts.AirlineTransactionArtifactLedgerExpectedIdentityV01,
) -> seal_contracts.AirlineCryptoArtifactSealManifestCoreV01:
    return seal_contracts.build_airline_crypto_artifact_seal_manifest_core_v01(
        ledger_item,
        ordered_source_files=ordered_source_files,
        source_package_ref=source_package_ref,
        source_audit_status=source_audit_status,
        secret_scan_passed=secret_scan_passed,
        expected_identity=expected_identity,
    )


def _collect_envelope_v01(
    manifest_core: seal_contracts.AirlineCryptoArtifactSealManifestCoreV01,
) -> seal_contracts.AirlineCryptoArtifactSealEnvelopeV01:
    return seal_contracts.build_airline_crypto_artifact_seal_envelope_v01(
        manifest_core,
    )


def _verify_collected_envelope_v01(
    envelope: seal_contracts.AirlineCryptoArtifactSealEnvelopeV01,
    *,
    ledger_item: ledger_contracts.AirlineTransactionArtifactLedgerV01,
    ordered_source_files_before: object,
    ordered_source_files_after: object,
    expected_source_package_ref: object,
    source_audit_status: object,
    secret_scan_passed: object,
    expected_manifest_core_hash: object | None,
    expected_identity: object,
) -> seal_contracts.AirlineCryptoArtifactSealVerificationReportV01:
    return seal_contracts.verify_airline_crypto_artifact_seal_v01(
        envelope,
        ledger_item=ledger_item,
        ordered_source_files_before=ordered_source_files_before,
        ordered_source_files_after=ordered_source_files_after,
        expected_source_package_ref=expected_source_package_ref,
        source_audit_status=source_audit_status,
        secret_scan_passed=secret_scan_passed,
        expected_manifest_core_hash=expected_manifest_core_hash,
        expected_identity=expected_identity,
    )


def _accepted_nested_verification_report_v01(
    verification_report: object,
    *,
    manifest_core: seal_contracts.AirlineCryptoArtifactSealManifestCoreV01,
    envelope: seal_contracts.AirlineCryptoArtifactSealEnvelopeV01,
    safe_expected_anchor: str | None,
    expected_anchor_input_malformed: bool,
    source_bytes_unchanged_after_collection: bool,
) -> tuple[
    seal_contracts.AirlineCryptoArtifactSealVerificationReportV01 | None,
    tuple[str, ...],
]:
    errors: list[str] = []
    if (
        type(verification_report)
        is not seal_contracts.AirlineCryptoArtifactSealVerificationReportV01
    ):
        return (
            None,
            (
                REASON_VERIFICATION_REPORT_CONTRACT_INVALID,
                REASON_VERIFICATION_REPORT_MISSING,
            ),
        )
    try:
        validation = (
            seal_contracts
            .validate_airline_crypto_artifact_seal_verification_report_v01(
                verification_report,
            )
        )
    except Exception:
        validation = None
    if validation is None or validation.validation_status != STATUS_PASS:
        return (
            None,
            (
                REASON_VERIFICATION_REPORT_CONTRACT_INVALID,
                REASON_VERIFICATION_REPORT_MISSING,
            ),
        )
    if (
        verification_report.transaction_id != manifest_core.transaction_id
        or verification_report.ledger_id != manifest_core.ledger_id
        or verification_report.manifest_core_hash != envelope.manifest_core_hash
    ):
        _append(errors, REASON_COLLECTION_IDENTITY_MISMATCH)
    if verification_report.expected_manifest_core_hash != safe_expected_anchor:
        _append(errors, REASON_COLLECTION_EXPECTED_ANCHOR_MISMATCH)
    if (
        verification_report.source_bytes_unchanged
        is not source_bytes_unchanged_after_collection
    ):
        _append(errors, REASON_COLLECTION_RESULT_FIELD_MISMATCH)
    if expected_anchor_input_malformed:
        if (
            verification_report.verification_status != STATUS_FAIL_CLOSED
            or verification_report.expected_manifest_core_hash is not None
            or verification_report.external_anchor_supplied is not False
            or verification_report.external_anchor_verified is not False
            or seal_contracts.REASON_VERIFICATION_EXPECTED_ANCHOR_MALFORMED
            not in verification_report.verification_errors
        ):
            _append(errors, REASON_COLLECTION_EXPECTED_ANCHOR_MISMATCH)
    elif safe_expected_anchor is None:
        if (
            verification_report.external_anchor_supplied is not False
            or verification_report.external_anchor_verified is not False
            or verification_report.verification_status == STATUS_PASS
        ):
            _append(errors, REASON_COLLECTION_EXPECTED_ANCHOR_MISMATCH)
    elif (
        verification_report.external_anchor_supplied is not True
        or verification_report.verification_status
        == STATUS_SELF_CONSISTENT_UNANCHORED
        or (
            verification_report.verification_status == STATUS_PASS
            and (
                safe_expected_anchor != envelope.manifest_core_hash
                or verification_report.external_anchor_verified is not True
            )
        )
    ):
        _append(errors, REASON_COLLECTION_EXPECTED_ANCHOR_MISMATCH)
    if errors:
        _append(errors, REASON_VERIFICATION_REPORT_MISSING)
        return None, tuple(errors)
    return verification_report, ()


def _collection_result(
    *,
    source_report: AirlineCryptoArtifactSealSourceBundleValidationReportV01,
    stage_counts: Mapping[str, int],
    source_bundle: AirlineCryptoArtifactSealSourceBundleV01 | None = None,
    manifest_core: (
        seal_contracts.AirlineCryptoArtifactSealManifestCoreV01 | None
    ) = None,
    envelope: seal_contracts.AirlineCryptoArtifactSealEnvelopeV01 | None = None,
    verification_report: (
        seal_contracts.AirlineCryptoArtifactSealVerificationReportV01 | None
    ) = None,
    expected_manifest_core_hash: str | None = None,
    source_bytes_unchanged_after_collection: bool | None = None,
    errors: object = (),
) -> AirlineCryptoArtifactSealCollectionResultV01:
    transaction_id = manifest_core.transaction_id if manifest_core is not None else ""
    ledger_id = manifest_core.ledger_id if manifest_core is not None else ""
    manifest_core_hash = ""
    if manifest_core is not None:
        try:
            manifest_core_hash = (
                seal_contracts
                .hash_airline_crypto_artifact_seal_manifest_core_v01(
                    manifest_core,
                )
            )
        except (TypeError, AttributeError, ValueError, KeyError, IndexError, RecursionError):
            manifest_core_hash = ""
    if envelope is not None and type(envelope.manifest_core_hash) is str:
        manifest_core_hash = envelope.manifest_core_hash
    source_after_audit = (
        source_report.source_bytes_unchanged_after_audit
        if type(source_report.source_bytes_unchanged_after_audit) is bool
        else False
    )
    source_after_collection = False
    if type(source_bytes_unchanged_after_collection) is bool:
        source_after_collection = source_bytes_unchanged_after_collection
    elif (
        type(verification_report)
        is seal_contracts.AirlineCryptoArtifactSealVerificationReportV01
        and type(verification_report.source_bytes_unchanged) is bool
    ):
        source_after_collection = verification_report.source_bytes_unchanged
    return AirlineCryptoArtifactSealCollectionResultV01(
        collection_status=STATUS_FAIL_CLOSED,
        source_bundle_id=source_report.source_bundle_id,
        source_package_ref=source_report.source_package_ref,
        transaction_id=transaction_id,
        ledger_id=ledger_id,
        manifest_core_hash=manifest_core_hash,
        expected_manifest_core_hash=expected_manifest_core_hash,
        source_bundle_validation_report=source_report,
        manifest_core=manifest_core,
        envelope=envelope,
        verification_report=verification_report,
        source_bytes_unchanged_after_audit=source_after_audit,
        source_bytes_unchanged_after_collection=source_after_collection,
        **{
            field_name: stage_counts.get(field_name, 0)
            for field_name in COLLECTION_STAGE_COUNT_FIELDS
        },
        **{field_name: 0 for field_name in COLLECTION_ZERO_COUNTER_FIELDS},
        collection_errors=errors,  # type: ignore[arg-type]
    )


def _derive_collection_status(
    result: AirlineCryptoArtifactSealCollectionResultV01,
    errors: tuple[str, ...],
) -> str:
    if errors or not _collection_internal_success(result):
        return STATUS_FAIL_CLOSED
    assert result.verification_report is not None
    if result.verification_report.verification_status == STATUS_PASS:
        return STATUS_PASS
    if (
        result.verification_report.verification_status
        == STATUS_SELF_CONSISTENT_UNANCHORED
    ):
        return STATUS_SELF_CONSISTENT_UNANCHORED
    return STATUS_FAIL_CLOSED


def _collection_internal_success(
    result: AirlineCryptoArtifactSealCollectionResultV01,
) -> bool:
    try:
        if (
            type(result.manifest_core)
            is not seal_contracts.AirlineCryptoArtifactSealManifestCoreV01
            or type(result.envelope)
            is not seal_contracts.AirlineCryptoArtifactSealEnvelopeV01
            or type(result.verification_report)
            is not seal_contracts.AirlineCryptoArtifactSealVerificationReportV01
        ):
            return False
        if _source_bundle_report_contract_errors(
            result.source_bundle_validation_report,
        ):
            return False
        if result.source_bundle_validation_report.validation_status != STATUS_PASS:
            return False
        if any(
            not _exact_int_equal(getattr(result, field_name), 1)
            for field_name in COLLECTION_STAGE_COUNT_FIELDS
        ):
            return False
        if any(
            not _exact_int_equal(getattr(result, field_name), 0)
            for field_name in COLLECTION_ZERO_COUNTER_FIELDS
        ):
            return False
        if (
            result.source_bytes_unchanged_after_audit is not True
            or result.source_bytes_unchanged_after_collection is not True
        ):
            return False
        if _collection_nested_contract_errors(result):
            return False
        if _collection_duplicate_coherence_errors(result):
            return False
        if result.verification_report is None:
            return False
        if result.verification_report.verification_status == STATUS_PASS:
            return (
                result.expected_manifest_core_hash is not None
                and result.verification_report.external_anchor_supplied is True
                and result.verification_report.external_anchor_verified is True
                and result.expected_manifest_core_hash
                == result.manifest_core_hash
            )
        if (
            result.verification_report.verification_status
            == STATUS_SELF_CONSISTENT_UNANCHORED
        ):
            return (
                result.expected_manifest_core_hash is None
                and result.verification_report.external_anchor_supplied is False
                and result.verification_report.external_anchor_verified is False
            )
    except (TypeError, AttributeError, ValueError, KeyError, IndexError, RecursionError):
        return False
    return False


def _collection_identity_strings_valid(
    result: AirlineCryptoArtifactSealCollectionResultV01,
) -> bool:
    if type(result.source_bundle_id) is not str:
        return False
    if result.source_bundle_id and not _safe_non_empty_string(
        result.source_bundle_id,
    ):
        return False
    if type(result.source_package_ref) is not str:
        return False
    if (
        result.source_package_ref
        and seal_contracts.validate_airline_crypto_source_package_ref_v01(
            result.source_package_ref,
        ).validation_status
        != STATUS_PASS
    ):
        return False
    for value in (
        result.transaction_id,
        result.ledger_id,
        result.manifest_core_hash,
    ):
        if type(value) is not str:
            return False
        if value and not _safe_non_empty_string(value):
            return False
    if result.expected_manifest_core_hash is not None:
        if (
            type(result.expected_manifest_core_hash) is not str
            or seal_contracts.validate_sha256_hex_v01(
                result.expected_manifest_core_hash,
            ).validation_status
            != STATUS_PASS
        ):
            return False
    return True


def _source_bundle_report_contract_errors(
    report: object,
) -> tuple[str, ...]:
    if type(report) is not AirlineCryptoArtifactSealSourceBundleValidationReportV01:
        return (REASON_COLLECTION_SOURCE_BUNDLE_VALIDATION_REPORT_MALFORMED,)
    try:
        if (
            type(report.source_bundle_id) is not str
            or type(report.source_package_ref) is not str
            or (
                report.source_bundle_id
                and not _safe_non_empty_string(report.source_bundle_id)
            )
            or (
                report.source_package_ref
                and seal_contracts.validate_airline_crypto_source_package_ref_v01(
                    report.source_package_ref,
                ).validation_status
                != STATUS_PASS
            )
            or type(report.validation_errors) is not tuple
            or report.validation_errors != _freeze_errors(report.validation_errors)
            or any(
                type(getattr(report, field_name)) is not bool
                for field_name in SOURCE_BUNDLE_REPORT_BOOLEAN_FIELDS
            )
        ):
            return (REASON_COLLECTION_SOURCE_BUNDLE_VALIDATION_REPORT_MALFORMED,)
        identity_valid = _source_bundle_report_identity_valid(
            report.source_bundle_id,
            report.source_package_ref,
        )
        expected_status = (
            STATUS_PASS
            if not report.validation_errors
            and identity_valid
            and all(
                getattr(report, field_name) is True
                for field_name in SOURCE_BUNDLE_REPORT_BOOLEAN_FIELDS
            )
            else STATUS_FAIL_CLOSED
        )
        if report.validation_status != expected_status:
            return (REASON_COLLECTION_SOURCE_BUNDLE_VALIDATION_REPORT_MALFORMED,)
    except (TypeError, AttributeError, ValueError, KeyError, IndexError, RecursionError):
        return (REASON_COLLECTION_SOURCE_BUNDLE_VALIDATION_REPORT_MALFORMED,)
    return ()


def _collection_stage_contract_errors(
    result: AirlineCryptoArtifactSealCollectionResultV01,
) -> tuple[str, ...]:
    errors: list[str] = []
    counts = tuple(getattr(result, field_name) for field_name in COLLECTION_STAGE_COUNT_FIELDS)
    if (
        any(type(count) is not int or count not in (0, 1) for count in counts)
        or counts[0] != 1
        or not all(later <= earlier for earlier, later in zip(counts, counts[1:]))
    ):
        _append(errors, REASON_COLLECTION_RESULT_STAGE_COUNT_MISMATCH)
        return tuple(errors)
    source_count, manifest_count, envelope_count, callback_count, verify_count = counts
    del source_count
    source_passed = (
        type(result.source_bundle_validation_report)
        is AirlineCryptoArtifactSealSourceBundleValidationReportV01
        and result.source_bundle_validation_report.validation_status == STATUS_PASS
    )
    if not source_passed and counts[1:] != (0, 0, 0, 0):
        _append(errors, REASON_COLLECTION_RESULT_STAGE_COUNT_MISMATCH)
    if (
        source_passed
        and manifest_count == 0
        and REASON_POST_COLLECTION_SNAPSHOT_PROVIDER_INVALID
        not in result.collection_errors
    ):
        _append(errors, REASON_COLLECTION_RESULT_STAGE_COUNT_MISMATCH)
    if result.manifest_core is not None and manifest_count != 1:
        _append(errors, REASON_COLLECTION_RESULT_STAGE_COUNT_MISMATCH)
    if result.envelope is not None and envelope_count != 1:
        _append(errors, REASON_COLLECTION_RESULT_STAGE_COUNT_MISMATCH)
    if result.verification_report is not None and verify_count != 1:
        _append(errors, REASON_COLLECTION_RESULT_STAGE_COUNT_MISMATCH)
    if (
        manifest_count == 1
        and result.manifest_core is None
        and REASON_MANIFEST_CORE_COLLECTION_FAILED not in result.collection_errors
    ):
        _append(errors, REASON_COLLECTION_RESULT_STAGE_COUNT_MISMATCH)
    if (
        envelope_count == 1
        and result.envelope is None
        and REASON_ENVELOPE_COLLECTION_FAILED not in result.collection_errors
        and REASON_COLLECTION_MANIFEST_ENVELOPE_MISMATCH
        not in result.collection_errors
    ):
        _append(errors, REASON_COLLECTION_RESULT_STAGE_COUNT_MISMATCH)
    if (
        result.manifest_core is not None
        and envelope_count == 0
    ):
        _append(errors, REASON_COLLECTION_RESULT_STAGE_COUNT_MISMATCH)
    if result.envelope is not None and callback_count == 0:
        _append(errors, REASON_COLLECTION_RESULT_STAGE_COUNT_MISMATCH)
    if (
        callback_count == 1
        and verify_count == 0
        and REASON_POST_COLLECTION_SNAPSHOT_PROVIDER_FAILED
        not in result.collection_errors
    ):
        _append(errors, REASON_COLLECTION_RESULT_STAGE_COUNT_MISMATCH)
    if (
        verify_count == 1
        and result.verification_report is None
        and REASON_VERIFICATION_CALL_FAILED not in result.collection_errors
        and REASON_VERIFICATION_REPORT_MISSING not in result.collection_errors
    ):
        _append(errors, REASON_COLLECTION_RESULT_STAGE_COUNT_MISMATCH)
    if (
        result.verification_report is not None
        and result.verification_report.verification_status
        in (STATUS_PASS, STATUS_SELF_CONSISTENT_UNANCHORED)
        and result.collection_errors
    ):
        _append(errors, REASON_COLLECTION_RESULT_FIELD_MISMATCH)
    return tuple(errors)


def _collection_nested_contract_errors(
    result: AirlineCryptoArtifactSealCollectionResultV01,
) -> tuple[str, ...]:
    errors: list[str] = []
    if result.manifest_core is not None:
        report = seal_contracts.validate_airline_crypto_artifact_seal_manifest_core_v01(
            result.manifest_core,
        )
        if report.validation_status != STATUS_PASS:
            _append(errors, REASON_MANIFEST_CORE_COLLECTION_FAILED)
    if result.envelope is not None:
        report = seal_contracts.validate_airline_crypto_artifact_seal_envelope_contract_v01(
            result.envelope,
        )
        if report.validation_status != STATUS_PASS:
            _append(errors, REASON_ENVELOPE_COLLECTION_FAILED)
    if result.verification_report is not None:
        report = seal_contracts.validate_airline_crypto_artifact_seal_verification_report_v01(
            result.verification_report,
        )
        if report.validation_status != STATUS_PASS:
            _append(errors, REASON_VERIFICATION_REPORT_CONTRACT_INVALID)
    return tuple(errors)


def _collection_duplicate_coherence_errors(
    result: AirlineCryptoArtifactSealCollectionResultV01,
) -> tuple[str, ...]:
    errors: list[str] = []
    source_report = result.source_bundle_validation_report
    if (
        type(source_report)
        is AirlineCryptoArtifactSealSourceBundleValidationReportV01
        and (
            result.source_bundle_id != source_report.source_bundle_id
            or result.source_package_ref != source_report.source_package_ref
        )
    ):
        _append(errors, REASON_COLLECTION_IDENTITY_MISMATCH)
    if result.manifest_core is None:
        if result.transaction_id or result.ledger_id or result.manifest_core_hash:
            _append(errors, REASON_COLLECTION_IDENTITY_MISMATCH)
    else:
        expected_hash = (
            seal_contracts.hash_airline_crypto_artifact_seal_manifest_core_v01(
                result.manifest_core,
            )
        )
        if (
            result.transaction_id != result.manifest_core.transaction_id
            or result.ledger_id != result.manifest_core.ledger_id
            or result.manifest_core_hash != expected_hash
            or result.source_package_ref
            != result.manifest_core.source_package_ref
        ):
            _append(errors, REASON_COLLECTION_IDENTITY_MISMATCH)
    if result.envelope is not None:
        if (
            result.manifest_core is None
            or result.envelope.manifest_core != result.manifest_core
            or result.envelope.manifest_core_hash != result.manifest_core_hash
        ):
            _append(errors, REASON_COLLECTION_MANIFEST_ENVELOPE_MISMATCH)
    if result.verification_report is not None:
        verification = result.verification_report
        if (
            result.transaction_id != verification.transaction_id
            or result.ledger_id != verification.ledger_id
            or result.manifest_core_hash != verification.manifest_core_hash
        ):
            _append(errors, REASON_COLLECTION_IDENTITY_MISMATCH)
        if result.expected_manifest_core_hash != verification.expected_manifest_core_hash:
            _append(errors, REASON_COLLECTION_EXPECTED_ANCHOR_MISMATCH)
        if (
            result.source_bytes_unchanged_after_collection
            is not verification.source_bytes_unchanged
        ):
            _append(errors, REASON_COLLECTION_RESULT_FIELD_MISMATCH)
    if (
        type(source_report)
        is AirlineCryptoArtifactSealSourceBundleValidationReportV01
        and result.source_bytes_unchanged_after_audit
        is not source_report.source_bytes_unchanged_after_audit
    ):
        _append(errors, REASON_COLLECTION_RESULT_FIELD_MISMATCH)
    return tuple(errors)


def _collection_result_plain_dict_unchecked(
    result: AirlineCryptoArtifactSealCollectionResultV01,
) -> dict[str, object]:
    source_report = result.source_bundle_validation_report
    source_report_plain = {
        field_name: (
            list(source_report.validation_errors)
            if field_name == "validation_errors"
            else getattr(source_report, field_name)
        )
        for field_name in SOURCE_BUNDLE_VALIDATION_REPORT_FIELD_NAMES
    }
    manifest_plain = (
        seal_contracts.airline_crypto_artifact_seal_manifest_core_to_plain_dict_v01(
            result.manifest_core,
        )
        if result.manifest_core is not None
        else None
    )
    envelope_plain = None
    if result.envelope is not None:
        signature = result.envelope.signature
        envelope_plain = {
            "manifest_core": manifest_plain,
            "manifest_core_hash": result.envelope.manifest_core_hash,
            "signature": {
                "mode": signature.mode,
                "algorithm": signature.algorithm,
                "key_id": signature.key_id,
                "value": signature.value,
                "verified": signature.verified,
            },
        }
    verification_plain = (
        seal_contracts
        .airline_crypto_artifact_seal_verification_report_to_plain_dict_v01(
            result.verification_report,
        )
        if result.verification_report is not None
        else None
    )
    return {
        "collection_status": result.collection_status,
        "source_bundle_id": result.source_bundle_id,
        "source_package_ref": result.source_package_ref,
        "transaction_id": result.transaction_id,
        "ledger_id": result.ledger_id,
        "manifest_core_hash": result.manifest_core_hash,
        "expected_manifest_core_hash": result.expected_manifest_core_hash,
        "source_bundle_validation_report": source_report_plain,
        "manifest_core": manifest_plain,
        "envelope": envelope_plain,
        "verification_report": verification_plain,
        "source_bytes_unchanged_after_audit": (
            result.source_bytes_unchanged_after_audit
        ),
        "source_bytes_unchanged_after_collection": (
            result.source_bytes_unchanged_after_collection
        ),
        **{
            field_name: getattr(result, field_name)
            for field_name in COLLECTION_STAGE_COUNT_FIELDS
        },
        **{
            field_name: getattr(result, field_name)
            for field_name in COLLECTION_ZERO_COUNTER_FIELDS
        },
        "collection_errors": list(result.collection_errors),
    }


def _safe_expected_anchor_for_result(value: object | None) -> str | None:
    if (
        type(value) is str
        and seal_contracts.validate_sha256_hex_v01(value).validation_status
        == STATUS_PASS
    ):
        return value
    return None


def _source_bundle_report_identity_valid(
    source_bundle_id: object,
    source_package_ref: object,
) -> bool:
    return bool(
        _safe_non_empty_string(source_bundle_id)
        and seal_contracts.validate_airline_crypto_source_package_ref_v01(
            source_package_ref,
        ).validation_status
        == STATUS_PASS
    )


def _safe_source_bundle_identity(
    source_bundle: object,
) -> tuple[str, str]:
    if type(source_bundle) is not AirlineCryptoArtifactSealSourceBundleV01:
        return "", ""
    source_bundle_id = (
        source_bundle.source_bundle_id
        if _safe_non_empty_string(source_bundle.source_bundle_id)
        else ""
    )
    source_package_ref = (
        source_bundle.source_package_ref
        if seal_contracts.validate_airline_crypto_source_package_ref_v01(
            source_bundle.source_package_ref,
        ).validation_status
        == STATUS_PASS
        else ""
    )
    return source_bundle_id, source_package_ref


def _freeze_collection_errors(value: object) -> tuple[str, ...]:
    if type(value) not in (tuple, list):
        return (REASON_COLLECTION_ERROR_CONTAINER_MALFORMED,)
    output: list[str] = []
    for reason in value:
        actual_reason = (
            reason
            if type(reason) is str
            and reason in COLLECTION_REASONS
            and seal_contracts.validate_airline_crypto_canonical_json_value_v01(
                reason,
            ).validation_status
            == STATUS_PASS
            else REASON_COLLECTION_ERROR_CONTAINER_MALFORMED
        )
        if actual_reason not in output:
            output.append(actual_reason)
    return tuple(output)


def _source_bundle_report(
    *,
    source_bundle_id: str = "",
    source_package_ref: str = "",
    flags: Mapping[str, bool] | None = None,
    errors: object = (),
) -> AirlineCryptoArtifactSealSourceBundleValidationReportV01:
    actual_flags = flags or {}
    return AirlineCryptoArtifactSealSourceBundleValidationReportV01(
        validation_status=STATUS_PASS,
        source_bundle_id=source_bundle_id,
        source_package_ref=source_package_ref,
        **{
            field_name: actual_flags.get(field_name, False)
            for field_name in SOURCE_BUNDLE_REPORT_BOOLEAN_FIELDS
        },
        validation_errors=errors,  # type: ignore[arg-type]
    )


def _validate_accepted_ledger(
    ledger_item: object,
    *,
    expected_identity: object,
) -> tuple[bool, tuple[int, int, int] | None]:
    if (
        type(ledger_item) is not ledger_contracts.AirlineTransactionArtifactLedgerV01
        or type(expected_identity)
        is not ledger_contracts.AirlineTransactionArtifactLedgerExpectedIdentityV01
    ):
        return False, None
    try:
        report = ledger_contracts.validate_airline_transaction_artifact_ledger_v01(
            ledger_item,
            expected_identity=expected_identity,
        )
        if (
            report.validation_status != ledger_contracts.STATUS_PASS
            or type(ledger_item.validation_status) is not str
            or ledger_item.validation_status != ledger_contracts.STATUS_PASS
            or type(ledger_item.validation_errors) is not tuple
            or ledger_item.validation_errors != ()
            or type(ledger_item.entries) is not tuple
            or len(ledger_item.entries) != 19
            or not all(
                type(entry) is ledger_contracts.AirlineTransactionArtifactLedgerEntryV01
                for entry in ledger_item.entries
            )
        ):
            return False, None
        actual_edges = sum(len(entry.depends_on) for entry in ledger_item.entries)
        root_types = tuple(
            entry.artifact_type
            for entry in ledger_item.entries
            if entry.artifact_type
            in (
                ledger_contracts.ARTIFACT_CLIENT_ROOT_FINAL,
                ledger_contracts.ARTIFACT_AIRLINE_ROOT_FINAL,
                ledger_contracts.ARTIFACT_BANK_ROOT_FINAL,
            )
        )
        geometry = (len(ledger_item.entries), actual_edges, len(root_types))
        if (
            geometry != (19, 29, 3)
            or ledger_item.entry_count != 19
            or ledger_item.dependency_edge_count != 29
            or ledger_item.root_final_count != 3
            or tuple(entry.artifact_type for entry in ledger_item.entries)
            != ledger_contracts.EXPECTED_ARTIFACT_TYPE_SEQUENCE
            or root_types.count(ledger_contracts.ARTIFACT_CLIENT_ROOT_FINAL) != 1
            or root_types.count(ledger_contracts.ARTIFACT_AIRLINE_ROOT_FINAL) != 1
            or root_types.count(ledger_contracts.ARTIFACT_BANK_ROOT_FINAL) != 1
        ):
            return False, None
        return True, geometry
    except (TypeError, AttributeError, ValueError, KeyError, IndexError, RecursionError):
        return False, None


def _project_ledger_value(value: object, active_ids: set[int]) -> object:
    if value is None or type(value) in (bool, int, str):
        return value
    if type(value) in (ledger_contracts.AirlineTransactionArtifactLedgerV01,
                       ledger_contracts.AirlineTransactionArtifactLedgerEntryV01):
        value_id = id(value)
        if value_id in active_ids:
            raise ValueError(REASON_LEDGER_DOCUMENT_PROJECTION_FAILED)
        active_ids.add(value_id)
        output = {
            field.name: _project_ledger_value(getattr(value, field.name), active_ids)
            for field in fields(value)
        }
        active_ids.remove(value_id)
        return output
    if type(value) in (
        dict,
        MappingProxyType,
        ledger_contracts._FrozenDict,
    ):
        value_id = id(value)
        if value_id in active_ids:
            raise ValueError(REASON_LEDGER_DOCUMENT_PROJECTION_FAILED)
        active_ids.add(value_id)
        output_dict: dict[str, object] = {}
        for key, item in value.items():
            if type(key) is not str:
                raise ValueError(REASON_LEDGER_DOCUMENT_PROJECTION_FAILED)
            output_dict[key] = _project_ledger_value(item, active_ids)
        active_ids.remove(value_id)
        return output_dict
    if type(value) is tuple:
        value_id = id(value)
        if value_id in active_ids:
            raise ValueError(REASON_LEDGER_DOCUMENT_PROJECTION_FAILED)
        active_ids.add(value_id)
        output_list = [_project_ledger_value(item, active_ids) for item in value]
        active_ids.remove(value_id)
        return output_list
    if is_dataclass(value) or isinstance(value, MappingABC):
        raise ValueError(REASON_LEDGER_DOCUMENT_PROJECTION_FAILED)
    raise ValueError(REASON_LEDGER_DOCUMENT_PROJECTION_FAILED)


def _ledger_document_matches(
    ledger_item: ledger_contracts.AirlineTransactionArtifactLedgerV01,
    expected_identity: ledger_contracts.AirlineTransactionArtifactLedgerExpectedIdentityV01,
    snapshot: tuple[tuple[str, bytes], ...],
    errors: list[str],
) -> bool:
    ledger_rows = tuple(
        row for row in snapshot if row[0] == REQUIRED_SOURCE_FILE_REFS[0]
    )
    if len(ledger_rows) != 1:
        _append(errors, REASON_LEDGER_DOCUMENT_MISSING)
        return False
    try:
        parsed = seal_contracts.parse_airline_crypto_json_object_bytes_v01(
            ledger_rows[0][1],
        )
    except ValueError:
        _append(errors, REASON_LEDGER_DOCUMENT_MALFORMED_JSON)
        return False
    try:
        projected = airline_crypto_artifact_seal_ledger_document_to_plain_dict_v01(
            ledger_item,
            expected_identity=expected_identity,
        )
    except ValueError:
        _append(errors, REASON_LEDGER_DOCUMENT_PROJECTION_FAILED)
        return False
    if not _exact_json_equal(parsed, projected):
        _append(errors, REASON_LEDGER_DOCUMENT_OBJECT_MISMATCH)
        return False
    return True


def _validate_snapshot_shape(snapshot: object) -> tuple[bool, bool]:
    if type(snapshot) is not tuple or len(snapshot) != len(REQUIRED_SOURCE_FILE_REFS):
        return False, False
    refs: list[str] = []
    for row in snapshot:
        if type(row) is not tuple or len(row) != 2:
            return False, False
        ref, content = row
        if type(ref) is not str or type(content) is not bytes:
            return False, False
        refs.append(ref)
    return True, tuple(refs) == REQUIRED_SOURCE_FILE_REFS


def _freeze_valid_snapshot(value: object) -> tuple[tuple[str, bytes], ...] | None:
    valid, _ = _validate_snapshot_shape(value)
    if not valid:
        return None
    assert type(value) is tuple
    return tuple((row[0], row[1]) for row in value)


def _source_refs_match(
    audit: AirlineCryptoArtifactSealAcceptedLedgerAuditV01,
    ledger_item: ledger_contracts.AirlineTransactionArtifactLedgerV01,
    expected_identity: ledger_contracts.AirlineTransactionArtifactLedgerExpectedIdentityV01,
) -> bool:
    expected_refs = expected_identity.expected_source_refs
    if type(expected_refs) is not ledger_contracts.AirlineTransactionArtifactLedgerExpectedSourceRefsV01:
        return False
    return (
        audit.source_run_ref
        == ledger_item.source_run_ref
        == expected_refs.source_run_ref
        and audit.source_causal_report_ref
        == ledger_item.source_causal_report_ref
        == expected_refs.source_causal_report_ref
        and audit.source_corridor_report_ref
        == ledger_item.source_corridor_report_ref
        == expected_refs.source_corridor_report_ref
    )


def _selected_offer_matches(
    ledger_item: ledger_contracts.AirlineTransactionArtifactLedgerV01,
    audit_offer_id: object,
) -> bool:
    if not _safe_non_empty_string(audit_offer_id):
        return False
    observations: list[object] = []
    for entry in ledger_item.entries:
        _collect_selected_offer_ids(entry.canonical_hash_input, observations, set())
    return bool(observations) and all(
        type(value) is str and value == audit_offer_id for value in observations
    )


def _collect_selected_offer_ids(
    value: object,
    output: list[object],
    active_ids: set[int],
) -> None:
    if type(value) in (
        dict,
        MappingProxyType,
        ledger_contracts._FrozenDict,
    ):
        value_id = id(value)
        if value_id in active_ids:
            raise ValueError(REASON_SOURCE_BUNDLE_SELECTED_OFFER_MISMATCH)
        active_ids.add(value_id)
        for key, item in value.items():
            if key == "selected_offer_id":
                output.append(item)
            _collect_selected_offer_ids(item, output, active_ids)
        active_ids.remove(value_id)
    elif type(value) is tuple:
        value_id = id(value)
        if value_id in active_ids:
            raise ValueError(REASON_SOURCE_BUNDLE_SELECTED_OFFER_MISMATCH)
        active_ids.add(value_id)
        for item in value:
            _collect_selected_offer_ids(item, output, active_ids)
        active_ids.remove(value_id)


def _secret_boundary_valid(
    audit: AirlineCryptoArtifactSealAcceptedLedgerAuditV01,
    ledger_item: ledger_contracts.AirlineTransactionArtifactLedgerV01,
) -> bool:
    return (
        audit.secret_scan_passed is True
        and audit.authority_evidence_boundaries_valid is True
        and audit.canonical_hash_inputs_safe is True
        and all(
            entry.raw_secret_included is False
            and entry.raw_provider_text_included is False
            for entry in ledger_item.entries
        )
    )


def _runtime_boundary_valid(
    audit: AirlineCryptoArtifactSealAcceptedLedgerAuditV01,
    ledger_item: ledger_contracts.AirlineTransactionArtifactLedgerV01,
) -> bool:
    return (
        all(
            _exact_int_equal(getattr(audit, field_name), 0)
            for field_name in ACCEPTED_AUDIT_ZERO_COUNTER_FIELDS
        )
        and all(
            _exact_int_equal(getattr(ledger_item, field_name), 0)
            for field_name in (
                "ledger_created_authority_count",
                "ledger_created_permission_count",
                "ledger_created_action_count",
                "provider_called_count",
                "network_used_count",
                "gemini_called_count",
                "real_world_effects_count",
            )
        )
        and all(
            entry.ledger_created_authority is False
            and entry.ledger_created_permission is False
            and entry.ledger_created_action is False
            and _exact_int_equal(entry.real_world_effects_count, 0)
            for entry in ledger_item.entries
        )
    )


def _exact_json_equal(left: object, right: object) -> bool:
    if type(left) is not type(right):
        return False
    if type(left) is dict:
        if left.keys() != right.keys():
            return False
        return all(_exact_json_equal(left[key], right[key]) for key in left)
    if type(left) is list:
        return len(left) == len(right) and all(
            _exact_json_equal(left_item, right_item)
            for left_item, right_item in zip(left, right)
        )
    return left == right


def _freeze_sequence_or_empty(value: object) -> tuple[str, ...]:
    if type(value) not in (tuple, list):
        return ()
    if any(type(item) is not str for item in value):
        return ()
    return tuple(value)


def _freeze_errors(value: object) -> tuple[str, ...]:
    if type(value) not in (tuple, list):
        return (REASON_MALFORMED_VALIDATION_ERRORS,)
    output: list[str] = []
    for reason in value:
        actual_reason = (
            reason
            if type(reason) is str and reason in VALIDATION_REASONS
            else REASON_MALFORMED_VALIDATION_ERRORS
        )
        if actual_reason not in output:
            output.append(actual_reason)
    return tuple(output)


def _safe_non_empty_string(value: object) -> bool:
    if type(value) is not str or not value:
        return False
    return (
        seal_contracts.validate_airline_crypto_canonical_json_value_v01(
            value,
        ).validation_status
        == STATUS_PASS
    )


def _exact_int_equal(value: object, expected: int) -> bool:
    return type(value) is int and value == expected


def _append(errors: list[str], reason: str) -> None:
    if reason not in errors:
        errors.append(reason)
