"""Run the bounded Supplier Water Filter S1 programme sequence.

The module composes committed Supplier components. Provider output remains
advisory; existing deterministic validators and Root-owned contracts decide
what is accepted. Injected execution is local proof only. The real-provider
CLI is owner-gated, single-attempt, and is not exercised by automated tests.
"""

from __future__ import annotations

from argparse import ArgumentParser
from collections.abc import Callable, Mapping
from dataclasses import dataclass, replace
import hashlib
import json
import os
from pathlib import Path
import re
import stat
import subprocess
import sys
from typing import Any

from demo import run_full_wow_v1_2_manual_live_multillm_fractal_trace as _live
from demo.run_full_wow_v1_2_product_trace import (
    collect_full_wow_v1_2_product_trace,
)
from hedgehog.domains.supplier_water_filter import kernel_adapter_v01 as _kernel
from hedgehog.domains.supplier_water_filter import live_evidence_adapter_v01 as _safe
from hedgehog.kernel.integrity_replay_v01 import (
    canonical_json_bytes_v01,
    domain_separated_sha256_hex_v01,
)


MODULE_ID = "two_domain_supplier_water_filter_program_v01"
PROGRAMME_ID = "two_domain_all_real_sealed_evidence_program_v01"
PROGRAMME_VERSION = "v0.1"
GATE_ID = "two_domain_all_real_sealed_evidence_program_v01_s1_supplier_live"
DOMAIN_ID = "supplier_water_filter"
MODEL_ID = _live.DEFAULT_MODEL

MODE_INJECTED = "injected_deterministic"
MODE_REAL = "real_provider"
STATUS_PASS = "PASS"
STATUS_FAIL_CLOSED = "FAIL_CLOSED"
BUSINESS_OUTCOME_MIXED = "MIXED"

ACTOR_IDS = _safe.ACTOR_IDS
SCENARIO_IDS = ("S-N1", "S-C1", "S-P1", "S-P2", "S-M1")
SCENARIO_NAMES = (
    "initial_business_blockers_root_not_ready",
    "corrected_evidence_validation_rerun",
    "supplier_a_scoped_human_approval",
    "supplier_a_mock_bank_happy_path",
    "integrated_mixed_business_outcome",
)

REASON_INVALID = "supplier_s1_program_invalid"
REASON_APPROVAL_REQUIRED = "supplier_s1_owner_approval_required"
REASON_COLLECTION_FAILED = "supplier_s1_collection_failed"
REASON_SOURCE_INVALID = "supplier_s1_source_invalid"
REASON_KERNEL_INVALID = "supplier_s1_kernel_invalid"
REASON_PATH_INVALID = "supplier_s1_private_output_invalid"
REASON_PATH_EXISTS = "supplier_s1_private_output_exists"
REASON_PUBLIC_EXISTS = "supplier_s1_public_report_exists"
REASON_WRITE_FAILED = "supplier_s1_write_failed"
REASON_UNEXPECTED = "supplier_s1_unexpected_exception"

_RESULT_DOMAIN = "hedgehog-os:supplier-water-filter-s1-result:v0.1"
_SCENARIO_DOMAIN = "hedgehog-os:supplier-water-filter-s1-scenario:v0.1"
_ATTEMPT_DOMAIN = "hedgehog-os:supplier-water-filter-s1-attempt:v0.1"
_REPOSITORY_ROOT = Path(__file__).absolute().parent.parent
CANONICAL_SAFE_REPORT_REF = (
    "docs/evidence/two_domain_all_real_sealed_evidence_program_v01/"
    "supplier_water_filter/supplier_safe_execution_report_v01.json"
)
CANONICAL_SAFE_REPORT_PATH = _REPOSITORY_ROOT / CANONICAL_SAFE_REPORT_REF
RAW_ATTEMPT_DIRECTORY = "raw_attempt"
ATTEMPT_IDENTITY_FILE = "attempt_identity_v01.json"
PRIVATE_INVENTORY_FILE = "private_inventory_v01.json"
GENERATION_GATE_FILE = "generation_gate_v01.json"
_LOWER_HEAD = re.compile(r"^[0-9a-f]{40}$")
_LOWER_SHA256 = re.compile(r"^[0-9a-f]{64}$")
_OWNER_APPROVAL_FLAG = "--owner-reviewed-supplier-a-approval"
_EXPECTED_KERNEL_ADAPTER_ID = (
    "0b653be0c6bd513cd4ea6071a3b64300dff57866d7a3da66ebf25f17b8199bd9"
)


Provider = Callable[[str, str, Mapping[str, Any]], str]


@dataclass(frozen=True, slots=True)
class SupplierS1ScenarioResultV01:
    scenario_id: str
    scenario_name: str
    validation_status: str
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
    scenario_result_id: str


@dataclass(frozen=True, slots=True)
class SupplierS1ProgramResultV01:
    result_id: str
    result_version: str
    programme_id: str
    gate_id: str
    domain_id: str
    execution_head: str
    implementation_sha256: str
    attempt_number: int
    execution_mode: str
    provider_mode: str
    model_id: str
    final_status: str
    official_evidence_eligible: bool
    actor_ids: tuple[str, ...]
    actor_validation_statuses: tuple[str, ...]
    actor_safe_summaries: tuple[str, ...]
    callback_count: int
    provider_start_count: int
    provider_completion_count: int
    provider_call_count: int
    network_call_count: int
    gemini_call_count: int
    collector_invocation_count: int
    duplicate_call_count: int
    retry_count: int
    fallback_call_count: int
    bsep_status: str
    drs_status: str
    avf_status: str
    first_root_status: str
    corrected_root_status: str
    root_created_action_commit_packet_count: int
    corridor_execution_count: int
    receipt_validation_count: int
    kernel_adapter_id: str
    kernel_validation_status: str
    scenarios: tuple[SupplierS1ScenarioResultV01, ...]
    technical_conformance_status: str
    supplier_a_status: str
    supplier_b_status: str
    shipment_status: str
    receipt_status: str
    real_payment_executed: bool
    real_shipment_released: bool
    business_outcome: str
    real_world_effects_count: int
    raw_prompt_included: bool
    raw_provider_response_included: bool
    secret_scan_passed: bool
    validation_errors: tuple[str, ...]


def _scenario_plain(item: SupplierS1ScenarioResultV01, *, zero_id: bool = False) -> dict[str, object]:
    return {
        "additional_gemini_call_count": item.additional_gemini_call_count,
        "additional_network_call_count": item.additional_network_call_count,
        "additional_provider_call_count": item.additional_provider_call_count,
        "business_outcome": item.business_outcome,
        "corridor_status": item.corridor_status,
        "evidence_refs": list(item.evidence_refs),
        "packet_status": item.packet_status,
        "real_payment_executed": item.real_payment_executed,
        "real_shipment_released": item.real_shipment_released,
        "real_world_effects_count": item.real_world_effects_count,
        "receipt_status": item.receipt_status,
        "root_status": item.root_status,
        "scenario_id": item.scenario_id,
        "scenario_name": item.scenario_name,
        "scenario_result_id": "0" * 64 if zero_id else item.scenario_result_id,
        "shipment_status": item.shipment_status,
        "supplier_a_status": item.supplier_a_status,
        "supplier_b_status": item.supplier_b_status,
        "validation_status": item.validation_status,
        "validated_facts": list(item.validated_facts),
    }


def _result_plain(result: SupplierS1ProgramResultV01, *, zero_id: bool = False) -> dict[str, object]:
    return {
        "actor_ids": list(result.actor_ids),
        "actor_safe_summaries": list(result.actor_safe_summaries),
        "actor_validation_statuses": list(result.actor_validation_statuses),
        "attempt_number": result.attempt_number,
        "avf_status": result.avf_status,
        "bsep_status": result.bsep_status,
        "business_outcome": result.business_outcome,
        "callback_count": result.callback_count,
        "collector_invocation_count": result.collector_invocation_count,
        "corrected_root_status": result.corrected_root_status,
        "corridor_execution_count": result.corridor_execution_count,
        "domain_id": result.domain_id,
        "drs_status": result.drs_status,
        "duplicate_call_count": result.duplicate_call_count,
        "execution_head": result.execution_head,
        "execution_mode": result.execution_mode,
        "fallback_call_count": result.fallback_call_count,
        "final_status": result.final_status,
        "first_root_status": result.first_root_status,
        "gate_id": result.gate_id,
        "gemini_call_count": result.gemini_call_count,
        "implementation_sha256": result.implementation_sha256,
        "kernel_adapter_id": result.kernel_adapter_id,
        "kernel_validation_status": result.kernel_validation_status,
        "model_id": result.model_id,
        "network_call_count": result.network_call_count,
        "official_evidence_eligible": result.official_evidence_eligible,
        "programme_id": result.programme_id,
        "provider_call_count": result.provider_call_count,
        "provider_completion_count": result.provider_completion_count,
        "provider_mode": result.provider_mode,
        "provider_start_count": result.provider_start_count,
        "raw_prompt_included": result.raw_prompt_included,
        "raw_provider_response_included": result.raw_provider_response_included,
        "real_payment_executed": result.real_payment_executed,
        "real_shipment_released": result.real_shipment_released,
        "real_world_effects_count": result.real_world_effects_count,
        "receipt_status": result.receipt_status,
        "receipt_validation_count": result.receipt_validation_count,
        "result_id": "0" * 64 if zero_id else result.result_id,
        "result_version": result.result_version,
        "retry_count": result.retry_count,
        "root_created_action_commit_packet_count": result.root_created_action_commit_packet_count,
        "scenarios": [_scenario_plain(item) for item in result.scenarios],
        "secret_scan_passed": result.secret_scan_passed,
        "shipment_status": result.shipment_status,
        "supplier_a_status": result.supplier_a_status,
        "supplier_b_status": result.supplier_b_status,
        "technical_conformance_status": result.technical_conformance_status,
        "validation_errors": list(result.validation_errors),
    }


def _identity(domain: str, plain: object) -> str:
    return domain_separated_sha256_hex_v01(
        domain=domain,
        payload=canonical_json_bytes_v01(plain),
    )


def _build_scenario(**values: object) -> SupplierS1ScenarioResultV01:
    provisional = SupplierS1ScenarioResultV01(
        scenario_result_id="0" * 64,
        **values,
    )
    return replace(
        provisional,
        scenario_result_id=_identity(_SCENARIO_DOMAIN, _scenario_plain(provisional, zero_id=True)),
    )


def _require(condition: bool, reason: str = REASON_SOURCE_INVALID) -> None:
    if not condition:
        raise ValueError(reason)


def _accepted_semantic_objects(source: Mapping[str, object]) -> tuple[dict[str, object], ...]:
    orchestrator = source.get("top_level_orchestrator")
    architect = source.get("top_level_architect")
    _require(type(orchestrator) is dict and set(orchestrator) == _live.ORCHESTRATOR_REQUIRED_FIELDS)
    _require(type(architect) is dict and set(architect) == _live.ARCHITECT_REQUIRED_FIELDS)
    _require(_live._validate_orchestrator(orchestrator)["accepted"] is True)
    _require(_live._validate_architect(architect)["accepted"] is True)
    branches = source.get("fractal_branches")
    _require(type(branches) is tuple and len(branches) == len(_live.BRANCH_IDS))
    by_id: dict[str, Mapping[str, object]] = {}
    for row in branches:
        _require(type(row) is dict and type(row.get("branch_id")) is str)
        branch_id = row["branch_id"]
        _require(branch_id not in by_id)
        by_id[branch_id] = row
    _require(tuple(by_id) == _live.BRANCH_IDS)
    semantic_objects: list[dict[str, object]] = [dict(orchestrator), dict(architect)]
    for branch_id, actor_id in _live.BRANCH_ACTOR_ROLES.items():
        _require(actor_id == ACTOR_IDS[len(semantic_objects)])
        semantic = by_id[branch_id].get("branch_semantic_actor_output")
        _require(type(semantic) is dict and set(semantic) == _live.BRANCH_SEMANTIC_REQUIRED_FIELDS)
        validation = _live._validate_branch_semantics(semantic, branch_id) if type(semantic) is dict else {"accepted": False}
        _require(validation["accepted"] is True)
        semantic_objects.append(dict(semantic))
    _require(len(semantic_objects) == len(ACTOR_IDS))
    return tuple(semantic_objects)


def _semantic_summary(semantic: Mapping[str, object]) -> str:
    return canonical_json_bytes_v01(dict(semantic)).decode("utf-8")


def _semantic_safe_projection(semantic: Mapping[str, object]) -> dict[str, object]:
    return {
        "ordered_fields": [
            {"field_name": key, "field_value": semantic[key]}
            for key in sorted(semantic)
        ]
    }


def _decode_semantic_summaries(summaries: object) -> tuple[dict[str, object], ...] | None:
    if type(summaries) is not tuple or len(summaries) != len(ACTOR_IDS):
        return None
    decoded: list[dict[str, object]] = []

    def reject_duplicate(pairs: list[tuple[str, object]]) -> dict[str, object]:
        value: dict[str, object] = {}
        for key, item in pairs:
            if key in value:
                raise ValueError
            value[key] = item
        return value

    for summary in summaries:
        if type(summary) is not str or not summary:
            return None
        try:
            parsed = json.loads(
                summary,
                object_pairs_hook=reject_duplicate,
                parse_constant=lambda value: (_ for _ in ()).throw(ValueError()),
            )
        except (TypeError, ValueError, json.JSONDecodeError):
            return None
        if type(parsed) is not dict or canonical_json_bytes_v01(parsed).decode("utf-8") != summary:
            return None
        decoded.append(parsed)
    if set(decoded[0]) != _live.ORCHESTRATOR_REQUIRED_FIELDS:
        return None
    if set(decoded[1]) != _live.ARCHITECT_REQUIRED_FIELDS:
        return None
    if _live._validate_orchestrator(decoded[0])["accepted"] is not True:
        return None
    if _live._validate_architect(decoded[1])["accepted"] is not True:
        return None
    for semantic, branch_id in zip(decoded[2:], _live.BRANCH_ACTOR_ROLES, strict=True):
        if set(semantic) != _live.BRANCH_SEMANTIC_REQUIRED_FIELDS:
            return None
        if _live._validate_branch_semantics(semantic, branch_id)["accepted"] is not True:
            return None
    return tuple(decoded)


def _validate_live_report(report: object, execution_mode: str) -> tuple[dict[str, object], tuple[str, ...]]:
    _require(type(report) is dict)
    source = report
    _require(source.get("final_status") == STATUS_PASS)
    _require(source.get("validation_errors") == ())
    _require(source.get("model") == MODEL_ID)
    rows = source.get("semantic_actor_calls")
    _require(type(rows) is tuple and len(rows) == len(ACTOR_IDS))
    actor_ids = tuple(item.get("role") for item in rows if type(item) is dict)
    statuses = tuple(item.get("validation_status") for item in rows if type(item) is dict)
    _require(actor_ids == ACTOR_IDS)
    _require(statuses == (STATUS_PASS,) * len(ACTOR_IDS))
    counters = source.get("counters")
    _require(type(counters) is dict)
    _require(counters.get("semantic_actor_call_count") == 6)
    if execution_mode == MODE_INJECTED:
        _require(counters.get("fake_provider_call_count") == 6)
        _require(counters.get("real_provider_call_count") == 0)
        _require(counters.get("network_used_count") == 0)
        _require(counters.get("gemini_called_count") == 0)
        provider_mode = "fake_injected"
    else:
        _require(counters.get("fake_provider_call_count") == 0)
        _require(counters.get("real_provider_call_count") == 6)
        _require(counters.get("network_used_count") == 6)
        _require(counters.get("gemini_called_count") == 6)
        provider_mode = MODE_REAL
    _require(source.get("provider_mode") == provider_mode)

    bsep = source.get("bsep_validation")
    _require(type(bsep) is dict and bsep.get("accepted") is True and bsep.get("errors") == [])
    drs = source.get("local_drs_v0_2_observation")
    avf = source.get("avf_v0_2_observation")
    _require(type(drs) is dict and drs.get("local_drs_v0_2_status") == STATUS_PASS)
    _require(type(avf) is dict and avf.get("avf_v0_2_status") == STATUS_PASS)
    _require(drs.get("direct_reuse_allowed_count") == 0)
    _require(avf.get("root_review_required_count") == 9)

    root = source.get("post_vv_gt_root")
    _require(type(root) is dict)
    _require(root.get("root_first_decision") == "NOT_READY")
    _require(root.get("root_second_decision") == "SUPPLIER_A_SCOPED_REVIEW_READY")
    _require(root.get("supplier_b_final_status") == "BLOCKED")
    _require(root.get("shipment_final_status") == "HELD")
    _require(root.get("receipt_final_status") == "EVIDENCE_ONLY")
    _require(root.get("root_remains_final_authority") is True)

    packet = source.get("action_commit_packet_v0_2_integration")
    _require(type(packet) is dict and packet.get("status") == STATUS_PASS)
    for key in (
        "root_created",
        "human_approval_is_scoped_evidence_only",
        "packet_validated",
        "registry_validated",
        "packet_corridor_entry_validated",
        "accepted_for_mock_corridor",
    ):
        _require(packet.get(key) is True)
    _require(packet.get("created_by") == "root")
    _require(packet.get("allowed_subjects") == ("supplier_a_adriatic_filters",))
    _require("supplier_b_balkan_pumps" in packet.get("forbidden_subjects", ()))
    _require("shipment_sh_2042" in packet.get("forbidden_subjects", ()))
    _require("shipment_release" in packet.get("forbidden_actions", ()))
    _require("real_payment" in packet.get("forbidden_actions", ()))
    _require("real_bank" in packet.get("forbidden_adapters", ()))
    for key in ("amount", "creditor_ref", "payment_slot_ref"):
        _require(type(packet.get(key)) is str and bool(packet[key]))
    _require(counters.get("mock_bank_sandbox_v0_2_amount_check_passed_count") == 1)
    _require(counters.get("mock_bank_sandbox_v0_2_creditor_check_passed_count") == 1)
    _require(counters.get("mock_bank_sandbox_v0_2_payment_slot_check_passed_count") == 1)
    _require(counters.get("mock_bank_sandbox_v0_2_adapter_binding_check_passed_count") == 1)
    _require(counters.get("mock_bank_sandbox_v0_2_expiry_ttl_check_passed_count") == 1)
    _require(counters.get("mock_bank_sandbox_v0_2_forbidden_surface_check_passed_count") == 1)

    corridor = source.get("mock_bank_sandbox_v0_2_corridor_execution")
    _require(type(corridor) is dict and corridor.get("status") == STATUS_PASS)
    _require(corridor.get("mock_bank_sandbox_v0_2_status") == STATUS_PASS)
    for key in (
        "source_packet_validated",
        "source_packet_corridor_entry_validated",
        "source_packet_seen_in_registry",
        "receipt_validated",
        "terminal_receipt_observed_in_local_registry",
        "receipt_evidence_only",
        "supplier_b_excluded",
        "shipment_release_excluded",
        "real_bank_excluded",
    ):
        _require(corridor.get(key) is True)
    for key in (
        "receipt_permission_created",
        "receipt_future_permission_created",
        "receipt_final_output_created",
        "receipt_authorizes_supplier_b",
        "receipt_releases_shipment",
        "receipt_mutates_packet_scope",
        "receipt_creates_production_drs_record",
        "real_payment_executed",
    ):
        _require(corridor.get(key) is False)
    _require(corridor.get("real_world_effects_count") == 0)
    _require(counters.get("mock_bank_sandbox_v0_2_corridor_invoked_count") == 1)
    _require(counters.get("mock_bank_sandbox_v0_2_mock_payment_intent_created_count") == 1)
    _require(counters.get("mock_bank_sandbox_v0_2_mock_payment_consent_created_count") == 1)
    _require(counters.get("mock_bank_sandbox_v0_2_mock_payment_order_created_count") == 1)
    _require(counters.get("mock_bank_sandbox_v0_2_mock_receipt_evidence_created_count") == 1)
    _require(counters.get("mock_bank_sandbox_v0_2_terminal_receipt_observed_count") == 1)
    _require(counters.get("mock_bank_sandbox_v0_2_real_payment_executed_count") == 0)
    _require(counters.get("mock_bank_sandbox_v0_2_shipment_released_count") == 0)
    _require(counters.get("mock_bank_sandbox_v0_2_real_world_effects_count") == 0)
    _require(counters.get("action_commit_packet_v0_2_root_created_model_packet_count") == 1)
    _require(counters.get("mock_bank_sandbox_v0_2_receipt_validated_count") == 1)
    _require(counters.get("action_commit_packet_v0_2_created_by_root_count") == 1)
    for key in (
        "action_commit_packet_v0_2_created_by_human_count",
        "action_commit_packet_v0_2_created_by_llm_count",
        "action_commit_packet_v0_2_created_by_drs_count",
        "action_commit_packet_v0_2_created_by_avf_count",
        "action_commit_packet_v0_2_created_by_gt_lgt_count",
        "provider_owned_plangraph_count",
    ):
        _require(counters.get(key) == 0)
    secret = source.get("secret_membrane")
    _require(type(secret) is dict)
    _require(secret.get("prompt_secret_scan_passed") is True)
    _require(secret.get("artifact_secret_scan_passed") is True)
    _require(secret.get("llm_visible_secret_count") == 0)
    _accepted_semantic_objects(source)
    return source, statuses


def _scenario_laws(kernel_adapter_id: str) -> tuple[dict[str, object], ...]:
    common = {
        "supplier_b_status": "BLOCKED",
        "shipment_status": "HELD",
        "additional_provider_call_count": 0,
        "additional_network_call_count": 0,
        "additional_gemini_call_count": 0,
        "real_payment_executed": False,
        "real_shipment_released": False,
        "real_world_effects_count": 0,
    }
    return (
        {
            "scenario_id": "S-N1",
            "scenario_name": SCENARIO_NAMES[0],
            "validation_status": STATUS_PASS,
            "business_outcome": "NOT_READY",
            "root_status": "NOT_READY",
            "supplier_a_status": "BLOCKED_PENDING_CORRECTION",
            "packet_status": "ABSENT",
            "corridor_status": "NOT_ENTERED",
            "receipt_status": "ABSENT",
            "evidence_refs": (
                "live:/post_vv_gt_root/root_first_decision",
                "product_trace:/transition_cards/root_first_not_ready",
                "product_trace:/secret_membrane/payment_slot_boundary",
            ),
            "validated_facts": (
                "warehouse_shortage_visible",
                "legal_or_insurance_missing_invalid_or_expired_visible",
                "supplier_b_invoice_mismatch_or_delay_visible",
                "payment_slot_is_not_permission",
            ),
            **common,
        },
        {
            "scenario_id": "S-C1",
            "scenario_name": SCENARIO_NAMES[1],
            "validation_status": STATUS_PASS,
            "business_outcome": BUSINESS_OUTCOME_MIXED,
            "root_status": "SUPPLIER_A_SCOPED_REVIEW_READY",
            "supplier_a_status": "SUPPLIER_A_SCOPED_REVIEW_READY",
            "packet_status": "ABSENT",
            "corridor_status": "NOT_ENTERED",
            "receipt_status": "ABSENT",
            "evidence_refs": (
                "live:/post_vv_gt_root/root_second_decision",
                "product_trace:/transition_cards/corrected_evidence_received",
                "product_trace:/transition_cards/root_second_supplier_a_scoped_review",
            ),
            "validated_facts": (
                "corrected_evidence_is_context_only",
                "prior_root_final_is_immutable",
                "changed_facts_trigger_fresh_validation",
                "payment_remains_unexecuted",
            ),
            **common,
        },
        {
            "scenario_id": "S-P1",
            "scenario_name": SCENARIO_NAMES[2],
            "validation_status": STATUS_PASS,
            "business_outcome": BUSINESS_OUTCOME_MIXED,
            "root_status": "SUPPLIER_A_SCOPED_REVIEW_READY",
            "supplier_a_status": "APPROVED_SCOPE_ONLY",
            "packet_status": "ROOT_CREATED_SCOPED",
            "corridor_status": "NOT_ENTERED",
            "receipt_status": "ABSENT",
            "evidence_refs": (
                "live:/action_commit_packet_v0_2_integration",
                "product_trace:/transition_cards/human_approval_supplier_a_only",
                "product_trace:/action_commit_packet_v0_2_integration",
            ),
            "validated_facts": (
                "amount_checked",
                "beneficiary_checked",
                "bank_policy_checked",
                "payment_slot_checked",
                "adapter_checked",
                "expiry_checked",
                "forbidden_subjects_checked",
                "forbidden_actions_checked",
            ),
            **common,
        },
        {
            "scenario_id": "S-P2",
            "scenario_name": SCENARIO_NAMES[3],
            "validation_status": STATUS_PASS,
            "business_outcome": BUSINESS_OUTCOME_MIXED,
            "root_status": "SUPPLIER_A_SCOPED_REVIEW_READY",
            "supplier_a_status": STATUS_PASS,
            "packet_status": "VALID_SCOPED",
            "corridor_status": STATUS_PASS,
            "receipt_status": "EVIDENCE_ONLY",
            "evidence_refs": (
                "live:/mock_bank_sandbox_v0_2_corridor_execution",
                "product_trace:/mock_bank_sandbox_v0_2_corridor_execution",
            ),
            "validated_facts": (
                "mock_payment_intent_validated",
                "mock_consent_validated",
                "mock_payment_order_validated",
                "mock_receipt_validated",
                "terminal_receipt_observed",
            ),
            **common,
        },
        {
            "scenario_id": "S-M1",
            "scenario_name": SCENARIO_NAMES[4],
            "validation_status": STATUS_PASS,
            "business_outcome": BUSINESS_OUTCOME_MIXED,
            "root_status": "HELD",
            "supplier_a_status": STATUS_PASS,
            "packet_status": "VALID_SCOPED",
            "corridor_status": STATUS_PASS,
            "receipt_status": "EVIDENCE_ONLY",
            "evidence_refs": (
                f"kernel_adapter:{kernel_adapter_id}",
                "kernel:/multiroot_outcome/outcome_status",
                "product_trace:/business_boundaries",
            ),
            "validated_facts": (
                "technical_conformance_pass",
                "supplier_a_scoped_mock_path_pass",
                "supplier_b_blocked",
                "shipment_held",
                "receipt_evidence_only",
                "business_outcome_mixed",
            ),
            **common,
        },
    )


def _transition_by_id(product_trace: Mapping[str, object], step_id: str) -> Mapping[str, object]:
    rows = product_trace.get("transition_cards")
    _require(type(rows) is tuple)
    matched = tuple(row for row in rows if type(row) is dict and row.get("step_id") == step_id)
    _require(len(matched) == 1)
    return matched[0]


def _build_scenarios(
    source: Mapping[str, object],
    product_trace: Mapping[str, object],
    kernel_result: object,
) -> tuple[SupplierS1ScenarioResultV01, ...]:
    root = source["post_vv_gt_root"]
    packet = source["action_commit_packet_v0_2_integration"]
    corridor = source["mock_bank_sandbox_v0_2_corridor_execution"]
    product_root = product_trace.get("post_vv_gt_root")
    product_packet = product_trace.get("action_commit_packet_v0_2_integration")
    product_corridor = product_trace.get("mock_bank_sandbox_v0_2_corridor_execution")
    product_secret = product_trace.get("secret_membrane")
    product_boundaries = product_trace.get("business_boundaries")
    _require(all(type(item) is dict for item in (root, packet, corridor, product_root, product_packet, product_corridor, product_secret, product_boundaries)))
    _require(product_root["root_first_decision"] == root["root_first_decision"] == "NOT_READY")
    _require(product_root["root_second_decision"] == root["root_second_decision"] == "SUPPLIER_A_SCOPED_REVIEW_READY")
    _require(product_secret["payment_slot_boundary"] == "payment_slot != permission")
    _require("short by 2" in _transition_by_id(product_trace, "warehouse_inventory_query")["output_summary"])
    _require("Invoice mismatch" in _transition_by_id(product_trace, "supplier_b_blocker_query")["output_summary"])
    _require("expired insurance" in _transition_by_id(product_trace, "legal_insurance_contract_check")["output_summary"])
    _require(_transition_by_id(product_trace, "root_first_not_ready")["output_summary"] == "First decision is NOT_READY.")
    _require(_transition_by_id(product_trace, "corrected_evidence_received")["next_step"] == "root_second_supplier_a_scoped_review")
    _require(_transition_by_id(product_trace, "root_second_supplier_a_scoped_review")["output_summary"] == "Second decision is SUPPLIER_A_SCOPED_REVIEW_READY.")
    _require(_transition_by_id(product_trace, "human_approval_supplier_a_only")["output_summary"] == "Approval is evidence for Supplier A scope only.")
    _require(product_packet["action_commit_packet_v0_2_status"] == packet["action_commit_packet_v0_2_status"] == STATUS_PASS)
    _require(product_corridor["mock_bank_sandbox_v0_2_status"] == corridor["mock_bank_sandbox_v0_2_status"] == STATUS_PASS)
    _require(product_corridor["receipt_evidence_only"] is corridor["receipt_evidence_only"] is True)
    _require(product_boundaries["supplier_B_final_status"] == "BLOCKED")
    _require(product_boundaries["shipment_final_status"] == "HELD")
    _require(product_boundaries["receipt_final_status"] == "EVIDENCE_ONLY")
    _require(kernel_result.provider_call_count == kernel_result.network_call_count == kernel_result.gemini_call_count == 0)
    _require(kernel_result.real_world_effects_count == 0)
    laws = _scenario_laws(kernel_result.adapter_id)
    derived = (
        {**laws[0], "root_status": root["root_first_decision"], "business_outcome": root["root_first_decision"]},
        {**laws[1], "root_status": root["root_second_decision"], "supplier_a_status": product_root["root_second_decision"]},
        {**laws[2], "validation_status": packet["status"], "root_status": root["root_second_decision"]},
        {**laws[3], "validation_status": corridor["status"], "corridor_status": corridor["status"], "receipt_status": root["receipt_final_status"]},
        {
            **laws[4],
            "validation_status": (
                STATUS_PASS
                if kernel_result.multiroot_validation.final_status == BUSINESS_OUTCOME_MIXED
                and kernel_result.multiroot_validation.errors == ()
                else STATUS_FAIL_CLOSED
            ),
            "business_outcome": kernel_result.multiroot_outcome.outcome_status,
            "supplier_a_status": corridor["status"],
            "supplier_b_status": kernel_result.supplier_b_status,
            "shipment_status": kernel_result.shipment_status,
            "receipt_status": kernel_result.receipt_status,
            "real_world_effects_count": kernel_result.real_world_effects_count,
        },
    )
    _require(derived == laws)
    return tuple(_build_scenario(**values) for values in derived)


def _safe_execution_source(report: Mapping[str, object], execution_head: str) -> dict[str, object]:
    actor_rows = report["semantic_actor_calls"]
    bsep = report["bsep_packet"]
    counters = report["counters"]
    semantics = _accepted_semantic_objects(report)
    return {
        "execution_head": execution_head,
        "run_id": report["run_id"],
        "report_id": report["report_id"],
        "source_task_id": "supplier_water_filter_s1_live_semantic_collection_v01",
        "transaction_id": _kernel.TRANSACTION_ID,
        "provider_mode": report["provider_mode"],
        "model_id": report["model"],
        "source_final_status": report["final_status"],
        "actors": [
            {
                "actor_id": row["role"],
                "safe_projection": {
                    "actor_id": row["role"],
                    "advisory_only": True,
                    "canonical_semantics": _semantic_safe_projection(semantic),
                },
                "validation_status": row["validation_status"],
            }
            for row, semantic in zip(actor_rows, semantics, strict=True)
        ],
        "bsep": {
            "bsep_id": bsep["bsep_packet_id"],
            "safe_projection": {
                "selected_branch_ids": list(bsep["selected_branch_ids"]),
                "validation_required_before_architect": bsep["validation_required_before_architect"],
                "source_request_excluded": not bsep["raw_user_text_included"],
                "source_provider_material_excluded": not bsep["raw_provider_text_included"],
                "bank_sensitive_material_excluded": not bsep["raw_bank_secrets_included"],
            },
            "validation_status": STATUS_PASS,
            "validated_before_architect": True,
        },
        "counters": {
            "provider_call_count": counters["real_provider_call_count"],
            "network_call_count": counters["network_used_count"],
            "gemini_call_count": counters["gemini_called_count"],
        },
        "raw_prompt_included": False,
        "raw_provider_response_included": False,
        "secret_scan_passed": True,
        "real_world_effects_count": 0,
        "validation_errors": (),
    }


def _collect_with_context(
    *,
    provider: Provider | None,
    execution_head: str,
    owner_approved_supplier_a: bool,
    execution_mode: str | None = None,
    artifact_directory: str | None = None,
) -> tuple[SupplierS1ProgramResultV01, dict[str, object]]:
    """Collect one six-actor lane and validate the five S1 scenario rows."""
    if type(owner_approved_supplier_a) is not bool or not owner_approved_supplier_a:
        raise ValueError(REASON_APPROVAL_REQUIRED)
    mode = MODE_INJECTED if provider is not None else MODE_REAL
    if execution_mode is not None and execution_mode != mode:
        raise ValueError(REASON_INVALID)
    if type(execution_head) is not str or not _LOWER_HEAD.fullmatch(execution_head):
        raise ValueError(REASON_INVALID)
    env = {
        _live.ENABLE_ENV: "1",
        _live.MODEL_ENV: MODEL_ID,
        _live.CALL_DELAY_ENV: "0" if mode == MODE_INJECTED else "30",
    }
    if artifact_directory is not None:
        env[_live.ARTIFACT_DIR_ENV] = artifact_directory

    callback_order: list[str] = []
    starts = 0
    completions = 0

    def observed_provider(role: str, prompt: str, context: Mapping[str, Any]) -> str:
        nonlocal starts, completions
        index = len(callback_order)
        if index >= len(ACTOR_IDS) or role != ACTOR_IDS[index] or role in callback_order:
            raise ValueError("supplier_s1_actor_order_invalid")
        callback_order.append(role)
        starts += 1
        value = provider(role, prompt, context)  # type: ignore[misc]
        if type(value) is not str:
            raise ValueError("supplier_s1_provider_result_invalid")
        completions += 1
        return value

    report = _live.collect_full_wow_v1_2_manual_live_multillm_fractal_trace(
        env=env,
        provider=observed_provider if provider is not None else None,
    )
    source, statuses = _validate_live_report(report, mode)
    counters = source["counters"]
    source_callback_count = counters["semantic_actor_call_count"]
    source_completion_count = sum(
        item["validation_status"] == STATUS_PASS
        for item in source["semantic_actor_calls"]
    )
    if mode == MODE_INJECTED:
        _require(tuple(callback_order) == ACTOR_IDS)
        _require(starts == completions == 6)
        _require((source_callback_count, starts, completions) == (6, 6, 6))
        callback_count = len(callback_order)
        start_count = starts
        completion_count = completions
    else:
        callback_count = source_callback_count
        start_count = counters["real_provider_call_count"]
        completion_count = source_completion_count
        _require((callback_count, start_count, completion_count) == (6, 6, 6))

    product_trace = collect_full_wow_v1_2_product_trace()
    _require(type(product_trace) is dict and product_trace.get("final_status") == STATUS_PASS)
    _require(product_trace.get("validation_errors") == ())
    kernel_result = _kernel.build_supplier_water_filter_kernel_adapter_result_v01(
        source_report=product_trace
    )
    kernel_errors = _kernel.validate_supplier_water_filter_kernel_adapter_result_v01(
        source_report=product_trace,
        result=kernel_result,
    )
    _require(kernel_errors == (), REASON_KERNEL_INVALID)
    _require(kernel_result.supplier_a_status == "SUPPLIER_A_SCOPED_REVIEW_READY", REASON_KERNEL_INVALID)
    _require(kernel_result.supplier_b_status == "BLOCKED", REASON_KERNEL_INVALID)
    _require(kernel_result.shipment_status == "HELD", REASON_KERNEL_INVALID)
    _require(kernel_result.receipt_status == "EVIDENCE_ONLY", REASON_KERNEL_INVALID)
    _require(kernel_result.multiroot_outcome.outcome_status == BUSINESS_OUTCOME_MIXED, REASON_KERNEL_INVALID)
    _require(kernel_result.real_world_effects_count == 0, REASON_KERNEL_INVALID)

    scenarios = _build_scenarios(source, product_trace, kernel_result)
    semantics = _accepted_semantic_objects(source)
    external = (
        counters["real_provider_call_count"],
        counters["network_used_count"],
        counters["gemini_called_count"],
    )
    provisional = SupplierS1ProgramResultV01(
        result_id="0" * 64,
        result_version=PROGRAMME_VERSION,
        programme_id=PROGRAMME_ID,
        gate_id=GATE_ID,
        domain_id=DOMAIN_ID,
        execution_head=execution_head,
        implementation_sha256=_implementation_sha256(),
        attempt_number=1,
        execution_mode=mode,
        provider_mode="fake_injected" if mode == MODE_INJECTED else MODE_REAL,
        model_id=MODEL_ID,
        final_status=STATUS_PASS,
        official_evidence_eligible=mode == MODE_REAL,
        actor_ids=ACTOR_IDS,
        actor_validation_statuses=statuses,
        actor_safe_summaries=tuple(_semantic_summary(item) for item in semantics),
        callback_count=callback_count,
        provider_start_count=start_count,
        provider_completion_count=completion_count,
        provider_call_count=external[0],
        network_call_count=external[1],
        gemini_call_count=external[2],
        collector_invocation_count=1,
        duplicate_call_count=0,
        retry_count=0,
        fallback_call_count=0,
        bsep_status=STATUS_PASS,
        drs_status=STATUS_PASS,
        avf_status=STATUS_PASS,
        first_root_status="NOT_READY",
        corrected_root_status="SUPPLIER_A_SCOPED_REVIEW_READY",
        root_created_action_commit_packet_count=counters["action_commit_packet_v0_2_root_created_model_packet_count"],
        corridor_execution_count=counters["mock_bank_sandbox_v0_2_corridor_invoked_count"],
        receipt_validation_count=counters["mock_bank_sandbox_v0_2_receipt_validated_count"],
        kernel_adapter_id=kernel_result.adapter_id,
        kernel_validation_status=STATUS_PASS,
        scenarios=scenarios,
        technical_conformance_status=STATUS_PASS,
        supplier_a_status=STATUS_PASS,
        supplier_b_status="BLOCKED",
        shipment_status="HELD",
        receipt_status="EVIDENCE_ONLY",
        real_payment_executed=False,
        real_shipment_released=False,
        business_outcome=BUSINESS_OUTCOME_MIXED,
        real_world_effects_count=0,
        raw_prompt_included=False,
        raw_provider_response_included=False,
        secret_scan_passed=True,
        validation_errors=(),
    )
    result = replace(
        provisional,
        result_id=_identity(_RESULT_DOMAIN, _result_plain(provisional, zero_id=True)),
    )
    if validate_supplier_s1_program_result_v01(result):
        raise ValueError(REASON_INVALID)
    if mode == MODE_REAL:
        safe_execution = _safe.build_supplier_water_filter_safe_execution_projection_v01(
            _safe_execution_source(source, execution_head)
        )
        _require(_safe.validate_supplier_water_filter_safe_execution_projection_v01(safe_execution) == ())
    return result, source


def collect_two_domain_supplier_water_filter_program_v01(
    *,
    provider: Provider | None,
    execution_head: str,
    owner_approved_supplier_a: bool,
    execution_mode: str | None = None,
    artifact_directory: str | None = None,
) -> SupplierS1ProgramResultV01:
    """Collect one six-actor lane and return its bounded validated S1 result."""
    result, _ = _collect_with_context(
        provider=provider,
        execution_head=execution_head,
        owner_approved_supplier_a=owner_approved_supplier_a,
        execution_mode=execution_mode,
        artifact_directory=artifact_directory,
    )
    return result


def validate_supplier_s1_program_result_v01(result: object) -> tuple[str, ...]:
    if type(result) is not SupplierS1ProgramResultV01:
        return (REASON_INVALID,)
    errors: list[str] = []
    if result.result_version != PROGRAMME_VERSION or result.programme_id != PROGRAMME_ID:
        errors.append(REASON_INVALID)
    if result.gate_id != GATE_ID or result.domain_id != DOMAIN_ID:
        errors.append(REASON_INVALID)
    if not _LOWER_HEAD.fullmatch(result.execution_head) or not _LOWER_SHA256.fullmatch(result.implementation_sha256):
        errors.append(REASON_INVALID)
    elif result.implementation_sha256 != _implementation_sha256():
        errors.append(REASON_INVALID)
    if result.attempt_number != 1 or type(result.attempt_number) is not int:
        errors.append(REASON_INVALID)
    if result.execution_mode not in (MODE_INJECTED, MODE_REAL):
        errors.append(REASON_INVALID)
    expected_provider_mode = "fake_injected" if result.execution_mode == MODE_INJECTED else MODE_REAL
    if result.provider_mode != expected_provider_mode or result.model_id != MODEL_ID:
        errors.append(REASON_SOURCE_INVALID)
    if result.actor_ids != ACTOR_IDS or result.actor_validation_statuses != (STATUS_PASS,) * 6:
        errors.append(REASON_SOURCE_INVALID)
    if _decode_semantic_summaries(result.actor_safe_summaries) is None:
        errors.append(REASON_SOURCE_INVALID)
    if (result.callback_count, result.provider_start_count, result.provider_completion_count) != (6, 6, 6):
        errors.append(REASON_SOURCE_INVALID)
    expected_external = (0, 0, 0) if result.execution_mode == MODE_INJECTED else (6, 6, 6)
    if (result.provider_call_count, result.network_call_count, result.gemini_call_count) != expected_external:
        errors.append(REASON_SOURCE_INVALID)
    if (result.collector_invocation_count, result.duplicate_call_count, result.retry_count, result.fallback_call_count) != (1, 0, 0, 0):
        errors.append(REASON_SOURCE_INVALID)
    if (result.bsep_status, result.drs_status, result.avf_status) != (STATUS_PASS, STATUS_PASS, STATUS_PASS):
        errors.append(REASON_SOURCE_INVALID)
    if (result.first_root_status, result.corrected_root_status) != (
        "NOT_READY",
        "SUPPLIER_A_SCOPED_REVIEW_READY",
    ):
        errors.append(REASON_SOURCE_INVALID)
    if (
        result.root_created_action_commit_packet_count,
        result.corridor_execution_count,
        result.receipt_validation_count,
    ) != (1, 1, 1):
        errors.append(REASON_SOURCE_INVALID)
    counter_values = (
        result.callback_count,
        result.provider_start_count,
        result.provider_completion_count,
        result.provider_call_count,
        result.network_call_count,
        result.gemini_call_count,
        result.collector_invocation_count,
        result.duplicate_call_count,
        result.retry_count,
        result.fallback_call_count,
        result.root_created_action_commit_packet_count,
        result.corridor_execution_count,
        result.receipt_validation_count,
        result.real_world_effects_count,
    )
    if any(type(value) is not int for value in counter_values):
        errors.append(REASON_SOURCE_INVALID)
    if (
        result.kernel_adapter_id != _EXPECTED_KERNEL_ADAPTER_ID
        or result.kernel_validation_status != STATUS_PASS
    ):
        errors.append(REASON_KERNEL_INVALID)
    if type(result.scenarios) is not tuple or tuple(item.scenario_id for item in result.scenarios) != SCENARIO_IDS:
        errors.append(REASON_SOURCE_INVALID)
    if tuple(item.scenario_name for item in result.scenarios) != SCENARIO_NAMES:
        errors.append(REASON_SOURCE_INVALID)
    if any(
        type(item.additional_provider_call_count) is not int
        or type(item.additional_network_call_count) is not int
        or type(item.additional_gemini_call_count) is not int
        or type(item.real_world_effects_count) is not int
        or item.additional_provider_call_count
        or item.additional_network_call_count
        or item.additional_gemini_call_count
        or item.real_world_effects_count
        or item.real_payment_executed
        or item.real_shipment_released
        for item in result.scenarios
    ):
        errors.append(REASON_SOURCE_INVALID)
    required = (
        result.final_status == STATUS_PASS,
        result.technical_conformance_status == STATUS_PASS,
        result.supplier_a_status == STATUS_PASS,
        result.supplier_b_status == "BLOCKED",
        result.shipment_status == "HELD",
        result.receipt_status == "EVIDENCE_ONLY",
        result.business_outcome == BUSINESS_OUTCOME_MIXED,
        result.real_payment_executed is False,
        result.real_shipment_released is False,
        result.real_world_effects_count == 0,
        result.raw_prompt_included is False,
        result.raw_provider_response_included is False,
        result.secret_scan_passed is True,
        result.validation_errors == (),
    )
    if not all(required):
        errors.append(REASON_SOURCE_INVALID)
    if result.official_evidence_eligible is not (result.execution_mode == MODE_REAL):
        errors.append(REASON_SOURCE_INVALID)
    expected_scenarios = tuple(
        _build_scenario(**values) for values in _scenario_laws(result.kernel_adapter_id)
    )
    if result.scenarios != expected_scenarios:
        errors.append(REASON_SOURCE_INVALID)
    for item in result.scenarios:
        if (
            type(item.validated_facts) is not tuple
            or not item.validated_facts
            or any(type(value) is not str or not value for value in item.validated_facts)
        ):
            errors.append(REASON_SOURCE_INVALID)
        if item.scenario_result_id != _identity(_SCENARIO_DOMAIN, _scenario_plain(item, zero_id=True)):
            errors.append(REASON_INVALID)
    if result.result_id != _identity(_RESULT_DOMAIN, _result_plain(result, zero_id=True)):
        errors.append(REASON_INVALID)
    return tuple(dict.fromkeys(errors))


def supplier_s1_program_result_to_plain_dict_v01(result: SupplierS1ProgramResultV01) -> dict[str, object]:
    if validate_supplier_s1_program_result_v01(result):
        raise ValueError(REASON_INVALID)
    plain = _result_plain(result)
    canonical_json_bytes_v01(plain)
    return plain


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


def _git_head() -> str:
    completed = subprocess.run(
        ("git", "-C", str(_REPOSITORY_ROOT), "rev-parse", "HEAD"),
        check=True,
        capture_output=True,
        text=True,
        timeout=5,
    )
    value = completed.stdout.strip()
    if not _LOWER_HEAD.fullmatch(value):
        raise ValueError(REASON_INVALID)
    return value


def _open_absolute_directory(path: Path) -> int:
    if not path.is_absolute() or str(path) != os.path.normpath(str(path)):
        raise ValueError(REASON_PATH_INVALID)
    descriptor = os.open("/", os.O_RDONLY | os.O_DIRECTORY)
    try:
        for component in path.parts[1:]:
            if component in ("", ".", ".."):
                raise ValueError(REASON_PATH_INVALID)
            before = os.stat(component, dir_fd=descriptor, follow_symlinks=False)
            next_descriptor = os.open(
                component,
                os.O_RDONLY | os.O_DIRECTORY | getattr(os, "O_NOFOLLOW", 0),
                dir_fd=descriptor,
            )
            observed = os.fstat(next_descriptor)
            if (before.st_dev, before.st_ino) != (observed.st_dev, observed.st_ino):
                os.close(next_descriptor)
                raise ValueError(REASON_PATH_INVALID)
            os.close(descriptor)
            descriptor = next_descriptor
        return descriptor
    except Exception:
        os.close(descriptor)
        raise


def _validate_private_output(path_text: object) -> Path:
    if type(path_text) is not str or not path_text:
        raise ValueError(REASON_PATH_INVALID)
    path = Path(path_text)
    if not path.is_absolute() or path_text != os.path.normpath(path_text):
        raise ValueError(REASON_PATH_INVALID)
    try:
        path.relative_to(_REPOSITORY_ROOT)
    except ValueError:
        pass
    else:
        raise ValueError(REASON_PATH_INVALID)
    parent_fd = _open_absolute_directory(path.parent)
    try:
        try:
            os.stat(path.name, dir_fd=parent_fd, follow_symlinks=False)
        except FileNotFoundError:
            return path
        raise ValueError(REASON_PATH_EXISTS)
    finally:
        os.close(parent_fd)


def _write_all(descriptor: int, content: bytes) -> None:
    offset = 0
    while offset < len(content):
        written = os.write(descriptor, content[offset:])
        if written <= 0:
            raise OSError("short_write")
        offset += written


def _canonical_line(plain: object) -> bytes:
    return canonical_json_bytes_v01(plain) + b"\n"


def _write_owned_file(parent_fd: int, name: str, content: bytes, mode: int) -> tuple[int, int]:
    flags = os.O_WRONLY | os.O_CREAT | os.O_EXCL | getattr(os, "O_NOFOLLOW", 0)
    descriptor = os.open(name, flags, mode, dir_fd=parent_fd)
    opened = os.fstat(descriptor)
    identity = (opened.st_dev, opened.st_ino)
    try:
        _write_all(descriptor, content)
        os.fsync(descriptor)
        os.close(descriptor)
        descriptor = -1
        os.fsync(parent_fd)
        read_fd = os.open(
            name,
            os.O_RDONLY | getattr(os, "O_NOFOLLOW", 0),
            dir_fd=parent_fd,
        )
        try:
            observed = os.fstat(read_fd)
            entry = os.stat(name, dir_fd=parent_fd, follow_symlinks=False)
            if identity != (observed.st_dev, observed.st_ino) or identity != (entry.st_dev, entry.st_ino):
                raise OSError("identity_mismatch")
            data = bytearray()
            while True:
                chunk = os.read(read_fd, 65536)
                if not chunk:
                    break
                data.extend(chunk)
            if bytes(data) != content or stat.S_IMODE(observed.st_mode) != mode:
                raise OSError("reread_mismatch")
        finally:
            os.close(read_fd)
        return identity
    except Exception:
        cleanup_error: Exception | None = None
        if descriptor >= 0:
            try:
                os.close(descriptor)
            except OSError as error:
                cleanup_error = error
        try:
            entry = os.stat(name, dir_fd=parent_fd, follow_symlinks=False)
            if stat.S_ISREG(entry.st_mode) and (entry.st_dev, entry.st_ino) == identity:
                os.unlink(name, dir_fd=parent_fd)
                os.fsync(parent_fd)
                try:
                    os.stat(name, dir_fd=parent_fd, follow_symlinks=False)
                except FileNotFoundError:
                    pass
                else:
                    cleanup_error = ValueError(REASON_WRITE_FAILED)
            elif (entry.st_dev, entry.st_ino) != identity:
                cleanup_error = ValueError(REASON_WRITE_FAILED)
        except FileNotFoundError:
            pass
        except OSError as error:
            cleanup_error = error
        if cleanup_error is not None:
            raise ValueError(REASON_WRITE_FAILED) from None
        raise


def _inventory_rows(raw_fd: int) -> tuple[dict[str, object], ...]:
    rows: list[dict[str, object]] = []
    for name in sorted(os.listdir(raw_fd)):
        entry = os.stat(name, dir_fd=raw_fd, follow_symlinks=False)
        if not stat.S_ISREG(entry.st_mode):
            raise ValueError(REASON_WRITE_FAILED)
        descriptor = os.open(name, os.O_RDONLY | getattr(os, "O_NOFOLLOW", 0), dir_fd=raw_fd)
        try:
            digest = hashlib.sha256()
            count = 0
            while True:
                chunk = os.read(descriptor, 65536)
                if not chunk:
                    break
                count += len(chunk)
                digest.update(chunk)
            observed = os.fstat(descriptor)
            if (entry.st_dev, entry.st_ino, entry.st_size) != (observed.st_dev, observed.st_ino, count):
                raise ValueError(REASON_WRITE_FAILED)
        finally:
            os.close(descriptor)
        rows.append({"byte_count": count, "logical_name": f"raw_attempt/{name}", "sha256": digest.hexdigest()})
    return tuple(rows)


def _preserve_attempt(
    *,
    root: Path,
    execution_head: str,
    result: SupplierS1ProgramResultV01 | None,
    reason: str,
) -> None:
    root_fd = _open_absolute_directory(root)
    raw_fd = os.open(RAW_ATTEMPT_DIRECTORY, os.O_RDONLY | os.O_DIRECTORY | getattr(os, "O_NOFOLLOW", 0), dir_fd=root_fd)
    try:
        rows = _inventory_rows(raw_fd)
        inventory = {
            "aggregate_digest": _identity("hedgehog-os:supplier-s1-inventory:v0.1", list(rows)),
            "attempt_number": 1,
            "files": list(rows),
            "raw_file_count": len(rows),
        }
        _write_owned_file(root_fd, PRIVATE_INVENTORY_FILE, _canonical_line(inventory), 0o600)
        gate = {
            "attempt_number": 1,
            "execution_head": execution_head,
            "final_status": result.final_status if result is not None else STATUS_FAIL_CLOSED,
            "gate_id": GATE_ID,
            "inventory_digest": inventory["aggregate_digest"],
            "reason_code": reason,
            "result_id": result.result_id if result is not None else "",
            "retry_count": 0,
        }
        _write_owned_file(root_fd, GENERATION_GATE_FILE, _canonical_line(gate), 0o600)
        for name in os.listdir(raw_fd):
            descriptor = os.open(
                name,
                os.O_RDONLY | getattr(os, "O_NOFOLLOW", 0),
                dir_fd=raw_fd,
            )
            try:
                if not stat.S_ISREG(os.fstat(descriptor).st_mode):
                    raise ValueError(REASON_WRITE_FAILED)
                os.fchmod(descriptor, 0o400)
                os.fsync(descriptor)
            finally:
                os.close(descriptor)
        for name in (ATTEMPT_IDENTITY_FILE, PRIVATE_INVENTORY_FILE, GENERATION_GATE_FILE):
            descriptor = os.open(
                name,
                os.O_RDONLY | getattr(os, "O_NOFOLLOW", 0),
                dir_fd=root_fd,
            )
            try:
                if not stat.S_ISREG(os.fstat(descriptor).st_mode):
                    raise ValueError(REASON_WRITE_FAILED)
                os.fchmod(descriptor, 0o400)
                os.fsync(descriptor)
            finally:
                os.close(descriptor)
        os.fchmod(raw_fd, 0o500)
        os.fchmod(root_fd, 0o500)
        os.fsync(root_fd)
    finally:
        os.close(raw_fd)
        os.close(root_fd)


def _create_attempt_root(
    path: Path,
    execution_head: str,
    *,
    root_created: Callable[[tuple[int, int]], None] | None = None,
) -> None:
    parent_fd = _open_absolute_directory(path.parent)
    try:
        os.mkdir(path.name, 0o700, dir_fd=parent_fd)
        os.fsync(parent_fd)
    finally:
        os.close(parent_fd)
    root_fd = _open_absolute_directory(path)
    try:
        root_stat = os.fstat(root_fd)
        if root_created is not None:
            root_created((root_stat.st_dev, root_stat.st_ino))
        os.mkdir(RAW_ATTEMPT_DIRECTORY, 0o700, dir_fd=root_fd)
        attempt = {
            "attempt_id": _identity(
                _ATTEMPT_DOMAIN,
                {
                    "attempt_number": 1,
                    "execution_head": execution_head,
                    "private_output_sha256": hashlib.sha256(str(path).encode("utf-8")).hexdigest(),
                },
            ),
            "attempt_number": 1,
            "execution_head": execution_head,
            "gate_id": GATE_ID,
            "implementation_sha256": _implementation_sha256(),
            "provider_mode": MODE_REAL,
            "retry_count": 0,
        }
        _write_owned_file(root_fd, ATTEMPT_IDENTITY_FILE, _canonical_line(attempt), 0o600)
    finally:
        os.close(root_fd)


def _preflight_public_report_parent() -> tuple[int, int, int]:
    parent_fd = _open_absolute_directory(CANONICAL_SAFE_REPORT_PATH.parent)
    try:
        parent = os.fstat(parent_fd)
        if not stat.S_ISDIR(parent.st_mode):
            raise ValueError(REASON_PATH_INVALID)
        try:
            os.stat(
                CANONICAL_SAFE_REPORT_PATH.name,
                dir_fd=parent_fd,
                follow_symlinks=False,
            )
        except FileNotFoundError:
            return parent.st_dev, parent.st_ino, stat.S_IMODE(parent.st_mode)
        raise ValueError(REASON_PUBLIC_EXISTS)
    finally:
        os.close(parent_fd)


def _build_public_report(
    result: SupplierS1ProgramResultV01,
    live_report: Mapping[str, object],
) -> bytes:
    if validate_supplier_s1_program_result_v01(result):
        raise ValueError(REASON_INVALID)
    source, statuses = _validate_live_report(live_report, result.execution_mode)
    rows = source["semantic_actor_calls"]
    counters = source["counters"]
    semantics = _accepted_semantic_objects(source)
    source_actor_ids = tuple(row["role"] for row in rows)
    source_summaries = tuple(_semantic_summary(semantic) for semantic in semantics)
    source_start_count = (
        counters["fake_provider_call_count"]
        if result.execution_mode == MODE_INJECTED
        else counters["real_provider_call_count"]
    )
    source_external_counts = (
        counters["real_provider_call_count"],
        counters["network_used_count"],
        counters["gemini_called_count"],
    )
    _require(source_actor_ids == result.actor_ids)
    _require(statuses == result.actor_validation_statuses)
    _require(source_summaries == result.actor_safe_summaries)
    _require(source["model"] == result.model_id)
    _require(source["provider_mode"] == result.provider_mode)
    _require(counters["semantic_actor_call_count"] == result.callback_count)
    _require(source_start_count == result.provider_start_count)
    _require(len(semantics) == result.provider_completion_count)
    _require(
        source_external_counts
        == (
            result.provider_call_count,
            result.network_call_count,
            result.gemini_call_count,
        )
    )
    safe_execution = _safe.build_supplier_water_filter_safe_execution_projection_v01(
        _safe_execution_source(source, result.execution_head)
    )
    if _safe.validate_supplier_water_filter_safe_execution_projection_v01(safe_execution):
        raise ValueError(REASON_SOURCE_INVALID)
    public = supplier_s1_program_result_to_plain_dict_v01(result)
    public["safe_execution_projection"] = _safe.supplier_water_filter_safe_execution_projection_to_plain_dict_v01(safe_execution)
    return _canonical_line(public)


def _write_public_report(
    content: bytes,
    expected_parent_identity: tuple[int, int, int],
) -> tuple[int, int]:
    parent_fd = _open_absolute_directory(CANONICAL_SAFE_REPORT_PATH.parent)
    identity: tuple[int, int] | None = None
    try:
        parent = os.fstat(parent_fd)
        observed_identity = (parent.st_dev, parent.st_ino, stat.S_IMODE(parent.st_mode))
        if observed_identity != expected_parent_identity:
            raise ValueError(REASON_WRITE_FAILED)
        identity = _write_owned_file(
            parent_fd,
            CANONICAL_SAFE_REPORT_PATH.name,
            content,
            0o400,
        )
    except Exception:
        try:
            os.close(parent_fd)
        except OSError:
            pass
        raise
    try:
        os.close(parent_fd)
    except OSError:
        if identity is not None:
            _cleanup_owned_public(identity)
        raise ValueError(REASON_WRITE_FAILED) from None
    return identity


def _cleanup_owned_public(identity: tuple[int, int]) -> None:
    parent_fd = _open_absolute_directory(CANONICAL_SAFE_REPORT_PATH.parent)
    try:
        entry = os.stat(
            CANONICAL_SAFE_REPORT_PATH.name,
            dir_fd=parent_fd,
            follow_symlinks=False,
        )
        if not stat.S_ISREG(entry.st_mode) or (entry.st_dev, entry.st_ino) != identity:
            raise ValueError(REASON_WRITE_FAILED)
        os.unlink(CANONICAL_SAFE_REPORT_PATH.name, dir_fd=parent_fd)
        os.fsync(parent_fd)
        try:
            os.stat(
                CANONICAL_SAFE_REPORT_PATH.name,
                dir_fd=parent_fd,
                follow_symlinks=False,
            )
        except FileNotFoundError:
            return
        raise ValueError(REASON_WRITE_FAILED)
    finally:
        os.close(parent_fd)


def _freeze_existing_attempt(root: Path) -> None:
    root_fd = _open_absolute_directory(root)
    raw_fd = -1
    try:
        try:
            raw_fd = os.open(
                RAW_ATTEMPT_DIRECTORY,
                os.O_RDONLY | os.O_DIRECTORY | getattr(os, "O_NOFOLLOW", 0),
                dir_fd=root_fd,
            )
        except FileNotFoundError:
            raw_fd = -1
        if raw_fd >= 0:
            for name in os.listdir(raw_fd):
                descriptor = os.open(
                    name,
                    os.O_RDONLY | getattr(os, "O_NOFOLLOW", 0),
                    dir_fd=raw_fd,
                )
                try:
                    if not stat.S_ISREG(os.fstat(descriptor).st_mode):
                        raise ValueError(REASON_WRITE_FAILED)
                    os.fchmod(descriptor, 0o400)
                    os.fsync(descriptor)
                finally:
                    os.close(descriptor)
        for name in (ATTEMPT_IDENTITY_FILE, PRIVATE_INVENTORY_FILE, GENERATION_GATE_FILE):
            try:
                descriptor = os.open(
                    name,
                    os.O_RDONLY | getattr(os, "O_NOFOLLOW", 0),
                    dir_fd=root_fd,
                )
            except FileNotFoundError:
                continue
            try:
                if not stat.S_ISREG(os.fstat(descriptor).st_mode):
                    raise ValueError(REASON_WRITE_FAILED)
                os.fchmod(descriptor, 0o400)
                os.fsync(descriptor)
            finally:
                os.close(descriptor)
        if raw_fd >= 0:
            os.fchmod(raw_fd, 0o500)
        os.fchmod(root_fd, 0o500)
        os.fsync(root_fd)
    finally:
        if raw_fd >= 0:
            os.close(raw_fd)
        os.close(root_fd)


def _execute_real_attempt(private_output_directory: str) -> SupplierS1ProgramResultV01:
    root = _validate_private_output(private_output_directory)
    public_parent_identity = _preflight_public_report_parent()
    execution_head = _git_head()
    root_identity: tuple[int, int] | None = None
    private_frozen = False
    result: SupplierS1ProgramResultV01 | None = None

    def record_root_identity(identity: tuple[int, int]) -> None:
        nonlocal root_identity
        root_identity = identity

    def invocation_root_is_current() -> bool:
        if root_identity is None:
            return False
        try:
            descriptor = _open_absolute_directory(root)
        except Exception:
            return False
        try:
            observed = os.fstat(descriptor)
            return (observed.st_dev, observed.st_ino) == root_identity
        finally:
            os.close(descriptor)

    try:
        _create_attempt_root(
            root,
            execution_head,
            root_created=record_root_identity,
        )
        result, live_report = _collect_with_context(
            provider=None,
            execution_head=execution_head,
            owner_approved_supplier_a=True,
            execution_mode=MODE_REAL,
            artifact_directory=str(root / RAW_ATTEMPT_DIRECTORY),
        )
        public_content = _build_public_report(result, live_report)
        _preserve_attempt(root=root, execution_head=execution_head, result=result, reason="")
        private_frozen = True
        _write_public_report(public_content, public_parent_identity)
        return result
    except Exception as error:
        preservation_error: Exception | None = None
        root_created = invocation_root_is_current()
        if root_created and not private_frozen:
            try:
                _preserve_attempt(
                    root=root,
                    execution_head=execution_head,
                    result=None,
                    reason=REASON_COLLECTION_FAILED,
                )
                private_frozen = True
            except Exception as freeze_error:
                preservation_error = freeze_error
        if root_created and not private_frozen:
            try:
                _freeze_existing_attempt(root)
            except Exception as freeze_error:
                preservation_error = freeze_error
        if preservation_error is not None:
            raise ValueError(REASON_WRITE_FAILED) from None
        raise ValueError(error.args[0] if error.args and type(error.args[0]) is str else REASON_UNEXPECTED) from None


class _CliError(Exception):
    pass


class _SanitizedParser(ArgumentParser):
    def error(self, message: str) -> None:
        raise _CliError from None


def _parser() -> _SanitizedParser:
    parser = _SanitizedParser(add_help=False, allow_abbrev=False)
    parser.add_argument("--real-provider", action="store_true", required=True)
    parser.add_argument("--attempt-number", required=True)
    parser.add_argument("--private-output-directory", required=True)
    parser.add_argument(_OWNER_APPROVAL_FLAG, action="store_true", required=True)
    return parser


def _reject_duplicate_options(argv: tuple[str, ...]) -> None:
    seen: set[str] = set()
    for token in argv:
        if type(token) is not str or not token.startswith("--"):
            continue
        option = token.split("=", 1)[0]
        if option in seen:
            raise _CliError
        seen.add(option)


def _terminal_summary(status: str, reason: str = "") -> str:
    return _canonical_line(
        {
            "final_status": status,
            "gate_id": GATE_ID,
            "official_evidence_eligible": status == STATUS_PASS,
            "reason_code": reason,
        }
    ).decode("utf-8").rstrip("\n")


def main(argv: list[str] | None = None) -> int:
    try:
        raw = tuple(sys.argv[1:] if argv is None else argv)
        _reject_duplicate_options(raw)
        args = _parser().parse_args(raw)
        if args.attempt_number != "1" or not args.real_provider or not args.owner_reviewed_supplier_a_approval:
            raise _CliError
        result = _execute_real_attempt(args.private_output_directory)
        if result.final_status != STATUS_PASS or validate_supplier_s1_program_result_v01(result):
            raise ValueError(REASON_INVALID)
        print(_terminal_summary(result.final_status))
        return 0
    except (_CliError, ValueError):
        print(_terminal_summary(STATUS_FAIL_CLOSED, REASON_INVALID))
        return 2
    except Exception:
        print(_terminal_summary(STATUS_FAIL_CLOSED, REASON_UNEXPECTED))
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
