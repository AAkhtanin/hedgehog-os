# Outgoing VVReport Runtime Schema Validation Preflight v0.1

## 1. Status

outgoing_vvreport_runtime_validation_preflight_v01_status: COMPLETE
preflight_only: true
patch_applied: false
runtime_modified: false
schemas_modified: false
tests_modified: false
evidence_kind_alignment_implemented: false
artifact_type_alignment_implemented: false
production_ready_claimed: false
public_auditor_ready_claimed: false

This is a read-only preflight and patch plan. It creates no runtime behavior,
changes no schemas, changes no tests, and does not implement outgoing VVReport
runtime validation.

## 2. Context

Incoming ResultProposal runtime schema validation at Post V&V is now
implemented. The closed chain is:

- preflight: `3207a19` Add Runtime JSON Schema Validation Hardening preflight
- runtime patch: `48e2515` Add Post V&V ResultProposal runtime schema validation
- audit: `107a7c4` Add Runtime JSON Schema Validation Hardening audit log
- docs sync: `e468541` Document Runtime JSON Schema Validation Hardening checkpoint

The remaining local Finding B subphase is outgoing VVReport runtime validation.
This preflight decides whether to patch now, defer until EvidenceItem.kind /
artifact_type alignment, or split the work.

Read-only scan commands used:

- `git status --short`
- `rg -n "vv_report_id|proposal_id|status|scores|overall_score|decision|checked_at|violations|normalized_features|trace_refs|request_id|validate_result_proposal|validate_result_proposals" hedgehog/post_vv.py tests schemas specs docs README.md AGENTS.md`
- `rg -n "vv_report.schema.json|VVReport|ValidationReport|vv_report_id|overall_score|decision|checked_at|violation|normalized_features|additionalProperties|accepted|rejected|needs_revision|revise" schemas tests hedgehog specs docs README.md AGENTS.md`
- `rg -n "vv_report_schema|validate\(|Draft202012Validator|test_.*vv|test_.*post_vv|validate_result_proposal|validate_result_proposals|overall_score|decision|checked_at" tests hedgehog`
- `rg -n "ValidationReport|VVReport|status|decision|scores|overall_score|violations|trace_refs|gt_validator|GTDecision|validate" hedgehog/gt_validator.py tests/test_gt_validator_runtime.py tests/test_gt_from_validation_report_runner.py`
- `rg -n "VVReport|ValidationReport|GTDecision|Root Final|RootFinal|raw ValidationReport|malformed" tests/test_root_final_from_gt_decision_runner.py hedgehog`
- `sed -n` and `cat` reads of the focused runtime, schema, test, preflight, and audit files listed below.

Focused files read:

- `hedgehog/post_vv.py`
- `hedgehog/gt_validator.py`
- `schemas/vv_report.schema.json`
- `schemas/result_proposal.schema.json`
- `schemas/common.schema.json`
- `tests/test_post_vv_runtime.py`
- `tests/test_post_vv_from_result_proposal_runner.py`
- `tests/test_gt_validator_runtime.py`
- `tests/test_gt_from_validation_report_runner.py`
- `tests/test_schema_files_valid.py`
- `docs/audit_reports/auditor_runtime_jsonschema_hardening_post_vv_resultproposal_v01.log`
- `docs/schema_contract_alignment_runtime_jsonschema_hardening_preflight_v01.md`

## 3. Current Outgoing VVReport Evidence

Active outgoing report creator:

- `hedgehog/post_vv.py`
- function: `validate_result_proposal()`
- batch function: `validate_result_proposals()`

`validate_result_proposal()` currently returns a report dictionary with these
fields:

- `vv_report_id`
- `proposal_id`
- `dependency_depth`
- `status`
- `scores`
- `overall_score`
- `decision`
- `checked_at`
- `violations`
- `normalized_features`
- `trace_refs`

It may also include these optional fields:

- `vector_id`
- `artifact_type`
- `execution_status`
- `request_id`

Observed value mappings:

- `vv_report_id` is `vv:{proposal_id}`.
- `proposal_id` uses the incoming proposal id when present, otherwise
  `missing_proposal`.
- `dependency_depth` is an integer minimum `0`.
- `status` maps `accept -> accepted`, `reject -> rejected`, and
  `revise -> needs_revision`.
- `scores` includes `schema`, `evidence`, `policy`, `time`, `safety`, and
  `consistency`.
- `overall_score` is the arithmetic mean of score values.
- `decision` is one of `accept`, `reject`, or `revise`.
- `checked_at` uses `utc_now_iso()`.
- `violations` are dictionaries with `violation_id`, `kind`, and
  `description`.
- `normalized_features` includes `utility`, `robustness`, `compute_cost`,
  `violations`, `transfer`, `novelty_guard`, `avf_final_viability`, and
  `avf_soft_mask`.
- `trace_refs` is copied from the proposal only if it is a list; malformed
  trace refs become an empty list.

Comparison with `schemas/vv_report.schema.json`:

- Required schema fields are present in the runtime output:
  `vv_report_id`, `proposal_id`, `status`, `scores`, `overall_score`,
  `decision`, and `checked_at`.
- Runtime `status` values match the schema enum: `accepted`, `rejected`,
  `needs_revision`.
- Runtime `decision` values match the schema enum: `accept`, `reject`,
  `revise`.
- Runtime `scores` contains exactly the schema-required keys and no observed
  extras.
- Runtime `normalized_features` keys match the schema properties.
- Runtime `violations` shape matches the schema for observed violation kinds:
  `schema`, `evidence`, `policy`, `time`, `safety`, and `consistency`.
- Runtime optional `vector_id`, `artifact_type`, `execution_status`,
  `dependency_depth`, `request_id`, and `trace_refs` are allowed by the schema.
- `schemas/vv_report.schema.json` has `additionalProperties: false`, so a
  future runtime output validator would catch accidental extra top-level keys.

No current runtime outgoing VVReport validation was observed before returning
from `validate_result_proposal()`.

## 4. Current Schema Validation Evidence

VVReport schema validation already exists in tests:

- `tests/test_post_vv_runtime.py` defines `vv_report_validator()` using
  `jsonschema.Draft202012Validator`.
- That helper loads `schemas/vv_report.schema.json` and
  `schemas/common.schema.json`.
- `test_validate_demo_result_proposals_are_task_aware_and_schema_valid()`
  validates runtime Post V&V output reports against
  `schemas/vv_report.schema.json`.
- The same test verifies current task-aware fields such as `vector_id`,
  `artifact_type`, `execution_status`, `normalized_features`,
  `avf_final_viability`, and `avf_soft_mask`.
- `tests/test_schema_files_valid.py` verifies every `schemas/*.schema.json`
  file is a valid Draft 2020-12 JSON Schema.

Existing tests also cover incoming ResultProposal runtime validation:

- missing required ResultProposal field rejected by runtime schema validation
- bad nested TimeEnvelope rejected by runtime schema validation
- malformed risk severity rejected by runtime schema validation
- extra top-level ResultProposal field rejected by runtime schema validation
- schema-valid critical risk still rejected by manual safety check
- forbidden `final_output` and `answer` keys still rejected by manual policy
  check
- malformed proposal does not crash Post V&V

Downstream GT evidence:

- `hedgehog/gt_validator.py` consumes the current VVReport shape directly.
- GT reads `scores`, `overall_score`, `violations`, `normalized_features`,
  `proposal_id`, `status`, `decision`, and optional `vector_id`,
  `artifact_type`, `execution_status`, `dependency_depth`, and `request_id`.
- `tests/test_gt_validator_runtime.py` builds VVReport dictionaries and
  validates GT output against `schemas/gt_report.schema.json`.
- `tests/test_gt_from_validation_report_runner.py` verifies GT accepts valid
  ValidationReport / VVReport inputs, rejects malformed validation reports, and
  does not create FinalOutput, write DRS, execute action, or invoke Root.

Root boundary evidence:

- `tests/test_root_final_from_gt_decision_runner.py` verifies Root Final
  receives GTDecision artifacts, rejects malformed GTDecision, and does not
  consume raw ValidationReport as the final boundary.

## 5. Gap Analysis

incoming_resultproposal_runtime_schema_validation_present: true
outgoing_vv_report_runtime_schema_validation_present: false
vv_report_schema_validation_in_tests_present: true
vv_report_runtime_output_conforms_to_schema_in_tests: true
downstream_gt_expects_current_vv_shape: true
additive_output_validation_needed: true
schema_or_runtime_shape_mismatch_found: false

What is already covered:

- Post V&V validates incoming ResultProposal against
  `schemas/result_proposal.schema.json` at runtime.
- Post V&V manual policy and safety checks remain preserved.
- Tests validate normal runtime Post V&V reports against
  `schemas/vv_report.schema.json`.
- The current runtime output shape matches the active VVReport schema for the
  observed report fields.
- GT already expects and consumes the current VVReport shape.

What is missing:

- Post V&V does not validate the outgoing VVReport dictionary against
  `schemas/vv_report.schema.json` before returning.
- The schema-valid normal output path is tested, but there is no runtime
  output-validation guard for future accidental changes.
- Rejection and malformed-input paths are not all explicitly validated against
  the outgoing schema before return.

Whether outgoing validation should be patched now:

- Yes, based on this scan. The current runtime output and schema are aligned
  enough for a narrow outgoing validation patch.
- EvidenceItem.kind alignment is not a blocker because VVReport does not carry
  EvidenceItem.kind.
- artifact_type alignment is not a blocker because VVReport treats
  `artifact_type` as an optional non-empty string, not a closed enum.
- No schema/runtime shape mismatch was found that would require schema edits.

## 6. Minimal Future Patch Proposal

Recommended option: A. Patch now.

Future patch shape:

- Add outgoing VVReport JSON Schema validation before returning from
  `validate_result_proposal()`.
- Use `schemas/vv_report.schema.json`.
- Resolve local `common.schema.json` refs.
- Keep incoming ResultProposal schema validation unchanged.
- Keep all existing manual Post V&V checks unchanged.
- Validation failure must not create FinalOutput, write DRS, execute action, or
  call GT/Root.
- Prefer a safe deterministic report path if outgoing validation fails.

Recommended failure handling:

- Avoid recursive self-validation loops.
- If ordinary report validation fails, return a minimal schema-conforming
  rejected / needs_revision report with a schema violation describing the
  internal outgoing VVReport validation failure.
- Include a deterministic `vv_report_id`, `proposal_id`, score map,
  `overall_score`, `decision`, `status`, `checked_at`, violations list,
  normalized features, and trace refs.
- Do not raise an uncaught exception in the normal Post V&V path unless focused
  tests explicitly prove no downstream unsafe behavior and the user approves
  that behavior. The safer default is the V&V report path.

Focused tests for the future patch:

- normal accepted outgoing report validates at runtime and remains unchanged
- normal needs_revision outgoing report validates at runtime and remains
  unchanged
- normal rejected outgoing report validates at runtime and remains unchanged
- malformed incoming proposal still returns schema-valid rejected VVReport
- manual policy/safety rejection still returns schema-valid rejected VVReport
- an injected/internal outgoing report shape error is converted to a safe
  schema-valid rejected / needs_revision VVReport without calling GT/Root
- outgoing validation does not create FinalOutput, write DRS, execute action, or
  grant authority

## 7. Files Likely Affected By Future Patch

Likely:

- `hedgehog/post_vv.py`: add VVReport validator and validate outgoing report
  before return.
- `tests/test_post_vv_runtime.py`: add focused outgoing validation tests.

Optional:

- A tiny shared schema validation helper if duplication between ResultProposal
  and VVReport validation becomes messy. This is optional; the current
  `hedgehog/post_vv.py` helper pattern may be enough.

Not recommended:

- `schemas/*.schema.json`: no precise schema defect was found.
- `hedgehog/gt_validator.py`: downstream GT expects the current shape and does
  not need to change for this subphase.
- `hedgehog/root_orchestrator.py`: Root boundary is downstream of GTDecision,
  not outgoing VVReport validation.
- README / AGENTS / specs during the runtime patch: leave high-level docs for
  audit/docs sync after the patch.

## 8. Non-goals

This preflight does not:

- implement outgoing VVReport validation
- change runtime
- change schemas
- change tests
- align EvidenceItem.kind
- align artifact_type
- modify GT
- modify Root
- modify DRS
- claim production readiness
- claim public-auditor readiness
- close all findings

## 9. Risks

output_validation_regression_risk: low
schema_runtime_shape_mismatch_risk: low
gt_downstream_compatibility_risk: low
overclaim_risk: medium
patch_needed_before_artifact_taxonomy: true

Risk notes:

- Regression risk is low because current normal runtime output already
  validates against `schemas/vv_report.schema.json` in focused tests.
- Shape mismatch risk is low because the schema permits observed optional
  fields and no required runtime field is missing.
- GT compatibility risk is low because GT consumes the current shape and the
  patch should preserve that shape.
- Overclaim risk remains medium because this subphase still would not align
  EvidenceItem.kind, align artifact_type, validate every runtime artifact, or
  create production readiness.

## 10. Recommended Next Step

Recommended next step: outgoing VVReport runtime validation patch now.

The future patch should be narrow:

1. Add a cached VVReport schema validator in `hedgehog/post_vv.py`, following
   the existing ResultProposal validator pattern.
2. Validate outgoing reports against `schemas/vv_report.schema.json` before
   returning from `validate_result_proposal()`.
3. Convert outgoing schema validation failure into a safe schema-conforming
   rejected / needs_revision VVReport path.
4. Add focused tests in `tests/test_post_vv_runtime.py`.
5. Do not modify schemas, GT, Root, DRS, EvidenceItem.kind, or artifact_type.

This recommendation still requires user approval before any patch.

## 11. Summary

outgoing_vvreport_runtime_validation_preflight_v01_status: COMPLETE
preflight_only: true
patch_applied: false
runtime_modified: false
schemas_modified: false
tests_modified: false
incoming_resultproposal_runtime_schema_validation_present: true
outgoing_vv_report_runtime_schema_validation_present: false
vv_report_schema_validation_in_tests_present: true
vv_report_runtime_output_conforms_to_schema_in_tests: true
downstream_gt_expects_current_vv_shape: true
additive_output_validation_needed: true
schema_or_runtime_shape_mismatch_found: false
evidence_kind_alignment_deferred: true
artifact_type_alignment_deferred: true
root_remains_final_authority: true
recommended_next_patch_requires_user_approval: true
production_ready_claimed: false
public_auditor_ready_claimed: false
