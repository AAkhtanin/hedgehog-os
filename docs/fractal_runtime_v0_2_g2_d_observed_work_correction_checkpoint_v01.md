# G2-D v0.3.7 Observed-Work Correction Additive Successor Checkpoint

## 1. Metadata and Closure Boundary

```text
document_status: CHECKPOINT
checkpoint_id: fractal_runtime_v0_2_g2_d_observed_work_correction_v01
checkpoint_version: v0.1
gate_id: gate2_g2d_fractal_runtime_v0_2_v037_correction
gate_slice: G2-D
corrected_g2d_status: CLOSED_PASS
closure_commit_identity: NOT_SELF_RECORDED
closure_commit_subject: Close G2-D v0.3.7 observed-work correction
```

This additive successor checkpoint closes the accepted G2-D v0.3.7
observed-work correction after corrected implementation, full owner execution
evidence, independent re-audit, and additive release/status synchronization.
The future owner reclosure commit cannot be self-recorded inside its own
pre-commit checkpoint, so its identity remains `NOT_SELF_RECORDED`.

## 2. Corrected Committed Basis

```text
accepted_v037_addendum_sha256: 29983cd17cbefe306de32cf045827fc927280bae5fdb0d7c9db50203a0ea6511
corrected_implementation_commit: 27c6dfd10740103cddc13bac3ce35f917b5f30c5
corrected_implementation_parent_commit: 3dcaabb7a231259c488643a652b92ee03d7faf52
corrected_implementation_patch_sha256: be594af310b2d13baf0e45283944bd68f56461126b6aa3fbbcaff541a58a0279
independent_reaudit_commit: 2eccb604fee89d7e79025337d3858d6dbfea5fbc
independent_reaudit_path: docs/audit_reports/auditor_fractal_runtime_g2_d_v037_observed_work_correction_v01.log
independent_reaudit_sha256: c31d1712593184317b03425c57c5fcebf19532cbfc3086981223bf32afd0e8a3
owner_evidence_bundle_sha256: e49752fcd1c19dfe8ddf55a254b2d97f8c27688bc0c2371b6ad4ffe2ec5c9cdd
closure_commit_identity: NOT_SELF_RECORDED
```

The corrected implementation commit is the accepted byte basis. The
independent re-audit commit is evidence over those bytes. Neither commit nor
this checkpoint creates authority, permission, execution, or effect.

## 3. Authority and Ownership Boundary

- Root remains the only final authority.
- G2-C owns the accepted Root-reviewed route.
- G2-D owns `RuntimeExecutionTopology` and stable topology-node IDs.
- `RuntimeObservedWorkContextV02` and observed-work `KernelArtifactV01`
  bindings are evidence-only, Root-review-required carriers and are not
  authority.
- Post V&V validates and GT advises; neither decides.
- G2-D imports no G2-E module or type.
- No PlanGraph adapter, migration, or ownership path is introduced.
- The independent re-audit is evidence, not authority or closure by itself.

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
- Package `__all__`: `19`, unchanged.
- Validation targets: `35`.
- Failure stages: `30`.
- Public reason codes: `220`.
- Transition rules: `17`.
- G2-D-local causal decision effects: `14`.
- `FractalRuntimeExecutionBundleV02` fields: `28`.
- G2-D test function nodes: `83`.
- G2-D collected items: `92`.
- Transition test function nodes: `60`.
- Transition collected items: `268`.
- D5 cases: `72`.
- D5 split: `36/36`.
- D5 constructive accepted public runs: `10`.

The corrected surface adds no authority/effect field, serialized observed-work
binding type, G2-E dependency, or E4 implementation surface.

## 5. Accepted Execution Evidence

```text
historical D3 context focused: 2/2 PASS, calls 0/0
release plus maintenance: 23/23 PASS, calls 0/0
complete G2-C: 392/392 PASS, calls 0/0
shared compatibility: 64/64 PASS, calls 0/0
complete G2-D plus Transition: 360/360 PASS, calls 30/30
D5 child 1: PASS
D5 child 2: PASS
D5 cases per process: 72
D5 split per process: 36/36
D5 accepted bundles per process: 10
D5 public calls per process: 27/27
D5 rendered SHA-256: ec05a8cf9377953abdf84b8a45af07afa3615bcaf78411be6a351fe895663f86
D5 report ID: frg2dproof_v02:3bf2eb39b8e4e2ea0fe5b7517f677da3b784c43b75d60bce09fb69524c7cc2e1
complete Living: 575/575 PASS, calls 27/27
complete Kernel Conformance: 349/349 PASS, calls 27/27
```

Evidence-log SHA-256 ledger:

- Static: `a770361c93e9fc89434d3e546f8a40c5d4f48a1056e67978dc092be52ee87e5c`.
- D3 context focused: `05fda5661a4ec50e093e2ee91f986e4b73ce965a6ed99c4023d95d657e153c11`.
- Release 23: `10a8e28f0716353f4155ff89fd3b8197ab685eb449a2e58c5d94653dc3f5bd25`.
- Complete G2-C: `5de16c4117ed9b28de7e91261d7cccc29d9d0fd66954d6bc4a6e8a37e9ad4cb0`.
- Shared compatibility: `3f85c7ff15727b283f323ea63c72387c06253de59b1f8ce3eee3d2d981babeb7`.
- Core 360: `c707a8653fb62ce89d0fe1af4d92e3d82e75e516b50321d92ec3e8b40750b599`.
- D5 two-process: `530210d9b1361b2d3485909ba3434563ea72d982426a9c2c0200b4e8640a3aa6`.
- Living: `38cb6fc8a67ec291ffb6bf637310a983ccc885b3d86325229da354bb75435f08`.
- Kernel Conformance: `aa20a31b6dbeb241fa18eda4cae5e88c7e5af9c9e8d1b80a4ec60bcd251f4255`.

These are owner execution results consumed by the independent re-audit. Test,
runner, hash, trace, report, and audit outputs are evidence, not truth or
authority.

## 6. Independent Re-Audit

The independent read-only re-audit at
`docs/audit_reports/auditor_fractal_runtime_g2_d_v037_observed_work_correction_v01.log`
passed with blocker count `0` over implementation commit
`27c6dfd10740103cddc13bac3ce35f917b5f30c5`. Its exact SHA-256 is
`c31d1712593184317b03425c57c5fcebf19532cbfc3086981223bf32afd0e8a3`,
and it was committed as `2eccb604fee89d7e79025337d3858d6dbfea5fbc`.

```text
INDEPENDENT_REAUDIT=PASS
CORRECTED_IMPLEMENTATION_CONFORMS_TO_ACCEPTED_V037=true
CORRECTED_G2D_CLOSED_PASS=false
ADDITIVE_RECLOSURE_REQUIRED=true
FRESH_G2E3_V06_REQUIRED_AFTER_RECLOSURE=true
G2E4_STARTED=false
```

The re-audit did not close G2-D by itself. This additive successor checkpoint
and synchronized active release surfaces complete the separately authorized
reclosure step.

## 7. Exact Additive Reclosure Path Scope

1. `AGENTS.md`
2. `README.md`
3. `docs/fractal_runtime_v0_2_g2_d_observed_work_correction_checkpoint_v01.md`
4. `release/claim_to_evidence_index.md`
5. `release/current_limitations.md`
6. `release/current_release_notes.md`
7. `release/current_status_overlay_v01.json`
8. `specs/machine_manifest_v0_25.json`
9. `tests/test_repository_release_spine_v01.py`

No runtime, schema, Transition, facade, G2-E, Living, Conformance, historical
audit, or historical checkpoint byte is part of this reclosure scope.

## 8. Historical Evidence and Preserved Nonclaims

- Historical pre-correction audit SHA-256:
  `ccc367ac92ad02e005c7968d152bf7810a772db94dd671e26e5d27f30d2d72aa`.
- Historical pre-correction checkpoint SHA-256:
  `f5bb19741ee992605ed772a282f4374bc3949508052edb09c8b3fdbbf210c1de`.
- Both remain immutable evidence for old bytes only.
- Gate 2 remains `NOT_CLOSED`.
- G2-E3 remains `REVALIDATION_PENDING_ON_CORRECTED_G2D`.
- G2-E4 remains `NOT_STARTED_NOT_AUTHORIZED`.
- No G2-E4, G2-E5, G2-E6, or G2-F implementation is claimed.
- No production readiness or production security is claimed.
- No public release or RC2 is claimed.
- No persistence, distribution, or fault tolerance is claimed.
- No provider, network, connector, or external-DRS reliability is claimed.
- No successor baseline, authority, permission, `FinalOutput`, DRS write, or
  real-world effect is claimed.

## 9. Closing Flags

```text
G2D_V037_CORRECTED_STATUS=CLOSED_PASS
G2D_V037_IMPLEMENTATION_COMMIT=27c6dfd10740103cddc13bac3ce35f917b5f30c5
G2D_V037_INDEPENDENT_REAUDIT_COMMIT=2eccb604fee89d7e79025337d3858d6dbfea5fbc
G2D_V037_ADDITIVE_RECLOSURE_COMPLETED=true
G2D_V037_CLOSURE_COMMIT_IDENTITY=NOT_SELF_RECORDED
G2D_V037_CLOSURE_COMMIT_SUBJECT=Close G2-D v0.3.7 observed-work correction
G2E3_STATUS=REVALIDATION_PENDING_ON_CORRECTED_G2D
G2E4_STATUS=NOT_STARTED_NOT_AUTHORIZED
GATE2_STATUS=NOT_CLOSED
G2E4_G2E5_G2E6_G2F_IMPLEMENTATION_CLAIMED=false
PRODUCTION_READINESS_OR_SECURITY_CLAIMED=false
PUBLIC_RELEASE_OR_RC2_CLAIMED=false
PERSISTENCE_DISTRIBUTION_OR_FAULT_TOLERANCE_CLAIMED=false
PROVIDER_NETWORK_CONNECTOR_EXTERNAL_DRS_RELIABILITY_CLAIMED=false
SUCCESSOR_BASELINE_AUTHORITY_PERMISSION_FINALOUTPUT_DRS_WRITE_EFFECT_CLAIMED=false
```

Corrected G2-D v0.3.7 is internally `CLOSED_PASS` at this additive reclosure
boundary. Gate 2 remains open, one fresh unchanged owner-terminal G2-E3 V06 is
still required, G2-E4 remains unstarted and unauthorized, and every preserved
nonclaim above remains in force.
