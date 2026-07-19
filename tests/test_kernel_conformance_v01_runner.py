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
from hedgehog.kernel import conformance_v01 as conformance


REPOSITORY_ROOT = Path(__file__).resolve().parents[1]
COMPLETION_MANIFEST_PATH = REPOSITORY_ROOT / "release/completion_manifest.json"


EXPECTED_CATEGORIES = (
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
EXPECTED_DOMAINS = ("airline", "supplier_water_filter")
EXPECTED_PROBES = (
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
EXPECTED_ACTIVE_REFS = (
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
        evidence_refs=(f"evidence:{category_id}",),
        limitation_refs=(f"limitation:{category_id}",),
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
        evidence_refs=(f"evidence:{probe_id}",),
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
        ("CONFORMANCE_VERSION", "v0.1"),
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
    assert (len(report.category_results), len(report.domain_results), len(report.negative_test_results)) == (10, 2, 10)
    assert report.counters.category_pass_count == 10
    assert report.counters.domain_pass_count == 2
    assert report.counters.negative_pass_count == 10
    assert report.counters.active_gauntlet_ref_count == 12


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
    assert len(projection["category_results"]) == 10
    assert len(projection["domain_results"]) == 2
    assert len(projection["negative_test_results"]) == 10


@pytest.mark.parametrize("index", range(10))
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


@pytest.mark.parametrize("index", range(10))
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
    assert "kernel_conformance_v01 v0.1" in rendered
    assert "final_status=PASS" in rendered
    for forbidden in ("manifest_hash=", "adapter_id=", "artifact_id=", "invoice", "shipment_sh"):
        assert forbidden not in rendered.lower()
