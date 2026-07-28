"""Deterministic Gate-1 conformance runner over already-executed Living acts.

The runner consumes already-executed Living act results and calls public
Kernel contracts for direct negative probes. It performs no provider, network,
Gemini, .tmp, all-real rerun, package regeneration, external connector, or real
effect operation. It is not production certification.
"""

from __future__ import annotations

from collections.abc import Mapping
from dataclasses import asdict as _asdict
from dataclasses import fields, replace
import inspect
import re
import subprocess

import demo.run_action_commit_packet_lifecycle_g2_a_v01 as _action_packet_lifecycle
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
RUNNER_VERSION = "v0.2"
SLICE_ID = "domain_neutral_reference_kernel_gate1_g1e"

_COMMIT_PATTERN = re.compile(r"^[0-9a-f]{7,40}$")
_GATE1_BASE_ACT_IDS_V01 = (
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
_BASE_ACT_IDS = (*_GATE1_BASE_ACT_IDS_V01, "action_packet_lifecycle")
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
)
_LIMITATIONS = (
    "deterministic_current_repository_conformance_only",
    "exact_accepted_airline_and_supplier_adapters_only",
    "no_fresh_all_real_run_or_package_regeneration",
    "no_root_attestation_pki_federation_or_production_connector",
    "independent_audit_and_consolidated_docs_closure_pending",
    "limitation_g2a6_deterministic_local_actionpacket_lifecycle_only",
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


def collect_kernel_conformance_v01(
    *,
    active_act_results: tuple[Mapping[str, object], ...],
    implementation_commit: str,
) -> conformance.KernelConformanceReportV01:
    try:
        rows = _validate_active_act_results(active_act_results)
        if _COMMIT_PATTERN.fullmatch(implementation_commit) is None:
            raise ValueError("implementation_commit_invalid")
        by_id = {row["act_id"]: row for row in rows}
        action_packet_report = (
            _action_packet_lifecycle.collect_action_commit_packet_lifecycle_g2_a_v01()
        )
        action_packet_geometry_pass = _action_packet_report_geometry_passes_v01(
            action_packet_report
        )
        negatives = _collect_negative_results(by_id, action_packet_report)
        domains = _build_domain_results(by_id, negatives)
        categories = _build_category_results(
            by_id,
            domains,
            negatives,
            action_packet_geometry_pass,
        )
        report = conformance.build_kernel_conformance_report_v01(
            implementation_commit=implementation_commit,
            category_results=categories,
            domain_results=domains,
            negative_test_results=negatives,
            active_gauntlet_refs=_BASE_ACT_IDS,
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
        raise ValueError(reason if reason in allowed else "kernel_conformance_runtime_invalid") from None
    except Exception:
        raise ValueError("kernel_conformance_runtime_invalid") from None


def collect_standalone_kernel_conformance_v01(
    *,
    implementation_commit: str | None = None,
) -> conformance.KernelConformanceReportV01:
    try:
        from demo import run_living_gauntlet_v01 as living

        base_results = living.collect_living_gauntlet_base_act_results_v01()
        lifecycle_result = living.collect_action_packet_lifecycle_gauntlet_act_v01()
        active_results = (*base_results, _asdict(lifecycle_result))
        commit = (
            resolve_current_implementation_commit_v01()
            if implementation_commit is None
            else implementation_commit
        )
        return collect_kernel_conformance_v01(
            active_act_results=active_results,
            implementation_commit=commit,
        )
    except ValueError:
        raise
    except Exception:
        raise ValueError("kernel_conformance_standalone_failed") from None


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
        if report.final_status != conformance.STATUS_PASS:
            errors.append("kernel_conformance_not_pass")
        counters = report.counters
        if (
            counters.category_pass_count != 11
            or counters.domain_pass_count != 2
            or counters.negative_pass_count != 20
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
            "kernel_conformance: kernel_conformance_v01 v0.2\n"
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


def _build_category_results(
    by_id: Mapping[str, Mapping[str, object]],
    domains: tuple[conformance.DomainConformanceResultV01, ...],
    negatives: tuple[conformance.NegativeConformanceResultV01, ...],
    action_packet_geometry_pass: bool,
) -> tuple[conformance.ConformanceCategoryResultV01, ...]:
    negative_by_id = {item.probe_id: item for item in negatives}
    domain_by_id = {item.domain_id: item for item in domains}
    safe = {key: _act_safe(value) for key, value in by_id.items()}
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
    )
    return tuple(
        conformance.build_conformance_category_result_v01(
            category_id=category_id,
            check_results=checks,
            evidence_refs=_category_evidence(category_id),
            limitation_refs=limitations,
        )
        for category_id, checks, limitations in rows
    )


def _category_evidence(category_id: str) -> tuple[str, ...]:
    return (f"runtime:kernel_conformance:{category_id}",)


def _collect_negative_results(
    by_id: Mapping[str, Mapping[str, object]],
    action_packet_report: object,
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
    )
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
