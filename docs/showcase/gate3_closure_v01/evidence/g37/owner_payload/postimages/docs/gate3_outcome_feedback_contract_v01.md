# G3-1 Outcome Feedback Foundation v0.1

## G3-3 Source-Bound GT-TTL Successor

G3-3 adds the pure `G3_FIXED_POINT_REFERENCE_V01` calibration boundary. It
consumes independently validated `OutcomeFeedbackEnvelopeV01` values and never
discovers history, reads a clock or store, calls a provider, invokes a Root, or
dispatches an effect. Its output is advisory evidence. It is not permission,
accepted durable history, an online correction, or a reason to skip any current
Root, Post V&V, Host or Firewall check.

The public bounded surface is:

* `round_half_even_rational_v01(numerator, denominator)` implements signed exact
  ties-to-even rounding with a positive denominator.
* `bind_outcome_feedback_event_v01(...)` validates the actual feedback against
  an independently supplied source context and binds all eleven subject fields,
  original occurrence, prospective expectation, event time and causal sequence.
* `build_numerical_reference_event_v01(...)` constructs explicitly labelled
  `NUMERICAL_REFERENCE_NOT_RUNTIME` input for mathematical checks only.
* `evaluate_gt_trust_update_v01(...)` validates one predecessor/event pair and
  returns an immutable `GTTrustUpdateV01`; missing or ineligible evidence yields
  an explicit `NO_UPDATE`, not a fabricated zero outcome.
* `bounded_gt_event_fold_v01(...)` canonically orders and audits at most 256
  delivered rows, while deduplicating and folding at most 64 distinct effective
  events for exactly one complete subject key.
* `evaluate_gt_trust_at_v01(...)` and `evaluate_review_pressure_v01(...)`
  evaluate explicit-time decay and its advisory review pressure.
* `validate_calibration_against_sources_v01(...)` independently replays the
  supplied events and compares the complete derived value; a self-consistent
  status, digest or reserialized mutation is insufficient.

`Q=1000000000` and `K_fp=125000000`. For an admitted binary outcome `Y`, the
increment is rounded before addition:

```text
increment = RHE(K_fp * (Y - E) / Q)
R_after = clamp(R_before + increment, 0, Q)
```

`E` is the prospective expectation retained by that event and is never replaced
by a later predecessor. Booleans, floats, unknown profiles, unresolved required
inputs and non-binary outcomes are rejected or retained as explicit no-update
audit evidence. An incorrect result is not automatically an unsafe result.

Half-life is derived from exposed fixed-point trust, independently known regret,
freshness and verified-safety factors. Unknown regret uses the explicit `Q/2`
factor and remains UNKNOWN. The final rounded value is clamped to 3600..604800
seconds. `eta_fp` and `beta_fp` remain reserved G3-4 constants; G3-3 implements no
EMA and no hidden latency, cost, regret or manual-override penalty.

Time evaluation accepts an explicit integer UTC second. It retains distinct
history observation, advice creation and history update times, with
`anchor=min(history_observation_anchor, advice_created_at)`. Future anchors are
invalid. Advice `valid_from` is inclusive and `valid_to` is exclusive under the
existing envelope semantics. TTL and the 604800-second maximum trust age are
independent hard limits. At an exact maximum-age boundary the result is
`EXPIRED_NOT_CONSUMABLE`; a usable value that decays to zero remains distinct.
Exact half-life multiples use rational division, age at least `64*H` shortcuts to
zero, and other values use a local Decimal context at precision 80 with
ROUND_HALF_EVEN. Process-wide Decimal state is never changed.

The reducer keys by all eleven `GTTrustSubjectKey` fields. Original occurrence,
proposal identity and purpose establish the deduplication key. Independently
supplied semantic occurrence values, including event time, must agree;
presentation labels, feedback IDs and causal delivery ordering cannot manufacture
an independent sample. Equal occurrences are idempotent, conflicting occurrences
fail closed, and canonical order is `(event_time, causal_sequence, feedback_id)`.
The chronological delivery audit retains one row per admitted input and may
therefore repeat an event reference. Its accepted occurrence list remains unique,
matches the effective updates and is bounded by 64. Ineligible events cannot
change rating, effective count or the accepted observation anchor. Three distinct
effective events are WARM only as a counting state, not statistical confidence.
The 65th effective event is refused atomically with CAP status and no partial
mutation of the supplied predecessor. Inputs above 256 refuse before folding.

Proof lanes remain separate. The calibration fixture and high-precision oracle
are numerical references, not executions. G3-1 alpha variants remain one original
reference occurrence and cannot manufacture warmth. The G3-2 Sentinel seam is
used once as actual source evidence: a prospectively supplied `Q/2` expectation,
healthy controlled feedback and independent retained-source validation produce
the expected source-bound update; missing expectation produces `NO_UPDATE`.
Neither lane claims environmental or geological truth.

G3-3 adds no writer, persistent accepted snapshot, current DRS descent, correction
epoch, model reputation, alternate Root or hidden deny list. G3-4 must separately
review EMA, durable independent history-source binding, CAS/correction epochs,
actual DRS query/eligibility/current descent, a current-transaction evidence
bridge, and CP-RANK/CP-TIME through public Work/Root boundaries. All five domains,
four semantic families and post-Gate Atlas work remain required.

## G3-2 Native Observation and Genesis Successor

G3-2 extends this one pipeline with `G32_NATIVE_REVIEWED_WORK_V01`.
The exact G31 synthetic corpus and its output identities remain unchanged.
`NativeOutcomeSourceContextV01(canonical: bytes)` is an immutable independently
supplied normalization baseline, NOT proof of native provenance by type or hash.
The pure common evaluator never imports a domain or performs Host callbacks.

The trusted application creates `SentinelOutcomeSourceV01(session)`. Its bounded
`observe_role_v01(semantic, *, expected_fp)` freezes the prospective claim, raw
wall nanoseconds, source/config closure and actual semantic input before calling
the existing plan/execute public boundary. It captures the live retained RESULT
basis only after successful native validation. The new episode accessor
`reviewed_role_result(artifact_id)` returns evidence, never permission. Existing
composition return bytes and checks are unchanged. The source store retains at
most four attempts, no global registrations, executable paths or caller validators.

`validate_capture_v01(capture, *, require_current=True)` verifies actual origin,
ordinal, exact retained bytes, source closure and native Work/Root references.
Current calls use `validate_reviewed_work(session, basis)` on PLAN and RESULT;
source/dependency changes fail. Historical calls compare the retained native
snapshots and validate their real Root objects, with no action replay or current
eligibility claim. This is in-process retained observation verification, not
offline reconstruction of a Host from JSON. Root/time/profile changes never
inherit a stored PASS. Equivalent copies with intact origin remain valid.

`build_feedback_v01(capture, *, require_current=True)` returns the common
observation and feedback. `validate_feedback_v01(value, *, capture,
supplied_source=None, require_current=True)` validates the actual supplied value
against that independent live store, not against a baseline copied from the
report. Supplying a modified source report cannot replace the store. The plain
common native-profile API requires this trusted-input separation; it alone is
not a native authentication entrypoint. Captured source objects cannot select
a validator or turn a self-described CONTEXT_VALIDATED field into provenance.

Native bindings cover Root/task/transaction, role/proposal/occurrence, operation,
object, policy/capability revisions, prospective expectation, actual material and
consumed output hashes, reached boundary and producer closure. Actual Work Root
refs are KNOWN; pure action/Firewall are NOT_APPLICABLE; an early semantic refusal
leaves downstream mechanisms NOT_REACHED and quality NOT_SCORABLE/NO_UPDATE.
Unmeasured costs remain UNKNOWN. Only the target Work count, zero controlled
provider calls, and monotonic target latency are recorded as measured facts.

Raw wall nanoseconds are retained as decimal strings in the source record;
canonical UTC seconds use floor(ns/1000000000). Prospective sequence and raw
nanosecond order permit same-second completion without backdating or sleeps.
Scenario ticks remain separate native source fields. Native ABI TimeEnvelope
bytes, including CT and nullable ET/precision, are preserved, not normalized to
the reference profile's one-hour acceptance window. Historical feedback has no
new current-use eligibility merely because it remains structurally valid.
Ingestion cannot precede the actual capture's UTC second. Independent native
validation also rejects a supplied evidence timestamp later than the real local
validation clock; a coherent recomputation of a future wrapper is not provenance.

`NativeOutcomeWorkProofV01` in the history boundary retains independent actual
generic Work/Root objects plus the verified source baseline. The application
obtains both from the validated native store, never from a supplied JSON report.
`validate_native_work_proof_v01` revalidates the public Work result/artifact and
Root result, exact material/output consumption and source-owner bindings.
`review_outcome_recording_v01(value, *, native_proof)` builds a NEW ordinary Root
review through public generic semantic/Root builders. The sole claim is the exact
sanitized recording candidate/content hash and RECORD_VERIFIED_OUTCOME_GENESIS_ONLY
purpose; deterministic one-candidate advice is not model GT or a learned score.
The checks have actual native validation behind them, not caller-provided booleans.

`OutcomeHistoryGenesisV01(directory)` owns one explicit new external directory.
`query_v01(*, subject, history_key, as_of)` uses SemanticResolveQuery and the
existing public resolver, without a preselected record ID. `record_v01(value, *,
native_proof, review)` revalidates the new Root kernel/input/result, exact selected
claim, local owner, source, purpose and payload before `write_semantic_record`.
An unrelated diagnostic ACCEPT does not qualify. `readback_v01` compares the
provided record and payload against independently retained Root-reviewed bytes.
Only safe typed keys/summary/pointers enter LocalDRS; exact safe feedback/source
payloads remain in its sibling evidence directory. No domain Root helper or
private DRS writer is imported. This is a legacy semantic-record genesis, not
formal MeaningRecord supersession, an epoch or a claimed current descent.
The existing resolver's scalar `subject_key` is a deterministic key identity;
the full eleven-field subject remains in `subject_fields`, used with the complete
history key as exact content filters. This preserves the existing duplicate
signature contract without changing or bypassing the resolver.

Only one original occurrence can be recorded in this bounded writer. Identical
recording is idempotent; another packaging or event is not an additional sample.
The resolver's review_required and zero direct-reuse permission remain intact.
Storage corruption is rejected against the independent expected objects, not a
pin taken from the corrupted report. Offline native replay, general correction,
CAS epochs, WARM status and next-task history consumption remain unimplemented.

| Boundary | G3-2 evidence | Still pending |
|---|---|---|
| Source -> common feedback | Actual controlled REFERENCE_INTEGRITY Work/Root and earlier public refusal | Other four adapters, real environmental truth |
| Observation -> DRS | Root-reviewed genesis/readback/semantic rediscovery | New-task current descent and causal bridge |
| Atlas D1/D2/D3 compatibility | Exact native source/operation/Root and output bindings, coherent poisoning refusals | Actual Atlas incidents, live/adversary and later comparable consumer |

The historical G3-2 statement that G3-3 was not started is superseded only by the
bounded G3-3 section above. All five domains, four families and the post-Gate
Atlas obligations below remain; neither successor specializes the common evaluator.

This is a pure source-bound reference foundation, not Gate-3 closure, a new Root,
current permission, actual history admission or incident detection. Accepted base:
`d199199a578c078c913a2381f595549175bd9235`. Root/ABI/Host/GT/AVF/DRS laws stay unchanged.
Master sections 3-7, 10-11, 13-16 and 21 supply the scoped requirements.

## Public Surface and Immutable Values

The single module `hedgehog.outcome_feedback_v01` owns these exact responsibilities:

* `TaggedValueV01(state, value, reason_code, evidence_refs, unit)` validates a
  frozen scalar and a tuple of references; `to_plain_data()` returns a new map.
* `OutcomeObservationV01(canonical: bytes)` and
  `OutcomeFeedbackEnvelopeV01(canonical: bytes)` own bounded canonical immutable
  JSON bytes. Construction checks structure and identity, not context acceptance.
* `parse_outcome_feedback_json_v01(raw: str | bytes)` checks duplicate keys before
  constructing a map, then exact types, structure and identity. Context remains
  independently required. `validate_outcome_feedback_structure_v01(value)` returns
  an empty reason tuple for structurally valid feedback, otherwise a reason tuple.
* `build_outcome_observation_v01(*, source_bundle: dict, profile: str,
  explicit_times: dict)` and `validate_outcome_observation_v01(observation, *,
  source_bundle: dict, profile: str)` independently check the reference source.
* `build_outcome_feedback_v01(*, observation: OutcomeObservationV01,
  source_bundle: dict, profile: str)` derives, never accepts, assessments.
* `validate_outcome_feedback_against_sources_v01(feedback, *, source_bundle: dict,
  profile: str)` recomputes every derived field against the supplied independently
  pinned reference source. It never substitutes an ideal output for the input.
* `outcome_feedback_to_plain_data_v01(feedback)` returns isolated dict/list values.
* `project_outcome_feedback_evidence_v01(feedback, *, source_bundle: dict,
  profile: str, current_abi_context: dict)` validates the actual input before
  creating an existing SemanticEvidence/EVIDENCE_ONLY carrier. The exact context
  keys are artifact_id, transaction_id, owner_root_id, parent_refs and time_envelope.
  It must match the feedback transaction/Root/time; current history bridging is
  not authorized by this projection.

No classes hold caller-owned dictionaries. There is no global PASS cache and no
public trust flag. A serializer validates its input each time but cannot certify
source truth without the independent source bundle.

## Closed Fields and Trust

The closed schema is `schemas/outcome_feedback_v01.schema.json`. It preserves all
master section 5 fields, including separate timestamp/event/ingest/evaluation,
other_root_evidence_refs, attempted/realized violations, predecessor_feedback_ref,
supersedes_ref and correction_reason. New explicit discriminators are
numeric_profile_id, source_profile_id, evidence_class and avf_history_key.
`profile_id` names the feedback contract, not a domain or scenario.
Schema version is `v0.1`; numeric profile is `G3_FIXED_POINT_REFERENCE_V01`;
source profile is `G31_SYNTHETIC_REFERENCE_V01`; claim profile is
`G31_SCOPE_ADVICE_BINARY_V01`. Unknown contextual profiles are rejected.

Domain is a bounded typed name, not a five-domain enum. Both typed keys preserve
all eleven master components. The AVF component `evidence/validation_profile_id`
is spelled `evidence_validation_profile_id`. No brand dispatch or cross-Root
history transfer exists. Assessment code never branches on domain/scenario IDs.

The source profile admits only the canonical source bundles frozen in the
reference corpus, through source-defined content identities. These identities
are fixture provenance, not a signature or live clock. Each public invocation
checks complete actual source bytes; rehashing a substituted source or an envelope
cannot change the admitted source set. Expected assessment rows are test oracles
only and are not read by production code. Source digest literals are frozen before
outcome tests. New real profiles need explicit reviewed adapters in a later slice.

Every source contains independent context, policy, origin, proposal, pre-outcome
expectation, observation and producer/config closure records. Operation, object,
recipient, version and occurrence relations are checked before assessment.
Summary text is proposal data, never an observation. The reference fixture did
not execute Root, ACP, Firewall, Work or a domain. Accordingly the envelope uses
`HISTORICAL_IMPORT` with `REFERENCE_FIXTURE_NOT_EXECUTED`, never a live/control
runtime claim. All four master lane values remain representable in the schema;
only this source profile's exact lane is contextually admitted in G3-1.

Known tagged values have an exact scalar/unit and resolvable evidence refs.
Unknown, not-applicable and not-reached have null value and a nonempty reason.
Unreached Root/packet/Firewall refs and nonexistent receipts are never fabricated.
Reference-only simulated boundary facts remain separately labelled from real
execution. No new accepted learning event is created by parsing any fixture.
Non-authority keys are exactly claims_permission, claims_root_decision and
requests_effect, all false.

## Derivation

Compare proposed operation/object/recipient with the independent policy, then
compare PROCEED/STOP advice with that relation. Unsupported WRITE advice is UNSAFE;
STOP on an allowed neighboring operation is INCORRECT; correct STOP advice on a
disallowed operation is CORRECT. Independently missing facts, absent expectation
or environmental failure yield NOT_SCORABLE/NO_UPDATE, not a model penalty.
Enforcement and useful task outcome are derived separately from the observed
boundary/result. An observed prohibited effect yields UNEXPECTED_EFFECT/FAILED
and NO_UPDATE; preserving the record is not a successful demonstration.
Known binary quality is 0 or Q only. Regret is UNKNOWN without counterfactual
provenance. Unmeasured costs and latency are UNKNOWN, not zero. Money minor units
and currency remain separate; no aggregate of overlapping phase durations exists.

## Bounds, Time and Identity

Canonical feedback/raw input <=65536 UTF-8 bytes, depth <=12, total nodes <=4096,
text <=256 characters, maps <=96 fields, keys <=64 characters, arrays <=64, references <=32
per field, exact integer magnitude <=2^53-1. Fixed-point scores are 0..10^9;
money/count/latency are nonnegative. Bool is not an integer. Floats/nonfinite,
surrogates, non-NFC strings, duplicate raw JSON keys and extra keys are rejected.
Limits cover the small reference corpus, not arbitrary telemetry or text storage.
JSON Schema expresses mathematical integer types, not the lexical difference
between 1 and 1.0. Raw JSON therefore first uses the public strict parser; Python
schema controls use Draft202012 with its documented integer type checker narrowed
to exact int (excluding bool/float). Cross-field time order, NFC, identity and
reference resolution are DTO/context obligations, not claims of standalone schema
sufficiency. All schema references resolve locally within this bundle.

Times are exact UTC epoch seconds, 0..253402300799, converted with timezone.utc
to ABI aware ISO seconds. Proposal and expectation precede the observed event;
event <= ingested <= evaluated <= timestamp. Source event/KT remain historical.
The projected envelope preserves these fields, with 3600-second reference validity;
evaluation/creation outside that window fail. No wall clock is read.

Use the existing public canonical encoder and domain-separated hash function.
Domains: g3_source_bundle_v01, g3_observation_v01, g3_context_report_v01,
g3_context_v01 and g3_feedback_v01. Self IDs are excluded from their own hash.
Validation report depends on source/observation, never a future feedback ID.
There is no future-consumer reference in feedback identity. Structural cross-task
bridge tests keep the old artifact outside the current same-transaction ABI bundle.

## Frozen Numeric Reference, Deferred Algorithms

Q=1000000000, K=125000000, eta=62500000, beta=250000000. Round ties to even on
the increment BEFORE addition; R/E/Y in [0,Q], P in [-Q,Q]. Half-life base86400,
min3600,max604800; trust age cap604800; extra review below600000000, not at equality.
WARM requires three distinct effective events, cap64. Formula and full oracle
rows/counterexample are transcribed unchanged in `fixtures/gate3_reference_v01.json`.
They are specification inputs, not current calibration results. G3-1 implements
no update, decay, rank, epoch, DRS write, external observer or history consumer.

## Atlas Compatibility and Continuing Obligations

| Reusable boundary | Later variant | Established here | Pending real integration |
|---|---|---|---|
| Independent observation and proposal separation | D1 summary/continuation | Missing result cannot be replaced by a success assertion | Actual continuation producer and public consumer |
| Source operation/object/recipient and policy bindings | D2 discovered credential | Technical-looking proposal data grants nothing | Synthetic resource acquisition measurement and actual current Host refusal |
| Typed task/Root/version relationship | D3 read/write/cross-task | Coherent wrong-context substitution fails even after local rehash | Named forbidden state-change readback plus lawful operation |
| Three independent assessments and tagged unknowns | All Atlas variants | Bad advice/correct stopping/honest uncertainty remain distinct | Real reached boundaries and independent facts |
| Canonical occurrence/lineage, full typed keys | Replay/history | Original occurrence survives presentation label changes | DRS/CAS/dedup/calibration and later comparable Work |

All five Gate3 domains and four families remain obligations. Sentinel is the first
G3-2 adapter; Supplier is the adversary world. No Atlas incident, live provider,
universal detector, new sandbox, second scorer or altered authority law is claimed.
# G34 Bounded Durable History and Current Consumption

This appended successor applies only to `G34_CONTROLLED_BOOLEAN_WORK_PREDICTION_V01`
and `G34_DURABLE_SOURCE_BOUND_HISTORY_V01`. Earlier G31/G32/G33 sections keep their
named historical scope and bytes of reference outputs. It is an external source
proposal, not owner admission, Gate3 closure, or new authority.

The adapter freezes a typed Boolean prediction, expectation, source observations,
dependencies, policy, operation, Root and finite window before executing the
existing role-aware diagnostic Work. Independent current-pair metadata produces
CORRECT; correlated displacement/reserve lineage contradicts a positive prediction
and produces INCORRECT while faithful Work remains ALLOWED_AS_REQUIRED/COMPLETED.
This is neither an unsafe action nor a physical landslide prediction. Eight bounded
controlled executions include a missing-expectation NO_UPDATE control; they are
not live model samples or independent environmental observations.

The public common validator receives an independently supplied source context,
checks the typed prospective claim against completed Work input/output hashes,
references, actual Boolean output and chronology, and never trusts a supplied
assessment. Captures additionally verify retained local origin and contents.
New outcome advice is produced at the actual Work outcome time; the original
prospective claim bytes and its fixed valid-to boundary are never backdated or
extended. The new closed schema is selected only for this exact profile. Old
observation schema and profile laws are unchanged.

AVFHistoryPrior uses the same admitted finite occurrence set as the existing GT
fold: <=256 audited deliveries, <=64 effective occurrences, deterministic event
order, exact duplicate/conflict rules. Q=1000000000, eta=62500000, beta=250000000.
The signed RHE increment is rounded before addition; no floating canonical values.
Signal=2Y-Q; P'=clamp(P+RHE(eta*(Signal-P)/Q),-Q,Q). Delta=RHE(beta*P/Q);
Adjusted=clamp(Base+Delta,0,Q); Root micros=RHE(Adjusted*1000000/Q).
Full history key, source profile and evidence lane must agree. Counts, unresolved
events and known/unknown cost information are not silently converted to samples.

OutcomeHistoryV01 derives snapshots from independent immutable source anchors.
Every exact write proposal has a real ordinary Root review over its predecessor,
epoch, sources and derived fold/prior. A local exclusive writer lock checks the
actual expected head. Immutable records precede atomic head replacement; a failed
installation cleans its unpublished data and retains the prior head. Readback
checks hashes, modes, full ancestry, source rederivation, Root and MeaningRecord.
Each ancestry step strictly decreases epoch. A correction needs distinct admitted
native source provenance, a same-key replacement, explicit supersession reason,
and a new Root-reviewed epoch. Previous sources/decisions/records are immutable.
This finite local filesystem demonstration is not a federated database, an
OS-secured hostile-writer store, or a generic crash-recovery engine.

Current retrieval performs public LocalDRS discovery, temporal/authority
eligibility, ranking, plan, ordinary Root review and bounded descent. The opened
digest resolves independently checked history. A retained read binding and a fresh
head check prevent substituting a rehashed prior at the current consumer. Foreign
context and true expiry can yield explicit cold advice; tampered required bodies
fail. A new current SemanticEvidence bridge references the original historical
CanonicalArtifactRef in its payload. Historical transaction, identity, time and
body are not rebased into the new transaction.

The consumer obtains BaseScore from a real public AVFDecisionReportV02's
score_explanation.final_avf_score using Decimal(str(value))*Q and RHE. HardMask
precedes history, then matching lawful candidates use adjusted score and stable
candidate-ID ties. Root candidate and score micros come from that one projection.
The unchanged closed selected material flows through public pure Work/Host and
post-Work review. Field-level CausalConsumptionRef links the current prior to
actual selected output; history does not authorize work.

CP-RANK freezes lawful diagnostic/observability candidates and .70/.67 AVF inputs:
neutral selects diagnostic; three actual negative predictions yield P=-176025391,
A adjusted655993652, and observability is actually executed. A later positive
prediction recovers P without deleting bad history. CP-TIME uses the same positive
snapshot R665039062/H50330/P176025391: trust is665039062 at age0 and332519531 at H.
It uses a separate prospectively bounded G34 controlled current context, not a
7200-second Sentinel session extended after expiry. Each invocation obtains its
own current pure-only Host/Root setup. Aged advice adds one contract-permitted
evidence obligation, producing actual NEEDS_MORE_EVIDENCE and zero main Work;
an actual observability receipt satisfies it and ordinary reconsideration accepts.
Equality at600000000 does not request review. Valid history and advice decay are
separate from current execution authority.

Focused proofs are in test_outcome_feedback_history_v01 and
test_gate3_current_advisory_v01. Shape-only numerical controls are labelled, not
counted as native episodes. G35, universal replay, Atlas, presentation, provider
calls, effects and owner landing remain outside this slice.

## G34R Reviewed-Boundary Corrections

The preceding G34 prose describes the reviewed predecessor, not accepted proof
of its original time, opening, causal or correction boundaries. G34R supersedes
only those boundaries; the G33 numerical rules and earlier source laws stand.

CurrentReviewContractV01 is a finite application-owned task contract, supplied
independently of a candidate projection. Its full current source/evaluation
context, policy, per-candidate material and definition, full GT subject and AVF
key are revalidated. The Sentinel adapter derives these from the actual operation,
validated task material, current capability profile and semantic source revision.
It does not copy a GT subject from retrieved history. Prior and trust have separate
matching tests. Nonmatching GT advice is COLD_START_NEUTRAL with maximal review
pressure, not transferable reputation. An expired history supplies neither active
prior nor active numerical trust. Equality at 600000000 remains no extra review.

The fixed MAIN contract cannot suppress required evidence by omitting a string.
A contract with no offered check remains NEEDS_MORE_EVIDENCE and explicitly says
the check is unavailable. The EVIDENCE_CHECK role is a distinct bounded task:
its source transaction and actual Host-executed Work task bind the exact check ID,
operation, definition, material, observation refs, target claim, policy, time and
accepted epoch. A changed role flag is not sufficient. The validated original
Work output must equal the contracted result facts. A current evidence bridge
references the independent check's original transaction, artifact and envelope;
no old receipt is rebased or promoted to new authority.

Before Work materialization/execution, the consumer rederives the projection and
ordinary Root review against independently supplied inputs. Root, transaction,
source identity/evaluation triad, current Host context, proposal parents, receipt
bridge and decision reference must match. The actual WorkItem literal is compared
with the selected material and definition. A separate equal material argument
cannot authorize a different literal. Public Work/Host validators remain intact.

History storage separates an immutable canonical snapshot payload (at most
524288 bytes) from its bounded descriptor. Current discovery, head lookup and
eligibility use only the descriptor. The MeaningRecord has one LOCAL_DOCUMENT
pointer, SHA256, exact length, application/json, INTERNAL sensitivity and the
explicit g34:history_context_read:v01 policy. Ordinary Root approves the exact
OPEN_ONE_ARTIFACT plan: depth/records/pointers/artifacts each one, bytes exactly
the payload length, lineage/conflict zero, no memory pointers. Only after approval
are the bytes read and passed to public execute_local_memory_descent_v01. Parsing,
numeric rederivation and ancestry verification follow successful public opening.
Administrative full-history verification is explicit and separate. The retained
open proof binds payload identity, actual descent accounting and current head.

The current advisory evidence is parented by the history bridge. Field paths are
relative to source.payload, without a /payload prefix. The explicit G34R proof
uses the real advisory/proposal/Work-proposal/topology/result artifacts and their
actual component names. Every G34R proof edge is checked by the unchanged public
ABI bundle validator, then its selected values are checked against the independent
current projection. Raw inherited Work source_bindings are retained separately
for diagnostic validation; no inherited invalid reference is silently rewritten.

Corrections require separately supplied trusted history-owner instructions,
binding both exact event/source/occurrence/claim identities, Root, full subject/key,
scope, reason and predecessor. Prepare, commit and administrative reload check
the relation. The controlled demonstration substitutes one predeclared negative
trial with another negative trial without improving the rating. It is explicitly
administrative replacement, not correction of a physical measurement. Positive
recovery appends experience and retains earlier negatives. Neither a candidate
tuple nor its recomputed hash creates correction authority; this is not PKI or
hostile-filesystem protection.

CP-RANK uses the same fixed mandatory/check profile in both branches and executes
real additional evidence before either main Work. CP-TIME uses diagnostic A and
matching A history; only evaluation time changes. The measured normalization
delay d is retained, with trust evaluated at d and d+H, never backdated to force
zero age. Recorded native sources are immutable independent inputs, not fresh
observations or restored Host authority. Actual corrected consumers run fresh.

## G34R2 Native Work Causal Closure

The G34R protected conflict above is superseded only by the explicitly authorized
native causal-label repair. `materialize_work_program_v01` obtains the consumer
component of its three items/budget/bsep_ref bindings from the actual topology.
Topology remains `runtime`; its identity, payload, parents, time, lifecycle and
authority do not change. No other common Work statement changes, and public ABI
equality remains strict. Old materialized programs remain original-source evidence;
new consumers must use newly materialized programs and ordinary Work validation.

The current proof/export boundary now verifies exact public rematerialization,
requires every actual native binding in the submitted combined causal tuple, and
validates that entire tuple together with the G34R field-level edges over complete
artifacts. Missing, altered or legacy native metadata is rejected. Independent
current-advisory numeric rederivation remains mandatory. Distinct uses of a field
are retained with their original reason and effect; no refs are filtered or fixed
in export. The inventory reports current/native/combined counts and any exact
canonical deduplication (none in this producer).

One fresh finite seven-event source stream is justified by the changed common
materializer. Each prospective expectation precedes its unchanged controlled
outcome; both plan and result programs are captured before the next ingest.
The same immutable event set feeds isolated histories and current controls.
Real normalization/write times determine age d and d+H; no backdating or window
extension is permitted. Earlier observations and refusal reports stay historical.

The unaccepted G34 proposal now has 32 cumulative paths: 21 additions and 11
modifications. The two added scope entries are existing Work and its test file.
Its current guard verifies their exact d199 preimages, the one permitted Work
argument change, preservation of old test bodies, and final current pins.
G31/G32/G33R routes, constants and predecessor bytes remain unchanged. This is
not retrospective U4 acceptance, owner admission, a new Gate or Root authority.
# G35 Addendum: Controlled Source Profiles and Supplied Proof

G35 is an additive, bounded five-domain integration. The historical G31 synthetic,
G32 native and G34 predictive contracts are unchanged. The finite G35 profile
registry is in `hedgehog/outcome_feedback_v01.py`; its source envelope is closed
by `schemas/outcome_feedback_g35_sources_v01.schema.json`. All five profiles use
the same existing OFE shape, size and temporal limits. Data codecs reconstruct
only finite named local record types, never a Host, callable or authority origin.
Unknown profiles, fields, record types and invalid public relationships fail.

The source schema describes bounded public serialization shapes, not success
values. Opaque recorded Testflix D source material is an independently pinned
audit attachment, not a newly supported native D replay schema. Public source
validators check the supported Root, corridor, native action, Work result and
consumption relationships. The independent saved baseline binds the exact whole
source, including opaque material. Rehashing a report cannot change that anchor.

Airline runs request-bound controlled semantics, selected-offer/hold and the
three-Root corridor. BankRoot is an ordinary new public review whose returned
decision is consumed at the Bank gate. Existing receipts are explicitly controlled
fixture inputs, not live banking or native Host effects. Supplier's reusable local
session admits resource-specific native capabilities, keeps confirmation separate
from an untrusted document, dispatches Supplier A through Host/Firewall, and holds
Supplier B and shipment. Testflix shares one real quote/D return for immutable
Work evidence, with isolated lawful/revoked/fresh-neighbor Host branches and a
missing-consent Root refusal. Workspace compiles then consumes `/material` from
the actual first result; it starts no preview service. Sentinel performs a fresh
reference-integrity diagnostic and current/stale observation suitability checks.

Quality, enforcement and task outcome are independent axes. A blocked unsafe
document proposal is not an enforcement failure. A lawful observed mock receipt
is not an unexpected effect. Unknown prospective expectation and regret remain
unknown: all new G35 observations are NO_UPDATE and write no history. Brier N=0
means UNKNOWN, with absent numerator/denominator, not perfect calibration. Existing
Sentinel predictive learning and current consumer proofs remain separate streams.

`validate_supplied_report_v01` compares every supplied field and complete ordered
coverage against independently supplied source bytes and baseline. Replay uses
saved measurements and explicit times, preserves identities, and does not allocate
a Host, create a current Root decision, call an executor or read/write current
history. Public validation of saved Root decisions may internally recompute them;
that is not current permission. The supported proof is SAFE_DERIVED; unsupported
full native schema replay is labelled explicitly.

The CLI is `python -B demo/run_gate3_calibration_v01.py`. `inspect` and `collect`
only describe inventory/cost. `run --output <external-directory>` collects bounded
controlled sources. `verify` and `replay` require saved report, sources and a
separately supplied baseline. `live-adversary` is unavailable/PENDING_G36.
No mode implicitly contacts a provider. G35 does not register Living/Conformance,
change Root/Host/Firewall laws, close Gate3 or authorize owner landing.

## G35R Saved-Source Binding and Invocation Scope

The Testflix and Workspace consumers bind the entire native ResultProposal
payload to independently validated Work rows and the actual topology, including
native identities, envelope, ordered program, Roots, capability and input edges.
This is a supported saved relation proof, not Host reconstruction or opaque D
replay. Collectors, schemas and original measured observations remain unchanged.

Each pure build/verify/replay invocation owns its source snapshot, performs one
complete validation per domain and derives occurrences through the same private
primitives used by the independently validating public entrypoints. No validated
token, caller bypass or success cache survives the call. Supplied comparison is
complete; replay returns the checked derivation without a second source pass.

Existing G35 generic policy/window fields describe only the observation wrapper.
They are not native authorization, a reusable prediction key or history admission.
All fourteen observations remain NO_UPDATE and Brier N=0/UNKNOWN. A future scoring
profile must bind real policy, contract, route and time dimensions to its source.

## G3-6 Supplier Learning Mechanism

The G36 external successor adds one finite Supplier action-advice profile,
actual native refusal/receipt sources, numerical Root-recorded local history,
current Root descent and consumed pure review Work. Controlled and configured
Gemini origins are separate; captures are evidence, never restored authority.
The versioned Living/Conformance entrypoints consume the same checked G3 bundle.
An independent top-level successor owns one fresh E5 and one fresh G3 collection;
shared supplied consumers add neither. Historical profile geometry is unchanged.
Direct mechanism proof is not a full top-level release PASS. G3-7 remains pending,
and G3-8 owner landing, full Gate3 closure and production certification are not claimed.
The exact guard route is gate3_g36_adversary_admission_v01, based on d199.
No commit is self-recorded; source admission gives no Root/effect permission.
See the G3 checkpoint for commands, limitations and the frozen-release plan.
# G36R Semantic Proof Repair Addendum

The corrected `G36R_REVIEW_THEN_LEARN_THEN_EXECUTE_V01` collector retains the
frozen G36 requests, numerical fixture and authority laws. ADV-1/2 perform real
canonical/Root review without installation. Accepted proposals have verified
`PREPARED_NOT_DISPATCHED` native facts, PARTIAL task status and NOT_EXERCISED
enforcement. ADV-3 installs the historical packet and reaches actual expiry
refusal. CONTINUE alone installs the objective after successful consumed Work.
One new Host spans the corrected episode and rejects redispatch after CONSUMED.
The original G36 chronology remains incomplete evidence, never rewritten.

# G3-7 Frozen Release Contract Addendum

The exact G37 candidate is the cumulative 59-path successor of accepted main
d199199a578c078c913a2381f595549175bd9235. Its source-admission route is
gate3_g37_frozen_release_admission_v01. The route recognizes only the complete
exact unstaged proposal, the complete exact staged proposal or a clean
sole-parent child whose delta is the same path ledger. Git supplies the child
identity; no future commit hash is embedded in source.

Admission is not authority. It does not grant Root permission, currentness,
effect ownership, a new Living seam, Gate3 closure or production status. Stored
feedback and replay remain advisory evidence. Current action-like work still
requires its ordinary current source validation, independent Root review and
exclusive Firewall path. Unknown source, time, consumer or supplied-report
bindings fail closed.

The two explicit top-level release consumers are collect_living_g36_v01 and
collect_kernel_conformance_g36_v01. Each independent invocation owns one fresh
legacy E5 collection and one fresh G3 mechanism collection. Living may pass its
validated E5 object to shared Conformance, and both wrappers may consume the
same validated G3 bundle. Shared rendering, supplied validation and mutation
controls must not recollect either producer.

After a frozen runtime execution, documentation and admission metadata may
change only with an explicit source-impact bridge. Such edits cannot
retroactively rename old runtime as fresh final-source execution. Runtime
reports remain bound to their loaded source ledger; final guard/binder controls
bind the governance postimages separately.

G3-8 is a future owner operation. It must verify the reviewed archive, exact
postimages and clean owner basis before application; prove exact unstaged and
staged guard states; create a normal sole-parent commit; derive the commit from
Git; run the required postcommit controls; push without force only after
success; and independently fetch/read back the remote commit and tree. G37
prepares and tests that procedure but does not execute it.

Provenance review additionally validates exact request/reply/claim identities,
prospective timing, source/event bindings and the Root-opened history/current
context. New corrected snapshots carry finite `review_source_projections`
derived from independently validated events. The existing Root record and DRS
read bind these exact rows; coherent row substitution fails. Legacy snapshots
omit the optional field and preserve their accepted identities. Cold start
contains no invented history. Output success and exact Work consumption remain
necessary before ordinary fresh Root/Host action preparation.

An independently pinned first outcome binds the immutable original sample.
Captured deliveries retain new native clocks and IDs but not a refreshed
scoring anchor. Exact original request/reply/model/claim/Root/subject identity,
not text equality alone, determines deduplication. Current age and eligibility
remain unchanged. Historical offline comparisons declare their evaluation time.

Supplied proof validates complete CurrentReviewContract bodies and all copies,
pure source reconstruction, Work material/results, ordered registry/Host event
spans and exact ADV-4 attempted inputs/refusals. Replay creates no current Root,
Host, Work, effects or current history. Full native graph replay remains
unsupported. A generated history digest rejected by the unchanged DRS secret
guard uses a reversible letter encoding through the same public pointer builder;
all previously accepted pointer bytes remain unchanged.

These statements describe a bounded candidate repair, not owner admission,
Gate3 closure, uninterrupted fresh-live success or production certification.
