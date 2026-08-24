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
    "Current checkpoint: G2-D v0.3.10 contract-only Profile-D and E4 "
    "backpressure-scope correction accepted; implementation pending and "
    "unauthorized."
)
AGENTS_G2D_V039_CLOSED_BEGIN_MARKER = (
    "Current checkpoint: G2-D v0.3.9 t12 revise-no-progress correction "
    "CLOSED_PASS; fresh G2-E3 V06 pending."
)
AGENTS_G2D_V039_CONTRACT_BEGIN_MARKER = (
    "Current checkpoint: G2-D v0.3.9 t12 revise-no-progress correction "
    "contract accepted; implementation pending and unauthorized."
)
AGENTS_G2D_V038_BEGIN_MARKER = (
    "Current checkpoint: G2-D v0.3.8 proof-based whole-run correction "
    "CLOSED_PASS."
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
    "09db4ff2224e59c878b967ba634084d72cd01b36f86edfa5fca2e9750e976ea6"
)
G2D_V039_ACCEPTED_ADDENDUM_SHA256 = (
    "1bbe028a4c757330b4ba94aec461e5bfbb1d1ef7496a68593dc20106c4867445"
)
G2D_V0310_ACCEPTED_ADDENDUM_SHA256 = (
    "1655fbed584e24c980dda723d9e7521b4540ec528128f436ec4f458f7f40563d"
)
G2D_V0310_CONTRACT_TEST_SHA256 = (
    "d2420f07d41e17b9a2f6351f2e2bd01226d14578e1cc01056532d22d8f04d384"
)
G2D_ACCEPTED_NORMATIVE_DONOR_SHA256 = (
    "91264cc9f6177edc1779d3d7553b4ef4484d3db196900380a987b3ae0ccc1454"
)
G2D_CONTROLLING_DESIGN_V03_SHA256 = (
    "7e32560ff19b95a8bd553072d855e8378d749c0f5d17861b7dee9a1f2577c4fe"
)
G2D_V037_ACCEPTED_ADDENDUM_SHA256 = (
    "29983cd17cbefe306de32cf045827fc927280bae5fdb0d7c9db50203a0ea6511"
)
G2D_V037_NORMATIVE_DONOR_SHA256 = (
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
G2D_V038_CONTRACT_CLAIM_ID = (
    "claim_g2d_v038_clarification_contract_accepted_implementation_pending"
)
G2D_V038_CONTRACT_CLAIM_WORDING = (
    "Gate 2 slice G2-D v0.3.8 clarification contract is accepted with "
    "implementation pending and unauthorized."
)
G2D_V038_IMPLEMENTATION_CLAIM_ID = (
    "claim_g2d_v038_proof_based_null_policy_implementation_reaudit_pending"
)
G2D_V038_IMPLEMENTATION_CLAIM_WORDING = (
    "Gate 2 slice G2-D v0.3.8 proof-based whole-run null-policy correction "
    "is implemented with independent re-audit pending."
)
G2D_V038_IMPLEMENTATION_BASIS = (
    "a2d04e03d2b3b1b2b0beeaf407234ae091ae8eb7"
)
G2D_V038_IMPLEMENTATION_COMMIT = (
    "3d9cc2aac45d2923a9d9d5848a8f4f81d011b22e"
)
G2D_V038_IMPLEMENTATION_PATCH_SHA256 = (
    "dbb5e3010e3337b5da0a36cfb69f9597a090be6d14b256699945c5a6fb09c291"
)
G2D_V038_OWNER_EVIDENCE_BUNDLE_SHA256 = (
    "51e913b59a8a82ea3fc5b7688f02dc07e4d9bf15d487d23d879d0b30f6b938f6"
)
G2D_V038_LIFECYCLE_SYNC_COMMIT = (
    "e66c8be08e753077b6a99eeb635bf6fe25ee4b90"
)
G2D_V038_INDEPENDENT_REAUDIT_COMMIT = (
    "edfa42198efa1d03097570d30b6364af1b567050"
)
G2D_V038_INDEPENDENT_REAUDIT_PATH = (
    "docs/audit_reports/"
    "auditor_fractal_runtime_g2_d_v038_proof_based_whole_run_correction_v01.log"
)
G2D_V038_INDEPENDENT_REAUDIT_SHA256 = (
    "acd62cfcf3753a4c02c5f5187e64e8940cf3b3420f97850b0426583465996d67"
)
G2D_V038_INDEPENDENT_REAUDIT_EVIDENCE_SHA256 = (
    "5e43b38b921f7035609e5ef3a33058325c4b529193ad82d87b70a84cd6ff363b"
)
G2D_V038_CHECKPOINT_PATH = (
    "docs/fractal_runtime_v0_2_g2_d_"
    "proof_based_whole_run_correction_checkpoint_v01.md"
)
G2D_V038_CHECKPOINT_SHA256 = (
    "64e2c94f83e8dd2012d0f6f6d8f969bc08832b61194ce24668c6ec7a4eb96e6b"
)
G2D_V038_CLOSURE_SUBJECT = (
    "Close G2-D v0.3.8 proof-based whole-run correction"
)
G2D_V038_CLOSURE_PARENT = G2D_V038_INDEPENDENT_REAUDIT_COMMIT
G2D_V038_CLOSURE_CLAIM_ID = (
    "claim_g2d_v038_proof_based_whole_run_correction_closed_pass"
)
G2D_V038_CLOSURE_CLAIM_WORDING = (
    "Gate 2 slice G2-D Fractal Runtime v0.2 with the accepted v0.3.8 "
    "proof-based whole-run correction is CLOSED_PASS."
)
G2D_V039_CONTRACT_CLAIM_ID = (
    "claim_g2d_v039_t12_revise_no_progress_correction_contract_accepted"
)
G2D_V039_CONTRACT_CLAIM_WORDING = (
    "Gate 2 slice G2-D v0.3.9 t12 revise-no-progress correction contract "
    "is accepted with implementation pending and unauthorized."
)
G2D_V039_IMPLEMENTATION_CLAIM_ID = (
    "claim_g2d_v039_t12_revise_no_progress_implementation_reaudit_pending"
)
G2D_V039_IMPLEMENTATION_CLAIM_WORDING = (
    "Gate 2 slice G2-D v0.3.9 t12 revise-no-progress correction is "
    "implemented, committed, and fully owner-accepted with independent "
    "re-audit pending."
)
G2D_V039_CLOSURE_CLAIM_ID = (
    "claim_g2d_v039_t12_revise_no_progress_correction_closed_pass"
)
G2D_V039_CLOSURE_CLAIM_WORDING = (
    "Historical Gate 2 slice G2-D Fractal Runtime v0.2 with the accepted "
    "v0.3.9 t12 revise-no-progress correction is CLOSED_PASS_ON_V039_BYTES."
)
G2D_V039_BASIS = "4cf427f82a096383ae5873024787c19e56ac0fb5"
G2D_V039_CONTRACT_COMMIT = "8638a3c7d0c2774de161a5e52a8aa62ac9db2aa3"
G2D_V039_CONTRACT_SUBJECT = (
    "Accept G2-D v0.3.9 t12 revise-no-progress correction contract"
)
G2D_V039_CONTRACT_TEST_SHA256 = (
    "b91b66dced57ab32779fc2b18ad567c2ab176f953fc2dba67205d268cf9edec5"
)
G2D_V039_RELEASE_CONSUMER_MAINTENANCE_COMMIT = (
    "b9d95605b960ce3837446b1bf38b665ce16f03fb"
)
G2D_V039_IMPLEMENTATION_RUNTIME_SHA256 = (
    "e1201de1f03d8d33353ae9edf026879214afab25eca6dcb9cd1670779b53bd08"
)
G2D_V039_IMPLEMENTATION_TEST_SHA256 = (
    "8119d7bf3647652a71754e62baeccb12665b323dc3b36c762c841e4ad56ef5bf"
)
G2D_V039_IMPLEMENTATION_PATCH_SHA256 = (
    "442b68cdff95fc06a1176fcb4c3d64323110e197b771d5e932db5215b3d8bc13"
)
G2D_V039_IMPLEMENTATION_PATCH_BYTES = 26107
G2D_V039_IMPLEMENTATION_PATCH_LF = 560
G2D_V039_IMPLEMENTATION_COMMIT = (
    "7a915111e974bc62ff2a7bfe70e8d5a911da03fd"
)
G2D_V039_IMPLEMENTATION_PARENT = G2D_V039_RELEASE_CONSUMER_MAINTENANCE_COMMIT
G2D_V039_OWNER_EVIDENCE_BUNDLE_SHA256 = (
    "fac5596484fb5207632ec6083eeaf2d3cb7d2fa4cdb8f726762d1d635e9e34a0"
)
G2D_V039_RUNTIME_IMPLEMENTATION_STATUS = (
    "IMPLEMENTED_COMMITTED_FULL_ACCEPTANCE_PASS"
)
G2D_V039_IMPLEMENTATION_PATHS = (
    "hedgehog/kernel/fractal_runtime_v02.py",
    "tests/test_fractal_runtime_g2_d_v02.py",
)
G2D_V039_RELEASE_CONSUMER_MAINTENANCE_SUBJECT = (
    "Align G2-D v0.3.9 release tests with implementation candidate"
)
G2D_V039_IMPLEMENTATION_SUBJECT = (
    "Implement G2-D v0.3.9 t12 revise-no-progress correction"
)
G2D_V039_LIFECYCLE_SYNC_SUBJECT = (
    "Synchronize G2-D v0.3.9 post-implementation lifecycle"
)
G2D_V039_LIFECYCLE_SYNC_COMMIT = (
    "f7feaa3170717ee6347a6d3d531f376ec857041a"
)
G2D_V039_INDEPENDENT_REAUDIT_COMMIT = (
    "04892249fbac7ebb83b80e0a2c65c6b1b7a85c7a"
)
G2D_V039_INDEPENDENT_REAUDIT_SUBJECT = (
    "Add G2-D v0.3.9 t12 correction independent re-audit"
)
G2D_V039_INDEPENDENT_REAUDIT_PATH = (
    "docs/audit_reports/"
    "auditor_fractal_runtime_g2_d_v039_t12_revise_no_progress_correction_v01.log"
)
G2D_V039_INDEPENDENT_REAUDIT_SHA256 = (
    "83d4b4451a2d00b0a44451cc5c37917cf409a0e0ecc8b1a75575d7df1caf71e8"
)
G2D_V039_INDEPENDENT_REAUDIT_EVIDENCE_SHA256 = (
    "552413a978f371f297ac6454ece8d502847473f93009e44cd2ae89bc9088df81"
)
G2D_V039_LIFECYCLE_SYNC_EVIDENCE_SHA256 = (
    "a62578f36418771508289f879be06215b63115bac545587bd97f167507ae86bc"
)
G2D_V039_CHECKPOINT_PATH = (
    "docs/fractal_runtime_v0_2_g2_d_"
    "t12_revise_no_progress_correction_checkpoint_v01.md"
)
G2D_V039_CHECKPOINT_SHA256 = (
    "6b8f12c46acc93742f2f36e2186d8e076b63c9d5392fb8212cd89d78147d6c0b"
)
G2D_V039_CLOSURE_SUBJECT = (
    "Close G2-D v0.3.9 t12 revise-no-progress correction"
)
G2D_V039_PRIMARY_PARKED_PATCH_SHA256 = (
    "3c08807bcf8545b95ceca22ec13f1aa1cb2e8d2669ad72cf269ac2d077163aff"
)
G2D_V0310_CONTRACT_CLAIM_ID = (
    "claim_g2d_v0310_profile_d_and_e4_backpressure_scope_contract_accepted"
)
G2D_V0310_CONTRACT_CLAIM_WORDING = (
    "G2-D v0.3.10 Profile-D t12 projection correction and G2-E4 "
    "strict-selective backpressure-scope reconciliation contract is accepted; "
    "implementation is pending and unauthorized."
)
G2D_V0310_BASIS = "36c43db9045d56666e961b54b4f9b272079f41a8"
G2D_V0310_CONTRACT_COMMIT = "99d6fbf3870b839852a4d3ea659eed548381f5ce"
G2D_V0310_RELEASE_CONSUMER_MAINTENANCE_ACTIVATED = True
G2D_V0310_CONTRACT_SUBJECT = (
    "Accept G2-D v0.3.10 Profile-D and E4 scope correction contract"
)
G2D_V0310_RELEASE_CONSUMER_MAINTENANCE_SUBJECT = (
    "Align G2-D v0.3.10 release tests with implementation candidate"
)
G2D_V0310_IMPLEMENTATION_SUBJECT = (
    "Implement G2-D v0.3.10 Profile-D t12 projection correction"
)
G2D_V0310_RELEASE_CONSUMER_MAINTENANCE_PATHS = (
    "tests/test_repository_release_spine_v01.py",
)
G2D_V0310_IMPLEMENTATION_PATHS = (
    "hedgehog/kernel/fractal_runtime_v02.py",
    "tests/test_fractal_runtime_g2_d_v02.py",
)
G2D_V0310_IMPLEMENTATION_RUNTIME_SHA256 = (
    "917caabd0c3e2033cfc57be71771abf9a87558e945b3d4f6713c48cd8796aa01"
)
G2D_V0310_IMPLEMENTATION_RUNTIME_BYTES = 802334
G2D_V0310_IMPLEMENTATION_RUNTIME_LF = 18306
G2D_V0310_IMPLEMENTATION_TEST_SHA256 = (
    "18c69854153d6ad85359f1bac984f50dab1743c3459b5547ae56305cfd5a89a4"
)
G2D_V0310_IMPLEMENTATION_TEST_BYTES = 586939
G2D_V0310_IMPLEMENTATION_TEST_LF = 13528
G2D_V0310_IMPLEMENTATION_PATCH_SHA256 = (
    "f6ce9ada6fc2c557f0f1647d018b8f26b7d9a3d03ff3786dc5dda2a8c646ce94"
)
G2D_V0310_IMPLEMENTATION_PATCH_BYTES = 34943
G2D_V0310_IMPLEMENTATION_PATCH_LF = 747
G2D_V0310_INDEPENDENT_REAUDIT_PATH = (
    "docs/audit_reports/"
    "auditor_fractal_runtime_g2_d_v0310_profile_d_t12_revise_projection_"
    "correction_v01.log"
)
G2D_V0310_CHECKPOINT_PATH = (
    "docs/fractal_runtime_v0_2_g2_d_profile_d_t12_revise_projection_"
    "correction_checkpoint_v01.md"
)
G2D_V0310_LIFECYCLE_SYNC_SUBJECT = 'Synchronize G2-D v0.3.10 post-implementation lifecycle'
G2D_V0310_LIFECYCLE_SYNC_PATHS = ('AGENTS.md',
 'README.md',
 'release/claim_to_evidence_index.md',
 'release/current_limitations.md',
 'release/current_release_notes.md',
 'release/current_status_overlay_v01.json',
 'specs/machine_manifest_v0_25.json',
 'tests/test_repository_release_spine_v01.py')
G2D_V0310_LIFECYCLE_SYNC_COMMIT = '5dbf1116afbb010b8737e6fa3150907b6e29ae48'
G2D_V0310_IMPLEMENTATION_COMMIT = '41db6c6bfbf787c04d288c5ddb40e285118d06c1'
G2D_V0310_IMPLEMENTATION_PARENT = '2c9f2060ab0abf6dffa270dac4ffd7095d091d08'
G2D_V0310_IMPLEMENTATION_PATCH_SHA256 = 'f6ce9ada6fc2c557f0f1647d018b8f26b7d9a3d03ff3786dc5dda2a8c646ce94'
G2D_V0310_OWNER_EVIDENCE_BUNDLE_SHA256 = '19b8695bafba7f9fff04eb9045d1e60b7e319d1d72f52c0f05724499c64de7d0'
G2D_V0310_INDEPENDENT_REAUDIT_SUBJECT = 'Add G2-D v0.3.10 Profile-D correction independent re-audit'
G2D_V0310_INDEPENDENT_REAUDIT_COMMIT = '5001db910fcc6e68cbe03a527eccd9455d7bf063'
G2D_V0310_CLOSURE_SUBJECT = 'Close G2-D v0.3.10 Profile-D t12 revise projection correction'
G2D_V0310_RECLOSURE_PATHS = ('AGENTS.md',
 'README.md',
 'docs/fractal_runtime_v0_2_g2_d_profile_d_t12_revise_projection_correction_checkpoint_v01.md',
 'release/claim_to_evidence_index.md',
 'release/current_limitations.md',
 'release/current_release_notes.md',
 'release/current_status_overlay_v01.json',
 'specs/machine_manifest_v0_25.json',
 'tests/test_repository_release_spine_v01.py')
G2D_V0310_E4_CODE_SUBJECT = 'Close G2-E4 anti-gaming acceptance correction'
G2D_V0310_E4_CODE_PATHS = ('hedgehog/kernel/continuous_delta_runtime_v01.py',
 'tests/test_continuous_delta_runtime_g2_e_v01.py')
G2D_V0310_E4_CODE_COMMIT = '21176be090cab9aa9b8ea9cce2ae052bed8039da'
G2D_V0310_FINAL_SYNC_SUBJECT = 'Synchronize G2-E3 revalidation and G2-E4 acceptance'
G2D_V0310_FINAL_SYNC_PATHS = ('AGENTS.md',
 'README.md',
 'release/claim_to_evidence_index.md',
 'release/current_limitations.md',
 'release/current_release_notes.md',
 'release/current_status_overlay_v01.json',
 'specs/machine_manifest_v0_25.json',
 'tests/test_repository_release_spine_v01.py')
AGENTS_G2D_V0310_CURRENT_BEGIN_MARKER = 'Current checkpoint: G2-D v0.3.10 Profile-D correction CLOSED_PASS.'
G2D_V0310_IMPLEMENTATION_CLAIM_ID = "claim_g2d_v0310_profile_d_t12_projection_implementation_reaudit_pending"
G2D_V0310_CLOSURE_CLAIM_ID = "claim_g2d_v0310_profile_d_t12_projection_correction_closed_pass"
G2E4_V0310_ACCEPTANCE_CLAIM_ID = "claim_g2e_v013_e4_anti_gaming_acceptance_pass"
G2D_V0310_SUCCESSOR_CLAIM_IDS = ('claim_g2d_v0310_profile_d_t12_projection_implementation_reaudit_pending',
 'claim_g2d_v0310_profile_d_t12_projection_correction_closed_pass',
 'claim_g2e_v013_e4_anti_gaming_acceptance_pass')
G2D_V0310_EXPECTED_SUCCESSOR_PHASE = 'final_e4_sync'
G2D_V0310_SUCCESSOR_EXPECTED_FIELDS = {'g2d_status': 'CLOSED_PASS',
 'g2d_contract_status': 'ACCEPTED_COMMITTED',
 'g2d_contract_commit': '99d6fbf3870b839852a4d3ea659eed548381f5ce',
 'g2d_release_consumer_maintenance_commit': '2c9f2060ab0abf6dffa270dac4ffd7095d091d08',
 'g2d_correction_implementation_authorized': False,
 'g2d_implementation_action_open': False,
 'g2d_corrected_implementation_exists': True,
 'g2d_contract_only_claim': False,
 'g2d_corrected_runtime_acceptance_claimed': True,
 'g2d_runtime_implementation_status': 'IMPLEMENTED_COMMITTED_FULL_ACCEPTANCE_PASS',
 'g2d_full_owner_acceptance_passed': True,
 'g2d_corrected_implementation_committed': True,
 'g2d_corrected_implementation_commit': '41db6c6bfbf787c04d288c5ddb40e285118d06c1',
 'g2d_corrected_implementation_parent_commit': '2c9f2060ab0abf6dffa270dac4ffd7095d091d08',
 'g2d_corrected_implementation_patch_sha256': 'f6ce9ada6fc2c557f0f1647d018b8f26b7d9a3d03ff3786dc5dda2a8c646ce94',
 'g2d_corrected_owner_evidence_bundle_sha256': '19b8695bafba7f9fff04eb9045d1e60b7e319d1d72f52c0f05724499c64de7d0',
 'g2d_independent_reaudit_required': True,
 'g2d_independent_reaudit_passed': True,
 'g2d_independent_reaudit_commit': '5001db910fcc6e68cbe03a527eccd9455d7bf063',
 'g2d_independent_reaudit_path': 'docs/audit_reports/auditor_fractal_runtime_g2_d_v0310_profile_d_t12_revise_projection_correction_v01.log',
 'g2d_independent_reaudit_sha256': 'b1ff61f42158d914b9afcf48e0d3ef5f9f980288d134130031e79c631f5101b6',
 'g2d_additive_reclosure_required': True,
 'g2d_additive_reclosure_completed': True,
 'g2d_corrected_closure_claimed': True,
 'g2d_corrected_checkpoint_path': 'docs/fractal_runtime_v0_2_g2_d_profile_d_t12_revise_projection_correction_checkpoint_v01.md',
 'g2d_corrected_checkpoint_sha256': '226a96cb345a94e2f631fc7b914aafb5bbb7e3aaede924f10d3045d7491f72c0',
 'g2d_corrected_closure_commit_identity': 'NOT_SELF_RECORDED',
 'g2d_v0310_implementation_authorized': False,
 'g2d_v0310_implementation_started': True,
 'g2d_v0310_corrected_implementation_exists': True,
 'g2d_v0310_corrected_implementation_committed': True,
 'g2d_v0310_independent_reaudit_required': True,
 'g2d_v0310_independent_reaudit_passed': True,
 'g2d_v0310_additive_reclosure_required': True,
 'g2d_v0310_additive_reclosure_completed': True,
 'g2d_v0310_status': 'CLOSED_PASS',
 'g2e3_status': 'IMPLEMENTED_COMMITTED_ACCEPTANCE_PASS_ON_CORRECTED_G2D',
 'g2e3_post_v0310_implementation_status': 'IMPLEMENTED_COMMITTED_ACCEPTANCE_PASS_ON_CORRECTED_G2D',
 'g2e3_fresh_v06_required_after_v0310_reclosure': False,
 'g2e3_v0310_fresh_v06_passed': True,
 'g2e3_v0310_fresh_v06_archive_sha256': '8301e6886ab1400fabffe1c850205c73b02919dc844dffe119a42550eb92b4ba',
 'g2e3_v0310_fresh_source_observation_sha256': 'fb2687f08911e5420d03ec40fef02fde3794edc1e03d637df9f8d26c062b3f3c',
 'g2e3_v0310_fresh_member_observation_sha256': 'fbd40637c2082ec385204a53a2173695a2247b6cd8e908f34349d75d6a1e3467',
 'g2e3_v0310_fresh_member_identities_sha256': '8924a3971624823805d2ed7b99adff5a68ca96d07aa67bb516d744e7f3877b39',
 'g2e4_strict_subtree_status': 'IMPLEMENTED_COMMITTED_PASS',
 'g2e4_anti_gaming_acceptance': 'PASS',
 'g2e4_anti_gaming_correction_authorized': False,
 'gate2_status': 'NOT_CLOSED',
 'g2e3_post_reclosure_v06_passed': True,
 'g2e3_post_reclosure_v06_archive_sha256': '8301e6886ab1400fabffe1c850205c73b02919dc844dffe119a42550eb92b4ba',
 'g2e3_baseline_source_observation_sha256': 'fb2687f08911e5420d03ec40fef02fde3794edc1e03d637df9f8d26c062b3f3c',
 'g2e3_baseline_member_observation_sha256': 'fbd40637c2082ec385204a53a2173695a2247b6cd8e908f34349d75d6a1e3467',
 'g2e3_baseline_member_identities_sha256': '8924a3971624823805d2ed7b99adff5a68ca96d07aa67bb516d744e7f3877b39',
 'g2e4_contract_status': 'HISTORICAL_CONTRACT_HOP_COMPLETED',
 'g2e4_status': 'IMPLEMENTED_COMMITTED_ACCEPTANCE_PASS',
 'g2e4_acceptance_correction_commit': '21176be090cab9aa9b8ea9cce2ae052bed8039da',
 'g2e4_acceptance_correction_patch_sha256': 'ea1b030bb40e52aeb30ea5d49599ba2e3a59f50398ef8d74234ab77e30842157',
 'g2e4_acceptance_owner_evidence_sha256': '92390ad076307a73473f1bb22b65748bbc2e25bcdccd6fe0250312d26b124b31',
 'g2e5_status': 'NOT_STARTED_NOT_AUTHORIZED',
 'g2e6_status': 'NOT_STARTED_NOT_AUTHORIZED',
 'g2f_status': 'NOT_STARTED_NOT_AUTHORIZED',
 'public_release_claimed': False,
 'rc2_claimed': False,
 'production_readiness_claimed': False,
 'production_security_certification_claimed': False,
 'g2e3_post_corrected_g2d_landing_status': 'IMPLEMENTED_COMMITTED_ACCEPTANCE_PASS_ON_CORRECTED_G2D'}
G2D_TRANSITION_FACADE_CONSUMER_MAINTENANCE_COMMIT = (
    "a2d04e03d2b3b1b2b0beeaf407234ae091ae8eb7"
)
G2D_TRANSITION_FACADE_CONSUMER_MAINTENANCE_PARENT = (
    "51ffa86fbabfb81bf5b23ed5c7993b3251e7fe9d"
)
G2D_TRANSITION_FACADE_CONSUMER_MAINTENANCE_SUBJECT = (
    "Align G2-E Transition facade test with kernel package facade"
)
G2D_TRANSITION_FACADE_CONSUMER_PREIMAGE_SHA256 = (
    "6543bb228f6c9c8a8b064f55fb55b84e426320b51ca12243b04db9f8efa1ac67"
)
G2D_TRANSITION_FACADE_CONSUMER_SHA256 = (
    "c8c115d4120823ca30bc05c5eb0a475a1278060713a3faf903c5e4309f26f111"
)
G2D_FACADE_MAINTENANCE_COMMIT = (
    "10aaf866da071cfd6ff460182bc64b4311477bff"
)
G2D_G2C_FACADE_CONSUMER_MAINTENANCE_COMMIT = (
    "51ffa86fbabfb81bf5b23ed5c7993b3251e7fe9d"
)
G2D_G2C_FACADE_CONSUMER_MAINTENANCE_PARENT = (
    "10aaf866da071cfd6ff460182bc64b4311477bff"
)
G2D_G2C_FACADE_CONSUMER_MAINTENANCE_SUBJECT = (
    "Align G2-C facade test with lazy G2-E package facade"
)
G2D_G2C_FACADE_CONSUMER_PREIMAGE_SHA256 = (
    "feb7807db6dc750acfad3395cacca72dd398cbbd47cf980463ce0b5ea544a33e"
)
G2D_G2C_FACADE_CONSUMER_SHA256 = (
    "571ceff174bcfe0b5b94f3bf94c957de90503b3a8590a784d320887bcb86261d"
)
G2D_FACADE_MAINTENANCE_PARENT = (
    "66c5d04003f29c19a736d5029b09c89b17d5dd65"
)
G2D_FACADE_MAINTENANCE_SUBJECT = (
    "Repair kernel G2-E facade import cycle"
)
G2D_FACADE_MAINTENANCE_PREIMAGE_SHA256 = {
    "hedgehog/kernel/__init__.py": (
        "0925a20b439a7fc8be28fa4a9db353b164e57c74a93805b103465268d8d75b17"
    ),
    "tests/test_repository_maintenance_contract_v01.py": (
        "22d9c6687500079954ddb3f57e8937516f27d54de27d9f2034957d033b152d81"
    ),
}
G2D_FACADE_MAINTENANCE_SHA256 = {
    "hedgehog/kernel/__init__.py": (
        "99b2847d4dac09827b0a56cd820302052139654314ff02789363480cc98df4e0"
    ),
    "tests/test_repository_maintenance_contract_v01.py": (
        "be4fe799e9e18efa2ecf436f22fd70a80bd764b2783b9f6d9d238145cc26130c"
    ),
}
G2D_V038_RUNTIME_SHA256 = (
    "33d42b280944783adc1e4a2ee86bf6ecf54ff9026bb67a0036cf0f98f2ddb00f"
)
G2D_V038_TEST_SHA256 = (
    "59a370b9d642f473f0f827af941a12cca93ea1349d2861cd1ef4243f3507bae3"
)
G2D_CLOSURE_SUBJECT = "Close G2-D v0.3.7 observed-work correction"
G2D_CLOSURE_PARENT = G2D_INDEPENDENT_REAUDIT_COMMIT
G2D_CLOSURE_COMMIT = "48ab284ee7c1ba33400f0d0c7fe5656b4249b839"

G2E_ACCEPTED_PREFLIGHT_PATH = (
    "docs/continuous_delta_runtime_v0_1_g2_e_preflight_v01.md"
)
G2E_ACCEPTED_PREFLIGHT_SHA256 = (
    "83f36c9b2d47619a8c8ab997eba6b8ef16f2a3ab07cb3aecfc77ea82469f0d8b"
)
G2E_ACCEPTED_ADDENDUM_PATH = (
    "docs/continuous_delta_runtime_v0_1_g2_e_"
    "post_acceptance_contract_addendum_v01.md"
)
G2E_ACCEPTED_ADDENDUM_SHA256 = (
    "2b982ecaed9dc5cea2373676d816840ca683c8190b69516c14688cbba9e452f8"
)
G2E_V012_ADDENDUM_SHA256 = (
    "1041dbf3da320557d5eca948a13d0c4737e4e9b9ffac64c9453c97503527ca4c"
)
G2E_V013_NORMATIVE_DONOR_SHA256 = (
    "17b9384db812d5078301a9b3d4335dd3351481e117929b6b04c1ff6a137f4a56"
)
G2E3_V06_ARCHIVE_SHA256 = (
    "d8630f68af26ab9ae1d925c0e236b71e1e2ac3e759a39f642af2fcf432e4ead3"
)
G2E3_V038_V06_ARCHIVE_SHA256 = (
    "09bfe734048febfcf1ea32cc35195fb494b73c36a360163c8329aaf5e3fc2ca8"
)
G2E3_BASELINE_SOURCE_OBSERVATION_SHA256 = (
    "fb2687f08911e5420d03ec40fef02fde3794edc1e03d637df9f8d26c062b3f3c"
)
G2E3_BASELINE_MEMBER_OBSERVATION_SHA256 = (
    "fbd40637c2082ec385204a53a2173695a2247b6cd8e908f34349d75d6a1e3467"
)
G2E3_BASELINE_MEMBER_IDENTITIES_SHA256 = (
    "8924a3971624823805d2ed7b99adff5a68ca96d07aa67bb516d744e7f3877b39"
)
G2E4_PUBLIC_SEAM_REGISTER_SHA256 = (
    "a10be3df58ed7fbf32fcb853c7de93f76eec5b3070120b0f895b27340cf2aed2"
)
G2E4_TWO_ROOT_PAIR_REGISTER_SHA256 = (
    "a8a8fd530d95ec4bce8a0faf14044c8b98f53973651cf65784a717d69e02ce33"
)
G2E_CONTRACT_CLAIM_ID = (
    "claim_g2e_v013_e4_contract_accepted_implementation_pending"
)
G2E_CONTRACT_CLAIM_WORDING = (
    "Gate 2 slice G2-E v0.1.3 E4 contract is accepted with implementation "
    "pending and unauthorized."
)

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

G2D_V038_CLOSURE_PATHS = (
    G2D_V038_CHECKPOINT_PATH,
    "AGENTS.md",
    "README.md",
    "specs/machine_manifest_v0_25.json",
    "release/current_status_overlay_v01.json",
    "release/claim_to_evidence_index.md",
    "release/current_limitations.md",
    "release/current_release_notes.md",
    "tests/test_repository_release_spine_v01.py",
)

G2D_V038_IMPLEMENTATION_PATHS = (
    "hedgehog/kernel/fractal_runtime_v02.py",
    "tests/test_fractal_runtime_g2_d_v02.py",
    "AGENTS.md",
    "README.md",
    "specs/machine_manifest_v0_25.json",
    "release/current_status_overlay_v01.json",
    "release/claim_to_evidence_index.md",
    "release/current_limitations.md",
    "release/current_release_notes.md",
    "tests/test_repository_release_spine_v01.py",
)

G2D_V039_CONTRACT_PATHS = (
    "docs/fractal_runtime_v0_2_g2_d_post_acceptance_contract_addendum_v01.md",
    "tests/test_fractal_runtime_g2_d_v02.py",
    "AGENTS.md",
    "README.md",
    "specs/machine_manifest_v0_25.json",
    "release/current_status_overlay_v01.json",
    "release/claim_to_evidence_index.md",
    "release/current_limitations.md",
    "release/current_release_notes.md",
    "tests/test_repository_release_spine_v01.py",
)

G2D_V0310_CONTRACT_PATHS = G2D_V039_CONTRACT_PATHS

G2D_V039_LIFECYCLE_SYNC_PATHS = (
    "AGENTS.md",
    "README.md",
    "release/claim_to_evidence_index.md",
    "release/current_limitations.md",
    "release/current_release_notes.md",
    "release/current_status_overlay_v01.json",
    "specs/machine_manifest_v0_25.json",
    "tests/test_repository_release_spine_v01.py",
)

G2D_V039_RECLOSURE_PATHS = (
    "AGENTS.md",
    "README.md",
    G2D_V039_CHECKPOINT_PATH,
    "release/claim_to_evidence_index.md",
    "release/current_limitations.md",
    "release/current_release_notes.md",
    "release/current_status_overlay_v01.json",
    "specs/machine_manifest_v0_25.json",
    "tests/test_repository_release_spine_v01.py",
)

G2D_V037_RECLOSURE_BOUNDARY_FIELDS = {
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
    "g2d_accepted_normative_donor_sha256": G2D_V037_NORMATIVE_DONOR_SHA256,
    "g2d_accepted_repository_addendum_sha256": (
        G2D_V037_ACCEPTED_ADDENDUM_SHA256
    ),
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
}

G2D_CURRENT_BOUNDARY_FIELDS = {'g2d_status': 'CLOSED_PASS',
 'g2d_contract_status': 'ACCEPTED_COMMITTED',
 'g2d_contract_commit': '99d6fbf3870b839852a4d3ea659eed548381f5ce',
 'g2d_release_consumer_maintenance_commit': '2c9f2060ab0abf6dffa270dac4ffd7095d091d08',
 'g2d_correction_implementation_authorized': False,
 'g2d_implementation_action_open': False,
 'g2d_corrected_implementation_exists': True,
 'g2d_contract_only_claim': False,
 'g2d_corrected_runtime_acceptance_claimed': True,
 'g2d_runtime_implementation_status': 'IMPLEMENTED_COMMITTED_FULL_ACCEPTANCE_PASS',
 'g2d_full_owner_acceptance_passed': True,
 'g2d_corrected_implementation_committed': True,
 'g2d_corrected_implementation_commit': '41db6c6bfbf787c04d288c5ddb40e285118d06c1',
 'g2d_corrected_implementation_parent_commit': '2c9f2060ab0abf6dffa270dac4ffd7095d091d08',
 'g2d_corrected_implementation_patch_sha256': 'f6ce9ada6fc2c557f0f1647d018b8f26b7d9a3d03ff3786dc5dda2a8c646ce94',
 'g2d_corrected_owner_evidence_bundle_sha256': '19b8695bafba7f9fff04eb9045d1e60b7e319d1d72f52c0f05724499c64de7d0',
 'g2d_independent_reaudit_required': True,
 'g2d_independent_reaudit_passed': True,
 'g2d_independent_reaudit_commit': '5001db910fcc6e68cbe03a527eccd9455d7bf063',
 'g2d_independent_reaudit_path': 'docs/audit_reports/auditor_fractal_runtime_g2_d_v0310_profile_d_t12_revise_projection_correction_v01.log',
 'g2d_independent_reaudit_sha256': 'b1ff61f42158d914b9afcf48e0d3ef5f9f980288d134130031e79c631f5101b6',
 'g2d_additive_reclosure_required': True,
 'g2d_additive_reclosure_completed': True,
 'g2d_corrected_closure_claimed': True,
 'g2d_corrected_checkpoint_path': 'docs/fractal_runtime_v0_2_g2_d_profile_d_t12_revise_projection_correction_checkpoint_v01.md',
 'g2d_corrected_checkpoint_sha256': '226a96cb345a94e2f631fc7b914aafb5bbb7e3aaede924f10d3045d7491f72c0',
 'g2d_corrected_closure_commit_identity': 'NOT_SELF_RECORDED',
 'g2d_old_audit_checkpoint_class': 'HISTORICAL_PRECORRECTION_EVIDENCE',
 'g2d_accepted_normative_donor_sha256': '91264cc9f6177edc1779d3d7553b4ef4484d3db196900380a987b3ae0ccc1454',
 'g2d_accepted_repository_addendum_sha256': '1655fbed584e24c980dda723d9e7521b4540ec528128f436ec4f458f7f40563d',
 'g2d_v037_implementation_nonconformance': True,
 'g2d_v038_implementation_nonconformance': True,
 'g2d_v038_contract_semantics_changed': False,
 'g2d_v038_role': 'EXPLICIT_CLARIFICATION_AND_LIFECYCLE_REOPENING',
 'g2d_v038_directional_draft_review': 'APPROVE_WITH_MANDATORY_OVERLAY',
 'g2d_v038_directional_draft_sha256': '91264cc9f6177edc1779d3d7553b4ef4484d3db196900380a987b3ae0ccc1454',
 'g2d_v038_controlling_design_v03_sha256': '7e32560ff19b95a8bd553072d855e8378d749c0f5d17861b7dee9a1f2577c4fe',
 'g2d_v038_accepted_addendum_sha256': '09db4ff2224e59c878b967ba634084d72cd01b36f86edfa5fca2e9750e976ea6',
 'g2d_v038_status': 'CLOSED_PASS_ON_V038_BYTES',
 'g2d_v038_implementation_authorized': True,
 'g2d_v038_implementation_started': True,
 'g2d_v038_corrected_implementation_exists': True,
 'g2d_v038_corrected_implementation_committed': True,
 'g2d_v038_corrected_implementation_commit': '3d9cc2aac45d2923a9d9d5848a8f4f81d011b22e',
 'g2d_v038_corrected_implementation_patch_sha256': 'dbb5e3010e3337b5da0a36cfb69f9597a090be6d14b256699945c5a6fb09c291',
 'g2d_v038_corrected_owner_evidence_bundle_sha256': '51e913b59a8a82ea3fc5b7688f02dc07e4d9bf15d487d23d879d0b30f6b938f6',
 'g2d_v038_full_acceptance_pending_owner': False,
 'g2d_v038_independent_reaudit_passed': True,
 'g2d_v038_independent_reaudit_commit': 'edfa42198efa1d03097570d30b6364af1b567050',
 'g2d_v038_independent_reaudit_path': 'docs/audit_reports/auditor_fractal_runtime_g2_d_v038_proof_based_whole_run_correction_v01.log',
 'g2d_v038_independent_reaudit_sha256': 'acd62cfcf3753a4c02c5f5187e64e8940cf3b3420f97850b0426583465996d67',
 'g2d_v038_additive_reclosure_completed': True,
 'g2d_v038_corrected_closure_claimed': True,
 'g2d_v038_checkpoint_path': 'docs/fractal_runtime_v0_2_g2_d_proof_based_whole_run_correction_checkpoint_v01.md',
 'g2d_v038_checkpoint_sha256': '64e2c94f83e8dd2012d0f6f6d8f969bc08832b61194ce24668c6ec7a4eb96e6b',
 'g2d_v038_reclosure_commit': '4cf427f82a096383ae5873024787c19e56ac0fb5',
 'g2d_v039_contract_semantics_changed': False,
 'g2d_v039_role': 'EXPLICIT_IMPLEMENTATION_NONCONFORMANCE_CLARIFICATION_AND_LIFECYCLE_REOPENING',
 'g2d_v039_guardian_ruling': 'APPROVE_WITH_MANDATORY_OVERLAY',
 'g2d_v039_accepted_v038_basis_sha256': '09db4ff2224e59c878b967ba634084d72cd01b36f86edfa5fca2e9750e976ea6',
 'g2d_v039_repository_basis_head': '4cf427f82a096383ae5873024787c19e56ac0fb5',
 'g2d_v039_contract_commit': '8638a3c7d0c2774de161a5e52a8aa62ac9db2aa3',
 'g2d_v039_release_consumer_maintenance_commit': 'b9d95605b960ce3837446b1bf38b665ce16f03fb',
 'g2d_v039_implementation_authorized': False,
 'g2d_v039_implementation_action_open': False,
 'g2d_v039_implementation_started': True,
 'g2d_v039_corrected_implementation_exists': True,
 'g2d_v039_corrected_implementation_committed': True,
 'g2d_v039_corrected_implementation_commit': '7a915111e974bc62ff2a7bfe70e8d5a911da03fd',
 'g2d_v039_corrected_implementation_parent_commit': 'b9d95605b960ce3837446b1bf38b665ce16f03fb',
 'g2d_v039_corrected_implementation_patch_sha256': '442b68cdff95fc06a1176fcb4c3d64323110e197b771d5e932db5215b3d8bc13',
 'g2d_v039_corrected_owner_evidence_bundle_sha256': 'fac5596484fb5207632ec6083eeaf2d3cb7d2fa4cdb8f726762d1d635e9e34a0',
 'g2d_v039_runtime_implementation_status': 'IMPLEMENTED_COMMITTED_FULL_ACCEPTANCE_PASS',
 'g2d_v039_full_owner_acceptance_passed': True,
 'g2d_v039_contract_hop_completed': True,
 'g2d_v039_implementation_repository_patch_created': True,
 'g2d_v039_isolated_worktree_strategy_approved': True,
 'g2d_v039_e4_two_path_only_implementation_sufficient': False,
 'g2d_v039_e4_public_end_to_end_carrier_overlay_required': True,
 'g2d_v039_revised_guardian_decision_required': False,
 'g2d_v039_status': 'CLOSED_PASS_ON_V039_BYTES',
 'g2d_v0310_profile_d_implementation_nonconformance': True,
 'g2d_v0310_g2d_runtime_semantics_changed': False,
 'g2d_v0310_g2e4_acceptance_overlay_semantics_changed': True,
 'g2d_v0310_role': 'EXPLICIT_PROFILE_D_T12_IMPLEMENTATION_NONCONFORMANCE_AND_E4_BACKPRESSURE_SCOPE_CORRECTION',
 'g2d_v0310_positive_backpressure_law_changed': False,
 'g2d_v0310_public_revise_semantics_changed': False,
 'g2d_v0310_guardian_ruling': 'APPROVE_PROFILE_D_CORRECTION_AND_E4_BACKPRESSURE_SCOPE_RECONCILIATION',
 'g2d_v0310_accepted_v039_basis_sha256': '1bbe028a4c757330b4ba94aec461e5bfbb1d1ef7496a68593dc20106c4867445',
 'g2d_v0310_repository_basis_head': '36c43db9045d56666e961b54b4f9b272079f41a8',
 'g2d_v0310_contract_hop_completed': True,
 'g2d_v0310_implementation_authorized': False,
 'g2d_v0310_implementation_started': True,
 'g2d_v0310_corrected_implementation_exists': True,
 'g2d_v0310_corrected_implementation_committed': True,
 'g2d_v0310_independent_reaudit_required': True,
 'g2d_v0310_independent_reaudit_passed': True,
 'g2d_v0310_additive_reclosure_required': True,
 'g2d_v0310_additive_reclosure_completed': True,
 'g2d_v0310_e4_public_backpressure_calls_required': 2,
 'g2d_v0310_e4_public_backpressure_geometry_required': [[0, 3], [2, 1]],
 'g2d_v0310_e4_public_backpressure_latest_queue_counts_required': [7, 15],
 'g2d_v0310_e4_public_backpressure_results_required': [None, None],
 'g2d_v0310_e4_nonempty_backpressure_state_required': False,
 'g2d_v0310_e4_explicit_public_revise_calls_required': 4,
 'g2d_v0310_internal_public_revise_calls_per_reconstruction_required': 0,
 'g2d_v037_status': 'HISTORICAL_CLOSED_PASS_WITH_IMPLEMENTATION_NONCONFORMANCE',
 'g2d_v037_accepted_normative_donor_sha256': '8801e413f93765cc7059ce5e03e82e881b20cfd193f12551a60a0b90920bb63d',
 'g2d_v037_accepted_addendum_sha256': '29983cd17cbefe306de32cf045827fc927280bae5fdb0d7c9db50203a0ea6511',
 'g2d_v037_corrected_implementation_commit': '27c6dfd10740103cddc13bac3ce35f917b5f30c5',
 'g2d_v037_corrected_implementation_patch_sha256': 'be594af310b2d13baf0e45283944bd68f56461126b6aa3fbbcaff541a58a0279',
 'g2d_v037_owner_evidence_bundle_sha256': 'e49752fcd1c19dfe8ddf55a254b2d97f8c27688bc0c2371b6ad4ffe2ec5c9cdd',
 'g2d_v037_independent_reaudit_commit': '2eccb604fee89d7e79025337d3858d6dbfea5fbc',
 'g2d_v037_independent_reaudit_path': 'docs/audit_reports/auditor_fractal_runtime_g2_d_v037_observed_work_correction_v01.log',
 'g2d_v037_independent_reaudit_sha256': 'c31d1712593184317b03425c57c5fcebf19532cbfc3086981223bf32afd0e8a3',
 'g2d_v037_checkpoint_path': 'docs/fractal_runtime_v0_2_g2_d_observed_work_correction_checkpoint_v01.md',
 'g2d_v037_checkpoint_sha256': '606d9f1c516ddbe86ec63fe93fc2126ae69bfbf3f8169879a6c1933162296677',
 'g2d_v037_closure_commit': '48ab284ee7c1ba33400f0d0c7fe5656b4249b839',
 'g2d_v037_evidence_classification': 'IMMUTABLE_HISTORICAL_EVIDENCE_FOR_V037_BYTES_ONLY',
 'g2d_historical_precorrection_status': 'CLOSED_PASS_ON_PRECORRECTION_BYTES',
 'g2d_historical_precorrection_implementation_basis_commit': '5e5d565eb6c2088db995cf9e5b3ccb0743f1c9cd',
 'g2d_historical_precorrection_audit_commit': 'c0dc618a0b693fe55435f17a025789267bcb79ff',
 'g2d_historical_precorrection_audit_path': 'docs/audit_reports/auditor_fractal_runtime_g2_d_v02.log',
 'g2d_historical_precorrection_audit_sha256': 'ccc367ac92ad02e005c7968d152bf7810a772db94dd671e26e5d27f30d2d72aa',
 'g2d_historical_precorrection_checkpoint_path': 'docs/fractal_runtime_v0_2_g2_d_checkpoint_v01.md',
 'g2d_historical_precorrection_checkpoint_sha256': 'f5bb19741ee992605ed772a282f4374bc3949508052edb09c8b3fdbbf210c1de',
 'g2d_historical_precorrection_evidence_only': True,
 'g2d_v0310_status': 'CLOSED_PASS'}

G2E_CURRENT_BOUNDARY_FIELDS = {'g2e3_status': 'IMPLEMENTED_COMMITTED_ACCEPTANCE_PASS_ON_CORRECTED_G2D',
 'g2e3_historical_v038_status': 'IMPLEMENTED_COMMITTED_ACCEPTANCE_PASS_ON_V038_G2D',
 'g2e3_post_corrected_g2d_landing_status': 'IMPLEMENTED_COMMITTED_ACCEPTANCE_PASS_ON_CORRECTED_G2D',
 'g2e3_post_v039_implementation_status': 'REVALIDATION_PENDING_ON_CORRECTED_G2D',
 'g2e3_post_v0310_implementation_status': 'IMPLEMENTED_COMMITTED_ACCEPTANCE_PASS_ON_CORRECTED_G2D',
 'g2e3_fresh_v06_required_after_v0310_reclosure': False,
 'g2e3_post_reclosure_v06_passed': True,
 'g2e3_post_reclosure_v06_archive_sha256': '8301e6886ab1400fabffe1c850205c73b02919dc844dffe119a42550eb92b4ba',
 'g2e3_baseline_source_observation_sha256': 'fb2687f08911e5420d03ec40fef02fde3794edc1e03d637df9f8d26c062b3f3c',
 'g2e3_baseline_member_observation_sha256': 'fbd40637c2082ec385204a53a2173695a2247b6cd8e908f34349d75d6a1e3467',
 'g2e3_baseline_member_identities_sha256': '8924a3971624823805d2ed7b99adff5a68ca96d07aa67bb516d744e7f3877b39',
 'g2e_accepted_preflight_sha256': '83f36c9b2d47619a8c8ab997eba6b8ef16f2a3ab07cb3aecfc77ea82469f0d8b',
 'g2e_accepted_addendum_revision': 'v0.1.3',
 'g2e_accepted_addendum_sha256': '2b982ecaed9dc5cea2373676d816840ca683c8190b69516c14688cbba9e452f8',
 'g2e_v013_normative_donor_sha256': '17b9384db812d5078301a9b3d4335dd3351481e117929b6b04c1ff6a137f4a56',
 'g2e4_public_seam_register_sha256': 'a10be3df58ed7fbf32fcb853c7de93f76eec5b3070120b0f895b27340cf2aed2',
 'g2e4_two_root_pair_register_sha256': 'a8a8fd530d95ec4bce8a0faf14044c8b98f53973651cf65784a717d69e02ce33',
 'g2e4_contract_accepted': True,
 'g2e4_contract_status': 'HISTORICAL_CONTRACT_HOP_COMPLETED',
 'g2e4_status': 'IMPLEMENTED_COMMITTED_ACCEPTANCE_PASS',
 'g2e4_implementation_authorized': True,
 'g2e4_implementation_started': True,
 'g2e4_strict_subtree_implementation_committed': True,
 'g2e4_strict_subtree_status': 'IMPLEMENTED_COMMITTED_PASS',
 'g2e4_anti_gaming_acceptance': 'PASS',
 'g2e4_anti_gaming_correction_authorized': False,
 'g2e5_status': 'NOT_STARTED_NOT_AUTHORIZED',
 'g2e6_status': 'NOT_STARTED_NOT_AUTHORIZED',
 'g2f_status': 'NOT_STARTED_NOT_AUTHORIZED',
 'g2e3_v0310_fresh_v06_passed': True,
 'g2e3_v0310_fresh_v06_archive_sha256': '8301e6886ab1400fabffe1c850205c73b02919dc844dffe119a42550eb92b4ba',
 'g2e3_v0310_fresh_source_observation_sha256': 'fb2687f08911e5420d03ec40fef02fde3794edc1e03d637df9f8d26c062b3f3c',
 'g2e3_v0310_fresh_member_observation_sha256': 'fbd40637c2082ec385204a53a2173695a2247b6cd8e908f34349d75d6a1e3467',
 'g2e3_v0310_fresh_member_identities_sha256': '8924a3971624823805d2ed7b99adff5a68ca96d07aa67bb516d744e7f3877b39',
 'g2e4_acceptance_correction_commit': '21176be090cab9aa9b8ea9cce2ae052bed8039da',
 'g2e4_acceptance_correction_patch_sha256': 'ea1b030bb40e52aeb30ea5d49599ba2e3a59f50398ef8d74234ab77e30842157',
 'g2e4_acceptance_owner_evidence_sha256': '92390ad076307a73473f1bb22b65748bbc2e25bcdccd6fe0250312d26b124b31'}

CURRENT_BOUNDARY_FIELDS = {
    **G2D_CURRENT_BOUNDARY_FIELDS,
    **G2E_CURRENT_BOUNDARY_FIELDS,
}

G2D_RECLOSURE_G2E_FIELDS = {
    "g2e3_status": "REVALIDATION_PENDING_ON_CORRECTED_G2D",
    "g2e3_post_corrected_g2d_landing_status": (
        "REVALIDATION_PENDING_ON_CORRECTED_G2D"
    ),
    "g2e4_status": "NOT_STARTED_NOT_AUTHORIZED",
}
G2E_CONTRACT_TRANSITION_FIELDS = set(G2E_CURRENT_BOUNDARY_FIELDS) - {
    "g2e3_status",
    "g2e3_post_corrected_g2d_landing_status",
}
G2D_V038_TRANSITION_FIELDS = {
    key
    for key in set(G2D_CURRENT_BOUNDARY_FIELDS)
    | set(G2D_V037_RECLOSURE_BOUNDARY_FIELDS)
    if G2D_CURRENT_BOUNDARY_FIELDS.get(key, "MISSING_CURRENT")
    != G2D_V037_RECLOSURE_BOUNDARY_FIELDS.get(key, "MISSING_RECLOSURE")
}
CURRENT_TRANSITION_FIELDS = (
    G2D_V038_TRANSITION_FIELDS | G2E_CONTRACT_TRANSITION_FIELDS
)

G2D_FROZEN_IMPLEMENTATION_SHA256 = {
    "schemas/fractal_runtime_v02.schema.json": (
        "a70ea31721a08c9edaaeb7c7aa6a91abb2e6c92b408fd72f22f1165b4baef4e8"
    ),
    "demo/run_fractal_runtime_g2_d_v02.py": (
        "ead2127501c15f6c8ab01eab0c95c65a838008326004bb9ce290557a2fb890ff"
    ),
    "hedgehog/kernel/transition_registry_v01.py": (
        "31492ba73aabc7139bc2bae17dbbd7bbf5b6c8496c8b64764faebeff3c2fc107"
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
    "schemas/continuous_delta_runtime_v01.schema.json": (
        "6d2d2c8756ebf261724742ad14294094ee9ce04a28c0498b264164ec585d11f2"
    ),
}

G2D_HISTORICAL_G2E_DEPENDENCY_SHA256 = {
    G2E_ACCEPTED_ADDENDUM_PATH: G2E_V012_ADDENDUM_SHA256,
    "tests/test_continuous_delta_runtime_g2_e_v01.py": (
        "812cbf76e75c7389cb3d687c453acdacee7e9de531350cdd1c9e28ffd73b113d"
    ),
}
G2E_CONTRACT_UPDATED_SHA256 = {
    G2E_ACCEPTED_ADDENDUM_PATH: G2E_ACCEPTED_ADDENDUM_SHA256,
    "hedgehog/kernel/continuous_delta_runtime_v01.py": (
        "6e6679a592e45bc268d1bb8476c171111571f012f06fe5b65a030092b68ef6e0"
    ),
    "tests/test_continuous_delta_runtime_g2_e_v01.py": (
        "b4c355b6de16d7417c4b48710fbcd4f4ef70c2f7a1cfa68a1de1e8a716fd9e77"
    ),
    "hedgehog/kernel/__init__.py": (
        "99b2847d4dac09827b0a56cd820302052139654314ff02789363480cc98df4e0"
    ),
}

G2E4_V0310_RUNTIME_PATH = "hedgehog/kernel/continuous_delta_runtime_v01.py"
G2E4_V0310_TEST_PATH = "tests/test_continuous_delta_runtime_g2_e_v01.py"
G2E4_V0310_RUNTIME_SHA256 = '6eec2a20d0035a12beb47df6989a106bc0d87cefb00cc7434733fd0b79d8bd0e'
G2E4_V0310_TEST_SHA256 = '438fafc7647f0c2b453f763f9425e2565792eaa7321b9726969e6bbf39c386d3'


def _g2d_v0310_bind_exact_e4_candidate_hashes_v01() -> str:
    paths = (G2E4_V0310_RUNTIME_PATH, G2E4_V0310_TEST_PATH)
    historical = tuple(G2E_CONTRACT_UPDATED_SHA256[path] for path in paths)
    successor = (G2E4_V0310_RUNTIME_SHA256, G2E4_V0310_TEST_SHA256)
    observed = tuple(
        hashlib.sha256((REPOSITORY_ROOT / path).read_bytes()).hexdigest()
        for path in paths
    )
    if observed == historical:
        return "HISTORICAL_E4_CONTRACT_BYTES"
    assert observed == successor
    G2E_CONTRACT_UPDATED_SHA256.update(dict(zip(paths, successor)))
    return "EXACT_E4_CORRECTION_BYTES"


G2E4_V0310_ACTIVE_BYTES_BINDING = (
    _g2d_v0310_bind_exact_e4_candidate_hashes_v01()
)


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


def _git_commits_with_subject_v0310(subject: str) -> tuple[tuple[str, str], ...]:
    rows = subprocess.run(
        ("git", "log", "--all", "--format=%H%x1f%P%x1f%s"),
        cwd=REPOSITORY_ROOT,
        check=True,
        capture_output=True,
        text=True,
    ).stdout.splitlines()
    matches: list[tuple[str, str]] = []
    for row in rows:
        commit, parents, observed_subject = row.split("\x1f", 2)
        if observed_subject == subject:
            matches.append((commit, parents))
    return tuple(matches)


def _assert_exact_commit_v0310(
    *,
    commit: str,
    parent: str,
    subject: str,
    paths: tuple[str, ...],
) -> None:
    row = subprocess.run(
        ("git", "show", "-s", "--format=%H%x1f%P%x1f%s", commit),
        cwd=REPOSITORY_ROOT,
        check=True,
        capture_output=True,
        text=True,
    ).stdout.strip()
    observed_commit, observed_parent, observed_subject = row.split("\x1f", 2)
    assert observed_commit == commit
    assert observed_parent == parent
    assert observed_subject == subject
    changed_paths = subprocess.run(
        ("git", "diff", "--name-only", parent, commit),
        cwd=REPOSITORY_ROOT,
        check=True,
        capture_output=True,
        text=True,
    ).stdout.splitlines()
    assert tuple(changed_paths) == tuple(sorted(paths))


def _g2d_v0310_implementation_patch_v01(
    *,
    parent: str | None = None,
    commit: str | None = None,
) -> bytes:
    command = ["git", "diff", "--no-ext-diff", "--full-index", "--binary"]
    if parent is not None:
        assert commit is not None
        command.extend((parent, commit))
    command.extend(("--", *G2D_V0310_IMPLEMENTATION_PATHS))
    return subprocess.run(
        tuple(command),
        cwd=REPOSITORY_ROOT,
        check=True,
        capture_output=True,
    ).stdout


def _assert_g2d_v0310_implementation_patch_v01(patch: bytes) -> None:
    assert _sha256_bytes(patch) == G2D_V0310_IMPLEMENTATION_PATCH_SHA256
    assert len(patch) == G2D_V0310_IMPLEMENTATION_PATCH_BYTES
    assert patch.count(b"\n") == G2D_V0310_IMPLEMENTATION_PATCH_LF


def _g2d_v0310_legacy_lifecycle_state_v01() -> tuple[str, str, str | None, str | None]:
    head = subprocess.run(
        ("git", "rev-parse", "HEAD"),
        cwd=REPOSITORY_ROOT,
        check=True,
        capture_output=True,
        text=True,
    ).stdout.strip()
    status = subprocess.run(
        ("git", "status", "--short", "--untracked-files=all"),
        cwd=REPOSITORY_ROOT,
        check=True,
        capture_output=True,
        text=True,
    ).stdout.splitlines()
    staged = subprocess.run(
        ("git", "diff", "--cached", "--name-only"),
        cwd=REPOSITORY_ROOT,
        check=True,
        capture_output=True,
        text=True,
    ).stdout.splitlines()
    assert staged == []

    contract_rows = _git_commits_with_subject_v0310(G2D_V0310_CONTRACT_SUBJECT)
    maintenance_rows = _git_commits_with_subject_v0310(
        G2D_V0310_RELEASE_CONSUMER_MAINTENANCE_SUBJECT
    )
    implementation_rows = _git_commits_with_subject_v0310(
        G2D_V0310_IMPLEMENTATION_SUBJECT
    )
    dirty_contract = {" M " + path for path in G2D_V0310_CONTRACT_PATHS}

    if not G2D_V0310_RELEASE_CONSUMER_MAINTENANCE_ACTIVATED:
        assert G2D_V0310_CONTRACT_COMMIT == "NOT_SELF_RECORDED"
        assert maintenance_rows == ()
        assert implementation_rows == ()
        if head == G2D_V0310_BASIS:
            assert contract_rows == ()
            assert set(status) == dirty_contract
            return ("PRE_CONTRACT_DIRTY", head, None, None)
        assert len(contract_rows) == 1
        contract_commit, contract_parents = contract_rows[0]
        assert contract_parents == G2D_V0310_BASIS
        _assert_exact_commit_v0310(
            commit=contract_commit,
            parent=G2D_V0310_BASIS,
            subject=G2D_V0310_CONTRACT_SUBJECT,
            paths=G2D_V0310_CONTRACT_PATHS,
        )
        assert head == contract_commit
        assert status == []
        return ("POST_CONTRACT_PRE_MAINTENANCE_CLEAN", head, contract_commit, None)

    assert re.fullmatch(r"[0-9a-f]{40}", G2D_V0310_CONTRACT_COMMIT)
    assert len(contract_rows) == 1
    contract_commit, contract_parents = contract_rows[0]
    assert contract_commit == G2D_V0310_CONTRACT_COMMIT
    assert contract_parents == G2D_V0310_BASIS
    _assert_exact_commit_v0310(
        commit=contract_commit,
        parent=G2D_V0310_BASIS,
        subject=G2D_V0310_CONTRACT_SUBJECT,
        paths=G2D_V0310_CONTRACT_PATHS,
    )

    release_test_path = G2D_V0310_RELEASE_CONSUMER_MAINTENANCE_PATHS[0]
    contract_release_test = _git_show(contract_commit, release_test_path)
    maintenance_replacements = (
        (
            b"G2D_V0310_CONTRACT_COMMIT = " + b'"NOT_SELF_RECORDED"',
            f'G2D_V0310_CONTRACT_COMMIT = "{contract_commit}"'.encode("ascii"),
        ),
        (
            b"G2D_V0310_RELEASE_CONSUMER_MAINTENANCE_ACTIVATED = " + b"False",
            b"G2D_V0310_RELEASE_CONSUMER_MAINTENANCE_ACTIVATED = True",
        ),
        (
            b'"RUNTIME_SHA256_NOT_FROZEN_'
            + b'BY_RELEASE_CONSUMER_MAINTENANCE"',
            f'"{G2D_V0310_IMPLEMENTATION_RUNTIME_SHA256}"'.encode("ascii"),
        ),
        (
            b"G2D_V0310_IMPLEMENTATION_RUNTIME_BYTES = " + b"0",
            (
                "G2D_V0310_IMPLEMENTATION_RUNTIME_BYTES = "
                f"{G2D_V0310_IMPLEMENTATION_RUNTIME_BYTES}"
            ).encode("ascii"),
        ),
        (
            b"G2D_V0310_IMPLEMENTATION_RUNTIME_LF = " + b"0",
            (
                "G2D_V0310_IMPLEMENTATION_RUNTIME_LF = "
                f"{G2D_V0310_IMPLEMENTATION_RUNTIME_LF}"
            ).encode("ascii"),
        ),
        (
            b'"TEST_SHA256_NOT_FROZEN_'
            + b'BY_RELEASE_CONSUMER_MAINTENANCE"',
            f'"{G2D_V0310_IMPLEMENTATION_TEST_SHA256}"'.encode("ascii"),
        ),
        (
            b"G2D_V0310_IMPLEMENTATION_TEST_BYTES = " + b"0",
            (
                "G2D_V0310_IMPLEMENTATION_TEST_BYTES = "
                f"{G2D_V0310_IMPLEMENTATION_TEST_BYTES}"
            ).encode("ascii"),
        ),
        (
            b"G2D_V0310_IMPLEMENTATION_TEST_LF = " + b"0",
            (
                "G2D_V0310_IMPLEMENTATION_TEST_LF = "
                f"{G2D_V0310_IMPLEMENTATION_TEST_LF}"
            ).encode("ascii"),
        ),
        (
            b'"PATCH_SHA256_NOT_FROZEN_'
            + b'BY_RELEASE_CONSUMER_MAINTENANCE"',
            f'"{G2D_V0310_IMPLEMENTATION_PATCH_SHA256}"'.encode("ascii"),
        ),
        (
            b"G2D_V0310_IMPLEMENTATION_PATCH_BYTES = " + b"0",
            (
                "G2D_V0310_IMPLEMENTATION_PATCH_BYTES = "
                f"{G2D_V0310_IMPLEMENTATION_PATCH_BYTES}"
            ).encode("ascii"),
        ),
        (
            b"G2D_V0310_IMPLEMENTATION_PATCH_LF = " + b"0",
            (
                "G2D_V0310_IMPLEMENTATION_PATCH_LF = "
                f"{G2D_V0310_IMPLEMENTATION_PATCH_LF}"
            ).encode("ascii"),
        ),
    )
    expected_maintenance_test = contract_release_test
    for before, after in maintenance_replacements:
        assert before != after
        assert expected_maintenance_test.count(before) == 1
        expected_maintenance_test = expected_maintenance_test.replace(
            before,
            after,
            1,
        )
    assert expected_maintenance_test != contract_release_test

    if not maintenance_rows:
        assert implementation_rows == ()
        assert head == contract_commit
        assert status == [" M " + release_test_path]
        assert (REPOSITORY_ROOT / release_test_path).read_bytes() == (
            expected_maintenance_test
        )
        return ("MAINTENANCE_CANDIDATE_DIRTY", head, contract_commit, None)

    assert len(maintenance_rows) == 1
    maintenance_commit, maintenance_parents = maintenance_rows[0]
    assert maintenance_parents == contract_commit
    _assert_exact_commit_v0310(
        commit=maintenance_commit,
        parent=contract_commit,
        subject=G2D_V0310_RELEASE_CONSUMER_MAINTENANCE_SUBJECT,
        paths=G2D_V0310_RELEASE_CONSUMER_MAINTENANCE_PATHS,
    )
    assert _git_show(maintenance_commit, release_test_path) == (
        expected_maintenance_test
    )

    runtime_path, test_path = G2D_V0310_IMPLEMENTATION_PATHS
    current_runtime = (REPOSITORY_ROOT / runtime_path).read_bytes()
    current_test = (REPOSITORY_ROOT / test_path).read_bytes()
    implementation_dirty = {" M " + path for path in G2D_V0310_IMPLEMENTATION_PATHS}
    if not implementation_rows:
        assert head == maintenance_commit
        if status == []:
            return (
                "POST_MAINTENANCE_CLEAN",
                head,
                contract_commit,
                maintenance_commit,
            )
        assert set(status) == implementation_dirty
        assert _sha256_bytes(current_runtime) == (
            G2D_V0310_IMPLEMENTATION_RUNTIME_SHA256
        )
        assert len(current_runtime) == G2D_V0310_IMPLEMENTATION_RUNTIME_BYTES
        assert current_runtime.count(b"\n") == G2D_V0310_IMPLEMENTATION_RUNTIME_LF
        assert _sha256_bytes(current_test) == G2D_V0310_IMPLEMENTATION_TEST_SHA256
        assert len(current_test) == G2D_V0310_IMPLEMENTATION_TEST_BYTES
        assert current_test.count(b"\n") == G2D_V0310_IMPLEMENTATION_TEST_LF
        _assert_g2d_v0310_implementation_patch_v01(
            _g2d_v0310_implementation_patch_v01()
        )
        return (
            "IMPLEMENTATION_CANDIDATE_DIRTY",
            head,
            contract_commit,
            maintenance_commit,
        )

    assert len(implementation_rows) == 1
    implementation_commit, implementation_parents = implementation_rows[0]
    assert implementation_parents == maintenance_commit
    _assert_exact_commit_v0310(
        commit=implementation_commit,
        parent=maintenance_commit,
        subject=G2D_V0310_IMPLEMENTATION_SUBJECT,
        paths=G2D_V0310_IMPLEMENTATION_PATHS,
    )
    assert head == implementation_commit
    assert status == []
    assert _sha256_bytes(current_runtime) == G2D_V0310_IMPLEMENTATION_RUNTIME_SHA256
    assert len(current_runtime) == G2D_V0310_IMPLEMENTATION_RUNTIME_BYTES
    assert current_runtime.count(b"\n") == G2D_V0310_IMPLEMENTATION_RUNTIME_LF
    assert _sha256_bytes(current_test) == G2D_V0310_IMPLEMENTATION_TEST_SHA256
    assert len(current_test) == G2D_V0310_IMPLEMENTATION_TEST_BYTES
    assert current_test.count(b"\n") == G2D_V0310_IMPLEMENTATION_TEST_LF
    _assert_g2d_v0310_implementation_patch_v01(
        _g2d_v0310_implementation_patch_v01(
            parent=maintenance_commit,
            commit=implementation_commit,
        )
    )
    return (
        "POST_IMPLEMENTATION_CLEAN",
        head,
        contract_commit,
        maintenance_commit,
    )


def _g2d_v0310_protected_paths_v01() -> frozenset[str]:
    return frozenset(
        (
            G2D_ACCEPTED_PREFLIGHT_PATH,
            G2D_AUDIT_PATH,
            G2D_HISTORICAL_CHECKPOINT_PATH,
            G2D_INDEPENDENT_REAUDIT_PATH,
            G2D_CHECKPOINT_PATH,
            G2D_V038_INDEPENDENT_REAUDIT_PATH,
            G2D_V038_CHECKPOINT_PATH,
            G2D_V039_INDEPENDENT_REAUDIT_PATH,
            G2D_V039_CHECKPOINT_PATH,
            G2D_ACCEPTED_ADDENDUM_PATH,
            G2D_V0310_INDEPENDENT_REAUDIT_PATH,
            G2D_V0310_CHECKPOINT_PATH,
            *G2D_V0310_IMPLEMENTATION_PATHS,
            *G2D_V0310_E4_CODE_PATHS,
            *G2D_FROZEN_IMPLEMENTATION_SHA256,
            *G2E_CONTRACT_UPDATED_SHA256,
            *G2D_FACADE_MAINTENANCE_SHA256,
        )
    )


def _porcelain_paths_v01(status: tuple[str, ...]) -> frozenset[str]:
    paths: set[str] = set()
    for row in status:
        assert len(row) >= 4
        assert row[2] == " "
        rendered_path = row[3:]
        assert rendered_path
        if row[0] in {"R", "C"} or row[1] in {"R", "C"}:
            old_path, separator, new_path = rendered_path.partition(" -> ")
            assert separator == " -> "
            assert old_path and new_path
            paths.update((old_path, new_path))
        else:
            paths.add(rendered_path)
    return frozenset(paths)


def _g2d_v0310_terminal_phase_v01(
    *,
    head: str,
    final_sync_commit: str,
    final_sync_is_ancestor: bool,
    status: tuple[str, ...],
) -> str:
    assert final_sync_is_ancestor
    protected_dirty = (
        _porcelain_paths_v01(status) & _g2d_v0310_protected_paths_v01()
    )
    assert protected_dirty == frozenset()
    if head == final_sync_commit and status == ():
        return "POST_FINAL_E4_SYNC_CLEAN"
    return "POST_FINAL_E4_SYNC_SUCCESSOR"


def _assert_g2d_v0310_terminal_rejected_v01(
    *,
    head: str,
    final_sync_commit: str,
    final_sync_is_ancestor: bool,
    status: tuple[str, ...],
) -> None:
    try:
        _g2d_v0310_terminal_phase_v01(
            head=head,
            final_sync_commit=final_sync_commit,
            final_sync_is_ancestor=final_sync_is_ancestor,
            status=status,
        )
    except AssertionError:
        return
    raise AssertionError(
        "terminal lifecycle case was accepted: "
        f"{head=}, {final_sync_commit=}, {final_sync_is_ancestor=}, {status=}"
    )


def test_g2d_v0310_terminal_accepts_exact_and_unrelated_successor_dirt() -> None:
    final_sync = "f" * 40
    descendant = "d" * 40
    unrelated_status = (
        " M AGENTS.md",
        " M hedgehog/structured_rationale.py",
        "M  specs/document_authority_index_v01.json",
        "?? tests/test_active_architecture_authority_v01.py",
    )

    assert _g2d_v0310_terminal_phase_v01(
        head=final_sync,
        final_sync_commit=final_sync,
        final_sync_is_ancestor=True,
        status=(),
    ) == "POST_FINAL_E4_SYNC_CLEAN"
    assert _g2d_v0310_terminal_phase_v01(
        head=final_sync,
        final_sync_commit=final_sync,
        final_sync_is_ancestor=True,
        status=unrelated_status,
    ) == "POST_FINAL_E4_SYNC_SUCCESSOR"
    assert _g2d_v0310_terminal_phase_v01(
        head=descendant,
        final_sync_commit=final_sync,
        final_sync_is_ancestor=True,
        status=unrelated_status,
    ) == "POST_FINAL_E4_SYNC_SUCCESSOR"


def test_g2d_v0310_terminal_rejects_non_descendant() -> None:
    final_sync = "f" * 40
    descendant = "d" * 40
    _assert_g2d_v0310_terminal_rejected_v01(
        head=descendant,
        final_sync_commit=final_sync,
        final_sync_is_ancestor=False,
        status=(),
    )
def test_g2d_v0310_terminal_rejects_exact_protected_dirty_intersection() -> None:
    final_sync = "f" * 40
    descendant = "d" * 40
    assert _porcelain_paths_v01(("R  old/path -> new/path",)) == frozenset(
        {"old/path", "new/path"}
    )

    rejected_cases = (
        {
            "head": descendant,
            "final_sync_commit": final_sync,
            "final_sync_is_ancestor": True,
            "status": (" M " + G2D_V0310_IMPLEMENTATION_PATHS[0],),
        },
        {
            "head": descendant,
            "final_sync_commit": final_sync,
            "final_sync_is_ancestor": True,
            "status": ("M  " + G2D_V0310_IMPLEMENTATION_PATHS[1],),
        },
        {
            "head": descendant,
            "final_sync_commit": final_sync,
            "final_sync_is_ancestor": True,
            "status": ("?? " + G2D_V0310_E4_CODE_PATHS[1],),
        },
        {
            "head": descendant,
            "final_sync_commit": final_sync,
            "final_sync_is_ancestor": True,
            "status": (
                " M hedgehog/structured_rationale.py",
                " M " + G2D_ACCEPTED_ADDENDUM_PATH,
            ),
        },
        {
            "head": descendant,
            "final_sync_commit": final_sync,
            "final_sync_is_ancestor": True,
            "status": (
                "R  "
                + G2D_V0310_IMPLEMENTATION_PATHS[0]
                + " -> moved/runtime.py",
            ),
        },
    )
    for rejected in rejected_cases:
        _assert_g2d_v0310_terminal_rejected_v01(**rejected)


def _g2d_v0310_successor_state_v01() -> tuple[str, str, str, str]:
    head = subprocess.run(
        ("git", "rev-parse", "HEAD"), cwd=REPOSITORY_ROOT, check=True,
        capture_output=True, text=True,
    ).stdout.strip()
    status = subprocess.run(
        ("git", "status", "--short", "--untracked-files=all"),
        cwd=REPOSITORY_ROOT, check=True, capture_output=True, text=True,
    ).stdout.splitlines()
    status = [row for row in status if "__pycache__/" not in row and ".pytest_cache/" not in row]
    staged = subprocess.run(
        ("git", "diff", "--cached", "--name-only"), cwd=REPOSITORY_ROOT,
        check=True, capture_output=True, text=True,
    ).stdout.splitlines()

    def unique(subject: str) -> tuple[str, str] | None:
        rows = _git_commits_with_subject_v0310(subject)
        assert len(rows) <= 1
        return rows[0] if rows else None

    contract = unique(G2D_V0310_CONTRACT_SUBJECT)
    maintenance = unique(G2D_V0310_RELEASE_CONSUMER_MAINTENANCE_SUBJECT)
    implementation = unique(G2D_V0310_IMPLEMENTATION_SUBJECT)
    sync = unique(G2D_V0310_LIFECYCLE_SYNC_SUBJECT)
    audit = unique(G2D_V0310_INDEPENDENT_REAUDIT_SUBJECT)
    closure = unique(G2D_V0310_CLOSURE_SUBJECT)
    e4 = unique(G2D_V0310_E4_CODE_SUBJECT)
    final_sync = unique(G2D_V0310_FINAL_SYNC_SUBJECT)
    if final_sync is None:
        assert staged == []

    assert contract == (G2D_V0310_CONTRACT_COMMIT, G2D_V0310_BASIS)
    assert maintenance is not None and maintenance[1] == contract[0]
    assert implementation is not None and implementation[1] == maintenance[0]
    _assert_exact_commit_v0310(
        commit=implementation[0], parent=maintenance[0],
        subject=G2D_V0310_IMPLEMENTATION_SUBJECT,
        paths=G2D_V0310_IMPLEMENTATION_PATHS,
    )
    previous = implementation[0]
    if sync is not None:
        assert sync[1] == previous
        _assert_exact_commit_v0310(
            commit=sync[0], parent=previous,
            subject=G2D_V0310_LIFECYCLE_SYNC_SUBJECT,
            paths=G2D_V0310_LIFECYCLE_SYNC_PATHS,
        )
        if G2D_V0310_LIFECYCLE_SYNC_COMMIT != "NOT_CREATED":
            assert sync[0] == G2D_V0310_LIFECYCLE_SYNC_COMMIT
        previous = sync[0]
    if audit is not None:
        assert sync is not None and audit[1] == previous
        _assert_exact_commit_v0310(
            commit=audit[0], parent=previous,
            subject=G2D_V0310_INDEPENDENT_REAUDIT_SUBJECT,
            paths=(G2D_V0310_INDEPENDENT_REAUDIT_PATH,),
        )
        if G2D_V0310_INDEPENDENT_REAUDIT_COMMIT != "NOT_CREATED":
            assert audit[0] == G2D_V0310_INDEPENDENT_REAUDIT_COMMIT
        previous = audit[0]
    if closure is not None:
        assert audit is not None and closure[1] == previous
        _assert_exact_commit_v0310(
            commit=closure[0], parent=previous,
            subject=G2D_V0310_CLOSURE_SUBJECT,
            paths=G2D_V0310_RECLOSURE_PATHS,
        )
        previous = closure[0]
    if e4 is not None:
        assert closure is not None and e4[1] == previous
        _assert_exact_commit_v0310(
            commit=e4[0], parent=previous,
            subject=G2D_V0310_E4_CODE_SUBJECT,
            paths=G2D_V0310_E4_CODE_PATHS,
        )
        if G2D_V0310_E4_CODE_COMMIT != "NOT_CREATED":
            assert e4[0] == G2D_V0310_E4_CODE_COMMIT
        previous = e4[0]
    if final_sync is not None:
        assert e4 is not None and final_sync[1] == previous
        _assert_exact_commit_v0310(
            commit=final_sync[0], parent=previous,
            subject=G2D_V0310_FINAL_SYNC_SUBJECT,
            paths=G2D_V0310_FINAL_SYNC_PATHS,
        )
        previous = final_sync[0]

    dirty_sync = sorted(" M " + path for path in G2D_V0310_LIFECYCLE_SYNC_PATHS)
    dirty_reclosure = sorted(
        [" M " + path for path in G2D_V0310_RECLOSURE_PATHS if path != G2D_V0310_CHECKPOINT_PATH]
        + ["?? " + G2D_V0310_CHECKPOINT_PATH]
    )
    if final_sync is not None:
        ancestor = subprocess.run(
            ("git", "merge-base", "--is-ancestor", final_sync[0], head),
            cwd=REPOSITORY_ROOT,
            check=False,
            capture_output=True,
        )
        assert ancestor.returncode in {0, 1}
        phase = _g2d_v0310_terminal_phase_v01(
            head=head,
            final_sync_commit=final_sync[0],
            final_sync_is_ancestor=ancestor.returncode == 0,
            status=tuple(status),
        )
    elif e4 is not None:
        assert head == e4[0] and (status == [] or sorted(status) == dirty_sync)
        phase = "POST_E4_CLEAN" if not status else "FINAL_E4_SYNC_CANDIDATE_DIRTY"
    elif closure is not None:
        dirty_e4 = sorted(" M " + path for path in G2D_V0310_E4_CODE_PATHS)
        assert head == closure[0] and (status == [] or sorted(status) == dirty_e4)
        phase = "POST_RECLOSURE_CLEAN" if not status else "E4_CODE_CANDIDATE_DIRTY"
    elif audit is not None:
        assert head == audit[0] and (status == [] or sorted(status) == dirty_reclosure)
        phase = "POST_AUDIT_CLEAN" if not status else "RECLOSURE_CANDIDATE_DIRTY"
    elif sync is not None:
        audit_dirty = ["?? " + G2D_V0310_INDEPENDENT_REAUDIT_PATH]
        assert head == sync[0] and (status == [] or status == audit_dirty)
        phase = "POST_SYNC_CLEAN" if not status else "AUDIT_CANDIDATE_DIRTY"
    else:
        assert head == implementation[0] and (status == [] or sorted(status) == dirty_sync)
        phase = "POST_IMPLEMENTATION_CLEAN" if not status else "SYNC_CANDIDATE_DIRTY"
    return phase, head, contract[0], maintenance[0]


def _g2d_v0310_lifecycle_state_v01() -> tuple[str, str, str | None, str | None]:
    phase, head, contract, maintenance = _g2d_v0310_successor_state_v01()
    assert phase in {
        "POST_IMPLEMENTATION_CLEAN", "SYNC_CANDIDATE_DIRTY", "POST_SYNC_CLEAN",
        "AUDIT_CANDIDATE_DIRTY", "POST_AUDIT_CLEAN", "RECLOSURE_CANDIDATE_DIRTY",
        "POST_RECLOSURE_CLEAN", "POST_E4_CLEAN", "FINAL_E4_SYNC_CANDIDATE_DIRTY",
        "E4_CODE_CANDIDATE_DIRTY",
        "POST_FINAL_E4_SYNC_CLEAN",
        "POST_FINAL_E4_SYNC_SUCCESSOR",
    }
    # Preserve the historical helper's bounded two-phase public contract for
    # exact legacy tests.  Successor-aware tests consume the exact phase from
    # _g2d_v0310_successor_state_v01 above.
    return "POST_IMPLEMENTATION_CLEAN", head, contract, maintenance


def _current_boundary() -> dict[str, object]:
    overlay = _read_json(OVERLAY_PATH)
    boundary = overlay["current_engineering_boundary"]
    assert isinstance(boundary, dict)
    return boundary


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
    for key, value in G2D_V037_RECLOSURE_BOUNDARY_FIELDS.items():
        assert boundary.pop(key) == value
    for key, value in G2D_RECLOSURE_G2E_FIELDS.items():
        assert boundary.pop(key) == value
    return reverted


def _assert_exactly_once(text: str, required: tuple[str, ...]) -> None:
    for value in required:
        assert text.count(value) == 1, value


def _assert_absent(text: str, forbidden: tuple[str, ...]) -> None:
    for value in forbidden:
        assert value not in text, value


def _assert_closed_boundary(boundary: dict[str, object]) -> None:
    assert set(boundary) == set(IN_PROGRESS_BOUNDARY) | set(
        CURRENT_BOUNDARY_FIELDS
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
    for key, value in CURRENT_BOUNDARY_FIELDS.items():
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
    for key in CURRENT_BOUNDARY_FIELDS:
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


def test_readme_current_engineering_view_and_license_are_bounded() -> None:
    text = README_PATH.read_text(encoding="utf-8")
    normalized = " ".join(text.split())
    for heading in (
        "## What Hedgehog OS is",
        "## Current Root-centered topology",
        "## What the current reference runtime demonstrates",
        "## Current capabilities and checkpoints",
        "## Evidence and historical checkpoint navigation",
        "## Run the current Living Gauntlet and Kernel Conformance",
        "## Claims and non-claims",
        "## Where integrators extend the Kernel",
    ):
        assert text.count(heading) == 1
    for required in (
        "[Current Architecture Lock](specs/current_architecture_lock_v01.md)",
        "BSEP is the canonical semantic membrane",
        "RuntimeExecutionTopology is locally materialized",
        "Root is the sole local final and commit authority",
        "Gate 1 is `CLOSED_PASS`",
        "G2-D is `CLOSED_PASS`",
        "G2-E5, G2-E6, and G2-F are `NOT_STARTED_NOT_AUTHORIZED`",
        "[Document Authority Index](specs/document_authority_index_v01.json)",
        "[Successor Context Manifest](release/successor_context_manifest_v01.json)",
        "[LICENSE](LICENSE)",
        "[COMMERCIAL-LICENSING.md](COMMERCIAL-LICENSING.md)",
    ):
        assert required in normalized, required
    assert "Gate 2 remains `NOT_CLOSED`" in normalized
    assert "does not claim production readiness" in normalized
    assert "physical-world effects, or Gate-2 closure" in normalized
    assert "From an installed editable checkout with `.venv` available" in text
    assert ".venv/bin/python -m demo.run_kernel_conformance_v01" in text
    assert ".venv/bin/python -m demo.run_living_gauntlet_v01" in text
    assert README_BEGIN_MARKER not in text
    assert README_END_MARKER not in text
    with (REPOSITORY_ROOT / "pyproject.toml").open("rb") as handle:
        project = tomllib.load(handle)["project"]
    assert project["license"] == "AGPL-3.0-only"
    assert project["license-files"] == ["LICENSE"]


def test_agents_current_operational_surface_is_exactly_bounded() -> None:
    text = AGENTS_PATH.read_text(encoding="utf-8")
    normalized = " ".join(text.split())
    for heading in (
        "## Source-of-truth order",
        "## Canonical runtime",
        "## Current authority law",
        "## Current Gate status and E5 handoff",
        "## Worktree discipline",
        "## Test and commit discipline",
        "## Bounded context and onboarding",
        "## Current navigation",
    ):
        assert text.count(heading) == 1
    for required in (
        "[Current Architecture Lock](specs/current_architecture_lock_v01.md)",
        "[Document Authority Index](specs/document_authority_index_v01.json)",
        "BSEP is the canonical semantic membrane",
        "RuntimeExecutionTopology is materialized and owned locally by runtime",
        "Root is the sole local final and commit authority",
        "Gate 1 and G2-A, G2-B, G2-C, and G2-D are `CLOSED_PASS`",
        "G2-E5, G2-E6, and G2-F are `NOT_STARTED_NOT_AUTHORIZED`",
        "S2_CLOSED_PENDING_S3",
        "S3_ACTIVE_SCHEMA_AND_LEGACY_ISOLATION",
        "Permanent successor onboarding remains prohibited",
        "The frozen E5 transplant remains prohibited",
    ):
        assert required in normalized, required
    source_order = text.split("## Source-of-truth order", 1)[1].split(
        "## Canonical runtime", 1
    )[0]
    assert source_order.index("1. [Current Architecture Lock]") < (
        source_order.index("2. Accepted current Kernel and Gate runtime contracts")
    )
    assert "subordinate to the" in text.split("## Source-of-truth order", 1)[0]
    for stale_marker in (
        AGENTS_BEGIN_MARKER,
        AGENTS_CURRENT_BEGIN_MARKER,
        AGENTS_G2D_CURRENT_BEGIN_MARKER,
        AGENTS_G2D_V039_CLOSED_BEGIN_MARKER,
        AGENTS_G2D_V039_CONTRACT_BEGIN_MARKER,
        AGENTS_G2D_V038_BEGIN_MARKER,
        AGENTS_G2D_V0310_CURRENT_BEGIN_MARKER,
        AGENTS_END_MARKER,
    ):
        assert stale_marker not in text
    for route_step in (
        "BSEP",
        "Semantic Architect proposal",
        "runtime-owned RuntimeExecutionTopology",
        "bounded actors / executors / child cells",
        "ResultProposal / receipts / boundary snapshots",
        "terminal GT advisory",
        "independent local Root decision(s)",
    ):
        assert route_step in text

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
    boundary = overlay["current_engineering_boundary"]
    assert boundary == _current_boundary()
    assert set(boundary) == set(IN_PROGRESS_BOUNDARY) | set(CURRENT_BOUNDARY_FIELDS)
    for key, value in CURRENT_BOUNDARY_FIELDS.items():
        assert boundary[key] == value
    assert boundary["g2d_status"] == G2D_V0310_SUCCESSOR_EXPECTED_FIELDS['g2d_status']
    assert boundary["g2d_contract_status"] == G2D_V0310_SUCCESSOR_EXPECTED_FIELDS['g2d_contract_status']
    assert boundary["g2d_contract_commit"] == G2D_V0310_SUCCESSOR_EXPECTED_FIELDS['g2d_contract_commit']
    assert boundary["g2d_release_consumer_maintenance_commit"] == G2D_V0310_SUCCESSOR_EXPECTED_FIELDS['g2d_release_consumer_maintenance_commit']
    assert boundary["g2d_correction_implementation_authorized"] == G2D_V0310_SUCCESSOR_EXPECTED_FIELDS['g2d_correction_implementation_authorized']
    assert boundary["g2d_implementation_action_open"] == G2D_V0310_SUCCESSOR_EXPECTED_FIELDS['g2d_implementation_action_open']
    assert boundary["g2d_corrected_implementation_exists"] == G2D_V0310_SUCCESSOR_EXPECTED_FIELDS['g2d_corrected_implementation_exists']
    assert boundary["g2d_contract_only_claim"] == G2D_V0310_SUCCESSOR_EXPECTED_FIELDS['g2d_contract_only_claim']
    assert boundary["g2d_runtime_implementation_status"] == G2D_V0310_SUCCESSOR_EXPECTED_FIELDS['g2d_runtime_implementation_status']
    assert boundary["g2d_full_owner_acceptance_passed"] == G2D_V0310_SUCCESSOR_EXPECTED_FIELDS['g2d_full_owner_acceptance_passed']
    assert boundary["g2d_corrected_implementation_commit"] == G2D_V0310_SUCCESSOR_EXPECTED_FIELDS['g2d_corrected_implementation_commit']
    assert boundary["g2d_independent_reaudit_passed"] == G2D_V0310_SUCCESSOR_EXPECTED_FIELDS['g2d_independent_reaudit_passed']
    assert boundary["g2d_independent_reaudit_commit"] == G2D_V0310_SUCCESSOR_EXPECTED_FIELDS['g2d_independent_reaudit_commit']
    assert boundary["g2d_corrected_closure_claimed"] == G2D_V0310_SUCCESSOR_EXPECTED_FIELDS['g2d_corrected_closure_claimed']
    assert boundary["g2d_additive_reclosure_completed"] == G2D_V0310_SUCCESSOR_EXPECTED_FIELDS['g2d_additive_reclosure_completed']
    assert boundary["g2d_additive_reclosure_required"] == G2D_V0310_SUCCESSOR_EXPECTED_FIELDS['g2d_additive_reclosure_required']
    assert boundary["g2d_v038_status"] == "CLOSED_PASS_ON_V038_BYTES"
    assert boundary["g2d_v039_contract_semantics_changed"] is False
    assert boundary["g2d_v039_status"] == "CLOSED_PASS_ON_V039_BYTES"
    assert boundary["g2d_v0310_profile_d_implementation_nonconformance"] is True
    assert boundary["g2d_v0310_g2d_runtime_semantics_changed"] is False
    assert boundary["g2d_v0310_g2e4_acceptance_overlay_semantics_changed"] is True
    assert boundary["g2d_v0310_positive_backpressure_law_changed"] is False
    assert boundary["g2d_v0310_e4_public_backpressure_calls_required"] == 2
    assert boundary["g2d_v0310_e4_public_backpressure_geometry_required"] == (
        [[0, 3], [2, 1]]
    )
    assert boundary[
        "g2d_v0310_e4_public_backpressure_latest_queue_counts_required"
    ] == [7, 15]
    assert boundary["g2d_v0310_e4_public_backpressure_results_required"] == [
        None,
        None,
    ]
    assert boundary["g2e3_status"] == G2D_V0310_SUCCESSOR_EXPECTED_FIELDS['g2e3_status']
    assert boundary["g2e3_historical_v038_status"] == (
        "IMPLEMENTED_COMMITTED_ACCEPTANCE_PASS_ON_V038_G2D"
    )
    assert boundary["g2e3_post_v0310_implementation_status"] == G2D_V0310_SUCCESSOR_EXPECTED_FIELDS['g2e3_post_v0310_implementation_status']
    assert boundary["g2e4_strict_subtree_status"] == G2D_V0310_SUCCESSOR_EXPECTED_FIELDS['g2e4_strict_subtree_status']
    assert boundary["g2e4_anti_gaming_acceptance"] == G2D_V0310_SUCCESSOR_EXPECTED_FIELDS['g2e4_anti_gaming_acceptance']
    assert boundary["gate2_status"] == G2D_V0310_SUCCESSOR_EXPECTED_FIELDS['gate2_status']
    assert overlay["frozen_evidence"] == FROZEN_EVIDENCE
    assert overlay["does_not_override"] == [
        "owner_instruction",
        "AGENTS.md",
        "accepted_checkpoints",
        "accepted_audits",
        "specs/human_passport_v0_25.md",
    ]
    assert overlay["release_spine_paths"] == list(RELEASE_SPINE_PATHS)
    baseline = json.loads(
        _git_show(G2D_V0310_BASIS, "release/current_status_overlay_v01.json")
    )
    reverted = copy.deepcopy(overlay)
    reverted["current_engineering_boundary"] = baseline["current_engineering_boundary"]
    assert reverted == baseline

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
    implementation_claim_row = next(
        line for line in claim_text.splitlines()
        if f"| {G2D_V0310_IMPLEMENTATION_CLAIM_ID} |" in line
    )
    assert G2D_V0310_IMPLEMENTATION_CLAIM_ID in observed_claim_ids
    assert "| REAUDIT_PENDING |" in implementation_claim_row
    for evidence in (
        G2D_V0310_IMPLEMENTATION_COMMIT,
        G2D_V0310_IMPLEMENTATION_PARENT,
        G2D_V0310_IMPLEMENTATION_PATCH_SHA256,
        G2D_V0310_OWNER_EVIDENCE_BUNDLE_SHA256,
        "REAUDIT_PENDING",
    ):
        assert evidence in implementation_claim_row
    if G2D_V0310_EXPECTED_SUCCESSOR_PHASE in {"reclosure", "final_e4_sync"}:
        closure_claim_row = next(
            line for line in claim_text.splitlines()
            if f"| {G2D_V0310_CLOSURE_CLAIM_ID} |" in line
        )
        assert G2D_V0310_CLOSURE_CLAIM_ID in observed_claim_ids
        assert "| CLOSED_PASS |" in closure_claim_row
        for evidence in (
            "CLOSED_PASS", G2D_V0310_INDEPENDENT_REAUDIT_PATH,
            G2D_V0310_CHECKPOINT_PATH, G2D_V0310_INDEPENDENT_REAUDIT_COMMIT,
            'b1ff61f42158d914b9afcf48e0d3ef5f9f980288d134130031e79c631f5101b6',
        ):
            assert evidence in closure_claim_row
    if G2D_V0310_EXPECTED_SUCCESSOR_PHASE == "final_e4_sync":
        e4_claim_row = next(
            line for line in claim_text.splitlines()
            if f"| {G2E4_V0310_ACCEPTANCE_CLAIM_ID} |" in line
        )
        assert G2E4_V0310_ACCEPTANCE_CLAIM_ID in observed_claim_ids
        assert "| ACCEPTANCE_PASS |" in e4_claim_row
        for evidence in (
            "ACCEPTANCE_PASS", G2D_V0310_E4_CODE_COMMIT,
            'ea1b030bb40e52aeb30ea5d49599ba2e3a59f50398ef8d74234ab77e30842157', '92390ad076307a73473f1bb22b65748bbc2e25bcdccd6fe0250312d26b124b31',
            '8301e6886ab1400fabffe1c850205c73b02919dc844dffe119a42550eb92b4ba',
        ):
            assert evidence in e4_claim_row
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
            G2E_CONTRACT_CLAIM_ID,
            G2D_V038_CONTRACT_CLAIM_ID,
            G2D_V038_IMPLEMENTATION_CLAIM_ID,
            G2D_V038_CLOSURE_CLAIM_ID,
            G2D_V039_CONTRACT_CLAIM_ID,
            G2D_V039_IMPLEMENTATION_CLAIM_ID,
            G2D_V039_CLOSURE_CLAIM_ID,
            G2D_V0310_CONTRACT_CLAIM_ID,
            *G2D_V0310_SUCCESSOR_CLAIM_IDS,
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
        assert G2D_V037_NORMATIVE_DONOR_SHA256 in active_g2d_row
        assert G2D_V037_ACCEPTED_ADDENDUM_SHA256 in active_g2d_row
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
        g2e_contract_row = next(
            line
            for line in claim_text.splitlines()
            if f"| {G2E_CONTRACT_CLAIM_ID} |" in line
        )
        assert G2E_CONTRACT_CLAIM_WORDING in g2e_contract_row
        assert "| CONTRACT_ACCEPTED_IMPLEMENTATION_PENDING |" in g2e_contract_row
        for path in (
            "tests/test_continuous_delta_runtime_g2_e_v01.py",
            "tests/test_repository_release_spine_v01.py",
            G2E_ACCEPTED_ADDENDUM_PATH,
        ):
            assert path in g2e_contract_row
            assert (REPOSITORY_ROOT / path).exists()
        for evidence_sha256 in (
            G2E_V013_NORMATIVE_DONOR_SHA256,
            G2E4_PUBLIC_SEAM_REGISTER_SHA256,
            G2E4_TWO_ROOT_PAIR_REGISTER_SHA256,
            G2E3_V06_ARCHIVE_SHA256,
        ):
            assert evidence_sha256 in g2e_contract_row
        for limitation in (
            "strict-subtree implementation is committed",
            "anti-gaming acceptance is blocked",
            "correction is not authorized",
            "Gate 2 is not closed",
            "no authority",
            "real-world effect",
            "production-readiness",
            "public-release",
        ):
            assert limitation in g2e_contract_row
        v038_row = next(
            line
            for line in claim_text.splitlines()
            if f"| {G2D_V038_CONTRACT_CLAIM_ID} |" in line
        )
        assert G2D_V038_CONTRACT_CLAIM_WORDING in v038_row
        assert "| HISTORICAL_CONTRACT_HOP_COMPLETED |" in v038_row
        for path in (
            "tests/test_fractal_runtime_g2_d_v02.py",
            "tests/test_repository_release_spine_v01.py",
            G2D_ACCEPTED_ADDENDUM_PATH,
        ):
            assert path in v038_row
            assert (REPOSITORY_ROOT / path).exists()
        for evidence_sha256 in (
            G2D_ACCEPTED_NORMATIVE_DONOR_SHA256,
            G2D_CONTROLLING_DESIGN_V03_SHA256,
            G2D_ACCEPTED_ADDENDUM_SHA256,
        ):
            assert evidence_sha256 in v038_row
        for required in (
            "V037_IMPLEMENTATION_NONCONFORMANCE=YES",
            "V038_CONTRACT_SEMANTICS_CHANGED=NO",
            "V038_ROLE=EXPLICIT_CLARIFICATION_AND_LIFECYCLE_REOPENING",
            "then-current implementation-pending limitation is superseded",
            "G2-E5/E6/F are not started",
            "Gate 2 is not closed",
            "no authority",
            "real-world effect",
        ):
            assert required in v038_row
        assert "immutable evidence for v0.3.7 bytes only" in v038_row
        assert G2D_CHECKPOINT_PATH not in v038_row
        v038_implementation_row = next(
            line
            for line in claim_text.splitlines()
            if f"| {G2D_V038_IMPLEMENTATION_CLAIM_ID} |" in line
        )
        assert G2D_V038_IMPLEMENTATION_CLAIM_WORDING in v038_implementation_row
        assert "| REAUDIT_PENDING |" in v038_implementation_row
        assert G2D_V038_IMPLEMENTATION_COMMIT in v038_implementation_row
        assert G2D_V038_IMPLEMENTATION_PATCH_SHA256 in v038_implementation_row
        assert G2D_V038_OWNER_EVIDENCE_BUNDLE_SHA256 in v038_implementation_row
        assert "NOT_SELF_RECORDED" not in v038_implementation_row
        for path in (
            "tests/test_fractal_runtime_g2_d_v02.py",
            "tests/test_transition_registry_v01.py",
            "tests/test_repository_release_spine_v01.py",
            "hedgehog/kernel/fractal_runtime_v02.py",
            G2D_ACCEPTED_ADDENDUM_PATH,
        ):
            assert path in v038_implementation_row
            assert (REPOSITORY_ROOT / path).exists()
        for required in (
            "independent re-audit pending",
            "v0.3.7 bytes only",
            "additive successor checkpoint and reclosure are mandatory",
            "corrected closure is not claimed",
            "REVALIDATION_PENDING_ON_CORRECTED_G2D",
            "BLOCKED_PENDING_G2D_RECLOSURE",
            "NOT_STARTED_NOT_AUTHORIZED",
            "NOT_CLOSED",
            "no successor baseline",
            "real-world effect",
        ):
            assert required in v038_implementation_row
        v038_closure_row = next(
            line
            for line in claim_text.splitlines()
            if f"| {G2D_V038_CLOSURE_CLAIM_ID} |" in line
        )
        assert G2D_V038_CLOSURE_CLAIM_WORDING in v038_closure_row
        assert "| CLOSED_PASS |" in v038_closure_row
        for path in (
            "tests/test_fractal_runtime_g2_d_v02.py",
            "tests/test_transition_registry_v01.py",
            "tests/test_living_gauntlet_v01_runner.py",
            "tests/test_kernel_conformance_v01_runner.py",
            "tests/test_repository_release_spine_v01.py",
            "tests/test_repository_maintenance_contract_v01.py",
            "demo/run_fractal_runtime_g2_d_v02.py",
            G2D_V038_INDEPENDENT_REAUDIT_PATH,
            G2D_V038_CHECKPOINT_PATH,
        ):
            assert path in v038_closure_row
            assert (REPOSITORY_ROOT / path).exists()
        for evidence in (
            G2D_V038_IMPLEMENTATION_COMMIT,
            G2D_V038_IMPLEMENTATION_PATCH_SHA256,
            G2D_V038_OWNER_EVIDENCE_BUNDLE_SHA256,
        ):
            assert evidence in v038_closure_row
        for limitation in (
            "does not close Gate 2",
            "does not validate G2-E3 on v0.3.8 bytes",
            "does not authorize E4 anti-gaming correction before fresh V06",
            "does not start E5/E6/F",
            "creates no authority, permission, FinalOutput, DRS write, or real-world effect",
        ):
            assert limitation in v038_closure_row
        v039_row = next(
            line
            for line in claim_text.splitlines()
            if f"| {G2D_V039_CONTRACT_CLAIM_ID} |" in line
        )
        assert G2D_V039_CONTRACT_CLAIM_WORDING in v039_row
        assert "| HISTORICAL_CONTRACT_HOP_COMPLETED |" in v039_row
        assert G2D_V039_ACCEPTED_ADDENDUM_SHA256 in v039_row
        assert G2D_V039_BASIS in v039_row
        assert G2D_V039_CONTRACT_COMMIT in v039_row
        for path in (
            "tests/test_fractal_runtime_g2_d_v02.py",
            "tests/test_repository_release_spine_v01.py",
            G2D_ACCEPTED_ADDENDUM_PATH,
        ):
            assert path in v039_row
            assert (REPOSITORY_ROOT / path).exists()
        for required in (
            "contract hop is complete",
            "implementation-pending status is superseded",
            "does not certify the v0.3.9 implementation",
            "close G2-D or Gate 2",
            "validate G2-E3 on v0.3.9 bytes",
            "authorize E4 anti-gaming correction",
            "create authority, permission, FinalOutput, DRS write, release, or effect",
        ):
            assert required in v039_row
        v039_implementation_row = next(
            line
            for line in claim_text.splitlines()
            if f"| {G2D_V039_IMPLEMENTATION_CLAIM_ID} |" in line
        )
        assert G2D_V039_IMPLEMENTATION_CLAIM_WORDING in v039_implementation_row
        assert "| REAUDIT_PENDING |" in v039_implementation_row
        for evidence in (
            G2D_V039_IMPLEMENTATION_COMMIT,
            G2D_V039_IMPLEMENTATION_PARENT,
            G2D_V039_IMPLEMENTATION_PATCH_SHA256,
            G2D_V039_OWNER_EVIDENCE_BUNDLE_SHA256,
        ):
            assert evidence in v039_implementation_row
        for path in (
            "tests/test_fractal_runtime_g2_d_v02.py",
            "tests/test_transition_registry_v01.py",
            "tests/test_repository_release_spine_v01.py",
            "tests/test_repository_maintenance_contract_v01.py",
            "tests/test_execution_mode_router_g2_c_v01.py",
            "tests/test_living_gauntlet_v01_runner.py",
            "tests/test_kernel_conformance_v01_runner.py",
            "hedgehog/kernel/fractal_runtime_v02.py",
        ):
            assert path in v039_implementation_row
            assert (REPOSITORY_ROOT / path).exists()
        for required in (
            "Corrected G2-D CLOSED_PASS is not claimed",
            "REVALIDATION_PENDING_ON_CORRECTED_G2D",
            "historical G2-E3 v0.3.8 acceptance remains evidence",
            "strict-subtree PASS is preserved",
            "BLOCKED_PENDING_G2D_V039_RECLOSURE",
            "NOT_STARTED_NOT_AUTHORIZED",
            "Gate 2 remains `NOT_CLOSED`",
            "no successor baseline",
            "real-world effect",
        ):
            assert required in v039_implementation_row
        v039_closure_row = next(
            line
            for line in claim_text.splitlines()
            if f"| {G2D_V039_CLOSURE_CLAIM_ID} |" in line
        )
        assert G2D_V039_CLOSURE_CLAIM_WORDING in v039_closure_row
        assert "| HISTORICAL_CLOSED_PASS_ON_V039_BYTES |" in v039_closure_row
        for evidence in (
            G2D_V039_IMPLEMENTATION_COMMIT,
            G2D_V039_IMPLEMENTATION_PATCH_SHA256,
            G2D_V039_OWNER_EVIDENCE_BUNDLE_SHA256,
            G2D_V039_INDEPENDENT_REAUDIT_COMMIT,
            G2D_V039_INDEPENDENT_REAUDIT_SHA256,
            G2D_V039_CHECKPOINT_SHA256,
        ):
            assert evidence in v039_closure_row
        for path in (
            "tests/test_fractal_runtime_g2_d_v02.py",
            "tests/test_transition_registry_v01.py",
            "tests/test_repository_release_spine_v01.py",
            "tests/test_repository_maintenance_contract_v01.py",
            "tests/test_execution_mode_router_g2_c_v01.py",
            "tests/test_living_gauntlet_v01_runner.py",
            "tests/test_kernel_conformance_v01_runner.py",
            "hedgehog/kernel/fractal_runtime_v02.py",
            G2D_V039_INDEPENDENT_REAUDIT_PATH,
            G2D_V039_CHECKPOINT_PATH,
        ):
            assert path in v039_closure_row
            assert (REPOSITORY_ROOT / path).exists()
        for limitation in (
            "Immutable closure evidence for exact v0.3.9 bytes only",
            "does not certify v0.3.10 implementation",
            "G2-E3 revalidation",
            "E4 anti-gaming acceptance",
            "Gate-2 closure",
            "authority",
            "release",
            "real-world effect",
        ):
            assert limitation in v039_closure_row
        v0310_contract_row = next(
            line
            for line in claim_text.splitlines()
            if f"| {G2D_V0310_CONTRACT_CLAIM_ID} |" in line
        )
        assert G2D_V0310_CONTRACT_CLAIM_WORDING in v0310_contract_row
        assert "| HISTORICAL_CONTRACT_HOP_COMPLETED |" in (
            v0310_contract_row
        )
        for evidence in (
            G2D_V0310_ACCEPTED_ADDENDUM_SHA256,
            G2D_V039_ACCEPTED_ADDENDUM_SHA256,
            G2D_V0310_BASIS,
            "((0,3),(2,1))",
            "(7,15)",
            "(None,None)",
            "explicit/internal public revise call accounting `4/0`",
            "mandatory one-path maintenance bridge",
            G2D_V0310_RELEASE_CONSUMER_MAINTENANCE_SUBJECT,
            "future implementation identities pinned only by that maintenance version",
        ):
            assert evidence in v0310_contract_row
        for path in (
            "tests/test_fractal_runtime_g2_d_v02.py::"
            "test_d3_post_acceptance_contract_addendum_v0310_accepted",
            "tests/test_repository_release_spine_v01.py",
            "tests/test_repository_maintenance_contract_v01.py",
            G2D_ACCEPTED_ADDENDUM_PATH,
            G2D_V0310_INDEPENDENT_REAUDIT_PATH,
            G2D_V0310_CHECKPOINT_PATH,
        ):
            assert path in v0310_contract_row
        for limitation in (
            "V039_PROFILE_D_IMPLEMENTATION_NONCONFORMANCE=YES",
            "runtime semantics",
            "public revise semantics",
            "positive 3/3 backpressure law are unchanged",
            "clean isolated worktree",
            "fe6cecec37512faad1c36eaea2a6ad61f4173998dfa09a993c0c889a1857dee0",
            "No v0.3.10 runtime implementation",
            "Gate-2 closure",
            "authority",
            "permission",
            "FinalOutput",
            "DRS write",
            "release",
            "real-world effect",
        ):
            assert limitation in v0310_contract_row
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
    for required in (
        "G2-C are `CLOSED_PASS`",
        "Historical G2-D v0.3.9 is `CLOSED_PASS_ON_V039_BYTES`",
        "Active G2-D v0.3.10 is `CORRECTION_CONTRACT_ACCEPTED_IMPLEMENTATION_PENDING`",
        "`V039_PROFILE_D_IMPLEMENTATION_NONCONFORMANCE=YES`",
        "`V0310_G2D_RUNTIME_SEMANTICS_CHANGED=NO`",
        "`V0310_G2E4_ACCEPTANCE_OVERLAY_SEMANTICS_CHANGED=YES`",
        "`G2D_POSITIVE_BACKPRESSURE_LAW_CHANGED=NO`",
        "mandatory release-consumer maintenance is authorized and required but `NOT_STARTED`",
        "must precede separate implementation authorization",
        "identities are deliberately absent from contract-commit bytes",
        "clean isolated Git worktree",
        "fe6cecec37512faad1c36eaea2a6ad61f4173998dfa09a993c0c889a1857dee0",
        G2D_V0310_ACCEPTED_ADDENDUM_SHA256,
        G2D_V039_ACCEPTED_ADDENDUM_SHA256,
        G2D_V0310_INDEPENDENT_REAUDIT_PATH,
        G2D_V0310_CHECKPOINT_PATH,
        "exactly two real public backpressure calls",
        "baseline `(occupied,residual)=(0,3)` over 7 lawful append-log-latest queue entries",
        "conditional `(2,1)` over 15 entries",
        "Both public backpressure results must be `None`",
        "stored revise order is eligible positive then noneligible `DEADEND`",
        "requires exactly one qualifying noneligible `DEADEND`",
        "lawful eligible observation is not ambiguity",
        "Public revise semantics are unchanged",
        "exactly 4 explicit public revise calls",
        "0 nested public calls",
        "G2-E3 is `REVALIDATION_PENDING_ON_CORRECTED_G2D`",
        "G2-E4 strict subtree is `IMPLEMENTED_COMMITTED_PASS`",
        "G2-E4 anti-gaming acceptance is `BLOCKED_PENDING_G2D_V0310_RECLOSURE`",
        "G2-E5, G2-E6, and G2-F remain `NOT_STARTED_NOT_AUTHORIZED`",
        "Public release, RC2, production readiness, production security certification, and successor baseline remain `NOT_CLAIMED`",
        "Real-world effects remain zero",
        "RuntimeExecutionTopology is not authority",
        "a child result is not FinalOutput",
    ):
        assert required in limitations_normalized
    for stale in (
        "BLOCKED_PENDING_G2D_V039_RECLOSURE",
        "BLOCKED_PENDING_G2D_RECLOSURE",
        "Active G2-D v0.3.9 is `CLOSED_PASS`",
        "v0.3.10 implementation is authorized",
    ):
        assert stale not in limitations

    notes = (REPOSITORY_ROOT / "release/current_release_notes.md").read_text(
        encoding="utf-8"
    )
    assert notes.startswith("# Current Engineering Notes\n")
    assert "not a public release announcement" in notes
    for required in (
        "Accepted guardian ruling: `APPROVE_PROFILE_D_CORRECTION_AND_E4_BACKPRESSURE_SCOPE_RECONCILIATION`",
        "Active status: `CORRECTION_CONTRACT_ACCEPTED_IMPLEMENTATION_PENDING`",
        G2D_V0310_ACCEPTED_ADDENDUM_SHA256,
        G2D_V039_ACCEPTED_ADDENDUM_SHA256,
        G2D_V0310_BASIS,
        "`V039_PROFILE_D_IMPLEMENTATION_NONCONFORMANCE=YES`",
        "`V0310_G2D_RUNTIME_SEMANTICS_CHANGED=NO`",
        "`V0310_G2E4_ACCEPTANCE_OVERLAY_SEMANTICS_CHANGED=YES`",
        "`G2D_POSITIVE_BACKPRESSURE_LAW_CHANGED=NO`",
        "both public results are `None`",
        "exact append-log latest order",
        "public call count remains exactly two",
        "exactly four explicit public revise calls",
        "zero nested public calls",
        "This contract-only hop changes exactly ten paths",
        G2D_V0310_INDEPENDENT_REAUDIT_PATH,
        G2D_V0310_CHECKPOINT_PATH,
        "Historical G2-D v0.3.9 is `CLOSED_PASS_ON_V039_BYTES`",
        "G2-E3 is `REVALIDATION_PENDING_ON_CORRECTED_G2D`",
        "G2-E4 strict subtree is `IMPLEMENTED_COMMITTED_PASS`",
        "anti-gaming acceptance is `BLOCKED_PENDING_G2D_V0310_RECLOSURE`",
        "Gate 2 is `NOT_CLOSED`",
        "Public release, RC2, production readiness, production security certification, and successor baseline remain `NOT_CLAIMED`",
        "Real-world effects remain zero",
    ):
        assert required in notes
    notes_normalized = " ".join(notes.split())
    for required in (
        "mandatory nonsemantic release-consumer maintenance commit",
        "Contract bytes retain prospective identity placeholders",
        "clean isolated Git worktree",
        "fe6cecec37512faad1c36eaea2a6ad61f4173998dfa09a993c0c889a1857dee0",
        "stores exactly two revise observations in order: an eligible positive "
        "observation followed by a noneligible `DEADEND` observation",
        "Profile-D must select exactly one qualifying noneligible `DEADEND`",
        "Missing proof or more than one qualifying `DEADEND` fails closed",
    ):
        assert required in notes_normalized
    for stale in (
        "BLOCKED_PENDING_G2D_V039_RECLOSURE",
        "BLOCKED_PENDING_G2D_RECLOSURE",
        "G2-D v0.3.9 is `CLOSED_PASS`",
    ):
        assert stale not in notes
    assert "Gate 2 is `NOT_CLOSED`" in notes
    assert "G2-D v0.3.9 is `CLOSED_PASS_ON_V039_BYTES`" in notes
    assert "BLOCKED_PENDING_G2D_V0310_RECLOSURE" in notes


def test_current_surfaces_preserve_status_and_licensing_nonclaims() -> None:
    historical_heading = "## Historical C/M boundary — superseded as current state"
    limitations = LIMITATIONS_PATH.read_text(encoding="utf-8")
    notes = NOTES_PATH.read_text(encoding="utf-8")
    assert limitations.count(historical_heading) == 1
    assert notes.count(historical_heading) == 1
    current_limitations = limitations.split(historical_heading, 1)[0]
    current_notes = notes.split(historical_heading, 1)[0]
    active_status_text = "\n".join((
        README_PATH.read_text(encoding="utf-8"),
        AGENTS_PATH.read_text(encoding="utf-8"),
        current_limitations,
        current_notes,
        json.dumps(_read_json(OVERLAY_PATH), sort_keys=True),
    ))
    active_text = active_status_text + "\n" + CLAIM_INDEX_PATH.read_text(
        encoding="utf-8"
    )
    lowered = active_text.lower()
    for required in (
        "CLOSED_PASS",
        "IMPLEMENTED_COMMITTED_ACCEPTANCE_PASS_ON_CORRECTED_G2D",
        "IMPLEMENTED_COMMITTED_PASS",
        "G2-E4 anti-gaming acceptance is `PASS`",
        "NOT_STARTED_NOT_AUTHORIZED",
        "NOT_CLOSED",
        G2D_V0310_IMPLEMENTATION_COMMIT,
        "real-world effects remain zero",
    ):
        assert required in active_text
    for forbidden in (
        "CORRECTION_CONTRACT_ACCEPTED_IMPLEMENTATION_PENDING",
        "ACCEPTED_IMPLEMENTATION_PENDING",
        "BLOCKED_PENDING_G2D_V0310_RECLOSURE",
        "BLOCKED_PENDING_G2D_V039_RECLOSURE",
        "BLOCKED_PENDING_G2D_RECLOSURE",
        "full cumulative acceptance remains pending the owner",
        '"g2d_status": "DEPRECATED_PRE_V0310_STATUS"',
        '"g2d_correction_implementation_authorized": true',
        '"g2d_v0310_implementation_authorized": true',
        '"g2d_v0310_corrected_implementation_exists": "DEPRECATED_PRE_V0310"',
    ):
        assert forbidden not in active_status_text
    assert "public release" in lowered
    assert "production readiness" in lowered
    assert "real-world effect" in lowered
    assert "g2-c is in development" not in lowered
    assert "functional equivalents are licensed" not in lowered
    for affirmative_claim in (
        "title is established",
        "relicensing authority is established",
        "patent clearance is complete",
        "legal review is complete",
    ):
        assert affirmative_claim not in lowered
    for key, value in G2E_CURRENT_BOUNDARY_FIELDS.items():
        assert _current_boundary()[key] == value

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
    current_addendum = (
        REPOSITORY_ROOT / G2D_ACCEPTED_ADDENDUM_PATH
    ).read_bytes()
    assert _sha256_bytes(current_addendum) == G2D_V0310_ACCEPTED_ADDENDUM_SHA256
    assert len(current_addendum) == 237495
    assert current_addendum.count(b"\n") == 4736
    separator = (
        b"===============================================================================\n"
        b"HISTORICAL ACCEPTED V0.3.9 CONTENT - EXACT REPOSITORY BYTES\n"
        b"===============================================================================\n"
        b"\n"
        b"The complete byte sequence below is the previously accepted cumulative\n"
        b"v0.3.9 addendum. It remains immutable historical contract and evidence context\n"
        b"for its exact bytes. Its embedded present-tense lifecycle statements do not\n"
        b"override the active v0.3.10 metadata and rulings above.\n"
        b"\n"
    )
    assert current_addendum.count(separator) == 1
    active_v0310, historical_v039 = current_addendum.split(separator, 1)
    assert _sha256_bytes(historical_v039) == G2D_V039_ACCEPTED_ADDENDUM_SHA256
    assert len(historical_v039) == 212148
    assert historical_v039.count(b"\n") == 4185
    active_text = active_v0310.decode("ascii")
    for required in (
        "document_revision: v0.3.10",
        "guardian_ruling: APPROVE_PROFILE_D_CORRECTION_AND_E4_BACKPRESSURE_SCOPE_RECONCILIATION",
        "V039_PROFILE_D_IMPLEMENTATION_NONCONFORMANCE: YES",
        "V0310_G2D_RUNTIME_SEMANTICS_CHANGED: NO",
        "V0310_G2E4_ACCEPTANCE_OVERLAY_SEMANTICS_CHANGED: YES",
        "G2D_POSITIVE_BACKPRESSURE_LAW_CHANGED: NO",
        "G2D_PUBLIC_REVISE_SEMANTICS_CHANGED: NO",
        "implementation_authorized: false",
        "implementation_started: false",
        "historical_v039_g2d_status: CLOSED_PASS_ON_V039_BYTES",
        "g2e4_public_backpressure_geometry_required: ((0,3),(2,1))",
        "g2e4_public_backpressure_latest_queue_counts_required: (7,15)",
        "g2e4_public_backpressure_results_required: NONE_NONE",
        "g2e4_explicit_public_revise_calls_required: 4",
        "g2d_internal_public_revise_calls_per_reconstruction_required: 0",
        "release_consumer_maintenance_required: true",
        "release_consumer_maintenance_status: NOT_STARTED",
        "release_consumer_maintenance_scope: tests/test_repository_release_spine_v01.py",
        "parked_primary_e4_patch_sha256: fe6cecec37512faad1c36eaea2a6ad61f4173998dfa09a993c0c889a1857dee0",
        "runtime_identity: PINNED_BY_RELEASE_CONSUMER_MAINTENANCE",
        "test_identity: PINNED_BY_RELEASE_CONSUMER_MAINTENANCE",
        "full_index_patch_identity: PINNED_BY_RELEASE_CONSUMER_MAINTENANCE",
        "clean isolated Git worktree",
        "latest queue order = exact append-log order at both calls",
        "G2E4_ANTI_GAMING_STATUS=BLOCKED_PENDING_G2D_V0310_RECLOSURE",
        "E4_PAIR_CALL_ACCOUNTING=2/2",
        "E4_FOCUSED_CALL_ACCOUNTING=2/2",
        "E4_COMPLETE_FILE_CALL_ACCOUNTING=3/3",
        "Root remains the only final authority",
        "This contract-only hop authorizes no implementation",
    ):
        assert required in active_text
    active_normalized = " ".join(active_text.split())
    for selector_law in (
        "must not require the total number of observations bound to the "
        "`VALIDATING` queue entry to equal one",
        "stores an eligible positive observation followed by a noneligible "
        "`DEADEND` observation on the same exact topology, cell, queue, budget, "
        "and revision binding",
        "more than one qualifying noneligible `DEADEND` observation is real "
        "local ambiguity",
        "The lawful eligible positive observation is neither extra proof nor "
        "ambiguity",
        "exactly one qualifies for Profile-D `DEADEND` projection",
    ):
        assert selector_law in active_normalized

    v039_separator = (
        b"===============================================================================\n"
        b"HISTORICAL ACCEPTED V0.3.8 CONTENT - EXACT REPOSITORY BYTES\n"
        b"===============================================================================\n"
        b"\n"
        b"The complete byte sequence below is the previously accepted v0.3.8 addendum.\n"
        b"It remains immutable historical contract and evidence context for v0.3.8. Its\n"
        b"embedded present-tense lifecycle statements do not override the active v0.3.9\n"
        b"metadata and clarification above.\n"
        b"\n"
    )
    assert historical_v039.count(v039_separator) == 1
    active_v039, historical_v038 = historical_v039.split(v039_separator, 1)
    assert _sha256_bytes(historical_v038) == G2D_ACCEPTED_ADDENDUM_SHA256
    assert len(historical_v038) == 197537
    assert historical_v038.count(b"\n") == 3828
    active_text = active_v039.decode("ascii")
    for required in (
        "document_revision: v0.3.9",
        "guardian_ruling: APPROVE_WITH_MANDATORY_OVERLAY",
        "V038_IMPLEMENTATION_NONCONFORMANCE: YES",
        "V039_CONTRACT_SEMANTICS_CHANGED: NO",
        "V039_ROLE: EXPLICIT_IMPLEMENTATION_NONCONFORMANCE_CLARIFICATION_AND_LIFECYCLE_REOPENING",
        "implementation_authorized: false",
        "historical_v038_g2d_status: CLOSED_PASS_ON_V038_BYTES",
        "g2d_t12_validating_to_deadend",
        "G2E4_ANTI_GAMING_STATUS=BLOCKED_PENDING_G2D_V039_RECLOSURE",
        "E4_PAIR_CALL_ACCOUNTING=2/2",
        "E4_FOCUSED_CALL_ACCOUNTING=2/2",
        "E4_COMPLETE_FILE_CALL_ACCOUNTING=3/3",
        "Root remains the only final authority",
        "This contract-only hop authorizes no implementation",
    ):
        assert required in active_text

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
        f"accepted_v037_addendum_sha256: {G2D_V037_ACCEPTED_ADDENDUM_SHA256}",
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

    v038_checkpoint_path = REPOSITORY_ROOT / G2D_V038_CHECKPOINT_PATH
    assert v038_checkpoint_path.is_file()
    v038_raw = v038_checkpoint_path.read_bytes()
    v038_text = v038_raw.decode("utf-8")
    assert _sha256_bytes(v038_raw) == G2D_V038_CHECKPOINT_SHA256
    assert v038_checkpoint_path.stat().st_mode & 0o777 == 0o644
    assert v038_raw.endswith(b"\n")
    assert b"\x00" not in v038_raw
    assert b"\r" not in v038_raw
    assert tuple(
        re.findall(r"^## \d+\..+$", v038_text, re.MULTILINE)
    ) == required_sections
    for required in (
        "document_status: CHECKPOINT",
        "checkpoint_id: "
        "fractal_runtime_v0_2_g2_d_proof_based_whole_run_correction_v01",
        "checkpoint_version: v0.1",
        "gate_id: gate2_g2d_fractal_runtime_v0_2_v038_correction",
        "gate_slice: G2-D",
        "corrected_g2d_status: CLOSED_PASS",
        "closure_commit_identity: NOT_SELF_RECORDED",
        f"closure_commit_subject: {G2D_V038_CLOSURE_SUBJECT}",
        f"accepted_v038_addendum_sha256: {G2D_ACCEPTED_ADDENDUM_SHA256}",
        f"historical_v037_addendum_sha256: {G2D_V037_ACCEPTED_ADDENDUM_SHA256}",
        f"corrected_implementation_commit: {G2D_V038_IMPLEMENTATION_COMMIT}",
        f"corrected_implementation_parent_commit: {G2D_V038_IMPLEMENTATION_BASIS}",
        "corrected_implementation_patch_sha256: "
        f"{G2D_V038_IMPLEMENTATION_PATCH_SHA256}",
        f"post_implementation_lifecycle_sync_commit: {G2D_V038_LIFECYCLE_SYNC_COMMIT}",
        f"independent_reaudit_commit: {G2D_V038_INDEPENDENT_REAUDIT_COMMIT}",
        f"independent_reaudit_path: {G2D_V038_INDEPENDENT_REAUDIT_PATH}",
        f"independent_reaudit_sha256: {G2D_V038_INDEPENDENT_REAUDIT_SHA256}",
        f"owner_evidence_bundle_sha256: {G2D_V038_OWNER_EVIDENCE_BUNDLE_SHA256}",
        "independent_reaudit_evidence_bundle_sha256: "
        f"{G2D_V038_INDEPENDENT_REAUDIT_EVIDENCE_SHA256}",
        "cannot record its own commit identity without",
    ):
        assert required in v038_text
    assert v038_text.count("closure_commit_identity: NOT_SELF_RECORDED") == 1

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
        "Package `__all__`: `19`",
        "Validation targets: `35`",
        "Failure stages: `30`",
        "Public reason codes: `220`",
        "Transition rules: `17`",
        "`FractalRuntimeExecutionBundleV02` fields: `28`",
        "G2-D test functions/items: `83/92`",
        "Transition test functions/items: `60/268`",
        "D5 cases/split/accepted runs: `72/36-36/10`",
    ):
        assert required in v038_text

    for required in (
        "Transition facade consumer focused: 1/1 PASS, calls 0/0",
        "Complete Transition: 268/268 PASS, calls 0/0",
        "Focused G2-D/Transition: 43/43 PASS, calls 3/3",
        "Complete G2-C: 392/392 PASS, calls 0/0",
        "Release plus maintenance: 23/23 PASS, calls 0/0",
        "Shared compatibility: 64/64 PASS, calls 0/0",
        "Complete G2-D plus Transition: 360/360 PASS, calls 30/30",
        "D5 child 1: PASS",
        "D5 child 2: PASS",
        "D5 cases per process: 72",
        "D5 split per process: 36/36",
        "D5 accepted bundles per process: 10",
        "D5 public calls per process: 27/27",
        "ec05a8cf9377953abdf84b8a45af07afa3615bcaf78411be6a351fe895663f86",
        "frg2dproof_v02:3bf2eb39b8e4e2ea0fe5b7517f677da3b784c43b75d60bce09fb69524c7cc2e1",
        "Complete Living: 575/575 PASS, calls 27/27",
        "Complete Kernel Conformance: 349/349 PASS, calls 27/27",
        "Anti-gaming micro: 4/4 PASS, calls 3/3",
        "d3b2b8789f1490422537a28d3616807aec8acdcef817732d6e4d54300e6c0eeb",
        "435037a91f85783963d9c565f8b1eba546ab2318ff7e30baa51be18aca8beaff",
        "e74cbf5dde1c21d2750c372d838e3e56f0dbbfead5b1e1a629a228d4cf0f1e47",
        "e6d651c909f34251da873531838978588842a2b5f3bc158682e3c6089427a349",
        "5a4e4d6b9877d9e93195bb6715e8c83418631dd45f1cab0fedd91dee8502528e",
        "9049eb8ac32894f743746cecab93e9045d23a4bb25314021bd1952a17b4437d7",
        "9ec46d157b5382ebee757035fdb6540389f640ab7df99421cb5de83e41e0d2b8",
        "bc30b2ddcabc2d4f78943aec5f5fb1912cddea55db8cb1eec1b69e98a18fd63d",
        "7c80e053e2423fd296f51a9535e4e261453462e21200de508b725ba2aed13f38",
        "4bf08b89b45356e19e18d083442c5c5595ff441cd52e96b9c21afc6af5d539af",
        "36d91a16d778837427937ddce68ae4ae77fc9c3b5d3084e13209876ea2d676c4",
    ):
        assert required in v038_text

    v038_scope = v038_text.split(required_sections[6], 1)[1].split(
        required_sections[7], 1
    )[0]
    assert tuple(
        match.group(1)
        for match in re.finditer(r"^\d+\. `([^`]+)`", v038_scope, re.MULTILINE)
    ) == G2D_V038_CLOSURE_PATHS
    for required in (
        "G2E3_STATUS=REVALIDATION_PENDING_ON_CORRECTED_G2D",
        "G2E4_STATUS=BLOCKED_PENDING_FRESH_G2E3_V06",
        "G2E4_ANTI_GAMING_ACCEPTANCE=BLOCKED_PENDING_FRESH_G2E3_V06",
        "G2E5_STARTED=false",
        "G2E6_STARTED=false",
        "G2F_STARTED=false",
        "GATE2_STATUS=NOT_CLOSED",
        "ROOT_ONLY_FINAL_AUTHORITY=true",
        "REAL_WORLD_EFFECTS=0",
        "No old audit or checkpoint certifies v0.3.8 bytes",
    ):
        assert required in v038_text

    v039_checkpoint_path = REPOSITORY_ROOT / G2D_V039_CHECKPOINT_PATH
    assert v039_checkpoint_path.is_file()
    v039_raw = v039_checkpoint_path.read_bytes()
    v039_text = v039_raw.decode("ascii")
    assert _sha256_bytes(v039_raw) == G2D_V039_CHECKPOINT_SHA256
    assert v039_checkpoint_path.stat().st_mode & 0o777 == 0o644
    assert v039_raw.endswith(b"\n")
    assert b"\x00" not in v039_raw
    assert b"\r" not in v039_raw
    assert tuple(
        re.findall(r"^## \d+\..+$", v039_text, re.MULTILINE)
    ) == required_sections
    for required in (
        "document_status: CHECKPOINT",
        "checkpoint_role: ADDITIVE_SUCCESSOR_CHECKPOINT",
        "checkpoint_id: "
        "fractal_runtime_v0_2_g2_d_t12_revise_no_progress_correction_v01",
        "checkpoint_version: v0.1",
        "gate_id: gate2_g2d_fractal_runtime_v0_2_v039_correction",
        "gate_slice: G2-D",
        "corrected_g2d_status: CLOSED_PASS",
        "closure_commit_identity: NOT_SELF_RECORDED",
        f"closure_commit_subject: {G2D_V039_CLOSURE_SUBJECT}",
        f"accepted_v039_addendum_sha256: {G2D_V039_ACCEPTED_ADDENDUM_SHA256}",
        f"contract_commit: {G2D_V039_CONTRACT_COMMIT}",
        "release_consumer_maintenance_commit: "
        f"{G2D_V039_RELEASE_CONSUMER_MAINTENANCE_COMMIT}",
        f"corrected_implementation_commit: {G2D_V039_IMPLEMENTATION_COMMIT}",
        "corrected_implementation_parent_commit: "
        f"{G2D_V039_IMPLEMENTATION_PARENT}",
        "corrected_implementation_patch_sha256: "
        f"{G2D_V039_IMPLEMENTATION_PATCH_SHA256}",
        "post_implementation_lifecycle_sync_commit: "
        f"{G2D_V039_LIFECYCLE_SYNC_COMMIT}",
        f"independent_reaudit_commit: {G2D_V039_INDEPENDENT_REAUDIT_COMMIT}",
        f"independent_reaudit_path: {G2D_V039_INDEPENDENT_REAUDIT_PATH}",
        f"independent_reaudit_sha256: {G2D_V039_INDEPENDENT_REAUDIT_SHA256}",
        "owner_execution_evidence_sha256: "
        f"{G2D_V039_OWNER_EVIDENCE_BUNDLE_SHA256}",
        "lifecycle_sync_evidence_sha256: "
        f"{G2D_V039_LIFECYCLE_SYNC_EVIDENCE_SHA256}",
        "independent_reaudit_evidence_sha256: "
        f"{G2D_V039_INDEPENDENT_REAUDIT_EVIDENCE_SHA256}",
    ):
        assert required in v039_text
    assert v039_text.count("closure_commit_identity: NOT_SELF_RECORDED") == 1
    for required in (
        "Root remains the only final authority",
        "G2-C owns the accepted Root-reviewed route",
        "G2-D owns `RuntimeExecutionTopology` and stable topology-node and cell IDs",
        "audit and this checkpoint are evidence, not authority",
        "No PlanGraph ownership path is introduced",
        "successor runtime baseline",
        "PUBLIC_T12_REVISE_NO_PROGRESS_CHAIN=PASS",
        "G2D_V039_INDEPENDENT_REAUDIT=PASS",
        "G2D_V039_ADDITIVE_RECLOSURE_COMPLETED=true",
        "G2D_V039_CORRECTED_CLOSED_PASS=true",
        "G2D_STATUS=CLOSED_PASS",
        "G2E3_STATUS=REVALIDATION_PENDING_ON_CORRECTED_G2D",
        "G2E4_STRICT_SUBTREE_STATUS=IMPLEMENTED_COMMITTED_PASS",
        "G2E4_ANTI_GAMING_ACCEPTANCE=BLOCKED_PENDING_FRESH_G2E3_V06",
        "GATE2_STATUS=NOT_CLOSED",
        "REAL_WORLD_EFFECTS=0",
    ):
        assert required in v039_text
    v039_scope = v039_text.split(required_sections[6], 1)[1].split(
        required_sections[7], 1
    )[0]
    assert tuple(
        match.group(1)
        for match in re.finditer(r"^\d+\. `([^`]+)`", v039_scope, re.MULTILINE)
    ) == G2D_V039_RECLOSURE_PATHS

def test_g2d_current_manifest_and_overlay_transition_are_exact() -> None:
    current_manifest = _read_json(MANIFEST_PATH)
    current_overlay = _read_json(OVERLAY_PATH)
    current_manifest_boundary = current_manifest["current_checkpoint_status"][
        "current_engineering_boundary_v01"
    ]
    current_overlay_boundary = current_overlay["current_engineering_boundary"]
    assert current_manifest_boundary == current_overlay_boundary == _current_boundary()
    for key, value in G2D_CURRENT_BOUNDARY_FIELDS.items():
        assert current_manifest_boundary[key] == value
    for key, value in G2E_CURRENT_BOUNDARY_FIELDS.items():
        assert current_manifest_boundary[key] == value
    assert current_manifest_boundary["gate2_status"] == G2D_V0310_SUCCESSOR_EXPECTED_FIELDS['gate2_status']
    assert current_manifest_boundary["g2d_status"] == G2D_V0310_SUCCESSOR_EXPECTED_FIELDS['g2d_status']
    assert current_manifest_boundary["g2d_contract_status"] == G2D_V0310_SUCCESSOR_EXPECTED_FIELDS['g2d_contract_status']
    assert current_manifest_boundary["g2d_v039_implementation_authorized"] is False
    assert current_manifest_boundary["g2d_v039_implementation_action_open"] is False
    assert current_manifest_boundary["g2d_v039_corrected_implementation_exists"] is True
    assert current_manifest_boundary["g2d_v039_corrected_implementation_committed"] is True
    assert current_manifest_boundary["g2d_v039_full_owner_acceptance_passed"] is True
    assert current_manifest_boundary["g2d_v039_runtime_implementation_status"] == (
        G2D_V039_RUNTIME_IMPLEMENTATION_STATUS
    )
    assert current_manifest_boundary["g2d_v039_contract_hop_completed"] is True
    assert current_manifest_boundary["g2d_v039_status"] == (
        "CLOSED_PASS_ON_V039_BYTES"
    )
    assert current_manifest_boundary["g2d_v0310_contract_hop_completed"] is True
    assert current_manifest_boundary["g2d_v0310_implementation_authorized"] == G2D_V0310_SUCCESSOR_EXPECTED_FIELDS['g2d_v0310_implementation_authorized']
    assert current_manifest_boundary["g2d_v0310_implementation_started"] == G2D_V0310_SUCCESSOR_EXPECTED_FIELDS['g2d_v0310_implementation_started']
    assert current_manifest_boundary[
        "g2d_v0310_corrected_implementation_exists"
    ] == G2D_V0310_SUCCESSOR_EXPECTED_FIELDS['g2d_v0310_corrected_implementation_exists']
    assert current_manifest_boundary["g2d_independent_reaudit_passed"] == G2D_V0310_SUCCESSOR_EXPECTED_FIELDS['g2d_independent_reaudit_passed']
    assert current_manifest_boundary["g2d_independent_reaudit_commit"] == G2D_V0310_SUCCESSOR_EXPECTED_FIELDS['g2d_independent_reaudit_commit']
    assert current_manifest_boundary["g2d_independent_reaudit_path"] == G2D_V0310_SUCCESSOR_EXPECTED_FIELDS['g2d_independent_reaudit_path']
    assert current_manifest_boundary["g2d_independent_reaudit_sha256"] == G2D_V0310_SUCCESSOR_EXPECTED_FIELDS['g2d_independent_reaudit_sha256']
    assert current_manifest_boundary["g2d_additive_reclosure_completed"] == G2D_V0310_SUCCESSOR_EXPECTED_FIELDS['g2d_additive_reclosure_completed']
    assert current_manifest_boundary["g2d_corrected_closure_claimed"] == G2D_V0310_SUCCESSOR_EXPECTED_FIELDS['g2d_corrected_closure_claimed']
    assert current_manifest_boundary["g2d_corrected_checkpoint_path"] == G2D_V0310_SUCCESSOR_EXPECTED_FIELDS['g2d_corrected_checkpoint_path']
    assert current_manifest_boundary["g2d_corrected_checkpoint_sha256"] == G2D_V0310_SUCCESSOR_EXPECTED_FIELDS['g2d_corrected_checkpoint_sha256']
    assert current_manifest_boundary["g2e3_status"] == G2D_V0310_SUCCESSOR_EXPECTED_FIELDS['g2e3_status']
    assert current_manifest_boundary["g2e3_historical_v038_status"] == (
        "IMPLEMENTED_COMMITTED_ACCEPTANCE_PASS_ON_V038_G2D"
    )
    assert current_manifest_boundary["g2e3_post_v0310_implementation_status"] == G2D_V0310_SUCCESSOR_EXPECTED_FIELDS['g2e3_post_v0310_implementation_status']
    assert current_manifest_boundary["g2e4_anti_gaming_acceptance"] == G2D_V0310_SUCCESSOR_EXPECTED_FIELDS['g2e4_anti_gaming_acceptance']
    basis_manifest = json.loads(
        _git_show(G2D_V0310_BASIS, "specs/machine_manifest_v0_25.json")
    )
    basis_overlay = json.loads(
        _git_show(G2D_V0310_BASIS, "release/current_status_overlay_v01.json")
    )
    reverted_current_manifest = copy.deepcopy(current_manifest)
    reverted_current_manifest["current_checkpoint_status"][
        "current_engineering_boundary_v01"
    ] = basis_manifest["current_checkpoint_status"][
        "current_engineering_boundary_v01"
    ]
    assert reverted_current_manifest == basis_manifest
    reverted_current_overlay = copy.deepcopy(current_overlay)
    reverted_current_overlay["current_engineering_boundary"] = basis_overlay[
        "current_engineering_boundary"
    ]
    assert reverted_current_overlay == basis_overlay

    v039_audit_manifest = json.loads(
        _git_show(
            G2D_V039_INDEPENDENT_REAUDIT_COMMIT,
            "specs/machine_manifest_v0_25.json",
        )
    )
    v039_audit_overlay = json.loads(
        _git_show(
            G2D_V039_INDEPENDENT_REAUDIT_COMMIT,
            "release/current_status_overlay_v01.json",
        )
    )
    v039_audit_manifest_boundary = v039_audit_manifest[
        "current_checkpoint_status"
    ]["current_engineering_boundary_v01"]
    v039_audit_overlay_boundary = v039_audit_overlay[
        "current_engineering_boundary"
    ]
    assert v039_audit_manifest_boundary == v039_audit_overlay_boundary
    v039_closed_manifest_boundary = basis_manifest[
        "current_checkpoint_status"
    ]["current_engineering_boundary_v01"]
    v039_closed_overlay_boundary = basis_overlay["current_engineering_boundary"]
    assert v039_closed_manifest_boundary == v039_closed_overlay_boundary
    missing = object()
    v039_reclosure_changes = {
        key
        for key in set(v039_closed_manifest_boundary)
        | set(v039_audit_manifest_boundary)
        if v039_closed_manifest_boundary.get(key, missing)
        != v039_audit_manifest_boundary.get(key, missing)
    }
    assert v039_reclosure_changes == {
        "g2d_status",
        "g2d_corrected_runtime_acceptance_claimed",
        "g2d_independent_reaudit_passed",
        "g2d_independent_reaudit_commit",
        "g2d_independent_reaudit_path",
        "g2d_independent_reaudit_sha256",
        "g2d_additive_reclosure_completed",
        "g2d_corrected_closure_claimed",
        "g2d_corrected_checkpoint_path",
        "g2d_corrected_checkpoint_sha256",
        "g2e4_anti_gaming_acceptance",
    }
    reverted_v039_manifest = copy.deepcopy(basis_manifest)
    reverted_v039_manifest["current_checkpoint_status"][
        "current_engineering_boundary_v01"
    ] = v039_audit_manifest_boundary
    assert reverted_v039_manifest == v039_audit_manifest
    reverted_v039_overlay = copy.deepcopy(basis_overlay)
    reverted_v039_overlay["current_engineering_boundary"] = (
        v039_audit_overlay_boundary
    )
    assert reverted_v039_overlay == v039_audit_overlay

    manifest = json.loads(
        _git_show(G2D_V039_BASIS, "specs/machine_manifest_v0_25.json")
    )
    overlay = json.loads(
        _git_show(G2D_V039_BASIS, "release/current_status_overlay_v01.json")
    )
    manifest_boundary = manifest["current_checkpoint_status"][
        "current_engineering_boundary_v01"
    ]
    overlay_boundary = overlay["current_engineering_boundary"]
    assert manifest_boundary == overlay_boundary
    audit_manifest = json.loads(
        _git_show(G2D_V038_INDEPENDENT_REAUDIT_COMMIT, "specs/machine_manifest_v0_25.json")
    )
    audit_overlay = json.loads(
        _git_show(
            G2D_V038_INDEPENDENT_REAUDIT_COMMIT,
            "release/current_status_overlay_v01.json",
        )
    )
    audit_manifest_boundary = audit_manifest["current_checkpoint_status"][
        "current_engineering_boundary_v01"
    ]
    audit_overlay_boundary = audit_overlay["current_engineering_boundary"]
    assert audit_manifest_boundary == audit_overlay_boundary
    missing = object()
    changed_by_v038_reclosure = {
        key
        for key in set(manifest_boundary) | set(audit_manifest_boundary)
        if manifest_boundary.get(key, missing)
        != audit_manifest_boundary.get(key, missing)
    }
    assert changed_by_v038_reclosure == {
        "g2d_status",
        "g2d_corrected_runtime_acceptance_claimed",
        "g2d_independent_reaudit_passed",
        "g2d_independent_reaudit_commit",
        "g2d_independent_reaudit_path",
        "g2d_independent_reaudit_sha256",
        "g2d_additive_reclosure_completed",
        "g2d_corrected_closure_claimed",
        "g2d_corrected_checkpoint_path",
        "g2d_corrected_checkpoint_sha256",
        "g2e4_status",
        "g2e4_anti_gaming_acceptance",
    }
    reverted_current_manifest = copy.deepcopy(manifest)
    reverted_current_manifest["current_checkpoint_status"][
        "current_engineering_boundary_v01"
    ] = audit_manifest_boundary
    assert reverted_current_manifest == audit_manifest
    reverted_current_overlay = copy.deepcopy(overlay)
    reverted_current_overlay["current_engineering_boundary"] = audit_overlay_boundary
    assert reverted_current_overlay == audit_overlay

    reclosure_manifest = json.loads(
        _git_show(G2D_CLOSURE_COMMIT, "specs/machine_manifest_v0_25.json")
    )
    reclosure_overlay = json.loads(
        _git_show(G2D_CLOSURE_COMMIT, "release/current_status_overlay_v01.json")
    )
    reclosure_manifest_boundary = reclosure_manifest["current_checkpoint_status"][
        "current_engineering_boundary_v01"
    ]
    reclosure_overlay_boundary = reclosure_overlay["current_engineering_boundary"]
    assert reclosure_manifest_boundary == reclosure_overlay_boundary
    changed_since_reclosure = {
        key
        for key in set(manifest_boundary) | set(reclosure_manifest_boundary)
        if manifest_boundary.get(key, missing)
        != reclosure_manifest_boundary.get(key, missing)
    }
    assert tuple(sorted(changed_since_reclosure)) == ('g2d_accepted_normative_donor_sha256', 'g2d_accepted_repository_addendum_sha256', 'g2d_corrected_checkpoint_path', 'g2d_corrected_checkpoint_sha256', 'g2d_corrected_implementation_commit', 'g2d_corrected_implementation_patch_sha256', 'g2d_corrected_owner_evidence_bundle_sha256', 'g2d_independent_reaudit_commit', 'g2d_independent_reaudit_path', 'g2d_independent_reaudit_sha256', 'g2d_v037_accepted_addendum_sha256', 'g2d_v037_accepted_normative_donor_sha256', 'g2d_v037_checkpoint_path', 'g2d_v037_checkpoint_sha256', 'g2d_v037_closure_commit', 'g2d_v037_corrected_implementation_commit', 'g2d_v037_corrected_implementation_patch_sha256', 'g2d_v037_evidence_classification', 'g2d_v037_implementation_nonconformance', 'g2d_v037_independent_reaudit_commit', 'g2d_v037_independent_reaudit_path', 'g2d_v037_independent_reaudit_sha256', 'g2d_v037_owner_evidence_bundle_sha256', 'g2d_v037_status', 'g2d_v038_accepted_addendum_sha256', 'g2d_v038_contract_semantics_changed', 'g2d_v038_controlling_design_v03_sha256', 'g2d_v038_directional_draft_review', 'g2d_v038_directional_draft_sha256', 'g2d_v038_full_acceptance_pending_owner', 'g2d_v038_implementation_authorized', 'g2d_v038_implementation_started', 'g2d_v038_role', 'g2e3_baseline_member_identities_sha256', 'g2e3_baseline_member_observation_sha256', 'g2e3_baseline_source_observation_sha256', 'g2e3_post_reclosure_v06_archive_sha256', 'g2e3_post_reclosure_v06_passed', 'g2e4_anti_gaming_acceptance', 'g2e4_anti_gaming_correction_authorized', 'g2e4_contract_accepted', 'g2e4_contract_status', 'g2e4_implementation_authorized', 'g2e4_implementation_started', 'g2e4_public_seam_register_sha256', 'g2e4_status', 'g2e4_strict_subtree_implementation_committed', 'g2e4_two_root_pair_register_sha256', 'g2e5_status', 'g2e6_status', 'g2e_accepted_addendum_revision', 'g2e_accepted_addendum_sha256', 'g2e_accepted_preflight_sha256', 'g2e_v013_normative_donor_sha256', 'g2f_status')
    reverted_contract_manifest = copy.deepcopy(manifest)
    reverted_contract_manifest["current_checkpoint_status"][
        "current_engineering_boundary_v01"
    ] = reclosure_manifest_boundary
    assert reverted_contract_manifest == reclosure_manifest
    reverted_contract_overlay = copy.deepcopy(overlay)
    reverted_contract_overlay["current_engineering_boundary"] = (
        reclosure_overlay_boundary
    )
    assert reverted_contract_overlay == reclosure_overlay

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
    changed_fields = {
        key
        for key in set(reclosure_manifest_boundary) | set(parent_manifest_boundary)
        if reclosure_manifest_boundary.get(key, missing)
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
    reverted_manifest = copy.deepcopy(reclosure_manifest)
    reverted_manifest["current_checkpoint_status"][
        "current_engineering_boundary_v01"
    ] = parent_manifest_boundary
    assert reverted_manifest == parent_manifest
    reverted_overlay = copy.deepcopy(reclosure_overlay)
    reverted_overlay["current_engineering_boundary"] = parent_overlay_boundary
    assert reverted_overlay == parent_overlay

    audit_manifest = json.loads(
        _git_show(G2D_AUDIT_COMMIT, "specs/machine_manifest_v0_25.json")
    )
    audit_overlay = json.loads(
        _git_show(G2D_AUDIT_COMMIT, "release/current_status_overlay_v01.json")
    )
    assert _revert_g2d_boundary_transition(
        reclosure_manifest,
        overlay=False,
    ) == audit_manifest
    assert _revert_g2d_boundary_transition(
        reclosure_overlay,
        overlay=True,
    ) == audit_overlay

def test_g2d_binding_and_implementation_bytes_remain_frozen() -> None:
    current_addendum = (
        REPOSITORY_ROOT / G2D_ACCEPTED_ADDENDUM_PATH
    ).read_bytes()
    assert _sha256_bytes(current_addendum) == G2D_V0310_ACCEPTED_ADDENDUM_SHA256
    v0310_marker = (
        b"===============================================================================\n"
        b"HISTORICAL ACCEPTED V0.3.9 CONTENT - EXACT REPOSITORY BYTES\n"
        b"===============================================================================\n"
        b"\n"
        b"The complete byte sequence below is the previously accepted cumulative\n"
        b"v0.3.9 addendum. It remains immutable historical contract and evidence context\n"
        b"for its exact bytes. Its embedded present-tense lifecycle statements do not\n"
        b"override the active v0.3.10 metadata and rulings above.\n"
        b"\n"
    )
    assert current_addendum.count(v0310_marker) == 1
    _, historical_v039 = current_addendum.split(v0310_marker, 1)
    assert _sha256_bytes(historical_v039) == G2D_V039_ACCEPTED_ADDENDUM_SHA256
    v039_marker = (
        b"===============================================================================\n"
        b"HISTORICAL ACCEPTED V0.3.8 CONTENT - EXACT REPOSITORY BYTES\n"
        b"===============================================================================\n"
        b"\n"
        b"The complete byte sequence below is the previously accepted v0.3.8 addendum.\n"
        b"It remains immutable historical contract and evidence context for v0.3.8. Its\n"
        b"embedded present-tense lifecycle statements do not override the active v0.3.9\n"
        b"metadata and clarification above.\n"
        b"\n"
    )
    assert historical_v039.count(v039_marker) == 1
    _, historical_v038 = historical_v039.split(v039_marker, 1)
    assert _sha256_bytes(historical_v038) == G2D_ACCEPTED_ADDENDUM_SHA256
    addendum = historical_v038
    assert _sha256_bytes(addendum) == G2D_ACCEPTED_ADDENDUM_SHA256
    historical_marker = (
        b"===============================================================================\n"
        b"HISTORICAL ACCEPTED V0.3.7 CONTENT - EXACT REPOSITORY BYTES\n"
        b"===============================================================================\n"
        b"\n"
        b"The complete byte sequence below is the previously accepted v0.3.7 addendum.\n"
        b"It remains immutable historical contract and evidence context for v0.3.7. Its\n"
        b"embedded present-tense lifecycle statements do not override the active v0.3.8\n"
        b"metadata and clarification above.\n"
        b"\n"
    )
    assert addendum.count(historical_marker) == 1
    _, historical_v037 = addendum.split(historical_marker, 1)
    assert _sha256_bytes(historical_v037) == G2D_V037_ACCEPTED_ADDENDUM_SHA256
    assert len(historical_v037) == 185220
    assert historical_v037.count(b"\n") == 3532
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
        G2D_V038_INDEPENDENT_REAUDIT_PATH: G2D_V038_INDEPENDENT_REAUDIT_SHA256,
        G2D_V038_CHECKPOINT_PATH: G2D_V038_CHECKPOINT_SHA256,
        G2D_V039_INDEPENDENT_REAUDIT_PATH: G2D_V039_INDEPENDENT_REAUDIT_SHA256,
        G2D_V039_CHECKPOINT_PATH: G2D_V039_CHECKPOINT_SHA256,
        **G2D_FROZEN_IMPLEMENTATION_SHA256,
        **G2E_CONTRACT_UPDATED_SHA256,
        **G2D_FACADE_MAINTENANCE_SHA256,
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
    assert (
        REPOSITORY_ROOT / G2D_V038_INDEPENDENT_REAUDIT_PATH
    ).read_bytes() == _git_show(
        G2D_V038_INDEPENDENT_REAUDIT_COMMIT,
        G2D_V038_INDEPENDENT_REAUDIT_PATH,
    )
    for path in G2D_FROZEN_IMPLEMENTATION_SHA256:
        assert (REPOSITORY_ROOT / path).read_bytes() == _git_show(
            G2D_CORRECTED_IMPLEMENTATION_COMMIT,
            path,
        ), path

    facade_commit_row = subprocess.run(
        (
            "git",
            "show",
            "-s",
            "--format=%H%x1f%P%x1f%s",
            G2D_FACADE_MAINTENANCE_COMMIT,
        ),
        cwd=REPOSITORY_ROOT,
        check=True,
        capture_output=True,
        text=True,
    ).stdout.strip()
    facade_commit, facade_parent, facade_subject = facade_commit_row.split(
        "\x1f",
        2,
    )
    assert facade_commit == G2D_FACADE_MAINTENANCE_COMMIT
    assert facade_parent == G2D_FACADE_MAINTENANCE_PARENT
    assert facade_subject == G2D_FACADE_MAINTENANCE_SUBJECT
    facade_paths = tuple(
        subprocess.run(
            (
                "git",
                "diff-tree",
                "--no-commit-id",
                "--name-only",
                "-r",
                G2D_FACADE_MAINTENANCE_COMMIT,
            ),
            cwd=REPOSITORY_ROOT,
            check=True,
            capture_output=True,
            text=True,
        ).stdout.splitlines()
    )
    assert facade_paths == tuple(sorted(G2D_FACADE_MAINTENANCE_SHA256))
    for path, expected_sha256 in G2D_FACADE_MAINTENANCE_PREIMAGE_SHA256.items():
        assert _sha256_bytes(
            _git_show(G2D_FACADE_MAINTENANCE_PARENT, path)
        ) == expected_sha256, path
    for path, expected_sha256 in G2D_FACADE_MAINTENANCE_SHA256.items():
        current = (REPOSITORY_ROOT / path).read_bytes()
        assert _sha256_bytes(current) == expected_sha256, path
        assert current == _git_show(G2D_FACADE_MAINTENANCE_COMMIT, path), path

    g2c_facade_commit_row = subprocess.run(
        (
            "git",
            "show",
            "-s",
            "--format=%H%x1f%P%x1f%s",
            G2D_G2C_FACADE_CONSUMER_MAINTENANCE_COMMIT,
        ),
        cwd=REPOSITORY_ROOT,
        check=True,
        capture_output=True,
        text=True,
    ).stdout.strip()
    g2c_commit, g2c_parent, g2c_subject = g2c_facade_commit_row.split(
        "\x1f",
        2,
    )
    assert g2c_commit == G2D_G2C_FACADE_CONSUMER_MAINTENANCE_COMMIT
    assert g2c_parent == G2D_G2C_FACADE_CONSUMER_MAINTENANCE_PARENT
    assert g2c_subject == G2D_G2C_FACADE_CONSUMER_MAINTENANCE_SUBJECT
    g2c_paths = tuple(
        subprocess.run(
            (
                "git",
                "diff-tree",
                "--no-commit-id",
                "--name-only",
                "-r",
                G2D_G2C_FACADE_CONSUMER_MAINTENANCE_COMMIT,
            ),
            cwd=REPOSITORY_ROOT,
            check=True,
            capture_output=True,
            text=True,
        ).stdout.splitlines()
    )
    g2c_path = "tests/test_execution_mode_router_g2_c_v01.py"
    assert g2c_paths == (g2c_path,)
    assert _sha256_bytes(
        _git_show(G2D_G2C_FACADE_CONSUMER_MAINTENANCE_PARENT, g2c_path)
    ) == G2D_G2C_FACADE_CONSUMER_PREIMAGE_SHA256
    current_g2c = (REPOSITORY_ROOT / g2c_path).read_bytes()
    assert _sha256_bytes(current_g2c) == G2D_G2C_FACADE_CONSUMER_SHA256
    assert current_g2c == _git_show(
        G2D_G2C_FACADE_CONSUMER_MAINTENANCE_COMMIT,
        g2c_path,
    )

    transition_facade_commit_row = subprocess.run(
        (
            "git",
            "show",
            "-s",
            "--format=%H%x1f%P%x1f%s",
            G2D_TRANSITION_FACADE_CONSUMER_MAINTENANCE_COMMIT,
        ),
        cwd=REPOSITORY_ROOT,
        check=True,
        capture_output=True,
        text=True,
    ).stdout.strip()
    transition_commit, transition_parent, transition_subject = (
        transition_facade_commit_row.split("\x1f", 2)
    )
    assert transition_commit == G2D_TRANSITION_FACADE_CONSUMER_MAINTENANCE_COMMIT
    assert transition_parent == G2D_TRANSITION_FACADE_CONSUMER_MAINTENANCE_PARENT
    assert transition_subject == G2D_TRANSITION_FACADE_CONSUMER_MAINTENANCE_SUBJECT
    transition_paths = tuple(
        subprocess.run(
            (
                "git",
                "diff-tree",
                "--no-commit-id",
                "--name-only",
                "-r",
                G2D_TRANSITION_FACADE_CONSUMER_MAINTENANCE_COMMIT,
            ),
            cwd=REPOSITORY_ROOT,
            check=True,
            capture_output=True,
            text=True,
        ).stdout.splitlines()
    )
    transition_path = "tests/test_transition_registry_v01.py"
    assert transition_paths == (transition_path,)
    assert _sha256_bytes(
        _git_show(
            G2D_TRANSITION_FACADE_CONSUMER_MAINTENANCE_PARENT,
            transition_path,
        )
    ) == G2D_TRANSITION_FACADE_CONSUMER_PREIMAGE_SHA256
    current_transition = (REPOSITORY_ROOT / transition_path).read_bytes()
    assert _sha256_bytes(current_transition) == G2D_TRANSITION_FACADE_CONSUMER_SHA256
    assert current_transition == _git_show(
        G2D_TRANSITION_FACADE_CONSUMER_MAINTENANCE_COMMIT,
        transition_path,
    )

    runtime_path = "hedgehog/kernel/fractal_runtime_v02.py"
    test_path = "tests/test_fractal_runtime_g2_d_v02.py"
    assert _sha256_bytes(
        _git_show(G2D_V039_CONTRACT_COMMIT, runtime_path)
    ) == G2D_V038_RUNTIME_SHA256
    assert _sha256_bytes(
        _git_show(G2D_V039_CONTRACT_COMMIT, test_path)
    ) == G2D_V039_CONTRACT_TEST_SHA256
    assert _sha256_bytes(
        _git_show(G2D_V039_BASIS, test_path)
    ) == G2D_V038_TEST_SHA256

    current_runtime = (REPOSITORY_ROOT / runtime_path).read_bytes()
    current_test = (REPOSITORY_ROOT / test_path).read_bytes()
    current_runtime_sha256 = _sha256_bytes(current_runtime)
    current_test_sha256 = _sha256_bytes(current_test)
    lifecycle_state, lifecycle_head, contract_commit, maintenance_commit = (
        _g2d_v0310_lifecycle_state_v01()
    )
    preimplementation_states = {
        "PRE_CONTRACT_DIRTY",
        "POST_CONTRACT_PRE_MAINTENANCE_CLEAN",
        "MAINTENANCE_CANDIDATE_DIRTY",
        "POST_MAINTENANCE_CLEAN",
    }
    implementation_states = {
        "IMPLEMENTATION_CANDIDATE_DIRTY",
        "POST_IMPLEMENTATION_CLEAN",
    }
    assert lifecycle_state in preimplementation_states | implementation_states
    if lifecycle_state in preimplementation_states:
        assert current_runtime_sha256 == G2D_V039_IMPLEMENTATION_RUNTIME_SHA256
        assert current_test_sha256 == G2D_V0310_CONTRACT_TEST_SHA256
        assert current_runtime == _git_show(
            G2D_V039_IMPLEMENTATION_COMMIT,
            runtime_path,
        )
    else:
        assert current_runtime_sha256 == G2D_V0310_IMPLEMENTATION_RUNTIME_SHA256
        assert current_test_sha256 == G2D_V0310_IMPLEMENTATION_TEST_SHA256
        assert len(current_runtime) == G2D_V0310_IMPLEMENTATION_RUNTIME_BYTES
        assert current_runtime.count(b"\n") == G2D_V0310_IMPLEMENTATION_RUNTIME_LF
        assert len(current_test) == G2D_V0310_IMPLEMENTATION_TEST_BYTES
        assert current_test.count(b"\n") == G2D_V0310_IMPLEMENTATION_TEST_LF
        assert contract_commit is not None
        assert maintenance_commit is not None
    historical_v039_test = _git_show(G2D_V0310_BASIS, test_path)
    assert _sha256_bytes(historical_v039_test) == G2D_V039_IMPLEMENTATION_TEST_SHA256
    assert current_test != historical_v039_test

    for commit, parent, subject, paths in (
        (
            G2D_V039_CONTRACT_COMMIT,
            G2D_V039_BASIS,
            G2D_V039_CONTRACT_SUBJECT,
            G2D_V039_CONTRACT_PATHS,
        ),
        (
            G2D_V039_RELEASE_CONSUMER_MAINTENANCE_COMMIT,
            G2D_V039_CONTRACT_COMMIT,
            G2D_V039_RELEASE_CONSUMER_MAINTENANCE_SUBJECT,
            ("tests/test_repository_release_spine_v01.py",),
        ),
        (
            G2D_V039_IMPLEMENTATION_COMMIT,
            G2D_V039_IMPLEMENTATION_PARENT,
            G2D_V039_IMPLEMENTATION_SUBJECT,
            G2D_V039_IMPLEMENTATION_PATHS,
        ),
        (
            G2D_V039_LIFECYCLE_SYNC_COMMIT,
            G2D_V039_IMPLEMENTATION_COMMIT,
            G2D_V039_LIFECYCLE_SYNC_SUBJECT,
            G2D_V039_LIFECYCLE_SYNC_PATHS,
        ),
        (
            G2D_V039_INDEPENDENT_REAUDIT_COMMIT,
            G2D_V039_LIFECYCLE_SYNC_COMMIT,
            G2D_V039_INDEPENDENT_REAUDIT_SUBJECT,
            (G2D_V039_INDEPENDENT_REAUDIT_PATH,),
        ),
    ):
        row = subprocess.run(
            ("git", "show", "-s", "--format=%H%x1f%P%x1f%s", commit),
            cwd=REPOSITORY_ROOT,
            check=True,
            capture_output=True,
            text=True,
        ).stdout.strip()
        observed_commit, observed_parent, observed_subject = row.split("\x1f", 2)
        assert observed_commit == commit
        assert observed_parent == parent
        assert observed_subject == subject
        changed_paths = subprocess.run(
            ("git", "diff", "--name-only", parent, commit),
            cwd=REPOSITORY_ROOT,
            check=True,
            capture_output=True,
            text=True,
        ).stdout.splitlines()
        assert tuple(changed_paths) == tuple(sorted(paths))

    implementation_patch = subprocess.run(
        (
            "git",
            "diff",
            "--no-ext-diff",
            "--full-index",
            "--binary",
            G2D_V039_IMPLEMENTATION_PARENT,
            G2D_V039_IMPLEMENTATION_COMMIT,
        ),
        cwd=REPOSITORY_ROOT,
        check=True,
        capture_output=True,
    ).stdout
    assert _sha256_bytes(implementation_patch) == (
        G2D_V039_IMPLEMENTATION_PATCH_SHA256
    )
    assert len(implementation_patch) == G2D_V039_IMPLEMENTATION_PATCH_BYTES
    assert implementation_patch.count(b"\n") == G2D_V039_IMPLEMENTATION_PATCH_LF

    if lifecycle_state == "PRE_CONTRACT_DIRTY":
        assert lifecycle_head == G2D_V0310_BASIS
        assert contract_commit is None
        assert maintenance_commit is None
    elif lifecycle_state == "POST_CONTRACT_PRE_MAINTENANCE_CLEAN":
        assert lifecycle_head == contract_commit
        assert maintenance_commit is None
    elif lifecycle_state == "MAINTENANCE_CANDIDATE_DIRTY":
        assert lifecycle_head == contract_commit
        assert maintenance_commit is None
    elif lifecycle_state in {
        "POST_MAINTENANCE_CLEAN",
        "IMPLEMENTATION_CANDIDATE_DIRTY",
    }:
        assert lifecycle_head == maintenance_commit
    else:
        assert lifecycle_state == "POST_IMPLEMENTATION_CLEAN"
        assert lifecycle_head not in {G2D_V0310_BASIS, contract_commit, maintenance_commit}

    current_test_source = current_test.decode("ascii")
    assert len(re.findall(r"(?m)^def test_", current_test_source)) == 83
    assert current_test_source.count(
        "def test_d3_post_acceptance_contract_addendum_v0310_accepted"
    ) == 1
    assert "def test_d3_post_acceptance_contract_addendum_v039_accepted" not in (
        current_test_source
    )
    assert "def test_d3_post_acceptance_contract_addendum_v038_accepted" not in (
        current_test_source
    )
    assert current_runtime != _git_show(
        G2D_CORRECTED_IMPLEMENTATION_COMMIT,
        runtime_path,
    )
    for path, sha256 in G2D_HISTORICAL_G2E_DEPENDENCY_SHA256.items():
        historical_raw = _git_show(G2D_CORRECTED_IMPLEMENTATION_COMMIT, path)
        assert _sha256_bytes(historical_raw) == sha256, path
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
    successor_phase, _, _, _ = _g2d_v0310_successor_state_v01()
    expected_successor_phases = {
        'post_i_sync': {'SYNC_CANDIDATE_DIRTY', 'POST_SYNC_CLEAN', 'AUDIT_CANDIDATE_DIRTY', 'POST_AUDIT_CLEAN'},
        'reclosure': {'RECLOSURE_CANDIDATE_DIRTY', 'POST_RECLOSURE_CLEAN', 'E4_CODE_CANDIDATE_DIRTY', 'POST_E4_CLEAN'},
        'final_e4_sync': {
            'FINAL_E4_SYNC_CANDIDATE_DIRTY',
            'POST_FINAL_E4_SYNC_CLEAN',
            'POST_FINAL_E4_SYNC_SUCCESSOR',
        },
    }
    assert successor_phase in expected_successor_phases[G2D_V0310_EXPECTED_SUCCESSOR_PHASE]
    addendum = (
        REPOSITORY_ROOT / G2D_ACCEPTED_ADDENDUM_PATH
    ).read_text(encoding="ascii")
    contract_scope = addendum.split(
        "This contract-only candidate modifies exactly these ten", 1
    )[1].split("The active contract-only lifecycle is exact:", 1)[0]
    offsets = tuple(
        contract_scope.index("`" + path + "`") for path in G2D_V0310_CONTRACT_PATHS
    )
    assert offsets == tuple(sorted(offsets))
    future_scope = addendum.split(
        "A later separately owner-authorized implementation may modify exactly:", 1
    )[1].split("No public type", 1)[0]
    assert future_scope.count("`hedgehog/kernel/fractal_runtime_v02.py`") == 1
    assert future_scope.count("`tests/test_fractal_runtime_g2_d_v02.py`") == 1
    operational = addendum.split(
        "The operational order is exact:", 1
    )[1].split("No stash, reset, restore", 1)[0]
    assert operational.index("separate explicit owner authorization") < (
        operational.index("narrow G2-D runtime")
    )
    assert operational.index(
        "commit only `tests/test_repository_release_spine_v01.py`"
    ) < operational.index("separate explicit owner authorization")
    assert operational.index("v0.3.10 successor checkpoint") < (
        operational.index("fresh unchanged G2-E3 V06")
    )
    assert operational.index("fresh unchanged G2-E3 V06") < (
        operational.index("resume the parked dirty G2-E4 candidate")
    )
    assert "E4_PAIR_CALL_ACCOUNTING=2/2" in addendum
    assert "E4_FOCUSED_CALL_ACCOUNTING=2/2" in addendum
    assert "E4_COMPLETE_FILE_CALL_ACCOUNTING=3/3" in addendum
    assert "+ exactly four explicit public revise evaluations" in addendum
    assert "+ zero nested public revise evaluations" in addendum
    addendum_normalized = " ".join(addendum.split())
    assert "explicit `NOT_FROZEN`/zero placeholders" in addendum_normalized
    assert "directly on top of that primary dirt is forbidden" in (
        addendum_normalized
    )
    head = subprocess.run(
        ("git", "rev-parse", "HEAD"),
        cwd=REPOSITORY_ROOT,
        check=True,
        capture_output=True,
        text=True,
    ).stdout.strip()
    status = subprocess.run(
        ("git", "status", "--short", "--untracked-files=all"),
        cwd=REPOSITORY_ROOT,
        check=True,
        capture_output=True,
        text=True,
    ).stdout.splitlines()
    staged = subprocess.run(
        ("git", "diff", "--cached", "--name-only"),
        cwd=REPOSITORY_ROOT,
        check=True,
        capture_output=True,
        text=True,
    ).stdout.splitlines()
    assert set(staged).isdisjoint(_g2d_v0310_protected_paths_v01())
    exact_reclosure_status = [
        " M " + path
        for path in G2D_V039_RECLOSURE_PATHS
        if path != G2D_V039_CHECKPOINT_PATH
    ] + ["?? " + G2D_V039_CHECKPOINT_PATH]
    lifecycle_state, lifecycle_head, contract_commit, maintenance_commit = (
        _g2d_v0310_lifecycle_state_v01()
    )
    assert lifecycle_state in {
        "PRE_CONTRACT_DIRTY",
        "POST_CONTRACT_PRE_MAINTENANCE_CLEAN",
        "MAINTENANCE_CANDIDATE_DIRTY",
        "POST_MAINTENANCE_CLEAN",
        "IMPLEMENTATION_CANDIDATE_DIRTY",
        "POST_IMPLEMENTATION_CLEAN",
        "SYNC_CANDIDATE_DIRTY",
        "POST_SYNC_CLEAN",
        "AUDIT_CANDIDATE_DIRTY",
        "POST_AUDIT_CLEAN",
        "RECLOSURE_CANDIDATE_DIRTY",
        "POST_RECLOSURE_CLEAN",
        "E4_CODE_CANDIDATE_DIRTY",
        "POST_E4_CLEAN",
        "FINAL_E4_SYNC_CANDIDATE_DIRTY",
        "POST_FINAL_E4_SYNC_CLEAN",
        "POST_FINAL_E4_SYNC_SUCCESSOR",
    }
    assert head == lifecycle_head
    if lifecycle_state == "PRE_CONTRACT_DIRTY":
        assert contract_commit is None
        assert maintenance_commit is None
    elif lifecycle_state in {
        "POST_CONTRACT_PRE_MAINTENANCE_CLEAN",
        "MAINTENANCE_CANDIDATE_DIRTY",
    }:
        assert contract_commit is not None
        assert maintenance_commit is None
    else:
        assert contract_commit is not None
        assert maintenance_commit is not None
    assert _current_boundary()["g2d_v0310_contract_hop_completed"] is True
    assert _current_boundary()["g2d_v0310_implementation_authorized"] == G2D_V0310_SUCCESSOR_EXPECTED_FIELDS['g2d_v0310_implementation_authorized']
    assert _current_boundary()["g2d_v0310_implementation_started"] == G2D_V0310_SUCCESSOR_EXPECTED_FIELDS['g2d_v0310_implementation_started']
    assert _current_boundary()["g2d_v0310_corrected_implementation_exists"] == G2D_V0310_SUCCESSOR_EXPECTED_FIELDS['g2d_v0310_corrected_implementation_exists']
    assert _current_boundary()["g2d_independent_reaudit_passed"] == G2D_V0310_SUCCESSOR_EXPECTED_FIELDS['g2d_independent_reaudit_passed']
    assert _current_boundary()["g2d_independent_reaudit_commit"] == G2D_V0310_SUCCESSOR_EXPECTED_FIELDS['g2d_independent_reaudit_commit']
    assert _current_boundary()["g2d_additive_reclosure_completed"] == G2D_V0310_SUCCESSOR_EXPECTED_FIELDS['g2d_additive_reclosure_completed']
    assert _current_boundary()["g2d_corrected_closure_claimed"] == G2D_V0310_SUCCESSOR_EXPECTED_FIELDS['g2d_corrected_closure_claimed']

    v039_checkpoint = (REPOSITORY_ROOT / G2D_V039_CHECKPOINT_PATH).read_text(
        encoding="ascii"
    )
    v039_scope = v039_checkpoint.split(
        "## 7. Exact Additive Reclosure Path Scope", 1
    )[1].split(
        "## 8. Historical Evidence and Preserved Nonclaims",
        1,
    )[0]
    assert tuple(
        match.group(1)
        for match in re.finditer(r"^\d+\. `([^`]+)`", v039_scope, re.MULTILINE)
    ) == G2D_V039_RECLOSURE_PATHS
    assert "closure_commit_identity: NOT_SELF_RECORDED" in v039_checkpoint
    assert G2D_V039_INDEPENDENT_REAUDIT_COMMIT not in v039_checkpoint.split(
        "independent_reaudit_commit:", 1
    )[0]

    v039_candidates = []
    for line in subprocess.run(
        ("git", "log", "--all", "--format=%H%x1f%P%x1f%s"),
        cwd=REPOSITORY_ROOT,
        check=True,
        capture_output=True,
        text=True,
    ).stdout.splitlines():
        commit, parents, observed_subject = line.split("\x1f", 2)
        if observed_subject == G2D_V039_CLOSURE_SUBJECT:
            v039_candidates.append((commit, tuple(parents.split())))
    if not v039_candidates:
        assert head == G2D_V039_INDEPENDENT_REAUDIT_COMMIT
        assert status == exact_reclosure_status
    else:
        assert len(v039_candidates) == 1
        v039_closure_commit, v039_parents = v039_candidates[0]
        assert v039_parents == (G2D_V039_INDEPENDENT_REAUDIT_COMMIT,)
        assert v039_closure_commit not in v039_checkpoint
        changed = subprocess.run(
            (
                "git",
                "diff-tree",
                "--no-commit-id",
                "--name-status",
                "-r",
                "--no-renames",
                G2D_V039_INDEPENDENT_REAUDIT_COMMIT,
                v039_closure_commit,
            ),
            cwd=REPOSITORY_ROOT,
            check=True,
            capture_output=True,
            text=True,
        ).stdout.splitlines()
        observed = {
            path: path_status
            for path_status, path in (line.split("\t", 1) for line in changed)
        }
        assert tuple(sorted(observed)) == tuple(sorted(G2D_V039_RECLOSURE_PATHS))
        assert observed[G2D_V039_CHECKPOINT_PATH] == "A"
        assert tuple(observed.values()).count("A") == 1
        assert tuple(observed.values()).count("M") == 8

    v038_checkpoint = (REPOSITORY_ROOT / G2D_V038_CHECKPOINT_PATH).read_text(
        encoding="utf-8"
    )
    v038_scope = v038_checkpoint.split(
        "## 7. Exact Additive Reclosure Path Scope", 1
    )[1].split(
        "## 8. Historical Evidence and Preserved Nonclaims",
        1,
    )[0]
    assert tuple(
        match.group(1)
        for match in re.finditer(r"^\d+\. `([^`]+)`", v038_scope, re.MULTILINE)
    ) == G2D_V038_CLOSURE_PATHS
    assert "closure_commit_identity: NOT_SELF_RECORDED" in v038_checkpoint

    v038_history = subprocess.run(
        ("git", "log", "--all", "--format=%H%x1f%P%x1f%s"),
        cwd=REPOSITORY_ROOT,
        check=True,
        capture_output=True,
        text=True,
    ).stdout.splitlines()
    v038_candidates = []
    for line in v038_history:
        commit, parents, subject = line.split("\x1f", 2)
        if subject == G2D_V038_CLOSURE_SUBJECT:
            v038_candidates.append((commit, tuple(parents.split())))
    if not v038_candidates:
        head = subprocess.run(
            ("git", "rev-parse", "HEAD"),
            cwd=REPOSITORY_ROOT,
            check=True,
            capture_output=True,
            text=True,
        ).stdout.strip()
        assert head == G2D_V038_CLOSURE_PARENT
        status = subprocess.run(
            ("git", "status", "--porcelain=v1", "--untracked-files=all"),
            cwd=REPOSITORY_ROOT,
            check=True,
            capture_output=True,
            text=True,
        ).stdout.splitlines()
        assert set(status) == {
            f" M {path}"
            for path in G2D_V038_CLOSURE_PATHS
            if path != G2D_V038_CHECKPOINT_PATH
        } | {f"?? {G2D_V038_CHECKPOINT_PATH}"}
        assert subprocess.run(
            ("git", "diff", "--cached", "--name-only"),
            cwd=REPOSITORY_ROOT,
            check=True,
            capture_output=True,
        ).stdout == b""
    else:
        assert len(v038_candidates) == 1
        v038_closure_commit, v038_parents = v038_candidates[0]
        assert v038_parents == (G2D_V038_CLOSURE_PARENT,)
        assert v038_closure_commit not in v038_checkpoint
        changed = subprocess.run(
            (
                "git",
                "diff-tree",
                "--no-commit-id",
                "--name-status",
                "-r",
                "--no-renames",
                G2D_V038_CLOSURE_PARENT,
                v038_closure_commit,
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
        assert tuple(sorted(observed)) == tuple(sorted(G2D_V038_CLOSURE_PATHS))
        assert observed[G2D_V038_CHECKPOINT_PATH] == "A"
        assert tuple(observed.values()).count("A") == 1
        assert tuple(observed.values()).count("M") == 8

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

    head = subprocess.run(
        ("git", "rev-parse", "HEAD"),
        cwd=REPOSITORY_ROOT,
        check=True,
        capture_output=True,
        text=True,
    ).stdout.strip()
    if head == G2D_V038_IMPLEMENTATION_BASIS:
        status = subprocess.run(
            ("git", "status", "--porcelain=v1", "--untracked-files=all"),
            cwd=REPOSITORY_ROOT,
            check=True,
            capture_output=True,
            text=True,
        ).stdout.splitlines()
        assert set(status) == {
            f" M {path}" for path in G2D_V038_IMPLEMENTATION_PATHS
        }
        assert subprocess.run(
            ("git", "diff", "--cached", "--name-only"),
            cwd=REPOSITORY_ROOT,
            check=True,
            capture_output=True,
        ).stdout == b""
        return

    parent = subprocess.run(
        ("git", "rev-parse", f"{G2D_V038_IMPLEMENTATION_COMMIT}^"),
        cwd=REPOSITORY_ROOT,
        check=True,
        capture_output=True,
        text=True,
    ).stdout.strip()
    assert parent == G2D_V038_IMPLEMENTATION_BASIS
    rows = subprocess.run(
        (
            "git",
            "diff-tree",
            "--no-commit-id",
            "--name-status",
            "-r",
            "--no-renames",
            G2D_V038_IMPLEMENTATION_BASIS,
            G2D_V038_IMPLEMENTATION_COMMIT,
        ),
        cwd=REPOSITORY_ROOT,
        check=True,
        capture_output=True,
        text=True,
    ).stdout.splitlines()
    candidate = {
        path: status
        for status, path in (line.split("\t", 1) for line in rows)
    }
    assert set(candidate) == set(G2D_V038_IMPLEMENTATION_PATHS)
    assert set(candidate.values()) == {"M"}
    committed_patch = subprocess.run(
        (
            "git",
            "diff",
            "--no-ext-diff",
            "--full-index",
            "--binary",
            G2D_V038_IMPLEMENTATION_BASIS,
            G2D_V038_IMPLEMENTATION_COMMIT,
        ),
        cwd=REPOSITORY_ROOT,
        check=True,
        capture_output=True,
    ).stdout
    assert _sha256_bytes(committed_patch) == G2D_V038_IMPLEMENTATION_PATCH_SHA256
    assert subprocess.run(
        (
            "git",
            "merge-base",
            "--is-ancestor",
            G2D_V038_IMPLEMENTATION_COMMIT,
            head,
        ),
        cwd=REPOSITORY_ROOT,
        check=False,
        capture_output=True,
    ).returncode == 0

def test_quantum_roadmap_identity_metadata_and_amendment_are_exact() -> None:
    assert ROADMAP_PATH.is_file()
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
    assert raw == _git_show(
        "HEAD", ROADMAP_PATH.relative_to(REPOSITORY_ROOT).as_posix()
    )
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
    roadmap_path = ROADMAP_PATH.relative_to(REPOSITORY_ROOT).as_posix()
    expected_reference = {
        "path": roadmap_path,
        "status": "future_reference_non_current",
        "current_authority": False,
        "onboarding_allowed": False,
        "authority_scope": "future_research_reference_only",
        "may_override_architecture_lock": False,
        "role": (
            "Future mathematical extension roadmap; not current runtime, Gate "
            "contract, implementation, completion claim, or architecture authority."
        ),
    }
    authority_index = _read_json(
        REPOSITORY_ROOT / "specs/document_authority_index_v01.json"
    )
    assert authority_index["future_reference_documents"] == [expected_reference]
    for category in (
        "current_normative_documents",
        "current_operational_documents",
        "current_technical_annexes",
        "audit_only_sources",
    ):
        assert roadmap_path not in {
            entry["path"] for entry in authority_index[category]
        }
    assert roadmap_path not in authority_index["source_of_truth_order"]
    assert roadmap_path in authority_index["excluded_from_successor_onboarding"]

    successor_context = _read_json(
        REPOSITORY_ROOT / "release/successor_context_manifest_v01.json"
    )
    for category in (
        "always_include",
        "include_current_gate_sources",
        "include_current_gate_tests",
        "include_current_release_sources",
        "authority_documents",
    ):
        assert roadmap_path not in successor_context[category]
    assert "specs/future/**" in successor_context["exclude_globs"]

    roadmap = ROADMAP_PATH.read_text(encoding="utf-8")
    metadata = roadmap.split("```text\n", 1)[1].split("\n```", 1)[0]
    for nonclaim in (
        "document_status: FUTURE_POST_GATE6_ENGINEERING_DESIGN",
        "current_release_claim: false",
        "normative_for_current_gate_1_to_gate_6_runtime: false",
        "changes_current_six_gate_strategy: NO",
        "quantum_advantage_claimed: NO",
    ):
        assert metadata.splitlines().count(nonclaim) == 1

    limitations = LIMITATIONS_PATH.read_text(encoding="utf-8")
    notes = NOTES_PATH.read_text(encoding="utf-8")
    assert limitations.count(QUANTUM_LIMITATION) == 1
    assert notes.count(QUANTUM_ENGINEERING_NOTE) == 1
    note_line = next(
        line for line in notes.splitlines() if line == QUANTUM_ENGINEERING_NOTE
    )
    assert "published" not in note_line.lower()
    assert "publicly released" not in note_line.lower()

    current_claim_surfaces = "\n".join(
        (
            README_PATH.read_text(encoding="utf-8"),
            AGENTS_PATH.read_text(encoding="utf-8"),
            json.dumps(_read_json(OVERLAY_PATH), sort_keys=True),
        )
    )
    for forbidden_current_claim in (
        "The Quantum-Inspired Mathematical Extension is implemented",
        "Quantum AVF is implemented",
        "physical quantum-state result is implemented",
        "quantum advantage is claimed",
    ):
        assert forbidden_current_claim not in current_claim_surfaces

    assert REPOSITORY_RELEASE_SPINE_TEST_MODIFIED is True
    assert OTHER_TESTS_MODIFIED is False
    assert RUNTIME_TESTS_MODIFIED is False
