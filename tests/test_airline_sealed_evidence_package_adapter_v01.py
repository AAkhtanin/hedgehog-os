import ast
import json
from copy import deepcopy
from dataclasses import FrozenInstanceError, fields, replace
from pathlib import Path
from types import SimpleNamespace

import pytest

from hedgehog.domains.airline import crypto_artifact_seal_collector_v01 as crypto_collector
from hedgehog.domains.airline import crypto_artifact_seal_v01 as crypto
from hedgehog.domains.airline import kernel_adapter_v01 as kernel_adapter
from hedgehog.domains.airline import sealed_evidence_package_adapter_v01 as adapter
from hedgehog.domains.airline import sealed_trace_replay_v01 as airline_replay
from hedgehog.domains.airline import transaction_artifact_ledger_collector_v01 as ledger_collector
from hedgehog.domains.airline import transaction_artifact_ledger_v01 as ledger
from hedgehog.evidence import sealed_evidence_profile_v01 as profile
from hedgehog.evidence import sealed_package_v01 as sealed_package
from hedgehog.kernel import abi_v01 as abi
from hedgehog.kernel import integrity_replay_v01 as integrity
from tests import test_airline_transaction_artifact_ledger_collector_v01 as ledger_source_fixtures


MODULE_PATH = Path(
    "hedgehog/domains/airline/sealed_evidence_package_adapter_v01.py"
)
PACKAGE_REF = "packages/airline/accepted-fixture"
MANIFEST_HASH = "a" * 64
KERNEL_MANIFEST_HASH = "b" * 64
REPLAY_ID = "airline_replay:accepted:001"
_SAFE_REPORT_TEMPLATE = None
_CONTEXT_TEMPLATE = None
_SAFE_EXECUTION_TEMPLATE = None
_RESULT_TEMPLATE = None
_REAL_LEDGER_VALIDATOR = adapter._validate_ledger_source_bundle
_REAL_CRYPTO_VALIDATOR = adapter._validate_crypto_collection
_REAL_REPLAY_INPUT_VALIDATOR = adapter._validate_replay_input
_REAL_REPLAY_REPORT_VALIDATOR = adapter._validate_replay_report
_REAL_KERNEL_VALIDATOR = adapter._validate_kernel_adapter

SAFE_FIELDS = (
    "safe_execution_id",
    "safe_execution_version",
    "execution_head",
    "run_id",
    "report_id",
    "source_task_id",
    "transaction_id",
    "selected_offer_id",
    "provider_mode",
    "model_id",
    "source_final_status",
    "actor_ids",
    "actor_safe_projection_hashes",
    "actor_validation_statuses",
    "bsep_packet_id",
    "bsep_safe_hash",
    "bsep_projection_refs",
    "bsep_projection_hashes",
    "client_root_final_id",
    "client_root_final_hash",
    "airline_root_final_id",
    "airline_root_final_hash",
    "bank_root_final_id",
    "bank_root_final_hash",
    "corridor_report_id",
    "corridor_report_hash",
    "receipt_ids",
    "receipt_safe_hashes",
    "provider_call_count",
    "network_call_count",
    "gemini_call_count",
    "raw_prompt_included",
    "raw_provider_response_included",
    "secret_scan_passed",
    "real_world_effects_count",
    "validation_errors",
    "status",
)
RESULT_FIELDS = (
    "adapter_result_id",
    "adapter_version",
    "safe_execution_id",
    "source_bundle_id",
    "transaction_id",
    "selected_offer_id",
    "ledger_id",
    "crypto_manifest_core_hash",
    "kernel_manifest_hash",
    "source_package_ref",
    "source_replay_id",
    "kernel_adapter_id",
    "domain_projection",
    "source_record_count",
    "artifact_record_count",
    "kernel_artifact_ref_count",
    "causal_ref_count",
    "root_final_count",
    "source_file_count",
    "critical_file_count",
    "replay_row_count",
    "adapter_provider_call_count",
    "adapter_network_call_count",
    "adapter_gemini_call_count",
    "created_authority_count",
    "created_permission_count",
    "action_created_count",
    "receipt_created_count",
    "final_output_created_count",
    "real_world_effects_count",
    "validation_errors",
    "status",
)
PUBLIC_FUNCTIONS = (
    "build_airline_safe_execution_projection_v01",
    "validate_airline_safe_execution_projection_v01",
    "airline_safe_execution_projection_to_plain_dict_v01",
    "build_airline_sealed_evidence_package_adapter_result_v01",
    "validate_airline_sealed_evidence_package_adapter_result_v01",
    "airline_sealed_evidence_package_adapter_result_to_plain_dict_v01",
)


def _shell(contract_type: type[object], **values: object) -> object:
    result = object.__new__(contract_type)
    for name, value in values.items():
        object.__setattr__(result, name, value)
    return result


def _clone_shell(result: object) -> object:
    cloned = object.__new__(type(result))
    if hasattr(result, "__dict__"):
        object.__getattribute__(cloned, "__dict__").update(
            object.__getattribute__(result, "__dict__")
        )
    for contract_type in type(result).__mro__:
        slots = getattr(contract_type, "__slots__", ())
        if type(slots) is str:
            slots = (slots,)
        for name in slots:
            if name not in ("__dict__", "__weakref__") and hasattr(result, name):
                object.__setattr__(cloned, name, getattr(result, name))
    return cloned


def _forge(result: object, **changes: object) -> object:
    forged = object.__new__(type(result))
    for field in fields(result):
        object.__setattr__(
            forged,
            field.name,
            changes.get(field.name, getattr(result, field.name)),
        )
    return forged


def _safe_report() -> dict[str, object]:
    global _SAFE_REPORT_TEMPLATE
    if _SAFE_REPORT_TEMPLATE is not None:
        return deepcopy(_SAFE_REPORT_TEMPLATE)
    item = ledger.build_airline_transaction_artifact_ledger_fixture_v01(
        offer_id=kernel_adapter.SELECTED_OFFER_ID,
    )
    ids_by_type = {entry.artifact_type: entry.artifact_id for entry in item.entries}
    actor_rows = [
        {
            "actor_id": actor_id,
            "safe_projection": {
                "actor_id": actor_id,
                "accepted": True,
                "safe_summary": f"accepted:{index}",
            },
            "validation_status": adapter.STATUS_PASS,
        }
        for index, actor_id in enumerate(adapter._EXPECTED_ACTOR_IDS)
    ]
    bsep_rows = [
        {
            "projection_ref": projection_ref,
            "safe_projection": {
                "projection_id": projection_id,
                "projection_ref": projection_ref,
                "accepted": True,
            },
        }
        for projection_id, projection_ref in zip(
            adapter._EXPECTED_BSEP_IDS,
            adapter._EXPECTED_BSEP_REFS,
            strict=True,
        )
    ]
    root_types = (
        ledger.ARTIFACT_CLIENT_ROOT_FINAL,
        ledger.ARTIFACT_AIRLINE_ROOT_FINAL,
        ledger.ARTIFACT_BANK_ROOT_FINAL,
    )
    receipt_types = (
        ledger.ARTIFACT_AIRLINE_OFFER_HOLD_RECEIPT,
        ledger.ARTIFACT_MOCK_TICKET_RECEIPT,
        ledger.ARTIFACT_MOCK_PURCHASE_RECEIPT,
    )
    report = {
        "execution_head": "b1096c2",
        "run_id": "airline-live-accepted-001",
        "report_id": "airline-live-report-001",
        "source_task_id": "airline-par-lim-task-001",
        "transaction_id": item.transaction_id,
        "selected_offer_id": kernel_adapter.SELECTED_OFFER_ID,
        "provider_mode": "real_provider",
        "model_id": "gemini-2.5-flash",
        "source_final_status": adapter.STATUS_PASS,
        "actors": actor_rows,
        "bsep": {
            "packet_id": "bsep:airline:accepted:001",
            "safe_projection": {"packet_id": "bsep:airline:accepted:001"},
            "projections": bsep_rows,
        },
        "root_finals": [
            {
                "root_role": role,
                "final_id": ids_by_type[artifact_type],
                "safe_projection": {
                    "root_role": role,
                    "final_id": ids_by_type[artifact_type],
                },
            }
            for role, artifact_type in zip(
                adapter._EXPECTED_ROOT_ROLES,
                root_types,
                strict=True,
            )
        ],
        "corridor": {
            "report_id": "corridor:airline:accepted:001",
            "safe_projection": {"status": "PASS", "mock_only": True},
        },
        "receipts": [
            {
                "receipt_id": ids_by_type[artifact_type],
                "safe_projection": {
                    "receipt_id": ids_by_type[artifact_type],
                    "evidence_only": True,
                },
            }
            for artifact_type in receipt_types
        ],
        "counters": {
            "provider_call_count": 12,
            "network_call_count": 12,
            "gemini_call_count": 12,
        },
        "raw_prompt_included": False,
        "raw_provider_response_included": False,
        "secret_scan_passed": True,
        "real_world_effects_count": 0,
        "validation_errors": (),
    }
    _SAFE_REPORT_TEMPLATE = report
    return deepcopy(report)


def _canonical_refs(
    item: ledger.AirlineTransactionArtifactLedgerV01,
) -> tuple[integrity.CanonicalArtifactRefV01, ...]:
    return tuple(
        integrity.CanonicalArtifactRefV01(
            artifact_id=entry.artifact_id,
            artifact_type=entry.artifact_type,
            schema_version="v1",
            transaction_id=entry.transaction_id,
            owner_root_id=entry.root_owner,
            authority_class=entry.authority_class,
            lifecycle_state="VALIDATED",
            payload_hash=f"{index + 1:064x}",
        )
        for index, entry in enumerate(item.entries)
    )


def _causal_refs(
    item: ledger.AirlineTransactionArtifactLedgerV01,
) -> tuple[abi.CausalConsumptionRefV01, ...]:
    refs = []
    for entry in item.entries:
        for parent in entry.depends_on:
            refs.append(
                abi.build_causal_consumption_ref_v01(
                    producer_actor_id=f"producer:{parent}",
                    source_artifact_id=parent,
                    output_field="/safe_projection_hash",
                    consumer_component=f"consumer:{entry.artifact_id}",
                    downstream_artifact_id=entry.artifact_id,
                    decision_effect="airline_evidence_continuity",
                    disposition="USED",
                    reason_code="used:airline_evidence_continuity",
                    trace_refs=(f"trace:{len(refs):02d}",),
                )
            )
    assert len(refs) == 29
    return tuple(refs)


def _context() -> dict[str, object]:
    global _CONTEXT_TEMPLATE
    if _CONTEXT_TEMPLATE is not None:
        return {
            name: _clone_shell(value)
            for name, value in _CONTEXT_TEMPLATE.items()
        }
    item = ledger.build_airline_transaction_artifact_ledger_fixture_v01(
        offer_id=kernel_adapter.SELECTED_OFFER_ID,
    )
    safe_execution = adapter.build_airline_safe_execution_projection_v01(
        _safe_report()
    )
    by_type = {entry.artifact_type: entry.artifact_id for entry in item.entries}
    bsep_sources = tuple(
        SimpleNamespace(
            projection_id=projection_id,
            projection_ref=projection_ref,
            bsep_packet_id=safe_execution.bsep_packet_id,
        )
        for projection_id, projection_ref in zip(
            adapter._EXPECTED_BSEP_IDS,
            safe_execution.bsep_projection_refs,
            strict=True,
        )
    )
    expected_source_refs = SimpleNamespace(
        source_run_ref=item.source_run_ref,
        source_causal_report_ref=item.source_causal_report_ref,
        source_corridor_report_ref=item.source_corridor_report_ref,
    )
    ledger_source_bundle = _shell(
        ledger_collector.AirlineTransactionArtifactLedgerSourceBundleV01,
        source_bundle_id="airline-ledger-source-bundle:accepted:001",
        transaction_id=item.transaction_id,
        expected_source_refs=expected_source_refs,
        client_bsep_projection=bsep_sources[0],
        airline_bsep_projection=bsep_sources[1],
        bank_bsep_projection=bsep_sources[2],
        cross_root_bsep_projection=bsep_sources[3],
        offer_packet=SimpleNamespace(offer_id=kernel_adapter.SELECTED_OFFER_ID),
        hold_receipt=SimpleNamespace(
            receipt_id=by_type[ledger.ARTIFACT_AIRLINE_OFFER_HOLD_RECEIPT]
        ),
        mock_ticket_receipt=SimpleNamespace(
            receipt_id=by_type[ledger.ARTIFACT_MOCK_TICKET_RECEIPT]
        ),
        mock_purchase_receipt=SimpleNamespace(
            receipt_id=by_type[ledger.ARTIFACT_MOCK_PURCHASE_RECEIPT]
        ),
        corridor_report=SimpleNamespace(run_id=safe_execution.corridor_report_id),
        client_root_final=SimpleNamespace(
            final_id=by_type[ledger.ARTIFACT_CLIENT_ROOT_FINAL]
        ),
        airline_root_final=SimpleNamespace(
            final_id=by_type[ledger.ARTIFACT_AIRLINE_ROOT_FINAL]
        ),
        bank_root_final=SimpleNamespace(
            final_id=by_type[ledger.ARTIFACT_BANK_ROOT_FINAL]
        ),
        source_validation_refs=(
            item.source_run_ref,
            item.source_causal_report_ref,
            item.source_corridor_report_ref,
        ),
    )
    manifest_core = _shell(
        crypto.AirlineCryptoArtifactSealManifestCoreV01,
        transaction_id=item.transaction_id,
        ledger_id=item.ledger_id,
        source_package_ref=PACKAGE_REF,
        source_file_count=9,
        seal_created_authority_count=0,
        seal_created_permission_count=0,
        seal_created_action_count=0,
        real_world_effects_count=0,
    )
    crypto_result = _shell(
        crypto_collector.AirlineCryptoArtifactSealCollectionResultV01,
        transaction_id=item.transaction_id,
        ledger_id=item.ledger_id,
        manifest_core_hash=MANIFEST_HASH,
        source_package_ref=PACKAGE_REF,
        manifest_core=manifest_core,
        provider_call_count=0,
        network_call_count=0,
        gemini_call_count=0,
        collector_created_authority_count=0,
        collector_created_permission_count=0,
        collector_created_action_count=0,
        real_world_effects_count=0,
    )
    replay_input = _shell(
        airline_replay.AirlineSealedTraceReplayInputV01,
        source_package_ref=PACKAGE_REF,
        accepted_ledger_audit=SimpleNamespace(
            source_run_ref=item.source_run_ref,
            source_causal_report_ref=item.source_causal_report_ref,
            source_corridor_report_ref=item.source_corridor_report_ref,
        ),
        ledger_item=item,
        envelope=SimpleNamespace(manifest_core=manifest_core),
        expected_manifest_core_hash=MANIFEST_HASH,
    )
    timeline = tuple(
        _shell(
            airline_replay.AirlineSealedTraceReplayTimelineRowV01,
            artifact_id=entry.artifact_id,
            selected_offer_id=kernel_adapter.SELECTED_OFFER_ID,
        )
        for entry in item.entries
    )
    replay_report = _shell(
        airline_replay.AirlineSealedTraceReplayReportV01,
        replay_id=REPLAY_ID,
        transaction_id=item.transaction_id,
        ledger_id=item.ledger_id,
        manifest_core_hash=MANIFEST_HASH,
        expected_manifest_core_hash=MANIFEST_HASH,
        source_package_ref=PACKAGE_REF,
        critical_package_file_count=11,
        dependency_edge_count=29,
        source_file_count=9,
        reconstructed_timeline=timeline,
        transaction_rerun_count=0,
        semantic_rerun_count=0,
        corridor_rerun_count=0,
        ledger_recollection_count=0,
        crypto_collection_count=0,
        provider_call_count=0,
        network_call_count=0,
        gemini_call_count=0,
        replay_created_authority_count=0,
        replay_created_permission_count=0,
        replay_created_action_count=0,
        replay_created_receipt_count=0,
        replay_created_final_output_count=0,
        real_world_effects_count=0,
    )
    manifest = SimpleNamespace(
        artifacts=_canonical_refs(item),
        manifest_hash=KERNEL_MANIFEST_HASH,
    )
    kernel_result = _shell(
        kernel_adapter.AirlineKernelAdapterResultV01,
        adapter_id="airline-kernel-adapter:accepted:001",
        transaction_id=item.transaction_id,
        selected_offer_id=kernel_adapter.SELECTED_OFFER_ID,
        source_package_ref=PACKAGE_REF,
        source_replay_id=REPLAY_ID,
        source_manifest_core_hash=MANIFEST_HASH,
        root_ids=kernel_adapter.ROOT_IDS,
        kernel_manifest=manifest,
        causal_consumption_refs=_causal_refs(item),
        ledger_entry_count=19,
        dependency_edge_count=29,
        root_final_count=3,
        source_file_count=9,
        critical_file_count=11,
        timeline_row_count=19,
        provider_call_count=0,
        network_call_count=0,
        gemini_call_count=0,
        real_world_effects_count=0,
    )
    context = {
        "safe_execution": safe_execution,
        "ledger_source_bundle": ledger_source_bundle,
        "crypto_collection_result": crypto_result,
        "replay_input": replay_input,
        "replay_report": replay_report,
        "kernel_adapter_result": kernel_result,
    }
    _CONTEXT_TEMPLATE = context
    return {name: _clone_shell(value) for name, value in context.items()}


def _accepted_audit(
    item: ledger.AirlineTransactionArtifactLedgerV01,
    offer_id: str,
) -> crypto_collector.AirlineCryptoArtifactSealAcceptedLedgerAuditV01:
    return crypto_collector.AirlineCryptoArtifactSealAcceptedLedgerAuditV01(
        audit_id=crypto_collector.EXPECTED_LEDGER_AUDIT_ID,
        audit_version=crypto_collector.EXPECTED_LEDGER_AUDIT_VERSION,
        final_status=crypto_collector.STATUS_PASS,
        required_source_files=crypto_collector.REQUIRED_SOURCE_FILE_REFS,
        files_read_count=9,
        ledger_id=item.ledger_id,
        transaction_id=item.transaction_id,
        selected_offer_id=offer_id,
        source_run_ref=item.source_run_ref,
        source_causal_report_ref=item.source_causal_report_ref,
        source_corridor_report_ref=item.source_corridor_report_ref,
        actual_entry_count=19,
        actual_dependency_edge_count=29,
        actual_root_final_count=3,
        client_root_final_count=1,
        airline_root_final_count=1,
        bank_root_final_count=1,
        **{
            field_name: True
            for field_name in crypto_collector.ACCEPTED_AUDIT_BOOLEAN_FIELDS
        },
        stored_validation_status=crypto_collector.STATUS_PASS,
        stored_validation_errors=(),
        **{
            field_name: 0
            for field_name in crypto_collector.ACCEPTED_AUDIT_ZERO_COUNTER_FIELDS
        },
        validation_errors=(),
    )


def _real_source_rows(
    item: ledger.AirlineTransactionArtifactLedgerV01,
    expected_identity: ledger.AirlineTransactionArtifactLedgerExpectedIdentityV01,
) -> tuple[tuple[str, bytes], ...]:
    ledger_plain = (
        crypto_collector.airline_crypto_artifact_seal_ledger_document_to_plain_dict_v01(
            item,
            expected_identity=expected_identity,
        )
    )
    rows = []
    for index, ref in enumerate(crypto_collector.REQUIRED_SOURCE_FILE_REFS):
        if index == 0:
            content = json.dumps(
                ledger_plain,
                ensure_ascii=False,
                sort_keys=True,
                separators=(",", ":"),
            ).encode("utf-8")
        else:
            content = crypto.canonical_airline_crypto_json_bytes_v01(
                {
                    "source_file_ref": ref,
                    "transaction_id": item.transaction_id,
                }
            )
        rows.append((ref, content))
    return tuple(rows)


def _real_ledger_from_source_bundle(
    source_bundle: ledger_collector.AirlineTransactionArtifactLedgerSourceBundleV01,
) -> tuple[
    ledger.AirlineTransactionArtifactLedgerV01,
    ledger.AirlineTransactionArtifactLedgerExpectedIdentityV01,
]:
    expected_identity = (
        ledger_collector.build_airline_transaction_artifact_ledger_expected_identity_from_source_v01(
            source_bundle=source_bundle
        )
    )
    offer_id = source_bundle.causal_report.semantic_recommendation_id
    resolution = source_bundle.causal_report.airline_root_resolution
    expected_ids = expected_identity.expected_artifact_ids
    fixture = ledger.build_airline_transaction_artifact_ledger_fixture_v01(
        offer_id=offer_id
    )
    fixture_types_by_id = {
        entry.artifact_id: entry.artifact_type for entry in fixture.entries
    }
    dependencies_by_type = {
        entry.artifact_type: tuple(
            expected_ids[fixture_types_by_id[dependency_id]]
            for dependency_id in entry.depends_on
        )
        for entry in fixture.entries
    }
    entries = tuple(
        ledger.build_airline_transaction_artifact_ledger_entry_from_source_v01(
            index=index,
            artifact_type=artifact_type,
            artifact_id=expected_ids[artifact_type],
            depends_on=dependencies_by_type[artifact_type],
            offer_id=offer_id,
            hold_id=source_bundle.hold_packet.hold_id,
            amount=resolution.resolved_amount,
            currency=resolution.resolved_currency,
            route_ref=resolution.resolved_route_ref,
            source_validation_refs=(
                expected_identity.expected_source_validation_refs_by_type[
                    artifact_type
                ]
            ),
            auxiliary_artifact_refs=(
                expected_identity.expected_auxiliary_artifact_refs_by_type[
                    artifact_type
                ]
            ),
            source_identity_fields=(
                expected_identity.expected_source_identity_fields_by_type[
                    artifact_type
                ]
            ),
        )
        for index, artifact_type in enumerate(
            ledger.EXPECTED_ARTIFACT_TYPE_SEQUENCE
        )
    )
    event_type_counts: dict[str, int] = {}
    for entry in entries:
        event_type_counts[entry.event_type] = (
            event_type_counts.get(entry.event_type, 0) + 1
        )
    source_refs = expected_identity.expected_source_refs
    item = ledger.AirlineTransactionArtifactLedgerV01(
        ledger_id=f"airline_transaction_artifact_ledger:{offer_id}",
        ledger_version=ledger.LEDGER_VERSION,
        transaction_id=source_bundle.transaction_id,
        source_run_ref=source_refs.source_run_ref,
        source_causal_report_ref=source_refs.source_causal_report_ref,
        source_corridor_report_ref=source_refs.source_corridor_report_ref,
        entries=entries,
        entry_count=len(entries),
        dependency_edge_count=sum(len(entry.depends_on) for entry in entries),
        event_type_counts=event_type_counts,
        root_final_count=sum(
            entry.event_type == ledger.EVENT_ROOT_FINAL_CREATED
            for entry in entries
        ),
        validation_status=ledger.STATUS_PASS,
        validation_errors=(),
        ledger_created_authority_count=0,
        ledger_created_permission_count=0,
        ledger_created_action_count=0,
        provider_called_count=0,
        network_used_count=0,
        gemini_called_count=0,
        real_world_effects_count=0,
    )
    return item, expected_identity


def _real_context() -> dict[str, object]:
    offer_id = kernel_adapter.SELECTED_OFFER_ID
    ledger_source_bundle = ledger_source_fixtures._source_bundle(offer_id)
    source_validation = (
        ledger_collector.validate_airline_transaction_artifact_ledger_source_bundle_v01(
            ledger_source_bundle
        )
    )
    assert source_validation.validation_status == adapter.STATUS_PASS
    ledger_item, expected_identity = _real_ledger_from_source_bundle(
        ledger_source_bundle
    )
    accepted_audit = _accepted_audit(ledger_item, offer_id)
    assert (
        crypto_collector.validate_airline_crypto_artifact_seal_accepted_ledger_audit_v01(
            accepted_audit
        ).validation_status
        == adapter.STATUS_PASS
    )
    replay_expected_identity = (
        airline_replay.build_airline_sealed_trace_replay_expected_identity_adapter_v01(
            ledger_item=ledger_item,
            accepted_ledger_audit=accepted_audit,
        )
    )
    assert replay_expected_identity == expected_identity
    assert (
        ledger.validate_airline_transaction_artifact_ledger_v01(
            ledger_item,
            expected_identity=expected_identity,
        ).validation_status
        == adapter.STATUS_PASS
    )
    package_ref = "airline_adapter_real_contract_fixture"
    rows = _real_source_rows(ledger_item, expected_identity)
    crypto_source_bundle = (
        crypto_collector.build_airline_crypto_artifact_seal_source_bundle_v01(
            source_bundle_id="airline_crypto_source_bundle:real_contract:001",
            source_package_ref=package_ref,
            accepted_audit=accepted_audit,
            ledger_item=ledger_item,
            expected_identity=expected_identity,
            ordered_source_files_before_audit=rows,
            ordered_source_files_after_audit=rows,
        )
    )
    crypto_source_report = (
        crypto_collector.validate_airline_crypto_artifact_seal_source_bundle_v01(
            crypto_source_bundle
        )
    )
    assert crypto_source_report.validation_status == adapter.STATUS_PASS
    manifest_core = crypto.build_airline_crypto_artifact_seal_manifest_core_v01(
        ledger_item,
        ordered_source_files=rows,
        source_package_ref=package_ref,
        source_audit_status=crypto.STATUS_PASS,
        secret_scan_passed=True,
        expected_identity=expected_identity,
    )
    envelope = crypto.build_airline_crypto_artifact_seal_envelope_v01(manifest_core)
    stored_verification = crypto.verify_airline_crypto_artifact_seal_v01(
        envelope,
        ledger_item=ledger_item,
        ordered_source_files_before=rows,
        ordered_source_files_after=rows,
        expected_source_package_ref=package_ref,
        source_audit_status=crypto.STATUS_PASS,
        secret_scan_passed=True,
        expected_manifest_core_hash=None,
        expected_identity=expected_identity,
    )
    fresh_verification = crypto.verify_airline_crypto_artifact_seal_v01(
        envelope,
        ledger_item=ledger_item,
        ordered_source_files_before=rows,
        ordered_source_files_after=rows,
        expected_source_package_ref=package_ref,
        source_audit_status=crypto.STATUS_PASS,
        secret_scan_passed=True,
        expected_manifest_core_hash=envelope.manifest_core_hash,
        expected_identity=expected_identity,
    )
    crypto_result = crypto_collector.AirlineCryptoArtifactSealCollectionResultV01(
        collection_status=crypto_collector.STATUS_PASS,
        source_bundle_id=crypto_source_bundle.source_bundle_id,
        source_package_ref=package_ref,
        transaction_id=ledger_item.transaction_id,
        ledger_id=ledger_item.ledger_id,
        manifest_core_hash=envelope.manifest_core_hash,
        expected_manifest_core_hash=envelope.manifest_core_hash,
        source_bundle_validation_report=crypto_source_report,
        manifest_core=manifest_core,
        envelope=envelope,
        verification_report=fresh_verification,
        source_bytes_unchanged_after_audit=True,
        source_bytes_unchanged_after_collection=True,
        **{
            field_name: 1
            for field_name in crypto_collector.COLLECTION_STAGE_COUNT_FIELDS
        },
        **{
            field_name: 0
            for field_name in crypto_collector.COLLECTION_ZERO_COUNTER_FIELDS
        },
        collection_errors=(),
    )
    assert (
        crypto_collector.validate_airline_crypto_artifact_seal_collection_result_v01(
            crypto_result
        ).validation_status
        == adapter.STATUS_PASS
    )
    replay_input = airline_replay.build_airline_sealed_trace_replay_input_v01(
        source_package_ref=package_ref,
        accepted_ledger_audit=accepted_audit,
        ledger_item=ledger_item,
        envelope=envelope,
        stored_verification_report=stored_verification,
        fresh_anchored_verification_report=fresh_verification,
        expected_manifest_core_hash=envelope.manifest_core_hash,
        ordered_source_files=rows,
    )
    replay_report = airline_replay.verify_airline_sealed_trace_replay_v01(
        replay_input,
        critical_package_bytes_unchanged=True,
        post_replay_snapshot_provider_call_count=1,
    )
    assert (
        airline_replay.validate_airline_sealed_trace_replay_input_v01(
            replay_input
        ).validation_status
        == adapter.STATUS_PASS
    )
    assert (
        airline_replay.validate_airline_sealed_trace_replay_report_v01(
            replay_report
        ).validation_status
        == adapter.STATUS_PASS
    )
    assert replay_report.replay_status == adapter.STATUS_PASS
    kernel_result = kernel_adapter.build_airline_kernel_adapter_result_v01(
        replay_input=replay_input,
        replay_report=replay_report,
    )
    report = _safe_report()
    report["run_id"] = "airline-real-contract-compatibility-001"
    report["report_id"] = "airline-real-contract-report-001"
    report["source_task_id"] = "airline-real-contract-task-001"
    report["transaction_id"] = ledger_item.transaction_id
    report["selected_offer_id"] = offer_id
    report["bsep"]["packet_id"] = ledger_source_bundle.client_bsep_projection.bsep_packet_id
    report["bsep"]["safe_projection"] = {
        "packet_id": ledger_source_bundle.client_bsep_projection.bsep_packet_id
    }
    source_bsep = (
        ledger_source_bundle.client_bsep_projection,
        ledger_source_bundle.airline_bsep_projection,
        ledger_source_bundle.bank_bsep_projection,
        ledger_source_bundle.cross_root_bsep_projection,
    )
    report["bsep"]["projections"] = [
        {
            "projection_ref": item.projection_ref,
            "safe_projection": {
                "projection_id": item.projection_id,
                "projection_ref": item.projection_ref,
                "accepted": True,
            },
        }
        for item in source_bsep
    ]
    roots = (
        ledger_source_bundle.client_root_final,
        ledger_source_bundle.airline_root_final,
        ledger_source_bundle.bank_root_final,
    )
    for row, root in zip(report["root_finals"], roots, strict=True):
        row["final_id"] = root.final_id
        row["safe_projection"]["final_id"] = root.final_id
    report["corridor"]["report_id"] = ledger_source_bundle.corridor_report.run_id
    receipts = (
        ledger_source_bundle.hold_receipt,
        ledger_source_bundle.mock_ticket_receipt,
        ledger_source_bundle.mock_purchase_receipt,
    )
    for row, receipt in zip(report["receipts"], receipts, strict=True):
        row["receipt_id"] = receipt.receipt_id
        row["safe_projection"]["receipt_id"] = receipt.receipt_id
    safe_execution = adapter.build_airline_safe_execution_projection_v01(report)
    return {
        "safe_execution": safe_execution,
        "ledger_source_bundle": ledger_source_bundle,
        "crypto_collection_result": crypto_result,
        "replay_input": replay_input,
        "replay_report": replay_report,
        "kernel_adapter_result": kernel_result,
    }


def _safe_execution():
    global _SAFE_EXECUTION_TEMPLATE
    if _SAFE_EXECUTION_TEMPLATE is None:
        _SAFE_EXECUTION_TEMPLATE = (
            adapter.build_airline_safe_execution_projection_v01(_safe_report())
        )
    return _SAFE_EXECUTION_TEMPLATE


def _result():
    global _RESULT_TEMPLATE
    if _RESULT_TEMPLATE is None:
        _RESULT_TEMPLATE = _build(_context())
    return _RESULT_TEMPLATE


def _build(context: dict[str, object] | None = None):
    values = context or _context()
    return adapter.build_airline_sealed_evidence_package_adapter_result_v01(
        **values
    )


def _validate(result: object, context: dict[str, object]):
    return adapter.validate_airline_sealed_evidence_package_adapter_result_v01(
        result,
        **context,
    )


def _airline_package_members(
    projection: profile.DomainEvidenceProjectionV01,
) -> tuple[tuple[sealed_package.SafeFileRecordV01, ...], tuple[bytes, ...]]:
    contents = tuple(
        json.dumps(
            {"source_record_id": source.source_record_id},
            sort_keys=True,
            separators=(",", ":"),
        ).encode("utf-8")
        + b"\n"
        for source in projection.source_records
    )
    files = tuple(
        sealed_package.build_safe_file_record_v01(
            logical_path=f"evidence/{index:02d}-{source.source_type}.json",
            media_type="application/json",
            content_bytes=content,
            evidence_class=source.evidence_class,
            source_record_ids=(source.source_record_id,),
            terminal_newline_required=True,
            secret_scan_passed=True,
        )
        for index, (source, content) in enumerate(
            zip(projection.source_records, contents, strict=True)
        )
    )
    return files, contents


def _rehash_profile_source(
    source: profile.SafeSourceRecordV01,
) -> profile.SafeSourceRecordV01:
    return replace(
        source,
        source_record_id=profile._identity_hash(
            profile._SAFE_SOURCE_RECORD_DOMAIN,
            profile._safe_source_record_plain(source, include_id=False),
        ),
    )


def _projection_with_source(
    projection: profile.DomainEvidenceProjectionV01,
    index: int,
    source: profile.SafeSourceRecordV01,
) -> profile.DomainEvidenceProjectionV01:
    sources = list(projection.source_records)
    sources[index] = source
    changed = replace(projection, source_records=tuple(sources), projection_id="0" * 64)
    return replace(changed, projection_id=profile._projection_identity(changed))


@pytest.fixture(autouse=True)
def _accepted_context_validators(monkeypatch: pytest.MonkeyPatch) -> None:
    report = SimpleNamespace(validation_status=adapter.STATUS_PASS)
    monkeypatch.setattr(adapter, "_validate_ledger_source_bundle", lambda value: report)
    monkeypatch.setattr(adapter, "_validate_crypto_collection", lambda value: report)
    monkeypatch.setattr(adapter, "_validate_replay_input", lambda value: report)
    monkeypatch.setattr(adapter, "_validate_replay_report", lambda value: report)
    monkeypatch.setattr(adapter, "_validate_kernel_adapter", lambda **values: ())


def test_module_constants_are_exact() -> None:
    assert adapter.MODULE_ID == "airline_sealed_evidence_package_adapter_v01"
    assert adapter.ADAPTER_VERSION == "v0.1"
    assert adapter.STATUS_PASS == "PASS"
    assert adapter.STATUS_FAIL_CLOSED == "FAIL_CLOSED"
    assert adapter.ADAPTER_STATUSES == ("PASS", "FAIL_CLOSED")


@pytest.mark.parametrize(
    ("contract_type", "expected_fields"),
    (
        (adapter.AirlineSafeExecutionProjectionV01, SAFE_FIELDS),
        (adapter.AirlineSealedEvidencePackageAdapterResultV01, RESULT_FIELDS),
    ),
)
def test_public_dataclass_field_order_is_exact(contract_type, expected_fields) -> None:
    assert tuple(field.name for field in fields(contract_type)) == expected_fields
    assert contract_type.__slots__ == expected_fields


@pytest.mark.parametrize(
    ("factory", "field_name"),
    (
        (_safe_execution, "run_id"),
        (_result, "status"),
    ),
)
def test_public_dataclasses_are_frozen(factory, field_name: str) -> None:
    with pytest.raises(FrozenInstanceError):
        setattr(factory(), field_name, "changed")


def test_public_surface_is_exact() -> None:
    tree = ast.parse(MODULE_PATH.read_text(encoding="utf-8"))
    public_classes = tuple(
        node.name
        for node in tree.body
        if isinstance(node, ast.ClassDef) and not node.name.startswith("_")
    )
    public_functions = tuple(
        node.name
        for node in tree.body
        if isinstance(node, ast.FunctionDef) and not node.name.startswith("_")
    )
    assert public_classes == (
        "AirlineSafeExecutionProjectionV01",
        "AirlineSealedEvidencePackageAdapterResultV01",
    )
    assert public_functions == PUBLIC_FUNCTIONS
    assert "annotations" not in vars(adapter)


@pytest.mark.parametrize("name", PUBLIC_FUNCTIONS)
def test_public_functions_are_direct_module_attributes(name: str) -> None:
    assert callable(getattr(adapter, name))


def test_safe_execution_valid_geometry_and_copy_isolation() -> None:
    report = _safe_report()
    result = adapter.build_airline_safe_execution_projection_v01(report)
    original_id = result.safe_execution_id
    report["run_id"] = "mutated"
    report["actors"][0]["safe_projection"]["accepted"] = False
    assert result.status == adapter.STATUS_PASS
    assert result.safe_execution_id == original_id
    assert result.actor_ids == adapter._EXPECTED_ACTOR_IDS
    assert len(result.actor_safe_projection_hashes) == 12
    assert len(result.bsep_projection_hashes) == 4
    assert len(result.receipt_ids) == 3
    assert adapter.validate_airline_safe_execution_projection_v01(result) == ()


@pytest.mark.parametrize("index", range(12))
def test_each_actor_identity_hash_and_status_is_bound(index: int) -> None:
    report = _safe_report()
    result = adapter.build_airline_safe_execution_projection_v01(report)
    assert result.actor_ids[index] == adapter._EXPECTED_ACTOR_IDS[index]
    assert len(result.actor_safe_projection_hashes[index]) == 64
    assert result.actor_validation_statuses[index] == adapter.STATUS_PASS


@pytest.mark.parametrize("index", range(12))
def test_each_actor_safe_projection_changes_its_hash(index: int) -> None:
    first = adapter.build_airline_safe_execution_projection_v01(_safe_report())
    changed = _safe_report()
    changed["actors"][index]["safe_projection"]["safe_summary"] = "changed"
    second = adapter.build_airline_safe_execution_projection_v01(changed)
    assert first.actor_safe_projection_hashes[index] != second.actor_safe_projection_hashes[index]
    assert first.safe_execution_id != second.safe_execution_id


@pytest.mark.parametrize("index", range(12))
def test_each_actor_failure_derives_fail_closed(index: int) -> None:
    report = _safe_report()
    report["actors"][index]["validation_status"] = adapter.STATUS_FAIL_CLOSED
    result = adapter.build_airline_safe_execution_projection_v01(report)
    assert result.status == adapter.STATUS_FAIL_CLOSED
    assert adapter.validate_airline_safe_execution_projection_v01(result) == ()


@pytest.mark.parametrize("index", range(4))
def test_each_bsep_projection_is_bound_in_order(index: int) -> None:
    result = _safe_execution()
    assert result.bsep_projection_refs[index] == adapter._EXPECTED_BSEP_REFS[index]
    assert len(result.bsep_projection_hashes[index]) == 64


@pytest.mark.parametrize(
    "missing_key",
    (
        "execution_head",
        "run_id",
        "report_id",
        "source_task_id",
        "transaction_id",
        "selected_offer_id",
        "provider_mode",
        "model_id",
        "source_final_status",
        "actors",
        "bsep",
        "root_finals",
        "corridor",
        "receipts",
        "counters",
        "raw_prompt_included",
        "raw_provider_response_included",
        "secret_scan_passed",
        "real_world_effects_count",
        "validation_errors",
    ),
)
def test_safe_report_missing_field_is_rejected(missing_key: str) -> None:
    report = _safe_report()
    del report[missing_key]
    with pytest.raises(ValueError, match="^airline_safe_execution_projection_invalid$"):
        adapter.build_airline_safe_execution_projection_v01(report)


def test_safe_report_additional_field_is_rejected() -> None:
    report = _safe_report()
    report["raw_provider_dump"] = "forbidden"
    with pytest.raises(ValueError, match="^airline_safe_execution_projection_invalid$"):
        adapter.build_airline_safe_execution_projection_v01(report)


@pytest.mark.parametrize(
    ("container", "operation"),
    (
        ("actors", "reverse"),
        ("actors", "remove"),
        ("actors", "duplicate"),
        ("bsep.projections", "reverse"),
        ("bsep.projections", "remove"),
        ("root_finals", "reverse"),
        ("root_finals", "remove"),
        ("receipts", "remove"),
    ),
)
def test_safe_geometry_attacks_are_rejected(container: str, operation: str) -> None:
    report = _safe_report()
    if container == "bsep.projections":
        values = report["bsep"]["projections"]
    else:
        values = report[container]
    if operation == "reverse":
        values.reverse()
    elif operation == "remove":
        values.pop()
    else:
        values.append(deepcopy(values[-1]))
    with pytest.raises(ValueError):
        adapter.build_airline_safe_execution_projection_v01(report)


@pytest.mark.parametrize(
    ("field_name", "value", "reason"),
    (
        ("raw_prompt_included", True, "airline_safe_execution_raw_material_forbidden"),
        ("raw_provider_response_included", True, "airline_safe_execution_raw_material_forbidden"),
        ("secret_scan_passed", False, "airline_safe_execution_secret_scan_required"),
    ),
)
def test_raw_and_secret_boundaries_fail_closed(field_name, value, reason) -> None:
    report = _safe_report()
    report[field_name] = value
    with pytest.raises(ValueError, match=f"^{reason}$"):
        adapter.build_airline_safe_execution_projection_v01(report)


@pytest.mark.parametrize(
    "forbidden_key",
    (
        "raw_prompt",
        "prompt_text",
        "raw_response",
        "provider_response",
        "api_key",
        "private_key",
        "credential",
        "secret_value",
    ),
)
def test_forbidden_material_key_is_rejected_from_safe_projection(forbidden_key: str) -> None:
    report = _safe_report()
    report["actors"][0]["safe_projection"][forbidden_key] = "not-retained"
    with pytest.raises(ValueError, match="^airline_safe_execution_raw_material_forbidden$"):
        adapter.build_airline_safe_execution_projection_v01(report)


@pytest.mark.parametrize("field_name", ("provider_call_count", "network_call_count", "gemini_call_count"))
@pytest.mark.parametrize("value", (0, 11, 13, True, 12.0))
def test_source_call_geometry_requires_exact_integer_twelve(field_name: str, value: object) -> None:
    report = _safe_report()
    report["counters"][field_name] = value
    with pytest.raises(ValueError):
        adapter.build_airline_safe_execution_projection_v01(report)


@pytest.mark.parametrize("field_name", ("provider_call_count", "network_call_count", "gemini_call_count"))
@pytest.mark.parametrize("value", (True, 12.0, 11, 13))
def test_stored_safe_source_counter_forgery_is_rejected(field_name: str, value: object) -> None:
    result = _safe_execution()
    forged = _forge(result, **{field_name: value})
    forged = _forge(forged, safe_execution_id=adapter._safe_execution_identity(forged))
    assert "airline_safe_execution_call_geometry_invalid" in (
        adapter.validate_airline_safe_execution_projection_v01(forged)
    )
    with pytest.raises(ValueError):
        adapter.airline_safe_execution_projection_to_plain_dict_v01(forged)


@pytest.mark.parametrize(
    ("field_name", "value"),
    (
        ("raw_prompt_included", 0),
        ("raw_prompt_included", 1),
        ("raw_provider_response_included", 0),
        ("raw_provider_response_included", 1),
        ("secret_scan_passed", 0),
        ("secret_scan_passed", 1),
    ),
)
def test_stored_safe_bool_requires_exact_bool(field_name: str, value: int) -> None:
    result = adapter.build_airline_safe_execution_projection_v01(_safe_report())
    forged = _forge(result, **{field_name: value})
    forged = _forge(forged, safe_execution_id=adapter._safe_execution_identity(forged))
    assert adapter.validate_airline_safe_execution_projection_v01(forged)


def test_valid_adapter_result_has_exact_geometry_and_bindings() -> None:
    context = _context()
    result = _build(context)
    projection = result.domain_projection
    assert result.status == adapter.STATUS_PASS
    assert result.validation_errors == ()
    assert (
        result.source_record_count,
        result.artifact_record_count,
        result.kernel_artifact_ref_count,
        result.causal_ref_count,
        result.root_final_count,
        result.source_file_count,
        result.critical_file_count,
        result.replay_row_count,
    ) == (6, 19, 19, 29, 3, 9, 11, 19)
    assert projection.status == profile.STATUS_PASS
    assert projection.source_provider_call_count == 12
    assert projection.source_network_call_count == 12
    assert projection.source_gemini_call_count == 12
    assert projection.projection_provider_call_count == 0
    assert projection.projection_network_call_count == 0
    assert projection.projection_gemini_call_count == 0
    assert _validate(result, context) == ()


def test_airline_projection_builds_deterministic_shared_package_manifest() -> None:
    result = _result()
    projection = result.domain_projection
    assert profile.validate_domain_evidence_projection_v01(projection) == ()
    assert projection.status == profile.STATUS_PASS
    files, contents = _airline_package_members(projection)
    first = sealed_package.build_sealed_package_manifest_v01(
        domain_projection=projection,
        safe_file_records=files,
        safe_file_contents=contents,
        kernel_manifest_hash=result.kernel_manifest_hash,
    )
    second = sealed_package.build_sealed_package_manifest_v01(
        domain_projection=projection,
        safe_file_records=files,
        safe_file_contents=contents,
        kernel_manifest_hash=result.kernel_manifest_hash,
    )
    assert first.package_status == sealed_package.STATUS_SELF_CONSISTENT_UNANCHORED
    assert sealed_package.validate_sealed_package_manifest_v01(
        first,
        domain_projection=projection,
        safe_file_contents=contents,
    ) == ()
    assert first.file_count == 6
    assert first.artifact_count == 19
    assert {
        source_id
        for item in first.safe_file_records
        for source_id in item.source_record_ids
    } == {source.source_record_id for source in projection.source_records}
    assert first.package_content_hash == second.package_content_hash
    assert first.manifest_id == second.manifest_id


def test_airline_package_seam_rejects_changed_kernel_manifest_hash() -> None:
    projection = _result().domain_projection
    files, contents = _airline_package_members(projection)
    with pytest.raises(ValueError, match="^sealed_package_reference_unresolved$"):
        sealed_package.build_sealed_package_manifest_v01(
            domain_projection=projection,
            safe_file_records=files,
            safe_file_contents=contents,
            kernel_manifest_hash="f" * 64,
        )


def test_airline_package_seam_rejects_removed_crypto_trace() -> None:
    result = _result()
    crypto_source = result.domain_projection.source_records[4]
    changed_source = _rehash_profile_source(
        replace(
            crypto_source,
            trace_refs=tuple(
                ref for ref in crypto_source.trace_refs if ref != result.kernel_manifest_hash
            ),
        )
    )
    projection = _projection_with_source(result.domain_projection, 4, changed_source)
    assert profile.validate_domain_evidence_projection_v01(projection) == ()
    files, contents = _airline_package_members(projection)
    with pytest.raises(ValueError, match="^sealed_package_reference_unresolved$"):
        sealed_package.build_sealed_package_manifest_v01(
            domain_projection=projection,
            safe_file_records=files,
            safe_file_contents=contents,
            kernel_manifest_hash=result.kernel_manifest_hash,
        )


def test_airline_package_seam_rejects_changed_file_bytes() -> None:
    result = _result()
    files, contents = _airline_package_members(result.domain_projection)
    manifest = sealed_package.build_sealed_package_manifest_v01(
        domain_projection=result.domain_projection,
        safe_file_records=files,
        safe_file_contents=contents,
        kernel_manifest_hash=result.kernel_manifest_hash,
    )
    changed = (b'{"changed":true}\n', *contents[1:])
    assert "sealed_package_hash_mismatch" in (
        sealed_package.validate_sealed_package_manifest_v01(
            manifest,
            domain_projection=result.domain_projection,
            safe_file_contents=changed,
        )
    )


def test_airline_package_seam_rejects_incomplete_source_coverage() -> None:
    result = _result()
    files, contents = _airline_package_members(result.domain_projection)
    with pytest.raises(ValueError, match="^sealed_package_reference_unresolved$"):
        sealed_package.build_sealed_package_manifest_v01(
            domain_projection=result.domain_projection,
            safe_file_records=files[:-1],
            safe_file_contents=contents[:-1],
            kernel_manifest_hash=result.kernel_manifest_hash,
        )


def test_airline_package_seam_rejects_self_rehashed_false_grounding() -> None:
    result = _result()
    crypto_source = result.domain_projection.source_records[4]
    changed_source = _rehash_profile_source(
        replace(
            crypto_source,
            evidence_class="EXECUTED_DETERMINISTIC_RUNTIME",
        )
    )
    projection = _projection_with_source(result.domain_projection, 4, changed_source)
    assert profile.validate_domain_evidence_projection_v01(projection) == ()
    files, contents = _airline_package_members(projection)
    with pytest.raises(ValueError, match="^sealed_package_reference_unresolved$"):
        sealed_package.build_sealed_package_manifest_v01(
            domain_projection=projection,
            safe_file_records=files,
            safe_file_contents=contents,
            kernel_manifest_hash=result.kernel_manifest_hash,
        )


def test_real_committed_contract_chain_passes_without_validator_stubs(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setattr(adapter, "_validate_ledger_source_bundle", _REAL_LEDGER_VALIDATOR)
    monkeypatch.setattr(adapter, "_validate_crypto_collection", _REAL_CRYPTO_VALIDATOR)
    monkeypatch.setattr(adapter, "_validate_replay_input", _REAL_REPLAY_INPUT_VALIDATOR)
    monkeypatch.setattr(adapter, "_validate_replay_report", _REAL_REPLAY_REPORT_VALIDATOR)
    monkeypatch.setattr(adapter, "_validate_kernel_adapter", _REAL_KERNEL_VALIDATOR)
    context = _real_context()
    assert (
        ledger_collector.validate_airline_transaction_artifact_ledger_source_bundle_v01(
            context["ledger_source_bundle"]
        ).validation_status
        == adapter.STATUS_PASS
    )
    assert (
        crypto_collector.validate_airline_crypto_artifact_seal_collection_result_v01(
            context["crypto_collection_result"]
        ).validation_status
        == adapter.STATUS_PASS
    )
    assert (
        airline_replay.validate_airline_sealed_trace_replay_input_v01(
            context["replay_input"]
        ).validation_status
        == adapter.STATUS_PASS
    )
    assert (
        airline_replay.validate_airline_sealed_trace_replay_report_v01(
            context["replay_report"]
        ).validation_status
        == adapter.STATUS_PASS
    )
    assert kernel_adapter.validate_airline_kernel_adapter_result_v01(
        replay_input=context["replay_input"],
        replay_report=context["replay_report"],
        result=context["kernel_adapter_result"],
    ) == ()
    result = _build(context)
    assert result.status == adapter.STATUS_PASS
    assert adapter.validate_airline_sealed_evidence_package_adapter_result_v01(
        result,
        **context,
    ) == ()
    source_bsep = (
        context["ledger_source_bundle"].client_bsep_projection,
        context["ledger_source_bundle"].airline_bsep_projection,
        context["ledger_source_bundle"].bank_bsep_projection,
        context["ledger_source_bundle"].cross_root_bsep_projection,
    )
    assert tuple(item.projection_id for item in source_bsep) == adapter._EXPECTED_BSEP_IDS
    assert tuple(item.projection_ref for item in source_bsep) == (
        context["safe_execution"].bsep_projection_refs
    )


@pytest.mark.parametrize(
    ("owner", "field_name", "index"),
    (
        ("expected", "source_run_ref", 0),
        ("expected", "source_causal_report_ref", 1),
        ("expected", "source_corridor_report_ref", 2),
        ("bundle", "source_validation_refs", 0),
        ("bundle", "source_validation_refs", 1),
        ("bundle", "source_validation_refs", 2),
        ("ledger", "source_run_ref", 0),
        ("ledger", "source_causal_report_ref", 1),
        ("ledger", "source_corridor_report_ref", 2),
        ("audit", "source_run_ref", 0),
        ("audit", "source_causal_report_ref", 1),
        ("audit", "source_corridor_report_ref", 2),
    ),
)
def test_each_public_source_lineage_field_is_bound(
    owner: str,
    field_name: str,
    index: int,
) -> None:
    context = _context()
    if owner == "expected":
        current = context["ledger_source_bundle"].expected_source_refs
        changed = SimpleNamespace(**vars(current))
        setattr(changed, field_name, f"changed:{field_name}")
        object.__setattr__(context["ledger_source_bundle"], "expected_source_refs", changed)
    elif owner == "bundle":
        refs = list(context["ledger_source_bundle"].source_validation_refs)
        refs[index] = f"changed:{index}"
        object.__setattr__(
            context["ledger_source_bundle"],
            "source_validation_refs",
            tuple(refs),
        )
    elif owner == "ledger":
        changed_ledger = replace(
            context["replay_input"].ledger_item,
            **{field_name: f"changed:{field_name}"},
        )
        object.__setattr__(context["replay_input"], "ledger_item", changed_ledger)
    else:
        current = context["replay_input"].accepted_ledger_audit
        changed = SimpleNamespace(**vars(current))
        setattr(changed, field_name, f"changed:{field_name}")
        object.__setattr__(context["replay_input"], "accepted_ledger_audit", changed)
    result = _build(context)
    assert result.status == adapter.STATUS_FAIL_CLOSED
    assert "airline_sealed_evidence_source_lineage_mismatch" in result.validation_errors


@pytest.mark.parametrize("index", range(4))
@pytest.mark.parametrize("field_name", ("projection_id", "projection_ref"))
def test_each_bsep_public_identity_field_is_bound(
    index: int,
    field_name: str,
) -> None:
    context = _context()
    names = (
        "client_bsep_projection",
        "airline_bsep_projection",
        "bank_bsep_projection",
        "cross_root_bsep_projection",
    )
    source = getattr(context["ledger_source_bundle"], names[index])
    changed = SimpleNamespace(**vars(source))
    setattr(changed, field_name, f"changed:{field_name}:{index}")
    object.__setattr__(context["ledger_source_bundle"], names[index], changed)
    result = _build(context)
    assert result.status == adapter.STATUS_FAIL_CLOSED
    assert "airline_sealed_evidence_bsep_mismatch" in result.validation_errors


def test_normalized_safe_input_boundary_is_explicit() -> None:
    assert "owner-built safe normalization" in adapter.__doc__
    assert "does not accept or" in adapter.__doc__
    result = _result()
    assert (
        "limitation:owner_built_safe_normalization_not_raw_provider_report"
        in result.domain_projection.limitation_refs
    )
    report = _safe_report()
    report["raw_provider_report"] = {"provider_response": "forbidden"}
    with pytest.raises(ValueError, match="^airline_safe_execution_projection_invalid$"):
        adapter.build_airline_safe_execution_projection_v01(report)


@pytest.mark.parametrize("index", range(6))
def test_each_shared_source_record_is_safe_and_resolved(index: int) -> None:
    result = _result()
    source = result.domain_projection.source_records[index]
    assert source.contains_raw_prompt is False
    assert source.contains_raw_provider_response is False
    assert source.secret_scan_passed is True
    assert source.real_world_effects_count == 0
    expected = (12, 12, 12) if index == 0 else (0, 0, 0)
    assert (
        source.observed_provider_call_count,
        source.observed_network_call_count,
        source.observed_gemini_call_count,
    ) == expected


@pytest.mark.parametrize("index", range(19))
def test_each_shared_artifact_and_kernel_ref_preserves_order(index: int) -> None:
    result = _result()
    projection = result.domain_projection
    artifact = projection.artifact_records[index]
    kernel_ref = projection.kernel_artifact_refs[index]
    assert artifact.artifact_id == kernel_ref.artifact_id
    assert artifact.source_record_ids[0] in {
        source.source_record_id for source in projection.source_records
    }
    assert artifact.created_authority_count == 0
    assert artifact.created_permission_count == 0
    assert artifact.real_world_effects_count == 0


@pytest.mark.parametrize("index", range(29))
def test_each_causal_reference_is_valid_and_ordered(index: int) -> None:
    result = _result()
    causal_ref = result.domain_projection.causal_consumption_refs[index]
    assert abi.validate_causal_consumption_ref_v01(causal_ref) == ()
    assert causal_ref.trace_refs == (f"trace:{index:02d}",)


@pytest.mark.parametrize("index", range(3))
def test_each_root_final_is_bound(index: int) -> None:
    context = _context()
    result = _result()
    expected = (
        context["ledger_source_bundle"].client_root_final.final_id,
        context["ledger_source_bundle"].airline_root_final.final_id,
        context["ledger_source_bundle"].bank_root_final.final_id,
    )
    assert result.domain_projection.artifact_records[-3 + index].artifact_id == expected[index]


@pytest.mark.parametrize(
    ("context_key", "field_name", "changed", "expected_reason"),
    (
        ("ledger_source_bundle", "transaction_id", "transaction:changed", "airline_sealed_evidence_transaction_mismatch"),
        ("crypto_collection_result", "transaction_id", "transaction:changed", "airline_sealed_evidence_transaction_mismatch"),
        ("replay_report", "transaction_id", "transaction:changed", "airline_sealed_evidence_transaction_mismatch"),
        ("kernel_adapter_result", "transaction_id", "transaction:changed", "airline_sealed_evidence_transaction_mismatch"),
        ("kernel_adapter_result", "selected_offer_id", "offer:changed", "airline_sealed_evidence_offer_mismatch"),
        ("crypto_collection_result", "ledger_id", "ledger:changed", "airline_sealed_evidence_ledger_mismatch"),
        ("replay_report", "ledger_id", "ledger:changed", "airline_sealed_evidence_ledger_mismatch"),
        ("crypto_collection_result", "manifest_core_hash", "c" * 64, "airline_sealed_evidence_manifest_hash_mismatch"),
        ("replay_input", "expected_manifest_core_hash", "c" * 64, "airline_sealed_evidence_manifest_hash_mismatch"),
        ("replay_report", "manifest_core_hash", "c" * 64, "airline_sealed_evidence_manifest_hash_mismatch"),
        ("kernel_adapter_result", "source_manifest_core_hash", "c" * 64, "airline_sealed_evidence_manifest_hash_mismatch"),
        ("crypto_collection_result", "source_package_ref", "packages/changed", "airline_sealed_evidence_package_ref_mismatch"),
        ("replay_input", "source_package_ref", "packages/changed", "airline_sealed_evidence_package_ref_mismatch"),
        ("replay_report", "source_package_ref", "packages/changed", "airline_sealed_evidence_package_ref_mismatch"),
        ("kernel_adapter_result", "source_package_ref", "packages/changed", "airline_sealed_evidence_package_ref_mismatch"),
        ("kernel_adapter_result", "source_replay_id", "replay:changed", "airline_sealed_evidence_replay_mismatch"),
        ("kernel_adapter_result", "ledger_entry_count", 18, "airline_sealed_evidence_geometry_mismatch"),
        ("kernel_adapter_result", "dependency_edge_count", 28, "airline_sealed_evidence_geometry_mismatch"),
        ("kernel_adapter_result", "root_final_count", 2, "airline_sealed_evidence_geometry_mismatch"),
        ("kernel_adapter_result", "source_file_count", 8, "airline_sealed_evidence_geometry_mismatch"),
        ("kernel_adapter_result", "critical_file_count", 10, "airline_sealed_evidence_geometry_mismatch"),
        ("kernel_adapter_result", "timeline_row_count", 18, "airline_sealed_evidence_geometry_mismatch"),
        ("replay_report", "critical_package_file_count", 10, "airline_sealed_evidence_geometry_mismatch"),
        ("replay_report", "source_file_count", 8, "airline_sealed_evidence_geometry_mismatch"),
        ("replay_report", "dependency_edge_count", 28, "airline_sealed_evidence_geometry_mismatch"),
    ),
)
def test_cross_contract_mismatch_derives_fail_closed(
    context_key: str,
    field_name: str,
    changed: object,
    expected_reason: str,
) -> None:
    context = _context()
    object.__setattr__(context[context_key], field_name, changed)
    if field_name == "critical_package_file_count":
        with pytest.raises(
            ValueError,
            match="^airline_sealed_evidence_adapter_geometry_mismatch$",
        ):
            _build(context)
    elif (context_key, field_name) in {
        ("ledger_source_bundle", "transaction_id"),
        ("kernel_adapter_result", "selected_offer_id"),
        ("crypto_collection_result", "ledger_id"),
        ("crypto_collection_result", "manifest_core_hash"),
        ("crypto_collection_result", "source_package_ref"),
        ("kernel_adapter_result", "source_replay_id"),
        ("kernel_adapter_result", "ledger_entry_count"),
    }:
        result = _build(context)
        assert result.status == adapter.STATUS_FAIL_CLOSED
        assert expected_reason in result.validation_errors
    else:
        assert expected_reason in adapter._cross_contract_errors(**context)


@pytest.mark.parametrize(
    ("context_key", "field_name"),
    (
        ("crypto_collection_result", "provider_call_count"),
        ("crypto_collection_result", "network_call_count"),
        ("crypto_collection_result", "gemini_call_count"),
        ("crypto_collection_result", "collector_created_authority_count"),
        ("crypto_collection_result", "collector_created_permission_count"),
        ("crypto_collection_result", "collector_created_action_count"),
        ("crypto_collection_result", "real_world_effects_count"),
        ("replay_report", "transaction_rerun_count"),
        ("replay_report", "semantic_rerun_count"),
        ("replay_report", "corridor_rerun_count"),
        ("replay_report", "ledger_recollection_count"),
        ("replay_report", "crypto_collection_count"),
        ("replay_report", "provider_call_count"),
        ("replay_report", "network_call_count"),
        ("replay_report", "gemini_call_count"),
        ("replay_report", "replay_created_authority_count"),
        ("replay_report", "replay_created_permission_count"),
        ("replay_report", "replay_created_action_count"),
        ("replay_report", "replay_created_receipt_count"),
        ("replay_report", "replay_created_final_output_count"),
        ("replay_report", "real_world_effects_count"),
        ("kernel_adapter_result", "provider_call_count"),
        ("kernel_adapter_result", "network_call_count"),
        ("kernel_adapter_result", "gemini_call_count"),
        ("kernel_adapter_result", "real_world_effects_count"),
    ),
)
def test_domain_operation_boundary_mismatch_derives_fail_closed(
    context_key: str,
    field_name: str,
) -> None:
    context = _context()
    object.__setattr__(context[context_key], field_name, 1)
    errors = adapter._cross_contract_errors(**context)
    assert "airline_sealed_evidence_effect_boundary_invalid" in errors


RESULT_ZERO_FIELDS = (
    "adapter_provider_call_count",
    "adapter_network_call_count",
    "adapter_gemini_call_count",
    "created_authority_count",
    "created_permission_count",
    "action_created_count",
    "receipt_created_count",
    "final_output_created_count",
    "real_world_effects_count",
)


@pytest.mark.parametrize("field_name", RESULT_ZERO_FIELDS)
def test_result_zero_boundary_rejects_nonexact_or_nonzero_counts(
    field_name: str,
) -> None:
    context = _context()
    result = _result()
    forged = _forge(result, **{field_name: 1})
    forged = _forge(forged, adapter_result_id=adapter._adapter_result_identity(forged))
    errors = adapter._adapter_result_structure_errors(forged)
    assert errors
    assert "airline_sealed_evidence_adapter_zero_boundary_invalid" in errors
    with pytest.raises(ValueError):
        adapter.airline_sealed_evidence_package_adapter_result_to_plain_dict_v01(
            forged,
            **context,
        )


@pytest.mark.parametrize(
    ("field_name", "value"),
    (
        ("adapter_provider_call_count", True),
        ("adapter_network_call_count", False),
        ("created_authority_count", 1.0),
        ("real_world_effects_count", 0.0),
    ),
)
def test_result_zero_boundary_rejects_bool_and_float_attacks(
    field_name: str,
    value: object,
) -> None:
    forged = _forge(_result(), **{field_name: value})
    forged = _forge(forged, adapter_result_id=adapter._adapter_result_identity(forged))
    assert "airline_sealed_evidence_adapter_zero_boundary_invalid" in (
        adapter._adapter_result_structure_errors(forged)
    )


GEOMETRY_FIELDS = (
    "source_record_count",
    "artifact_record_count",
    "kernel_artifact_ref_count",
    "causal_ref_count",
    "root_final_count",
    "source_file_count",
    "critical_file_count",
    "replay_row_count",
)


@pytest.mark.parametrize("field_name", GEOMETRY_FIELDS)
def test_result_geometry_rejects_exact_type_and_value_attacks(
    field_name: str,
) -> None:
    context = _context()
    result = _result()
    forged = _forge(result, **{field_name: 0})
    forged = _forge(forged, adapter_result_id=adapter._adapter_result_identity(forged))
    errors = adapter._adapter_result_structure_errors(forged)
    assert "airline_sealed_evidence_adapter_geometry_mismatch" in errors


@pytest.mark.parametrize(
    ("field_name", "value"),
    (
        ("source_record_count", True),
        ("artifact_record_count", 1.0),
        ("kernel_artifact_ref_count", False),
        ("causal_ref_count", 0.0),
    ),
)
def test_result_geometry_rejects_bool_and_float_attacks(
    field_name: str,
    value: object,
) -> None:
    forged = _forge(_result(), **{field_name: value})
    forged = _forge(forged, adapter_result_id=adapter._adapter_result_identity(forged))
    errors = adapter._adapter_result_structure_errors(forged)
    assert "airline_sealed_evidence_adapter_geometry_mismatch" in errors


@pytest.mark.parametrize(
    "field_name",
    (
        "safe_execution_id",
        "source_bundle_id",
        "transaction_id",
        "selected_offer_id",
        "ledger_id",
        "crypto_manifest_core_hash",
        "kernel_manifest_hash",
        "source_package_ref",
        "source_replay_id",
        "kernel_adapter_id",
    ),
)
def test_self_rehashed_result_identity_binding_attack_is_rejected(field_name: str) -> None:
    context = _context()
    result = _result()
    value = "c" * 64 if "hash" in field_name or field_name == "safe_execution_id" else "changed:value"
    forged = _forge(result, **{field_name: value})
    forged = _forge(forged, adapter_result_id=adapter._adapter_result_identity(forged))
    assert "airline_sealed_evidence_adapter_context_mismatch" in _validate(forged, context)


@pytest.mark.parametrize(
    ("validation_errors", "status"),
    (
        (("forged:error",), adapter.STATUS_PASS),
        ((), adapter.STATUS_FAIL_CLOSED),
    ),
)
def test_synthetic_status_is_rejected(validation_errors, status) -> None:
    context = _context()
    result = _result()
    forged = _forge(result, validation_errors=validation_errors, status=status)
    forged = _forge(forged, adapter_result_id=adapter._adapter_result_identity(forged))
    assert "airline_sealed_evidence_adapter_status_mismatch" in _validate(forged, context)


def test_safe_public_projection_is_json_safe_and_mutation_isolated() -> None:
    result = _safe_execution()
    plain = adapter.airline_safe_execution_projection_to_plain_dict_v01(result)
    json.dumps(plain, sort_keys=True)
    plain["actor_ids"][0] = "changed"
    assert result.actor_ids[0] == adapter._EXPECTED_ACTOR_IDS[0]
    assert not any(isinstance(value, tuple) for value in plain.values())


def test_adapter_public_projection_is_json_safe_and_mutation_isolated() -> None:
    context = _context()
    result = _result()
    plain = adapter.airline_sealed_evidence_package_adapter_result_to_plain_dict_v01(
        result,
        **context,
    )
    json.dumps(plain, sort_keys=True)
    plain["domain_projection"]["evidence_refs"][0] = "changed"
    assert result.domain_projection.evidence_refs[0] != "changed"


@pytest.mark.parametrize(
    "token",
    (
        "pathlib",
        "import os",
        "tempfile",
        "subprocess",
        "datetime",
        "import time",
        "random",
        "secrets",
        "uuid",
        "cryptography",
        "from demo",
        "from tests",
        "sealed_package_v01",
        "external_anchor_v01",
        "sealed_replay_evidence_v01",
        "open(",
        ".read_text(",
        ".write_text(",
        "os.environ",
        "getenv(",
        "provider.generate",
        "network_call(",
        "gemini_call(",
        "collect_airline",
        "create_authority(",
        "create_permission(",
        "execute_effect(",
    ),
)
def test_static_forbidden_capabilities_are_absent(token: str) -> None:
    source = MODULE_PATH.read_text(encoding="utf-8")
    assert token not in source


def test_static_import_boundary_is_exact() -> None:
    tree = ast.parse(MODULE_PATH.read_text(encoding="utf-8"))
    modules = {
        node.module
        for node in ast.walk(tree)
        if isinstance(node, ast.ImportFrom)
    }
    assert modules <= {
        "collections.abc",
        "dataclasses",
        "hedgehog.evidence.sealed_evidence_profile_v01",
        "hedgehog.domains.airline.transaction_artifact_ledger_collector_v01",
        "hedgehog.domains.airline.transaction_artifact_ledger_v01",
        "hedgehog.domains.airline.crypto_artifact_seal_collector_v01",
        "hedgehog.domains.airline.crypto_artifact_seal_v01",
        "hedgehog.domains.airline.sealed_trace_replay_v01",
        "hedgehog.domains.airline.kernel_adapter_v01",
        "hedgehog.kernel.integrity_replay_v01",
        "hedgehog.kernel.abi_v01",
    }


def test_adapter_never_calls_imported_collectors_or_runners() -> None:
    tree = ast.parse(MODULE_PATH.read_text(encoding="utf-8"))
    called_names = {
        node.func.id
        for node in ast.walk(tree)
        if isinstance(node, ast.Call) and isinstance(node.func, ast.Name)
    }
    assert not any(name.startswith("collect_") for name in called_names)
    assert not any("runner" in name for name in called_names)
    assert not any("provider" in name for name in called_names)
