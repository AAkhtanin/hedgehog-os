# Audit Reports

This folder stores milestone audit logs for Hedgehog OS.

These reports are historical development artifacts, not runtime inputs.
They document proof checkpoints, test runs, auditor-facing traces, and architectural validation logs.

Current reports:

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
  - Confirms completed/degraded/blocked/failed outcomes remain visible and raw output plus malicious FinalOutput, DRS write, Root bypass, and external-action claims are rejected.
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
  - Confirms live opt-in/network use with Gemini only as bounded child Executor, valid completed proof-task output, valid action-like request blocking, no fallback, and no API/tool call, real action, child FinalOutput, parent DRS write, Root bypass, or Post V&V / GT / Root bypass.

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

- Older ordered Gemini live reports
  - Historical fallback/safety evidence only, not final dual-live success proof.
  - These reports prove invalid live Orchestrator output is caught, does not reach Architect / Executor / Root final, falls back deterministically, and preserves Root boundaries.
  - Do not use fallback reports to claim dual-live success.

Rules:

- Do not store secrets, API keys, tokens, private credentials, or personal documents here.
- These files are for audit/history only.
- They must not be used as runtime memory or production input.
