from __future__ import annotations

from collections.abc import Mapping, Sequence
from dataclasses import asdict, dataclass
import json
from pathlib import Path
from typing import Any

from demo.run_all_layers_applied_super_smoke import (
    collect_all_layers_applied_super_smoke,
    validate_all_layers_applied_super_smoke_report_consistency,
)
from demo.run_tri_party_airline_ticket_purchase_mock_e2e_v01 import (
    collect_tri_party_airline_ticket_purchase_mock_e2e_v01,
)


RUNNER_ID = "living_gauntlet_v01"
RUNNER_VERSION = "v0.1"

STATUS_PASS = "PASS"
STATUS_FAIL_CLOSED = "FAIL_CLOSED"
STATUS_EVIDENCE_ONLY = "EVIDENCE_ONLY"
STATUS_PLANNED_NOT_ACTIVE = "PLANNED_NOT_ACTIVE"
STATUS_ACTIVE = "ACTIVE"
STATUS_REFERENCE_ONLY = "REFERENCE_ONLY"

_REPOSITORY_ROOT = Path(__file__).resolve().parents[1]
_COMPLETION_MANIFEST_PATH = _REPOSITORY_ROOT / "release/completion_manifest.json"
_INTEGRATION_SEAM_INDEX_PATH = (
    _REPOSITORY_ROOT / "release/integration_seam_index.json"
)

_MANIFEST_FIELD_NAMES = frozenset(
    {
        "active_runtime_acts",
        "document_id",
        "evidence_only_references",
        "limitations",
        "manifest_status",
        "non_claims",
        "planned_gate1_acts",
        "public_claims",
        "version",
    }
)
_SEAM_INDEX_FIELD_NAMES = frozenset(
    {"document_id", "index_status", "seams", "version"}
)
_SEAM_FIELD_NAMES = frozenset(
    {
        "authority_status",
        "current_mode",
        "effect_access",
        "gate1_target",
        "notes",
        "seam_class",
        "seam_id",
        "source_module",
        "source_symbol",
        "status",
    }
)
_ACTIVE_ACT_SOURCES = {
    "airline_deterministic_transaction_runtime": (
        "demo.run_tri_party_airline_ticket_purchase_mock_e2e_v01",
        "collect_tri_party_airline_ticket_purchase_mock_e2e_v01",
    ),
    "all_layers_invariant_super_smoke": (
        "demo.run_all_layers_applied_super_smoke",
        "collect_all_layers_applied_super_smoke",
    ),
}
_ACTIVE_ACT_IDS = tuple(_ACTIVE_ACT_SOURCES)
_EVIDENCE_ONLY_ACT_IDS = ("airline_all_real_frozen_reference",)
_PLANNED_ACT_IDS = (
    "generic_integrity_replay",
    "root_signer_isolation_conformance",
    "semantic_work_contract",
    "domain_neutral_kernel_abi",
    "causal_consumption",
    "transition_registry",
    "root_decision_kernel",
    "effect_firewall",
    "generic_multiroot",
    "supplier_water_filter_portability",
    "kernel_conformance_closure",
)
_PLANNED_SEAM_IDS = (
    "generic_integrity_replay_adapter",
    "root_signer_isolation_conformance",
    "supplier_water_filter_abi_adapter",
    "transition_registry",
    "root_decision_kernel",
    "effect_firewall",
    "multiroot_envelope",
    "kernel_conformance_report",
)
_CURRENT_SEAMS = {
    "deterministic_airline_reference_collector": _ACTIVE_ACT_SOURCES[
        "airline_deterministic_transaction_runtime"
    ],
    "all_layers_invariant_super_smoke_collector": _ACTIVE_ACT_SOURCES[
        "all_layers_invariant_super_smoke"
    ],
    "airline_transaction_artifact_ledger_reference": (
        "hedgehog.domains.airline.transaction_artifact_ledger_v01",
        "AirlineTransactionArtifactLedgerV01",
    ),
    "airline_crypto_artifact_seal_reference": (
        "hedgehog.domains.airline.crypto_artifact_seal_v01",
        "AirlineCryptoArtifactSealEnvelopeV01",
    ),
    "airline_sealed_trace_replay_reference": (
        "hedgehog.domains.airline.sealed_trace_replay_v01",
        "AirlineSealedTraceReplayInputV01",
    ),
    "core_context_packets": (
        "hedgehog.context_packets",
        "build_bounded_semantic_evidence_packet",
    ),
    "core_structured_rationale": (
        "hedgehog.structured_rationale",
        "validate_orchestrator_structured_rationale",
    ),
    "core_semantic_reasoning_adapter": (
        "hedgehog.semantic_reasoning_adapter",
        "validate_orchestrator_semantic_reasoning_proposal",
    ),
    "core_action_commit_packet": (
        "hedgehog.action_commit_packet",
        "build_mock_action_commit_packet",
    ),
    "core_mock_connector_sandbox": (
        "hedgehog.mock_connector_sandbox",
        "run_mock_connector_sandbox",
    ),
    "core_fractal_fulfillment": (
        "hedgehog.fractal_fulfillment",
        "run_fractal_order_fulfillment_dag",
    ),
}


@dataclass(frozen=True)
class LivingGauntletActResultV01:
    act_id: str
    errors: tuple[str, ...]
    executed: bool
    no_real_connector_or_action: bool
    real_world_effects_count: int
    root_authority_preserved: bool
    runtime_status: str
    source_module: str
    source_symbol: str
    state: str


_ACTIVE_RESULT_FIELD_NAMES = frozenset(
    {
        "act_id",
        "errors",
        "executed",
        "no_real_connector_or_action",
        "real_world_effects_count",
        "root_authority_preserved",
        "runtime_status",
        "source_module",
        "source_symbol",
        "state",
    }
)
_EVIDENCE_RESULT_FIELD_NAMES = frozenset(
    {"act_id", "evidence_paths", "executed", "state"}
)
_PLANNED_RESULT_FIELD_NAMES = frozenset({"act_id", "executed", "state"})
_INVARIANT_RESULT_FIELD_NAMES = frozenset({"invariant_id", "state"})
_COUNTER_FIELD_NAMES = frozenset(
    {
        "active_act_count",
        "active_act_fail_closed_count",
        "active_act_pass_count",
        "active_collector_execution_count",
        "airline_collector_execution_count",
        "evidence_only_entry_count",
        "evidence_only_executed_count",
        "invariant_collector_execution_count",
        "planned_act_count",
        "planned_executed_count",
        "real_world_effects_count",
    }
)


def _reject_json_constant(value: str) -> None:
    raise ValueError(f"non_finite_json_constant:{value}")


def _strict_object_pairs(pairs: list[tuple[str, Any]]) -> dict[str, Any]:
    result: dict[str, Any] = {}
    for key, value in pairs:
        if key in result:
            raise ValueError(f"duplicate_json_key:{key}")
        result[key] = value
    return result


def _load_strict_json_object(path: Path) -> dict[str, Any]:
    raw = path.read_bytes()
    if raw.startswith(b"\xef\xbb\xbf"):
        raise ValueError("json_bom_not_allowed")
    value = json.loads(
        raw.decode("utf-8"),
        object_pairs_hook=_strict_object_pairs,
        parse_constant=_reject_json_constant,
    )
    if not isinstance(value, dict):
        raise ValueError("json_top_level_not_object")
    return value


def _is_exact_int(value: Any) -> bool:
    return isinstance(value, int) and not isinstance(value, bool)


def _is_string_list(value: Any) -> bool:
    return isinstance(value, list) and all(
        isinstance(item, str) and bool(item) for item in value
    )


def _record_ids(records: Any, key: str, prefix: str) -> tuple[tuple[str, ...], list[str]]:
    if not isinstance(records, list):
        return (), [f"{prefix}_not_list"]
    ids: list[str] = []
    errors: list[str] = []
    for index, record in enumerate(records):
        if not isinstance(record, dict):
            errors.append(f"{prefix}_record_not_object:{index}")
            continue
        record_id = record.get(key)
        if not isinstance(record_id, str) or not record_id:
            errors.append(f"{prefix}_id_invalid:{index}")
            continue
        ids.append(record_id)
    if len(ids) != len(set(ids)):
        errors.append(f"{prefix}_duplicate_id")
    return tuple(ids), errors


def _validate_completion_manifest_v01(manifest: Any) -> tuple[str, ...]:
    errors: list[str] = []
    if not isinstance(manifest, dict):
        return ("completion_manifest_not_object",)
    if frozenset(manifest) != _MANIFEST_FIELD_NAMES:
        errors.append("completion_manifest_field_surface_mismatch")
    for key, expected in (
        ("document_id", "living_release_completion_manifest_v01"),
        ("version", RUNNER_VERSION),
        ("manifest_status", "ACTIVE_SCAFFOLD"),
    ):
        if manifest.get(key) != expected:
            errors.append(f"completion_manifest_value_mismatch:{key}")

    active = manifest.get("active_runtime_acts")
    evidence = manifest.get("evidence_only_references")
    planned = manifest.get("planned_gate1_acts")
    active_ids, id_errors = _record_ids(active, "act_id", "active_act")
    errors.extend(id_errors)
    evidence_ids, id_errors = _record_ids(evidence, "act_id", "evidence_act")
    errors.extend(id_errors)
    planned_ids, id_errors = _record_ids(planned, "act_id", "planned_act")
    errors.extend(id_errors)
    if active_ids != _ACTIVE_ACT_IDS:
        errors.append("active_act_ids_mismatch")
    if evidence_ids != _EVIDENCE_ONLY_ACT_IDS:
        errors.append("evidence_only_act_ids_mismatch")
    if planned_ids != _PLANNED_ACT_IDS:
        errors.append("planned_act_ids_mismatch")
    all_ids = active_ids + evidence_ids + planned_ids
    if len(all_ids) != len(set(all_ids)):
        errors.append("completion_manifest_duplicate_act_id")

    if isinstance(active, list):
        for record in active:
            if not isinstance(record, dict):
                continue
            if record.get("status") != STATUS_ACTIVE:
                errors.append(f"active_act_status_invalid:{record.get('act_id', '')}")
            expected_source = _ACTIVE_ACT_SOURCES.get(record.get("act_id"))
            if expected_source is not None and (
                record.get("source_module"), record.get("source_symbol")
            ) != expected_source:
                errors.append(f"active_act_source_mismatch:{record.get('act_id', '')}")
            if not _is_string_list(record.get("claim_ids")):
                errors.append(f"active_act_claim_ids_invalid:{record.get('act_id', '')}")
            if not isinstance(record.get("focused_test"), str):
                errors.append(f"active_act_focused_test_invalid:{record.get('act_id', '')}")
    if isinstance(evidence, list):
        for record in evidence:
            if not isinstance(record, dict):
                continue
            if record.get("status") != STATUS_EVIDENCE_ONLY:
                errors.append("evidence_only_status_invalid")
            if not _is_string_list(record.get("evidence_paths")):
                errors.append("evidence_only_paths_invalid")
            if not _is_string_list(record.get("claim_ids")):
                errors.append("evidence_only_claim_ids_invalid")
    if isinstance(planned, list):
        for record in planned:
            if not isinstance(record, dict):
                continue
            if record.get("status") != STATUS_PLANNED_NOT_ACTIVE:
                errors.append(f"planned_act_status_invalid:{record.get('act_id', '')}")
            if not _is_string_list(record.get("claim_ids")):
                errors.append(f"planned_act_claim_ids_invalid:{record.get('act_id', '')}")

    limitations = manifest.get("limitations")
    limitation_ids, id_errors = _record_ids(
        limitations, "limitation_id", "limitation"
    )
    errors.extend(id_errors)
    if not limitation_ids:
        errors.append("completion_manifest_limitations_empty")
    if isinstance(limitations, list):
        for record in limitations:
            if not isinstance(record, dict) or not isinstance(
                record.get("statement"), str
            ):
                errors.append("completion_manifest_limitation_invalid")

    claims = manifest.get("public_claims")
    claim_ids, id_errors = _record_ids(claims, "claim_id", "public_claim")
    errors.extend(id_errors)
    if not claim_ids:
        errors.append("completion_manifest_public_claims_empty")
    claim_fields = {
        "act_ids",
        "claim_class",
        "claim_id",
        "evidence_ref",
        "focused_test_ref",
        "limitation_ref",
        "runtime_ref",
        "statement",
    }
    class_to_ids = {
        "EXECUTED_RUNTIME": set(active_ids),
        STATUS_EVIDENCE_ONLY: set(evidence_ids),
        STATUS_PLANNED_NOT_ACTIVE: set(planned_ids),
    }
    if isinstance(claims, list):
        for claim in claims:
            if not isinstance(claim, dict):
                continue
            claim_id = claim.get("claim_id", "")
            if set(claim) != claim_fields:
                errors.append(f"public_claim_field_surface_mismatch:{claim_id}")
            claim_class = claim.get("claim_class")
            act_ids = claim.get("act_ids")
            if claim_class not in class_to_ids:
                errors.append(f"public_claim_class_invalid:{claim_id}")
            if not _is_string_list(act_ids):
                errors.append(f"public_claim_act_ids_invalid:{claim_id}")
            elif claim_class in class_to_ids and not set(act_ids).issubset(
                class_to_ids[claim_class]
            ):
                errors.append(f"public_claim_classification_mismatch:{claim_id}")
            for ref_key in (
                "runtime_ref",
                "focused_test_ref",
                "evidence_ref",
                "limitation_ref",
            ):
                if not isinstance(claim.get(ref_key), str) or not claim[ref_key]:
                    errors.append(f"public_claim_reference_invalid:{claim_id}:{ref_key}")
            if claim.get("limitation_ref") not in set(limitation_ids):
                errors.append(f"public_claim_limitation_unknown:{claim_id}")

    if not _is_string_list(manifest.get("non_claims")):
        errors.append("completion_manifest_non_claims_invalid")
    return tuple(dict.fromkeys(errors))


def _validate_integration_seam_index_v01(index: Any) -> tuple[str, ...]:
    errors: list[str] = []
    if not isinstance(index, dict):
        return ("integration_seam_index_not_object",)
    if frozenset(index) != _SEAM_INDEX_FIELD_NAMES:
        errors.append("integration_seam_index_field_surface_mismatch")
    for key, expected in (
        ("document_id", "living_release_integration_seam_index_v01"),
        ("version", RUNNER_VERSION),
        ("index_status", "ACTIVE_SCAFFOLD"),
    ):
        if index.get(key) != expected:
            errors.append(f"integration_seam_index_value_mismatch:{key}")
    seams = index.get("seams")
    seam_ids, id_errors = _record_ids(seams, "seam_id", "seam")
    errors.extend(id_errors)
    if set(_CURRENT_SEAMS) - set(seam_ids):
        errors.append("current_seam_missing")
    if not set(_PLANNED_SEAM_IDS).issubset(seam_ids):
        errors.append("planned_seam_missing")
    if isinstance(seams, list):
        for seam in seams:
            if not isinstance(seam, dict):
                continue
            seam_id = seam.get("seam_id", "")
            if frozenset(seam) != _SEAM_FIELD_NAMES:
                errors.append(f"seam_field_surface_mismatch:{seam_id}")
            status = seam.get("status")
            if status not in {
                STATUS_ACTIVE,
                STATUS_REFERENCE_ONLY,
                STATUS_PLANNED_NOT_ACTIVE,
            }:
                errors.append(f"seam_status_unknown:{seam_id}")
            if seam_id in _CURRENT_SEAMS:
                if status == STATUS_PLANNED_NOT_ACTIVE:
                    errors.append(f"current_seam_marked_planned:{seam_id}")
                if (
                    seam.get("source_module"), seam.get("source_symbol")
                ) != _CURRENT_SEAMS[seam_id]:
                    errors.append(f"current_seam_source_mismatch:{seam_id}")
            elif seam_id in _PLANNED_SEAM_IDS:
                if status != STATUS_PLANNED_NOT_ACTIVE:
                    errors.append(f"planned_seam_status_invalid:{seam_id}")
                if seam.get("source_symbol") is not None:
                    errors.append(f"planned_seam_symbol_present:{seam_id}")
            if seam_id != "effect_firewall" and seam.get("effect_access") != "NONE":
                errors.append(f"seam_effect_access_forbidden:{seam_id}")
            if seam_id == "effect_firewall" and (
                status != STATUS_PLANNED_NOT_ACTIVE
                or seam.get("effect_access")
                != "BOUNDED_EFFECT_HANDLE_OWNER_PLANNED"
            ):
                errors.append("effect_firewall_boundary_invalid")
            authority_status = seam.get("authority_status")
            if authority_status in {
                "PLANNED_ROOT_BOUNDARY",
                "PLANNED_ROOT_SCOPED_EFFECT_BOUNDARY",
                "PLANNED_ROOT_ENVELOPE",
            } and seam.get("seam_class") != "PLANNED_GATE1_ROOT_BOUNDARY":
                errors.append(f"root_authority_seam_not_explicit_boundary:{seam_id}")
    return tuple(dict.fromkeys(errors))


def _airline_act_result(report: Any) -> LivingGauntletActResultV01:
    act_id = _ACTIVE_ACT_IDS[0]
    source_module, source_symbol = _ACTIVE_ACT_SOURCES[act_id]
    errors: list[str] = []
    root_authority_preserved = False
    no_real_connector_or_action = False
    effects = -1
    runtime_status = "MISSING"
    if not isinstance(report, Mapping):
        errors.append("airline_report_not_mapping")
    else:
        runtime_status = report.get("final_status", "MISSING")
        if runtime_status != STATUS_PASS:
            errors.append("airline_runtime_status_not_pass")
        if report.get("validation_errors") != ():
            errors.append("airline_runtime_validation_errors_present")
        boundaries = report.get("root_boundary_matrix")
        root_authority_preserved = bool(
            isinstance(boundaries, Sequence)
            and not isinstance(boundaries, (str, bytes))
            and len(boundaries) == 12
            and all(
                isinstance(row, Mapping)
                and row.get("boundary_preserved") is True
                and _is_exact_int(row.get("violation_count"))
                and row.get("violation_count") == 0
                for row in boundaries
            )
        )
        counters = report.get("counter_table")
        zero_keys = (
            "real_airline_api_called_count",
            "real_bank_api_called_count",
            "real_payment_executed_count",
            "real_settlement_executed_count",
            "real_booking_created_count",
            "real_ticket_issued_count",
            "provider_called_count",
            "network_used_count",
            "gemini_called_count",
            "cross_root_authority_transfer_count",
            "airline_root_called_real_airline_api_count",
            "airline_root_called_real_gds_api_count",
            "airline_ticket_purchase_corridor_provider_called_count",
            "airline_ticket_purchase_corridor_network_used_count",
            "airline_ticket_purchase_corridor_gemini_called_count",
            "airline_ticket_purchase_corridor_real_world_effects_count",
            "real_world_effects_count",
        )
        if isinstance(counters, Mapping):
            effects_value = counters.get("real_world_effects_count")
            effects = effects_value if _is_exact_int(effects_value) else -1
            no_real_connector_or_action = all(
                _is_exact_int(counters.get(key)) and counters.get(key) == 0
                for key in zero_keys
            )
            if counters.get("final_authority_transferred_between_roots_count") != 0:
                root_authority_preserved = False
        else:
            errors.append("airline_counter_table_missing")
        final_summary = report.get("final_tri_party_mock_summary")
        if not isinstance(final_summary, Mapping) or any(
            final_summary.get(key) is not False
            for key in (
                "authority_transferred_between_roots",
                "real_airline_api_called",
                "real_bank_api_called",
                "real_gds_api_called",
                "real_payment_executed",
                "real_ticket_issued",
                "real_booking_created",
                "provider_called",
                "network_used",
                "gemini_called",
            )
        ):
            no_real_connector_or_action = False
    if not root_authority_preserved:
        errors.append("airline_root_authority_not_preserved")
    if effects != 0:
        errors.append("airline_real_world_effects_nonzero_or_missing")
    if not no_real_connector_or_action:
        errors.append("airline_real_connector_or_action_reported")
    state = STATUS_PASS if not errors else STATUS_FAIL_CLOSED
    return LivingGauntletActResultV01(
        act_id=act_id,
        errors=tuple(dict.fromkeys(errors)),
        executed=True,
        no_real_connector_or_action=no_real_connector_or_action,
        real_world_effects_count=effects,
        root_authority_preserved=root_authority_preserved,
        runtime_status=str(runtime_status),
        source_module=source_module,
        source_symbol=source_symbol,
        state=state,
    )


def _super_smoke_act_result(report: Any) -> LivingGauntletActResultV01:
    act_id = _ACTIVE_ACT_IDS[1]
    source_module, source_symbol = _ACTIVE_ACT_SOURCES[act_id]
    errors: list[str] = []
    summary = getattr(report, "summary", None)
    root_final = getattr(report, "super_smoke_root_final", None)
    input_mode = getattr(report, "input_mode", None)
    runtime_status = (
        summary.get("all_layers_applied_super_smoke_status", "MISSING")
        if isinstance(summary, Mapping)
        else "MISSING"
    )
    try:
        consistency_passed = (
            validate_all_layers_applied_super_smoke_report_consistency(report) is True
        )
    except Exception:
        consistency_passed = False
    if runtime_status != STATUS_PASS:
        errors.append("super_smoke_runtime_status_not_pass")
    if not consistency_passed:
        errors.append("super_smoke_consistency_validation_failed")
    root_authority_preserved = bool(
        isinstance(summary, Mapping)
        and summary.get("root_remains_final_authority") is True
        and isinstance(root_final, Mapping)
        and root_final.get("root_final_authority_preserved") is True
    )
    no_real_connector_or_action = bool(
        isinstance(summary, Mapping)
        and summary.get("no_real_external_action_executed") is True
        and summary.get("no_completed_external_action_created") is True
        and summary.get("gemini_called") is False
        and summary.get("network_called") is False
        and summary.get("production_autonomy_claimed") is False
        and isinstance(input_mode, Mapping)
        and input_mode.get("real_external_action") is False
        and input_mode.get("live_network_used") is False
        and input_mode.get("gemini_called") is False
    )
    effects = 0 if no_real_connector_or_action else -1
    if not root_authority_preserved:
        errors.append("super_smoke_root_authority_not_preserved")
    if not no_real_connector_or_action:
        errors.append("super_smoke_real_connector_or_action_reported")
    state = STATUS_PASS if not errors else STATUS_FAIL_CLOSED
    return LivingGauntletActResultV01(
        act_id=act_id,
        errors=tuple(dict.fromkeys(errors)),
        executed=True,
        no_real_connector_or_action=no_real_connector_or_action,
        real_world_effects_count=effects,
        root_authority_preserved=root_authority_preserved,
        runtime_status=str(runtime_status),
        source_module=source_module,
        source_symbol=source_symbol,
        state=state,
    )


def _failed_act_result(*, act_id: str, reason: str) -> LivingGauntletActResultV01:
    source_module, source_symbol = _ACTIVE_ACT_SOURCES[act_id]
    return LivingGauntletActResultV01(
        act_id=act_id,
        errors=(reason,),
        executed=True,
        no_real_connector_or_action=False,
        real_world_effects_count=-1,
        root_authority_preserved=False,
        runtime_status="COLLECTOR_FAILURE",
        source_module=source_module,
        source_symbol=source_symbol,
        state=STATUS_FAIL_CLOSED,
    )


def _invariant_result(invariant_id: str, passed: bool) -> dict[str, Any]:
    return {
        "invariant_id": invariant_id,
        "state": STATUS_PASS if passed else STATUS_FAIL_CLOSED,
    }


def _aggregate_real_world_effects_count(active: Any) -> int:
    if not isinstance(active, list) or len(active) != len(_ACTIVE_ACT_IDS):
        return -1
    effect_counts = [
        row.get("real_world_effects_count") if isinstance(row, Mapping) else None
        for row in active
    ]
    if not all(_is_exact_int(value) and value >= 0 for value in effect_counts):
        return -1
    return sum(effect_counts)


def _derive_report_counters_v01(
    active: Any,
    evidence: Any,
    planned: Any,
) -> dict[str, int]:
    active_rows = active if isinstance(active, list) else []
    evidence_rows = evidence if isinstance(evidence, list) else []
    planned_rows = planned if isinstance(planned, list) else []
    return {
        "active_act_count": len(active_rows),
        "active_act_fail_closed_count": sum(
            isinstance(row, Mapping) and row.get("state") == STATUS_FAIL_CLOSED
            for row in active_rows
        ),
        "active_act_pass_count": sum(
            isinstance(row, Mapping) and row.get("state") == STATUS_PASS
            for row in active_rows
        ),
        "active_collector_execution_count": sum(
            isinstance(row, Mapping) and row.get("executed") is True
            for row in active_rows
        ),
        "airline_collector_execution_count": sum(
            isinstance(row, Mapping)
            and row.get("act_id") == _ACTIVE_ACT_IDS[0]
            and row.get("executed") is True
            for row in active_rows
        ),
        "evidence_only_entry_count": len(evidence_rows),
        "evidence_only_executed_count": sum(
            isinstance(row, Mapping) and row.get("executed") is True
            for row in evidence_rows
        ),
        "invariant_collector_execution_count": sum(
            isinstance(row, Mapping)
            and row.get("act_id") == _ACTIVE_ACT_IDS[1]
            and row.get("executed") is True
            for row in active_rows
        ),
        "planned_act_count": len(planned_rows),
        "planned_executed_count": sum(
            isinstance(row, Mapping) and row.get("executed") is True
            for row in planned_rows
        ),
        "real_world_effects_count": _aggregate_real_world_effects_count(active_rows),
    }


def collect_living_gauntlet_v01() -> dict[str, Any]:
    errors: list[str] = []
    manifest: dict[str, Any] = {}
    seam_index: dict[str, Any] = {}
    try:
        manifest = _load_strict_json_object(_COMPLETION_MANIFEST_PATH)
        errors.extend(_validate_completion_manifest_v01(manifest))
    except (OSError, UnicodeError, ValueError, json.JSONDecodeError) as exc:
        errors.append(f"completion_manifest_load_failed:{type(exc).__name__}")
    try:
        seam_index = _load_strict_json_object(_INTEGRATION_SEAM_INDEX_PATH)
        errors.extend(_validate_integration_seam_index_v01(seam_index))
    except (OSError, UnicodeError, ValueError, json.JSONDecodeError) as exc:
        errors.append(f"integration_seam_index_load_failed:{type(exc).__name__}")

    active_results: list[LivingGauntletActResultV01] = []
    airline_calls = 0
    invariant_calls = 0
    if not errors:
        airline_calls += 1
        try:
            active_results.append(
                _airline_act_result(
                    collect_tri_party_airline_ticket_purchase_mock_e2e_v01()
                )
            )
        except Exception:
            active_results.append(
                _failed_act_result(
                    act_id=_ACTIVE_ACT_IDS[0],
                    reason="airline_collector_failed",
                )
            )
        invariant_calls += 1
        try:
            active_results.append(
                _super_smoke_act_result(collect_all_layers_applied_super_smoke())
            )
        except Exception:
            active_results.append(
                _failed_act_result(
                    act_id=_ACTIVE_ACT_IDS[1],
                    reason="super_smoke_collector_failed",
                )
            )

    for result in active_results:
        errors.extend(result.errors)
    evidence_entries = [
        {
            "act_id": record["act_id"],
            "evidence_paths": list(record["evidence_paths"]),
            "executed": False,
            "state": STATUS_EVIDENCE_ONLY,
        }
        for record in manifest.get("evidence_only_references", [])
        if isinstance(record, dict)
        and isinstance(record.get("evidence_paths"), list)
        and isinstance(record.get("act_id"), str)
    ]
    planned_entries = [
        {
            "act_id": record["act_id"],
            "executed": False,
            "state": STATUS_PLANNED_NOT_ACTIVE,
        }
        for record in manifest.get("planned_gate1_acts", [])
        if isinstance(record, dict) and isinstance(record.get("act_id"), str)
    ]
    active_pass_count = sum(
        result.state == STATUS_PASS for result in active_results
    )
    index_valid = not any(
        error.startswith(("completion_manifest", "integration_seam", "active_act", "evidence_", "planned_act", "public_claim", "current_seam", "planned_seam", "seam_", "effect_firewall", "root_authority_seam"))
        for error in errors
    )
    invariants = [
        _invariant_result("release_indexes_valid", index_valid),
        _invariant_result(
            "all_active_acts_executed_once",
            airline_calls == 1
            and invariant_calls == 1
            and len(active_results) == len(_ACTIVE_ACT_IDS),
        ),
        _invariant_result(
            "all_active_acts_pass",
            active_pass_count == len(_ACTIVE_ACT_IDS),
        ),
        _invariant_result(
            "root_authority_preserved",
            bool(active_results)
            and all(result.root_authority_preserved for result in active_results),
        ),
        _invariant_result(
            "real_world_effects_zero",
            bool(active_results)
            and all(result.real_world_effects_count == 0 for result in active_results),
        ),
        _invariant_result(
            "no_real_connector_or_action",
            bool(active_results)
            and all(result.no_real_connector_or_action for result in active_results),
        ),
        _invariant_result(
            "evidence_only_not_executed",
            len(evidence_entries) == len(_EVIDENCE_ONLY_ACT_IDS)
            and all(entry["executed"] is False for entry in evidence_entries),
        ),
        _invariant_result(
            "planned_acts_not_executed",
            len(planned_entries) == len(_PLANNED_ACT_IDS)
            and all(entry["executed"] is False for entry in planned_entries),
        ),
    ]
    for invariant in invariants:
        if invariant["state"] != STATUS_PASS:
            errors.append(f"invariant_failed:{invariant['invariant_id']}")
    active_result_rows = [asdict(result) for result in active_results]
    counters = _derive_report_counters_v01(
        active_result_rows,
        evidence_entries,
        planned_entries,
    )
    final_status = STATUS_PASS if not errors else STATUS_FAIL_CLOSED
    report: dict[str, Any] = {
        "runner_id": RUNNER_ID,
        "runner_version": RUNNER_VERSION,
        "active_act_results": active_result_rows,
        "evidence_only_entries": evidence_entries,
        "planned_entries": planned_entries,
        "invariant_results": invariants,
        "public_claims": manifest.get("public_claims", []),
        "non_claims": manifest.get("non_claims", []),
        "validation_errors": tuple(dict.fromkeys(errors)),
        "counters": counters,
        "final_status": final_status,
    }
    valid, report_errors = validate_living_gauntlet_report_v01(report)
    if not valid:
        report["validation_errors"] = tuple(
            dict.fromkeys((*report["validation_errors"], *report_errors))
        )
        report["final_status"] = STATUS_FAIL_CLOSED
    return report


def validate_living_gauntlet_report_v01(
    report: Any,
) -> tuple[bool, tuple[str, ...]]:
    errors: list[str] = []
    if not isinstance(report, Mapping):
        return False, ("living_gauntlet_report_not_mapping",)
    required_fields = {
        "runner_id",
        "runner_version",
        "active_act_results",
        "evidence_only_entries",
        "planned_entries",
        "invariant_results",
        "public_claims",
        "non_claims",
        "validation_errors",
        "counters",
        "final_status",
    }
    if set(report) != required_fields:
        errors.append("living_gauntlet_report_field_surface_mismatch")
    if report.get("runner_id") != RUNNER_ID:
        errors.append("living_gauntlet_runner_id_mismatch")
    if report.get("runner_version") != RUNNER_VERSION:
        errors.append("living_gauntlet_runner_version_mismatch")
    active = report.get("active_act_results")
    evidence = report.get("evidence_only_entries")
    planned = report.get("planned_entries")
    invariants = report.get("invariant_results")
    counters = report.get("counters")
    active_ids, id_errors = _record_ids(active, "act_id", "report_active_act")
    errors.extend(id_errors)
    evidence_ids, id_errors = _record_ids(
        evidence, "act_id", "report_evidence_act"
    )
    errors.extend(id_errors)
    planned_ids, id_errors = _record_ids(planned, "act_id", "report_planned_act")
    errors.extend(id_errors)
    if active_ids != _ACTIVE_ACT_IDS:
        errors.append("report_active_act_ids_mismatch")
    if evidence_ids != _EVIDENCE_ONLY_ACT_IDS:
        errors.append("report_evidence_act_ids_mismatch")
    if planned_ids != _PLANNED_ACT_IDS:
        errors.append("report_planned_act_ids_mismatch")
    if isinstance(active, list):
        for result in active:
            if not isinstance(result, dict):
                continue
            act_id = result.get("act_id", "")
            if frozenset(result) != _ACTIVE_RESULT_FIELD_NAMES:
                errors.append(f"report_active_act_field_surface_mismatch:{act_id}")
            state = result.get("state")
            if state not in {STATUS_PASS, STATUS_FAIL_CLOSED}:
                errors.append(f"report_active_act_state_unknown:{act_id}")
            if state != STATUS_PASS:
                errors.append(f"report_active_act_state_not_pass:{act_id}")
            if result.get("runtime_status") != STATUS_PASS:
                errors.append(f"report_active_runtime_status_not_pass:{act_id}")
            nested_errors = result.get("errors")
            if not isinstance(nested_errors, (tuple, list)) or any(
                not isinstance(item, str) for item in nested_errors
            ):
                errors.append(f"report_active_act_errors_invalid:{act_id}")
            elif nested_errors:
                errors.append(f"report_active_act_errors_present:{act_id}")
            if result.get("executed") is not True:
                errors.append(f"report_active_act_not_executed:{act_id}")
            if result.get("root_authority_preserved") is not True:
                errors.append(f"report_root_authority_lost:{act_id}")
            effects = result.get("real_world_effects_count")
            if not _is_exact_int(effects) or effects != 0:
                errors.append(f"report_real_world_effects_nonzero:{act_id}")
            if result.get("no_real_connector_or_action") is not True:
                errors.append(f"report_real_connector_or_action:{act_id}")
            expected_source = _ACTIVE_ACT_SOURCES.get(act_id)
            if expected_source is None or (
                result.get("source_module"), result.get("source_symbol")
            ) != expected_source:
                errors.append(f"report_active_source_identity_mismatch:{act_id}")
    if isinstance(evidence, list):
        for entry in evidence:
            if not isinstance(entry, dict):
                continue
            if frozenset(entry) != _EVIDENCE_RESULT_FIELD_NAMES:
                errors.append("report_evidence_only_field_surface_mismatch")
            if entry.get("state") != STATUS_EVIDENCE_ONLY:
                errors.append("report_evidence_only_state_invalid")
            if entry.get("executed") is not False:
                errors.append("report_evidence_only_counted_as_executed")
            if not _is_string_list(entry.get("evidence_paths")):
                errors.append("report_evidence_only_paths_invalid")
    if isinstance(planned, list):
        for entry in planned:
            if not isinstance(entry, dict):
                continue
            if frozenset(entry) != _PLANNED_RESULT_FIELD_NAMES:
                errors.append(
                    f"report_planned_field_surface_mismatch:{entry.get('act_id', '')}"
                )
            if entry.get("state") != STATUS_PLANNED_NOT_ACTIVE:
                errors.append(f"report_planned_state_invalid:{entry.get('act_id', '')}")
            if entry.get("executed") is not False:
                errors.append(f"report_planned_counted_as_executed:{entry.get('act_id', '')}")
    if not isinstance(invariants, list) or not invariants:
        errors.append("report_invariant_results_invalid")
    else:
        for item in invariants:
            if not isinstance(item, dict):
                errors.append("report_invariant_row_not_object")
                continue
            if frozenset(item) != _INVARIANT_RESULT_FIELD_NAMES:
                errors.append(
                    f"report_invariant_field_surface_mismatch:{item.get('invariant_id', '')}"
                )
            if item.get("state") != STATUS_PASS:
                errors.append(
                    f"report_invariant_not_pass:{item.get('invariant_id', '')}"
                )
    public_claims = report.get("public_claims")
    if not isinstance(public_claims, list):
        errors.append("report_public_claims_not_list")
    non_claims = report.get("non_claims")
    if not isinstance(non_claims, list) or not non_claims or any(
        not isinstance(item, str) or not item for item in non_claims
    ):
        errors.append("report_non_claims_invalid")
    if not isinstance(counters, Mapping):
        errors.append("report_counters_invalid")
    else:
        if frozenset(counters) != _COUNTER_FIELD_NAMES:
            errors.append("report_counter_field_surface_mismatch")
        derived_counters = _derive_report_counters_v01(active, evidence, planned)
        for key, expected in derived_counters.items():
            if counters.get(key) != expected or not _is_exact_int(counters.get(key)):
                errors.append(f"report_counter_mismatch:{key}")
    existing_errors = report.get("validation_errors")
    if not isinstance(existing_errors, (tuple, list)) or any(
        not isinstance(item, str) for item in existing_errors
    ):
        errors.append("report_validation_errors_invalid")
    else:
        errors.extend(existing_errors)
    final_status = report.get("final_status")
    if final_status not in {STATUS_PASS, STATUS_FAIL_CLOSED}:
        errors.append("report_final_status_unknown")
    if errors and final_status != STATUS_FAIL_CLOSED:
        errors.append("report_failed_checks_not_fail_closed")
    if not errors and final_status != STATUS_PASS:
        errors.append("report_clean_checks_not_pass")
    unique_errors = tuple(dict.fromkeys(errors))
    return not unique_errors, unique_errors


def render_living_gauntlet_v01(report: Mapping[str, Any]) -> str:
    lines = [
        f"living_gauntlet: {report['runner_id']} {report['runner_version']}",
        "",
        "[ACTIVE EXECUTED ACTS]",
    ]
    for result in report["active_act_results"]:
        lines.append(
            " | ".join(
                (
                    f"act_id={result['act_id']}",
                    f"state={result['state']}",
                    f"runtime_status={result['runtime_status']}",
                    f"root_authority_preserved={str(result['root_authority_preserved']).lower()}",
                    f"real_world_effects_count={result['real_world_effects_count']}",
                )
            )
        )
    lines.extend(("", "[EVIDENCE-ONLY REFERENCES]"))
    for entry in report["evidence_only_entries"]:
        lines.append(
            f"act_id={entry['act_id']} | state={entry['state']} | executed=false"
        )
        lines.extend(f"evidence={path}" for path in entry["evidence_paths"])
    lines.extend(("", "[PLANNED GATE-1 ACTS]"))
    for entry in report["planned_entries"]:
        lines.append(
            f"act_id={entry['act_id']} | state={entry['state']} | executed=false"
        )
    lines.extend(("", "[INVARIANTS]"))
    for invariant in report["invariant_results"]:
        lines.append(
            f"invariant_id={invariant['invariant_id']} | state={invariant['state']}"
        )
    lines.extend(("", "[NON-CLAIMS]"))
    lines.extend(f"- {statement}" for statement in report["non_claims"])
    lines.extend(
        (
            "",
            "[FINAL STATUS]",
            f"validation_errors={json.dumps(list(report['validation_errors']), separators=(',', ':'))}",
            f"real_world_effects_count={report['counters']['real_world_effects_count']}",
            f"final_status={report['final_status']}",
        )
    )
    return "\n".join(lines).rstrip() + "\n"


def main() -> int:
    report = collect_living_gauntlet_v01()
    print(render_living_gauntlet_v01(report), end="")
    return 0 if report["final_status"] == STATUS_PASS else 1


if __name__ == "__main__":
    raise SystemExit(main())
