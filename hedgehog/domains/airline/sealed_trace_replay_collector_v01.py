"""Exact-package in-memory collector for Airline sealed-trace Replay.

This module performs deterministic sealed-trace reconstruction, not transaction
re-execution. It performs no filesystem I/O or package discovery, invokes no
Ledger audit, runs no semantic or Corridor work, and recollects neither Ledger
nor Crypto artifacts. It performs exactly one fresh B2b verification and no
provider/network/Gemini call. It creates no authority, permission, action,
packet, receipt, FinalOutput, or real-world effect. Root Attestation is absent.
This is Airline-domain code, not universal Hedgehog OS core.
"""

from __future__ import annotations

from collections.abc import Mapping
from dataclasses import fields
from typing import Any, Callable

from hedgehog.domains.airline import crypto_artifact_seal_collector_v01 as crypto_collector
from hedgehog.domains.airline import crypto_artifact_seal_v01 as crypto_contracts
from hedgehog.domains.airline import sealed_trace_replay_v01 as replay_contracts
from hedgehog.domains.airline import transaction_artifact_ledger_v01 as ledger_contracts


MODULE_ID = "airline_sealed_trace_replay_collector_v01"
SLICE_ID = "airline_sealed_trace_replay_v01_slice_c1"

STATUS_PASS = replay_contracts.STATUS_PASS
STATUS_FAIL_CLOSED = replay_contracts.STATUS_FAIL_CLOSED

EXPECTED_IDENTITY_ROLE = (
    "verifier_contract_adapter_after_independent_ledger_audit"
)
LEDGER_SOURCE_ARTIFACT_REF = "airline_transaction_artifact_ledger.json"
MANIFEST_DOCUMENT_FIELD_NAMES = (
    "manifest_core",
    "manifest_core_hash",
    "signature",
)

AirlineSealedTraceReplayPostVerificationSnapshotProviderV01 = Callable[[], object]

REASON_PACKAGE_SNAPSHOT_INVALID = (
    "replay_collection_package_snapshot_invalid"
)
REASON_ACCEPTED_LEDGER_AUDIT_INVALID = (
    "replay_collection_accepted_ledger_audit_invalid"
)
REASON_EXPECTED_MANIFEST_CORE_HASH_INVALID = (
    "replay_collection_expected_manifest_core_hash_invalid"
)
REASON_LEDGER_DOCUMENT_MISSING = "replay_collection_ledger_document_missing"
REASON_LEDGER_DOCUMENT_PARSE_FAILED = (
    "replay_collection_ledger_document_parse_failed"
)
REASON_LEDGER_DOCUMENT_FIELD_MISMATCH = (
    "replay_collection_ledger_document_field_mismatch"
)
REASON_LEDGER_DOCUMENT_RECONSTRUCTION_FAILED = (
    "replay_collection_ledger_document_reconstruction_failed"
)
REASON_LEDGER_DOCUMENT_PROJECTION_MISMATCH = (
    "replay_collection_ledger_document_projection_mismatch"
)
REASON_MANIFEST_DOCUMENT_PARSE_FAILED = (
    "replay_collection_manifest_document_parse_failed"
)
REASON_MANIFEST_DOCUMENT_FIELD_MISMATCH = (
    "replay_collection_manifest_document_field_mismatch"
)
REASON_MANIFEST_DOCUMENT_RECONSTRUCTION_FAILED = (
    "replay_collection_manifest_document_reconstruction_failed"
)
REASON_MANIFEST_DOCUMENT_PROJECTION_MISMATCH = (
    "replay_collection_manifest_document_projection_mismatch"
)
REASON_STORED_VERIFICATION_DOCUMENT_PARSE_FAILED = (
    "replay_collection_stored_verification_document_parse_failed"
)
REASON_STORED_VERIFICATION_DOCUMENT_FIELD_MISMATCH = (
    "replay_collection_stored_verification_document_field_mismatch"
)
REASON_STORED_VERIFICATION_RECONSTRUCTION_FAILED = (
    "replay_collection_stored_verification_reconstruction_failed"
)
REASON_STORED_VERIFICATION_PROJECTION_MISMATCH = (
    "replay_collection_stored_verification_projection_mismatch"
)
REASON_EXPECTED_IDENTITY_ADAPTER_FAILED = (
    "replay_collection_expected_identity_adapter_failed"
)
REASON_LEDGER_VALIDATION_FAILED = "replay_collection_ledger_validation_failed"
REASON_AUDIT_LEDGER_IDENTITY_MISMATCH = (
    "replay_collection_audit_ledger_identity_mismatch"
)
REASON_FRESH_ANCHORED_VERIFICATION_FAILED = (
    "replay_collection_fresh_anchored_verification_failed"
)
REASON_REPLAY_INPUT_BUILD_FAILED = (
    "replay_collection_replay_input_build_failed"
)
REASON_TIMELINE_RECONSTRUCTION_FAILED = (
    "replay_collection_timeline_reconstruction_failed"
)
REASON_POST_REPLAY_SNAPSHOT_PROVIDER_INVALID = (
    "replay_collection_post_snapshot_provider_invalid"
)
REASON_POST_REPLAY_SNAPSHOT_PROVIDER_FAILED = (
    "replay_collection_post_snapshot_provider_failed"
)
REASON_POST_REPLAY_SNAPSHOT_WRONG_TYPE = (
    "replay_collection_post_snapshot_wrong_type"
)
REASON_POST_REPLAY_SNAPSHOT_MISMATCH = (
    "replay_collection_post_snapshot_mismatch"
)
REASON_PURE_REPLAY_FAILED = "replay_collection_pure_replay_failed"

REPLAY_COLLECTION_REASON_ALLOWLIST = (
    REASON_PACKAGE_SNAPSHOT_INVALID,
    REASON_ACCEPTED_LEDGER_AUDIT_INVALID,
    REASON_EXPECTED_MANIFEST_CORE_HASH_INVALID,
    REASON_LEDGER_DOCUMENT_MISSING,
    REASON_LEDGER_DOCUMENT_PARSE_FAILED,
    REASON_LEDGER_DOCUMENT_FIELD_MISMATCH,
    REASON_LEDGER_DOCUMENT_RECONSTRUCTION_FAILED,
    REASON_LEDGER_DOCUMENT_PROJECTION_MISMATCH,
    REASON_MANIFEST_DOCUMENT_PARSE_FAILED,
    REASON_MANIFEST_DOCUMENT_FIELD_MISMATCH,
    REASON_MANIFEST_DOCUMENT_RECONSTRUCTION_FAILED,
    REASON_MANIFEST_DOCUMENT_PROJECTION_MISMATCH,
    REASON_STORED_VERIFICATION_DOCUMENT_PARSE_FAILED,
    REASON_STORED_VERIFICATION_DOCUMENT_FIELD_MISMATCH,
    REASON_STORED_VERIFICATION_RECONSTRUCTION_FAILED,
    REASON_STORED_VERIFICATION_PROJECTION_MISMATCH,
    REASON_EXPECTED_IDENTITY_ADAPTER_FAILED,
    REASON_LEDGER_VALIDATION_FAILED,
    REASON_AUDIT_LEDGER_IDENTITY_MISMATCH,
    REASON_FRESH_ANCHORED_VERIFICATION_FAILED,
    REASON_REPLAY_INPUT_BUILD_FAILED,
    REASON_TIMELINE_RECONSTRUCTION_FAILED,
    REASON_POST_REPLAY_SNAPSHOT_PROVIDER_INVALID,
    REASON_POST_REPLAY_SNAPSHOT_PROVIDER_FAILED,
    REASON_POST_REPLAY_SNAPSHOT_WRONG_TYPE,
    REASON_POST_REPLAY_SNAPSHOT_MISMATCH,
    REASON_PURE_REPLAY_FAILED,
)

_SIGNATURE_FIELD_NAMES = (
    "mode",
    "algorithm",
    "key_id",
    "value",
    "verified",
)

_VERIFICATION_TRUE_FIELDS = (
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

_VERIFICATION_ZERO_FIELDS = (
    "provider_call_count",
    "network_call_count",
    "gemini_call_count",
    "seal_created_authority_count",
    "seal_created_permission_count",
    "seal_created_action_count",
    "real_world_effects_count",
)


def _raise(reason: str) -> None:
    actual_reason = (
        reason
        if reason in REPLAY_COLLECTION_REASON_ALLOWLIST
        else REASON_PURE_REPLAY_FAILED
    )
    raise ValueError(actual_reason) from None


def _stable_reason_from_exception(error: Exception, fallback: str) -> str:
    if (
        type(error) is ValueError
        and type(error.args) is tuple
        and len(error.args) == 1
        and type(error.args[0]) is str
        and error.args[0] in REPLAY_COLLECTION_REASON_ALLOWLIST
    ):
        return error.args[0]
    return fallback


def _exact_field_names(value: object, contract_type: type[object]) -> bool:
    return (
        type(value) is dict
        and frozenset(value) == frozenset(field.name for field in fields(contract_type))
    )


def _plain_frozen_ledger_json(value: object, active_ids: set[int]) -> object:
    if value is None or type(value) in (bool, int, str):
        return value
    if type(value) is tuple:
        value_id = id(value)
        if value_id in active_ids:
            _raise(REASON_LEDGER_DOCUMENT_PROJECTION_MISMATCH)
        active_ids.add(value_id)
        output = [_plain_frozen_ledger_json(item, active_ids) for item in value]
        active_ids.remove(value_id)
        return output
    if type(value) is ledger_contracts._FrozenDict:
        value_id = id(value)
        if value_id in active_ids:
            _raise(REASON_LEDGER_DOCUMENT_PROJECTION_MISMATCH)
        active_ids.add(value_id)
        output_dict: dict[str, object] = {}
        for key, item in value.items():
            if type(key) is not str:
                _raise(REASON_LEDGER_DOCUMENT_PROJECTION_MISMATCH)
            output_dict[key] = _plain_frozen_ledger_json(item, active_ids)
        active_ids.remove(value_id)
        return output_dict
    _raise(REASON_LEDGER_DOCUMENT_PROJECTION_MISMATCH)


def _ledger_entry_to_plain_dict(
    entry: ledger_contracts.AirlineTransactionArtifactLedgerEntryV01,
) -> dict[str, object]:
    return {
        "ledger_index": entry.ledger_index,
        "event_type": entry.event_type,
        "artifact_id": entry.artifact_id,
        "artifact_type": entry.artifact_type,
        "transaction_id": entry.transaction_id,
        "root_owner": entry.root_owner,
        "created_by": entry.created_by,
        "authority_class": entry.authority_class,
        "evidence_class": entry.evidence_class,
        "depends_on": list(entry.depends_on),
        "event_time": entry.event_time,
        "recorded_at": entry.recorded_at,
        "source_validation_refs": list(entry.source_validation_refs),
        "auxiliary_artifact_refs": list(entry.auxiliary_artifact_refs),
        "canonical_hash_input": _plain_frozen_ledger_json(
            entry.canonical_hash_input,
            set(),
        ),
        "raw_secret_included": entry.raw_secret_included,
        "raw_provider_text_included": entry.raw_provider_text_included,
        "ledger_created_authority": entry.ledger_created_authority,
        "ledger_created_permission": entry.ledger_created_permission,
        "ledger_created_action": entry.ledger_created_action,
        "real_world_effects_count": entry.real_world_effects_count,
    }


def _ledger_to_plain_dict(
    ledger_item: ledger_contracts.AirlineTransactionArtifactLedgerV01,
) -> dict[str, object]:
    return {
        "ledger_id": ledger_item.ledger_id,
        "ledger_version": ledger_item.ledger_version,
        "transaction_id": ledger_item.transaction_id,
        "source_run_ref": ledger_item.source_run_ref,
        "source_causal_report_ref": ledger_item.source_causal_report_ref,
        "source_corridor_report_ref": ledger_item.source_corridor_report_ref,
        "entries": [
            _ledger_entry_to_plain_dict(entry) for entry in ledger_item.entries
        ],
        "entry_count": ledger_item.entry_count,
        "dependency_edge_count": ledger_item.dependency_edge_count,
        "event_type_counts": _plain_frozen_ledger_json(
            ledger_item.event_type_counts,
            set(),
        ),
        "root_final_count": ledger_item.root_final_count,
        "validation_status": ledger_item.validation_status,
        "validation_errors": list(ledger_item.validation_errors),
        "ledger_created_authority_count": (
            ledger_item.ledger_created_authority_count
        ),
        "ledger_created_permission_count": (
            ledger_item.ledger_created_permission_count
        ),
        "ledger_created_action_count": ledger_item.ledger_created_action_count,
        "provider_called_count": ledger_item.provider_called_count,
        "network_used_count": ledger_item.network_used_count,
        "gemini_called_count": ledger_item.gemini_called_count,
        "real_world_effects_count": ledger_item.real_world_effects_count,
    }


def _reconstruct_ledger_entry(
    raw_entry: object,
) -> ledger_contracts.AirlineTransactionArtifactLedgerEntryV01:
    if not _exact_field_names(
        raw_entry,
        ledger_contracts.AirlineTransactionArtifactLedgerEntryV01,
    ):
        _raise(REASON_LEDGER_DOCUMENT_FIELD_MISMATCH)
    if not (
        type(raw_entry["depends_on"]) is list
        and type(raw_entry["source_validation_refs"]) is list
        and type(raw_entry["auxiliary_artifact_refs"]) is list
        and type(raw_entry["canonical_hash_input"]) is dict
    ):
        _raise(REASON_LEDGER_DOCUMENT_FIELD_MISMATCH)
    try:
        entry = ledger_contracts.AirlineTransactionArtifactLedgerEntryV01(
            ledger_index=raw_entry["ledger_index"],
            event_type=raw_entry["event_type"],
            artifact_id=raw_entry["artifact_id"],
            artifact_type=raw_entry["artifact_type"],
            transaction_id=raw_entry["transaction_id"],
            root_owner=raw_entry["root_owner"],
            created_by=raw_entry["created_by"],
            authority_class=raw_entry["authority_class"],
            evidence_class=raw_entry["evidence_class"],
            depends_on=tuple(raw_entry["depends_on"]),
            event_time=raw_entry["event_time"],
            recorded_at=raw_entry["recorded_at"],
            source_validation_refs=tuple(raw_entry["source_validation_refs"]),
            auxiliary_artifact_refs=tuple(raw_entry["auxiliary_artifact_refs"]),
            canonical_hash_input=raw_entry["canonical_hash_input"],
            raw_secret_included=raw_entry["raw_secret_included"],
            raw_provider_text_included=raw_entry["raw_provider_text_included"],
            ledger_created_authority=raw_entry["ledger_created_authority"],
            ledger_created_permission=raw_entry["ledger_created_permission"],
            ledger_created_action=raw_entry["ledger_created_action"],
            real_world_effects_count=raw_entry["real_world_effects_count"],
        )
    except Exception:
        _raise(REASON_LEDGER_DOCUMENT_RECONSTRUCTION_FAILED)
    if ledger_contracts.validate_airline_transaction_artifact_ledger_entry_v01(
        entry,
    ):
        _raise(REASON_LEDGER_DOCUMENT_RECONSTRUCTION_FAILED)
    return entry


def _reconstruct_ledger(
    snapshot: replay_contracts.AirlineSealedTraceReplayPackageSnapshotV01,
) -> tuple[ledger_contracts.AirlineTransactionArtifactLedgerV01, dict[str, object]]:
    rows = tuple(
        row
        for row in snapshot.ordered_source_files
        if row[0] == LEDGER_SOURCE_ARTIFACT_REF
    )
    if len(rows) != 1:
        _raise(REASON_LEDGER_DOCUMENT_MISSING)
    try:
        parsed = crypto_contracts.parse_airline_crypto_json_object_bytes_v01(
            rows[0][1],
        )
    except Exception:
        _raise(REASON_LEDGER_DOCUMENT_PARSE_FAILED)
    if not _exact_field_names(
        parsed,
        ledger_contracts.AirlineTransactionArtifactLedgerV01,
    ):
        _raise(REASON_LEDGER_DOCUMENT_FIELD_MISMATCH)
    if not (
        type(parsed["entries"]) is list
        and type(parsed["validation_errors"]) is list
        and type(parsed["event_type_counts"]) is dict
    ):
        _raise(REASON_LEDGER_DOCUMENT_FIELD_MISMATCH)
    entries = tuple(_reconstruct_ledger_entry(item) for item in parsed["entries"])
    try:
        ledger_item = ledger_contracts.AirlineTransactionArtifactLedgerV01(
            ledger_id=parsed["ledger_id"],
            ledger_version=parsed["ledger_version"],
            transaction_id=parsed["transaction_id"],
            source_run_ref=parsed["source_run_ref"],
            source_causal_report_ref=parsed["source_causal_report_ref"],
            source_corridor_report_ref=parsed["source_corridor_report_ref"],
            entries=entries,
            entry_count=parsed["entry_count"],
            dependency_edge_count=parsed["dependency_edge_count"],
            event_type_counts=parsed["event_type_counts"],
            root_final_count=parsed["root_final_count"],
            validation_status=parsed["validation_status"],
            validation_errors=tuple(parsed["validation_errors"]),
            ledger_created_authority_count=parsed["ledger_created_authority_count"],
            ledger_created_permission_count=parsed["ledger_created_permission_count"],
            ledger_created_action_count=parsed["ledger_created_action_count"],
            provider_called_count=parsed["provider_called_count"],
            network_used_count=parsed["network_used_count"],
            gemini_called_count=parsed["gemini_called_count"],
            real_world_effects_count=parsed["real_world_effects_count"],
        )
    except Exception:
        _raise(REASON_LEDGER_DOCUMENT_RECONSTRUCTION_FAILED)
    try:
        projected = _ledger_to_plain_dict(ledger_item)
    except Exception:
        _raise(REASON_LEDGER_DOCUMENT_PROJECTION_MISMATCH)
    if projected != parsed:
        _raise(REASON_LEDGER_DOCUMENT_PROJECTION_MISMATCH)
    return ledger_item, parsed


def _reconstruct_envelope(
    snapshot: replay_contracts.AirlineSealedTraceReplayPackageSnapshotV01,
    ledger_item: ledger_contracts.AirlineTransactionArtifactLedgerV01,
) -> tuple[crypto_contracts.AirlineCryptoArtifactSealEnvelopeV01, dict[str, object]]:
    try:
        parsed = crypto_contracts.parse_airline_crypto_json_object_bytes_v01(
            snapshot.manifest_bytes,
        )
    except Exception:
        _raise(REASON_MANIFEST_DOCUMENT_PARSE_FAILED)
    if frozenset(parsed) != frozenset(MANIFEST_DOCUMENT_FIELD_NAMES):
        _raise(REASON_MANIFEST_DOCUMENT_FIELD_MISMATCH)
    core_raw = parsed["manifest_core"]
    signature_raw = parsed["signature"]
    if not (
        type(core_raw) is dict
        and frozenset(core_raw) == frozenset(crypto_contracts.MANIFEST_CORE_FIELD_NAMES)
        and type(signature_raw) is dict
        and frozenset(signature_raw) == frozenset(_SIGNATURE_FIELD_NAMES)
        and type(core_raw["ordered_artifact_refs"]) is list
        and type(core_raw["ordered_artifact_hashes"]) is list
        and type(core_raw["ordered_source_file_refs"]) is list
        and type(core_raw["ordered_source_file_hashes"]) is list
    ):
        _raise(REASON_MANIFEST_DOCUMENT_FIELD_MISMATCH)
    try:
        core = crypto_contracts.AirlineCryptoArtifactSealManifestCoreV01(
            seal_id=core_raw["seal_id"],
            seal_version=core_raw["seal_version"],
            transaction_id=core_raw["transaction_id"],
            ledger_id=core_raw["ledger_id"],
            source_package_ref=core_raw["source_package_ref"],
            canonicalization_profile_id=core_raw["canonicalization_profile_id"],
            hash_algorithm=core_raw["hash_algorithm"],
            hash_encoding=core_raw["hash_encoding"],
            ledger_entry_count=core_raw["ledger_entry_count"],
            dependency_edge_count=core_raw["dependency_edge_count"],
            root_final_count=core_raw["root_final_count"],
            ordered_artifact_refs=tuple(core_raw["ordered_artifact_refs"]),
            ordered_artifact_hashes=tuple(core_raw["ordered_artifact_hashes"]),
            chain_genesis_hash=core_raw["chain_genesis_hash"],
            chain_head_hash=core_raw["chain_head_hash"],
            chain_tail_hash=core_raw["chain_tail_hash"],
            source_file_count=core_raw["source_file_count"],
            ordered_source_file_refs=tuple(core_raw["ordered_source_file_refs"]),
            ordered_source_file_hashes=tuple(core_raw["ordered_source_file_hashes"]),
            source_package_hash=core_raw["source_package_hash"],
            ledger_document_byte_hash=core_raw["ledger_document_byte_hash"],
            previous_manifest_ref=core_raw["previous_manifest_ref"],
            signature_placeholder_present=core_raw["signature_placeholder_present"],
            signature_verified=core_raw["signature_verified"],
            source_audit_status=core_raw["source_audit_status"],
            secret_scan_passed=core_raw["secret_scan_passed"],
            raw_secret_included=core_raw["raw_secret_included"],
            seal_created_authority_count=core_raw["seal_created_authority_count"],
            seal_created_permission_count=core_raw["seal_created_permission_count"],
            seal_created_action_count=core_raw["seal_created_action_count"],
            real_world_effects_count=core_raw["real_world_effects_count"],
        )
        signature = crypto_contracts.AirlineCryptoArtifactSealSignaturePlaceholderV01(
            mode=signature_raw["mode"],
            algorithm=signature_raw["algorithm"],
            key_id=signature_raw["key_id"],
            value=signature_raw["value"],
            verified=signature_raw["verified"],
        )
        envelope = crypto_contracts.AirlineCryptoArtifactSealEnvelopeV01(
            manifest_core=core,
            manifest_core_hash=parsed["manifest_core_hash"],
            signature=signature,
        )
    except Exception:
        _raise(REASON_MANIFEST_DOCUMENT_RECONSTRUCTION_FAILED)
    if not (
        crypto_contracts.validate_airline_crypto_artifact_seal_manifest_core_v01(
            core,
        ).validation_status
        == STATUS_PASS
        and crypto_contracts.validate_airline_crypto_artifact_seal_signature_placeholder_v01(
            signature,
        ).validation_status
        == STATUS_PASS
        and crypto_contracts.validate_airline_crypto_artifact_seal_envelope_contract_v01(
            envelope,
        ).validation_status
        == STATUS_PASS
        and crypto_contracts.hash_airline_crypto_artifact_seal_manifest_core_v01(core)
        == envelope.manifest_core_hash
        and core.source_package_ref == snapshot.source_package_ref
        and core.ordered_source_file_refs
        == tuple(row[0] for row in snapshot.ordered_source_files)
        and core.transaction_id == ledger_item.transaction_id
        and core.ledger_id == ledger_item.ledger_id
        and (core.ledger_entry_count, core.dependency_edge_count, core.root_final_count)
        == (19, 29, 3)
        and len(core.ordered_artifact_refs) == 19
        and len(core.ordered_artifact_hashes) == 19
        and len(core.ordered_source_file_refs) == 9
        and len(core.ordered_source_file_hashes) == 9
        and signature.mode
        == crypto_contracts.SIGNATURE_MODE_UNSIGNED_PLACEHOLDER
        and signature.verified is False
    ):
        _raise(REASON_MANIFEST_DOCUMENT_RECONSTRUCTION_FAILED)
    projected = {
        "manifest_core": (
            crypto_contracts.airline_crypto_artifact_seal_manifest_core_to_plain_dict_v01(
                core,
            )
        ),
        "manifest_core_hash": envelope.manifest_core_hash,
        "signature": {
            "mode": signature.mode,
            "algorithm": signature.algorithm,
            "key_id": signature.key_id,
            "value": signature.value,
            "verified": signature.verified,
        },
    }
    if projected != parsed:
        _raise(REASON_MANIFEST_DOCUMENT_PROJECTION_MISMATCH)
    return envelope, parsed


def _reconstruct_stored_verification(
    snapshot: replay_contracts.AirlineSealedTraceReplayPackageSnapshotV01,
    ledger_item: ledger_contracts.AirlineTransactionArtifactLedgerV01,
    envelope: crypto_contracts.AirlineCryptoArtifactSealEnvelopeV01,
) -> tuple[
    crypto_contracts.AirlineCryptoArtifactSealVerificationReportV01,
    dict[str, object],
]:
    try:
        parsed = crypto_contracts.parse_airline_crypto_json_object_bytes_v01(
            snapshot.stored_verification_bytes,
        )
    except Exception:
        _raise(REASON_STORED_VERIFICATION_DOCUMENT_PARSE_FAILED)
    if not (
        frozenset(parsed) == frozenset(crypto_contracts.VERIFICATION_REPORT_FIELD_NAMES)
        and type(parsed["verification_errors"]) is list
    ):
        _raise(REASON_STORED_VERIFICATION_DOCUMENT_FIELD_MISMATCH)
    try:
        report = crypto_contracts.AirlineCryptoArtifactSealVerificationReportV01(
            verification_status=parsed["verification_status"],
            transaction_id=parsed["transaction_id"],
            ledger_id=parsed["ledger_id"],
            manifest_core_hash=parsed["manifest_core_hash"],
            expected_manifest_core_hash=parsed["expected_manifest_core_hash"],
            external_anchor_supplied=parsed["external_anchor_supplied"],
            external_anchor_verified=parsed["external_anchor_verified"],
            canonicalization_profile_verified=parsed["canonicalization_profile_verified"],
            hash_algorithm_verified=parsed["hash_algorithm_verified"],
            manifest_core_hash_verified=parsed["manifest_core_hash_verified"],
            ledger_document_byte_hash_verified=parsed["ledger_document_byte_hash_verified"],
            artifact_hashes_verified=parsed["artifact_hashes_verified"],
            chain_genesis_verified=parsed["chain_genesis_verified"],
            chain_order_verified=parsed["chain_order_verified"],
            chain_head_verified=parsed["chain_head_verified"],
            chain_tail_verified=parsed["chain_tail_verified"],
            source_file_hashes_verified=parsed["source_file_hashes_verified"],
            source_package_hash_verified=parsed["source_package_hash_verified"],
            ledger_geometry_verified=parsed["ledger_geometry_verified"],
            root_ownership_verified=parsed["root_ownership_verified"],
            authority_evidence_boundaries_verified=parsed["authority_evidence_boundaries_verified"],
            secret_boundary_verified=parsed["secret_boundary_verified"],
            source_bytes_unchanged=parsed["source_bytes_unchanged"],
            signature_mode=parsed["signature_mode"],
            signature_verified=parsed["signature_verified"],
            verification_errors=tuple(parsed["verification_errors"]),
            provider_call_count=parsed["provider_call_count"],
            network_call_count=parsed["network_call_count"],
            gemini_call_count=parsed["gemini_call_count"],
            seal_created_authority_count=parsed["seal_created_authority_count"],
            seal_created_permission_count=parsed["seal_created_permission_count"],
            seal_created_action_count=parsed["seal_created_action_count"],
            real_world_effects_count=parsed["real_world_effects_count"],
        )
    except Exception:
        _raise(REASON_STORED_VERIFICATION_RECONSTRUCTION_FAILED)
    if not _stored_verification_valid(report, ledger_item, envelope):
        _raise(REASON_STORED_VERIFICATION_RECONSTRUCTION_FAILED)
    try:
        projected = (
            crypto_contracts.airline_crypto_artifact_seal_verification_report_to_plain_dict_v01(
                report,
            )
        )
    except Exception:
        _raise(REASON_STORED_VERIFICATION_PROJECTION_MISMATCH)
    if projected != parsed:
        _raise(REASON_STORED_VERIFICATION_PROJECTION_MISMATCH)
    return report, parsed


def _stored_verification_valid(
    report: object,
    ledger_item: ledger_contracts.AirlineTransactionArtifactLedgerV01,
    envelope: crypto_contracts.AirlineCryptoArtifactSealEnvelopeV01,
) -> bool:
    try:
        return (
            type(report)
            is crypto_contracts.AirlineCryptoArtifactSealVerificationReportV01
            and crypto_contracts.validate_airline_crypto_artifact_seal_verification_report_v01(
                report,
            ).validation_status
            == STATUS_PASS
            and report.verification_status
            == crypto_contracts.STATUS_SELF_CONSISTENT_UNANCHORED
            and report.expected_manifest_core_hash is None
            and report.external_anchor_supplied is False
            and report.external_anchor_verified is False
            and report.signature_mode
            == crypto_contracts.SIGNATURE_MODE_UNSIGNED_PLACEHOLDER
            and report.signature_verified is False
            and report.verification_errors == ()
            and all(getattr(report, name) is True for name in _VERIFICATION_TRUE_FIELDS)
            and all(
                type(getattr(report, name)) is int and getattr(report, name) == 0
                for name in _VERIFICATION_ZERO_FIELDS
            )
            and report.transaction_id == ledger_item.transaction_id
            and report.ledger_id == ledger_item.ledger_id
            and report.manifest_core_hash == envelope.manifest_core_hash
        )
    except Exception:
        return False


def _audit_ledger_coherent(
    accepted_audit: crypto_collector.AirlineCryptoArtifactSealAcceptedLedgerAuditV01,
    ledger_item: ledger_contracts.AirlineTransactionArtifactLedgerV01,
) -> bool:
    try:
        entries = ledger_item.entries
        selected_offer_values = tuple(
            entry.canonical_hash_input["selected_offer_id"]
            for entry in entries
            if isinstance(entry.canonical_hash_input, Mapping)
            and "selected_offer_id" in entry.canonical_hash_input
        )
        root_types = tuple(
            entry.artifact_type
            for entry in entries
            if entry.artifact_type
            in (
                ledger_contracts.ARTIFACT_CLIENT_ROOT_FINAL,
                ledger_contracts.ARTIFACT_AIRLINE_ROOT_FINAL,
                ledger_contracts.ARTIFACT_BANK_ROOT_FINAL,
            )
        )
        return (
            accepted_audit.ledger_id == ledger_item.ledger_id
            and accepted_audit.transaction_id == ledger_item.transaction_id
            and accepted_audit.source_run_ref == ledger_item.source_run_ref
            and accepted_audit.source_causal_report_ref
            == ledger_item.source_causal_report_ref
            and accepted_audit.source_corridor_report_ref
            == ledger_item.source_corridor_report_ref
            and accepted_audit.actual_entry_count == len(entries) == 19
            and accepted_audit.actual_dependency_edge_count
            == sum(len(entry.depends_on) for entry in entries)
            == 29
            and accepted_audit.actual_root_final_count == len(root_types) == 3
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
            and accepted_audit.files_read_count == 9
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
    except Exception:
        return False


def _project_expected_identity_value(value: object, active_ids: set[int]) -> object:
    if value is None or type(value) in (bool, int, str):
        return value
    if type(value) is tuple:
        value_id = id(value)
        if value_id in active_ids:
            _raise(REASON_EXPECTED_IDENTITY_ADAPTER_FAILED)
        active_ids.add(value_id)
        output = [_project_expected_identity_value(item, active_ids) for item in value]
        active_ids.remove(value_id)
        return output
    if type(value) is ledger_contracts._FrozenDict:
        value_id = id(value)
        if value_id in active_ids:
            _raise(REASON_EXPECTED_IDENTITY_ADAPTER_FAILED)
        active_ids.add(value_id)
        output_dict: dict[str, object] = {}
        for key, item in value.items():
            if type(key) is not str:
                _raise(REASON_EXPECTED_IDENTITY_ADAPTER_FAILED)
            output_dict[key] = _project_expected_identity_value(item, active_ids)
        active_ids.remove(value_id)
        return output_dict
    _raise(REASON_EXPECTED_IDENTITY_ADAPTER_FAILED)


def _build_airline_sealed_trace_replay_expected_identity_adapter_impl_v01(
    *,
    ledger_item: object,
    accepted_ledger_audit: object,
) -> ledger_contracts.AirlineTransactionArtifactLedgerExpectedIdentityV01:
    try:
        if not (
            type(ledger_item)
            is ledger_contracts.AirlineTransactionArtifactLedgerV01
            and type(accepted_ledger_audit)
            is crypto_collector.AirlineCryptoArtifactSealAcceptedLedgerAuditV01
            and crypto_collector.validate_airline_crypto_artifact_seal_accepted_ledger_audit_v01(
                accepted_ledger_audit,
            ).validation_status
            == STATUS_PASS
            and _audit_ledger_coherent(accepted_ledger_audit, ledger_item)
            and type(ledger_item.entries) is tuple
            and len(ledger_item.entries) == 19
            and tuple(entry.artifact_type for entry in ledger_item.entries)
            == ledger_contracts.EXPECTED_ARTIFACT_TYPE_SEQUENCE
            and len({entry.artifact_type for entry in ledger_item.entries}) == 19
        ):
            _raise(REASON_EXPECTED_IDENTITY_ADAPTER_FAILED)
        artifact_ids: dict[str, str] = {}
        source_refs: dict[str, tuple[str, ...]] = {}
        auxiliary_refs: dict[str, tuple[str, ...]] = {}
        source_identity: dict[str, dict[str, object]] = {}
        for entry in ledger_item.entries:
            if type(entry) is not ledger_contracts.AirlineTransactionArtifactLedgerEntryV01:
                _raise(REASON_EXPECTED_IDENTITY_ADAPTER_FAILED)
            artifact_type = entry.artifact_type
            extra_keys = ledger_contracts.CANONICAL_HASH_INPUT_EXTRA_KEYS_BY_ARTIFACT_TYPE[
                artifact_type
            ]
            if not isinstance(entry.canonical_hash_input, Mapping) or any(
                key not in entry.canonical_hash_input for key in extra_keys
            ):
                _raise(REASON_EXPECTED_IDENTITY_ADAPTER_FAILED)
            artifact_ids[artifact_type] = entry.artifact_id
            source_refs[artifact_type] = tuple(entry.source_validation_refs)
            auxiliary_refs[artifact_type] = tuple(entry.auxiliary_artifact_refs)
            source_identity[artifact_type] = {
                key: _project_expected_identity_value(
                    entry.canonical_hash_input[key],
                    set(),
                )
                for key in extra_keys
            }
        expected_types = frozenset(ledger_contracts.EXPECTED_ARTIFACT_TYPE_SEQUENCE)
        if not all(
            frozenset(mapping) == expected_types
            for mapping in (
                artifact_ids,
                source_refs,
                auxiliary_refs,
                source_identity,
            )
        ):
            _raise(REASON_EXPECTED_IDENTITY_ADAPTER_FAILED)
        adapter = ledger_contracts.AirlineTransactionArtifactLedgerExpectedIdentityV01(
            expected_source_refs=(
                ledger_contracts.AirlineTransactionArtifactLedgerExpectedSourceRefsV01(
                    source_run_ref=ledger_item.source_run_ref,
                    source_causal_report_ref=ledger_item.source_causal_report_ref,
                    source_corridor_report_ref=ledger_item.source_corridor_report_ref,
                )
            ),
            expected_artifact_ids=artifact_ids,
            expected_source_validation_refs_by_type=source_refs,
            expected_auxiliary_artifact_refs_by_type=auxiliary_refs,
            expected_source_identity_fields_by_type=source_identity,
        )
        validation = ledger_contracts.validate_airline_transaction_artifact_ledger_v01(
            ledger_item,
            expected_identity=adapter,
        )
        if validation.validation_status != STATUS_PASS or validation.validation_errors:
            _raise(REASON_EXPECTED_IDENTITY_ADAPTER_FAILED)
        return adapter
    except ValueError:
        _raise(REASON_EXPECTED_IDENTITY_ADAPTER_FAILED)
    except Exception:
        _raise(REASON_EXPECTED_IDENTITY_ADAPTER_FAILED)


def build_airline_sealed_trace_replay_expected_identity_adapter_v01(
    *,
    ledger_item: object,
    accepted_ledger_audit: object,
) -> ledger_contracts.AirlineTransactionArtifactLedgerExpectedIdentityV01:
    failure_reason = REASON_EXPECTED_IDENTITY_ADAPTER_FAILED
    try:
        return _build_airline_sealed_trace_replay_expected_identity_adapter_impl_v01(
            ledger_item=ledger_item,
            accepted_ledger_audit=accepted_ledger_audit,
        )
    except Exception as error:
        failure_reason = _stable_reason_from_exception(
            error,
            REASON_EXPECTED_IDENTITY_ADAPTER_FAILED,
        )
    _raise(failure_reason)


def _fresh_verification_valid(
    report: object,
    ledger_item: ledger_contracts.AirlineTransactionArtifactLedgerV01,
    envelope: crypto_contracts.AirlineCryptoArtifactSealEnvelopeV01,
    expected_manifest_core_hash: str,
) -> bool:
    try:
        return (
            type(report)
            is crypto_contracts.AirlineCryptoArtifactSealVerificationReportV01
            and crypto_contracts.validate_airline_crypto_artifact_seal_verification_report_v01(
                report,
            ).validation_status
            == STATUS_PASS
            and report.verification_status == STATUS_PASS
            and report.expected_manifest_core_hash == expected_manifest_core_hash
            and report.external_anchor_supplied is True
            and report.external_anchor_verified is True
            and all(getattr(report, name) is True for name in _VERIFICATION_TRUE_FIELDS)
            and report.verification_errors == ()
            and report.signature_mode
            == crypto_contracts.SIGNATURE_MODE_UNSIGNED_PLACEHOLDER
            and report.signature_verified is False
            and all(
                type(getattr(report, name)) is int and getattr(report, name) == 0
                for name in _VERIFICATION_ZERO_FIELDS
            )
            and report.transaction_id == ledger_item.transaction_id
            and report.ledger_id == ledger_item.ledger_id
            and report.manifest_core_hash == envelope.manifest_core_hash
        )
    except Exception:
        return False


def _collector_stage_timeline_valid(
    replay_input: replay_contracts.AirlineSealedTraceReplayInputV01,
    timeline: object,
) -> bool:
    try:
        if (
            type(replay_input) is not replay_contracts.AirlineSealedTraceReplayInputV01
            or type(timeline) is not tuple
            or len(timeline) != 19
            or type(replay_input.ledger_item.entries) is not tuple
            or len(replay_input.ledger_item.entries) != 19
            or any(
                type(row)
                is not replay_contracts.AirlineSealedTraceReplayTimelineRowV01
                or replay_contracts.validate_airline_sealed_trace_replay_timeline_row_v01(
                    row,
                ).validation_status
                != STATUS_PASS
                for row in timeline
            )
        ):
            return False
        replay_indexes = tuple(row.replay_index for row in timeline)
        ledger_indexes = tuple(row.ledger_index for row in timeline)
        expected_indexes = tuple(range(19))
        artifact_ids = tuple(row.artifact_id for row in timeline)
        if (
            replay_indexes != expected_indexes
            or ledger_indexes != expected_indexes
            or len(set(replay_indexes)) != 19
            or len(set(ledger_indexes)) != 19
            or len(set(artifact_ids)) != 19
            or tuple(row.artifact_type for row in timeline)
            != ledger_contracts.EXPECTED_ARTIFACT_TYPE_SEQUENCE
            or tuple(
                row.artifact_type for row in timeline if row.is_root_final
            )
            != replay_contracts.ROOT_FINAL_ARTIFACT_TYPES
            or sum(row.dependency_count for row in timeline) != 29
        ):
            return False
        entries = replay_input.ledger_item.entries
        manifest_core = replay_input.envelope.manifest_core
        seen_artifact_ids: set[str] = set()
        for index, (row, entry) in enumerate(zip(timeline, entries)):
            canonical = entry.canonical_hash_input
            if isinstance(canonical, Mapping) and "selected_offer_id" in canonical:
                selected_offer_id = canonical["selected_offer_id"]
                if type(selected_offer_id) is not str or not selected_offer_id:
                    return False
            else:
                selected_offer_id = None
            if not (
                row.replay_index == index
                and row.ledger_index == entry.ledger_index
                and row.event_time == entry.event_time
                and row.event_type == entry.event_type
                and row.artifact_type == entry.artifact_type
                and row.artifact_id == entry.artifact_id
                and row.artifact_id == manifest_core.ordered_artifact_refs[index]
                and row.artifact_hash
                == manifest_core.ordered_artifact_hashes[index]
                and row.root_owner == entry.root_owner
                and row.created_by == entry.created_by
                and row.authority_class == entry.authority_class
                and row.evidence_class == entry.evidence_class
                and row.depends_on == entry.depends_on
                and row.dependency_count == len(row.depends_on)
                and all(
                    dependency in seen_artifact_ids
                    for dependency in row.depends_on
                )
                and row.is_root_final
                is (entry.artifact_type in replay_contracts.ROOT_FINAL_ARTIFACT_TYPES)
                and row.selected_offer_id == selected_offer_id
            ):
                return False
            seen_artifact_ids.add(row.artifact_id)
        return True
    except Exception:
        return False


def _final_replay_report_valid(
    report: object,
    replay_input: object,
    timeline: object,
) -> bool:
    try:
        return (
            type(replay_input) is replay_contracts.AirlineSealedTraceReplayInputV01
            and type(timeline) is tuple
            and type(report) is replay_contracts.AirlineSealedTraceReplayReportV01
            and replay_contracts.validate_airline_sealed_trace_replay_report_v01(
                report,
            ).validation_status
            == STATUS_PASS
            and report.replay_status == STATUS_PASS
            and report.replay_version == replay_contracts.REPLAY_VERSION
            and report.replay_id
            == (
                replay_contracts.REPLAY_ID_PREFIX
                + ":"
                + replay_input.ledger_item.transaction_id
                + ":"
                + replay_input.envelope.manifest_core_hash
            )
            and report.source_package_ref == replay_input.source_package_ref
            and report.source_package_ref
            == replay_input.envelope.manifest_core.source_package_ref
            and report.transaction_id == replay_input.ledger_item.transaction_id
            and report.transaction_id
            == replay_input.envelope.manifest_core.transaction_id
            and report.ledger_id == replay_input.ledger_item.ledger_id
            and report.ledger_id == replay_input.envelope.manifest_core.ledger_id
            and report.manifest_core_hash
            == replay_input.envelope.manifest_core_hash
            and report.expected_manifest_core_hash
            == replay_input.expected_manifest_core_hash
            and report.stored_verification_status
            == replay_input.stored_verification_report.verification_status
            and report.fresh_anchored_verification_status
            == replay_input.fresh_anchored_verification_report.verification_status
            and report.external_anchor_supplied
            is replay_input.fresh_anchored_verification_report.external_anchor_supplied
            and report.external_anchor_verified
            is replay_input.fresh_anchored_verification_report.external_anchor_verified
            and report.signature_mode
            == replay_input.stored_verification_report.signature_mode
            and report.signature_mode
            == replay_input.fresh_anchored_verification_report.signature_mode
            and report.signature_verified
            is replay_input.fresh_anchored_verification_report.signature_verified
            and report.reconstructed_timeline == timeline
            and (report.ledger_entry_count, report.dependency_edge_count, report.root_final_count)
            == (19, 29, 3)
            and report.timeline_row_count == 19
            and report.stored_verification_status
            == crypto_contracts.STATUS_SELF_CONSISTENT_UNANCHORED
            and report.fresh_anchored_verification_status == STATUS_PASS
            and report.external_anchor_supplied is True
            and report.external_anchor_verified is True
            and report.signature_verified is False
            and report.source_file_count == 9
            and report.critical_package_file_count == 11
            and report.ledger_audit_count == 1
            and report.anchored_verification_count == 1
            and report.post_replay_snapshot_provider_call_count == 1
            and report.root_attestation_required is False
            and report.root_attestation_present is False
            and report.source_bytes_unchanged is True
            and report.critical_package_bytes_unchanged is True
        )
    except Exception:
        return False


def _collect_airline_sealed_trace_replay_from_package_snapshot_impl_v01(
    *,
    package_snapshot: object,
    accepted_ledger_audit: object,
    expected_manifest_core_hash: object,
    post_replay_snapshot_provider: object,
) -> replay_contracts.AirlineSealedTraceReplayReportV01:
    if not (
        type(package_snapshot)
        is replay_contracts.AirlineSealedTraceReplayPackageSnapshotV01
        and replay_contracts.validate_airline_sealed_trace_replay_package_snapshot_v01(
            package_snapshot,
        ).validation_status
        == STATUS_PASS
    ):
        _raise(REASON_PACKAGE_SNAPSHOT_INVALID)
    if not (
        type(accepted_ledger_audit)
        is crypto_collector.AirlineCryptoArtifactSealAcceptedLedgerAuditV01
        and crypto_collector.validate_airline_crypto_artifact_seal_accepted_ledger_audit_v01(
            accepted_ledger_audit,
        ).validation_status
        == STATUS_PASS
    ):
        _raise(REASON_ACCEPTED_LEDGER_AUDIT_INVALID)
    if not (
        type(expected_manifest_core_hash) is str
        and crypto_contracts.validate_sha256_hex_v01(
            expected_manifest_core_hash,
        ).validation_status
        == STATUS_PASS
    ):
        _raise(REASON_EXPECTED_MANIFEST_CORE_HASH_INVALID)
    if not callable(post_replay_snapshot_provider):
        _raise(REASON_POST_REPLAY_SNAPSHOT_PROVIDER_INVALID)

    ledger_item, _ = _reconstruct_ledger(package_snapshot)
    if not _audit_ledger_coherent(accepted_ledger_audit, ledger_item):
        _raise(REASON_AUDIT_LEDGER_IDENTITY_MISMATCH)
    envelope, _ = _reconstruct_envelope(package_snapshot, ledger_item)
    stored_report, _ = _reconstruct_stored_verification(
        package_snapshot,
        ledger_item,
        envelope,
    )
    adapter_failed = False
    try:
        expected_identity = (
            build_airline_sealed_trace_replay_expected_identity_adapter_v01(
                ledger_item=ledger_item,
                accepted_ledger_audit=accepted_ledger_audit,
            )
        )
    except Exception:
        adapter_failed = True
        expected_identity = None
    if adapter_failed:
        _raise(REASON_EXPECTED_IDENTITY_ADAPTER_FAILED)
    if ledger_contracts.validate_airline_transaction_artifact_ledger_v01(
        ledger_item,
        expected_identity=expected_identity,
    ).validation_status != STATUS_PASS:
        _raise(REASON_LEDGER_VALIDATION_FAILED)

    b2b_failed = False
    try:
        fresh_report = crypto_contracts.verify_airline_crypto_artifact_seal_v01(
            envelope,
            ledger_item=ledger_item,
            ordered_source_files_before=package_snapshot.ordered_source_files,
            ordered_source_files_after=package_snapshot.ordered_source_files,
            expected_source_package_ref=package_snapshot.source_package_ref,
            source_audit_status=crypto_contracts.STATUS_PASS,
            secret_scan_passed=True,
            expected_manifest_core_hash=expected_manifest_core_hash,
            expected_identity=expected_identity,
        )
    except Exception:
        b2b_failed = True
        fresh_report = None
    if b2b_failed:
        _raise(REASON_FRESH_ANCHORED_VERIFICATION_FAILED)
    if not _fresh_verification_valid(
        fresh_report,
        ledger_item,
        envelope,
        expected_manifest_core_hash,
    ):
        _raise(REASON_FRESH_ANCHORED_VERIFICATION_FAILED)
    replay_input_failed = False
    try:
        replay_input = replay_contracts.build_airline_sealed_trace_replay_input_v01(
            source_package_ref=package_snapshot.source_package_ref,
            accepted_ledger_audit=accepted_ledger_audit,
            ledger_item=ledger_item,
            envelope=envelope,
            stored_verification_report=stored_report,
            fresh_anchored_verification_report=fresh_report,
            expected_manifest_core_hash=expected_manifest_core_hash,
            ordered_source_files=package_snapshot.ordered_source_files,
        )
    except Exception:
        replay_input_failed = True
        replay_input = None
    if replay_input_failed:
        _raise(REASON_REPLAY_INPUT_BUILD_FAILED)
    if replay_contracts.validate_airline_sealed_trace_replay_input_v01(
        replay_input,
    ).validation_status != STATUS_PASS:
        _raise(REASON_REPLAY_INPUT_BUILD_FAILED)
    timeline_failed = False
    try:
        timeline = replay_contracts.build_airline_sealed_trace_replay_timeline_v01(
            replay_input,
        )
    except Exception:
        timeline_failed = True
        timeline = None
    if timeline_failed:
        _raise(REASON_TIMELINE_RECONSTRUCTION_FAILED)
    if not _collector_stage_timeline_valid(replay_input, timeline):
        _raise(REASON_TIMELINE_RECONSTRUCTION_FAILED)

    snapshot_provider_failed = False
    try:
        post_snapshot = post_replay_snapshot_provider()
    except Exception:
        snapshot_provider_failed = True
        post_snapshot = None
    if snapshot_provider_failed:
        _raise(REASON_POST_REPLAY_SNAPSHOT_PROVIDER_FAILED)
    if type(post_snapshot) is not replay_contracts.AirlineSealedTraceReplayPackageSnapshotV01:
        _raise(REASON_POST_REPLAY_SNAPSHOT_WRONG_TYPE)
    if replay_contracts.validate_airline_sealed_trace_replay_package_snapshot_v01(
        post_snapshot,
    ).validation_status != STATUS_PASS:
        _raise(REASON_POST_REPLAY_SNAPSHOT_MISMATCH)
    if post_snapshot != package_snapshot:
        _raise(REASON_POST_REPLAY_SNAPSHOT_MISMATCH)

    pure_replay_failed = False
    try:
        report = replay_contracts.verify_airline_sealed_trace_replay_v01(
            replay_input,
            critical_package_bytes_unchanged=True,
            post_replay_snapshot_provider_call_count=1,
        )
    except Exception:
        pure_replay_failed = True
        report = None
    if pure_replay_failed:
        _raise(REASON_PURE_REPLAY_FAILED)
    if not _final_replay_report_valid(report, replay_input, timeline):
        _raise(REASON_PURE_REPLAY_FAILED)
    return report


def collect_airline_sealed_trace_replay_from_package_snapshot_v01(
    *,
    package_snapshot: object,
    accepted_ledger_audit: object,
    expected_manifest_core_hash: object,
    post_replay_snapshot_provider: object,
) -> replay_contracts.AirlineSealedTraceReplayReportV01:
    failure_reason = REASON_PURE_REPLAY_FAILED
    try:
        return _collect_airline_sealed_trace_replay_from_package_snapshot_impl_v01(
            package_snapshot=package_snapshot,
            accepted_ledger_audit=accepted_ledger_audit,
            expected_manifest_core_hash=expected_manifest_core_hash,
            post_replay_snapshot_provider=post_replay_snapshot_provider,
        )
    except Exception as error:
        failure_reason = _stable_reason_from_exception(
            error,
            REASON_PURE_REPLAY_FAILED,
        )
    _raise(failure_reason)
