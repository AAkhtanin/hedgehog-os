# Audit Reports

This folder stores milestone audit logs for Hedgehog OS.

These reports are historical development artifacts, not runtime inputs.
They document proof checkpoints, test runs, auditor-facing traces, and architectural validation logs.

Current reports:

- `auditor_root_native_dag_drs_audit_report.log`
  - Root-native DAG path, DRS writeback, audit/provenance, sensitive-scan checkpoint.

- `auditor_large_graph_drs_lineage_report.log`
  - Large Graph / Bounded Fractal Stress and DRS Graph Proximity / Lineage checkpoint.

Rules:

- Do not store secrets, API keys, tokens, private credentials, or personal documents here.
- These files are for audit/history only.
- They must not be used as runtime memory or production input.
