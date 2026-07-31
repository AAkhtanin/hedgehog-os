from __future__ import annotations

import ast
from dataclasses import FrozenInstanceError, fields, is_dataclass, replace
import hashlib
import inspect
import json
from pathlib import Path

import pytest

import hedgehog.kernel as kernel
from demo import run_kernel_conformance_v01 as runner
from demo import run_living_gauntlet_v01 as living
from hedgehog.kernel import conformance_v01 as conformance


REPOSITORY_ROOT = Path(__file__).resolve().parents[1]
COMPLETION_MANIFEST_PATH = REPOSITORY_ROOT / "release/completion_manifest.json"


GATE1_EXPECTED_CATEGORIES = (
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
G2A_EXPECTED_CATEGORIES = (
    *GATE1_EXPECTED_CATEGORIES,
    "ActionPacketLifecycleConformance",
)
EXPECTED_CATEGORIES = (
    *G2A_EXPECTED_CATEGORIES,
    "DRSSemanticAddressReuseCertificateConformance",
)
EXPECTED_DOMAINS = ("airline", "supplier_water_filter")
GATE1_EXPECTED_PROBES = (
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
G2A_EXPECTED_PROBES = (
    *GATE1_EXPECTED_PROBES,
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
EXPECTED_PROBES = (
    *G2A_EXPECTED_PROBES,
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
GATE1_EXPECTED_ACTIVE_REFS = (
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
G2A_EXPECTED_ACTIVE_REFS = (
    *GATE1_EXPECTED_ACTIVE_REFS,
    "action_packet_lifecycle",
)
EXPECTED_ACTIVE_REFS = (
    *G2A_EXPECTED_ACTIVE_REFS,
    "drs_semantic_address_and_reuse_certificate",
)
DATACLASS_FIELDS = {
    "ConformanceCountersV01": (
        "category_result_count",
        "category_pass_count",
        "domain_result_count",
        "domain_pass_count",
        "negative_result_count",
        "negative_pass_count",
        "active_gauntlet_ref_count",
        "evidence_ref_count",
        "provider_call_count",
        "network_call_count",
        "gemini_call_count",
        "created_authority_count",
        "created_permission_count",
        "real_world_effects_count",
    ),
    "ConformanceCategoryResultV01": (
        "result_id",
        "category_id",
        "required_check_ids",
        "passed_check_ids",
        "failed_check_ids",
        "evidence_refs",
        "limitation_refs",
        "status",
        "real_world_effects_count",
    ),
    "DomainConformanceResultV01": (
        "result_id",
        "domain_id",
        "adapter_ref",
        "source_ref",
        "required_check_ids",
        "passed_check_ids",
        "failed_check_ids",
        "evidence_refs",
        "limitation_refs",
        "provider_call_count",
        "network_call_count",
        "gemini_call_count",
        "real_world_effects_count",
        "status",
    ),
    "NegativeConformanceResultV01": (
        "result_id",
        "probe_id",
        "target_contract",
        "expected_reason_codes",
        "observed_reason_codes",
        "blocked",
        "evidence_refs",
        "status",
        "real_world_effects_count",
    ),
    "KernelConformanceReportV01": (
        "report_id",
        "conformance_version",
        "implementation_commit",
        "category_results",
        "domain_results",
        "negative_test_results",
        "active_gauntlet_refs",
        "evidence_refs",
        "limitations",
        "counters",
        "final_status",
    ),
}
PUBLIC_FUNCTIONS = (
    "build_conformance_category_result_v01",
    "validate_conformance_category_result_v01",
    "build_domain_conformance_result_v01",
    "validate_domain_conformance_result_v01",
    "build_negative_conformance_result_v01",
    "validate_negative_conformance_result_v01",
    "validate_conformance_counters_v01",
    "build_kernel_conformance_report_v01",
    "validate_kernel_conformance_report_v01",
    "conformance_counters_to_plain_dict_v01",
    "conformance_category_result_to_plain_dict_v01",
    "domain_conformance_result_to_plain_dict_v01",
    "negative_conformance_result_to_plain_dict_v01",
    "kernel_conformance_report_to_plain_dict_v01",
)
_PUBLIC_FUNCTION_SIGNATURES = {
    "build_conformance_category_result_v01": (
        "(*, category_id: 'str', check_results: "
        "'tuple[tuple[str, bool], ...]', evidence_refs: 'tuple[str, ...]', "
        "limitation_refs: 'tuple[str, ...]') -> "
        "'ConformanceCategoryResultV01'"
    ),
    "validate_conformance_category_result_v01": (
        "(result: 'object') -> 'tuple[str, ...]'"
    ),
    "build_domain_conformance_result_v01": (
        "(*, domain_id: 'str', adapter_ref: 'str', source_ref: 'str', "
        "check_results: 'tuple[tuple[str, bool], ...]', evidence_refs: "
        "'tuple[str, ...]', limitation_refs: 'tuple[str, ...]', "
        "provider_call_count: 'int', network_call_count: 'int', "
        "gemini_call_count: 'int', real_world_effects_count: 'int') -> "
        "'DomainConformanceResultV01'"
    ),
    "validate_domain_conformance_result_v01": (
        "(result: 'object') -> 'tuple[str, ...]'"
    ),
    "build_negative_conformance_result_v01": (
        "(*, probe_id: 'str', target_contract: 'str', "
        "expected_reason_codes: 'tuple[str, ...]', observed_reason_codes: "
        "'tuple[str, ...]', blocked: 'bool', evidence_refs: "
        "'tuple[str, ...]', real_world_effects_count: 'int') -> "
        "'NegativeConformanceResultV01'"
    ),
    "validate_negative_conformance_result_v01": (
        "(result: 'object') -> 'tuple[str, ...]'"
    ),
    "validate_conformance_counters_v01": (
        "(counters: 'object') -> 'tuple[str, ...]'"
    ),
    "build_kernel_conformance_report_v01": (
        "(*, implementation_commit: 'str', category_results: "
        "'tuple[ConformanceCategoryResultV01, ...]', domain_results: "
        "'tuple[DomainConformanceResultV01, ...]', negative_test_results: "
        "'tuple[NegativeConformanceResultV01, ...]', active_gauntlet_refs: "
        "'tuple[str, ...]', evidence_refs: 'tuple[str, ...]', limitations: "
        "'tuple[str, ...]') -> 'KernelConformanceReportV01'"
    ),
    "validate_kernel_conformance_report_v01": (
        "(report: 'object') -> 'tuple[str, ...]'"
    ),
    "conformance_counters_to_plain_dict_v01": (
        "(counters: 'ConformanceCountersV01') -> 'dict[str, object]'"
    ),
    "conformance_category_result_to_plain_dict_v01": (
        "(result: 'ConformanceCategoryResultV01') -> 'dict[str, object]'"
    ),
    "domain_conformance_result_to_plain_dict_v01": (
        "(result: 'DomainConformanceResultV01') -> 'dict[str, object]'"
    ),
    "negative_conformance_result_to_plain_dict_v01": (
        "(result: 'NegativeConformanceResultV01') -> 'dict[str, object]'"
    ),
    "kernel_conformance_report_to_plain_dict_v01": (
        "(report: 'KernelConformanceReportV01') -> 'dict[str, object]'"
    ),
}
COMMITTED_KERNEL_ALL = (
    "CanonicalArtifactRefV01",
    "ArtifactDependencyEdgeV01",
    "RootOwnershipBindingV01",
    "EvidenceClassBindingV01",
    "AuthorityClassBindingV01",
    "SealProfileV01",
    "ArtifactManifestV01",
    "SealVerificationResultV01",
    "ReplayVerificationResultV01",
    "build_default_seal_profile_v01",
    "canonical_json_bytes_v01",
    "domain_separated_sha256_hex_v01",
    "build_canonical_artifact_ref_v01",
    "build_artifact_manifest_v01",
    "verify_artifact_manifest_v01",
    "verify_artifact_replay_v01",
    "artifact_manifest_to_plain_dict_v01",
    "seal_verification_result_to_plain_dict_v01",
    "replay_verification_result_to_plain_dict_v01",
)


def _category(category_id: str, passed: bool = True):
    required = next(
        check_ids
        for expected_id, check_ids in conformance._EXPECTED_CATEGORY_CHECK_IDS
        if expected_id == category_id
    )
    return conformance.build_conformance_category_result_v01(
        category_id=category_id,
        check_results=tuple((check_id, passed) for check_id in required),
        evidence_refs=(
            (
                "runtime:kernel_conformance:"
                "ActionPacketLifecycleConformance",
            )
            if category_id == "ActionPacketLifecycleConformance"
            else (
                (
                    "runtime:kernel_conformance:"
                    "DRSSemanticAddressReuseCertificateConformance",
                )
                if category_id
                == "DRSSemanticAddressReuseCertificateConformance"
                else (f"evidence:{category_id}",)
            )
        ),
        limitation_refs=(
            (
                "limitation_g2a6_deterministic_local_actionpacket_lifecycle_only",
            )
            if category_id == "ActionPacketLifecycleConformance"
            else (
                (
                    "limitation_g2b6_deterministic_local_drs_"
                    "semantic_reuse_only",
                )
                if category_id
                == "DRSSemanticAddressReuseCertificateConformance"
                else (f"limitation:{category_id}",)
            )
        ),
    )


def _domain(domain_id: str, passed: bool = True, **counts: int):
    expected = next(
        item
        for item in conformance._EXPECTED_DOMAIN_GEOMETRY
        if item[0] == domain_id
    )
    _, adapter_ref, source_ref, required, evidence_refs, limitation_refs = expected
    return conformance.build_domain_conformance_result_v01(
        domain_id=domain_id,
        adapter_ref=adapter_ref,
        source_ref=source_ref,
        check_results=tuple((check_id, passed) for check_id in required),
        evidence_refs=evidence_refs,
        limitation_refs=limitation_refs,
        provider_call_count=counts.get("provider_call_count", 0),
        network_call_count=counts.get("network_call_count", 0),
        gemini_call_count=counts.get("gemini_call_count", 0),
        real_world_effects_count=counts.get("real_world_effects_count", 0),
    )


def _negative(probe_id: str, *, blocked: bool = True, observed: bool = True):
    _, target_contract, expected_reasons = next(
        item
        for item in conformance._EXPECTED_NEGATIVE_GEOMETRY
        if item[0] == probe_id
    )
    return conformance.build_negative_conformance_result_v01(
        probe_id=probe_id,
        target_contract=target_contract,
        expected_reason_codes=expected_reasons,
        observed_reason_codes=expected_reasons if observed else (),
        blocked=blocked,
        evidence_refs=(
            ("demo/run_drs_semantic_address_reuse_certificate_g2_b_v01.py",)
            if probe_id in EXPECTED_PROBES[len(G2A_EXPECTED_PROBES) :]
            else (
                ("demo/run_action_commit_packet_lifecycle_g2_a_v01.py",)
                if probe_id not in GATE1_EXPECTED_PROBES
                else (f"evidence:{probe_id}",)
            )
        ),
        real_world_effects_count=0,
    )


def _report(*, commit: str = "abcdef0", categories=None, domains=None, negatives=None):
    return conformance.build_kernel_conformance_report_v01(
        implementation_commit=commit,
        category_results=(
            tuple(_category(item) for item in EXPECTED_CATEGORIES)
            if categories is None
            else categories
        ),
        domain_results=(
            tuple(_domain(item) for item in EXPECTED_DOMAINS)
            if domains is None
            else domains
        ),
        negative_test_results=(
            tuple(_negative(item) for item in EXPECTED_PROBES)
            if negatives is None
            else negatives
        ),
        active_gauntlet_refs=EXPECTED_ACTIVE_REFS,
        evidence_refs=("evidence:kernel:conformance",),
        limitations=("limitation:kernel:conformance",),
    )


def _historical_v01_report():
    categories = tuple(_category(item) for item in GATE1_EXPECTED_CATEGORIES)
    domains = tuple(_domain(item) for item in EXPECTED_DOMAINS)
    negatives = tuple(_negative(item) for item in GATE1_EXPECTED_PROBES)
    evidence_refs = ("evidence:kernel:conformance:v0.1",)
    provisional = conformance.KernelConformanceReportV01(
        report_id="0" * 64,
        conformance_version="v0.1",
        implementation_commit="abcdef0",
        category_results=categories,
        domain_results=domains,
        negative_test_results=negatives,
        active_gauntlet_refs=GATE1_EXPECTED_ACTIVE_REFS,
        evidence_refs=evidence_refs,
        limitations=("limitation:kernel:conformance:v0.1",),
        counters=conformance._derive_counters(
            categories,
            domains,
            negatives,
            GATE1_EXPECTED_ACTIVE_REFS,
            evidence_refs,
        ),
        final_status=conformance.STATUS_PASS,
    )
    return conformance._replace_report_id(provisional)


def _contains_type(value, target_type) -> bool:
    if isinstance(value, target_type):
        return True
    if isinstance(value, dict):
        return any(_contains_type(item, target_type) for item in value.values())
    if isinstance(value, (list, tuple)):
        return any(_contains_type(item, target_type) for item in value)
    return False


@pytest.fixture(scope="module")
def standalone_report():
    return runner.collect_standalone_kernel_conformance_v01(
        implementation_commit="abcdef0"
    )


@pytest.mark.parametrize("name,expected", DATACLASS_FIELDS.items())
def test_public_dataclass_field_order_is_exact(name, expected):
    cls = getattr(conformance, name)
    assert is_dataclass(cls)
    assert tuple(item.name for item in fields(cls)) == expected


@pytest.mark.parametrize("name", DATACLASS_FIELDS)
def test_public_dataclasses_are_frozen_and_slotted(name):
    cls = getattr(conformance, name)
    assert cls.__dataclass_params__.frozen is True
    assert "__slots__" in vars(cls)


@pytest.mark.parametrize("name", (*DATACLASS_FIELDS, *PUBLIC_FUNCTIONS))
def test_package_exposes_conformance_surface(name):
    assert getattr(kernel, name) is getattr(conformance, name)


def test_public_function_surface_is_exact():
    actual = tuple(
        name
        for name, value in vars(conformance).items()
        if not name.startswith("_") and inspect.isfunction(value)
    )
    assert actual == PUBLIC_FUNCTIONS


def test_package_all_is_byte_compatible_in_content_and_order():
    assert kernel.__all__ == COMMITTED_KERNEL_ALL


def test_future_annotations_binding_is_absent():
    assert "annotations" not in vars(conformance)


@pytest.mark.parametrize(
    "name,expected",
    (
        ("MODULE_ID", "kernel_conformance_v01"),
        ("SLICE_ID", "domain_neutral_reference_kernel_gate1_g1e"),
        ("CONFORMANCE_VERSION", "v0.2"),
        ("STATUS_PASS", "PASS"),
        ("STATUS_FAIL_CLOSED", "FAIL_CLOSED"),
        ("CONFORMANCE_STATUSES", ("PASS", "FAIL_CLOSED")),
        ("CATEGORY_IDS", EXPECTED_CATEGORIES),
        ("DOMAIN_IDS", EXPECTED_DOMAINS),
        ("NEGATIVE_PROBE_IDS", EXPECTED_PROBES),
    ),
)
def test_constants_are_exact(name, expected):
    assert getattr(conformance, name) == expected
    if isinstance(expected, tuple):
        assert type(getattr(conformance, name)) is tuple


@pytest.mark.parametrize("category_id", EXPECTED_CATEGORIES)
def test_each_category_derives_pass(category_id):
    result = _category(category_id)
    assert result.status == "PASS"
    assert result.failed_check_ids == ()
    assert conformance.validate_conformance_category_result_v01(result) == ()


def test_category_false_check_derives_fail_closed():
    result = _category(EXPECTED_CATEGORIES[0], False)
    assert result.status == "FAIL_CLOSED"
    assert result.passed_check_ids == ()
    assert result.failed_check_ids == result.required_check_ids
    assert conformance.validate_conformance_category_result_v01(result) == ()


@pytest.mark.parametrize(
    "check_results",
    ((), (("same", True), ("same", False)), [("check", True)], (("check", 1),)),
)
def test_category_rejects_invalid_check_geometry(check_results):
    with pytest.raises(ValueError, match="^conformance_category_invalid$"):
        conformance.build_conformance_category_result_v01(
            category_id=EXPECTED_CATEGORIES[0],
            check_results=check_results,
            evidence_refs=("evidence",),
            limitation_refs=("limitation",),
        )


def test_category_identity_is_deterministic_and_field_sensitive():
    first = _category(EXPECTED_CATEGORIES[0])
    second = _category(EXPECTED_CATEGORIES[0])
    changed = conformance.build_conformance_category_result_v01(
        category_id=EXPECTED_CATEGORIES[0],
        check_results=(("different", True),),
        evidence_refs=("evidence:changed",),
        limitation_refs=("limitation:changed",),
    )
    assert first == second
    assert first.result_id == second.result_id
    assert changed.result_id != first.result_id


@pytest.mark.parametrize("domain_id", EXPECTED_DOMAINS)
def test_each_domain_derives_pass(domain_id):
    result = _domain(domain_id)
    assert result.status == "PASS"
    assert conformance.validate_domain_conformance_result_v01(result) == ()


def test_supplier_mixed_visibility_is_a_successful_explicit_check():
    result = conformance.build_domain_conformance_result_v01(
        domain_id="supplier_water_filter",
        adapter_ref="adapter:supplier",
        source_ref="source:supplier",
        check_results=(("supplier_multiroot_mixed_visible", True),),
        evidence_refs=("evidence:supplier",),
        limitation_refs=("limitation:supplier",),
        provider_call_count=0,
        network_call_count=0,
        gemini_call_count=0,
        real_world_effects_count=0,
    )
    assert result.status == "PASS"
    assert result.passed_check_ids == ("supplier_multiroot_mixed_visible",)


@pytest.mark.parametrize(
    "field",
    (
        "provider_call_count",
        "network_call_count",
        "gemini_call_count",
        "real_world_effects_count",
    ),
)
def test_nonzero_domain_boundary_derives_fail_closed(field):
    result = _domain(EXPECTED_DOMAINS[0], **{field: 1})
    assert result.status == "FAIL_CLOSED"
    assert conformance.validate_domain_conformance_result_v01(result) == ()


@pytest.mark.parametrize("field", ("adapter_ref", "source_ref"))
def test_domain_rejects_empty_binding(field):
    kwargs = {"adapter_ref": "adapter", "source_ref": "source"}
    kwargs[field] = ""
    with pytest.raises(ValueError, match="^domain_conformance_invalid$"):
        conformance.build_domain_conformance_result_v01(
            domain_id="airline",
            check_results=(("check", True),),
            evidence_refs=("evidence",),
            limitation_refs=("limitation",),
            provider_call_count=0,
            network_call_count=0,
            gemini_call_count=0,
            real_world_effects_count=0,
            **kwargs,
        )


@pytest.mark.parametrize("probe_id", EXPECTED_PROBES)
def test_each_negative_probe_contract_derives_pass(probe_id):
    result = _negative(probe_id)
    assert result.status == "PASS"
    assert conformance.validate_negative_conformance_result_v01(result) == ()


@pytest.mark.parametrize("blocked,observed", ((False, True), (True, False), (False, False)))
def test_negative_probe_failure_derives_fail_closed(blocked, observed):
    result = _negative(EXPECTED_PROBES[0], blocked=blocked, observed=observed)
    assert result.status == "FAIL_CLOSED"
    assert conformance.validate_negative_conformance_result_v01(result) == ()


def test_negative_probe_rejects_duplicate_reasons():
    with pytest.raises(ValueError, match="^negative_conformance_invalid$"):
        conformance.build_negative_conformance_result_v01(
            probe_id=EXPECTED_PROBES[0],
            target_contract="contract",
            expected_reason_codes=("reason", "reason"),
            observed_reason_codes=("reason",),
            blocked=True,
            evidence_refs=("evidence",),
            real_world_effects_count=0,
        )


def test_negative_empty_evidence_is_rejected_after_rehash():
    valid = _negative(EXPECTED_PROBES[0])
    forged = conformance._replace_negative_id(
        replace(valid, evidence_refs=())
    )
    assert conformance.validate_negative_conformance_result_v01(forged) == (
        "negative_conformance_invalid",
    )


def test_negative_empty_evidence_projection_is_rejected():
    valid = _negative(EXPECTED_PROBES[0])
    forged = conformance._replace_negative_id(
        replace(valid, evidence_refs=())
    )
    with pytest.raises(ValueError, match="^negative_conformance_invalid$"):
        conformance.negative_conformance_result_to_plain_dict_v01(forged)


def test_report_pass_geometry_and_counters_are_derived():
    report = _report()
    assert report.final_status == "PASS"
    assert conformance.validate_kernel_conformance_report_v01(report) == ()
    assert (
        len(report.category_results),
        len(report.domain_results),
        len(report.negative_test_results),
    ) == (11, 2, 20)
    assert report.counters.category_pass_count == 11
    assert report.counters.domain_pass_count == 2
    assert report.counters.negative_pass_count == 20
    assert report.counters.active_gauntlet_ref_count == 13


def test_final_report_rejects_arbitrary_synthetic_check_geometry_after_rehash():
    report = _report()
    categories = tuple(
        conformance.build_conformance_category_result_v01(
            category_id=category_id,
            check_results=((f"synthetic:{category_id}", True),),
            evidence_refs=(f"evidence:{category_id}",),
            limitation_refs=(f"limitation:{category_id}",),
        )
        for category_id in EXPECTED_CATEGORIES
    )
    domains = tuple(
        conformance.build_domain_conformance_result_v01(
            domain_id=domain_id,
            adapter_ref=f"synthetic:adapter:{domain_id}",
            source_ref=f"synthetic:source:{domain_id}",
            check_results=((f"synthetic:{domain_id}", True),),
            evidence_refs=(f"evidence:{domain_id}",),
            limitation_refs=(f"limitation:{domain_id}",),
            provider_call_count=0,
            network_call_count=0,
            gemini_call_count=0,
            real_world_effects_count=0,
        )
        for domain_id in EXPECTED_DOMAINS
    )
    forged = conformance._replace_report_id(
        replace(report, category_results=categories, domain_results=domains)
    )
    assert "conformance_report_geometry_invalid" in (
        conformance.validate_kernel_conformance_report_v01(forged)
    )


def test_final_report_rejects_wrong_category_check_tuple_after_rehash():
    report = _report()
    wrong = conformance.build_conformance_category_result_v01(
        category_id=EXPECTED_CATEGORIES[0],
        check_results=(("synthetic", True),),
        evidence_refs=report.category_results[0].evidence_refs,
        limitation_refs=report.category_results[0].limitation_refs,
    )
    forged = conformance._replace_report_id(
        replace(
            report,
            category_results=(wrong, *report.category_results[1:]),
        )
    )
    assert "conformance_report_geometry_invalid" in (
        conformance.validate_kernel_conformance_report_v01(forged)
    )


def test_final_report_rejects_wrong_domain_adapter_after_rehash():
    report = _report()
    wrong = conformance._replace_domain_id(
        replace(report.domain_results[0], adapter_ref="adapter:wrong")
    )
    forged = conformance._replace_report_id(
        replace(report, domain_results=(wrong, report.domain_results[1]))
    )
    assert "conformance_report_geometry_invalid" in (
        conformance.validate_kernel_conformance_report_v01(forged)
    )


def test_final_report_rejects_wrong_domain_checks_after_rehash():
    report = _report()
    wrong = conformance._replace_domain_id(
        replace(
            report.domain_results[0],
            required_check_ids=("synthetic",),
            passed_check_ids=("synthetic",),
        )
    )
    forged = conformance._replace_report_id(
        replace(report, domain_results=(wrong, report.domain_results[1]))
    )
    assert "conformance_report_geometry_invalid" in (
        conformance.validate_kernel_conformance_report_v01(forged)
    )


@pytest.mark.parametrize("field", ("target_contract", "expected_reason_codes"))
def test_final_report_rejects_wrong_negative_geometry_after_rehash(field):
    report = _report()
    value = "contract:wrong" if field == "target_contract" else ("reason:wrong",)
    wrong = conformance._replace_negative_id(
        replace(report.negative_test_results[0], **{field: value})
    )
    forged = conformance._replace_report_id(
        replace(
            report,
            negative_test_results=(wrong, *report.negative_test_results[1:]),
        )
    )
    assert "conformance_report_geometry_invalid" in (
        conformance.validate_kernel_conformance_report_v01(forged)
    )


@pytest.mark.parametrize("commit", ("abc1234", "0" * 40))
def test_valid_implementation_commit_is_preserved(commit):
    assert _report(commit=commit).implementation_commit == commit


@pytest.mark.parametrize("commit", ("", "ABC1234", "abc123", "g" * 7, "0" * 41))
def test_invalid_implementation_commit_is_rejected(commit):
    with pytest.raises(ValueError, match="^kernel_conformance_report_invalid$"):
        _report(commit=commit)


def test_changed_commit_changes_report_identity():
    assert _report(commit="abcdef0").report_id != _report(commit="abcdef1").report_id


@pytest.mark.parametrize("kind", ("category", "domain", "negative"))
def test_nested_failure_derives_report_fail_closed(kind):
    categories = tuple(_category(item) for item in EXPECTED_CATEGORIES)
    domains = tuple(_domain(item) for item in EXPECTED_DOMAINS)
    negatives = tuple(_negative(item) for item in EXPECTED_PROBES)
    if kind == "category":
        categories = (_category(EXPECTED_CATEGORIES[0], False), *categories[1:])
    elif kind == "domain":
        domains = (_domain(EXPECTED_DOMAINS[0], False), domains[1])
    else:
        negatives = (_negative(EXPECTED_PROBES[0], blocked=False), *negatives[1:])
    report = _report(categories=categories, domains=domains, negatives=negatives)
    assert report.final_status == "FAIL_CLOSED"
    assert conformance.validate_kernel_conformance_report_v01(report) == ()


@pytest.mark.parametrize("kind", ("category", "domain", "negative", "active"))
def test_report_rejects_reordered_or_missing_geometry(kind):
    report = _report()
    if kind == "category":
        forged = replace(report, category_results=tuple(reversed(report.category_results)))
    elif kind == "domain":
        forged = replace(report, domain_results=tuple(reversed(report.domain_results)))
    elif kind == "negative":
        forged = replace(report, negative_test_results=tuple(reversed(report.negative_test_results)))
    else:
        forged = replace(report, active_gauntlet_refs=report.active_gauntlet_refs[:-1])
    forged = conformance._replace_report_id(forged)
    assert conformance.validate_kernel_conformance_report_v01(forged)


@pytest.mark.parametrize(
    "field,value",
    (
        ("category_result_count", 9),
        ("category_pass_count", 9),
        ("domain_result_count", 1),
        ("domain_pass_count", 1),
        ("negative_result_count", 9),
        ("negative_pass_count", 9),
        ("active_gauntlet_ref_count", 11),
        ("evidence_ref_count", 2),
        ("provider_call_count", 1),
        ("network_call_count", 1),
        ("gemini_call_count", 1),
        ("created_authority_count", 1),
        ("created_permission_count", 1),
        ("real_world_effects_count", 1),
    ),
)
def test_report_rejects_every_counter_lie_after_rehash(field, value):
    report = _report()
    counters = replace(report.counters, **{field: value})
    forged = conformance._replace_report_id(replace(report, counters=counters))
    assert conformance.validate_kernel_conformance_report_v01(forged)


def test_category_forged_pass_with_visible_failure_is_rejected_after_rehash():
    failed = _category(EXPECTED_CATEGORIES[0], False)
    forged = conformance._replace_category_id(replace(failed, status="PASS"))
    assert "conformance_status_mismatch" in conformance.validate_conformance_category_result_v01(forged)


def test_category_hidden_failure_breaks_partition_after_rehash():
    failed = _category(EXPECTED_CATEGORIES[0], False)
    forged = conformance._replace_category_id(replace(failed, failed_check_ids=()))
    assert "conformance_check_partition_invalid" in conformance.validate_conformance_category_result_v01(forged)


def test_category_failed_check_cannot_also_be_passed_after_rehash():
    failed = _category(EXPECTED_CATEGORIES[0], False)
    forged = conformance._replace_category_id(replace(failed, passed_check_ids=failed.required_check_ids))
    assert "conformance_check_partition_invalid" in conformance.validate_conformance_category_result_v01(forged)


def test_domain_forged_pass_is_rejected_after_rehash():
    failed = _domain("airline", provider_call_count=1)
    forged = conformance._replace_domain_id(replace(failed, status="PASS"))
    assert conformance.validate_domain_conformance_result_v01(forged)


def test_negative_forged_pass_is_rejected_after_rehash():
    failed = _negative(EXPECTED_PROBES[0], blocked=False)
    forged = conformance._replace_negative_id(replace(failed, status="PASS"))
    assert conformance.validate_negative_conformance_result_v01(forged)


def test_report_forged_pass_is_rejected_after_rehash():
    categories = (_category(EXPECTED_CATEGORIES[0], False),) + tuple(
        _category(item) for item in EXPECTED_CATEGORIES[1:]
    )
    failed = _report(categories=categories)
    forged = conformance._replace_report_id(replace(failed, final_status="PASS"))
    assert conformance.validate_kernel_conformance_report_v01(forged)


@pytest.mark.parametrize("probe_id", EXPECTED_PROBES)
def test_standalone_executes_each_exact_negative_probe(standalone_report, probe_id):
    by_id = {item.probe_id: item for item in standalone_report.negative_test_results}
    assert by_id[probe_id].status == "PASS"
    assert by_id[probe_id].blocked is True


def test_supplier_negative_uses_executed_source_act_provenance(standalone_report):
    result = next(
        item
        for item in standalone_report.negative_test_results
        if item.probe_id == "supplier_adapter_effect_counter_rejected"
    )
    assert result.probe_id == "supplier_adapter_effect_counter_rejected"
    assert result.target_contract == (
        "demo.run_living_gauntlet_v01:"
        "collect_supplier_water_filter_portability_gauntlet_act_v01"
    )
    assert result.expected_reason_codes == (
        "supplier_water_filter_effect_creation_forbidden",
    )
    assert result.observed_reason_codes == (
        "supplier_water_filter_effect_creation_forbidden",
    )
    assert result.evidence_refs == ("demo/run_living_gauntlet_v01.py",)
    assert result.status == conformance.STATUS_PASS


@pytest.mark.parametrize("category_id", EXPECTED_CATEGORIES)
def test_standalone_executes_each_exact_category(standalone_report, category_id):
    by_id = {item.category_id: item for item in standalone_report.category_results}
    assert by_id[category_id].status == "PASS"
    assert by_id[category_id].failed_check_ids == ()


@pytest.mark.parametrize("domain_id", EXPECTED_DOMAINS)
def test_standalone_executes_each_exact_domain(standalone_report, domain_id):
    by_id = {item.domain_id: item for item in standalone_report.domain_results}
    assert by_id[domain_id].status == "PASS"
    assert by_id[domain_id].provider_call_count == 0
    assert by_id[domain_id].network_call_count == 0
    assert by_id[domain_id].gemini_call_count == 0
    assert by_id[domain_id].real_world_effects_count == 0


def test_supplier_multiroot_mixed_remains_visible(standalone_report):
    supplier = standalone_report.domain_results[1]
    assert "supplier_multiroot_mixed_visible" in supplier.passed_check_ids
    assert not any("supplier_multiroot_pass" in item for item in supplier.required_check_ids)


def test_standalone_report_runtime_validation_passes(standalone_report):
    assert runner.validate_kernel_conformance_runtime_v01(standalone_report) == ()
    assert standalone_report.final_status == "PASS"


def test_canonical_report_validates_and_projects(standalone_report):
    assert conformance.validate_kernel_conformance_report_v01(standalone_report) == ()
    projection = conformance.kernel_conformance_report_to_plain_dict_v01(
        standalone_report
    )
    assert projection["final_status"] == conformance.STATUS_PASS
    assert len(projection["category_results"]) == 11
    assert len(projection["domain_results"]) == 2
    assert len(projection["negative_test_results"]) == 20


@pytest.mark.parametrize("index", range(11))
def test_canonical_category_check_geometry_is_exact(standalone_report, index):
    category_id, required = conformance._EXPECTED_CATEGORY_CHECK_IDS[index]
    result = standalone_report.category_results[index]
    assert result.category_id == category_id
    assert result.required_check_ids == required


@pytest.mark.parametrize("index", range(2))
def test_canonical_domain_binding_geometry_is_exact(standalone_report, index):
    expected = conformance._EXPECTED_DOMAIN_GEOMETRY[index]
    result = standalone_report.domain_results[index]
    assert (
        result.domain_id,
        result.adapter_ref,
        result.source_ref,
        result.required_check_ids,
        result.evidence_refs,
        result.limitation_refs,
    ) == expected


@pytest.mark.parametrize("index", range(20))
def test_canonical_negative_geometry_is_exact(standalone_report, index):
    probe_id, target, expected_reasons = conformance._EXPECTED_NEGATIVE_GEOMETRY[
        index
    ]
    result = standalone_report.negative_test_results[index]
    assert result.probe_id == probe_id
    assert result.target_contract == target
    assert result.expected_reason_codes == expected_reasons
    assert result.evidence_refs


def test_completion_claim_uses_honest_negative_check_wording():
    manifest = json.loads(COMPLETION_MANIFEST_PATH.read_text(encoding="utf-8"))
    claim = next(
        item
        for item in manifest["public_claims"]
        if item["claim_id"] == "claim_kernel_conformance_closure_execution"
    )
    assert "ten executed negative conformance checks" in claim["statement"]
    assert "direct negative probes" not in claim["statement"]


def test_standalone_zero_boundaries_are_exact(standalone_report):
    counters = standalone_report.counters
    assert (
        counters.provider_call_count,
        counters.network_call_count,
        counters.gemini_call_count,
        counters.created_authority_count,
        counters.created_permission_count,
        counters.real_world_effects_count,
    ) == (0, 0, 0, 0, 0, 0)


def test_report_projection_is_json_safe_and_independent(standalone_report):
    first = conformance.kernel_conformance_report_to_plain_dict_v01(standalone_report)
    second = conformance.kernel_conformance_report_to_plain_dict_v01(standalone_report)
    assert first == second
    assert not _contains_type(first, tuple)
    assert not _contains_type(first, bytes)
    assert not _contains_type(first, type(standalone_report))
    json.dumps(first, sort_keys=True, separators=(",", ":"), allow_nan=False)
    first["active_gauntlet_refs"].append("forged")
    assert second["active_gauntlet_refs"] == list(EXPECTED_ACTIVE_REFS)


def test_two_pure_reports_and_projection_hashes_are_deterministic():
    first = _report()
    second = _report()
    first_plain = conformance.kernel_conformance_report_to_plain_dict_v01(first)
    second_plain = conformance.kernel_conformance_report_to_plain_dict_v01(second)
    first_bytes = json.dumps(first_plain, sort_keys=True, separators=(",", ":")).encode()
    second_bytes = json.dumps(second_plain, sort_keys=True, separators=(",", ":")).encode()
    assert first == second
    assert first.report_id == second.report_id
    assert first_bytes == second_bytes
    assert hashlib.sha256(first_bytes).hexdigest() == hashlib.sha256(second_bytes).hexdigest()


@pytest.mark.parametrize(
    "projection_name,value_factory",
    (
        ("conformance_category_result_to_plain_dict_v01", lambda: _category(EXPECTED_CATEGORIES[0])),
        ("domain_conformance_result_to_plain_dict_v01", lambda: _domain(EXPECTED_DOMAINS[0])),
        ("negative_conformance_result_to_plain_dict_v01", lambda: _negative(EXPECTED_PROBES[0])),
        ("kernel_conformance_report_to_plain_dict_v01", _report),
    ),
)
def test_public_projections_reject_wrong_exact_type(projection_name, value_factory):
    projection = getattr(conformance, projection_name)
    with pytest.raises(ValueError):
        projection(object())
    assert value_factory() is not None


def test_frozen_contract_rejects_assignment():
    result = _category(EXPECTED_CATEGORIES[0])
    with pytest.raises(FrozenInstanceError):
        result.status = "FAIL_CLOSED"


@pytest.mark.parametrize(
    "forbidden",
    (
        "subprocess",
        "pathlib",
        "import os",
        ".tmp",
        "requests",
        "socket",
        "cryptography",
    ),
)
def test_kernel_contract_static_boundary(forbidden):
    source = inspect.getsource(conformance).lower()
    assert forbidden.lower() not in source


def test_kernel_contract_imports_only_approved_kernel_helpers():
    tree = ast.parse(inspect.getsource(conformance))
    imports = {
        node.module
        for node in ast.walk(tree)
        if isinstance(node, ast.ImportFrom) and node.module is not None
    }
    assert imports == {"__future__", "dataclasses", "hedgehog.kernel.integrity_replay_v01"}


def test_runner_living_import_is_function_local():
    tree = ast.parse(inspect.getsource(runner))
    module_imports = [
        node
        for node in tree.body
        if isinstance(node, (ast.Import, ast.ImportFrom))
    ]
    assert not any(
        isinstance(node, ast.ImportFrom) and node.module == "demo" for node in module_imports
    )
    standalone = next(
        node
        for node in tree.body
        if isinstance(node, ast.FunctionDef)
        and node.name == "collect_standalone_kernel_conformance_v01"
    )
    assert any(
        isinstance(node, ast.ImportFrom)
        and node.module == "demo"
        and any(alias.name == "run_living_gauntlet_v01" for alias in node.names)
        for node in ast.walk(standalone)
    )


@pytest.mark.parametrize(
    "forbidden",
    (
        "socket",
        "create_audit",
        "write_audit",
        "presentation",
        "production certification.",
    ),
)
def test_runner_static_boundary(forbidden):
    source = inspect.getsource(runner).lower()
    if forbidden == "production certification.":
        assert "not production certification" in source
    else:
        assert forbidden not in source


def test_runner_imports_no_network_client_modules():
    tree = ast.parse(inspect.getsource(runner))
    imported = {
        node.module
        for node in ast.walk(tree)
        if isinstance(node, ast.ImportFrom) and node.module is not None
    }
    imported.update(
        alias.name
        for node in ast.walk(tree)
        if isinstance(node, ast.Import)
        for alias in node.names
    )
    assert not imported.intersection({"requests", "socket", "urllib"})


def test_runner_does_not_call_supplier_source_collector():
    source = inspect.getsource(runner.collect_kernel_conformance_v01)
    assert "collect_full_wow_v1_2_product_trace" not in source
    assert "collect_supplier_water_filter_portability_gauntlet_act_v01" not in source


def test_render_contains_only_summary_geometry(standalone_report):
    rendered = runner.render_kernel_conformance_v01(standalone_report)
    assert "kernel_conformance_v01 v0.2" in rendered
    assert "final_status=PASS" in rendered
    for forbidden in ("manifest_hash=", "adapter_id=", "artifact_id=", "invoice", "shipment_sh"):
        assert forbidden not in rendered.lower()


def test_g2a6_conformance_v02_preserves_v01_geometry_and_adds_lifecycle_category(
    standalone_report,
):
    historical = _historical_v01_report()
    historical_v02 = _historical_v02_report(standalone_report)
    assert conformance.validate_kernel_conformance_report_v01(historical) == ()
    assert conformance.validate_kernel_conformance_report_v01(
        historical_v02
    ) == ()
    assert (
        len(historical.category_results),
        len(historical.domain_results),
        len(historical.negative_test_results),
        len(historical.active_gauntlet_refs),
    ) == (10, 2, 10, 12)
    assert (
        historical_v02.conformance_version,
        len(historical_v02.category_results),
        len(historical_v02.domain_results),
        len(historical_v02.negative_test_results),
        len(historical_v02.active_gauntlet_refs),
    ) == ("v0.2", 11, 2, 20, 13)
    unknown = conformance._replace_report_id(
        replace(standalone_report, conformance_version="v0.4")
    )
    mixed_v01 = conformance._replace_report_id(
        replace(historical_v02, conformance_version="v0.1")
    )
    mixed_v02 = conformance._replace_report_id(
        replace(historical, conformance_version="v0.2")
    )
    assert conformance.validate_kernel_conformance_report_v01(unknown)
    assert "conformance_report_geometry_invalid" in (
        conformance.validate_kernel_conformance_report_v01(mixed_v01)
    )
    assert "conformance_report_geometry_invalid" in (
        conformance.validate_kernel_conformance_report_v01(mixed_v02)
    )
    assert conformance.CATEGORY_IDS[:10] == GATE1_EXPECTED_CATEGORIES
    assert conformance.NEGATIVE_PROBE_IDS[:10] == GATE1_EXPECTED_PROBES
    assert conformance._ACTIVE_GAUNTLET_REFS[:12] == GATE1_EXPECTED_ACTIVE_REFS
    assert tuple(
        (item.category_id, item.required_check_ids)
        for item in standalone_report.category_results[:10]
    ) == conformance._GATE1_EXPECTED_CATEGORY_CHECK_IDS_V01
    assert tuple(
        (
            item.probe_id,
            item.target_contract,
            item.expected_reason_codes,
        )
        for item in standalone_report.negative_test_results[:10]
    ) == conformance._GATE1_EXPECTED_NEGATIVE_GEOMETRY_V01
    assert standalone_report.category_results[10].category_id == (
        "ActionPacketLifecycleConformance"
    )
    assert standalone_report.category_results[:11] == (
        historical_v02.category_results
    )
    assert standalone_report.negative_test_results[:20] == (
        historical_v02.negative_test_results
    )
    assert standalone_report.active_gauntlet_refs[:13] == (
        historical_v02.active_gauntlet_refs
    )
    assert tuple(item.name for item in fields(conformance.KernelConformanceReportV01)) == (
        DATACLASS_FIELDS["KernelConformanceReportV01"]
    )
    assert {
        name: str(inspect.signature(getattr(conformance, name)))
        for name in PUBLIC_FUNCTIONS
    } == _PUBLIC_FUNCTION_SIGNATURES


def test_g2a6_action_packet_lifecycle_category_matches_exact_checks(
    standalone_report,
):
    category = standalone_report.category_results[10]
    expected_checks = (
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
    )
    assert category.category_id == "ActionPacketLifecycleConformance"
    assert category.required_check_ids == expected_checks
    assert category.passed_check_ids == expected_checks
    assert category.failed_check_ids == ()
    assert category.evidence_refs == (
        "runtime:kernel_conformance:ActionPacketLifecycleConformance",
    )
    assert category.limitation_refs == (
        "limitation_g2a6_deterministic_local_actionpacket_lifecycle_only",
    )
    assert category.status == conformance.STATUS_PASS
    assert category.result_id == conformance._category_id(category)

    failed = conformance.build_conformance_category_result_v01(
        category_id=category.category_id,
        check_results=tuple(
            (check_id, index != 0)
            for index, check_id in enumerate(expected_checks)
        ),
        evidence_refs=category.evidence_refs,
        limitation_refs=category.limitation_refs,
    )
    assert failed.status == conformance.STATUS_FAIL_CLOSED
    forged_rows = (
        replace(category, required_check_ids=expected_checks[:-1]),
        replace(
            category,
            required_check_ids=tuple(reversed(expected_checks)),
            passed_check_ids=tuple(reversed(expected_checks)),
        ),
        replace(
            category,
            required_check_ids=(expected_checks[0], *expected_checks),
            passed_check_ids=(expected_checks[0], *expected_checks),
        ),
        replace(failed, status=conformance.STATUS_PASS),
    )
    for forged in forged_rows:
        forged = conformance._replace_category_id(forged)
        forged_report = conformance._replace_report_id(
            replace(
                standalone_report,
                category_results=(
                    *standalone_report.category_results[:10],
                    forged,
                    *standalone_report.category_results[11:],
                ),
            )
        )
        assert conformance.validate_kernel_conformance_report_v01(forged_report)
    source = inspect.getsource(runner._build_category_results)
    assert "action_packet_lifecycle" in source
    for probe_id in conformance._G2A_NEGATIVE_PROBE_IDS_V02[10:]:
        assert probe_id in source
    assert standalone_report.counters.created_authority_count == 0
    assert standalone_report.counters.created_permission_count == 0
    assert standalone_report.counters.real_world_effects_count == 0


def test_g2a6_action_packet_lifecycle_negative_probe_matrix_is_exact(
    monkeypatch: pytest.MonkeyPatch,
):
    collection_count = 0
    original_collect = (
        runner._action_packet_lifecycle.collect_action_commit_packet_lifecycle_g2_a_v01
    )
    original_validate = (
        runner._action_packet_lifecycle.validate_action_commit_packet_lifecycle_g2_a_report_v01
    )
    validations = []

    def collect_once():
        nonlocal collection_count
        collection_count += 1
        return original_collect()

    def validate_wrapper(report):
        result = original_validate(report)
        validations.append(result)
        return result

    monkeypatch.setattr(
        runner._action_packet_lifecycle,
        "collect_action_commit_packet_lifecycle_g2_a_v01",
        collect_once,
    )
    monkeypatch.setattr(
        runner._action_packet_lifecycle,
        "validate_action_commit_packet_lifecycle_g2_a_report_v01",
        validate_wrapper,
    )
    baseline = (
        runner._action_packet_lifecycle.collect_action_commit_packet_lifecycle_g2_a_v01()
    )
    observations = runner._collect_action_packet_negative_observations_v01(
        baseline
    )
    assert collection_count == 1
    assert validations == [(True, ()), *((False, ("g2a5_report_fail_closed",)),) * 10]
    assert tuple(item[0] for item in observations) == (
        conformance._G2A_NEGATIVE_PROBE_IDS_V02[10:]
    )
    assert len(observations) == 10
    for observation, expected_geometry in zip(
        observations,
        conformance._G2A_EXPECTED_NEGATIVE_GEOMETRY_V02[10:],
    ):
        probe_id, target, expected, observed, blocked, evidence = observation
        assert (probe_id, target, expected) == expected_geometry
        assert observed == ("g2a5_report_fail_closed",)
        assert blocked is True
        assert evidence == "demo/run_action_commit_packet_lifecycle_g2_a_v01.py"
        result = conformance.build_negative_conformance_result_v01(
            probe_id=probe_id,
            target_contract=target,
            expected_reason_codes=expected,
            observed_reason_codes=observed,
            blocked=blocked,
            evidence_refs=(evidence,),
            real_world_effects_count=0,
        )
        assert result.status == conformance.STATUS_PASS
        assert result.result_id == conformance._negative_id(result)

    class _AlwaysEqual:
        def __eq__(self, other):
            return True

        def __hash__(self):
            return hash(conformance.NEGATIVE_PROBE_IDS[10])

    class _AlwaysEqualStr(str):
        def __eq__(self, other):
            return True

        __hash__ = str.__hash__

    valid = conformance.build_negative_conformance_result_v01(
        probe_id=conformance.NEGATIVE_PROBE_IDS[10],
        target_contract=conformance._EXPECTED_NEGATIVE_GEOMETRY[10][1],
        expected_reason_codes=("g2a5_report_fail_closed",),
        observed_reason_codes=("g2a5_report_fail_closed",),
        blocked=True,
        evidence_refs=("demo/run_action_commit_packet_lifecycle_g2_a_v01.py",),
        real_world_effects_count=0,
    )
    custom_object = replace(valid, probe_id=_AlwaysEqual())
    custom_str = replace(valid, probe_id=_AlwaysEqualStr("forged"))
    assert conformance.validate_negative_conformance_result_v01(custom_object)
    assert conformance.validate_negative_conformance_result_v01(custom_str)


def test_g2a6_conformance_and_living_gauntlet_are_deterministic_and_zero_effect():
    release_hashes_before = (
        hashlib.sha256(COMPLETION_MANIFEST_PATH.read_bytes()).hexdigest(),
        hashlib.sha256(
            (REPOSITORY_ROOT / "release/integration_seam_index.json").read_bytes()
        ).hexdigest(),
    )
    first_conformance = runner.collect_standalone_kernel_conformance_v01(
        implementation_commit="abcdef0"
    )
    second_conformance = runner.collect_standalone_kernel_conformance_v01(
        implementation_commit="abcdef0"
    )
    first_living = living.collect_living_gauntlet_v01()
    second_living = living.collect_living_gauntlet_v01()
    assert (
        conformance.kernel_conformance_report_to_plain_dict_v01(first_conformance)
        == conformance.kernel_conformance_report_to_plain_dict_v01(
            second_conformance
        )
    )
    assert first_living == second_living
    assert first_conformance.final_status == conformance.STATUS_PASS
    assert (
        first_conformance.counters.category_pass_count,
        first_conformance.counters.domain_pass_count,
        first_conformance.counters.negative_pass_count,
    ) == (12, 2, 30)
    assert first_living["final_status"] == living.STATUS_PASS
    assert first_living["counters"]["active_act_pass_count"] == 15
    assert (
        first_conformance.counters.provider_call_count,
        first_conformance.counters.network_call_count,
        first_conformance.counters.gemini_call_count,
        first_conformance.counters.created_authority_count,
        first_conformance.counters.created_permission_count,
        first_conformance.counters.real_world_effects_count,
        first_living["counters"]["real_world_effects_count"],
    ) == (0, 0, 0, 0, 0, 0, 0)
    assert release_hashes_before == (
        hashlib.sha256(COMPLETION_MANIFEST_PATH.read_bytes()).hexdigest(),
        hashlib.sha256(
            (REPOSITORY_ROOT / "release/integration_seam_index.json").read_bytes()
        ).hexdigest(),
    )
    source = inspect.getsource(runner) + inspect.getsource(living)
    for forbidden in (
        "run_airline_all_real",
        "run_supplier_programme",
        "run_package",
        "run_anchor",
        "run_sealed_replay",
    ):
        assert forbidden not in source


_G2B_EXPECTED_CATEGORY = (
    "DRSSemanticAddressReuseCertificateConformance"
)
_G2B_EXPECTED_CHECKS = (
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
)
_G2B_EXPECTED_PROBES = (
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


def _historical_v02_report(current):
    categories = current.category_results[:11]
    negatives = current.negative_test_results[:20]
    active_refs = current.active_gauntlet_refs[:13]
    evidence_refs = current.evidence_refs
    provisional = conformance.KernelConformanceReportV01(
        report_id="0" * 64,
        conformance_version="v0.2",
        implementation_commit=current.implementation_commit,
        category_results=categories,
        domain_results=current.domain_results,
        negative_test_results=negatives,
        active_gauntlet_refs=active_refs,
        evidence_refs=evidence_refs,
        limitations=current.limitations,
        counters=conformance._derive_counters(
            categories,
            current.domain_results,
            negatives,
            active_refs,
            evidence_refs,
        ),
        final_status=conformance.STATUS_PASS,
    )
    return conformance._replace_report_id(provisional)


def _reversion(report, version):
    return conformance._replace_report_id(
        replace(report, conformance_version=version)
    )


def test_g2b6_conformance_v03_preserves_v02_geometry(
    standalone_report,
):
    historical_v01 = _historical_v01_report()
    historical_v02 = _historical_v02_report(standalone_report)
    assert conformance.validate_kernel_conformance_report_v01(
        historical_v01
    ) == ()
    assert conformance.validate_kernel_conformance_report_v01(
        historical_v02
    ) == ()
    assert conformance.validate_kernel_conformance_report_v01(
        standalone_report
    ) == ()
    assert (
        len(historical_v01.category_results),
        len(historical_v01.domain_results),
        len(historical_v01.negative_test_results),
        len(historical_v01.active_gauntlet_refs),
    ) == (10, 2, 10, 12)
    assert (
        len(historical_v02.category_results),
        len(historical_v02.domain_results),
        len(historical_v02.negative_test_results),
        len(historical_v02.active_gauntlet_refs),
    ) == (11, 2, 20, 13)
    assert (
        standalone_report.conformance_version,
        len(standalone_report.category_results),
        len(standalone_report.domain_results),
        len(standalone_report.negative_test_results),
        len(standalone_report.active_gauntlet_refs),
    ) == ("v0.3", 12, 2, 30, 14)
    assert standalone_report.category_results[:11] == (
        historical_v02.category_results
    )
    assert standalone_report.negative_test_results[:20] == (
        historical_v02.negative_test_results
    )
    assert standalone_report.active_gauntlet_refs[:13] == (
        historical_v02.active_gauntlet_refs
    )
    mixed = (
        _reversion(historical_v02, "v0.1"),
        _reversion(standalone_report, "v0.1"),
        _reversion(historical_v01, "v0.2"),
        _reversion(standalone_report, "v0.2"),
        _reversion(historical_v01, "v0.3"),
        _reversion(historical_v02, "v0.3"),
        _reversion(standalone_report, "v0.4"),
    )
    for forged in mixed:
        assert conformance.validate_kernel_conformance_report_v01(forged)
        assert "conformance_report_geometry_invalid" in (
            conformance.validate_kernel_conformance_report_v01(forged)
        )


def test_g2b6_drs_semantic_address_reuse_certificate_category_is_exact(
    standalone_report,
):
    category = standalone_report.category_results[11]
    assert category.category_id == _G2B_EXPECTED_CATEGORY
    assert category.required_check_ids == _G2B_EXPECTED_CHECKS
    assert category.passed_check_ids == _G2B_EXPECTED_CHECKS
    assert category.failed_check_ids == ()
    assert category.evidence_refs == (
        "runtime:kernel_conformance:"
        "DRSSemanticAddressReuseCertificateConformance",
    )
    assert category.limitation_refs == (
        "limitation_g2b6_deterministic_local_drs_semantic_reuse_only",
    )
    assert category.status == conformance.STATUS_PASS
    assert category.real_world_effects_count == 0
    assert category.result_id == conformance._category_id(category)
    failed = conformance.build_conformance_category_result_v01(
        category_id=category.category_id,
        check_results=tuple(
            (check_id, index != 0)
            for index, check_id in enumerate(_G2B_EXPECTED_CHECKS)
        ),
        evidence_refs=category.evidence_refs,
        limitation_refs=category.limitation_refs,
    )
    forged_report = conformance._replace_report_id(
        replace(
            standalone_report,
            category_results=(
                *standalone_report.category_results[:11],
                failed,
            ),
            counters=conformance._derive_counters(
                (
                    *standalone_report.category_results[:11],
                    failed,
                ),
                standalone_report.domain_results,
                standalone_report.negative_test_results,
                standalone_report.active_gauntlet_refs,
                standalone_report.evidence_refs,
            ),
            final_status=conformance.STATUS_FAIL_CLOSED,
        )
    )
    assert conformance.validate_kernel_conformance_report_v01(
        forged_report
    ) == ()
    assert failed.status == conformance.STATUS_FAIL_CLOSED


def test_g2b6_drs_negative_probe_matrix_is_exact(
    monkeypatch: pytest.MonkeyPatch,
):
    collection_count = 0
    validations = []
    original_collect = (
        runner._g2b.collect_drs_semantic_address_reuse_certificate_g2_b_v01
    )
    original_validate = (
        runner._g2b.validate_drs_semantic_address_reuse_certificate_g2_b_report_v01
    )

    def collect_once():
        nonlocal collection_count
        collection_count += 1
        monkeypatch.setattr(
            runner._g2b,
            "validate_drs_semantic_address_reuse_certificate_g2_b_report_v01",
            original_validate,
        )
        try:
            return original_collect()
        finally:
            monkeypatch.setattr(
                runner._g2b,
                "validate_drs_semantic_address_reuse_certificate_g2_b_report_v01",
                validate_wrapper,
            )

    def validate_wrapper(report):
        result = original_validate(report)
        validations.append((report, result))
        return result

    monkeypatch.setattr(
        runner._g2b,
        "collect_drs_semantic_address_reuse_certificate_g2_b_v01",
        collect_once,
    )
    monkeypatch.setattr(
        runner._g2b,
        "validate_drs_semantic_address_reuse_certificate_g2_b_report_v01",
        validate_wrapper,
    )
    baseline = (
        runner._g2b.collect_drs_semantic_address_reuse_certificate_g2_b_v01()
    )
    mutations = runner._g2b_negative_mutations_v01(baseline)
    observations = runner._collect_g2b_negative_observations_v01(
        baseline
    )

    assert collection_count == 1
    assert validations[0] == (baseline, (True, ()))
    assert len(validations) == 11
    assert all(
        result == (False, ("g2b_report_fail_closed",))
        for _, result in validations[1:]
    )
    assert tuple(item[0] for item in mutations) == _G2B_EXPECTED_PROBES
    assert tuple(item[0] for item in observations) == _G2B_EXPECTED_PROBES
    assert len(mutations) == len(observations) == 10
    for (probe_id, forged), observation in zip(
        mutations,
        observations,
    ):
        assert type(forged) is type(baseline), probe_id
        assert len(forged.domain_results) == 2, probe_id
        assert forged.report_id != baseline.report_id, probe_id
        assert (
            runner._g2b._reidentify_report_v01(forged) == forged
        ), probe_id
        (
            observed_probe_id,
            target,
            expected,
            observed,
            blocked,
            evidence,
        ) = observation
        assert observed_probe_id == probe_id
        assert target == (
            "demo.run_drs_semantic_address_reuse_certificate_g2_b_v01."
            "validate_drs_semantic_address_reuse_certificate_g2_b_report_v01"
        )
        assert expected == observed == ("g2b_report_fail_closed",)
        assert blocked is True
        assert evidence == (
            "demo/run_drs_semantic_address_reuse_certificate_g2_b_v01.py"
        )
    results = runner._build_g2b_negative_results_v01(observations)
    assert len({item.result_id for item in results}) == 10
    assert all(item.status == conformance.STATUS_PASS for item in results)
    assert all(item.real_world_effects_count == 0 for item in results)


def test_g2b6_conformance_and_gauntlet_are_deterministic_and_zero_effect():
    first_conformance = runner.collect_standalone_kernel_conformance_v01(
        implementation_commit="abcdef0"
    )
    second_conformance = runner.collect_standalone_kernel_conformance_v01(
        implementation_commit="abcdef0"
    )
    first_living = living.collect_living_gauntlet_v01()
    second_living = living.collect_living_gauntlet_v01()
    assert first_conformance == second_conformance
    assert (
        conformance.kernel_conformance_report_to_plain_dict_v01(
            first_conformance
        )
        == conformance.kernel_conformance_report_to_plain_dict_v01(
            second_conformance
        )
    )
    assert first_living == second_living
    assert living.render_living_gauntlet_v01(first_living) == (
        living.render_living_gauntlet_v01(second_living)
    )
    assert first_conformance.final_status == conformance.STATUS_PASS
    assert first_living["final_status"] == living.STATUS_PASS
    assert (
        first_conformance.counters.category_pass_count,
        first_conformance.counters.domain_pass_count,
        first_conformance.counters.negative_pass_count,
        first_conformance.counters.active_gauntlet_ref_count,
    ) == (12, 2, 30, 14)
    assert (
        first_conformance.counters.provider_call_count,
        first_conformance.counters.network_call_count,
        first_conformance.counters.gemini_call_count,
        first_conformance.counters.created_authority_count,
        first_conformance.counters.created_permission_count,
        first_conformance.counters.real_world_effects_count,
        first_living["counters"]["real_world_effects_count"],
    ) == (0, 0, 0, 0, 0, 0, 0)
