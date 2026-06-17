# EvidenceItem.kind Alignment v0.1 Patch Plan

## 1. Status

evidenceitem_kind_alignment_plan_v01_status: COMPLETE
patch_plan_only: true
patch_applied: false
runtime_modified: false
schemas_modified: false
tests_modified: false
artifact_type_alignment_implemented: false
transition_matrix_modified: false
drs_lifecycle_modified: false
production_ready_claimed: false
public_auditor_ready_claimed: false

Scan inputs used:

- `rg -n "EvidenceItem|kind|simulated_executor|manual|trace|schema|policy|drs_record|needle|fractal_dag_executor|needle_runtime|audit" schemas hedgehog demo tests specs docs README.md AGENTS.md`
- `rg -n "\"evidence\"|evidence =|kind:|\"kind\":|simulated_executor|fractal_dag_executor|needle_runtime|audit" hedgehog demo tests`
- `rg -n "result_proposal.schema.json|EvidenceItem|validate_result_proposal|_result_proposal_validator|Post V&V|vv_runtime_schema_validation_failed" hedgehog tests schemas docs`
- `rg -n "EvidenceItem.kind|evidence_kind|evidence.*truth|evidence.*authority|accepted evidence|AcceptedEvidence|candidate.*accepted|artifact_type.*authority|Root remains final authority|Root creates FinalOutput" specs docs README.md AGENTS.md tests`

## 2. Context

Artifact Vocabulary / Evidence Taxonomy Preflight v0.1 found that the active
EvidenceItem.kind enum is narrower than observed runtime and proof evidence
terms. The finding matters more now because Post V&V validates incoming
ResultProposal artifacts against `schemas/result_proposal.schema.json` at
runtime.

This plan scopes a narrow EvidenceItem.kind patch. EvidenceItem.kind is a local
schema enum for items inside `ResultProposal.evidence`. It is not the global
artifact vocabulary, not `artifact_type`, not authority, not truth, not accepted
evidence, and not action permission.

## 3. Current EvidenceItem.kind Enum

Current enum in `schemas/common.schema.json`:

- `drs_record`
- `needle`
- `schema`
- `policy`
- `trace`
- `simulated_executor`
- `manual`

Schema placement:

- `schemas/common.schema.json` defines `$defs.EvidenceItem`.
- `EvidenceItem` requires `kind` and `summary`.
- Optional fields are `ref_id` and `confidence`.
- `EvidenceItem` has `additionalProperties: false`.
- `schemas/result_proposal.schema.json` uses `EvidenceItem` for
  `ResultProposal.evidence`.

## 4. Observed Evidence Kind Usage

| observed kind | source file | current meaning | active schema status | recommended action |
| --- | --- | --- | --- | --- |
| `simulated_executor` | `hedgehog/executor.py` | Deterministic local Executor evidence for schema-valid active ResultProposal objects. | already_allowed | Keep unchanged and keep schema-valid Executor test coverage. |
| `fractal_dag_executor` | `hedgehog/fractal_dag_executor.py` | Fractal DAG proof-level node execution evidence on ResultProposal-shaped boundary artifacts. | missing_from_enum | Add narrowly if future patch wants otherwise schema-valid Fractal DAG boundary evidence to pass EvidenceItem validation. Do not treat the DAG artifact as Root Final. |
| `audit` | `hedgehog/needle_runtime.py` | NeedleRuntime adapter evidence points to a structured audit event for a mock needle outcome. | missing_from_enum, and current evidence item shape also differs from `EvidenceItem` | Add only if kept as a ResultProposal evidence item kind. Pair with a targeted evidence item shape cleanup for this emitter if the next patch tests NeedleRuntime through Post V&V schema validation. |
| `needle_runtime` | `hedgehog/needle_runtime.py` | Used in `trace_refs.kind` for the NeedleRuntime adapter span, not as an `EvidenceItem.kind` in the active return object read. | should_not_be_evidence_kind for current usage | Do not add only because it appears in `trace_refs`. Reconsider only if an actual `ResultProposal.evidence[*].kind` need is introduced. |
| `executor_node` | `hedgehog/executor.py` | TraceRef kind for ordinary Executor node span. | should_not_be_evidence_kind | Keep as trace metadata, not evidence kind. |
| `fractal_dag_executor_node` | `hedgehog/fractal_dag_executor.py` | TraceRef kind for Fractal DAG node span. | should_not_be_evidence_kind | Keep as trace metadata, not evidence kind. |
| `test` | `tests/test_root_dag_integration_runner.py` | Test DRS provenance trace kind in a seeded record. | should_not_be_evidence_kind | Do not add to EvidenceItem.kind. Normalize a fixture only if it ever becomes ResultProposal evidence. |

Additional shape note:

- `hedgehog/needle_runtime.py` currently emits an evidence item with
  `evidence_id`, `description`, and `ref`. That differs from active
  `EvidenceItem`, which allows `kind`, `summary`, `ref_id`, and `confidence`.
  A future patch must not pretend enum expansion alone validates that emitter if
  the emitted object remains in the old shape.

## 5. Alignment Options

### Option A: Expand EvidenceItem.kind enum narrowly

Add only observed valid `ResultProposal.evidence[*].kind` values that are
actually source categories for evidence items.

Candidate additions:

- `fractal_dag_executor`
- `audit`, only if the NeedleRuntime adapter continues to use an audit-backed
  evidence item

Do not add `needle_runtime` unless a future patch changes it from trace metadata
into a real `ResultProposal.evidence[*].kind`.

Safety impact: low if paired with authority guardrail tests.
Schema compatibility: medium-positive because schema accepts observed evidence
source kinds without expanding into artifact taxonomy.
Runtime breakage risk: low for enum-only validation; medium if existing
NeedleRuntime evidence shape is left unnormalized and then expected to pass.
Conceptual clarity: medium-high because evidence kind remains local.
Authority leakage risk: low if docs/tests state evidence kind does not create
truth, authority, acceptance, action permission, DRS write, or FinalOutput.

### Option B: Normalize runtime/proof emitters to existing enum

Possible mappings:

- `fractal_dag_executor` -> `simulated_executor` or `trace`
- `audit` -> `trace`
- `needle_runtime` -> `needle`, but only if it becomes an evidence item kind

Safety impact: low.
Schema compatibility: high.
Runtime breakage risk: medium because it changes source semantics in emitters.
Conceptual clarity: medium-low because distinct sources become less visible.
Authority leakage risk: low, but source provenance becomes less precise.

### Option C: Add separate evidence_source / evidence_role later

Introduce a new field or vocabulary split in a later schema layer.

Safety impact: medium because it broadens schema shape.
Schema compatibility: medium-low until migration is planned.
Runtime breakage risk: medium.
Conceptual clarity: high if designed carefully, but too broad for v0.1.
Authority leakage risk: medium unless paired with explicit guardrails.

## 6. Recommended Patch

recommended_patch_type: narrow_enum_expansion

Proceed with a narrow enum expansion for observed values that are truly
`ResultProposal.evidence` source kinds:

- Add `fractal_dag_executor`.
- Add `audit` only if the future patch also keeps NeedleRuntime audit evidence
  as an EvidenceItem and normalizes that evidence object to the active
  EvidenceItem shape.
- Do not add `needle_runtime` based only on current trace-ref usage.

The future patch should not add every artifact vocabulary term to
EvidenceItem.kind. It should not add `AcceptedEvidence`, `EvidenceCandidate`,
`ValidationPacket`, `RootFinalOutput`, `GTReport`, `AuditEvent`,
`ChildBoundarySnapshot`, `SemanticDraft`, `NeedleCandidate`, or
`ManifestCandidate` unless a precise `ResultProposal.evidence` need is found and
reviewed.

EvidenceItem.kind must remain a local evidence item classification, not a global
artifact registry. `artifact_type` mapping remains deferred and separate.

Focused future tests should prove:

- an otherwise schema-valid ResultProposal can use `fractal_dag_executor`
  evidence kind without becoming FinalOutput or authority;
- an otherwise schema-valid ResultProposal can use `audit` evidence kind, if
  retained, without making audit truth or authority;
- current ordinary Executor output with `simulated_executor` remains schema-valid;
- trace ref kinds such as `executor_node`, `fractal_dag_executor_node`, and
  `needle_runtime` are not automatically evidence kinds;
- Post V&V still rejects malformed EvidenceItem shape.

## 7. Future Patch Targets

Likely future patch files:

- `schemas/common.schema.json`
- `specs/schema_package_v0_25_reference.md`
- `tests/test_schema_files_valid.py`
- `tests/test_post_vv_runtime.py` or a focused ResultProposal schema test
- tests around Fractal DAG / NeedleRuntime only if those outputs are explicitly
  sent through Post V&V runtime schema validation

Optional future patch file:

- `specs/invariants.md`, only if adding a compact authority guardrail note

Conditional future runtime file:

- `hedgehog/needle_runtime.py`, only if the patch validates its adapter output
  through active ResultProposal schema and must normalize the evidence item
  shape from `description/ref/evidence_id` to `summary/ref_id/confidence`.

Not recommended for this patch:

- broad runtime rewrites
- artifact_type mapping
- Transition Matrix work
- DRS lifecycle work
- GT, Root, or DRS changes

## 8. Authority Guardrails for Future Patch

Future tests or assertions should prove:

- EvidenceItem.kind does not create truth.
- EvidenceItem.kind does not create authority.
- EvidenceItem.kind does not imply AcceptedEvidence.
- EvidenceItem.kind does not authorize action.
- EvidenceItem.kind does not write DRS.
- EvidenceItem.kind does not create FinalOutput.
- Root remains final authority.

Additional guardrails:

- `audit` evidence kind, if added, records support/provenance only; audit hash is
  not truth.
- `fractal_dag_executor` evidence kind, if added, records source of bounded node
  execution only; DAG output remains downstream of Post V&V, GT, and Root.
- EvidenceItem.kind must not be used as `artifact_type`.

## 9. Non-goals

This plan does not:

- patch schemas
- patch runtime
- patch tests
- align artifact_type
- create a global artifact registry
- change Transition Matrix
- change DRS lifecycle
- create Negative Trace layer
- activate Marennya
- claim production readiness
- claim public-auditor readiness

## 10. Risks

schema_enum_expansion_risk: medium
authority_leakage_from_kind_risk: low
runtime_breakage_risk: medium
auditor_confusion_risk: medium
patch_needed_before_artifact_type_mapping: true

Risk notes:

- Schema enum expansion risk is medium because adding source terms can be
  misread as blessing broader artifact categories unless the patch stays narrow.
- Authority leakage risk is low if guardrail tests explicitly keep Root as the
  only final authority.
- Runtime breakage risk is medium because the NeedleRuntime adapter has evidence
  item shape drift in addition to enum drift.
- Auditor confusion risk is medium until artifact_type mapping is handled in a
  later layer.

## 11. Recommended Next Step

Patch EvidenceItem.kind enum narrowly now, after review.

Recommended staged patch:

1. Add `fractal_dag_executor` to the active EvidenceItem.kind enum.
2. Add `audit` only with focused tests and, if needed, a minimal NeedleRuntime
   evidence item shape normalization.
3. Keep `needle_runtime` as trace metadata unless a direct evidence item need is
   introduced.
4. Add tests that schema-valid evidence kinds do not create truth, authority,
   AcceptedEvidence, action permission, DRS write, or FinalOutput.
5. Do not touch artifact_type mapping in this patch.

## 12. Summary

evidenceitem_kind_alignment_plan_v01_status: COMPLETE
patch_plan_only: true
patch_applied: false
runtime_modified: false
schemas_modified: false
tests_modified: false
evidenceitem_kind_alignment_needed: true
artifact_type_alignment_deferred: true
recommended_patch_type: narrow_enum_expansion
root_remains_final_authority: true
recommended_next_patch_requires_user_approval: true
production_ready_claimed: false
public_auditor_ready_claimed: false
