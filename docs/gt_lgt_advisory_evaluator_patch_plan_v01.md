# GT/LGT Advisory Evaluator v0.1 — Patch Plan

## 1. Current checkpoint

- patch_plan_id: gt_lgt_advisory_evaluator_patch_plan_v01
- patch_plan_status: COMPLETE
- preflight_commit: c9ff238
- previous_runtime_checkpoint: 762239c
- runtime_gate_commit: 1e1afe6
- roadmap_block: Real Semantic Runtime MVP
- layer_type: runtime_facing_patch_plan
- implementation_started: false
- runtime_modified: false
- schemas_modified: false
- tests_created: false
- demos_created: false
- full_pytest_run: false

## 2. Purpose

This patch plan defines the future implementation of a deterministic advisory
evaluator that consumes candidate, vector, and AVF review signals and produces
advisory GT/LGT-style evaluation reports for Root review.

The evaluator does not create truth, Root Final, direct reuse permission, action
permission, or final output. It connects the current runtime-facing chain:

```text
DRS resolved candidates
-> CandidateVectors
-> AVF scored/ranked reports
-> GT/LGT advisory evaluation
-> Root review/final authority still required
```

## 3. LGT decision

- Concrete LGT runtime module: absent
- Concrete LGT schema: absent
- Concrete LGT tests/demos: absent
- LGT appears as roadmap/checkpoint terminology and review-required signal
  terminology in recent runtime layers.

Decision for v0.1:

- Do not implement full LGT runtime in this layer.
- Implement GT-first advisory evaluator.
- If LGT is referenced, keep it as a local/deferred advisory placeholder only.
- Any LGT-style signal must have:
  - authority_claimed: false
  - truth_claimed: false
  - action_permission_claimed: false
  - final_output_claimed: false
  - root_review_required: true
- Do not add LGT schema.
- Do not modify RootOrchestrator.
- Do not claim a production LGT layer exists.

## 4. Implementation decision

Future implementation seam:

- add `hedgehog/gt_lgt_advisory_evaluator.py`

It should compose:

- existing `hedgehog/gt_validator.py`
- existing `hedgehog/candidate_vector_generator.py`
- existing `hedgehog/avf.py`
- existing `hedgehog/local_drs_resolver.py`
- existing `hedgehog/post_vv.py` / ValidationReport concepts where useful

Do not replace:

- `hedgehog/gt_validator.py`
- `hedgehog/post_vv.py`
- `hedgehog/root_orchestrator.py`
- `hedgehog/candidate_vector_generator.py`

Do not modify RootOrchestrator. Do not create FinalOutput. Do not create new
schema unless a hard blocker is found and a separate schema patch plan is
approved.

## 5. Future allowed implementation files

Future implementation should be limited to:

- `hedgehog/gt_lgt_advisory_evaluator.py`
- `demo/run_gt_lgt_advisory_evaluator_v01.py`
- `tests/test_gt_lgt_advisory_evaluator_v01_runner.py`

No schema changes are expected for v0.1.

If any schema change is proposed, mark it as deferred and requiring a separate
schema patch plan.

## 6. Advisory evaluator model v0.1

Future conceptual API only; this patch plan does not implement it.

Expected concepts:

- `AdvisoryEvaluationInput`
- `AdvisorySignal`
- `GTLGTAdvisoryReport`
- `evaluate_candidate_report(...)`
- `evaluate_gt_signal(...)`
- `evaluate_lgt_signal(...)`
- `build_advisory_report(...)`

Important:

If LGT is absent, `evaluate_lgt_signal(...)` must either:

- return a deferred/local advisory placeholder, or
- emit no LGT signal and record `lgt_status: deferred`.

It must not claim a production LGT exists.

`AdvisoryEvaluationInput` should preserve:

- candidate vector report id
- DRS candidate refs
- AVF score refs
- ranked candidate ids
- reason codes
- conflict flags
- stale flags
- quarantine/deadend flags
- poisoning flags
- provenance refs
- trace refs
- source refs
- root_review_required
- direct_reuse_allowed: false

`AdvisorySignal` should preserve:

- signal_id
- signal_kind: gt / lgt_placeholder / lgt_deferred
- advisory_decision:
  - accept_candidate
  - degrade_candidate
  - reject_candidate
  - needs_review
  - no_update
- confidence or strength as advisory metadata only
- reason codes
- authority_claimed: false
- truth_claimed: false
- action_permission_claimed: false
- final_output_claimed: false
- direct_reuse_allowed: false
- root_review_required: true

`GTLGTAdvisoryReport` should preserve:

- report_id
- candidate_count
- signals
- recommended_review_route
- root_review_required: true
- direct_reuse_allowed_count: 0
- action_permission_granted_count: 0
- final_output_created_count: 0
- root_final_authority_preserved: true

## 7. Decision vocabulary mapping

Existing GT vocabulary includes terms such as:

- accept
- revise
- reject
- rerun
- needs_user
- no_update

The future advisory evaluator may use local proof terminology:

- accept_candidate
- degrade_candidate
- reject_candidate
- needs_review
- no_update

Required mapping:

- accept_candidate maps to advisory accept only, not Root Final
- degrade_candidate maps to existing revise / needs_user style semantics
- reject_candidate blocks candidate route but is not Root Final rejection
- needs_review maps to Root review required
- no_update maps to advisory no_update only, not final rejection

Do not modify GT schema vocabulary in v0.1. Do not add new GT enum without a
separate schema patch plan.

## 8. Deterministic advisory logic v0.1

Allowed inputs:

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
- LGT is advisory or deferred
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

Because this layer interprets ranked/scored candidates, include guardrails:

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

## 11. Future proof scenarios

1. `avf_ranked_report_becomes_advisory_input_only`
   - input setup: generate a local DRS candidate, convert it to a
     CandidateVector, score/rank it with AVF, and feed the report into the
     evaluator.
   - expected advisory signals: one GT-style advisory input signal and LGT
     deferred/local placeholder status.
   - expected review route: Root review required.
   - expected blocked/degraded/rejected behavior: no direct reuse permission and
     no action permission.
   - expected reason codes: `avf_ranked_report_input_only`,
     `root_review_required`.
   - authority invariant tested: AVF score is not authority.

2. `gt_accept_signal_requires_root_final_review`
   - input setup: clean high-ranked candidate with no stale, conflict,
     quarantine, deadend, or poisoning flags.
   - expected advisory signals: `accept_candidate`.
   - expected review route: Root final review required.
   - expected blocked/degraded/rejected behavior: accept remains advisory.
   - expected reason codes: `gt_accept_advisory_only`,
     `root_final_review_required`.
   - authority invariant tested: GT/LGT advisory accept is not action permission
     and is not direct reuse permission.

3. `gt_degrade_signal_routes_to_review_not_final`
   - input setup: candidate with partial freshness, weaker provenance, or
     needs-user style review pressure.
   - expected advisory signals: `degrade_candidate`.
   - expected review route: Root review required.
   - expected blocked/degraded/rejected behavior: degraded candidate cannot
     create final output.
   - expected reason codes: `gt_degrade_routes_to_review`,
     `final_output_not_created`.
   - authority invariant tested: GT/LGT report is not Root Final.

4. `gt_reject_signal_blocks_candidate_not_root_final`
   - input setup: candidate with hard safety block, forbidden mask, or invalid
     advisory evidence.
   - expected advisory signals: `reject_candidate`.
   - expected review route: candidate blocked or sent to Root review.
   - expected blocked/degraded/rejected behavior: GT reject blocks the candidate
     route but does not become Root Final rejection.
   - expected reason codes: `gt_reject_blocks_candidate_only`,
     `root_remains_required`.
   - authority invariant tested: GT signal does not modify Root behavior.

5. `lgt_absent_or_local_signal_remains_advisory`
   - input setup: same candidate report when no concrete LGT runtime exists.
   - expected advisory signals: `lgt_deferred` or local placeholder signal.
   - expected review route: Root review required.
   - expected blocked/degraded/rejected behavior: no LGT signal creates
     authority.
   - expected reason codes: `lgt_absent_or_local_signal_advisory_only`,
     `lgt_status_deferred`.
   - authority invariant tested: LGT is advisory or deferred.

6. `stale_high_score_candidate_cannot_silent_accept`
   - input setup: stale candidate that still has high token/domain overlap and
     a high AVF score.
   - expected advisory signals: `degrade_candidate` or `needs_review`, not
     silent accept.
   - expected review route: Root review required.
   - expected blocked/degraded/rejected behavior: stale candidate cannot pass
     silently.
   - expected reason codes: `stale_high_score_review_required`,
     `silent_accept_blocked`.
   - authority invariant tested: stale candidate cannot silently pass.

7. `quarantine_deadend_overrides_high_score_to_review`
   - input setup: high-scoring candidate with quarantine or deadend proximity.
   - expected advisory signals: `reject_candidate` or `needs_review`.
   - expected review route: blocked/review route.
   - expected blocked/degraded/rejected behavior: quarantine/deadend status is
     not overridden by score.
   - expected reason codes: `quarantine_deadend_overrides_score`,
     `direct_reuse_permission_blocked`.
   - authority invariant tested: quarantine/deadend candidate forces review or
     block.

8. `conflicting_provenance_blocks_advisory_accept`
   - input setup: candidate report with conflicting provenance flags.
   - expected advisory signals: `reject_candidate` or `needs_review`, not
     `accept_candidate`.
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

## 12. Future counters

- scenarios_total
- scenarios_passed
- advisory_inputs_count
- gt_signals_emitted_count
- lgt_signals_emitted_count
- lgt_deferred_count
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

- `scenarios_total == 10`
- `scenarios_passed == scenarios_total`
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

## 13. Future validation plan

Future implementation should run targeted validation only inside Codex:

```bash
python3 -m demo.run_gt_lgt_advisory_evaluator_v01

PYTHONPATH=. .venv/bin/python -m pytest -q \
  tests/test_gt_lgt_advisory_evaluator_v01_runner.py \
  tests/test_gt_validator_runtime.py \
  tests/test_post_vv_runtime.py \
  tests/test_candidate_vector_generator_avf_scoring_v01_runner.py
```

Do not instruct Codex to run full pytest.

Because this future patch will add runtime code, full pytest must be run
separately by the user before commit and before closure/docs sync.

## 14. Non-goals

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
- no GT schema mutation
- no LGT schema creation
- no full LGT runtime implementation
- Real Semantic Runtime MVP is not complete

## 15. Recommended next step

GT/LGT Advisory Evaluator v0.1 IMPLEMENTATION
