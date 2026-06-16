# Schema Contract Alignment / Runtime Schema Validation Hardening v0.1 - Preflight Scan

## 1. Status

status: read_only_preflight_scan
patch_applied: false
schemas_modified: false
runtime_modified: false
tests_modified: false
production_claim_created: false

This report is a read-only inventory. It records contract drift and validation gaps before any schema, runtime, Post V&V, or test patch is attempted.

Scan commands used:

- `git status --short`
- `find schemas specs docs demo tests src -maxdepth 3 -type f \( -name '*schema*' -o -name '*.py' -o -name '*.md' -o -name '*.json' \)`
- `rg -n "must_return_result_proposals_only|Architect.*ResultProposal|Architect.*PlanGraph|returns PlanGraph|returns ResultProposal|Executor.*ResultProposal|Fractal DAG|DAG Executor|EvidenceItem.kind|artifact_type|Post V&V|post_vv|jsonschema|JSON Schema|ResultProposal|PlanGraph|GT report|gt_report|Root Final|final_output|DRS writeback" .`
- `rg -n "must_return_result_proposals_only|architect_instructions|Architect" schemas specs docs demo tests hedgehog`
- `rg -n "EvidenceItem|EvidenceItem\.kind|kind|artifact_type" schemas specs docs demo tests hedgehog`
- `rg -n "post_vv|Post V&V|ValidationReport|ResultProposal|jsonschema|Draft7Validator|validate\(" hedgehog demo tests schemas specs docs`
- `rg -n "GT.*FinalOutput|gt.*final|creates FinalOutput|Root.*FinalOutput|Root Final|DRS writeback|writeback|drs_writes|final_output|created_by.*root_orchestrator|result_proposal_only|PlanGraph only|must_return_result_proposals_only|architect_instructions" tests demo hedgehog specs docs schemas`
- `cat` / `sed` reads of the schema, runtime, spec, demo, and focused test files named below.

Path note: the suggested `src` path does not exist in this repository. The active runtime package discovered by the scan is `hedgehog/`.

## 2. Why This Scan Exists

Blind auditor notes from Enterprise Document Killer Demo B identified real engineering debt:

- schema drift
- runtime validation lighter than full JSON Schema contracts
- EvidenceItem.kind / artifact vocabulary mismatch
- Demo B is an applied proof, not a general engine

This scan inventories the debt before patching. It does not apply fixes.

## 3. Canonical Contract Baseline

Canonical baseline for this scan:

- Root remains final authority.
- Orchestrator / route assembly does not create FinalOutput.
- Architect returns PlanGraph only.
- Executor / Fractal DAG returns ResultProposal artifacts.
- Node-level executors return ResultProposal-like artifacts.
- Post V&V validates the ResultProposal boundary before GT.
- GT is advisory only and does not create FinalOutput.
- Root creates FinalOutput.
- DRS writeback happens only after Root Final and remains local/audit unless a later production layer exists.
- ConnectorObservation is not truth.
- EvidenceCandidate is not AcceptedEvidence.
- AcceptedEvidence is not action.
- DRS reuse is not authority.
- Audit hash is not truth.
- Developer manifest is not installed capability.
- NeedleCandidate is not installed Needle.
- No component gets authority from schema text alone.

Primary baseline references observed:

- `specs/human_passport_v0_25.md`: core pipeline states Architect -> PlanGraph -> Executors -> ResultProposals -> Post V&V -> GTValidator -> Root FinalOutput -> DRS writeback.
- `specs/invariants.md`: Architect output contract states Architect returns PlanGraph and time assumptions; Executor contract states Executors return ResultProposal only.
- `specs/schema_package_v0_25_reference.md:27`: Architect must return PlanGraph, not ResultProposal.
- `specs/schema_package_v0_25_reference.md:28`: Executors / DAG runner return ResultProposal-shaped outputs.

## 4. Finding A - Architect / ResultProposal Schema Drift

severity: schema_contract_drift
patch_status: not_patched_in_this_scan
architect_resultproposal_drift_found: true

Locations of `must_return_result_proposals_only`:

- `schemas/attractor_packet.schema.json:221`: active AttractorPacket schema requires `must_return_result_proposals_only`.
- `schemas/attractor_packet.schema.json:230`: active AttractorPacket schema defines `must_return_result_proposals_only` as `const: true`.
- `hedgehog/avf.py:145`: active runtime `build_attractor_packet()` emits `architect_instructions.must_return_result_proposals_only: True`.
- `specs/schema_package_v0_25_reference.md:29`: reference file says this field is obsolete and must not be copied into active schemas.
- `specs/schema_package_v0_25_reference.md:697`: reference schema block still requires `must_return_result_proposals_only`.
- `specs/schema_package_v0_25_reference.md:708`: reference schema block still defines `must_return_result_proposals_only`.

Locations saying or proving Architect returns PlanGraph:

- `specs/schema_package_v0_25_reference.md:27`: Architect must return `PlanGraph`, not `ResultProposal`.
- `specs/human_passport_v0_25.md`: canonical pipeline and Observable Zero Trust section state Architect output as PlanGraph.
- `specs/invariants.md`: Architect output contract states Architect returns PlanGraph and time assumptions.
- `hedgehog/architect.py`: `make_plan_graph()` returns a PlanGraph-shaped dict.
- `hedgehog/llm_architect.py`: validates an LLM Architect artifact as a PlanGraph contract before use.
- `tests/test_architect_runtime.py`: validates `make_plan_graph()` output against `schemas/plan_graph.schema.json`.
- `demo/run_architect_from_bounded_attractor_packet.py`: Architect layer creates valid PlanGraph proposals and does not invoke Executor.

Locations saying or implying Architect returns ResultProposal:

- `schemas/attractor_packet.schema.json` and `hedgehog/avf.py` imply this through the Architect-facing instruction `must_return_result_proposals_only`.
- The reference spec has self-acknowledged drift: it says the field is obsolete, but still includes it in the copied schema block.

Classification:

The runtime behavior is mostly aligned with the canonical architecture because Architect code and tests produce PlanGraph, and Executor code produces ResultProposal. The active AttractorPacket schema and AVF runtime instruction are not aligned with current canonical wording because they still tell Architect to return result proposals only.

Finding A is real.

## 5. Finding B - Runtime Validation vs JSON Schema Contracts

severity: runtime_validation_gap
patch_status: not_patched_in_this_scan
runtime_jsonschema_gap_found: true

Post V&V runtime locations:

- `hedgehog/post_vv.py`: `validate_result_proposal()` checks required ResultProposal fields, forbidden root/user-facing keys, TimeEnvelope required fields, evidence list presence, critical risks, consistency fields, and task semantics such as `needs_user` / blocked status.
- `hedgehog/post_vv.py`: no runtime `jsonschema` import, `Draft202012Validator`, or full nested schema validator invocation was observed.
- `hedgehog/post_vv.py`: `artifact_type` is read from `result_payload` and propagated to the V&V report.

Schema validation observed in tests:

- `tests/test_schema_files_valid.py`: validates every `*.schema.json` file as Draft 2020-12 JSON Schema.
- `tests/test_architect_runtime.py`: validates PlanGraph outputs against `schemas/plan_graph.schema.json`.
- `tests/test_executor_runtime.py`: validates Executor ResultProposal outputs against `schemas/result_proposal.schema.json`.
- `tests/test_post_vv_runtime.py`: validates Post V&V report outputs against `schemas/vv_report.schema.json`.
- `tests/test_gt_validator_runtime.py`: validates GT report outputs against `schemas/gt_report.schema.json`.
- `tests/test_root_orchestrator_runtime.py`: validates Root FinalOutput outputs against `schemas/final_output.schema.json`.

Focused proof validation observed:

- `tests/test_post_vv_from_result_proposal_runner.py`: Post V&V blocks raw Executor text, raw Architect PlanGraph, raw Orchestrator matrix, raw user intent, and real action output before Post V&V; malformed ResultProposal is rejected.
- `tests/test_gt_from_validation_report_runner.py`: GT blocks raw ResultProposal, raw Executor text, raw Architect PlanGraph, raw Orchestrator matrix, raw user intent, and real action output; GT does not create FinalOutput.
- `tests/test_root_final_from_gt_decision_runner.py`: Root Final blocks raw ValidationReport, raw ResultProposal, raw Executor text, raw Architect PlanGraph, raw Orchestrator matrix, raw user intent, and real action output; Root creates the final artifact.
- `tests/test_drs_writeback_from_root_final_runner.py`: DRS writeback receives only Root Final artifacts and stays local audit only.

Current classification:

- PlanGraph, ResultProposal, V&V report, GT report, and FinalOutput have schema validation in focused tests.
- Runtime Post V&V performs deterministic boundary checks, but full nested JSON Schema validation was not observed inside `hedgehog/post_vv.py`.
- DRS writeback validation in `hedgehog/drs.py` checks required record fields, TimeEnvelope presence, sensitive key names, pointer shape, and layer validity. It is not full schema-backed DRS record validation.

Finding B is real.

## 6. Finding C - EvidenceItem.kind / Artifact Vocabulary Mismatch

severity: evidence_vocabulary_alignment_gap
patch_status: not_patched_in_this_scan
evidence_kind_alignment_gap_found: true

Active EvidenceItem.kind enum:

- `schemas/common.schema.json:136`: defines `$defs.EvidenceItem`.
- `schemas/common.schema.json:139`: requires `kind` and `summary`.
- `schemas/common.schema.json:143`: `kind` enum values are:
  - `drs_record`
  - `needle`
  - `schema`
  - `policy`
  - `trace`
  - `simulated_executor`
  - `manual`
- `schemas/result_proposal.schema.json:72`: ResultProposal evidence items reference `common.schema.json#/$defs/EvidenceItem`.

Runtime evidence use observed:

- `hedgehog/executor.py`: Executor ResultProposal evidence uses `kind: simulated_executor`.
- `hedgehog/needle_runtime.py`: Needle runtime evidence uses `kind: audit`.
- `schemas/common.schema.json` does not include `audit` in the active EvidenceItem.kind enum, while current runtime/docs use audit-like artifacts elsewhere.

Artifact kinds that may not fit the active EvidenceItem.kind enum without mapping:

- connector observation
- evidence candidate
- accepted evidence
- validation packet
- audit event
- child boundary snapshot
- fractal DAG executor trace
- ResultProposal
- PlanGraph
- GT report
- Root Final

Current classification:

The active EvidenceItem.kind enum is narrow and ResultProposal-specific. The wider proof stack now talks about observations, candidates, accepted evidence, validation packets, audit events, child snapshots, DAG traces, GT reports, and Root Final artifacts. Some of these should probably remain artifacts rather than evidence kinds, but the mapping is not explicit enough for public review.

Finding C is real.

## 7. Finding D - artifact_type / Contract Vocabulary

severity: artifact_vocabulary_mapping_needed
patch_status: not_patched_in_this_scan
artifact_type_mapping_needed: true

Where `artifact_type` is used:

- `schemas/vv_report.schema.json:28`: V&V report has optional `artifact_type`.
- `hedgehog/executor.py`: result payloads set `artifact_type` values including `generic_simulated_result`, `request_payload`, `field_validation`, `submission_simulation`, `visit_checklist`, `visit_estimate`, `delegation_requirements`, `authorization_validation`, `missing_requirements_research`, and `human_review_questions`.
- `hedgehog/post_vv.py`: reads `result_payload.artifact_type` and propagates it into the V&V report.
- `hedgehog/gt_validator.py`: reads `artifact_type` from V&V report or nested payload metadata.
- `tests/test_executor_runtime.py`: asserts Executor result payload `artifact_type` values.
- `tests/test_post_vv_runtime.py`: asserts V&V report `artifact_type` is present.

Overlap assessment:

- `EvidenceItem.kind` describes the category of evidence supporting a ResultProposal.
- `artifact_type` describes the shape or semantic class of an artifact or result payload.
- They overlap conceptually because both classify objects, but they should not be silently merged.

Current classification:

`artifact_type` should remain separate from `EvidenceItem.kind` unless a later patch explicitly defines a shared vocabulary model. A mapping table is needed before changing either field.

## 8. Finding E - Contract Validation Test Coverage

severity: test_coverage_gap
patch_status: not_patched_in_this_scan
focused_tests_needed: true

Existing tests that prove Architect returns PlanGraph only:

- `tests/test_architect_runtime.py`
- `tests/test_llm_architect_runtime.py`
- `tests/test_architect_from_bounded_attractor_packet_runner.py`

Existing tests that prove Executor / DAG returns ResultProposal only:

- `tests/test_executor_runtime.py`
- `tests/test_dag_executor_from_valid_plan_graph_runner.py`
- `tests/test_fractal_dag_executor_core_runner.py`

Existing tests that prove Post V&V rejects raw Architect PlanGraph:

- `tests/test_post_vv_from_result_proposal_runner.py`

Existing tests that prove Post V&V rejects raw Executor text:

- `tests/test_post_vv_from_result_proposal_runner.py`

Existing tests that prove GT cannot create FinalOutput:

- `tests/test_gt_validator_runtime.py`
- `tests/test_gt_from_validation_report_runner.py`

Existing tests that prove Root creates FinalOutput:

- `tests/test_root_orchestrator_runtime.py`
- `tests/test_root_final_from_gt_decision_runner.py`
- `tests/test_root_dag_drs_audit_runner.py`

Existing tests that prove DRS writeback remains after Root Final / local audit only:

- `tests/test_drs_writeback_from_root_final_runner.py`
- `tests/test_drs_runtime.py`
- `tests/test_root_orchestrator_runtime.py`

Focused gaps to cover later:

- A test that active AttractorPacket architect instructions no longer include obsolete ResultProposal wording after a reviewed patch.
- A test that Architect-facing contract uses PlanGraph-only wording.
- A runtime test that Post V&V validates ResultProposal against the active JSON Schema, including nested `time_envelope` and `EvidenceItem` shape, if that hardening is accepted.
- Tests that malformed nested evidence, cost, risk, trace refs, and TimeEnvelope structures are rejected by runtime validation.
- A vocabulary matrix test for EvidenceItem.kind and artifact_type.
- A test that DRS writeback validation remains local/audit and does not become authority.

## 9. Risk Classification

Finding A: schema_contract_drift
Finding B: runtime_validation_gap
Finding C: evidence_vocabulary_alignment_gap
Finding D: artifact_vocabulary_mapping_needed
Finding E: test_coverage_gap

architectural_risk_now: false
public_review_risk: true
production_claim_blocker: true
patch_required_before_public_auditor_packet: true

Rationale:

The deterministic runtime proofs still show the intended role boundaries: Architect produces PlanGraph, Executor produces ResultProposal, Post V&V precedes GT, GT does not finalize, Root creates FinalOutput, and DRS writeback remains local/audit after Root. The risk is not immediate authority failure in the current proof path. The risk is public contract ambiguity and incomplete runtime schema-backed validation depth.

## 10. Proposed Patch Plan - Not Implemented Yet

Phase 1 - Align Architect-facing schema/docs wording:

- Architect returns PlanGraph only.
- Remove or rename `must_return_result_proposals_only` from Architect-facing contract after review.
- If needed, introduce `must_return_plan_graph_only`.
- Update active AttractorPacket schema and runtime AVF packet construction together.

Phase 2 - Align Executor / DAG contract:

- Executor / Fractal DAG returns ResultProposal only.
- Make this explicit in schema/docs/tests.
- Preserve child boundary snapshot semantics without making child cells Root.

Phase 3 - Runtime JSON Schema Validation Hardening:

- Add or verify JSON Schema validation for nested artifacts.
- Validate ResultProposal against the active schema at the runtime boundary where appropriate.
- Validate PlanGraph against the active schema where appropriate.
- Validate V&V report, GT report, Root Final, and DRS writeback artifacts where appropriate.
- Keep Root authority unchanged.

Phase 4 - Evidence / artifact vocabulary alignment:

- Decide whether to expand EvidenceItem.kind enum or introduce artifact_type/subtype mapping.
- Map connector observations, evidence candidates, validation packets, audit events, child snapshots, DAG traces, ResultProposal, PlanGraph, GT report, and Root Final.
- Do not silently overload evidence kind.

Phase 5 - Focused tests:

- Architect returns PlanGraph only.
- Executor / DAG returns ResultProposal only.
- Post V&V rejects raw PlanGraph, raw text, and malformed nested artifacts.
- GT cannot create FinalOutput.
- Root Final remains Root-only.
- EvidenceItem.kind vocabulary matches runtime artifacts or has an explicit mapping.

## 11. Non-Goals

This scan does not:

- patch schemas
- patch runtime validation
- patch Post V&V
- change EvidenceItem.kind
- change artifact_type
- change proof runners
- change tests
- create production validation
- create a production document/workflow engine
- claim public-auditor readiness

## 12. Preflight Summary

schema_contract_alignment_preflight_v01_status: COMPLETE
read_only_scan: true
patch_applied: false
schemas_modified: false
runtime_modified: false
tests_modified: false
architect_resultproposal_drift_found: true
runtime_jsonschema_gap_found: true
evidence_kind_alignment_gap_found: true
artifact_type_mapping_needed: true
focused_tests_needed: true
production_claim_blocker: true
public_review_risk: true
next_step: review preflight report before any patch
next_patch_layer_requires_user_approval: true
