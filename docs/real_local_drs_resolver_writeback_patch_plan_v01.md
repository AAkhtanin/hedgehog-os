# Real Local DRS Resolver / Writeback v0.1 — Patch Plan

## 1. Current Checkpoint

* patch_plan_id: real_local_drs_resolver_writeback_patch_plan_v01
* patch_plan_status: COMPLETE
* current_head_before_patch: 55ab2cd
* preflight_commit: 55ab2cd
* runtime_gate_commit: 1e1afe6
* starts Real Semantic Runtime MVP
* follows STOP PROOF-ONLY EXPANSION GATE
* runtime_implemented: false
* proof_runner_created: false
* tests_created: false
* schemas_modified: false
* demos_modified: false
* full_pytest_run: false

This patch plan defines the exact future implementation boundary for the first
runtime-facing local DRS layer. It does not implement runtime, proof runner,
tests, schemas, audit log, or walkthrough.

The future implementation must create the bounded local semantic runtime
primitive:

```text
write meaning
resolve meaning
reuse under Root review
```

## 2. Source Review Summary

Reviewed sources for this plan:

* `docs/real_local_drs_resolver_writeback_preflight_v01.md`
* `hedgehog/drs.py`
* `hedgehog/reuse_gate.py`
* `hedgehog/time_model.py`
* `schemas/drs_record.schema.json`
* `tests/test_drs_runtime.py`
* `demo/run_drs_writeback_from_root_final.py`
* `demo/run_applied_drs_retrieval_reuse.py`
* `demo/run_long_lived_drs_ttl_aging_stress_v01.py`
* `demo/run_drs_lineage_provenance_pressure_v01.py`
* `demo/run_compromised_upstream_pack_v01.py`

Observed basis:

* `LocalDRS` already provides local file-backed record writes, reads, layer
  separation, required field checks, TimeEnvelope requirement, pointer shape
  checks, sensitive-key rejection, and duplicate record id protection.
* `reuse_gate.py` already provides deterministic advisory scoring helpers.
  Its reuse result remains candidate-oriented and does not produce final reuse.
* `time_model.py` already provides local TimeEnvelope and TemporalQuery helpers.
* `drs_record.schema.json` already supports the v0.1 stored-record shape with
  `content`, `time_envelope`, `provenance`, `trace_refs`, `source_refs`, hash
  fields, GT metadata, and validation metadata.
* Existing proofs already establish Root Final writeback filtering, candidate
  reuse boundaries, TTL/stale review pressure, lineage/provenance pressure,
  quarantine/deadend bounds, conflicting provenance handling, and compromised
  upstream guardrails.

## 3. Implementation Decision

Future implementation should add:

* `hedgehog/local_drs_resolver.py`

This module should compose:

* `LocalDRS` from `hedgehog/drs.py`
* `make_time_envelope` and temporal query helpers from `hedgehog/time_model.py`
* existing advisory reuse logic from `hedgehog/reuse_gate.py` where useful

The future module must not make ReuseScore, GT, DRS, freshness, provenance, or
source frequency authoritative. It should convert local records into structured
candidate reports and Root-review-required outcomes.

Implementation constraints:

* Do not modify `hedgehog/drs.py` unless a tiny helper is unavoidable.
* Do not use `hedgehog/external_drs/*`.
* Do not implement external/global DRS.
* Do not modify schemas for v0.1 unless implementation discovers a hard blocker
  and a separate schema patch plan is approved first.

## 4. Future Allowed Implementation Files

Future implementation should be limited to:

* `hedgehog/local_drs_resolver.py`
* `demo/run_real_local_drs_resolver_writeback_v01.py`
* `tests/test_real_local_drs_resolver_writeback_v01_runner.py`

No other files are planned for the implementation patch. If the implementation
finds an unavoidable need for another file, that must be justified before code
is changed.

The demo runner should prove the runtime primitive locally and deterministically
over temporary/local DRS paths. The focused test should verify the module API,
scenario report, counters, and existing `LocalDRS` compatibility.

## 5. Runtime Primitive API Sketch

The future runtime-facing module should define local dataclasses or equivalent
structured objects. Names and exact fields can be adjusted in implementation if
tests preserve the same behavioral contract.

### SemanticDRSRecordInput

Conceptual fields:

* record_id
* layer
* record_type
* domain
* content
* semantic_keys
* source_refs
* trace_refs
* provenance
* time_envelope
* status
* gt
* validation
* root_final_ref
* worldstate_ref
* poisoning_markers

### SemanticResolveQuery

Conceptual fields:

* query_id
* domain
* semantic_terms
* content_filters
* temporal_query
* worldstate
* source_refs
* trace_refs
* max_candidates
* require_root_review
* risk_class

### ResolvedDRSCandidate

Conceptual fields:

* candidate_id
* record_id
* domain
* match_score
* match_reasons
* review_required
* blocked
* direct_reuse_allowed
* action_permission_granted
* stale
* quarantine_pressure
* deadend_pressure
* conflicting_provenance
* changed_worldstate
* poisoning_pressure
* reason_codes

### ResolvedDRSReport

Conceptual fields:

* query_id
* candidates
* candidate_count
* root_review_required
* direct_reuse_allowed_count
* blocked_count
* review_required_count
* authority_boundary
* counters
* reason_codes

### Required functions

* `write_semantic_record(...)`
* `resolve_semantic_candidates(...)`
* `write_root_final_record(...)`

Required behavior:

* write DRS record using existing DRSRecord shape
* preserve domain, content, time envelope, provenance, trace refs, source refs
* resolve candidates deterministically by domain + semantic query/context
* return candidates only
* attach reason codes
* mark stale/quarantine/deadend/conflict/poisoning pressure as review-required or blocked
* never return action permission
* never create final output
* never bypass Root

## 6. Semantic Matching v0.1

Semantic matching for v0.1 must be deterministic only.

Allowed:

* exact domain match
* explicit content key match
* token-set overlap over controlled fields
* source_refs / trace_refs / provenance comparison
* status and TimeEnvelope checks

Not allowed:

* LLM semantic matching
* embeddings
* network lookup
* external/global DRS lookup
* probabilistic authority claims

Suggested scoring is bounded and explanatory only:

* domain match: hard filter
* explicit content key match: positive reason
* token-set overlap over selected text fields: advisory match reason
* source/trace/provenance overlap: advisory context reason
* stale/quarantine/deadend/conflict/poisoning markers: review or block reason

## 7. Writeback Rules

Future writeback must:

* write only local DRS records
* use temporary/local test paths in tests
* record Root-reviewed semantic outcomes only
* record RootFinal-derived writeback without action side effects
* reject raw upstream claims as writeback authority
* reject production persistence claims
* reject connector/action claims
* not mutate manifest
* not mutate transition matrix

`write_root_final_record(...)` should accept only a Root-reviewed semantic
outcome or RootFinal-derived artifact shape. It must reject raw connector
observations, raw ValidationPacket-like objects, raw EvidenceCandidate-like
objects, raw ResultProposal-like objects, and any object claiming direct action
execution, connector side effects, production persistence, external/global DRS
write, or Root bypass.

## 8. Resolve / Reuse Rules

Future resolver must:

* return reuse candidates, not reuse permission
* require Root review before reuse affects final output
* force review for stale records
* force review/block for quarantine/deadend proximity
* block direct reuse when WorldState changed
* block direct reuse on conflicting provenance
* block direct reuse under poisoning pressure
* preserve `direct_reuse_allowed_count: 0` for v0.1

The resolver may rank candidates and explain why they were returned. It may not
authorize final reuse, create FinalOutput, execute an action, write production
Work, or bypass Root review.

## 9. Required Invariants

The future implementation and proof must preserve:

* DRS record is not truth
* DRS hit is not authority
* DRS reuse candidate is not action permission
* DRS freshness is advisory, not final authority
* stale DRS record cannot silently reuse
* quarantined/deadend proximity forces review
* conflicting provenance blocks direct ready/reuse
* Root remains final authority
* resolver cannot mutate manifest
* resolver cannot mutate transition matrix
* resolver cannot call network/Gemini/connectors
* writeback cannot create production persistence claims
* local file-backed DRS is still not production DRS

## 10. DRS Poisoning Acceptance Criteria

Because this begins real write/resolve/reuse behavior, the future proof must
include minimum poisoning guardrails:

* duplicate/spam records cannot become authority
* duplicate/spam records can at most create review pressure
* compromised/stale/upstream-looking records cannot become truth
* repeated external pointer cannot become trust
* schema-valid DRS record cannot become semantic truth
* accepted historical evidence cannot become future action permission
* poisoning pressure can force Root review/quarantine, not reuse

This is not separate DRS Poisoning Resistance v0.1. This is acceptance criteria
for Real Local DRS Resolver / Writeback v0.1.

## 11. Future Proof Scenarios

The future deterministic proof runner must implement exactly these scenarios:

1. `write_then_resolve_semantic_record_candidate_only`
2. `stale_record_forces_root_review`
3. `quarantine_proximity_blocks_direct_reuse`
4. `changed_worldstate_blocks_old_reuse`
5. `conflicting_provenance_blocks_reuse`
6. `duplicate_poisoning_pressure_does_not_create_authority`
7. `root_review_required_before_reuse_affects_final_output`
8. `writeback_records_root_final_without_action_side_effects`

Expected scenario intent:

| Scenario | Expected behavior | Required reason emphasis |
| --- | --- | --- |
| `write_then_resolve_semantic_record_candidate_only` | Local semantic record is written, resolved, and returned as candidate only. | `candidate_only_root_review_required` |
| `stale_record_forces_root_review` | Stale candidate is visible but direct reuse is blocked. | `stale_record_forces_root_review` |
| `quarantine_proximity_blocks_direct_reuse` | Quarantine/deadend pressure blocks direct reuse and requires Root review. | `quarantine_proximity_blocks_direct_reuse` |
| `changed_worldstate_blocks_old_reuse` | Candidate from old compatible world state is blocked when current WorldState changes. | `changed_worldstate_blocks_old_reuse` |
| `conflicting_provenance_blocks_reuse` | Conflicting provenance blocks direct reuse and remains advisory until Root. | `conflicting_provenance_blocks_reuse` |
| `duplicate_poisoning_pressure_does_not_create_authority` | Duplicate/spam records increase review pressure only; no authority is created. | `duplicate_poisoning_pressure_does_not_create_authority` |
| `root_review_required_before_reuse_affects_final_output` | Candidate cannot affect final output before Root review. | `root_review_required_before_reuse_affects_final_output` |
| `writeback_records_root_final_without_action_side_effects` | RootFinal-derived local writeback records outcome without connector/action side effects. | `writeback_without_action_side_effects` |

## 12. Future Counters

The future proof report must include:

* records_written_count
* resolve_queries_count
* candidates_returned_count
* direct_reuse_allowed_count: 0
* root_review_required_count
* stale_record_reuse_blocked_count
* quarantine_reuse_blocked_count
* changed_worldstate_reuse_blocked_count
* conflicting_provenance_blocked_count
* duplicate_poisoning_records_seen_count
* poisoning_pressure_authority_claimed_count: 0
* action_permission_granted_count: 0
* manifest_mutation_count: 0
* transition_matrix_mutation_count: 0
* production_drs_used_count: 0
* external_drs_used_count: 0
* network_used_count: 0
* gemini_used_count: 0
* root_final_authority_preserved_count

Required PASS conditions:

* scenario count equals 8.
* every scenario status is PASS.
* records_written_count is greater than 0.
* resolve_queries_count is greater than 0.
* candidates_returned_count is greater than 0.
* direct_reuse_allowed_count == 0.
* root_review_required_count is greater than 0.
* stale_record_reuse_blocked_count is greater than 0.
* quarantine_reuse_blocked_count is greater than 0.
* changed_worldstate_reuse_blocked_count is greater than 0.
* conflicting_provenance_blocked_count is greater than 0.
* duplicate_poisoning_records_seen_count is greater than 0.
* poisoning_pressure_authority_claimed_count == 0.
* action_permission_granted_count == 0.
* manifest_mutation_count == 0.
* transition_matrix_mutation_count == 0.
* production_drs_used_count == 0.
* external_drs_used_count == 0.
* network_used_count == 0.
* gemini_used_count == 0.
* root_final_authority_preserved_count equals scenario count.

## 13. Future Validation Commands

After implementation, run targeted validation:

```bash
python3 -m demo.run_real_local_drs_resolver_writeback_v01

PYTHONPATH=. .venv/bin/python -m pytest -q \
  tests/test_real_local_drs_resolver_writeback_v01_runner.py \
  tests/test_drs_runtime.py
```

Then run static checks:

```bash
git status --short --untracked-files=all
git diff --stat
git diff --check
git diff --name-only
```

Because the future patch touches runtime code, full pytest should be required
before closure/docs sync. Full pytest is not required during this patch-plan
step.

## 14. Non-goals

* no production DRS
* no external/global DRS
* no network
* no Gemini
* no autonomous action
* no connector side effects
* no public WOW
* no whitepaper/public auditor packet
* no Marennya/UP
* no self-modifying manifest
* no transition matrix mutation
* no DRS Poisoning Resistance v0.1 as separate layer
* no Economic Adversary v0.1

## 15. Recommended Next Step

Real Local DRS Resolver / Writeback v0.1 IMPLEMENTATION
