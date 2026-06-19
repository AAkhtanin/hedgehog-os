# Full Suite Drift Triage / Repair v0.1 — Read-only Preflight

## 1. Status

* preflight_id: full_suite_drift_triage_preflight_v01
* preflight_status: COMPLETE
* latest_checkpoint_commit: f9b5731
* full_pytest_status: FAIL
* full_pytest_failed: 25
* full_pytest_passed: 1667
* full_pytest_warnings: 60
* repair_started: false
* runtime_modified: false
* schemas_modified: false
* tests_modified: false
* skips_added: false
* xfails_added: false
* full_suite_green_claimed: false
* production_ready_claimed: false
* public_auditor_ready_claimed: false

## 2. Scope

This is a read-only triage. It does not repair anything yet.

Inputs inspected:

* `_audit_exports/full_pytest_output.txt`
* targeted failing test subset covering canonical pipeline, Root-native canonical traces, Root DAG integration/audit, live Gemini smoke layers, ordered live Gemini smoke, and Controlled Orchestrator Matrix Gate
* relevant tests, demo collectors, RootOrchestrator, Post V&V, GTValidator, FinalRenderer, and Fractal DAG Executor code paths

Local `_audit_exports/` is personal audit evidence only and must not be committed.

Read-only diagnostics run:

* `git status --short --untracked-files=all`
* `tail -n 160 _audit_exports/full_pytest_output.txt`
* `rg -n "FAILED|AssertionError|needs_user|no_update|SKIPPED|FAIL|completed_reports|root_native_full_canonical_e2e_trace_status|live_gemini_.*_status|gt_decision|final_status" _audit_exports/full_pytest_output.txt`
* targeted pytest subset covering the failing canonical, Root DAG, live Gemini, ordered live Gemini, and matrix gate files

Focused diagnostic result:

* targeted_subset_status: FAIL
* targeted_subset_failed: 25
* targeted_subset_passed: 123
* targeted_subset_warnings: 2

## 3. Failure Inventory

All 25 failed tests observed in `_audit_exports/full_pytest_output.txt` and reproduced by targeted diagnostics:

| # | test file | test name | expected value | actual value | immediate assertion category | likely cluster |
| - | --------- | --------- | -------------- | ------------ | ---------------------------- | -------------- |
| 1 | `tests/test_canonical_pipeline_trace_runner.py` | `test_root_creates_final_output_and_preserves_authority` | `final_status == success` | `needs_user` | Root final status | Cluster A |
| 2 | `tests/test_canonical_pipeline_trace_runner.py` | `test_post_vv_runs_before_gt_and_gt_accepts` | `completed_reports > 0`, then GT `accept` | `completed_reports == 0` | Post V&V completed reports | Cluster B |
| 3 | `tests/test_controlled_orchestrator_matrix_gate_runner.py` | `test_ordered_live_gemini_context_verifies_success_report` | `ordered_live_roles_preserved is true` | `false` | Ordered live context marker / boundary drift | Cluster F |
| 4 | `tests/test_live_gemini_architect_smoke_runner.py` | `test_live_mode_requires_explicit_gate_and_config` | `live_gemini_architect_smoke_status == SKIPPED` | `FAIL` | Live smoke skip/status propagation | Cluster D |
| 5 | `tests/test_live_gemini_architect_smoke_runner.py` | `test_missing_live_config_skips_not_crashes` | `live_gemini_architect_smoke_status == SKIPPED` | `FAIL` | Live smoke missing config gating | Cluster D |
| 6 | `tests/test_live_gemini_architect_smoke_runner.py` | `test_invalid_artifact_path_is_contained` | `live_gemini_architect_smoke_status == PASS` | `FAIL` | Invalid artifact containment summary | Cluster D |
| 7 | `tests/test_live_gemini_architect_smoke_runner.py` | `test_boundaries_are_preserved` | `avf_boundary_preserved is true` | `false` | Boundary propagation from full canonical E2E | Cluster D |
| 8 | `tests/test_live_gemini_architect_smoke_runner.py` | `test_full_canonical_e2e_collector_is_consumed` | source `root_native_full_canonical_e2e_trace_status == PASS` | `FAIL` | Full canonical E2E dependency | Cluster C / D |
| 9 | `tests/test_live_gemini_architect_smoke_runner.py` | `test_ready_for_future_orchestrator_live_smoke_requires_boundaries_and_containment` | readiness `true` | `false` | Readiness derived from degraded dependency | Cluster D |
| 10 | `tests/test_live_gemini_orchestrator_smoke_runner.py` | `test_live_mode_requires_explicit_gate_and_config` | `live_gemini_orchestrator_smoke_status == SKIPPED` | `FAIL` | Live smoke skip/status propagation | Cluster D |
| 11 | `tests/test_live_gemini_orchestrator_smoke_runner.py` | `test_missing_live_config_skips_not_crashes` | `live_gemini_orchestrator_smoke_status == SKIPPED` | `FAIL` | Live smoke missing config gating | Cluster D |
| 12 | `tests/test_live_gemini_orchestrator_smoke_runner.py` | `test_invalid_proposal_path_is_contained` | `live_gemini_orchestrator_smoke_status == PASS` | `FAIL` | Invalid proposal containment summary | Cluster D |
| 13 | `tests/test_live_gemini_orchestrator_smoke_runner.py` | `test_boundaries_are_preserved` | `avf_boundary_preserved is true` | `false` | Boundary propagation from full canonical E2E | Cluster D |
| 14 | `tests/test_live_gemini_orchestrator_smoke_runner.py` | `test_full_canonical_e2e_collector_is_consumed` | source `root_native_full_canonical_e2e_trace_status == PASS` | `FAIL` | Full canonical E2E dependency | Cluster C / D |
| 15 | `tests/test_live_gemini_orchestrator_smoke_runner.py` | `test_ready_for_future_controlled_orchestrator_integration_requires_boundaries_and_containment` | readiness `true` | `false` | Readiness derived from degraded dependency | Cluster D |
| 16 | `tests/test_live_gemini_ordered_orchestrator_architect_smoke_runner.py` | `test_invalid_architect_output_is_contained_if_injected` | ordered smoke status `PASS` | `FAIL` | Ordered invalid artifact containment summary | Cluster D |
| 17 | `tests/test_live_gemini_ordered_orchestrator_architect_smoke_runner.py` | `test_full_canonical_e2e_source_consumed` | source `root_native_full_canonical_e2e_trace_status == PASS` | `FAIL` | Full canonical E2E dependency | Cluster C / D |
| 18 | `tests/test_live_gemini_ordered_orchestrator_architect_smoke_runner.py` | `test_pass_summary_derived_from_structured_facts` | ordered smoke status `PASS` | `FAIL` | Summary readiness derived from degraded dependency | Cluster D |
| 19 | `tests/test_root_dag_drs_audit_runner.py` | `test_work_record_content_contains_root_native_dag_trace_fields` | `gt_decision == accept` | `no_update` | Root DAG work content GT decision | Cluster E / B |
| 20 | `tests/test_root_dag_drs_audit_runner.py` | `test_work_record_provenance_contains_route_engine_plan_and_trace` | provenance `gt_decision == accept` | `no_update` | Root DAG provenance GT decision | Cluster E / B |
| 21 | `tests/test_root_dag_integration_runner.py` | `test_opt_in_dag_route_uses_fractal_dag_executor_and_root_commits` | `gt_report.decision == accept` | `no_update` | Root DAG GT decision | Cluster E / B |
| 22 | `tests/test_root_native_canonical_trace_runner.py` | `test_post_vv_and_gt_order_is_visible` | `gt_decision == accept` | `no_update` | Root-native canonical GT decision | Cluster B |
| 23 | `tests/test_root_native_canonical_trace_runner.py` | `test_root_receives_dag_artifacts_and_creates_final_output` | `final_status == success` | `needs_user` | Root-native canonical final status | Cluster A |
| 24 | `tests/test_root_native_full_canonical_e2e_trace_runner.py` | `test_first_run_canonical_path_has_nine_stages` | all first-run stages `PASS` | at least one first-run stage `FAIL` | Root-native canonical E2E aggregate | Cluster C |
| 25 | `tests/test_root_native_full_canonical_e2e_trace_runner.py` | `test_post_vv_is_before_gt_and_gt_after_post_vv` | GT stage `PASS` | `FAIL` | Root-native canonical E2E GT stage | Cluster C / B |

## 4. Failure Clusters

### Cluster A — Root final status expectation drift

Examples:

* final_status expected `success`
* actual `needs_user`

Observed evidence:

* RootOrchestrator maps GT `no_update` to Root final `needs_user`.
* FinalRenderer maps GT `no_update` to `needs_user`.
* Canonical and Root-native canonical tests still expect optimistic `success`.

Questions:

* Is `needs_user` now correct under stricter Post V&V / GT behavior?
* Does old E2E test need semantic update?
* Or did ResultProposal become malformed and force needs_user incorrectly?

### Cluster B — Post V&V completed reports / GT decision drift

Examples:

* completed_reports expected `> 0`, actual `0`
* gt_decision expected `accept`, actual `no_update`

Observed evidence:

* Post V&V returns reports, but none are accepted/completed in the canonical path.
* GTValidator returns `no_update` when there are no accepted completed candidates.
* Fractal DAG proposals include child boundary snapshots and needs-revision semantics that may no longer satisfy completed acceptance criteria.

Questions:

* Is `no_update` now correct because no completed ResultProposal passes Post V&V?
* Is Post V&V too strict?
* Is Fractal DAG proposal shape missing completion fields?
* Is GT interpreting validated-but-not-completed proposals correctly?

### Cluster C — Root-native canonical E2E dependency failure

Examples:

* root_native_full_canonical_e2e_trace_status expected `PASS`, actual `FAIL`
* GT stage expected `PASS`, actual `FAIL`

Observed evidence:

* Full canonical E2E computes first-run stage status from Root-native canonical trace sections.
* Its GT first-run stage requires `gt_decision == accept`.
* Current upstream GT result is `no_update`, so the aggregate report correctly propagates `FAIL`.

Questions:

* Is this downstream of Cluster A/B?
* Is the E2E report correctly propagating failure?

### Cluster D — Live Gemini smoke status propagation

Examples:

* live smoke expected `PASS` / `SKIPPED`, actual `FAIL`
* missing live config expected `SKIPPED`, current summary reports `FAIL`
* live boundaries such as AVF/Post V&V/GT preservation derive false from full canonical E2E `FAIL`

Observed evidence:

* Architect, Orchestrator, and ordered Orchestrator-to-Architect smoke collectors consume the Root-native full canonical E2E report.
* Their boundary summaries require full canonical E2E status `PASS`.
* Missing live config only returns `SKIPPED` when upstream boundaries also pass; with full canonical E2E degraded, status becomes `FAIL`.

Questions:

* Are live smoke tests failing because their source full canonical E2E is `FAIL`?
* Should missing live config return `SKIPPED` even when dependency report is degraded?
* Is `FAIL` appropriate when live config missing but deterministic fallback works?

### Cluster E — Fractal DAG / Root DAG contract drift

Examples:

* gt_decision expected `accept`, actual `no_update`
* Root DAG work record provenance expects `accept`

Observed evidence:

* Root DAG integration uses the real RootOrchestrator opt-in Fractal DAG route.
* Fractal DAG Executor returns ResultProposal-shaped outputs.
* Post V&V/GT currently produce no accepted completed winner, so work content/provenance record `gt_decision: no_update`.

Questions:

* Does Fractal DAG ResultProposal still match current schema and Post V&V criteria?
* Are evidence kinds valid but completion status not accepted?
* Is Root committing correct safe output?

### Cluster F — Controlled Orchestrator Matrix Gate context drift

Examples:

* ordered_live_roles_preserved expected `true`, actual `false`

Observed evidence:

* Controlled Orchestrator Matrix Gate verifies ordered live Gemini success-report markers.
* The required markers include ordered smoke status `PASS`.
* Current ordered smoke status is `FAIL`, downstream of Root-native full canonical E2E dependency degradation.

Questions:

* Is this a stale success-report marker check?
* Is it downstream of live/canonical failure?

Cluster classification summary:

| cluster | primary classification | secondary classification | current triage status |
| ------- | ---------------------- | ------------------------ | --------------------- |
| Cluster A | Root final status semantic change | stale test expectation or real runtime regression | unknown, requires Phase 1 proof |
| Cluster B | Post V&V acceptance criteria mismatch / GT semantic change | possible ResultProposal shape mismatch | unknown, requires focused reproduction |
| Cluster C | Root-native canonical E2E dependency failure | downstream of Cluster A/B | likely propagated failure |
| Cluster D | live smoke dependency propagation issue | environment/config gating issue for missing live config | likely propagated plus gating policy drift |
| Cluster E | Fractal DAG / Root DAG contract drift | possible schema/ResultProposal shape mismatch or Post V&V criteria mismatch | unknown, requires focused reproduction |
| Cluster F | controlled matrix ordered-live context drift | stale success-report marker check or downstream live/canonical failure | likely propagated failure |

## 5. Hypothesis Ranking

These are hypotheses, not facts:

1. Post-hardening expectation drift after stricter ResultProposal / Post V&V boundary.
2. GT semantics changed from optimistic accept to no_update when proposals are not completed/accepted.
3. Root final status changed from optimistic success to needs_user when GT/Post V&V cannot accept completion.
4. Live Gemini smoke tests propagate full canonical E2E failure instead of cleanly SKIPPING missing config.
5. Fractal DAG proposal shape or status semantics may not satisfy current Post V&V completion criteria.

Current likely dependency chain:

`Fractal DAG ResultProposal semantics / Post V&V acceptance`
-> `GT no_update`
-> `Root needs_user`
-> `Root-native full canonical E2E FAIL`
-> `live Gemini smoke FAIL`
-> `Controlled Orchestrator Matrix Gate ordered-live context drift`

## 6. Sterile Repair Principles

* Do not hide failures.
* Do not skip or xfail tests just to make the suite pass.
* Do not force success.
* Do not force accept.
* Do not mass replace `success` with `needs_user`.
* Do not mass replace `accept` with `no_update`.
* Do not relax schema contracts without a separate schema patch plan.
* Do not weaken Post V&V.
* Do not allow live Gemini to bypass deterministic fallback and boundary checks.
* Preserve Root final authority.
* Preserve Post V&V boundary.
* Preserve GT semantics.
* Preserve schema contracts.
* Preserve hardening layers.

## 7. Proposed Repair Order

### Stage 1 — canonical minimal trace facts

* inspect current actual structured outputs
* decide whether `needs_user` / `no_update` are correct or regression
* patch either runtime semantics or test expectations, but only after proof

### Stage 2 — ResultProposal / Post V&V / GT alignment

* verify Fractal DAG ResultProposal shape
* verify Post V&V completion criteria
* verify GT decision semantics
* update narrow code/tests accordingly

### Stage 3 — Root-native canonical E2E

* repair source E2E after Stage 1/2
* avoid patching downstream smoke first

### Stage 4 — live Gemini smoke gating

* ensure missing config returns SKIPPED when appropriate
* ensure dependency failure is reported as dependency_degraded or fail intentionally
* preserve no network use unless explicitly live opt-in

### Stage 5 — full suite proof

* rerun targeted failing files
* then rerun full pytest
* expected final target: zero failures, with all non-deprecated warnings understood

## 8. Recommended Next Patch

Recommended next real patch:

Full Suite Drift Repair Phase 1 — Canonical Status / GT / Post V&V Alignment

Allowed only after this preflight is reviewed.

Initial repair focus should be narrow:

* canonical pipeline actual structured output
* Fractal DAG ResultProposal completion semantics
* Post V&V accepted/completed criteria
* GT `accept` versus `no_update` semantics
* Root final `success` versus `needs_user` semantics

Live Gemini smoke and Controlled Orchestrator Matrix Gate should be treated as downstream until the canonical source report is understood.

## 9. Non-goals

* no new architecture layer
* no production DRS
* no external/global DRS
* no Marennya/UP
* no Negative Trace
* no artifact_type vocabulary work
* no public auditor packet
* no whitepaper
* no broad refactor
* no full pytest rerun inside this preflight
* no test expectation update inside this preflight
* no skip or xfail addition inside this preflight
