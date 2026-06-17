# Hedgehog OS MVP Invariants

These invariants are non-negotiable for the proof-of-architecture demo.

Document hierarchy:

- specs/human_passport_v0_25.md defines MVP architecture and invariants.
- specs/math_appendix_v0_3.md defines formulas and algorithmic details.
- docs/passport_geometry_root_needles.md defines Root-centered capability geometry.
- docs/strategic_expansion_map.md is vision-only and not an implementation sprint.
- If documents conflict for current MVP implementation, the Human Passport controls.

Root-centered capability geometry invariants:

- Pipeline trace is an observable projection, not the architecture. Root-centered capability geometry is the architecture.
- Canonical execution is the main downward Root-controlled runtime vector; it is not merely an ordinary needle.
- Needle is a directed bounded capability contract / semantic organ anchored in Root, not a plugin.
- A complex needle or child cell may hold bounded local authority but never becomes Root; authority does not automatically propagate upward, sideways, or outward.
- DRS is semantic topology / address / resonance / lineage / audit / trust / TTL / conflict / reuse / promotion fabric, not a memory database, vector store, or authority.
- Marennya is a deferred lateral reflective systemic needle-like direction; UP is a deferred upward transfer/opportunity systemic needle-like direction.
- Marennya / UP are proposal-only, quarantine-first, Root-approved, do not mutate Work, install needles, or create FinalOutput, and are not required for first applied semantic demos.
- Architecture must allow other future systemic reflective needles; Marennya / UP are not exhaustive.
- Orchestrator, Architect, Executor, child cells, needles, DRS, GT, ConflictCheck, Marennya, UP, and external DRS must never receive final authority.

1. Root-only FinalOutput
   - FinalOutput is created only by RootOrchestrator.
   - No executor, validator, architect, DRS component, Marennya hook, or UP hook may produce final user-facing output.

Final draft / Root authority invariant:

- RootOrchestrator is the only component allowed to create FinalOutput.
- Root is the final authority and commit wrapper, not necessarily the strongest prose generator.
- FinalRenderer or a future SynthesisExecutor may create FinalDraftProposal only.
- FinalDraftProposal is not FinalOutput.
- FinalDraftProposal must not write DRS records.
- FinalDraftProposal must not perform external actions.
- Root may use, reject, or rewrite a FinalDraftProposal before creating FinalOutput.
- FinalOutput.created_by must remain root_orchestrator.
- Renderer-created drafts must remain subordinate artifacts.

Observable Zero Trust Runtime proof:

- python -m demo.run_canonical_pipeline_trace is the main auditor-facing proof of the canonical runtime.
- The trace must show Root authority, explicit Orchestrator-stage / Route Assembly, allowed CandidateVector sources, AVF / HardMask / SoftMask before Architect, Root-created AttractorPacket, Architect input as AttractorPacket only, Architect output as PlanGraph, Fractal DAG Executor Core execution, ResultProposal-only Executor output, Post V&V before GT, GT selection without commit, artifact return to Root, Root-only FinalOutput, DRS writeback / audit, no real external actions, and no uncontrolled delegation.
- The DAG runner connects to the Root-controlled pipeline after Architect. It executes Architect PlanGraph and returns ResultProposals; it is not Root, does not own execution authority, and must not commit output.
- This is a demo-runtime proof, not production OS runtime. Production recursive child-cell execution, real external API/needle execution, and live Gemini/SLM Orchestrator defaults are not enabled here.

2. Executor contract
   - Executors return ResultProposal only.
   - Executors may simulate work, report evidence, and surface uncertainty, but they must not finalize.

3. Architect input contract
   - Architect receives AttractorPacket, not raw user text.
   - User/event text must pass through intent, world state, DRS retrieval, candidate generation, and AVF first.

4. Architect output contract
   - Architect returns PlanGraph and time_assumptions.
   - Architect does not return a user-facing answer.
   - Active AttractorPacket Architect instructions must use
     `must_return_plan_graph_only`.
   - Active Architect-facing contract must not tell Architect to return
     ResultProposal.
   - Executor / DAG ResultProposal contract remains downstream.
   - Root remains final authority.

Fractal DAG Executor invariant:

- Fractal DAG Executor runs after Architect returns PlanGraph.
- It computes ready sets, respects dependencies, parallelism, and budget limits.
- It may produce ResultProposal-shaped outputs and child boundary snapshots.
- It must not create FinalOutput.
- It must not perform global commit.
- Non-atomic nodes must return boundary artifacts, not uncontrolled recursion.
- The DAG runner is part of the Root-controlled pipeline, but it is not Root.
- Large or malformed PlanGraphs must be bounded or blocked rather than executed as uncontrolled flat graphs.
- Large Graph / Bounded Fractal Stress v0.1 demonstrates max_nodes, max_edges, max_depth, max_parallelism, cycle detection, unknown dependency detection, child boundary snapshots, and bounded GT candidate summaries.
- That stress runner proves a GT boundary / bounded summary check only: gt_runtime_called = false, gt_boundary_mode = bounded_summary_check, and raw large graphs are not sent to GT.

Executor / DAG ResultProposal boundary:

- Executor receives validated PlanGraph node(s).
- Executor returns ResultProposal only.
- Active Executor output must be schema-valid ResultProposal.
- Executor does not create FinalOutput.
- Executor does not write DRS directly.
- Executor does not bypass Post V&V / GT / Root.
- Executor does not execute real external actions unless a later explicit
  production/action layer authorizes that capability.
- Fractal DAG consumes valid PlanGraph / DAG node structure.
- Fractal DAG returns ResultProposal-shaped boundary artifacts.
- Atomic node outputs and child boundary snapshots are not Root Final.
- Child cell / node outputs must remain internal or boundary artifacts until
  wrapped into the parent ResultProposal path.
- ResultProposal-shaped != FinalOutput.
- ResultProposal-shaped != authority.
- ResultProposal-shaped != accepted evidence.
- ResultProposal-shaped != action authorization.
- ResultProposal-shaped != DRS writeback.
- ResultProposal-shaped boundary artifacts must flow through
  Post V&V / GT / Root before any final answer or writeback.
- Root remains final authority.

5. DRS time requirement
   - Every DRSRecord requires TimeEnvelope.
   - A DRS record without TimeEnvelope is invalid.

6. DRS retrieval time requirement
   - Every DRS retrieval requires TemporalQuery.
   - Retrieval must be explicit about as_of, range, freshness bias, and maximum age policy.

DRS registry invariant:

- DRS is a registry/resolver/index, not a raw memory dump.
- MVP LocalDRS may store inline content only as a local simplification.
- Future DRS records should prefer pointer and summary metadata over raw payload.
- Secrets, credentials, passport data, card data, tokens, passwords, and private keys must not be stored directly in DRSRecord.content.
- Sensitive data must be referenced through secure vault/storage pointers with explicit access policy.
- Future production versions should use a Credential Vault / sealed secret slot model.
- DRS may store secret references, scopes, provenance, permission rules, access policies, and audit metadata, but not raw secret values.
- LLM/SLM components may reason over the existence, type, scope, and permission state of a sealed slot without seeing the secret itself.
- Every DRSRecord still requires TimeEnvelope.
- Every retrieval still requires TemporalQuery.
- Work, Thoughts, UP, DeadEnds, and Quarantine layer separation remains mandatory.

DRS graph proximity / lineage invariant:

- MVP DRS graph proximity is LocalDRS-only and read-only.
- Records may store lineage/source links, but they must not store static hops_ago, hop_distance, or graph_distance.
- graph_distance is computed at query time from record links.
- graph_proximity = 2 ** (-distance / hop_half_life).
- GraphProximity is a retrieval/ranking signal only.
- GraphProximity must not override TimeEnvelope, GTTrust, policy, validation, or ReuseGate.
- Nearby DeadEnds may be warning signals, not direct-reuse candidates.
- Nearby Quarantine records may be quarantine signals, not direct-reuse candidates.
- External DRS, global DRS, and Internet of Meaning remain future pointer/protocol boundaries, not current implementation.

Chaos Survival Showcase invariant:

- Chaos Survival Showcase is an auditor-facing evidence aggregator over existing deterministic proof modules, not a new core runtime layer.
- Its PASS/FAIL summary must be derived from computed section predicates.
- It must not claim production autonomy, global DRS, external DRS, production 10k-node execution, production retrieval, live Gemini, Telegram actions, or real external actions.
- It may summarize NeedleRuntime Chaos, Canonical Needle Outcome Trace, Needle Outcome DRS Routing Persistence, Large Graph / Bounded Fractal Stress, and DRS Graph Proximity / Lineage.
- It must preserve Root final authority, Executor/needle no-FinalOutput, GT no-commit, unsafe reuse candidates = 0, and bad outcomes written to successful Work = 0.

Compute Collapse via DRS Reuse invariant:

- Compute Collapse via DRS Reuse is an auditor-facing evidence aggregator, not a new core runtime layer.
- It may demonstrate cold_start_full_pipeline, memory_context_only, eligible_direct_reuse, and unsafe_records_not_reused.
- Context memory is not direct reuse.
- Direct reuse requires eligible Work and explicit Root gate.
- Direct reuse must not bypass Root and must not use Quarantine, DeadEnds, failed, blocked, or degraded records.
- Architect / Executor / DAG skipping is allowed only in the eligible direct reuse scenario.
- Compute units are illustrative deterministic units derived from route flags, not real token billing.
- The proof must not claim absolute zero cost, real token savings proven, production billing benchmark, production autonomy, live Gemini, Telegram actions, global DRS, external DRS, or real external actions.

DRS layer taxonomy invariant:

- DRS Layer Taxonomy v0.1 is an engineering hardening layer, not a showcase.
- It is a LocalDRS taxonomy/reporting semantics layer.
- It does not perform a schema refactor, change ReuseGate behavior, implement global/external DRS, or make unsafe records reusable.
- The MVP DeadEnds layer remains physically broad in v0.1, but routing/report/content semantics must distinguish dead_end, blocked_trace, degraded_trace, and needs_user_trace.
- work_candidate / successful_work is the only direct-reuse eligible case in the current demo.
- quarantine covers invalid_json, schema_validation_failed, and unknown_exception / failed payloads; it is not Work and not direct-reuse eligible.
- dead_end means stable bad route / do not repeat without changing contract or path.
- blocked_trace means blocked by guard, policy, permission boundary, circuit breaker, or runtime safety boundary.
- degraded_trace means timeout, temporary degradation, partial failure, or service instability; it is not successful Work.
- needs_user_trace means confirmation, permission, or missing human input required; it is not completed action.
- Taxonomy does not override policy. Direct reuse policy remains unchanged, unsafe_direct_reuse_candidates must remain 0, local_drs_only remains true, external/global DRS are not implemented, and schema_refactor_performed remains false.
- taxonomy_does_not_override_policy, broad_deadends_semantics_clarified, direct_reuse_policy_unchanged, and PASS status must be derived from classified rows, not hardcoded.

Typed DRS lineage edges invariant:

- Typed DRS Lineage Edges v0.1 is an engineering hardening layer, not a showcase.
- It is a LocalDRS-only typed-edge proof.
- It does not perform a schema refactor, change ReuseGate behavior, implement ReuseScore, implement ConflictCheck, implement global/external DRS, or make unsafe records reusable.
- After DRS Layer Taxonomy clarifies what kind of records exist, typed edges clarify what kind of relationships exist between records.
- Required edge classes are derived_from, same_trace, warns_against, blocked_by_policy, requires_user, degraded_from, supports, and contradicts.
- Typed edge interpretation is computed at query time. Records must not store static hops_ago, hop_distance, or graph_distance as persisted truth.
- supports may contribute positive evidence, but cannot make a target directly reusable by itself.
- derived_from may contribute lineage evidence, but does not override policy.
- warns_against is warning evidence, not positive reuse evidence.
- blocked_by_policy is blocking evidence, not success.
- requires_user is needs-user evidence, not completed action.
- degraded_from is degradation evidence, not stable success.
- contradicts is contradiction evidence, but does not auto-block the target in v0.1.
- Contradiction source records must not be reused; contradiction targets require future ConflictCheck / ReuseScore handling.
- typed_edges_are_signals_only must remain true for v0.1.
- direct reuse policy remains unchanged, ReuseScore_implemented = false, conflict_check_implemented = false, local_drs_only = true, external/global DRS are not implemented, and schema_refactor_performed = false.

ReuseScore invariant:

- ReuseScore v0.1 is an engineering hardening layer.
- It is a LocalDRS-only advisory/ranking proof that consumes Typed DRS Lineage Edges candidates.
- It computes deterministic illustrative reuse scores from visible components: quality, freshness, gt_trust, semantic_similarity, graph_proximity, typed_positive_signal, warning_penalty, blocking_penalty, needs_user_penalty, degraded_penalty, contradiction_penalty, and risk_penalty.
- Raw score calculation and policy gates must remain separate.
- ReuseScore does not change ReuseGate behavior, bypass Root, implement production ConflictCheck, implement global/external DRS, make unsafe records reusable, claim real token billing, or claim production autonomy.
- ReuseScore is not Root, not ReuseGate, and not policy override.
- High score cannot override policy.
- Direct reuse still requires eligible successful Work.
- Context memory does not equal direct reuse.
- Quarantine, dead_end, blocked_trace, degraded_trace, and needs_user_trace records are not direct-reuse candidates.
- Contradiction does not auto-reuse; contradiction-risk candidates route to needs_conflict_check until future ConflictCheck exists.
- Root authority and ReuseGate authority remain preserved.
- Important proof examples: a high-ish scoring unsafe blocked_trace remains not reusable because policy_allowed is false; a work_candidate with contradiction_penalty becomes needs_conflict_check rather than direct_reuse; unsafe_direct_reuse_candidates remains 0.
- The current DRS semantic stack through this layer is DRS Graph Proximity / Lineage v0.1, DRS Layer Taxonomy v0.1, Typed DRS Lineage Edges v0.1, and ReuseScore v0.1.

Semantic Reuse Pipeline Integration invariant:

- Semantic Reuse Pipeline Integration v0.1 is an engineering integration proof.
- It is a bounded LocalDRS semantic reuse integration proof, not production RootOrchestrator integration.
- It connects LocalDRS retrieval -> taxonomy-aware filtering -> typed edge interpretation -> graph proximity -> ReuseScore -> ReuseGate / Root boundary -> direct reuse candidate or full pipeline fallback.
- It is not production autonomy, global DRS, external DRS, a ReuseGate replacement, a Root bypass, direct reuse execution, FinalOutput creation, real external action, live Gemini, or Telegram action.
- It must structurally consume collect_reuse_score() and preserve the source Typed DRS Lineage Edges report.
- All six pipeline stages must be represented: local_drs_retrieval, taxonomy_filtering, typed_edge_interpretation, graph_proximity, reuse_score, and reuse_gate_root_boundary.
- Scenario rows must separate recommendations from authority: eligible direct reuse may be recommended but not committed by the pipeline; context memory does not equal direct reuse; contradiction routes to needs_conflict_check; high score does not override policy; quarantine, needs_user, degraded, and dead_end records are not reused.
- semantic_pipeline_committed_final_output must be false.
- semantic_pipeline_bypassed_root must be false.
- semantic_pipeline_bypassed_reuse_gate must be false.
- root_boundary_preserved and reuse_gate_boundary_preserved must remain true.
- unsafe_reuse_candidates must remain 0.
- PASS must be derived from stages, scenarios, and boundary facts, not hardcoded.
- Root-controlled Semantic Reuse Decision Trace v0.1 is a deterministic Root-controlled dry-run proof. It consumes Semantic Reuse Pipeline recommendations, does not change production RootOrchestrator behavior, does not execute direct reuse, does not create production FinalOutput, does not write production Work records, and does not grant authority to the semantic pipeline.
- Root decision mapping must remain explicit: direct_reuse_candidate -> root_accepts_direct_reuse_candidate_for_gate_review; needs_full_pipeline -> root_selects_full_pipeline_fallback; needs_conflict_check -> root_requires_conflict_check; blocked -> root_blocks_policy_blocked_route; quarantine -> root_routes_to_quarantine; needs_user -> root_requires_user_input; degraded -> root_marks_degraded_trace; dead_end -> root_rejects_dead_end.
- Root-controlled Semantic Reuse Gate Trace v0.1 is a deterministic Root/ReuseGate dry-run proof. It consumes the Root decision trace and performs gate review only for the Root-approved direct reuse candidate.
- Non-direct-reuse routes must remain non-gate routes: full pipeline fallback, conflict check required, policy blocked, quarantine, needs_user, degraded, and dead_end.
- gate_review_accepts_candidate_for_root_final_decision means the candidate returns upward to Root. It is not production execution.
- ReuseGate must not create FinalOutput or execute direct reuse; semantic pipeline must not commit; Root remains final authority.
- Gate trace safety flags must preserve gate_reviews_performed = 1, gate_approvals_for_root_final_decision = 1, non_applicable_gate_routes = 7, root_final_decision_required_for_gate_approval = true, gate_did_not_commit_final_output = true, gate_did_not_execute_direct_reuse = true, direct_reuse_executed_in_trace = false, production_final_output_created = false, unsafe_reuse_candidates = 0, root_authority_preserved = true, reuse_gate_boundary_preserved = true, semantic_pipeline_authority_granted = false, local_drs_only = true, external/global DRS not implemented, and production_autonomy_claimed = false.
- Root-controlled Semantic Reuse Final Decision Trace v0.1 is a deterministic Root-controlled dry-run proof. It consumes the Root Semantic Reuse Gate Trace, does not change production RootOrchestrator behavior, does not execute production direct reuse, does not create production FinalOutput, does not perform real external actions, does not write production Work records, and does not grant authority to the semantic pipeline or ReuseGate.
- Root Final Decision Trace may create only a trace-level Root final decision artifact. That artifact is not production FinalOutput.
- Final decision mapping must remain explicit: gate_review_accepts_candidate_for_root_final_decision -> root_final_accepts_controlled_direct_reuse_trace; gate_not_applicable_full_pipeline_fallback -> root_final_selects_full_pipeline_fallback; gate_not_applicable_conflict_check_required -> root_final_requires_conflict_check; gate_not_applicable_policy_blocked -> root_final_blocks_policy_route; gate_not_applicable_quarantine -> root_final_routes_to_quarantine; gate_not_applicable_needs_user -> root_final_requires_user_input; gate_not_applicable_degraded -> root_final_marks_degraded_trace; gate_not_applicable_dead_end -> root_final_rejects_dead_end.
- Final Decision Trace safety flags must preserve trace_final_decision_artifacts_created = 1, trace_artifacts_created_only_by_root = true, controlled_direct_reuse_trace_accepts = 1, production_direct_reuse_executed = false, production_final_output_created = false, production_action_executed = false, production_work_record_written = false, semantic_pipeline_authority_granted = false, reuse_gate_authority_granted = false, unsafe_reuse_candidates = 0, root_authority_preserved = true, reuse_gate_boundary_preserved = true, local_drs_only = true, external/global DRS not implemented, and production_autonomy_claimed = false.
- root_final_accepts_controlled_direct_reuse_trace is still trace/dry-run, not production direct reuse execution.
- The current semantic reuse authority chain is complete in dry-run form: Semantic Reuse Pipeline recommends -> Root Decision Trace maps recommendations -> ReuseGate Trace reviews direct reuse candidate only -> approved candidate returns upward to Root -> Root Final Decision Trace makes final dry-run decision -> no production execution yet.
- Root-native Semantic Reuse E2E Trace v0.1 is complete. It is the first deterministic end-to-end semantic reuse trace and consumes the Semantic Reuse Authority Stack Audit.
- The E2E path is input task -> TemporalQuery -> LocalDRS retrieval -> taxonomy-aware filtering -> typed edge interpretation -> graph proximity -> ReuseScore -> semantic reuse recommendation -> Root decision -> ReuseGate review -> Root final dry-run decision -> trace-level final answer artifact -> audit visibility.
- The selected E2E scenario must remain eligible_direct_reuse_candidate with direct_reuse_candidate -> root_accepts_direct_reuse_candidate_for_gate_review -> gate_review_accepts_candidate_for_root_final_decision -> root_final_accepts_controlled_direct_reuse_trace, artifact_kind = trace_level_final_answer_artifact, created_by = root_orchestrator, production_final_output = false, production_action_executed = false, and production_work_record_written = false.
- E2E safety invariants: semantic pipeline recommends only, ReuseScore is advisory, Root decides, ReuseGate guards, Root final trace decides, trace artifact is not production FinalOutput, controlled direct reuse trace accept is not production direct reuse execution, context memory is not direct reuse, high score does not override policy, contradiction does not auto-reuse, unsafe reuse candidates remain zero, LocalDRS is local-only, external/global DRS are not implemented, and production autonomy is not claimed.
- Root-native Full Canonical E2E Trace v0.1 is complete. It is a deterministic full canonical E2E proof that composes first-run canonical Root-controlled execution with second-run semantic reuse authority.
- First-run path invariants: input task -> Root intake / Orchestrator boundary -> Architect / PlanGraph -> AVF / Attractor formation -> DAG / Executor -> ResultProposals -> Post V&V -> GT -> Root trace artifact -> LocalDRS writeback / audit visibility. root_authority_preserved_first_run = true, architect_does_not_answer_user = true, executor_does_not_create_final_output = true, gt_does_not_create_final_output = true, first_run_created_root_trace_artifact = true, first_run_local_drs_writeback_visible = true, first_run_local_work_record_written_in_proof = true, and production_external_action_executed = false.
- Second-run path invariants: repeat/similar task -> TemporalQuery -> LocalDRS retrieval -> taxonomy / typed edges / graph proximity -> ReuseScore -> Semantic Pipeline recommendation -> Root decision -> ReuseGate review -> Root final dry-run decision -> trace-level semantic reuse answer artifact. second_run_stages_passed = 12, selected_scenario = eligible_direct_reuse_candidate, semantic_reuse_path_used = true, second_run_root_authority_preserved = true, reuse_gate_boundary_preserved = true, semantic_pipeline_recommends_only = true, and reuse_score_advisory_only = true.
- Bridge honesty invariants: bridge_mode = deterministic_proof_linkage, deterministic_bridge_between_runs = true, production_persistence_claimed = false, production_reuse_claimed = false, and production_reuse_not_executed = true. Local proof DRS writeback may be visible, but production persistence and production reuse are not claimed.
- Full Canonical E2E safety flags must preserve production_direct_reuse_executed = false, production_final_output_created = false, production_work_record_written = false, production_external_action_executed = false, no_real_external_actions = true, no_live_gemini = true, no_telegram_actions = true, no_global_drs = true, no_external_drs_network = true, and production_autonomy_claimed = false.
- Optional Live Gemini Architect Smoke v0.1 is complete. It is an opt-in role-substitution smoke proof inside the Full Canonical E2E boundary.
- Gemini may substitute only the Architect proposal role. It must not become Root, Orchestrator, Executor, GT, or FinalRenderer; create FinalOutput; write DRS; execute actions; or bypass AVF, PlanGraph contract, Executor, Post V&V, GT, Root, ReuseGate, policy, or permission gates.
- Default mode must remain `dry_run_default`, deterministic, network-free, and must not call live Gemini. It uses `architect_artifact_source = deterministic_mock` and preserves `plan_graph_contract_checked = true`.
- Live mode must remain opt-in through explicit `--live`, `HEDGEHOG_ALLOW_LIVE_GEMINI = 1`, and Gemini configuration. Missing live configuration must report SKIPPED, not crash. Invalid live artifacts must be caught, contained, kept away from Executor and Root final output, and fall back visibly to deterministic Architect.
- Architect smoke boundary checks must derive from the Full Canonical E2E source report, role substitution flags, artifact containment, and context facts. Rendered output must not print credential environment names or secret terms.
- Architect smoke proof status: focused tests passed = 212, full suite passed = 788, sensitive scan found no secret terms, default dry-run status = PASS, and ready_for_future_orchestrator_live_smoke = true.
- Ordered Live Gemini Orchestrator-to-Architect Smoke v0.1 is complete. It proves an opt-in ordered role-substitution path: Root boundary -> live Gemini Orchestrator proposal -> schema-backed local validation -> live Gemini Architect proposal -> Architect contract check -> no production execution.
- Final success evidence is `docs/audit_reports/auditor_live_gemini_ordered_orchestrator_architect_25_success_report.log`. It proves orchestrator_initial_attempt_valid = true, orchestrator_active_proposal_source = live_gemini, orchestrator_active_proposal_is_fallback = false, temporal_query_required_value = true, downstream_actors_missing = [], downstream_actors_extra = [], architect_artifact_source = live_gemini, architect_artifact_valid = true, production_final_output_created = false, and production_external_action_executed = false.
- Gemini did not receive Root authority, write DRS, execute actions, create FinalOutput, activate Marennya / UP, or perform Telegram / external action. Historical fallback reports are safety evidence only and must not be used as proof of dual-live success.
- Controlled Orchestrator Matrix Gate v0.1 is complete. It is deterministic proof only: Orchestrator matrix is an input artifact, not authority; Root creates RootMatrixGateDecision artifacts and may accept, reject, or downgrade.
- Gate decisions preserve these meanings: accept means a valid matrix may become future AVF input; reject means unsafe/invalid matrix cannot continue; downgrade means a partially usable matrix may continue only with unsafe or incomplete claims removed.
- Verified gate scenarios must remain covered: valid_matrix_accept accepted; missing_temporal_query_reject rejected; incomplete_guards_downgrade_or_reject downgraded with missing guards listed; wrong_downstream_actors_reject rejected with missing/extra actor diagnostics; forbidden_bypass_reject rejected; high_confidence_policy_block rejected because policy beats Orchestrator confidence; fallback_route_visible keeps fallback visible but not executed.
- Gate evidence is `docs/audit_reports/auditor_controlled_orchestrator_matrix_gate_report.log`. The gate runner verifies the final ordered Gemini 2.5 success report before using it as live-role context: success_report_exists = true, success_report_verified = true, success_report_missing_markers = [], and ordered_live_context_mode = success_report_verified.
- Gate boundary invariants: AVF is not invoked, AttractorPacket is not created, Architect / Executor / Post V&V / GT are not reached in this layer, Orchestrator does not write DRS or create FinalOutput, production FinalOutput and external action are false, global/external DRS are not implemented, and Marennya / UP are not invoked.
- AVF / Attractor Formation from accepted Matrix v0.1 is complete. It consumes Controlled Orchestrator Matrix Gate v0.1 without hardcoding Matrix Gate PASS and forms AttractorPacket-like artifacts only from accepted or downgraded RootMatrixGateDecision outputs.
- AVF formation invariants: rejected matrices must not reach AVF, rejected matrices create no AttractorPacket, AVF remains independent, Orchestrator hints are hints and not commands, HardMask beats Orchestrator confidence, policy beats Orchestrator confidence, and Root may downgrade or override matrix claims.
- Verified AVF cases must remain covered: valid_matrix_accept forms an AttractorPacket-like artifact; incomplete_guards_downgrade_or_reject forms a limited artifact with downgraded claims visible; missing_temporal_query_reject, high_confidence_policy_block, forbidden_bypass_reject, and wrong_downstream_actors_reject are blocked before AVF. rejected_matrix_packets = 0 and rejected_matrices_blocked_before_avf = true.
- AVF boundary invariants: Architect is not invoked in this layer, Executor is not invoked, AVF does not create FinalOutput, write DRS, or execute actions, Orchestrator does not write DRS, production FinalOutput/external action are false, global/external DRS are not implemented, and Marennya / UP are not invoked.
- AVF evidence is `docs/audit_reports/auditor_avf_attractor_from_accepted_matrix_report.log`.
- Architect from bounded AttractorPacket v0.1 is complete. It consumes AVF / Attractor Formation from accepted Matrix v0.1 without hardcoding AVF PASS.
- Architect input invariants: Architect receives only bounded AVF output, not raw Orchestrator matrix, raw unchecked user intent, rejected matrix, or invalid/unbounded AttractorPacket.
- Verified Architect cases must remain covered: accepted bounded AttractorPacket creates a valid PlanGraph proposal; downgraded bounded AttractorPacket creates a limited valid PlanGraph proposal; rejected matrix, raw Orchestrator matrix, raw unchecked user intent, and invalid/unbounded AttractorPacket are blocked; invalid Architect artifact is contained.
- Architect boundary invariants: PlanGraph contract is checked, invalid Architect artifact does not reach Executor, create FinalOutput, or write DRS, Executor / Post V&V / GT are not invoked, production FinalOutput/external action are false, global/external DRS are not implemented, and Marennya / UP are not invoked.
- Architect evidence is `docs/audit_reports/auditor_architect_from_bounded_attractor_packet_report.log`.
- DAG / Executor from valid PlanGraph v0.1 is complete. It consumes Architect from bounded AttractorPacket v0.1 without hardcoding Architect PASS.
- Executor input invariants: Executor receives only validated PlanGraph nodes, not invalid Architect artifact, raw Architect text, raw Orchestrator matrix, raw user intent, or unvalidated PlanGraph.
- Verified Executor cases must remain covered: accepted valid PlanGraph creates ResultProposal; downgraded valid PlanGraph creates limited/degraded ResultProposal; invalid Architect artifact, raw Architect text, raw Orchestrator matrix, raw user intent, and unvalidated PlanGraph are blocked before Executor.
- Executor boundary invariants: ResultProposal only, no FinalOutput, no direct DRS write, no real external action, Post V&V not invoked, GT not invoked, production FinalOutput/external action false, global/external DRS not implemented, and Marennya / UP not invoked.
- DAG / Executor evidence is `docs/audit_reports/auditor_dag_executor_from_valid_plan_graph_report.log`.
- Post V&V from ResultProposal v0.1 is complete. It consumes DAG / Executor from valid PlanGraph v0.1 without hardcoding DAG / Executor PASS.
- Post V&V input invariants: Post V&V receives only ResultProposal artifacts, not raw Executor text, raw Architect PlanGraph, raw Orchestrator matrix, raw user intent, real action output, malformed ResultProposal shapes, or malicious ResultProposal claims.
- Verified Post V&V cases must remain covered: completed ResultProposal creates accepted ValidationReport; degraded ResultProposal creates degraded ValidationReport; raw upstream inputs are blocked; malicious FinalOutput and DRS write claims are rejected; malformed ResultProposal is rejected.
- Post V&V boundary invariants: ValidationReport / V&VReport only, no FinalOutput, no direct DRS write, no action execution, GT not invoked, Root Final not invoked, production FinalOutput/external action false, global/external DRS not implemented, and Marennya / UP not invoked.
- Post V&V evidence is `docs/audit_reports/auditor_post_vv_from_result_proposal_report.log`.
- GT from ValidationReport v0.1 is complete. It consumes Post V&V from ResultProposal v0.1 without hardcoding Post V&V PASS.
- GT input invariants: GT receives only ValidationReport / V&VReport artifacts, not raw ResultProposal, raw Executor text, raw Architect PlanGraph, raw Orchestrator matrix, raw user intent, real action output, malformed ValidationReport shapes, or malicious ValidationReport claims.
- Verified GT cases must remain covered: accepted ValidationReport creates accept GTDecision; degraded ValidationReport creates degrade GTDecision; rejected ValidationReport creates reject GTDecision; raw upstream inputs are blocked; malicious FinalOutput, DRS write, and action execution claims are rejected; malformed ValidationReport is rejected.
- GT boundary invariants: GTDecision / selection artifact only, no FinalOutput, no direct DRS write, no action execution, Root Final not invoked, production FinalOutput/external action false, global/external DRS not implemented, and Marennya / UP not invoked.
- GT evidence is `docs/audit_reports/auditor_gt_from_validation_report.log`.
- Root Final from GTDecision v0.1 is complete. It consumes GT from ValidationReport v0.1 without hardcoding GT PASS.
- Root Final input invariants: Root Final receives only GTDecision / selection artifacts, not raw ValidationReport, raw ResultProposal, raw Executor text, raw Architect PlanGraph, raw Orchestrator matrix, raw user intent, real action output, malformed GTDecision shapes, or malicious GTDecision claims.
- Verified Root Final cases must remain covered: accept GTDecision creates accepted RootFinalArtifact; degrade GTDecision creates degraded RootFinalArtifact; reject GTDecision creates rejected RootFinalArtifact; raw upstream inputs are blocked; malicious GT FinalOutput, DRS write, and action execution claims are rejected; malformed GTDecision is rejected.
- Root Final boundary invariants: Root is the only FinalOutput authority, GT does not create FinalOutput, Root does not write DRS in this layer, DRS writeback is not invoked, Root does not execute actions, production persistence is not claimed, production external action is false, global/external DRS are not implemented, and Marennya / UP are not invoked.
- Root Final evidence is `docs/audit_reports/auditor_root_final_from_gt_decision.log`.
- DRS Writeback / Audit from Root Final v0.1 is complete. It actually consumes `collect_root_final_from_gt_decision()` and does not hardcode Root Final PASS.
- DRS writeback input invariant: only valid RootFinalArtifact may enter. Raw GTDecision, ValidationReport, ResultProposal, Architect PlanGraph, Orchestrator matrix, user intent, and real action output are blocked; malformed artifacts and malicious global/external DRS, production persistence, Root DRS write, and action claims are rejected.
- DRS writeback boundary invariant: records are `local_audit_only`; DRS is not authority, full memory, or a vector store; Root remains commit authority. Production persistence, global/external DRS, direct reuse, Telegram, real actions, and Marennya / UP activation remain out of scope.
- DRS writeback proof status: PASS, scenarios_verified=16, records_created=3, accepted/degraded/rejected=1/1/1, focused tests passed=98, full suite passed=1037, sensitive scan clear. Evidence: `docs/audit_reports/auditor_drs_writeback_from_root_final.log`.
- Root-native sandbox NeedleRuntime E2E v0.1 is complete. It sources a validated PlanGraph node and permits only Root-approved bounded sandbox/mock capability execution.
- NeedleRuntime invariants: NeedleRuntime is not authority; NeedleExecutionResult is evidence, not final truth; NeedleRuntime creates no FinalOutput, writes no DRS, executes no real external action, and bypasses neither Root, policy, permission, Post V&V / GT / Root Final, nor audit.
- Needle outcome invariant: completed, degraded, blocked, failed, timeout, invalid_json, contract_mismatch, permission_required, forbidden_external_action, quarantine, circuit-breaker, safe-for-GT, and crash-containment facts remain visible downstream.
- Sandbox NeedleRuntime proof status: PASS, scenarios_verified=11, malicious_claims_rejected=4, focused tests passed=70, full suite passed=1057, sensitive scan clear. Evidence: `docs/audit_reports/auditor_root_native_sandbox_needleruntime_e2e.log`.
- Fractal Cell Runtime v0.1 is complete. It proves atomic node -> ordinary Executor, needle-bound node -> sandbox NeedleRuntime, and non-atomic node -> bounded child fractal cell returning ChildBoundarySnapshot upward.
- Child-cell invariant: child cell and child Orchestrator are not Root; child output is boundary evidence, not final truth; completed, degraded, blocked, and failed outcomes remain visible; recursion and execution are bounded by max depth and budget.
- Child-cell authority invariant: no child FinalOutput, parent DRS write, real external action, live child LLM/SLM, or automatic parent DRS promotion is allowed. Parent promotion remains Root-authorized.
- ChildBoundarySnapshot is addressable experience, not an installed needle. Successful child traces do not automatically create needles; future promotion remains lifecycle and Root-policy work.
- Fractal Cell Runtime proof status: PASS, scenarios_verified=12, completed/degraded/blocked_or_failed=1/1/2, malicious_child_claims_rejected=5, focused tests passed=56, full suite passed=1069, sensitive scan clear. Evidence: `docs/audit_reports/auditor_fractal_cell_runtime.log`.
- Live Child Executor in Fractal Cell v0.1 is complete. Opt-in live Gemini may substitute only one child Executor role inside a bounded child cell and receives an Architect-provided node contract, never a free instruction.
- Live child result invariant: Gemini returns only ChildExecutionResult JSON/evidence; ChildExecutionResult becomes ChildBoundarySnapshot evidence and must pass through parent adapter, Post V&V, GT, and Root. It is not FinalOutput, DRS writeback, a needle, a protocol template, or production action execution.
- Live child authority invariant: child Executor is not Root, child Orchestrator, or child Architect; action-like requests are blocked/rejected/permission-required/sandbox-only; no API/tool calls, real actions, child FinalOutput, parent DRS write, Root bypass, or Post V&V / GT / Root bypass is allowed.
- Live child proof status: PASS, live opt-in/network used, completed proof task accepted, action-like request blocked and rejected through Root, malicious_claims_rejected=6, focused deterministic tests passed=36, full suite passed=1082, sensitive scan clear. Evidence: `docs/audit_reports/auditor_live_child_executor_in_fractal_cell_deterministic.log` and `docs/audit_reports/auditor_live_child_executor_in_fractal_cell_LIVE.log`.
- DRS Lifecycle Semantics v0.2 is complete. It consumes current proof collectors and creates local/proof-level, pointer-first ExperienceRecord objects for Root Final audit, sandbox NeedleRuntime, child-cell boundary, live child Executor, blocked-action, and synthetic promotion examples.
- Lifecycle status invariant: completed, degraded, blocked, failed, rejected, quarantined, deadend, and promotion_candidate remain distinct and visible.
- Promotion invariant: experience_record, reuse_candidate, protocol_candidate, and needle_candidate may be represented, but installed_needle_ref is supported only and installed_needle_count remains 0. One successful run does not install a needle; automatic needle creation is blocked.
- Lifecycle authority invariant: trust and TTL updates are advisory; DRS does not mutate itself or decide promotion, reuse, override, quarantine release, or commit. Root remains commit authority.
- DRS topology invariant: DRS remains address/resonance/lineage/audit, not full memory, decision authority, vector store, automatic NeedleFactory, or external/global DRS. Dense artifacts remain outside DRS behind pointers.
- DRS Lifecycle proof status: PASS, records_created=13, malicious_claims_rejected=5, quarantine/deadends and advisory trust/TTL represented, focused tests passed=75, full suite passed=1097, sensitive scan clear. Evidence: `docs/audit_reports/auditor_drs_lifecycle_semantics.log`.
- ConflictCheck v0.1 is complete. It consumes DRS Lifecycle ExperienceRecord objects, creates ConflictCandidatePair objects, and emits ConflictReport flags without mutating source lifecycle records.
- ConflictCheck invariant: recommendations for Root/GT review, reuse/promotion block, quarantine review, or invalidation review are advisory only. ConflictCheck does not decide final truth, invalidate, promote, demote, delete, rewrite, mutate DRS, or commit.
- ConflictCheck authority invariant: Root decides truth, commit, invalidation, promotion, demotion, reuse, quarantine release, and override. GT review remains advisory until Root; DRS remains storage/index/lifecycle rather than judge.
- ConflictCheck proof status: PASS, lifecycle_records_consumed=13 and unchanged, candidate_pairs_created=11, conflict_reports_created=11, flagged_conflicts=6, root_review_required_reports=10, no_conflict_reports=1, malicious_claims_rejected=8, focused tests passed=47, full suite passed=1116, sensitive scan clear. Evidence: `docs/audit_reports/auditor_conflictcheck.log`.
- Audit / hash-chain hardening v0.1 is complete. It creates proof-level append-only evidence links from consumed proof collectors without mutating their source artifacts.
- Hash-chain proves continuity, not truth.
- Audit/hash-chain must not mutate DRS or source artifacts.
- Hash-chain entries are proof-level append-only evidence links; Root remains final authority.
- Audit/hash-chain does not validate semantic correctness, replace GT or ConflictCheck, grant authority, implement blockchain, or provide production persistence.
- Audit/hash-chain proof status: PASS, entries_created=7, chain_continuity_valid=true, tamper_detection_valid=true, append_only_semantics_preserved=true, source_artifacts_unchanged=true, malicious_claims_rejected=8, focused tests passed=49, full suite passed=1131 with 37 warnings, sensitive scan clear. Evidence: `docs/audit_reports/auditor_audit_hash_chain.log`.
- Controlled RootOrchestrator Route Assembly Integration v0.1 is complete as a standalone deterministic proof over existing collectors; it does not replace production RootOrchestrator runtime.
- Orchestrator has delegated bounded route-assembly authority only.
- Orchestrator proposes AVF inputs; AVF / HardMask remain independent and stronger than Orchestrator confidence.
- Every Orchestrator route-assembly proposal must pass Root / MatrixGate / RouteGate / Policy / AVF before reaching Architect.
- Controlled route assembly does not replace production RootOrchestrator runtime yet.
- Route-assembly authority invariant: Orchestrator is not Root and cannot create FinalOutput, write DRS, execute actions, call needles directly, bypass gates or AVF, manage AVF, override HardMask, install needles, promote candidates, release quarantine, mutate ConflictReports, decide truth, or grant authority.
- Controlled route-assembly proof status: PASS, scenarios_verified=8, malicious_claims_rejected=14, focused tests passed=67, full suite passed=1149 with 37 warnings, sensitive scan clear, production_autonomy_claimed=false. Evidence: `docs/audit_reports/auditor_controlled_root_orchestrator_route_assembly.log`.
- Applied Warehouse Semantic Demo / Warehouse-Style Proof v0.1 is complete. It proves `dispatch_readiness=not_ready` from explicit W-17 `water_filter short_by_2` evidence and rejects `invalid_ready_certificate`.
- Applied Warehouse explicit-artifact invariant: PASS depends on `validate_applied_report_consistency()` over the applied PlanGraph, node results, validation rows, GT selection, lifecycle records, ConflictReports, artifact, and audit entry.
- Applied demos must not create `protocol_candidate` / `needle_candidate` automatically unless the layer explicitly tests that lifecycle.
- Applied Warehouse proof status: PASS, applied audit entry created and hash-linked, explicit applied artifacts consistent, focused tests passed=98, full suite passed=1180 with 37 warnings, sensitive scan clear, production_autonomy_claimed=false. Evidence: `docs/audit_reports/auditor_applied_warehouse_semantic_demo.log` and `docs/audit_reports/auditor_applied_warehouse_semantic_demo_postcommit.log`.
- Applied Certificate / Document Readiness Demo v0.1 is complete. It proves `certificate_readiness=not_ready` from expired `insurance_certificate` and missing `payment_receipt` evidence and rejects `invalid_ready_certificate`.
- Applied Certificate promotion invariant: `protocol_candidate_created=false`, `needle_candidate_created=false`, and `installed_needle_created=false`.
- Applied Certificate proof status: PASS, focused tests passed=68, full suite passed=1199 with 37 warnings, sensitive scan clear, production_autonomy_claimed=false. Evidence: `docs/audit_reports/auditor_applied_certificate_readiness_demo.log` and `docs/audit_reports/auditor_applied_certificate_readiness_demo_postcommit.log`.
- Permission / NeedsUser UX Proof v0.1 is complete. Permission is not execution, approval is not completed action, and `needs_user` is not failure.
- Permission/NeedsUser proof rejects permission bypass and completed-action-without-execution. User denial remains blocked; proof-only approval is future-action permission only; Root remains final authority.
- Permission/NeedsUser promotion invariant: `protocol_candidate_created=false`, `needle_candidate_created=false`, and `installed_needle_created=false`.
- Permission/NeedsUser proof status: PASS, scenarios_verified=5, focused tests passed=70, full suite passed=1219 with 37 warnings, sensitive scan clear, production_autonomy_claimed=false. Evidence: `docs/audit_reports/auditor_permission_needsuser_ux_proof.log` and `docs/audit_reports/auditor_permission_needsuser_ux_proof_postcommit.log`.
- NeedleCandidate lifecycle / NeedleForge prototype v0.1 is complete. A safe repeated applied pattern may become a bounded proof-level NeedleCandidate after applied evidence, permission boundaries, validation, advisory GT, and Root review.
- NeedleCandidate != installed Needle. NeedleForge prototype != production NeedleFactory. GT cannot install needles. Root alone may dispose a candidate as `candidate_pending_review`, `candidate_rejected`, or `candidate_quarantined`.
- NeedleCandidate proof invariant: `needle_candidate_created=true`, `installed_needle_created=false`, `protocol_candidate_created=false`, no real external action, no production persistence, and no global DRS write.
- NeedleCandidate proof status: PASS, scenarios_verified=5, NeedleCandidate tests passed=28, focused tests passed=98, full suite passed=1247 with 37 warnings, sensitive scan clear, explicit artifacts consistent, production_autonomy_claimed=false. Evidence: `docs/audit_reports/auditor_needlecandidate_lifecycle_proof.log` and `docs/audit_reports/auditor_needlecandidate_lifecycle_proof_postcommit.log`.
- Applied DRS Retrieval / Reuse v0.1 is complete. DRS retrieval is not authority. ReuseScore is not Root. Semantic similarity is insufficient. Root alone decides final reuse.
- Applied reuse must check freshness, WorldState compatibility, permission boundaries, quarantine/deadend proximity, ConflictCheck, advisory GT, and audit evidence before Root disposition.
- Applied reuse proof invariant: every retrieval candidate remains `direct_reuse_allowed=false`, `root_review_required=true`, proof-only, local-only, and non-persistent. Stale, quarantined, deadend, wrong-domain, and permission-as-completed-action evidence cannot direct-reuse.
- Applied reuse promotion invariant: `protocol_candidate_created=false`, `needle_candidate_created=false`, and `installed_needle_created=false`. The layer consumes NeedleCandidate source proof but creates no new NeedleCandidate.
- Applied reuse proof status: PASS, scenarios_verified=7, targeted tests passed=22, focused tests passed=120, full suite passed=1269 with 37 warnings, sensitive scan clear, explicit artifacts consistent, production_autonomy_claimed=false. Evidence: `docs/audit_reports/auditor_applied_drs_retrieval_reuse.log` and `docs/audit_reports/auditor_applied_drs_retrieval_reuse_postcommit.log`.
- Roadmap order: completed through Applied DRS Retrieval / Reuse proof, postcommit audit, and fixture optimization -> Applied DRS Retrieval / Reuse docs sync current -> DRS adversarial stress -> Travel readiness -> multi-domain smoke -> Needle adversarial/safety pack -> External DRS pointer protocol -> read-only connector sandbox -> chaos applied stress -> production-boundary design docs -> only then Marennya quarantine-first -> UP transfer/opportunity.
- Roadmap priority invariant: prove the applied Root-controlled canonical path before self-improvement layers. Marennya / UP may remain deferred stubs.

7. WorldState relevance
   - WorldState must not auto-load irrelevant needles such as weather.
   - Optional context is loaded only when requested by intent, policy, or an applicable installed needle.

8. Memory-first reuse
   - Local memory retrieval must be attempted before Architect.
   - Prior records are retrieved through TemporalQuery before Architect.
   - ReuseGate evaluates freshness, GTTrust, policy, conflict, TimeEnvelope validity, and ReuseScore.
   - If explicit direct reuse is not allowed, retrieved records may influence CandidateVector generation and AVF as context_only / memory-informed context.
   - ReuseGate may return none, context_only, or direct_reuse_candidate.
   - direct_reuse_candidate is not actual direct reuse by itself.
   - reuse_applied remains false unless Root is explicitly called with direct reuse enabled.
   - Actual direct reuse requires explicit Root-level shortcut logic and tests proving Architect and Executor were skipped.

Execution routing invariant:

- The full cognitive pipeline must be available, but it is the maximum loop, not the mandatory path for every request.
- An explicit ExecutionModeRouter / ModeRouter must select the cheapest safe execution mode before choosing pipeline depth.
- Adaptive routing is future production behavior; the v0.25 CLI demo intentionally runs in proof_full_pipeline mode.
- In default v0.25 demo mode, shortcut_disabled_for_demo = true, direct_reuse_candidate_only = true, and adaptive_routing_future_runtime = true.
- The default v0.25 demo must not silently choose L0 deterministic_reflex or L1 direct_reuse; it exercises the full deterministic pipeline to prove contracts and invariants.
- The explicit direct_reuse CLI/test scenario may skip Architect and Executor only after ReuseGate eligibility and explicit Root permission.
- Routing must consider intent complexity, risk, novelty, installed needles, DRS candidates, ReuseScore, Freshness, GTTrust, PolicyOK, ConflictCheck, ActionPermission, user confirmation needs, latency/token budget, provenance needs, and whether state or external action will change.
- L0 deterministic_reflex may use ready deterministic needles for known safe actions without Architect or heavy LLM, but it still requires policy, permission when actionful, minimal trace/audit, and DRS writeback when state changes or an action was performed.
- L1 direct_reuse may use RootFinalFromReuse or direct protocol execution only after explicit gates: ReuseScore, Freshness, GTTrust, PolicyOK, ConflictCheck, TimeEnvelope validity, and ActionPermission when external action is involved.
- L2 memory_informed_execution means prior records exist, but shortcut is not allowed; a DRS hit is not direct reuse by itself.
- L3 avf_architect_execution uses AVF and Architect for tasks needing planning without full deep branching.
- L4 full_fractal_reasoning is reserved for novel, ambiguous, risky, high-value, conflicting, or multi-branch tasks.
- L5 deferred_reflection covers Marennya, UP, deep research, idle validation, and scheduled work; it must not block immediate user response unless explicitly requested.
- No DRS retrieval may occur without TemporalQuery in any execution mode.
- L0/L1 paths must not bypass safety, policy, permission, audit, or required DRS writeback.
- A DRS hit only permits memory_context_applied by default.
- Direct reuse requires explicit Root shortcut logic and must not be implemented by accident.
- Direct reuse must still create Root-only FinalOutput plus DRS writeback and audit trace.
- Tests for direct reuse must prove Architect and Executor were skipped.
- Direct external/action execution must still respect policy, access control, audit, and DRS writeback.

L0 closure invariant:

- Deterministic reflex is a minimal mock path, not the main intelligence layer.
- L0 exists to prove a cheap execution path without the full pipeline.
- L0 must not bypass Root.
- L0 must not bypass permission, policy, audit, or DRS writeback.
- L0 may skip Architect and Executor only when explicitly allowed by Root flags.
- L0 must not perform real external actions in MVP.
- Full pipeline proof mode remains available and default.
- L0 should not be expanded further until real needle/interface work begins.
- After L0 closure, the next development focus is Architect/PlanGraph depth and richer planning semantics.

Needle contract invariant:

- A needle is not merely a plugin.
- A needle is a bounded protocol cell declaring capabilities, candidate vectors, allowed actions, risk level, permission policy, execution mode, audit requirements, and DRS writeback requirements.
- Runtime action/reflex behavior should prefer declared needle action metadata over hardcoded assumptions.
- declared_actions may enable deterministic_reflex or direct_protocol routing, but must not bypass Root, permission, policy, audit, or required DRS writeback.
- In MVP, real_execution_supported must remain false for declared actions.
- Mock execution must not perform real external API calls, device control, purchases, banking, identity, or government actions.
- proof_full_pipeline must remain available even if a needle declares deterministic_reflex actions.
- Unknown actions must not be executed by the reflex path.

Needle protocol steps invariant:

- declared_actions may include protocol_steps.
- protocol_steps are bounded deterministic mock workflow declarations.
- In MVP every protocol step must be mock-only.
- protocol_steps must not perform real external API calls, real device control, real purchases, banking, identity, government actions, or Telegram actions.
- Protocol execution must remain under Root authority and permission policy.
- Protocol execution must produce audit/DRS evidence when action state changes.
- Unknown protocol steps must not execute.

Canonical needle topology invariant:

- Needles are contract modules and capability boundaries, not Executor-owned plugins.
- A needle may be Root-visible, cluster-local, or branch-bound.
- Executor/runtime-port may call a permitted bounded needle capability, but Executor does not own the needle.
- Loading a needle does not grant sovereignty.
- A needle-local Orchestrator, if present, is not global Root.
- Needle outcomes pass through the canonical execution pipeline: ResultProposal -> Post V&V -> GT/Root decision -> DRS/audit/quarantine/writeback.
- Executor may call a permitted needle capability, but Root owns authority.
- Marennya and UP are built-in systemic/internal needles, not ordinary external action needles:
  - Marennya is a reflective/internal-improvement needle.
  - UP is a transfer/cross-domain-opportunity needle.
- Future systemic needle classes may include action, data, device, validator, reflective, transfer, scheduler, policy/governance, and memory-evolution/GT.
- Future systemic/internal needles may contain bounded local fractal cycles, but they must not receive global sovereignty.
- Systemic needle outputs must become canonical boundary artifacts such as ResultProposal, QuarantineRecord, VVReport, GTReport, DRS pointer, or AuditEvent.
- Cognitive mutations from systemic needles must follow quarantine-first behavior and Root-controlled promotion.
- Wording and implementation must avoid treating a needle as integrated into Executor, owned by Executor, or merely a plugin/tool.
- The current needle outcome checkpoint proves simulated NeedleRuntime outcomes can become ResultProposal-compatible artifacts, pass through Post V&V, receive real GTValidator runtime reports, receive Root-visible routing semantics, and persist to LocalDRS Work / Quarantine / DeadEnds.
- LocalDRS is the only implemented DRS runtime for this checkpoint. External DRS remains a future pointer/protocol boundary. Global DRS / Internet of Meaning is not implemented.
- Needle outcome routing semantics:
  - completed accepted outcome -> Work / task_outcome;
  - invalid_json -> Quarantine;
  - schema_validation_failed -> Quarantine;
  - unknown_exception -> Quarantine or failed trace;
  - contract_version_mismatch -> DeadEnds / blocked trace;
  - circuit_breaker_open -> DeadEnds / blocked trace;
  - timeout -> degraded trace, not successful Work;
  - permission_required -> needs_user / blocked trace, not completed action.
- Needle outcome reuse safety:
  - Work != Quarantine.
  - Work != DeadEnds.
  - degraded trace != successful Work.
  - permission_required != completed action.
  - blocked != success.
  - failed, quarantined, degraded, blocked, and deadend records are not direct-reuse eligible.
  - only accepted completed Work candidate is direct-reuse eligible in this MVP demo.
- Known limitation: the `deadends` layer is currently used broadly for blocked, degraded, and needs_user traces. A future schema may split DeadEnd, BlockedTrace, DegradedTrace, and NeedsUserTrace.

9. CandidateVector sources
   - CandidateVector values may come only from installed needles, Local DRS, external DRS pointers, or fallback exploration templates.
   - CandidateVectors must not be freely hallucinated by an LLM.

10. AVF gate
    - AVF runs before Architect.
    - AVF hard-masks forbidden vectors before Architect can see them.
    - AVF scoring is deterministic/vectorized over structured metadata, not free-form LLM reasoning.

11. Validation order
    - Post V&V runs before GTValidator.
    - GTValidator evaluates proposals after Post V&V reports exist.

12. GT scope
    - GT is not TruthProof.
    - GT is a payoff, regret, Elo, and decay update mechanism, not a claim of absolute truth.
    - GT selects the most viable candidate under explicit payoff and policy constraints.
    - GT v0.1 exposes candidate_scores, winner_payoff, and regret_summary.
    - GT v0.1.1 exposes tie_detected, tie_candidate_ids, and a deterministic tie-break rule: lower risk, lower cost, higher robustness, higher utility, then deterministic proposal id.
    - Future GT v0.2 must incorporate architecture-aware signals such as vector_id, AVF final_viability, AVF soft_mask, artifact type, execution status, human burden, fallback role, primary path role, risk level, dependency depth, reuse potential, and evidence strength.
    - GT v0.2 must not call LLMs, execute actions, or mutate DRS directly.
    - fallback_exploration must not beat safe primary paths only because of lexical proposal id.
    - illegal_coercion remains hard-masked and must never enter GT as an executable winner.
    - Marennya and UP may later consume GT v0.2 scores, regret, dominance, and dead-end signals, but GT itself remains a selector, not a truth oracle.

13. GT update rule
    - GTValidator updates Elo, regret, half_life, and/or decay_rate, or explicitly returns no_update.

14. Quarantine-first mutation
    - Marennya and UP write to Quarantine first.
    - Marennya and UP cannot mutate Work directly.

15. UP default actionability
    - UP is non-actionable by default.
    - UP records require later validation/promotion before they can influence Work.

16. Layer separation
    - Work, Thoughts, UP, DeadEnds, and Quarantine remain separate layers.
    - No component may silently merge or cross-write these layers.

## Closed Enterprise Boundary Invariants v0.4

This section records only already closed local proof boundaries. It does not
add runtime enforcement, transition-matrix hardening, schemas, proof runners,
tests, demos, real APIs, External/global DRS implementation, Marennya / UP
activation, production persistence, production autonomy, or Killer Demo
authorization.

External DRS Pointer Protocol v0.1:

- External pointer is not external/global DRS write.
- External pointer cannot launder provenance.
- External pointer does not become authority.

Read-only Enterprise Connector Sandbox v0.1:

- ConnectorObservation is not truth.
- ConnectorObservation is not trusted evidence.
- Read-only connector observation does not execute action.
- Read-only connector observation does not write DRS by itself.
- Mock connector stubs are not production connectors.

External Evidence Acceptance Gate v0.1:

- EvidenceCandidate is not AcceptedEvidence.
- EvidenceCandidate remains candidate_only until Root decision.
- ValidationPacket is not Root acceptance.
- AcceptedEvidence requires Root decision.
- AcceptedEvidence is not truth.
- AcceptedEvidence is not ready status.
- AcceptedEvidence is not action.
- AcceptedEvidence is not DRS write.
- AcceptedEvidence is not installed Needle.
- Mock validation is not real cryptographic/trust/revocation validation.

Bounded LLM Semantic Executor Node v0.1:

- Bounded LLM Semantic Executor Node keeps model output inside Executor.
- LLM is bounded Executor node capability, not actor/layer/authority.
- LLM is not Root.
- LLM is not GT.
- LLM does not finalize.
- LLM does not execute external actions.
- LLM does not write DRS by itself.
- SemanticDraft is not truth/final/action.
- SemanticDraftResultProposal must pass Post V&V, GT, and Root.

Enterprise Chaos Pack v0.1:

- Dirty enterprise surfaces cannot transfer authority.
- GT advisory cannot become Root.
- ResultProposal bypass cannot become FinalOutput.
- NeedleCandidate cannot become installed Needle.
- Child/fractal cell claim cannot become autonomous actor.
- ConflictCheck detects; Root decides.
- 18/18 escalation attempts blocked.
- 4 attempts were quarantined and blocked.

Compute Collapse Enterprise Bench v0.1:

- Synthetic compute-collapse metric is not production economics.
- `hedgehog_llm_calls=1` is synthetic routed-path estimate, not a real
  LLM/Gemini/API call by docs, walkthrough, or audit.
- DRS reuse is not authority.
- closed checkpoint metadata is not authority.
- `source_collectors_replayed=false` is performance hygiene, not truth proof.
- Audit hash-chain records continuity, not truth.
- Killer Demo remains future assembly target after maturity gates, not next
  layer and not authorized by benchmark.

Kernel Enforcement / Transition Matrix Hardening v0.1:

- Kernel Enforcement / Transition Matrix Hardening v0.1 confirms the closed
  invariants as a proof-level transition matrix.
- The transition matrix is not authority.
- The transition matrix is not production runtime authority.
- The transition matrix does not replace Root.
- Root remains final authority.
- Non-Root artifacts cannot self-promote into truth, ready status, external
  action, DRS write, installed Needle, FinalOutput, runtime activation, or
  production claim.
- RootFinalOutput -> DRSWriteback is local-only:
  `drs_writeback_scope=local_after_root_final`,
  `local_drs_writeback=true`, `global_drs_write=false`, and
  `external_drs_write=false`.

Developer Facade / Capability Manifest UX v0.1:

- Developer Facade is not Root.
- Capability manifest is not authority.
- Validated manifest candidate is not installed capability.
- Validated manifest candidate is not installed Needle.
- Validated manifest candidate is not execution permission.
- Validated manifest candidate is not accepted evidence.
- Validated manifest candidate is not truth.
- Validated manifest candidate is not FinalOutput.
- Validated manifest candidate is not production readiness.
- Developer Facade cannot bypass Transition Matrix.
- Root remains final authority.

Production Boundary Design Docs v0.1:

- Production boundary design is not production implementation.
- Production design docs do not authorize external actions.
- Production design docs do not install capabilities.
- Production design docs do not install Needles.
- Production design docs do not implement External/global DRS.
- Production design docs do not activate Marennya / UP.
- Production design docs do not make Killer Demo production-ready.
- Root remains final authority.

Enterprise Killer Demo v0.1 / Demo A:

- Demo A is Authority / Safety / Compute Collapse assembly proof only.
- Demo A does not create production readiness.
- Demo A does not execute real action.
- Demo A does not install capability.
- Demo A does not install Needle.
- Demo A does not implement Enterprise Document Killer Demo B.
- Demo A does not implement document/evidence workflow.
- Demo A preserves Root final authority.

Enterprise Document Killer Demo B v0.1:

- Demo B is Document / Evidence Workflow applied proof only.
- Demo B does not create a production document/workflow engine.
- Demo B does not execute real action.
- Demo B does not prove OCR, PDF parsing, document extraction, connector trust,
  production runtime, or production DRS.
- Demo B does not install Needle.
- Demo B does not activate Marennya or UP.
- Demo B preserves Root final authority.
- DRS reuse is not authority.
- Next schema hardening must begin with a read-only preflight scan before any
  schema/runtime validation patch.

Runtime JSON Schema Validation Hardening v0.1:

- Post V&V incoming ResultProposal and outgoing VVReport runtime schema
  validation are boundary filters only.
- The incoming schema filter validates ResultProposal artifacts before manual
  Post V&V checks.
- The outgoing schema filter validates VVReport dictionaries before Post V&V
  returns.
- Schema validation is additive and does not replace manual safety checks.
- Schema validation failure returns the V&V report rejection path or a safe
  rejected VVReport fallback and must not crash the boundary.
- Schema validation cannot create FinalOutput.
- Schema validation cannot write DRS.
- Schema validation cannot execute action.
- Schema validation cannot call GT or Root.
- Schema validation cannot grant authority.
- EvidenceItem.kind / artifact_type alignment remain open.
- Root remains final authority.

EvidenceItem.kind alignment invariant:

- EvidenceItem.kind is a local ResultProposal evidence classification.
- `fractal_dag_executor` is allowed as an evidence source classification.
- `audit` is allowed as local ResultProposal evidence support/provenance.
- `needle_runtime` remains trace metadata, not EvidenceItem.kind.
- EvidenceItem.kind does not create truth, authority, AcceptedEvidence, action
  permission, DRS write, or FinalOutput.
- Root remains final authority.
