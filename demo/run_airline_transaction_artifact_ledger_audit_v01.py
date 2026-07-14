from __future__ import annotations

import json
import os
from collections import Counter
from collections.abc import Mapping
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Any

from hedgehog.domains.airline import transaction_artifact_ledger_v01 as ledger_contracts


PASS = ledger_contracts.STATUS_PASS
FAIL_CLOSED = ledger_contracts.STATUS_FAIL_CLOSED
SKIPPED_CLOSED = "SKIPPED_CLOSED"

ENV_ARTIFACT_DIR = "HEDGEHOG_AIRLINE_LEDGER_AUDIT_ARTIFACT_DIR"
AUDIT_ID = "airline_transaction_artifact_ledger_audit_v01"
AUDIT_VERSION = "v0.1"
NEXT_GATE = (
    "Airline Transaction Artifact Ledger Slice E2 completed-package audit log "
    "and checkpoint sync"
)

LEDGER_FILE = "airline_transaction_artifact_ledger.json"
SUMMARY_FILE = "summary.json"
SECRET_SCAN_FILE = "secret_scan.json"
CAUSAL_FILE = "semantic_to_contract_causal_run.json"
BRIDGE_FILE = "semantic_to_contract_bridge.json"
INTEGRATED_FILE = "integrated_deterministic_airline_summary.json"
BSEP_PACKET_FILE = "tri_party_airline_bsep_packet.json"
BSEP_VALIDATION_FILE = "tri_party_airline_bsep_validation.json"
BSEP_PROJECTIONS_FILE = "tri_party_airline_bsep_side_projections.json"

REQUIRED_SOURCE_FILES = (
    LEDGER_FILE,
    SUMMARY_FILE,
    SECRET_SCAN_FILE,
    CAUSAL_FILE,
    BRIDGE_FILE,
    INTEGRATED_FILE,
    BSEP_PACKET_FILE,
    BSEP_VALIDATION_FILE,
    BSEP_PROJECTIONS_FILE,
)

ROOT_FINAL_TYPES = (
    ledger_contracts.ARTIFACT_CLIENT_ROOT_FINAL,
    ledger_contracts.ARTIFACT_AIRLINE_ROOT_FINAL,
    ledger_contracts.ARTIFACT_BANK_ROOT_FINAL,
)

EXPECTED_BSEP_PROJECTION_SIDES = {
    "client_bsep_projection": "client",
    "airline_bsep_projection": "airline",
    "bank_bsep_projection": "bank",
    "cross_root_bsep_projection": "cross_root_advisory",
}

CAUSAL_ACTOR_REVIEW_ORDER = (
    "client_purchase_intent_reviewer_llm",
    "airline_offer_policy_reviewer_llm",
    "airline_fare_rules_vertical_cell_llm",
    "airline_seat_baggage_vertical_cell_llm",
    "tri_party_evidence_consistency_reviewer_llm",
)

CAUSAL_REVIEWER_RESPONSE_ORDER = (
    "airline_offer_policy_reviewer_llm",
    "airline_fare_rules_vertical_cell_llm",
    "airline_seat_baggage_vertical_cell_llm",
    "tri_party_evidence_consistency_reviewer_llm",
)

REQUIRED_CAUSAL_TRANSACTION_OBJECTS = (
    "proposal",
    "proposer_payload",
    "synthesis",
    "canonical_evidence",
    "client_root_decision",
    "airline_root_resolution",
    "hold_binding",
    "hold_packet",
    "local_chain_validation",
)

BSEP_ARTIFACT_TO_SOURCE_KEY = {
    ledger_contracts.ARTIFACT_CLIENT_BSEP_PROJECTION: "client_bsep_projection",
    ledger_contracts.ARTIFACT_AIRLINE_BSEP_PROJECTION: "airline_bsep_projection",
    ledger_contracts.ARTIFACT_BANK_BSEP_PROJECTION: "bank_bsep_projection",
    ledger_contracts.ARTIFACT_CROSS_ROOT_BSEP_PROJECTION: (
        "cross_root_bsep_projection"
    ),
}

RECEIPT_ARTIFACT_TYPES = (
    ledger_contracts.ARTIFACT_AIRLINE_OFFER_HOLD_RECEIPT,
    ledger_contracts.ARTIFACT_MOCK_TICKET_RECEIPT,
    ledger_contracts.ARTIFACT_MOCK_PURCHASE_RECEIPT,
)

ZERO_COUNTER_FIELDS = (
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

SECRET_TOKENS = tuple(
    dict.fromkeys(
        tuple(getattr(ledger_contracts, "FORBIDDEN_HASH_INPUT_TOKENS", ()))
        + (
            "raw_prompt",
            "raw_response",
            "raw provider",
            "provider response body",
            "provider prompt body",
        ),
    ),
)

HUMAN_LABELS: Mapping[str, tuple[str, str]] = {
    ledger_contracts.ARTIFACT_TRANSACTION_SCOPE: (
        "Transaction scope opened",
        "The Ledger records the transaction envelope and source references.",
    ),
    ledger_contracts.ARTIFACT_CLIENT_BSEP_PROJECTION: (
        "Client bounded context recorded",
        "Client-side BSEP context is evidence, not authority.",
    ),
    ledger_contracts.ARTIFACT_AIRLINE_BSEP_PROJECTION: (
        "Airline bounded context recorded",
        "Airline-side BSEP context is evidence, not authority.",
    ),
    ledger_contracts.ARTIFACT_BANK_BSEP_PROJECTION: (
        "Bank bounded context recorded",
        "Bank-side BSEP context is evidence, not authority.",
    ),
    ledger_contracts.ARTIFACT_CROSS_ROOT_BSEP_PROJECTION: (
        "Cross-root advisory context recorded",
        "Cross-root advisory context is not a fourth Root.",
    ),
    ledger_contracts.ARTIFACT_VALIDATED_CANONICAL_SEMANTIC_EVIDENCE: (
        "Canonical semantic evidence recorded",
        "Validated semantic evidence remains advisory lineage.",
    ),
    ledger_contracts.ARTIFACT_CLIENT_ROOT_SELECTION_DECISION: (
        "ClientRoot selected an offer",
        "ClientRoot decided which offer moved forward.",
    ),
    ledger_contracts.ARTIFACT_AIRLINE_ROOT_OFFER_RESOLUTION: (
        "AirlineRoot resolved the offer",
        "AirlineRoot accepted the selected offer for its local contract path.",
    ),
    ledger_contracts.ARTIFACT_AIRLINE_OFFER_PACKET: (
        "Airline offer packet recorded",
        "The AirlineRoot offer contract is recorded as scoped source fact.",
    ),
    ledger_contracts.ARTIFACT_AIRLINE_HOLD_PACKET: (
        "Airline hold packet recorded",
        "The AirlineRoot hold contract is recorded without executing a booking.",
    ),
    ledger_contracts.ARTIFACT_AIRLINE_OFFER_HOLD_RECEIPT: (
        "Hold receipt recorded",
        "The hold receipt is evidence only and creates no permission.",
    ),
    ledger_contracts.ARTIFACT_CLIENT_PURCHASE_INTENT: (
        "Client purchase intent recorded",
        "ClientRoot intent and exact approval evidence are recorded.",
    ),
    ledger_contracts.ARTIFACT_BANK_PAYMENT_AUTHORIZATION: (
        "Bank payment authorization reference recorded",
        "BankRoot scoped mock authorization reference is recorded.",
    ),
    ledger_contracts.ARTIFACT_AIRLINE_TICKET_ISSUE_INTENT: (
        "Airline ticket issue intent recorded",
        "AirlineRoot ticket intent is recorded without issuing a real ticket.",
    ),
    ledger_contracts.ARTIFACT_MOCK_TICKET_RECEIPT: (
        "Mock ticket receipt recorded",
        "The mock ticket receipt is evidence only.",
    ),
    ledger_contracts.ARTIFACT_MOCK_PURCHASE_RECEIPT: (
        "Mock purchase receipt recorded",
        "The purchase receipt is evidence only and creates no permission.",
    ),
    ledger_contracts.ARTIFACT_CLIENT_ROOT_FINAL: (
        "ClientRoot final recorded",
        "ClientRoot closed its side-specific transaction view.",
    ),
    ledger_contracts.ARTIFACT_AIRLINE_ROOT_FINAL: (
        "AirlineRoot final recorded",
        "AirlineRoot closed its side-specific transaction view.",
    ),
    ledger_contracts.ARTIFACT_BANK_ROOT_FINAL: (
        "BankRoot final recorded",
        "BankRoot closed its side-specific transaction view.",
    ),
}

NON_CLAIMS = (
    "Ledger records trace; it does not authorize.",
    "Ledger audit records consistency; it does not prove semantic truth.",
    "No Crypto Artifact Seal is implemented.",
    "No cryptographic manifest is implemented.",
    "No signature is implemented.",
    "No hash chain is implemented.",
    "No sealed replay is implemented.",
    "No production security claim is made.",
    "No real payment, real ticket, or real booking occurred.",
)


@dataclass(frozen=True)
class AirlineTransactionArtifactLedgerAuditTimelineRowV01:
    ledger_index: int
    event_time: str
    recorded_at: str
    event_type: str
    artifact_type: str
    artifact_id: str
    transaction_id: str
    root_owner: str
    created_by: str
    authority_class: str
    evidence_class: str
    depends_on: tuple[str, ...]
    dependency_count: int
    selected_offer_id: str
    human_event_label: str
    human_explanation: str


@dataclass(frozen=True)
class AirlineTransactionArtifactLedgerAuditReportV01:
    audit_id: str
    audit_version: str
    final_status: str
    source_artifact_dir: str
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
    stored_validation_errors: tuple[Any, ...]
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
    timeline_rows: tuple[AirlineTransactionArtifactLedgerAuditTimelineRowV01, ...]
    validation_errors: tuple[str, ...]
    non_claims: tuple[str, ...]
    next_gate: str


def collect_airline_transaction_artifact_ledger_audit_v01(
    *,
    artifact_dir: str | Path | None = None,
    env: Mapping[str, str] | None = None,
) -> AirlineTransactionArtifactLedgerAuditReportV01:
    selected_dir = _selected_artifact_dir(artifact_dir=artifact_dir, env=env)
    if selected_dir is None:
        return _report(
            final_status=SKIPPED_CLOSED,
            source_artifact_dir="",
            validation_errors=("source_artifact_dir_not_selected",),
        )

    loaded, read_errors, files_read_count = _read_required_json_objects(selected_dir)
    if read_errors:
        return _report(
            final_status=FAIL_CLOSED,
            source_artifact_dir=str(selected_dir),
            files_read_count=files_read_count,
            validation_errors=read_errors,
        )
    try:
        return _audit_loaded_package(selected_dir=selected_dir, loaded=loaded)
    except (TypeError, ValueError, KeyError, IndexError) as exc:
        return _report(
            final_status=FAIL_CLOSED,
            source_artifact_dir=str(selected_dir),
            files_read_count=files_read_count,
            validation_errors=(f"source_package_malformed:{type(exc).__name__}",),
        )


def _selected_artifact_dir(
    *,
    artifact_dir: str | Path | None,
    env: Mapping[str, str] | None,
) -> Path | None:
    if artifact_dir is not None:
        return Path(artifact_dir)
    effective_env = os.environ if env is None else env
    raw = effective_env.get(ENV_ARTIFACT_DIR, "")
    if not raw:
        return None
    return Path(raw)


def _read_required_json_objects(
    selected_dir: Path,
) -> tuple[dict[str, dict[str, Any]], tuple[str, ...], int]:
    loaded: dict[str, dict[str, Any]] = {}
    errors: list[str] = []
    files_read_count = 0
    for filename in REQUIRED_SOURCE_FILES:
        path = selected_dir / filename
        if not path.exists():
            errors.append(f"missing_source_file:{filename}")
            continue
        if not path.is_file():
            errors.append(f"source_file_not_regular:{filename}")
            continue
        try:
            raw = path.read_bytes()
            text = raw.decode("utf-8")
            payload = json.loads(text)
        except UnicodeDecodeError:
            errors.append(f"source_file_invalid_utf8:{filename}")
            continue
        except json.JSONDecodeError:
            errors.append(f"source_file_invalid_json:{filename}")
            continue
        except OSError:
            errors.append(f"source_file_unreadable:{filename}")
            continue
        if not isinstance(payload, dict):
            errors.append(f"source_file_root_not_object:{filename}")
            continue
        loaded[filename] = payload
        files_read_count += 1
    return loaded, tuple(errors), files_read_count


def _audit_loaded_package(
    *,
    selected_dir: Path,
    loaded: Mapping[str, Mapping[str, Any]],
) -> AirlineTransactionArtifactLedgerAuditReportV01:
    ledger = loaded[LEDGER_FILE]
    summary = loaded[SUMMARY_FILE]
    secret_scan = loaded[SECRET_SCAN_FILE]
    causal = loaded[CAUSAL_FILE]
    bridge = loaded[BRIDGE_FILE]
    integrated = loaded[INTEGRATED_FILE]
    bsep_packet = loaded[BSEP_PACKET_FILE]
    bsep_validation = loaded[BSEP_VALIDATION_FILE]
    bsep_projections = loaded[BSEP_PROJECTIONS_FILE]

    errors: list[str] = []
    entries = ledger.get("entries")
    if not isinstance(entries, list) or not all(isinstance(item, dict) for item in entries):
        errors.append("ledger_entries_malformed")
        entries = []
    entries = list(entries)

    errors.extend(
        _source_status_errors(
            summary=summary,
            causal=causal,
            bridge=bridge,
            integrated=integrated,
            bsep_packet=bsep_packet,
            bsep_validation=bsep_validation,
            bsep_projections=bsep_projections,
        ),
    )
    errors.extend(
        _duplicate_view_errors(
            summary=summary,
            ledger=ledger,
            secret_scan=secret_scan,
            bridge=bridge,
            integrated=integrated,
            bsep_packet=bsep_packet,
            bsep_validation=bsep_validation,
            bsep_projections=bsep_projections,
        ),
    )

    shape = _entry_shape_checks(entries)
    errors.extend(shape)

    geometry = _ledger_geometry(entries)
    sequence_valid = tuple(
        entry.get("artifact_type") for entry in entries
    ) == ledger_contracts.EXPECTED_ARTIFACT_TYPE_SEQUENCE
    if not sequence_valid:
        errors.append("artifact_type_sequence_mismatch")

    root_counts = Counter(
        entry.get("artifact_type")
        for entry in entries
        if isinstance(entry.get("artifact_type"), str)
    )
    client_root_final_count = root_counts[ledger_contracts.ARTIFACT_CLIENT_ROOT_FINAL]
    airline_root_final_count = root_counts[ledger_contracts.ARTIFACT_AIRLINE_ROOT_FINAL]
    bank_root_final_count = root_counts[ledger_contracts.ARTIFACT_BANK_ROOT_FINAL]
    root_final_set_valid = (
        client_root_final_count == 1
        and airline_root_final_count == 1
        and bank_root_final_count == 1
        and geometry["actual_root_final_count"] == 3
    )
    if not root_final_set_valid:
        errors.append("root_final_set_mismatch")

    stored_count_errors = _stored_count_errors(ledger, geometry)
    errors.extend(stored_count_errors)

    structure = _entry_structure_checks(entries)
    errors.extend(structure["errors"])

    profile = _profile_checks(entries)
    errors.extend(profile["errors"])

    canonical = _canonical_hash_input_checks(entries)
    errors.extend(canonical["errors"])

    source = _source_consistency_checks(
        ledger=ledger,
        summary=summary,
        causal=causal,
        bridge=bridge,
        integrated=integrated,
        bsep_packet=bsep_packet,
        bsep_validation=bsep_validation,
        bsep_projections=bsep_projections,
        entries=entries,
    )
    errors.extend(source["errors"])

    secret = _secret_boundary_checks(
        ledger=ledger,
        secret_scan=secret_scan,
        entries=entries,
    )
    errors.extend(secret["errors"])

    validation_errors_value = ledger.get("validation_errors", None)
    stored_validation_errors = _tuple_if_sequence(validation_errors_value)
    stored_validation_status = _str_or_empty(ledger.get("validation_status"))
    if stored_validation_status != PASS:
        errors.append("stored_validation_status_not_pass")
    if not isinstance(validation_errors_value, list):
        errors.append("stored_validation_errors_malformed")
    elif validation_errors_value != []:
        errors.append("stored_validation_errors_non_empty")

    timeline_rows, timeline_errors = _timeline_rows(entries)
    errors.extend(timeline_errors)

    zero_counter_values = {
        "audit_created_authority_count": 0,
        "audit_created_permission_count": 0,
        "audit_created_action_count": 0,
        "semantic_rerun_count": 0,
        "corridor_rerun_count": 0,
        "ledger_collection_count": 0,
        "provider_call_count": 0,
        "network_call_count": 0,
        "gemini_call_count": 0,
        "crypto_operation_count": 0,
        "replay_operation_count": 0,
        "real_world_effects_count": 0,
    }

    final_status = PASS if not errors else FAIL_CLOSED
    return _report(
        final_status=final_status,
        source_artifact_dir=str(selected_dir),
        files_read_count=len(REQUIRED_SOURCE_FILES),
        ledger_id=_str_or_empty(ledger.get("ledger_id")),
        transaction_id=source["transaction_id"],
        selected_offer_id=source["selected_offer_id"],
        source_run_ref=source["source_run_ref"],
        source_causal_report_ref=source["source_causal_report_ref"],
        source_corridor_report_ref=source["source_corridor_report_ref"],
        actual_entry_count=geometry["actual_entry_count"],
        actual_dependency_edge_count=geometry["actual_dependency_edge_count"],
        actual_root_final_count=geometry["actual_root_final_count"],
        client_root_final_count=client_root_final_count,
        airline_root_final_count=airline_root_final_count,
        bank_root_final_count=bank_root_final_count,
        artifact_ids_unique=structure["artifact_ids_unique"],
        ledger_indexes_contiguous=structure["ledger_indexes_contiguous"],
        artifact_type_sequence_valid=sequence_valid,
        dependencies_present=structure["dependencies_present"],
        dependencies_backward_only=structure["dependencies_backward_only"],
        dependency_graph_acyclic=structure["dependency_graph_acyclic"],
        root_final_set_valid=root_final_set_valid,
        root_ownership_valid=profile["root_ownership_valid"],
        authority_evidence_boundaries_valid=profile[
            "authority_evidence_boundaries_valid"
        ],
        canonical_hash_inputs_safe=canonical["canonical_hash_inputs_safe"],
        source_refs_consistent=source["source_refs_consistent"],
        transaction_identity_consistent=source["transaction_identity_consistent"],
        selected_offer_chain_consistent=source["selected_offer_chain_consistent"],
        secret_scan_passed=secret["secret_scan_passed"],
        stored_validation_status=stored_validation_status,
        stored_validation_errors=stored_validation_errors,
        timeline_rows=timeline_rows,
        validation_errors=tuple(dict.fromkeys(errors)),
        **zero_counter_values,
    )


def _ledger_geometry(entries: list[dict[str, Any]]) -> dict[str, int]:
    return {
        "actual_entry_count": len(entries),
        "actual_dependency_edge_count": sum(
            len(entry.get("depends_on", ()))
            for entry in entries
            if isinstance(entry.get("depends_on"), list)
        ),
        "actual_root_final_count": sum(
            entry.get("artifact_type") in ROOT_FINAL_TYPES for entry in entries
        ),
    }


def _source_status_errors(
    *,
    summary: Mapping[str, Any],
    causal: Mapping[str, Any],
    bridge: Mapping[str, Any],
    integrated: Mapping[str, Any],
    bsep_packet: Mapping[str, Any],
    bsep_validation: Mapping[str, Any],
    bsep_projections: Mapping[str, Any],
) -> tuple[str, ...]:
    errors: list[str] = []
    if summary.get("final_status") != PASS:
        errors.append("summary_status_not_pass")
    if summary.get("validation_errors") != []:
        errors.append("summary_validation_errors_not_empty")
    ledger_integration = summary.get("airline_transaction_artifact_ledger_integration")
    if not isinstance(ledger_integration, Mapping):
        errors.append("summary_ledger_integration_missing")
        ledger_integration = {}
    for field_name in (
        "integration_status",
        "source_bundle_validation_status",
        "ledger_validation_status",
    ):
        if ledger_integration.get(field_name) != PASS:
            errors.append(f"summary_ledger_{field_name}_not_pass")
    for field_name in (
        "source_bundle_validation_errors",
        "ledger_validation_errors",
    ):
        if ledger_integration.get(field_name) != []:
            errors.append(f"summary_ledger_{field_name}_not_empty")
    if causal.get("final_status") != "LOCAL_MODEL_PASS":
        errors.append("causal_status_not_pass")
    if causal.get("validation_errors") != []:
        errors.append("causal_validation_errors_not_empty")
    errors.extend(_causal_collection_shape_errors(causal))
    for field_name in (
        "semantic_to_root_binding_match",
        "root_to_hold_binding_match",
    ):
        if causal.get(field_name) is not True:
            errors.append(f"causal_{field_name}_not_true")
    for field_name in (
        "default_offer_used",
        "silent_fallback_used",
    ):
        if causal.get(field_name) is not False:
            errors.append(f"causal_{field_name}_not_false")
    for field_name in (
        "provider_created_authority_count",
        "provider_created_contract_count",
        "runtime_receipt_created_count",
        "corridor_execution_count",
        "provider_calls_performed_inside_precollected_entrypoint",
        "duplicate_provider_call_count",
        "real_world_effects_count",
    ):
        if not _is_exact_int_zero(causal.get(field_name)):
            errors.append(f"causal_{field_name}_not_zero")
    if bridge.get("bridge_status") != PASS:
        errors.append("bridge_status_not_pass")
    for field_name in (
        "all_offer_ids_match",
        "causal_report_validation_accepted",
        "bsep_refs_match",
    ):
        if bridge.get(field_name) is not True:
            errors.append(f"bridge_{field_name}_not_true")
    for field_name in (
        "direct_offer_override_used",
        "default_offer_used",
        "silent_fallback_used",
    ):
        if bridge.get(field_name) is not False:
            errors.append(f"bridge_{field_name}_not_false")
    for field_name in (
        "deterministic_report_final_status",
        "deterministic_corridor_final_status",
    ):
        if bridge.get(field_name) != PASS:
            errors.append(f"bridge_{field_name}_not_pass")
    for field_name, expected_value in (
        ("semantic_actor_calls_total", 12),
        ("causal_actor_calls_total", 5),
        ("duplicate_actor_calls", 0),
        ("deterministic_collection_count", 1),
        ("corridor_execution_count", 1),
        ("provider_created_authority_count", 0),
        ("real_world_effects_count", 0),
    ):
        if not _is_exact_int(bridge.get(field_name)) or bridge.get(field_name) != expected_value:
            errors.append(f"bridge_{field_name}_mismatch")
    if integrated.get("collection_status") != PASS:
        errors.append("integrated_collection_status_not_pass")
    if integrated.get("corridor_final_status") != PASS:
        errors.append("integrated_corridor_status_not_pass")
    if not _is_exact_int(integrated.get("corridor_execution_count")) or integrated.get("corridor_execution_count") != 1:
        errors.append("integrated_corridor_execution_count_mismatch")
    if not _is_exact_int_zero(integrated.get("real_world_effects_count")):
        errors.append("integrated_real_world_effects_nonzero")
    if bsep_packet.get("validation_status") != PASS:
        errors.append("bsep_packet_status_not_pass")
    for field_name in (
        "authority_created",
        "action_permission_created",
        "payment_created",
        "ticket_created",
        "booking_created",
        "final_output_created",
        "raw_passport_included",
        "raw_card_included",
        "raw_iban_included",
        "raw_payment_token_included",
        "raw_private_profile_included",
        "raw_provider_text_included",
        "raw_response_dump_included",
    ):
        if bsep_packet.get(field_name) is not False:
            errors.append(f"bsep_packet_{field_name}_not_false")
    if bsep_validation.get("validation_status") != PASS:
        errors.append("bsep_validation_status_not_pass")
    if bsep_validation.get("accepted") is not True:
        errors.append("bsep_validation_not_accepted")
    if bsep_validation.get("errors") != []:
        errors.append("bsep_validation_errors_not_empty")
    for field_name in (
        "bsep_is_truth",
        "bsep_is_authority",
        "bsep_is_permission",
        "bsep_creates_packet",
        "bsep_creates_receipt",
        "bsep_creates_payment",
        "bsep_creates_ticket",
        "bsep_creates_booking",
    ):
        if bsep_validation.get(field_name) is not False:
            errors.append(f"bsep_validation_{field_name}_not_false")
    for source_key in EXPECTED_BSEP_PROJECTION_SIDES:
        projection = bsep_projections.get(source_key)
        if not isinstance(projection, Mapping):
            errors.append(f"bsep_projection_missing:{source_key}")
            continue
        if projection.get("validation_status") != PASS:
            errors.append(f"bsep_projection_status_not_pass:{source_key}")
        for field_name in (
            "authority_created",
            "permission_created",
            "raw_secrets_included",
            "raw_provider_text_included",
        ):
            if projection.get(field_name) is not False:
                errors.append(f"bsep_projection_{field_name}_not_false:{source_key}")
        if not _is_exact_int_zero(projection.get("real_world_effects_count")):
            errors.append(f"bsep_projection_real_world_effects_nonzero:{source_key}")
    return tuple(errors)


def _causal_collection_shape_errors(causal: Mapping[str, Any]) -> tuple[str, ...]:
    errors: list[str] = []
    errors.extend(
        _closed_actor_collection_errors(
            collection=causal.get("actor_reviews"),
            expected_order=CAUSAL_ACTOR_REVIEW_ORDER,
            reason_prefix="causal_actor_reviews",
        ),
    )
    errors.extend(
        _closed_actor_collection_errors(
            collection=causal.get("reviewer_responses"),
            expected_order=CAUSAL_REVIEWER_RESPONSE_ORDER,
            reason_prefix="causal_reviewer_responses",
        ),
    )
    synthesis = causal.get("synthesis")
    pairs = (
        synthesis.get("actor_recommended_offer_ids")
        if isinstance(synthesis, Mapping)
        else None
    )
    errors.extend(
        _closed_actor_recommendation_pair_errors(
            pairs=pairs,
            expected_order=CAUSAL_ACTOR_REVIEW_ORDER,
        ),
    )
    return tuple(errors)


def _closed_actor_collection_errors(
    *,
    collection: Any,
    expected_order: tuple[str, ...],
    reason_prefix: str,
) -> tuple[str, ...]:
    errors: list[str] = []
    if not isinstance(collection, list):
        return (f"{reason_prefix}_shape_mismatch",)
    if len(collection) != len(expected_order):
        errors.append(f"{reason_prefix}_shape_mismatch")
    actor_ids: list[str] = []
    for index, row in enumerate(collection):
        if not isinstance(row, Mapping):
            errors.append(f"{reason_prefix}_row_malformed")
            continue
        actor_id = row.get("actor_id")
        actor_ids.append(actor_id if isinstance(actor_id, str) else "")
        if not _is_non_empty_string(actor_id):
            errors.append(f"{reason_prefix}_actor_id_missing")
        if not _is_non_empty_string(row.get("reviewed_offer_id")):
            errors.append(f"{reason_prefix}_reviewed_offer_id_missing")
    if tuple(actor_ids) != expected_order:
        errors.append(f"{reason_prefix}_actor_order_mismatch")
    if len(set(actor_ids)) != len(actor_ids):
        errors.append(f"{reason_prefix}_duplicate_actor")
    if any(actor_id and actor_id not in expected_order for actor_id in actor_ids):
        errors.append(f"{reason_prefix}_foreign_actor")
    return tuple(errors)


def _closed_actor_recommendation_pair_errors(
    *,
    pairs: Any,
    expected_order: tuple[str, ...],
) -> tuple[str, ...]:
    reason_prefix = "causal_actor_recommended_offer_ids"
    errors: list[str] = []
    if not isinstance(pairs, list):
        return (f"{reason_prefix}_shape_mismatch",)
    if len(pairs) != len(expected_order):
        errors.append(f"{reason_prefix}_shape_mismatch")
    actor_ids: list[str] = []
    for pair in pairs:
        if (
            not isinstance(pair, list)
            or len(pair) != 2
            or not _is_non_empty_string(pair[0])
            or not _is_non_empty_string(pair[1])
        ):
            errors.append(f"{reason_prefix}_pair_malformed")
            actor_ids.append("")
            continue
        actor_ids.append(pair[0])
    if tuple(actor_ids) != expected_order:
        errors.append(f"{reason_prefix}_actor_order_mismatch")
    if len(set(actor_ids)) != len(actor_ids):
        errors.append(f"{reason_prefix}_duplicate_actor")
    if any(actor_id and actor_id not in expected_order for actor_id in actor_ids):
        errors.append(f"{reason_prefix}_foreign_actor")
    return tuple(errors)


def _duplicate_view_errors(
    *,
    summary: Mapping[str, Any],
    ledger: Mapping[str, Any],
    secret_scan: Mapping[str, Any],
    bridge: Mapping[str, Any],
    integrated: Mapping[str, Any],
    bsep_packet: Mapping[str, Any],
    bsep_validation: Mapping[str, Any],
    bsep_projections: Mapping[str, Any],
) -> tuple[str, ...]:
    pairs = (
        ("airline_transaction_artifact_ledger_v0_1", ledger),
        ("semantic_to_contract_deterministic_bridge", bridge),
        ("integrated_deterministic_airline_transaction", integrated),
        ("bsep_membrane", bsep_packet),
        ("bsep_validation", bsep_validation),
        ("bsep_side_projections", bsep_projections),
        ("secret_scan", secret_scan),
    )
    errors: list[str] = []
    for summary_key, standalone in pairs:
        if summary.get(summary_key) != standalone:
            errors.append(f"duplicate_view_mismatch:{summary_key}")
    return tuple(errors)


def _entry_shape_checks(entries: list[dict[str, Any]]) -> tuple[str, ...]:
    errors: list[str] = []
    for index, entry in enumerate(entries):
        for field_name in (
            "artifact_type",
            "artifact_id",
            "event_type",
            "root_owner",
            "created_by",
            "authority_class",
            "evidence_class",
            "transaction_id",
            "event_time",
            "recorded_at",
        ):
            if not _is_non_empty_string(entry.get(field_name)):
                errors.append(f"entry_{field_name}_malformed:{index}")
        if not _is_exact_int(entry.get("ledger_index")):
            errors.append(f"entry_ledger_index_malformed:{index}")
        depends_on = entry.get("depends_on")
        if not isinstance(depends_on, list):
            errors.append(f"entry_depends_on_malformed:{index}")
        else:
            for dependency in depends_on:
                if not _is_non_empty_string(dependency):
                    errors.append(f"entry_dependency_malformed:{index}")
    return tuple(errors)


def _stored_count_errors(
    ledger: Mapping[str, Any],
    geometry: Mapping[str, int],
) -> tuple[str, ...]:
    errors: list[str] = []
    expected = {
        "entry_count": 19,
        "dependency_edge_count": 29,
        "root_final_count": 3,
    }
    actual_names = {
        "entry_count": "actual_entry_count",
        "dependency_edge_count": "actual_dependency_edge_count",
        "root_final_count": "actual_root_final_count",
    }
    for stored_key, expected_value in expected.items():
        actual_value = geometry[actual_names[stored_key]]
        if actual_value != expected_value:
            errors.append(f"actual_{stored_key}_mismatch")
        if ledger.get(stored_key) != actual_value:
            errors.append(f"stored_{stored_key}_mismatch")
    return tuple(errors)


def _entry_structure_checks(entries: list[dict[str, Any]]) -> dict[str, Any]:
    errors: list[str] = []
    ids = [entry.get("artifact_id") for entry in entries]
    artifact_ids_unique = (
        all(isinstance(value, str) and value for value in ids)
        and len(set(ids)) == len(ids)
    )
    if not artifact_ids_unique:
        errors.append("artifact_ids_not_unique")

    ledger_indexes = [entry.get("ledger_index") for entry in entries]
    ledger_indexes_contiguous = ledger_indexes == list(range(len(entries)))
    if not ledger_indexes_contiguous:
        errors.append("ledger_indexes_not_contiguous")

    id_to_index = {
        entry.get("artifact_id"): entry.get("ledger_index")
        for entry in entries
        if isinstance(entry.get("artifact_id"), str)
        and _is_exact_int(entry.get("ledger_index"))
    }
    dependencies_present = True
    dependencies_backward_only = True
    dependency_graph_acyclic = True
    for entry in entries:
        depends_on = entry.get("depends_on")
        if not isinstance(depends_on, list):
            errors.append("depends_on_malformed")
            dependencies_present = False
            dependencies_backward_only = False
            dependency_graph_acyclic = False
            continue
        artifact_id = entry.get("artifact_id")
        ledger_index = entry.get("ledger_index")
        for dependency in depends_on:
            if not isinstance(dependency, str):
                dependencies_present = False
                dependencies_backward_only = False
                dependency_graph_acyclic = False
                continue
            if dependency not in id_to_index:
                dependencies_present = False
            if dependency == artifact_id:
                dependencies_backward_only = False
                dependency_graph_acyclic = False
            if (
                dependency in id_to_index
                and _is_exact_int(ledger_index)
                and id_to_index[dependency] >= ledger_index
            ):
                dependencies_backward_only = False
                dependency_graph_acyclic = False
    if not dependencies_present:
        errors.append("dependency_missing")
    if not dependencies_backward_only:
        errors.append("dependency_not_backward_only")
    if not dependency_graph_acyclic:
        errors.append("dependency_graph_not_acyclic")
    return {
        "artifact_ids_unique": artifact_ids_unique,
        "ledger_indexes_contiguous": ledger_indexes_contiguous,
        "dependencies_present": dependencies_present,
        "dependencies_backward_only": dependencies_backward_only,
        "dependency_graph_acyclic": dependency_graph_acyclic,
        "errors": tuple(errors),
    }


def _profile_checks(entries: list[dict[str, Any]]) -> dict[str, Any]:
    errors: list[str] = []
    root_ownership_valid = True
    authority_evidence_boundaries_valid = True
    for entry in entries:
        artifact_type = entry.get("artifact_type")
        profile = (
            ledger_contracts.ARTIFACT_PROFILES.get(artifact_type)
            if isinstance(artifact_type, str)
            else None
        )
        if profile is None:
            root_ownership_valid = False
            authority_evidence_boundaries_valid = False
            errors.append("unknown_artifact_type")
            continue
        for field_name, expected in (
            ("event_type", profile.event_type),
            ("root_owner", profile.root_owner),
            ("created_by", profile.created_by),
        ):
            if entry.get(field_name) != expected:
                root_ownership_valid = False
                errors.append(f"{field_name}_mismatch")
        for field_name, expected in (
            ("authority_class", profile.authority_class),
            ("evidence_class", profile.evidence_class),
        ):
            if entry.get(field_name) != expected:
                authority_evidence_boundaries_valid = False
                errors.append(f"{field_name}_mismatch")
        if profile.classification != ledger_contracts.CLASS_CANONICAL_LEDGER_ENTRY:
            authority_evidence_boundaries_valid = False
            errors.append("artifact_profile_classification_mismatch")
        if entry.get("authority_class") == "provider_authority":
            authority_evidence_boundaries_valid = False
            errors.append("provider_authority_classification_detected")
        if artifact_type in RECEIPT_ARTIFACT_TYPES and (
            entry.get("authority_class")
            != ledger_contracts.AUTHORITY_EVIDENCE_ONLY_RECEIPT
            or entry.get("evidence_class") != ledger_contracts.EVIDENCE_RECEIPT_ONLY
        ):
            authority_evidence_boundaries_valid = False
            errors.append("receipt_permission_or_authority_detected")
        if artifact_type == ledger_contracts.ARTIFACT_CROSS_ROOT_BSEP_PROJECTION and (
            entry.get("authority_class") == ledger_contracts.AUTHORITY_ROOT_FINAL
        ):
            authority_evidence_boundaries_valid = False
            errors.append("cross_root_advisory_claimed_as_root_final")
        if entry.get("ledger_created_authority") is not False:
            authority_evidence_boundaries_valid = False
            errors.append("ledger_created_authority_detected")
        if entry.get("ledger_created_permission") is not False:
            authority_evidence_boundaries_valid = False
            errors.append("ledger_created_permission_detected")
        if entry.get("ledger_created_action") is not False:
            authority_evidence_boundaries_valid = False
            errors.append("ledger_created_action_detected")
        if not _is_exact_int_zero(entry.get("real_world_effects_count")):
            authority_evidence_boundaries_valid = False
            errors.append("real_world_effect_detected")
    return {
        "root_ownership_valid": root_ownership_valid,
        "authority_evidence_boundaries_valid": authority_evidence_boundaries_valid,
        "errors": tuple(errors),
    }


def _canonical_hash_input_checks(entries: list[dict[str, Any]]) -> dict[str, Any]:
    errors: list[str] = []
    safe = True
    for entry in entries:
        canonical = entry.get("canonical_hash_input")
        if not isinstance(canonical, dict):
            safe = False
            errors.append("canonical_hash_input_malformed")
            continue
        if canonical.get("artifact_id") != entry.get("artifact_id"):
            safe = False
            errors.append("canonical_hash_input_artifact_id_mismatch")
        if canonical.get("depends_on") != entry.get("depends_on"):
            safe = False
            errors.append("canonical_hash_input_dependency_mismatch")
        if _contains_forbidden_secret_material(canonical):
            safe = False
            errors.append("canonical_hash_input_forbidden_raw_material")
    return {
        "canonical_hash_inputs_safe": safe,
        "errors": tuple(errors),
    }


def _source_consistency_checks(
    *,
    ledger: Mapping[str, Any],
    summary: Mapping[str, Any],
    causal: Mapping[str, Any],
    bridge: Mapping[str, Any],
    integrated: Mapping[str, Any],
    bsep_packet: Mapping[str, Any],
    bsep_validation: Mapping[str, Any],
    bsep_projections: Mapping[str, Any],
    entries: list[dict[str, Any]],
) -> dict[str, Any]:
    errors: list[str] = []
    accepted_transaction_id, transaction_errors = _validate_labeled_string_observations(
        _transaction_observations(
            ledger=ledger,
            summary=summary,
            causal=causal,
            bridge=bridge,
            integrated=integrated,
            bsep_packet=bsep_packet,
            bsep_projections=bsep_projections,
            entries=entries,
        ),
        reason_prefix="transaction",
    )
    errors.extend(transaction_errors)
    transaction_identity_consistent = not transaction_errors

    accepted_selected_offer_id, offer_errors = _validate_labeled_string_observations(
        _selected_offer_observations(
            summary=summary,
            causal=causal,
            bridge=bridge,
            integrated=integrated,
            entries=entries,
        ),
        reason_prefix="selected_offer",
    )
    errors.extend(offer_errors)
    selected_offer_chain_consistent = not offer_errors

    source_refs, ref_errors = _source_ref_values(
        ledger=ledger,
        summary=summary,
        causal=causal,
        entries=entries,
        accepted_transaction_id=accepted_transaction_id,
        accepted_selected_offer_id=accepted_selected_offer_id,
    )
    errors.extend(ref_errors)
    source_refs_consistent = not ref_errors and all(source_refs.values())

    errors.extend(
        _bsep_consistency_errors(
            bsep_packet=bsep_packet,
            bsep_validation=bsep_validation,
            bsep_projections=bsep_projections,
            entries=entries,
        ),
    )

    if source_refs_consistent is False:
        errors.append("source_ref_mismatch")
    return {
        "transaction_id": (
            accepted_transaction_id
            if transaction_identity_consistent
            else _str_or_empty(ledger.get("transaction_id"))
        ),
        "selected_offer_id": accepted_selected_offer_id,
        "source_run_ref": source_refs["source_run_ref"],
        "source_causal_report_ref": source_refs["source_causal_report_ref"],
        "source_corridor_report_ref": source_refs["source_corridor_report_ref"],
        "source_refs_consistent": source_refs_consistent,
        "transaction_identity_consistent": transaction_identity_consistent,
        "selected_offer_chain_consistent": selected_offer_chain_consistent,
        "errors": tuple(errors),
    }


def _transaction_observations(
    *,
    ledger: Mapping[str, Any],
    summary: Mapping[str, Any],
    causal: Mapping[str, Any],
    bridge: Mapping[str, Any],
    integrated: Mapping[str, Any],
    bsep_packet: Mapping[str, Any],
    bsep_projections: Mapping[str, Any],
    entries: list[dict[str, Any]],
) -> tuple[tuple[str, Any], ...]:
    observations: list[tuple[str, Any]] = [
        ("ledger.transaction_id", ledger.get("transaction_id")),
        ("summary.transaction_id", summary.get("transaction_id")),
        ("causal.transaction_id", causal.get("transaction_id")),
        ("bridge.transaction_id", bridge.get("transaction_id")),
        ("integrated.transaction_id", integrated.get("transaction_id")),
        ("bsep_packet.transaction_id", bsep_packet.get("transaction_id")),
    ]
    for source_key in EXPECTED_BSEP_PROJECTION_SIDES:
        projection = bsep_projections.get(source_key)
        observations.append(
            (
                f"bsep_side_projections.{source_key}.transaction_id",
                projection.get("transaction_id") if isinstance(projection, Mapping) else None,
            ),
        )
    for index, entry in enumerate(entries):
        observations.append(
            (f"ledger.entries[{index}].transaction_id", entry.get("transaction_id")),
        )
        canonical = entry.get("canonical_hash_input")
        observations.append(
            (
                f"ledger.entries[{index}].canonical_hash_input.transaction_id",
                canonical.get("transaction_id") if isinstance(canonical, Mapping) else None,
            ),
        )
    for causal_key in REQUIRED_CAUSAL_TRANSACTION_OBJECTS:
        causal_object = causal.get(causal_key)
        observations.append(
            (
                f"causal.{causal_key}.transaction_id",
                causal_object.get("transaction_id")
                if isinstance(causal_object, Mapping)
                else None,
            ),
        )
    reviewer_responses = causal.get("reviewer_responses")
    for index in range(len(CAUSAL_REVIEWER_RESPONSE_ORDER)):
        response = (
            reviewer_responses[index]
            if isinstance(reviewer_responses, list)
            and index < len(reviewer_responses)
            else None
        )
        observations.append(
            (
                f"causal.reviewer_responses[{index}].transaction_id",
                response.get("transaction_id") if isinstance(response, Mapping) else None,
            ),
        )
    for causal_key in (
        "proposal",
        "proposer_payload",
        "synthesis",
        "canonical_evidence",
        "client_root_decision",
        "airline_root_resolution",
        "hold_binding",
        "hold_packet",
        "causal_binding_report",
        "local_chain_validation",
        "actor_reviews",
        "reviewer_responses",
    ):
        _collect_transaction_id_observations_from_object(
            causal.get(causal_key),
            f"causal.{causal_key}",
            observations,
        )
    return tuple(observations)


def _collect_transaction_id_observations_from_object(
    value: Any,
    label_prefix: str,
    observations: list[tuple[str, Any]],
) -> None:
    if isinstance(value, Mapping):
        for key, item in value.items():
            child_label = f"{label_prefix}.{key}"
            if key == "transaction_id":
                observations.append((child_label, item))
            _collect_transaction_id_observations_from_object(
                item,
                child_label,
                observations,
            )
    elif isinstance(value, list):
        for index, item in enumerate(value):
            _collect_transaction_id_observations_from_object(
                item,
                f"{label_prefix}[{index}]",
                observations,
            )


def _selected_offer_observations(
    *,
    summary: Mapping[str, Any],
    causal: Mapping[str, Any],
    bridge: Mapping[str, Any],
    integrated: Mapping[str, Any],
    entries: list[dict[str, Any]],
) -> tuple[tuple[str, Any], ...]:
    observations: list[tuple[str, Any]] = [
        (
            "summary.airline_transaction_artifact_ledger_integration.selected_offer_id",
            _nested(
                summary,
                "airline_transaction_artifact_ledger_integration",
                "selected_offer_id",
            ),
        ),
        ("integrated.selected_offer_id", integrated.get("selected_offer_id")),
        ("causal.semantic_recommendation_id", causal.get("semantic_recommendation_id")),
        ("causal.root_selected_offer_id", causal.get("root_selected_offer_id")),
        ("causal.hold_contract_offer_id", causal.get("hold_contract_offer_id")),
        (
            "causal.proposal.recommended_offer_id",
            _nested(causal, "proposal", "recommended_offer_id"),
        ),
        (
            "causal.proposer_payload.recommended_offer_id",
            _nested(causal, "proposer_payload", "recommended_offer_id"),
        ),
        (
            "causal.synthesis.synthesized_recommended_offer_id",
            _nested(causal, "synthesis", "synthesized_recommended_offer_id"),
        ),
        (
            "causal.canonical_evidence.recommended_offer_id",
            _nested(causal, "canonical_evidence", "recommended_offer_id"),
        ),
        (
            "causal.client_root_decision.recommended_offer_id",
            _nested(causal, "client_root_decision", "recommended_offer_id"),
        ),
        (
            "causal.client_root_decision.selected_offer_id",
            _nested(causal, "client_root_decision", "selected_offer_id"),
        ),
        (
            "causal.airline_root_resolution.selected_offer_id",
            _nested(causal, "airline_root_resolution", "selected_offer_id"),
        ),
        (
            "causal.airline_root_resolution.authoritative_offer_ref",
            _nested(causal, "airline_root_resolution", "authoritative_offer_ref"),
        ),
        (
            "causal.airline_root_resolution.resolved_offer_record_ref",
            _nested(causal, "airline_root_resolution", "resolved_offer_record_ref"),
        ),
        (
            "causal.hold_binding.selected_offer_id",
            _nested(causal, "hold_binding", "selected_offer_id"),
        ),
        ("causal.hold_packet.offer_id", _nested(causal, "hold_packet", "offer_id")),
        (
            "causal.causal_binding_report.selected_offer_id",
            _nested(causal, "causal_binding_report", "selected_offer_id"),
        ),
        ("bridge.semantic_recommendation_id", bridge.get("semantic_recommendation_id")),
        (
            "bridge.client_root_selected_offer_id",
            bridge.get("client_root_selected_offer_id"),
        ),
        (
            "bridge.airline_root_resolved_offer_id",
            bridge.get("airline_root_resolved_offer_id"),
        ),
        ("bridge.hold_contract_offer_id", bridge.get("hold_contract_offer_id")),
        (
            "bridge.deterministic_transaction_offer_id",
            bridge.get("deterministic_transaction_offer_id"),
        ),
        (
            "bridge.deterministic_corridor_offer_id",
            bridge.get("deterministic_corridor_offer_id"),
        ),
    ]
    _append_actor_recommended_offer_observations(
        causal.get("synthesis"),
        observations,
    )
    _append_reviewed_offer_observations(
        "causal.actor_reviews",
        causal.get("actor_reviews"),
        observations,
    )
    _append_reviewed_offer_observations(
        "causal.reviewer_responses",
        causal.get("reviewer_responses"),
        observations,
    )
    for index, entry in enumerate(entries):
        canonical = entry.get("canonical_hash_input")
        if isinstance(canonical, Mapping):
            _collect_labeled_offer_observations_from_object(
                canonical,
                f"ledger.entries[{index}].canonical_hash_input",
                observations,
            )
    return tuple(observations)


def _append_actor_recommended_offer_observations(
    synthesis: Any,
    observations: list[tuple[str, Any]],
) -> None:
    pairs = (
        synthesis.get("actor_recommended_offer_ids")
        if isinstance(synthesis, Mapping)
        else None
    )
    if not isinstance(pairs, list):
        observations.append(("causal.synthesis.actor_recommended_offer_ids", None))
        return
    for index, pair in enumerate(pairs):
        if isinstance(pair, list) and len(pair) >= 2:
            value = pair[1]
        else:
            value = None
        observations.append(
            (f"causal.synthesis.actor_recommended_offer_ids[{index}][1]", value),
        )


def _append_reviewed_offer_observations(
    label_prefix: str,
    rows: Any,
    observations: list[tuple[str, Any]],
) -> None:
    if not isinstance(rows, list):
        observations.append((label_prefix, None))
        return
    for index, row in enumerate(rows):
        observations.append(
            (
                f"{label_prefix}[{index}].reviewed_offer_id",
                row.get("reviewed_offer_id") if isinstance(row, Mapping) else None,
            ),
        )


def _collect_labeled_offer_observations_from_object(
    value: Any,
    label_prefix: str,
    observations: list[tuple[str, Any]],
) -> None:
    if isinstance(value, Mapping):
        for key, item in value.items():
            child_label = f"{label_prefix}.{key}"
            if key in {
                "selected_offer_id",
                "offer_id",
                "recommended_offer_id",
                "authoritative_offer_ref",
                "resolved_offer_record_ref",
            }:
                observations.append((child_label, item))
            _collect_labeled_offer_observations_from_object(
                item,
                child_label,
                observations,
            )
    elif isinstance(value, list):
        for index, item in enumerate(value):
            _collect_labeled_offer_observations_from_object(
                item,
                f"{label_prefix}[{index}]",
                observations,
            )


def _validate_labeled_string_observations(
    observations: tuple[tuple[str, Any], ...],
    *,
    reason_prefix: str,
) -> tuple[str, tuple[str, ...]]:
    errors: list[str] = []
    values: list[str] = []
    for label, value in observations:
        if not _is_non_empty_string(value):
            errors.append(f"{reason_prefix}_observation_missing:{label}")
            continue
        values.append(value)
    if values and len(set(values)) != 1:
        errors.append(f"{reason_prefix}_identity_mismatch")
    if not values:
        errors.append(f"{reason_prefix}_identity_missing")
        return "", tuple(errors)
    return values[0], tuple(errors)


def _collect_selected_offer_values_from_object(value: Any, values: set[str]) -> None:
    if isinstance(value, dict):
        for key, item in value.items():
            if key in {
                "selected_offer_id",
                "offer_id",
                "recommended_offer_id",
                "authoritative_offer_ref",
                "resolved_offer_record_ref",
            }:
                values.add(_str_or_empty(item))
            _collect_selected_offer_values_from_object(item, values)
    elif isinstance(value, list):
        for item in value:
            _collect_selected_offer_values_from_object(item, values)


def _source_ref_values(
    ledger: Mapping[str, Any],
    summary: Mapping[str, Any],
    causal: Mapping[str, Any],
    entries: list[dict[str, Any]],
    accepted_transaction_id: str,
    accepted_selected_offer_id: str,
) -> tuple[dict[str, str], tuple[str, ...]]:
    errors: list[str] = []
    transaction_entry = entries[0] if entries else {}
    canonical = transaction_entry.get("canonical_hash_input", {})
    if not isinstance(canonical, dict):
        canonical = {}
    summary_refs = summary.get("airline_transaction_artifact_ledger_integration")
    if not isinstance(summary_refs, dict):
        summary_refs = {}
    source_run_parts = (
        summary.get("run_id"),
        summary.get("report_id"),
        causal.get("scenario_id"),
    )
    source_causal_parts = (causal.get("run_id"), causal.get("scenario_id"))
    if not all(_is_non_empty_string(part) for part in source_run_parts):
        errors.append("source_run_ref_derivation_missing")
    if not all(_is_non_empty_string(part) for part in source_causal_parts):
        errors.append("source_causal_report_ref_derivation_missing")
    if not _is_non_empty_string(accepted_transaction_id):
        errors.append("source_corridor_report_ref_derivation_missing")
    if not _is_non_empty_string(accepted_selected_offer_id):
        errors.append("ledger_id_derivation_missing")

    expected_values = {
        "source_run_ref": (
            f"source_run:{source_run_parts[0]}:{source_run_parts[1]}:"
            f"{source_run_parts[2]}"
            if all(_is_non_empty_string(part) for part in source_run_parts)
            else ""
        ),
        "source_causal_report_ref": (
            f"source_causal_report:{source_causal_parts[0]}:{source_causal_parts[1]}"
            if all(_is_non_empty_string(part) for part in source_causal_parts)
            else ""
        ),
        "source_corridor_report_ref": (
            "source_corridor_report:"
            "airline_ticket_purchase_corridor_runtime_v01:"
            f"{accepted_transaction_id}"
            if _is_non_empty_string(accepted_transaction_id)
            else ""
        ),
    }
    expected_ledger_id = (
        f"airline_transaction_artifact_ledger:{accepted_selected_offer_id}"
        if _is_non_empty_string(accepted_selected_offer_id)
        else ""
    )
    if ledger.get("ledger_id") != expected_ledger_id:
        errors.append("ledger_id_source_identity_mismatch")

    values = {
        key: (
            ledger.get(key),
            canonical.get(key),
            summary_refs.get(key),
        )
        for key in expected_values
    }
    accepted: dict[str, str] = {}
    for key, refs in values.items():
        expected = expected_values[key]
        if not _is_non_empty_string(expected):
            accepted[key] = ""
            continue
        if any(ref != expected for ref in refs):
            errors.append(f"{key}_mismatch")
            accepted[key] = expected
        else:
            accepted[key] = expected
    return accepted, tuple(errors)


def _bsep_consistency_errors(
    *,
    bsep_packet: Mapping[str, Any],
    bsep_validation: Mapping[str, Any],
    bsep_projections: Mapping[str, Any],
    entries: list[dict[str, Any]],
) -> tuple[str, ...]:
    errors: list[str] = []
    if bsep_validation.get("validation_status") != PASS:
        errors.append("bsep_validation_not_pass")
    packet_id = _str_or_empty(bsep_packet.get("bsep_packet_id"))
    transaction_id = _str_or_empty(bsep_packet.get("transaction_id"))
    if not packet_id or not transaction_id:
        errors.append("bsep_packet_identity_missing")
    if set(bsep_projections) != set(EXPECTED_BSEP_PROJECTION_SIDES):
        errors.append("bsep_projection_set_mismatch")
        return tuple(errors)
    entry_by_artifact = {
        entry.get("artifact_type"): entry
        for entry in entries
        if entry.get("artifact_type") in BSEP_ARTIFACT_TO_SOURCE_KEY
    }
    for source_key, expected_side in EXPECTED_BSEP_PROJECTION_SIDES.items():
        projection = bsep_projections.get(source_key)
        if not isinstance(projection, dict):
            errors.append("bsep_projection_wrong_type")
            continue
        if projection.get("side") != expected_side:
            errors.append("bsep_projection_side_mismatch")
        if projection.get("source_bsep_packet_id") != packet_id:
            errors.append("bsep_packet_mismatch")
        if projection.get("transaction_id") != transaction_id:
            errors.append("bsep_transaction_mismatch")
    for artifact_type, source_key in BSEP_ARTIFACT_TO_SOURCE_KEY.items():
        projection = bsep_projections.get(source_key)
        entry = entry_by_artifact.get(artifact_type)
        if not isinstance(projection, dict) or not isinstance(entry, dict):
            errors.append("bsep_entry_missing")
            continue
        canonical = entry.get("canonical_hash_input")
        if not isinstance(canonical, dict):
            errors.append("bsep_canonical_missing")
            continue
        if entry.get("artifact_id") != projection.get("projection_id"):
            errors.append("bsep_projection_id_mismatch")
        if canonical.get("projection_id") != projection.get("projection_id"):
            errors.append("bsep_canonical_projection_id_mismatch")
        if canonical.get("projection_ref") != projection.get("projection_ref"):
            errors.append("bsep_projection_ref_mismatch")
        if canonical.get("bsep_packet_id") != packet_id:
            errors.append("bsep_canonical_packet_mismatch")
    return tuple(errors)


def _secret_boundary_checks(
    *,
    ledger: Mapping[str, Any],
    secret_scan: Mapping[str, Any],
    entries: list[dict[str, Any]],
) -> dict[str, Any]:
    errors: list[str] = []
    matched = secret_scan.get("matched_markers", ())
    matched_markers_empty = matched in ((), [])
    secret_scan_passed = secret_scan.get("passed") is True and matched_markers_empty
    if not secret_scan_passed:
        errors.append("secret_scan_not_pass")
    for entry in entries:
        if entry.get("raw_secret_included") is not False:
            errors.append("raw_secret_included")
        if entry.get("raw_provider_text_included") is not False:
            errors.append("raw_provider_text_included")
        if entry.get("ledger_created_authority") is not False:
            errors.append("entry_ledger_created_authority_not_false")
        if entry.get("ledger_created_permission") is not False:
            errors.append("entry_ledger_created_permission_not_false")
        if entry.get("ledger_created_action") is not False:
            errors.append("entry_ledger_created_action_not_false")
        if not _is_exact_int_zero(entry.get("real_world_effects_count")):
            errors.append("entry_real_world_effects_count_not_zero")
    for field_name in (
        "provider_called_count",
        "network_used_count",
        "gemini_called_count",
        "ledger_created_authority_count",
        "ledger_created_permission_count",
        "ledger_created_action_count",
        "real_world_effects_count",
    ):
        if not _is_exact_int_zero(ledger.get(field_name)):
            errors.append(f"{field_name}_nonzero")
    return {
        "secret_scan_passed": secret_scan_passed,
        "errors": tuple(errors),
    }


def _timeline_rows(
    entries: list[dict[str, Any]],
) -> tuple[tuple[AirlineTransactionArtifactLedgerAuditTimelineRowV01, ...], tuple[str, ...]]:
    rows: list[AirlineTransactionArtifactLedgerAuditTimelineRowV01] = []
    errors: list[str] = []
    for entry in entries:
        artifact_type = _str_or_empty(entry.get("artifact_type"))
        event_type = _str_or_empty(entry.get("event_type"))
        expected_profile = ledger_contracts.ARTIFACT_PROFILES.get(artifact_type)
        label = HUMAN_LABELS.get(artifact_type)
        if expected_profile is None or label is None:
            errors.append("timeline_label_missing")
            continue
        if event_type != expected_profile.event_type:
            errors.append("timeline_event_type_mismatch")
        canonical = entry.get("canonical_hash_input")
        selected_offer_id = ""
        if isinstance(canonical, dict):
            selected_offer_id = _selected_offer_from_canonical(canonical)
        depends_on = entry.get("depends_on")
        if not isinstance(depends_on, list):
            depends_on = []
        rows.append(
            AirlineTransactionArtifactLedgerAuditTimelineRowV01(
                ledger_index=(
                    _int_or_none(entry.get("ledger_index"))
                    if _int_or_none(entry.get("ledger_index")) is not None
                    else -1
                ),
                event_time=_str_or_empty(entry.get("event_time")),
                recorded_at=_str_or_empty(entry.get("recorded_at")),
                event_type=event_type,
                artifact_type=artifact_type,
                artifact_id=_str_or_empty(entry.get("artifact_id")),
                transaction_id=_str_or_empty(entry.get("transaction_id")),
                root_owner=_str_or_empty(entry.get("root_owner")),
                created_by=_str_or_empty(entry.get("created_by")),
                authority_class=_str_or_empty(entry.get("authority_class")),
                evidence_class=_str_or_empty(entry.get("evidence_class")),
                depends_on=tuple(_str_or_empty(value) for value in depends_on),
                dependency_count=len(depends_on),
                selected_offer_id=selected_offer_id,
                human_event_label=label[0],
                human_explanation=label[1],
            ),
        )
    if len(rows) != 19:
        errors.append("timeline_row_count_mismatch")
    return tuple(rows), tuple(errors)


def _selected_offer_from_canonical(canonical: Mapping[str, Any]) -> str:
    values: set[str] = set()
    _collect_selected_offer_values_from_object(canonical, values)
    values.discard("")
    if len(values) == 1:
        return next(iter(values))
    return ""


def _contains_forbidden_secret_material(value: Any) -> bool:
    if isinstance(value, str):
        lowered = value.lower()
        return any(token in lowered for token in SECRET_TOKENS)
    if isinstance(value, dict):
        return any(
            _contains_forbidden_secret_material(key)
            or _contains_forbidden_secret_material(item)
            for key, item in value.items()
        )
    if isinstance(value, list):
        return any(_contains_forbidden_secret_material(item) for item in value)
    return False


def _report(
    *,
    final_status: str,
    source_artifact_dir: str,
    required_source_files: tuple[str, ...] = REQUIRED_SOURCE_FILES,
    files_read_count: int = 0,
    ledger_id: str = "",
    transaction_id: str = "",
    selected_offer_id: str = "",
    source_run_ref: str = "",
    source_causal_report_ref: str = "",
    source_corridor_report_ref: str = "",
    actual_entry_count: int = 0,
    actual_dependency_edge_count: int = 0,
    actual_root_final_count: int = 0,
    client_root_final_count: int = 0,
    airline_root_final_count: int = 0,
    bank_root_final_count: int = 0,
    artifact_ids_unique: bool = False,
    ledger_indexes_contiguous: bool = False,
    artifact_type_sequence_valid: bool = False,
    dependencies_present: bool = False,
    dependencies_backward_only: bool = False,
    dependency_graph_acyclic: bool = False,
    root_final_set_valid: bool = False,
    root_ownership_valid: bool = False,
    authority_evidence_boundaries_valid: bool = False,
    canonical_hash_inputs_safe: bool = False,
    source_refs_consistent: bool = False,
    transaction_identity_consistent: bool = False,
    selected_offer_chain_consistent: bool = False,
    secret_scan_passed: bool = False,
    stored_validation_status: str = "",
    stored_validation_errors: tuple[Any, ...] = (),
    audit_created_authority_count: int = 0,
    audit_created_permission_count: int = 0,
    audit_created_action_count: int = 0,
    semantic_rerun_count: int = 0,
    corridor_rerun_count: int = 0,
    ledger_collection_count: int = 0,
    provider_call_count: int = 0,
    network_call_count: int = 0,
    gemini_call_count: int = 0,
    crypto_operation_count: int = 0,
    replay_operation_count: int = 0,
    real_world_effects_count: int = 0,
    timeline_rows: tuple[AirlineTransactionArtifactLedgerAuditTimelineRowV01, ...] = (),
    validation_errors: tuple[str, ...] = (),
    non_claims: tuple[str, ...] = NON_CLAIMS,
    next_gate: str = NEXT_GATE,
) -> AirlineTransactionArtifactLedgerAuditReportV01:
    return AirlineTransactionArtifactLedgerAuditReportV01(
        audit_id=AUDIT_ID,
        audit_version=AUDIT_VERSION,
        final_status=final_status,
        source_artifact_dir=source_artifact_dir,
        required_source_files=required_source_files,
        files_read_count=files_read_count,
        ledger_id=ledger_id,
        transaction_id=transaction_id,
        selected_offer_id=selected_offer_id,
        source_run_ref=source_run_ref,
        source_causal_report_ref=source_causal_report_ref,
        source_corridor_report_ref=source_corridor_report_ref,
        actual_entry_count=actual_entry_count,
        actual_dependency_edge_count=actual_dependency_edge_count,
        actual_root_final_count=actual_root_final_count,
        client_root_final_count=client_root_final_count,
        airline_root_final_count=airline_root_final_count,
        bank_root_final_count=bank_root_final_count,
        artifact_ids_unique=artifact_ids_unique,
        ledger_indexes_contiguous=ledger_indexes_contiguous,
        artifact_type_sequence_valid=artifact_type_sequence_valid,
        dependencies_present=dependencies_present,
        dependencies_backward_only=dependencies_backward_only,
        dependency_graph_acyclic=dependency_graph_acyclic,
        root_final_set_valid=root_final_set_valid,
        root_ownership_valid=root_ownership_valid,
        authority_evidence_boundaries_valid=authority_evidence_boundaries_valid,
        canonical_hash_inputs_safe=canonical_hash_inputs_safe,
        source_refs_consistent=source_refs_consistent,
        transaction_identity_consistent=transaction_identity_consistent,
        selected_offer_chain_consistent=selected_offer_chain_consistent,
        secret_scan_passed=secret_scan_passed,
        stored_validation_status=stored_validation_status,
        stored_validation_errors=stored_validation_errors,
        audit_created_authority_count=audit_created_authority_count,
        audit_created_permission_count=audit_created_permission_count,
        audit_created_action_count=audit_created_action_count,
        semantic_rerun_count=semantic_rerun_count,
        corridor_rerun_count=corridor_rerun_count,
        ledger_collection_count=ledger_collection_count,
        provider_call_count=provider_call_count,
        network_call_count=network_call_count,
        gemini_call_count=gemini_call_count,
        crypto_operation_count=crypto_operation_count,
        replay_operation_count=replay_operation_count,
        real_world_effects_count=real_world_effects_count,
        timeline_rows=timeline_rows,
        validation_errors=validation_errors,
        non_claims=non_claims,
        next_gate=next_gate,
    )


def report_to_json_safe(report: AirlineTransactionArtifactLedgerAuditReportV01) -> dict[str, Any]:
    return asdict(report)


def _nested(value: Mapping[str, Any], *keys: str) -> Any:
    current: Any = value
    for key in keys:
        if not isinstance(current, Mapping):
            return ""
        current = current.get(key, "")
    return current


def _str_or_empty(value: Any) -> str:
    return value if isinstance(value, str) else ""


def _is_non_empty_string(value: Any) -> bool:
    return isinstance(value, str) and value != ""


def _is_exact_int(value: Any) -> bool:
    return type(value) is int


def _is_exact_int_zero(value: Any) -> bool:
    return _is_exact_int(value) and value == 0


def _int_or_none(value: Any) -> int | None:
    if isinstance(value, bool):
        return None
    return value if isinstance(value, int) else None


def _tuple_if_sequence(value: Any) -> tuple[Any, ...]:
    if isinstance(value, tuple):
        return value
    if isinstance(value, list):
        return tuple(value)
    return (value,) if value else ()


def _first_non_empty(values: set[str]) -> str:
    for value in sorted(values):
        if value:
            return value
    return ""


def main() -> int:
    report = collect_airline_transaction_artifact_ledger_audit_v01()
    print(json.dumps(report_to_json_safe(report), indent=2, sort_keys=True))
    return 0 if report.final_status in (PASS, SKIPPED_CLOSED) else 1


if __name__ == "__main__":
    raise SystemExit(main())
