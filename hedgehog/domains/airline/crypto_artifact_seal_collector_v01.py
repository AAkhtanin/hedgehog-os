"""Airline Crypto Artifact Seal v0.1 exact-source validation contracts.

Airline Crypto Artifact Seal Collector Slice C1 validates one explicitly
provided immutable source bundle.

It does not discover a package.
It does not read files.
It does not write files.
It does not rerun an audit.
It does not recollect a Ledger.
It does not rerun semantics or the corridor.
It does not create authority, permission, action, payment, ticket, booking,
receipt, or FinalOutput.
"""

from __future__ import annotations

from collections.abc import Mapping as MappingABC
from dataclasses import dataclass, fields, is_dataclass
from types import MappingProxyType
from typing import Mapping

from hedgehog.domains.airline import crypto_artifact_seal_v01 as seal_contracts
from hedgehog.domains.airline import transaction_artifact_ledger_v01 as ledger_contracts


MODULE_ID = "airline_crypto_artifact_seal_collector_v01"
SLICE_ID = "airline_crypto_artifact_seal_v01_slice_c1"

EXPECTED_LEDGER_AUDIT_ID = "airline_transaction_artifact_ledger_audit_v01"
EXPECTED_LEDGER_AUDIT_VERSION = "v0.1"

STATUS_PASS = seal_contracts.STATUS_PASS
STATUS_FAIL_CLOSED = seal_contracts.STATUS_FAIL_CLOSED
REQUIRED_SOURCE_FILE_REFS = seal_contracts.REQUIRED_SOURCE_FILE_REFS

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
        all_flags_true = all(
            type(getattr(self, field_name)) is bool
            and getattr(self, field_name) is True
            for field_name in SOURCE_BUNDLE_REPORT_BOOLEAN_FIELDS
        )
        object.__setattr__(self, "validation_errors", errors)
        object.__setattr__(
            self,
            "validation_status",
            STATUS_PASS if not errors and all_flags_true else STATUS_FAIL_CLOSED,
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

    return _source_bundle_report(
        source_bundle_id=(
            source_bundle.source_bundle_id
            if type(source_bundle.source_bundle_id) is str
            else ""
        ),
        source_package_ref=(
            source_bundle.source_package_ref
            if type(source_bundle.source_package_ref) is str
            else ""
        ),
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
