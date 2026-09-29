# Delegated Source Ledger

## Scope and Classification

Repository root: `accepted repository checkout`.
Observed HEAD: `2e965ecb18e545e428380eb8e9aa5a7037a388be`.
Initial full porcelain status: empty. Repository is read-only for this task.

All paths below are relative to that root unless explicitly absolute. All source functions and tests were READ, not imported or run. Equations were transcribed from pure source; arithmetic in the chapter is editorial derivation beside recorded values, not new runtime evidence. No network, provider, installation or Git write was used.

Classes used:

- `accepted-source/static`: implementation present at the user-specified accepted HEAD; not a newly executed result.
- `recorded-historical`: a retained execution with its own source/profile/clock, including original/reviewed G6A views and G36R captures.
- `retained-current-source-witness`: the finite G6A5R1 witness class described by `source_impact.json`, now read as an existing record, not observed again today.
- `check-source-only`: an available test/consumer path inspected without execution. Never promote this to independently-checked by this worker.
- `interpretation/not-demonstrated`: architectural composition or generalisation for which this worker did not locate an executed chain.

The chapter's S references are local editorial citations, not a new authority registry. Main should relocate them into the existing publication index, retaining resource key, payload path, JSON pointer and evidence class.

## S01: Indices and Source Views

Read targeted structured entries in:

- `docs/gate6_reference_v01/evidence_index.json`: `resources` maps resource keys to actual checkout paths, sizes, SHA-256 and recovery provenance. Original absolute paths are provenance only. `current_protocol=TWO_FRESH_NINE_RETAINED_PLUS_FOUR_FINITE_SUCCESSOR_ROWS`.
- `docs/gate6_reference_v01/contract_index.json`: G3 calibration -> `hedgehog/outcome_calibration_v01.py`, normative `docs/gate3_outcome_feedback_contract_v01.md`; G4 reference -> `hedgehog/gate4_reference_contracts_v01.py`, normative `docs/gate4_reference_contract_v01.md`.
- `docs/gate6_reference_v01/geometry_index.json`: `OutcomeHistory -> Root` means `new_review_not_old_authority`; `WorkChild -> ResultProposal` means proposal; `RuntimeTopology -> WorkChild` means runtime-owned execution. This is explanatory, not a registry or proof that every drawn edge executed.
- `docs/gate6_reference_v01/acceptance_matrix.json`: N1-05, N4-04, N4-05 and four deferments; preserved historical `PENDING_EXACT_INDEPENDENT_PACKAGE_REVIEW`/`NOT_YET_AWARDED` fields are not rewritten or used to deny the owner-specified later accepted HEAD.
- `docs/gate6_reference_v01/source_impact.json`: original closure `859c863fa40000dfcd6759685f3b0083f0e040b777df19e5393154fc9ac0f288`; reviewed closure `73f5fe75dee04bb54c629c148bc48b98516765776649b100d108884e5cf7115b`. Current retained obligations have the narrowly repaired compatibility classifier, not a fresh full campaign. G4_original/G44_original and G4_successor/G44_successor stay distinct.
- `specs/current_architecture_lock_v01.md`, current authority laws and named historical scope, read without treating old proposal status as a new instruction to execute.

## S02: Exact G3 Numerical Rules

Source: `hedgehog/outcome_calibration_v01.py`, SHA-256 `ce4a29c7dfe0f536b53fce8435ac584509681bf1cef4511d46ac0bfd48e05079`.

| Formula | Function / location | Types, premises and check route |
| --- | --- | --- |
| Signed nearest/ties-even rational rounding | `round_half_even_rational_v01`, line 334 | Exact Python ints, booleans excluded, positive integer denominator. `tests/test_outcome_calibration_v01.py::test_g33_signed_rational_rounding_and_increment_position`. |
| `R'=clamp(R+RHE(K*(O-E)/Q),0,Q)`, `K=125000000` | `_evaluate_from_plain`, line 970 | Q=10^9, R/E dimensionless fixed-point ints in [0,Q], O in {0,Q}; eligible, comparable subject, time admitted, no unexpected effect, count below 64. No-update preserves prior. `test_g33_frozen_expectation_is_not_replaced_by_fold_predecessor`, `test_g33_dedup_conflict_sparse_warm_cap_and_no_update_preservation`. |
| `P'=clamp(P+RHE(62500000*((2*O-Q)-P)/Q),-Q,Q)` | `fold_avf_history_prior_v01`, line 1406 | Signed dimensionless fixed-point prior; exactly admitted GT occurrence IDs, comparable history key/profile/lane; duplicate occurrences counted once. `validate_avf_prior_against_sources_v01`, line 1445; history consumer below. |
| `A=clamp(B+RHE(250000000*P/Q),0,Q)`; six-place score `RHE(A*1000000/Q)` | `adjusted_avf_score_v01`, line 1438 | B in [0,Q], P in [-Q,Q]. Distinct from G4's five-feature pressure: do NOT first apply this correction and then apply the same raw prior again to G4. |
| `h=clamp(RHE(86400*t*g*f*s/Q^4),3600,604800)` seconds | `_half_life`, line 706 | `t=Q/2+R'`; `g=Q-regret` if known, otherwise Q/2; `f=Q`; `s=Q/2` for verified unsafe, otherwise Q. Factors are fixed-point dimensionless; 86400, h and bounds are seconds. `test_g33_regret_safety_factors_and_profile_bounds`. |
| `T=RHE(R*2^(-a/h))`; exact rational at whole multiples; zero at >=64h | `_decayed_trust`, line 1134; `evaluate_gt_decay_value_v01`, line 1150 | R [0,Q], integer age a >=0, h in [3600,604800] seconds. Time admission is separate in `evaluate_gt_trust_at_v01`; this arithmetic cannot renew TTL. `test_g33_decay_named_vectors_seeded_oracle_and_local_decimal`, `test_g33_explicit_time_boundaries_and_advice_history_anchors`. |
| pressure `Q-T`; recommend if `T<600000000` | `evaluate_review_pressure_v01`, line 1164 | Usable trust only; unusable states require absent T and return `(Q,True)`. Mandatory review is never suppressed. |

`bounded_gt_event_fold_v01` line 852 controls event ordering/deduplication and the 64-event cap. `WARM_SAMPLE_COUNT=3` is a sample-state threshold, not the meaning of a warm DRS/cache execution. No learned global reputation or cross-Root average follows.

## S03: Supplier Refusal -> History -> Different Review

Class: `recorded-historical`, G36R captured reexecution, not current acquisition.

- `docs/showcase/gate3_closure_v01/evidence/g36r/runtime/captured_final/report.json`, SHA-256 `c480efb76fee277b0de4b811b6518a0d62bfeb0a2dace3e00bdbec9931b99667`.
- Same directory `ADV-3_feedback.json`, SHA-256 `facd9b9dbf4be9fa94e6c5a10442a5f95908a1e6c293c1b18c9ac83ce80c72ed`.
- `ADV-1_feedback.json` and `ADV-2_feedback.json`: pre-decision expectation UNKNOWN, observation UNKNOWN, NO_UPDATE, PARTIAL/NOT_EXERCISED. Their prepared packets are not receipts or dispatches.

Exact report pointers:

- `/profile=G36_SOURCE_BOUND_LEARNING_MECHANISM_V01`.
- `/lane=LIVE_OBSERVATION` is an origin label; `/history/prior/lane=CAPTURED_REEXECUTION` identifies consumption. Preserve both.
- `/native_boundaries/2`: case ADV-3, CURRENTNESS, UNSAFE, BLOCKED_AS_REQUIRED, effects 0, firewall null, receipts [].
- `/history/fold/effective_sample_count=1`, `/history/fold/rating_after_fp=375000000`, `/history/prior/prior_fp=-62500000`, negative 1, positive 0, unresolved 2, SPARSE.
- `/history/snapshot_id=7d3398af41d95034a3823b513aa4e004c91965998c8f5ab0a2351b5ab14c7bad`.
- `/current/before_selected=standard`, `/current/after_selected=provenance`, `/current/operation=supplier.review_provenance.v01`.
- `/current/consumed_work=work_results:5a2a7667538205064014b97c0de360ed6b5ab9c4b39a5e6937434cf7d6ab7fd6`.
- `/native_boundaries/3`: CONTINUE, EXECUTOR, one lawful effect with receipt, COMPLETED; `/unauthorized_effects=0`. Mock profile, not a real purchase claim.

Implementation: `hedgehog/domains/supplier_water_filter/adversarial_feedback_v01.py::consume_history_v01` line 558 opens current history, builds current advisory/review, executes bound pure review Work, and compares actual output to `review_material_v01`. `execute_provenance_review_v01` line 489 / `validate_provenance_v01` line 424. Generic history: `hedgehog/outcome_feedback_history_v01.py::OutcomeHistoryV01.current_v01` line 409 and `validate_opened_v01` line 527.

Checks (read only): `tests/test_gate3_adversary_v01.py::test_g36_actual_boundaries_and_useful_continuation`, `test_g36_missing_prospective_expectation_is_no_update`, `test_g36r_provenance_is_additional_capability_validation`, `test_g36r_captured_original_time_and_actual_continuation`, `test_g36_early_lawful_advice_does_not_revive_consumed_order`. Some require pinned external fixture inputs; no availability/execution is asserted here.

## S04: G35 Does Not Manufacture Scorable History

Resource `r/fresh/G35/G35/native/report.json` resolves to `docs/gate6_reference_v01/evidence/blobs/ec4ad7b768ca5790a3c261d2797b62a9f4992d314fd31bd2ea5104aad0ceb97e`; its basename is the indexed SHA-256.

Class: reviewed historical source view, controlled native/safe-derived relations. `/aggregate`: domains 5, unique_occurrences 14, scorable_count 0, model_calls 0, currency/money/tokens UNKNOWN, cross_root_rating NOT_APPLICABLE. `/rows/*/observations/*/feedback/attribution` carries NO_PROSPECTIVE_COMPARABLE_EXPECTATION where applicable. This report is not the scored G36 Supplier profile. The chapter does not turn shared-domain coverage into learning evidence.

## S05: Worked G4 Allocation, Exact Recorded Numbers

Class: recorded campaign G4 evidence, not newly run; keep separate from the old published story even when scalar values coincide. Prefix `a/campaign/G4/G4/package/story/` in the evidence index resolves:

| Resource suffix | Actual path under `docs/gate6_reference_v01/evidence/blobs/` (also SHA-256) |
| --- | --- |
| `summary.json` | `a0d0753edb2e6d235fdc18a14eb184a9d8d7f9c8d77eecaced3c679fb5443db9` |
| `observed_g3.json` | `cfc0bf8da5e79b2778b3383d6d20e1dff09f02ad213cfc779128089b2488466d` |
| `history_recorded.json` | `9dbc3c2e1abf432c6fecc2545b09e10f71a003f2c8482fafcf19da7e0989ad08` |
| `cold/allocation_before_install.json` | `ae6fde136d0c0f8180d71ed082c2b197c744ffb12217b80f83772d95ef7d253f` |
| `warm/allocation_before_install.json` | `7271bfcc4e6d0097895fcab16d94efb96f67494a1599db58c72c6445c62ea2b4` |

`observed_g3.json /feedback` is INCORRECT/ALLOWED_AS_REQUIRED, E=10^9, O=0. It is not the G36 unsafe currentness refusal. `history_recorded.json /snapshot/updates/0`: rating before 500000000, after 375000000, h=37800 seconds. `/snapshot/prior`: one effective occurrence `3c168e1937c24115130c791798919348dd486d483400e27c2a02165cd4d47d5e`, prior -62500000, SPARSE, CONTROLLED_RUNTIME.

Budget pointers: `/budget/total=9`, `/budget/spent=1`, `/allocation/mandatory_units=1`, `/allocation/available=7`, `/allocation/target=7`, `/allocation/unallocated=0`. The already-spent initial constraint must not be counted twice as another remaining mandatory unit.

Exact branch identities for this campaign:

- offer_0: `g4_reference:branch:aa53f7aa77ec1bfcac6845396c8cd1a02463c13e842514e007bc290b9507fbcb`.
- offer_1: `g4_reference:branch:297e03a0299905e46034e9b1a7f5a96d9c1f82b75bfbd0481eba2a06b04fa94f`.

`/budget/pressure_inputs/branches` supplies features and raw prior; `/allocation/rows` is ID ordered, NOT offer-number ordered. Exact residual shares after the two 2-unit minima:

| Phase/offer | z_fp | Weight | Extra numerator / denominator | Remainder numerator / denominator | Allocation |
| --- | ---: | ---: | --- | --- | ---: |
| cold/0 | 425000000 | 1000000000000 | 3000000000000 / 1985111939603 | 1014888060397 / 1985111939603 | 4 |
| cold/1 | 421250000 | 985111939603 | 2955335818809 / 1985111939603 | 970223879206 / 1985111939603 | 3 |
| warm/0 | 417187500 | 983881318977 | 2951643956931 / 1983881318977 | 967762637954 / 1983881318977 | 3 |
| warm/1 | 421250000 | 1000000000000 | 3000000000000 / 1983881318977 | 1016118681023 / 1983881318977 | 4 |

Each extra floor is 1. `/allocation/remainder_awards` names offer_0 cold and offer_1 warm. `summary.json /comparisons/cp_budget` binds cold/warm allocations to actual `*_performed` work IDs; `/instances` records compute_units=dispatches=cap=9 in cold/warm/contrast, model_calls=0. Unit is `ONE_NATIVE_WORK_DISPATCH_UNIT`, not tokens, CPU time, money or probability. Configured features are not measured hardware cost.

Source: `hedgehog/gate4_pressure_budget_v01.py`, SHA-256 `768094bea0cc012046f6c1c514ccbf108e340932f86324d76c59cad0d6680d27`. Functions: `evaluate_reference_pressure_v01` line 12; `_weights` line 47; `_apportion` line 65; `allocate_reference_work_budget_v01` line 103; `validate_reference_allocation_v01` line 146. Constants/types: `hedgehog/gate4_reference_contracts_v01.py` lines 11-18 and branch/budget schemas.

Premises: bound context/source/candidate/catalogue; original policy and spending hashes; hard eligibility before weighting; mandatory count before apportionment; integer total/spent/quotas, available 0..4096; lower <= upper, feasible minima. Weights use a fixed 80-digit Decimal context and RHE. Caps saturate iteratively, residuals use exact Fractions, largest remainder then stable ID; total never exceeds original cap.

Check-source-only: `tests/test_gate4_reference_math_v01.py::test_pressure_contrast`, `test_hand_allocation_vectors`, `test_seeded_allocation_by_saturated_set_enumeration`, `test_mask_before_softmax_negative_score_and_history_once`, `test_decimal_ambient_isolation`; `tests/test_gate4_reference_native_v01.py::test_native_causal_strategy_and_budget`, `test_native_quota_refusals_and_real_exhaustion`.

## S06: Current History Descent

Resource `a/campaign/G4/G4/package/story/warm/current_history.json` -> blob `d7603a6812fc2f14a917b8891e2aceaebfd60a718fd9eab816b702fbefcd825a`.

`/0/read_audit` records DESCRIPTOR -> ROOT_APPROVED -> PAYLOAD_READ -> PUBLIC_OPEN_VALIDATED -> NUMERIC_SOURCE_VALIDATED. Do not count repeated audit rows as independent experience samples. `/0/descent`: records_opened=1, artifacts_opened=1, bytes_opened=7564, depth_reached=1, creates_authority=false, creates_permission=false. `/0/review/result`: ACCEPT, permission_created=false, effect_requested=false. `/0/bridge/payload/prior/prior_fp=-62500000`.

Resource `a/campaign/G4/G4/package/story/warm/current_use.json` -> blob `1a173e73b908da52b3cbb3a09220a2d5d2f1d2dbd46bc35fa7ef8408a57270d5`, current-time records, not a wall-time benchmark.

Source: `hedgehog/domains/airline/gate4_reference_history_v01.py::consume_opened_v01` line 96 calls `current_v01` for a changed current clock and checks identical head/prior/payload before use, refusing expiry. Checks: `tests/test_gate4_reference_history_v01.py::test_history_actual_native_proof_and_recording`, `test_history_wrong_source_role_policy_time_and_head`, `test_g43_retained_history_current_requalification` (end-1 succeeds; end and end+1 fail; original and usage preserved).

## S07: Choice Is Not Shared Authority

Same S05 summary `/comparisons/cp_strategy`: PRICE_FIRST -> `g40:offer:0`; COMFORT_FIRST -> `g40:offer:1`, with independent recorded client/airline/bank Root decisions. `/real_business_effects=0`; `/full_gate4=NOT_CLAIMED`.

Source: `hedgehog/gate4_strategy_reference_v01.py::evaluate_reference_strategy_v01` line 8. It binds source/context, hard-filters, computes one-round weighted utility minus explicit penalties, retains individually rational candidates, computes the Pareto frontier and ranks by product of nonnegative gains (epsilon 1), then stable ID. Missing evidence blocks a recommendation. Flags: root_review_required=true, creates_permission=false, requests_effect=false. This is not full negotiation/StrongGT.

Checks: `tests/test_gate4_reference_native_v01.py::test_native_independent_consent_and_cross_root`: missing bank consent yields NEEDS_USER, hold preparation fails, and swapping a client decision for airline authority fails. `test_native_causal_strategy_and_budget` asserts preparation-only hold and actual consumed work. No real booking claimed.

## S08: N4-04 Cold/Warm Reuse

Exact resource keys `finite/reuse/{witness,checked,collection_receipt}.json` resolve to `docs/gate6_reference_v01/evidence/retained_obligations/reuse/` with the same filenames. Witness SHA-256 `862491cd777f7ca52b60c721ae7923e83f2d42560b3af8c63b9305195e238d81`; checked SHA-256 `0d3d0ddaba99d3b065a885f7746170b1aef0f2bde02c1903f3b9e30ed9883c64`.

Class: retained-current-source-witness. `/business_cold` equals `/business_warm`: operation gate5.source, inputs readings TEXT `[8,10,9]` and reference INTEGER 10, owner `root:gate5:calibration`, policy `policy:g6a5r:informational`, schema `g6a5r.calibration_source.v01`. `/cold/value/outputs` and `/warm/value/answer/answer` contain 27/3/1/1 fields. `/changed_business` has readings `[8,10,8]`; `/changed_refusal/value/reason=warm_business_binding`. `/expired/@tuple/1/@tuple/0=reuse_certificate_expired`; `/wrong_root/@tuple/1/@tuple/0=drs_root_decision_binding_invalid`.

`checked.json`: domain_executions=[1,0], host_work=[1,0], warm_roots=2, action_effects=0. `cold.observation.json` counts domain_executor=1, host_work=1; `warm.observation.json` counts read=1, root=2. Both state CURRENT_PROCESS_CURRENT_THREAD_ONLY and children UNOBSERVED_NOT_ZERO. The two Root calls are observed calls, not a claim of two distinct policy owners or two grants. Cold Root review/writeback occur outside the cold observed native-work closure; durations would therefore be unlike-for-like even before other overhead.

Source: `demo/run_gate6_retained_obligations_v01.py::collect_reuse` line 250; `business_binding` line 235; `warm_consume` line 244; `shortcut` line 194; `check_reuse` line 501. `shortcut` builds current query/evaluation/rank, a summary-only retrieval plan and current Root-bound shortcut projection/certificate, then validates it. It does not dispatch a domain executor.

Arithmetic source: `hedgehog/external_drs/gate5_contracts_v01.py::calibration` line 55 and `rational` line 35; `hedgehog/external_drs/gate5_native_v01.py::execute_calibration_v01` line 216 -> `execute_values`/`compute_values`; `validate_math_output_v01`. Exact ints exclude bool; 1..8 observations; arithmetic checked against the profile's integer bound; rational denominator >0 and gcd-reduced. No physical unit is declared for this controlled input, so do not label it Celsius or another invented measurement.

Check-source-only: `tests/test_gate6_retained_obligations_v01.py::test_reuse_actual_binding_and_arithmetic` changes business, answer, counter or warm Root; `test_supplied_positive_no_new_runtime` consumes all four witness families without recollection. The supplied checker is a route for a later authorised reviewer, not a command executed here.

## S09: N4-05 Current Policy and Restricted Descent

Resource keys `finite/policy/{witness,checked,collection_receipt}.json` resolve to `docs/gate6_reference_v01/evidence/retained_obligations/policy/`. Witness SHA-256 `e97b645b4d5aad785fc9e60a8743e1be1ed938463784059dba31f21a9676f520`; checked SHA-256 `c64dee25b07ed1e1e528dbe242992d21d8ab43874eca09fdadb8d6ec52fff5d4`.

Checked fields: current_record `drsmeaning_v01:a3b6b4727137283a9057070714634f5ff6ae158c7df7b4f999c12ddcd121eb33`; successor_writes=1; predecessor_historically_valid=true; replaced_current_use=REFUSED; restricted_descent=REFUSED; summary_bytes=0; exact_failed_geometry=IDENTICAL. Source collection uses explicit logical time 1790503615, successor creation 1790503617, not a claim of current real-world travel policy.

Source `demo/run_gate6_retained_obligations_v01.py`: `current_policy_id` line 297 validates the two-record store, Root writeback geometry and replacement edge; `current_policy_consume` line 315 first validates the old certificate as historical evidence, then separately reviews whether its record is the current tip; `descent_case` line 334 uses explicit pointer-access checks; `check_policy` line 537 checks source/policy/returned-summary relations. The payload origin is CONTROLLED_IN_MEMORY_NOT_EXTERNAL_READ.

Tests: `test_policy_independent_current_derivation` changes lineage, derived current ID, old certificate or returned summary. Do not relabel the local closed-store policy as global DRS latest-record discovery, external revocation service or universal caching.

## S10: High Score Does Not Supply Permission

Resource `finite/avf/checked.json` -> `docs/gate6_reference_v01/evidence/retained_obligations/avf/checked.json`: high_avf=1.0, invalid_builders=2, mock_effects=1, new_authority_restored=false, row N1-05. Class: retained-current-source-witness.

`demo/run_gate6_retained_obligations_v01.py::collect_avf` line 108 and `check_avf` line 467 distinguish rejected high-score construction, a separately valid Root path with one mock effect, and missing permission with no additional effect. `tests/test_gate6_retained_obligations_v01.py::test_avf_actual_bindings` checks candidate, Root, state and counters. Root law remains in `hedgehog/kernel/root_decision_v01.py::decide_root_v01`; effect ownership remains `hedgehog/kernel/effect_firewall_v01.py`. Score is not permission.

## S11: Nested Work and Memory: What Is Actually Supported

Source `hedgehog/kernel/work_composition_v01.py`, SHA-256 `1f068c0d1156a312f36a7e55b7cbaf0e3e84503168b3305e10420bd8e3d3cbf0`:

- `WorkOutputBindingV01` line 26 and `_inputs` line 382 bind a producer's actual typed field to a consumer.
- `WorkHistoricalOutputV01` line 33, `_historical_value` line 1104 and `build_work_historical_output_v01` line 1132 bind task/revision/invocation/result/admission/artifact/output type and actual value. A data edge can disappear only when its exact retained result replaces it (revision check around line 985).
- `observe_missing_pure_need_v01` line 1042 requires an actual NEEDS_CAPABILITY observation without invocation/result, resolves the item's actual input and binds need to task/revision/topology/source. This is a continuation-internal need, not merely initial prompt retrieval.
- `execute_work_task_review_v01` line 1355 reserves the whole source-policy child ceiling before review; it records actual children and releases unused reservation. No refund of already consumed work.

Source `hedgehog/capability_memory_binding_v01.py`, SHA-256 `6e4f2ca3be12a1e9a93d7b59318d9a6ba90ea6f43bbd9bccc81d8bdefe1b1b79`:

- `search_pure_need_v01` line 41 uses current Host time, semantic terms integer/affine/u8, exact contract/multiplier/offset/memory scope/owner/profile filters, max_candidates=4 and Root-review-required. It reserves and charges local DRS bytes.
- `retrieve_pure_memory_v01` line 282 rejects stale/ambiguous candidates, performs current temporal/ranking checks, constructs a one-record/one-artifact/depth-1 budget, obtains a Root-reviewed OPEN_ONE_ARTIFACT request, reads bounded payload, validates public descent/hash, and calls `admit_pure_candidate_v01` again. Discovery is not installation or executable authority.
- `validate_pure_memory_retrieval_v01` line 379 checks current need, binding, actual descent and independent readmission.

Executed-mechanism evidence status: `docs/common_action_and_dynamic_composition_checkpoint_v01.md` reports historical U3 cold generation1/warm generation0 with local DRS rediscovery and independent readmission, and U4 retained native/legacy x child0/child1 cases. Those are checkpoint-reported historical executions; this worker did not locate/revalidate a raw U3 runtime archive and does not claim a new observation. The old contract's Contract Only status is a historical predecessor, not the current implementation inventory.

Read check sources:

- `tests/test_work_continuation_and_reuse_v01.py::test_u3_cold_warm_actual_same_task_and_canonical_report`: cold and warm each resume their own existing task; no claim they are the same task as each other. Actual need output reaches render input; retrieval Root ACCEPT creates no permission.
- `test_u3_history_membership_and_no_live_callback_replay`: historical field inspection has no executor callback or Host mutation.
- `tests/test_work_composition_v01.py::test_u2_r02_actual_recursive_review_child_accounting` line 1580: actual recursive review and cumulative child accounting.
- Retained recomputation assertions around lines 933-943: one retained consumption, two newly returned cell results (fresh child and parent), no new queue entry for retained child, canonical parent child-result order.

Disposition: implemented bounded nested review + retained child output consumption; implemented Work-internal pure-need memory retrieval/continuation. Their arbitrary recursive combination as child-local autonomous DRS search is NOT_DEMONSTRATED by these targeted sources. Do not draw a recorded child->memory edge without a concrete trace. A conceptual diagram may connect these mechanisms with that label. The no-world-I/O pure/Wasm profile does not imply sandboxing for arbitrary native plugins.

## S12: Deferrals and Non-Claims

`acceptance_matrix.json /rows` exact approved deferments: N1-18 Factory candidate-only; N1-19 Marennya/UP quarantine-first; N4-12 NeedleFactory; N4-13 Marennya/UP. Existing generic non-promotion controls do not implement those programmes.

`docs/gate4_reference_contract_v01.md` H6/H7/H10 preserve advanced-profile deferrals: unilateral regret/stability, robust/minimax/CVaR/sensitivity, LGT. FullAVF, StrongGT and unqualified RC4 are not claimed. The matrix's N4-09 title Strong GT negotiation has only SATISFIED_BOUNDED_REFERENCE disposition; it must not be expanded to full StrongGT.

`docs/gate6_reference_v01/FINITE_COMPLETION.md` and `BOUNDARY_AND_FINDINGS.md` state finite witness/observer limits, no whole-profile inference, and historical source-view separation. Current accepted admission is not production security certification.

## Editorial Routing for Main

- CASE-G3G4 / GEO-6: chapter throughout; numerical insets 1 and 2; S02-S10.
- GEO-4 with GEO-3: renewed history descent, two-record current policy, current time versus history; S06/S08/S09.
- GEO-1 with GEO-4: bounded internal Work need and retained child output; S11; explicitly conceptual generalisation for arbitrary child-local search.
- GEO-2: independent Root decisions, scores never permission; S03/S07/S10.
- Preserve diagram instance identities within each source. The G36 Supplier, G4 Airline and G6A calibration/policy cases are distinct; cross-case correspondence is interpretation, not one recorded timeline.
- Global framing and the three original-source arguments are delegated separately in `original_arguments_disposition.md`; no global outline or semantic-map completion is claimed by this worker.
