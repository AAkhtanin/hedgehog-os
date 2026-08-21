# G2-D Post-Acceptance Contract Addendum Version 0.3.10

## Current Accepted v0.3.10 Correction and E4 Scope-Reconciliation Metadata

```text
document_status: POST_ACCEPTANCE_CORRECTION_ADDENDUM
document_revision: v0.3.10
guardian_review_status: ACCEPTED_WITH_MANDATORY_NARROW_OVERLAY
guardian_ruling: APPROVE_PROFILE_D_CORRECTION_AND_E4_BACKPRESSURE_SCOPE_RECONCILIATION
accepted_v039_basis_revision: v0.3.9
accepted_v039_basis_sha256: 1bbe028a4c757330b4ba94aec461e5bfbb1d1ef7496a68593dc20106c4867445
repository_basis_branch: main
repository_basis_head: 36c43db9045d56666e961b54b4f9b272079f41a8
repository_basis_origin_main: 36c43db9045d56666e961b54b4f9b272079f41a8
V039_PROFILE_D_IMPLEMENTATION_NONCONFORMANCE: YES
V0310_G2D_RUNTIME_SEMANTICS_CHANGED: NO
V0310_G2E4_ACCEPTANCE_OVERLAY_SEMANTICS_CHANGED: YES
V0310_ROLE: EXPLICIT_PROFILE_D_T12_IMPLEMENTATION_NONCONFORMANCE_AND_E4_BACKPRESSURE_SCOPE_CORRECTION
G2D_POSITIVE_BACKPRESSURE_LAW_CHANGED: NO
G2D_PUBLIC_REVISE_SEMANTICS_CHANGED: NO
implementation_authorized: false
implementation_started: false
contract_hop_completed: true
implementation_repository_patch_created: false
release_consumer_maintenance_authorized: true
release_consumer_maintenance_required: true
release_consumer_maintenance_status: NOT_STARTED
release_consumer_maintenance_scope: tests/test_repository_release_spine_v01.py
parked_primary_e4_patch_sha256: fe6cecec37512faad1c36eaea2a6ad61f4173998dfa09a993c0c889a1857dee0
parked_primary_e4_patch_bytes: 117645
parked_primary_e4_patch_lf: 2708
parked_primary_e4_runtime_postimage_sha256: 825fb732504725d200761cb2dbfddbf0f6ca94b5b946f32b0bdc8b5876f1985f
parked_primary_e4_test_postimage_sha256: 49982e9dbf1968550c46ddaf04770f1d5d81bfa3b6f32fc8612ee7ca631d456f
g2e4_scope_correction_authorized: false
g2e4_public_backpressure_calls_required: 2
g2e4_public_backpressure_geometry_required: ((0,3),(2,1))
g2e4_public_backpressure_latest_queue_counts_required: (7,15)
g2e4_public_backpressure_results_required: NONE_NONE
g2e4_nonempty_backpressure_state_required: false
g2e4_explicit_public_revise_calls_required: 4
g2d_internal_public_revise_calls_per_reconstruction_required: 0
current_g2d_status: CORRECTION_CONTRACT_ACCEPTED_IMPLEMENTATION_PENDING
historical_v039_g2d_status: CLOSED_PASS_ON_V039_BYTES
current_g2e3_status: REVALIDATION_PENDING_ON_CORRECTED_G2D
current_g2e4_strict_subtree_status: IMPLEMENTED_COMMITTED_PASS
current_g2e4_anti_gaming_status: BLOCKED_PENDING_G2D_V0310_RECLOSURE
g2e5_status: NOT_STARTED_NOT_AUTHORIZED
g2e6_status: NOT_STARTED_NOT_AUTHORIZED
g2f_status: NOT_STARTED_NOT_AUTHORIZED
gate2_status: NOT_CLOSED
```

Version v0.3.10 records one implementation nonconformance in the accepted
Profile-D child t12 projection and corrects one proven overconstraint in the
G2-E4 acceptance overlay. These are separate scopes:

- the accepted G2-D runtime semantics do not change;
- the G2-D positive backpressure law does not change;
- only the G2-E4 requirement to manufacture a nonempty backpressure carrier
  in a lawful non-exhausted strict-selective frontier changes.

This contract-only hop authorizes no implementation. It changes no runtime,
schema, demo, facade, Transition Registry, G2-E runtime, Root, Post V&V, GT,
G2-C, ABI, D5, Living, Conformance, or V06 byte.

It does authorize one nonsemantic release-consumer maintenance hop after the
contract commit and before any runtime authorization. That hop may modify only
`tests/test_repository_release_spine_v01.py`. It creates no runtime or G2-D
test implementation, changes no contract or semantic law, grants no authority,
and claims no acceptance or closure.

## 1. Guardian Ruling and Exact Supersession Boundary

The controlling guardian result is exact:

```text
GUARDIAN_RULING=APPROVE_PROFILE_D_CORRECTION_AND_E4_BACKPRESSURE_SCOPE_RECONCILIATION
V039_PROFILE_D_IMPLEMENTATION_NONCONFORMANCE=YES
V0310_G2D_RUNTIME_SEMANTICS_CHANGED=NO
V0310_G2E4_ACCEPTANCE_OVERLAY_SEMANTICS_CHANGED=YES
G2D_POSITIVE_BACKPRESSURE_LAW_CHANGED=NO
G2D_PUBLIC_SURFACE_CHANGED=NO
G2D_SCHEMA_CHANGED=NO
NEW_ARCHITECTURE_REQUIRED=NO
IMPLEMENTATION_AUTHORIZED=NO
```

This v0.3.10 overlay supersedes only:

1. the v0.3.8 Section 8 statement that the standard G2-E4 conditional path
   must produce a nonempty typed backpressure carrier; and
2. the v0.3.9 Section 7 statement that the same public path must carry
   nonempty backpressure states.

It does not supersede the requirement to execute the real public G2-D
backpressure operation. It does not supersede nonempty revise observations,
partial-failure IDs, unresolved IDs, the exact public reason set, the final
non-ACCEPT Root decision, strict sibling preservation, or any authority and
zero-effect law.

The complete accepted v0.3.9 addendum is retained byte-exact below. Every
v0.3.9 law outside this exact supersession boundary remains controlling.

## 2. Existing Profile-D t12 Duty and Proven v0.3.9 Nonconformance

The accepted t12 law already permits a valid, settled, non-eligible revise
observation to map an exact D3-local child `VALIDATING` occurrence to
`DEADEND`. The observation must be produced by the public revise evaluator,
must replay the exact historical t06 origin, and must preserve the source
queue observations, evidence, advisories, queue reasons, cell, node, round,
and budget identities.

The v0.3.9 runtime reaches the correct public t12 decision and queue entry, but
the Profile-D artifact projection later applies the ordinary local outcome
again. For a dependency-free child D3-local node that ordinary material is
`COMPLETED`; the projector therefore rejects the already accepted revise
target `DEADEND`. The accepted semantic decision is correct and the later
projection is nonconformant:

```text
V039_PROFILE_D_IMPLEMENTATION_NONCONFORMANCE=YES
V0310_G2D_RUNTIME_SEMANTICS_CHANGED=NO
PROFILE_D_PUBLIC_T12_DECISION_REACHABLE=YES
PROFILE_D_PUBLIC_T12_ARTIFACT_PROJECTION_CONFORMANT=NO
```

No Root-only substitution, ordinary `COMPLETED` laundering, manually built
revise object, caller-selected outcome, or E4-side adapter may replace the
Profile-D correction.

The clean v0.3.9 transition reconstruction also calls the public
`evaluate_fractal_revise_observation_v02` internally. Once the Profile-D
projector consumes the same reconstruction, that nesting inflates captured
public-call accounting (101 observed calls in the repaired contour, and more
than four even without the projector). This is an implementation
nonconformance, not a semantic-law change. E4 owns exactly four explicit
public revise calls; internal transition/projector reconstruction owns zero
public calls.

## 3. Future Narrow G2-D v0.3.10 Runtime Correction

A later separately owner-authorized implementation may modify exactly:

1. `hedgehog/kernel/fractal_runtime_v02.py`
2. `tests/test_fractal_runtime_g2_d_v02.py`

No public type, field, signature, schema definition, reason, validation target,
failure stage, Transition rule, facade name, authority, or effect law may
change.

The future correction must:

1. consume settled revise observations already constructed through
   `evaluate_fractal_revise_observation_v02`;
2. require the exact child Profile-D topology, cell, node, queue, t06 origin,
   source observations, evidence, advisories, queue reasons, and budget
   identities;
3. reconstruct and validate the settled observation through public semantics,
   not object identity or a copied PASS label;
4. select revise-derived `DEADEND` before the generic D3-local ordinary
   outcome can mask it in Profile-D projection;
5. preserve the exact t12 rule, decision, reason, target entry, target
   artifact, copied queue support reasons, and no-budget-successor law;
6. preserve ordinary dependency-free child `COMPLETED` when no accepted
   revise-no-progress observation exists;
7. place exact deterministic revise reconstruction behind one private helper;
   the public evaluator delegates to it, while transition and Profile-D
   projection call it directly and create no nested public calls;
8. preserve exactly four explicit public E4 revise calls and zero internal
   public revise calls per reconstruction;
9. filter the already validated settled revise ledger for the exact
   noneligible `DEADEND` observation bound to the Profile-D child topology,
   cell, `VALIDATING` queue entry, and budget identities; require exactly one
   such qualifying observation; permit the lawful eligible positive
   observation bound to the same queue entry and revision without treating it
   as a competing `DEADEND` candidate; and preserve contextual rejection of
   missing, ambiguous, duplicate, foreign, reordered, wrong-cell, wrong-node,
   wrong-round, wrong-origin, wrong-queue, and wrong-budget revise material;
   and
10. preserve exact-repeat/no-spin and all positive backpressure behavior.

The existing public t12 test item must be strengthened without adding a test
function or parametrized item. G2-D geometry remains 83 test functions and 92
collected items. Private reconstruction is not a second semantic path: public
and internal consumers must return the same canonical decision or fail closed.

The local Profile-D selector must not require the total number of observations
bound to the `VALIDATING` queue entry to equal one. The accepted E4 contour
stores an eligible positive observation followed by a noneligible `DEADEND`
observation on the same exact topology, cell, queue, budget, and revision
binding. Only the latter qualifies for `DEADEND` projection. Zero qualifying
observations is missing proof; more than one qualifying noneligible `DEADEND`
observation is real local ambiguity. Either case fails closed. The lawful
eligible positive observation is neither extra proof nor ambiguity, and its
presence must not change the four-explicit/zero-internal public-call law.

## 4. Proven Strict-Selective E4 Backpressure Geometry

The standard conditional G2-E4 profile is a strict affected subtree. Its two
required public backpressure evaluations observe different lawful frontiers
in this exact order:

```text
call 1 baseline: max_parallelism=3, current_parallelism=0, latest READY=0,
                 occupied=0, residual=3, lawful latest queue entries=7
call 2 conditional: max_parallelism=3, current_parallelism=1, latest READY=1,
                    occupied=2, residual=1, lawful latest queue entries=15
public evaluate_fractal_backpressure_v02 calls = 2
public results = (None, None)
latest queue order = exact append-log order at both calls
```

Capacity is not exhausted at either call. No dependency-satisfied PENDING
occurrence is blocked solely by zero residual capacity. Public G2-D therefore
returns `None` twice exactly as designed.

The unaffected sibling is already terminal and must remain byte-exact. The
other selected child nodes are linearly dependency-bound. Creating an extra
RUNNING, READY, or eligible PENDING occurrence would fabricate source work,
execute an unaffected sibling, widen the affected closure, or violate stable
topology and append-only history. Lowering `max_parallelism`, injecting a
synthetic third slot, transplanting the separate full-fractal 3/3 witness, or
constructing a fake `FractalBackpressureStateV02` is forbidden.

The public nullable result is a semantic result. `None` is not a malformed
typed state and must not be passed to
`validate_fractal_backpressure_state_v02`.

## 5. Preserved Positive G2-D Backpressure Law

The accepted positive G2-D witness remains exact and unchanged:

- two accepted parent FRACTAL_CELL occurrences are RUNNING;
- one accepted child node occurrence is READY;
- another accepted dependency-satisfied child occurrence is PENDING;
- `occupied=3`, `residual=0`, and the public evaluator returns one typed
  backpressure state;
- exact t03 defer closure, reconsideration, capacity release, later admission,
  append-only history, and no-spin behavior remain required.

The existing
`test_d3_s0_t03_postclosure_suppression_s1_no_spin_v035` remains a mandatory
positive control. The future Profile-D correction may not change the public
backpressure evaluator or weaken this witness.

## 6. Corrected Mandatory G2-E4 Public End-to-End Overlay

After v0.3.10 implementation, acceptance, commit, independent re-audit,
additive reclosure, and one fresh unchanged G2-E3 V06, the parked G2-E4
candidate resumes through the public path:

```text
run_continuous_delta_runtime_v01
-> execute_selective_recomputation_v01
-> public conditional branch
```

The conditional profile must execute and carry:

```text
two public backpressure evaluations at ((occupied,residual)=(0,3),(2,1))
with latest queue counts (7,15) in append-log order -> (None, None)
+ exactly four explicit public revise evaluations
+ zero nested public revise evaluations from transition/projector reconstruction
+ nonempty revise observations including exact-repeat/no-progress
+ nonempty partial failures
+ nonempty unresolved artifact IDs
-> complete publicly valid G2-D evidence family
-> SelectiveRecomputationResultV01
-> ContinuousDeltaRuntimeTraceV01
-> ContinuousDeltaRuntimeReportV01
-> non-ACCEPT Root decision
-> bundle = None
-> report.status = FAIL_CLOSED
```

The exact strict-selective conditional result is:

```text
recomputed_g2d_bundle.backpressure_states = ()
runtime_trace.backpressure_state_ids = ()
g2d_transition_backpressure_deferred = absent
g2e_recomputation_budget_exceeded = absent
result.reason_codes = (
  g2e_recomputation_no_progress,
  g2e_transition_selective_recomputation_blocked,
)
```

The complete public path still requires exactly two public calls. Zero, one,
three, or more calls fail acceptance. A non-`None` state at either frozen
frontier, any t03 defer occurrence, any budget-exceeded reason, or any
success-laundered carrier fails closed.

Contextual validators must still reject missing, extra, duplicate, foreign,
reordered, or success-laundered revise, partial-failure, and unresolved
carriers. t10, an accepted FINALIZED report artifact, and an accepted E4
bundle remain absent. The normal strict-subtree PASS path remains free of
synthetic failure carriers.

## 7. E4 Acceptance Assertions and Call Accounting

The existing
`test_e4_partial_failure_backpressure_revise_no_progress_v01` must prove,
through captured public calls rather than a private helper:

1. both call frontiers have `max_parallelism=3`;
2. call 1 has `(current_parallelism, latest READY, occupied, residual) =
   (0,0,0,3)` and exactly 7 lawful latest queue entries;
3. call 2 has `(current_parallelism, latest READY, occupied, residual) =
   (1,1,2,1)` and exactly 15 lawful latest queue entries;
4. both queue-entry tuples are the exact append-log latest projections;
5. the ordered public result tuple is `(None, None)`;
6. backpressure state and trace-ID tuples are empty;
7. no t03 transition or backpressure queue support reason exists;
8. the exact two public E4 reasons exclude budget exhaustion;
9. two stored revise observations in exact order -- eligible positive followed
   by noneligible `DEADEND` -- share the exact `VALIDATING` queue and revision
   binding, exactly one qualifies for Profile-D `DEADEND` projection, and the
   partial failure plus nonempty unresolved IDs are publicly and contextually
   valid;
10. exactly four explicit public revise calls are observed and internal
    transition/projector reconstruction adds zero public calls;
11. a forged budget-exceeded reason fails contextual validation;
12. the final Root decision is non-ACCEPT and no t10 or accepted bundle exists;
13. the baseline and unaffected sibling canonical bytes remain unchanged.

Final E4 call accounting remains controlling:

```text
E4_PAIR_CALL_ACCOUNTING=2/2
E4_FOCUSED_CALL_ACCOUNTING=2/2
E4_COMPLETE_FILE_CALL_ACCOUNTING=3/3
```

No extra call may be introduced to satisfy a counter.

## 8. Preserved Geometry, Authority, and Protected Surfaces

The future G2-D correction preserves:

```text
public dataclass types = 21
serialized types = 18
runtime-only types = 3
canonical-module public functions = 116
module __all__ entries = 137
direct package G2-D attributes = 143
validation targets = 35
failure stages = 30
public reason codes = 220
Transition rules = 17
G2-D test function nodes = 83
G2-D collected items = 92
```

Root remains the only final authority. G2-C owns the accepted Root-reviewed
route. G2-D owns RuntimeExecutionTopology and stable topology-node and cell
IDs. G2-D imports no G2-E module or type. Post V&V validates and GT advises.

No successor baseline, permission, ActionCommitPacket, receipt, FinalOutput,
DRS write, provider/model/network/connector authority, external-DRS action,
or real-world effect is created or claimed.

The G2-D schema, demo, Transition Registry, package facade, Root, Post V&V,
GT, G2-C, G2-E addendum and preflight, D5, Living, Conformance, roadmaps, and
V06 runner remain protected in the contract-only hop.

## 9. Future Acceptance and Reclosure

### 9.1 Mandatory release-consumer maintenance bridge

The contract commit cannot be followed directly by the two-path runtime
repair. A mandatory one-path release-consumer maintenance commit must first
align the release-spine test with the exact implementation candidate while
preserving all historical checks.

The exact commit subjects are reserved as:

```text
contract: Accept G2-D v0.3.10 Profile-D and E4 scope correction contract
maintenance: Align G2-D v0.3.10 release tests with implementation candidate
implementation: Implement G2-D v0.3.10 Profile-D t12 projection correction
```

The maintenance scope is exactly:

```text
tests/test_repository_release_spine_v01.py
```

The contract-commit release test must retain explicit `NOT_FROZEN`/zero
placeholders for every prospective implementation runtime, test, and patch
identity. Only after the contract commit exists may the exact two-path
candidate be derived from its final G2-D contract-test bytes. The maintenance
version must record the exact contract commit identity, materialize the exact
derived runtime/test/patch SHA-256, byte, and LF identities, and activate the
already-reviewed lifecycle state machine. No other line or path may change in
that maintenance commit. The release test must distinguish and fail closed
outside these exact states:

| State | HEAD / parent law | Dirty paths | Runtime SHA-256 | G2-D test SHA-256 |
|---|---|---|---|---|
| PRE_CONTRACT_DIRTY | HEAD `36c43db9045d56666e961b54b4f9b272079f41a8` | exact ten contract paths | historical v0.3.9 | contract-only v0.3.10 |
| POST_CONTRACT_PRE_MAINTENANCE_CLEAN | unique contract commit, parent basis, exact subject and ten-path diff | none | historical v0.3.9 | contract-only v0.3.10 |
| MAINTENANCE_CANDIDATE_DIRTY | HEAD contract commit | only release-spine test | historical v0.3.9 | contract-only v0.3.10 |
| POST_MAINTENANCE_CLEAN | unique maintenance commit, parent contract, exact subject and one-path diff | none | historical v0.3.9 | contract-only v0.3.10 |
| IMPLEMENTATION_CANDIDATE_DIRTY | HEAD maintenance commit | exact runtime plus G2-D test | exact maintenance-pinned candidate | exact maintenance-pinned candidate |
| POST_IMPLEMENTATION_CLEAN | unique implementation commit, parent maintenance, exact subject and two-path diff | none | same implementation runtime | same implementation test |

The exact future implementation candidate remains `PENDING_FULL_ACCEPTANCE`
and unauthorized by this contract hop. To avoid a recursive hash dependency
between the cumulative addendum and the G2-D test that validates it, exact
runtime, test, and full-index patch SHA/byte/LF identities are absent from the
contract-commit release-test bytes and are owned only by the one-path
maintenance version of the release-spine test:

```text
runtime_identity: PINNED_BY_RELEASE_CONSUMER_MAINTENANCE
test_identity: PINNED_BY_RELEASE_CONSUMER_MAINTENANCE
full_index_patch_identity: PINNED_BY_RELEASE_CONSUMER_MAINTENANCE
implementation_candidate_status: PENDING_FULL_ACCEPTANCE_NOT_AUTHORIZED
```

Both the dirty two-path implementation diff and the committed implementation
diff must match that full-index patch identity. Exact parent, subject, path,
hash, byte, and LF checks may not be weakened or replaced by status labels.

All B -> C -> M -> I work and later G2-D reclosure must occur in a
clean isolated Git worktree. The real primary worktree remains parked with its exact
two-path dirty G2-E4 runtime/test patch throughout this lifecycle. Applying
the G2-D contract, maintenance, implementation, audit, or reclosure directly
on top of that primary dirt is forbidden. The primary patch may be restored
only by guarded fast-forward after v0.3.10 reclosure and a fresh unchanged
G2-E3 V06 PASS; its bytes may not be rewritten, stashed, reset, or absorbed
into any G2-D commit.

The parked owner-primary identity is exact:

```text
patch_sha256: fe6cecec37512faad1c36eaea2a6ad61f4173998dfa09a993c0c889a1857dee0
patch_bytes: 117645
patch_lf: 2708
runtime_postimage_sha256: 825fb732504725d200761cb2dbfddbf0f6ca94b5b946f32b0bdc8b5876f1985f
test_postimage_sha256: 49982e9dbf1968550c46ddaf04770f1d5d81bfa3b6f32fc8612ee7ca631d456f
```

### 9.2 Runtime acceptance and reclosure

Future v0.3.10 implementation acceptance preserves the existing cumulative
contours:

- one strengthened Profile-D t12 focused node;
- complete G2-D: 92/92 PASS;
- complete Transition: 268/268 PASS;
- complete G2-C: 392/392 PASS;
- release plus maintenance: 23/23 PASS;
- complete G2-D plus Transition: 360/360 PASS, calls 30/30;
- D5 in two processes: 72 cases, 36/36 split, 10 accepted bundles, and 27/27
  calls per process;
- Living: 575/575 PASS, calls 27/27;
- Kernel Conformance: 349/349 PASS, calls 27/27.

After the implementation commit, G2-D is `REAUDIT_PENDING`. An independent
read-only re-audit and additive successor checkpoint/reclosure are mandatory
before G2-D returns to `CLOSED_PASS`.

The future audit path is reserved as:

`docs/audit_reports/auditor_fractal_runtime_g2_d_v0310_profile_d_t12_revise_projection_correction_v01.log`

The future checkpoint path is reserved as:

`docs/fractal_runtime_v0_2_g2_d_profile_d_t12_revise_projection_correction_checkpoint_v01.md`

No G2-E checkpoint is created at E4. The accepted G2-E preflight reserves its
checkpoint for the later post-E6 audit and closure hop.

## 10. Frozen Operational Order

The operational order is exact:

1. accept and commit this v0.3.10 contract-only hop;
2. prepare and validate the one-path release-consumer maintenance candidate;
3. commit only `tests/test_repository_release_spine_v01.py` with the exact
   maintenance subject and the contract commit as its sole parent;
4. obtain separate explicit owner authorization for the narrow G2-D runtime
   and existing-test correction;
5. apply exactly the pinned two-path implementation candidate;
6. run complete cumulative G2-D acceptance;
7. commit the exact G2-D correction as `REAUDIT_PENDING` with the maintenance
   commit as its sole parent;
8. synchronize the post-implementation lifecycle surfaces;
9. perform an independent read-only re-audit on exact committed bytes;
10. add the v0.3.10 successor checkpoint and reclose G2-D;
11. run one fresh unchanged G2-E3 V06 on the reclosed v0.3.10 bytes;
12. only after V06 PASS, resume the parked dirty G2-E4 candidate;
13. apply the bounded E4 corrections, including the corrected backpressure
    absence law;
14. run the anti-gaming pair 2/2;
15. run complete G2-E4 18/18;
16. run complete G2-E1 through G2-E4 68/68;
17. create a transparent final G2-E4 corrective commit.

No stash, reset, restore, checkout, amend, rebase, history rewrite, or
force-push is required by this contract.

## 11. Exact Contract-Hop Scope and Lifecycle

This contract-only candidate modifies exactly these ten paths, in this order:

1. `docs/fractal_runtime_v0_2_g2_d_post_acceptance_contract_addendum_v01.md`
2. `tests/test_fractal_runtime_g2_d_v02.py`
3. `AGENTS.md`
4. `README.md`
5. `specs/machine_manifest_v0_25.json`
6. `release/current_status_overlay_v01.json`
7. `release/claim_to_evidence_index.md`
8. `release/current_limitations.md`
9. `release/current_release_notes.md`
10. `tests/test_repository_release_spine_v01.py`

The active contract-only lifecycle is exact:

```text
G2D_STATUS=CORRECTION_CONTRACT_ACCEPTED_IMPLEMENTATION_PENDING
G2D_IMPLEMENTATION_AUTHORIZED=false
G2D_CORRECTED_V0310_IMPLEMENTATION_EXISTS=false
G2D_CONTRACT_ONLY_CLAIM=true
HISTORICAL_V039_G2D_STATUS=CLOSED_PASS_ON_V039_BYTES
G2E3_STATUS=REVALIDATION_PENDING_ON_CORRECTED_G2D
G2E4_STRICT_SUBTREE_STATUS=IMPLEMENTED_COMMITTED_PASS
G2E4_ANTI_GAMING_STATUS=BLOCKED_PENDING_G2D_V0310_RECLOSURE
G2E5_STATUS=NOT_STARTED_NOT_AUTHORIZED
G2E6_STATUS=NOT_STARTED_NOT_AUTHORIZED
G2F_STATUS=NOT_STARTED_NOT_AUTHORIZED
GATE2_STATUS=NOT_CLOSED
```

Public release, RC2, production readiness, and production security
certification remain `NOT_CLAIMED`.

===============================================================================
HISTORICAL ACCEPTED V0.3.9 CONTENT - EXACT REPOSITORY BYTES
===============================================================================

The complete byte sequence below is the previously accepted cumulative
v0.3.9 addendum. It remains immutable historical contract and evidence context
for its exact bytes. Its embedded present-tense lifecycle statements do not
override the active v0.3.10 metadata and rulings above.

# G2-D Post-Acceptance Contract Addendum Version 0.3.9

## Current Accepted v0.3.9 Clarification and Lifecycle Reopening Metadata

```text
document_status: POST_ACCEPTANCE_CORRECTION_ADDENDUM
document_revision: v0.3.9
guardian_review_status: ACCEPTED_WITH_MANDATORY_OVERLAY
guardian_ruling: APPROVE_WITH_MANDATORY_OVERLAY
accepted_v038_basis_revision: v0.3.8
accepted_v038_basis_sha256: 09db4ff2224e59c878b967ba634084d72cd01b36f86edfa5fca2e9750e976ea6
repository_basis_branch: main
repository_basis_head: 4cf427f82a096383ae5873024787c19e56ac0fb5
repository_basis_subject: Close G2-D v0.3.8 proof-based whole-run correction
V038_IMPLEMENTATION_NONCONFORMANCE: YES
V039_CONTRACT_SEMANTICS_CHANGED: NO
V039_ROLE: EXPLICIT_IMPLEMENTATION_NONCONFORMANCE_CLARIFICATION_AND_LIFECYCLE_REOPENING
implementation_authorized: false
implementation_started: false
contract_hop_completed: true
implementation_repository_patch_created: false
isolated_worktree_strategy_approved: true
e4_two_path_only_implementation_sufficient: false
e4_public_end_to_end_carrier_overlay_required: true
revised_guardian_decision_required: false
current_g2d_status: CORRECTION_CONTRACT_ACCEPTED_IMPLEMENTATION_PENDING
historical_v038_g2d_status: CLOSED_PASS_ON_V038_BYTES
current_g2e3_status: IMPLEMENTED_COMMITTED_ACCEPTANCE_PASS_ON_V038_G2D
post_v039_implementation_g2e3_status: REVALIDATION_PENDING_ON_CORRECTED_G2D
current_g2e4_status: IMPLEMENTED_COMMITTED_STRICT_SUBTREE_PASS_ANTI_GAMING_ACCEPTANCE_BLOCKED
current_g2e4_anti_gaming_acceptance: BLOCKED_PENDING_G2D_V039_RECLOSURE
g2e5_status: NOT_STARTED_NOT_AUTHORIZED
g2e6_status: NOT_STARTED_NOT_AUTHORIZED
g2f_status: NOT_STARTED_NOT_AUTHORIZED
gate2_status: NOT_CLOSED
```

Version v0.3.9 introduces no new semantic law, type, field, public signature,
schema definition, reason, validation target, failure stage, facade name,
authority, or effect. It clarifies an existing accepted t12 duty, records that
v0.3.8 did not conform to it, and reopens the lifecycle for one narrow
implementation correction.

This contract-only hop authorizes no implementation. It changes no runtime,
schema, demo, facade, Transition Registry, G2-E runtime, Root, Post V&V, GT,
G2-C, ABI, D5, Living, Conformance, or V06 bytes.

## 1. Guardian Ruling and No-New-Semantics Boundary

The controlling guardian result is exact:

```text
GUARDIAN_RULING=APPROVE_WITH_MANDATORY_OVERLAY
PREACTION_HASH_LITERAL_DEFECT=YES
G2D_V038_IMPLEMENTATION_NONCONFORMANCE=YES
G2D_V039_CONTRACT_SEMANTICS_CHANGED=NO
G2D_V039_LIFECYCLE_REOPENING_REQUIRED=YES
E4_TWO_PATH_ONLY_IMPLEMENTATION_SUFFICIENT=NO
ISOLATED_WORKTREE_STRATEGY_APPROVED=YES
E4_PUBLIC_END_TO_END_CARRIER_OVERLAY_REQUIRED=YES
REVISED_GUARDIAN_DECISION_REQUIRED=NO
IMPLEMENTATION_AUTHORIZED=NO
```

The corrected `hedgehog/gt_validator.py` pre-action identity is
`e8fa9af23cbff04a059523aa25e47eec790c00776c902e545f1779e20ee5f0dd`.
The earlier shortened literal was a prompt defect, not a repository defect and
not a new semantic issue.

The accepted v0.3.8 contract, implementation, independent re-audit, and
successor checkpoint remain immutable historical evidence for their exact
v0.3.8 bytes. Their `CLOSED_PASS` classification is historical and does not
certify future v0.3.9 bytes.

## 2. Existing t12 Duty and Proven Implementation Nonconformance

The accepted contract already requires t12 for a D3-local, child-result, gate,
or structural revise no-progress mapping. Exact revise evidence is present only
for revise no-progress. The D3-local VALIDATING source is replayed against its
historical t06 origin. Non-PARENT_RETURN t08 through t12 decisions copy exact
source observations and queue support reasons and create no budget successor.
Queue support reasons and Transition decision reasons remain separate.

The v0.3.8 implementation validates a non-eligible revise observation and then
classifies VALIDATING work in this order:

1. PARENT_RETURN;
2. FRACTAL_CELL;
3. every D3-local node kind;
4. POST_VV or GT_ADVISORY;
5. only then revise observation to DEADEND.

Every valid node kind is consumed before the revise fallback. For the
dependency-free D3-local source used by G2-E4, ordinary local material derives
COMPLETED and masks the accepted revise-derived DEADEND. Therefore:

```text
V038_IMPLEMENTATION_NONCONFORMANCE=YES
V039_CONTRACT_SEMANTICS_CHANGED=NO
NEW_ARCHITECTURE_REQUIRED=NO
G2D_PUBLIC_SURFACE_CHANGED=NO
G2D_SCHEMA_CHANGED=NO
```

The existing `test_d4_revise_retry_and_no_progress_v02` proves construction of
a non-eligible DEADEND revise observation but does not prove the complete
public chain:

```text
evaluate_fractal_revise_observation_v02
-> evaluate_fractal_runtime_state_transition_v02
-> g2d_t12_validating_to_deadend
-> advance_fractal_cell_queue_v02
-> DEADEND queue entry and artifact
```

## 3. Future Narrow v0.3.9 Runtime Correction

A later separately owner-authorized implementation may modify exactly:

1. `hedgehog/kernel/fractal_runtime_v02.py`
2. `tests/test_fractal_runtime_g2_d_v02.py`

No schema, Transition Registry, facade, Root, G2-C, ABI, Post V&V, GT, public
type, public field, public signature, public reason, validation target, failure
stage, `__all__`, authority, or effect change is allowed.

The runtime correction must:

1. obtain the exact non-eligible revise observation through
   `evaluate_fractal_revise_observation_v02`, not manual dataclass construction;
2. preserve complete public validation of the revise observation;
3. require exact D3-local VALIDATING source material and exact historical t06
   origin replay;
4. require exact source queue observations, evidence, advisories, and immutable
   `queue_reason_codes`;
5. select revise-derived DEADEND after exact revise validation but before the
   generic D3-local allowed-outcome branch can mask it;
6. call `evaluate_fractal_runtime_state_transition_v02` and return exact
   `rule_id = g2d_t12_validating_to_deadend`,
   `decision = RETURN_TO_ROOT`, and
   `reason_code = g2d_transition_deadend_recorded`;
7. preserve target queue reasons equal to source VALIDATING queue reasons and
   `revise.reason_codes = ("g2d_no_progress_deadend",)`;
8. create no budget successor for non-PARENT_RETURN t12;
9. call `advance_fractal_cell_queue_v02` and produce the exact DEADEND queue
   entry and queue artifact;
10. preserve child-result, activation-gate, ordinary D3-local non-revise,
    POST_VV, GT_ADVISORY, PARENT_RETURN, revise-eligible, backpressure, budget,
    trace, and parent identity laws;
11. prove exact-repeat/no-spin: identical revise evidence is deterministic and
    bounded and cannot create an unbounded revision loop.

## 4. Future Public t12 Test Duty

The existing G2-D test family must be strengthened without adding a test
function or parametrized item. It must:

- use the public revise evaluator;
- use the public state-transition evaluator;
- require exact t12 rule, decision, and reason;
- use public queue advance;
- require exact DEADEND entry and artifact;
- require copied source observations, evidence, advisories, and queue reasons;
- require no budget successor;
- require exact trace and parent identity;
- reject wrong node, cell, budget, round, origin, and source tuples;
- prove ordinary D3-local COMPLETED remains unchanged when revise is absent.

## 5. Authority, Ownership, and Zero-Effect Boundary

- Root remains the only final authority.
- G2-C owns the accepted Root-reviewed route.
- G2-D owns RuntimeExecutionTopology and stable topology-node and cell IDs.
- G2-D imports no G2-E module or type.
- PlanGraph remains historical and proof-donor material only.
- Runtime contexts, bindings, queue entries, results, reports, traces, hashes,
  tests, audits, checkpoints, and contract text create no authority.
- Post V&V validates and GT advises; neither decides.
- No successor baseline, permission, ActionCommitPacket, receipt, FinalOutput,
  DRS write, provider/model/network/connector authority, external DRS action,
  or real-world effect is created or claimed.

## 6. Frozen Public Geometry and Protected Surfaces

The future correction preserves the accepted G2-D geometry:

```text
public dataclass types = 21
serialized types = 18
runtime-only types = 3
canonical-module public functions = 116
module __all__ entries = 137
direct package G2-D attributes = 143
validation targets = 35
failure stages = 30
public reason codes = 220
Transition rules = 17
G2-D test function nodes = 83
G2-D collected items = 92
```

The schema, demo, Transition Registry, package facade, Root, Post V&V, GT,
G2-C, G2-E, D5, Living, Conformance, and V06 runner remain protected.

## 7. Mandatory G2-E4 Public End-to-End Carrier Overlay

After v0.3.9 implementation, acceptance, commit, independent re-audit,
reclosure, and one fresh clean G2-E3 V06, the parked G2-E4 candidate resumes
without being rebuilt from scratch.

Final G2-E4 conditional behavior is accepted only through:

```text
run_continuous_delta_runtime_v01
-> execute_selective_recomputation_v01
-> public conditional branch
```

Private-helper-only evidence is forbidden. A private helper may remain only if
it has a production caller in the public E4 call graph, its typed outputs are
consumed by the public path, and the behavioral test does not call it directly
as the execution under test.

The required public chain is:

```text
revise / exact-repeat / no-progress
+ partial failure
+ backpressure
-> complete G2-D evidence family
-> SelectiveRecomputationResultV01
-> ContinuousDeltaRuntimeTraceV01
-> ContinuousDeltaRuntimeReportV01
-> non-ACCEPT Root decision
-> bundle = None
-> report.status = FAIL_CLOSED
```

The public path carries nonempty revise observations, partial-failure IDs,
unresolved IDs, and backpressure states; an exact public reason set; an exact
report unresolved count; and a non-ACCEPT Root decision. t10, an accepted
FINALIZED report artifact, and an accepted G2-E bundle are absent. Every
authority and effect counter remains zero.

Contextual validators may accept only the exact lawful FAIL_CLOSED profile.
Missing, extra, duplicate, foreign, reordered, or success-laundered carriers
fail closed. The normal strict-subtree PASS path remains unchanged and free of
synthetic failure carriers.

## 8. Future Acceptance and Exact Call Accounting

Future v0.3.9 implementation acceptance includes:

- one exact t12 focused node;
- complete G2-D: 92/92 PASS;
- complete Transition: 268/268 PASS;
- complete G2-C: 392/392 PASS;
- release plus maintenance: 23/23 PASS;
- complete G2-D plus Transition: 360/360 PASS, calls 30/30;
- D5 in two processes: 72 cases, 36/36 split, 10 accepted bundles, and 27/27
  calls per process;
- Living: 575/575 PASS, calls 27/27;
- Kernel Conformance: 349/349 PASS, calls 27/27.

After the implementation commit, G2-D is REAUDIT_PENDING. An independent
read-only re-audit and additive reclosure are required before G2-D returns to
CLOSED_PASS. One fresh unchanged logical G2-E3 V06 then runs in the clean
isolated worktree before the primary dirty worktree is fast-forwarded.

Final G2-E4 call accounting is controlling and exact:

```text
E4_PAIR_CALL_ACCOUNTING=2/2
E4_FOCUSED_CALL_ACCOUNTING=2/2
E4_COMPLETE_FILE_CALL_ACCOUNTING=3/3
```

Older 3/3, 3/3, and 4/4 expectations are historical and not controlling. No
extra call may be added to satisfy a counter.

## 9. Frozen Operational Order

The complete operational order is frozen:

1. v0.3.9 clarification and lifecycle-reopening contract in the isolated
   worktree;
2. contract commit and normal non-force push;
3. narrow G2-D runtime and G2-D test correction in the isolated worktree;
4. complete G2-D cumulative acceptance;
5. implementation commit and normal non-force push;
6. independent read-only re-audit;
7. additive v0.3.9 reclosure;
8. one fresh unchanged logical G2-E3 V06 in the clean isolated worktree;
9. only after V06 PASS, guarded fast-forward of the original dirty primary
   worktree to origin/main while proving the parked G2-E4 patch SHA-256 remains
   `3c08807bcf8545b95ceca22ec13f1aa1cb2e8d2669ad72cf269ac2d077163aff`;
10. resume the exact parked G2-E4 candidate;
11. implement the public end-to-end conditional carrier overlay;
12. run the anti-gaming pair 2/2;
13. run complete G2-E4 18/18;
14. run complete G2-E1 through G2-E4 68/68;
15. transparent final G2-E4 corrective commit and normal push.

The forbidden order is v0.3.9 reclosure, primary fast-forward, then V06. V06
must occur before returning to the dirty G2-E4 checkout. No stash, reset,
restore, checkout, amend, rebase, history rewrite, or force-push is required.

## 10. Contract-Hop Scope and Current Lifecycle

This contract-only candidate modifies exactly these ten isolated-worktree
paths, in this order:

1. `docs/fractal_runtime_v0_2_g2_d_post_acceptance_contract_addendum_v01.md`
2. `tests/test_fractal_runtime_g2_d_v02.py`
3. `AGENTS.md`
4. `README.md`
5. `specs/machine_manifest_v0_25.json`
6. `release/current_status_overlay_v01.json`
7. `release/claim_to_evidence_index.md`
8. `release/current_limitations.md`
9. `release/current_release_notes.md`
10. `tests/test_repository_release_spine_v01.py`

The active contract-only lifecycle is exact:

```text
G2D_STATUS=CORRECTION_CONTRACT_ACCEPTED_IMPLEMENTATION_PENDING
G2D_IMPLEMENTATION_AUTHORIZED=false
G2D_CORRECTED_V039_IMPLEMENTATION_EXISTS=false
G2D_CONTRACT_ONLY_CLAIM=true
HISTORICAL_V038_G2D_STATUS=CLOSED_PASS_ON_V038_BYTES
G2E3_STATUS=IMPLEMENTED_COMMITTED_ACCEPTANCE_PASS_ON_V038_G2D
POST_V039_IMPLEMENTATION_G2E3_STATUS=REVALIDATION_PENDING_ON_CORRECTED_G2D
G2E4_STRICT_SUBTREE_STATUS=IMPLEMENTED_COMMITTED_PASS
G2E4_ANTI_GAMING_STATUS=BLOCKED_PENDING_G2D_V039_RECLOSURE
G2E5_STATUS=NOT_STARTED_NOT_AUTHORIZED
G2E6_STATUS=NOT_STARTED_NOT_AUTHORIZED
G2F_STATUS=NOT_STARTED_NOT_AUTHORIZED
GATE2_STATUS=NOT_CLOSED
```

Public release, RC2, production readiness, and production security
certification remain NOT_CLAIMED. The contract creates no implementation,
execution evidence, audit, checkpoint, reclosure, authority, permission,
FinalOutput, DRS write, successor baseline, provider/model/network/connector
operation, external DRS action, or real-world effect.

===============================================================================
HISTORICAL ACCEPTED V0.3.8 CONTENT - EXACT REPOSITORY BYTES
===============================================================================

The complete byte sequence below is the previously accepted v0.3.8 addendum.
It remains immutable historical contract and evidence context for v0.3.8. Its
embedded present-tense lifecycle statements do not override the active v0.3.9
metadata and clarification above.

# G2-D Post-Acceptance Contract Addendum Version 0.3.8

## Current Accepted v0.3.8 Clarification and Lifecycle Reopening Metadata

```text
document_status: POST_ACCEPTANCE_CORRECTION_ADDENDUM
document_revision: v0.3.8
guardian_review_status: ACCEPTED
directional_draft_sha256: 91264cc9f6177edc1779d3d7553b4ef4484d3db196900380a987b3ae0ccc1454
directional_draft_review: APPROVE_WITH_MANDATORY_OVERLAY
mandatory_overlay_integrated: true
controlling_design_v03_sha256: 7e32560ff19b95a8bd553072d855e8378d749c0f5d17861b7dee9a1f2577c4fe
repository_basis_branch: main
repository_basis_head: 0a741d20ebe9092685a1e1117da01438499168e5
repository_basis_origin_main: 0a741d20ebe9092685a1e1117da01438499168e5
repository_basis_subject: Correct G2-E4 strict selective subtree execution
V037_IMPLEMENTATION_NONCONFORMANCE: YES
V038_CONTRACT_SEMANTICS_CHANGED: NO
V038_ROLE: EXPLICIT_CLARIFICATION_AND_LIFECYCLE_REOPENING
current_g2d_status: CORRECTION_CONTRACT_ACCEPTED_IMPLEMENTATION_PENDING
implementation_authorized: false
implementation_started: false
current_g2e3_status: IMPLEMENTED_COMMITTED_ACCEPTANCE_PASS_ON_CORRECTED_G2D
current_g2e4_status: IMPLEMENTED_COMMITTED_STRICT_SUBTREE_PASS_ANTI_GAMING_ACCEPTANCE_BLOCKED
g2e5_status: NOT_STARTED_NOT_AUTHORIZED
g2e6_status: NOT_STARTED_NOT_AUTHORIZED
g2f_status: NOT_STARTED_NOT_AUTHORIZED
gate2_status: NOT_CLOSED
```

This accepted v0.3.8 overlay is an explicit clarification of already
controlling DESIGN_V03 semantics and an honest lifecycle reopening. It does
not invent or change the null-policy proof branch. The v0.3.7 implementation
failed to conform to the already controlling matrix, so its implementation,
execution evidence, independent re-audit, checkpoint, and closure remain
immutable historical evidence for their exact v0.3.7 bytes only.

This contract-only hop authorizes no implementation. It changes no G2-D
runtime, schema, demo, package facade, Transition Registry, G2-E runtime, or
behavior. A separate explicit owner action is required before future v0.3.8
implementation bytes may change.

## 1. Clarification and Nonconformance Boundary

The proof-based null-policy matrix was already controlling in DESIGN_V03.
Version v0.3.8 makes that law explicit, records current implementation
nonconformance, and reopens the G2-D lifecycle. The governing facts are exact:

```text
V037_IMPLEMENTATION_NONCONFORMANCE=YES
V038_CONTRACT_SEMANTICS_CHANGED=NO
V038_ROLE=EXPLICIT_CLARIFICATION_AND_LIFECYCLE_REOPENING
```

The historical v0.3.7 corrected implementation commit
`27c6dfd10740103cddc13bac3ce35f917b5f30c5`, independent re-audit commit
`2eccb604fee89d7e79025337d3858d6dbfea5fbc`, and reclosure commit
`48ab284ee7c1ba33400f0d0c7fe5656b4249b839` are not rewritten. Their evidence
does not certify future v0.3.8 implementation bytes.

## 2. Authority and Ownership Boundary

- Root remains the only final authority.
- G2-C owns the accepted Root-reviewed route.
- G2-D owns RuntimeExecutionTopology and stable topology-node and cell IDs.
- G2-E imports and calls only generic public G2-D seams.
- G2-D imports no G2-E type or module.
- PlanGraph remains historical and proof-donor material only.
- RuntimeObservedWorkContextV02, binding artifacts, bundles, traces, reports,
  hashes, tests, audits, and checkpoints create no authority.
- No successor baseline, permission, ActionCommitPacket, receipt, FinalOutput,
  DRS write, provider/model/network/connector authority, or real-world effect
  is created or claimed.

## 3. Local Binding Projector Responsibility

The future corrected observed-work binding projector validates only local
binding facts:

- exact baseline and observed source objects;
- exact topology, node, and cell witness for that binding;
- the local execution scope, reason, and policy triad;
- canonical payload, identity, parents, trace references, and zero-authority
  counters.

One binding artifact does not prove aggregate full closure. The local triad
matrix is exact.

### A. SELECTIVE

```text
execution_scope = SELECTIVE
whole_run_escalation_reason = None
whole_run_escalation_policy_id = None
```

### B. PROOF-BASED FULL CLOSURE

```text
execution_scope = WHOLE_RUN_ESCALATION
whole_run_escalation_reason = AFFECTED_CLOSURE_EQUALS_ALL_RECOMPUTABLE_WORK
whole_run_escalation_policy_id = None
```

### C. NAMED POLICY

```text
execution_scope = WHOLE_RUN_ESCALATION
whole_run_escalation_reason = FAIL_CLOSED_POLICY_REQUIRES_FULL_RECONSTRUCTION
whole_run_escalation_policy_id = an explicitly accepted policy ID
```

The accepted named-policy inventory is empty in v0.3.8. Every nonempty policy
ID therefore fails closed. A syntactically well-formed arbitrary string is not
an accepted policy.

Every other triad is invalid. In particular, SELECTIVE rejects either non-null
whole-run field; proof-based full closure rejects a non-null policy; and the
named-policy reason rejects a null, empty, whitespace, sentinel, malformed,
foreign, substituted, or unapproved policy.

## 4. Aggregate Closure Responsibility

Only aggregate RuntimeObservedWorkContextV02 validation, complete-bundle
validation, and public-run contextual validation may prove full closure. The
future corrected aggregate validators must independently derive, rather than
trust:

1. the validated baseline topology and recomputable universe;
2. direct affected node, cell, and artifact rows from actual validated source
   and binding evidence;
3. the parent-closed affected execution closure;
4. the complete recomputable node, cell, and artifact universe;
5. equality or strict inequality between those two sets.

The proof-based whole-run branch passes only when the independently derived
closure is exactly equal to every recomputable node, cell, and artifact in the
bounded baseline topology.

The following are forbidden substitutes for aggregate proof:

- manually supplying every topology ID;
- manually supplying every cell ID;
- `replace(plan)` accommodation;
- a specially crafted `full_plan` built only to satisfy a test;
- caller assertions that closure is complete;
- copied PASS, status, or reason values;
- a binding artifact claiming aggregate closure by itself.

## 5. Required Negative Matrix

Future implementation tests must execute and fail closed for every row below:

1. named-policy reason plus any nonempty but unapproved policy ID;
2. arbitrary or substituted reason;
3. arbitrary or substituted policy;
4. empty, whitespace, sentinel, or foreign policy ID;
5. forged closure;
6. missing closure member;
7. foreign node, cell, or artifact in the closure;
8. strict subset with WHOLE_RUN_ESCALATION;
9. full closure with SELECTIVE;
10. proof reason plus non-null policy;
11. named-policy reason plus null policy;
12. binding or context identity substitution;
13. a full ID inventory unsupported by actual source and binding evidence.

These tests must exercise public construction and validation. Source-text
inspection, caller-provided IDs, copied PASS labels, and manually fabricated
aggregate proof do not satisfy the matrix.

## 6. Identity Propagation and Complete-Bundle Law

For the proof-based branch, the exact reason and Python `None` policy must be
proven through the complete identity chain:

- every relevant binding artifact payload and identity;
- RuntimeObservedWorkContextV02 plain material and identity;
- queue, input, and result lineage where current public contracts bind the
  context;
- runtime trace identity and references;
- runtime report identity and references;
- report KernelArtifact identity, parent, and trace material;
- causal evidence and current trace binding;
- the complete publicly validated 28-field
  FractalRuntimeExecutionBundleV02.

The JSON diagnostic value is `null`. No hidden sentinel, empty string,
invented policy ID, or out-of-band sidecar may substitute for `None`.

No new public dataclass, serialized type, schema definition, reason,
validation target, failure stage, ABI literal, Transition rule, authority
field, or effect field is authorized by this contract.

## 7. Future Implementation Path and Lifecycle Ledger

The future separately authorized implementation correction is expected to
modify exactly these ten paths, in this order:

1. `hedgehog/kernel/fractal_runtime_v02.py`
2. `tests/test_fractal_runtime_g2_d_v02.py`
3. `AGENTS.md`
4. `README.md`
5. `specs/machine_manifest_v0_25.json`
6. `release/current_status_overlay_v01.json`
7. `release/claim_to_evidence_index.md`
8. `release/current_limitations.md`
9. `release/current_release_notes.md`
10. `tests/test_repository_release_spine_v01.py`

That implementation prompt may not change this contract addendum, the G2-D
schema, demo, Transition Registry, package facade, or any G2-E path. A proven
need for another path is a blocker and not implicit scope expansion.

The same future implementation commit must set the current lifecycle to:

```text
G2-D = REAUDIT_PENDING
G2-D corrected closure claimed = false
G2-D independent re-audit passed = false
G2-E3 = REVALIDATION_PENDING_ON_CORRECTED_G2D
G2-E4 anti-gaming acceptance = BLOCKED_PENDING_G2D_RECLOSURE
Gate 2 = NOT_CLOSED
```

This avoids a separate lifecycle synchronization hop.

The complete execution order is frozen:

1. v0.3.8 clarification and lifecycle-reopening contract hop;
2. owner contract review and separate contract commit and push;
3. separately authorized G2-D implementation correction;
4. complete bounded and cumulative evidence;
5. implementation commit with REAUDIT_PENDING status;
6. independent read-only re-audit on committed v0.3.8 bytes;
7. additive successor checkpoint, reclosure, and release synchronization;
8. corrected G2-D returns to CLOSED_PASS;
9. one fresh unchanged G2-E3 V06;
10. real G2-E4 whole-run anti-gaming correction;
11. real G2-E4 revise, exact-repeat/no-progress, partial-failure, and
    backpressure correction;
12. final separate G2-E4 corrective commit;
13. only then may G2-E5 be considered.

No reset, revert, amend, rebase, squash, or force-push is permitted.

## 8. G2-E4 Post-Reclosure Anti-Gaming Duty

After G2-D v0.3.8 implementation, evidence, re-audit, reclosure, and a fresh
unchanged G2-E3 V06, G2-E4 must be corrected in two behavioral areas:

1. whole-run selection must be reached from independently derived full
   affected closure through the normal E4 execution entry, not from a manually
   built full plan;
2. revise, exact-repeat/no-progress, partial-failure, and backpressure must
   execute real public G2-D operations and produce nonempty typed carriers.

Forbidden acceptance substitutes are callable-only checks, `hasattr`-only
checks, function-name searches in source text, uniqueness assertions over
empty tuples, manual PASS objects, skip or xfail, weakened strict-subtree or
sibling-preservation assertions, and test-only projections replacing runtime
behavior.

## 9. Current Lifecycle and Nonclaims

Current accepted state after this contract-only hop is exact:

```text
G2D_STATUS=CORRECTION_CONTRACT_ACCEPTED_IMPLEMENTATION_PENDING
G2D_IMPLEMENTATION_AUTHORIZED=false
G2D_IMPLEMENTATION_STARTED=false
G2E3_STATUS=IMPLEMENTED_COMMITTED_ACCEPTANCE_PASS_ON_CORRECTED_G2D
G2E4_STATUS=IMPLEMENTED_COMMITTED_STRICT_SUBTREE_PASS_ANTI_GAMING_ACCEPTANCE_BLOCKED
G2E5_STATUS=NOT_STARTED_NOT_AUTHORIZED
G2E6_STATUS=NOT_STARTED_NOT_AUTHORIZED
G2F_STATUS=NOT_STARTED_NOT_AUTHORIZED
GATE2_STATUS=NOT_CLOSED
```

Historical v0.3.7 implementation, execution evidence, independent re-audit,
checkpoint, and closure remain immutable evidence for their exact bytes only.
This contract claims no v0.3.8 implementation, execution evidence, audit,
checkpoint, reclosure, G2-E5, G2-E6, G2-F, Gate-2 closure, public release, RC2,
production readiness, production security, authority, permission, FinalOutput,
DRS write, successor baseline, provider/model/network/connector operation, or
real-world effect.

===============================================================================
HISTORICAL ACCEPTED V0.3.7 CONTENT - EXACT REPOSITORY BYTES
===============================================================================

The complete byte sequence below is the previously accepted v0.3.7 addendum.
It remains immutable historical contract and evidence context for v0.3.7. Its
embedded present-tense lifecycle statements do not override the active v0.3.8
metadata and clarification above.

# G2-D Post-Acceptance Contract Addendum Version 0.3.7

## Current Accepted v0.3.7 Correction Metadata

```yaml
document_status: POST_ACCEPTANCE_CORRECTION_ADDENDUM
document_revision: v0.3.7
guardian_review_status: ACCEPTED
guardian_accepted_v037_pending_draft_sha256: 8801e413f93765cc7059ce5e03e82e881b20cfd193f12551a60a0b90920bb63d
applies_to_preflight: docs/fractal_runtime_v0_2_g2_d_preflight_v01.md
applies_to_preflight_sha256: 8e3ae3b04a9b622329e85529edb8a150739cc787b341f1609438dbde00412e79
accepted_v036_basis_revision: v0.3.6
accepted_v036_basis_sha256: 7e3a9039e04a7ef2b20cd69ac442ad62c073e88d7d3b93c26f35b48b18d67570
repository_basis_branch: main
repository_basis_head: 7fef8617cdde0e8202e892414591c1726fa16cbc
repository_basis_origin_main: 7fef8617cdde0e8202e892414591c1726fa16cbc
repository_basis_subject: Implement G2-E3 source context, invalidation, and preservation
controlling_design_v03_sha256: 7e32560ff19b95a8bd553072d855e8378d749c0f5d17861b7dee9a1f2577c4fe
controlling_full_consumer_closure_decision_sha256: 69981a3547357b167ea3c260da145038b6b38a1726a910bbd8fd78b1fd46a794
original_constructibility_register_sha256: a5c7c98c5d04382ab704dcd5f8e42cbeb06aac8bfa7b4777d771d01155527c7a
blocker_id: BLOCKER_E4C_001
guardian_direction: OPTION_1
current_g2d_status: CORRECTION_CONTRACT_ACCEPTED_IMPLEMENTATION_PENDING
historical_precorrection_g2d_status: CLOSED_PASS_ON_PRECORRECTION_BYTES
current_g2e3_status: IMPLEMENTED_COMMITTED_ACCEPTANCE_PASS_ON_PRECORRECTION_G2D
post_corrected_g2d_landing_g2e3_status: REVALIDATION_PENDING_ON_CORRECTED_G2D
g2e4_status: NOT_STARTED_NOT_AUTHORIZED
gate2_status: NOT_CLOSED
implementation_authorized: false
implementation_started: false
contract_hop_completed: true
implementation_repository_patch_created: false
codex_implementation_prompt_prepared: false
```

This guardian-accepted v0.3.7 correction overlay controls only the narrow
BLOCKER_E4C_001 contract correction defined below. It is integrated through a
contract-only repository hop and grants no implementation, staging, commit,
push, G2-E4, G2-E5, G2-E6, or G2-F authority.

Accepted v0.3.6 and every older accepted addendum remain immutable historical
authority for every unaffected ruling. The G2-D preflight remains byte-identical
and controlling outside this narrow correction boundary. The complete accepted
v0.3.6 repository addendum bytes are retained verbatim in the historical section
at the end of this file.

The accepted external decision
`HEDGEHOG_G2E4_BLOCKER_E4C_001_V03_FULL_CONSUMER_CLOSURE_DECISION_V01.txt`,
SHA-256 `69981a3547357b167ea3c260da145038b6b38a1726a910bbd8fd78b1fd46a794`,
is the controlling architectural and consumer-closure overlay incorporated by
this contract. The exact accepted normative donor for this v0.3.7 overlay is
SHA-256 `8801e413f93765cc7059ce5e03e82e881b20cfd193f12551a60a0b90920bb63d`.

===============================================================================
2. AUTHORITY, SUPERSESSION, AND NON-AUTHORITY BOUNDARY
===============================================================================

The controlling hierarchy remains:

1. current explicit owner/guardian instruction;
2. current exact Git facts;
3. accepted G2-E preflight and addendum where they define the consumer duty;
4. accepted G2-D preflight, accepted v0.3.6 addendum, and accepted v0.3.7;
5. frozen G2-A, G2-B, G2-C, Root, ABI, Post V&V, GT, Semantic Work, Trust, and
   other compatible constitutional project surfaces;
6. roadmap v3.1 for execution order;
7. roadmap v2.1 for technical inventory;
8. historical demos, tests, audits, checkpoints, and PlanGraph material only as
   explicitly classified evidence or donors.

The correction preserves exactly:

- Root is the only final authority.
- G2-C owns the current Root-reviewed route.
- G2-D owns the runtime topology and stable topology-node IDs.
- RuntimeExecutionTopology, child cells, result proposals, Post V&V, GT,
  reports, traces, hashes, audit outputs, and this document create no authority.
- G2-D imports no G2-E type or module.
- G2-E later projects its typed carriers into one generic G2-D boundary.
- PlanGraph remains historical/proof-donor material only. No adapter, migration,
  compatibility workstream, or provider-owned topology is created.
- Baseline G2-C and G2-D objects remain immutable.
- No successor baseline, permission, ActionCommitPacket, receipt, FinalOutput,
  DRS write, provider authority, connector authority, effect handle, or real-
  world effect is created.
- Post V&V validates. GT advises. Neither decides.

Option 2 is rejected: byte-identical deterministic replay is not recomputation.
Option 3 remains the existing fail-closed route-change boundary and is not the
normal positive G2-E4 path.

===============================================================================
3. BLOCKER AND ACCEPTED CORRECTION DIRECTION
===============================================================================

BLOCKER_E4C_001 is exact:

The pre-correction public G2-D surface has no public input through which actual
observed G2-E source material can enter G2-D content-derived execution
identities. With the exact baseline FractalRuntimeSourceContextV02 and topology,
the public runtime reconstructs the same source-bound material. That cannot
simultaneously prove actual observed-source execution, a genuinely recomputed
bundle, new recomputed artifact identities, and rejection of in-place
recomputation.

The accepted v0.3.7 correction contract is:

    actual baseline/observed KernelArtifactV01 source objects
    -> generic observed-work binding KernelArtifactV01 objects
    -> one frozen runtime-only RuntimeObservedWorkContextV02
    -> context-aware t02 initial queue parent envelope
    -> context-aware settled-prefix reconstruction
    -> FractalCellInputV02 evidence/context identity
    -> queue/result/Post-V&V/GT/trace/report/causal identity chain
    -> complete publicly validated FractalRuntimeExecutionBundleV02

KernelArtifactV01 remains the canonical identity/evidence carrier. No new
serialized observed-work binding dataclass is introduced. Exactly one new
runtime-only aggregate type is required to prevent split-brain pairing between
separately supplied source and binding tuples.

===============================================================================
4. RUNTIME-ONLY TYPE, CONTEXT IDENTITY, AND BUNDLE FIELD
===============================================================================

4.1 New runtime-only type

Append exactly one public frozen runtime-only dataclass after the existing
FractalRuntimeExecutionBundleV02 definition. The former 20-type prefix remains
exact.

```python
@dataclass(frozen=True)
class RuntimeObservedWorkContextV02:
    observed_work_context_id: str
    context_version: str
    context_profile_id: str
    baseline_execution_bundle: FractalRuntimeExecutionBundleV02
    baseline_bundle_anchor_sha256: str
    runtime_source_binding_id: str
    topology_id: str
    topology_artifact_id: str
    baseline_runtime_trace_id: str
    baseline_runtime_report_id: str
    baseline_report_artifact_id: str
    execution_scope: str
    whole_run_escalation_reason: str | None
    whole_run_escalation_policy_id: str | None
    ordered_direct_affected_node_ids: tuple[str, ...]
    ordered_execution_node_ids: tuple[str, ...]
    ordered_affected_cell_ids: tuple[str, ...]
    ordered_direct_source_artifacts: tuple[KernelArtifactV01, ...]
    ordered_supporting_artifacts: tuple[KernelArtifactV01, ...]
    ordered_binding_artifacts: tuple[KernelArtifactV01, ...]
    root_review_required: bool
    provider_calls: int
    model_calls: int
    network_calls: int
    connector_calls: int
    external_drs_calls: int
    authority_created: bool
    permission_created: bool
    action_commit_packet_created: bool
    receipt_created: bool
    final_output_created: bool
    drs_write_created: bool
    real_world_effects_count: int
```

Constants are exact:

```text
context_version = v0.2
context_profile_id = fractal_runtime_observed_work_context_v02
observed_work_context_id prefix = frobservedctx_v02:
identity domain = HEDGEHOG_FRACTAL_RUNTIME_V02_OBSERVED_WORK_CONTEXT
execution_scope in {SELECTIVE, WHOLE_RUN_ESCALATION}
```

The context is runtime-only. It is not serialized by
schemas/fractal_runtime_v02.schema.json, is not a new ABI artifact literal, is
not a Root object, is not a topology owner, is not an authority layer, and is
not a successor baseline.

4.2 Baseline anchor

baseline_execution_bundle must pass the public complete-bundle validator and
must itself have observed_work_context is None. It is immutable prior evidence.

baseline_bundle_anchor_sha256 is not repr, asdict, object identity, or a hidden
registry value. It is the domain-separated SHA-256 of one canonical public
observation containing the exact current G2-C proposal/decision/route IDs and
artifact hashes; Root input/result/decision artifact IDs; runtime policy and
source-binding IDs; topology seed/topology/artifact IDs; ordered budgets,
nodes, edges, assignments, queue entries/artifacts, scopes, inputs, revise,
partial failure, backpressure, validation, proposal, Post V&V, GT, result and
result-artifact identities; runtime trace/report/report-artifact identities;
Transition decisions; and public plain causal-ref mappings.

The context identity is:

```python
observed_work_context_id = (
    "frobservedctx_v02:"
    + domain_separated_sha256_hex_v01(
        domain="HEDGEHOG_FRACTAL_RUNTIME_V02_OBSERVED_WORK_CONTEXT",
        payload=canonical_json_bytes_v01(
            runtime_observed_work_context_to_plain_data_v02(context_without_id)
        ),
    )
)
```

The plain projection replaces the full baseline bundle object with the exact
baseline anchor and projects each KernelArtifactV01 through the public Kernel
ABI plain-data seam. All mappings are canonicalized lexicographically and all
ordered artifact families use the canonical ordering laws in Section 8.
Equivalent input sets in different caller order yield the same context ID.

4.3 Bundle field

Append exactly one trailing defaulted runtime-only field:

```python
observed_work_context: RuntimeObservedWorkContextV02 | None = None
```

The historical source-compatible call remains:

```python
run_fractal_runtime_v02(source_context)
```

Raw Python dataclass repr, asdict output, field enumeration, and E3 observation
digests are not promised byte-stable after this field is added.

===============================================================================
5. GENERIC OBSERVED-WORK BINDING ARTIFACT
===============================================================================

5.1 Carrier and public projector

The binding is an ordinary KernelArtifactV01:

```text
artifact_type = ValidatedEvidence
lifecycle_state = VALIDATED
authority_class = EVIDENCE_ONLY
source_component = fractal_runtime_v02
artifact_id prefix = frobservedwork_v02:
identity domain = HEDGEHOG_FRACTAL_RUNTIME_V02_OBSERVED_WORK_BINDING_ARTIFACT
```

No new generic Kernel ABI literal, KernelArtifact schema definition, authority
class, or G2-D Transition rule is introduced.

The public projector is exact:

```python
project_runtime_observed_work_binding_kernel_artifact_v02(
    *,
    baseline_execution_bundle: FractalRuntimeExecutionBundleV02,
    node: RuntimeTopologyNodeV02,
    cell_input: FractalCellInputV02,
    baseline_source_artifact: KernelArtifactV01,
    observed_source_artifact: KernelArtifactV01,
    changed_full_artifact_pointers: tuple[str, ...],
    execution_scope: str,
    whole_run_escalation_reason: str | None = None,
    whole_run_escalation_policy_id: str | None = None,
) -> KernelArtifactV01
```

The function accepts no caller-selected cell ID, parent cell ID, child index,
depth, scope projection, activation witness, identity, status, or PASS label.
Those facts are recovered from the publicly valid baseline bundle and exact
carried node/input objects.

5.2 Parent order

Root-cell binding parents:

```text
topology artifact
baseline source artifact
observed source artifact
```

Child-cell binding parents:

```text
topology artifact
baseline source artifact
observed source artifact
baseline activation-parent queue artifact
```

5.3 Canonical payload

The exact top-level payload key set is, in ABI-canonical lexicographic order:

```text
change_proof
execution
profile
safety
source_pair
topology_binding
```

Exact nested key sets are:

```text
profile:
  binding_profile_id
  binding_version
  canonicalization_profile_id

execution:
  execution_scope
  whole_run_escalation_policy_id
  whole_run_escalation_reason

safety:
  action_commit_packet_created
  authority_created
  connector_calls
  drs_write_created
  external_drs_calls
  final_output_created
  model_calls
  network_calls
  permission_created
  provider_calls
  real_world_effects_count
  receipt_created

source_pair:
  baseline_envelope_sha256
  baseline_identity_ref
  baseline_payload_sha256
  baseline_schema_version_value
  baseline_source_component_id
  baseline_type
  bound_domain_id
  bound_owner_root_id
  bound_transaction_id
  observed_envelope_sha256
  observed_identity_ref
  observed_parent_refs
  observed_payload_sha256
  observed_schema_version_value
  observed_source_component_id
  observed_type
  predecessor_relation

topology_binding:
  activation_parent_queue_artifact_ref
  assignment_ref
  baseline_cell_input_ref
  canonical_child_index
  cell_depth
  cell_ref
  node_ref
  parent_cell_ref
  runtime_source_binding_ref
  scope_projection_ref
  topology_artifact_ref
  topology_ref
  witness_class

change_proof:
  all_full_artifact_changed_pointers
  consumed_changed_material_rows
  whole_artifact_expanded
  whole_payload_expanded

consumed_changed_material_rows item:
  baseline_present
  baseline_value_sha256
  full_artifact_pointer
  observed_present
  observed_value_sha256
  payload_pointer
```

Mappings are canonicalized lexicographically at every level. No insertion order
is a contract. No KernelArtifact envelope-reserved key is duplicated as a
payload top-level key.

5.4 Source-pair and pointer law

Both source artifacts must pass the public Kernel ABI and preserve exact
abi_version, artifact_type, schema_version, transaction ID, owner Root, and
authority class. The observed artifact must differ from the baseline, carry the
baseline artifact ID exactly once as predecessor, remain parent-closed, and
create no authority or effect.

G2-E full-artifact RFC-6901 pointers and G2-D payload-relative pointers remain
separate:

- /payload/x normalizes to payload-relative /x;
- /payload expands to the actual differing nonempty payload leaf pointers;
- the empty full-artifact pointer expands to all actual differing permissible
  nonempty full-artifact leaf pointers;
- envelope changes retain their full-artifact pointers and have payload_pointer
  null;
- /artifact_id is only a derived identity consequence;
- changes to abi_version, artifact_type, schema_version, transaction_id,
  owner_root_id, or authority_class fail closed;
- changes to payload, time_envelope, trace_refs, parent_refs, lifecycle_state,
  and source_component remain supported when every hard boundary, predecessor,
  parent-closure, and changed-material law passes;
- no empty CausalConsumptionRef output_field is introduced.

===============================================================================
6. STABLE ROOT/CHILD WITNESS AND SELECTIVE EXECUTION SCOPE
===============================================================================

The projector first proves node and cell_input are exact baseline bundle
members.

Root witness requires parent_cell_id is None, cell_id equals topology.root_cell_id,
depth zero, no scope projection, public root-cell identity reconstruction, and
witness_class BASELINE_ROOT_CELL_INPUT.

Child witness requires:

1. exactly one baseline parent FractalCellInputV02;
2. exactly one child occurrence in parent_input.ordered_planned_child_cell_ids;
3. tuple position as canonical_child_index;
4. exact public ParentChildScopeProjectionV02 validation;
5. exact baseline parent FRACTAL_CELL running queue artifact naming the child;
6. exact baseline child initial queue artifact naming that activation parent;
7. public derive_fractal_child_cell_id_v02 reconstruction from topology seed,
   parent, canonical index, accepted mode, local profile, profile set, scope,
   policy, required capabilities, forbidden claims, and depth;
8. exact equality with the carried child cell ID;
9. witness_class BASELINE_CHILD_ACTIVATION_INPUT.

ordered_direct_affected_node_ids are exact bound topology nodes.
ordered_affected_cell_ids are exact baseline cells containing those nodes.
ordered_execution_node_ids are the minimal frozen topology dependency/control
closure required to execute affected cells through ResultProposal, Post V&V,
GT, and PARENT_RETURN.

Unselected sibling cells are not admitted. Required ancestor/return closure may
execute only when the existing topology and control-dependency law requires it.
Baseline queue, budget, input, result, trace, report, and artifact objects are
never mutated or reissued as new outputs.

===============================================================================
7. PUBLIC API AND SIGNATURE CORRECTIONS
===============================================================================

7.1 Six new public functions

The corrected module adds exactly:

```text
1. project_runtime_observed_work_binding_kernel_artifact_v02
2. build_runtime_observed_work_context_v02
3. validate_runtime_observed_work_context_v02
4. runtime_observed_work_context_to_plain_data_v02
5. validate_runtime_observed_work_context_against_sources_v02
6. validate_runtime_observed_work_counterfactual_v02
```

The context API signatures are:

```python
build_runtime_observed_work_context_v02(
    *,
    baseline_execution_bundle: FractalRuntimeExecutionBundleV02,
    direct_source_artifacts: tuple[KernelArtifactV01, ...],
    supporting_artifacts: tuple[KernelArtifactV01, ...],
    binding_artifacts: tuple[KernelArtifactV01, ...],
    execution_scope: str,
    whole_run_escalation_reason: str | None = None,
    whole_run_escalation_policy_id: str | None = None,
) -> RuntimeObservedWorkContextV02

validate_runtime_observed_work_context_v02(
    value: object,
) -> FractalRuntimeValidationReportV02

runtime_observed_work_context_to_plain_data_v02(
    value: RuntimeObservedWorkContextV02,
) -> dict[str, object]

validate_runtime_observed_work_context_against_sources_v02(
    value: object,
    *,
    baseline_execution_bundle: FractalRuntimeExecutionBundleV02,
    direct_source_artifacts: tuple[KernelArtifactV01, ...],
    supporting_artifacts: tuple[KernelArtifactV01, ...],
    binding_artifacts: tuple[KernelArtifactV01, ...],
) -> FractalRuntimeValidationReportV02

validate_runtime_observed_work_counterfactual_v02(
    *,
    execution_bundle: FractalRuntimeExecutionBundleV02,
    observed_work_causal_ref: CausalConsumptionRefV01,
    mutated_observed_source_artifact: KernelArtifactV01,
) -> FractalRuntimeValidationReportV02
```

7.2 Thirteen additive signature corrections

Append the same optional keyword-only parameter to exactly these existing public
functions, preserving every former parameter and return type:

```python
observed_work_context: RuntimeObservedWorkContextV02 | None = None
```

Exact function set:

```text
admit_runtime_execution_topology_v02
advance_fractal_cell_queue_v02
build_fractal_cell_input_from_queue_v02
validate_fractal_cell_input_against_sources_v02
evaluate_fractal_backpressure_v02
project_fractal_cell_queue_entry_kernel_artifact_v02
evaluate_fractal_runtime_state_transition_v02
validate_fractal_runtime_stage_bundle_v02
validate_fractal_runtime_abi_profile_v02
build_fractal_runtime_causal_consumption_refs_v02
validate_fractal_runtime_causal_consumption_refs_v02
build_fractal_runtime_execution_bundle_v02
run_fractal_runtime_v02
```

The exact full signatures are the current committed signatures at repository
basis 7fef8617cdde0e8202e892414591c1726fa16cbc plus only this trailing
keyword-only parameter. The exact complete signature ledger in controlling
decision SHA-256
69981a3547357b167ea3c260da145038b6b38a1726a910bbd8fd78b1fd46a794
is incorporated without alteration.

validate_fractal_runtime_execution_bundle_v02 retains its public signature and
reads value.observed_work_context. The historical
validate_fractal_runtime_causal_counterfactual_v02 signature remains unchanged.
No other public signature changes without a new guardian blocker and ruling.

Private propagation is limited to the shared runtime implementation:
_d3_validate_settled_runtime_prefix_v02, _d4_run_runtime_v02,
_d4_initialize_runtime_state_v02, _d4_prefix_kwargs_v02, _d4_indexes_v02, and
state-owned helpers that inherit one validated context value. E4 never imports
or calls a private G2-D helper.

===============================================================================
8. CANONICAL INVENTORIES, PARENT CLOSURE, AND STAGE-D PARTITIONS
===============================================================================

Direct source inventory contains each unique baseline/observed pair exactly once
in first-binding canonical order, baseline immediately followed by observed.
Multiple changed-material rows for one source pair do not duplicate that pair.

Supporting artifacts contain only ancestors required to close direct sources,
bindings, topology, and activation witnesses and exclude all direct-source and
binding identities.

Binding order is topology node order, then cell depth, cell ID, baseline source
ID, observed source ID, then canonical changed-pointer tuple.

Supporting closure uses deterministic Kahn topological order, parent before
child, with artifact_id lexical tie-break among simultaneously ready nodes.
Duplicate-equal objects may coalesce by artifact ID only in the parent-closed
union. Duplicate-unequal, omitted, foreign, self-parent, or cyclic material
fails closed.

Three maps are exact:

```text
stage_artifact_by_id
  existing Stage-D topology/queue/result/report artifacts only

input_evidence_artifact_by_id
  direct baseline/observed sources, support-only ancestors, binding artifacts

parent_closed_artifact_by_id
  exact union of Stage-D, input evidence, and exact carried G2-C ancestry
```

runtime_trace.abi_artifact_refs retains its existing queue/result ABI meaning.
Observed-work artifacts are not inserted into it. Stage-D A/B/C tuple
cardinalities remain unchanged. Generic validate_kernel_artifact_bundle_v01 is
called only after contextual proof that the supplied family is parent-closed.

===============================================================================
9. T02 PARENT ENVELOPES AND SETTLED-PREFIX RECONSTRUCTION
===============================================================================

No queue parser may classify an artifact from len(parent_refs) alone. Parent
forms are selected by Transition rule plus queue payload predecessor/state/cell
facts.

Exact t02 initial forms:

```text
INITIAL_ROOT_HISTORICAL
  payload: predecessor None; prior_state None; INITIAL_NONE; parent_cell None
  parents: topology artifact

INITIAL_CHILD_HISTORICAL
  payload: predecessor None; prior_state None; INITIAL_NONE; parent_cell non-None
  parents: topology artifact, activation-parent queue artifact

INITIAL_ROOT_OBSERVED_WORK
  same root initial payload
  parents: topology artifact, one-or-more canonical binding artifacts

INITIAL_CHILD_OBSERVED_WORK
  same child initial payload
  parents: topology artifact, activation-parent queue artifact,
           one-or-more canonical binding artifacts
```

Successor forms retain their historical predecessor/result parent law. A
three-parent successor may mean result introduction and must never be confused
with a context initial form merely because the cardinality is three.

Transition Registry structural validation recognizes exact disjoint historical
and context t02 envelopes, exact leading parent roles, nonempty unique digest
suffixes, and no suffix on historical forms. It does not validate actual binding
objects.

Runtime contextual validation independently receives RuntimeObservedWorkContextV02,
resolves every suffix ID to an exact binding artifact, checks canonical order and
exact node/cell mapping, and rejects missing, foreign, reordered, duplicated,
wrong-cell, wrong-node, mixed historical/context, or unconsumed bindings.

The shared settled-prefix reconstruction receives the optional context and must
rebuild both queue artifacts and FractalCellInputV02 values with the same
context. Every public caller that cannot recover the context from an already
validated aggregate passes it explicitly. Complete-bundle validation and D4
state indexes use the one context stored in the bundle/state. No hidden string-
only sidecar lineage is accepted.

The Transition Registry t02 parent-envelope profile is narrowly extended while
all 17 rule identities, transition authorities, source/target classes, and
historical None-path decisions remain exact. Structural prefix parsing and
contextual binding-object validation remain separate layers.

===============================================================================
10. CAUSAL ROWS AND COUNTERFACTUAL SEMANTICS
===============================================================================

10.1 Causal effects

Append exactly two G2-D-local causal decision effects:

```text
OBSERVED_WORK_INPUT
OBSERVED_WORK_CELL_BINDING
```

The generic ABI remains unchanged.

For each consumed changed-material row, emit binding-to-initial-queue USED rows:

```text
source_artifact_id = binding artifact ID
output_field = /change_proof/consumed_changed_material_rows/{index}/observed_value_sha256
downstream_artifact_id = exact directly bound initial queue artifact ID
decision_effect = OBSERVED_WORK_INPUT
disposition = USED
reason_code = used:g2d_observed_work_input
```

Cell binding row:

```text
output_field = /topology_binding/node_ref
decision_effect = OBSERVED_WORK_CELL_BINDING
disposition = USED
reason_code = used:g2d_observed_work_cell_binding
```

Observed-envelope row:

```text
output_field = /source_pair/observed_envelope_sha256
decision_effect = OBSERVED_WORK_INPUT
disposition = USED
reason_code = used:g2d_observed_work_envelope
```

The binding artifact is an actual parent of the queue artifact, so generic
causal bundle validation can prove the relation. Source-to-binding predecessor
and full-byte proof remains a separate contextual law because generic causal
pointers are payload-relative.

10.2 Historical counterfactual seam

The existing public function remains semantically unchanged:

```python
validate_fractal_runtime_causal_counterfactual_v02(
    *,
    execution_bundle: FractalRuntimeExecutionBundleV02,
    causal_ref: CausalConsumptionRefV01,
    mutated_source_artifact: KernelArtifactV01,
) -> FractalRuntimeValidationReportV02
```

causal_ref.source_artifact_id and mutated_source_artifact always refer to the
same exact historical Stage-D causal source. Observed-work rows passed to this
function fail closed with g2d_causal_counterfactual_mismatch.

10.3 Separate observed-work counterfactual seam

validate_runtime_observed_work_counterfactual_v02 accepts only an exact bundle
member causal row with disposition USED, effect OBSERVED_WORK_INPUT, reason
used:g2d_observed_work_input, exact binding-artifact source, exact initial queue
downstream, and exact changed-material output pointer. Caller-created,
historical, cell-binding-only, aggregate-envelope-only, ignored, rejected, or
unrelated blocked rows are ineligible.

The seam publicly validates the original bundle/context; resolves all objects
from that context; validates the mutated source; preserves hard ABI/transaction/
Root/authority boundaries and parent closure; permits only the selected full-
artifact leaf changes plus derived identity; rebuilds source inventory,
bindings, context, affected selective execution, t02 lineage, input, queue,
budgets, ResultProposal, Post V&V, advisory GT, result, parent return, trace,
report, artifacts and causal refs; validates the complete counterfactual bundle;
and proves every unaffected object remains equal.

A valid mutation stopped by an accepted gate may return a PASS validation report
proving BLOCKED_BY_GATE evidence and no accepted counterfactual bundle. Every
malformed, wrong-row, wrong-pointer, substituted, unclosed, cyclic, authority-
claiming, effect-claiming, or identity-incoherent case returns FAIL_CLOSED with
g2d_causal_counterfactual_mismatch.

10.4 Existing target/stage

The seam reuses:

```text
validation_target = CAUSAL_COUNTERFACTUAL
failure_stage = CAUSAL_COUNTERFACTUAL
```

No new reason, target, failure stage, serialized type, ABI literal, Transition
rule, or authority class is introduced by the counterfactual seam.

10.5 Required identity changes

USED PASS requires identity changes at the exact binding artifact, observed-work
context, directly bound initial queue artifact, affected cell input, affected
result artifact, runtime trace, runtime report, and report artifact. Route,
runtime source binding, topology seed/nodes/edges/assignments, topology ID,
topology artifact, and every unaffected preserved object remain equal.

10.6 Exact validated_object_id identity law

This subsection is an explicit v0.3.7 guardian precision and is normative.

The successful FractalRuntimeValidationReportV02 returned by
validate_runtime_observed_work_counterfactual_v02 has:

```text
validation_target = CAUSAL_COUNTERFACTUAL
failure_stage = NONE
status = PASS
validated_object_id prefix = frcounterfactual_v02:
validated_object_id domain = HEDGEHOG_FRACTAL_RUNTIME_V02_OBSERVED_WORK_COUNTERFACTUAL
```

The exact ID is:

```python
validated_object_id = (
    "frcounterfactual_v02:"
    + domain_separated_sha256_hex_v01(
        domain=(
            "HEDGEHOG_FRACTAL_RUNTIME_V02_"
            "OBSERVED_WORK_COUNTERFACTUAL"
        ),
        payload=canonical_json_bytes_v01(counterfactual_identity_material),
    )
)
```

counterfactual_identity_material is one exact four-key mapping. Canonical JSON
sorts every mapping lexicographically; tuple families project as lists in the
exact validated canonical order.

```text
baseline
candidate
preserved
profile
```

Exact nested material:

```python
counterfactual_identity_material = {
    "baseline": {
        "affected_cell_input_ids": [
            ... exact current affected cell-input IDs in context order ...
        ],
        "affected_result_artifact_ids": [
            ... exact current affected result-artifact IDs in result order ...
        ],
        "binding_artifact_ids": [
            ... execution_bundle.observed_work_context binding IDs ...
        ],
        "direct_initial_queue_artifact_ids": [
            ... exact directly bound initial queue artifact IDs ...
        ],
        "observed_work_context_id": (
            execution_bundle.observed_work_context.observed_work_context_id
        ),
        "report_artifact_id": execution_bundle.report_artifact.artifact_id,
        "runtime_report_id": execution_bundle.runtime_report.report_id,
        "runtime_trace_id": execution_bundle.runtime_trace.trace_id,
    },
    "candidate": {
        "affected_cell_input_ids": [
            ... rebuilt affected cell-input IDs in the same context order ...
        ],
        "affected_result_artifact_ids": [
            ... rebuilt affected result-artifact IDs in result order ...
        ],
        "binding_artifact_ids": [
            ... rebuilt binding artifact IDs in canonical binding order ...
        ],
        "blocked_by_gate_causal_refs": [
            ... exact public plain BLOCKED_BY_GATE refs in canonical causal order ...
        ],
        "counterfactual_disposition": "USED" | "BLOCKED_BY_GATE",
        "direct_initial_queue_artifact_ids": [
            ... rebuilt directly bound initial queue artifact IDs ...
        ],
        "mutated_observed_source_artifact": (
            kernel_artifact_to_plain_dict_v01(
                mutated_observed_source_artifact
            )
        ),
        "observed_work_causal_ref": (
            causal_consumption_ref_to_plain_dict_v01(
                observed_work_causal_ref
            )
        ),
        "observed_work_context_id": rebuilt_context.observed_work_context_id,
        "report_artifact_id": rebuilt_report_artifact_id_or_none,
        "runtime_report_id": rebuilt_runtime_report_id_or_none,
        "runtime_trace_id": rebuilt_runtime_trace_id_or_none,
    },
    "preserved": {
        "ordered_unaffected_artifact_ids": [
            ... exact unaffected IDs in parent-closed canonical order ...
        ],
        "route_eligibility_artifact_id": (
            execution_bundle.source_context.route_eligibility_artifact.artifact_id
        ),
        "runtime_source_binding_id": execution_bundle.source_binding.source_binding_id,
        "topology_artifact_id": execution_bundle.topology_artifact.artifact_id,
        "topology_id": execution_bundle.topology.topology_id,
    },
    "profile": {
        "counterfactual_profile_id": (
            "fractal_runtime_observed_work_counterfactual_v02"
        ),
        "counterfactual_profile_version": "v0.2",
        "validation_target": "CAUSAL_COUNTERFACTUAL",
    },
}
```

USED PASS shape is exact:

- counterfactual_disposition is USED;
- blocked_by_gate_causal_refs is empty;
- rebuilt runtime_trace_id, runtime_report_id, and report_artifact_id are
  nonempty and resolve to the publicly valid counterfactual complete bundle;
- every required identity-delta and preservation assertion passes.

BLOCKED_BY_GATE PASS shape is exact:

- counterfactual_disposition is BLOCKED_BY_GATE;
- blocked_by_gate_causal_refs is nonempty and every row is publicly valid,
  context-derived, and canonical;
- no accepted counterfactual bundle is produced;
- candidate runtime_trace_id, runtime_report_id, and report_artifact_id are null;
- binding/context reconstruction and the exact gate proof pass;
- zero authority/effect law remains exact.

The material never contains the returned validation report ID or
validated_object_id itself, so the identity graph is acyclic. The existing
FractalRuntimeValidationReportV02 builder derives its own validation_report_id
only after this validated_object_id is frozen.

Every failure report has validated_object_id is None under the existing
_d4_contextual_report_v02 fail-closed law. The historical counterfactual seam
retains its existing prefix/domain/material unchanged:

```text
prefix = frcounterfactual_v02:
domain = HEDGEHOG_FRACTAL_RUNTIME_V02_CAUSAL_COUNTERFACTUAL
```

===============================================================================
11. APPEND-ONLY TARGET, SCHEMA, GEOMETRY, AND FACADE LAW
===============================================================================

Append OBSERVED_WORK_BINDINGS_AGAINST_SOURCES strictly after the complete former
34-entry VALIDATION_TARGETS prefix. It is target 35, after COMPLETE_PROFILE.

Append the contextual row strictly after the former complete prefix:

```python
(
    "OBSERVED_WORK_BINDINGS_AGAINST_SOURCES",
    "frobservedctx_v02:",
    "SOURCE_BINDING",
)
```

Append the same literal to the end of the exact schema enum. Do not insert it at
an interior location. G2-D schema definitions remain 18. G2-E schema and the
generic KernelArtifact schema remain byte-frozen.

Final accepted corrected geometry contract is exact:

```text
public G2-D dataclass types:              20 -> 21
serialized types:                         18 -> 18
runtime-only types:                         2 -> 3
schema definitions:                       18 -> 18
canonical-module public functions:       110 -> 116
Transition-profile public functions:       6 -> 6
total G2-D public functions:              116 -> 122
direct hedgehog.kernel package attrs:     136 -> 143
public reason codes:                      220 -> 220
validation targets:                        34 -> 35
failure stages:                            30 -> 30
Transition rules:                          17 -> 17
G2-D-local causal decision effects:        12 -> 14
FractalRuntimeExecutionBundleV02 fields:   27 -> 28
G2-D test function nodes:                  75 -> 83
G2-D collected pytest items:               84 -> 92
Transition test function nodes:            60 -> 60
Transition collected pytest items:        268 -> 268
D5 cases:                                  72 -> 72
D5 constructive / negative:             36/36 -> 36/36
D5 accepted context-None public runs:      10 -> 10
Living acts:                               17 -> 17
Conformance categories:                    14 -> 14
Conformance negative probes:               50 -> 50
Conformance active refs:                    16 -> 16
```

hedgehog.kernel.__all__ remains byte-exact. The one new type and six new
functions are direct package attributes only.

D5 case 64 observes the exact 35-target append-only geometry. D5 case 67
preserves historical staged counts [74,81,90,110] and records current module
count 116. The D5 report identity and rendered proof bytes change honestly.
Historical report IDs and bytes remain pre-correction evidence only.

===============================================================================
12. HISTORICAL COMPATIBILITY AND WHOLE-RUN BOUNDARY
===============================================================================

When observed_work_context is None, preserve:

- the historical run_fractal_runtime_v02(source_context) call;
- historical runtime behavior;
- all canonical serialized topology/queue/result/trace/report/artifact bytes and
  identities;
- historical validation outcomes;
- no observed-work parents or causal rows;
- zero authority/effect outputs.

Do not claim raw Python bundle field geometry, repr, asdict, or E3 observation
digests remain byte-identical.

Whole-run execution is not the normal selective path. It is permitted only when
execution_scope is WHOLE_RUN_ESCALATION and either the independently validated
affected closure equals all recomputable artifacts in the bounded topology or
one exact named fail-closed policy requires full reconstruction. The exact
reason and policy ID are carried by the context and downstream report evidence.

Calling the whole-run seam with execution_scope SELECTIVE fails closed. A
whole-run escalation uses the same accepted observed-work binding/context law
and does not bypass granular constructibility proof.

===============================================================================
13. G2-E3 REVALIDATION STATUS AFTER CORRECTED G2-D LANDING
===============================================================================

This subsection is an explicit v0.3.7 guardian precision and is normative.

Before corrected G2-D implementation bytes land, the current G2-E3 status
remains:

```text
IMPLEMENTED_COMMITTED_ACCEPTANCE_PASS_ON_PRECORRECTION_G2D
```

Acceptance of this contract alone does not change that status because no
runtime byte has changed.

Immediately after the corrected G2-D implementation commit lands, and before a
fresh owner-terminal V06, G2-E3 status becomes exactly:

```text
REVALIDATION_PENDING_ON_CORRECTED_G2D
```

This transition is mandatory even when no G2-E source, schema, test, or runner
byte changed. The reason is that FractalRuntimeExecutionBundleV02 gains a new
runtime-only field and E3 public observation enumerates dataclass fields, so the
cross-process member-observation digests must be regenerated against corrected
G2-D bytes.

During REVALIDATION_PENDING_ON_CORRECTED_G2D:

- the committed G2-E3 implementation remains intact historical code;
- the prior V06 PASS remains valid evidence for pre-correction G2-D bytes only;
- no current G2-E3 acceptance claim may be made for corrected G2-D bytes;
- no G2-E code/test patch is presumed or authorized;
- G2-E4 remains NOT_STARTED_NOT_AUTHORIZED;
- Gate 2 remains NOT_CLOSED.

G2-E3 may return to:

```text
IMPLEMENTED_COMMITTED_ACCEPTANCE_PASS_ON_CORRECTED_G2D
```

only after all of the following:

1. corrected G2-D implementation is committed as REAUDIT_PENDING;
2. independent re-audit passes on those exact committed bytes;
3. additive G2-D reclosure returns corrected G2-D to CLOSED_PASS;
4. the unchanged owner-terminal V06 runs exactly once;
5. focused Tier 2 is 11/11;
6. complete G2-E file is 50/50;
7. exactly two independent test-only public baseline calls are observed;
8. all three freshly computed cross-process digests are equal;
9. repository mutation during V06 is absent.

No historical digest literal is reused as an expected corrected value. If V06
fails, G2-E3 remains fail-closed pending guardian review; no E4 prompt is
prepared and no blind repair/rerun is authorized.

===============================================================================
14. CORRECTION LIFECYCLE AND EXACT PATH CLASSES
===============================================================================

14.1 Contract hop

The accepted v0.3.7 contract-only repository hop changes only the ten
contract/lifecycle surfaces frozen by the controlling consumer-closure decision:

```text
docs/fractal_runtime_v0_2_g2_d_post_acceptance_contract_addendum_v01.md
tests/test_fractal_runtime_g2_d_v02.py
  only the accepted v0.3.7 revision/hash/lifecycle assertion
AGENTS.md
README.md
specs/machine_manifest_v0_25.json
release/current_status_overlay_v01.json
release/claim_to_evidence_index.md
release/current_limitations.md
release/current_release_notes.md
tests/test_repository_release_spine_v01.py
```

After this contract hop, active G2-D status is
CORRECTION_CONTRACT_ACCEPTED_IMPLEMENTATION_PENDING. Pre-correction CLOSED_PASS
remains historical evidence only. implementation_authorized remains false until
a separate owner action.

14.2 Implementation correction paths

A later separately authorized implementation action may change exactly:

```text
hedgehog/kernel/fractal_runtime_v02.py
schemas/fractal_runtime_v02.schema.json
tests/test_fractal_runtime_g2_d_v02.py
demo/run_fractal_runtime_g2_d_v02.py
hedgehog/kernel/transition_registry_v01.py
tests/test_transition_registry_v01.py
hedgehog/kernel/__init__.py
demo/run_kernel_conformance_v01.py
```

Active lifecycle synchronization to REAUDIT_PENDING may additionally change the
exact governance/release surfaces listed in the accepted decision. G2-C, ABI,
KernelArtifact schema, Root, Semantic Work, Trust, Post V&V, GT, G2-E code/schema/
tests/addendum, old audit, old checkpoint, Living implementation, Conformance
kernel implementation, and all other paths remain protected unless a new exact
blocker is separately ruled.

14.3 Evidence, audit, and reclosure paths

Execution evidence is external /tmp/log material and does not itself mutate the
repository.

A new independent audit is additive and must use a new path under:

```text
docs/audit_reports/
```

The old audit and checkpoint remain immutable historical pre-correction
evidence.

Additive reclosure may create:

```text
docs/fractal_runtime_v0_2_g2_d_observed_work_correction_checkpoint_v01.md
```

and synchronize the exact governance/release/status paths required by the
accepted decision. Only after independent audit and additive reclosure may
corrected G2-D return to CLOSED_PASS.

===============================================================================
15. ACCEPTANCE EVIDENCE AND TEST-OPERATION LAW
===============================================================================

This accepted contract authorizes no implementation test. The contract-only hop
may run only its bounded contract-identity, release-spine, and static checks. If
implementation is later separately authorized, the exact commands, nodes,
fixture expansions, public-call counts, forecasts, watchdog ceilings, process-
group termination, and repository guards in controlling decision SHA-256
69981a3547357b167ea3c260da145038b6b38a1726a910bbd8fd78b1fd46a794,
Sections 14.1 through 14.11, are incorporated as the required evidence plan.
They may not be weakened by an implementation prompt.

Required contour summary:

```text
static proof:
  pytest items 0; public calls 0; watchdog 120s

four-node microproof:
  4 items; public calls 1 historical; watchdog 600s

focused core:
  27 function nodes / 43 items;
  public calls 3 = 1 historical + 2 context;
  watchdog 1800s

focused shared compatibility:
  64 items; public calls 0; watchdog 1800s

focused D6 consumer:
  5 items; public calls 27; watchdog 1800s

complete G2-D + complete Transition:
  92 + 268 = 360 items;
  public calls 30 = 27 D5 + 1 historical + 1 context PASS
                    + 1 SELECTIVE whole-run FAIL_CLOSED;
  watchdog 3600s; owner terminal only

independent two-process D5:
  two fresh processes; 72 cases each; 36/36 each; 10 accepted each;
  27 public calls per child; equal rendered bytes and report identity;
  child ceiling 1800s; outer ceiling 3900s; owner terminal only

complete Living:
  575 items; public calls 27; watchdog 5400s; owner terminal only

complete Kernel Conformance:
  349 items; public calls 27; watchdog 5400s; owner terminal only

release spine:
  23 items; public calls 0; watchdog 600s

post-reclosure G2-E3 V06:
  11 focused + 50 complete; two public baseline calls;
  three fresh equal digests; outer watchdog 2100s; owner terminal only
```

No full-repository pytest, nested pytest, multi-hour diagnostic loop, blind
repair, blind rerun, Living/Conformance iterative debugger, live provider/model/
network/connector/external-DRS operation, real effect, or manual all-real runner
is authorized.

On any new failure class: preserve exact bytes and logs, stop the remaining
contours, report the complete failure set, and await a new owner/guardian ruling.

===============================================================================
16. INDEPENDENT RE-AUDIT, ADDITIVE RECLOSURE, AND E4 ENTRY ORDER
===============================================================================

The exact lifecycle is:

```text
A. guardian accepts v0.3.7 correction contract
B. owner separately authorizes implementation correction
C. static/micro/focused/full evidence passes
D. corrected implementation bytes commit with G2-D = REAUDIT_PENDING
   and G2-E3 = REVALIDATION_PENDING_ON_CORRECTED_G2D
E. new independent audit runs on exact committed corrected bytes
F. additive successor checkpoint and release/status synchronization land
G. corrected G2-D returns to CLOSED_PASS
H. owner runs one fresh unchanged G2-E3 V06
I. regenerate E4 public-seam constructibility register
J. complete exact two-Root-pair register
K. guardian accepts G2-E v0.1.3 / E4 contract hop
L. only then prepare the first G2-E4 implementation prompt
```

The new audit must bind the corrected implementation commit and verify at least:
21/18/3/18 and 116/122/143 geometry; old-34-plus-target-35; t02 historical and
context parent forms; full settled-prefix propagation; separate historical and
observed-work counterfactual semantics; the exact observed-work
counterfactual validated_object_id domain/material; full-artifact pointer law;
parent-closed input family; unchanged Stage-D ABI partition semantics; D5 two-
process equality; complete G2-D, Transition, Living, Conformance and shared
compatibility evidence; zero authority/effect boundary; old audit/checkpoint
immutability; G2-D REAUDIT_PENDING and G2-E3 REVALIDATION_PENDING status before
reclosure; and no E4 implementation.

The successor checkpoint must bind corrected implementation, new audit,
evidence-log identities, new geometry, current release-spine paths, and explicit
nonclaims. Old audit/checkpoint certify old bytes only.

After reclosure and fresh V06, the regenerated E4 register must still prove one
minimal affected subtree, complete corrected bundle construction, conditional
escalation, both Root review pairs, both RootDecision Kernel artifacts, ACCEPT
and every non-ACCEPT branch, exact t04/t05/t06/t09/t10 bindings, no private G2-D
dependency, and no E5/E6/G2-F work.

===============================================================================
17. PRESERVED NONCLAIMS
===============================================================================

Neither this accepted contract nor the future correction claims:

- production readiness or security certification;
- provider, model, network, connector, or external DRS reliability;
- persistence, distribution, fault tolerance, or performance beyond evidence;
- successor-baseline creation;
- truth or authority from an audit/checkpoint/test/hash;
- G2-E4 completion;
- G2-E5 runner/matrix completion;
- G2-E6 Living/Conformance extension;
- Gate 2 closure;
- public release, RC2, or real-world effects.

===============================================================================
18. ACCEPTED V0.3.7 CLOSING FLAGS
===============================================================================

```yaml
G2D_V037_DOCUMENT_STATUS=POST_ACCEPTANCE_CORRECTION_ADDENDUM
G2D_V037_GUARDIAN_REVIEW_STATUS=ACCEPTED
G2D_V037_ACCEPTED=true
G2D_V037_ACCEPTED_PENDING_DRAFT_SHA256=8801e413f93765cc7059ce5e03e82e881b20cfd193f12551a60a0b90920bb63d
G2D_V037_CONTRACT_HOP_COMPLETED=true
G2D_V037_IMPLEMENTATION_AUTHORIZED=false
G2D_V037_IMPLEMENTATION_STARTED=false
G2D_V037_IMPLEMENTATION_REPOSITORY_PATCH_CREATED=false
G2D_V037_CODEX_IMPLEMENTATION_PROMPT_PREPARED=false
G2D_V037_BLOCKER_ID=BLOCKER_E4C_001
G2D_V037_GUARDIAN_DIRECTION=OPTION_1
G2D_V037_KERNEL_ARTIFACT_IDENTITY_CARRIER_PRESERVED=true
G2D_V037_NEW_SERIALIZED_BINDING_TYPE_COUNT=0
G2D_V037_NEW_RUNTIME_ONLY_TYPE_COUNT=1
G2D_V037_RUNTIME_OBSERVED_WORK_CONTEXT_REQUIRED=true
G2D_V037_LOWER_LAYER_G2E_IMPORT_COUNT=0
G2D_V037_NEW_PUBLIC_FUNCTION_COUNT=6
G2D_V037_CORRECTED_EXISTING_PUBLIC_SIGNATURE_COUNT=13
G2D_V037_NEW_VALIDATION_TARGET_COUNT=1
G2D_V037_VALIDATION_TARGET_APPEND_ONLY=true
G2D_V037_NEW_FAILURE_STAGE_COUNT=0
G2D_V037_NEW_REASON_COUNT=0
G2D_V037_NEW_SCHEMA_DEFINITION_COUNT=0
G2D_V037_NEW_TRANSITION_RULE_COUNT=0
G2D_V037_NEW_CAUSAL_DECISION_EFFECT_COUNT=2
G2D_V037_HISTORICAL_COUNTERFACTUAL_SEMANTICS_PRESERVED=true
G2D_V037_OBSERVED_WORK_COUNTERFACTUAL_SEAM_SEPARATE=true
G2D_V037_OBSERVED_WORK_COUNTERFACTUAL_ID_PREFIX=frcounterfactual_v02:
G2D_V037_OBSERVED_WORK_COUNTERFACTUAL_ID_DOMAIN=HEDGEHOG_FRACTAL_RUNTIME_V02_OBSERVED_WORK_COUNTERFACTUAL
G2D_V037_OBSERVED_WORK_COUNTERFACTUAL_ID_MATERIAL_FROZEN=true
G2D_V037_T02_HISTORICAL_CONTEXT_PARENT_FORMS_DISJOINT=true
G2D_V037_SETTLED_PREFIX_CONTEXT_PROPAGATION_REQUIRED=true
G2D_V037_STAGE_D_ABI_PARTITION_SEMANTICS_PRESERVED=true
G2D_V037_PARENT_CLOSED_INPUT_EVIDENCE_REQUIRED=true
G2D_V037_FULL_ARTIFACT_CHANGE_SUPPORT=true
G2D_V037_WHOLE_RUN_ESCALATION_CONDITIONAL_ONLY=true
G2D_V037_G2C_ROUTE_OWNERSHIP_CHANGED=false
G2D_V037_RUNTIME_TOPOLOGY_OWNERSHIP_CHANGED=false
G2D_V037_ROOT_ONLY_AUTHORITY_PRESERVED=true
G2D_V037_POST_IMPLEMENTATION_COMMIT_G2D_STATUS=REAUDIT_PENDING
G2D_V037_POST_CORRECTED_LANDING_G2E3_STATUS=REVALIDATION_PENDING_ON_CORRECTED_G2D
G2D_V037_FRESH_G2E3_V06_REQUIRED=true
G2D_V037_G2E4_STARTED=false
G2D_V037_GATE2_CLOSED=false
G2D_V037_OLD_AUDIT_CHECKPOINT_IMMUTABLE=true
G2D_V037_INDEPENDENT_REAUDIT_REQUIRED=true
G2D_V037_ADDITIVE_RECLOSURE_REQUIRED=true
G2D_V037_CURRENT_G2D_STATUS=CORRECTION_CONTRACT_ACCEPTED_IMPLEMENTATION_PENDING
G2D_V037_HISTORICAL_PRECORRECTION_G2D_STATUS=CLOSED_PASS_ON_PRECORRECTION_BYTES
G2D_V037_CURRENT_G2E3_STATUS=IMPLEMENTED_COMMITTED_ACCEPTANCE_PASS_ON_PRECORRECTION_G2D
G2D_V037_G2E4_STATUS=NOT_STARTED_NOT_AUTHORIZED
G2D_V037_GATE2_STATUS=NOT_CLOSED
G2D_V037_READY_FOR_SEPARATE_IMPLEMENTATION_AUTHORIZATION=true
```

===============================================================================
HISTORICAL ACCEPTED V0.3.6 CONTENT - EXACT PRE-CORRECTION REPOSITORY BYTES
===============================================================================

The following byte sequence is retained verbatim as immutable historical
accepted content. Its embedded present-tense lifecycle statements are historical
to v0.3.6 and do not override the active v0.3.7 metadata above.

# G2-D Post-Acceptance Contract Addendum Version 0.3.6

## 1. Title and Metadata

```yaml
document_status: POST_ACCEPTANCE_CONTRACT_ADDENDUM
document_revision: v0.3.6
guardian_review_status: ACCEPTED
applies_to_preflight: docs/fractal_runtime_v0_2_g2_d_preflight_v01.md
applies_to_preflight_sha256: 8e3ae3b04a9b622329e85529edb8a150739cc787b341f1609438dbde00412e79
repository_basis: 3c80eb63a01c63a8d4a930e4b199a093a90901a5
accepted_v034_basis_revision: v0.3.4
accepted_v034_basis_sha256: 7ea510c4bea2b995074bd9dfdb9108cc51145526c559638964f8a9b70723e69e
accepted_v035_basis_revision: v0.3.5
accepted_v035_basis_sha256: 1a1a546804535602b6f1df65fba16e1ad223cdca85ef1b6c963d797b3228451e
gate_slice: G2-D
affected_slices:
  - G2-D3_CONTEXT_CARRIAGE_AND_CONTEXTUAL_CLOSURE
  - G2-D4_TYPED_RESULT_ACTIVATION_BOUNDARY
g2d3_implementation_authorized: true
g2d3_implementation_resumed: true
g2d3_implementation_completed: true
g2d1_policy_schema_repair_required: true
g2d1_policy_schema_repair_authorized: true
g2d1_policy_schema_repair_started: true
g2d1_policy_schema_repair_completed: true
g2d4_implementation_authorized: false
g2d4_started: false
gate2_closed: false
```

v0.3.6 is the controlling accepted addendum only for Profile D
`CHILD_ACTIVATION_PARENT_DEPENDENCY_FREE_EVIDENCE_ALIAS`, the accepted active
queue-role-alias count of three, its identity-impact register, its proof
ledger, and its final closing flags. Accepted v0.3.5 remains historical
accepted authority for CTC-01, CTC-02, CTC-03, and every unaffected ruling.
Accepted v0.3.4 remains historical accepted evidence at SHA-256
`7ea510c4bea2b995074bd9dfdb9108cc51145526c559638964f8a9b70723e69e`,
and every v0.3.4 ruling outside the earlier exact supersession boundary remains
binding. v0.3.6 creates no D4, G2-E, G2-F, effect, authority, release,
staging, commit, push, or publication authority. Profile D is accepted on the
completed implementation candidate and final 57/57 complete-file proof ledger
recorded below.

Three exact D3 queue role-alias profiles are accepted: preserved Profiles A
and B plus accepted Profile D. The future Root-result alias ruling and all eight
settled-prefix components remain unchanged. Public type counts, public
function counts, schema-definition counts, reason counts, validation-target
counts, failure-stage counts, ABI literal counts, Transition-rule counts, and
facade counts remain unchanged. The only accepted public signature delta is
one required keyword-only `source_context` parameter on existing function 88.
The only accepted reference-policy value delta is `max_parallelism: 4 -> 3`.
No other public geometry change is accepted.

## 2. Preserved v0.2 Constitutional Distinction

1. A source object may represent two semantic roles that intentionally
   reference the same immutable object.
2. A generic Kernel `trace_refs` tuple is an ordered inventory of unique
   causal identities. It cannot repeat an identity merely to repeat a role.
3. Role multiplicity remains visible in typed object fields and Kernel payload
   fields.
4. A later trace occurrence may be omitted only when an explicit profile
   equality-binds the roles, contextual validation proves the same immutable
   object and exact parent geometry, both fields remain in the object and
   payload, and every other reference and order remains exact.
5. No `set`, `dict.fromkeys`, arbitrary stable deduplication, lexical sort,
   or value-wide duplicate suppression is permitted.
6. The generic Kernel ABI, trace uniqueness law, historical artifacts,
   authority law, and effect law remain unchanged.

## 3. Preserved Active Alias Profiles A and B

### A. ROOT_QUEUE_CELL_GLOBAL_BUDGET_ALIAS

- Applies only when `parent_cell_id is None`.
- The queue object and payload retain `cell_budget_id` and
  `global_budget_id`.
- Exact equality is `cell_budget_id == global_budget_id`.
- The artifact trace keeps the cell-budget occurrence and omits only the later
  global-budget occurrence.
- This profile may coexist with profile B.

### B. INVOKED_CHILD_RESULT_OBSERVATION_ALIAS

- Applies only to exact invoked-child FRACTAL_CELL t06 and t08-t12 forms.
- The exact child-result artifact is the third queue artifact parent.
- Queue lineage carries the result artifact once after predecessor lineage.
- `observed_output_refs == (same_child_result_artifact_id,)` preserves the
  output role in the source object and payload.
- The artifact trace keeps the dedicated result-parent occurrence and omits
  only the later observed-output occurrence.
- This profile applies to Root or child parent-slot queues and may coexist
  with profile A.

Child queue local and global budgets remain different immutable objects and
receive no budget-role normalization. Every omitted occurrence must match one
of the three exact accepted active profiles. Profile D supplies the third
accepted omission rule under the exact contextual proof below.

## 4. Preserved Future Profile C

### C. ROOT_RESULT_FINAL_GLOBAL_BUDGET_ALIAS

- Applies only to an exact Root result after contextual completion-budget
  validation.
- Exact equality is `final_cell_budget_id == global_budget_id`.
- The source result object and payload retain both roles.
- The future result trace keeps the final-cell-budget occurrence and omits
  only the later global-budget occurrence.
- This is a documented D4-only ruling. D4 implementation is not authorized or
  started.

## 4A. Accepted Active Profile D: Child Activation-Parent / Dependency-Free Evidence Alias

### D. CHILD_ACTIVATION_PARENT_DEPENDENCY_FREE_EVIDENCE_ALIAS

This accepted v0.3.6 profile applies only when all of the following are
independently and contextually proven:

- `parent_cell_id` is not `None` and the queue occurrence is noninitial;
- the occurrence is exact D3-local t06 `RUNNING -> VALIDATING`, or an exact
  copied-observation t08-t12 `VALIDATING -> terminal` form;
- the historical t06 origin is an exact dependency-free local observation;
- `observed_evidence_refs` exactly equals the validated
  `cell_input.evidence_refs` tuple;
- the exact activation-parent queue artifact ID is the immutable
  activation-parent lineage identity preserved from the accepted child
  initial occurrence through the exact predecessor chain;
- that identity occurs exactly once in `observed_evidence_refs`; and
- source context, topology, cell input, queue predecessor, queue artifact,
  activation-parent artifact, retained report, budget, transition, and
  historical t06-origin checks all pass.

The typed queue object and Kernel payload retain both semantic roles:
activation-parent lineage and dependency-free observed evidence. No queue,
evidence, lineage, parent relation, or contextual binding is removed or
weakened.

The generic Kernel trace keeps the earlier activation-parent-lineage
occurrence and omits only the later equal observed-evidence occurrence. Every
other evidence occurrence and its exact order remain. The trace remains
unique, with the Transition decision first and topology identity second. No
set, `dict.fromkeys`, lexical sort, value-wide deduplication, or arbitrary
first/last occurrence rule is permitted.

Profile D fails closed for Root entries, initial child entries,
dependency-bearing local observations, t02-t05, t07, PARENT_RETURN, foreign,
copied, missing, reordered, duplicated, or multiply occurring
activation-parent identities, nonmatching evidence, arbitrary duplicates, and
D4 result construction. It does not apply to a foreign or copied cell input.

Profile D may coexist with another exact accepted profile only when every
profile predicate and exact omission index is
independently proven. No profile may hide a duplicate created by another
unproven role. For the current dependency-free D3-local child t06/t08-t12
witness, Profile D is the only accepted new omission rule required.

The accepted child queue admission and t04/t05 remain constructible. The
dependency-free child local t06 material remains exactly
`cell_input.evidence_refs`; activation-parent lineage remains exact and
append-only. Profile D reconciles typed role multiplicity with generic trace
uniqueness without accepting synthetic terminal occurrences. The positive
proof requires an actual public t04 -> t05 -> t06 -> t08-t12 child history.

The accepted implementation is limited to private queue trace projection and
contextual validation: derive
the exact alias index from validated child lineage and exact dependency-free
cell-input evidence, omit only that later evidence occurrence, preserve typed
fields and Profiles A/B, and enforce exact coexistence. No public surface,
schema, ABI, Transition rule, or facade changes are permitted. The separately
observed S0 t06 predecessor failure is test-helper round ownership and is not
part of Profile D or this contract correction.

### Profile D identity impact register

The accepted implementation changes D3-local child t06 queue
artifact `trace_refs` and `artifact_id`, copied-observation t08-t12 child
terminal queue artifact `trace_refs` and `artifact_id`, downstream
`FractalCellResult` artifact `parent_refs` and `artifact_id`, and affected
parent-slot invoked-child artifact identities and expected test identity bytes.
Typed queue identity and fields, cell-input identity and evidence, the
activation-parent artifact, generic ABI, Transition Registry, public counts and
signatures, schemas, reasons, validation targets, failure stages,
`max_parallelism=3`, `profile_version=v0.3.1`, Root authority, and the
zero-effect law remain unchanged. No historical artifact is rewritten.

### Profile D accepted proof ledger

The final proof builds an accepted full-fractal source context, actual parent
slot, and child activation; drives the dependency-free first child D3-local
node through public t04, t05, t06, and t08; proves both typed roles remain
present; validates the Profile D trace and canonical identity; and uses a
`TEST_ONLY_EXTERNAL_D4_BOUNDARY` for the remaining typed child tail and
completion budgets solely to validate the externally visible child-result
pair. D4-owned POST_VV, GT, PARENT_RETURN, result, report, and bundle semantics
are not executed by D3.

The final mutation proof rejects Root and initial-child forms,
dependency-bearing locals, wrong t-rules, missing or foreign activation-parent
evidence, reordered or duplicate evidence, activation-parent multiplicity,
foreign/copied cell inputs, arbitrary duplicates, Profile-B duplicates hidden
by Profile D, manually resealed terminal rows, and boundary-only synthetic
indexes as runtime integration proof.

## 5. Guardian Repair 3 Stopped-Finding Register

| Finding | Accepted obligation | Omitted current input | Existing typed carrier | Amended signatures | Boundary | No-new-public proof |
|---|---|---|---|---|---|---|
| Actual parent-slot chain | Child authority requires actual t02 -> t04 -> t05 occurrence chain | Predecessor entries/artifacts, parent input, START_NODE budget, round reservation | Settled budgets, queue entries, queue artifacts, cell inputs | 82, 86, 87, 89, 90 | D3 | Existing tuples only |
| Queue-budget continuity | Queue IDs bind immutable occurrence anchors while new events advance from reconstructed live heads | Complete ordered budget history at queue construction | Settled budget log | 82, 83, 90 | D3; completion remains D4-owned | Existing budget type |
| READY reservation | Occupied capacity is RUNNING plus READY | Complete latest round family and prior reservations | Settled queue entries/artifacts, budgets, backpressure states | 83, 88, 90 | D3 | Existing queue/backpressure types |
| No-child disposition | Reasons cannot select BLOCKED, NEEDS_USER, or DEADEND | Typed activation facts and accepted history | Settled prefix plus private activation material | 90 | D3 | Private canonical dictionary |
| Local observation | Arbitrary refs cannot select t06 or terminal state | Exact node/assignment/dependency observation context | Settled prefix plus private local material | 83, 90 | D3-local nodes; report nodes remain D4 | Private canonical dictionary |
| Cell-aware history | Latest state is keyed by cell and node and forks fail closed | Complete aligned queue occurrence history | Settled queue entries/artifacts | 83, 88, 89, 90 | D3 | Existing tuples only |
| Unchanged defer and no-spin | Full controlling state must be compared across rounds | Cell input, activation, dependencies, prior backpressure and round state | Settled prefix plus private round fingerprint | 88, 90 | D3 | Private canonical dictionary |
| Cell-input contextual closure | Root/child inputs bind complete actual initial families and activation chain | Complete queue/artifact, budget, input and scope history | Settled queue/artifact/budget/input/scope tuples | 86, 87 | D3 | Existing tuples only |
| Node-kind report availability | D3 cannot accept copied semantic PASS for POST_VV/GT/PARENT_RETURN | Actual typed proposal/VV/GT family | Existing D4 typed families and validation reports | 90 carries prefix but returns unavailable | D4 | No D3 type or report target added |

The stopped implementation could not repair these findings without changing
the accepted signatures or accepting caller-selected truth. Stopping before
runtime or test mutation was therefore the only fail-closed result.

The v0.3.1 guardian correction matrix is exact:

| Defect | v0.3 text | Accepted authority | v0.3.1 replacement | Sections | Public geometry |
|---|---|---|---|---|---|
| Round fingerprint contradiction | Complete dictionary hash included round and prior-state IDs | Unchanged defer depends only on controlling state | Audit envelope is retained but excluded from `control_core_sha256` | 10, 14, 16, 19 | Same private profile |
| Reason namespace conflation | Local DEGRADED used the t09 decision reason | Queue support reason is `g2d_partial_failure_recorded`; t09 decision reason is Registry-owned | Explicit queue/Transition namespace split | 10, 12, 16, 19 | No reason added |
| Report prefix overbreadth | Every accepted report appeared retained | Preflight partitions retained, transient-rederived, and external-only reports | Exact seven-part D3 retained prefix and explicit exclusions | 7, 9, 10, 12, 16, 19 | Same report type and parameter |
| Cross-chain revise contamination | Every settled revise observation entered child evidence | Revise evidence is exact cell/node/predecessor-chain context | Parent-slot-local revise IDs/states and exact evidence order | 10, 11, 16, 19 | Same revise type |
| Missing NEEDS_USER carrier | Direct typed missing-input fact was named without an existing carrier | D3 has exact terminal dependency occurrences | NEEDS_USER requires an exact NEEDS_USER dependency and aligned artifact | 10, 11, 12, 15, 16, 19 | No type or parameter added |
| Dependency-free evidence narrowing | RouteEligibility alone replaced the cell-input family | Cell input already carries exact validated evidence order | Dependency-free evidence equals `cell_input.evidence_refs` | 10, 12, 16, 19 | Same cell-input type |

The v0.3.2 queue-budget temporal-role matrix remains binding with the v0.3.3
frontier clarifications shown here:

| Row | v0.3.1 ambiguity | Immutable preflight law | v0.3.2 ruling | Sections | Public geometry |
|---|---|---|---|---|---|
| 1. Latest global per decision | Queue global ID was treated as necessarily current | Every decision sees latest global state | Reconstruct the unique live Root/global head from the settled budget log | 7, 8, 13, 14 | None |
| 2. Queue budget IDs | IDs were called current objects without temporal qualification | Queue identity preserves bound budgets | IDs are immutable event-time anchors | 7, 8, 12, 13 | None |
| 3. PENDING/READY no successor | Reuse wording conflated anchors and live heads | t03/t04 create no budget object | Copy source queue anchors; live heads may advance elsewhere | 8, 12, 13 | None |
| 4. t05 START_NODE | Exact predecessor wording could select the READY anchor | START_NODE advances parallelism on the latest global axis | Candidate successor advances from reconstructed live heads | 8, 9, 12, 13 | None |
| 5. t06 FINISH_NODE | Exact predecessor wording could select the RUNNING anchor | FINISH_NODE releases latest global parallelism | Candidate successor advances from reconstructed live heads | 8, 9, 12, 13 | None |
| 6. t07 REVISE | Exact predecessor wording could select the VALIDATING anchor | REVISE advances exact live counters | Candidate pair advances from reconstructed live heads | 8, 9, 12, 13 | None |
| 7. Non-PARENT_RETURN terminal | Reuse wording implied live-head equality | t08-t12 create no budget successor | Copy source VALIDATING anchors as provenance | 8, 12, 13 | None |
| 8. Root/global axis | Root role alias lacked temporal-axis wording | Root local/global is one object | One linear combined Root/global axis; live roles alias | 7, 13 | None |
| 9. Child-local axes | Child queue/local ancestry was underspecified | Child local/global objects differ | One linear child-local axis per instantiated child | 7, 13 | None |
| 10. Paired child events | Pair adjacency did not identify pre-event heads | Child local/global successors are paired exactly | Child-local candidate then paired global candidate is one atomic suffix | 7, 8, 13 | None |
| 11. Source anchor ancestry | Historical anchor could be misclassified stale | Stale event predecessor fails closed | Queue anchor must equal or precede the applicable live head | 7, 8, 13 | None |
| 12. Candidate suffix frontier | Prefix included after budgets without pre-head rule | Decision precedes budget successors and target queue | Signature 90 has no suffix; signatures 83/89 validate the post-decision suffix and exclude it only to reconstruct pre-event heads | 7, 9, 13 | None |
| 13. Mixed occupancy | Multiple READY starts were unconstructible | READY plus RUNNING consumes bounded capacity | Serialize G0 through G4 while READY anchors remain historical | 7, 14 | None |
| 14. Backpressure identity | Queue anchor could be supplied as global parameter | Backpressure uses latest global budget | Signature 88 binds the reconstructed live global head | 8, 14 | None |
| 15. Round fingerprint | All budget ID fields lacked role distinction | Core detects queue and budget changes | Latest fields are anchors; current global fields are the live head | 10, 14 | None |
| 16. Local observation | Before IDs could mean queue anchors | Local work observes exact execution frontier | Budget fields mean live heads at the material's t06 origin frontier; later validation replays that origin | 10, 13 | None |
| 17. Child precheck | Parent/global IDs could mean parent-slot anchors | Activation checks current capacity and budget state | Budget fields mean live heads at the t06 precheck origin; slot chain retains anchors and terminal validation replays the origin | 10, 11, 13 | None |
| 18. D4 forward boundary | Terminal anchors could be used for finalization | FINALIZE and aggregate require exact predecessors | Queue anchors are predecessors only when they are also live | 13, 15 | None |

The v0.3.3 two-defect correction matrix is exact:

| Row | Immutable preflight order or replay law | v0.3.2 defect | v0.3.3 correction | Public geometry |
|---|---|---|---|---|
| A. Transition-decision construction frontier | Current source and optional pre-decision material -> Transition decision -> budget successors -> target queue -> target artifact -> contextual validation | Section 9 allowed signature 90 to see an exact candidate suffix, although those budgets are future objects derived from its not-yet-built decision | Signature 90 receives the complete accepted pre-decision budget prefix with candidate suffix length zero; signatures 83 and 89 validate the post-decision suffix at their later frontiers | None |
| B. t06-origin observation replay | t06 introduces one attempt's observations/reasons, then FINISH_NODE budgets are built; t08-t12 copy the validating tuples unchanged | Later terminal validation could rebuild local/precheck material with later current live heads and reseal frozen t06 output or evidence | Reconstruct the exact historical t06 budget prefix and origin heads, rebuild the same branch material, and compare it to the VALIDATING tuples while separately validating current terminal live heads | None |
| C. t07 source validation | t07 clears observations/reasons only after the VALIDATING source is proven | Source-origin validation did not explicitly require historical t06 reconstruction before clearing | Rebuild D3-local material at the historical t06 origin; keep child-result and no-child branches t07-forbidden; then build the t07 decision before its REVISE suffix | None |
| D. Public geometry | Existing settled typed families carry every required fact | No additional carrier is required | Add no type, parameter, profile, function, reason, signature, schema, ABI literal, Transition rule, or package attribute | None |

The v0.3.4 backpressure-frontier contradiction matrix is exact:

| Row | v0.3.3 wording or ambiguity | Immutable preflight law | v0.3.4 ruling | Sections | Public geometry |
|---|---|---|---|---|---|
| 1. State creation frontier | Candidate core and prior comparison frontier were not separated by t03 closure | Backpressure state is built after non-t03 progress and before t03 | Candidate state is absent from the current pre-new-state core | 8, 10, 12 | None |
| 2. Deferred queue family | Deferred IDs existed without a complete closure reconstruction law | One exact deterministic deferred suffix; no work dropped | `state.deferred_queue_entry_ids` is the exact ordered source family | 7, 10 | None |
| 3. t03 decision frontier | State/decision ordering was implicit | t03 requires the exact current-round backpressure state and immutable PENDING source | State exists first; t03 decision sees no target and no budget successor | 6, 12 | None |
| 4. t03 successor/artifact | Recording order was not bound to the prior comparison baseline | Decision -> queue -> artifact -> contextual validation | Build exactly one aligned successor/artifact per deferred source before comparison | 6, 7, 8 | None |
| 5. t03 successor fields | A resealed PENDING entry could appear changed without role classification | t03 preserves source context and records exact defer reason | Exact direct predecessor, +1 snapshot, next round, preserved anchors/observations/lineage, exact t03 reason | 7 | None |
| 6. Append order | Interleaving could make closure frontier ambiguous | Queue/artifact logs are append-only and occurrence-aligned | Closure is contiguous and follows deferred order with no foreign interleave | 6, 7 | None |
| 7. Prior core reconstruction | Prior core was reconstructed merely at its evaluated round | Complete settled history must prove prior state | Reconstruct only after the state's complete t03 closure | 8, 10, 11 | None |
| 8. Future current core | Future candidate and current-round t03 material were not explicitly absent | Candidate state derives from immutable current prefix | Build current core before new state or t03 objects exist | 8, 12 | None |
| 9. Unchanged state | Prior t03 recording changed raw latest fields and appeared as new control change | Unchanged higher round creates nothing | Compare current pre-new-state core to prior post-t03 closure core | 8, 9 | None |
| 10. Changed state | Expected t03 occurrence could masquerade as a change | Only controlling facts permit reconsideration | Dependency, budget, input, activation, semantic occurrence/surface, capacity, order, or scope change opens one bounded epoch | 9 | None |
| 11. Repeated t03 | No explicit epoch-level second-successor prohibition | One transition occurrence per node per round and unchanged defer suppression | At most one t03 successor per deferred source in one control epoch | 7, 9, 10 | None |
| 12. One state per round | Existing round uniqueness remained binding | At most one state for an exact round | Preserve one-state-per-round independently of core comparison | 9, 10, 14 | None |
| 13. No-spin | Self-changing t03 history could permit endless rounds | Settled no-progress fails closed | Suppressed unchanged epochs create no round-only state or t03; bounded wait or fail closed | 9, 13 | None |
| 14. Prefix closure | A prior state could appear before its t03 family was complete | Settled prefixes contain complete accepted history only | Prior state is comparison-eligible only with one complete validated t03 closure | 8, 10 | None |
| 15. Public geometry | Existing state, queue, artifact, and prefix types carry all facts | No new public carrier is authorized | No type, parameter, profile, field, reason, signature, schema, ABI, Transition, or protected-path change | 5, 11, 17 | None |

The v0.3.5 accepted correction matrix is exact:

| Finding | Accepted v0.3.4 basis | Accepted v0.3.5 ruling | Accepted effect | Public geometry |
|---|---|---|---|---|
| CTC-01 no-child NEEDS_USER acceptance boundary | Conditional D3 validation requires an exact typed NEEDS_USER dependency; a direct carrier is future D4-owned | Current accepted topology cannot construct that dependency at the parent activation precheck, so current D3 acceptance requires negative manufacture rejection but no positive standalone no-child NEEDS_USER witness | Clarifies acceptance and tests only; ownership and fail-closed validator remain unchanged | None |
| CTC-02 reference capacity witness | v0.3.2-v0.3.4 retained the reference `max_parallelism=4` and historical G0 -> G4 witness | Accept reference `max_parallelism=3` and the exact R0/R1/R2 source-bound witness below | Lower D1 policy/schema repair is completed on the current basis; ordinary downstream identity rebuild is preserved before D3 acceptance | No new public shape; accepted value and future derived identities change |
| CTC-03 / IFC-01 source context | Function 88 receives IDs and retained prefixes but not the actual typed source family | Accept required keyword-only `source_context: FractalRuntimeSourceContextV02` on existing function 88 | Enables, but does not implement here, complete source-bound reconstruction | Exactly one required public parameter on existing signature 88; public function/type counts unchanged |
| Private canonical identity lock | Three private profiles already use `profile_version=v0.3.1` | Document revision and profile identity remain distinct; preserve domains, ordered fields, and v0.3.1 | Ordinary max-parallelism value changes alter derived material without a profile-version change | Three profiles; no fourth profile |

Accepted v0.3.5 supersedes the historical v0.3.2 matrix row 13 and every
v0.3.4 G0 -> G4 clause only as positive acceptance witnesses. They remain
historical evidence explaining the temporal queue-anchor/live-head correction.
Every other v0.3.2-v0.3.4 temporal, decision-frontier, t06-origin, and
post-t03 ruling remains binding.

## 6. Accepted v0.3.5 Authority and v0.3.6 Supersession Boundary

This document preserves the v0.3.1 context-carriage and D3/D4 availability
corrections, v0.3.2 queue-budget temporal roles, and every v0.3.3
decision-frontier and t06-origin replay ruling, and every v0.3.4 post-t03
closure ruling. Accepted v0.3.5 corrected only CTC-01, CTC-02, and CTC-03.
Accepted v0.3.6 now narrowly supersedes v0.3.5 only for Profile D
`CHILD_ACTIVATION_PARENT_DEPENDENCY_FREE_EVIDENCE_ALIAS`, the accepted active
queue-role-alias count of three, its identity-impact register, its proof
ledger, and its final closing flags. The dataclass and schema shapes remain
unchanged. The separately authorized lower D1 runtime/schema repair is
completed on the current repository basis: runtime and schema use
`max_parallelism=3`, function 88 requires `source_context`, and downstream
identities were rebuilt. Neither accepted addendum changes the ABI or
Transition Registry, exposes the package facade, authorizes D4, G2-E, or G2-F,
or closes G2-D or Gate 2.

The exact supersession boundary is:

1. Accepted v0.3.6 controls only Profile D, the accepted active queue-role-
   alias count of three, its identity-impact register, its proof ledger, and
   its final closing flags.
2. Accepted v0.3.5 remains historical accepted authority for CTC-01, CTC-02,
   CTC-03, and every unaffected ruling.
3. CTC-01 supersedes only the positive standalone no-child NEEDS_USER
   acceptance expectation. It transfers no ownership and retains the
   conditional D3 validator.
4. CTC-02 supersedes the v0.3.2 row-13 and v0.3.4 G0 -> G4 positive witness,
   the accepted preflight source-derived policy value `max_parallelism=4`,
   the preflight Section 13 reference-policy ceiling `max_parallelism=4`, and
   the historical runtime/schema implementation target value four. The
   accepted preflight bytes remain unchanged; the separately authorized lower
   D1 runtime/schema repair is complete on the current basis.
5. CTC-03 supersedes the v0.3.4 function-88 signature without
   `source_context` and the v0.3.4 machine flag
   `NEW_PUBLIC_PARAMETER_COUNT=0` only for this exact one-parameter delta.
6. Every other v0.3.4 ruling, public signature, and count remains preserved.
7. v0.3.4 remains historical accepted evidence at exact SHA-256
   `7ea510c4bea2b995074bd9dfdb9108cc51145526c559638964f8a9b70723e69e`.
8. Accepted v0.3.6 creates no D4, G2-E, G2-F, effect, authority, release,
   staging, commit, push, or publication authority. The completed lower D1
   repair and G2-D3 implementation were authorized separately.

The complete replacement signatures in Section 8 supersede only the prior
signatures numbered 82, 83, 86, 87, 88, 89, and 90. Signatures 84 and 85 are
byte-semantically unchanged. Every other D1, D2, D3, D4, Transition-owned,
ABI-owned, and package-facade public signature remains unchanged.

## 7. Settled Runtime Prefix Component Registry

`SETTLED_RUNTIME_PREFIX_COMPONENTS_V02` is a conceptual internal contract,
not a dataclass, runtime context type, public function, artifact, identity, or
schema definition.

| Order | Component | Exact type | Exact order |
|---|---|---|---|
| 1 | `settled_budget_log` | `tuple[FractalRuntimeBudgetV02, ...]` | BUDGET_CONSTRUCTION_LOG_V02 order |
| 2 | `settled_queue_entry_log` | `tuple[FractalCellQueueEntryV02, ...]` | Accepted queue occurrence order |
| 3 | `settled_queue_artifact_log` | `tuple[KernelArtifactV01, ...]` | One-to-one accepted queue artifact order |
| 4 | `settled_cell_inputs` | `tuple[FractalCellInputV02, ...]` | Cell-instantiation preorder |
| 5 | `settled_scope_projections` | `tuple[ParentChildScopeProjectionV02, ...]` | Accepted child-creation order |
| 6 | `settled_revise_observations` | `tuple[FractalReviseObservationV02, ...]` | Accepted construction order |
| 7 | `settled_backpressure_states` | `tuple[FractalBackpressureStateV02, ...]` | Accepted construction order |
| 8 | `settled_validation_reports` | `tuple[FractalRuntimeValidationReportV02, ...]` | Exact retained D3 report order below |

Every component is a complete immutable accepted prefix, never a selected
subset. Queue entries and queue artifacts are one-to-one and
occurrence-aligned for every artifact already built at the construction
frontier. A candidate is absent from its prefix until built, except that a
queue entry is present when its artifact is projected.

Every member is structurally valid, identity-rebuilt, source-bound, and
transaction/Root/topology-consistent before use. Foreign, missing, extra,
duplicated, reordered, forked, skipped, or not-yet-built members fail closed.
Sorting, deduplication, reconstructed subsets, caller role labels, copied PASS,
and ID-only proof are forbidden.

The exact retained D3 validation-report prefix is:

1. one `SOURCE_CONTEXT_STRUCTURAL` report;
2. one `SOURCE_BINDING_AGAINST_G2C` report;
3. one structural `RuntimeTopologySeedV02` report;
4. one `TOPOLOGY_AGAINST_SOURCES` report;
5. every retained queue-entry report in exact accepted queue build-log order;
6. every `SCOPE_PROJECTION_AGAINST_SOURCES` report in accepted child-creation
   order; and
7. every `CELL_INPUT_AGAINST_SOURCES` report in cell-instantiation order.

No D4 result, runtime-report, Stage-D, ABI-profile, causal, or
`COMPLETE_PROFILE` report exists in the D3 retained prefix. Policy structural,
budget structural, source-binding structural, node, edge, assignment,
topology structural, scope structural, cell-input structural, revise,
partial-failure, backpressure, trace, and runtime-report structural reports
are transient and independently re-derived. `RESULT_PROPOSAL`,
`POST_VV_REPORT`, `GT_ADVISORY_REPORT`, `ABI_PROFILE`, and
`CAUSAL_CONSUMPTION` reports are also transient or future-only.
`COMPLETE_PROFILE` and `CAUSAL_COUNTERFACTUAL` are external-only and are never
inserted into the D3 retained prefix.

Signature 89 receives a candidate queue entry while its candidate retained
queue report remains absent until the candidate artifact and contextual pair
validate. Signature 90 receives the retained report for its exact current
source queue, never a target report. Signatures 86 and 87 receive retained
reports for every already accepted initial queue/artifact pair. An explicit
t07 `validation_report` parameter is transient, is independently rebuilt from
the exact revise observation, and gains no authority from appearing in any
caller tuple.

D4 may extend the retained tuple only with the accepted preflight's exact
later report list. D3 may not pre-create those rows.

### Complete-Prefix Closure

Budget-log closure requires Root `INITIAL_ALLOCATION` first. It derives
`budget_by_id`, the exact axis of every budget, predecessor and successor
indexes, the unique live head of every axis, the exact anchor object of every
queue occurrence, anchor-to-live ancestry, and the candidate budget suffix at
the current construction frontier. At signature 90 that suffix is necessarily
empty; at signatures 83 and 89 it is empty for no-successor rules or the exact
post-decision tail for t05/t06/t07. Every later budget predecessor occurs
exactly once earlier, every event-specific owner/scope/state/pair/counter law
is exact, and every queue budget ID resolves to one exact settled budget.

Closure rejects two successors from one predecessor on an axis, a candidate
successor from a non-live predecessor, a skipped head, interleaved or reversed
child-local/global pairs, wrong event or event-ref pairing, foreign owner or
scope, incomparable or future queue anchors, missing anchors, duplicate
budgets, a successor from `FINAL`, `FINAL -> ACTIVE`, Root local/global
divergence, and child local/global accidental aliasing. A historical queue
anchor that is an exact ancestor of the applicable live head remains valid.

Queue/artifact closure requires occurrence-aligned one-to-one entries and
artifacts at every completed artifact frontier. Every `(cell_id, node_id)` has
one initial occurrence and every successor names its immediate earlier
predecessor. Forks, gaps, skips, reversal, terminal reentry, cross-cell edges,
and cross-node edges fail closed. Candidate placement follows the Section 9
construction frontier exactly.

Cell-input closure requires exactly one input per instantiated cell in
cell-instantiation preorder. Every initial and required queue ID resolves to
that cell's exact accepted queue family; no foreign or required node may be
omitted.

Scope closure requires exactly one accepted projection per activated child in
accepted child-creation order. Every child input and child `CELL_CREATE` pair
binds that projection. No projection exists for an unactivated or no-child
slot.

Revise/backpressure closure admits only observations and states constructed
before the current frontier, bound to the exact topology, cell, node, and
queue chain. Future or unrelated members fail closed. Backpressure states use
strictly accepted round order with at most one state per round. A prior
backpressure state is comparison-eligible only after its exact deferred and
admission families resolve and its complete contiguous t03 successor/artifact
closure validates. An incomplete closure, future member, unrelated member,
ambiguous closure frontier, second closure for one state, or second t03
successor for one deferred source in the same control epoch fails closed. The
currently evaluated candidate state remains absent from the settled prefix.

Report-prefix closure requires the exact D3 retained membership and order
above. No transient or future D4 report may be inserted, and no retained
report may be omitted. Caller-supplied counts, subset labels, tuple-prefix
claims, and ID-only assertions do not prove completeness.

### D3_QUEUE_BUDGET_TEMPORAL_ROLE_MODEL_V02

`D3_QUEUE_BUDGET_TEMPORAL_ROLE_MODEL_V02` is a conceptual internal contract,
not a dataclass, runtime context, public function, artifact, identity, schema
definition, validation target, reason, parameter, or fourth private material
profile. It has exactly three roles.

#### QUEUE_OCCURRENCE_BUDGET_ANCHORS

For every `FractalCellQueueEntryV02`, `cell_budget_id` and
`global_budget_id` are immutable event-time causal anchors of that exact queue
occurrence. They resolve to exact earlier accepted budget objects in the
complete settled budget log and prove the queue construction frontier, the
cell/global budget state bound into queue identity, queue/artifact payload and
trace continuity, and source-anchor ancestry for a later transition.

An anchor does not assert that its object remains the live head after another
accepted node or cell advances the same budget axis. Queue occurrences never
mutate in place. There is no hidden queue refresh, queue-ID rewrite, or
post-hoc anchor substitution.

#### LIVE_EXECUTION_BUDGET_HEADS

At every exact construction frontier, live execution heads are independently
reconstructed from the complete settled budget log. The exact axes are one
combined Root/global axis with `budget_scope=ROOT_GLOBAL_AND_CELL` and
`owning_cell_id=topology.root_cell_id`, plus one child-local axis per
instantiated child with `budget_scope=CHILD_CELL_LOCAL` and the exact child as
owner.

For Root, the live cell head and live global head are the same exact immutable
object. For a child, the live child-local head and live Root/global head are
different exact objects. Every axis is linear: it has one legal initial
object, at most one accepted immediate successor per object, and every
non-initial successor names the exact current live head at its construction
frontier. Forks, skipped or future predecessors, sibling or foreign-axis
substitution, successors from `FINAL`, and `FINAL -> ACTIVE` fail closed.

A valid queue anchor equals or is an exact ancestor of its applicable live
head. A foreign or incomparable queue anchor fails closed. A historical queue
anchor is provenance; it is never used as a stale event predecessor.

#### CANDIDATE_BUDGET_SUFFIX

For a rule that creates budget successors, the exact candidate successor or
pair is appended to the settled budget log before queue-advance validation.
At signature 83 or 89, that post-decision suffix is excluded when
reconstructing pre-event live heads and is then validated as already-built
material. Signature 90 never receives it.

- Root t05/t06/t07 has one `ROOT_GLOBAL_AND_CELL` candidate;
  `cell_budget_after is global_budget_after` and both roles reference it.
- Child t05/t06/t07 has one `CHILD_CELL_LOCAL` candidate immediately followed
  by one paired `ROOT_GLOBAL_AND_CELL` candidate. Both share the exact event
  kind, event ref, decision, and pairing law.
- No event may interleave inside a candidate suffix.
- A no-successor rule has an empty candidate suffix.

The preflight statement that every decision sees the latest global budget
remains fully binding: the latest live global head is derived from the complete
settled budget log, never inferred from the source queue's
`global_budget_id` and never caller-selected. The explicit current entry and
latest global budget are distinct immutable contextual inputs: the former is
the latest queue occurrence for one `(cell_id, node_id)`, while the latter is
the unique live Root/global head. After another same-round budget event, their
budget identities need not match.

The PENDING/READY no-successor law means t03/t04 create no budget object and
their targets copy source queue anchors. It does not prevent the topology-wide
live head from advancing through another node. The stale-global failure law
applies to a new event naming a non-live predecessor, a foreign or incomparable
substitution, or an axis fork. It does not reject a proven historical queue
anchor used only as queue lineage.

### D3_TRANSITION_AND_BUDGET_FRONTIER_V02

`D3_TRANSITION_AND_BUDGET_FRONTIER_V02` is a conceptual internal law, not a
type, profile, parameter, function, identity, reason, artifact, or schema
definition. The immutable order is:

```text
exact current entry/artifact
-> optional pre-decision validation/revise/backpressure object
-> TransitionDecisionV01
-> required budget successor(s)
-> target queue entry
-> target queue artifact
-> contextual source/target validation
```

For every t02-t12 call to signature 90, `settled_budget_log` is the exact
accepted pre-decision budget prefix. No budget object derived from the decision
being evaluated is present, candidate suffix length is exactly zero, and live
heads are reconstructed from the supplied log as-is. A future `START_NODE`,
`FINISH_NODE`, `REVISE`, `FINALIZE`, or `CHILD_AGGREGATE` candidate for that
not-yet-built decision fails the frontier. The evaluator never consumes or
validates its own future budget successor. At t02, already committed
`CELL_CREATE` objects are historical pre-decision objects and remain allowed.

For t05/t06/t07, the accepted decision is built first. The budget builder then
uses reconstructed live heads to build one Root candidate or the exact adjacent
child-local/global pair. After structural and contextual validation, those
objects are appended as the exact current candidate suffix.

At signature 83, the accepted decision and required t05/t06/t07 candidate
suffix already exist. That suffix is the exact budget-log tail, is excluded
only while reconstructing pre-event live heads, and is then validated against
the decision, event kind/ref, pre-event heads, deltas, pairing, and target
anchors. t03/t04 and non-PARENT_RETURN t08-t12 have an empty suffix. At
signature 89, the target queue is already the final queue entry and any
required suffix is settled; projection validates target anchors against it and
creates no budget.

### D3_BUDGET_PREFIX_AT_QUEUE_OCCURRENCE_V02

`D3_BUDGET_PREFIX_AT_QUEUE_OCCURRENCE_V02` is a conceptual reconstruction law
and adds no public geometry. Every settled queue occurrence maps to the one
exact historical budget-log prefix present at its construction frontier.

For a t05/t06/t07 target, its anchors identify the exact event candidate or
pair. That segment appears exactly once in budget-log order and is the tail of
the occurrence's historical prefix. The segment predecessors are the exact
pre-event live heads. Budgets accepted later in the current complete log are
outside that historical frontier and cannot alter the occurrence.

For a no-successor target, no event candidate segment exists and target anchors
equal source anchors. Its historical prefix still includes every unrelated
budget event accepted before that target queue was built. An ambiguous
frontier, missing or repeated candidate segment, segment after an object that
could not yet exist, event/decision mismatch, pair interleaving or reversal,
or an occurrence without one exact historical prefix fails closed. A
historical event segment is not required to remain the tail of the current
complete log after later events exist.

### D3_T06_OBSERVATION_ORIGIN_FRONTIER_V02

`D3_T06_OBSERVATION_ORIGIN_FRONTIER_V02` is a conceptual internal law, not a
fourth private profile, type, parameter, identity, artifact, or reason. t06
alone introduces one attempt's `observed_output_refs`,
`observed_evidence_refs`, `advisory_refs`, and `queue_reason_codes`.

Those tuples are frozen at the exact t06 source frontier: the RUNNING source
entry/artifact, cell input, node and assignment, dependency
occurrences/artifacts, source context and topology, pre-FINISH_NODE live
cell/global heads, exact local-observation/child-result/no-child branch, and
the exact t06 decision. The `FINISH_NODE` candidate segment is built only after
that decision. The VALIDATING target stores the candidate anchors and exact
t06-origin tuples. Later live-budget movement cannot change that material.

For t08-t12, the exact t06 origin replay is:

1. locate the exact RUNNING predecessor entry and artifact;
2. locate the exact t06 decision ID;
3. locate the exact t06 `FINISH_NODE` candidate segment from the VALIDATING
   target anchor IDs;
4. derive the historical budget prefix immediately before that segment;
5. reconstruct the exact t06 pre-event live heads from that prefix;
6. reconstruct the exact t06 dependencies, cell input, node, assignment, and
   source context;
7. rebuild the same D3 local-observation material, no-child precheck material,
   or child-result projection used by t06; and
8. require exact equality with all four VALIDATING tuples.

Current terminal-decision live heads remain separate contextual current state
and never reseal the historical t06 material.

The child-result branch continues to bind the exact result/artifact projection
and does not create another private material profile.

Before t07 clears tuples, its VALIDATING source must likewise be proven to
originate from the exact t06 frontier. A D3-local branch rebuilds local
material at that historical origin. Child-result and no-child branches remain
t07-forbidden. The exact revise observation and transient rebuilt structural
report remain required, and the accepted t07 decision precedes its REVISE
candidate suffix.

### D3_BACKPRESSURE_POST_T03_CLOSURE_FRONTIER_V02

`D3_BACKPRESSURE_POST_T03_CLOSURE_FRONTIER_V02` is a conceptual internal law,
not a type, profile, parameter, function, identity, reason, artifact, or schema
definition. One backpressure control epoch has the exact order:

```text
complete latest settled round state
-> all non-t03 progress and READY reservation selection complete
-> one FractalBackpressureStateV02 or None
-> if a state exists, exact t03 decisions for its deferred tuple
-> exact PENDING successor queue entries in deferred order
-> exact queue artifacts in the same order
-> contextual source/target validation for every pair
-> post-t03 defer-closure frontier
```

No t03 successor exists before its state. A prior state cannot be a settled
future-round comparison baseline until this closure is complete. No unrelated
decision, budget, queue, artifact, activation, result, report, or resort may
interleave inside the required closure. t03 creates no budget successor.

#### Exact t03 Defer-Closure Family

For one accepted `FractalBackpressureStateV02`, its ordered source family is
exactly `state.deferred_queue_entry_ids`. Every source is present in the
complete prefix, latest at state evaluation, PENDING, dependency-satisfied,
selected in the deterministic deferred suffix, blocked solely by zero residual
capacity, and bound to the state's live-global frontier.

In exact source order, each source has exactly one direct t03 successor and one
aligned artifact. Each successor has `state=PENDING`, `prior_state=PENDING`,
the source ID as `predecessor_queue_entry_id`,
`predecessor_relation=EXACT_IMMEDIATE_PREDECESSOR`, snapshot sequence +1, and
the exact next accepted queue admission round. It preserves topology, cell,
parent cell, node, planned child, depth, scope, cell/global anchors,
activation-parent lineage, observations, evidence, and advisories. Its sole
queue reason is `("g2d_transition_backpressure_deferred",)`. It binds the exact
t03 decision, creates no budget successor, uses the ordinary predecessor
artifact parent form, and passes contextual source/target validation.

The closure is contiguous in queue execution-build and artifact-build order
and follows `state.deferred_queue_entry_ids` exactly. Missing, extra,
duplicated, reordered, nondeferred, or doubly deferred successors; wrong
predecessor, state, round, sequence, reason, anchor, observation, activation
lineage, artifact parent, or decision; any budget successor; or an interleaved
foreign object fails closed.

The state gains no field and the t03 target gains no backpressure-state ID.
Association is reconstructed from `state.evaluated_round`, the deferred IDs,
direct predecessor relation, exact t03 reason and decision, contiguous order,
and complete-prefix closure.

#### Post-t03 Comparison Baseline

For a newly evaluated candidate state, the current controlling core is built
from the complete current typed prefix before that candidate exists. The
candidate state and current-round t03 decisions, successors, and artifacts are
absent.

For every prior accepted state, first reconstruct and validate its complete
t03 closure. Then reconstruct the prior comparison core at the exact post-t03
closure frontier, after all required successors and artifacts are accepted.
Those t03 occurrences remain the latest queue occurrences in the core; only
objects created after that exact closure frontier are excluded. Compare the
future-round current pre-new-state core to this prior post-t03 core. Never
compare it to the prior state-creation pre-t03 core.

Raw t03 entries and artifacts remain present in the settled prefix and
controlling core. No normalization, erasure, deduplication, refresh, queue-ID
mutation, history drop, or lexical resort is permitted. The correction changes
only the comparison frontier, not the controlling-core field list.

#### Non-Self-Referential Unchanged Defer

The first legal defer in a new controlling-state epoch creates one
backpressure state and exactly one t03 successor/artifact per deferred source.
A later evaluation with the same post-t03 controlling core and only a higher
requested round creates no state, Transition decision, queue entry, artifact,
budget, or round-only identity. A second t03 successor for the same source in
that epoch is forbidden.

A dependency occurrence/state, live-global identity/counter, queue anchor,
cell input, activation lineage, observation/evidence/advisory/reason surface,
latest non-defer semantic occurrence, capacity, deterministic candidate order,
relevant scope projection, or other already-frozen controlling-field change
opens one bounded new epoch and one exact new closure. The expected t03
successor from the prior epoch is the completed recording of that epoch and is
not by itself a controlling-state change.

## 8. Exact Seven-Signature Replacement Table

### 82. admit_runtime_execution_topology_v02

```python
admit_runtime_execution_topology_v02(
    *,
    source_context: FractalRuntimeSourceContextV02,
    topology: RuntimeExecutionTopologyV02,
    topology_artifact: KernelArtifactV01,
    topology_transition_decision: TransitionDecisionV01,
    cell_id: str,
    parent_cell_id: str | None,
    parent_slot_artifact: KernelArtifactV01 | None,
    cell_depth: int,
    scope_ref: str,
    cell_budget: FractalRuntimeBudgetV02,
    global_budget: FractalRuntimeBudgetV02,
    projected_nodes: tuple[RuntimeTopologyNodeV02, ...],
    planned_child_cell_ids: tuple[str, ...],
    admission_decisions: tuple[TransitionDecisionV01, ...],
    cell_instantiation_order: tuple[str, ...],
    settled_budget_log: tuple[FractalRuntimeBudgetV02, ...],
    settled_queue_entry_log: tuple[FractalCellQueueEntryV02, ...],
    settled_queue_artifact_log: tuple[KernelArtifactV01, ...],
    settled_cell_inputs: tuple[FractalCellInputV02, ...],
    settled_scope_projections: tuple[ParentChildScopeProjectionV02, ...],
    settled_revise_observations: tuple[FractalReviseObservationV02, ...],
    settled_backpressure_states: tuple[FractalBackpressureStateV02, ...],
    settled_validation_reports: tuple[FractalRuntimeValidationReportV02, ...],
) -> tuple[FractalCellQueueEntryV02, ...]
```

### 83. advance_fractal_cell_queue_v02

```python
advance_fractal_cell_queue_v02(
    *,
    source_context: FractalRuntimeSourceContextV02,
    topology: RuntimeExecutionTopologyV02,
    current_entry: FractalCellQueueEntryV02,
    node: RuntimeTopologyNodeV02,
    cell_input: FractalCellInputV02,
    transition_decision: TransitionDecisionV01,
    cell_budget_after: FractalRuntimeBudgetV02,
    global_budget_after: FractalRuntimeBudgetV02,
    dependencies: tuple[FractalCellQueueEntryV02, ...],
    local_child_result: FractalCellResultV02 | None,
    local_child_result_artifact: KernelArtifactV01 | None,
    cell_instantiation_order: tuple[str, ...],
    projected_node_ids: tuple[str, ...],
    round_start_queue_entries: tuple[FractalCellQueueEntryV02, ...],
    queue_reason_codes: tuple[str, ...],
    observed_output_refs: tuple[str, ...],
    observed_evidence_refs: tuple[str, ...],
    advisory_refs: tuple[str, ...],
    settled_budget_log: tuple[FractalRuntimeBudgetV02, ...],
    settled_queue_entry_log: tuple[FractalCellQueueEntryV02, ...],
    settled_queue_artifact_log: tuple[KernelArtifactV01, ...],
    settled_cell_inputs: tuple[FractalCellInputV02, ...],
    settled_scope_projections: tuple[ParentChildScopeProjectionV02, ...],
    settled_revise_observations: tuple[FractalReviseObservationV02, ...],
    settled_backpressure_states: tuple[FractalBackpressureStateV02, ...],
    settled_validation_reports: tuple[FractalRuntimeValidationReportV02, ...],
) -> FractalCellQueueEntryV02
```

### 86. build_fractal_cell_input_from_queue_v02

```python
build_fractal_cell_input_from_queue_v02(
    *,
    source_context: FractalRuntimeSourceContextV02,
    topology: RuntimeExecutionTopologyV02,
    topology_artifact: KernelArtifactV01,
    cell_id: str,
    parent_cell_id: str | None,
    parent_input: FractalCellInputV02 | None,
    parent_slot_artifact: KernelArtifactV01 | None,
    scope_projection: ParentChildScopeProjectionV02 | None,
    cell_budget: FractalRuntimeBudgetV02,
    global_budget: FractalRuntimeBudgetV02,
    initial_queue_entries: tuple[FractalCellQueueEntryV02, ...],
    initial_queue_artifacts: tuple[KernelArtifactV01, ...],
    ordered_planned_child_cell_ids: tuple[str, ...],
    settled_budget_log: tuple[FractalRuntimeBudgetV02, ...],
    settled_queue_entry_log: tuple[FractalCellQueueEntryV02, ...],
    settled_queue_artifact_log: tuple[KernelArtifactV01, ...],
    settled_cell_inputs: tuple[FractalCellInputV02, ...],
    settled_scope_projections: tuple[ParentChildScopeProjectionV02, ...],
    settled_revise_observations: tuple[FractalReviseObservationV02, ...],
    settled_backpressure_states: tuple[FractalBackpressureStateV02, ...],
    settled_validation_reports: tuple[FractalRuntimeValidationReportV02, ...],
) -> FractalCellInputV02
```

### 87. validate_fractal_cell_input_against_sources_v02

```python
validate_fractal_cell_input_against_sources_v02(
    value: object,
    *,
    source_context: FractalRuntimeSourceContextV02,
    topology: RuntimeExecutionTopologyV02,
    topology_artifact: KernelArtifactV01,
    parent_input: FractalCellInputV02 | None,
    parent_slot_artifact: KernelArtifactV01 | None,
    scope_projection: ParentChildScopeProjectionV02 | None,
    cell_budget: FractalRuntimeBudgetV02,
    global_budget: FractalRuntimeBudgetV02,
    queue_entries: tuple[FractalCellQueueEntryV02, ...],
    queue_artifacts: tuple[KernelArtifactV01, ...],
    settled_budget_log: tuple[FractalRuntimeBudgetV02, ...],
    settled_queue_entry_log: tuple[FractalCellQueueEntryV02, ...],
    settled_queue_artifact_log: tuple[KernelArtifactV01, ...],
    settled_cell_inputs: tuple[FractalCellInputV02, ...],
    settled_scope_projections: tuple[ParentChildScopeProjectionV02, ...],
    settled_revise_observations: tuple[FractalReviseObservationV02, ...],
    settled_backpressure_states: tuple[FractalBackpressureStateV02, ...],
    settled_validation_reports: tuple[FractalRuntimeValidationReportV02, ...],
) -> FractalRuntimeValidationReportV02
```

### 88. evaluate_fractal_backpressure_v02

Relative to accepted v0.3.4, the sole signature delta is insertion of the
required keyword-only `source_context: FractalRuntimeSourceContextV02`
immediately after `*`. The repository has no accepted typed registry or
resolver that can reconstruct this fifteen-component source context from IDs.
No other function-88 parameter or return type changes.

```python
evaluate_fractal_backpressure_v02(
    *,
    source_context: FractalRuntimeSourceContextV02,
    topology: RuntimeExecutionTopologyV02,
    policy: FractalRuntimePolicyV02,
    global_budget: FractalRuntimeBudgetV02,
    queue_entries: tuple[FractalCellQueueEntryV02, ...],
    admission_round: int,
    settled_budget_log: tuple[FractalRuntimeBudgetV02, ...],
    settled_queue_entry_log: tuple[FractalCellQueueEntryV02, ...],
    settled_queue_artifact_log: tuple[KernelArtifactV01, ...],
    settled_cell_inputs: tuple[FractalCellInputV02, ...],
    settled_scope_projections: tuple[ParentChildScopeProjectionV02, ...],
    settled_revise_observations: tuple[FractalReviseObservationV02, ...],
    settled_backpressure_states: tuple[FractalBackpressureStateV02, ...],
    settled_validation_reports: tuple[FractalRuntimeValidationReportV02, ...],
) -> FractalBackpressureStateV02 | None
```

### 89. project_fractal_cell_queue_entry_kernel_artifact_v02

```python
project_fractal_cell_queue_entry_kernel_artifact_v02(
    queue_entry: FractalCellQueueEntryV02,
    *,
    topology_artifact: KernelArtifactV01,
    predecessor_artifact: KernelArtifactV01 | None,
    activation_parent_artifact: KernelArtifactV01 | None,
    local_child_result_artifact: KernelArtifactV01 | None,
    source_context: FractalRuntimeSourceContextV02,
    settled_budget_log: tuple[FractalRuntimeBudgetV02, ...],
    settled_queue_entry_log: tuple[FractalCellQueueEntryV02, ...],
    settled_queue_artifact_log: tuple[KernelArtifactV01, ...],
    settled_cell_inputs: tuple[FractalCellInputV02, ...],
    settled_scope_projections: tuple[ParentChildScopeProjectionV02, ...],
    settled_revise_observations: tuple[FractalReviseObservationV02, ...],
    settled_backpressure_states: tuple[FractalBackpressureStateV02, ...],
    settled_validation_reports: tuple[FractalRuntimeValidationReportV02, ...],
) -> KernelArtifactV01
```

### 90. evaluate_fractal_runtime_state_transition_v02

```python
evaluate_fractal_runtime_state_transition_v02(
    *,
    source_context: FractalRuntimeSourceContextV02,
    topology: RuntimeExecutionTopologyV02,
    source_artifact: KernelArtifactV01,
    current_entry: FractalCellQueueEntryV02 | None,
    node: RuntimeTopologyNodeV02,
    cell_input: FractalCellInputV02 | None,
    cell_id: str,
    parent_cell_id: str | None,
    planned_child_cell_id: str | None,
    cell_depth: int,
    scope_ref: str,
    cell_budget_before: FractalRuntimeBudgetV02,
    global_budget_before: FractalRuntimeBudgetV02,
    dependencies: tuple[FractalCellQueueEntryV02, ...],
    queue_reason_codes: tuple[str, ...],
    observed_output_refs: tuple[str, ...],
    observed_evidence_refs: tuple[str, ...],
    advisory_refs: tuple[str, ...],
    local_child_result: FractalCellResultV02 | None,
    local_child_result_artifact: KernelArtifactV01 | None,
    validation_report: FractalRuntimeValidationReportV02 | None,
    parent_return_pre_post_vv_terminal_queue_entries:
        tuple[FractalCellQueueEntryV02, ...],
    parent_return_child_results: tuple[FractalCellResultV02, ...],
    parent_return_partial_failures:
        tuple[FractalPartialFailureRecordV02, ...],
    parent_return_result_proposal: dict[str, object] | None,
    parent_return_post_vv_report: dict[str, object] | None,
    parent_return_gt_advisory_report: dict[str, object] | None,
    parent_return_validation_reports:
        tuple[FractalRuntimeValidationReportV02, ...],
    revise_observation: FractalReviseObservationV02 | None,
    backpressure_state: FractalBackpressureStateV02 | None,
    transition_registry: TransitionRegistryV01,
    settled_budget_log: tuple[FractalRuntimeBudgetV02, ...],
    settled_queue_entry_log: tuple[FractalCellQueueEntryV02, ...],
    settled_queue_artifact_log: tuple[KernelArtifactV01, ...],
    settled_cell_inputs: tuple[FractalCellInputV02, ...],
    settled_scope_projections: tuple[ParentChildScopeProjectionV02, ...],
    settled_revise_observations: tuple[FractalReviseObservationV02, ...],
    settled_backpressure_states: tuple[FractalBackpressureStateV02, ...],
    settled_validation_reports: tuple[FractalRuntimeValidationReportV02, ...],
) -> TransitionDecisionV01 | None
```

All seven signatures carry the eight relevant settled-prefix families
explicitly. The amended-signature count remains seven. Only existing signature
88 gains one accepted required keyword-only parameter in v0.3.5. Signatures
82, 83, 86, 87, 89, and 90 remain unchanged from v0.3.4; signatures 84 and 85
remain unchanged. No aggregate context type, public function, public type,
dataclass field, schema definition, reason, validation target, failure stage,
ABI literal, Transition rule, artifact type, or package-facade attribute is
introduced. At the accepted repository basis, production caller count and
direct test caller count for function 88 are both zero. The required
function-88 `source_context` parameter is implemented on the accepted runtime
identity and covered by the final 57/57 proof ledger. This metadata acceptance
introduces no additional signature change.

### Existing Public Parameter Temporal Semantics

- **82 admission.** At t02, `cell_budget` and `global_budget` are the exact
  committed `CELL_CREATE` anchors for the new cell. Root supplies one shared
  object; a child supplies the exact child-local/global pair. At this admission
  frontier those anchors are also the applicable live heads.
- **83 queue advance.** For t03, t04, and non-PARENT_RETURN t08-t12,
  `cell_budget_after` and `global_budget_after` are the source queue anchor
  objects; there is no budget successor and the target copies their IDs. For
  t05, t06, and t07, those parameters are the exact candidate successors
  derived from pre-event live heads; the target stores their IDs, even when
  source anchors are older ancestors. Signature 83 runs after the accepted
  decision and budget construction. Its settled budget log contains the exact
  candidate suffix as the current tail and proves both that suffix and the
  pre-event heads obtained by excluding it.
- **84/85 scope projection.** Their signatures remain unchanged.
  `parent_budget` is the immutable parent allocation basis named by
  `parent_input.cell_budget_id`; `child_budget` is the exact child
  `INITIAL_ALLOCATION` candidate; and `global_budget` is the exact live
  Root/global head at the projection frontier. Complete-prefix validation
  proves the frontier and subsequent paired activation/create sequence. The
  immutable common sibling allocation basis is unchanged.
- **86/87 cell input.** `cell_budget` and `global_budget` are the exact
  committed `CELL_CREATE` anchors bound into the cell input. They are immutable
  input-allocation anchors, not mutable scheduler head pointers.
- **88 backpressure.** `source_context` is the required actual typed
  `FractalRuntimeSourceContextV02`; no `None` acceptance path, mutable global
  registry, ID resolver, cache authority, or reverse lookup is permitted.
  Function 88 independently validates that source context, rebuilds source
  binding, topology seed, and topology against the actual source family, and
  validates queue artifacts, scope projections, cell inputs, and retained
  reports through exact source-aware reconstruction. Retained reports must
  equal independently rebuilt typed objects and canonical bytes in accepted
  order. Copied or constructed PASS reports, IDs, labels, and
  `SimpleNamespace` objects are insufficient. Performance pressure cannot
  weaken source proof. `global_budget` is the exact live Root/global head at
  the evaluated frontier and must equal the unique reconstructed live head. A
  historical queue anchor is not accepted for this parameter.
- **89 artifact projection.** No budget parameter is added. The complete
  settled prefix already contains any required post-decision candidate suffix
  and target queue. It proves queue anchors, anchor ancestry, target budget
  IDs, and exact artifact payload, trace, and parent geometry. Projection
  creates no budget.
- **90 transition evaluation.** For t03-t12, `cell_budget_before` and
  `global_budget_before` are the exact queue-bound anchor objects named by
  `current_entry`. The evaluator independently reconstructs
  `live_cell_budget_before` and `live_global_budget_before` from the settled
  pre-decision budget prefix as supplied; caller values never select them.
  Candidate budget suffix length is exactly zero because the decision does not
  yet exist. For t02, current entry is absent, so the explicit committed
  `CELL_CREATE` objects are historical pre-decision anchors and applicable live
  heads.

## 9. Function Construction-Frontier Matrix

| Function/frontier | Candidate absent from prefix | Required settled frontier | Exact nullability |
|---|---|---|---|
| 82 Root admission | Root initial queue family | Root INITIAL_ALLOCATION, ACTIVATE, CELL_CREATE budget; its shared committed anchor is also the live Root/global head; no queue/input/scope candidate | Parent cell and slot are null; non-budget histories are empty |
| 82 child admission | Child initial queue family | Complete parent history through actual t05 RUNNING; parent input; child allocation, projection, ACTIVATE and paired CELL_CREATE suffix; committed anchors are live at admission | Parent and slot required; planned child tuple empty |
| 83 t03 queue advance | Target PENDING queue entry | Accepted backpressure state and t03 decision; exact deferred source and round family; no budget suffix; target absent | Exact t03 reason; observations/anchors/activation lineage preserved; result families absent |
| 83 other queue advance | Target queue entry | Accepted decision exists; current entry/artifact and round family are settled; t05/t06/t07 exact candidate suffix is the current budget-log tail and is excluded only to reconstruct pre-event heads; other no-successor suffixes are empty | Optional families follow the selected rule only |
| 86 Root input build | Root input | All Root initial entries/artifacts, their retained queue reports, and CELL_CREATE budget | Parent input, slot and projection null |
| 86 child input build | Child input | Actual parent t02/t04/t05 chain, accepted projection, child CELL_CREATE pair, all child initial entries/artifacts, and their retained queue reports | Parent input, slot and projection required |
| 87 input validation | Validation report | Same frontier as 86; candidate input supplied directly and absent from accepted input prefix; every accepted initial pair has its retained queue report | Root/child nullability identical to 86 |
| 88 backpressure | New backpressure state and current-round t03 family | Actual typed source context independently validated; source binding, topology seed, topology, artifacts, projections, inputs, and retained reports rebuilt source-aware; complete current pre-new-state prefix after all non-t03 progress/reservations; unique live global head; every prior state fully t03-closed; current candidate and t03 family absent | `source_context` is required and non-null; returns null unless residual is zero, an exact deferred suffix exists, and changed-core law permits a new epoch |
| 89 initial queue artifact | Candidate artifact and candidate retained queue report | Candidate queue entry is last entry; artifact and retained-report logs end immediately before it; committed anchor objects and ancestry validate | Root activation parent null; child activation parent required |
| 89 t03 successor artifact | Candidate artifact and candidate retained queue report | Accepted backpressure state and t03 decision settled; target PENDING entry is last queue entry; exact source predecessor artifact settled; no budget suffix | Activation/result parents null; ordinary exact predecessor parent required |
| 89 other successor artifact | Candidate artifact and candidate retained queue report | Current target entry is last entry; exact predecessor entry/artifact and source retained report are settled; any required post-decision candidate suffix is already settled and target anchors match it | Activation parent null; result artifact only for invoked-child forms |
| 90 t02 evaluation | Transition decision | Exact committed CELL_CREATE anchors, also live at this frontier; topology source artifact; no current queue candidate | Current entry/input and all optional families null or empty |
| 90 t03 evaluation | Transition decision | Accepted current-round backpressure state; exact deferred PENDING source entry/artifact and retained source report; exact pre-decision budget prefix; target queue/artifact and budget successor absent | Backpressure required; target and all unrelated optional families absent |
| 90 t04-t12 evaluation | Transition decision | Current entry/artifact, retained source report, exact queue-bound anchor parameters, cell input, dependencies, complete latest round family, and exact accepted pre-decision budget prefix; candidate budget suffix absent; no target queue, artifact, or report | Rule-specific matrix in Section 12 |

Every frontier uses the complete prefix at that instant. The queue-only log,
budget log, and runtime-ABI queue artifact log remain append-only and are never
post-hoc regrouped.

Signature 90 never sees a budget candidate derived from the decision it is
evaluating. Signatures 83 and 89 are later construction frontiers and validate
the already-built post-decision suffix where the selected rule requires one.

For t07, the VALIDATING source is first reconstructed against its exact
historical t06 origin. The explicit `validation_report` is transient and
independently rebuilt from the exact settled revise observation. It is not
retained-prefix authority and is never accepted merely because an equal value
is supplied in `settled_validation_reports`.

## 10. Private Canonical Material Profile Field Tables

The following profiles are canonical JSON-safe dictionaries built from exact
existing typed objects. They are domain-separated and deterministic. They are
not dataclasses, ABI artifacts, public identities, schema definitions, public
functions, authority, permission, PASS, or effect.

Document revision and private canonical material identity are distinct. Each
of the three profiles below retains exact `profile_version=v0.3.1`, its
existing domain, and its existing ordered field list. The accepted corrected
`max_parallelism` value changes future material values and derived digests
through ordinary canonical identity laws; it does not authorize a profile
version change. No fourth private canonical material profile exists. A future profile identity change
would require a separately stated semantic change, exact old/new definitions,
field/order/domain comparison, complete downstream identity-churn inventory,
separate guardian review, and separate owner authorization. None is authorized
by this accepted document.

### D3_LOCAL_OBSERVATION_MATERIAL_V02

Domain: `HEDGEHOG_FRACTAL_RUNTIME_V02_D3_LOCAL_OBSERVATION_MATERIAL`.

Ordered fields:

```text
profile_version
topology_id
topology_seed_id
source_binding_id
request_id
transaction_id
owning_root_id
source_time_envelope_ref
node_id
assignment_id
node_kind
expected_output_kind
cell_input_id
cell_input_evidence_refs
cell_id
parent_cell_id
scope_ref
cell_budget_before_id
global_budget_before_id
dependency_queue_entry_ids
dependency_queue_artifact_ids
dependency_states
dependency_reason_tuples
dependency_output_tuples
dependency_evidence_tuples
dependency_advisory_tuples
provider_calls
model_calls
network_calls
connector_calls
external_drs_calls
authority_created
permission_created
final_output_created
drs_write_created
real_world_effects_count
derived_observed_output_refs
derived_observed_evidence_refs
derived_advisory_refs
derived_queue_reason_codes
allowed_outcome
```

The fields through `real_world_effects_count` form the canonical core,
including the exact cell-input identity and evidence family.
`cell_budget_before_id` and `global_budget_before_id` are the exact
live execution heads at the material's origin event frontier, not source queue
anchors. During t06 evaluation they are the current pre-decision live heads.
During t07/t08-t12 validation they are the reconstructed historical t06-origin
heads, never the later terminal-decision heads. The current queue occurrence
and aligned artifact independently bind their immutable anchors.
Positive output is exactly
`("d3local:output:" + sha256(domain || canonical_core_bytes),)`.
When dependencies are nonempty, evidence is the exact aligned dependency queue
artifact IDs in dependency order. When dependencies are empty, evidence is
the exact validated `cell_input.evidence_refs`. Advisory refs are always empty
in D3. Raw caller evidence or output strings cannot select an outcome.

Outcome precedence for deterministic D3-local nodes is BLOCKED, NEEDS_USER,
DEADEND, DEGRADED, COMPLETED based on exact dependency terminal states.
The exact queue support reason map is:

| Local outcome | Exact queue support reasons |
|---|---|
| COMPLETED | `()` |
| DEGRADED | `("g2d_partial_failure_recorded",)` |
| BLOCKED | `("g2d_required_child_failure",)` |
| NEEDS_USER | `("g2d_resolvable_input_needs_user",)` |
| DEADEND | `("g2d_no_progress_deadend",)` |

BLOCKED, NEEDS_USER, and DEADEND have no output ref. DEGRADED and COMPLETED
use the one exact output ref. This profile is available only for MEMORY_CONTEXT,
LOCAL_MODEL_DECLARATION, CLOUD_MODEL_DECLARATION, SEMANTIC_ACTOR,
SEMANTIC_MERGE, and FRACTAL_MERGE.

Queue support reasons and Transition Registry decision reasons are distinct
namespaces. A queue entry uses the derived support tuple above, while
`TransitionDecisionV01.reason_code` uses the exact Registry reason. In
particular, `g2d_transition_degraded_recorded` is only the t09 decision reason
and is never a queue support reason. The child-result branch copies the exact
validated `child_result.reason_codes` at t06 and t08-t12; a DEGRADED child
result carries `("g2d_partial_failure_recorded",)` while its t09 decision
reason remains `g2d_transition_degraded_recorded`.

### D3_CHILD_ACTIVATION_PRECHECK_MATERIAL_V02

Domain: `HEDGEHOG_FRACTAL_RUNTIME_V02_D3_CHILD_ACTIVATION_PRECHECK_MATERIAL`.

Ordered fields:

```text
profile_version
topology_id
topology_seed_id
source_binding_id
route_eligibility_artifact_id
topology_artifact_id
parent_cell_id
parent_cell_input_id
parent_scope_ref
parent_slot_node_id
parent_slot_assignment_id
canonical_child_index
planned_child_cell_id
candidate_child_scope_ref
parent_slot_initial_queue_entry_id
parent_slot_initial_artifact_id
parent_slot_t02_decision_id
parent_slot_ready_queue_entry_id
parent_slot_ready_artifact_id
parent_slot_t04_decision_id
parent_slot_running_queue_entry_id
parent_slot_running_artifact_id
parent_slot_t05_decision_id
parent_cell_budget_id
global_budget_id
parent_budget_state
global_budget_state
parent_budget_counters
global_budget_counters
dependency_queue_entry_ids
dependency_queue_artifact_ids
dependency_states
dependency_reason_tuples
dependency_output_tuples
dependency_evidence_tuples
parent_allowed_capability_ids
child_allowed_capability_ids
parent_forbidden_claims
child_forbidden_claims
parent_ttl_units
child_ttl_units
parent_depth
child_depth
instantiated_sibling_count
instantiated_total_cell_count
occupied_admission_slots
max_depth
max_fan_out
max_total_cells
max_parallelism
max_provider_calls
relevant_parent_slot_revise_observation_ids
relevant_parent_slot_revise_terminal_states
derived_disposition
derived_queue_reason_codes
derived_evidence_refs
```

The candidate child scope is the scope already used by the settled planned
child identity. Child capabilities are the policy-ordered subset allowed by
the parent and policy; child prohibitions retain every parent prohibition and
every additional policy prohibition in that order.

Relevant revise history is restricted to the same topology ID, parent cell
ID, and parent FRACTAL_CELL node ID. Each observation queue entry belongs to
the exact immediate-predecessor chain leading to the current RUNNING parent
slot, was constructed before that frontier, and remains in exact construction
order. A sibling node, other child slot, other cell, other topology, future
observation, duplicate, or reordered observation fails closed.

The exact no-child precheck evidence order is:

1. exact RouteEligibility artifact ID;
2. exact topology artifact ID;
3. exact parent cell-input ID;
4. exact parent-slot initial t02 artifact ID;
5. exact parent-slot READY t04 artifact ID;
6. exact parent-slot RUNNING t05 artifact ID;
7. exact live parent-local budget ID;
8. exact live global budget ID, omitted only when it is the same Root
   budget identity already emitted at position 7;
9. exact dependency artifact IDs in dependency order; and
10. exact relevant parent-slot revise observation IDs in construction order.

The typed material retains both budget roles even when Root aliases them. The
evidence tuple is an ordered unique causal-identity inventory and emits a
shared Root budget identity once. This is not a queue-trace alias profile and
does not change the active queue alias count. Every evidence member is
independently rebuilt from the settled typed prefix; caller evidence is
comparison-only.

Within this material, `parent_cell_budget_id`, `global_budget_id`,
`parent_budget_state`, `global_budget_state`, `parent_budget_counters`, and
`global_budget_counters` describe the exact live parent-local and live global
heads at the t06 precheck origin frontier. During t10-t12 validation those
heads are reconstructed from the historical t06 prefix and are not replaced
by later current heads. The t02/t04/t05 queue/artifact chain separately carries
immutable queue anchors. The immutable parent allocation basis remains bound
through `parent_input.cell_budget_id` and child `INITIAL_ALLOCATION` lineage.
Evidence positions 7 and 8 therefore use origin-frontier live heads and
preserve the existing exact Root same-identity omission law.

### D3_ROUND_CONTROL_FINGERPRINT_MATERIAL_V02

This single canonical JSON-safe material has an audit envelope and a
controlling core. It does not create a fourth private profile.

Audit envelope fields, retained for ordering and diagnostics but excluded
from the controlling-state digest:

```text
profile_version
topology_id
policy_id
admission_round
prior_backpressure_state_ids
```

Controlling core fields, which alone determine whether scheduler state
changed:

```text
latest_cell_node_keys
latest_queue_entry_ids
latest_queue_artifact_ids
latest_states
latest_snapshot_sequences
latest_admission_rounds
latest_predecessor_queue_entry_ids
latest_cell_budget_ids
latest_global_budget_ids
latest_cell_input_ids
relevant_scope_projection_ids
dependency_occurrence_ids_by_key
dependency_states_by_key
activation_parent_artifact_ids_by_key
observed_output_tuples_by_key
observed_evidence_tuples_by_key
advisory_tuples_by_key
queue_reason_tuples_by_key
current_global_budget_id
current_global_budget_counters
deterministic_admission_order
running_count
ready_count
occupied_admission_slots
residual_admission_slots
eligible_pending_queue_entry_ids
deferred_queue_entry_ids
future_progress_source_queue_entry_ids
```

`latest_cell_budget_ids` and `latest_global_budget_ids` are the immutable
budget-anchor IDs carried by the latest queue occurrences per key.
`current_global_budget_id` and `current_global_budget_counters` are the exact
live Root/global head and counters at the actual backpressure evaluation
frontier. This profile's field list is unchanged from v0.3.4 and remains at
`profile_version=v0.3.1`. The controlling
core therefore detects both queue occurrence/anchor changes and live global
budget changes without conflating their temporal roles.

Keys are ordered by state class and then the accepted admission key; they are
never keyed by node ID alone. The exact comparison is:

```text
control_core_sha256 =
  SHA256(
    domain = HEDGEHOG_FRACTAL_RUNTIME_V02_D3_ROUND_CONTROL_FINGERPRINT_CORE
    payload = canonical JSON bytes of the exact controlling core only
  )
```

`control_core_sha256` is a private comparison value. It is not a public
identity, scheduler object ID, ABI reference, lineage field, reason, or
authority. `admission_round` and `prior_backpressure_state_ids` do not
influence it.

The current candidate core is independently built from the complete typed
prefix at the current pre-new-state frontier. The candidate state and its t03
decisions, successors, and artifacts are absent. For each prior accepted
state, its exact defer family is first reconstructed and validated; its
comparison core is then rebuilt at the post-t03 closure frontier, including the
accepted t03 successors as latest queue/artifact occurrences. Objects after
that closure frontier are excluded. A pre-t03 state-creation core is never the
prior comparison baseline.

All existing core fields remain unchanged. In particular,
`latest_queue_entry_ids`, `latest_queue_artifact_ids`, states, snapshot and
admission sequences, predecessor IDs, anchors, reasons, observations, and
candidate order include the prior state's t03 successors. A caller-supplied
digest is never stored or trusted; every core is rebuilt from typed logs.
`FractalBackpressureStateV02.lineage_refs`, its dataclass, and its schema
remain unchanged.

The same post-t03 `control_core_sha256` with only a higher requested round
creates no backpressure state, decision, queue, artifact, budget, t03
successor, or round-only identity. The expected prior t03 occurrence does not
self-change the control epoch. A changed dependency, budget, input,
activation, semantic observation/lineage, latest non-defer occurrence,
capacity, scope projection, or candidate order permits one bounded new epoch.
`admission_round` independently enforces at most one accepted state for that
exact round. The full material may be logged privately for diagnostics, but
only the core digest controls unchanged-defer suppression.

## 11. Exact Child Activation Disposition Matrix

| Precedence | Typed condition | Disposition | Rules and terminal | Exact reasons | Exact evidence |
|---|---|---|---|---|---|
| 1 | Structural, identity, lineage, parent-chain, prefix or contextual corruption | FAIL_CLOSED | No accepted t06 or terminal | Existing structural reason | No accepted gate evidence |
| 2 | Valid hard policy/authority/scope/budget/capacity denial or exact BLOCKED dependency | VALID_HARD_POLICY_AUTHORITY_SCOPE_OR_BUDGET_DENIAL | t06 -> t10 -> BLOCKED | `g2d_required_child_failure` | Exact precheck evidence tuple |
| 3 | No hard denial; at least one exact latest dependency is NEEDS_USER with queue reason `("g2d_resolvable_input_needs_user",)`, aligned artifact, and validated evidence | RESOLVABLE_INPUT_MISSING | t06 -> t11 -> NEEDS_USER | `g2d_resolvable_input_needs_user` | Exact precheck evidence tuple |
| 4 | No prior condition and an exact DEADEND dependency or exact bounded no-progress fact from relevant parent-slot revise history | NO_PROGRESS_OR_NONRESOLVABLE | t06 -> t12 -> DEADEND | `g2d_no_progress_deadend` | Exact precheck evidence tuple |
| 5 | Every required fact valid | PASS_FOR_CHILD_ACTIVATION | Child candidate path | Empty | Empty |

Mixed valid conditions use BLOCKED > NEEDS_USER > DEADEND > PASS. Caller
reasons and evidence are comparison values only. They must equal the exact
derived tuples. A no-child COMPLETED or DEGRADED branch does not exist.

D3 has no direct standalone typed user-resolvable missing-input carrier. The
accepted v0.3.4 ownership rule remains unchanged; v0.3.5 clarifies only the
current acceptance and test boundary:

1. Under the currently accepted D3 `RuntimeExecutionTopologyV02` geometry, no
   legal typed NEEDS_USER dependency carrier reaches the required parent
   FRACTAL_CELL activation precheck.
2. G2-C `needs_user` is `TERMINAL_NO_CONSUMPTION` and creates no G2-D
   topology.
3. Root FRACTAL_CELL slots depend on the accepted Root predecessor geometry,
   which does not originate a typed NEEDS_USER occurrence.
4. The accepted leaf projection contains no FRACTAL_CELL source that can
   create an alternative carrier.
5. D3 retains the conditional fail-closed validator. If a later accepted
   topology supplies the exact typed dependency, D3 may validate it only under
   the existing exact state, reason, artifact, evidence, lineage, and
   source-binding law.
6. The current D3 acceptance set does not require a positive standalone
   no-child NEEDS_USER execution proof.
7. A synthetic or manually resealed dependency occurrence cannot satisfy the
   condition.
8. Caller reasons, raw strings, copied PASS reports, `SimpleNamespace`
   objects, ID-only relations, D4-shaped dictionaries, and invented evidence
   remain forbidden.
9. The direct typed carrier remains future D4-owned exactly as stated in
   v0.3.4. This is preservation, not an ownership transfer.
10. A later D5 resolvable-missing-input case may become positive only through
    the actual separately authorized D4 typed family; it is not a D3
    acceptance witness.

Current D3 acceptance preserves positive no-child BLOCKED proof from exact
valid hard denial, positive no-child DEADEND proof from exact bounded
no-progress facts, and child-result NEEDS_USER boundary validation as a
separate exact result/artifact mapping surface where applicable. It requires
negative proof that no caller or synthetic fixture can manufacture a no-child
NEEDS_USER carrier. It neither requires nor permits fabrication of a positive
standalone no-child NEEDS_USER D3 witness. This adds no D3 type, field,
parameter, topology node, or topology edge; uses no D4 material as current D3
evidence; and does not weaken or remove the conditional validator.

The no-child precheck is derived once at the t06 origin frontier. t10-t12
reconstruct that historical frontier and require exact equality with the
VALIDATING reasons and evidence while independently validating current live
heads. No-child and child-result branches remain t07-forbidden.

## 12. t02-t12 Availability and Nullability Matrix

| Rule | Current/input | Dependencies | Observation/reasons | Child/result | Report/revise/backpressure | Budget law | D3 availability |
|---|---|---|---|---|---|---|---|
| t02 | Both absent | Empty | Empty | Absent | All absent | Exact committed CELL_CREATE anchors, also live at admission | Available |
| t03 | Exact deferred PENDING source/current input | Satisfied at state frontier | Source observations/evidence/advisories preserved; exact defer reason replaces source reasons | Absent | Exact already-accepted current-round backpressure state; target absent during decision | No budget successor; signature 83 target copies source anchors | Available once per deferred source in that control epoch |
| t04 | PENDING/current input exact | Satisfied | Empty | Absent | Backpressure absent; prefix proves one selected residual reservation using live global | No successor; target copies source anchors | Available |
| t05 | READY/current input exact | Current exact | Empty | Absent | All absent | Decision sees zero suffix; afterward exact START_NODE suffix advances from live heads and target stores candidates | Available |
| t06 local | RUNNING/current input exact | Current exact | Exact local material frozen at t06 origin; dependency-free evidence is exact `cell_input.evidence_refs` | Absent | Report/revise/backpressure absent | Decision sees zero suffix; afterward exact FINISH_NODE suffix advances from live heads and target stores candidates | Available only for listed D3-local kinds |
| t06 child result | RUNNING/current input exact | Current exact | Exact result projection frozen at t06 origin | Exact mutually bound result/artifact | Report/revise/backpressure absent | Decision sees zero suffix; afterward exact FINISH_NODE suffix advances from live heads and target stores candidates | Available |
| t06 no-child | RUNNING/current input exact | Current exact | Exact precheck material frozen at t06 origin; NEEDS_USER only from an exact typed NEEDS_USER dependency | Both absent | Report/revise/backpressure absent | Decision sees zero suffix; afterward exact FINISH_NODE suffix advances from live heads and target stores candidates | BLOCKED and DEADEND available in current accepted geometry; conditional NEEDS_USER validator retained but no positive standalone D3 witness is required or constructible |
| t07 | VALIDATING/current input exact | Current exact | Source tuples are validated against historical t06 origin, then target clears all tuples | Child/result and no-child branches forbidden | Exact settled revise observation and transient independently rebuilt structural PASS report; exact live-capacity reservation | Decision sees zero suffix; afterward exact REVISE suffix advances from live heads and target stores candidates | Structurally available; complete runtime orchestration remains D4 |
| t08-t09 | VALIDATING/current input exact | Historical t06 dependencies reconstructed; current dependencies exact | Copy exact validating tuples after replaying t06 origin | Exact child result for FRACTAL_CELL, otherwise absent | Validation report absent when outcome is independently reconstructed; revise/backpressure absent | Current decision sees current live heads and zero suffix; target copies source anchors | Available for D3-local or child-result mapping |
| t10-t11 | VALIDATING/current input exact | Historical t06 dependencies reconstructed; current dependencies exact | Copy exact validating tuples after replaying t06 origin | Exact child result or both absent for gate/local branch | Report absent when independently reconstructed; revise/backpressure absent | Current decision sees current live heads and zero suffix; target copies source anchors | Available for D3-local, child-result or gate mapping |
| t12 | VALIDATING/current input exact | Historical t06 dependencies reconstructed; current dependencies exact | Copy exact validating tuples after replaying t06 origin | Exact child result or both absent | Exact revise observation only for revise no-progress; otherwise absent | Current decision sees current live heads and zero suffix; target copies source anchors | Available for D3-local, child-result, gate or structural revise mapping |

For every non-PARENT_RETURN node all seven parent-return family components are
empty or null. PARENT_RETURN actual-family inputs remain unavailable in D3:
the evaluator returns `None` for the wholly absent family and fails closed
for a partial, copied, or nonempty family. No target queue or target artifact
is an evaluator input.

For every t08-t12 rule, queue support reasons and Transition decision reasons
remain separate. The queue entry carries the exact derived support tuple;
`TransitionDecisionV01.reason_code` carries the exact Registry reason. Local
DEGRADED uses queue support `("g2d_partial_failure_recorded",)` while t09 uses
decision reason `g2d_transition_degraded_recorded`. The child-result branch
copies the exact validated `child_result.reason_codes` at t06 and t08-t12;
its DEGRADED support tuple is likewise
`("g2d_partial_failure_recorded",)`.

Every t08-t12 evaluator uses the current terminal-decision live heads only as
current contextual state. It locates the source VALIDATING occurrence's exact
FINISH_NODE segment, reconstructs the historical pre-segment t06 prefix and
origin heads, and rebuilds the same local/precheck/result branch. The rebuilt
tuples must equal the VALIDATING tuples exactly; later budget progress cannot
change output digests, evidence, advisories, or support reasons.

The t07 `validation_report` is transient and independently reconstructed from
the exact revise observation. Before it is used, a D3-local VALIDATING source
is replayed against its historical t06 origin; child-result and no-child
sources fail the t07 branch. The report is neither retained in the D3 report
prefix nor accepted because a caller supplied a matching PASS value.

POST_VV, GT_ADVISORY, and PARENT_RETURN cannot use
`D3_LOCAL_OBSERVATION_MATERIAL_V02`. Their t06 and terminal decisions remain
unavailable until D4 supplies the actual typed report family.

## 13. Queue and Budget Continuity Matrix

| Boundary | Exact contextual law |
|---|---|
| Anchor lookup | Current queue cell/global IDs resolve exact immutable anchor objects in the settled log; each anchor equals or is an ancestor of its applicable live head |
| Signature 90 live lookup | Reconstruct pre-event live heads from the supplied accepted pre-decision budget prefix as-is; candidate suffix is absent |
| Signature 83 live lookup | The accepted decision exists and any required candidate suffix is the current tail; exclude that suffix only to reconstruct pre-event heads, then validate and consume it for target anchors |
| Signature 89 suffix relation | Target queue and any required candidate suffix are already settled; projection validates anchors and creates no budget |
| Root t02 | One exact ROOT_GLOBAL_AND_CELL CELL_CREATE object; anchors and live cell/global heads are the same object |
| Child t02 | Exact child-local then paired global CELL_CREATE objects after validated allocation, scope and ACTIVATE; both are live at admission |
| t03 PENDING -> PENDING | Exact source anchors; capacity/backpressure uses live global; no successor; target copies source anchor IDs |
| t04 PENDING -> READY | Exact source anchors; residual capacity uses live global plus latest READY reservations; no successor; target copies source anchor IDs |
| t05 READY -> RUNNING | Decision from zero-suffix prefix; then consumes one logical reservation and builds exact START_NODE suffix from live heads; Root has one candidate, child has local then global pair; target stores candidate IDs |
| t06 RUNNING -> VALIDATING | Decision and observation material from zero-suffix t06 origin; then builds exact FINISH_NODE suffix from live heads; global parallelism -1; target stores candidates and frozen tuples |
| t07 VALIDATING -> READY | Replay source t06 origin, prove revise observation/report and reservation, build decision from zero-suffix prefix, then build exact REVISE suffix; target stores candidates and clears tuples |
| Non-PARENT_RETURN t08-t12 | Replay historical t06 origin tuples while separately validating current live heads; no successor; target copies source VALIDATING anchors and tuples |
| Root FINALIZE, D4-forward | One unique ROOT_GLOBAL_AND_CELL FINAL advances from the exact live Root/global head |
| Child FINALIZE, D4-forward | Child-local FINAL advances from the live child-local head; paired global ACTIVE FINALIZE advances from the live global head; no child-global FINAL |
| CHILD_AGGREGATE, D4-forward | Advances from the latest child-completion global head; exact child-local FINAL pair; result-ID event ref; counters unchanged |

For t03-t12, signature 90's explicit `cell_budget_before` and
`global_budget_before` equal the source queue's anchor objects. They prove
queue binding, not live-head selection. For t05/t06/t07, the pre-event live
heads are reconstructed independently from the pre-decision prefix and only
they may become event predecessors after the decision is accepted. Signature
90 always receives suffix length zero. Signature 83 later receives the exact
post-decision suffix as the current log tail; signature 89 receives that suffix
already settled. For t03/t04 and non-PARENT_RETURN t08-t12, the suffix remains
empty and targets preserve source anchors.

A foreign same-counter budget, incomparable anchor, future anchor, event from
a non-live predecessor, axis fork, hidden queue refresh, or queue-ID mutation
fails closed. `FINAL` never returns `ACTIVE` and has no successor.
`CELL_CREATE` is the sole cell debit. Duplicate `CELL_CREATE`, `FINALIZE`, or
`CHILD_AGGREGATE` fails. Child local/global pairing and the latest
post-aggregate global budget are reconstructed from exact log adjacency and
object equality, not IDs alone.

### Mixed READY/RUNNING Constructibility

CTC-02 accepts the minimal reference-policy correction
`max_parallelism: 4 -> 3`. The separately authorized lower D1 policy/schema
repair and complete source-derived identity rebuild were completed before D3
implementation resumed. This acceptance action changes no runtime, schema,
preflight, or derived identity bytes.

The prior G0 -> G4 sequence remains historical explanation of queue anchors
versus live heads, but it is not a constructible positive scheduler acceptance
witness for the accepted topology. The exact accepted positive witness is:

Definitions:

- P1 and P2 are the two accepted parent FRACTAL_CELL slots.
- C1 and C2 are the two child cells derived from the accepted planned child
  slots.
- C1N0 and C2N0 are their accepted leaf node-0 occurrences.
- `max_parallelism=3`.
- `occupied = current_parallelism + latest READY count`.
- `residual = max_parallelism - occupied`.
- Every queue row, artifact, budget, input, scope projection, and decision is
  an actual accepted object derived in frozen construction order.

Round R0 - parent slots running:

1. P1 and P2 have each passed their exact PENDING -> READY transition.
2. P1 and P2 then pass READY -> RUNNING in frozen state-class and admission-key
   order.
3. The live global budget has `current_parallelism=2`.
4. No synthetic reservation or queue occurrence exists.

Child creation frontier:

5. While P1 and P2 remain RUNNING, both child activation prechecks pass from
   their exact parent t02 -> t04 -> t05 chains.
6. C1 and C2 are created through exact accepted ACTIVATE and CELL_CREATE
   budget pairs.
7. C1N0 and C2N0 are admitted as actual PENDING occurrences with actual
   artifacts and validated child inputs.
8. Child creation itself does not consume a RUNNING admission slot.

Round R1 - one residual reservation and S0:

9. At round start, `current_parallelism=2`, READY count is zero,
   `occupied=2`, and `residual=1`.
10. The frozen scheduler considers dependency-satisfied PENDING candidates in
    exact state-class order and then admission-key order.
11. C1N0 is the deterministic selected candidate and receives the sole t04
    READY reservation.
12. C2N0 remains an exact dependency-satisfied PENDING candidate.
13. After C1N0 becomes READY, `current_parallelism=2`, READY count is one,
    `occupied=3`, and `residual=0`.
14. Function 88 evaluates the complete accepted source-bound prefix and
    creates exactly one S0 whose deferred source tuple contains C2N0.
15. S0 creates exactly one contiguous t03 decision, PENDING successor, queue
    artifact, contextual pair validation, and retained queue report for C2N0.
16. No t03 budget successor is created.

Round R2 - C1 start and S1:

17. Existing READY work is considered before deferred PENDING work.
18. C1N0 passes t05 READY -> RUNNING.
19. The START_NODE successor advances the live global budget from
    `current_parallelism=2` to `current_parallelism=3`.
20. READY count changes from one to zero, so `occupied=3` and `residual=0`
    remain unchanged.
    Because one occurrence per (cell_id,node_id) is processed at most once in one scheduler round, the newly created C1N0 RUNNING successor is not reprocessed through t06 in R2; its applicable t06 occurs only at a later accepted frontier.
21. The live-global identity/counters and exact state-class surface change the
    controlling core.
22. C2N0 remains the exact dependency-satisfied PENDING candidate through its
    accepted t03 history.
23. Function 88 creates exactly one S1 and exactly one new contiguous t03
    closure for C2N0 under the changed controlling core.

Unchanged suppression:

24. A later evaluation with the same S1 post-t03 controlling core and only a
    higher requested round creates no new state, decision, queue entry,
    artifact, budget, report, or round-only identity.
25. Raw S0 and S1 t03 histories remain present and ordered in the complete
    prefix.

Capacity release and admission:

26. A later exact t06 completion of any applicable RUNNING occurrence releases
    one live global parallelism slot.
27. `current_parallelism=2`, READY count remains zero, `occupied=2`, and
    `residual=1`.
28. C2N0 then passes through t04 under the ordinary selected residual
    reservation law.
29. The sequence terminates without scheduler spin and without dropping work.

This witness requires no fifth candidate and permits no synthetic candidate,
topology node, or topology edge. The existing two parent slots and two
accepted child node-0 occurrences are sufficient after `max_parallelism=3`.
It remains queue-, artifact-, input-, scope-, budget-, transition-, and
source-bound. No fork occurs, no queue snapshot is refreshed, no historical
queue anchor becomes a new event predecessor, and every budget event
serializes on the one live global axis. Each child retains its own linear
local axis. Same-cell anchors may be historical ancestors of that child's live
local head; a cross-cell anchor never substitutes for another child's local
axis.

Bounds remain `max_depth=3`, `max_fan_out=4`, `max_total_cells=21`, and
`max_provider_calls=0`; the accepted corrected reference `max_parallelism` is
three.
t03 still creates no budget successor. State-class order, admission-key order,
and unchanged post-t03 suppression remain exact and unchanged. Scope remains
EQUAL or proven NARROWER, child capability remains a subset, child
prohibitions remain a superset, TTL never widens, and immediate parent, depth,
budgets, and proof lineage remain exact. Only full_fractal may recurse.

## 14. Cell-Aware Round, Backpressure, and No-Spin Matrix

| Obligation | Frozen rule |
|---|---|
| Latest key | Exactly `(cell_id, node_id)` |
| Chain | One initial occurrence and one immediate-predecessor chain per key |
| Sequence | Snapshot increments exactly one; admission round follows accepted round order |
| Ambiguity | Equal-sequence fork, duplicate same-round state, gap, skip, reverse, reorder, cross-cell, cross-node and cycle fail closed |
| Capacity | `occupied = live_global.current_parallelism + latest_READY_count` |
| t04/t07 | Consume one selected residual logical reservation |
| t05 | READY becomes RUNNING while occupied remains unchanged |
| t06 | Releases exactly one RUNNING slot |
| Deferred work | Only dependency-satisfied PENDING entries blocked solely by zero residual capacity |
| Exclusions | Dependency-unsatisfied PENDING and budget exhaustion are not backpressure |
| State count | `admission_round` in the audit envelope enforces at most one accepted backpressure state per exact round |
| State closure | One accepted state has one complete contiguous t03 closure and exactly one direct successor/artifact per deferred source |
| Comparison | Current pre-new-state core is compared with each prior state's exact post-t03 closure core, never its pre-t03 creation core |
| Unchanged defer | Identical post-t03 `control_core_sha256` with only a higher round creates no state, decision, queue, artifact, budget, second t03 or round-only identity |
| Reconsideration | Dependency, queue anchor, live global budget, input, activation, observation, lineage, latest non-defer semantic occurrence, scope, capacity, or candidate-order change opens one bounded epoch |
| Expected t03 | The prior epoch's required t03 successor is completed recording, not a self-generated control change |
| Ordering | Exact state-class order then admission key; deferred IDs are the deterministic unselected suffix |
| No work loss | Raw t03 history remains visible; no drop, duplicate, normalization, resort or post-hoc grouping |
| No-spin | Suppressed unchanged epochs create nothing; bounded future progress waits, otherwise no progress fails closed with the existing reason |

`admission_round` and `prior_backpressure_state_ids` remain audit-envelope
fields and are excluded from `control_core_sha256`. A higher round number alone
therefore cannot manufacture progress or a new backpressure identity. Each
prior state's complete t03 closure is first reconstructed from typed queue and
artifact logs. Its comparison core is then rebuilt at the exact post-t03
closure frontier. The current core is rebuilt at the future round's
pre-new-state frontier. No caller digest or prior-state ID alone proves the
comparison, and a pre-t03 state-creation core is never used as the baseline.

Every accepted `FractalBackpressureStateV02.global_budget_id` binds the exact
live Root/global head at that frontier. Deferred queue entries may retain older
anchors proven ancestral to that head; because no budget event is built from
those anchors, they are not stale event predecessors. Capacity uses the live
global `current_parallelism` plus the latest READY count. Changed live-global
identity or counters changes the controlling core and permits one bounded
reconsideration; unchanged core with only a higher round remains suppressed.

After suppression, no new round-only state or t03 occurrence exists. If a
RUNNING or READY occurrence can produce future progress, waiting remains under
the existing bounded deterministic runtime law. If no queue transition,
activation/CELL_CREATE, budget, deterministic local result, result, or report
progress exists and no RUNNING/READY future-progress source exists, the
scheduler fails closed with `g2d_no_progress_deadend`; it never increments
rounds indefinitely.

## 15. D3/D4 Availability Boundary

D3 owns contextual execution of t02, t03, t04, and t05. It owns t06 only for
an exact D3-local deterministic observation, exact child-result return, or
exact no-child gate disposition. It owns structural t07 constructibility only
when the VALIDATING source is replayed against its historical t06 origin and
the exact revise observation and independently reconstructed report are
settled. It owns t08-t12 only when frozen VALIDATING tuples replay exactly from
their historical t06 origin for D3-local observations, FRACTAL_CELL
child-result mappings, no-child gate mappings, and the structural
revise-no-progress case specified in Section 12.

D3 does not activate actual POST_VV report semantics, GT_ADVISORY report
semantics, the PARENT_RETURN typed family, t13-t17, result construction,
runtime-report construction, result/report artifacts, causal execution, final
bundle construction, or the package facade.

D3 no-child NEEDS_USER is available only through an exact typed NEEDS_USER
dependency occurrence and its aligned artifact/evidence. A direct standalone
user-resolvable missing-input fact has no D3 carrier. Any such future carrier
belongs to a separately authorized D4 typed report or input family.

D4 remains the sole owner of actual ResultProposal construction, actual Post
V&V and GT family construction, actual PARENT_RETURN typed-family construction
and activation, partial-failure and cell-result construction, runtime trace and
report construction, result/report artifact construction, t13-t17, causal
execution, the complete runtime bundle, and sole package-facade integration.
D3 may validate an exact externally visible child-result/artifact pair at its
queue boundary under IFC-04 but cannot construct or simulate any D4 family.

For future D4 completion, terminal queue budget IDs remain immutable lineage
anchors. Root `FINALIZE` advances from the exact live Root/global head; child
local `FINALIZE` advances from the exact live child-local head; paired child
completion global `FINALIZE` advances from the exact live global head; and
`CHILD_AGGREGATE` advances from the exact latest child-completion global head.
A terminal queue anchor is an event predecessor only when reconstruction proves
that it is also the applicable live head. This ruling does not authorize or
start D4.

This boundary still permits D3 to prove the public parent FRACTAL_CELL
t02 -> t04 -> t05 chain because that chain uses topology, queue, budget,
dependency, cell-input, reservation, and artifact values already present in
the settled prefix. It requires no fabricated child result or D4 report. The
D3 retained report prefix remains limited to the seven ordered groups in
Section 7; transient and future D4 reports are reconstructed or unavailable,
never smuggled into that prefix.

## 16. Validation-Group 9-12 Reconciliation

| Group | Contextual closure |
|---|---|
| 9 | Exact source occurrence, actual typed source context, six parent forms, immutable queue anchors, anchor ancestry, historical occurrence frontier, t06-origin observation/reason replay, transition-specific target-anchor law, predecessor chain, nullability, dependency-free evidence, separated queue/Transition reasons, result/gate exclusivity, and dependency wait derive from the complete source-bound settled prefix and local profiles |
| 10 | Signature 90's zero-suffix pre-decision prefix, signatures 83/89 post-decision suffix, one unique live head per axis, event successor from live head only, no fork, Root/child pairing, allocation-anchor/live-head separation, delta, debit, finalization, aggregate and bounds derive from the settled budget log |
| 11 | Immutable parent allocation basis, live capacity budgets, scope EQUAL/NARROWER, capabilities, prohibitions, TTL, parent, depth, exact projection/input lineage, source-aware contextual validation, and no caller-selected stale global derive from the actual typed source family and complete settled prefix |
| 12 | Full-fractal-only recursion, actual parent slot, cell-aware latest state, the exact R0/R1/R2 constructibility witness at accepted corrected reference `max_parallelism=3`, live-global capacity plus READY count, proven historical deferred anchors, historical t06 material replay, backpressure live-global binding, fork rejection, parent-slot-local revise history, one state per round, one complete t03 closure per state, one direct t03 successor per deferred source, exact deferred order, current pre-new-state core versus prior post-t03 closure core, unchanged higher-round suppression, changed-state reconsideration, no second t03 in one control epoch, preserved raw queue history, no work drop, and no-spin derive from the complete source-bound settled prefix and round profile |

No copied reason, evidence tuple, PASS report, state label, prefix, fixture
constant, ID-only relation, or arbitrary deterministic convention supplies
authority for these groups.

The exact retained/transient report partition and every complete-prefix closure
law in Section 7 apply cumulatively to all four groups. Direct untyped
NEEDS_USER classification and cross-cell revise evidence are unavailable.

### Accepted v0.3.6 Final Proof Ledger

The final implementation and complete-file execution ledger prove these
positive cases without any additional public geometry change beyond the
accepted v0.3.5 function-88 parameter delta and reference-policy value
correction:

1. the exact R0 parent P1/P2 RUNNING frontier at live
   `current_parallelism=2`;
2. exact ACTIVATE/CELL_CREATE construction of C1/C2 and actual PENDING
   C1N0/C2N0 occurrences without consuming a RUNNING slot;
3. R1 selects C1N0 for the sole residual READY reservation and creates S0 plus
   one exact t03 closure for deferred C2N0;
4. R2 starts C1N0, advances live parallelism to three, changes the controlling
   core, and creates one bounded S1 closure for C2N0;
5. a higher round equal to the S1 post-t03 core creates nothing;
6. exact t06 capacity release permits ordinary t04 admission of C2N0;
7. t06 from a historical RUNNING anchor using the latest live global head;
8. t04 from a historical PENDING anchor using latest live capacity;
9. a child same-cell historical local anchor and cross-cell independent local
   heads sharing one global head;
10. backpressure bound to the live global head while deferred queues retain
    older valid anchors; and
11. the D4-forward terminal-anchor versus live-finalization distinction.

The CTC-01 D3 acceptance boundary requires positive exact no-child BLOCKED and
DEADEND proofs, preserves separate exact child-result NEEDS_USER mapping where
applicable, and requires negative proof that caller or synthetic material
cannot manufacture a no-child NEEDS_USER carrier. It does not require a
positive standalone no-child NEEDS_USER D3 witness.

The final execution ledger rejects use of a historical queue anchor as a
candidate event predecessor, a budget fork, two successors from one live
head, a caller-supplied false latest head, an incomparable or foreign anchor, a wrong
child-local axis, Root cell/global divergence, hidden queue refresh, queue-ID
mutation, a t03/t04 budget successor, a t05 target retaining the old anchor,
backpressure bound to a historical queue global instead of the live global,
candidate-suffix interleaving or pair reversal, a candidate successor absent
from the settled log, and finalization from a terminal queue anchor that is not
live. The final execution ledger also rejects dependency-unsatisfied PENDING
as deferred work,
budget exhaustion as backpressure, a caller-created queue row, a fourth
occupied slot under accepted corrected `max_parallelism=3`, any missing, extra,
duplicated, reordered, or interleaved t03 closure member, two t03 successors
for one source in one control epoch, comparison to a prior pre-t03 core,
higher-round-only construction, stale or foreign live-global budget, use of a
historical queue anchor as a new event predecessor, erased or normalized raw
t03 history, and scheduler spin. No fifth candidate, synthetic queue row, or
arbitrary `0 RUNNING + 3 READY` fixture is an acceptance witness. These
obligations are satisfied by the final 57/57 ledger; this metadata acceptance
action does not rerun them.

The final function-88 tests pass the actual typed source family directly and
prove independent source-context validation, source-binding reconstruction,
topology-seed and topology reconstruction, source-aware queue-artifact
validation, existing contextual scope/input validation, and exact retained
report typed-object and canonical-byte equality in accepted order. The final
function-88 tests reject `source_context=None`, IDs or labels in place of typed
sources, mutable
registry or reverse-lookup authority, copied or constructed PASS reports,
`SimpleNamespace` substitutes, reordered reports, and performance shortcuts
that omit source proof. These proofs are included in the final complete-file
ledger and are not rerun by this metadata acceptance action.

The final implementation additionally proves these decision-frontier
positives:

1. a t05 evaluator sees the pre-decision log ending at the current live head;
2. a t06 evaluator sees no `FINISH_NODE` candidate;
3. a t07 evaluator sees no `REVISE` candidate;
4. signature 83 accepts the exact post-decision candidate suffix; and
5. signature 89 accepts the already-settled target/suffix relation.

The final decision-frontier tests reject a candidate `START_NODE` before t05,
candidate `FINISH_NODE` before t06, candidate `REVISE` before t07, wrong
decision/event ref, suffix
interleaving, a suffix that is not the current signature-83 frontier tail, and
a candidate constructed from a non-live predecessor.

The final observation-origin positives are exact:

1. t06 local material at live G1 creates one frozen output/evidence tuple;
2. an unrelated accepted event advances live global to G2;
3. t08/t09 reconstruct historical t06 origin G1 and copy the tuple unchanged
   while separately observing current live G2;
4. a t06 no-child precheck at G2 creates frozen gate evidence;
5. another accepted event advances live global to G3;
6. t10/t11/t12 reconstruct historical precheck origin G2 and copy exact
   reasons/evidence; and
7. t07 validates the source t06 origin before clearing tuples.

The final observation-origin tests reject terminal material resealed with
later current heads, an output digest changed only by unrelated budget
advancement, no-child evidence changed
only by later head advancement, a missing or ambiguous t06 candidate segment,
a wrong RUNNING predecessor, t06 decision, or t06 dependency occurrence, and a
terminal current live head substituted for a t06 origin head. Every
v0.3.2-v0.3.4 queue-anchor/live-head law remains binding, but historical
G0 -> G4 occupancy is not a current positive acceptance witness under accepted
v0.3.5. These obligations are satisfied by the final complete-file ledger and
are not rerun here.

The final implementation additionally proves these post-t03 closure
positives:

1. a first saturated round creates exactly one state S0;
2. S0 creates exactly one t03 successor and aligned artifact for every
   deferred source in exact order;
3. the S0 post-t03 closure core is reconstructed from the complete typed logs;
4. a higher round with no controlling change compares equal to that core and
   creates nothing;
5. a dependency-state change creates a different core, exactly one new state
   S1, and one exact new t03 closure;
6. a live-global-budget change creates a different core and permits one
   bounded reconsideration;
7. a cell-input, activation, observation, or candidate-order change likewise
   permits one bounded new epoch; and
8. every raw t03 occurrence and artifact remains visible in the queue and
   artifact logs.

The final post-t03 closure tests reject comparison against S0's pre-t03
state-creation core, a missing or extra t03 successor, two t03 successors for
one source in one epoch, a
reordered or noncontiguous closure, a wrong predecessor, t03 reason or
decision, a t03 budget successor, altered anchors or observations, a prior
state without complete closure, a second state in the same round, a state or
second t03 created by a higher round alone, erased or normalized queue
history, and scheduler spin. Every earlier v0.3.3 test obligation remains
binding. These obligations are satisfied by the final complete-file ledger
and are not rerun here.

## 17. Preserved Counts and Nonclaims

```text
TOTAL_G2D_TYPE_COUNT=20
SERIALIZED_IDENTITY_TYPE_COUNT=18
RUNTIME_ONLY_CONTEXT_TYPE_COUNT=2
SCHEMA_DEFINITION_COUNT=18

FRACTAL_RUNTIME_MODULE_PUBLIC_FUNCTION_COUNT=110
FRACTAL_RUNTIME_TRANSITION_PUBLIC_FUNCTION_COUNT=6
TOTAL_G2D_PUBLIC_FUNCTION_COUNT=116

D1_MODULE_PUBLIC_FUNCTION_COUNT=74
D2_MODULE_PUBLIC_FUNCTION_COUNT=81
D3_MODULE_PUBLIC_FUNCTION_COUNT=90
D4_MODULE_PUBLIC_FUNCTION_COUNT=110

PUBLIC_G2D_REASON_COUNT=220
VALIDATION_TARGET_COUNT=34
FAILURE_STAGE_COUNT=30
TRANSITION_PROFILE_RULE_COUNT=17

SETTLED_RUNTIME_PREFIX_COMPONENT_COUNT: 8
AMENDED_D3_PUBLIC_SIGNATURE_COUNT: 7
PRIVATE_CANONICAL_MATERIAL_PROFILE_COUNT: 3
ACTIVE_G2D3_QUEUE_ROLE_ALIAS_PROFILE_COUNT: 3
FUTURE_DOCUMENTED_ROLE_ALIAS_PROFILE_COUNT: 1
```

No public dataclass, runtime context type, serialized identity, schema
definition, function, reason, validation target, failure stage, ABI artifact
type, Transition rule, or package attribute is added. Existing public function
88 alone gains one accepted required keyword-only `source_context` parameter;
the public function count and amended-signature count remain unchanged. No
fourth private canonical material profile, ninth prefix component, eighth
amended signature, or other public parameter is introduced.

This document makes no public-release, RC2, production-readiness, production
security, provider, model, network, connector, external DRS, authority,
permission, packet, receipt, FinalOutput, DRS-write, or real-world-effect
claim.

### Accepted Identity-Impact Register

Accepted v0.3.6 records the Profile D implementation and its final proof
ledger. It accepts only the identity impact enumerated in this section and
does not rewrite any historical accepted artifact.

Under accepted v0.3.5, the lower repair is completed on the current basis.
`FractalRuntimePolicyV02.max_parallelism` is three in implementation and its
source-derived identity family was rebuilt from exact canonical material.
Every downstream typed identity whose material directly or transitively
depends on `policy_id`, `max_parallelism`, topology seed, topology, budget,
queue, input, scope, or backpressure material follows those rebuilt sources.
No old ID is copied, no object is resealed around an obsolete policy identity,
no partial compatibility alias is created, and no historical artifact is
rewritten.

The accepted rebuild inventory includes at minimum:

- `FractalRuntimePolicyV02`;
- `RuntimeTopologySourceBindingV02`;
- `RuntimeTopologySeedV02`;
- Root and planned child cell identities where policy identity participates;
- `RuntimeTopologyNodeV02`;
- `RuntimeTopologyEdgeV02`;
- `RuntimeAssignmentV02`;
- `RuntimeExecutionTopologyV02`;
- `FractalRuntimeBudgetV02`;
- `FractalCellQueueEntryV02` and queue Kernel artifacts;
- `FractalCellInputV02`;
- `ParentChildScopeProjectionV02`;
- `FractalReviseObservationV02`;
- `FractalBackpressureStateV02`;
- retained validation reports whose validated object IDs change; and
- later D4 result, report, and bundle identities only as future downstream
  impact, not current D3 implementation.

Private profile version v0.3.1 is not a shortcut for this ordinary identity
churn and remains unchanged.

### Preserved IFC Obligations

- **IFC-01.** Complete-prefix validation must be fully source-bound. The
  accepted function-88 source-context input supplies the missing typed family;
  the accepted runtime implements this binding and the final ledger proves it.
- **IFC-02.** For PARENT_RETURN in D3, a wholly absent future family remains
  unavailable and returns no decision. Any partial, copied, nonempty,
  malformed, or substituted future family fails closed. D3 does not construct
  the D4 family.
- **IFC-03.** `D3_CHILD_ACTIVATION_PRECHECK_MATERIAL_V02` retains its complete
  accepted ordered field set. A disposition-only assertion is insufficient.
  The final tests prove exact field set, order, canonical equality, source
  projection, and field-by-field mutation rejection.
- **IFC-04.** D3 may validate an externally visible child-result/artifact pair
  at the queue boundary only with full exact mutual binding across every
  frozen result field, canonical artifact projection, envelope, trace, parent
  geometry, and canonical equality. D3 does not construct ResultProposal,
  Post V&V, GT, runtime report, or final bundle.
- **IFC-05.** The exact scheduler classes and order remain: (1) READY; (2)
  RUNNING with an exact result or gate outcome available; (3) VALIDATING
  eligible for t08-t12 terminal recording; (4) VALIDATING eligible for t07
  bounded revise; (5) dependency-satisfied PENDING eligible for t04; and (6)
  capacity-deferred PENDING eligible for t03. Each class uses the accepted
  admission key. The CTC-02 witness follows this order without weakening or
  reordering it.

The final G2-D3 ledger satisfies the G2-D3 IFC obligations above. IFC-02 and
IFC-04 preserve the exact D3/D4 boundary; no D4 family is implemented or
started, and G2-D and Gate 2 remain open.

## 18. Implementation Authorization State

Accepted v0.3.6 is the controlling accepted addendum only for Profile D
`CHILD_ACTIVATION_PARENT_DEPENDENCY_FREE_EVIDENCE_ALIAS`, the accepted active
queue-role-alias count of three, its identity-impact register, its proof
ledger, and its final closing flags. Accepted v0.3.5 remains historical
accepted authority for CTC-01, CTC-02, CTC-03, and every unaffected ruling.
Accepted v0.3.4 remains historical accepted evidence.

The accepted implementation state is:

- reference runtime and schema `max_parallelism=3`;
- function 88 requires `source_context`;
- downstream identities were rebuilt on that basis;
- Profile D is implemented, contextually proven, integration-proven, and
  accepted;
- G2-D3 implementation is completed but not committed; and
- staging remains unchanged, with no commit or push.

The exact final focused G2-D file ledger collected 57 tests and passed all 57,
with zero failures, skips, or xfails. Pytest reported 19385.32 seconds
(`5:23:05`), the wrapper elapsed time was `5:23:06`, the test exit code was
zero, and the final repository guard passed. The external execution log has
SHA-256
`17003824f527e8ca1adbf9e256ca61d9cbc085939fe0badb02ec3535f0c90628`,
47840 bytes, and 575 LF lines.

The exact accepted production evidence identities are runtime SHA-256
`dcfee5bef674c8b90e875e04fa64312df3db021bafdd0c6e476f2bb01fe4a386`,
schema SHA-256
`e62f693cc24a0562ca2955b011530916a85598dd00026f6dbadb80b6b9eb94ac`,
and preflight SHA-256
`8e3ae3b04a9b622329e85529edb8a150739cc787b341f1609438dbde00412e79`.
The pre-acceptance test-file evidence identity that received the 57/57 run is
SHA-256
`ae7d3e5438ff51c1269b2c11c6b9e28beb85792d644847f25230a12b789058b1`;
it is not the post-acceptance metadata-test identity.

G2-D4 is not authorized or started. G2-E and G2-F are not started. G2-D and
Gate 2 remain open. This acceptance creates no provider, model, network,
connector, external DRS, permission, packet, receipt, FinalOutput, authority,
release, publication, or real-world effect. This metadata action neither
changes production bytes nor self-authorizes staging, commit, push, or any
later slice.

## 19. Machine-Readable Closing Flags

```yaml
G2D3_V036_CONTRACT_DRAFT=false
G2D3_V036_CONTRACT_ACCEPTED=true
G2D3_V036_GUARDIAN_REVIEW_STATUS=ACCEPTED
G2D3_V035_REMAINS_HISTORICAL_ACCEPTED=true
G2D3_V036_SUPERSESSION_BOUNDARY_NARROW=true
G2D3_ADDENDUM_REVISION=v0.3.6
G2D3_ADDENDUM_GUARDIAN_STATUS=ACCEPTED
G2D3_ACCEPTED_V034_BASIS_REVISION=v0.3.4
G2D3_ACCEPTED_V034_BASIS_SHA256=7ea510c4bea2b995074bd9dfdb9108cc51145526c559638964f8a9b70723e69e
G2D1_POLICY_SCHEMA_REPAIR_REQUIRED=true
G2D1_POLICY_SCHEMA_REPAIR_AUTHORIZED=true
G2D1_POLICY_SCHEMA_REPAIR_STARTED=true
G2D1_POLICY_SCHEMA_REPAIR_COMPLETED=true
G2D3_IMPLEMENTATION_AUTHORIZED=true
G2D3_IMPLEMENTATION_RESUMED=true
G2D3_IMPLEMENTATION_COMPLETED=true
G2D3_IMPLEMENTATION_COMMITTED=false
G2D3_FINAL_COMPLETE_DFILE_EXECUTED=true
G2D3_FINAL_COMPLETE_DFILE_COLLECTION=57
G2D3_FINAL_COMPLETE_DFILE_PASSED=57
G2D3_FINAL_COMPLETE_DFILE_FAILED=0
G2D3_FINAL_COMPLETE_DFILE_SKIPPED=0
G2D3_FINAL_COMPLETE_DFILE_XFAIL=0
G2D3_FINAL_COMPLETE_DFILE_DURATION_SECONDS=19385.32
G2D3_FINAL_COMPLETE_DFILE_REPORTED_DURATION=5:23:05
G2D3_FINAL_COMPLETE_DFILE_WRAPPER_ELAPSED=5:23:06
G2D3_FINAL_COMPLETE_DFILE_EXIT_CODE=0
G2D3_FINAL_COMPLETE_DFILE_RUN_RESULT=G2D3_FINAL_COMPLETE_DFILE_PASS
G2D3_FINAL_COMPLETE_DFILE_REPOSITORY_GUARD=PASS
G2D3_FINAL_COMPLETE_DFILE_LOG_SHA256=17003824f527e8ca1adbf9e256ca61d9cbc085939fe0badb02ec3535f0c90628
G2D3_FINAL_COMPLETE_DFILE_LOG_BYTES=47840
G2D3_FINAL_COMPLETE_DFILE_LOG_LF_LINES=575
G2D3_ACCEPTED_RUNTIME_SHA256=dcfee5bef674c8b90e875e04fa64312df3db021bafdd0c6e476f2bb01fe4a386
G2D3_ACCEPTED_SCHEMA_SHA256=e62f693cc24a0562ca2955b011530916a85598dd00026f6dbadb80b6b9eb94ac
G2D3_ACCEPTED_PREFLIGHT_SHA256=8e3ae3b04a9b622329e85529edb8a150739cc787b341f1609438dbde00412e79
G2D3_PRE_ACCEPTANCE_TEST_SHA256=ae7d3e5438ff51c1269b2c11c6b9e28beb85792d644847f25230a12b789058b1
G2D4_IMPLEMENTATION_AUTHORIZED=false
G2D4_STARTED=false
CTC01_ACCEPTANCE_BOUNDARY_CLARIFIED=true
CTC01_POSITIVE_STANDALONE_NO_CHILD_NEEDS_USER_REQUIRED=false
CTC02_REFERENCE_MAX_PARALLELISM_ACCEPTED=3
CTC02_ROUND_EXPLICIT_WITNESS_ACCEPTED=true
CTC02_LOWER_D1_POLICY_SCHEMA_REPAIR_REQUIRED=true
CTC03_FUNCTION88_SOURCE_CONTEXT_PARAMETER_ACCEPTED=true
FUNCTION88_REQUIRED_PARAMETER_ADDITION_COUNT=1
V035_FUNCTION88_REQUIRED_PARAMETER_ADDITION_COUNT=1
V036_NEW_PUBLIC_PARAMETER_COUNT=0
CURRENT_PREFLIGHT_REFERENCE_MAX_PARALLELISM=4
CURRENT_RUNTIME_REFERENCE_MAX_PARALLELISM=3
CURRENT_SCHEMA_REFERENCE_MAX_PARALLELISM=3
ACCEPTED_CONTRACT_REFERENCE_MAX_PARALLELISM=3
SETTLED_RUNTIME_PREFIX_COMPONENT_COUNT=8
AMENDED_D3_PUBLIC_SIGNATURE_COUNT=7
PRIVATE_CANONICAL_MATERIAL_PROFILE_VERSION=v0.3.1
PRIVATE_CANONICAL_MATERIAL_PROFILE_COUNT=3
ACTIVE_G2D3_QUEUE_ROLE_ALIAS_PROFILE_COUNT=3
PROFILE_D_DRAFTED=true
PROFILE_D_ACCEPTED=true
PROFILE_D_IMPLEMENTATION_CANDIDATE_PRESENT=true
PROFILE_D_IMPLEMENTATION_PROVEN=true
PROFILE_D_INTEGRATION_SENTINEL_PASS=true
PROFILE_D_NAME=CHILD_ACTIVATION_PARENT_DEPENDENCY_FREE_EVIDENCE_ALIAS
FUTURE_DOCUMENTED_ROLE_ALIAS_PROFILE_COUNT=1
QUEUE_BUDGET_TEMPORAL_ROLE_MODEL_FROZEN=true
QUEUE_OCCURRENCE_BUDGET_ANCHOR_ROLE_FROZEN=true
LIVE_EXECUTION_BUDGET_HEAD_ROLE_FROZEN=true
CANDIDATE_BUDGET_SUFFIX_ROLE_FROZEN=true
TRANSITION_DECISION_BUDGET_PREFIX_IS_PRE_DECISION=true
TRANSITION_DECISION_CANDIDATE_BUDGET_SUFFIX_ALLOWED=false
QUEUE_ADVANCE_CANDIDATE_SUFFIX_IS_POST_DECISION=true
QUEUE_ARTIFACT_CANDIDATE_SUFFIX_ALREADY_SETTLED=true
HISTORICAL_QUEUE_OCCURRENCE_BUDGET_FRONTIER_FROZEN=true
T06_OBSERVATION_ORIGIN_FRONTIER_FROZEN=true
T08_T12_REPLAY_T06_ORIGIN_MATERIAL=true
T07_VALIDATING_SOURCE_ORIGIN_RECONSTRUCTED=true
TERMINAL_CURRENT_LIVE_HEAD_RESEALS_T06_MATERIAL=false
LOCAL_OBSERVATION_BUDGET_FIELDS_USE_ORIGIN_FRONTIER=true
CHILD_PRECHECK_BUDGET_FIELDS_USE_ORIGIN_FRONTIER=true
ROUND_CONTROL_BUDGET_FIELDS_REMAIN_CURRENT_FRONTIER=true
BACKPRESSURE_STATE_CREATION_PRECEDES_T03_CLOSURE=true
PRIOR_BACKPRESSURE_COMPARISON_USES_POST_T03_CLOSURE=true
PRIOR_BACKPRESSURE_PRE_T03_CORE_IS_COMPARISON_BASELINE=false
PRIOR_BACKPRESSURE_STATE_REQUIRES_COMPLETE_T03_CLOSURE=true
EXACT_ONE_T03_SUCCESSOR_PER_DEFERRED_SOURCE=true
SECOND_T03_IN_UNCHANGED_CONTROL_EPOCH_ACCEPTED=false
T03_EXPECTED_OCCURRENCE_SELF_CHANGES_CONTROL_EPOCH=false
RAW_T03_QUEUE_HISTORY_PRESERVED=true
UNCHANGED_HIGHER_ROUND_CREATES_BACKPRESSURE=false
UNCHANGED_HIGHER_ROUND_CREATES_T03=false
CHANGED_CONTROLLING_STATE_PERMITS_BOUNDED_RECONSIDERATION=true
BACKPRESSURE_POST_T03_CLOSURE_FRONTIER_FROZEN=true
SCHEDULER_SPIN_ACCEPTED=false
QUEUE_ANCHOR_MUST_EQUAL_OR_ANCESTOR_LIVE_HEAD=true
QUEUE_ANCHOR_MUST_ALWAYS_EQUAL_LIVE_HEAD=false
HISTORICAL_QUEUE_ANCHOR_IS_STALE_EVENT_PREDECESSOR=false
BUDGET_EVENT_PREDECESSOR_MUST_EQUAL_LIVE_HEAD=true
BUDGET_AXIS_FORK_ACCEPTED=false
HIDDEN_QUEUE_BUDGET_REFRESH_ACCEPTED=false
T03_T04_CREATE_BUDGET_SUCCESSOR=false
T03_T04_COPY_SOURCE_QUEUE_ANCHORS=true
T05_T06_T07_ADVANCE_FROM_LIVE_HEADS=true
T05_T06_T07_TARGET_ANCHORS_ARE_CANDIDATE_SUCCESSORS=true
NON_PARENT_RETURN_T08_T12_COPY_SOURCE_QUEUE_ANCHORS=true
ROOT_LIVE_CELL_AND_GLOBAL_HEAD_ALIAS=true
CHILD_LIVE_CELL_AND_GLOBAL_HEAD_ALIAS=false
MIXED_READY_RUNNING_CONSTRUCTIBLE_UNDER_ACCEPTED_V035=true
MIXED_READY_RUNNING_IMPLEMENTATION_PROVEN=true
MIXED_READY_RUNNING_TEST_PROVEN=true
BACKPRESSURE_BINDS_LIVE_GLOBAL_HEAD=true
ROUND_CONTROL_LATEST_BUDGET_ID_FIELDS_ARE_QUEUE_ANCHORS=true
ROUND_CONTROL_CURRENT_GLOBAL_BUDGET_IS_LIVE_HEAD=true
LOCAL_OBSERVATION_BUDGET_FIELDS_ARE_LIVE_HEADS=true
CHILD_PRECHECK_BUDGET_FIELDS_ARE_LIVE_HEADS=true
D4_TERMINAL_QUEUE_ANCHORS_ARE_FINALIZATION_PREDECESSORS_ONLY_IF_LIVE=true
D3_D4_AVAILABILITY_BOUNDARY_FROZEN=true
NEW_PUBLIC_TYPE_COUNT=0
NEW_PUBLIC_FUNCTION_COUNT=0
NEW_PUBLIC_REASON_COUNT=0
NEW_VALIDATION_TARGET_COUNT=0
NEW_FAILURE_STAGE_COUNT=0
NEW_SCHEMA_DEFINITION_COUNT=0
NEW_ABI_ARTIFACT_TYPE_COUNT=0
NEW_TRANSITION_RULE_COUNT=0
D3_LOCAL_OBSERVATION_MATERIAL_FROZEN=true
D3_CHILD_ACTIVATION_PRECHECK_MATERIAL_FROZEN=true
D3_ROUND_CONTROL_FINGERPRINT_MATERIAL_FROZEN=true
ROUND_CONTROL_AUDIT_ENVELOPE_SEPARATED=true
ROUND_CONTROL_CORE_EXCLUDES_ADMISSION_ROUND=true
ROUND_CONTROL_CORE_EXCLUDES_PRIOR_BACKPRESSURE_IDS=true
HIGHER_ROUND_ALONE_CHANGES_CONTROL_FINGERPRINT=false
QUEUE_AND_TRANSITION_REASON_NAMESPACES_SEPARATED=true
D3_LOCAL_DEGRADED_QUEUE_REASON=g2d_partial_failure_recorded
D3_RETAINED_REPORT_PREFIX_FROZEN=true
TRANSIENT_REPORTS_EXCLUDED_FROM_SETTLED_PREFIX=true
PARENT_SLOT_REVISE_HISTORY_CELL_LOCAL=true
DIRECT_UNTYPED_NEEDS_USER_CARRIER_ACCEPTED=false
NEEDS_USER_FROM_EXACT_DEPENDENCY_ONLY_IN_D3=true
DEPENDENCY_FREE_LOCAL_EVIDENCE_FROM_CELL_INPUT=true
COMPLETE_PREFIX_CLOSURE_FROZEN=true
QUEUE_BUDGET_CONTEXT_CARRIAGE_CONTRACT_FROZEN=true
ACTUAL_PARENT_SLOT_CHAIN_CONTRACT_FROZEN=true
NO_CHILD_DISPOSITION_DERIVATION_CONTRACT_FROZEN=true
CELL_AWARE_QUEUE_HISTORY_CONTRACT_FROZEN=true
READY_BACKPRESSURE_NO_SPIN_CONTRACT_FROZEN=true
ARBITRARY_QUEUE_TRACE_DEDUP_ALLOWED=false
PACKAGE_FACADE_CHANGED=false
RUNTIME_CHANGED=true
TESTS_CHANGED=true
SCHEMA_CHANGED=false
PREFLIGHT_CHANGED=false
TESTS_EXECUTED=true
PYTHON_EXECUTED=true
STAGING_CHANGED=false
COMMIT_CREATED=false
PUSH_PERFORMED=false
PROVIDER_CALLS=0
MODEL_CALLS=0
NETWORK_CALLS=0
CONNECTOR_CALLS=0
EXTERNAL_DRS_CALLS=0
ACTION_COMMIT_PACKETS_CREATED=0
PERMISSIONS_CREATED=0
RECEIPTS_CREATED=0
FINAL_OUTPUTS_CREATED=0
DRS_WRITES_CREATED=0
AUTHORITY_CREATED_COUNT=0
REAL_WORLD_EFFECTS_COUNT=0
PUBLIC_RELEASE_CLAIMED=false
RC2_CLAIMED=false
PRODUCTION_READINESS_CLAIMED=false
G2D_CLOSED=false
G2E_STARTED=false
G2F_STARTED=false
GATE2_CLOSED=false
READY_FOR_OWNER_GUARDIAN_REVIEW=true
READY_FOR_OWNER_COMMIT_REVIEW=true
```
