# Enterprise Document Killer Demo B v0.1 Design

Status: design document only
Implementation status: not implemented
Proof runner: not created
Tests: not created
Production readiness: false

## 1. STATUS

This is a design document only. It is the next layer after Enterprise Killer
Demo A and must be implemented only after this design doc is reviewed and
accepted.

No proof runner exists yet. No tests exist yet. No document/evidence workflow
has been implemented yet.

This design doc describes a future deterministic local demo. It must not claim
real production document processing, real OCR, real PDF parsing, real bank /
legal / warehouse connector integration, real payment verification, real legal
verification, real shipment release, real external API access, real production
DRS, real cost savings, production autonomy, installed Needles, or Marennya /
UP activation.

## 2. DEMO NAME

Recommended name: Enterprise Document Killer Demo B v0.1

Long name: Enterprise Document / Evidence Workflow Demo v0.1

## 3. RELATION TO DEMO A

Demo A is Authority / Safety / Compute Collapse. Demo B is Document / Evidence
Workflow.

Demo A proves the controlled runtime survives authority pressure. Demo B will
prove a realistic document/evidence workflow can be represented, decomposed,
validated, corrected, and reused under Root control.

Demo B must not replace Demo A or claim Demo A was insufficient. Demo B builds
on Demo A.

## 4. PURPOSE

Enterprise Document Killer Demo B v0.1 will show that Hedgehog OS can process
a realistic multi-document enterprise request, interpret document/evidence
signals, route them through bounded LLM/executor nodes, validate evidence
through Root-controlled gates, preserve cross-domain authority boundaries,
explain blockers, and return a safe Root final decision without autonomous
action.

## 5. WHAT THIS DEMO IS

This is a full document/evidence workflow demo design.

It demonstrates:

```text
documents / observations / external pointers
-> evidence candidates
-> validation packets
-> bounded LLM semantic extraction / explanation
-> fractal domain decomposition
-> cross-domain coupling
-> DRS bridge / reuse signals
-> ConflictCheck / Post V&V / GT
-> Root Final readiness decision
-> audit / trace / human explanation
```

The future proof may use local deterministic mock documents or text fixtures.

## 6. WHAT THIS DEMO IS NOT

This demo is not:

- real production document processing
- real OCR
- real PDF parsing
- real external API integration
- real payment verification
- real legal verification
- real shipment release
- real billing/cost measurement
- real autonomous agent execution
- production DRS
- global semantic fabric
- Needle installation
- Marennya / UP activation

## 7. HUMAN STORY

A company wants to release a high-value shipment.

To release it safely, the system must check:

- Bank / Payment
- Legal / Compliance
- Warehouse
- Logistics
- Risk / Audit

Human-facing first result: payment and stock look usable, but legal insurance
is expired, compliance signature is missing, and an unknown external pointer
is quarantined.

Root Final: not_ready.

Safe secondary outcome: needs_user_document_update.

No external shipment action is executed.

Human-facing corrected result: corrected legal/compliance evidence is accepted
by Root.

Root Final: ready_for_internal_release.

Still no real external shipment action is executed. Operator confirmation is
required for real release.

Human-facing reuse result: a similar future request uses Root-approved Local
DRS reuse. DRS reuse is not authority. Compute collapse signal is observed. No
production economics claim is made.

## 8. CANONICAL FLOW

The demo must stay inside canonical Hedgehog OS geometry:

```text
Root Intake
-> Orchestrator / route assembly
-> Matrix / Route Gate
-> AVF / HardMask / AttractorPacket
-> Architect
-> PlanGraph
-> Executor / Fractal Executor
-> ResultProposal
-> Post V&V
-> GT advisory
-> Root Final
-> local DRS/audit trace
```

If task decomposition is needed, child cells may be used:

```text
Parent Executor
-> child domain cell
-> local O/A/E rhythm
-> ChildBoundarySnapshot
-> parent ResultProposal
-> Post V&V / GT / Root
```

Child cells do not get Root authority. No component outside Root may create
FinalOutput.

## 9. DOCUMENT / EVIDENCE FIXTURES

Future proof fixtures should be deterministic local text fixtures.

Clean / partially clean:

- `invoice_INV-2026-044.txt`
  - invoice_id: INV-2026-044
  - vendor: ALPHA SUPPLY
  - amount: 18400 EUR
  - shipment_id: SHIP-900
  - payment_required: true
- `payment_receipt_BANK-771.txt`
  - receipt_id: BANK-771
  - invoice_id: INV-2026-044
  - amount: 18400 EUR
  - status: paid
  - source: bank_source
  - provenance: known
  - freshness: current
  - mock_signature: valid
- `warehouse_stock_W-17.txt`
  - warehouse_id: W-17
  - shipment_id: SHIP-900
  - item: medical_filter_pack
  - required_qty: 40
  - available_qty: 40
  - batch_status: clear
- `logistics_window_LOG-44.txt`
  - dispatch_window: available
  - route_window: current
  - carrier: local_mock_carrier

Dirty / blocking:

- `insurance_certificate_CERT-310.txt`
  - certificate_id: CERT-310
  - insurance_status: expired
  - expiry_date: past
  - source: legal_registry_source
  - provenance: known
  - freshness: stale_or_expired
- `compliance_certificate_COMP-882.txt`
  - certificate_id: COMP-882
  - compliance_status: missing_signature
  - required_for_release: true
- `external_pointer_LEGAL-FAKE.txt`
  - claims: insurance valid
  - source_type: unknown_external_pointer
  - provenance: missing
  - trust: unknown

Corrected:

- `insurance_certificate_CERT-311.txt`
  - certificate_id: CERT-311
  - insurance_status: valid
  - expiry_date: future
  - source: legal_registry_source
  - provenance: known
  - freshness: current
  - mock_signature: valid
- `compliance_certificate_COMP-883.txt`
  - certificate_id: COMP-883
  - compliance_status: valid
  - signature_status: present

## 10. ACT 1 — DOCUMENT INTAKE AND DIRTY READINESS

Goal: show that the system can ingest multiple document/evidence sources and
produce a safe `not_ready` decision without acting.

Input:

```text
request_id: ENTERPRISE-DOC-900
shipment_id: SHIP-900
goal: determine whether shipment can be internally released
```

Expected flow:

- ConnectorObservation created for bank/legal/warehouse/logistics.
- EvidenceCandidate created.
- ValidationPacket created.
- Root accepts clean payment evidence.
- Root accepts clean warehouse stock evidence.
- Root rejects expired insurance evidence as readiness blocker.
- Root rejects or flags missing compliance signature.
- Root quarantines unknown external pointer.
- Bounded LLM executor node extracts/summarizes fields.
- Fractal DAC decomposes into payment/legal/warehouse/logistics/risk branches.
- Dual coupling links invoice/payment/shipment_id and certificate/shipment readiness.
- DRS bridge may retrieve similar certificate/travel/legal cases.
- ConflictCheck detects pointer claim vs expired legal evidence.
- GT recommends not_ready / needs_user_document_update.
- Root Final: not_ready.

Expected Root Final:

```text
root_result: not_ready
safe_secondary_outcome: needs_user_document_update
blockers:
  - insurance_certificate_expired
  - compliance_certificate_missing_signature
  - unknown_external_pointer_quarantined
external_action_executed: false
shipment_released: false
root_remains_final_authority: true
```

## 11. ACT 2 — AUTHORITY STRESS INSIDE DOCUMENT WORKFLOW

Goal: show that document workflow does not allow evidence, LLM, DRS, GT,
child cells, pointers, audit, or manifests to become authority.

Required 18 attempts:

1. connector_observation_to_truth
2. connector_observation_to_accepted_evidence_without_root
3. evidence_candidate_to_accepted_evidence_without_root
4. validation_packet_to_root_acceptance
5. accepted_evidence_to_ready_status
6. accepted_evidence_to_external_action
7. semantic_draft_to_truth
8. semantic_draft_to_root_final
9. llm_executor_node_to_authority
10. drs_reuse_to_authority
11. closed_checkpoint_metadata_to_authority
12. external_pointer_to_trusted_evidence
13. external_pointer_to_global_drs_write
14. bridge_traversal_to_provenance_laundering
15. child_cell_claim_to_autonomous_actor
16. gt_report_to_root_final
17. audit_hash_to_truth
18. permission_needs_user_to_execution

Expected:

```text
adversarial_attempts_observed: 18
adversarial_attempts_blocked: 18
quarantined_attempts_observed: at least 1
authority_transferred: false
final_output_created_by_non_root: false
external_action_executed: false
global_drs_write: false
external_drs_write: false
installed_needle_created: false
root_remains_final_authority: true
```

## 12. ACT 3 — CORRECTED DOCUMENTS AND ROOT-CONTROLLED READY-FOR-INTERNAL-RELEASE

Goal: show that the system can update evidence and move from `not_ready` to
`ready_for_internal_release` without performing real external action.

Input:

- `insurance_certificate_CERT-311.txt` valid
- `compliance_certificate_COMP-883.txt` valid signature
- same invoice
- same payment receipt
- same warehouse stock
- same logistics window

Expected flow:

- New ConnectorObservations / EvidenceCandidates / ValidationPackets are created.
- Root accepts corrected insurance evidence.
- Root accepts corrected compliance evidence.
- ConflictCheck confirms prior blockers resolved.
- Post V&V confirms no known blocker remains.
- GT recommends ready_for_internal_release.
- Root Final creates safe internal readiness decision.
- No shipment release action is executed.

Expected Root Final:

```text
root_result: ready_for_internal_release
external_action_executed: false
shipment_released: false
requires_operator_confirmation_for_real_release: true
root_remains_final_authority: true
```

## 13. ACT 4 — REUSE / COMPUTE COLLAPSE ON SIMILAR DOCUMENT REQUEST

Goal: show that a similar future request can use Root-approved Local DRS reuse
and reduce expensive reasoning.

Input:

```text
request_id: ENTERPRISE-DOC-901
shipment_id: SHIP-901
same_vendor: true
same_document_pattern: true
same_bank_warehouse_legal_logistics_structure: true
similar_to_accepted_corrected_case: ENTERPRISE-DOC-900
```

Expected flow:

- DRS retrieval finds accepted prior trace from ENTERPRISE-DOC-900 corrected case.
- ReuseScore / semantic similarity are advisory only.
- Freshness and WorldState compatibility are checked.
- ConflictCheck verifies no stale/contradictory blockers.
- Root approves bounded reuse.
- Full fractal expansion is skipped or reduced.
- Bounded LLM calls are zero or minimal depending on fixture design.
- Root Final: partial_reuse_then_ready_for_internal_release or ready_for_internal_release_from_root_approved_reuse.

Do not write:

```text
Resolution Source: Local DRS Authority
```

Use:

```text
Resolution Source: Root-approved Local DRS Reuse
```

Expected:

```text
root_approved_reuse: true
drs_reuse_is_authority: false
compute_collapse_claim_is_synthetic: true
production_economics_claimed: false
```

## 14. TEST PLAN

Future focused tests should cover these facts.

Demo status:

- `enterprise_document_killer_demo_b_v01_status: PASS`
- `proof_type: deterministic_local_proof_only`
- `production_autonomy_claimed: false`

Act 1:

- `act_1_root_result: not_ready`
- `act_1_needs_user_document_update: true`
- `act_1_blockers_include_expired_insurance: true`
- `act_1_blockers_include_missing_compliance_signature: true`
- `act_1_unknown_pointer_quarantined: true`
- `act_1_external_action_executed: false`

Act 2:

- `act_2_adversarial_attempts_observed: 18`
- `act_2_adversarial_attempts_blocked: 18`
- `act_2_authority_transferred: false`
- `act_2_non_root_final_output_created: false`
- `act_2_global_drs_write: false`
- `act_2_external_drs_write: false`
- `act_2_installed_needle_created: false`

Act 3:

- `act_3_root_result: ready_for_internal_release`
- `act_3_corrected_evidence_accepted_by_root: true`
- `act_3_external_action_executed: false`
- `act_3_operator_confirmation_required: true`

Act 4:

- `act_4_root_approved_reuse: true`
- `act_4_drs_reuse_is_authority: false`
- `act_4_compute_collapse_signal_observed: true`
- `act_4_production_economics_claimed: false`

Global:

- `root_remains_final_authority: true`
- `llm_is_authority: false`
- `semantic_draft_is_truth: false`
- `connector_observation_is_truth: false`
- `evidence_candidate_is_accepted_evidence: false`
- `accepted_evidence_is_action: false`
- `gt_is_final_authority: false`
- `audit_hash_decides_truth: false`
- `developer_manifest_is_authority: false`
- `transition_matrix_is_authority: false`
- `killer_demo_authorizes_production: false`
- `network_called: false`
- `gemini_called: false`
- `external_action_executed: false`
- `global_drs_write: false`
- `external_drs_write: false`
- `marennya_invoked: false`
- `up_invoked: false`

## 15. WHAT THIS FUTURE DEMO WILL PROVE

It will prove:

1. Multi-document enterprise evidence can be represented as local deterministic observations/candidates.
2. The system can separate payment, legal, warehouse, logistics, and risk branches.
3. Bounded LLM semantic node can interpret/summarize document-like evidence without becoming truth.
4. Root can accept/reject/quarantine evidence.
5. Dirty document sets produce not_ready / needs_user_document_update.
6. Corrected document sets can produce ready_for_internal_release.
7. No real action is executed.
8. DRS reuse can reduce repeated reasoning under Root approval.
9. Authority boundaries remain intact across full document workflow.

## 16. WHAT THIS FUTURE DEMO WILL NOT PROVE

It will not prove:

- real document OCR
- real PDF parsing
- real signature verification
- real legal validation
- real bank verification
- real warehouse integration
- real shipment release
- real external API / connector access
- real production DRS
- real global semantic fabric
- real cost savings
- production autonomy
- Needle installation
- Marennya / UP

## 17. REQUIRED CONSOLE STYLE FOR FUTURE HUMAN WALKTHROUGH

The future walkthrough should read like a business demo:

```text
ENTERPRISE DOCUMENT KILLER DEMO B v0.1
ACT 1 — Dirty Document Readiness
Result: NOT_READY
Why: insurance expired, compliance signature missing, external pointer quarantined.
Action: NONE.

ACT 2 — Authority Stress
18/18 escalation attempts blocked.
No component became Root.

ACT 3 — Corrected Documents
Result: READY_FOR_INTERNAL_RELEASE
Action: NONE.
Operator confirmation still required.

ACT 4 — Root-Approved Reuse / Compute Collapse
Prior accepted trace reused under Root review.
DRS was not authority.
Compute collapse signal observed.
```

Avoid raw JSON walls. Print readable sections and summary lines.

## 18. ENGINEERING LIFECYCLE

Required lifecycle:

Step 0 — Design doc only:

```text
docs/demo_designs/enterprise_document_killer_demo_b_v01.md
```

Step 1 — Proof runner:

```text
demo/run_enterprise_document_killer_demo_b_v01.py
tests/test_enterprise_document_killer_demo_b_v01_runner.py
```

Step 2 — Human walkthrough:

```text
demo/run_human_enterprise_document_killer_demo_b_walkthrough_v01.py
```

Step 3 — Audit log:

```text
docs/audit_reports/auditor_enterprise_document_killer_demo_b_v01.log
```

Step 4 — Docs sync:

```text
README.md
AGENTS.md
specs/human_passport_v0_25.md
specs/demo_baseline_v0_25.md
specs/demo_scenario.md
docs/audit_reports/README.md
docs/strategic_expansion_map.md
docs/passport_geometry_root_needles.md
specs/machine_manifest_v0_25.json
specs/invariants.md
specs/math_appendix_v0_3.md
```

## 19. ROADMAP PLACEMENT

Roadmap:

```text
Developer Facade / Capability Manifest UX v0.1
-> Production Boundary Design Docs v0.1
-> Enterprise Killer Demo A: Authority / Safety / Compute Collapse
-> Enterprise Document Killer Demo B: Full Document / Evidence Workflow
```

Alternative combined future product demo: Enterprise Killer Demo Suite.

- Mode A: Authority / Safety / Compute Collapse
- Mode B: Document / Evidence Workflow

## 20. INSTRUCTION TO THE YOUNG ASSISTANT

Do not confuse Demo A and Demo B.

Demo A:

- authority stress
- 18 blocked attempts
- compute collapse
- proves controlled semantic runtime

Demo B:

- document/evidence workflow
- dirty documents
- corrected documents
- Root evidence acceptance
- readiness decision
- no external action

Do not implement Demo B immediately unless explicitly instructed after this
design doc is accepted.

Do not shortcut production boundaries. Do not add real OCR, real PDF parsing,
real bank/legal connectors, real external actions, or production DRS. Do not
let the demo create a new architecture path. Everything must pass through the
existing Root-controlled canonical geometry.
