# Long-lived DRS State / TTL / Aging Stress v0.1 Preflight

## 1. Status

long_lived_drs_ttl_aging_stress_preflight_v01_status: COMPLETE
preflight_only: true
patch_applied: false
runtime_modified: false
schemas_modified: false
tests_modified: false
docs_modified_except_preflight: false
proof_runner_created: false
external_drs_implemented: false
production_drs_implemented: false
marennya_activated: false
up_activated: false
negative_trace_layer_created: false
production_ready_claimed: false
public_auditor_ready_claimed: false

## 2. Context and Previous Checkpoint

Guardian Passport accepted artifact_type Mapping / Runtime Artifact Vocabulary
v0.1 Option A as current-stage complete and instructed vocabulary work to pause.
The current next major layer is Long-lived DRS State / TTL / Aging Stress v0.1.
This preflight is read-only and performs no implementation.

Controlling basis:

- specs/math_appendix_v0_3.md
- specs/human_passport_v0_25.md
- specs/invariants.md
- Guardian TIME / DRS AGING MATH INVARIANTS PACK

Read-only scans used:

- TimeEnvelope / TemporalQuery / TTL / freshness scan across hedgehog, demo,
  tests, schemas, specs, docs, README.md, and AGENTS.md.
- DRS / LocalDRS / reuse / direct reuse / ReuseScore / Root shortcut scan.
- GT-TTL / half_life / decay / Elo / regret / survival scan.
- Quarantine / DeadEnd / ConflictCheck / lineage / source_refs scan.
- Audit replay / hash-chain / continuity / historical_as_of scan.

Files inspected include active schemas, hedgehog/time_model.py,
hedgehog/drs.py, hedgehog/reuse_gate.py, hedgehog/root_orchestrator.py,
hedgehog/mode_router.py, hedgehog/gt_validator.py, DRS lifecycle, graph
proximity, reuse score, semantic reuse, ConflictCheck, audit hash-chain, and
the current DRS/reuse/time/GT/Root tests.

## 3. Golden Math Basis

The controlling TimeEnvelope basis is preserved exactly:

```text
TE = (PT, KT, ET, CT, TTL)
```

Where:

```text
PT  = Physical Time / system creation time
KT  = Knowledge Time / as-of time
ET  = Event Time / observed event time
CT  = Context Time / session/context anchor
TTL = lifetime window / freshness lifetime
```

Required future extension target:

```text
TE_ext = (
  PT,
  KT,
  ET,
  CT,
  TTL,
  valid_from,
  valid_to,
  source_observed_at,
  source_reported_at,
  system_ingested_at,
  system_verified_at,
  freshness_class
)
```

Required interpretation:

- TTL expiry != claim invalidity.
- Claim validity interval != record freshness.
- Fresh verification != long document validity.
- Stale verification may require rerun even if document remains valid.
- Unexpired document may still require fresh verification.

Current finding: active TimeEnvelope already contains PT, KT, ET, CT, TTL,
valid_from, valid_to, and freshness_class. It does not contain
source_observed_at, source_reported_at, system_ingested_at, or
system_verified_at.

## 4. TemporalQuery Requirements

Current math basis:

```text
TQ = (as_of, range, freshness_bias, max_age)
```

Required future extension:

```text
TQ_ext = (
  as_of,
  query_mode,
  time_range,
  freshness_bias,
  max_age,
  required_time_axes,
  risk_class,
  domain,
  reuse_intent
)
```

Required query modes:

- current_decision
- historical_as_of
- audit_replay
- trend_analysis
- memory_context_only
- direct_reuse_candidate
- warning_lookup

Invariant:

```text
Validity(r, TQ) is query-mode dependent.
Do not implement retrieval as simply record valid/invalid.
Implement as valid for query mode and decision class.
```

Current finding: active TemporalQuery has as_of, time_range, freshness_bias,
max_age_seconds, and freshness_required. It has no query_mode,
required_time_axes, risk_class, domain, or reuse_intent.

## 5. Existing Implementation Inventory

### A. TimeEnvelope Structures

| file | fields found | PT/KT/ET/CT/TTL coverage | valid_from/valid_to coverage | source_observed_at/source_reported_at coverage | system_ingested_at/system_verified_at coverage | freshness_class coverage | gap |
| --- | --- | --- | --- | --- | --- | --- | --- |
| schemas/time_envelope.schema.json | pt_created_at, kt_asof, et_observed_at, ct_session_anchor, ttl_seconds, freshness_class, valid_from, valid_to | yes | yes | no | no | yes | missing source/system axes and clock pathology semantics |
| hedgehog/time_model.py | make_time_envelope returns active schema fields | yes | yes | no | no | yes | helper creates one clock instant for PT/KT/valid_from; no event/source/system split |
| schemas/drs_record.schema.json | time_envelope ref required | yes via ref | yes via ref | no | no | yes via ref | DRS record shape depends on TimeEnvelope but adds no aging semantics |
| schemas/result_proposal.schema.json | time_envelope ref required | yes via ref | yes via ref | no | no | yes via ref | proposal boundary validates shape, not long-lived freshness |
| schemas/final_output.schema.json | time_envelope ref required | yes via ref | yes via ref | no | no | yes via ref | Root final output records time shape, not reuse aging |
| demo/run_drs_lifecycle_semantics.py | proof-local observed_at, valid_from, valid_to, time_basis | partial | yes | observed_at only, not active TE_ext names | no | ttl_state separate | proof-only shape differs from active schema |
| tests/test_time_model.py | checks helper field set and timestamp tzinfo | yes | yes | no | no | yes | no negative/pathology tests |

### B. TemporalQuery Structures

| file | fields found | as_of coverage | freshness_bias coverage | max_age coverage | query_mode coverage | required_time_axes coverage | risk_class/domain/reuse_intent coverage | gap |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| schemas/temporal_query.schema.json | as_of, time_range, freshness_bias, max_age_seconds, freshness_required | yes | yes | yes | no | no | no | no query-mode dependent validity |
| hedgehog/time_model.py | make_temporal_query | yes | yes | yes | no | no | no | helper emits prefer_recent only by default |
| hedgehog/drs.py | query_records requires temporal_query with as_of | yes, shallow | no validation | no enforcement | no | no | no | returns records with time_envelope without applying freshness/validity |
| schemas/world_state.schema.json | temporal_query ref and time_context | yes via ref | yes via ref | yes via ref | no | no | no | WorldState carries TemporalQuery but does not define aging semantics |
| tests/test_drs_runtime.py | query_records requires temporal query | yes | no | no | no | no | no | covers presence, not query modes |
| tests/test_time_envelope_required.py | empty file | no | no | no | no | no | no | test placeholder has no assertions |
| tests/test_temporal_query_required.py | empty file | no | no | no | no | no | no | test placeholder has no assertions |

### C. DRS Retrieval / Reuse Gates

| file | retrieval requires TemporalQuery? | direct reuse gate exists? | RootShortcutAllowed exists? | freshness gate before ReuseScore? | conflict gate exists? | policy gate exists? | permission gate exists? | gap |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| hedgehog/drs.py | yes, as_of presence only | no | no | no | no | layer only | no | no TTL, validity, query-mode, or clock checks |
| hedgehog/reuse_gate.py | consumes temporal_query | direct_reuse_candidate only | no named RootShortcutAllowed | freshness is score component, not hard gate | content string heuristic | status score | no | hard temporal gates and ConflictOK absent |
| hedgehog/mode_router.py | indirect | yes, if allow_direct_reuse and candidate | partial explicit switch, not named RootShortcutAllowed | no | no | indirect through reuse_gate | no | direct reuse route depends on candidate and flag, not full hard-gate formula |
| hedgehog/root_orchestrator.py | yes, calls LocalDRS.query_records(make_temporal_query()) | yes, Root executes direct reuse path when enabled | partial Root-only shortcut logic | no hard temporal gate | no hard ConflictOK | indirect | action permission only for reflex/action path | direct reuse can skip Architect/Executor after current reuse_gate eligibility but lacks long-lived aging gates |
| tests/test_root_orchestrator_runtime.py | yes via Root path | yes | partial | no | partial via reuse_gate | yes through status | no aging-specific permission proof | proves Root switch and full-pipeline fallback, not TTL expiry |
| demo/run_applied_drs_retrieval_reuse.py | proof query artifacts mark TemporalQuery present | proof-only direct_reuse_allowed=false rows | proof Root review rows | proof-only freshness_status | proof ConflictCheck rows | proof-only | proof-only permission boundary | useful scenario substrate, not active runtime gate |

### D. GT-TTL / Survival

| file | half_life/decay/Elo/regret fields found | survival formula implemented? | popularity/reuse-frequency bias guard found? | hard gates override survival? | gap |
| --- | --- | --- | --- | --- | --- |
| schemas/gt_report.schema.json | candidates include payoff/regret/Elo; top-level half_life_hours and decay_rate | no | no | no | schema has fields, not survival semantics |
| schemas/drs_record.schema.json | gt half_life_hours, decay_rate, regret, elo | no | no | no | DRS stores advisory metadata only |
| hedgehog/gt_validator.py | computes payoff, regret, Elo update, half_life_hours, decay_rate | no | no | no | no SafetyScore, ProvenanceQuality, ConflictPenalty, QuarantineProximity, ReuseBoost |
| hedgehog/reuse_gate.py | computes gt_trust from half_life/decay | no | no | partial via eligibility thresholds | GTTrust is a score input, not complete GT-TTL survival |
| demo/run_drs_lifecycle_semantics.py | ttl_state advisory; trust_state advisory | no | no | direct_reuse_allowed proof fields only | proof-only TTL classification |
| specs/math_appendix_v0_3.md | GT-TTL formulas documented | documented only | Smart TTL references Reuse(r), not capped boost | not fully specified | needs updated math/invariant patch before implementation |

### E. Quarantine / DeadEnd / ConflictCheck

| file | quarantine state found | deadend state found | proximity logic found | lineages/source_refs found | route block logic found | gap |
| --- | --- | --- | --- | --- | --- | --- |
| schemas/drs_record.schema.json | layer enum quarantine | layer enum deadends and type dead_end | no | source_refs and trace_refs | no | schema stores layer/type, not proximity thresholds |
| demo/run_drs_lifecycle_semantics.py | quarantine_state proof object | deadend_state proof object | no numeric proximity | lineage_refs | direct_reuse_allowed proof field | proof-only lifecycle semantics |
| demo/run_drs_graph_proximity.py | quarantine routing role | deadend warning role | graph_proximity ranking | source_refs links | direct_reuse_eligible false for unsafe layers | proximity is ranking/signal proof, not hard direct-reuse gate |
| demo/run_typed_drs_lineage_edges.py | quarantine/deadend taxonomy signals | yes | typed edges | source refs | unsafe direct reuse blocked | proof-only |
| demo/run_applied_drs_retrieval_reuse.py | quarantine_proximity boolean | deadend_proximity boolean | boolean only | source records | block rows and validator | proof-only; no active DRS retrieval integration |
| demo/run_conflictcheck.py | consumes quarantine/deadend lifecycle rows | yes | no query-local proximity formula | lineage/evidence views | recommends block/root review | advisory proof, not runtime invalidation |

### F. Audit Replay / Hash-chain

| file | audit hash continuity found | historical_as_of semantics found | current truth blocked? | gap |
| --- | --- | --- | --- | --- |
| demo/run_audit_hash_chain.py | canonical_json, SHA256, previous hash, tamper checks | no | yes, audit_chain_decides_truth=false | audit replay mode not implemented |
| schemas/temporal_query.schema.json | historical_as_of freshness_bias enum | partial enum only | n/a | no audit_replay query_mode |
| README.md / AGENTS.md / specs/invariants.md | hash-chain proves continuity, not truth | docs only | yes | no historical replay algorithm |
| docs/audit_reports/*.log | historical proof logs with timestamps and hashes | proof records only | yes | not a replay engine |

## 6. Required Hard Temporal Gates

Required future gate order:

```text
TemporalHardGate -> PolicyGate -> ConflictGate -> QuarantineDeadEndGate -> ReuseScore ranking -> Root decision
```

Required formulas:

```text
TemporalHardGate(r,TQ) =
  TimeEnvelopePresent(r)
  and TemporalQueryPresent(TQ)
  and ClockOK(r)
  and ValidityIntervalOK(r,TQ)
  and FreshnessOK(r,TQ)

FreshnessOK(r,TQ) =
  forall axis in required_time_axes(TQ):
    Age_axis(r, as_of(TQ)) <= min(TTL_axis(r), max_age_axis(TQ))
```

Required invariant:

- Age_effective is ranking metadata, not direct reuse permission.
- Hard temporal gates check required axes independently.
- Freshness hard gate beats ReuseScore.
- Freshness hard gate beats ReuseFrequency.
- Freshness hard gate beats SemanticSimilarity.
- Freshness hard gate beats Survival.

Current gap: reuse_gate computes freshness as one score component. It does not
apply TemporalHardGate before scoring or direct reuse selection.

## 7. Direct Reuse Gate Requirements

Required future formula:

```text
DirectReuseAllowed(r,TQ) =
  RootShortcutAllowed(r,TQ)
  and TimeEnvelopePresent(r)
  and TemporalQueryPresent(TQ)
  and TemporalHardGate(r,TQ)
  and PolicyOK(r,TQ)
  and ConflictOK(r,TQ)
  and QuarantineProximityOK(r,TQ)
  and DeadEndProximityOK(r,TQ)
  and GTTrustOK(r,TQ)
  and PermissionOK(r,TQ)
  and ReuseScore(r,TQ) >= tau_reuse
```

If any hard gate fails:

```text
DirectReuseAllowed = false
```

Allowed fallback states:

- partial_reuse_then_validation
- context_only
- warning_only
- historical_replay
- blocked

Required invariant:

- DRS retrieval is not direct reuse.
- Root-approved reuse may reduce reasoning.
- DRS does not become authority.

Current gap: Root direct reuse exists and is Root-controlled, but the runtime
does not yet implement RootShortcutAllowed(r,TQ) as a named decision class with
the hard temporal/conflict/quarantine/deadend/permission formula above.

## 8. Query-local State Requirements

Persistent lifecycle_state values:

- active
- completed
- rejected
- quarantined
- deadend
- archived

Query-local states:

- fresh_candidate
- stale_context_only
- historical_only
- warning_only
- rerun_required
- blocked_by_conflict
- blocked_by_quarantine_proximity
- blocked_by_deadend_proximity
- blocked_by_time_gate

Required invariant:

```text
record.lifecycle_state != query_state
```

Current gap: active schema uses status/layer/type. Proof layers use status,
lifecycle_stage, quarantine_state, and deadend_state. There is no formal
query_state output for retrieval/reuse decisions.

## 9. Temporal Conflict / Supersession Requirements

Required formula:

```text
TemporalConflict(r_i, r_j, TQ) =
  SameSubject(r_i,r_j)
  and IncompatibleClaim(r_i,r_j)
  and ValidityIntervalsOverlap(r_i,r_j,TQ)
  and not SupersessionExplained(r_i,r_j)

Supersedes(r_new, r_old) =
  SameSubject(r_new, r_old)
  and SameClaimDimension(r_new, r_old)
  and KT(r_new) > KT(r_old)
  and ValidityIntervalsCompatibleForSupersession(r_new, r_old)
  and ProvenanceChainValid(r_new)
  and ReplacementReasonPresent(r_new)
  and RootAcceptedForSupersession(r_new)
  and TrustClassAllowedToSupersede(r_new, r_old)

TrustClassAllowedToSupersede(r_new, r_old) =
  authority_class(r_new) >= authority_class(r_old)
  or RootExplicitOverride(r_new, r_old) = true
```

Optional advisory check only:

```text
GTTrust(r_new) >= GTTrust(r_old) - tau_trust_tolerance
```

Required invariant:

- Two records may disagree but both be correct in different time windows.
- Newer wins alone is insufficient.
- GTTrust is not authority.
- Root acceptance beats freshness.
- authority class beats freshness.
- freshness alone never supersedes trusted Work.
- unaccepted ConnectorObservation cannot supersede Work.
- SemanticDraft cannot supersede Work.
- ExternalDRSPointer cannot supersede Work.
- EvidenceCandidate cannot supersede Work.

Allowed outcome for unaccepted fresh observation:

- conflict.
- warning.
- rerun_required.
- quarantine/review.
- but not supersession.

Current gap: ConflictCheck represents stale_vs_fresh and incompatible evidence
proofs, but not overlap-aware temporal conflict or supersession semantics.

## 10. Quarantine / DeadEnd Proximity Requirements

Required formulas:

```text
CandidateSet_pre =
  filter_by_domain
  intersection filter_by_time_window
  intersection filter_by_subject_or_claim_key
  intersection top_k_semantic_candidates

QuarantineProximity(r,TQ) =
  max_{q in RelevantQuarantine(r,TQ)}
    Risk(q) * Sim(r,q) * LineageDecay(distance(r,q))

DeadEndProximity(r,TQ) =
  max_{d in RelevantDeadEnds(r,TQ)}
    Risk(d) * Sim(r,d) * LineageDecay(distance(r,d))

LineageDecay(d) = exp(-lambda_lineage * d)
```

Hard bound:

```text
if distance(r,x) > max_lineage_hops:
  do not full-traverse
  use aggregate_taint_signal instead
```

Allowed acceleration signals:

- quarantine_taint_summary.
- deadend_taint_summary.
- lineage_risk_bucket.
- subject_risk_tags.
- claim_risk_tags.

Required behavior:

- QuarantineProximity > tau_quarantine blocks direct reuse and requires Root review.
- DeadEndProximity > tau_deadend blocks direct reuse and route reuse.
- Quarantine proximity cannot become Work.
- DeadEnd proximity cannot become authority.
- quarantine_taint propagation must be bounded.
- a quarantined record cannot cascade-taint the whole DRS graph.

Current gap: graph proximity and applied DRS retrieval proofs show quarantine
and deadend signals, but active DRS retrieval does not compute these hard gate
proximities. Future implementation must avoid raw unbounded full graph scans in
the hot path.

## 11. GT-TTL / Survival Requirements

Required improved survival:

```text
ReuseBoost(r) =
  min(
    1 + k * ln(1 + reuse_count(r)),
    reuse_boost_max
  )

Survival(r,t) =
  GTTrust(r)
  * Freshness(r,t)
  * UtilityHistory(r)
  * SafetyScore(r)
  * ProvenanceQuality(r)
  * (1 - ConflictPenalty(r))
  * (1 - QuarantineProximity(r))
  * ReuseBoost(r)
```

Hard rules:

- FreshnessHardGate beats Survival.
- ConflictHardGate beats Survival.
- QuarantineHardGate beats Survival.
- DeadEndHardGate beats Survival.
- High Survival never overrides failed hard gate.
- ReuseBoost affects survival/ranking only.
- ReuseBoost does not affect RootShortcutAllowed.
- ReuseBoost does not affect DirectReuseAllowed hard gates.
- ReuseBoost does not create authority.
- ReuseBoost may help record remain visible.
- ReuseBoost may affect retrieval ranking.
- ReuseBoost may delay archive.
- ReuseBoost must not override TemporalHardGate.
- ReuseBoost must not override PolicyGate.
- ReuseBoost must not override ConflictGate.
- ReuseBoost must not override QuarantineDeadEndGate.
- ReuseBoost must not override PermissionGate.
- ReuseBoost must not grant RootShortcutAllowed.
- ReuseBoost cannot override hard gates.

Hard invariant:

```text
If any hard gate fails:
  DirectReuseAllowed = false
  regardless of ReuseBoost
```

Current gap: GT and DRS carry half_life and decay metadata, and ReuseScore has
advisory freshness/gt_trust components. The full Survival formula and capped
ReuseBoost isolation rules are not implemented.

## 12. Clock Pathology Requirements

Required invalid/suspicious cases:

- future_PT
- future_KT
- future_ET_without_explanation
- ET_after_PT_without_explanation
- valid_to_before_valid_from
- negative_TTL
- zero_TTL_without_policy
- timezone_mismatch
- clock_skew
- DST_ambiguous_local_time

Required behavior:

- valid_to_before_valid_from -> reject_or_quarantine
- negative_TTL -> reject
- future_KT -> quarantine_or_review
- clock_skew -> root_review_required
- timezone_mismatch -> normalize_or_quarantine
- Clock pathology cannot create freshness.

Current gap: schema rejects negative ttl_seconds when schema validation is
applied, but LocalDRS does not schema-validate records on write and there is no
ClockOK function for future timestamps, interval inversion, skew, timezone, or
DST ambiguity.

## 13. Audit Replay Requirements

Required:

- AuditReplay(TQ) requires query_mode = historical_as_of.
- audit replay evaluates what the system knew at that historical time, not what
  is known now.
- audit hash proves continuity, not truth.
- audit replay uses historical_as_of semantics.

Current gap: hash-chain proof verifies continuity and tamper detection, and
TemporalQuery has historical_as_of as freshness_bias, but there is no
audit_replay query_mode or replay evaluator.

## 14. AcceptedEvidence Time Boundary

Required:

```text
AcceptedEvidence(t_old) != ActionPermission(t_now)
```

If action requested at t_now:

- permission boundary must be rechecked.
- freshness must be rechecked.
- policy must be rechecked.
- Root must decide.

Invariant:

- AcceptedEvidence is bounded evidence.
- AcceptedEvidence is not action permission.
- AcceptedEvidence does not survive time as execution authority.

Current gap: docs and proof layers repeatedly state AcceptedEvidence is not
truth or action permission, but there is no long-lived DRS aging stress proof
that rechecks old accepted evidence at t_now.

## 15. Minimal Stress Scenario Inventory

| scenario | coverage | evidence | gap |
| --- | --- | --- | --- |
| missing_time_envelope_rejected | already_covered | LocalDRS write test rejects missing time_envelope; ResultProposal runtime schema also checks TimeEnvelope shape | no long-lived aging semantics |
| drs_query_without_temporal_query_rejected | already_covered | LocalDRS.query_records raises when as_of is missing | only as_of presence, not full TemporalQuery schema/mode |
| fresh_record_direct_reuse_candidate_but_root_required | already_covered | Root tests show direct_reuse_candidate still runs full pipeline unless direct reuse is enabled | no hard temporal gate |
| stale_work_record_context_only_not_direct_reuse | partially_covered | applied DRS retrieval proof marks stale high similarity as rerun_required/direct_reuse_allowed=false | proof-only, not runtime DRS |
| expired_time_envelope_blocks_direct_reuse | not_covered | none found | TTL expiry does not hard block active direct reuse |
| valid_document_but_stale_verification_requires_rerun | partially_covered | external evidence/applied proofs reject stale or expired evidence | not modeled with separate document validity vs verification freshness |
| fresh_ingestion_old_source_observed_at_blocks_freshness | not_covered | source_observed_at/system_ingested_at absent | TE_ext axes missing |
| prefer_recent_selects_new_record | partially_covered | freshness scoring prefers newer KT/PT by score | no deterministic prefer_recent selection stress |
| historical_as_of_selects_old_record | not_covered | historical_as_of enum exists | no retrieval semantics |
| non_overlapping_validity_records_do_not_conflict | not_covered | no overlap-aware temporal conflict | missing temporal conflict formula |
| overlapping_validity_conflict_blocks_reuse | partially_covered | ConflictCheck flags incompatible/stale-vs-fresh proof pairs | no validity interval overlap logic |
| quarantine_proximity_blocks_reuse | partially_covered | graph proximity/applied proof blocks quarantine direct reuse | proof-only, no active hard gate |
| deadend_proximity_blocks_route | partially_covered | graph proximity/applied proof blocks deadend direct reuse | proof-only, no route reuse gate |
| reuse_frequency_cannot_override_staleness | not_covered | reuse_count absent | no capped ReuseBoost |
| gt_ttl_decay_penalizes_bad_old_record | partially_covered | GT half_life/decay and reuse_gate GTTrust scoring exist | no survival hard-gate override |
| future_timestamp_quarantined | not_covered | none found | no ClockOK |
| negative_ttl_rejected | partially_covered | schema and Post V&V schema validation reject negative ttl_seconds | LocalDRS write path does not schema validate |
| audit_replay_uses_historical_time | not_covered | hash-chain continuity proof exists | no audit replay query mode |
| accepted_evidence_not_future_action_permission | partially_covered | docs/proofs state accepted evidence is not action permission | no time stress scenario |
| root_shortcut_required_for_any_direct_final_reuse | already_covered | Root direct reuse requires explicit allow_direct_reuse and Root path | no long-lived aging hard gates |
| supersession_requires_root_accepted_trustworthy_new_record | not_covered | ConflictCheck has stale_vs_fresh proof but no trust-aware supersession | RootAcceptedForSupersession and TrustClassAllowedToSupersede absent |
| fresh_unaccepted_observation_cannot_supersede_work | not_covered | artifact vocabulary distinguishes ConnectorObservation/EvidenceCandidate/SemanticDraft from Work authority | no temporal supersession stress proof |
| quarantine_proximity_computation_is_bounded | not_covered | graph proximity proof computes bounded demo graph, but no max_lineage_hops hard bound | CandidateSet_pre and aggregate_taint_signal absent |
| quarantine_taint_does_not_cascade_to_whole_graph | not_covered | docs say quarantine is not reusable, but no taint propagation model exists | no anti-DoS taint proof |
| reuse_boost_cannot_override_hard_gates | not_covered | reuse_count / ReuseBoost absent | no hard-gate isolation proof |

## 16. Gap Classification

| gap_id | classification | current evidence | risk | recommended stage | recommended next action |
| --- | --- | --- | --- | --- | --- |
| gap_te_ext_axes | schema_gap | TimeEnvelope lacks source_observed_at/source_reported_at/system_ingested_at/system_verified_at | medium | Stage 2 | plan math/invariants extension first |
| gap_tq_query_modes | schema_gap | TemporalQuery lacks query_mode and required_time_axes | high | Stage 2 | plan query-mode semantics before schema/runtime |
| gap_temporal_hard_gate | runtime_gap | reuse_gate freshness is score metadata | high | Stage 2 then Stage 3 | document hard gate formula before proof runner |
| gap_direct_reuse_decision_class | runtime_gap | Root shortcut exists but not full DirectReuseAllowed formula | high | Stage 2 | define RootShortcutAllowed and fallback states |
| gap_query_state | schema_gap | lifecycle/status exists, query_state absent | medium | Stage 2 | document query-local state distinction |
| gap_temporal_conflict_supersession | math_docs_gap | ConflictCheck has stale/fresh proof, no interval overlap or supersession | high | Stage 2 | add temporal conflict and supersession invariants |
| gap_trust_aware_supersession | math_docs_gap | no RootAcceptedForSupersession or TrustClassAllowedToSupersede | high | Stage 2 | document trust-aware supersession before implementation |
| gap_quarantine_deadend_proximity_gate | runtime_gap | proof-only proximity exists | high | Stage 2 then Stage 3 | specify bounded thresholds and hard block semantics |
| gap_bounded_taint_propagation | math_docs_gap | no CandidateSet_pre, max_lineage_hops, or aggregate taint signals | high | Stage 2 | document bounded quarantine/deadend proximity and anti-DoS invariant |
| gap_survival_reuse_boost | math_docs_gap | GT-TTL formulas exist but lack capped ReuseBoost and hard-gate override | medium | Stage 2 | update survival formula, isolation rules, and hard gates |
| gap_clock_pathology | test_gap | no future timestamp/skew/DST tests found | high | Stage 4 | add after proof runner |
| gap_audit_replay | proof_runner_gap | hash-chain continuity exists, no replay evaluator | medium | Stage 3 | design deterministic historical_as_of proof |
| gap_empty_time_tests | test_gap | tests/test_time_envelope_required.py and tests/test_temporal_query_required.py are empty | medium | Stage 4 | replace with focused tests later |
| gap_localdrs_schema_validation | runtime_gap | LocalDRS manual validation does not use full DRS schema | medium | deferred_future_layer | keep out of first aging stress unless needed |
| gap_external_drs | deferred_future_layer | external/global DRS explicitly future | low for this layer | none | do not implement |
| gap_artifact_type | no_gap | vocabulary paused by Guardian | low | none | do not touch artifact_type vocabulary |

## 17. Recommended Staging After Preflight

Stage 2 - Math Appendix / invariants patch:

- Add valid_from / valid_to distinction.
- Add query modes.
- Add hard temporal gates.
- Add query-local state.
- Add quarantine/deadend proximity.
- Add bounded quarantine/deadend proximity.
- Add trust-aware supersession.
- Add ReuseBoost isolation.
- Add direct reuse decision class.
- Add clock pathology rules.
- Add audit replay semantics.
- No runtime change yet.

Stage 3 - Deterministic proof runner:

- local deterministic records and queries only.
- no production DRS.
- no external DRS.
- no real connector.
- no network.
- no Gemini.
- no Marennya.
- no UP.

Stage 4 - Focused tests:

- expired/stale records cannot direct reuse.
- historical_as_of differs from prefer_recent.
- deadend/quarantine proximity blocks reuse.
- accepted evidence is not action permission.
- RootShortcutAllowed required.
- proximity computation is bounded.
- unaccepted fresh observation cannot supersede trusted Work.
- ReuseBoost cannot override hard gates.
- DRS reuse not authority.
- Root remains final authority.

Stage 5 - Human walkthrough:

- old memory is not deleted, but cannot act like fresh memory.

Stage 6 - Audit log.

Stage 7 - Docs sync.

## 18. What Not To Do

- do not implement production DRS.
- do not implement external/global DRS.
- do not change artifact_type vocabulary.
- do not add schema enum.
- do not activate Marennya.
- do not activate UP.
- do not create Negative Trace layer.
- do not treat GT-TTL as authority.
- do not treat TTL as deletion.
- do not treat old AcceptedEvidence as action permission.
- do not treat audit replay as current truth.
- do not treat source ingestion time as source freshness.
- do not compute unbounded graph proximity in hot path.
- do not allow fresh unaccepted observations to supersede Work.
- do not let ReuseBoost affect RootShortcutAllowed.

## 19. Final Compact Rule

Memory may survive.
Authority does not survive through memory.
Old records may inform.
Old records may warn.
Old records may explain history.
Old records may suggest rerun.
Old records may not silently authorize direct reuse.
Freshness can expire reuse.
Trust can constrain supersession.
Proximity can warn or block.
Popularity can preserve visibility.
None of them can authorize final reuse.
Root remains final authority.

## 20. Recommended Next Step

Recommended next step after preflight:

- Math Appendix / invariants patch plan, not implementation.
- do not implement proof runner before math/invariants are documented.
- do not modify runtime/schema/tests before patch plan and review.

## 21. Summary

long_lived_drs_ttl_aging_stress_preflight_v01_status: COMPLETE
preflight_only: true
patch_applied: false
runtime_modified: false
schemas_modified: false
tests_modified: false
docs_modified_except_preflight: false
proof_runner_created: false
external_drs_implemented: false
production_drs_implemented: false
artifact_type_vocabulary_changed: false
schema_enum_created: false
marennya_activated: false
up_activated: false
negative_trace_layer_created: false
time_envelope_current_basis_confirmed: TE = (PT, KT, ET, CT, TTL)
te_ext_needed: true
tq_ext_needed: true
temporal_hard_gate_needed: true
direct_reuse_decision_class_needed: true
query_local_state_needed: true
quarantine_deadend_proximity_gate_needed: true
bounded_quarantine_deadend_proximity_needed: true
trust_aware_supersession_needed: true
reuseboost_isolation_needed: true
clock_pathology_rules_needed: true
audit_replay_semantics_needed: true
recommended_next_stage: Math Appendix / invariants patch plan
recommended_next_stage_requires_user_approval: true
root_remains_final_authority: true
production_ready_claimed: false
public_auditor_ready_claimed: false
