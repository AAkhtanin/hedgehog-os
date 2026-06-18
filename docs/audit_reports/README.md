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
