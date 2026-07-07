# Audit Reports

This folder stores milestone audit logs for Hedgehog OS.

These reports are historical development artifacts, not runtime inputs.
They document proof checkpoints, test runs, auditor-facing traces, and architectural validation logs.

Current reports:

- `auditor_local_drs_v0_2_closure_before_avf_v01.log`
  - Audit status: PASS.
  - Audits Local DRS v0.2 closure/boundary hardening before AVF v0.2.
  - Observed checkpoint base: `9749616`.
  - Source live observation audit:
    `docs/audit_reports/auditor_local_drs_v0_2_full_wow_v1_2_live_observation_real_run_v01.log`.
  - Confirms deadend audit wording is aligned: `deadend_record` is blocked.
  - Confirms missing TimeEnvelope, missing TemporalQuery, and invalid TTL are
    rejected.
  - Confirms BSEP carries bounded DRS context only, without raw DRS tables or
    DRS authority.
  - Confirms DRS writeback candidate cannot create action permission, cannot
    create FinalOutput, cannot persist a production/global record, and is
    rejected before Root.
  - No AVF v0.2 implementation, no provider/network/Gemini calls, and no
    action/effect counters.
  - Non-claims: not production and not public auditor final package.

- `auditor_drs_v0_2_local_lineage_reuse_v01.log`
  - Audit status: PASS.
  - Audits Local DRS v0.2 lineage/freshness/provenance/reuse/trace after
    Full WOW v1.2.
  - Observed checkpoint base: `246715a`.
  - Covers Slice A record/time/lineage model, Slice B local resolver/reuse
    decision report, Slice C Full WOW v1.2 deterministic product trace
    integration, and Slice D adversarial/stale/quarantine/deadend hardening.
  - Confirms Full WOW v1.2 remains the baseline regression scenario.
  - Confirms DRS remembers / links / warns, while Root decides.
  - Confirms direct reuse remains default false and Root review is required by
    default.
  - Confirms `drs_v0_2_regression_records_count: 11`,
    default WOW trace `direct_reuse_allowed_count: 0`, and default WOW trace
    `root_review_required_count: 11`.
  - Confirms old receipt is not current permission, old Root Final is not
    silently reused, changed facts require rerun validation, quarantine
    proximity blocks direct reuse, deadend proximity blocks or downgrades
    reuse, conflicting provenance blocks reuse, duplicate poisoning does not
    create authority, wrong-domain near match is not direct reuse, permission
    trace cannot become completed action, ReuseScore is not Root, and semantic
    similarity is not authority.
  - No AVF v0.2 implementation, no provider/network/Gemini calls, and no
    action/effect counters.
  - Non-claims: not production and not public auditor final package.

- `auditor_human_full_wow_v1_2_live_fractal_story_renderer_v01.log`
  - Audit status: PASS.
  - Audits Full WOW v1.2 live fractal artifact-backed human story renderer.
  - Renderer commit: `29560c7`; renderer audit commit: `e42116b`.
  - Reads artifact files only and renders a reusable human story over completed
    v1.2 manual live multi-LLM/fractal artifact directories.
  - Default renderer state is `SKIPPED_CLOSED` when no artifact directory is
    provided.
  - Canonical real artifact directory renders PASS.
  - Calls no provider/network/Gemini lane.
  - Emits no raw provider response by default.
  - Requires secret scan and required validation artifacts.
  - Fails closed on missing summary, invalid validation evidence, failed secret
    scan, or nonzero effect counters.
  - Creates no ActionCommitPacket, creates no receipt, executes no mock
    payment, executes no real payment, releases no shipment, and creates no
    real-world effects.
  - Non-claims: not production and not public auditor final package.

- `auditor_human_full_wow_v1_1_final_walkthrough_v01.log`
  - Audit status: PASS.
  - Audits Full WOW v1.1 final human-facing walkthrough.
  - Audit commit: `b6c5cb0`; human walkthrough runner commit: `2699bb1`; final rollup docs checkpoint commit: `b074ea8`.
  - Walkthrough type: `human_product_facing_closed_evidence_walkthrough`.
  - Observes the final integrated rollup only.
  - Transition cards created: `15`.
  - Product/business story visibility is closed for warehouse evidence, Supplier A, Supplier B blocker, legal/accounting review, BSEP membrane, Root / human / action boundary, and MockBankSandbox receipt boundary.
  - Real Gemini lane is observed, not rerun.
  - No Gemini/provider/network rerun, no secret access, no ActionCommitPacket creation, no receipt creation, no mock payment execution, no real payment execution, no shipment release, and no connector/API effects.
  - Counters preserve `real_world_effects_count: 0`.
  - v1.2 is not implemented.
  - Non-claims: not production and not public auditor final package.

- `auditor_full_wow_v1_1_final_integrated_rollup_v01.log`
  - Audit status: PASS.
  - Audits Full WOW v1.1 final integrated rollup runner.
  - Audit commit: `a958204`; rollup runner commit: `f22d452`; preflight commit: `2993b46`.
  - Rollup type: `deterministic_closed_evidence_observer`.
  - Observes closed evidence only: Supplier WOW deterministic state machine, human walkthrough, Full Semantic E2E spine, BSEP topology repair, and the real Gemini semantic lane audit.
  - Real Gemini lane PASS is observed, not rerun.
  - BSEP-before-Architect sequence and Semantic Architect / runtime-owned PlanGraph boundary are preserved.
  - Final rollup calls no Gemini/provider/network lane and accesses no secrets.
  - Final rollup creates no ActionCommitPacket, creates no receipt, executes no mock payment, executes no real payment, releases no shipment, and calls no bank/supplier/warehouse API.
  - Counters preserve `real_world_effects_count: 0`.
  - Non-claims: not production and not public auditor final package.

- `auditor_full_wow_v1_1_manual_live_gemini_lane_real_run_v01.log`
  - Audit status: PASS.
  - Audits Full WOW v1.1 manual live Gemini lane real provider run.
  - Run id: `full_wow_v1_1_manual_live_gemini_real_20260705_232010`; runtime/audit base commit: `121d22c`; audit commit: `8318be9`.
  - Model: `gemini-2.5-flash`; contract mode: `semantic_reasoning_adapter`; schema mode: `json_mime_only`.
  - Real Gemini Orchestrator was called once and real Gemini Architect was called once.
  - `live_model_call_count: 2`, `gemini_called_count: 2`, and `network_used_count: 2`.
  - Orchestrator validation accepted, runtime canonicalization was used, BSEP was built after Orchestrator validation, and BSEP was validated before Architect.
  - Architect received BSEP-derived bounded context after the 30-second pre-delay, and Architect validation accepted.
  - Provider output is not truth, authority, action permission, or FinalOutput.
  - Gemini creates no ActionCommitPacket, no receipt, no mock payment, no real payment, and no shipment release.
  - Supplier B remains blocked; shipment release remains held; receipt remains evidence only.
  - Counters preserve `real_world_effects_count: 0`.
  - Secret scan passed: no API key, raw bank secret, raw IBAN, or sandbox token was logged.
  - Non-claims: not production and not public auditor final package.

- `auditor_full_wow_v1_1_manual_live_gemini_bsep_topology_repair_v01.log`
  - Audit status: PASS.
  - Audits Full WOW v1.1 manual live Gemini lane BSEP topology repair.
  - Runtime repair commit: `920e5b3`; preflight commit: `b58226a`; previous live evidence coherence commit: `f119d7c`.
  - Existing Full E2E runner remains the spine; no new bridge runner was created.
  - Manual live Gemini lane is env-gated, and default deterministic mode remains no Gemini/network/provider.
  - This is monkeypatched/no-network topology proof, not final real Gemini lane closure.
  - BSEP is built after Orchestrator validation and semantic canonicalization.
  - BSEP is validated before Architect provider call.
  - Architect receives BSEP-derived bounded context.
  - Invalid BSEP blocks Architect provider call.
  - The BSEP builder no longer accepts Architect semantics.
  - Raw Orchestrator/provider/user/secret text is not passed to Architect.
  - Manual lane creates no ActionCommitPacket, no receipt, no mock payment, no real payment, and no shipment release.
  - Root remains final authority.
  - Counters preserve `real_world_effects_count: 0`.
  - Non-claims: not production and not public auditor final package.

- `auditor_full_semantic_e2e_live_evidence_wow_v1_1_coherence_v01.log`
  - Audit status: PASS.
  - Audits Full Semantic E2E live evidence + Supplier Payment WOW v1.1 coherence.
  - Runtime coherence commit: `b4a3f31`; preflight commit: `4adebf4`; previous alignment audit commit: `82b896d`.
  - Existing Full E2E runner remains the spine; no new bridge runner was created.
  - Explicit live/captured evidence mode includes `supplier_payment_wow_v1_1_summary`.
  - `supplier_payment_wow_v1_1_summary` is PASS in live/captured mode.
  - SemanticEvidenceClaim remains candidate-only.
  - Provider output is not truth, authority, action permission, or FinalOutput.
  - Closed ActionCommitPacket and closed receipt are observed only.
  - Live evidence creates no ActionCommitPacket, no receipt, and no mock payment.
  - Supplier B remains blocked; shipment release remains held; receipt is evidence only.
  - Root alone creates FinalOutput and Root remains final authority.
  - Counters preserve no real payment, no real shipment release, no real bank/supplier/warehouse API effects, and `real_world_effects_count: 0`.
  - Non-claims: not production and not public auditor final package.

- `auditor_full_semantic_e2e_wow_v1_1_alignment_v01.log`
  - Audit status: PASS.
  - Audits Full Semantic E2E v0.1 alignment to Supplier Payment / Shipment Release Review WOW v1.1.
  - Runtime alignment commit: `160f6c5`; preflight commit: `b4ac7fa`; WOW audit commit: `2aa3f13`.
  - Existing Full Semantic E2E runner was patched, not replaced; no new bridge runner was created.
  - Full Semantic E2E invokes the closed WOW v1.1 summary runner as `supplier_payment_wow_v1_1_summary`.
  - WOW v1.1 summary is observed as bounded context/evidence.
  - Closed mock ActionCommitPacket and closed receipt are observed only.
  - Full Semantic E2E creates no new ActionCommitPacket, no new receipt, and no new mock payment.
  - Supplier B remains blocked; shipment release remains held; receipt is evidence only.
  - SemanticEvidenceClaim remains candidate-only.
  - Root alone creates FinalOutput and Root remains final authority.
  - Counters preserve no real payment, no real shipment release, no real bank/supplier/warehouse API effects, and `real_world_effects_count: 0`.
  - Non-claims: not production and not public auditor final package.

- `auditor_supplier_payment_shipment_release_review_wow_v1_1.log`
  - Audit status: PASS.
  - Audits the deterministic sandbox business WOW through Slice E:
    Supplier Payment / Shipment Release Review WOW v1.1.
  - Commit chain: `78fb37d` -> `06f4c55` -> `84d5c6d` -> `06744b2` -> `9ac174b` -> `f7ca348`.
  - Machine runner: `demo/run_supplier_payment_shipment_release_review_wow_v1_1.py`.
  - Human walkthrough: `demo/run_human_supplier_payment_shipment_release_review_wow_v1_1_walkthrough.py`.
  - Focused regression and core contract suite: 275 passed.
  - Deterministic lane PASS; optional live Gemini lane remains manual and was not enabled.
  - Supplier A scoped mock payment only; Supplier B remains blocked; shipment release remains held; receipt is evidence only.
  - Counters preserve no real payment, no real shipment release, no real bank/supplier/warehouse API effects, and `real_world_effects_count: 0`.
  - Root remains final authority.
  - Non-claims: not production and not public auditor final package.

- `auditor_bounded_semantic_evidence_real_gemini_slice_d_004_v01.log`
  - Audit status: PASS.
  - Run id: `manual-bounded-semantic-evidence-real-gemini-slice-d-004`; base_head: `6a2950a`.
  - Real Gemini dual role: Orchestrator called once and Architect called once.
  - Contract mode: `semantic_reasoning_adapter`; schema mode: `json_mime_only`; BSEP gate enabled.
  - BoundedSemanticEvidencePacket accepted, OrchestratorRouteContextPacket accepted, ArchitectPlanContextPacket accepted, structured_orchestrator_rationale accepted, and structured_architect_rationale accepted.
  - Root decision: `needs_more_evidence`; validation_errors: [].
  - Counters: `live_model_call_count: 2`, `network_used_count: 2`, `gemini_called_count: 2`, `bounded_semantic_evidence_packet_created_count: 1`, and `bounded_semantic_evidence_packet_validated_count: 1`.
  - Action counters stayed zero: action_permission_created_count: 0, action_commit_packet_created_count: 0, connector_called_count: 0, real_world_effects_count: 0.
  - Non-claims: not production autonomy, no real connector, no real-world action, no ActionCommitPacket from Gemini, and no FinalOutput from Gemini.
  - Later status: Supplier Payment / Shipment Release Review WOW v1.1 deterministic sandbox business WOW is now PASS.

- `auditor_live_unknown_request_real_gemini_007_v01.log`
  - Audit status: PASS.
  - First successful real live unknown-request run through real Gemini Orchestrator and real Gemini Architect.
  - Run id: `manual-live-unknown-request-real-gemini-007`; run base head: `fa8877d`; audit commit/head context: `d2a0968`.
  - Model: `gemini-2.5-flash`; contract mode: `semantic_reasoning_adapter`; schema mode: `json_mime_only`.
  - Current hedgehog core baseline is `hedgehog.context_packets`, `hedgehog.structured_rationale`, `hedgehog.semantic_reasoning_adapter`, `hedgehog.action_commit_packet`, `hedgehog.mock_connector_sandbox`, and `hedgehog.fractal_fulfillment`.
  - `hedgehog.context_packets` contains bounded ContextPacket contracts; `hedgehog.structured_rationale` contains canonical structured rationale contracts/builders/validators; `hedgehog.semantic_reasoning_adapter` contains stable semantic reasoning provider contracts, reasoning normalization/validation, semantic-to-canonical rationale conversion, safe local advisory PlanGraph node builders, provider claim boolean preservation, and no Gemini/provider/network/runtime imports; `hedgehog.action_commit_packet` contains the Root-created/mock-only ActionCommitPacket contract; `hedgehog.mock_connector_sandbox` contains fake-adapter/local-only sandbox contracts; `hedgehog.fractal_fulfillment` contains child branch / fulfillment topology contracts.
  - Rich Context / Structured Rationale core checkpoint files remain `hedgehog.context_packets`, `tests/test_context_packets_core.py`, `hedgehog.structured_rationale`, and `tests/test_structured_rationale_core.py`.
  - Core Extraction Action + Mock + Fractal remains closed under `auditor_core_extraction_action_mock_fractal_v01`: `c62ab84`, `be4f40d`, `e26c05a`, `4723830`; regression suite 272 passed, 2 warnings; deterministic extracted-core smoke PASS; dual Gemini extracted-core smoke PASS.
  - Integration separation: `demo/run_full_semantic_e2e_v01.py` remains integration harness / integration spine; `demo/run_live_unknown_request_dual_rich_context_v01.py` is the current live unknown-request provider spine; these runners are not `hedgehog` core modules.
  - `semantic_reasoning_adapter` status is `approved_live_provider_architecture`, `core_extracted`, `runner_delegated`, and `slice_c_audited`; the live unknown-request runner delegates semantic adapter mechanics to `hedgehog.semantic_reasoning_adapter`.
  - The live runner still owns Gemini/provider/env/prompt/timeout/pre-delay/orchestration behavior, 007 integration policy, and prompt policy; core does not own Gemini or network.
  - This was not injected provider, not monkeypatched provider, and not a prepared domain fixture.
  - Root boundary was created with Root decision `needs_more_evidence`; this is a happy path for a safety/uncertainty request, not physical-action approval.
  - Provider proposes semantics. Runtime canonicalizes. Validators verify. Root decides.
  - External provider output did not emit internal canonical `structured_rationale` objects; runtime built `structured_orchestrator_rationale`, `structured_architect_rationale`, and safe local PlanGraph nodes.
  - Validated artifacts: OrchestratorRouteContextPacket accepted, ArchitectPlanContextPacket accepted, structured_orchestrator_rationale accepted, structured_architect_rationale accepted, PlanGraph is not authority, ResultProposal is not FinalOutput, Root remains final authority, and validation_errors=[].
  - Safety counters stayed zero: action_permission_created_count: 0, action_commit_packet_created_count: 0, connector_called_count: 0, real_world_effects_count: 0.
  - Provider semantic summary: sealed historical artifact movement after hours, missing approval and unknown climate status remained uncertainty, route `unknown_request_root_review`, vector `unknown_request_semantic_review`, Architect recommendation `needs_more_evidence`.
  - Runtime built safe local nodes `node:unknown_request_semantic_review` and `node:root_review_gate`.
  - Prior real-live attempts 001-006 are superseded diagnostics: the full provider-canonical structured rationale contract was too heavy, compact object-array rationale remained weak/timeout-prone, and `semantic_reasoning_adapter` + `json_mime_only` resolved the live happy path.
  - Superseded next-step note: BoundedSemanticEvidencePacket has now reached real Gemini Slice D 004 PASS; Supplier Payment / Shipment Release Review WOW v1.1 deterministic sandbox business WOW is now PASS.

- `auditor_semantic_reasoning_adapter_delegation_slice_c_v01.log`
  - Audit status: PASS.
  - Slice A/B/C are closed for semantic reasoning adapter core extraction and runner delegation.
  - `hedgehog.semantic_reasoning_adapter` is now core.
  - The live unknown-request runner delegates semantic adapter mechanics to core while retaining Gemini/provider/env/prompt/orchestration behavior.
  - 007-compatible shape preserved with `node:unknown_request_semantic_review` and `node:root_review_gate`.
  - Compact/full compatibility paths preserved: `compact_rationale_adapter` and `full_structured_rationale`.
  - Replay smoke was monkeypatched and network-free: `no_real_gemini_or_network: true`.
  - Action counters remained zero.
  - Slice D docs sync records this status; BoundedSemanticEvidencePacket has now progressed through core, runner integration, and real Gemini Slice D 004 PASS.

- `auditor_core_extraction_action_mock_fractal_v01.log`
  - Audit status: PASS.
  - Core Extraction checkpoint for ActionCommitPacket, MockConnectorSandbox, and FractalFulfillmentTopology.
  - Extracted modules: `hedgehog.action_commit_packet`, `hedgehog.mock_connector_sandbox`, and `hedgehog.fractal_fulfillment`.
  - Related docs: `docs/full_semantic_e2e_core_contracts_v01.md`, `docs/core_extraction_checkpoint_v01.md`, and `docs/public_wow_core_extracted_fractal_fulfillment_walkthrough_v01.md`.
  - Deterministic extracted-core smoke PASS and dual Gemini extracted-core smoke PASS.
  - Real/external counters remain zero, including connector/payment/shipment/API counters.
  - Root remains final authority.

- `auditor_root_native_dag_drs_audit_report.log`
  - Root-native DAG path, DRS writeback, audit/provenance, sensitive-scan checkpoint.

- `auditor_large_graph_drs_lineage_report.log`
  - Large Graph / Bounded Fractal Stress and DRS Graph Proximity / Lineage checkpoint.

- `auditor_live_gemini_ordered_orchestrator_architect_25_success_report.log`
  - Final success proof for Ordered Live Gemini Orchestrator->Architect Smoke v0.1.
  - Shows live Gemini 2.5 as valid Orchestrator proposal actor first, then live Gemini as Architect proposal role after local schema-backed validation.
  - Key success facts: orchestrator_initial_attempt_valid=true, orchestrator_active_proposal_source=live_gemini, orchestrator_active_proposal_is_fallback=false, temporal_query_required_value=true, downstream_actors_missing=[], downstream_actors_extra=[], architect_artifact_source=live_gemini, architect_artifact_valid=true, production_final_output_created=false, production_external_action_executed=false.

- `auditor_controlled_orchestrator_matrix_gate_report.log`
  - Proof for Controlled Orchestrator Matrix Gate v0.1.
  - Shows Root-created RootMatrixGateDecision artifacts over seven scenarios: accept, reject, and downgrade.
  - Verifies the final ordered Gemini 2.5 success report before using it as live-role context: success_report_exists=true, success_report_verified=true, success_report_missing_markers=[].
  - Confirms AVF / Attractor formation is not invoked yet, Orchestrator does not write DRS or create FinalOutput, and no production external action is executed.

- `auditor_avf_attractor_from_accepted_matrix_report.log`
  - Proof for AVF / Attractor Formation from accepted Matrix v0.1.
  - Shows accepted and downgraded RootMatrixGateDecision outputs forming bounded AttractorPacket-like artifacts.
  - Confirms rejected matrices do not reach AVF and create no AttractorPacket.
  - Confirms Architect / Executor are not invoked, AVF does not create FinalOutput or write DRS, and no production external action is executed.

- `auditor_architect_from_bounded_attractor_packet_report.log`
  - Proof for Architect from bounded AttractorPacket v0.1.
  - Shows accepted and downgraded bounded AttractorPacket-like inputs creating valid Architect PlanGraph proposals.
  - Confirms rejected matrix, raw Orchestrator matrix, raw unchecked user intent, and invalid/unbounded AttractorPacket inputs are blocked before Architect.
  - Confirms invalid Architect artifact is contained, Executor / Post V&V / GT are not invoked, Architect does not create FinalOutput or write DRS, and no production external action is executed.

- `auditor_dag_executor_from_valid_plan_graph_report.log`
  - Proof for DAG / Executor from valid PlanGraph v0.1.
  - Shows accepted and downgraded valid Architect PlanGraph proposals creating ResultProposal artifacts.
  - Confirms invalid Architect artifact, raw Architect text, raw Orchestrator matrix, raw user intent, and unvalidated PlanGraph inputs are blocked before Executor.
  - Confirms Executor returns ResultProposal only, does not create FinalOutput, does not write DRS directly, does not execute real external actions, and Post V&V / GT are not invoked.

- `auditor_post_vv_from_result_proposal_report.log`
  - Proof for Post V&V from ResultProposal v0.1.
  - Shows completed and degraded ResultProposal artifacts creating accepted/degraded ValidationReport artifacts.
  - Confirms raw Executor text, raw Architect PlanGraph, raw Orchestrator matrix, raw user intent, and real action output are blocked before Post V&V.
  - Confirms malicious FinalOutput / DRS write claims and malformed ResultProposal input are rejected.
  - Confirms Post V&V creates ValidationReport / V&VReport only, does not create FinalOutput, does not write DRS directly, does not execute actions, and GT / Root Final are not invoked.

- `auditor_gt_from_validation_report.log`
  - Proof for GT from ValidationReport v0.1.
  - Shows accepted, degraded, and rejected ValidationReport artifacts creating accept/degrade/reject GTDecision artifacts.
  - Confirms raw ResultProposal, raw Executor text, raw Architect PlanGraph, raw Orchestrator matrix, raw user intent, and real action output are blocked before GT.
  - Confirms malicious FinalOutput / DRS write / action execution claims and malformed ValidationReport input are rejected.
  - Confirms GT creates GTDecision / selection artifact only, does not create FinalOutput, does not write DRS directly, does not execute actions, and Root Final is not invoked.

- `auditor_root_final_from_gt_decision.log`
  - Proof for Root Final from GTDecision v0.1.
  - Shows accept, degrade, and reject GTDecision artifacts creating accepted/degraded/rejected RootFinalArtifact outputs.
  - Confirms raw ValidationReport, raw ResultProposal, raw Executor text, raw Architect PlanGraph, raw Orchestrator matrix, raw user intent, and real action output are blocked before Root Final.
  - Confirms malicious GT FinalOutput / DRS write / action execution claims and malformed GTDecision input are rejected.
  - Confirms Root is the only FinalOutput authority, GT does not create FinalOutput, Root does not write DRS in this layer, DRS writeback is not invoked, no production persistence is claimed, and no production external action is executed.

- `auditor_drs_writeback_from_root_final.log`
  - Proof for DRS Writeback / Audit from Root Final v0.1.
  - Confirms the proof actually consumes Root Final output and only valid RootFinalArtifact inputs create three `local_audit_only` accepted/degraded/rejected records.
  - Confirms raw upstream inputs, malformed RootFinalArtifact input, and malicious global DRS, external DRS network, production persistence, Root DRS write, and real action claims are rejected.
  - Confirms DRS is not authority, Root authority is preserved, and no production persistence, global/external DRS, or real external action is claimed.

- `auditor_root_native_sandbox_needleruntime_e2e.log`
  - Proof for Root-native sandbox NeedleRuntime E2E v0.1.
  - Shows a validated Root-approved PlanGraph node invoking bounded sandbox/mock NeedleRuntime and flowing through NeedleExecutionResult, ResultProposal, Post V&V, GTDecision, and Root FinalArtifact.
  - Confirms completed/degraded/blocked/failed outcomes remain visible and raw output plus malicious FinalOutput, DRS write, bypassing Root, and external-action claims are rejected.
  - Confirms NeedleRuntime is not authority and no real external action, production persistence, Telegram, or global/external DRS is claimed.

- `auditor_fractal_cell_runtime.log`
  - Proof for Fractal Cell Runtime v0.1.
  - Shows a non-atomic parent PlanGraph node creating a bounded ChildCellRequest, deterministic child mini-cell, ChildBoundarySnapshot, and ResultProposal-compatible parent artifact visible to Post V&V, GT, and Root Final.
  - Confirms atomic and NeedleRuntime routes remain distinct; completed/degraded/blocked/failed child outcomes remain visible; raw output and malicious child authority claims are rejected.
  - Confirms child cell and child Orchestrator are not Root, recursion and budget are bounded, and no child FinalOutput, parent DRS write, live child LLM/SLM, or real external action occurs.

- `auditor_live_child_executor_in_fractal_cell_deterministic.log`
  - Deterministic safe-fallback proof for Live Child Executor in Fractal Cell v0.1.
  - Confirms no live network/Gemini use, reports `SAFE_FALLBACK_NOT_LIVE_SUCCESS`, preserves the completed and action-like-blocked child paths through Root, and includes 36 focused / 1082 full-suite passing tests.

- `auditor_live_child_executor_in_fractal_cell_LIVE.log`
  - Live Gemini PASS proof for Live Child Executor in Fractal Cell v0.1.
  - Confirms live opt-in/network use with Gemini only as bounded child Executor, valid completed proof-task output, valid action-like request blocking, no fallback, and no API/tool call, real action, child FinalOutput, parent DRS write, bypassing Root, or Post V&V / GT / bypassing Root.

- `auditor_drs_lifecycle_semantics.log`
  - Proof for DRS Lifecycle Semantics v0.2.
  - Confirms current proof collectors produce 13 local/proof-level, pointer-first ExperienceRecord examples across completed, degraded, blocked, failed, rejected, quarantined, deadend, and promotion_candidate states.
  - Confirms automatic needle creation is blocked, installed needle count remains zero, trust/TTL metadata is advisory, source conflict status defaults to `not_checked`, and Root remains commit authority.

- `auditor_conflictcheck.log`
  - Proof for ConflictCheck v0.1.
  - Confirms 13 unchanged DRS Lifecycle ExperienceRecord objects produce 11 ConflictCandidatePair and 11 ConflictReport objects across contradiction, risk, and compatible-lineage comparisons.
  - Confirms ConflictCheck recommendations are advisory only: no truth decision, DRS mutation, invalidation, promotion, demotion, production persistence, global/external DRS, or real external action occurs; Root remains final authority.

- `auditor_audit_hash_chain.log`
  - Proof for Audit / hash-chain hardening v0.1.
  - Confirms seven deterministic append-only evidence links, valid chain continuity, eight detected tamper classes, unchanged source artifacts, and eight rejected malicious authority/persistence claims.
  - Confirms hash-chain proves continuity, not truth: it does not mutate DRS or artifacts, grant authority, replace GT / ConflictCheck / Root, implement blockchain, or provide production persistence.

- `auditor_controlled_root_orchestrator_route_assembly.log`
  - Proof for Controlled RootOrchestrator Route Assembly Integration v0.1.
  - Confirms delegated bounded route-assembly authority across eight deterministic scenarios while Root / MatrixGate / RouteGate / Policy / AVF preserve authority and boundary continuity.
  - Confirms this standalone proof does not replace production RootOrchestrator runtime, manage AVF, call live network, execute actions, write production DRS, or claim production autonomy.

- `auditor_applied_warehouse_semantic_demo.log`
  - Proof for Applied Warehouse Semantic Demo / Warehouse-Style Proof v0.1.
  - Confirms W-17 / D-2042 resolves to `not_ready` from explicit `water_filter short_by_2` evidence, with explicit applied PlanGraph, execution, validation, GT, lifecycle, conflict, artifact, and audit-entry objects.
  - Confirms applied artifact consistency and proof-only hash linkage; no production autonomy, persistence, global/external DRS, or real action occurs.

- `auditor_applied_warehouse_semantic_demo_postcommit.log`
  - Postcommit audit evidence for commits `9342b59` and `0de8db6`.
  - Confirms the applied warehouse proof remains PASS after commit, with focused/full-suite verification and a clear sensitive scan.

- `auditor_applied_certificate_readiness_demo.log`
  - Proof for Applied Certificate / Document Readiness Demo v0.1.
  - Confirms APP-77 / CERT-310 resolves to `not_ready` from expired insurance and a missing payment receipt through explicit applied artifacts.
  - Confirms no external submission, protocol candidate, needle candidate, installed needle, production persistence, or production autonomy.

- `auditor_applied_certificate_readiness_demo_postcommit.log`
  - Postcommit audit evidence for commits `aa55384` and `2c9a23f`.
  - Confirms the applied certificate proof remains PASS after commit, with focused/full-suite verification and a clear sensitive scan.

- `auditor_permission_needsuser_ux_proof.log`
  - Proof for Permission / NeedsUser UX Proof v0.1.
  - Confirms five permission scenarios preserve blocked/needs-user/denied/future-permission semantics without claiming completed action.
  - Confirms permission bypass and completed-action-without-execution claims are rejected; no real action, production persistence, or automatic candidate/needle creation occurs.

- `auditor_permission_needsuser_ux_proof_postcommit.log`
  - Postcommit audit evidence for commits `cd0ce4c` and `7d2a121`.
  - Confirms the permission proof remains PASS after commit, with focused/full-suite verification and a clear sensitive scan.

- `auditor_needlecandidate_lifecycle_proof.log`
  - Proof for NeedleCandidate lifecycle / NeedleForge prototype v0.1.
  - Confirms two bounded safe candidates remain pending Root review while unsafe auto-submit, ready-override, permission-bypass, and installed-needle claims are rejected or quarantined.
  - Confirms `needle_candidate_created=true`, `installed_needle_created=false`, no real action, production persistence, or global DRS write.

- `auditor_needlecandidate_lifecycle_proof_postcommit.log`
  - Postcommit audit evidence for commits `acb5aac` and `7fc0a1b`.
  - Confirms the NeedleCandidate proof remains PASS after commit, with 28 NeedleCandidate tests, focused/full-suite verification, and a clear sensitive scan.

- `auditor_applied_drs_retrieval_reuse.log`
  - Proof for Applied DRS Retrieval / Reuse v0.1.
  - Confirms seven advisory retrieval/reuse scenarios preserve freshness, WorldState, permission, quarantine/deadend, ConflictCheck, GT, audit, and Root boundaries.
  - Confirms no direct ready, completed external action, new candidate/needle, production persistence, or global DRS write.

- `auditor_applied_drs_retrieval_reuse_postcommit.log`
  - Postcommit audit evidence for commits `0bbf81a`, `3fdc78e`, and `420b005`.
  - Confirms the proof remains PASS after the module-scoped fixture optimization: 22 targeted tests, 120 focused tests, 1269 full-suite tests, and a clear sensitive scan.
  - Fixture optimization removed repeated `_report()` collection across Applied DRS and NeedleCandidate tests; targeted times improved to about 15.55s and 7.88s, focused tests to about 106.41s, and the post-fixture full suite to about 171.50s.

- `auditor_post_super_smoke_full_suite.log`
  - Full-stack evidence after DRS Adversarial Stress Pack v0.1 and the all-layers applied super-smoke.
  - Confirms adversarial targeted tests passed=14, super-smoke targeted tests passed=12, and the full suite passed=1295 with 37 warnings.

- `auditor_human_applied_stack_walkthrough.log`
  - Human-readable walkthrough and applied-stack evidence for commits `398dace`, `9824431`, `27a5b1b`, and `db18c6e`.
  - Confirms the walkthrough was manually inspected and its sensitive scan was clear.

- `auditor_applied_travel_readiness_demo.log`
  - Applied Travel / Multi-condition Readiness Demo v0.1 evidence.
  - Confirms targeted tests passed=16 and the Root result remains `not_ready`.

- `auditor_multi_domain_applied_smoke_v02.log`
  - Multi-domain Applied Smoke v0.2 evidence.
  - Confirms targeted tests passed=16 and three domains remain separately Root-governed.

- `auditor_controlled_fractal_dac_expansion_v01.log`
  - Controlled Fractal DAC Expansion v0.1 evidence.
  - Confirms targeted tests passed=26 and five local proof-mode child-cell candidates remain bounded under Root aggregation.

- `auditor_dual_fractal_coupling_v01.log`
  - Dual Fractal Coupling / Interlocking DAC Proof v0.1 evidence.
  - Confirms targeted tests passed=35 and semantic coupling transfers no authority, finalization, execution, or DRS write.

- `auditor_cross_domain_drs_bridge_v01.log`
  - Cross-domain DRS Traversal / DRS Bridge Proof v0.1 evidence for commits `2a48d35`, `1b6b5e0`, and `a2721af`.
  - Confirms targeted tests passed=30, sensitive scan clean, bridge records observed=2, and traversal steps observed=2.
  - Confirms `external_drs_implemented=false` and `global_semantic_fabric_claimed=false`; traversal informs but cannot decide, finalize, execute, transfer authority, or prove truth.

- `auditor_needle_adversarial_safety_pack_v01.log`
  - Needle adversarial / safety pack v0.1 evidence for commits `5b5fa3a`, `165d679`, and `1f9d89d`.
  - Confirms targeted tests passed=30, adversarial attempts observed=8, attempts blocked=8, quarantined attempts observed=1, and sensitive scan clean.
  - Confirms no installed Needle, external action, production persistence, or global/external DRS write.

- `auditor_external_drs_pointer_protocol_v01.log`
  - External DRS Pointer Protocol v0.1 evidence for commits `0a690c5`, `3e3cc3d`, and `2036247`.
  - Confirms targeted tests passed=28, pointer candidates observed=2, pointer candidates accepted=0, adversarial attempts observed=6, attempts blocked=6, quarantined attempts observed=1, and sensitive scan clean.
  - Confirms performance hygiene with `source_collectors_replayed=false` and a clean heavy historical collector replay check.
  - Confirms no External DRS, retrieval, connector, trusted evidence, truth, DRS write, installed Needle, or external action.

- `auditor_read_only_enterprise_connector_sandbox_v01.log`
  - Read-only Enterprise Connector Sandbox v0.1 evidence for commits `5110d14`, `01a6b64`, and `af872eb`.
  - Confirms targeted tests passed=18, connector observations=4, adversarial attempts=6, blocked attempts=6, and quarantined attempts=1.
  - Confirms the heavy historical collector replay check, overclaim scan, and sensitive scan are clean.
  - Confirms no trusted evidence, truth, ready status, DRS write, installed Needle, external action, network, or production persistence.

- `auditor_external_evidence_acceptance_gate_v01.log`
  - External Evidence Acceptance Gate v0.1 evidence for commits `ece902f`, `00e98cd`, and `632ecb1`.
  - Confirms targeted tests passed=18, evidence candidates=6, validation packets=6, accepted=2, rejected=3, quarantined=1, adversarial attempts=8, and blocked attempts=8.
  - Confirms candidate wiring keeps EvidenceCandidate `candidate_only` before Root decision.
  - Confirms the heavy historical collector replay check, overclaim scan, and sensitive scan are clean.

- `auditor_enterprise_chaos_pack_v01.log`
  - Enterprise Chaos Pack v0.1 evidence for commits `082753e`, `104105b`, and `668a51a`.
  - Confirms 18 enterprise chaos attempts were observed, detected, and blocked; four were quarantined and blocked.
  - Confirms four closed checkpoints were referenced with `source_evidence_mode=closed_checkpoint_metadata_only`, `source_collectors_replayed=false`, and replay count=0.
  - Confirms Root rejected enterprise-ready, action, and truth, with no network, Gemini, DRS write, installed Needle, external action, or production persistence.

- `auditor_compute_collapse_enterprise_bench_v01.log`
  - Compute Collapse Enterprise Bench v0.1 evidence for commits `bc606ff`, `5cc0516`, and `baac894`.
  - Audit status PASS. Confirms `baseline_llm_calls=29`, `hedgehog_llm_calls=1`, and context units `180 -> 32`.
  - `hedgehog_llm_calls=1` is a synthetic routed-path estimate, not a real LLM call by the walkthrough or audit.
  - Confirms `source_collectors_replayed=false`, `production_economics_claimed=false`, `real_billing_claimed=false`, `real_latency_claimed=false`, and `killer_demo_authorized=false`.
  - Confirms Root remains final authority.

- `auditor_kernel_enforcement_transition_matrix_v01.log`
  - Kernel Enforcement / Transition Matrix Hardening v0.1 evidence for commits `5acfc8a`, `5212eec`, and `9d648e3`.
  - Audit status PASS. Confirms `allowed_transitions_count=10`, `blocked_transitions_count=35`, and `focused_tests_passed=15`.
  - Confirms `transition_matrix_is_authority=false` and `transition_matrix_is_production_runtime_authority=false`.
  - Confirms `drs_writeback_scope=local_after_root_final`, `local_drs_writeback=true`, `global_drs_write=false`, and `external_drs_write=false`.
  - Confirms Root remains final authority.

- `auditor_developer_facade_capability_manifest_ux_v01.log`
  - Developer Facade / Capability Manifest UX v0.1 evidence for commits `dd18d5f`, `85c7e56`, and `a2b9479`.
  - Audit status PASS. Confirms `manifest_candidates_created=6`, `facade_validated_manifest_candidates=3`, `rejected_manifest_candidates=2`, and `needs_user_manifest_candidates=1`.
  - Confirms `adversarial_attempts_blocked=10` and `focused_tests_passed=16`.
  - Confirms `installed_capabilities_created=0`, `installed_needles_created=0`, `developer_manifest_is_authority=false`, `validated_manifest_is_truth=false`, and `validated_manifest_is_final_output=false`.
  - Confirms `developer_facade_does_not_authorize_killer_demo=true`.

- `auditor_enterprise_killer_demo_v01.log`
  - Enterprise Killer Demo v0.1 / Demo A evidence for commits `23a0cfe`, `a8940f2`, and `c955524`.
  - Audit status PASS. Confirms `demo_mode=Enterprise Killer Demo A — Authority / Safety / Compute Collapse` and `demo_b_implemented=false`.
  - Confirms `act_count=3`, `adversarial_attempts_blocked=18`, `root_final_status=not_ready`, and `safe_secondary_outcome=needs_human_review`.
  - Confirms `real_external_action_executed=false` and `production_ready_claimed=false`.

- `auditor_enterprise_document_killer_demo_b_v01.log`
  - Enterprise Document Killer Demo B v0.1 evidence for design doc commit `bb1f7c2`, proof commit `46d9bfe`, human walkthrough commit `e3b6ed9`, and audit log commit `d4c6668`.
  - Audit status PASS. Confirms `demo_mode=Enterprise Document Killer Demo B — Document / Evidence Workflow`.
  - Confirms Demo B is an applied proof, not engine: `demo_b_is_applied_proof_not_engine=true`.
  - Confirms `fixture_fidelity_verified=true`, `canonical_vendor=ALPHA SUPPLY`, `canonical_amount=18400 EUR`, and `canonical_shipment_id=SHIP-900`.
  - Confirms ACT 1 `not_ready`, ACT 2 `adversarial_attempts_blocked=18`, ACT 3 `ready_for_internal_release`, and ACT 4 `act_4_resolution_source=Root-approved Local DRS Reuse`.
  - Confirms blind auditor notes were accepted and `schema_contract_alignment_required=true`, `runtime_jsonschema_hardening_required=true`, and `evidence_kind_alignment_required=true`.
  - Later hardening after Demo B docs sync began with Schema Contract Alignment / Runtime Schema Validation Hardening v0.1 preflight; Phase 1 is now closed separately.

- `auditor_schema_contract_alignment_phase1_attractor_packet_v01.log`
  - Schema Contract Alignment v0.1 Phase 1 audit for the AttractorPacket Architect-facing contract.
  - Audit status PASS. Evidence: preflight commit `d6aaf9f`, patch commit `bd0c518`, audit commit `233b4d5`.
  - Confirms Finding A is closed for the active AttractorPacket contract: `finding_a_schema_contract_drift_status=closed_for_active_attractor_packet_contract`.
  - Confirms active schema/runtime use `must_return_plan_graph_only`, Architect returns PlanGraph only, Executor / DAG returns ResultProposal, and Root remains final authority.
  - Confirms Findings B/C/D/E remain open: Runtime JSON Schema Validation Hardening, EvidenceItem.kind vocabulary alignment, artifact_type vocabulary alignment, and focused coverage gaps.

- `auditor_schema_contract_alignment_phase2_executor_dag_resultproposal_v01.log`
  - Schema Contract Alignment v0.1 Phase 2 audit for Executor / DAG ResultProposal contract wording.
  - Audit status PASS. Evidence: plan commit `fad2276`, wording patch commit `146d44c`, audit commit `6e47485`.
  - Confirms `patch_type=docs_spec_wording_contract_alignment`.
  - Confirms runtime/schema/tests unchanged: `runtime_modified=false`, `schemas_modified=false`, and `tests_modified=false`.
  - Confirms ResultProposal-shaped boundary artifacts are not FinalOutput, not authority, do not authorize action, and do not write DRS.
  - Confirms Post V&V / GT / Root remain required after the ResultProposal boundary and Root remains final authority.
  - Confirms Findings B/C/D/E remain open after Phase 2.

- `auditor_runtime_jsonschema_hardening_post_vv_resultproposal_v01.log`
  - Runtime JSON Schema Validation Hardening v0.1 audit for Post V&V incoming ResultProposal runtime schema validation.
  - Audit status PASS. Evidence: preflight commit `3207a19`, runtime patch commit `48e2515`, audit commit `107a7c4`.
  - Confirms `patch_type=runtime_post_vv_incoming_resultproposal_schema_validation`.
  - Confirms `result_proposal_runtime_schema_validation_present=true` and `post_vv_validates_incoming_resultproposal_schema=true`.
  - Confirms schema validation runs before manual checks, is additive, and records `schema_validation_replaces_manual_checks=false`.
  - Confirms schema failures return the V&V report path without crashing, manual policy/safety checks are preserved, and Root remains final authority.
  - Superseded for outgoing boundary status by `auditor_outgoing_vvreport_runtime_validation_v01.log`.

- `auditor_outgoing_vvreport_runtime_validation_v01.log`
  - Outgoing VVReport Runtime Schema Validation v0.1 audit for Post V&V outgoing VVReport runtime schema validation.
  - Audit status PASS. Evidence: preflight commit `c6e1bf7`, runtime patch commit `187461d`, audit commit `916a913`.
  - Confirms `patch_type=runtime_post_vv_outgoing_vvreport_schema_validation`.
  - Confirms `outgoing_vv_report_runtime_schema_validation_present=true` and `post_vv_validates_outgoing_vvreport_schema=true`.
  - Confirms outgoing validation runs before return, is additive, preserves manual checks, and falls back to safe rejected VVReport on validation failure.
  - Confirms EvidenceItem.kind / artifact_type remain open.

- `auditor_evidenceitem_kind_alignment_v01.log`
  - EvidenceItem.kind Alignment v0.1 audit for the narrow enum expansion.
  - Audit status PASS. Evidence: plan commit `2685921`, patch commit `4ced110`, audit commit `0eb58c1`.
  - Confirms `patch_type=narrow_evidenceitem_kind_enum_expansion`.
  - Confirms the exact enum addition is `fractal_dag_executor` only.
  - Confirms `audit_added_to_evidenceitem_kind=false`, `needle_runtime_added_to_evidenceitem_kind=false`, and `artifact_vocab_terms_added_to_evidenceitem_kind=false`.
  - Confirms authority guardrails: EvidenceItem.kind does not create truth, authority, AcceptedEvidence, action permission, DRS write, or FinalOutput; Root remains final authority.
  - Confirms NeedleRuntime evidence shape and artifact_type Mapping remain deferred.

- `auditor_needleruntime_audit_evidence_shape_v01.log`
  - NeedleRuntime Audit Evidence Shape v0.1 audit for the narrow Option B patch.
  - Audit status PASS. Evidence: preflight commit `99592a6`, patch plan commit `fd9e862`, patch commit `f0bf7be`, audit commit `0b2ffc8`.
  - Confirms `patch_type=option_b_add_audit_and_normalize_shape`.
  - Confirms exact enum addition `audit` and `audit_added_to_evidenceitem_kind=true`.
  - Confirms `needle_runtime_added_to_evidenceitem_kind=false` and `artifact_vocab_terms_added_to_evidenceitem_kind=false`.
  - Confirms NeedleRuntime evidence shape changed from `kind: audit; evidence_id; description; ref` to `kind: audit; summary; ref_id` with `confidence_added=false`.
  - Confirms authority guardrails: audit evidence does not create truth, authority, AcceptedEvidence, action permission, DRS write, or FinalOutput; audit hash is not truth; Root remains final authority.
  - Confirms artifact_type Mapping remains deferred.

- `auditor_artifact_type_mapping_runtime_vocabulary_v01.log`
  - artifact_type Mapping / Runtime Artifact Vocabulary v0.1 audit for the Option A docs/spec human-readable artifact vocabulary map.
  - Audit status PASS. Evidence: preflight commit `b4aaf8e`, patch plan commit `c4f9a02`, map commit `d3193a2`, audit commit `27bee7d`.
  - Confirms Option A docs/spec map only.
  - Confirms no runtime/schema/test/registry/enum changes.
  - Confirms canonical axes: artifact_type, source_artifact_type, EvidenceItem.kind, TraceRef.kind, lifecycle_state/status, and authority_status.
  - Confirms Root authority guardrails: artifact_type and source_artifact_type do not create truth or authority; TraceRef.kind does not create evidence; GTReport remains advisory; DRSRecord remains memory/audit; RootFinalOutput is Root-created only.
  - Confirms full artifact vocabulary completion is not claimed.

- `auditor_long_lived_drs_ttl_aging_stress_v01.log`
  - Long-lived DRS State / TTL / Aging Stress v0.1 audit: `audited_commit: d3840db`, `audit_commit: f1eefee`.
  - `audit_status: PASS`, `proof_status: PASS`, `scenarios_total: 25`, `scenarios_passed: 25`, `25/25 scenarios` PASS, and `19 focused tests` PASS.
  - Confirms TemporalHardGate, FreshnessOK, DirectReuseAllowed, RootShortcutAllowed, trust-aware supersession, bounded proximity through CandidateSet_pre / max_lineage_hops, ReuseBoost isolation, AcceptedEvidence(t_old) != ActionPermission(t_now), audit replay boundary, and Root final authority.
  - Confirms limitations: deterministic local proof only, not production DRS, not external/global DRS, not real database, not distributed DRS, not real clock security, not runtime integration, not schema change, and not deployment/public-auditor readiness.

- `auditor_human_long_lived_drs_ttl_aging_stress_walkthrough_v01.log`
  - Human Long-lived DRS TTL Aging walkthrough audit for commit `e22ee04`; audit commit `4a30d39`.
  - `audit_status: PASS_WITH_SCOPE_WARNING`, `walkthrough_status: PASS`, `targeted_tests_status: PASS`, focused tests: 3 passed, `3 focused tests`.
  - `full_pytest_status: FAIL_KNOWN_GLOBAL_DRIFT`; full pytest observed: 25 failed, 1667 passed, 60 warnings.
  - Confirms full pytest failures outside walkthrough scope and likely post-hardening expectation drift.
  - Confirms Demo B bridge is narrative only, not merged Killer Demo B proof, and does not rerun Demo B as executable proof.
  - Confirms no runtime/schema/prod DRS/external DRS/network/Gemini/Marennya/UP.
  - Recommends Full Suite Drift Triage / Repair v0.1.

- `auditor_full_suite_drift_repair_phase1_resultproposal_alignment_v01.log`
  - Full Suite Drift Repair Phase 1 audit for commit `ef8b63b`; audit commit `627ab74`; preflight commit `99455db`.
  - `audit_status: PASS`; `patch_type: narrow_runtime_schema_contract_alignment`.
  - Root cause: schema-invalid top-level node_id in Fractal DAG ResultProposal.
  - Before repair: 25 failed, 1667 passed, 60 warnings.
  - After repair: 1692 passed, 60 warnings, 0 failed.
  - Confirms no schema relaxation, no Post V&V weakening, no forced GT accept, no forced Root success, and no skip/xfail.
  - Confirms Executor still returns ResultProposal only, Post V&V remains the ResultProposal validator, GT remains advisory/selection, and Root remains final authority.

- `auditor_drs_lineage_provenance_pressure_v01.log`
  - DRS Lineage / Provenance Pressure v0.1 technical audit for commit `d3d13c1`; audit commit `24b64c2`; preflight `e60b40f`; patch plan `7415be3`.
  - `audit_status: PASS`; scope: deterministic local proof runner and focused tests.
  - Key counters: `scenarios_total: 10`, `scenarios_passed: 10`, `direct_reuse_allowed_count: 0`, `direct_reuse_blocked_count: 10`, `root_review_required_count: 10`, and `root_final_authority_preserved_count: 10`.
  - Authority counters: `lineage_decides_count: 0`, `provenance_truth_claimed_count: 0`, `audit_hash_truth_claimed_count: 0`, `bridge_authority_transfer_count: 0`, `quarantine_global_taint_count: 0`, `deadend_global_taint_count: 0`, `conflictcheck_authority_count: 0`, and `gt_authority_count: 0`.
  - Confirms lineage informs, lineage does not decide; provenance does not become truth; audit/hash-chain proves continuity, not truth; bridge traversal is not authority transfer; quarantine/deadend proximity is bounded; ConflictCheck and GT remain advisory; Root remains final authority.
  - Limitations: deterministic local proof only; no production DRS, external/global DRS, network, Gemini, Marennya, UP, runtime integration, or schema mutation.
  - Next step was human-readable walkthrough.

- `auditor_human_drs_lineage_provenance_pressure_walkthrough_v01.log`
  - Human DRS Lineage / Provenance Pressure walkthrough audit for commit `fefd6a4`; audit commit `b486171`; technical audit `24b64c2`.
  - `audit_status: PASS`; scope: human-readable walkthrough and focused tests.
  - Confirms `underlying_proof_status: PASS`, `walkthrough_required_counters_match: True`, focused tests: `7 passed`, and the human acts cover trace ancestry, AcceptedEvidence ancestry, bridge traversal, quarantine/deadend bounded pressure, conflicting provenance, supersession review, audit continuity, popular lineage, and composite pressure ending at Root.
  - Confirms the walkthrough is explanatory, imports and reflects audited proof behavior, does not change proof logic, and creates no runtime capability, action permission, DRS write authority, or Root Final authority.
  - Limitations: deterministic local human walkthrough only; no production DRS, external/global DRS, real connector, network, Gemini, Marennya, UP, runtime integration, schema mutation, or readiness packet.
  - Next step: Docs sync / checkpoint closure.

- `auditor_compromised_upstream_pack_v01.log`
  - Compromised Upstream Pack v0.1 technical audit for commit `c131ddc`; audit commit `b17c096`; preflight `2ec1266`; patch plan `003bcf3`.
  - Proof status: PASS. Technical audit status: PASS. Scope: deterministic local proof runner and focused tests.
  - Key counters: `scenarios_total: 6`, `scenarios_passed: 6`, and `root_final_authority_preserved_count: 6`.
  - Scenario coverage: compromised_bank_source_cannot_create_truth, stale_legal_source_signed_looking_forces_review, warehouse_source_contradiction_blocks_ready, external_pointer_trust_laundering_rejected, accepted_evidence_from_compromised_source_is_not_action_permission, and root_final_authority_preserved_under_compromised_upstream_pressure.
  - Confirms compromised upstream source pressure does not create source truth, pointer trust, ready status, direct reuse permission, action permission, ValidationPacket authority, EvidenceCandidate authority, AcceptedEvidence action permission, ConflictCheck authority, GT authority, or Root Final authority.
  - Limitations: deterministic local proof only; no production connector, production DRS, external/global DRS, network, Gemini, Negative Trace, DRS Poisoning Resistance, Economic Adversary, Marennya/UP, manifest hardening, or transition matrix mutation.
  - Root remains final authority.

- `auditor_human_compromised_upstream_pack_walkthrough_v01.log`
  - Human Compromised Upstream Pack walkthrough audit for commit `38be1d1`; audit commit `8dc22d3`; technical audit `b17c096`; proof `c131ddc`.
  - Human walkthrough status: PASS. Human walkthrough audit status: PASS. Scope: human-readable walkthrough and focused tests.
  - Confirms `underlying_proof_status: PASS`, `walkthrough_required_counters_match: True`, focused walkthrough tests: `8 passed`, `scenarios_total: 6`, `scenarios_passed: 6`, and `root_final_authority_preserved_count: 6`.
  - Confirms the walkthrough covers compromised_bank_source_cannot_create_truth, stale_legal_source_signed_looking_forces_review, warehouse_source_contradiction_blocks_ready, external_pointer_trust_laundering_rejected, accepted_evidence_from_compromised_source_is_not_action_permission, and root_final_authority_preserved_under_compromised_upstream_pressure.
  - Confirms official-looking sources, signed-looking stale documents, repeated external pointers, schema-valid content, ValidationPacket, EvidenceCandidate, AcceptedEvidence, ConflictCheck, and GT may inform or force review, but do not become truth, trust, authority, action permission, or Root Final authority.
  - Root remains final authority.
  - Next possible layers may include DRS Poisoning Resistance v0.1 and Economic Adversary v0.1, but they are not implemented by this checkpoint.

- `auditor_real_local_drs_resolver_writeback_v01.log`
  - Real Local DRS Resolver / Writeback v0.1 technical audit for commit `2a18df5`; audit commit `6bb2422`; preflight `55ab2cd`; patch plan `cbe170c`; runtime gate `1e1afe6`.
  - Audit status: PASS. Scope: runtime implementation and tests. Runtime runner: `FINAL STATUS: PASS`. Focused runtime tests: `35 passed, 2 warnings`. Full pytest evidence: `1754 passed, 60 warnings in 934.65s`.
  - Audited runtime seam: `hedgehog/local_drs_resolver.py`, composing existing LocalDRS and local temporal helpers without a separate DRS store, without `hedgehog/external_drs/*`, and without schema changes.
  - Confirms the first runtime-facing primitive under Real Semantic Runtime MVP: write meaning -> resolve meaning -> reuse under Root review.
  - Key counters: `scenarios_total: 8`, `scenarios_passed: 8`, `records_written_count: 9`, `resolve_queries_count: 7`, `candidates_returned_count: 8`, `direct_reuse_allowed_count: 0`, `root_review_required_count: 8`, `poisoning_pressure_authority_claimed_count: 0`, `action_permission_granted_count: 0`, `production_drs_used_count: 0`, `external_drs_used_count: 0`, `network_used_count: 0`, `gemini_used_count: 0`, and `root_final_authority_preserved_count: 8`.
  - Confirms stale record, quarantine proximity, changed WorldState, conflicting provenance, and duplicate poisoning pressure scenarios force review or block candidate reuse instead of creating authority.
  - Confirms raw ValidationPacket-like, EvidenceCandidate-like, ResultProposal-like, and ConnectorObservation-like shapes cannot become RootFinal writeback authority even if they claim `root_reviewed=true` and `created_by=root_orchestrator`.
  - Limitations: not production DRS, not external/global DRS, no network, no Gemini, no autonomous action, no connector side effects, no public WOW, no whitepaper/public auditor packet, no Marennya/UP, no self-modifying manifest, no transition matrix mutation, not separate DRS Poisoning Resistance v0.1, not Economic Adversary v0.1, and Real Semantic Runtime MVP not complete.

- `auditor_human_real_local_drs_resolver_walkthrough_v01.log`
  - Human Real Local DRS Resolver walkthrough audit for commit `118f040`; audit commit `dfbcd6e`; technical audit `6bb2422`; runtime commit `2a18df5`.
  - Human walkthrough status: PASS. Human audit status: PASS. Scope: human-readable walkthrough and focused tests.
  - Confirms `underlying_runtime_status: PASS`, `walkthrough_required_counters_match: True`, focused human walkthrough tests: `4 passed in 0.10s`, `scenarios_total: 8`, `scenarios_passed: 8`, and `root_final_authority_preserved_count: 8`.
  - Confirms all eight runtime scenarios are explained: write_then_resolve_semantic_record_candidate_only, stale_record_forces_root_review, quarantine_proximity_blocks_direct_reuse, changed_worldstate_blocks_old_reuse, conflicting_provenance_blocks_reuse, duplicate_poisoning_pressure_does_not_create_authority, root_review_required_before_reuse_affects_final_output, and writeback_records_root_final_without_action_side_effects.
  - Confirms the human message: DRS record is not truth, DRS hit is not authority, DRS reuse candidate is not action permission, and Root remains final authority.
  - CandidateVectorGenerator + Real AVF Scoring v0.1 is now closed separately after this checkpoint.

- `auditor_candidate_vector_generator_avf_scoring_v01.log`
  - CandidateVectorGenerator + Real AVF Scoring v0.1 technical audit for commit `1506eea`; audit commit `cf3da99`; preflight `97a1437`; patch plan `8f8f78d`; previous runtime checkpoint `4f513d1`; runtime gate `1e1afe6`.
  - Audit status: PASS. Scope: runtime implementation and tests. Runner: `FINAL STATUS: PASS`. Focused tests: `51 passed, 1 warning in 0.27s`. Full pytest evidence: `1772 passed, 60 warnings in 957.62s`.
  - Scope summary: audits `hedgehog/candidate_vector_generator.py`, `demo/run_candidate_vector_generator_avf_scoring_v01.py`, and `tests/test_candidate_vector_generator_avf_scoring_v01_runner.py`.
  - Confirms the second runtime-facing primitive under Real Semantic Runtime MVP: resolved local DRS candidates -> bounded candidate vectors -> deterministic AVF scores -> ranked/reviewable candidate report.
  - Key counters: `avf_scenarios_total: 9`, `avf_scenarios_passed: 9`, `drs_candidates_input_count: 17`, `candidate_vectors_generated_count: 17`, `avf_scores_computed_count: 17`, `ranked_candidates_count: 17`, `top_ranked_candidates_count: 9`, `avf_direct_reuse_allowed_count: 0`, `avf_action_permission_granted_count: 0`, `avf_authority_claimed_count: 0`, `vector_truth_claimed_count: 0`, `schema_validity_truth_claimed_count: 0`, `duplicate_spam_authority_claimed_count: 0`, `high_score_direct_reuse_granted_count: 0`, `avf_network_used_count: 0`, `avf_gemini_used_count: 0`, and `avf_root_final_authority_preserved_count: 9`.
  - Boundary conclusion: Candidate vector is not truth, AVF score is not authority, Top-ranked candidate outputs do not become action permission or direct reuse permission, GT/LGT remains advisory, and Root remains final authority.

- `auditor_human_real_semantic_drs_avf_walkthrough_v01.log`
  - Human Real Semantic DRS -> AVF walkthrough audit for commit `e0ccf54`; audit commit `51bd000`; AVF technical audit `cf3da99`; AVF runtime `1506eea`; DRS checkpoint `4f513d1`; DRS runtime `2a18df5`; DRS technical audit `6bb2422`.
  - Audit status: PASS. Scope: human-readable combined walkthrough and focused tests. Walkthrough command exits 0. Focused tests: `8 passed in 0.24s`.
  - Confirms `walkthrough_required_counters_match: True`, DRS underlying status PASS, AVF underlying status PASS, `drs_scenarios_total: 8`, and `avf_scenarios_total: 9`.
  - Confirms the combined thread: write meaning -> resolve meaning -> candidate only -> generate candidate vector -> deterministic AVF score -> ranked review report -> GT/LGT review required -> Root remains final authority.
  - Combined counters: `combined_direct_reuse_allowed_count: 0`, `combined_action_permission_granted_count: 0`, `combined_network_used_count: 0`, and `combined_gemini_used_count: 0`.
  - Boundary conclusion: Hedgehog OS can now write meaning into local memory, resolve candidate memory, turn candidates into bounded vectors, and score/rank them for review. DRS hits do not become truth, AVF scores do not become authority, top-ranked candidates do not become permission, and Root remains final authority.

- `auditor_gt_lgt_advisory_evaluator_v01.log`
  - GT/LGT Advisory Evaluator v0.1 technical audit for commit `b0ce686`; audit commit `7cbcb77`; preflight `c9ff238`; patch plan `d00fa21`; previous checkpoint `762239c`; runtime gate `1e1afe6`.
  - Audit status: PASS. Scope: runtime implementation and tests. Runner: `FINAL STATUS: PASS`. Targeted tests: `68 passed, 40 warnings`. Full pytest evidence: `1792 passed, 60 warnings`.
  - Topology/naming clarification: the human-facing alias is AVF Candidate Advisory Evaluator v0.1; the internal runtime/checkpoint name remains GT/LGT Advisory Evaluator v0.1. It is pre-Architect candidate-level advisory review over AVF-ranked DRS candidates, emits GT-style advisory signals, does not relocate canonical terminal GTValidator, does not command Architect, returns advisory signals to Root/Orchestrator route decision, and Root remains final authority.
  - LGT handling: LGT is deferred/local placeholder only; no concrete production LGT runtime/schema exists; LGT signals remain advisory-only.
  - Key counters: `scenarios_total: 10`, `scenarios_passed: 10`, `advisory_inputs_count: 10`, `gt_signals_emitted_count: 10`, `lgt_signals_emitted_count: 10`, `lgt_deferred_count: 10`, `advisory_reports_created_count: 10`, `root_review_required_count: 10`, `root_final_authority_preserved_count: 10`, `direct_reuse_allowed_count: 0`, `action_permission_granted_count: 0`, `final_output_created_count: 0`, `gt_authority_claimed_count: 0`, `lgt_authority_claimed_count: 0`, `advisory_truth_claimed_count: 0`, `advisory_accept_as_root_final_count: 0`, `network_used_count: 0`, and `gemini_used_count: 0`.
  - Boundary conclusion: advisory accept/degrade/reject/needs-review signals cannot decide truth, create FinalOutput, grant action permission, grant direct reuse permission, move canonical GTValidator upstream, or override Root.

- `auditor_human_avf_candidate_advisory_evaluator_walkthrough_v01.log`
  - Human AVF Candidate Advisory Evaluator walkthrough audit for commit `5f7cfe7`; audit commit `bc80aae`; technical audit `7cbcb77`; runtime commit `b0ce686`.
  - Audit status: PASS. Scope: human-readable walkthrough and focused tests. Walkthrough command exits 0. Focused tests: `4 passed in 0.11s`.
  - Confirms `underlying_runtime_status: PASS`, `walkthrough_required_counters_match: True`, `scenarios_total: 10`, and `scenarios_passed: 10`.
  - Topology/naming clarification: AVF Candidate Advisory Evaluator v0.1 is the human-facing name for GT/LGT Advisory Evaluator v0.1. It does not relocate canonical terminal GTValidator; canonical GTValidator remains after Executor/Post V&V and before Root FinalOutput. The layer is pre-Architect candidate-level advisory review, does not command Architect, and returns advisory signals to Root/Orchestrator.
  - LGT handling: LGT is deferred/local placeholder only with `lgt_deferred_count: 10` and `lgt_authority_claimed_count: 0`.
  - Boundary conclusion: the walkthrough accurately explains that this small advisory stage cannot decide truth, cannot create FinalOutput, cannot grant action permission, cannot grant direct reuse permission, cannot move canonical GTValidator upstream, and cannot override Root. Root remains final authority.

- `auditor_bounded_llm_slm_actors_v01.log`
  - Bounded LLM/SLM Actors v0.1 technical audit for commit `6802d14`; audit commit `dfd43b9`; preflight `a0e3145`; patch plan `be4995d`; previous checkpoint `68ca777`; runtime gate `1e1afe6`.
  - Audit status: PASS. Scope: runtime implementation and tests. Runner: `FINAL STATUS: PASS`. Targeted tests: `92 passed, 50 warnings`. Full pytest evidence: `1819 passed, 60 warnings`.
  - Scope summary: audits `hedgehog/bounded_actor_contracts.py`, `demo/run_bounded_llm_slm_actors_v01.py`, and `tests/test_bounded_llm_slm_actors_v01_runner.py`.
  - Implementation seam: contract adapter / validator only, not a new execution engine. It does not replace RootOrchestrator, Architect, Executor, Post V&V, GTValidator, or schemas, and it does not activate Gemini/network/model calls.
  - Target Boundary Fix: it is not enough to check what an actor outputs; the system must check where the output is being sent. Dangerous transitions such as Architect PlanGraph -> final_output, Executor ResultProposal -> final_output, Verifier VVReport -> final_output, and GTReport -> final_output are blocked with `final_output_target_boundary_blocked`.
  - Canonical chain accepted: intake -> Root/Orchestrator; Root-shaped route -> Architect; PlanGraph -> Executor; ResultProposal -> Verifier/Post V&V; VVReport -> GT boundary; GTReport -> Root return; Root return -> Root/Orchestrator.
  - Key counters: `scenarios_total: 12`, `scenarios_passed: 12`, `actor_inputs_seen_count: 22`, `actor_outputs_emitted_count: 16`, `intake_outputs_count: 2`, `route_proposals_count: 4`, `plangraph_proposals_count: 3`, `result_proposals_count: 3`, `validation_reports_count: 2`, `root_review_required_count: 16`, `final_output_created_count: 0`, `action_permission_granted_count: 0`, `actor_authority_claimed_count: 0`, `llm_truth_claimed_count: 0`, `slm_truth_claimed_count: 0`, `model_confidence_authority_claimed_count: 0`, `prompt_injection_escalation_count: 0`, `actor_self_promotion_count: 0`, `raw_advisory_command_accepted_count: 0`, `raw_drs_memory_instruction_accepted_count: 0`, `root_boundary_bypass_count: 0`, `post_vv_bypass_count: 0`, `gt_bypass_count: 0`, `manifest_mutation_count: 0`, `transition_matrix_mutation_count: 0`, `network_used_count: 0`, `gemini_used_count: 0`, `connector_side_effect_count: 0`, and `root_final_authority_preserved_count: 12`.
  - Boundary conclusion: actor output is not truth, actor output is not authority, LLM output is not truth, SLM output is not truth, route proposals are not Root decisions, PlanGraph proposals are not execution authority, ResultProposal is not FinalOutput, advisory reports are not commands, and Root remains final authority.
  - Limitations: no production LLM autonomy, no production SLM autonomy, no real model calls, no Gemini activation, no network, no embeddings, no external tool calls, no connector side effects, no autonomous action, no Fractal Cell Runtime integration in this layer, no Root behavior modification, no FinalOutput creation, no action permission, no direct reuse permission, no manifest mutation, no transition matrix mutation, no Marennya/UP, no public WOW, no whitepaper/public auditor packet, and Real Semantic Runtime MVP is not complete.

- `auditor_human_bounded_llm_slm_actors_walkthrough_v01.log`
  - Human Bounded LLM/SLM Actors walkthrough audit for commit `df45900`; audit commit `388749c`; technical audit `dfd43b9`; runtime commit `6802d14`.
  - Audit status: PASS. Scope: human-readable walkthrough and focused tests. Walkthrough command exits 0. Focused tests: `5 passed in 0.05s`.
  - Confirms `underlying_runtime_status: PASS`, `walkthrough_required_counters_match: True`, `scenarios_total: 12`, and `scenarios_passed: 12`.
  - Confirms the walkthrough explains that the layer does NOT create autonomous agents, does NOT activate LLM/SLM/Gemini/network, and creates bounded actor contracts and transition checks so future Fractal Cell Runtime knows who may speak, route, propose, execute, verify, and return to Root.
  - Target-boundary coverage: `final_output_target_boundary_blocked`; Architect PlanGraph -> final_output; Architect PlanGraph -> root_return; Executor ResultProposal -> final_output; Executor ResultProposal -> root_return; Verifier VVReport -> final_output; Verifier VVReport -> root_return; GTReport -> final_output; GTReport -> Architect.
  - Canonical chain accepted: intake -> Root/Orchestrator; Root-shaped route -> Architect; PlanGraph -> Executor; ResultProposal -> Verifier/Post V&V; VVReport -> GT boundary; GTReport -> Root return; Root return -> Root/Orchestrator.
  - Boundary conclusion: the walkthrough accurately explains the role-boundary skeleton for bounded actors. It does not make autonomous agents, prevents role confusion before Fractal Cell Runtime integration, and keeps Root as final authority.
  - Limitations: no production LLM autonomy, no production SLM autonomy, no real model calls, no Gemini activation, no network, no external tool calls, no connector side effects, no autonomous action, no Fractal Cell Runtime integration in this layer, no Root behavior modification, no FinalOutput creation, no action permission, no direct reuse permission, no manifest mutation, no transition matrix mutation, no Marennya/UP, no public WOW, no whitepaper/public auditor packet, and Real Semantic Runtime MVP is not complete.

- `auditor_fractal_cell_runtime_integration_v01.log`
  - Fractal Cell Runtime Integration v0.1 technical audit for commit `96755ba`; audit commit `643d6cd`; preflight `84303eb`; patch plan `9f49cbc`; previous checkpoint `09523bf`; runtime gate `1e1afe6`.
  - Audit status: PASS. Scope: runtime implementation and tests. Runner: `FINAL STATUS: PASS`. Targeted tests: `99 passed, 40 warnings`. Full pytest evidence: `1845 passed, 60 warnings`.
  - Implementation seam: `hedgehog/fractal_cell_integration.py` is a bounded integration adapter only. It composes `hedgehog/fractal_dag_executor.py`, `hedgehog/bounded_actor_contracts.py`, and existing PlanGraph / ResultProposal / Post V&V / GT boundaries without replacing RootOrchestrator, Architect, Executor, Post V&V, GTValidator, schemas, or model/network boundaries.
  - Post V&V fallback boundary fix: Post V&V fallback fails closed as review-required / needs-revision, not accepted authority. Reason codes: `post_vv_runtime_unavailable_review_required`, `post_vv_fallback_not_authority`, `child_output_requires_real_post_vv_or_root_review`, and `post_vv_fallback_used_review_required`. Counter: `post_vv_fallback_used_count: 3`.
  - Child target-boundary fix: `child_target_boundary_blocked` prevents child outputs from going directly to `final_output` or parent Architect command. Dangerous child transitions blocked include child Architect PlanGraph -> final_output, child Executor ResultProposal -> final_output, child Verifier VVReport -> final_output, child GTReport -> final_output, child GTReport -> parent Architect command, and child Root-like return -> user FinalOutput.
  - Key counters: `scenarios_total: 12`, `scenarios_passed: 12`, `cells_started_count: 4`, `child_actor_inputs_seen_count: 21`, `child_actor_outputs_emitted_count: 21`, `child_result_proposals_count: 5`, `child_validation_reports_count: 3`, `child_gt_reports_count: 3`, `parent_return_reports_count: 3`, `root_review_required_count: 12`, `post_vv_fallback_used_count: 3`, `final_output_created_count: 0`, `action_permission_granted_count: 0`, `child_root_claimed_count: 0`, `child_authority_claimed_count: 0`, `child_finaloutput_claimed_count: 0`, `child_action_permission_claimed_count: 0`, `child_actor_self_promotion_count: 0`, `parent_boundary_bypass_count: 0`, `post_vv_bypass_count: 0`, `gt_bypass_count: 0`, `parent_architect_commanded_count: 0`, `recursive_depth_limit_exceeded_count: 0`, `unbounded_child_spawn_count: 0`, `child_consensus_authority_claimed_count: 0`, `manifest_mutation_count: 0`, `transition_matrix_mutation_count: 0`, `network_used_count: 0`, `gemini_used_count: 0`, `connector_side_effect_count: 0`, and `root_final_authority_preserved_count: 12`.
  - Boundary conclusion: Fractal Cell is not Root; bounded actor contracts apply inside child cell; child ResultProposal is not FinalOutput; child cell output must return to parent / Post V&V / GT / Root boundary; child cell cannot command parent Architect; child consensus is not authority; and Root remains final authority.

- `auditor_human_fractal_cell_runtime_integration_walkthrough_v01.log`
  - Human Fractal Cell Runtime Integration walkthrough audit for commit `b6b53f8`; audit commit `1f1a196`; technical audit `643d6cd`; runtime commit `96755ba`; preflight `84303eb`; patch plan `9f49cbc`; previous checkpoint `09523bf`.
  - Audit status: PASS. Scope: human-readable walkthrough and focused tests. Walkthrough command exits 0. Focused tests: `5 passed, 2 warnings`.
  - Validation facts: underlying runtime status PASS, `walkthrough_required_counters_match: True`, runtime runner `FINAL STATUS: PASS`, targeted tests `99 passed, 40 warnings`, and full pytest evidence `1845 passed, 60 warnings`.
  - Confirms the walkthrough explains that a Fractal Cell is a bounded child execution container, not Root; bounded actor contracts apply inside child cell; child ResultProposal is not FinalOutput; child cell output must return to parent / Post V&V / GT / Root boundary; child cell cannot command parent Architect; recursive child depth is bounded; child consensus is not authority; and Root remains final authority.
  - Post V&V fallback boundary explanation: fallback is shape-compatible only and fails closed as review-required / needs-revision using `post_vv_runtime_unavailable_review_required`, `post_vv_fallback_not_authority`, `child_output_requires_real_post_vv_or_root_review`, and `post_vv_fallback_used_review_required`.
  - Child target-boundary explanation: `child_target_boundary_blocked` covers child Architect PlanGraph -> final_output, child Executor ResultProposal -> final_output, child Verifier VVReport -> final_output, child GTReport -> final_output, child GTReport -> parent Architect command, and child Root-like return -> user FinalOutput.
  - Key counters: `scenarios_total: 12`, `scenarios_passed: 12`, `cells_started_count: 4`, `child_actor_inputs_seen_count: 21`, `child_actor_outputs_emitted_count: 21`, `child_result_proposals_count: 5`, `child_validation_reports_count: 3`, `child_gt_reports_count: 3`, `parent_return_reports_count: 3`, `root_review_required_count: 12`, `post_vv_fallback_used_count: 3`, `final_output_created_count: 0`, `action_permission_granted_count: 0`, `child_root_claimed_count: 0`, `child_authority_claimed_count: 0`, `parent_boundary_bypass_count: 0`, `post_vv_bypass_count: 0`, `gt_bypass_count: 0`, `parent_architect_commanded_count: 0`, `network_used_count: 0`, `gemini_used_count: 0`, and `root_final_authority_preserved_count: 12`.
  - Boundary conclusion: the human walkthrough accurately explains that the bounded child execution container can host child actors and return child reports upward, but cannot become Root, create FinalOutput, grant action permission, bypass Post V&V / GT / Root, command parent Architect, or turn child consensus into authority.

- `auditor_human_real_semantic_runtime_thread_walkthrough_v01.log`
  - Human Real Semantic Runtime Thread Walkthrough v0.1 audit for commit `4fa59d7`; audit commit `3c21206`; previous docs checkpoint `bc7ec63`; runtime gate `1e1afe6`.
  - Audit status: PASS. Scope: human composite walkthrough and focused tests. Walkthrough command exits 0. Focused tests: `10 passed, 2 warnings`. Overclaim grep: no hits.
  - Invoked deterministic core layers: Real Local DRS Resolver / Writeback; CandidateVectorGenerator + Real AVF Scoring; AVF Candidate Advisory / GT-LGT Advisory; Bounded LLM/SLM Actors; Fractal Cell Runtime Integration.
  - Key counters: `walkthrough_required_counters_match: True`, `closed_layers_invoked_count: 5`, `closed_layers_status_pass_count: 5`, `combined_direct_reuse_allowed_count: 0`, `combined_action_permission_granted_count: 0`, `combined_final_output_created_by_non_root_count: 0`, `combined_authority_claimed_by_non_root_count: 0`, `combined_parent_boundary_bypass_count: 0`, `combined_post_vv_bypass_count: 0`, `combined_gt_bypass_count: 0`, `combined_network_used_count: 0`, `combined_gemini_used_count: 0`, `root_final_authority_preserved_across_thread: True`, `historical_closed_layers_listed_count: 36`, `optional_live_llm_evidence_paths_listed_count: 4`, `live_llm_authority_claimed_count: 0`, and `live_llm_final_output_created_count: 0`.
  - Historical catalog coverage: 36 closed / working historical layers are listed as evidence-only, including Enterprise Document Killer Demo B v0.1. The catalog does not imply one live object traverses every layer and does not create runtime authority.
  - Optional live LLM/Gemini handling: optional live Gemini Architect smoke, optional live Gemini Orchestrator smoke, ordered live Gemini Orchestrator Architect smoke, and live dual-Gemini full chain smoke are historical optional evidence, not default PASS dependencies.
  - Authority boundary conclusion: DRS record is not truth, DRS hit is not authority, Candidate vector is not truth, AVF score is not authority, GT-style advisory signal is not Root Final, actor output is not truth/authority/action permission/FinalOutput, Fractal Cell is not Root, child ResultProposal is not FinalOutput, Post V&V fallback fails closed, live LLM/Gemini output is not authority, and Root remains final authority.

- `auditor_real_semantic_runtime_thread_composite_smoke_v01.log`
  - Real Semantic Runtime Thread Composite Smoke v0.1 technical audit for commit `7736fe8`; audit commit `821675b`; previous docs checkpoint `90cf0d4`; runtime gate `1e1afe6`.
  - Audit status: PASS. Scope: composite smoke runner and focused tests. runner_result: FINAL STATUS: PASS. Focused test result: `8 passed, 2 warnings`. Overclaim grep: no hits.
  - Invoked runtime layers: Real Local DRS Resolver / Writeback; CandidateVectorGenerator + Real AVF Scoring; AVF Candidate Advisory / GT-LGT Advisory; Bounded LLM/SLM Actors; Fractal Cell Runtime Integration.
  - Scenario coverage: `drs_scenarios_total: 8`, `avf_scenarios_total: 9`, `advisory_scenarios_total: 10`, `bounded_actor_scenarios_total: 12`, `fractal_cell_scenarios_total: 12`, `composite_layers_total: 5`, `composite_layers_passed: 5`, `composite_scenarios_total: 51`, and `composite_required_scenarios_present: True`.
  - Machine smoke hardening: `composite_required_counter_keys_present: True`; `missing_required_counter_keys: {}`. The smoke fails closed if any critical underlying counter key is missing, preventing renamed/missing safety counters from silently defaulting to zero.
  - Key counters: `composite_required_counters_match: True`, `composite_direct_reuse_allowed_count: 0`, `composite_action_permission_granted_count: 0`, `composite_final_output_created_by_non_root_count: 0`, `composite_authority_claimed_by_non_root_count: 0`, `composite_truth_claimed_by_non_root_count: 0`, `composite_poisoning_or_spam_authority_claimed_count: 0`, `composite_high_score_or_advisory_forced_accept_count: 0`, `composite_silent_or_hidden_safety_failure_count: 0`, `composite_actor_escalation_or_raw_command_accept_count: 0`, `composite_root_boundary_bypass_count: 0`, `composite_child_boundary_violation_count: 0`, `composite_production_or_external_drs_used_count: 0`, `composite_network_used_count: 0`, `composite_gemini_used_count: 0`, `optional_live_llm_lane_default_enabled: False`, `optional_live_llm_core_pass_dependency: False`, and `root_final_authority_preserved_across_thread: True`.
  - Authority boundary conclusion: DRS record is not truth, DRS hit is not authority, Candidate vector is not truth, AVF score is not authority, GT-style advisory signal is not Root Final, actor output is not truth/authority/action permission/FinalOutput, Fractal Cell is not Root, child ResultProposal is not FinalOutput, Post V&V fallback fails closed, and Root remains final authority.

- `auditor_zero_trust_supplier_payment_wow_v01.log`
  - Zero Trust Supplier Payment WOW v0.1 technical audit for commit `87665d2`; audit_commit: 02b836f; patch plan `8509ab9`; preflight `fdc9abd`; previous docs checkpoint `5a1e0fe`; runtime gate `1e1afe6`.
  - audit_status: PASS. Scope: deterministic business-semantic sandbox runner. Runner: FINAL STATUS: PASS. targeted_test_result: 87 passed, 2 warnings.
  - Conclusion: business-semantic sandbox proof, not production integration. It reviews supplier payment / shipment release through deterministic local fake evidence, creates only a local mock receipt in the mock-approved scenario after Root review, and does not execute payment or release shipment.
  - Key counters: `scenarios_total: 10`, `scenarios_passed: 10`, `local_fake_evidence_records_count: 10`, `mock_approval_present_count: 1`, `mock_receipt_created_count: 1`, `real_payment_executed_count: 0`, `real_shipment_released_count: 0`, `real_supplier_api_called_count: 0`, `real_bank_api_called_count: 0`, `connector_side_effect_count: 0`, `secrets_accessed_count: 0`, `network_used_count: 0`, `gemini_used_count: 0`, `real_model_call_count: 0`, and `root_final_authority_preserved_count: 10`.
  - Authority boundary conclusion: warehouse stock evidence is not authority, invoice is not authority, DRS hit is not authority, stale DRS memory cannot authorize payment, AVF score is not authority, high AVF score cannot override legal hold, advisory report is not Root Final, bounded actor route cannot command bank or supplier, Fractal Cell is not Root, child branch report is not FinalOutput, mock approval is local sandbox signal only, mock receipt is not real payment, mock receipt is not real shipment release, and Root remains final authority.
  - Limitations: not production E2E, no real bank/supplier/warehouse integration, no network/Gemini/live model/connectors/secrets, and Real Semantic Runtime MVP is not complete.

- `auditor_live_llm_semantic_evidence_reader_v01.log`
  - Live LLM Semantic Evidence Reader / Extractor v0.1 technical audit for commit `2c7eaed`; audit commit `8750634`; patch plan `b626544`; preflight `42551c1`.
  - audit_status: PASS. Scope: deterministic fixture semantic evidence reader runtime. Runner: FINAL STATUS: PASS. Targeted pytest: `29 passed, 2 warnings`; warnings are existing jsonschema.RefResolver deprecations from the composite smoke dependency path.
  - Confirms `ReaderMode`, `SemanticEvidenceInput`, `SemanticEvidenceClaim`, `SemanticEvidenceReaderReport`, `build_semantic_evidence_claims`, `evaluate_semantic_evidence_inputs`, and `run_live_llm_semantic_evidence_reader_scenarios`.
  - Confirms `deterministic_fixture_reader` is the active default, `live_llm_reader` is default off, and explicit live mode fails closed with `ValueError("live_llm_reader is disabled in v0.1 deterministic runner")`.
  - Key counters: `scenarios_total: 10`, `scenarios_passed: 10`, `llm_inputs_seen_count: 11`, `semantic_claims_created_count: 11`, `uncertainty_notes_created_count: 11`, `contradiction_flags_created_count: 2`, `unsafe_instruction_flags_created_count: 6`, `root_review_required_count: 11`, `deterministic_fixture_reader_used_count: 1`, `live_llm_default_enabled_count: 0`, `live_llm_core_pass_dependency_count: 0`, `live_model_call_count: 0`, `network_used_count: 0`, `gemini_used_count: 0`, `secrets_accessed_count: 0`, `truth_claimed_count: 0`, `authority_claimed_count: 0`, `action_permission_claimed_count: 0`, `final_output_claimed_count: 0`, `connector_command_created_count: 0`, `payment_executed_count: 0`, `shipment_released_count: 0`, `prompt_injection_escalation_count: 0`, and `root_final_authority_preserved_count: 10`.
  - Authority boundary conclusion: LLM output is not truth, LLM output is not authority, LLM confidence is not authority, LLM extracted claim is not action permission, SemanticEvidenceClaim is candidate evidence only, SemanticEvidenceClaim is not FinalOutput, prompt injection cannot escalate authority, contradiction detection is review signal only, semantic claims return to a Root-shaped route, and Root remains final authority.

- `auditor_human_live_llm_semantic_evidence_reader_walkthrough_v01.log`
  - Human Live LLM Semantic Evidence Reader walkthrough audit for commit `e904b8d`; audit commit `7f0a21d`; technical audit `8750634`; runtime commit `2c7eaed`; patch plan `b626544`; preflight `42551c1`.
  - audit_status: PASS. Scope: human walkthrough for deterministic Live LLM Semantic Evidence Reader. Walkthrough runner: FINAL STATUS: PASS. Focused pytest: `22 passed`.
  - Confirms the walkthrough imports and calls the committed runtime scenario function, explains the returned facts, and does not add runtime capability or live model behavior.
  - Confirms `walkthrough_required_counters_match: True`, `scenarios_total: 10`, `scenarios_passed: 10`, `live_model_call_count: 0`, `network_used_count: 0`, `gemini_used_count: 0`, `secrets_accessed_count: 0`, and `root_final_authority_preserved_count: 10`.
  - Human explanation coverage: Live LLM is not active in this layer; this layer creates the bounded contract for future live LLM evidence reading; SemanticEvidenceClaim is not truth, authority, action permission, or FinalOutput; prompt injection text is evidence, not instruction; bank/supplier/warehouse examples are demo-domain stress cases; the construct is universal across dirty evidence domains; Root remains final authority; and Real Semantic Runtime MVP is not complete.

- `auditor_optional_live_llm_evidence_reader_smoke_v01.log`
  - Optional Live LLM Evidence Reader Smoke v0.1 technical audit for runtime commit `9e58dad`; preflight `f397190`; patch plan `e88657d`; audit commit `0695ace`.
  - audit_status: PASS. Scope: response-file optional smoke runtime. Runner default: FINAL STATUS: SKIPPED_CLOSED. Focused pytest: `33 passed`.
  - Confirms response-file optional smoke, no model/network/connector call by runner, no Gemini call, no secrets access, no payment or shipment action, and Root final authority preserved.
  - Confirms explicit response-file mode can validate exactly one SemanticEvidenceClaim-compatible candidate; invalid JSON, authority/action/FinalOutput/connector claims, unexpected fields, and secret-like keys and values fail closed.
  - Confirms `deterministic_fixture_reader` remains unchanged and ReaderMode.live_llm_reader remains fail-closed in the closed deterministic runtime.

- `auditor_human_optional_live_llm_evidence_reader_smoke_walkthrough_v01.log`
  - Human Optional Live LLM Evidence Reader Smoke walkthrough audit for commit `0b202f9`; audit commit `69cf748`; technical audit `0695ace`; runtime commit `9e58dad`; patch plan `e88657d`; preflight `f397190`.
  - audit_status: PASS. Scope: human walkthrough for response-file optional smoke runtime. Walkthrough runner: FINAL STATUS: PASS. Underlying runtime status: SKIPPED_CLOSED. Focused pytest: `29 passed`.
  - Confirms the walkthrough calls the committed optional smoke runtime, adds no capability, explains response-file mode only, command adapter absent/deferred, and no model/network/connector call by runner.
  - Confirms `walkthrough_required_counters_match: True`, `live_model_call_count: 0`, `network_used_count: 0`, `semantic_claim_created_count: 0`, `silent_fallback_to_deterministic_pass_count: 0`, `deterministic_reader_mutated_count: 0`, and `root_final_authority_preserved_count: 1`.
  - Human explanation coverage: SKIPPED_CLOSED is safe closure, not proof that a live provider call occurred; the default walkthrough does not execute a live provider read; the response-file artifact is untrusted input; SemanticEvidenceClaim is candidate evidence only; decision-like wording remains non-authoritative; ReaderMode.live_llm_reader remains fail-closed; and Root remains final authority.

- `auditor_live_provider_adapter_response_capture_v01.log`
  - Live Provider Adapter / Response Capture v0.1 technical audit for runtime commit `3c88ede`; audit commit `d405c45`; preflight `50922fb`; patch plan `9448f67`.
  - audit_status: PASS. Scope: controlled adapter + response capture boundary. Default runner: FINAL STATUS: SKIPPED_CLOSED. Focused pytest: `38 passed`.
  - Confirms explicit-only provider path, raw provider response artifact capture, response-file validation gate reuse, exactly one candidate-only SemanticEvidenceClaim for valid artifacts, and fail-closed handling for invalid/unsafe artifacts.
  - Confirms fake provider tests do not count live model/network/Gemini, real Gemini configured path counts env credential access without writing key to artifacts, ReaderMode.live_llm_reader remains disabled/fail-closed, arbitrary command adapter is not approved, and Root remains final authority.

- `auditor_human_live_provider_adapter_response_capture_walkthrough_v01.log`
  - Human Live Provider Adapter / Response Capture walkthrough audit for commit `87b484b`; audit commit `1b6f716`; technical audit `d405c45`; runtime commit `3c88ede`; patch plan `9448f67`; preflight `50922fb`.
  - audit_status: PASS. Scope: human walkthrough for the closed Live Provider Adapter / Response Capture runtime. Walkthrough runner: FINAL STATUS: PASS. Focused pytest: `22 passed`.
  - Confirms the walkthrough explains default SKIPPED_CLOSED behavior, fake-provider zero live model/network/Gemini counts, monkeypatched real-Gemini credential access without artifact leakage, response-file validation gate reuse, unsafe-output fail-closed behavior, and provider may read, but provider cannot decide.
  - Confirms the walkthrough adds no runtime capability, no provider/network/model call, no connector, no provider FinalOutput, and Root remains final authority.

## Current Applied Auditor Commands

```bash
.venv/bin/python -m demo.run_drs_adversarial_stress_pack
.venv/bin/python -m pytest tests/test_drs_adversarial_stress_pack_runner.py -q
.venv/bin/python -m demo.run_all_layers_applied_super_smoke
.venv/bin/python -m pytest tests/test_all_layers_applied_super_smoke_runner.py -q
.venv/bin/python -m demo.run_human_applied_auditor_walkthrough
.venv/bin/python -m pytest
```

Latest confirmed full-suite evidence: 1295 passed, 37 warnings. These commands
are for human audit and verification; the walkthrough is explanatory only and
does not create a proof or capability layer.

- Older ordered Gemini live reports
  - Historical fallback/safety evidence only, not final dual-live success proof.
  - These reports prove invalid live Orchestrator output is caught, does not reach Architect / Executor / Root final, falls back deterministically, and preserves Root boundaries.
  - Do not use fallback reports to claim dual-live success.

Rules:

- Do not store secrets, API keys, tokens, private credentials, or personal documents here.
- These files are for audit/history only.
- They must not be used as runtime memory or production input.
