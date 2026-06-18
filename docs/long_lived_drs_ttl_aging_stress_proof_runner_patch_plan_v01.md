# Long-lived DRS State / TTL / Aging Stress v0.1 Proof Runner Patch Plan

## 1. Status

long_lived_drs_ttl_aging_stress_proof_runner_patch_plan_v01_status: COMPLETE
plan_only: true
patch_applied: false
proof_runner_created: false
tests_created: false
runtime_modified: false
schemas_modified: false
docs_modified_except_patch_plan: false
production_drs_implemented: false
external_drs_implemented: false
real_connector_used: false
network_used: false
gemini_used: false
marennya_activated: false
up_activated: false
negative_trace_layer_created: false
production_ready_claimed: false
public_auditor_ready_claimed: false

## 2. Context

- Preflight committed at `c8c0907`: `Add long-lived DRS TTL aging stress preflight`.
- Math/invariants patch plan committed at `49b0a11`: `Add long-lived DRS TTL aging math invariants patch plan`.
- Math/invariants docs patch committed at `1cc9c69`: `Document long-lived DRS TTL aging math invariants`.
- This plan is for a deterministic proof runner only.
- No proof runner, tests, runtime behavior, schema change, audit log, or human walkthrough is created by this plan.

## 3. Source Of Truth

- Human Passport controls MVP architecture and invariants.
- Math Appendix records formulas and algorithms.
- Invariants file records hard invariant bullets.
- Preflight records implementation gaps.
- Patch plan records where math was inserted.
- This proof runner patch plan must follow the committed math/invariants docs.

Controlling documents:

- `docs/long_lived_drs_ttl_aging_stress_preflight_v01.md`
- `docs/long_lived_drs_ttl_aging_stress_math_invariants_patch_plan_v01.md`
- `specs/math_appendix_v0_3.md`
- `specs/invariants.md`
- `specs/human_passport_v0_25.md`
- `specs/machine_manifest_v0_25.json`
- `specs/schema_package_v0_25_reference.md`
- `README.md`
- `AGENTS.md`

## 4. Proof Goal

The future proof runner must prove locally and deterministically:

- old memory may remain visible.
- stale memory may become context_only / warning_only / historical_replay / rerun_required.
- stale memory must not silently become direct_final_reuse.
- expired or malformed time data blocks direct reuse.
- freshness hard gates beat ReuseScore, semantic similarity, reuse frequency, ReuseBoost, and Survival.
- RootShortcutAllowed is required for direct final reuse.
- AcceptedEvidence from the past is not future action permission.
- fresh unaccepted observations cannot supersede trusted Work.
- quarantine/deadend proximity can block or warn.
- bounded proximity computation prevents unbounded graph traversal / taint cascade.
- Root remains final authority.

The future proof must demonstrate the compact rule:

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

## 5. Proposed Future Files

| future file | purpose | allowed in future patch? | notes |
| ----------- | ------- | ------------------------ | ----- |
| `demo/run_long_lived_drs_ttl_aging_stress_v01.py` | deterministic local proof runner for the 25 time/DRS aging scenarios | yes | local Python only; no production DRS, external/global DRS, network, Gemini, Marennya, UP, or schema changes |
| `tests/test_long_lived_drs_ttl_aging_stress_v01_runner.py` | focused tests for proof output, scenario coverage, counters, and authority guardrails | yes | targeted tests only; do not run full pytest unless explicitly requested |
| `docs/audit_reports/auditor_long_lived_drs_ttl_aging_stress_v01.log` | later audit record after proof and tests pass | no, not in initial proof runner patch | create only in a separate audit-log task |
| human walkthrough file | later human-readable walkthrough after proof and tests pass | no, not in initial proof runner patch | create only in a separate walkthrough task |

Do not create any of these files in this plan-only task.

## 6. Proposed Proof Data Model

The future runner should use deterministic local Python-only structures. Local
dataclasses are acceptable if they keep the proof readable; dictionaries are
acceptable if they match the existing demo style better. The proof data model
must remain separate from active runtime schemas.

### A. TimeEnvelope / Extended Envelope

Fields:

- pt_created_at
- kt_asof
- et_observed_at
- ct_session_anchor
- ttl_seconds
- valid_from
- valid_to
- source_observed_at
- source_reported_at
- system_ingested_at
- system_verified_at
- freshness_class

### B. TemporalQuery / Extended Query

Fields:

- as_of
- query_mode
- time_range
- freshness_bias
- max_age_seconds
- required_time_axes
- risk_class
- domain
- reuse_intent

### C. Local DRS Record

Fields:

- record_id
- layer
- lifecycle_state
- subject_key
- claim_dimension
- content
- time_envelope
- authority_class
- root_accepted
- root_accepted_for_supersession
- root_shortcut_allowed
- provenance_chain_valid
- replacement_reason_present
- gt_trust
- reuse_count
- utility_history
- safety_score
- provenance_quality
- conflict_penalty
- quarantine_taint_summary
- deadend_taint_summary
- lineage_refs

### D. Query Evaluation Result

Fields:

- record_id
- query_state
- reuse_decision_class
- temporal_hard_gate_ok
- freshness_ok
- validity_interval_ok
- conflict_ok
- quarantine_proximity_ok
- deadend_proximity_ok
- gt_trust_ok
- permission_ok
- root_shortcut_allowed
- reuse_score
- survival_score
- direct_reuse_allowed
- root_final_authority_preserved
- reason_codes

## 7. Required Formulas For Proof Runner

Plan local pure functions:

- parse_time / normalize_time
- age_axis
- clock_ok
- validity_interval_ok
- freshness_ok
- temporal_hard_gate
- temporal_conflict
- trust_class_allowed_to_supersede
- supersedes
- candidate_set_pre
- lineage_decay
- quarantine_proximity
- deadend_proximity
- reuse_boost
- survival_score
- reuse_score
- direct_reuse_allowed
- reuse_decision_class
- evaluate_record_for_query
- evaluate_scenario

Required formulas:

```text
TemporalHardGate(r,TQ) =
  TimeEnvelopePresent(r)
  and TemporalQueryPresent(TQ)
  and ClockOK(r)
  and ValidityIntervalOK(r,TQ)
  and FreshnessOK(r,TQ)
```

```text
FreshnessOK(r,TQ) =
  forall axis in required_time_axes(TQ):
    Age_axis(r, as_of(TQ)) <= min(TTL_axis(r), max_age_axis(TQ))
```

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

```text
CandidateSet_pre =
  filter_by_domain
  intersection filter_by_time_window
  intersection filter_by_subject_or_claim_key
  intersection top_k_semantic_candidates
```

```text
LineageDecay(d) = exp(-lambda_lineage * d)
```

```text
ReuseBoost(r) =
  min(
    1 + k * ln(1 + reuse_count(r)),
    reuse_boost_max
  )
```

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

## 8. Required Scenario Table

The future proof runner must cover exactly or at least these 25 scenarios:

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

For each scenario, the future implementation should define:

- setup records.
- temporal query.
- expected query_state.
- expected reuse_decision_class.
- expected direct_reuse_allowed.
- expected root_final_authority_preserved.
- expected reason_codes.
- expected notes.

## 9. Scenario Expectations

| scenario | expected direct_reuse_allowed | expected query_state | expected reuse_decision_class | key invariant |
| -------- | ----------------------------- | -------------------- | ----------------------------- | ------------- |
| missing_time_envelope_rejected | false | blocked_by_time_gate | blocked | TimeEnvelopePresent is required |
| drs_query_without_temporal_query_rejected | false | blocked_by_time_gate | blocked | TemporalQueryPresent is required |
| fresh_record_direct_reuse_candidate_but_root_required | false unless RootShortcutAllowed true | fresh_candidate | partial_reuse_then_validation or direct_final_reuse only if allowed | RootShortcutAllowed gates direct final reuse |
| stale_work_record_context_only_not_direct_reuse | false | stale_context_only | context_only | stale Work can inform but not silently authorize reuse |
| expired_time_envelope_blocks_direct_reuse | false | blocked_by_time_gate | context_only or blocked | TemporalHardGate beats scoring |
| valid_document_but_stale_verification_requires_rerun | false | rerun_required | partial_reuse_then_validation | document validity is not verification freshness |
| fresh_ingestion_old_source_observed_at_blocks_freshness | false | blocked_by_time_gate | context_only or rerun_required | fresh ingestion is not fresh knowledge |
| prefer_recent_selects_new_record | only newer fresh candidate can rank higher, not authority | fresh_candidate | partial_reuse_then_validation | ranking is not authority |
| historical_as_of_selects_old_record | false for current decision | historical_only | historical_replay for historical query | historical_as_of differs from current_decision |
| non_overlapping_validity_records_do_not_conflict | no conflict | fresh_candidate or historical_only | partial_reuse_then_validation | time windows can make both records valid |
| overlapping_validity_conflict_blocks_reuse | false | blocked_by_conflict | blocked | ConflictGate beats reuse |
| quarantine_proximity_blocks_reuse | false | blocked_by_quarantine_proximity | blocked | Quarantine proximity blocks direct reuse |
| deadend_proximity_blocks_route | false | blocked_by_deadend_proximity | blocked | DeadEnd proximity blocks route reuse |
| reuse_frequency_cannot_override_staleness | false | blocked_by_time_gate | context_only or blocked | reuse frequency cannot override freshness gates |
| gt_ttl_decay_penalizes_bad_old_record | false or downgraded | stale_context_only | context_only | GT-TTL decay is advisory, not authority |
| future_timestamp_quarantined | false | blocked_by_time_gate | blocked | ClockOK must reject/review future timestamps |
| negative_ttl_rejected | false | blocked_by_time_gate | blocked | negative TTL rejects the record |
| audit_replay_uses_historical_time | false for current direct reuse | historical_only | historical_replay for audit replay | audit replay uses historical time, not current truth |
| accepted_evidence_not_future_action_permission | false | rerun_required | partial_reuse_then_validation | AcceptedEvidence is not action permission |
| root_shortcut_required_for_any_direct_final_reuse | false unless RootShortcutAllowed true | fresh_candidate or blocked_by_time_gate | direct_final_reuse only if all gates pass | Root remains final authority |
| supersession_requires_root_accepted_trustworthy_new_record | false until root-accepted trustworthy supersession | warning_only or rerun_required | warning_only or partial_reuse_then_validation | RootAcceptedForSupersession and TrustClassAllowedToSupersede are required |
| fresh_unaccepted_observation_cannot_supersede_work | false | warning_only or rerun_required | warning_only or partial_reuse_then_validation | fresh unaccepted observation cannot supersede Work |
| quarantine_proximity_computation_is_bounded | false if proximity threshold exceeded | blocked_by_quarantine_proximity | blocked | max_lineage_hops and CandidateSet_pre must be used |
| quarantine_taint_does_not_cascade_to_whole_graph | false for tainted close candidates only | warning_only or blocked_by_quarantine_proximity | warning_only or blocked | quarantine taint is bounded |
| reuse_boost_cannot_override_hard_gates | false when hard gate fails regardless of high reuse_count | blocked_by_time_gate | context_only or blocked | ReuseBoost cannot override hard gates |

## 10. Expected Proof Output Shape

The future runner should print a human-readable deterministic report with these
sections:

- title.
- purpose.
- compact rule.
- formula summary.
- scenario table.
- aggregate counters.
- failed gates summary.
- authority preservation summary.
- limitations.

Required aggregate counters:

- scenarios_total
- scenarios_passed
- direct_reuse_allowed_count
- direct_reuse_blocked_count
- context_only_count
- warning_only_count
- historical_replay_count
- rerun_required_count
- blocked_count
- root_final_authority_preserved_count
- unbounded_graph_traversal_used_count
- reuse_boost_hard_gate_overrides_count
- unaccepted_supersession_count
- accepted_evidence_action_permission_count
- production_drs_used_count
- external_drs_used_count
- network_used_count
- gemini_used_count
- marennya_activated_count
- up_activated_count

Required PASS conditions:

```text
scenarios_passed == scenarios_total
root_final_authority_preserved_count == scenarios_total
unbounded_graph_traversal_used_count == 0
reuse_boost_hard_gate_overrides_count == 0
unaccepted_supersession_count == 0
accepted_evidence_action_permission_count == 0
production_drs_used_count == 0
external_drs_used_count == 0
network_used_count == 0
gemini_used_count == 0
marennya_activated_count == 0
up_activated_count == 0
```

## 11. Expected Test Assertions

The future test file should assert:

- runner exits successfully.
- all 25 scenarios are present.
- every scenario PASSes.
- missing TimeEnvelope blocks direct reuse.
- missing TemporalQuery blocks direct reuse.
- expired/stale records cannot direct reuse.
- valid document but stale verification requires rerun.
- fresh ingestion old source blocks freshness.
- historical_as_of differs from current_decision/prefer_recent.
- non-overlapping validity records do not conflict.
- overlapping validity conflict blocks reuse.
- quarantine proximity blocks reuse.
- deadend proximity blocks route.
- reuse frequency cannot override staleness.
- GT-TTL decay penalizes bad old record.
- future timestamp is blocked/quarantined.
- negative TTL is rejected.
- audit replay uses historical time.
- accepted evidence is not future action permission.
- RootShortcutAllowed required.
- supersession requires Root-accepted trustworthy new record.
- fresh unaccepted observation cannot supersede Work.
- proximity computation is bounded.
- quarantine taint does not cascade to whole graph.
- ReuseBoost cannot override hard gates.
- DRS reuse is not authority.
- Root remains final authority.
- no production DRS.
- no external/global DRS.
- no network/Gemini.
- no Marennya/UP.

## 12. Explicit Non-goals

- no production DRS.
- no external/global DRS.
- no real database.
- no distributed DRS.
- no real time synchronization.
- no clock security.
- no real connector.
- no network.
- no Gemini.
- no Marennya.
- no UP.
- no Negative Trace layer.
- no artifact_type vocabulary change.
- no schema enum.
- no runtime integration.
- no schema change.
- no production readiness.
- no public auditor readiness.

## 13. Recommended Future Patch Order

Next implementation patch after this plan:

Allowed future files:

- `demo/run_long_lived_drs_ttl_aging_stress_v01.py`
- `tests/test_long_lived_drs_ttl_aging_stress_v01_runner.py`

Possible future docs only after proof:

- README.md / AGENTS.md status update.
- `specs/machine_manifest_v0_25.json` status update.
- human walkthrough.
- audit log.
- docs sync.

Those docs are not part of the initial proof runner patch unless explicitly
requested.

## 14. Validation For This Plan-only Task

Run:

```text
git status --short
git diff --stat
git diff --check

wc -l docs/long_lived_drs_ttl_aging_stress_proof_runner_patch_plan_v01.md

sed -n '1,300p' docs/long_lived_drs_ttl_aging_stress_proof_runner_patch_plan_v01.md
tail -n 260 docs/long_lived_drs_ttl_aging_stress_proof_runner_patch_plan_v01.md
```

Positive grep:

```text
rg -n "long_lived_drs_ttl_aging_stress_proof_runner_patch_plan_v01_status|plan_only: true|patch_applied: false|proof_runner_created: false|tests_created: false|runtime_modified: false|schemas_modified: false|c8c0907|49b0a11|1cc9c69|demo/run_long_lived_drs_ttl_aging_stress_v01.py|tests/test_long_lived_drs_ttl_aging_stress_v01_runner.py|TemporalHardGate|FreshnessOK|DirectReuseAllowed|Supersedes|RootAcceptedForSupersession|TrustClassAllowedToSupersede|CandidateSet_pre|LineageDecay|ReuseBoost|Survival|missing_time_envelope_rejected|drs_query_without_temporal_query_rejected|expired_time_envelope_blocks_direct_reuse|fresh_ingestion_old_source_observed_at_blocks_freshness|historical_as_of_selects_old_record|quarantine_proximity_blocks_reuse|deadend_proximity_blocks_route|reuse_frequency_cannot_override_staleness|accepted_evidence_not_future_action_permission|root_shortcut_required_for_any_direct_final_reuse|supersession_requires_root_accepted_trustworthy_new_record|fresh_unaccepted_observation_cannot_supersede_work|quarantine_proximity_computation_is_bounded|quarantine_taint_does_not_cascade_to_whole_graph|reuse_boost_cannot_override_hard_gates|scenarios_passed == scenarios_total|root_final_authority_preserved_count == scenarios_total|unbounded_graph_traversal_used_count == 0|reuse_boost_hard_gate_overrides_count == 0|unaccepted_supersession_count == 0|accepted_evidence_action_permission_count == 0|production_drs_used_count == 0|external_drs_used_count == 0|network_used_count == 0|gemini_used_count == 0|marennya_activated_count == 0|up_activated_count == 0|Memory may survive|Authority does not survive through memory|Root remains final authority" docs/long_lived_drs_ttl_aging_stress_proof_runner_patch_plan_v01.md
```

Overclaim grep:

- run the requester-provided overclaim grep against this plan and repository
  docs.
- expected result for this new file: no positive overclaim.
- historical audit logs or already-committed docs may produce safe false
  positives and should be reported as such.

Final accidental-change check:

```text
git diff --name-only
```

Allowed changed file exactly:

- `docs/long_lived_drs_ttl_aging_stress_proof_runner_patch_plan_v01.md`

If any other file changed, stop and report.
If overclaim grep finds safe historical false positives, report them.
If overclaim grep finds positive overclaim in the new file, stop and fix.
Do not commit.

## 15. Summary

long_lived_drs_ttl_aging_stress_proof_runner_patch_plan_v01_status: COMPLETE
plan_only: true
patch_applied: false
proof_runner_created: false
tests_created: false
runtime_modified: false
schemas_modified: false
docs_modified_except_patch_plan: false
production_drs_implemented: false
external_drs_implemented: false
real_connector_used: false
network_used: false
gemini_used: false
marennya_activated: false
up_activated: false
negative_trace_layer_created: false
future_proof_runner_file_planned: demo/run_long_lived_drs_ttl_aging_stress_v01.py
future_test_file_planned: tests/test_long_lived_drs_ttl_aging_stress_v01_runner.py
scenario_inventory_count: 25
expected_pass_condition: scenarios_passed == scenarios_total
root_final_authority_expected: root_final_authority_preserved_count == scenarios_total
unbounded_graph_traversal_used_count_expected: 0
reuse_boost_hard_gate_overrides_count_expected: 0
unaccepted_supersession_count_expected: 0
accepted_evidence_action_permission_count_expected: 0
production_drs_used_count_expected: 0
external_drs_used_count_expected: 0
network_used_count_expected: 0
gemini_used_count_expected: 0
marennya_activated_count_expected: 0
up_activated_count_expected: 0
recommended_next_patch: deterministic proof runner and focused test patch
recommended_next_patch_requires_user_approval: true
root_remains_final_authority: true
production_ready_claimed: false
public_auditor_ready_claimed: false
