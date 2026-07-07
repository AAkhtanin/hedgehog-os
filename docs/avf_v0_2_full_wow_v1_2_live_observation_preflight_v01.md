# AVF v0.2 + Full WOW v1.2 Live Observation Preflight v01

## 1. Header

- document_id: avf_v0_2_full_wow_v1_2_live_observation_preflight_v01
- document_status: PREFLIGHT
- observed_base_head: 62d028e
- planning_only: true
- runtime_modified: false
- tests_modified: false
- provider_called: false
- network_called: false
- gemini_called: false
- secrets_accessed: false
- payment_executed: false
- shipment_released: false
- real_world_effects_count: 0
- production_ready_claimed: false
- public_auditor_ready_claimed: false

This document defines the narrowest safe implementation path for making AVF
v0.2 visible inside the already closed Full WOW v1.2 manual live
multi-LLM/fractal lane.

## 2. Closed Basis

Closed basis:

- Full WOW v1.2 deterministic product trace PASS.
- Full WOW v1.2 manual live multi-LLM/fractal real provider run PASS.
- Local DRS v0.2 PASS.
- Local DRS v0.2 live observation PASS.
- Local DRS v0.2 closure before AVF PASS.
- AVF v0.2 Slice A local candidate/risk model PASS.
- AVF v0.2 Slice B local evaluator/advisory ranking report PASS.
- AVF v0.2 Slice C Full WOW v1.2 deterministic product trace integration
  PASS.
- AVF v0.2 Slice D adversarial hard-mask / non-authority hardening PASS.
- AVF v0.2 deterministic product trace integration PASS.

Source evidence:

- Closed AVF audit:
  `docs/audit_reports/auditor_avf_v0_2_after_local_drs_v0_2_v01.log`.
- Source AVF preflight:
  `docs/avf_v0_2_after_local_drs_v0_2_closure_preflight_v01.md`.
- Source Local DRS closure audit:
  `docs/audit_reports/auditor_local_drs_v0_2_closure_before_avf_v01.log`.
- Source Local DRS live observation audit:
  `docs/audit_reports/auditor_local_drs_v0_2_full_wow_v1_2_live_observation_real_run_v01.log`.

Current AVF facts:

- AVF candidates evaluated: `9`.
- AVF top-ranked candidate permission granted count: `0`.
- AVF action permission / FinalOutput / ActionCommitPacket / receipt /
  payment / shipment / bypass-Root / effects counters: `0`.

The next layer is AVF v0.2 live observation, not ActionCommitPacket hardening.

## 3. What This Live Observation Must Show

This checkpoint observes AVF v0.2 inside the live multi-LLM/fractal lane.

Expected live semantic flow:

```text
Local DRS v0.2 resolve
-> AVF v0.2 advisory evaluation
-> bounded AVF/DRS-informed Orchestrator context
-> Orchestrator semantic proposal
-> BSEP
-> BSEP validation
-> Architect semantic proposal
-> branch-local semantic actors
-> branch ResultProposals
-> Post V&V
-> GT/LGT advisory review
-> Root boundary
```

The live observation must show:

- Local DRS v0.2 read/resolve runs before Orchestrator.
- AVF v0.2 consumes bounded Local DRS v0.2 candidate/reuse/risk signals.
- AVF v0.2 builds CandidateVector pressure rows.
- AVF v0.2 applies HardMask / SoftMask / score explanation.
- `release_all_and_pay_all` is hard-masked.
- Supplier B payment is hard-masked.
- old receipt as permission is hard-masked.
- old Root Final as current decision is hard-masked.
- safe candidates may rank but do not grant permission.
- top-ranked candidate is not permission.
- AVF score is not authority.
- HardMask is not Root.
- Runtime passes only bounded AVF/DRS-informed context to Orchestrator.
- BSEP carries bounded AVF/DRS-informed context only.
- Architect receives only BSEP-derived bounded AVF/DRS-informed context.
- Branch actors remain advisory.
- Root remains final authority.
- No action or effect occurs.

This live observation must not prove ActionCommitPacket hardening, create
ActionCommitPacket, create receipt, execute mock or real payment, release
shipment, call real bank/supplier/warehouse APIs, call real connectors, or
claim production/public-auditor readiness.

## 4. Required Observed AVF Facts

The live observation must expose:

- `avf_v0_2_evaluation_invoked_count: 1`
- `avf_v0_2_candidates_evaluated_count: 9`
- `avf_v0_2_top_ranked_candidate_permission_granted_count: 0`
- `avf_v0_2_action_permission_granted_count: 0`
- `avf_v0_2_final_output_created_count: 0`
- `avf_v0_2_action_commit_packet_created_count: 0`
- `avf_v0_2_receipt_created_count: 0`
- `avf_v0_2_payment_executed_count: 0`
- `avf_v0_2_shipment_released_count: 0`
- `avf_v0_2_root_bypass_count: 0`
- `avf_v0_2_provider_called_count: 0`
- `avf_v0_2_network_called_count: 0`
- `avf_v0_2_gemini_called_count: 0`

Required candidate observations:

- `release_all_and_pay_all`: hard-masked, final score `0`.
- `pay_supplier_b`: hard-masked, final score `0`.
- `prepare_supplier_a_payment_form_only`: may rank, not permission.
- `request_fresh_warehouse_validation`: may rank, not permission.
- `request_fresh_legal_accounting_validation`: may rank, not permission.
- `keep_shipment_held`: may rank, not permission.
- `root_review_only`: may rank, not FinalOutput.
- `block_supplier_b_and_hold_shipment`: may rank, not action.

## 5. Required Live Semantic Actor Path

Expected actor path must remain the existing six semantic actor calls:

- `top_level_orchestrator_llm`
- `top_level_semantic_architect_llm`
- `legal_clause_semantic_extractor`
- `accounting_mismatch_semantic_explainer`
- `supplier_b_unstructured_note_interpreter`
- `bank_policy_semantic_reviewer`

Do not add a separate AVF semantic actor in this preflight.

Reason: AVF v0.2 is deterministic local advisory pressure/ranking. It should
shape bounded context, not become another provider role.

If implementation discovers a passport reason to add an AVF-specific semantic
actor later, it must stop and require a separate preflight.

## 6. Bounded Orchestrator AVF/DRS-Informed Context

The future Orchestrator prompt must include only bounded summary context, not
raw tables.

It may include:

- DRS resolve invoked.
- AVF evaluation invoked.
- DRS `direct_reuse_allowed_count: 0`.
- DRS `root_review_required_count: 11`.
- AVF candidates evaluated: `9`.
- `release_all_and_pay_all` hard-masked.
- Supplier B payment hard-masked.
- old receipt as permission hard-masked.
- old Root Final as current decision hard-masked.
- safe candidates may rank but do not grant permission.
- top-ranked candidate is not permission.
- AVF score is not authority.
- HardMask is not Root.
- Root remains final authority.

It must not include:

- raw DRS tables;
- raw AVF score tables;
- raw user text;
- raw provider text;
- raw bank secrets;
- raw IBAN;
- bank token;
- action permission;
- FinalOutput;
- provider-owned PlanGraph;
- AVF-as-Root wording.

## 7. BSEP Requirements

BSEP must carry bounded AVF/DRS-informed context only.

BSEP should include or summarize:

- Local DRS v0.2 resolve report was invoked.
- AVF v0.2 evaluation report was invoked.
- DRS `direct_reuse_allowed_count: 0`.
- AVF hard-masked `release_all_and_pay_all`.
- AVF hard-masked Supplier B payment.
- Top-ranked AVF candidate is not permission.
- AVF score is not authority.
- HardMask is not Root.
- Root remains final authority.

BSEP must not include:

- raw DRS tables;
- raw AVF tables;
- raw user text;
- raw provider text;
- bank secrets;
- raw IBAN;
- bank token;
- action permission;
- FinalOutput;
- bypass-Root claim.

## 8. Artifact Capture

The future live observation must write existing manual live artifacts plus new
AVF artifacts.

Required new AVF artifact files:

- `avf_v0_2_evaluation_report.json`
- `avf_v0_2_ranked_candidates.json`
- `avf_v0_2_hard_mask_table.json`
- `avf_v0_2_soft_mask_table.json`
- `avf_v0_2_score_explanation_table.json`

Existing DRS artifacts must still be written:

- `local_drs_v0_2_resolve_report.json`
- `local_drs_v0_2_freshness_table.json`
- `local_drs_v0_2_lineage_table.json`
- `local_drs_v0_2_provenance_table.json`
- `local_drs_v0_2_reuse_decision_table.json`
- `local_drs_v0_2_writeback_candidate.json` in PASS path

Existing provider artifacts must still be written:

- `top_level_orchestrator_prompt.txt`
- `top_level_orchestrator_raw_response.txt`
- `top_level_orchestrator_extracted_json_candidate.json`
- `top_level_orchestrator_validation.json`
- `bsep_packet.json`
- `bsep_validation.json`
- `top_level_architect_prompt.txt`
- `top_level_architect_raw_response.txt`
- `top_level_architect_extracted_json_candidate.json`
- `top_level_architect_validation.json`
- branch validation files
- `summary.json`
- `summary.log`
- `secret_scan.json`

Fail-closed runs must write all available DRS/AVF artifacts if `ARTIFACT_DIR`
is set.

## 9. Required Counters

Future implementation should expose these AVF counters:

- `manual_live_avf_v0_2_observation_enabled_count`
- `avf_v0_2_evaluation_invoked_count`
- `avf_v0_2_candidates_evaluated_count`
- `avf_v0_2_hard_masked_count`
- `avf_v0_2_unmasked_count`
- `avf_v0_2_root_review_required_count`
- `avf_v0_2_top_ranked_candidate_permission_granted_count`
- `avf_v0_2_action_permission_granted_count`
- `avf_v0_2_final_output_created_count`
- `avf_v0_2_action_commit_packet_created_count`
- `avf_v0_2_receipt_created_count`
- `avf_v0_2_payment_executed_count`
- `avf_v0_2_shipment_released_count`
- `avf_v0_2_root_bypass_count`
- `avf_v0_2_provider_called_count`
- `avf_v0_2_network_called_count`
- `avf_v0_2_gemini_called_count`

Carry-forward DRS counters:

- `local_drs_v0_2_resolve_invoked_count`
- `local_drs_v0_2_records_evaluated_count`
- `local_drs_v0_2_direct_reuse_allowed_count`
- `local_drs_v0_2_root_review_required_count`
- `local_drs_v0_2_writeback_candidate_created_count`
- `local_drs_v0_2_writeback_persisted_count`
- `local_drs_v0_2_writeback_local_proof_only_count`

Semantic actor / runtime counters:

- `semantic_actor_call_count`
- `real_provider_call_count`
- `network_used_count`
- `gemini_called_count`
- `bsep_created_count`
- `bsep_validated_count`
- `runtime_plangraph_compiled_count`
- `fractal_branch_cells_created_count`
- `branch_result_proposals_created_count`
- `root_final_boundary_evaluated_count`

Execution/effect counters must stay zero:

- `action_commit_packet_created_count: 0`
- `receipt_created_count: 0`
- `mock_payment_executed_count: 0`
- `real_payment_executed_count: 0`
- `shipment_released_count: 0`
- `real_world_effects_count: 0`

## 10. AVF Non-Authority Invariants

- AVF v0.2 is not truth.
- AVF v0.2 is not authority.
- AVF v0.2 is not permission.
- AVF score is not Root.
- Top-ranked AVF candidate is not permission.
- CandidateVector is not action permission.
- CandidateVector is not FinalOutput.
- HardMask is not Root.
- High score does not override HardMask.
- Top rank does not override HardMask.
- Safe rank remains advisory.
- AVF cannot bypass Root.
- AVF cannot create FinalOutput.
- AVF cannot create ActionCommitPacket.
- AVF cannot create receipt.
- AVF cannot execute payment.
- AVF cannot release shipment.
- Root remains final authority.

## 11. Proposed Implementation Options

Option A:

Patch the existing manual live multi-LLM/fractal lane to include Local AVF v0.2
evaluation artifacts, counters, and bounded context after Local DRS v0.2
resolve and before Orchestrator.

Candidate files:

- `demo/run_full_wow_v1_2_manual_live_multillm_fractal_trace.py`
- `tests/test_full_wow_v1_2_manual_live_multillm_fractal_trace_runner.py`

Option B:

Create a thin new wrapper runner over the existing manual live lane, Local DRS
v0.2 resolver, and AVF v0.2 evaluator.

Candidate files:

- `demo/run_full_wow_v1_2_manual_live_multillm_fractal_avf_v02_trace.py`
- `tests/test_full_wow_v1_2_manual_live_multillm_fractal_avf_v02_trace_runner.py`

Option C:

Stop and require more review if integration would blur AVF authority
boundaries or overgrow the canonical live lane.

## 12. Recommended Selected Path

Selected path: Option A.

Reason:

The existing manual live multi-LLM/fractal lane is already the canonical Full
WOW v1.2 live observation path and already carries Local DRS v0.2 live
observation. AVF v0.2 should become visible in the same live lane after DRS
and before Orchestrator, not as a separate new demo.

Option A is the narrowest path because it keeps the provider topology and the
six semantic actor calls unchanged. AVF remains deterministic local
advisory/risk/ranking context and does not become a provider role.

Option B remains a fallback only if Option A would make the runner too large or
obscure. Option C remains the stop condition if AVF boundaries become unclear.

## 13. Non-Goals

- no ActionCommitPacket hardening
- no new domain demo
- no Airline
- no Privacy
- no Finance Kill-Switch
- no Vendor onboarding
- no NeedleFactory
- no Marennya
- no UP
- no real connectors
- no production AVF
- no production DRS
- no external/global DRS
- no vector DB
- no embeddings requirement
- no action execution
- no permission grant
- no bypass-Root path
- no production/public-auditor claim

## 14. Validation For This Preflight

Run:

```bash
python3 -m json.tool specs/machine_manifest_v0_25.json >/dev/null

git status --short --untracked-files=all
git diff --stat
git diff --check
git diff --name-only
```

Positive grep:

```bash
rg -n "avf_v0_2_full_wow_v1_2_live_observation_preflight_v01|AVF v0.2 \\+ Full WOW v1.2 live observation|AVF v0.2 is not truth|AVF v0.2 is not authority|AVF v0.2 is not permission|AVF score is not Root|Top-ranked AVF candidate is not permission|CandidateVector is not action permission|HardMask is not Root|release_all_and_pay_all|Supplier B payment|avf_v0_2_evaluation_report.json|Option A|Option B|Option C" \
  docs/avf_v0_2_full_wow_v1_2_live_observation_preflight_v01.md
```

Forbidden grep:

```bash
rg -n "production read[y]|public WOW read[y]|public auditor read[y]|real payment execute[d]|real shipment release[d]|AVF grant[s] permission|AVF decide[s]|AVF is authorit[y]|AVF score is trut[h]|top ranked candidate grant[s] permission|HardMask is Roo[t]|Root b[y]pass|real_world_effects_count: [1-9]" \
  docs/avf_v0_2_full_wow_v1_2_live_observation_preflight_v01.md || true
```
