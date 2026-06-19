# DRS Lineage / Provenance Pressure v0.1 — Patch Plan

## 1. Status

* patch_plan_id: drs_lineage_provenance_pressure_patch_plan_v01
* patch_plan_status: COMPLETE
* preflight_commit: e60b40f
* latest_checkpoint_commit: c1f0abd
* proof_runner_created: false
* tests_created: false
* runtime_modified: false
* schemas_modified: false
* production_drs_implemented: false
* external_drs_implemented: false
* network_used: false
* gemini_used: false
* marennya_activated: false
* up_activated: false

## 2. Scope

This patch plan defines a future local deterministic proof runner. It does not
implement runtime lineage pressure, does not modify schemas, does not create
production DRS, and does not create proof files.

The future proof must demonstrate that lineage, provenance, bridge traversal,
quarantine/deadend proximity, ConflictCheck, audit hash continuity,
AcceptedEvidence ancestry, and reuse history can influence review, ranking,
warning, or blocking, but cannot become truth, authority, direct reuse
permission, action permission, DRS write authority, or Root Final authority.

Core invariant:

```text
lineage informs
lineage does not decide
provenance does not become truth
```

## 3. Files Planned

Future files:

* `demo/run_drs_lineage_provenance_pressure_v01.py`
* `tests/test_drs_lineage_provenance_pressure_v01_runner.py`

No other files should be created or modified in the future proof patch unless
explicitly approved later.

## 4. Local Proof Model

The future proof should use local proof-only dataclasses or dictionaries. The
model should be deterministic and independent of filesystem state, network,
APIs, Gemini, external DRS, real connectors, or production persistence.

Required local concepts:

* `LocalLineageRecord`
* `LocalProvenanceRef`
* `LocalTraceRef`
* `LocalEvidenceRef`
* `LocalAuditLink`
* `LocalPressureQuery`
* `LineagePressureResult`
* `ScenarioResult`

Planned `LocalLineageRecord` fields:

* `record_id`
* `record_kind`
* `lifecycle_state`
* `domain`
* `subject_key`
* `claim_key`
* `claim_value`
* `created_at`
* `valid_from`
* `valid_to`
* `trace_refs`
* `source_refs`
* `evidence_refs`
* `parent_record_ids`
* `derived_from_record_ids`
* `bridge_refs`
* `conflict_refs`
* `quarantine_refs`
* `deadend_refs`
* `audit_links`
* `root_accepted`
* `accepted_evidence`
* `root_final`
* `reuse_count`
* `trust_class`
* `authority_status`

Planned `LocalPressureQuery` fields:

* `query_id`
* `domain`
* `subject_key`
* `claim_key`
* `as_of`
* `reuse_intent`
* `risk_class`
* `max_lineage_hops`
* `require_root_review`
* `allow_direct_reuse_if_all_gates_pass`

Planned `LineagePressureResult` fields:

* `scenario_id`
* `query_state`
* `reuse_decision_class`
* `direct_reuse_allowed`
* `root_review_required`
* `lineage_informs`
* `lineage_decides`
* `provenance_truth_claimed`
* `audit_hash_truth_claimed`
* `bridge_transfers_authority`
* `quarantine_global_taint`
* `deadend_global_taint`
* `conflictcheck_advisory_only`
* `gt_advisory_only`
* `root_final_authority_preserved`
* `reason_codes`

Planned supporting local references:

| concept | planned fields | purpose |
| --- | --- | --- |
| `LocalTraceRef` | `trace_id`, `span_id`, `kind` | Model trace ancestry without making the trace authoritative. |
| `LocalProvenanceRef` | `source`, `source_id`, `trace_ref`, `trust_hint` | Model source/provenance pressure as advisory evidence. |
| `LocalEvidenceRef` | `kind`, `summary`, `ref_id`, `confidence` | Model ResultProposal-style evidence refs. |
| `LocalAuditLink` | `source_artifact_type`, `source_artifact_id`, `previous_hash`, `entry_hash`, `continuity_valid` | Model audit/hash-chain continuity without truth claims. |
| `ScenarioResult` | `scenario_id`, `status`, expected/actual fields, `reason_codes`, `notes` | Provide testable scenario outputs. |

## 5. Required Scenarios

The future proof must define exactly these scenarios:

1. `trace_derived_from_trace_informs_only`
2. `reuse_candidate_derived_from_old_accepted_evidence_requires_review`
3. `bridge_traversal_across_domain_informs_only`
4. `quarantine_near_reuse_candidate_warns_or_blocks`
5. `deadend_near_reuse_candidate_warns_or_blocks`
6. `conflicting_provenance_blocks_direct_reuse`
7. `trusted_newer_provenance_can_request_supersession_review_but_not_self_authorize`
8. `audit_hash_continuity_does_not_create_truth`
9. `high_reuse_lineage_does_not_create_authority`
10. `root_final_authority_preserved_across_lineage_pressure`

Scenario plan:

| scenario | local input records | query | expected query_state | expected reuse_decision_class | expected direct_reuse_allowed | expected root_review_required | expected reason_codes | authority invariant tested |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| `trace_derived_from_trace_informs_only` | Prior trace record, derived candidate record, `trace_refs`, `derived_from_record_ids` | Same subject/claim current review query | `context_only` or `review_required` | `context_only` or `partial_reuse_then_validation` | false | true | `lineage_informs_only` | lineage_informs=true; lineage_decides=false. |
| `reuse_candidate_derived_from_old_accepted_evidence_requires_review` | Old Root-created AcceptedEvidence ancestor and reuse candidate derived from it | Current action/reuse query | `rerun_required` | `partial_reuse_then_validation` | false | true | `accepted_evidence_ancestry_not_action_permission` | accepted evidence ancestry is not future action permission. |
| `bridge_traversal_across_domain_informs_only` | Source-domain bridge record, target-domain candidate, bridge traversal refs | Cross-domain review query | `context_only` or `warning_only` | `context_only` | false | true | `bridge_informs_only` | bridge traversal informs but does not transfer authority. |
| `quarantine_near_reuse_candidate_warns_or_blocks` | Reuse candidate near quarantine ref within bounded hops | Current reuse query with max lineage hops | `blocked_by_quarantine_proximity` or `warning_only` | `blocked` or `warning_only` | false | true | `quarantine_proximity_bounded` | quarantine proximity is bounded and not global taint. |
| `deadend_near_reuse_candidate_warns_or_blocks` | Reuse candidate near deadend ref within bounded hops | Current route/reuse query with max lineage hops | `blocked_by_deadend_proximity` or `warning_only` | `blocked` or `warning_only` | false | true | `deadend_proximity_bounded` | deadend proximity is bounded and not global taint. |
| `conflicting_provenance_blocks_direct_reuse` | Two records with same subject/claim but incompatible provenance/conflict refs | Current reuse query | `blocked_by_conflicting_provenance` | `blocked` | false | true | `conflictcheck_advisory_root_required` | ConflictCheck remains advisory until Root. |
| `trusted_newer_provenance_can_request_supersession_review_but_not_self_authorize` | Older trusted work, newer trusted record, replacement evidence, root not yet accepted for supersession | Supersession review query | `supersession_review_required` | `partial_reuse_then_validation` | false | true | `supersession_review_required` | trusted newer provenance can request review but cannot self-authorize. |
| `audit_hash_continuity_does_not_create_truth` | Record with valid `LocalAuditLink` continuity and source artifact refs | Historical/audit review query | `audit_continuity_only` | `historical_replay` or `context_only` | false | true | `audit_hash_continuity_not_truth` | audit hash continuity is not truth. |
| `high_reuse_lineage_does_not_create_authority` | Popular lineage with high `reuse_count` and many descendants | Current direct reuse query | `review_required` or `context_only` | `partial_reuse_then_validation` or `context_only` | false unless all future hard gates pass | true | `popularity_not_authority` | reuse history and popularity do not decide. |
| `root_final_authority_preserved_across_lineage_pressure` | Composite graph: derived trace, old AcceptedEvidence, bridge, quarantine, deadend, conflict, audit links | Current high-risk reuse query | `blocked_by_lineage_pressure` or `root_review_required` | `blocked` | false | true | `root_final_authority_preserved` | all non-Root authority flags remain false and Root remains final authority. |

Required scenario behavior:

1. `trace_derived_from_trace_informs_only`
   * `lineage_informs: true`
   * `lineage_decides: false`
   * `direct_reuse_allowed: false`
   * `query_state: context_only` or `review_required`
   * reason includes `lineage_informs_only`

2. `reuse_candidate_derived_from_old_accepted_evidence_requires_review`
   * accepted evidence ancestry present
   * accepted evidence ancestry is not future action permission
   * `direct_reuse_allowed: false`
   * `root_review_required: true`
   * reason includes `accepted_evidence_ancestry_not_action_permission`

3. `bridge_traversal_across_domain_informs_only`
   * bridge traversal informs target domain
   * `bridge_transfers_authority: false`
   * `external_drs_implemented: false`
   * `direct_reuse_allowed: false`
   * reason includes `bridge_informs_only`

4. `quarantine_near_reuse_candidate_warns_or_blocks`
   * quarantine proximity detected
   * `quarantine_global_taint: false`
   * `direct_reuse_allowed: false`
   * `query_state: blocked_by_quarantine_proximity` or `warning_only`
   * reason includes `quarantine_proximity_bounded`

5. `deadend_near_reuse_candidate_warns_or_blocks`
   * deadend proximity detected
   * `deadend_global_taint: false`
   * `direct_reuse_allowed: false`
   * `query_state: blocked_by_deadend_proximity` or `warning_only`
   * reason includes `deadend_proximity_bounded`

6. `conflicting_provenance_blocks_direct_reuse`
   * conflicting provenance present
   * ConflictCheck remains advisory until Root
   * `direct_reuse_allowed: false`
   * `query_state: blocked_by_conflicting_provenance`
   * reason includes `conflictcheck_advisory_root_required`

7. `trusted_newer_provenance_can_request_supersession_review_but_not_self_authorize`
   * newer trusted provenance can request review
   * does not self-authorize supersession
   * `direct_reuse_allowed: false`
   * `root_review_required: true`
   * reason includes `supersession_review_required`

8. `audit_hash_continuity_does_not_create_truth`
   * audit hash chain continuity valid
   * `audit_hash_truth_claimed: false`
   * `direct_reuse_allowed: false`
   * `query_state: audit_continuity_only`
   * reason includes `audit_hash_continuity_not_truth`

9. `high_reuse_lineage_does_not_create_authority`
   * high `reuse_count` / popular lineage present
   * `lineage_decides: false`
   * `direct_reuse_allowed: false` unless all future gates pass
   * reason includes `popularity_not_authority`

10. `root_final_authority_preserved_across_lineage_pressure`
    * composite scenario
    * derived trace + bridge + quarantine + deadend + conflict + audit links
    * all non-Root authority flags false
    * `root_final_authority_preserved: true`
    * `direct_reuse_allowed: false`
    * reason includes `root_final_authority_preserved`

## 6. Required Helper Functions For Future Proof

Plan local pure functions:

* `build_records()`
* `build_queries()`
* `lineage_distance(record_a, record_b)`
* `bounded_lineage_candidates(records, query)`
* `quarantine_pressure(record, records, query)`
* `deadend_pressure(record, records, query)`
* `conflict_pressure(record, records, query)`
* `bridge_pressure(record, records, query)`
* `audit_continuity_pressure(record)`
* `accepted_evidence_ancestry_pressure(record)`
* `reuse_lineage_pressure(record)`
* `evaluate_lineage_pressure(record, records, query)`
* `evaluate_scenario(scenario_id)`
* `run_all_scenarios()`
* `render_report()`

Important implementation constraints for the future proof:

* Deterministic local data only.
* No filesystem state dependency.
* No network.
* No APIs.
* No Gemini.
* No external DRS.
* No real connector.
* No production persistence.
* No runtime integration.
* No schema mutation.

## 7. Required Aggregate Counters For Future Proof

Planned counters:

* `scenarios_total`
* `scenarios_passed`
* `direct_reuse_allowed_count`
* `direct_reuse_blocked_count`
* `root_review_required_count`
* `lineage_informs_count`
* `lineage_decides_count`
* `provenance_truth_claimed_count`
* `audit_hash_truth_claimed_count`
* `bridge_authority_transfer_count`
* `quarantine_global_taint_count`
* `deadend_global_taint_count`
* `conflictcheck_authority_count`
* `gt_authority_count`
* `root_final_authority_preserved_count`
* `production_drs_used_count`
* `external_drs_used_count`
* `network_used_count`
* `gemini_used_count`
* `marennya_activated_count`
* `up_activated_count`

Required PASS conditions:

* `scenarios_total == 10`
* `scenarios_passed == scenarios_total`
* `lineage_decides_count == 0`
* `provenance_truth_claimed_count == 0`
* `audit_hash_truth_claimed_count == 0`
* `bridge_authority_transfer_count == 0`
* `quarantine_global_taint_count == 0`
* `deadend_global_taint_count == 0`
* `conflictcheck_authority_count == 0`
* `gt_authority_count == 0`
* `root_final_authority_preserved_count == scenarios_total`
* `production_drs_used_count == 0`
* `external_drs_used_count == 0`
* `network_used_count == 0`
* `gemini_used_count == 0`
* `marennya_activated_count == 0`
* `up_activated_count == 0`

## 8. Required Output Of Future Proof Runner

When running:

```bash
python -m demo.run_drs_lineage_provenance_pressure_v01
```

The future output must include:

* title: HEDGEHOG OS — DRS LINEAGE / PROVENANCE PRESSURE v0.1
* compact rule
* scenario table
* aggregate counters
* authority boundary summary
* limitations
* final PASS/FAIL line

Compact rule:

```text
lineage informs
lineage does not decide
provenance does not become truth
audit/hash-chain proves continuity, not truth
accepted evidence ancestry is not future action permission
bridge traversal is not authority transfer
quarantine/deadend proximity is bounded
ConflictCheck remains advisory
GT remains advisory
Root remains final authority
```

## 9. Required Tests For Future Proof

Future test file must assert:

* `run_all_scenarios` returns structured dict
* `scenarios_total == 10`
* `scenarios_passed == scenarios_total`
* all scenario ids present
* every scenario status PASS
* `lineage_decides_count == 0`
* `provenance_truth_claimed_count == 0`
* `audit_hash_truth_claimed_count == 0`
* `bridge_authority_transfer_count == 0`
* `quarantine_global_taint_count == 0`
* `deadend_global_taint_count == 0`
* `conflictcheck_authority_count == 0`
* `gt_authority_count == 0`
* `root_final_authority_preserved_count == scenarios_total`
* production/external/network/Gemini/Marennya/UP counters all zero
* each specific scenario has expected query_state and reason code

Specific scenario assertions should include:

* `trace_derived_from_trace_informs_only` has reason `lineage_informs_only`
  and `lineage_decides` is false.
* `reuse_candidate_derived_from_old_accepted_evidence_requires_review` has
  reason `accepted_evidence_ancestry_not_action_permission`.
* `bridge_traversal_across_domain_informs_only` has
  `bridge_transfers_authority` false and reason `bridge_informs_only`.
* `quarantine_near_reuse_candidate_warns_or_blocks` has
  `quarantine_global_taint` false and reason `quarantine_proximity_bounded`.
* `deadend_near_reuse_candidate_warns_or_blocks` has `deadend_global_taint`
  false and reason `deadend_proximity_bounded`.
* `conflicting_provenance_blocks_direct_reuse` has
  `blocked_by_conflicting_provenance` and
  `conflictcheck_advisory_root_required`.
* `trusted_newer_provenance_can_request_supersession_review_but_not_self_authorize`
  has reason `supersession_review_required`.
* `audit_hash_continuity_does_not_create_truth` has
  `audit_hash_truth_claimed` false and reason
  `audit_hash_continuity_not_truth`.
* `high_reuse_lineage_does_not_create_authority` has reason
  `popularity_not_authority`.
* `root_final_authority_preserved_across_lineage_pressure` has
  `root_final_authority_preserved` true and reason
  `root_final_authority_preserved`.

## 10. Future Validation Plan

For the future proof patch, run targeted validation:

```bash
python -m demo.run_drs_lineage_provenance_pressure_v01
PYTHONPATH=. pytest -q tests/test_drs_lineage_provenance_pressure_v01_runner.py
```

Fallback if local env lacks python/pytest on PATH:

```bash
python3 -m demo.run_drs_lineage_provenance_pressure_v01
PYTHONPATH=. .venv/bin/python -m pytest -q tests/test_drs_lineage_provenance_pressure_v01_runner.py
```

Static checks:

```bash
git status --short --untracked-files=all
git diff --stat
git diff --check
git diff --name-only
```

Do not run full pytest for patch plan. For the later proof patch, targeted
tests are enough initially; full pytest is required before closing any layer
that changes runtime/schema/contract/hardening. If the proof is demo/test-only
and does not touch runtime/schema/contracts, full pytest may be deferred to
audit/docs closure by explicit review.

## 11. Non-goals

* no production DRS
* no external/global DRS
* no real connector trust
* no network
* no Gemini
* no Marennya
* no UP
* no Negative Trace
* no auto-governance
* no manifest hardening
* no transition matrix mutation
* no installed Needle
* no production persistence
* no broad schema rewrite
* no runtime lineage engine
* no schema patch
* no full pytest run in patch plan
* no proof runner in patch plan
