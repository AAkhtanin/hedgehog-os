# artifact_type Mapping / Runtime Artifact Vocabulary v0.1

## 1. Status

artifact_type_mapping_runtime_vocabulary_v01_status: implemented_docs_spec_map_only
option_selected: Option A docs/spec human-readable artifact vocabulary map
preflight_commit: b4aaf8e
patch_plan_commit: c4f9a02
runtime_modified: false
schemas_modified: false
tests_modified: false
registry_created: false
enum_created: false
evidenceitem_kind_modified: false
transition_matrix_modified: false
drs_lifecycle_modified: false
gt_modified: false
root_modified: false
drs_modified: false
negative_trace_layer_created: false
marennya_activated: false
production_ready_claimed: false
public_auditor_ready_claimed: false

This is Option A only: a docs/spec human-readable artifact vocabulary map.
It implements no runtime registry, no schema enum, no runtime behavior change,
and no test change.

Core principle:

Map first, constrain later, enum last if still needed.

## 2. Canonical Separation

artifact_type:

- Meaning: what kind of runtime/proof/report artifact this is.
- Role: semantic metadata / classification only.
- Authority: does not decide anything.

EvidenceItem.kind / evidence_kind:

- Meaning: local ResultProposal evidence classification/source/provenance.
- Current active needs include `fractal_dag_executor` and `audit`.
- It remains separate from artifact_type.

source_artifact_type:

- Meaning: audit/lifecycle/proof source label.
- It indicates where an audit/lifecycle/proof record came from.
- It remains separate from active runtime payload artifact_type unless
  explicitly mapped.

TraceRef.kind:

- Meaning: trace metadata reference type.
- It is not evidence by itself.
- It is not EvidenceItem.kind.

lifecycle_state / status:

- Meaning: where the artifact is in process, such as completed, blocked,
  degraded, failed, rejected, quarantined, candidate, accepted, or finalized.
- It remains separate from artifact_type.

authority_status:

- Meaning: whether an artifact can decide anything.
- RootFinalOutput is Root-created only.
- GTReport is advisory.
- DRSRecord is memory/audit.
- AuditEvent is provenance/continuity.
- AcceptedEvidence is Root-reviewed accepted evidence but not action
  permission by itself.

## 3. Vocabulary Map

| term | axis | current field / location | active runtime/proof/docs scope | authority_status | lifecycle_relation | schema_backed | enum_backed | future_schema_action | notes |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| generic_simulated_result | artifact_type | `result_payload.artifact_type` in Executor payloads | active runtime payload label | no_authority | completed payload | partial | no | map first, no enum now | Default deterministic Executor artifact label. |
| request_payload | artifact_type | `result_payload.artifact_type` | active runtime payload label | no_authority | completed payload | partial | no | map first, no enum now | Prepared request payload step. |
| field_validation | artifact_type | `result_payload.artifact_type` | active runtime payload label | no_authority | needs_user or blocked payload | partial | no | map first, no enum now | Field-check payload; lifecycle remains separate. |
| submission_simulation | artifact_type | `result_payload.artifact_type` | active runtime payload label | no_authority | blocked until permission | partial | no | map first, no enum now | Simulation label, not real submission. |
| visit_checklist | artifact_type | `result_payload.artifact_type` | active runtime payload label | no_authority | completed payload | partial | no | map first, no enum now | Domain-specific checklist payload. |
| visit_estimate | artifact_type | `result_payload.artifact_type` | active runtime payload label | no_authority | completed payload | partial | no | map first, no enum now | Domain-specific estimate payload. |
| delegation_requirements | artifact_type | `result_payload.artifact_type` | active runtime payload label | no_authority | completed payload | partial | no | map first, no enum now | Delegation requirement artifact. |
| authorization_validation | artifact_type | `result_payload.artifact_type` | active runtime payload label | no_authority | needs_user or blocked payload | partial | no | map first, no enum now | Authorization check label, not authority. |
| missing_requirements_research | artifact_type | `result_payload.artifact_type` | active runtime payload label | no_authority | draft or needs_user payload | partial | no | map first, no enum now | Research/questions payload, not AcceptedEvidence. |
| human_review_questions | artifact_type | `result_payload.artifact_type` | active runtime payload label | no_authority | needs_user payload | partial | no | map first, no enum now | Human review payload, not action authorization. |
| needle_runtime_result | artifact_type | `result_payload.artifact_type` in NeedleRuntime adapter | active runtime payload label | no_authority | completed/degraded/blocked/failed payload | partial | no | map first, no enum now | NeedleRuntime payload label; `needle_runtime` remains TraceRef.kind only. |
| ResultProposal | schema/report artifact name | `schemas/result_proposal.schema.json`, runtime boundary | active schema/runtime boundary | no_authority | proposed/validated boundary input | yes | no | none now | Executor proposal, not FinalOutput. |
| VVReport | schema/report artifact name | `schemas/vv_report.schema.json`, Post V&V output | active schema/runtime report | advisory_only | validated/rejected/needs_revision report | yes | no | none now | Optional free-string artifact_type metadata. |
| ValidationReport | schema/report artifact name | docs/runtime synonym for VVReport | active docs/runtime report term | advisory_only | validation report | partial | no | none now | Synonym family around VVReport. |
| PostVVReport | proof taxonomy value | Transition Matrix proof terminology | proof-only taxonomy label | advisory_only | validation report | no | no | do not copy into runtime enum now | Proof spelling for Post V&V report. |
| GTReport | schema/report artifact name | `schemas/gt_report.schema.json`, GT output | active schema/runtime report | advisory_only | selection/advisory report | yes | partial | none now | Uses `candidate_type`, not top-level artifact_type. |
| RootFinalOutput | schema/report artifact name | `schemas/final_output.schema.json` | active Root final boundary | root_only_authority | finalized_by_root | yes | no | none now | No artifact_type by design; Root-created only. |
| DRSRecord | schema/report artifact name | `schemas/drs_record.schema.json` | active memory/audit schema | audit_only | memory/audit record | yes | partial | none now | Uses layer/type/status, not artifact_type. |
| ConnectorObservation | proof taxonomy term | connector sandbox proof rows | proof/demo term | no_authority | observation/candidate | no | no | docs map only | Read-only observation, not accepted evidence. |
| EvidenceCandidate | proof taxonomy term | external evidence gate proof rows | proof/demo term | candidate_only | candidate | no | no | docs map only | Candidate requiring validation and Root review. |
| ValidationPacket | proof taxonomy term | external evidence gate proof rows | proof/demo term | advisory_only | validated packet | no | no | docs map only | Validation packet is not Root acceptance. |
| AcceptedEvidence | proof taxonomy term | external evidence gate proof rows | proof/demo term | accepted_but_bounded | accepted evidence | no | no | docs map only | Root-reviewed accepted evidence; not action permission by itself. |
| RejectedEvidence | proof taxonomy term | external evidence gate proof rows | proof/demo term | audit_only | rejected | no | no | docs map only | Rejection record only. |
| QuarantinedEvidence | proof taxonomy term | external evidence gate proof rows | proof/demo term | audit_only | quarantined | no | no | docs map only | Quarantine signal only. |
| SemanticDraft | proof taxonomy term | bounded LLM semantic executor proof | proof/demo term | no_authority | draft | no | no | docs map only | Bounded draft, not truth or final output. |
| NeedleCandidate | proof taxonomy term | NeedleCandidate lifecycle proof | proof/demo term | candidate_only | candidate | partial | no | docs map only | Candidate for future Needle review, not installed Needle. |
| ManifestCandidate | proof/docs term | docs/audits, CapabilityManifestCandidate family | docs/proof term | candidate_only | candidate | partial | no | docs map only | Expected term family; not active runtime enum. |
| ExternalDRSPointer | proof/schema-adjacent term | CandidateVector source enum and proof taxonomy | proof/docs term | candidate_only | candidate/source pointer | partial | partial | docs map only | Pointer/reference, not global DRS write. |
| DRSWritebackAuditRecord | source_artifact_type | DRS lifecycle and audit hash-chain source label | audit/lifecycle/proof label | audit_only | audit_recorded | no | no | source map later | Source label for Root-final-derived writeback audit. |
| NeedleExecutionResult | source_artifact_type | NeedleRuntime / DRS lifecycle / audit hash-chain | audit/lifecycle/proof label | no_authority | completed/degraded/blocked/failed | partial | no | source map later | Needle result evidence, not final truth. |
| ChildBoundarySnapshot | source_artifact_type | Fractal child boundary / DRS lifecycle / audit hash-chain | audit/lifecycle/proof label | no_authority | boundary snapshot | no | no | source map later | Bounded child-cell boundary evidence. |
| ChildExecutionResult | source_artifact_type | live child executor proof / DRS lifecycle | audit/lifecycle/proof label | no_authority | boundary result | no | no | source map later | Child execution result, not Root. |
| ChildExecutionResult/ChildBoundarySnapshot | source_artifact_type | audit hash-chain source label | proof-only compound source label | audit_only | audit_recorded | no | no | source map later | Compound proof label needing later cleanup/mapping. |
| DrsLifecycleSemanticsReport | source_artifact_type | audit hash-chain source label | proof/audit label | audit_only | audit_recorded | no | no | source map later | DRS lifecycle proof report source. |
| ConflictCheckReport | source_artifact_type | audit hash-chain source label | proof/audit label | advisory_only | audit_recorded | no | no | source map later | ConflictCheck report source; advisory until Root. |
| FinalDayCheckpointSummary | source_artifact_type | audit hash-chain source label | proof/audit label | audit_only | audit_recorded | no | no | source map later | Final checkpoint summary source. |
| AppliedWarehouseSemanticDemoArtifact | source_artifact_type | applied warehouse proof/audit | proof/audit label | audit_only | audit_recorded | no | no | source map later | Applied proof source label. |
| AppliedCertificateReadinessArtifact | source_artifact_type | applied certificate proof/audit | proof/audit label | audit_only | audit_recorded | no | no | source map later | Applied proof source label. |
| AppliedDrsRetrievalReuseProofArtifact | source_artifact_type | applied DRS retrieval proof/audit | proof/audit label | audit_only | audit_recorded | no | no | source map later | Applied proof source label. |
| PermissionNeedsUserProofArtifact | source_artifact_type | permission/needs-user proof/audit | proof/audit label | audit_only | audit_recorded | no | no | source map later | Applied proof source label. |
| NeedleCandidateLifecycleProofArtifact | source_artifact_type | NeedleCandidate lifecycle proof/audit | proof/audit label | audit_only | audit_recorded | no | no | source map later | Lifecycle proof source label. |
| SyntheticRepeatedValidationSummary | source_artifact_type | DRS lifecycle proof | proof/lifecycle label | candidate_only | promotion_candidate | no | no | source map later | Synthetic proof source; lifecycle state remains separate. |
| SyntheticNeedleCandidateDraft | source_artifact_type | DRS lifecycle proof | proof/lifecycle label | candidate_only | promotion_candidate | no | no | source map later | Synthetic draft source; not installed Needle. |
| RootFinalArtifact | boundary/authority vocabulary | Root final proof/docs | proof-level final artifact term | root_only_authority | finalized_by_root | partial | no | docs map only | Trace-level Root final artifact family. |
| AuditEvent | boundary/authority vocabulary | audit docs/hash-chain | audit/provenance term | audit_only | audit_recorded | partial | no | docs map only | Audit/provenance, not truth. |
| TraceRef | boundary/authority vocabulary | common schema trace refs | trace metadata | audit_only | audit_recorded | yes | no | docs map only | Trace metadata reference, not evidence by itself. |
| EvidenceItem.kind | boundary/authority vocabulary | ResultProposal evidence item field | active local evidence classification | no_authority | evidence support/provenance | yes | yes | already aligned for current active needs | Not artifact_type and not global registry. |
| artifact_type | boundary/authority vocabulary | runtime payload/VVReport metadata when present | classification metadata | no_authority | separate from status | partial | no | map first, enum later only if needed | What kind of artifact this is; not authority. |
| source_artifact_type | boundary/authority vocabulary | audit/lifecycle/proof source labels | proof/audit source metadata | audit_only | audit_recorded/source context | no | no | split later if needed | Source label, not active runtime artifact_type. |
| lifecycle_state | boundary/authority vocabulary | status/lifecycle fields in reports/proofs | process state | no_authority | process state | partial | partial | keep separate | completed/blocked/degraded/etc. |
| authority_status | boundary/authority vocabulary | docs/spec concept | authority classification | varies by artifact | separate axis | no | no | keep docs concept | Only Root final authority can finalize output. |

## 4. Guardrails

artifact_type_creates_truth: false
artifact_type_creates_authority: false
artifact_type_implies_accepted_evidence: false
artifact_type_authorizes_action: false
artifact_type_writes_drs: false
artifact_type_creates_finaloutput: false
source_artifact_type_creates_truth: false
source_artifact_type_creates_authority: false
evidenceitem_kind_creates_truth: false
evidenceitem_kind_creates_authority: false
trace_ref_creates_evidence: false
audit_event_creates_truth: false
audit_hash_creates_truth: false
accepted_evidence_authorizes_action_by_itself: false
gt_report_is_advisory: true
drs_record_is_memory_not_authority: true
root_final_output_created_only_by_root: true
root_remains_final_authority: true

Interpretation:

- artifact_type is metadata/classification only.
- source_artifact_type is provenance/source metadata only.
- EvidenceItem.kind is local ResultProposal evidence classification only.
- TraceRef.kind is trace metadata only.
- lifecycle_state/status is process state only.
- authority_status records who can decide; it is not inferred from naming.

## 5. Recommendations

runtime_artifact_registry_recommended_now: false
artifact_type_schema_enum_recommended_now: false
broad_schema_enum_rejected_now: true
global_artifact_ontology_rejected_now: true
runtime_constants_option_b_deferred: true
source_artifact_type_option_e_deferred: true
guardrail_tests_option_d_deferred: true
future_schema_enum_option_c_deferred: true

Recommendation notes:

- Do not create a runtime artifact registry from this map.
- Do not create an artifact_type schema enum from this map.
- Do not move proof-only terms into active runtime payload vocabulary.
- Do not change GT, Root, DRS, Transition Matrix, or DRS lifecycle behavior.
- Use this map as the reviewed vocabulary baseline for later staged work.

## 6. Future Work

Option B:

- Small runtime constants for active runtime payload artifact_type values only.
- Later if needed, after review.
- No authority semantics.
- No schema enum.
- No GT / Root / DRS changes.

Option C:

- Limited schema enum later only after runtime vocabulary stabilizes.
- Not recommended now.
- Must not include proof-only or source_artifact_type terms blindly.

Option D:

- Guardrail tests later proving artifact_type / source_artifact_type do not
  create truth, authority, AcceptedEvidence, action permission, DRS write, or
  FinalOutput.
- Not required for this docs/spec map.

Option E:

- source_artifact_type mapping split later.
- Needed because source_artifact_type is heavily used by audit/lifecycle/proof
  layers and should not be merged blindly with runtime payload artifact_type.

No GT / Root / DRS / Transition Matrix / DRS lifecycle changes are made in
this map.

## 7. Summary

artifact_type_mapping_runtime_vocabulary_v01_status: implemented_docs_spec_map_only
option_selected: Option A docs/spec human-readable artifact vocabulary map
preflight_commit: b4aaf8e
patch_plan_commit: c4f9a02
runtime_modified: false
schemas_modified: false
tests_modified: false
registry_created: false
enum_created: false
evidenceitem_kind_modified: false
transition_matrix_modified: false
drs_lifecycle_modified: false
gt_modified: false
root_modified: false
drs_modified: false
negative_trace_layer_created: false
marennya_activated: false
artifact_type_creates_truth: false
artifact_type_creates_authority: false
artifact_type_implies_accepted_evidence: false
artifact_type_authorizes_action: false
artifact_type_writes_drs: false
artifact_type_creates_finaloutput: false
source_artifact_type_creates_truth: false
source_artifact_type_creates_authority: false
evidenceitem_kind_creates_truth: false
evidenceitem_kind_creates_authority: false
trace_ref_creates_evidence: false
audit_event_creates_truth: false
audit_hash_creates_truth: false
accepted_evidence_authorizes_action_by_itself: false
gt_report_is_advisory: true
drs_record_is_memory_not_authority: true
root_final_output_created_only_by_root: true
root_remains_final_authority: true
runtime_artifact_registry_recommended_now: false
artifact_type_schema_enum_recommended_now: false
broad_schema_enum_rejected_now: true
global_artifact_ontology_rejected_now: true
runtime_constants_option_b_deferred: true
source_artifact_type_option_e_deferred: true
guardrail_tests_option_d_deferred: true
future_schema_enum_option_c_deferred: true
production_ready_claimed: false
public_auditor_ready_claimed: false
