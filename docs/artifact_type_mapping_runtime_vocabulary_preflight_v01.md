# artifact_type Mapping / Runtime Artifact Vocabulary Preflight v0.1

## 1. Status

artifact_type_mapping_runtime_vocabulary_preflight_v01_status: COMPLETE
preflight_only: true
patch_applied: false
runtime_modified: false
schemas_modified: false
tests_modified: false
artifact_type_mapping_implemented: false
runtime_artifact_registry_created: false
evidenceitem_kind_modified: false
transition_matrix_modified: false
drs_lifecycle_modified: false
production_ready_claimed: false
public_auditor_ready_claimed: false

This is a read-only preflight. It maps current artifact_type, source_artifact_type,
runtime artifact names, schema/report names, proof-row labels, and docs/passport
vocabulary before any patch.

Read-only scan commands used:

- `git status --short`
- `rg -n "artifact_type|source_artifact_type|result_payload|RootFinalOutput|RootFinalArtifact|ResultProposal|VVReport|ValidationReport|GTReport|DRSRecord|AuditEvent|TraceRef|ChildBoundarySnapshot|ConnectorObservation|EvidenceCandidate|ValidationPacket|AcceptedEvidence|RejectedEvidence|QuarantinedEvidence|SemanticDraft|NeedleCandidate|ManifestCandidate|NeedleExecutionResult|NeedleRuntimeResult|DRSWritebackAuditRecord|ExternalDRSPointer" hedgehog demo tests schemas specs docs README.md AGENTS.md`
- `rg -n "\"artifact_type\"|artifact_type =|source_artifact_type|result_payload" hedgehog demo tests`
- `rg -n "artifact_type|source_artifact_type|title|created_by|producer|report|proposal|final_output|additionalProperties|enum" schemas specs/schema_package_v0_25_reference.md`
- `rg -n "source_artifact_type|AuditEvent|audit hash|hash-chain|source artifact|artifact vocabulary|artifact_type Mapping|Runtime Artifact Vocabulary|artifact_type.*authority|artifact_type.*truth" docs specs README.md AGENTS.md demo tests`
- `rg -n "artifact_type.*authority|artifact_type.*truth|Root remains final authority|Root-only|FinalOutput|AcceptedEvidence|audit.*truth|DRS.*authority|GT.*advisory|ResultProposal.*FinalOutput|trace.*evidence" specs docs README.md AGENTS.md tests`
- `sed -n` reads of the schema, runtime, proof/demo, and prior vocabulary files named below.

## 2. Context

Guardian Passport accepted the completed current-stage Evidence Boundary
Hardening block as current-stage evidence boundary hardening, not full artifact
vocabulary completion.

Accepted current-stage results:

- `fractal_dag_executor` is accepted as EvidenceItem.kind for local
  ResultProposal evidence provenance.
- `audit` is accepted as EvidenceItem.kind for local NeedleRuntime
  ResultProposal evidence support/provenance.
- `needle_runtime` correctly remains trace_refs.kind only.
- Root-only authority is preserved.
- artifact_type Mapping / Runtime Artifact Vocabulary remains deferred and
  must be a separate later layer.

Closed current-stage chain:

- `8a76a49` Add Artifact Vocabulary Evidence Taxonomy preflight
- `2685921` Add EvidenceItem kind Alignment patch plan
- `4ced110` Align EvidenceItem kind for Fractal DAG executor evidence
- `0eb58c1` Add EvidenceItem kind Alignment audit log
- `3e35548` Document EvidenceItem kind Alignment checkpoint
- `99592a6` Add NeedleRuntime audit evidence shape preflight
- `fd9e862` Add NeedleRuntime audit evidence shape patch plan
- `f0bf7be` Normalize NeedleRuntime audit evidence shape
- `0b2ffc8` Add NeedleRuntime audit evidence shape audit log
- `9b8cfe7` Document NeedleRuntime audit evidence shape checkpoint

This preflight starts the separate artifact_type Mapping / Runtime Artifact
Vocabulary layer. It does not patch artifact_type, create a registry, modify
EvidenceItem.kind, or change authority semantics.

## 3. Current artifact_type Inventory

| term / value | field name | location / file family | current meaning | artifact_class | authority_status | lifecycle_state | schema-backed? | enum-backed? | notes / ambiguity |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| generic_simulated_result | result_payload.artifact_type | `hedgehog/executor.py` | Default deterministic Executor payload label. | proposal_payload | no_authority | completed | partial | no | Free string inside open ResultProposal payload. |
| request_payload | result_payload.artifact_type | `hedgehog/executor.py`, executor tests | Prepared request payload step. | proposal_payload | no_authority | completed | partial | no | Active Executor value; propagated to VVReport artifact_type. |
| field_validation | result_payload.artifact_type | `hedgehog/executor.py`, executor tests | Required field validation step. | proposal_payload | no_authority | needs_user | partial | no | Can be semantically needs-user without authority. |
| submission_simulation | result_payload.artifact_type | `hedgehog/executor.py` | Simulated submission step, blocked until user confirmation. | proposal_payload | no_authority | blocked | partial | no | Must not imply real submission/action. |
| visit_checklist | result_payload.artifact_type | `hedgehog/executor.py` | Visit checklist payload. | proposal_payload | no_authority | completed | partial | no | Domain-specific artifact_type value. |
| visit_estimate | result_payload.artifact_type | `hedgehog/executor.py` | Visit estimate payload. | proposal_payload | no_authority | completed | partial | no | Domain-specific artifact_type value. |
| delegation_requirements | result_payload.artifact_type | `hedgehog/executor.py` | Delegation requirements payload. | proposal_payload | no_authority | completed | partial | no | Domain-specific artifact_type value. |
| authorization_validation | result_payload.artifact_type | `hedgehog/executor.py` | Delegation/authorization validation payload. | proposal_payload | no_authority | needs_user | partial | no | Domain-specific and policy-sensitive label. |
| missing_requirements_research | result_payload.artifact_type | `hedgehog/executor.py` | Missing requirements research/questions. | proposal_payload | no_authority | draft | partial | no | Not AcceptedEvidence. |
| human_review_questions | result_payload.artifact_type | `hedgehog/executor.py` | Human review questions. | proposal_payload | no_authority | needs_user | partial | no | Not action authorization. |
| needle_runtime_result | result_payload.artifact_type | `hedgehog/needle_runtime.py`, NeedleRuntime tests | NeedleRuntime adapter ResultProposal payload. | proposal_payload | no_authority | completed/degraded/blocked/failed | partial | no | Active NeedleRuntime payload label; `needle_runtime` remains trace_refs.kind only. |
| ResultProposal | artifact name / transition artifact_type | schemas, runtime, Transition Matrix, docs | Executor proposal boundary. | proposal | no_authority | validated | yes | no | Schema exists; Transition Matrix also uses this as proof taxonomy value. |
| VVReport / ValidationReport / PostVVReport | schema/report/proof name | `schemas/vv_report.schema.json`, `hedgehog/post_vv.py`, Transition Matrix | Post V&V validation report. | report | advisory_only | validated | yes | no | VVReport has optional free-string artifact_type; PostVVReport is proof taxonomy spelling. |
| GTReport | schema/report/proof name | `schemas/gt_report.schema.json`, `hedgehog/gt_validator.py`, Transition Matrix | GT advisory report/selection. | report | advisory_only | validated | yes | partial | GT schema has candidate_type enum, not artifact_type. |
| RootFinalOutput | schema/proof name | `schemas/final_output.schema.json`, Transition Matrix, docs | Root-created final output. | final_output | root_only_authority | finalized_by_root | yes | no | No artifact_type field by design; `created_by` is const root_orchestrator. |
| RootFinalArtifact | proof/docs name | Root Final proof, DRS writeback proof/docs | Trace-level Root final artifact used by proofs. | final_output | root_only_authority | finalized_by_root | partial | no | Proof-level naming around FinalOutput boundary. |
| DRSRecord | schema/docs name | `schemas/drs_record.schema.json`, docs | Local memory/lineage/audit record. | memory_record | audit_only | audit_recorded | yes | partial | Uses layer/type/status, not artifact_type. |
| DRSWritebackAuditRecord | source_artifact_type | DRS lifecycle, audit hash-chain, DRS writeback docs | Root-final-derived local audit/writeback record. | audit_event | audit_only | audit_recorded | no | no | Proof source label, not active schema enum. |
| AuditEvent | docs/proof concept | audit hash-chain, specs/docs | Audit/hash-chain or event/provenance record. | audit_event | audit_only | audit_recorded | partial | no | Audit hash proves continuity, not truth. |
| TraceRef | schema ref | `schemas/common.schema.json`, runtime schemas | Trace metadata reference. | trace | audit_only | audit_recorded | yes | no | Trace metadata is not evidence by itself. |
| ConnectorObservation | proof dataclass / taxonomy value | read-only connector sandbox, Transition Matrix | Read-only connector observation. | observation | no_authority | candidate | no | no | Can feed EvidenceCandidate; not trusted evidence. |
| EvidenceCandidate | proof object / taxonomy value | external evidence gate, Transition Matrix | Candidate derived from observation. | candidate | candidate_only | candidate | no | no | Requires validation and Root review. |
| ValidationPacket | proof object / taxonomy value | external evidence gate, Transition Matrix | Local validation packet over candidate. | validation_packet | advisory_only | validated | no | no | Not Root acceptance. |
| AcceptedEvidence | proof object / taxonomy value | external evidence gate, Transition Matrix | Root-reviewed bounded accepted evidence. | accepted_artifact | accepted_but_bounded | accepted | no | no | Not truth, action, DRS write, or Needle. |
| RejectedEvidence | proof object / taxonomy value | external evidence gate, Transition Matrix | Root-reviewed rejected evidence. | rejected_artifact | audit_only | rejected | no | no | Rejection artifact only. |
| QuarantinedEvidence | proof object / taxonomy value | external evidence gate, Transition Matrix | Root-reviewed quarantined evidence. | quarantine_artifact | audit_only | quarantined | no | no | Quarantine signal only. |
| ChildBoundarySnapshot | source_artifact_type / proof name | Fractal Cell, DRS lifecycle, audit chain | Bounded child-cell boundary snapshot. | boundary_snapshot | no_authority | completed/degraded/blocked | no | no | Not Root Final or installed Needle. |
| ChildExecutionResult | source_artifact_type | Live Child Executor, DRS lifecycle, audit chain | Child executor boundary result. | boundary_snapshot | no_authority | completed/rejected | no | no | Boundary evidence only. |
| ChildExecutionResult/ChildBoundarySnapshot | source_artifact_type | audit hash-chain | Combined source label for live child boundary. | audit_event | audit_only | audit_recorded | no | no | Compound proof-only label; likely needs mapping rule. |
| SemanticDraft | proof object / taxonomy value | bounded LLM semantic executor, Transition Matrix | Bounded LLM draft. | semantic_draft | no_authority | draft | no | no | Not truth, ready status, DRS write, action, or Root final. |
| NeedleCandidate | proof object / taxonomy value | NeedleCandidate lifecycle, Transition Matrix | Candidate for future needle review. | candidate | candidate_only | candidate | partial | no | Not installed Needle. |
| ManifestCandidate | docs/proof concept | Developer Facade docs mention CapabilityManifestCandidate | Candidate manifest/capability artifact. | manifest_candidate | candidate_only | candidate | partial | no | Exact `ManifestCandidate` string is expected-but-not-found; `CapabilityManifestCandidate` appears in docs/audits. |
| NeedleExecutionResult | dataclass/source_artifact_type | `hedgehog/needle_runtime.py`, NeedleRuntime demos, DRS lifecycle | Bounded needle execution result. | proposal_payload | no_authority | completed/degraded/blocked/failed | partial | no | Evidence/result, not final truth. |
| NeedleRuntimeResult | expected concept | required concept scan | Expected-but-not-found exact term. | proposal_payload | no_authority | unknown | no | no | Current code uses `NeedleExecutionResult` and `needle_runtime_result`. |
| ExternalDRSPointer | schema enum/proof taxonomy | CandidateVector source enum, Transition Matrix, docs | Pointer to external meaning trace/reference. | candidate | candidate_only | candidate | partial | partial | Not external/global DRS write. |
| AppliedWarehouseSemanticDemoArtifact | source_artifact_type | applied warehouse demo/audit | Proof-level applied artifact source. | audit_event | audit_only | audit_recorded | no | no | Postcommit/source artifact label. |
| AppliedCertificateReadinessArtifact | source_artifact_type | applied certificate demo/audit | Proof-level applied artifact source. | audit_event | audit_only | audit_recorded | no | no | Postcommit/source artifact label. |
| AppliedDrsRetrievalReuseProofArtifact | source_artifact_type | applied DRS retrieval proof/audit | Proof-level source artifact. | audit_event | audit_only | audit_recorded | no | no | Proof-only label. |
| PermissionNeedsUserProofArtifact | source_artifact_type | permission/needs-user proof/audit | Proof-level source artifact. | audit_event | audit_only | audit_recorded | no | no | Proof-only label. |
| NeedleCandidateLifecycleProofArtifact | source_artifact_type | NeedleCandidate lifecycle proof/audit | Proof-level source artifact. | audit_event | audit_only | audit_recorded | no | no | Proof-only label. |
| SyntheticRepeatedValidationSummary | source_artifact_type | DRS lifecycle | Synthetic repeated-validation source. | lifecycle_record | candidate_only | promotion_candidate | no | no | Proof-only source label; mixes artifact and lifecycle concepts. |
| SyntheticNeedleCandidateDraft | source_artifact_type | DRS lifecycle | Synthetic draft needle candidate source. | manifest_candidate | candidate_only | promotion_candidate | no | no | Proof-only source label. |
| DrsLifecycleSemanticsReport | source_artifact_type | audit hash-chain | DRS lifecycle proof report source. | report | audit_only | audit_recorded | no | no | Proof report label. |
| ConflictCheckReport | source_artifact_type | audit hash-chain | ConflictCheck proof report source. | report | advisory_only | audit_recorded | no | no | ConflictCheck remains advisory until Root. |
| FinalDayCheckpointSummary | source_artifact_type | audit hash-chain | Final checkpoint summary source. | audit_event | audit_only | audit_recorded | no | no | Proof summary label. |

Observed artifact_type / source_artifact_type values are not centralized today.
They are not all the same class of thing: some are active runtime payload labels,
some are schema/report names, some are proof transition taxonomy values, and some
are audit/lifecycle source labels.

## 4. Schema Evidence

Files read:

- `schemas/common.schema.json`
- `schemas/result_proposal.schema.json`
- `schemas/vv_report.schema.json`
- `schemas/gt_report.schema.json`
- `schemas/final_output.schema.json`
- `schemas/drs_record.schema.json`
- `specs/schema_package_v0_25_reference.md`

Schema findings:

- `schemas/vv_report.schema.json` defines optional `artifact_type` as
  `NonEmptyString`.
- `artifact_type` in VVReport is free string, not enum-backed.
- `schemas/result_proposal.schema.json` does not formally define
  `result_payload.artifact_type`. It allows `result_payload` as an object while
  forbidding root/user-facing keys such as `final_output` and `answer`.
- ResultProposal therefore encodes artifact_type only indirectly when runtime
  payloads include that free-string field.
- `schemas/gt_report.schema.json` does not define top-level artifact_type.
  GTReport has `candidate_type` enum values such as `result_proposal`,
  `memory_record`, `marenna_patch`, `up_candidate`, and `protocol_template`.
- `schemas/final_output.schema.json` does not define artifact_type. It uses
  `created_by: root_orchestrator`, status, answer, used_proposals, gt_report_ref,
  drs_writes, time_envelope, summary, warnings, and trace_refs.
- `schemas/drs_record.schema.json` does not use artifact_type. It uses `layer`,
  `type`, `status`, provenance, validation, gt metadata, trace_refs, and
  source_refs.
- `source_artifact_type` was not found in active schemas; it appears in
  proof/demo/audit layers.
- EvidenceItem.kind remains separate from artifact_type and is scoped to
  `ResultProposal.evidence[*]`.

Schema interpretation:

- Active schema coverage is partial. VVReport can carry artifact_type as
  metadata, but no active schema centralizes payload, proof, report, and source
  artifact vocabulary.
- This does not prove a schema defect. It proves the vocabulary is not centrally
  mapped yet.

## 5. Runtime Evidence

Files read:

- `hedgehog/executor.py`
- `hedgehog/post_vv.py`
- `hedgehog/gt_validator.py`
- `hedgehog/needle_runtime.py`
- `hedgehog/fractal_dag_executor.py`

Runtime emitters:

- `hedgehog/executor.py` emits `result_payload.artifact_type` values:
  `generic_simulated_result`, `request_payload`, `field_validation`,
  `submission_simulation`, `visit_checklist`, `visit_estimate`,
  `delegation_requirements`, `authorization_validation`,
  `missing_requirements_research`, and `human_review_questions`.
- `hedgehog/needle_runtime.py` emits `result_payload.artifact_type:
  needle_runtime_result`.
- `hedgehog/fractal_dag_executor.py` emits ResultProposal-shaped payloads for
  atomic and child boundary cases, but no explicit artifact_type was found in
  that payload path.

Runtime consumers / propagation:

- `hedgehog/post_vv.py` reads `result_payload.artifact_type` through
  `_payload_semantics()`.
- If present and non-empty, Post V&V copies it into outgoing VVReport
  `artifact_type`.
- `hedgehog/gt_validator.py` reads artifact_type from the VVReport first, or
  from an optional embedded result_payload if present.
- GT uses artifact_type as metadata in `_metadata()`. The scanned code does not
  show artifact_type granting authority, action permission, DRS writeback, or
  FinalOutput creation.
- Root/FinalOutput schema and Root final proof docs preserve Root-only authority;
  no scanned Root boundary uses artifact_type as final authority.

Runtime flow:

```text
Executor / NeedleRuntime result_payload.artifact_type
-> Post V&V payload semantics
-> optional VVReport.artifact_type
-> GT metadata
-> Root remains final authority
```

Runtime interpretation:

- artifact_type currently behaves as semantic metadata.
- It is useful for report/classification and GT tie-break context, but the
  current scan did not find authority semantics.
- Runtime values are not centrally declared.

## 6. Proof / Demo Vocabulary Evidence

Transition Matrix:

- `demo/run_kernel_enforcement_transition_matrix_v01.py` defines a local
  `ARTIFACT_TYPES` tuple with values such as `ConnectorObservation`,
  `EvidenceCandidate`, `ValidationPacket`, `AcceptedEvidence`,
  `RejectedEvidence`, `QuarantinedEvidence`, `SemanticDraft`, `ResultProposal`,
  `PostVVReport`, `GTReport`, `RootFinalOutput`, `DRSWriteback`,
  `ExternalDRSPointer`, `NeedleCandidate`, `AuditHashClaim`,
  `ComputeCollapseMetric`, `ClosedCheckpointMetadata`, `LLMExecutorNode`,
  `MarennyaStub`, and `UPStub`.
- That taxonomy is local to Transition Matrix proof rows. It is not an active
  runtime artifact registry.
- Transition Matrix also defines allowed and blocked transitions, showing that
  these artifact names do not themselves carry authority.

DRS lifecycle:

- `demo/run_drs_lifecycle_semantics.py` uses `source_artifact_type` in
  experience records.
- Observed values include `DRSWritebackAuditRecord`, `NeedleExecutionResult`,
  `ChildBoundarySnapshot`, `ChildExecutionResult`,
  `SyntheticRepeatedValidationSummary`, and `SyntheticNeedleCandidateDraft`.
- DRS lifecycle records also carry `status`, `lifecycle_stage`,
  `promotion_state`, quarantine/deadend state, trust state, TTL state, and Root
  policy flags.
- This mixes source artifact labels with lifecycle state unless mapped
  carefully.

Audit hash-chain:

- `demo/run_audit_hash_chain.py` uses `source_artifact_type` for audit entries.
- Observed values include `DRSWritebackAuditRecord`, `NeedleExecutionResult`,
  `ChildBoundarySnapshot`, `ChildExecutionResult/ChildBoundarySnapshot`,
  `DrsLifecycleSemanticsReport`, `ConflictCheckReport`, and
  `FinalDayCheckpointSummary`.
- Audit hash-chain is proof-level continuity only. It does not decide truth,
  mutate DRS, grant authority, or replace GT/Root.

External evidence / connector evidence:

- `demo/run_read_only_enterprise_connector_sandbox_v01.py` defines
  ConnectorObservation proof dataclasses.
- `demo/run_external_evidence_acceptance_gate_v01.py` defines
  EvidenceCandidate, ValidationPacket, AcceptedEvidence, RejectedEvidence, and
  QuarantinedEvidence proof rows.
- Those proof artifacts are not active schemas and not artifact_type enum
  values.

Bounded LLM semantic executor:

- `demo/run_bounded_llm_semantic_executor_node_v01.py` uses `SemanticDraft` and
  wraps it as a ResultProposal-shaped output before Post V&V / GT / Root.
- SemanticDraft is not truth, final output, action, DRS write, or Needle.

Applied proof source artifacts:

- Applied demos and audit logs use `source_artifact_type` values such as
  `AppliedWarehouseSemanticDemoArtifact`, `AppliedCertificateReadinessArtifact`,
  `AppliedDrsRetrievalReuseProofArtifact`, `PermissionNeedsUserProofArtifact`,
  and `NeedleCandidateLifecycleProofArtifact`.
- These are proof/audit source labels and should not be collapsed into the same
  runtime payload vocabulary without review.

## 7. Drift / Ambiguity Findings

| finding | status | risk | patch_needed | recommended later patch target |
| --- | --- | --- | --- | --- |
| artifact_type_free_string_without_central_map | open | medium | true | Docs/spec mapping plan, then optional constants. |
| result_payload_artifact_type_not_formally_declared | open | medium | true | Map active runtime payload values before schema decision. |
| vvreport_artifact_type_is_free_string | partially_covered | low | true | Keep free string short-term; document allowed/current values. |
| gtreport_artifact_type_indirect_only | by_design | low | false | Document that GT reads metadata but schema uses candidate_type. |
| finaloutput_has_no_artifact_type_by_design | by_design | low | false | Keep FinalOutput Root-created; no artifact_type needed now. |
| drsrecord_uses_layer_type_status_not_artifact_type | by_design | low | false | Map relation between DRS layer/type/status and artifact_type terms. |
| source_artifact_type_not_centralized | open | medium | true | Source artifact map for audit and DRS lifecycle labels. |
| proof_taxonomy_values_not_separated_from_runtime_values | open | medium | true | Separate runtime payload labels from proof taxonomy labels. |
| artifact_type_vs_authority_guardrail_needed | partially_covered | medium | true | Add explicit docs/test guardrails in later patch. |
| artifact_type_vs_lifecycle_state_mixed | open | medium | true | Keep lifecycle_state separate from artifact_type and source_artifact_type. |
| artifact_type_vs_evidence_kind_separation_needed | partially_covered | low | true | Preserve EvidenceItem.kind as local ResultProposal evidence classification. |

Finding interpretation:

- The risk is public/reviewer ambiguity and future patch drift, not current
  Root authority failure.
- No scan evidence showed artifact_type currently creates FinalOutput, writes
  DRS, executes action, or grants authority.
- A broad schema enum now would likely be brittle because proof taxonomy,
  source artifact labels, and runtime payload labels are not the same layer.

## 8. Proposed Canonical Model

Do not patch now. Proposed separation:

- artifact_type = what kind of runtime/proof artifact this is.
- source_artifact_type = what source artifact a lifecycle/audit entry points to.
- evidence_kind = what kind/source of evidence item inside ResultProposal this
  is.
- lifecycle_state = where the artifact is in review/execution/memory.
- authority_status = whether it can decide anything.

Proposed guardrails:

- artifact_type does not grant authority.
- artifact_type does not create truth.
- artifact_type does not imply AcceptedEvidence.
- artifact_type does not authorize action.
- artifact_type does not write DRS.
- artifact_type does not create FinalOutput.
- source_artifact_type does not create truth.
- source_artifact_type does not create authority.
- RootFinalOutput is created only by Root.
- GTReport remains advisory.
- DRSRecord remains memory/audit, not authority.
- AuditEvent remains audit/provenance, not truth.
- TraceRef remains trace metadata, not evidence by itself.
- EvidenceItem.kind remains separate from artifact_type.

Proposed artifact classes:

- runtime_payload_label: current ResultProposal payload artifact_type values.
- report_type: ResultProposal, VVReport, GTReport, DRS lifecycle reports.
- proof_transition_type: Transition Matrix artifact names.
- source_artifact_type: DRS lifecycle and audit hash-chain source labels.
- final_output: RootFinalOutput / RootFinalArtifact.
- memory_record: DRSRecord and related lifecycle records.
- audit_event: AuditEvent and hash-chain entries.
- candidate_artifact: EvidenceCandidate, NeedleCandidate, ManifestCandidate.
- validation_packet: ValidationPacket / VVReport.

## 9. Patch Options

| option | safety impact | schema compatibility | runtime breakage risk | authority leakage risk | testability | recommendation |
| --- | --- | --- | --- | --- | --- | --- |
| Option A - Create central docs-only artifact_type map first, no schema enum yet | High; clarifies without changing behavior. | High; no schema changes. | Low. | Low if guardrails are explicit. | Medium; grep/docs tests possible later. | Recommended first. |
| Option B - Create runtime artifact vocabulary constants / registry for known values, no authority semantics | Medium-high; reduces drift in emitters. | High if no schema enum. | Medium because emitters/tests may import constants. | Medium unless guardrails are pinned. | High with focused tests. | Recommended after a patch plan, not directly from this preflight. |
| Option C - Add schema enum for artifact_type in limited places | Medium; can harden VVReport/runtime payload if scoped. | Medium-low now because values span layers and ResultProposal payload is open. | High if proof/runtime values are incomplete. | Medium. | High but brittle. | Not recommended now. |
| Option D - Keep artifact_type as free string but add guardrail tests and docs mapping | Medium; protects authority boundaries while preserving flexibility. | High. | Low. | Low. | Medium-high. | Recommended as part of early patch plan. |
| Option E - Split artifact_type from source_artifact_type and lifecycle_state through separate layers | High; best conceptual clarity. | High if docs-first. | Medium if runtime changes later. | Low if staged. | Medium. | Recommended as staged model, not a single broad patch. |

## 10. Recommended Next Step

recommended_next_step: create artifact_type Mapping / Runtime Artifact Vocabulary Patch Plan v0.1.

Recommended plan direction:

- Start with a docs/spec mapping patch plan, not code.
- Do not introduce a broad schema enum yet.
- Do not create a runtime registry yet.
- Separate runtime payload artifact_type values from proof Transition Matrix
  artifact names and source_artifact_type values.
- Preserve EvidenceItem.kind as a separate local ResultProposal evidence
  classification.
- Keep lifecycle_state separate from artifact_type.
- Add future tests only after the map is reviewed, proving artifact_type and
  source_artifact_type do not create authority, truth, AcceptedEvidence, action
  permission, DRS write, or FinalOutput.

## 11. Authority Guardrails for Future Patch

Future tests or docs must prove:

- artifact_type does not create truth.
- artifact_type does not create authority.
- artifact_type does not imply AcceptedEvidence.
- artifact_type does not authorize action.
- artifact_type does not write DRS.
- artifact_type does not create FinalOutput.
- source_artifact_type does not create truth.
- source_artifact_type does not create authority.
- Root remains final authority.

## 12. Non-goals

This preflight does not:

- patch runtime
- patch schemas
- patch tests
- create artifact_type enum
- create runtime registry
- modify EvidenceItem.kind
- modify ResultProposal schema
- modify VVReport schema
- modify GTReport schema
- modify FinalOutput schema
- modify DRS schema
- modify GT / Root / DRS
- modify Transition Matrix
- modify DRS lifecycle
- create Negative Trace layer
- activate Marennya
- claim production readiness
- claim public-auditor readiness

## 13. Risks

artifact_type_drift_risk: medium
authority_leakage_from_artifact_type_risk: medium
schema_enum_breakage_risk: high
runtime_registry_breakage_risk: medium
auditor_confusion_risk: medium

Risk notes:

- Drift risk is medium because active runtime payload labels, proof taxonomy
  values, and source artifact labels are not centralized.
- Authority leakage risk is medium because terms such as RootFinalOutput,
  AcceptedEvidence, and AuditEvent can be misread without guardrails.
- Schema enum breakage risk is high if attempted before separating value
  families.
- Runtime registry breakage risk is medium because emitters/tests currently use
  string literals.
- Auditor confusion risk is medium until the map is explicit.

## 14. Summary

artifact_type_mapping_runtime_vocabulary_preflight_v01_status: COMPLETE
preflight_only: true
patch_applied: false
runtime_modified: false
schemas_modified: false
tests_modified: false
artifact_type_mapping_needed: true
runtime_artifact_registry_needed: true
artifact_type_schema_enum_recommended_now: false
source_artifact_type_mapping_needed: true
evidenceitem_kind_remains_separate: true
root_remains_final_authority: true
recommended_next_patch_requires_user_approval: true
production_ready_claimed: false
public_auditor_ready_claimed: false

Recommendation summary:

- artifact_type Mapping is needed.
- source_artifact_type Mapping is needed.
- A runtime artifact registry may be useful later, but should not be created in
  this preflight.
- A schema enum is not recommended now.
- The next step should be a reviewed patch plan for artifact_type Mapping /
  Runtime Artifact Vocabulary.
