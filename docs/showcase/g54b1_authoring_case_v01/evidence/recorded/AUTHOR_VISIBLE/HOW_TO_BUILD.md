# HOW to Build a Bounded Domain

## 1. Architecture and Ownership

The public runtime is a chain of proposals, checks, local decisions and separately
owned effects. User/event intake belongs to a local Root. Semantic actors propose;
they do not own topology or finality. Runtime materializes Work. A result proposal,
Post V&V record or GT advisory remains evidence. Root decides locally. A current
Root-created scoped ActionCommitPacket is needed for consequential effects; the
Effect Firewall/bounded Corridor is the exclusive effect owner. Host binds current
source state, capability code and dispatch. External DRS transports evidence, not
Host handles, Root state or permission. There is no SuperRoot.

Use accepted modules; do not copy kernel logic into your domain. The shipped source
is read-only. An adapter may define a new closed body profile, pure domain functions,
typed parameter mapping, a finite MOCK executor and source-bound validators. It
cannot change ABI, Root rules, currentness, effect kinds, admission, crypto laws,
guard/binder policy, existing schema enums or arbitrary executable-plugin rules.
When a required operation lacks an honest public seam, report the exact symbol,
input and refusal. Do not emulate an ACCEPT or invent an undocumented function.

Three distinct decisions are required: independent source review for new code;
native capability admission for a concrete local executor/validators; current local
Root/Host authorization for an action. Neither passing own tests nor a foreign
signature supplies the other decisions. Candidate state is DRAFT, CANDIDATE_READY,
QUARANTINED_FOR_REVIEW, APPROVED_FOR_DECLARED_SANDBOX, then a separately recorded
LOCAL_REFERENCE_ADMITTED or REJECTED. Revocation only applies to a real admission.

## 2. Source Surface and Limits

Use NATIVE_INTERFACE_MAP.md/json for exact positional/keyword signatures, dataclass
fields, file paths, line numbers and source hashes. Required imports are included
in source/. `hedgehog.kernel.work_composition_v01` reads
`schemas/work_composition_v01.schema.json`; this resource is part of the inventory.
The dependency record describes the measured interpreter and installed packages,
not a request to upgrade them. Examples use only existing dependencies and stdlib.

The reference transport is two peer processes over inherited, length-framed pipes.
It is signed, not encrypted, internet-ready or isolated from an OS administrator.
Each peer owns its key capability, state, local policy, Root and Work. The trusted
launcher distributes synthetic inputs and separately pinned PUBLIC keys, not an
offer, answer or cross-Root capability. Different peer roots never share finality.
No arbitrary URL/path from payload is opened. There is no HTTP redirect mechanism.

Bounds: one automatic hop; four pointers; eight records per opened bundle; sixteen
lineage references; pointer16KiB; body64KiB; frame256KiB; JSON depth12. Each declared
task has at most two payload attempts, eight metadata/status observations, two
accepted bodies and128KiB cumulative accepted body bytes. The finite G52 sessions
have at most32 requests, clean boundary EOF and signed CLOSE. A malformed/truncated
frame is not clean EOF. Existing stalled IPC read ceiling is60 seconds, a finite
donor operational bound; changing it requires an explicit versioned profile.

## 3. Build Actual PURE Work

The concrete example is `example/run_numeric.py::calculate`. Its executor computes
3*x+2, while a distinct validator checks typed output and the equation. Input7 and
input11 produce23 and35, respectively. No expected numeric result enters bootstrap.
Boolean input is refused before a Work is constructed. A missing required input
also produces a real Root refusal, not an offset/default answer.

1. Define module-level executor and input/output validators, not anonymous closures
   created from text. An executor receives a BoundCapabilityInvocationV01 and
   returns a tuple of ActionEffectParameterRecordV01 from the public builder.
2. The input/output schema is expressed using exact names and value_type strings
   (INTEGER, TEXT, REFERENCE, BOOLEAN as appropriate). Optionality, consequential
   flags and allowed values are native fields, not free-form hints.
3. `mocks.admit_pure_operation_v01` observes local code and admits the exact PURE
   definition through Host. That donor is finite controlled reference code, not
   permission for downloaded code or an OS sandbox.
4. Make `work.WorkItemV01(work_id, definition_id, owning_root_id,
   inputs, resource_refs, depends_on, guard, review_obligation_id)`.
   Literal bindings come from `donor.work_literal_v01`. Binding an earlier actual
   Work output uses the public WorkOutputBindingV01/WorkInputBindingV01 shapes in the map;
   do not replace it with a caption or hardcoded fixture value.
5. `donor.prepare_work_program_v01` returns `(program, common, host)`. It constructs
   the semantic proposal, candidate, topology and controlled source/Host, then
   `advance_work_program_v01(program, **common, host_map={root_id: host})` invokes
   the actual local executor. Call the supplied program-result validator with the
   same live values; then `work_program_result_to_artifact_v01` produces the artifact.
6. Preserve invocation, admission snapshot, typed inputs/output, artifact, status,
   source references and actual host.work_attempts. A nominal function called
   "Work" or a summary JSON alone is not evidence of native performance.

The donor's Work source clock is controlled logical1014, not current Unix time.
Its preparatory action stages use1010..1014. Do not substitute wall time for one
axis or claim its logical envelope is today's observation. Domain
source envelopes and current external reviews use explicitly recorded UTC. A real
external input's validity is checked separately at the domain boundary. Later live
deployment needs its own supported current source, not an unbounded logical fixture.

`gate5_native_v01.native_work` offers only source/mean/corrected calibration modes.
It is a declared donor, not a function that accepts a new domain mode magically.
Use the lower public Work/capability pattern for new functions, without changing
that donor or forcing data into its calibration fields. All strings that reference
IDs are canonical identifiers, not permission tokens.

## 4. Local Root Review

`gate5_native_v01.root_review(root, transaction, candidate, subject, checks,
claim_value, now, predicate=..., window=None)` is a working controlled adapter.
It constructs public semantic request/evidence/contribution/trust/synthesis/packet
records, then invokes the actual Root kernel and validates its result. Inspect its
source and mapped underlying public builders when adapting to new semantics.

`checks` must be actual independently computed boolean predicates. Supplying True
because a foreign record says so is not validation. `claim_value` must carry exact
consumed inputs, Work output/ref and dependent source identity. The source-bound
Root input/result is retained using `root_plain`; JSON copies cannot be revived as
new grants. Local acceptance for reading a foreign body is not effect permission.

For the controlled adapter, `now` is the recorded integer UTC observation and
`window` is a half-open validity interval. The helper compares the actual wall clock
with that interval. All checks plus temporal validity are required for ACCEPT.
Preserve refusals with their real reason and phase; never rename a failed call as
PASS because setup or teardown completed. Source review, publication review,
release/access review, retrieval review, import acceptance and final result review
are distinct subjects. Link their exact IDs rather than duplicating one conclusion.

## 5. Persisted Pointer Lookup and Descent

LocalDRS is storage, not an authority service. `write_semantic_record` stores a
SemanticDRSRecordInput; `resolve_semantic_candidates` accepts SemanticResolveQuery
and returns candidates requiring local review. Reconstruct a new LocalDRS instance
to exercise persisted reads. A process-global Python map is not restart evidence.
The address layer carries only safe metadata: publisher, source/revision, declared
meaning/schema, body hash/length, time/scope and an operator endpoint alias/object.
Do not put source observations, full schedule/body, private notes or complete native
trace in a public summary. Do not put hashes into natural-language summaries merely
to evade a privacy filter; content_fingerprint binds exact metadata separately.

For native descent, build SemanticAddressV01, DRSTimeEnvelopeV01 and authority
envelope through their public builders. Start as CONNECTOR_OBSERVATION, not accepted
memory. A later locally reviewed context can refer to its own Root input/result
while keeping foreign identities in source refs. Existing MemoryPointer storage
classes are LOCAL_*; external metadata is not a new remote enum or a fake local
file pointer. The explicit provider bridge opens the exact permitted remote body.

The working numerical donor `pointer_descent_v01(pointer, folder, source_end)`
shows the complete public query/evaluate/retrieval-plan/Root/descent-request/
execute_local_memory_descent sequence. It is calibrated to its declared Root/domain
labels, not a general new-domain entrypoint. Reuse that sequence in a reviewed thin
domain adapter with its own current identities and exact fields from the interface
map; do not suppress its source checks or rename foreign owning_root_id as local.
Source end bounds the context. A historical query labels original source/time and
may have a new local READ review, but no new remote body fetch or computation.
Completely pure supplied verification makes no new Root decisions either.

## 6. Canonical Wire and Identity Order

`gate5_contracts_v01` supplies decode/canonical/sha/shape, bounded arithmetic,
time validation, public commitment signatures and the closed carrier field sets.
The machine interface index includes FIELDS, IDS, bounds and exact callable shapes.
`decode` rejects duplicate keys, floats, NaN/Inf, noncanonical bytes, excessive
depth/size and unsupported JSON scalars. Integers use an explicit signed bound;
bool is not int. References/labels are bounded ASCII. Do not lossy-normalize an ID
into a path. Use allowlisted logical IDs, not caller paths. IDs hash the canonical
body excluding their own ID field. Lists keep their order; sets must be normalized
deliberately, never sorted because a comparison failed.

Construct dependencies in this order:

1. Actual source inputs -> native Work -> current source review.
2. Closed body with original source record/revision/Work/review/time/lineage fields.
3. Content manifest covering `body.json` length/hash and original source refs.
4. Pointer tying body and manifest; its publication/release records are separate.
5. Domain-separated POINTER/STATUS/RELEASE commitment+signature over exact bytes.
6. Import candidate retaining foreign IDs plus local request, verification facts,
   dependency/policy fingerprint and status observation. Immutable candidate first,
   separate immutable disposition/review later; do not introduce a hash cycle.

Manifest never contains its own hash, pointer or signature. Pointer includes the
prior source review, not a future review that includes the pointer. SignatureValid
proves only the pinned test key and linked bytes, not arithmetic or policy truth.
Keysets are accepted from independent local trust input, never from the same body
advertising itself. `sign`/`verify` call the existing Ed25519 commitment primitives;
no custom cryptography, no private key export or key hash in logs. Production PKI,
enrollment, encryption and administrative isolation are not claimed.

The generic numeric signed-profile subtest is explicitly a component crypto check,
not a peer release or grant. Full peer execution is the separately source-bound
recorded G52 donor, not repeated for prose or recast as fresh new-domain execution.

## 7. Add One Reviewed Body Profile

The G52 default is intentionally closed to BoundedCalibrationSummaryV01. Changing
only a schema_id in JSON cannot turn it into another type. The G53 correction adds
`ReviewedBodyProfileV01` and keyword-only `profile=` on `validate`, `check_pointer`
and `check_bundle`. Old calls without profile remain strict calibration calls;
the frozen calibration profile cannot be replaced through this seam.

After independent source review, trusted LOCAL deployment code may instantiate one
profile with exact schema_id, closed body_fields, closed scope_fields, local policy
acceptance field and three module-level local functions:

- validate_body(body): check all domain types, ranges, equations and closed meaning.
- validate_pointer(pointer): enforce safe metadata-only summary; no full payload.
- validate_binding(body, policy, pointer): check domain semantics against the local
  task, units/recipient policy and coherent source projection as applicable.

These callbacks raise a specific ValueError on failure; they do not return a trusted
boolean from the wire. They are part of the reviewed TCB, not proof that arbitrary
caller code is safe. Profile construction is not source admission. The record is
not serialized and there is no module-name loader or network plugin registry.
Explicit profile selection occurs from separately reviewed local source/policy,
not from a payload-provided import path or self-selected validator. Unknown type
or schema mismatches fail. The example's `numeric_profile.py` is a concrete working
non-target profile with independent arithmetic validation.

Common required body fields remain version, source_record_ref, source_revision,
source_work_ref, source_review_ref, time_envelope, ttl_base and source_lineage_refs.
Generic validation still enforces bounds, exact identity, provenance, signatures,
request/release binding, freshness/status/conflict and local policy. Schema-specific
fields are NOT smuggled into calibration observation/correction fields. Use
`validate(kind, value, profile=PROFILE)` before canonicalizing/signing. The old
`contract(kind,value)`/BoundedContractV01 remains the strict calibration carrier;
it has no implicit profile. Do not use it to silently accept a new schema.

The G52 high-level source/requester lifecycle is a calibration donor. A new domain
owns its body producer and consumer adapter using the same PipeChannel,
PublisherBudget, signature/status/temporal/current-review primitives. It does not
rewrite transport, Root/ABI or invent federation. ImportStore's calibration
convenience `validate_bundle` is not profile-aware; call public check_bundle with
the explicit reviewed profile, then preserve its authenticated state/dedup rules
in the domain adapter. Do not monkeypatch BODY_SCHEMA, functions or global policy.
New schema/adapter changes are part of the exact candidate diff for source review.

## 8. Currentness, Refusals and Accounting

Use the public DRS TimeEnvelope builder and original axes. End is
min(valid_to, pt_created_at+ttl_seconds, source_observed_at+local_max_source_age).
Use is valid only for valid_from<=t<End and source_observed_at<=t. Ingestion or
verification time cannot renew source life. Status independently requires
checked_at<=t<min(valid_until,checked_at+60), matching request/subject/nonce,
pointer/stream/publisher and effective_at<=t. Actual refresh does not rewrite an
old signed timestamp. Store authentic terminal entries before current-use refusal.

Persist highwater by publisher,pointer_id,stream_id. A lower revision is rollback;
same revision/different immutable entry hash is equivocation; same entry with a
new freshness envelope is not conflict. REVOKED/SUPERSEDED do not become ACTIVE
after replay/restart. Distinct pointers' streams are independent. Status unavailable
is CURRENT_STATUS_UNKNOWN, not a permanent peer blacklist. Historical source/result
bytes survive. Changed local policy/dependencies require a new appropriate review.

Use `PublisherBudget(path, contexts)` on the source side independently of B's
`Budget`. Contexts are operator-established before execution, binding requester,
object, purpose, use and source revision. Reserve authenticated attempts before
release review; reserve allowed disclosure bytes before constructing/sending body.
Count denied responses separately from bytes released. Never split an exhausted
task just to reset counters. Helper reconstruction/restart reopens the same state.
The source profile is finite single-writer, not a cross-process database lock.

The receiver checks frame size before reading, then typed body size/integrity and
cumulative accepted-body budget. Wire bytes and semantic body bytes are distinct.
Keep reciprocal bytes and attempted-operation evidence. After refusal, show a
lawful current input succeeds. Dedup key is publisher/source_record/revision/hash;
same identity with different bytes is quarantine, not best-score selection.
No duplicate import earns independent-source or history/reputation credit.

## 9. MOCK Effects and Recovery

The exact G50 donor is `mock_effect.py` plus `check_effect.py`, with a minimal
import-only shim to the reviewed native modules. It changes two disposable local
records, not real money/device state. Functions are observed by
`observe_local_capability_code_v01`; build business semantics, field definitions
and native capability definition, then `admit_local_capability_v01` with the exact
validators/executor. Only MOCK_CONSEQUENTIAL is used. Do not add an effect kind.

Resolve typed inputs first. `build_native_work_action_v01` derives a canonical
packet from admitted business semantics, root/transaction/business object and
input values. Its donor expects device_ref plus declared bindings and controlled
1010..1014 source time. `authorize_and_prepare_action_v01` performs the real Root
review and lifecycle preparation; `host_for_prepared_action_v01` binds the live
trusted source. Dispatch requires current revision and exact evaluation context.
The native firewall checks candidate/packet/owner/inputs/code before the callback.

The MOCK executor binds a logical key from canonical.idempotency_identity, not a
model string, to exact payload hash and packet. It atomically replaces one local
snapshot containing both records and key map, then returns typed output. The
native registry owns the actual EvidenceReceipt and consumed lifecycle. Save them
before optional rendering. Check actual state readback, not just "COMMITTED" text.
The donor tests stale Host revision/time, foreign owner, changed payload and exact
duplicate of the terminal packet. A duplicate dispatch REFUSES; native Host does
not automatically return a second successful receipt. Do not retry CONSUMED.

`reconcile_receipt.py` demonstrates application-level saved MOCK receipt/readback:
same key+same payload+matching stored snapshot returns the old receipt as HISTORY;
changed payload refuses; unknown/missing/mismatched state yields
UNKNOWN_REQUIRES_READBACK and dispatch=False. This does not reconstruct a Host,
grant or prove hostile-storage/power-loss recovery. In uncertain real execution,
stop retry, inspect supported independent state/readback and reconcile under a new
current review if needed. Compensation is NOT_APPLICABLE for the disposable
all-or-none one-file mock, with no cross-owner rollback or real-world transaction
promise. A domain must state its own exact failure policy, not claim universal
atomicity because os.replace appeared in a sample.

## 10. Candidate, Tests and Handoff

Fill every Authoring Passport field in CANDIDATE_OUTPUT.md. Own tests cover a genuine
positive, altered input, refusal and a lawful continuation. Unknown body fields,
bad arithmetic, source/time/scope mismatch and removed producer output must not
fall back to an expected caption. Keep profile validation independent of the
producer's success flag. Include a source impact/dependency list and exact limits.

The package checker checks data/path shape only; it never executes the candidate
or awards acceptance. A complete independent source/import/I/O review precedes
the first candidate execution. The current environment has not been certified as
the required cold-execution boundary. A plain directory, venv, PURE admission or
static code scan is not OS isolation for arbitrary Python. No sandbox experiments
or tool escalation are instructions to the author. Await the separately reviewed
runner. Existing native guards stay active in trusted execution infrastructure.

For future trial: initial response plus at most three specific test-feedback
corrections. Architecture hints are recorded assistance. A kit defect versions the
kit and preserves the failed trial; at most one additional trial without a new
scope decision. Report observable inputs/outputs/tool accesses, not hidden reasoning.
Never include credentials, old chat, examiner tests or target answers in author
context. Runtime semantic-model calls, author-model calls, native Work and transport
counts are separate. Native/result verification is not installation or Gate closure.
