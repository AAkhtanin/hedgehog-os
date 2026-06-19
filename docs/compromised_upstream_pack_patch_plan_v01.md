# Compromised Upstream Pack v0.1 — Patch Plan

## 1. Status

* patch_plan_id: compromised_upstream_pack_patch_plan_v01
* patch_plan_status: COMPLETE
* preflight_commit: 2ec1266
* previous_checkpoint_commit: 9b70726
* roadmap_track: Compromised Upstream / Economic Adversary / DRS poisoning-adversarial maturity
* selected_split_option: Option B
* selected_layer: Compromised Upstream Pack v0.1
* later_layer_1: DRS Poisoning Resistance v0.1
* later_layer_2: Economic Adversary Pack v0.1
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
* negative_trace_implemented: false
* auto_governance_implemented: false
* manifest_hardening_implemented: false
* transition_matrix_mutated: false

## 2. Scope

This patch plan defines a future local deterministic proof runner for
compromised upstream source pressure only.

It does not implement:

* production connectors
* production DRS
* external/global DRS
* DRS poisoning resistance proof
* economic adversary proof
* Negative Trace governance
* manifest hardening
* transition matrix mutation
* auto-governance
* Marennya
* UP

## 3. Why Split The Track

The read-only preflight selected Option B because source compromise, DRS
poisoning, and economic/governance pressure are distinct adversarial
pressures.

This first patch plan focuses only on upstream source compromise and trust
laundering through source/evidence/pointer surfaces. It keeps DRS poisoning,
quarantine flood economics, fake repeated negative traces, manifest hardening,
transition matrix mutation, and auto-governance outside this first layer.

The split keeps the proof small enough to audit:

* Compromised Upstream Pack v0.1: source compromise, signed-looking stale
  sources, warehouse contradiction, external pointer trust laundering,
  candidate/evidence boundaries, and Root final authority.
* DRS Poisoning Resistance v0.1: later memory/reuse/quarantine poisoning
  pressure.
* Economic Adversary Pack v0.1: later repeated fake negative traces, fake
  success pressure, governance pressure, and DoS/economic pressure.

## 4. Future Files Planned

Future proof files:

* `demo/run_compromised_upstream_pack_v01.py`
* `tests/test_compromised_upstream_pack_v01_runner.py`

No other files should be created or modified in the future proof patch unless
explicitly approved later.

## 5. Local Proof Model

The future proof should use local proof-only dataclasses or structured
dictionaries. It should not depend on production connectors, filesystem state,
network calls, APIs, Gemini, external DRS, production persistence, or a
production connector sandbox.

Required local concepts:

* `LocalUpstreamObservation`
* `LocalEvidenceCandidate`
* `LocalValidationPacket`
* `LocalAcceptedEvidence`
* `LocalExternalPointer`
* `LocalConflictSignal`
* `LocalRootDecision`
* `UpstreamPressureResult`
* `ScenarioResult`

Planned fields:

`LocalUpstreamObservation`:

* `observation_id`
* `source_kind`
* `source_id`
* `source_trust_hint`
* `domain`
* `subject_key`
* `claim_key`
* `claim_value`
* `observed_at`
* `reported_at`
* `freshness_state`
* `signature_state`
* `contradiction_refs`
* `pointer_refs`
* `schema_valid`
* `compromised_signal`
* `economic_incentive`
* `source_truth_claimed`

`LocalEvidenceCandidate`:

* `candidate_id`
* `observation_id`
* `evidence_kind`
* `summary`
* `confidence`
* `validation_refs`
* `root_accepted`
* `action_permission_claimed`
* `truth_claimed`

`LocalValidationPacket`:

* `packet_id`
* `candidate_id`
* `schema_valid`
* `freshness_valid`
* `signature_valid`
* `conflict_detected`
* `pointer_trust_laundering_detected`
* `validation_accepts_as_truth`
* `root_required`

`LocalAcceptedEvidence`:

* `accepted_evidence_id`
* `candidate_id`
* `root_decision_id`
* `bounded_scope`
* `future_action_permission`
* `direct_reuse_permission`

`LocalExternalPointer`:

* `pointer_id`
* `pointer_kind`
* `target_domain`
* `trust_claim`
* `repeated_reference_count`
* `accepted_as_trust`

`LocalConflictSignal`:

* `conflict_id`
* `subject_key`
* `claim_key`
* `conflict_kind`
* `advisory_only`
* `blocks_direct_ready`

`LocalRootDecision`:

* `decision_id`
* `scenario_id`
* `final_status`
* `root_final_authority_preserved`
* `direct_reuse_allowed`
* `action_permission_granted`
* `reason_codes`

`UpstreamPressureResult`:

* `scenario_id`
* `status`
* `query_state`
* `direct_ready_allowed`
* `direct_reuse_allowed`
* `action_permission_granted`
* `source_truth_claimed`
* `schema_validity_truth_claimed`
* `signed_source_truth_claimed`
* `pointer_trust_claimed`
* `evidence_candidate_authority_claimed`
* `validation_packet_authority_claimed`
* `accepted_evidence_action_permission_claimed`
* `conflictcheck_advisory_only`
* `gt_advisory_only`
* `root_final_authority_preserved`
* `production_connector_used`
* `external_drs_used`
* `network_used`
* `gemini_used`
* `reason_codes`

## 6. Required Scenarios

The future proof should implement exactly these 6 scenarios:

1. `compromised_bank_source_cannot_create_truth`
2. `stale_legal_source_signed_looking_forces_review`
3. `warehouse_source_contradiction_blocks_ready`
4. `external_pointer_trust_laundering_rejected`
5. `accepted_evidence_from_compromised_source_is_not_action_permission`
6. `root_final_authority_preserved_under_compromised_upstream_pressure`

For each scenario, the future proof should define attacker input / upstream
pressure, local observation, validation packet behavior, expected
`query_state`, expected `final_status`, expected `direct_ready_allowed`,
expected `direct_reuse_allowed`, expected `action_permission_granted`,
expected `reason_codes`, and the authority invariant tested.

### 1. compromised_bank_source_cannot_create_truth

Attacker pressure:

Known bank-like source claims payment truth and tries to mark readiness.

Expected:

* `source_truth_claimed: false`
* `direct_ready_allowed: false`
* `action_permission_granted: false`
* `root_final_authority_preserved: true`
* reason includes `compromised_source_not_truth`

Authority invariant tested:

* compromised upstream source is not truth
* schema-valid upstream content is not semantic truth
* Root remains final authority

### 2. stale_legal_source_signed_looking_forces_review

Attacker pressure:

Legal registry-like source is signed-looking but stale.

Expected:

* `signed_source_truth_claimed: false`
* `query_state: stale_source_review_required`
* `direct_ready_allowed: false`
* `action_permission_granted: false`
* reason includes `stale_signed_source_requires_review`

Authority invariant tested:

* signed-looking source is not truth
* ValidationPacket is not Root acceptance
* Root remains final authority

### 3. warehouse_source_contradiction_blocks_ready

Attacker pressure:

Warehouse source claims ready while known stock/world-state evidence says
shortage/not_ready.

Expected:

* `conflict_detected: true`
* `direct_ready_allowed: false`
* `final_status: not_ready`
* ConflictCheck remains advisory until Root
* reason includes `conflicting_warehouse_provenance_blocks_ready`

Authority invariant tested:

* ConflictCheck remains advisory until Root
* schema-valid upstream content is not semantic truth
* Root remains final authority

### 4. external_pointer_trust_laundering_rejected

Attacker pressure:

External pointer repeats trust claims and tries to become trusted evidence or
external/global DRS.

Expected:

* `pointer_trust_claimed: false`
* `external_drs_used: false`
* `direct_reuse_allowed: false`
* `action_permission_granted: false`
* reason includes `external_pointer_trust_laundering_rejected`

Authority invariant tested:

* external pointer is not trust
* external/global DRS is not implemented
* Root remains final authority

### 5. accepted_evidence_from_compromised_source_is_not_action_permission

Attacker pressure:

Evidence candidate from compromised upstream tries to become AcceptedEvidence
and action permission.

Expected:

* EvidenceCandidate remains candidate-only unless Root accepts
* even if Root creates bounded AcceptedEvidence, `future_action_permission: false`
* `accepted_evidence_action_permission_claimed: false`
* `action_permission_granted: false`
* reason includes `accepted_evidence_not_action_permission`

Authority invariant tested:

* EvidenceCandidate is candidate-only before Root
* AcceptedEvidence is bounded evidence, not future action permission
* Root remains final authority

### 6. root_final_authority_preserved_under_compromised_upstream_pressure

Composite:

Compromised bank source + stale signed-looking legal source + warehouse
contradiction + external pointer laundering + candidate pressure.

Expected:

* all non-Root authority flags false
* `direct_ready_allowed: false`
* `direct_reuse_allowed: false`
* `action_permission_granted: false`
* `root_final_authority_preserved: true`
* reason includes `root_final_authority_preserved_under_compromised_upstream_pressure`

Authority invariant tested:

* compromised upstream source is not truth
* signed-looking source is not truth
* external pointer is not trust
* Root remains final authority

## 7. Required Helper Functions For Future Proof

Plan pure local functions:

* `build_upstream_observations()`
* `build_evidence_candidates()`
* `build_external_pointers()`
* `build_validation_packets()`
* `validate_freshness(observation)`
* `validate_signature_state(observation)`
* `detect_source_compromise(observation)`
* `detect_conflict(observation, observations)`
* `detect_pointer_trust_laundering(pointer)`
* `evaluate_evidence_candidate(candidate, observation, validation_packet)`
* `root_review(scenario_id, pressure_result)`
* `evaluate_scenario(scenario_id)`
* `run_all_scenarios()`
* `render_report()`
* `main()`

Important:

The future proof must be deterministic, local, standard-library only, and not
depend on filesystem state, network, APIs, Gemini, external DRS, real
connector, production persistence, or production connector sandbox.

## 8. Required Aggregate Counters For Future Proof

Plan counters:

* `scenarios_total`
* `scenarios_passed`
* `direct_ready_allowed_count`
* `direct_reuse_allowed_count`
* `action_permission_granted_count`
* `source_truth_claimed_count`
* `schema_validity_truth_claimed_count`
* `signed_source_truth_claimed_count`
* `pointer_trust_claimed_count`
* `evidence_candidate_authority_claimed_count`
* `validation_packet_authority_claimed_count`
* `accepted_evidence_action_permission_claimed_count`
* `conflictcheck_authority_count`
* `gt_authority_count`
* `root_final_authority_preserved_count`
* `production_connector_used_count`
* `production_drs_used_count`
* `external_drs_used_count`
* `network_used_count`
* `gemini_used_count`
* `negative_trace_implemented_count`
* `auto_governance_implemented_count`
* `manifest_hardening_implemented_count`
* `transition_matrix_mutated_count`
* `marennya_activated_count`
* `up_activated_count`

Required PASS conditions:

* `scenarios_total == 6`
* `scenarios_passed == scenarios_total`
* `direct_ready_allowed_count == 0`
* `direct_reuse_allowed_count == 0`
* `action_permission_granted_count == 0`
* `source_truth_claimed_count == 0`
* `schema_validity_truth_claimed_count == 0`
* `signed_source_truth_claimed_count == 0`
* `pointer_trust_claimed_count == 0`
* `evidence_candidate_authority_claimed_count == 0`
* `validation_packet_authority_claimed_count == 0`
* `accepted_evidence_action_permission_claimed_count == 0`
* `conflictcheck_authority_count == 0`
* `gt_authority_count == 0`
* `root_final_authority_preserved_count == scenarios_total`
* `production_connector_used_count == 0`
* `production_drs_used_count == 0`
* `external_drs_used_count == 0`
* `network_used_count == 0`
* `gemini_used_count == 0`
* `negative_trace_implemented_count == 0`
* `auto_governance_implemented_count == 0`
* `manifest_hardening_implemented_count == 0`
* `transition_matrix_mutated_count == 0`
* `marennya_activated_count == 0`
* `up_activated_count == 0`

## 9. Required Output Of Future Proof Runner

When running:

```bash
python -m demo.run_compromised_upstream_pack_v01
```

Output must include:

* title: `HEDGEHOG OS — COMPROMISED UPSTREAM PACK v0.1`
* compact rule
* scenario table
* aggregate counters
* authority boundary summary
* limitations
* final PASS/FAIL line

Compact rule:

```text
compromised upstream source is not truth
signed-looking source is not truth
external pointer is not trust
schema-valid upstream content is not semantic truth
ValidationPacket is not Root acceptance
EvidenceCandidate is candidate-only before Root
AcceptedEvidence is bounded evidence, not future action permission
ConflictCheck remains advisory
GT remains advisory
Root remains final authority
```

## 10. Required Focused Tests For Future Proof

Future test file must assert:

* `run_all_scenarios` returns structured dict
* `scenarios_total == 6`
* `scenarios_passed == scenarios_total`
* all scenario ids present
* every scenario status PASS
* `direct_ready_allowed_count == 0`
* `direct_reuse_allowed_count == 0`
* `action_permission_granted_count == 0`
* `source_truth_claimed_count == 0`
* `schema_validity_truth_claimed_count == 0`
* `signed_source_truth_claimed_count == 0`
* `pointer_trust_claimed_count == 0`
* `evidence_candidate_authority_claimed_count == 0`
* `validation_packet_authority_claimed_count == 0`
* `accepted_evidence_action_permission_claimed_count == 0`
* `conflictcheck_authority_count == 0`
* `gt_authority_count == 0`
* `root_final_authority_preserved_count == scenarios_total`
* production/external/network/Gemini/NegativeTrace/auto-governance/manifest-hardening/transition-matrix/Marennya/UP counters all zero
* each specific scenario has expected final_status/query_state and reason code

Specific scenario assertions:

* `compromised_bank_source_cannot_create_truth` has reason `compromised_source_not_truth`
* `stale_legal_source_signed_looking_forces_review` has reason `stale_signed_source_requires_review`
* `warehouse_source_contradiction_blocks_ready` has reason `conflicting_warehouse_provenance_blocks_ready`
* `external_pointer_trust_laundering_rejected` has reason `external_pointer_trust_laundering_rejected`
* `accepted_evidence_from_compromised_source_is_not_action_permission` has reason `accepted_evidence_not_action_permission`
* `root_final_authority_preserved_under_compromised_upstream_pressure` has reason `root_final_authority_preserved_under_compromised_upstream_pressure`

## 11. Future Validation Plan

For the future proof patch, run targeted validation:

```bash
python -m demo.run_compromised_upstream_pack_v01

PYTHONPATH=. pytest -q tests/test_compromised_upstream_pack_v01_runner.py
```

Fallback if local env lacks python/pytest on PATH:

```bash
python3 -m demo.run_compromised_upstream_pack_v01

PYTHONPATH=. .venv/bin/python -m pytest -q tests/test_compromised_upstream_pack_v01_runner.py
```

Static checks:

```bash
git status --short --untracked-files=all
git diff --stat
git diff --check
git diff --name-only
```

Do not run full pytest for patch plan.

For the later proof patch, targeted tests are enough initially because the
proof is demo/test-only and does not touch runtime/schema/contracts. Full
pytest is required before closing any future runtime/schema/contract/hardening
layer.

## 12. Non-goals

* no production DRS
* no external/global DRS
* no real connector trust
* no production connector sandbox
* no network
* no Gemini
* no Marennya
* no UP
* no Negative Trace implementation
* no DRS poisoning proof in this first layer
* no economic adversary proof in this first layer
* no auto-governance
* no manifest hardening implementation
* no transition matrix mutation
* no installed Needle
* no production persistence
* no runtime integration
* no schema patch
* no full pytest run in patch plan
* no proof runner in patch plan
