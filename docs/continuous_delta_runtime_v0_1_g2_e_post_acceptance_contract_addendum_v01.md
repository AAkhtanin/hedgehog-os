# G2-E Post-Acceptance Contract Addendum Version 0.1.1

```text
document_status: POST_ACCEPTANCE_CONTRACT_ADDENDUM
document_revision: v0.1.1
guardian_review_status: ACCEPTED
guardian_accepted_pending_draft_sha256: ca6c37ff0f7494fee9dffee633243ea4a721a0417305d80d845d83da00c1f0cf
applies_to_preflight: docs/continuous_delta_runtime_v0_1_g2_e_preflight_v01.md
applies_to_preflight_revision: v0.1.4
applies_to_preflight_sha256: 83f36c9b2d47619a8c8ab997eba6b8ef16f2a3ab07cb3aecfc77ea82469f0d8b
repository_basis: 6112cd6ed1b7645ce997cb5cb45d1c77fde9ad58
stopped_candidate_runtime_sha256: 30e82448dfa90b200ad25c90094a3f8f08075188fc0267d035b9debbcabc74ec
stopped_candidate_transition_sha256: fba16c4a1337860ce4c8f4f60c775a602a9e9925b00b04aaa0dcf7f465745546
stopped_candidate_schema_sha256: 6b7ef792a81ce14ebd0132377ce24b307a5c9d772e33fc159dfd278a6be75aed
stopped_candidate_runtime_tests_sha256: 0d96cd7b42fedc7c567c9f61e221d2ec6fc2a62f0e7f8b58ed71e445b2a36de4
stopped_candidate_transition_tests_sha256: f0e86b4809d06ea277d115d32a0a5ee8f4aadad139edb54ebbf452f9d306ba2b
gate_slice: G2-E
affected_slice: G2-E2
g2e2_implementation_attempted: true
g2e2_implementation_accepted: false
g2e2_repair_authorized: false
g2e2_repair_started: false
g2e3_started: false
gate2_closed: false
```

## 1. Title and Metadata

This document is the G2-E Post-Acceptance Contract Addendum Version 0.1.1.
It records the accepted guardian ruling over the accepted G2-E v0.1.4 preflight
and the stopped, uncommitted G2-E2 candidate identified in the metadata.

This v0.1.1 addendum is now controlling only for PAC-01 through PAC-08. The
accepted preflight v0.1.4 remains controlling everywhere else. This accepted
addendum does not self-authorize repair and authorizes no code, schema, test,
runner, facade, staging, commit, or push action. Only separate owner repair
authorization may resume G2-E2. G2-E3 remains not started and not authorized.

## 2. Status and Supersession Boundary

The accepted preflight remains byte-identical and authoritative everywhere
outside the exact PAC-01 through PAC-08 rulings. Guardian acceptance of this
addendum creates no implementation authority, no repair authority, and no
change to Gate 2.

This accepted addendum supersedes only the exact contradictory or
underspecified statements identified by PAC-01 through PAC-08. Every other
v0.1.4 field, function signature, identity profile, count, invariant, reason,
target, failure stage, Transition row, ABI profile, bound, case, path, and
non-authority law remains controlling under the accepted preflight.

No metadata value, accepted ruling, path ledger, proof obligation, or closing
flag in this draft self-authorizes implementation. G2-E2 remains unaccepted.
G2-E3 remains not started. Gate 2 remains open.

## 3. Stopped Candidate and Observed Failure

The G2-E2 implementation attempt is an uncommitted five-path candidate over
repository basis `6112cd6ed1b7645ce997cb5cb45d1c77fde9ad58`. It passed its
non-importing static validator, exact collection gates, and fourteen-node
focused microproof. It stopped fail-closed during the one-shot six-node
ABI/Transition integration selector with five passes and one failure.

The observed failure is exactly:

```text
payload_reserved_field
```

The first PROPOSED `ContinuousDeltaSource` projector supplied the complete
`WorldStateDeltaV01` plain-data mapping as the generic `KernelArtifactV01`
payload. The generic ABI reserves every top-level Kernel envelope name,
including `transaction_id` and `trace_refs`, and rejects a payload containing
either key. The accepted preflight simultaneously required the public generic
ABI, no private ABI, and a complete source-object payload. That combination is
not constructible without an exact projection ruling.

Read-only static inspection also found these connected contract gaps:

1. Replay-pair coverage is reduced to a set, so multiple projection rows for
   one Replay pair can survive when pointer or edge-class material differs.
2. An extra known-node pair absent from Replay is classified as
   `g2e_dependency_graph_missing_edge` instead of the frozen unknown-source
   reason.
3. Timestamp checks prove lexical/calendar form but do not enforce the local
   half-open delta interval or cross-carrier temporal equality before walking.
4. Changed-binding closure checks exact IDs but not semantic duplicate keys,
   so resealed duplicate or conflicting rows can carry different IDs.
5. A source-text test rejects `_execute` as a substring even though accepted
   reason literals legitimately contain that text.
6. The historical Transition public-function tuple stops before the six
   additive G2-E profile functions.

These findings do not authorize repair. They define the accepted contract
reconciliation and later proof obligations only.

## 4. Preserved Constitutional Laws

This addendum preserves exactly:

- 20 canonical types;
- 18 serialized types;
- 2 runtime-only types;
- 18 schema definitions;
- 88 public reasons;
- 32 validation targets;
- 24 failure stages;
- 4 E2-owned serialized types;
- 16 E2 quartet functions;
- 5 E2 behavioral functions;
- 45 implemented canonical public functions through E2;
- 6 G2-E Transition public functions;
- 10 exact eleven-field Transition rules;
- 7 ABI literals;
- 9 successful-path G2-E artifact instances;
- 4 E2 artifact instances;
- graph bounds of 256 nodes, 1024 edges, and 32 hops;
- artifact-node deterministic FIFO closure;
- pointer and edge-class non-pruning;
- zero-operation and zero-authority geometry;
- ownership by the one public generic Kernel ABI;
- an unchanged package facade until G2-E4; and
- untouched G2-D, Root, G2-E3, runner, Living, and Conformance surfaces.

Structural validity remains distinct from semantic acceptance. No G2-E
artifact, graph, edge, fingerprint, affected set, Transition decision, test,
or document creates truth, permission, Root authority, an ActionCommitPacket,
a receipt, a FinalOutput, a DRS write, an effect handle, or a real-world
effect.

## 5. PAC-01 Generic ABI Reserved-Payload Projection

### Ruling

The generic Kernel ABI remains unchanged and protected. No G2-E private ABI,
alternate artifact envelope, generic reserved-field bypass, or modification of
`_RESERVED_PAYLOAD_FIELDS` is permitted.

A G2-E ABI payload is not the raw complete source-object dictionary when that
dictionary contains a key reserved by `KernelArtifactV01`. It is the exact
profile-specific canonical source projection after relocating only exact
envelope-reserved roles into their already-required ABI envelope or trace
channels.

| G2-E artifact profile | Serialized source | Exact payload fields omitted only from payload |
| --- | --- | --- |
| delta_source_proposed | WorldStateDeltaV01 | transaction_id; trace_refs |
| delta_source_validated | WorldStateDeltaV01 | transaction_id; trace_refs |
| dependency_graph_validated | DependencyGraphIndexV01 | transaction_id; trace_refs |
| affected_set_validated | AffectedSetResultV01 | trace_refs |
| invalidation_report_validated | InvalidationReportV01 | none |
| plan_proposed | SelectiveRecomputationPlanV01 | trace_refs |
| plan_root_accepted | SelectiveRecomputationPlanV01 | trace_refs |
| preservation_proof_validated | PreservationProofV01 | none |
| runtime_report_finalized | ContinuousDeltaRuntimeReportV01 | none |

No other field may be dropped, renamed, nested, summarized, aliased, or
reordered. Projection preserves the serialized source field order after
removing only the fields listed for that exact profile.

### Binding of omitted roles

- `transaction_id` is bound by the exact `KernelArtifactV01.transaction_id`
  envelope field.
- Source `trace_refs` are bound by the exact profile-specific artifact
  `trace_refs` construction and by contextual comparison with the carried
  typed source object.
- The public contextual validator receives the typed source object and
  independently reconstructs the projected payload and complete envelope.
- PROPOSED and VALIDATED `ContinuousDeltaSource` artifacts retain
  byte-identical projected payloads while lifecycle, parent, trace,
  prefix/domain, and artifact IDs remain distinct.
- PROPOSED and ROOT_ACCEPTED `SelectiveRecomputationPlan` artifacts retain
  byte-identical projected payloads under the same law.
- Artifact identity continues to cover every complete non-ID
  `KernelArtifactV01` envelope field.

### Narrow supersession text

Under this accepted addendum, the phrase "complete serialized source object as
payload" in preflight Section 9 is superseded only by:

> complete exact profile-specific canonical source projection, omitting only
> the exact Kernel ABI envelope-reserved fields listed in PAC-01.

All seven ABI literals, nine successful-path G2-E instances, prefixes,
domains, lifecycle states, authorities, parent orders, trace orders,
time-envelope laws, and generic ABI ownership remain unchanged.

## 6. PAC-02 E2 Local Temporal Coherence

E2 owns only deterministic temporal facts constructible from its direct typed
inputs. Before affected-set traversal, E2 must reject:

1. any non-canonical or impossible timestamp;
2. `valid_from_utc >= valid_to_utc`;
3. `delta.observed_at_utc < delta.valid_from_utc`;
4. `delta.observed_at_utc >= delta.valid_to_utc`;
5. any source binding whose `valid_from_utc` or `valid_to_utc` differs from the
   delta;
6. any changed-field or changed-artifact binding whose `observed_at_utc`
   differs from the delta;
7. any plural source pair with incompatible observed or valid times; and
8. any temporal mismatch hidden behind a coherently rebuilt object identity.

The validity interval is exactly half-open:

```text
valid_from_utc <= observed_at_utc < valid_to_utc
```

The interval itself must be nonempty:

```text
valid_from_utc < valid_to_utc
```

The exact E2 reason law is:

| Failure | Exact reason |
| --- | --- |
| malformed or impossible timestamp | g2e_delta_time_invalid |
| empty or inverted interval | g2e_delta_time_invalid |
| observation outside its own carried half-open interval | g2e_delta_time_invalid |
| source or change carrier temporal mismatch | g2e_delta_time_invalid |

Structural validators may reject facts provable inside one object.
Cross-object temporal equality is contextual and must be rerun by both
`compute_affected_set_v01` and
`validate_affected_set_against_graph_v01` before either walk accepts a result.

No clock read, `datetime.now`, filesystem time, mutable current-time global,
or caller-selected PASS status is permitted.

## 7. PAC-03 E2 / E3 Currentness Boundary

The stopped E2 public signatures do not carry the complete G2-C route, G2-D
baseline bundle, G2-B temporal evaluation, or another accepted typed
currentness ceiling. E2 therefore cannot honestly prove external baseline
freshness or that an observation is future relative to a trusted current
evaluation point.

E2 retains responsibility for:

- exact `baseline_report_id` equality across its direct carriers;
- exact graph ID and graph-version equality;
- source-pair, policy, schema, history, hash, and local-time coherence;
- complete carrier closure; and
- affected-set construction only after those local checks pass.

E3 `ContinuousDeltaSourceContextV01` owns:

- direct validation of the accepted baseline report carrier;
- baseline route and topology currentness;
- Manifest, Replay, and source current-use validity beyond E2-local equality;
- trusted evaluation/currentness ceiling derivation from existing typed
  carriers;
- `g2e_delta_baseline_stale`;
- `g2e_delta_future_observation`; and
- `g2e_delta_source_unvalidated` when failure depends on E3-only source
  currentness.

If no exact trusted future-observation comparator is constructible from the
accepted E3 public carriers, E3 must stop before mutation and return to
guardian review. E3 may not use wall-clock time or invent a synthetic
comparator.

Under this accepted addendum, the preflight statement that stale baseline,
future observation, and all source-currentness failures occur before
affected-set creation is superseded only as follows:

- E2-local interval and carrier-coherence failures occur before affected-set
  traversal.
- E3 external/current-use failures occur after SourceContext construction but
  before invalidation, plan construction, Root review, or execution.

The frozen E5 negative cases and public reasons remain. Cases whose truth
depends on E3 currentness are full-public-run or E3 proof obligations, not
direct E2 affected-closure obligations. No E2 public signature changes are
authorized by this addendum.

## 8. PAC-04 Replay Dependency-Pair Cardinality

For each accepted Replay pair:

```text
(dependent_artifact_id, dependency_artifact_id)
```

there is exactly one G2-E edge-projection row. That row carries one exact
ordered tuple of zero or more RFC-6901 pointers and one exact `edge_class`.
Multiple pointers for one dependency relation belong inside that one pointer
tuple. They do not create multiple G2-E edges for the same Replay pair.

The exact fail-closed classification is:

| Condition | Exact reason |
| --- | --- |
| missing accepted Replay pair | g2e_dependency_graph_missing_edge |
| duplicate projection rows for one Replay pair, including different pointer or class material | g2e_dependency_edge_duplicate |
| extra pair absent from Replay | g2e_dependency_edge_unknown_source |
| unknown dependency endpoint | g2e_dependency_edge_unknown_source |
| unknown dependent endpoint | g2e_dependency_edge_unknown_dependent |
| self pair | g2e_dependency_edge_self |

No set-only comparison may erase pair multiplicity. No silent deduplication is
permitted. Exact pair cardinality must be checked before graph-basis or edge
identity acceptance.

Canonical pre-ID sorting, graph-basis construction, source-Replay-edge digest,
edge identity, cycle rejection, bounds, and pointer non-pruning remain
unchanged.

## 9. PAC-05 Semantic Changed-Binding Duplicate Law

Semantic duplicate classification is independent of object identity and
trace-reference variation. It occurs after exact ID-to-object closure and
before fingerprint acceptance and graph traversal.

### ChangedFieldBindingV01

The semantic key is:

```text
(source_binding_id, json_pointer)
```

For two field rows with the same semantic key:

- the same prior and observed value hashes and the same change meaning,
  regardless of a different object ID or trace ref, produce
  `g2e_delta_duplicate_binding`;
- a different prior or observed value hash, observed time, or incompatible
  change meaning produces `g2e_delta_conflicting_duplicate`.

### ChangedArtifactBindingV01

The semantic key is:

```text
(source_binding_id, baseline_artifact_id)
```

For two artifact rows with the same semantic key:

- the same observed successor, payload hashes, dependency fingerprints, and
  change meaning, regardless of a different object ID or trace ref, produce
  `g2e_delta_duplicate_binding`;
- a different observed successor, payload hash, dependency fingerprint,
  observed time, predecessor relation, or incompatible change meaning
  produces `g2e_delta_conflicting_duplicate`.

A delta may carry both one changed-field family and one changed-artifact family
for the same source pair when the field row names a causal detail of the exact
artifact successor. Cross-family coexistence is not itself a duplicate.

No caller mapping, object identity, hidden registry, or trace-ref difference
can turn a semantic duplicate into a distinct accepted change.

## 10. PAC-06 Reason and Failure-Stage Preservation

The 88-reason registry, 32 validation targets, and 24 failure stages remain
unchanged. A later repair must use existing reasons only.

| Repair condition | Existing exact reason |
| --- | --- |
| ABI profile or source-projection mutation | g2e_object_invalid or g2e_identity_mismatch, according to the frozen ABI-profile matrix |
| invalid local time | g2e_delta_time_invalid |
| semantic duplicate | g2e_delta_duplicate_binding |
| semantic conflict | g2e_delta_conflicting_duplicate |
| duplicate Replay pair | g2e_dependency_edge_duplicate |
| extra non-Replay pair | g2e_dependency_edge_unknown_source |

No new public reason, validation target, or failure stage is added by this
addendum.

## 11. PAC-07 Test-Surface Corrections

Two test-only corrections are frozen for a separately authorized later repair.

1. A source-text assertion may not reject the substring `_execute`, because
   accepted reason literals include text such as
   `g2e_transition_selective_recomputation_executed`. The replacement must use
   AST call-target inspection and reject only actual forbidden function calls
   or definitions, including:

   - `execute_selective_recomputation_v01`;
   - `run_continuous_delta_runtime_v01`;
   - `_d4_run_runtime_v02`; and
   - any demo or runner execution seam.

2. Historical Transition public-function surface tests must append exactly:

   - `build_continuous_delta_transition_registry_profile_v01`;
   - `validate_continuous_delta_transition_registry_profile_v01`;
   - `continuous_delta_transition_registry_profile_to_plain_dict_v01`;
   - `validate_continuous_delta_transition_decision_v01`;
   - `continuous_delta_transition_decision_to_plain_dict_v01`; and
   - `rebuild_continuous_delta_transition_decision_identity_v01`.

Every historical, G2-C, and G2-D function prefix remains byte-for-byte and
order-for-order preserved. Neither correction changes production semantics.

## 12. PAC-08 Later Repair Proof Obligations

This addendum does not authorize repair. A separate owner repair prompt must
add durable tests proving at least:

1. all four E2 ABI instances pass generic ABI validation;
2. exact projected payload key order for all four E2 instances;
3. proposed and validated source projected payload bytes are identical;
4. reserved source fields remain separately bound in envelope and trace
   channels;
5. mutation of any omitted source role is detected contextually;
6. graph and affected payloads also contain no reserved top-level key;
7. a duplicate Replay pair with a different pointer tuple is rejected;
8. a duplicate Replay pair with a different edge class is rejected;
9. an extra known-node pair absent from Replay returns
   `g2e_dependency_edge_unknown_source`;
10. an inverted or empty validity interval is rejected;
11. a delta observation outside its own half-open validity interval is
    rejected;
12. a source-binding validity mismatch is rejected;
13. a changed-field observed-time mismatch is rejected;
14. a changed-artifact observed-time mismatch is rejected;
15. the same semantic field change with a different ID or trace is rejected as
    duplicate;
16. a conflicting semantic field change is rejected as conflict;
17. the same semantic artifact change with a different ID or trace is rejected
    as duplicate;
18. a conflicting semantic artifact change is rejected as conflict;
19. an AST no-E3 and no-execution boundary check passes; and
20. the exact additive Transition public surface is preserved.

A separately authorized later repair must rerun:

- a non-importing static validator;
- exact collection counts;
- a focused repair microproof;
- the six-node ABI/Transition integration selector; and
- the complete two-file G2-E1 plus G2-E2 acceptance.

No G2-E3 implementation, runner, Living, Conformance, provider, model,
network, connector, DRS, permission, packet, receipt, FinalOutput, authority,
or effect operation belongs in that repair.

## 13. Identity-Impact Register

| Identity surface | Impact of a separately authorized repair under this accepted addendum |
| --- | --- |
| Serialized G2-E object identities | Unchanged by PAC-01. Source dataclasses and their canonical serialized identities retain every field. |
| G2-E ABI artifact identities | Changed by PAC-01 because projected payload bytes change. Every identity still covers the complete non-ID Kernel artifact envelope. |
| t01 and t02 TransitionDecision identities | Unchanged when rule and guard material is unchanged. |
| Graph, edge, fingerprint, and affected semantic identities | Unchanged unless a later repair correctly rejects a formerly accepted invalid candidate. |
| Test file identities | Changed by a later repair. |
| Generic ABI identity and bytes | Unchanged and protected. |
| Accepted preflight bytes | Unchanged and protected. |

This register predicts identity consequences only. It grants no permission to
change any identity or file.

## 14. Exact Repair Path Ledger

This is a non-authorizing forecast for a separately reviewed and separately
authorized repair. It is not an implementation scope.

### EXPECTED LATER CREATE

- `docs/continuous_delta_runtime_v0_1_g2_e_post_acceptance_contract_addendum_v01.md`
  only if it is not already committed in the contract hop.

### EXPECTED LATER MODIFY

- `hedgehog/kernel/continuous_delta_runtime_v01.py`;
- `tests/test_continuous_delta_runtime_g2_e_v01.py`;
- `tests/test_transition_registry_v01.py`.

### CONDITIONALLY MODIFY ONLY IF STATIC PARITY REQUIRES

- `schemas/continuous_delta_runtime_v01.schema.json`;
- `hedgehog/kernel/transition_registry_v01.py`.

### PROTECTED

- `hedgehog/kernel/abi_v01.py`;
- `schemas/kernel_artifact_v01.schema.json`;
- `tests/test_kernel_abi_v01.py`;
- `hedgehog/kernel/__init__.py`;
- all G2-D, Root, G2-E3/G2-E4, runner, Living, Conformance, release, audit,
  checkpoint, and status paths.

The path ledger does not authorize any create or modify operation.

## 15. Non-Claims and Forbidden Work

This accepted addendum does not claim or authorize:

- acceptance or completion of G2-E2;
- implementation repair or test repair;
- construction or validation of `ContinuousDeltaSourceContextV01`;
- invalidation, preservation, plan construction, selective recomputation, or
  either Root review;
- G2-D execution or modification;
- package-facade modification;
- a demo, runner, Living, Conformance, audit, checkpoint, status, release, or
  G2-F operation;
- staging, commit, amend, or push;
- a private ABI, ABI bypass, hidden registry, mutable cache, wall-clock
  currentness comparator, or synthetic future-observation authority;
- provider, model, network, connector, external DRS, permission, packet,
  receipt, FinalOutput, DRS-write, authority, or real-world-effect creation;
- production readiness, RC2, public release, or production security
  certification.

No code, schema, test, or existing document is changed by this document-only
hop. The stopped five-path candidate remains byte-identical.

## 16. Accepted Closing Flags

```text
G2E2_ADDENDUM_CREATED=true
G2E2_ADDENDUM_REVISION=v0.1.1
G2E2_ADDENDUM_GUARDIAN_STATUS=ACCEPTED
G2E2_ADDENDUM_ACCEPTED=true
G2E2_ABI_CONFLICT_RECONCILED=true
G2E2_LOCAL_TIME_LAW_RECONCILED=true
G2E2_CURRENTNESS_BOUNDARY_RECONCILED=true
G2E2_REPLAY_PAIR_LAW_RECONCILED=true
G2E2_SEMANTIC_DUPLICATE_LAW_RECONCILED=true
G2E2_TEST_SURFACE_LAW_RECONCILED=true
G2E2_PUBLIC_GEOMETRY_CHANGED=false
G2E2_REASON_COUNT=88
G2E2_VALIDATION_TARGET_COUNT=32
G2E2_FAILURE_STAGE_COUNT=24
G2E2_REPAIR_AUTHORIZED=false
G2E2_REPAIR_STARTED=false
G2E3_STARTED=false
GATE2_CLOSED=false
PYTHON_IMPORTED=false
PYTEST_EXECUTED=false
RUNNER_EXECUTED=false
G2D_EXECUTED=false
STAGING_CHANGED=false
COMMIT_CREATED=false
PUSH_PERFORMED=false
READY_FOR_GUARDIAN_ADDENDUM_REVIEW=false
```

These flags describe this guardian-accepted addendum. Guardian acceptance does
not authorize the later repair; repair authority remains external to this
document.
