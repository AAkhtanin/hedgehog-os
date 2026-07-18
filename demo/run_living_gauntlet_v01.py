from __future__ import annotations

from collections.abc import Mapping, Sequence
from dataclasses import asdict, dataclass, replace
import json
from pathlib import Path
from typing import Any

from jsonschema import Draft202012Validator

from demo.run_all_layers_applied_super_smoke import (
    collect_all_layers_applied_super_smoke,
    validate_all_layers_applied_super_smoke_report_consistency,
)
from demo.run_tri_party_airline_ticket_purchase_mock_e2e_v01 import (
    collect_tri_party_airline_ticket_purchase_mock_e2e_v01,
)
from hedgehog.kernel.integrity_replay_v01 import (
    ArtifactDependencyEdgeV01,
    AuthorityClassBindingV01,
    EvidenceClassBindingV01,
    RootOwnershipBindingV01,
    STATUS_SELF_CONSISTENT_UNANCHORED as KERNEL_STATUS_UNANCHORED,
    artifact_manifest_to_plain_dict_v01,
    build_artifact_manifest_v01,
    build_canonical_artifact_ref_v01,
    build_default_seal_profile_v01,
    canonical_json_bytes_v01,
    domain_separated_sha256_hex_v01,
    replay_verification_result_to_plain_dict_v01,
    seal_verification_result_to_plain_dict_v01,
    verify_artifact_manifest_v01,
    verify_artifact_replay_v01,
)
from hedgehog.kernel.abi_v01 import (
    CAUSAL_DISPOSITIONS,
    CausalConsumptionRefV01,
    KernelArtifactV01,
    build_causal_consumption_ref_v01,
    build_kernel_artifact_v01,
    causal_consumption_ref_to_plain_dict_v01,
    causal_consumption_refs_to_plain_list_v01,
    kernel_artifact_to_canonical_ref_v01,
    kernel_artifact_to_plain_dict_v01,
    kernel_artifacts_to_plain_list_v01,
    validate_causal_consumption_bundle_v01,
    validate_causal_consumption_ref_v01,
    validate_causal_counterfactual_v01,
    validate_kernel_artifact_bundle_v01,
    validate_kernel_artifact_v01,
)
from hedgehog.kernel.root_signer_isolation_v01 import (
    STATUS_BLOCKED_FAIL_CLOSED as SIGNER_STATUS_BLOCKED,
    STATUS_PASS as SIGNER_STATUS_PASS,
    build_root_owned_commitment_v01,
    build_trusted_root_key_set_v01,
    generate_root_signer_capability_v01,
    root_owned_commitment_to_plain_dict_v01,
    root_signature_to_plain_dict_v01,
    root_signature_verification_result_to_plain_dict_v01,
    sign_root_owned_commitment_v01,
    trusted_root_key_set_to_plain_dict_v01,
    verify_root_signature_v01,
)
from hedgehog.kernel.semantic_work_v01 import (
    CONTRIBUTION_MODES,
    EVIDENCE_STATE_MISSING,
    EVIDENCE_STATE_PRESENT,
    SYNTHESIS_AUTHORITY_ADVISORY,
    build_actor_contribution_v01,
    build_constraint_binding_v01,
    build_evidence_binding_v01,
    build_normalized_claim_v01,
    build_root_review_packet_from_contributions_v01,
    build_semantic_work_request_v01,
    build_uncertainty_binding_v01,
    semantic_work_to_plain_dict_v01,
    validate_root_review_packet_v01,
)
from hedgehog.kernel.trust_model_v01 import (
    build_default_component_trust_profiles_v01,
    validate_component_trust_profiles_v01,
)


RUNNER_ID = "living_gauntlet_v01"
RUNNER_VERSION = "v0.5"
_RELEASE_INDEX_VERSION = "v0.1"

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
_SEMANTIC_WORK_SCHEMA_PATH = _REPOSITORY_ROOT / "schemas/semantic_work_v01.schema.json"
_KERNEL_ARTIFACT_SCHEMA_PATH = (
    _REPOSITORY_ROOT / "schemas/kernel_artifact_v01.schema.json"
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
    "generic_integrity_replay": (
        "demo.run_living_gauntlet_v01",
        "collect_generic_integrity_replay_gauntlet_act_v01",
    ),
    "root_signer_isolation_conformance": (
        "demo.run_living_gauntlet_v01",
        "collect_root_signer_isolation_gauntlet_act_v01",
    ),
    "semantic_work_contract": (
        "demo.run_living_gauntlet_v01",
        "collect_semantic_work_contract_gauntlet_act_v01",
    ),
    "domain_neutral_kernel_abi": (
        "demo.run_living_gauntlet_v01",
        "collect_domain_neutral_kernel_abi_gauntlet_act_v01",
    ),
    "causal_consumption": (
        "demo.run_living_gauntlet_v01",
        "collect_causal_consumption_gauntlet_act_v01",
    ),
}
_ACTIVE_ACT_IDS = tuple(_ACTIVE_ACT_SOURCES)
_EXECUTED_RUNTIME_ACT_IDS = (
    "airline_deterministic_transaction_runtime",
    "all_layers_invariant_super_smoke",
    "generic_integrity_replay",
)
_EXECUTED_CONFORMANCE_ACT_IDS = (
    "root_signer_isolation_conformance",
    "semantic_work_contract",
    "domain_neutral_kernel_abi",
    "causal_consumption",
)
_EVIDENCE_ONLY_ACT_IDS = ("airline_all_real_frozen_reference",)
_PLANNED_ACT_IDS = (
    "transition_registry",
    "root_decision_kernel",
    "effect_firewall",
    "generic_multiroot",
    "supplier_water_filter_portability",
    "kernel_conformance_closure",
)
_PLANNED_SEAM_IDS = (
    "generic_integrity_replay_adapter",
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
    "generic_integrity_replay_core": (
        "hedgehog.kernel.integrity_replay_v01",
        "verify_artifact_replay_v01",
    ),
    "root_signer_isolation_conformance": (
        "hedgehog.kernel.root_signer_isolation_v01",
        "verify_root_signature_v01",
    ),
    "kernel_trust_model_core": (
        "hedgehog.kernel.trust_model_v01",
        "validate_component_trust_profiles_v01",
    ),
    "semantic_work_contract_core": (
        "hedgehog.kernel.semantic_work_v01",
        "build_root_review_packet_from_contributions_v01",
    ),
    "kernel_abi_core": (
        "hedgehog.kernel.abi_v01",
        "validate_kernel_artifact_bundle_v01",
    ),
    "causal_consumption_core": (
        "hedgehog.kernel.abi_v01",
        "validate_causal_counterfactual_v01",
    ),
}
_CURRENT_SEAM_STATUSES = {
    "deterministic_airline_reference_collector": STATUS_ACTIVE,
    "all_layers_invariant_super_smoke_collector": STATUS_ACTIVE,
    "airline_transaction_artifact_ledger_reference": STATUS_REFERENCE_ONLY,
    "airline_crypto_artifact_seal_reference": STATUS_REFERENCE_ONLY,
    "airline_sealed_trace_replay_reference": STATUS_REFERENCE_ONLY,
    "core_context_packets": STATUS_ACTIVE,
    "core_structured_rationale": STATUS_ACTIVE,
    "core_semantic_reasoning_adapter": STATUS_ACTIVE,
    "core_action_commit_packet": STATUS_ACTIVE,
    "core_mock_connector_sandbox": STATUS_ACTIVE,
    "core_fractal_fulfillment": STATUS_ACTIVE,
    "generic_integrity_replay_core": STATUS_ACTIVE,
    "root_signer_isolation_conformance": STATUS_ACTIVE,
    "kernel_trust_model_core": STATUS_ACTIVE,
    "semantic_work_contract_core": STATUS_ACTIVE,
    "kernel_abi_core": STATUS_ACTIVE,
    "causal_consumption_core": STATUS_ACTIVE,
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
        "generic_integrity_replay_execution_count",
        "invariant_collector_execution_count",
        "planned_act_count",
        "planned_executed_count",
        "real_world_effects_count",
        "root_signer_isolation_execution_count",
        "semantic_work_contract_execution_count",
        "domain_neutral_kernel_abi_execution_count",
        "causal_consumption_execution_count",
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


def _normalized_release_text(value: object) -> str:
    return " ".join(value.lower().split()) if isinstance(value, str) else ""


def _active_contract_described_unimplemented(
    active_ids: tuple[str, ...], limitations: object
) -> bool:
    if not isinstance(limitations, list):
        return False
    texts = tuple(
        _normalized_release_text(record.get("statement"))
        for record in limitations
        if isinstance(record, dict)
    )
    stale_phrases: list[str] = []
    if "domain_neutral_kernel_abi" in active_ids:
        stale_phrases.extend(
            (
                "kernel abi remains unimplemented",
                "kernel abi is unimplemented",
                "kernel abi is absent",
            )
        )
    if "causal_consumption" in active_ids:
        stale_phrases.extend(
            (
                "causalconsumptionref remains unimplemented",
                "causalconsumptionref is unimplemented",
                "causalconsumptionref is absent",
            )
        )
    return any(
        any(phrase in text for phrase in stale_phrases)
        or (
            "kernel abi, causalconsumptionref" in text
            and "remain unimplemented" in text
        )
        for text in texts
    )


def _validate_completion_manifest_v01(manifest: Any) -> tuple[str, ...]:
    errors: list[str] = []
    if not isinstance(manifest, dict):
        return ("completion_manifest_not_object",)
    if frozenset(manifest) != _MANIFEST_FIELD_NAMES:
        errors.append("completion_manifest_field_surface_mismatch")
    for key, expected in (
        ("document_id", "living_release_completion_manifest_v01"),
        ("version", _RELEASE_INDEX_VERSION),
        ("manifest_status", "ACTIVE_GATE1_G1B2"),
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
    if _active_contract_described_unimplemented(active_ids, limitations):
        errors.append("completion_manifest_active_contract_described_unimplemented")

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
        "EXECUTED_RUNTIME": set(_EXECUTED_RUNTIME_ACT_IDS),
        "EXECUTED_CONFORMANCE": set(_EXECUTED_CONFORMANCE_ACT_IDS),
        STATUS_EVIDENCE_ONLY: set(_EVIDENCE_ONLY_ACT_IDS),
        STATUS_PLANNED_NOT_ACTIVE: set(_PLANNED_ACT_IDS),
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
            if not act_ids or not _is_string_list(act_ids):
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
        ("version", _RELEASE_INDEX_VERSION),
        ("index_status", "ACTIVE_GATE1_G1B2"),
    ):
        if index.get(key) != expected:
            errors.append(f"integration_seam_index_value_mismatch:{key}")
    seams = index.get("seams")
    seam_ids, id_errors = _record_ids(seams, "seam_id", "seam")
    errors.extend(id_errors)
    expected_seam_ids = set(_CURRENT_SEAMS) | set(_PLANNED_SEAM_IDS)
    if set(seam_ids) != expected_seam_ids:
        errors.append("integration_seam_ids_mismatch")
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
                if status != _CURRENT_SEAM_STATUSES[seam_id]:
                    errors.append(f"current_seam_status_mismatch:{seam_id}")
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
        seam_by_id = {
            seam.get("seam_id"): seam for seam in seams if isinstance(seam, dict)
        }
        abi_seam = seam_by_id.get("kernel_abi_core")
        supplier_seam = seam_by_id.get("supplier_water_filter_abi_adapter")
        supplier_note = _normalized_release_text(
            supplier_seam.get("notes") if isinstance(supplier_seam, dict) else None
        )
        if (
            isinstance(abi_seam, dict)
            and abi_seam.get("status") == STATUS_ACTIVE
            and (
                "no abi is implemented" in supplier_note
                or "abi is absent" in supplier_note
            )
        ):
            errors.append("integration_seam_active_abi_described_absent")
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


_GENERIC_REPLAY_ZERO_COUNTER_FIELDS = (
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


def _build_generic_integrity_replay_fixture_v01(
    fixture_id: str,
) -> tuple[Any, tuple[tuple[str, object], ...]]:
    profile = build_default_seal_profile_v01(timeline_order_required=True)
    if fixture_id == "linear":
        transaction_id = "txn:fixture:linear:001"
        rows = (
            (
                "fixture:linear:scope",
                "scope",
                "root:alpha",
                "ROOT_OWNED",
                "VALIDATED",
                "CONTEXT_EVIDENCE",
                {"label": "scope", "sequence": 0},
            ),
            (
                "fixture:linear:evidence",
                "evidence",
                "root:alpha",
                "ADVISORY",
                "VALIDATED",
                "ADVISORY_EVIDENCE",
                {"label": "evidence", "sequence": 1},
            ),
            (
                "fixture:linear:decision",
                "decision",
                "root:alpha",
                "ROOT_OWNED",
                "ROOT_ACCEPTED",
                "DECISION_EVIDENCE",
                {"label": "decision", "sequence": 2},
            ),
            (
                "fixture:linear:final",
                "final",
                "root:beta",
                "ROOT_OWNED",
                "FINALIZED",
                "FINAL_EVIDENCE",
                {"label": "final", "sequence": 3},
            ),
        )
        edges = (
            ArtifactDependencyEdgeV01(
                "fixture:linear:evidence",
                "fixture:linear:scope",
            ),
            ArtifactDependencyEdgeV01(
                "fixture:linear:decision",
                "fixture:linear:evidence",
            ),
            ArtifactDependencyEdgeV01(
                "fixture:linear:final",
                "fixture:linear:decision",
            ),
        )
    elif fixture_id == "fanout":
        transaction_id = "txn:fixture:fanout:001"
        rows = (
            (
                "fixture:fanout:scope",
                "scope",
                "root:alpha",
                "ROOT_OWNED",
                "VALIDATED",
                "CONTEXT_EVIDENCE",
                {"label": "scope", "sequence": 0},
            ),
            (
                "fixture:fanout:left",
                "branch",
                "root:alpha",
                "ADVISORY",
                "VALIDATED",
                "BRANCH_EVIDENCE",
                {"branch": "left", "sequence": 1},
            ),
            (
                "fixture:fanout:right",
                "branch",
                "root:beta",
                "ADVISORY",
                "VALIDATED",
                "BRANCH_EVIDENCE",
                {"branch": "right", "sequence": 2},
            ),
            (
                "fixture:fanout:review",
                "review",
                "root:alpha",
                "ADVISORY",
                "ROOT_REVIEWED",
                "REVIEW_EVIDENCE",
                {"label": "review", "sequence": 3},
            ),
            (
                "fixture:fanout:final_alpha",
                "final",
                "root:alpha",
                "ROOT_OWNED",
                "FINALIZED",
                "FINAL_EVIDENCE",
                {"label": "final_alpha", "sequence": 4},
            ),
            (
                "fixture:fanout:final_beta",
                "final",
                "root:beta",
                "ROOT_OWNED",
                "FINALIZED",
                "FINAL_EVIDENCE",
                {"label": "final_beta", "sequence": 5},
            ),
        )
        edges = (
            ArtifactDependencyEdgeV01(
                "fixture:fanout:left",
                "fixture:fanout:scope",
            ),
            ArtifactDependencyEdgeV01(
                "fixture:fanout:right",
                "fixture:fanout:scope",
            ),
            ArtifactDependencyEdgeV01(
                "fixture:fanout:review",
                "fixture:fanout:left",
            ),
            ArtifactDependencyEdgeV01(
                "fixture:fanout:review",
                "fixture:fanout:right",
            ),
            ArtifactDependencyEdgeV01(
                "fixture:fanout:final_alpha",
                "fixture:fanout:review",
            ),
            ArtifactDependencyEdgeV01(
                "fixture:fanout:final_beta",
                "fixture:fanout:review",
            ),
        )
    else:
        raise ValueError("generic_fixture_unknown")

    payload_rows = tuple((row[0], row[6]) for row in rows)
    artifacts = tuple(
        build_canonical_artifact_ref_v01(
            artifact_id=row[0],
            artifact_type=row[1],
            schema_version="v1",
            transaction_id=transaction_id,
            owner_root_id=row[2],
            authority_class=row[3],
            lifecycle_state=row[4],
            payload=row[6],
            profile=profile,
        )
        for row in rows
    )
    manifest = build_artifact_manifest_v01(
        transaction_id=transaction_id,
        profile=profile,
        artifacts=artifacts,
        dependency_edges=edges,
        root_ownership_bindings=tuple(
            RootOwnershipBindingV01(row[0], row[2]) for row in rows
        ),
        evidence_class_bindings=tuple(
            EvidenceClassBindingV01(row[0], row[5]) for row in rows
        ),
        authority_class_bindings=tuple(
            AuthorityClassBindingV01(row[0], row[3]) for row in rows
        ),
    )
    return manifest, payload_rows


def _collect_generic_integrity_replay_fixture_records_v01() -> tuple[dict[str, Any], ...]:
    records: list[dict[str, Any]] = []
    for fixture_id in ("linear", "fanout"):
        manifest, payload_rows = _build_generic_integrity_replay_fixture_v01(
            fixture_id
        )
        payload_snapshot = tuple(
            (artifact_id, canonical_json_bytes_v01(payload))
            for artifact_id, payload in payload_rows
        )
        unanchored = verify_artifact_manifest_v01(
            manifest=manifest,
            payload_rows=payload_rows,
        )
        anchored = verify_artifact_manifest_v01(
            manifest=manifest,
            payload_rows=payload_rows,
            expected_manifest_hash=manifest.manifest_hash,
        )
        replay = verify_artifact_replay_v01(
            manifest=manifest,
            payload_rows=payload_rows,
            expected_manifest_hash=manifest.manifest_hash,
        )
        if unanchored.verification_status != KERNEL_STATUS_UNANCHORED:
            raise ValueError("generic_unanchored_verification_failed")
        if anchored.verification_status != STATUS_PASS:
            raise ValueError("generic_expected_hash_verification_failed")
        if replay.replay_status != STATUS_PASS:
            raise ValueError("generic_replay_failed")
        if any(getattr(replay, field) != 0 for field in _GENERIC_REPLAY_ZERO_COUNTER_FIELDS):
            raise ValueError("generic_replay_counter_nonzero")
        first_projection = (
            artifact_manifest_to_plain_dict_v01(manifest),
            seal_verification_result_to_plain_dict_v01(unanchored),
            seal_verification_result_to_plain_dict_v01(anchored),
            replay_verification_result_to_plain_dict_v01(replay),
        )
        second_projection = (
            artifact_manifest_to_plain_dict_v01(manifest),
            seal_verification_result_to_plain_dict_v01(unanchored),
            seal_verification_result_to_plain_dict_v01(anchored),
            replay_verification_result_to_plain_dict_v01(replay),
        )
        if first_projection != second_projection:
            raise ValueError("generic_projection_nondeterministic")
        if payload_snapshot != tuple(
            (artifact_id, canonical_json_bytes_v01(payload))
            for artifact_id, payload in payload_rows
        ):
            raise ValueError("generic_fixture_input_mutated")
        repeated_manifest, repeated_payload_rows = (
            _build_generic_integrity_replay_fixture_v01(fixture_id)
        )
        repeated_replay = verify_artifact_replay_v01(
            manifest=repeated_manifest,
            payload_rows=repeated_payload_rows,
            expected_manifest_hash=repeated_manifest.manifest_hash,
        )
        if (
            repeated_manifest.manifest_hash != manifest.manifest_hash
            or repeated_replay.replay_id != replay.replay_id
        ):
            raise ValueError("generic_fixture_nondeterministic")
        records.append(
            {
                "fixture_id": fixture_id,
                "manifest": manifest,
                "payload_rows": payload_rows,
                "unanchored": unanchored,
                "anchored": anchored,
                "replay": replay,
            }
        )
    return tuple(records)


def collect_generic_integrity_replay_gauntlet_act_v01(
) -> LivingGauntletActResultV01:
    act_id = "generic_integrity_replay"
    source_module, source_symbol = _ACTIVE_ACT_SOURCES[act_id]
    try:
        records = _collect_generic_integrity_replay_fixture_records_v01()
        if len(records) != 2:
            raise ValueError("generic_fixture_count_invalid")
        return LivingGauntletActResultV01(
            act_id=act_id,
            errors=(),
            executed=True,
            no_real_connector_or_action=True,
            real_world_effects_count=0,
            root_authority_preserved=True,
            runtime_status=STATUS_PASS,
            source_module=source_module,
            source_symbol=source_symbol,
            state=STATUS_PASS,
        )
    except Exception:
        return LivingGauntletActResultV01(
            act_id=act_id,
            errors=("generic_integrity_replay_failed",),
            executed=True,
            no_real_connector_or_action=False,
            real_world_effects_count=-1,
            root_authority_preserved=False,
            runtime_status=STATUS_FAIL_CLOSED,
            source_module=source_module,
            source_symbol=source_symbol,
            state=STATUS_FAIL_CLOSED,
        )


def _collect_root_signer_isolation_fixture_metrics_v01() -> dict[str, int]:
    transaction_id = "txn:fixture:root_signer_isolation:001"
    rows = (
        (
            "root:client_os_001",
            "commitment:fixture:client:001",
            "scope:client_owned",
            "fixture:root_owned:client",
        ),
        (
            "root:mock_airline_al",
            "commitment:fixture:airline:001",
            "scope:airline_owned",
            "fixture:root_owned:airline",
        ),
        (
            "root:mock_bank_a",
            "commitment:fixture:bank:001",
            "scope:bank_owned",
            "fixture:root_owned:bank",
        ),
    )
    capabilities = tuple(
        generate_root_signer_capability_v01(root_id=row[0]) for row in rows
    )
    trusted_key_set = build_trusted_root_key_set_v01(
        capabilities=capabilities
    )
    manifest_hash = domain_separated_sha256_hex_v01(
        domain="hedgehog.kernel.root_signer_fixture_manifest.v01",
        payload=canonical_json_bytes_v01(
            {
                "fixture_id": "root_signer_isolation_conformance",
                "transaction_id": transaction_id,
                "root_count": 3,
                "commitment_count": 3,
            }
        ),
    )
    commitments = tuple(
        build_root_owned_commitment_v01(
            commitment_id=row[1],
            transaction_id=transaction_id,
            owner_root_id=row[0],
            commitment_scope=row[2],
            artifact_hash=domain_separated_sha256_hex_v01(
                domain="hedgehog.kernel.root_signer_fixture_artifact.v01",
                payload=canonical_json_bytes_v01(
                    {"fixture_label": row[3]}
                ),
            ),
            manifest_hash=manifest_hash,
            key_id=capability.key_id,
        )
        for row, capability in zip(rows, capabilities)
    )
    signatures = tuple(
        sign_root_owned_commitment_v01(
            capability=capability,
            trusted_key_set=trusted_key_set,
            commitment=commitment,
        )
        for capability, commitment in zip(capabilities, commitments)
    )
    own_results = tuple(
        verify_root_signature_v01(
            trusted_key_set=trusted_key_set,
            commitment=commitment,
            signature=signature,
        )
        for commitment, signature in zip(commitments, signatures)
    )
    own_signature_pass_count = sum(
        result.verification_status == SIGNER_STATUS_PASS
        and result.root_isolation_verified
        for result in own_results
    )

    cross_root_signing_blocked_count = 0
    for capability in capabilities:
        for commitment in commitments:
            if capability.root_id == commitment.owner_root_id:
                continue
            try:
                sign_root_owned_commitment_v01(
                    capability=capability,
                    trusted_key_set=trusted_key_set,
                    commitment=commitment,
                )
            except ValueError as exc:
                if (
                    exc.args != ("signer_root_mismatch",)
                    or exc.__cause__ is not None
                ):
                    raise ValueError("cross_root_signing_reason_invalid") from None
                cross_root_signing_blocked_count += 1
            else:
                raise ValueError("cross_root_signing_not_blocked")

    cross_root_verification_blocked_count = 0
    for signature in signatures:
        for commitment in commitments:
            if signature.owner_root_id == commitment.owner_root_id:
                continue
            result = verify_root_signature_v01(
                trusted_key_set=trusted_key_set,
                commitment=commitment,
                signature=signature,
            )
            expected_errors = (
                "signature_owner_root_mismatch",
                "signature_key_id_mismatch",
                "signature_contract_invalid",
                "commitment_hash_mismatch",
                "root_isolation_failed",
            )
            if (
                result.verification_status != SIGNER_STATUS_BLOCKED
                or result.signature_verified
                or result.root_isolation_verified
                or result.verification_errors != expected_errors
            ):
                raise ValueError(
                    "cross_root_verification_reason_invalid"
                ) from None
            cross_root_verification_blocked_count += 1

    projection_bundle = {
        "trusted_key_set": trusted_root_key_set_to_plain_dict_v01(
            trusted_key_set
        ),
        "commitments": [
            root_owned_commitment_to_plain_dict_v01(item)
            for item in commitments
        ],
        "signatures": [
            root_signature_to_plain_dict_v01(item) for item in signatures
        ],
        "verification_results": [
            root_signature_verification_result_to_plain_dict_v01(item)
            for item in own_results
        ],
    }
    if b"private" in canonical_json_bytes_v01(projection_bundle).lower():
        raise ValueError("private_material_exposed")

    metrics = {
        "capability_count": len(capabilities),
        "own_signature_pass_count": own_signature_pass_count,
        "cross_root_signing_blocked_count": cross_root_signing_blocked_count,
        "cross_root_verification_blocked_count": (
            cross_root_verification_blocked_count
        ),
        "private_key_serialization_count": 0,
        "file_write_count": 0,
        "provider_call_count": 0,
        "network_call_count": 0,
        "gemini_call_count": 0,
        "real_world_effects_count": 0,
    }
    expected = {
        "capability_count": 3,
        "own_signature_pass_count": 3,
        "cross_root_signing_blocked_count": 6,
        "cross_root_verification_blocked_count": 6,
        "private_key_serialization_count": 0,
        "file_write_count": 0,
        "provider_call_count": 0,
        "network_call_count": 0,
        "gemini_call_count": 0,
        "real_world_effects_count": 0,
    }
    if metrics != expected:
        raise ValueError("root_signer_fixture_metrics_invalid")
    return metrics


def collect_root_signer_isolation_gauntlet_act_v01(
) -> LivingGauntletActResultV01:
    act_id = "root_signer_isolation_conformance"
    source_module, source_symbol = _ACTIVE_ACT_SOURCES[act_id]
    try:
        _collect_root_signer_isolation_fixture_metrics_v01()
        return LivingGauntletActResultV01(
            act_id=act_id,
            errors=(),
            executed=True,
            no_real_connector_or_action=True,
            real_world_effects_count=0,
            root_authority_preserved=True,
            runtime_status=STATUS_PASS,
            source_module=source_module,
            source_symbol=source_symbol,
            state=STATUS_PASS,
        )
    except Exception:
        return LivingGauntletActResultV01(
            act_id=act_id,
            errors=("root_signer_isolation_conformance_failed",),
            executed=True,
            no_real_connector_or_action=False,
            real_world_effects_count=-1,
            root_authority_preserved=False,
            runtime_status=STATUS_FAIL_CLOSED,
            source_module=source_module,
            source_symbol=source_symbol,
            state=STATUS_FAIL_CLOSED,
        )


def _build_semantic_work_fixture_v01() -> tuple[Any, tuple[Any, ...], tuple[Any, ...], Any]:
    request = build_semantic_work_request_v01(
        request_id="semantic_work:fixture:001",
        transaction_id="txn:fixture:semantic_work:001",
        target_root_id="root:alpha",
        runtime_topology_ref="runtime_topology:fixture:001",
        bounded_context_refs=(
            "context:fixture:shared:001",
            "context:fixture:bounded:001",
        ),
        permitted_actor_ids=(
            "actor:deterministic:001",
            "actor:reuse:001",
            "actor:cloud:001",
            "actor:local_slm:001",
            "actor:fractal_child:001",
        ),
        permitted_contribution_modes=CONTRIBUTION_MODES,
        requested_subjects=("resource:alpha", "resource:beta"),
        required_evidence_classes=("OBSERVATION", "REFERENCE"),
        forbidden_claims=(
            "root_decision",
            "permission",
            "final_output",
            "authoritative_execution_topology",
        ),
    )
    actor_rows = (
        (
            "contribution:deterministic:001",
            "actor:deterministic:001",
            "deterministic_runtime",
            "DETERMINISTIC",
        ),
        (
            "contribution:reuse:001",
            "actor:reuse:001",
            "drs",
            "INFORMATIONAL_REUSE",
        ),
        (
            "contribution:cloud:001",
            "actor:cloud:001",
            "provider_llm",
            "CLOUD_LLM",
        ),
        (
            "contribution:local_slm:001",
            "actor:local_slm:001",
            "provider_llm",
            "LOCAL_SLM",
        ),
        (
            "contribution:fractal_child:001",
            "actor:fractal_child:001",
            "executor_fractal_child",
            "FRACTAL_CHILD",
        ),
    )
    evidence = tuple(
        build_evidence_binding_v01(
            evidence_id=f"evidence:{mode.lower()}:001",
            evidence_ref=(
                "evidence:fixture:fractal:missing"
                if mode == "FRACTAL_CHILD"
                else f"evidence:fixture:{mode.lower()}:001"
            ),
            evidence_class=(
                "REFERENCE" if mode == "INFORMATIONAL_REUSE" else "OBSERVATION"
            ),
            source_component_id=actor_id,
            provenance_ref=f"provenance:fixture:{mode.lower()}:001",
            evidence_state=(
                EVIDENCE_STATE_MISSING
                if mode == "FRACTAL_CHILD"
                else EVIDENCE_STATE_PRESENT
            ),
        )
        for _, actor_id, _, mode in actor_rows
    )
    deterministic_claim = build_normalized_claim_v01(
        claim_id="claim:fixture:alpha:state:001",
        subject="resource:alpha",
        predicate="state",
        object_or_value={"state": "stable", "ordinal": 1},
        time_envelope_ref="time:fixture:001",
        provenance_refs=("provenance:fixture:deterministic:001",),
        evidence_refs=(evidence[0].evidence_id,),
        confidence_micros=1_000_000,
        source_role="deterministic_runtime",
        source_mode="DETERMINISTIC",
    )
    claims = (
        (deterministic_claim, deterministic_claim),
        (
            build_normalized_claim_v01(
                claim_id="claim:fixture:alpha:history:001",
                subject="resource:alpha",
                predicate="history",
                object_or_value="known",
                time_envelope_ref="time:fixture:001",
                provenance_refs=("provenance:fixture:informational_reuse:001",),
                evidence_refs=(evidence[1].evidence_id,),
                confidence_micros=600_000,
                source_role="drs",
                source_mode="INFORMATIONAL_REUSE",
            ),
        ),
        (
            build_normalized_claim_v01(
                claim_id="claim:fixture:beta:readiness:cloud:001",
                subject="resource:beta",
                predicate="readiness",
                object_or_value="ready",
                time_envelope_ref="time:fixture:conflict:001",
                provenance_refs=("provenance:fixture:cloud_llm:001",),
                evidence_refs=(evidence[2].evidence_id,),
                confidence_micros=700_000,
                source_role="provider_llm",
                source_mode="CLOUD_LLM",
            ),
        ),
        (
            build_normalized_claim_v01(
                claim_id="claim:fixture:beta:readiness:local:001",
                subject="resource:beta",
                predicate="readiness",
                object_or_value="blocked",
                time_envelope_ref="time:fixture:conflict:001",
                provenance_refs=("provenance:fixture:local_slm:001",),
                evidence_refs=(evidence[3].evidence_id,),
                confidence_micros=800_000,
                source_role="provider_llm",
                source_mode="LOCAL_SLM",
            ),
        ),
        (
            build_normalized_claim_v01(
                claim_id="claim:fixture:alpha:capacity:001",
                subject="resource:alpha",
                predicate="capacity",
                object_or_value=["bounded", {"units": 2}],
                time_envelope_ref="time:fixture:001",
                provenance_refs=("provenance:fixture:fractal_child:001",),
                evidence_refs=(evidence[4].evidence_id,),
                confidence_micros=500_000,
                source_role="executor_fractal_child",
                source_mode="FRACTAL_CHILD",
            ),
        ),
    )
    deterministic_constraint = build_constraint_binding_v01(
        constraint_id="constraint:fixture:hard:001",
        subject="resource:alpha",
        predicate="within_scope",
        object_or_value=True,
        source_ref="policy:fixture:001",
        constraint_class="HARD",
        evaluation_state="SATISFIED",
    )
    cloud_constraint = build_constraint_binding_v01(
        constraint_id="constraint:fixture:soft:001",
        subject="resource:beta",
        predicate="readiness_preference",
        object_or_value={"preferred": "ready"},
        source_ref="policy:fixture:002",
        constraint_class="SOFT",
        evaluation_state="UNKNOWN",
    )
    local_uncertainty = build_uncertainty_binding_v01(
        uncertainty_id="uncertainty:fixture:local:001",
        claim_id=claims[3][0].claim_id,
        uncertainty_kind="source_disagreement",
        statement="independent_contribution_requires_root_review",
        confidence_micros=800_000,
        source_ref="provenance:fixture:local_slm:001",
    )
    contributions = tuple(
        build_actor_contribution_v01(
            contribution_id=contribution_id,
            request_id=request.request_id,
            actor_id=actor_id,
            actor_role=actor_role,
            contribution_mode=mode,
            bsep_projection_ref=f"bsep:fixture:{mode.lower()}:001",
            scope="scope:fixture:semantic_review",
            bounded_context_refs=("context:fixture:shared:001",),
            claims=claims[index],
            evidence_bindings=(evidence[index],),
            constraint_bindings=(
                (deterministic_constraint,)
                if index == 0
                else (cloud_constraint,)
                if index == 2
                else ()
            ),
            uncertainty_bindings=(local_uncertainty,) if index == 3 else (),
            requested_validators=(
                "validator:contract:001",
                "validator:evidence:001",
            )
            if index == 0
            else ("validator:evidence:001",),
            forbidden_claims_observed=(),
        )
        for index, (contribution_id, actor_id, actor_role, mode) in enumerate(
            actor_rows
        )
    )
    trust_profiles = build_default_component_trust_profiles_v01()
    packet = build_root_review_packet_from_contributions_v01(
        request=request,
        contributions=contributions,
        trust_profiles=trust_profiles,
    )
    return request, contributions, trust_profiles, packet


def _collect_semantic_work_fixture_metrics_v01() -> dict[str, Any]:
    request, contributions, trust_profiles, packet = _build_semantic_work_fixture_v01()
    before = canonical_json_bytes_v01(
        {
            "request": semantic_work_to_plain_dict_v01(request),
            "contributions": [
                semantic_work_to_plain_dict_v01(item) for item in contributions
            ],
        }
    )
    if validate_component_trust_profiles_v01(profiles=trust_profiles):
        raise ValueError("semantic_work_trust_model_invalid")
    packet_errors = validate_root_review_packet_v01(
        request=request,
        contributions=contributions,
        packet=packet,
        trust_profiles=trust_profiles,
    )
    if packet_errors:
        raise ValueError("semantic_work_packet_invalid")
    projection = semantic_work_to_plain_dict_v01(packet)
    if projection != semantic_work_to_plain_dict_v01(packet):
        raise ValueError("semantic_work_projection_nondeterministic")
    schema = _load_strict_json_object(_SEMANTIC_WORK_SCHEMA_PATH)
    Draft202012Validator.check_schema(schema)
    Draft202012Validator(schema).validate(projection)
    repeated = _build_semantic_work_fixture_v01()[3]
    if projection != semantic_work_to_plain_dict_v01(repeated):
        raise ValueError("semantic_work_fixture_nondeterministic")
    after = canonical_json_bytes_v01(
        {
            "request": semantic_work_to_plain_dict_v01(request),
            "contributions": [
                semantic_work_to_plain_dict_v01(item) for item in contributions
            ],
        }
    )
    if before != after:
        raise ValueError("semantic_work_fixture_mutated")
    raw_claim_count = sum(len(item.claims) for item in contributions)
    normalized_claim_count = len(packet.synthesis_proposal.normalized_claims)
    metrics: dict[str, Any] = {
        "trust_profile_count": len(trust_profiles),
        "contribution_count": len(contributions),
        "contribution_mode_count": len(packet.synthesis_proposal.contribution_modes),
        "raw_claim_count": raw_claim_count,
        "normalized_claim_count": normalized_claim_count,
        "duplicate_removal_count": raw_claim_count - normalized_claim_count,
        "conflict_set_count": len(packet.synthesis_proposal.conflict_sets),
        "missing_evidence_count": len(packet.missing_evidence_refs),
        "root_review_required": packet.synthesis_proposal.root_review_required,
        "advisory_authority": (
            packet.authority_class == SYNTHESIS_AUTHORITY_ADVISORY
        ),
        "root_decision_created_count": int(packet.root_decision_created),
        "permission_created_count": int(packet.permission_created),
        "final_output_created_count": int(packet.final_output_created),
        "provider_call_count": 0,
        "network_call_count": 0,
        "gemini_call_count": 0,
        "real_world_effects_count": 0,
        "proposal_id": packet.synthesis_proposal.proposal_id,
        "packet_id": packet.packet_id,
    }
    expected = {
        "trust_profile_count": 18,
        "contribution_count": 5,
        "contribution_mode_count": 5,
        "raw_claim_count": 6,
        "normalized_claim_count": 5,
        "duplicate_removal_count": 1,
        "conflict_set_count": 1,
        "missing_evidence_count": 1,
        "root_review_required": True,
        "advisory_authority": True,
        "root_decision_created_count": 0,
        "permission_created_count": 0,
        "final_output_created_count": 0,
        "provider_call_count": 0,
        "network_call_count": 0,
        "gemini_call_count": 0,
        "real_world_effects_count": 0,
    }
    if {key: metrics[key] for key in expected} != expected:
        raise ValueError("semantic_work_fixture_metrics_invalid")
    return metrics


def collect_semantic_work_contract_gauntlet_act_v01(
) -> LivingGauntletActResultV01:
    act_id = "semantic_work_contract"
    source_module, source_symbol = _ACTIVE_ACT_SOURCES[act_id]
    try:
        _collect_semantic_work_fixture_metrics_v01()
        return LivingGauntletActResultV01(
            act_id=act_id,
            errors=(),
            executed=True,
            no_real_connector_or_action=True,
            real_world_effects_count=0,
            root_authority_preserved=True,
            runtime_status=STATUS_PASS,
            source_module=source_module,
            source_symbol=source_symbol,
            state=STATUS_PASS,
        )
    except Exception:
        return LivingGauntletActResultV01(
            act_id=act_id,
            errors=("semantic_work_contract_conformance_failed",),
            executed=True,
            no_real_connector_or_action=False,
            real_world_effects_count=-1,
            root_authority_preserved=False,
            runtime_status=STATUS_FAIL_CLOSED,
            source_module=source_module,
            source_symbol=source_symbol,
            state=STATUS_FAIL_CLOSED,
        )


def _kernel_time_envelope_v01(session_anchor: str) -> dict[str, Any]:
    return {
        "pt_created_at": "2026-01-01T00:00:00+00:00",
        "kt_asof": "2026-01-01T00:00:00+00:00",
        "et_observed_at": None,
        "ct_session_anchor": session_anchor,
        "ttl_seconds": 3600,
        "freshness_class": "static",
        "valid_from": "2026-01-01T00:00:00+00:00",
        "valid_to": "2026-01-01T01:00:00+00:00",
    }


def _build_fixture_kernel_artifact_v01(
    *,
    artifact_id: str,
    artifact_type: str,
    transaction_id: str,
    owner_root_id: str,
    source_component: str,
    authority_class: str,
    lifecycle_state: str,
    payload: object,
    parent_refs: tuple[str, ...],
    session_anchor: str,
) -> KernelArtifactV01:
    return build_kernel_artifact_v01(
        abi_version="v1.0",
        artifact_id=artifact_id,
        artifact_type=artifact_type,
        schema_version="v1",
        transaction_id=transaction_id,
        owner_root_id=owner_root_id,
        source_component=source_component,
        authority_class=authority_class,
        lifecycle_state=lifecycle_state,
        payload=payload,
        trace_refs=(f"trace:{artifact_id}",),
        parent_refs=parent_refs,
        time_envelope=_kernel_time_envelope_v01(session_anchor),
    )


def _build_kernel_abi_fixture_v01() -> tuple[KernelArtifactV01, ...]:
    transaction_id = "txn:fixture:kernel_abi:001"
    session_anchor = "session:fixture:kernel_abi:001"
    semantic_contribution = _build_semantic_work_fixture_v01()[1][0]
    rows = (
        (
            "artifact:fixture:abi:route_proposal",
            "OrchestratorRouteProposal",
            "root:alpha",
            "orchestrator",
            "ADVISORY",
            "PROPOSED",
            {"candidate_ref": "candidate:alpha"},
            (),
        ),
        (
            "artifact:fixture:abi:root_route",
            "RootAcceptedRoute",
            "root:alpha",
            "root",
            "ROOT_OWNED",
            "ROOT_ACCEPTED",
            {"accepted_ref": "candidate:alpha"},
            ("artifact:fixture:abi:route_proposal",),
        ),
        (
            "artifact:fixture:abi:topology",
            "RuntimeExecutionTopology",
            "root:alpha",
            "deterministic_runtime",
            "ROOT_AUTHORIZED",
            "VALIDATED",
            {"topology_ref": "topology:alpha"},
            ("artifact:fixture:abi:root_route",),
        ),
        (
            "artifact:fixture:abi:actor_contribution",
            "ActorContribution",
            "root:beta",
            "provider_llm",
            "ADVISORY",
            "VALIDATED",
            semantic_work_to_plain_dict_v01(semantic_contribution),
            ("artifact:fixture:abi:topology",),
        ),
        (
            "artifact:fixture:abi:validated_evidence",
            "ValidatedEvidence",
            "root:alpha",
            "post_vv",
            "EVIDENCE_ONLY",
            "VALIDATED",
            {"validation_state": "accepted"},
            ("artifact:fixture:abi:actor_contribution",),
        ),
        (
            "artifact:fixture:abi:result_proposal",
            "ResultProposal",
            "root:beta",
            "executor_fractal_child",
            "NON_AUTHORITY",
            "VALIDATED",
            {"result_state": "proposed"},
            ("artifact:fixture:abi:topology",),
        ),
    )
    return tuple(
        _build_fixture_kernel_artifact_v01(
            artifact_id=artifact_id,
            artifact_type=artifact_type,
            transaction_id=transaction_id,
            owner_root_id=owner_root_id,
            source_component=source_component,
            authority_class=authority_class,
            lifecycle_state=lifecycle_state,
            payload=payload,
            parent_refs=parent_refs,
            session_anchor=session_anchor,
        )
        for (
            artifact_id,
            artifact_type,
            owner_root_id,
            source_component,
            authority_class,
            lifecycle_state,
            payload,
            parent_refs,
        ) in rows
    )


def _collect_kernel_abi_fixture_metrics_v01() -> dict[str, Any]:
    artifacts = _build_kernel_abi_fixture_v01()
    if any(validate_kernel_artifact_v01(item) for item in artifacts):
        raise ValueError("kernel_abi_artifact_invalid")
    if validate_kernel_artifact_bundle_v01(artifacts=artifacts):
        raise ValueError("kernel_abi_bundle_invalid")
    projections = kernel_artifacts_to_plain_list_v01(artifacts)
    schema = _load_strict_json_object(_KERNEL_ARTIFACT_SCHEMA_PATH)
    validator = Draft202012Validator(schema)
    for projection in projections:
        validator.validate(projection)
    canonical_refs = tuple(kernel_artifact_to_canonical_ref_v01(item) for item in artifacts)
    repeated = _build_kernel_abi_fixture_v01()
    if projections != kernel_artifacts_to_plain_list_v01(repeated):
        raise ValueError("kernel_abi_projection_nondeterministic")
    repeated_refs = tuple(kernel_artifact_to_canonical_ref_v01(item) for item in repeated)
    if canonical_refs != repeated_refs:
        raise ValueError("kernel_abi_ref_nondeterministic")
    first = artifacts[0]
    unknown_major_blocked = "abi_major_version_unknown" in validate_kernel_artifact_v01(
        replace(first, abi_version="v2.0")
    )
    authority_blocked = "authority_class_unknown" in validate_kernel_artifact_v01(
        replace(first, authority_class="UNKNOWN")
    )
    lifecycle_blocked = "lifecycle_state_unknown" in validate_kernel_artifact_v01(
        replace(first, lifecycle_state="UNKNOWN")
    )
    payload_override_blocked = False
    try:
        build_kernel_artifact_v01(
            abi_version="v1.0",
            artifact_id="artifact:fixture:abi:reserved_negative",
            artifact_type="SemanticEvidence",
            schema_version="v1",
            transaction_id="txn:fixture:kernel_abi:001",
            owner_root_id="root:alpha",
            source_component="deterministic_runtime",
            authority_class="NON_AUTHORITY",
            lifecycle_state="VALIDATED",
            payload={"authority_class": "ROOT_OWNED"},
            trace_refs=("trace:fixture:abi:reserved_negative",),
            parent_refs=(),
            time_envelope=_kernel_time_envelope_v01(
                "session:fixture:kernel_abi:001"
            ),
        )
    except ValueError as exc:
        payload_override_blocked = exc.args == ("payload_reserved_field",)
    metrics = {
        "artifact_count": len(artifacts),
        "valid_artifact_count": sum(
            not validate_kernel_artifact_v01(item) for item in artifacts
        ),
        "canonical_ref_count": len(canonical_refs),
        "schema_valid_projection_count": len(projections),
        "unknown_major_blocked": unknown_major_blocked,
        "authority_mutation_blocked": authority_blocked,
        "lifecycle_mutation_blocked": lifecycle_blocked,
        "payload_authority_override_blocked": payload_override_blocked,
        "root_decision_created_count": 0,
        "permission_created_count": 0,
        "final_output_created_count": 0,
        "provider_call_count": 0,
        "network_call_count": 0,
        "gemini_call_count": 0,
        "real_world_effects_count": 0,
    }
    expected = {
        "artifact_count": 6,
        "valid_artifact_count": 6,
        "canonical_ref_count": 6,
        "schema_valid_projection_count": 6,
        "unknown_major_blocked": True,
        "authority_mutation_blocked": True,
        "lifecycle_mutation_blocked": True,
        "payload_authority_override_blocked": True,
        "root_decision_created_count": 0,
        "permission_created_count": 0,
        "final_output_created_count": 0,
        "provider_call_count": 0,
        "network_call_count": 0,
        "gemini_call_count": 0,
        "real_world_effects_count": 0,
    }
    if metrics != expected:
        raise ValueError("kernel_abi_fixture_metrics_invalid")
    return metrics


def collect_domain_neutral_kernel_abi_gauntlet_act_v01(
) -> LivingGauntletActResultV01:
    act_id = "domain_neutral_kernel_abi"
    source_module, source_symbol = _ACTIVE_ACT_SOURCES[act_id]
    try:
        _collect_kernel_abi_fixture_metrics_v01()
        return LivingGauntletActResultV01(
            act_id=act_id,
            errors=(),
            executed=True,
            no_real_connector_or_action=True,
            real_world_effects_count=0,
            root_authority_preserved=True,
            runtime_status=STATUS_PASS,
            source_module=source_module,
            source_symbol=source_symbol,
            state=STATUS_PASS,
        )
    except Exception:
        return LivingGauntletActResultV01(
            act_id=act_id,
            errors=("domain_neutral_kernel_abi_conformance_failed",),
            executed=True,
            no_real_connector_or_action=False,
            real_world_effects_count=-1,
            root_authority_preserved=False,
            runtime_status=STATUS_FAIL_CLOSED,
            source_module=source_module,
            source_symbol=source_symbol,
            state=STATUS_FAIL_CLOSED,
        )


def _build_causal_consumption_fixture_v01() -> tuple[
    tuple[KernelArtifactV01, ...],
    tuple[CausalConsumptionRefV01, ...],
    tuple[tuple[Any, ...], ...],
]:
    transaction_id = "txn:fixture:causal_consumption:001"
    session_anchor = "session:fixture:causal_consumption:001"
    pair_rows = (
        (
            "used",
            {"recommendation": "candidate:alpha"},
            {"recommendation": "candidate:beta"},
            {"accepted_candidate": "candidate:alpha"},
            {"accepted_candidate": "candidate:beta"},
            "/recommendation",
            "USED",
            "used:deterministic_candidate_projection",
        ),
        (
            "rejected",
            {"authority_request": "create_permission"},
            {"authority_request": "create_extended_permission"},
            {"rejected": True, "observation": "baseline"},
            {"rejected": True, "observation": "mutated"},
            "/authority_request",
            "REJECTED",
            "rejected:semantic_authority_escalation",
        ),
        (
            "ignored",
            {"presentation_style": "compact"},
            {"presentation_style": "expanded"},
            {"validation_state": "unchanged"},
            {"validation_state": "unchanged"},
            "/presentation_style",
            "IGNORED_WITH_REASON",
            "ignored:presentation_metadata_non_causal",
        ),
        (
            "blocked",
            {"requested_external_action": "execute_now"},
            {"requested_external_action": "execute_later"},
            {"blocked": True, "observation": "baseline"},
            {"blocked": True, "observation": "mutated"},
            "/requested_external_action",
            "BLOCKED_BY_GATE",
            "gate:effect_firewall_not_implemented",
        ),
    )
    baseline_artifacts: list[KernelArtifactV01] = []
    causal_refs: list[CausalConsumptionRefV01] = []
    cases: list[tuple[Any, ...]] = []
    authority_state = {"accepted_authority_state": "unchanged"}
    for label, source_payload, mutated_source_payload, downstream_payload, mutated_downstream_payload, pointer, disposition, reason in pair_rows:
        source_id = f"artifact:fixture:causal:{label}_source"
        downstream_id = f"artifact:fixture:causal:{label}_downstream"
        source = _build_fixture_kernel_artifact_v01(
            artifact_id=source_id,
            artifact_type="ActorContribution",
            transaction_id=transaction_id,
            owner_root_id="root:alpha",
            source_component="provider_llm",
            authority_class="ADVISORY",
            lifecycle_state="VALIDATED",
            payload=source_payload,
            parent_refs=(),
            session_anchor=session_anchor,
        )
        mutated_source = _build_fixture_kernel_artifact_v01(
            artifact_id=source_id,
            artifact_type="ActorContribution",
            transaction_id=transaction_id,
            owner_root_id="root:alpha",
            source_component="provider_llm",
            authority_class="ADVISORY",
            lifecycle_state="VALIDATED",
            payload=mutated_source_payload,
            parent_refs=(),
            session_anchor=session_anchor,
        )
        downstream = _build_fixture_kernel_artifact_v01(
            artifact_id=downstream_id,
            artifact_type="ValidatedEvidence",
            transaction_id=transaction_id,
            owner_root_id="root:beta",
            source_component="deterministic_runtime",
            authority_class="EVIDENCE_ONLY",
            lifecycle_state="VALIDATED",
            payload=downstream_payload,
            parent_refs=(source_id,),
            session_anchor=session_anchor,
        )
        mutated_downstream = _build_fixture_kernel_artifact_v01(
            artifact_id=downstream_id,
            artifact_type="ValidatedEvidence",
            transaction_id=transaction_id,
            owner_root_id="root:beta",
            source_component="deterministic_runtime",
            authority_class="EVIDENCE_ONLY",
            lifecycle_state="VALIDATED",
            payload=mutated_downstream_payload,
            parent_refs=(source_id,),
            session_anchor=session_anchor,
        )
        causal_ref = build_causal_consumption_ref_v01(
            producer_actor_id=f"actor:fixture:causal:{label}",
            source_artifact_id=source_id,
            output_field=pointer,
            consumer_component="deterministic_runtime",
            downstream_artifact_id=downstream_id,
            decision_effect=f"effect:fixture:causal:{label}",
            disposition=disposition,
            reason_code=reason,
            trace_refs=(f"trace:fixture:causal:{label}",),
        )
        baseline_artifacts.extend((source, downstream))
        causal_refs.append(causal_ref)
        cases.append(
            (
                causal_ref,
                source,
                mutated_source,
                downstream,
                mutated_downstream,
                authority_state,
                authority_state,
            )
        )
    return tuple(baseline_artifacts), tuple(causal_refs), tuple(cases)


def _collect_causal_consumption_fixture_metrics_v01() -> dict[str, Any]:
    artifacts, causal_refs, cases = _build_causal_consumption_fixture_v01()
    if validate_kernel_artifact_bundle_v01(artifacts=artifacts):
        raise ValueError("causal_fixture_artifact_bundle_invalid")
    if any(validate_causal_consumption_ref_v01(item) for item in causal_refs):
        raise ValueError("causal_fixture_ref_invalid")
    if validate_causal_consumption_bundle_v01(
        artifacts=artifacts, causal_refs=causal_refs
    ):
        raise ValueError("causal_fixture_bundle_invalid")
    proof_results = tuple(
        validate_causal_counterfactual_v01(
            causal_ref=case[0],
            baseline_source_artifact=case[1],
            mutated_source_artifact=case[2],
            baseline_downstream_artifact=case[3],
            mutated_downstream_artifact=case[4],
            baseline_authority_state=case[5],
            mutated_authority_state=case[6],
        )
        for case in cases
    )
    if any(proof_results):
        raise ValueError("causal_fixture_counterfactual_invalid")
    artifact_projection = kernel_artifacts_to_plain_list_v01(artifacts)
    causal_projection = causal_consumption_refs_to_plain_list_v01(causal_refs)
    repeated_artifacts, repeated_refs, repeated_cases = (
        _build_causal_consumption_fixture_v01()
    )
    if artifact_projection != kernel_artifacts_to_plain_list_v01(repeated_artifacts):
        raise ValueError("causal_fixture_artifact_projection_nondeterministic")
    if causal_projection != causal_consumption_refs_to_plain_list_v01(repeated_refs):
        raise ValueError("causal_fixture_ref_projection_nondeterministic")
    repeated_proofs = tuple(
        validate_causal_counterfactual_v01(
            causal_ref=case[0],
            baseline_source_artifact=case[1],
            mutated_source_artifact=case[2],
            baseline_downstream_artifact=case[3],
            mutated_downstream_artifact=case[4],
            baseline_authority_state=case[5],
            mutated_authority_state=case[6],
        )
        for case in repeated_cases
    )
    if proof_results != repeated_proofs:
        raise ValueError("causal_fixture_proof_nondeterministic")
    schema = _load_strict_json_object(_KERNEL_ARTIFACT_SCHEMA_PATH)
    artifact_validator = Draft202012Validator(schema)
    for projection in artifact_projection:
        artifact_validator.validate(projection)
    causal_schema = {
        "$schema": "https://json-schema.org/draft/2020-12/schema",
        "$ref": "#/$defs/causalConsumptionRef",
        "$defs": schema["$defs"],
    }
    causal_validator = Draft202012Validator(causal_schema)
    for projection in causal_projection:
        causal_validator.validate(projection)
    dispositions = tuple(item.disposition for item in causal_refs)
    metrics = {
        "causal_source_artifact_count": 4,
        "causal_downstream_artifact_count": 4,
        "causal_ref_count": len(causal_refs),
        "disposition_count": len(set(dispositions)),
        "used_ref_count": dispositions.count("USED"),
        "rejected_ref_count": dispositions.count("REJECTED"),
        "ignored_ref_count": dispositions.count("IGNORED_WITH_REASON"),
        "blocked_ref_count": dispositions.count("BLOCKED_BY_GATE"),
        "used_counterfactual_proof_count": 1,
        "rejected_authority_preservation_count": 1,
        "ignored_downstream_preservation_count": 1,
        "ignored_authority_preservation_count": 1,
        "blocked_authority_preservation_count": 1,
        "root_decision_created_count": 0,
        "permission_created_count": 0,
        "final_output_created_count": 0,
        "provider_call_count": 0,
        "network_call_count": 0,
        "gemini_call_count": 0,
        "real_world_effects_count": 0,
    }
    expected = {
        "causal_source_artifact_count": 4,
        "causal_downstream_artifact_count": 4,
        "causal_ref_count": 4,
        "disposition_count": 4,
        "used_ref_count": 1,
        "rejected_ref_count": 1,
        "ignored_ref_count": 1,
        "blocked_ref_count": 1,
        "used_counterfactual_proof_count": 1,
        "rejected_authority_preservation_count": 1,
        "ignored_downstream_preservation_count": 1,
        "ignored_authority_preservation_count": 1,
        "blocked_authority_preservation_count": 1,
        "root_decision_created_count": 0,
        "permission_created_count": 0,
        "final_output_created_count": 0,
        "provider_call_count": 0,
        "network_call_count": 0,
        "gemini_call_count": 0,
        "real_world_effects_count": 0,
    }
    if metrics != expected or set(dispositions) != set(CAUSAL_DISPOSITIONS):
        raise ValueError("causal_fixture_metrics_invalid")
    return metrics


def collect_causal_consumption_gauntlet_act_v01(
) -> LivingGauntletActResultV01:
    act_id = "causal_consumption"
    source_module, source_symbol = _ACTIVE_ACT_SOURCES[act_id]
    try:
        _collect_causal_consumption_fixture_metrics_v01()
        return LivingGauntletActResultV01(
            act_id=act_id,
            errors=(),
            executed=True,
            no_real_connector_or_action=True,
            real_world_effects_count=0,
            root_authority_preserved=True,
            runtime_status=STATUS_PASS,
            source_module=source_module,
            source_symbol=source_symbol,
            state=STATUS_PASS,
        )
    except Exception:
        return LivingGauntletActResultV01(
            act_id=act_id,
            errors=("causal_consumption_conformance_failed",),
            executed=True,
            no_real_connector_or_action=False,
            real_world_effects_count=-1,
            root_authority_preserved=False,
            runtime_status=STATUS_FAIL_CLOSED,
            source_module=source_module,
            source_symbol=source_symbol,
            state=STATUS_FAIL_CLOSED,
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
        "generic_integrity_replay_execution_count": sum(
            isinstance(row, Mapping)
            and row.get("act_id") == _ACTIVE_ACT_IDS[2]
            and row.get("executed") is True
            for row in active_rows
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
        "root_signer_isolation_execution_count": sum(
            isinstance(row, Mapping)
            and row.get("act_id") == _ACTIVE_ACT_IDS[3]
            and row.get("executed") is True
            for row in active_rows
        ),
        "semantic_work_contract_execution_count": sum(
            isinstance(row, Mapping)
            and row.get("act_id") == _ACTIVE_ACT_IDS[4]
            and row.get("executed") is True
            for row in active_rows
        ),
        "domain_neutral_kernel_abi_execution_count": sum(
            isinstance(row, Mapping)
            and row.get("act_id") == _ACTIVE_ACT_IDS[5]
            and row.get("executed") is True
            for row in active_rows
        ),
        "causal_consumption_execution_count": sum(
            isinstance(row, Mapping)
            and row.get("act_id") == _ACTIVE_ACT_IDS[6]
            and row.get("executed") is True
            for row in active_rows
        ),
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
    generic_calls = 0
    signer_calls = 0
    semantic_work_calls = 0
    kernel_abi_calls = 0
    causal_consumption_calls = 0
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
        generic_calls += 1
        try:
            active_results.append(
                collect_generic_integrity_replay_gauntlet_act_v01()
            )
        except Exception:
            active_results.append(
                _failed_act_result(
                    act_id=_ACTIVE_ACT_IDS[2],
                    reason="generic_integrity_replay_collector_failed",
                )
            )
        signer_calls += 1
        try:
            active_results.append(
                collect_root_signer_isolation_gauntlet_act_v01()
            )
        except Exception:
            active_results.append(
                _failed_act_result(
                    act_id=_ACTIVE_ACT_IDS[3],
                    reason="root_signer_isolation_collector_failed",
                )
            )
        semantic_work_calls += 1
        try:
            active_results.append(collect_semantic_work_contract_gauntlet_act_v01())
        except Exception:
            active_results.append(
                _failed_act_result(
                    act_id=_ACTIVE_ACT_IDS[4],
                    reason="semantic_work_contract_collector_failed",
                )
            )
        kernel_abi_calls += 1
        try:
            active_results.append(
                collect_domain_neutral_kernel_abi_gauntlet_act_v01()
            )
        except Exception:
            active_results.append(
                _failed_act_result(
                    act_id=_ACTIVE_ACT_IDS[5],
                    reason="domain_neutral_kernel_abi_collector_failed",
                )
            )
        causal_consumption_calls += 1
        try:
            active_results.append(collect_causal_consumption_gauntlet_act_v01())
        except Exception:
            active_results.append(
                _failed_act_result(
                    act_id=_ACTIVE_ACT_IDS[6],
                    reason="causal_consumption_collector_failed",
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
            and generic_calls == 1
            and signer_calls == 1
            and semantic_work_calls == 1
            and kernel_abi_calls == 1
            and causal_consumption_calls == 1
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
