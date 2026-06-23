# GT/LGT Advisory Evaluator v0.1 — Preflight

## 1. Current checkpoint

- preflight_id: gt_lgt_advisory_evaluator_preflight_v01
- preflight_status: COMPLETE
- current_head_before_layer: 762239c
- previous_runtime_layer: CandidateVectorGenerator + Real AVF Scoring v0.1
- previous_runtime_checkpoint: 762239c
- runtime_gate_commit: 1e1afe6
- roadmap_block: Real Semantic Runtime MVP
- follows_STOP_PROOF_ONLY_EXPANSION_GATE: true
- runtime_modified: false
- schemas_modified: false
- tests_modified: false
- demos_modified: false
- proof_started: false
- audit_started: false
- human_walkthrough_started: false
- full_pytest_run: false

## 2. Purpose

This layer begins the third runtime-facing primitive of Real Semantic Runtime
MVP.

Current state:

- DRS can write and resolve local semantic memory candidates.
- CandidateVectorGenerator can convert candidates into bounded vectors.
- AVF can score and rank those vectors deterministically for review.

GT/LGT Advisory Evaluator should interpret candidate, vector, and AVF review
signals into advisory evaluation reports for Root review. It must not create
final output, action permission, direct reuse permission, or Root authority.

## 3. Non-goals / boundaries

- no production GT/LGT
- no production DRS
- no production AVF
- no external/global DRS
- no network
- no Gemini
- no embeddings
- no LLM semantic matching
- no autonomous action
- no connector side effects
- no public WOW
- no whitepaper/public auditor packet
- no Marennya/UP
- no self-modifying manifest
- no transition matrix mutation
- no Fractal Cell Runtime integration in this layer
- no Root behavior modification
- no FinalOutput creation
- no direct reuse permission
- no action permission
- Real Semantic Runtime MVP is not complete

## 4. Existing assets found

### Existing GT validator / GTReport runtime

- file path: `hedgehog/gt_validator.py`
- observed role: deterministic GT validator over Post V&V reports.
- what it already provides: `validate_gt(...)`, payoff component computation,
  `accept`, `revise`, and `no_update` report paths, Elo/regret/half-life
  metadata, schema validation, and explicit notes that GT is not TruthProof.
- what it does not provide yet: direct input from CandidateVectorReport,
  GT/LGT combined advisory report construction, LGT signals, Root review route
  output for AVF-ranked candidates, or Root Final authority.
- boundary status: advisory, not final authority.

- file path: `schemas/gt_report.schema.json`
- observed role: JSON Schema for GTValidator report artifacts.
- what it already provides: `GTValidator Report` shape with `gt_report_id`,
  `game_mode`, `candidates`, `decision`, and `created_at`; decision values
  include `accept`, `revise`, `reject`, `rerun`, `needs_user`, and `no_update`.
- what it does not provide yet: LGT schema, CandidateVectorReport input schema,
  or a GT/LGT advisory evaluator report schema.
- boundary status: advisory artifact schema, not final authority.

- file path: `tests/test_gt_validator_runtime.py`
- observed role: focused runtime tests for GTValidator behavior.
- what it already provides: schema validation, `accept`, `revise`, `no_update`,
  payoff component, AVF viability influence, tie-break, and forbidden final
  output/raw text boundary checks.
- what it does not provide yet: tests for CandidateVectorReport-to-GT/LGT
  advisory mapping or LGT signals.
- boundary status: advisory tests, not final authority tests.

### Post V&V validation report flow

- file path: `hedgehog/post_vv.py`
- observed role: validates ResultProposal artifacts and emits V&V reports before
  GT.
- what it already provides: `validate_result_proposals(...)`, JSON Schema-backed
  V&V report construction, task-aware `accept`, `revise`, and `reject`
  decisions, and containment for malformed or unsafe ResultProposal payloads.
- what it does not provide yet: CandidateVectorReport advisory evaluation,
  LGT signals, or Root Final creation.
- boundary status: validation/advisory input to GT, not final authority.

- file path: `schemas/vv_report.schema.json`
- observed role: JSON Schema for Post V&V reports.
- what it already provides: V&V report shape with decisions, scores, normalized
  features, and optional AVF-derived viability metadata.
- what it does not provide yet: GT/LGT advisory evaluator report schema.
- boundary status: validation artifact schema, not final authority.

- file path: `tests/test_post_vv_runtime.py`
- observed role: focused Post V&V runtime tests.
- what it already provides: ResultProposal and VVReport schema validation,
  accepted/revise/reject paths, malformed evidence rejection, and checks that
  V&V does not create final output, authority, AcceptedEvidence, action, or DRS
  write fields from evidence kinds.
- what it does not provide yet: GT/LGT advisory evaluation from AVF-ranked
  candidates.
- boundary status: validation tests, not final authority tests.

### Root final boundary

- file path: `hedgehog/root_orchestrator.py`
- observed role: canonical local pipeline owner and Root FinalOutput creator.
- what it already provides: orchestration through CandidateVectors, AVF,
  Architect, Executor/DAG, Post V&V, GT, Root FinalOutput, and local DRS
  writeback; FinalOutput references `gt_report_ref` and is created by
  `root_orchestrator`.
- what it does not provide yet: a separate GT/LGT advisory evaluator between
  CandidateVector/AVF reports and Root review. It should not be modified by the
  v0.1 advisory evaluator.
- boundary status: final authority.

- file path: `schemas/final_output.schema.json`
- observed role: Root FinalOutput schema.
- what it already provides: FinalOutput shape constrained to
  `created_by: root_orchestrator` with `gt_report_ref` metadata.
- what it does not provide yet: any permission for GT/LGT, AVF, DRS, or
  CandidateVectorGenerator to create FinalOutput.
- boundary status: Root final authority schema.

- file path: `tests/test_root_orchestrator_runtime.py`
- observed role: focused RootOrchestrator runtime tests.
- what it already provides: Root-created FinalOutput checks, GT report
  reference checks, DRS Work writeback checks, and final authority ownership.
- what it does not provide yet: a GT/LGT advisory evaluator input boundary.
- boundary status: final authority tests.

### CandidateVectorGenerator / AVF reports

- file path: `hedgehog/candidate_vector_generator.py`
- observed role: runtime-facing adapter from resolved local DRS candidates to
  bounded candidate vectors, deterministic AVF scores, and reviewable reports.
- what it already provides: `CandidateVectorInput`, `GeneratedCandidateVector`,
  `CandidateVectorScore`, `CandidateVectorReport`,
  `generate_candidate_vectors(...)`, `score_candidate_vector(...)`,
  `rank_candidate_vectors(...)`, and `build_avf_candidate_report(...)`.
- what it does not provide yet: GT/LGT advisory signal creation or GT report
  emission.
- boundary status: candidate/advisory review signal, not final authority.

- file path: `hedgehog/avf.py`
- observed role: deterministic AVF scoring and AttractorPacket construction.
- what it already provides: hard-mask and soft-mask scoring for candidate
  vectors before Architect in the canonical pipeline.
- what it does not provide yet: GT/LGT advisory report generation or Root Final
  decision-making.
- boundary status: advisory ranking/scoring, not authority.

- file path: `tests/test_candidate_vector_generator_avf_scoring_v01_runner.py`
- observed role: focused tests for the current CandidateVectorGenerator + AVF
  layer.
- what it already provides: checks for bounded vectors, deterministic score
  objects, ranking without authorization, review requirements, high-score
  boundary preservation, and zero authority/truth/action counters.
- what it does not provide yet: GT/LGT advisory evaluation tests.
- boundary status: candidate/advisory tests.

- file path: `demo/run_candidate_vector_generator_avf_scoring_v01.py`
- observed role: deterministic runner for the current CandidateVectorGenerator
  + AVF runtime layer.
- what it already provides: nine scenarios proving AVF scoring and ranking
  remain review-only and that GT/LGT review remains required.
- what it does not provide yet: GT/LGT advisory reports.
- boundary status: candidate/advisory proof runner.

### ReuseGate advisory scoring support

- file path: `hedgehog/reuse_gate.py`
- observed role: deterministic reuse scoring support over DRS records and
  temporal queries.
- what it already provides: freshness, GT trust, policy, conflict, and combined
  reuse score calculations; `evaluate_reuse_candidates(...)` returns
  context-only or candidate routing with no applied reuse side effects.
- what it does not provide yet: GT/LGT advisory reports, Root Final review
  routing, or CandidateVectorReport interpretation.
- boundary status: advisory scoring support, not final authority.

- file path: `tests/test_reuse_gate_runtime.py`
- observed role: focused tests for ReuseGate scoring and routing.
- what it already provides: checks for no-record behavior, low GT trust,
  rejected/archived records, conflict markers, candidate scoring, and empty
  reused record ids.
- what it does not provide yet: GT/LGT advisory evaluator coverage.
- boundary status: advisory tests, not final authority tests.

### DRS resolver candidate reports

- file path: `hedgehog/local_drs_resolver.py`
- observed role: runtime-facing local DRS resolver/writeback primitive.
- what it already provides: local semantic record write, deterministic resolve,
  RootFinal-derived local writeback, review-required candidate reports, and
  anti-poisoning writeback boundaries.
- what it does not provide yet: CandidateVector scoring or GT/LGT advisory
  evaluation.
- boundary status: candidate-only memory resolver, not authority.

- file path: `demo/run_real_local_drs_resolver_writeback_v01.py`
- observed role: deterministic runner for local DRS write, resolve, and
  writeback.
- what it already provides: eight scenarios proving DRS records and hits remain
  candidate-only and Root-reviewed.
- what it does not provide yet: AVF scoring or GT/LGT advisory evaluation.
- boundary status: candidate-only proof runner.

### Canonical proofs and invariants

- file path: `demo/run_canonical_pipeline_trace.py`
- observed role: canonical local pipeline proof.
- what it already provides: visible ordering from Root through DRS precheck,
  AVF, Architect, Executor, Post V&V, GT, Root FinalOutput, and DRS writeback.
- what it does not provide yet: a dedicated GT/LGT advisory evaluator over the
  new CandidateVectorReport layer.
- boundary status: proof runner that preserves Root final authority.

- file path: `demo/run_root_native_full_canonical_e2e_trace.py`
- observed role: full canonical E2E proof connecting first-run canonical
  execution and second-run semantic reuse trace.
- what it already provides: authority safety checks including GT no final output
  and Root authority preservation.
- what it does not provide yet: GT/LGT advisory evaluator over AVF-ranked
  candidates.
- boundary status: proof runner, not production autonomy.

- file path: `specs/invariants.md`
- observed role: non-negotiable architecture invariants.
- what it already provides: Root-only FinalOutput, Post V&V before GT, GT
  selection without final commit, DRS not authority, AVF before Architect, and
  Root final authority.
- what it does not provide yet: detailed GT/LGT Advisory Evaluator v0.1
  acceptance criteria.
- boundary status: invariant source.

- file path: `specs/human_passport_v0_25.md`
- observed role: MVP architecture and checkpoint narrative.
- what it already provides: current semantic runtime thread through local DRS
  and CandidateVector/AVF, plus next step as GT/LGT advisory evaluator v0.1
  preflight.
- what it does not provide yet: this preflight's implementation seam and future
  proof scope.
- boundary status: architecture reference.

- file path: `specs/schema_package_v0_25_reference.md`
- observed role: schema reference and checkpoint notes.
- what it already provides: GTReport, V&V report, FinalOutput, CandidateVector,
  and DRSRecord reference context, plus Root/GT/DRS authority boundaries.
- what it does not provide yet: an LGT schema or GT/LGT advisory evaluator
  schema.
- boundary status: schema reference, not runtime authority.

## 5. LGT status

- Is LGT currently implemented in code? No concrete LGT runtime module was found.
  The search found GT runtime code, and GT/LGT review terminology in the current
  CandidateVectorGenerator layer, but no standalone LGT evaluator.
- Is LGT only mentioned in docs/roadmap? Mostly yes. LGT appears in roadmap and
  checkpoint wording, and in CandidateVectorGenerator fields such as
  `gt_lgt_review_required` and `gt_lgt_review_required_count`.
- Is there any schema for LGT? No LGT schema was found.
- Is there any test/demo for LGT? No dedicated LGT test or demo was found.
- Should v0.1 implement LGT now, defer it, or define a proof-local advisory
  placeholder? The safe recommendation is to not implement full LGT in v0.1.
  Keep GT/LGT layer as an advisory evaluator preflight. A future patch plan may
  define a local lightweight LGT advisory signal only if it composes existing
  DRS/AVF provenance and does not create authority.

## 6. Proposed implementation seam

Recommended future seam:

- add `hedgehog/gt_lgt_advisory_evaluator.py`

It should compose:

- existing `hedgehog/gt_validator.py`
- existing `hedgehog/candidate_vector_generator.py`
- existing `hedgehog/avf.py`
- existing `hedgehog/local_drs_resolver.py`
- existing Post V&V / ValidationReport concepts where useful

The v0.1 implementation should be a narrow adapter over current runtime
artifacts. It should not replace `gt_validator.py`, should not modify
RootOrchestrator, should not create FinalOutput, and should not create a new
schema unless a hard blocker is found and a separate schema patch plan is
approved.

If LGT remains absent at patch time, the safest patch plan is either a GT-only
adapter with LGT explicitly deferred, or a proof-local LGT advisory placeholder
that reports absence/local signal status without adding authority.

## 7. Advisory evaluator model v0.1

Future conceptual API only; this preflight does not implement it.

Expected concepts:

- `AdvisoryEvaluationInput`
- `AdvisorySignal`
- `GTLGTAdvisoryReport`
- `evaluate_candidate_report(...)`
- `evaluate_gt_signal(...)`
- `evaluate_lgt_signal(...)`
- `build_advisory_report(...)`

`AdvisoryEvaluationInput` should preserve:

- candidate vector report id
- DRS candidate refs
- AVF score refs
- ranked candidate ids
- reason codes
- conflict/stale/quarantine/deadend/poisoning flags
- provenance refs
- trace refs
- source refs
- root_review_required
- direct_reuse_allowed: false

`AdvisorySignal` should preserve:

- signal_id
- signal_kind: gt or lgt
- advisory_decision: accept_candidate / degrade_candidate / reject_candidate /
  needs_review / no_update
- confidence or strength as advisory metadata only
- reason codes
- authority_claimed: false
- truth_claimed: false
- action_permission_claimed: false
- final_output_claimed: false

`GTLGTAdvisoryReport` should preserve:

- report_id
- candidate_count
- signals
- recommended_review_route
- root_review_required: true
- direct_reuse_allowed_count: 0
- action_permission_granted_count: 0
- root_final_authority_preserved: true

## 8. Deterministic advisory logic v0.1

Allowed signals:

- AVF ranked candidate report
- DRS resolver candidate review flags
- freshness/staleness flags
- conflict flags
- quarantine/deadend flags
- poisoning pressure flags
- provenance/source/trace refs
- schema-validity as shape-only
- Post V&V / GT accept/degrade/reject concepts as advisory mapping only

Not allowed:

- LLM judgement
- embeddings
- network lookup
- external/global DRS lookup
- GT/LGT score as truth
- advisory accept as Root Final
- advisory accept as action permission
- advisory accept as direct reuse permission
- advisory no_update as final rejection
- modifying Root behavior

## 9. Required invariants

- GT is advisory
- LGT is advisory
- GT/LGT report is not truth
- GT/LGT report is not Root Final
- GT/LGT advisory accept is not action permission
- GT/LGT advisory accept is not direct reuse permission
- AVF score is not authority
- Candidate vector is not truth
- DRS hit is not authority
- DRS reuse candidate is not action permission
- stale candidate cannot silently pass
- quarantine/deadend candidate forces review or block
- conflicting provenance forces review or block
- duplicate/spam candidates cannot become authority by volume
- schema-valid advisory report is not semantic truth
- Root remains final authority
- evaluator cannot mutate manifest
- evaluator cannot mutate transition matrix
- evaluator cannot call network/Gemini/connectors
- evaluator cannot create FinalOutput

## 10. Poisoning/adversarial acceptance criteria

Because this layer interprets ranked/scored candidates, the future proof should
include these guardrails:

- high AVF score cannot force GT accept
- many duplicate candidates cannot force GT/LGT accept
- stale but high-ranked candidate cannot silently pass
- quarantine/deadend cannot be overridden by GT/LGT advisory score
- conflicting provenance cannot be hidden by high AVF score
- schema-valid report cannot become truth
- advisory accept cannot become RootFinal
- advisory accept cannot create action permission
- advisory accept cannot create direct reuse permission

This is not separate DRS Poisoning Resistance v0.1. This is acceptance criteria
for GT/LGT Advisory Evaluator v0.1.

## 11. Proposed future proof scenarios

1. `avf_ranked_report_becomes_advisory_input_only`
   - input setup: one AVF-ranked CandidateVectorReport from local DRS
     candidates.
   - expected advisory signals: candidate report accepted as advisory input.
   - expected review route: Root review required.
   - expected blocked/degraded/rejected behavior: no candidate receives direct
     reuse permission.
   - expected reason codes: `avf_ranked_report_input_only`,
     `root_review_required`.
   - authority invariant tested: AVF score is not authority.

2. `gt_accept_signal_requires_root_final_review`
   - input setup: clean high-ranked candidate with no stale, conflict,
     quarantine, or poisoning flags.
   - expected advisory signals: GT accept_candidate signal.
   - expected review route: Root final review required.
   - expected blocked/degraded/rejected behavior: accept signal remains
     advisory.
   - expected reason codes: `gt_accept_advisory_only`,
     `root_final_review_required`.
   - authority invariant tested: GT/LGT advisory accept is not action permission
     and not direct reuse permission.

3. `gt_degrade_signal_routes_to_review_not_final`
   - input setup: candidate with partial freshness or provenance concern.
   - expected advisory signals: GT degrade_candidate signal.
   - expected review route: needs review.
   - expected blocked/degraded/rejected behavior: degraded candidate cannot
     become final output.
   - expected reason codes: `gt_degrade_routes_to_review`,
     `final_output_not_created`.
   - authority invariant tested: GT/LGT report is not Root Final.

4. `gt_reject_signal_blocks_candidate_not_root_final`
   - input setup: candidate with hard safety block or invalid advisory
     evidence.
   - expected advisory signals: GT reject_candidate signal.
   - expected review route: candidate blocked or routed for Root review.
   - expected blocked/degraded/rejected behavior: rejected candidate does not
     become Root rejection by itself.
   - expected reason codes: `gt_reject_blocks_candidate_only`,
     `root_remains_required`.
   - authority invariant tested: GT reject does not modify Root behavior.

5. `lgt_absent_or_local_signal_remains_advisory`
   - input setup: same candidate report with no concrete LGT runtime present.
   - expected advisory signals: LGT absent/deferred or proof-local advisory
     signal.
   - expected review route: Root review required.
   - expected blocked/degraded/rejected behavior: no LGT signal creates
     authority.
   - expected reason codes: `lgt_absent_or_local_signal_advisory_only`,
     `root_review_required`.
   - authority invariant tested: LGT is advisory.

6. `stale_high_score_candidate_cannot_silent_accept`
   - input setup: high-overlap stale candidate with a strong AVF score.
   - expected advisory signals: needs_review or degrade_candidate.
   - expected review route: Root review required.
   - expected blocked/degraded/rejected behavior: stale candidate cannot pass
     silently.
   - expected reason codes: `stale_high_score_review_required`,
     `silent_accept_blocked`.
   - authority invariant tested: stale candidate cannot silently pass.

7. `quarantine_deadend_overrides_high_score_to_review`
   - input setup: high-scoring candidate with quarantine or deadend proximity.
   - expected advisory signals: reject_candidate or needs_review.
   - expected review route: blocked/review route.
   - expected blocked/degraded/rejected behavior: quarantine/deadend status is
     not overridden by score.
   - expected reason codes: `quarantine_deadend_overrides_score`,
     `direct_reuse_permission_blocked`.
   - authority invariant tested: quarantine/deadend candidate forces review or
     block.

8. `conflicting_provenance_blocks_advisory_accept`
   - input setup: candidate report with conflicting provenance flags.
   - expected advisory signals: reject_candidate or needs_review, not
     accept_candidate.
   - expected review route: conflict review required.
   - expected blocked/degraded/rejected behavior: conflict cannot be hidden by
     AVF rank.
   - expected reason codes: `conflicting_provenance_blocks_accept`,
     `conflict_review_required`.
   - authority invariant tested: conflicting provenance forces review or block.

9. `duplicate_spam_cannot_force_gt_lgt_accept`
   - input setup: many duplicate/spam candidates with matching terms.
   - expected advisory signals: poisoning/spam review pressure, not forced
     accept.
   - expected review route: Root review or quarantine review.
   - expected blocked/degraded/rejected behavior: volume cannot create
     authority.
   - expected reason codes: `duplicate_spam_cannot_force_accept`,
     `poisoning_review_pressure_only`.
   - authority invariant tested: duplicate/spam candidates cannot become
     authority by volume.

10. `root_final_authority_preserved_across_gt_lgt_advisory`
    - input setup: combined clean, degraded, rejected, absent-LGT, stale,
      quarantine, conflict, and duplicate-pressure advisory results.
    - expected advisory signals: mixed accept/degrade/reject/needs_review/
      no_update signals.
    - expected review route: all routes return to Root review.
    - expected blocked/degraded/rejected behavior: no advisory signal creates
      final output, action permission, or direct reuse permission.
    - expected reason codes: `root_final_authority_preserved`,
      `gt_lgt_advisory_only`.
    - authority invariant tested: Root remains final authority.

## 12. Proposed counters for future proof

- advisory_inputs_count
- gt_signals_emitted_count
- lgt_signals_emitted_count
- advisory_reports_created_count
- advisory_accept_count
- advisory_degrade_count
- advisory_reject_count
- advisory_needs_review_count
- direct_reuse_allowed_count: 0
- action_permission_granted_count: 0
- final_output_created_count: 0
- gt_authority_claimed_count: 0
- lgt_authority_claimed_count: 0
- advisory_truth_claimed_count: 0
- advisory_accept_as_root_final_count: 0
- high_score_forced_accept_count: 0
- duplicate_spam_forced_accept_count: 0
- stale_silent_accept_count: 0
- quarantine_deadend_override_count: 0
- conflicting_provenance_hidden_count: 0
- manifest_mutation_count: 0
- transition_matrix_mutation_count: 0
- network_used_count: 0
- gemini_used_count: 0
- root_review_required_count
- root_final_authority_preserved_count

Required PASS conditions:

- `direct_reuse_allowed_count == 0`
- `action_permission_granted_count == 0`
- `final_output_created_count == 0`
- `gt_authority_claimed_count == 0`
- `lgt_authority_claimed_count == 0`
- `advisory_truth_claimed_count == 0`
- `advisory_accept_as_root_final_count == 0`
- `high_score_forced_accept_count == 0`
- `duplicate_spam_forced_accept_count == 0`
- `stale_silent_accept_count == 0`
- `quarantine_deadend_override_count == 0`
- `conflicting_provenance_hidden_count == 0`
- `manifest_mutation_count == 0`
- `transition_matrix_mutation_count == 0`
- `network_used_count == 0`
- `gemini_used_count == 0`
- `root_final_authority_preserved_count == scenarios_total`

## 13. Risks / decisions needed

- Decide whether LGT should stay deferred or appear as a minimal local advisory
  signal in the future patch plan.
- Decide whether existing GTReport schema can represent this layer or whether a
  proof-local report should be used first.
- Decide whether the advisory evaluator should emit schema-compatible GTReport
  artifacts, a new internal report, or both in a later reviewed schema phase.
- Avoid changing RootOrchestrator prematurely; Root behavior should remain
  unchanged in v0.1.
- Keep GT/LGT deterministic and non-LLM by using only DRS, AVF, provenance,
  stale/conflict/quarantine/deadend, poisoning, and validation metadata.
- Because future implementation will add runtime code, full pytest should be
  required before closure/docs sync.

## 14. Recommended next step

GT/LGT Advisory Evaluator v0.1 PATCH PLAN
