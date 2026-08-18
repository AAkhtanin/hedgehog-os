# G2-D v0.3.8 Proof-Based Whole-Run Correction Checkpoint

## 1. Metadata and Closure Boundary

document_status: CHECKPOINT
checkpoint_id: fractal_runtime_v0_2_g2_d_proof_based_whole_run_correction_v01
checkpoint_version: v0.1
gate_id: gate2_g2d_fractal_runtime_v0_2_v038_correction
gate_slice: G2-D
corrected_g2d_status: CLOSED_PASS
closure_commit_identity: NOT_SELF_RECORDED
closure_commit_subject: Close G2-D v0.3.8 proof-based whole-run correction
accepted_v038_addendum_sha256: 09db4ff2224e59c878b967ba634084d72cd01b36f86edfa5fca2e9750e976ea6
historical_v037_addendum_sha256: 29983cd17cbefe306de32cf045827fc927280bae5fdb0d7c9db50203a0ea6511
corrected_implementation_commit: 3d9cc2aac45d2923a9d9d5848a8f4f81d011b22e
corrected_implementation_parent_commit: a2d04e03d2b3b1b2b0beeaf407234ae091ae8eb7
corrected_implementation_patch_sha256: dbb5e3010e3337b5da0a36cfb69f9597a090be6d14b256699945c5a6fb09c291
post_implementation_lifecycle_sync_commit: e66c8be08e753077b6a99eeb635bf6fe25ee4b90
independent_reaudit_commit: edfa42198efa1d03097570d30b6364af1b567050
independent_reaudit_path: docs/audit_reports/auditor_fractal_runtime_g2_d_v038_proof_based_whole_run_correction_v01.log
independent_reaudit_sha256: acd62cfcf3753a4c02c5f5187e64e8940cf3b3420f97850b0426583465996d67
owner_evidence_bundle_sha256: 51e913b59a8a82ea3fc5b7688f02dc07e4d9bf15d487d23d879d0b30f6b938f6
independent_reaudit_evidence_bundle_sha256: 5e43b38b921f7035609e5ef3a33058325c4b529193ad82d87b70a84cd6ff363b

The future reclosure commit cannot record its own commit identity without
making its content and therefore its identity self-referential. The accepted
repository placeholder law therefore requires `NOT_SELF_RECORDED`; the exact
subject, parent, and nine-path scope remain independently testable before and
after the owner creates that commit.

This checkpoint records additive reclosure evidence only. It is not Root, a
permission, an execution instruction, a successor baseline, a public release,
or Gate-2 closure.

## 2. Corrected Committed Basis

The accepted v0.3.8 clarification is revision `v0.3.8` of
`docs/fractal_runtime_v0_2_g2_d_post_acceptance_contract_addendum_v01.md`.
It preserves the controlling DESIGN_V03 semantics and records:

- `V037_IMPLEMENTATION_NONCONFORMANCE=YES`.
- `V038_CONTRACT_SEMANTICS_CHANGED=NO`.
- `V038_ROLE=EXPLICIT_CLARIFICATION_AND_LIFECYCLE_REOPENING`.

The corrected implementation commit is
`3d9cc2aac45d2923a9d9d5848a8f4f81d011b22e`, with parent
`a2d04e03d2b3b1b2b0beeaf407234ae091ae8eb7`. Its full-index patch SHA-256 is
`dbb5e3010e3337b5da0a36cfb69f9597a090be6d14b256699945c5a6fb09c291`.
The post-implementation lifecycle synchronization commit is
`e66c8be08e753077b6a99eeb635bf6fe25ee4b90`. The independent re-audit commit
is `edfa42198efa1d03097570d30b6364af1b567050`.

The implementation preserves the proof-based full-closure branch with
`AFFECTED_CLOSURE_EQUALS_ALL_RECOMPUTABLE_WORK` and Python/JSON null policy.
The accepted named-policy inventory remains empty. The historical context-None
and strict selective paths remain preserved.

## 3. Authority and Ownership Boundary

- Root remains the only final authority.
- G2-C owns the accepted Root-reviewed route.
- G2-D owns `RuntimeExecutionTopology` and stable topology-node and cell IDs.
- `RuntimeObservedWorkContextV02`, bindings, reports, traces, hashes, tests,
  execution evidence, and this checkpoint are evidence only.
- Post V&V validates and GT advises; neither decides.
- G2-D imports no G2-E module or type.
- PlanGraph remains historical proof-donor material and is not G2-D ownership.
- No successor baseline, permission, `ActionCommitPacket`, receipt,
  `FinalOutput`, DRS write, provider/model/network/connector operation,
  external-DRS operation, or real-world effect is created or authorized.

## 4. Corrected Geometry and Public Surface

- Public dataclass types: `21`.
- Serialized types: `18`.
- Runtime-only types: `3`.
- Schema definitions: `18`.
- Canonical-module public functions: `116`.
- Transition-profile public functions: `6`.
- Total G2-D public functions: `122`.
- Canonical module `__all__`: `137`.
- Direct package G2-D attributes: `143`.
- Package `__all__`: `19`.
- Validation targets: `35`.
- Failure stages: `30`.
- Public reason codes: `220`.
- Transition rules: `17`.
- `FractalRuntimeExecutionBundleV02` fields: `28`.
- G2-D test functions/items: `83/92`.
- Transition test functions/items: `60/268`.
- D5 cases/split/accepted runs: `72/36-36/10`.

No public type, function, schema definition, reason, target, stage, Transition
rule, facade export, authority field, or effect field was added by reclosure.

## 5. Accepted Execution Evidence

- Transition facade consumer focused: 1/1 PASS, calls 0/0.
  Log SHA-256: `d3b2b8789f1490422537a28d3616807aec8acdcef817732d6e4d54300e6c0eeb`.
- Complete Transition: 268/268 PASS, calls 0/0.
  Log SHA-256: `435037a91f85783963d9c565f8b1eba546ab2318ff7e30baa51be18aca8beaff`.
- Focused G2-D/Transition: 43/43 PASS, calls 3/3.
  Log SHA-256: `e74cbf5dde1c21d2750c372d838e3e56f0dbbfead5b1e1a629a228d4cf0f1e47`.
- Complete G2-C: 392/392 PASS, calls 0/0.
  Log SHA-256: `e6d651c909f34251da873531838978588842a2b5f3bc158682e3c6089427a349`.
- Release plus maintenance: 23/23 PASS, calls 0/0.
  Log SHA-256: `5a4e4d6b9877d9e93195bb6715e8c83418631dd45f1cab0fedd91dee8502528e`.
- Shared compatibility: 64/64 PASS, calls 0/0.
  Log SHA-256: `9049eb8ac32894f743746cecab93e9045d23a4bb25314021bd1952a17b4437d7`.
- Complete G2-D plus Transition: 360/360 PASS, calls 30/30.
  Log SHA-256: `9ec46d157b5382ebee757035fdb6540389f640ab7df99421cb5de83e41e0d2b8`.
- D5 child 1: PASS.
- D5 child 2: PASS.
- D5 cases per process: 72.
- D5 split per process: 36/36.
- D5 accepted bundles per process: 10.
- D5 public calls per process: 27/27.
- D5 rendered SHA-256:
  `ec05a8cf9377953abdf84b8a45af07afa3615bcaf78411be6a351fe895663f86`.
- D5 report ID:
  `frg2dproof_v02:3bf2eb39b8e4e2ea0fe5b7517f677da3b784c43b75d60bce09fb69524c7cc2e1`.
- D5 two-process log SHA-256:
  `bc30b2ddcabc2d4f78943aec5f5fb1912cddea55db8cb1eec1b69e98a18fd63d`.
- Complete Living: 575/575 PASS, calls 27/27.
  Log SHA-256: `7c80e053e2423fd296f51a9535e4e261453462e21200de508b725ba2aed13f38`.
- Complete Kernel Conformance: 349/349 PASS, calls 27/27.
  Log SHA-256: `4bf08b89b45356e19e18d083442c5c5595ff441cd52e96b9c21afc6af5d539af`.
- Anti-gaming micro: 4/4 PASS, calls 3/3.
  Log SHA-256: `36d91a16d778837427937ddce68ae4ae77fc9c3b5d3084e13209876ea2d676c4`.

Every accepted watchdog reported no timeout, no repository mutation, and no
output-reader failure. This evidence records bounded execution; it creates no
authority, truth, permission, external action, or effect.

## 6. Independent Re-Audit

The committed independent re-audit is:

- Path: `docs/audit_reports/auditor_fractal_runtime_g2_d_v038_proof_based_whole_run_correction_v01.log`.
- Commit: `edfa42198efa1d03097570d30b6364af1b567050`.
- SHA-256: `acd62cfcf3753a4c02c5f5187e64e8940cf3b3420f97850b0426583465996d67`.
- Bytes/LF/mode: `21325/459/0644`.
- Evidence archive SHA-256:
  `5e43b38b921f7035609e5ef3a33058325c4b529193ad82d87b70a84cd6ff363b`.

All audit registers 6.1 through 6.15 passed with blocker count zero. The audit
found the implementation conformant to the accepted v0.3.8 contract, including
the proof-based null-policy branch, empty named-policy inventory, independently
derived aggregate full closure, activation-witness support closure, historical
context-None path, strict-selective path, identity lineage, negative matrix,
and zero-authority/effect boundary.

The independent re-audit is evidence and did not itself close G2-D. This
additive checkpoint and synchronized current status record the successor
reclosure after that audit.

## 7. Exact Additive Reclosure Path Scope

1. `docs/fractal_runtime_v0_2_g2_d_proof_based_whole_run_correction_checkpoint_v01.md`
2. `AGENTS.md`
3. `README.md`
4. `specs/machine_manifest_v0_25.json`
5. `release/current_status_overlay_v01.json`
6. `release/claim_to_evidence_index.md`
7. `release/current_limitations.md`
8. `release/current_release_notes.md`
9. `tests/test_repository_release_spine_v01.py`

The future owner commit adds the checkpoint and modifies the other eight paths.
It changes no runtime, schema, G2-D implementation test, demo, facade,
Transition Registry, G2-E code, contract, or lower/shared implementation path.

## 8. Historical Evidence and Preserved Nonclaims

The original pre-correction audit
`docs/audit_reports/auditor_fractal_runtime_g2_d_v02.log` and checkpoint
`docs/fractal_runtime_v0_2_g2_d_checkpoint_v01.md` remain immutable evidence
for their exact pre-correction bytes only.

The v0.3.7 implementation, audit
`docs/audit_reports/auditor_fractal_runtime_g2_d_v037_observed_work_correction_v01.log`,
checkpoint
`docs/fractal_runtime_v0_2_g2_d_observed_work_correction_checkpoint_v01.md`,
and closure commit `48ab284ee7c1ba33400f0d0c7fe5656b4249b839` remain immutable evidence for
v0.3.7 bytes only. No old audit or checkpoint certifies v0.3.8 bytes.

The v0.3.8 evidence chain consists of the accepted addendum, implementation
commit, lifecycle-sync commit, owner execution archive, independent re-audit,
and this new additive successor checkpoint. These records do not create
authority or close Gate 2.

G2-E3 remains `REVALIDATION_PENDING_ON_CORRECTED_G2D`; one fresh unchanged
owner-terminal V06 is required after this reclosure. G2-E4 status and anti-gaming
acceptance remain `BLOCKED_PENDING_FRESH_G2E3_V06`; no anti-gaming correction is
authorized before that V06 passes. G2-E5, G2-E6, and G2-F remain
`NOT_STARTED_NOT_AUTHORIZED`. Gate 2 remains `NOT_CLOSED`.

No public release, RC2, production readiness, production security, successor
baseline, provider/model/network/connector operation, external/global DRS,
permission, `ActionCommitPacket`, receipt, `FinalOutput`, DRS write, or
real-world effect is claimed.

## 9. Closing Flags

G2D_V038_PROOF_BASED_NULL_POLICY_BRANCH=PASS
G2D_V038_NAMED_POLICY_INVENTORY=EMPTY
G2D_V038_AGGREGATE_FULL_CLOSURE_PROOF=PASS
G2D_V038_ACTIVATION_WITNESS_SUPPORT_CLOSURE=PASS
G2D_V038_INDEPENDENT_REAUDIT=PASS
G2D_V038_ADDITIVE_RECLOSURE_COMPLETED=true
G2D_V038_CORRECTED_CLOSED_PASS=true
G2D_STATUS=CLOSED_PASS
G2E3_STATUS=REVALIDATION_PENDING_ON_CORRECTED_G2D
G2E4_STATUS=BLOCKED_PENDING_FRESH_G2E3_V06
G2E4_ANTI_GAMING_ACCEPTANCE=BLOCKED_PENDING_FRESH_G2E3_V06
G2E5_STARTED=false
G2E6_STARTED=false
G2F_STARTED=false
GATE2_STATUS=NOT_CLOSED
ROOT_ONLY_FINAL_AUTHORITY=true
REAL_WORLD_EFFECTS=0
