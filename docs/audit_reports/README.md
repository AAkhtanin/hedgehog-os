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

- Older ordered Gemini live reports
  - Historical fallback/safety evidence only, not final dual-live success proof.
  - These reports prove invalid live Orchestrator output is caught, does not reach Architect / Executor / Root final, falls back deterministically, and preserves Root boundaries.
  - Do not use fallback reports to claim dual-live success.

Rules:

- Do not store secrets, API keys, tokens, private credentials, or personal documents here.
- These files are for audit/history only.
- They must not be used as runtime memory or production input.
