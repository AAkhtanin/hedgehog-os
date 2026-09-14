from __future__ import annotations

from collections.abc import Mapping, Sequence
from dataclasses import asdict, dataclass, replace
import copy
import hashlib
import json
from pathlib import Path
import pickle
from typing import Any

from jsonschema import Draft202012Validator

from demo import (
    run_action_commit_packet_lifecycle_g2_a_v01 as _action_packet_lifecycle
)
from demo import (
    run_drs_semantic_address_reuse_certificate_g2_b_v01 as _g2b
)
from demo import run_execution_mode_router_g2_c_v01 as _g2c
from demo import run_fractal_runtime_g2_d_v02 as _g2d
from demo import run_continuous_delta_runtime_g2_e_v01 as _g2e
from demo.run_tri_party_airline_ticket_purchase_mock_e2e_v01 import (
    collect_tri_party_airline_ticket_purchase_mock_e2e_v01,
)
from demo.run_full_wow_v1_2_product_trace import (
    collect_full_wow_v1_2_product_trace,
)
from demo.run_kernel_conformance_v01 import (
    _collect_kernel_conformance_with_validated_fractal_runtime_v01,
    collect_kernel_conformance_v01,
    resolve_current_implementation_commit_v01,
    validate_kernel_conformance_runtime_v01,
)
from hedgehog.domains.airline import (
    crypto_artifact_seal_collector_v01 as airline_crypto_collector,
)
from hedgehog.domains.airline import crypto_artifact_seal_v01 as airline_crypto
from hedgehog.domains.airline import kernel_adapter_v01 as airline_kernel_adapter
from hedgehog.domains.airline import sealed_trace_replay_v01 as airline_replay
from hedgehog.domains.airline import (
    transaction_artifact_ledger_v01 as airline_ledger,
)
from hedgehog.domains.supplier_water_filter import (
    kernel_adapter_v01 as supplier_water_filter_adapter,
)
from hedgehog.kernel import multiroot_v01 as multiroot
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
from hedgehog.kernel.effect_firewall_v01 import (
    EFFECT_DECISION_ALLOW_MOCK_EFFECT,
    EFFECT_DECISION_BLOCKED_FAIL_CLOSED,
    EffectCapabilityV01,
    authorize_effect_request_v01,
    build_effect_firewall_v01,
    build_effect_request_v01,
    effect_firewall_decision_to_plain_dict_v01,
    effect_firewall_to_plain_dict_v01,
    effect_request_to_plain_dict_v01,
    execute_mock_effect_v01,
    validate_effect_firewall_decision_v01,
    validate_effect_firewall_v01,
    validate_effect_receipt_v01,
    validate_effect_request_v01,
)
import hedgehog.kernel.effect_firewall_v01 as effect_firewall_module
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
from hedgehog.kernel.root_decision_v01 import (
    ROOT_DECISION_ACCEPT,
    ROOT_DECISION_BLOCKED_FAIL_CLOSED,
    ROOT_DECISION_DEFER,
    ROOT_DECISION_NEEDS_MORE_EVIDENCE,
    ROOT_DECISION_NEEDS_USER,
    ROOT_DECISION_NO_UPDATE,
    ROOT_DECISION_REJECT,
    build_root_decision_input_v01,
    build_root_decision_kernel_v01,
    decide_root_v01,
    root_decision_input_to_plain_dict_v01,
    root_decision_kernel_to_plain_dict_v01,
    root_decision_result_to_plain_dict_v01,
    validate_root_decision_kernel_v01,
    validate_root_decision_result_v01,
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
from hedgehog.kernel.transition_registry_v01 import (
    DECISION_ALLOW,
    DECISION_BLOCKED_FAIL_CLOSED,
    DECISION_NEEDS_MORE_EVIDENCE,
    DECISION_NEEDS_USER,
    DECISION_RETURN_TO_ROOT,
    TransitionRegistryV01,
    build_default_transition_registry_v01,
    lookup_transition_v01,
    transition_decision_to_plain_dict_v01,
    transition_registry_to_plain_dict_v01,
    validate_transition_decision_v01,
    validate_transition_registry_v01,
)
import hedgehog.kernel.transition_registry_v01 as transition_registry_module


RUNNER_ID = "living_gauntlet_v01"
RUNNER_VERSION = "v1.6"
_GATE1_RELEASE_RUNNER_VERSION_V10 = "v1.0"
_G2A_RUNNER_VERSION_V11 = "v1.1"
_G2B_RUNNER_VERSION_V12 = "v1.2"
_G2C_RUNNER_VERSION_V13 = "v1.3"
_RELEASE_INDEX_VERSION = "v0.1"

KERNEL_CONFORMANCE_PROFILE_V05_HISTORICAL = (
    "kernel_conformance_v0_5_historical"
)
KERNEL_CONFORMANCE_PROFILE_V06_HISTORICAL = (
    "kernel_conformance_v0_6_historical"
)
KERNEL_CONFORMANCE_PROFILE_V07_CURRENT = "kernel_conformance_v0_7_current"
DEFAULT_KERNEL_CONFORMANCE_PROFILE = KERNEL_CONFORMANCE_PROFILE_V07_CURRENT
HISTORICAL_KERNEL_CONFORMANCE_ACTIVE_REFS_V05 = (
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

STATUS_PASS = "PASS"
STATUS_FAIL_CLOSED = "FAIL_CLOSED"
STATUS_EVIDENCE_ONLY = "EVIDENCE_ONLY"
STATUS_PLANNED_NOT_ACTIVE = "PLANNED_NOT_ACTIVE"
STATUS_ACTIVE = "ACTIVE"
STATUS_REFERENCE_ONLY = "REFERENCE_ONLY"
STATUS_HISTORICAL_EVIDENCE_ONLY = "HISTORICAL_EVIDENCE_ONLY"

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
        "runner_version",
        "version",
        "current_kernel_conformance_profile",
        "kernel_conformance_profiles",
        "current_regression_claim_mapping",
    }
)
_SEAM_INDEX_FIELD_NAMES = frozenset(
    {
        "current_kernel_conformance_profile",
        "document_id",
        "historical_kernel_conformance_profile",
        "index_status",
        "seams",
        "version",
    }
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
_GATE1_CURRENT_ACTIVE_ACT_SOURCES_V15 = {
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
    "kernel_conformance_closure": (
        "demo.run_living_gauntlet_v01",
        "collect_kernel_conformance_closure_gauntlet_act_v01",
    ),
}
_GATE1_CURRENT_ACTIVE_ACT_IDS_V15 = tuple(
    _GATE1_CURRENT_ACTIVE_ACT_SOURCES_V15
)
_G2A_ACTIVE_ACT_SOURCES_V11 = {
    **_GATE1_CURRENT_ACTIVE_ACT_SOURCES_V15,
    "action_packet_lifecycle": (
        "demo.run_living_gauntlet_v01",
        "collect_action_packet_lifecycle_gauntlet_act_v01",
    ),
}
_G2A_ACTIVE_ACT_IDS_V11 = tuple(_G2A_ACTIVE_ACT_SOURCES_V11)
_G2B_ACTIVE_ACT_SOURCES_V12 = {
    **_G2A_ACTIVE_ACT_SOURCES_V11,
    "drs_semantic_address_and_reuse_certificate": (
        "demo.run_living_gauntlet_v01",
        (
            "collect_drs_semantic_address_and_reuse_certificate_"
            "gauntlet_act_v01"
        ),
    ),
}
_G2B_ACTIVE_ACT_IDS_V12 = tuple(_G2B_ACTIVE_ACT_SOURCES_V12)
_G2C_ACTIVE_ACT_SOURCES_V13 = {
    **_G2B_ACTIVE_ACT_SOURCES_V12,
    "execution_mode_router": (
        "demo.run_execution_mode_router_g2_c_v01",
        "collect_execution_mode_router_g2_c_v01",
    ),
}
_G2C_ACTIVE_ACT_IDS_V13 = tuple(_G2C_ACTIVE_ACT_SOURCES_V13)
_ACTIVE_ACT_SOURCES = {
    **_G2C_ACTIVE_ACT_SOURCES_V13,
    "fractal_runtime": (
        "demo.run_fractal_runtime_g2_d_v02",
        "collect_fractal_runtime_g2_d_v02",
    ),
    "continuous_delta_runtime": (
        "demo.run_continuous_delta_runtime_g2_e_v01",
        "collect_continuous_delta_runtime_g2_e_v01",
    ),
}
_ACTIVE_ACT_IDS = tuple(_ACTIVE_ACT_SOURCES)
HISTORICAL_KERNEL_CONFORMANCE_ACTIVE_REFS_V06 = (
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
CURRENT_KERNEL_CONFORMANCE_ACTIVE_REFS_V07 = (
    *HISTORICAL_KERNEL_CONFORMANCE_ACTIVE_REFS_V06,
    "continuous_delta_runtime",
)
CURRENT_REGRESSION_CLAIM_TO_ACTS_V06 = (
    (
        "root_sole_local_final_commit_authority",
        (
            "root_decision_kernel",
            "action_packet_lifecycle",
            "fractal_runtime",
        ),
    ),
    ("no_superroot_exists", ("generic_multiroot",)),
    (
        "bsep_semantic_membrane",
        ("execution_mode_router", "fractal_runtime"),
    ),
    (
        "runtime_execution_topology_runtime_owned",
        ("fractal_runtime",),
    ),
    (
        "provider_model_advisory_only",
        ("semantic_work_contract", "fractal_runtime"),
    ),
    (
        "actor_output_cannot_create_final_output",
        ("semantic_work_contract", "fractal_runtime"),
    ),
    (
        "resultproposal_postvv_terminal_gt_before_root",
        ("fractal_runtime",),
    ),
    (
        "drs_retrieval_reuse_no_authority",
        ("drs_semantic_address_and_reuse_certificate",),
    ),
    (
        "receipt_evidence_only",
        ("effect_firewall", "action_packet_lifecycle"),
    ),
    (
        "effect_capability_bounded_corridor_only",
        ("effect_firewall",),
    ),
    (
        "airline_supplier_same_authority_law",
        (
            "airline_deterministic_transaction_runtime",
            "supplier_water_filter_portability",
            "action_packet_lifecycle",
        ),
    ),
    (
        "real_world_effects_zero",
        HISTORICAL_KERNEL_CONFORMANCE_ACTIVE_REFS_V06,
    ),
)
CURRENT_REGRESSION_CLAIM_TO_ACTS_V07 = (
    (
        "root_sole_local_final_commit_authority",
        (
            "root_decision_kernel",
            "action_packet_lifecycle",
            "fractal_runtime",
            "continuous_delta_runtime",
        ),
    ),
    ("no_superroot_exists", ("generic_multiroot",)),
    (
        "bsep_semantic_membrane",
        (
            "execution_mode_router",
            "fractal_runtime",
            "continuous_delta_runtime",
        ),
    ),
    (
        "runtime_execution_topology_runtime_owned",
        ("fractal_runtime", "continuous_delta_runtime"),
    ),
    (
        "provider_model_advisory_only",
        (
            "semantic_work_contract",
            "fractal_runtime",
            "continuous_delta_runtime",
        ),
    ),
    (
        "actor_output_cannot_create_final_output",
        (
            "semantic_work_contract",
            "fractal_runtime",
            "continuous_delta_runtime",
        ),
    ),
    (
        "resultproposal_postvv_terminal_gt_before_root",
        ("fractal_runtime", "continuous_delta_runtime"),
    ),
    (
        "drs_retrieval_reuse_no_authority",
        (
            "drs_semantic_address_and_reuse_certificate",
            "continuous_delta_runtime",
        ),
    ),
    (
        "receipt_evidence_only",
        (
            "effect_firewall",
            "action_packet_lifecycle",
            "continuous_delta_runtime",
        ),
    ),
    (
        "effect_capability_bounded_corridor_only",
        ("effect_firewall", "continuous_delta_runtime"),
    ),
    (
        "airline_supplier_same_authority_law",
        (
            "airline_deterministic_transaction_runtime",
            "supplier_water_filter_portability",
            "action_packet_lifecycle",
            "continuous_delta_runtime",
        ),
    ),
    ("real_world_effects_zero", CURRENT_KERNEL_CONFORMANCE_ACTIVE_REFS_V07),
)
_EXECUTED_RUNTIME_ACT_IDS = (
    "airline_deterministic_transaction_runtime",
    "generic_integrity_replay",
    "transition_registry",
    "root_decision_kernel",
    "effect_firewall",
    "supplier_water_filter_portability",
    "continuous_delta_runtime",
)
_EXECUTED_CONFORMANCE_ACT_IDS = (
    "root_signer_isolation_conformance",
    "semantic_work_contract",
    "domain_neutral_kernel_abi",
    "causal_consumption",
    "generic_multiroot",
    "kernel_conformance_closure",
)
_EVIDENCE_ONLY_ACT_IDS = (
    "airline_all_real_frozen_reference",
    "all_layers_invariant_super_smoke",
)
_HISTORICAL_EVIDENCE_ACT_IDS = ("all_layers_invariant_super_smoke",)
_PLANNED_ACT_IDS: tuple[str, ...] = ()
_PLANNED_SEAM_IDS: tuple[str, ...] = ()
_CURRENT_SEAMS = {
    "deterministic_airline_reference_collector": _ACTIVE_ACT_SOURCES[
        "airline_deterministic_transaction_runtime"
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
    "generic_integrity_replay_adapter": (
        "hedgehog.domains.airline.kernel_adapter_v01",
        "build_airline_kernel_adapter_result_v01",
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
    "transition_registry": (
        "hedgehog.kernel.transition_registry_v01",
        "lookup_transition_v01",
    ),
    "root_decision_kernel": (
        "hedgehog.kernel.root_decision_v01",
        "decide_root_v01",
    ),
    "effect_firewall": (
        "hedgehog.kernel.effect_firewall_v01",
        "execute_mock_effect_v01",
    ),
    "supplier_water_filter_abi_adapter": (
        "hedgehog.domains.supplier_water_filter.kernel_adapter_v01",
        "build_supplier_water_filter_kernel_adapter_result_v01",
    ),
    "multiroot_envelope": (
        "hedgehog.kernel.multiroot_v01",
        "validate_multiroot_v01",
    ),
    "kernel_conformance_report": (
        "demo.run_kernel_conformance_v01",
        "collect_kernel_conformance_v01",
    ),
}
_HISTORICAL_SEAMS = {
    "all_layers_invariant_super_smoke_collector": (
        "demo.run_all_layers_applied_super_smoke",
        "collect_all_layers_applied_super_smoke",
    ),
}
_CURRENT_SEAM_STATUSES = {
    "deterministic_airline_reference_collector": STATUS_ACTIVE,
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
    "generic_integrity_replay_adapter": STATUS_ACTIVE,
    "root_signer_isolation_conformance": STATUS_ACTIVE,
    "kernel_trust_model_core": STATUS_ACTIVE,
    "semantic_work_contract_core": STATUS_ACTIVE,
    "kernel_abi_core": STATUS_ACTIVE,
    "causal_consumption_core": STATUS_ACTIVE,
    "transition_registry": STATUS_ACTIVE,
    "root_decision_kernel": STATUS_ACTIVE,
    "effect_firewall": STATUS_ACTIVE,
    "supplier_water_filter_abi_adapter": STATUS_ACTIVE,
    "multiroot_envelope": STATUS_ACTIVE,
    "kernel_conformance_report": STATUS_ACTIVE,
}
_ACTIVE_RECORD_EXPECTATIONS = {
    "generic_integrity_replay": (
        (
            "claim_generic_integrity_replay_execution",
            "claim_airline_kernel_adapter_execution",
        ),
        "tests/test_kernel_integrity_replay_v01.py",
    ),
    "transition_registry": (
        ("claim_transition_registry_runtime_execution",),
        "tests/test_transition_registry_v01.py",
    ),
    "root_decision_kernel": (
        ("claim_root_decision_kernel_runtime_execution",),
        "tests/test_root_decision_kernel_v01.py",
    ),
    "effect_firewall": (
        ("claim_effect_firewall_runtime_execution",),
        "tests/test_effect_firewall_v01.py",
    ),
    "generic_multiroot": (
        ("claim_generic_multiroot_execution",),
        "tests/test_multiroot_v01.py",
    ),
    "supplier_water_filter_portability": (
        ("claim_supplier_water_filter_portability_execution",),
        "tests/test_supplier_water_filter_kernel_adapter_v01.py",
    ),
    "kernel_conformance_closure": (
        ("claim_kernel_conformance_closure_execution",),
        "tests/test_kernel_conformance_v01_runner.py",
    ),
}
_ACTIVE_SEAM_EXPECTATIONS = {
    "generic_integrity_replay_adapter": {
        "authority_status": "NON_ROOT_FROZEN_DOMAIN_ADAPTER",
        "current_mode": "PURE_IN_MEMORY_FROZEN_AIRLINE_PROJECTION",
        "effect_access": "NONE",
        "gate1_target": "generic_integrity_replay",
        "seam_class": "DOMAIN_ADAPTER",
    },
    "transition_registry": {
        "authority_status": "NON_ROOT_IMMUTABLE_TRANSITION_POLICY",
        "current_mode": "PURE_IN_MEMORY_DETERMINISTIC_LOOKUP",
        "effect_access": "NONE",
        "gate1_target": "transition_registry",
        "seam_class": "KERNEL_CORE",
    },
    "root_decision_kernel": {
        "authority_status": "ROOT_DECISION_AUTHORITY",
        "current_mode": "PURE_IN_MEMORY_DETERMINISTIC_ROOT_DECISION",
        "effect_access": "NONE",
        "gate1_target": "root_decision_kernel",
        "seam_class": "KERNEL_ROOT_BOUNDARY",
    },
    "effect_firewall": {
        "authority_status": "ROOT_SCOPED_EXCLUSIVE_EFFECT_BOUNDARY",
        "current_mode": "PURE_IN_MEMORY_MOCK_ONLY_CAPABILITY_EXECUTION",
        "effect_access": "BOUNDED_EFFECT_HANDLE_OWNER",
        "gate1_target": "effect_firewall",
        "seam_class": "KERNEL_EFFECT_BOUNDARY",
    },
    "supplier_water_filter_abi_adapter": {
        "authority_status": "NON_ROOT_DOMAIN_ADAPTER",
        "current_mode": "PURE_IN_MEMORY_DETERMINISTIC_PRODUCT_TRACE_PROJECTION",
        "effect_access": "NONE",
        "gate1_target": "supplier_water_filter_portability",
        "seam_class": "DOMAIN_ADAPTER",
    },
    "multiroot_envelope": {
        "authority_status": "INDEPENDENT_ROOT_OUTCOME_PROTOCOL",
        "current_mode": "PURE_IN_MEMORY_SOVEREIGN_ROOT_GEOMETRY",
        "effect_access": "NONE",
        "gate1_target": "generic_multiroot",
        "seam_class": "KERNEL_ROOT_BOUNDARY",
    },
    "kernel_conformance_report": {
        "authority_status": "NON_AUTHORITY_CONFORMANCE_EVIDENCE",
        "current_mode": "DETERMINISTIC_MACHINE_READABLE_GATE1_CONFORMANCE",
        "effect_access": "NONE",
        "gate1_target": "kernel_conformance_closure",
        "seam_class": "RELEASE_CONFORMANCE",
    },
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
_G2C_COUNTER_FIELD_NAMES_V13 = frozenset(
    {
        "active_act_count",
        "active_act_fail_closed_count",
        "active_act_pass_count",
        "active_collector_execution_count",
        "airline_collector_execution_count",
        "evidence_only_entry_count",
        "evidence_only_executed_count",
        "generic_integrity_replay_execution_count",
        "planned_act_count",
        "planned_executed_count",
        "real_world_effects_count",
        "root_signer_isolation_execution_count",
        "semantic_work_contract_execution_count",
        "domain_neutral_kernel_abi_execution_count",
        "causal_consumption_execution_count",
        "transition_registry_execution_count",
        "root_decision_kernel_execution_count",
        "effect_firewall_execution_count",
        "generic_multiroot_execution_count",
        "supplier_water_filter_portability_execution_count",
        "kernel_conformance_closure_execution_count",
        "action_packet_lifecycle_execution_count",
        "drs_semantic_address_reuse_certificate_execution_count",
        "execution_mode_router_execution_count",
    }
)
_G2B_COUNTER_FIELD_NAMES_V12 = _G2C_COUNTER_FIELD_NAMES_V13 - {
    "execution_mode_router_execution_count",
}
_G2A_COUNTER_FIELD_NAMES_V11 = _G2B_COUNTER_FIELD_NAMES_V12 - {
    "drs_semantic_address_reuse_certificate_execution_count",
}
_GATE1_COUNTER_FIELD_NAMES_V10 = _G2A_COUNTER_FIELD_NAMES_V11 - {
    "action_packet_lifecycle_execution_count",
}
_COUNTER_FIELD_NAMES = frozenset(
    (
        *_G2C_COUNTER_FIELD_NAMES_V13,
        "fractal_runtime_execution_count",
        "continuous_delta_runtime_execution_count",
    )
)
_LIVING_VERSION_GEOMETRY = {
    RUNNER_VERSION: (
        _ACTIVE_ACT_IDS,
        _ACTIVE_ACT_SOURCES,
        _COUNTER_FIELD_NAMES,
    ),
}

_G2B_EXPECTED_OPERATION_COUNTERS_V01 = (
    ("domain_count", 2),
    ("positive_answer_shortcuts", 2),
    ("context_only_fallbacks", 2),
    ("action_negative_requests", 8),
    ("pure_read_passes", 4),
    ("initial_local_records_written", 4),
    ("immutable_successor_records_written", 2),
    ("root_decisions_created_in_fixture", 6),
    ("reuse_certificates_created_in_fixture", 2),
    ("provider_calls", 0),
    ("network_calls", 0),
    ("gemini_calls", 0),
    ("external_drs_calls", 0),
    ("connector_calls", 0),
    ("real_world_effects", 0),
    ("canonical_meaning_records_mutated", 0),
    ("final_outputs_created_by_drs", 0),
    ("final_outputs_created_by_certificate", 0),
    ("action_commit_packets_created", 0),
    ("receipts_created", 0),
    ("capabilities_created", 0),
    ("effect_handles_created", 0),
)
_G2B_EXPECTED_CLOSED_PROGRAMME_COUNTERS_V01 = (
    ("airline_programme_runs", 0),
    ("supplier_programme_runs", 0),
    ("package_runner_calls", 0),
    ("anchor_runner_calls", 0),
    ("replay_runner_calls", 0),
    ("living_gauntlet_calls", 0),
    ("kernel_conformance_calls", 0),
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


def _active_g1c1_absence_errors(
    active_ids: tuple[str, ...], manifest: Mapping[str, Any]
) -> tuple[str, ...]:
    texts = [
        _normalized_release_text(record.get("statement"))
        for key in ("limitations", "public_claims")
        for record in manifest.get(key, [])
        if isinstance(record, dict)
    ]
    texts.extend(
        _normalized_release_text(item)
        for item in manifest.get("non_claims", [])
        if isinstance(item, str)
    )
    errors: list[str] = []
    if "transition_registry" in active_ids and any(
        phrase in text
        for text in texts
        for phrase in (
            "transition registry remains unimplemented",
            "transition registry is unimplemented",
            "no transition registry exists",
            "not a transition system",
        )
    ):
        errors.append("completion_manifest_active_transition_described_unimplemented")
    if "root_decision_kernel" in active_ids and any(
        phrase in text
        for text in texts
        for phrase in (
            "root decision kernel remains unimplemented",
            "root decision kernel is unimplemented",
            "no root decision kernel exists",
            "not a root decision",
        )
    ):
        errors.append("completion_manifest_active_root_decision_described_unimplemented")
    if "effect_firewall" in active_ids and any(
        phrase in text
        for text in texts
        for phrase in (
            "effect firewall remains unimplemented",
            "effect firewall is unimplemented",
            "no effect handle exists",
            "no effect request exists",
            "not effect execution",
        )
    ):
        errors.append(
            "completion_manifest_active_effect_firewall_described_unimplemented"
        )
    return tuple(errors)


def _active_g1d1_absence_errors(
    active_ids: tuple[str, ...], manifest: Mapping[str, Any]
) -> tuple[str, ...]:
    claims = manifest.get("public_claims", [])
    airline_adapter_active = (
        "generic_integrity_replay" in active_ids
        and isinstance(claims, list)
        and any(
            isinstance(record, dict)
            and record.get("claim_id") == "claim_airline_kernel_adapter_execution"
            and record.get("claim_class") == "EXECUTED_RUNTIME"
            for record in claims
        )
    )
    if not airline_adapter_active:
        return ()
    texts = [
        _normalized_release_text(record.get("statement"))
        for key in ("limitations", "public_claims")
        for record in manifest.get(key, [])
        if isinstance(record, dict)
    ]
    texts.extend(
        _normalized_release_text(item)
        for item in manifest.get("non_claims", [])
        if isinstance(item, str)
    )
    if any(
        phrase in text
        for text in texts
        for phrase in (
            "airline adapter remains unimplemented",
            "airline adapter is unimplemented",
            "no airline adapter exists",
            "not an airline integrity adapter",
        )
    ):
        return ("completion_manifest_active_airline_adapter_described_unimplemented",)
    return ()


def _active_g1d2_absence_errors(
    active_ids: tuple[str, ...], manifest: Mapping[str, Any]
) -> tuple[str, ...]:
    texts = [
        _normalized_release_text(record.get("statement"))
        for key in ("limitations", "public_claims")
        for record in manifest.get(key, [])
        if isinstance(record, dict)
    ]
    texts.extend(
        _normalized_release_text(item)
        for item in manifest.get("non_claims", [])
        if isinstance(item, str)
    )
    errors: list[str] = []
    if "generic_multiroot" in active_ids and any(
        phrase in text
        for text in texts
        for phrase in (
            "generic multiroot remains unimplemented",
            "generic multiroot is unimplemented",
            "not generic multiroot",
            "no generic multiroot exists",
        )
    ):
        errors.append("completion_manifest_active_multiroot_described_unimplemented")
    if "supplier_water_filter_portability" in active_ids and any(
        phrase in text
        for text in texts
        for phrase in (
            "supplier portability remains unimplemented",
            "supplier / water filter portability remains unimplemented",
            "not supplier or water filter portability",
            "not a supplier integrity adapter",
        )
    ):
        errors.append("completion_manifest_active_supplier_adapter_described_unimplemented")
    return tuple(errors)


def _validate_completion_manifest_v01(manifest: Any) -> tuple[str, ...]:
    errors: list[str] = []
    if not isinstance(manifest, dict):
        return ("completion_manifest_not_object",)
    if frozenset(manifest) != _MANIFEST_FIELD_NAMES:
        errors.append("completion_manifest_field_surface_mismatch")
    for key, expected in (
        ("document_id", "living_release_completion_manifest_v01"),
        ("version", _RELEASE_INDEX_VERSION),
        ("runner_version", "v1.5"),
        ("manifest_status", "ACTIVE_GATE1_G1E"),
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
    if active_ids != _GATE1_CURRENT_ACTIVE_ACT_IDS_V15:
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
            expected_source = _GATE1_CURRENT_ACTIVE_ACT_SOURCES_V15.get(
                record.get("act_id")
            )
            if expected_source is not None and (
                record.get("source_module"), record.get("source_symbol")
            ) != expected_source:
                errors.append(f"active_act_source_mismatch:{record.get('act_id', '')}")
            if not _is_string_list(record.get("claim_ids")):
                errors.append(f"active_act_claim_ids_invalid:{record.get('act_id', '')}")
            if not isinstance(record.get("focused_test"), str):
                errors.append(f"active_act_focused_test_invalid:{record.get('act_id', '')}")
            expected_record = _ACTIVE_RECORD_EXPECTATIONS.get(record.get("act_id"))
            if expected_record is not None and (
                tuple(record.get("claim_ids", ())) != expected_record[0]
                or record.get("focused_test") != expected_record[1]
            ):
                errors.append(f"active_act_contract_mismatch:{record.get('act_id', '')}")
    if isinstance(evidence, list):
        for record in evidence:
            if not isinstance(record, dict):
                continue
            expected_status = (
                STATUS_HISTORICAL_EVIDENCE_ONLY
                if record.get("act_id") in _HISTORICAL_EVIDENCE_ACT_IDS
                else STATUS_EVIDENCE_ONLY
            )
            if record.get("status") != expected_status:
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
    errors.extend(_active_g1c1_absence_errors(active_ids, manifest))
    errors.extend(_active_g1d1_absence_errors(active_ids, manifest))
    errors.extend(_active_g1d2_absence_errors(active_ids, manifest))

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
        STATUS_EVIDENCE_ONLY: set(_EVIDENCE_ONLY_ACT_IDS)
        - set(_HISTORICAL_EVIDENCE_ACT_IDS),
        STATUS_HISTORICAL_EVIDENCE_ONLY: set(
            _HISTORICAL_EVIDENCE_ACT_IDS
        ),
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
        airline_claims = [
            claim
            for claim in claims
            if isinstance(claim, dict)
            and claim.get("claim_id") == "claim_airline_kernel_adapter_execution"
        ]
        expected_airline_claim = {
            "act_ids": ["generic_integrity_replay"],
            "claim_class": "EXECUTED_RUNTIME",
            "claim_id": "claim_airline_kernel_adapter_execution",
            "evidence_ref": "hedgehog/domains/airline/kernel_adapter_v01.py",
            "focused_test_ref": "tests/test_airline_kernel_adapter_v01.py",
            "limitation_ref": "limitation_g1d1_frozen_airline_projection_only",
            "runtime_ref": (
                "demo.run_living_gauntlet_v01:"
                "collect_generic_integrity_replay_gauntlet_act_v01"
            ),
        }
        if len(airline_claims) != 1 or any(
            airline_claims[0].get(key) != value
            for key, value in expected_airline_claim.items()
        ):
            errors.append("completion_manifest_airline_adapter_claim_mismatch")
        expected_g1d2_claims = {
            "claim_generic_multiroot_execution": {
                "act_ids": ["generic_multiroot"],
                "claim_class": "EXECUTED_CONFORMANCE",
                "evidence_ref": "hedgehog/kernel/multiroot_v01.py",
                "focused_test_ref": "tests/test_multiroot_v01.py",
                "limitation_ref": "limitation_g1d2_generic_multiroot_conformance_only",
                "runtime_ref": (
                    "demo.run_living_gauntlet_v01:"
                    "collect_generic_multiroot_gauntlet_act_v01"
                ),
            },
            "claim_supplier_water_filter_portability_execution": {
                "act_ids": ["supplier_water_filter_portability"],
                "claim_class": "EXECUTED_RUNTIME",
                "evidence_ref": (
                    "hedgehog/domains/supplier_water_filter/kernel_adapter_v01.py"
                ),
                "focused_test_ref": (
                    "tests/test_supplier_water_filter_kernel_adapter_v01.py"
                ),
                "limitation_ref": (
                    "limitation_g1d2_supplier_water_filter_projection_only"
                ),
                "runtime_ref": (
                    "demo.run_living_gauntlet_v01:"
                    "collect_supplier_water_filter_portability_gauntlet_act_v01"
                ),
            },
        }
        for expected_id, expected_claim in expected_g1d2_claims.items():
            matching = [
                claim for claim in claims if claim.get("claim_id") == expected_id
            ]
            if len(matching) != 1 or any(
                matching[0].get(key) != value
                for key, value in expected_claim.items()
            ):
                errors.append(f"completion_manifest_g1d2_claim_mismatch:{expected_id}")
        expected_g1e_claim = {
            "act_ids": ["kernel_conformance_closure"],
            "claim_class": "EXECUTED_CONFORMANCE",
            "evidence_ref": "hedgehog/kernel/conformance_v01.py",
            "focused_test_ref": "tests/test_kernel_conformance_v01_runner.py",
            "limitation_ref": "limitation_g1e_kernel_conformance_scope",
            "runtime_ref": (
                "demo.run_living_gauntlet_v01:"
                "collect_kernel_conformance_closure_gauntlet_act_v01"
            ),
        }
        matching_g1e = [
            claim
            for claim in claims
            if claim.get("claim_id") == "claim_kernel_conformance_closure_execution"
        ]
        if len(matching_g1e) != 1 or any(
            matching_g1e[0].get(key) != value
            for key, value in expected_g1e_claim.items()
        ):
            errors.append("completion_manifest_g1e_claim_mismatch")
        if any(
            claim.get("claim_id") == "claim_gate1_planned_not_active"
            for claim in claims
        ):
            errors.append("completion_manifest_stale_planned_claim")

    if not _is_string_list(manifest.get("non_claims")):
        errors.append("completion_manifest_non_claims_invalid")

    expected_claim_mapping = {
        claim_id: list(act_ids)
        for claim_id, act_ids in CURRENT_REGRESSION_CLAIM_TO_ACTS_V06
    }
    expected_profiles = {
        "historical_v0_5": {
            "profile_id": KERNEL_CONFORMANCE_PROFILE_V05_HISTORICAL,
            "profile_version": "v0.5",
            "profile_status": "HISTORICAL_EVIDENCE_ONLY",
            "default_current": False,
            "active_gauntlet_refs": list(
                HISTORICAL_KERNEL_CONFORMANCE_ACTIVE_REFS_V05
            ),
            "historical_act_id": "all_layers_invariant_super_smoke",
        },
        "current_v0_6": {
            "profile_id": "kernel_conformance_v0_6_current",
            "profile_version": "v0.6",
            "profile_status": "CURRENT_ACTIVE",
            "default_current": True,
            "active_gauntlet_refs": list(
                HISTORICAL_KERNEL_CONFORMANCE_ACTIVE_REFS_V06
            ),
            "historical_profile_ref": (
                KERNEL_CONFORMANCE_PROFILE_V05_HISTORICAL
            ),
            "historical_act_id_rebound": False,
        },
    }
    if (
        manifest.get("current_kernel_conformance_profile")
        != "kernel_conformance_v0_6_current"
    ):
        errors.append("completion_manifest_current_profile_mismatch")
    if manifest.get("kernel_conformance_profiles") != expected_profiles:
        errors.append("completion_manifest_profile_geometry_mismatch")
    if manifest.get("current_regression_claim_mapping") != expected_claim_mapping:
        errors.append("completion_manifest_claim_mapping_mismatch")
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
        ("index_status", "ACTIVE_GATE1_G1E"),
    ):
        if index.get(key) != expected:
            errors.append(f"integration_seam_index_value_mismatch:{key}")
    if (
        index.get("current_kernel_conformance_profile")
        != "kernel_conformance_v0_6_current"
    ):
        errors.append("integration_seam_current_profile_mismatch")
    if (
        index.get("historical_kernel_conformance_profile")
        != "kernel_conformance_v0_5_historical"
    ):
        errors.append("integration_seam_historical_profile_mismatch")
    seams = index.get("seams")
    seam_ids, id_errors = _record_ids(seams, "seam_id", "seam")
    errors.extend(id_errors)
    expected_seam_ids = (
        set(_CURRENT_SEAMS)
        | set(_HISTORICAL_SEAMS)
        | set(_PLANNED_SEAM_IDS)
    )
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
                STATUS_HISTORICAL_EVIDENCE_ONLY,
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
                    if seam_id == "generic_integrity_replay_adapter":
                        errors.append("integration_seam_airline_adapter_source_mismatch")
                expected_contract = _ACTIVE_SEAM_EXPECTATIONS.get(seam_id)
                if expected_contract is not None and any(
                    seam.get(key) != value
                    for key, value in expected_contract.items()
                ):
                    errors.append(f"current_seam_contract_mismatch:{seam_id}")
            elif seam_id in _PLANNED_SEAM_IDS:
                if status != STATUS_PLANNED_NOT_ACTIVE:
                    errors.append(f"planned_seam_status_invalid:{seam_id}")
                if seam.get("source_symbol") is not None:
                    errors.append(f"planned_seam_symbol_present:{seam_id}")
            elif seam_id in _HISTORICAL_SEAMS:
                if status != STATUS_HISTORICAL_EVIDENCE_ONLY:
                    errors.append(f"historical_seam_status_invalid:{seam_id}")
                if (
                    seam.get("source_module"),
                    seam.get("source_symbol"),
                ) != _HISTORICAL_SEAMS[seam_id]:
                    errors.append(f"historical_seam_source_mismatch:{seam_id}")
            if seam_id != "effect_firewall" and seam.get("effect_access") != "NONE":
                errors.append(f"seam_effect_access_forbidden:{seam_id}")
                errors.append("integration_seam_non_firewall_effect_access_forbidden")
                if seam_id == "generic_integrity_replay_adapter":
                    errors.append(
                        "integration_seam_domain_adapter_effect_access_forbidden"
                    )
                if seam_id == "supplier_water_filter_abi_adapter":
                    errors.append(
                        "integration_seam_domain_adapter_effect_access_forbidden"
                    )
            if seam_id == "effect_firewall" and (
                status != STATUS_ACTIVE
                or seam.get("effect_access") != "BOUNDED_EFFECT_HANDLE_OWNER"
            ):
                errors.append("integration_seam_effect_owner_identity_invalid")
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
        transition_seam = seam_by_id.get("transition_registry")
        if isinstance(transition_seam, dict) and transition_seam.get("status") == STATUS_ACTIVE:
            note = _normalized_release_text(transition_seam.get("notes"))
            if any(
                phrase in note
                for phrase in (
                    "not implemented",
                    "unimplemented",
                    "no transition registry",
                    "not a transition system",
                )
            ):
                errors.append("integration_seam_active_transition_described_absent")
        root_seam = seam_by_id.get("root_decision_kernel")
        if isinstance(root_seam, dict) and root_seam.get("status") == STATUS_ACTIVE:
            note = _normalized_release_text(root_seam.get("notes"))
            if any(
                phrase in note
                for phrase in (
                    "not implemented",
                    "unimplemented",
                    "no root decision kernel",
                    "not a root decision",
                )
            ):
                errors.append("integration_seam_active_root_decision_described_absent")
        effect_seam = seam_by_id.get("effect_firewall")
        if isinstance(effect_seam, dict) and effect_seam.get("status") == STATUS_ACTIVE:
            note = _normalized_release_text(effect_seam.get("notes"))
            if any(
                phrase in note
                for phrase in (
                    "not implemented",
                    "unimplemented",
                    "no effect handle exists",
                    "no effect request exists",
                    "not effect execution",
                )
            ):
                errors.append(
                    "integration_seam_active_effect_firewall_described_absent"
                )
        airline_adapter_seam = seam_by_id.get("generic_integrity_replay_adapter")
        if (
            isinstance(airline_adapter_seam, dict)
            and airline_adapter_seam.get("status") == STATUS_ACTIVE
        ):
            note = _normalized_release_text(airline_adapter_seam.get("notes"))
            if any(
                phrase in note
                for phrase in (
                    "not implemented",
                    "unimplemented",
                    "no airline adapter",
                    "airline adapter is absent",
                )
            ):
                errors.append("integration_seam_active_airline_adapter_described_absent")
        supplier_adapter_seam = seam_by_id.get("supplier_water_filter_abi_adapter")
        if (
            isinstance(supplier_adapter_seam, dict)
            and supplier_adapter_seam.get("status") == STATUS_ACTIVE
        ):
            note = _normalized_release_text(supplier_adapter_seam.get("notes"))
            if any(
                phrase in note
                for phrase in ("not implemented", "unimplemented", "adapter is absent")
            ):
                errors.append("integration_seam_active_supplier_adapter_described_absent")
            if supplier_adapter_seam.get("effect_access") != "NONE":
                errors.append("integration_seam_domain_adapter_effect_access_forbidden")
        active_effect_owners = [
            seam
            for seam in seams
            if isinstance(seam, dict)
            and seam.get("status") == STATUS_ACTIVE
            and seam.get("effect_access") != "NONE"
        ]
        if len(active_effect_owners) != 1:
            errors.append("integration_seam_effect_owner_count_invalid")
        elif (
            active_effect_owners[0].get("seam_id") != "effect_firewall"
            or active_effect_owners[0].get("effect_access")
            != "BOUNDED_EFFECT_HANDLE_OWNER"
        ):
            errors.append("integration_seam_effect_owner_identity_invalid")
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


def _build_frozen_airline_adapter_audit_v01(
    ledger_item: airline_ledger.AirlineTransactionArtifactLedgerV01,
) -> airline_crypto_collector.AirlineCryptoArtifactSealAcceptedLedgerAuditV01:
    values: dict[str, object] = {
        "audit_id": airline_crypto_collector.EXPECTED_LEDGER_AUDIT_ID,
        "audit_version": airline_crypto_collector.EXPECTED_LEDGER_AUDIT_VERSION,
        "final_status": airline_crypto_collector.STATUS_PASS,
        "required_source_files": airline_crypto.REQUIRED_SOURCE_FILE_REFS,
        "files_read_count": airline_replay.SOURCE_FILE_COUNT,
        "ledger_id": ledger_item.ledger_id,
        "transaction_id": ledger_item.transaction_id,
        "selected_offer_id": airline_kernel_adapter.SELECTED_OFFER_ID,
        "source_run_ref": ledger_item.source_run_ref,
        "source_causal_report_ref": ledger_item.source_causal_report_ref,
        "source_corridor_report_ref": ledger_item.source_corridor_report_ref,
        "actual_entry_count": airline_replay.LEDGER_ENTRY_COUNT,
        "actual_dependency_edge_count": airline_replay.DEPENDENCY_EDGE_COUNT,
        "actual_root_final_count": airline_replay.ROOT_FINAL_COUNT,
        "client_root_final_count": 1,
        "airline_root_final_count": 1,
        "bank_root_final_count": 1,
        **{
            field_name: True
            for field_name in (
                airline_crypto_collector.ACCEPTED_AUDIT_BOOLEAN_FIELDS
            )
        },
        "stored_validation_status": airline_crypto_collector.STATUS_PASS,
        "stored_validation_errors": (),
        **{
            field_name: 0
            for field_name in (
                airline_crypto_collector.ACCEPTED_AUDIT_ZERO_COUNTER_FIELDS
            )
        },
        "validation_errors": (),
    }
    return airline_crypto_collector.AirlineCryptoArtifactSealAcceptedLedgerAuditV01(
        **values,
    )


def _build_frozen_airline_kernel_adapter_fixture_v01(
) -> tuple[
    airline_replay.AirlineSealedTraceReplayInputV01,
    airline_replay.AirlineSealedTraceReplayReportV01,
    airline_kernel_adapter.AirlineKernelAdapterResultV01,
]:
    package_ref = "airline_kernel_adapter_living_fixture_v01"
    ledger_item = airline_ledger.build_airline_transaction_artifact_ledger_fixture_v01(
        offer_id=airline_kernel_adapter.SELECTED_OFFER_ID,
    )
    expected_identity = (
        airline_ledger.build_airline_transaction_artifact_ledger_fixture_expected_identity_v01(
            offer_id=airline_kernel_adapter.SELECTED_OFFER_ID,
        )
    )
    source_rows = tuple(
        (
            source_ref,
            (
                "airline-kernel-adapter-living:"
                f"{index}:{source_ref}"
            ).encode("utf-8"),
        )
        for index, source_ref in enumerate(airline_crypto.REQUIRED_SOURCE_FILE_REFS)
    )
    manifest_core = airline_crypto.build_airline_crypto_artifact_seal_manifest_core_v01(
        ledger_item,
        ordered_source_files=source_rows,
        source_package_ref=package_ref,
        source_audit_status=airline_crypto.STATUS_PASS,
        secret_scan_passed=True,
        expected_identity=expected_identity,
    )
    envelope = airline_crypto.build_airline_crypto_artifact_seal_envelope_v01(
        manifest_core
    )
    stored = airline_crypto.verify_airline_crypto_artifact_seal_v01(
        envelope,
        ledger_item=ledger_item,
        ordered_source_files_before=source_rows,
        ordered_source_files_after=source_rows,
        expected_source_package_ref=package_ref,
        source_audit_status=airline_crypto.STATUS_PASS,
        secret_scan_passed=True,
        expected_manifest_core_hash=None,
        expected_identity=expected_identity,
    )
    fresh = airline_crypto.verify_airline_crypto_artifact_seal_v01(
        envelope,
        ledger_item=ledger_item,
        ordered_source_files_before=source_rows,
        ordered_source_files_after=source_rows,
        expected_source_package_ref=package_ref,
        source_audit_status=airline_crypto.STATUS_PASS,
        secret_scan_passed=True,
        expected_manifest_core_hash=envelope.manifest_core_hash,
        expected_identity=expected_identity,
    )
    replay_input = airline_replay.build_airline_sealed_trace_replay_input_v01(
        source_package_ref=package_ref,
        accepted_ledger_audit=_build_frozen_airline_adapter_audit_v01(ledger_item),
        ledger_item=ledger_item,
        envelope=envelope,
        stored_verification_report=stored,
        fresh_anchored_verification_report=fresh,
        expected_manifest_core_hash=envelope.manifest_core_hash,
        ordered_source_files=source_rows,
    )
    replay_report = airline_replay.verify_airline_sealed_trace_replay_v01(
        replay_input,
        critical_package_bytes_unchanged=True,
        post_replay_snapshot_provider_call_count=1,
    )
    adapter_result = (
        airline_kernel_adapter.build_airline_kernel_adapter_result_v01(
            replay_input=replay_input,
            replay_report=replay_report,
        )
    )
    return replay_input, replay_report, adapter_result


def _validate_frozen_airline_kernel_adapter_fixture_v01() -> None:
    replay_input, replay_report, adapter_result = (
        _build_frozen_airline_kernel_adapter_fixture_v01()
    )
    source_snapshot = (
        replay_input.source_package_ref,
        replay_input.expected_manifest_core_hash,
        replay_input.ordered_source_files,
        airline_replay.airline_sealed_trace_replay_report_to_plain_dict_v01(
            replay_report
        ),
    )
    if (
        airline_replay.validate_airline_sealed_trace_replay_input_v01(
            replay_input
        ).validation_status
        != STATUS_PASS
        or airline_replay.validate_airline_sealed_trace_replay_report_v01(
            replay_report
        ).validation_status
        != STATUS_PASS
        or airline_kernel_adapter.validate_airline_kernel_adapter_result_v01(
            replay_input=replay_input,
            replay_report=replay_report,
            result=adapter_result,
        )
        != ()
    ):
        raise ValueError("airline_kernel_adapter_validation_failed")
    projection = airline_kernel_adapter.airline_kernel_adapter_result_to_plain_dict_v01(
        adapter_result
    )
    canonical_json_bytes_v01(projection)
    if (
        len(adapter_result.kernel_artifacts) != 19
        or adapter_result.kernel_manifest.artifact_count != 19
        or adapter_result.kernel_manifest.dependency_edge_count != 29
        or len(adapter_result.causal_consumption_refs) != 29
        or adapter_result.kernel_unanchored_verification.verification_status
        != KERNEL_STATUS_UNANCHORED
        or adapter_result.kernel_anchored_verification.verification_status
        != STATUS_PASS
        or adapter_result.kernel_replay.replay_status != STATUS_PASS
        or any(
            value != 0
            for value in (
                adapter_result.provider_call_count,
                adapter_result.network_call_count,
                adapter_result.gemini_call_count,
                adapter_result.real_world_effects_count,
            )
        )
    ):
        raise ValueError("airline_kernel_adapter_geometry_failed")
    if (
        projection
        != airline_kernel_adapter.airline_kernel_adapter_result_to_plain_dict_v01(
            adapter_result
        )
        or source_snapshot
        != (
            replay_input.source_package_ref,
            replay_input.expected_manifest_core_hash,
            replay_input.ordered_source_files,
            airline_replay.airline_sealed_trace_replay_report_to_plain_dict_v01(
                replay_report
            ),
        )
    ):
        raise ValueError("airline_kernel_adapter_nondeterministic")


def collect_generic_integrity_replay_gauntlet_act_v01(
) -> LivingGauntletActResultV01:
    act_id = "generic_integrity_replay"
    source_module, source_symbol = _ACTIVE_ACT_SOURCES[act_id]
    try:
        records = _collect_generic_integrity_replay_fixture_records_v01()
        if len(records) != 2:
            raise ValueError("generic_fixture_count_invalid")
        _validate_frozen_airline_kernel_adapter_fixture_v01()
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


def _collect_transition_registry_fixture_metrics_v01() -> dict[str, Any]:
    first = build_default_transition_registry_v01()
    second = build_default_transition_registry_v01()
    if validate_transition_registry_v01(first) or validate_transition_registry_v01(second):
        raise ValueError("transition_registry_invalid")
    first_projection = transition_registry_to_plain_dict_v01(first)
    if first_projection != transition_registry_to_plain_dict_v01(second):
        raise ValueError("transition_registry_nondeterministic")
    if first.registry_id != second.registry_id:
        raise ValueError("transition_registry_id_nondeterministic")

    canonical_decisions = []
    for rule in first.rules:
        decision = lookup_transition_v01(
            registry=first,
            abi_major_version=rule.abi_major_version,
            source_artifact_type=rule.source_artifact_type,
            source_lifecycle_state=rule.source_lifecycle_state,
            actor_role=rule.actor_role,
            attempted_effect=rule.attempted_effect,
            target_artifact_type=rule.target_artifact_type,
            satisfied_guards=rule.required_guards,
            root_commit_present=True,
        )
        repeated = lookup_transition_v01(
            registry=first,
            abi_major_version=rule.abi_major_version,
            source_artifact_type=rule.source_artifact_type,
            source_lifecycle_state=rule.source_lifecycle_state,
            actor_role=rule.actor_role,
            attempted_effect=rule.attempted_effect,
            target_artifact_type=rule.target_artifact_type,
            satisfied_guards=rule.required_guards,
            root_commit_present=True,
        )
        if (
            validate_transition_decision_v01(registry=first, decision=decision)
            or transition_decision_to_plain_dict_v01(decision)
            != transition_decision_to_plain_dict_v01(repeated)
            or decision.decision_id != repeated.decision_id
        ):
            raise ValueError("transition_decision_nondeterministic")
        canonical_decisions.append(decision)

    def lookup(rule_id: str, *, remove_guard: str | None = None, commit: bool = True):
        rule = next(item for item in first.rules if item.rule_id == rule_id)
        guards = tuple(
            guard for guard in rule.required_guards if guard != remove_guard
        )
        return lookup_transition_v01(
            registry=first,
            abi_major_version=rule.abi_major_version,
            source_artifact_type=rule.source_artifact_type,
            source_lifecycle_state=rule.source_lifecycle_state,
            actor_role=rule.actor_role,
            attempted_effect=rule.attempted_effect,
            target_artifact_type=rule.target_artifact_type,
            satisfied_guards=guards,
            root_commit_present=commit,
        )

    missing_user = lookup(
        "root_decision_to_execution_request",
        remove_guard="user_permission_present",
    )
    missing_evidence = lookup(
        "actor_contribution_to_validated_evidence",
        remove_guard="required_evidence_present",
    )
    missing_generic = lookup(
        "result_proposal_to_post_vv_report",
        remove_guard="hard_predicates_evaluated",
    )
    missing_commit = lookup(
        "root_accepted_route_to_runtime_topology",
        commit=False,
    )
    unknown_transition = lookup_transition_v01(
        registry=first,
        abi_major_version=1,
        source_artifact_type="ActorContribution",
        source_lifecycle_state="VALIDATED",
        actor_role="gt",
        attempted_effect="RETURN_TO_ROOT",
        target_artifact_type="RootDecision",
        satisfied_guards=(),
        root_commit_present=False,
    )
    unknown_major = lookup_transition_v01(
        registry=first,
        abi_major_version=2,
        source_artifact_type="ActorContribution",
        source_lifecycle_state="VALIDATED",
        actor_role="post_vv",
        attempted_effect="CREATE_TARGET_ARTIFACT",
        target_artifact_type="ValidatedEvidence",
        satisfied_guards=(),
        root_commit_present=False,
    )
    extra_rule = replace(first.rules[0], rule_id="extra_rule_forbidden")
    extra_registry = replace(first, rules=first.rules + (extra_rule,))
    if not validate_transition_registry_v01(extra_registry):
        raise ValueError("transition_registry_mutation_accepted")
    if any(
        hasattr(transition_registry_module, name)
        for name in ("register_rule", "add_rule", "remove_rule", "update_rule")
    ):
        raise ValueError("transition_dynamic_registration_present")

    expected_special = (
        (missing_user, DECISION_NEEDS_USER, "explicit_user_permission_required"),
        (missing_evidence, DECISION_NEEDS_MORE_EVIDENCE, "required_evidence_missing"),
        (missing_generic, DECISION_BLOCKED_FAIL_CLOSED, "required_guard_missing"),
        (missing_commit, DECISION_RETURN_TO_ROOT, "root_commit_required"),
        (unknown_transition, DECISION_BLOCKED_FAIL_CLOSED, "unknown_transition"),
        (unknown_major, DECISION_BLOCKED_FAIL_CLOSED, "unknown_abi_major"),
    )
    if any(
        (decision.decision, decision.reason_code) != (expected, reason)
        for decision, expected, reason in expected_special
    ):
        raise ValueError("transition_special_lookup_invalid")
    if first_projection != transition_registry_to_plain_dict_v01(first):
        raise ValueError("transition_registry_mutated")

    return {
        "registry_id": first.registry_id,
        "rule_count": len(first.rules),
        "allow_rule_count": sum(rule.decision == DECISION_ALLOW for rule in first.rules),
        "return_to_root_rule_count": sum(rule.decision == DECISION_RETURN_TO_ROOT for rule in first.rules),
        "blocked_rule_count": sum(rule.decision == DECISION_BLOCKED_FAIL_CLOSED for rule in first.rules),
        "canonical_lookup_count": len(canonical_decisions),
        "needs_user_proof_count": int(missing_user.decision == DECISION_NEEDS_USER),
        "needs_more_evidence_proof_count": int(missing_evidence.decision == DECISION_NEEDS_MORE_EVIDENCE),
        "unknown_transition_blocked_count": int(unknown_transition.decision == DECISION_BLOCKED_FAIL_CLOSED),
        "unknown_major_blocked_count": int(unknown_major.decision == DECISION_BLOCKED_FAIL_CLOSED),
        "registry_mutation_rejected_count": 1,
        "provider_call_count": 0,
        "network_call_count": 0,
        "gemini_call_count": 0,
        "real_world_effects_count": 0,
    }


def collect_transition_registry_gauntlet_act_v01(
) -> LivingGauntletActResultV01:
    act_id = "transition_registry"
    source_module, source_symbol = _ACTIVE_ACT_SOURCES[act_id]
    try:
        metrics = _collect_transition_registry_fixture_metrics_v01()
        if (
            metrics["rule_count"],
            metrics["allow_rule_count"],
            metrics["return_to_root_rule_count"],
            metrics["blocked_rule_count"],
        ) != (18, 8, 4, 6):
            raise ValueError("transition_registry_geometry_invalid")
        return LivingGauntletActResultV01(
            act_id=act_id, errors=(), executed=True,
            no_real_connector_or_action=True, real_world_effects_count=0,
            root_authority_preserved=True, runtime_status=STATUS_PASS,
            source_module=source_module, source_symbol=source_symbol,
            state=STATUS_PASS,
        )
    except Exception:
        return LivingGauntletActResultV01(
            act_id=act_id, errors=("transition_registry_runtime_failed",),
            executed=True, no_real_connector_or_action=False,
            real_world_effects_count=-1, root_authority_preserved=False,
            runtime_status=STATUS_FAIL_CLOSED, source_module=source_module,
            source_symbol=source_symbol, state=STATUS_FAIL_CLOSED,
        )


def _root_decision_base_states_v01(packet: Any) -> dict[str, Any]:
    candidate_ids = [
        claim.claim_id for claim in packet.synthesis_proposal.normalized_claims
    ]
    required_evidence = list(packet.missing_evidence_refs)
    return {
        "post_vv_bundle": {
            "bundle_id": "post_vv:fixture:root_decision:001",
            "post_vv_passed": True,
            "validated_candidate_ids": candidate_ids,
            "rejected_candidate_ids": [],
            "required_evidence_refs": required_evidence,
            "provided_evidence_refs": required_evidence,
            "hard_failure_reasons": [],
        },
        "gt_advisory": {
            "advisory_id": "gt:fixture:root_decision:001",
            "candidate_ids": candidate_ids,
            "selected_candidate_id": candidate_ids[0],
            "score_micros_by_candidate": {
                candidate_id: 500_000 for candidate_id in candidate_ids
            },
            "source_artifact_type": "GTAdvisoryReport",
            "source_lifecycle_state": "VALIDATED",
            "actor_role": "gt",
            "attempted_effect": "CREATE_ROOT_DECISION",
            "target_artifact_type": "RootDecision",
            "advisory_only": True,
            "creates_final_output": False,
            "requests_effect": False,
        },
        "policy_state": {
            "policy_id": "policy:fixture:root_decision:001",
            "identity_passed": True,
            "scope_passed": True,
            "hard_policy_passed": True,
            "allow_accept": True,
            "conflict_policy": "DEFER",
            "no_candidate_policy": "NO_UPDATE",
        },
        "permission_state": {
            "permission_required": False,
            "user_permission_present": False,
            "permission_scope_valid": True,
            "permission_ref": None,
        },
        "temporal_state": {
            "temporal_valid": True,
            "expired": False,
            "not_before_satisfied": True,
            "time_envelope_ref": "time_envelope:fixture:root_decision:001",
        },
        "conflict_state": {
            "material_unresolved_conflict": False,
            "conflict_set_ids": list(packet.conflict_set_ids),
        },
        "prior_root_state": {
            "prior_decision_id": None,
            "prior_decision": None,
            "prior_selected_candidate_id": None,
        },
    }


def _build_root_decision_fixture_v01() -> tuple[Any, tuple[Any, ...], tuple[Any, ...]]:
    packet = _build_semantic_work_fixture_v01()[3]
    kernel = build_root_decision_kernel_v01()
    if validate_root_decision_kernel_v01(kernel):
        raise ValueError("root_decision_kernel_invalid")
    scenarios = (
        ("identity_violation", {"policy_state": {"identity_passed": False}}),
        ("temporal_expired", {"temporal_state": {"expired": True}}),
        ("maximum_score_cannot_override_scope_failure", {"policy_state": {"scope_passed": False}, "maximum_score": True}),
        ("explicit_user_permission_missing", {"permission_state": {"permission_required": True}}),
        ("required_evidence_missing", {"post_vv_bundle": {"provided_evidence_refs": []}}),
        ("material_conflict_defer", {"conflict_state": {"material_unresolved_conflict": True}, "policy_state": {"conflict_policy": "DEFER"}}),
        ("material_conflict_reject", {"conflict_state": {"material_unresolved_conflict": True}, "policy_state": {"conflict_policy": "REJECT"}}),
        ("no_valid_candidate_no_update", {"gt_advisory": {"selected_candidate_id": None}, "policy_state": {"no_candidate_policy": "NO_UPDATE"}}),
        ("no_valid_candidate_reject", {"gt_advisory": {"selected_candidate_id": None}, "policy_state": {"no_candidate_policy": "REJECT"}}),
        ("validated_candidate_accept", {}),
    )
    expected = (
        (ROOT_DECISION_BLOCKED_FAIL_CLOSED, "hard_identity_violation"),
        (ROOT_DECISION_BLOCKED_FAIL_CLOSED, "hard_temporal_violation"),
        (ROOT_DECISION_BLOCKED_FAIL_CLOSED, "hard_scope_violation"),
        (ROOT_DECISION_NEEDS_USER, "user_permission_missing"),
        (ROOT_DECISION_NEEDS_MORE_EVIDENCE, "required_evidence_missing"),
        (ROOT_DECISION_DEFER, "material_conflict_deferred"),
        (ROOT_DECISION_REJECT, "material_conflict_rejected"),
        (ROOT_DECISION_NO_UPDATE, "no_valid_candidate"),
        (ROOT_DECISION_REJECT, "no_valid_candidate_rejected"),
        (ROOT_DECISION_ACCEPT, "validated_candidate_accepted"),
    )
    decision_inputs = []
    results = []
    packet_projection = semantic_work_to_plain_dict_v01(packet)
    for (_, changes), expected_outcome in zip(scenarios, expected):
        states = _root_decision_base_states_v01(packet)
        if changes.get("maximum_score", False):
            selected = states["gt_advisory"]["selected_candidate_id"]
            states["gt_advisory"]["score_micros_by_candidate"][selected] = 1_000_000
        for state_name, state_changes in changes.items():
            if state_name == "maximum_score":
                continue
            states[state_name].update(state_changes)
        decision_input = build_root_decision_input_v01(
            transaction_id=packet.transaction_id,
            target_root_id=packet.target_root_id,
            root_review_packet=packet,
            **states,
        )
        input_projection = root_decision_input_to_plain_dict_v01(decision_input)
        result = decide_root_v01(kernel=kernel, decision_input=decision_input)
        repeated = decide_root_v01(kernel=kernel, decision_input=decision_input)
        if (
            (result.decision, result.reason_code) != expected_outcome
            or validate_root_decision_result_v01(
                kernel=kernel,
                decision_input=decision_input,
                result=result,
            )
            or root_decision_result_to_plain_dict_v01(result)
            != root_decision_result_to_plain_dict_v01(repeated)
            or result.decision_id != repeated.decision_id
            or root_decision_input_to_plain_dict_v01(decision_input) != input_projection
            or semantic_work_to_plain_dict_v01(packet) != packet_projection
        ):
            raise ValueError("root_decision_fixture_invalid")
        decision_inputs.append(decision_input)
        results.append(result)
    return kernel, tuple(decision_inputs), tuple(results)


def _collect_root_decision_fixture_metrics_v01() -> dict[str, Any]:
    kernel, decision_inputs, results = _build_root_decision_fixture_v01()
    repeated_kernel, repeated_inputs, repeated_results = _build_root_decision_fixture_v01()
    if (
        root_decision_kernel_to_plain_dict_v01(kernel)
        != root_decision_kernel_to_plain_dict_v01(repeated_kernel)
        or tuple(root_decision_input_to_plain_dict_v01(item) for item in decision_inputs)
        != tuple(root_decision_input_to_plain_dict_v01(item) for item in repeated_inputs)
        or tuple(root_decision_result_to_plain_dict_v01(item) for item in results)
        != tuple(root_decision_result_to_plain_dict_v01(item) for item in repeated_results)
    ):
        raise ValueError("root_decision_fixture_nondeterministic")
    return {
        "kernel_id": kernel.kernel_id,
        "result_count": len(results),
        "blocked_count": sum(item.decision == ROOT_DECISION_BLOCKED_FAIL_CLOSED for item in results),
        "needs_user_count": sum(item.decision == ROOT_DECISION_NEEDS_USER for item in results),
        "needs_more_evidence_count": sum(item.decision == ROOT_DECISION_NEEDS_MORE_EVIDENCE for item in results),
        "defer_count": sum(item.decision == ROOT_DECISION_DEFER for item in results),
        "reject_count": sum(item.decision == ROOT_DECISION_REJECT for item in results),
        "no_update_count": sum(item.decision == ROOT_DECISION_NO_UPDATE for item in results),
        "accept_count": sum(item.decision == ROOT_DECISION_ACCEPT for item in results),
        "root_commit_created_count": sum(item.root_commit_created for item in results),
        "permission_created_count": sum(item.permission_created for item in results),
        "final_output_created_count": sum(item.final_output_created for item in results),
        "effect_requested_count": sum(item.effect_requested for item in results),
        "provider_call_count": 0,
        "network_call_count": 0,
        "gemini_call_count": 0,
        "real_world_effects_count": 0,
    }


def collect_root_decision_kernel_gauntlet_act_v01(
) -> LivingGauntletActResultV01:
    act_id = "root_decision_kernel"
    source_module, source_symbol = _ACTIVE_ACT_SOURCES[act_id]
    try:
        metrics = _collect_root_decision_fixture_metrics_v01()
        geometry = tuple(
            metrics[key]
            for key in (
                "result_count", "blocked_count", "needs_user_count",
                "needs_more_evidence_count", "defer_count", "reject_count",
                "no_update_count", "accept_count", "root_commit_created_count",
                "permission_created_count", "final_output_created_count",
                "effect_requested_count",
            )
        )
        if geometry != (10, 3, 1, 1, 1, 2, 1, 1, 10, 0, 0, 0):
            raise ValueError("root_decision_geometry_invalid")
        return LivingGauntletActResultV01(
            act_id=act_id, errors=(), executed=True,
            no_real_connector_or_action=True, real_world_effects_count=0,
            root_authority_preserved=True, runtime_status=STATUS_PASS,
            source_module=source_module, source_symbol=source_symbol,
            state=STATUS_PASS,
        )
    except Exception:
        return LivingGauntletActResultV01(
            act_id=act_id, errors=("root_decision_kernel_runtime_failed",),
            executed=True, no_real_connector_or_action=False,
            real_world_effects_count=-1, root_authority_preserved=False,
            runtime_status=STATUS_FAIL_CLOSED, source_module=source_module,
            source_symbol=source_symbol, state=STATUS_FAIL_CLOSED,
        )


_EFFECT_FIXTURE_TIME_ENVELOPE = {
    "pt_created_at": "2026-01-01T00:00:00+00:00",
    "kt_asof": "2026-01-01T00:00:00+00:00",
    "et_observed_at": None,
    "ct_session_anchor": "session:fixture:effect_firewall:001",
    "ttl_seconds": 3600,
    "freshness_class": "static",
    "valid_from": "2026-01-01T00:00:00+00:00",
    "valid_to": "2026-01-01T01:00:00+00:00",
}


def _build_effect_firewall_root_context_v01() -> tuple[Any, Any, Any, Any]:
    packet = _build_semantic_work_fixture_v01()[3]
    kernel = build_root_decision_kernel_v01()
    states = _root_decision_base_states_v01(packet)
    states["permission_state"] = {
        "permission_required": True,
        "user_permission_present": True,
        "permission_scope_valid": True,
        "permission_ref": "permission:fixture:effect_firewall:001",
    }
    decision_input = build_root_decision_input_v01(
        transaction_id=packet.transaction_id,
        target_root_id=packet.target_root_id,
        root_review_packet=packet,
        **states,
    )
    result = decide_root_v01(kernel=kernel, decision_input=decision_input)
    if (
        result.decision != ROOT_DECISION_ACCEPT
        or validate_root_decision_result_v01(
            kernel=kernel,
            decision_input=decision_input,
            result=result,
        )
        or result.root_commit_created is not True
        or result.selected_candidate_id is None
        or result.permission_created is not False
        or result.final_output_created is not False
        or result.effect_requested is not False
    ):
        raise ValueError("effect_firewall_root_context_invalid")
    return packet, kernel, decision_input, result


def _fresh_effect_firewall_request_v01() -> tuple[Any, ...]:
    packet, kernel, decision_input, result = (
        _build_effect_firewall_root_context_v01()
    )
    firewall = build_effect_firewall_v01(
        root_decision_kernel=kernel,
        decision_input=decision_input,
        root_decision_result=result,
        invocation_id="invocation:fixture:effect_firewall:001",
        allowed_adapter_ids=("mock_adapter:bounded_neutral_v01",),
        allowed_action_kinds=("mock_action:record_neutral_receipt",),
        root_scope_refs=("scope:neutral:alpha", "scope:neutral:beta"),
        maximum_expires_at_tick=200,
    )
    request = build_effect_request_v01(
        root_decision_kernel=kernel,
        decision_input=decision_input,
        root_decision_result=result,
        request_kind="ActionCommitPacket",
        adapter_id="mock_adapter:bounded_neutral_v01",
        action_kind="mock_action:record_neutral_receipt",
        scope_refs=("scope:neutral:alpha",),
        issued_at_tick=100,
        expires_at_tick=150,
        idempotency_key="idempotency:fixture:effect_firewall:001",
    )
    if validate_effect_firewall_v01(firewall) or validate_effect_request_v01(request):
        raise ValueError("effect_firewall_fixture_construction_invalid")
    return packet, kernel, decision_input, result, firewall, request


def _effect_request_variant_v01(request: Any, **changes: Any) -> Any:
    changed = replace(request, **changes)
    return replace(
        changed,
        request_id=effect_firewall_module._request_id(changed),
    )


def _fresh_effect_authorization_v01() -> tuple[Any, ...]:
    context = _fresh_effect_firewall_request_v01()
    firewall, request = context[-2:]
    decision = authorize_effect_request_v01(
        firewall=firewall,
        request=request,
        current_tick=110,
    )
    if (
        decision.decision != EFFECT_DECISION_ALLOW_MOCK_EFFECT
        or decision.reason_code != "mock_effect_authorized"
        or validate_effect_firewall_decision_v01(
            firewall=firewall,
            request=request,
            decision=decision,
        )
    ):
        raise ValueError("effect_firewall_authorization_invalid")
    return (*context, decision)


def _build_effect_firewall_fixture_v01() -> dict[str, Any]:
    context = _fresh_effect_authorization_v01()
    packet, kernel, decision_input, result, firewall, request, decision = context
    input_before = root_decision_input_to_plain_dict_v01(decision_input)
    result_before = root_decision_result_to_plain_dict_v01(result)
    packet_before = semantic_work_to_plain_dict_v01(packet)
    receipt = execute_mock_effect_v01(
        firewall=firewall,
        request=request,
        decision=decision,
        current_tick=120,
        adapter_id="mock_adapter:bounded_neutral_v01",
        action_kind="mock_action:record_neutral_receipt",
        child_scope_refs=("scope:neutral:alpha",),
        child_expires_at_tick=140,
        receipt_artifact_id="receipt:fixture:effect_firewall:001",
        time_envelope=_EFFECT_FIXTURE_TIME_ENVELOPE,
    )
    if (
        validate_effect_receipt_v01(
            firewall=firewall,
            request=request,
            decision=decision,
            receipt=receipt,
        )
        or validate_effect_firewall_v01(firewall)
        or root_decision_input_to_plain_dict_v01(decision_input) != input_before
        or root_decision_result_to_plain_dict_v01(result) != result_before
        or semantic_work_to_plain_dict_v01(packet) != packet_before
    ):
        raise ValueError("effect_firewall_receipt_invalid")
    return {
        "packet": packet,
        "kernel": kernel,
        "decision_input": decision_input,
        "root_result": result,
        "firewall": firewall,
        "request": request,
        "decision": decision,
        "receipt": receipt,
    }


def _expect_effect_block_v01(
    firewall: Any,
    request: Any,
    tick: int,
    reason: str,
) -> None:
    before = effect_firewall_to_plain_dict_v01(firewall)["state_counters"].copy()
    decision = authorize_effect_request_v01(
        firewall=firewall,
        request=request,
        current_tick=tick,
    )
    if (
        decision.decision != EFFECT_DECISION_BLOCKED_FAIL_CLOSED
        or decision.reason_code != reason
        or decision.capability_issued is not False
        or decision.capability_id is not None
        or decision.return_to_root is not True
        or decision.real_world_effects_count != 0
        or validate_effect_firewall_decision_v01(
            firewall=firewall,
            request=request,
            decision=decision,
        )
        or effect_firewall_to_plain_dict_v01(firewall)["state_counters"]
        != before
    ):
        raise ValueError("effect_firewall_negative_authorization_failed")


def _effect_execution_must_fail_v01(reason: str, **changes: Any) -> None:
    context = _fresh_effect_authorization_v01()
    firewall, request, decision = context[-3:]
    values = {
        "firewall": firewall,
        "request": request,
        "decision": decision,
        "current_tick": 120,
        "adapter_id": request.adapter_id,
        "action_kind": request.action_kind,
        "child_scope_refs": ("scope:neutral:alpha",),
        "child_expires_at_tick": 140,
        "receipt_artifact_id": "receipt:fixture:effect_firewall:negative",
        "time_envelope": _EFFECT_FIXTURE_TIME_ENVELOPE,
    }
    values.update(changes)
    before = effect_firewall_to_plain_dict_v01(firewall)["state_counters"].copy()
    try:
        execute_mock_effect_v01(**values)
    except ValueError as exc:
        if exc.args != (reason,):
            raise ValueError("effect_firewall_negative_execution_reason") from None
    else:
        raise ValueError("effect_firewall_negative_execution_allowed")
    if effect_firewall_to_plain_dict_v01(firewall)["state_counters"] != before:
        raise ValueError("effect_firewall_failed_execution_mutated_state")


def _effect_receipt_variant_v01(receipt: Any, field: str, value: Any) -> Any:
    plain = kernel_artifact_to_plain_dict_v01(receipt)
    payload = plain["payload"]
    payload[field] = value
    return build_kernel_artifact_v01(
        abi_version=plain["abi_version"],
        artifact_id=plain["artifact_id"],
        artifact_type=plain["artifact_type"],
        schema_version=plain["schema_version"],
        transaction_id=plain["transaction_id"],
        owner_root_id=plain["owner_root_id"],
        source_component=plain["source_component"],
        authority_class=plain["authority_class"],
        lifecycle_state=plain["lifecycle_state"],
        payload=payload,
        trace_refs=tuple(plain["trace_refs"]),
        parent_refs=tuple(plain["parent_refs"]),
        time_envelope=plain["time_envelope"],
    )


def _collect_effect_firewall_fixture_metrics_v01() -> dict[str, Any]:
    fixture = _build_effect_firewall_fixture_v01()
    firewall = fixture["firewall"]
    request = fixture["request"]
    decision = fixture["decision"]
    receipt = fixture["receipt"]

    attack_cases = []
    for changes, tick, reason, preserve_id in (
        ({"request_id": "0" * 64}, 110, "forged_request", True),
        ({"root_decision_id": "decision:other"}, 110, "request_root_binding_mismatch", False),
        ({"permission_ref": "receipt:fixture:effect_firewall:001"}, 110, "permission_binding_mismatch", False),
        ({"adapter_id": "adapter:real"}, 110, "real_effect_forbidden", False),
        ({"adapter_id": "mock_adapter:other"}, 110, "adapter_not_allowed", False),
        ({"action_kind": "mock_action:other"}, 110, "action_not_allowed", False),
        ({"scope_refs": ("scope:neutral:alpha", "scope:other")}, 110, "scope_expansion_forbidden", False),
        ({"expires_at_tick": 201}, 110, "ttl_expansion_forbidden", False),
        ({}, 99, "request_not_yet_valid", True),
        ({}, 150, "request_expired", True),
    ):
        fresh = _fresh_effect_firewall_request_v01()
        case_firewall, case_request = fresh[-2:]
        if changes:
            case_request = (
                replace(case_request, **changes)
                if preserve_id
                else _effect_request_variant_v01(case_request, **changes)
            )
        _expect_effect_block_v01(case_firewall, case_request, tick, reason)
        attack_cases.append(reason)

    fresh = _fresh_effect_firewall_request_v01()
    duplicate_firewall, duplicate_request = fresh[-2:]
    authorize_effect_request_v01(
        firewall=duplicate_firewall,
        request=duplicate_request,
        current_tick=110,
    )
    _expect_effect_block_v01(
        duplicate_firewall, duplicate_request, 110, "duplicate_request"
    )
    attack_cases.append("duplicate_request")

    fresh = _fresh_effect_firewall_request_v01()
    idempotent_firewall, first_request = fresh[-2:]
    authorize_effect_request_v01(
        firewall=idempotent_firewall,
        request=first_request,
        current_tick=110,
    )
    second_request = _effect_request_variant_v01(
        first_request,
        request_kind="ExecutionRequest",
    )
    _expect_effect_block_v01(
        idempotent_firewall,
        second_request,
        110,
        "duplicate_idempotency_key",
    )
    attack_cases.append("duplicate_idempotency_key")

    for reason, changes in (
        ("effect_capability_adapter_mismatch", {"adapter_id": "mock_adapter:other"}),
        ("effect_scope_expansion_forbidden", {"child_scope_refs": ("scope:other",)}),
        ("effect_ttl_expansion_forbidden", {"child_expires_at_tick": 151}),
    ):
        _effect_execution_must_fail_v01(reason, **changes)
        attack_cases.append(reason)

    try:
        execute_mock_effect_v01(
            firewall=firewall,
            request=request,
            decision=decision,
            current_tick=120,
            adapter_id=request.adapter_id,
            action_kind=request.action_kind,
            child_scope_refs=("scope:neutral:alpha",),
            child_expires_at_tick=140,
            receipt_artifact_id="receipt:fixture:effect_firewall:second",
            time_envelope=_EFFECT_FIXTURE_TIME_ENVELOPE,
        )
    except ValueError as exc:
        if exc.args != ("effect_capability_consumed",):
            raise ValueError("effect_firewall_duplicate_execution_reason") from None
    else:
        raise ValueError("effect_firewall_duplicate_execution_allowed")
    attack_cases.append("effect_capability_consumed")

    capability = firewall._state.issued_capabilities[decision.capability_id]
    if isinstance(decision, EffectCapabilityV01):
        raise ValueError("effect_firewall_public_capability_returned")
    for operation in (
        lambda: copy.copy(capability),
        lambda: copy.deepcopy(capability),
        lambda: pickle.dumps(capability),
        lambda: json.dumps(capability),
        lambda: canonical_json_bytes_v01(capability),
    ):
        try:
            operation()
        except (TypeError, ValueError):
            pass
        else:
            raise ValueError("effect_firewall_capability_serialized")
    firewall_projection = effect_firewall_to_plain_dict_v01(firewall)
    decision_projection = effect_firewall_decision_to_plain_dict_v01(decision)
    receipt_projection = kernel_artifact_to_plain_dict_v01(receipt)
    if (
        "EffectCapabilityV01" in repr(firewall_projection)
        or "EffectCapabilityV01" in repr(decision_projection)
        or "EffectCapabilityV01" in repr(receipt_projection)
        or "capability_id" in firewall_projection
        or any(isinstance(value, EffectCapabilityV01) for value in receipt_projection["payload"].values())
    ):
        raise ValueError("effect_firewall_capability_exposed")
    other = _fresh_effect_authorization_v01()
    other_firewall, other_request, other_decision = other[-3:]
    other_capability = other_firewall._state.issued_capabilities[
        other_decision.capability_id
    ]
    if (
        capability is other_capability
        or effect_firewall_module._capability_valid(
            capability, other_firewall, other_request
        )
    ):
        raise ValueError("effect_firewall_capability_transferable")
    forged = object.__new__(EffectCapabilityV01)
    for slot in EffectCapabilityV01.__slots__:
        object.__setattr__(forged, slot, getattr(capability, slot))
    object.__setattr__(forged, "_issuer_token", object())
    if effect_firewall_module._capability_valid(forged, firewall, request):
        raise ValueError("effect_firewall_capability_forgery_accepted")

    receipt_attacks = (
        ("future_permission_created", True),
        ("root_decision_created", True),
        ("final_output_created", True),
        ("effect_handle_exposed", True),
        ("real_world_effects_count", 1),
        ("scope_refs", ["scope:other"]),
    )
    for field, value in receipt_attacks:
        forged_receipt = _effect_receipt_variant_v01(receipt, field, value)
        if not validate_effect_receipt_v01(
            firewall=firewall,
            request=request,
            decision=decision,
            receipt=forged_receipt,
        ):
            raise ValueError("effect_firewall_receipt_attack_accepted")

    repeated = _build_effect_firewall_fixture_v01()
    if (
        effect_request_to_plain_dict_v01(request)
        != effect_request_to_plain_dict_v01(repeated["request"])
        or effect_firewall_decision_to_plain_dict_v01(decision)
        != effect_firewall_decision_to_plain_dict_v01(repeated["decision"])
        or kernel_artifact_to_plain_dict_v01(receipt)
        != kernel_artifact_to_plain_dict_v01(repeated["receipt"])
        or effect_firewall_to_plain_dict_v01(firewall)
        != effect_firewall_to_plain_dict_v01(repeated["firewall"])
    ):
        raise ValueError("effect_firewall_fixture_nondeterministic")

    counters = firewall_projection["state_counters"]
    return {
        "firewall_count": 1,
        "request_count": 1,
        "allowed_authorization_count": 1,
        "capability_issued_count": counters["issued_capability_count"],
        "mock_effect_execution_count": counters["mock_effect_execution_count"],
        "evidence_receipt_count": 1,
        "return_to_root_transition_count": 1,
        "duplicate_execution_success_count": 0,
        "negative_test_count": len(attack_cases) + len(receipt_attacks),
        "capability_public_exposure_count": 0,
        "permission_created_count": 0,
        "root_decision_created_by_firewall_count": 0,
        "final_output_created_count": 0,
        "real_connector_count": 0,
        "provider_call_count": 0,
        "network_call_count": 0,
        "gemini_call_count": 0,
        "real_world_effects_count": 0,
        "firewall_id": firewall.firewall_id,
        "request_id": request.request_id,
        "decision_id": decision.decision_id,
        "capability_id": decision.capability_id,
    }


def collect_effect_firewall_gauntlet_act_v01() -> LivingGauntletActResultV01:
    act_id = "effect_firewall"
    source_module, source_symbol = _ACTIVE_ACT_SOURCES[act_id]
    try:
        metrics = _collect_effect_firewall_fixture_metrics_v01()
        geometry = tuple(
            metrics[key]
            for key in (
                "firewall_count",
                "request_count",
                "allowed_authorization_count",
                "capability_issued_count",
                "mock_effect_execution_count",
                "evidence_receipt_count",
                "return_to_root_transition_count",
                "duplicate_execution_success_count",
                "capability_public_exposure_count",
                "permission_created_count",
                "root_decision_created_by_firewall_count",
                "final_output_created_count",
                "real_connector_count",
                "provider_call_count",
                "network_call_count",
                "gemini_call_count",
                "real_world_effects_count",
            )
        )
        if geometry != (1, 1, 1, 1, 1, 1, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0):
            raise ValueError("effect_firewall_geometry_invalid")
        if metrics["negative_test_count"] < 22:
            raise ValueError("effect_firewall_negative_geometry_invalid")
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
            errors=("effect_firewall_runtime_failed",),
            executed=True,
            no_real_connector_or_action=False,
            real_world_effects_count=-1,
            root_authority_preserved=False,
            runtime_status=STATUS_FAIL_CLOSED,
            source_module=source_module,
            source_symbol=source_symbol,
            state=STATUS_FAIL_CLOSED,
        )


def _neutral_root_decision_v01(
    *, transaction_id: str, root_id: str, outcome_class: str
) -> multiroot.RootDecisionEnvelopeV01:
    return multiroot.build_root_decision_envelope_v01(
        transaction_id=transaction_id,
        root_id=root_id,
        root_decision_id=f"decision:{transaction_id}:{root_id}",
        source_decision_ref=f"source:{transaction_id}:{root_id}",
        outcome_class=outcome_class,
        reason_code=f"reason:{outcome_class.lower()}",
        selected_subject_id=(
            f"subject:{root_id}" if outcome_class == "ACCEPTED" else None
        ),
        evidence_refs=(f"evidence:{root_id}",),
        cross_root_input_refs=(),
    )


def _neutral_multiroot_outcome_v01(
    *,
    transaction_id: str,
    root_ids: tuple[str, ...],
    outcome_classes: tuple[str, ...],
) -> multiroot.TransactionOutcomeEnvelopeV01:
    return multiroot.build_transaction_outcome_envelope_v01(
        transaction_id=transaction_id,
        expected_root_ids=root_ids,
        root_decisions=tuple(
            _neutral_root_decision_v01(
                transaction_id=transaction_id,
                root_id=root_id,
                outcome_class=outcome_class,
            )
            for root_id, outcome_class in zip(
                root_ids, outcome_classes, strict=False
            )
        ),
        cross_root_evidence_refs=(),
    )


def collect_generic_multiroot_gauntlet_act_v01() -> LivingGauntletActResultV01:
    act_id = "generic_multiroot"
    source_module, source_symbol = _ACTIVE_ACT_SOURCES[act_id]
    try:
        three = _neutral_multiroot_outcome_v01(
            transaction_id="transaction:multiroot:three",
            root_ids=("root:alpha", "root:beta", "root:gamma"),
            outcome_classes=("ACCEPTED", "ACCEPTED", "ACCEPTED"),
        )
        four = _neutral_multiroot_outcome_v01(
            transaction_id="transaction:multiroot:four",
            root_ids=("root:north", "root:east", "root:south", "root:west"),
            outcome_classes=("ACCEPTED",) * 4,
        )
        mixed = _neutral_multiroot_outcome_v01(
            transaction_id="transaction:multiroot:mixed",
            root_ids=("root:first", "root:second"),
            outcome_classes=("ACCEPTED", "BLOCKED"),
        )
        incomplete = _neutral_multiroot_outcome_v01(
            transaction_id="transaction:multiroot:incomplete",
            root_ids=("root:one", "root:two", "root:three"),
            outcome_classes=("ACCEPTED", "ACCEPTED"),
        )
        validations = tuple(
            multiroot.validate_multiroot_v01(outcome)
            for outcome in (three, four, mixed, incomplete)
        )
        unknown_decision = _neutral_root_decision_v01(
            transaction_id=three.transaction_id,
            root_id="root:unknown",
            outcome_class="ACCEPTED",
        )
        unknown = replace(
            three,
            root_decisions=(unknown_decision, *three.root_decisions[1:]),
            observed_root_ids=("root:unknown", *three.observed_root_ids[1:]),
        )
        duplicate = replace(
            three,
            expected_root_ids=("root:alpha", "root:alpha", "root:gamma"),
        )
        reserved = replace(
            three,
            expected_root_ids=("root:superroot", "root:beta", "root:gamma"),
        )
        invalid_validations = tuple(
            multiroot.validate_multiroot_v01(outcome)
            for outcome in (unknown, duplicate, reserved)
        )
        passed = (
            tuple(item.final_status for item in validations)
            == (
                multiroot.STATUS_PASS,
                multiroot.STATUS_PASS,
                multiroot.STATUS_MIXED,
                multiroot.STATUS_INCOMPLETE,
            )
            and mixed.mixed_outcomes_visible is True
            and validations[3].missing_root_ids == ("root:three",)
            and all(
                item.final_status == multiroot.STATUS_FAIL_CLOSED
                for item in invalid_validations
            )
            and all(
                item.authority_transfer_count == 0
                and item.permission_creation_count == 0
                and item.real_world_effects_count == 0
                for item in (*validations, *invalid_validations)
            )
        )
        if not passed:
            raise ValueError("generic_multiroot_runtime_failed")
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
            errors=("generic_multiroot_runtime_failed",),
            executed=True,
            no_real_connector_or_action=False,
            real_world_effects_count=-1,
            root_authority_preserved=False,
            runtime_status=STATUS_FAIL_CLOSED,
            source_module=source_module,
            source_symbol=source_symbol,
            state=STATUS_FAIL_CLOSED,
        )


def collect_supplier_water_filter_portability_gauntlet_act_v01(
) -> LivingGauntletActResultV01:
    act_id = "supplier_water_filter_portability"
    source_module, source_symbol = _ACTIVE_ACT_SOURCES[act_id]
    try:
        source_report = collect_full_wow_v1_2_product_trace()
        result = (
            supplier_water_filter_adapter.
            build_supplier_water_filter_kernel_adapter_result_v01(
                source_report=source_report
            )
        )
        validation_errors = (
            supplier_water_filter_adapter.
            validate_supplier_water_filter_kernel_adapter_result_v01(
                source_report=source_report,
                result=result,
            )
        )
        projection = (
            supplier_water_filter_adapter.
            supplier_water_filter_kernel_adapter_result_to_plain_dict_v01(result)
        )
        canonical_json_bytes_v01(projection)
        forged_effect_result = replace(result, real_world_effects_count=1)
        forged_effect_errors = (
            supplier_water_filter_adapter.
            validate_supplier_water_filter_kernel_adapter_result_v01(
                source_report=source_report,
                result=forged_effect_result,
            )
        )
        passed = (
            source_report.get("final_status") == STATUS_PASS
            and source_report.get("validation_errors") == ()
            and not validation_errors
            and len(result.kernel_artifacts)
            == supplier_water_filter_adapter.TRANSITION_CARD_COUNT
            and result.kernel_manifest.dependency_edge_count
            == supplier_water_filter_adapter.DEPENDENCY_EDGE_COUNT
            and len(result.causal_consumption_refs)
            == supplier_water_filter_adapter.DEPENDENCY_EDGE_COUNT
            and result.kernel_unanchored_verification.verification_status
            == KERNEL_STATUS_UNANCHORED
            and result.kernel_anchored_verification.verification_status
            == STATUS_PASS
            and result.kernel_replay.replay_status == STATUS_PASS
            and result.multiroot_outcome.outcome_status == multiroot.STATUS_MIXED
            and result.multiroot_validation.final_status == multiroot.STATUS_MIXED
            and result.multiroot_outcome.outcome_status != multiroot.STATUS_PASS
            and result.supplier_b_status
            == supplier_water_filter_adapter.SUPPLIER_B_STATUS
            and result.shipment_status
            == supplier_water_filter_adapter.SHIPMENT_STATUS
            and result.receipt_status
            == supplier_water_filter_adapter.RECEIPT_STATUS
            and bool(forged_effect_errors)
            and "supplier_water_filter_effect_creation_forbidden"
            in forged_effect_errors
            and all(
                value == 0
                for value in (
                    result.provider_call_count,
                    result.network_call_count,
                    result.gemini_call_count,
                    result.real_world_effects_count,
                )
            )
        )
        if not passed:
            raise ValueError("supplier_water_filter_runtime_failed")
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
            errors=("supplier_water_filter_runtime_failed",),
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


def _aggregate_real_world_effects_count(
    active: Any,
    *,
    expected_active_ids: tuple[str, ...] = _ACTIVE_ACT_IDS,
) -> int:
    if not isinstance(active, list) or len(active) != len(expected_active_ids):
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
    *,
    active_ids: tuple[str, ...] = _ACTIVE_ACT_IDS,
    counter_field_names: frozenset[str] = _COUNTER_FIELD_NAMES,
) -> dict[str, int]:
    active_rows = active if isinstance(active, list) else []
    evidence_rows = evidence if isinstance(evidence, list) else []
    planned_rows = planned if isinstance(planned, list) else []
    counters = {
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
            and row.get("act_id") == "airline_deterministic_transaction_runtime"
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
            and row.get("act_id") == "generic_integrity_replay"
            and row.get("executed") is True
            for row in active_rows
        ),
        "planned_act_count": len(planned_rows),
        "planned_executed_count": sum(
            isinstance(row, Mapping) and row.get("executed") is True
            for row in planned_rows
        ),
        "real_world_effects_count": _aggregate_real_world_effects_count(
            active_rows,
            expected_active_ids=active_ids,
        ),
        "root_signer_isolation_execution_count": sum(
            isinstance(row, Mapping)
            and row.get("act_id") == "root_signer_isolation_conformance"
            and row.get("executed") is True
            for row in active_rows
        ),
        "semantic_work_contract_execution_count": sum(
            isinstance(row, Mapping)
            and row.get("act_id") == "semantic_work_contract"
            and row.get("executed") is True
            for row in active_rows
        ),
        "domain_neutral_kernel_abi_execution_count": sum(
            isinstance(row, Mapping)
            and row.get("act_id") == "domain_neutral_kernel_abi"
            and row.get("executed") is True
            for row in active_rows
        ),
        "causal_consumption_execution_count": sum(
            isinstance(row, Mapping)
            and row.get("act_id") == "causal_consumption"
            and row.get("executed") is True
            for row in active_rows
        ),
        "transition_registry_execution_count": sum(
            isinstance(row, Mapping)
            and row.get("act_id") == "transition_registry"
            and row.get("executed") is True
            for row in active_rows
        ),
        "root_decision_kernel_execution_count": sum(
            isinstance(row, Mapping)
            and row.get("act_id") == "root_decision_kernel"
            and row.get("executed") is True
            for row in active_rows
        ),
        "effect_firewall_execution_count": sum(
            isinstance(row, Mapping)
            and row.get("act_id") == "effect_firewall"
            and row.get("executed") is True
            for row in active_rows
        ),
        "generic_multiroot_execution_count": sum(
            isinstance(row, Mapping)
            and row.get("act_id") == "generic_multiroot"
            and row.get("executed") is True
            for row in active_rows
        ),
        "supplier_water_filter_portability_execution_count": sum(
            isinstance(row, Mapping)
            and row.get("act_id") == "supplier_water_filter_portability"
            and row.get("executed") is True
            for row in active_rows
        ),
        "kernel_conformance_closure_execution_count": sum(
            isinstance(row, Mapping)
            and row.get("act_id") == "kernel_conformance_closure"
            and row.get("executed") is True
            for row in active_rows
        ),
        "action_packet_lifecycle_execution_count": sum(
            isinstance(row, Mapping)
            and row.get("act_id") == "action_packet_lifecycle"
            and row.get("executed") is True
            for row in active_rows
        ),
        "drs_semantic_address_reuse_certificate_execution_count": sum(
            isinstance(row, Mapping)
            and row.get("act_id")
            == "drs_semantic_address_and_reuse_certificate"
            and row.get("executed") is True
            for row in active_rows
        ),
        "execution_mode_router_execution_count": sum(
            isinstance(row, Mapping)
            and row.get("act_id") == "execution_mode_router"
            and row.get("executed") is True
            for row in active_rows
        ),
        "fractal_runtime_execution_count": sum(
            isinstance(row, Mapping)
            and row.get("act_id") == "fractal_runtime"
            and row.get("executed") is True
            for row in active_rows
        ),
        "continuous_delta_runtime_execution_count": sum(
            isinstance(row, Mapping)
            and row.get("act_id") == "continuous_delta_runtime"
            and row.get("executed") is True
            for row in active_rows
        ),
    }
    return {
        key: value for key, value in counters.items() if key in counter_field_names
    }


def _prefixed_sha256_identity_v01(value: object, prefix: str) -> bool:
    return (
        type(value) is str
        and value.startswith(prefix)
        and len(value) == len(prefix) + 64
        and all(character in "0123456789abcdef" for character in value[len(prefix) :])
    )


def _action_packet_lifecycle_domain_passes_v01(
    result: object,
    *,
    domain_shape: str,
    root_id: str,
    invalidation_class: str,
) -> bool:
    try:
        replay = result.replay_report
        inspection = result.present_inspection
        transitions = replay.recorded_transitions
        domain_context = domain_shape.lower()
        expected_transitions = (
            (
                "g2a_t01_activate_root_authorization",
                "CREATED",
                "ROOT_AUTHORIZED",
                f"evaluation_context:g2a5:{domain_context}:activate",
            ),
            (
                "g2a_t02_queue",
                "ROOT_AUTHORIZED",
                "QUEUED",
                f"evaluation_context:g2a5:{domain_context}:g2a_t02_queue",
            ),
            (
                "g2a_t03_pending",
                "QUEUED",
                "PENDING_FULFILLMENT",
                f"evaluation_context:g2a5:{domain_context}:g2a_t03_pending",
            ),
            (
                "g2a_t09_pending_block",
                "PENDING_FULFILLMENT",
                "BLOCKED",
                f"evaluation_context:g2a5:{domain_context}:invalidation",
            ),
        )
        if (
            result.domain_shape != domain_shape
            or result.owning_local_root_id != root_id
            or result.invalidation_class != invalidation_class
            or result.authority_effect != "DETERMINISTIC_BLOCK"
            or result.transition_rule_id != "g2a_t09_pending_block"
            or not _prefixed_sha256_identity_v01(result.packet_id, "acp_v02:")
            or result.lifecycle_before != "PENDING_FULFILLMENT"
            or result.lifecycle_after != "BLOCKED"
            or result.idempotency_disposition_after != "RESERVED"
            or result.reservation_owner_packet_id_after != result.packet_id
            or type(transitions) is not tuple
            or len(transitions) != 4
        ):
            return False
        for index, (transition, expected) in enumerate(
            zip(transitions, expected_transitions)
        ):
            rule_id, source_state, target_state, context_id = expected
            attempt_id = transition.execution_attempt_id
            if (
                not _prefixed_sha256_identity_v01(
                    transition.transition_event_id,
                    "acpt_v01:",
                )
                or transition.transition_rule_id != rule_id
                or transition.source_state != source_state
                or transition.target_state != target_state
                or type(transition.evaluation_time) is not int
                or transition.evaluation_time != 1783470600 + index
                or transition.evaluation_time_source
                != "explicit_g2a5_synthetic_time"
                or transition.evaluation_context_id != context_id
                or (
                    index == 2
                    and not _prefixed_sha256_identity_v01(
                        attempt_id,
                        "execution_attempt_v01:",
                    )
                )
                or (index != 2 and attempt_id is not None)
                or transition.effect_consumption_class != "NOT_CONSUMED"
                or transition.receipt_ref is not None
            ):
                return False
        state = replay.reconstructed_state
        return (
            replay.packet_id == result.packet_id
            and replay.rebuilt_packet_id == result.packet_id
            and replay.transition_registry_id == result.transition_registry_id
            and replay.registry_unchanged is True
            and replay.historical_temporal_replay_pass is True
            and replay.t24_reserved_history_replay_pass is True
            and replay.distinct_firewall_attempt_replay_pass is True
            and replay.creates_authority is False
            and replay.creates_permission is False
            and replay.creates_packet is False
            and replay.creates_receipt is False
            and replay.adapter_calls == 0
            and replay.real_world_effects_count == 0
            and state.packet_id == result.packet_id
            and state.lifecycle_state == "BLOCKED"
            and state.transition_event_count == 4
            and state.latest_transition_event_id
            == transitions[-1].transition_event_id
            and state.execution_attempt_count == 1
            and state.idempotency_disposition == "RESERVED"
            and state.reservation_owner_packet_id == result.packet_id
            and state.terminal_receipt_ref is None
            and state.lifecycle_terminal is True
            and state.executable is False
            and state.registry_is_authority is False
            and state.registry_grants_permission is False
            and state.real_world_effects_count == 0
            and inspection.packet_id == result.packet_id
            and inspection.historical_state == state
            and inspection.historical_result_unchanged is True
            and inspection.present_eligibility_status == "NON_EXECUTABLE"
            and inspection.present_executable is False
            and inspection.retry_eligible is False
            and inspection.creates_authority is False
            and inspection.creates_permission is False
            and inspection.creates_packet is False
            and inspection.creates_receipt is False
            and inspection.adapter_calls == 0
            and inspection.real_world_effects_count == 0
            and result.registry_creates_authority is False
            and result.adapter_calls == 0
            and result.receipt_creations == 0
            and result.real_world_effects_count == 0
        )
    except Exception:
        return False


def collect_action_packet_lifecycle_gauntlet_act_v01(
) -> LivingGauntletActResultV01:
    act_id = "action_packet_lifecycle"
    source_module, source_symbol = _ACTIVE_ACT_SOURCES[act_id]
    try:
        report = (
            _action_packet_lifecycle.collect_action_commit_packet_lifecycle_g2_a_v01()
        )
        valid, validation_errors = (
            _action_packet_lifecycle.validate_action_commit_packet_lifecycle_g2_a_report_v01(
                report
            )
        )
        if (
            type(report)
            is not _action_packet_lifecycle.ActionCommitPacketLifecycleG2A5ReportV01
            or valid is not True
            or validation_errors != ()
            or report.final_status != STATUS_PASS
            or report.same_packet_family is not True
            or report.same_transition_registry_id is not True
            or report.same_authority_law is not True
            or report.immutable_history_proven is not True
            or report.closed_domain_artifacts_rerun is not False
            or not _action_packet_lifecycle_domain_passes_v01(
                report.airline,
                domain_shape="AIRLINE",
                root_id="root:g2a5:airline",
                invalidation_class="DEPENDENCY_CHANGED",
            )
            or not _action_packet_lifecycle_domain_passes_v01(
                report.supplier,
                domain_shape="SUPPLIER",
                root_id="root:g2a5:supplier",
                invalidation_class="ROOT_BOUND_KILL_SWITCH",
            )
            or report.airline.packet_id == report.supplier.packet_id
            or report.airline.transition_registry_id
            != report.supplier.transition_registry_id
            or report.airline.generic_authority_law_id
            != report.supplier.generic_authority_law_id
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
            raise ValueError
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
            errors=("action_packet_lifecycle_gauntlet_act_failed",),
            executed=True,
            no_real_connector_or_action=False,
            real_world_effects_count=-1,
            root_authority_preserved=False,
            runtime_status=STATUS_FAIL_CLOSED,
            source_module=source_module,
            source_symbol=source_symbol,
            state=STATUS_FAIL_CLOSED,
        )


def _g2b_domain_result_passes_v01(value: object) -> bool:
    try:
        answer = value.answer_report
        context = value.context_report
        descent = answer.memory_descent_result
        certificate = answer.reuse_certificate
        writeback = value.writeback_evidence
        selected = tuple(
            item
            for item in answer.eligible_candidates
            if item.resolution_candidate_id == answer.selected_candidate_id
        )
        return (
            type(value) is _g2b._G2B5DomainProofV01
            and value.final_status == STATUS_PASS
            and value.reason_codes == ()
            and value.pure_read_snapshot_before
            == value.pure_read_snapshot_after
            and type(value.answer_use_time) is int
            and type(answer.query.as_of) is int
            and len(selected) == 1
            and answer.root_shortcut_projection is not None
            and certificate is not None
            and descent is not None
            and descent.executed_descent_class == "SUMMARY_ONLY"
            and descent.bytes_opened == 0
            and descent.real_world_effects_count == 0
            and all(
                evaluation.g2a_action_history_passed is True
                and evaluation.permission_boundary_passed is True
                and evaluation.creates_authority is False
                and evaluation.creates_permission is False
                for evaluation in answer.query_evaluations
            )
            and context.selected_candidate_id is None
            and context.root_shortcut_projection is None
            and context.reuse_certificate is None
            and context.memory_descent_result is None
            and tuple(
                _g2b._action_reason(request)
                for request in value.negative_requests
            )
            == value.negative_reason_codes
            and writeback
            == {
                **writeback,
                "predecessor_preserved": True,
                "successor_readback_exact": True,
                "records_written": 1,
                "creates_authority": False,
                "creates_permission": False,
                "real_world_effects_count": 0,
            }
            and certificate.creates_authority is False
            and certificate.creates_permission is False
            and certificate.creates_final_output is False
            and certificate.creates_action_commit_packet is False
            and certificate.creates_receipt is False
            and certificate.creates_capability is False
            and certificate.creates_effect_handle is False
            and certificate.creates_effect is False
            and certificate.real_world_effects_count == 0
        )
    except Exception:
        return False


def _g2b_report_passes_living_act_v01(value: object) -> bool:
    try:
        return (
            type(value) is _g2b._G2B5DeterministicReportV01
            and value.final_status == STATUS_PASS
            and value.reason_codes == ()
            and value.domain_order
            == (
                "TRAVEL_POLICY_INFORMATION",
                "WAREHOUSE_MAINTENANCE_INFORMATION",
            )
            and type(value.domain_results) is tuple
            and len(value.domain_results) == 2
            and all(
                _g2b_domain_result_passes_v01(domain)
                for domain in value.domain_results
            )
            and sum(
                len(domain.negative_requests)
                for domain in value.domain_results
            )
            == 8
            and value.operation_counters
            == _G2B_EXPECTED_OPERATION_COUNTERS_V01
            and value.closed_programme_counters
            == _G2B_EXPECTED_CLOSED_PROGRAMME_COUNTERS_V01
            and value.raw_user_request_to_query_cross_binding_implemented
            is False
            and value.production_generic_informational_responder_claimed
            is False
        )
    except Exception:
        return False


def collect_drs_semantic_address_and_reuse_certificate_gauntlet_act_v01(
) -> LivingGauntletActResultV01:
    act_id = "drs_semantic_address_and_reuse_certificate"
    source_module, source_symbol = _ACTIVE_ACT_SOURCES[act_id]
    try:
        report = (
            _g2b.collect_drs_semantic_address_reuse_certificate_g2_b_v01()
        )
        validation_result = (
            _g2b.validate_drs_semantic_address_reuse_certificate_g2_b_report_v01(
                report
            )
        )
        if (
            validation_result != (True, ())
            or not _g2b_report_passes_living_act_v01(report)
        ):
            raise ValueError
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
            errors=(
                "drs_semantic_address_reuse_certificate_gauntlet_act_failed",
            ),
            executed=True,
            no_real_connector_or_action=False,
            real_world_effects_count=-1,
            root_authority_preserved=False,
            runtime_status=STATUS_FAIL_CLOSED,
            source_module=source_module,
            source_symbol=source_symbol,
            state=STATUS_FAIL_CLOSED,
        )


_G2C_EXPECTED_DOMAIN_ORDER_V13 = (
    "TRAVEL_POLICY_INFORMATION",
    "WAREHOUSE_MAINTENANCE_INFORMATION",
)
_G2C_EXPECTED_CASE_ORDER_V13 = (
    "g2c_case:travel:sealed_replay:v01",
    "g2c_case:travel:direct_informational_reuse:v01",
    "g2c_case:travel:memory_informed:v01",
    "g2c_case:travel:cloud_llm_narrow:v01",
    "g2c_case:travel:full_semantic_reject:v01",
    "g2c_case:warehouse:deterministic_new_action:v01",
    "g2c_case:warehouse:local_slm:v01",
    "g2c_case:warehouse:full_fractal_fixture_capability:v01",
    "g2c_case:warehouse:blocked_existing_packet:v01",
    "g2c_case:warehouse:needs_user:v01",
)
_G2C_EXPECTED_CASE_GEOMETRY_V13 = (
    (
        "g2c_sealed_replay_feasible",
        "validated_candidate_accepted",
        "ACCEPT",
        "g2c_root_accept_projected",
        "g2c_transition_route_accept_allowed",
        True,
    ),
    (
        "g2c_direct_informational_reuse_feasible",
        "validated_candidate_accepted",
        "ACCEPT",
        "g2c_root_accept_projected",
        "g2c_transition_route_accept_allowed",
        True,
    ),
    (
        "g2c_memory_informed_feasible",
        "validated_candidate_accepted",
        "ACCEPT",
        "g2c_root_accept_projected",
        "g2c_transition_route_accept_allowed",
        True,
    ),
    (
        "g2c_cloud_llm_feasible",
        "validated_candidate_accepted",
        "NARROW",
        "g2c_root_narrow_projected",
        "g2c_transition_scope_narrow_allowed",
        True,
    ),
    (
        "g2c_full_semantic_feasible",
        "policy_rejected_candidate",
        "REJECT",
        "g2c_root_reject_projected",
        "g2c_transition_reject_recorded",
        False,
    ),
    (
        "g2c_deterministic_feasible",
        "validated_candidate_accepted",
        "ACCEPT",
        "g2c_root_accept_projected",
        "g2c_transition_route_accept_allowed",
        True,
    ),
    (
        "g2c_local_slm_feasible",
        "validated_candidate_accepted",
        "ACCEPT",
        "g2c_root_accept_projected",
        "g2c_transition_route_accept_allowed",
        True,
    ),
    (
        "g2c_full_fractal_feasible",
        "validated_candidate_accepted",
        "ACCEPT",
        "g2c_root_accept_projected",
        "g2c_transition_route_accept_allowed",
        True,
    ),
    (
        "g2c_hard_block_present",
        "hard_policy_violation",
        "BLOCKED",
        "g2c_root_blocked_projected",
        "g2c_transition_blocked_recorded",
        False,
    ),
    (
        "g2c_user_input_required",
        "user_permission_missing",
        "NEEDS_USER",
        "g2c_root_needs_user_projected",
        "g2c_transition_needs_user_recorded",
        False,
    ),
)
_G2C_ZERO_OPERATION_FIELDS_V13 = (
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


def _execution_mode_router_report_passes_living_act_v01(
    report: object,
) -> bool:
    try:
        if (
            type(report) is not _g2c.ExecutionModeRouterG2CReportV01
            or _g2c.validate_execution_mode_router_g2_c_report_v01(report) != ()
            or report.report_version != "v0.1"
            or report.profile_id
            != "execution_mode_router_g2c_two_domain_proof_v01"
            or report.final_status != STATUS_PASS
            or report.reason_codes != ()
            or report.domain_order != _G2C_EXPECTED_DOMAIN_ORDER_V13
            or report.case_order != _G2C_EXPECTED_CASE_ORDER_V13
            or type(report.case_results) is not tuple
            or len(report.case_results) != 10
            or any(
                type(getattr(report, name)) is not int
                or getattr(report, name) != 0
                for name in _G2C_ZERO_OPERATION_FIELDS_V13
            )
        ):
            return False
        for index, (case, expected) in enumerate(
            zip(
                report.case_results,
                _G2C_EXPECTED_CASE_GEOMETRY_V13,
                strict=True,
            )
        ):
            (
                row_reason,
                source_root_reason,
                root_outcome,
                projection_reason,
                post_transition_reason,
                eligibility_present,
            ) = expected
            if (
                case.case_id != _G2C_EXPECTED_CASE_ORDER_V13[index]
                or case.selected_feasibility_row_id
                != case.rebuilt_selected_feasibility_row_id
                or case.selected_row_reason != row_reason
                or case.proposal_reason_codes
                != ("g2c_proposal_sources_valid",)
                or case.source_root_reason != source_root_reason
                or case.root_outcome != root_outcome
                or case.root_projection_reason_codes
                != (projection_reason,)
                or case.pre_root_transition_reason
                != "g2c_transition_root_review_required"
                or case.post_root_transition_reason
                != post_transition_reason
                or (case.route_eligibility_artifact_id is not None)
                is not eligibility_present
                or case.root_review_conflict_set_ids != ()
                or case.root_input_conflict_set_ids != ()
                or case.root_result_conflict_set_ids != ()
                or len(case.root_support_ids) != 6
                or len(set(case.root_support_ids)) != 6
                or case.operation_steps != _g2c.OPERATION_STEPS
                or case.final_status != STATUS_PASS
                or case.reason_codes != ()
                or any(
                    type(getattr(case, name)) is not int
                    or getattr(case, name) != 0
                    for name in _G2C_ZERO_OPERATION_FIELDS_V13
                )
            ):
                return False
            if index in (1, 2, 3) and (
                case.temporal_query_id is None
                or not case.temporal_query_id.startswith("drsquery_v01:")
                or case.transaction_id != case.temporal_query_id
            ):
                return False
        return {case.root_outcome for case in report.case_results} == {
            "ACCEPT",
            "NARROW",
            "REJECT",
            "BLOCKED",
            "NEEDS_USER",
        }
    except Exception:
        return False


def collect_execution_mode_router_gauntlet_act_v01(
) -> LivingGauntletActResultV01:
    act_id = "execution_mode_router"
    source_module, source_symbol = _ACTIVE_ACT_SOURCES[act_id]
    try:
        report = _g2c.collect_execution_mode_router_g2_c_v01()
        if not _execution_mode_router_report_passes_living_act_v01(report):
            raise ValueError
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
            errors=("execution_mode_router_gauntlet_act_failed",),
            executed=True,
            no_real_connector_or_action=False,
            real_world_effects_count=-1,
            root_authority_preserved=False,
            runtime_status=STATUS_FAIL_CLOSED,
            source_module=source_module,
            source_symbol=source_symbol,
            state=STATUS_FAIL_CLOSED,
        )


_G2D_ZERO_COUNTER_FIELDS_V14 = (
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


def _fractal_runtime_report_passes_living_act_v01(report: object) -> bool:
    try:
        if type(report) is not _g2d.FractalRuntimeG2DReportV02:
            return False
        cases = report.case_results
        return (
            report.report_version == _g2d.REPORT_VERSION
            and report.profile_id == _g2d.PROFILE_ID
            and report.final_status == STATUS_PASS
            and report.reason_codes == ()
            and report.domain_order
            == (
                "TRAVEL_POLICY_INFORMATION",
                "WAREHOUSE_MAINTENANCE_INFORMATION",
            )
            and len(report.case_order) == len(cases) == 72
            and report.case_order == tuple(item.case_id for item in cases)
            and len(set(report.case_order)) == 72
            and report.constructive_case_count == 36
            and report.negative_case_count == 36
            and report.domain_positive_case_count == 10
            and report.accepted_bundle_count == 10
            and report.topology_created_count == 10
            and all(
                type(getattr(report, name)) is int
                and getattr(report, name) == 0
                for name in _G2D_ZERO_COUNTER_FIELDS_V14
            )
            and all(
                item.final_status == STATUS_PASS
                and item.reason_codes == ()
                and item.observed_outcome == item.expected_outcome
                and type(item.evidence_material_json) is str
                and hashlib.sha256(
                    item.evidence_material_json.encode("ascii")
                ).hexdigest()
                == item.evidence_sha256
                and all(
                    type(getattr(item, name)) is int
                    and getattr(item, name) == 0
                    for name in _G2D_ZERO_COUNTER_FIELDS_V14
                )
                for item in cases
            )
        )
    except Exception:
        return False


def _fractal_runtime_gauntlet_act_from_validated_report_v01(
    report: object,
) -> LivingGauntletActResultV01:
    act_id = "fractal_runtime"
    source_module, source_symbol = _ACTIVE_ACT_SOURCES[act_id]
    if _fractal_runtime_report_passes_living_act_v01(report):
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
    return LivingGauntletActResultV01(
        act_id=act_id,
        errors=("fractal_runtime_gauntlet_act_failed",),
        executed=True,
        no_real_connector_or_action=False,
        real_world_effects_count=-1,
        root_authority_preserved=False,
        runtime_status=STATUS_FAIL_CLOSED,
        source_module=source_module,
        source_symbol=source_symbol,
        state=STATUS_FAIL_CLOSED,
    )


def collect_fractal_runtime_gauntlet_act_v01() -> LivingGauntletActResultV01:
    try:
        report = _g2d.collect_fractal_runtime_g2_d_v02()
        reasons = _g2d.validate_fractal_runtime_g2_d_report_v02(report)
        if reasons:
            raise ValueError
        return _fractal_runtime_gauntlet_act_from_validated_report_v01(report)
    except Exception:
        return _fractal_runtime_gauntlet_act_from_validated_report_v01(None)


_G2E_ZERO_COUNTER_FIELDS_V16 = (
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


def _validated_e5_receipt_v01(
    report: object,
) -> tuple[_g2e.ContinuousDeltaRuntimeG2EReportV01, str, int]:
    validated = _g2e.validate_continuous_delta_runtime_g2_e_report_v01(report)
    canonical_bytes = _g2e.render_continuous_delta_runtime_g2_e_v01(
        validated
    ).encode("utf-8")
    return validated, hashlib.sha256(canonical_bytes).hexdigest(), len(canonical_bytes)


def _continuous_delta_runtime_report_passes_living_act_v01(
    report: object,
) -> bool:
    try:
        validated = _g2e.validate_continuous_delta_runtime_g2_e_report_v01(
            report
        )
        return (
            validated.report_version == _g2e.REPORT_VERSION
            and validated.profile_id == _g2e.PROFILE_ID
            and validated.domain_order
            == (
                "TRAVEL_POLICY_INFORMATION",
                "WAREHOUSE_MAINTENANCE_INFORMATION",
            )
            and validated.case_order
            == tuple(item.case_id for item in validated.case_results)
            and len(validated.case_results) == 100
            and validated.constructive_case_count == 10
            and validated.negative_case_count == 90
            and validated.total_case_count == 100
            and validated.accepted_baseline_bundle_count == 2
            and validated.explicit_public_g2d_baseline_call_count == 2
            and validated.final_status == STATUS_PASS
            and validated.reason_codes == ()
            and type(validated.sealed_evidence_sha256) is str
            and len(validated.sealed_evidence_sha256) == 64
            and set(validated.sealed_evidence_sha256)
            <= set("0123456789abcdef")
            and all(
                getattr(validated, field) == 0
                for field in _G2E_ZERO_COUNTER_FIELDS_V16
            )
            and all(
                item.expected_outcome == item.observed_outcome
                and item.expected_reason_codes == item.observed_reason_codes
                and item.final_status == STATUS_PASS
                and item.reason_codes == ()
                and type(item.evidence_material_json) is str
                and bool(item.evidence_material_json)
                and type(item.evidence_sha256) is str
                and len(item.evidence_sha256) == 64
                and set(item.evidence_sha256) <= set("0123456789abcdef")
                and all(
                    getattr(item, field) == 0
                    for field in _G2E_ZERO_COUNTER_FIELDS_V16
                )
                and all(
                    subcase.expected_reason_codes
                    == subcase.observed_reason_codes
                    and subcase.final_status == STATUS_PASS
                    and type(subcase.evidence_sha256) is str
                    and len(subcase.evidence_sha256) == 64
                    and set(subcase.evidence_sha256)
                    <= set("0123456789abcdef")
                    for subcase in item.subcase_results
                )
                for item in validated.case_results
            )
        )
    except Exception:
        return False


def _continuous_delta_runtime_gauntlet_act_from_validated_report_v01(
    report: object,
) -> LivingGauntletActResultV01:
    act_id = "continuous_delta_runtime"
    source_module, source_symbol = _ACTIVE_ACT_SOURCES[act_id]
    if _continuous_delta_runtime_report_passes_living_act_v01(report):
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
    return LivingGauntletActResultV01(
        act_id=act_id,
        errors=("continuous_delta_runtime_gauntlet_act_failed",),
        executed=True,
        no_real_connector_or_action=False,
        real_world_effects_count=-1,
        root_authority_preserved=False,
        runtime_status=STATUS_FAIL_CLOSED,
        source_module=source_module,
        source_symbol=source_symbol,
        state=STATUS_FAIL_CLOSED,
    )


def collect_continuous_delta_runtime_gauntlet_act_v01(
) -> LivingGauntletActResultV01:
    try:
        report = _g2e.collect_continuous_delta_runtime_g2_e_v01()
        report, _sha256, _byte_count = _validated_e5_receipt_v01(report)
        return _continuous_delta_runtime_gauntlet_act_from_validated_report_v01(
            report
        )
    except Exception:
        return _continuous_delta_runtime_gauntlet_act_from_validated_report_v01(
            None
        )


def collect_living_gauntlet_base_act_results_v01(
) -> tuple[dict[str, object], ...]:
    collectors = (
        (
            "airline_deterministic_transaction_runtime",
            lambda: _airline_act_result(
                collect_tri_party_airline_ticket_purchase_mock_e2e_v01()
            ),
            "airline_collector_failed",
        ),
        (
            "generic_integrity_replay",
            collect_generic_integrity_replay_gauntlet_act_v01,
            "generic_integrity_replay_collector_failed",
        ),
        (
            "root_signer_isolation_conformance",
            collect_root_signer_isolation_gauntlet_act_v01,
            "root_signer_isolation_collector_failed",
        ),
        (
            "semantic_work_contract",
            collect_semantic_work_contract_gauntlet_act_v01,
            "semantic_work_contract_collector_failed",
        ),
        (
            "domain_neutral_kernel_abi",
            collect_domain_neutral_kernel_abi_gauntlet_act_v01,
            "domain_neutral_kernel_abi_collector_failed",
        ),
        (
            "causal_consumption",
            collect_causal_consumption_gauntlet_act_v01,
            "causal_consumption_collector_failed",
        ),
        (
            "transition_registry",
            collect_transition_registry_gauntlet_act_v01,
            "transition_registry_collector_failed",
        ),
        (
            "root_decision_kernel",
            collect_root_decision_kernel_gauntlet_act_v01,
            "root_decision_kernel_collector_failed",
        ),
        (
            "effect_firewall",
            collect_effect_firewall_gauntlet_act_v01,
            "effect_firewall_collector_failed",
        ),
        (
            "generic_multiroot",
            collect_generic_multiroot_gauntlet_act_v01,
            "generic_multiroot_collector_failed",
        ),
        (
            "supplier_water_filter_portability",
            collect_supplier_water_filter_portability_gauntlet_act_v01,
            "supplier_water_filter_collector_failed",
        ),
    )
    results: list[dict[str, object]] = []
    for act_id, collector, failure_reason in collectors:
        try:
            result = collector()
        except Exception:
            result = _failed_act_result(act_id=act_id, reason=failure_reason)
        results.append(asdict(result))
    return tuple(results)


def _collect_kernel_conformance_closure_from_validated_fractal_runtime_v01(
    active_act_results: tuple[Mapping[str, object], ...],
    fractal_runtime_report: _g2d.FractalRuntimeG2DReportV02,
    continuous_delta_runtime_report: _g2e.ContinuousDeltaRuntimeG2EReportV01,
    continuous_delta_runtime_report_sha256: str,
    continuous_delta_runtime_report_bytes: int,
) -> LivingGauntletActResultV01:
    act_id = "kernel_conformance_closure"
    source_module, source_symbol = _ACTIVE_ACT_SOURCES[act_id]
    try:
        report = _collect_kernel_conformance_with_validated_fractal_runtime_v01(
            active_act_results=active_act_results,
            implementation_commit=resolve_current_implementation_commit_v01(),
            fractal_runtime_report=fractal_runtime_report,
            continuous_delta_runtime_report=continuous_delta_runtime_report,
            continuous_delta_runtime_report_sha256=(
                continuous_delta_runtime_report_sha256
            ),
            continuous_delta_runtime_report_bytes=(
                continuous_delta_runtime_report_bytes
            ),
        )
        validation_errors = validate_kernel_conformance_runtime_v01(report)
        counters = report.counters
        passed = (
            not validation_errors
            and report.final_status == STATUS_PASS
            and report.profile_id == KERNEL_CONFORMANCE_PROFILE_V07_CURRENT
            and report.conformance_version == "v0.7"
            and report.historical_profile_ref
            == KERNEL_CONFORMANCE_PROFILE_V06_HISTORICAL
            and report.claim_to_current_act
            == CURRENT_REGRESSION_CLAIM_TO_ACTS_V07
            and report.current_act_count
            == len(CURRENT_KERNEL_CONFORMANCE_ACTIVE_REFS_V07)
            and len(report.category_results) == 15
            and len(report.domain_results) == 2
            and len(report.negative_test_results) == 60
            and report.active_gauntlet_refs
            == CURRENT_KERNEL_CONFORMANCE_ACTIVE_REFS_V07
            and report.continuous_delta_runtime_execution_count == 1
            and report.continuous_delta_runtime_public_validation_status
            == STATUS_PASS
            and report.continuous_delta_runtime_report_sha256
            == continuous_delta_runtime_report_sha256
            and report.continuous_delta_runtime_report_bytes
            == continuous_delta_runtime_report_bytes
            and report.shared_conformance_e5_collector_calls == 0
            and report.shared_conformance_e5_report_sha256
            == continuous_delta_runtime_report_sha256
            and report.shared_conformance_e5_report_bytes
            == continuous_delta_runtime_report_bytes
            and all(item.status == STATUS_PASS for item in report.category_results)
            and all(item.status == STATUS_PASS for item in report.domain_results)
            and all(
                item.status == STATUS_PASS for item in report.negative_test_results
            )
            and "supplier_multiroot_mixed_visible"
            in report.domain_results[1].passed_check_ids
            and all(
                value == 0
                for value in (
                    counters.provider_call_count,
                    counters.network_call_count,
                    counters.gemini_call_count,
                    counters.created_authority_count,
                    counters.created_permission_count,
                    counters.real_world_effects_count,
                )
            )
        )
        if not passed:
            raise ValueError("kernel_conformance_closure_failed")
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
            errors=("kernel_conformance_closure_failed",),
            executed=True,
            no_real_connector_or_action=False,
            real_world_effects_count=-1,
            root_authority_preserved=False,
            runtime_status=STATUS_FAIL_CLOSED,
            source_module=source_module,
            source_symbol=source_symbol,
            state=STATUS_FAIL_CLOSED,
        )


def collect_kernel_conformance_closure_gauntlet_act_v01(
    active_act_results: tuple[Mapping[str, object], ...],
) -> LivingGauntletActResultV01:
    try:
        fractal_runtime_report = _g2d.collect_fractal_runtime_g2_d_v02()
        reasons = _g2d.validate_fractal_runtime_g2_d_report_v02(
            fractal_runtime_report
        )
        if reasons:
            raise ValueError
        continuous_delta_runtime_report = (
            _g2e.collect_continuous_delta_runtime_g2_e_v01()
        )
        continuous_delta_runtime_report, e5_sha256, e5_bytes = (
            _validated_e5_receipt_v01(continuous_delta_runtime_report)
        )
        e5_act = _continuous_delta_runtime_gauntlet_act_from_validated_report_v01(
            continuous_delta_runtime_report
        )
        rows = active_act_results
        if tuple(row.get("act_id") for row in rows) == (
            HISTORICAL_KERNEL_CONFORMANCE_ACTIVE_REFS_V06
        ):
            rows = (*rows, asdict(e5_act))
        return _collect_kernel_conformance_closure_from_validated_fractal_runtime_v01(
            rows,
            fractal_runtime_report,
            continuous_delta_runtime_report,
            e5_sha256,
            e5_bytes,
        )
    except Exception:
        return _failed_act_result(
            act_id="kernel_conformance_closure",
            reason="kernel_conformance_closure_failed",
        )


_U4_REGISTRATION_KEY = "universality_current_registration_v01"
_U4_H = "20d16af823ed4af94dc0a342c731aef81e8a23de"
_U4_REGISTRATION_ROWS = ({'seam_id': 'native_action_packet',
  'producer': 'hedgehog.action_commit_packet_v02:build_native_root_bound_action_commit_packet_v01',
  'validator': 'hedgehog.action_commit_packet_v02:validate_native_root_bound_action_commit_packet_v01',
  'consumer': 'hedgehog.kernel.effect_firewall_v01:bind_native_action_authorization_v01',
  'source_sha256': 'b38c9e134a13caa5a0f65e0ede3faba6f3fa6dbff32761398927df8b5d903110',
  'focused_evidence': 'tests/test_action_packet_portability_v01.py',
  'status': 'CURRENT_BOUNDED_IMPLEMENTATION',
  'authority': 'EVIDENCE_ONLY',
  'effect_access': 'NONE'},
 {'seam_id': 'native_action_current_dispatch',
  'producer': 'hedgehog.work_execution_host_v01:dispatch_current_action_v01',
  'validator': 'hedgehog.kernel.effect_firewall_v01:validate_native_effect_receipt_v01',
  'consumer': 'hedgehog.kernel.effect_firewall_v01:execute_bound_effect_v01',
  'source_sha256': 'c54b0204c4f664dfd234db26f29cf7164baf803780b69af0a57fb9397ca9bd25',
  'focused_evidence': 'tests/test_action_packet_portability_v01.py',
  'status': 'CURRENT_BOUNDED_IMPLEMENTATION',
  'authority': 'EVIDENCE_ONLY',
  'effect_access': 'NONE'},
 {'seam_id': 'work_composition',
  'producer': 'hedgehog.kernel.work_composition_v01:materialize_work_program_v01',
  'validator': 'hedgehog.kernel.work_composition_v01:validate_work_program_candidate_v01',
  'consumer': 'hedgehog.kernel.work_composition_v01:validate_work_program_result_v01',
  'source_sha256': 'f4085174a6cdfcb9a0c9983854a26c32625f4a811b2e1c4b81888c28a83f6061',
  'focused_evidence': 'tests/test_work_composition_v01.py',
  'status': 'CURRENT_BOUNDED_IMPLEMENTATION',
  'authority': 'EVIDENCE_ONLY',
  'effect_access': 'NONE'},
 {'seam_id': 'same_task_continuation',
  'producer': 'hedgehog.kernel.work_composition_v01:revise_work_program_v01',
  'validator': 'hedgehog.kernel.work_composition_v01:validate_work_continuation_outcome_v01',
  'consumer': 'hedgehog.kernel.work_composition_v01:validate_work_program_result_v01',
  'source_sha256': 'f4085174a6cdfcb9a0c9983854a26c32625f4a811b2e1c4b81888c28a83f6061',
  'focused_evidence': 'tests/test_work_continuation_and_reuse_v01.py',
  'status': 'CURRENT_BOUNDED_IMPLEMENTATION',
  'authority': 'EVIDENCE_ONLY',
  'effect_access': 'NONE'},
 {'seam_id': 'pure_capability_admission',
  'producer': 'hedgehog.capability_admission_v01:admit_pure_candidate_v01',
  'validator': 'hedgehog.capability_admission_v01:validate_admitted_pure_package_v01',
  'consumer': 'hedgehog.capability_admission_v01:validate_pure_guest_evidence_v01',
  'source_sha256': '2261347c11f7535522653f0a2e301bed69cbbc5e0ef737bc4a37d2b9954b0cda',
  'focused_evidence': 'tests/test_capability_admission_v01.py',
  'status': 'CURRENT_BOUNDED_IMPLEMENTATION',
  'authority': 'EVIDENCE_ONLY',
  'effect_access': 'NONE'},
 {'seam_id': 'closed_pure_wasm_execution',
  'producer': 'hedgehog.wasm_pure_worker_v01:run_pure_wasm_worker_v01',
  'validator': 'hedgehog.wasm_pure_worker_v01:validate_closed_pure_wasm_v01',
  'consumer': 'hedgehog.capability_admission_v01:admit_pure_candidate_v01',
  'source_sha256': 'e9d727f3f971d5429fdffe25b0917548f2e903b63f1922a3bc60f9cb33e6d3ae',
  'focused_evidence': 'tests/test_capability_admission_v01.py',
  'status': 'CURRENT_BOUNDED_IMPLEMENTATION',
  'authority': 'EVIDENCE_ONLY',
  'effect_access': 'NONE'},
 {'seam_id': 'local_pure_capability_reuse',
  'producer': 'hedgehog.capability_memory_binding_v01:retrieve_pure_memory_v01',
  'validator': 'hedgehog.capability_memory_binding_v01:validate_pure_memory_retrieval_v01',
  'consumer': 'hedgehog.capability_admission_v01:admit_pure_candidate_v01',
  'source_sha256': '6e4f2ca3be12a1e9a93d7b59318d9a6ba90ea6f43bbd9bccc81d8bdefe1b1b79',
  'focused_evidence': 'tests/test_work_continuation_and_reuse_v01.py',
  'status': 'CURRENT_BOUNDED_IMPLEMENTATION',
  'authority': 'EVIDENCE_ONLY',
  'effect_access': 'NONE'},
 {'seam_id': 'retained_fractal_work',
  'producer': 'hedgehog.kernel.fractal_runtime_v02:consume_fractal_retained_work_v01',
  'validator': 'hedgehog.kernel.fractal_runtime_v02:validate_fractal_retained_work_consumption_v01',
  'consumer': 'hedgehog.kernel.continuous_delta_runtime_v01:validate_retained_work_preservation_v01',
  'source_sha256': 'e02ccdab45725de6f3091897b317eb93076717c7d3a107fafa99f657917ef8ca',
  'focused_evidence': 'tests/test_continuous_delta_runtime_g2_e_v01.py',
  'status': 'CURRENT_BOUNDED_IMPLEMENTATION',
  'authority': 'EVIDENCE_ONLY',
  'effect_access': 'NONE'},
 {'seam_id': 'retained_selective_recomputation',
  'producer': 'hedgehog.kernel.continuous_delta_runtime_v01:build_retained_selective_recomputation_plan_v01',
  'validator': 'hedgehog.kernel.continuous_delta_runtime_v01:validate_retained_selective_recomputation_plan_v01',
  'consumer': 'hedgehog.kernel.continuous_delta_runtime_v01:prove_retained_work_preservation_v01',
  'source_sha256': 'efb0ef689bde0efbbbbc5cddcc7e3d0237c5dacf05e7c1f6415e5d5d808bd282',
  'focused_evidence': 'tests/test_continuous_delta_runtime_g2_e_v01.py',
  'status': 'CURRENT_BOUNDED_IMPLEMENTATION',
  'authority': 'EVIDENCE_ONLY',
  'effect_access': 'NONE'})
_U4_FROZEN_SOURCES = {'demo/run_action_packet_portability_v01.py': '82be33d8420e4e106203898e709399230f6d7f64d4b8243e94269bec828f88cb',
 'demo/run_capability_cold_start_reuse_v01.py': '123714d89b7542abdba2c6d79e7a16ce98b5bd92810b032eccab3e82201f56ff',
 'demo/run_fractal_runtime_g2_d_v02.py': '9d1b0045de22b4b9482876f5e8a11b12bdc2f35191fa97d51540beb22fbe9d2a',
 'demo/run_kernel_conformance_v01.py': '4fe949a09653a72eef2b9a885254a29bd9be4cff018d155dacc816671d291f55',
 'demo/work_composition_mock_capabilities_v01.py': 'f02da370499fccddf88bb2dbdbd9fe6e2a33fa4143bf205a59770f9f84bb2731',
 'docs/common_action_and_dynamic_composition_contract_v01.md': '2776a5eaba4e87c71c2fc1e9af875c985147c8a4f47d24f91049cd8232b5befd',
 'docs/continuous_delta_runtime_v0_1_g2_e_post_acceptance_contract_addendum_v01.md': '5dcc7a28485ebd1d09075520fb290b858949fea6d64a4b76a8f927317ea3c369',
 'docs/fractal_runtime_v0_2_g2_d_post_acceptance_contract_addendum_v01.md': '4515e5e3e333ce9c00bc3696ddd1a478550414e45d379c7eacf726729d4940b6',
 'hedgehog/action_commit_packet_v02.py': 'b38c9e134a13caa5a0f65e0ede3faba6f3fa6dbff32761398927df8b5d903110',
 'hedgehog/capability_admission_v01.py': '2261347c11f7535522653f0a2e301bed69cbbc5e0ef737bc4a37d2b9954b0cda',
 'hedgehog/capability_memory_binding_v01.py': '6e4f2ca3be12a1e9a93d7b59318d9a6ba90ea6f43bbd9bccc81d8bdefe1b1b79',
 'hedgehog/kernel/continuous_delta_runtime_v01.py': 'efb0ef689bde0efbbbbc5cddcc7e3d0237c5dacf05e7c1f6415e5d5d808bd282',
 'hedgehog/kernel/effect_firewall_v01.py': '46a453e0ef98565f0de59ab062b307eff6549a716973268a034592a5f98463bd',
 'hedgehog/kernel/execution_mode_router_v01.py': '4b19de7348a15cd65f1bed02bd93d848ccc490b6c7b8fe21338c3784809f79c4',
 'hedgehog/kernel/fractal_runtime_v02.py': 'e02ccdab45725de6f3091897b317eb93076717c7d3a107fafa99f657917ef8ca',
 'hedgehog/kernel/work_composition_v01.py': 'f4085174a6cdfcb9a0c9983854a26c32625f4a811b2e1c4b81888c28a83f6061',
 'hedgehog/wasm_pure_worker_v01.py': 'e9d727f3f971d5429fdffe25b0917548f2e903b63f1922a3bc60f9cb33e6d3ae',
 'hedgehog/work_execution_host_v01.py': 'c54b0204c4f664dfd234db26f29cf7164baf803780b69af0a57fb9397ca9bd25',
 'pyproject.toml': '34feed08e3befc6a4bc4dfa53d69cf827e676e28a321d4770d2a39bec4772f73',
 'schemas/capability_admission_v01.schema.json': 'b09ac99cb2e62ffd95098401a5695a0f018d87d4f2e61f9de723f710ac7455e0',
 'schemas/continuous_delta_runtime_v01.schema.json': '9cdeb3d987241383360413d6a4a02be4a3a1480e840aa334737dccd25fddb3b5',
 'schemas/fractal_runtime_v02.schema.json': 'db4b5a232e945cea8a6167f36007963534b6852a5a9d53e81325912399d1fcf8',
 'schemas/work_composition_v01.schema.json': 'ac385c7202e39c88890d66fd148c85bfafe35e9c8f79ec9748866be39e6ba6a0',
 'tests/test_action_packet_portability_v01.py': 'af8dfe77d9750bad37d7e1e206195c5a9fc0913f1fef7e06d1ec70b8acc672c7',
 'tests/test_capability_admission_v01.py': '914aa8d7913ed4e40405cd6a6339e85ada4a7f41840b0e4b1e6e8c311751dda2',
 'tests/test_continuous_delta_runtime_g2_e_v01.py': '94dc6941ff6fc3f06dfb7f5f05ef1a55716ff359bd258439051f1226a911111f',
 'tests/test_effect_firewall_v01.py': 'c4cc287217a5cd680b3ea1105e23c6c845e0d8732c53855b7a585aec1a1fe1eb',
 'tests/test_execution_mode_router_g2_c_v01.py': 'e2fae99b3530be81fa8bf47027139bf3a23fda6b58a80b2bda9db21f5407b801',
 'tests/test_fractal_runtime_g2_d_v02.py': 'c853bc340337ae6410dbd8c8591f49b85a2b7cbf345563d77415656ea2b7d6c1',
 'tests/test_work_composition_v01.py': '599561099290cf50951b4768a5dfd338fef76a924e6887ebce25ca0e984ba7bc',
 'tests/test_work_continuation_and_reuse_v01.py': 'c283d1eb3920076311328a6922257a83672b0bef847e109bedfdcaa3b32d001f'}
_U4_BASE_IDENTITIES = {'release/completion_manifest.json': '4ae53a074dd49440c191928b10b390120cc97aa7c04f23c3ddc9771fd914d5b9', 'release/integration_seam_index.json': '4b0d65b84ca253b2a41b03777ae64a67f9ca048608b0d9648196129c1754fb03'}

_TESTFLIX_REGISTRATION_KEY_V11 = "testflix_current_registration_v11"
_TESTFLIX_L_V11 = "54e32dbcc0e4d68431ec2b9428eac965f88ee47c"
_TESTFLIX_SOURCE_UPDATES_V11 = {'demo/run_fractal_runtime_g2_d_v02.py': '6399913a0aaca15dc11476045fb514e6059e7d43ed012e0da539b3546a2a80a6',
 'demo/run_kernel_conformance_v01.py': 'fc4f919db78519f1f69f87a897989b88b6e125e41e85d22b28b6ba41432d4578',
 'docs/common_action_and_dynamic_composition_contract_v01.md': '7f747d14065c11e6194fce94aabcd107693e7d27cd75c5558c37cef0a0a3092d',
 'docs/continuous_delta_runtime_v0_1_g2_e_post_acceptance_contract_addendum_v01.md': '160676d9db97a68e09393c79287d1c860cbf30cd3aacf05f7760ef67a81ee518',
 'docs/fractal_runtime_v0_2_g2_d_post_acceptance_contract_addendum_v01.md': 'd5cd57769c417749927f163925bc214c9c61125ef98beb31f46c154616fbb5a2',
 'hedgehog/kernel/continuous_delta_runtime_v01.py': '879abad289ebae13b65cd0d2c5858e89f55fb059fecb111cde61d37f575a6af0',
 'hedgehog/kernel/fractal_runtime_v02.py': 'ac946801b15c7464dd228034f64f0849c9567a71328ba50f3df314fe433dd0ba',
 'hedgehog/work_execution_host_v01.py': '56b7ba85e8612df517d566418fa60a2512bcf9f6707877618a3d846010e6071b',
 'schemas/fractal_runtime_v02.schema.json': '95f81f4122e021d4cba1bd43e6ec8d337ccdb36af058e96ea1e7e3f2f6283df5',
 'tests/test_action_packet_portability_v01.py': 'c2179fc7c7fd9d293d3bdef20f8702ac07840024956abd0216d4fc38d2f37875',
 'tests/test_continuous_delta_runtime_g2_e_v01.py': '3bb3d6678ea5e016dc6fd2b2ef825148c5198db3e7dce3b114577cd12b2a3c4d',
 'tests/test_fractal_runtime_g2_d_v02.py': 'a456769d2b89c7aa7f14ef8332bab40ddfc007bbf3c2b201288539189889dfad',
 'tests/test_work_composition_v01.py': '62c9b9f5769aa447ec858b3b40fe6c346499e058db0546efd3f539a73222396c'}
_TESTFLIX_FROZEN_SOURCES_V11 = {**_U4_FROZEN_SOURCES, **_TESTFLIX_SOURCE_UPDATES_V11}
_TESTFLIX_REGISTRATION_ROWS_V11 = tuple(
    {**row, "source_sha256": _TESTFLIX_FROZEN_SOURCES_V11[row["producer"].split(":")[0].replace(".", "/") + ".py"]}
    for row in _U4_REGISTRATION_ROWS
)


_EWS_REGISTRATION_KEY_V01 = "ephemeral_workspace_current_registration_v01"
_EWS_BASE_V01 = "e42d37fa98dfec7110b8cf75b1aceaa614f461be"
_EWS_FROZEN_SOURCES_V01 = {
    **_TESTFLIX_FROZEN_SOURCES_V11,
    "hedgehog/action_commit_packet_v02.py": "e24b8c4bd3284c4b9db8944e2a9c268d26816956880ffb0700700bbf3fdc59ac",
    "pyproject.toml": "b9d0ba6c3ef5aba0e75882a5c7501c4ac3631b9ccf8559f17ed73ce34a8efea0",
}
_EWS_REGISTRATION_ROWS_V01 = tuple(
    {**row, "source_sha256": _EWS_FROZEN_SOURCES_V01[row["producer"].split(":")[0].replace(".", "/") + ".py"]}
    for row in _U4_REGISTRATION_ROWS
)


def _current_registration_v01(root: Path) -> tuple[dict[str, Any] | None, tuple[str, ...]]:
    """Read current registration as evidence, never dispatch metadata symbols."""
    import ast
    import subprocess

    errors: list[str] = []
    try:
        overlay = _load_strict_json_object(root / "release/current_status_overlay_v01.json")
        ews = _EWS_REGISTRATION_KEY_V01 in overlay
        testflix = _TESTFLIX_REGISTRATION_KEY_V11 in overlay
        block = overlay.get(_EWS_REGISTRATION_KEY_V01 if ews else _TESTFLIX_REGISTRATION_KEY_V11 if testflix else _U4_REGISTRATION_KEY)
        sources = _EWS_FROZEN_SOURCES_V01 if ews else _TESTFLIX_FROZEN_SOURCES_V11 if testflix else _U4_FROZEN_SOURCES
        rows = _EWS_REGISTRATION_ROWS_V01 if ews else _TESTFLIX_REGISTRATION_ROWS_V11 if testflix else _U4_REGISTRATION_ROWS
        if block is None:
            # A missing block is historical only with the entire exact H tree.
            head = subprocess.check_output(("git", "rev-parse", "HEAD"), cwd=root).decode().strip()
            if head != _U4_H:
                return None, ("registration_missing_current",)
            tree = subprocess.check_output(("git", "ls-tree", "-rz", _U4_H), cwd=root)
            entries = tree.split(b"\0")[:-1]
            if len(entries) != 912:
                return None, ("registration_historical_tree",)
            for item in entries:
                metadata, name = item.split(b"\t")
                mode, kind, oid = metadata.decode().split()
                path = root / name.decode()
                if path.is_symlink() or not path.is_file():
                    return None, ("registration_historical_source",)
                b = path.read_bytes()
                actual = hashlib.sha1(b"blob " + str(len(b)).encode() + b"\0" + b).hexdigest()
                if kind != "blob" or oid != actual or bool(path.stat().st_mode & 0o111) != (mode == "100755"):
                    return None, ("registration_missing_current",)
            if any((root / p).exists() for p in _U4_FROZEN_SOURCES if p not in {e.split(b"\t")[1].decode() for e in entries}):
                return None, ("registration_missing_current",)
            return None, ()
        expected = {
            "profile": "EPHEMERAL_WORKSPACE_ADMISSION_V01" if ews else "TESTFLIX_TEMPORAL_IMPLEMENTATION_ADMISSION_V11" if testflix else "U1_U4_BOUNDED_IMPLEMENTATION_ADMISSION_V01",
            "basis": _EWS_BASE_V01 if ews else _TESTFLIX_L_V11 if testflix else _U4_H,
            "status": "EXACT_SOURCE_ADMISSION_DERIVED_FROM_GIT" if ews else "IMPLEMENTED_REGISTRATION_CANDIDATE_OWNER_ACCEPTANCE_PENDING",
            "authority": "EVIDENCE_ONLY_NO_ROOT_OR_EFFECT_HANDLE",
            "base_identities": _U4_BASE_IDENTITIES,
            "frozen_source_identities": sources,
            "rows": list(rows),
            "schema_paths": ["schemas/work_composition_v01.schema.json", "schemas/capability_admission_v01.schema.json"],
        }
        if block != expected:
            errors.append("registration_exact_block")
        for path, digest in {**_U4_BASE_IDENTITIES, **sources}.items():
            file = root / path
            if file.is_symlink() or not file.is_file() or hashlib.sha256(file.read_bytes()).hexdigest() != digest:
                errors.append("registration_source:" + path)
        schema = _load_strict_json_object(root / "release/current_schema_surface_v01.json")
        base_schema = json.loads(subprocess.check_output(("git", "show", _U4_H + ":release/current_schema_surface_v01.json"), cwd=root))
        if schema.get("current_schema_paths") != sorted(base_schema["current_schema_paths"] + expected["schema_paths"]):
            errors.append("registration_schema_inventory")
        for row in rows:
            for key in ("producer", "validator", "consumer"):
                module, symbol = row[key].split(":")
                path = module.replace(".", "/") + ".py"
                if path not in sources:
                    errors.append("registration_module:" + path)
                    continue
                tree = ast.parse((root / path).read_bytes())
                if symbol not in {n.name for n in tree.body if isinstance(n, ast.FunctionDef)}:
                    errors.append("registration_symbol:" + row[key])
        return block, tuple(dict.fromkeys(errors))
    except (OSError, ValueError, TypeError, KeyError, subprocess.SubprocessError) as exc:
        return None, ("registration_load:" + type(exc).__name__,)


def collect_living_gauntlet_v01() -> dict[str, Any]:
    try:
        continuous_delta_runtime_report = (
            _g2e.collect_continuous_delta_runtime_g2_e_v01()
        )
    except Exception:
        continuous_delta_runtime_report = None
    return _collect_living_gauntlet_with_validated_continuous_delta_runtime_v01(
        continuous_delta_runtime_report
    )


def _collect_living_gauntlet_with_validated_continuous_delta_runtime_v01(
    continuous_delta_runtime_report: object,
) -> dict[str, Any]:
    errors: list[str] = []
    e5_sha256 = ""
    e5_bytes = 0
    e5_collection_failed = False
    try:
        (
            continuous_delta_runtime_report,
            e5_sha256,
            e5_bytes,
        ) = _validated_e5_receipt_v01(continuous_delta_runtime_report)
        e5 = _continuous_delta_runtime_gauntlet_act_from_validated_report_v01(
            continuous_delta_runtime_report
        )
    except Exception:
        continuous_delta_runtime_report = None
        e5_collection_failed = True
        e5 = _continuous_delta_runtime_gauntlet_act_from_validated_report_v01(
            None
        )
    current_registration, registration_errors = _current_registration_v01(_REPOSITORY_ROOT)
    errors.extend(registration_errors)
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

    active_result_rows: list[dict[str, object]] = []
    if not errors:
        try:
            base_results = collect_living_gauntlet_base_act_results_v01()
        except Exception:
            base_results = ()
            errors.append("living_base_collection_failed")
        if base_results:
            try:
                lifecycle = collect_action_packet_lifecycle_gauntlet_act_v01()
            except Exception:
                lifecycle = _failed_act_result(
                    act_id="action_packet_lifecycle",
                    reason="action_packet_lifecycle_gauntlet_act_failed",
                )
            try:
                g2b = (
                    collect_drs_semantic_address_and_reuse_certificate_gauntlet_act_v01()
                )
            except Exception:
                g2b = _failed_act_result(
                    act_id="drs_semantic_address_and_reuse_certificate",
                    reason=(
                        "drs_semantic_address_reuse_certificate_"
                        "gauntlet_act_failed"
                    ),
                )
            try:
                g2c = collect_execution_mode_router_gauntlet_act_v01()
            except Exception:
                g2c = _failed_act_result(
                    act_id="execution_mode_router",
                    reason="execution_mode_router_gauntlet_act_failed",
                )
            fractal_runtime_report = None
            try:
                candidate = _g2d.collect_fractal_runtime_g2_d_v02()
                reasons = _g2d.validate_fractal_runtime_g2_d_report_v02(
                    candidate
                )
                if reasons:
                    raise ValueError
                fractal_runtime_report = candidate
                g2d = _fractal_runtime_gauntlet_act_from_validated_report_v01(
                    candidate
                )
            except Exception:
                g2d = _fractal_runtime_gauntlet_act_from_validated_report_v01(
                    None
                )
            closure_inputs = (
                *base_results,
                asdict(lifecycle),
                asdict(g2b),
                asdict(g2c),
                asdict(g2d),
                asdict(e5),
            )
            if (
                fractal_runtime_report is None
                or continuous_delta_runtime_report is None
            ):
                closure = _failed_act_result(
                    act_id="kernel_conformance_closure",
                    reason="kernel_conformance_closure_failed",
                )
            else:
                closure = (
                    _collect_kernel_conformance_closure_from_validated_fractal_runtime_v01(
                        closure_inputs,
                        fractal_runtime_report,
                        continuous_delta_runtime_report,
                        e5_sha256,
                        e5_bytes,
                    )
                )
            active_result_rows.extend(dict(row) for row in base_results)
            active_result_rows.append(asdict(closure))
            active_result_rows.append(asdict(lifecycle))
            active_result_rows.append(asdict(g2b))
            active_result_rows.append(asdict(g2c))
            active_result_rows.append(asdict(g2d))
            active_result_rows.append(asdict(e5))

    if e5_collection_failed:
        errors.append("continuous_delta_runtime_collection_failed")
    for result in active_result_rows:
        row_errors = result.get("errors")
        if type(row_errors) is tuple:
            errors.extend(row_errors)
    evidence_entries = [
        {
            "act_id": record["act_id"],
            "evidence_paths": list(record["evidence_paths"]),
            "executed": False,
            "state": record.get("status", STATUS_EVIDENCE_ONLY),
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
        result.get("state") == STATUS_PASS for result in active_result_rows
    )
    index_valid = not any(
        error.startswith(("completion_manifest", "integration_seam", "active_act", "evidence_", "planned_act", "public_claim", "current_seam", "planned_seam", "seam_", "effect_firewall", "root_authority_seam"))
        for error in errors
    )
    invariants = [
        _invariant_result("release_indexes_valid", index_valid),
        _invariant_result(
            "all_active_acts_executed_once",
            tuple(result.get("act_id") for result in active_result_rows)
            == _ACTIVE_ACT_IDS
            and all(result.get("executed") is True for result in active_result_rows),
        ),
        _invariant_result(
            "all_active_acts_pass",
            active_pass_count == len(_ACTIVE_ACT_IDS),
        ),
        _invariant_result(
            "root_authority_preserved",
            bool(active_result_rows)
            and all(
                result.get("root_authority_preserved") is True
                for result in active_result_rows
            ),
        ),
        _invariant_result(
            "real_world_effects_zero",
            bool(active_result_rows)
            and all(
                result.get("real_world_effects_count") == 0
                for result in active_result_rows
            ),
        ),
        _invariant_result(
            "no_real_connector_or_action",
            bool(active_result_rows)
            and all(
                result.get("no_real_connector_or_action") is True
                for result in active_result_rows
            ),
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
        _invariant_result(
            "action_packet_lifecycle_act_pass",
            len(active_result_rows) == len(_ACTIVE_ACT_IDS)
            and active_result_rows[-5].get("act_id")
            == "action_packet_lifecycle"
            and active_result_rows[-5].get("state") == STATUS_PASS,
        ),
        _invariant_result(
            "drs_semantic_address_reuse_certificate_act_pass",
            len(active_result_rows) == len(_ACTIVE_ACT_IDS)
            and active_result_rows[-4].get("act_id")
            == "drs_semantic_address_and_reuse_certificate"
            and active_result_rows[-4].get("state") == STATUS_PASS,
        ),
        _invariant_result(
            "execution_mode_router_act_pass",
            len(active_result_rows) == len(_ACTIVE_ACT_IDS)
            and active_result_rows[-3].get("act_id")
            == "execution_mode_router"
            and active_result_rows[-3].get("state") == STATUS_PASS,
        ),
        _invariant_result(
            "fractal_runtime_act_pass",
            len(active_result_rows) == len(_ACTIVE_ACT_IDS)
            and active_result_rows[-2].get("act_id") == "fractal_runtime"
            and active_result_rows[-2].get("state") == STATUS_PASS,
        ),
        _invariant_result(
            "continuous_delta_runtime_act_pass",
            len(active_result_rows) == len(_ACTIVE_ACT_IDS)
            and active_result_rows[-1].get("act_id")
            == "continuous_delta_runtime"
            and active_result_rows[-1].get("state") == STATUS_PASS,
        ),
    ]
    for invariant in invariants:
        if invariant["state"] != STATUS_PASS:
            errors.append(f"invariant_failed:{invariant['invariant_id']}")
    counters = _derive_report_counters_v01(
        active_result_rows,
        evidence_entries,
        planned_entries,
    )
    final_status = STATUS_PASS if not errors else STATUS_FAIL_CLOSED
    report: dict[str, Any] = {
        "current_registration": current_registration,
        "runner_id": RUNNER_ID,
        "runner_version": RUNNER_VERSION,
        "kernel_conformance_profile": KERNEL_CONFORMANCE_PROFILE_V07_CURRENT,
        "historical_kernel_conformance_profile": (
            KERNEL_CONFORMANCE_PROFILE_V06_HISTORICAL
        ),
        "current_regression_claim_mapping": {
            claim_id: list(act_ids)
            for claim_id, act_ids in CURRENT_REGRESSION_CLAIM_TO_ACTS_V07
        },
        "continuous_delta_runtime_execution_count": 1,
        "continuous_delta_runtime_public_validation_status": (
            STATUS_PASS
            if continuous_delta_runtime_report is not None
            else STATUS_FAIL_CLOSED
        ),
        "continuous_delta_runtime_report_sha256": e5_sha256,
        "continuous_delta_runtime_report_bytes": e5_bytes,
        "shared_conformance_e5_collector_calls": 0,
        "shared_conformance_e5_report_sha256": e5_sha256,
        "shared_conformance_e5_report_bytes": e5_bytes,
        "continuous_delta_runtime_second_execution_count": 0,
        "continuous_delta_runtime_cache_reuse_count": 0,
        "continuous_delta_runtime_test_fixture_substitution_count": 0,
        "continuous_delta_runtime_private_g2d_calls": 0,
        "continuous_delta_runtime_reconstructed_case_count": 0,
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
    report_errors = validate_living_gauntlet_report_v01(report)
    if report_errors:
        report["validation_errors"] = tuple(
            dict.fromkeys((*report["validation_errors"], *report_errors))
        )
        report["final_status"] = STATUS_FAIL_CLOSED
    return report


def validate_living_gauntlet_report_v01(
    report: Any,
) -> tuple[str, ...]:
    errors: list[str] = []
    if not isinstance(report, Mapping):
        return ("living_gauntlet_report_not_mapping",)
    current_registration, registration_errors = _current_registration_v01(_REPOSITORY_ROOT)
    errors.extend(registration_errors)
    if report.get("current_registration") != current_registration:
        errors.append("report_current_registration_mismatch")
    required_fields = {
        "current_registration",
        "runner_id",
        "runner_version",
        "kernel_conformance_profile",
        "historical_kernel_conformance_profile",
        "current_regression_claim_mapping",
        "continuous_delta_runtime_execution_count",
        "continuous_delta_runtime_public_validation_status",
        "continuous_delta_runtime_report_sha256",
        "continuous_delta_runtime_report_bytes",
        "shared_conformance_e5_collector_calls",
        "shared_conformance_e5_report_sha256",
        "shared_conformance_e5_report_bytes",
        "continuous_delta_runtime_second_execution_count",
        "continuous_delta_runtime_cache_reuse_count",
        "continuous_delta_runtime_test_fixture_substitution_count",
        "continuous_delta_runtime_private_g2d_calls",
        "continuous_delta_runtime_reconstructed_case_count",
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
    if (
        report.get("kernel_conformance_profile")
        != KERNEL_CONFORMANCE_PROFILE_V07_CURRENT
    ):
        errors.append("living_gauntlet_current_profile_mismatch")
    if (
        report.get("historical_kernel_conformance_profile")
        != KERNEL_CONFORMANCE_PROFILE_V06_HISTORICAL
    ):
        errors.append("living_gauntlet_historical_profile_mismatch")
    expected_claim_mapping = {
        claim_id: list(act_ids)
        for claim_id, act_ids in CURRENT_REGRESSION_CLAIM_TO_ACTS_V07
    }
    if report.get("current_regression_claim_mapping") != expected_claim_mapping:
        errors.append("living_gauntlet_claim_mapping_mismatch")
    e5_sha256 = report.get("continuous_delta_runtime_report_sha256")
    shared_e5_sha256 = report.get("shared_conformance_e5_report_sha256")
    e5_bytes = report.get("continuous_delta_runtime_report_bytes")
    shared_e5_bytes = report.get("shared_conformance_e5_report_bytes")
    if (
        report.get("continuous_delta_runtime_execution_count") != 1
        or report.get("continuous_delta_runtime_public_validation_status")
        != STATUS_PASS
        or not isinstance(e5_sha256, str)
        or len(e5_sha256) != 64
        or not set(e5_sha256) <= set("0123456789abcdef")
        or shared_e5_sha256 != e5_sha256
        or not isinstance(e5_bytes, int)
        or isinstance(e5_bytes, bool)
        or e5_bytes <= 0
        or shared_e5_bytes != e5_bytes
        or report.get("shared_conformance_e5_collector_calls") != 0
        or report.get("continuous_delta_runtime_second_execution_count") != 0
        or report.get("continuous_delta_runtime_cache_reuse_count") != 0
        or report.get("continuous_delta_runtime_test_fixture_substitution_count")
        != 0
        or report.get("continuous_delta_runtime_private_g2d_calls") != 0
        or report.get("continuous_delta_runtime_reconstructed_case_count") != 0
    ):
        errors.append("living_gauntlet_e5_receipt_invalid")
    version_geometry = _LIVING_VERSION_GEOMETRY.get(
        report.get("runner_version")
    )
    if version_geometry is None:
        errors.append("living_gauntlet_runner_version_mismatch")
        expected_active_ids = _ACTIVE_ACT_IDS
        expected_active_sources = _ACTIVE_ACT_SOURCES
        expected_counter_fields = _COUNTER_FIELD_NAMES
    else:
        (
            expected_active_ids,
            expected_active_sources,
            expected_counter_fields,
        ) = version_geometry
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
    if active_ids != expected_active_ids:
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
            expected_source = expected_active_sources.get(act_id)
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
            expected_state = (
                STATUS_HISTORICAL_EVIDENCE_ONLY
                if entry.get("act_id") in _HISTORICAL_EVIDENCE_ACT_IDS
                else STATUS_EVIDENCE_ONLY
            )
            if entry.get("state") != expected_state:
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
        if frozenset(counters) != expected_counter_fields:
            errors.append("report_counter_field_surface_mismatch")
        derived_counters = _derive_report_counters_v01(
            active,
            evidence,
            planned,
            active_ids=expected_active_ids,
            counter_field_names=expected_counter_fields,
        )
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
    return tuple(dict.fromkeys(errors))


def render_living_gauntlet_v01(report: Mapping[str, Any]) -> str:
    lines = [
        f"living_gauntlet: {report['runner_id']} {report['runner_version']}",
        f"kernel_conformance_profile={report['kernel_conformance_profile']}",
        "historical_kernel_conformance_profile="
        f"{report['historical_kernel_conformance_profile']}",
        "continuous_delta_runtime_report_sha256="
        f"{report['continuous_delta_runtime_report_sha256']}",
        "continuous_delta_runtime_report_bytes="
        f"{report['continuous_delta_runtime_report_bytes']}",
        "shared_conformance_e5_collector_calls="
        f"{report['shared_conformance_e5_collector_calls']}",
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
