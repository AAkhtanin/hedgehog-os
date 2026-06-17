# NeedleRuntime Audit Evidence Shape Patch Plan v0.1

## 1. Status

needleruntime_audit_evidence_shape_patch_plan_v01_status: COMPLETE
patch_plan_only: true
patch_applied: false
runtime_modified: false
schemas_modified: false
tests_modified: false
audit_added_to_evidenceitem_kind: false
needle_runtime_added_to_evidenceitem_kind: false
artifact_type_modified: false
production_ready_claimed: false
public_auditor_ready_claimed: false

This is a patch plan only. It does not change runtime, schemas, tests,
README, AGENTS, specs, Transition Matrix, DRS lifecycle, GT, Root, DRS,
artifact_type, Negative Trace, or Marennya.

## 2. Context

NeedleRuntime Audit Evidence Shape Preflight v0.1 is committed:

- preflight_commit: 99592a6
- preflight_file: `docs/needleruntime_audit_evidence_shape_preflight_v01.md`

Earlier chain:

- EvidenceItem.kind Alignment docs sync: 3e35548
- EvidenceItem.kind audit: 0eb58c1
- EvidenceItem.kind patch: 4ced110
- EvidenceItem.kind plan: 2685921
- Artifact Vocabulary / Evidence Taxonomy preflight: 8a76a49

Preflight finding:

- `hedgehog/needle_runtime.py` emits an old-shape EvidenceItem inside
  `ResultProposal.evidence[*]`.
- The emitted object uses `kind: audit`, `evidence_id`, `description`, and
  `ref`.
- Active EvidenceItem requires `kind` and `summary`.
- Active EvidenceItem optionally allows `ref_id` and `confidence`.
- Active EvidenceItem has `additionalProperties: false`.
- `audit` is not currently allowed in EvidenceItem.kind.
- `needle_runtime` appears as `trace_refs.kind`, not EvidenceItem.kind.
- The NeedleRuntime proposal crosses the Post V&V ResultProposal schema
  boundary through demo/tests.
- The current NeedleRuntime evidence object is not schema-valid if validated
  as active ResultProposal evidence.
- artifact_type Mapping remains a separate later layer.

Current boundary risk:

- Post V&V now validates incoming ResultProposal artifacts against
  `schemas/result_proposal.schema.json` at runtime.
- A NeedleRuntime proposal with the current evidence object should fail the
  EvidenceItem schema boundary.
- Existing tests exercise the adapter through Post V&V, but the current
  coverage does not pin the NeedleRuntime evidence object as schema-valid.

## 3. Current Broken Shape

Current object shape from `hedgehog/needle_runtime.py`:

```json
{
  "evidence_id": "evidence:<request_id>:<needle_id>:<failure_kind>",
  "kind": "audit",
  "description": "NeedleRuntime returned a structured mock result with no external action.",
  "ref": "needle_runtime_mock_execution"
}
```

Why it fails active EvidenceItem:

- `summary` is missing.
- `evidence_id` is not allowed.
- `description` is not allowed.
- `ref` is not allowed.
- `audit` is not in the active EvidenceItem.kind enum.

Active EvidenceItem shape:

```json
{
  "kind": "<allowed enum>",
  "summary": "<non-empty string>",
  "ref_id": "<optional id>",
  "confidence": "<optional 0..1 score>"
}
```

## 4. Decision Matrix

| option | schema correctness | semantic honesty | authority leakage risk | runtime breakage risk | testability | recommendation |
| --- | --- | --- | --- | --- | --- | --- |
| Option A - Normalize shape only, do not add audit to EvidenceItem.kind | Partial. Shape can be fixed, but `kind` must use an existing enum. | Weak unless an existing allowed kind is genuinely correct. `needle` could imply a needle source, while the current object is specifically audit/event support; `trace` could obscure evidence semantics; `schema`, `policy`, `manual`, and executor kinds are dishonest. | Low if guardrails are added. | Medium because the adapter object changes and the kind may change semantics. | Medium. Tests can prove schema validity, but semantic ambiguity remains. | Not recommended as the primary patch because existing allowed kinds would mislabel the audit event. |
| Option B - Add audit to EvidenceItem.kind and normalize shape | Strong. Adds the missing enum value and converts to active fields. | Strong. The current adapter already treats audit information as a ResultProposal evidence item, and `audit` accurately identifies the support source. | Medium unless the patch pins that audit evidence is not truth or authority. | Medium because the adapter object and enum change narrowly. | High. Tests can cover schema validity, Post V&V acceptance path, old-field rejection, and authority guardrails. | Recommended. |
| Option C - Keep audit outside EvidenceItem.kind | Potentially strong if the audit pointer can move to schema-allowed trace/payload metadata and evidence is replaced with a valid non-audit EvidenceItem. | Strong if the project decides audit is metadata, not evidence. Weak if the current ResultProposal loses its only explicit support item. | Low. | Medium-high because moving/removing the evidence item may affect adapter semantics and tests. | Medium. Tests can verify schema compatibility, but need a clear replacement evidence item or accepted metadata field. | Not recommended unless Guardian Passport decides audit must remain outside EvidenceItem.kind. |
| Option D - Defer until artifact_type Mapping | Weak for the current boundary. The NeedleRuntime proposal already crosses Post V&V runtime schema validation. | Weak. It leaves the evidence/audit distinction unresolved in an active adapter. | Low short-term, but ambiguity remains. | Low short-term. | Low. No patch means no new proof. | Not recommended because current boundary risk is local and narrow enough to fix before artifact_type Mapping. |

Decision:

- recommended option: Option B
- rationale: `audit` is already the adapter's declared evidence kind. Adding it
  narrowly and converting the object to active EvidenceItem fields preserves
  current intent while keeping `needle_runtime` as trace metadata and leaving
  artifact_type for a separate layer.

## 5. Recommended Patch

recommended_patch_type: option_b_add_audit_and_normalize_shape
audit_evidence_kind_decision: add_audit
needle_runtime_evidence_kind_decision: keep_trace_metadata_only
artifact_type_mapping_status: deferred_separate_layer

Future patch files likely:

- `schemas/common.schema.json`
- `specs/schema_package_v0_25_reference.md`
- `hedgehog/needle_runtime.py`
- `tests/test_needle_failure_integration_runner.py`
- `tests/test_post_vv_runtime.py` or a focused schema test
- `specs/invariants.md` optional

Future patch steps:

1. Add `audit` to the active EvidenceItem.kind enum.
2. Do not add `needle_runtime` to EvidenceItem.kind.
3. Normalize the NeedleRuntime evidence object to active EvidenceItem fields:
   - `kind: audit`
   - `summary: NeedleRuntime returned a structured mock result with no external action.`
   - `ref_id: needle_runtime_mock_execution` or another stable audit event id
   - `confidence`: optional, only if a bounded score is semantically meaningful
4. Remove old fields from the evidence object:
   - `evidence_id`
   - `description`
   - `ref`
5. Keep `needle_runtime` in `trace_refs.kind`.
6. Do not change `artifact_type`.
7. Do not modify GT, Root, DRS, Transition Matrix, DRS lifecycle, Negative
   Trace, or Marennya.

Future patch invariant:

- `audit` in EvidenceItem.kind means local audit/event support for a
  ResultProposal evidence item. It does not mean truth, authority,
  AcceptedEvidence, action permission, DRS write, or FinalOutput.

If Guardian Passport rejects `audit` as EvidenceItem.kind, use Option C instead:

- keep `audit` out of EvidenceItem.kind;
- remove the audit evidence item or replace it with a semantically honest
  allowed evidence kind;
- move the audit pointer outside `ResultProposal.evidence[*]` only where the
  active schema allows it;
- add focused tests for schema validity and authority guardrails.

## 6. Future Tests

Required future tests should prove:

- NeedleRuntime adapter output is schema-valid ResultProposal after the patch.
- Post V&V no longer rejects NeedleRuntime proposal for EvidenceItem shape.
- audit evidence, if added, does not create truth.
- audit evidence, if added, does not create authority.
- audit evidence, if added, does not imply AcceptedEvidence.
- audit evidence, if added, does not authorize action.
- audit evidence, if added, does not write DRS.
- audit evidence, if added, does not create FinalOutput.
- `needle_runtime` remains `trace_refs.kind` and is not EvidenceItem.kind.
- malformed old fields are rejected if reintroduced.
- unknown evidence kind is still rejected.

Suggested focused test targets:

- `tests/test_needle_failure_integration_runner.py`
- `tests/test_post_vv_runtime.py` or a small focused schema test
- existing schema file validation, if needed to prove enum/reference sync

## 7. Authority Guardrails

Required future patch invariants:

- NeedleRuntime is not authority.
- NeedleRuntime does not create FinalOutput.
- NeedleRuntime does not write DRS directly.
- NeedleRuntime does not execute real external action.
- audit evidence is not truth.
- audit hash is not truth.
- EvidenceItem.kind does not create truth.
- EvidenceItem.kind does not create authority.
- Root remains final authority.

Guardrail fields for later audit:

- needleruntime_is_authority: false
- needleruntime_creates_finaloutput: false
- needleruntime_writes_drs_directly: false
- needleruntime_executes_real_external_action: false
- audit_evidence_creates_truth: false
- audit_hash_creates_truth: false
- evidenceitem_kind_creates_truth: false
- evidenceitem_kind_creates_authority: false
- root_remains_final_authority: true

## 8. Non-goals

This plan does not:

- patch runtime
- patch schemas
- patch tests
- add audit to EvidenceItem.kind
- add needle_runtime to EvidenceItem.kind
- perform NeedleRuntime evidence-shape changes
- align artifact_type
- change Transition Matrix
- change DRS lifecycle
- create Negative Trace layer
- activate Marennya
- claim production readiness
- claim public-auditor readiness

## 9. Risks

schema_patch_risk: medium
runtime_adapter_patch_risk: medium
audit_authority_leakage_risk: medium
test_gap_risk: medium
artifact_type_coupling_risk: low

Risk notes:

- Schema patch risk is medium because adding `audit` to EvidenceItem.kind can
  be misread as broad audit taxonomy unless the patch stays local.
- Runtime adapter patch risk is medium because callers may inspect the old
  fields.
- Audit authority leakage risk is medium because audit terminology can be
  mistaken for truth unless guardrails are tested.
- Test gap risk is medium because current NeedleRuntime tests call Post V&V but
  do not clearly pin EvidenceItem schema validity.
- artifact_type coupling risk is low if the patch explicitly avoids
  artifact_type Mapping.

## 10. Recommended Next Step

recommended_next_step: implement narrow Option B patch after user approval.

Exact next patch:

- add only `audit` to EvidenceItem.kind;
- normalize only the NeedleRuntime audit evidence object to active
  EvidenceItem fields;
- keep `needle_runtime` as trace metadata only;
- keep artifact_type Mapping deferred;
- add focused schema and authority guardrail tests;
- do not touch GT, Root, DRS, Transition Matrix, DRS lifecycle, Negative Trace,
  or Marennya.

If Guardian Passport flags `audit` as metadata rather than evidence, implement
the narrow Option C patch instead.

## 11. Summary

needleruntime_audit_evidence_shape_patch_plan_v01_status: COMPLETE
patch_plan_only: true
patch_applied: false
runtime_modified: false
schemas_modified: false
tests_modified: false
recommended_patch_type: option_b_add_audit_and_normalize_shape
audit_evidence_kind_decision: add_audit
needle_runtime_evidence_kind_decision: keep_trace_metadata_only
artifact_type_mapping_status: deferred_separate_layer
recommended_next_patch_requires_user_approval: true
root_remains_final_authority: true
production_ready_claimed: false
public_auditor_ready_claimed: false
