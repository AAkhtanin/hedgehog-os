# Schema Contract Alignment v0.1 Phase 2 - Executor / DAG ResultProposal Contract Patch Plan

## 1. Status

- status: patch_plan_only
- patch_applied: false
- schemas_modified: false
- runtime_modified: false
- tests_modified: false
- phase1_closed: true
- phase2_patch_not_started: true

This file is a reviewed patch plan only. It records read-only scan evidence for
the Executor / DAG ResultProposal contract before any Phase 2 patch.

Scan commands used:

```bash
rg -n "Executor.*ResultProposal|returns ResultProposal|ResultProposal only|ResultProposal-shaped|DAG.*ResultProposal|Fractal DAG.*ResultProposal|node.*ResultProposal|execute_plan_graph|FractalDagExecutor|DAG runner" hedgehog demo tests schemas specs docs README.md AGENTS.md
rg -n "Architect.*PlanGraph|Architect.*ResultProposal|Executor.*PlanGraph|Executor.*ResultProposal|PlanGraph.*ResultProposal|AttractorPacket|must_return_plan_graph_only|must_return_result_proposals_only" hedgehog demo tests schemas specs docs README.md AGENTS.md
rg -n "raw Architect PlanGraph|raw Executor text|raw ResultProposal|Post V&V rejects|rejects raw|malformed ResultProposal|ValidationReport|ResultProposal boundary|Post V&V" tests demo hedgehog specs docs README.md AGENTS.md
rg -n "test_.*executor|test_.*dag|test_.*result_proposal|test_.*post_vv|execute_plan_graph|fractal_dag|ResultProposal" tests
```

Files read in context:

- `hedgehog/executor.py`
- `hedgehog/fractal_dag_executor.py`
- `hedgehog/post_vv.py`
- `tests/test_executor_runtime.py`
- `tests/test_dag_executor_from_valid_plan_graph_runner.py`
- `tests/test_fractal_dag_executor_core_runner.py`
- `tests/test_post_vv_from_result_proposal_runner.py`
- `schemas/result_proposal.schema.json`
- `schemas/plan_graph.schema.json`
- `specs/schema_package_v0_25_reference.md`
- `specs/invariants.md`
- `specs/human_passport_v0_25.md`
- `docs/schema_contract_alignment_preflight_v01.md`
- `docs/audit_reports/auditor_schema_contract_alignment_phase1_attractor_packet_v01.log`

## 2. Context

Phase 1 aligned the Architect-facing AttractorPacket contract with PlanGraph:
the active AttractorPacket schema/runtime now uses `must_return_plan_graph_only`.

Phase 2 should align and clarify the downstream Executor / DAG ResultProposal
contract wording and tests. This plan must be reviewed before any patch.

Phase 2 is not Post V&V JSON Schema hardening. Phase 2 is not
EvidenceItem.kind vocabulary work. Phase 2 is not artifact_type vocabulary work.
Phase 2 is not production validation.

## 3. Canonical Baseline

- Architect returns PlanGraph only.
- Executor returns ResultProposal only.
- Fractal DAG / DAG runner returns ResultProposal-shaped outputs only.
- Node-level executor outputs must be wrapped or validated before Post V&V.
- Post V&V consumes the ResultProposal boundary.
- GT consumes ValidationReport / V&V output and is advisory.
- Root creates FinalOutput.
- No role collapse.

## 4. Current Evidence From Scan

Files that already correctly state the Executor contract:

- `AGENTS.md`: says Executors return ResultProposal only and Fractal DAG may
  return ResultProposal-shaped outputs and child boundary snapshots.
- `README.md`: says Executors return ResultProposal only and DAG runner returns
  ResultProposal-shaped artifacts / boundary snapshots.
- `specs/invariants.md`: says Executor receives only validated PlanGraph nodes,
  creates ResultProposal, and does not create FinalOutput, write DRS directly,
  or execute real external actions.
- `specs/human_passport_v0_25.md`: says Executor receives a plan node and
  returns ResultProposal.
- `specs/schema_package_v0_25_reference.md`: now warns that Architect must
  return PlanGraph and Executors / DAG runner return ResultProposal-shaped
  outputs.
- `docs/audit_reports/auditor_schema_contract_alignment_phase1_attractor_packet_v01.log`:
  records the Phase 1 separation: Architect returns PlanGraph only; Executor /
  DAG returns ResultProposal.

Runtime files observed:

- `hedgehog/executor.py`: `execute_plan_graph()` calls `execute_node()` and
  returns active-schema ResultProposal dictionaries with `proposal_id`,
  `producer`, `vector_id`, `plan_id`, `result_payload`, `evidence`, `cost`,
  `risks`, `time_envelope`, and `trace_refs`.
- `hedgehog/fractal_dag_executor.py`: `run_fractal_dag_executor()` returns
  RunnerReport data containing `result_proposals`; atomic nodes and non-atomic
  child-boundary snapshots are represented as ResultProposal-shaped dictionaries
  with no FinalOutput and no real external action.
- `hedgehog/post_vv.py`: `validate_result_proposal()` performs deterministic
  boundary checks over required ResultProposal fields, forbidden root/user-facing
  keys, evidence presence, TimeEnvelope fields, risk severity, consistency, and
  payload semantics.

Existing tests that verify Executor ResultProposal schema:

- `tests/test_executor_runtime.py::test_execute_plan_graph_returns_schema_valid_result_proposals`
  validates active Executor outputs against `schemas/result_proposal.schema.json`.
- `tests/test_post_vv_runtime.py` validates runtime Post V&V output over
  Executor-produced proposals.
- `tests/test_gt_validator_runtime.py` consumes Executor proposals through the
  GT runtime path.

Existing tests that verify DAG ResultProposal-shaped outputs:

- `tests/test_dag_executor_from_valid_plan_graph_runner.py` proves valid
  PlanGraph inputs create ResultProposal rows and invalid/raw inputs are blocked
  before Executor.
- `tests/test_fractal_dag_executor_core_runner.py` proves Fractal DAG scenarios
  create ResultProposal-shaped dictionaries with TimeEnvelope data, child
  boundary snapshots for non-atomic nodes, no FinalOutput, and no real external
  action.

Existing tests that verify Post V&V boundary rejection:

- `tests/test_post_vv_from_result_proposal_runner.py` verifies Post V&V blocks
  raw Executor text, raw PlanGraph from Architect, raw Orchestrator matrix, raw
  user intent, real action output, malformed ResultProposal, malicious
  FinalOutput claims, and malicious DRS write claims.

Existing tests that verify downstream authority:

- `tests/test_gt_from_validation_report_runner.py` verifies GT blocks raw
  ResultProposal, raw Executor text, and raw PlanGraph from Architect, and GT
  does not create FinalOutput.
- `tests/test_root_final_from_gt_decision_runner.py` verifies Root Final blocks
  raw ValidationReport, raw ResultProposal, raw Executor text, and raw PlanGraph
  from Architect, and Root creates the final artifact.

Unclear wording or gaps found:

- No runtime behavior drift was found in the active Executor path.
- The public wording alternates between `ResultProposal` and
  `ResultProposal-shaped`. That distinction is valid, but should be made more
  explicit: active `hedgehog/executor.py` emits schema-valid ResultProposal
  objects, while proof-level DAG / child-cell reports may use
  ResultProposal-shaped boundary artifacts until a later normalization layer.
- Node-level executor outputs and child boundary snapshots are safe in the
  current proofs, but the wording should say they are internal or boundary
  artifacts until wrapped into a parent ResultProposal path before Post V&V.
- Existing behavior tests are broad enough for current runtime behavior. A
  wording pin test is optional if the reviewed Phase 2 patch changes docs/spec
  contract text in a way that should be mechanically guarded.

## 5. Proposed Phase 2 Patch Scope

Patch scope should be narrow.

Allowed future patch targets may include, depending on review:

- `specs/schema_package_v0_25_reference.md`
- `specs/invariants.md`
- `specs/human_passport_v0_25.md`
- `specs/demo_baseline_v0_25.md`
- `docs/passport_geometry_root_needles.md`
- `docs/strategic_expansion_map.md`
- `tests/test_executor_runtime.py`
- `tests/test_dag_executor_from_valid_plan_graph_runner.py`
- `tests/test_fractal_dag_executor_core_runner.py`
- `tests/test_post_vv_from_result_proposal_runner.py`

Runtime code should not be changed unless a future review identifies actual
behavior drift. This scan did not find such drift.

Schema changes are not recommended for Phase 2 unless review finds a precise
description-only patch in `schemas/result_proposal.schema.json` is needed. A
structural schema overhaul belongs to a later reviewed phase.

## 6. Proposed Future Patch Steps

Phase 2 patch should:

1. Add or strengthen docs/spec wording:
   - Executor returns ResultProposal only.
   - Fractal DAG returns ResultProposal-shaped outputs only.
   - Architect PlanGraph and Executor ResultProposal are separate contracts.
   - Child cell / node outputs are not Root Final and must flow through parent
     ResultProposal / Post V&V / GT / Root.
2. Add focused tests only if review finds a missing guard:
   - Executor output validates against `result_proposal.schema.json`.
   - DAG / Fractal DAG output is ResultProposal-shaped and not FinalOutput.
   - Post V&V rejects raw PlanGraph.
   - Post V&V rejects raw Executor text.
   - GT cannot consume raw PlanGraph or raw Executor text.
   - Root Final remains Root-only.
3. Keep non-goals explicit:
   - no Post V&V JSON Schema hardening yet
   - no EvidenceItem.kind vocabulary changes yet
   - no artifact_type mapping changes yet

## 7. Risks

- role_collapse_risk: low
- public_contract_ambiguity_risk: medium
- runtime_behavior_drift_found: false
- tests_missing_for_contract: false
- optional_wording_pin_test_useful: true
- patch_needed_before_public_auditor_packet: true

Risk notes:

- Runtime behavior already follows the role split.
- Public wording should more clearly separate schema-valid active Executor
  ResultProposal from proof-level ResultProposal-shaped boundary artifacts.
- The next patch should avoid expanding into Post V&V JSON Schema hardening or
  evidence/artifact vocabulary alignment.

## 8. Non-goals

This plan does not:

- patch schemas
- patch runtime
- patch tests
- implement Post V&V JSON Schema validation
- change EvidenceItem.kind
- change artifact_type
- claim production readiness
- claim public-auditor readiness
- claim every schema-hardening phase is done

## 9. Recommended Next Patch

Recommended Phase 2 patch:

- docs/spec wording patch first, because no runtime behavior drift was found.
- clarify active Executor ResultProposal versus proof-level DAG
  ResultProposal-shaped boundary artifacts.
- preserve the existing tests as the behavior evidence.
- optionally add one focused wording/contract test only if review decides the
  docs/spec contract should be mechanically pinned.
- defer Post V&V JSON Schema validation, EvidenceItem.kind vocabulary work, and
  artifact_type vocabulary work to later phases.

Do not start with a broad fix. Do not alter runtime behavior unless review
identifies a concrete behavior gap.

## 10. Summary

- schema_contract_alignment_phase2_plan_v01_status: COMPLETE
- patch_plan_only: true
- patch_applied: false
- phase1_closed: true
- phase2_patch_started: false
- executor_resultproposal_contract_scan_complete: true
- architect_executor_boundary_scan_complete: true
- post_vv_boundary_scan_complete: true
- recommended_next_patch_requires_user_approval: true
- runtime_jsonschema_hardening_deferred: true
- evidence_kind_alignment_deferred: true
- artifact_type_alignment_deferred: true
- production_ready_claimed: false
- public_auditor_ready_claimed: false
- runtime_behavior_drift_found: false
- tests_already_cover_behavior: true
- recommended_next_patch: docs/spec wording patch, optional focused wording pin test after review
