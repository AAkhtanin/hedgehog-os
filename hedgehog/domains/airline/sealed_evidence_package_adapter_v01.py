"""Frozen Airline evidence mapping from owner-normalized safe input only.

AirlineSafeExecutionProjectionV01 consumes one explicit owner-built safe normalization
produced from accepted live evidence. It does not accept or retain the raw provider
report. This PAR-LIM-only adapter calls no live
collector, provider, network, or Gemini service. It performs no
filesystem, package, Anchor, shared Replay execution, semantic, Root, or
Corridor rerun and recollects neither Ledger nor Crypto evidence. It creates
no authority, permission, action, receipt, FinalOutput, or effect. This is not
an arbitrary Airline integration or production certification. PASS is
derived, never caller supplied.
"""

from collections.abc import Mapping as _Mapping
from dataclasses import dataclass as _dataclass
import re as _re
import unicodedata as _unicodedata

from hedgehog.domains.airline.crypto_artifact_seal_collector_v01 import (
    AirlineCryptoArtifactSealCollectionResultV01 as _AirlineCryptoArtifactSealCollectionResultV01,
    validate_airline_crypto_artifact_seal_collection_result_v01 as _validate_crypto_collection,
)
from hedgehog.domains.airline.crypto_artifact_seal_v01 import (
    AirlineCryptoArtifactSealManifestCoreV01 as _AirlineCryptoArtifactSealManifestCoreV01,
)
from hedgehog.domains.airline.kernel_adapter_v01 import (
    AirlineKernelAdapterResultV01 as _AirlineKernelAdapterResultV01,
    validate_airline_kernel_adapter_result_v01 as _validate_kernel_adapter,
)
from hedgehog.domains.airline.sealed_trace_replay_v01 import (
    AirlineSealedTraceReplayInputV01 as _AirlineSealedTraceReplayInputV01,
    AirlineSealedTraceReplayReportV01 as _AirlineSealedTraceReplayReportV01,
    AirlineSealedTraceReplayTimelineRowV01 as _AirlineSealedTraceReplayTimelineRowV01,
    validate_airline_sealed_trace_replay_input_v01 as _validate_replay_input,
    validate_airline_sealed_trace_replay_report_v01 as _validate_replay_report,
)
from hedgehog.domains.airline.transaction_artifact_ledger_collector_v01 import (
    AirlineTransactionArtifactLedgerSourceBundleV01 as _AirlineTransactionArtifactLedgerSourceBundleV01,
    validate_airline_transaction_artifact_ledger_source_bundle_v01 as _validate_ledger_source_bundle,
)
from hedgehog.domains.airline.transaction_artifact_ledger_v01 import (
    AIRLINE_ROOT_ID as _AIRLINE_ROOT_ID,
    ARTIFACT_AIRLINE_BSEP_PROJECTION as _ARTIFACT_AIRLINE_BSEP_PROJECTION,
    ARTIFACT_AIRLINE_ROOT_FINAL as _ARTIFACT_AIRLINE_ROOT_FINAL,
    ARTIFACT_AIRLINE_ROOT_OFFER_RESOLUTION as _ARTIFACT_AIRLINE_ROOT_OFFER_RESOLUTION,
    ARTIFACT_BANK_BSEP_PROJECTION as _ARTIFACT_BANK_BSEP_PROJECTION,
    ARTIFACT_BANK_ROOT_FINAL as _ARTIFACT_BANK_ROOT_FINAL,
    ARTIFACT_CLIENT_BSEP_PROJECTION as _ARTIFACT_CLIENT_BSEP_PROJECTION,
    ARTIFACT_CLIENT_ROOT_FINAL as _ARTIFACT_CLIENT_ROOT_FINAL,
    ARTIFACT_CLIENT_ROOT_SELECTION_DECISION as _ARTIFACT_CLIENT_ROOT_SELECTION_DECISION,
    ARTIFACT_CROSS_ROOT_BSEP_PROJECTION as _ARTIFACT_CROSS_ROOT_BSEP_PROJECTION,
    ARTIFACT_MOCK_PURCHASE_RECEIPT as _ARTIFACT_MOCK_PURCHASE_RECEIPT,
    ARTIFACT_MOCK_TICKET_RECEIPT as _ARTIFACT_MOCK_TICKET_RECEIPT,
    ARTIFACT_AIRLINE_OFFER_HOLD_RECEIPT as _ARTIFACT_AIRLINE_OFFER_HOLD_RECEIPT,
    BANK_ROOT_ID as _BANK_ROOT_ID,
    CLIENT_ROOT_ID as _CLIENT_ROOT_ID,
    AirlineTransactionArtifactLedgerEntryV01 as _AirlineTransactionArtifactLedgerEntryV01,
    AirlineTransactionArtifactLedgerV01 as _AirlineTransactionArtifactLedgerV01,
)
from hedgehog.evidence.sealed_evidence_profile_v01 import (
    DomainEvidenceProjectionV01 as _DomainEvidenceProjectionV01,
    build_domain_evidence_projection_v01 as _build_domain_evidence_projection_v01,
    build_domain_execution_identity_v01 as _build_domain_execution_identity_v01,
    build_evidence_artifact_record_v01 as _build_evidence_artifact_record_v01,
    build_live_attempt_identity_v01 as _build_live_attempt_identity_v01,
    build_programme_evidence_identity_v01 as _build_programme_evidence_identity_v01,
    build_safe_source_record_v01 as _build_safe_source_record_v01,
    domain_evidence_projection_to_plain_dict_v01 as _domain_projection_plain,
    validate_domain_evidence_projection_v01 as _validate_domain_projection,
)
from hedgehog.kernel.abi_v01 import (
    CausalConsumptionRefV01 as _CausalConsumptionRefV01,
)
from hedgehog.kernel.integrity_replay_v01 import (
    CanonicalArtifactRefV01 as _CanonicalArtifactRefV01,
    canonical_json_bytes_v01 as _canonical_json_bytes_v01,
    domain_separated_sha256_hex_v01 as _domain_separated_sha256_hex_v01,
)


MODULE_ID = "airline_sealed_evidence_package_adapter_v01"
ADAPTER_VERSION = "v0.1"

STATUS_PASS = "PASS"
STATUS_FAIL_CLOSED = "FAIL_CLOSED"
ADAPTER_STATUSES = (STATUS_PASS, STATUS_FAIL_CLOSED)

_PROGRAMME_ID = "two_domain_all_real_sealed_evidence_program_v01"
_PROGRAMME_VERSION = "v0.1"
_DOMAIN_ID = "airline"
_PROVIDER_MODE = "real_provider"
_SAFE_EXECUTION_DOMAIN = "hedgehog.airline.safe_execution_projection.v01"
_ADAPTER_RESULT_DOMAIN = "hedgehog.airline.sealed_evidence_adapter.v01"
_SAFE_COMPONENT_DOMAIN = "hedgehog.airline.safe_component.v01"
_LOWER_HEX = _re.compile(r"^[0-9a-f]{7,40}$")
_LOWER_HEX_64 = _re.compile(r"^[0-9a-f]{64}$")
_WINDOWS_DRIVE = _re.compile(r"^[A-Za-z]:")

_EXPECTED_ACTOR_IDS = (
    "tri_party_airline_orchestrator_llm",
    "tri_party_airline_semantic_architect_llm",
    "client_purchase_intent_reviewer_llm",
    "client_profile_privacy_reviewer_llm",
    "airline_offer_policy_reviewer_llm",
    "airline_fare_rules_vertical_cell_llm",
    "airline_seat_baggage_vertical_cell_llm",
    "airline_ticketing_policy_reviewer_llm",
    "bank_payment_policy_reviewer_llm",
    "bank_idempotency_risk_vertical_cell_llm",
    "bank_payment_status_explainer_llm",
    "tri_party_evidence_consistency_reviewer_llm",
)
_EXPECTED_BSEP_IDS = (
    "client_bsep_projection",
    "airline_bsep_projection",
    "bank_bsep_projection",
    "cross_root_bsep_projection",
)
_EXPECTED_BSEP_REFS = (
    "bsep_projection:client:001",
    "bsep_projection:airline_offer_selection:001",
    "bsep_projection:bank:001",
    "bsep_projection:cross_root:001",
)
_EXPECTED_ROOT_ROLES = ("ClientRoot", "AirlineRoot", "BankRoot")
_EXPECTED_ROOT_OWNER_IDS = (_CLIENT_ROOT_ID, _AIRLINE_ROOT_ID, _BANK_ROOT_ID)
_EXPECTED_GEOMETRY = (6, 19, 19, 29, 3, 9, 11, 19)

_REPORT_KEYS = frozenset(
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
    )
)
_LIMITATIONS = (
    "limitation:par_lim_only_airline_geometry",
    "limitation:frozen_accepted_airline_evidence",
    "limitation:mock_corridor",
    "limitation:no_new_all_real_run_during_r1",
    "limitation:no_real_ticket_booking_payment_bank_gds_connector_action",
    "limitation:no_arbitrary_airline_integration",
    "limitation:no_production_signer",
    "limitation:no_signer_identity_verification",
    "limitation:no_root_attestation",
    "limitation:no_pki",
    "limitation:no_production_certification",
    "limitation:owner_built_safe_normalization_not_raw_provider_report",
)


@_dataclass(frozen=True, slots=True)
class AirlineSafeExecutionProjectionV01:
    safe_execution_id: str
    safe_execution_version: str
    execution_head: str
    run_id: str
    report_id: str
    source_task_id: str
    transaction_id: str
    selected_offer_id: str
    provider_mode: str
    model_id: str
    source_final_status: str
    actor_ids: tuple[str, ...]
    actor_safe_projection_hashes: tuple[str, ...]
    actor_validation_statuses: tuple[str, ...]
    bsep_packet_id: str
    bsep_safe_hash: str
    bsep_projection_refs: tuple[str, ...]
    bsep_projection_hashes: tuple[str, ...]
    client_root_final_id: str
    client_root_final_hash: str
    airline_root_final_id: str
    airline_root_final_hash: str
    bank_root_final_id: str
    bank_root_final_hash: str
    corridor_report_id: str
    corridor_report_hash: str
    receipt_ids: tuple[str, ...]
    receipt_safe_hashes: tuple[str, ...]
    provider_call_count: int
    network_call_count: int
    gemini_call_count: int
    raw_prompt_included: bool
    raw_provider_response_included: bool
    secret_scan_passed: bool
    real_world_effects_count: int
    validation_errors: tuple[str, ...]
    status: str

    def __post_init__(self) -> None:
        tuple_values = (
            self.actor_ids,
            self.actor_safe_projection_hashes,
            self.actor_validation_statuses,
            self.bsep_projection_refs,
            self.bsep_projection_hashes,
            self.receipt_ids,
            self.receipt_safe_hashes,
            self.validation_errors,
        )
        if any(type(value) is not tuple for value in tuple_values):
            raise ValueError("airline_safe_execution_projection_invalid")


@_dataclass(frozen=True, slots=True)
class AirlineSealedEvidencePackageAdapterResultV01:
    adapter_result_id: str
    adapter_version: str
    safe_execution_id: str
    source_bundle_id: str
    transaction_id: str
    selected_offer_id: str
    ledger_id: str
    crypto_manifest_core_hash: str
    kernel_manifest_hash: str
    source_package_ref: str
    source_replay_id: str
    kernel_adapter_id: str
    domain_projection: _DomainEvidenceProjectionV01
    source_record_count: int
    artifact_record_count: int
    kernel_artifact_ref_count: int
    causal_ref_count: int
    root_final_count: int
    source_file_count: int
    critical_file_count: int
    replay_row_count: int
    adapter_provider_call_count: int
    adapter_network_call_count: int
    adapter_gemini_call_count: int
    created_authority_count: int
    created_permission_count: int
    action_created_count: int
    receipt_created_count: int
    final_output_created_count: int
    real_world_effects_count: int
    validation_errors: tuple[str, ...]
    status: str

    def __post_init__(self) -> None:
        if type(self.validation_errors) is not tuple:
            raise ValueError("airline_sealed_evidence_adapter_invalid")


def build_airline_safe_execution_projection_v01(
    source_report: _Mapping[str, object],
) -> AirlineSafeExecutionProjectionV01:
    try:
        source = _consume_mapping(source_report, _REPORT_KEYS)
        actors = _consume_sequence_of_mappings(
            source["actors"],
            keys=frozenset(("actor_id", "safe_projection", "validation_status")),
            expected_count=12,
        )
        actor_ids = tuple(_required_text(item["actor_id"]) for item in actors)
        if actor_ids != _EXPECTED_ACTOR_IDS:
            raise ValueError("airline_safe_execution_actor_geometry_invalid")
        actor_hashes = tuple(
            _safe_component_hash(
                "actor",
                actor_id,
                item["safe_projection"],
            )
            for actor_id, item in zip(actor_ids, actors, strict=True)
        )
        actor_statuses = tuple(
            _required_status(item["validation_status"]) for item in actors
        )

        bsep = _consume_mapping(
            source["bsep"],
            frozenset(("packet_id", "safe_projection", "projections")),
        )
        bsep_packet_id = _required_text(bsep["packet_id"])
        bsep_hash = _safe_component_hash(
            "bsep_packet",
            bsep_packet_id,
            bsep["safe_projection"],
        )
        bsep_projections = _consume_sequence_of_mappings(
            bsep["projections"],
            keys=frozenset(("projection_ref", "safe_projection")),
            expected_count=4,
        )
        bsep_refs = tuple(
            _required_text(item["projection_ref"]) for item in bsep_projections
        )
        if bsep_refs != _EXPECTED_BSEP_REFS:
            raise ValueError("airline_safe_execution_bsep_geometry_invalid")
        bsep_hashes = tuple(
            _safe_component_hash("bsep_projection", ref, item["safe_projection"])
            for ref, item in zip(bsep_refs, bsep_projections, strict=True)
        )

        roots = _consume_sequence_of_mappings(
            source["root_finals"],
            keys=frozenset(("root_role", "final_id", "safe_projection")),
            expected_count=3,
        )
        root_roles = tuple(_required_text(item["root_role"]) for item in roots)
        if root_roles != _EXPECTED_ROOT_ROLES:
            raise ValueError("airline_safe_execution_root_geometry_invalid")
        root_ids = tuple(_required_text(item["final_id"]) for item in roots)
        root_hashes = tuple(
            _safe_component_hash("root_final", final_id, item["safe_projection"])
            for final_id, item in zip(root_ids, roots, strict=True)
        )

        corridor = _consume_mapping(
            source["corridor"],
            frozenset(("report_id", "safe_projection")),
        )
        corridor_id = _required_text(corridor["report_id"])
        corridor_hash = _safe_component_hash(
            "corridor",
            corridor_id,
            corridor["safe_projection"],
        )
        receipts = _consume_sequence_of_mappings(
            source["receipts"],
            keys=frozenset(("receipt_id", "safe_projection")),
            expected_count=3,
        )
        receipt_ids = tuple(
            _required_text(item["receipt_id"]) for item in receipts
        )
        receipt_hashes = tuple(
            _safe_component_hash("receipt", receipt_id, item["safe_projection"])
            for receipt_id, item in zip(receipt_ids, receipts, strict=True)
        )

        counters = _consume_mapping(
            source["counters"],
            frozenset(
                (
                    "provider_call_count",
                    "network_call_count",
                    "gemini_call_count",
                )
            ),
        )
        external_counts = tuple(
            _required_nonnegative_int(counters[name])
            for name in (
                "provider_call_count",
                "network_call_count",
                "gemini_call_count",
            )
        )
        if external_counts != (12, 12, 12):
            raise ValueError("airline_safe_execution_call_geometry_invalid")
        raw_prompt = _required_bool(source["raw_prompt_included"])
        raw_response = _required_bool(source["raw_provider_response_included"])
        secret_scan = _required_bool(source["secret_scan_passed"])
        if raw_prompt or raw_response:
            raise ValueError("airline_safe_execution_raw_material_forbidden")
        if not secret_scan:
            raise ValueError("airline_safe_execution_secret_scan_required")
        validation_errors = _required_text_tuple(source["validation_errors"])
        effects = _required_nonnegative_int(source["real_world_effects_count"])
        source_final_status = _required_status(source["source_final_status"])
        provider_mode = _required_text(source["provider_mode"])

        status = (
            STATUS_PASS
            if source_final_status == STATUS_PASS
            and provider_mode == _PROVIDER_MODE
            and all(item == STATUS_PASS for item in actor_statuses)
            and not validation_errors
            and effects == 0
            else STATUS_FAIL_CLOSED
        )
        provisional = AirlineSafeExecutionProjectionV01(
            safe_execution_id="0" * 64,
            safe_execution_version=ADAPTER_VERSION,
            execution_head=_required_execution_head(source["execution_head"]),
            run_id=_required_text(source["run_id"]),
            report_id=_required_text(source["report_id"]),
            source_task_id=_required_text(source["source_task_id"]),
            transaction_id=_required_text(source["transaction_id"]),
            selected_offer_id=_required_text(source["selected_offer_id"]),
            provider_mode=provider_mode,
            model_id=_required_text(source["model_id"]),
            source_final_status=source_final_status,
            actor_ids=actor_ids,
            actor_safe_projection_hashes=actor_hashes,
            actor_validation_statuses=actor_statuses,
            bsep_packet_id=bsep_packet_id,
            bsep_safe_hash=bsep_hash,
            bsep_projection_refs=bsep_refs,
            bsep_projection_hashes=bsep_hashes,
            client_root_final_id=root_ids[0],
            client_root_final_hash=root_hashes[0],
            airline_root_final_id=root_ids[1],
            airline_root_final_hash=root_hashes[1],
            bank_root_final_id=root_ids[2],
            bank_root_final_hash=root_hashes[2],
            corridor_report_id=corridor_id,
            corridor_report_hash=corridor_hash,
            receipt_ids=receipt_ids,
            receipt_safe_hashes=receipt_hashes,
            provider_call_count=external_counts[0],
            network_call_count=external_counts[1],
            gemini_call_count=external_counts[2],
            raw_prompt_included=raw_prompt,
            raw_provider_response_included=raw_response,
            secret_scan_passed=secret_scan,
            real_world_effects_count=effects,
            validation_errors=validation_errors,
            status=status,
        )
        result = _replace_safe_execution_id(
            provisional,
            _safe_execution_identity(provisional),
        )
        errors = _safe_execution_errors(result)
        if errors:
            raise ValueError(errors[0])
        return result
    except ValueError as error:
        raise ValueError(_stable_safe_reason(error)) from None
    except Exception:
        raise ValueError("airline_safe_execution_unexpected_exception") from None


def validate_airline_safe_execution_projection_v01(
    result: object,
) -> tuple[str, ...]:
    try:
        return _safe_execution_errors(result)
    except Exception:
        return ("airline_safe_execution_unexpected_exception",)


def airline_safe_execution_projection_to_plain_dict_v01(
    result: AirlineSafeExecutionProjectionV01,
) -> dict[str, object]:
    try:
        if _safe_execution_errors(result):
            raise ValueError
        plain = _safe_execution_plain(result)
        _canonical_json_bytes_v01(plain)
        return plain
    except Exception:
        raise ValueError("airline_safe_execution_projection_invalid") from None


def build_airline_sealed_evidence_package_adapter_result_v01(
    *,
    safe_execution: AirlineSafeExecutionProjectionV01,
    ledger_source_bundle: _AirlineTransactionArtifactLedgerSourceBundleV01,
    crypto_collection_result: _AirlineCryptoArtifactSealCollectionResultV01,
    replay_input: _AirlineSealedTraceReplayInputV01,
    replay_report: _AirlineSealedTraceReplayReportV01,
    kernel_adapter_result: _AirlineKernelAdapterResultV01,
) -> AirlineSealedEvidencePackageAdapterResultV01:
    try:
        return _build_adapter_result(
            safe_execution=safe_execution,
            ledger_source_bundle=ledger_source_bundle,
            crypto_collection_result=crypto_collection_result,
            replay_input=replay_input,
            replay_report=replay_report,
            kernel_adapter_result=kernel_adapter_result,
        )
    except ValueError as error:
        raise ValueError(_stable_adapter_reason(error)) from None
    except Exception:
        raise ValueError("airline_sealed_evidence_adapter_unexpected_exception") from None


def validate_airline_sealed_evidence_package_adapter_result_v01(
    result: object,
    *,
    safe_execution: AirlineSafeExecutionProjectionV01,
    ledger_source_bundle: _AirlineTransactionArtifactLedgerSourceBundleV01,
    crypto_collection_result: _AirlineCryptoArtifactSealCollectionResultV01,
    replay_input: _AirlineSealedTraceReplayInputV01,
    replay_report: _AirlineSealedTraceReplayReportV01,
    kernel_adapter_result: _AirlineKernelAdapterResultV01,
) -> tuple[str, ...]:
    try:
        structure = list(_adapter_result_structure_errors(result))
        if type(result) is not AirlineSealedEvidencePackageAdapterResultV01:
            return tuple(structure)
        expected = _build_adapter_result(
            safe_execution=safe_execution,
            ledger_source_bundle=ledger_source_bundle,
            crypto_collection_result=crypto_collection_result,
            replay_input=replay_input,
            replay_report=replay_report,
            kernel_adapter_result=kernel_adapter_result,
        )
        if _canonical_json_bytes_v01(_adapter_result_plain(result)) != (
            _canonical_json_bytes_v01(_adapter_result_plain(expected))
        ):
            structure.append("airline_sealed_evidence_adapter_context_mismatch")
            if result.adapter_result_id != expected.adapter_result_id:
                structure.append("airline_sealed_evidence_adapter_id_mismatch")
        return _dedupe(structure)
    except ValueError as error:
        return (_stable_adapter_reason(error),)
    except Exception:
        return ("airline_sealed_evidence_adapter_unexpected_exception",)


def airline_sealed_evidence_package_adapter_result_to_plain_dict_v01(
    result: AirlineSealedEvidencePackageAdapterResultV01,
    *,
    safe_execution: AirlineSafeExecutionProjectionV01,
    ledger_source_bundle: _AirlineTransactionArtifactLedgerSourceBundleV01,
    crypto_collection_result: _AirlineCryptoArtifactSealCollectionResultV01,
    replay_input: _AirlineSealedTraceReplayInputV01,
    replay_report: _AirlineSealedTraceReplayReportV01,
    kernel_adapter_result: _AirlineKernelAdapterResultV01,
) -> dict[str, object]:
    try:
        if validate_airline_sealed_evidence_package_adapter_result_v01(
            result,
            safe_execution=safe_execution,
            ledger_source_bundle=ledger_source_bundle,
            crypto_collection_result=crypto_collection_result,
            replay_input=replay_input,
            replay_report=replay_report,
            kernel_adapter_result=kernel_adapter_result,
        ):
            raise ValueError
        plain = _adapter_result_plain(result)
        _canonical_json_bytes_v01(plain)
        return plain
    except Exception:
        raise ValueError("airline_sealed_evidence_adapter_invalid") from None


def _build_adapter_result(
    *,
    safe_execution: object,
    ledger_source_bundle: object,
    crypto_collection_result: object,
    replay_input: object,
    replay_report: object,
    kernel_adapter_result: object,
) -> AirlineSealedEvidencePackageAdapterResultV01:
    _require_context_shape(
        safe_execution=safe_execution,
        ledger_source_bundle=ledger_source_bundle,
        crypto_collection_result=crypto_collection_result,
        replay_input=replay_input,
        replay_report=replay_report,
        kernel_adapter_result=kernel_adapter_result,
    )
    ledger = replay_input.ledger_item
    manifest_core = crypto_collection_result.manifest_core
    cross_errors = _cross_contract_errors(
        safe_execution=safe_execution,
        ledger_source_bundle=ledger_source_bundle,
        crypto_collection_result=crypto_collection_result,
        replay_input=replay_input,
        replay_report=replay_report,
        kernel_adapter_result=kernel_adapter_result,
    )
    domain_projection = _build_shared_projection(
        safe_execution=safe_execution,
        ledger_source_bundle=ledger_source_bundle,
        crypto_collection_result=crypto_collection_result,
        replay_input=replay_input,
        replay_report=replay_report,
        kernel_adapter_result=kernel_adapter_result,
    )
    if _validate_domain_projection(domain_projection):
        cross_errors = _dedupe(
            (*cross_errors, "airline_sealed_evidence_shared_projection_invalid")
        )
    status = STATUS_PASS if not cross_errors else STATUS_FAIL_CLOSED
    provisional = AirlineSealedEvidencePackageAdapterResultV01(
        adapter_result_id="0" * 64,
        adapter_version=ADAPTER_VERSION,
        safe_execution_id=safe_execution.safe_execution_id,
        source_bundle_id=ledger_source_bundle.source_bundle_id,
        transaction_id=ledger.transaction_id,
        selected_offer_id=safe_execution.selected_offer_id,
        ledger_id=ledger.ledger_id,
        crypto_manifest_core_hash=crypto_collection_result.manifest_core_hash,
        kernel_manifest_hash=kernel_adapter_result.kernel_manifest.manifest_hash,
        source_package_ref=replay_input.source_package_ref,
        source_replay_id=replay_report.replay_id,
        kernel_adapter_id=kernel_adapter_result.adapter_id,
        domain_projection=domain_projection,
        source_record_count=len(domain_projection.source_records),
        artifact_record_count=len(domain_projection.artifact_records),
        kernel_artifact_ref_count=len(domain_projection.kernel_artifact_refs),
        causal_ref_count=len(domain_projection.causal_consumption_refs),
        root_final_count=ledger.root_final_count,
        source_file_count=manifest_core.source_file_count,
        critical_file_count=replay_report.critical_package_file_count,
        replay_row_count=len(replay_report.reconstructed_timeline),
        adapter_provider_call_count=0,
        adapter_network_call_count=0,
        adapter_gemini_call_count=0,
        created_authority_count=0,
        created_permission_count=0,
        action_created_count=0,
        receipt_created_count=0,
        final_output_created_count=0,
        real_world_effects_count=0,
        validation_errors=cross_errors,
        status=status,
    )
    result = _replace_adapter_result_id(
        provisional,
        _adapter_result_identity(provisional),
    )
    errors = _adapter_result_structure_errors(result)
    if errors:
        raise ValueError(errors[0])
    return result


def _require_context_shape(
    *,
    safe_execution: object,
    ledger_source_bundle: object,
    crypto_collection_result: object,
    replay_input: object,
    replay_report: object,
    kernel_adapter_result: object,
) -> None:
    if type(safe_execution) is not AirlineSafeExecutionProjectionV01:
        raise ValueError("airline_sealed_evidence_adapter_source_invalid")
    if type(ledger_source_bundle) is not _AirlineTransactionArtifactLedgerSourceBundleV01:
        raise ValueError("airline_sealed_evidence_adapter_source_invalid")
    if type(crypto_collection_result) is not _AirlineCryptoArtifactSealCollectionResultV01:
        raise ValueError("airline_sealed_evidence_adapter_crypto_invalid")
    if type(replay_input) is not _AirlineSealedTraceReplayInputV01:
        raise ValueError("airline_sealed_evidence_adapter_replay_invalid")
    if type(replay_report) is not _AirlineSealedTraceReplayReportV01:
        raise ValueError("airline_sealed_evidence_adapter_replay_invalid")
    if type(kernel_adapter_result) is not _AirlineKernelAdapterResultV01:
        raise ValueError("airline_sealed_evidence_adapter_kernel_invalid")
    try:
        if type(replay_input.ledger_item) is not _AirlineTransactionArtifactLedgerV01:
            raise ValueError
        if (
            type(replay_input.ledger_item.entries) is not tuple
            or len(replay_input.ledger_item.entries) != 19
            or any(
                type(item) is not _AirlineTransactionArtifactLedgerEntryV01
                for item in replay_input.ledger_item.entries
            )
        ):
            raise ValueError
        if type(crypto_collection_result.manifest_core) is not (
            _AirlineCryptoArtifactSealManifestCoreV01
        ):
            raise ValueError
        if (
            type(replay_report.reconstructed_timeline) is not tuple
            or len(replay_report.reconstructed_timeline) != 19
            or any(
                type(item) is not _AirlineSealedTraceReplayTimelineRowV01
                for item in replay_report.reconstructed_timeline
            )
        ):
            raise ValueError
        if (
            type(kernel_adapter_result.kernel_manifest.artifacts) is not tuple
            or len(kernel_adapter_result.kernel_manifest.artifacts) != 19
            or any(
                type(item) is not _CanonicalArtifactRefV01
                for item in kernel_adapter_result.kernel_manifest.artifacts
            )
            or type(kernel_adapter_result.causal_consumption_refs) is not tuple
            or len(kernel_adapter_result.causal_consumption_refs) != 29
            or any(
                type(item) is not _CausalConsumptionRefV01
                for item in kernel_adapter_result.causal_consumption_refs
            )
        ):
            raise ValueError
    except (AttributeError, TypeError, ValueError):
        raise ValueError("airline_sealed_evidence_adapter_source_invalid") from None


def _cross_contract_errors(
    *,
    safe_execution: AirlineSafeExecutionProjectionV01,
    ledger_source_bundle: _AirlineTransactionArtifactLedgerSourceBundleV01,
    crypto_collection_result: _AirlineCryptoArtifactSealCollectionResultV01,
    replay_input: _AirlineSealedTraceReplayInputV01,
    replay_report: _AirlineSealedTraceReplayReportV01,
    kernel_adapter_result: _AirlineKernelAdapterResultV01,
) -> tuple[str, ...]:
    errors: list[str] = []
    ledger = replay_input.ledger_item
    manifest_core = crypto_collection_result.manifest_core
    if _safe_execution_errors(safe_execution) or safe_execution.status != STATUS_PASS:
        errors.append("airline_sealed_evidence_safe_execution_invalid")
    if _validation_status(_validate_ledger_source_bundle(ledger_source_bundle)) != STATUS_PASS:
        errors.append("airline_sealed_evidence_ledger_invalid")
    if _validation_status(_validate_crypto_collection(crypto_collection_result)) != STATUS_PASS:
        errors.append("airline_sealed_evidence_crypto_invalid")
    if _validation_status(_validate_replay_input(replay_input)) != STATUS_PASS:
        errors.append("airline_sealed_evidence_replay_invalid")
    if _validation_status(_validate_replay_report(replay_report)) != STATUS_PASS:
        errors.append("airline_sealed_evidence_replay_invalid")
    if _validate_kernel_adapter(
        replay_input=replay_input,
        replay_report=replay_report,
        result=kernel_adapter_result,
    ):
        errors.append("airline_sealed_evidence_kernel_invalid")

    transaction_values = (
        safe_execution.transaction_id,
        ledger_source_bundle.transaction_id,
        ledger.transaction_id,
        crypto_collection_result.transaction_id,
        manifest_core.transaction_id,
        replay_report.transaction_id,
        kernel_adapter_result.transaction_id,
    )
    if len(set(transaction_values)) != 1:
        errors.append("airline_sealed_evidence_transaction_mismatch")
    selected_values = (
        safe_execution.selected_offer_id,
        ledger_source_bundle.offer_packet.offer_id,
        kernel_adapter_result.selected_offer_id,
        _timeline_selected_offer(replay_report.reconstructed_timeline),
    )
    if len(set(selected_values)) != 1:
        errors.append("airline_sealed_evidence_offer_mismatch")
    ledger_ids = (
        ledger.ledger_id,
        crypto_collection_result.ledger_id,
        manifest_core.ledger_id,
        replay_report.ledger_id,
    )
    if len(set(ledger_ids)) != 1:
        errors.append("airline_sealed_evidence_ledger_mismatch")
    manifest_hashes = (
        crypto_collection_result.manifest_core_hash,
        replay_input.expected_manifest_core_hash,
        replay_report.manifest_core_hash,
        replay_report.expected_manifest_core_hash,
        kernel_adapter_result.source_manifest_core_hash,
    )
    if len(set(manifest_hashes)) != 1:
        errors.append("airline_sealed_evidence_manifest_hash_mismatch")
    package_refs = (
        crypto_collection_result.source_package_ref,
        manifest_core.source_package_ref,
        replay_input.source_package_ref,
        replay_report.source_package_ref,
        kernel_adapter_result.source_package_ref,
    )
    if len(set(package_refs)) != 1:
        errors.append("airline_sealed_evidence_package_ref_mismatch")
    if replay_input.envelope.manifest_core != manifest_core:
        errors.append("airline_sealed_evidence_crypto_mismatch")
    if replay_report.replay_id != kernel_adapter_result.source_replay_id:
        errors.append("airline_sealed_evidence_replay_mismatch")

    expected_source_refs = ledger_source_bundle.expected_source_refs
    accepted_audit = replay_input.accepted_ledger_audit
    lineage_rows = (
        (
            expected_source_refs.source_run_ref,
            ledger.source_run_ref,
            accepted_audit.source_run_ref,
        ),
        (
            expected_source_refs.source_causal_report_ref,
            ledger.source_causal_report_ref,
            accepted_audit.source_causal_report_ref,
        ),
        (
            expected_source_refs.source_corridor_report_ref,
            ledger.source_corridor_report_ref,
            accepted_audit.source_corridor_report_ref,
        ),
    )
    if (
        ledger_source_bundle.source_validation_refs
        != tuple(row[0] for row in lineage_rows)
        or any(len(set(row)) != 1 for row in lineage_rows)
    ):
        errors.append("airline_sealed_evidence_source_lineage_mismatch")

    root_final_ids = (
        ledger_source_bundle.client_root_final.final_id,
        ledger_source_bundle.airline_root_final.final_id,
        ledger_source_bundle.bank_root_final.final_id,
    )
    safe_root_ids = (
        safe_execution.client_root_final_id,
        safe_execution.airline_root_final_id,
        safe_execution.bank_root_final_id,
    )
    ledger_root_ids = tuple(
        entry.artifact_id
        for entry in ledger.entries
        if entry.artifact_type
        in (
            _ARTIFACT_CLIENT_ROOT_FINAL,
            _ARTIFACT_AIRLINE_ROOT_FINAL,
            _ARTIFACT_BANK_ROOT_FINAL,
        )
    )
    if (
        safe_root_ids != root_final_ids
        or ledger_root_ids != root_final_ids
        or kernel_adapter_result.root_ids != _EXPECTED_ROOT_OWNER_IDS
    ):
        errors.append("airline_sealed_evidence_root_final_mismatch")
    source_bsep_refs = (
        ledger_source_bundle.client_bsep_projection.projection_ref,
        ledger_source_bundle.airline_bsep_projection.projection_ref,
        ledger_source_bundle.bank_bsep_projection.projection_ref,
        ledger_source_bundle.cross_root_bsep_projection.projection_ref,
    )
    source_bsep_ids = (
        ledger_source_bundle.client_bsep_projection.projection_id,
        ledger_source_bundle.airline_bsep_projection.projection_id,
        ledger_source_bundle.bank_bsep_projection.projection_id,
        ledger_source_bundle.cross_root_bsep_projection.projection_id,
    )
    source_bsep_packet_ids = {
        ledger_source_bundle.client_bsep_projection.bsep_packet_id,
        ledger_source_bundle.airline_bsep_projection.bsep_packet_id,
        ledger_source_bundle.bank_bsep_projection.bsep_packet_id,
        ledger_source_bundle.cross_root_bsep_projection.bsep_packet_id,
    }
    if (
        source_bsep_ids != _EXPECTED_BSEP_IDS
        or safe_execution.bsep_projection_refs != source_bsep_refs
        or source_bsep_packet_ids != {safe_execution.bsep_packet_id}
    ):
        errors.append("airline_sealed_evidence_bsep_mismatch")
    source_receipts = (
        ledger_source_bundle.hold_receipt.receipt_id,
        ledger_source_bundle.mock_ticket_receipt.receipt_id,
        ledger_source_bundle.mock_purchase_receipt.receipt_id,
    )
    if safe_execution.receipt_ids != source_receipts:
        errors.append("airline_sealed_evidence_receipt_mismatch")
    if safe_execution.corridor_report_id != ledger_source_bundle.corridor_report.run_id:
        errors.append("airline_sealed_evidence_corridor_mismatch")

    geometry = (
        6,
        ledger.entry_count,
        len(kernel_adapter_result.kernel_manifest.artifacts),
        len(kernel_adapter_result.causal_consumption_refs),
        ledger.root_final_count,
        manifest_core.source_file_count,
        replay_report.critical_package_file_count,
        len(replay_report.reconstructed_timeline),
    )
    if geometry != _EXPECTED_GEOMETRY:
        errors.append("airline_sealed_evidence_geometry_mismatch")
    if (
        ledger.dependency_edge_count != 29
        or replay_report.dependency_edge_count != 29
        or replay_report.source_file_count != 9
        or kernel_adapter_result.ledger_entry_count != 19
        or kernel_adapter_result.dependency_edge_count != 29
        or kernel_adapter_result.root_final_count != 3
        or kernel_adapter_result.source_file_count != 9
        or kernel_adapter_result.critical_file_count != 11
        or kernel_adapter_result.timeline_row_count != 19
    ):
        errors.append("airline_sealed_evidence_geometry_mismatch")
    ledger_artifact_ids = tuple(entry.artifact_id for entry in ledger.entries)
    kernel_artifact_ids = tuple(
        item.artifact_id for item in kernel_adapter_result.kernel_manifest.artifacts
    )
    replay_artifact_ids = tuple(
        item.artifact_id for item in replay_report.reconstructed_timeline
    )
    if (
        ledger_artifact_ids != kernel_artifact_ids
        or ledger_artifact_ids != replay_artifact_ids
    ):
        errors.append("airline_sealed_evidence_order_mismatch")
    if not _domain_zero_boundaries(
        safe_execution,
        ledger,
        crypto_collection_result,
        manifest_core,
        replay_report,
        kernel_adapter_result,
    ):
        errors.append("airline_sealed_evidence_effect_boundary_invalid")
    return _dedupe(errors)


def _build_shared_projection(
    *,
    safe_execution: AirlineSafeExecutionProjectionV01,
    ledger_source_bundle: _AirlineTransactionArtifactLedgerSourceBundleV01,
    crypto_collection_result: _AirlineCryptoArtifactSealCollectionResultV01,
    replay_input: _AirlineSealedTraceReplayInputV01,
    replay_report: _AirlineSealedTraceReplayReportV01,
    kernel_adapter_result: _AirlineKernelAdapterResultV01,
) -> _DomainEvidenceProjectionV01:
    ledger = replay_input.ledger_item
    programme = _build_programme_evidence_identity_v01(
        programme_id=_PROGRAMME_ID,
        programme_version=_PROGRAMME_VERSION,
    )
    domain_identity = _build_domain_execution_identity_v01(
        programme_identity=programme,
        domain_id=_DOMAIN_ID,
        execution_head=safe_execution.execution_head,
        source_task_id=safe_execution.source_task_id,
        run_id=safe_execution.run_id,
        report_id=safe_execution.report_id,
    )
    attempt = _build_live_attempt_identity_v01(
        programme_identity=programme,
        domain_execution_identity=domain_identity,
        attempt_number=1,
        package_id=f"airline_sealed_evidence:{safe_execution.transaction_id}",
        logical_package_ref=replay_input.source_package_ref,
        output_directory_ref=f"airline/{safe_execution.run_id}/sealed_evidence",
        provider_mode=_PROVIDER_MODE,
        model_id=safe_execution.model_id,
        expected_actor_count=12,
        provider_call_budget=12,
    )
    source_records = _build_source_records(
        safe_execution=safe_execution,
        ledger_source_bundle=ledger_source_bundle,
        crypto_collection_result=crypto_collection_result,
        replay_input=replay_input,
        replay_report=replay_report,
        kernel_adapter_result=kernel_adapter_result,
    )
    artifact_records = tuple(
        _build_shared_artifact(entry, source_records)
        for entry in ledger.entries
    )
    return _build_domain_evidence_projection_v01(
        programme_identity=programme,
        domain_execution_identity=domain_identity,
        attempt_identity=attempt,
        source_records=source_records,
        artifact_records=artifact_records,
        kernel_artifact_refs=tuple(
            item for item in kernel_adapter_result.kernel_manifest.artifacts
        ),
        causal_consumption_refs=tuple(
            item for item in kernel_adapter_result.causal_consumption_refs
        ),
        evidence_refs=(
            safe_execution.safe_execution_id,
            ledger_source_bundle.source_bundle_id,
            ledger.ledger_id,
            crypto_collection_result.manifest_core_hash,
            replay_report.replay_id,
            kernel_adapter_result.adapter_id,
        ),
        limitation_refs=_LIMITATIONS,
    )


def _build_source_records(
    *,
    safe_execution: AirlineSafeExecutionProjectionV01,
    ledger_source_bundle: _AirlineTransactionArtifactLedgerSourceBundleV01,
    crypto_collection_result: _AirlineCryptoArtifactSealCollectionResultV01,
    replay_input: _AirlineSealedTraceReplayInputV01,
    replay_report: _AirlineSealedTraceReplayReportV01,
    kernel_adapter_result: _AirlineKernelAdapterResultV01,
) -> tuple[object, ...]:
    common = {
        "media_type": "application/json",
        "contains_raw_prompt": False,
        "contains_raw_provider_response": False,
        "secret_scan_passed": True,
        "real_world_effects_count": 0,
    }
    records = (
        _build_safe_source_record_v01(
            source_id=f"airline:live:{safe_execution.run_id}",
            source_type="airline_live_execution_safe_projection",
            evidence_class="EXECUTED_LIVE_RUNTIME",
            canonical_projection=_safe_execution_plain(safe_execution),
            trace_refs=(safe_execution.run_id, safe_execution.report_id),
            observed_provider_call_count=12,
            observed_network_call_count=12,
            observed_gemini_call_count=12,
            **common,
        ),
        _build_safe_source_record_v01(
            source_id=f"airline:bsep:{safe_execution.bsep_packet_id}",
            source_type="airline_bsep_safe_projection",
            evidence_class="LIVE_PROVIDER_SAFE_PROJECTION",
            canonical_projection={
                "packet_id": safe_execution.bsep_packet_id,
                "packet_hash": safe_execution.bsep_safe_hash,
                "projection_ids": [
                    ledger_source_bundle.client_bsep_projection.projection_id,
                    ledger_source_bundle.airline_bsep_projection.projection_id,
                    ledger_source_bundle.bank_bsep_projection.projection_id,
                    ledger_source_bundle.cross_root_bsep_projection.projection_id,
                ],
                "projection_refs": list(safe_execution.bsep_projection_refs),
                "projection_hashes": list(safe_execution.bsep_projection_hashes),
            },
            trace_refs=(safe_execution.bsep_packet_id,),
            observed_provider_call_count=0,
            observed_network_call_count=0,
            observed_gemini_call_count=0,
            **common,
        ),
        _build_safe_source_record_v01(
            source_id=f"airline:roots:{safe_execution.transaction_id}",
            source_type="airline_three_root_final_evidence",
            evidence_class="ROOT_DECISION_EVIDENCE",
            canonical_projection={
                "final_ids": [
                    safe_execution.client_root_final_id,
                    safe_execution.airline_root_final_id,
                    safe_execution.bank_root_final_id,
                ],
                "final_hashes": [
                    safe_execution.client_root_final_hash,
                    safe_execution.airline_root_final_hash,
                    safe_execution.bank_root_final_hash,
                ],
            },
            trace_refs=(safe_execution.transaction_id,),
            observed_provider_call_count=0,
            observed_network_call_count=0,
            observed_gemini_call_count=0,
            **common,
        ),
        _build_safe_source_record_v01(
            source_id=f"airline:corridor:{safe_execution.corridor_report_id}",
            source_type="airline_corridor_and_receipt_evidence",
            evidence_class="CORRIDOR_EVIDENCE",
            canonical_projection={
                "corridor_report_id": safe_execution.corridor_report_id,
                "corridor_report_hash": safe_execution.corridor_report_hash,
                "receipt_ids": list(safe_execution.receipt_ids),
                "receipt_hashes": list(safe_execution.receipt_safe_hashes),
            },
            trace_refs=(safe_execution.corridor_report_id,),
            observed_provider_call_count=0,
            observed_network_call_count=0,
            observed_gemini_call_count=0,
            **common,
        ),
        _build_safe_source_record_v01(
            source_id=f"airline:ledger_crypto:{replay_input.ledger_item.ledger_id}",
            source_type="airline_ledger_and_crypto_evidence",
            evidence_class="CRYPTOGRAPHIC_INTEGRITY",
            canonical_projection={
                "ledger_id": replay_input.ledger_item.ledger_id,
                "ledger_entry_count": replay_input.ledger_item.entry_count,
                "dependency_edge_count": replay_input.ledger_item.dependency_edge_count,
                "manifest_core_hash": crypto_collection_result.manifest_core_hash,
                "kernel_manifest_hash": (
                    kernel_adapter_result.kernel_manifest.manifest_hash
                ),
                "source_package_ref": replay_input.source_package_ref,
            },
            trace_refs=(
                replay_input.ledger_item.ledger_id,
                crypto_collection_result.manifest_core_hash,
                kernel_adapter_result.kernel_manifest.manifest_hash,
            ),
            observed_provider_call_count=0,
            observed_network_call_count=0,
            observed_gemini_call_count=0,
            **common,
        ),
        _build_safe_source_record_v01(
            source_id=f"airline:replay_kernel:{replay_report.replay_id}",
            source_type="airline_replay_and_gate1_kernel_evidence",
            evidence_class="REPLAY_EVIDENCE",
            canonical_projection={
                "replay_id": replay_report.replay_id,
                "replay_row_count": len(replay_report.reconstructed_timeline),
                "kernel_adapter_id": kernel_adapter_result.adapter_id,
                "kernel_manifest_hash": (
                    kernel_adapter_result.kernel_manifest.manifest_hash
                ),
                "kernel_artifact_ref_count": len(
                    kernel_adapter_result.kernel_manifest.artifacts
                ),
                "causal_ref_count": len(
                    kernel_adapter_result.causal_consumption_refs
                ),
            },
            trace_refs=(replay_report.replay_id, kernel_adapter_result.adapter_id),
            observed_provider_call_count=0,
            observed_network_call_count=0,
            observed_gemini_call_count=0,
            **common,
        ),
    )
    return records


def _build_shared_artifact(entry: object, source_records: tuple[object, ...]) -> object:
    source_index, evidence_class = _artifact_source_and_class(entry.artifact_type)
    source_record = source_records[source_index]
    return _build_evidence_artifact_record_v01(
        artifact_id=entry.artifact_id,
        artifact_type=entry.artifact_type,
        evidence_class=evidence_class,
        source_record_ids=(source_record.source_record_id,),
        canonical_projection={
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
            "canonical_hash_input": _safe_json_copy(entry.canonical_hash_input),
        },
        authority_class=entry.authority_class,
        owner_root_id=entry.root_owner,
        trace_refs=(entry.artifact_id, entry.transaction_id),
        created_authority_count=0,
        created_permission_count=0,
        real_world_effects_count=entry.real_world_effects_count,
    )


def _artifact_source_and_class(artifact_type: str) -> tuple[int, str]:
    if artifact_type in (
        _ARTIFACT_CLIENT_BSEP_PROJECTION,
        _ARTIFACT_AIRLINE_BSEP_PROJECTION,
        _ARTIFACT_BANK_BSEP_PROJECTION,
        _ARTIFACT_CROSS_ROOT_BSEP_PROJECTION,
    ):
        return 1, "LIVE_PROVIDER_SAFE_PROJECTION"
    if artifact_type in (
        _ARTIFACT_CLIENT_ROOT_SELECTION_DECISION,
        _ARTIFACT_AIRLINE_ROOT_OFFER_RESOLUTION,
        _ARTIFACT_CLIENT_ROOT_FINAL,
        _ARTIFACT_AIRLINE_ROOT_FINAL,
        _ARTIFACT_BANK_ROOT_FINAL,
    ):
        return 2, "ROOT_DECISION_EVIDENCE"
    if artifact_type in (
        _ARTIFACT_AIRLINE_OFFER_HOLD_RECEIPT,
        _ARTIFACT_MOCK_TICKET_RECEIPT,
        _ARTIFACT_MOCK_PURCHASE_RECEIPT,
    ):
        return 3, "CORRIDOR_EVIDENCE"
    return 3, "EXECUTED_DETERMINISTIC_RUNTIME"


def _safe_execution_errors(result: object) -> tuple[str, ...]:
    if type(result) is not AirlineSafeExecutionProjectionV01:
        return ("airline_safe_execution_projection_invalid",)
    errors: list[str] = []
    text_values = (
        result.run_id,
        result.report_id,
        result.source_task_id,
        result.transaction_id,
        result.selected_offer_id,
        result.provider_mode,
        result.model_id,
        result.bsep_packet_id,
        result.client_root_final_id,
        result.airline_root_final_id,
        result.bank_root_final_id,
        result.corridor_report_id,
    )
    hash_values = (
        result.safe_execution_id,
        *result.actor_safe_projection_hashes,
        result.bsep_safe_hash,
        *result.bsep_projection_hashes,
        result.client_root_final_hash,
        result.airline_root_final_hash,
        result.bank_root_final_hash,
        result.corridor_report_hash,
        *result.receipt_safe_hashes,
    )
    if (
        result.safe_execution_version != ADAPTER_VERSION
        or not _valid_execution_head(result.execution_head)
        or any(not _valid_text(item) for item in text_values)
        or any(not _valid_sha256(item) for item in hash_values)
        or result.actor_ids != _EXPECTED_ACTOR_IDS
        or len(result.actor_safe_projection_hashes) != 12
        or len(result.actor_validation_statuses) != 12
        or any(item not in ADAPTER_STATUSES for item in result.actor_validation_statuses)
        or result.bsep_projection_refs != _EXPECTED_BSEP_REFS
        or len(result.bsep_projection_hashes) != 4
        or len(result.receipt_ids) != 3
        or len(result.receipt_safe_hashes) != 3
        or any(not _valid_text(item) for item in result.receipt_ids)
        or type(result.validation_errors) is not tuple
        or any(not _valid_text(item) for item in result.validation_errors)
        or result.source_final_status not in ADAPTER_STATUSES
        or result.status not in ADAPTER_STATUSES
    ):
        errors.append("airline_safe_execution_projection_invalid")
    counts = (
        result.provider_call_count,
        result.network_call_count,
        result.gemini_call_count,
    )
    if any(not _nonnegative_int(item) for item in counts) or counts != (12, 12, 12):
        errors.append("airline_safe_execution_call_geometry_invalid")
    bools = (
        result.raw_prompt_included,
        result.raw_provider_response_included,
        result.secret_scan_passed,
    )
    if any(type(item) is not bool for item in bools):
        errors.append("airline_safe_execution_projection_invalid")
    if result.raw_prompt_included is not False or result.raw_provider_response_included is not False:
        errors.append("airline_safe_execution_raw_material_forbidden")
    if result.secret_scan_passed is not True:
        errors.append("airline_safe_execution_secret_scan_required")
    if not _nonnegative_int(result.real_world_effects_count):
        errors.append("airline_safe_execution_projection_invalid")
    expected_status = (
        STATUS_PASS
        if result.source_final_status == STATUS_PASS
        and result.provider_mode == _PROVIDER_MODE
        and all(item == STATUS_PASS for item in result.actor_validation_statuses)
        and not result.validation_errors
        and result.real_world_effects_count == 0
        else STATUS_FAIL_CLOSED
    )
    if result.status != expected_status:
        errors.append("airline_safe_execution_status_mismatch")
    try:
        if result.safe_execution_id != _safe_execution_identity(result):
            errors.append("airline_safe_execution_id_mismatch")
    except Exception:
        errors.append("airline_safe_execution_projection_invalid")
    return _dedupe(errors)


def _adapter_result_structure_errors(result: object) -> tuple[str, ...]:
    if type(result) is not AirlineSealedEvidencePackageAdapterResultV01:
        return ("airline_sealed_evidence_adapter_invalid",)
    errors: list[str] = []
    identity_values = (
        result.adapter_result_id,
        result.safe_execution_id,
        result.crypto_manifest_core_hash,
        result.kernel_manifest_hash,
    )
    text_values = (
        result.source_bundle_id,
        result.transaction_id,
        result.selected_offer_id,
        result.ledger_id,
        result.source_package_ref,
        result.source_replay_id,
        result.kernel_adapter_id,
    )
    counts = (
        result.source_record_count,
        result.artifact_record_count,
        result.kernel_artifact_ref_count,
        result.causal_ref_count,
        result.root_final_count,
        result.source_file_count,
        result.critical_file_count,
        result.replay_row_count,
        result.adapter_provider_call_count,
        result.adapter_network_call_count,
        result.adapter_gemini_call_count,
        result.created_authority_count,
        result.created_permission_count,
        result.action_created_count,
        result.receipt_created_count,
        result.final_output_created_count,
        result.real_world_effects_count,
    )
    if (
        result.adapter_version != ADAPTER_VERSION
        or any(not _valid_sha256(item) for item in identity_values)
        or any(not _valid_text(item) for item in text_values)
        or any(not _nonnegative_int(item) for item in counts)
        or type(result.validation_errors) is not tuple
        or any(not _valid_text(item) for item in result.validation_errors)
        or result.status not in ADAPTER_STATUSES
        or type(result.domain_projection) is not _DomainEvidenceProjectionV01
        or _validate_domain_projection(result.domain_projection)
    ):
        errors.append("airline_sealed_evidence_adapter_invalid")
    if (
        result.source_record_count,
        result.artifact_record_count,
        result.kernel_artifact_ref_count,
        result.causal_ref_count,
        result.root_final_count,
        result.source_file_count,
        result.critical_file_count,
        result.replay_row_count,
    ) != _EXPECTED_GEOMETRY:
        errors.append("airline_sealed_evidence_adapter_geometry_mismatch")
    zero_counts = counts[8:]
    if any(not _nonnegative_int(item) for item in zero_counts) or any(zero_counts):
        errors.append("airline_sealed_evidence_adapter_zero_boundary_invalid")
    expected_status = STATUS_PASS if not result.validation_errors else STATUS_FAIL_CLOSED
    if result.status != expected_status:
        errors.append("airline_sealed_evidence_adapter_status_mismatch")
    try:
        if result.adapter_result_id != _adapter_result_identity(result):
            errors.append("airline_sealed_evidence_adapter_id_mismatch")
    except Exception:
        errors.append("airline_sealed_evidence_adapter_invalid")
    return _dedupe(errors)


def _domain_zero_boundaries(*values: object) -> bool:
    safe, ledger, crypto, manifest, replay, kernel = values
    try:
        return bool(
            safe.real_world_effects_count == 0
            and ledger.ledger_created_authority_count == 0
            and ledger.ledger_created_permission_count == 0
            and ledger.ledger_created_action_count == 0
            and ledger.real_world_effects_count == 0
            and crypto.provider_call_count == 0
            and crypto.network_call_count == 0
            and crypto.gemini_call_count == 0
            and crypto.collector_created_authority_count == 0
            and crypto.collector_created_permission_count == 0
            and crypto.collector_created_action_count == 0
            and crypto.real_world_effects_count == 0
            and manifest.seal_created_authority_count == 0
            and manifest.seal_created_permission_count == 0
            and manifest.seal_created_action_count == 0
            and manifest.real_world_effects_count == 0
            and replay.transaction_rerun_count == 0
            and replay.semantic_rerun_count == 0
            and replay.corridor_rerun_count == 0
            and replay.ledger_recollection_count == 0
            and replay.crypto_collection_count == 0
            and replay.provider_call_count == 0
            and replay.network_call_count == 0
            and replay.gemini_call_count == 0
            and replay.replay_created_authority_count == 0
            and replay.replay_created_permission_count == 0
            and replay.replay_created_action_count == 0
            and replay.replay_created_receipt_count == 0
            and replay.replay_created_final_output_count == 0
            and replay.real_world_effects_count == 0
            and kernel.provider_call_count == 0
            and kernel.network_call_count == 0
            and kernel.gemini_call_count == 0
            and kernel.real_world_effects_count == 0
        )
    except Exception:
        return False


def _timeline_selected_offer(rows: tuple[object, ...]) -> str:
    values = tuple(
        dict.fromkeys(
            row.selected_offer_id
            for row in rows
            if row.selected_offer_id is not None
        )
    )
    return values[0] if len(values) == 1 and _valid_text(values[0]) else ""


def _validation_status(report: object) -> str:
    value = getattr(report, "validation_status", "")
    return value if type(value) is str else ""


def _consume_mapping(value: object, keys: frozenset[str]) -> dict[str, object]:
    if not isinstance(value, _Mapping):
        raise ValueError("airline_safe_execution_projection_invalid")
    copied = dict(value)
    if frozenset(copied) != keys:
        raise ValueError("airline_safe_execution_projection_invalid")
    return copied


def _consume_sequence_of_mappings(
    value: object,
    *,
    keys: frozenset[str],
    expected_count: int,
) -> tuple[dict[str, object], ...]:
    if type(value) not in (tuple, list) or len(value) != expected_count:
        raise ValueError("airline_safe_execution_projection_invalid")
    return tuple(_consume_mapping(item, keys) for item in value)


def _safe_component_hash(kind: str, identity: str, projection: object) -> str:
    safe_projection = _safe_json_copy(projection)
    if _contains_forbidden_safe_material(safe_projection):
        raise ValueError("airline_safe_execution_raw_material_forbidden")
    return _domain_separated_sha256_hex_v01(
        domain=_SAFE_COMPONENT_DOMAIN,
        payload=_canonical_json_bytes_v01(
            {"kind": kind, "identity": identity, "safe_projection": safe_projection}
        ),
    )


def _safe_json_copy(value: object) -> object:
    if value is None or type(value) in (str, int, float, bool):
        _canonical_json_bytes_v01(value)
        return value
    if isinstance(value, _Mapping):
        copied: dict[str, object] = {}
        for key, item in value.items():
            if type(key) is not str:
                raise ValueError("airline_safe_execution_projection_invalid")
            copied[key] = _safe_json_copy(item)
        _canonical_json_bytes_v01(copied)
        return copied
    if type(value) in (tuple, list):
        copied_list = [_safe_json_copy(item) for item in value]
        _canonical_json_bytes_v01(copied_list)
        return copied_list
    raise ValueError("airline_safe_execution_projection_invalid")


def _contains_forbidden_safe_material(value: object) -> bool:
    tokens = (
        "raw_prompt",
        "prompt_text",
        "raw_response",
        "provider_response",
        "api_key",
        "private_key",
        "credential",
        "secret_value",
    )
    if isinstance(value, dict):
        return any(
            any(token in key.casefold() for token in tokens)
            or _contains_forbidden_safe_material(item)
            for key, item in value.items()
        )
    if isinstance(value, list):
        return any(_contains_forbidden_safe_material(item) for item in value)
    return False


def _safe_execution_plain(
    result: AirlineSafeExecutionProjectionV01,
    *,
    include_id: bool = True,
) -> dict[str, object]:
    plain: dict[str, object] = {}
    if include_id:
        plain["safe_execution_id"] = result.safe_execution_id
    plain.update(
        {
            "safe_execution_version": result.safe_execution_version,
            "execution_head": result.execution_head,
            "run_id": result.run_id,
            "report_id": result.report_id,
            "source_task_id": result.source_task_id,
            "transaction_id": result.transaction_id,
            "selected_offer_id": result.selected_offer_id,
            "provider_mode": result.provider_mode,
            "model_id": result.model_id,
            "source_final_status": result.source_final_status,
            "actor_ids": list(result.actor_ids),
            "actor_safe_projection_hashes": list(
                result.actor_safe_projection_hashes
            ),
            "actor_validation_statuses": list(result.actor_validation_statuses),
            "bsep_packet_id": result.bsep_packet_id,
            "bsep_safe_hash": result.bsep_safe_hash,
            "bsep_projection_refs": list(result.bsep_projection_refs),
            "bsep_projection_hashes": list(result.bsep_projection_hashes),
            "client_root_final_id": result.client_root_final_id,
            "client_root_final_hash": result.client_root_final_hash,
            "airline_root_final_id": result.airline_root_final_id,
            "airline_root_final_hash": result.airline_root_final_hash,
            "bank_root_final_id": result.bank_root_final_id,
            "bank_root_final_hash": result.bank_root_final_hash,
            "corridor_report_id": result.corridor_report_id,
            "corridor_report_hash": result.corridor_report_hash,
            "receipt_ids": list(result.receipt_ids),
            "receipt_safe_hashes": list(result.receipt_safe_hashes),
            "provider_call_count": result.provider_call_count,
            "network_call_count": result.network_call_count,
            "gemini_call_count": result.gemini_call_count,
            "raw_prompt_included": result.raw_prompt_included,
            "raw_provider_response_included": (
                result.raw_provider_response_included
            ),
            "secret_scan_passed": result.secret_scan_passed,
            "real_world_effects_count": result.real_world_effects_count,
            "validation_errors": list(result.validation_errors),
            "status": result.status,
        }
    )
    return plain


def _adapter_result_plain(
    result: AirlineSealedEvidencePackageAdapterResultV01,
    *,
    include_id: bool = True,
) -> dict[str, object]:
    plain: dict[str, object] = {}
    if include_id:
        plain["adapter_result_id"] = result.adapter_result_id
    plain.update(
        {
            "adapter_version": result.adapter_version,
            "safe_execution_id": result.safe_execution_id,
            "source_bundle_id": result.source_bundle_id,
            "transaction_id": result.transaction_id,
            "selected_offer_id": result.selected_offer_id,
            "ledger_id": result.ledger_id,
            "crypto_manifest_core_hash": result.crypto_manifest_core_hash,
            "kernel_manifest_hash": result.kernel_manifest_hash,
            "source_package_ref": result.source_package_ref,
            "source_replay_id": result.source_replay_id,
            "kernel_adapter_id": result.kernel_adapter_id,
            "domain_projection": _domain_projection_plain(result.domain_projection),
            "source_record_count": result.source_record_count,
            "artifact_record_count": result.artifact_record_count,
            "kernel_artifact_ref_count": result.kernel_artifact_ref_count,
            "causal_ref_count": result.causal_ref_count,
            "root_final_count": result.root_final_count,
            "source_file_count": result.source_file_count,
            "critical_file_count": result.critical_file_count,
            "replay_row_count": result.replay_row_count,
            "adapter_provider_call_count": result.adapter_provider_call_count,
            "adapter_network_call_count": result.adapter_network_call_count,
            "adapter_gemini_call_count": result.adapter_gemini_call_count,
            "created_authority_count": result.created_authority_count,
            "created_permission_count": result.created_permission_count,
            "action_created_count": result.action_created_count,
            "receipt_created_count": result.receipt_created_count,
            "final_output_created_count": result.final_output_created_count,
            "real_world_effects_count": result.real_world_effects_count,
            "validation_errors": list(result.validation_errors),
            "status": result.status,
        }
    )
    return plain


def _safe_execution_identity(result: AirlineSafeExecutionProjectionV01) -> str:
    return _domain_separated_sha256_hex_v01(
        domain=_SAFE_EXECUTION_DOMAIN,
        payload=_canonical_json_bytes_v01(
            _safe_execution_plain(result, include_id=False)
        ),
    )


def _adapter_result_identity(
    result: AirlineSealedEvidencePackageAdapterResultV01,
) -> str:
    return _domain_separated_sha256_hex_v01(
        domain=_ADAPTER_RESULT_DOMAIN,
        payload=_canonical_json_bytes_v01(
            _adapter_result_plain(result, include_id=False)
        ),
    )


def _replace_safe_execution_id(
    result: AirlineSafeExecutionProjectionV01,
    safe_execution_id: str,
) -> AirlineSafeExecutionProjectionV01:
    values = {name: getattr(result, name) for name in result.__slots__}
    values["safe_execution_id"] = safe_execution_id
    return AirlineSafeExecutionProjectionV01(**values)


def _replace_adapter_result_id(
    result: AirlineSealedEvidencePackageAdapterResultV01,
    adapter_result_id: str,
) -> AirlineSealedEvidencePackageAdapterResultV01:
    values = {name: getattr(result, name) for name in result.__slots__}
    values["adapter_result_id"] = adapter_result_id
    return AirlineSealedEvidencePackageAdapterResultV01(**values)


def _required_text(value: object) -> str:
    if not _valid_text(value):
        raise ValueError("airline_safe_execution_projection_invalid")
    return value


def _required_execution_head(value: object) -> str:
    if not _valid_execution_head(value):
        raise ValueError("airline_safe_execution_projection_invalid")
    return value


def _required_status(value: object) -> str:
    if type(value) is not str or value not in ADAPTER_STATUSES:
        raise ValueError("airline_safe_execution_projection_invalid")
    return value


def _required_bool(value: object) -> bool:
    if type(value) is not bool:
        raise ValueError("airline_safe_execution_projection_invalid")
    return value


def _required_nonnegative_int(value: object) -> int:
    if not _nonnegative_int(value):
        raise ValueError("airline_safe_execution_projection_invalid")
    return value


def _required_text_tuple(value: object) -> tuple[str, ...]:
    if type(value) is not tuple or any(not _valid_text(item) for item in value):
        raise ValueError("airline_safe_execution_projection_invalid")
    return tuple(item for item in value)


def _valid_text(value: object) -> bool:
    if type(value) is not str or not value or value != value.strip():
        return False
    if any(
        0xD800 <= ord(character) <= 0xDFFF
        or _unicodedata.category(character) in ("Cc", "Cf", "Cs", "Zl", "Zp")
        for character in value
    ):
        return False
    try:
        value.encode("utf-8", errors="strict")
    except UnicodeError:
        return False
    return True


def _valid_execution_head(value: object) -> bool:
    return type(value) is str and _LOWER_HEX.fullmatch(value) is not None


def _valid_sha256(value: object) -> bool:
    return type(value) is str and _LOWER_HEX_64.fullmatch(value) is not None


def _nonnegative_int(value: object) -> bool:
    return type(value) is int and value >= 0


def _logical_ref_valid(value: object) -> bool:
    if not _valid_text(value) or type(value) is not str:
        return False
    if (
        value.startswith("/")
        or "\\" in value
        or _WINDOWS_DRIVE.match(value) is not None
        or _unicodedata.normalize("NFC", value) != value
    ):
        return False
    return all(item not in ("", ".", "..") for item in value.split("/"))


def _dedupe(values: object) -> tuple[str, ...]:
    return tuple(dict.fromkeys(values))


def _stable_safe_reason(error: ValueError) -> str:
    allowed = (
        "airline_safe_execution_projection_invalid",
        "airline_safe_execution_actor_geometry_invalid",
        "airline_safe_execution_bsep_geometry_invalid",
        "airline_safe_execution_root_geometry_invalid",
        "airline_safe_execution_call_geometry_invalid",
        "airline_safe_execution_raw_material_forbidden",
        "airline_safe_execution_secret_scan_required",
        "airline_safe_execution_status_mismatch",
        "airline_safe_execution_id_mismatch",
    )
    if len(error.args) == 1 and error.args[0] in allowed:
        return error.args[0]
    return "airline_safe_execution_projection_invalid"


def _stable_adapter_reason(error: ValueError) -> str:
    allowed = (
        "airline_sealed_evidence_adapter_invalid",
        "airline_sealed_evidence_adapter_source_invalid",
        "airline_sealed_evidence_adapter_crypto_invalid",
        "airline_sealed_evidence_adapter_replay_invalid",
        "airline_sealed_evidence_adapter_kernel_invalid",
        "airline_sealed_evidence_adapter_geometry_mismatch",
        "airline_sealed_evidence_adapter_zero_boundary_invalid",
        "airline_sealed_evidence_adapter_status_mismatch",
        "airline_sealed_evidence_adapter_context_mismatch",
        "airline_sealed_evidence_adapter_id_mismatch",
        "airline_sealed_evidence_shared_projection_invalid",
        "airline_sealed_evidence_source_lineage_mismatch",
    )
    if len(error.args) == 1 and error.args[0] in allowed:
        return error.args[0]
    return "airline_sealed_evidence_adapter_invalid"
