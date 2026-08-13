# G2-E Post-Acceptance Contract Addendum Version 0.1.2

```text
document_status: POST_ACCEPTANCE_CONSTRUCTIBILITY_ADDENDUM
document_revision: v0.1.2
guardian_review_status: ACCEPTED
guardian_accepted_v012_pending_draft_sha256: 83e089679b73dcb5f43384ec788c53d86f59b350229bfb28859c8aa72db083dd
applies_to_preflight: docs/continuous_delta_runtime_v0_1_g2_e_preflight_v01.md
applies_to_preflight_revision: v0.1.4
applies_to_preflight_sha256: 83f36c9b2d47619a8c8ab997eba6b8ef16f2a3ab07cb3aecfc77ea82469f0d8b
accepted_v011_basis_revision: v0.1.1
accepted_v011_basis_sha256: b3a6c9c7b3687f18bd3c6739c096e7486a4f6505dc9dd49ecc5e1ecd8a4a49f1
repository_basis: e7f80f16481e9e1afd85417d49d55d8b9d8e9c78
committed_g2e2_implementation_basis: e7f80f16481e9e1afd85417d49d55d8b9d8e9c78
committed_g2e2_runtime_sha256: 2e67cb686ffa6bb867598c2445700eb9e625635c62a27ba095281b17506b524d
committed_g2e2_schema_sha256: 6b7ef792a81ce14ebd0132377ce24b307a5c9d772e33fc159dfd278a6be75aed
committed_g2e2_tests_sha256: 7075d91fbbe07ea8f6292b710cefaea580c1bb3478f149b145a27cfd929cf5f1
g2e2_current_state: IMPLEMENTED_COMMITTED_ACCEPTED
g2e2_committed_implementation_accepted: true
gate_slice: G2-E
affected_slice: G2-E3
g2e3_implementation_authorized: false
g2e3_started: false
g2e3_implemented: false
g2e4_started: false
gate2_closed: false
accepted_v011_pending_draft_sha256: ca6c37ff0f7494fee9dffee633243ea4a721a0417305d80d845d83da00c1f0cf
accepted_v011_stopped_candidate_runtime_sha256: 30e82448dfa90b200ad25c90094a3f8f08075188fc0267d035b9debbcabc74ec
accepted_v011_stopped_candidate_transition_sha256: fba16c4a1337860ce4c8f4f60c775a602a9e9925b00b04aaa0dcf7f465745546
accepted_v011_stopped_candidate_schema_sha256: 6b7ef792a81ce14ebd0132377ce24b307a5c9d772e33fc159dfd278a6be75aed
accepted_v011_stopped_candidate_runtime_tests_sha256: 0d96cd7b42fedc7c567c9f61e221d2ec6fc2a62f0e7f8b58ed71e445b2a36de4
accepted_v011_stopped_candidate_transition_tests_sha256: f0e86b4809d06ea277d115d32a0a5ee8f4aadad139edb54ebbf452f9d306ba2b
accepted_v011_g2e2_implementation_attempted: true
accepted_v011_g2e2_implementation_accepted: false
accepted_v011_g2e2_repair_authorized: false
accepted_v011_g2e2_repair_started: false
```

## 1. Title and Metadata

This document is the guardian-accepted G2-E Post-Acceptance Contract Addendum
Version 0.1.2. It records a narrow constructibility reconciliation over the
accepted G2-E v0.1.4 preflight and accepted v0.1.1 addendum.

The accepted v0.1.1 addendum, with SHA-256
`b3a6c9c7b3687f18bd3c6739c096e7486a4f6505dc9dd49ecc5e1ecd8a4a49f1`,
is immutable historical evidence and remains controlling for PAC-01 through
PAC-08. This accepted v0.1.2 addendum controls PAC-09 through PAC-12. The
accepted preflight v0.1.4 remains controlling for every unaffected law.

This accepted addendum does not self-authorize implementation and authorizes no code,
schema, test, runner, facade, staging, commit, or push action. G2-E3 remains
`NOT_STARTED`, `NOT_IMPLEMENTED`, and `NOT_AUTHORIZED`. G2-E4 remains
`NOT_STARTED` and `NOT_AUTHORIZED`. Gate 2 remains `NOT_CLOSED`. No code or
test result follows from this draft.

## 2. Status and Supersession Boundary

The accepted preflight remains byte-identical and authoritative everywhere
outside the exact PAC-01 through PAC-08 rulings already accepted in v0.1.1.
Version 0.1.1 remains controlling for PAC-01 through PAC-08. Version 0.1.2 is
accepted and controls PAC-09 through PAC-12.

This accepted addendum supersedes only the exact E3 constructibility topics
defined by PAC-09 through PAC-12: three phantom SourceContext carriers, test-only
baseline G2-D materialization, the trusted currentness comparator, and the E3
test contour. It does not alter any accepted PAC-01 through PAC-08 ruling.
Every other v0.1.4 field, function signature, identity profile, count,
invariant, reason, target, failure stage, Transition row, ABI profile, bound,
case, path, and non-authority law remains controlling.

No metadata value, accepted ruling, path ledger, proof obligation, or closing
flag in this document self-authorizes implementation. Separate owner
implementation authorization remains mandatory. G2-E3 and G2-E4 remain not
started. Gate 2 remains open.

## 3. Stopped Candidate and Observed Failure

The first subsection below is retained historical v0.1.1 evidence describing
the pre-commit stopped G2-E2 candidate. Its present-tense status statements are
historical as of that accepted addendum. They do not override the current
metadata recording committed, accepted G2-E2. The later G2-E3 constructibility
subsection describes the current stopped E3 entry.

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

### Stopped G2-E3 constructibility attempt

After the accepted G2-E2 implementation was committed at repository basis
`e7f80f16481e9e1afd85417d49d55d8b9d8e9c78`, a separately authorized G2-E3
implementation attempt stopped before repository mutation at its mandatory
constructibility gate. Static inspection established exactly:

1. a trusted currentness comparator is publicly constructible from the
   accepted G2-C/G2-D carriers;
2. `ContinuousDeltaSourceContextV01.g2b_writeback_evidence` has no canonical
   non-None public carrier under the current G2-B/G2-C contract;
3. `post_vv_profile` and `gt_profile` have no public profile type, builder, or
   validator; and
4. a complete baseline `FractalRuntimeExecutionBundleV02` cannot be
   materialized for E3 tests under the simultaneous prohibitions on the public
   complete runtime, private G2-D calls, G2-D execution, Post V&V/GT execution,
   test imports, and synthetic complete-bundle fabrication.

The repository remained clean and byte-exact. G2-E3 was not implemented. These
facts motivate PAC-09 through PAC-12 but grant no implementation authority.

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

## 13. PAC-09 Exact Absence-Sentinel Law

### Ruling

The committed `ContinuousDeltaSourceContextV01` dataclass field names, field
order, annotations, and accepted public function signatures remain
conceptually unchanged. In G2-E v0.1, these three SourceContext fields are
retained solely as exact absence sentinels:

```text
g2b_writeback_evidence is None
post_vv_profile is None
gt_profile is None
```

They are not untyped extension points. They are not caller-selected profile
dictionaries, module objects, functions, hidden registries, or synthetic
evidence.

The exact contextual law is:

1. `g2b_writeback_evidence` must be `None`.
2. It must equal `g2c_source_context.g2b_writeback_evidence`, which is also
   exactly `None`.
3. `post_vv_profile` must be `None`.
4. `gt_profile` must be `None`.
5. Any non-None value in any of the three fields fails SourceContext validation
   with exactly `("g2e_delta_source_unvalidated",)`.
6. The exact `None` values are identity-neutral runtime absence facts because
   `ContinuousDeltaSourceContextV01` is runtime-only and has no serialized
   identity.
7. No new schema definition is added for the SourceContext.
8. No new public type, profile, ABI literal, Transition rule, reason,
   validation target, failure stage, or package-facade entry is created.

The absence sentinels do not bypass real validation:

- G2-B resolution and ReuseCertificate currentness remain validated through
  their exact public carriers.
- The complete baseline G2-D bundle remains validated through
  `validate_fractal_runtime_execution_bundle_v02`.
- That bundle owns its actual Post V&V and GT rows.
- A later E4 uses existing public Post V&V and GT functions through G2-D
  granular seams, not a fabricated profile object.

No G2-B writeback occurs in E3. No replacement ReuseCertificate is issued. No
DRS write occurs.

## 14. PAC-10 Accepted Baseline Bundle Versus Test Materialization

PAC-10 freezes a strict distinction between canonical E3 runtime behavior and
later test-only materialization of one immutable accepted baseline.

`FractalRuntimeExecutionBundleV02` is a frozen runtime-only aggregate. It has
no public complete-bundle serialized identity, plain-data serializer, identity
rebuilder, or canonical byte representation. G2-E3 creates no such public
type, identity, serializer, ABI profile, schema definition, or package-facade
entry.

### Canonical E3 runtime law

The canonical G2-E module:

- receives `baseline_g2d_execution_bundle` as an immutable input;
- validates it publicly;
- never calls `run_fractal_runtime_v02`;
- never calls a private G2-D helper;
- never constructs a baseline G2-D bundle;
- never performs G2-D admission, queue advancement, budget events, result
  construction, Post V&V, GT, trace/report, parent return, or Root review; and
- never mutates the baseline bundle.

The accepted preflight phrase "without running G2-D" remains fully controlling
for canonical E3 behavior.

### Later E3 test-support law

A separately authorized later E3 implementation action may materialize the
immutable accepted baseline for tests by calling the existing public
`run_fractal_runtime_v02`. This allowance is test-only and exact. It does not
authorize any canonical-module call.

Each authorized baseline fixture call must satisfy all of the following:

1. The call exists only in
   `tests/test_continuous_delta_runtime_g2_e_v01.py`.
2. The source is built deterministically in memory through public builders and
   validators.
3. No test module is imported.
4. No demo or runner module is imported.
5. No private G2-D function is called.
6. No D5 case matrix is reconstructed.
7. The returned object is a complete `FractalRuntimeExecutionBundleV02`.
8. The returned bundle passes
   `validate_fractal_runtime_execution_bundle_v02`.
9. The fixture uses zero provider, model, network, connector, external-DRS,
   permission, packet, receipt, FinalOutput, DRS-write, authority, and
   real-world-effect counters.
10. The exact same deterministic source bytes produce identical independently
    computed source-observation, ordered public canonical member-observation,
    and identity-bearing member-identity evidence in the other prescribed
    process.
11. The fixture object is reused module-wide inside its own pytest process.
12. No test claims that Python object identity proves preservation.

Independent public baseline runs must each return a complete bundle that
passes `validate_fractal_runtime_execution_bundle_v02`. Determinism is proved
without Python object identity and without claiming undefined complete-bundle
bytes. The focused Tier-2 process and complete acceptance process do not share
a Python object graph. Neither process receives, deserializes, unpickles,
reconstructs, or imports the other process's complete bundle.

Each process independently:

1. builds the exact deterministic source through the same public source law;
2. calls public `run_fractal_runtime_v02` exactly once;
3. obtains a complete frozen bundle;
4. requires public complete-bundle validation `PASS`;
5. computes the exact ordered public canonical member-observation record;
6. computes the exact identity-bearing member-identity tuple; and
7. computes the exact source-observation digest.

Cross-process determinism is proved by equality of the independently computed
observation evidence, not by direct Python-object comparison.

Each process constructs one exact ordered, test-only observation record over
every complete-bundle field. For each field, and for every tuple member in
exact tuple order, the record binds:

```text
field_name
tuple_index_or_none
exact_type_name
public_semantic_identity_or_none
canonical_member_sha256
```

Canonical member observation follows these exact rules:

- Existing serialized G2-D dataclasses use their existing public
  `*_to_plain_data_v02` representation and existing public rebuilt identity;
  `canonical_member_sha256` hashes
  `canonical_json_bytes_v01(plain_data)`.
- `KernelArtifactV01` uses `kernel_artifact_to_plain_dict_v01`, and its member
  hash covers `canonical_json_bytes_v01(plain_dict)`.
- `TransitionDecisionV01`, `CausalConsumptionRefV01`, and G2-C, Root, and
  Integrity serialized carriers use their existing public plain-data and
  validation seams.
- `result_proposals`, `post_vv_reports`, and `gt_advisory_reports` dictionaries
  are hashed from their exact canonical JSON bytes in tuple order.
- Runtime-only `FractalRuntimeSourceContextV02` observes its identity-bearing
  members recursively through the same public canonical seams. No direct
  cross-process Python-object equality is claimed.
- Primitive values observe their exact type and canonical JSON value.

The ordered observation record may be hashed under the exact test-only domain:

```text
HEDGEHOG_G2E3_BASELINE_OBSERVATION_V01
```

The exact source-observation record walks every deterministic public source
input in its public signature order and every tuple member in exact tuple
order, applying the same canonical observation rules. The exact
member-identity tuple contains every
`public_semantic_identity_or_none` position from the complete member record in
that same order.

Each of the three evidence digests is lowercase SHA-256 over
`canonical_json_bytes_v01` of the exact test-only domain, one exact typed role,
and its exact ordered material:

```text
HEDGEHOG_G2E3_BASELINE_OBSERVATION_V01
G2E3_BASELINE_SOURCE_OBSERVATION
G2E3_BASELINE_MEMBER_OBSERVATION
G2E3_BASELINE_MEMBER_IDENTITIES
```

These digests are test evidence only. They are not public G2-D or G2-E
identities, ABI artifacts, schema definitions, production cache keys, hidden
registries, replacements for public bundle validation, or new package-facade
symbols.

The exact cross-process comparison law is:

```text
both complete bundles independently pass public validation
+ identical deterministic source-observation SHA-256
+ identical ordered public canonical member-observation SHA-256
+ identical identity-bearing member-identity-tuple SHA-256
```

This law binds every complete-bundle field and every tuple member in exact
order through the frozen public observation rules.

### Exact test-only parent-runner transport

A temporary bounded parent runner under `/tmp` owns the two pytest child
processes in a later separately authorized implementation action. The parent
runner:

1. clears all three expected-observation environment variables before the
   focused Tier-2 process;
2. runs the focused Tier-2 process;
3. requires exit code zero;
4. captures exactly one well-formed line for each value:

```text
G2E3_BASELINE_SOURCE_OBSERVATION_SHA256=<64 lowercase hex>
G2E3_BASELINE_MEMBER_OBSERVATION_SHA256=<64 lowercase hex>
G2E3_BASELINE_MEMBER_IDENTITIES_SHA256=<64 lowercase hex>
```

5. rejects missing, duplicate, malformed, or extra conflicting lines;
6. passes the three captured values to the complete acceptance child only as:

```text
HEDGEHOG_G2E3_EXPECTED_BASELINE_SOURCE_OBSERVATION_SHA256
HEDGEHOG_G2E3_EXPECTED_BASELINE_MEMBER_OBSERVATION_SHA256
HEDGEHOG_G2E3_EXPECTED_BASELINE_MEMBER_IDENTITIES_SHA256
```

7. runs the complete acceptance process;
8. requires the acceptance process to independently recompute and compare all
   three values;
9. treats any mismatch as fail-closed; and
10. creates no repository output and performs no third baseline call.

The environment values are test-runner transport only. They are not
canonical-module inputs, caller-selected PASS, public identities, ABI
artifacts, schema fields, cache keys, persistent state, DRS evidence,
authority, permission, or an effect.

The focused process may emit the values only after its complete bundle passes
public validation and its exact observation record is complete. The acceptance
process may accept the values only when the exact parent runner supplies them
from the preceding successful focused process in the same owner action. No
arbitrary preexisting environment value is accepted.

No file, pickle, `repr`, memory address, shared Python object, hidden registry,
or mutable cache transports the complete bundle.

A later E3 implementation action may use at most two public baseline calls:

- one call in the focused SourceContext, invalidation, and preservation
  integration process; and
- one call in the sole complete E3 acceptance process.

No baseline call occurs during static validation, collection, or the Tier-1
structural microproof process. The two allowed calls are independent
process-local materializations of the same immutable accepted baseline. They
are not selective recomputation, successor-baseline creation, an E5 two-domain
proof, or G2-E production execution.

Exact limit and observed accounting for a later implementation action is:

```text
G2E3_CANONICAL_MODULE_G2D_CALLS=0
G2E3_TEST_BASELINE_G2D_CALL_LIMIT=2
G2E3_TEST_BASELINE_G2D_CALLS_OBSERVED=<actual integer 0, 1, or 2>
G2E3_TEST_BASELINE_G2D_CALLS_SUCCESS_ACCEPTANCE_REQUIRED=2
G2E3_SELECTIVE_RECOMPUTATION_EXECUTED=false
G2E3_SUCCESSOR_BASELINE_CREATED=false
G2D_CHANGED=false
```

A fail-closed stop before either call reports an observed count of `0`. A
failure after the first proof process but before the second reports `1`.
Successful completion of both prescribed proof processes requires exactly `2`.
No report may hardcode `2` after a stopped action that observed fewer calls.
Canonical-module calls remain exactly zero, selective recomputation remains
false in E3, no successor baseline is created, and G2-D code remains
unchanged.

The exact successful-acceptance terminology is:

```text
G2E3_CANONICAL_MODULE_G2D_CALLS=0
G2E3_TEST_BASELINE_G2D_CALL_LIMIT=2
G2E3_TEST_BASELINE_G2D_CALLS_OBSERVED=2
G2E3_TEST_BASELINE_G2D_CALLS_SUCCESS_ACCEPTANCE_REQUIRED=2
G2E3_SELECTIVE_RECOMPUTATION_EXECUTED=false
G2E3_SUCCESSOR_BASELINE_CREATED=false
G2D_CHANGED=false
```

For any stopped implementation attempt, the same block must carry the actual
observed call count.

A later report must not state `G2D_EXECUTED=false` without qualification when
the two test-only baseline calls occurred. The Post V&V, GT, and parent-return
rows produced inside the public baseline run remain G2-D-owned baseline
evidence. G2-E3 does not create or authorize them.

## 15. PAC-11 Trusted Currentness Comparator

The primary trusted ceiling is:

```text
baseline_g2d_execution_bundle
  .source_context
  .router_input
  .local_routing_snapshot
  .evaluation_time_epoch_seconds
```

Its representation is an exact Python `int` Unix epoch second value. The
required public trust chain is:

```text
validate_fractal_runtime_execution_bundle_v02
-> validate_fractal_runtime_source_context_v02
-> validate_execution_mode_router_input_against_sources_v01
```

The following agreement is mandatory:

- the routing snapshot evaluation time equals
  `g2c_source_context.g2a_evaluation_time`;
- when G2-B is applicable, it also equals
  `g2c_source_context.g2b_use_time`; and
- G2-A invalidation-evidence evaluation time equals the same ceiling.

The observed-time source is:

```text
observed KernelArtifactV01.time_envelope.et_observed_at
```

The exact comparison procedure is:

1. Parse canonical aware ISO timestamps.
2. Normalize to UTC.
3. Convert to exact integer microseconds using integer day, second, and
   microsecond arithmetic.
4. Convert the trusted ceiling to
   `evaluation_time_epoch_seconds * 1_000_000`.
5. Accept only `observed_microseconds <= trusted_ceiling_microseconds`.

A later observation fails with exactly:

```text
("g2e_delta_future_observation",)
```

The comparator may not use a wall clock, `datetime.now`, `time.time`,
filesystem time, float timestamps, tolerance windows, `delta.valid_to_utc` as
synthetic current time, a caller-selected comparator, mutable global, or copied
PASS report.

## 16. PAC-12 E3 Test-Contour Reconciliation

PAC-12 preserves:

- exactly 20 canonical types;
- exactly 18 serialized types;
- exactly 18 schema definitions;
- exactly 88 public reasons;
- exactly 32 validation targets;
- exactly 24 failure stages;
- exactly 10 G2-E Transition rules;
- exactly 17 new E3 public functions;
- a canonical public-function target of 62 after E3;
- a canonical `__all__` target of 82 after E3;
- exactly 18 new E3 test nodes; and
- a complete canonical test target of 50.

Only the later E3 execution contour is reconciled below.

### Tier 1 - no baseline fixture

The Tier-1 process contains only structural and pure deterministic tests that
do not request SourceContext or the G2-D baseline fixture. It covers:

- the exact E3 surface;
- the three quartets;
- identity, plain-data, and schema parity;
- invalidation-record structural mutation;
- invalidation-report structural mutation;
- preservation-proof structural mutation;
- no-cache constants and structural derivation; and
- the no-E4, no-facade, and no-prior-slice-mutation boundary.

The hard ceiling is 60 seconds. No baseline G2-D call is allowed in Tier 1.

### Tier 2 - one public baseline fixture call

The focused integration process may execute one module-scoped public
`run_fractal_runtime_v02` baseline call. It covers:

- complete SourceContext construction and validation;
- Manifest, Replay, and source-pair binding;
- trusted currentness;
- the route and topology boundary;
- actual-binding invalidation;
- the G2-A packet-candidate boundary;
- the G2-B stale-certificate boundary;
- the invalidation ABI artifact and t03;
- the no-recomputation preservation control; and
- mutation matrices requiring exact baseline objects.

The hard ceiling is 900 seconds. Exactly one baseline call is allowed in this
process.

### Sole complete E3 acceptance

The complete 50-node canonical file runs exactly once after edits freeze. The
hard ceiling is 900 seconds, and exactly one baseline call is allowed in this
process.

Acceptance requires exactly 50 collected tests, 50 passes, zero failures, zero
errors, zero skips, zero xfails, and no ceiling event. No full repository
pytest, Living, Conformance, D5, provider, network, or effect process is
authorized.

## 17. Identity-Impact Register

| Identity surface | Impact under accepted v0.1.1 or proposed v0.1.2 rulings |
| --- | --- |
| Serialized G2-E object identities | Unchanged by PAC-01. Source dataclasses and their canonical serialized identities retain every field. |
| G2-E ABI artifact identities | Changed by PAC-01 because projected payload bytes change. Every identity still covers the complete non-ID Kernel artifact envelope. |
| t01 and t02 TransitionDecision identities | Unchanged when rule and guard material is unchanged. |
| Graph, edge, fingerprint, and affected semantic identities | Unchanged unless a later repair correctly rejects a formerly accepted invalid candidate. |
| Test file identities | Changed by a later repair. |
| Generic ABI identity and bytes | Unchanged and protected. |
| Accepted preflight bytes | Unchanged and protected. |
| `ContinuousDeltaSourceContextV01` serialized identity | No impact. The SourceContext is runtime-only and has no serialized identity; exact `None` sentinels are identity-neutral. |
| Complete G2-D bundle representation | No public full-bundle serialized identity or canonical byte representation is introduced. No direct cross-process Python-object equality is claimed, and object identity is never proof. |
| Cross-process baseline evidence | The exact three-digest observation tuple compares independently validated process-local bundles without transporting either bundle. Parent-runner transport changes no G2-D or G2-E public identity. |
| G2-D object and artifact identities | No impact. PAC-10 changes no G2-D code or identity law. The test-only observation digests change no G2-D or G2-E public identity. |
| Accepted v0.1.1 addendum bytes | Unchanged as historical evidence and recorded by exact SHA-256 in v0.1.2 metadata. |
| Later G2-E3 runtime, schema, and test identities | Change only after separate owner implementation authorization. |

This register predicts identity consequences only. It grants no permission to
change any identity or file.

The following remain unchanged:

- all 20 dataclass names and field orders;
- all existing E1/E2 public function signatures;
- the exact E3 signatures accepted by the preflight;
- all 18 serialized identity prefixes and domains;
- all 7 ABI literals and all 9 G2-E artifact-instance profiles;
- all 10 Transition rules;
- all reason, validation-target, failure-stage, and schema-definition counts;
- all G2-A, G2-B, G2-C, G2-D, Root, Post V&V, and GT bytes;
- package-facade bytes;
- accepted preflight bytes; and
- accepted v0.1.1 addendum bytes as exact historical evidence.

Only after separate owner implementation authorization may the canonical G2-E
runtime, schema, and test bytes change.
Such a later action may change E3 SourceContext contextual-validation semantics
and E3 test execution accounting and ceilings. The exact `None` sentinel law
changes no serialized identity because SourceContext is runtime-only. The
test-only baseline allowance changes no G2-D identity or code. It proves
cross-process determinism through the exact three-digest observation tuple
computed independently from validated process-local bundles. No direct
cross-process Python-object equality is claimed, and object identity is never
proof.

## 18. Later Implementation Path Ledger

### Accepted v0.1.1 historical G2-E2 forecast

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

### v0.1.2 non-authorizing G2-E3 forecast

A later separately guardian-accepted and owner-authorized G2-E3 implementation
may modify exactly:

- `hedgehog/kernel/continuous_delta_runtime_v01.py`;
- `schemas/continuous_delta_runtime_v01.schema.json`; and
- `tests/test_continuous_delta_runtime_g2_e_v01.py`.

Every other repository path remains protected. No new public profile type is
proposed. No G2-B, G2-C, G2-D, Post V&V, or GT repair is proposed. No new
baseline-fixture constructor is proposed in G2-D. No package-facade
modification belongs to E3.

This forecast does not authorize any later path.

## 19. Non-Claims and Forbidden Work

This accepted addendum does not claim or authorize:

- G2-E3 implementation or test execution;
- construction or validation of `ContinuousDeltaSourceContextV01`;
- invalidation, preservation, plan construction, selective recomputation, or
  either Root review;
- a G2-D baseline materialization during this document-only hop;
- G2-D modification or private G2-D use;
- package-facade modification;
- a demo, runner, Living, Conformance, audit, checkpoint, status, release, or
  G2-F operation;
- staging, commit, amend, or push;
- a private ABI, ABI bypass, hidden registry, mutable cache, wall-clock
  currentness comparator, or synthetic future-observation authority;
- a public complete-bundle serializer or identity, a canonical complete-bundle
  byte representation, or production use of the test-only observation digest;
- direct transport of the complete bundle between the two pytest processes;
- pickle, `repr`, shared-object, memory-address, or hidden-registry transport;
- treating the three environment values as production inputs, authority,
  permission, persistent state, DRS evidence, or effects;
- provider, model, network, connector, external DRS, permission, packet,
  receipt, FinalOutput, DRS-write, authority, or real-world-effect creation;
- production readiness, RC2, public release, or production security
  certification.

Only this addendum document changes in this document-only hop. No code, schema,
test, accepted preflight, G2-A/B/C/D, Root, Integrity Replay, Post V&V, GT,
Transition, ABI, package-facade, demo, runner, Living, Conformance, release,
audit, checkpoint, status, governance, or G2-F path changes.

## 20. v0.1.1 Accepted Historical Closing Flags

The following block is retained byte-for-byte as accepted v0.1.1 historical
evidence. It does not describe the review status of this v0.1.2 draft.

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

These historical flags describe the guardian-accepted v0.1.1 addendum.
Guardian acceptance of v0.1.1 did not authorize later repair; repair authority
remained external to that document.

## 21. v0.1.2 Accepted Closing Flags

These flags describe this accepted addendum only and grant no implementation
authority.

```text
G2E3_V012_ADDENDUM_DRAFTED=true
G2E3_V012_ADDENDUM_REVISION=v0.1.2
G2E3_V012_GUARDIAN_STATUS=ACCEPTED
G2E3_V012_ADDENDUM_ACCEPTED=true
G2E3_V011_CONTROLS_PAC01_THROUGH_PAC08=true
G2E3_V012_CONTROLS_PAC09_THROUGH_PAC12=true

G2E3_PHANTOM_CARRIER_CONFLICT_RECONCILED=true
G2E3_G2B_WRITEBACK_SENTINEL=None
G2E3_POST_VV_PROFILE_SENTINEL=None
G2E3_GT_PROFILE_SENTINEL=None
G2E3_TRUSTED_CURRENTNESS_COMPARATOR_FROZEN=true
G2E3_TEST_BASELINE_MATERIALIZATION_RECONCILED=true
G2E3_V012_METADATA_NAMESPACE_RECONCILED=true
G2E3_BASELINE_OBSERVATION_LAW_RECONCILED=true
G2E3_BASELINE_COMPLETE_BUNDLE_BYTES_CLAIMED=false
G2E3_TEST_BASELINE_CALL_ACCOUNTING_RECONCILED=true
G2E3_CROSS_PROCESS_BASELINE_OBSERVATION_RECONCILED=true
G2E3_DIRECT_CROSS_PROCESS_BUNDLE_EQUALITY_REQUIRED=false
G2E3_TEST_ONLY_OBSERVATION_TRANSPORT=IN_MEMORY_PARENT_RUNNER

G2E3_PUBLIC_TYPE_COUNT=20
G2E3_SERIALIZED_TYPE_COUNT=18
G2E_REASON_COUNT=88
G2E_VALIDATION_TARGET_COUNT=32
G2E_FAILURE_STAGE_COUNT=24
G2E_SCHEMA_DEFINITION_COUNT=18
G2E3_LATER_NEW_PUBLIC_FUNCTION_COUNT=17
G2E3_LATER_CANONICAL_PUBLIC_FUNCTION_COUNT=62
G2E3_LATER_CANONICAL_ALL_COUNT=82
G2E3_LATER_NEW_TEST_COUNT=18
G2E3_LATER_CANONICAL_TEST_COUNT=50

G2E3_IMPLEMENTATION_AUTHORIZED=false
G2E3_IMPLEMENTATION_STARTED=false
G2E3_IMPLEMENTATION_COMPLETED=false
G2E4_STARTED=false
GATE2_CLOSED=false

PYTHON_REPOSITORY_IMPORTED=false
PYTEST_EXECUTED=false
RUNNER_EXECUTED=false
G2D_EXECUTED=false
ROOT_REVIEW_EXECUTED=false
REPOSITORY_CODE_CHANGED=false
STAGING_CHANGED=false
COMMIT_CREATED=false
PUSH_PERFORMED=false

READY_FOR_GUARDIAN_V012_REVIEW=false
```
