"""Execute the deterministic Supplier Water Filter S2 negative matrix.

The runner consumes the accepted public S1 report and calls the committed
Supplier safe-projection and ActionCommitPacket validators directly. It does
not collect semantics, call providers, execute business operations, or read
private attempt evidence.
"""

from __future__ import annotations

from argparse import ArgumentParser
from dataclasses import dataclass, fields, replace
import hashlib
import json
import os
from pathlib import Path
import re
import stat
import sys
from typing import TypeAlias

from demo import run_two_domain_supplier_water_filter_program_v01 as _s1
from hedgehog import action_commit_packet_v02 as _packet
from hedgehog.domains.supplier_water_filter import live_evidence_adapter_v01 as _safe
from hedgehog.kernel.integrity_replay_v01 import (
    canonical_json_bytes_v01,
    domain_separated_sha256_hex_v01,
)


MODULE_ID = "supplier_water_filter_negative_matrix_v01"
RESULT_VERSION = "v0.1"
PROGRAMME_ID = "two_domain_all_real_sealed_evidence_program_v01"
GATE_ID = "two_domain_all_real_sealed_evidence_program_v01_s2_supplier_negative_matrix"
DOMAIN_ID = "supplier_water_filter"
STATUS_PASS = "PASS"
STATUS_FAIL_CLOSED = "FAIL_CLOSED"

ACCEPTED_S1_REPORT_REF = (
    "docs/evidence/two_domain_all_real_sealed_evidence_program_v01/"
    "supplier_water_filter/supplier_safe_execution_report_v01.json"
)
CANONICAL_S2_OUTPUT_REF = (
    "docs/evidence/two_domain_all_real_sealed_evidence_program_v01/"
    "supplier_water_filter/supplier_water_filter_negative_matrix_v01.json"
)
ACCEPTED_S1_REPORT_SHA256 = (
    "293a6ed1f0b943557e2bd33f2ac52f49610e8924574d2784af328d964ba1d666"
)
ACCEPTED_S1_RESULT_ID = (
    "31059f0fa2566cc9040f813680a3c827f41c49f07db6b5885e040a0ed48b8bb5"
)
ACCEPTED_S1_EXECUTION_HEAD = "e1fe7bfc44fe482814b1957840b6d8c434cad5c6"
ACCEPTED_S1_SAFE_EXECUTION_ID = (
    "26a6d430fffded9119c5743796b2cbfccd87f67f6eee57e617a094bc9c41779c"
)
ACCEPTED_SOURCE_CALLS = (6, 6, 6)

MATRIX_SCENARIO_IDS = (
    "S-N1",
    "S-N2",
    "S-C1",
    "S-P1",
    "S-P2",
    "S-F1",
    "S-F2",
    "S-F3",
    "S-M1",
)
MATRIX_SCENARIO_NAMES = (
    "initial_business_blockers_root_not_ready",
    "unsafe_live_evidence_fail_closed",
    "corrected_evidence_validation_rerun",
    "supplier_a_scoped_human_approval",
    "supplier_a_mock_bank_happy_path",
    "no_human_approval_blocks_action",
    "packet_and_corridor_mutation_matrix",
    "receipt_attack_matrix",
    "integrated_mixed_business_outcome",
)
PRESERVED_S1_IDS = ("S-N1", "S-C1", "S-P1", "S-P2", "S-M1")
NEGATIVE_SCENARIO_IDS = ("S-N2", "S-F1", "S-F2", "S-F3")

VALIDATOR_API_NAMES = (
    "validate_supplier_water_filter_safe_execution_projection_v01",
    "validate_action_commit_packet_v02",
    "validate_corridor_no_post_root_reasoning_v01",
    "validate_corridor_step_against_packet_v01",
    "validate_packet_corridor_entry_v02",
    "validate_mock_receipt_evidence_v01",
    "validate_action_commit_packet_registry_v02",
)

_PACKAGE_ROW_SPECS = (
    (
        "S-N1",
        "initial_business_blockers_root_not_ready",
        "deterministic_initial_business_evidence",
        "PASS",
        "NOT_READY",
        "NOT_READY",
        "BLOCKED_PENDING_CORRECTION",
        "ABSENT",
        "NOT_ENTERED",
        "ABSENT",
    ),
    (
        "S-N2",
        "unsafe_live_evidence_fail_closed",
        "live_bound_negative_safe_projection",
        "FAIL_CLOSED",
        "NOT_READY",
        "NO_ACCEPTED_NEW_ROOT_FINAL",
        "BLOCKED_PENDING_CORRECTION",
        "ABSENT",
        "NOT_ENTERED",
        "ABSENT",
    ),
    (
        "S-C1",
        "corrected_evidence_validation_rerun",
        "deterministic_corrected_evidence",
        "PASS",
        "MIXED",
        "SUPPLIER_A_SCOPED_REVIEW_READY",
        "SUPPLIER_A_SCOPED_REVIEW_READY",
        "ABSENT",
        "NOT_ENTERED",
        "ABSENT",
    ),
    (
        "S-P1",
        "supplier_a_scoped_human_approval",
        "deterministic_owner_approval",
        "PASS",
        "MIXED",
        "SUPPLIER_A_SCOPED_REVIEW_READY",
        "APPROVED_SCOPE_ONLY",
        "ROOT_CREATED_SCOPED",
        "NOT_ENTERED",
        "ABSENT",
    ),
    (
        "S-P2",
        "supplier_a_mock_bank_happy_path",
        "live_bound_deterministic_corridor",
        "PASS",
        "MIXED",
        "SUPPLIER_A_SCOPED_REVIEW_READY",
        "PASS",
        "VALID_SCOPED",
        "PASS",
        "EVIDENCE_ONLY",
    ),
    (
        "S-F1",
        "no_human_approval_blocks_action",
        "deterministic_policy_probe",
        "FAIL_CLOSED",
        "NOT_READY",
        "NO_ACTION_APPROVAL",
        "NOT_EXECUTED",
        "REJECTED",
        "NOT_ENTERED",
        "ABSENT",
    ),
    (
        "S-F2",
        "packet_and_corridor_mutation_matrix",
        "deterministic_packet_corridor_mutation",
        "FAIL_CLOSED",
        "MIXED",
        "NO_WIDENED_ROOT_DECISION",
        "UNCHANGED",
        "REJECTED",
        "REJECTED",
        "ABSENT",
    ),
    (
        "S-F3",
        "receipt_attack_matrix",
        "deterministic_receipt_attack",
        "FAIL_CLOSED",
        "MIXED",
        "NO_NEW_PERMISSION",
        "UNCHANGED",
        "UNCHANGED",
        "NO_NEW_EXECUTION",
        "ATTACK_REJECTED",
    ),
    (
        "S-M1",
        "integrated_mixed_business_outcome",
        "deterministic_integrated_outcome",
        "PASS",
        "MIXED",
        "HELD",
        "PASS",
        "VALID_SCOPED",
        "PASS",
        "EVIDENCE_ONLY",
    ),
)

REASON_INVALID = "supplier_s2_negative_matrix_invalid"
REASON_SOURCE_INVALID = "supplier_s2_accepted_source_invalid"
REASON_PROBE_ACCEPTED = "supplier_s2_negative_probe_accepted"
REASON_REASON_MISMATCH = "supplier_s2_negative_reason_mismatch"
REASON_PATH_INVALID = "supplier_s2_path_invalid"
REASON_OUTPUT_EXISTS = "supplier_s2_output_exists"
REASON_WRITE_FAILED = "supplier_s2_output_write_failed"
REASON_FAIL_CLOSED = "supplier_s2_fail_closed"

_PROBE_DOMAIN = "hedgehog-os:supplier-water-filter-s2-probe:v0.1"
_NEGATIVE_SCENARIO_DOMAIN = (
    "hedgehog-os:supplier-water-filter-s2-negative-scenario:v0.1"
)
_RESULT_DOMAIN = "hedgehog-os:supplier-water-filter-s2-result:v0.1"
_LOWER_SHA256 = re.compile(r"^[0-9a-f]{64}$")
_MAX_SOURCE_BYTES = 256 * 1024


@dataclass(frozen=True, slots=True)
class SupplierS2ValidatorProbeV01:
    probe_id: str
    probe_name: str
    validator_api: str
    mutation_class: str
    mutation_fields: tuple[str, ...]
    baseline_status: str
    attack_status: str
    proof_status: str
    reason_codes: tuple[str, ...]
    source_safe_execution_id: str
    provider_call_count: int
    network_call_count: int
    gemini_call_count: int
    real_world_effects_count: int


@dataclass(frozen=True, slots=True)
class SupplierS2NegativeScenarioResultV01:
    scenario_result_id: str
    scenario_id: str
    scenario_name: str
    attack_status: str
    proof_status: str
    business_outcome: str
    root_status: str
    supplier_a_status: str
    supplier_b_status: str
    shipment_status: str
    packet_status: str
    corridor_status: str
    receipt_status: str
    additional_provider_call_count: int
    additional_network_call_count: int
    additional_gemini_call_count: int
    real_payment_executed: bool
    real_shipment_released: bool
    real_world_effects_count: int
    evidence_refs: tuple[str, ...]
    validated_facts: tuple[str, ...]
    probes: tuple[SupplierS2ValidatorProbeV01, ...]


MatrixRow: TypeAlias = (
    _s1.SupplierS1ScenarioResultV01 | SupplierS2NegativeScenarioResultV01
)


@dataclass(frozen=True, slots=True)
class SupplierS2PackageAdapterScenarioRowV01:
    scenario_id: str
    scenario_name: str
    classification: str
    technical_status: str
    business_outcome: str
    root_status: str
    supplier_a_status: str
    supplier_b_status: str
    shipment_status: str
    packet_status: str
    corridor_status: str
    receipt_status: str
    additional_provider_call_count: int
    additional_network_call_count: int
    additional_gemini_call_count: int
    real_payment_executed: bool
    real_shipment_released: bool
    real_world_effects_count: int
    evidence_refs: tuple[str, ...]


@dataclass(frozen=True, slots=True)
class SupplierS2NegativeMatrixResultV01:
    result_id: str
    result_version: str
    programme_id: str
    gate_id: str
    domain_id: str
    implementation_sha256: str
    accepted_s1_report_ref: str
    accepted_s1_report_sha256: str
    accepted_s1_result_id: str
    accepted_s1_execution_head: str
    accepted_s1_safe_execution_id: str
    accepted_s1_provider_call_count: int
    accepted_s1_network_call_count: int
    accepted_s1_gemini_call_count: int
    s2_provider_call_count: int
    s2_network_call_count: int
    s2_gemini_call_count: int
    s2_real_world_effects_count: int
    s2_collector_invocation_count: int
    s2_duplicate_live_source_count: int
    s2_retry_count: int
    scenario_rows: tuple[MatrixRow, ...]
    package_adapter_scenario_rows: tuple[
        SupplierS2PackageAdapterScenarioRowV01, ...
    ]
    negative_probe_ids: tuple[str, ...]
    invoked_validator_api_names: tuple[str, ...]
    supplier_b_status: str
    shipment_status: str
    receipt_status: str
    real_payment_executed: bool
    real_shipment_released: bool
    final_status: str
    validation_errors: tuple[str, ...]


@dataclass(frozen=True, slots=True)
class _AcceptedS1Source:
    report_sha256: str
    result: _s1.SupplierS1ProgramResultV01
    safe_execution: _safe.SupplierWaterFilterSafeExecutionProjectionV01


class _RunError(Exception):
    pass


def _identity(domain: str, plain: object) -> str:
    return domain_separated_sha256_hex_v01(
        domain=domain,
        payload=canonical_json_bytes_v01(plain),
    )


def _probe_plain(
    probe: SupplierS2ValidatorProbeV01,
    *,
    zero_id: bool = False,
) -> dict[str, object]:
    return {
        "attack_status": probe.attack_status,
        "baseline_status": probe.baseline_status,
        "gemini_call_count": probe.gemini_call_count,
        "mutation_class": probe.mutation_class,
        "mutation_fields": list(probe.mutation_fields),
        "network_call_count": probe.network_call_count,
        "probe_id": "0" * 64 if zero_id else probe.probe_id,
        "probe_name": probe.probe_name,
        "proof_status": probe.proof_status,
        "provider_call_count": probe.provider_call_count,
        "real_world_effects_count": probe.real_world_effects_count,
        "reason_codes": list(probe.reason_codes),
        "source_safe_execution_id": probe.source_safe_execution_id,
        "validator_api": probe.validator_api,
    }


def _negative_scenario_plain(
    scenario: SupplierS2NegativeScenarioResultV01,
    *,
    zero_id: bool = False,
) -> dict[str, object]:
    return {
        "additional_gemini_call_count": scenario.additional_gemini_call_count,
        "additional_network_call_count": scenario.additional_network_call_count,
        "additional_provider_call_count": scenario.additional_provider_call_count,
        "attack_status": scenario.attack_status,
        "business_outcome": scenario.business_outcome,
        "corridor_status": scenario.corridor_status,
        "evidence_refs": list(scenario.evidence_refs),
        "packet_status": scenario.packet_status,
        "probes": [_probe_plain(item) for item in scenario.probes],
        "proof_status": scenario.proof_status,
        "real_payment_executed": scenario.real_payment_executed,
        "real_shipment_released": scenario.real_shipment_released,
        "real_world_effects_count": scenario.real_world_effects_count,
        "receipt_status": scenario.receipt_status,
        "root_status": scenario.root_status,
        "scenario_id": scenario.scenario_id,
        "scenario_name": scenario.scenario_name,
        "scenario_result_id": "0" * 64 if zero_id else scenario.scenario_result_id,
        "shipment_status": scenario.shipment_status,
        "supplier_a_status": scenario.supplier_a_status,
        "supplier_b_status": scenario.supplier_b_status,
        "validated_facts": list(scenario.validated_facts),
    }


def _s1_scenario_plain(
    scenario: _s1.SupplierS1ScenarioResultV01,
) -> dict[str, object]:
    return {
        "additional_gemini_call_count": scenario.additional_gemini_call_count,
        "additional_network_call_count": scenario.additional_network_call_count,
        "additional_provider_call_count": scenario.additional_provider_call_count,
        "business_outcome": scenario.business_outcome,
        "corridor_status": scenario.corridor_status,
        "evidence_refs": list(scenario.evidence_refs),
        "packet_status": scenario.packet_status,
        "real_payment_executed": scenario.real_payment_executed,
        "real_shipment_released": scenario.real_shipment_released,
        "real_world_effects_count": scenario.real_world_effects_count,
        "receipt_status": scenario.receipt_status,
        "root_status": scenario.root_status,
        "scenario_id": scenario.scenario_id,
        "scenario_name": scenario.scenario_name,
        "scenario_result_id": scenario.scenario_result_id,
        "shipment_status": scenario.shipment_status,
        "supplier_a_status": scenario.supplier_a_status,
        "supplier_b_status": scenario.supplier_b_status,
        "validated_facts": list(scenario.validated_facts),
        "validation_status": scenario.validation_status,
    }


def _row_plain(row: MatrixRow) -> dict[str, object]:
    if type(row) is _s1.SupplierS1ScenarioResultV01:
        return _s1_scenario_plain(row)
    if type(row) is SupplierS2NegativeScenarioResultV01:
        return _negative_scenario_plain(row)
    raise ValueError(REASON_INVALID)


def _package_adapter_row_plain(
    row: SupplierS2PackageAdapterScenarioRowV01,
    *,
    serialized: bool,
) -> dict[str, object]:
    return {
        "additional_gemini_call_count": row.additional_gemini_call_count,
        "additional_network_call_count": row.additional_network_call_count,
        "additional_provider_call_count": row.additional_provider_call_count,
        "business_outcome": row.business_outcome,
        "classification": row.classification,
        "corridor_status": row.corridor_status,
        "evidence_refs": list(row.evidence_refs) if serialized else row.evidence_refs,
        "packet_status": row.packet_status,
        "real_payment_executed": row.real_payment_executed,
        "real_shipment_released": row.real_shipment_released,
        "real_world_effects_count": row.real_world_effects_count,
        "receipt_status": row.receipt_status,
        "root_status": row.root_status,
        "scenario_id": row.scenario_id,
        "scenario_name": row.scenario_name,
        "shipment_status": row.shipment_status,
        "supplier_a_status": row.supplier_a_status,
        "supplier_b_status": row.supplier_b_status,
        "technical_status": row.technical_status,
    }


def _result_plain(
    result: SupplierS2NegativeMatrixResultV01,
    *,
    zero_id: bool = False,
) -> dict[str, object]:
    return {
        "accepted_s1_execution_head": result.accepted_s1_execution_head,
        "accepted_s1_gemini_call_count": result.accepted_s1_gemini_call_count,
        "accepted_s1_network_call_count": result.accepted_s1_network_call_count,
        "accepted_s1_provider_call_count": result.accepted_s1_provider_call_count,
        "accepted_s1_report_ref": result.accepted_s1_report_ref,
        "accepted_s1_report_sha256": result.accepted_s1_report_sha256,
        "accepted_s1_result_id": result.accepted_s1_result_id,
        "accepted_s1_safe_execution_id": result.accepted_s1_safe_execution_id,
        "domain_id": result.domain_id,
        "final_status": result.final_status,
        "gate_id": result.gate_id,
        "implementation_sha256": result.implementation_sha256,
        "invoked_validator_api_names": list(result.invoked_validator_api_names),
        "negative_probe_ids": list(result.negative_probe_ids),
        "package_adapter_scenario_rows": [
            _package_adapter_row_plain(item, serialized=True)
            for item in result.package_adapter_scenario_rows
        ],
        "programme_id": result.programme_id,
        "real_payment_executed": result.real_payment_executed,
        "real_shipment_released": result.real_shipment_released,
        "receipt_status": result.receipt_status,
        "result_id": "0" * 64 if zero_id else result.result_id,
        "result_version": result.result_version,
        "s2_collector_invocation_count": result.s2_collector_invocation_count,
        "s2_duplicate_live_source_count": result.s2_duplicate_live_source_count,
        "s2_gemini_call_count": result.s2_gemini_call_count,
        "s2_network_call_count": result.s2_network_call_count,
        "s2_provider_call_count": result.s2_provider_call_count,
        "s2_real_world_effects_count": result.s2_real_world_effects_count,
        "s2_retry_count": result.s2_retry_count,
        "scenario_rows": [_row_plain(item) for item in result.scenario_rows],
        "shipment_status": result.shipment_status,
        "supplier_b_status": result.supplier_b_status,
        "validation_errors": list(result.validation_errors),
    }


def _build_probe(
    *,
    probe_name: str,
    validator_api: str,
    mutation_class: str,
    mutation_fields: tuple[str, ...],
    reasons: tuple[str, ...],
    required_reasons: tuple[str, ...],
    source_safe_execution_id: str,
) -> SupplierS2ValidatorProbeV01:
    if not reasons:
        raise ValueError(REASON_PROBE_ACCEPTED)
    if any(reason not in reasons for reason in required_reasons):
        raise ValueError(REASON_REASON_MISMATCH)
    provisional = SupplierS2ValidatorProbeV01(
        probe_id="0" * 64,
        probe_name=probe_name,
        validator_api=validator_api,
        mutation_class=mutation_class,
        mutation_fields=mutation_fields,
        baseline_status=STATUS_PASS,
        attack_status=STATUS_FAIL_CLOSED,
        proof_status=STATUS_PASS,
        reason_codes=reasons,
        source_safe_execution_id=source_safe_execution_id,
        provider_call_count=0,
        network_call_count=0,
        gemini_call_count=0,
        real_world_effects_count=0,
    )
    return replace(
        provisional,
        probe_id=_identity(_PROBE_DOMAIN, _probe_plain(provisional, zero_id=True)),
    )


def _build_negative_scenario(
    *,
    scenario_id: str,
    scenario_name: str,
    business_outcome: str,
    root_status: str,
    supplier_a_status: str,
    packet_status: str,
    corridor_status: str,
    receipt_status: str,
    evidence_refs: tuple[str, ...],
    validated_facts: tuple[str, ...],
    probes: tuple[SupplierS2ValidatorProbeV01, ...],
) -> SupplierS2NegativeScenarioResultV01:
    if not probes or any(item.proof_status != STATUS_PASS for item in probes):
        raise ValueError(REASON_INVALID)
    provisional = SupplierS2NegativeScenarioResultV01(
        scenario_result_id="0" * 64,
        scenario_id=scenario_id,
        scenario_name=scenario_name,
        attack_status=STATUS_FAIL_CLOSED,
        proof_status=STATUS_PASS,
        business_outcome=business_outcome,
        root_status=root_status,
        supplier_a_status=supplier_a_status,
        supplier_b_status="BLOCKED",
        shipment_status="HELD",
        packet_status=packet_status,
        corridor_status=corridor_status,
        receipt_status=receipt_status,
        additional_provider_call_count=0,
        additional_network_call_count=0,
        additional_gemini_call_count=0,
        real_payment_executed=False,
        real_shipment_released=False,
        real_world_effects_count=0,
        evidence_refs=evidence_refs,
        validated_facts=validated_facts,
        probes=probes,
    )
    return replace(
        provisional,
        scenario_result_id=_identity(
            _NEGATIVE_SCENARIO_DOMAIN,
            _negative_scenario_plain(provisional, zero_id=True),
        ),
    )


def _safe_projection_probes(
    source: _AcceptedS1Source,
) -> tuple[SupplierS2ValidatorProbeV01, ...]:
    baseline = source.safe_execution
    if _safe.validate_supplier_water_filter_safe_execution_projection_v01(baseline):
        raise ValueError(REASON_SOURCE_INVALID)
    cases = (
        (
            "s_n2_raw_prompt_inclusion",
            replace(baseline, raw_prompt_included=True),
            ("raw_prompt_included",),
            ("supplier_water_filter_safe_execution_raw_material_forbidden",),
        ),
        (
            "s_n2_failed_secret_scan",
            replace(baseline, secret_scan_passed=False),
            ("secret_scan_passed",),
            ("supplier_water_filter_safe_execution_secret_scan_required",),
        ),
        (
            "s_n2_nonzero_effect",
            replace(baseline, real_world_effects_count=1),
            ("real_world_effects_count",),
            ("supplier_water_filter_safe_execution_effect_forbidden",),
        ),
        (
            "s_n2_invalid_call_geometry",
            replace(baseline, provider_call_count=7),
            ("provider_call_count",),
            ("supplier_water_filter_safe_execution_call_geometry_invalid",),
        ),
    )
    return tuple(
        _build_probe(
            probe_name=name,
            validator_api="validate_supplier_water_filter_safe_execution_projection_v01",
            mutation_class="SupplierWaterFilterSafeExecutionProjectionV01",
            mutation_fields=mutation_fields,
            reasons=_safe.validate_supplier_water_filter_safe_execution_projection_v01(
                mutated
            ),
            required_reasons=required,
            source_safe_execution_id=source.safe_execution.safe_execution_id,
        )
        for name, mutated, mutation_fields, required in cases
    )


def _packet_approval_probes(
    source: _AcceptedS1Source,
) -> tuple[SupplierS2ValidatorProbeV01, ...]:
    packet = _packet.build_supplier_a_mock_action_commit_packet_fixture_v02()
    valid, reasons = _packet.validate_action_commit_packet_v02(packet)
    if not valid or reasons:
        raise ValueError(REASON_SOURCE_INVALID)
    changed = replace(packet, human_approval_ref="")
    attack_valid, attack_reasons = _packet.validate_action_commit_packet_v02(changed)
    if attack_valid:
        raise ValueError(REASON_PROBE_ACCEPTED)
    if attack_reasons != (_packet.REASON_MISSING_HUMAN_APPROVAL_REF,):
        raise ValueError(REASON_REASON_MISMATCH)
    return (
        _build_probe(
            probe_name="s_f1_missing_human_approval",
            validator_api="validate_action_commit_packet_v02",
            mutation_class="ActionCommitPacketV02",
            mutation_fields=("human_approval_ref",),
            reasons=attack_reasons,
            required_reasons=(_packet.REASON_MISSING_HUMAN_APPROVAL_REF,),
            source_safe_execution_id=source.safe_execution.safe_execution_id,
        ),
    )


def _packet_corridor_probes(
    source: _AcceptedS1Source,
) -> tuple[SupplierS2ValidatorProbeV01, ...]:
    packet, corridor, step, registry = (
        _packet.build_supplier_a_packet_corridor_validation_fixture_v02()
    )
    packet_valid, packet_reasons = _packet.validate_action_commit_packet_v02(packet)
    corridor_valid, corridor_reasons = (
        _packet.validate_corridor_no_post_root_reasoning_v01(corridor)
    )
    step_report = _packet.validate_corridor_step_against_packet_v01(packet, step)
    entry_report = _packet.validate_packet_corridor_entry_v02(
        packet,
        corridor,
        step,
        registry,
    )
    if (
        not packet_valid
        or packet_reasons
        or not corridor_valid
        or corridor_reasons
        or step_report.validation_status != STATUS_PASS
        or step_report.reason_codes
        or entry_report.validation_status != STATUS_PASS
        or entry_report.reason_codes
    ):
        raise ValueError(REASON_SOURCE_INVALID)

    supplier_b_scope = replace(
        packet.scope,
        allowed_subjects=(*packet.scope.allowed_subjects, _packet.SUBJECT_SUPPLIER_B),
    )
    shipment_scope = replace(
        packet.scope,
        allowed_actions=(*packet.scope.allowed_actions, _packet.ACTION_SHIPMENT_RELEASE),
    )
    packet_cases = (
        (
            "s_f2_packet_supplier_b_scope_widening",
            replace(packet, scope=supplier_b_scope),
            ("scope.allowed_subjects",),
            (_packet.REASON_SUPPLIER_B_SCOPE_FORBIDDEN,),
        ),
        (
            "s_f2_packet_shipment_scope_widening",
            replace(packet, scope=shipment_scope),
            ("scope.allowed_actions",),
            (_packet.REASON_SHIPMENT_RELEASE_FORBIDDEN,),
        ),
    )
    probes: list[SupplierS2ValidatorProbeV01] = []
    for name, changed, mutation_fields, required in packet_cases:
        valid, reasons = _packet.validate_action_commit_packet_v02(changed)
        if valid:
            raise ValueError(REASON_PROBE_ACCEPTED)
        probes.append(
            _build_probe(
                probe_name=name,
                validator_api="validate_action_commit_packet_v02",
                mutation_class="ActionCommitPacketV02",
                mutation_fields=mutation_fields,
                reasons=reasons,
                required_reasons=required,
                source_safe_execution_id=source.safe_execution.safe_execution_id,
            )
        )

    step_cases = (
        (
            "s_f2_corridor_supplier_b_scope_widening",
            replace(
                step,
                allowed_subjects=(*step.allowed_subjects, _packet.SUBJECT_SUPPLIER_B),
            ),
            ("allowed_subjects",),
        ),
        (
            "s_f2_corridor_shipment_scope_widening",
            replace(
                step,
                allowed_actions=(*step.allowed_actions, _packet.ACTION_SHIPMENT_RELEASE),
            ),
            ("allowed_actions",),
        ),
    )
    required = (
        _packet.REASON_CHILD_ALLOWED_NOT_SUBSET_OF_PARENT,
        _packet.REASON_CHILD_SCOPE_NOT_SUBSET_OF_PARENT,
    )
    for name, changed, mutation_fields in step_cases:
        report = _packet.validate_corridor_step_against_packet_v01(packet, changed)
        if report.validation_status != STATUS_FAIL_CLOSED:
            raise ValueError(REASON_PROBE_ACCEPTED)
        probes.append(
            _build_probe(
                probe_name=name,
                validator_api="validate_corridor_step_against_packet_v01",
                mutation_class="CorridorStepV01",
                mutation_fields=mutation_fields,
                reasons=report.reason_codes,
                required_reasons=required,
                source_safe_execution_id=source.safe_execution.safe_execution_id,
            )
        )
    return tuple(probes)


def _receipt_registry_probes(
    source: _AcceptedS1Source,
) -> tuple[SupplierS2ValidatorProbeV01, ...]:
    packet = _packet.build_supplier_a_mock_action_commit_packet_fixture_v02()
    packet_valid, packet_reasons = _packet.validate_action_commit_packet_v02(packet)
    receipt = _packet.build_supplier_a_mock_receipt_evidence_fixture_v01(packet)
    receipt_valid, receipt_reasons = _packet.validate_mock_receipt_evidence_v01(
        packet,
        receipt,
    )
    registry = _packet.build_empty_action_commit_packet_registry_v02()
    registry_valid, registry_reasons = (
        _packet.validate_action_commit_packet_registry_v02(registry)
    )
    if (
        not packet_valid
        or packet_reasons
        or not receipt_valid
        or receipt_reasons
        or not registry_valid
        or registry_reasons
    ):
        raise ValueError(REASON_SOURCE_INVALID)

    receipt_cases = (
        (
            "s_f3_receipt_future_permission",
            replace(receipt, creates_future_permission=True),
            ("creates_future_permission",),
            (_packet.REASON_RECEIPT_CANNOT_CREATE_FUTURE_PERMISSION,),
        ),
        (
            "s_f3_receipt_supplier_b_authority",
            replace(receipt, authorizes_supplier_b=True),
            ("authorizes_supplier_b",),
            (_packet.REASON_RECEIPT_CANNOT_AUTHORIZE_SUPPLIER_B,),
        ),
        (
            "s_f3_receipt_final_output",
            replace(receipt, creates_final_output=True),
            ("creates_final_output",),
            (_packet.REASON_NO_EXPANSION_AFTER_ROOT,),
        ),
        (
            "s_f3_receipt_shipment_release",
            replace(receipt, releases_shipment=True),
            ("releases_shipment",),
            (_packet.REASON_RECEIPT_CANNOT_RELEASE_SHIPMENT,),
        ),
    )
    probes: list[SupplierS2ValidatorProbeV01] = []
    for name, changed, mutation_fields, required in receipt_cases:
        valid, reasons = _packet.validate_mock_receipt_evidence_v01(packet, changed)
        if valid:
            raise ValueError(REASON_PROBE_ACCEPTED)
        probes.append(
            _build_probe(
                probe_name=name,
                validator_api="validate_mock_receipt_evidence_v01",
                mutation_class="MockReceiptEvidenceV01",
                mutation_fields=mutation_fields,
                reasons=reasons,
                required_reasons=required,
                source_safe_execution_id=source.safe_execution.safe_execution_id,
            )
        )

    registry_cases = (
        (
            "s_f3_registry_future_permission",
            replace(registry, creates_permission=True),
            ("creates_permission",),
            (
                _packet.REASON_REGISTRY_IS_NOT_PERMISSION,
                _packet.REASON_REGISTRY_IS_NOT_AUTHORITY,
            ),
        ),
        (
            "s_f3_registry_shipment_release",
            replace(registry, releases_shipment=True),
            ("releases_shipment",),
            (_packet.REASON_REGISTRY_CANNOT_RELEASE_SHIPMENT,),
        ),
    )
    for name, changed, mutation_fields, required in registry_cases:
        valid, reasons = _packet.validate_action_commit_packet_registry_v02(changed)
        if valid:
            raise ValueError(REASON_PROBE_ACCEPTED)
        probes.append(
            _build_probe(
                probe_name=name,
                validator_api="validate_action_commit_packet_registry_v02",
                mutation_class="ActionCommitPacketRegistryV02",
                mutation_fields=mutation_fields,
                reasons=reasons,
                required_reasons=required,
                source_safe_execution_id=source.safe_execution.safe_execution_id,
            )
        )
    return tuple(probes)


def _build_matrix(source: _AcceptedS1Source) -> tuple[MatrixRow, ...]:
    by_id = {item.scenario_id: item for item in source.result.scenarios}
    if tuple(by_id) != PRESERVED_S1_IDS or len(by_id) != 5:
        raise ValueError(REASON_SOURCE_INVALID)

    s_n2 = _build_negative_scenario(
        scenario_id="S-N2",
        scenario_name=MATRIX_SCENARIO_NAMES[1],
        business_outcome="UNCHANGED",
        root_status="NO_ACCEPTED_NEW_ROOT_FINAL",
        supplier_a_status="UNCHANGED",
        packet_status="ABSENT",
        corridor_status="NOT_ENTERED",
        receipt_status="ABSENT",
        evidence_refs=(
            f"accepted_s1_safe_execution:{source.safe_execution.safe_execution_id}",
            "validator:validate_supplier_water_filter_safe_execution_projection_v01",
        ),
        validated_facts=(
            "single_accepted_live_source_bound",
            "unsafe_safe_projection_rejected",
            "no_new_root_packet_corridor_or_receipt",
        ),
        probes=_safe_projection_probes(source),
    )
    s_f1 = _build_negative_scenario(
        scenario_id="S-F1",
        scenario_name=MATRIX_SCENARIO_NAMES[5],
        business_outcome="UNCHANGED",
        root_status="NO_ACTION_APPROVAL",
        supplier_a_status="NOT_EXECUTED",
        packet_status="REJECTED",
        corridor_status="NOT_ENTERED",
        receipt_status="ABSENT",
        evidence_refs=(
            "validator:validate_action_commit_packet_v02",
            "baseline:root_created_supplier_a_packet_v02",
        ),
        validated_facts=(
            "baseline_packet_valid",
            "missing_human_approval_rejected",
            "no_action_permission_created",
        ),
        probes=_packet_approval_probes(source),
    )
    s_f2 = _build_negative_scenario(
        scenario_id="S-F2",
        scenario_name=MATRIX_SCENARIO_NAMES[6],
        business_outcome="UNCHANGED",
        root_status="NO_WIDENED_ROOT_DECISION",
        supplier_a_status="UNCHANGED",
        packet_status="REJECTED",
        corridor_status="REJECTED",
        receipt_status="ABSENT",
        evidence_refs=(
            "validator:validate_action_commit_packet_v02",
            "validator:validate_corridor_step_against_packet_v01",
            "baseline:supplier_a_packet_corridor_v02",
        ),
        validated_facts=(
            "baseline_packet_valid",
            "baseline_corridor_valid",
            "supplier_b_scope_widening_rejected",
            "shipment_scope_widening_rejected",
        ),
        probes=_packet_corridor_probes(source),
    )
    s_f3 = _build_negative_scenario(
        scenario_id="S-F3",
        scenario_name=MATRIX_SCENARIO_NAMES[7],
        business_outcome="UNCHANGED",
        root_status="NO_NEW_PERMISSION",
        supplier_a_status="UNCHANGED",
        packet_status="UNCHANGED_VALID_SCOPED",
        corridor_status="NO_NEW_EXECUTION",
        receipt_status="EVIDENCE_ONLY",
        evidence_refs=(
            "validator:validate_mock_receipt_evidence_v01",
            "validator:validate_action_commit_packet_registry_v02",
            "baseline:supplier_a_mock_receipt_evidence_v01",
        ),
        validated_facts=(
            "baseline_receipt_valid",
            "future_permission_attack_rejected",
            "supplier_b_authority_attack_rejected",
            "final_output_attack_rejected",
            "shipment_release_attack_rejected",
        ),
        probes=_receipt_registry_probes(source),
    )
    return (
        by_id["S-N1"],
        s_n2,
        by_id["S-C1"],
        by_id["S-P1"],
        by_id["S-P2"],
        s_f1,
        s_f2,
        s_f3,
        by_id["S-M1"],
    )


def _build_package_adapter_scenario_rows(
    matrix: tuple[MatrixRow, ...],
) -> tuple[SupplierS2PackageAdapterScenarioRowV01, ...]:
    if (
        type(matrix) is not tuple
        or len(matrix) != len(_PACKAGE_ROW_SPECS)
        or any(
            type(row)
            not in (
                _s1.SupplierS1ScenarioResultV01,
                SupplierS2NegativeScenarioResultV01,
            )
            for row in matrix
        )
    ):
        raise ValueError(REASON_INVALID)
    rows: list[SupplierS2PackageAdapterScenarioRowV01] = []
    for source_row, spec in zip(matrix, _PACKAGE_ROW_SPECS, strict=True):
        (
            scenario_id,
            scenario_name,
            classification,
            technical_status,
            business_outcome,
            root_status,
            supplier_a_status,
            packet_status,
            corridor_status,
            receipt_status,
        ) = spec
        if (
            source_row.scenario_id != scenario_id
            or source_row.scenario_name != scenario_name
            or source_row.supplier_b_status != "BLOCKED"
            or source_row.shipment_status != "HELD"
            or (
                source_row.additional_provider_call_count,
                source_row.additional_network_call_count,
                source_row.additional_gemini_call_count,
                source_row.real_world_effects_count,
            )
            != (0, 0, 0, 0)
            or source_row.real_payment_executed is not False
            or source_row.real_shipment_released is not False
        ):
            raise ValueError(REASON_INVALID)
        rows.append(
            SupplierS2PackageAdapterScenarioRowV01(
                scenario_id=scenario_id,
                scenario_name=scenario_name,
                classification=classification,
                technical_status=technical_status,
                business_outcome=business_outcome,
                root_status=root_status,
                supplier_a_status=supplier_a_status,
                supplier_b_status="BLOCKED",
                shipment_status="HELD",
                packet_status=packet_status,
                corridor_status=corridor_status,
                receipt_status=receipt_status,
                additional_provider_call_count=0,
                additional_network_call_count=0,
                additional_gemini_call_count=0,
                real_payment_executed=False,
                real_shipment_released=False,
                real_world_effects_count=0,
                evidence_refs=(f"evidence:supplier:{scenario_id.casefold()}",),
            )
        )
    return tuple(rows)


def build_supplier_water_filter_negative_matrix_v01(
    source: _AcceptedS1Source,
) -> SupplierS2NegativeMatrixResultV01:
    if type(source) is not _AcceptedS1Source:
        raise ValueError(REASON_SOURCE_INVALID)
    matrix = _build_matrix(source)
    package_rows = _build_package_adapter_scenario_rows(matrix)
    probe_ids = tuple(
        probe.probe_id
        for row in matrix
        if type(row) is SupplierS2NegativeScenarioResultV01
        for probe in row.probes
    )
    provisional = SupplierS2NegativeMatrixResultV01(
        result_id="0" * 64,
        result_version=RESULT_VERSION,
        programme_id=PROGRAMME_ID,
        gate_id=GATE_ID,
        domain_id=DOMAIN_ID,
        implementation_sha256=_implementation_sha256(),
        accepted_s1_report_ref=ACCEPTED_S1_REPORT_REF,
        accepted_s1_report_sha256=source.report_sha256,
        accepted_s1_result_id=source.result.result_id,
        accepted_s1_execution_head=source.result.execution_head,
        accepted_s1_safe_execution_id=source.safe_execution.safe_execution_id,
        accepted_s1_provider_call_count=source.safe_execution.provider_call_count,
        accepted_s1_network_call_count=source.safe_execution.network_call_count,
        accepted_s1_gemini_call_count=source.safe_execution.gemini_call_count,
        s2_provider_call_count=0,
        s2_network_call_count=0,
        s2_gemini_call_count=0,
        s2_real_world_effects_count=0,
        s2_collector_invocation_count=0,
        s2_duplicate_live_source_count=0,
        s2_retry_count=0,
        scenario_rows=matrix,
        package_adapter_scenario_rows=package_rows,
        negative_probe_ids=probe_ids,
        invoked_validator_api_names=VALIDATOR_API_NAMES,
        supplier_b_status="BLOCKED",
        shipment_status="HELD",
        receipt_status="EVIDENCE_ONLY",
        real_payment_executed=False,
        real_shipment_released=False,
        final_status=STATUS_PASS,
        validation_errors=(),
    )
    result = replace(
        provisional,
        result_id=_identity(_RESULT_DOMAIN, _result_plain(provisional, zero_id=True)),
    )
    if validate_supplier_water_filter_negative_matrix_v01(result, source):
        raise ValueError(REASON_INVALID)
    return result


def _exact_nonempty_string_tuple(value: object) -> bool:
    return (
        type(value) is tuple
        and bool(value)
        and all(type(item) is str and bool(item) for item in value)
    )


def _probe_is_structurally_valid(value: object) -> bool:
    if type(value) is not SupplierS2ValidatorProbeV01:
        return False
    string_values = (
        value.probe_id,
        value.probe_name,
        value.validator_api,
        value.mutation_class,
        value.baseline_status,
        value.attack_status,
        value.proof_status,
        value.source_safe_execution_id,
    )
    counters = (
        value.provider_call_count,
        value.network_call_count,
        value.gemini_call_count,
        value.real_world_effects_count,
    )
    return (
        all(type(item) is str and bool(item) for item in string_values)
        and _LOWER_SHA256.fullmatch(value.probe_id) is not None
        and _LOWER_SHA256.fullmatch(value.source_safe_execution_id) is not None
        and _exact_nonempty_string_tuple(value.mutation_fields)
        and _exact_nonempty_string_tuple(value.reason_codes)
        and all(type(item) is int for item in counters)
    )


def _negative_row_is_structurally_valid(value: object) -> bool:
    if type(value) is not SupplierS2NegativeScenarioResultV01:
        return False
    strings = (
        value.scenario_result_id,
        value.scenario_id,
        value.scenario_name,
        value.attack_status,
        value.proof_status,
        value.business_outcome,
        value.root_status,
        value.supplier_a_status,
        value.supplier_b_status,
        value.shipment_status,
        value.packet_status,
        value.corridor_status,
        value.receipt_status,
    )
    counters = (
        value.additional_provider_call_count,
        value.additional_network_call_count,
        value.additional_gemini_call_count,
        value.real_world_effects_count,
    )
    return (
        all(type(item) is str and bool(item) for item in strings)
        and _LOWER_SHA256.fullmatch(value.scenario_result_id) is not None
        and all(type(item) is int for item in counters)
        and type(value.real_payment_executed) is bool
        and type(value.real_shipment_released) is bool
        and _exact_nonempty_string_tuple(value.evidence_refs)
        and _exact_nonempty_string_tuple(value.validated_facts)
        and type(value.probes) is tuple
        and bool(value.probes)
        and all(_probe_is_structurally_valid(item) for item in value.probes)
    )


def _matrix_is_structurally_valid(value: object) -> bool:
    if type(value) is not tuple or len(value) != len(MATRIX_SCENARIO_IDS):
        return False
    preserved_positions = frozenset((0, 2, 3, 4, 8))
    for index, row in enumerate(value):
        if index in preserved_positions:
            if type(row) is not _s1.SupplierS1ScenarioResultV01:
                return False
        elif not _negative_row_is_structurally_valid(row):
            return False
    return True


def _package_row_is_structurally_valid(value: object) -> bool:
    if type(value) is not SupplierS2PackageAdapterScenarioRowV01:
        return False
    strings = (
        value.scenario_id,
        value.scenario_name,
        value.classification,
        value.technical_status,
        value.business_outcome,
        value.root_status,
        value.supplier_a_status,
        value.supplier_b_status,
        value.shipment_status,
        value.packet_status,
        value.corridor_status,
        value.receipt_status,
    )
    counters = (
        value.additional_provider_call_count,
        value.additional_network_call_count,
        value.additional_gemini_call_count,
        value.real_world_effects_count,
    )
    return (
        all(type(item) is str and bool(item) for item in strings)
        and all(type(item) is int for item in counters)
        and type(value.real_payment_executed) is bool
        and type(value.real_shipment_released) is bool
        and _exact_nonempty_string_tuple(value.evidence_refs)
    )


def _package_rows_are_structurally_valid(value: object) -> bool:
    return (
        type(value) is tuple
        and len(value) == len(_PACKAGE_ROW_SPECS)
        and all(_package_row_is_structurally_valid(item) for item in value)
    )


def _source_is_structurally_valid(value: object) -> bool:
    return (
        type(value) is _AcceptedS1Source
        and type(value.report_sha256) is str
        and _LOWER_SHA256.fullmatch(value.report_sha256) is not None
        and type(value.result) is _s1.SupplierS1ProgramResultV01
        and type(value.safe_execution)
        is _safe.SupplierWaterFilterSafeExecutionProjectionV01
    )


def validate_supplier_water_filter_negative_matrix_v01(
    result: object,
    source: object,
) -> tuple[str, ...]:
    if type(result) is not SupplierS2NegativeMatrixResultV01:
        return (REASON_INVALID,)
    if not _source_is_structurally_valid(source):
        return (REASON_SOURCE_INVALID,)
    errors: list[str] = []
    try:
        source_valid = not (
            _s1.validate_supplier_s1_program_result_v01(source.result)
            or _safe.validate_supplier_water_filter_safe_execution_projection_v01(
                source.safe_execution
            )
        )
        if not source_valid:
            errors.append(REASON_SOURCE_INVALID)

        string_fields = (
            result.result_id,
            result.result_version,
            result.programme_id,
            result.gate_id,
            result.domain_id,
            result.implementation_sha256,
            result.accepted_s1_report_ref,
            result.accepted_s1_report_sha256,
            result.accepted_s1_result_id,
            result.accepted_s1_execution_head,
            result.accepted_s1_safe_execution_id,
            result.supplier_b_status,
            result.shipment_status,
            result.receipt_status,
            result.final_status,
        )
        integer_fields = (
            result.accepted_s1_provider_call_count,
            result.accepted_s1_network_call_count,
            result.accepted_s1_gemini_call_count,
            result.s2_provider_call_count,
            result.s2_network_call_count,
            result.s2_gemini_call_count,
            result.s2_real_world_effects_count,
            result.s2_collector_invocation_count,
            result.s2_duplicate_live_source_count,
            result.s2_retry_count,
        )
        top_level_structure_valid = (
            all(type(value) is str for value in string_fields)
            and all(type(value) is int for value in integer_fields)
            and type(result.real_payment_executed) is bool
            and type(result.real_shipment_released) is bool
            and type(result.negative_probe_ids) is tuple
            and all(type(value) is str for value in result.negative_probe_ids)
            and type(result.invoked_validator_api_names) is tuple
            and all(
                type(value) is str for value in result.invoked_validator_api_names
            )
            and type(result.validation_errors) is tuple
            and all(type(value) is str for value in result.validation_errors)
        )
        matrix_structure_valid = _matrix_is_structurally_valid(result.scenario_rows)
        package_structure_valid = _package_rows_are_structurally_valid(
            result.package_adapter_scenario_rows
        )
        if not (
            top_level_structure_valid
            and matrix_structure_valid
            and package_structure_valid
        ):
            errors.append(REASON_INVALID)

        if top_level_structure_valid:
            if (
                result.result_version != RESULT_VERSION
                or result.programme_id != PROGRAMME_ID
                or result.gate_id != GATE_ID
                or result.domain_id != DOMAIN_ID
                or result.implementation_sha256 != _implementation_sha256()
                or _LOWER_SHA256.fullmatch(result.implementation_sha256) is None
            ):
                errors.append(REASON_INVALID)
            source_bindings = (
                result.accepted_s1_report_ref == ACCEPTED_S1_REPORT_REF,
                result.accepted_s1_report_sha256 == ACCEPTED_S1_REPORT_SHA256,
                result.accepted_s1_result_id == ACCEPTED_S1_RESULT_ID,
                result.accepted_s1_execution_head == ACCEPTED_S1_EXECUTION_HEAD,
                result.accepted_s1_safe_execution_id == ACCEPTED_S1_SAFE_EXECUTION_ID,
                result.accepted_s1_report_sha256 == source.report_sha256,
                result.accepted_s1_result_id == source.result.result_id,
                result.accepted_s1_execution_head == source.result.execution_head,
                result.accepted_s1_safe_execution_id
                == source.safe_execution.safe_execution_id,
                (
                    result.accepted_s1_provider_call_count,
                    result.accepted_s1_network_call_count,
                    result.accepted_s1_gemini_call_count,
                )
                == ACCEPTED_SOURCE_CALLS,
            )
            if not all(source_bindings):
                errors.append(REASON_SOURCE_INVALID)
            if (
                result.s2_provider_call_count,
                result.s2_network_call_count,
                result.s2_gemini_call_count,
                result.s2_real_world_effects_count,
                result.s2_collector_invocation_count,
                result.s2_duplicate_live_source_count,
                result.s2_retry_count,
            ) != (0, 0, 0, 0, 0, 0, 0):
                errors.append(REASON_INVALID)
            if (
                result.invoked_validator_api_names != VALIDATOR_API_NAMES
                or result.supplier_b_status != "BLOCKED"
                or result.shipment_status != "HELD"
                or result.receipt_status != "EVIDENCE_ONLY"
                or result.real_payment_executed is not False
                or result.real_shipment_released is not False
                or result.final_status != STATUS_PASS
                or result.validation_errors != ()
            ):
                errors.append(REASON_INVALID)

        expected_matrix: tuple[MatrixRow, ...] = ()
        if source_valid and matrix_structure_valid:
            expected_matrix = _build_matrix(source)
            if (
                tuple(item.scenario_id for item in result.scenario_rows)
                != MATRIX_SCENARIO_IDS
                or tuple(item.scenario_name for item in result.scenario_rows)
                != MATRIX_SCENARIO_NAMES
                or result.scenario_rows != expected_matrix
            ):
                errors.append(REASON_INVALID)
            for row in result.scenario_rows:
                if type(row) is not SupplierS2NegativeScenarioResultV01:
                    continue
                if (
                    row.attack_status != STATUS_FAIL_CLOSED
                    or row.proof_status != STATUS_PASS
                    or row.supplier_b_status != "BLOCKED"
                    or row.shipment_status != "HELD"
                    or row.real_payment_executed is not False
                    or row.real_shipment_released is not False
                    or (
                        row.additional_provider_call_count,
                        row.additional_network_call_count,
                        row.additional_gemini_call_count,
                        row.real_world_effects_count,
                    )
                    != (0, 0, 0, 0)
                    or row.scenario_result_id
                    != _identity(
                        _NEGATIVE_SCENARIO_DOMAIN,
                        _negative_scenario_plain(row, zero_id=True),
                    )
                ):
                    errors.append(REASON_INVALID)
                for probe in row.probes:
                    if (
                        probe.baseline_status != STATUS_PASS
                        or probe.attack_status != STATUS_FAIL_CLOSED
                        or probe.proof_status != STATUS_PASS
                        or probe.source_safe_execution_id
                        != source.safe_execution.safe_execution_id
                        or (
                            probe.provider_call_count,
                            probe.network_call_count,
                            probe.gemini_call_count,
                            probe.real_world_effects_count,
                        )
                        != (0, 0, 0, 0)
                        or probe.probe_id
                        != _identity(
                            _PROBE_DOMAIN,
                            _probe_plain(probe, zero_id=True),
                        )
                    ):
                        errors.append(REASON_INVALID)

            expected_probe_ids = tuple(
                probe.probe_id
                for row in result.scenario_rows
                if type(row) is SupplierS2NegativeScenarioResultV01
                for probe in row.probes
            )
            if (
                type(result.negative_probe_ids) is not tuple
                or not all(
                    type(value) is str for value in result.negative_probe_ids
                )
                or result.negative_probe_ids != expected_probe_ids
                or len(set(result.negative_probe_ids))
                != len(result.negative_probe_ids)
                or any(
                    _LOWER_SHA256.fullmatch(value) is None
                    for value in result.negative_probe_ids
                )
            ):
                errors.append(REASON_INVALID)

        if matrix_structure_valid and package_structure_valid:
            expected_package_rows = _build_package_adapter_scenario_rows(
                result.scenario_rows
            )
            if result.package_adapter_scenario_rows != expected_package_rows:
                errors.append(REASON_INVALID)

        if (
            top_level_structure_valid
            and matrix_structure_valid
            and package_structure_valid
        ):
            expected_id = _identity(
                _RESULT_DOMAIN,
                _result_plain(result, zero_id=True),
            )
            if (
                result.result_id != expected_id
                or _LOWER_SHA256.fullmatch(result.result_id) is None
            ):
                errors.append(REASON_INVALID)
    except Exception:
        errors.append(REASON_INVALID)
    return tuple(dict.fromkeys(errors))


def supplier_water_filter_negative_matrix_package_rows_v01(
    result: SupplierS2NegativeMatrixResultV01,
    source: _AcceptedS1Source,
) -> tuple[dict[str, object], ...]:
    if validate_supplier_water_filter_negative_matrix_v01(result, source):
        raise ValueError(REASON_INVALID)
    return tuple(
        _package_adapter_row_plain(item, serialized=False)
        for item in result.package_adapter_scenario_rows
    )


def supplier_water_filter_negative_matrix_to_plain_dict_v01(
    result: SupplierS2NegativeMatrixResultV01,
    source: _AcceptedS1Source,
) -> dict[str, object]:
    if validate_supplier_water_filter_negative_matrix_v01(result, source):
        raise ValueError(REASON_INVALID)
    plain = _result_plain(result)
    canonical_json_bytes_v01(plain)
    return plain


def _strict_object_pairs(pairs: list[tuple[str, object]]) -> dict[str, object]:
    result: dict[str, object] = {}
    for key, value in pairs:
        if key in result:
            raise ValueError(REASON_SOURCE_INVALID)
        result[key] = value
    return result


def _reject_nonfinite(_: str) -> object:
    raise ValueError(REASON_SOURCE_INVALID)


def _strict_json(content: bytes) -> dict[str, object]:
    if (
        not content
        or len(content) > _MAX_SOURCE_BYTES
        or b"\x00" in content
        or b"\r" in content
        or content.startswith(b"\xef\xbb\xbf")
        or not content.endswith(b"\n")
        or content.endswith(b"\n\n")
    ):
        raise ValueError(REASON_SOURCE_INVALID)
    try:
        text = content[:-1].decode("utf-8", errors="strict")
        value = json.loads(
            text,
            object_pairs_hook=_strict_object_pairs,
            parse_constant=_reject_nonfinite,
        )
    except (UnicodeError, json.JSONDecodeError, ValueError):
        raise ValueError(REASON_SOURCE_INVALID) from None
    if type(value) is not dict or canonical_json_bytes_v01(value) + b"\n" != content:
        raise ValueError(REASON_SOURCE_INVALID)
    return value


def _exact_list(value: object, item_type: type, *, allow_empty: bool = True) -> tuple[object, ...]:
    if type(value) is not list or (not allow_empty and not value):
        raise ValueError(REASON_SOURCE_INVALID)
    if any(type(item) is not item_type for item in value):
        raise ValueError(REASON_SOURCE_INVALID)
    return tuple(value)


def _hydrate_s1_scenario(value: object) -> _s1.SupplierS1ScenarioResultV01:
    expected = {item.name for item in fields(_s1.SupplierS1ScenarioResultV01)}
    if type(value) is not dict or set(value) != expected:
        raise ValueError(REASON_SOURCE_INVALID)
    values = dict(value)
    values["evidence_refs"] = _exact_list(values["evidence_refs"], str, allow_empty=False)
    values["validated_facts"] = _exact_list(
        values["validated_facts"],
        str,
        allow_empty=False,
    )
    try:
        return _s1.SupplierS1ScenarioResultV01(**values)
    except (TypeError, ValueError):
        raise ValueError(REASON_SOURCE_INVALID) from None


def _hydrate_s1_result(value: dict[str, object]) -> _s1.SupplierS1ProgramResultV01:
    expected = {item.name for item in fields(_s1.SupplierS1ProgramResultV01)}
    if set(value) != expected:
        raise ValueError(REASON_SOURCE_INVALID)
    values = dict(value)
    for name in ("actor_ids", "actor_validation_statuses", "actor_safe_summaries"):
        values[name] = _exact_list(values[name], str, allow_empty=False)
    values["validation_errors"] = _exact_list(values["validation_errors"], str)
    rows = values["scenarios"]
    if type(rows) is not list:
        raise ValueError(REASON_SOURCE_INVALID)
    values["scenarios"] = tuple(_hydrate_s1_scenario(item) for item in rows)
    try:
        result = _s1.SupplierS1ProgramResultV01(**values)
    except (TypeError, ValueError):
        raise ValueError(REASON_SOURCE_INVALID) from None
    if _s1.validate_supplier_s1_program_result_v01(result):
        raise ValueError(REASON_SOURCE_INVALID)
    if _s1.supplier_s1_program_result_to_plain_dict_v01(result) != value:
        raise ValueError(REASON_SOURCE_INVALID)
    return result


def _hydrate_safe_execution(
    value: object,
) -> _safe.SupplierWaterFilterSafeExecutionProjectionV01:
    expected = {
        item.name for item in fields(_safe.SupplierWaterFilterSafeExecutionProjectionV01)
    }
    if type(value) is not dict or set(value) != expected:
        raise ValueError(REASON_SOURCE_INVALID)
    values = dict(value)
    for name in (
        "actor_ids",
        "actor_safe_projection_hashes",
        "actor_validation_statuses",
        "validation_errors",
    ):
        values[name] = _exact_list(values[name], str)
    try:
        result = _safe.SupplierWaterFilterSafeExecutionProjectionV01(**values)
    except (TypeError, ValueError):
        raise ValueError(REASON_SOURCE_INVALID) from None
    if _safe.validate_supplier_water_filter_safe_execution_projection_v01(result):
        raise ValueError(REASON_SOURCE_INVALID)
    if _safe.supplier_water_filter_safe_execution_projection_to_plain_dict_v01(result) != value:
        raise ValueError(REASON_SOURCE_INVALID)
    return result


def _hydrate_source(content: bytes) -> _AcceptedS1Source:
    report_sha256 = hashlib.sha256(content).hexdigest()
    if report_sha256 != ACCEPTED_S1_REPORT_SHA256:
        raise ValueError(REASON_SOURCE_INVALID)
    plain = _strict_json(content)
    result_keys = {item.name for item in fields(_s1.SupplierS1ProgramResultV01)}
    if set(plain) != result_keys | {"safe_execution_projection"}:
        raise ValueError(REASON_SOURCE_INVALID)
    result_plain = {key: value for key, value in plain.items() if key != "safe_execution_projection"}
    result = _hydrate_s1_result(result_plain)
    safe_execution = _hydrate_safe_execution(plain["safe_execution_projection"])
    if (
        result.result_id != ACCEPTED_S1_RESULT_ID
        or result.execution_head != ACCEPTED_S1_EXECUTION_HEAD
        or safe_execution.safe_execution_id != ACCEPTED_S1_SAFE_EXECUTION_ID
        or safe_execution.execution_head != result.execution_head
        or (
            safe_execution.provider_call_count,
            safe_execution.network_call_count,
            safe_execution.gemini_call_count,
        )
        != ACCEPTED_SOURCE_CALLS
        or result.real_world_effects_count != 0
        or safe_execution.real_world_effects_count != 0
        or result.raw_prompt_included
        or result.raw_provider_response_included
        or len(result.scenarios) != 5
    ):
        raise ValueError(REASON_SOURCE_INVALID)
    return _AcceptedS1Source(
        report_sha256=report_sha256,
        result=result,
        safe_execution=safe_execution,
    )


def _canonical_absolute_path(value: object) -> Path:
    if type(value) is not str or not value.startswith("/"):
        raise ValueError(REASON_PATH_INVALID)
    if value != os.path.normpath(value) or "//" in value:
        raise ValueError(REASON_PATH_INVALID)
    return Path(value)


def _open_absolute_directory(path: Path) -> int:
    if not path.is_absolute():
        raise ValueError(REASON_PATH_INVALID)
    flags = os.O_RDONLY | getattr(os, "O_DIRECTORY", 0) | getattr(os, "O_NOFOLLOW", 0)
    descriptor = os.open("/", flags)
    try:
        for component in path.parts[1:]:
            entry = os.stat(component, dir_fd=descriptor, follow_symlinks=False)
            if not stat.S_ISDIR(entry.st_mode):
                raise ValueError(REASON_PATH_INVALID)
            child = os.open(component, flags, dir_fd=descriptor)
            opened = os.fstat(child)
            if (
                opened.st_dev,
                opened.st_ino,
                stat.S_IFMT(opened.st_mode),
            ) != (
                entry.st_dev,
                entry.st_ino,
                stat.S_IFMT(entry.st_mode),
            ):
                os.close(child)
                raise ValueError(REASON_PATH_INVALID)
            os.close(descriptor)
            descriptor = child
        return descriptor
    except Exception:
        os.close(descriptor)
        raise


def _read_regular_file(path: Path, *, expected_mode: int) -> bytes:
    parent_fd = _open_absolute_directory(path.parent)
    descriptor = -1
    try:
        entry = os.stat(path.name, dir_fd=parent_fd, follow_symlinks=False)
        if not stat.S_ISREG(entry.st_mode) or stat.S_IMODE(entry.st_mode) != expected_mode:
            raise ValueError(REASON_SOURCE_INVALID)
        descriptor = os.open(
            path.name,
            os.O_RDONLY | getattr(os, "O_NOFOLLOW", 0),
            dir_fd=parent_fd,
        )
        opened = os.fstat(descriptor)
        if (opened.st_dev, opened.st_ino) != (entry.st_dev, entry.st_ino):
            raise ValueError(REASON_SOURCE_INVALID)
        chunks: list[bytes] = []
        total = 0
        while True:
            chunk = os.read(descriptor, min(65536, _MAX_SOURCE_BYTES + 1 - total))
            if not chunk:
                break
            chunks.append(chunk)
            total += len(chunk)
            if total > _MAX_SOURCE_BYTES:
                raise ValueError(REASON_SOURCE_INVALID)
        content = b"".join(chunks)
        final_fd = os.fstat(descriptor)
        final_entry = os.stat(path.name, dir_fd=parent_fd, follow_symlinks=False)
        if (
            final_fd.st_dev,
            final_fd.st_ino,
            final_fd.st_size,
            stat.S_IMODE(final_fd.st_mode),
        ) != (
            entry.st_dev,
            entry.st_ino,
            entry.st_size,
            expected_mode,
        ) or (final_entry.st_dev, final_entry.st_ino) != (
            entry.st_dev,
            entry.st_ino,
        ):
            raise ValueError(REASON_SOURCE_INVALID)
        return content
    finally:
        if descriptor >= 0:
            os.close(descriptor)
        os.close(parent_fd)


def load_accepted_supplier_s1_source_v01(
    source_path: str,
) -> _AcceptedS1Source:
    path = _canonical_absolute_path(source_path)
    return _hydrate_source(_read_regular_file(path, expected_mode=0o400))


def _validate_boundaries(
    *,
    repository_root: str,
    source_path: str,
    output_path: str,
) -> tuple[Path, Path, Path, tuple[int, int, int]]:
    root = _canonical_absolute_path(repository_root)
    source = _canonical_absolute_path(source_path)
    output = _canonical_absolute_path(output_path)
    root_fd = _open_absolute_directory(root)
    os.close(root_fd)
    if source != root / ACCEPTED_S1_REPORT_REF:
        raise ValueError(REASON_PATH_INVALID)
    if output != root / CANONICAL_S2_OUTPUT_REF or output == source:
        raise ValueError(REASON_PATH_INVALID)
    output_parent_fd = _open_absolute_directory(output.parent)
    try:
        output_parent = os.fstat(output_parent_fd)
        output_parent_identity = (
            output_parent.st_dev,
            output_parent.st_ino,
            stat.S_IMODE(output_parent.st_mode),
        )
        try:
            os.stat(output.name, dir_fd=output_parent_fd, follow_symlinks=False)
        except FileNotFoundError:
            pass
        else:
            raise ValueError(REASON_OUTPUT_EXISTS)
    finally:
        os.close(output_parent_fd)
    return root, source, output, output_parent_identity


def _write_all(descriptor: int, content: bytes) -> None:
    offset = 0
    while offset < len(content):
        written = os.write(descriptor, content[offset:])
        if written <= 0:
            raise OSError(REASON_WRITE_FAILED)
        offset += written


def _cleanup_owned_output(parent_fd: int, name: str, identity: tuple[int, int]) -> None:
    try:
        entry = os.stat(name, dir_fd=parent_fd, follow_symlinks=False)
    except FileNotFoundError:
        return
    if not stat.S_ISREG(entry.st_mode) or (entry.st_dev, entry.st_ino) != identity:
        return
    os.unlink(name, dir_fd=parent_fd)
    os.fsync(parent_fd)
    try:
        os.stat(name, dir_fd=parent_fd, follow_symlinks=False)
    except FileNotFoundError:
        return
    raise OSError(REASON_WRITE_FAILED)


def _write_output(
    path: Path,
    content: bytes,
    expected_parent_identity: tuple[int, int, int],
) -> None:
    parent_fd = _open_absolute_directory(path.parent)
    identity: tuple[int, int] | None = None
    descriptor = -1
    try:
        parent = os.fstat(parent_fd)
        if (
            parent.st_dev,
            parent.st_ino,
            stat.S_IMODE(parent.st_mode),
        ) != expected_parent_identity:
            raise OSError(REASON_WRITE_FAILED)
        flags = os.O_WRONLY | os.O_CREAT | os.O_EXCL | getattr(os, "O_NOFOLLOW", 0)
        descriptor = os.open(path.name, flags, 0o400, dir_fd=parent_fd)
        opened = os.fstat(descriptor)
        if not stat.S_ISREG(opened.st_mode):
            raise OSError(REASON_WRITE_FAILED)
        identity = (opened.st_dev, opened.st_ino)
        os.fchmod(descriptor, 0o400)
        _write_all(descriptor, content)
        os.fsync(descriptor)
        written = os.fstat(descriptor)
        if (
            written.st_size != len(content)
            or stat.S_IMODE(written.st_mode) != 0o400
            or (written.st_dev, written.st_ino) != identity
        ):
            raise OSError(REASON_WRITE_FAILED)
        os.close(descriptor)
        descriptor = -1
        os.fsync(parent_fd)

        entry = os.stat(path.name, dir_fd=parent_fd, follow_symlinks=False)
        if not stat.S_ISREG(entry.st_mode) or (
            entry.st_dev,
            entry.st_ino,
            entry.st_size,
            stat.S_IMODE(entry.st_mode),
        ) != (identity[0], identity[1], len(content), 0o400):
            raise OSError(REASON_WRITE_FAILED)
        reread_fd = os.open(
            path.name,
            os.O_RDONLY | getattr(os, "O_NOFOLLOW", 0),
            dir_fd=parent_fd,
        )
        try:
            reread_stat = os.fstat(reread_fd)
            if (reread_stat.st_dev, reread_stat.st_ino) != identity:
                raise OSError(REASON_WRITE_FAILED)
            chunks: list[bytes] = []
            while True:
                chunk = os.read(reread_fd, 65536)
                if not chunk:
                    break
                chunks.append(chunk)
            if b"".join(chunks) != content:
                raise OSError(REASON_WRITE_FAILED)
        finally:
            os.close(reread_fd)
        final_entry = os.stat(path.name, dir_fd=parent_fd, follow_symlinks=False)
        if (final_entry.st_dev, final_entry.st_ino) != identity:
            raise OSError(REASON_WRITE_FAILED)
    except Exception:
        if descriptor >= 0:
            try:
                os.close(descriptor)
            except OSError:
                pass
        if identity is not None:
            _cleanup_owned_output(parent_fd, path.name, identity)
        raise ValueError(REASON_WRITE_FAILED) from None
    finally:
        os.close(parent_fd)


def run_supplier_water_filter_negative_matrix_v01(
    *,
    repository_root: str,
    source_path: str,
    output_path: str,
) -> SupplierS2NegativeMatrixResultV01:
    _, source_file, output_file, output_parent_identity = _validate_boundaries(
        repository_root=repository_root,
        source_path=source_path,
        output_path=output_path,
    )
    source = load_accepted_supplier_s1_source_v01(str(source_file))
    result = build_supplier_water_filter_negative_matrix_v01(source)
    if validate_supplier_water_filter_negative_matrix_v01(result, source):
        raise ValueError(REASON_INVALID)
    content = canonical_json_bytes_v01(
        supplier_water_filter_negative_matrix_to_plain_dict_v01(result, source)
    ) + b"\n"
    _write_output(output_file, content, output_parent_identity)
    return result


def _implementation_sha256() -> str:
    descriptor = os.open(__file__, os.O_RDONLY | getattr(os, "O_NOFOLLOW", 0))
    try:
        digest = hashlib.sha256()
        while True:
            chunk = os.read(descriptor, 65536)
            if not chunk:
                break
            digest.update(chunk)
        return digest.hexdigest()
    finally:
        os.close(descriptor)


class _SanitizedParser(ArgumentParser):
    def error(self, message: str) -> None:
        raise _RunError(REASON_PATH_INVALID)


def _parser() -> _SanitizedParser:
    parser = _SanitizedParser(allow_abbrev=False, add_help=False)
    parser.add_argument("--repository-root", required=True)
    parser.add_argument("--accepted-s1-report", required=True)
    parser.add_argument("--output", required=True)
    return parser


def _reject_duplicate_options(argv: tuple[str, ...]) -> None:
    names: list[str] = []
    for token in argv:
        if token.startswith("--"):
            names.append(token.split("=", 1)[0])
    if len(names) != len(set(names)):
        raise _RunError(REASON_PATH_INVALID)


def _terminal_summary(status: str, *, result_id: str = "") -> str:
    plain: dict[str, object] = {"final_status": status, "gate_id": GATE_ID}
    if status == STATUS_PASS:
        plain["result_id"] = result_id
    else:
        plain["reason_code"] = REASON_FAIL_CLOSED
    return canonical_json_bytes_v01(plain).decode("utf-8")


def main(argv: list[str] | None = None) -> int:
    tokens = tuple(sys.argv[1:] if argv is None else argv)
    try:
        _reject_duplicate_options(tokens)
        args = _parser().parse_args(tokens)
        result = run_supplier_water_filter_negative_matrix_v01(
            repository_root=args.repository_root,
            source_path=args.accepted_s1_report,
            output_path=args.output,
        )
        print(_terminal_summary(STATUS_PASS, result_id=result.result_id))
        return 0
    except Exception:
        print(_terminal_summary(STATUS_FAIL_CLOSED))
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
