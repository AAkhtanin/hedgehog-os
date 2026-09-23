"""Deterministic Gate-1 conformance runner over already-executed Living acts.

The runner consumes already-executed Living act results and calls public
Kernel contracts for direct negative probes. It performs no provider, network,
Gemini, .tmp, all-real rerun, package regeneration, external connector, or real
effect operation. It is not production certification.
"""

from __future__ import annotations


def validate_kernel_conformance_g44_v01(**inputs):
    """The same supplied G4 extension and pinned retained parent; no collector."""
    from hedgehog.gate4_reference_release_v01 import validate_release_v01
    return validate_release_v01(**inputs)


def consume_gate3_mechanism_v01(bundle):
    """The supplied G3 path is independent of expensive E5 collection."""
    from hedgehog.kernel.conformance_v01 import build_gate3_mechanism_receipt_v01
    return build_gate3_mechanism_receipt_v01(bundle)


def collect_kernel_conformance_g36_v01(directory, *, implementation_commit=None):
    """G3-7 successor owner: one legacy E5 and one fresh G3 collection."""
    from hedgehog.gate3_mechanism_v01 import collect_mechanism_v01
    legacy=collect_standalone_kernel_conformance_v01(implementation_commit=implementation_commit)
    bundle=collect_mechanism_v01(directory)
    result=dict(profile='KERNEL_CONFORMANCE_G36_SUCCESSOR_V01',legacy=legacy,
        gate3=consume_gate3_mechanism_v01(bundle),gate3_bundle=bundle,g3_collector_calls=1,e5_collector_calls=1)
    if validate_kernel_conformance_g36_v01(result):raise ValueError('g36_conformance_successor_invalid')
    return result


def validate_kernel_conformance_g36_v01(value):
    """The existing full-report law remains mandatory alongside the G3 proof."""
    try:
        if set(value)!={'profile','legacy','gate3','gate3_bundle','g3_collector_calls','e5_collector_calls'} or value['profile']!='KERNEL_CONFORMANCE_G36_SUCCESSOR_V01':return ('g36_conformance_shape',)
        errors=conformance.validate_kernel_conformance_report_v01(value['legacy'])
        if errors:return errors
        if value['gate3']!=consume_gate3_mechanism_v01(value['gate3_bundle']) or (value['g3_collector_calls'],value['e5_collector_calls'])!=(1,1):return ('g36_conformance_binding',)
        return ()
    except (TypeError,KeyError,ValueError):return ('g36_conformance_supplied_invalid',)

from collections.abc import Mapping
from dataclasses import asdict as _asdict
from dataclasses import fields, replace
import hashlib
import inspect
import json
import re
import subprocess

import demo.run_action_commit_packet_lifecycle_g2_a_v01 as _action_packet_lifecycle
from demo import (
    run_drs_semantic_address_reuse_certificate_g2_b_v01 as _g2b,
)
import demo.run_execution_mode_router_g2_c_v01 as _g2c
import demo.run_fractal_runtime_g2_d_v02 as _g2d
import demo.run_continuous_delta_runtime_g2_e_v01 as _g2e
import hedgehog.kernel as _kernel_package
from hedgehog.kernel import execution_mode_router_v01 as _execution_mode_router
from hedgehog.kernel import transition_registry_v01 as _transition_registry
from hedgehog import drs_memory_resolution_v01 as _drs_resolution
from hedgehog.domains.airline import kernel_adapter_v01 as airline_adapter
from hedgehog.domains.supplier_water_filter import (
    kernel_adapter_v01 as supplier_adapter,
)
from hedgehog.kernel import conformance_v01 as conformance
from hedgehog.kernel.effect_firewall_v01 import (
    EFFECT_DECISION_BLOCKED_FAIL_CLOSED,
    authorize_effect_request_v01,
    build_effect_firewall_v01,
    build_effect_request_v01,
    effect_firewall_to_plain_dict_v01,
    validate_effect_firewall_decision_v01,
    validate_effect_firewall_v01,
    validate_effect_request_v01,
)
from hedgehog.kernel.integrity_replay_v01 import (
    AuthorityClassBindingV01,
    EvidenceClassBindingV01,
    RootOwnershipBindingV01,
    STATUS_BLOCKED_FAIL_CLOSED as INTEGRITY_BLOCKED,
    build_artifact_manifest_v01,
    build_canonical_artifact_ref_v01,
    build_default_seal_profile_v01,
    canonical_json_bytes_v01,
    domain_separated_sha256_hex_v01,
    verify_artifact_manifest_v01,
    verify_artifact_replay_v01,
)
from hedgehog.kernel.multiroot_v01 import (
    STATUS_FAIL_CLOSED as MULTIROOT_FAIL_CLOSED,
    build_root_decision_envelope_v01,
    build_transaction_outcome_envelope_v01,
    validate_multiroot_v01,
)
from hedgehog.kernel.root_decision_v01 import (
    ROOT_DECISION_ACCEPT,
    ROOT_DECISION_BLOCKED_FAIL_CLOSED,
    build_root_decision_input_v01,
    build_root_decision_kernel_v01,
    decide_root_v01,
    validate_root_decision_result_v01,
)
from hedgehog.kernel import root_decision_v01 as _root_decision
from hedgehog.kernel.root_signer_isolation_v01 import (
    build_root_owned_commitment_v01,
    build_trusted_root_key_set_v01,
    generate_root_signer_capability_v01,
    sign_root_owned_commitment_v01,
)
from hedgehog.kernel.semantic_work_v01 import (
    build_actor_contribution_v01,
    build_evidence_binding_v01,
    build_normalized_claim_v01,
    build_root_review_packet_from_contributions_v01,
    build_semantic_work_request_v01,
)
from hedgehog.kernel.transition_registry_v01 import (
    DECISION_BLOCKED_FAIL_CLOSED,
    build_default_transition_registry_v01,
    lookup_transition_v01,
    validate_transition_decision_v01,
    validate_transition_registry_v01,
)
from hedgehog.kernel.trust_model_v01 import (
    build_default_component_trust_profiles_v01,
)


RUNNER_ID = "kernel_conformance_v01"
_G2C_RUNNER_VERSION_V03 = "v0.3"
RUNNER_VERSION = "v0.7"
SLICE_ID = "domain_neutral_reference_kernel_gate1_g1e"

KERNEL_CONFORMANCE_PROFILE_V05_HISTORICAL = (
    "kernel_conformance_v0_5_historical"
)
KERNEL_CONFORMANCE_PROFILE_V06_HISTORICAL = (
    "kernel_conformance_v0_6_historical"
)
KERNEL_CONFORMANCE_PROFILE_V07_CURRENT = "kernel_conformance_v0_7_current"
DEFAULT_KERNEL_CONFORMANCE_PROFILE = KERNEL_CONFORMANCE_PROFILE_V07_CURRENT

_COMMIT_PATTERN = re.compile(r"^[0-9a-f]{7,40}$")
_G2C_TRANSITION_FUNCTION_NAMES_V03 = (
    "build_execution_mode_transition_registry_profile_v01",
    "validate_execution_mode_transition_registry_profile_v01",
    "execution_mode_transition_registry_profile_to_plain_dict_v01",
    "validate_execution_mode_transition_decision_v01",
    "execution_mode_transition_decision_to_plain_dict_v01",
    "rebuild_execution_mode_transition_decision_identity_v01",
)
_V05_HISTORICAL_BASE_ACT_IDS = (
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
    "action_packet_lifecycle",
    "drs_semantic_address_and_reuse_certificate",
    "execution_mode_router",
    "fractal_runtime",
)
_V06_HISTORICAL_BASE_ACT_IDS = (
    "airline_deterministic_transaction_runtime",
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
    "action_packet_lifecycle",
    "drs_semantic_address_and_reuse_certificate",
    "execution_mode_router",
    "fractal_runtime",
)
_BASE_ACT_IDS = (*_V06_HISTORICAL_BASE_ACT_IDS, "continuous_delta_runtime")
_ACT_FIELDS = frozenset(
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
_ACT_SOURCES = {
    "airline_deterministic_transaction_runtime": (
        "demo.run_tri_party_airline_ticket_purchase_mock_e2e_v01",
        "collect_tri_party_airline_ticket_purchase_mock_e2e_v01",
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
    "transition_registry": (
        "demo.run_living_gauntlet_v01",
        "collect_transition_registry_gauntlet_act_v01",
    ),
    "root_decision_kernel": (
        "demo.run_living_gauntlet_v01",
        "collect_root_decision_kernel_gauntlet_act_v01",
    ),
    "effect_firewall": (
        "demo.run_living_gauntlet_v01",
        "collect_effect_firewall_gauntlet_act_v01",
    ),
    "generic_multiroot": (
        "demo.run_living_gauntlet_v01",
        "collect_generic_multiroot_gauntlet_act_v01",
    ),
    "supplier_water_filter_portability": (
        "demo.run_living_gauntlet_v01",
        "collect_supplier_water_filter_portability_gauntlet_act_v01",
    ),
    "action_packet_lifecycle": (
        "demo.run_living_gauntlet_v01",
        "collect_action_packet_lifecycle_gauntlet_act_v01",
    ),
    "drs_semantic_address_and_reuse_certificate": (
        "demo.run_living_gauntlet_v01",
        (
            "collect_drs_semantic_address_and_reuse_certificate_"
            "gauntlet_act_v01"
        ),
    ),
    "execution_mode_router": (
        "demo.run_execution_mode_router_g2_c_v01",
        "collect_execution_mode_router_g2_c_v01",
    ),
    "fractal_runtime": (
        "demo.run_fractal_runtime_g2_d_v02",
        "collect_fractal_runtime_g2_d_v02",
    ),
    "continuous_delta_runtime": (
        "demo.run_continuous_delta_runtime_g2_e_v01",
        "collect_continuous_delta_runtime_g2_e_v01",
    ),
}
_EVIDENCE_REFS = (
    "hedgehog/kernel/integrity_replay_v01.py",
    "hedgehog/kernel/root_signer_isolation_v01.py",
    "hedgehog/kernel/trust_model_v01.py",
    "hedgehog/kernel/semantic_work_v01.py",
    "hedgehog/kernel/abi_v01.py",
    "hedgehog/kernel/transition_registry_v01.py",
    "hedgehog/kernel/root_decision_v01.py",
    "hedgehog/kernel/effect_firewall_v01.py",
    "hedgehog/kernel/multiroot_v01.py",
    "hedgehog/domains/airline/kernel_adapter_v01.py",
    "hedgehog/domains/supplier_water_filter/kernel_adapter_v01.py",
    "demo/run_action_commit_packet_lifecycle_g2_a_v01.py",
    "demo/run_drs_semantic_address_reuse_certificate_g2_b_v01.py",
    "demo/run_execution_mode_router_g2_c_v01.py",
    "demo/run_fractal_runtime_g2_d_v02.py",
    "demo/run_continuous_delta_runtime_g2_e_v01.py",
)
_LIMITATIONS = (
    "deterministic_current_repository_conformance_only",
    "exact_accepted_airline_and_supplier_adapters_only",
    "no_fresh_all_real_run_or_package_regeneration",
    "no_root_attestation_pki_federation_or_production_connector",
    "independent_audit_and_consolidated_docs_closure_pending",
    "limitation_g2a6_deterministic_local_actionpacket_lifecycle_only",
    "limitation_g2b6_deterministic_local_drs_semantic_reuse_only",
    "limitation_g2c6_deterministic_two_domain_execution_mode_router_only",
    "limitation_g2d6_validated_d5_report_only",
    "limitation_g2e6_validated_public_e5_report_only",
)


def resolve_current_implementation_commit_v01() -> str:
    try:
        completed = subprocess.run(
            ("git", "rev-parse", "--short", "HEAD"),
            check=True,
            capture_output=True,
            text=True,
        )
        value = completed.stdout.strip()
        if _COMMIT_PATTERN.fullmatch(value) is None:
            raise ValueError
        return value
    except Exception:
        raise ValueError("implementation_commit_resolution_failed") from None


def kernel_conformance_profile_metadata_v01(
    profile_id: str = DEFAULT_KERNEL_CONFORMANCE_PROFILE,
) -> dict[str, object]:
    """Expose profile geometry without executing historical profile acts."""

    return conformance.kernel_conformance_profile_metadata_v01(profile_id)


def _validated_e5_receipt_v01(
    report: object,
) -> tuple[_g2e.ContinuousDeltaRuntimeG2EReportV01, str, int]:
    validated = _g2e.validate_continuous_delta_runtime_g2_e_report_v01(report)
    canonical_bytes = _g2e.render_continuous_delta_runtime_g2_e_v01(
        validated
    ).encode("utf-8")
    return validated, hashlib.sha256(canonical_bytes).hexdigest(), len(canonical_bytes)


def collect_kernel_conformance_v01(
    *,
    active_act_results: tuple[Mapping[str, object], ...] | None = None,
    implementation_commit: str | None = None,
) -> conformance.KernelConformanceReportV01:
    try:
        continuous_delta_runtime_report = (
            _g2e.collect_continuous_delta_runtime_g2_e_v01()
        )
        continuous_delta_runtime_report, e5_sha256, e5_bytes = (
            _validated_e5_receipt_v01(continuous_delta_runtime_report)
        )
        if active_act_results is None:
            return _collect_standalone_kernel_conformance_with_validated_e5_v01(
                continuous_delta_runtime_report=continuous_delta_runtime_report,
                continuous_delta_runtime_report_sha256=e5_sha256,
                continuous_delta_runtime_report_bytes=e5_bytes,
                implementation_commit=implementation_commit,
            )
        if implementation_commit is None:
            raise ValueError("implementation_commit_invalid")
        fractal_runtime_report = _g2d.collect_fractal_runtime_g2_d_v02()
        reasons = _g2d.validate_fractal_runtime_g2_d_report_v02(
            fractal_runtime_report
        )
        if reasons:
            raise ValueError("kernel_conformance_runtime_invalid")
        return _collect_kernel_conformance_with_validated_fractal_runtime_v01(
            active_act_results=active_act_results,
            implementation_commit=implementation_commit,
            fractal_runtime_report=fractal_runtime_report,
            continuous_delta_runtime_report=continuous_delta_runtime_report,
            continuous_delta_runtime_report_sha256=e5_sha256,
            continuous_delta_runtime_report_bytes=e5_bytes,
        )
    except ValueError as exc:
        reason = (
            exc.args[0]
            if len(exc.args) == 1 and type(exc.args[0]) is str
            else "kernel_conformance_runtime_invalid"
        )
        allowed = {
            "active_gauntlet_results_invalid",
            "implementation_commit_invalid",
            "kernel_conformance_runtime_invalid",
        }
        raise ValueError(
            reason if reason in allowed else "kernel_conformance_runtime_invalid"
        ) from None
    except Exception:
        raise ValueError("kernel_conformance_runtime_invalid") from None


def _collect_kernel_conformance_with_validated_fractal_runtime_v01(
    *,
    active_act_results: tuple[Mapping[str, object], ...],
    implementation_commit: str,
    fractal_runtime_report: _g2d.FractalRuntimeG2DReportV02,
    continuous_delta_runtime_report: _g2e.ContinuousDeltaRuntimeG2EReportV01,
    continuous_delta_runtime_report_sha256: str,
    continuous_delta_runtime_report_bytes: int,
) -> conformance.KernelConformanceReportV01:
    try:
        rows = _validate_active_act_results(active_act_results)
        if _COMMIT_PATTERN.fullmatch(implementation_commit) is None:
            raise ValueError("implementation_commit_invalid")
        (
            continuous_delta_runtime_report,
            shared_e5_sha256,
            shared_e5_bytes,
        ) = _validated_e5_receipt_v01(continuous_delta_runtime_report)
        if (
            continuous_delta_runtime_report_sha256 != shared_e5_sha256
            or continuous_delta_runtime_report_bytes != shared_e5_bytes
        ):
            raise ValueError("kernel_conformance_runtime_invalid")
        by_id = {row["act_id"]: row for row in rows}
        action_packet_report = (
            _action_packet_lifecycle.collect_action_commit_packet_lifecycle_g2_a_v01()
        )
        action_packet_geometry_pass = _action_packet_report_geometry_passes_v01(
            action_packet_report
        )
        g2b_baseline = (
            _g2b.collect_drs_semantic_address_reuse_certificate_g2_b_v01()
        )
        g2b_observations = _collect_g2b_negative_observations_v01(
            g2b_baseline
        )
        g2c_baseline = _g2c.collect_execution_mode_router_g2_c_v01()
        g2c_observations = _collect_g2c_negative_observations_v01(
            g2c_baseline
        )
        g2d_observations = _collect_g2d_negative_observations_v01(
            fractal_runtime_report
        )
        g2e_observations = _collect_g2e_negative_observations_v01(
            continuous_delta_runtime_report
        )
        negatives = _collect_negative_results(
            by_id,
            action_packet_report,
            g2b_observations,
            g2c_observations,
            g2d_observations,
            g2e_observations,
        )
        domains = _build_domain_results(by_id, negatives)
        categories = _build_category_results(
            by_id,
            domains,
            negatives,
            action_packet_geometry_pass,
            g2b_baseline,
            g2c_baseline,
            fractal_runtime_report,
            continuous_delta_runtime_report,
        )
        report = conformance.build_kernel_conformance_report_v01(
            implementation_commit=implementation_commit,
            category_results=categories,
            domain_results=domains,
            negative_test_results=negatives,
            active_gauntlet_refs=_BASE_ACT_IDS,
            continuous_delta_runtime_report_sha256=(
                continuous_delta_runtime_report_sha256
            ),
            continuous_delta_runtime_report_bytes=(
                continuous_delta_runtime_report_bytes
            ),
            shared_conformance_e5_report_sha256=shared_e5_sha256,
            shared_conformance_e5_report_bytes=shared_e5_bytes,
            evidence_refs=_EVIDENCE_REFS,
            limitations=_LIMITATIONS,
        )
        if validate_kernel_conformance_runtime_v01(report):
            raise ValueError("kernel_conformance_runtime_invalid")
        return report
    except ValueError as exc:
        reason = (
            exc.args[0]
            if len(exc.args) == 1 and type(exc.args[0]) is str
            else "kernel_conformance_runtime_invalid"
        )
        allowed = {
            "active_gauntlet_results_invalid",
            "implementation_commit_invalid",
            "kernel_conformance_runtime_invalid",
        }
        raise ValueError(
            reason if reason in allowed else "kernel_conformance_runtime_invalid"
        ) from None
    except Exception:
        raise ValueError("kernel_conformance_runtime_invalid") from None


def collect_standalone_kernel_conformance_v01(
    *,
    implementation_commit: str | None = None,
) -> conformance.KernelConformanceReportV01:
    try:
        continuous_delta_runtime_report = (
            _g2e.collect_continuous_delta_runtime_g2_e_v01()
        )
        continuous_delta_runtime_report, e5_sha256, e5_bytes = (
            _validated_e5_receipt_v01(continuous_delta_runtime_report)
        )
        return _collect_standalone_kernel_conformance_with_validated_e5_v01(
            continuous_delta_runtime_report=continuous_delta_runtime_report,
            continuous_delta_runtime_report_sha256=e5_sha256,
            continuous_delta_runtime_report_bytes=e5_bytes,
            implementation_commit=implementation_commit,
        )
    except ValueError:
        raise
    except Exception:
        raise ValueError("kernel_conformance_standalone_failed") from None


def _collect_standalone_kernel_conformance_with_validated_e5_v01(
    *,
    continuous_delta_runtime_report: _g2e.ContinuousDeltaRuntimeG2EReportV01,
    continuous_delta_runtime_report_sha256: str,
    continuous_delta_runtime_report_bytes: int,
    implementation_commit: str | None = None,
) -> conformance.KernelConformanceReportV01:
    from demo import run_living_gauntlet_v01 as living

    (
        continuous_delta_runtime_report,
        shared_e5_sha256,
        shared_e5_bytes,
    ) = _validated_e5_receipt_v01(continuous_delta_runtime_report)
    if (
        continuous_delta_runtime_report_sha256 != shared_e5_sha256
        or continuous_delta_runtime_report_bytes != shared_e5_bytes
    ):
        raise ValueError("kernel_conformance_runtime_invalid")
    base_results = living.collect_living_gauntlet_base_act_results_v01()
    lifecycle_result = living.collect_action_packet_lifecycle_gauntlet_act_v01()
    g2b_result = (
        living.collect_drs_semantic_address_and_reuse_certificate_gauntlet_act_v01()
    )
    g2c_result = living.collect_execution_mode_router_gauntlet_act_v01()
    fractal_runtime_report = _g2d.collect_fractal_runtime_g2_d_v02()
    reasons = _g2d.validate_fractal_runtime_g2_d_report_v02(
        fractal_runtime_report
    )
    if reasons:
        raise ValueError("kernel_conformance_runtime_invalid")
    g2d_result = living._fractal_runtime_gauntlet_act_from_validated_report_v01(
        fractal_runtime_report
    )
    g2e_result = (
        living._continuous_delta_runtime_gauntlet_act_from_validated_report_v01(
            continuous_delta_runtime_report
        )
    )
    active_results = (
        *base_results,
        _asdict(lifecycle_result),
        _asdict(g2b_result),
        _asdict(g2c_result),
        _asdict(g2d_result),
        _asdict(g2e_result),
    )
    commit = (
        resolve_current_implementation_commit_v01()
        if implementation_commit is None
        else implementation_commit
    )
    return _collect_kernel_conformance_with_validated_fractal_runtime_v01(
        active_act_results=active_results,
        implementation_commit=commit,
        fractal_runtime_report=fractal_runtime_report,
        continuous_delta_runtime_report=continuous_delta_runtime_report,
        continuous_delta_runtime_report_sha256=shared_e5_sha256,
        continuous_delta_runtime_report_bytes=shared_e5_bytes,
    )


def validate_kernel_conformance_runtime_v01(
    report: object,
) -> tuple[str, ...]:
    try:
        errors = list(conformance.validate_kernel_conformance_report_v01(report))
        if type(report) is not conformance.KernelConformanceReportV01:
            return tuple(dict.fromkeys(errors or ("kernel_conformance_runtime_invalid",)))
        if tuple(item.category_id for item in report.category_results) != conformance.CATEGORY_IDS:
            errors.append("kernel_conformance_category_geometry_invalid")
        if tuple(item.domain_id for item in report.domain_results) != conformance.DOMAIN_IDS:
            errors.append("kernel_conformance_domain_geometry_invalid")
        if tuple(item.probe_id for item in report.negative_test_results) != conformance.NEGATIVE_PROBE_IDS:
            errors.append("kernel_conformance_negative_geometry_invalid")
        if report.active_gauntlet_refs != _BASE_ACT_IDS:
            errors.append("kernel_conformance_active_refs_invalid")
        if (
            report.profile_id != KERNEL_CONFORMANCE_PROFILE_V07_CURRENT
            or report.conformance_version != "v0.7"
            or report.historical_profile_ref
            != KERNEL_CONFORMANCE_PROFILE_V06_HISTORICAL
            or report.claim_to_current_act
            != conformance.CURRENT_REGRESSION_CLAIM_TO_ACTS_V07
            or report.current_act_count != len(_BASE_ACT_IDS)
        ):
            errors.append("kernel_conformance_profile_invalid")
        if report.final_status != conformance.STATUS_PASS:
            errors.append("kernel_conformance_not_pass")
        counters = report.counters
        if (
            counters.category_pass_count != 15
            or counters.domain_pass_count != 2
            or counters.negative_pass_count != 60
            or counters.active_gauntlet_ref_count != len(_BASE_ACT_IDS)
            or any(
                value != 0
                for value in (
                    counters.provider_call_count,
                    counters.network_call_count,
                    counters.gemini_call_count,
                    counters.created_authority_count,
                    counters.created_permission_count,
                    counters.real_world_effects_count,
                )
            )
        ):
            errors.append("kernel_conformance_counter_boundary_invalid")
        if (
            report.continuous_delta_runtime_execution_count != 1
            or report.continuous_delta_runtime_public_validation_status
            != conformance.STATUS_PASS
            or not _valid_e5_sha256_v01(
                report.continuous_delta_runtime_report_sha256
            )
            or report.continuous_delta_runtime_report_sha256
            != report.shared_conformance_e5_report_sha256
            or report.continuous_delta_runtime_report_bytes <= 0
            or report.continuous_delta_runtime_report_bytes
            != report.shared_conformance_e5_report_bytes
            or report.shared_conformance_e5_collector_calls != 0
            or report.continuous_delta_runtime_second_execution_count != 0
            or report.continuous_delta_runtime_cache_reuse_count != 0
            or report.continuous_delta_runtime_test_fixture_substitution_count
            != 0
            or report.continuous_delta_runtime_private_g2d_calls != 0
            or report.continuous_delta_runtime_reconstructed_case_count != 0
        ):
            errors.append("kernel_conformance_e5_receipt_invalid")
        supplier = report.domain_results[1]
        if "supplier_multiroot_mixed_visible" not in supplier.passed_check_ids:
            errors.append("kernel_conformance_supplier_mixed_missing")
        return tuple(dict.fromkeys(errors))
    except Exception:
        return ("kernel_conformance_runtime_unexpected_exception",)


def render_kernel_conformance_v01(
    report: conformance.KernelConformanceReportV01,
) -> str:
    if validate_kernel_conformance_runtime_v01(report):
        raise ValueError("kernel_conformance_runtime_invalid") from None
    counters = report.counters
    lines = [
        f"kernel_conformance: {RUNNER_ID} {RUNNER_VERSION}",
        f"profile_id={report.profile_id}",
        f"historical_profile_ref={report.historical_profile_ref}",
        f"current_act_count={report.current_act_count}",
        f"implementation_commit={report.implementation_commit}",
        "",
        "[CATEGORY RESULTS]",
    ]
    lines.extend(
        f"category={item.category_id} | status={item.status}"
        for item in report.category_results
    )
    lines.extend(("", "[DOMAIN RESULTS]"))
    lines.extend(
        f"domain={item.domain_id} | status={item.status}"
        for item in report.domain_results
    )
    lines.append("supplier_multiroot=MIXED")
    lines.extend(("", "[NEGATIVE RESULTS]"))
    lines.extend(
        f"probe={item.probe_id} | status={item.status}"
        for item in report.negative_test_results
    )
    lines.extend(
        (
            "",
            "[COUNTERS]",
            f"categories={counters.category_pass_count}/{counters.category_result_count}",
            f"domains={counters.domain_pass_count}/{counters.domain_result_count}",
            f"negative={counters.negative_pass_count}/{counters.negative_result_count}",
            "provider_network_gemini="
            f"{counters.provider_call_count}/{counters.network_call_count}/{counters.gemini_call_count}",
            f"created_authority={counters.created_authority_count}",
            f"created_permission={counters.created_permission_count}",
            f"real_world_effects={counters.real_world_effects_count}",
            "continuous_delta_runtime_execution_count="
            f"{report.continuous_delta_runtime_execution_count}",
            "continuous_delta_runtime_public_validation_status="
            f"{report.continuous_delta_runtime_public_validation_status}",
            "continuous_delta_runtime_report_sha256="
            f"{report.continuous_delta_runtime_report_sha256}",
            "continuous_delta_runtime_report_bytes="
            f"{report.continuous_delta_runtime_report_bytes}",
            "shared_conformance_e5_collector_calls="
            f"{report.shared_conformance_e5_collector_calls}",
            f"final_status={report.final_status}",
        )
    )
    return "\n".join(lines) + "\n"


def main() -> int:
    try:
        report = collect_standalone_kernel_conformance_v01()
        print(render_kernel_conformance_v01(report), end="")
        return 0
    except Exception:
        print(
            f"kernel_conformance: {RUNNER_ID} {RUNNER_VERSION}\n"
            "final_status=FAIL_CLOSED\n",
            end="",
        )
        return 1


def _validate_active_act_results(
    active_act_results: object,
) -> tuple[dict[str, object], ...]:
    if (
        type(active_act_results) is not tuple
        or len(active_act_results) != len(_BASE_ACT_IDS)
    ):
        raise ValueError("active_gauntlet_results_invalid")
    copied: list[dict[str, object]] = []
    for expected_id, row in zip(_BASE_ACT_IDS, active_act_results):
        if type(row) is not dict or frozenset(row) != _ACT_FIELDS:
            raise ValueError("active_gauntlet_results_invalid")
        copied_row = {
            key: tuple(value) if key == "errors" and type(value) is tuple else value
            for key, value in row.items()
        }
        if (
            copied_row.get("act_id") != expected_id
            or copied_row.get("executed") is not True
            or copied_row.get("runtime_status") != conformance.STATUS_PASS
            or copied_row.get("state") != conformance.STATUS_PASS
            or copied_row.get("errors") != ()
            or copied_row.get("root_authority_preserved") is not True
            or copied_row.get("no_real_connector_or_action") is not True
            or type(copied_row.get("real_world_effects_count")) is not int
            or copied_row.get("real_world_effects_count") != 0
            or (
                copied_row.get("source_module"),
                copied_row.get("source_symbol"),
            )
            != _ACT_SOURCES[expected_id]
        ):
            raise ValueError("active_gauntlet_results_invalid")
        copied.append(copied_row)
    return tuple(copied)


def _act_safe(row: Mapping[str, object]) -> bool:
    return (
        row.get("executed") is True
        and row.get("runtime_status") == conformance.STATUS_PASS
        and row.get("state") == conformance.STATUS_PASS
        and row.get("errors") == ()
        and row.get("root_authority_preserved") is True
        and row.get("no_real_connector_or_action") is True
        and row.get("real_world_effects_count") == 0
    )


def _action_packet_report_geometry_passes_v01(report: object) -> bool:
    try:
        if (
            type(report)
            is not _action_packet_lifecycle.ActionCommitPacketLifecycleG2A5ReportV01
            or report.final_status != conformance.STATUS_PASS
            or report.same_packet_family is not True
            or report.same_transition_registry_id is not True
            or report.same_authority_law is not True
            or report.immutable_history_proven is not True
            or report.closed_domain_artifacts_rerun is not False
            or any(
                type(value) is not int or value != 0
                for value in (
                    report.provider_calls,
                    report.network_calls,
                    report.gemini_calls,
                    report.adapter_calls,
                    report.receipt_creations,
                    report.real_world_effects_count,
                )
            )
        ):
            return False
        expected_domains = (
            (
                report.airline,
                "AIRLINE",
                "DEPENDENCY_CHANGED",
                "root:g2a5:airline",
            ),
            (
                report.supplier,
                "SUPPLIER",
                "ROOT_BOUND_KILL_SWITCH",
                "root:g2a5:supplier",
            ),
        )
        for result, domain_shape, invalidation_class, root_id in expected_domains:
            replay = result.replay_report
            inspection = result.present_inspection
            if (
                result.domain_shape != domain_shape
                or result.owning_local_root_id != root_id
                or result.invalidation_class != invalidation_class
                or result.authority_effect != "DETERMINISTIC_BLOCK"
                or result.transition_rule_id != "g2a_t09_pending_block"
                or result.lifecycle_before != "PENDING_FULFILLMENT"
                or result.lifecycle_after != "BLOCKED"
                or result.idempotency_disposition_after != "RESERVED"
                or result.reservation_owner_packet_id_after != result.packet_id
                or replay.registry_unchanged is not True
                or replay.historical_temporal_replay_pass is not True
                or replay.t24_reserved_history_replay_pass is not True
                or replay.distinct_firewall_attempt_replay_pass is not True
                or inspection.historical_result_unchanged is not True
                or inspection.present_eligibility_status != "NON_EXECUTABLE"
                or inspection.present_executable is not False
                or inspection.retry_eligible is not False
                or result.registry_creates_authority is not False
                or result.adapter_calls != 0
                or result.receipt_creations != 0
                or result.real_world_effects_count != 0
            ):
                return False
        return report.airline.packet_id != report.supplier.packet_id
    except Exception:
        return False


def _build_domain_results(
    by_id: Mapping[str, Mapping[str, object]],
    negatives: tuple[conformance.NegativeConformanceResultV01, ...],
) -> tuple[conformance.DomainConformanceResultV01, ...]:
    airline_runtime = by_id["airline_deterministic_transaction_runtime"]
    airline_adapter_act = by_id["generic_integrity_replay"]
    supplier = by_id["supplier_water_filter_portability"]
    airline_negative = negatives[8]
    supplier_negative = negatives[9]
    airline_checks = (
        ("airline_act_executed", _act_safe(airline_adapter_act)),
        ("airline_adapter_validated", _act_safe(airline_adapter_act)),
        ("airline_generic_unanchored_exact", _act_safe(airline_adapter_act)),
        ("airline_generic_anchored_pass", _act_safe(airline_adapter_act)),
        ("airline_generic_replay_pass", _act_safe(airline_adapter_act)),
        ("airline_causal_bundle_valid", _act_safe(airline_adapter_act)),
        ("airline_root_authority_preserved", _act_safe(airline_runtime)),
        ("airline_effect_access_none", airline_negative.status == conformance.STATUS_PASS),
        ("airline_real_effects_zero", airline_adapter_act["real_world_effects_count"] == 0),
        ("airline_frozen_reference_remains_evidence_only", "airline_all_real_frozen_reference" not in _BASE_ACT_IDS),
        ("airline_signature_verified_remains_false", _act_safe(airline_adapter_act)),
        ("airline_root_attestation_not_claimed", not hasattr(airline_adapter, "RootAttestation")),
    )
    supplier_checks = (
        ("supplier_act_executed", _act_safe(supplier)),
        ("supplier_exact_source_contract", _act_safe(supplier)),
        ("supplier_adapter_validated", _act_safe(supplier)),
        ("supplier_generic_unanchored_exact", _act_safe(supplier)),
        ("supplier_generic_anchored_pass", _act_safe(supplier)),
        ("supplier_generic_replay_pass", _act_safe(supplier)),
        ("supplier_causal_bundle_valid", _act_safe(supplier)),
        ("supplier_multiroot_mixed_visible", _act_safe(supplier)),
        ("supplier_root_authority_preserved", supplier["root_authority_preserved"] is True),
        ("supplier_effect_access_none", supplier_negative.status == conformance.STATUS_PASS),
        ("supplier_real_effects_zero", supplier["real_world_effects_count"] == 0),
        ("supplier_b_blocked", _act_safe(supplier)),
        ("shipment_held", _act_safe(supplier)),
        ("receipt_evidence_only", _act_safe(supplier)),
    )
    return (
        conformance.build_domain_conformance_result_v01(
            domain_id="airline",
            adapter_ref="hedgehog.domains.airline.kernel_adapter_v01",
            source_ref=(
                "demo.run_living_gauntlet_v01:"
                "collect_generic_integrity_replay_gauntlet_act_v01"
            ),
            check_results=airline_checks,
            evidence_refs=(
                "hedgehog/domains/airline/kernel_adapter_v01.py",
                "tests/test_airline_kernel_adapter_v01.py",
            ),
            limitation_refs=("limitation_g1d1_frozen_airline_projection_only",),
            provider_call_count=0,
            network_call_count=0,
            gemini_call_count=0,
            real_world_effects_count=0,
        ),
        conformance.build_domain_conformance_result_v01(
            domain_id="supplier_water_filter",
            adapter_ref=(
                "hedgehog.domains.supplier_water_filter.kernel_adapter_v01"
            ),
            source_ref=(
                "demo.run_living_gauntlet_v01:"
                "collect_supplier_water_filter_portability_gauntlet_act_v01"
            ),
            check_results=supplier_checks,
            evidence_refs=(
                "hedgehog/domains/supplier_water_filter/kernel_adapter_v01.py",
                "tests/test_supplier_water_filter_kernel_adapter_v01.py",
            ),
            limitation_refs=(
                "limitation_g1d2_supplier_water_filter_projection_only",
            ),
            provider_call_count=0,
            network_call_count=0,
            gemini_call_count=0,
            real_world_effects_count=0,
        ),
    )


def _g2b_baseline_geometry_v01(report: object) -> dict[str, bool]:
    checks = {
        "canonical_identity": False,
        "time": False,
        "pointer_policy": False,
        "eligibility": False,
        "ranking": False,
        "descent": False,
        "root_shortcut": False,
        "certificate_non_authority": False,
        "action_boundary": False,
        "cross_domain_invariance": False,
    }
    try:
        if (
            type(report) is not _g2b._G2B5DeterministicReportV01
            or report.final_status != conformance.STATUS_PASS
            or report.reason_codes != ()
            or report.domain_order
            != (
                "TRAVEL_POLICY_INFORMATION",
                "WAREHOUSE_MAINTENANCE_INFORMATION",
            )
            or len(report.domain_results) != 2
        ):
            return checks
        domains = report.domain_results
        operation_counters = dict(report.operation_counters)
        checks["canonical_identity"] = (
            report.report_id == _g2b._reidentify_report_v01(report).report_id
            and all(
                type(item) is _g2b._G2B5DomainProofV01
                and item.final_status == conformance.STATUS_PASS
                and item.reason_codes == ()
                for item in domains
            )
        )
        checks["time"] = all(
            type(item.answer_report.query.as_of) is int
            and type(item.answer_use_time) is int
            for item in domains
        )
        checks["pointer_policy"] = all(
            item.answer_report.memory_descent_result is not None
            and item.answer_report.memory_descent_result.executed_descent_class
            == "SUMMARY_ONLY"
            and item.answer_report.memory_descent_result.bytes_opened == 0
            for item in domains
        )
        checks["eligibility"] = all(
            item.answer_report.query_evaluations
            and all(
                evaluation.eligible_for_ranking is True
                for evaluation in item.answer_report.query_evaluations
                if evaluation.meaning_record_id
                in {
                    candidate.meaning_record_id
                    for candidate in item.answer_report.eligible_candidates
                }
            )
            for item in domains
        )
        checks["ranking"] = all(
            item.answer_report.ranked_candidate_ids
            and item.answer_report.selected_candidate_id
            == item.answer_report.ranked_candidate_ids[0]
            and item.answer_report.eligible_candidates
            and item.answer_report.selected_candidate_id
            == item.answer_report.eligible_candidates[
                0
            ].resolution_candidate_id
            for item in domains
        )
        checks["descent"] = all(
            item.answer_report.memory_descent_result is not None
            and item.answer_report.memory_descent_result.limits_respected
            is True
            and item.answer_report.memory_descent_result.real_world_effects_count
            == 0
            for item in domains
        )
        checks["root_shortcut"] = all(
            item.answer_report.root_shortcut_projection is not None
            and item.answer_report.reuse_certificate is not None
            for item in domains
        )
        checks["certificate_non_authority"] = (
            all(
                certificate is not None
                and certificate.creates_authority is False
                and certificate.creates_permission is False
                and certificate.creates_final_output is False
                and certificate.creates_action_commit_packet is False
                and certificate.creates_receipt is False
                and certificate.creates_capability is False
                and certificate.creates_effect_handle is False
                and certificate.creates_effect is False
                and certificate.real_world_effects_count == 0
                for certificate in (
                    item.answer_report.reuse_certificate for item in domains
                )
            )
            and all(
                operation_counters[name] == 0
                for name in (
                    "provider_calls",
                    "network_calls",
                    "gemini_calls",
                    "external_drs_calls",
                    "connector_calls",
                    "real_world_effects",
                    "canonical_meaning_records_mutated",
                    "final_outputs_created_by_drs",
                    "final_outputs_created_by_certificate",
                    "action_commit_packets_created",
                    "receipts_created",
                    "capabilities_created",
                    "effect_handles_created",
                )
            )
        )
        checks["action_boundary"] = (
            sum(len(item.negative_requests) for item in domains) == 8
            and operation_counters["action_negative_requests"] == 8
        )
        checks["cross_domain_invariance"] = (
            len({item.domain_id for item in domains}) == 2
            and all(
                item.pure_read_snapshot_before
                == item.pure_read_snapshot_after
                and item.context_report.selected_candidate_id is None
                and item.context_report.root_shortcut_projection is None
                and item.context_report.reuse_certificate is None
                and item.writeback_evidence["predecessor_preserved"] is True
                and item.writeback_evidence["successor_readback_exact"] is True
                and item.writeback_evidence["records_written"] == 1
                and item.writeback_evidence["real_world_effects_count"] == 0
                for item in domains
            )
        )
        return checks
    except Exception:
        return {key: False for key in checks}


def _g2c_package_facade_passes_v01() -> bool:
    try:
        type_names = tuple(item.__name__ for item in _execution_mode_router.G2C_TYPES_V01)
        router_names = tuple(
            name
            for name in _execution_mode_router.PUBLIC_G2C_FUNCTIONS_V01
            if name not in _G2C_TRANSITION_FUNCTION_NAMES_V03
        )
        direct_names = (
            *type_names,
            *router_names,
            *_G2C_TRANSITION_FUNCTION_NAMES_V03,
        )
        return (
            len(type_names) == 13
            and len(router_names) == 68
            and len(_G2C_TRANSITION_FUNCTION_NAMES_V03) == 6
            and len(_execution_mode_router.PUBLIC_G2C_FUNCTIONS_V01) == 74
            and len(direct_names) == len(set(direct_names)) == 87
            and all(
                getattr(_kernel_package, name, None)
                is getattr(_execution_mode_router, name, None)
                for name in (*type_names, *router_names)
            )
            and all(
                getattr(_kernel_package, name, None)
                is getattr(_transition_registry, name, None)
                for name in _G2C_TRANSITION_FUNCTION_NAMES_V03
            )
            and not set(direct_names).intersection(_kernel_package.__all__)
        )
    except Exception:
        return False


def _g2c_baseline_geometry_v01(report: object) -> dict[str, bool]:
    checks = {
        "two_domain_ten_case_report": False,
        "all_five_root_outcomes": False,
        "seventeen_step_order": False,
        "source_binding_and_derived_query": False,
        "one_abi_profile_and_stage_bundles": False,
        "one_transition_profile_and_root_lineage": False,
        "route_eligibility_and_direct_bypass": False,
        "package_facade_and_import_boundary": False,
        "negative_matrix_and_domain_invariance": False,
        "zero_operations": False,
    }
    try:
        valid = (
            type(report) is _g2c.ExecutionModeRouterG2CReportV01
            and _g2c.validate_execution_mode_router_g2_c_report_v01(report) == ()
        )
        if not valid:
            return checks
        cases = report.case_results
        checks["two_domain_ten_case_report"] = (
            report.report_version == "v0.1"
            and report.profile_id
            == "execution_mode_router_g2c_two_domain_proof_v01"
            and report.domain_order
            == (
                "TRAVEL_POLICY_INFORMATION",
                "WAREHOUSE_MAINTENANCE_INFORMATION",
            )
            and len(cases) == 10
            and report.case_order == tuple(item.case_id for item in cases)
        )
        checks["all_five_root_outcomes"] = {
            item.root_outcome for item in cases
        } == {"ACCEPT", "NARROW", "REJECT", "BLOCKED", "NEEDS_USER"}
        checks["seventeen_step_order"] = all(
            item.operation_steps == _g2c.OPERATION_STEPS for item in cases
        )
        checks["source_binding_and_derived_query"] = (
            all(
                item.selected_feasibility_row_id
                == item.rebuilt_selected_feasibility_row_id
                and item.request_id != item.transaction_id
                for item in cases
            )
            and all(
                cases[index].temporal_query_id is not None
                and cases[index].transaction_id
                == cases[index].temporal_query_id
                and cases[index].transaction_id.startswith("drsquery_v01:")
                for index in (1, 2, 3)
            )
        )
        checks["one_abi_profile_and_stage_bundles"] = all(
            item.proposal_artifact_id.startswith("emabi_proposal_v01:")
            and item.decision_artifact_id.startswith("emabi_decision_v01:")
            for item in cases
        )
        checks["one_transition_profile_and_root_lineage"] = all(
            item.pre_root_transition_id
            and item.pre_root_transition_reason
            == "g2c_transition_root_review_required"
            and item.post_root_transition_id
            and item.source_root_result_id
            and item.root_decision_id
            for item in cases
        )
        checks["route_eligibility_and_direct_bypass"] = all(
            (item.route_eligibility_artifact_id is not None)
            is (item.root_outcome in {"ACCEPT", "NARROW"})
            for item in cases
        )
        checks["package_facade_and_import_boundary"] = (
            _g2c_package_facade_passes_v01()
        )
        checks["negative_matrix_and_domain_invariance"] = (
            len({item.domain_id for item in cases}) == 2
            and report.domain_order
            == (
                "TRAVEL_POLICY_INFORMATION",
                "WAREHOUSE_MAINTENANCE_INFORMATION",
            )
        )
        zero_names = (
            "provider_calls",
            "model_calls",
            "gemini_calls",
            "network_calls",
            "connector_calls",
            "external_drs_calls",
            "action_commit_packets_created",
            "permissions_created",
            "receipts_created",
            "topologies_created",
            "drs_writes",
            "final_outputs_created",
            "real_world_effects",
        )
        checks["zero_operations"] = all(
            getattr(report, name) == 0 for name in zero_names
        ) and all(
            getattr(item, name) == 0 for item in cases for name in zero_names
        )
        return checks
    except Exception:
        return {key: False for key in checks}


_G2D_CHECK_CASE_NUMBERS_V04 = (
    ("policy_identity_and_staged_surface", (59, 67)),
    ("executable_templates_and_child_activation", (40, 48, 51, 66, 69)),
    ("queue_input_outcome_and_result_order", (44, 48, 49, 50, 65, 66, 71)),
    ("paired_budget_events_and_backpressure", (30, 53, 58, 61, 68)),
    ("resultproposal_unique_gt_kt_validation", (45, 54, 63, 72)),
    ("pre_root_four_artifact_abi_partitions", (56, 62, 72)),
    ("transition_profile_and_root_only_report", (55, 70)),
    ("causal_pointer_reason_and_root_outcome", (47, 57, 67)),
    ("two_domain_seventy_two_case_boundary", (1, 10, 42, 72)),
    ("zero_authority_and_operations", (1, 41, 72)),
)
_G2D_CHECK_CASE_IDS_V04 = {
    1: "g2d_case:travel:memory_informed:v02",
    10: "g2d_case:warehouse:full_fractal:v02",
    30: "g2d_case:negative:total_cell_overflow:v02",
    40: "g2d_case:required_child_hard_failure:v02",
    41: "g2d_case:negative:child_authority_claims:v02",
    42: "g2d_case:repeated_canonical_equality:v02",
    44: "g2d_case:negative:queue_predecessor_substitution:v02",
    45: "g2d_case:deterministic:post_vv_gt_injected_time:v02",
    47: "g2d_case:causal:blocked_and_ignored_dispositions:v02",
    48: "g2d_case:identity:child_result_partial_failure_postorder:v02",
    49: "g2d_case:identity:pre_result_validation_no_cycle:v02",
    50: "g2d_case:runtime:node_work_queue_cell_aggregation:v02",
    51: "g2d_case:runtime:five_mode_exact_template_rows:v02",
    53: "g2d_case:budget:allocation_predecessor_debit_matrix:v02",
    54: "g2d_case:validation:resultproposal_postvv_gt_outcome_matrix:v02",
    55: "g2d_case:transition:root_only_parent_return:v02",
    56: "g2d_case:abi:complete_field_partition_and_trace:v02",
    57: "g2d_case:causal:exact_pointer_reason_bundle:v02",
    58: "g2d_case:queue:backpressure_precedence:v02",
    59: "g2d_case:identity:policy_profile_separation:v02",
    61: "g2d_case:budget:cell_global_event_pairing:v02",
    62: "g2d_case:abi:pre_root_lifecycle_boundary:v02",
    63: "g2d_case:validation:context_unique_gt_report_ids:v02",
    65: "g2d_case:queue:instance_snapshot_round_and_blocked_reason:v02",
    66: "g2d_case:runtime:child_slot_input_node_outcome_order:v02",
    67: "g2d_case:validation:root_result_report_and_slice_surface:v02",
    68: "g2d_case:budget:typed_event_and_child_allocation_context:v02",
    69: "g2d_case:runtime:planned_child_activation_boundary:v02",
    70: "g2d_case:transition:prestate_decision_budget_queue_order:v02",
    71: "g2d_case:revise:observation_before_t07_and_budget:v02",
    72: "g2d_case:bundle:prebundle_validation_causal_final_assembly:v02",
}
_G2D_ZERO_COUNTER_FIELDS_V04 = (
    "provider_calls",
    "model_calls",
    "gemini_calls",
    "network_calls",
    "connector_calls",
    "external_drs_calls",
    "action_commit_packets_created",
    "permissions_created",
    "receipts_created",
    "final_outputs_created",
    "drs_writes",
    "authority_created_count",
    "real_world_effects_count",
)


def _g2d_case_and_details_v04(
    report: _g2d.FractalRuntimeG2DReportV02,
    case_number: int,
) -> tuple[_g2d.FractalRuntimeG2DCaseResultV02, dict[str, object]]:
    case = report.case_results[case_number - 1]
    if case.case_id != _G2D_CHECK_CASE_IDS_V04[case_number]:
        raise ValueError
    material = json.loads(case.evidence_material_json)
    if (
        type(material) is not dict
        or hashlib.sha256(canonical_json_bytes_v01(material)).hexdigest()
        != case.evidence_sha256
        or material.get("case_id") != case.case_id
        or material.get("evidence_refs") != list(case.evidence_refs)
        or type(material.get("proof")) is not dict
    ):
        raise ValueError
    proof = material["proof"]
    details = proof.get("details")
    if (
        type(details) is not dict
        or proof.get("details_sha256")
        != hashlib.sha256(canonical_json_bytes_v01(details)).hexdigest()
    ):
        raise ValueError
    return case, details


def _g2d_check_evidence_refs_v04(
    report: _g2d.FractalRuntimeG2DReportV02,
) -> tuple[str, ...]:
    rows = ["runtime:kernel_conformance:FractalRuntimeConformance"]
    for check_id, case_numbers in _G2D_CHECK_CASE_NUMBERS_V04:
        case_rows = []
        for case_number in case_numbers:
            case, _details = _g2d_case_and_details_v04(report, case_number)
            case_rows.append(
                {
                    "case_id": case.case_id,
                    "evidence_sha256": case.evidence_sha256,
                    "evidence_refs": list(case.evidence_refs),
                }
            )
        payload = canonical_json_bytes_v01(
            {"check_id": check_id, "case_evidence": case_rows}
        ).decode("ascii")
        rows.append(
            f"{conformance._G2D_CHECK_EVIDENCE_PREFIX_V05}{check_id}:{payload}"
        )
    return tuple(rows)


def _g2d_baseline_geometry_v04(report: object) -> dict[str, bool]:
    checks = {check_id: False for check_id, _ in _G2D_CHECK_CASE_NUMBERS_V04}
    try:
        if type(report) is not _g2d.FractalRuntimeG2DReportV02:
            return checks
        details = {
            number: _g2d_case_and_details_v04(report, number)[1]
            for number in _G2D_CHECK_CASE_IDS_V04
        }
        transition_profile = (
            _transition_registry.build_fractal_runtime_transition_registry_profile_v02()
        )
        checks["policy_identity_and_staged_surface"] = (
            details[59]["profile_count"] == 1
            and details[59]["policy_identity_count"] == 5
            and details[59]["source_binding_identity_count"] == 5
            and len(details[59]["policy_profile_separation"]) == 5
            and details[67]["staged_public_function_counts"]
            == [74, 81, 90, 110]
            and details[67]["module_public_function_count"] == 137
            and details[67]["public_return_bundle_type"]
            == "FractalRuntimeExecutionBundleV02"
            and details[67]["terminal_report_target"] == "COMPLETE_PROFILE"
        )
        checks["executable_templates_and_child_activation"] = (
            len(details[51]["five_mode_template_rows"]) == 5
            and all(
                row["node_count"] > 0 and row["assignment_count"] > 0
                for row in details[51]["five_mode_template_rows"]
            )
            and len(details[69]["planned_child_ids"]) == 2
            and len(details[69]["activated_child_ids"]) == 2
            and len(details[69]["activation_rows"]) == 2
            and details[40]["no_child_invocation_delta"]["created_count"] == 0
            and details[48]["no_child_result_ids"] == []
            and details[48]["no_child_partial_failure_ids"] == []
            and details[66]["child_invocation_count"] == 2
            and details[66]["denied_result_delta"]["created_count"] == 0
        )
        checks["queue_input_outcome_and_result_order"] = (
            details[44]["mutation_count"] == 10
            and len(details[48]["actual_child_result_rows"]) == 3
            and len(details[49]["validation_chain_rows"]) == 3
            and [row[0] for row in details[50]["aggregation_rows"]]
            == [0, 1, 2]
            and details[65]["rejected_copied_signal_count"] == 2
            and len(details[66]["child_slot_input_node_order"]) == 3
            and details[66]["child_results_before_root"] == [True, True]
            and details[71]["transition_rule_id"]
            == "g2d_t07_validating_to_revise"
        )
        checks["paired_budget_events_and_backpressure"] = (
            details[30]["tree_shape"] == [1, 4, 16]
            and details[30]["accepted_cell_count"] == 21
            and details[30]["planning_debit_count"] == 0
            and details[30]["allocation_debit_count"] == 0
            and details[30]["activate_debit_count"] == 0
            and details[30]["cell_create_debit_count"] == 21
            and details[53]["mutation_count"] == 8
            and details[58]["unique_state_per_round"] is True
            and details[58]["unchanged_t03_suppressed"] is True
            and details[58]["no_work_dropped"] is True
            and details[58]["exhausted_consumed_cell_count"] == 21
            and details[58]["exhausted_remaining_cell_count"] == 0
            and len(details[61]["mutation_rows"]) == 3
            and len(details[68]["four_child_structural_rows"]) == 4
        )
        checks["resultproposal_unique_gt_kt_validation"] = (
            details[45]["first_vv_report_id"]
            == details[45]["second_vv_report_id"]
            and details[45]["first_gt_report_id"]
            == details[45]["second_gt_report_id"]
            and details[45]["post_wall_clock_call_count"] == 0
            and details[45]["gt_wall_clock_call_count"] == 0
            and details[54]["outcome_count"] == 5
            and len(details[63]["context_unique_gt_rows"]) == 3
            and len(set(row[2] for row in details[63]["context_unique_gt_rows"]))
            == 3
            and len(details[72]["retained_result_report_rows"]) == 3
            and details[72]["complete_profile_status"] == "PASS"
        )
        checks["pre_root_four_artifact_abi_partitions"] = (
            details[56]["field_partitions"] == [32, 31, 32, 42]
            and len(details[56]["queue_parent_form_names"]) == 6
            and details[56]["trace_unique"] is True
            and details[62]["final_output_created"] == 0
            and details[62]["forbidden_root_lifecycles"]
            == ["ACCEPTED", "REJECTED", "ROOT_REVIEWED"]
            and details[72]["stage_d_a_artifact_count"]
            < details[72]["stage_d_b_artifact_count"]
            < details[72]["stage_d_c_artifact_count"]
        )
        checks["transition_profile_and_root_only_report"] = (
            _transition_registry.validate_fractal_runtime_transition_registry_profile_v02(
                transition_profile
            )
            == ()
            and len(transition_profile.rules) == 17
            and len(details[55]["root_final_budget_ids"]) == 1
            and len(details[55]["root_return_rule_ids"]) == 5
            and details[70]["root_return_decision_position"]
            == len(details[70]["transition_decision_ids"]) - 1
            and details[70]["post_hoc_mapping_count"] == 0
        )
        checks["causal_pointer_reason_and_root_outcome"] = (
            details[47]["ignored_causal_ref"]["disposition"]
            == "IGNORED_WITH_REASON"
            and details[47]["blocked_gate_causal_ref"]["disposition"]
            == "BLOCKED_BY_GATE"
            and details[47]["blocked_gate_causal_ref"]["decision_effect"]
            == "CELL_RESULT_OUTPUT"
            and details[57]["activation_causal_row_count"] == 2
            and details[57]["child_return_causal_row_count"] == 6
            and details[57]["corruption_causal_delta"]["created_count"] == 0
            and details[67]["root_owned_outcome"] is True
        )
        checks["two_domain_seventy_two_case_boundary"] = (
            report.domain_order
            == (
                "TRAVEL_POLICY_INFORMATION",
                "WAREHOUSE_MAINTENANCE_INFORMATION",
            )
            and len(report.case_order) == len(report.case_results) == 72
            and report.constructive_case_count == 36
            and report.negative_case_count == 36
            and report.domain_positive_case_count == 10
            and report.accepted_bundle_count == 10
            and details[42]["construction_call_count"] == 2
            and details[42]["repeated_value_equal"] is True
            and details[42]["repeated_id_equal"] is True
            and details[42]["repeated_bytes_equal"] is True
            and all(
                hashlib.sha256(item.evidence_material_json.encode("ascii")).hexdigest()
                == item.evidence_sha256
                for item in report.case_results
            )
        )
        checks["zero_authority_and_operations"] = (
            report.topology_created_count == 10
            and all(getattr(report, name) == 0 for name in _G2D_ZERO_COUNTER_FIELDS_V04)
            and all(
                getattr(item, name) == 0
                for item in report.case_results
                for name in _G2D_ZERO_COUNTER_FIELDS_V04
            )
            and details[41]["no_created_objects"]["created_count"] == 0
        )
        return checks
    except Exception:
        return {key: False for key in checks}


_G2E_ZERO_COUNTER_FIELDS_V07 = (
    "provider_calls",
    "model_calls",
    "network_calls",
    "connector_calls",
    "external_drs_calls",
    "action_commit_packets_created",
    "permissions_created",
    "receipts_created",
    "final_outputs_created",
    "drs_writes",
    "authority_created_count",
    "real_world_effects_count",
)
_G2E_TO_CONFORMANCE_DOMAIN_IDS_V07 = (
    ("TRAVEL_POLICY_INFORMATION", "airline"),
    ("WAREHOUSE_MAINTENANCE_INFORMATION", "supplier_water_filter"),
)
_G2E_ZERO_CASE_IDS_V07 = tuple(
    "g2e_case:negative:" + suffix + ":v01"
    for suffix in (
        "nonzero_provider_calls",
        "nonzero_model_calls",
        "nonzero_network_calls",
        "nonzero_connector_calls",
        "nonzero_external_drs_calls",
        "nonzero_drs_writes",
        "nonzero_action_packets",
        "nonzero_permissions",
        "nonzero_receipts",
        "nonzero_final_outputs",
        "nonzero_authority",
        "nonzero_real_world_effects",
    )
)
_G2E_PROBE_CASE_IDS_V07 = (
    None,
    "g2e_case:negative:cross_domain_substitution:v01",
    "g2e_case:negative:dependency_fingerprint_forgery:v01",
    "g2e_case:negative:missing_dependency_edge:v01",
    "g2e_case:negative:omitted_direct_dependent:v01",
    "g2e_case:negative:injected_unrelated_affected_artifact:v01",
    "g2e_case:negative:deletion_disguised_as_invalidation:v01",
    "g2e_case:negative:preserved_payload_mutation:v01",
    "g2e_case:negative:root_acceptance_outcome_forgery:v01",
    None,
)
_G2E_CHECK_SUPPORT_CASE_IDS_V07 = (
    (
        "g2e_case:travel:hold_expiry:v01",
        "g2e_case:warehouse:water_filter_stock:v01",
        "g2e_case:negative:unvalidated_delta_source:v01",
        "g2e_case:negative:missing_changed_binding_carrier:v01",
        "g2e_case:negative:source_binding_set_mismatch:v01",
    ),
    (
        "g2e_case:negative:dependency_fingerprint_forgery:v01",
        "g2e_case:negative:dependency_digest_role_collision:v01",
        "g2e_case:negative:source_history_substitution:v01",
    ),
    (
        "g2e_case:negative:missing_dependency_edge:v01",
        "g2e_case:negative:dependency_cycle:v01",
        "g2e_case:negative:graph_edge_reordering:v01",
        "g2e_case:negative:graph_node_bound_overflow:v01",
        "g2e_case:negative:graph_edge_bound_overflow:v01",
        "g2e_case:negative:graph_hop_bound_overflow:v01",
    ),
    (
        "g2e_case:negative:omitted_direct_dependent:v01",
        "g2e_case:negative:omitted_transitive_dependent:v01",
        "g2e_case:negative:injected_unrelated_affected_artifact:v01",
        "g2e_case:negative:affected_set_reordering:v01",
        "g2e_case:negative:affected_closure_proof_forgery:v01",
    ),
    (
        "g2e_case:negative:deletion_disguised_as_invalidation:v01",
        "g2e_case:negative:invalidation_predecessor_mismatch:v01",
        "g2e_case:negative:invalidation_supersession_mismatch:v01",
    ),
    (
        "g2e_case:travel:repeat_idempotent:v01",
        "g2e_case:warehouse:repeat_idempotent:v01",
        "g2e_case:negative:preserved_payload_mutation:v01",
        "g2e_case:negative:preserved_identity_mutation:v01",
        "g2e_case:negative:in_place_recomputation:v01",
    ),
    (
        "g2e_case:negative:packet_kept_executable_after_invalidation:v01",
        "g2e_case:negative:stale_reuse_certificate_retained_current:v01",
        "g2e_case:negative:route_reused_after_bound_source_change:v01",
        "g2e_case:negative:result_report_binding_mismatch:v01",
        "g2e_case:negative:post_vv_gt_binding_mismatch:v01",
    ),
    (
        "g2e_case:travel:repeat_idempotent:v01",
        "g2e_case:warehouse:repeat_idempotent:v01",
        "g2e_case:negative:repeated_delta_spin:v01",
        "g2e_case:negative:hidden_mutable_global_state:v01",
        "g2e_case:negative:unsupported_sequential_delta:v01",
    ),
    (
        "g2e_case:travel:policy_change:v01",
        "g2e_case:travel:unrelated_preference:v01",
        "g2e_case:warehouse:policy_change:v01",
        "g2e_case:warehouse:safe_sibling:v01",
        "g2e_case:negative:cross_domain_substitution:v01",
    ),
    _G2E_ZERO_CASE_IDS_V07,
)


def _valid_e5_sha256_v01(value: object) -> bool:
    return (
        type(value) is str
        and len(value) == 64
        and set(value) <= set("0123456789abcdef")
    )


def _g2e_case_passes_consumer_evidence_v01(case: object) -> bool:
    try:
        return (
            type(case) is _g2e.ContinuousDeltaRuntimeG2ECaseResultV01
            and case.expected_outcome == case.observed_outcome
            and case.expected_reason_codes == case.observed_reason_codes
            and case.final_status == conformance.STATUS_PASS
            and case.reason_codes == ()
            and type(case.evidence_material_json) is str
            and bool(case.evidence_material_json)
            and _valid_e5_sha256_v01(case.evidence_sha256)
            and type(case.evidence_refs) is tuple
            and bool(case.evidence_refs)
            and all(
                getattr(case, field) == 0
                for field in _G2E_ZERO_COUNTER_FIELDS_V07
            )
            and all(
                type(subcase)
                is _g2e.ContinuousDeltaRuntimeG2ESubcaseResultV01
                and subcase.expected_reason_codes
                == subcase.observed_reason_codes
                and subcase.final_status == conformance.STATUS_PASS
                and type(subcase.evidence_material_json) is str
                and bool(subcase.evidence_material_json)
                and _valid_e5_sha256_v01(subcase.evidence_sha256)
                and type(subcase.evidence_refs) is tuple
                and bool(subcase.evidence_refs)
                for subcase in case.subcase_results
            )
        )
    except Exception:
        return False


def _g2e_case_evidence_ref_v01(case: object) -> str:
    if not _g2e_case_passes_consumer_evidence_v01(case):
        raise ValueError("kernel_conformance_runtime_invalid")
    return f"case:{case.case_id}:sha256:{case.evidence_sha256}"


def _g2e_baseline_geometry_v07(report: object) -> dict[str, bool]:
    checks = dict.fromkeys(conformance._G2E_EXPECTED_CHECK_IDS_V07, False)
    try:
        validated = _g2e.validate_continuous_delta_runtime_g2_e_report_v01(
            report
        )
        cases = {item.case_id: item for item in validated.case_results}
        all_cases_bound = (
            tuple(cases) == validated.case_order
            and all(
                _g2e_case_passes_consumer_evidence_v01(item)
                for item in validated.case_results
            )
        )
        support_passes = tuple(
            all(
                case_id in cases
                and _g2e_case_passes_consumer_evidence_v01(cases[case_id])
                for case_id in case_ids
            )
            for case_ids in _G2E_CHECK_SUPPORT_CASE_IDS_V07
        )
        zero_boundary = (
            all(
                getattr(validated, field) == 0
                for field in _G2E_ZERO_COUNTER_FIELDS_V07
            )
            and all(
                getattr(item, field) == 0
                for item in validated.case_results
                for field in _G2E_ZERO_COUNTER_FIELDS_V07
            )
        )
        two_domain_boundary = (
            validated.domain_order
            == tuple(
                source_domain
                for source_domain, _ in _G2E_TO_CONFORMANCE_DOMAIN_IDS_V07
            )
            and conformance.DOMAIN_IDS
            == tuple(
                target_domain
                for _, target_domain in _G2E_TO_CONFORMANCE_DOMAIN_IDS_V07
            )
            and tuple(item.domain_id for item in validated.case_results[:5])
            == ("TRAVEL_POLICY_INFORMATION",) * 5
            and tuple(item.domain_id for item in validated.case_results[5:10])
            == ("WAREHOUSE_MAINTENANCE_INFORMATION",) * 5
        )
        for check_id, passed in zip(
            conformance._G2E_EXPECTED_CHECK_IDS_V07,
            support_passes,
            strict=True,
        ):
            checks[check_id] = (
                all_cases_bound
                and passed
                and _valid_e5_sha256_v01(validated.sealed_evidence_sha256)
            )
        checks["two_domain_selective_recomputation"] = (
            checks["two_domain_selective_recomputation"]
            and two_domain_boundary
        )
        checks["zero_authority_and_operations"] = (
            checks["zero_authority_and_operations"] and zero_boundary
        )
        return checks
    except Exception:
        return checks


def _g2e_check_evidence_refs_v07(report: object) -> tuple[str, ...]:
    validated = _g2e.validate_continuous_delta_runtime_g2_e_report_v01(report)
    cases = {item.case_id: item for item in validated.case_results}
    result = ["runtime:kernel_conformance:ContinuousDeltaRuntimeConformance"]
    for check_id, case_ids in zip(
        conformance._G2E_EXPECTED_CHECK_IDS_V07,
        _G2E_CHECK_SUPPORT_CASE_IDS_V07,
        strict=True,
    ):
        support = ",".join(
            _g2e_case_evidence_ref_v01(cases[case_id]) for case_id in case_ids
        )
        result.append(
            f"{conformance._G2E_CHECK_EVIDENCE_PREFIX_V07}{check_id}:"
            f"report:{validated.report_id}:seal:{validated.sealed_evidence_sha256}:"
            f"support:{support}"
        )
    return tuple(result)


def _collect_g2e_negative_observations_v01(
    report: object,
) -> tuple[tuple[object, ...], ...]:
    validated = _g2e.validate_continuous_delta_runtime_g2_e_report_v01(report)
    cases = {item.case_id: item for item in validated.case_results}
    target = conformance._G2E_REPORT_VALIDATOR_TARGET_V07
    evidence_base = (
        "demo/run_continuous_delta_runtime_g2_e_v01.py",
        f"report:{validated.report_id}",
        f"seal:{validated.sealed_evidence_sha256}",
    )
    observations: list[tuple[object, ...]] = []
    for index, (probe_id, expected) in enumerate(
        zip(
            conformance._G2E_NEGATIVE_PROBE_IDS_V07,
            conformance._G2E_EXPECTED_NEGATIVE_REASONS_V07,
            strict=True,
        )
    ):
        if index == 0:
            forged = replace(
                validated,
                report_id=_g2e.REPORT_ID_PREFIX + "f" * 64,
            )
            try:
                _g2e.validate_continuous_delta_runtime_g2_e_report_v01(forged)
                observed: tuple[str, ...] = ()
            except ValueError as exc:
                observed = (
                    str(exc),
                ) if len(exc.args) == 1 and type(exc.args[0]) is str else ()
            evidence_refs = (*evidence_base, f"forged_report:{forged.report_id}")
            blocked = observed == expected
        elif index == 9:
            zero_cases = tuple(cases[case_id] for case_id in _G2E_ZERO_CASE_IDS_V07)
            observed = tuple(
                dict.fromkeys(
                    reason
                    for case in zero_cases
                    for reason in case.observed_reason_codes
                )
            )
            evidence_refs = (
                *evidence_base,
                *(_g2e_case_evidence_ref_v01(case) for case in zero_cases),
            )
            blocked = (
                observed == expected
                and all(
                    _g2e_case_passes_consumer_evidence_v01(case)
                    for case in zero_cases
                )
                and all(
                    getattr(validated, field) == 0
                    for field in _G2E_ZERO_COUNTER_FIELDS_V07
                )
            )
        else:
            case_id = _G2E_PROBE_CASE_IDS_V07[index]
            case = cases[case_id]
            observed = case.observed_reason_codes
            evidence_refs = (*evidence_base, _g2e_case_evidence_ref_v01(case))
            blocked = (
                observed == expected
                and case.expected_reason_codes == expected
                and _g2e_case_passes_consumer_evidence_v01(case)
            )
        observations.append(
            (probe_id, target, expected, observed, blocked, evidence_refs)
        )
    return tuple(observations)


def _build_category_results(
    by_id: Mapping[str, Mapping[str, object]],
    domains: tuple[conformance.DomainConformanceResultV01, ...],
    negatives: tuple[conformance.NegativeConformanceResultV01, ...],
    action_packet_geometry_pass: bool,
    g2b_baseline: object,
    g2c_baseline: object,
    g2d_baseline: object,
    g2e_baseline: object,
) -> tuple[conformance.ConformanceCategoryResultV01, ...]:
    negative_by_id = {item.probe_id: item for item in negatives}
    domain_by_id = {item.domain_id: item for item in domains}
    safe = {key: _act_safe(value) for key, value in by_id.items()}
    g2b_geometry = _g2b_baseline_geometry_v01(g2b_baseline)
    g2b_act_pass = safe["drs_semantic_address_and_reuse_certificate"]
    g2c_geometry = _g2c_baseline_geometry_v01(g2c_baseline)
    g2c_act_pass = safe["execution_mode_router"]
    g2d_geometry = _g2d_baseline_geometry_v04(g2d_baseline)
    g2d_act_pass = safe["fractal_runtime"]
    g2e_geometry = _g2e_baseline_geometry_v07(g2e_baseline)
    g2e_act_pass = safe["continuous_delta_runtime"]
    rows = (
        (
            "DomainPackConformance",
            (
                ("airline_domain_pass", domain_by_id["airline"].status == conformance.STATUS_PASS),
                ("supplier_domain_pass", domain_by_id["supplier_water_filter"].status == conformance.STATUS_PASS),
                ("shared_integrity_contract", safe["generic_integrity_replay"] and safe["supplier_water_filter_portability"]),
                ("shared_replay_contract", safe["generic_integrity_replay"] and safe["supplier_water_filter_portability"]),
                (
                    "zero_kernel_law_changes",
                    safe["domain_neutral_kernel_abi"]
                    and safe["generic_multiroot"]
                    and safe["supplier_water_filter_portability"],
                ),
            ),
            ("limitation_g1e_kernel_conformance_scope",),
        ),
        (
            "RootAdapterConformance",
            (
                ("both_domains_preserve_root", all(item["root_authority_preserved"] is True for item in by_id.values())),
                ("root_decision_act_pass", safe["root_decision_kernel"]),
                (
                    "domain_authority_creation_zero",
                    negative_by_id["airline_adapter_effect_access_forbidden"].status
                    == conformance.STATUS_PASS
                    and negative_by_id["supplier_adapter_effect_counter_rejected"].status
                    == conformance.STATUS_PASS,
                ),
                ("no_superroot", safe["generic_multiroot"]),
            ),
            ("limitation_g1c1_in_memory_transition_and_root_decision_only",),
        ),
        (
            "CorridorAdapterConformance",
            (
                ("airline_corridor_pass", safe["airline_deterministic_transaction_runtime"]),
                ("supplier_mock_corridor_contained", safe["supplier_water_filter_portability"]),
                (
                    "corridor_law_unchanged",
                    safe["airline_deterministic_transaction_runtime"]
                    and safe["supplier_water_filter_portability"],
                ),
                ("no_real_connector_or_action", all(item["no_real_connector_or_action"] is True for item in by_id.values())),
            ),
            ("limitation_deterministic_local_scaffold",),
        ),
        (
            "SemanticProviderConformance",
            (
                ("trust_model_pass", safe["semantic_work_contract"]),
                ("semantic_work_pass", safe["semantic_work_contract"]),
                ("providers_advisory_only", safe["semantic_work_contract"]),
                ("external_calls_zero", all(safe.values())),
            ),
            ("limitation_g1b1_in_memory_contract_conformance_only",),
        ),
        (
            "ReplayCompatibility",
            (
                ("airline_replay_pass", "airline_generic_replay_pass" in domain_by_id["airline"].passed_check_ids),
                ("supplier_replay_pass", "supplier_generic_replay_pass" in domain_by_id["supplier_water_filter"].passed_check_ids),
                ("replay_rerun_counts_zero", safe["generic_integrity_replay"] and safe["supplier_water_filter_portability"]),
                (
                    "replay_creates_no_authority_or_effect",
                    safe["generic_integrity_replay"]
                    and safe["supplier_water_filter_portability"],
                ),
            ),
            ("limitation_g1a1_neutral_fixtures_only",),
        ),
        (
            "CryptoCompatibility",
            (
                ("both_anchored_checks_pass", "airline_generic_anchored_pass" in domain_by_id["airline"].passed_check_ids and "supplier_generic_anchored_pass" in domain_by_id["supplier_water_filter"].passed_check_ids),
                ("both_unanchored_checks_explicit", "airline_generic_unanchored_exact" in domain_by_id["airline"].passed_check_ids and "supplier_generic_unanchored_exact" in domain_by_id["supplier_water_filter"].passed_check_ids),
                (
                    "no_false_unanchored_pass",
                    "airline_generic_unanchored_exact"
                    in domain_by_id["airline"].passed_check_ids
                    and "supplier_generic_unanchored_exact"
                    in domain_by_id["supplier_water_filter"].passed_check_ids,
                ),
                ("no_production_signer_identity", safe["root_signer_isolation_conformance"]),
                ("airline_signature_false", "airline_signature_verified_remains_false" in domain_by_id["airline"].passed_check_ids),
                ("root_attestation_deferred", "airline_root_attestation_not_claimed" in domain_by_id["airline"].passed_check_ids),
            ),
            ("limitation_g1a2_conformance_only_signer_isolation",),
        ),
        (
            "SignerIsolationConformance",
            (
                ("own_root_signatures_verify", safe["root_signer_isolation_conformance"]),
                ("cross_root_misuse_blocked", negative_by_id["cross_root_signer_misuse"].status == conformance.STATUS_PASS),
                (
                    "no_pki_claim",
                    safe["root_signer_isolation_conformance"]
                    and negative_by_id["cross_root_signer_misuse"].status
                    == conformance.STATUS_PASS,
                ),
                (
                    "no_key_persistence",
                    safe["root_signer_isolation_conformance"]
                    and negative_by_id["cross_root_signer_misuse"].status
                    == conformance.STATUS_PASS,
                ),
            ),
            ("limitation_g1a2_conformance_only_signer_isolation",),
        ),
        (
            "TransitionRegistryConformance",
            (
                ("registry_act_pass", safe["transition_registry"]),
                ("unknown_transition_blocked", negative_by_id["unknown_transition"].status == conformance.STATUS_PASS),
                ("registry_immutable", safe["transition_registry"]),
                ("no_rule_injection", safe["transition_registry"]),
            ),
            ("limitation_g1c1_in_memory_transition_and_root_decision_only",),
        ),
        (
            "EffectFirewallConformance",
            (
                ("firewall_act_pass", safe["effect_firewall"]),
                ("widened_scope_blocked", negative_by_id["effect_firewall_scope_widening"].status == conformance.STATUS_PASS),
                (
                    "firewall_sole_effect_owner",
                    safe["effect_firewall"]
                    and negative_by_id["airline_adapter_effect_access_forbidden"].status
                    == conformance.STATUS_PASS
                    and negative_by_id["supplier_adapter_effect_counter_rejected"].status
                    == conformance.STATUS_PASS,
                ),
                ("domain_adapters_no_effect_access", negative_by_id["airline_adapter_effect_access_forbidden"].status == conformance.STATUS_PASS and negative_by_id["supplier_adapter_effect_counter_rejected"].status == conformance.STATUS_PASS),
                ("real_effects_zero", all(item["real_world_effects_count"] == 0 for item in by_id.values())),
            ),
            ("limitation_g1c2_in_memory_mock_effect_only",),
        ),
        (
            "MultiRootConformance",
            (
                ("three_root_pass", safe["generic_multiroot"]),
                ("four_root_pass", safe["generic_multiroot"]),
                ("mixed_visible", safe["generic_multiroot"] and safe["supplier_water_filter_portability"]),
                ("incomplete_visible", safe["generic_multiroot"]),
                ("duplicate_root_blocked", negative_by_id["multiroot_duplicate_root"].status == conformance.STATUS_PASS),
                ("reserved_root_blocked", negative_by_id["multiroot_reserved_root"].status == conformance.STATUS_PASS),
                ("authority_transfer_zero", safe["generic_multiroot"]),
                ("permission_transfer_zero", safe["generic_multiroot"]),
                (
                    "no_superroot",
                    negative_by_id["multiroot_reserved_root"].status
                    == conformance.STATUS_PASS,
                ),
            ),
            ("limitation_g1d2_generic_multiroot_conformance_only",),
        ),
        (
            "ActionPacketLifecycleConformance",
            (
                (
                    "canonical_identity",
                    safe["action_packet_lifecycle"]
                    and action_packet_geometry_pass
                    and negative_by_id["action_packet_identity_forgery"].status
                    == conformance.STATUS_PASS,
                ),
                (
                    "canonical_time",
                    action_packet_geometry_pass
                    and negative_by_id["action_packet_time_forgery"].status
                    == conformance.STATUS_PASS,
                ),
                (
                    "legal_transitions",
                    action_packet_geometry_pass
                    and negative_by_id["action_packet_illegal_transition"].status
                    == conformance.STATUS_PASS,
                ),
                (
                    "unknown_transition_block",
                    negative_by_id["action_packet_unknown_transition"].status
                    == conformance.STATUS_PASS,
                ),
                (
                    "root_only_authority_changes",
                    safe["action_packet_lifecycle"]
                    and negative_by_id[
                        "action_packet_root_authority_forgery"
                    ].status
                    == conformance.STATUS_PASS,
                ),
                (
                    "registry_non_authority",
                    negative_by_id[
                        "action_packet_registry_authority_forgery"
                    ].status
                    == conformance.STATUS_PASS,
                ),
                (
                    "corridor_freshness_enforcement",
                    negative_by_id[
                        "action_packet_corridor_freshness_forgery"
                    ].status
                    == conformance.STATUS_PASS,
                ),
                (
                    "receipt_non_authority",
                    negative_by_id[
                        "action_packet_receipt_authority_forgery"
                    ].status
                    == conformance.STATUS_PASS,
                ),
                (
                    "replay_non_execution",
                    negative_by_id[
                        "action_packet_replay_execution_forgery"
                    ].status
                    == conformance.STATUS_PASS,
                ),
                (
                    "cross_domain_invariance",
                    action_packet_geometry_pass
                    and negative_by_id[
                        "action_packet_cross_domain_substitution"
                    ].status
                    == conformance.STATUS_PASS,
                ),
            ),
            (
                "limitation_g2a6_deterministic_local_actionpacket_lifecycle_only",
            ),
        ),
        (
            "DRSSemanticAddressReuseCertificateConformance",
            tuple(
                (
                    check_id,
                    g2b_act_pass
                    and passed
                    and negative_by_id[probe_id].status
                    == conformance.STATUS_PASS,
                )
                for check_id, probe_id, passed in zip(
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
                    (
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
                    ),
                    tuple(g2b_geometry.values()),
                    strict=True,
                )
            ),
            (
                "limitation_g2b6_deterministic_local_drs_semantic_reuse_only",
            ),
        ),
        (
            "ExecutionModeRouterConformance",
            tuple(
                (
                    check_id,
                    g2c_act_pass
                    and passed
                    and (
                        check_id
                        != "negative_matrix_and_domain_invariance"
                        or all(
                            negative_by_id[probe_id].status
                            == conformance.STATUS_PASS
                            for probe_id in conformance._G2C_NEGATIVE_PROBE_IDS_V04
                        )
                    ),
                )
                for check_id, passed in g2c_geometry.items()
            ),
            (
                "limitation_g2c6_deterministic_two_domain_"
                "execution_mode_router_only",
            ),
        ),
        (
            "FractalRuntimeConformance",
            tuple(
                (
                    check_id,
                    g2d_act_pass
                    and passed
                    and (
                        check_id != "zero_authority_and_operations"
                        or all(
                            negative_by_id[probe_id].status
                            == conformance.STATUS_PASS
                            for probe_id in conformance._G2D_NEGATIVE_PROBE_IDS_V05
                        )
                    ),
                )
                for check_id, passed in g2d_geometry.items()
            ),
            ("limitation_g2d6_validated_d5_report_only",),
        ),
        (
            "ContinuousDeltaRuntimeConformance",
            tuple(
                (
                    check_id,
                    g2e_act_pass
                    and passed
                    and (
                        check_id != "zero_authority_and_operations"
                        or all(
                            negative_by_id[probe_id].status
                            == conformance.STATUS_PASS
                            for probe_id in conformance._G2E_NEGATIVE_PROBE_IDS_V07
                        )
                    ),
                )
                for check_id, passed in g2e_geometry.items()
            ),
            ("limitation_g2e6_validated_public_e5_report_only",),
        ),
    )
    return tuple(
        conformance.build_conformance_category_result_v01(
            category_id=category_id,
            check_results=checks,
            evidence_refs=(
                _g2d_check_evidence_refs_v04(g2d_baseline)
                if category_id == "FractalRuntimeConformance"
                else _g2e_check_evidence_refs_v07(g2e_baseline)
                if category_id == "ContinuousDeltaRuntimeConformance"
                else _category_evidence(category_id)
            ),
            limitation_refs=limitations,
        )
        for category_id, checks, limitations in rows
    )


def _category_evidence(category_id: str) -> tuple[str, ...]:
    return (f"runtime:kernel_conformance:{category_id}",)


def _collect_negative_results(
    by_id: Mapping[str, Mapping[str, object]],
    action_packet_report: object,
    g2b_observations: tuple[tuple[object, ...], ...],
    g2c_observations: tuple[tuple[object, ...], ...],
    g2d_observations: tuple[tuple[object, ...], ...],
    g2e_observations: tuple[tuple[object, ...], ...],
) -> tuple[conformance.NegativeConformanceResultV01, ...]:
    observations = (
        _probe_manifest_hash_mismatch(),
        _probe_replay_hash_mismatch(),
        _probe_cross_root_signer_misuse(),
        _probe_unknown_transition(),
        _probe_root_hard_failure(),
        _probe_effect_firewall_scope_widening(),
        _probe_multiroot_duplicate(),
        _probe_multiroot_reserved(),
        _probe_airline_effect_access(by_id["generic_integrity_replay"]),
        _probe_supplier_effect_counter(by_id["supplier_water_filter_portability"]),
        *_collect_action_packet_negative_observations_v01(action_packet_report),
        *g2b_observations,
        *g2c_observations,
        *g2d_observations,
        *g2e_observations,
    )
    return tuple(
        conformance.build_negative_conformance_result_v01(
            probe_id=probe_id,
            target_contract=target,
            expected_reason_codes=expected,
            observed_reason_codes=observed,
            blocked=blocked,
            evidence_refs=(evidence,) if type(evidence) is str else evidence,
            real_world_effects_count=0,
        )
        for probe_id, target, expected, observed, blocked, evidence in observations
    )


def _reidentify_drs_contract_v01(value: object) -> object:
    identity_field, _, prefix, _ = _drs_resolution._profile(
        type(value).__name__
    )
    provisional = replace(
        value,
        **{identity_field: prefix + "0" * 64},
    )
    return replace(
        provisional,
        **{
            identity_field: _drs_resolution._identity(
                provisional,
                type(value).__name__,
            )
        },
    )


def _reidentify_root_result_v01(value: object) -> object:
    provisional = replace(value, decision_id="0" * 64)
    return replace(
        provisional,
        decision_id=_root_decision._result_id(provisional),
    )


def _replace_g2b_domain_v01(
    report: object,
    *,
    domain_index: int,
    **changes: object,
) -> object:
    domains = list(report.domain_results)
    domains[domain_index] = replace(domains[domain_index], **changes)
    return _g2b._reidentify_report_v01(
        replace(report, domain_results=tuple(domains))
    )


def _g2b_negative_mutations_v01(
    report: object,
) -> tuple[tuple[str, object], ...]:
    if (
        type(report) is not _g2b._G2B5DeterministicReportV01
        or len(report.domain_results) != 2
    ):
        raise ValueError("kernel_conformance_runtime_invalid")
    domain = report.domain_results[0]
    other = report.domain_results[1]
    answer = domain.answer_report

    changed_address = replace(
        domain.semantic_address,
        semantic_address_id=f"drsaddr_v01:{'f' * 64}",
    )
    address_forgery = _replace_g2b_domain_v01(
        report,
        domain_index=0,
        semantic_address=changed_address,
    )

    selected_record = next(
        record
        for record in domain.source_records
        if record.meaning_record_id
        == next(
            candidate.meaning_record_id
            for candidate in answer.eligible_candidates
            if candidate.resolution_candidate_id
            == answer.selected_candidate_id
        )
    )
    changed_query = replace(
        answer.query,
        as_of=selected_record.time_envelope.valid_to,
    )
    time_forgery = _replace_g2b_domain_v01(
        report,
        domain_index=0,
        answer_report=replace(answer, query=changed_query),
    )

    selected_index = domain.source_records.index(selected_record)
    changed_pointer = replace(
        selected_record.memory_pointers[0],
        summary_read_permitted=False,
    )
    changed_record = replace(
        selected_record,
        memory_pointers=(
            changed_pointer,
            *selected_record.memory_pointers[1:],
        ),
    )
    changed_records = list(domain.source_records)
    changed_records[selected_index] = changed_record
    changed_records_tuple = tuple(changed_records)
    pointer_forgery = _replace_g2b_domain_v01(
        report,
        domain_index=0,
        source_records=changed_records_tuple,
        answer_report=replace(
            answer,
            source_records=changed_records_tuple,
        ),
        context_report=replace(
            domain.context_report,
            source_records=changed_records_tuple,
        ),
    )

    reversed_evaluations = _reidentify_drs_contract_v01(
        replace(
            answer,
            query_evaluations=tuple(reversed(answer.query_evaluations)),
        )
    )
    eligibility_forgery = _replace_g2b_domain_v01(
        report,
        domain_index=0,
        answer_report=reversed_evaluations,
    )

    selected_candidate = next(
        candidate
        for candidate in answer.eligible_candidates
        if candidate.resolution_candidate_id
        == answer.selected_candidate_id
    )
    ineligible_candidate = _reidentify_drs_contract_v01(
        replace(selected_candidate, eligible_for_ranking=False)
    )
    changed_candidates = tuple(
        ineligible_candidate
        if candidate is selected_candidate
        else candidate
        for candidate in answer.eligible_candidates
    )
    changed_ranked_ids = tuple(
        ineligible_candidate.resolution_candidate_id
        if candidate_id == selected_candidate.resolution_candidate_id
        else candidate_id
        for candidate_id in answer.ranked_candidate_ids
    )
    changed_candidate_report = _reidentify_drs_contract_v01(
        replace(
            answer,
            eligible_candidates=changed_candidates,
            ranked_candidate_ids=changed_ranked_ids,
            selected_candidate_id=ineligible_candidate.resolution_candidate_id,
        )
    )
    ranking_forgery = _replace_g2b_domain_v01(
        report,
        domain_index=0,
        answer_report=changed_candidate_report,
    )

    changed_budget = replace(
        domain.descent_proposed_budget,
        max_depth=4,
    )
    budget_forgery = _replace_g2b_domain_v01(
        report,
        domain_index=0,
        descent_proposed_budget=changed_budget,
    )

    changed_root_result = _reidentify_root_result_v01(
        replace(
            domain.shortcut_root_decision_result,
            permission_created=True,
        )
    )
    root_forgery = _replace_g2b_domain_v01(
        report,
        domain_index=0,
        shortcut_root_decision_result=changed_root_result,
    )

    changed_certificate_report = _reidentify_drs_contract_v01(
        replace(
            answer,
            reuse_certificate=other.answer_report.reuse_certificate,
        )
    )
    certificate_forgery = _replace_g2b_domain_v01(
        report,
        domain_index=0,
        answer_report=changed_certificate_report,
    )

    action_forgery = _replace_g2b_domain_v01(
        report,
        domain_index=0,
        positive_question="buy ticket",
    )
    cross_domain_forgery = _replace_g2b_domain_v01(
        report,
        domain_index=0,
        source_records=other.source_records,
        source_projections=other.source_projections,
    )

    return (
        ("drs_address_identity_forgery", address_forgery),
        ("drs_time_query_forgery", time_forgery),
        ("drs_pointer_policy_forgery", pointer_forgery),
        ("drs_eligibility_order_forgery", eligibility_forgery),
        (
            "drs_ranking_ineligible_selection_forgery",
            ranking_forgery,
        ),
        ("drs_memory_descent_budget_forgery", budget_forgery),
        ("drs_root_shortcut_authority_forgery", root_forgery),
        (
            "reuse_certificate_cross_binding_forgery",
            certificate_forgery,
        ),
        ("drs_action_reuse_forgery", action_forgery),
        ("drs_cross_domain_substitution", cross_domain_forgery),
    )


def _collect_g2b_negative_observations_v01(
    report: object,
) -> tuple[tuple[object, ...], ...]:
    if (
        type(report) is not _g2b._G2B5DeterministicReportV01
        or _g2b.validate_drs_semantic_address_reuse_certificate_g2_b_report_v01(
            report
        )
        != (True, ())
    ):
        raise ValueError("kernel_conformance_runtime_invalid")
    target = (
        "demo.run_drs_semantic_address_reuse_certificate_g2_b_v01."
        "validate_drs_semantic_address_reuse_certificate_g2_b_report_v01"
    )
    expected = ("g2b_report_fail_closed",)
    evidence = (
        "demo/run_drs_semantic_address_reuse_certificate_g2_b_v01.py"
    )
    observations: list[tuple[object, ...]] = []
    for probe_id, forged in _g2b_negative_mutations_v01(report):
        stable_identity = _g2b._reidentify_report_v01(forged) == forged
        try:
            valid, observed = (
                _g2b.validate_drs_semantic_address_reuse_certificate_g2_b_report_v01(
                    forged
                )
            )
        except Exception:
            valid, observed = False, ()
        blocked = (
            stable_identity
            and type(forged) is type(report)
            and valid is False
            and type(observed) is tuple
            and observed == expected
        )
        observations.append(
            (probe_id, target, expected, observed, blocked, evidence)
        )
    return tuple(observations)


def _build_g2b_negative_results_v01(
    observations: tuple[tuple[object, ...], ...],
) -> tuple[conformance.NegativeConformanceResultV01, ...]:
    return tuple(
        conformance.build_negative_conformance_result_v01(
            probe_id=probe_id,
            target_contract=target,
            expected_reason_codes=expected,
            observed_reason_codes=observed,
            blocked=blocked,
            evidence_refs=(evidence,),
            real_world_effects_count=0,
        )
        for probe_id, target, expected, observed, blocked, evidence in observations
    )


def _replace_g2c_case_v01(
    report: _g2c.ExecutionModeRouterG2CReportV01,
    *,
    case_index: int,
    **changes: object,
) -> _g2c.ExecutionModeRouterG2CReportV01:
    cases = list(report.case_results)
    cases[case_index] = replace(cases[case_index], **changes)
    return replace(report, case_results=tuple(cases))


def _g2c_negative_mutations_v01(
    report: object,
) -> tuple[tuple[str, object], ...]:
    if (
        type(report) is not _g2c.ExecutionModeRouterG2CReportV01
        or _g2c.validate_execution_mode_router_g2_c_report_v01(report) != ()
        or len(report.case_results) != 10
    ):
        raise ValueError("kernel_conformance_runtime_invalid")
    first = report.case_results[0]
    second_domain = report.case_results[5].domain_id
    return (
        (
            "execution_mode_report_identity_forgery",
            replace(report, report_id="emproof_v01:" + "f" * 64),
        ),
        (
            "execution_mode_case_order_forgery",
            replace(report, case_order=tuple(reversed(report.case_order))),
        ),
        (
            "execution_mode_selected_row_forgery",
            _replace_g2c_case_v01(
                report,
                case_index=0,
                selected_feasibility_row_id="emrow_v01:" + "f" * 64,
            ),
        ),
        (
            "execution_mode_root_outcome_forgery",
            _replace_g2c_case_v01(
                report,
                case_index=0,
                root_outcome="REJECT",
            ),
        ),
        (
            "execution_mode_transition_lineage_forgery",
            _replace_g2c_case_v01(
                report,
                case_index=0,
                post_root_transition_reason="g2c_transition_reject_recorded",
            ),
        ),
        (
            "execution_mode_route_eligibility_forgery",
            _replace_g2c_case_v01(
                report,
                case_index=0,
                route_eligibility_artifact_id=None,
            ),
        ),
        (
            "execution_mode_conflict_state_forgery",
            _replace_g2c_case_v01(
                report,
                case_index=0,
                root_review_conflict_set_ids=("conflict:g2c:forged:v01",),
            ),
        ),
        (
            "execution_mode_cross_domain_substitution",
            _replace_g2c_case_v01(
                report,
                case_index=0,
                domain_id=second_domain,
            ),
        ),
        (
            "execution_mode_operation_order_forgery",
            _replace_g2c_case_v01(
                report,
                case_index=0,
                operation_steps=tuple(reversed(first.operation_steps)),
            ),
        ),
        (
            "execution_mode_zero_operation_forgery",
            replace(report, provider_calls=1),
        ),
    )


def _collect_g2c_negative_observations_v01(
    report: object,
) -> tuple[tuple[object, ...], ...]:
    if (
        type(report) is not _g2c.ExecutionModeRouterG2CReportV01
        or _g2c.validate_execution_mode_router_g2_c_report_v01(report) != ()
    ):
        raise ValueError("kernel_conformance_runtime_invalid")
    target = (
        "demo.run_execution_mode_router_g2_c_v01."
        "validate_execution_mode_router_g2_c_report_v01"
    )
    evidence = "demo/run_execution_mode_router_g2_c_v01.py"
    observations: list[tuple[object, ...]] = []
    for (probe_id, forged), expected in zip(
        _g2c_negative_mutations_v01(report),
        conformance._G2C_EXPECTED_NEGATIVE_REASONS_V04,
        strict=True,
    ):
        try:
            observed = _g2c.validate_execution_mode_router_g2_c_report_v01(
                forged
            )
        except Exception:
            observed = ()
        blocked = (
            type(forged) is type(report)
            and type(observed) is tuple
            and observed == expected
        )
        observations.append(
            (probe_id, target, expected, observed, blocked, evidence)
        )
    return tuple(observations)


def _build_g2c_negative_results_v01(
    observations: tuple[tuple[object, ...], ...],
) -> tuple[conformance.NegativeConformanceResultV01, ...]:
    return tuple(
        conformance.build_negative_conformance_result_v01(
            probe_id=probe_id,
            target_contract=target,
            expected_reason_codes=expected,
            observed_reason_codes=observed,
            blocked=blocked,
            evidence_refs=(evidence,),
            real_world_effects_count=0,
        )
        for probe_id, target, expected, observed, blocked, evidence in observations
    )


_G2D_NEGATIVE_AXIS_CASE_IDS_V04 = (
    None,
    "g2d_case:negative:route_substitution:v02",
    "g2d_case:negative:direct_root_decision:v02",
    "g2d_case:identity:policy_profile_separation:v02",
    "g2d_case:negative:scope_budget_monotonic_matrix:v02",
    "g2d_case:negative:queue_predecessor_substitution:v02",
    "g2d_case:negative:fractal_capability_missing:v02",
    "g2d_case:no_progress_deadend:v02",
    "g2d_case:negative:child_authority_claims:v02",
    None,
)


def _g2d_report_identity_v04(
    report: _g2d.FractalRuntimeG2DReportV02,
) -> str:
    material = _g2d.fractal_runtime_g2_d_report_to_plain_data_v02(report)
    material.pop("report_id")
    return _g2d.REPORT_ID_PREFIX + domain_separated_sha256_hex_v01(
        domain=_g2d.REPORT_ID_DOMAIN,
        payload=canonical_json_bytes_v01(material),
    )


def _reseal_g2d_case_detail_v04(
    report: _g2d.FractalRuntimeG2DReportV02,
    *,
    case_id: str,
    detail_key: str,
    detail_value: object,
) -> _g2d.FractalRuntimeG2DReportV02:
    cases = list(report.case_results)
    index = report.case_order.index(case_id)
    case = cases[index]
    material = json.loads(case.evidence_material_json)
    proof = material["proof"]
    details = proof["details"]
    details[detail_key] = detail_value
    proof["details_sha256"] = hashlib.sha256(
        canonical_json_bytes_v01(details)
    ).hexdigest()
    evidence_bytes = canonical_json_bytes_v01(material)
    cases[index] = replace(
        case,
        evidence_material_json=evidence_bytes.decode("ascii"),
        evidence_sha256=hashlib.sha256(evidence_bytes).hexdigest(),
    )
    provisional = replace(report, case_results=tuple(cases))
    return replace(provisional, report_id=_g2d_report_identity_v04(provisional))


def _g2d_negative_mutations_v04(
    report: _g2d.FractalRuntimeG2DReportV02,
) -> tuple[tuple[str, _g2d.FractalRuntimeG2DReportV02], ...]:
    route_case = report.case_results[17]
    route_material = json.loads(route_case.evidence_material_json)
    route_details = route_material["proof"]["details"]
    route_baseline_sha = route_details["baseline_sha256"]
    accepted_attempted_sha = route_details["attempted_sha256"]
    if (
        type(route_baseline_sha) is not str
        or type(accepted_attempted_sha) is not str
        or re.fullmatch(r"[0-9a-f]{64}", route_baseline_sha) is None
        or re.fullmatch(r"[0-9a-f]{64}", accepted_attempted_sha) is None
        or route_baseline_sha == accepted_attempted_sha
    ):
        raise ValueError("kernel_conformance_runtime_invalid")
    zero_operation = replace(report, provider_calls=1)
    zero_operation = replace(
        zero_operation,
        report_id=_g2d_report_identity_v04(zero_operation),
    )
    return (
        (
            "fractal_runtime_report_identity_forgery",
            replace(report, report_id=_g2d.REPORT_ID_PREFIX + "f" * 64),
        ),
        (
            "fractal_runtime_route_eligibility_substitution",
            _reseal_g2d_case_detail_v04(
                report,
                case_id=_G2D_NEGATIVE_AXIS_CASE_IDS_V04[1],
                detail_key="attempted_sha256",
                detail_value=route_baseline_sha,
            ),
        ),
        (
            "fractal_runtime_direct_root_decision_bypass",
            _reseal_g2d_case_detail_v04(
                report,
                case_id=_G2D_NEGATIVE_AXIS_CASE_IDS_V04[2],
                detail_key="topology_created_delta",
                detail_value=1,
            ),
        ),
        (
            "fractal_runtime_mode_profile_forgery",
            _reseal_g2d_case_detail_v04(
                report,
                case_id=_G2D_NEGATIVE_AXIS_CASE_IDS_V04[3],
                detail_key="profile_count",
                detail_value=2,
            ),
        ),
        (
            "fractal_runtime_scope_budget_widening",
            _reseal_g2d_case_detail_v04(
                report,
                case_id=_G2D_NEGATIVE_AXIS_CASE_IDS_V04[4],
                detail_key="mutation_count",
                detail_value=11,
            ),
        ),
        (
            "fractal_runtime_queue_transition_forgery",
            _reseal_g2d_case_detail_v04(
                report,
                case_id=_G2D_NEGATIVE_AXIS_CASE_IDS_V04[5],
                detail_key="mutation_count",
                detail_value=9,
            ),
        ),
        (
            "fractal_runtime_recursive_capability_forgery",
            _reseal_g2d_case_detail_v04(
                report,
                case_id=_G2D_NEGATIVE_AXIS_CASE_IDS_V04[6],
                detail_key="mutated_path",
                detail_value="/runtime_policy/allowed_capability_ids",
            ),
        ),
        (
            "fractal_runtime_no_progress_forgery",
            _reseal_g2d_case_detail_v04(
                report,
                case_id=_G2D_NEGATIVE_AXIS_CASE_IDS_V04[7],
                detail_key="consecutive_non_positive_count",
                detail_value=1,
            ),
        ),
        (
            "fractal_runtime_child_authority_forgery",
            _reseal_g2d_case_detail_v04(
                report,
                case_id=_G2D_NEGATIVE_AXIS_CASE_IDS_V04[8],
                detail_key="mutation_count",
                detail_value=5,
            ),
        ),
        ("fractal_runtime_zero_operation_forgery", zero_operation),
    )


def _collect_g2d_negative_observations_v01(
    report: _g2d.FractalRuntimeG2DReportV02,
) -> tuple[tuple[object, ...], ...]:
    if (
        type(report) is not _g2d.FractalRuntimeG2DReportV02
        or len(report.case_results) != 72
        or report.final_status != conformance.STATUS_PASS
    ):
        raise ValueError("kernel_conformance_runtime_invalid")
    target = conformance._G2D_REPORT_VALIDATOR_TARGET_V02
    evidence_path = "demo/run_fractal_runtime_g2_d_v02.py"
    observations: list[tuple[object, ...]] = []
    for index, ((probe_id, forged), expected) in enumerate(
        zip(
            _g2d_negative_mutations_v04(report),
            conformance._G2D_EXPECTED_NEGATIVE_REASONS_V05,
            strict=True,
        )
    ):
        try:
            observed = _g2d.validate_fractal_runtime_g2_d_report_v02(forged)
        except Exception:
            observed = ()
        axis_case_id = _G2D_NEGATIVE_AXIS_CASE_IDS_V04[index]
        evidence_refs = (
            evidence_path,
            f"baseline_report:{report.report_id}",
            *(
                (f"axis_case:{axis_case_id}",)
                if axis_case_id is not None
                else ()
            ),
            f"forged_report:{forged.report_id}",
        )
        observations.append(
            (
                probe_id,
                target,
                expected,
                observed,
                type(observed) is tuple and observed == expected,
                evidence_refs,
            )
        )
    return tuple(observations)


def _build_g2d_negative_results_v01(
    observations: tuple[tuple[object, ...], ...],
) -> tuple[conformance.NegativeConformanceResultV01, ...]:
    return tuple(
        conformance.build_negative_conformance_result_v01(
            probe_id=probe_id,
            target_contract=target,
            expected_reason_codes=expected,
            observed_reason_codes=observed,
            blocked=blocked,
            evidence_refs=evidence,
            real_world_effects_count=0,
        )
        for probe_id, target, expected, observed, blocked, evidence in observations
    )


def _collect_action_packet_negative_observations_v01(
    report: object,
) -> tuple[tuple[object, ...], ...]:
    if (
        type(report)
        is not _action_packet_lifecycle.ActionCommitPacketLifecycleG2A5ReportV01
        or _action_packet_lifecycle.validate_action_commit_packet_lifecycle_g2_a_report_v01(
            report
        )
        != (True, ())
    ):
        raise ValueError("kernel_conformance_runtime_invalid")

    airline = report.airline
    supplier = report.supplier
    first_transition = airline.replay_report.recorded_transitions[0]
    identity_forgery = replace(
        report,
        airline=replace(airline, packet_id=f"acp_v02:{'f' * 64}"),
    )
    time_forgery = replace(
        report,
        airline=replace(
            airline,
            replay_report=replace(
                airline.replay_report,
                recorded_transitions=(
                    replace(
                        first_transition,
                        evaluation_time=first_transition.evaluation_time + 1,
                    ),
                    *airline.replay_report.recorded_transitions[1:],
                ),
            ),
        ),
    )
    illegal_transition = replace(
        report,
        airline=replace(
            airline,
            replay_report=replace(
                airline.replay_report,
                recorded_transitions=(
                    replace(
                        first_transition,
                        source_state="BLOCKED",
                        target_state="CREATED",
                    ),
                    *airline.replay_report.recorded_transitions[1:],
                ),
            ),
        ),
    )
    unknown_transition = replace(
        report,
        airline=replace(
            airline,
            replay_report=replace(
                airline.replay_report,
                recorded_transitions=(
                    replace(first_transition, transition_rule_id="g2a_t99_unknown"),
                    *airline.replay_report.recorded_transitions[1:],
                ),
            ),
        ),
    )
    root_authority_forgery = replace(
        report,
        airline=replace(airline, owning_local_root_id="root:g2a5:forged"),
    )
    registry_authority_forgery = replace(
        report,
        airline=replace(airline, registry_creates_authority=True),
    )
    corridor_freshness_forgery = replace(
        report,
        airline=replace(
            airline,
            present_inspection=replace(
                airline.present_inspection,
                present_eligibility_status="ELIGIBLE_FOR_BOUNDED_MOCK_ATTEMPT",
                present_executable=True,
                reason_codes=(),
            ),
        ),
    )
    receipt_authority_forgery = replace(
        report,
        airline=replace(airline, receipt_creations=1),
    )
    replay_execution_forgery = replace(
        report,
        airline=replace(
            airline,
            replay_report=replace(airline.replay_report, adapter_calls=1),
        ),
    )
    cross_domain_substitution = replace(
        report,
        airline=replace(
            airline,
            replay_report=supplier.replay_report,
            present_inspection=supplier.present_inspection,
        ),
    )
    mutations = (
        ("action_packet_identity_forgery", identity_forgery),
        ("action_packet_time_forgery", time_forgery),
        ("action_packet_illegal_transition", illegal_transition),
        ("action_packet_unknown_transition", unknown_transition),
        ("action_packet_root_authority_forgery", root_authority_forgery),
        (
            "action_packet_registry_authority_forgery",
            registry_authority_forgery,
        ),
        (
            "action_packet_corridor_freshness_forgery",
            corridor_freshness_forgery,
        ),
        ("action_packet_receipt_authority_forgery", receipt_authority_forgery),
        ("action_packet_replay_execution_forgery", replay_execution_forgery),
        (
            "action_packet_cross_domain_substitution",
            cross_domain_substitution,
        ),
    )
    target = (
        "demo.run_action_commit_packet_lifecycle_g2_a_v01."
        "validate_action_commit_packet_lifecycle_g2_a_report_v01"
    )
    expected = ("g2a5_report_fail_closed",)
    evidence = "demo/run_action_commit_packet_lifecycle_g2_a_v01.py"
    observations: list[tuple[object, ...]] = []
    for probe_id, forged in mutations:
        try:
            valid, observed = (
                _action_packet_lifecycle.validate_action_commit_packet_lifecycle_g2_a_report_v01(
                    forged
                )
            )
        except Exception:
            valid, observed = False, ()
        blocked = (
            valid is False
            and type(observed) is tuple
            and observed == expected
            and all(type(item) is str for item in observed)
        )
        observations.append(
            (probe_id, target, expected, observed, blocked, evidence)
        )
    return tuple(observations)


def _neutral_manifest_fixture() -> tuple[object, tuple[tuple[str, object], ...]]:
    profile = build_default_seal_profile_v01()
    payload = {"value": "neutral"}
    artifact = build_canonical_artifact_ref_v01(
        artifact_id="artifact:conformance:neutral:001",
        artifact_type="SemanticEvidence",
        schema_version="v1",
        transaction_id="transaction:conformance:neutral:001",
        owner_root_id="root:conformance:neutral",
        authority_class="NON_AUTHORITY",
        lifecycle_state="VALIDATED",
        payload=payload,
        profile=profile,
    )
    manifest = build_artifact_manifest_v01(
        transaction_id=artifact.transaction_id,
        profile=profile,
        artifacts=(artifact,),
        dependency_edges=(),
        root_ownership_bindings=(
            RootOwnershipBindingV01(artifact.artifact_id, artifact.owner_root_id),
        ),
        evidence_class_bindings=(
            EvidenceClassBindingV01(artifact.artifact_id, "VALIDATED_EVIDENCE"),
        ),
        authority_class_bindings=(
            AuthorityClassBindingV01(artifact.artifact_id, artifact.authority_class),
        ),
    )
    return manifest, ((artifact.artifact_id, payload),)


def _probe_manifest_hash_mismatch() -> tuple[object, ...]:
    manifest, rows = _neutral_manifest_fixture()
    verification = verify_artifact_manifest_v01(
        manifest=manifest,
        payload_rows=rows,
        expected_manifest_hash="0" * 64,
    )
    observed = tuple(verification.verification_errors)
    expected = ("expected_manifest_hash_mismatch",)
    return (
        "manifest_hash_mismatch",
        "hedgehog.kernel.integrity_replay_v01.verify_artifact_manifest_v01",
        expected,
        observed,
        verification.verification_status == INTEGRITY_BLOCKED and all(item in observed for item in expected),
        "hedgehog/kernel/integrity_replay_v01.py",
    )


def _probe_replay_hash_mismatch() -> tuple[object, ...]:
    manifest, rows = _neutral_manifest_fixture()
    replay = verify_artifact_replay_v01(
        manifest=manifest,
        payload_rows=rows,
        expected_manifest_hash="0" * 64,
    )
    observed = tuple(replay.replay_errors)
    expected = ("replay_manifest_verification_failed",)
    zero_reruns = all(
        getattr(replay, field_name) == 0
        for field_name in (
            "provider_call_count",
            "network_call_count",
            "semantic_rerun_count",
            "transaction_rerun_count",
            "corridor_rerun_count",
            "ledger_recollection_count",
            "crypto_recollection_count",
            "real_world_effects_count",
        )
    )
    return (
        "replay_hash_mismatch",
        "hedgehog.kernel.integrity_replay_v01.verify_artifact_replay_v01",
        expected,
        observed,
        replay.replay_status != conformance.STATUS_PASS and zero_reruns,
        "hedgehog/kernel/integrity_replay_v01.py",
    )


def _probe_cross_root_signer_misuse() -> tuple[object, ...]:
    first = generate_root_signer_capability_v01(root_id="root:signer:first")
    second = generate_root_signer_capability_v01(root_id="root:signer:second")
    key_set = build_trusted_root_key_set_v01(capabilities=(first, second))
    commitment = build_root_owned_commitment_v01(
        commitment_id="commitment:signer:misuse:001",
        transaction_id="transaction:signer:misuse:001",
        owner_root_id=second.root_id,
        commitment_scope="scope:signer:second",
        artifact_hash="1" * 64,
        manifest_hash="2" * 64,
        key_id=second.key_id,
    )
    observed: tuple[str, ...]
    try:
        sign_root_owned_commitment_v01(
            capability=first,
            trusted_key_set=key_set,
            commitment=commitment,
        )
    except ValueError as exc:
        observed = tuple(item for item in exc.args if type(item) is str)
    else:
        observed = ()
    expected = ("signer_root_mismatch",)
    return (
        "cross_root_signer_misuse",
        "hedgehog.kernel.root_signer_isolation_v01.sign_root_owned_commitment_v01",
        expected,
        observed,
        all(item in observed for item in expected),
        "hedgehog/kernel/root_signer_isolation_v01.py",
    )


def _probe_unknown_transition() -> tuple[object, ...]:
    registry = build_default_transition_registry_v01()
    decision = lookup_transition_v01(
        registry=registry,
        abi_major_version=1,
        source_artifact_type="ActorContribution",
        source_lifecycle_state="VALIDATED",
        actor_role="gt",
        attempted_effect="RETURN_TO_ROOT",
        target_artifact_type="RootDecision",
        satisfied_guards=(),
        root_commit_present=False,
    )
    observed = (decision.reason_code,)
    expected = ("unknown_transition",)
    blocked = (
        not validate_transition_registry_v01(registry)
        and not validate_transition_decision_v01(registry=registry, decision=decision)
        and decision.decision == DECISION_BLOCKED_FAIL_CLOSED
    )
    return (
        "unknown_transition",
        "hedgehog.kernel.transition_registry_v01.lookup_transition_v01",
        expected,
        observed,
        blocked,
        "hedgehog/kernel/transition_registry_v01.py",
    )


def _neutral_root_review_packet() -> object:
    request = build_semantic_work_request_v01(
        request_id="semantic_work:conformance:001",
        transaction_id="transaction:conformance:root:001",
        target_root_id="root:conformance:owner",
        runtime_topology_ref="topology:conformance:001",
        bounded_context_refs=("context:conformance:001",),
        permitted_actor_ids=("actor:conformance:deterministic",),
        permitted_contribution_modes=("DETERMINISTIC",),
        requested_subjects=("subject:conformance:001",),
        required_evidence_classes=("OBSERVATION",),
        forbidden_claims=("permission", "final_output", "effect"),
    )
    evidence = build_evidence_binding_v01(
        evidence_id="evidence:conformance:001",
        evidence_ref="evidence_ref:conformance:001",
        evidence_class="OBSERVATION",
        source_component_id="actor:conformance:deterministic",
        provenance_ref="provenance:conformance:001",
        evidence_state="PRESENT",
    )
    claim = build_normalized_claim_v01(
        claim_id="claim:conformance:001",
        subject="subject:conformance:001",
        predicate="eligible",
        object_or_value=True,
        time_envelope_ref="time:conformance:001",
        provenance_refs=("provenance:conformance:001",),
        evidence_refs=(evidence.evidence_id,),
        confidence_micros=1_000_000,
        source_role="deterministic_runtime",
        source_mode="DETERMINISTIC",
    )
    contribution = build_actor_contribution_v01(
        contribution_id="contribution:conformance:001",
        request_id=request.request_id,
        actor_id="actor:conformance:deterministic",
        actor_role="deterministic_runtime",
        contribution_mode="DETERMINISTIC",
        bsep_projection_ref="bsep:conformance:001",
        scope="scope:conformance:001",
        bounded_context_refs=("context:conformance:001",),
        claims=(claim,),
        evidence_bindings=(evidence,),
        constraint_bindings=(),
        uncertainty_bindings=(),
        requested_validators=("validator:conformance:001",),
        forbidden_claims_observed=(),
    )
    return build_root_review_packet_from_contributions_v01(
        request=request,
        contributions=(contribution,),
        trust_profiles=build_default_component_trust_profiles_v01(),
    )


def _root_input(*, hard_scope_passed: bool, permission_required: bool) -> tuple[object, object, object]:
    packet = _neutral_root_review_packet()
    candidate_id = packet.synthesis_proposal.normalized_claims[0].claim_id
    kernel = build_root_decision_kernel_v01()
    decision_input = build_root_decision_input_v01(
        transaction_id=packet.transaction_id,
        target_root_id=packet.target_root_id,
        root_review_packet=packet,
        post_vv_bundle={
            "bundle_id": "post_vv:conformance:001",
            "post_vv_passed": True,
            "validated_candidate_ids": [candidate_id],
            "rejected_candidate_ids": [],
            "required_evidence_refs": [],
            "provided_evidence_refs": [],
            "hard_failure_reasons": [],
        },
        gt_advisory={
            "advisory_id": "gt:conformance:001",
            "candidate_ids": [candidate_id],
            "selected_candidate_id": candidate_id,
            "score_micros_by_candidate": {candidate_id: 1_000_000},
            "source_artifact_type": "GTAdvisoryReport",
            "source_lifecycle_state": "VALIDATED",
            "actor_role": "gt",
            "attempted_effect": "CREATE_ROOT_DECISION",
            "target_artifact_type": "RootDecision",
            "advisory_only": True,
            "creates_final_output": False,
            "requests_effect": False,
        },
        policy_state={
            "policy_id": "policy:conformance:001",
            "identity_passed": True,
            "scope_passed": hard_scope_passed,
            "hard_policy_passed": True,
            "allow_accept": True,
            "conflict_policy": "DEFER",
            "no_candidate_policy": "NO_UPDATE",
        },
        permission_state={
            "permission_required": permission_required,
            "user_permission_present": permission_required,
            "permission_scope_valid": True,
            "permission_ref": (
                "permission:conformance:001" if permission_required else None
            ),
        },
        temporal_state={
            "temporal_valid": True,
            "expired": False,
            "not_before_satisfied": True,
            "time_envelope_ref": "time:conformance:001",
        },
        conflict_state={
            "material_unresolved_conflict": False,
            "conflict_set_ids": list(packet.conflict_set_ids),
        },
        prior_root_state={
            "prior_decision_id": None,
            "prior_decision": None,
            "prior_selected_candidate_id": None,
        },
    )
    result = decide_root_v01(kernel=kernel, decision_input=decision_input)
    return kernel, decision_input, result


def _probe_root_hard_failure() -> tuple[object, ...]:
    kernel, decision_input, result = _root_input(
        hard_scope_passed=False,
        permission_required=False,
    )
    repeated = decide_root_v01(kernel=kernel, decision_input=decision_input)
    observed = tuple(result.hard_failure_reasons)
    expected = ("hard_scope_violation",)
    blocked = (
        result.decision == ROOT_DECISION_BLOCKED_FAIL_CLOSED
        and result.decision != ROOT_DECISION_ACCEPT
        and result == repeated
        and not validate_root_decision_result_v01(
            kernel=kernel,
            decision_input=decision_input,
            result=result,
        )
    )
    return (
        "root_hard_failure_not_overridden",
        "hedgehog.kernel.root_decision_v01.validate_root_decision_result_v01",
        expected,
        observed,
        blocked,
        "hedgehog/kernel/root_decision_v01.py",
    )


def _probe_effect_firewall_scope_widening() -> tuple[object, ...]:
    kernel, decision_input, root_result = _root_input(
        hard_scope_passed=True,
        permission_required=True,
    )
    firewall = build_effect_firewall_v01(
        root_decision_kernel=kernel,
        decision_input=decision_input,
        root_decision_result=root_result,
        invocation_id="invocation:conformance:firewall:001",
        allowed_adapter_ids=("mock_adapter:conformance",),
        allowed_action_kinds=("mock_action:conformance",),
        root_scope_refs=("scope:conformance:allowed",),
        maximum_expires_at_tick=200,
    )
    request = build_effect_request_v01(
        root_decision_kernel=kernel,
        decision_input=decision_input,
        root_decision_result=root_result,
        request_kind="ExecutionRequest",
        adapter_id="mock_adapter:conformance",
        action_kind="mock_action:conformance",
        scope_refs=("scope:conformance:forbidden",),
        issued_at_tick=100,
        expires_at_tick=150,
        idempotency_key="idempotency:conformance:firewall:001",
    )
    decision = authorize_effect_request_v01(
        firewall=firewall,
        request=request,
        current_tick=110,
    )
    state = effect_firewall_to_plain_dict_v01(firewall)["state_counters"]
    observed = (decision.reason_code,)
    expected = ("scope_expansion_forbidden",)
    blocked = (
        not validate_effect_firewall_v01(firewall)
        and not validate_effect_request_v01(request)
        and not validate_effect_firewall_decision_v01(
            firewall=firewall,
            request=request,
            decision=decision,
        )
        and decision.decision == EFFECT_DECISION_BLOCKED_FAIL_CLOSED
        and decision.capability_issued is False
        and decision.capability_id is None
        and state["issued_capability_count"] == 0
        and state["mock_effect_execution_count"] == 0
    )
    return (
        "effect_firewall_scope_widening",
        "hedgehog.kernel.effect_firewall_v01.authorize_effect_request_v01",
        expected,
        observed,
        blocked,
        "hedgehog/kernel/effect_firewall_v01.py",
    )


def _neutral_multiroot_outcome() -> object:
    transaction_id = "transaction:conformance:multiroot:001"
    roots = ("root:conformance:first", "root:conformance:second")
    decisions = tuple(
        build_root_decision_envelope_v01(
            transaction_id=transaction_id,
            root_id=root_id,
            root_decision_id=f"decision:{root_id}",
            source_decision_ref=f"source:{root_id}",
            outcome_class="ACCEPTED",
            reason_code="accepted:conformance",
            selected_subject_id=f"subject:{root_id}",
            evidence_refs=(f"evidence:{root_id}",),
            cross_root_input_refs=(),
        )
        for root_id in roots
    )
    return build_transaction_outcome_envelope_v01(
        transaction_id=transaction_id,
        expected_root_ids=roots,
        root_decisions=decisions,
        cross_root_evidence_refs=(),
    )


def _probe_multiroot_duplicate() -> tuple[object, ...]:
    outcome = _neutral_multiroot_outcome()
    forged = replace(
        outcome,
        expected_root_ids=(
            outcome.expected_root_ids[0],
            outcome.expected_root_ids[0],
        ),
    )
    result = validate_multiroot_v01(forged)
    observed = tuple(result.errors)
    expected = ("multiroot_duplicate_root",)
    return (
        "multiroot_duplicate_root",
        "hedgehog.kernel.multiroot_v01.validate_multiroot_v01",
        expected,
        observed,
        result.final_status == MULTIROOT_FAIL_CLOSED
        and bool(result.duplicate_root_ids),
        "hedgehog/kernel/multiroot_v01.py",
    )


def _probe_multiroot_reserved() -> tuple[object, ...]:
    outcome = _neutral_multiroot_outcome()
    forged = replace(
        outcome,
        expected_root_ids=("root:super_root", outcome.expected_root_ids[1]),
    )
    result = validate_multiroot_v01(forged)
    observed = tuple(result.errors)
    expected = ("multiroot_super_root_forbidden",)
    return (
        "multiroot_reserved_root",
        "hedgehog.kernel.multiroot_v01.validate_multiroot_v01",
        expected,
        observed,
        result.final_status == MULTIROOT_FAIL_CLOSED and result.super_root_created,
        "hedgehog/kernel/multiroot_v01.py",
    )


def _probe_airline_effect_access(row: Mapping[str, object]) -> tuple[object, ...]:
    public_functions = tuple(
        name
        for name, value in vars(airline_adapter).items()
        if not name.startswith("_") and inspect.isfunction(value)
    )
    field_names = tuple(item.name for item in fields(airline_adapter.AirlineKernelAdapterResultV01))
    capability_exposed = hasattr(airline_adapter, "EffectCapabilityV01") or any(
        "capability" in name.lower() for name in (*public_functions, *field_names)
    )
    blocked = (
        _act_safe(row)
        and public_functions
        == (
            "build_airline_kernel_adapter_result_v01",
            "validate_airline_kernel_adapter_result_v01",
            "airline_kernel_adapter_result_to_plain_dict_v01",
        )
        and not capability_exposed
        and "real_world_effects_count" in field_names
    )
    observed = ("airline_adapter_effect_access_forbidden",) if blocked else ()
    return (
        "airline_adapter_effect_access_forbidden",
        "hedgehog.domains.airline.kernel_adapter_v01",
        ("airline_adapter_effect_access_forbidden",),
        observed,
        blocked,
        "hedgehog/domains/airline/kernel_adapter_v01.py",
    )


def _probe_supplier_effect_counter(row: Mapping[str, object]) -> tuple[object, ...]:
    blocked = _act_safe(row) and not hasattr(supplier_adapter, "EffectCapabilityV01")
    observed = (
        ("supplier_water_filter_effect_creation_forbidden",) if blocked else ()
    )
    return (
        "supplier_adapter_effect_counter_rejected",
        (
            "demo.run_living_gauntlet_v01:"
            "collect_supplier_water_filter_portability_gauntlet_act_v01"
        ),
        ("supplier_water_filter_effect_creation_forbidden",),
        observed,
        blocked,
        "demo/run_living_gauntlet_v01.py",
    )


if __name__ == "__main__":
    raise SystemExit(main())
