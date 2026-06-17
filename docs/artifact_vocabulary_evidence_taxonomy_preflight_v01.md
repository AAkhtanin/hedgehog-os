# Artifact Vocabulary / Evidence Taxonomy Preflight v0.1

## 1. Status

artifact_vocabulary_evidence_taxonomy_preflight_v01_status: COMPLETE
preflight_only: true
patch_applied: false
runtime_modified: false
schemas_modified: false
tests_modified: false
evidence_kind_alignment_implemented: false
artifact_type_alignment_implemented: false
transition_matrix_modified: false
drs_lifecycle_modified: false
production_ready_claimed: false
public_auditor_ready_claimed: false

This is a read-only vocabulary preflight. It maps current terminology before any
EvidenceItem.kind or artifact_type patch.

Read-only scan commands used:

- `git status --short`
- `rg -n "EvidenceItem|kind|artifact_type|evidence_kind|observation|candidate|accepted|rejected|quarantine|quarantined|trace|report|proposal|audit|DRSRecord|RootFinal|GTReport|VVReport|ValidationReport|ResultProposal|ChildBoundarySnapshot|ConnectorObservation|EvidenceCandidate|AcceptedEvidence|NeedleCandidate|ManifestCandidate|SemanticDraft" schemas specs docs README.md AGENTS.md`
- `rg -n "artifact_type|evidence|evidence_kind|trace_refs|report|proposal|candidate|accepted|rejected|quarantine|deadend|audit|DRS|RootFinal|GTReport|VVReport|ValidationReport|ResultProposal|ChildBoundarySnapshot|ConnectorObservation|EvidenceCandidate|AcceptedEvidence|NeedleCandidate|ManifestCandidate|SemanticDraft" hedgehog demo tests`
- `rg -n "enum|additionalProperties|EvidenceItem|artifact_type|kind|status|decision|lifecycle|accepted|rejected|quarantined|deadend" schemas specs docs`
- `rg -n "accepted evidence|AcceptedEvidence|EvidenceCandidate|ValidationPacket|ConnectorObservation|AuditEvent|audit entry|hash|truth|authority|candidate|trace|report|artifact|artifact_type|EvidenceItem.kind" docs/audit_reports docs specs README.md AGENTS.md`
- `rg -n "Marennya|Negative Trace|negative trace|auto-hardening|manifest hardening|ManifestHardeningCandidate|GovernancePatchCandidate|Root decides|Root commit|trace signal|deadend|quarantine" docs specs README.md AGENTS.md`
- `sed -n` reads of active schema, runtime, demo, spec, and audit index files named below.

## 2. Context

Schema Contract Alignment v0.1 and Runtime JSON Schema Validation Hardening v0.1
are closed for the current Post V&V boundary:

- Architect-facing AttractorPacket contract now says Architect returns PlanGraph.
- Executor / DAG ResultProposal wording is clarified in canonical docs.
- Post V&V validates incoming ResultProposal artifacts at runtime.
- Post V&V validates outgoing VVReport dictionaries at runtime.
- Manual policy and safety checks remain in force.
- Root remains final authority.

The next risk is vocabulary drift, not runtime behavior drift. The project now
uses many related terms across schemas, runtime, proof runners, docs, and audit
reports:

- evidence vs accepted evidence
- artifact vs report vs trace
- candidate vs accepted artifact
- audit event vs truth
- artifact_type vs authority
- EvidenceItem.kind vs wider runtime and proof vocabulary

This preflight maps those terms before any patch. It does not assume the
vocabulary is wrong and does not collapse categories prematurely.

Required guardrail invariants for this vocabulary layer:

- artifact_type != authority
- evidence_kind != truth
- trace != accepted evidence
- audit_event != truth
- candidate != accepted artifact
- accepted evidence != action permission
- DRS record != authority
- GT report != final output
- ValidationPacket != Root acceptance
- AcceptedEvidence requires Root decision
- Root remains final authority

## 3. Current Vocabulary Inventory

| term | location / file family | current meaning | artifact_class | authority_status | lifecycle_state | notes / ambiguity |
| --- | --- | --- | --- | --- | --- | --- |
| EvidenceItem.kind | `schemas/common.schema.json`; `schemas/result_proposal.schema.json`; `hedgehog/executor.py`; `hedgehog/fractal_dag_executor.py`; `hedgehog/needle_runtime.py`; preflight docs | Schema enum for items inside ResultProposal.evidence. Active Executor uses `simulated_executor`; proof-level emitters also use values such as `fractal_dag_executor`, `audit`, and `needle_runtime`. | report | no_authority | validated | Active enum is narrower than all observed runtime/proof evidence terms. |
| artifact_type | `schemas/vv_report.schema.json`; `hedgehog/executor.py`; `hedgehog/post_vv.py`; `hedgehog/gt_validator.py`; Transition Matrix proof; DRS lifecycle proof | Free semantic label for result payload/report/transition/source artifact shape. | report | no_authority | validated | Used in multiple local vocabularies; not centralized and not an authority marker. |
| evidence | ResultProposal schema/runtime; docs; demos | Support material attached to a proposal or proof row. | report | advisory_only | validated | Generic term collides with accepted evidence wording unless qualified. |
| observation | connector sandbox; Demo B; docs | Read-only signal from a connector or external mock source. | observation | no_authority | draft | Observation is not truth and not accepted evidence. |
| ConnectorObservation | `demo/run_read_only_enterprise_connector_sandbox_v01.py`; Transition Matrix; docs | Dataclass/proof artifact for read-only connector signal. | observation | no_authority | candidate | It can feed EvidenceCandidate but cannot skip Root review. |
| EvidenceCandidate | External Evidence Acceptance Gate; Transition Matrix; docs/audits | Candidate built from observation for validation and Root review. | candidate | candidate_only | candidate | Candidate-only before Root decision. |
| ValidationPacket | External Evidence Acceptance Gate; Transition Matrix; docs/audits | Local validation result over EvidenceCandidate metadata. | validation_packet | advisory_only | validated | Not Root acceptance and not Root final. |
| AcceptedEvidence | External Evidence Acceptance Gate; Transition Matrix; Demo B docs | Root-reviewed accepted evidence artifact. | accepted_artifact | accepted_but_bounded | accepted | Requires Root decision; not truth, action, DRS write, ready status, or installed Needle. |
| RejectedEvidence | External Evidence Acceptance Gate; Transition Matrix | Root-reviewed rejection record for failed evidence candidate. | rejected_artifact | audit_only | rejected | Records rejection; no authority transfer. |
| QuarantinedEvidence | External Evidence Acceptance Gate; Transition Matrix | Root-reviewed quarantine record for unsafe or unknown candidate. | quarantine_artifact | audit_only | quarantined | Quarantine signal; not Work success. |
| ResultProposal | `schemas/result_proposal.schema.json`; `hedgehog/executor.py`; `hedgehog/fractal_dag_executor.py`; specs/tests | Executor output boundary. Active Executor output is schema-valid; Fractal DAG proof outputs may be ResultProposal-shaped. | proposal | no_authority | validated | Must pass Post V&V / GT / Root before final answer or writeback. |
| VVReport / ValidationReport | `schemas/vv_report.schema.json`; `hedgehog/post_vv.py`; Post V&V proofs | Post V&V report over ResultProposal boundary. | report | advisory_only | validated | Runtime-schema validated on outgoing boundary; not GT, Root, or final output. |
| GTReport | `schemas/gt_report.schema.json`; `hedgehog/gt_validator.py`; docs/tests | GT advisory selection/scoring report. | report | advisory_only | validated | GT report is not final output and cannot create AcceptedEvidence. |
| RootFinalOutput | `schemas/final_output.schema.json`; Root/runtime docs/tests | Final output created by RootOrchestrator. | final_output | root_only_authority | finalized_by_root | Only Root Final / Root Commit may be root_only_authority. |
| DRSRecord | `schemas/drs_record.schema.json`; DRS lifecycle docs/tests | Local memory/lineage/audit record with TimeEnvelope, layer, type, status, provenance. | memory_record | audit_only | audit_recorded | DRS is storage/topology, not decision authority. |
| AuditEvent | `demo/run_audit_hash_chain.py`; audit reports/docs | Audit/hash-chain entry linking source artifact type/id and canonical payload hash. | audit_event | audit_only | audit_recorded | Hash proves continuity/integrity in proof scope, not truth. |
| ExternalDRSPointer | candidate vector schema; External DRS Pointer Protocol docs; Transition Matrix | Pointer to external meaning trace/reference. | candidate | candidate_only | candidate | External pointer is not external DRS write, global DRS write, or provenance laundering. |
| ChildBoundarySnapshot | Fractal Cell, DRS lifecycle, audit hash chain, docs | Bounded child-cell boundary artifact or addressable experience. | boundary_snapshot | no_authority | completed | Child snapshot is not Root Final, installed Needle, or parent commit. |
| SemanticDraft | Bounded LLM Semantic Executor Node; Transition Matrix; Demo B | Bounded LLM draft payload before wrapping/validation. | semantic_draft | no_authority | draft | Not truth, final, action, DRS write, or Needle. |
| NeedleCandidate | NeedleCandidate lifecycle proof; Transition Matrix; docs/audits | Bounded proof-level candidate for future Root review. | candidate | candidate_only | candidate | Not installed Needle; Root alone disposes pending/rejected/quarantined candidate. |
| ManifestCandidate | Developer Facade / Capability Manifest UX proof; docs/audits | Candidate manifest for facade validation and Root review. | manifest_candidate | candidate_only | candidate | Validated manifest candidate is not installed capability or accepted evidence. |
| QuarantineRecord | DRS layer taxonomy, Marennya/UP schemas, audit reports | Quarantine-layer record for invalid/unsafe/unknown payloads or proposals. | quarantine_artifact | audit_only | quarantined | Not Work and not direct-reuse eligible. |
| DeadEnd / deadend | DRS layer taxonomy, DRSRecord schema, specs/audits | Stable bad route or broad proof deadend record. | lifecycle_record | audit_only | deadend | Current DeadEnds semantics are broad; not reusable without Root override. |
| trace | common TraceRef, specs, audit reports | Reference/path/projection of execution or proof flow. | trace | audit_only | audit_recorded | trace_refs are not evidence by themselves and not accepted evidence. |
| report | VVReport, GTReport, RunnerReport, audit reports | Structured output summarizing validation, scoring, execution, or audit. | report | advisory_only | validated | Report type must not imply authority. |
| proposal | ResultProposal, PlanGraph proposal, manifest/needle candidates | Proposed plan/result/capability for review. | proposal | candidate_only | candidate | Proposal remains subordinate until the appropriate boundary accepts it. |

## 4. Schema Vocabulary Evidence

Active schema files read:

- `schemas/common.schema.json`
- `schemas/result_proposal.schema.json`
- `schemas/vv_report.schema.json`
- `schemas/gt_report.schema.json`
- `schemas/final_output.schema.json`
- `schemas/drs_record.schema.json`
- `schemas/marenna_record.schema.json`
- `schemas/needle.schema.json`
- `schemas/up_record.schema.json`
- `schemas/candidate_vector.schema.json`
- `schemas/plan_graph.schema.json`

Current EvidenceItem.kind enum values in `schemas/common.schema.json`:

- `drs_record`
- `needle`
- `schema`
- `policy`
- `trace`
- `simulated_executor`
- `manual`

EvidenceItem schema facts:

- `schemas/common.schema.json` defines `$defs.EvidenceItem`.
- EvidenceItem requires `kind` and `summary`.
- Optional EvidenceItem fields are `ref_id` and `confidence`.
- EvidenceItem has `additionalProperties: false`.
- `schemas/result_proposal.schema.json` uses EvidenceItem for
  `ResultProposal.evidence`.

artifact_type schema facts:

- `schemas/vv_report.schema.json` has optional `artifact_type`.
- The active VVReport `artifact_type` references NonEmptyString.
- It is not an enum in active schema.
- `schemas/result_proposal.schema.json` does not define a formal
  `artifact_type` property inside `result_payload`; `result_payload` is an
  object that forbids `final_output` and `answer` but otherwise carries payload
  shape.
- `schemas/gt_report.schema.json` does not encode a top-level artifact_type;
  GT runtime reads it from V&V report metadata when available.
- `schemas/final_output.schema.json` does not encode artifact_type; it encodes
  Root-created FinalOutput with `created_by: root_orchestrator`.
- `schemas/drs_record.schema.json` uses `layer`, `type`, and `status`, not
  artifact_type.

Schemas for named evidence workflow artifacts:

- ConnectorObservation: no standalone schema found; represented in proof
  dataclasses and Transition Matrix taxonomy.
- EvidenceCandidate: no standalone schema found; represented in proof rows and
  Transition Matrix taxonomy.
- ValidationPacket: no standalone schema found; represented in proof rows and
  Transition Matrix taxonomy.
- AcceptedEvidence / RejectedEvidence / QuarantinedEvidence: no standalone
  schemas found; represented in proof rows, docs, and Transition Matrix.
- ChildBoundarySnapshot: no standalone schema found; represented in proof rows,
  DRS lifecycle records, and audit hash chain source artifact types.
- SemanticDraft: no standalone schema found; represented in proof runners/docs.
- NeedleCandidate / ManifestCandidate: no standalone schema found under those
  names; represented in proof runners/docs and related Needle schema/capability
  manifest artifacts.

Schema enum narrower than runtime/docs vocabulary:

- EvidenceItem.kind is narrower than observed proof/runtime evidence terms.
- Examples observed outside the active enum include `fractal_dag_executor`,
  `audit`, and `needle_runtime` as evidence kinds in runtime/proof code.
- Wider docs/proofs also use ConnectorObservation, EvidenceCandidate,
  ValidationPacket, AcceptedEvidence, AuditEvent, ChildBoundarySnapshot,
  SemanticDraft, NeedleCandidate, and ManifestCandidate as artifact terms.
- Some of those should likely remain artifacts rather than EvidenceItem.kind
  enum values, but the mapping is not explicit yet.

## 5. Runtime Vocabulary Evidence

Active runtime/proof files read:

- `hedgehog/post_vv.py`
- `hedgehog/executor.py`
- `hedgehog/fractal_dag_executor.py`
- `hedgehog/gt_validator.py`
- `hedgehog/needle_runtime.py` by grep evidence
- `hedgehog/root_orchestrator.py` by grep evidence
- `demo/run_read_only_enterprise_connector_sandbox_v01.py`
- `demo/run_external_evidence_acceptance_gate_v01.py`
- `demo/run_kernel_enforcement_transition_matrix_v01.py`
- `demo/run_drs_lifecycle_semantics.py` by grep evidence
- `demo/run_audit_hash_chain.py` by grep evidence

ResultProposal evidence field usage:

- `hedgehog/executor.py` emits active Executor ResultProposal evidence with
  `kind: simulated_executor`.
- `hedgehog/fractal_dag_executor.py` emits proof-level ResultProposal-shaped
  evidence with `kind: fractal_dag_executor`.
- `hedgehog/needle_runtime.py` grep evidence shows `kind: audit` and
  `kind: needle_runtime` around NeedleRuntime result artifacts.
- Runtime schema validation at Post V&V now means incoming active
  ResultProposal evidence kind must match the active enum when it crosses that
  boundary.

trace_refs usage:

- ResultProposal schema requires `trace_refs`.
- VVReport supports `trace_refs`.
- FinalOutput supports `trace_refs`.
- DRSRecord has provenance trace_refs and top-level trace_refs.
- Trace refs are linkage/audit references, not accepted evidence.

artifact_type usage:

- `hedgehog/executor.py` sets result payload `artifact_type` values such as
  `generic_simulated_result`, `request_payload`, `field_validation`,
  `submission_simulation`, `visit_checklist`, `visit_estimate`,
  `delegation_requirements`, `authorization_validation`,
  `missing_requirements_research`, and `human_review_questions`.
- `hedgehog/post_vv.py` reads `result_payload.artifact_type` and propagates it
  into outgoing VVReport when present.
- `hedgehog/gt_validator.py` reads `artifact_type` from V&V report or nested
  payload metadata.
- `demo/run_kernel_enforcement_transition_matrix_v01.py` uses `artifact_type`
  as a local transition taxonomy field with values like ConnectorObservation,
  EvidenceCandidate, ValidationPacket, AcceptedEvidence, ResultProposal,
  GTReport, RootFinalOutput, ExternalDRSPointer, NeedleCandidate, and others.
- `demo/run_drs_lifecycle_semantics.py` uses `source_artifact_type` for local
  lifecycle records, including `DRSWritebackAuditRecord`,
  `NeedleExecutionResult`, `ChildBoundarySnapshot`, `ChildExecutionResult`,
  `SyntheticRepeatedValidationSummary`, and `SyntheticNeedleCandidateDraft`.

DRS lifecycle records:

- `schemas/drs_record.schema.json` encodes `layer`, `type`, `status`,
  TimeEnvelope, provenance, validation, GT metadata, hash, previous_hash,
  trace_refs, and source_refs.
- DRS lifecycle proofs represent completed, degraded, blocked, failed,
  rejected, quarantined, deadend, and promotion_candidate states.
- DRS lifecycle is not changed by this preflight.

Audit events / audit hash references:

- `demo/run_audit_hash_chain.py` uses `source_artifact_type` and source artifact
  ids to build hash-chain entries.
- Audit reports repeatedly state audit hash proves continuity, not truth.
- AuditEvent should remain audit_only.

Child boundary snapshots:

- `hedgehog/fractal_dag_executor.py` counts child_boundary_snapshots and creates
  child-cell boundary payloads for non-atomic nodes.
- Fractal Cell and DRS lifecycle proofs represent ChildBoundarySnapshot as
  addressable experience, not Root Final and not installed Needle.

Connector observations and evidence candidates:

- `demo/run_read_only_enterprise_connector_sandbox_v01.py` defines
  ConnectorObservation as a read-only, proof-only observation with
  `final_effect: observation_only`.
- `demo/run_external_evidence_acceptance_gate_v01.py` creates
  EvidenceCandidate, ValidationPacket, AcceptedEvidence, RejectedEvidence, and
  QuarantinedEvidence proof rows.
- The Transition Matrix encodes allowed candidate/validation/Root-decision
  transitions and blocks illegal authority jumps.

SemanticDraft / LLM executor draft:

- Bounded LLM Semantic Executor Node proof and walkthrough use SemanticDraft as
  bounded LLM output.
- SemanticDraft is wrapped as a ResultProposal-shaped boundary and must still
  pass Post V&V, GT, and Root.

## 6. Docs / Passport Vocabulary Evidence

Passport/spec/docs evidence:

- `specs/human_passport_v0_25.md` states the canonical pipeline and repeatedly
  separates ResultProposal, VVReport / ValidationReport, GT, Root FinalOutput,
  DRS writeback, and audit.
- `specs/invariants.md` states Root-only FinalOutput, Executor-only
  ResultProposal, Post V&V before GT, GT advisory, DRS not authority, and
  EvidenceItem.kind / artifact_type work remaining open.
- `docs/passport_geometry_root_needles.md` states Root is the point of
  sovereignty, DRS is not authority, and child cells return boundary artifacts.
- `docs/audit_reports/README.md` records the closed audits for Post V&V
  incoming ResultProposal and outgoing VVReport runtime-schema boundaries, and
  states EvidenceItem.kind / artifact_type remain open.
- `docs/schema_contract_alignment_preflight_v01.md` already identified
  EvidenceItem.kind vocabulary mismatch and artifact_type mapping need.

Authority invariant language observed:

- Root creates FinalOutput.
- GT is advisory and does not commit final output.
- DRS is memory/topology/audit, not authority.
- ConnectorObservation is not truth or trusted evidence.
- EvidenceCandidate remains candidate_only.
- ValidationPacket is not Root acceptance.
- AcceptedEvidence requires Root decision and remains bounded.
- Audit hash decides no truth.
- NeedleCandidate is not installed Needle.

Negative Trace final decision:

Negative traces are future Marennya-readable trace signals, not an active artifact vocabulary layer and not a governance patch mechanism.

Marennya may consume negative trace signals later as one input class.
Marennya may propose candidates later.
Marennya may not patch anything.
Root decides.

This preflight rejects a separate Negative Trace layer for the current
vocabulary work. It also rejects a Negative Trace runtime, stub, or roadmap item
in this layer.

## 7. Drift / Ambiguity Findings

| finding | status | risk | patch_needed | recommended later patch target |
| --- | --- | --- | --- | --- |
| evidence_term_collision | open | medium | true | Docs/passport vocabulary sync and focused vocabulary tests. |
| evidenceitem_kind_enum_too_narrow | open | medium | true | EvidenceItem.kind Alignment v0.1. |
| artifact_type_usage_not_centralized | open | medium | true | artifact_type Mapping / Runtime Artifact Vocabulary v0.1. |
| accepted_evidence_vs_evidence_candidate_needs_clearer_contract | partially_covered | medium | true | Evidence workflow docs/schema comments and tests proving candidate-only boundary. |
| audit_event_vs_truth_needs_guardrail | partially_covered | low | false | Docs/test guardrail only unless schema introduces AuditEvent later. |
| child_boundary_snapshot_not_clearly_represented | open | medium | true | artifact_type mapping and optional boundary_snapshot artifact class pin. |
| connector_observation_not_cleanly_separated_from_evidence_candidate | partially_covered | medium | true | EvidenceItem.kind or artifact vocabulary map, not authority change. |
| semantic_draft_resultproposal_boundary_needs_vocabulary_pin | partially_covered | medium | true | Docs/spec vocabulary pin and possibly artifact_type mapping. |
| trace_refs_not_same_as_evidence | partially_covered | low | true | Focused tests/docs guardrail. |
| DRSRecord_not_authority_guardrail_needed | partially_covered | low | false | Keep guardrail in docs/tests; no DRS lifecycle change here. |

Notes:

- The Transition Matrix already captures many authority boundaries, but it is a
  proof taxonomy and not an active shared runtime artifact vocabulary.
- Active schemas distinguish some boundary types structurally, but many proof
  artifacts exist as dataclasses/dicts without standalone schemas.
- The immediate risk is public/auditor confusion more than current runtime
  authority failure.

## 8. Proposed Canonical Vocabulary Model

| canonical_name | artifact_class | authority_status | lifecycle_state | allowed_transitions_summary | forbidden_interpretations |
| --- | --- | --- | --- | --- | --- |
| Observation | observation | no_authority | draft | May become EvidenceCandidate through an explicit acceptance-gate path. | Not truth, not trusted evidence, not action, not DRS write. |
| ConnectorObservation | observation | no_authority | candidate | Connector sandbox may create it as read-only signal; Root review remains required. | Not AcceptedEvidence, not ready status, not authority. |
| EvidenceCandidate | candidate | candidate_only | candidate | May become ValidationPacket; may later be accepted/rejected/quarantined by Root. | Candidate must not imply accepted artifact or truth. |
| ValidationPacket | validation_packet | advisory_only | validated | May be submitted to Root review as validation evidence. | Not Root acceptance, not Root Final, not action permission. |
| AcceptedEvidence | accepted_artifact | accepted_but_bounded | accepted | Created only by Root decision from candidate/validation path. | Not truth, ready status, action authorization, DRS write, or installed Needle. |
| RejectedEvidence | rejected_artifact | audit_only | rejected | Created by Root decision to record failed candidate. | Not accepted evidence, not reusable success. |
| QuarantinedEvidence | quarantine_artifact | audit_only | quarantined | Created by Root decision for unsafe/unknown candidate. | Not Work, not accepted evidence, not direct reuse. |
| ResultProposal | proposal | no_authority | validated | Executor returns it; Post V&V consumes it; GT/Root remain downstream. | Not FinalOutput, not AcceptedEvidence, not action permission, not DRS write. |
| VVReport | report | advisory_only | validated | Post V&V creates it from ResultProposal and sends it toward GT. | Not GTReport, not Root Final, not authority. |
| GTReport | report | advisory_only | validated | GT creates advisory selection/scoring artifact for Root. | Not FinalOutput, not AcceptedEvidence, not truth. |
| RootFinalOutput | final_output | root_only_authority | finalized_by_root | RootOrchestrator creates final output / final commit artifact. | Must not be created by Executor, Post V&V, GT, DRS, child cells, Marennya, or UP. |
| DRSRecord | memory_record | audit_only | audit_recorded | Root-authorized local writeback may record Work, Quarantine, DeadEnds, UP, or Thoughts layers. | Not decision authority, not truth, not automatic reuse. |
| AuditEvent | audit_event | audit_only | audit_recorded | Records continuity/linkage/hash for source artifact. | Audit hash is not truth and not authority. |
| ChildBoundarySnapshot | boundary_snapshot | no_authority | completed | Child cell returns bounded snapshot upward; parent wraps into ResultProposal path. | Not Root Final, not installed Needle, not parent DRS write by itself. |
| SemanticDraft | semantic_draft | no_authority | draft | Bounded LLM output may be wrapped into ResultProposal-shaped boundary. | Not truth, action, final output, DRS write, or Needle. |
| NeedleCandidate | candidate | candidate_only | candidate | Root may keep pending review, reject, or quarantine. | Not installed Needle and not execution permission. |
| ManifestCandidate | manifest_candidate | candidate_only | candidate | Facade may validate candidate manifest for Root review input. | Not installed capability, AcceptedEvidence, or action permission. |

Model guidance:

- EvidenceItem.kind should describe evidence item role inside ResultProposal,
  not every artifact in the whole system.
- artifact_type should describe artifact shape/semantic payload class, not
  authority.
- lifecycle_state should describe where an artifact is in review or memory, not
  who can decide.
- authority_status should be explicit and separate from both schema kind and
  artifact_type.

## 9. Proposed Split for Future Patches

Recommended split:

1. EvidenceItem.kind Alignment v0.1
   - Decide whether active EvidenceItem.kind enum should expand, normalize, or
     accept a separate evidence_role/evidence_source map.
   - Keep ResultProposal evidence semantics narrow.
   - Add focused tests proving evidence_kind does not create truth or authority.
2. artifact_type Mapping / Runtime Artifact Vocabulary v0.1
   - Create a central map for runtime/proof artifact_type values and broader
     artifact classes.
   - Preserve separation from EvidenceItem.kind.
   - Include ResultProposal, VVReport, GTReport, RootFinalOutput,
     ChildBoundarySnapshot, ConnectorObservation, EvidenceCandidate,
     ValidationPacket, AcceptedEvidence, AuditEvent, DRSRecord, SemanticDraft,
     NeedleCandidate, and ManifestCandidate.
3. Docs / Passport Vocabulary Sync v0.1
   - Update high-level docs after reviewed vocabulary patches.
   - Keep Negative Trace wording as future Marennya-readable signal only.
4. Focused tests proving vocabulary does not create authority
   - candidate != accepted artifact
   - trace != accepted evidence
   - audit_event != truth
   - artifact_type != authority
   - EvidenceItem.kind != truth
   - AcceptedEvidence != action permission
   - DRSRecord != authority
   - GTReport != final output

EvidenceItem.kind and artifact_type should be patched separately. EvidenceItem.kind
is a schema enum inside ResultProposal evidence; artifact_type is a wider
artifact/payload/report vocabulary. Combining them would increase schema and
runtime breakage risk.

## 10. Non-goals

This preflight does not:

- modify schemas
- modify runtime
- modify tests
- align EvidenceItem.kind
- align artifact_type
- change Transition Matrix
- change DRS lifecycle
- create Negative Trace layer
- activate Marennya
- create authority semantics
- claim production readiness
- claim public-auditor readiness

## 11. Risks

vocabulary_drift_risk: medium
authority_leakage_from_terms_risk: medium
schema_enum_expansion_risk: medium
runtime_breakage_risk_if_patched_too_broadly: high
auditor_confusion_risk: medium

Risk notes:

- Vocabulary drift risk is medium because the project already has strong
  authority guardrails, but naming is spread across many artifact families.
- Authority leakage risk is medium because accepted/candidate/report/trace
  words can be misread without a central map.
- Schema enum expansion risk is medium because expanding EvidenceItem.kind could
  accidentally bless artifacts that should remain outside evidence items.
- Runtime breakage risk is high if EvidenceItem.kind and artifact_type are
  patched together or if proof-level ResultProposal-shaped outputs are forced
  through the active ResultProposal schema without normalization.
- Auditor confusion risk is medium because public review will ask whether
  observation, evidence, accepted evidence, report, and trace are distinct.

## 12. Recommended Next Step

Recommended next patch after review:

Proceed to EvidenceItem.kind Alignment v0.1 as the first narrow patch.

Reasoning:

- EvidenceItem.kind is the active schema enum now used by runtime Post V&V
  incoming ResultProposal validation.
- Active Executor evidence uses an enum member that fits today, while nearby
  proof-level emitters use evidence kinds that do not fit the active enum.
- Fixing or explicitly mapping EvidenceItem.kind first reduces runtime boundary
  ambiguity before broader artifact_type mapping.
- artifact_type should come second because it spans payload shape, report
  propagation, Transition Matrix taxonomy, DRS lifecycle source artifacts, and
  proof/audit terminology.

Patch shape should remain narrow:

- no DRS lifecycle change
- no Transition Matrix change
- no GT / Root / DRS authority change
- no Negative Trace layer
- no Marennya runtime
- focused schema/docs/test patch only after user approval

## 13. Summary

artifact_vocabulary_evidence_taxonomy_preflight_v01_status: COMPLETE
preflight_only: true
patch_applied: false
runtime_modified: false
schemas_modified: false
tests_modified: false
vocabulary_inventory_complete: true
evidenceitem_kind_alignment_needed: true
artifact_type_mapping_needed: true
negative_trace_layer_rejected: true
negative_traces_are_marennya_readable_trace_signals_only: true
root_remains_final_authority: true
recommended_next_patch_requires_user_approval: true
production_ready_claimed: false
public_auditor_ready_claimed: false
