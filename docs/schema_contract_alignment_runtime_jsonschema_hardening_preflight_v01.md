# Runtime JSON Schema Validation Hardening Preflight v0.1

## 1. Status

runtime_jsonschema_hardening_preflight_v01_status: COMPLETE
preflight_only: true
patch_applied: false
runtime_modified: false
schemas_modified: false
tests_modified: false
evidence_kind_alignment_implemented: false
artifact_type_alignment_implemented: false
production_ready_claimed: false
public_auditor_ready_claimed: false

This is a read-only preflight and patch plan. It adds no runtime code, changes no
schemas, changes no tests, and applies no Post V&V behavior change.

## 2. Context

Schema Contract Alignment v0.1 Phase 1 aligned the active AttractorPacket
Architect contract with PlanGraph-only output. Phase 2 clarified downstream
Executor / DAG ResultProposal wording without runtime, schema, or test changes.

This preflight starts Finding B: runtime validation gap. It inventories where
the runtime currently performs deterministic manual boundary validation, where
JSON Schema validation already exists in tests, and where a future minimal patch
should add runtime JSON Schema validation without rewriting the pipeline.

Read-only scan commands used:

- `git status --short`
- `rg -n "validate_result_proposal|ValidationReport|VVReport|Post V&V|post_vv|jsonschema|Draft|schema|result_proposal|malformed|required|forbidden|FinalOutput|DRS write|action" hedgehog tests schemas specs docs README.md AGENTS.md`
- `rg -n "jsonschema|Draft7Validator|Draft202012Validator|validate\(|RefResolver|schema_store|json.load|schemas/" hedgehog tests demo scripts specs docs README.md AGENTS.md`
- `rg -n "jsonschema|Draft7Validator|Draft202012Validator|validate\(|RefResolver|schema_store|json.load|schemas/" hedgehog tests demo specs docs README.md AGENTS.md`
- `rg -n "result_proposal.schema.json|ResultProposal|proposal_id|producer|vector_id|plan_id|result_payload|evidence|cost|risks|time_envelope|trace_refs" hedgehog tests schemas specs docs README.md AGENTS.md`
- `rg -n "vv_report.schema.json|VVReport|ValidationReport|validation_report|validation_status|accepted|rejected|degraded|blocked" hedgehog tests schemas specs docs README.md AGENTS.md`
- `rg -n "raw PlanGraph|raw Executor text|raw ResultProposal|malformed ResultProposal|malicious FinalOutput|DRS write|action claim|reject|blocked|Post V&V" tests`
- `sed -n` reads of the runtime, schema, test, and preflight files listed in this report.

Note: the requested scan path `scripts` is not present in this workspace, so the
JSON Schema usage scan was also rerun against existing paths.

## 3. Finding B Definition

Finding B is the runtime validation gap.

Current suspected gap:

- Post V&V performs deterministic manual boundary checks.
- Tests validate some artifacts against JSON schemas.
- Runtime does not appear to use full JSON Schema validation for incoming
  ResultProposal artifacts or outgoing VVReport / ValidationReport artifacts.
- A minimal future patch should add runtime JSON Schema validation where it
  belongs without weakening existing manual policy and safety checks.

JSON Schema validation must be additive. It must not replace manual safety
checks. It must not convert invalid data into valid data. It must not grant
authority. It must not create FinalOutput. It must not write DRS. It must not
execute actions.

## 4. Current Runtime Validation Evidence

Primary active runtime file:

- `hedgehog/post_vv.py`

Observed active Post V&V behavior:

- `validate_result_proposal()` deep-copies the input proposal.
- It checks required top-level ResultProposal fields using
  `REQUIRED_RESULT_PROPOSAL_FIELDS`.
- It checks evidence presence by requiring a non-empty `evidence` list.
- It checks TimeEnvelope presence by requiring `pt_created_at`, `kt_asof`,
  `ct_session_anchor`, and `ttl_seconds`.
- It checks critical risk severity by treating any risk with
  `severity == "critical"` as a safety failure.
- It checks forbidden root/user-facing keys recursively through
  `FORBIDDEN_KEYS = {"final_output", "answer", "raw_user_text"}`.
- It checks identifier and payload consistency through `proposal_id`,
  `vector_id`, `plan_id`, and `result_payload`.
- It derives payload semantics from `result_payload.status`,
  `task_completed`, `requires_human_input`, and `blocked_reason`.
- It maps active runtime decisions to `accepted`, `rejected`, or
  `needs_revision`.
- It creates a V&V report dictionary with scores, decision, violations,
  normalized features, trace refs, and optional request id.

Current manual checks by requested category:

- required top-level fields: present as manual set containment.
- evidence presence: present as manual non-empty list check.
- TimeEnvelope fields: present as manual required-field check.
- risk severity: present for `critical` risks.
- forbidden FinalOutput claims: present for the key `final_output`.
- forbidden DRS write claims: not explicit in active `hedgehog/post_vv.py`;
  proof-level boundary tests cover malicious DRS write claims.
- forbidden action claims: not explicit in active `hedgehog/post_vv.py`;
  proof-level boundary tests cover real action output before Post V&V.
- payload semantics: present for needs-user and blocked semantics.
- malformed proposal shape: partially present through required-field,
  evidence, TimeEnvelope, and consistency checks.
- accepted/degraded/rejected status mapping: active runtime maps to
  accepted/rejected/needs_revision; proof-level Post V&V uses accepted,
  degraded, and rejected validation reports.

No `jsonschema`, `Draft202012Validator`, or schema-store invocation was observed
inside `hedgehog/post_vv.py`.

Related runtime files read:

- `hedgehog/executor.py`: active Executor emits schema-valid ResultProposal
  objects for focused runtime tests.
- `hedgehog/fractal_dag_executor.py`: Fractal DAG runner emits
  ResultProposal-shaped boundary artifacts and RunnerReport data, with no
  FinalOutput and no real external action.
- `hedgehog/gt_validator.py`: GT consumes V&V report dictionaries and remains
  advisory.
- `hedgehog/root_orchestrator.py`: Root creates FinalOutput artifacts in the
  active root path.

## 5. Current Schema Validation Evidence

Active schemas read:

- `schemas/result_proposal.schema.json`
- `schemas/vv_report.schema.json`
- `schemas/common.schema.json`
- `schemas/time_envelope.schema.json`
- `schemas/plan_graph.schema.json`
- `schemas/final_output.schema.json`

Observed schema facts:

- `schemas/result_proposal.schema.json` requires `proposal_id`, `producer`,
  `vector_id`, `plan_id`, `result_payload`, `evidence`, `cost`, `risks`,
  `time_envelope`, and `trace_refs`.
- ResultProposal `producer` requires `executor_id` and disallows unknown
  producer fields.
- ResultProposal `result_payload` forbids `final_output` and `answer` keys.
- ResultProposal `evidence` items reference
  `common.schema.json#/$defs/EvidenceItem`.
- ResultProposal `risks` require `risk_id`, `severity`, and `description`, with
  severity limited to `low`, `medium`, `high`, or `critical`.
- ResultProposal `time_envelope` references `time_envelope.schema.json`.
- ResultProposal has `additionalProperties: false`.
- `schemas/vv_report.schema.json` requires `vv_report_id`, `proposal_id`,
  `status`, `scores`, `overall_score`, `decision`, and `checked_at`.
- VVReport status is limited to `accepted`, `rejected`, or `needs_revision`.
- VVReport decision is limited to `accept`, `reject`, or `revise`.
- VVReport violation kinds are limited to `schema`, `evidence`, `policy`,
  `time`, `safety`, `consistency`, or `forbidden_region`.
- `schemas/time_envelope.schema.json` requires the same four top-level fields
  that Post V&V checks manually and also defines allowed optional freshness /
  validity fields.
- `schemas/common.schema.json` defines a narrow `EvidenceItem.kind` enum. That
  vocabulary issue belongs to Finding C and is deferred here.

Schema validation already observed in tests:

- `tests/test_schema_files_valid.py` checks every `*.schema.json` file as Draft
  2020-12 JSON Schema.
- `tests/test_executor_runtime.py` validates active Executor outputs against
  `schemas/result_proposal.schema.json`.
- `tests/test_post_vv_runtime.py` validates runtime Post V&V output reports
  against `schemas/vv_report.schema.json`.
- `tests/test_gt_validator_runtime.py` validates GT report outputs against
  `schemas/gt_report.schema.json`.
- `tests/test_root_orchestrator_runtime.py` validates Root FinalOutput outputs
  against `schemas/final_output.schema.json`.
- `tests/test_architect_runtime.py` validates PlanGraph output against
  `schemas/plan_graph.schema.json`.

Boundary proof tests observed:

- `tests/test_post_vv_from_result_proposal_runner.py` verifies Post V&V blocks
  raw Executor text, raw Architect PlanGraph, raw Orchestrator matrix, raw user
  intent, real action output, malformed ResultProposal, malicious FinalOutput
  claims, and malicious DRS write claims.
- `tests/test_gt_from_validation_report_runner.py` verifies GT blocks raw
  ResultProposal, raw Executor text, raw Architect PlanGraph, raw Orchestrator
  matrix, raw user intent, real action output, malicious FinalOutput claims,
  DRS write claims, action claims, and malformed ValidationReport.
- `tests/test_root_final_from_gt_decision_runner.py` verifies Root Final blocks
  raw ValidationReport, raw ResultProposal, raw Executor text, raw Architect
  PlanGraph, raw Orchestrator matrix, raw user intent, real action output,
  malicious GT FinalOutput claims, DRS write claims, action claims, and
  malformed GTDecision.

## 6. Gap Analysis

result_proposal_runtime_schema_validation_present: false
vv_report_runtime_schema_validation_present: false
nested_time_envelope_runtime_schema_validation_present: false
schema_validation_in_tests_present: true
manual_policy_checks_present: true
additive_hardening_needed: true

What is already covered:

- Active Post V&V has deterministic manual checks for required top-level fields,
  evidence presence, TimeEnvelope required fields, critical risk, forbidden
  `final_output` / `answer` / `raw_user_text`, consistency, and needs-user /
  blocked semantics.
- Active tests validate Executor ResultProposal output against the active
  ResultProposal schema.
- Active tests validate Post V&V report output against the active VVReport
  schema.
- Proof-level tests exercise raw input rejection and malicious boundary claims
  across Post V&V, GT, and Root Final.

What is missing:

- Active Post V&V does not validate incoming ResultProposal dictionaries against
  `schemas/result_proposal.schema.json` at runtime.
- Active Post V&V does not validate nested TimeEnvelope, EvidenceItem, cost,
  risk, trace ref, producer, and additionalProperties constraints through the
  active schema at runtime.
- Active Post V&V does not validate outgoing VVReport / ValidationReport
  dictionaries against `schemas/vv_report.schema.json` before returning.
- Manual DRS/action claim checks are stronger in proof-level runners than in the
  active `hedgehog/post_vv.py` forbidden-key list.

The future patch should preserve all current manual safety checks and add schema
validation before and optionally after those checks.

## 7. Minimal Future Patch Proposal

Recommended patch shape:

1. Add a small runtime schema validation helper if no suitable helper exists.
2. Load active JSON schemas from `schemas/` with an explicit local schema store.
3. Validate incoming ResultProposal at the start of Post V&V.
4. Convert schema validation failures into the existing rejected V&V report
   shape without crashing downstream GT / Root paths.
5. Keep all existing manual checks after schema validation.
6. Preserve manual forbidden-key, semantic, risk, needs-user, blocked, DRS/action
   boundary checks.
7. Optionally validate outgoing VVReport / ValidationReport before returning, or
   keep that as a second subphase if the first patch should remain smaller.

Focused tests for the future patch:

- missing required ResultProposal field is rejected by schema validation.
- bad nested TimeEnvelope is rejected by schema validation.
- malformed EvidenceItem / risk / cost / trace refs are rejected by schema
  validation.
- extra top-level fields are rejected by schema validation.
- extra forbidden final/action/DRS claims remain rejected by manual checks.
- schema-valid but semantically unsafe proposal remains rejected or revised by
  manual checks.
- schema-valid safe proposal remains accepted.
- malformed proposal does not crash the GT / Root path.
- optional: outgoing VVReport shape validates before return.

This is a plan only. No patch is applied in this report.

## 8. Files Likely Affected By Future Patch

Likely:

- `hedgehog/post_vv.py`: add incoming ResultProposal runtime schema validation
  at the Post V&V boundary and preserve existing manual checks.
- `tests/test_post_vv_runtime.py`: add focused runtime tests for schema failure
  and manual safety failure composition.
- `tests/test_post_vv_from_result_proposal_runner.py`: add or preserve proof
  assertions if the future patch changes the failure explanation wording.

Optional:

- `hedgehog/schema_validation.py`: a tiny helper only if keeping schema loading
  out of `post_vv.py` materially reduces duplication.
- `tests/test_schema_files_valid.py`: no change expected, unless a helper needs
  a shared fixture or a new schema-store assertion.
- `tests/test_gt_from_validation_report_runner.py`: only if outgoing V&V report
  shape changes, which should be avoided.
- `tests/test_root_final_from_gt_decision_runner.py`: only if failure artifacts
  change, which should be avoided.

Not recommended for this future patch:

- `schemas/*.schema.json`: schema edits are not needed unless implementation
  reveals a precise schema defect.
- `hedgehog/executor.py`: active Executor output already validates in tests.
- `hedgehog/fractal_dag_executor.py`: proof-level ResultProposal-shaped output
  normalization belongs to a later focused layer if needed.
- `hedgehog/gt_validator.py`: GT hardening is downstream and should not be
  bundled with the first Post V&V boundary patch.
- `hedgehog/root_orchestrator.py`: Root authority should remain unchanged.

## 9. Non-goals

This preflight does not:

- implement runtime JSON Schema hardening
- change runtime
- change schemas
- change tests
- align EvidenceItem.kind
- align artifact_type
- claim production readiness
- claim public-auditor readiness
- close Finding C/D/E

## 10. Risks

runtime_validation_gap_risk: medium
schema_helper_complexity_risk: low
behavior_regression_risk: medium
overclaim_risk: medium
patch_needed_before_public_auditor_packet: true

Risk notes:

- Runtime validation gap risk is medium because the current proof boundary is
  safe, but public review will expect active runtime validation to use the
  active schemas at the boundary.
- Schema helper complexity risk is low if the helper is small, local, and
  read-only over repository schemas.
- Behavior regression risk is medium because `additionalProperties: false` and
  nested enum checks can reject artifacts that manual checks currently tolerate.
- Overclaim risk is medium because schema validation is a contract check, not an
  authority grant, production guarantee, or security proof.

## 11. Recommended Next Patch

recommended_next_patch: Post V&V ResultProposal runtime schema validation patch + focused tests

Recommended next step after review:

- Add Post V&V incoming ResultProposal JSON Schema validation at the runtime
  boundary.
- Keep existing manual checks and run them after schema validation.
- Convert schema failures to the existing rejected V&V report path.
- Add focused tests for missing fields, bad nested TimeEnvelope, malformed
  evidence/risk/cost/trace refs, forbidden claims, semantic unsafe-but-valid
  proposals, and safe accepted proposals.
- Treat outgoing VVReport validation as optional in the first patch or as a
  second subphase if keeping the first patch smaller is preferable.

Not recommended:

- broad runtime/schema rewrite.
- EvidenceItem.kind vocabulary changes.
- artifact_type vocabulary mapping.
- GT / Root / DRS changes.
- production validation claims.

## 12. Summary

runtime_jsonschema_hardening_preflight_v01_status: COMPLETE
finding_b_runtime_validation_gap_status: scoped_for_patch
preflight_only: true
patch_applied: false
runtime_modified: false
schemas_modified: false
tests_modified: false
result_proposal_runtime_schema_validation_present: false
vv_report_runtime_schema_validation_present: false
schema_validation_in_tests_present: true
manual_policy_checks_present: true
additive_hardening_needed: true
evidence_kind_alignment_deferred: true
artifact_type_alignment_deferred: true
production_ready_claimed: false
public_auditor_ready_claimed: false
recommended_next_patch_requires_user_approval: true
