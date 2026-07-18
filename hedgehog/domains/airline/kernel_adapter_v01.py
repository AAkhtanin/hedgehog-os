"""Frozen Airline-to-Kernel compatibility adapter.

This Airline-domain adapter is pure in-memory, deterministic, and limited to
the frozen oracle. It maps accepted Airline Ledger, Crypto, and Replay objects
into existing Kernel contracts without modifying Kernel law. It performs no
package discovery, filesystem access, provider or network call, Gemini call,
transaction or Corridor rerun, Ledger or Crypto recollection, authority,
permission, Root decision, FinalOutput, or effect creation. It is not Root
Attestation and is not production integration.
"""

from __future__ import annotations

from dataclasses import dataclass as _dataclass, replace as _replace

from hedgehog.domains.airline import crypto_artifact_seal_v01 as _crypto
from hedgehog.domains.airline import sealed_trace_replay_v01 as _replay
from hedgehog.domains.airline import transaction_artifact_ledger_v01 as _ledger
from hedgehog.kernel import abi_v01 as _abi
from hedgehog.kernel import integrity_replay_v01 as _integrity

globals().pop("annotations", None)


MODULE_ID = "airline_kernel_adapter_v01"
SLICE_ID = "domain_neutral_reference_kernel_gate1_g1d1"
ADAPTER_VERSION = "v0.1"

STATUS_PASS = "PASS"
STATUS_BLOCKED_FAIL_CLOSED = "BLOCKED_FAIL_CLOSED"

TRANSACTION_ID = "tri_airline_purchase:PAR-LIM:2026-08-12:client_001"
SELECTED_OFFER_ID = "offer:mock_airline_al:PAR-LIM:001"
ROOT_IDS = (
    "root:client_os_001",
    "root:mock_airline_al",
    "root:mock_bank_a",
)

LEDGER_ENTRY_COUNT = 19
DEPENDENCY_EDGE_COUNT = 29
ROOT_FINAL_COUNT = 3
SOURCE_FILE_COUNT = 9
CRITICAL_FILE_COUNT = 11
TIMELINE_ROW_COUNT = 19

_ADAPTER_ID_DOMAIN = "hedgehog.domains.airline.kernel_adapter.v01"
_SOURCE_COMPONENT = MODULE_ID
_CAUSAL_OUTPUT_FIELD = "/airline_artifact_hash"
_CAUSAL_EFFECT = "dependency_integrity_binding"
_CAUSAL_REASON = "used:airline_ledger_dependency_hash"
_KERNEL_TIME_ENVELOPE = {
    "pt_created_at": "2026-01-01T00:00:00+00:00",
    "kt_asof": "2026-01-01T00:00:00+00:00",
    "et_observed_at": None,
    "ct_session_anchor": "session:fixture:airline_kernel_adapter:001",
    "ttl_seconds": 3600,
    "freshness_class": "static",
    "valid_from": "2026-01-01T00:00:00+00:00",
    "valid_to": "2026-01-01T01:00:00+00:00",
}
_PAYLOAD_KEYS = frozenset(
    {
        "airline_ledger_index",
        "airline_event_time",
        "airline_event_type",
        "airline_artifact_type",
        "airline_artifact_hash",
        "airline_created_by",
        "airline_authority_class",
        "airline_evidence_class",
        "airline_is_root_final",
        "airline_selected_offer_id",
        "airline_canonical_hash_input",
    }
)
_TYPE_MAPPING = (
    ("AirlineTransactionScopeV01", "SemanticEvidence", "NON_AUTHORITY", "VALIDATED"),
    ("ClientBSEPProjectionV01", "BSEPProjection", "ADVISORY", "VALIDATED"),
    ("AirlineBSEPProjectionV01", "BSEPProjection", "ADVISORY", "VALIDATED"),
    ("BankBSEPProjectionV01", "BSEPProjection", "ADVISORY", "VALIDATED"),
    (
        "CrossRootAdvisoryBSEPProjectionV01",
        "BSEPProjection",
        "ADVISORY",
        "VALIDATED",
    ),
    (
        "ValidatedAirlineSemanticSelectionEvidenceV01",
        "ValidatedEvidence",
        "EVIDENCE_ONLY",
        "VALIDATED",
    ),
    (
        "ClientRootOfferSelectionDecisionV01",
        "RootDecision",
        "ROOT_OWNED",
        "ROOT_ACCEPTED",
    ),
    (
        "AirlineRootSelectedOfferResolutionV01",
        "RootDecision",
        "ROOT_OWNED",
        "ROOT_ACCEPTED",
    ),
    ("AirlineOfferPacketV01", "ResultProposal", "ROOT_OWNED", "ROOT_ACCEPTED"),
    (
        "AirlineHoldCommitPacketV01",
        "RootOwnedIntent",
        "ROOT_OWNED",
        "ROOT_ACCEPTED",
    ),
    (
        "AirlineOfferHoldReceiptV01",
        "EvidenceReceipt",
        "EVIDENCE_ONLY",
        "RECEIPT_RECORDED",
    ),
    ("ClientPurchaseIntentV01", "RootOwnedIntent", "ROOT_OWNED", "ROOT_ACCEPTED"),
    (
        "BankPaymentAuthorizationRefV01",
        "CrossRootEvidenceRef",
        "EVIDENCE_ONLY",
        "VALIDATED",
    ),
    (
        "AirlineTicketIssueIntentV01",
        "ExecutionRequest",
        "ROOT_AUTHORIZED",
        "ROOT_ACCEPTED",
    ),
    (
        "MockTicketReceiptV01",
        "EvidenceReceipt",
        "EVIDENCE_ONLY",
        "RECEIPT_RECORDED",
    ),
    (
        "MockPurchaseReceiptV01",
        "EvidenceReceipt",
        "EVIDENCE_ONLY",
        "RECEIPT_RECORDED",
    ),
    ("ClientRootFinalV01", "RootFinal", "ROOT_OWNED", "FINALIZED"),
    ("AirlineRootFinalV01", "RootFinal", "ROOT_OWNED", "FINALIZED"),
    ("BankRootFinalV01", "RootFinal", "ROOT_OWNED", "FINALIZED"),
)
_SOURCE_ZERO_COUNTER_FIELDS = (
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
_GENERIC_ZERO_COUNTER_FIELDS = (
    "provider_call_count",
    "network_call_count",
    "semantic_rerun_count",
    "transaction_rerun_count",
    "corridor_rerun_count",
    "ledger_recollection_count",
    "crypto_recollection_count",
    "root_decision_created_count",
    "authority_created_count",
    "permission_created_count",
    "action_created_count",
    "action_commit_packet_created_count",
    "receipt_created_count",
    "final_output_created_count",
    "real_world_effects_count",
)


@_dataclass(frozen=True, slots=True)
class AirlineKernelAdapterResultV01:
    adapter_id: str
    adapter_version: str
    transaction_id: str
    selected_offer_id: str
    source_package_ref: str
    source_replay_id: str
    source_manifest_core_hash: str
    source_stored_verification_status: str
    source_fresh_verification_status: str
    source_signature_verified: bool
    root_ids: tuple[str, ...]
    kernel_artifacts: tuple[_abi.KernelArtifactV01, ...]
    kernel_manifest: _integrity.ArtifactManifestV01
    kernel_unanchored_verification: _integrity.SealVerificationResultV01
    kernel_anchored_verification: _integrity.SealVerificationResultV01
    kernel_replay: _integrity.ReplayVerificationResultV01
    causal_consumption_refs: tuple[_abi.CausalConsumptionRefV01, ...]
    ledger_entry_count: int
    dependency_edge_count: int
    root_final_count: int
    source_file_count: int
    critical_file_count: int
    timeline_row_count: int
    provider_call_count: int
    network_call_count: int
    gemini_call_count: int
    real_world_effects_count: int


def _source_contract_errors(
    replay_input: object,
    replay_report: object,
) -> tuple[str, ...]:
    if type(replay_input) is not _replay.AirlineSealedTraceReplayInputV01:
        return ("airline_kernel_adapter_source_input_invalid",)
    if type(replay_report) is not _replay.AirlineSealedTraceReplayReportV01:
        return ("airline_kernel_adapter_source_replay_invalid",)
    try:
        errors: list[str] = []
        if (
            _replay.validate_airline_sealed_trace_replay_input_v01(
                replay_input
            ).validation_status
            != STATUS_PASS
        ):
            errors.append("airline_kernel_adapter_source_input_invalid")
        if (
            _replay.validate_airline_sealed_trace_replay_report_v01(
                replay_report
            ).validation_status
            != STATUS_PASS
            or replay_report.replay_status != STATUS_PASS
        ):
            errors.append("airline_kernel_adapter_source_replay_invalid")
        ledger = replay_input.ledger_item
        if (
            type(ledger) is not _ledger.AirlineTransactionArtifactLedgerV01
            or _ledger.validate_airline_transaction_artifact_ledger_v01(
                ledger
            ).validation_status
            != STATUS_PASS
        ):
            errors.append("airline_kernel_adapter_source_input_invalid")
            return tuple(dict.fromkeys(errors))
        envelope = replay_input.envelope
        stored = replay_input.stored_verification_report
        fresh = replay_input.fresh_anchored_verification_report
        if (
            replay_report.transaction_id != TRANSACTION_ID
            or ledger.transaction_id != TRANSACTION_ID
            or replay_report.source_package_ref != replay_input.source_package_ref
            or replay_report.ledger_id != ledger.ledger_id
            or replay_report.manifest_core_hash != envelope.manifest_core_hash
            or replay_report.expected_manifest_core_hash
            != replay_input.expected_manifest_core_hash
            or replay_input.expected_manifest_core_hash != envelope.manifest_core_hash
            or envelope.manifest_core.transaction_id != TRANSACTION_ID
            or envelope.manifest_core.ledger_id != ledger.ledger_id
            or envelope.manifest_core.source_package_ref
            != replay_input.source_package_ref
            or replay_input.accepted_ledger_audit.selected_offer_id
            != SELECTED_OFFER_ID
            or tuple(entry.transaction_id for entry in ledger.entries)
            != (TRANSACTION_ID,) * LEDGER_ENTRY_COUNT
        ):
            errors.append("airline_kernel_adapter_source_binding_mismatch")
        rebuilt_timeline = _replay.build_airline_sealed_trace_replay_timeline_v01(
            replay_input
        )
        rebuilt_timeline_plain = [
            _replay.airline_sealed_trace_replay_timeline_row_to_plain_dict_v01(row)
            for row in rebuilt_timeline
        ]
        reported_timeline_plain = [
            _replay.airline_sealed_trace_replay_timeline_row_to_plain_dict_v01(row)
            for row in replay_report.reconstructed_timeline
        ]
        if _integrity.canonical_json_bytes_v01(
            rebuilt_timeline_plain
        ) != _integrity.canonical_json_bytes_v01(reported_timeline_plain):
            errors.append("airline_kernel_adapter_source_binding_mismatch")
        final_rows = tuple(row for row in rebuilt_timeline if row.is_root_final)
        if (
            tuple(entry.artifact_type for entry in ledger.entries)
            != tuple(row[0] for row in _TYPE_MAPPING)
            or len(ledger.entries) != LEDGER_ENTRY_COUNT
            or ledger.entry_count != LEDGER_ENTRY_COUNT
            or ledger.dependency_edge_count != DEPENDENCY_EDGE_COUNT
            or ledger.root_final_count != ROOT_FINAL_COUNT
            or len(rebuilt_timeline) != TIMELINE_ROW_COUNT
            or tuple(row.replay_index for row in rebuilt_timeline)
            != tuple(range(TIMELINE_ROW_COUNT))
            or len(replay_input.ordered_source_files) != SOURCE_FILE_COUNT
            or tuple(row[0] for row in replay_input.ordered_source_files)
            != _crypto.REQUIRED_SOURCE_FILE_REFS
            or envelope.manifest_core.source_file_count != SOURCE_FILE_COUNT
            or envelope.manifest_core.ordered_source_file_refs
            != _crypto.REQUIRED_SOURCE_FILE_REFS
            or len(envelope.manifest_core.ordered_artifact_refs)
            != LEDGER_ENTRY_COUNT
            or len(envelope.manifest_core.ordered_artifact_hashes)
            != LEDGER_ENTRY_COUNT
            or envelope.manifest_core.ordered_artifact_refs
            != tuple(entry.artifact_id for entry in ledger.entries)
            or replay_report.source_file_count != SOURCE_FILE_COUNT
            or replay_report.critical_package_file_count != CRITICAL_FILE_COUNT
            or replay_report.ledger_entry_count != LEDGER_ENTRY_COUNT
            or replay_report.dependency_edge_count != DEPENDENCY_EDGE_COUNT
            or replay_report.root_final_count != ROOT_FINAL_COUNT
            or replay_report.timeline_row_count != TIMELINE_ROW_COUNT
            or len(final_rows) != ROOT_FINAL_COUNT
            or tuple(row.root_owner for row in final_rows) != ROOT_IDS
            or (
                replay_report.client_root_final_count,
                replay_report.airline_root_final_count,
                replay_report.bank_root_final_count,
            )
            != (1, 1, 1)
        ):
            errors.append("airline_kernel_adapter_source_geometry_mismatch")
        if (
            stored.verification_status
            != _crypto.STATUS_SELF_CONSISTENT_UNANCHORED
            or fresh.verification_status != STATUS_PASS
            or replay_report.stored_verification_status
            != _crypto.STATUS_SELF_CONSISTENT_UNANCHORED
            or replay_report.fresh_anchored_verification_status != STATUS_PASS
            or fresh.external_anchor_supplied is not True
            or fresh.external_anchor_verified is not True
            or replay_report.external_anchor_supplied is not True
            or replay_report.external_anchor_verified is not True
            or replay_report.signature_mode
            != _crypto.SIGNATURE_MODE_UNSIGNED_PLACEHOLDER
            or replay_report.signature_verified is not False
            or envelope.signature.mode
            != _crypto.SIGNATURE_MODE_UNSIGNED_PLACEHOLDER
            or envelope.signature.verified is not False
            or replay_report.source_bytes_unchanged is not True
            or replay_report.critical_package_bytes_unchanged is not True
            or replay_report.root_attestation_required is not False
            or replay_report.root_attestation_present is not False
            or any(getattr(replay_report, name) != 0 for name in _SOURCE_ZERO_COUNTER_FIELDS)
            or any(
                getattr(ledger, name) != 0
                for name in (
                    "ledger_created_authority_count",
                    "ledger_created_permission_count",
                    "ledger_created_action_count",
                    "provider_called_count",
                    "network_used_count",
                    "gemini_called_count",
                    "real_world_effects_count",
                )
            )
            or any(
                getattr(envelope.manifest_core, name) != 0
                for name in (
                    "seal_created_authority_count",
                    "seal_created_permission_count",
                    "seal_created_action_count",
                    "real_world_effects_count",
                )
            )
            or any(
                getattr(verification, name) != 0
                for verification in (stored, fresh)
                for name in (
                    "provider_call_count",
                    "network_call_count",
                    "gemini_call_count",
                    "seal_created_authority_count",
                    "seal_created_permission_count",
                    "seal_created_action_count",
                    "real_world_effects_count",
                )
            )
        ):
            errors.append("airline_kernel_adapter_source_binding_mismatch")
        return tuple(dict.fromkeys(errors))
    except Exception:
        return ("airline_kernel_adapter_source_input_invalid",)


def _build_kernel_projection(
    replay_input: _replay.AirlineSealedTraceReplayInputV01,
    replay_report: _replay.AirlineSealedTraceReplayReportV01,
) -> tuple[
    tuple[_abi.KernelArtifactV01, ...],
    _integrity.ArtifactManifestV01,
    _integrity.SealVerificationResultV01,
    _integrity.SealVerificationResultV01,
    _integrity.ReplayVerificationResultV01,
    tuple[_abi.CausalConsumptionRefV01, ...],
]:
    ledger = replay_input.ledger_item
    timeline = _replay.build_airline_sealed_trace_replay_timeline_v01(replay_input)
    crypto_projections = _crypto.build_airline_crypto_ledger_entry_projections_v01(
        ledger
    )
    artifacts: list[_abi.KernelArtifactV01] = []
    for row, crypto_projection, mapping in zip(
        timeline,
        crypto_projections,
        _TYPE_MAPPING,
        strict=True,
    ):
        source_type, artifact_type, authority, lifecycle = mapping
        if row.artifact_type != source_type:
            raise ValueError("airline_kernel_adapter_artifact_projection_invalid")
        crypto_plain = _crypto.airline_crypto_ledger_entry_projection_to_plain_dict_v01(
            crypto_projection
        )
        artifacts.append(
            _abi.build_kernel_artifact_v01(
                abi_version="v1.0",
                artifact_id=row.artifact_id,
                artifact_type=artifact_type,
                schema_version="v1",
                transaction_id=TRANSACTION_ID,
                owner_root_id=row.root_owner,
                source_component=_SOURCE_COMPONENT,
                authority_class=authority,
                lifecycle_state=lifecycle,
                payload={
                    "airline_ledger_index": row.ledger_index,
                    "airline_event_time": row.event_time,
                    "airline_event_type": row.event_type,
                    "airline_artifact_type": row.artifact_type,
                    "airline_artifact_hash": row.artifact_hash,
                    "airline_created_by": row.created_by,
                    "airline_authority_class": row.authority_class,
                    "airline_evidence_class": row.evidence_class,
                    "airline_is_root_final": row.is_root_final,
                    "airline_selected_offer_id": row.selected_offer_id,
                    "airline_canonical_hash_input": crypto_plain[
                        "canonical_hash_input"
                    ],
                },
                trace_refs=(
                    replay_input.source_package_ref,
                    replay_report.replay_id,
                    ledger.ledger_id,
                ),
                parent_refs=row.depends_on,
                time_envelope=_KERNEL_TIME_ENVELOPE,
            )
        )
    kernel_artifacts = tuple(artifacts)
    if _abi.validate_kernel_artifact_bundle_v01(artifacts=kernel_artifacts):
        raise ValueError("airline_kernel_adapter_artifact_projection_invalid")
    canonical_refs = tuple(
        _abi.kernel_artifact_to_canonical_ref_v01(artifact)
        for artifact in kernel_artifacts
    )
    dependency_edges = tuple(
        _integrity.ArtifactDependencyEdgeV01(row.artifact_id, parent_id)
        for row in timeline
        for parent_id in row.depends_on
    )
    manifest = _integrity.build_artifact_manifest_v01(
        transaction_id=TRANSACTION_ID,
        profile=_integrity.build_default_seal_profile_v01(
            timeline_order_required=True
        ),
        artifacts=canonical_refs,
        dependency_edges=dependency_edges,
        root_ownership_bindings=tuple(
            _integrity.RootOwnershipBindingV01(row.artifact_id, row.root_owner)
            for row in timeline
        ),
        evidence_class_bindings=tuple(
            _integrity.EvidenceClassBindingV01(row.artifact_id, row.evidence_class)
            for row in timeline
        ),
        authority_class_bindings=tuple(
            _integrity.AuthorityClassBindingV01(
                artifact.artifact_id,
                artifact.authority_class,
            )
            for artifact in kernel_artifacts
        ),
    )
    payload_rows = tuple(
        (
            artifact.artifact_id,
            _abi.kernel_artifact_to_plain_dict_v01(artifact)["payload"],
        )
        for artifact in kernel_artifacts
    )
    unanchored = _integrity.verify_artifact_manifest_v01(
        manifest=manifest,
        payload_rows=payload_rows,
    )
    anchored = _integrity.verify_artifact_manifest_v01(
        manifest=manifest,
        payload_rows=payload_rows,
        expected_manifest_hash=manifest.manifest_hash,
    )
    generic_replay = _integrity.verify_artifact_replay_v01(
        manifest=manifest,
        payload_rows=payload_rows,
        expected_manifest_hash=manifest.manifest_hash,
    )
    causal_refs = tuple(
        _abi.build_causal_consumption_ref_v01(
            producer_actor_id=_SOURCE_COMPONENT,
            source_artifact_id=parent_id,
            output_field=_CAUSAL_OUTPUT_FIELD,
            consumer_component=_SOURCE_COMPONENT,
            downstream_artifact_id=row.artifact_id,
            decision_effect=_CAUSAL_EFFECT,
            disposition="USED",
            reason_code=_CAUSAL_REASON,
            trace_refs=(replay_report.replay_id, parent_id, row.artifact_id),
        )
        for row in timeline
        for parent_id in row.depends_on
    )
    if _abi.validate_causal_consumption_bundle_v01(
        artifacts=kernel_artifacts,
        causal_refs=causal_refs,
    ):
        raise ValueError("airline_kernel_adapter_causal_projection_invalid")
    return (
        kernel_artifacts,
        manifest,
        unanchored,
        anchored,
        generic_replay,
        causal_refs,
    )


def _result_plain(
    result: AirlineKernelAdapterResultV01,
) -> dict[str, object]:
    return {
        "adapter_id": result.adapter_id,
        "adapter_version": result.adapter_version,
        "transaction_id": result.transaction_id,
        "selected_offer_id": result.selected_offer_id,
        "source_package_ref": result.source_package_ref,
        "source_replay_id": result.source_replay_id,
        "source_manifest_core_hash": result.source_manifest_core_hash,
        "source_stored_verification_status": result.source_stored_verification_status,
        "source_fresh_verification_status": result.source_fresh_verification_status,
        "source_signature_verified": result.source_signature_verified,
        "root_ids": list(result.root_ids),
        "kernel_artifacts": _abi.kernel_artifacts_to_plain_list_v01(
            result.kernel_artifacts
        ),
        "kernel_manifest": _integrity.artifact_manifest_to_plain_dict_v01(
            result.kernel_manifest
        ),
        "kernel_unanchored_verification": (
            _integrity.seal_verification_result_to_plain_dict_v01(
                result.kernel_unanchored_verification
            )
        ),
        "kernel_anchored_verification": (
            _integrity.seal_verification_result_to_plain_dict_v01(
                result.kernel_anchored_verification
            )
        ),
        "kernel_replay": _integrity.replay_verification_result_to_plain_dict_v01(
            result.kernel_replay
        ),
        "causal_consumption_refs": _abi.causal_consumption_refs_to_plain_list_v01(
            result.causal_consumption_refs
        ),
        "ledger_entry_count": result.ledger_entry_count,
        "dependency_edge_count": result.dependency_edge_count,
        "root_final_count": result.root_final_count,
        "source_file_count": result.source_file_count,
        "critical_file_count": result.critical_file_count,
        "timeline_row_count": result.timeline_row_count,
        "provider_call_count": result.provider_call_count,
        "network_call_count": result.network_call_count,
        "gemini_call_count": result.gemini_call_count,
        "real_world_effects_count": result.real_world_effects_count,
    }


def _adapter_id(result: AirlineKernelAdapterResultV01) -> str:
    material = _result_plain(result)
    material.pop("adapter_id")
    return _integrity.domain_separated_sha256_hex_v01(
        domain=_ADAPTER_ID_DOMAIN,
        payload=_integrity.canonical_json_bytes_v01(material),
    )


def _result_structure_errors(result: object) -> tuple[str, ...]:
    if type(result) is not AirlineKernelAdapterResultV01:
        return ("airline_kernel_adapter_invalid",)
    try:
        errors: list[str] = []
        if (
            result.adapter_version != ADAPTER_VERSION
            or result.transaction_id != TRANSACTION_ID
            or result.selected_offer_id != SELECTED_OFFER_ID
            or type(result.source_package_ref) is not str
            or not result.source_package_ref
            or type(result.source_replay_id) is not str
            or not result.source_replay_id
            or type(result.source_manifest_core_hash) is not str
            or len(result.source_manifest_core_hash) != 64
            or any(
                character not in "0123456789abcdef"
                for character in result.source_manifest_core_hash
            )
            or result.source_stored_verification_status
            != _crypto.STATUS_SELF_CONSISTENT_UNANCHORED
            or result.source_fresh_verification_status != STATUS_PASS
            or result.source_signature_verified is not False
            or result.root_ids != ROOT_IDS
        ):
            errors.append("airline_kernel_adapter_invalid")
        artifacts_valid = not (
            type(result.kernel_artifacts) is not tuple
            or len(result.kernel_artifacts) != LEDGER_ENTRY_COUNT
            or _abi.validate_kernel_artifact_bundle_v01(
                artifacts=result.kernel_artifacts
            )
        )
        if not artifacts_valid:
            errors.append("airline_kernel_adapter_artifact_projection_invalid")
        else:
            ledger_trace_ids: set[str] = set()
            for index, (artifact, mapping) in enumerate(
                zip(result.kernel_artifacts, _TYPE_MAPPING, strict=True)
            ):
                plain = _abi.kernel_artifact_to_plain_dict_v01(artifact)
                if (
                    artifact.abi_version != "v1.0"
                    or artifact.schema_version != "v1"
                    or artifact.transaction_id != TRANSACTION_ID
                    or artifact.source_component != _SOURCE_COMPONENT
                    or artifact.artifact_type != mapping[1]
                    or artifact.authority_class != mapping[2]
                    or artifact.lifecycle_state != mapping[3]
                    or type(artifact.trace_refs) is not tuple
                    or len(artifact.trace_refs) != 3
                    or artifact.trace_refs[:2]
                    != (result.source_package_ref, result.source_replay_id)
                    or type(artifact.trace_refs[2]) is not str
                    or not artifact.trace_refs[2]
                    or set(plain["payload"]) != _PAYLOAD_KEYS
                    or plain["payload"]["airline_ledger_index"] != index
                    or plain["payload"]["airline_artifact_type"] != mapping[0]
                ):
                    errors.append(
                        "airline_kernel_adapter_artifact_projection_invalid"
                    )
                    break
                ledger_trace_ids.add(artifact.trace_refs[2])
            if (
                len(ledger_trace_ids) != 1
                or sum(
                    artifact.artifact_type == "RootFinal"
                    for artifact in result.kernel_artifacts
                )
                != ROOT_FINAL_COUNT
                or tuple(
                    artifact.owner_root_id
                    for artifact in result.kernel_artifacts
                    if artifact.artifact_type == "RootFinal"
                )
                != ROOT_IDS
            ):
                errors.append("airline_kernel_adapter_artifact_projection_invalid")
        manifest = result.kernel_manifest
        if (
            type(manifest) is not _integrity.ArtifactManifestV01
            or manifest.artifact_count != LEDGER_ENTRY_COUNT
            or manifest.dependency_edge_count != DEPENDENCY_EDGE_COUNT
            or manifest.root_ownership_binding_count != LEDGER_ENTRY_COUNT
            or manifest.evidence_class_binding_count != LEDGER_ENTRY_COUNT
            or manifest.authority_class_binding_count != LEDGER_ENTRY_COUNT
        ):
            errors.append("airline_kernel_adapter_manifest_invalid")
        if (
            result.kernel_unanchored_verification.verification_status
            != _integrity.STATUS_SELF_CONSISTENT_UNANCHORED
            or result.kernel_anchored_verification.verification_status != STATUS_PASS
            or result.kernel_replay.replay_status != STATUS_PASS
            or result.kernel_replay.artifact_count != LEDGER_ENTRY_COUNT
            or result.kernel_replay.dependency_edge_count != DEPENDENCY_EDGE_COUNT
            or any(
                getattr(result.kernel_replay, name) != 0
                for name in _GENERIC_ZERO_COUNTER_FIELDS
            )
        ):
            errors.append("airline_kernel_adapter_replay_invalid")
        if artifacts_valid and type(manifest) is _integrity.ArtifactManifestV01:
            payload_rows = tuple(
                (
                    artifact.artifact_id,
                    _abi.kernel_artifact_to_plain_dict_v01(artifact)["payload"],
                )
                for artifact in result.kernel_artifacts
            )
            expected_unanchored = _integrity.verify_artifact_manifest_v01(
                manifest=manifest,
                payload_rows=payload_rows,
            )
            expected_anchored = _integrity.verify_artifact_manifest_v01(
                manifest=manifest,
                payload_rows=payload_rows,
                expected_manifest_hash=manifest.manifest_hash,
            )
            expected_replay = _integrity.verify_artifact_replay_v01(
                manifest=manifest,
                payload_rows=payload_rows,
                expected_manifest_hash=manifest.manifest_hash,
            )
            if (
                _integrity.canonical_json_bytes_v01(
                    _integrity.seal_verification_result_to_plain_dict_v01(
                        result.kernel_unanchored_verification
                    )
                )
                != _integrity.canonical_json_bytes_v01(
                    _integrity.seal_verification_result_to_plain_dict_v01(
                        expected_unanchored
                    )
                )
                or _integrity.canonical_json_bytes_v01(
                    _integrity.seal_verification_result_to_plain_dict_v01(
                        result.kernel_anchored_verification
                    )
                )
                != _integrity.canonical_json_bytes_v01(
                    _integrity.seal_verification_result_to_plain_dict_v01(
                        expected_anchored
                    )
                )
                or _integrity.canonical_json_bytes_v01(
                    _integrity.replay_verification_result_to_plain_dict_v01(
                        result.kernel_replay
                    )
                )
                != _integrity.canonical_json_bytes_v01(
                    _integrity.replay_verification_result_to_plain_dict_v01(
                        expected_replay
                    )
                )
            ):
                errors.append("airline_kernel_adapter_replay_invalid")
        if (
            type(result.causal_consumption_refs) is not tuple
            or len(result.causal_consumption_refs) != DEPENDENCY_EDGE_COUNT
            or _abi.validate_causal_consumption_bundle_v01(
                artifacts=result.kernel_artifacts,
                causal_refs=result.causal_consumption_refs,
            )
            or any(
                ref.output_field != _CAUSAL_OUTPUT_FIELD
                or ref.decision_effect != _CAUSAL_EFFECT
                or ref.disposition != "USED"
                or ref.reason_code != _CAUSAL_REASON
                or ref.producer_actor_id != _SOURCE_COMPONENT
                or ref.consumer_component != _SOURCE_COMPONENT
                or ref.trace_refs
                != (
                    result.source_replay_id,
                    ref.source_artifact_id,
                    ref.downstream_artifact_id,
                )
                for ref in result.causal_consumption_refs
            )
            or (
                type(manifest) is _integrity.ArtifactManifestV01
                and frozenset(
                    (ref.downstream_artifact_id, ref.source_artifact_id)
                    for ref in result.causal_consumption_refs
                )
                != frozenset(
                    (edge.artifact_id, edge.depends_on_artifact_id)
                    for edge in manifest.dependency_edges
                )
            )
            or (
                artifacts_valid
                and tuple(
                    (ref.source_artifact_id, ref.downstream_artifact_id)
                    for ref in result.causal_consumption_refs
                )
                != tuple(
                    (parent_id, artifact.artifact_id)
                    for artifact in result.kernel_artifacts
                    for parent_id in artifact.parent_refs
                )
            )
        ):
            errors.append("airline_kernel_adapter_causal_projection_invalid")
        geometry_values = (
            result.ledger_entry_count,
            result.dependency_edge_count,
            result.root_final_count,
            result.source_file_count,
            result.critical_file_count,
            result.timeline_row_count,
        )
        if any(type(value) is not int for value in geometry_values) or (
            geometry_values
            != (
                LEDGER_ENTRY_COUNT,
                DEPENDENCY_EDGE_COUNT,
                ROOT_FINAL_COUNT,
                SOURCE_FILE_COUNT,
                CRITICAL_FILE_COUNT,
                TIMELINE_ROW_COUNT,
            )
        ):
            errors.append("airline_kernel_adapter_source_geometry_mismatch")
        if any(
            type(value) is not int or value != 0
            for value in (
                result.provider_call_count,
                result.network_call_count,
                result.gemini_call_count,
            )
        ):
            errors.append("airline_kernel_adapter_authority_creation_forbidden")
        if (
            type(result.real_world_effects_count) is not int
            or result.real_world_effects_count != 0
            or result.kernel_replay.real_world_effects_count != 0
        ):
            errors.append("airline_kernel_adapter_effect_creation_forbidden")
        if any(
            getattr(result.kernel_replay, name) != 0
            for name in (
                "root_decision_created_count",
                "authority_created_count",
                "permission_created_count",
                "action_created_count",
                "action_commit_packet_created_count",
                "receipt_created_count",
                "final_output_created_count",
            )
        ):
            errors.append("airline_kernel_adapter_authority_creation_forbidden")
        try:
            expected_adapter_id = _adapter_id(result)
        except Exception:
            expected_adapter_id = None
        if (
            expected_adapter_id is not None
            and result.adapter_id != expected_adapter_id
        ):
            errors.append("airline_kernel_adapter_id_mismatch")
        try:
            _integrity.canonical_json_bytes_v01(_result_plain(result))
        except Exception:
            if not errors:
                errors.append("airline_kernel_adapter_invalid")
        return tuple(dict.fromkeys(errors))
    except Exception:
        return ("airline_kernel_adapter_invalid",)


def _build_exact_result(
    replay_input: _replay.AirlineSealedTraceReplayInputV01,
    replay_report: _replay.AirlineSealedTraceReplayReportV01,
) -> AirlineKernelAdapterResultV01:
    source_errors = _source_contract_errors(replay_input, replay_report)
    if source_errors:
        raise ValueError(source_errors[0])
    (
        artifacts,
        manifest,
        unanchored,
        anchored,
        generic_replay,
        causal_refs,
    ) = _build_kernel_projection(replay_input, replay_report)
    if (
        unanchored.verification_status
        != _integrity.STATUS_SELF_CONSISTENT_UNANCHORED
        or anchored.verification_status != STATUS_PASS
        or generic_replay.replay_status != STATUS_PASS
        or manifest.artifact_count != LEDGER_ENTRY_COUNT
        or manifest.dependency_edge_count != DEPENDENCY_EDGE_COUNT
        or len(causal_refs) != DEPENDENCY_EDGE_COUNT
    ):
        raise ValueError("airline_kernel_adapter_replay_invalid")
    result = AirlineKernelAdapterResultV01(
        adapter_id="",
        adapter_version=ADAPTER_VERSION,
        transaction_id=TRANSACTION_ID,
        selected_offer_id=SELECTED_OFFER_ID,
        source_package_ref=replay_input.source_package_ref,
        source_replay_id=replay_report.replay_id,
        source_manifest_core_hash=replay_report.manifest_core_hash,
        source_stored_verification_status=replay_report.stored_verification_status,
        source_fresh_verification_status=(
            replay_report.fresh_anchored_verification_status
        ),
        source_signature_verified=replay_report.signature_verified,
        root_ids=ROOT_IDS,
        kernel_artifacts=artifacts,
        kernel_manifest=manifest,
        kernel_unanchored_verification=unanchored,
        kernel_anchored_verification=anchored,
        kernel_replay=generic_replay,
        causal_consumption_refs=causal_refs,
        ledger_entry_count=LEDGER_ENTRY_COUNT,
        dependency_edge_count=DEPENDENCY_EDGE_COUNT,
        root_final_count=ROOT_FINAL_COUNT,
        source_file_count=SOURCE_FILE_COUNT,
        critical_file_count=CRITICAL_FILE_COUNT,
        timeline_row_count=TIMELINE_ROW_COUNT,
        provider_call_count=0,
        network_call_count=0,
        gemini_call_count=0,
        real_world_effects_count=0,
    )
    return _replace(result, adapter_id=_adapter_id(result))


def build_airline_kernel_adapter_result_v01(
    *,
    replay_input: _replay.AirlineSealedTraceReplayInputV01,
    replay_report: _replay.AirlineSealedTraceReplayReportV01,
) -> AirlineKernelAdapterResultV01:
    try:
        result = _build_exact_result(replay_input, replay_report)
        if _result_structure_errors(result):
            raise ValueError("airline_kernel_adapter_invalid")
        return result
    except ValueError as exc:
        reason = str(exc)
        allowed = {
            "airline_kernel_adapter_invalid",
            "airline_kernel_adapter_source_input_invalid",
            "airline_kernel_adapter_source_replay_invalid",
            "airline_kernel_adapter_source_binding_mismatch",
            "airline_kernel_adapter_source_geometry_mismatch",
            "airline_kernel_adapter_artifact_projection_invalid",
            "airline_kernel_adapter_manifest_invalid",
            "airline_kernel_adapter_replay_invalid",
            "airline_kernel_adapter_causal_projection_invalid",
        }
        raise ValueError(
            reason if reason in allowed else "airline_kernel_adapter_invalid"
        ) from None
    except Exception:
        raise ValueError("airline_kernel_adapter_unexpected_exception") from None


def validate_airline_kernel_adapter_result_v01(
    *,
    replay_input: object,
    replay_report: object,
    result: object,
) -> tuple[str, ...]:
    try:
        source_errors = _source_contract_errors(replay_input, replay_report)
        if source_errors:
            return source_errors
        structure_errors = _result_structure_errors(result)
        if type(result) is not AirlineKernelAdapterResultV01:
            return structure_errors
        expected = _build_exact_result(replay_input, replay_report)
        errors = list(structure_errors)
        try:
            projections_differ = _integrity.canonical_json_bytes_v01(
                _result_plain(result)
            ) != _integrity.canonical_json_bytes_v01(_result_plain(expected))
        except Exception:
            projections_differ = True
        if projections_differ:
            errors.append("airline_kernel_adapter_invalid")
            if result.adapter_id != expected.adapter_id:
                errors.append("airline_kernel_adapter_id_mismatch")
        return tuple(dict.fromkeys(errors))
    except Exception:
        return ("airline_kernel_adapter_unexpected_exception",)


def airline_kernel_adapter_result_to_plain_dict_v01(
    result: AirlineKernelAdapterResultV01,
) -> dict[str, object]:
    try:
        if _result_structure_errors(result):
            raise ValueError("airline_kernel_adapter_invalid")
        projection = _result_plain(result)
        _integrity.canonical_json_bytes_v01(projection)
        return projection
    except Exception:
        raise ValueError("airline_kernel_adapter_invalid") from None
