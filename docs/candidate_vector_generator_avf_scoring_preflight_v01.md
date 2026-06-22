# CandidateVectorGenerator + Real AVF Scoring v0.1 - Preflight

## 1. Current checkpoint

* preflight_id: candidate_vector_generator_avf_scoring_preflight_v01
* preflight_status: COMPLETE
* current_head_before_layer: 4f513d1
* previous_runtime_layer: Real Local DRS Resolver / Writeback v0.1
* roadmap_block: Real Semantic Runtime MVP
* follows_STOP_PROOF_ONLY_EXPANSION_GATE: true
* runtime_modified: false
* schemas_modified: false
* tests_modified: false
* demos_modified: false
* proof_started: false
* audit_started: false
* human_walkthrough_started: false
* full_pytest_run: false

This is a read-only preflight. It follows the STOP PROOF-ONLY EXPANSION GATE
and inspects the next runtime-facing layer before any patch plan,
implementation, proof runner, tests, audit, or walkthrough.

## 2. Purpose

This layer begins the second runtime-facing primitive of Real Semantic Runtime
MVP.

Real Local DRS Resolver / Writeback v0.1 can now write semantic memory and
resolve candidate memory. CandidateVectorGenerator + Real AVF Scoring v0.1
should convert resolved candidates into bounded candidate vectors and
deterministic AVF scores.

The intended path is:

```text
DRS writes/resolves candidate memory
-> CandidateVectorGenerator produces bounded candidate vectors
-> AVF scores them deterministically
-> score influences ranking/review
-> GT/LGT/Root remain required before final use
```

AVF may rank, filter, or route candidates for review. AVF must not decide
truth, permission, action, or final output.

Core rule:

* Candidate vector is not truth
* AVF score is not authority
* Top-ranked candidate is not action permission
* DRS hit is not authority
* Root remains final authority

## 3. Non-goals / boundaries

This preflight does not implement the layer. The future layer must preserve
these boundaries unless a later reviewed patch explicitly changes scope:

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

## 4. Existing assets found

| File path | Observed role | Already provides | Does not yet provide | Boundary role |
| --- | --- | --- | --- | --- |
| `hedgehog/candidate_vectors.py` | Candidate vector loader for installed needles. | Loads declared vectors from needle files, validates allowed sources, and validates declared action metadata. | Does not convert Local DRS resolver candidates into vectors; does not perform runtime DRS candidate scoring. | Candidate/advisory input loader. |
| `hedgehog/models.py` | Runtime dataclasses for `CandidateFeatures` and `CandidateVector`. | Structured candidate vector shape with AVF feature fields, source, domain, branching hint, hard-forbidden flag, and source record ref. | Does not include DRS resolver pressure fields such as stale, conflict, quarantine, duplicate pressure, or Root review state. | Candidate shape, not authority. |
| `hedgehog/avf.py` | Existing AVF helper. | Deterministic `score_candidate_vector(...)`, hard mask, soft mask, viability score, and `build_attractor_packet(...)`. | Does not generate candidate vectors from resolved DRS candidates; does not produce a DRS candidate-vector report with poisoning/review counters. | Advisory scoring/filtering before Architect. |
| `hedgehog/policies.py` | Candidate source and hard-forbidden policy constants. | Allowed sources are needle, local_drs, external_drs_pointer, and fallback_template; hard-forbidden regions include illegal_coercion, fraud, identity_abuse, violence, and privacy_violation. | Does not rank or generate DRS-derived vectors. | Blocking policy support, not final authority. |
| `hedgehog/local_drs_resolver.py` | First runtime-facing DRS resolver/writeback primitive. | `write_semantic_record(...)`, `resolve_semantic_candidates(...)`, `write_root_final_record(...)`, `ResolvedDRSCandidate`, and `ResolvedDRSReport`; returns candidates only with Root review and reason codes. | Does not convert candidates to AVF `CandidateVector` objects or produce AVF-ranked candidate reports. | Candidate/review primitive, not authority. |
| `hedgehog/drs.py` | Local file-backed DRS store. | `LocalDRS`, local layer separation, required field checks, TimeEnvelope requirement, sensitive-key rejection, pointer shape validation, read/write/query. | Does not do AVF scoring or semantic vector generation. | Local storage boundary, not truth. |
| `hedgehog/reuse_gate.py` | Advisory reuse scoring helpers. | Deterministic freshness, GT trust, policy, conflict, reuse score, and candidate decision helpers. | Does not create AVF vectors and does not grant final reuse. | Advisory scoring, not Root. |
| `hedgehog/time_model.py` | Time helpers. | `make_time_envelope(...)`, `make_temporal_query(...)`, and UTC timestamps. | Does not rank candidates. | Freshness/time context support, not final authority. |
| `hedgehog/gt_validator.py` | GT validator and payoff scoring. | GT selection over V&V reports, payoff components, deterministic tie-break behavior, and AVF viability as one input to payoff. | Does not provide LGT and is not the current layer implementation target. | Advisory/selection, not final output authority. |
| `hedgehog/root_orchestrator.py` | Existing Root-controlled pipeline. | Root orchestrates TemporalQuery, LocalDRS query, ReuseGate, candidate vector loading from needles, AVF AttractorPacket, Architect, Executor, Post V&V, GT, Root final, and DRS writeback. | Does not yet use a DRS-resolved CandidateVectorGenerator adapter. Future v0.1 should avoid changing RootOrchestrator unless separately planned. | Root final authority. |
| `schemas/candidate_vector.schema.json` | CandidateVector schema. | Shape for vector_id, source, domain, branching_hint, features, hard_forbidden, provenance_refs, and source_record_ref. | Does not include resolver pressure metadata; schema change is not required for preflight. | Shape validation, not semantic truth. |
| `schemas/attractor_packet.schema.json` | AttractorPacket schema. | Packet shape with hard_forbidden_regions, selected candidate_vectors, branch budget, exploration budget, and Architect instructions. | Current candidate vector item shape is compact and may not fit detailed DRS pressure reports without a sidecar report. | Architect input contract, not authority. |
| `schemas/common.schema.json` | Shared schema definitions. | Common IDs, timestamps, scores, provenance refs, and domain primitives. | Does not implement scoring. | Schema vocabulary only. |
| `tests/test_candidate_vectors.py` | Candidate vector loader tests. | Verifies needle-declared vectors, allowed sources, missing field behavior, and declared action metadata. | Does not cover DRS-resolved vector generation. | Focused loader coverage. |
| `tests/test_candidate_vectors_no_llm_hallucination.py` | Discovered test file. | Empty file at inspection time. | Does not yet enforce the new runtime adapter behavior. | No current coverage. |
| `tests/test_avf_runtime.py` | AVF runtime tests. | Verifies hard masking of illegal_coercion, AttractorPacket schema validation, selected vector sorting, and Architect instruction boundaries. | Does not score DRS resolver candidates. | Focused AVF coverage. |
| `tests/test_avf_hardmask.py` | Discovered test file. | Empty file at inspection time. | No current hardmask-specific coverage beyond `tests/test_avf_runtime.py`. | No current coverage. |
| `tests/test_real_local_drs_resolver_writeback_v01_runner.py` | Real Local DRS resolver tests. | Verifies resolver API, candidate-only returns, stale/quarantine/deadend/worldstate/conflict/duplicate pressure boundaries, RootFinal writeback, and raw artifact rejection. | Does not generate or score candidate vectors. | Runtime DRS candidate coverage. |
| `tests/test_reuse_gate_runtime.py` | ReuseGate tests. | Verifies advisory reuse score, freshness, GT trust, policy rejection, conflict marker behavior, and direct-reuse candidate flag without applying reuse. | Does not create AVF vectors or Root-reviewed output. | Advisory scoring coverage. |
| `demo/run_real_local_drs_resolver_writeback_v01.py` | Runtime DRS resolver proof runner. | Demonstrates 8 scenarios, candidate-only resolution, Root review required, no action permission, no external/global DRS, and RootFinal local writeback without side effects. | Does not include candidate vector generation or AVF scoring. | Runtime proof, not final authority. |
| `demo/run_avf_attractor_from_accepted_matrix.py` | AVF / Attractor proof. | Forms AttractorPacket-like artifacts only from accepted/downgraded RootMatrixGateDecision outputs; rejected matrices do not reach AVF; AVF does not create final output, write DRS, or execute actions. | Does not consume Local DRS resolver candidates. | AVF boundary proof. |
| `demo/run_applied_drs_retrieval_reuse.py` | Applied DRS retrieval/reuse proof. | Shows retrieval candidates, semantic similarity, reuse score, stale/quarantine/deadend/wrong-domain/permission boundaries, and Root authority. | Proof-local candidate rows, not runtime CandidateVectorGenerator. | Advisory proof evidence. |
| `demo/run_reuse_score.py` | ReuseScore proof. | Deterministic advisory ranking over visible DRS signals and policy gates. | Not a runtime AVF adapter and not Root authority. | Advisory/ranking proof. |
| `specs/invariants.md`, `specs/human_passport_v0_25.md`, `README.md`, `AGENTS.md` | Architecture invariants and roadmap. | Record CandidateVectors allowed sources, AVF before Architect, HardMask before Architect, DRS hit not direct reuse, ReuseScore advisory, Root final authority, and Real Semantic Runtime MVP next-layer wording. | Do not implement the runtime layer. | Controlling boundary docs. |

## 5. Proposed implementation seam

The safest future seam is to add a small adapter module:

* `hedgehog/candidate_vector_generator.py`

This should sit beside, not replace, `hedgehog/candidate_vectors.py`.
`candidate_vectors.py` is currently a loader for declared needle vectors. The
new module should be the runtime adapter that converts `ResolvedDRSCandidate`
objects from `hedgehog/local_drs_resolver.py` into bounded `CandidateVector`
objects and an auditable candidate-vector report.

The future module should compose:

* `hedgehog/local_drs_resolver.py` for resolved Local DRS candidates and reason codes.
* `hedgehog/avf.py` for existing `score_candidate_vector(...)` and, where useful, existing AttractorPacket helpers.
* `hedgehog/reuse_gate.py` for advisory freshness/reuse score components where useful.
* `hedgehog/time_model.py` for TimeEnvelope and freshness signals.
* `hedgehog.models.CandidateVector` and `CandidateFeatures` for existing vector shape compatibility.

Do not replace existing AVF. Do not create a separate memory store. Do not use
external/global DRS. Do not use network/Gemini/LLM/embeddings.

Based on the inspected AttractorPacket schema, the future proof should likely
produce a sidecar `CandidateVectorReport` rather than forcing all DRS pressure
metadata into the existing AttractorPacket candidate item shape. AttractorPacket
can remain the downstream bounded Architect input; the candidate-vector report
can preserve review, poisoning, conflict, stale, and Root boundary details.

## 6. Candidate vector model v0.1

The patch plan should define conceptual dataclasses/functions but not make the
preflight itself an implementation.

Expected concepts:

* `CandidateVectorInput`
* `CandidateVector`
* `CandidateVectorScore`
* `CandidateVectorReport`
* `generate_candidate_vectors(...)`
* `score_candidate_vector(...)`
* `rank_candidate_vectors(...)`
* `build_avf_candidate_report(...)`

The future `CandidateVector` adapter output should preserve:

* candidate_id
* source_record_id
* domain
* subject_key
* claim_key
* content_summary
* semantic_tokens
* time_envelope / freshness flags
* provenance refs
* trace refs
* source refs
* conflict flags
* quarantine/deadend flags
* poisoning flags
* root_review_required
* direct_reuse_allowed: false

The future implementation can either wrap existing `hedgehog.models.CandidateVector`
or emit that existing model plus report-side metadata. The key requirement is
that the generated vector remains candidate/advisory, not authority.

## 7. Deterministic scoring v0.1

Allowed scoring signals:

* exact domain match
* subject/claim key match
* controlled token overlap
* freshness / TTL advisory status
* provenance quality advisory status
* source_refs / trace_refs overlap
* conflict penalty
* quarantine/deadend penalty or block
* duplicate/spam/poisoning pressure penalty
* schema-validity as shape-only, not truth
* Root-reviewed provenance as bounded evidence only

Not allowed:

* LLM scoring
* embedding scoring
* network lookup
* external/global DRS lookup
* source popularity as authority
* schema-validity as semantic truth
* AVF score as final decision
* score threshold creating action permission

Scoring should remain deterministic over structured local fields. A high score
may change ranking or review routing; it must not produce final output,
permission, or reuse.

## 8. Required invariants

Future patch plan, proof, and implementation must preserve:

* Candidate vector is not truth
* Candidate vector is not authority
* AVF score is not authority
* Top-ranked candidate is not action permission
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

## 9. Poisoning / adversarial guardrails folded into acceptance criteria

Because this layer starts scoring candidates, the future layer must include
these guardrails:

* duplicate candidates cannot win by count alone
* spam candidates can at most create review pressure
* compromised upstream-looking records cannot become truth
* repeated external pointer cannot become trust
* stale but high-overlap record cannot silently outrank fresh review
* high AVF score cannot override quarantine/deadend/conflict
* high AVF score cannot create direct reuse permission
* high AVF score cannot create RootFinal output

This is not separate DRS Poisoning Resistance v0.1. This is acceptance criteria
for CandidateVectorGenerator + Real AVF Scoring v0.1.

## 10. Proposed future proof scenarios

The future proof should be local and deterministic. Candidate scenario set:

1. `drs_resolved_candidates_generate_candidate_vectors`
   * Input: Local DRS resolver returns candidate memory.
   * Expected: candidate vectors are generated with source `local_drs`, reason codes, and Root review required.
   * Boundary: generated vector is not truth or authority.

2. `exact_domain_and_claim_match_scores_higher_but_not_authority`
   * Input: one exact domain/claim match and one lower-overlap candidate.
   * Expected: exact match scores higher.
   * Boundary: higher score influences ranking only.

3. `stale_candidate_gets_review_required_penalty`
   * Input: stale high-overlap DRS record.
   * Expected: review-required penalty or downgraded rank.
   * Boundary: stale candidate cannot silently win.

4. `quarantine_deadend_candidate_blocked_from_top_reuse`
   * Input: quarantine/deadend-near candidate with otherwise attractive overlap.
   * Expected: blocked or hard-penalized from reuse path.
   * Boundary: quarantine/deadend candidate cannot become direct reuse.

5. `conflicting_provenance_penalizes_or_blocks_candidate`
   * Input: candidate with conflicting provenance.
   * Expected: conflict penalty or block, with review required.
   * Boundary: provenance informs; it does not decide truth.

6. `duplicate_spam_candidates_do_not_win_by_volume`
   * Input: duplicate/spam candidates attempting to dominate rank by count.
   * Expected: duplicates are detected and penalized or summarized as pressure.
   * Boundary: volume does not create authority.

7. `high_score_candidate_still_requires_gt_lgt_root_review`
   * Input: candidate with high deterministic AVF score.
   * Expected: GT/LGT/Root review remains required.
   * Boundary: AVF score is not final authority.

8. `schema_valid_vector_is_not_semantic_truth`
   * Input: schema-valid vector from a semantically unsafe or stale candidate.
   * Expected: shape validity does not become truth.
   * Boundary: schema-valid candidate vector is not semantic truth.

9. `root_final_authority_preserved_across_avf_scoring`
   * Input: composite stale, conflict, duplicate, and high-scoring candidates.
   * Expected: all non-Root authority flags remain false.
   * Boundary: Root remains final authority.

## 11. Proposed counters for future proof

Proposed counters:

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
* gt_lgt_review_required_count
* root_review_required_count
* manifest_mutation_count: 0
* transition_matrix_mutation_count: 0
* network_used_count: 0
* gemini_used_count: 0
* root_final_authority_preserved_count

Expected PASS shape for v0.1:

* all scenarios pass
* generated vectors are candidate-only
* AVF scores computed deterministically
* direct_reuse_allowed_count: 0
* action_permission_granted_count: 0
* avf_authority_claimed_count: 0
* vector_truth_claimed_count: 0
* duplicate_spam_authority_claimed_count: 0
* network_used_count: 0
* gemini_used_count: 0
* Root final authority preserved for every scenario

## 12. Risks / decisions needed

Implementation decisions to settle in the patch plan:

* Whether to reuse existing AVF builder directly or add a candidate-vector adapter beside it.
  * Recommendation: add an adapter beside it. Existing AVF scoring is useful, but DRS pressure metadata needs a richer report.
* Whether AttractorPacket schema already fits candidate vector reports.
  * Finding: AttractorPacket fits selected Architect-facing vectors, but not detailed DRS pressure evidence. Use a sidecar report for v0.1 unless a later schema patch is approved.
* Whether AVF scoring should output a new proof-local report or existing AttractorPacket-compatible shape.
  * Recommendation: output a report with existing `CandidateVector` compatibility and optional AttractorPacket build only for bounded selected vectors.
* How much to reuse `reuse_gate.py`.
  * Recommendation: reuse its deterministic advisory freshness/reuse components where helpful, but do not allow ReuseGate eligibility to become Root authority.
* How to keep scoring deterministic without embeddings/LLM.
  * Recommendation: exact domain/key matches, controlled token overlap, TimeEnvelope freshness, source/trace/provenance overlap, and explicit penalties.
* Whether full pytest is required after implementation.
  * Recommendation: because this next layer will touch runtime code, run focused tests plus adjacent AVF/DRS/reuse tests initially, and require full pytest before checkpoint closure/docs sync.

## 13. Recommended next step

CandidateVectorGenerator + Real AVF Scoring v0.1 PATCH PLAN
