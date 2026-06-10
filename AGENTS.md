# AGENTS.md — Hedgehog OS / Fractal Reflexive OS Demo

## Project identity

This repository is a proof-of-architecture demo for Hedgehog OS / Fractal Reflexive OS.

This is not a chatbot, not a generic agent, not a LangChain-style tool wrapper, and not a simple script.

The goal is to implement a small local demo proving that the core architecture works:

text User/Event → RootOrchestrator → Orchestrator-stage / Route Assembly → Intent → TemporalQuery → WorldState → Local DRS retrieval → CandidateVectorGenerator → AVF / HardMask / SoftMask → AttractorPacket → Architect → PlanGraph → Fractal DAG Executor / node-level Executors → ResultProposals → Post V&V → GTValidator → back to Root → Root FinalOutput → DRS writeback / audit

This is the main downward canonical execution vector, not the full architecture. Marennya and UP are separate deferred lateral/upward systemic directions.

Demo domain:

text mock government certificate request 

This repository currently targets a deterministic MVP / proof-of-architecture demo.

Do not implement the full OS.

Do not implement real external APIs.

Do not implement UI first.

Do not turn this into a chatbot.

Do not treat strategic vision documents as the current implementation sprint.

---

## Document hierarchy

Primary documents:

- specs/human_passport_v0_25.md defines MVP architecture and invariants.
- specs/math_appendix_v0_3.md defines formulas and algorithmic details.
- specs/machine_manifest_v0_25.json defines the machine-readable project manifest.
- specs/invariants.md defines non-negotiable implementation invariants.
- specs/demo_baseline_v0_25.md defines the current deterministic demo baseline.
- specs/legacy_mapping.md defines how old code may be used as donor/reference only.
- docs/passport_geometry_root_needles.md defines the Root-centered capability geometry and anti-reduction framing.
- docs/strategic_expansion_map.md defines long-term strategic vision only.

If documents conflict for current MVP implementation, the Human Passport controls.

docs/strategic_expansion_map.md is a lighthouse / vision document, not a task queue.

Do not implement from the Strategic Expansion Map unless a later explicit task promotes part of it into the engineering roadmap.

---

## Current engineering focus

The current MVP focus is:

text Observable Zero Trust Runtime proof → Root-controlled Fractal DAG Executor integration → Root-native canonical trace → stable DRS writeback / audit → NeedleRuntime outcomes through Post V&V / real GTValidator / LocalDRS routing → Large Graph / Bounded Fractal Stress → DRS Graph Proximity / Lineage → Chaos Survival Showcase → Compute Collapse via DRS Reuse → DRS Layer Taxonomy → Typed DRS Lineage Edges → ReuseScore → Semantic Reuse Pipeline Integration → Root Semantic Reuse Decision/Gate/Final Traces → Semantic Reuse Authority Stack Audit → Root-native Semantic Reuse E2E Trace → Root-native Full Canonical E2E Trace → Optional Live Gemini Architect Smoke → Ordered Live Gemini Orchestrator-to-Architect Smoke → Controlled Orchestrator Matrix Gate → AVF / Attractor Formation from accepted Matrix → bounded Architect / Executor / Post V&V / GT / Root Final → local DRS audit/writeback → sandbox NeedleRuntime → bounded child fractal cell → live child Executor → DRS Lifecycle Semantics → ConflictCheck → Audit/hash-chain → Controlled Route Assembly → Applied Warehouse Semantic Demo → Applied Certificate Readiness Demo → next: Permission/NeedsUser UX → only later: NeedleFactory / NeedleForge

Do not jump ahead to:

- global DRS network;
- Internet of Meaning;
- needle marketplace;
- official bank/airline/government needles;
- blockchain;
- real external actions;
- production secret vault;
- global reputation system;
- unbounded recursive fractals;
- public semantic network.

These are future strategic layers, not current MVP tasks.

---

## Root-centered capability geometry

Pipeline traces are observable projections, not the architecture. Root-centered
capability geometry is the architecture. Canonical execution is the main
downward Root-controlled runtime vector; it is not merely an ordinary needle.

Needles are directed bounded capability contracts / semantic organs anchored in
Root, not plugins. DRS is semantic topology and address/resonance/lineage/audit
fabric, not vector memory or authority. Marennya is a deferred lateral
reflective systemic needle-like direction; UP is a deferred upward
transfer/opportunity systemic needle-like direction. They are proposal-only,
quarantine-first, Root-approved, and not required for first applied semantic
demos.

Anti-reduction rules:

- Do not reduce Hedgehog OS to a linear long-chain.
- Do not describe needles as plugins.
- Do not describe DRS as vector memory.
- Do not describe Marennya / UP as post-pipeline modules.
- Do not grant final authority to Orchestrator, Architect, Executor, child
  cells, needles, DRS, GT, ConflictCheck, Marennya, UP, or external DRS.
- Apply "Vassal of my vassal is not my vassal": bounded local authority does
  not propagate upward, sideways, outward, or into Root.
- Applied demos prove domain transfer of the canonical Root-controlled path.
- Applied demos now cover at least warehouse readiness and
  certificate/document readiness.
- Applied demos must not automatically create `protocol_candidate` or
  `needle_candidate` unless that lifecycle is explicitly under test.
- The next layer is Permission/NeedsUser UX proof, not Marennya / UP.

See `docs/passport_geometry_root_needles.md`.

---

## Non-negotiable architecture rules

1. FinalOutput is created only by RootOrchestrator.
2. FinalRenderer may create FinalDraftProposal only.
3. FinalDraftProposal is not FinalOutput.
4. Executors return ResultProposal only.
5. Architect receives AttractorPacket, not raw user text.
6. Architect returns PlanGraph, not a user-facing answer.
7. Fractal DAG Executor runs after Architect returns PlanGraph.
8. Fractal DAG Executor is not Root.
9. Fractal DAG Executor may return ResultProposal-shaped outputs and child boundary snapshots.
10. Fractal DAG Executor must not create FinalOutput or perform global commit.
11. Every DRSRecord must include TimeEnvelope.
12. Every DRS retrieval must use TemporalQuery.
13. AVF must run before Architect.
14. AVF must hard-mask forbidden vectors before Architect sees them.
15. CandidateVectors must come only from:
    - installed needles;
    - Local DRS;
    - external DRS pointers;
    - fallback exploration templates.
16. CandidateVectors must not be freely hallucinated by LLM.
17. AVF scoring must be deterministic/vectorized over structured metadata, not free-form LLM reasoning.
18. Post V&V runs before GTValidator.
19. GTValidator updates Elo/regret/half_life or explicitly returns no_update.
20. GTValidator does not prove truth and does not commit final output.
21. Marennya and UP must write to quarantine first.
22. Marennya and UP must not mutate Work directly.
23. Work / Thoughts / UP / DeadEnds / Quarantine must remain separate layers.
24. L0/L1 shortcuts must not bypass Root, policy, permission, audit, or required DRS writeback.
25. A DRS hit is not direct reuse by itself.
26. Direct reuse requires explicit Root shortcut logic and tests proving Architect and Executor were skipped.
27. No real external API, device, purchase, banking, identity, government, or Telegram action may execute in MVP.
28. Large or malformed PlanGraphs must be bounded or blocked, not executed as uncontrolled flat graphs.
29. Graph proximity is a query-time ranking signal only; it does not override policy, validation, TimeEnvelope, GTTrust, or ReuseGate.
30. DeadEnds, Quarantine, blocked, failed, and degraded records must not become direct-reuse eligible because they are graph-near.
31. Showcase reports must be derived from existing proof outputs or structured collectors, not hardcoded PASS tables.
32. Chaos Survival Showcase is not production autonomy and must not imply live Gemini, Telegram actions, external DRS, global DRS, or real external actions.
33. Compute Collapse via DRS Reuse is an evidence aggregator, not a new runtime layer or billing benchmark.
34. Compute Collapse may say zero re-planning path or near-zero LLM cost path, but must not claim absolute zero cost or real token savings proven.
35. Direct reuse must require eligible Work and must not bypass Root.
36. DRS Layer Taxonomy clarifies broad DeadEnds semantics but does not change ReuseGate, schema layers, or direct reuse eligibility.
37. Taxonomy must not make quarantine, dead_end, blocked_trace, degraded_trace, or needs_user_trace records reusable.
38. Typed DRS Lineage Edges are query-time semantic signals only in v0.1; they must not override policy, ReuseGate, or direct reuse gates.
39. ReuseScore is advisory/ranking only; it is not Root, not ReuseGate, and not policy override.
40. High ReuseScore must not make Quarantine, dead_end, blocked_trace, degraded_trace, needs_user_trace, or contradiction-risk records direct-reuse eligible.
41. ReuseScore must send contradiction-risk candidates to needs_conflict_check until production ConflictCheck exists.
42. Semantic Reuse Pipeline may recommend and explain, but must not commit FinalOutput, bypass Root, bypass ReuseGate, execute direct reuse, or treat context memory as direct reuse.
43. Root Semantic Reuse Decision/Gate traces are dry-run proofs only; they must not change production RootOrchestrator behavior, execute direct reuse, create production FinalOutput, or write production Work records.
44. ReuseGate approval in the semantic reuse trace means return upward to Root final decision, not production execution.
45. Root Semantic Reuse Final Decision Trace is a dry-run proof only; it may create a trace-level Root final decision artifact, but not production FinalOutput, production direct reuse, external action, or production Work writeback.
46. Root-native Semantic Reuse E2E Trace is deterministic proof only; it may create a trace-level final answer artifact by Root, but it must not change production RootOrchestrator behavior, execute production direct reuse, create production FinalOutput, write production Work, call live Gemini, use Telegram actions, or implement global/external DRS.
47. Root-native Full Canonical E2E Trace is deterministic proof only; it may show local proof DRS writeback, but it must not claim production persistence, production reuse, production direct reuse, production external-action FinalOutput, live Gemini, Telegram action, global DRS, or external DRS.
48. Optional Live Gemini Architect Smoke is opt-in role substitution only. Gemini may substitute only the Architect proposal role and must not become Root, Orchestrator, Executor, GT, or FinalRenderer; create FinalOutput; write DRS; execute actions; or bypass AVF, PlanGraph contract, Executor, Post V&V, GT, Root, ReuseGate, policy, or permission gates.
49. Ordered Live Gemini Orchestrator-to-Architect Smoke is opt-in role substitution only. Gemini may act as Orchestrator proposal actor first and Architect proposal role second, but only after schema-backed local Orchestrator validation. Gemini must not become Root, create FinalOutput, write DRS, execute actions, bypass AVF / Architect contract / Executor / Post V&V / GT / Root / ReuseGate / policy / permission gates, or activate Marennya / UP by default.
50. Controlled Orchestrator Matrix Gate is deterministic proof only. Orchestrator matrix is an input artifact, not authority; Root creates RootMatrixGateDecision artifacts and may accept, reject, or downgrade. The layer must not invoke AVF / Attractor formation, reach Architect from invalid/rejected matrices, execute production actions, create FinalOutput, write DRS by Orchestrator, implement global/external DRS, or invoke Marennya / UP.
51. AVF / Attractor Formation from accepted Matrix is deterministic proof only. It may consume accepted or downgraded RootMatrixGateDecision outputs, but rejected matrices must not reach AVF. AVF remains independent; Orchestrator hints are hints, not commands; HardMask and policy beat Orchestrator confidence. This layer must not invoke Architect or Executor, create FinalOutput, write DRS, execute actions, implement global/external DRS, or invoke Marennya / UP.
52. Architect from bounded AttractorPacket is deterministic proof only. Architect receives only bounded AVF output, not raw Orchestrator matrix, raw unchecked user intent, rejected matrix, or invalid/unbounded AttractorPacket. Architect may produce PlanGraph proposal only; PlanGraph contract must be checked; invalid Architect output must be contained. This layer must not invoke Executor, Post V&V, or GT, create FinalOutput, write DRS, execute actions, implement global/external DRS, or invoke Marennya / UP.
53. DAG / Executor from valid PlanGraph is deterministic proof only. Executor receives only validated PlanGraph nodes, not invalid Architect artifact, raw Architect text, raw Orchestrator matrix, raw user intent, or unvalidated PlanGraph. Executor returns ResultProposal only and must not create FinalOutput, write DRS directly, execute real external actions, invoke Post V&V / GT, implement global/external DRS, or invoke Marennya / UP.
54. Post V&V from ResultProposal is deterministic proof only. Post V&V receives only ResultProposal artifacts, not raw Executor text, raw Architect PlanGraph, raw Orchestrator matrix, raw user intent, real action output, malicious claim payloads, or malformed ResultProposal shapes. It creates ValidationReport / V&VReport only and must not create FinalOutput, write DRS directly, execute actions, invoke GT / Root Final, implement global/external DRS, or invoke Marennya / UP.
55. GT from ValidationReport is deterministic proof only. GT receives only ValidationReport / V&VReport artifacts, not raw ResultProposal, raw Executor text, raw Architect PlanGraph, raw Orchestrator matrix, raw user intent, real action output, malicious claim payloads, or malformed ValidationReport shapes. It creates GTDecision / selection artifact only and must not create FinalOutput, write DRS directly, execute actions, invoke Root Final, implement global/external DRS, or invoke Marennya / UP.
56. Root Final from GTDecision is deterministic proof only. Root Final receives only GTDecision / selection artifacts, not raw ValidationReport, raw ResultProposal, raw Executor text, raw Architect PlanGraph, raw Orchestrator matrix, raw user intent, real action output, malicious GTDecision claims, or malformed GTDecision shapes. Root creates FinalOutput / trace-level final artifact only and is the only final-output authority. This layer must not write DRS, invoke DRS writeback, execute actions, claim production persistence, implement global/external DRS, or invoke Marennya / UP.
57. Applied Warehouse Semantic Demo v0.1 proves `not_ready` from explicit W-17 stock shortage and rejects an invalid ready certificate. Its applied PlanGraph, execution results, validation rows, GT selection, lifecycle records, ConflictReports, artifact, and audit entry must remain explicitly linked and consistency-checked.
58. Applied demos must not automatically create `protocol_candidate` or `needle_candidate` unless that lifecycle is explicitly under test.
59. Applied Certificate / Document Readiness Demo v0.1 proves `not_ready` from expired/missing documents and rejects an invalid ready certificate. It creates no protocol candidate, needle candidate, or installed needle.

---

## Observable Zero Trust Runtime proof

The main auditor-facing proof command is:

bash python -m demo.run_canonical_pipeline_trace 

This trace should show:

- Root authority;
- explicit Orchestrator-stage / Route Assembly;
- TemporalQuery and DRS precheck;
- allowed CandidateVector sources only;
- AVF / HardMask / SoftMask before Architect;
- Root-created AttractorPacket;
- Architect input as AttractorPacket only;
- Architect output as PlanGraph;
- Fractal DAG Executor Core execution;
- ResultProposal-only execution outputs;
- Post V&V before GT;
- GT selection without final commit;
- artifact return to Root;
- Root-only FinalOutput;
- DRS writeback / audit;
- Marennya/UP quarantine hooks;
- no real external actions;
- no uncontrolled delegation.

This is a demo-runtime proof, not production OS runtime.

---

## Large Graph / Bounded Fractal Stress

`python -m demo.run_large_graph_stress` proves deterministic bounded behavior for oversized or malformed PlanGraphs. It demonstrates max_nodes, max_edges, max_depth, max_parallelism, cycle detection, unknown dependency detection, child boundary snapshots, and bounded GT candidate summaries.

This does not prove production 10k-node execution. It shows that oversized or malformed graphs are blocked or bounded instead of attempted as uncontrolled flat execution. The stress runner does not call the real GTValidator runtime; it reports `gt_runtime_called: false` and `gt_boundary_mode: bounded_summary_check`. The raw large graph is not sent to GT. The DAG runner remains after Architect and is not Root.

## DRS Graph Proximity / Lineage

`python -m demo.run_drs_graph_proximity` proves a LocalDRS-only read-only ranking signal. Records store links through lineage/source refs; they do not store static `hops_ago`, `hop_distance`, or `graph_distance`. Graph distance is computed at query time, and GraphProximity uses:

```text
graph_proximity = 2 ** (-distance / hop_half_life)
```

GraphProximity does not change ReuseGate and does not override policy. Nearby DeadEnds are warning signals, nearby Quarantine records are quarantine signals, and neither becomes a direct-reuse candidate. External/global DRS remains future work.

---

## Chaos Survival Showcase

`python -m demo.run_chaos_survival_showcase` is an auditor-facing showcase over existing deterministic proof modules:

- NeedleRuntime Chaos;
- Canonical Needle Outcome Trace with real GTValidator integration;
- Needle Outcome DRS Routing Persistence;
- Large Graph / Bounded Fractal Stress;
- DRS Graph Proximity / Lineage.

It is not a new runtime layer. It summarizes timeout containment, quarantine routing, blocked permission/circuit-breaker cases, unsafe reuse candidates = 0, bad outcomes written to successful Work = 0, bounded/malformed graph survival, graph proximity policy safety, Root authority, no Executor/needle FinalOutput, no GT commit, no live Gemini, no Telegram actions, and no real external actions. Its PASS summary must be derived from computed section predicates.

Compute Collapse via DRS Reuse / Zero Re-Planning Path / Near-Zero LLM Cost Path is complete. Do not claim absolute zero cost.

---

## Compute Collapse via DRS Reuse

`python -m demo.run_compute_collapse_reuse_showcase` is an auditor-facing showcase over existing deterministic cold-start, Root direct reuse, LocalDRS, ReuseGate, and unsafe DRS routing proofs. It complements Chaos Survival Showcase: Chaos Survival demonstrates resilience / safety / containment, while Compute Collapse demonstrates efficiency / reuse / zero re-planning path.

It shows four scenarios:

- cold_start_full_pipeline: full pipeline, no direct reuse, Architect/Executor run, Post V&V and GT run, Root creates FinalOutput, and DRS writeback occurs.
- memory_context_only: memory_context_applied=true, direct_reuse_applied=false; context memory does not bypass Architect/Executor without eligibility.
- eligible_direct_reuse: direct_reuse_applied=true; Architect and Executor/DAG are skipped, result is sourced from eligible Work, and Root still creates FinalOutput.
- unsafe_records_not_reused: Quarantine, DeadEnds, failed, blocked, and degraded records are not direct-reuse candidates.

Compute units are illustrative deterministic units derived from route flags. They are not real token billing. Do not claim absolute zero cost, real token savings proven, or production billing benchmark.

DRS Layer Taxonomy v0.1 returns development to runtime hardening after the showcase pair. It is a LocalDRS taxonomy/reporting semantics layer, not a schema refactor and not a ReuseGate change.

It classifies the broad MVP DeadEnds semantics into:

- work_candidate / successful_work: accepted successful Work; the only direct-reuse eligible case in this demo.
- quarantine: invalid_json, schema_validation_failed, unknown_exception / failed payloads; not Work and not direct-reuse eligible.
- dead_end: stable bad route, such as contract_version_mismatch / contract_boundary.
- blocked_trace: guard, policy, permission boundary, circuit breaker, or runtime safety block.
- degraded_trace: timeout, partial failure, or service instability; not successful Work.
- needs_user_trace: user confirmation, permission, or missing human input required; not completed action.

Safety flags such as taxonomy_does_not_override_policy, broad_deadends_semantics_clarified, and direct_reuse_policy_unchanged must be derived from classified rows, not hardcoded.

Typed DRS Lineage Edges v0.1 is the completed hardening step after taxonomy. It is LocalDRS-only typed-edge proof, not a schema refactor, not a ReuseGate change, not ReuseScore, not ConflictCheck, and not global/external DRS.

It distinguishes:

- derived_from;
- same_trace;
- warns_against;
- blocked_by_policy;
- requires_user;
- degraded_from;
- supports;
- contradicts.

Typed edges are semantic signals only in v0.1. `supports` and `derived_from` may provide positive or lineage evidence but cannot make a target directly reusable by themselves. `warns_against` is warning evidence, `blocked_by_policy` is blocking evidence, `requires_user` is needs-user evidence, `degraded_from` is degradation evidence, and `contradicts` is contradiction evidence. A contradiction source is not reused, but the target is not auto-blocked by typed edges alone.

ReuseScore v0.1 is the next completed hardening step. It is a LocalDRS-only advisory/ranking proof that consumes Typed DRS Lineage Edges candidates and computes deterministic illustrative scores from visible signals: quality, freshness, gt_trust, semantic_similarity, graph_proximity, typed_positive_signal, warning_penalty, blocking_penalty, needs_user_penalty, degraded_penalty, contradiction_penalty, and risk_penalty. Raw score calculation and policy gates remain separate. ReuseScore does not change ReuseGate, bypass Root, implement production ConflictCheck, implement global/external DRS, make unsafe records reusable, claim real token billing, or claim production autonomy.

Safety examples: a high-ish scoring unsafe `blocked_trace` remains not reusable because `policy_allowed=false`; a `work_candidate` with contradiction_penalty becomes `needs_conflict_check` rather than direct reuse; `unsafe_direct_reuse_candidates` remains 0. ReuseScore is not Root, not ReuseGate, and not policy override.

Semantic Reuse Pipeline Integration v0.1 is the next completed engineering integration proof. It connects LocalDRS retrieval → taxonomy-aware filtering → typed edge interpretation → graph proximity → ReuseScore → ReuseGate / Root boundary → direct reuse candidate or full pipeline fallback. It structurally consumes `collect_reuse_score()`, preserves the source Typed DRS Lineage Edges report, evaluates scenario rows, and separates recommendations from authority. It is not production RootOrchestrator integration, production autonomy, global DRS, external DRS, a ReuseGate replacement, a Root bypass, direct reuse execution, FinalOutput creation, real external action, live Gemini, or Telegram action.

Scenario semantics: `eligible_direct_reuse_candidate` is recommended but not committed by the pipeline; `context_memory_not_reuse` falls back to full pipeline because context memory is not direct reuse; `contradiction_needs_conflict_check` routes to needs_conflict_check; high score does not override policy; quarantine is not reused; needs_user is not completed action; degraded trace is not stable success; dead_end is not reused.

Safety flags: semantic_pipeline_committed_final_output=false, semantic_pipeline_bypassed_root=false, semantic_pipeline_bypassed_reuse_gate=false, root_boundary_preserved=true, reuse_gate_boundary_preserved=true, unsafe_reuse_candidates=0, production_autonomy_claimed=false, local_drs_only=true, external/global DRS not implemented. PASS must be derived from stages, scenarios, and boundary facts, not hardcoded.

Root-controlled Semantic Reuse Decision Trace v0.1 is complete. It is a deterministic Root-controlled dry-run proof that consumes Semantic Reuse Pipeline recommendations. It does not change production RootOrchestrator behavior, execute direct reuse, create production FinalOutput, write production Work records, or grant authority to the semantic pipeline. Decision mapping: direct_reuse_candidate → root_accepts_direct_reuse_candidate_for_gate_review; needs_full_pipeline → root_selects_full_pipeline_fallback; needs_conflict_check → root_requires_conflict_check; blocked → root_blocks_policy_blocked_route; quarantine → root_routes_to_quarantine; needs_user → root_requires_user_input; degraded → root_marks_degraded_trace; dead_end → root_rejects_dead_end.

Root-controlled Semantic Reuse Gate Trace v0.1 is complete. It is a deterministic Root/ReuseGate dry-run proof that consumes the Root decision trace. Gate review happens only for the Root-approved direct reuse candidate. Non-direct-reuse routes remain non-gate routes: full pipeline fallback, conflict check required, policy blocked, quarantine, needs_user, degraded, and dead_end. `gate_review_accepts_candidate_for_root_final_decision` means candidate returns upward to Root; it is not production execution. ReuseGate does not create FinalOutput, does not execute direct reuse, semantic pipeline does not commit, and Root keeps final authority.

Root-controlled Semantic Reuse Final Decision Trace v0.1 is complete. It is a deterministic Root-controlled dry-run proof that consumes the Root Semantic Reuse Gate Trace. It does not change production RootOrchestrator behavior, execute production direct reuse, create production FinalOutput, perform real external actions, write production Work records, or grant authority to the semantic pipeline or ReuseGate. It creates only a trace-level Root final decision artifact. Final decisions map gate outcomes explicitly: gate-approved direct reuse candidate → root_final_accepts_controlled_direct_reuse_trace; full pipeline fallback → root_final_selects_full_pipeline_fallback; conflict check → root_final_requires_conflict_check; policy blocked → root_final_blocks_policy_route; quarantine → root_final_routes_to_quarantine; needs_user → root_final_requires_user_input; degraded → root_final_marks_degraded_trace; dead_end → root_final_rejects_dead_end. `root_final_accepts_controlled_direct_reuse_trace` is still trace/dry-run, and the trace final decision artifact is not production FinalOutput.

Root-native Semantic Reuse E2E Trace v0.1 is complete. It is the first deterministic end-to-end semantic reuse trace and consumes the Semantic Reuse Authority Stack Audit. The connected path is input task → TemporalQuery → LocalDRS retrieval → taxonomy-aware filtering → typed edge interpretation → graph proximity → ReuseScore → semantic reuse recommendation → Root decision → ReuseGate review → Root final dry-run decision → trace-level final answer artifact → audit visibility. It does not change production RootOrchestrator behavior, execute production direct reuse, create production FinalOutput, write production Work records, perform real external actions, use live Gemini, use Telegram actions, or implement global/external DRS.

Selected scenario: `eligible_direct_reuse_candidate` maps direct_reuse_candidate → root_accepts_direct_reuse_candidate_for_gate_review → gate_review_accepts_candidate_for_root_final_decision → root_final_accepts_controlled_direct_reuse_trace, producing `trace_level_final_answer_artifact` by `root_orchestrator`. production_final_output=false, production_action_executed=false, production_work_record_written=false, unsafe_reuse_candidates=0, and production_autonomy_claimed=false. Proof status: E2E stages passed=12, focused tests passed=229, full suite passed=749, and the sensitive scan found no secret terms.

Root-native Full Canonical E2E Trace v0.1 is complete. It is a deterministic full canonical E2E proof that composes a first-run canonical Root-controlled path with a second-run semantic reuse authority path. The first run covers input task → Root intake / Orchestrator boundary → Architect / PlanGraph → AVF / Attractor formation → DAG / Executor → ResultProposals → Post V&V → GT → Root trace artifact → LocalDRS writeback / audit visibility. The second run covers repeat/similar task → TemporalQuery → LocalDRS retrieval → taxonomy / typed edges / graph proximity → ReuseScore → Semantic Pipeline recommendation → Root decision → ReuseGate review → Root final dry-run decision → trace-level semantic reuse answer artifact.

Full Canonical E2E safety: first_run_created_root_trace_artifact=true, first_run_local_drs_writeback_visible=true, first_run_local_work_record_written_in_proof=true, bridge_mode=deterministic_proof_linkage, production_persistence_claimed=false, production_reuse_claimed=false, production_direct_reuse_executed=false, production_final_output_created=false, production_work_record_written=false, no_live_gemini=true, no_telegram_actions=true, no_global_drs=true, no_external_drs_network=true, and production_autonomy_claimed=false. Proof status: first_run_stages_passed=9, second_run_stages_passed=12, focused tests passed=250, full suite passed=770, sensitive scan found no secret terms, commit=83f59a2 Add Root-native full canonical E2E trace.

Optional Live Gemini Architect Smoke v0.1 is complete. It is an opt-in smoke proof for substituting only the Architect proposal role inside the Full Canonical E2E boundary. Default mode is `dry_run_default`, deterministic, network-free, uses a deterministic mock Architect artifact, does not call live Gemini, and keeps `plan_graph_contract_checked=true`. Live mode requires explicit `--live`, `HEDGEHOG_ALLOW_LIVE_GEMINI=1`, and Gemini configuration; missing config reports SKIPPED rather than crashing, and invalid live artifacts are contained, do not reach Executor or Root final output, and fall back visibly to deterministic Architect. Boundary checks derive from the Full Canonical E2E source report, role flags, artifact containment, and context facts; rendered output does not print credential environment names or secret terms. Proof status: focused tests passed=212, full suite passed=788, sensitive scan found no secret terms, default dry-run status PASS, and `ready_for_future_orchestrator_live_smoke=true`.

Ordered Live Gemini Orchestrator-to-Architect Smoke v0.1 is complete. It proves an opt-in ordered role-substitution path: Root boundary → live Gemini Orchestrator proposal → schema-backed local validation → live Gemini Architect proposal → Architect contract check → no production execution. Final success evidence is `docs/audit_reports/auditor_live_gemini_ordered_orchestrator_architect_25_success_report.log`: orchestrator_initial_attempt_valid=true, orchestrator_active_proposal_source=live_gemini, orchestrator_active_proposal_is_fallback=false, temporal_query_required_value=true, downstream_actors_missing=[], downstream_actors_extra=[], architect_artifact_source=live_gemini, architect_artifact_valid=true, production_final_output_created=false, and production_external_action_executed=false. Older ordered Gemini fallback reports are historical safety evidence only and must not be used as proof of dual-live success.

Controlled Orchestrator Matrix Gate v0.1 is complete. It is a deterministic Root-controlled gate proof: Orchestrator matrix is an input artifact, not authority; Root creates RootMatrixGateDecision artifacts and may accept, reject, or downgrade. Verified scenarios: valid_matrix_accept accepted; missing_temporal_query_reject rejected; incomplete_guards_downgrade_or_reject downgraded with missing guards listed and unsafe_claims_removed=true; wrong_downstream_actors_reject rejected with missing/extra actor diagnostics; forbidden_bypass_reject rejected; high_confidence_policy_block rejected with high_confidence_overrides_policy=false and policy_beats_orchestrator_confidence=true; fallback_route_visible keeps fallback visible but not executed. Proof status: scenarios_verified=7, accepted_count=1, rejected_count=5, downgraded_count=1, focused tests passed=110, full suite passed=859, sensitive scan found no secret terms. Evidence: `docs/audit_reports/auditor_controlled_orchestrator_matrix_gate_report.log`.

Gate evidence hygiene: the runner verifies `docs/audit_reports/auditor_live_gemini_ordered_orchestrator_architect_25_success_report.log` before using ordered live Gemini context. success_report_exists=true, success_report_verified=true, success_report_missing_markers=[], ordered_live_context_mode=success_report_verified, live_orchestrator_can_create_valid_matrix=true, and live_architect_can_create_valid_artifact=true. Boundary semantics: AVF, AttractorPacket, Architect, Executor, Post V&V, and GT are not reached in this layer; Orchestrator does not write DRS or create FinalOutput; production_final_output_created=false; production_external_action_executed=false; global/external DRS are not implemented; Marennya / UP are not invoked.

AVF / Attractor Formation from accepted Matrix v0.1 is complete. It consumes Controlled Orchestrator Matrix Gate v0.1 without hardcoding Matrix Gate PASS and forms AttractorPacket-like artifacts only from accepted or downgraded RootMatrixGateDecision outputs. valid_matrix_accept forms a packet; incomplete_guards_downgrade_or_reject forms a limited packet with downgraded claims visible; missing_temporal_query_reject, high_confidence_policy_block, forbidden_bypass_reject, and wrong_downstream_actors_reject are blocked before AVF. rejected_matrix_packets=0, rejected_matrices_blocked_before_avf=true, attractor_packets_created=2, accepted_matrix_packets=1, downgraded_matrix_packets=1, focused tests passed=91, full suite passed=880, and sensitive scan found no secret terms. Evidence: `docs/audit_reports/auditor_avf_attractor_from_accepted_matrix_report.log`.

Architect from bounded AttractorPacket v0.1 is complete. It consumes AVF / Attractor Formation from accepted Matrix v0.1 without hardcoding AVF PASS. Architect receives only bounded AVF output, not raw Orchestrator matrix, raw unchecked user intent, rejected matrix, or invalid/unbounded AttractorPacket. Accepted bounded packets and downgraded bounded packets create valid PlanGraph proposals; rejected matrix, raw Orchestrator matrix, raw unchecked user intent, and invalid/unbounded packet inputs are blocked; invalid Architect artifact is contained. PlanGraph contract is checked, Executor / Post V&V / GT are not invoked, Architect does not create FinalOutput, write DRS, or execute actions, and Marennya / UP remain deferred. Proof status: scenarios_verified=7, valid_plan_graph_proposals_created=2, focused tests passed=93, full suite passed=903, sensitive scan found no secret terms. Evidence: `docs/audit_reports/auditor_architect_from_bounded_attractor_packet_report.log`.

DAG / Executor from valid PlanGraph v0.1 is complete. It consumes Architect from bounded AttractorPacket v0.1 without hardcoding Architect PASS. Executor receives only validated PlanGraph nodes; invalid Architect artifact, raw Architect text, raw Orchestrator matrix, raw user intent, and unvalidated PlanGraph are blocked. Accepted valid PlanGraph creates ResultProposal; downgraded valid PlanGraph creates limited/degraded ResultProposal. Executor returns ResultProposal only, does not create FinalOutput, write DRS directly, or execute real external actions, and Post V&V / GT are not invoked. Proof status: scenarios_verified=7, result_proposals_created=2, focused tests passed=85, full suite passed=923, sensitive scan found no secret terms. Evidence: `docs/audit_reports/auditor_dag_executor_from_valid_plan_graph_report.log`.

Post V&V from ResultProposal v0.1 is complete. It consumes DAG / Executor from valid PlanGraph v0.1 without hardcoding DAG / Executor PASS. Post V&V receives only ResultProposal artifacts; raw Executor text, raw Architect PlanGraph, raw Orchestrator matrix, raw user intent, and real action output are blocked. Completed ResultProposal creates an accepted ValidationReport, degraded ResultProposal creates a degraded ValidationReport, malicious FinalOutput and DRS write claims are rejected, and malformed ResultProposal is rejected. Post V&V creates ValidationReport / V&VReport only, does not create FinalOutput, write DRS directly, execute actions, invoke GT, or invoke Root Final. Proof status: scenarios_verified=10, validation_reports_created=5, rejected_validation_reports=3, focused tests passed=87, full suite passed=946, sensitive scan found no secret terms. Evidence: `docs/audit_reports/auditor_post_vv_from_result_proposal_report.log`.

GT from ValidationReport v0.1 is complete. It consumes Post V&V from ResultProposal v0.1 without hardcoding Post V&V PASS. GT receives only ValidationReport / V&VReport artifacts; raw ResultProposal, raw Executor text, raw Architect PlanGraph, raw Orchestrator matrix, raw user intent, and real action output are blocked. Accepted, degraded, and rejected ValidationReports create accept/degrade/reject GTDecision artifacts. Malicious FinalOutput, DRS write, and action execution claims are rejected; malformed ValidationReport is rejected. GT creates GTDecision / selection artifact only, does not create FinalOutput, write DRS directly, execute actions, or invoke Root Final. Proof status: scenarios_verified=13, gt_decisions_created=7, rejected_gt_decisions=5, focused tests passed=91, full suite passed=971, sensitive scan found no secret terms. Evidence: `docs/audit_reports/auditor_gt_from_validation_report.log`.

Root Final from GTDecision v0.1 is complete. It consumes GT from ValidationReport v0.1 without hardcoding GT PASS. Root Final receives only GTDecision / selection artifacts; raw ValidationReport, raw ResultProposal, raw Executor text, raw Architect PlanGraph, raw Orchestrator matrix, raw user intent, and real action output are blocked. Accept/degrade/reject GTDecision artifacts create accepted/degraded/rejected RootFinalArtifact outputs. Malicious GT FinalOutput, DRS write, and action claims are rejected; malformed GTDecision is rejected. Root is the only FinalOutput authority, GT does not create FinalOutput, Root does not write DRS, DRS writeback is not invoked, no production persistence is claimed, and Marennya / UP remain deferred. Proof status: scenarios_verified=14, root_final_artifacts_created=7, rejected_root_final_artifacts=5, focused tests passed=94, full suite passed=997, sensitive scan found no secret terms. Evidence: `docs/audit_reports/auditor_root_final_from_gt_decision.log`.

DRS Writeback / Audit from Root Final v0.1 is complete. It is a deterministic proof-level boundary that actually consumes `collect_root_final_from_gt_decision()` without hardcoding Root Final PASS. Only valid RootFinalArtifact inputs create `local_audit_only` records. Raw upstream artifacts and real action output are blocked; malformed RootFinalArtifact inputs and malicious global DRS, external DRS network, production persistence, Root DRS write, and real action claims are rejected. DRS is not the full memory, a decision authority, or a vector store; it is an address/resonance/lineage/audit layer for Root-authorized memory access, while Root remains commit authority. Proof status: scenarios_verified=16, writeback records=3 (accepted/degraded/rejected=1/1/1), focused tests passed=98, full suite passed=1037, sensitive scan found no secret terms. Evidence: `docs/audit_reports/auditor_drs_writeback_from_root_final.log`.

Root-native sandbox NeedleRuntime E2E v0.1 is complete. It sources a validated PlanGraph node from the existing Architect proof and demonstrates Root-approved bounded sandbox/mock capability execution through NeedleExecutionResult → ResultProposal → Post V&V → GTDecision → Root FinalArtifact. NeedleRuntime is not authority; needle outcome is evidence, not final truth; degraded/blocked/failed outcomes remain visible; raw output and malicious FinalOutput, DRS write, Root bypass, and external-action claims are rejected. Proof status: PASS, scenarios_verified=11, completed/degraded/blocked_or_failed=1/1/4, malicious_claims_rejected=4, focused tests passed=70, full suite passed=1057, sensitive scan clear. Evidence: `docs/audit_reports/auditor_root_native_sandbox_needleruntime_e2e.log`.

Fractal Cell Runtime v0.1 is complete. It proves the third execution route inside a parent PlanGraph: atomic node → ordinary Executor; needle-bound node → sandbox NeedleRuntime; non-atomic node with `child_cell_required=true` → bounded child fractal cell. This is not a long chain. The deterministic child mini-cell may run child Orchestrator / Architect / Executor roles, returns ChildBoundarySnapshot upward, and is adapted into a ResultProposal-compatible artifact visible to Post V&V, GT, and Root Final. Completed, degraded, blocked, and failed child states remain visible.

Child-cell boundaries: child cell and child Orchestrator are not Root; child output is boundary evidence, not final truth; no child FinalOutput, parent DRS write, real external action, or live child LLM/SLM is allowed. Recursion and execution remain bounded by depth and budget, and parent DRS promotion requires Root. ChildBoundarySnapshot is addressable experience, not an installed needle; successful traces do not automatically create needles. Proof status: PASS, scenarios_verified=12, completed/degraded/blocked_or_failed=1/1/2, malicious_child_claims_rejected=5, focused tests passed=56, full suite passed=1069, sensitive scan clear. Evidence: `docs/audit_reports/auditor_fractal_cell_runtime.log`.

Live Child Executor in Fractal Cell v0.1 is complete. It is an opt-in live Gemini proof inside one bounded child cell, not a long chain. Gemini substitutes only child Executor, receives one Architect-provided bounded node contract rather than a free instruction, and returns ChildExecutionResult JSON/evidence only. It is not child Orchestrator, child Architect, Root, FinalOutput, DRS writeback, a needle, a protocol template, or production action execution.

Verified live behavior: the proof-only task completed and reached accepted Root Final; the action-like request was detected, blocked, and preserved through ChildBoundarySnapshot, parent adapter, Post V&V, GT, and rejected Root Final with no hidden success. Live status=PASS, live opt-in/network used, child Executor only, no fallback, malicious_claims_rejected=6, no child FinalOutput, parent DRS write, API/tool call, real action, Root bypass, or Post V&V / GT / Root bypass. Deterministic safe-fallback proof and live PASS evidence: `docs/audit_reports/auditor_live_child_executor_in_fractal_cell_deterministic.log` and `docs/audit_reports/auditor_live_child_executor_in_fractal_cell_LIVE.log`. Focused deterministic tests passed=36, full suite passed=1082, sensitive scan clear.

DRS Lifecycle Semantics v0.2 is complete. It consumes the current DRS writeback, sandbox NeedleRuntime, Fractal Cell Runtime, and deterministic Live Child Executor collectors and creates local/proof-level, pointer-first ExperienceRecord objects. It represents completed, degraded, blocked, failed, rejected, quarantined, deadend, and promotion_candidate states plus experience_record, reuse_candidate, protocol_candidate, needle_candidate, and supported installed_needle_ref stages. installed_needle_count=0 and automatic needle creation remains blocked.

Lifecycle trust and TTL hints are advisory; quarantine release, deadend override, promotion, reuse, and commit remain Root-controlled. DRS remains address/resonance/lineage/audit, not full memory, decision authority, vector store, automatic NeedleFactory, or external/global DRS. Proof status: PASS, records_created=13, malicious_claims_rejected=5, focused tests passed=75, full suite passed=1097, sensitive scan clear. Evidence: `docs/audit_reports/auditor_drs_lifecycle_semantics.log`.

ConflictCheck v0.1 is complete. It consumes the 13 ExperienceRecord objects from `collect_drs_lifecycle_semantics()`, creates 11 ConflictCandidatePair objects, and emits 11 ConflictReport objects. It represents 10 contradiction/risk families plus one compatible completed-lineage no-conflict case. Lifecycle records remain unchanged.

ConflictCheck recommendations are advisory until Root. It may recommend Root/GT review, reuse/promotion blocks, quarantine review, or invalidation review, but it does not decide truth, mutate DRS, invalidate, promote, demote, delete, rewrite, or commit. DRS remains storage/index/lifecycle, not judge. Proof status: PASS, candidate_pairs_created=11, conflict_reports_created=11, flagged_conflicts=6, root_review_required_reports=10, no_conflict_reports=1, malicious_claims_rejected=8, focused tests passed=47, full suite passed=1116, sensitive scan clear. Evidence: `docs/audit_reports/auditor_conflictcheck.log`.

Audit / hash-chain hardening v0.1 is complete. It consumes the current proof collectors and creates seven deterministic append-only evidence links across Root Final / DRS writeback, NeedleRuntime, ChildCell, deterministic Live Child Executor reference, DRS Lifecycle, ConflictCheck, and the final checkpoint. Proof status: PASS, chain_continuity_valid=true, tamper_detection_valid=true, source_artifacts_unchanged=true, malicious_claims_rejected=8, focused tests passed=49, full suite passed=1131 with 37 warnings, sensitive scan clear. Evidence: `docs/audit_reports/auditor_audit_hash_chain.log`.

Audit/hash-chain is tamper-evident proof linkage only. Hash-chain proves continuity, not truth. It is not authority, persistence, blockchain, semantic validation, GT, ConflictCheck, or Root; it must not mutate DRS or source artifacts.

Controlled RootOrchestrator Route Assembly Integration v0.1 is complete. It is a standalone deterministic route-assembly integration proof that consumes existing collectors and verifies boundary continuity; it does not replace production RootOrchestrator runtime. The Orchestrator-stage has delegated bounded route-assembly authority only.

Orchestrator may propose route-assembly fields, but every proposal must pass Root / MatrixGate / RouteGate / Policy / AVF before reaching Architect. Orchestrator proposes AVF inputs; it does not manage AVF. AVF / HardMask remain independent and stronger than Orchestrator confidence. Orchestrator is not Root and must not create FinalOutput, write DRS, execute actions, call needles directly, install needles, promote candidates, release quarantine, mutate ConflictReports, decide truth, or grant authority.

Current status: Root-centered proof geometry now includes controlled route assembly, Gate / AVF constraints, bounded planning/execution contracts, Root Final, DRS Lifecycle, ConflictCheck, and proof-level audit/hash linkage. Pipeline traces remain observable projections, not the architecture.

Corrected engineering order: Passport Geometry docs sync (complete) -> Audit / hash-chain hardening v0.1 (complete) -> audit/hash-chain docs sync (complete) -> Controlled RootOrchestrator Route Assembly Integration v0.1 (complete) -> Controlled RootOrchestrator docs sync (current) -> applied semantic demo / warehouse-style proof -> applied demo docs/audit -> Marennya quarantine-first v0.1 -> UP transfer/opportunity v0.1 -> NeedleCandidate lifecycle / NeedleForge prototype -> External DRS pointer protocol.

Do not implement Marennya / UP before the applied Root-controlled canonical path passes practical semantic demos cleanly. The current priority is applied canonical execution, not self-improvement.

---

## Execution routing

The full cognitive pipeline must be available, but it is the maximum loop, not the mandatory path for every request.

Future production runtime requires an explicit ExecutionModeRouter / ModeRouter.

Execution levels:

- L0 deterministic_reflex: ready deterministic needle / known safe action; no Architect; no heavy LLM.
- L1 direct_reuse: fresh trusted DRS record or protocol replay through explicit Root shortcut gates.
- L2 memory_informed_execution: prior records found, but shortcut not allowed.
- L3 avf_architect_execution: AVF + Architect for bounded planning.
- L4 full_fractal_reasoning: multi-branch, ambiguous, risky, or high-value tasks.
- L5 deferred_reflection: Marennya, UP, idle validation, deep research, scheduled work.

In default v0.25 proof mode, shortcut routing is disabled so the demo exercises the full deterministic pipeline.

Explicit direct reuse scenario may skip Architect and Executor only after:

- ReuseScore;
- Freshness;
- GTTrust;
- PolicyOK;
- ConflictCheck;
- TimeEnvelope validity;
- ActionPermission if external action is involved;
- explicit Root permission.

---

## DRS pointer-first rule

- DRS is a registry/resolver/index, similar to a much more complex DNS for memory, capabilities, and knowledge routes.
- DRS records should prefer pointer + summary + metadata over raw payload.
- MVP LocalDRS may store small inline non-secret content only as a local simplification.
- LocalDRS is the only implemented DRS runtime in the MVP.
- External DRS remains a future pointer/protocol boundary.
- Global DRS / Internet of Meaning is not implemented.
- DRS records are addressable meaning records with TimeEnvelope, provenance, GT metadata, validation metadata, trace refs, and routing semantics.
- Real payload may live in local memory, local JSON, local secure vault, vector store, document store, project store, or external DRS pointer.
- Pointer resolution is a separate future responsibility and must respect access_policy.
- DRS must never directly store credentials, tokens, passwords, private keys, passport numbers, card numbers, CVV, or similar sensitive payloads.
- Future production versions should use Credential Vault / sealed secret slots.
- DRS may store secret references, scopes, provenance, access policy, and audit metadata, but not raw secret values.
- LLM/SLM components may reason over the existence, type, scope, and permission state of sealed slots without seeing the secret itself.
- Every DRSRecord still requires TimeEnvelope.
- Every retrieval still requires TemporalQuery.
- Work / Thoughts / UP / DeadEnds / Quarantine remain separate layers.
- Marennya and UP must write to Quarantine first and must not mutate Work directly.

---

## Needle topology

Needles are contract modules and capability boundaries, not Executor-owned plugins.

A needle may be:

- Root-visible;
- cluster-local;
- branch-bound;
- systemic/internal.

Executor or a runtime port may call a permitted bounded needle capability, but Executor does not own the needle.

Loading a needle does not grant sovereignty.

A needle-local Orchestrator, if present, is not global Root.

Needle outcomes must pass through the canonical pipeline:

text NeedleRuntime / adapter → ResultProposal-compatible artifact → Post V&V → real GTValidator runtime report → Root-visible routing semantics → LocalDRS Work / Quarantine / DeadEnds persistence 

Needle outcome routing semantics in the current MVP:

- completed accepted outcome -> Work / task_outcome;
- invalid_json -> Quarantine;
- schema_validation_failed -> Quarantine;
- unknown_exception -> Quarantine or failed trace;
- contract_version_mismatch -> DeadEnds / blocked trace;
- circuit_breaker_open -> DeadEnds / blocked trace;
- timeout -> degraded trace, not successful Work;
- permission_required -> needs_user / blocked trace, not completed action.

Safety rules:

- Work != Quarantine.
- Work != DeadEnds.
- degraded trace != successful Work.
- permission_required != completed action.
- blocked != success.
- failed / quarantined / degraded / blocked / deadend records are not direct-reuse eligible.
- only accepted completed Work candidate is direct-reuse eligible in this MVP demo.

Known limitation: `deadends` is currently used broadly for blocked, degraded, and needs_user traces. A future schema may split DeadEnd, BlockedTrace, DegradedTrace, and NeedsUserTrace.

Marennya and UP are built-in systemic/internal needles:

- Marennya is a reflective/internal-improvement needle.
- UP is a transfer/cross-domain-opportunity needle.

Future systemic/internal needles may contain bounded local fractal cycles, but they must not receive global sovereignty.

Systemic needle outputs must become canonical boundary artifacts such as:

- ResultProposal;
- QuarantineRecord;
- VVReport;
- GTReport;
- DRS pointer;
- AuditEvent.

Cognitive mutations from systemic needles must follow quarantine-first behavior and Root-controlled promotion.

---

## Required MVP repository layout

Create and preserve this structure as the baseline, while allowing newer committed files to extend it:

text hedgehog-os/   README.md   AGENTS.md    docs/     strategic_expansion_map.md    specs/     human_passport_v0_25.md     math_appendix_v0_3.md     machine_manifest_v0_25.json     invariants.md     demo_baseline_v0_25.md     legacy_mapping.md    schemas/     common.schema.json     intent.schema.json     time_envelope.schema.json     temporal_query.schema.json     world_state.schema.json     candidate_vector.schema.json     attractor_packet.schema.json     plan_graph.schema.json     result_proposal.schema.json     vv_report.schema.json     gt_report.schema.json     drs_record.schema.json     marenna_record.schema.json     up_record.schema.json     final_output.schema.json    hedgehog/     __init__.py     models.py     time_model.py     drs.py     world_state.py     candidate_vectors.py     avf.py     architect.py     fractal_dag_executor.py     executor.py     post_vv.py     gt_validator.py     root_orchestrator.py     marenna.py     up.py     audit.py     policies.py     local_embeddings.py     similarity.py     vector_store.py    hedgehog/external_drs/     __init__.py     index.py     record.py     resolver.py    needles/     government_services.json     fallback_exploration.json    data/     drs/       work/       thoughts/       up/       quarantine/       deadends/    demo/     run_certificate_demo.py     run_fractal_dag_executor_core.py     run_canonical_pipeline_trace.py     scenarios/       cold_start.json       reuse.json    tests/     test_schema_files_valid.py     test_needles_valid.py     test_time_model.py     test_candidate_vectors.py     test_avf_runtime.py     test_architect_runtime.py     test_fractal_dag_executor_core_runner.py     test_executor_runtime.py     test_post_vv_runtime.py     test_gt_validator_runtime.py     test_drs_runtime.py     test_root_orchestrator_runtime.py     test_canonical_pipeline_trace_runner.py 

---

## Implementation order

Do not start by writing the whole OS.

Use this order for current MVP work:

1. Repository layout.
2. JSON schemas.
3. Python models.
4. TimeEnvelope and TemporalQuery helpers.
5. Local JSON DRS.
6. CandidateVectorGenerator.
7. AVF scoring.
8. AttractorPacket creation.
9. Deterministic Architect stub.
10. Executor stubs returning ResultProposal.
11. Post V&V.
12. GTValidator.
13. RootOrchestrator full pipeline.
14. Marennya quarantine hook.
15. UP quarantine hook.
16. Demo runner:
    - cold_start scenario;
    - reuse scenario.
17. Execution routing / direct reuse gate.
18. L0 deterministic reflex proof path.
19. Fractal DAG Executor Core.
20. Canonical pipeline trace / Observable Zero Trust Runtime proof.
21. Documentation checkpoint.
22. Root-controlled FractalDagExecutor integration.
23. Root-native canonical trace.
24. Root-native DAG/DRS/audit stabilization.
25. Needle outcome Post V&V / real GTValidator / LocalDRS routing.
26. Large Graph / Bounded Fractal Stress.
27. DRS Graph Proximity / Lineage.
28. Chaos Survival Showcase.
29. Compute Collapse via DRS Reuse / Zero Re-Planning Path / Near-Zero LLM Cost Path.
30. DRS Layer Taxonomy v0.1.
31. Typed DRS Lineage Edges v0.1.
32. ReuseScore v0.1 as advisory/ranking only.
33. Semantic Reuse Pipeline Integration v0.1.
34. Root-controlled Semantic Reuse Decision Trace v0.1.
35. Root-controlled Semantic Reuse Gate Trace v0.1.
36. Root-controlled Semantic Reuse Final Decision Trace v0.1.
37. Root-native Semantic Reuse E2E Trace v0.1.
38. Root-native Full Canonical E2E Trace v0.1.
39. Optional Live Gemini Architect Smoke v0.1, opt-in only.
40. Optional Live Gemini Orchestrator Smoke v0.1, opt-in only.
41. Ordered Live Gemini Orchestrator-to-Architect Smoke v0.1, opt-in only.
42. Controlled Orchestrator Matrix Gate v0.1.
43. AVF / Attractor Formation from accepted Matrix v0.1.
44. Architect from bounded AttractorPacket v0.1.
45. DAG / Executor from valid PlanGraph v0.1.

Do not implement NeedleFactory, marketplace, global DRS, official organizational needles, blockchain, or real external actions before the canonical runtime is stable.

---

## MVP simplifications allowed

The MVP may use deterministic Python stubs.

Allowed:

- RootOrchestrator may be deterministic Python.
- Architect may be deterministic stub.
- Executors may be simulators.
- Fractal DAG Executor may use deterministic local execution.
- DRS may be local JSON files.
- External DRS may be mocked or disabled.
- GTValidator may use simple payoff + Elo.
- Marennya/UP validation may be a stubbed six-stage pipeline.
- Needles may be static JSON files.
- NeedleRuntime may be mock-only.

Not allowed:

- Removing TimeEnvelope.
- Removing TemporalQuery.
- Removing AVF.
- Removing GTValidator.
- Removing quarantine.
- Letting Executor create FinalOutput.
- Letting Architect answer the user.
- Letting DAG runner become Root.
- Mixing Work / Thoughts / UP.
- Performing real external actions in MVP.

---

## Legacy code usage

Legacy code may be used only as donor/reference.

Do not blindly preserve the old architecture.

Mapping:

- legacy engine.py -> donor for RootOrchestrator skeleton.
- legacy manager.py -> donor for WorldStateAssembler, but weather must become optional needle/context.
- legacy client.py -> donor for LocalDRS layout and registry.
- legacy fractal.py -> donor for Fractal DAG Executor / dependency execution.
- legacy run.py -> donor for executor runner.
- legacy validators.py / finalize.py -> donor for Post V&V / final draft only.
- legacy validator.py -> donor for GTValidator.
- legacy logging_audit.py -> donor for audit hashing/events.
- legacy embeddings.py / similar_lsh.py / vector_store.py -> donor for local semantic search/dedup.
- legacy index.py / record.py / resolver.py -> donor for future ExternalDRS pointer layer.
- legacy architect prompts -> reference only; upgrade to AttractorPacket input and PlanGraph output.
- legacy executor prompts -> reference only; upgrade to ResultProposal output.

Never use legacy config.py.

Never commit secrets.

Use .env.example only.

---

## Coding rules

Before editing:

1. Explain which files will change.
2. Explain why.
3. Mention which invariants are affected.

After editing:

1. List changed files.
2. Explain the reason for each change.
3. Run tests if possible.
4. Report remaining risks.

Do not run destructive commands unless explicitly requested.

Do not delete files without explicit permission.

Prefer small, reviewable commits.

For docs-only edits, do not modify runtime code, schemas, or tests unless explicitly requested.

For JSON manifest edits, validate with:

bash python3 -m json.tool specs/machine_manifest_v0_25.json > /tmp/manifest_check.json 

---

## Test policy

Every implementation phase must add or preserve tests.

Required invariants:

- Only RootOrchestrator creates FinalOutput.
- FinalRenderer creates FinalDraftProposal only.
- Executor returns ResultProposal only.
- Architect receives AttractorPacket only.
- Architect returns PlanGraph only.
- Fractal DAG Executor does not create FinalOutput.
- Every DRSRecord has TimeEnvelope.
- Every DRS retrieval requires TemporalQuery.
- AVF blocks forbidden vectors before Architect.
- CandidateVectors are not freely LLM-generated.
- GTValidator updates half_life or returns no_update.
- GTValidator does not commit FinalOutput.
- Marennya writes to quarantine before Thoughts.
- UP writes to quarantine before UP layer.
- UP and Marennya cannot mutate Work directly.
- Work / Thoughts / UP / DeadEnds remain separated.
- Direct reuse skips Architect/Executor only when explicit gates and Root permission allow it.
- L0/L1 shortcuts preserve policy, permission, audit, and DRS writeback.
- No real external actions occur in MVP.

---

## First task for Codex

When first started, Codex must not edit files.

First command should be:

text Analyze this repository without changing files. Explain what files and structure exist now. Do not edit anything. 
