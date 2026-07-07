# Local DRS v0.2 + Full WOW v1.2 Live Observation Preflight v01

## 1. Header

- document_id: local_drs_v0_2_full_wow_v1_2_live_observation_preflight_v01
- document_status: PREFLIGHT
- observed_base_head: 3885d5c
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

This document defines the narrowest safe implementation path for a Local DRS
v0.2 + Full WOW v1.2 live observation checkpoint.

## 2. Closed Basis

Closed Full WOW v1.2 baseline:

- Full WOW v1.2 deterministic product trace PASS.
- Full WOW v1.2 manual live multi-LLM/fractal real provider run PASS.
- Full WOW v1.2 human story PASS.
- Full WOW v1.2 artifact-backed story renderer PASS.
- Local DRS v0.2 resolve is visible in the deterministic product trace PASS.

Closed Local DRS v0.2 baseline:

- Preflight:
  `docs/local_drs_v0_2_after_full_wow_v1_2_preflight_v01.md`.
- Audit:
  `docs/audit_reports/auditor_drs_v0_2_local_lineage_reuse_v01.log`.
- Slice A record/time/lineage model: PASS.
- Slice B local resolver/reuse decision report: PASS.
- Slice C Full WOW v1.2 deterministic product trace integration: PASS.
- Slice D adversarial/stale/quarantine/deadend hardening: PASS.
- Audit/docs checkpoint: PASS.

Full WOW v1.2 remains the baseline regression scenario. The next step is a
live observation of Local DRS v0.2 inside the already closed v1.2 live
multi-LLM/fractal lane. It is not AVF v0.2.

## 3. What This Live Observation Must Show

This checkpoint must observe DRS v0.2 inside the live multi-LLM/fractal lane.

Required observation shape:

- DRS read/resolve happens before or during top-level semantic route
  construction.
- Real Orchestrator receives DRS-informed bounded context, not raw DRS
  authority.
- BSEP is created after Orchestrator validation.
- BSEP is validated before Architect.
- BSEP carries only bounded DRS-informed context.
- Architect receives BSEP-derived DRS-informed context.
- Branch actors remain advisory.
- Runtime owns PlanGraph/local artifacts.
- Branch ResultProposals remain proposals only.
- Post V&V and GT/LGT do not finalize.
- Root remains final authority.
- DRS writeback after Root is local proof/audit only.

The live observation must show what DRS v0.2 reads, what prior traces it finds,
how it classifies freshness/staleness/reuse, which records become
`context_only`, `warning_only`, `rerun_required`, or `blocked`, and that
`direct_reuse_allowed` remains `0` by default.

## 4. Required Observed DRS Facts

The live observation must expose these DRS facts:

- `drs_v0_2_records_evaluated_count: 11`
- `drs_v0_2_direct_reuse_allowed_count: 0`
- `drs_v0_2_root_review_required_count: 11`
- `supplier_a_prior_scoped_trace` classification
- `supplier_b_blocker_trace` classification
- `old_receipt_trace` classification
- `old_root_final_trace` classification
- `changed_warehouse_fact` classification
- `stale_legal_accounting_evidence` classification
- `quarantined_record` classification
- `deadend_record` classification
- `wrong_domain_near_match` classification
- `permission_trace_completed_action_attempt` classification

The human-readable trace must make these meanings visible:

- Supplier A prior trace may inform bounded context.
- Supplier B blocker trace may warn or block.
- old receipt remains context, not current permission.
- old Root Final is not silently reused.
- changed warehouse facts require rerun validation.
- stale legal/accounting evidence receives freshness downgrade.
- quarantined records block direct reuse.
- deadend proximity blocks or downgrades reuse.
- wrong-domain near match is not direct reuse.
- permission trace cannot become completed action.

## 5. Required Live Semantic Actor Path

Expected live semantic actor path:

- `top_level_orchestrator_llm`
- BSEP
- `top_level_semantic_architect_llm`
- `legal_clause_semantic_extractor`
- `accounting_mismatch_semantic_explainer`
- `supplier_b_unstructured_note_interpreter`
- `bank_policy_semantic_reviewer`

The live run should continue to use six semantic actor calls unless
implementation discovers a passport reason to add a DRS-specific semantic
actor. If a DRS-specific semantic actor is proposed, it must be preflighted
explicitly and remain advisory only.

## 6. Required Artifact Capture

The live observation must write an artifact directory when enabled.

Required files:

- `summary.json`
- `summary.log`
- `secret_scan.json`
- `local_drs_v0_2_resolve_report.json`
- `local_drs_v0_2_freshness_table.json`
- `local_drs_v0_2_lineage_table.json`
- `local_drs_v0_2_provenance_table.json`
- `local_drs_v0_2_reuse_decision_table.json`
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

Fail-closed runs must also write available artifacts if `ARTIFACT_DIR` is set.
Later-stage files may be absent or safe `not_run` placeholders when the failure
occurs before that stage.

Raw provider responses are artifact evidence, not console story text. They
must not be printed by default.

## 7. Required Counters

Future implementation should expose:

- `manual_live_drs_v0_2_observation_enabled_count`
- `local_drs_v0_2_resolve_invoked_count`
- `local_drs_v0_2_records_evaluated_count`
- `local_drs_v0_2_direct_reuse_allowed_count`
- `local_drs_v0_2_root_review_required_count`
- `local_drs_v0_2_context_only_count`
- `local_drs_v0_2_warning_only_count`
- `local_drs_v0_2_rerun_required_count`
- `local_drs_v0_2_blocked_count`
- `local_drs_v0_2_writeback_candidate_created_count`
- `local_drs_v0_2_writeback_persisted_count`
- `local_drs_v0_2_writeback_local_proof_only_count`
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
- `action_commit_packet_created_count: 0`
- `receipt_created_count: 0`
- `mock_payment_executed_count: 0`
- `real_payment_executed_count: 0`
- `shipment_released_count: 0`
- `real_world_effects_count: 0`

The live observation must not create an ActionCommitPacket, receipt, payment,
shipment release, connector effect, or real-world effect.

## 8. DRS Non-Authority Invariants

- DRS v0.2 is not truth.
- DRS v0.2 is not authority.
- DRS v0.2 is not permission.
- DRS hit is context only.
- Reuse candidate is not direct reuse.
- old receipt is not current permission.
- old Root Final is not silently reused.
- Permission trace cannot become completed action.
- ReuseScore is not Root.
- Semantic similarity is not authority.
- Direct reuse default false.
- DRS writeback after Root is local proof/audit only.
- Root remains final authority.

Additional carry-forward boundaries:

- Accepted evidence ancestry is not future action permission.
- Changed facts require rerun validation.
- Quarantine proximity blocks direct reuse.
- Deadend proximity blocks or downgrades reuse.
- Conflicting provenance blocks reuse.
- Duplicate poisoning does not create authority.
- Wrong-domain near match is not direct reuse.

## 9. Proposed Implementation Options

Option A:

Patch the existing manual live multi-LLM/fractal lane to include Local DRS v0.2
resolve artifacts and counters.

Candidate files:

- `demo/run_full_wow_v1_2_manual_live_multillm_fractal_trace.py`
- `tests/test_full_wow_v1_2_manual_live_multillm_fractal_trace_runner.py`

Option B:

Create a thin new wrapper runner over the existing manual live lane and Local
DRS v0.2 resolver.

Candidate files:

- `demo/run_full_wow_v1_2_manual_live_multillm_fractal_drs_v02_trace.py`
- `tests/test_full_wow_v1_2_manual_live_multillm_fractal_drs_v02_trace_runner.py`

Option C:

Stop and require more review if integration would blur DRS authority
boundaries.

## 10. Recommended Selected Path

Selected path: Option A.

Reason:

The existing manual live multi-LLM/fractal lane is already the canonical Full
WOW v1.2 live observation path. Source inspection shows it already has public
collect/render/run APIs, artifact capture, fail-closed artifact writing,
semantic actor counters, BSEP creation/validation, branch actor validation,
and Root boundary reporting. Adding a deterministic Local DRS v0.2 resolve
report before top-level route construction is therefore the narrowest path.

Option A keeps the observation inside the real v1.2 lane instead of creating a
separate new demo. It should add local deterministic DRS artifacts and counters
while preserving the existing provider topology: Orchestrator -> BSEP ->
Architect -> branch actors -> ResultProposals -> Post V&V -> GT/LGT -> Root.

Option B remains a fallback if implementation discovers that the existing
runner cannot accept DRS artifacts without becoming unclear. Option C remains a
stop condition if DRS authority boundaries would be blurred.

## 11. Non-Goals

- no AVF v0.2 implementation
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
- no production DRS
- no external/global DRS
- no vector DB
- no embeddings requirement
- no production/public-auditor claim

This live observation must not execute action, create a new ActionCommitPacket,
create a new receipt, execute mock or real payment, release shipment, or call
real bank/supplier/warehouse APIs.

## 12. Validation for This Preflight

Commands run for this docs-only preflight:

```bash
python3 -m json.tool specs/machine_manifest_v0_25.json >/dev/null
git status --short --untracked-files=all
git diff --stat
git diff --check
git diff --name-only
```

Positive grep target:

```bash
rg -n "local_drs_v0_2_full_wow_v1_2_live_observation_preflight_v01|Local DRS v0.2 \\+ Full WOW v1.2 live observation|DRS v0.2 is not truth|DRS v0.2 is not authority|DRS v0.2 is not permission|DRS hit is context only|old receipt|old Root Final|permission trace cannot become completed action|ReuseScore is not Root|Semantic similarity is not authority|local_drs_v0_2_resolve_report.json|Option A|Option B|Option C" \
  docs/local_drs_v0_2_full_wow_v1_2_live_observation_preflight_v01.md
```

Forbidden static scan:

- Run the operator-provided forbidden grep against this file.
- Expected result: no matches.
