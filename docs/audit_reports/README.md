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

- Older ordered Gemini live reports
  - Historical fallback/safety evidence only, not final dual-live success proof.
  - These reports prove invalid live Orchestrator output is caught, does not reach Architect / Executor / Root final, falls back deterministically, and preserves Root boundaries.
  - Do not use fallback reports to claim dual-live success.

Rules:

- Do not store secrets, API keys, tokens, private credentials, or personal documents here.
- These files are for audit/history only.
- They must not be used as runtime memory or production input.
