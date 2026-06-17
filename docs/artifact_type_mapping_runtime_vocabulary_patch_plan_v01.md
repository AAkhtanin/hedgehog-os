# artifact_type Mapping / Runtime Artifact Vocabulary Patch Plan v0.1

## 1. Status

artifact_type_mapping_runtime_vocabulary_patch_plan_v01_status: COMPLETE
patch_plan_only: true
patch_applied: false
runtime_modified: false
schemas_modified: false
tests_modified: false
registry_created: false
enum_created: false
evidenceitem_kind_modified: false
production_ready_claimed: false
public_auditor_ready_claimed: false
preflight_commit: b4aaf8e

This is a patch plan only. It applies no runtime, schema, test, registry, enum,
GT, Root, DRS, Transition Matrix, or DRS lifecycle change.

## 2. Preflight Basis

Preflight source:

- `b4aaf8e` Add artifact type runtime vocabulary preflight
- `docs/artifact_type_mapping_runtime_vocabulary_preflight_v01.md`

The preflight found that artifact_type / source_artifact_type are mixed
families today, not one simple active runtime enum:

- active runtime payload labels
- schema/report names
- proof taxonomy values
- audit/lifecycle source labels
- report metadata

Required interpretation from the preflight:

- artifact_type is currently free-string metadata in active runtime flow.
- `result_payload.artifact_type` is not formally declared in ResultProposal
  schema.
- VVReport has optional free-string artifact_type.
- GTReport does not have top-level artifact_type; it has `candidate_type`.
- FinalOutput has no artifact_type by design.
- DRSRecord uses `layer`, `type`, and `status`, not artifact_type.
- source_artifact_type appears in proof/demo/audit layers, not active schemas.
- EvidenceItem.kind remains separate from artifact_type.
- artifact_type currently does not grant authority.
- artifact_type currently does not create truth.
- artifact_type currently does not authorize action.
- artifact_type currently does not write DRS.
- artifact_type currently does not create FinalOutput.

## 3. Problem Statement

The issue is not that artifact_type is wrong. The issue is that the vocabulary
is not centrally mapped and can confuse distinct concepts:

- artifact_type
- source_artifact_type
- EvidenceItem.kind
- TraceRef.kind
- lifecycle_state
- authority_status
- AcceptedEvidence
- RootFinalOutput

The next patch should clarify vocabulary boundaries before adding code,
schemas, tests, enums, or registries.

## 4. Non-Overengineering Constraint

This plan must not create a global ontology.
This plan must not enumerate every future artifact.
This plan must not convert docs/proof-only labels into active runtime schema.
This plan must not make artifact_type an authority mechanism.
This plan must keep the runtime vocabulary small.

Map first, constrain later, enum last if still needed.

## 5. Canonical Separation

Four axes must remain separate:

| axis | meaning | guardrail |
| --- | --- | --- |
| artifact_type | What kind of runtime/proof/report artifact this is. | Does not decide anything. |
| evidence_kind / EvidenceItem.kind | Local ResultProposal evidence classification/source/provenance. | Already aligned for current active needs and remains separate from artifact_type. |
| source_artifact_type | Audit/lifecycle/proof source label. | Must remain separate from active runtime payload artifact_type unless explicitly mapped. |
| lifecycle_state / status | completed / blocked / degraded / failed / rejected / quarantined / candidate / accepted / finalized. | Must not be encoded as artifact_type except as documented source context. |

Authority remains a separate concept:

- artifact_type does not create truth.
- artifact_type does not create authority.
- artifact_type does not imply AcceptedEvidence.
- artifact_type does not authorize action.
- artifact_type does not write DRS.
- artifact_type does not create FinalOutput.
- source_artifact_type does not create truth.
- source_artifact_type does not create authority.
- Root remains final authority.

## 6. Recommended Patch: Option A

Recommended next actual patch:

recommended_next_patch: Option A docs/spec human-readable artifact vocabulary map

Option A should create a docs/spec human-readable artifact vocabulary map only.
It should not change runtime, schemas, tests, enums, registries, GT, Root, DRS,
Transition Matrix, or DRS lifecycle behavior.

Allowed future patch files for Option A:

- `specs/schema_package_v0_25_reference.md`
- `specs/invariants.md`
- `specs/human_passport_v0_25.md`
- `specs/machine_manifest_v0_25.json`
- `README.md`
- `AGENTS.md`

Optional if needed:

- `docs/artifact_type_mapping_runtime_vocabulary_v01.md`

No runtime changes.
No schema changes.
No tests yet.
No enum.
No registry.

Purpose of Option A:

Create a canonical human-readable map with columns or fields:

- term
- axis
- current field
- active runtime/proof/docs scope
- authority status
- lifecycle relation
- whether schema-backed
- whether enum-backed
- whether future schema action is recommended

Option A should explicitly separate:

- active runtime payload artifact_type values
- schema/report names
- proof taxonomy names
- audit/lifecycle source_artifact_type values
- lifecycle_state / status values
- EvidenceItem.kind values
- TraceRef.kind values
- Root-only final-output vocabulary

## 7. Option B Later

Option B:

Add small runtime constants only for active runtime payload artifact_type values.

Only possible after Option A and user approval.

Candidate runtime payload labels from the preflight:

- `generic_simulated_result`
- `request_payload`
- `field_validation`
- `submission_simulation`
- `visit_checklist`
- `visit_estimate`
- `delegation_requirements`
- `authorization_validation`
- `missing_requirements_research`
- `human_review_questions`
- `needle_runtime_result`

Constraints:

- constants only
- no authority semantics
- no schema enum
- no GT / Root / DRS changes
- preserve backward compatibility

Option B is useful only if repeated string usage becomes a maintenance risk
after the map is reviewed.

## 8. Option C Later / Not Now

Option C:

Schema enum for limited artifact_type values.

Recommendation:

Not now.

Reason:

artifact_type values are currently mixed families and a broad enum risks
overengineering and breakage.

Only reconsider after:

- Option A map
- Option B constants if needed
- runtime usage stabilizes
- proof-only terms are separated from active runtime payload terms

Option C must not include proof-only terms just because they appear in reports,
docs, audit rows, or Transition Matrix rows.

## 9. Option D Later

Option D:

Guardrail tests proving artifact_type / source_artifact_type do not create
authority.

Possible later tests:

- artifact_type does not create truth.
- artifact_type does not create authority.
- artifact_type does not imply AcceptedEvidence.
- artifact_type does not authorize action.
- artifact_type does not write DRS.
- artifact_type does not create FinalOutput.
- source_artifact_type does not create truth.
- source_artifact_type does not create authority.
- Root remains final authority.

Recommendation:

Good later after Option A, but not required for the docs-only map.

## 10. Option E Later

Option E:

Split source_artifact_type mapping from artifact_type mapping.

Recommendation:

Likely needed after Option A.

Reason:

source_artifact_type is used heavily by audit/lifecycle/proof layers and should
not be merged blindly with runtime payload artifact_type.

Option E should distinguish:

- audit source labels
- DRS lifecycle source labels
- proof report source labels
- active runtime payload artifact_type labels
- lifecycle_state / status labels

## 11. Explicitly Rejected Immediate Actions

Reject now:

- runtime artifact registry
- broad schema enum
- global artifact ontology
- artifact_type authority semantics
- source_artifact_type authority semantics
- changing FinalOutput schema
- changing GTReport schema
- changing DRSRecord schema
- changing Transition Matrix
- changing DRS lifecycle
- changing Root
- changing GT
- changing DRS
- activating Negative Trace layer
- activating Marennya / UP

These may be reconsidered only through later explicit preflight/plan work, and
only where they remain within the MVP boundary.

## 12. Patch Risk Assessment

Option A risk: low
Option B risk: low/medium
Option C risk: medium/high
Option D risk: low/medium
Option E risk: medium if done too early, low if docs-first

overengineering_risk_current_plan: low
overengineering_risk_broad_enum_now: high
authority_leakage_risk_current_plan: low
authority_leakage_risk_if_misdesigned: high
compatibility_risk_option_a: low
compatibility_risk_option_c_now: high

Risk notes:

- Option A is low risk because it records the map without changing behavior.
- Option B has low/medium risk because constants can be introduced safely, but
  only after the map confirms active runtime labels.
- Option C has medium/high risk now because payload labels, proof taxonomy
  terms, source artifact labels, and report names are not one enum family.
- Option D has low/medium risk because tests are useful, but may encode an
  incomplete model if added before the map.
- Option E is likely necessary, but doing it before Option A could blur the
  same distinction it is meant to clarify.

## 13. Recommended Next Command After This Plan

Do not patch automatically.

Recommended next layer after this patch plan:

- Guardian / user review of patch plan
- then Option A docs/spec map patch only if approved

Required next-step fields:

recommended_next_patch: Option A docs/spec human-readable artifact vocabulary map
recommended_next_patch_requires_user_approval: true
artifact_type_schema_enum_recommended_now: false
runtime_artifact_registry_recommended_now: false
artifact_type_mapping_needed: true
source_artifact_type_mapping_needed: true
evidenceitem_kind_remains_separate: true
root_remains_final_authority: true

## 14. Summary

artifact_type_mapping_runtime_vocabulary_patch_plan_v01_status: COMPLETE
patch_plan_only: true
patch_applied: false
preflight_commit: b4aaf8e
recommended_next_patch: Option A docs/spec human-readable artifact vocabulary map
recommended_next_patch_requires_user_approval: true
artifact_type_mapping_needed: true
source_artifact_type_mapping_needed: true
runtime_artifact_registry_recommended_now: false
artifact_type_schema_enum_recommended_now: false
broad_schema_enum_rejected_now: true
global_artifact_ontology_rejected_now: true
evidenceitem_kind_remains_separate: true
source_artifact_type_remains_separate: true
lifecycle_state_remains_separate: true
artifact_type_creates_truth: false
artifact_type_creates_authority: false
artifact_type_implies_accepted_evidence: false
artifact_type_authorizes_action: false
artifact_type_writes_drs: false
artifact_type_creates_finaloutput: false
source_artifact_type_creates_truth: false
source_artifact_type_creates_authority: false
root_remains_final_authority: true
production_ready_claimed: false
public_auditor_ready_claimed: false

Summary interpretation:

- artifact_type Mapping is needed.
- source_artifact_type Mapping is needed.
- EvidenceItem.kind remains separate and already aligned for current active
  evidence-boundary needs.
- Runtime registry work is not recommended now.
- artifact_type schema enum work is not recommended now.
- Broad schema enum is rejected now.
- Global artifact ontology is rejected now.
- Option A docs/spec human-readable artifact vocabulary map is the narrow next
  patch, pending user approval.
