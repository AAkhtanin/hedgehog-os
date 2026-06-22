# CandidateVectorGenerator + Real AVF Scoring v0.1 — Patch Plan

## 1. Current checkpoint

* patch_plan_id: candidate_vector_generator_avf_scoring_patch_plan_v01
* patch_plan_status: COMPLETE
* preflight_commit: 97a1437
* previous_runtime_checkpoint: 4f513d1
* runtime_gate_commit: 1e1afe6
* roadmap_block: Real Semantic Runtime MVP
* layer_type: runtime_facing_patch_plan
* implementation_started: false
* runtime_modified: false
* schemas_modified: false
* tests_created: false
* demos_created: false
* full_pytest_run: false

This patch plan defines the future implementation boundary only. It does not
implement runtime, create a proof runner, create tests, modify schemas, create
audit logs, create a human walkthrough, run full pytest, or close the layer.

## 2. Purpose

This patch plan defines the future implementation of a small runtime-facing
adapter/generator that converts resolved local DRS candidates into bounded
candidate vectors and deterministic AVF scores.

The bridge is:

```text
Real Local DRS Resolver candidates
-> bounded CandidateVectors
-> deterministic AVF scores
-> ranked/reviewable candidate report
-> GT/LGT/Root still required
```

The layer does not make AVF authoritative. It creates ranking/review signals
only.

Core rule:

* Candidate vector is not truth.
* AVF score is not authority.
* Top-ranked candidate is not action permission.
* DRS hit is not authority.
* Root remains final authority.

## 3. Implementation decision

Future implementation should add:

* `hedgehog/candidate_vector_generator.py`

This is the preferred seam from the read-only preflight. It should sit beside
the existing `hedgehog/candidate_vectors.py` loader and compose existing
runtime helpers rather than replacing them.

It should compose:

* existing `hedgehog/local_drs_resolver.py`
* existing `hedgehog/candidate_vectors.py`
* existing `hedgehog/avf.py`
* existing `hedgehog/reuse_gate.py` only as advisory scoring/support
* existing `hedgehog/time_model.py`

Do not replace:

* `hedgehog/avf.py`
* `hedgehog/candidate_vectors.py`
* `hedgehog/local_drs_resolver.py`

Do not create a separate DRS store. Do not use external/global DRS. Do not use
network/Gemini/LLM/embeddings.

Reasoning: `candidate_vectors.py` is already a needle-vector loader;
`avf.py` already performs deterministic scoring and hard/soft masking;
`local_drs_resolver.py` already returns local DRS candidates with review and
boundary reason codes. The missing seam is a narrow adapter that turns resolved
DRS candidates into AVF-compatible candidate vectors plus a sidecar report that
preserves review, poison, conflict, stale, and Root boundary metadata.

## 4. Future allowed implementation files

Future implementation should be limited to:

* `hedgehog/candidate_vector_generator.py`
* `demo/run_candidate_vector_generator_avf_scoring_v01.py`
* `tests/test_candidate_vector_generator_avf_scoring_v01_runner.py`

No schema changes are expected for v0.1. If implementation discovers a hard
schema blocker, the schema change must be deferred and require a separate
schema patch plan.

## 5. Runtime API sketch

The future module should define local dataclasses or equivalent structured
objects. Exact field names may be adjusted during implementation if tests
preserve the same behavioral contract.

Expected concepts:

* `CandidateVectorInput`
* `GeneratedCandidateVector`
* `CandidateVectorScore`
* `CandidateVectorReport`
* `generate_candidate_vectors(...)`
* `score_candidate_vector(...)`
* `rank_candidate_vectors(...)`
* `build_avf_candidate_report(...)`

`CandidateVectorInput` should preserve:

* resolved_candidate_id
* source_record_id
* domain
* subject_key
* claim_key
* content_summary
* semantic_tokens
* time_envelope / freshness state
* provenance refs
* trace refs
* source refs
* conflict flags
* quarantine/deadend flags
* poisoning flags
* root_review_required
* direct_reuse_allowed: false

`GeneratedCandidateVector` should preserve:

* vector_id
* candidate_id
* vector_features
* forbidden_or_masked_features
* advisory_only: true
* truth_claimed: false
* authority_claimed: false
* action_permission_claimed: false

The generated vector may wrap or serialize existing `hedgehog.models.CandidateVector`
for compatibility with `hedgehog.avf.score_candidate_vector(...)`.

`CandidateVectorScore` should preserve:

* score
* score_components
* penalties
* hard_blocks
* review_required
* score_is_authority: false

`CandidateVectorReport` should preserve:

* candidates
* ranked_candidates
* top_candidate_ids
* review_required_count
* blocked_count
* direct_reuse_allowed_count: 0
* root_review_required: true
* root_final_authority_preserved: true

## 6. Deterministic matching / vector generation v0.1

Allowed vector features:

* exact domain match
* subject_key match
* claim_key match
* controlled token overlap
* freshness / TTL advisory status
* provenance quality advisory status
* source_refs overlap
* trace_refs overlap
* conflict flags
* quarantine/deadend flags
* duplicate/spam/poisoning pressure flags
* schema-validity as shape-only

Not allowed:

* LLM semantic matching
* embeddings
* network lookup
* external/global DRS lookup
* source popularity as authority
* schema-validity as semantic truth
* AVF score as final decision
* score threshold creating action permission
* score threshold creating direct reuse permission

Generation should consume `ResolvedDRSCandidate`/`ResolvedDRSReport` outputs
from the real local resolver where possible. It must not duplicate resolver
logic or re-query external/global sources.

## 7. AVF scoring rules

Future AVF scoring must be deterministic.

Required score components:

* domain_match_score
* subject_claim_match_score
* token_overlap_score
* freshness_score
* provenance_quality_score
* trace_source_overlap_score
* conflict_penalty
* quarantine_deadend_penalty
* poisoning_pressure_penalty
* root_review_requirement_flag

Required hard blocks:

* quarantine/deadend direct reuse block
* conflicting provenance direct reuse block
* stale direct reuse block
* poisoning pressure direct reuse block
* unsafe forbidden vector mask

AVF score may:

* rank candidates
* explain review priority
* suggest routing to GT/LGT/Root review

AVF score must not:

* decide truth
* grant action permission
* create FinalOutput
* bypass Root
* mutate manifest
* mutate transition matrix
* call network/Gemini/connectors

## 8. Integration with Real Local DRS Resolver

The future proof should compose the current runtime resolver:

1. Write a small set of local semantic DRS records.
2. Resolve local candidates with `resolve_semantic_candidates(...)`.
3. Feed resolved candidates into CandidateVectorGenerator.
4. Score/rank them with AVF.
5. Verify every ranked output remains candidate-only.
6. Verify Root/GT/LGT review remains required.

Do not duplicate the DRS resolver logic. Do not use external/global DRS. Do
not allow AVF to directly write back final output.

## 9. Required invariants

Future implementation, proof, and tests must preserve:

* Candidate vector is not truth
* Candidate vector is not authority
* AVF score is not authority
* Top-ranked candidate is not action permission
* Top-ranked candidate is not direct reuse permission
* DRS hit is not authority
* DRS reuse candidate is not action permission
* AVF ranking can influence review/routing only
* stale candidate cannot silently win
* quarantine/deadend candidate cannot become direct reuse
* conflicting provenance blocks or forces review
* duplicate/spam candidates cannot become authority by volume
* schema-valid candidate vector is not semantic truth
* GT/LGT remains advisory
* Root remains final authority
* CandidateVectorGenerator cannot mutate manifest
* CandidateVectorGenerator cannot mutate transition matrix
* CandidateVectorGenerator cannot call network/Gemini/connectors

## 10. Poisoning/adversarial acceptance criteria

Because this layer starts scoring/ranking candidates, the future proof must
include these guardrails:

* duplicate candidates cannot win by count alone
* spam candidates can at most create review pressure
* compromised upstream-looking records cannot become truth
* repeated external pointer cannot become trust
* stale but high-overlap record cannot silently outrank fresh review
* high AVF score cannot override quarantine/deadend/conflict
* high AVF score cannot create direct reuse permission
* high AVF score cannot create action permission
* high AVF score cannot create RootFinal output

This is not separate DRS Poisoning Resistance v0.1. This is acceptance
criteria for CandidateVectorGenerator + Real AVF Scoring v0.1.

## 11. Future proof scenarios

The future proof runner must implement these exact scenarios.

1. `drs_resolved_candidates_generate_candidate_vectors`
   * input setup: write one clean local semantic DRS record, resolve it through `resolve_semantic_candidates(...)`, and feed the returned candidate into the generator.
   * expected candidate vector count: 1.
   * expected score/ranking behavior: one generated `local_drs` vector with deterministic AVF score.
   * expected review/block flags: Root review required, not blocked.
   * expected reason codes: `drs_candidate_vector_generated`, `candidate_only_root_review_required`.
   * authority invariant tested: Candidate vector is not truth.

2. `exact_domain_and_claim_match_scores_higher_but_not_authority`
   * input setup: resolve one exact domain/subject/claim candidate and one lower-overlap candidate.
   * expected candidate vector count: 2.
   * expected score/ranking behavior: exact match ranks above lower-overlap candidate.
   * expected review/block flags: both remain review-required candidates.
   * expected reason codes: `exact_domain_match`, `subject_claim_match_score_applied`, `ranking_not_authority`.
   * authority invariant tested: AVF score is not authority.

3. `stale_candidate_gets_review_required_penalty`
   * input setup: resolve a stale high-overlap candidate.
   * expected candidate vector count: 1.
   * expected score/ranking behavior: stale penalty lowers score or marks review priority.
   * expected review/block flags: review required; direct reuse blocked.
   * expected reason codes: `stale_candidate_review_required`, `stale_direct_reuse_block`.
   * authority invariant tested: stale candidate cannot silently win.

4. `quarantine_deadend_candidate_blocked_from_top_reuse`
   * input setup: resolve quarantine/deadend candidates with otherwise attractive overlap.
   * expected candidate vector count: at least 2.
   * expected score/ranking behavior: hard block or heavy penalty prevents reuse path.
   * expected review/block flags: blocked from direct reuse.
   * expected reason codes: `quarantine_deadend_direct_reuse_block`, `hard_block_applied`.
   * authority invariant tested: quarantine/deadend candidate cannot become direct reuse.

5. `conflicting_provenance_penalizes_or_blocks_candidate`
   * input setup: resolve candidate with conflicting provenance.
   * expected candidate vector count: 1.
   * expected score/ranking behavior: conflict penalty or block applies.
   * expected review/block flags: review required or blocked.
   * expected reason codes: `conflicting_provenance_penalty`, `conflicting_provenance_direct_reuse_block`.
   * authority invariant tested: conflicting provenance blocks or forces review.

6. `duplicate_spam_candidates_do_not_win_by_volume`
   * input setup: resolve duplicate/spam candidates that try to dominate by count.
   * expected candidate vector count: duplicate inputs are visible, but duplicate pressure is detected.
   * expected score/ranking behavior: duplicate pressure is penalized or summarized; volume alone does not pick a winner.
   * expected review/block flags: review required.
   * expected reason codes: `duplicate_spam_pressure_detected`, `duplicate_count_not_authority`.
   * authority invariant tested: duplicate/spam candidates cannot become authority by volume.

7. `high_score_candidate_still_requires_gt_lgt_root_review`
   * input setup: generate a high-scoring clean candidate.
   * expected candidate vector count: 1.
   * expected score/ranking behavior: high score may be top-ranked.
   * expected review/block flags: GT/LGT/Root review required.
   * expected reason codes: `high_score_review_required`, `gt_lgt_root_review_required`.
   * authority invariant tested: Top-ranked candidate is not action permission.

8. `schema_valid_vector_is_not_semantic_truth`
   * input setup: generate a schema-compatible vector from a candidate carrying semantic risk.
   * expected candidate vector count: 1.
   * expected score/ranking behavior: schema validity only affects shape/compatibility.
   * expected review/block flags: semantic risk still forces review or block.
   * expected reason codes: `schema_validity_shape_only`, `schema_valid_vector_is_not_semantic_truth`.
   * authority invariant tested: schema-valid candidate vector is not semantic truth.

9. `root_final_authority_preserved_across_avf_scoring`
   * input setup: composite set with clean, stale, conflict, quarantine/deadend, duplicate, and high-scoring candidates.
   * expected candidate vector count: multiple generated vectors.
   * expected score/ranking behavior: deterministic ranking is produced, but no final use occurs.
   * expected review/block flags: every candidate remains candidate-only; Root review required.
   * expected reason codes: `root_final_authority_preserved_across_avf_scoring`.
   * authority invariant tested: Root remains final authority.

## 12. Future counters

Future proof counters:

* drs_candidates_input_count
* candidate_vectors_generated_count
* avf_scores_computed_count
* ranked_candidates_count
* top_ranked_candidates_count
* direct_reuse_allowed_count: 0
* action_permission_granted_count: 0
* avf_authority_claimed_count: 0
* vector_truth_claimed_count: 0
* schema_validity_truth_claimed_count: 0
* stale_candidate_review_required_count
* quarantine_deadend_blocked_count
* conflicting_provenance_penalized_count
* duplicate_spam_candidates_seen_count
* duplicate_spam_authority_claimed_count: 0
* high_score_direct_reuse_granted_count: 0
* gt_lgt_review_required_count
* root_review_required_count
* manifest_mutation_count: 0
* transition_matrix_mutation_count: 0
* network_used_count: 0
* gemini_used_count: 0
* root_final_authority_preserved_count

Required PASS conditions:

* direct_reuse_allowed_count == 0
* action_permission_granted_count == 0
* avf_authority_claimed_count == 0
* vector_truth_claimed_count == 0
* schema_validity_truth_claimed_count == 0
* duplicate_spam_authority_claimed_count == 0
* high_score_direct_reuse_granted_count == 0
* manifest_mutation_count == 0
* transition_matrix_mutation_count == 0
* network_used_count == 0
* gemini_used_count == 0
* root_final_authority_preserved_count == scenarios_total

## 13. Future validation plan

Future implementation should run:

```bash
python3 -m demo.run_candidate_vector_generator_avf_scoring_v01

PYTHONPATH=. .venv/bin/python -m pytest -q \
  tests/test_candidate_vector_generator_avf_scoring_v01_runner.py \
  tests/test_candidate_vectors.py \
  tests/test_avf_runtime.py \
  tests/test_reuse_gate_runtime.py \
  tests/test_real_local_drs_resolver_writeback_v01_runner.py
```

Because this future patch will add runtime code, full pytest is required before
closure/docs sync.

## 14. Non-goals

The future layer must explicitly remain within these non-goals:

* no production AVF
* no production DRS
* no external/global DRS
* no network
* no Gemini
* no embeddings
* no LLM semantic matching
* no autonomous action
* no connector side effects
* no public WOW
* no whitepaper/public auditor packet
* no Marennya/UP
* no self-modifying manifest
* no transition matrix mutation
* no GT/LGT implementation in this layer
* no Fractal Cell runtime integration in this layer
* no direct reuse permission
* no final output authority
* Real Semantic Runtime MVP is not complete

## 15. Recommended next step

CandidateVectorGenerator + Real AVF Scoring v0.1 IMPLEMENTATION
