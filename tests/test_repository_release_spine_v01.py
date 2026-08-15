from __future__ import annotations

import copy
import hashlib
import json
from pathlib import Path
import re
import subprocess
import tomllib


REPOSITORY_ROOT = Path(__file__).resolve().parents[1]
AGENTS_PATH = REPOSITORY_ROOT / "AGENTS.md"
README_PATH = REPOSITORY_ROOT / "README.md"
HUMAN_PASSPORT_PATH = REPOSITORY_ROOT / "specs/human_passport_v0_25.md"
MATH_APPENDIX_PATH = REPOSITORY_ROOT / "specs/math_appendix_v0_3.md"
MANIFEST_PATH = REPOSITORY_ROOT / "specs/machine_manifest_v0_25.json"
OVERLAY_PATH = REPOSITORY_ROOT / "release/current_status_overlay_v01.json"
CLAIM_INDEX_PATH = REPOSITORY_ROOT / "release/claim_to_evidence_index.md"
LIMITATIONS_PATH = REPOSITORY_ROOT / "release/current_limitations.md"
NOTES_PATH = REPOSITORY_ROOT / "release/current_release_notes.md"
ROADMAP_PATH = REPOSITORY_ROOT / (
    "specs/future/quantum/"
    "hedgehog_quantum_mathematical_extension_roadmap_v2_0.md"
)

ACCEPTED_PRE_R_H1_BASE_COMMIT = (
    "3785d67e9d33adf145a3f6f60981abf38767b25d"
)
ACCEPTED_PREFLIGHT_COMMIT = "df6b4904594a84519a3056e77d2af5a9eb743185"
ACCEPTED_MANIFEST_SHA256 = (
    "880cc7066e6aedbd9157bf860dcfec7836c8d9f7fb61b92e4262d30b6801aa66"
)

README_BEGIN_MARKER = "<!-- BEGIN HEDGEHOG CURRENT ENGINEERING BOUNDARY -->"
README_END_MARKER = "<!-- END HEDGEHOG CURRENT ENGINEERING BOUNDARY -->"
AGENTS_BEGIN_MARKER = (
    "Current checkpoint: R-H1 Clean-Clone, Licensing, and Release-Spine "
    "Reconciliation CLOSED_PASS."
)
AGENTS_CURRENT_BEGIN_MARKER = (
    "Current checkpoint: G2-C ExecutionModeRouter CLOSED_PASS."
)
AGENTS_G2D_CURRENT_BEGIN_MARKER = (
    "Current checkpoint: G2-D v0.3.7 observed-work correction CLOSED_PASS."
)
AGENTS_END_MARKER = "## Root-centered capability geometry"

G2C_ACCEPTED_PREFLIGHT_COMMIT = (
    "4b33c8106dbb3d7b50596630cd9dcdcf3f84cfac"
)
G2C_ACCEPTED_PREFLIGHT_PATH = (
    "docs/execution_mode_router_g2_c_preflight_v01.md"
)
G2C_ACCEPTED_PREFLIGHT_SHA256 = (
    "5bea2e49a6a5ff1c80df526a142329e7e218558f64c77be0a2f64294f2673077"
)
G2C_IMPLEMENTATION_BASIS_COMMIT = (
    "27a866ca06a331b4169c56abac9a460334d75539"
)
G2C_AUDIT_COMMIT = "72854bcdc85d19e9c6a6636f9a7eedd1929f03cb"
G2C_AUDIT_COMMIT_BASELINE = G2C_AUDIT_COMMIT
G2C_AUDIT_PATH = (
    "docs/audit_reports/auditor_execution_mode_router_g2_c_v01.log"
)
G2C_AUDIT_SHA256 = (
    "3f6aab5c26b486a463174a6d57a22097b8eee2dcd314433b27462117b21d73d5"
)
G2C_CHECKPOINT_PATH = "docs/execution_mode_router_g2_c_checkpoint_v01.md"
G2C_CHECKPOINT_SHA256 = (
    "28ba0de21cf6458a408911b0342d57db72ad6f6cf6e8e5aec8b87fb616802f0b"
)
G2C_CLOSURE_COMMIT = "5d1c64942ec141a65ac6be9cb469d428a3cca73d"
G2C_CLOSURE_PARENT = G2C_AUDIT_COMMIT
G2C_CLOSURE_SUBJECT = "Close G2-C ExecutionModeRouter"
G2C_CLOSURE_CLAIM_ID = "claim_g2c_execution_mode_router_closed_pass"
G2C_CLOSURE_CLAIM_WORDING = (
    "Gate 2 slice G2-C ExecutionModeRouter is CLOSED_PASS."
)

G2D_ACCEPTED_PREFLIGHT_COMMIT = (
    "2e1681a54c847beb106d9e57da250dac82ea6192"
)
G2D_ACCEPTED_PREFLIGHT_PATH = (
    "docs/fractal_runtime_v0_2_g2_d_preflight_v01.md"
)
G2D_ACCEPTED_PREFLIGHT_SHA256 = (
    "8e3ae3b04a9b622329e85529edb8a150739cc787b341f1609438dbde00412e79"
)
G2D_ACCEPTED_ADDENDUM_PATH = (
    "docs/fractal_runtime_v0_2_g2_d_post_acceptance_contract_addendum_v01.md"
)
G2D_ACCEPTED_ADDENDUM_SHA256 = (
    "29983cd17cbefe306de32cf045827fc927280bae5fdb0d7c9db50203a0ea6511"
)
G2D_ACCEPTED_NORMATIVE_DONOR_SHA256 = (
    "8801e413f93765cc7059ce5e03e82e881b20cfd193f12551a60a0b90920bb63d"
)
G2D_PRECORRECTION_ACCEPTED_ADDENDUM_SHA256 = (
    "7e3a9039e04a7ef2b20cd69ac442ad62c073e88d7d3b93c26f35b48b18d67570"
)
G2D_PRECORRECTION_TEST_SHA256 = (
    "0ed20add36a82a576cf5e4ce9d787079c6052bf24465b225c18d2c33303416e7"
)
G2D_IMPLEMENTATION_BASIS_COMMIT = (
    "5e5d565eb6c2088db995cf9e5b3ccb0743f1c9cd"
)
G2D_AUDIT_COMMIT = "c0dc618a0b693fe55435f17a025789267bcb79ff"
G2D_AUDIT_PATH = "docs/audit_reports/auditor_fractal_runtime_g2_d_v02.log"
G2D_AUDIT_SHA256 = (
    "ccc367ac92ad02e005c7968d152bf7810a772db94dd671e26e5d27f30d2d72aa"
)
G2D_HISTORICAL_CHECKPOINT_PATH = (
    "docs/fractal_runtime_v0_2_g2_d_checkpoint_v01.md"
)
G2D_HISTORICAL_CHECKPOINT_SHA256 = (
    "f5bb19741ee992605ed772a282f4374bc3949508052edb09c8b3fdbbf210c1de"
)
G2D_CORRECTED_IMPLEMENTATION_COMMIT = (
    "27c6dfd10740103cddc13bac3ce35f917b5f30c5"
)
G2D_CORRECTED_IMPLEMENTATION_PARENT = (
    "3dcaabb7a231259c488643a652b92ee03d7faf52"
)
G2D_CORRECTED_IMPLEMENTATION_PATCH_SHA256 = (
    "be594af310b2d13baf0e45283944bd68f56461126b6aa3fbbcaff541a58a0279"
)
G2D_OWNER_EVIDENCE_BUNDLE_SHA256 = (
    "e49752fcd1c19dfe8ddf55a254b2d97f8c27688bc0c2371b6ad4ffe2ec5c9cdd"
)
G2D_INDEPENDENT_REAUDIT_COMMIT = (
    "2eccb604fee89d7e79025337d3858d6dbfea5fbc"
)
G2D_INDEPENDENT_REAUDIT_PATH = (
    "docs/audit_reports/"
    "auditor_fractal_runtime_g2_d_v037_observed_work_correction_v01.log"
)
G2D_INDEPENDENT_REAUDIT_SHA256 = (
    "c31d1712593184317b03425c57c5fcebf19532cbfc3086981223bf32afd0e8a3"
)
G2D_CHECKPOINT_PATH = (
    "docs/fractal_runtime_v0_2_g2_d_observed_work_correction_checkpoint_v01.md"
)
G2D_CHECKPOINT_SHA256 = (
    "606d9f1c516ddbe86ec63fe93fc2126ae69bfbf3f8169879a6c1933162296677"
)
G2D_CLOSURE_CLAIM_ID = "claim_g2d_fractal_runtime_v0_2_closed_pass"
G2D_CLOSURE_CLAIM_WORDING = (
    "Historical pre-correction Gate 2 slice G2-D Fractal Runtime v0.2 is "
    "CLOSED_PASS_ON_PRECORRECTION_BYTES."
)
G2D_ACTIVE_CONTRACT_CLAIM_ID = (
    "claim_g2d_v037_corrected_implementation_reaudit_pending"
)
G2D_ACTIVE_CONTRACT_CLAIM_WORDING = (
    "Gate 2 slice G2-D v0.3.7 corrected implementation is commit-ready "
    "with independent re-audit pending."
)
G2D_CORRECTED_CLOSURE_CLAIM_ID = (
    "claim_g2d_v037_observed_work_correction_closed_pass"
)
G2D_CORRECTED_CLOSURE_CLAIM_WORDING = (
    "Gate 2 slice G2-D Fractal Runtime v0.2 with the accepted v0.3.7 "
    "observed-work correction is CLOSED_PASS."
)
G2D_CLOSURE_SUBJECT = "Close G2-D v0.3.7 observed-work correction"
G2D_CLOSURE_PARENT = G2D_INDEPENDENT_REAUDIT_COMMIT

G2D_CLOSURE_PATHS = (
    "AGENTS.md",
    "README.md",
    "docs/fractal_runtime_v0_2_g2_d_observed_work_correction_checkpoint_v01.md",
    "release/claim_to_evidence_index.md",
    "release/current_limitations.md",
    "release/current_release_notes.md",
    "release/current_status_overlay_v01.json",
    "specs/machine_manifest_v0_25.json",
    "tests/test_repository_release_spine_v01.py",
)

G2D_CURRENT_BOUNDARY_FIELDS = {
    "g2d_status": "CLOSED_PASS",
    "g2d_correction_implementation_authorized": True,
    "g2d_corrected_implementation_exists": True,
    "g2d_contract_only_claim": False,
    "g2d_corrected_runtime_acceptance_claimed": True,
    "g2d_corrected_implementation_committed": True,
    "g2d_corrected_implementation_commit": G2D_CORRECTED_IMPLEMENTATION_COMMIT,
    "g2d_corrected_implementation_patch_sha256": (
        G2D_CORRECTED_IMPLEMENTATION_PATCH_SHA256
    ),
    "g2d_corrected_owner_evidence_bundle_sha256": (
        G2D_OWNER_EVIDENCE_BUNDLE_SHA256
    ),
    "g2d_independent_reaudit_required": True,
    "g2d_independent_reaudit_passed": True,
    "g2d_independent_reaudit_commit": G2D_INDEPENDENT_REAUDIT_COMMIT,
    "g2d_independent_reaudit_path": G2D_INDEPENDENT_REAUDIT_PATH,
    "g2d_independent_reaudit_sha256": G2D_INDEPENDENT_REAUDIT_SHA256,
    "g2d_additive_reclosure_required": True,
    "g2d_additive_reclosure_completed": True,
    "g2d_corrected_closure_claimed": True,
    "g2d_corrected_checkpoint_path": G2D_CHECKPOINT_PATH,
    "g2d_corrected_checkpoint_sha256": G2D_CHECKPOINT_SHA256,
    "g2d_corrected_closure_commit_identity": "NOT_SELF_RECORDED",
    "g2d_old_audit_checkpoint_class": "HISTORICAL_PRECORRECTION_EVIDENCE",
    "g2d_accepted_normative_donor_sha256": G2D_ACCEPTED_NORMATIVE_DONOR_SHA256,
    "g2d_accepted_repository_addendum_sha256": G2D_ACCEPTED_ADDENDUM_SHA256,
    "g2d_historical_precorrection_status": "CLOSED_PASS_ON_PRECORRECTION_BYTES",
    "g2d_historical_precorrection_implementation_basis_commit": (
        G2D_IMPLEMENTATION_BASIS_COMMIT
    ),
    "g2d_historical_precorrection_audit_commit": G2D_AUDIT_COMMIT,
    "g2d_historical_precorrection_audit_path": G2D_AUDIT_PATH,
    "g2d_historical_precorrection_audit_sha256": G2D_AUDIT_SHA256,
    "g2d_historical_precorrection_checkpoint_path": (
        G2D_HISTORICAL_CHECKPOINT_PATH
    ),
    "g2d_historical_precorrection_checkpoint_sha256": (
        G2D_HISTORICAL_CHECKPOINT_SHA256
    ),
    "g2d_historical_precorrection_evidence_only": True,
    "g2e3_status": "REVALIDATION_PENDING_ON_CORRECTED_G2D",
    "g2e3_post_corrected_g2d_landing_status": (
        "REVALIDATION_PENDING_ON_CORRECTED_G2D"
    ),
    "g2e4_status": "NOT_STARTED_NOT_AUTHORIZED",
}

G2D_FROZEN_IMPLEMENTATION_SHA256 = {
    "hedgehog/kernel/fractal_runtime_v02.py": (
        "0788ae1a8d46093c0094aa338081625fd92bd744288f1c79a98a764a63b4aa9b"
    ),
    "schemas/fractal_runtime_v02.schema.json": (
        "a70ea31721a08c9edaaeb7c7aa6a91abb2e6c92b408fd72f22f1165b4baef4e8"
    ),
    "tests/test_fractal_runtime_g2_d_v02.py": (
        "52da16aea1929bd7039e1222c27f1841c65388fcf5f123ff372957f0f82d694a"
    ),
    "demo/run_fractal_runtime_g2_d_v02.py": (
        "ead2127501c15f6c8ab01eab0c95c65a838008326004bb9ce290557a2fb890ff"
    ),
    "hedgehog/kernel/transition_registry_v01.py": (
        "31492ba73aabc7139bc2bae17dbbd7bbf5b6c8496c8b64764faebeff3c2fc107"
    ),
    "tests/test_transition_registry_v01.py": (
        "6543bb228f6c9c8a8b064f55fb55b84e426320b51ca12243b04db9f8efa1ac67"
    ),
    "hedgehog/kernel/__init__.py": (
        "e4b0578d26910fa6de9c8976395218544d4d5e10c55bcf96e6ce57b7475394cc"
    ),
    "demo/run_living_gauntlet_v01.py": (
        "d066cb9cd3a681acbc774ac3eb878dd54ac190ca1e1d8cb6a823bc1aa9513d00"
    ),
    "tests/test_living_gauntlet_v01_runner.py": (
        "48bf157ea080e994f42ace54e7393463cb6ec95fc16175ff1455ddd9026a7b78"
    ),
    "hedgehog/kernel/conformance_v01.py": (
        "038abbea4cd1504472ed5bad5f7b1c73b9f46d5cff3fa4b4cdf9c13a8586813e"
    ),
    "demo/run_kernel_conformance_v01.py": (
        "a5206b8e0a66609bc524104df6c2ba7a5e6d558b1dbeae73f81f3756dc7dc4ed"
    ),
    "tests/test_kernel_conformance_v01_runner.py": (
        "c2b36e6bb799e9c291abd5913c5494c637d09f154f6db7aed56c75d51eab1624"
    ),
    "docs/continuous_delta_runtime_v0_1_g2_e_post_acceptance_contract_addendum_v01.md": (
        "1041dbf3da320557d5eca948a13d0c4737e4e9b9ffac64c9453c97503527ca4c"
    ),
    "hedgehog/kernel/continuous_delta_runtime_v01.py": (
        "929f99da757647506f326c5c6cd17e2c7895f4c50bf4ed3f4e3b0d53fda743d3"
    ),
    "schemas/continuous_delta_runtime_v01.schema.json": (
        "6d2d2c8756ebf261724742ad14294094ee9ce04a28c0498b264164ec585d11f2"
    ),
    "tests/test_continuous_delta_runtime_g2_e_v01.py": (
        "812cbf76e75c7389cb3d687c453acdacee7e9de531350cdd1c9e28ffd73b113d"
    ),
    "tests/test_execution_mode_router_g2_c_v01.py": (
        "feb7807db6dc750acfad3395cacca72dd398cbbd47cf980463ce0b5ea544a33e"
    ),
    "tests/test_repository_maintenance_contract_v01.py": (
        "22d9c6687500079954ddb3f57e8937516f27d54de27d9f2034957d033b152d81"
    ),
}

G2C_CLOSURE_PATHS = (
    "AGENTS.md",
    "README.md",
    "docs/execution_mode_router_g2_c_checkpoint_v01.md",
    "release/claim_to_evidence_index.md",
    "release/current_limitations.md",
    "release/current_release_notes.md",
    "release/current_status_overlay_v01.json",
    "specs/machine_manifest_v0_25.json",
    "tests/test_repository_release_spine_v01.py",
)

PROTECTED_PATHS_AT_G2C_AUDIT = (
    "release/completion_manifest.json",
    "release/integration_seam_index.json",
    "release/integration_seam_index.md",
    "release/one_command_gauntlet.md",
    "pyproject.toml",
    "LICENSE",
    "COMMERCIAL-LICENSING.md",
)

ROADMAP_SHA256 = (
    "c406dd84163634d55e23309a814d49c7a3ff30171059b7b95a1a38e2cc07e7b6"
)
ROADMAP_BYTES = 82789
ROADMAP_LINES = 2291
RETIRED_ROADMAP_PATH = (
    "specs/future/quantum/"
    "hedgehog_quantum_mathematical_extension_roadmap_v1_0.md"
)

REPOSITORY_RELEASE_SPINE_TEST_MODIFIED = True
OTHER_TESTS_MODIFIED = False
RUNTIME_TESTS_MODIFIED = False

README_QUANTUM_SECTION = """## Future Mathematical Profiles

**Probabilistic intelligence. Deterministic authority.**

Hedgehog OS does not require uncertain computation to become deterministic. It gives deterministic, probabilistic, tensor, quantum-inspired, and optional QPU-backed methods a bounded advisory space while keeping authority and consequential effects classical, explicit, Root-bound, and auditable.

Future mathematical profiles may change how possibilities are represented and explored. They do not change who owns the decision or who controls the effect.

Status: future post-Gate-6 design only; not implemented; not part of current release claims; physical QPU not required; quantum advantage not claimed.

[Quantum-Inspired Mathematical Extension Roadmap v2.0](specs/future/quantum/hedgehog_quantum_mathematical_extension_roadmap_v2_0.md)"""

PASSPORT_QUANTUM_SECTION = """### Computational Substrate Neutrality

Hedgehog authority law is independent of the advisory mathematical or computational substrate. Deterministic code, classical optimization, probabilistic models, LLMs, SLMs, tensor methods, quantum-inspired mathematics, classical simulators, and optional physical-QPU backends may serve as replaceable advisory compute organs only when Root sovereignty, BSEP context boundaries, HardMask, Transition Registry, Root-created ActionCommitPacket, Corridor exclusivity, Receipt non-authority, temporal hard gates, and Replay non-execution remain unchanged.

Hedgehog does not make intelligence deterministic. It makes the ownership of action deterministic."""

MATH_QUANTUM_SECTION = """## Future Mathematical Extension Profiles

Hedgehog OS preserves a possibility space before it creates authority. The current classical AVF, GT, DRS, ExecutionModeRouter, and Fractal mathematics may be extended after Gate 6 by versioned probabilistic, tensor, quantum-inspired, or optional physical-QPU advisory profiles.

Possibility may remain probabilistic. Authority must become explicit.

Such a profile may change representation and evaluation of candidate space, contextual interaction, strategy correlation, advisory-memory evolution, or compute allocation. It may not change Root sovereignty, BSEP-scoped observation, HardMask, Transition Registry, ActionCommitPacket, Corridor exclusivity, Receipt non-authority, temporal hard gates, or Replay non-execution.

The classical profile remains mandatory and must appear as an exact or explicitly bounded classical limit of every promoted extension. This is an architectural-computation statement, not a claim that the current runtime contains a physical quantum state.

See: `specs/future/quantum/hedgehog_quantum_mathematical_extension_roadmap_v2_0.md`."""

QUANTUM_LIMITATION = (
    "- The Quantum-Inspired Mathematical Extension is a future post-Gate-6 "
    "engineering design only. No quantum-inspired state ABI, Quantum AVF, "
    "Quantum GT, Quantum DRS, quantum Fractal allocator, simulator backend, "
    "physical-QPU adapter, physical quantum-state result, or quantum-advantage "
    "result is implemented or claimed in the current release."
)

QUANTUM_ENGINEERING_NOTE = (
    "- Added the non-implementing future Quantum-Inspired Mathematical "
    "Extension Roadmap v2.0. This private design record changes no current "
    "runtime, gate status, conformance result, release claim, or authority law "
    "and does not authorize implementation before the tagged Gate-6 baseline."
)

QUANTUM_FUTURE_PROFILE = {
    "profile_id": "quantum_mathematical_extension_v2_0",
    "document_ref": (
        "specs/future/quantum/"
        "hedgehog_quantum_mathematical_extension_roadmap_v2_0.md"
    ),
    "status": "FUTURE_DESIGN_NOT_IMPLEMENTED",
    "private_design_commit_allowed_after": "G2C_CLOSED_PASS",
    "public_disclosure_required_gate": (
        "GATE6_CLOSED_PASS_AND_R_IP1_RELEASE_APPROVAL"
    ),
    "implementation_baseline_required": "HEDGEHOG_GATE6_CLOSED_PASS_AND_TAGGED",
    "current_release_claim": False,
    "current_conformance_category": None,
    "physical_qpu_required": False,
    "quantum_advantage_claimed": False,
    "physical_quantum_state_claimed": False,
    "changes_root_law": False,
    "changes_bsep_law": False,
    "changes_hardmask_law": False,
    "changes_corridor_law": False,
    "changes_replay_law": False,
}

FROZEN_EVIDENCE = {
    "completion_manifest": {
        "path": "release/completion_manifest.json",
        "sha256": (
            "02ffac0d78df768f91df0bb06bdd15ec463dbe5ccea6ef82b7022146819f3466"
        ),
        "classification": "FROZEN_EVIDENCE",
    },
    "integration_seam_index": {
        "path": "release/integration_seam_index.json",
        "sha256": (
            "c29c2ff873c8b448d8825c3288918e980eab3d65a5114762d2e3fbe5b1206231"
        ),
        "classification": "FROZEN_EVIDENCE",
    },
}

IN_PROGRESS_BOUNDARY = {
    "profile_version": "v0.1",
    "boundary_id": "current_engineering_boundary_v01",
    "accepted_pre_r_h1_base_commit": ACCEPTED_PRE_R_H1_BASE_COMMIT,
    "preflight_commit": ACCEPTED_PREFLIGHT_COMMIT,
    "implementation_basis_commit": None,
    "audit_commit": None,
    "closure_commit_identity": None,
    "workstream_id": "R-H1",
    "workstream_status": "IMPLEMENTATION_IN_PROGRESS",
    "implementation_was_explicitly_authorized": True,
    "implementation_open": True,
    "closure_claimed": False,
    "independent_audit_passed": False,
    "gate1_status": "CLOSED_PASS",
    "two_domain_status": "CLOSED_PASS",
    "g2a_status": "CLOSED_PASS",
    "g2b_status": "CLOSED_PASS",
    "gate2_status": "NOT_CLOSED",
    "g2c_status": "NEXT_NOT_STARTED",
    "g2c_implementation_authorized": False,
    "public_release_claimed": False,
    "rc2_claimed": False,
    "production_readiness_claimed": False,
    "production_security_certification_claimed": False,
    "accepted_pre_r_h1_checkpoint": (
        "docs/drs_semantic_address_space_reuse_certificate_g2_b_"
        "checkpoint_v01.md"
    ),
    "accepted_pre_r_h1_audit": (
        "docs/audit_reports/auditor_drs_semantic_address_space_"
        "reuse_certificate_g2_b_v01.log"
    ),
    "r_h1_audit_path": None,
    "r_h1_checkpoint_path": None,
    "historical_nested_objects_are_current_queue_authority": False,
}

CLOSURE_TRANSITION_FIELDS = {
    "workstream_status",
    "implementation_open",
    "closure_claimed",
    "independent_audit_passed",
    "implementation_basis_commit",
    "audit_commit",
    "closure_commit_identity",
    "r_h1_audit_path",
    "r_h1_checkpoint_path",
}

CLAIM_IDS = (
    "claim_gate1_domain_neutral_reference_kernel_closed_pass",
    "claim_two_domain_all_real_sealed_evidence_program_closed_pass",
    "claim_g2a_actionpacket_lifecycle_kill_switch_closed_pass",
    "claim_g2b_drs_semantic_address_reuse_certificate_closed_pass",
)

R_H1_CLOSURE_CLAIM_ID = (
    "claim_r_h1_clean_clone_licensing_release_spine_reconciliation_"
    "closed_pass"
)
R_H1_AUDIT_PATH = (
    "docs/audit_reports/"
    "auditor_clean_clone_licensing_release_spine_reconciliation_r_h1_v01.log"
)
R_H1_CHECKPOINT_PATH = (
    "docs/"
    "clean_clone_licensing_release_spine_reconciliation_r_h1_checkpoint_v01.md"
)
R_H1_CLOSURE_TEST_PATHS = (
    "tests/test_repository_maintenance_contract_v01.py",
    "tests/test_repository_release_spine_v01.py",
    "tests/test_repomix_handoff_reproducibility_v01.py",
)
R_H1_CLOSURE_CLAIM_WORDING = (
    "The R-H1 Clean-Clone, Licensing, and Release-Spine Reconciliation "
    "workstream is CLOSED_PASS."
)

CLAIM_EVIDENCE_PATHS = {
    CLAIM_IDS[0]: (
        "tests/test_kernel_conformance_v01_runner.py",
        "demo/run_kernel_conformance_v01.py",
        "docs/audit_reports/auditor_domain_neutral_reference_kernel_gate1_v01.log",
        "docs/domain_neutral_reference_kernel_gate1_checkpoint_v01.md",
    ),
    CLAIM_IDS[1]: (
        "tests/test_two_domain_airline_all_real_program_v01_runner.py",
        "tests/test_two_domain_supplier_water_filter_program_v01_runner.py",
        "docs/audit_reports/auditor_two_domain_all_real_sealed_evidence_program_v01.log",
        "docs/two_domain_all_real_sealed_evidence_program_v01_checkpoint.md",
    ),
    CLAIM_IDS[2]: (
        "tests/test_action_commit_packet_lifecycle_g2_a_v01.py",
        "demo/run_action_commit_packet_lifecycle_g2_a_v01.py",
        "docs/audit_reports/auditor_action_commit_packet_lifecycle_kill_switch_g2_a_v01.log",
        "docs/actionpacket_lifecycle_kill_switch_g2_a_checkpoint_v01.md",
    ),
    CLAIM_IDS[3]: (
        "tests/test_drs_semantic_address_reuse_certificate_g2_b_v01.py",
        "demo/run_drs_semantic_address_reuse_certificate_g2_b_v01.py",
        "docs/audit_reports/auditor_drs_semantic_address_space_reuse_certificate_g2_b_v01.log",
        "docs/drs_semantic_address_space_reuse_certificate_g2_b_checkpoint_v01.md",
    ),
}

RELEASE_SPINE_PATHS = (
    "release/claim_to_evidence_index.md",
    "release/integration_seam_index.md",
    "release/one_command_gauntlet.md",
    "release/current_limitations.md",
    "release/current_release_notes.md",
)


def _sha256_bytes(value: bytes) -> str:
    return hashlib.sha256(value).hexdigest()


def _read_json(path: Path) -> dict[str, object]:
    value = json.loads(path.read_text(encoding="utf-8"))
    assert isinstance(value, dict)
    return value


def _nested_mapping_keys(value: object) -> set[str]:
    if isinstance(value, dict):
        return set(value) | {
            key
            for nested in value.values()
            for key in _nested_mapping_keys(nested)
        }
    if isinstance(value, list):
        return {
            key
            for nested in value
            for key in _nested_mapping_keys(nested)
        }
    return set()


def _git_show(commit: str, path: str) -> bytes:
    completed = subprocess.run(
        ("git", "show", f"{commit}:{path}"),
        cwd=REPOSITORY_ROOT,
        check=False,
        capture_output=True,
    )
    assert completed.returncode == 0, (
        "unsupported non-Git/source-archive validation: required Git object "
        f"{commit}:{path} is unavailable; stderr="
        f"{completed.stderr.decode('utf-8', errors='replace')}"
    )
    return completed.stdout


def _current_boundary() -> dict[str, object]:
    manifest = _read_json(MANIFEST_PATH)
    checkpoint = manifest["current_checkpoint_status"]
    assert isinstance(checkpoint, dict)
    boundary = checkpoint["current_engineering_boundary_v01"]
    assert isinstance(boundary, dict)
    return boundary


def _readme_block(raw: bytes) -> bytes:
    begin = README_BEGIN_MARKER.encode("utf-8")
    end = README_END_MARKER.encode("utf-8")
    assert raw.count(begin) == 1
    assert raw.count(end) == 1
    begin_offset = raw.index(begin)
    end_offset = raw.index(end)
    assert begin_offset < end_offset
    assert begin not in raw[begin_offset + len(begin) : end_offset]
    return raw[begin_offset : end_offset + len(end)]


def _readme_without_block(raw: bytes) -> bytes:
    block = _readme_block(raw)
    return raw.replace(block, b"", 1)


def _agents_block(raw: bytes) -> bytes:
    starts = tuple(
        marker.encode("utf-8")
        for marker in (
            AGENTS_BEGIN_MARKER,
            AGENTS_CURRENT_BEGIN_MARKER,
            AGENTS_G2D_CURRENT_BEGIN_MARKER,
        )
        if marker.encode("utf-8") in raw
    )
    end = AGENTS_END_MARKER.encode("utf-8")
    assert len(starts) == 1
    assert raw.count(starts[0]) == 1
    assert raw.count(end) == 1
    begin_offset = raw.index(starts[0])
    end_offset = raw.index(end)
    assert begin_offset < end_offset
    return raw[begin_offset:end_offset]


def _agents_without_block(raw: bytes) -> bytes:
    block = _agents_block(raw)
    return raw.replace(block, b"", 1)


def _revert_g2c_boundary_transition(
    document: dict[str, object],
    *,
    overlay: bool,
) -> dict[str, object]:
    reverted = copy.deepcopy(document)
    if overlay:
        boundary = reverted["current_engineering_boundary"]
    else:
        checkpoint = reverted["current_checkpoint_status"]
        assert isinstance(checkpoint, dict)
        boundary = checkpoint["current_engineering_boundary_v01"]
    assert isinstance(boundary, dict)
    boundary["g2c_status"] = "NEXT_NOT_STARTED"
    boundary["g2c_implementation_authorized"] = False
    return reverted


def _revert_g2d_boundary_transition(
    document: dict[str, object],
    *,
    overlay: bool,
) -> dict[str, object]:
    reverted = copy.deepcopy(document)
    if overlay:
        boundary = reverted["current_engineering_boundary"]
    else:
        checkpoint = reverted["current_checkpoint_status"]
        assert isinstance(checkpoint, dict)
        boundary = checkpoint["current_engineering_boundary_v01"]
    assert isinstance(boundary, dict)
    for key in G2D_CURRENT_BOUNDARY_FIELDS:
        assert boundary.pop(key) == G2D_CURRENT_BOUNDARY_FIELDS[key]
    return reverted


def _assert_exactly_once(text: str, required: tuple[str, ...]) -> None:
    for value in required:
        assert text.count(value) == 1, value


def _assert_absent(text: str, forbidden: tuple[str, ...]) -> None:
    for value in forbidden:
        assert value not in text, value


def _assert_closed_boundary(boundary: dict[str, object]) -> None:
    assert set(boundary) == set(IN_PROGRESS_BOUNDARY) | set(
        G2D_CURRENT_BOUNDARY_FIELDS
    )
    assert re.fullmatch(r"[0-9a-f]{40}", boundary["implementation_basis_commit"])
    assert re.fullmatch(r"[0-9a-f]{40}", boundary["audit_commit"])
    assert boundary["closure_commit_identity"] == "NOT_SELF_RECORDED"
    assert boundary["workstream_status"] == "CLOSED_PASS"
    assert boundary["implementation_was_explicitly_authorized"] is True
    assert boundary["implementation_open"] is False
    assert boundary["closure_claimed"] is True
    assert boundary["independent_audit_passed"] is True
    assert boundary["r_h1_audit_path"] == R_H1_AUDIT_PATH
    assert boundary["r_h1_checkpoint_path"] == R_H1_CHECKPOINT_PATH
    assert boundary["g2c_status"] == "CLOSED_PASS"
    assert boundary["g2c_implementation_authorized"] is True
    for key, value in G2D_CURRENT_BOUNDARY_FIELDS.items():
        assert boundary[key] == value

    basis_commit = boundary["implementation_basis_commit"]
    assert isinstance(basis_commit, str)
    basis_manifest = json.loads(
        _git_show(basis_commit, "specs/machine_manifest_v0_25.json")
    )
    basis_boundary = basis_manifest["current_checkpoint_status"][
        "current_engineering_boundary_v01"
    ]
    assert basis_boundary == IN_PROGRESS_BOUNDARY
    r_h1_closure_boundary = copy.deepcopy(boundary)
    for key in G2D_CURRENT_BOUNDARY_FIELDS:
        r_h1_closure_boundary.pop(key)
    r_h1_closure_boundary["g2c_status"] = "NEXT_NOT_STARTED"
    r_h1_closure_boundary["g2c_implementation_authorized"] = False
    changed_fields = {
        key
        for key in r_h1_closure_boundary
        if r_h1_closure_boundary[key] != basis_boundary[key]
    }
    assert changed_fields == CLOSURE_TRANSITION_FIELDS


def test_manifest_baseline_is_preserved_by_one_add_only_boundary() -> None:
    baseline_bytes = _git_show(
        ACCEPTED_PRE_R_H1_BASE_COMMIT,
        "specs/machine_manifest_v0_25.json",
    )
    assert _sha256_bytes(baseline_bytes) == ACCEPTED_MANIFEST_SHA256
    baseline = json.loads(baseline_bytes)
    closure = json.loads(_git_show(
        G2C_CLOSURE_COMMIT,
        MANIFEST_PATH.relative_to(REPOSITORY_ROOT).as_posix(),
    ))

    checkpoint = closure["current_checkpoint_status"]
    assert isinstance(checkpoint, dict)
    assert tuple(checkpoint).count("current_engineering_boundary_v01") == 1
    boundary = checkpoint["current_engineering_boundary_v01"]
    assert isinstance(boundary, dict)
    assert set(boundary) == set(IN_PROGRESS_BOUNDARY)

    closure_without_boundary = copy.deepcopy(closure)
    removed = closure_without_boundary["current_checkpoint_status"].pop(
        "current_engineering_boundary_v01"
    )
    assert removed == boundary
    assert closure_without_boundary == baseline
    assert checkpoint["metadata_sync_only"] is True
    assert checkpoint["manifest_does_not_override_human_passport"] is True

    current = _read_json(MANIFEST_PATH)
    current_checkpoint = current["current_checkpoint_status"]
    assert isinstance(current_checkpoint, dict)
    assert current_checkpoint["metadata_sync_only"] is True
    assert current_checkpoint["manifest_does_not_override_human_passport"] is True
    _assert_closed_boundary(
        current_checkpoint["current_engineering_boundary_v01"]
    )


def test_g2c_manifest_transition_is_exactly_two_children() -> None:
    audit_manifest = json.loads(
        _git_show(G2C_AUDIT_COMMIT_BASELINE, MANIFEST_PATH.relative_to(
            REPOSITORY_ROOT
        ).as_posix())
    )
    closure_manifest = json.loads(_git_show(
        G2C_CLOSURE_COMMIT,
        MANIFEST_PATH.relative_to(REPOSITORY_ROOT).as_posix(),
    ))
    audit_boundary = audit_manifest["current_checkpoint_status"][
        "current_engineering_boundary_v01"
    ]
    current_boundary = closure_manifest["current_checkpoint_status"][
        "current_engineering_boundary_v01"
    ]
    assert isinstance(audit_boundary, dict)
    assert isinstance(current_boundary, dict)
    assert set(current_boundary) == set(audit_boundary)
    assert audit_boundary["g2c_status"] == "NEXT_NOT_STARTED"
    assert audit_boundary["g2c_implementation_authorized"] is False
    assert current_boundary["g2c_status"] == "CLOSED_PASS"
    assert current_boundary["g2c_implementation_authorized"] is True
    assert _revert_g2c_boundary_transition(
        closure_manifest,
        overlay=False,
    ) == audit_manifest


def test_current_boundary_has_exact_supported_lifecycle_geometry() -> None:
    boundary = _current_boundary()
    status = boundary["workstream_status"]
    assert status in {"IMPLEMENTATION_IN_PROGRESS", "CLOSED_PASS"}
    assert status != "PREFLIGHT_ONLY"

    if status == "IMPLEMENTATION_IN_PROGRESS":
        assert boundary == IN_PROGRESS_BOUNDARY
    else:
        _assert_closed_boundary(boundary)


def test_readme_current_boundary_install_and_license_are_bounded() -> None:
    raw = README_PATH.read_bytes()
    text = raw.decode("utf-8")
    block = _readme_block(raw).decode("utf-8")
    boundary = _current_boundary()

    common_lines = {
        "workstream_id: R-H1",
        "implementation_was_explicitly_authorized: true",
        f"accepted_pre_r_h1_base_commit: {ACCEPTED_PRE_R_H1_BASE_COMMIT}",
        f"preflight_commit: {ACCEPTED_PREFLIGHT_COMMIT}",
        "gate1_status: CLOSED_PASS",
        "two_domain_status: CLOSED_PASS",
        "g2a_status: CLOSED_PASS",
        "g2b_status: CLOSED_PASS",
        "gate2_status: NOT_CLOSED",
        "g2c_status: CLOSED_PASS",
        "g2c_implementation_authorized: true",
        f"g2c_preflight_commit: {G2C_ACCEPTED_PREFLIGHT_COMMIT}",
        f"g2c_implementation_basis_commit: {G2C_IMPLEMENTATION_BASIS_COMMIT}",
        f"g2c_audit_commit: {G2C_AUDIT_COMMIT}",
        "g2c_closure_commit_identity: NOT_SELF_RECORDED",
        "g2d_status: CLOSED_PASS",
        "g2d_correction_implementation_authorized: true",
        "g2d_corrected_implementation_exists: true",
        "g2d_contract_only_claim: false",
        "g2d_corrected_runtime_acceptance_claimed: true",
        "g2d_corrected_implementation_committed: true",
        f"g2d_corrected_implementation_commit: {G2D_CORRECTED_IMPLEMENTATION_COMMIT}",
        "g2d_corrected_implementation_patch_sha256: "
        f"{G2D_CORRECTED_IMPLEMENTATION_PATCH_SHA256}",
        "g2d_corrected_owner_evidence_bundle_sha256: "
        f"{G2D_OWNER_EVIDENCE_BUNDLE_SHA256}",
        "g2d_independent_reaudit_required: true",
        "g2d_independent_reaudit_passed: true",
        f"g2d_independent_reaudit_commit: {G2D_INDEPENDENT_REAUDIT_COMMIT}",
        f"g2d_independent_reaudit_path: {G2D_INDEPENDENT_REAUDIT_PATH}",
        f"g2d_independent_reaudit_sha256: {G2D_INDEPENDENT_REAUDIT_SHA256}",
        "g2d_additive_reclosure_required: true",
        "g2d_additive_reclosure_completed: true",
        "g2d_corrected_closure_claimed: true",
        f"g2d_corrected_checkpoint_path: {G2D_CHECKPOINT_PATH}",
        f"g2d_corrected_checkpoint_sha256: {G2D_CHECKPOINT_SHA256}",
        "g2d_corrected_closure_commit_identity: NOT_SELF_RECORDED",
        "g2d_old_audit_checkpoint_class: HISTORICAL_PRECORRECTION_EVIDENCE",
        f"g2d_accepted_normative_donor_sha256: {G2D_ACCEPTED_NORMATIVE_DONOR_SHA256}",
        f"g2d_accepted_repository_addendum_sha256: {G2D_ACCEPTED_ADDENDUM_SHA256}",
        "g2d_historical_precorrection_status: CLOSED_PASS_ON_PRECORRECTION_BYTES",
        "g2d_historical_precorrection_audit_status: PASS",
        "g2d_historical_precorrection_checkpoint_present: true",
        f"g2d_preflight_commit: {G2D_ACCEPTED_PREFLIGHT_COMMIT}",
        "g2d_historical_precorrection_implementation_basis_commit: "
        f"{G2D_IMPLEMENTATION_BASIS_COMMIT}",
        f"g2d_historical_precorrection_audit_commit: {G2D_AUDIT_COMMIT}",
        "g2d_closure_commit_identity: NOT_SELF_RECORDED",
        "g2e3_status: REVALIDATION_PENDING_ON_CORRECTED_G2D",
        "g2e3_post_corrected_g2d_landing_status: REVALIDATION_PENDING_ON_CORRECTED_G2D",
        "g2e4_status: NOT_STARTED_NOT_AUTHORIZED",
        "g2f_status: NOT_STARTED",
        "g2f_implementation_authorized: false",
        "g2f_implementation_started: false",
        "public_release_claimed: false",
        "rc2_claimed: false",
        "production_readiness_claimed: false",
        "production_security_certification_claimed: false",
    }
    for line in common_lines:
        assert line in block

    if boundary["workstream_status"] == "IMPLEMENTATION_IN_PROGRESS":
        _assert_exactly_once(block, (
            "workstream_status: IMPLEMENTATION_IN_PROGRESS",
            "implementation_open: true",
            "closure_claimed: false",
            "independent_audit_passed: false",
            "implementation_basis_commit: NOT_YET_SYNCHRONIZED",
            "audit_commit: NOT_YET_SYNCHRONIZED",
            "closure_commit_identity: NOT_APPLICABLE",
            "R-H1 independent audit synchronized for closure: `false`",
            "R-H1 checkpoint: `NOT_YET_PRESENT`",
            "R-H1 is not closed",
        ))
        _assert_absent(block, (
            "workstream_status: CLOSED_PASS",
            "implementation_open: false",
            "closure_claimed: true",
            "independent_audit_passed: true",
            "closure_commit_identity: NOT_SELF_RECORDED",
            "R-H1 independent audit synchronized for closure: `true`",
            "R-H1 is `CLOSED_PASS`",
            R_H1_AUDIT_PATH,
            R_H1_CHECKPOINT_PATH,
        ))
    else:
        _assert_exactly_once(block, (
            "workstream_status: CLOSED_PASS",
            "implementation_open: false",
            "\nclosure_claimed: true\n",
            "independent_audit_passed: true",
            f"implementation_basis_commit: {boundary['implementation_basis_commit']}",
            f"audit_commit: {boundary['audit_commit']}",
            "\nclosure_commit_identity: NOT_SELF_RECORDED\n",
            "R-H1 independent audit synchronized for closure: `true`",
            f"R-H1 audit: `{R_H1_AUDIT_PATH}`",
            f"R-H1 checkpoint: `{R_H1_CHECKPOINT_PATH}`",
            "R-H1 is `CLOSED_PASS`",
            "Historical pre-correction G2-D is `CLOSED_PASS_ON_PRECORRECTION_BYTES`",
            "G2-D is `CLOSED_PASS` on the corrected v0.3.7 bytes",
            "G2-D correction implementation authorization is `true`",
            "implementation bytes exist and are committed",
            "G2-E3 is `REVALIDATION_PENDING_ON_CORRECTED_G2D`",
            "G2-E4 is `NOT_STARTED_NOT_AUTHORIZED`",
            "- G2-F is `NOT_STARTED / NOT_AUTHORIZED`",
            f"[Accepted G2-C preflight]({G2C_ACCEPTED_PREFLIGHT_PATH})",
            f"[G2-C independent audit]({G2C_AUDIT_PATH})",
            f"[G2-C checkpoint]({G2C_CHECKPOINT_PATH})",
            f"[Accepted G2-D preflight]({G2D_ACCEPTED_PREFLIGHT_PATH})",
            f"[Accepted G2-D addendum]({G2D_ACCEPTED_ADDENDUM_PATH})",
            f"[G2-D independent audit]({G2D_AUDIT_PATH})",
            f"[G2-D checkpoint]({G2D_HISTORICAL_CHECKPOINT_PATH})",
            f"[Corrected G2-D independent re-audit]({G2D_INDEPENDENT_REAUDIT_PATH})",
            f"[Corrected G2-D successor checkpoint]({G2D_CHECKPOINT_PATH})",
            f"Accepted G2-D v0.3.7 normative donor SHA-256:\n  `{G2D_ACCEPTED_NORMATIVE_DONOR_SHA256}`",
            f"Accepted G2-D repository addendum SHA-256:\n  `{G2D_ACCEPTED_ADDENDUM_SHA256}`",
            "The old G2-D audit and checkpoint certify pre-correction bytes only",
            "Independent re-audit and additive successor reclosure are complete",
            "The independent re-audit is evidence, not authority or closure by itself",
            "Real-world effects remain zero",
        ))
        assert block.count(R_H1_AUDIT_PATH) == 1
        assert block.count(R_H1_CHECKPOINT_PATH) == 1
        _assert_absent(block, (
            "workstream_status: IMPLEMENTATION_IN_PROGRESS",
            "implementation_open: true",
            "\nclosure_claimed: false\n",
            "independent_audit_passed: false",
            "implementation_basis_commit: NOT_YET_SYNCHRONIZED",
            "audit_commit: NOT_YET_SYNCHRONIZED",
            "closure_commit_identity: NOT_APPLICABLE",
            "R-H1 independent audit synchronized for closure: `false`",
            "R-H1 checkpoint: `NOT_YET_PRESENT`",
            "R-H1 is not closed",
        ))

    for path in RELEASE_SPINE_PATHS:
        assert path in block
    assert (
        "docs/clean_clone_licensing_release_spine_reconciliation_r_h1_"
        "preflight_v01.md"
    ) in block
    assert "G2-C is in development" not in block
    assert "G2-C is `NEXT / NOT_STARTED`" not in block
    assert "g2c_status: NEXT_NOT_STARTED" not in block
    assert "g2c_implementation_authorized: false" not in block
    assert "g2d_status: NEXT_NOT_STARTED" not in block
    assert "g2d_implementation_authorized:" not in block
    assert "G2-D is `NEXT / NOT_STARTED`" not in block

    assert "python3 -m venv .venv" in text
    assert ".venv/bin/python -m pip install -e ." in text
    assert ".venv/bin/python -m pip check" in text
    assert ".venv/bin/python -m demo.run_kernel_conformance_v01" in text
    assert ".venv/bin/python -m demo.run_living_gauntlet_v01" in text
    assert "This README section does not" in text
    assert "itself claim an external clean-clone result" in text
    assert "release/current_limitations.md" in text

    with (REPOSITORY_ROOT / "pyproject.toml").open("rb") as handle:
        project = tomllib.load(handle)["project"]
    assert project["license"] == "AGPL-3.0-only"
    assert project["license-files"] == ["LICENSE"]
    assert "`AGPL-3.0-only`" in text
    assert "[LICENSE](LICENSE)" in text
    assert "[COMMERCIAL-LICENSING.md](COMMERCIAL-LICENSING.md)" in text
    assert "non-granting" in text
    assert "informational policy notice" in text
    assert "not a granted license" in text


def test_agents_g2c_closure_block_is_exactly_bounded() -> None:
    raw = AGENTS_PATH.read_bytes()
    block = _agents_block(raw).decode("utf-8")
    audit_agents = _git_show(G2C_AUDIT_COMMIT_BASELINE, "AGENTS.md")
    assert _agents_without_block(raw) == _agents_without_block(audit_agents)
    _assert_exactly_once(block, (
        AGENTS_G2D_CURRENT_BEGIN_MARKER,
        f"Accepted G2-C preflight commit: `{G2C_ACCEPTED_PREFLIGHT_COMMIT}`",
        f"Accepted G2-C preflight path: `{G2C_ACCEPTED_PREFLIGHT_PATH}`",
        f"G2-C implementation basis: `{G2C_IMPLEMENTATION_BASIS_COMMIT}`",
        f"G2-C audit commit: `{G2C_AUDIT_COMMIT}`",
        f"G2-C audit: `{G2C_AUDIT_PATH}`",
        f"G2-C checkpoint: `{G2C_CHECKPOINT_PATH}`",
        f"Accepted G2-D preflight commit: `{G2D_ACCEPTED_PREFLIGHT_COMMIT}`",
        f"Accepted G2-D preflight path: `{G2D_ACCEPTED_PREFLIGHT_PATH}`",
        f"Accepted G2-D preflight SHA-256: `{G2D_ACCEPTED_PREFLIGHT_SHA256}`",
        f"Accepted G2-D addendum path: `{G2D_ACCEPTED_ADDENDUM_PATH}`",
        f"Accepted G2-D addendum SHA-256: `{G2D_ACCEPTED_ADDENDUM_SHA256}`",
        f"Accepted G2-D v0.3.7 normative donor SHA-256: `{G2D_ACCEPTED_NORMATIVE_DONOR_SHA256}`",
        f"Historical pre-correction G2-D implementation basis: `{G2D_IMPLEMENTATION_BASIS_COMMIT}`",
        f"Historical pre-correction G2-D audit commit: `{G2D_AUDIT_COMMIT}`",
        f"Historical pre-correction G2-D audit: `{G2D_AUDIT_PATH}`",
        f"Historical pre-correction G2-D audit SHA-256: `{G2D_AUDIT_SHA256}`",
        f"Historical pre-correction G2-D checkpoint: `{G2D_HISTORICAL_CHECKPOINT_PATH}`",
        f"Corrected G2-D implementation commit: `{G2D_CORRECTED_IMPLEMENTATION_COMMIT}`",
        f"Corrected G2-D implementation parent: `{G2D_CORRECTED_IMPLEMENTATION_PARENT}`",
        "Corrected G2-D implementation patch SHA-256: "
        f"`{G2D_CORRECTED_IMPLEMENTATION_PATCH_SHA256}`",
        "Corrected G2-D owner evidence bundle SHA-256: "
        f"`{G2D_OWNER_EVIDENCE_BUNDLE_SHA256}`",
        f"Independent corrected G2-D re-audit commit: `{G2D_INDEPENDENT_REAUDIT_COMMIT}`",
        f"Independent corrected G2-D re-audit: `{G2D_INDEPENDENT_REAUDIT_PATH}`",
        "Independent corrected G2-D re-audit SHA-256: "
        f"`{G2D_INDEPENDENT_REAUDIT_SHA256}`",
        f"Corrected G2-D successor checkpoint: `{G2D_CHECKPOINT_PATH}`",
        f"Corrected G2-D successor checkpoint SHA-256: `{G2D_CHECKPOINT_SHA256}`",
        "The old audit and checkpoint certify pre-correction bytes only",
        f"Corrected closure commit subject: `{G2D_CLOSURE_SUBJECT}`",
        "Corrected closure commit identity: `NOT_SELF_RECORDED`",
        "R-H1 status: `CLOSED_PASS`",
        "G2-A: `CLOSED_PASS`",
        "G2-B: `CLOSED_PASS`",
        "G2-C: `CLOSED_PASS`",
        "Historical pre-correction G2-D: `CLOSED_PASS_ON_PRECORRECTION_BYTES`",
        "G2-D: `CLOSED_PASS`",
        "G2-D correction implementation authorized: `true`",
        "Corrected G2-D implementation byte exists: `true`",
        "Corrected G2-D implementation committed: `true`",
        "G2-D contract-only claim: `false`",
        "Corrected G2-D runtime acceptance claimed: `true`",
        "Independent G2-D re-audit passed: `true`",
        "Additive G2-D reclosure completed: `true`",
        "Corrected G2-D closure claimed: `true`",
        "Old G2-D audit/checkpoint class: `HISTORICAL_PRECORRECTION_EVIDENCE`",
        "G2-E3: `REVALIDATION_PENDING_ON_CORRECTED_G2D`",
        "G2-E4: `NOT_STARTED_NOT_AUTHORIZED`",
        "Gate 2: `NOT_CLOSED`",
        "G2-F: `NOT_STARTED / NOT_AUTHORIZED`",
        "Provider, model, network, connector, and external-DRS calls remain zero",
        "Corrected G2-D v0.3.7 is `CLOSED_PASS` after corrected implementation",
        "The independent re-audit is evidence, not authority or closure by itself",
        "Corrected G2-D closure is not fresh G2-E3 V06 acceptance or Gate-2 closure",
        "Public release: `NOT_CLAIMED`",
        "RC2: `NOT_CLAIMED`",
        "Production readiness: `NOT_CLAIMED`",
        "Production security certification: `NOT_CLAIMED`",
        "Real-world effects remain zero",
    ))
    _assert_absent(block, (
        "G2-C: `NEXT / NOT_STARTED`",
        "G2-C implementation: `NOT_AUTHORIZED`",
        "G2-D: `NEXT / NOT_STARTED`",
        "G2-D implementation: `NOT_AUTHORIZED`",
        "read-only G2-C inventory",
        "No G2-C slice names",
    ))
    for route_step in (
        "BSEP",
        "semantic proposal",
        "G2-C Root-reviewed ExecutionModeRouteEligibility",
        "runtime-owned RuntimeExecutionTopology",
        "bounded runtime execution",
        "ResultProposal / Post V&V / GT / PARENT_RETURN",
        "Root",
    ):
        assert route_step in block


def test_current_status_overlay_is_exact_and_non_authoritative() -> None:
    overlay = _read_json(OVERLAY_PATH)
    assert tuple(overlay) == (
        "profile_version",
        "overlay_id",
        "overlay_role",
        "current_engineering_boundary",
        "frozen_evidence",
        "does_not_override",
        "release_spine_paths",
    )
    assert overlay["profile_version"] == "v0.1"
    assert overlay["overlay_id"] == "current_status_overlay_v01"
    assert overlay["overlay_role"] == {
        "metadata_only": True,
        "is_authority": False,
        "is_root_decision": False,
        "is_completion_certificate": False,
        "replaces_historical_evidence": False,
        "is_gate2_closure_manifest": False,
        "is_public_release_declaration": False,
    }
    assert overlay["current_engineering_boundary"] == _current_boundary()
    assert overlay["frozen_evidence"] == FROZEN_EVIDENCE
    assert overlay["does_not_override"] == [
        "owner_instruction",
        "AGENTS.md",
        "accepted_checkpoints",
        "accepted_audits",
        "specs/human_passport_v0_25.md",
    ]
    assert overlay["release_spine_paths"] == list(RELEASE_SPINE_PATHS)
    assert "implementation_authorized" not in _nested_mapping_keys(overlay)
    assert "head" not in overlay["current_engineering_boundary"]
    boundary = overlay["current_engineering_boundary"]
    assert isinstance(boundary, dict)
    assert boundary["g2c_status"] == "CLOSED_PASS"
    assert boundary["g2c_implementation_authorized"] is True
    for key, value in G2D_CURRENT_BOUNDARY_FIELDS.items():
        assert boundary[key] == value

    g2d_audit_overlay = json.loads(
        _git_show(G2D_AUDIT_COMMIT, "release/current_status_overlay_v01.json")
    )
    assert _revert_g2d_boundary_transition(
        overlay,
        overlay=True,
    ) == g2d_audit_overlay

    audit_overlay = json.loads(
        _git_show(G2C_AUDIT_COMMIT_BASELINE, "release/current_status_overlay_v01.json")
    )
    audit_boundary = audit_overlay["current_engineering_boundary"]
    assert isinstance(audit_boundary, dict)
    assert audit_boundary["g2c_status"] == "NEXT_NOT_STARTED"
    assert audit_boundary["g2c_implementation_authorized"] is False
    assert _revert_g2c_boundary_transition(
        g2d_audit_overlay,
        overlay=True,
    ) == audit_overlay


def test_frozen_gate1_release_evidence_hashes_are_exact() -> None:
    for evidence in FROZEN_EVIDENCE.values():
        path = REPOSITORY_ROOT / evidence["path"]
        assert path.is_file()
        assert _sha256_bytes(path.read_bytes()) == evidence["sha256"]


def test_release_spine_roles_claims_and_commands_are_bounded() -> None:
    for path in RELEASE_SPINE_PATHS:
        assert (REPOSITORY_ROOT / path).is_file()

    claim_text = CLAIM_INDEX_PATH.read_text(encoding="utf-8")
    observed_claim_ids = tuple(re.findall(r"\bclaim_[a-z0-9_]+\b", claim_text))
    boundary = _current_boundary()
    claim_normalized = " ".join(claim_text.split())
    for required in (
        "At the R-H1A implementation boundary, R-H1 was "
        "`IMPLEMENTATION_IN_PROGRESS`.",
        "Limitation at that boundary: R-H1 as a whole remained "
        "`IMPLEMENTATION_IN_PROGRESS`; no accepted R-H1 audit and checkpoint "
        "had yet been synchronized into R-H1 closure status.",
    ):
        assert required in claim_normalized
    _assert_absent(claim_normalized, (
        "Workstream: R-H1, `IMPLEMENTATION_IN_PROGRESS`.",
        "R-H1 as a whole remains `IMPLEMENTATION_IN_PROGRESS`",
    ))
    if boundary["workstream_status"] == "IMPLEMENTATION_IN_PROGRESS":
        assert observed_claim_ids == CLAIM_IDS
        assert R_H1_CLOSURE_CLAIM_ID not in claim_text
        assert (
            "R-H1A Maintenance Implementation Evidence - Not a Closure Claim"
            in claim_text
        )
    else:
        assert observed_claim_ids == CLAIM_IDS + (
            R_H1_CLOSURE_CLAIM_ID,
            G2C_CLOSURE_CLAIM_ID,
            G2D_CLOSURE_CLAIM_ID,
            G2D_ACTIVE_CONTRACT_CLAIM_ID,
            G2D_CORRECTED_CLOSURE_CLAIM_ID,
        )
        closure_row = next(
            line
            for line in claim_text.splitlines()
            if f"| {R_H1_CLOSURE_CLAIM_ID} |" in line
        )
        assert R_H1_CLOSURE_CLAIM_WORDING in closure_row
        assert "CLOSED_PASS" in closure_row
        for path in (
            *R_H1_CLOSURE_TEST_PATHS,
            R_H1_AUDIT_PATH,
            R_H1_CHECKPOINT_PATH,
        ):
            assert path in closure_row
            assert (REPOSITORY_ROOT / path).exists()
        for limitation in (
            "does not close Gate 2",
            "does not start or authorize G2-C",
            "does not declare a public release",
            "does not declare RC2",
            "does not claim production readiness",
            "does not claim production security certification",
        ):
            assert limitation in closure_row
        g2c_row = next(
            line
            for line in claim_text.splitlines()
            if f"| {G2C_CLOSURE_CLAIM_ID} |" in line
        )
        assert G2C_CLOSURE_CLAIM_WORDING in g2c_row
        assert "CLOSED_PASS" in g2c_row
        for path in (
            "tests/test_execution_mode_router_g2_c_v01.py",
            "tests/test_transition_registry_v01.py",
            "tests/test_living_gauntlet_v01_runner.py",
            "tests/test_kernel_conformance_v01_runner.py",
            "tests/test_repository_release_spine_v01.py",
            "demo/run_execution_mode_router_g2_c_v01.py",
            "demo/run_living_gauntlet_v01.py",
            "demo/run_kernel_conformance_v01.py",
            G2C_AUDIT_PATH,
            G2C_CHECKPOINT_PATH,
        ):
            assert path in g2c_row
            assert (REPOSITORY_ROOT / path).exists()
        for limitation in (
            "does not close Gate 2",
            "does not start or authorize G2-D",
            "does not declare a public release",
            "does not declare RC2",
            "does not claim production readiness",
            "does not claim production security certification",
            "creates no topology or real-world effect",
        ):
            assert limitation in g2c_row
        g2d_row = next(
            line
            for line in claim_text.splitlines()
            if f"| {G2D_CLOSURE_CLAIM_ID} |" in line
        )
        assert G2D_CLOSURE_CLAIM_WORDING in g2d_row
        assert "HISTORICAL_PRECORRECTION_CLOSED_PASS" in g2d_row
        for path in (
            "tests/test_fractal_runtime_g2_d_v02.py",
            "tests/test_living_gauntlet_v01_runner.py",
            "tests/test_kernel_conformance_v01_runner.py",
            "demo/run_fractal_runtime_g2_d_v02.py",
            "demo/run_living_gauntlet_v01.py",
            "demo/run_kernel_conformance_v01.py",
            G2D_AUDIT_PATH,
            G2D_HISTORICAL_CHECKPOINT_PATH,
        ):
            assert path in g2d_row
            assert (REPOSITORY_ROOT / path).exists()
        for limitation in (
            "historical evidence for pre-correction bytes only",
            "not proof of corrected runtime bytes",
            "corrected CLOSED_PASS",
            "public release",
            "production readiness",
            "authority",
            "real-world effects",
        ):
            assert limitation in g2d_row
        active_g2d_row = next(
            line
            for line in claim_text.splitlines()
            if f"| {G2D_ACTIVE_CONTRACT_CLAIM_ID} |" in line
        )
        assert G2D_ACTIVE_CONTRACT_CLAIM_WORDING in active_g2d_row
        assert "HISTORICAL_CONTRACT_HOP_COMPLETED" in active_g2d_row
        assert G2D_ACCEPTED_NORMATIVE_DONOR_SHA256 in active_g2d_row
        assert G2D_ACCEPTED_ADDENDUM_SHA256 in active_g2d_row
        for path in (
            "tests/test_fractal_runtime_g2_d_v02.py",
            "tests/test_transition_registry_v01.py",
            "tests/test_repository_release_spine_v01.py",
            "hedgehog/kernel/fractal_runtime_v02.py",
            "demo/run_fractal_runtime_g2_d_v02.py",
        ):
            assert path in active_g2d_row
        for limitation in (
            "Historical completed contract-hop evidence only",
            "then-current REAUDIT_PENDING limitation is superseded",
            "creates no authority or real-world effect",
        ):
            assert limitation in active_g2d_row
        assert G2D_AUDIT_PATH not in active_g2d_row
        assert G2D_CHECKPOINT_PATH not in active_g2d_row
        corrected_g2d_row = next(
            line
            for line in claim_text.splitlines()
            if f"| {G2D_CORRECTED_CLOSURE_CLAIM_ID} |" in line
        )
        assert G2D_CORRECTED_CLOSURE_CLAIM_WORDING in corrected_g2d_row
        assert "| CLOSED_PASS |" in corrected_g2d_row
        for path in (
            "tests/test_fractal_runtime_g2_d_v02.py",
            "tests/test_transition_registry_v01.py",
            "tests/test_living_gauntlet_v01_runner.py",
            "tests/test_kernel_conformance_v01_runner.py",
            "tests/test_repository_release_spine_v01.py",
            "tests/test_repository_maintenance_contract_v01.py",
            "demo/run_fractal_runtime_g2_d_v02.py",
            G2D_INDEPENDENT_REAUDIT_PATH,
            G2D_CHECKPOINT_PATH,
        ):
            assert path in corrected_g2d_row
            assert (REPOSITORY_ROOT / path).exists()
        for limitation in (
            "does not close Gate 2",
            "does not validate G2-E3 on corrected bytes",
            "does not start or authorize G2-E4",
            "creates no authority or real-world effect",
        ):
            assert limitation in corrected_g2d_row
    for claim_id, paths in CLAIM_EVIDENCE_PATHS.items():
        row = next(
            line for line in claim_text.splitlines() if f"| {claim_id} |" in line
        )
        assert "CLOSED_PASS" in row
        assert "Limitation" not in row
        for path in paths:
            assert path in row
            assert (REPOSITORY_ROOT / path).exists()
    assert "233 passed" in claim_text
    assert "R-H1A is not an independent audit" in claim_text

    seam_text = (REPOSITORY_ROOT / "release/integration_seam_index.md").read_text(
        encoding="utf-8"
    )
    seam_normalized = " ".join(seam_text.split())
    assert "release/integration_seam_index.json" in seam_text
    assert FROZEN_EVIDENCE["integration_seam_index"]["sha256"] in seam_text
    assert "not a final Gate-2 seam inventory" in seam_text
    assert seam_text.count("| r_h1_") == 8
    assert seam_text.count("IMPLEMENTATION_IN_PROGRESS") >= 9
    assert "R-H1B implementation-basis maintenance" in seam_normalized
    assert "row statuses are basis evidence" in seam_normalized
    assert "not the mutable current R-H1 lifecycle authority" in seam_normalized

    gauntlet_text = (REPOSITORY_ROOT / "release/one_command_gauntlet.md").read_text(
        encoding="utf-8"
    )
    command_blocks = re.findall(r"```bash\n(.*?)```", gauntlet_text, flags=re.DOTALL)
    assert len(command_blocks) == 2
    execution_command = command_blocks[1]
    assert execution_command.count("demo.run_kernel_conformance_v01") == 1
    assert execution_command.count("demo.run_living_gauntlet_v01") == 1
    assert "&&" in execution_command
    for forbidden in ("--live", "gemini", "provider", "telegram", "connector"):
        assert forbidden not in execution_command.lower()
    assert "NOT_YET_COMPLETED" not in gauntlet_text
    assert "release/current_limitations.md" in gauntlet_text
    assert "accepted R-H1 audit/checkpoint" in gauntlet_text

    limitations = (REPOSITORY_ROOT / "release/current_limitations.md").read_text(
        encoding="utf-8"
    )
    limitations_normalized = " ".join(limitations.split())
    if boundary["workstream_status"] == "IMPLEMENTATION_IN_PROGRESS":
        for required in (
            "R-H1 is `IMPLEMENTATION_IN_PROGRESS`",
            "R-H1 independent audit is not yet synchronized into accepted "
            "closure status",
            "External clean-clone validation is not yet synchronized into "
            "accepted R-H1 closure status",
            "Gate 2 is `NOT_CLOSED`",
            "G2-C is `NEXT / NOT_STARTED`",
            "G2-C implementation is `NOT_AUTHORIZED`",
            "Public release is `NOT_CLAIMED`",
            "RC2 is `NOT_CLAIMED`",
            "Production readiness is `NOT_CLAIMED`",
            "Production security certification is `NOT_CLAIMED`",
            "Standalone wheel completeness is `NOT_CLAIMED`",
        ):
            assert required in limitations_normalized
        _assert_absent(limitations, (
            "R-H1 is `CLOSED_PASS`",
            "External clean-clone validation is `ACCEPTED_PASS`",
            R_H1_AUDIT_PATH,
            R_H1_CHECKPOINT_PATH,
        ))
    else:
        for required in (
            "R-H1 is `CLOSED_PASS`",
            R_H1_AUDIT_PATH,
            R_H1_CHECKPOINT_PATH,
            "External clean-clone validation is `ACCEPTED_PASS` for the "
            "audited implementation basis",
            "G2-C is `CLOSED_PASS`",
            G2C_AUDIT_PATH,
            G2C_CHECKPOINT_PATH,
            "Historical pre-correction G2-D is "
            "`CLOSED_PASS_ON_PRECORRECTION_BYTES` only",
            "Corrected G2-D v0.3.7 is `CLOSED_PASS`",
            "G2-D correction implementation authorization is `true`; corrected "
            "implementation bytes exist and are committed",
            "Corrected runtime acceptance, independent re-audit PASS, additive "
            "reclosure, and corrected closure are all `true`; contract-only claim "
            "is `false`",
            G2D_ACCEPTED_NORMATIVE_DONOR_SHA256,
            G2D_ACCEPTED_ADDENDUM_SHA256,
            G2D_AUDIT_PATH,
            G2D_HISTORICAL_CHECKPOINT_PATH,
            G2D_CORRECTED_IMPLEMENTATION_COMMIT,
            G2D_CORRECTED_IMPLEMENTATION_PATCH_SHA256,
            G2D_OWNER_EVIDENCE_BUNDLE_SHA256,
            G2D_INDEPENDENT_REAUDIT_PATH,
            G2D_INDEPENDENT_REAUDIT_COMMIT,
            G2D_INDEPENDENT_REAUDIT_SHA256,
            G2D_CHECKPOINT_PATH,
            G2D_CLOSURE_SUBJECT,
            "The old audit and checkpoint certify pre-correction bytes only",
            "The old audit and checkpoint are `HISTORICAL_PRECORRECTION_EVIDENCE` only",
            "Independent re-audit and additive successor reclosure are complete",
            "Gate 2 remains `NOT_CLOSED`",
            "G2-E3 is `REVALIDATION_PENDING_ON_CORRECTED_G2D`",
            "G2-E4 is `NOT_STARTED_NOT_AUTHORIZED`",
            "G2-F remains `NOT_STARTED / NOT_AUTHORIZED`",
            "Public release remains `NOT_CLAIMED`",
            "RC2 remains `NOT_CLAIMED`",
            "Production readiness remains `NOT_CLAIMED`",
            "Production security certification remains `NOT_CLAIMED`",
            "Real-world effects remain zero",
            "No RuntimeExecutionTopology was created by G2-C",
            "RuntimeExecutionTopology is not authority",
            "Child results are not FinalOutput",
            "No successor baseline, FinalOutput, permission, packet, receipt, "
            "DRS write, or real-world effect is claimed",
            "A D5 or D6 validation PASS is not truth or authority",
            "Important maintenance debt is recorded for post-Gate-2 treatment",
            "metadata-only and non-authoritative",
            "frozen Gate-1 evidence",
        ):
            assert required in limitations_normalized
        _assert_absent(limitations, (
            "IMPLEMENTATION_IN_PROGRESS",
            "NOT_YET_PRESENT",
            "NOT_YET_SYNCHRONIZED",
            "not yet synchronized",
            "not yet completed",
            "NOT_YET_COMPLETED",
            "G2-C remains `NEXT / NOT_STARTED`",
            "G2-C implementation remains `NOT_AUTHORIZED`",
            "G2-D is `NEXT / NOT_STARTED`",
            "G2-D implementation remains `NOT_AUTHORIZED`",
        ))

    notes = (REPOSITORY_ROOT / "release/current_release_notes.md").read_text(
        encoding="utf-8"
    )
    assert notes.startswith("# Current Engineering Notes\n")
    assert "not a public release announcement" in notes
    if boundary["workstream_status"] == "IMPLEMENTATION_IN_PROGRESS":
        assert "R-H1 remains `IMPLEMENTATION_IN_PROGRESS`" in notes
        assert (
            "At the R-H1B implementation boundary, R-H1C, R-H1D1, and R-H1D2 "
            "had not started"
        ) in " ".join(notes.split())
        assert "This R-H1B implementation note does not itself claim" in notes
        _assert_absent(notes, (
            "R-H1 is `CLOSED_PASS`",
            "External clean-clone validation: `ACCEPTED_PASS`",
            R_H1_AUDIT_PATH,
            R_H1_CHECKPOINT_PATH,
        ))
    else:
        for required in (
            "R-H1 is `CLOSED_PASS`",
            f"implementation_basis_commit: {boundary['implementation_basis_commit']}",
            f"audit_commit: {boundary['audit_commit']}",
            R_H1_AUDIT_PATH,
            R_H1_CHECKPOINT_PATH,
            "External clean-clone validation: `ACCEPTED_PASS`",
            f"Accepted G2-C preflight commit:\n  `{G2C_ACCEPTED_PREFLIGHT_COMMIT}`",
            f"G2-C implementation basis commit:\n  `{G2C_IMPLEMENTATION_BASIS_COMMIT}`",
            f"G2-C audit commit:\n  `{G2C_AUDIT_COMMIT}`",
            G2C_AUDIT_PATH,
            G2C_CHECKPOINT_PATH,
            "G2-C closure_commit_identity: `NOT_SELF_RECORDED`",
            f"Accepted G2-D preflight commit:\n  `{G2D_ACCEPTED_PREFLIGHT_COMMIT}`",
            f"Accepted G2-D v0.3.7 normative donor SHA-256:\n  `{G2D_ACCEPTED_NORMATIVE_DONOR_SHA256}`",
            f"Accepted G2-D repository addendum SHA-256:\n  `{G2D_ACCEPTED_ADDENDUM_SHA256}`",
            "Historical pre-correction G2-D implementation basis commit:\n  "
            f"`{G2D_IMPLEMENTATION_BASIS_COMMIT}`",
            f"Historical pre-correction G2-D audit commit:\n  `{G2D_AUDIT_COMMIT}`",
            G2D_AUDIT_PATH,
            G2D_HISTORICAL_CHECKPOINT_PATH,
            "The old G2-D audit and checkpoint certify pre-correction bytes only",
            f"Corrected G2-D implementation commit:\n  `{G2D_CORRECTED_IMPLEMENTATION_COMMIT}`",
            "Corrected G2-D implementation patch SHA-256:\n  "
            f"`{G2D_CORRECTED_IMPLEMENTATION_PATCH_SHA256}`",
            f"Corrected owner evidence bundle SHA-256:\n  `{G2D_OWNER_EVIDENCE_BUNDLE_SHA256}`",
            f"Independent corrected G2-D re-audit commit:\n  `{G2D_INDEPENDENT_REAUDIT_COMMIT}`",
            G2D_INDEPENDENT_REAUDIT_PATH,
            G2D_INDEPENDENT_REAUDIT_SHA256,
            G2D_CHECKPOINT_PATH,
            f"Corrected G2-D closure commit subject:\n  `{G2D_CLOSURE_SUBJECT}`",
            "Corrected G2-D closure_commit_identity: `NOT_SELF_RECORDED`",
            "G2-C is `CLOSED_PASS`",
            "Historical pre-correction G2-D is\n  "
            "`CLOSED_PASS_ON_PRECORRECTION_BYTES`",
            "Corrected G2-D v0.3.7 is `CLOSED_PASS`",
            "G2-D correction implementation authorization is `true`",
            "implementation bytes exist and are committed",
            "Gate 2 remains `NOT_CLOSED`",
            "G2-E3 is `REVALIDATION_PENDING_ON_CORRECTED_G2D`",
            "G2-E4 is `NOT_STARTED_NOT_AUTHORIZED`",
            "G2-F is `NOT_STARTED / NOT_AUTHORIZED`",
            "The old G2-D audit and checkpoint are\n  "
            "`HISTORICAL_PRECORRECTION_EVIDENCE` only",
            "Independent re-audit and additive successor reclosure are complete",
            "The independent re-audit is evidence, not authority or closure by itself",
            "Public release remains `NOT_CLAIMED`",
            "RC2 remains `NOT_CLAIMED`",
            "Production readiness remains `NOT_CLAIMED`",
            "Production security certification remains `NOT_CLAIMED`",
            "Real-world effects remain zero",
        ):
            assert required in notes
        _assert_absent(notes, (
            "IMPLEMENTATION_IN_PROGRESS",
            "This R-H1B implementation note does not itself claim",
            "R-H1C, R-H1D1, and R-H1D2 had not started",
            "not yet synchronized",
            "NOT_YET_PRESENT",
            "NOT_YET_COMPLETED",
            "G2-C remains `NEXT / NOT_STARTED`",
            "read-only G2-C inventory",
            "G2-D is `NEXT / NOT_STARTED`",
        ))
    assert "Gate 2 remains `NOT_CLOSED`" in notes
    assert "G2-C is `CLOSED_PASS`" in notes
    assert "Corrected G2-D v0.3.7 is `CLOSED_PASS`" in notes
    assert "G2-E3 is `REVALIDATION_PENDING_ON_CORRECTED_G2D`" in notes


def test_current_surfaces_preserve_status_and_licensing_nonclaims() -> None:
    current_text = "\n".join((
        _readme_block(README_PATH.read_bytes()).decode("utf-8"),
        _agents_block(AGENTS_PATH.read_bytes()).decode("utf-8"),
        CLAIM_INDEX_PATH.read_text(encoding="utf-8"),
        LIMITATIONS_PATH.read_text(encoding="utf-8"),
        NOTES_PATH.read_text(encoding="utf-8"),
        (REPOSITORY_ROOT / G2C_CHECKPOINT_PATH).read_text(encoding="utf-8"),
        (REPOSITORY_ROOT / G2D_HISTORICAL_CHECKPOINT_PATH).read_text(
            encoding="utf-8"
        ),
        (REPOSITORY_ROOT / G2D_CHECKPOINT_PATH).read_text(encoding="utf-8"),
        json.dumps(_read_json(OVERLAY_PATH), sort_keys=True),
    ))
    lowered = current_text.lower()

    assert "g2-c is in development" not in lowered
    assert "functional equivalents are licensed" not in lowered
    for affirmative_claim in (
        "title is established",
        "relicensing authority is established",
        "patent clearance is complete",
        "legal review is complete",
    ):
        assert affirmative_claim not in lowered

    boundary = _current_boundary()
    if boundary["workstream_status"] == "IMPLEMENTATION_IN_PROGRESS":
        assert "R-H1 is `IMPLEMENTATION_IN_PROGRESS`" in current_text
        assert "R-H1 remains `IMPLEMENTATION_IN_PROGRESS`" in current_text
        assert "Gate 2 is `NOT_CLOSED`" in current_text
        assert "G2-C is `NEXT / NOT_STARTED`" in current_text
    else:
        assert "R-H1 is `CLOSED_PASS`" in current_text
        assert "Gate 2 remains `NOT_CLOSED`" in current_text
        assert "G2-C is `CLOSED_PASS`" in current_text
        assert "Corrected G2-D v0.3.7 is `CLOSED_PASS`" in current_text
        assert "CLOSED_PASS_ON_PRECORRECTION_BYTES" in current_text
        assert "REVALIDATION_PENDING_ON_CORRECTED_G2D" in current_text
        assert "G2-E4 is `NOT_STARTED_NOT_AUTHORIZED`" in current_text
        assert "G2-F is `NOT_STARTED / NOT_AUTHORIZED`" in current_text
        _assert_absent(current_text, (
            "G2-C remains `NEXT / NOT_STARTED`",
            "G2-C is `NEXT / NOT_STARTED`",
            "G2-C implementation remains `NOT_AUTHORIZED`",
            '"g2c_status": "NEXT_NOT_STARTED"',
            '"g2c_implementation_authorized": false',
            '"g2d_status": "NEXT_NOT_STARTED"',
            '"g2d_implementation_authorized":',
            '"g2e_implementation_authorized":',
            '"g2e_implementation_started":',
        ))


def test_g2c_checkpoint_metadata_scope_and_nonclaims_are_exact() -> None:
    checkpoint_path = REPOSITORY_ROOT / G2C_CHECKPOINT_PATH
    assert checkpoint_path.is_file()
    text = checkpoint_path.read_text(encoding="utf-8")
    required_sections = tuple(f"## {index}. " for index in range(1, 9))
    offsets = tuple(text.index(section) for section in required_sections)
    assert offsets == tuple(sorted(offsets))
    _assert_exactly_once(text, (
        "document_status: CHECKPOINT",
        "checkpoint_id: execution_mode_router_g2_c_v01",
        "checkpoint_status: CLOSED_PASS",
        "gate_id: gate2_g2c_execution_mode_router",
        "gate_slice: G2-C",
        "closure_date: 2026-08-03",
        f"accepted_preflight_commit:\n{G2C_ACCEPTED_PREFLIGHT_COMMIT}",
        f"accepted_preflight_path:\n{G2C_ACCEPTED_PREFLIGHT_PATH}",
        f"accepted_preflight_sha256:\n{G2C_ACCEPTED_PREFLIGHT_SHA256}",
        f"implementation_basis_commit:\n{G2C_IMPLEMENTATION_BASIS_COMMIT}",
        f"audit_commit:\n{G2C_AUDIT_COMMIT}",
        f"audit_path:\n{G2C_AUDIT_PATH}",
        f"audit_sha256:\n{G2C_AUDIT_SHA256}",
        "closure_commit_identity: NOT_SELF_RECORDED",
        "G2-C status: `CLOSED_PASS`",
        "Gate 2 status: `NOT_CLOSED`",
        "G2-D status: `NEXT / NOT_STARTED`",
        "G2-D implementation authorized: `false`",
        "G2-D implementation started: `false`",
        "Human Passport changed: `false`",
        "Public release: `NOT_CLAIMED`",
        "RC2: `NOT_CLAIMED`",
        "Production readiness: `NOT_CLAIMED`",
        "Production security certification: `NOT_CLAIMED`",
        "Publication before Gate 6 closure and separate owner approval: not allowed",
        "Real-world effects: `0`",
    ))
    for path in G2C_CLOSURE_PATHS:
        assert f"`{path}`" in text
    for commit in (
        G2C_ACCEPTED_PREFLIGHT_COMMIT,
        "664bf5c0496d69e8a29dc0dc667f8c009a936222",
        "e0c13919222b40a21b0ed0662c1144a5971209af",
        "80090cfed292346f1bef3a93e2c6d46b45686f83",
        "87fbae934192498a13362f76e9d4af3cd288475b",
        "1782ad40ec64f3c1a1d3960628208110d2c54a57",
        G2C_IMPLEMENTATION_BASIS_COMMIT,
        G2C_AUDIT_COMMIT,
    ):
        assert commit in text
    for required in (
        "Total G2-C types: `13`",
        "Total public G2-C functions: `74`",
        "Public G2-C reasons: `100`",
        "Direct package G2-C attributes: `87`",
        "Canonical domains: `2`",
        "Canonical scenarios: `10`",
        "Exact pipeline order: `17` steps",
        "RuntimeExecutionTopology created by G2-C: `false`",
        "C5 targeted tests: `139 passed`",
        "Complete Router: `392 passed`",
        "Complete Transition: `237 passed`",
        "C5 focused: `4038 passed`",
        "C6 targeted: `13 passed`",
        "Complete Living: `569 passed`",
        "Complete Conformance: `310 passed`",
        "Exact cumulative: `4917 passed`",
        FROZEN_EVIDENCE["completion_manifest"]["sha256"],
        FROZEN_EVIDENCE["integration_seam_index"]["sha256"],
    ):
        assert required in text


def test_g2c_preflight_audit_and_protected_bytes_are_exact() -> None:
    assert _sha256_bytes(
        (REPOSITORY_ROOT / G2C_ACCEPTED_PREFLIGHT_PATH).read_bytes()
    ) == G2C_ACCEPTED_PREFLIGHT_SHA256
    assert _sha256_bytes(
        (REPOSITORY_ROOT / G2C_AUDIT_PATH).read_bytes()
    ) == G2C_AUDIT_SHA256
    assert _sha256_bytes(
        (REPOSITORY_ROOT / G2C_CHECKPOINT_PATH).read_bytes()
    ) == G2C_CHECKPOINT_SHA256
    for path in PROTECTED_PATHS_AT_G2C_AUDIT:
        current = (REPOSITORY_ROOT / path).read_bytes()
        assert current == _git_show(G2C_AUDIT_COMMIT_BASELINE, path), path


def test_g2c_closure_history_has_exact_scope_and_preservation() -> None:
    parent = subprocess.run(
        ("git", "rev-parse", f"{G2C_CLOSURE_COMMIT}^"),
        cwd=REPOSITORY_ROOT,
        check=True,
        capture_output=True,
        text=True,
    ).stdout.strip()
    subject = subprocess.run(
        ("git", "show", "-s", "--format=%s", G2C_CLOSURE_COMMIT),
        cwd=REPOSITORY_ROOT,
        check=True,
        capture_output=True,
        text=True,
    ).stdout.strip()
    changed = subprocess.run(
        (
            "git",
            "diff-tree",
            "--no-commit-id",
            "--name-status",
            "-r",
            "--no-renames",
            G2C_CLOSURE_PARENT,
            G2C_CLOSURE_COMMIT,
        ),
        cwd=REPOSITORY_ROOT,
        check=True,
        capture_output=True,
        text=True,
    ).stdout.splitlines()

    assert parent == G2C_CLOSURE_PARENT
    assert subject == G2C_CLOSURE_SUBJECT
    observed = {
        path: status
        for status, path in (line.split("\t", 1) for line in changed)
    }
    assert tuple(sorted(observed)) == G2C_CLOSURE_PATHS
    assert observed[G2C_CHECKPOINT_PATH] == "A"
    for path in G2C_CLOSURE_PATHS:
        if path != G2C_CHECKPOINT_PATH:
            assert observed[path] == "M"
    assert tuple(observed.values()).count("M") == 8
    assert tuple(observed.values()).count("A") == 1

    historical_passport = "specs/human_passport_v0_25.md"
    assert _git_show(G2C_AUDIT_COMMIT, historical_passport) == _git_show(
        G2C_CLOSURE_COMMIT,
        historical_passport,
    )


def test_g2d_checkpoint_metadata_geometry_and_nonclaims_are_exact() -> None:
    checkpoint_path = REPOSITORY_ROOT / G2D_CHECKPOINT_PATH
    assert checkpoint_path.is_file()
    raw = checkpoint_path.read_bytes()
    text = raw.decode("utf-8")
    assert _sha256_bytes(raw) == G2D_CHECKPOINT_SHA256
    assert checkpoint_path.stat().st_mode & 0o777 == 0o644
    assert raw.endswith(b"\n")
    assert b"\x00" not in raw
    assert b"\r" not in raw

    required_sections = (
        "## 1. Metadata and Closure Boundary",
        "## 2. Corrected Committed Basis",
        "## 3. Authority and Ownership Boundary",
        "## 4. Corrected Geometry and Public Surface",
        "## 5. Accepted Execution Evidence",
        "## 6. Independent Re-Audit",
        "## 7. Exact Additive Reclosure Path Scope",
        "## 8. Historical Evidence and Preserved Nonclaims",
        "## 9. Closing Flags",
    )
    observed_sections = tuple(re.findall(r"^## \d+\..+$", text, re.MULTILINE))
    assert observed_sections == required_sections
    for required in (
        "document_status: CHECKPOINT",
        "checkpoint_id: fractal_runtime_v0_2_g2_d_observed_work_correction_v01",
        "checkpoint_version: v0.1",
        "gate_id: gate2_g2d_fractal_runtime_v0_2_v037_correction",
        "gate_slice: G2-D",
        "corrected_g2d_status: CLOSED_PASS",
        f"accepted_v037_addendum_sha256: {G2D_ACCEPTED_ADDENDUM_SHA256}",
        f"corrected_implementation_commit: {G2D_CORRECTED_IMPLEMENTATION_COMMIT}",
        "corrected_implementation_parent_commit: "
        f"{G2D_CORRECTED_IMPLEMENTATION_PARENT}",
        "corrected_implementation_patch_sha256: "
        f"{G2D_CORRECTED_IMPLEMENTATION_PATCH_SHA256}",
        f"independent_reaudit_commit: {G2D_INDEPENDENT_REAUDIT_COMMIT}",
        f"independent_reaudit_path: {G2D_INDEPENDENT_REAUDIT_PATH}",
        f"independent_reaudit_sha256: {G2D_INDEPENDENT_REAUDIT_SHA256}",
        f"owner_evidence_bundle_sha256: {G2D_OWNER_EVIDENCE_BUNDLE_SHA256}",
        f"closure_commit_subject: {G2D_CLOSURE_SUBJECT}",
        "The future owner reclosure commit cannot be self-recorded inside its own",
    ):
        assert required in text
    assert text.count("closure_commit_identity: NOT_SELF_RECORDED") == 2

    for required in (
        "Public dataclass types: `21`",
        "Serialized types: `18`",
        "Runtime-only types: `3`",
        "Schema definitions: `18`",
        "Canonical-module public functions: `116`",
        "Transition-profile public functions: `6`",
        "Total G2-D public functions: `122`",
        "Canonical module `__all__`: `137`",
        "Direct package G2-D attributes: `143`",
        "Package `__all__`: `19`, unchanged",
        "Validation targets: `35`",
        "Failure stages: `30`",
        "Public reason codes: `220`",
        "Transition rules: `17`",
        "G2-D-local causal decision effects: `14`",
        "`FractalRuntimeExecutionBundleV02` fields: `28`",
        "G2-D test function nodes: `83`",
        "G2-D collected items: `92`",
        "Transition test function nodes: `60`",
        "Transition collected items: `268`",
        "D5 cases: `72`",
        "D5 split: `36/36`",
        "D5 constructive accepted public runs: `10`",
    ):
        assert required in text

    for required in (
        "historical D3 context focused: 2/2 PASS, calls 0/0",
        "release plus maintenance: 23/23 PASS, calls 0/0",
        "complete G2-C: 392/392 PASS, calls 0/0",
        "shared compatibility: 64/64 PASS, calls 0/0",
        "complete G2-D plus Transition: 360/360 PASS, calls 30/30",
        "D5 child 1: PASS",
        "D5 child 2: PASS",
        "D5 cases per process: 72",
        "D5 split per process: 36/36",
        "D5 accepted bundles per process: 10",
        "D5 public calls per process: 27/27",
        "D5 rendered SHA-256: "
        "ec05a8cf9377953abdf84b8a45af07afa3615bcaf78411be6a351fe895663f86",
        "D5 report ID: "
        "frg2dproof_v02:3bf2eb39b8e4e2ea0fe5b7517f677da3b784c43b75d60bce09fb69524c7cc2e1",
        "complete Living: 575/575 PASS, calls 27/27",
        "complete Kernel Conformance: 349/349 PASS, calls 27/27",
        "a770361c93e9fc89434d3e546f8a40c5d4f48a1056e67978dc092be52ee87e5c",
        "05fda5661a4ec50e093e2ee91f986e4b73ce965a6ed99c4023d95d657e153c11",
        "10a8e28f0716353f4155ff89fd3b8197ab685eb449a2e58c5d94653dc3f5bd25",
        "5de16c4117ed9b28de7e91261d7cccc29d9d0fd66954d6bc4a6e8a37e9ad4cb0",
        "3f85c7ff15727b283f323ea63c72387c06253de59b1f8ce3eee3d2d981babeb7",
        "c707a8653fb62ce89d0fe1af4d92e3d82e75e516b50321d92ec3e8b40750b599",
        "530210d9b1361b2d3485909ba3434563ea72d982426a9c2c0200b4e8640a3aa6",
        "38cb6fc8a67ec291ffb6bf637310a983ccc885b3d86325229da354bb75435f08",
        "aa20a31b6dbeb241fa18eda4cae5e88c7e5af9c9e8d1b80a4ec60bcd251f4255",
    ):
        assert required in text

    scope = text.split(required_sections[6], 1)[1].split(required_sections[7], 1)[0]
    observed_scope = tuple(
        match.group(1)
        for match in re.finditer(r"^\d+\. `([^`]+)`", scope, re.MULTILINE)
    )
    assert observed_scope == G2D_CLOSURE_PATHS
    assert G2D_AUDIT_SHA256 in text
    assert G2D_HISTORICAL_CHECKPOINT_SHA256 in text
    for required in (
        "Gate 2 remains `NOT_CLOSED`",
        "G2-E3 remains `REVALIDATION_PENDING_ON_CORRECTED_G2D`",
        "G2-E4 remains `NOT_STARTED_NOT_AUTHORIZED`",
        "No G2-E4, G2-E5, G2-E6, or G2-F implementation is claimed",
        "No production readiness or production security is claimed",
        "No public release or RC2 is claimed",
        "No persistence, distribution, or fault tolerance is claimed",
        "No provider, network, connector, or external-DRS reliability is claimed",
        "No successor baseline, authority, permission, `FinalOutput`, DRS write, or",
        "real-world effect is claimed",
    ):
        assert required in text


def test_g2d_current_manifest_and_overlay_transition_are_exact() -> None:
    manifest = _read_json(MANIFEST_PATH)
    overlay = _read_json(OVERLAY_PATH)
    checkpoint = manifest["current_checkpoint_status"]
    assert isinstance(checkpoint, dict)
    manifest_boundary = checkpoint["current_engineering_boundary_v01"]
    overlay_boundary = overlay["current_engineering_boundary"]
    assert isinstance(manifest_boundary, dict)
    assert manifest_boundary == overlay_boundary
    for key, value in G2D_CURRENT_BOUNDARY_FIELDS.items():
        assert manifest_boundary[key] == value
    assert manifest_boundary["gate2_status"] == "NOT_CLOSED"
    assert manifest_boundary["g2c_status"] == "CLOSED_PASS"
    assert manifest_boundary["public_release_claimed"] is False
    assert manifest_boundary["rc2_claimed"] is False
    assert manifest_boundary["production_readiness_claimed"] is False
    assert manifest_boundary["production_security_certification_claimed"] is False

    parent_manifest = json.loads(
        _git_show(G2D_CLOSURE_PARENT, "specs/machine_manifest_v0_25.json")
    )
    parent_overlay = json.loads(
        _git_show(G2D_CLOSURE_PARENT, "release/current_status_overlay_v01.json")
    )
    parent_manifest_boundary = parent_manifest["current_checkpoint_status"][
        "current_engineering_boundary_v01"
    ]
    parent_overlay_boundary = parent_overlay["current_engineering_boundary"]
    assert parent_manifest_boundary == parent_overlay_boundary
    missing = object()
    changed_fields = {
        key
        for key in set(manifest_boundary) | set(parent_manifest_boundary)
        if manifest_boundary.get(key, missing)
        != parent_manifest_boundary.get(key, missing)
    }
    assert changed_fields == {
        "g2d_status",
        "g2d_corrected_runtime_acceptance_claimed",
        "g2d_corrected_implementation_commit",
        "g2d_corrected_implementation_patch_sha256",
        "g2d_corrected_owner_evidence_bundle_sha256",
        "g2d_independent_reaudit_passed",
        "g2d_independent_reaudit_commit",
        "g2d_independent_reaudit_path",
        "g2d_independent_reaudit_sha256",
        "g2d_additive_reclosure_completed",
        "g2d_corrected_closure_claimed",
        "g2d_corrected_checkpoint_path",
        "g2d_corrected_checkpoint_sha256",
        "g2d_corrected_closure_commit_identity",
    }
    reverted_manifest = copy.deepcopy(manifest)
    reverted_manifest["current_checkpoint_status"][
        "current_engineering_boundary_v01"
    ] = parent_manifest_boundary
    assert reverted_manifest == parent_manifest
    reverted_overlay = copy.deepcopy(overlay)
    reverted_overlay["current_engineering_boundary"] = parent_overlay_boundary
    assert reverted_overlay == parent_overlay

    audit_manifest = json.loads(
        _git_show(G2D_AUDIT_COMMIT, "specs/machine_manifest_v0_25.json")
    )
    audit_overlay = json.loads(
        _git_show(G2D_AUDIT_COMMIT, "release/current_status_overlay_v01.json")
    )
    assert _revert_g2d_boundary_transition(
        manifest,
        overlay=False,
    ) == audit_manifest
    assert _revert_g2d_boundary_transition(
        overlay,
        overlay=True,
    ) == audit_overlay


def test_g2d_binding_and_implementation_bytes_remain_frozen() -> None:
    assert _sha256_bytes(
        (REPOSITORY_ROOT / G2D_ACCEPTED_ADDENDUM_PATH).read_bytes()
    ) == G2D_ACCEPTED_ADDENDUM_SHA256
    assert _sha256_bytes(
        _git_show(G2D_AUDIT_COMMIT, G2D_ACCEPTED_ADDENDUM_PATH)
    ) == G2D_PRECORRECTION_ACCEPTED_ADDENDUM_SHA256
    assert _sha256_bytes(
        _git_show(G2D_AUDIT_COMMIT, "tests/test_fractal_runtime_g2_d_v02.py")
    ) == G2D_PRECORRECTION_TEST_SHA256

    expected = {
        G2D_ACCEPTED_PREFLIGHT_PATH: G2D_ACCEPTED_PREFLIGHT_SHA256,
        G2D_AUDIT_PATH: G2D_AUDIT_SHA256,
        G2D_HISTORICAL_CHECKPOINT_PATH: G2D_HISTORICAL_CHECKPOINT_SHA256,
        G2D_INDEPENDENT_REAUDIT_PATH: G2D_INDEPENDENT_REAUDIT_SHA256,
        G2D_CHECKPOINT_PATH: G2D_CHECKPOINT_SHA256,
        **G2D_FROZEN_IMPLEMENTATION_SHA256,
    }
    for path, sha256 in expected.items():
        raw = (REPOSITORY_ROOT / path).read_bytes()
        assert _sha256_bytes(raw) == sha256, path
    for path in (
        G2D_ACCEPTED_PREFLIGHT_PATH,
        G2D_AUDIT_PATH,
        G2D_HISTORICAL_CHECKPOINT_PATH,
    ):
        assert (REPOSITORY_ROOT / path).read_bytes() == _git_show(
            G2D_INDEPENDENT_REAUDIT_COMMIT,
            path,
        ), path
    assert (REPOSITORY_ROOT / G2D_INDEPENDENT_REAUDIT_PATH).read_bytes() == (
        _git_show(G2D_INDEPENDENT_REAUDIT_COMMIT, G2D_INDEPENDENT_REAUDIT_PATH)
    )
    for path in G2D_FROZEN_IMPLEMENTATION_SHA256:
        assert (REPOSITORY_ROOT / path).read_bytes() == _git_show(
            G2D_CORRECTED_IMPLEMENTATION_COMMIT,
            path,
        ), path
    for path in (
        "release/completion_manifest.json",
        "release/integration_seam_index.json",
        "specs/human_passport_v0_25.md",
    ):
        assert (REPOSITORY_ROOT / path).read_bytes() == _git_show(
            G2D_INDEPENDENT_REAUDIT_COMMIT,
            path,
        )
    implementation_patch = subprocess.run(
        (
            "git",
            "diff",
            "--no-ext-diff",
            "--full-index",
            "--binary",
            G2D_CORRECTED_IMPLEMENTATION_PARENT,
            G2D_CORRECTED_IMPLEMENTATION_COMMIT,
        ),
        cwd=REPOSITORY_ROOT,
        check=True,
        capture_output=True,
    ).stdout
    assert _sha256_bytes(implementation_patch) == (
        G2D_CORRECTED_IMPLEMENTATION_PATCH_SHA256
    )


def test_g2d_closure_scope_is_exact_before_and_after_owner_commit() -> None:
    checkpoint = (REPOSITORY_ROOT / G2D_CHECKPOINT_PATH).read_text(
        encoding="utf-8"
    )
    scope = checkpoint.split("## 7. Exact Additive Reclosure Path Scope", 1)[1].split(
        "## 8. Historical Evidence and Preserved Nonclaims",
        1,
    )[0]
    observed_scope = tuple(
        match.group(1)
        for match in re.finditer(r"^\d+\. `([^`]+)`", scope, re.MULTILINE)
    )
    assert observed_scope == G2D_CLOSURE_PATHS
    assert "closure_commit_identity: NOT_SELF_RECORDED" in checkpoint

    history = subprocess.run(
        ("git", "log", "--all", "--format=%H%x1f%P%x1f%s"),
        cwd=REPOSITORY_ROOT,
        check=True,
        capture_output=True,
        text=True,
    ).stdout.splitlines()
    candidates = []
    for line in history:
        commit, parents, subject = line.split("\x1f", 2)
        if subject == G2D_CLOSURE_SUBJECT:
            candidates.append((commit, tuple(parents.split())))
    if not candidates:
        head = subprocess.run(
            ("git", "rev-parse", "HEAD"),
            cwd=REPOSITORY_ROOT,
            check=True,
            capture_output=True,
            text=True,
        ).stdout.strip()
        assert head == G2D_CLOSURE_PARENT
        status = subprocess.run(
            (
                "git",
                "status",
                "--porcelain=v1",
                "--untracked-files=all",
            ),
            cwd=REPOSITORY_ROOT,
            check=True,
            capture_output=True,
            text=True,
        ).stdout.splitlines()
        expected_status = {
            f" M {path}"
            for path in G2D_CLOSURE_PATHS
            if path != G2D_CHECKPOINT_PATH
        } | {f"?? {G2D_CHECKPOINT_PATH}"}
        assert set(status) == expected_status
        assert subprocess.run(
            ("git", "diff", "--cached", "--name-only"),
            cwd=REPOSITORY_ROOT,
            check=True,
            capture_output=True,
        ).stdout == b""
        return

    assert len(candidates) == 1
    closure_commit, parents = candidates[0]
    assert parents == (G2D_CLOSURE_PARENT,)
    assert closure_commit not in checkpoint
    changed = subprocess.run(
        (
            "git",
            "diff-tree",
            "--no-commit-id",
            "--name-status",
            "-r",
            "--no-renames",
            G2D_CLOSURE_PARENT,
            closure_commit,
        ),
        cwd=REPOSITORY_ROOT,
        check=True,
        capture_output=True,
        text=True,
    ).stdout.splitlines()
    observed = {
        path: status
        for status, path in (line.split("\t", 1) for line in changed)
    }
    assert tuple(sorted(observed)) == G2D_CLOSURE_PATHS
    assert observed[G2D_CHECKPOINT_PATH] == "A"
    assert tuple(observed.values()).count("A") == 1
    assert tuple(observed.values()).count("M") == 8


def test_quantum_roadmap_identity_metadata_and_amendment_are_exact() -> None:
    raw = ROADMAP_PATH.read_bytes()
    text = raw.decode("utf-8", errors="strict")
    lines = text.splitlines()
    metadata_lines = text.split("```text\n", 1)[1].split("\n```", 1)[0].splitlines()

    assert len(raw) == ROADMAP_BYTES
    assert raw.count(b"\n") == ROADMAP_LINES
    assert _sha256_bytes(raw) == ROADMAP_SHA256
    assert b"\x00" not in raw
    assert b"\r" not in raw
    assert raw.endswith(b"\n")
    for required in (
        "document_id: hedgehog_quantum_mathematical_extension_roadmap_v2_0",
        "document_status: FUTURE_POST_GATE6_ENGINEERING_DESIGN",
        "intended_first_repository_version: v2.0",
        (
            "repository_target_path: specs/future/quantum/"
            "hedgehog_quantum_mathematical_extension_roadmap_v2_0.md"
        ),
        "earliest_private_design_commit_point: AFTER_G2C_CLOSED_PASS",
        (
            "implementation_baseline_required: "
            "HEDGEHOG_GATE6_CLOSED_PASS_AND_TAGGED"
        ),
        "current_release_claim: false",
        "normative_for_current_gate_1_to_gate_6_runtime: false",
        "private_commit_is_publication: false",
        "public_prior_art_created_by_private_commit: false",
        "changes_current_six_gate_strategy: NO",
        "physical_qpu_required_for_initial_profile: NO",
        "quantum_advantage_claimed: NO",
        "license: AGPL-3.0-only",
    ):
        assert metadata_lines.count(required) == 1
    assert lines.count("## 19.10. Post-G2-C integration nonclaims") == 1
    assert lines.count("repository_release_spine_test_modified: true") == 1
    assert lines.count("other_tests_modified: false") == 1
    assert lines.count("runtime_tests_modified: false") == 1
    assert lines.count("tests_modified: false") == 0

    retired = REPOSITORY_ROOT / RETIRED_ROADMAP_PATH
    assert not retired.exists()
    history = subprocess.run(
        ("git", "log", "--all", "--format=", "--name-only", "--", RETIRED_ROADMAP_PATH),
        cwd=REPOSITORY_ROOT,
        check=True,
        capture_output=True,
        text=True,
    )
    assert history.stdout.strip() == ""


def test_quantum_future_design_content_is_exact_and_non_implementing() -> None:
    readme = README_PATH.read_text(encoding="utf-8")
    passport = HUMAN_PASSPORT_PATH.read_text(encoding="utf-8")
    math_appendix = MATH_APPENDIX_PATH.read_text(encoding="utf-8")
    limitations = LIMITATIONS_PATH.read_text(encoding="utf-8")
    notes = NOTES_PATH.read_text(encoding="utf-8")

    assert readme.count(README_QUANTUM_SECTION) == 1
    assert readme.count(ROADMAP_PATH.relative_to(REPOSITORY_ROOT).as_posix()) == 1
    assert "Status: future post-Gate-6 design only; not implemented" in readme
    assert "quantum advantage not claimed" in readme

    assert passport.count(PASSPORT_QUANTUM_SECTION) == 1
    assert passport.count("### Computational Substrate Neutrality") == 1
    assert passport.count(
        "Hedgehog does not make intelligence deterministic. "
        "It makes the ownership of action deterministic."
    ) == 1

    assert math_appendix.count(MATH_QUANTUM_SECTION) == 1
    assert math_appendix.endswith(MATH_QUANTUM_SECTION + "\n")
    assert "may be extended after Gate 6" in MATH_QUANTUM_SECTION
    assert "not a claim that the current runtime contains" in MATH_QUANTUM_SECTION

    manifest = _read_json(MANIFEST_PATH)
    hierarchy = manifest["document_hierarchy"]
    assert isinstance(hierarchy, dict)
    profiles = hierarchy["future_design_profiles"]
    assert isinstance(profiles, list)
    matching = [
        profile
        for profile in profiles
        if isinstance(profile, dict)
        and profile.get("profile_id") == "quantum_mathematical_extension_v2_0"
    ]
    assert matching == [QUANTUM_FUTURE_PROFILE]

    assert limitations.count(QUANTUM_LIMITATION) == 1
    for forbidden_claim in (
        "The Quantum-Inspired Mathematical Extension is implemented",
        "Quantum AVF is implemented",
        "quantum advantage is claimed",
    ):
        assert forbidden_claim not in limitations
    assert notes.count(QUANTUM_ENGINEERING_NOTE) == 1
    note_line = next(
        line for line in notes.splitlines() if line == QUANTUM_ENGINEERING_NOTE
    )
    assert "published" not in note_line.lower()
    assert "publicly released" not in note_line.lower()

    assert REPOSITORY_RELEASE_SPINE_TEST_MODIFIED is True
    assert OTHER_TESTS_MODIFIED is False
    assert RUNTIME_TESTS_MODIFIED is False
