# NeedleRuntime Audit Evidence Shape Preflight v0.1

## 1. Status

needleruntime_audit_evidence_shape_preflight_v01_status: COMPLETE
preflight_only: true
patch_applied: false
runtime_modified: false
schemas_modified: false
tests_modified: false
evidenceitem_kind_modified: false
audit_added_to_evidenceitem_kind: false
needle_runtime_added_to_evidenceitem_kind: false
artifact_type_modified: false
transition_matrix_modified: false
drs_lifecycle_modified: false
production_ready_claimed: false
public_auditor_ready_claimed: false

This is a read-only preflight. It maps the current NeedleRuntime audit evidence
shape before any schema, runtime, or test patch.

Read-only scan commands used:

- `git status --short`
- `rg -n "NeedleRuntime|needle_runtime|evidence|evidence_id|description|summary|ref_id|ref|kind|audit|trace_refs|ResultProposal|result_proposal" hedgehog demo tests specs docs README.md AGENTS.md`
- `rg -n "EvidenceItem|kind|summary|ref_id|confidence|additionalProperties|fractal_dag_executor|audit|needle_runtime" schemas specs docs tests`
- `rg -n "needle_result_to_result_proposal|result_to_result_proposal|NeedleExecutionResult|NeedleRuntimeResult|NeedleRuntime|ResultProposal|trace_refs|audit" hedgehog demo tests`
- `rg -n "validate_result_proposal|vv_runtime_schema_validation_failed|unknown evidence kind|malformed EvidenceItem|fractal_dag_executor|simulated_executor|audit|needle_runtime" tests hedgehog schemas docs`
- `rg -n "NeedleRuntime.*authority|NeedleRuntime.*FinalOutput|NeedleRuntime.*DRS|NeedleRuntime.*action|audit.*truth|audit.*authority|EvidenceItem.kind.*truth|EvidenceItem.kind.*authority|Root remains final authority|Root creates FinalOutput" specs docs README.md AGENTS.md tests`
- `sed -n` reads of the focused NeedleRuntime, Post V&V, schema, test, plan,
  audit, and invariant files listed in this report.

## 2. Context

EvidenceItem.kind Alignment v0.1 is complete through docs sync:

- vocabulary_preflight_commit: 8a76a49
- evidenceitem_kind_plan_commit: 2685921
- evidenceitem_kind_patch_commit: 4ced110
- evidenceitem_kind_audit_commit: 0eb58c1
- evidenceitem_kind_docs_sync_commit: 3e35548

The active EvidenceItem.kind enum now includes `fractal_dag_executor`.
`audit` and `needle_runtime` remain deferred. `artifact_type` remains untouched.

The deferred question is NeedleRuntime audit evidence shape. The active
EvidenceItem fields are `kind`, `summary`, optional `ref_id`, and optional
`confidence`. The current `hedgehog/needle_runtime.py` adapter emits an
evidence item with old fields: `evidence_id`, `description`, and `ref`, plus
`kind: audit`.

This preflight determines whether that object is already a valid
`ResultProposal.evidence[*]` item, an old-shape evidence item needing
normalization, trace/audit metadata that should stay outside EvidenceItem.kind,
or a separate artifact/audit reference that belongs outside EvidenceItem.kind.

## 3. Active EvidenceItem Contract

Active schema source:

- `schemas/common.schema.json`
- `$defs.EvidenceItem`
- referenced by `schemas/result_proposal.schema.json` for
  `ResultProposal.evidence[*]`

Active EvidenceItem required fields:

- `kind`
- `summary`

Active EvidenceItem optional fields:

- `ref_id`
- `confidence`

Active EvidenceItem kind enum:

- `drs_record`
- `needle`
- `schema`
- `policy`
- `trace`
- `simulated_executor`
- `fractal_dag_executor`
- `manual`

Active EvidenceItem structural constraint:

- `additionalProperties: false`

Current enum status:

- `fractal_dag_executor` is allowed.
- `audit` is not allowed.
- `needle_runtime` is not allowed.

TraceRef distinction:

- `schemas/common.schema.json` also defines `$defs.TraceRef`.
- TraceRef requires `trace_id`.
- TraceRef optionally allows `span_id` and `kind`.
- `trace_refs.kind` is a trace metadata string and is not EvidenceItem.kind.

## 4. NeedleRuntime Emitted Evidence Inventory

| file | function / path | emitted object | uses kind | uses summary | uses ref_id | uses confidence | uses old fields evidence_id / description / ref | currently schema-valid as EvidenceItem | crosses Post V&V ResultProposal schema boundary today | notes |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| `hedgehog/needle_runtime.py` | `needle_result_to_result_proposal()` -> `evidence[0]` | `{"evidence_id": ..., "kind": "audit", "description": ..., "ref": ...}` | yes, `audit` | no | no | no | yes, all three old fields appear | no | yes | The adapter returns an active-looking ResultProposal dict and `tests/test_needle_failure_integration_runner.py` sends it through `validate_result_proposal()`. Runtime schema validation should reject this EvidenceItem shape. |
| `hedgehog/needle_runtime.py` | `needle_result_to_result_proposal()` -> `trace_refs[0]` | `{"trace_id": ..., "span_id": "needle_runtime_adapter", "kind": "needle_runtime"}` | yes, as `trace_refs.kind` | not applicable | not applicable | not applicable | no | not an EvidenceItem | yes, as trace metadata inside the proposal | This is schema-valid TraceRef metadata if IDs are valid. It is not EvidenceItem.kind. |
| `hedgehog/needle_runtime.py` | `_audit_event()` and `NeedleExecutionResult.audit_event` | audit event dict with `event_type`, `needle_id`, `capability`, `scenario`, `status`, `failure_kind`, `no_real_external_action` | no EvidenceItem.kind | no | no | no | no EvidenceItem fields | not an EvidenceItem | indirectly referenced by adapter evidence `ref` | This is audit/event metadata. It does not by itself require `audit` in EvidenceItem.kind. |
| `demo/run_needle_failure_integration.py` | `collect_needle_failure_integration()` | `proposal = needle_result_to_result_proposal(...); vv_report = validate_result_proposal(proposal)` | inherits `audit` evidence item and `needle_runtime` TraceRef kind | no | no | no | yes via adapter | no for evidence item | yes | The demo crosses the Post V&V boundary but its tests mostly assert payload and execution status, not ResultProposal schema acceptance. |
| `tests/test_needle_failure_integration_runner.py` | `_proposal_for()` and adapter tests | Proposal from NeedleRuntime adapter, then `validate_result_proposal()` | inherits `audit` evidence item and `needle_runtime` TraceRef kind | no | no | no | yes via adapter | no for evidence item | yes | Tests call Post V&V but do not currently assert that the proposal is accepted or that the EvidenceItem object is schema-valid. |
| `demo/run_root_native_sandbox_needleruntime_e2e.py` | `_execution_result()` | proof-level `NeedleExecutionResult` row with `evidence` as list of strings | no EvidenceItem.kind | no | no | no | no | not an active EvidenceItem | no, this proof uses local rows, not active ResultProposal schema | Proof-level rows are ResultProposal-shaped later, but not active JSON Schema ResultProposal objects. |
| `demo/run_root_native_sandbox_needleruntime_e2e.py` | `_result_proposal()` | proof-level result proposal row with `evidence: list(result["evidence"])` | no EvidenceItem.kind | no | no | no | no | no, evidence is list of strings | no active Post V&V schema boundary | This is a deterministic proof row with its own validation/report path, not the active `hedgehog/post_vv.py` schema path. |
| docs and audit reports | EvidenceItem.kind docs sync and audit logs | checkpoint metadata | varies | varies | varies | varies | historical mentions of old fields | docs-only | no | Historical references explain the gap and must not be treated as active emitters. |

Preflight conclusion from inventory:

- The active NeedleRuntime adapter evidence object is not schema-valid as
  EvidenceItem today.
- The current mismatch is both enum drift (`kind: audit` is not allowed) and
  shape drift (`summary` is missing; `evidence_id`, `description`, and `ref`
  are forbidden by `additionalProperties: false`).
- `needle_runtime` appears as `trace_refs.kind`, not as
  `ResultProposal.evidence[*].kind`.

## 5. Trace vs Evidence Distinction

Observed `needle_runtime` placements:

| placement | observed? | evidence |
| --- | --- | --- |
| `trace_refs.kind` | yes | `hedgehog/needle_runtime.py` emits `kind: needle_runtime` in the TraceRef object. |
| `ResultProposal.evidence[*].kind` | no | The evidence item uses `kind: audit`, not `needle_runtime`. |
| audit source artifact type | yes, elsewhere | Audit/hash-chain and DRS lifecycle docs use source artifact labels such as `NeedleExecutionResult`; this is not EvidenceItem.kind. |
| DRS lifecycle source artifact | yes, elsewhere | DRS lifecycle proofs reference `NeedleExecutionResult` as `source_artifact_type`. |
| test fixture label | yes | Tests and demos use NeedleRuntime labels for scenarios and report rows. |
| docs-only term | yes | README, AGENTS, specs, and audit reports describe NeedleRuntime boundaries. |

Trace distinction:

- `trace_refs.kind` is not EvidenceItem.kind.
- Trace metadata should not be added to EvidenceItem.kind just because it
  appears in `trace_refs`.
- `needle_runtime` should remain outside EvidenceItem.kind unless a later patch
  introduces a precise `ResultProposal.evidence[*].kind` need.

## 6. Audit Evidence Distinction

Observed `audit` placements:

| placement | observed? | evidence |
| --- | --- | --- |
| EvidenceItem.kind | yes | `hedgehog/needle_runtime.py` emits `ResultProposal.evidence[0].kind: audit`. |
| audit event type | yes | `NeedleExecutionResult.audit_event.event_type` is `needle_runtime_mock_execution`. |
| source_artifact_type | yes, elsewhere | DRS lifecycle and audit/hash-chain use audit and source artifact type labels such as `DRSWritebackAuditRecord` and `NeedleExecutionResult`. |
| trace/audit ref | yes | The adapter evidence old field `ref` points to the audit event type. |
| docs-only term | yes | Docs and audit reports repeatedly describe audit/hash-chain as continuity evidence. |
| schema enum elsewhere | yes, separate contexts | `schemas/needle.schema.json` contains audit-related action metadata; this is not EvidenceItem.kind. |

Audit distinction:

- Audit event / audit hash is not truth.
- Audit metadata is not automatically `ResultProposal.evidence`.
- `audit` should only become EvidenceItem.kind if there is a precise
  `ResultProposal.evidence` need and the object shape matches EvidenceItem.
- Adding `audit` to EvidenceItem.kind alone would not validate current
  NeedleRuntime evidence because the current object still uses old fields.

## 7. Drift Findings

| finding | status | risk | patch_needed | recommended later patch target |
| --- | --- | --- | --- | --- |
| needleruntime_evidence_shape_old_fields | open | high | true | A focused NeedleRuntime evidence-shape patch plan, then a narrow runtime/test patch if approved. Normalize `evidence_id`, `description`, and `ref` into active EvidenceItem fields or move the audit pointer outside EvidenceItem. |
| audit_kind_missing_from_evidenceitem_enum | open | medium | maybe | Decide only after shape review. If audit remains actual `ResultProposal.evidence[*].kind`, add it narrowly with authority guardrail tests. |
| needle_runtime_is_trace_metadata_not_evidence_kind | partially_covered | low | false | Keep `needle_runtime` in `trace_refs.kind`; do not add it to EvidenceItem.kind from current evidence. |
| audit_event_vs_evidence_item_collision | open | medium | true | Clarify whether NeedleRuntime audit event is provenance metadata, trace/audit ref, or an EvidenceItem. |
| needle_result_adapter_not_schema_valid_if_sent_through_post_vv | open | high | true | `hedgehog/needle_runtime.py` and focused tests around `tests/test_needle_failure_integration_runner.py` or `tests/test_post_vv_runtime.py`, after a reviewed patch plan. |
| tests_do_not_cover_needleruntime_through_post_vv_schema_boundary | open | medium | true | Add focused tests that assert schema rejection today or acceptance after a reviewed normalization patch. |
| artifact_type_not_in_scope | partially_covered | low | false | Keep `artifact_type` Mapping / Runtime Artifact Vocabulary as a separate later layer. |

## 8. Patch Options

### Option A: Normalize NeedleRuntime evidence shape, but do not add audit yet

Shape:

- Convert the current evidence object to active EvidenceItem fields.
- Use an existing allowed kind only if semantically correct.
- Otherwise keep audit information outside `ResultProposal.evidence` until
  `audit` EvidenceItem.kind is explicitly reviewed.

Safety impact: low.
Schema compatibility: medium-high if an allowed kind is semantically correct.
Runtime breakage risk: medium because the adapter output changes.
Authority leakage risk: low if tests prove the evidence label creates no truth
or authority.
Conceptual clarity: medium, because it fixes shape first and avoids deciding
`audit` too early.

### Option B: Add audit to EvidenceItem.kind and normalize NeedleRuntime evidence shape

Shape:

- Add `audit` to the active EvidenceItem.kind enum.
- Change the NeedleRuntime evidence item to active fields such as `kind`,
  `summary`, `ref_id`, and optional `confidence`.
- Add tests proving audit evidence is not truth, authority, action permission,
  DRS write, AcceptedEvidence, or FinalOutput.

Safety impact: medium.
Schema compatibility: high if implemented narrowly.
Runtime breakage risk: medium.
Authority leakage risk: medium unless guardrails are explicit.
Conceptual clarity: medium-high if the report proves NeedleRuntime audit event
is a true local evidence source rather than trace/audit metadata.

### Option C: Keep audit as trace/audit metadata outside EvidenceItem.kind

Shape:

- Do not add `audit` to EvidenceItem.kind.
- Store the audit event reference in `trace_refs`, payload metadata, or a
  dedicated audit/source reference field if a later schema allows it.
- Keep `ResultProposal.evidence[*]` for active EvidenceItem-shaped support
  items only.

Safety impact: low.
Schema compatibility: medium, depending on where the audit reference is stored.
Runtime breakage risk: medium if callers expect the old evidence object.
Authority leakage risk: low.
Conceptual clarity: high because audit metadata stays separate from evidence
classification.

### Option D: Defer all changes until artifact_type Mapping

Shape:

- Do nothing in NeedleRuntime until the artifact vocabulary layer maps audit
  events, source artifact types, trace refs, EvidenceItem.kind, and
  `artifact_type`.

Safety impact: low short term.
Schema compatibility: low for current NeedleRuntime proposals crossing Post
V&V.
Runtime breakage risk: low short term, higher if schema validation becomes
more relied on.
Authority leakage risk: low.
Conceptual clarity: low-medium because the active drift remains visible.

## 9. Recommended Next Patch

recommended_next_step: create a small NeedleRuntime audit evidence shape patch
plan before code.

Recommended plan conclusion to review:

- Do not add `needle_runtime` to EvidenceItem.kind.
- Do not start artifact_type Mapping in the same patch.
- First decide whether NeedleRuntime audit information belongs inside
  `ResultProposal.evidence[*]` or outside it as trace/audit metadata.
- If it remains evidence, use Option B in a narrow patch: add only `audit` to
  EvidenceItem.kind and normalize the evidence object to active EvidenceItem
  fields with focused schema and authority tests.
- If it is provenance/audit metadata rather than evidence, use Option C in a
  narrow patch: keep `audit` out of EvidenceItem.kind and move or represent the
  audit pointer outside `ResultProposal.evidence[*]`.

Do not recommend a broad patch. Do not combine this with artifact_type Mapping.
Do not recommend a Negative Trace layer. Do not recommend Marennya activation.

## 10. Authority Guardrails

A future patch must preserve:

- NeedleRuntime is not authority.
- NeedleRuntime does not create FinalOutput.
- NeedleRuntime does not write DRS directly.
- NeedleRuntime does not execute real external action.
- NeedleRuntime audit evidence is not truth.
- Audit hash is not truth.
- EvidenceItem.kind does not create truth.
- EvidenceItem.kind does not create authority.
- Root remains final authority.

Guardrail fields:

- needleruntime_creates_finaloutput: false
- needleruntime_writes_drs_directly: false
- needleruntime_executes_real_external_action: false
- needleruntime_is_authority: false
- needleruntime_audit_evidence_is_truth: false
- audit_hash_is_truth: false
- evidenceitem_kind_creates_truth: false
- evidenceitem_kind_creates_authority: false
- root_remains_final_authority: true

## 11. Non-goals

This preflight does not:

- patch runtime
- patch schemas
- patch tests
- add audit to EvidenceItem.kind
- add needle_runtime to EvidenceItem.kind
- perform NeedleRuntime evidence-shape normalization
- align artifact_type
- change DRS lifecycle
- change Transition Matrix
- create Negative Trace layer
- activate Marennya
- claim production readiness
- claim public-auditor readiness

## 12. Risks

evidence_shape_drift_risk: high
audit_kind_authority_leakage_risk: medium
runtime_schema_boundary_risk: high
needle_runtime_breakage_risk_if_patched: medium
auditor_confusion_risk: medium

Risk notes:

- Evidence shape drift risk is high because the adapter emits an object that
  does not match active EvidenceItem shape and is sent through Post V&V.
- Audit kind authority leakage risk is medium because adding `audit` without
  guardrails could be misread as making audit events evidentiary truth.
- Runtime schema boundary risk is high because Post V&V now validates incoming
  ResultProposal artifacts and should reject the current old-shape evidence
  item.
- NeedleRuntime breakage risk is medium because a normalization patch can
  affect demos/tests that inspect adapter output.
- Auditor confusion risk is medium until the next patch explicitly separates
  audit metadata, evidence item classification, trace refs, and artifact_type.

## 13. Summary

needleruntime_audit_evidence_shape_preflight_v01_status: COMPLETE
preflight_only: true
patch_applied: false
runtime_modified: false
schemas_modified: false
tests_modified: false
needleruntime_evidence_shape_status: open
audit_evidence_kind_status: deferred
needle_runtime_evidence_kind_status: not_added_trace_metadata_only
audit_added_to_evidenceitem_kind: false
needle_runtime_added_to_evidenceitem_kind: false
artifact_type_mapping_status: deferred_separate_layer
recommended_next_patch_requires_user_approval: true
root_remains_final_authority: true
production_ready_claimed: false
public_auditor_ready_claimed: false

Evidence summary:

- Active EvidenceItem requires `kind` and `summary`; optional fields are
  `ref_id` and `confidence`; `additionalProperties: false` is active.
- `fractal_dag_executor` is allowed.
- `audit` is not allowed.
- `needle_runtime` is not allowed.
- `hedgehog/needle_runtime.py` emits `ResultProposal.evidence[0].kind: audit`
  with old fields `evidence_id`, `description`, and `ref`.
- `hedgehog/needle_runtime.py` emits `trace_refs.kind: needle_runtime`, which
  is trace metadata, not EvidenceItem.kind.
- Current NeedleRuntime adapter output crosses the Post V&V ResultProposal
  boundary through `demo/run_needle_failure_integration.py` and
  `tests/test_needle_failure_integration_runner.py`.
- A follow-up patch should be preceded by a small patch plan and should not
  combine with artifact_type Mapping.
