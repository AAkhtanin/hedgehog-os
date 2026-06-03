# Demo Baseline v0.25

## 1. Purpose

This document defines the current deterministic Hedgehog OS / Fractal Reflexive OS MVP demo baseline.

This is a baseline proof-of-architecture demo, not the final AI OS demo. Its job is to prove that the invariant pipeline exists, runs locally, preserves contracts, and produces auditable trace outputs. It is intentionally small, deterministic, and CLI-driven.

The current runtime uses deterministic Python stubs. Future versions may replace specific roles with LLMs, SLMs, tool-runners, richer local services, or live integrations, but those replacements must preserve the same contracts and invariants.

This baseline should be read together with:

- specs/human_passport_v0_25.md
- specs/math_appendix_v0_3.md
- specs/machine_manifest_v0_25.json
- specs/invariants.md
- docs/strategic_expansion_map.md

docs/strategic_expansion_map.md is vision-only and not an implementation sprint. The current baseline remains focused on proving canonical runtime invariants.

## 2. Baseline Pipeline

The v0.25 baseline proves the canonical deterministic pipeline:

text User/Event → RootOrchestrator → Orchestrator-stage / Route Assembly → TemporalQuery → WorldState → LocalDRS retrieval → CandidateVectors → AVF / HardMask / SoftMask → AttractorPacket → Architect → PlanGraph → Fractal DAG Executor / node-level Executors → ResultProposals → Post V&V → GTValidator → back to Root → Root FinalOutput → DRS writeback / audit → Marennya/UP quarantine hooks 

This is the core result of the baseline. The demo is not trying to be useful as a real certificate assistant yet. It is proving that the architecture can be executed end to end without collapsing into a chatbot, generic agent chain, or unstructured prompt loop.

The full pipeline is the maximum cognitive loop, not the mandatory path for every future user action. In the full OS, an ExecutionModeRouter / ModeRouter must choose the cheapest safe execution depth. Frequent safe actions may use deterministic needles or direct reuse, while novel, risky, ambiguous, conflicting, high-value, or multi-branch tasks may use the full loop.

## 3. Demo Modes

The default v0.25 CLI demo scenarios intentionally run in proof_full_pipeline mode.

This means:

- shortcut_disabled_for_demo = true for cold_start and reuse;
- direct_reuse_candidate_only = true for cold_start and reuse;
- adaptive_routing_future_runtime = true.

The baseline demo must force the full deterministic pipeline to prove all core contracts. It should not silently choose L0 deterministic_reflex or L1 direct_reuse, even though those modes are documented as architectural requirements.

This is intentional, not inefficient design. The baseline demo is a proof harness, not production routing policy. It avoids hiding untested components behind shortcut routing. A direct_reuse_candidate may be detected by ReuseGate, but Root must still run AVF, Architect, Executor / DAG execution, Post V&V, and GTValidator unless direct reuse is explicitly enabled.

v0.25 also includes a separate explicit direct_reuse CLI/test scenario. That scenario proves the optional RootFinalFromReuse shortcut:

- direct reuse requires explicit Root permission;
- direct reuse requires an eligible ReuseGate decision;
- Architect and Executor are skipped;
- FinalOutput is still created only by RootOrchestrator;
- a new Work DRS writeback and audit trace are still created;
- no LLMs or external APIs are called;
- raw user text and secrets are not stored in DRS.

v0.25 also contains an L0 deterministic_reflex proof path. L0 exists only to prove that a cheap, permission-gated execution path can pass through Root without running the full pipeline. It is disabled by default for proof/full pipeline tests, performs no real external action, and should not be expanded further until real needle/interface work begins.

Production runtime may later enable adaptive routing after tests prove each shortcut path is safe.

## 4. Cold Start Expected Behavior

The cold_start scenario runs once against an empty LocalDRS.

Expected trace behavior:

- retrieved_record_count = 0;
- memory_context_applied = false;
- reuse_decision = none;
- reuse_applied = false;
- illegal_coercion blocked = true;
- GT winner vector id = official_online_request;
- FinalOutput created_by = root_orchestrator.

Interpretation:

- Root creates a TemporalQuery before retrieval.
- LocalDRS returns no prior Work records.
- CandidateVectors are loaded from allowed static sources.
- AVF blocks the forbidden illegal_coercion vector before Architect.
- Architect receives an AttractorPacket and returns PlanGraph only.
- Fractal DAG Executor / node-level Executors produce ResultProposals only.
- Post V&V validates the proposals.
- GTValidator selects the strongest deterministic candidate.
- Result artifacts return to Root.
- RootOrchestrator alone creates FinalOutput.
- Root writes a Work DRS record with TimeEnvelope.
- Marennya and UP create quarantine records only.

## 5. Reuse Scenario Expected Behavior

The reuse scenario runs twice against the same LocalDRS path.

The first run behaves like cold start.

The second run is expected to show:

- retrieved_record_count >= 1;
- memory_context_applied = true;
- reuse_decision = context_only for ordinary prior records;
- reuse_applied = false;
- direct reuse is not applied in this scenario;
- Architect and Executor / DAG execution still run.

Interpretation:

- The second run sees the Work record created by the first run.
- That record becomes memory context.
- The runtime is memory-informed, but it does not bypass planning or execution.
- GT still selects among fresh ResultProposals from the full pipeline.

## 6. ReuseGate Semantics

v0.25 includes a deterministic ReuseGate scoring layer. ReuseGate runs after TemporalQuery retrieval and evaluates prior DRS records before the normal planning pipeline.

ReuseGate computes:

- freshness;
- gt_trust;
- policy;
- conflict;
- reuse_score.

ReuseGate may return:

- none: no prior records were retrieved;
- context_only: records exist, but no record passed the direct reuse scoring gates;
- direct_reuse_candidate: a record passed the scoring gates.

direct_reuse_candidate is not actual reuse by itself. It means a candidate has been identified. Root still runs AVF, Architect, Executor / DAG execution, Post V&V, and GTValidator unless Root is explicitly called with direct reuse enabled.

Actual direct reuse requires explicit Root-level shortcut logic and tests proving Architect and Executor were skipped.

## 7. Direct Reuse Scenario Expected Behavior

The direct_reuse scenario seeds LocalDRS with a strong accepted Work record and calls Root with direct reuse enabled.

Expected trace behavior:

- retrieved_record_count >= 1;
- memory_context_applied = true;
- reuse_decision = direct_reuse;
- reuse_applied = true;
- architect_skipped = true;
- executor_skipped = true;
- FinalOutput created_by = root_orchestrator;
- new Work DRS writeback exists.

Interpretation:

- ReuseGate first returns direct_reuse_candidate.
- Explicit Root permission converts that candidate into actual direct reuse.
- Root creates FinalOutput directly from the trusted prior DRS record.
- Architect, Executor / DAG execution, Post V&V, and fresh GT selection are skipped for that request.
- Root still writes a new Work record and audit trace.
- No external APIs, LLMs, raw user text persistence, or secret storage are involved.

## 8. Context-Only Memory vs Direct Reuse

### Memory-Informed Execution / context_only

context_only means prior DRS records were retrieved and made visible as memory context for the run.

In v0.25:

- TemporalQuery is required.
- LocalDRS retrieval happens before AVF and Architect.
- memory_context_applied = true when relevant prior records exist.
- reuse_decision = context_only.
- reuse_applied = false.
- AVF, Architect, Executor / DAG execution, Post V&V, GTValidator, and Root FinalOutput still run normally.

This proves memory-first execution without claiming direct reuse.

### True Direct Reuse / RootFinalFromReuse

True direct reuse is an explicit optional path where Root may create a final output from a validated prior record without running the full planning/execution pipeline.

That path must be gated by checks such as:

- ReuseScore;
- Freshness;
- GTTrust;
- PolicyOK;
- ConflictCheck;
- TimeEnvelope validity.

Direct reuse is implemented in v0.25 only as an explicit CLI/test scenario. The baseline must not describe context_only or direct_reuse_candidate as actual direct reuse.

## 9. Observable Zero Trust Runtime Trace

The auditor-facing trace command is:

bash python -m demo.run_canonical_pipeline_trace 

This trace is intended to show that the deterministic runtime is not a long-chain prompt loop.

It should make visible:

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

This is still a demo-runtime proof. It does not claim production recursive child-cell execution, real external API execution, real external DRS protocol, or live LLM/SLM Orchestrator defaults.

## 10. Needle Outcome DRS Routing Checkpoint

The current needle outcome demos prove a local simulated path:

```text
NeedleRuntime / adapter
-> ResultProposal-compatible artifact
-> Post V&V
-> real GTValidator runtime report
-> Root-visible routing semantics
-> LocalDRS Work / Quarantine / DeadEnds persistence
```

Routing semantics:

- completed accepted outcome -> Work / task_outcome;
- invalid_json -> Quarantine;
- schema_validation_failed -> Quarantine;
- unknown_exception -> Quarantine or failed trace;
- contract_version_mismatch -> DeadEnds / blocked trace;
- circuit_breaker_open -> DeadEnds / blocked trace;
- timeout -> degraded trace, not successful Work;
- permission_required -> needs_user / blocked trace, not completed action.

Reuse safety:

- Work != Quarantine.
- Work != DeadEnds.
- degraded trace != successful Work.
- permission_required != completed action.
- blocked != success.
- failed / quarantined / degraded / blocked / deadend records are not direct-reuse eligible.
- only accepted completed Work candidate is direct-reuse eligible in this MVP demo.

This is LocalDRS only. External DRS remains a future pointer/protocol boundary.
Global DRS / Internet of Meaning, NeedleFactory, marketplace, and real external
needle execution are not implemented.

## 11. Large Graph And DRS Lineage Checkpoints

Large Graph / Bounded Fractal Stress v0.1 proves bounded behavior for oversized
or malformed PlanGraphs. It demonstrates max_nodes, max_edges, max_depth,
max_parallelism, cycle detection, unknown dependency detection, child boundary
snapshots, and bounded GT candidate summaries. It does not prove production
10k-node execution. The stress runner does not call the real GT runtime; it
reports `gt_runtime_called: false` and `gt_boundary_mode:
bounded_summary_check`. Raw large graphs are not sent to GT.

DRS Graph Proximity / Lineage v0.1 proves a LocalDRS-only read-only
retrieval/ranking signal. Records are written to and read from LocalDRS, store
links through source_refs / lineage refs, and do not store static `hops_ago`,
`hop_distance`, or `graph_distance`. `graph_distance` is computed at query time,
and GraphProximity is computed as:

```text
graph_proximity = 2 ** (-distance / hop_half_life)
```

GraphProximity is only a ranking signal. It does not change ReuseGate and does
not override policy. Nearby DeadEnds are warning signals, nearby Quarantine
records are quarantine signals, and neither becomes a direct-reuse candidate.
External/global DRS remains unimplemented.

## 12. Chaos Survival Showcase Checkpoint

Chaos Survival Showcase v0.1 is an auditor-facing showcase / evidence
aggregator over existing deterministic proof modules. It is not a new core
runtime layer. It composes:

1. NeedleRuntime Chaos.
2. Canonical Needle Outcome Trace with real GTValidator integration.
3. Needle Outcome DRS Routing Persistence.
4. Large Graph / Bounded Fractal Stress.
5. DRS Graph Proximity / Lineage.

It demonstrates timeout containment, invalid_json and schema_validation_failed
quarantine, unknown_exception containment, permission_required needs_user /
blocking, circuit breaker blocking, bad outcomes not written to successful
Work, unsafe reuse candidates = 0, oversized graph blocking, cycle graph
blocking, unknown dependency graph blocking, raw large graph not sent to GT,
Large Graph Stress as bounded-summary check rather than real GT runtime,
GraphProximity not overriding policy, Quarantine/DeadEnds not being
direct-reuse eligible, Root final authority, no Executor/needle FinalOutput, no
GT commit, no live Gemini, no Telegram actions, no real external actions, and
`production_autonomy_claimed: false`.

The showcase PASS summary is derived from computed section predicates. It does
not claim production autonomy, global DRS, production 10k-node graph execution,
or a production retrieval engine.

## 13. Compute Collapse Via DRS Reuse Checkpoint

Compute Collapse via DRS Reuse v0.1 is an auditor-facing showcase / evidence
aggregator over existing deterministic cold-start, Root direct reuse, LocalDRS,
ReuseGate, and unsafe DRS routing proof modules. It is not a new core runtime
layer.

It complements Chaos Survival Showcase:

- Chaos Survival Showcase v0.1 demonstrates reliability / safety / containment.
- Compute Collapse via DRS Reuse v0.1 demonstrates efficiency / reuse / zero
  re-planning path.

It demonstrates four scenarios:

1. cold_start_full_pipeline: full pipeline path, direct_reuse_applied=false,
   Architect and Executor are not skipped, Post V&V and GT run, Root creates
   FinalOutput, and DRS writeback happens.
2. memory_context_only: memory_context_applied=true and
   direct_reuse_applied=false. Prior memory may inform context, but it does not
   bypass Architect/Executor without eligibility.
3. eligible_direct_reuse: direct_reuse_applied=true, Architect skipped,
   Executor/DAG skipped, result sourced from eligible Work, Root still creates
   FinalOutput, and direct reuse does not bypass Root.
4. unsafe_records_not_reused: Quarantine / DeadEnds / failed / blocked /
   degraded records are not direct-reuse candidates, and
   direct_reuse_unsafe_candidates=0.

Compute units are illustrative deterministic units derived from route flags.
They are not real token billing, and savings_ratio is not a production billing
benchmark. Do not claim absolute zero cost, real token savings proven, or
production autonomy.

## 14. DRS Layer Taxonomy Checkpoint

DRS Layer Taxonomy v0.1 is runtime hardening, not a showcase. It clarifies the
broad MVP DeadEnds/reporting semantics at routing/report/content level without a
schema refactor, ReuseGate behavior change, global DRS, external DRS, or unsafe
reuse.

Taxonomy meanings:

- work_candidate / successful_work: accepted successful Work; the only
  direct-reuse eligible case in this demo.
- quarantine: invalid_json, schema_validation_failed, unknown_exception /
  failed payloads; not Work and not direct-reuse eligible.
- dead_end: stable bad route such as contract_version_mismatch /
  contract_boundary.
- blocked_trace: blocked by guard, policy, permission boundary, circuit breaker,
  or runtime safety boundary.
- degraded_trace: timeout, partial failure, or service instability; not
  successful Work.
- needs_user_trace: user confirmation, permission, or missing human input; not
  completed action.

Safety:

- timeout is degraded_trace, not stable successful Work.
- permission_required is needs_user_trace, not completed action.
- blocked_trace is not success.
- quarantine is not Work.
- direct_reuse_eligible remains true only for accepted successful Work.
- unsafe_direct_reuse_candidates = 0.
- taxonomy does not override policy.
- local_drs_only = true.
- external/global DRS are not implemented.
- schema_refactor_performed = false.

The taxonomy proof derives taxonomy_does_not_override_policy,
broad_deadends_semantics_clarified, direct_reuse_policy_unchanged, and PASS from
classified rows rather than hardcoded claims.

## 15. Typed DRS Lineage Edges Checkpoint

Typed DRS Lineage Edges v0.1 is engineering hardening after taxonomy. It is a
LocalDRS-only typed-edge proof, not a showcase, schema refactor, ReuseGate
change, ReuseScore implementation, ConflictCheck implementation, global DRS, or
external DRS.

Typed edge classes:

- derived_from;
- same_trace;
- warns_against;
- blocked_by_policy;
- requires_user;
- degraded_from;
- supports;
- contradicts.

Safety semantics:

- supports may contribute positive evidence, but cannot make a target directly
  reusable by itself.
- derived_from may contribute lineage evidence, but does not override policy.
- warns_against is warning evidence, not positive reuse evidence.
- blocked_by_policy is blocking evidence, not success.
- requires_user is needs-user evidence, not completed action.
- degraded_from is degradation evidence, not stable success.
- contradicts is contradiction evidence, but does not auto-block the target in
  v0.1.
- contradiction source records are not reused.
- contradiction targets require future ConflictCheck / ReuseScore handling.
- typed_edges_are_signals_only = true.
- ReuseScore_implemented = false.
- conflict_check_implemented = false.
- direct reuse policy remains unchanged.

Graph distance and typed edge interpretation are computed at query time. Records
do not store static hops_ago / hop_distance / graph_distance. This checkpoint is
not a claim of production retrieval or a production semantic internet.

## 16. What This Baseline Does Not Prove Yet

This baseline does not prove:

- production L0 deterministic reflex routing beyond the closed mock path;
- production L1 direct reuse routing beyond explicit CLI/test scenario;
- a complete adaptive ExecutionModeRouter;
- real LLM/SLM role substitution;
- automatic Root-level direct reuse routing;
- pointer resolution;
- external DRS protocol;
- universal natural Telegram assistant behavior;
- real external API/needle execution;
- production recursive child-cell execution;
- production 10k-node graph execution;
- production DRS retrieval engine;
- production typed-edge retrieval engine;
- production ConflictCheck;
- production ReuseScore;
- production autonomy;
- production billing benchmark;
- real token savings measurement;
- global or external DRS graph traversal;
- a polished or genuinely useful real-world assistant scenario.

These are future layers. The v0.25 baseline exists to make later changes measurable against a stable contract.

v0.25 currently demonstrates deterministic L2/L3/L4-style baseline behavior plus explicit L0 and L1 proof paths:

- cold_start uses the full deterministic path.
- The second reuse run is memory-informed context_only.
- direct_reuse demonstrates explicit optional RootFinalFromReuse.
- L0 deterministic reflex exists as a closed mock proof path, not a production expansion target.
- Automatic L0/L1 routing is future production work.

After this baseline, the next architecture work should continue runtime hardening with ReuseScore v0.1. ReuseScore must remain advisory/ranking only, not Root, not ReuseGate, and not policy override.

## 17. Future Demo Evolution

- v0.25: deterministic CLI baseline, memory-informed reuse, explicit direct reuse scenario, and closed L0 proof path.
- v0.26: Observable Zero Trust Runtime proof / canonical pipeline trace.
- v0.27: Root-controlled Fractal DAG Executor integration.
- v0.28: Root-native canonical trace.
- v0.29: Root-native DAG/DRS/audit stabilization and needle outcome LocalDRS routing.
- v0.30: Large Graph / Bounded Fractal Stress and DRS Graph Proximity / Lineage.
- v0.31: Chaos Survival Showcase.
- v0.32: Compute Collapse via DRS Reuse / Zero Re-Planning Path / Near-Zero LLM Cost Path.
- v0.33: DRS layer taxonomy v0.1.
- v0.34: Typed DRS Lineage Edges v0.1.
- v0.35: ReuseScore v0.1 as advisory/ranking only.
- v0.36: controlled LLM/SLM role substitution.
- v0.40: Telegram shell as interface only, not autonomous natural assistant.
- v0.45: richer useful assistant scenario.
