#!/usr/bin/env python3
"""Validate the active Hedgehog OS document/onboarding authority boundary."""

from __future__ import annotations

import argparse
import ast
import fnmatch
import hashlib
import json
from pathlib import Path, PurePosixPath
import re
import subprocess
from typing import Iterable, Sequence


BASE_HEAD = "931645dc724c54d635f32dabfca4b62fbc9a39a2"
E5_IMPLEMENTATION_BASIS_COMMIT = "f582701208b603463a03d404aa841c302a8221d6"
G2E_CLASS_A_COMMIT = "7f3c7138b553096252fefee7930f89100d835fcd"
G2E_CLASS_B_COMMIT = "4c133da11b8bcbd642e1aaa3413ce0a9c357731d"
G2E_CLOSURE_BASIS_COMMIT = "6079ddcfe59f582936e7b13af2753a6533117970"
G2E_CLOSURE_COMMIT = "282e319241946b34987b2533d95ed514c3d884c1"
LOCK_PATH = "specs/current_architecture_lock_v01.md"
INDEX_PATH = "specs/document_authority_index_v01.json"
MANIFEST_PATH = "release/successor_context_manifest_v01.json"
G2E_AUDIT_PATH = (
    "docs/audit_reports/auditor_continuous_delta_runtime_g2_e_v01.log"
)
G2E_CHECKPOINT_PATH = (
    "docs/continuous_delta_runtime_v0_1_g2_e_checkpoint_v01.md"
)
E6_RECONCILIATION_ANNEX_PATH = (
    "docs/continuous_delta_runtime_v0_1_"
    "g2_e6_sanitized_basis_reconciliation_addendum_v01.md"
)
RETIRED_INVENTORY_PATH = "release/retired_architecture_inventory_v01.json"
CURRENT_SCHEMA_SURFACE_PATH = "release/current_schema_surface_v01.json"
COMPLETION_MANIFEST_PATH = "release/completion_manifest.json"
SEAM_INDEX_PATH = "release/integration_seam_index.json"
CONFORMANCE_SOURCE_PATH = "hedgehog/kernel/conformance_v01.py"
KERNEL_CONFORMANCE_RUNNER_PATH = "demo/run_kernel_conformance_v01.py"
LIVING_GAUNTLET_PATH = "demo/run_living_gauntlet_v01.py"
LIVING_GAUNTLET_TEST_PATH = "tests/test_living_gauntlet_v01_runner.py"
KERNEL_CONFORMANCE_TEST_PATH = "tests/test_kernel_conformance_v01_runner.py"
G2F_PREFLIGHT_PATH = "docs/consolidated_gate2_gauntlet_g2_f_preflight_v01.md"
G2F_RUNNER_PATH = "demo/run_consolidated_gate2_gauntlet_g2_f_v01.py"
G2F_TEST_PATH = "tests/test_consolidated_gate2_gauntlet_g2_f_v01.py"
G2F_PREFLIGHT_SHA256_V13 = (
    "679a9f1a1ac9b7908c4cde7aaa825f02bf07f27d02c5fa582168e26ac46fd9c1"
)
G2F_PUBLIC_CONSTRUCTION_LEDGER_SHA256_V13 = (
    "4e59552077f03b1f2f3fdafc901737ad2db9185ad2bf2c304afd87e19b70fe97"
)
G2F_EXECUTED_PRODUCER_BASIS_SHA256_V13 = (
    "f78aedd408138603d78f249178e171c48b0338e7aa331293f0832cbb27815b0d"
)
G2F_V12R2_ARCHIVE_SHA256 = (
    "c600d68e0cf4fce20a00a0783e470d3169d6f35566609b94a3e13745b5409fec"
)
G2F_V12R4_ARCHIVE_SHA256 = (
    "3ef8186d734436d5332d1ba43f27652c91fdc5cb1d58a7fd6089ba081df3cec3"
)
G2F_V12R5_ARCHIVE_SHA256 = (
    "ac705170be8fc731767f27637a6cb8595eec531ef24ac4acae8e3484e7a8d006"
)
G2F_V12R6_ARCHIVE_SHA256 = (
    "78fd785e707fc6d198878a566b49ba6dad0e47d2e0efd0bc8c812b78d33334d4"
)
G2F_V13_ARCHIVE_SHA256 = (
    "854583db82779dea15aec2abff29944cc46e015a71234fcf61185f0fc2c1e6e7"
)
G2F_V13_STATUS_CONTRACT = {
    "G2F_PREFLIGHT_STATUS": "CLASS_A_181_ROW_RECONCILIATION_CANDIDATE",
    "G2F_CLASS_A_STATUS": "V13R1_CANDIDATE_PENDING_OWNER_REVIEW",
    "G2F_CLASSIFICATION": "ORCHESTRATION_AND_ACCEPTANCE_ONLY",
    "G2F_RUNTIME_IMPLEMENTATION_PERFORMED": "false",
    "G2F_IMPLEMENTATION_AUTHORIZED": "false",
    "G2F_STATUS": "NOT_CLOSED",
    "GATE2_STATUS": "NOT_CLOSED",
    "OWNER_ONLY_COMMIT_PUSH": "true",
    "SOURCE_BASIS_HEAD": "c3f2cd379bcebc71e46e83f44aee0b68d76ae5ce",
    "PUBLIC_CONSTRUCTION_LEDGER_ROWS": "181",
    "CONSTRUCTION_LEDGER_CONSECUTIVE": "true",
    "CURRENT_CLASS_A_POSTIMAGES_RECONCILED": "true",
    "V12R2_RUNTIME_SEMANTIC_AND_PARENT_MAP_STATUS": "ACCEPTED",
    "V12R3_EXECUTED_PRODUCER_BASIS_STATUS": "ACCEPTED_THROUGH_V12R6",
    "V12R3_RECONCILIATION_READINESS_STATUS": "SUPERSEDED_BY_V12R4",
    "V12R3_ALL_ANTI_FITTING_HOSTILES_STATUS": "SUPERSEDED_BY_V12R4",
    "V12R4_PROOF_STATUS": "ACCEPTED_AS_REGRESSION_PROVENANCE_SUPERSEDED_BY_V12R5",
    "V12R5_RECONCILIATION_READINESS_STATUS": "SUPERSEDED",
    "V12R5_RECONCILIATION_READINESS_SCOPE": "ONLY_TERMINAL_READINESS",
    "V12R5_RECONCILIATION_READINESS_SUPERSEDED_BY": "V12R6_FULL_CORRIDOR_EXTERNAL_PROOF",
    "V12R5_EXECUTED_PRODUCER_BASIS_STATUS": "ACCEPTED",
    "V12R5_EXECUTED_PRODUCER_BASIS_SCOPE": "IMMUTABLE_REGRESSION_EVIDENCE",
    "V12R5_ROW099_SOURCE_RECEIPT_BINDING_STATUS": "ACCEPTED",
    "V12R5_ROW099_SOURCE_RECEIPT_BINDING_SCOPE": "IMMUTABLE_REGRESSION_EVIDENCE",
    "V12R5_CLEAN_RUNTIME_AND_SEMANTIC_PROJECTION_STATUS": "ACCEPTED",
    "V12R5_CLEAN_RUNTIME_AND_SEMANTIC_PROJECTION_SCOPE": "IMMUTABLE_REGRESSION_EVIDENCE",
    "V12R5_CLEAN_CAUSAL_AND_LOCAL_USE_PROJECTION_STATUS": "ACCEPTED",
    "V12R5_CLEAN_CAUSAL_AND_LOCAL_USE_PROJECTION_SCOPE": "REGRESSION_TARGET",
    "V12R5_EXECUTED_32_NEGATIVE_REGRESSION_RESULTS_STATUS": "ACCEPTED",
    "V12R5_EXECUTED_32_NEGATIVE_REGRESSION_RESULTS_SCOPE": "HISTORICAL_TESTED_SCOPE",
    "V12R5_FULL_BYTE_CORRIDOR_STATEMENT_COVERAGE_STATUS": "NOT_PROVEN",
    "V12R5_FULL_BYTE_CORRIDOR_STATEMENT_COVERAGE_SCOPE": "PROOF_ANALYZER_DEFECT_ONLY",
    "G2F_V12R6_RESULT": "PASS_READY_FOR_V13_EXACT_SEVEN_PATH_CLASS_A_181_ROW_RECONCILIATION",
    "V12R6_SCOPE": "EXTERNAL_PROOF_ONLY",
    "V12R6_FULL_CORRIDOR_EXTERNAL_PROOF_STATUS": "DIRECT_AUTHORITY_FOR_V13_RECONCILIATION",
    "V12R6_FULL_CORRIDOR_EXTERNAL_PROOF_SCOPE": "NO_IMPLEMENTATION_OR_RECONCILIATION_AUTHORITY",
    "V12R6_FULL_CORRIDOR_STATEMENT_COVERAGE_STATUS": "PASS_EXACT",
    "V13_INPUT_ARCHIVE_SHA256": G2F_V13_ARCHIVE_SHA256,
    "V13_OWNER_READINESS_STATUS": "SUPERSEDED_BY_V13R1_VALIDATOR_CLOSURE",
    "V13R1_VALIDATOR_CLOSURE_STATUS": "FULL_181_ROW_EXPECTED_SIDE_RECONSTRUCTED_CANDIDATE",
}
G2F_ORIGINAL_CLASS_A_PARENT = G2E_CLOSURE_COMMIT
G2F_ORIGINAL_CLASS_A_COMMIT = "c3f2cd379bcebc71e46e83f44aee0b68d76ae5ce"

CLASS_A_RECONCILIATION_PATHS = frozenset(
    {
        E6_RECONCILIATION_ANNEX_PATH,
        LOCK_PATH,
        INDEX_PATH,
        MANIFEST_PATH,
        "tools/check_active_architecture_authority_v01.py",
        "tests/test_active_architecture_authority_v01.py",
        "tests/test_repository_release_spine_v01.py",
    }
)
CLASS_B_E6_IMPLEMENTATION_PATHS = frozenset(
    {
        LIVING_GAUNTLET_PATH,
        LIVING_GAUNTLET_TEST_PATH,
        CONFORMANCE_SOURCE_PATH,
        KERNEL_CONFORMANCE_RUNNER_PATH,
        KERNEL_CONFORMANCE_TEST_PATH,
    }
)
CLASS_D_LIFECYCLE_PATHS = frozenset(
    {
        G2E_AUDIT_PATH,
        G2E_CHECKPOINT_PATH,
        "AGENTS.md",
        "README.md",
        "release/current_status_overlay_v01.json",
        "release/claim_to_evidence_index.md",
        "release/current_limitations.md",
        "release/current_release_notes.md",
    }
)
CLASS_D_CONTROL_PLANE_PATHS = frozenset(
    {
        LOCK_PATH,
        INDEX_PATH,
        MANIFEST_PATH,
        "tools/check_active_architecture_authority_v01.py",
        "tests/test_active_architecture_authority_v01.py",
        "tests/test_repository_release_spine_v01.py",
    }
)
G2E_CLASS_D_CLOSURE_PATHS = (
    CLASS_D_LIFECYCLE_PATHS | CLASS_D_CONTROL_PLANE_PATHS
)
G2F_CLASS_A_PATHS = frozenset(
    {
        G2F_PREFLIGHT_PATH,
        LOCK_PATH,
        INDEX_PATH,
        MANIFEST_PATH,
        "tools/check_active_architecture_authority_v01.py",
        "tests/test_active_architecture_authority_v01.py",
        "tests/test_repository_release_spine_v01.py",
    }
)
G2F_IMPLEMENTATION_PATHS = frozenset({G2F_RUNNER_PATH, G2F_TEST_PATH})
G2F_CLOSURE_OVERLAP_PATHS = frozenset(
    {
        LOCK_PATH,
        INDEX_PATH,
        MANIFEST_PATH,
        "tools/check_active_architecture_authority_v01.py",
        "tests/test_active_architecture_authority_v01.py",
        "tests/test_repository_release_spine_v01.py",
    }
)
G2F_CLOSURE_PATHS = frozenset(
    {
        "docs/audit_reports/auditor_consolidated_gate2_gauntlet_g2_f_v01.log",
        "docs/consolidated_gate2_gauntlet_g2_f_checkpoint_v01.md",
        "AGENTS.md",
        "README.md",
        "release/current_status_overlay_v01.json",
        "release/claim_to_evidence_index.md",
        "release/current_limitations.md",
        "release/current_release_notes.md",
        *G2F_CLOSURE_OVERLAP_PATHS,
    }
)

CLASS_A_COMMITTED_NAME_STATUS = {
    path: "A" if path == E6_RECONCILIATION_ANNEX_PATH else "M"
    for path in CLASS_A_RECONCILIATION_PATHS
}
CLASS_B_COMMITTED_NAME_STATUS = {
    path: "M" for path in CLASS_B_E6_IMPLEMENTATION_PATHS
}
CLASS_D_COMMITTED_NAME_STATUS = {
    path: "A" if path in {G2E_AUDIT_PATH, G2E_CHECKPOINT_PATH} else "M"
    for path in G2E_CLASS_D_CLOSURE_PATHS
}
G2F_ORIGINAL_CLASS_A_COMMITTED_NAME_STATUS = {
    path: "A" if path == G2F_PREFLIGHT_PATH else "M"
    for path in G2F_CLASS_A_PATHS
}
G2F_CLASS_A_RECONCILIATION_COMMITTED_NAME_STATUS = {
    path: "M" for path in G2F_CLASS_A_PATHS
}
G2F_IMPLEMENTATION_COMMITTED_NAME_STATUS = {
    path: "A" for path in G2F_IMPLEMENTATION_PATHS
}
G2F_ORIGINAL_CLASS_A_POSTIMAGE_IDENTITIES = {
    G2F_PREFLIGHT_PATH: (
        "d438d7c07ac00ea8c5f3c258b895abd1839d8384e1752ec4357134e8a1594f20",
        45931,
        537,
    ),
    LOCK_PATH: (
        "7b6cd950e1f434d62d3f0763df92debf93e88670bdc17b12d34b66bb0a45fabe",
        10646,
        222,
    ),
    INDEX_PATH: (
        "f4a8229ef0186323de7e21dec7d52d95654ba111f137565596824b3ccc174072",
        17541,
        393,
    ),
    MANIFEST_PATH: (
        "6b9c21737c3aca42b2b71bd48bdc991414af0e05ee958a4c0d645120223620fe",
        23603,
        554,
    ),
    "tools/check_active_architecture_authority_v01.py": (
        "4cf3194a1609bd29bb92a73ad161c4a9b16b3e376c64eaa71040fa105f609765",
        412276,
        11023,
    ),
    "tests/test_active_architecture_authority_v01.py": (
        "1f00397f3d39b9702f313abc407a800615f13a262bc4f92b52fc0a85ea08576a",
        236174,
        6478,
    ),
    "tests/test_repository_release_spine_v01.py": (
        "1a89a4a13469bbb0c87fed8f04ec8ad12cba1fc2c837c26d5eab2787cebeba24",
        258023,
        6067,
    ),
}
POST_E6_LIVING_ACCEPTANCE_TEST = (
    "test_living_gauntlet_v16_continuous_delta_runtime_acceptance_v01"
)
POST_E6_CONFORMANCE_ACCEPTANCE_TEST = (
    "test_kernel_conformance_v07_continuous_delta_runtime_acceptance_v01"
)
G2F_FOCUSED_TEST_IDS = (
    "g2f_positive_01_report_geometry_and_current_basis",
    "g2f_positive_02_causal_order_and_identity_lineage",
    "g2f_positive_03_informational_fast_path_heavy_skip",
    "g2f_positive_04_high_risk_multiroot_full_fractal_execution",
    "g2f_positive_05_packet_delta_revocation_supersession_chain",
    "g2f_positive_06_canonical_plain_projection_and_render",
    "g2f_positive_07_independent_fresh_collections_no_cache",
    "g2f_positive_08_public_validator_accepts_actual_report",
    "g2f_dod_01_safe_informational_reuse",
    "g2f_dod_02_action_reuse_blocked",
    "g2f_dod_03_high_risk_multiroot_deep",
    "g2f_dod_04_revoke_before_fulfillment",
    "g2f_dod_05_superseded_replay_blocked",
    "g2f_dod_06_selective_recompute",
    "g2f_dod_07_components_non_authority",
    "g2f_hostile_08_drs_not_authority",
    "g2f_hostile_09_router_not_authority",
    "g2f_hostile_10_registry_not_authority",
    "g2f_hostile_11_child_not_root",
    "g2f_hostile_12_delta_not_authority",
    "g2f_hostile_13_no_permission_revival",
    "g2f_hostile_14_no_stale_packet_replay",
    "g2f_hostile_15_no_aggregate_pass",
    "g2f_hostile_16_zero_operations",
)
G2F_REQUIRED_PUBLIC_CALLS_V02 = {
    "validate_existing_root_shortcut_decision_v01": (
        "hedgehog.reuse_certificate_v01",
        1,
    ),
    "evaluate_drs_candidate_v01": ("hedgehog.drs_memory_resolution_v01", 1),
    "route_execution_mode_v01": (
        "hedgehog.kernel.execution_mode_router_v01",
        2,
    ),
    "review_execution_mode_proposal_v01": (
        "hedgehog.kernel.execution_mode_router_v01",
        2,
    ),
    "build_transaction_outcome_envelope_v01": (
        "hedgehog.kernel.multiroot_v01",
        1,
    ),
    "validate_transaction_outcome_envelope_v01": (
        "hedgehog.kernel.multiroot_v01",
        1,
    ),
    "validate_multiroot_v01": ("hedgehog.kernel.multiroot_v01", 1),
    "run_fractal_runtime_v02": ("hedgehog.kernel.fractal_runtime_v02", 2),
    "build_semantic_work_request_v01": (
        "hedgehog.kernel.semantic_work_v01",
        7,
    ),
    "build_evidence_binding_v01": (
        "hedgehog.kernel.semantic_work_v01",
        7,
    ),
    "build_normalized_claim_v01": (
        "hedgehog.kernel.semantic_work_v01",
        7,
    ),
    "build_actor_contribution_v01": (
        "hedgehog.kernel.semantic_work_v01",
        7,
    ),
    "build_root_review_packet_from_contributions_v01": (
        "hedgehog.kernel.semantic_work_v01",
        7,
    ),
    "build_root_decision_input_v01": (
        "hedgehog.kernel.root_decision_v01",
        7,
    ),
    "decide_root_v01": ("hedgehog.kernel.root_decision_v01", 7),
    "build_root_decision_candidate_projection_v01": (
        "hedgehog.action_commit_packet_v02",
        4,
    ),
    "record_action_packet_genesis_v01": (
        "hedgehog.action_commit_packet_v02",
        2,
    ),
    "build_action_packet_transition_event_v01": (
        "hedgehog.action_commit_packet_v02",
        8,
    ),
    "activate_action_packet_lifecycle_v01": (
        "hedgehog.action_commit_packet_v02",
        1,
    ),
    "append_action_packet_lifecycle_transition_v01": (
        "hedgehog.action_commit_packet_v02",
        4,
    ),
    "inspect_action_packet_present_eligibility_v01": (
        "hedgehog.action_commit_packet_v02",
        3,
    ),
    "run_continuous_delta_runtime_v01": (
        "hedgehog.kernel.continuous_delta_runtime_v01",
        1,
    ),
    "build_action_invalidation_evidence_v01": (
        "hedgehog.action_commit_packet_v02",
        3,
    ),
    "record_action_packet_revocation_v01": (
        "hedgehog.action_commit_packet_v02",
        1,
    ),
    "build_supplier_root_bound_action_commit_packet_v02_projection_v01": (
        "hedgehog.action_commit_packet_v02",
        2,
    ),
    "record_action_packet_supersession_v01": (
        "hedgehog.action_commit_packet_v02",
        1,
    ),
    "replay_action_packet_lifecycle_history_v01": (
        "hedgehog.action_commit_packet_v02",
        1,
    ),
}

AUTHORITY_INDEX_KEYS = (
    "schema_version",
    "generated_for_head",
    "current_normative_documents",
    "current_operational_documents",
    "current_technical_annexes",
    "future_reference_documents",
    "historical_documents",
    "audit_only_sources",
    "excluded_from_successor_onboarding",
    "source_of_truth_order",
    "notes",
)
PRE_CLOSURE_MANIFEST_KEYS = (
    "schema_version",
    "base_head",
    "manifest_status",
    "onboarding_ready",
    "blocking_repairs",
    "purpose",
    "always_include",
    "include_current_gate_sources",
    "include_current_gate_tests",
    "include_current_release_sources",
    "exclude_paths",
    "exclude_globs",
    "committed_e5_basis",
    "authority_documents",
    "historical_access_method",
    "validation_command",
)
G2E_CLOSURE_MANIFEST_KEYS = (
    *PRE_CLOSURE_MANIFEST_KEYS[:13],
    "committed_e6_basis",
    *PRE_CLOSURE_MANIFEST_KEYS[13:],
)
MANIFEST_KEYS = (
    *PRE_CLOSURE_MANIFEST_KEYS[:13],
    "committed_e6_basis",
    "g2f_class_a_succession",
    *PRE_CLOSURE_MANIFEST_KEYS[13:],
)
CURRENT_DOCUMENT_ENTRY_KEYS = (
    "path",
    "status",
    "current_authority",
    "authority_scope",
    "may_override_architecture_lock",
    "onboarding_allowed",
    "role",
)
HISTORICAL_ENTRY_KEYS = (
    "path",
    "status",
    "historical_git_ref",
    "current_authority",
    "onboarding_allowed",
    "preservation",
    "current_replacement",
)
COMMITTED_E5_ENTRY_KEYS = ("path", "sha256", "bytes", "lf")
COMMITTED_E5_BASIS_KEYS = (
    "implementation_commit",
    "implementation_subject",
    "status",
    "paths",
    "e6_implementation_status",
    "g2e_status",
    "gate2_status",
)
COMMITTED_E6_BASIS_KEYS = (
    "class_a_commit",
    "class_a_subject",
    "class_b_commit",
    "class_b_subject",
    "control_plane_repair_commit",
    "control_plane_repair_subject",
    "status",
    "runtime_phase",
    "lifecycle_phase",
    "class_b_paths",
    "control_plane_test_paths",
    "v10_evidence",
    "audit_path",
    "audit_sha256",
    "checkpoint_path",
    "checkpoint_sha256",
    "g2e_status",
    "g2f_status",
    "g2f_implementation_authorized",
    "gate2_status",
    "public_release_status",
    "rc2_status",
    "production_readiness_status",
    "production_security_certification_status",
    "real_world_effects_count",
)
V10_EVIDENCE_KEYS = (
    "archive_sha256",
    "archive_bytes",
    "regular_members",
    "manifest_data_rows",
    "kernel_runtime_tests",
    "living_runtime_tests",
    "release_spine_tests",
    "authority_tests",
    "runtime_evidence_reuse_dependency_proof",
)

REQUIRED_HISTORICAL_PATHS = (
    "specs/human_passport_v0_25.md",
    "specs/math_appendix_v0_3.md",
    "specs/machine_manifest_v0_25.json",
    "specs/schema_package_v0_25_reference.md",
    "specs/invariants.md",
    "specs/demo_baseline_v0_25.md",
    "specs/demo_scenario.md",
    "specs/legacy_mapping.md",
    "docs/passport_geometry_root_needles.md",
    "docs/strategic_expansion_map.md",
)
REQUIRED_ALWAYS_INCLUDE = frozenset(
    {
        "AGENTS.md",
        "README.md",
        LOCK_PATH,
        INDEX_PATH,
        MANIFEST_PATH,
        RETIRED_INVENTORY_PATH,
        CURRENT_SCHEMA_SURFACE_PATH,
        "docs/continuous_delta_runtime_v0_1_g2_e_preflight_v01.md",
        "docs/continuous_delta_runtime_v0_1_g2_e_post_acceptance_contract_addendum_v01.md",
        E6_RECONCILIATION_ANNEX_PATH,
        "hedgehog/__init__.py",
        "hedgehog/drs.py",
        "hedgehog/local_drs_resolver.py",
        "hedgehog/local_drs_v02.py",
        "hedgehog/reuse_gate.py",
        "hedgehog/semantic_reasoning_adapter.py",
        "hedgehog/evidence/__init__.py",
        "hedgehog/evidence/external_anchor_v01.py",
        "hedgehog/evidence/sealed_evidence_profile_v01.py",
        "hedgehog/evidence/sealed_package_v01.py",
        "hedgehog/evidence/sealed_replay_evidence_v01.py",
        "hedgehog/kernel/abi_v01.py",
        "hedgehog/kernel/integrity_replay_v01.py",
        "hedgehog/kernel/root_decision_v01.py",
        "hedgehog/kernel/root_signer_isolation_v01.py",
        "hedgehog/kernel/execution_mode_router_v01.py",
        "hedgehog/kernel/fractal_runtime_v02.py",
        "hedgehog/kernel/continuous_delta_runtime_v01.py",
        "demo/run_continuous_delta_runtime_g2_e_v01.py",
        "tests/test_continuous_delta_runtime_g2_e_v01.py",
        "hedgehog/time_model.py",
        "hedgehog/domains/airline/kernel_adapter_v01.py",
        "hedgehog/domains/supplier_water_filter/kernel_adapter_v01.py",
        "schemas/common.schema.json",
        "schemas/time_envelope.schema.json",
        "schemas/result_proposal.schema.json",
        "schemas/vv_report.schema.json",
        "schemas/gt_report.schema.json",
        "release/current_status_overlay_v01.json",
        "release/claim_to_evidence_index.md",
        "release/current_limitations.md",
        "release/current_release_notes.md",
        "release/one_command_gauntlet.md",
        "release/completion_manifest.json",
        "release/integration_seam_index.json",
        "release/integration_seam_index.md",
    }
)
REQUIRED_GATE_SOURCES = frozenset(
    {
        "hedgehog/context_packets.py",
        "hedgehog/__init__.py",
        "hedgehog/drs.py",
        "hedgehog/local_drs_resolver.py",
        "hedgehog/local_drs_v02.py",
        "hedgehog/reuse_gate.py",
        "hedgehog/semantic_reasoning_adapter.py",
        "hedgehog/evidence/__init__.py",
        "hedgehog/evidence/external_anchor_v01.py",
        "hedgehog/evidence/sealed_evidence_profile_v01.py",
        "hedgehog/evidence/sealed_package_v01.py",
        "hedgehog/evidence/sealed_replay_evidence_v01.py",
        "hedgehog/action_commit_packet_v02.py",
        "hedgehog/drs_semantic_address_v01.py",
        "hedgehog/drs_memory_resolution_v01.py",
        "hedgehog/reuse_certificate_v01.py",
        "hedgehog/kernel/semantic_work_v01.py",
        "hedgehog/kernel/transition_registry_v01.py",
        "hedgehog/kernel/effect_firewall_v01.py",
        "hedgehog/kernel/multiroot_v01.py",
        "hedgehog/kernel/root_signer_isolation_v01.py",
        "hedgehog/kernel/execution_mode_router_v01.py",
        "hedgehog/kernel/fractal_runtime_v02.py",
        "hedgehog/kernel/continuous_delta_runtime_v01.py",
        CONFORMANCE_SOURCE_PATH,
        "hedgehog/time_model.py",
        "hedgehog/domains/airline/kernel_adapter_v01.py",
        "hedgehog/domains/supplier_water_filter/kernel_adapter_v01.py",
        "schemas/common.schema.json",
        "schemas/time_envelope.schema.json",
        "schemas/result_proposal.schema.json",
        "schemas/vv_report.schema.json",
        "schemas/gt_report.schema.json",
        "schemas/execution_mode_router_v01.schema.json",
        "schemas/fractal_runtime_v02.schema.json",
        "schemas/continuous_delta_runtime_v01.schema.json",
        "demo/run_continuous_delta_runtime_g2_e_v01.py",
        "demo/run_kernel_conformance_v01.py",
        "demo/run_living_gauntlet_v01.py",
    }
)
REQUIRED_GATE_TESTS = frozenset(
    {
        "tests/test_action_commit_packet_lifecycle_g2_a_v01.py",
        "tests/test_drs_semantic_address_reuse_certificate_g2_b_v01.py",
        "tests/test_execution_mode_router_g2_c_v01.py",
        "tests/test_fractal_runtime_g2_d_v02.py",
        "tests/test_continuous_delta_runtime_g2_e_v01.py",
        "tests/test_kernel_integrity_replay_v01.py",
        "tests/test_root_signer_isolation_v01.py",
        "tests/test_airline_kernel_adapter_v01.py",
        "tests/test_supplier_water_filter_kernel_adapter_v01.py",
        "tests/test_living_gauntlet_v01_runner.py",
        "tests/test_kernel_conformance_v01_runner.py",
    }
)
REQUIRED_RELEASE_SOURCES = frozenset(
    {
        "release/current_status_overlay_v01.json",
        "release/claim_to_evidence_index.md",
        "release/current_limitations.md",
        "release/current_release_notes.md",
        "release/one_command_gauntlet.md",
        "release/completion_manifest.json",
        "release/integration_seam_index.json",
        "release/integration_seam_index.md",
        RETIRED_INVENTORY_PATH,
        CURRENT_SCHEMA_SURFACE_PATH,
    }
)
REQUIRED_E5_PATHS = frozenset(
    {
        "hedgehog/kernel/continuous_delta_runtime_v01.py",
        "tests/test_continuous_delta_runtime_g2_e_v01.py",
        "demo/run_continuous_delta_runtime_g2_e_v01.py",
    }
)

FROZEN_E5_IDENTITIES = {
    "hedgehog/kernel/continuous_delta_runtime_v01.py": (
        "97184c1f47548f8bab96f9a01644a2fb96dd23029fe917c522c6635c96ad099a",
        519719,
        12927,
    ),
    "demo/run_continuous_delta_runtime_g2_e_v01.py": (
        "5a39f5ead5241cc529359d173bdf999ed190b1a5b2668828c0eeca8fbcb6433c",
        381288,
        9267,
    ),
    "tests/test_continuous_delta_runtime_g2_e_v01.py": (
        "8d26d45a71334172b73fa30125b0e3ddfff74aeb66431af56594d75f9a7f4d8b",
        661888,
        16182,
    ),
}
PRE_E6_CLASS_B_IDENTITIES = {
    LIVING_GAUNTLET_PATH: (
        "72ace8d6060dd66ddfc09e205a0e1cf5e019419dbd3786b2152ba533c8f64905",
        226590,
        5823,
    ),
    LIVING_GAUNTLET_TEST_PATH: (
        "4125cf936d81ffdd503d4ad6dcb6bfffb22b21d163999996b403aeb9f41854ff",
        189925,
        5175,
    ),
    CONFORMANCE_SOURCE_PATH: (
        "93460bfd6262b9fec221c454637d27afbb346f3e444740c55e7e2496af866b91",
        62485,
        1749,
    ),
    KERNEL_CONFORMANCE_RUNNER_PATH: (
        "75accdcda30fa9d66771b15bfdaf417f65cd27319e5beb3fb7edca32284a2e30",
        115121,
        2993,
    ),
    KERNEL_CONFORMANCE_TEST_PATH: (
        "562d2a96ab01373e9cff7d37badf7e68a089e2b9ad0351fd7081aa62540a3ac5",
        96905,
        2554,
    ),
}
POST_E6_CLASS_B_IDENTITIES = {
    LIVING_GAUNTLET_PATH: (
        "99ea9b788a6d02b71afcc8e9e1b19fce834c50673c13a21f19a080658f37a9f7",
        241073,
        6204,
    ),
    LIVING_GAUNTLET_TEST_PATH: (
        "78228e0efbe02b5eb9d8bf841f9fb43c8b42ebdf55c1576cf45107bafa78a7b6",
        217249,
        5636,
    ),
    CONFORMANCE_SOURCE_PATH: (
        "3b04b62e960d5cab058a4d04bc5cbc92e20de39fdc297059298032cc176a4a62",
        76011,
        2082,
    ),
    KERNEL_CONFORMANCE_RUNNER_PATH: (
        "9314eb3ba16ee333fa9066719023de4d2957679610a3748e26a0c6b25789411d",
        134798,
        3479,
    ),
    KERNEL_CONFORMANCE_TEST_PATH: (
        "d24bbac266b020b5c9d66f9376eead51cdf836fcb537fea393251a44d99a0ed0",
        126972,
        3320,
    ),
}
POST_E6_CONTROL_TEST_IDENTITIES = {
    "tests/test_active_architecture_authority_v01.py": (
        "6c979026cd5b8728612fc6eff3e1d6b80de56f48f627429346026ca6ac0cd175",
        197672,
        5707,
    ),
    "tests/test_repository_release_spine_v01.py": (
        "fc40a0b9e9e3168c003b62a4b79409e146d44f7a4644e608084495930afcdd9c",
        241233,
        5668,
    ),
}
POST_E6_CONTROL_PLANE_BASIS_IDENTITIES = {
    LOCK_PATH: (
        "f2299fe6330d91f6e328df3b323b299d0b58c0cddfb2721495444358d5e5ebb0",
        7725,
        169,
    ),
    INDEX_PATH: (
        "718b1bfb03f5ccef78db5ca4ffebc9a58024352db80f8bf1b11a5925a8200eec",
        15964,
        365,
    ),
    MANIFEST_PATH: (
        "e06dc5821efcda885c465349231d58270094d35342a2552b585bda754b685a76",
        14893,
        327,
    ),
    "tools/check_active_architecture_authority_v01.py": (
        "ed287de34baf17243283c237c943e956403bb88e7244029a5856c7e3f87abe0f",
        325713,
        8708,
    ),
    **POST_E6_CONTROL_TEST_IDENTITIES,
}
G2E_AUDIT_SHA256 = (
    "623fc966b2087c9bc77064ad9bc2b304b2dc7e735a5d220e83c9f224e991e5eb"
)
G2E_CHECKPOINT_SHA256 = (
    "494cf40ad6d080d2dd0b7508eadc13ae4e6ada32ad1f905025fb9cee78bdb33d"
)
G2E_CLOSURE_EVIDENCE_IDENTITIES = {
    G2E_AUDIT_PATH: (G2E_AUDIT_SHA256, 8664, 197),
    G2E_CHECKPOINT_PATH: (G2E_CHECKPOINT_SHA256, 5461, 126),
}
G2E_CLOSURE_EXPECTED_STATUS_FIELDS = {
    "g2e3_status": "IMPLEMENTED_COMMITTED_ACCEPTANCE_PASS_ON_CORRECTED_G2D",
    "g2e4_status": "IMPLEMENTED_COMMITTED_ACCEPTANCE_PASS",
    "g2e5_status": "IMPLEMENTED_COMMITTED_ACCEPTANCE_PASS",
    "g2e6_status": "IMPLEMENTED_COMMITTED_ACCEPTANCE_PASS",
    "g2e_status": "CLOSED_PASS",
    "g2e_runtime_phase": "POST_E6_SUCCESSOR",
    "g2e_lifecycle_phase": "G2E_CLOSED_PASS",
    "g2e5_implementation_commit": E5_IMPLEMENTATION_BASIS_COMMIT,
    "g2e6_class_a_commit": G2E_CLASS_A_COMMIT,
    "g2e6_class_b_commit": G2E_CLASS_B_COMMIT,
    "g2e6_control_plane_repair_commit": G2E_CLOSURE_BASIS_COMMIT,
    "g2e6_v10_archive_sha256": (
        "33942d30f59d9f63dafa0c0f633b2f7e53c2b9f8e7f634b1dc798942e97e8573"
    ),
    "g2e6_v10_archive_bytes": 253612,
    "g2e6_v10_archive_members": 57,
    "g2e6_v10_manifest_rows": 56,
    "g2e6_kernel_runtime_tests_passed": 400,
    "g2e6_living_runtime_tests_passed": 595,
    "g2e6_release_spine_tests_passed": 32,
    "g2e6_authority_tests_passed": 941,
    "g2e6_runtime_evidence_reuse_dependency_proof": "PASS",
    "g2e_audit_path": G2E_AUDIT_PATH,
    "g2e_audit_sha256": G2E_AUDIT_SHA256,
    "g2e_checkpoint_path": G2E_CHECKPOINT_PATH,
    "g2e_checkpoint_sha256": G2E_CHECKPOINT_SHA256,
    "g2e_living_version": "v1.6",
    "g2e_living_act_count": 17,
    "g2e_conformance_version": "v0.7",
    "g2e_conformance_category_count": 15,
    "g2e_conformance_negative_probe_count": 60,
    "g2e_conformance_active_ref_count": 16,
    "g2e_conformance_domain_count": 2,
    "g2e_profile_succession": (
        "V05_HISTORICAL_TO_V06_HISTORICAL_TO_V07_CURRENT"
    ),
    "g2e_frozen_completion_manifest_sha256": (
        "4ae53a074dd49440c191928b10b390120cc97aa7c04f23c3ddc9771fd914d5b9"
    ),
    "g2e_frozen_integration_seam_index_sha256": (
        "4b0d65b84ca253b2a41b03777ae64a67f9ca048608b0d9648196129c1754fb03"
    ),
    "g2e_frozen_release_evidence_classification": (
        "FROZEN_PREDECESSOR_EVIDENCE_NOT_CURRENT_E6_EXECUTION"
    ),
    "g2f_status": "NEXT_NOT_STARTED_NOT_AUTHORIZED",
    "g2f_implementation_authorized": False,
    "gate2_status": "NOT_CLOSED",
    "public_release_status": "NOT_CLAIMED",
    "rc2_status": "NOT_CLAIMED",
    "production_readiness_status": "NOT_CLAIMED",
    "production_security_certification_status": "NOT_CLAIMED",
    "public_release_claimed": False,
    "rc2_claimed": False,
    "production_readiness_claimed": False,
    "production_security_certification_claimed": False,
    "real_world_effects_count": 0,
}
FROZEN_PREDECESSOR_EVIDENCE_IDENTITIES = {
    COMPLETION_MANIFEST_PATH: (
        "4ae53a074dd49440c191928b10b390120cc97aa7c04f23c3ddc9771fd914d5b9",
        30628,
        567,
    ),
    SEAM_INDEX_PATH: (
        "4b0d65b84ca253b2a41b03777ae64a67f9ca048608b0d9648196129c1754fb03",
        15589,
        297,
    ),
}
CLASS_A_CONTROL_SURFACE_IDENTITIES = {
    E6_RECONCILIATION_ANNEX_PATH: (
        "1050079c7ea159f56e8645fad4e7398b008faa005a8597a05befa13ae0c65e60",
        17033,
        401,
    ),
    LOCK_PATH: (
        "f2299fe6330d91f6e328df3b323b299d0b58c0cddfb2721495444358d5e5ebb0",
        7725,
        169,
    ),
    INDEX_PATH: (
        "718b1bfb03f5ccef78db5ca4ffebc9a58024352db80f8bf1b11a5925a8200eec",
        15964,
        365,
    ),
    MANIFEST_PATH: (
        "e06dc5821efcda885c465349231d58270094d35342a2552b585bda754b685a76",
        14893,
        327,
    ),
}

REQUIRED_MANIFEST_STATUS = "SUCCESSOR_ONBOARDING_READY"
REQUIRED_BLOCKING_REPAIRS: tuple[str, ...] = ()
S3_GENERATED_FROM_HEAD = "237501110159f1adb6d8a4c5e9482d618e5a8187"
RETIRED_RECORD_KEYS = (
    "path",
    "classification",
    "current_runtime_allowed",
    "current_schema_registration_allowed",
    "current_export_allowed",
    "successor_onboarding_allowed",
    "preservation",
    "reason",
)
RETIRED_INVENTORY_KEYS = (
    "inventory_id",
    "inventory_status",
    "architecture_lock_ref",
    "generated_from_head",
    "retired_schema_paths",
    "retired_runtime_reference_paths",
    "historical_demo_test_families",
    "forbidden_current_uses",
    "preservation_law",
    "onboarding_law",
)
CURRENT_SCHEMA_SURFACE_KEYS = (
    "schema_surface_id",
    "schema_surface_status",
    "generated_from_head",
    "current_schema_paths",
    "retired_schema_paths",
    "current_loader_or_registry_refs",
    "isolation_invariants",
)
SCHEMA_LOADER_REF_KEYS = ("source_path", "schema_paths", "role")

HISTORICAL_ALL_LAYERS_RUNNER_PATH = (
    "demo/run_all_layers_applied_super_smoke.py"
)
HISTORICAL_ALL_LAYERS_TEST_PATH = (
    "tests/test_all_layers_applied_super_smoke_runner.py"
)
HISTORICAL_ALL_LAYERS_PATHS = (
    HISTORICAL_ALL_LAYERS_RUNNER_PATH,
    HISTORICAL_ALL_LAYERS_TEST_PATH,
)
_HISTORICAL_ACT_ID = "all_layers_" + "invariant_super_smoke"
_HISTORICAL_RUNNER_MODULE = "demo.run_all_layers_" + "applied_super_smoke"
_HISTORICAL_RUNNER_SYMBOL = "collect_all_layers_" + "applied_super_smoke"
CURRENT_PROFILE_ID = "kernel_conformance_v0_6_current"
HISTORICAL_PROFILE_ID = "kernel_conformance_v0_5_historical"
HISTORICAL_V05_ACTIVE_REFS = (
    "airline_deterministic_transaction_runtime",
    _HISTORICAL_ACT_ID,
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
CURRENT_V06_ACTIVE_REFS = tuple(
    act_id for act_id in HISTORICAL_V05_ACTIVE_REFS if act_id != _HISTORICAL_ACT_ID
)
POST_E6_PROFILE_ID = "kernel_conformance_v0_7_current"
POST_E6_IMMEDIATE_HISTORICAL_PROFILE_ID = "kernel_conformance_v0_6_historical"
PRE_E6_LIVING_ACT_IDS = (
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
    "kernel_conformance_closure",
    "action_packet_lifecycle",
    "drs_semantic_address_and_reuse_certificate",
    "execution_mode_router",
    "fractal_runtime",
)
POST_E6_LIVING_ACT_IDS = (*PRE_E6_LIVING_ACT_IDS, "continuous_delta_runtime")
POST_E6_ACTIVE_REFS = (*CURRENT_V06_ACTIVE_REFS, "continuous_delta_runtime")
PRE_E6_CATEGORY_CHECK_IDS = (
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
    (
        "ExecutionModeRouterConformance",
        (
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
        ),
    ),
    (
        "FractalRuntimeConformance",
        (
            "policy_identity_and_staged_surface",
            "executable_templates_and_child_activation",
            "queue_input_outcome_and_result_order",
            "paired_budget_events_and_backpressure",
            "resultproposal_unique_gt_kt_validation",
            "pre_root_four_artifact_abi_partitions",
            "transition_profile_and_root_only_report",
            "causal_pointer_reason_and_root_outcome",
            "two_domain_seventy_two_case_boundary",
            "zero_authority_and_operations",
        ),
    ),
)
E6_CATEGORY_CHECK_IDS = (
    "delta_source_identity_and_changed_field_binding",
    "dependency_fingerprint_profile_and_role_separation",
    "dependency_graph_bounds_order_and_acyclicity",
    "affected_set_complete_and_minimal",
    "invalidation_without_deletion",
    "preservation_and_new_identity_recomputation",
    "g2a_g2b_g2c_g2d_source_binding",
    "repeated_delta_idempotency_and_no_spin",
    "two_domain_selective_recomputation",
    "zero_authority_and_operations",
)
POST_E6_CATEGORY_CHECK_IDS = (
    *PRE_E6_CATEGORY_CHECK_IDS,
    ("ContinuousDeltaRuntimeConformance", E6_CATEGORY_CHECK_IDS),
)
PRE_E6_NEGATIVE_PROBE_IDS = (
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
    "fractal_runtime_report_identity_forgery",
    "fractal_runtime_route_eligibility_substitution",
    "fractal_runtime_direct_root_decision_bypass",
    "fractal_runtime_mode_profile_forgery",
    "fractal_runtime_scope_budget_widening",
    "fractal_runtime_queue_transition_forgery",
    "fractal_runtime_recursive_capability_forgery",
    "fractal_runtime_no_progress_forgery",
    "fractal_runtime_child_authority_forgery",
    "fractal_runtime_zero_operation_forgery",
)
E6_NEGATIVE_PROBE_IDS = (
    "continuous_delta_report_identity_forgery",
    "continuous_delta_source_substitution",
    "continuous_delta_dependency_fingerprint_forgery",
    "continuous_delta_graph_edge_forgery",
    "continuous_delta_affected_set_omission",
    "continuous_delta_unrelated_artifact_injection",
    "continuous_delta_invalidation_deletion_forgery",
    "continuous_delta_preserved_artifact_mutation",
    "continuous_delta_root_authority_forgery",
    "continuous_delta_zero_operation_forgery",
)
POST_E6_NEGATIVE_PROBE_IDS = (*PRE_E6_NEGATIVE_PROBE_IDS, *E6_NEGATIVE_PROBE_IDS)
PRESERVED_DOMAIN_IDS = ("airline", "supplier_water_filter")
PRESERVED_DOMAIN_GEOMETRY = (
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

PRE_E6_LIVING_EXECUTED_RUNTIME_ACT_IDS = (
    "airline_deterministic_transaction_runtime",
    "generic_integrity_replay",
    "transition_registry",
    "root_decision_kernel",
    "effect_firewall",
    "supplier_water_filter_portability",
)
POST_E6_LIVING_EXECUTED_RUNTIME_ACT_IDS = (
    *PRE_E6_LIVING_EXECUTED_RUNTIME_ACT_IDS,
    "continuous_delta_runtime",
)
PRE_E6_LIVING_EXECUTED_CONFORMANCE_ACT_IDS = (
    "root_signer_isolation_conformance",
    "semantic_work_contract",
    "domain_neutral_kernel_abi",
    "causal_consumption",
    "generic_multiroot",
    "kernel_conformance_closure",
)
LIVING_EVIDENCE_ONLY_ACT_IDS = (
    "airline_all_real_frozen_reference",
    _HISTORICAL_ACT_ID,
)
LIVING_HISTORICAL_EVIDENCE_ACT_IDS = (_HISTORICAL_ACT_ID,)

# These repr digests freeze insertion order, exact Python container type, keys,
# and values for the bounded source/seam maps without duplicating large maps.
PRE_E6_LIVING_ACTIVE_SOURCES_REPR_SHA256 = (
    "931f2754d830fb8b0987ea46a790c3e054bf8f3393da9541588c8096e1cc24dc"
)
POST_E6_LIVING_ACTIVE_SOURCES_REPR_SHA256 = (
    "12436b3490f1d0cc5e2c275d9202633ed5255e1c0402dfe1cce02d8efb7f8af4"
)
LIVING_CURRENT_SEAMS_REPR_SHA256 = (
    "559b30638e0f69f58cf173d0a04d7efeda4035abc419369209e154b17c071206"
)
PRE_E6_CONFORMANCE_ACT_SOURCES_REPR_SHA256 = (
    "4729a796314e6b78011ec723f09e2ed6269fa54f40289d36cbdb2d838d663bf6"
)
POST_E6_CONFORMANCE_ACT_SOURCES_REPR_SHA256 = (
    "e4e25ea012c5fd1bec34072a9361e145f45a5d86d432b7002450cedd38dda4b0"
)

CORE_PHASE_CRITICAL_NAMES = frozenset(
    {
        "CONFORMANCE_VERSION",
        "KERNEL_CONFORMANCE_PROFILE_V05_HISTORICAL",
        "KERNEL_CONFORMANCE_PROFILE_V06_CURRENT",
        "KERNEL_CONFORMANCE_PROFILE_V06_HISTORICAL",
        "KERNEL_CONFORMANCE_PROFILE_V07_CURRENT",
        "DEFAULT_KERNEL_CONFORMANCE_PROFILE",
        "CATEGORY_IDS",
        "DOMAIN_IDS",
        "NEGATIVE_PROBE_IDS",
        "_V05_HISTORICAL_ACTIVE_GAUNTLET_REFS",
        "_V06_CURRENT_ACTIVE_GAUNTLET_REFS",
        "_V06_HISTORICAL_ACTIVE_GAUNTLET_REFS",
        "_V07_CURRENT_ACTIVE_GAUNTLET_REFS",
        "_ACTIVE_GAUNTLET_REFS",
        "_EXPECTED_CATEGORY_CHECK_IDS",
        "_EXPECTED_DOMAIN_GEOMETRY",
    }
)
RUNNER_PHASE_CRITICAL_NAMES = frozenset(
    {
        "RUNNER_VERSION",
        "KERNEL_CONFORMANCE_PROFILE_V05_HISTORICAL",
        "KERNEL_CONFORMANCE_PROFILE_V06_CURRENT",
        "KERNEL_CONFORMANCE_PROFILE_V06_HISTORICAL",
        "KERNEL_CONFORMANCE_PROFILE_V07_CURRENT",
        "DEFAULT_KERNEL_CONFORMANCE_PROFILE",
        "_V05_HISTORICAL_BASE_ACT_IDS",
        "_V06_HISTORICAL_BASE_ACT_IDS",
        "_BASE_ACT_IDS",
        "_ACT_SOURCES",
    }
)
LIVING_PHASE_CRITICAL_NAMES = frozenset(
    {
        "RUNNER_VERSION",
        "KERNEL_CONFORMANCE_PROFILE_V05_HISTORICAL",
        "KERNEL_CONFORMANCE_PROFILE_V06_CURRENT",
        "KERNEL_CONFORMANCE_PROFILE_V06_HISTORICAL",
        "KERNEL_CONFORMANCE_PROFILE_V07_CURRENT",
        "DEFAULT_KERNEL_CONFORMANCE_PROFILE",
        "HISTORICAL_KERNEL_CONFORMANCE_ACTIVE_REFS_V05",
        "HISTORICAL_KERNEL_CONFORMANCE_ACTIVE_REFS_V06",
        "CURRENT_KERNEL_CONFORMANCE_ACTIVE_REFS_V06",
        "CURRENT_KERNEL_CONFORMANCE_ACTIVE_REFS_V07",
        "_ACTIVE_ACT_SOURCES",
        "_ACTIVE_ACT_IDS",
        "_CURRENT_SEAMS",
        "_EXECUTED_RUNTIME_ACT_IDS",
        "_EXECUTED_CONFORMANCE_ACT_IDS",
        "_EVIDENCE_ONLY_ACT_IDS",
        "_HISTORICAL_EVIDENCE_ACT_IDS",
        "_HISTORICAL_SEAMS",
    }
)

POST_E6_SHARED_REPORT_ASSERTION_FIELDS = frozenset(
    {
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
    }
)
POST_E6_SHARED_FIXED_REPORT_VALUES = (
    ("continuous_delta_runtime_execution_count", 1),
    ("continuous_delta_runtime_public_validation_status", "PASS"),
    ("shared_conformance_e5_collector_calls", 0),
    ("continuous_delta_runtime_second_execution_count", 0),
    ("continuous_delta_runtime_cache_reuse_count", 0),
    ("continuous_delta_runtime_test_fixture_substitution_count", 0),
    ("continuous_delta_runtime_private_g2d_calls", 0),
    ("continuous_delta_runtime_reconstructed_case_count", 0),
)
POST_E6_SHARED_SHA256_FIELDS = (
    "continuous_delta_runtime_report_sha256",
    "shared_conformance_e5_report_sha256",
)
POST_E6_SHARED_BYTE_COUNT_FIELDS = (
    "continuous_delta_runtime_report_bytes",
    "shared_conformance_e5_report_bytes",
)
POST_E6_LIVING_GEOMETRY_ASSERTIONS = (
    ("runner_version", "v1.6"),
    ("kernel_conformance_profile", POST_E6_PROFILE_ID),
    (
        "historical_kernel_conformance_profile",
        POST_E6_IMMEDIATE_HISTORICAL_PROFILE_ID,
    ),
    ("active_act_results", POST_E6_LIVING_ACT_IDS),
)
POST_E6_CONFORMANCE_GEOMETRY_ASSERTIONS = (
    ("conformance_version", "v0.7"),
    ("profile_id", POST_E6_PROFILE_ID),
    ("historical_profile_ref", POST_E6_IMMEDIATE_HISTORICAL_PROFILE_ID),
    ("category_results", tuple(item[0] for item in POST_E6_CATEGORY_CHECK_IDS)),
    ("category_results", POST_E6_CATEGORY_CHECK_IDS),
    ("negative_test_results", POST_E6_NEGATIVE_PROBE_IDS),
    ("active_gauntlet_refs", POST_E6_ACTIVE_REFS),
    ("domain_results", PRESERVED_DOMAIN_IDS),
)

CRITICAL_MUTATING_METHODS_V03 = frozenset(
    {
        "update",
        "setdefault",
        "pop",
        "popitem",
        "clear",
        "__setitem__",
        "__delitem__",
        "setitem",
        "delitem",
        "append",
        "extend",
        "insert",
        "remove",
        "reverse",
        "sort",
        "add",
        "discard",
        "difference_update",
        "intersection_update",
        "symmetric_difference_update",
        "__iadd__",
        "__iand__",
        "__imul__",
        "__ior__",
        "__isub__",
        "__ixor__",
    }
)
CRITICAL_READ_ONLY_CALLS_V03 = frozenset(
    {
        "all",
        "any",
        "dict",
        "enumerate",
        "frozenset",
        "isinstance",
        "iter",
        "len",
        "list",
        "repr",
        "reversed",
        "set",
        "sorted",
        "str",
        "tuple",
        "zip",
    }
)
CRITICAL_READ_ONLY_METHODS_V03 = frozenset(
    {"copy", "get", "items", "keys", "values"}
)

HISTORICAL_EVIDENCE_STRUCTURAL_ALLOWLIST_V03 = (
    (
        "kernel_conformance",
        "module",
        "binding:_GATE1_ACTIVE_GAUNTLET_REFS_V01",
    ),
    (
        "kernel_conformance",
        "module",
        "binding:_G2A_ACTIVE_GAUNTLET_REFS_V02",
    ),
    (
        "kernel_conformance",
        "module",
        "binding:_G2B_ACTIVE_GAUNTLET_REFS_V03",
    ),
    (
        "kernel_conformance",
        "module",
        "binding:_G2C_ACTIVE_GAUNTLET_REFS_V04",
    ),
    (
        "kernel_conformance",
        "module",
        "binding:_V05_HISTORICAL_ACTIVE_GAUNTLET_REFS",
    ),
    (
        "kernel_conformance",
        "function:kernel_conformance_profile_metadata_v01",
        "return_field:historical_act_id",
    ),
    (
        "kernel_conformance_runner",
        "module",
        "binding:_V05_HISTORICAL_BASE_ACT_IDS",
    ),
    (
        "living_gauntlet",
        "module",
        "binding:HISTORICAL_KERNEL_CONFORMANCE_ACTIVE_REFS_V05",
    ),
    (
        "living_gauntlet",
        "module",
        "binding:_EVIDENCE_ONLY_ACT_IDS",
    ),
    (
        "living_gauntlet",
        "module",
        "binding:_HISTORICAL_EVIDENCE_ACT_IDS",
    ),
    (
        "living_gauntlet",
        "module",
        "binding:_HISTORICAL_SEAMS",
    ),
    (
        "living_gauntlet",
        "function:_validate_completion_manifest_v01",
        "binding:expected_profiles.historical_v0_5.historical_act_id",
    ),
)
CURRENT_REGRESSION_CLAIM_TO_ACTS = (
    (
        "root_sole_local_final_commit_authority",
        ("root_decision_kernel", "action_packet_lifecycle", "fractal_runtime"),
    ),
    ("no_superroot_exists", ("generic_multiroot",)),
    (
        "bsep_semantic_membrane",
        ("execution_mode_router", "fractal_runtime"),
    ),
    ("runtime_execution_topology_runtime_owned", ("fractal_runtime",)),
    (
        "provider_model_advisory_only",
        ("semantic_work_contract", "fractal_runtime"),
    ),
    (
        "actor_output_cannot_create_final_output",
        ("semantic_work_contract", "fractal_runtime"),
    ),
    ("resultproposal_postvv_terminal_gt_before_root", ("fractal_runtime",)),
    (
        "drs_retrieval_reuse_no_authority",
        ("drs_semantic_address_and_reuse_certificate",),
    ),
    ("receipt_evidence_only", ("effect_firewall", "action_packet_lifecycle")),
    ("effect_capability_bounded_corridor_only", ("effect_firewall",)),
    (
        "airline_supplier_same_authority_law",
        (
            "airline_deterministic_transaction_runtime",
            "supplier_water_filter_portability",
            "action_packet_lifecycle",
        ),
    ),
    ("real_world_effects_zero", CURRENT_V06_ACTIVE_REFS),
)

RETIRED_SCHEMA_PATHS = (
    "schemas/attractor_" + "packet.schema.json",
    "schemas/plan_" + "graph.schema.json",
)
CURRENT_SCHEMA_PATHS = (
    "schemas/common.schema.json",
    "schemas/continuous_delta_runtime_v01.schema.json",
    "schemas/drs_meaning_record_v01.schema.json",
    "schemas/drs_memory_resolution_v01.schema.json",
    "schemas/drs_semantic_address_v01.schema.json",
    "schemas/execution_mode_router_v01.schema.json",
    "schemas/fractal_runtime_v02.schema.json",
    "schemas/gt_report.schema.json",
    "schemas/kernel_artifact_v01.schema.json",
    "schemas/result_proposal.schema.json",
    "schemas/reuse_certificate_v01.schema.json",
    "schemas/semantic_work_v01.schema.json",
    "schemas/time_envelope.schema.json",
    "schemas/vv_report.schema.json",
)
REQUIRED_SCHEMA_ISOLATION_INVARIANTS = (
    "RETIRED_SCHEMAS_ARE_NOT_CURRENT",
    "RETIRED_SCHEMAS_EXCLUDED_FROM_SUCCESSOR_ONBOARDING",
    "RETIRED_SCHEMAS_NOT_REGISTERED_BY_CURRENT_LOADER",
    "GIT_BYTE_PRESERVATION_ALLOWED",
    "HISTORICAL_TEST_REFERENCES_OUTSIDE_CURRENT_CONFORMANCE_ONLY",
)
RETIRED_RUNTIME_MODULE_PATHS = (
    "hedgehog/architect.py",
    "hedgehog/architect_prompt_compiler.py",
    "hedgehog/executor.py",
    "hedgehog/fractal_dag_executor.py",
    "hedgehog/llm_architect.py",
    "hedgehog/root_orchestrator.py",
    "hedgehog/trace_reporter.py",
)
RETIRED_MODULE_NAMES = frozenset(
    path[:-3].replace("/", ".") for path in RETIRED_RUNTIME_MODULE_PATHS
)
RETIRED_IMPORT_SCOPE_LABELS = {
    "current_gate1": "CURRENT_GATE1_RETIRED_IMPORTS",
    "current_gate2": "CURRENT_GATE2_RETIRED_IMPORTS",
    "living_gauntlet": "LIVING_GAUNTLET_RETIRED_IMPORTS",
    "kernel_conformance": "KERNEL_CONFORMANCE_RETIRED_IMPORTS",
    "e5": "E5_RETIRED_IMPORTS",
}

GLOBAL_ARCHITECTURE_SCOPE = "current_global_architecture_law"
OPERATIONAL_SCOPE = "operational_instructions_subordinate_to_architecture_lock"
PUBLIC_VIEW_SCOPE = "public_engineering_view_only"
SUCCESSOR_CONTEXT_SCOPE = "successor_context_selection_only"
NAMED_GATE_SCOPE = "named_gate_contract_only"
STATUS_EVIDENCE_SCOPE = "status_or_evidence_only"
AUDIT_EVIDENCE_SCOPE = "audit_evidence_only"
FUTURE_REFERENCE_SCOPE = "future_research_reference_only"
RETIRED_INVENTORY_SCOPE = "retired_architecture_inventory_only"
CURRENT_SCHEMA_SURFACE_SCOPE = "current_schema_surface_index_only"
KNOWN_AUTHORITY_SCOPES = frozenset(
    {
        GLOBAL_ARCHITECTURE_SCOPE,
        OPERATIONAL_SCOPE,
        PUBLIC_VIEW_SCOPE,
        SUCCESSOR_CONTEXT_SCOPE,
        NAMED_GATE_SCOPE,
        STATUS_EVIDENCE_SCOPE,
        AUDIT_EVIDENCE_SCOPE,
        FUTURE_REFERENCE_SCOPE,
        RETIRED_INVENTORY_SCOPE,
        CURRENT_SCHEMA_SURFACE_SCOPE,
    }
)
BOUNDED_AUTHORITATIVE_SCOPES = frozenset({OPERATIONAL_SCOPE, NAMED_GATE_SCOPE})

PRE_CLOSURE_AGENTS_ONBOARDING_WARNINGS = (
    ("manifest_status", "`SUCCESSOR_ONBOARDING_READY`"),
    ("onboarding_ready", "its `onboarding_ready` value is `true`"),
    (
        "s1_s2_s3_closed",
        "S1 document-authority succession, S2 vocabulary repair, and S3 "
        "active-schema and retired-subsystem isolation are closed.",
    ),
    (
        "architecture_clean",
        "The bounded successor context is architecture-clean and ready for guarded "
        "reintegration.",
    ),
    (
        "permanent_onboarding_guarded",
        "Permanent assistant onboarding occurs only after the sanitation changes are "
        "reintegrated into the primary worktree and the three deferred E5 paths are "
        "verified against the owner's exact frozen hashes.",
    ),
    (
        "e5_worktree_untouched",
        "The primary dirty E5 worktree remains untouched",
    ),
    (
        "no_retired_revival",
        "no compatibility, migration, alias, or revival path exists.",
    ),
)
REQUIRED_AGENTS_ONBOARDING_WARNINGS = (
    ("manifest_status", "`SUCCESSOR_ONBOARDING_READY`"),
    ("onboarding_ready", "its `onboarding_ready` value is `true`"),
    (
        "s1_s2_s3_closed",
        "S1 document-authority succession, S2 vocabulary repair, and S3 "
        "active-schema and retired-subsystem isolation are closed.",
    ),
    (
        "architecture_clean",
        "The bounded successor context is architecture-clean and ready for guarded "
        "use.",
    ),
    (
        "checkpoint_onboarded",
        "The exact committed G2-E successor and its current checkpoint are permanent "
        "bounded onboarding inputs.",
    ),
    (
        "audit_explicit_only",
        "The independent G2-E audit remains explicit-request evidence",
    ),
    (
        "no_retired_revival",
        "no compatibility, migration, alias, or revival path exists.",
    ),
)
REQUIRED_GATE_SCOPE_NOTE = (
    "Named Gate authority cannot redefine global topology, Root sovereignty, "
    "BSEP, runtime ownership, or another Gate's contract."
)

FUTURE_REFERENCE_PATH = (
    "specs/future/quantum/"
    "hedgehog_quantum_mathematical_extension_roadmap_v2_0.md"
)
FUTURE_REFERENCE_MANIFEST_EXCLUSION = "specs/future/**"
FUTURE_REFERENCE_ROLE = (
    "Future mathematical extension roadmap; not current runtime, Gate contract, "
    "implementation, completion claim, or architecture authority."
)

PRE_CLOSURE_REQUIRED_CURRENT_CLASSIFICATIONS = {
    "current_normative_documents": {
        LOCK_PATH: (
            "current_normative_architecture_lock",
            True,
            True,
            GLOBAL_ARCHITECTURE_SCOPE,
            False,
        ),
    },
    "current_operational_documents": {
        "AGENTS.md": (
            "current_operational_view_after_s1",
            True,
            True,
            OPERATIONAL_SCOPE,
            False,
        ),
        "README.md": (
            "current_public_engineering_view_after_s1",
            False,
            True,
            PUBLIC_VIEW_SCOPE,
            False,
        ),
        MANIFEST_PATH: (
            "successor_onboarding_ready_after_s3",
            False,
            True,
            SUCCESSOR_CONTEXT_SCOPE,
            False,
        ),
        RETIRED_INVENTORY_PATH: (
            "s3_retired_architecture_inventory",
            False,
            True,
            RETIRED_INVENTORY_SCOPE,
            False,
        ),
        CURRENT_SCHEMA_SURFACE_PATH: (
            "s3_current_schema_surface_index",
            False,
            True,
            CURRENT_SCHEMA_SURFACE_SCOPE,
            False,
        ),
    },
    "current_technical_annexes": {
        "docs/domain_neutral_reference_kernel_gate1_checkpoint_v01.md": (
            "accepted_gate1_checkpoint",
            True,
            True,
            NAMED_GATE_SCOPE,
            False,
        ),
        "docs/actionpacket_lifecycle_kill_switch_g2_a_checkpoint_v01.md": (
            "accepted_gate2_g2a_checkpoint",
            True,
            True,
            NAMED_GATE_SCOPE,
            False,
        ),
        "docs/drs_semantic_address_space_reuse_certificate_g2_b_checkpoint_v01.md": (
            "accepted_gate2_g2b_checkpoint",
            True,
            True,
            NAMED_GATE_SCOPE,
            False,
        ),
        "docs/execution_mode_router_g2_c_checkpoint_v01.md": (
            "accepted_gate2_g2c_checkpoint",
            True,
            True,
            NAMED_GATE_SCOPE,
            False,
        ),
        "docs/fractal_runtime_v0_2_g2_d_post_acceptance_contract_addendum_v01.md": (
            "accepted_cumulative_gate2_g2d_contract",
            True,
            True,
            NAMED_GATE_SCOPE,
            False,
        ),
        (
            "docs/fractal_runtime_v0_2_g2_d_profile_d_t12_revise_projection_"
            "correction_checkpoint_v01.md"
        ): (
            "accepted_current_gate2_g2d_checkpoint",
            True,
            True,
            NAMED_GATE_SCOPE,
            False,
        ),
        "docs/continuous_delta_runtime_v0_1_g2_e_preflight_v01.md": (
            "accepted_repository_gate_continuation_contract",
            True,
            True,
            NAMED_GATE_SCOPE,
            False,
        ),
        "docs/continuous_delta_runtime_v0_1_g2_e_post_acceptance_contract_addendum_v01.md": (
            "accepted_cumulative_gate2_g2e_contract",
            True,
            True,
            NAMED_GATE_SCOPE,
            False,
        ),
        E6_RECONCILIATION_ANNEX_PATH: (
            "accepted_g2e6_sanitized_basis_reconciliation_contract",
            True,
            True,
            NAMED_GATE_SCOPE,
            False,
        ),
        "release/current_status_overlay_v01.json": (
            "current_lifecycle_metadata_view",
            False,
            True,
            STATUS_EVIDENCE_SCOPE,
            False,
        ),
        "release/claim_to_evidence_index.md": (
            "current_claim_evidence_navigation",
            False,
            True,
            STATUS_EVIDENCE_SCOPE,
            False,
        ),
        "release/current_limitations.md": (
            "current_limitations_view",
            False,
            True,
            STATUS_EVIDENCE_SCOPE,
            False,
        ),
        "release/current_release_notes.md": (
            "current_engineering_notes_view",
            False,
            True,
            STATUS_EVIDENCE_SCOPE,
            False,
        ),
    },
    "future_reference_documents": {
        FUTURE_REFERENCE_PATH: (
            "future_reference_non_current",
            False,
            False,
            FUTURE_REFERENCE_SCOPE,
            False,
        ),
    },
    "audit_only_sources": {
        "docs/audit_reports/**": (
            "audit_only",
            False,
            False,
            AUDIT_EVIDENCE_SCOPE,
            False,
        ),
        "docs/evidence/**": (
            "evidence_only",
            False,
            False,
            AUDIT_EVIDENCE_SCOPE,
            False,
        ),
        "release/completion_manifest.json": (
            "current_release_completion_and_profile_index",
            False,
            True,
            STATUS_EVIDENCE_SCOPE,
            False,
        ),
        "release/integration_seam_index.json": (
            "current_release_integration_and_profile_index",
            False,
            True,
            STATUS_EVIDENCE_SCOPE,
            False,
        ),
        "release/integration_seam_index.md": (
            "historical_release_basis_overlay",
            False,
            True,
            STATUS_EVIDENCE_SCOPE,
            False,
        ),
    },
}
REQUIRED_CURRENT_CLASSIFICATIONS = {
    category: dict(entries)
    for category, entries in PRE_CLOSURE_REQUIRED_CURRENT_CLASSIFICATIONS.items()
}
REQUIRED_CURRENT_CLASSIFICATIONS["current_technical_annexes"][
    G2E_CHECKPOINT_PATH
] = (
    "accepted_g2e_continuous_delta_runtime_closure_checkpoint",
    True,
    True,
    NAMED_GATE_SCOPE,
    False,
)
REQUIRED_CURRENT_CLASSIFICATIONS["current_technical_annexes"][
    G2F_PREFLIGHT_PATH
] = (
    "accepted_g2f_v13r1_full_validator_closure_candidate",
    True,
    True,
    NAMED_GATE_SCOPE,
    False,
)
REQUIRED_CURRENT_CLASSIFICATIONS["audit_only_sources"][G2E_AUDIT_PATH] = (
    "accepted_g2e_closure_audit_evidence",
    False,
    False,
    AUDIT_EVIDENCE_SCOPE,
    False,
)

_RETIRED_PLAN_STEM = "plan" + "_" + "graph"
_RETIRED_PACKET_STEM = "attractor" + "_" + "packet"
REQUIRED_RETIRED_EXCLUDE_PATHS = frozenset(
    {
        "hedgehog/mode_router.py",
        "demo/run_mode_selection_matrix.py",
        "tests/test_mode_router_runtime.py",
        "tests/test_mode_selection_matrix_runner.py",
        "hedgehog/architect.py",
        "hedgehog/architect_prompt_compiler.py",
        "hedgehog/llm_architect.py",
        "hedgehog/fractal_cell_integration.py",
        "hedgehog/fractal_dag_executor.py",
        "hedgehog/fractal_fulfillment.py",
        "hedgehog/bounded_actor_contracts.py",
        "hedgehog/root_orchestrator.py",
        "hedgehog/executor.py",
        "hedgehog/trace_reporter.py",
        "hedgehog/needle_runtime.py",
        "schemas/needle.schema.json",
        f"schemas/{_RETIRED_PACKET_STEM}.schema.json",
        f"schemas/{_RETIRED_PLAN_STEM}.schema.json",
        f"demo/run_architect_from_bounded_{_RETIRED_PACKET_STEM}.py",
        "demo/run_avf_attractor_from_accepted_matrix.py",
        f"demo/run_dag_executor_from_valid_{_RETIRED_PLAN_STEM}.py",
        "demo/run_bounded_llm_semantic_executor_node_v01.py",
        "demo/run_gemini_orchestrator_architect_pair_smoke.py",
        "demo/run_fractal_cell_runtime_integration_v01.py",
        "demo/run_fractal_cell_runtime.py",
        "demo/run_fractal_dag_executor_core.py",
        "demo/run_controlled_fractal_dac_expansion_v01.py",
        "demo/run_dual_fractal_coupling_v01.py",
        "demo/run_full_semantic_e2e_v01.py",
        "demo/run_controlled_root_orchestrator_route_assembly.py",
        f"tests/test_architect_from_bounded_{_RETIRED_PACKET_STEM}_runner.py",
        "tests/test_avf_attractor_from_accepted_matrix_runner.py",
        f"tests/test_dag_executor_from_valid_{_RETIRED_PLAN_STEM}_runner.py",
        "tests/test_bounded_llm_semantic_executor_node_v01_runner.py",
        "tests/test_gemini_orchestrator_architect_pair_smoke_runner.py",
        "tests/test_architect_runtime.py",
        "tests/test_architect_prompt_compiler_runtime.py",
        "tests/test_llm_architect_runtime.py",
        "tests/test_fractal_cell_runtime_integration_v01_runner.py",
        "tests/test_fractal_cell_runtime_runner.py",
        "tests/test_fractal_dag_executor_core_runner.py",
        "tests/test_fractal_fulfillment_core.py",
        "tests/test_controlled_fractal_dac_expansion_v01_runner.py",
        "tests/test_dual_fractal_coupling_v01_runner.py",
        "tests/test_full_semantic_e2e_v01_runner.py",
        "tests/test_executor_runtime.py",
        "tests/test_executor_no_final_output.py",
        "tests/test_root_orchestrator_runtime.py",
        "tests/test_controlled_root_orchestrator_route_assembly_runner.py",
        "tests/test_post_vv_runtime.py",
        "tests/test_gt_validator_runtime.py",
        "tests/test_up_never_mutates_work.py",
        "tests/test_work_thoughts_up_separation.py",
        HISTORICAL_ALL_LAYERS_RUNNER_PATH,
        HISTORICAL_ALL_LAYERS_TEST_PATH,
    }
)
REQUIRED_EXCLUDE_GLOBS = frozenset(
    {
        "docs/audit_reports/**",
        "docs/evidence/**",
        "docs/showcase/**",
        FUTURE_REFERENCE_MANIFEST_EXCLUSION,
        "demo/run_human_*.py",
        "tests/test_human_*_runner.py",
        "demo/run_live_*.py",
        "tests/test_live_*.py",
        "demo/run_*showcase*.py",
        "tests/test_*showcase*_runner.py",
        "needles/**",
        "docs/*needle*.md",
        "demo/run_*needle*.py",
        "tests/test_*needle*.py",
        "hedgehog/marenna*.py",
        "hedgehog/up*.py",
        "schemas/marenna*.json",
        "schemas/up*.json",
        "tests/test_marenna*.py",
        "data/**",
        "_audit_exports/**",
        "**/__pycache__/**",
        "**/*.pyc",
    }
)

# Fragment construction keeps retired direct strings out of this source file.
FORBIDDEN_DIRECT_TERMS = (
    "Plan" + "Graph",
    "plan" + "_" + "graph",
    "Attractor" + "Packet",
    "attractor" + "_" + "packet",
)
REQUIRED_CURRENT_TERMS = ("BSEP", "RuntimeExecutionTopology")
SCANNED_CURRENT_DOCUMENTS = ("AGENTS.md", "README.md", LOCK_PATH)

STRUCTURED_RATIONALE_PATH = "hedgehog/structured_rationale.py"
SUPPLIER_EVENT_SOURCE_PATHS = (
    "demo/run_full_wow_v1_2_product_trace.py",
    "hedgehog/domains/supplier_water_filter/kernel_adapter_v01.py",
    (
        "hedgehog/domains/supplier_water_filter/"
        "sealed_evidence_package_adapter_v01.py"
    ),
)
_RETIRED_TITLE_PLAN = "Plan" + "Graph"
_RETIRED_SUPPLIER_EVENT = "runtime_" + "plan" + "graph_compiled"
_REQUIRED_SUPPLIER_EVENT = "runtime_execution_topology_materialized"
_RETIRED_STRUCTURED_POSITIVE_TERMS = (
    "bounded_" + _RETIRED_PLAN_STEM,
    _RETIRED_TITLE_PLAN + " remains advisory until validated",
    _RETIRED_TITLE_PLAN + " contract",
)
_FORBIDDEN_E5_TOPOLOGY_OWNERSHIP_PATTERNS = (
    re.compile(
        r"(?<![A-Za-z0-9])(?:provider|model)[\s_-]*"
        r"(?:owns?|owned|creates?|created|materializes?|materialized)[\s_-]*"
        r"(?:runtime[\s_-]*execution[\s_-]*)?topology\b",
        re.IGNORECASE,
    ),
    re.compile(
        r"(?<![A-Za-z0-9])(?:runtime[\s_-]*execution[\s_-]*)?topology"
        r"[\s_-]*(?:is[\s_-]*)?(?:owned|created|materialized)[\s_-]*by"
        r"[\s_-]*(?:provider|model)\b",
        re.IGNORECASE,
    ),
)


class DuplicateJSONKeyError(ValueError):
    """Raised when a JSON object contains a duplicate key."""


def _reject_duplicate_keys(pairs: list[tuple[str, object]]) -> dict[str, object]:
    result: dict[str, object] = {}
    for key, value in pairs:
        if key in result:
            raise DuplicateJSONKeyError(f"duplicate key: {key}")
        result[key] = value
    return result


class StaticValueUnavailable(ValueError):
    """Raised when an assignment is not a bounded literal composition."""


def _static_value(node: ast.AST, values: dict[str, object]) -> object:
    if isinstance(node, ast.Constant):
        return node.value
    if isinstance(node, ast.Name) and node.id in values:
        return values[node.id]
    if isinstance(node, (ast.Tuple, ast.List)):
        items: list[object] = []
        for element in node.elts:
            if isinstance(element, ast.Starred):
                expanded = _static_value(element.value, values)
                if not isinstance(expanded, (tuple, list)):
                    raise StaticValueUnavailable
                items.extend(expanded)
            else:
                items.append(_static_value(element, values))
        return tuple(items) if isinstance(node, ast.Tuple) else items
    if isinstance(node, ast.Dict):
        result: dict[object, object] = {}
        for key_node, value_node in zip(node.keys, node.values, strict=True):
            if key_node is None:
                expanded = _static_value(value_node, values)
                if not isinstance(expanded, dict):
                    raise StaticValueUnavailable
                result.update(expanded)
            else:
                result[_static_value(key_node, values)] = _static_value(
                    value_node, values
                )
        return result
    if isinstance(node, ast.Subscript):
        container = _static_value(node.value, values)
        key = _static_value(node.slice, values)
        try:
            return container[key]  # type: ignore[index]
        except (KeyError, IndexError, TypeError):
            raise StaticValueUnavailable from None
    if (
        isinstance(node, ast.Call)
        and isinstance(node.func, ast.Name)
        and node.func.id == "tuple"
        and len(node.args) == 1
        and not node.keywords
    ):
        value = _static_value(node.args[0], values)
        if not isinstance(value, (tuple, list, dict)):
            raise StaticValueUnavailable
        return tuple(value)
    if isinstance(node, ast.BinOp) and isinstance(node.op, ast.Add):
        left = _static_value(node.left, values)
        right = _static_value(node.right, values)
        if type(left) is type(right) and isinstance(left, (str, bytes, tuple, list)):
            return left + right
        raise StaticValueUnavailable
    raise StaticValueUnavailable


def _static_assignments(
    source_path: Path,
    code: str,
    failures: list[str],
) -> tuple[dict[str, object], ast.Module | None, str]:
    try:
        source = source_path.read_text(encoding="utf-8")
    except (OSError, UnicodeError) as exc:
        failures.append(f"{code}.read:{type(exc).__name__}")
        return {}, None, ""
    try:
        tree = ast.parse(source, filename=str(source_path))
    except SyntaxError:
        failures.append(f"{code}.syntax")
        return {}, None, source
    pending: list[tuple[str, ast.AST]] = []
    for statement in tree.body:
        if isinstance(statement, ast.Assign) and len(statement.targets) == 1:
            target = statement.targets[0]
            if isinstance(target, ast.Name):
                pending.append((target.id, statement.value))
        elif isinstance(statement, ast.AnnAssign) and isinstance(
            statement.target, ast.Name
        ) and statement.value is not None:
            pending.append((statement.target.id, statement.value))
    values: dict[str, object] = {}
    while pending:
        next_pending: list[tuple[str, ast.AST]] = []
        progressed = False
        for name, node in pending:
            try:
                values[name] = _static_value(node, values)
            except StaticValueUnavailable:
                next_pending.append((name, node))
            else:
                progressed = True
        if not progressed:
            break
        pending = next_pending
    return values, tree, source


def _load_json(path: Path, code: str, failures: list[str]) -> dict[str, object] | None:
    try:
        raw = path.read_text(encoding="utf-8")
    except (OSError, UnicodeError) as exc:
        failures.append(f"{code}.read:{type(exc).__name__}")
        return None
    try:
        value = json.loads(raw, object_pairs_hook=_reject_duplicate_keys)
    except (json.JSONDecodeError, DuplicateJSONKeyError) as exc:
        failures.append(f"{code}.json:{type(exc).__name__}")
        return None
    if not isinstance(value, dict):
        failures.append(f"{code}.root_type")
        return None
    return value


def _file_identity(path: Path) -> tuple[str, int, int] | None:
    try:
        data = path.read_bytes()
    except OSError:
        return None
    return hashlib.sha256(data).hexdigest(), len(data), data.count(b"\n")


def _validate_exact_identities(
    repo_root: Path,
    expected: dict[str, tuple[str, int, int]],
    code: str,
    failures: list[str],
) -> None:
    for relative_path, expected_identity in expected.items():
        identity = _file_identity(repo_root / relative_path)
        if identity is None:
            failures.append(f"{code}.missing:{relative_path}")
        elif identity != expected_identity:
            failures.append(f"{code}.identity:{relative_path}")


def _validate_git_blob_identities_v01(
    repo_root: Path,
    commit: str,
    expected: dict[str, tuple[str, int, int]],
    code: str,
    failures: list[str],
) -> None:
    for relative_path, expected_identity in expected.items():
        try:
            completed = subprocess.run(
                ("git", "show", f"{commit}:{relative_path}"),
                cwd=repo_root,
                check=False,
                capture_output=True,
            )
        except OSError as exc:
            failures.append(
                f"{code}.read:{relative_path}:{type(exc).__name__}"
            )
            continue
        if completed.returncode != 0:
            failures.append(
                f"{code}.missing:{relative_path}:exit_{completed.returncode}"
            )
            continue
        data = completed.stdout
        observed = (
            hashlib.sha256(data).hexdigest(),
            len(data),
            data.count(b"\n"),
        )
        if observed != expected_identity:
            failures.append(f"{code}.identity:{relative_path}")


def _valid_relative_pattern(value: object) -> bool:
    if (
        not isinstance(value, str)
        or not value
        or "\\" in value
        or any(ord(character) < 32 or ord(character) == 127 for character in value)
    ):
        return False
    path = PurePosixPath(value)
    return (
        not path.is_absolute()
        and str(path) == value
        and all(part not in {"", ".", ".."} for part in path.parts)
    )


def _load_reconciliation_contract(
    repo_root: Path,
    failures: list[str],
) -> dict[str, object] | None:
    path = repo_root / E6_RECONCILIATION_ANNEX_PATH
    try:
        source = path.read_text(encoding="ascii")
    except (OSError, UnicodeError) as exc:
        failures.append(f"e6.annex.read:{type(exc).__name__}")
        return None
    begin = "<!-- BEGIN HEDGEHOG_G2E6_SANITIZED_BASIS_RECONCILIATION_V01 -->"
    end = "<!-- END HEDGEHOG_G2E6_SANITIZED_BASIS_RECONCILIATION_V01 -->"
    if source.count(begin) != 1 or source.count(end) != 1:
        failures.append("e6.annex.machine_block.markers")
        return None
    block = source.split(begin, 1)[1].split(end, 1)[0].strip()
    if not block.startswith("```json\n") or not block.endswith("\n```"):
        failures.append("e6.annex.machine_block.fence")
        return None
    try:
        value = json.loads(
            block[len("```json\n") : -len("\n```")],
            object_pairs_hook=_reject_duplicate_keys,
        )
    except (json.JSONDecodeError, DuplicateJSONKeyError):
        failures.append("e6.annex.machine_block.json")
        return None
    if not isinstance(value, dict):
        failures.append("e6.annex.machine_block.root_type")
        return None
    return value


def _validate_reconciliation_contract(
    value: dict[str, object] | None,
    failures: list[str],
) -> None:
    if value is None:
        return
    exact_scalars = {
        "protocol": "HEDGEHOG_G2E6_SANITIZED_BASIS_RECONCILIATION_V01",
        "contract_status": "CLASS_A_RECONCILIATION_ONLY",
        "repository_basis_commit": E5_IMPLEMENTATION_BASIS_COMMIT,
        "repository_basis_subject": (
            "Implement G2-E5 continuous delta runtime acceptance"
        ),
        "conflict_class": "STALE_E6_PROFILE_AND_RELEASE_GEOMETRY",
        "ARCHITECTURE_CONFLICT": False,
        "E5_INVALIDATED": False,
        "G2E_REDESIGN_REQUIRED": False,
        "E6_IMPLEMENTATION_STATUS": "NOT_STARTED_NOT_AUTHORIZED_BY_CLASS_A",
        "G2E_STATUS": "NOT_CLOSED",
        "GATE2_STATUS": "NOT_CLOSED",
        "PUBLIC_RELEASE_STATUS": "NOT_CLAIMED",
        "RC2_STATUS": "NOT_CLAIMED",
        "PRODUCTION_READINESS_STATUS": "NOT_CLAIMED",
        "AUTHORITY_CREATED": False,
        "PERMISSION_CREATED": False,
        "ACTION_PACKET_CREATED": False,
        "RECEIPT_CREATED": False,
        "FINAL_OUTPUT_CREATED": False,
        "EXTERNAL_ACTION_CREATED": False,
        "REAL_WORLD_EFFECTS_COUNT": 0,
    }
    for key, expected in exact_scalars.items():
        if value.get(key) != expected:
            failures.append(f"e6.annex.exact:{key}")

    archive = value.get("accepted_reconciliation_archive")
    expected_archive = {
        "path": (
            "/Users/admin/Downloads/"
            "HEDGEHOG_G2E6_SANITIZED_BASIS_RECONCILIATION_"
            "20260826T181617Z.tar.gz"
        ),
        "sha256": (
            "5a9e2efdd8718cba9abd671b989ba4613fe0b79160e0994c9f023e3ac1ebbc6b"
        ),
        "bytes": 28990,
        "status": "READ_ONLY_BOUNDED_RECONCILIATION_EVIDENCE",
    }
    if archive != expected_archive:
        failures.append("e6.annex.reconciliation_archive.exact")

    current = value.get("current_pre_e6")
    if not isinstance(current, dict):
        failures.append("e6.annex.current_pre_e6.type")
        current = {}
    current_expected = {
        "phase_id": "PRE_E6_RECONCILED",
        "living_version": "v1.5",
        "living_act_ids": list(PRE_E6_LIVING_ACT_IDS),
        "living_act_count": 16,
        "conformance_core_version": "v0.6",
        "conformance_runner_version": "v0.6",
        "current_profile_id": CURRENT_PROFILE_ID,
        "immediate_historical_profile_id": HISTORICAL_PROFILE_ID,
        "historical_v0_5_active_refs": list(HISTORICAL_V05_ACTIVE_REFS),
        "category_ids": [item[0] for item in PRE_E6_CATEGORY_CHECK_IDS],
        "category_count": 14,
        "domain_ids": list(PRESERVED_DOMAIN_IDS),
        "domain_count": 2,
        "negative_probe_ids": list(PRE_E6_NEGATIVE_PROBE_IDS),
        "negative_probe_count": 50,
        "active_refs": list(CURRENT_V06_ACTIVE_REFS),
        "active_ref_count": 15,
        "all_layers_invariant_super_smoke": (
            "HISTORICAL_EVIDENCE_ONLY_NOT_CURRENT"
        ),
    }
    if current != current_expected:
        failures.append("e6.annex.current_pre_e6.exact")

    successor = value.get("future_post_e6")
    if not isinstance(successor, dict):
        failures.append("e6.annex.future_post_e6.type")
        successor = {}
    successor_expected = {
        "phase_id": "POST_E6_SUCCESSOR",
        "living_version": "v1.6",
        "living_immediate_historical_version": "v1.5",
        "living_preserved_prefix_count": 16,
        "living_appended_act_id": "continuous_delta_runtime",
        "living_appended_act_position": 17,
        "living_resulting_act_count": 17,
        "conformance_core_version": "v0.7",
        "conformance_runner_version": "v0.7",
        "current_profile_id": POST_E6_PROFILE_ID,
        "immediate_historical_profile_id": (
            POST_E6_IMMEDIATE_HISTORICAL_PROFILE_ID
        ),
        "preserved_earlier_profile_id": HISTORICAL_PROFILE_ID,
        "profile_succession": [
            HISTORICAL_PROFILE_ID,
            POST_E6_IMMEDIATE_HISTORICAL_PROFILE_ID,
            POST_E6_PROFILE_ID,
        ],
        "preserved_category_prefix_count": 14,
        "appended_category_id": "ContinuousDeltaRuntimeConformance",
        "appended_category_position": 15,
        "resulting_category_count": 15,
        "appended_check_ids": list(E6_CATEGORY_CHECK_IDS),
        "preserved_negative_probe_prefix_count": 50,
        "appended_probe_ids": list(E6_NEGATIVE_PROBE_IDS),
        "appended_probe_positions": list(range(51, 61)),
        "resulting_negative_probe_count": 60,
        "preserved_active_ref_prefix_count": 15,
        "appended_active_ref_id": "continuous_delta_runtime",
        "appended_active_ref_position": 16,
        "resulting_active_ref_count": 16,
        "preserved_domain_ids": list(PRESERVED_DOMAIN_IDS),
        "all_layers_invariant_super_smoke": (
            "HISTORICAL_EVIDENCE_ONLY_NEVER_REBOUND"
        ),
    }
    if successor != successor_expected:
        failures.append("e6.annex.future_post_e6.exact")

    e5 = value.get("committed_e5_basis")
    expected_e5 = {
        "implementation_commit": E5_IMPLEMENTATION_BASIS_COMMIT,
        "status": "IMPLEMENTED_COMMITTED_ACCEPTANCE_PASS",
        "paths": [
            {
                "path": path,
                "sha256": identity[0],
                "bytes": identity[1],
                "lf": identity[2],
            }
            for path, identity in FROZEN_E5_IDENTITIES.items()
        ],
    }
    if e5 != expected_e5:
        failures.append("e6.annex.committed_e5_basis.exact")

    predecessor = value.get("frozen_predecessor_evidence")
    expected_predecessor = {
        "completion_manifest_path": COMPLETION_MANIFEST_PATH,
        "completion_manifest_sha256": (
            FROZEN_PREDECESSOR_EVIDENCE_IDENTITIES[COMPLETION_MANIFEST_PATH][0]
        ),
        "integration_seam_index_path": SEAM_INDEX_PATH,
        "integration_seam_index_sha256": (
            FROZEN_PREDECESSOR_EVIDENCE_IDENTITIES[SEAM_INDEX_PATH][0]
        ),
        "classification": "FROZEN_PREDECESSOR_EVIDENCE_NOT_CURRENT_E6_PASS",
    }
    if predecessor != expected_predecessor:
        failures.append("e6.annex.frozen_predecessor_evidence.exact")

    path_classes = value.get("path_classes")
    if not isinstance(path_classes, dict):
        failures.append("e6.annex.path_classes.type")
        path_classes = {}
    class_a = path_classes.get("CLASS_A_CONTRACT_OR_CONTROL_PLANE_RECONCILIATION")
    class_b = path_classes.get("CLASS_B_E6_IMPLEMENTATION")
    if not isinstance(class_a, list) or set(class_a) != set(CLASS_A_RECONCILIATION_PATHS):
        failures.append("e6.annex.path_classes.class_a_exact")
    if not isinstance(class_b, list) or set(class_b) != set(CLASS_B_E6_IMPLEMENTATION_PATHS):
        failures.append("e6.annex.path_classes.class_b_exact")
    class_values = [item for item in path_classes.values() if isinstance(item, list)]
    seen: set[str] = set()
    for items in class_values:
        overlap = seen & set(items)
        if overlap:
            failures.append("e6.annex.path_classes.overlap")
        seen.update(items)

    call_ownership = value.get("call_ownership")
    expected_call_ownership = {
        "direct_conformance_e5_collector_calls": 1,
        "living_e5_collector_calls": 1,
        "living_shared_conformance_builder_e5_collector_calls": 0,
        "shared_report_law": (
            "SAME_SEALED_CANONICAL_PUBLICLY_VALIDATED_E5_REPORT"
        ),
        "proof_law": (
            "SEALED_CANONICAL_IDENTITY_AND_BYTES_NOT_PYTHON_OBJECT_IDENTITY"
        ),
        "global_cache_allowed": False,
        "cross_invocation_reuse_allowed": False,
        "stale_report_allowed": False,
        "test_fixture_as_current_report_allowed": False,
        "consumer_reconstructs_e5_cases": False,
        "consumer_imports_tests": False,
        "consumer_calls_private_g2d": False,
        "consumer_calls_second_delta_runtime": False,
        "accepted_e5_call_characterization_seconds_approximate": 2040,
        "direct_conformance_operational_hang_guard_seconds": 7200,
        "full_living_operational_hang_guard_seconds": 10800,
        "hang_guards_are_latency_or_gate_claims": False,
    }
    if call_ownership != expected_call_ownership:
        failures.append("e6.annex.call_ownership.exact")


def _valid_relative_path(value: object) -> bool:
    return _valid_relative_pattern(value) and not any(
        character in value for character in "*?["
    )


def _valid_relative_glob(value: object) -> bool:
    return _valid_relative_pattern(value) and any(
        character in value for character in "*?["
    )


def _validate_unique_string_list(
    value: object,
    code: str,
    failures: list[str],
    *,
    require_paths: bool = True,
    allow_globs: bool = False,
) -> tuple[str, ...]:
    if not isinstance(value, list) or not all(isinstance(item, str) for item in value):
        failures.append(f"{code}.type")
        return ()
    items = tuple(value)
    if len(set(items)) != len(items):
        failures.append(f"{code}.duplicate")
    if require_paths:
        validator = _valid_relative_pattern if allow_globs else _valid_relative_path
        if any(not validator(item) for item in items):
            failures.append(f"{code}.path")
    return items


def _validate_unique_glob_list(
    value: object,
    code: str,
    failures: list[str],
) -> tuple[str, ...]:
    if not isinstance(value, list) or not all(isinstance(item, str) for item in value):
        failures.append(f"{code}.type")
        return ()
    items = tuple(value)
    if len(set(items)) != len(items):
        failures.append(f"{code}.duplicate")
    if any(not _valid_relative_glob(item) for item in items):
        failures.append(f"{code}.path")
    return items


def _validate_document_entries(
    value: object,
    code: str,
    failures: list[str],
    *,
    allow_globs: bool = False,
) -> tuple[dict[str, object], ...]:
    if not isinstance(value, list):
        failures.append(f"{code}.type")
        return ()
    entries: list[dict[str, object]] = []
    paths: list[str] = []
    for index, entry in enumerate(value):
        item_code = f"{code}[{index}]"
        if not isinstance(entry, dict):
            failures.append(f"{item_code}.type")
            continue
        if tuple(entry) != CURRENT_DOCUMENT_ENTRY_KEYS:
            failures.append(f"{item_code}.shape")
            continue
        path = entry.get("path")
        validator = _valid_relative_pattern if allow_globs else _valid_relative_path
        if not validator(path):
            failures.append(f"{item_code}.path")
        else:
            paths.append(path)
        if not isinstance(entry.get("status"), str) or not entry.get("status"):
            failures.append(f"{item_code}.status")
        if type(entry.get("current_authority")) is not bool:
            failures.append(f"{item_code}.current_authority")
        if not isinstance(entry.get("authority_scope"), str) or not entry.get(
            "authority_scope"
        ):
            failures.append(f"{item_code}.authority_scope")
        if type(entry.get("may_override_architecture_lock")) is not bool:
            failures.append(f"{item_code}.may_override_architecture_lock")
        if type(entry.get("onboarding_allowed")) is not bool:
            failures.append(f"{item_code}.onboarding_allowed")
        if not isinstance(entry.get("role"), str) or not entry.get("role"):
            failures.append(f"{item_code}.role")
        entries.append(entry)
    if len(set(paths)) != len(paths):
        failures.append(f"{code}.duplicate_path")
    return tuple(entries)


def _validate_historical_entries(
    value: object,
    failures: list[str],
) -> tuple[dict[str, object], ...]:
    code = "authority_index.historical_documents"
    if not isinstance(value, list):
        failures.append(f"{code}.type")
        return ()
    entries: list[dict[str, object]] = []
    paths: list[str] = []
    for index, entry in enumerate(value):
        item_code = f"{code}[{index}]"
        if not isinstance(entry, dict):
            failures.append(f"{item_code}.type")
            continue
        if tuple(entry) != HISTORICAL_ENTRY_KEYS:
            failures.append(f"{item_code}.shape")
            continue
        path = entry.get("path")
        if not _valid_relative_path(path):
            failures.append(f"{item_code}.path")
            continue
        paths.append(path)
        if entry.get("status") != "historical_reference":
            failures.append(f"historical.status:{path}")
        if entry.get("historical_git_ref") != f"{BASE_HEAD}:{path}":
            failures.append(f"historical.git_ref:{path}")
        if entry.get("current_authority") is not False:
            failures.append(f"historical.current_authority:{path}")
        if entry.get("onboarding_allowed") is not False:
            failures.append(f"historical.onboarding_allowed:{path}")
        if entry.get("preservation") != "byte history in Git":
            failures.append(f"historical.preservation:{path}")
        replacement = entry.get("current_replacement")
        if replacement is not None and not _valid_relative_path(replacement):
            failures.append(f"historical.current_replacement:{path}")
        entries.append(entry)
    if len(set(paths)) != len(paths):
        failures.append(f"{code}.duplicate_path")
    missing = sorted(set(REQUIRED_HISTORICAL_PATHS) - set(paths))
    for path in missing:
        failures.append(f"historical.missing:{path}")
    return tuple(entries)


def _validate_authority_index(
    value: dict[str, object] | None,
    failures: list[str],
    *,
    closure_active: bool = False,
    g2f_active: bool = False,
) -> tuple[dict[str, object], ...]:
    if value is None:
        return ()
    expected_index_keys = (
        ("g2f_landing_transition", *AUTHORITY_INDEX_KEYS)
        if g2f_active and "g2f_landing_transition" in value
        else AUTHORITY_INDEX_KEYS
    )
    if tuple(value) != expected_index_keys:
        failures.append("authority_index.top_level_shape")
    if not isinstance(value.get("schema_version"), str) or not value.get("schema_version"):
        failures.append("authority_index.schema_version")
    expected_generated_head = (
        G2E_CLOSURE_COMMIT
        if g2f_active
        else G2E_CLOSURE_BASIS_COMMIT
        if closure_active
        else BASE_HEAD
    )
    if value.get("generated_for_head") != expected_generated_head:
        failures.append("authority_index.generated_for_head")

    category_entries: dict[str, tuple[dict[str, object], ...]] = {}
    current_entries: list[dict[str, object]] = []
    for key in (
        "current_normative_documents",
        "current_operational_documents",
        "current_technical_annexes",
        "future_reference_documents",
        "audit_only_sources",
    ):
        entries = _validate_document_entries(
            value.get(key),
            f"authority_index.{key}",
            failures,
            allow_globs=key == "audit_only_sources",
        )
        category_entries[key] = entries
        current_entries.extend(entries)
    historical_entries = _validate_historical_entries(
        value.get("historical_documents"), failures
    )
    excluded = _validate_unique_string_list(
        value.get("excluded_from_successor_onboarding"),
        "authority_index.excluded_from_successor_onboarding",
        failures,
        allow_globs=True,
    )
    source_order = _validate_unique_string_list(
        value.get("source_of_truth_order"),
        "authority_index.source_of_truth_order",
        failures,
        require_paths=False,
    )
    notes = _validate_unique_string_list(
        value.get("notes"),
        "authority_index.notes",
        failures,
        require_paths=False,
    )
    if not notes:
        failures.append("authority_index.notes.empty")
    if REQUIRED_GATE_SCOPE_NOTE not in notes:
        failures.append("authority_index.notes.missing_gate_scope_law")
    if not source_order or source_order[0] != LOCK_PATH:
        failures.append("authority_index.source_of_truth_order.first")

    classifications = (
        REQUIRED_CURRENT_CLASSIFICATIONS
        if g2f_active
        else {
            category: {
                path: expected
                for path, expected in entries.items()
                if path != G2F_PREFLIGHT_PATH
            }
            for category, entries in REQUIRED_CURRENT_CLASSIFICATIONS.items()
        }
        if closure_active
        else PRE_CLOSURE_REQUIRED_CURRENT_CLASSIFICATIONS
    )
    for category, required_entries in classifications.items():
        entries_by_path = {
            entry.get("path"): entry
            for entry in category_entries.get(category, ())
            if isinstance(entry.get("path"), str)
        }
        for path in sorted(set(entries_by_path) - set(required_entries)):
            failures.append(f"authority_index.{category}.unexpected:{path}")
        for path, expected in required_entries.items():
            entry = entries_by_path.get(path)
            if entry is None:
                failures.append(f"authority_index.{category}.missing:{path}")
                continue
            (
                expected_status,
                expected_authority,
                expected_onboarding,
                expected_scope,
                expected_override,
            ) = expected
            if entry.get("status") != expected_status:
                failures.append(f"authority_index.{category}.status:{path}")
            if entry.get("current_authority") is not expected_authority:
                failures.append(f"authority_index.{category}.authority:{path}")
            if entry.get("onboarding_allowed") is not expected_onboarding:
                failures.append(f"authority_index.{category}.onboarding:{path}")
            if entry.get("authority_scope") != expected_scope:
                failures.append(f"authority_index.{category}.scope:{path}")
            if entry.get("may_override_architecture_lock") is not expected_override:
                failures.append(f"authority_index.{category}.override:{path}")

    for category, entries in category_entries.items():
        for entry in entries:
            path = entry.get("path")
            authority_scope = entry.get("authority_scope")
            current_authority = entry.get("current_authority")
            may_override = entry.get("may_override_architecture_lock")
            if authority_scope not in KNOWN_AUTHORITY_SCOPES:
                failures.append(f"authority_index.unknown_authority_scope:{path}")
            if may_override is not False:
                failures.append(
                    f"authority_index.may_override_architecture_lock:{path}"
                )
            if authority_scope == GLOBAL_ARCHITECTURE_SCOPE and path != LOCK_PATH:
                failures.append(f"authority_index.global_scope_not_lock:{path}")
            if (
                current_authority is True
                and path != LOCK_PATH
                and authority_scope not in BOUNDED_AUTHORITATIVE_SCOPES
            ):
                failures.append(
                    f"authority_index.current_authority_unbounded_scope:{path}"
                )
            if category == "current_normative_documents" and (
                path != LOCK_PATH or authority_scope != GLOBAL_ARCHITECTURE_SCOPE
            ):
                failures.append(f"authority_index.normative_scope:{path}")
            if category == "current_technical_annexes":
                if current_authority is True and authority_scope != NAMED_GATE_SCOPE:
                    failures.append(f"authority_index.gate_annex.scope:{path}")
                if (
                    current_authority is False
                    and authority_scope != STATUS_EVIDENCE_SCOPE
                ):
                    failures.append(f"authority_index.status_evidence.scope:{path}")
            if category == "audit_only_sources":
                is_wildcard = isinstance(path, str) and any(
                    character in path for character in "*?["
                )
                expected_audit_scope = (
                    AUDIT_EVIDENCE_SCOPE
                    if is_wildcard or path == G2E_AUDIT_PATH
                    else STATUS_EVIDENCE_SCOPE
                )
                if authority_scope != expected_audit_scope:
                    failures.append(f"authority_index.audit.scope:{path}")
            if category == "future_reference_documents":
                if current_authority is not False:
                    failures.append(f"future_reference.current_authority:{path}")
                if authority_scope != FUTURE_REFERENCE_SCOPE:
                    failures.append(f"future_reference.authority_scope:{path}")
                if entry.get("onboarding_allowed") is not False:
                    failures.append(f"future_reference.onboarding_allowed:{path}")

    manifest_entries = {
        entry.get("path"): entry
        for entry in category_entries.get("current_operational_documents", ())
        if isinstance(entry.get("path"), str)
    }
    manifest_entry = manifest_entries.get(MANIFEST_PATH)
    if manifest_entry is None or manifest_entry.get("current_authority") is not False:
        failures.append("authority_index.successor_manifest_has_authority")

    for entry in category_entries.get("current_normative_documents", ()):
        path = entry.get("path")
        if entry.get("current_authority") is not True:
            failures.append(f"authority_index.normative_without_authority:{path}")
        if entry.get("onboarding_allowed") is not True:
            failures.append(f"authority_index.normative_not_onboarded:{path}")
    for category in ("current_operational_documents", "current_technical_annexes"):
        for entry in category_entries.get(category, ()):
            if entry.get("onboarding_allowed") is not True:
                failures.append(
                    f"authority_index.current_not_onboarded:{entry.get('path')}"
                )
    for entry in category_entries.get("audit_only_sources", ()):
        if entry.get("current_authority") is not False:
            failures.append(f"authority_index.audit_has_authority:{entry.get('path')}")
    for entry in category_entries.get("future_reference_documents", ()):
        path = entry.get("path")
        if entry.get("may_override_architecture_lock") is not False:
            failures.append(f"future_reference.may_override_architecture_lock:{path}")
        if path == FUTURE_REFERENCE_PATH and entry.get("role") != FUTURE_REFERENCE_ROLE:
            failures.append(f"future_reference.role:{path}")

    categories_by_path: dict[str, list[str]] = {}
    for category, entries in category_entries.items():
        for entry in entries:
            path = entry.get("path")
            if isinstance(path, str):
                categories_by_path.setdefault(path, []).append(category)
    for path, categories in sorted(categories_by_path.items()):
        if len(categories) > 1:
            failures.append(f"authority_index.cross_category_duplicate:{path}")

    current_paths = {
        entry.get("path")
        for entry in current_entries
        if isinstance(entry.get("path"), str)
    }
    historical_paths = {
        entry.get("path")
        for entry in historical_entries
        if isinstance(entry.get("path"), str)
    }
    all_historical_paths = set(REQUIRED_HISTORICAL_PATHS) | historical_paths
    for path in sorted(all_historical_paths):
        if any(path in source for source in source_order):
            failures.append(f"historical.in_source_of_truth_order:{path}")
    for path in sorted(historical_paths & current_paths):
        failures.append(f"historical.listed_as_current:{path}")
    for path in historical_paths:
        if path not in excluded:
            failures.append(f"historical.not_index_excluded:{path}")
    if FUTURE_REFERENCE_PATH not in excluded:
        failures.append("future_reference.index_exclusion_missing")
    future_paths = {
        entry.get("path")
        for entry in category_entries.get("future_reference_documents", ())
        if isinstance(entry.get("path"), str)
    }
    for path in sorted(future_paths):
        if any(path in source for source in source_order):
            failures.append(f"future_reference.in_source_of_truth_order:{path}")
        if path not in excluded:
            failures.append(f"future_reference.not_index_excluded:{path}")
    return historical_entries


def _validate_manifest(
    value: dict[str, object] | None,
    failures: list[str],
    historical_paths: Iterable[str],
    *,
    closure_active: bool = False,
    g2f_active: bool = False,
) -> tuple[tuple[str, ...], frozenset[str]]:
    if value is None:
        return (), frozenset()
    expected_keys = (
        MANIFEST_KEYS
        if g2f_active
        else G2E_CLOSURE_MANIFEST_KEYS
        if closure_active
        else PRE_CLOSURE_MANIFEST_KEYS
    )
    if g2f_active and "g2f_landing_transition" in value:
        expected_keys = ("g2f_landing_transition", *expected_keys)
    if tuple(value) != expected_keys:
        failures.append("successor_manifest.top_level_shape")
    if not isinstance(value.get("schema_version"), str) or not value.get("schema_version"):
        failures.append("successor_manifest.schema_version")
    expected_base_head = (
        G2E_CLOSURE_COMMIT
        if g2f_active
        else G2E_CLOSURE_BASIS_COMMIT
        if closure_active
        else BASE_HEAD
    )
    if value.get("base_head") != expected_base_head:
        failures.append("successor_manifest.base_head")
    if value.get("manifest_status") != REQUIRED_MANIFEST_STATUS:
        failures.append("successor_manifest.manifest_status")
    if value.get("onboarding_ready") is not True:
        failures.append("successor_manifest.onboarding_ready")
    blocking_repairs = _validate_unique_string_list(
        value.get("blocking_repairs"),
        "successor_manifest.blocking_repairs",
        failures,
        require_paths=False,
    )
    if blocking_repairs != REQUIRED_BLOCKING_REPAIRS:
        failures.append("successor_manifest.blocking_repairs.exact")
    if value.get("onboarding_ready") is True and blocking_repairs:
        failures.append("successor_manifest.ready_with_blocking_repairs")
    if value.get("onboarding_ready") is False and not blocking_repairs:
        failures.append("successor_manifest.not_ready_without_blocking_repairs")
    for key in ("purpose", "historical_access_method", "validation_command"):
        if not isinstance(value.get(key), str) or not value.get(key):
            failures.append(f"successor_manifest.{key}")
    purpose = value.get("purpose")
    if isinstance(purpose, str):
        required_phrases = (
            (
                "S3 active-schema and retired-subsystem isolation",
                "guarded reintegration",
                "exact committed E5 implementation basis",
                "exact committed G2-E6 successor basis",
                "does not authorize G2-F implementation",
            )
            if closure_active
            else (
                "S3 active-schema and retired-subsystem isolation",
                "guarded reintegration",
                "exact committed E5 implementation basis",
                "does not authorize Class-B E6 implementation",
            )
        )
        for required_phrase in required_phrases:
            if required_phrase not in purpose:
                failures.append(
                    "successor_manifest.purpose.ready_scope:"
                    f"{required_phrase.replace(' ', '_')}"
                )
        if g2f_active:
            for required_phrase in (
                "corrected G2-F Class-A preflight candidate",
                "does not authorize G2-F implementation",
            ):
                if required_phrase not in purpose:
                    failures.append(
                        "successor_manifest.purpose.g2f_scope:"
                        f"{required_phrase.replace(' ', '_')}"
                    )
    if value.get("validation_command") != (
        "python3 tools/check_active_architecture_authority_v01.py"
    ):
        failures.append("successor_manifest.validation_command.exact")

    path_lists: dict[str, tuple[str, ...]] = {}
    for key in (
        "always_include",
        "include_current_gate_sources",
        "include_current_gate_tests",
        "include_current_release_sources",
        "exclude_paths",
        "authority_documents",
    ):
        path_lists[key] = _validate_unique_string_list(
            value.get(key), f"successor_manifest.{key}", failures
        )
    exclude_globs = _validate_unique_glob_list(
        value.get("exclude_globs"),
        "successor_manifest.exclude_globs",
        failures,
    )

    checkpoint_requirement = {G2E_CHECKPOINT_PATH} if closure_active else set()
    g2f_requirement = {G2F_PREFLIGHT_PATH} if g2f_active else set()
    required_sets = (
        (
            "always_include",
            REQUIRED_ALWAYS_INCLUDE | checkpoint_requirement | g2f_requirement,
        ),
        (
            "include_current_gate_sources",
            REQUIRED_GATE_SOURCES | checkpoint_requirement | g2f_requirement,
        ),
        ("include_current_gate_tests", REQUIRED_GATE_TESTS),
        ("include_current_release_sources", REQUIRED_RELEASE_SOURCES),
    )
    for key, required in required_sets:
        missing = sorted(required - set(path_lists.get(key, ())))
        for path in missing:
            failures.append(f"successor_manifest.{key}.missing:{path}")

    authority_documents = path_lists.get("authority_documents", ())
    if not authority_documents or authority_documents[0] != LOCK_PATH:
        failures.append("successor_manifest.authority_documents.first")
    required_authority_documents = {
        LOCK_PATH,
        INDEX_PATH,
        MANIFEST_PATH,
        "AGENTS.md",
        "README.md",
    }
    if closure_active:
        required_authority_documents.add(G2E_CHECKPOINT_PATH)
    if g2f_active:
        required_authority_documents.add(G2F_PREFLIGHT_PATH)
    for path in sorted(required_authority_documents - set(authority_documents)):
        failures.append(f"successor_manifest.authority_documents.missing:{path}")

    committed = value.get("committed_e5_basis")
    committed_paths: list[str] = []
    if not isinstance(committed, dict):
        failures.append("successor_manifest.committed_e5_basis.type")
        committed = {}
    elif tuple(committed) != COMMITTED_E5_BASIS_KEYS:
        failures.append("successor_manifest.committed_e5_basis.shape")
    expected_basis_values = {
        "implementation_commit": E5_IMPLEMENTATION_BASIS_COMMIT,
        "implementation_subject": (
            "Implement G2-E5 continuous delta runtime acceptance"
        ),
        "status": "IMPLEMENTED_COMMITTED_ACCEPTANCE_PASS",
        "e6_implementation_status": "NOT_STARTED_NOT_AUTHORIZED_BY_CLASS_A",
        "g2e_status": "NOT_CLOSED",
        "gate2_status": "NOT_CLOSED",
    }
    for key, expected in expected_basis_values.items():
        if committed.get(key) != expected:
            failures.append(f"successor_manifest.committed_e5_basis.{key}")
    committed_entries = committed.get("paths")
    if not isinstance(committed_entries, list):
        failures.append("successor_manifest.committed_e5_basis.paths.type")
    else:
        for index, entry in enumerate(committed_entries):
            code = f"successor_manifest.committed_e5_basis.paths[{index}]"
            if not isinstance(entry, dict):
                failures.append(f"{code}.type")
                continue
            if tuple(entry) != COMMITTED_E5_ENTRY_KEYS:
                failures.append(f"{code}.shape")
                continue
            path = entry.get("path")
            if not _valid_relative_path(path):
                failures.append(f"{code}.path")
                continue
            committed_paths.append(path)
            expected_identity = FROZEN_E5_IDENTITIES.get(path)
            if expected_identity is None:
                failures.append(f"{code}.unexpected_path")
                continue
            expected_sha, expected_bytes, expected_lf = expected_identity
            if entry.get("sha256") != expected_sha:
                failures.append(f"{code}.sha256")
            if entry.get("bytes") != expected_bytes:
                failures.append(f"{code}.bytes")
            if entry.get("lf") != expected_lf:
                failures.append(f"{code}.lf")
        if len(set(committed_paths)) != len(committed_paths):
            failures.append("successor_manifest.committed_e5_basis.paths.duplicate")
    if set(committed_paths) != set(REQUIRED_E5_PATHS):
        failures.append("successor_manifest.committed_e5_basis.paths.exact")

    if closure_active:
        committed_e6 = value.get("committed_e6_basis")
        if not isinstance(committed_e6, dict):
            failures.append("successor_manifest.committed_e6_basis.type")
            committed_e6 = {}
        elif tuple(committed_e6) != COMMITTED_E6_BASIS_KEYS:
            failures.append("successor_manifest.committed_e6_basis.shape")
        expected_e6_values = {
            "class_a_commit": G2E_CLASS_A_COMMIT,
            "class_a_subject": "Reconcile G2-E6 Class-A control plane",
            "class_b_commit": G2E_CLASS_B_COMMIT,
            "class_b_subject": (
                "Integrate G2-E6 Living Gauntlet and Kernel Conformance"
            ),
            "control_plane_repair_commit": G2E_CLOSURE_BASIS_COMMIT,
            "control_plane_repair_subject": (
                "Repair G2-E6 post-successor control-plane tests"
            ),
            "status": "IMPLEMENTED_COMMITTED_ACCEPTANCE_PASS",
            "runtime_phase": "POST_E6_SUCCESSOR",
            "lifecycle_phase": "G2E_CLOSED_PASS",
            "audit_path": G2E_AUDIT_PATH,
            "audit_sha256": G2E_AUDIT_SHA256,
            "checkpoint_path": G2E_CHECKPOINT_PATH,
            "checkpoint_sha256": G2E_CHECKPOINT_SHA256,
            "g2e_status": "CLOSED_PASS",
            "g2f_status": "NEXT_NOT_STARTED_NOT_AUTHORIZED",
            "g2f_implementation_authorized": False,
            "gate2_status": "NOT_CLOSED",
            "public_release_status": "NOT_CLAIMED",
            "rc2_status": "NOT_CLAIMED",
            "production_readiness_status": "NOT_CLAIMED",
            "production_security_certification_status": "NOT_CLAIMED",
            "real_world_effects_count": 0,
        }
        for key, expected in expected_e6_values.items():
            if committed_e6.get(key) != expected:
                failures.append(f"successor_manifest.committed_e6_basis.{key}")

        for key, identities in (
            ("class_b_paths", POST_E6_CLASS_B_IDENTITIES),
            ("control_plane_test_paths", POST_E6_CONTROL_TEST_IDENTITIES),
        ):
            entries = committed_e6.get(key)
            observed_paths: list[str] = []
            if not isinstance(entries, list):
                failures.append(
                    f"successor_manifest.committed_e6_basis.{key}.type"
                )
                continue
            for index, entry in enumerate(entries):
                code = f"successor_manifest.committed_e6_basis.{key}[{index}]"
                if not isinstance(entry, dict):
                    failures.append(f"{code}.type")
                    continue
                if tuple(entry) != COMMITTED_E5_ENTRY_KEYS:
                    failures.append(f"{code}.shape")
                    continue
                path = entry.get("path")
                if not isinstance(path, str) or path not in identities:
                    failures.append(f"{code}.path")
                    continue
                observed_paths.append(path)
                expected_sha, expected_bytes, expected_lf = identities[path]
                if entry.get("sha256") != expected_sha:
                    failures.append(f"{code}.sha256")
                if entry.get("bytes") != expected_bytes:
                    failures.append(f"{code}.bytes")
                if entry.get("lf") != expected_lf:
                    failures.append(f"{code}.lf")
            if len(observed_paths) != len(set(observed_paths)):
                failures.append(
                    f"successor_manifest.committed_e6_basis.{key}.duplicate"
                )
            if set(observed_paths) != set(identities):
                failures.append(
                    f"successor_manifest.committed_e6_basis.{key}.exact"
                )

        v10_evidence = committed_e6.get("v10_evidence")
        expected_v10 = {
            "archive_sha256": (
                "33942d30f59d9f63dafa0c0f633b2f7e53c2b9f8e7f634b1dc798942e97e8573"
            ),
            "archive_bytes": 253612,
            "regular_members": 57,
            "manifest_data_rows": 56,
            "kernel_runtime_tests": 400,
            "living_runtime_tests": 595,
            "release_spine_tests": 32,
            "authority_tests": 941,
            "runtime_evidence_reuse_dependency_proof": "PASS",
        }
        if not isinstance(v10_evidence, dict):
            failures.append(
                "successor_manifest.committed_e6_basis.v10_evidence.type"
            )
        else:
            if tuple(v10_evidence) != V10_EVIDENCE_KEYS:
                failures.append(
                    "successor_manifest.committed_e6_basis.v10_evidence.shape"
                )
            if v10_evidence != expected_v10:
                failures.append(
                    "successor_manifest.committed_e6_basis.v10_evidence.exact"
                )

    if g2f_active:
        succession = value.get("g2f_class_a_succession")
        if not isinstance(succession, dict):
            failures.append("successor_manifest.g2f_class_a_succession.type")
            succession = {}
        expected_scalars = {
            "basis_head": G2F_ORIGINAL_CLASS_A_COMMIT,
            "original_class_a_basis_head": G2F_ORIGINAL_CLASS_A_PARENT,
            "original_class_a_commit": G2F_ORIGINAL_CLASS_A_COMMIT,
            "reconciliation_basis_head": G2F_ORIGINAL_CLASS_A_COMMIT,
            "preflight_path": G2F_PREFLIGHT_PATH,
            "preflight_status": "CLASS_A_181_ROW_RECONCILIATION_CANDIDATE",
            "class_a_status": "V13R1_CANDIDATE_PENDING_OWNER_REVIEW",
            "classification": "ORCHESTRATION_AND_ACCEPTANCE_ONLY",
            "source_basis_head": G2F_ORIGINAL_CLASS_A_COMMIT,
            "public_construction_ledger_rows": 181,
            "construction_ledger_consecutive": True,
            "current_class_a_postimages_reconciled": True,
            "v12r2_runtime_semantic_and_parent_map_status": "ACCEPTED",
            "v12r2_evidence_archive_sha256": G2F_V12R2_ARCHIVE_SHA256,
            "v12r3_executed_producer_basis_status": "ACCEPTED_THROUGH_V12R6",
            "v12r3_reconciliation_readiness_status": "SUPERSEDED_BY_V12R4",
            "v12r3_all_anti_fitting_hostiles_status": "SUPERSEDED_BY_V12R4",
            "v12r4_proof_status": (
                "ACCEPTED_AS_REGRESSION_PROVENANCE_SUPERSEDED_BY_V12R5"
            ),
            "v12r4_evidence_archive_sha256": G2F_V12R4_ARCHIVE_SHA256,
            "v12r4_executed_producer_basis_sha256": (
                G2F_EXECUTED_PRODUCER_BASIS_SHA256_V13
            ),
            "v12r5_reconciliation_readiness_status": "SUPERSEDED",
            "v12r5_reconciliation_readiness_scope": "ONLY_TERMINAL_READINESS",
            "v12r5_reconciliation_readiness_superseded_by": (
                "V12R6_FULL_CORRIDOR_EXTERNAL_PROOF"
            ),
            "v12r5_evidence_archive_sha256": G2F_V12R5_ARCHIVE_SHA256,
            "v12r5_executed_producer_basis_status": "ACCEPTED",
            "v12r5_executed_producer_basis_scope": (
                "IMMUTABLE_REGRESSION_EVIDENCE"
            ),
            "v12r5_row099_source_receipt_binding_status": "ACCEPTED",
            "v12r5_row099_source_receipt_binding_scope": (
                "IMMUTABLE_REGRESSION_EVIDENCE"
            ),
            "v12r5_clean_runtime_and_semantic_projection_status": "ACCEPTED",
            "v12r5_clean_runtime_and_semantic_projection_scope": (
                "IMMUTABLE_REGRESSION_EVIDENCE"
            ),
            "v12r5_clean_causal_and_local_use_projection_status": "ACCEPTED",
            "v12r5_clean_causal_and_local_use_projection_scope": (
                "REGRESSION_TARGET"
            ),
            "v12r5_executed_32_negative_regression_results_status": "ACCEPTED",
            "v12r5_executed_32_negative_regression_results_scope": (
                "HISTORICAL_TESTED_SCOPE"
            ),
            "v12r5_full_byte_corridor_statement_coverage_status": "NOT_PROVEN",
            "v12r5_full_byte_corridor_statement_coverage_scope": (
                "PROOF_ANALYZER_DEFECT_ONLY"
            ),
            "g2f_v12r6_result": (
                "PASS_READY_FOR_V13_EXACT_SEVEN_PATH_CLASS_A_181_ROW_RECONCILIATION"
            ),
            "v12r6_scope": "EXTERNAL_PROOF_ONLY",
            "v12r6_full_corridor_external_proof_status": (
                "DIRECT_AUTHORITY_FOR_V13_RECONCILIATION"
            ),
            "v12r6_full_corridor_external_proof_scope": (
                "NO_IMPLEMENTATION_OR_RECONCILIATION_AUTHORITY"
            ),
            "v12r6_evidence_archive_sha256": G2F_V12R6_ARCHIVE_SHA256,
            "v12r6_executed_producer_basis_sha256": (
                G2F_EXECUTED_PRODUCER_BASIS_SHA256_V13
            ),
            "v12r6_full_corridor_statement_coverage_status": "PASS_EXACT",
            "v12r6_total_executed_negative_regression_count": 315,
            "v13_input_archive_sha256": G2F_V13_ARCHIVE_SHA256,
            "v13_owner_readiness_status": (
                "SUPERSEDED_BY_V13R1_VALIDATOR_CLOSURE"
            ),
            "v13r1_validator_closure_status": (
                "FULL_181_ROW_EXPECTED_SIDE_RECONSTRUCTED_CANDIDATE"
            ),
            "implementation_authorization": (
                "NOT_AUTHORIZED_PENDING_OWNER_RECONCILIATION_COMMIT_"
                "AND_SEPARATE_REAUTHORIZATION"
            ),
            "reconciliation_path_count": 7,
            "runtime_implementation_performed": False,
            "repository_g2f_lifecycle_status": (
                "G2F_CLASS_A_181_ROW_RECONCILIATION_CANDIDATE"
            ),
            "g2f_status": "NOT_CLOSED",
            "gate2_status": "NOT_CLOSED",
            "public_release_status": "NOT_CLAIMED",
            "rc2_status": "NOT_CLAIMED",
            "production_readiness_status": "NOT_CLAIMED",
            "production_security_certification_status": "NOT_CLAIMED",
            "real_world_effects_count": 0,
        }
        for key, expected in expected_scalars.items():
            if succession.get(key) != expected:
                failures.append(f"successor_manifest.g2f.{key}")

        def validate_path_actions(
            key: str,
            expected: dict[str, str],
        ) -> tuple[dict[str, object], ...]:
            records = succession.get(key)
            if not isinstance(records, list):
                failures.append(f"successor_manifest.g2f.{key}.type")
                return ()
            observed: dict[str, str] = {}
            valid_records: list[dict[str, object]] = []
            for index, record in enumerate(records):
                code = f"successor_manifest.g2f.{key}[{index}]"
                if not isinstance(record, dict):
                    failures.append(f"{code}.type")
                    continue
                path = record.get("path")
                action = record.get("action")
                if not _valid_relative_path(path):
                    failures.append(f"{code}.path")
                    continue
                if path in observed:
                    failures.append(f"successor_manifest.g2f.{key}.duplicate:{path}")
                    continue
                observed[path] = action if isinstance(action, str) else ""
                valid_records.append(record)
            if observed != expected:
                failures.append(f"successor_manifest.g2f.{key}.exact")
            return tuple(valid_records)

        validate_path_actions(
            "original_class_a_paths",
            {
                path: "ADD" if status == "A" else "MODIFY"
                for path, status in G2F_ORIGINAL_CLASS_A_COMMITTED_NAME_STATUS.items()
            },
        )
        validate_path_actions(
            "reconciliation_paths",
            {path: "MODIFY" for path in G2F_CLASS_A_PATHS},
        )
        original_postimages = succession.get("original_class_a_postimages")
        observed_original_postimages: dict[str, tuple[object, object, object]] = {}
        if not isinstance(original_postimages, list):
            failures.append("successor_manifest.g2f.original_postimages.type")
        else:
            for index, record in enumerate(original_postimages):
                code = f"successor_manifest.g2f.original_postimages[{index}]"
                if not isinstance(record, dict):
                    failures.append(f"{code}.type")
                    continue
                path = record.get("path")
                if not _valid_relative_path(path) or path in observed_original_postimages:
                    failures.append(f"{code}.path")
                    continue
                observed_original_postimages[path] = (
                    record.get("sha256"),
                    record.get("bytes"),
                    record.get("lf"),
                )
        if observed_original_postimages != G2F_ORIGINAL_CLASS_A_POSTIMAGE_IDENTITIES:
            failures.append("successor_manifest.g2f.original_postimages.exact")
        validate_path_actions(
            "future_implementation_paths",
            {path: "ADD" for path in G2F_IMPLEMENTATION_PATHS},
        )
        closure_actions = {
            path: (
                "ADD"
                if path
                in {
                    "docs/audit_reports/"
                    "auditor_consolidated_gate2_gauntlet_g2_f_v01.log",
                    "docs/consolidated_gate2_gauntlet_g2_f_checkpoint_v01.md",
                }
                else "MODIFY"
            )
            for path in G2F_CLOSURE_PATHS
        }
        closure_records = validate_path_actions(
            "future_closure_paths", closure_actions
        )
        stable_predecessors = {
            "docs/audit_reports/auditor_consolidated_gate2_gauntlet_g2_f_v01.log": (
                "ABSENT"
            ),
            "docs/consolidated_gate2_gauntlet_g2_f_checkpoint_v01.md": "ABSENT",
            "AGENTS.md": "7d2bc7d21a5a899a1f58abf364a7d1ae6cc015ffec425b7b46674d85d58a083e",
            "README.md": "05f22aa7624e20d01e080bd6efd5bab6a637283c7d715a11f9f414c27972efa5",
            "release/current_status_overlay_v01.json": (
                "05ad2f3a36632d2332fe9d6d5a08b5da3341afb6568088d1f51724b8d566f6f1"
            ),
            "release/claim_to_evidence_index.md": (
                "85dd82c735f2183e1587a8a93e0b53a1bc30e910c39fc96268c462ddad09c6f6"
            ),
            "release/current_limitations.md": (
                "7f8b8e65a29430425148aa16bc7764fe2accc3752aa98ac0140d9606acdb8885"
            ),
            "release/current_release_notes.md": (
                "0af690fce0bd46137114f6b8d8ceeb8c489edc212124b343164b054396ed4347"
            ),
        }
        for record in closure_records:
            path = record.get("path")
            if path in G2F_CLOSURE_OVERLAP_PATHS:
                if record.get("predecessor") != (
                    "RECONCILED_CLASS_A_COMMITTED_POSTIMAGE_"
                    "TO_BE_BOUND_EXACTLY_BEFORE_CLOSURE"
                ) or "predecessor_sha256" in record:
                    failures.append(f"successor_manifest.g2f.closure_deferred:{path}")
            elif stable_predecessors.get(path) == "ABSENT":
                if record.get("predecessor") != "ABSENT":
                    failures.append(f"successor_manifest.g2f.closure_absent:{path}")
            elif record.get("predecessor_sha256") != stable_predecessors.get(path):
                failures.append(f"successor_manifest.g2f.closure_sha256:{path}")
        if succession.get("owner_commit_boundaries") != [
            "ORIGINAL_CLASS_A_COMMIT_PROVENANCE",
            "CLASS_A_181_ROW_RECONCILIATION_EXACT_SEVEN_MODIFY_PATHS",
            "FUTURE_IMPLEMENTATION_EXACT_TWO_ADD_PATHS",
            "FUTURE_CLOSURE_EXACT_FOURTEEN_PATHS",
        ]:
            failures.append("successor_manifest.g2f.owner_commit_boundaries")
        frozen_classes = succession.get("frozen_path_classes")
        if not isinstance(frozen_classes, list) or len(frozen_classes) != 6:
            failures.append("successor_manifest.g2f.frozen_path_classes")

    onboarding_paths: set[str] = set()
    for key in (
        "always_include",
        "include_current_gate_sources",
        "include_current_gate_tests",
        "include_current_release_sources",
        "authority_documents",
    ):
        onboarding_paths.update(path_lists.get(key, ()))

    exclude_paths = set(path_lists.get("exclude_paths", ()))
    for path in sorted(REQUIRED_RETIRED_EXCLUDE_PATHS - exclude_paths):
        failures.append(f"successor_manifest.exclude_paths.missing_retired:{path}")
    for path in (*RETIRED_SCHEMA_PATHS, *RETIRED_RUNTIME_MODULE_PATHS, *HISTORICAL_ALL_LAYERS_PATHS):
        if path not in exclude_paths:
            failures.append(f"successor_manifest.exclude_paths.missing_s3:{path}")
    for pattern in sorted(REQUIRED_EXCLUDE_GLOBS - set(exclude_globs)):
        failures.append(f"successor_manifest.exclude_globs.missing_retired:{pattern}")

    for path in sorted(onboarding_paths & exclude_paths):
        failures.append(f"successor_manifest.exclusion_conflict_path:{path}")
    for path in sorted(onboarding_paths):
        for pattern in exclude_globs:
            if fnmatch.fnmatchcase(path, pattern):
                failures.append(
                    f"successor_manifest.exclusion_conflict_glob:{path}:{pattern}"
                )

    all_historical_paths = set(REQUIRED_HISTORICAL_PATHS) | set(historical_paths)
    for path in sorted(all_historical_paths):
        if path in onboarding_paths:
            failures.append(f"historical.in_successor_context:{path}")
        if path not in exclude_paths:
            failures.append(f"historical.not_manifest_excluded:{path}")
    return tuple(sorted(onboarding_paths)), frozenset()


def _validate_retired_records(
    value: object,
    code: str,
    expected_paths: Iterable[str],
    expected_classification: str,
    failures: list[str],
) -> tuple[str, ...]:
    if not isinstance(value, list):
        failures.append(f"{code}.type")
        return ()
    paths: list[str] = []
    for index, record in enumerate(value):
        item_code = f"{code}[{index}]"
        if not isinstance(record, dict):
            failures.append(f"{item_code}.type")
            continue
        if tuple(record) != RETIRED_RECORD_KEYS:
            failures.append(f"{item_code}.shape")
            continue
        path = record.get("path")
        if not _valid_relative_path(path):
            failures.append(f"{item_code}.path")
            continue
        paths.append(path)
        if record.get("classification") != expected_classification:
            failures.append(f"{code}.classification:{path}")
        for field in (
            "current_runtime_allowed",
            "current_schema_registration_allowed",
            "current_export_allowed",
            "successor_onboarding_allowed",
        ):
            if record.get(field) is not False:
                failures.append(f"{code}.{field}:{path}")
        if record.get("preservation") != "BYTE_HISTORY_IN_GIT":
            failures.append(f"{code}.preservation:{path}")
        if not isinstance(record.get("reason"), str) or not record.get("reason"):
            failures.append(f"{code}.reason:{path}")
    if len(paths) != len(set(paths)):
        failures.append(f"{code}.duplicate_path")
    if set(paths) != set(expected_paths):
        failures.append(f"{code}.paths_exact")
    return tuple(paths)


def _validate_s3_inventory(
    repo_root: Path,
    value: dict[str, object] | None,
    failures: list[str],
) -> tuple[str, ...]:
    if value is None:
        return ()
    if tuple(value) != RETIRED_INVENTORY_KEYS:
        failures.append("s3.retired_inventory.top_level_shape")
    exact_scalars = {
        "inventory_id": "retired_architecture_inventory_v01",
        "inventory_status": "S3_CURRENT_ISOLATION_BASELINE",
        "architecture_lock_ref": LOCK_PATH,
        "generated_from_head": S3_GENERATED_FROM_HEAD,
    }
    for key, expected in exact_scalars.items():
        if value.get(key) != expected:
            failures.append(f"s3.retired_inventory.{key}")
    schema_paths = _validate_retired_records(
        value.get("retired_schema_paths"),
        "s3.retired_inventory.retired_schema_paths",
        RETIRED_SCHEMA_PATHS,
        "RETIRED_SCHEMA_REFERENCE",
        failures,
    )
    runtime_paths = _validate_retired_records(
        value.get("retired_runtime_reference_paths"),
        "s3.retired_inventory.retired_runtime_reference_paths",
        RETIRED_RUNTIME_MODULE_PATHS,
        "RETIRED_RUNTIME_REFERENCE",
        failures,
    )
    family_paths = _validate_retired_records(
        value.get("historical_demo_test_families"),
        "s3.retired_inventory.historical_demo_test_families",
        HISTORICAL_ALL_LAYERS_PATHS,
        "HISTORICAL_DEMO_OR_TEST",
        failures,
    )
    forbidden_uses = _validate_unique_string_list(
        value.get("forbidden_current_uses"),
        "s3.retired_inventory.forbidden_current_uses",
        failures,
        require_paths=False,
    )
    required_uses = {
        "IMPORT_FROM_CURRENT_KERNEL_GATE_OR_E5",
        "EXPORT_FROM_CURRENT_PACKAGE_FACADE",
        "REGISTER_AS_CURRENT_SCHEMA",
        "INCLUDE_IN_SUCCESSOR_ONBOARDING",
        "INVOKE_FROM_CURRENT_LIVING_GAUNTLET_OR_KERNEL_CONFORMANCE",
        "WRAP_ALIAS_MIGRATE_OR_REVIVE",
    }
    if set(forbidden_uses) != required_uses:
        failures.append("s3.retired_inventory.forbidden_current_uses.exact")
    for key in ("preservation_law", "onboarding_law"):
        if not isinstance(value.get(key), str) or not value.get(key):
            failures.append(f"s3.retired_inventory.{key}")
    all_paths = (*schema_paths, *runtime_paths, *family_paths)
    for relative_path in all_paths:
        if not (repo_root / relative_path).is_file():
            failures.append(f"s3.retired_inventory.preserved_path_missing:{relative_path}")
    return tuple(all_paths)


def _validate_current_schema_surface(
    repo_root: Path,
    value: dict[str, object] | None,
    failures: list[str],
) -> tuple[str, ...]:
    if value is None:
        return ()
    if tuple(value) != CURRENT_SCHEMA_SURFACE_KEYS:
        failures.append("s3.current_schema_surface.top_level_shape")
    exact_scalars = {
        "schema_surface_id": "current_schema_surface_v01",
        "schema_surface_status": "CURRENT_SCHEMA_SURFACE_ISOLATED",
        "generated_from_head": S3_GENERATED_FROM_HEAD,
    }
    for key, expected in exact_scalars.items():
        if value.get(key) != expected:
            failures.append(f"s3.current_schema_surface.{key}")
    current_paths = _validate_unique_string_list(
        value.get("current_schema_paths"),
        "s3.current_schema_surface.current_schema_paths",
        failures,
    )
    retired_paths = _validate_unique_string_list(
        value.get("retired_schema_paths"),
        "s3.current_schema_surface.retired_schema_paths",
        failures,
    )
    if tuple(current_paths) != CURRENT_SCHEMA_PATHS:
        failures.append("s3.current_schema_surface.current_schema_paths.exact")
    if tuple(retired_paths) != RETIRED_SCHEMA_PATHS:
        failures.append("s3.current_schema_surface.retired_schema_paths.exact")
    for retired_path in RETIRED_SCHEMA_PATHS:
        if retired_path in current_paths:
            failures.append(
                f"s3.current_schema_surface.retired_schema_current:{retired_path}"
            )
    for relative_path in (*current_paths, *retired_paths):
        if not (repo_root / relative_path).is_file():
            failures.append(f"s3.current_schema_surface.schema_missing:{relative_path}")

    loader_value = value.get("current_loader_or_registry_refs")
    loader_paths: list[str] = []
    registered_schemas: set[str] = set()
    if not isinstance(loader_value, list):
        failures.append("s3.current_schema_surface.current_loader_or_registry_refs.type")
    else:
        for index, record in enumerate(loader_value):
            code = f"s3.current_schema_surface.current_loader_or_registry_refs[{index}]"
            if not isinstance(record, dict):
                failures.append(f"{code}.type")
                continue
            if tuple(record) != SCHEMA_LOADER_REF_KEYS:
                failures.append(f"{code}.shape")
                continue
            source_path = record.get("source_path")
            if not _valid_relative_path(source_path):
                failures.append(f"{code}.source_path")
                continue
            loader_paths.append(source_path)
            schema_paths = _validate_unique_string_list(
                record.get("schema_paths"), f"{code}.schema_paths", failures
            )
            registered_schemas.update(schema_paths)
            for schema_path in schema_paths:
                if schema_path not in CURRENT_SCHEMA_PATHS:
                    failures.append(f"{code}.non_current_schema:{schema_path}")
            if not isinstance(record.get("role"), str) or not record.get("role"):
                failures.append(f"{code}.role")
    if len(loader_paths) != len(set(loader_paths)):
        failures.append("s3.current_schema_surface.loader_duplicate")
    if registered_schemas != set(CURRENT_SCHEMA_PATHS):
        failures.append("s3.current_schema_surface.loader_coverage")

    invariants = _validate_unique_string_list(
        value.get("isolation_invariants"),
        "s3.current_schema_surface.isolation_invariants",
        failures,
        require_paths=False,
    )
    if tuple(invariants) != REQUIRED_SCHEMA_ISOLATION_INVARIANTS:
        failures.append("s3.current_schema_surface.isolation_invariants.exact")

    retired_names = {
        PurePosixPath(path).name for path in RETIRED_SCHEMA_PATHS
    } | set(RETIRED_SCHEMA_PATHS)
    for source_path in loader_paths:
        try:
            source = (repo_root / source_path).read_text(encoding="utf-8")
            tree = ast.parse(source, filename=source_path)
        except (OSError, UnicodeError, SyntaxError) as exc:
            failures.append(
                f"s3.current_schema_surface.loader_read:{source_path}:"
                f"{type(exc).__name__}"
            )
            continue
        literals = {
            node.value
            for node in ast.walk(tree)
            if isinstance(node, ast.Constant) and isinstance(node.value, str)
        }
        for retired_name in sorted(retired_names & literals):
            failures.append(
                f"s3.current_schema_surface.retired_registration:"
                f"{source_path}:{retired_name}"
            )
    return tuple(loader_paths)


def _validate_release_succession(
    completion: dict[str, object] | None,
    seam_index: dict[str, object] | None,
    failures: list[str],
) -> None:
    if completion is not None:
        if completion.get("current_kernel_conformance_profile") != CURRENT_PROFILE_ID:
            failures.append("s3.release.completion.current_profile")
        profiles = completion.get("kernel_conformance_profiles")
        if not isinstance(profiles, dict) or tuple(profiles) != (
            "historical_v0_5",
            "current_v0_6",
        ):
            failures.append("s3.release.completion.profile_shape")
            profiles = {}
        historical = profiles.get("historical_v0_5")
        current = profiles.get("current_v0_6")
        expected_historical = {
            "profile_id": HISTORICAL_PROFILE_ID,
            "profile_version": "v0.5",
            "profile_status": "HISTORICAL_EVIDENCE_ONLY",
            "default_current": False,
            "active_gauntlet_refs": list(HISTORICAL_V05_ACTIVE_REFS),
            "historical_act_id": _HISTORICAL_ACT_ID,
        }
        expected_current = {
            "profile_id": CURRENT_PROFILE_ID,
            "profile_version": "v0.6",
            "profile_status": "CURRENT_ACTIVE",
            "default_current": True,
            "active_gauntlet_refs": list(CURRENT_V06_ACTIVE_REFS),
            "historical_profile_ref": HISTORICAL_PROFILE_ID,
            "historical_act_id_rebound": False,
        }
        if historical != expected_historical:
            failures.append("s3.release.completion.historical_profile_exact")
        if current != expected_current:
            failures.append("s3.release.completion.current_profile_exact")
        expected_claims = {
            claim: list(act_ids)
            for claim, act_ids in CURRENT_REGRESSION_CLAIM_TO_ACTS
        }
        if completion.get("current_regression_claim_mapping") != expected_claims:
            failures.append("s3.release.completion.claim_mapping_exact")

        active_acts = completion.get("active_runtime_acts")
        if not isinstance(active_acts, list):
            failures.append("s3.release.completion.active_runtime_acts.type")
            active_acts = []
        for record in active_acts:
            if isinstance(record, dict) and record.get("act_id") == _HISTORICAL_ACT_ID:
                failures.append("s3.release.completion.historical_act_current")
        evidence = completion.get("evidence_only_references")
        if not isinstance(evidence, list):
            failures.append("s3.release.completion.evidence_only_references.type")
            evidence = []
        historical_records = [
            record
            for record in evidence
            if isinstance(record, dict) and record.get("act_id") == _HISTORICAL_ACT_ID
        ]
        if len(historical_records) != 1:
            failures.append("s3.release.completion.historical_evidence_record")
        else:
            record = historical_records[0]
            required_values = {
                "source_module": _HISTORICAL_RUNNER_MODULE,
                "source_symbol": _HISTORICAL_RUNNER_SYMBOL,
                "historical_profile_ref": HISTORICAL_PROFILE_ID,
                "current_execution_enabled": False,
                "successor_onboarding_allowed": False,
                "status": "HISTORICAL_EVIDENCE_ONLY",
            }
            for key, expected in required_values.items():
                if record.get(key) != expected:
                    failures.append(
                        f"s3.release.completion.historical_evidence:{key}"
                    )

    if seam_index is not None:
        if seam_index.get("current_kernel_conformance_profile") != CURRENT_PROFILE_ID:
            failures.append("s3.release.seam_index.current_profile")
        if seam_index.get("historical_kernel_conformance_profile") != (
            HISTORICAL_PROFILE_ID
        ):
            failures.append("s3.release.seam_index.historical_profile")
        seams = seam_index.get("seams")
        if not isinstance(seams, list):
            failures.append("s3.release.seam_index.seams.type")
            seams = []
        historical_seams = [
            seam
            for seam in seams
            if isinstance(seam, dict)
            and seam.get("source_module") == _HISTORICAL_RUNNER_MODULE
        ]
        if len(historical_seams) != 1:
            failures.append("s3.release.seam_index.historical_seam")
        else:
            seam = historical_seams[0]
            required_values = {
                "current_mode": "HISTORICAL_PROFILE_METADATA_ONLY",
                "gate1_target": HISTORICAL_PROFILE_ID,
                "source_symbol": _HISTORICAL_RUNNER_SYMBOL,
                "status": "HISTORICAL_EVIDENCE_ONLY",
            }
            for key, expected in required_values.items():
                if seam.get(key) != expected:
                    failures.append(f"s3.release.seam_index.historical_seam:{key}")


def _class_fields(tree: ast.Module | None, class_name: str) -> tuple[str, ...]:
    if tree is None:
        return ()
    for statement in tree.body:
        if isinstance(statement, ast.ClassDef) and statement.name == class_name:
            return tuple(
                child.target.id
                for child in statement.body
                if isinstance(child, ast.AnnAssign)
                and isinstance(child.target, ast.Name)
            )
    return ()


def _assignment_is_name(
    tree: ast.Module | None,
    assignment_name: str,
    referenced_name: str,
) -> bool:
    if tree is None:
        return False
    for statement in tree.body:
        value: ast.AST | None = None
        if (
            isinstance(statement, ast.Assign)
            and len(statement.targets) == 1
            and isinstance(statement.targets[0], ast.Name)
            and statement.targets[0].id == assignment_name
        ):
            value = statement.value
        elif (
            isinstance(statement, ast.AnnAssign)
            and isinstance(statement.target, ast.Name)
            and statement.target.id == assignment_name
        ):
            value = statement.value
        if value is None:
            continue
        while isinstance(value, (ast.Tuple, ast.List)) and len(value.elts) == 1:
            value = value.elts[0]
        return isinstance(value, ast.Name) and value.id == referenced_name
    return False


def _assignment_reference_name(
    tree: ast.Module | None,
    assignment_name: str,
) -> str | None:
    if tree is None:
        return None
    for statement in tree.body:
        value: ast.AST | None = None
        if (
            isinstance(statement, ast.Assign)
            and len(statement.targets) == 1
            and isinstance(statement.targets[0], ast.Name)
            and statement.targets[0].id == assignment_name
        ):
            value = statement.value
        elif (
            isinstance(statement, ast.AnnAssign)
            and isinstance(statement.target, ast.Name)
            and statement.target.id == assignment_name
        ):
            value = statement.value
        if isinstance(value, ast.Name):
            return value.id
    return None


def _bound_name_ids(target: ast.AST) -> frozenset[str]:
    if isinstance(target, ast.Name):
        return frozenset({target.id})
    if isinstance(target, (ast.Tuple, ast.List)):
        return frozenset(
            name
            for element in target.elts
            for name in _bound_name_ids(element)
        )
    if isinstance(target, ast.Starred):
        return _bound_name_ids(target.value)
    return frozenset()


def _expression_uses_names_v03(node: ast.AST, names: set[str]) -> bool:
    return any(
        isinstance(child, ast.Name)
        and isinstance(child.ctx, ast.Load)
        and child.id in names
        for child in ast.walk(node)
    )


def _mutable_alias_expression_v03(
    node: ast.AST,
    names: set[str],
    root_names: set[str] | frozenset[str] = frozenset(),
) -> bool:
    if isinstance(node, ast.Name):
        return node.id in names
    if isinstance(node, (ast.BoolOp, ast.IfExp)):
        return _expression_uses_names_v03(node, names)
    if isinstance(node, ast.Subscript):
        if isinstance(node.value, (ast.Tuple, ast.List, ast.Set, ast.Dict)):
            return _expression_uses_names_v03(node.value, names)
        return (
            isinstance(node.value, ast.Name)
            and node.value.id in names
            and node.value.id not in root_names
        )
    if isinstance(node, ast.Attribute):
        return (
            node.attr in CRITICAL_MUTATING_METHODS_V03
            and _expression_uses_names_v03(node.value, names)
        )
    if isinstance(node, (ast.Tuple, ast.List, ast.Set, ast.Dict)):
        return _expression_uses_names_v03(node, names)
    if isinstance(node, ast.Call) and isinstance(node.func, ast.Attribute):
        return (
            node.func.attr in CRITICAL_READ_ONLY_METHODS_V03
            and _expression_uses_names_v03(node.func.value, names)
        )
    if isinstance(node, ast.Attribute):
        return False
    return False


def _scope_nodes_v03(statements: Sequence[ast.stmt]) -> tuple[ast.AST, ...]:
    result: list[ast.AST] = []
    stack: list[ast.AST] = list(reversed(statements))
    while stack:
        node = stack.pop()
        result.append(node)
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
            definition_nodes: list[ast.AST] = [
                *node.decorator_list,
                *node.args.defaults,
                *(
                    item
                    for item in node.args.kw_defaults
                    if item is not None
                ),
            ]
            stack.extend(reversed(definition_nodes))
            continue
        if isinstance(node, ast.ClassDef):
            definition_nodes = [
                *node.decorator_list,
                *node.bases,
                *(keyword.value for keyword in node.keywords),
            ]
            stack.extend(reversed(definition_nodes))
            continue
        if isinstance(node, ast.Lambda):
            definition_nodes = [
                *node.args.defaults,
                *(
                    item
                    for item in node.args.kw_defaults
                    if item is not None
                ),
            ]
            stack.extend(reversed(definition_nodes))
            continue
        stack.extend(reversed(tuple(ast.iter_child_nodes(node))))
    return tuple(result)


def _module_level_bound_names_v05(tree: ast.Module) -> frozenset[str]:
    names: set[str] = set()
    for statement in tree.body:
        targets: tuple[ast.AST, ...] = ()
        if isinstance(statement, ast.Assign):
            targets = tuple(statement.targets)
        elif isinstance(statement, (ast.AnnAssign, ast.AugAssign)):
            targets = (statement.target,)
        elif isinstance(statement, (ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef)):
            names.add(statement.name)
        elif isinstance(statement, (ast.Import, ast.ImportFrom)):
            for alias in statement.names:
                names.add(
                    alias.asname
                    or (
                        alias.name
                        if isinstance(statement, ast.ImportFrom)
                        else alias.name.split(".", 1)[0]
                    )
                )
        for target in targets:
            names.update(_bound_name_ids(target))
    return frozenset(names)


class _DirectScopeBindingsV05(ast.NodeVisitor):
    def __init__(self) -> None:
        self.names: set[str] = set()
        self.global_names: set[str] = set()
        self.nonlocal_names: set[str] = set()

    def _target(self, target: ast.AST) -> None:
        self.names.update(_bound_name_ids(target))

    def visit_Assign(self, node: ast.Assign) -> None:
        for target in node.targets:
            self._target(target)
        self.visit(node.value)

    def visit_AnnAssign(self, node: ast.AnnAssign) -> None:
        self._target(node.target)
        if node.value is not None:
            self.visit(node.value)

    def visit_AugAssign(self, node: ast.AugAssign) -> None:
        self._target(node.target)
        self.visit(node.value)

    def visit_NamedExpr(self, node: ast.NamedExpr) -> None:
        self._target(node.target)
        self.visit(node.value)

    def visit_For(self, node: ast.For) -> None:
        self._target(node.target)
        self.visit(node.iter)
        for statement in (*node.body, *node.orelse):
            self.visit(statement)

    visit_AsyncFor = visit_For

    def visit_With(self, node: ast.With) -> None:
        for item in node.items:
            self.visit(item.context_expr)
            if item.optional_vars is not None:
                self._target(item.optional_vars)
        for statement in node.body:
            self.visit(statement)

    visit_AsyncWith = visit_With

    def visit_ExceptHandler(self, node: ast.ExceptHandler) -> None:
        if node.name is not None:
            self.names.add(node.name)
        for statement in node.body:
            self.visit(statement)

    def visit_Import(self, node: ast.Import) -> None:
        self.names.update(
            alias.asname or alias.name.split(".", 1)[0]
            for alias in node.names
        )

    def visit_ImportFrom(self, node: ast.ImportFrom) -> None:
        self.names.update(alias.asname or alias.name for alias in node.names)

    def visit_FunctionDef(self, node: ast.FunctionDef) -> None:
        self.names.add(node.name)

    visit_AsyncFunctionDef = visit_FunctionDef

    def visit_ClassDef(self, node: ast.ClassDef) -> None:
        self.names.add(node.name)

    def visit_Lambda(self, node: ast.Lambda) -> None:
        return None

    def visit_ListComp(self, node: ast.ListComp) -> None:
        return None

    visit_SetComp = visit_ListComp
    visit_DictComp = visit_ListComp
    visit_GeneratorExp = visit_ListComp

    def visit_Global(self, node: ast.Global) -> None:
        self.global_names.update(node.names)

    def visit_Nonlocal(self, node: ast.Nonlocal) -> None:
        self.nonlocal_names.update(node.names)


def _scope_bindings_v05(
    scope: ast.Module | ast.FunctionDef | ast.AsyncFunctionDef | ast.Lambda | ast.ClassDef,
) -> frozenset[str]:
    visitor = _DirectScopeBindingsV05()
    if isinstance(scope, (ast.FunctionDef, ast.AsyncFunctionDef, ast.Lambda)):
        visitor.names.update(_argument_binding_names_v03(scope.args))
    statements: Sequence[ast.stmt]
    if isinstance(scope, ast.Lambda):
        visitor.visit(scope.body)
        statements = ()
    else:
        statements = scope.body
    for statement in statements:
        visitor.visit(statement)
    visitor.names.difference_update(visitor.global_names | visitor.nonlocal_names)
    return frozenset(visitor.names)


def _lexical_scope_chains_v05(
    tree: ast.Module,
) -> dict[int, tuple[frozenset[str], ...]]:
    chains: dict[int, tuple[frozenset[str], ...]] = {}
    module_bindings = _scope_bindings_v05(tree)

    def walk(node: ast.AST, chain: tuple[frozenset[str], ...]) -> None:
        chains[id(node)] = chain
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
            definition_nodes = (
                *node.decorator_list,
                *node.args.defaults,
                *(value for value in node.args.kw_defaults if value is not None),
                *(
                    argument.annotation
                    for argument in (
                        *node.args.posonlyargs,
                        *node.args.args,
                        *node.args.kwonlyargs,
                    )
                    if argument.annotation is not None
                ),
                *(tuple([node.args.vararg.annotation]) if node.args.vararg is not None and node.args.vararg.annotation is not None else ()),
                *(tuple([node.args.kwarg.annotation]) if node.args.kwarg is not None and node.args.kwarg.annotation is not None else ()),
                *(tuple([node.returns]) if node.returns is not None else ()),
            )
            for child in definition_nodes:
                walk(child, chain)
            body_chain = (*chain, _scope_bindings_v05(node))
            for statement in node.body:
                walk(statement, body_chain)
            return
        if isinstance(node, ast.Lambda):
            for child in (
                *node.args.defaults,
                *(value for value in node.args.kw_defaults if value is not None),
            ):
                walk(child, chain)
            walk(node.body, (*chain, _scope_bindings_v05(node)))
            return
        if isinstance(node, ast.ClassDef):
            for child in (
                *node.decorator_list,
                *node.bases,
                *(keyword.value for keyword in node.keywords),
            ):
                walk(child, chain)
            class_chain = (*chain, _scope_bindings_v05(node))
            for statement in node.body:
                walk(statement, class_chain)
            return
        for child in ast.iter_child_nodes(node):
            walk(child, chain)

    chains[id(tree)] = (module_bindings,)
    for statement in tree.body:
        walk(statement, (module_bindings,))
    return chains


def _lexical_builtin_is_exact_v05(
    chains: dict[int, tuple[frozenset[str], ...]],
    node: ast.AST,
    name: str,
) -> bool:
    return all(name not in bindings for bindings in chains.get(id(node), ()))


def _module_exact_import_bindings_v05(tree: ast.Module) -> dict[str, str]:
    imported_targets: dict[str, list[str]] = {}
    nonimport_bindings: set[str] = set()

    class ModuleExecutionBindings(ast.NodeVisitor):
        def bind(self, target: ast.AST) -> None:
            nonimport_bindings.update(_bound_name_ids(target))

        def visit_Import(self, node: ast.Import) -> None:
            for alias in node.names:
                bound = alias.asname or alias.name.split(".", 1)[0]
                target = alias.name if alias.asname else bound
                imported_targets.setdefault(bound, []).append(target)

        def visit_ImportFrom(self, node: ast.ImportFrom) -> None:
            if node.level != 0:
                for alias in node.names:
                    if alias.name != "*":
                        nonimport_bindings.add(alias.asname or alias.name)
                return
            module = node.module or ""
            for alias in node.names:
                if alias.name == "*":
                    continue
                bound = alias.asname or alias.name
                target = f"{module}.{alias.name}" if module else alias.name
                imported_targets.setdefault(bound, []).append(target)

        def visit_Assign(self, node: ast.Assign) -> None:
            for target in node.targets:
                self.bind(target)
            self.visit(node.value)

        def visit_AnnAssign(self, node: ast.AnnAssign) -> None:
            self.bind(node.target)
            self.visit(node.annotation)
            if node.value is not None:
                self.visit(node.value)

        def visit_AugAssign(self, node: ast.AugAssign) -> None:
            self.bind(node.target)
            self.visit(node.value)

        def visit_NamedExpr(self, node: ast.NamedExpr) -> None:
            self.bind(node.target)
            self.visit(node.value)

        def visit_Delete(self, node: ast.Delete) -> None:
            for target in node.targets:
                self.bind(target)

        def visit_For(self, node: ast.For) -> None:
            self.bind(node.target)
            self.visit(node.iter)
            for statement in (*node.body, *node.orelse):
                self.visit(statement)

        visit_AsyncFor = visit_For

        def visit_With(self, node: ast.With) -> None:
            for item in node.items:
                self.visit(item.context_expr)
                if item.optional_vars is not None:
                    self.bind(item.optional_vars)
            for statement in node.body:
                self.visit(statement)

        visit_AsyncWith = visit_With

        def visit_ExceptHandler(self, node: ast.ExceptHandler) -> None:
            if node.name is not None:
                nonimport_bindings.add(node.name)
            if node.type is not None:
                self.visit(node.type)
            for statement in node.body:
                self.visit(statement)

        def visit_FunctionDef(self, node: ast.FunctionDef) -> None:
            nonimport_bindings.add(node.name)
            for expression in _definition_time_expressions_v05(node):
                self.visit(expression)

        visit_AsyncFunctionDef = visit_FunctionDef

        def visit_ClassDef(self, node: ast.ClassDef) -> None:
            nonimport_bindings.add(node.name)
            for expression in _definition_time_expressions_v05(node):
                self.visit(expression)

        def visit_Lambda(self, node: ast.Lambda) -> None:
            for expression in _definition_time_expressions_v05(node):
                self.visit(expression)

    visitor = ModuleExecutionBindings()
    for statement in tree.body:
        visitor.visit(statement)
    return {
        binding: targets[0]
        for binding, targets in imported_targets.items()
        if binding not in nonimport_bindings
        and targets
        and all(target == targets[0] for target in targets)
    }


def _lexical_module_is_exact_v05(
    tree: ast.Module,
    chains: dict[int, tuple[frozenset[str], ...]],
    node: ast.AST,
    binding: str,
    module_name: str,
) -> bool:
    chain = chains.get(id(node), ())
    if any(binding in names for names in chain[1:]):
        return False
    return _module_exact_import_bindings_v05(tree).get(binding) == module_name


def _identity_preserving_root_expression_v05(
    node: ast.AST,
    roots: set[str] | frozenset[str],
) -> bool:
    if isinstance(node, ast.Name):
        return node.id in roots
    if isinstance(node, ast.Starred):
        return _identity_preserving_root_expression_v05(node.value, roots)
    if isinstance(node, ast.NamedExpr):
        return _identity_preserving_root_expression_v05(node.value, roots)
    if isinstance(node, ast.IfExp):
        return any(
            _identity_preserving_root_expression_v05(value, roots)
            for value in (node.body, node.orelse)
        )
    if isinstance(node, ast.BoolOp):
        return any(
            _identity_preserving_root_expression_v05(value, roots)
            for value in node.values
        )
    if isinstance(node, (ast.Tuple, ast.List, ast.Set)):
        return any(
            _identity_preserving_root_expression_v05(value, roots)
            for value in node.elts
        )
    if isinstance(node, ast.Dict):
        return any(
            value is not None
            and _identity_preserving_root_expression_v05(value, roots)
            for value in (*node.keys, *node.values)
        )
    if isinstance(node, ast.Subscript) and isinstance(
        node.value, (ast.Tuple, ast.List)
    ):
        return _identity_preserving_root_expression_v05(node.value, roots)
    return False


def _identity_aliases_v05(
    tree: ast.Module,
    roots: set[str] | frozenset[str],
) -> frozenset[str]:
    """Close exact-object aliases without treating container members as roots."""

    aliases = set(roots)
    changed = True
    while changed:
        changed = False
        for node in ast.walk(tree):
            targets: tuple[ast.AST, ...] = ()
            value: ast.AST | None = None
            if isinstance(node, ast.Assign):
                targets = tuple(node.targets)
                value = node.value
            elif isinstance(node, ast.AnnAssign) and node.value is not None:
                targets = (node.target,)
                value = node.value
            elif isinstance(node, ast.NamedExpr):
                targets = (node.target,)
                value = node.value
            if value is None or isinstance(value, ast.Call):
                continue
            if not _identity_preserving_root_expression_v05(value, aliases):
                continue
            before = len(aliases)
            for target in targets:
                if isinstance(target, (ast.Name, ast.Tuple, ast.List, ast.Starred)):
                    aliases.update(_bound_name_ids(target))
            changed = changed or len(aliases) != before
    return frozenset(aliases)


def _critical_scope_escape_failures_v05(
    tree: ast.Module,
    *,
    label: str,
    mutable_names: set[str],
) -> tuple[str, ...]:
    alias_names = set(_identity_aliases_v05(tree, mutable_names))
    failures: set[str] = set()
    class_node_ids = {
        id(child)
        for class_node in ast.walk(tree)
        if isinstance(class_node, ast.ClassDef)
        for statement in class_node.body
        for child in ast.walk(statement)
    }
    for node in ast.walk(tree):
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef, ast.Lambda, ast.ClassDef)):
            if any(
                _expression_uses_names_v03(expression, alias_names)
                for expression in _definition_time_expressions_v05(node)
            ):
                failures.add(f"{label}.mutable_scope_escape:definition")
        if isinstance(node, ast.Lambda) and _identity_preserving_root_expression_v05(
            node.body, alias_names
        ):
            failures.add(f"{label}.mutable_scope_escape:lambda_return")
        if isinstance(node, (ast.Return, ast.Yield, ast.YieldFrom)):
            if node.value is not None and _identity_preserving_root_expression_v05(
                node.value, alias_names
            ):
                failures.add(
                    f"{label}.mutable_scope_escape:{type(node).__name__}"
                )
        if isinstance(
            node,
            (ast.GeneratorExp, ast.ListComp, ast.SetComp, ast.DictComp),
        ) and _expression_uses_names_v03(node, alias_names):
            failures.add(f"{label}.mutable_scope_escape:comprehension")
        targets: tuple[ast.AST, ...] = ()
        value: ast.AST | None = None
        if isinstance(node, ast.Assign):
            targets = tuple(node.targets)
            value = node.value
        elif isinstance(node, ast.AnnAssign) and node.value is not None:
            targets = (node.target,)
            value = node.value
        elif isinstance(node, ast.NamedExpr):
            targets = (node.target,)
            value = node.value
        if value is None or not _identity_preserving_root_expression_v05(
            value, alias_names
        ):
            continue
        if id(node) in class_node_ids:
            failures.add(f"{label}.mutable_scope_escape:class_storage")
        if any(
            isinstance(target, (ast.Attribute, ast.Subscript))
            for target in targets
        ):
            failures.add(f"{label}.mutable_scope_escape:storage")
    return tuple(sorted(failures))


def _phase_critical_mutation_failures_v03(
    tree: ast.Module,
    *,
    label: str,
    critical_names: frozenset[str],
    values: dict[str, object],
) -> tuple[str, ...]:
    mutable_names = {
        name
        for name in critical_names
        if type(values.get(name)) in {dict, list, set}
    }
    if not mutable_names:
        return ()
    failures: set[str] = set()
    failures.update(
        _critical_scope_escape_failures_v05(
            tree,
            label=label,
            mutable_names=mutable_names,
        )
    )
    failures.update(
        _dynamic_namespace_failures_v05(
            tree,
            label=f"{label}.critical_namespace",
            protected_names=frozenset(mutable_names),
        )
    )
    failures.update(
        _module_capability_failures_v05(
            tree,
            label=f"{label}.critical_builtin_authority",
            module_name="builtins",
            protected_attributes=CRITICAL_READ_ONLY_CALLS_V03,
        )
    )
    lexical_chains = _lexical_scope_chains_v05(tree)
    function_groups: dict[str, list[ast.FunctionDef | ast.AsyncFunctionDef]] = {}
    for node in ast.walk(tree):
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
            function_groups.setdefault(node.name, []).append(node)
    local_functions = {
        name: rows[0]
        for name, rows in function_groups.items()
        if len(rows) == 1
    }
    active_local_calls: set[tuple[int, tuple[str, ...]]] = set()

    def analyze_scope(
        statements: Sequence[ast.stmt],
        inherited_aliases: set[str],
    ) -> None:
        nodes = _scope_nodes_v03(statements)
        aliases = set(inherited_aliases)
        changed = True
        while changed:
            changed = False
            for node in nodes:
                targets: tuple[ast.AST, ...] = ()
                value: ast.AST | None = None
                if isinstance(node, ast.Assign):
                    targets = tuple(node.targets)
                    value = node.value
                elif isinstance(node, ast.AnnAssign) and node.value is not None:
                    targets = (node.target,)
                    value = node.value
                elif isinstance(node, ast.NamedExpr):
                    targets = (node.target,)
                    value = node.value
                elif isinstance(node, (ast.For, ast.AsyncFor)):
                    targets = (node.target,)
                    value = node.iter
                elif isinstance(node, ast.comprehension):
                    targets = (node.target,)
                    value = node.iter
                elif isinstance(node, (ast.With, ast.AsyncWith)):
                    for item in node.items:
                        if (
                            item.optional_vars is not None
                            and _mutable_alias_expression_v03(
                                item.context_expr, aliases, mutable_names
                            )
                        ):
                            before = len(aliases)
                            aliases.update(_bound_name_ids(item.optional_vars))
                            changed = changed or len(aliases) != before
                    continue
                if value is None or not _mutable_alias_expression_v03(
                    value, aliases, mutable_names
                ):
                    continue
                for target in targets:
                    before = len(aliases)
                    aliases.update(_bound_name_ids(target))
                    changed = changed or len(aliases) != before

        for node in nodes:
            if isinstance(node, (ast.Assign, ast.AnnAssign, ast.NamedExpr)):
                targets = (
                    tuple(node.targets)
                    if isinstance(node, ast.Assign)
                    else (node.target,)
                )
                value = node.value
                if value is not None and _mutable_alias_expression_v03(
                    value, aliases, mutable_names
                ):
                    if any(
                        isinstance(target, (ast.Attribute, ast.Subscript))
                        for target in targets
                    ):
                        failures.add(f"{label}.mutable_escape:storage")
                for target in targets:
                    if (
                        isinstance(target, (ast.Attribute, ast.Subscript))
                        and _expression_uses_names_v03(target, aliases)
                    ):
                        failures.add(
                            f"{label}.mutable_write:{type(node).__name__}"
                        )
            elif isinstance(node, ast.AugAssign):
                if (
                    _expression_uses_names_v03(node.target, aliases)
                    or bool(_bound_name_ids(node.target) & aliases)
                    or _target_root_name_v03(node.target) in aliases
                ):
                    failures.add(f"{label}.mutable_write:AugAssign")
            elif isinstance(node, ast.Delete):
                if any(
                    _expression_uses_names_v03(target, aliases)
                    for target in node.targets
                ):
                    failures.add(f"{label}.mutable_write:Delete")
            elif isinstance(node, (ast.Return, ast.Yield, ast.YieldFrom)):
                value = node.value
                if value is not None and _mutable_alias_expression_v03(
                    value, aliases, mutable_names
                ):
                    failures.add(
                        f"{label}.mutable_escape:{type(node).__name__}"
                    )
            if not isinstance(node, ast.Call):
                continue
            called = _dotted_ast_name(node.func) or ""
            call_leaf = called.split(".")[-1]
            tainted_arguments = any(
                _expression_uses_names_v03(argument, aliases)
                for argument in node.args
            ) or any(
                _expression_uses_names_v03(keyword.value, aliases)
                for keyword in node.keywords
            )
            tainted_receiver = (
                isinstance(node.func, ast.Attribute)
                and _expression_uses_names_v03(node.func.value, aliases)
            )
            tainted_callable = _expression_uses_names_v03(
                node.func, aliases
            )
            if call_leaf in CRITICAL_MUTATING_METHODS_V03 and (
                tainted_receiver or tainted_arguments or tainted_callable
            ):
                failures.add(f"{label}.mutable_call:{call_leaf}")
                continue
            local_function = local_functions.get(call_leaf)
            if tainted_arguments and local_function is not None:
                tainted_parameters = _tainted_call_parameters_v03(
                    node, local_function, aliases
                )
                token = (id(local_function), tuple(sorted(tainted_parameters)))
                if token not in active_local_calls:
                    active_local_calls.add(token)
                    analyze_scope(local_function.body, tainted_parameters)
                    active_local_calls.remove(token)
                continue
            if tainted_callable and not tainted_receiver:
                failures.add(f"{label}.mutable_escape:{called or call_leaf}")
                continue
            if tainted_receiver:
                if call_leaf not in CRITICAL_READ_ONLY_METHODS_V03:
                    failures.add(
                        f"{label}.mutable_escape:{called or call_leaf}"
                    )
                continue
            if (
                tainted_arguments
                and not (
                    isinstance(node.func, ast.Name)
                    and node.func.id in CRITICAL_READ_ONLY_CALLS_V03
                    and _lexical_builtin_is_exact_v05(
                        lexical_chains, node, node.func.id
                    )
                )
            ):
                failures.add(f"{label}.mutable_escape:{called or call_leaf}")

        for node in nodes:
            if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
                parameters = _argument_binding_names_v03(node.args)
                defaults = (
                    *node.args.defaults,
                    *(item for item in node.args.kw_defaults if item is not None),
                )
                if any(
                    _expression_uses_names_v03(default, aliases)
                    for default in defaults
                ):
                    failures.add(f"{label}.mutable_escape:function_default")
                analyze_scope(node.body, aliases - set(parameters))
            elif isinstance(node, ast.ClassDef):
                analyze_scope(node.body, aliases)
            elif isinstance(node, ast.Lambda):
                parameters = _argument_binding_names_v03(node.args)
                analyze_scope(
                    (ast.Expr(value=node.body),),
                    aliases - set(parameters),
                )

    analyze_scope(tree.body, set(mutable_names))
    return tuple(sorted(failures))


def _phase_critical_assignments_v02(
    source_path: Path,
    label: str,
    critical_names: frozenset[str],
    failures: list[str],
) -> tuple[
    dict[str, object],
    dict[str, ast.AST],
    ast.Module | None,
    str,
]:
    """Extract one exact, bounded module binding for each critical name."""

    try:
        source = source_path.read_text(encoding="utf-8")
    except (OSError, UnicodeError) as exc:
        failures.append(f"{label}.read:{type(exc).__name__}")
        return {}, {}, None, ""
    try:
        tree = ast.parse(source, filename=str(source_path))
    except SyntaxError:
        failures.append(f"{label}.syntax")
        return {}, {}, None, source

    direct_nodes: dict[str, list[ast.AST]] = {}
    permitted_statement_ids: set[int] = set()
    values: dict[str, object] = {}
    for statement in tree.body:
        name: str | None = None
        value_node: ast.AST | None = None
        if (
            isinstance(statement, ast.Assign)
            and len(statement.targets) == 1
            and isinstance(statement.targets[0], ast.Name)
        ):
            name = statement.targets[0].id
            value_node = statement.value
        elif (
            isinstance(statement, ast.AnnAssign)
            and isinstance(statement.target, ast.Name)
            and statement.value is not None
        ):
            name = statement.target.id
            value_node = statement.value
        if name is not None and value_node is not None:
            permitted_statement_ids.add(id(statement))
            if name in critical_names:
                direct_nodes.setdefault(name, []).append(value_node)
            try:
                values[name] = _static_value(value_node, values)
            except StaticValueUnavailable:
                values.pop(name, None)

    module_bound_names = _module_level_bound_names_v05(tree)
    for name, nodes in direct_nodes.items():
        for value_node in nodes:
            shadowed_calls = {
                call.func.id
                for call in ast.walk(value_node)
                if isinstance(call, ast.Call)
                and isinstance(call.func, ast.Name)
                and call.func.id in CRITICAL_READ_ONLY_CALLS_V03
                and call.func.id in module_bound_names
            }
            if shadowed_calls:
                failures.append(
                    f"{label}.critical_builtin_shadow:{name}:"
                    f"{','.join(sorted(shadowed_calls))}"
                )

    invalid_bindings: set[tuple[str, str]] = set()
    for node in ast.walk(tree):
        targets: tuple[ast.AST, ...] = ()
        kind = type(node).__name__
        if isinstance(node, ast.Assign):
            targets = tuple(node.targets)
        elif isinstance(node, ast.AnnAssign):
            targets = (node.target,)
        elif isinstance(node, ast.AugAssign):
            targets = (node.target,)
        elif isinstance(node, ast.NamedExpr):
            targets = (node.target,)
        elif isinstance(node, (ast.For, ast.AsyncFor)):
            targets = (node.target,)
        elif isinstance(node, (ast.With, ast.AsyncWith)):
            targets = tuple(
                item.optional_vars
                for item in node.items
                if item.optional_vars is not None
            )
        elif isinstance(node, ast.comprehension):
            targets = (node.target,)
        elif isinstance(node, ast.Delete):
            targets = tuple(node.targets)
        for target in targets:
            for name in _bound_name_ids(target) & critical_names:
                if id(node) not in permitted_statement_ids:
                    invalid_bindings.add((name, kind))
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef)):
            if node.name in critical_names:
                invalid_bindings.add((node.name, kind))
        elif isinstance(node, (ast.Global, ast.Nonlocal)):
            for name in set(node.names) & critical_names:
                invalid_bindings.add((name, kind))
        elif isinstance(node, (ast.Import, ast.ImportFrom)):
            for alias in node.names:
                bound = alias.asname or alias.name.split(".", 1)[0]
                if bound in critical_names:
                    invalid_bindings.add((bound, kind))
        elif isinstance(node, ast.Call):
            call_name = node.func.id if isinstance(node.func, ast.Name) else ""
            if call_name in {"exec", "eval", "globals", "locals"}:
                failures.append(f"{label}.dynamic_namespace:{call_name}")
            if call_name == "setattr" and len(node.args) >= 2:
                attribute = node.args[1]
                if (
                    isinstance(attribute, ast.Constant)
                    and attribute.value in critical_names
                ):
                    invalid_bindings.add((str(attribute.value), "setattr"))
        if isinstance(node, (ast.Assign, ast.AnnAssign, ast.AugAssign)):
            assignment_targets = (
                tuple(node.targets)
                if isinstance(node, (ast.Assign, ast.Delete))
                else (node.target,)
            )
            for target in assignment_targets:
                if not isinstance(target, ast.Subscript):
                    continue
                names = {
                    child.value
                    for child in ast.walk(target.slice)
                    if isinstance(child, ast.Constant)
                    and isinstance(child.value, str)
                }
                for name in names & critical_names:
                    invalid_bindings.add((name, "dynamic_subscript"))

    failures.extend(
        _phase_critical_mutation_failures_v03(
            tree,
            label=label,
            critical_names=critical_names,
            values=values,
        )
    )

    result: dict[str, object] = {}
    result_nodes: dict[str, ast.AST] = {}
    for name in sorted(critical_names):
        nodes = direct_nodes.get(name, [])
        matching_invalid = sorted(
            kind for invalid_name, kind in invalid_bindings if invalid_name == name
        )
        if len(nodes) > 1:
            failures.append(f"{label}.binding_duplicate:{name}")
        if matching_invalid:
            failures.append(
                f"{label}.binding_dynamic:{name}:{','.join(matching_invalid)}"
            )
        if len(nodes) != 1 or matching_invalid:
            continue
        try:
            value = _static_value(nodes[0], values)
        except StaticValueUnavailable:
            failures.append(f"{label}.binding_unresolved:{name}")
            continue
        result[name] = value
        result_nodes[name] = nodes[0]
    return result, result_nodes, tree, source


def _repr_sha256(value: object) -> str:
    return hashlib.sha256(repr(value).encode("ascii")).hexdigest()


def _critical_shape_matches(
    node: ast.AST,
    expected: object,
    expected_reference: str | None,
) -> bool:
    if expected_reference is not None:
        return isinstance(node, ast.Name) and node.id == expected_reference
    if type(expected) is str:
        return isinstance(node, ast.Constant) and type(node.value) is str
    if type(expected) is tuple:
        return isinstance(node, (ast.Tuple, ast.Name)) or (
            isinstance(node, ast.Call)
            and isinstance(node.func, ast.Name)
            and node.func.id == "tuple"
            and len(node.args) == 1
            and not node.keywords
        )
    if type(expected) is dict:
        return isinstance(node, ast.Dict)
    return False


def _validate_critical_value_set_v02(
    *,
    label: str,
    values: dict[str, object],
    nodes: dict[str, ast.AST],
    all_names: frozenset[str],
    expected_values: dict[str, object],
    expected_references: dict[str, str],
    expected_repr_digests: dict[str, tuple[type[object], str]],
    failures: list[str],
) -> None:
    required = set(expected_values) | set(expected_repr_digests)
    for name in sorted(required):
        if name not in values or name not in nodes:
            failures.append(f"{label}.binding_missing:{name}")
            continue
        value = values[name]
        expected = expected_values.get(name)
        if name in expected_repr_digests:
            expected_type, expected_digest = expected_repr_digests[name]
            if type(value) is not expected_type or _repr_sha256(value) != expected_digest:
                failures.append(f"{label}.binding_value:{name}")
            expected = {} if expected_type is dict else ()
        elif type(value) is not type(expected) or value != expected:
            failures.append(f"{label}.binding_value:{name}")
        if not _critical_shape_matches(
            nodes[name], expected, expected_references.get(name)
        ):
            failures.append(f"{label}.binding_shape:{name}")
    for name in sorted(all_names - required):
        if name in nodes or name in values:
            failures.append(f"{label}.binding_forbidden:{name}")


def _validate_phase_critical_bindings_v02(
    phase: str | None,
    core_values: dict[str, object],
    core_nodes: dict[str, ast.AST],
    runner_values: dict[str, object],
    runner_nodes: dict[str, ast.AST],
    living_values: dict[str, object],
    living_nodes: dict[str, ast.AST],
    failures: list[str],
) -> None:
    if phase not in {"PRE_E6_RECONCILED", "POST_E6_SUCCESSOR"}:
        return
    post = phase == "POST_E6_SUCCESSOR"
    current_refs = POST_E6_ACTIVE_REFS if post else CURRENT_V06_ACTIVE_REFS
    category_checks = POST_E6_CATEGORY_CHECK_IDS if post else PRE_E6_CATEGORY_CHECK_IDS
    probes = POST_E6_NEGATIVE_PROBE_IDS if post else PRE_E6_NEGATIVE_PROBE_IDS
    profile_name = (
        "KERNEL_CONFORMANCE_PROFILE_V07_CURRENT"
        if post
        else "KERNEL_CONFORMANCE_PROFILE_V06_CURRENT"
    )
    profile_value = POST_E6_PROFILE_ID if post else CURRENT_PROFILE_ID

    core_expected = {
        "CONFORMANCE_VERSION": "v0.7" if post else "v0.6",
        "KERNEL_CONFORMANCE_PROFILE_V05_HISTORICAL": HISTORICAL_PROFILE_ID,
        profile_name: profile_value,
        "DEFAULT_KERNEL_CONFORMANCE_PROFILE": profile_value,
        "CATEGORY_IDS": tuple(item[0] for item in category_checks),
        "DOMAIN_IDS": PRESERVED_DOMAIN_IDS,
        "NEGATIVE_PROBE_IDS": probes,
        "_V05_HISTORICAL_ACTIVE_GAUNTLET_REFS": HISTORICAL_V05_ACTIVE_REFS,
        "_ACTIVE_GAUNTLET_REFS": current_refs,
        "_EXPECTED_CATEGORY_CHECK_IDS": category_checks,
        "_EXPECTED_DOMAIN_GEOMETRY": PRESERVED_DOMAIN_GEOMETRY,
    }
    if post:
        core_expected.update(
            {
                "KERNEL_CONFORMANCE_PROFILE_V06_HISTORICAL": (
                    POST_E6_IMMEDIATE_HISTORICAL_PROFILE_ID
                ),
                "_V06_HISTORICAL_ACTIVE_GAUNTLET_REFS": CURRENT_V06_ACTIVE_REFS,
                "_V07_CURRENT_ACTIVE_GAUNTLET_REFS": POST_E6_ACTIVE_REFS,
            }
        )
    else:
        core_expected["_V06_CURRENT_ACTIVE_GAUNTLET_REFS"] = CURRENT_V06_ACTIVE_REFS
    _validate_critical_value_set_v02(
        label="e6.phase.critical.core",
        values=core_values,
        nodes=core_nodes,
        all_names=CORE_PHASE_CRITICAL_NAMES,
        expected_values=core_expected,
        expected_references={"DEFAULT_KERNEL_CONFORMANCE_PROFILE": profile_name},
        expected_repr_digests={},
        failures=failures,
    )

    runner_expected = {
        "RUNNER_VERSION": "v0.7" if post else "v0.6",
        "KERNEL_CONFORMANCE_PROFILE_V05_HISTORICAL": HISTORICAL_PROFILE_ID,
        profile_name: profile_value,
        "DEFAULT_KERNEL_CONFORMANCE_PROFILE": profile_value,
        "_V05_HISTORICAL_BASE_ACT_IDS": HISTORICAL_V05_ACTIVE_REFS,
        "_BASE_ACT_IDS": current_refs,
    }
    if post:
        runner_expected["KERNEL_CONFORMANCE_PROFILE_V06_HISTORICAL"] = (
            POST_E6_IMMEDIATE_HISTORICAL_PROFILE_ID
        )
        runner_expected["_V06_HISTORICAL_BASE_ACT_IDS"] = CURRENT_V06_ACTIVE_REFS
    runner_digest = (
        POST_E6_CONFORMANCE_ACT_SOURCES_REPR_SHA256
        if post
        else PRE_E6_CONFORMANCE_ACT_SOURCES_REPR_SHA256
    )
    _validate_critical_value_set_v02(
        label="e6.phase.critical.runner",
        values=runner_values,
        nodes=runner_nodes,
        all_names=RUNNER_PHASE_CRITICAL_NAMES,
        expected_values=runner_expected,
        expected_references={"DEFAULT_KERNEL_CONFORMANCE_PROFILE": profile_name},
        expected_repr_digests={"_ACT_SOURCES": (dict, runner_digest)},
        failures=failures,
    )

    living_expected = {
        "RUNNER_VERSION": "v1.6" if post else "v1.5",
        "KERNEL_CONFORMANCE_PROFILE_V05_HISTORICAL": HISTORICAL_PROFILE_ID,
        profile_name: profile_value,
        "DEFAULT_KERNEL_CONFORMANCE_PROFILE": profile_value,
        "HISTORICAL_KERNEL_CONFORMANCE_ACTIVE_REFS_V05": (
            HISTORICAL_V05_ACTIVE_REFS
        ),
        "_ACTIVE_ACT_IDS": POST_E6_LIVING_ACT_IDS if post else PRE_E6_LIVING_ACT_IDS,
        "_EXECUTED_RUNTIME_ACT_IDS": (
            POST_E6_LIVING_EXECUTED_RUNTIME_ACT_IDS
            if post
            else PRE_E6_LIVING_EXECUTED_RUNTIME_ACT_IDS
        ),
        "_EXECUTED_CONFORMANCE_ACT_IDS": (
            PRE_E6_LIVING_EXECUTED_CONFORMANCE_ACT_IDS
        ),
        "_EVIDENCE_ONLY_ACT_IDS": LIVING_EVIDENCE_ONLY_ACT_IDS,
        "_HISTORICAL_EVIDENCE_ACT_IDS": LIVING_HISTORICAL_EVIDENCE_ACT_IDS,
        "_HISTORICAL_SEAMS": {
            "all_layers_invariant_super_smoke_collector": (
                _HISTORICAL_RUNNER_MODULE,
                _HISTORICAL_RUNNER_SYMBOL,
            )
        },
    }
    if post:
        living_expected.update(
            {
                "KERNEL_CONFORMANCE_PROFILE_V06_HISTORICAL": (
                    POST_E6_IMMEDIATE_HISTORICAL_PROFILE_ID
                ),
                "HISTORICAL_KERNEL_CONFORMANCE_ACTIVE_REFS_V06": (
                    CURRENT_V06_ACTIVE_REFS
                ),
                "CURRENT_KERNEL_CONFORMANCE_ACTIVE_REFS_V07": POST_E6_ACTIVE_REFS,
            }
        )
    else:
        living_expected["CURRENT_KERNEL_CONFORMANCE_ACTIVE_REFS_V06"] = (
            CURRENT_V06_ACTIVE_REFS
        )
    living_digest = (
        POST_E6_LIVING_ACTIVE_SOURCES_REPR_SHA256
        if post
        else PRE_E6_LIVING_ACTIVE_SOURCES_REPR_SHA256
    )
    _validate_critical_value_set_v02(
        label="e6.phase.critical.living",
        values=living_values,
        nodes=living_nodes,
        all_names=LIVING_PHASE_CRITICAL_NAMES,
        expected_values=living_expected,
        expected_references={"DEFAULT_KERNEL_CONFORMANCE_PROFILE": profile_name},
        expected_repr_digests={
            "_ACTIVE_ACT_SOURCES": (dict, living_digest),
            "_CURRENT_SEAMS": (dict, LIVING_CURRENT_SEAMS_REPR_SHA256),
        },
        failures=failures,
    )


def _expected_pre_e6_phase_state_v01() -> dict[str, object]:
    return {
        "living_version": "v1.5",
        "living_act_ids": PRE_E6_LIVING_ACT_IDS,
        "living_profile_v05": HISTORICAL_PROFILE_ID,
        "living_profile_v06_current": CURRENT_PROFILE_ID,
        "living_profile_v06_historical": None,
        "living_profile_v07_current": None,
        "living_default_profile_ref": "KERNEL_CONFORMANCE_PROFILE_V06_CURRENT",
        "living_v05_refs": HISTORICAL_V05_ACTIVE_REFS,
        "living_v06_historical_refs": None,
        "living_current_refs": CURRENT_V06_ACTIVE_REFS,
        "core_version": "v0.6",
        "core_profile_v05": HISTORICAL_PROFILE_ID,
        "core_profile_v06_current": CURRENT_PROFILE_ID,
        "core_profile_v06_historical": None,
        "core_profile_v07_current": None,
        "core_default_profile_ref": "KERNEL_CONFORMANCE_PROFILE_V06_CURRENT",
        "core_v05_refs": HISTORICAL_V05_ACTIVE_REFS,
        "core_v06_historical_refs": None,
        "core_current_refs": CURRENT_V06_ACTIVE_REFS,
        "runner_version": "v0.6",
        "runner_profile_v05": HISTORICAL_PROFILE_ID,
        "runner_profile_v06_current": CURRENT_PROFILE_ID,
        "runner_profile_v06_historical": None,
        "runner_profile_v07_current": None,
        "runner_default_profile_ref": "KERNEL_CONFORMANCE_PROFILE_V06_CURRENT",
        "runner_v05_refs": HISTORICAL_V05_ACTIVE_REFS,
        "runner_v06_historical_refs": None,
        "runner_current_refs": CURRENT_V06_ACTIVE_REFS,
        "category_ids": tuple(item[0] for item in PRE_E6_CATEGORY_CHECK_IDS),
        "category_check_ids": PRE_E6_CATEGORY_CHECK_IDS,
        "negative_probe_ids": PRE_E6_NEGATIVE_PROBE_IDS,
        "domain_ids": PRESERVED_DOMAIN_IDS,
        "domain_geometry": PRESERVED_DOMAIN_GEOMETRY,
        "historical_all_layers_current": False,
        "historical_v05_evidence_preserved": True,
        "focused_test_phase": "PRE_E6_RECONCILED",
    }


def _expected_post_e6_phase_state_v01() -> dict[str, object]:
    return {
        "living_version": "v1.6",
        "living_act_ids": POST_E6_LIVING_ACT_IDS,
        "living_profile_v05": HISTORICAL_PROFILE_ID,
        "living_profile_v06_current": None,
        "living_profile_v06_historical": (
            POST_E6_IMMEDIATE_HISTORICAL_PROFILE_ID
        ),
        "living_profile_v07_current": POST_E6_PROFILE_ID,
        "living_default_profile_ref": "KERNEL_CONFORMANCE_PROFILE_V07_CURRENT",
        "living_v05_refs": HISTORICAL_V05_ACTIVE_REFS,
        "living_v06_historical_refs": CURRENT_V06_ACTIVE_REFS,
        "living_current_refs": POST_E6_ACTIVE_REFS,
        "core_version": "v0.7",
        "core_profile_v05": HISTORICAL_PROFILE_ID,
        "core_profile_v06_current": None,
        "core_profile_v06_historical": POST_E6_IMMEDIATE_HISTORICAL_PROFILE_ID,
        "core_profile_v07_current": POST_E6_PROFILE_ID,
        "core_default_profile_ref": "KERNEL_CONFORMANCE_PROFILE_V07_CURRENT",
        "core_v05_refs": HISTORICAL_V05_ACTIVE_REFS,
        "core_v06_historical_refs": CURRENT_V06_ACTIVE_REFS,
        "core_current_refs": POST_E6_ACTIVE_REFS,
        "runner_version": "v0.7",
        "runner_profile_v05": HISTORICAL_PROFILE_ID,
        "runner_profile_v06_current": None,
        "runner_profile_v06_historical": (
            POST_E6_IMMEDIATE_HISTORICAL_PROFILE_ID
        ),
        "runner_profile_v07_current": POST_E6_PROFILE_ID,
        "runner_default_profile_ref": "KERNEL_CONFORMANCE_PROFILE_V07_CURRENT",
        "runner_v05_refs": HISTORICAL_V05_ACTIVE_REFS,
        "runner_v06_historical_refs": CURRENT_V06_ACTIVE_REFS,
        "runner_current_refs": POST_E6_ACTIVE_REFS,
        "category_ids": tuple(item[0] for item in POST_E6_CATEGORY_CHECK_IDS),
        "category_check_ids": POST_E6_CATEGORY_CHECK_IDS,
        "negative_probe_ids": POST_E6_NEGATIVE_PROBE_IDS,
        "domain_ids": PRESERVED_DOMAIN_IDS,
        "domain_geometry": PRESERVED_DOMAIN_GEOMETRY,
        "historical_all_layers_current": False,
        "historical_v05_evidence_preserved": True,
        "focused_test_phase": "POST_E6_SUCCESSOR",
    }


def _classify_e6_phase_v01(
    state: dict[str, object],
) -> tuple[str | None, tuple[str, ...]]:
    versions = (
        state.get("living_version"),
        state.get("core_version"),
        state.get("runner_version"),
    )
    if versions == ("v1.5", "v0.6", "v0.6"):
        phase = "PRE_E6_RECONCILED"
        expected = _expected_pre_e6_phase_state_v01()
        code = "e6.phase.pre"
    elif versions == ("v1.6", "v0.7", "v0.7"):
        phase = "POST_E6_SUCCESSOR"
        expected = _expected_post_e6_phase_state_v01()
        code = "e6.phase.post"
    else:
        failures = ["e6.phase.version_hybrid"]
        expected_versions = {
            "living_version": {"v1.5", "v1.6"},
            "core_version": {"v0.6", "v0.7"},
            "runner_version": {"v0.6", "v0.7"},
        }
        for key, allowed in expected_versions.items():
            if state.get(key) not in allowed:
                failures.append(f"e6.phase.{key}")
        return None, tuple(sorted(failures))

    failures = [
        f"{code}.{key}"
        for key, expected_value in expected.items()
        if state.get(key) != expected_value
    ]
    if state.get("historical_all_layers_current") is not False:
        failures.append("e6.phase.historical_all_layers_rebound")
    if state.get("historical_v05_evidence_preserved") is not True:
        failures.append("e6.phase.historical_v05_evidence_erased")
    return phase if not failures else None, tuple(sorted(set(failures)))


def _dotted_ast_name(node: ast.AST) -> str | None:
    if isinstance(node, ast.Name):
        return node.id
    if isinstance(node, ast.Attribute):
        prefix = _dotted_ast_name(node.value)
        return f"{prefix}.{node.attr}" if prefix else node.attr
    return None


def _module_import_targets_v02(tree: ast.Module) -> dict[str, str]:
    targets: dict[str, str] = {}
    for statement in tree.body:
        if isinstance(statement, ast.Import):
            for alias in statement.names:
                bound = alias.asname or alias.name.split(".", 1)[0]
                targets[bound] = alias.name if alias.asname else bound
        elif isinstance(statement, ast.ImportFrom) and statement.level == 0:
            module = statement.module or ""
            for alias in statement.names:
                if alias.name == "*":
                    continue
                bound = alias.asname or alias.name
                targets[bound] = f"{module}.{alias.name}" if module else alias.name
    return targets


def _module_import_binding_counts_v03(tree: ast.Module) -> dict[str, int]:
    counts: dict[str, int] = {}
    for statement in tree.body:
        if isinstance(statement, ast.Import):
            aliases = statement.names
        elif isinstance(statement, ast.ImportFrom) and statement.level == 0:
            aliases = statement.names
        else:
            continue
        for alias in aliases:
            if alias.name == "*":
                continue
            bound = alias.asname or alias.name.split(".", 1)[0]
            counts[bound] = counts.get(bound, 0) + 1
    return counts


def _resolved_call_target_v02(
    node: ast.AST,
    import_targets: dict[str, str],
) -> str | None:
    dotted = _dotted_ast_name(node)
    if not dotted:
        return None
    first, *rest = dotted.split(".")
    if first not in import_targets:
        return dotted
    return ".".join((import_targets[first], *rest))


def _argument_binding_names_v03(arguments: ast.arguments) -> frozenset[str]:
    result = {
        argument.arg
        for argument in (
            *arguments.posonlyargs,
            *arguments.args,
            *arguments.kwonlyargs,
        )
    }
    if arguments.vararg is not None:
        result.add(arguments.vararg.arg)
    if arguments.kwarg is not None:
        result.add(arguments.kwarg.arg)
    return frozenset(result)


def _tainted_call_parameters_v03(
    call: ast.Call,
    function: ast.FunctionDef | ast.AsyncFunctionDef,
    aliases: set[str],
) -> set[str]:
    positional = (*function.args.posonlyargs, *function.args.args)
    tainted: set[str] = set()
    for index, argument in enumerate(call.args):
        if not _expression_uses_names_v03(argument, aliases):
            continue
        if isinstance(argument, ast.Starred) or index >= len(positional):
            tainted.update(_argument_binding_names_v03(function.args))
        else:
            tainted.add(positional[index].arg)
    keyword_names = {argument.arg for argument in function.args.kwonlyargs}
    keyword_names.update(argument.arg for argument in positional)
    for keyword in call.keywords:
        if not _expression_uses_names_v03(keyword.value, aliases):
            continue
        if keyword.arg is None:
            tainted.update(_argument_binding_names_v03(function.args))
        elif keyword.arg in keyword_names:
            tainted.add(keyword.arg)
    return tainted


def _target_root_name_v03(node: ast.AST) -> str | None:
    current = node
    while isinstance(current, (ast.Attribute, ast.Subscript)):
        current = current.value
    return current.id if isinstance(current, ast.Name) else None


_PROVENANCE_NONE_V04 = 0
_PROVENANCE_DERIVED_V04 = 1
_PROVENANCE_CONTAINER_V04 = 2
_PROVENANCE_IDENTITY_V04 = 3


def _expression_provenance_v04(
    node: ast.AST,
    bindings: dict[str, int],
) -> int:
    if isinstance(node, ast.Name):
        return bindings.get(node.id, _PROVENANCE_NONE_V04)
    if isinstance(node, ast.Starred):
        return _expression_provenance_v04(node.value, bindings)
    if isinstance(node, ast.NamedExpr):
        return _expression_provenance_v04(node.value, bindings)
    if isinstance(node, ast.IfExp):
        return max(
            _expression_provenance_v04(node.body, bindings),
            _expression_provenance_v04(node.orelse, bindings),
        )
    if isinstance(node, ast.BoolOp):
        return max(
            (
                _expression_provenance_v04(value, bindings)
                for value in node.values
            ),
            default=_PROVENANCE_NONE_V04,
        )
    if isinstance(node, (ast.Tuple, ast.List, ast.Set)):
        if any(
            _expression_provenance_v04(element, bindings)
            != _PROVENANCE_NONE_V04
            for element in node.elts
        ):
            return _PROVENANCE_CONTAINER_V04
        return _PROVENANCE_NONE_V04
    if isinstance(node, ast.Dict):
        if any(
            child is not None
            and _expression_provenance_v04(child, bindings)
            != _PROVENANCE_NONE_V04
            for child in (*node.keys, *node.values)
        ):
            return _PROVENANCE_CONTAINER_V04
        return _PROVENANCE_NONE_V04
    if isinstance(node, ast.Subscript):
        parent = _expression_provenance_v04(node.value, bindings)
        if parent == _PROVENANCE_CONTAINER_V04:
            return _PROVENANCE_IDENTITY_V04
        if parent != _PROVENANCE_NONE_V04:
            return _PROVENANCE_DERIVED_V04
        return _PROVENANCE_NONE_V04
    if isinstance(node, ast.Attribute):
        parent = _expression_provenance_v04(node.value, bindings)
        return (
            _PROVENANCE_DERIVED_V04
            if parent != _PROVENANCE_NONE_V04
            else _PROVENANCE_NONE_V04
        )
    child_kinds = tuple(
        _expression_provenance_v04(child, bindings)
        for child in ast.iter_child_nodes(node)
    )
    if any(kind != _PROVENANCE_NONE_V04 for kind in child_kinds):
        return _PROVENANCE_DERIVED_V04
    return _PROVENANCE_NONE_V04


def _propagate_provenance_target_v04(
    target: ast.AST,
    kind: int,
    bindings: dict[str, int],
) -> bool:
    if kind == _PROVENANCE_NONE_V04:
        return False
    changed = False
    if isinstance(target, ast.Name):
        if bindings.get(target.id, _PROVENANCE_NONE_V04) < kind:
            bindings[target.id] = kind
            changed = True
    elif isinstance(target, (ast.Tuple, ast.List)):
        child_kind = (
            _PROVENANCE_IDENTITY_V04
            if kind in {_PROVENANCE_IDENTITY_V04, _PROVENANCE_CONTAINER_V04}
            else kind
        )
        for element in target.elts:
            changed = (
                _propagate_provenance_target_v04(
                    element, child_kind, bindings
                )
                or changed
            )
    elif isinstance(target, ast.Starred):
        changed = _propagate_provenance_target_v04(
            target.value, kind, bindings
        )
    return changed


def _provenance_bindings_v04(
    root: ast.AST,
    initial: dict[str, int],
) -> dict[str, int]:
    bindings = dict(initial)
    nodes = tuple(ast.walk(root))
    changed = True
    while changed:
        changed = False
        for node in nodes:
            targets: tuple[ast.AST, ...] = ()
            value: ast.AST | None = None
            if isinstance(node, ast.Assign):
                targets = tuple(node.targets)
                value = node.value
            elif isinstance(node, ast.AnnAssign) and node.value is not None:
                targets = (node.target,)
                value = node.value
            elif isinstance(node, ast.NamedExpr):
                targets = (node.target,)
                value = node.value
            elif isinstance(node, (ast.For, ast.AsyncFor, ast.comprehension)):
                targets = (node.target,)
                value = node.iter
            elif isinstance(node, (ast.With, ast.AsyncWith)):
                for item in node.items:
                    if item.optional_vars is None:
                        continue
                    kind = _expression_provenance_v04(
                        item.context_expr, bindings
                    )
                    changed = (
                        _propagate_provenance_target_v04(
                            item.optional_vars, kind, bindings
                        )
                        or changed
                    )
                continue
            if value is None:
                continue
            kind = _expression_provenance_v04(value, bindings)
            for target in targets:
                changed = (
                    _propagate_provenance_target_v04(
                        target, kind, bindings
                    )
                    or changed
                )
    return bindings


def _binding_events_v04(
    tree: ast.Module,
    names: frozenset[str],
    *,
    permitted_module_imports: dict[str, str] | None = None,
) -> tuple[str, ...]:
    permitted = permitted_module_imports or {}
    top_level_imports = {
        id(statement)
        for statement in tree.body
        if isinstance(statement, (ast.Import, ast.ImportFrom))
    }
    events: set[str] = set()
    for node in ast.walk(tree):
        targets: tuple[ast.AST, ...] = ()
        kind = type(node).__name__
        if isinstance(node, ast.Assign):
            targets = tuple(node.targets)
        elif isinstance(node, (ast.AnnAssign, ast.AugAssign, ast.NamedExpr)):
            targets = (node.target,)
        elif isinstance(node, (ast.For, ast.AsyncFor, ast.comprehension)):
            targets = (node.target,)
        elif isinstance(node, (ast.With, ast.AsyncWith)):
            targets = tuple(
                item.optional_vars
                for item in node.items
                if item.optional_vars is not None
            )
        elif isinstance(node, ast.Delete):
            targets = tuple(node.targets)
        for target in targets:
            for name in _bound_name_ids(target) & names:
                events.add(f"{name}:{kind}")
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
            if node.name in names:
                events.add(f"{node.name}:{kind}")
            for name in _argument_binding_names_v03(node.args) & names:
                events.add(f"{name}:{kind}_parameter")
        elif isinstance(node, ast.Lambda):
            for name in _argument_binding_names_v03(node.args) & names:
                events.add(f"{name}:Lambda_parameter")
        elif isinstance(node, ast.ClassDef) and node.name in names:
            events.add(f"{node.name}:ClassDef")
        elif isinstance(node, ast.ExceptHandler) and node.name in names:
            events.add(f"{node.name}:ExceptHandler")
        elif isinstance(node, (ast.Global, ast.Nonlocal)):
            for name in set(node.names) & names:
                events.add(f"{name}:{kind}")
        elif isinstance(node, (ast.Import, ast.ImportFrom)):
            module = node.module or "" if isinstance(node, ast.ImportFrom) else ""
            for alias in node.names:
                bound = alias.asname or (
                    alias.name
                    if isinstance(node, ast.ImportFrom)
                    else alias.name.split(".", 1)[0]
                )
                if bound not in names:
                    continue
                target = (
                    f"{module}.{alias.name}" if module else alias.name
                )
                if (
                    id(node) in top_level_imports
                    and permitted.get(bound) == target
                ):
                    continue
                events.add(f"{bound}:{kind}")
    return tuple(sorted(events))


def _unshadowed_builtin_v04(tree: ast.Module, name: str) -> bool:
    return not _binding_events_v04(tree, frozenset({name}))


class _LexicalBindingVisitorV03(ast.NodeVisitor):
    def __init__(
        self,
        root: ast.FunctionDef | ast.AsyncFunctionDef | None,
        protected: frozenset[str],
        module_aliases: frozenset[str],
    ) -> None:
        self.root = root
        self.protected = protected
        self.module_aliases = set(module_aliases)
        self.events: set[str] = set()

    def _propagate_module_alias(self, target: ast.AST, value: ast.AST) -> None:
        if not (
            isinstance(value, ast.Name)
            and value.id in self.module_aliases
        ):
            return
        self.module_aliases.update(_bound_name_ids(target))

    def _target(self, target: ast.AST, kind: str) -> None:
        for name in _bound_name_ids(target) & self.protected:
            self.events.add(f"{name}:{kind}")
        root = _target_root_name_v03(target)
        if isinstance(target, (ast.Attribute, ast.Subscript)) and (
            root in self.module_aliases
            or _expression_uses_names_v03(target, self.module_aliases)
        ):
            self.events.add(f"{root}:module_{kind}")

    def visit_FunctionDef(self, node: ast.FunctionDef) -> None:
        if node is self.root:
            for name in _argument_binding_names_v03(node.args) & self.protected:
                self.events.add(f"{name}:parameter")
            for statement in node.body:
                self.visit(statement)
            return
        if node.name in self.protected:
            self.events.add(f"{node.name}:FunctionDef")

    def visit_AsyncFunctionDef(self, node: ast.AsyncFunctionDef) -> None:
        if node is self.root:
            for name in _argument_binding_names_v03(node.args) & self.protected:
                self.events.add(f"{name}:parameter")
            for statement in node.body:
                self.visit(statement)
            return
        if node.name in self.protected:
            self.events.add(f"{node.name}:AsyncFunctionDef")

    def visit_ClassDef(self, node: ast.ClassDef) -> None:
        if node.name in self.protected:
            self.events.add(f"{node.name}:ClassDef")

    def visit_Lambda(self, node: ast.Lambda) -> None:
        for name in _argument_binding_names_v03(node.args) & self.protected:
            self.events.add(f"{name}:lambda_parameter")

    def visit_Assign(self, node: ast.Assign) -> None:
        for target in node.targets:
            self._propagate_module_alias(target, node.value)
            self._target(target, "Assign")
        self.visit(node.value)

    def visit_AnnAssign(self, node: ast.AnnAssign) -> None:
        if node.value is not None:
            self._propagate_module_alias(node.target, node.value)
        self._target(node.target, "AnnAssign")
        if node.value is not None:
            self.visit(node.value)

    def visit_AugAssign(self, node: ast.AugAssign) -> None:
        self._target(node.target, "AugAssign")
        self.visit(node.value)

    def visit_NamedExpr(self, node: ast.NamedExpr) -> None:
        self._propagate_module_alias(node.target, node.value)
        self._target(node.target, "NamedExpr")
        self.visit(node.value)

    def visit_Delete(self, node: ast.Delete) -> None:
        for target in node.targets:
            self._target(target, "Delete")

    def visit_For(self, node: ast.For) -> None:
        self._target(node.target, "For")
        self.generic_visit(node)

    def visit_AsyncFor(self, node: ast.AsyncFor) -> None:
        self._target(node.target, "AsyncFor")
        self.generic_visit(node)

    def visit_comprehension(self, node: ast.comprehension) -> None:
        self._target(node.target, "comprehension")
        self.generic_visit(node)

    def visit_With(self, node: ast.With) -> None:
        for item in node.items:
            if item.optional_vars is not None:
                self._target(item.optional_vars, "With")
        self.generic_visit(node)

    def visit_AsyncWith(self, node: ast.AsyncWith) -> None:
        for item in node.items:
            if item.optional_vars is not None:
                self._target(item.optional_vars, "AsyncWith")
        self.generic_visit(node)

    def visit_ExceptHandler(self, node: ast.ExceptHandler) -> None:
        if node.name in self.protected:
            self.events.add(f"{node.name}:ExceptHandler")
        self.generic_visit(node)

    def visit_Import(self, node: ast.Import) -> None:
        for alias in node.names:
            bound = alias.asname or alias.name.split(".", 1)[0]
            if bound in self.protected:
                self.events.add(f"{bound}:Import")

    def visit_ImportFrom(self, node: ast.ImportFrom) -> None:
        for alias in node.names:
            bound = alias.asname or alias.name
            if bound in self.protected:
                self.events.add(f"{bound}:ImportFrom")

    def visit_Global(self, node: ast.Global) -> None:
        for name in set(node.names) & self.protected:
            self.events.add(f"{name}:Global")

    def visit_Nonlocal(self, node: ast.Nonlocal) -> None:
        for name in set(node.names) & self.protected:
            self.events.add(f"{name}:Nonlocal")

    def visit_Call(self, node: ast.Call) -> None:
        called = (_dotted_ast_name(node.func) or "").split(".")[-1]
        if called in {"setattr", "delattr"} and node.args:
            root = _target_root_name_v03(node.args[0])
            if root in self.module_aliases:
                self.events.add(f"{root}:{called}")
        if (
            isinstance(node.func, ast.Attribute)
            and node.func.attr in CRITICAL_MUTATING_METHODS_V03
            and _expression_uses_names_v03(
                node.func.value, self.module_aliases
            )
        ):
            self.events.add(f"module:{node.func.attr}")
        if any(
            _expression_uses_names_v03(argument, self.module_aliases)
            for argument in node.args
        ) or any(
            _expression_uses_names_v03(keyword.value, self.module_aliases)
            for keyword in node.keywords
        ):
            self.events.add("module:call_escape")
        self.generic_visit(node)


def _lexical_shadow_events_v03(
    root: ast.FunctionDef | ast.AsyncFunctionDef,
    *,
    protected: frozenset[str],
    module_aliases: frozenset[str],
) -> tuple[str, ...]:
    visitor = _LexicalBindingVisitorV03(root, protected, module_aliases)
    visitor.visit(root)
    return tuple(sorted(visitor.events))


def _module_shadow_events_v03(
    tree: ast.Module,
    *,
    protected: frozenset[str],
    module_aliases: frozenset[str],
    permitted_import_targets: dict[str, str],
) -> tuple[str, ...]:
    visitor = _LexicalBindingVisitorV03(None, protected, module_aliases)
    for statement in tree.body:
        if isinstance(statement, (ast.Import, ast.ImportFrom)):
            aliases = statement.names
            for alias in aliases:
                bound = alias.asname or alias.name.split(".", 1)[0]
                if bound in protected and bound not in permitted_import_targets:
                    visitor.events.add(f"{bound}:module_import")
            continue
        visitor.visit(statement)
    return tuple(sorted(visitor.events))


def _public_module_provenance_failures_v04(
    tree: ast.Module,
    *,
    module_aliases: frozenset[str],
    collector_name: str,
    validator_name: str,
) -> tuple[str, ...]:
    if not module_aliases:
        return ()
    bindings = {
        name: _PROVENANCE_IDENTITY_V04 for name in module_aliases
    }
    changed = True
    nodes = tuple(ast.walk(tree))
    while changed:
        changed = False
        for node in nodes:
            targets: tuple[ast.AST, ...] = ()
            value: ast.AST | None = None
            if isinstance(node, ast.Assign):
                targets = tuple(node.targets)
                value = node.value
            elif isinstance(node, ast.AnnAssign) and node.value is not None:
                targets = (node.target,)
                value = node.value
            elif isinstance(node, ast.NamedExpr):
                targets = (node.target,)
                value = node.value
            elif isinstance(node, (ast.For, ast.AsyncFor, ast.comprehension)):
                targets = (node.target,)
                value = node.iter
            if value is None or any(
                isinstance(child, ast.Call) for child in ast.walk(value)
            ):
                continue
            kind = _expression_provenance_v04(value, bindings)
            for target in targets:
                changed = (
                    _propagate_provenance_target_v04(
                        target, kind, bindings
                    )
                    or changed
                )
    failures: set[str] = set()
    allowed_attributes = {collector_name, validator_name}
    for node in ast.walk(tree):
        targets: tuple[ast.AST, ...] = ()
        value: ast.AST | None = None
        if isinstance(node, ast.Assign):
            targets = tuple(node.targets)
            value = node.value
        elif isinstance(node, ast.AnnAssign):
            targets = (node.target,)
            value = node.value
        elif isinstance(node, ast.NamedExpr):
            targets = (node.target,)
            value = node.value
        elif isinstance(node, ast.AugAssign):
            targets = (node.target,)
            value = node.value
        elif isinstance(node, ast.Delete):
            targets = tuple(node.targets)
        for target in targets:
            if isinstance(target, (ast.Attribute, ast.Subscript)) and (
                _expression_provenance_v04(target, bindings)
                != _PROVENANCE_NONE_V04
            ):
                failures.add("public_module_mutated")
            if (
                value is not None
                and isinstance(target, (ast.Attribute, ast.Subscript))
                and _expression_provenance_v04(value, bindings)
                != _PROVENANCE_NONE_V04
            ):
                failures.add("public_module_stored")
        if isinstance(node, (ast.Return, ast.Yield, ast.YieldFrom)):
            value = node.value
            if (
                value is not None
                and _expression_provenance_v04(value, bindings)
                != _PROVENANCE_NONE_V04
            ):
                failures.add("public_module_escaped")
        if not isinstance(node, ast.Call):
            continue
        receiver_kind = (
            _expression_provenance_v04(node.func.value, bindings)
            if isinstance(node.func, ast.Attribute)
            else _PROVENANCE_NONE_V04
        )
        tainted_arguments = any(
            _expression_provenance_v04(argument, bindings)
            != _PROVENANCE_NONE_V04
            for argument in node.args
        ) or any(
            _expression_provenance_v04(keyword.value, bindings)
            != _PROVENANCE_NONE_V04
            for keyword in node.keywords
        )
        if receiver_kind != _PROVENANCE_NONE_V04:
            if not (
                isinstance(node.func.value, ast.Name)
                and node.func.value.id in module_aliases
                and node.func.attr in allowed_attributes
            ):
                failures.add("public_module_callable_or_mutation")
        if tainted_arguments:
            failures.add("public_module_call_escape")
    return tuple(sorted(failures))


def _transparent_collector_spies_v02(
    function: ast.FunctionDef,
    public_collector: str,
    import_targets: dict[str, str],
    protected_bindings: frozenset[str],
    module_aliases: frozenset[str],
) -> frozenset[str]:
    valid: set[str] = set()
    fresh_recorders: set[str] = set()
    for statement in function.body:
        if not (
            isinstance(statement, ast.Assign)
            and len(statement.targets) == 1
            and isinstance(statement.targets[0], ast.Name)
            and isinstance(statement.value, ast.List)
            and not statement.value.elts
        ):
            continue
        recorder = statement.targets[0].id
        binding_count = 0
        for node in ast.walk(function):
            targets: tuple[ast.AST, ...] = ()
            if isinstance(node, ast.Assign):
                targets = tuple(node.targets)
            elif isinstance(node, (ast.AnnAssign, ast.AugAssign, ast.NamedExpr)):
                targets = (node.target,)
            elif isinstance(node, (ast.For, ast.AsyncFor, ast.comprehension)):
                targets = (node.target,)
            elif isinstance(node, (ast.With, ast.AsyncWith)):
                targets = tuple(
                    item.optional_vars
                    for item in node.items
                    if item.optional_vars is not None
                )
            elif isinstance(node, ast.Delete):
                targets = tuple(node.targets)
            binding_count += sum(
                recorder in _bound_name_ids(target) for target in targets
            )
            if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef, ast.Lambda)):
                binding_count += int(
                    recorder in _argument_binding_names_v03(node.args)
                )
        if binding_count == 1:
            fresh_recorders.add(recorder)

    for statement in function.body:
        if not isinstance(statement, ast.FunctionDef) or statement.decorator_list:
            continue
        if (
            statement.args.defaults
            or any(item is not None for item in statement.args.kw_defaults)
            or len(statement.body) != 3
            or not isinstance(statement.body[-1], ast.Return)
        ):
            continue
        if _lexical_shadow_events_v03(
            statement,
            protected=protected_bindings,
            module_aliases=module_aliases,
        ):
            continue
        first = statement.body[0]
        returned = statement.body[-1].value
        if not (
            isinstance(first, ast.Assign)
            and len(first.targets) == 1
            and isinstance(first.targets[0], ast.Name)
            and isinstance(first.value, ast.Call)
            and _resolved_call_target_v02(first.value.func, import_targets)
            == public_collector
            and isinstance(returned, ast.Name)
            and returned.id == first.targets[0].id
        ):
            continue
        result_name = first.targets[0].id
        middle = statement.body[1]
        if not (
            isinstance(middle, ast.Expr)
            and isinstance(middle.value, ast.Call)
            and isinstance(middle.value.func, ast.Attribute)
            and isinstance(middle.value.func.value, ast.Name)
            and middle.value.func.value.id in fresh_recorders
            and middle.value.func.attr == "append"
            and len(middle.value.args) == 1
            and isinstance(middle.value.args[0], ast.Name)
            and middle.value.args[0].id == result_name
            and not middle.value.keywords
        ):
            continue
        valid.add(statement.name)
    return frozenset(valid)


def _module_literal_values_v03(tree: ast.Module) -> dict[str, object]:
    direct: dict[str, list[tuple[ast.stmt, ast.AST]]] = {}
    for statement in tree.body:
        if (
            isinstance(statement, ast.Assign)
            and len(statement.targets) == 1
            and isinstance(statement.targets[0], ast.Name)
        ):
            direct.setdefault(statement.targets[0].id, []).append(
                (statement, statement.value)
            )
        elif (
            isinstance(statement, ast.AnnAssign)
            and isinstance(statement.target, ast.Name)
            and statement.value is not None
        ):
            direct.setdefault(statement.target.id, []).append(
                (statement, statement.value)
            )
    invalid: set[str] = set()
    permitted = {
        id(statement)
        for rows in direct.values()
        for statement, _value in rows
        if len(rows) == 1
    }
    for node in ast.walk(tree):
        targets: tuple[ast.AST, ...] = ()
        if isinstance(node, ast.Assign):
            targets = tuple(node.targets)
        elif isinstance(node, (ast.AnnAssign, ast.AugAssign, ast.NamedExpr)):
            targets = (node.target,)
        elif isinstance(node, (ast.For, ast.AsyncFor, ast.comprehension)):
            targets = (node.target,)
        elif isinstance(node, (ast.With, ast.AsyncWith)):
            targets = tuple(
                item.optional_vars
                for item in node.items
                if item.optional_vars is not None
            )
        elif isinstance(node, ast.Delete):
            targets = tuple(node.targets)
        for target in targets:
            if id(node) not in permitted:
                invalid.update(_bound_name_ids(target))
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef)):
            invalid.add(node.name)
        elif isinstance(node, (ast.Import, ast.ImportFrom)):
            invalid.update(
                alias.asname or alias.name.split(".", 1)[0]
                for alias in node.names
            )
        elif isinstance(node, (ast.Global, ast.Nonlocal)):
            invalid.update(node.names)
        elif isinstance(node, ast.Call):
            called = (_dotted_ast_name(node.func) or "").split(".")[-1]
            if called in {"exec", "eval", "globals", "locals"}:
                invalid.update(direct)
    pending = [
        (name, rows[0][1])
        for name, rows in direct.items()
        if len(rows) == 1 and name not in invalid
    ]
    values: dict[str, object] = {}
    while pending:
        remaining: list[tuple[str, ast.AST]] = []
        progressed = False
        for name, node in pending:
            try:
                values[name] = _static_value(node, values)
                progressed = True
            except StaticValueUnavailable:
                remaining.append((name, node))
        if not progressed:
            break
        pending = remaining
    return values


def _direct_report_field_v03(node: ast.AST, report_name: str) -> str | None:
    if (
        isinstance(node, ast.Subscript)
        and isinstance(node.value, ast.Name)
        and node.value.id == report_name
        and isinstance(node.slice, ast.Constant)
        and type(node.slice.value) is str
    ):
        return node.slice.value
    if (
        isinstance(node, ast.Attribute)
        and isinstance(node.value, ast.Name)
        and node.value.id == report_name
    ):
        return node.attr
    return None


def _report_rooted_fields_v03(
    node: ast.AST,
    report_name: str,
) -> frozenset[str]:
    return frozenset(
        field
        for child in ast.walk(node)
        if (field := _direct_report_field_v03(child, report_name)) is not None
    )


def _static_equals_v03(
    node: ast.AST,
    expected: object,
    module_values: dict[str, object],
) -> bool:
    try:
        value = _static_value(node, module_values)
    except StaticValueUnavailable:
        return False
    return type(value) is type(expected) and value == expected


def _assertion_comparisons_v03(assertions: Sequence[ast.Assert]) -> tuple[ast.Compare, ...]:
    return tuple(
        node
        for assertion in assertions
        for node in ast.walk(assertion.test)
        if isinstance(node, ast.Compare)
        and len(node.ops) == 1
        and len(node.comparators) == 1
    )


def _has_exact_validation_success_v03(
    comparisons: Sequence[ast.Compare],
    validation_name: str,
) -> bool:
    for comparison in comparisons:
        if not isinstance(comparison.ops[0], ast.Eq):
            continue
        left = comparison.left
        right = comparison.comparators[0]
        for actual, expected in ((left, right), (right, left)):
            if (
                isinstance(actual, ast.Name)
                and actual.id == validation_name
                and isinstance(expected, ast.Tuple)
                and not expected.elts
            ):
                return True
    return False


def _has_report_expected_comparison_v03(
    comparisons: Sequence[ast.Compare],
    *,
    report_name: str,
    field: str,
    expected: object,
    module_values: dict[str, object],
    direct: bool,
) -> bool:
    for comparison in comparisons:
        if not isinstance(comparison.ops[0], ast.Eq):
            continue
        left = comparison.left
        right = comparison.comparators[0]
        if ast.dump(left, include_attributes=False) == ast.dump(
            right, include_attributes=False
        ):
            continue
        for actual, expected_node in ((left, right), (right, left)):
            actual_matches = (
                _direct_report_field_v03(actual, report_name) == field
                if direct
                else field in _report_rooted_fields_v03(actual, report_name)
            )
            if actual_matches and _static_equals_v03(
                expected_node, expected, module_values
            ):
                return True
    return False


def _geometry_projection_matches_v03(
    node: ast.AST,
    *,
    report_name: str,
    field: str,
    expected: object,
    living: bool,
) -> bool:
    scalar_fields = (
        {
            "runner_version",
            "kernel_conformance_profile",
            "historical_kernel_conformance_profile",
        }
        if living
        else {
            "conformance_version",
            "profile_id",
            "historical_profile_ref",
            "active_gauntlet_refs",
        }
    )
    if field in scalar_fields:
        return _direct_report_field_v03(node, report_name) == field
    if not (
        isinstance(node, ast.Call)
        and isinstance(node.func, ast.Name)
        and node.func.id == "tuple"
        and len(node.args) == 1
        and not node.keywords
        and isinstance(node.args[0], ast.GeneratorExp)
    ):
        return False
    generator = node.args[0]
    if len(generator.generators) != 1:
        return False
    comprehension = generator.generators[0]
    if (
        comprehension.ifs
        or comprehension.is_async
        or not isinstance(comprehension.target, ast.Name)
        or _direct_report_field_v03(comprehension.iter, report_name) != field
    ):
        return False
    item_name = comprehension.target.id
    element = generator.elt
    if living:
        return (
            field == "active_act_results"
            and isinstance(element, ast.Subscript)
            and isinstance(element.value, ast.Name)
            and element.value.id == item_name
            and isinstance(element.slice, ast.Constant)
            and element.slice.value == "act_id"
        )
    attribute = (
        element.attr
        if isinstance(element, ast.Attribute)
        and isinstance(element.value, ast.Name)
        and element.value.id == item_name
        else None
    )
    if field == "category_results" and expected == tuple(
        item[0] for item in POST_E6_CATEGORY_CHECK_IDS
    ):
        return attribute == "category_id"
    if field == "category_results" and expected == POST_E6_CATEGORY_CHECK_IDS:
        return (
            isinstance(element, ast.Tuple)
            and len(element.elts) == 2
            and all(
                isinstance(child, ast.Attribute)
                and isinstance(child.value, ast.Name)
                and child.value.id == item_name
                for child in element.elts
            )
            and tuple(child.attr for child in element.elts)
            == ("category_id", "required_check_ids")
        )
    if field == "negative_test_results":
        return attribute == "probe_id"
    if field == "domain_results":
        return attribute == "domain_id"
    return False


def _has_geometry_comparison_v03(
    comparisons: Sequence[ast.Compare],
    *,
    report_name: str,
    field: str,
    expected: object,
    module_values: dict[str, object],
    living: bool,
) -> bool:
    for comparison in comparisons:
        if not isinstance(comparison.ops[0], ast.Eq):
            continue
        left = comparison.left
        right = comparison.comparators[0]
        if ast.dump(left, include_attributes=False) == ast.dump(
            right, include_attributes=False
        ):
            continue
        for actual, expected_node in ((left, right), (right, left)):
            if _geometry_projection_matches_v03(
                actual,
                report_name=report_name,
                field=field,
                expected=expected,
                living=living,
            ) and _static_equals_v03(expected_node, expected, module_values):
                return True
    return False


def _has_distinct_report_field_relation_v03(
    comparisons: Sequence[ast.Compare],
    *,
    report_name: str,
    first_field: str,
    second_field: str,
) -> bool:
    for comparison in comparisons:
        if not isinstance(comparison.ops[0], ast.Eq):
            continue
        left_field = _direct_report_field_v03(comparison.left, report_name)
        right_field = _direct_report_field_v03(
            comparison.comparators[0], report_name
        )
        if {left_field, right_field} == {first_field, second_field}:
            return True
    return False


def _has_length_check_v03(
    comparisons: Sequence[ast.Compare],
    *,
    report_name: str,
    field: str,
    expected_length: int,
) -> bool:
    for comparison in comparisons:
        if not isinstance(comparison.ops[0], ast.Eq):
            continue
        for actual, expected in (
            (comparison.left, comparison.comparators[0]),
            (comparison.comparators[0], comparison.left),
        ):
            if not (
                isinstance(actual, ast.Call)
                and isinstance(actual.func, ast.Name)
                and actual.func.id == "len"
                and len(actual.args) == 1
                and not actual.keywords
                and _direct_report_field_v03(actual.args[0], report_name) == field
            ):
                continue
            if isinstance(expected, ast.Constant) and expected.value == expected_length:
                return True
    return False


def _has_hex_alphabet_check_v03(
    comparisons: Sequence[ast.Compare],
    *,
    report_name: str,
    field: str,
) -> bool:
    for comparison in comparisons:
        if not isinstance(comparison.ops[0], ast.LtE):
            continue
        left = comparison.left
        right = comparison.comparators[0]
        if not (
            isinstance(left, ast.Call)
            and isinstance(left.func, ast.Name)
            and left.func.id == "set"
            and len(left.args) == 1
            and not left.keywords
            and _direct_report_field_v03(left.args[0], report_name) == field
            and isinstance(right, ast.Call)
            and isinstance(right.func, ast.Name)
            and right.func.id == "set"
            and len(right.args) == 1
            and not right.keywords
            and isinstance(right.args[0], ast.Constant)
            and right.args[0].value == "0123456789abcdef"
        ):
            continue
        return True
    return False


def _has_positive_field_check_v03(
    comparisons: Sequence[ast.Compare],
    *,
    report_name: str,
    field: str,
) -> bool:
    for comparison in comparisons:
        left = comparison.left
        right = comparison.comparators[0]
        operator = comparison.ops[0]
        if (
            isinstance(operator, ast.Gt)
            and _direct_report_field_v03(left, report_name) == field
            and isinstance(right, ast.Constant)
            and right.value == 0
        ) or (
            isinstance(operator, ast.Lt)
            and isinstance(left, ast.Constant)
            and left.value == 0
            and _direct_report_field_v03(right, report_name) == field
        ):
            return True
    return False


def _tautological_assertion_v03(
    assertion: ast.Assert,
    *,
    report_name: str | None,
    validation_name: str | None,
) -> bool:
    test = assertion.test
    if isinstance(test, (ast.Tuple, ast.List, ast.Dict, ast.Set)):
        return True
    if isinstance(test, ast.Name) and test.id in {report_name, validation_name}:
        return True
    for comparison in (
        node for node in ast.walk(test) if isinstance(node, ast.Compare)
    ):
        sides = (comparison.left, *comparison.comparators)
        if len(sides) == 2 and ast.dump(
            sides[0], include_attributes=False
        ) == ast.dump(sides[1], include_attributes=False):
            if any(
                isinstance(node, ast.Name)
                and node.id in {report_name, validation_name}
                for side in sides
                for node in ast.walk(side)
            ) or all(isinstance(side, ast.Constant) for side in sides):
                return True
    return False


def _actual_return_lineage_failures_v03(
    function: ast.FunctionDef,
    *,
    tree: ast.Module,
    report_name: str | None,
    validation_name: str | None,
    collector_statement: ast.Assign | None,
    validator_statement: ast.Assign | None,
    qualified_validator: str,
    import_targets: dict[str, str],
) -> tuple[str, ...]:
    protected = {
        name for name in (report_name, validation_name) if name is not None
    }
    if not protected:
        return ()
    failures: set[str] = set()
    allowed_assignments = {
        id(statement)
        for statement in (collector_statement, validator_statement)
        if statement is not None
    }
    report_bindings = (
        _provenance_bindings_v04(
            function,
            {report_name: _PROVENANCE_IDENTITY_V04},
        )
        if report_name is not None
        else {}
    )
    report_identity_aliases = {
        name
        for name, kind in report_bindings.items()
        if kind in {
            _PROVENANCE_IDENTITY_V04,
            _PROVENANCE_CONTAINER_V04,
        }
    }
    proof_builtin_names = frozenset({"len", "set", "tuple"})
    shadowed_proof_builtins = set(
        proof_builtin_names & _module_level_bound_names_v05(tree)
    )
    shadowed_proof_builtins.update(
        event.split(":", 1)[0]
        for event in _binding_events_v04(function, proof_builtin_names)
    )
    unshadowed_proof_builtins = (
        proof_builtin_names - shadowed_proof_builtins
    )
    for node in ast.walk(function):
        targets: tuple[ast.AST, ...] = ()
        if isinstance(node, ast.Assign):
            targets = tuple(node.targets)
        elif isinstance(node, ast.AnnAssign):
            targets = (node.target,)
        elif isinstance(node, ast.AugAssign):
            targets = (node.target,)
        elif isinstance(node, ast.NamedExpr):
            targets = (node.target,)
        elif isinstance(node, (ast.For, ast.AsyncFor, ast.comprehension)):
            targets = (node.target,)
        elif isinstance(node, (ast.With, ast.AsyncWith)):
            targets = tuple(
                item.optional_vars
                for item in node.items
                if item.optional_vars is not None
            )
        elif isinstance(node, ast.Delete):
            targets = tuple(node.targets)
        for target in targets:
            root = _target_root_name_v03(target)
            names = _bound_name_ids(target)
            if set(names) & protected or root in protected:
                if not (
                    id(node) in allowed_assignments
                    and isinstance(target, ast.Name)
                    and target.id in protected
                ):
                    failures.add("binding_reassigned_or_mutated")
            if report_name is None:
                continue
            value: ast.AST | None = None
            if isinstance(node, (ast.Assign, ast.AnnAssign, ast.NamedExpr)):
                value = node.value
            elif isinstance(node, ast.AugAssign):
                value = node.value
            value_kind = (
                _expression_provenance_v04(value, report_bindings)
                if value is not None
                else _PROVENANCE_NONE_V04
            )
            target_names = set(_bound_name_ids(target))
            target_kind = _expression_provenance_v04(
                target, report_bindings
            )
            if isinstance(target, (ast.Attribute, ast.Subscript)) and (
                target_kind != _PROVENANCE_NONE_V04
                or value_kind != _PROVENANCE_NONE_V04
            ):
                failures.add("actual_report_storage_or_mutation")
            if target_names & report_identity_aliases:
                if (
                    id(node) not in allowed_assignments
                    and value_kind == _PROVENANCE_NONE_V04
                ):
                    failures.add("actual_report_alias_replaced")
            if (
                isinstance(target, ast.Name)
                and value_kind == _PROVENANCE_CONTAINER_V04
            ):
                failures.add("actual_report_stored")
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
            if node is not function and node.name in protected:
                failures.add("binding_reassigned_or_mutated")
            if _argument_binding_names_v03(node.args) & protected:
                failures.add("binding_shadowed_by_parameter")
        elif isinstance(node, ast.ClassDef) and node.name in protected:
            failures.add("binding_reassigned_or_mutated")
        elif isinstance(node, (ast.Global, ast.Nonlocal)):
            if set(node.names) & protected:
                failures.add("binding_namespace_escape")
        elif isinstance(node, (ast.Import, ast.ImportFrom)):
            for alias in node.names:
                bound = alias.asname or alias.name.split(".", 1)[0]
                if bound in protected:
                    failures.add("binding_reassigned_or_mutated")
        if isinstance(node, (ast.Return, ast.Yield, ast.YieldFrom)):
            value = node.value
            if (
                value is not None
                and _expression_provenance_v04(value, report_bindings)
                != _PROVENANCE_NONE_V04
            ):
                failures.add("actual_report_escaped_or_mutated")
        if not isinstance(node, ast.Call) or report_name is None:
            continue
        report_in_arguments = any(
            _expression_provenance_v04(argument, report_bindings)
            != _PROVENANCE_NONE_V04
            for argument in node.args
        ) or any(
            _expression_provenance_v04(keyword.value, report_bindings)
            != _PROVENANCE_NONE_V04
            for keyword in node.keywords
        )
        report_receiver = (
            isinstance(node.func, ast.Attribute)
            and _expression_provenance_v04(
                node.func.value, report_bindings
            )
            != _PROVENANCE_NONE_V04
        )
        report_callable = (
            _expression_provenance_v04(node.func, report_bindings)
            != _PROVENANCE_NONE_V04
            and not report_receiver
        )
        if not report_in_arguments and not report_receiver and not report_callable:
            continue
        called = _resolved_call_target_v02(node.func, import_targets) or ""
        leaf = called.split(".")[-1]
        if called == qualified_validator:
            continue
        if (
            isinstance(node.func, ast.Name)
            and node.func.id in unshadowed_proof_builtins
        ):
            continue
        if leaf in CRITICAL_MUTATING_METHODS_V03:
            failures.add("actual_report_escaped_or_mutated")
            continue
        failures.add("actual_report_escaped_or_mutated")
    return tuple(sorted(failures))


def _static_string_v05(node: ast.AST) -> str | None:
    try:
        value = _static_value(node, {})
    except StaticValueUnavailable:
        return None
    return value if type(value) is str else None


def _definition_time_expressions_v05(
    node: ast.FunctionDef | ast.AsyncFunctionDef | ast.Lambda | ast.ClassDef,
) -> tuple[ast.AST, ...]:
    if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
        annotations = tuple(
            argument.annotation
            for argument in (
                *node.args.posonlyargs,
                *node.args.args,
                *node.args.kwonlyargs,
            )
            if argument.annotation is not None
        )
        if node.args.vararg is not None and node.args.vararg.annotation is not None:
            annotations += (node.args.vararg.annotation,)
        if node.args.kwarg is not None and node.args.kwarg.annotation is not None:
            annotations += (node.args.kwarg.annotation,)
        if node.returns is not None:
            annotations += (node.returns,)
        return (
            *node.decorator_list,
            *node.args.defaults,
            *(item for item in node.args.kw_defaults if item is not None),
            *annotations,
        )
    if isinstance(node, ast.Lambda):
        annotations = tuple(
            argument.annotation
            for argument in (
                *node.args.posonlyargs,
                *node.args.args,
                *node.args.kwonlyargs,
            )
            if argument.annotation is not None
        )
        if node.args.vararg is not None and node.args.vararg.annotation is not None:
            annotations += (node.args.vararg.annotation,)
        if node.args.kwarg is not None and node.args.kwarg.annotation is not None:
            annotations += (node.args.kwarg.annotation,)
        return (
            *node.args.defaults,
            *(item for item in node.args.kw_defaults if item is not None),
            *annotations,
        )
    return (*node.decorator_list, *node.bases, *(item.value for item in node.keywords))


def _module_identity_expression_v05(
    node: ast.AST,
    *,
    aliases: set[str],
    getter_names: set[str],
    module_name: str,
    import_targets: dict[str, str],
) -> bool:
    if isinstance(node, ast.Name):
        return node.id in aliases or (
            module_name == "builtins" and node.id == "__builtins__"
        )
    if isinstance(node, ast.Starred):
        return _module_identity_expression_v05(
            node.value,
            aliases=aliases,
            getter_names=getter_names,
            module_name=module_name,
            import_targets=import_targets,
        )
    if isinstance(node, ast.NamedExpr):
        return _module_identity_expression_v05(
            node.value,
            aliases=aliases,
            getter_names=getter_names,
            module_name=module_name,
            import_targets=import_targets,
        )
    if isinstance(node, ast.IfExp):
        return any(
            _module_identity_expression_v05(
                value,
                aliases=aliases,
                getter_names=getter_names,
                module_name=module_name,
                import_targets=import_targets,
            )
            for value in (node.body, node.orelse)
        )
    if isinstance(node, ast.BoolOp):
        return any(
            _module_identity_expression_v05(
                value,
                aliases=aliases,
                getter_names=getter_names,
                module_name=module_name,
                import_targets=import_targets,
            )
            for value in node.values
        )
    if isinstance(node, (ast.Tuple, ast.List, ast.Set)):
        return any(
            _module_identity_expression_v05(
                value,
                aliases=aliases,
                getter_names=getter_names,
                module_name=module_name,
                import_targets=import_targets,
            )
            for value in node.elts
        )
    if isinstance(node, ast.Dict):
        return any(
            value is not None
            and _module_identity_expression_v05(
                value,
                aliases=aliases,
                getter_names=getter_names,
                module_name=module_name,
                import_targets=import_targets,
            )
            for value in (*node.keys, *node.values)
        )
    if isinstance(node, ast.Subscript):
        dotted = _dotted_ast_name(node.value) or ""
        if dotted.endswith("sys.modules") or dotted == "sys.modules":
            return _static_string_v05(node.slice) == module_name
        if isinstance(node.value, (ast.Tuple, ast.List, ast.Dict)):
            return any(
                _module_identity_expression_v05(
                    element,
                    aliases=aliases,
                    getter_names=getter_names,
                    module_name=module_name,
                    import_targets=import_targets,
                )
                for element in (
                    node.value.elts
                    if isinstance(node.value, (ast.Tuple, ast.List))
                    else (*node.value.keys, *node.value.values)
                )
                if element is not None
            )
        return False
    if isinstance(node, ast.Call):
        if isinstance(node.func, ast.Lambda):
            return _module_identity_expression_v05(
                node.func.body,
                aliases=aliases,
                getter_names=getter_names,
                module_name=module_name,
                import_targets=import_targets,
            )
        called = _resolved_call_target_v02(node.func, import_targets) or ""
        leaf = called.split(".")[-1]
        if isinstance(node.func, ast.Name) and node.func.id in getter_names:
            return True
        if leaf in {"import_module", "__import__"} and node.args:
            return _static_string_v05(node.args[0]) == module_name
    return False


def _module_capability_failures_v05(
    tree: ast.Module,
    *,
    label: str,
    module_name: str,
    protected_attributes: frozenset[str],
) -> tuple[str, ...]:
    import_targets = _module_import_targets_v02(tree)
    aliases = {
        binding
        for binding, target in import_targets.items()
        if target == module_name
    }
    if module_name == "builtins":
        aliases.add("__builtins__")
    getter_names: set[str] = set()
    changed = True
    nodes = tuple(ast.walk(tree))
    while changed:
        changed = False
        for node in nodes:
            if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
                if any(
                    returned.value is not None
                    and _module_identity_expression_v05(
                        returned.value,
                        aliases=aliases,
                        getter_names=getter_names,
                        module_name=module_name,
                        import_targets=import_targets,
                    )
                    for returned in ast.walk(node)
                    if isinstance(returned, ast.Return)
                ) and node.name not in getter_names:
                    getter_names.add(node.name)
                    changed = True
            targets: tuple[ast.AST, ...] = ()
            value: ast.AST | None = None
            if isinstance(node, ast.Assign):
                targets = tuple(node.targets)
                value = node.value
            elif isinstance(node, ast.AnnAssign) and node.value is not None:
                targets = (node.target,)
                value = node.value
            elif isinstance(node, ast.NamedExpr):
                targets = (node.target,)
                value = node.value
            if value is None or not _module_identity_expression_v05(
                value,
                aliases=aliases,
                getter_names=getter_names,
                module_name=module_name,
                import_targets=import_targets,
            ):
                continue
            before = len(aliases)
            for target in targets:
                aliases.update(_bound_name_ids(target))
            changed = changed or len(aliases) != before

    failures: set[str] = set()
    class_node_ids = {
        id(child)
        for class_node in ast.walk(tree)
        if isinstance(class_node, ast.ClassDef)
        for statement in class_node.body
        for child in ast.walk(statement)
    }
    for node in nodes:
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef, ast.Lambda, ast.ClassDef)):
            if any(
                _module_identity_expression_v05(
                    expression,
                    aliases=aliases,
                    getter_names=getter_names,
                    module_name=module_name,
                    import_targets=import_targets,
                )
                for expression in _definition_time_expressions_v05(node)
            ):
                failures.add(f"{label}.definition_time_escape")
        if isinstance(node, ast.Lambda) and _module_identity_expression_v05(
            node.body,
            aliases=aliases,
            getter_names=getter_names,
            module_name=module_name,
            import_targets=import_targets,
        ):
            failures.add(f"{label}.call_return_escape")
        if isinstance(node, ast.Return) and node.value is not None and _module_identity_expression_v05(
            node.value,
            aliases=aliases,
            getter_names=getter_names,
            module_name=module_name,
            import_targets=import_targets,
        ):
            failures.add(f"{label}.call_return_escape")

        targets: tuple[ast.AST, ...] = ()
        value: ast.AST | None = None
        if isinstance(node, ast.Assign):
            targets = tuple(node.targets)
            value = node.value
        elif isinstance(node, ast.AnnAssign) and node.value is not None:
            targets = (node.target,)
            value = node.value
        elif isinstance(node, ast.AugAssign):
            targets = (node.target,)
            value = node.value
        elif isinstance(node, ast.NamedExpr):
            targets = (node.target,)
            value = node.value
        elif isinstance(node, ast.Delete):
            targets = tuple(node.targets)
        for target in targets:
            target_root = _target_root_name_v03(target)
            target_is_module = target_root in aliases or _module_identity_expression_v05(
                target,
                aliases=aliases,
                getter_names=getter_names,
                module_name=module_name,
                import_targets=import_targets,
            )
            if isinstance(target, (ast.Attribute, ast.Subscript)):
                target_is_module = target_is_module or (
                    _module_identity_expression_v05(
                        target.value,
                        aliases=aliases,
                        getter_names=getter_names,
                        module_name=module_name,
                        import_targets=import_targets,
                    )
                )
            protected = False
            if isinstance(target, ast.Attribute):
                protected = target.attr in protected_attributes or target.attr == "__dict__"
            elif isinstance(target, ast.Subscript):
                protected = _static_string_v05(target.slice) in protected_attributes
                if isinstance(target.value, ast.Attribute) and target.value.attr == "__dict__":
                    target_is_module = _module_identity_expression_v05(
                        target.value.value,
                        aliases=aliases,
                        getter_names=getter_names,
                        module_name=module_name,
                        import_targets=import_targets,
                    )
            if target_is_module and protected:
                failures.add(f"{label}.attribute_mutation")
            if (
                value is not None
                and _module_identity_expression_v05(
                    value,
                    aliases=aliases,
                    getter_names=getter_names,
                    module_name=module_name,
                    import_targets=import_targets,
                )
                and (
                    id(node) in class_node_ids
                    or isinstance(value, (ast.Tuple, ast.List, ast.Set, ast.Dict))
                )
            ):
                failures.add(f"{label}.storage_escape")
            if (
                value is not None
                and isinstance(target, (ast.Attribute, ast.Subscript))
                and _module_identity_expression_v05(
                    value,
                    aliases=aliases,
                    getter_names=getter_names,
                    module_name=module_name,
                    import_targets=import_targets,
                )
            ):
                failures.add(f"{label}.storage_escape")
        if not isinstance(node, ast.Call):
            continue
        called = _resolved_call_target_v02(node.func, import_targets) or ""
        leaf = called.split(".")[-1]
        if leaf in {"setattr", "delattr"} and len(node.args) >= 2:
            if _module_identity_expression_v05(
                node.args[0],
                aliases=aliases,
                getter_names=getter_names,
                module_name=module_name,
                import_targets=import_targets,
            ) and _static_string_v05(node.args[1]) in protected_attributes:
                failures.add(f"{label}.attribute_mutation")
        if isinstance(node.func, ast.Attribute) and node.func.attr in {
            "__setitem__",
            "__delitem__",
            "update",
            "pop",
            "clear",
        }:
            receiver = node.func.value
            receiver_is_dict = (
                isinstance(receiver, ast.Attribute)
                and receiver.attr == "__dict__"
                and _module_identity_expression_v05(
                    receiver.value,
                    aliases=aliases,
                    getter_names=getter_names,
                    module_name=module_name,
                    import_targets=import_targets,
                )
            )
            keys = {
                value
                for argument in (*node.args, *(item.value for item in node.keywords))
                for value in (
                    [_static_string_v05(argument)]
                    if _static_string_v05(argument) is not None
                    else []
                )
            }
            if receiver_is_dict and (not keys or keys & protected_attributes):
                failures.add(f"{label}.attribute_mutation")
    return tuple(sorted(failures))


def _dynamic_namespace_failures_v05(
    tree: ast.Module,
    *,
    label: str,
    protected_names: frozenset[str],
) -> tuple[str, ...]:
    import_targets = _module_import_targets_v02(tree)
    failures: set[str] = set()
    namespace_aliases: set[str] = set()
    namespace_callable_aliases: set[str] = set()

    def namespace_callable(node: ast.AST) -> bool:
        if isinstance(node, ast.Name) and node.id in namespace_callable_aliases:
            return True
        called = _resolved_call_target_v02(node, import_targets) or ""
        return called.split(".")[-1] in {"globals", "locals", "vars"}

    def namespace_expression(node: ast.AST) -> bool:
        if isinstance(node, ast.Name) and node.id in {
            "__builtins__",
            *namespace_aliases,
        }:
            return True
        if isinstance(node, ast.Call):
            return namespace_callable(node.func)
        if isinstance(node, ast.Attribute) and node.attr == "__dict__":
            return True
        if isinstance(node, ast.Subscript):
            dotted = _dotted_ast_name(node.value) or ""
            if dotted == "sys.modules" or dotted.endswith(".sys.modules"):
                return True
            return namespace_expression(node.value)
        if isinstance(node, (ast.Tuple, ast.List)):
            return any(namespace_expression(value) for value in node.elts)
        if isinstance(node, ast.BoolOp):
            return any(namespace_expression(value) for value in node.values)
        if isinstance(node, ast.IfExp):
            return namespace_expression(node.body) or namespace_expression(
                node.orelse
            )
        return False

    changed = True
    nodes = tuple(ast.walk(tree))
    while changed:
        changed = False
        for node in nodes:
            targets: tuple[ast.AST, ...] = ()
            value: ast.AST | None = None
            if isinstance(node, ast.Assign):
                targets = tuple(node.targets)
                value = node.value
            elif isinstance(node, ast.AnnAssign) and node.value is not None:
                targets = (node.target,)
                value = node.value
            elif isinstance(node, ast.NamedExpr):
                targets = (node.target,)
                value = node.value
            if value is None:
                continue
            bound = {
                name for target in targets for name in _bound_name_ids(target)
            }
            if namespace_callable(value):
                before = len(namespace_callable_aliases)
                namespace_callable_aliases.update(bound)
                changed = changed or len(namespace_callable_aliases) != before
            if namespace_expression(value):
                before = len(namespace_aliases)
                namespace_aliases.update(bound)
                changed = changed or len(namespace_aliases) != before

    for node in nodes:
        targets: tuple[ast.AST, ...] = ()
        if isinstance(node, ast.Assign):
            targets = tuple(node.targets)
        elif isinstance(node, (ast.AnnAssign, ast.AugAssign, ast.NamedExpr)):
            targets = (node.target,)
        elif isinstance(node, ast.Delete):
            targets = tuple(node.targets)
        for target in targets:
            if not isinstance(target, ast.Subscript):
                continue
            key = _static_string_v05(target.slice)
            if key in protected_names and namespace_expression(target.value):
                failures.add(f"{label}.dynamic_namespace_mutation")
        if not isinstance(node, ast.Call):
            continue
        called = _resolved_call_target_v02(node.func, import_targets) or ""
        leaf = called.split(".")[-1]
        if leaf in {"exec", "eval"} or (
            isinstance(node.func, ast.Name)
            and node.func.id in {"exec", "eval"}
        ):
            if any(
                name in (text or "")
                for name in protected_names
                for text in (_static_string_v05(argument) for argument in node.args)
            ):
                failures.add(f"{label}.dynamic_namespace_mutation")
        if isinstance(node.func, ast.Attribute) and node.func.attr in {
            "__setitem__",
            "__delitem__",
            "update",
            "pop",
        }:
            if namespace_expression(node.func.value):
                keys = {
                    value
                    for argument in node.args
                    for value in [_static_string_v05(argument)]
                    if value is not None
                }
                if not keys or keys & protected_names:
                    failures.add(f"{label}.dynamic_namespace_mutation")
        if leaf in {"setattr", "delattr"} and len(node.args) >= 2:
            if namespace_expression(node.args[0]) and (
                _static_string_v05(node.args[1]) in protected_names
            ):
                failures.add(f"{label}.dynamic_namespace_mutation")
    return tuple(sorted(failures))


def _post_e6_public_binding_use_failures_v05(
    tree: ast.Module,
    function: ast.FunctionDef,
    *,
    label: str,
    public_module: str,
    qualified_collector: str,
    qualified_validator: str,
    import_targets: dict[str, str],
) -> tuple[str, ...]:
    prefix = f"e6.phase.post.test_contract.{label}"
    protected = {
        name
        for name, target in import_targets.items()
        if target in {public_module, qualified_collector, qualified_validator}
    }
    allowed_load_ids: set[int] = set()
    for node in ast.walk(function):
        if not isinstance(node, ast.Call):
            continue
        if _resolved_call_target_v02(node.func, import_targets) not in {
            qualified_collector,
            qualified_validator,
        }:
            continue
        if isinstance(node.func, ast.Name):
            allowed_load_ids.add(id(node.func))
        elif isinstance(node.func, ast.Attribute) and isinstance(
            node.func.value, ast.Name
        ):
            allowed_load_ids.add(id(node.func.value))
    failures: set[str] = set()
    for node in ast.walk(tree):
        if (
            isinstance(node, ast.Name)
            and isinstance(node.ctx, ast.Load)
            and node.id in protected
            and id(node) not in allowed_load_ids
        ):
            failures.add(f"{prefix}.public_binding_escape")
        if isinstance(node, (ast.Assign, ast.AnnAssign, ast.AugAssign, ast.Delete)):
            targets = (
                tuple(node.targets)
                if isinstance(node, (ast.Assign, ast.Delete))
                else (node.target,)
            )
            for target in targets:
                if (
                    isinstance(target, ast.Attribute)
                    and target.attr
                    in {"__code__", "__defaults__", "__kwdefaults__"}
                    and isinstance(target.value, ast.Name)
                    and target.value.id in protected
                ):
                    failures.add(f"{prefix}.public_callable_mutation")
    return tuple(sorted(failures))


def _post_e6_dynamic_capability_failures_v05(
    tree: ast.Module,
    *,
    label: str,
) -> tuple[str, ...]:
    """Reject dynamic namespace machinery absent from the accepted test form."""

    prefix = f"e6.phase.post.test_contract.{label}"
    forbidden_leaf_names = {
        "__import__",
        "delattr",
        "eval",
        "exec",
        "globals",
        "import_module",
        "locals",
        "setattr",
        "vars",
    }
    failures: set[str] = set()
    for node in ast.walk(tree):
        if isinstance(node, ast.Call):
            leaf = (_dotted_ast_name(node.func) or "").split(".")[-1]
            if leaf in forbidden_leaf_names:
                failures.add(f"{prefix}.dynamic_capability")
        if isinstance(node, ast.Attribute) and node.attr in {
            "__code__",
            "__defaults__",
            "__kwdefaults__",
        }:
            failures.add(f"{prefix}.dynamic_capability")
        if isinstance(node, ast.Name) and node.id == "__builtins__":
            failures.add(f"{prefix}.dynamic_capability")
        if isinstance(node, ast.Attribute) and (
            _dotted_ast_name(node) or ""
        ).endswith("sys.modules"):
            failures.add(f"{prefix}.dynamic_capability")
    return tuple(sorted(failures))


def _post_e6_semantic_normal_form_failures_v05(
    tree: ast.Module,
    function: ast.FunctionDef,
    *,
    label: str,
    public_module: str,
    qualified_collector: str,
    qualified_validator: str,
    import_targets: dict[str, str],
) -> tuple[str, ...]:
    prefix = f"e6.phase.post.test_contract.{label}"
    failures: set[str] = set()
    arguments = function.args
    if (
        arguments.posonlyargs
        or arguments.args
        or arguments.kwonlyargs
        or arguments.vararg is not None
        or arguments.kwarg is not None
        or arguments.defaults
        or any(item is not None for item in arguments.kw_defaults)
        or function.returns is not None
        or function.type_comment is not None
        or function.decorator_list
    ):
        failures.add(f"{prefix}.semantic_normal_form:signature")

    public_imports = []
    for statement in tree.body:
        if isinstance(statement, ast.Import):
            if any(alias.name == public_module for alias in statement.names):
                public_imports.append(statement)
        elif isinstance(statement, ast.ImportFrom) and statement.module == public_module:
            if any(
                alias.name
                in {
                    qualified_collector.rsplit(".", 1)[-1],
                    qualified_validator.rsplit(".", 1)[-1],
                }
                for alias in statement.names
            ):
                public_imports.append(statement)
    if len(public_imports) != 1:
        failures.add(f"{prefix}.semantic_normal_form:public_import")
    else:
        public_import = public_imports[0]
        if isinstance(public_import, ast.Import):
            if not (
                len(public_import.names) == 1
                and public_import.names[0].name == public_module
                and public_import.names[0].asname == "public_runner"
            ):
                failures.add(f"{prefix}.semantic_normal_form:public_import")
        else:
            expected = {
                qualified_collector.rsplit(".", 1)[-1],
                qualified_validator.rsplit(".", 1)[-1],
            }
            if len(public_import.names) != 2 or {
                alias.name for alias in public_import.names
            } != expected:
                failures.add(f"{prefix}.semantic_normal_form:public_import")

    first_assert = next(
        (index for index, statement in enumerate(function.body) if isinstance(statement, ast.Assert)),
        len(function.body),
    )
    setup = function.body[:first_assert]
    assertions = function.body[first_assert:]
    if not assertions or any(not isinstance(statement, ast.Assert) for statement in assertions):
        failures.add(f"{prefix}.semantic_normal_form:assertion_tail")

    access = (
        (lambda field: f"report[{field!r}]")
        if label == "living"
        else (lambda field: f"report.{field}")
    )
    canonical_assertion_expressions = [
        "validation == ()",
        *(
            f"{access(field)} == {expected!r}"
            for field, expected in POST_E6_SHARED_FIXED_REPORT_VALUES
        ),
        (
            f"{access(POST_E6_SHARED_SHA256_FIELDS[0])} == "
            f"{access(POST_E6_SHARED_SHA256_FIELDS[1])}"
        ),
        *(
            f"len({access(field)}) == 64"
            for field in POST_E6_SHARED_SHA256_FIELDS
        ),
        *(
            f"set({access(field)}) <= set('0123456789abcdef')"
            for field in POST_E6_SHARED_SHA256_FIELDS
        ),
        (
            f"{access(POST_E6_SHARED_BYTE_COUNT_FIELDS[0])} == "
            f"{access(POST_E6_SHARED_BYTE_COUNT_FIELDS[1])}"
        ),
        *(
            f"{access(field)} > 0"
            for field in POST_E6_SHARED_BYTE_COUNT_FIELDS
        ),
    ]
    if label == "living":
        canonical_assertion_expressions.extend(
            (
                f"{access(field)} == {expected!r}"
                for field, expected in POST_E6_LIVING_GEOMETRY_ASSERTIONS[:-1]
            )
        )
        canonical_assertion_expressions.append(
            "tuple(row['act_id'] for row in "
            f"{access('active_act_results')}) == "
            f"{POST_E6_LIVING_GEOMETRY_ASSERTIONS[-1][1]!r}"
        )
    else:
        canonical_assertion_expressions.extend(
            (
                f"{access(field)} == {expected!r}"
                for field, expected in POST_E6_CONFORMANCE_GEOMETRY_ASSERTIONS[:3]
            )
        )
        canonical_assertion_expressions.extend(
            (
                "tuple(item.category_id for item in report.category_results) == "
                f"{POST_E6_CONFORMANCE_GEOMETRY_ASSERTIONS[3][1]!r}",
                "tuple((item.category_id, item.required_check_ids) for item in "
                "report.category_results) == "
                f"{POST_E6_CONFORMANCE_GEOMETRY_ASSERTIONS[4][1]!r}",
                "tuple(item.probe_id for item in report.negative_test_results) == "
                f"{POST_E6_CONFORMANCE_GEOMETRY_ASSERTIONS[5][1]!r}",
                f"{access('active_gauntlet_refs')} == "
                f"{POST_E6_CONFORMANCE_GEOMETRY_ASSERTIONS[6][1]!r}",
                "tuple(item.domain_id for item in report.domain_results) == "
                f"{POST_E6_CONFORMANCE_GEOMETRY_ASSERTIONS[7][1]!r}",
            )
        )
    module_literal_values = _module_literal_values_v03(tree)

    class ModuleLiteralNormalizer(ast.NodeTransformer):
        def visit_Name(self, node: ast.Name) -> ast.AST:
            if (
                isinstance(node.ctx, ast.Load)
                and node.id in module_literal_values
            ):
                replacement = ast.parse(
                    repr(module_literal_values[node.id]),
                    mode="eval",
                ).body
                return ast.copy_location(replacement, node)
            return node

    def semantic_assertion_dump(statement: ast.stmt) -> str:
        normalized = ast.parse(ast.unparse(statement)).body[0]
        normalized = ModuleLiteralNormalizer().visit(normalized)
        return ast.dump(
            normalized,
            annotate_fields=True,
            include_attributes=False,
        )

    canonical_assertions = tuple(
        semantic_assertion_dump(statement)
        for statement in ast.parse(
            "\n".join(
                f"assert {expression}"
                for expression in canonical_assertion_expressions
            )
            + "\n"
        ).body
    )
    actual_assertions = tuple(map(semantic_assertion_dump, assertions))
    if actual_assertions != canonical_assertions:
        failures.add(f"{prefix}.semantic_normal_form:assertion_tail")

    def exact_assign_call(
        statement: ast.stmt,
        *,
        target: str,
        called: frozenset[str],
        argument: str | None,
    ) -> bool:
        if not (
            isinstance(statement, ast.Assign)
            and len(statement.targets) == 1
            and isinstance(statement.targets[0], ast.Name)
            and statement.targets[0].id == target
            and isinstance(statement.value, ast.Call)
            and not statement.value.keywords
        ):
            return False
        resolved = _resolved_call_target_v02(statement.value.func, import_targets)
        if resolved not in called:
            return False
        if argument is None:
            return not statement.value.args
        return (
            len(statement.value.args) == 1
            and isinstance(statement.value.args[0], ast.Name)
            and statement.value.args[0].id == argument
        )

    direct = (
        len(setup) == 2
        and exact_assign_call(
            setup[0],
            target="report",
            called=frozenset({qualified_collector}),
            argument=None,
        )
        and exact_assign_call(
            setup[1],
            target="validation",
            called=frozenset({qualified_validator}),
            argument="report",
        )
    )
    spy = False
    if (
        len(setup) == 4
        and isinstance(setup[0], ast.Assign)
        and len(setup[0].targets) == 1
        and isinstance(setup[0].targets[0], ast.Name)
        and setup[0].targets[0].id == "calls"
        and isinstance(setup[0].value, ast.List)
        and not setup[0].value.elts
        and isinstance(setup[1], ast.FunctionDef)
        and setup[1].name == "counted_collector"
    ):
        counted = setup[1]
        counted_args = counted.args
        exact_signature = (
            not counted.decorator_list
            and not counted_args.posonlyargs
            and not counted_args.args
            and not counted_args.kwonlyargs
            and counted_args.vararg is not None
            and counted_args.vararg.arg == "args"
            and counted_args.vararg.annotation is None
            and counted_args.kwarg is not None
            and counted_args.kwarg.arg == "kwargs"
            and counted_args.kwarg.annotation is None
            and not counted_args.defaults
            and not any(item is not None for item in counted_args.kw_defaults)
            and counted.returns is None
            and counted.type_comment is None
        )
        exact_body = False
        if len(counted.body) == 3:
            first, second, third = counted.body
            exact_body = (
                isinstance(first, ast.Assign)
                and len(first.targets) == 1
                and isinstance(first.targets[0], ast.Name)
                and first.targets[0].id == "exact_return"
                and isinstance(first.value, ast.Call)
                and _resolved_call_target_v02(first.value.func, import_targets)
                == qualified_collector
                and len(first.value.args) == 1
                and isinstance(first.value.args[0], ast.Starred)
                and isinstance(first.value.args[0].value, ast.Name)
                and first.value.args[0].value.id == "args"
                and len(first.value.keywords) == 1
                and first.value.keywords[0].arg is None
                and isinstance(first.value.keywords[0].value, ast.Name)
                and first.value.keywords[0].value.id == "kwargs"
                and isinstance(second, ast.Expr)
                and isinstance(second.value, ast.Call)
                and isinstance(second.value.func, ast.Attribute)
                and isinstance(second.value.func.value, ast.Name)
                and second.value.func.value.id == "calls"
                and second.value.func.attr == "append"
                and len(second.value.args) == 1
                and isinstance(second.value.args[0], ast.Name)
                and second.value.args[0].id == "exact_return"
                and not second.value.keywords
                and isinstance(third, ast.Return)
                and isinstance(third.value, ast.Name)
                and third.value.id == "exact_return"
            )
        spy = (
            exact_signature
            and exact_body
            and exact_assign_call(
                setup[2],
                target="report",
                called=frozenset({"counted_collector"}),
                argument=None,
            )
            and exact_assign_call(
                setup[3],
                target="validation",
                called=frozenset({qualified_validator}),
                argument="report",
            )
        )
    if not direct and not spy:
        failures.add(f"{prefix}.semantic_normal_form:setup")
    return tuple(sorted(failures))


def _validate_post_e6_test_contract_v02(
    path: Path,
    *,
    living: bool,
) -> tuple[str, ...]:
    label = "living" if living else "conformance"
    try:
        source = path.read_text(encoding="utf-8")
        tree = ast.parse(source, filename=str(path))
    except (OSError, UnicodeError, SyntaxError) as exc:
        return (f"e6.phase.post.test_contract.{label}.parse:{type(exc).__name__}",)

    function_name = (
        POST_E6_LIVING_ACCEPTANCE_TEST
        if living
        else POST_E6_CONFORMANCE_ACCEPTANCE_TEST
    )
    collector_name = (
        "collect_living_gauntlet_v01"
        if living
        else "collect_kernel_conformance_v01"
    )
    validator_name = (
        "validate_living_gauntlet_report_v01"
        if living
        else "validate_kernel_conformance_runtime_v01"
    )
    public_module = (
        "demo.run_living_gauntlet_v01"
        if living
        else "demo.run_kernel_conformance_v01"
    )
    qualified_collector = f"{public_module}.{collector_name}"
    qualified_validator = f"{public_module}.{validator_name}"
    import_targets = _module_import_targets_v02(tree)
    matches = [
        node
        for node in tree.body
        if isinstance(node, ast.FunctionDef) and node.name == function_name
    ]
    failures: list[str] = []
    prefix = f"e6.phase.post.test_contract.{label}"
    if len(matches) != 1:
        return (f"{prefix}.function_count",)
    function = matches[0]
    failures.extend(
        _post_e6_semantic_normal_form_failures_v05(
            tree,
            function,
            label=label,
            public_module=public_module,
            qualified_collector=qualified_collector,
            qualified_validator=qualified_validator,
            import_targets=import_targets,
        )
    )
    failures.extend(
        _post_e6_public_binding_use_failures_v05(
            tree,
            function,
            label=label,
            public_module=public_module,
            qualified_collector=qualified_collector,
            qualified_validator=qualified_validator,
            import_targets=import_targets,
        )
    )
    failures.extend(
        _post_e6_dynamic_capability_failures_v05(tree, label=label)
    )
    public_binding_names = frozenset(
        {
            collector_name,
            validator_name,
            *(
                binding
                for binding, target in import_targets.items()
                if target in {
                    qualified_collector,
                    qualified_validator,
                }
            ),
        }
    )
    failures.extend(
        _dynamic_namespace_failures_v05(
            tree,
            label=f"{prefix}.dynamic_namespace_authority",
            protected_names=public_binding_names,
        )
    )
    failures.extend(
        _dynamic_namespace_failures_v05(
            tree,
            label=f"{prefix}.assertion_builtin_namespace",
            protected_names=frozenset({"len", "set", "tuple"}),
        )
    )
    failures.extend(
        _module_capability_failures_v05(
            tree,
            label=f"{prefix}.public_module_authority",
            module_name=public_module,
            protected_attributes=frozenset(
                {collector_name, validator_name}
            ),
        )
    )
    failures.extend(
        _module_capability_failures_v05(
            tree,
            label=f"{prefix}.assertion_builtin_authority",
            module_name="builtins",
            protected_attributes=frozenset({"len", "set", "tuple"}),
        )
    )
    if function.decorator_list:
        failures.append(f"{prefix}.decorated")
    forbidden_pytest_calls = {
        (_dotted_ast_name(node.func) or "").split(".")[-1]
        for node in ast.walk(tree)
        if isinstance(node, ast.Call)
        and (_dotted_ast_name(node.func) or "").split(".")[-1]
        in {"skip", "skipif", "xfail", "importorskip"}
    }
    forbidden_pytest_marks = {
        _dotted_ast_name(node)
        for node in ast.walk(tree)
        if isinstance(node, ast.Attribute)
        and (_dotted_ast_name(node) or "").split(".")[-1]
        in {"skip", "skipif", "xfail"}
    }
    if forbidden_pytest_calls or forbidden_pytest_marks:
        failures.append(f"{prefix}.skip_or_xfail")
    if any(
        isinstance(node, (ast.Import, ast.ImportFrom))
        and any(
            alias.name == "tests" or alias.name.startswith("tests.")
            for alias in node.names
        )
        for node in ast.walk(tree)
    ):
        failures.append(f"{prefix}.test_import")

    unreachable = False
    reachable: list[ast.stmt] = []
    for statement in function.body:
        if unreachable:
            failures.append(f"{prefix}.unreachable_evidence")
            break
        reachable.append(statement)
        if isinstance(statement, (ast.Return, ast.Raise)):
            unreachable = True
    if any(
        isinstance(statement, (ast.Pass, ast.If, ast.For, ast.While, ast.Try, ast.With, ast.Match))
        for statement in reachable
    ):
        failures.append(f"{prefix}.dead_or_controlled_evidence")

    forbidden_names = {
        name
        for node in ast.walk(function)
        for name in (
            [node.id] if isinstance(node, ast.Name) else
            [node.attr] if isinstance(node, ast.Attribute) else []
        )
        if any(marker in name.casefold() for marker in ("mock", "patch", "monkeypatch"))
    }
    if forbidden_names:
        failures.append(f"{prefix}.substituted_surface")

    public_names = frozenset({collector_name, validator_name})
    exact_imported_names = frozenset(
        name
        for name, target in import_targets.items()
        if target in {qualified_collector, qualified_validator, public_module}
    )
    module_aliases = frozenset(
        name for name, target in import_targets.items() if target == public_module
    )
    protected_bindings = public_names | exact_imported_names
    permitted_public_imports = {
        name: target
        for name, target in import_targets.items()
        if target in {qualified_collector, qualified_validator, public_module}
    }
    import_counts = _module_import_binding_counts_v03(tree)
    if any(import_counts.get(name, 0) != 1 for name in exact_imported_names):
        failures.append(f"{prefix}.public_import_binding_count")
    if _module_shadow_events_v03(
        tree,
        protected=protected_bindings,
        module_aliases=module_aliases,
        permitted_import_targets=import_targets,
    ):
        failures.append(f"{prefix}.public_surface_shadowed")
    if _binding_events_v04(
        tree,
        protected_bindings,
        permitted_module_imports=permitted_public_imports,
    ):
        failures.append(f"{prefix}.public_surface_shadowed")
    if _public_module_provenance_failures_v04(
        tree,
        module_aliases=module_aliases,
        collector_name=collector_name,
        validator_name=validator_name,
    ):
        failures.append(f"{prefix}.public_surface_provenance")
    proof_operators = frozenset({"len", "set", "tuple"})
    if (
        proof_operators & _module_level_bound_names_v05(tree)
        or _binding_events_v04(function, proof_operators)
    ):
        failures.append(f"{prefix}.assertion_operator_shadowed")
    if _lexical_shadow_events_v03(
        function,
        protected=protected_bindings,
        module_aliases=module_aliases,
    ):
        failures.append(f"{prefix}.public_surface_shadowed")
    if any(
        _lexical_shadow_events_v03(
            nested,
            protected=protected_bindings,
            module_aliases=module_aliases,
        )
        for nested in function.body
        if isinstance(nested, (ast.FunctionDef, ast.AsyncFunctionDef))
    ):
        failures.append(f"{prefix}.public_surface_shadowed")

    transparent_spies = _transparent_collector_spies_v02(
        function,
        qualified_collector,
        import_targets,
        protected_bindings,
        module_aliases,
    )
    if any(
        _lexical_shadow_events_v03(
            function,
            protected=frozenset({spy}),
            module_aliases=module_aliases,
        )
        != (f"{spy}:FunctionDef",)
        for spy in transparent_spies
    ):
        failures.append(f"{prefix}.public_surface_shadowed")
    report_name: str | None = None
    collector_statement: ast.Assign | None = None
    collector_index = -1
    for index, statement in enumerate(reachable):
        if not (
            isinstance(statement, ast.Assign)
            and len(statement.targets) == 1
            and isinstance(statement.targets[0], ast.Name)
            and isinstance(statement.value, ast.Call)
        ):
            continue
        called = _resolved_call_target_v02(statement.value.func, import_targets)
        if called == qualified_collector or called in transparent_spies:
            if report_name is not None:
                failures.append(f"{prefix}.collector_count")
                continue
            report_name = statement.targets[0].id
            collector_statement = statement
            collector_index = index
    if report_name is None:
        failures.append(f"{prefix}.collector_missing")

    validation_name: str | None = None
    validator_statement: ast.Assign | None = None
    validator_index = -1
    for index, statement in enumerate(reachable):
        call: ast.Call | None = None
        target_name: str | None = None
        if (
            isinstance(statement, ast.Assign)
            and len(statement.targets) == 1
            and isinstance(statement.targets[0], ast.Name)
            and isinstance(statement.value, ast.Call)
        ):
            call = statement.value
            target_name = statement.targets[0].id
        if call is None:
            continue
        called = _resolved_call_target_v02(call.func, import_targets)
        if called != qualified_validator:
            continue
        if (
            report_name is None
            or len(call.args) != 1
            or not isinstance(call.args[0], ast.Name)
            or call.args[0].id != report_name
        ):
            failures.append(f"{prefix}.validator_dataflow")
            continue
        if validation_name is not None:
            failures.append(f"{prefix}.validator_count")
            continue
        validation_name = target_name
        validator_statement = statement
        validator_index = index
    if validation_name is None:
        failures.append(f"{prefix}.validator_missing")
    if validator_index <= collector_index:
        failures.append(f"{prefix}.call_order")
    resolved_calls = tuple(
        _resolved_call_target_v02(node.func, import_targets)
        for node in ast.walk(function)
        if isinstance(node, ast.Call)
    )
    if resolved_calls.count(qualified_collector) != 1:
        failures.append(f"{prefix}.collector_occurrence_count")
    if resolved_calls.count(qualified_validator) != 1:
        failures.append(f"{prefix}.validator_occurrence_count")
    if any(
        target is not None
        and (
            target.endswith(".collect_continuous_delta_runtime_g2_e_v01")
            or target.endswith(".run_continuous_delta_runtime_v01")
            or (
                ("g2_d" in target or "fractal_runtime" in target)
                and any(part.startswith("_") for part in target.split("."))
            )
        )
        for target in resolved_calls
    ):
        failures.append(f"{prefix}.forbidden_runtime_substitution")
    if _actual_return_lineage_failures_v03(
        function,
        tree=tree,
        report_name=report_name,
        validation_name=validation_name,
        collector_statement=collector_statement,
        validator_statement=validator_statement,
        qualified_validator=qualified_validator,
        import_targets=import_targets,
    ):
        failures.append(f"{prefix}.actual_return_lineage")

    assertions = [
        statement
        for statement in reachable
        if isinstance(statement, ast.Assert)
    ]
    if any(
        not (
            isinstance(assertion.test, ast.Compare)
            and len(assertion.test.ops) == 1
            and len(assertion.test.comparators) == 1
        )
        for assertion in assertions
    ):
        failures.append(f"{prefix}.nonflat_assertion")
    if any(
        isinstance(assertion.test, ast.Constant) and bool(assertion.test.value)
        for assertion in assertions
    ):
        failures.append(f"{prefix}.constant_assertion")
    if any(
        _tautological_assertion_v03(
            assertion,
            report_name=report_name,
            validation_name=validation_name,
        )
        for assertion in assertions
    ):
        failures.append(f"{prefix}.tautological_assertion")
    comparisons = _assertion_comparisons_v03(assertions)
    module_values = _module_literal_values_v03(tree)
    if validation_name is None or not _has_exact_validation_success_v03(
        comparisons, validation_name
    ):
        failures.append(f"{prefix}.validation_success_contract")
    if report_name is None:
        failures.append(f"{prefix}.actual_return_assertion_missing")
    else:
        for field, expected in POST_E6_SHARED_FIXED_REPORT_VALUES:
            if not _has_report_expected_comparison_v03(
                comparisons,
                report_name=report_name,
                field=field,
                expected=expected,
                module_values=module_values,
                direct=True,
            ):
                failures.append(f"{prefix}.shared_field_contract:{field}")
        hash_first, hash_second = POST_E6_SHARED_SHA256_FIELDS
        if not _has_distinct_report_field_relation_v03(
            comparisons,
            report_name=report_name,
            first_field=hash_first,
            second_field=hash_second,
        ):
            failures.append(f"{prefix}.shared_hash_relation")
        for field in POST_E6_SHARED_SHA256_FIELDS:
            if not _has_length_check_v03(
                comparisons,
                report_name=report_name,
                field=field,
                expected_length=64,
            ) or not _has_hex_alphabet_check_v03(
                comparisons,
                report_name=report_name,
                field=field,
            ):
                failures.append(f"{prefix}.shared_hash_format:{field}")
        bytes_first, bytes_second = POST_E6_SHARED_BYTE_COUNT_FIELDS
        if not _has_distinct_report_field_relation_v03(
            comparisons,
            report_name=report_name,
            first_field=bytes_first,
            second_field=bytes_second,
        ):
            failures.append(f"{prefix}.shared_byte_relation")
        for field in POST_E6_SHARED_BYTE_COUNT_FIELDS:
            if not _has_positive_field_check_v03(
                comparisons,
                report_name=report_name,
                field=field,
            ):
                failures.append(f"{prefix}.shared_byte_positive:{field}")
        geometry = (
            POST_E6_LIVING_GEOMETRY_ASSERTIONS
            if living
            else POST_E6_CONFORMANCE_GEOMETRY_ASSERTIONS
        )
        for field, expected in geometry:
            if not _has_geometry_comparison_v03(
                comparisons,
                report_name=report_name,
                field=field,
                expected=expected,
                module_values=module_values,
                living=living,
            ):
                failures.append(
                    f"{prefix}.geometry_field_contract:{field}:"
                    f"{_repr_sha256(expected)}"
                )

    if not (
        any(target == qualified_collector for target in import_targets.values())
        or any(target == public_module for target in import_targets.values())
    ):
        failures.append(f"{prefix}.collector_import")
    if not (
        any(target == qualified_validator for target in import_targets.values())
        or any(target == public_module for target in import_targets.values())
    ):
        failures.append(f"{prefix}.validator_import")
    return tuple(sorted(set(failures)))


def _post_e6_test_contract_present(path: Path, *, living: bool) -> bool:
    return not _validate_post_e6_test_contract_v02(path, living=living)


def _historical_module_bindings_v03(label: str) -> frozenset[str]:
    return frozenset(
        context.removeprefix("binding:")
        for surface, enclosing, context in HISTORICAL_EVIDENCE_STRUCTURAL_ALLOWLIST_V03
        if surface == label
        and enclosing == "module"
        and context.startswith("binding:")
    )


def _dict_value_for_key_v03(mapping: ast.Dict, key: str) -> ast.AST | None:
    for key_node, value_node in zip(mapping.keys, mapping.values, strict=True):
        if isinstance(key_node, ast.Constant) and key_node.value == key:
            return value_node
    return None


def _historical_allowed_node_ids_v03(
    tree: ast.Module,
    label: str,
) -> frozenset[int]:
    allowed: set[int] = set()
    module_bindings = _historical_module_bindings_v03(label)
    for statement in tree.body:
        value: ast.AST | None = None
        name: str | None = None
        if (
            isinstance(statement, ast.Assign)
            and len(statement.targets) == 1
            and isinstance(statement.targets[0], ast.Name)
        ):
            name = statement.targets[0].id
            value = statement.value
        elif (
            isinstance(statement, ast.AnnAssign)
            and isinstance(statement.target, ast.Name)
            and statement.value is not None
        ):
            name = statement.target.id
            value = statement.value
        if name in module_bindings and value is not None:
            allowed.update(
                id(node)
                for node in ast.walk(value)
                if isinstance(node, ast.Constant)
                and node.value
                in {
                    _HISTORICAL_ACT_ID,
                    _HISTORICAL_RUNNER_MODULE,
                    _HISTORICAL_RUNNER_SYMBOL,
                }
            )

    functions = {
        node.name: node
        for node in tree.body
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef))
    }
    if label == "kernel_conformance":
        function = functions.get("kernel_conformance_profile_metadata_v01")
        if function is not None:
            for returned in (
                node.value
                for node in ast.walk(function)
                if isinstance(node, ast.Return) and isinstance(node.value, ast.Dict)
            ):
                profile = _dict_value_for_key_v03(returned, "profile_id")
                historical = _dict_value_for_key_v03(
                    returned, "historical_act_id"
                )
                if (
                    isinstance(profile, ast.Name)
                    and profile.id == "KERNEL_CONFORMANCE_PROFILE_V05_HISTORICAL"
                    and isinstance(historical, ast.Constant)
                    and historical.value == _HISTORICAL_ACT_ID
                ):
                    allowed.update(id(node) for node in ast.walk(historical))
    elif label == "living_gauntlet":
        function = functions.get("_validate_completion_manifest_v01")
        if function is not None:
            for assignment in (
                node
                for node in ast.walk(function)
                if isinstance(node, ast.Assign)
                and len(node.targets) == 1
                and isinstance(node.targets[0], ast.Name)
                and node.targets[0].id == "expected_profiles"
                and isinstance(node.value, ast.Dict)
            ):
                historical_profile = _dict_value_for_key_v03(
                    assignment.value, "historical_v0_5"
                )
                if isinstance(historical_profile, ast.Dict):
                    historical = _dict_value_for_key_v03(
                        historical_profile, "historical_act_id"
                    )
                    if (
                        isinstance(historical, ast.Constant)
                        and historical.value == _HISTORICAL_ACT_ID
                    ):
                        allowed.update(id(node) for node in ast.walk(historical))
    return frozenset(allowed)


def _historical_alias_expression_v03(node: ast.AST, aliases: set[str]) -> bool:
    return _expression_uses_names_v03(node, aliases)


def _historical_current_binding_v03(
    target: ast.AST,
    *,
    allowed_historical_bindings: frozenset[str],
) -> bool:
    names = set(_bound_name_ids(target))
    root = _target_root_name_v03(target)
    if root is not None:
        names.add(root)
    critical = (
        CORE_PHASE_CRITICAL_NAMES
        | RUNNER_PHASE_CRITICAL_NAMES
        | LIVING_PHASE_CRITICAL_NAMES
    )
    for name in names:
        if name in allowed_historical_bindings:
            continue
        folded = name.casefold()
        if name in critical:
            return True
        if any(marker in folded for marker in ("dispatch", "registry")):
            return True
        if any(marker in folded for marker in ("source", "seam", "profile", "runner")) and not folded.startswith(
            ("expected_", "historical_", "evidence_", "module_", "symbol_")
        ):
            return True
    return False


def _historical_scope_escape_failures_v05(
    tree: ast.Module,
    *,
    label: str,
    historical_bindings: frozenset[str],
) -> tuple[str, ...]:
    raw_aliases = set(_identity_aliases_v05(tree, historical_bindings))
    failures: set[str] = set()
    class_node_ids = {
        id(child)
        for class_node in ast.walk(tree)
        if isinstance(class_node, ast.ClassDef)
        for statement in class_node.body
        for child in ast.walk(statement)
    }
    for node in ast.walk(tree):
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef, ast.Lambda, ast.ClassDef)):
            if any(
                _expression_uses_names_v03(expression, raw_aliases)
                for expression in _definition_time_expressions_v05(node)
            ):
                failures.add(
                    f"e6.phase.historical.{label}.tainted_scope_definition"
                )
        if isinstance(node, ast.Lambda) and _identity_preserving_root_expression_v05(
            node.body, raw_aliases
        ):
            failures.add(
                f"e6.phase.historical.{label}.tainted_scope_return"
            )
        if isinstance(node, (ast.Return, ast.Yield, ast.YieldFrom)):
            if node.value is not None and _identity_preserving_root_expression_v05(
                node.value, raw_aliases
            ):
                failures.add(
                    f"e6.phase.historical.{label}.tainted_scope_return"
                )
        if isinstance(
            node,
            (ast.GeneratorExp, ast.ListComp, ast.SetComp, ast.DictComp),
        ) and _expression_uses_names_v03(node, raw_aliases):
            failures.add(
                f"e6.phase.historical.{label}.tainted_scope_container"
            )
        targets: tuple[ast.AST, ...] = ()
        value: ast.AST | None = None
        if isinstance(node, ast.Assign):
            targets = tuple(node.targets)
            value = node.value
        elif isinstance(node, ast.AnnAssign) and node.value is not None:
            targets = (node.target,)
            value = node.value
        elif isinstance(node, ast.NamedExpr):
            targets = (node.target,)
            value = node.value
        if value is None or not _identity_preserving_root_expression_v05(
            value, raw_aliases
        ):
            continue
        if id(node) in class_node_ids:
            failures.add(
                f"e6.phase.historical.{label}.tainted_scope_class_storage"
            )
        if any(
            isinstance(target, (ast.Attribute, ast.Subscript))
            for target in targets
        ):
            failures.add(
                f"e6.phase.historical.{label}.tainted_scope_storage"
            )
    return tuple(sorted(failures))


def _historical_taint_failures_v03(
    tree: ast.Module,
    *,
    label: str,
) -> tuple[str, ...]:
    historical_bindings = _historical_module_bindings_v03(label)
    failures: set[str] = set()
    failures.update(
        _historical_scope_escape_failures_v05(
            tree,
            label=label,
            historical_bindings=historical_bindings,
        )
    )
    failures.update(
        _module_capability_failures_v05(
            tree,
            label=f"e6.phase.historical.{label}.json_authority",
            module_name="json",
            protected_attributes=frozenset({"dumps", "loads"}),
        )
    )
    function_groups: dict[str, list[ast.FunctionDef | ast.AsyncFunctionDef]] = {}
    for node in ast.walk(tree):
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
            function_groups.setdefault(node.name, []).append(node)
    local_functions = {
        name: rows[0]
        for name, rows in function_groups.items()
        if len(rows) == 1
    }
    active_local_calls: set[tuple[int, tuple[str, ...]]] = set()
    safe_builtins = frozenset(
        {
        "all",
        "any",
        "bool",
        "dict",
        "enumerate",
        "frozenset",
        "isinstance",
        "iter",
        "len",
        "list",
        "print",
        "repr",
        "set",
        "sorted",
        "str",
        "sum",
        "tuple",
        "zip",
        }
    )
    lexical_chains = _lexical_scope_chains_v05(tree)
    historical_import_targets = _module_import_targets_v02(tree)
    safe_methods = {
        "copy",
        "get",
        "isdisjoint",
        "issubset",
        "issuperset",
        "items",
        "keys",
        "values",
    }

    def analyze_scope(
        statements: Sequence[ast.stmt],
        inherited_aliases: set[str],
    ) -> None:
        nodes = _scope_nodes_v03(statements)
        aliases = set(inherited_aliases)
        binding_counts: dict[str, int] = {}
        fresh_candidates: set[str] = set()
        for node in nodes:
            targets: tuple[ast.AST, ...] = ()
            if isinstance(node, ast.Assign):
                targets = tuple(node.targets)
                if (
                    len(node.targets) == 1
                    and isinstance(node.targets[0], ast.Name)
                    and isinstance(node.value, (ast.List, ast.Dict, ast.Set))
                    and (
                        (isinstance(node.value, (ast.List, ast.Set)) and not node.value.elts)
                        or (isinstance(node.value, ast.Dict) and not node.value.keys)
                    )
                ):
                    fresh_candidates.add(node.targets[0].id)
            elif isinstance(node, ast.AnnAssign):
                targets = (node.target,)
                if (
                    isinstance(node.target, ast.Name)
                    and isinstance(node.value, (ast.List, ast.Dict, ast.Set))
                    and (
                        (isinstance(node.value, (ast.List, ast.Set)) and not node.value.elts)
                        or (isinstance(node.value, ast.Dict) and not node.value.keys)
                    )
                ):
                    fresh_candidates.add(node.target.id)
            elif isinstance(node, (ast.AugAssign, ast.NamedExpr)):
                targets = (node.target,)
            elif isinstance(node, (ast.For, ast.AsyncFor, ast.comprehension)):
                targets = (node.target,)
            elif isinstance(node, (ast.With, ast.AsyncWith)):
                targets = tuple(
                    item.optional_vars
                    for item in node.items
                    if item.optional_vars is not None
                )
            elif isinstance(node, ast.Delete):
                targets = tuple(node.targets)
            for target in targets:
                for name in _bound_name_ids(target):
                    binding_counts[name] = binding_counts.get(name, 0) + 1
        fresh_containers = {
            name
            for name in fresh_candidates
            if binding_counts.get(name) == 1 and name not in aliases
        }
        string_containers = {
            node.target.id
            for node in nodes
            if isinstance(node, ast.AnnAssign)
            and isinstance(node.target, ast.Name)
            and node.target.id in fresh_containers
            and isinstance(node.annotation, ast.Subscript)
            and isinstance(node.annotation.value, ast.Name)
            and node.annotation.value.id == "list"
            and isinstance(node.annotation.slice, ast.Name)
            and node.annotation.slice.id == "str"
        }
        safe_string_receivers = {
            name
            for node in nodes
            if isinstance(node, (ast.For, ast.AsyncFor, ast.comprehension))
            and isinstance(node.iter, ast.Name)
            and node.iter.id in string_containers
            for name in _bound_name_ids(node.target)
        }
        changed = True
        while changed:
            changed = False
            for node in nodes:
                targets: tuple[ast.AST, ...] = ()
                value: ast.AST | None = None
                if isinstance(node, ast.Assign):
                    targets = tuple(node.targets)
                    value = node.value
                elif isinstance(node, ast.AnnAssign) and node.value is not None:
                    targets = (node.target,)
                    value = node.value
                elif isinstance(node, ast.NamedExpr):
                    targets = (node.target,)
                    value = node.value
                elif isinstance(node, (ast.For, ast.AsyncFor)):
                    targets = (node.target,)
                    value = node.iter
                elif isinstance(node, ast.comprehension):
                    targets = (node.target,)
                    value = node.iter
                if value is None or not _historical_alias_expression_v03(
                    value, aliases
                ):
                    continue
                for target in targets:
                    before = len(aliases)
                    aliases.update(_bound_name_ids(target))
                    changed = changed or len(aliases) != before
            for node in nodes:
                if not (
                    isinstance(node, ast.Call)
                    and isinstance(node.func, ast.Attribute)
                    and isinstance(node.func.value, ast.Name)
                    and node.func.value.id in fresh_containers
                    and node.func.attr in {"append", "extend"}
                    and any(
                        _expression_uses_names_v03(argument, aliases)
                        for argument in node.args
                    )
                ):
                    continue
                before = len(aliases)
                aliases.add(node.func.value.id)
                changed = changed or len(aliases) != before

        for node in nodes:
            if isinstance(node, (ast.Assign, ast.AnnAssign, ast.NamedExpr)):
                targets = (
                    tuple(node.targets)
                    if isinstance(node, ast.Assign)
                    else (node.target,)
                )
                value = node.value
                if value is not None and _historical_alias_expression_v03(
                    value, aliases
                ):
                    for target in targets:
                        if _historical_current_binding_v03(
                            target,
                            allowed_historical_bindings=historical_bindings,
                        ):
                            failures.add(
                                f"e6.phase.historical.{label}."
                                "tainted_current_binding"
                            )
            if not isinstance(node, ast.Call):
                continue
            called = _dotted_ast_name(node.func) or ""
            leaf = called.split(".")[-1]
            tainted_func = _expression_uses_names_v03(node.func, aliases)
            tainted_args = any(
                _expression_uses_names_v03(argument, aliases)
                for argument in node.args
            ) or any(
                _expression_uses_names_v03(keyword.value, aliases)
                for keyword in node.keywords
            )
            tainted_receiver = (
                isinstance(node.func, ast.Attribute)
                and _expression_uses_names_v03(node.func.value, aliases)
            )
            inert_container_call = (
                isinstance(node.func, ast.Attribute)
                and isinstance(node.func.value, ast.Name)
                and node.func.value.id in fresh_containers
                and node.func.attr in {"append", "extend"}
            )
            inert_string_call = (
                isinstance(node.func, ast.Attribute)
                and isinstance(node.func.value, ast.Name)
                and node.func.value.id in safe_string_receivers
                and node.func.attr in {"endswith", "startswith"}
            )
            if leaf in {"import_module", "__import__"} and tainted_args:
                failures.add(f"e6.phase.historical.{label}.tainted_import")
            if leaf == "getattr" and tainted_args:
                failures.add(f"e6.phase.historical.{label}.tainted_getattr")
            if tainted_func and not tainted_receiver:
                failures.add(
                    f"e6.phase.historical.{label}.tainted_callable:"
                    f"{called or leaf}"
                )
            if (
                tainted_args
                and isinstance(node.func, ast.Attribute)
                and _historical_current_binding_v03(
                    node.func.value,
                    allowed_historical_bindings=historical_bindings,
                )
            ):
                failures.add(
                    f"e6.phase.historical.{label}.tainted_current_binding"
                )
            local_function = local_functions.get(leaf)
            if tainted_args and local_function is not None:
                if leaf in safe_builtins:
                    failures.add(
                        f"e6.phase.historical.{label}.tainted_escape"
                    )
                tainted_parameters = _tainted_call_parameters_v03(
                    node, local_function, aliases
                )
                token = (id(local_function), tuple(sorted(tainted_parameters)))
                if token not in active_local_calls:
                    active_local_calls.add(token)
                    analyze_scope(local_function.body, tainted_parameters)
                    active_local_calls.remove(token)
                continue
            if (
                tainted_receiver
                and leaf not in safe_methods
                and not inert_container_call
                and not inert_string_call
            ):
                failures.add(
                    f"e6.phase.historical.{label}.tainted_callable:"
                    f"{called or leaf}"
                )
            elif (
                tainted_args
                and not (
                    (
                        isinstance(node.func, ast.Name)
                        and node.func.id in safe_builtins
                        and _lexical_builtin_is_exact_v05(
                            lexical_chains, node, node.func.id
                        )
                    )
                    or (
                        isinstance(node.func, ast.Attribute)
                        and isinstance(node.func.value, ast.Name)
                        and (
                            (
                                node.func.value.id == "dict"
                                and node.func.attr == "fromkeys"
                                and _lexical_builtin_is_exact_v05(
                                    lexical_chains, node, "dict"
                                )
                            )
                            or (
                                historical_import_targets.get(
                                    node.func.value.id
                                )
                                == "json"
                                and node.func.attr in {"dumps", "loads"}
                                and _lexical_module_is_exact_v05(
                                    tree,
                                    lexical_chains,
                                    node,
                                    node.func.value.id,
                                    "json",
                                )
                            )
                        )
                    )
                )
                and leaf not in safe_methods
                and not inert_container_call
            ):
                failures.add(
                    f"e6.phase.historical.{label}.tainted_escape:"
                    f"{called or leaf}"
                )

        for node in nodes:
            if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
                parameters = _argument_binding_names_v03(node.args)
                analyze_scope(node.body, aliases - set(parameters))
            elif isinstance(node, ast.ClassDef):
                analyze_scope(node.body, aliases)
            elif isinstance(node, ast.Lambda):
                parameters = _argument_binding_names_v03(node.args)
                analyze_scope(
                    (ast.Expr(value=node.body),),
                    aliases - set(parameters),
                )

    analyze_scope(tree.body, set(historical_bindings))
    return tuple(sorted(failures))


def _validate_historical_non_rebinding_v02(
    tree: ast.Module | None,
    *,
    label: str,
    allowed_evidence_assignments: frozenset[str],
    failures: list[str],
) -> None:
    if tree is None:
        return
    expected_bindings = _historical_module_bindings_v03(label)
    if allowed_evidence_assignments != expected_bindings:
        failures.append(f"e6.phase.historical.{label}.allowlist_mismatch")
    allowed_nodes = _historical_allowed_node_ids_v03(tree, label)
    module_values: dict[str, object] = {}
    for statement in tree.body:
        name: str | None = None
        value: ast.AST | None = None
        if (
            isinstance(statement, ast.Assign)
            and len(statement.targets) == 1
            and isinstance(statement.targets[0], ast.Name)
        ):
            name = statement.targets[0].id
            value = statement.value
        elif (
            isinstance(statement, ast.AnnAssign)
            and isinstance(statement.target, ast.Name)
        ):
            name = statement.target.id
            value = statement.value
        if name is not None and value is not None:
            try:
                module_values[name] = _static_value(value, module_values)
            except StaticValueUnavailable:
                module_values.pop(name, None)
    for node in ast.walk(tree):
        try:
            static_node_value = _static_value(node, {})
        except StaticValueUnavailable:
            static_node_value = None
        if (
            isinstance(static_node_value, str)
            and static_node_value
            in {
                _HISTORICAL_ACT_ID,
                _HISTORICAL_RUNNER_MODULE,
                _HISTORICAL_RUNNER_SYMBOL,
            }
            and id(node) not in allowed_nodes
        ):
            failures.append(f"e6.phase.historical.{label}.static_rebound")
        if isinstance(node, ast.Constant) and node.value in {
            _HISTORICAL_ACT_ID,
            _HISTORICAL_RUNNER_MODULE,
            _HISTORICAL_RUNNER_SYMBOL,
        }:
            if id(node) not in allowed_nodes:
                failures.append(f"e6.phase.historical.{label}.literal_rebound")
        elif isinstance(node, ast.Import):
            if any(
                alias.name == _HISTORICAL_RUNNER_MODULE
                or alias.name.startswith(_HISTORICAL_RUNNER_MODULE + ".")
                for alias in node.names
            ):
                failures.append(f"e6.phase.historical.{label}.import_rebound")
        elif isinstance(node, ast.ImportFrom):
            module = node.module or ""
            if (
                module == _HISTORICAL_RUNNER_MODULE
                or module.startswith(_HISTORICAL_RUNNER_MODULE + ".")
                or any(
                    alias.name == _HISTORICAL_RUNNER_SYMBOL
                    or f"{module}.{alias.name}" == _HISTORICAL_RUNNER_MODULE
                    for alias in node.names
                )
            ):
                failures.append(f"e6.phase.historical.{label}.import_from_rebound")
        elif isinstance(node, ast.Name) and node.id == _HISTORICAL_RUNNER_SYMBOL:
            if id(node) not in allowed_nodes:
                failures.append(f"e6.phase.historical.{label}.symbol_rebound")
        elif isinstance(node, ast.Attribute) and node.attr == _HISTORICAL_RUNNER_SYMBOL:
            if id(node) not in allowed_nodes:
                failures.append(f"e6.phase.historical.{label}.attribute_rebound")
        elif isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef)):
            if node.name == _HISTORICAL_RUNNER_SYMBOL:
                failures.append(f"e6.phase.historical.{label}.local_rebound")
        if isinstance(node, ast.Call):
            called = (_dotted_ast_name(node.func) or "").split(".")[-1]
            if called in {"__import__", "import_module"} and node.args:
                try:
                    imported = _static_value(node.args[0], module_values)
                except StaticValueUnavailable:
                    imported = None
                if imported == _HISTORICAL_RUNNER_MODULE:
                    failures.append(
                        f"e6.phase.historical.{label}.dynamic_import_rebound"
                    )
    if any(
        isinstance(node, ast.Call)
        and (
            (_dotted_ast_name(node.func) or "").split(".")[-1]
            == _HISTORICAL_RUNNER_SYMBOL
        )
        for node in ast.walk(tree)
    ):
        failures.append(f"e6.phase.historical.{label}.call_rebound")
    failures.extend(_historical_taint_failures_v03(tree, label=label))


def _derive_e6_phase_state_v01(
    repo_root: Path,
    failures: list[str],
) -> tuple[dict[str, object], ast.Module | None, ast.Module | None, ast.Module | None, str, str, str]:
    core, core_nodes, core_tree, core_source = _phase_critical_assignments_v02(
        repo_root / CONFORMANCE_SOURCE_PATH,
        "e6.phase.kernel_conformance",
        CORE_PHASE_CRITICAL_NAMES,
        failures,
    )
    runner, runner_nodes, runner_tree, runner_source = _phase_critical_assignments_v02(
        repo_root / KERNEL_CONFORMANCE_RUNNER_PATH,
        "e6.phase.kernel_conformance_runner",
        RUNNER_PHASE_CRITICAL_NAMES,
        failures,
    )
    living, living_nodes, living_tree, living_source = _phase_critical_assignments_v02(
        repo_root / LIVING_GAUNTLET_PATH,
        "e6.phase.living_gauntlet",
        LIVING_PHASE_CRITICAL_NAMES,
        failures,
    )
    living_sources = living.get("_ACTIVE_ACT_SOURCES")
    living_act_ids = (
        tuple(living_sources) if isinstance(living_sources, dict) else None
    )
    living_evidence = living.get("_EVIDENCE_ONLY_ACT_IDS")
    historical_preserved = all(
        isinstance(value, tuple) and _HISTORICAL_ACT_ID in value
        for value in (
            core.get("_V05_HISTORICAL_ACTIVE_GAUNTLET_REFS"),
            runner.get("_V05_HISTORICAL_BASE_ACT_IDS"),
            living.get("HISTORICAL_KERNEL_CONFORMANCE_ACTIVE_REFS_V05"),
            living_evidence,
        )
    )
    current_collections = (
        core.get("_ACTIVE_GAUNTLET_REFS"),
        runner.get("_BASE_ACT_IDS"),
        living_act_ids,
        tuple(living.get("_CURRENT_SEAMS", {}))
        if isinstance(living.get("_CURRENT_SEAMS"), dict)
        else None,
        living.get("_EXECUTED_RUNTIME_ACT_IDS"),
        living.get("_EXECUTED_CONFORMANCE_ACT_IDS"),
    )
    historical_current = any(
        isinstance(value, tuple) and _HISTORICAL_ACT_ID in value
        for value in current_collections
    )

    test_identities = {
        path: _file_identity(repo_root / path)
        for path in (LIVING_GAUNTLET_TEST_PATH, KERNEL_CONFORMANCE_TEST_PATH)
    }
    if all(
        test_identities[path] == PRE_E6_CLASS_B_IDENTITIES[path]
        for path in test_identities
    ):
        focused_test_phase = "PRE_E6_RECONCILED"
    elif _post_e6_test_contract_present(
        repo_root / LIVING_GAUNTLET_TEST_PATH, living=True
    ) and _post_e6_test_contract_present(
        repo_root / KERNEL_CONFORMANCE_TEST_PATH, living=False
    ):
        focused_test_phase = "POST_E6_SUCCESSOR"
    else:
        focused_test_phase = "HYBRID_OR_INVALID"

    state = {
        "living_version": living.get("RUNNER_VERSION"),
        "living_act_ids": living_act_ids,
        "living_profile_v05": living.get(
            "KERNEL_CONFORMANCE_PROFILE_V05_HISTORICAL"
        ),
        "living_profile_v06_current": living.get(
            "KERNEL_CONFORMANCE_PROFILE_V06_CURRENT"
        ),
        "living_profile_v06_historical": living.get(
            "KERNEL_CONFORMANCE_PROFILE_V06_HISTORICAL"
        ),
        "living_profile_v07_current": living.get(
            "KERNEL_CONFORMANCE_PROFILE_V07_CURRENT"
        ),
        "living_default_profile_ref": _assignment_reference_name(
            living_tree, "DEFAULT_KERNEL_CONFORMANCE_PROFILE"
        ),
        "living_v05_refs": living.get(
            "HISTORICAL_KERNEL_CONFORMANCE_ACTIVE_REFS_V05"
        ),
        "living_v06_historical_refs": living.get(
            "HISTORICAL_KERNEL_CONFORMANCE_ACTIVE_REFS_V06"
        ),
        "living_current_refs": living.get(
            "CURRENT_KERNEL_CONFORMANCE_ACTIVE_REFS_V07",
            living.get("CURRENT_KERNEL_CONFORMANCE_ACTIVE_REFS_V06"),
        ),
        "core_version": core.get("CONFORMANCE_VERSION"),
        "core_profile_v05": core.get(
            "KERNEL_CONFORMANCE_PROFILE_V05_HISTORICAL"
        ),
        "core_profile_v06_current": core.get(
            "KERNEL_CONFORMANCE_PROFILE_V06_CURRENT"
        ),
        "core_profile_v06_historical": core.get(
            "KERNEL_CONFORMANCE_PROFILE_V06_HISTORICAL"
        ),
        "core_profile_v07_current": core.get(
            "KERNEL_CONFORMANCE_PROFILE_V07_CURRENT"
        ),
        "core_default_profile_ref": _assignment_reference_name(
            core_tree, "DEFAULT_KERNEL_CONFORMANCE_PROFILE"
        ),
        "core_v05_refs": core.get("_V05_HISTORICAL_ACTIVE_GAUNTLET_REFS"),
        "core_v06_historical_refs": core.get(
            "_V06_HISTORICAL_ACTIVE_GAUNTLET_REFS"
        ),
        "core_current_refs": core.get(
            "_V07_CURRENT_ACTIVE_GAUNTLET_REFS",
            core.get("_V06_CURRENT_ACTIVE_GAUNTLET_REFS"),
        ),
        "runner_version": runner.get("RUNNER_VERSION"),
        "runner_profile_v05": runner.get(
            "KERNEL_CONFORMANCE_PROFILE_V05_HISTORICAL"
        ),
        "runner_profile_v06_current": runner.get(
            "KERNEL_CONFORMANCE_PROFILE_V06_CURRENT"
        ),
        "runner_profile_v06_historical": runner.get(
            "KERNEL_CONFORMANCE_PROFILE_V06_HISTORICAL"
        ),
        "runner_profile_v07_current": runner.get(
            "KERNEL_CONFORMANCE_PROFILE_V07_CURRENT"
        ),
        "runner_default_profile_ref": _assignment_reference_name(
            runner_tree, "DEFAULT_KERNEL_CONFORMANCE_PROFILE"
        ),
        "runner_v05_refs": runner.get("_V05_HISTORICAL_BASE_ACT_IDS"),
        "runner_v06_historical_refs": runner.get(
            "_V06_HISTORICAL_BASE_ACT_IDS"
        ),
        "runner_current_refs": runner.get("_BASE_ACT_IDS"),
        "category_ids": core.get("CATEGORY_IDS"),
        "category_check_ids": core.get("_EXPECTED_CATEGORY_CHECK_IDS"),
        "negative_probe_ids": core.get("NEGATIVE_PROBE_IDS"),
        "domain_ids": core.get("DOMAIN_IDS"),
        "domain_geometry": core.get("_EXPECTED_DOMAIN_GEOMETRY"),
        "historical_all_layers_current": historical_current,
        "historical_v05_evidence_preserved": historical_preserved,
        "focused_test_phase": focused_test_phase,
    }
    version_tuple = (
        state.get("living_version"),
        state.get("core_version"),
        state.get("runner_version"),
    )
    binding_phase = (
        "PRE_E6_RECONCILED"
        if version_tuple == ("v1.5", "v0.6", "v0.6")
        else "POST_E6_SUCCESSOR"
        if version_tuple == ("v1.6", "v0.7", "v0.7")
        else None
    )
    _validate_phase_critical_bindings_v02(
        binding_phase,
        core,
        core_nodes,
        runner,
        runner_nodes,
        living,
        living_nodes,
        failures,
    )
    _validate_historical_non_rebinding_v02(
        core_tree,
        label="kernel_conformance",
        allowed_evidence_assignments=frozenset(
            {
                "_GATE1_ACTIVE_GAUNTLET_REFS_V01",
                "_G2A_ACTIVE_GAUNTLET_REFS_V02",
                "_G2B_ACTIVE_GAUNTLET_REFS_V03",
                "_G2C_ACTIVE_GAUNTLET_REFS_V04",
                "_V05_HISTORICAL_ACTIVE_GAUNTLET_REFS",
            }
        ),
        failures=failures,
    )
    _validate_historical_non_rebinding_v02(
        runner_tree,
        label="kernel_conformance_runner",
        allowed_evidence_assignments=frozenset(
            {"_V05_HISTORICAL_BASE_ACT_IDS"}
        ),
        failures=failures,
    )
    _validate_historical_non_rebinding_v02(
        living_tree,
        label="living_gauntlet",
        allowed_evidence_assignments=frozenset(
            {
                "HISTORICAL_KERNEL_CONFORMANCE_ACTIVE_REFS_V05",
                "_EVIDENCE_ONLY_ACT_IDS",
                "_HISTORICAL_EVIDENCE_ACT_IDS",
                "_HISTORICAL_SEAMS",
            }
        ),
        failures=failures,
    )
    return (
        state,
        core_tree,
        runner_tree,
        living_tree,
        core_source,
        runner_source,
        living_source,
    )


def _reads_historical_pass_material(tree: ast.Module | None) -> bool:
    if tree is None:
        return False
    historical_path_markers = (
        "docs/audit_reports/",
        "docs/evidence/",
        "_audit_exports/",
        ".log",
    )
    for node in ast.walk(tree):
        if not isinstance(node, ast.Call):
            continue
        call_name = ""
        if isinstance(node.func, ast.Name):
            call_name = node.func.id
        elif isinstance(node.func, ast.Attribute):
            call_name = node.func.attr
        if call_name not in {"open", "read_text", "read_bytes"}:
            continue
        literals = {
            child.value
            for child in ast.walk(node)
            if isinstance(child, ast.Constant) and isinstance(child.value, str)
        }
        if any(
            marker in literal
            for literal in literals
            for marker in historical_path_markers
        ):
            return True
    return False


def _validate_conformance_profiles(
    repo_root: Path,
    failures: list[str],
    *,
    closure_active: bool = False,
) -> None:
    (
        phase_state,
        phase_core_tree,
        phase_runner_tree,
        phase_living_tree,
        phase_core_source,
        phase_runner_source,
        phase_living_source,
    ) = _derive_e6_phase_state_v01(repo_root, failures)
    phase, phase_failures = _classify_e6_phase_v01(phase_state)
    failures.extend(phase_failures)
    if not closure_active:
        _validate_phase_path_ledger_v02(repo_root, phase, failures)
    elif phase != "POST_E6_SUCCESSOR":
        failures.append("g2e.closure.runtime_phase_not_post_e6_successor")
    pre_e6_versions = (
        phase_state.get("living_version"),
        phase_state.get("core_version"),
        phase_state.get("runner_version"),
    ) == ("v1.5", "v0.6", "v0.6")
    if phase == "PRE_E6_RECONCILED" or pre_e6_versions:
        _validate_exact_identities(
            repo_root,
            PRE_E6_CLASS_B_IDENTITIES,
            "e6.phase.pre.class_b",
            failures,
        )
    elif phase == "POST_E6_SUCCESSOR":
        _validate_exact_identities(
            repo_root,
            POST_E6_CLASS_B_IDENTITIES,
            "e6.phase.post.class_b",
            failures,
        )
        report_fields = set(
            _class_fields(phase_core_tree, "KernelConformanceReportV01")
        )
        for field in (
            "profile_id",
            "historical_profile_ref",
            "claim_to_current_act",
            "current_act_count",
            "active_gauntlet_refs",
        ):
            if field not in report_fields:
                failures.append(
                    f"e6.phase.post.kernel_conformance.report_field_missing:{field}"
                )
        living_fields = set(
            _class_fields(phase_living_tree, "LivingGauntletReportV01")
        )
        for field in (
            "kernel_conformance_profile",
            "historical_kernel_conformance_profile",
            "current_regression_claim_mapping",
        ):
            if field not in living_fields and field not in phase_living_source:
                failures.append(
                    f"e6.phase.post.living_gauntlet.report_field_missing:{field}"
                )
        for label, tree, source in (
            ("kernel_conformance", phase_core_tree, phase_core_source),
            ("kernel_conformance_runner", phase_runner_tree, phase_runner_source),
            ("living_gauntlet", phase_living_tree, phase_living_source),
        ):
            if label != "living_gauntlet" and (
                _HISTORICAL_RUNNER_MODULE in source
                or _HISTORICAL_RUNNER_SYMBOL in source
            ):
                failures.append(f"e6.phase.post.{label}.historical_runner_reference")
            if _reads_historical_pass_material(tree):
                failures.append(f"e6.phase.post.{label}.historical_pass_consumption")
        return
    else:
        return

    values, tree, source = _static_assignments(
        repo_root / CONFORMANCE_SOURCE_PATH,
        "s3.kernel_conformance",
        failures,
    )
    exact_values = {
        "KERNEL_CONFORMANCE_PROFILE_V05_HISTORICAL": HISTORICAL_PROFILE_ID,
        "KERNEL_CONFORMANCE_PROFILE_V06_CURRENT": CURRENT_PROFILE_ID,
        "DEFAULT_KERNEL_CONFORMANCE_PROFILE": CURRENT_PROFILE_ID,
        "CONFORMANCE_VERSION": "v0.6",
        "_V05_HISTORICAL_ACTIVE_GAUNTLET_REFS": HISTORICAL_V05_ACTIVE_REFS,
        "_V06_CURRENT_ACTIVE_GAUNTLET_REFS": CURRENT_V06_ACTIVE_REFS,
        "_ACTIVE_GAUNTLET_REFS": CURRENT_V06_ACTIVE_REFS,
        "CURRENT_REGRESSION_CLAIM_TO_ACTS_V06": (
            CURRENT_REGRESSION_CLAIM_TO_ACTS
        ),
    }
    for name, expected in exact_values.items():
        if values.get(name) != expected:
            failures.append(f"s3.kernel_conformance.profile_exact:{name}")

    current_refs = values.get("_V06_CURRENT_ACTIVE_GAUNTLET_REFS")
    if isinstance(current_refs, tuple):
        if _HISTORICAL_ACT_ID in current_refs:
            failures.append("s3.kernel_conformance.old_act_in_current_profile")
        if len(current_refs) != len(set(current_refs)):
            failures.append("s3.kernel_conformance.current_profile_duplicate_act")
    act_sources = values.get("_ACT_SOURCES")
    if isinstance(act_sources, dict) and _HISTORICAL_ACT_ID in act_sources:
        failures.append("s3.kernel_conformance.historical_act_rebound")

    report_fields = set(_class_fields(tree, "KernelConformanceReportV01"))
    for field in (
        "profile_id",
        "historical_profile_ref",
        "claim_to_current_act",
        "current_act_count",
        "active_gauntlet_refs",
    ):
        if field not in report_fields:
            failures.append(f"s3.kernel_conformance.report_field_missing:{field}")

    if _HISTORICAL_RUNNER_MODULE in source or _HISTORICAL_RUNNER_SYMBOL in source:
        failures.append("s3.kernel_conformance.historical_runner_reference")
    if _reads_historical_pass_material(tree):
        failures.append("s3.kernel_conformance.historical_pass_consumption")

    runner_values, runner_tree, runner_source = _static_assignments(
        repo_root / KERNEL_CONFORMANCE_RUNNER_PATH,
        "s3.kernel_conformance_runner",
        failures,
    )
    if runner_values.get("RUNNER_VERSION") != "v0.6":
        failures.append("s3.kernel_conformance_runner.version")
    if not _assignment_is_name(
        runner_tree,
        "DEFAULT_KERNEL_CONFORMANCE_PROFILE",
        "KERNEL_CONFORMANCE_PROFILE_V06_CURRENT",
    ):
        failures.append("s3.kernel_conformance_runner.default_profile")
    if runner_values.get("KERNEL_CONFORMANCE_PROFILE_V05_HISTORICAL") != (
        HISTORICAL_PROFILE_ID
    ):
        failures.append("s3.kernel_conformance_runner.historical_profile")
    if runner_values.get("KERNEL_CONFORMANCE_PROFILE_V06_CURRENT") != (
        CURRENT_PROFILE_ID
    ):
        failures.append("s3.kernel_conformance_runner.current_profile")
    runner_refs = runner_values.get("_BASE_ACT_IDS")
    if runner_refs != CURRENT_V06_ACTIVE_REFS:
        failures.append("s3.kernel_conformance_runner.current_refs")
    if runner_values.get("_V05_HISTORICAL_BASE_ACT_IDS") != (
        HISTORICAL_V05_ACTIVE_REFS
    ):
        failures.append("s3.kernel_conformance_runner.historical_refs")
    runner_act_sources = runner_values.get("_ACT_SOURCES")
    if isinstance(runner_act_sources, dict) and _HISTORICAL_ACT_ID in runner_act_sources:
        failures.append("s3.kernel_conformance_runner.historical_act_rebound")
    if _reads_historical_pass_material(runner_tree):
        failures.append("s3.kernel_conformance_runner.historical_pass_consumption")

    living_values, living_tree, living_source = _static_assignments(
        repo_root / LIVING_GAUNTLET_PATH,
        "s3.living_gauntlet",
        failures,
    )
    if living_values.get("RUNNER_VERSION") != "v1.5":
        failures.append("s3.living_gauntlet.version")
    living_exact_values = {
        "KERNEL_CONFORMANCE_PROFILE_V05_HISTORICAL": HISTORICAL_PROFILE_ID,
        "KERNEL_CONFORMANCE_PROFILE_V06_CURRENT": CURRENT_PROFILE_ID,
        "DEFAULT_KERNEL_CONFORMANCE_PROFILE": CURRENT_PROFILE_ID,
        "HISTORICAL_KERNEL_CONFORMANCE_ACTIVE_REFS_V05": (
            HISTORICAL_V05_ACTIVE_REFS
        ),
        "CURRENT_KERNEL_CONFORMANCE_ACTIVE_REFS_V06": CURRENT_V06_ACTIVE_REFS,
        "CURRENT_REGRESSION_CLAIM_TO_ACTS_V06": (
            CURRENT_REGRESSION_CLAIM_TO_ACTS
        ),
    }
    for name, expected in living_exact_values.items():
        if living_values.get(name) != expected:
            failures.append(f"s3.living_gauntlet.profile_exact:{name}")
    for source_name in ("_ACTIVE_ACT_SOURCES", "_CURRENT_SEAMS"):
        source_map = living_values.get(source_name)
        if isinstance(source_map, dict) and _HISTORICAL_ACT_ID in source_map:
            failures.append(f"s3.living_gauntlet.historical_act_rebound:{source_name}")
    for executed_name in ("_EXECUTED_RUNTIME_ACT_IDS", "_EXECUTED_CONFORMANCE_ACT_IDS"):
        executed_ids = living_values.get(executed_name)
        if isinstance(executed_ids, tuple) and _HISTORICAL_ACT_ID in executed_ids:
            failures.append(
                f"s3.living_gauntlet.historical_act_executed:{executed_name}"
            )
    evidence_only_ids = living_values.get("_EVIDENCE_ONLY_ACT_IDS")
    if not isinstance(evidence_only_ids, tuple) or _HISTORICAL_ACT_ID not in (
        evidence_only_ids
    ):
        failures.append("s3.living_gauntlet.historical_evidence_identity_missing")
    if _reads_historical_pass_material(living_tree):
        failures.append("s3.living_gauntlet.historical_pass_consumption")
    living_report_fields = set(_class_fields(living_tree, "LivingGauntletReportV01"))
    # The Living report is a plain dictionary in the current runner; these keys
    # are therefore also accepted as explicit string literals in its collector.
    required_living_fields = (
        "kernel_conformance_profile",
        "historical_kernel_conformance_profile",
        "current_regression_claim_mapping",
    )
    for field in required_living_fields:
        if field not in living_report_fields and field not in living_source:
            failures.append(f"s3.living_gauntlet.report_field_missing:{field}")


def _python_module_name(relative_path: str) -> str | None:
    if not relative_path.endswith(".py"):
        return None
    parts = list(PurePosixPath(relative_path).with_suffix("").parts)
    if parts and parts[-1] == "__init__":
        parts.pop()
    return ".".join(parts) if parts else None


def _resolve_import_from(
    source_module: str,
    source_is_package: bool,
    node: ast.ImportFrom,
) -> str:
    if node.level == 0:
        return node.module or ""
    package_parts = source_module.split(".") if source_is_package else source_module.split(".")[:-1]
    trim = node.level - 1
    if trim:
        package_parts = package_parts[:-trim] if trim <= len(package_parts) else []
    if node.module:
        package_parts.extend(node.module.split("."))
    return ".".join(package_parts)


def _imports_from_tree(
    tree: ast.Module,
    source_module: str,
    source_is_package: bool,
) -> frozenset[str]:
    imported: set[str] = set()
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            imported.update(alias.name for alias in node.names)
        elif isinstance(node, ast.ImportFrom):
            base = _resolve_import_from(source_module, source_is_package, node)
            if base:
                imported.add(base)
            for alias in node.names:
                if alias.name != "*":
                    imported.add(f"{base}.{alias.name}" if base else alias.name)
        elif isinstance(node, ast.Call):
            dynamic_loader = (
                isinstance(node.func, ast.Name) and node.func.id == "__import__"
            ) or (
                isinstance(node.func, ast.Attribute)
                and node.func.attr == "import_module"
            )
            if (
                dynamic_loader
                and node.args
                and isinstance(node.args[0], ast.Constant)
                and isinstance(node.args[0].value, str)
            ):
                imported.add(node.args[0].value)
    return frozenset(imported)


def _build_python_import_graph(
    repo_root: Path,
    failures: list[str],
) -> tuple[dict[str, frozenset[str]], dict[str, str]]:
    graph: dict[str, frozenset[str]] = {}
    paths: dict[str, str] = {}
    for path in sorted(repo_root.rglob("*.py")):
        if ".git" in path.parts or "__pycache__" in path.parts:
            continue
        try:
            relative = path.relative_to(repo_root).as_posix()
        except ValueError:
            continue
        module = _python_module_name(relative)
        if module is None:
            continue
        try:
            tree = ast.parse(path.read_text(encoding="utf-8"), filename=relative)
        except (OSError, UnicodeError, SyntaxError) as exc:
            if relative in {
                CONFORMANCE_SOURCE_PATH,
                KERNEL_CONFORMANCE_RUNNER_PATH,
                LIVING_GAUNTLET_PATH,
            }:
                failures.append(
                    f"s3.import_graph.parse:{relative}:{type(exc).__name__}"
                )
            continue
        graph[module] = _imports_from_tree(
            tree,
            module,
            path.name == "__init__.py",
        )
        paths[module] = relative
    return graph, paths


def _retired_reachable(
    seed_modules: Iterable[str],
    graph: dict[str, frozenset[str]],
) -> frozenset[str]:
    retired_modules = set(RETIRED_MODULE_NAMES) | {_HISTORICAL_RUNNER_MODULE}
    found: set[str] = set()
    pending = list(seed_modules)
    visited: set[str] = set()
    while pending:
        module = pending.pop()
        if module in visited:
            continue
        visited.add(module)
        for imported in graph.get(module, ()):
            matches = {
                retired
                for retired in retired_modules
                if imported == retired or imported.startswith(retired + ".")
            }
            found.update(matches)
            candidates = [imported]
            parts = imported.split(".")
            candidates.extend(".".join(parts[:index]) for index in range(len(parts) - 1, 0, -1))
            pending.extend(candidate for candidate in candidates if candidate in graph)
    return frozenset(found)


def _validate_current_import_graph(
    repo_root: Path,
    onboarding_paths: Iterable[str],
    failures: list[str],
) -> None:
    graph, paths_by_module = _build_python_import_graph(repo_root, failures)
    modules_by_path = {path: module for module, path in paths_by_module.items()}
    current_python = {
        path for path in onboarding_paths if path.endswith(".py")
    }
    g2_markers = (
        "g2_",
        "action_commit_packet",
        "drs_semantic_address",
        "reuse_certificate",
        "execution_mode_router",
        "fractal_runtime",
        "continuous_delta_runtime",
    )
    scope_paths = {
        "current_gate2": {
            path for path in current_python if any(marker in path for marker in g2_markers)
        },
        "living_gauntlet": {
            LIVING_GAUNTLET_PATH,
            "tests/test_living_gauntlet_v01_runner.py",
        },
        "kernel_conformance": {
            CONFORMANCE_SOURCE_PATH,
            KERNEL_CONFORMANCE_RUNNER_PATH,
            "tests/test_kernel_conformance_v01_runner.py",
        },
        "e5": set(REQUIRED_E5_PATHS),
    }
    scope_paths["current_gate1"] = current_python - scope_paths["current_gate2"]
    scope_paths["current_gate1"].update(
        path
        for path in modules_by_path
        if path.startswith("hedgehog/kernel/") and path.endswith(".py")
    )
    for scope, paths in scope_paths.items():
        seeds = {
            modules_by_path[path]
            for path in paths
            if path in modules_by_path
        }
        for retired in sorted(_retired_reachable(seeds, graph)):
            failures.append(
                f"s3.import_graph.{RETIRED_IMPORT_SCOPE_LABELS[scope]}:{retired}"
            )

    facade_seeds = {
        modules_by_path[path]
        for path in ("hedgehog/__init__.py", "hedgehog/kernel/__init__.py")
        if path in modules_by_path
    }
    for retired in sorted(_retired_reachable(facade_seeds, graph)):
        failures.append(f"s3.package_facade.retired_export:{retired}")


def _validate_committed_e5_content(
    repo_root: Path,
    failures: list[str],
) -> None:
    """Reject retired positive vocabulary and topology-ownership claims.

    The focused E5 test and runner may contain exact negative assertions or
    non-claim fields for retired vocabulary. Import isolation for all three
    committed paths is enforced separately by ``_validate_current_import_graph``.
    """

    folded_forbidden = tuple(term.casefold() for term in FORBIDDEN_DIRECT_TERMS)
    for relative_path in sorted(REQUIRED_E5_PATHS):
        path = repo_root / relative_path
        if not path.exists():
            failures.append(f"s3.e5_runtime.missing:{relative_path}")
            continue
        try:
            source = path.read_text(encoding="utf-8")
        except (OSError, UnicodeError) as exc:
            failures.append(
                f"s3.e5_runtime.read:{relative_path}:{type(exc).__name__}"
            )
            continue
        lines = source.splitlines()
        for index, folded_term in enumerate(folded_forbidden):
            contaminated = False
            for line in lines:
                if folded_term not in line.casefold():
                    continue
                compact = "".join(line.split()).casefold()
                negative_nonclaim = (
                    folded_term == ("plan" + "_" + "graph")
                    and compact
                    in {
                        '"plan_graph_claimed":false,',
                        "'plan_graph_claimed':false,",
                    }
                )
                negative_assertion = (
                    folded_term == ("plan" + "graph")
                    and compact
                    in {
                        'assert"plangraph"notinsource',
                        "assert'plangraph'notinsource",
                    }
                )
                if not negative_nonclaim and not negative_assertion:
                    contaminated = True
                    break
            if contaminated:
                failures.append(
                    f"s3.e5_runtime.retired_positive:{relative_path}:{index}"
                )
        for line_number, line in enumerate(lines, start=1):
            if any(
                pattern.search(line)
                for pattern in _FORBIDDEN_E5_TOPOLOGY_OWNERSHIP_PATTERNS
            ):
                failures.append(
                    "s3.e5_runtime.provider_owned_topology:"
                    f"{relative_path}:{line_number}"
                )


def _validate_current_documents(
    repo_root: Path,
    failures: list[str],
    *,
    closure_active: bool = False,
) -> None:
    folded_forbidden = tuple(term.casefold() for term in FORBIDDEN_DIRECT_TERMS)
    for relative_path in SCANNED_CURRENT_DOCUMENTS:
        path = repo_root / relative_path
        try:
            text = path.read_text(encoding="utf-8")
        except (OSError, UnicodeError) as exc:
            failures.append(f"current_document.read:{relative_path}:{type(exc).__name__}")
            continue
        for term in REQUIRED_CURRENT_TERMS:
            if term not in text:
                failures.append(f"current_document.missing_term:{relative_path}:{term}")
        folded_text = text.casefold()
        for direct_term, folded_term in zip(FORBIDDEN_DIRECT_TERMS, folded_forbidden):
            if folded_term in folded_text:
                failures.append(
                    f"current_document.forbidden_term:{relative_path}:{direct_term}"
                )
        if relative_path == "AGENTS.md":
            section_heading = "## Bounded context and onboarding"
            if section_heading not in text:
                normalized_section = ""
            else:
                section = text.split(section_heading, 1)[1].split("\n## ", 1)[0]
                normalized_section = " ".join(section.split())
            required_warnings = (
                REQUIRED_AGENTS_ONBOARDING_WARNINGS
                if closure_active
                else PRE_CLOSURE_AGENTS_ONBOARDING_WARNINGS
            )
            for warning_id, required_text in required_warnings:
                if required_text not in normalized_section:
                    failures.append(
                        "current_document.missing_onboarding_warning:"
                        f"AGENTS.md:{warning_id}"
                    )


def _validate_e5_basis_ancestry_v02(
    repo_root: Path,
    failures: list[str],
) -> None:
    try:
        object_check = subprocess.run(
            (
                "git",
                "cat-file",
                "-e",
                f"{E5_IMPLEMENTATION_BASIS_COMMIT}^{{commit}}",
            ),
            cwd=repo_root,
            check=False,
            capture_output=True,
        )
    except OSError as exc:
        failures.append(f"e6.committed_e5.git_object:{type(exc).__name__}")
        return
    if object_check.returncode != 0:
        if not (repo_root / ".git").exists():
            failures.append(
                f"e6.committed_e5.git_object:exit_{object_check.returncode}"
            )
        else:
            failures.append("e6.committed_e5.basis_object_missing")
        return
    try:
        ancestor = subprocess.run(
            (
                "git",
                "merge-base",
                "--is-ancestor",
                E5_IMPLEMENTATION_BASIS_COMMIT,
                "HEAD",
            ),
            cwd=repo_root,
            check=False,
            capture_output=True,
        )
    except OSError as exc:
        failures.append(f"e6.committed_e5.git_ancestry:{type(exc).__name__}")
        return
    if ancestor.returncode == 1:
        failures.append("e6.committed_e5.basis_not_ancestor")
    elif ancestor.returncode != 0:
        failures.append(
            f"e6.committed_e5.ancestry_indeterminate:exit_{ancestor.returncode}"
        )


def _validate_g2e_closure_surfaces_v01(
    repo_root: Path,
    authority_index: dict[str, object] | None,
    successor_manifest: dict[str, object] | None,
    failures: list[str],
) -> None:
    overlay = _load_json(
        repo_root / "release/current_status_overlay_v01.json",
        "g2e.closure.overlay",
        failures,
    )
    if overlay is not None:
        role = overlay.get("overlay_role")
        if not isinstance(role, dict):
            failures.append("g2e.closure.overlay.role_type")
        else:
            for key in (
                "is_authority",
                "is_completion_certificate",
                "is_gate2_closure_manifest",
                "is_public_release_declaration",
                "is_root_decision",
                "replaces_historical_evidence",
            ):
                if role.get(key) is not False:
                    failures.append(f"g2e.closure.overlay.role:{key}")
            if role.get("metadata_only") is not True:
                failures.append("g2e.closure.overlay.role:metadata_only")
        boundary = overlay.get("current_engineering_boundary")
        if not isinstance(boundary, dict):
            failures.append("g2e.closure.overlay.boundary_type")
        else:
            for key, expected in G2E_CLOSURE_EXPECTED_STATUS_FIELDS.items():
                if boundary.get(key) != expected:
                    failures.append(f"g2e.closure.overlay.status:{key}")

    expected_checkpoint_entry = {
        "path": G2E_CHECKPOINT_PATH,
        "status": "accepted_g2e_continuous_delta_runtime_closure_checkpoint",
        "current_authority": True,
        "authority_scope": NAMED_GATE_SCOPE,
        "may_override_architecture_lock": False,
        "onboarding_allowed": True,
        "role": (
            "current G2-E CLOSED_PASS lifecycle checkpoint; bounded to G2-E "
            "and subordinate to the Current Architecture Lock"
        ),
    }
    expected_audit_entry = {
        "path": G2E_AUDIT_PATH,
        "status": "accepted_g2e_closure_audit_evidence",
        "current_authority": False,
        "authority_scope": AUDIT_EVIDENCE_SCOPE,
        "may_override_architecture_lock": False,
        "onboarding_allowed": False,
        "role": (
            "independent G2-E closure evidence; non-authoritative and excluded "
            "from automatic onboarding"
        ),
    }
    if authority_index is not None:
        technical = authority_index.get("current_technical_annexes")
        checkpoint_entries = (
            [
                entry
                for entry in technical
                if isinstance(entry, dict)
                and entry.get("path") == G2E_CHECKPOINT_PATH
            ]
            if isinstance(technical, list)
            else []
        )
        if checkpoint_entries != [expected_checkpoint_entry]:
            failures.append("g2e.closure.authority_index.checkpoint_exact")
        audit_sources = authority_index.get("audit_only_sources")
        audit_entries = (
            [
                entry
                for entry in audit_sources
                if isinstance(entry, dict)
                and entry.get("path") == G2E_AUDIT_PATH
            ]
            if isinstance(audit_sources, list)
            else []
        )
        if audit_entries != [expected_audit_entry]:
            failures.append("g2e.closure.authority_index.audit_exact")

    if successor_manifest is not None:
        for key in (
            "always_include",
            "include_current_gate_sources",
            "authority_documents",
        ):
            paths = successor_manifest.get(key)
            if not isinstance(paths, list) or paths.count(G2E_CHECKPOINT_PATH) != 1:
                failures.append(f"g2e.closure.manifest.checkpoint:{key}")
            if isinstance(paths, list) and G2E_AUDIT_PATH in paths:
                failures.append(f"g2e.closure.manifest.audit_onboarded:{key}")
        globs = successor_manifest.get("exclude_globs")
        if not isinstance(globs, list) or "docs/audit_reports/**" not in globs:
            failures.append("g2e.closure.manifest.audit_exclusion")

    required_text = {
        G2E_AUDIT_PATH: (
            "AUDIT_VERDICT=PASS",
            "G2E6_STATUS=IMPLEMENTED_COMMITTED_ACCEPTANCE_PASS",
            "G2E_STATUS=CLOSED_PASS",
            "G2F_STATUS=NEXT_NOT_STARTED_NOT_AUTHORIZED",
            "G2F_IMPLEMENTATION_AUTHORIZED=false",
            "GATE2_STATUS=NOT_CLOSED",
            "PUBLIC_RELEASE_STATUS=NOT_CLAIMED",
            "RC2_STATUS=NOT_CLAIMED",
            "PRODUCTION_READINESS_STATUS=NOT_CLAIMED",
            "PRODUCTION_SECURITY_CERTIFICATION_STATUS=NOT_CLAIMED",
            "REAL_WORLD_EFFECTS_COUNT=0",
        ),
        G2E_CHECKPOINT_PATH: (
            "CHECKPOINT_STATUS=CLOSED_PASS",
            "RUNTIME_PHASE=POST_E6_SUCCESSOR",
            "LIFECYCLE_PHASE=G2E_CLOSED_PASS",
            f"AUDIT_SHA256={G2E_AUDIT_SHA256}",
            "G2E6_STATUS=IMPLEMENTED_COMMITTED_ACCEPTANCE_PASS",
            "G2E_STATUS=CLOSED_PASS",
            "G2F_STATUS=NEXT_NOT_STARTED_NOT_AUTHORIZED",
            "G2F_IMPLEMENTATION_AUTHORIZED=false",
            "GATE2_STATUS=NOT_CLOSED",
            "REAL_WORLD_EFFECTS_COUNT=0",
        ),
        LOCK_PATH: (
            "## 8. Current Gate-2 / G2-E closure boundary",
            "G2-E: `CLOSED_PASS`",
            "G2-F is `NEXT_NOT_STARTED_NOT_AUTHORIZED`",
            "Gate 2 remains `NOT_CLOSED`",
        ),
        "AGENTS.md": (
            "G2-E is `CLOSED_PASS`",
            "G2-F is `NEXT_NOT_STARTED_NOT_AUTHORIZED`",
            "Gate 2 is `NOT_CLOSED`",
        ),
        "README.md": (
            "G2-E is `CLOSED_PASS`",
            "G2-F is `NEXT_NOT_STARTED_NOT_AUTHORIZED`",
            "Gate 2 remains `NOT_CLOSED`",
        ),
        "release/current_limitations.md": (
            "G2-E is `CLOSED_PASS`",
            "G2-F is `NEXT_NOT_STARTED_NOT_AUTHORIZED`",
            "Gate 2 remains `NOT_CLOSED`",
        ),
        "release/current_release_notes.md": (
            "G2-E is `CLOSED_PASS`",
            "G2-F is `NEXT_NOT_STARTED_NOT_AUTHORIZED`",
            "Gate 2 remains `NOT_CLOSED`",
        ),
    }
    for relative_path, markers in required_text.items():
        try:
            text = (repo_root / relative_path).read_text(encoding="utf-8")
        except (OSError, UnicodeError) as exc:
            failures.append(
                f"g2e.closure.document.read:{relative_path}:{type(exc).__name__}"
            )
            continue
        for marker in markers:
            if marker not in text:
                failures.append(
                    f"g2e.closure.document.marker:{relative_path}:{marker}"
                )

    claim_path = repo_root / "release/claim_to_evidence_index.md"
    try:
        claim_text = claim_path.read_text(encoding="utf-8")
    except (OSError, UnicodeError) as exc:
        failures.append(f"g2e.closure.claim_index.read:{type(exc).__name__}")
    else:
        claim_id = "claim_g2e_continuous_delta_runtime_closed_pass"
        rows = [line for line in claim_text.splitlines() if f"| {claim_id} |" in line]
        if len(rows) != 1:
            failures.append("g2e.closure.claim_index.row_count")
        else:
            row = rows[0]
            for value in (
                G2E_AUDIT_PATH,
                G2E_AUDIT_SHA256,
                G2E_CHECKPOINT_PATH,
                G2E_CHECKPOINT_SHA256,
                "CLOSED_PASS",
                "Gate 2",
                "G2-F",
            ):
                if value not in row:
                    failures.append(
                        f"g2e.closure.claim_index.binding:{value}"
                    )


def _g2f_import_bindings_v02(
    tree: ast.Module,
) -> tuple[dict[str, str], set[str], set[str]]:
    bindings: dict[str, str] = {}
    private_or_star: set[str] = set()
    mock_patch_aliases: set[str] = set()
    for node in tree.body:
        if isinstance(node, ast.Import):
            for alias in node.names:
                local = alias.asname or alias.name.split(".", 1)[0]
                bindings[local] = alias.name
                if any(part.startswith("_") for part in alias.name.split(".")):
                    private_or_star.add(alias.name)
                if alias.name in {"unittest.mock", "mock"}:
                    mock_patch_aliases.add(f"{local}.patch")
        elif isinstance(node, ast.ImportFrom):
            module = node.module or ""
            for alias in node.names:
                local = alias.asname or alias.name
                if alias.name == "*" or alias.name.startswith("_"):
                    private_or_star.add(f"{module}.{alias.name}")
                    continue
                bindings[local] = f"{module}.{alias.name}" if module else alias.name
                if module in {"unittest.mock", "mock"} and alias.name == "patch":
                    mock_patch_aliases.add(local)
                if module == "unittest" and alias.name == "mock":
                    mock_patch_aliases.add(f"{local}.patch")
    return bindings, private_or_star, mock_patch_aliases


def _g2f_resolved_call_v02(node: ast.Call, bindings: dict[str, str]) -> str:
    dotted = _dotted_ast_name(node.func) or ""
    if not dotted:
        return ""
    first, separator, remainder = dotted.partition(".")
    bound = bindings.get(first)
    if bound is None:
        return dotted
    return bound + (separator + remainder if separator else "")


def _g2f_constant_expression_v02(node: ast.AST) -> bool:
    if isinstance(node, ast.Constant):
        return True
    if isinstance(node, (ast.Tuple, ast.List, ast.Set)):
        return all(_g2f_constant_expression_v02(item) for item in node.elts)
    if isinstance(node, ast.Dict):
        return all(
            key is None or _g2f_constant_expression_v02(key)
            for key in node.keys
        ) and all(_g2f_constant_expression_v02(value) for value in node.values)
    if isinstance(node, ast.UnaryOp):
        return _g2f_constant_expression_v02(node.operand)
    if isinstance(node, ast.BoolOp):
        return all(_g2f_constant_expression_v02(value) for value in node.values)
    if isinstance(node, ast.Compare):
        return _g2f_constant_expression_v02(node.left) and all(
            _g2f_constant_expression_v02(value) for value in node.comparators
        )
    return False


def _g2f_direct_tautology_v02(node: ast.Assert) -> bool:
    test = node.test
    if isinstance(test, ast.Constant):
        return bool(test.value)
    if isinstance(test, ast.Compare) and len(test.ops) == len(test.comparators) == 1:
        right = test.comparators[0]
        if ast.dump(test.left, include_attributes=False) == ast.dump(
            right, include_attributes=False
        ):
            return isinstance(test.ops[0], (ast.Eq, ast.Is, ast.IsNot))
        return _g2f_constant_expression_v02(test.left) and (
            _g2f_constant_expression_v02(right)
        )
    return _g2f_constant_expression_v02(test)


def _g2f_public_call_graph_failures_v03(
    functions: dict[str, ast.FunctionDef | ast.AsyncFunctionDef],
) -> tuple[str, ...]:
    public_names = frozenset(
        {
            "collect_consolidated_gate2_gauntlet_g2_f_v01",
            "validate_consolidated_gate2_gauntlet_g2_f_report_v01",
            "consolidated_gate2_gauntlet_g2_f_report_to_plain_data_v01",
            "render_consolidated_gate2_gauntlet_g2_f_v01",
            "main",
        }
    )
    edges: dict[str, dict[str, int]] = {
        name: {target: 0 for target in public_names}
        for name in public_names
    }
    for name in public_names:
        function = functions.get(name)
        if function is None:
            continue
        for node in ast.walk(function):
            if not isinstance(node, ast.Call):
                continue
            called = (_dotted_ast_name(node.func) or "").rsplit(".", 1)[-1]
            if called in public_names:
                edges[name][called] += 1

    failures: list[str] = []
    collector = "collect_consolidated_gate2_gauntlet_g2_f_v01"
    validator = "validate_consolidated_gate2_gauntlet_g2_f_report_v01"
    projector = "consolidated_gate2_gauntlet_g2_f_report_to_plain_data_v01"
    renderer = "render_consolidated_gate2_gauntlet_g2_f_v01"
    if edges[collector][validator] != 1:
        failures.append(
            "g2f.implementation.call_graph.collector_validator_exact_once:"
            f"{edges[collector][validator]}"
        )

    def reaches(source: str, target: str) -> bool:
        pending = [name for name, count in edges[source].items() if count]
        seen: set[str] = set()
        while pending:
            current = pending.pop()
            if current == target:
                return True
            if current in seen:
                continue
            seen.add(current)
            pending.extend(
                name for name, count in edges[current].items() if count
            )
        return False

    for source in (validator, projector, renderer):
        if reaches(source, collector):
            failures.append(
                f"g2f.implementation.call_graph.collector_reachable:{source}"
            )
    for name in sorted(public_names):
        if edges[name][name]:
            failures.append(f"g2f.implementation.call_graph.self_recursion:{name}")
    for left in sorted(public_names):
        for right in sorted(public_names):
            if left >= right:
                continue
            if reaches(left, right) and reaches(right, left):
                failures.append(
                    f"g2f.implementation.call_graph.nontrivial_scc:{left}:{right}"
                )
    return tuple(sorted(set(failures)))


def _g2f_status_overclaims_v02(source: str) -> tuple[str, ...]:
    failures: list[str] = []
    exact_statuses = {
        "G2F_RUNTIME_IMPLEMENTATION_PERFORMED": "false",
        "GATE2_STATUS": "NOT_CLOSED",
    }
    for key, expected in exact_statuses.items():
        observed = re.findall(
            rf"(?m)^\s*{re.escape(key)}\s*=\s*([^\s#]+)", source
        )
        if any(value != expected for value in observed):
            failures.append(f"{key}:{','.join(observed)}")
    forbidden_patterns = (
        r"(?im)^\s*G2F_(?:STATUS|ACCEPTANCE_PASS|AUDIT_PASS)\s*=\s*(?:CLOSED_PASS|PASS|true)\s*$",
        r"(?im)^\s*GATE2_STATUS\s*=\s*(?:CLOSED|CLOSED_PASS|PASS)\s*$",
        r"(?im)^\s*RC2(?:_STATUS|_INTERNAL_REFERENCE_CLAIM_ALLOWED)?\s*=\s*(?:CLAIMED|ALLOWED|true|PASS)\s*$",
        r"(?im)^\s*PUBLIC_RELEASE(?:_STATUS)?\s*=\s*(?:CLAIMED|true|PASS)\s*$",
        r"(?im)^\s*PRODUCTION_(?:READINESS|SECURITY_CERTIFICATION)(?:_STATUS)?\s*=\s*(?:CLAIMED|true|PASS)\s*$",
        r"(?im)^\s*REAL_WORLD_EFFECTS(?:_COUNT)?\s*=\s*[1-9][0-9]*\s*$",
    )
    for index, pattern in enumerate(forbidden_patterns, 1):
        if re.search(pattern, source):
            failures.append(f"forbidden_status_pattern_{index}")
    return tuple(failures)


def _validate_g2f_future_implementation_contract_v01(
    repo_root: Path,
    failures: list[str],
) -> None:
    runner_path = repo_root / G2F_RUNNER_PATH
    test_path = repo_root / G2F_TEST_PATH
    if not runner_path.exists() and not test_path.exists():
        return
    if not runner_path.is_file():
        failures.append(f"g2f.implementation.missing:{G2F_RUNNER_PATH}")
        return
    if not test_path.is_file():
        failures.append(f"g2f.implementation.missing:{G2F_TEST_PATH}")
        return
    trees: dict[str, ast.Module] = {}
    sources: dict[str, str] = {}
    for label, path in (("runner", runner_path), ("tests", test_path)):
        try:
            source = path.read_text(encoding="utf-8")
            sources[label] = source
            trees[label] = ast.parse(source, filename=str(path))
        except (OSError, UnicodeError, SyntaxError) as exc:
            failures.append(
                f"g2f.implementation.{label}.parse:{type(exc).__name__}"
            )
    if set(trees) != {"runner", "tests"}:
        return
    runner_tree = trees["runner"]
    test_tree = trees["tests"]
    public_surface = {
        "collect_consolidated_gate2_gauntlet_g2_f_v01": 0,
        "validate_consolidated_gate2_gauntlet_g2_f_report_v01": 1,
        "consolidated_gate2_gauntlet_g2_f_report_to_plain_data_v01": 1,
        "render_consolidated_gate2_gauntlet_g2_f_v01": 1,
        "main": 0,
    }
    function_nodes = [
        node
        for node in runner_tree.body
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef))
    ]
    functions: dict[str, ast.FunctionDef | ast.AsyncFunctionDef] = {}
    for node in function_nodes:
        if node.name in functions:
            failures.append(
                f"g2f.implementation.public_surface.duplicate:{node.name}"
            )
        else:
            functions[node.name] = node
    for extra_name in sorted(set(functions) - set(public_surface)):
        failures.append(
            f"g2f.implementation.runner.extra_helper:{extra_name}"
        )
    for name, positional_count in public_surface.items():
        function = functions.get(name)
        if function is None:
            failures.append(f"g2f.implementation.public_surface.missing:{name}")
            continue
        if not isinstance(function, ast.FunctionDef):
            failures.append(f"g2f.implementation.public_surface.async:{name}")
        arguments = function.args
        if (
            len(arguments.posonlyargs) + len(arguments.args) != positional_count
            or arguments.kwonlyargs
            or arguments.vararg is not None
            or arguments.kwarg is not None
            or arguments.defaults
            or arguments.kw_defaults
        ):
            failures.append(f"g2f.implementation.public_surface.signature:{name}")
    failures.extend(_g2f_public_call_graph_failures_v03(functions))
    runner_bindings, private_or_star, _runner_patch_aliases = (
        _g2f_import_bindings_v02(runner_tree)
    )
    for imported in sorted(private_or_star):
        failures.append(
            f"g2f.implementation.runner.private_or_star_import:{imported}"
        )
    dynamic_calls = {
        "__import__", "getattr", "exec", "eval", "importlib.import_module"
    }
    aggregate_or_future_calls = (
        "collect_living_gauntlet",
        "collect_kernel_conformance",
        "collect_continuous_delta_runtime_g2_e",
        "gate6",
        "gate_6",
        "pack_s",
        "packs",
    )
    for node in ast.walk(runner_tree):
        if isinstance(node, (ast.Import, ast.ImportFrom)):
            for alias in node.names:
                imported = (
                    f"{node.module}.{alias.name}"
                    if isinstance(node, ast.ImportFrom) and node.module
                    else alias.name
                )
                if imported == "tests" or imported.startswith("tests."):
                    failures.append("g2f.implementation.runner.test_import")
                if alias.name.startswith("_"):
                    failures.append(
                        f"g2f.implementation.runner.private_import:{alias.name}"
                    )
                if any(
                    marker in imported.casefold()
                    for marker in (
                        "requests",
                        "urllib",
                        "http.client",
                        "socket",
                        "provider",
                        "connector",
                        "adapter",
                    )
                ):
                    failures.append(
                        f"g2f.implementation.runner.forbidden_import:{imported}"
                    )
        if isinstance(node, ast.Call):
            resolved = _g2f_resolved_call_v02(node, runner_bindings)
            called = resolved.casefold()
            dotted = (_dotted_ast_name(node.func) or "").casefold()
            if dotted in dynamic_calls or called in dynamic_calls:
                failures.append(
                    f"g2f.implementation.runner.dynamic_access:{called or dotted}"
                )
            if any(part.startswith("_") for part in resolved.split(".")):
                failures.append(
                    f"g2f.implementation.runner.private_attribute_call:{resolved}"
                )
            if any(marker in called for marker in aggregate_or_future_calls):
                failures.append(
                    f"g2f.implementation.runner.aggregate_or_future_call:{resolved}"
                )
            if any(
                marker in called
                for marker in (
                    "invoke_provider",
                    "call_provider",
                    "invoke_model",
                    "call_model",
                    "network_call",
                    "connector_call",
                    "adapter_call",
                    "execute_effect",
                    "apply_effect",
                )
            ):
                failures.append(
                    f"g2f.implementation.runner.forbidden_call:{called}"
                )
    for status_failure in _g2f_status_overclaims_v02(sources["runner"]):
        failures.append(
            f"g2f.implementation.runner.status_overclaim:{status_failure}"
        )
    collector = functions.get("collect_consolidated_gate2_gauntlet_g2_f_v01")
    if collector is not None:
        for node in ast.walk(collector):
            if isinstance(node, ast.Constant) and node.value == "PASS":
                failures.append("g2f.implementation.runner.copied_pass")
                break
        collector_calls: dict[str, int] = {
            name: 0 for name in G2F_REQUIRED_PUBLIC_CALLS_V02
        }
        for node in ast.walk(collector):
            if not isinstance(node, ast.Call):
                continue
            resolved = _g2f_resolved_call_v02(node, runner_bindings)
            for name, (module, _minimum) in G2F_REQUIRED_PUBLIC_CALLS_V02.items():
                if resolved == f"{module}.{name}":
                    collector_calls[name] += 1
        for name, (module, minimum) in G2F_REQUIRED_PUBLIC_CALLS_V02.items():
            observed = collector_calls[name]
            if observed < minimum:
                failures.append(
                    "g2f.implementation.runner.required_public_call:"
                    f"{module}.{name}:{observed}<{minimum}"
                )
        own_validator_calls = sum(
            1
            for node in ast.walk(collector)
            if isinstance(node, ast.Call)
            and (_dotted_ast_name(node.func) or "")
            == "validate_consolidated_gate2_gauntlet_g2_f_report_v01"
        )
        if own_validator_calls != 1:
            failures.append(
                "g2f.implementation.runner.required_public_call:"
                "validate_consolidated_gate2_gauntlet_g2_f_report_v01:"
                f"{own_validator_calls}!=1"
            )

    validator = functions.get(
        "validate_consolidated_gate2_gauntlet_g2_f_report_v01"
    )
    if validator is not None:
        argument_name = validator.args.args[0].arg if validator.args.args else ""
        report_used = any(
            isinstance(node, ast.Name)
            and isinstance(node.ctx, ast.Load)
            and node.id == argument_name
            for node in ast.walk(validator)
        )
        constant_returns = [
            node
            for node in ast.walk(validator)
            if isinstance(node, ast.Return)
            and node.value is not None
            and _g2f_constant_expression_v02(node.value)
        ]
        if not report_used and constant_returns:
            failures.append(
                "g2f.implementation.runner.constant_validator_without_report"
            )

    cache_decorator_aliases = {"cache", "lru_cache"}
    for local, imported in runner_bindings.items():
        if imported in {"functools.cache", "functools.lru_cache"}:
            cache_decorator_aliases.add(local)
        if imported == "functools":
            cache_decorator_aliases.update(
                {f"{local}.cache", f"{local}.lru_cache"}
            )
    for function in function_nodes:
        for decorator in function.decorator_list:
            target = decorator.func if isinstance(decorator, ast.Call) else decorator
            dotted = _dotted_ast_name(target) or ""
            if dotted in cache_decorator_aliases:
                failures.append(
                    f"g2f.implementation.runner.process_cache_decorator:{dotted}"
                )
    for statement in runner_tree.body:
        if not isinstance(statement, (ast.Assign, ast.AnnAssign)):
            continue
        targets = statement.targets if isinstance(statement, ast.Assign) else [statement.target]
        value = statement.value
        for target in targets:
            if not isinstance(target, ast.Name):
                continue
            target_name = target.id.casefold()
            collected_at_module_scope = (
                isinstance(value, ast.Call)
                and (_dotted_ast_name(value.func) or "").endswith(
                    "collect_consolidated_gate2_gauntlet_g2_f_v01"
                )
            )
            if collected_at_module_scope or any(
                marker in target_name
                for marker in ("cache", "cached_report", "report_singleton")
            ):
                failures.append(
                    f"g2f.implementation.runner.process_cache:{target.id}"
                )

    observed_tests = tuple(
        node.name
        for node in test_tree.body
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef))
        and node.name.startswith("test_")
    )
    expected_tests = tuple(f"test_{test_id}" for test_id in G2F_FOCUSED_TEST_IDS)
    if observed_tests != expected_tests:
        failures.append("g2f.implementation.tests.exact_24_ordered_nodes")
    for node in test_tree.body:
        if (
            isinstance(node, ast.AsyncFunctionDef)
            and node.name.startswith("test_")
        ):
            failures.append(
                f"g2f.implementation.tests.async_test:{node.name}"
            )
        if isinstance(node, ast.FunctionDef) and node.name.startswith("test_"):
            if any(isinstance(child, (ast.Yield, ast.YieldFrom)) for child in ast.walk(node)):
                failures.append(
                    f"g2f.implementation.tests.generator_test:{node.name}"
                )
            for decorator in node.decorator_list:
                target = decorator.func if isinstance(decorator, ast.Call) else decorator
                dotted = (_dotted_ast_name(target) or "").casefold()
                if dotted.endswith("parametrize"):
                    failures.append(
                        f"g2f.implementation.tests.parametrize:{node.name}"
                    )
        if isinstance(node, ast.ClassDef) and any(
            isinstance(child, (ast.FunctionDef, ast.AsyncFunctionDef))
            and child.name.startswith("test_")
            for child in node.body
        ):
            failures.append(
                f"g2f.implementation.tests.test_class:{node.name}"
            )
    test_bindings, _test_private_or_star, mock_patch_aliases = (
        _g2f_import_bindings_v02(test_tree)
    )
    forbidden_test_markers = set()
    for node in ast.walk(test_tree):
        if isinstance(node, ast.Call):
            called = (_dotted_ast_name(node.func) or "").casefold()
            resolved = _g2f_resolved_call_v02(node, test_bindings).casefold()
            if any(
                marker in called
                for marker in (
                    "monkeypatch",
                    "unittest.mock",
                    "pytest.skip",
                    "pytest.xfail",
                    "pytest.importorskip",
                )
            ):
                forbidden_test_markers.add(called)
            if called in {value.casefold() for value in mock_patch_aliases} or (
                resolved.endswith("unittest.mock.patch")
                or resolved.endswith("unittest.mock.patch.object")
                or called.endswith("monkeypatch.setattr")
            ):
                forbidden_test_markers.add(called or resolved)
        if isinstance(node, ast.Attribute):
            dotted = (_dotted_ast_name(node) or "").casefold()
            if dotted.endswith((".skip", ".skipif", ".xfail")):
                forbidden_test_markers.add(dotted)
    if forbidden_test_markers:
        failures.append("g2f.implementation.tests.substitution_or_skip")
    if any(
        isinstance(node, ast.Assert) and _g2f_direct_tautology_v02(node)
        for node in ast.walk(test_tree)
    ):
        failures.append("g2f.implementation.tests.tautological_assertion")
    for status_failure in _g2f_status_overclaims_v02(sources["tests"]):
        failures.append(
            f"g2f.implementation.tests.status_overclaim:{status_failure}"
        )
    collector_name = "collect_consolidated_gate2_gauntlet_g2_f_v01"
    validator_name = "validate_consolidated_gate2_gauntlet_g2_f_report_v01"
    accepted_test_nodes = tuple(
        node
        for node in test_tree.body
        if isinstance(node, ast.FunctionDef) and node.name in expected_tests
    )
    fixture_names: set[str] = set()
    for function in (
        node
        for node in test_tree.body
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef))
    ):
        for decorator in function.decorator_list:
            target = decorator.func if isinstance(decorator, ast.Call) else decorator
            dotted = _dotted_ast_name(target) or ""
            first, separator, remainder = dotted.partition(".")
            bound = test_bindings.get(first)
            resolved = bound + (separator + remainder if separator else "") if bound else dotted
            if resolved == "pytest.fixture":
                fixture_names.add(function.name)

    fixture_substitutions: set[str] = set()
    fixture_sensitive_calls = {
        collector_name,
        validator_name,
        *G2F_REQUIRED_PUBLIC_CALLS_V02,
    }
    for function in accepted_test_nodes:
        parameters = (
            *function.args.posonlyargs,
            *function.args.args,
            *function.args.kwonlyargs,
        )
        fixture_sources = {
            parameter.arg: parameter.arg
            for parameter in parameters
            if parameter.arg in fixture_names
        }
        changed = True
        while changed:
            changed = False
            for node in ast.walk(function):
                target: ast.Name | None = None
                value: ast.AST | None = None
                if (
                    isinstance(node, ast.Assign)
                    and len(node.targets) == 1
                    and isinstance(node.targets[0], ast.Name)
                ):
                    target = node.targets[0]
                    value = node.value
                elif isinstance(node, ast.AnnAssign) and isinstance(
                    node.target, ast.Name
                ):
                    target = node.target
                    value = node.value
                if (
                    target is not None
                    and isinstance(value, ast.Name)
                    and value.id in fixture_sources
                    and target.id not in fixture_sources
                ):
                    fixture_sources[target.id] = fixture_sources[value.id]
                    changed = True
        for node in ast.walk(function):
            if not isinstance(node, ast.Call):
                continue
            if isinstance(node.func, ast.Name) and node.func.id in fixture_sources:
                fixture_substitutions.add(fixture_sources[node.func.id])
            resolved = _g2f_resolved_call_v02(node, test_bindings)
            called_name = resolved.rsplit(".", 1)[-1]
            if called_name not in fixture_sensitive_calls:
                continue
            supplied_values = (*node.args, *(item.value for item in node.keywords))
            for value in supplied_values:
                if isinstance(value, ast.Name) and value.id in fixture_sources:
                    fixture_substitutions.add(fixture_sources[value.id])
    for fixture_name in sorted(fixture_substitutions):
        failures.append(
            f"g2f.implementation.tests.fixture_substitution:{fixture_name}"
        )

    actual_dataflow = False
    for function in accepted_test_nodes:
        report_names: set[str] = set()
        for node in ast.walk(function):
            if (
                isinstance(node, ast.Assign)
                and len(node.targets) == 1
                and isinstance(node.targets[0], ast.Name)
                and isinstance(node.value, ast.Call)
                and (_dotted_ast_name(node.value.func) or "").endswith(collector_name)
                and not node.value.args
                and not node.value.keywords
            ):
                report_names.add(node.targets[0].id)
        if report_names and any(
            isinstance(node, ast.Call)
            and (_dotted_ast_name(node.func) or "").endswith(validator_name)
            and len(node.args) == 1
            and isinstance(node.args[0], ast.Name)
            and node.args[0].id in report_names
            for node in ast.walk(function)
        ):
            actual_dataflow = True
            break
    if not actual_dataflow:
        failures.append("g2f.implementation.tests.actual_public_dataflow")


def _g2f_class_a_ledger_rows_v13(source: str) -> tuple[str, ...]:
    return tuple(
        line
        for line in source.splitlines()
        if re.fullmatch(r"[0-9]{3}\|[^\n]+", line)
    )


def _validate_g2f_class_a_ledger_v13(
    source: str,
    failures: list[str],
) -> tuple[str, ...]:
    rows = _g2f_class_a_ledger_rows_v13(source)
    expected_prefixes = tuple(f"{index:03d}|" for index in range(1, 182))
    if len(rows) != 181:
        failures.append(f"g2f.class_a.preflight.construction_ledger.count:{len(rows)}")
    if tuple(line[:4] for line in rows) != expected_prefixes:
        failures.append("g2f.class_a.preflight.construction_ledger.order")
    if len(rows) != 181 or tuple(line[:4] for line in rows) != expected_prefixes:
        return rows

    parsed: dict[int, tuple[str, str, str, str]] = {}
    for line in rows:
        fields = line.split("|")
        if len(fields) != 5 or any(not field for field in fields):
            failures.append("g2f.class_a.preflight.construction_ledger.shape")
            continue
        row = int(fields[0])
        parsed[row] = (fields[1], fields[2], fields[3], fields[4])
        module_symbol = fields[3]
        if ":" not in module_symbol:
            failures.append(f"g2f.class_a.preflight.producer_shape:{row:03d}")
            continue
        module_path, symbol = module_symbol.rsplit(":", 1)
        if (
            not module_path.startswith("hedgehog/")
            or not module_path.endswith(".py")
            or symbol.startswith("_")
        ):
            failures.append(f"g2f.class_a.preflight.public_producer:{row:03d}")

    ledger_body = ("\n".join(rows) + "\n").encode("utf-8")
    if hashlib.sha256(ledger_body).hexdigest() != (
        G2F_PUBLIC_CONSTRUCTION_LEDGER_SHA256_V13
    ):
        failures.append("g2f.class_a.preflight.construction_ledger.identity")

    producer_basis_parts: list[str] = []
    for row in range(1, 182):
        record = parsed.get(row)
        if record is None:
            continue
        module_path, symbol = record[2].rsplit(":", 1)
        producer_basis_parts.append(f"{row:03d}\t{module_path}\t{symbol}\n")
    producer_basis = "".join(producer_basis_parts).encode("ascii")
    if len(producer_basis_parts) != 181:
        failures.append("g2f.class_a.preflight.producer_basis.rows")
    if len(producer_basis) != 14264:
        failures.append(
            f"g2f.class_a.preflight.producer_basis.bytes:{len(producer_basis)}"
        )
    if producer_basis.count(b"\n") != 181:
        failures.append("g2f.class_a.preflight.producer_basis.lf")
    if hashlib.sha256(producer_basis).hexdigest() != (
        G2F_EXECUTED_PRODUCER_BASIS_SHA256_V13
    ):
        failures.append("g2f.class_a.preflight.producer_basis.sha256")

    exact_rows = {
        27: (
            "ROOT",
            "client_memory_descent_semantic_work_request",
            "hedgehog/kernel/semantic_work_v01.py:build_semantic_work_request_v01",
            "validate_semantic_work_request_v01",
        ),
        28: (
            "ROOT",
            "client_memory_descent_evidence_binding",
            "hedgehog/kernel/semantic_work_v01.py:build_evidence_binding_v01",
            "validate_actor_contribution_v01(enclosing_public_consumer)",
        ),
        29: (
            "ROOT",
            "client_memory_descent_normalized_plan_approval_claim",
            "hedgehog/kernel/semantic_work_v01.py:build_normalized_claim_v01",
            "validate_actor_contribution_v01(enclosing_public_consumer)",
        ),
        30: (
            "ROOT",
            "client_memory_descent_actor_contribution",
            "hedgehog/kernel/semantic_work_v01.py:build_actor_contribution_v01",
            "validate_actor_contribution_v01",
        ),
        31: (
            "ROOT",
            "client_memory_descent_root_review_packet",
            "hedgehog/kernel/semantic_work_v01.py:build_root_review_packet_from_contributions_v01",
            "validate_root_review_packet_v01",
        ),
        32: (
            "ROOT",
            "client_memory_descent_root_decision_input",
            "hedgehog/kernel/root_decision_v01.py:build_root_decision_input_v01",
            "validate_root_decision_input_v01",
        ),
        33: (
            "ROOT",
            "client_memory_descent_root_decision_result",
            "hedgehog/kernel/root_decision_v01.py:decide_root_v01",
            "validate_root_decision_result_v01",
        ),
        70: (
            "G2-A",
            "public_typed_action_source",
            "hedgehog/action_commit_packet_v02.py:ActionCommitPacketV02",
            "validate_action_commit_packet_v02",
        ),
        83: (
            "ROOT",
            "packet_authorization_root_candidate_projection",
            "hedgehog/action_commit_packet_v02.py:build_root_decision_candidate_projection_v01",
            "validate_root_decision_candidate_projection_v01+validate_supplier_root_context_coherence_v01",
        ),
        99: (
            "G2-A",
            "original_packet_corridor_step",
            "hedgehog/action_commit_packet_v02.py:CorridorStepV01",
            "validate_action_packet_present_eligibility_inspection_v01(enclosing_validator_at_row103)",
        ),
        129: (
            "G2-A",
            "root_accepted_g2e_invalidation_observation",
            "hedgehog/action_commit_packet_v02.py:build_action_invalidation_evidence_v01",
            "validate_action_invalidation_evidence_v01",
        ),
        138: (
            "ROOT",
            "revocation_review_root_candidate_projection",
            "hedgehog/action_commit_packet_v02.py:build_root_decision_candidate_projection_v01",
            "validate_root_decision_candidate_projection_v01+validate_revocation_root_context_coherence_v01",
        ),
        143: (
            "G2-A",
            "revoked_packet_registry",
            "hedgehog/action_commit_packet_v02.py:record_action_packet_revocation_v01",
            "validate_action_commit_packet_registry_v02+validate_action_packet_transition_history_v01",
        ),
        153: (
            "ROOT",
            "successor_authorization_root_candidate_projection",
            "hedgehog/action_commit_packet_v02.py:build_root_decision_candidate_projection_v01",
            "validate_root_decision_candidate_projection_v01+validate_supplier_root_context_coherence_v01",
        ),
        164: (
            "ROOT",
            "supersession_review_root_candidate_projection",
            "hedgehog/action_commit_packet_v02.py:build_root_decision_candidate_projection_v01",
            "validate_root_decision_candidate_projection_v01+validate_supersession_root_context_coherence_v01",
        ),
        165: (
            "G2-A",
            "accepted_supersession_binding",
            "hedgehog/action_commit_packet_v02.py:build_accepted_supersession_binding_v01",
            "validate_accepted_supersession_binding_v01+validate_action_packet_renewal_relationship_v01",
        ),
        171: (
            "G2-A",
            "successor_activation_disposition_event",
            "hedgehog/action_commit_packet_v02.py:build_idempotency_disposition_event_v01",
            "validate_idempotency_disposition_event_v01+validate_idempotency_disposition_history_v01",
        ),
        175: (
            "G2-A",
            "successor_queued_registry",
            "hedgehog/action_commit_packet_v02.py:append_action_packet_lifecycle_transition_v01",
            "validate_action_commit_packet_registry_v02",
        ),
        179: (
            "G2-A",
            "successor_pending_registry",
            "hedgehog/action_commit_packet_v02.py:append_action_packet_lifecycle_transition_v01",
            "validate_action_commit_packet_registry_v02",
        ),
    }
    for row, expected in exact_rows.items():
        if parsed.get(row) != expected:
            failures.append(f"g2f.class_a.preflight.row_{row:03d}.exact")

    root_rows = tuple(
        row
        for row, record in sorted(parsed.items())
        if record[2].endswith(":decide_root_v01")
    )
    if root_rows != (20, 33, 82, 128, 137, 152, 163):
        failures.append("g2f.class_a.preflight.direct_root_logical_rows")

    required_artifacts = (
        "packet_authorization_actor_contribution",
        "packet_authorization_root_decision_input",
        "packet_authorization_root_decision_result",
        "invalidation_acceptance_actor_contribution",
        "invalidation_acceptance_root_decision_input",
        "invalidation_acceptance_root_decision_result",
        "revocation_review_root_decision_input",
        "revocation_review_root_decision_result",
        "revocation_review_root_candidate_projection",
        "successor_authorization_root_decision_input",
        "successor_authorization_root_decision_result",
        "successor_authorization_root_candidate_projection",
        "supersession_review_root_decision_input",
        "supersession_review_root_decision_result",
        "supersession_review_root_candidate_projection",
        "original_activation_transition_event",
        "original_queue_transition_event",
        "original_pending_transition_event",
        "fresh_revocation_transition_event",
        "successor_activation_transition_event",
        "successor_activation_disposition_event",
        "predecessor_supersession_transition_event",
    )
    for artifact in required_artifacts:
        if sum(record[1] == artifact for record in parsed.values()) != 1:
            failures.append(f"g2f.class_a.preflight.artifact_cardinality:{artifact}")
    return rows


def _validate_g2f_class_a_contract_v01(
    repo_root: Path,
    authority_index: dict[str, object] | None,
    successor_manifest: dict[str, object] | None,
    failures: list[str],
    *,
    g2f_active: bool,
) -> None:
    if not g2f_active:
        return
    try:
        source = (repo_root / G2F_PREFLIGHT_PATH).read_text(encoding="utf-8")
    except (OSError, UnicodeError) as exc:
        failures.append(f"g2f.class_a.preflight.read:{type(exc).__name__}")
        return

    for key, expected in G2F_V13_STATUS_CONTRACT.items():
        observed = re.findall(
            rf"(?m)^\s*{re.escape(key)}\s*=\s*([^\s#]+)", source
        )
        if not observed or any(value != expected for value in observed):
            failures.append(f"g2f.class_a.preflight.status:{key}")

    exact_markers = (
        "PRODUCER_BASIS_ROWS=181",
        "PRODUCER_BASIS_BYTES=14264",
        "PRODUCER_BASIS_LF=181",
        f"PRODUCER_BASIS_SHA256={G2F_EXECUTED_PRODUCER_BASIS_SHA256_V13}",
        "PRIMARY_ROW_RECEIPT_COUNT=235",
        "DIRECT_DECIDE_ROOT_RECEIPT_COUNT=8",
        "DIRECT_DECIDE_ROOT_LOGICAL_ROW_COUNT=7",
        "CAUSAL_ROW_COUNT=60",
        "CAUSAL_EDGE_COUNT=274",
        "NEW_TO_NEW_CAUSAL_EDGE_COUNT=155",
        "MISSING_CAUSAL_EDGE_COUNT=0",
        "UNEXPECTED_CAUSAL_EDGE_COUNT=0",
        f"V12R2_EVIDENCE_ARCHIVE_SHA256={G2F_V12R2_ARCHIVE_SHA256}",
        f"V12R4_EVIDENCE_ARCHIVE_SHA256={G2F_V12R4_ARCHIVE_SHA256}",
        f"V12R5_EVIDENCE_ARCHIVE_SHA256={G2F_V12R5_ARCHIVE_SHA256}",
        f"V12R6_EVIDENCE_ARCHIVE_SHA256={G2F_V12R6_ARCHIVE_SHA256}",
        f"V13_INPUT_ARCHIVE_SHA256={G2F_V13_ARCHIVE_SHA256}",
        "V13_OWNER_READINESS_STATUS=SUPERSEDED_BY_V13R1_VALIDATOR_CLOSURE",
        "V13R1_VALIDATOR_CLOSURE_STATUS=FULL_181_ROW_EXPECTED_SIDE_RECONSTRUCTED_CANDIDATE",
        "V12R6_TOTAL_EXECUTED_NEGATIVE_REGRESSION_COUNT=315",
        "SHARED_REQUEST_ID=transaction:g2f:gate2:v01",
        "PARENT_MULTIROOT_CORRELATION_ID=transaction:g2f:gate2:v01",
        "CLIENT_LOCAL_TRANSACTION_ID=CLIENT_DRS_QUERY_ID",
        "SUPPLIER_LOCAL_TRANSACTION_ID=SUPPLIER_DRS_QUERY_ID",
        "ROOT_LOCAL_TRANSACTION_CARDINALITY=2",
        "PARENT_CORRELATION_CARDINALITY=1",
        "REQUEST_TO_PARENT_CORRELATION=SAME_TOKEN_DISTINCT_FIELD_ROLES",
        "PARENT_TOKEN_USED_AS_G2C_TRANSACTION=false",
        "ROOT_SET=(root:g2f:client,root:g2f:supplier)",
        "PACKET_OWNER_ROOT=root:g2f:supplier",
        "DELTA_AFFECTED_ROOT_SET=(root:g2f:supplier)",
        "SUPERROOT_CREATED=false",
        "AGGREGATE_AUTHORITY_CREATED=false",
        "ROW129_ACCEPTANCE_ROOT_DECISION_ID=None",
        "ROW129_ACCEPTANCE_ROOT_DECISION_HASH=None",
        "ROW129_ROOT_DECISION_REF=None",
        "ROW173_AUTHORIZED_CANONICAL_SOURCE=ROW154",
        "LIFECYCLE_BRANCH_MODEL=TWO_INDEPENDENT_PROOF_BRANCHES_FROM_ROW098_PENDING_BASELINE",
        "OPEN_QUESTIONS=NONE",
    )
    for marker in exact_markers:
        if marker not in source:
            failures.append(f"g2f.class_a.preflight.marker:{marker}")

    identity = _file_identity(repo_root / G2F_PREFLIGHT_PATH)
    expected_preflight = (
        "c3b54068b43ef75cce1fc903fea654b07c6fe6e55567f721140136531b673844"
        if isinstance(successor_manifest, dict) and "g2f_landing_transition" in successor_manifest
        else G2F_PREFLIGHT_SHA256_V13
    )
    if identity is None or identity[0] != expected_preflight:
        failures.append("g2f.class_a.preflight.identity")
    _validate_g2f_class_a_ledger_v13(source, failures)

    required_relations = (
        "075->{076,077}",
        "078<-{075,077}",
        "079<-{076,077,078}",
        "080<-{076,079}",
        "081<-{075,080}",
        "082<-{081}",
        "083<-{075,081,082}",
        "Row 083 binds rows 075, 081 and 082",
        "supplier Root-context\nvalidation through "
        "`validate_supplier_root_context_coherence_v01`",
        "084<-{075,083}",
        "ROW_122 <- {ROW_005,ROW_120}",
        "ROW_123 <- {ROW_120}",
        "ROW_124 <- {ROW_075,ROW_120,ROW_123}",
        "ROW_125 <- {ROW_007,ROW_017,ROW_122,ROW_123,ROW_124}",
        "ROW_126 <- {ROW_017,ROW_122,ROW_125}",
        "ROW_127 <- {ROW_005,ROW_012,ROW_075,ROW_120,ROW_126}",
        "ROW_128 <- {ROW_012,ROW_120,ROW_127}",
        "ROW_129 <- {ROW_084,ROW_104,ROW_120,ROW_124,ROW_127,ROW_128}",
        "causal inputs compatible with {85,154,168,171}",
        "row-143 revoked registry is not a supersession-branch input",
    )
    for relation in required_relations:
        if relation not in source:
            failures.append(f"g2f.class_a.preflight.semantic_relation:{relation}")

    forbidden_active = (
        "LEDGER_ROW_PRODUCER_SYMBOL_MULTISET_PRESERVED=true",
        "ROWS_025_THROUGH_174_NUMBERING_UNCHANGED=true",
        "REPAIRED_CLASS_A_COMMITTED_POSTIMAGE_TO_BE_BOUND_EXACTLY_BEFORE_CLOSURE",
        "build_supplier_a_mock_action_commit_packet_fixture_v02|validate_action_commit_packet_v02",
        "build_supplier_a_corridor_step_fixture_v01|",
        "3550b55766bc57975bf0f5c4c865d8be6c6c90e8461b8208f9b2f0753e57eebd",
    )
    for marker in forbidden_active:
        if marker in source:
            failures.append(f"g2f.class_a.preflight.forbidden_active:{marker}")
    if "G2F_cross_stage_validator" in source:
        failures.append("g2f.class_a.preflight.nonexistent_current_validator")
    for status_failure in _g2f_status_overclaims_v02(source):
        failures.append(
            f"g2f.class_a.preflight.status_overclaim:{status_failure}"
        )

    deferred = (
        "RECONCILED_CLASS_A_COMMITTED_POSTIMAGE_TO_BE_BOUND_EXACTLY_BEFORE_CLOSURE"
    )
    for path in G2F_CLOSURE_OVERLAP_PATHS:
        if f"MODIFY {path}|{deferred}" not in source:
            failures.append(f"g2f.class_a.preflight.deferred_predecessor:{path}")
    if source.count(deferred) != 6:
        failures.append("g2f.class_a.preflight.deferred_predecessor.count")
    for boundary in (
        "ORIGINAL_CLASS_A_COMMIT_PROVENANCE",
        "CLASS_A_181_ROW_RECONCILIATION_EXACT_SEVEN_MODIFY_PATHS",
        "FUTURE_IMPLEMENTATION_EXACT_TWO_ADD_PATHS",
        "FUTURE_CLOSURE_EXACT_FOURTEEN_PATHS",
    ):
        if boundary not in source:
            failures.append(f"g2f.class_a.preflight.commit_boundary:{boundary}")
    for test_id in G2F_FOCUSED_TEST_IDS:
        if source.splitlines().count(test_id) != 1:
            failures.append(f"g2f.class_a.preflight.focused_test:{test_id}")
    for phrase in (
        "freshly run the exact committed",
        "24-node focused suite",
        "direct canonical report receipt",
        "TRACKED_REPOSITORY_BYTES_UNCHANGED",
        "IGNORED_NON_VENV_STATE_UNCHANGED",
        "GIT_INDEX_SEMANTIC_CONTENT_AND_FLAGS_UNCHANGED",
    ):
        if phrase not in source:
            failures.append(f"g2f.class_a.preflight.correction:{phrase}")

    if authority_index is None or successor_manifest is None:
        failures.append("g2f.class_a.control_plane_json_missing")
    elif isinstance(authority_index.get("current_technical_annexes"), list):
        entries = [
            entry
            for entry in authority_index["current_technical_annexes"]
            if isinstance(entry, dict) and entry.get("path") == G2F_PREFLIGHT_PATH
        ]
        if len(entries) != 1:
            failures.append("g2f.class_a.authority_index.entry_count")
        else:
            entry = entries[0]
            if entry.get("status") != (
                "accepted_g2f_v13r1_full_validator_closure_candidate"
            ):
                failures.append("g2f.class_a.authority_index.status")
            role = entry.get("role")
            for marker in (
                G2F_ORIGINAL_CLASS_A_COMMIT,
                G2F_EXECUTED_PRODUCER_BASIS_SHA256_V13,
                G2F_V12R6_ARCHIVE_SHA256,
                "row-083 structural plus supplier-root-context validator contract",
                "implementation unauthorized and unperformed",
            ):
                if not isinstance(role, str) or marker not in role:
                    failures.append(f"g2f.class_a.authority_index.role:{marker}")
    _validate_g2f_future_implementation_contract_v01(repo_root, failures)


def _validate_e6_class_a_control_plane(
    repo_root: Path,
    authority_index: dict[str, object] | None,
    successor_manifest: dict[str, object] | None,
    failures: list[str],
    *,
    closure_active: bool = False,
) -> None:
    control_identities = (
        {E6_RECONCILIATION_ANNEX_PATH: CLASS_A_CONTROL_SURFACE_IDENTITIES[
            E6_RECONCILIATION_ANNEX_PATH
        ]}
        if closure_active
        else CLASS_A_CONTROL_SURFACE_IDENTITIES
    )
    _validate_exact_identities(
        repo_root,
        control_identities,
        "e6.class_a.control_surface",
        failures,
    )
    _validate_exact_identities(
        repo_root,
        FROZEN_E5_IDENTITIES,
        "e6.committed_e5",
        failures,
    )
    _validate_exact_identities(
        repo_root,
        FROZEN_PREDECESSOR_EVIDENCE_IDENTITIES,
        "e6.frozen_predecessor_evidence",
        failures,
    )
    if closure_active:
        _validate_exact_identities(
            repo_root,
            POST_E6_CLASS_B_IDENTITIES,
            "g2e.closure.class_b",
            failures,
        )
        _validate_exact_identities(
            repo_root,
            G2E_CLOSURE_EVIDENCE_IDENTITIES,
            "g2e.closure.evidence",
            failures,
        )
        _validate_git_blob_identities_v01(
            repo_root,
            G2E_CLOSURE_BASIS_COMMIT,
            POST_E6_CONTROL_PLANE_BASIS_IDENTITIES,
            "g2e.closure.control_plane_basis",
            failures,
        )
    if CLASS_A_RECONCILIATION_PATHS & CLASS_B_E6_IMPLEMENTATION_PATHS:
        failures.append("e6.path_classes.class_a_class_b_overlap")
    if len(CLASS_A_RECONCILIATION_PATHS) != 7:
        failures.append("e6.path_classes.class_a_count")
    if len(CLASS_B_E6_IMPLEMENTATION_PATHS) != 5:
        failures.append("e6.path_classes.class_b_count")
    if len(G2E_CLASS_D_CLOSURE_PATHS) != 14:
        failures.append("g2e.closure.path_count")
    if G2E_CLASS_D_CLOSURE_PATHS & CLASS_B_E6_IMPLEMENTATION_PATHS:
        failures.append("g2e.closure.class_b_overlap")

    annex = _load_reconciliation_contract(repo_root, failures)
    _validate_reconciliation_contract(annex, failures)

    stale_markers = (
        "deferred_e5_transplant",
        "DEFERRED_UNTIL_BYTE_EXACT_TRANSPLANT",
        "frozen E5 candidate exists only",
        "three deferred E5 paths",
    )
    for relative_path in (LOCK_PATH, MANIFEST_PATH, E6_RECONCILIATION_ANNEX_PATH):
        try:
            source = (repo_root / relative_path).read_text(encoding="utf-8")
        except (OSError, UnicodeError):
            continue
        for marker in stale_markers:
            if marker in source:
                failures.append(
                    f"e6.class_a.stale_e5_current_fact:{relative_path}:{marker}"
                )

    if authority_index is not None:
        entries = authority_index.get("current_technical_annexes")
        matching = [
            entry
            for entry in entries
            if isinstance(entries, list)
            and isinstance(entry, dict)
            and entry.get("path") == E6_RECONCILIATION_ANNEX_PATH
        ] if isinstance(entries, list) else []
        if len(matching) != 1:
            failures.append("e6.class_a.annex_authority_entry.count")
        elif matching[0] != {
            "path": E6_RECONCILIATION_ANNEX_PATH,
            "status": "accepted_g2e6_sanitized_basis_reconciliation_contract",
            "current_authority": True,
            "authority_scope": NAMED_GATE_SCOPE,
            "may_override_architecture_lock": False,
            "onboarding_allowed": True,
            "role": (
                "sanitized G2-E6 profile, version, geometry, call-ownership, "
                "and phased-path reconciliation only; subordinate to the "
                "Current Architecture Lock"
            ),
        }:
            failures.append("e6.class_a.annex_authority_entry.exact")

    if successor_manifest is not None:
        onboarding_lists = (
            successor_manifest.get("always_include"),
            successor_manifest.get("include_current_gate_sources"),
            successor_manifest.get("authority_documents"),
        )
        if any(
            not isinstance(items, list)
            or E6_RECONCILIATION_ANNEX_PATH not in items
            for items in onboarding_lists
        ):
            failures.append("e6.class_a.annex_onboarding.exact")

    _validate_e5_basis_ancestry_v02(repo_root, failures)

    if closure_active:
        _validate_g2e_closure_surfaces_v01(
            repo_root,
            authority_index,
            successor_manifest,
            failures,
        )


def _validate_s2_vocabulary(repo_root: Path, failures: list[str]) -> None:
    try:
        structured_text = (repo_root / STRUCTURED_RATIONALE_PATH).read_text(
            encoding="utf-8"
        )
    except (OSError, UnicodeError) as exc:
        failures.append(
            f"s2.structured_rationale.read:{type(exc).__name__}"
        )
    else:
        for index, retired_term in enumerate(_RETIRED_STRUCTURED_POSITIVE_TERMS):
            if retired_term in structured_text:
                failures.append(
                    f"s2.structured_rationale.retired_positive:{index}"
                )

    for relative_path in SUPPLIER_EVENT_SOURCE_PATHS:
        try:
            source_text = (repo_root / relative_path).read_text(encoding="utf-8")
        except (OSError, UnicodeError) as exc:
            failures.append(
                f"s2.supplier_event.read:{relative_path}:{type(exc).__name__}"
            )
            continue
        if _RETIRED_SUPPLIER_EVENT in source_text:
            failures.append(f"s2.supplier_event.retired:{relative_path}")
        if _REQUIRED_SUPPLIER_EVENT not in source_text:
            failures.append(f"s2.supplier_event.current_missing:{relative_path}")


def _validate_deliverable_paths(
    repo_root: Path,
    failures: list[str],
    *,
    closure_active: bool = False,
    g2f_active: bool = False,
) -> None:
    required = CLASS_A_RECONCILIATION_PATHS | CLASS_B_E6_IMPLEMENTATION_PATHS
    if closure_active:
        required |= G2E_CLASS_D_CLOSURE_PATHS
    if g2f_active:
        required |= {G2F_PREFLIGHT_PATH}
    for relative_path in sorted(required):
        if not (repo_root / relative_path).is_file():
            failures.append(f"deliverable.missing:{relative_path}")


def _git_status_entries_v02(
    repo_root: Path,
    failures: list[str],
) -> tuple[tuple[str, str, str | None], ...]:
    try:
        completed = subprocess.run(
            ("git", "status", "--porcelain=v1", "-z", "--untracked-files=all"),
            cwd=repo_root,
            check=False,
            capture_output=True,
        )
    except OSError as exc:
        failures.append(f"worktree.git_status:{type(exc).__name__}")
        return ()
    if completed.returncode != 0:
        failures.append(f"worktree.git_status:exit_{completed.returncode}")
        return ()

    fields = completed.stdout.split(b"\0")
    entries: list[tuple[str, str, str | None]] = []
    index = 0
    while index < len(fields):
        record = fields[index]
        index += 1
        if not record:
            continue
        if len(record) < 4 or record[2:3] != b" ":
            failures.append("worktree.git_status:malformed_record")
            continue
        status = record[:2].decode("ascii", errors="replace")
        path = record[3:].decode("utf-8", errors="surrogateescape")
        source: str | None = None
        if "R" in status or "C" in status:
            if index >= len(fields) or not fields[index]:
                failures.append("worktree.git_status:missing_rename_source")
            else:
                source = fields[index].decode(
                    "utf-8", errors="surrogateescape"
                )
                index += 1
        entries.append((status, path, source))
    return tuple(entries)


def _git_committed_entries_v02(
    repo_root: Path,
    failures: list[str],
) -> tuple[tuple[str, str, str | None], ...]:
    try:
        completed = subprocess.run(
            (
                "git",
                "diff",
                "--name-status",
                "-z",
                "--find-renames",
                "--find-copies",
                f"{E5_IMPLEMENTATION_BASIS_COMMIT}..HEAD",
            ),
            cwd=repo_root,
            check=False,
            capture_output=True,
        )
    except OSError as exc:
        failures.append(f"e6.path_ledger.git_diff:{type(exc).__name__}")
        return ()
    if completed.returncode != 0:
        failures.append(f"e6.path_ledger.git_diff:exit_{completed.returncode}")
        return ()
    fields = [field for field in completed.stdout.split(b"\0") if field]
    entries: list[tuple[str, str, str | None]] = []
    index = 0
    while index < len(fields):
        status = fields[index].decode("ascii", errors="replace")
        index += 1
        if index >= len(fields):
            failures.append("e6.path_ledger.git_diff:malformed_record")
            break
        path = fields[index].decode("utf-8", errors="surrogateescape")
        index += 1
        source: str | None = None
        if status.startswith(("R", "C")):
            if index >= len(fields):
                failures.append("e6.path_ledger.git_diff:missing_rename_target")
                break
            source, path = path, fields[index].decode(
                "utf-8", errors="surrogateescape"
            )
            index += 1
        entries.append((status, path, source))
    return tuple(entries)


def _git_head_v02(repo_root: Path, failures: list[str]) -> str | None:
    try:
        completed = subprocess.run(
            ("git", "rev-parse", "--verify", "HEAD"),
            cwd=repo_root,
            check=False,
            capture_output=True,
            text=True,
        )
    except OSError as exc:
        failures.append(f"e6.path_ledger.git_head:{type(exc).__name__}")
        return None
    if completed.returncode != 0:
        failures.append(f"e6.path_ledger.git_head:exit_{completed.returncode}")
        return None
    head = completed.stdout.strip()
    if not re.fullmatch(r"[0-9a-f]{40}", head):
        failures.append("e6.path_ledger.git_head:invalid")
        return None
    return head


def _entry_map_v02(
    entries: Sequence[tuple[str, str, str | None]],
    *,
    label: str,
    failures: list[str],
) -> dict[str, str]:
    result: dict[str, str] = {}
    for status, path, source in entries:
        if not _valid_relative_path(path):
            failures.append(f"{label}.invalid_path:{path}")
        if source is not None:
            if not _valid_relative_path(source):
                failures.append(f"{label}.invalid_source:{source}")
            failures.append(f"{label}.rename_or_copy:{source}->{path}")
        if path in result:
            failures.append(f"{label}.duplicate_path:{path}")
        result[path] = status
    return result


def _git_single_line_v01(
    repo_root: Path,
    arguments: Sequence[str],
    code: str,
    failures: list[str],
) -> str | None:
    try:
        completed = subprocess.run(
            ("git", *arguments),
            cwd=repo_root,
            check=False,
            capture_output=True,
            text=True,
        )
    except OSError as exc:
        failures.append(f"{code}:{type(exc).__name__}")
        return None
    if completed.returncode != 0:
        failures.append(f"{code}:exit_{completed.returncode}")
        return None
    value = completed.stdout.strip()
    if not value:
        failures.append(f"{code}:empty")
        return None
    return value


def _git_name_status_entries_v01(
    repo_root: Path,
    revision_range: str,
    failures: list[str],
) -> tuple[tuple[str, str, str | None], ...]:
    try:
        completed = subprocess.run(
            (
                "git",
                "diff",
                "--name-status",
                "-z",
                "--find-renames",
                "--find-copies",
                revision_range,
            ),
            cwd=repo_root,
            check=False,
            capture_output=True,
        )
    except OSError as exc:
        failures.append(f"g2e.closure.commit_ledger:{type(exc).__name__}")
        return ()
    if completed.returncode != 0:
        failures.append(
            f"g2e.closure.commit_ledger:exit_{completed.returncode}"
        )
        return ()
    fields = [field for field in completed.stdout.split(b"\0") if field]
    entries: list[tuple[str, str, str | None]] = []
    index = 0
    while index < len(fields):
        status = fields[index].decode("ascii", errors="replace")
        index += 1
        if index >= len(fields):
            failures.append("g2e.closure.commit_ledger:malformed_record")
            break
        path = fields[index].decode("utf-8", errors="surrogateescape")
        index += 1
        source: str | None = None
        if status.startswith(("R", "C")):
            if index >= len(fields):
                failures.append(
                    "g2e.closure.commit_ledger:missing_rename_target"
                )
                break
            source, path = path, fields[index].decode(
                "utf-8", errors="surrogateescape"
            )
            index += 1
        entries.append((status, path, source))
    return tuple(entries)


def _compare_exact_ledger_v01(
    observed: dict[str, str],
    expected: dict[str, str],
    *,
    label: str,
    failures: list[str],
) -> None:
    for path in sorted(set(observed) - set(expected)):
        failures.append(f"{label}.unexpected:{path}")
    for path in sorted(set(expected) - set(observed)):
        failures.append(f"{label}.missing:{path}")
    for path in sorted(set(observed) & set(expected)):
        if observed[path] != expected[path]:
            failures.append(
                f"{label}.status:{path}:{observed[path]}!={expected[path]}"
            )


G2F_LANDING_BASIS_V01 = "779641d1a2e1c256c8232655d02124b66e3657b3"
G2F_LANDING_MAINTENANCE_PATHS_V01 = G2F_CLASS_A_PATHS
G2F_LANDING_V04_IDENTITIES_V01 = {
    "demo/run_consolidated_gate2_gauntlet_g2_f_v01.py": (
        "579ee6918220b20998ce68569787119176634e2a072dac11a770aa432cc5dd8d", 399910, 2506
    ),
    "tests/test_consolidated_gate2_gauntlet_g2_f_v01.py": (
        "6ed3b73c41fb14fd41e45ba8086043db3268bbe780e1c2e9030dd5b9802151c6", 47633, 925
    ),
}


def _g2f_landing_contract_v01() -> dict[str, object]:
    return {
        "basis_head": G2F_LANDING_BASIS_V01,
        "scope": "PROPOSED_TRANSITION_NOT_OWNER_AUTHORIZED",
        "historical_fields": "V13R1_CLASS_A_SNAPSHOT_NOT_CURRENT_LANDING_AUTHORITY",
        "maintenance_boundary": "G2F_LANDING_MAINTENANCE_EXACT_SEVEN_MODIFY_PATHS",
        "maintenance_paths": sorted(G2F_LANDING_MAINTENANCE_PATHS_V01),
        "implementation_boundary": "FUTURE_IMPLEMENTATION_EXACT_TWO_ADD_PATHS",
        "implementation_paths": sorted(G2F_IMPLEMENTATION_PATHS),
        "maintenance_generations": 1,
        "origin_rule": "EXACT_HEAD_OR_EXACT_VALIDATED_IMMEDIATE_PARENT_ONLY",
        "preserved_v04": {p: {"sha256": v[0], "bytes": v[1], "lf": v[2], "mode": "0644"} for p, v in G2F_LANDING_V04_IDENTITIES_V01.items()},
        "closure_paths_unchanged": sorted(G2F_CLOSURE_PATHS),
        "closure_predecessor_rule": "BIND_SIX_OVERLAP_BLOBS_FROM_ACTUAL_MAINTENANCE_PARENT_OF_IMPLEMENTATION_BEFORE_SEPARATE_CLOSURE",
        "authority_node_count": 943,
        "release_node_count": 32,
        "focused_node_count": 24,
        "g2f_status": "NOT_CLOSED",
        "gate2_status": "NOT_CLOSED",
    }


def _classify_g2f_path_ledger_v01(
    *,
    requested: bool,
    head: str,
    parent: str | None,
    grandparent: str | None,
    branch: str | None,
    origin_main: str | None,
    worktree_entries: Sequence[tuple[str, str, str | None]],
    head_commit_entries: Sequence[tuple[str, str, str | None]],
    parent_commit_entries: Sequence[tuple[str, str, str | None]],
    parent_count: int = 1,
    parent_parent_count: int = 1,
) -> tuple[str | None, tuple[str, ...]]:
    if not requested:
        return None, ()
    failures: list[str] = []
    worktree = _entry_map_v02(
        worktree_entries, label="g2f.worktree", failures=failures
    )
    head_commit = _entry_map_v02(
        head_commit_entries, label="g2f.head_commit", failures=failures
    )
    parent_commit = _entry_map_v02(
        parent_commit_entries, label="g2f.parent_commit", failures=failures
    )
    repair_candidate = {path: " M" for path in G2F_CLASS_A_PATHS}
    implementation_candidate = {path: "??" for path in G2F_IMPLEMENTATION_PATHS}
    if parent_count != 1:
        failures.append(f"g2f.merge_or_parent_count:{parent_count}")
    maintenance = {path: "M" for path in G2F_LANDING_MAINTENANCE_PATHS_V01}
    if head == G2F_LANDING_BASIS_V01 and set(worktree) & set(maintenance):
        mode = "G2F_LANDING_MAINTENANCE_CANDIDATE"
        if parent != G2F_ORIGINAL_CLASS_A_COMMIT or grandparent != G2F_ORIGINAL_CLASS_A_PARENT:
            failures.append("g2f.landing.basis_ancestry")
        _compare_exact_ledger_v01(head_commit, dict(G2F_CLASS_A_RECONCILIATION_COMMITTED_NAME_STATUS), label="g2f.landing.basis_commit", failures=failures)
        _compare_exact_ledger_v01(parent_commit, dict(G2F_ORIGINAL_CLASS_A_COMMITTED_NAME_STATUS), label="g2f.landing.original_commit", failures=failures)
        _compare_exact_ledger_v01(worktree, {**{p: " M" for p in maintenance}, **implementation_candidate}, label="g2f.landing.candidate.worktree", failures=failures)
        if origin_main != head:
            failures.append("g2f.landing.candidate.origin_main")
    elif parent == G2F_LANDING_BASIS_V01 and head_commit == maintenance:
        mode = "G2F_LANDING_MAINTENANCE_COMMITTED"
        if grandparent != G2F_ORIGINAL_CLASS_A_COMMIT or parent_parent_count != 1:
            failures.append("g2f.landing.maintenance.ancestry")
        _compare_exact_ledger_v01(parent_commit, dict(G2F_CLASS_A_RECONCILIATION_COMMITTED_NAME_STATUS), label="g2f.landing.maintenance.basis_commit", failures=failures)
        _compare_exact_ledger_v01(worktree, implementation_candidate, label="g2f.landing.maintenance.worktree", failures=failures)
        if origin_main not in {head, parent}:
            failures.append("g2f.landing.maintenance.origin_main")
    elif grandparent == G2F_LANDING_BASIS_V01:
        mode = "G2F_IMPLEMENTATION_COMMITTED"
        if parent_parent_count != 1:
            failures.append("g2f.landing.implementation.parent_merge")
        _compare_exact_ledger_v01(parent_commit, maintenance, label="g2f.landing.implementation.maintenance_commit", failures=failures)
        _compare_exact_ledger_v01(head_commit, dict(G2F_IMPLEMENTATION_COMMITTED_NAME_STATUS), label="g2f.landing.implementation.commit", failures=failures)
        _compare_exact_ledger_v01(worktree, {}, label="g2f.landing.implementation.worktree", failures=failures)
        if origin_main not in {head, parent}:
            failures.append("g2f.landing.implementation.origin_main")
    elif head == G2F_ORIGINAL_CLASS_A_COMMIT:
        if parent != G2F_ORIGINAL_CLASS_A_PARENT:
            failures.append("g2f.original_class_a.parent")
        _compare_exact_ledger_v01(
            head_commit,
            dict(G2F_ORIGINAL_CLASS_A_COMMITTED_NAME_STATUS),
            label="g2f.original_class_a.commit",
            failures=failures,
        )
        if parent_commit:
            failures.append("g2f.original_class_a.unexpected_parent_commit_ledger")
        if not worktree:
            mode = "G2F_ORIGINAL_CLASS_A_COMMITTED_SUPERSEDED"
        else:
            mode = "G2F_CLASS_A_181_ROW_RECONCILIATION_CANDIDATE"
            _compare_exact_ledger_v01(
                worktree,
                repair_candidate,
                label="g2f.class_a_181_reconciliation_candidate.worktree",
                failures=failures,
            )
        if origin_main != G2F_ORIGINAL_CLASS_A_COMMIT:
            failures.append("g2f.original_or_repair_candidate.origin_main")
    elif parent == G2F_ORIGINAL_CLASS_A_COMMIT:
        mode = "G2F_CLASS_A_181_ROW_RECONCILIATION_COMMITTED"
        _compare_exact_ledger_v01(
            head_commit,
            dict(G2F_CLASS_A_RECONCILIATION_COMMITTED_NAME_STATUS),
            label="g2f.class_a_181_reconciliation_committed.commit",
            failures=failures,
        )
        _compare_exact_ledger_v01(
            parent_commit,
            dict(G2F_ORIGINAL_CLASS_A_COMMITTED_NAME_STATUS),
            label="g2f.class_a_181_reconciliation_committed.original_commit",
            failures=failures,
        )
        if grandparent != G2F_ORIGINAL_CLASS_A_PARENT:
            failures.append("g2f.class_a_181_reconciliation_committed.grandparent")
        if worktree:
            mode = "G2F_IMPLEMENTATION_CANDIDATE"
            _compare_exact_ledger_v01(
                worktree,
                implementation_candidate,
                label="g2f.implementation_candidate.worktree",
                failures=failures,
            )
        if origin_main != head:
            failures.append("g2f.class_a_181_reconciliation_successor.origin_main")
    elif grandparent == G2F_ORIGINAL_CLASS_A_COMMIT:
        mode = "G2F_IMPLEMENTATION_COMMITTED"
        if parent_parent_count != 1:
            failures.append(
                f"g2f.parent_merge_or_parent_count:{parent_parent_count}"
            )
        _compare_exact_ledger_v01(
            parent_commit,
            dict(G2F_CLASS_A_RECONCILIATION_COMMITTED_NAME_STATUS),
            label="g2f.implementation_committed.repair_commit",
            failures=failures,
        )
        _compare_exact_ledger_v01(
            head_commit,
            dict(G2F_IMPLEMENTATION_COMMITTED_NAME_STATUS),
            label="g2f.implementation_committed.commit",
            failures=failures,
        )
        _compare_exact_ledger_v01(
            worktree,
            {},
            label="g2f.implementation_committed.worktree",
            failures=failures,
        )
        if origin_main != head:
            failures.append("g2f.implementation_committed.origin_main")
    else:
        mode = "G2F_INVALID"
        failures.append("g2f.unrecognized_descendant_or_basis_not_exact")
    if branch != "main":
        failures.append("g2f.branch")
    return mode, tuple(sorted(set(failures)))


def _classify_g2e_closure_path_ledger_v01(
    *,
    closure_requested: bool,
    head: str,
    parent: str | None,
    branch: str | None,
    origin_main: str | None,
    subject: str | None,
    committed_entries: Sequence[tuple[str, str, str | None]],
    worktree_entries: Sequence[tuple[str, str, str | None]],
    closure_commit_entries: Sequence[tuple[str, str, str | None]],
    g2e_closure_ancestor: bool = False,
    g2f_topology_passed: bool = False,
    g2f_pre_push_parent: str | None = None,
) -> tuple[str | None, tuple[str, ...]]:
    if not closure_requested:
        return None, ()

    failures: list[str] = []
    committed = _entry_map_v02(
        committed_entries,
        label="g2e.closure.committed",
        failures=failures,
    )
    worktree = _entry_map_v02(
        worktree_entries,
        label="g2e.closure.worktree",
        failures=failures,
    )
    closure_commit = _entry_map_v02(
        closure_commit_entries,
        label="g2e.closure.commit",
        failures=failures,
    )
    class_a_and_b = {
        **dict(CLASS_A_COMMITTED_NAME_STATUS),
        **dict(CLASS_B_COMMITTED_NAME_STATUS),
    }
    class_a_b_and_d = {
        **class_a_and_b,
        **dict(CLASS_D_COMMITTED_NAME_STATUS),
    }
    candidate_worktree = {
        path: (
            "??" if path in {G2E_AUDIT_PATH, G2E_CHECKPOINT_PATH} else " M"
        )
        for path in G2E_CLASS_D_CLOSURE_PATHS
    }

    if head == G2E_CLOSURE_BASIS_COMMIT:
        mode = "G2E_CLOSED_PASS_CANDIDATE"
        _compare_exact_ledger_v01(
            committed,
            class_a_and_b,
            label="g2e.closure.candidate.committed",
            failures=failures,
        )
        _compare_exact_ledger_v01(
            worktree,
            candidate_worktree,
            label="g2e.closure.candidate.worktree",
            failures=failures,
        )
        if closure_commit:
            failures.append("g2e.closure.candidate.unexpected_commit_ledger")
        if origin_main != G2E_CLOSURE_BASIS_COMMIT:
            failures.append("g2e.closure.candidate.origin_main")
    elif parent == G2E_CLOSURE_BASIS_COMMIT or g2e_closure_ancestor:
        mode = "G2E_CLOSED_PASS_COMMITTED"
        if g2f_topology_passed:
            committed = {
                path: status
                for path, status in committed.items()
                if path
                not in ({G2F_PREFLIGHT_PATH} | G2F_IMPLEMENTATION_PATHS)
            }
            worktree = {
                path: status
                for path, status in worktree.items()
                if path not in G2F_CLASS_A_PATHS | G2F_IMPLEMENTATION_PATHS
            }
        _compare_exact_ledger_v01(
            committed,
            class_a_b_and_d,
            label="g2e.closure.committed.cumulative",
            failures=failures,
        )
        _compare_exact_ledger_v01(
            worktree,
            {},
            label="g2e.closure.committed.worktree",
            failures=failures,
        )
        _compare_exact_ledger_v01(
            closure_commit,
            dict(CLASS_D_COMMITTED_NAME_STATUS),
            label="g2e.closure.committed.commit",
            failures=failures,
        )
        if origin_main != head and not (
            g2f_topology_passed
            and g2f_pre_push_parent is not None
            and origin_main == parent == g2f_pre_push_parent
        ):
            failures.append("g2e.closure.committed.origin_main")
        if not g2e_closure_ancestor and subject != (
            "Close G2-E continuous delta runtime lifecycle"
        ):
            failures.append("g2e.closure.committed.subject")
    else:
        mode = "G2E_CLOSED_PASS_INVALID"
        failures.append("g2e.closure.basis_not_exact")

    if branch != "main":
        failures.append("g2e.closure.branch")
    return mode, tuple(sorted(set(failures)))


def _validate_g2e_closure_topology_v01(
    repo_root: Path,
    failures: list[str],
    *,
    g2f_topology_passed: bool = False,
) -> str | None:
    head = _git_head_v02(repo_root, failures)
    if head is None:
        return None
    worktree_entries = _git_status_entries_v02(repo_root, failures)
    worktree_paths = {path for _status, path, _source in worktree_entries}
    parent_probe: list[str] = []
    parent = _git_single_line_v01(
        repo_root,
        ("rev-parse", "--verify", "HEAD^"),
        "g2e.closure.parent",
        parent_probe,
    )
    try:
        ancestor_probe = subprocess.run(
            ("git", "merge-base", "--is-ancestor", G2E_CLOSURE_COMMIT, "HEAD"),
            cwd=repo_root,
            check=False,
            capture_output=True,
        )
    except OSError as exc:
        failures.append(f"g2e.closure.ancestor:{type(exc).__name__}")
        g2e_closure_ancestor = False
    else:
        g2e_closure_ancestor = ancestor_probe.returncode == 0
        if ancestor_probe.returncode not in {0, 1}:
            failures.append(
                f"g2e.closure.ancestor:exit_{ancestor_probe.returncode}"
            )
    closure_requested = (
        head == G2E_CLOSURE_BASIS_COMMIT
        and bool(worktree_paths & G2E_CLASS_D_CLOSURE_PATHS)
    ) or parent == G2E_CLOSURE_BASIS_COMMIT or g2e_closure_ancestor or any(
        (repo_root / path).exists()
        for path in (G2E_AUDIT_PATH, G2E_CHECKPOINT_PATH)
    )
    if not closure_requested:
        return None
    failures.extend(parent_probe)
    branch = _git_single_line_v01(
        repo_root,
        ("branch", "--show-current"),
        "g2e.closure.branch",
        failures,
    )
    origin_main = _git_single_line_v01(
        repo_root,
        ("rev-parse", "--verify", "refs/remotes/origin/main"),
        "g2e.closure.origin_main",
        failures,
    )
    subject = _git_single_line_v01(
        repo_root,
        ("show", "-s", "--format=%s", "HEAD"),
        "g2e.closure.subject",
        failures,
    )
    committed_entries = _git_committed_entries_v02(repo_root, failures)
    closure_commit_entries = (
        _git_name_status_entries_v01(
            repo_root,
            (
                f"{G2E_CLOSURE_BASIS_COMMIT}..{G2E_CLOSURE_COMMIT}"
                if g2e_closure_ancestor
                else f"{G2E_CLOSURE_BASIS_COMMIT}..HEAD"
            ),
            failures,
        )
        if parent == G2E_CLOSURE_BASIS_COMMIT or g2e_closure_ancestor
        else ()
    )
    # Derive the exception from a second successful exact F topology check,
    # never from a caller-supplied ancestor or an origin ref alone.
    pre_push_parent = None
    if g2f_topology_passed and origin_main != head:
        f_failures: list[str] = []
        f_mode = _validate_g2f_topology_v01(repo_root, f_failures)
        if not f_failures and f_mode in {
            "G2F_LANDING_MAINTENANCE_COMMITTED", "G2F_IMPLEMENTATION_COMMITTED"
        } and origin_main == parent:
            pre_push_parent = parent
    mode, topology_failures = _classify_g2e_closure_path_ledger_v01(
        closure_requested=True,
        head=head,
        parent=parent,
        branch=branch,
        origin_main=origin_main,
        subject=subject,
        committed_entries=committed_entries,
        worktree_entries=worktree_entries,
        closure_commit_entries=closure_commit_entries,
        g2e_closure_ancestor=g2e_closure_ancestor,
        g2f_topology_passed=g2f_topology_passed,
        g2f_pre_push_parent=pre_push_parent,
    )
    failures.extend(topology_failures)
    for marker in (
        "MERGE_HEAD",
        "REBASE_HEAD",
        "CHERRY_PICK_HEAD",
        "REVERT_HEAD",
        "BISECT_LOG",
        "rebase-merge",
        "rebase-apply",
        "sequencer",
    ):
        git_path = _git_single_line_v01(
            repo_root,
            ("rev-parse", "--git-path", marker),
            f"g2e.closure.git_operation_path:{marker}",
            failures,
        )
        if git_path is not None:
            operation_path = Path(git_path)
            if not operation_path.is_absolute():
                operation_path = repo_root / operation_path
            if operation_path.exists():
                failures.append(f"g2e.closure.git_operation_active:{marker}")
    return mode


def _validate_g2f_topology_v01(
    repo_root: Path,
    failures: list[str],
) -> str | None:
    head = _git_head_v02(repo_root, failures)
    if head is None:
        return None
    worktree_entries = _git_status_entries_v02(repo_root, failures)
    worktree_paths = {path for _status, path, _source in worktree_entries}
    parent_failures: list[str] = []
    parent = _git_single_line_v01(
        repo_root,
        ("rev-parse", "--verify", "HEAD^"),
        "g2f.parent",
        parent_failures,
    )
    grandparent = _git_single_line_v01(
        repo_root,
        ("rev-parse", "--verify", "HEAD^^"),
        "g2f.grandparent",
        parent_failures,
    )
    parent_line = _git_single_line_v01(
        repo_root,
        ("rev-list", "--parents", "-n", "1", "HEAD"),
        "g2f.parent_count",
        parent_failures,
    )
    parent_count = (
        len(parent_line.split()) - 1 if parent_line is not None else 0
    )
    parent_parent_count = 1
    if grandparent in {G2F_ORIGINAL_CLASS_A_COMMIT, G2F_LANDING_BASIS_V01} and parent is not None:
        parent_parent_line = _git_single_line_v01(
            repo_root,
            ("rev-list", "--parents", "-n", "1", parent),
            "g2f.parent_parent_count",
            parent_failures,
        )
        parent_parent_count = (
            len(parent_parent_line.split()) - 1
            if parent_parent_line is not None
            else 0
        )
    try:
        ancestor_probe = subprocess.run(
            ("git", "merge-base", "--is-ancestor", G2E_CLOSURE_COMMIT, "HEAD"),
            cwd=repo_root,
            check=False,
            capture_output=True,
        )
    except OSError as exc:
        parent_failures.append(f"g2f.ancestor:{type(exc).__name__}")
        g2f_descendant = False
    else:
        if ancestor_probe.returncode not in {0, 1}:
            parent_failures.append(
                f"g2f.ancestor:exit_{ancestor_probe.returncode}"
            )
        g2f_descendant = (
            head != G2E_CLOSURE_COMMIT and ancestor_probe.returncode == 0
        )
    requested = (
        (head == G2E_CLOSURE_COMMIT and bool(worktree_paths & G2F_CLASS_A_PATHS))
        or (repo_root / G2F_PREFLIGHT_PATH).exists()
        or bool(worktree_paths & G2F_IMPLEMENTATION_PATHS)
        or parent == G2E_CLOSURE_COMMIT
        or grandparent == G2E_CLOSURE_COMMIT
        or g2f_descendant
    )
    if not requested:
        return None
    failures.extend(parent_failures)
    original_parent = _git_single_line_v01(
        repo_root,
        ("rev-parse", "--verify", f"{G2F_ORIGINAL_CLASS_A_COMMIT}^"),
        "g2f.original_class_a.parent",
        failures,
    )
    if original_parent != G2F_ORIGINAL_CLASS_A_PARENT:
        failures.append("g2f.original_class_a.parent_exact")
    original_parent_line = _git_single_line_v01(
        repo_root,
        ("rev-list", "--parents", "-n", "1", G2F_ORIGINAL_CLASS_A_COMMIT),
        "g2f.original_class_a.parent_count",
        failures,
    )
    if original_parent_line is None or len(original_parent_line.split()) != 2:
        failures.append("g2f.original_class_a.parent_count_exact")
    original_commit_entries = _git_name_status_entries_v01(
        repo_root,
        f"{G2F_ORIGINAL_CLASS_A_PARENT}..{G2F_ORIGINAL_CLASS_A_COMMIT}",
        failures,
    )
    original_commit_ledger = _entry_map_v02(
        original_commit_entries,
        label="g2f.original_class_a.committed",
        failures=failures,
    )
    _compare_exact_ledger_v01(
        original_commit_ledger,
        dict(G2F_ORIGINAL_CLASS_A_COMMITTED_NAME_STATUS),
        label="g2f.original_class_a.committed",
        failures=failures,
    )
    _validate_git_blob_identities_v01(
        repo_root,
        G2F_ORIGINAL_CLASS_A_COMMIT,
        G2F_ORIGINAL_CLASS_A_POSTIMAGE_IDENTITIES,
        "g2f.original_class_a.blobs",
        failures,
    )
    branch = _git_single_line_v01(
        repo_root,
        ("branch", "--show-current"),
        "g2f.branch",
        failures,
    )
    origin_main = _git_single_line_v01(
        repo_root,
        ("rev-parse", "--verify", "refs/remotes/origin/main"),
        "g2f.origin_main",
        failures,
    )
    head_commit_entries = (
        _git_name_status_entries_v01(repo_root, f"{parent}..HEAD", failures)
        if parent is not None and head != G2E_CLOSURE_COMMIT
        else ()
    )
    parent_commit_entries = (
        _git_name_status_entries_v01(
            repo_root, f"{grandparent}..{parent}", failures
        )
        if (
            grandparent is not None
            and parent is not None
            and grandparent
            in {G2E_CLOSURE_COMMIT, G2F_ORIGINAL_CLASS_A_COMMIT, G2F_LANDING_BASIS_V01}
        )
        else ()
    )
    mode, topology_failures = _classify_g2f_path_ledger_v01(
        requested=True,
        head=head,
        parent=parent,
        grandparent=grandparent,
        branch=branch,
        origin_main=origin_main,
        worktree_entries=worktree_entries,
        head_commit_entries=head_commit_entries,
        parent_commit_entries=parent_commit_entries,
        parent_count=parent_count,
        parent_parent_count=parent_parent_count,
    )
    failures.extend(topology_failures)
    if (
        mode in {"G2F_LANDING_MAINTENANCE_CANDIDATE", "G2F_LANDING_MAINTENANCE_COMMITTED"}
        or grandparent == G2F_LANDING_BASIS_V01
        or parent == G2F_LANDING_BASIS_V01
        or (head == G2F_LANDING_BASIS_V01 and bool(worktree_paths & G2F_IMPLEMENTATION_PATHS))
    ):
        for path, expected in G2F_LANDING_V04_IDENTITIES_V01.items():
            file = repo_root / path
            if file.is_symlink() or not file.is_file() or file.stat().st_mode & 0o777 != 0o644:
                failures.append(f"g2f.landing.v04.type_mode:{path}")
                continue
            body = file.read_bytes()
            if (hashlib.sha256(body).hexdigest(), len(body), body.count(b"\n")) != expected:
                failures.append(f"g2f.landing.v04.identity:{path}")
        if mode == "G2F_IMPLEMENTATION_COMMITTED":
            _validate_git_blob_identities_v01(repo_root, "HEAD", G2F_LANDING_V04_IDENTITIES_V01, "g2f.landing.v04.committed", failures)
            implementation_tree = subprocess.run(("git", "ls-tree", "-r", "HEAD", "--", *sorted(G2F_IMPLEMENTATION_PATHS)), cwd=repo_root, capture_output=True, text=True, check=False)
            if implementation_tree.returncode or len(implementation_tree.stdout.splitlines()) != 2 or any(not line.startswith("100644 blob ") for line in implementation_tree.stdout.splitlines()):
                failures.append("g2f.landing.v04.committed_mode")
        # A mode-only or path-only proposal must not admit symlinks or mode drift.
        for path in G2F_LANDING_MAINTENANCE_PATHS_V01:
            file = repo_root / path
            if file.is_symlink() or not file.is_file() or file.stat().st_mode & 0o777 != 0o644:
                failures.append(f"g2f.landing.control.type_mode:{path}")
        for revision in ("HEAD", "HEAD^"):
            tree = subprocess.run(("git", "ls-tree", "-r", revision, "--", *sorted(G2F_LANDING_MAINTENANCE_PATHS_V01)), cwd=repo_root, capture_output=True, text=True, check=False)
            if tree.returncode or len(tree.stdout.splitlines()) != 7 or any(not line.startswith("100644 blob ") for line in tree.stdout.splitlines()):
                failures.append(f"g2f.landing.control.committed_mode:{revision}")
    return mode


def _classify_phase_path_ledger_v02(
    *,
    head: str,
    phase: str | None,
    committed_entries: Sequence[tuple[str, str, str | None]],
    worktree_entries: Sequence[tuple[str, str, str | None]],
) -> tuple[str, ...]:
    failures: list[str] = []
    committed = _entry_map_v02(
        committed_entries,
        label="e6.path_ledger.committed",
        failures=failures,
    )
    worktree = _entry_map_v02(
        worktree_entries,
        label="e6.path_ledger.worktree",
        failures=failures,
    )
    class_a = dict(CLASS_A_COMMITTED_NAME_STATUS)
    class_b = dict(CLASS_B_COMMITTED_NAME_STATUS)
    class_a_and_b = {**class_a, **class_b}

    expected_committed: dict[str, str]
    expected_worktree: dict[str, str]
    if head == E5_IMPLEMENTATION_BASIS_COMMIT and phase == "PRE_E6_RECONCILED":
        expected_committed = {}
        expected_worktree = class_a
    elif head != E5_IMPLEMENTATION_BASIS_COMMIT and phase == "PRE_E6_RECONCILED":
        expected_committed = class_a
        expected_worktree = {}
    elif head != E5_IMPLEMENTATION_BASIS_COMMIT and phase == "POST_E6_SUCCESSOR":
        if worktree:
            expected_committed = class_a
            expected_worktree = class_b
        else:
            expected_committed = class_a_and_b
            expected_worktree = {}
    else:
        expected_committed = {}
        expected_worktree = {}
        failures.append("e6.path_ledger.phase_head_combination")

    for path in sorted(set(committed) - set(expected_committed)):
        failures.append(f"e6.path_ledger.committed_unexpected:{path}")
    for path in sorted(set(expected_committed) - set(committed)):
        failures.append(f"e6.path_ledger.committed_missing:{path}")
    for path in sorted(set(committed) & set(expected_committed)):
        if committed[path] != expected_committed[path]:
            failures.append(
                f"e6.path_ledger.committed_status:{path}:"
                f"{committed[path]}!={expected_committed[path]}"
            )

    for path in sorted(set(worktree) - set(expected_worktree)):
        failures.append(f"worktree.unexpected_changed_path:{path}")
    for path in sorted(set(expected_worktree) - set(worktree)):
        failures.append(f"e6.path_ledger.worktree_missing:{path}")
    for path in sorted(set(worktree) & set(expected_worktree)):
        expected_kind = expected_worktree[path]
        permitted = (
            {"??", "A "}
            if expected_kind == "A"
            else {" M", "M "}
        )
        if worktree[path] not in permitted:
            failures.append(
                f"e6.path_ledger.worktree_status:{path}:{worktree[path]}"
            )
    return tuple(sorted(set(failures)))


def _validate_phase_path_ledger_v02(
    repo_root: Path,
    phase: str | None,
    failures: list[str],
) -> None:
    head = _git_head_v02(repo_root, failures)
    committed = _git_committed_entries_v02(repo_root, failures)
    worktree = _git_status_entries_v02(repo_root, failures)
    if head is None:
        return
    failures.extend(
        _classify_phase_path_ledger_v02(
            head=head,
            phase=phase,
            committed_entries=committed,
            worktree_entries=worktree,
        )
    )


def _validate_changed_paths(
    changed_paths: Iterable[str],
    _unused_manifest_paths: Iterable[str],
    failures: list[str],
) -> None:
    """Compatibility helper; production acceptance uses the phase ledger."""

    allowed = (
        CLASS_A_RECONCILIATION_PATHS
        | CLASS_B_E6_IMPLEMENTATION_PATHS
        | G2E_CLASS_D_CLOSURE_PATHS
        | G2F_CLASS_A_PATHS
        | G2F_IMPLEMENTATION_PATHS
    )
    for path in sorted(set(changed_paths)):
        if not _valid_relative_path(path) or path not in allowed:
            failures.append(f"worktree.unexpected_changed_path:{path}")


def collect_failures(
    repo_root: Path,
) -> tuple[str, ...]:
    """Return deterministic validation failures for ``repo_root``."""

    root = repo_root.resolve()
    failures: list[str] = []
    g2f_topology_failures: list[str] = []
    g2f_mode = _validate_g2f_topology_v01(root, g2f_topology_failures)
    g2f_active = g2f_mode is not None
    g2f_topology_passed = g2f_active and not g2f_topology_failures
    failures.extend(g2f_topology_failures)
    closure_mode = _validate_g2e_closure_topology_v01(
        root,
        failures,
        g2f_topology_passed=g2f_topology_passed,
    )
    closure_active = closure_mode is not None
    authority_index = _load_json(root / INDEX_PATH, "authority_index", failures)
    successor_manifest = _load_json(
        root / MANIFEST_PATH, "successor_manifest", failures
    )
    landing_present = isinstance(successor_manifest, dict) and "g2f_landing_transition" in successor_manifest
    landing_required = g2f_mode in {
        "G2F_LANDING_MAINTENANCE_CANDIDATE", "G2F_LANDING_MAINTENANCE_COMMITTED"
    } or (g2f_mode == "G2F_IMPLEMENTATION_COMMITTED" and _git_single_line_v01(root, ("rev-parse", "HEAD^^"), "g2f.landing.grandparent", failures) == G2F_LANDING_BASIS_V01)
    if landing_present or landing_required:
        expected_landing = _g2f_landing_contract_v01()
        for label, document in (("manifest", successor_manifest), ("authority_index", authority_index)):
            if not isinstance(document, dict) or document.get("g2f_landing_transition") != expected_landing:
                failures.append(f"g2f.landing.{label}.contract")
        lock = (root / LOCK_PATH).read_text(encoding="utf-8")
        if "G2F_LANDING_MAINTENANCE_EXACT_SEVEN_MODIFY_PATHS" not in lock or "PROPOSED_TRANSITION_NOT_OWNER_AUTHORIZED" not in lock:
            failures.append("g2f.landing.architecture_lock.contract")
    retired_inventory = _load_json(
        root / RETIRED_INVENTORY_PATH, "s3.retired_inventory", failures
    )
    current_schema_surface = _load_json(
        root / CURRENT_SCHEMA_SURFACE_PATH,
        "s3.current_schema_surface",
        failures,
    )
    completion_manifest = _load_json(
        root / COMPLETION_MANIFEST_PATH, "s3.release.completion", failures
    )
    seam_index = _load_json(
        root / SEAM_INDEX_PATH, "s3.release.seam_index", failures
    )
    historical_entries = _validate_authority_index(
        authority_index,
        failures,
        closure_active=closure_active,
        g2f_active=g2f_active,
    )
    historical_paths = {
        entry.get("path")
        for entry in historical_entries
        if isinstance(entry.get("path"), str)
    }
    onboarding_paths, _manifest_allowed_changed_paths = _validate_manifest(
        successor_manifest,
        failures,
        historical_paths,
        closure_active=closure_active,
        g2f_active=g2f_active,
    )
    _validate_e6_class_a_control_plane(
        root,
        authority_index,
        successor_manifest,
        failures,
        closure_active=closure_active,
    )
    _validate_g2f_class_a_contract_v01(
        root,
        authority_index,
        successor_manifest,
        failures,
        g2f_active=g2f_active,
    )
    _validate_s3_inventory(root, retired_inventory, failures)
    _validate_current_schema_surface(root, current_schema_surface, failures)
    _validate_release_succession(completion_manifest, seam_index, failures)
    _validate_conformance_profiles(
        root,
        failures,
        closure_active=closure_active,
    )
    _validate_current_import_graph(root, onboarding_paths, failures)
    _validate_committed_e5_content(root, failures)
    _validate_current_documents(
        root,
        failures,
        closure_active=closure_active,
    )
    _validate_s2_vocabulary(root, failures)
    _validate_deliverable_paths(
        root,
        failures,
        closure_active=closure_active,
        g2f_active=g2f_active,
    )
    return tuple(sorted(set(failures)))


def _build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Check the active Hedgehog OS architecture authority boundary."
    )
    parser.add_argument(
        "--root",
        type=Path,
        default=Path(__file__).resolve().parents[1],
        help="repository root (defaults to the parent of tools/)",
    )
    return parser


def main(arguments: Sequence[str] | None = None) -> int:
    args = _build_parser().parse_args(arguments)
    failures = collect_failures(args.root)
    if not failures:
        print("ACTIVE_ARCHITECTURE_AUTHORITY_V01 PASS")
        closure_failures: list[str] = []
        closure_mode = _validate_g2e_closure_topology_v01(
            args.root.resolve(), closure_failures
        )
        if closure_mode in {
            "G2E_CLOSED_PASS_CANDIDATE",
            "G2E_CLOSED_PASS_COMMITTED",
        }:
            print("CURRENT_PHASE=POST_E6_SUCCESSOR")
            print("LIFECYCLE_PHASE=G2E_CLOSED_PASS")
            print(f"LIFECYCLE_MODE={closure_mode}")
        g2f_failures: list[str] = []
        g2f_mode = _validate_g2f_topology_v01(
            args.root.resolve(), g2f_failures
        )
        if g2f_mode is not None:
            print(f"G2F_PHASE={g2f_mode}")
        return 0
    print("ACTIVE_ARCHITECTURE_AUTHORITY_V01 FAIL")
    for failure in failures:
        print(f"FAIL {failure}")
    return 1


if __name__ == "__main__":
    raise SystemExit(main())
