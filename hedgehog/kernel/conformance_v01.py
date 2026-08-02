"""Machine-readable domain-neutral conformance evidence only.

This pure in-memory deterministic module provides no production certification,
truth proof, authority creation, permission creation, provider, network,
Gemini, filesystem, clock, randomness, domain execution, or real-world effect.
PASS is derived from validated observations and is never caller supplied.
"""

from __future__ import annotations

from dataclasses import dataclass as _dataclass
import re as _re

from hedgehog.kernel.integrity_replay_v01 import (
    canonical_json_bytes_v01 as _canonical_json_bytes_v01,
    domain_separated_sha256_hex_v01 as _domain_separated_sha256_hex_v01,
)

del annotations


MODULE_ID = "kernel_conformance_v01"
SLICE_ID = "domain_neutral_reference_kernel_gate1_g1e"
CONFORMANCE_VERSION = "v0.4"
_GATE1_CONFORMANCE_VERSION_V01 = "v0.1"
_G2A_CONFORMANCE_VERSION_V02 = "v0.2"
_G2B_CONFORMANCE_VERSION_V03 = "v0.3"

STATUS_PASS = "PASS"
STATUS_FAIL_CLOSED = "FAIL_CLOSED"
CONFORMANCE_STATUSES = (STATUS_PASS, STATUS_FAIL_CLOSED)

_GATE1_CATEGORY_IDS_V01 = (
    "DomainPackConformance",
    "RootAdapterConformance",
    "CorridorAdapterConformance",
    "SemanticProviderConformance",
    "ReplayCompatibility",
    "CryptoCompatibility",
    "SignerIsolationConformance",
    "TransitionRegistryConformance",
    "EffectFirewallConformance",
    "MultiRootConformance",
)
_G2A_CATEGORY_IDS_V02 = (
    *_GATE1_CATEGORY_IDS_V01,
    "ActionPacketLifecycleConformance",
)
_G2B_CATEGORY_IDS_V03 = (
    *_G2A_CATEGORY_IDS_V02,
    "DRSSemanticAddressReuseCertificateConformance",
)
CATEGORY_IDS = (
    *_G2B_CATEGORY_IDS_V03,
    "ExecutionModeRouterConformance",
)
DOMAIN_IDS = ("airline", "supplier_water_filter")
_GATE1_NEGATIVE_PROBE_IDS_V01 = (
    "manifest_hash_mismatch",
    "replay_hash_mismatch",
    "cross_root_signer_misuse",
    "unknown_transition",
    "root_hard_failure_not_overridden",
    "effect_firewall_scope_widening",
    "multiroot_duplicate_root",
    "multiroot_reserved_root",
    "airline_adapter_effect_access_forbidden",
    "supplier_adapter_effect_counter_rejected",
)
_G2A_NEGATIVE_PROBE_IDS_V02 = (
    *_GATE1_NEGATIVE_PROBE_IDS_V01,
    "action_packet_identity_forgery",
    "action_packet_time_forgery",
    "action_packet_illegal_transition",
    "action_packet_unknown_transition",
    "action_packet_root_authority_forgery",
    "action_packet_registry_authority_forgery",
    "action_packet_corridor_freshness_forgery",
    "action_packet_receipt_authority_forgery",
    "action_packet_replay_execution_forgery",
    "action_packet_cross_domain_substitution",
)
_G2B_NEGATIVE_PROBE_IDS_V03 = (
    "drs_address_identity_forgery",
    "drs_time_query_forgery",
    "drs_pointer_policy_forgery",
    "drs_eligibility_order_forgery",
    "drs_ranking_ineligible_selection_forgery",
    "drs_memory_descent_budget_forgery",
    "drs_root_shortcut_authority_forgery",
    "reuse_certificate_cross_binding_forgery",
    "drs_action_reuse_forgery",
    "drs_cross_domain_substitution",
)
_G2B_NEGATIVE_PROBE_IDS_CUMULATIVE_V03 = (
    *_G2A_NEGATIVE_PROBE_IDS_V02,
    *_G2B_NEGATIVE_PROBE_IDS_V03,
)
_G2C_NEGATIVE_PROBE_IDS_V04 = (
    "execution_mode_report_identity_forgery",
    "execution_mode_case_order_forgery",
    "execution_mode_selected_row_forgery",
    "execution_mode_root_outcome_forgery",
    "execution_mode_transition_lineage_forgery",
    "execution_mode_route_eligibility_forgery",
    "execution_mode_conflict_state_forgery",
    "execution_mode_cross_domain_substitution",
    "execution_mode_operation_order_forgery",
    "execution_mode_zero_operation_forgery",
)
NEGATIVE_PROBE_IDS = (
    *_G2B_NEGATIVE_PROBE_IDS_CUMULATIVE_V03,
    *_G2C_NEGATIVE_PROBE_IDS_V04,
)

_GATE1_ACTIVE_GAUNTLET_REFS_V01 = (
    "airline_deterministic_transaction_runtime",
    "all_layers_invariant_super_smoke",
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
)
_G2A_ACTIVE_GAUNTLET_REFS_V02 = (
    *_GATE1_ACTIVE_GAUNTLET_REFS_V01,
    "action_packet_lifecycle",
)
_G2B_ACTIVE_GAUNTLET_REFS_V03 = (
    *_G2A_ACTIVE_GAUNTLET_REFS_V02,
    "drs_semantic_address_and_reuse_certificate",
)
_ACTIVE_GAUNTLET_REFS = (
    *_G2B_ACTIVE_GAUNTLET_REFS_V03,
    "execution_mode_router",
)
_GATE1_EXPECTED_CATEGORY_CHECK_IDS_V01 = (
    (
        "DomainPackConformance",
        (
            "airline_domain_pass",
            "supplier_domain_pass",
            "shared_integrity_contract",
            "shared_replay_contract",
            "zero_kernel_law_changes",
        ),
    ),
    (
        "RootAdapterConformance",
        (
            "both_domains_preserve_root",
            "root_decision_act_pass",
            "domain_authority_creation_zero",
            "no_superroot",
        ),
    ),
    (
        "CorridorAdapterConformance",
        (
            "airline_corridor_pass",
            "supplier_mock_corridor_contained",
            "corridor_law_unchanged",
            "no_real_connector_or_action",
        ),
    ),
    (
        "SemanticProviderConformance",
        (
            "trust_model_pass",
            "semantic_work_pass",
            "providers_advisory_only",
            "external_calls_zero",
        ),
    ),
    (
        "ReplayCompatibility",
        (
            "airline_replay_pass",
            "supplier_replay_pass",
            "replay_rerun_counts_zero",
            "replay_creates_no_authority_or_effect",
        ),
    ),
    (
        "CryptoCompatibility",
        (
            "both_anchored_checks_pass",
            "both_unanchored_checks_explicit",
            "no_false_unanchored_pass",
            "no_production_signer_identity",
            "airline_signature_false",
            "root_attestation_deferred",
        ),
    ),
    (
        "SignerIsolationConformance",
        (
            "own_root_signatures_verify",
            "cross_root_misuse_blocked",
            "no_pki_claim",
            "no_key_persistence",
        ),
    ),
    (
        "TransitionRegistryConformance",
        (
            "registry_act_pass",
            "unknown_transition_blocked",
            "registry_immutable",
            "no_rule_injection",
        ),
    ),
    (
        "EffectFirewallConformance",
        (
            "firewall_act_pass",
            "widened_scope_blocked",
            "firewall_sole_effect_owner",
            "domain_adapters_no_effect_access",
            "real_effects_zero",
        ),
    ),
    (
        "MultiRootConformance",
        (
            "three_root_pass",
            "four_root_pass",
            "mixed_visible",
            "incomplete_visible",
            "duplicate_root_blocked",
            "reserved_root_blocked",
            "authority_transfer_zero",
            "permission_transfer_zero",
            "no_superroot",
        ),
    ),
)
_G2A_EXPECTED_CATEGORY_CHECK_IDS_V02 = (
    *_GATE1_EXPECTED_CATEGORY_CHECK_IDS_V01,
    (
        "ActionPacketLifecycleConformance",
        (
            "canonical_identity",
            "canonical_time",
            "legal_transitions",
            "unknown_transition_block",
            "root_only_authority_changes",
            "registry_non_authority",
            "corridor_freshness_enforcement",
            "receipt_non_authority",
            "replay_non_execution",
            "cross_domain_invariance",
        ),
    ),
)
_G2B_EXPECTED_CATEGORY_CHECK_IDS_V03 = (
    *_G2A_EXPECTED_CATEGORY_CHECK_IDS_V02,
    (
        "DRSSemanticAddressReuseCertificateConformance",
        (
            "canonical_identity",
            "time",
            "pointer_policy",
            "eligibility",
            "ranking",
            "descent",
            "root_shortcut",
            "certificate_non_authority",
            "action_boundary",
            "cross_domain_invariance",
        ),
    ),
)
_G2C_EXPECTED_CHECK_IDS_V04 = (
    "two_domain_ten_case_report",
    "all_five_root_outcomes",
    "seventeen_step_order",
    "source_binding_and_derived_query",
    "one_abi_profile_and_stage_bundles",
    "one_transition_profile_and_root_lineage",
    "route_eligibility_and_direct_bypass",
    "package_facade_and_import_boundary",
    "negative_matrix_and_domain_invariance",
    "zero_operations",
)
_EXPECTED_CATEGORY_CHECK_IDS = (
    *_G2B_EXPECTED_CATEGORY_CHECK_IDS_V03,
    ("ExecutionModeRouterConformance", _G2C_EXPECTED_CHECK_IDS_V04),
)
_EXPECTED_DOMAIN_GEOMETRY = (
    (
        "airline",
        "hedgehog.domains.airline.kernel_adapter_v01",
        (
            "demo.run_living_gauntlet_v01:"
            "collect_generic_integrity_replay_gauntlet_act_v01"
        ),
        (
            "airline_act_executed",
            "airline_adapter_validated",
            "airline_generic_unanchored_exact",
            "airline_generic_anchored_pass",
            "airline_generic_replay_pass",
            "airline_causal_bundle_valid",
            "airline_root_authority_preserved",
            "airline_effect_access_none",
            "airline_real_effects_zero",
            "airline_frozen_reference_remains_evidence_only",
            "airline_signature_verified_remains_false",
            "airline_root_attestation_not_claimed",
        ),
        (
            "hedgehog/domains/airline/kernel_adapter_v01.py",
            "tests/test_airline_kernel_adapter_v01.py",
        ),
        ("limitation_g1d1_frozen_airline_projection_only",),
    ),
    (
        "supplier_water_filter",
        "hedgehog.domains.supplier_water_filter.kernel_adapter_v01",
        (
            "demo.run_living_gauntlet_v01:"
            "collect_supplier_water_filter_portability_gauntlet_act_v01"
        ),
        (
            "supplier_act_executed",
            "supplier_exact_source_contract",
            "supplier_adapter_validated",
            "supplier_generic_unanchored_exact",
            "supplier_generic_anchored_pass",
            "supplier_generic_replay_pass",
            "supplier_causal_bundle_valid",
            "supplier_multiroot_mixed_visible",
            "supplier_root_authority_preserved",
            "supplier_effect_access_none",
            "supplier_real_effects_zero",
            "supplier_b_blocked",
            "shipment_held",
            "receipt_evidence_only",
        ),
        (
            "hedgehog/domains/supplier_water_filter/kernel_adapter_v01.py",
            "tests/test_supplier_water_filter_kernel_adapter_v01.py",
        ),
        ("limitation_g1d2_supplier_water_filter_projection_only",),
    ),
)
_GATE1_EXPECTED_NEGATIVE_GEOMETRY_V01 = (
    (
        "manifest_hash_mismatch",
        "hedgehog.kernel.integrity_replay_v01.verify_artifact_manifest_v01",
        ("expected_manifest_hash_mismatch",),
    ),
    (
        "replay_hash_mismatch",
        "hedgehog.kernel.integrity_replay_v01.verify_artifact_replay_v01",
        ("replay_manifest_verification_failed",),
    ),
    (
        "cross_root_signer_misuse",
        "hedgehog.kernel.root_signer_isolation_v01.sign_root_owned_commitment_v01",
        ("signer_root_mismatch",),
    ),
    (
        "unknown_transition",
        "hedgehog.kernel.transition_registry_v01.lookup_transition_v01",
        ("unknown_transition",),
    ),
    (
        "root_hard_failure_not_overridden",
        "hedgehog.kernel.root_decision_v01.validate_root_decision_result_v01",
        ("hard_scope_violation",),
    ),
    (
        "effect_firewall_scope_widening",
        "hedgehog.kernel.effect_firewall_v01.authorize_effect_request_v01",
        ("scope_expansion_forbidden",),
    ),
    (
        "multiroot_duplicate_root",
        "hedgehog.kernel.multiroot_v01.validate_multiroot_v01",
        ("multiroot_duplicate_root",),
    ),
    (
        "multiroot_reserved_root",
        "hedgehog.kernel.multiroot_v01.validate_multiroot_v01",
        ("multiroot_super_root_forbidden",),
    ),
    (
        "airline_adapter_effect_access_forbidden",
        "hedgehog.domains.airline.kernel_adapter_v01",
        ("airline_adapter_effect_access_forbidden",),
    ),
    (
        "supplier_adapter_effect_counter_rejected",
        (
            "demo.run_living_gauntlet_v01:"
            "collect_supplier_water_filter_portability_gauntlet_act_v01"
        ),
        ("supplier_water_filter_effect_creation_forbidden",),
    ),
)
_ACTION_PACKET_REPORT_VALIDATOR_TARGET_V01 = (
    "demo.run_action_commit_packet_lifecycle_g2_a_v01."
    "validate_action_commit_packet_lifecycle_g2_a_report_v01"
)
_ACTION_PACKET_REPORT_REJECTION_REASONS_V01 = ("g2a5_report_fail_closed",)
_G2A_EXPECTED_NEGATIVE_GEOMETRY_V02 = (
    *_GATE1_EXPECTED_NEGATIVE_GEOMETRY_V01,
    *(
        (
            probe_id,
            _ACTION_PACKET_REPORT_VALIDATOR_TARGET_V01,
            _ACTION_PACKET_REPORT_REJECTION_REASONS_V01,
        )
        for probe_id in _G2A_NEGATIVE_PROBE_IDS_V02[
            len(_GATE1_NEGATIVE_PROBE_IDS_V01) :
        ]
    ),
)
_G2B_REPORT_VALIDATOR_TARGET_V01 = (
    "demo.run_drs_semantic_address_reuse_certificate_g2_b_v01."
    "validate_drs_semantic_address_reuse_certificate_g2_b_report_v01"
)
_G2B_REPORT_REJECTION_REASONS_V01 = ("g2b_report_fail_closed",)
_G2B_EXPECTED_NEGATIVE_GEOMETRY_V03 = (
    *_G2A_EXPECTED_NEGATIVE_GEOMETRY_V02,
    *(
        (
            probe_id,
            _G2B_REPORT_VALIDATOR_TARGET_V01,
            _G2B_REPORT_REJECTION_REASONS_V01,
        )
        for probe_id in _G2B_NEGATIVE_PROBE_IDS_V03
    ),
)
_G2C_REPORT_VALIDATOR_TARGET_V01 = (
    "demo.run_execution_mode_router_g2_c_v01."
    "validate_execution_mode_router_g2_c_report_v01"
)
_G2C_EXPECTED_NEGATIVE_REASONS_V04 = (
    ("g2c5_report_identity_invalid",),
    ("g2c5_case_order_invalid", "g2c5_report_identity_invalid"),
    ("g2c5_case_result_invalid", "g2c5_report_identity_invalid"),
    ("g2c5_case_result_invalid", "g2c5_report_identity_invalid"),
    ("g2c5_case_result_invalid", "g2c5_report_identity_invalid"),
    ("g2c5_case_result_invalid", "g2c5_report_identity_invalid"),
    ("g2c5_case_result_invalid", "g2c5_report_identity_invalid"),
    ("g2c5_case_result_invalid", "g2c5_report_identity_invalid"),
    ("g2c5_case_result_invalid", "g2c5_report_identity_invalid"),
    ("g2c5_zero_operation_invalid", "g2c5_report_identity_invalid"),
)
_EXPECTED_NEGATIVE_GEOMETRY = (
    *_G2B_EXPECTED_NEGATIVE_GEOMETRY_V03,
    *(
        (probe_id, _G2C_REPORT_VALIDATOR_TARGET_V01, expected_reasons)
        for probe_id, expected_reasons in zip(
            _G2C_NEGATIVE_PROBE_IDS_V04,
            _G2C_EXPECTED_NEGATIVE_REASONS_V04,
            strict=True,
        )
    ),
)
_CATEGORY_DOMAIN = "hedgehog.kernel.conformance.category_result.v01"
_DOMAIN_DOMAIN = "hedgehog.kernel.conformance.domain_result.v01"
_NEGATIVE_DOMAIN = "hedgehog.kernel.conformance.negative_result.v01"
_REPORT_DOMAIN = "hedgehog.kernel.conformance.report.v01"
_COMMIT_PATTERN = _re.compile(r"^[0-9a-f]{7,40}$")


@_dataclass(frozen=True, slots=True)
class ConformanceCountersV01:
    category_result_count: int
    category_pass_count: int
    domain_result_count: int
    domain_pass_count: int
    negative_result_count: int
    negative_pass_count: int
    active_gauntlet_ref_count: int
    evidence_ref_count: int
    provider_call_count: int
    network_call_count: int
    gemini_call_count: int
    created_authority_count: int
    created_permission_count: int
    real_world_effects_count: int


@_dataclass(frozen=True, slots=True)
class ConformanceCategoryResultV01:
    result_id: str
    category_id: str
    required_check_ids: tuple[str, ...]
    passed_check_ids: tuple[str, ...]
    failed_check_ids: tuple[str, ...]
    evidence_refs: tuple[str, ...]
    limitation_refs: tuple[str, ...]
    status: str
    real_world_effects_count: int


@_dataclass(frozen=True, slots=True)
class DomainConformanceResultV01:
    result_id: str
    domain_id: str
    adapter_ref: str
    source_ref: str
    required_check_ids: tuple[str, ...]
    passed_check_ids: tuple[str, ...]
    failed_check_ids: tuple[str, ...]
    evidence_refs: tuple[str, ...]
    limitation_refs: tuple[str, ...]
    provider_call_count: int
    network_call_count: int
    gemini_call_count: int
    real_world_effects_count: int
    status: str


@_dataclass(frozen=True, slots=True)
class NegativeConformanceResultV01:
    result_id: str
    probe_id: str
    target_contract: str
    expected_reason_codes: tuple[str, ...]
    observed_reason_codes: tuple[str, ...]
    blocked: bool
    evidence_refs: tuple[str, ...]
    status: str
    real_world_effects_count: int


@_dataclass(frozen=True, slots=True)
class KernelConformanceReportV01:
    report_id: str
    conformance_version: str
    implementation_commit: str
    category_results: tuple[ConformanceCategoryResultV01, ...]
    domain_results: tuple[DomainConformanceResultV01, ...]
    negative_test_results: tuple[NegativeConformanceResultV01, ...]
    active_gauntlet_refs: tuple[str, ...]
    evidence_refs: tuple[str, ...]
    limitations: tuple[str, ...]
    counters: ConformanceCountersV01
    final_status: str


def build_conformance_category_result_v01(
    *,
    category_id: str,
    check_results: tuple[tuple[str, bool], ...],
    evidence_refs: tuple[str, ...],
    limitation_refs: tuple[str, ...],
) -> ConformanceCategoryResultV01:
    try:
        checks = _require_check_results(check_results)
        _require_member(category_id, CATEGORY_IDS)
        _require_text_tuple(evidence_refs, allow_empty=False)
        _require_text_tuple(limitation_refs, allow_empty=False)
        required = tuple(item[0] for item in checks)
        passed = tuple(item[0] for item in checks if item[1])
        failed = tuple(item[0] for item in checks if not item[1])
        status = STATUS_PASS if not failed else STATUS_FAIL_CLOSED
        provisional = ConformanceCategoryResultV01(
            result_id="0" * 64,
            category_id=category_id,
            required_check_ids=required,
            passed_check_ids=passed,
            failed_check_ids=failed,
            evidence_refs=evidence_refs,
            limitation_refs=limitation_refs,
            status=status,
            real_world_effects_count=0,
        )
        return _replace_category_id(provisional)
    except Exception:
        raise ValueError("conformance_category_invalid") from None


def validate_conformance_category_result_v01(
    result: object,
) -> tuple[str, ...]:
    try:
        return _category_errors(result)
    except Exception:
        return ("conformance_unexpected_exception",)


def build_domain_conformance_result_v01(
    *,
    domain_id: str,
    adapter_ref: str,
    source_ref: str,
    check_results: tuple[tuple[str, bool], ...],
    evidence_refs: tuple[str, ...],
    limitation_refs: tuple[str, ...],
    provider_call_count: int,
    network_call_count: int,
    gemini_call_count: int,
    real_world_effects_count: int,
) -> DomainConformanceResultV01:
    try:
        checks = _require_check_results(check_results)
        _require_member(domain_id, DOMAIN_IDS)
        _require_text(adapter_ref)
        _require_text(source_ref)
        _require_text_tuple(evidence_refs, allow_empty=False)
        _require_text_tuple(limitation_refs, allow_empty=False)
        counts = (
            provider_call_count,
            network_call_count,
            gemini_call_count,
            real_world_effects_count,
        )
        if any(not _valid_count(item) for item in counts):
            raise ValueError
        required = tuple(item[0] for item in checks)
        passed = tuple(item[0] for item in checks if item[1])
        failed = tuple(item[0] for item in checks if not item[1])
        status = (
            STATUS_PASS
            if not failed and all(item == 0 for item in counts)
            else STATUS_FAIL_CLOSED
        )
        provisional = DomainConformanceResultV01(
            result_id="0" * 64,
            domain_id=domain_id,
            adapter_ref=adapter_ref,
            source_ref=source_ref,
            required_check_ids=required,
            passed_check_ids=passed,
            failed_check_ids=failed,
            evidence_refs=evidence_refs,
            limitation_refs=limitation_refs,
            provider_call_count=provider_call_count,
            network_call_count=network_call_count,
            gemini_call_count=gemini_call_count,
            real_world_effects_count=real_world_effects_count,
            status=status,
        )
        return _replace_domain_id(provisional)
    except Exception:
        raise ValueError("domain_conformance_invalid") from None


def validate_domain_conformance_result_v01(
    result: object,
) -> tuple[str, ...]:
    try:
        return _domain_errors(result)
    except Exception:
        return ("conformance_unexpected_exception",)


def build_negative_conformance_result_v01(
    *,
    probe_id: str,
    target_contract: str,
    expected_reason_codes: tuple[str, ...],
    observed_reason_codes: tuple[str, ...],
    blocked: bool,
    evidence_refs: tuple[str, ...],
    real_world_effects_count: int,
) -> NegativeConformanceResultV01:
    try:
        _require_member(probe_id, NEGATIVE_PROBE_IDS)
        _require_text(target_contract)
        _require_text_tuple(expected_reason_codes, allow_empty=False)
        _require_text_tuple(observed_reason_codes, allow_empty=True)
        _require_text_tuple(evidence_refs, allow_empty=False)
        if type(blocked) is not bool or not _valid_count(real_world_effects_count):
            raise ValueError
        status = (
            STATUS_PASS
            if blocked
            and all(item in observed_reason_codes for item in expected_reason_codes)
            and real_world_effects_count == 0
            else STATUS_FAIL_CLOSED
        )
        provisional = NegativeConformanceResultV01(
            result_id="0" * 64,
            probe_id=probe_id,
            target_contract=target_contract,
            expected_reason_codes=expected_reason_codes,
            observed_reason_codes=observed_reason_codes,
            blocked=blocked,
            evidence_refs=evidence_refs,
            status=status,
            real_world_effects_count=real_world_effects_count,
        )
        return _replace_negative_id(provisional)
    except Exception:
        raise ValueError("negative_conformance_invalid") from None


def validate_negative_conformance_result_v01(
    result: object,
) -> tuple[str, ...]:
    try:
        return _negative_errors(result)
    except Exception:
        return ("conformance_unexpected_exception",)


def validate_conformance_counters_v01(
    counters: object,
) -> tuple[str, ...]:
    try:
        if type(counters) is not ConformanceCountersV01:
            return ("conformance_counters_invalid",)
        if any(not _valid_count(item) for item in _counter_values(counters)):
            return ("conformance_counters_invalid",)
        if (
            counters.category_pass_count > counters.category_result_count
            or counters.domain_pass_count > counters.domain_result_count
            or counters.negative_pass_count > counters.negative_result_count
        ):
            return ("conformance_counters_invalid",)
        return ()
    except Exception:
        return ("conformance_unexpected_exception",)


def build_kernel_conformance_report_v01(
    *,
    implementation_commit: str,
    category_results: tuple[ConformanceCategoryResultV01, ...],
    domain_results: tuple[DomainConformanceResultV01, ...],
    negative_test_results: tuple[NegativeConformanceResultV01, ...],
    active_gauntlet_refs: tuple[str, ...],
    evidence_refs: tuple[str, ...],
    limitations: tuple[str, ...],
) -> KernelConformanceReportV01:
    try:
        _require_commit(implementation_commit)
        _require_report_geometry(
            category_results,
            domain_results,
            negative_test_results,
            active_gauntlet_refs,
        )
        if any(validate_conformance_category_result_v01(item) for item in category_results):
            raise ValueError
        if any(validate_domain_conformance_result_v01(item) for item in domain_results):
            raise ValueError
        if any(validate_negative_conformance_result_v01(item) for item in negative_test_results):
            raise ValueError
        _require_text_tuple(evidence_refs, allow_empty=False)
        _require_text_tuple(limitations, allow_empty=False)
        counters = _derive_counters(
            category_results,
            domain_results,
            negative_test_results,
            active_gauntlet_refs,
            evidence_refs,
        )
        final_status = _derive_report_status(
            category_results,
            domain_results,
            negative_test_results,
            counters,
        )
        provisional = KernelConformanceReportV01(
            report_id="0" * 64,
            conformance_version=CONFORMANCE_VERSION,
            implementation_commit=implementation_commit,
            category_results=category_results,
            domain_results=domain_results,
            negative_test_results=negative_test_results,
            active_gauntlet_refs=active_gauntlet_refs,
            evidence_refs=evidence_refs,
            limitations=limitations,
            counters=counters,
            final_status=final_status,
        )
        return _replace_report_id(provisional)
    except Exception:
        raise ValueError("kernel_conformance_report_invalid") from None


def validate_kernel_conformance_report_v01(
    report: object,
) -> tuple[str, ...]:
    try:
        return _report_errors(report)
    except Exception:
        return ("conformance_unexpected_exception",)


def conformance_counters_to_plain_dict_v01(
    counters: ConformanceCountersV01,
) -> dict[str, object]:
    try:
        if validate_conformance_counters_v01(counters):
            raise ValueError
        result = _counters_plain(counters)
        _canonical_json_bytes_v01(result)
        return result
    except Exception:
        raise ValueError("conformance_counters_invalid") from None


def conformance_category_result_to_plain_dict_v01(
    result: ConformanceCategoryResultV01,
) -> dict[str, object]:
    try:
        if validate_conformance_category_result_v01(result):
            raise ValueError
        plain = _category_plain(result)
        _canonical_json_bytes_v01(plain)
        return plain
    except Exception:
        raise ValueError("conformance_category_invalid") from None


def domain_conformance_result_to_plain_dict_v01(
    result: DomainConformanceResultV01,
) -> dict[str, object]:
    try:
        if validate_domain_conformance_result_v01(result):
            raise ValueError
        plain = _domain_plain(result)
        _canonical_json_bytes_v01(plain)
        return plain
    except Exception:
        raise ValueError("domain_conformance_invalid") from None


def negative_conformance_result_to_plain_dict_v01(
    result: NegativeConformanceResultV01,
) -> dict[str, object]:
    try:
        if validate_negative_conformance_result_v01(result):
            raise ValueError
        plain = _negative_plain(result)
        _canonical_json_bytes_v01(plain)
        return plain
    except Exception:
        raise ValueError("negative_conformance_invalid") from None


def kernel_conformance_report_to_plain_dict_v01(
    report: KernelConformanceReportV01,
) -> dict[str, object]:
    try:
        if validate_kernel_conformance_report_v01(report):
            raise ValueError
        plain = _report_plain(report)
        _canonical_json_bytes_v01(plain)
        return plain
    except Exception:
        raise ValueError("kernel_conformance_report_invalid") from None


def _category_errors(result: object) -> tuple[str, ...]:
    if type(result) is not ConformanceCategoryResultV01:
        return ("conformance_category_invalid",)
    errors: list[str] = []
    if (
        not _valid_text(result.result_id)
        or not _valid_text(result.category_id)
        or result.category_id not in CATEGORY_IDS
        or type(result.status) is not str
        or result.status not in CONFORMANCE_STATUSES
    ):
        errors.append("conformance_category_invalid")
    if not _partition_valid(
        result.required_check_ids,
        result.passed_check_ids,
        result.failed_check_ids,
    ):
        errors.append("conformance_check_partition_invalid")
    if not _valid_text_tuple(result.evidence_refs, allow_empty=False) or not _valid_text_tuple(
        result.limitation_refs, allow_empty=False
    ):
        errors.append("conformance_category_invalid")
    if not _valid_count(result.real_world_effects_count):
        errors.append("conformance_category_invalid")
    expected_status = (
        STATUS_PASS
        if not result.failed_check_ids and result.real_world_effects_count == 0
        else STATUS_FAIL_CLOSED
    )
    if result.status != expected_status:
        errors.append("conformance_status_mismatch")
    try:
        if result.result_id != _category_id(result):
            errors.append("conformance_identity_mismatch")
    except Exception:
        errors.append("conformance_category_invalid")
    return _dedupe(errors)


def _domain_errors(result: object) -> tuple[str, ...]:
    if type(result) is not DomainConformanceResultV01:
        return ("domain_conformance_invalid",)
    errors: list[str] = []
    if (
        not _valid_text(result.result_id)
        or not _valid_text(result.domain_id)
        or result.domain_id not in DOMAIN_IDS
        or not _valid_text(result.adapter_ref)
        or not _valid_text(result.source_ref)
        or type(result.status) is not str
        or result.status not in CONFORMANCE_STATUSES
    ):
        errors.append("domain_conformance_invalid")
    if not _partition_valid(
        result.required_check_ids,
        result.passed_check_ids,
        result.failed_check_ids,
    ):
        errors.append("conformance_check_partition_invalid")
    if not _valid_text_tuple(result.evidence_refs, allow_empty=False) or not _valid_text_tuple(
        result.limitation_refs, allow_empty=False
    ):
        errors.append("domain_conformance_invalid")
    counts = (
        result.provider_call_count,
        result.network_call_count,
        result.gemini_call_count,
        result.real_world_effects_count,
    )
    if any(not _valid_count(item) for item in counts):
        errors.append("domain_conformance_invalid")
    expected_status = (
        STATUS_PASS
        if not result.failed_check_ids
        and all(type(item) is int and item == 0 for item in counts)
        else STATUS_FAIL_CLOSED
    )
    if result.status != expected_status:
        errors.append("conformance_status_mismatch")
    try:
        if result.result_id != _domain_id(result):
            errors.append("conformance_identity_mismatch")
    except Exception:
        errors.append("domain_conformance_invalid")
    return _dedupe(errors)


def _negative_errors(result: object) -> tuple[str, ...]:
    if type(result) is not NegativeConformanceResultV01:
        return ("negative_conformance_invalid",)
    errors: list[str] = []
    if (
        not _valid_text(result.result_id)
        or not _valid_text(result.probe_id)
        or result.probe_id not in NEGATIVE_PROBE_IDS
        or not _valid_text(result.target_contract)
        or type(result.status) is not str
        or result.status not in CONFORMANCE_STATUSES
    ):
        errors.append("negative_conformance_invalid")
    if not _valid_text_tuple(
        result.expected_reason_codes, allow_empty=False
    ) or not _valid_text_tuple(result.observed_reason_codes, allow_empty=True):
        errors.append("negative_conformance_invalid")
    if not _valid_text_tuple(result.evidence_refs, allow_empty=False):
        errors.append("negative_conformance_invalid")
    if type(result.blocked) is not bool or not _valid_count(
        result.real_world_effects_count
    ):
        errors.append("negative_conformance_invalid")
    expected_status = (
        STATUS_PASS
        if result.blocked
        and all(item in result.observed_reason_codes for item in result.expected_reason_codes)
        and result.real_world_effects_count == 0
        else STATUS_FAIL_CLOSED
    )
    if result.status != expected_status:
        errors.append("conformance_status_mismatch")
    try:
        if result.result_id != _negative_id(result):
            errors.append("conformance_identity_mismatch")
    except Exception:
        errors.append("negative_conformance_invalid")
    return _dedupe(errors)


def _report_errors(report: object) -> tuple[str, ...]:
    if type(report) is not KernelConformanceReportV01:
        return ("kernel_conformance_report_invalid",)
    errors: list[str] = []
    if (
        not _valid_text(report.report_id)
        or type(report.conformance_version) is not str
        or report.conformance_version
        not in (
            _GATE1_CONFORMANCE_VERSION_V01,
            _G2A_CONFORMANCE_VERSION_V02,
            _G2B_CONFORMANCE_VERSION_V03,
            CONFORMANCE_VERSION,
        )
        or not _valid_commit(report.implementation_commit)
        or type(report.final_status) is not str
        or report.final_status not in CONFORMANCE_STATUSES
    ):
        errors.append("kernel_conformance_report_invalid")
    try:
        _require_report_geometry(
            report.category_results,
            report.domain_results,
            report.negative_test_results,
            report.active_gauntlet_refs,
            conformance_version=report.conformance_version,
        )
    except Exception:
        errors.append("conformance_report_geometry_invalid")
    if not _valid_text_tuple(report.evidence_refs, allow_empty=False) or not _valid_text_tuple(
        report.limitations, allow_empty=False
    ):
        errors.append("kernel_conformance_report_invalid")
    if type(report.category_results) is tuple:
        for item in report.category_results:
            errors.extend(validate_conformance_category_result_v01(item))
    if type(report.domain_results) is tuple:
        for item in report.domain_results:
            errors.extend(validate_domain_conformance_result_v01(item))
    if type(report.negative_test_results) is tuple:
        for item in report.negative_test_results:
            errors.extend(validate_negative_conformance_result_v01(item))
    errors.extend(validate_conformance_counters_v01(report.counters))
    if not errors:
        expected_counters = _derive_counters(
            report.category_results,
            report.domain_results,
            report.negative_test_results,
            report.active_gauntlet_refs,
            report.evidence_refs,
        )
        if report.counters != expected_counters:
            errors.append("conformance_counter_mismatch")
        expected_status = _derive_report_status(
            report.category_results,
            report.domain_results,
            report.negative_test_results,
            expected_counters,
        )
        if report.final_status != expected_status:
            errors.append("conformance_status_mismatch")
    elif report.final_status not in CONFORMANCE_STATUSES:
        errors.append("conformance_status_mismatch")
    try:
        if report.report_id != _report_id(report):
            errors.append("conformance_identity_mismatch")
    except Exception:
        errors.append("kernel_conformance_report_invalid")
    return _dedupe(errors)


def _require_report_geometry(
    categories: object,
    domains: object,
    negatives: object,
    active_refs: object,
    *,
    conformance_version: str = CONFORMANCE_VERSION,
) -> None:
    if conformance_version == _GATE1_CONFORMANCE_VERSION_V01:
        category_ids = _GATE1_CATEGORY_IDS_V01
        negative_probe_ids = _GATE1_NEGATIVE_PROBE_IDS_V01
        expected_active_refs = _GATE1_ACTIVE_GAUNTLET_REFS_V01
        expected_category_geometry = _GATE1_EXPECTED_CATEGORY_CHECK_IDS_V01
        expected_negative_geometry = _GATE1_EXPECTED_NEGATIVE_GEOMETRY_V01
    elif conformance_version == _G2A_CONFORMANCE_VERSION_V02:
        category_ids = _G2A_CATEGORY_IDS_V02
        negative_probe_ids = _G2A_NEGATIVE_PROBE_IDS_V02
        expected_active_refs = _G2A_ACTIVE_GAUNTLET_REFS_V02
        expected_category_geometry = _G2A_EXPECTED_CATEGORY_CHECK_IDS_V02
        expected_negative_geometry = _G2A_EXPECTED_NEGATIVE_GEOMETRY_V02
    elif conformance_version == _G2B_CONFORMANCE_VERSION_V03:
        category_ids = _G2B_CATEGORY_IDS_V03
        negative_probe_ids = _G2B_NEGATIVE_PROBE_IDS_CUMULATIVE_V03
        expected_active_refs = _G2B_ACTIVE_GAUNTLET_REFS_V03
        expected_category_geometry = _G2B_EXPECTED_CATEGORY_CHECK_IDS_V03
        expected_negative_geometry = _G2B_EXPECTED_NEGATIVE_GEOMETRY_V03
    elif conformance_version == CONFORMANCE_VERSION:
        category_ids = CATEGORY_IDS
        negative_probe_ids = NEGATIVE_PROBE_IDS
        expected_active_refs = _ACTIVE_GAUNTLET_REFS
        expected_category_geometry = _EXPECTED_CATEGORY_CHECK_IDS
        expected_negative_geometry = _EXPECTED_NEGATIVE_GEOMETRY
    else:
        raise ValueError
    if type(categories) is not tuple or tuple(
        item.category_id if type(item) is ConformanceCategoryResultV01 else None
        for item in categories
    ) != category_ids:
        raise ValueError
    if type(domains) is not tuple or tuple(
        item.domain_id if type(item) is DomainConformanceResultV01 else None
        for item in domains
    ) != DOMAIN_IDS:
        raise ValueError
    if type(negatives) is not tuple or tuple(
        item.probe_id if type(item) is NegativeConformanceResultV01 else None
        for item in negatives
    ) != negative_probe_ids:
        raise ValueError
    if (
        not _valid_text_tuple(active_refs, allow_empty=False)
        or active_refs != expected_active_refs
    ):
        raise ValueError
    for item, (category_id, required_check_ids) in zip(
        categories, expected_category_geometry
    ):
        if (
            item.category_id != category_id
            or item.required_check_ids != required_check_ids
        ):
            raise ValueError
        if category_id == "ActionPacketLifecycleConformance" and (
            item.evidence_refs
            != ("runtime:kernel_conformance:ActionPacketLifecycleConformance",)
            or item.limitation_refs
            != (
                "limitation_g2a6_deterministic_local_actionpacket_lifecycle_only",
            )
        ):
            raise ValueError
        if category_id == "DRSSemanticAddressReuseCertificateConformance" and (
            item.evidence_refs
            != (
                "runtime:kernel_conformance:"
                "DRSSemanticAddressReuseCertificateConformance",
            )
            or item.limitation_refs
            != (
                "limitation_g2b6_deterministic_local_drs_semantic_reuse_only",
            )
        ):
            raise ValueError
        if category_id == "ExecutionModeRouterConformance" and (
            item.evidence_refs
            != ("runtime:kernel_conformance:ExecutionModeRouterConformance",)
            or item.limitation_refs
            != (
                "limitation_g2c6_deterministic_two_domain_"
                "execution_mode_router_only",
            )
        ):
            raise ValueError
    for item, expected in zip(domains, _EXPECTED_DOMAIN_GEOMETRY):
        (
            domain_id,
            adapter_ref,
            source_ref,
            required_check_ids,
            evidence_refs,
            limitation_refs,
        ) = expected
        if (
            item.domain_id != domain_id
            or item.adapter_ref != adapter_ref
            or item.source_ref != source_ref
            or item.required_check_ids != required_check_ids
            or item.evidence_refs != evidence_refs
            or item.limitation_refs != limitation_refs
        ):
            raise ValueError
    for item, (probe_id, target_contract, expected_reasons) in zip(
        negatives, expected_negative_geometry
    ):
        if (
            item.probe_id != probe_id
            or item.target_contract != target_contract
            or item.expected_reason_codes != expected_reasons
            or not _valid_text_tuple(item.evidence_refs, allow_empty=False)
        ):
            raise ValueError
        if probe_id in _G2A_NEGATIVE_PROBE_IDS_V02[
            len(_GATE1_NEGATIVE_PROBE_IDS_V01) :
        ] and item.evidence_refs != (
            "demo/run_action_commit_packet_lifecycle_g2_a_v01.py",
        ):
            raise ValueError
        if probe_id in _G2B_NEGATIVE_PROBE_IDS_V03 and item.evidence_refs != (
            "demo/run_drs_semantic_address_reuse_certificate_g2_b_v01.py",
        ):
            raise ValueError
        if probe_id in _G2C_NEGATIVE_PROBE_IDS_V04 and item.evidence_refs != (
            "demo/run_execution_mode_router_g2_c_v01.py",
        ):
            raise ValueError
    if len({item.result_id for item in categories}) != len(categories):
        raise ValueError
    if len({item.result_id for item in domains}) != len(domains):
        raise ValueError
    if len({item.result_id for item in negatives}) != len(negatives):
        raise ValueError


def _derive_counters(
    categories: tuple[ConformanceCategoryResultV01, ...],
    domains: tuple[DomainConformanceResultV01, ...],
    negatives: tuple[NegativeConformanceResultV01, ...],
    active_refs: tuple[str, ...],
    evidence_refs: tuple[str, ...],
) -> ConformanceCountersV01:
    return ConformanceCountersV01(
        category_result_count=len(categories),
        category_pass_count=sum(item.status == STATUS_PASS for item in categories),
        domain_result_count=len(domains),
        domain_pass_count=sum(item.status == STATUS_PASS for item in domains),
        negative_result_count=len(negatives),
        negative_pass_count=sum(item.status == STATUS_PASS for item in negatives),
        active_gauntlet_ref_count=len(active_refs),
        evidence_ref_count=len(evidence_refs),
        provider_call_count=sum(item.provider_call_count for item in domains),
        network_call_count=sum(item.network_call_count for item in domains),
        gemini_call_count=sum(item.gemini_call_count for item in domains),
        created_authority_count=0,
        created_permission_count=0,
        real_world_effects_count=(
            sum(item.real_world_effects_count for item in categories)
            + sum(item.real_world_effects_count for item in domains)
            + sum(item.real_world_effects_count for item in negatives)
        ),
    )


def _derive_report_status(
    categories: tuple[ConformanceCategoryResultV01, ...],
    domains: tuple[DomainConformanceResultV01, ...],
    negatives: tuple[NegativeConformanceResultV01, ...],
    counters: ConformanceCountersV01,
) -> str:
    all_pass = all(
        item.status == STATUS_PASS for item in (*categories, *domains, *negatives)
    )
    zero_boundary = all(
        item == 0
        for item in (
            counters.provider_call_count,
            counters.network_call_count,
            counters.gemini_call_count,
            counters.created_authority_count,
            counters.created_permission_count,
            counters.real_world_effects_count,
        )
    )
    return STATUS_PASS if all_pass and zero_boundary else STATUS_FAIL_CLOSED


def _require_check_results(value: object) -> tuple[tuple[str, bool], ...]:
    if type(value) is not tuple or not value:
        raise ValueError
    checked: list[tuple[str, bool]] = []
    for item in value:
        if type(item) is not tuple or len(item) != 2:
            raise ValueError
        check_id, passed = item
        _require_text(check_id)
        if type(passed) is not bool:
            raise ValueError
        checked.append((check_id, passed))
    if len({item[0] for item in checked}) != len(checked):
        raise ValueError
    return tuple(checked)


def _partition_valid(required: object, passed: object, failed: object) -> bool:
    if not _valid_text_tuple(required, allow_empty=False):
        return False
    if not _valid_text_tuple(passed, allow_empty=True) or not _valid_text_tuple(
        failed, allow_empty=True
    ):
        return False
    if set(passed) & set(failed):
        return False
    return tuple(item for item in required if item in passed) == passed and tuple(
        item for item in required if item in failed
    ) == failed and len(passed) + len(failed) == len(required)


def _replace_category_id(
    result: ConformanceCategoryResultV01,
) -> ConformanceCategoryResultV01:
    return ConformanceCategoryResultV01(
        result_id=_category_id(result),
        category_id=result.category_id,
        required_check_ids=result.required_check_ids,
        passed_check_ids=result.passed_check_ids,
        failed_check_ids=result.failed_check_ids,
        evidence_refs=result.evidence_refs,
        limitation_refs=result.limitation_refs,
        status=result.status,
        real_world_effects_count=result.real_world_effects_count,
    )


def _replace_domain_id(result: DomainConformanceResultV01) -> DomainConformanceResultV01:
    return DomainConformanceResultV01(
        result_id=_domain_id(result),
        domain_id=result.domain_id,
        adapter_ref=result.adapter_ref,
        source_ref=result.source_ref,
        required_check_ids=result.required_check_ids,
        passed_check_ids=result.passed_check_ids,
        failed_check_ids=result.failed_check_ids,
        evidence_refs=result.evidence_refs,
        limitation_refs=result.limitation_refs,
        provider_call_count=result.provider_call_count,
        network_call_count=result.network_call_count,
        gemini_call_count=result.gemini_call_count,
        real_world_effects_count=result.real_world_effects_count,
        status=result.status,
    )


def _replace_negative_id(
    result: NegativeConformanceResultV01,
) -> NegativeConformanceResultV01:
    return NegativeConformanceResultV01(
        result_id=_negative_id(result),
        probe_id=result.probe_id,
        target_contract=result.target_contract,
        expected_reason_codes=result.expected_reason_codes,
        observed_reason_codes=result.observed_reason_codes,
        blocked=result.blocked,
        evidence_refs=result.evidence_refs,
        status=result.status,
        real_world_effects_count=result.real_world_effects_count,
    )


def _replace_report_id(report: KernelConformanceReportV01) -> KernelConformanceReportV01:
    return KernelConformanceReportV01(
        report_id=_report_id(report),
        conformance_version=report.conformance_version,
        implementation_commit=report.implementation_commit,
        category_results=report.category_results,
        domain_results=report.domain_results,
        negative_test_results=report.negative_test_results,
        active_gauntlet_refs=report.active_gauntlet_refs,
        evidence_refs=report.evidence_refs,
        limitations=report.limitations,
        counters=report.counters,
        final_status=report.final_status,
    )


def _category_id(result: ConformanceCategoryResultV01) -> str:
    plain = _category_plain(result)
    plain.pop("result_id")
    return _hash(_CATEGORY_DOMAIN, plain)


def _domain_id(result: DomainConformanceResultV01) -> str:
    plain = _domain_plain(result)
    plain.pop("result_id")
    return _hash(_DOMAIN_DOMAIN, plain)


def _negative_id(result: NegativeConformanceResultV01) -> str:
    plain = _negative_plain(result)
    plain.pop("result_id")
    return _hash(_NEGATIVE_DOMAIN, plain)


def _report_id(report: KernelConformanceReportV01) -> str:
    plain = _report_plain(report)
    plain.pop("report_id")
    return _hash(_REPORT_DOMAIN, plain)


def _hash(domain: str, value: object) -> str:
    return _domain_separated_sha256_hex_v01(
        domain=domain,
        payload=_canonical_json_bytes_v01(value),
    )


def _category_plain(result: ConformanceCategoryResultV01) -> dict[str, object]:
    return {
        "result_id": result.result_id,
        "category_id": result.category_id,
        "required_check_ids": list(result.required_check_ids),
        "passed_check_ids": list(result.passed_check_ids),
        "failed_check_ids": list(result.failed_check_ids),
        "evidence_refs": list(result.evidence_refs),
        "limitation_refs": list(result.limitation_refs),
        "status": result.status,
        "real_world_effects_count": result.real_world_effects_count,
    }


def _domain_plain(result: DomainConformanceResultV01) -> dict[str, object]:
    return {
        "result_id": result.result_id,
        "domain_id": result.domain_id,
        "adapter_ref": result.adapter_ref,
        "source_ref": result.source_ref,
        "required_check_ids": list(result.required_check_ids),
        "passed_check_ids": list(result.passed_check_ids),
        "failed_check_ids": list(result.failed_check_ids),
        "evidence_refs": list(result.evidence_refs),
        "limitation_refs": list(result.limitation_refs),
        "provider_call_count": result.provider_call_count,
        "network_call_count": result.network_call_count,
        "gemini_call_count": result.gemini_call_count,
        "real_world_effects_count": result.real_world_effects_count,
        "status": result.status,
    }


def _negative_plain(result: NegativeConformanceResultV01) -> dict[str, object]:
    return {
        "result_id": result.result_id,
        "probe_id": result.probe_id,
        "target_contract": result.target_contract,
        "expected_reason_codes": list(result.expected_reason_codes),
        "observed_reason_codes": list(result.observed_reason_codes),
        "blocked": result.blocked,
        "evidence_refs": list(result.evidence_refs),
        "status": result.status,
        "real_world_effects_count": result.real_world_effects_count,
    }


def _counters_plain(counters: ConformanceCountersV01) -> dict[str, object]:
    return {
        "category_result_count": counters.category_result_count,
        "category_pass_count": counters.category_pass_count,
        "domain_result_count": counters.domain_result_count,
        "domain_pass_count": counters.domain_pass_count,
        "negative_result_count": counters.negative_result_count,
        "negative_pass_count": counters.negative_pass_count,
        "active_gauntlet_ref_count": counters.active_gauntlet_ref_count,
        "evidence_ref_count": counters.evidence_ref_count,
        "provider_call_count": counters.provider_call_count,
        "network_call_count": counters.network_call_count,
        "gemini_call_count": counters.gemini_call_count,
        "created_authority_count": counters.created_authority_count,
        "created_permission_count": counters.created_permission_count,
        "real_world_effects_count": counters.real_world_effects_count,
    }


def _report_plain(report: KernelConformanceReportV01) -> dict[str, object]:
    return {
        "report_id": report.report_id,
        "conformance_version": report.conformance_version,
        "implementation_commit": report.implementation_commit,
        "category_results": [_category_plain(item) for item in report.category_results],
        "domain_results": [_domain_plain(item) for item in report.domain_results],
        "negative_test_results": [
            _negative_plain(item) for item in report.negative_test_results
        ],
        "active_gauntlet_refs": list(report.active_gauntlet_refs),
        "evidence_refs": list(report.evidence_refs),
        "limitations": list(report.limitations),
        "counters": _counters_plain(report.counters),
        "final_status": report.final_status,
    }


def _counter_values(counters: ConformanceCountersV01) -> tuple[int, ...]:
    return tuple(_counters_plain(counters).values())


def _valid_count(value: object) -> bool:
    return type(value) is int and value >= 0


def _valid_text(value: object) -> bool:
    return type(value) is str and bool(value) and not any(
        0xD800 <= ord(character) <= 0xDFFF for character in value
    )


def _valid_text_tuple(value: object, *, allow_empty: bool) -> bool:
    return (
        type(value) is tuple
        and (allow_empty or bool(value))
        and all(_valid_text(item) for item in value)
        and len(value) == len(set(value))
    )


def _require_text(value: object) -> None:
    if not _valid_text(value):
        raise ValueError


def _require_text_tuple(value: object, *, allow_empty: bool) -> None:
    if not _valid_text_tuple(value, allow_empty=allow_empty):
        raise ValueError


def _require_member(value: object, allowed: tuple[str, ...]) -> None:
    if type(value) is not str or value not in allowed:
        raise ValueError


def _valid_commit(value: object) -> bool:
    return type(value) is str and _COMMIT_PATTERN.fullmatch(value) is not None


def _require_commit(value: object) -> None:
    if not _valid_commit(value):
        raise ValueError


def _dedupe(values: object) -> tuple[str, ...]:
    return tuple(dict.fromkeys(values))
