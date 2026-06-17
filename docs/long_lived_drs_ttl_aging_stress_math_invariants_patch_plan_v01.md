# Long-lived DRS State / TTL / Aging Stress v0.1 Math Appendix / Invariants Patch Plan

## 1. Status

long_lived_drs_ttl_aging_stress_math_invariants_patch_plan_v01_status: COMPLETE
plan_only: true
patch_applied: false
runtime_modified: false
schemas_modified: false
tests_modified: false
proof_runner_created: false
audit_log_created: false
docs_modified_except_patch_plan: false
production_drs_implemented: false
external_drs_implemented: false
marennya_activated: false
up_activated: false
negative_trace_layer_created: false
production_ready_claimed: false
public_auditor_ready_claimed: false

## 2. Context

Commit `c8c0907` committed the read-only preflight:
`docs/long_lived_drs_ttl_aging_stress_preflight_v01.md`.

The next major layer is Long-lived DRS State / TTL / Aging Stress v0.1.
The final math basis for this layer is TIME / DRS AGING v0.2.

This plan prepares docs/spec insertion only. It does not apply the Math
Appendix / invariants docs patch, does not implement runtime behavior, does
not change schemas, does not add tests, and does not create a proof runner.

## 3. Source Of Truth Hierarchy

- Human Passport controls MVP architecture and invariants.
- Math Appendix records formulas and algorithms.
- Invariants file records hard invariant bullets.
- Machine manifest records machine-readable checkpoint status.
- README / AGENTS record engineering order and current layer status.
- If conflict exists, Human Passport controls current MVP implementation.

Inspected inputs for this plan:

- `docs/long_lived_drs_ttl_aging_stress_preflight_v01.md`
- `specs/math_appendix_v0_3.md`
- `specs/invariants.md`
- `specs/human_passport_v0_25.md`
- `specs/machine_manifest_v0_25.json`
- `specs/schema_package_v0_25_reference.md`
- `README.md`
- `AGENTS.md`
- `schemas/time_envelope.schema.json`
- `schemas/temporal_query.schema.json`
- `schemas/drs_record.schema.json`
- `schemas/world_state.schema.json`
- `schemas/result_proposal.schema.json`
- `schemas/gt_report.schema.json`
- `schemas/final_output.schema.json`
- `schemas/common.schema.json`

## 4. Required Existing Formula To Preserve

The existing TimeEnvelope formula must be preserved:

```text
TE = (PT, KT, ET, CT, TTL)
```

Where:

- PT = Physical Time / system-created time.
- KT = Knowledge Time / as-of time.
- ET = Event Time / observed event time.
- CT = Context Time / session/context anchor.
- TTL = time-to-live / freshness lifetime.

Required rule:

- Do not replace the existing TimeEnvelope formula.
- Extend it operationally.

## 5. Proposed Docs/Spec Insertion Map

| target file | target section | change type | content to add | why | risk if not added |
| --- | --- | --- | --- | --- | --- |
| `specs/math_appendix_v0_3.md` | after existing Section 2 Time material and cross-reference Section 8 GT-TTL, or as a dedicated subsection after Section 8 if maintainers prefer one consolidated math block | add dedicated subsection | `Long-lived DRS State / TTL / Aging Stress v0.1 - Math Invariants` with TE_ext, TQ_ext, Age_effective, TemporalHardGate, FreshnessOK, ValidityIntervalOK, FreshIngestionDoesNotImplyFreshKnowledge, TemporalConflict, trust-aware Supersedes, CandidateSet_pre, bounded QuarantineProximity, bounded DeadEndProximity, LineageDecay, ReuseDecisionClass, DirectReuseAllowed, ReuseBoost, Survival, clock pathology rules, AuditReplay historical_as_of semantics, `AcceptedEvidence(t_old) != ActionPermission(t_now)`, and final compact rule | Math Appendix is the formula home; Stage 2 must document math before runtime/schema/test work | Runtime or proof runner could implement inconsistent time semantics |
| `specs/invariants.md` | near existing DRS time requirement and DRS graph proximity / lineage invariant blocks | add hard invariant bullets | Time is reuse boundary not authority; failed TemporalHardGate blocks direct reuse; DRS retrieval is not direct reuse; Age_effective is ranking metadata only; fresh ingestion is not fresh knowledge; TTL expiry is not claim invalidity; claim validity interval is not record freshness; query mode determines temporal validity; `record.lifecycle_state != query_state`; freshness gates beat scoring/survival; RootShortcutAllowed required; unaccepted observations/drafts/pointers/candidates cannot supersede Work; ReuseBoost cannot affect RootShortcutAllowed or hard gates; bounded proximity only; quarantine taint cannot cascade; AcceptedEvidence from past is not future action permission; audit hash proves continuity not truth; Root remains final authority | invariants file is where future implementers look for non-negotiable constraints | Authority leakage, stale direct reuse, or unbounded graph traversal could be introduced later |
| `specs/human_passport_v0_25.md` | Time Model section and current checkpoint area | add architecture-level checkpoint | Long-lived DRS / TTL / Aging Stress is the next major layer after artifact_type vocabulary pause; time/DRS aging invariants come first; runtime/schema/tests/proof runner are future stages; Memory may survive; authority does not survive through memory; Root remains final authority | Human Passport controls MVP architecture | Engineers may jump directly to runtime/proof runner without the governing math |
| `specs/machine_manifest_v0_25.json` | checkpoint/status metadata | add future machine-readable fields only in the actual docs patch | fields listed in Section 5D below | manifest should reflect the docs-only Stage 2 checkpoint | downstream automation cannot see the layer status |
| `README.md` | current checkpoint / roadmap area after artifact_type Mapping status | add concise checkpoint section | preflight `c8c0907`; math/invariants patch next; no runtime/schema/test/proof runner yet; compact rule included | README records public engineering order | readers may mistake preflight for implementation |
| `AGENTS.md` | Current engineering focus / current engineering order | add engineering order update | current next layer is Long-lived DRS TTL Aging Stress math/invariants patch; do not jump to proof runner/runtime/schema/tests; do not modify artifact_type vocabulary; do not start Marennya/UP/Negative Trace/external DRS | AGENTS guides future coding turns | future agents may start a forbidden layer |
| `specs/schema_package_v0_25_reference.md` | near TimeEnvelope / TemporalQuery copied schemas | add schema-reference note only | TimeEnvelope / TemporalQuery schemas do not yet include all TE_ext/TQ_ext fields; expected at math/invariants stage; future schema changes require separate approved schema patch plan | avoids schema/reference confusion without modifying active schemas | schema readers may assume TE_ext/TQ_ext are active schema fields |

### 5A. `specs/math_appendix_v0_3.md`

Future patch should add a dedicated subsection titled:

```text
Long-lived DRS State / TTL / Aging Stress v0.1 - Math Invariants
```

The subsection must include:

- TE_ext.
- TQ_ext.
- Age_effective as ranking metadata only.
- TemporalHardGate.
- FreshnessOK.
- ValidityIntervalOK.
- FreshIngestionDoesNotImplyFreshKnowledge.
- TemporalConflict.
- trust-aware Supersedes.
- CandidateSet_pre.
- bounded QuarantineProximity.
- bounded DeadEndProximity.
- LineageDecay.
- ReuseDecisionClass.
- DirectReuseAllowed.
- ReuseBoost.
- Survival.
- clock pathology rules.
- AuditReplay historical_as_of semantics.
- `AcceptedEvidence(t_old) != ActionPermission(t_now)`.
- final compact rule.

### 5B. `specs/invariants.md`

Future patch should add hard invariant bullets:

- Time is reuse boundary, not authority.
- Failed TemporalHardGate blocks direct reuse.
- DRS retrieval is not direct reuse.
- Age_effective is ranking metadata, not permission.
- Fresh ingestion is not fresh knowledge.
- TTL expiry is not claim invalidity.
- Claim validity interval is not record freshness.
- Query mode determines temporal validity.
- `record.lifecycle_state != query_state`.
- Freshness hard gate beats ReuseScore / ReuseFrequency / SemanticSimilarity / Survival.
- RootShortcutAllowed required for any direct final reuse.
- Unaccepted ConnectorObservation / SemanticDraft / ExternalDRSPointer / EvidenceCandidate cannot supersede Work.
- ReuseBoost cannot affect RootShortcutAllowed or hard gates.
- Bounded proximity only; no unbounded graph traversal in hot path.
- Quarantine taint cannot cascade-taint the whole DRS graph.
- AcceptedEvidence from past is not future action permission.
- Audit hash proves continuity, not truth.
- Root remains final authority.

### 5C. `specs/human_passport_v0_25.md`

Future patch should add a short architecture-level checkpoint:

- Long-lived DRS / TTL / Aging Stress is the next major layer after the
  artifact_type vocabulary pause.
- The layer must first document time/DRS aging invariants.
- Runtime/schema/tests/proof runner remain future stages.
- Root remains final authority.
- Memory may survive; authority does not survive through memory.

### 5D. `specs/machine_manifest_v0_25.json`

Future patch should plan these fields, but this plan does not edit the manifest:

```text
long_lived_drs_ttl_aging_stress_preflight_commit: c8c0907
long_lived_drs_ttl_aging_stress_preflight_v01_status: complete
long_lived_drs_ttl_aging_stress_math_invariants_patch_plan_v01_status: complete
time_envelope_current_basis: "TE = (PT, KT, ET, CT, TTL)"
te_ext_documented: true
tq_ext_documented: true
temporal_hard_gate_documented: true
direct_reuse_gate_documented: true
bounded_proximity_documented: true
trust_aware_supersession_documented: true
reuseboost_isolation_documented: true
clock_pathology_rules_documented: true
accepted_evidence_time_boundary_documented: true
runtime_modified: false
schemas_modified: false
tests_modified: false
proof_runner_created: false
root_remains_final_authority: true
next_layer: "Long-lived DRS TTL Aging Stress math/invariants patch"
```

### 5E. `README.md`

Future patch should add a checkpoint section:

- Long-lived DRS State / TTL / Aging Stress v0.1 read-only preflight committed
  at `c8c0907`.
- Math/invariants patch is next.
- No runtime/schema/test/proof runner yet.
- The compact rule must be included.

### 5F. `AGENTS.md`

Future patch should update engineering order:

- Current next layer is Long-lived DRS TTL Aging Stress math/invariants patch.
- Do not jump to proof runner/runtime/schema/tests before math/invariants docs.
- Do not modify artifact_type vocabulary.
- Do not start Marennya/UP/Negative Trace/external DRS.

### 5G. `specs/schema_package_v0_25_reference.md`

Future patch should add a schema-reference note only:

- TimeEnvelope / TemporalQuery schemas currently do not yet include all
  TE_ext/TQ_ext fields.
- This is expected at math/invariants stage.
- Future schema changes require a separate approved schema patch plan.

## 6. Required Formulas To Include In Future Math Patch

### TE_ext

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

### TQ_ext

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

### TemporalHardGate

```text
TemporalHardGate(r,TQ) =
  TimeEnvelopePresent(r)
  and TemporalQueryPresent(TQ)
  and ClockOK(r)
  and ValidityIntervalOK(r,TQ)
  and FreshnessOK(r,TQ)
```

### FreshnessOK

```text
FreshnessOK(r,TQ) =
  forall axis in required_time_axes(TQ):
    Age_axis(r, as_of(TQ)) <= min(TTL_axis(r), max_age_axis(TQ))
```

### DirectReuseAllowed

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

### TemporalConflict

```text
TemporalConflict(r_i, r_j, TQ) =
  SameSubject(r_i,r_j)
  and IncompatibleClaim(r_i,r_j)
  and ValidityIntervalsOverlap(r_i,r_j,TQ)
  and not SupersessionExplained(r_i,r_j)
```

### Trust-aware Supersedes

```text
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

Required supersession invariants for the future patch:

- GTTrust is not authority.
- Root acceptance beats freshness.
- authority class beats freshness.
- freshness alone never supersedes trusted Work.
- unaccepted ConnectorObservation cannot supersede Work.
- SemanticDraft cannot supersede Work.
- ExternalDRSPointer cannot supersede Work.
- EvidenceCandidate cannot supersede Work.

### CandidateSet_pre

```text
CandidateSet_pre =
  filter_by_domain
  intersection filter_by_time_window
  intersection filter_by_subject_or_claim_key
  intersection top_k_semantic_candidates
```

### Bounded proximity

```text
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

Anti-DoS invariant:

- quarantine_taint propagation must be bounded.
- a quarantined record cannot cascade-taint the whole DRS graph.

### ReuseBoost

```text
ReuseBoost(r) =
  min(
    1 + k * ln(1 + reuse_count(r)),
    reuse_boost_max
  )
```

Required isolation:

- ReuseBoost affects survival/ranking only.
- ReuseBoost cannot affect RootShortcutAllowed.
- ReuseBoost cannot affect DirectReuseAllowed hard gates.
- ReuseBoost cannot create authority.
- ReuseBoost cannot override hard gates.
- reuse_boost_cannot_override_hard_gates is a required future stress scenario.

### Survival

```text
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

### Clock pathology rules

Future docs patch should list invalid or suspicious cases:

- future_PT.
- future_KT.
- future_ET_without_explanation.
- ET_after_PT_without_explanation.
- valid_to_before_valid_from.
- negative_TTL.
- zero_TTL_without_policy.
- timezone_mismatch.
- clock_skew.
- DST_ambiguous_local_time.

Clock pathology cannot create freshness.

### AuditReplay historical_as_of semantics

Future docs patch should state:

- AuditReplay(TQ) requires query_mode = historical_as_of.
- audit replay evaluates what the system knew at that historical time, not what
  is known now.
- audit hash proves continuity, not truth.
- audit replay is not current truth.

### AcceptedEvidence boundary

```text
AcceptedEvidence(t_old) != ActionPermission(t_now)
```

Required future invariant:

- AcceptedEvidence is bounded evidence.
- AcceptedEvidence is not action permission.
- AcceptedEvidence does not survive time as execution authority.
- Root remains final authority.

### Final compact rule

```text
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
```

## 7. Required Query Modes

Future docs patch should add:

- current_decision.
- historical_as_of.
- audit_replay.
- trend_analysis.
- memory_context_only.
- direct_reuse_candidate.
- warning_lookup.

Required invariant:

- Validity(r, TQ) is query-mode dependent.
- Do not implement retrieval as simply record valid/invalid.
- Implement as valid for query mode and decision class.

## 8. Required Query-local States

Future docs patch should add:

- fresh_candidate.
- stale_context_only.
- historical_only.
- warning_only.
- rerun_required.
- blocked_by_conflict.
- blocked_by_quarantine_proximity.
- blocked_by_deadend_proximity.
- blocked_by_time_gate.

Required invariant:

```text
record.lifecycle_state != query_state
```

## 9. Required Stress Scenario Inventory

Future docs patch should include these 25 scenarios as the initial proof
inventory, without implementing them:

1. missing_time_envelope_rejected
2. drs_query_without_temporal_query_rejected
3. fresh_record_direct_reuse_candidate_but_root_required
4. stale_work_record_context_only_not_direct_reuse
5. expired_time_envelope_blocks_direct_reuse
6. valid_document_but_stale_verification_requires_rerun
7. fresh_ingestion_old_source_observed_at_blocks_freshness
8. prefer_recent_selects_new_record
9. historical_as_of_selects_old_record
10. non_overlapping_validity_records_do_not_conflict
11. overlapping_validity_conflict_blocks_reuse
12. quarantine_proximity_blocks_reuse
13. deadend_proximity_blocks_route
14. reuse_frequency_cannot_override_staleness
15. gt_ttl_decay_penalizes_bad_old_record
16. future_timestamp_quarantined
17. negative_ttl_rejected
18. audit_replay_uses_historical_time
19. accepted_evidence_not_future_action_permission
20. root_shortcut_required_for_any_direct_final_reuse
21. supersession_requires_root_accepted_trustworthy_new_record
22. fresh_unaccepted_observation_cannot_supersede_work
23. quarantine_proximity_computation_is_bounded
24. quarantine_taint_does_not_cascade_to_whole_graph
25. reuse_boost_cannot_override_hard_gates

## 10. Explicit Deferrals

Stage 2 must defer:

- no runtime implementation in Stage 2.
- no schema changes in Stage 2.
- no tests in Stage 2.
- no proof runner in Stage 2.
- no production DRS.
- no external/global DRS.
- no artifact_type vocabulary change.
- no schema enum.
- no Marennya.
- no UP.
- no Negative Trace layer.

## 11. Validation Plan For Future Patch

The future Math Appendix / invariants docs patch should run:

```text
git status --short
python3 -m json.tool specs/machine_manifest_v0_25.json > /tmp/hedgehog_machine_manifest_check.json
git diff --stat
git diff --check
positive grep for formulas and invariants
overclaim grep for forbidden claims
```

Do not run full pytest for the docs-only patch unless the user explicitly
requests it.

## 12. Recommended Next Action

Recommended next action after this plan:

- apply Math Appendix / invariants docs patch.
- allowed files should be listed explicitly in the future prompt.
- no runtime/schema/test/proof runner until after docs math/invariants are
  committed and reviewed.

Recommended next patch: Math Appendix / invariants docs patch.
recommended_next_patch_requires_user_approval: true

## 13. Summary

long_lived_drs_ttl_aging_stress_math_invariants_patch_plan_v01_status: COMPLETE
plan_only: true
patch_applied: false
preflight_commit: c8c0907
target_files_for_future_patch: specs/math_appendix_v0_3.md, specs/invariants.md, specs/human_passport_v0_25.md, specs/machine_manifest_v0_25.json, README.md, AGENTS.md, specs/schema_package_v0_25_reference.md
te_basis_preserved: TE = (PT, KT, ET, CT, TTL)
te_ext_planned: true
tq_ext_planned: true
temporal_hard_gate_planned: true
direct_reuse_gate_planned: true
bounded_proximity_planned: true
trust_aware_supersession_planned: true
reuseboost_isolation_planned: true
stress_scenario_inventory_planned: 25
runtime_modified: false
schemas_modified: false
tests_modified: false
proof_runner_created: false
audit_log_created: false
docs_modified_except_patch_plan: false
production_drs_implemented: false
external_drs_implemented: false
artifact_type_vocabulary_changed: false
schema_enum_created: false
marennya_activated: false
up_activated: false
negative_trace_layer_created: false
root_remains_final_authority: true
recommended_next_action: Math Appendix / invariants docs patch
recommended_next_patch_requires_user_approval: true
production_ready_claimed: false
public_auditor_ready_claimed: false
