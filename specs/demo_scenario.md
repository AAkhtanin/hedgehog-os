# MVP Demo Scenario

The MVP demo domain is a mock government certificate request.

The demo is a local proof-of-architecture, not a production service, chatbot, UI, or external API integration.

This file is a short scenario overview. The more detailed baseline contract is defined in:

text specs/demo_baseline_v0_25.md 

The demo must preserve the current canonical runtime:

text User/Event → RootOrchestrator → Orchestrator-stage / Route Assembly → TemporalQuery → WorldState → LocalDRS retrieval → CandidateVectors → AVF / HardMask / SoftMask → AttractorPacket → Architect → PlanGraph → Fractal DAG Executor / node-level Executors → ResultProposals → Post V&V → GTValidator → back to Root → Root FinalOutput → DRS writeback / audit → Marennya/UP quarantine hooks 

## Scenarios

### cold_start

The cold-start scenario begins without a reusable prior DRS answer for the certificate request.

It must prove that the system can:

- derive intent from the user/event;
- create a TemporalQuery;
- assemble a relevant WorldState;
- query Local DRS only through TemporalQuery;
- return no reusable prior Work records;
- generate CandidateVector values from allowed sources only;
- hard-mask forbidden vectors through AVF before Architect;
- create an AttractorPacket;
- pass the AttractorPacket to Architect;
- receive a PlanGraph from Architect;
- execute the graph through Fractal DAG Executor / node-level Executors;
- receive ResultProposal outputs only;
- run Post V&V;
- run GTValidator;
- return artifacts back to Root;
- produce Root-only FinalOutput;
- write back to DRS with TimeEnvelope;
- route Marennya and UP outputs through quarantine hooks.

Expected high-level trace:

text retrieved_record_count = 0 memory_context_applied = false reuse_decision = none reuse_applied = false illegal_coercion blocked = true FinalOutput.created_by = root_orchestrator 

### reuse / context_only

The ordinary reuse scenario runs after a prior Work record exists.

It must prove memory-first behavior before Architect without claiming actual direct reuse.

Expected behavior:

- TemporalQuery runs before DRS retrieval;
- prior relevant records may be retrieved;
- memory_context_applied = true;
- reuse_decision = context_only for ordinary prior records;
- reuse_applied = false;
- Architect still runs;
- Fractal DAG Executor / node-level Executors still run;
- Post V&V still runs;
- GTValidator still runs;
- final output still comes only from RootOrchestrator;
- new DRS writeback includes TimeEnvelope.

Important distinction:

text A DRS hit is not direct reuse by itself. context_only is memory-informed execution, not RootFinalFromReuse. 

### direct_reuse

The explicit direct reuse scenario is separate from ordinary reuse.

It requires a strong accepted prior Work record and explicit Root permission.

It must prove that actual direct reuse is gated and intentional.

Expected behavior:

- TemporalQuery runs before DRS retrieval;
- ReuseGate finds an eligible prior record;
- reuse_decision = direct_reuse;
- reuse_applied = true;
- Architect is skipped;
- Executor / DAG execution is skipped;
- Root creates FinalOutput;
- Root writes a new Work DRS record and audit trace;
- no external APIs, real actions, raw user text persistence, or secret storage are involved.

Direct reuse must never happen accidentally.

## What The Demo Must Prove

- Root authority.
- Explicit Orchestrator-stage / Route Assembly.
- TemporalQuery before DRS retrieval.
- WorldState without irrelevant weather or unrelated context.
- Memory-first retrieval before Architect.
- DRS hit does not imply direct reuse.
- CandidateVectors from allowed sources only.
- No free LLM hallucination of CandidateVectors.
- AVF / HardMask / SoftMask before Architect.
- Forbidden vectors do not reach Architect.
- AttractorPacket to Architect.
- Architect returns PlanGraph only.
- Fractal DAG Executor / node-level Executors return ResultProposals only.
- Post V&V before GTValidator.
- GTValidator update or explicit no_update.
- GT does not commit final output.
- Artifacts return to Root.
- Root-only FinalOutput.
- DRS writeback with TimeEnvelope.
- Marennya/UP quarantine hooks.
- No real external actions.

## Observable Zero Trust Runtime Trace

The main auditor-facing trace command is:

bash python -m demo.run_canonical_pipeline_trace 

This trace should show the runtime as a controlled contour, not as a long-chain prompt loop:

text Root authority → Orchestrator-stage → AVF / Attractor formation → Architect PlanGraph → Fractal DAG Executor → Post V&V → GT → back to Root → Root FinalOutput → DRS writeback 

## Needle Outcome Routing Checkpoint

Needle outcome routing is a LocalDRS-only MVP proof:

```text
NeedleRuntime / adapter
-> ResultProposal-compatible artifact
-> Post V&V
-> real GTValidator runtime report
-> Root-visible routing semantics
-> LocalDRS Work / Quarantine / DeadEnds persistence
```

Completed accepted needle outcomes may become Work/task_outcome records.
invalid_json and schema_validation_failed route to Quarantine. unknown_exception
routes to Quarantine or failed trace. contract_version_mismatch and
circuit_breaker_open route to DeadEnds / blocked trace. timeout is degraded
trace, not successful Work. permission_required is needs_user / blocked trace,
not completed action.

Failed, quarantined, degraded, blocked, and deadend records are not direct-reuse
eligible. Only the accepted completed Work candidate is direct-reuse eligible in
this MVP demo.

## Large Graph And DRS Lineage Checkpoints

Large Graph / Bounded Fractal Stress v0.1 is a deterministic stress proof. It
shows that oversized or malformed PlanGraphs are blocked or bounded instead of
executed as uncontrolled flat graphs. It demonstrates max_nodes, max_edges,
max_depth, max_parallelism, cycle detection, unknown dependency detection, child
boundary snapshots, and bounded GT candidate summaries. It does not prove
production 10k-node execution. The stress runner does not call the real
GTValidator runtime; it uses `gt_boundary_mode: bounded_summary_check`, and the
raw large graph is not sent to GT.

DRS Graph Proximity / Lineage v0.1 is a LocalDRS-only read-only ranking proof.
It writes and reads linked LocalDRS records, stores lineage/source refs rather
than static hop counters, and computes `graph_distance` at query time.
GraphProximity uses:

```text
graph_proximity = 2 ** (-distance / hop_half_life)
```

GraphProximity is not policy. It does not change ReuseGate and does not make
DeadEnds, Quarantine, blocked, failed, or degraded records direct-reuse
eligible. Nearby DeadEnds are warnings; nearby Quarantine records are quarantine
signals. External/global DRS remains unimplemented.

## Chaos Survival Showcase

Chaos Survival Showcase v0.1 is a human-readable evidence aggregator over
existing deterministic proof modules, not a new runtime layer. It composes
NeedleRuntime Chaos, Canonical Needle Outcome Trace with real GTValidator
integration, Needle Outcome DRS Routing Persistence, Large Graph / Bounded
Fractal Stress, and DRS Graph Proximity / Lineage.

The report shows that timeouts, invalid JSON, schema failures, unknown
exceptions, permission-required cases, circuit breakers, malformed graphs, and
graph-near bad records are contained or routed safely. It also shows unsafe
reuse candidates = 0, bad outcomes written to successful Work = 0, no Executor
or needle FinalOutput, no GT commit, no live Gemini, no Telegram actions, no
real external actions, and `production_autonomy_claimed: false`.

Its PASS summary is derived from computed section predicates. It does not claim
global DRS, production 10k graph execution, production retrieval, or production
autonomy.

## Compute Collapse Via DRS Reuse

Compute Collapse via DRS Reuse v0.1 is an auditor-facing showcase over existing
deterministic cold-start, Root direct reuse, LocalDRS, ReuseGate, and unsafe DRS
routing proofs. It is not a new runtime layer. It complements Chaos Survival:
Chaos Survival demonstrates resilience / safety / containment, while Compute
Collapse demonstrates efficiency / reuse / zero re-planning path.

It shows cold_start_full_pipeline, memory_context_only, eligible_direct_reuse,
and unsafe_records_not_reused. Context memory does not equal direct reuse.
Eligible direct reuse skips Architect and Executor/DAG, but still returns
through Root. Unsafe Quarantine, DeadEnds, failed, blocked, and degraded records
are not direct-reuse candidates.

Compute units are illustrative deterministic units derived from route flags, not
real token billing. savings_ratio is computed from those units. Do not describe
this as absolute zero cost, real token savings proven, production billing
benchmark, or production autonomy.

## DRS Layer Taxonomy

DRS Layer Taxonomy v0.1 is an engineering hardening layer over LocalDRS
routing/report semantics. It is not a showcase, not a schema refactor, not a
ReuseGate change, and not global/external DRS.

The taxonomy clarifies the broad MVP DeadEnds semantics:

- work_candidate / successful_work: accepted successful Work; the only
  direct-reuse eligible case in this demo.
- quarantine: invalid_json, schema_validation_failed, unknown_exception /
  failed payloads; not Work and not direct-reuse eligible.
- dead_end: stable bad route such as contract_version_mismatch /
  contract_boundary.
- blocked_trace: guard, policy, permission boundary, circuit breaker, or runtime
  safety block.
- degraded_trace: timeout, partial failure, or service instability; not
  successful Work.
- needs_user_trace: permission_required or missing human input; not completed
  action.

The taxonomy does not override policy. Direct reuse remains true only for
accepted successful Work, unsafe_direct_reuse_candidates remains 0, LocalDRS is
the only implemented DRS runtime, external/global DRS are not implemented, and
schema_refactor_performed remains false. The taxonomy proof derives its safety
and summary flags from classified rows, not hardcoded PASS claims.

## Typed DRS Lineage Edges

Typed DRS Lineage Edges v0.1 is a LocalDRS-only typed-edge proof after DRS Layer
Taxonomy. It clarifies relationship types between records without a schema
refactor, ReuseGate change, ReuseScore, ConflictCheck, global DRS, or external
DRS.

Typed edge classes:

- derived_from
- same_trace
- warns_against
- blocked_by_policy
- requires_user
- degraded_from
- supports
- contradicts

Typed edges are query-time semantic signals only in v0.1. `supports` and
`derived_from` can contribute evidence but cannot make a target directly
reusable by themselves. `warns_against` is warning evidence, `blocked_by_policy`
is blocking evidence, `requires_user` is needs-user evidence, `degraded_from` is
degradation evidence, and `contradicts` is contradiction evidence.

Contradiction source records are not reused. Contradiction targets are not
auto-blocked by typed edges in v0.1 and require future ConflictCheck /
ReuseScore handling. Records do not store static hops_ago / hop_distance /
graph_distance; graph distance and typed interpretation are computed at query
time. This checkpoint is not production retrieval and not a production semantic
internet.

## ReuseScore

ReuseScore v0.1 is a LocalDRS-only advisory/ranking proof that consumes Typed
DRS Lineage Edges candidates. It computes deterministic illustrative raw scores
from quality, freshness, gt_trust, semantic_similarity, graph_proximity,
typed_positive_signal, warning_penalty, blocking_penalty, needs_user_penalty,
degraded_penalty, contradiction_penalty, and risk_penalty.

Policy gates are applied separately after raw score calculation. ReuseScore is
not Root, not ReuseGate, not policy override, not production ConflictCheck, not
global/external DRS, not real token billing, and not production autonomy.

Safety semantics:

- high score cannot override policy;
- direct reuse still requires eligible successful Work;
- context memory does not equal direct reuse;
- quarantine / dead_end / blocked_trace / degraded_trace / needs_user_trace
  records are not direct-reuse candidates;
- contradiction does not auto-reuse;
- contradiction-risk candidates become needs_conflict_check until future
  ConflictCheck exists;
- Root authority and ReuseGate authority are preserved.

Important proof examples: a high-ish scoring unsafe blocked_trace remains not
reusable because policy_allowed is false, a work_candidate with
contradiction_penalty becomes needs_conflict_check instead of direct_reuse, and
unsafe_direct_reuse_candidates remains 0.

## Semantic Reuse Pipeline Integration

Semantic Reuse Pipeline Integration v0.1 is a bounded LocalDRS semantic reuse
integration proof. It connects LocalDRS retrieval -> taxonomy-aware filtering ->
typed edge interpretation -> graph proximity -> ReuseScore -> ReuseGate / Root
boundary -> direct reuse candidate or full pipeline fallback.

It is not production RootOrchestrator integration, production autonomy, global
DRS, external DRS, a ReuseGate replacement, a Root bypass, direct reuse
execution, FinalOutput creation, real external action, live Gemini, or Telegram
action.

It proves:

- collect_reuse_score() is structurally consumed;
- the source Typed DRS Lineage Edges report is preserved;
- all six stages pass: local_drs_retrieval, taxonomy_filtering,
  typed_edge_interpretation, graph_proximity, reuse_score, and
  reuse_gate_root_boundary;
- recommendations are separated from authority.

Scenario semantics:

- eligible_direct_reuse_candidate is recommended as direct_reuse_candidate, but
  not committed by the pipeline;
- context_memory_not_reuse falls back to full pipeline because context memory is
  not direct reuse;
- contradiction_needs_conflict_check routes to needs_conflict_check, not direct
  reuse;
- high_score_blocked_by_policy proves high score does not override policy;
- quarantine_not_reused proves quarantine is not reused;
- needs_user_not_completed_action proves needs_user is not completed action;
- degraded_not_stable_success proves degraded trace is not stable success;
- dead_end_not_reused proves dead_end is not reused.

Safety flags: semantic_pipeline_committed_final_output=false,
semantic_pipeline_bypassed_root=false, semantic_pipeline_bypassed_reuse_gate=false,
root_boundary_preserved=true, reuse_gate_boundary_preserved=true,
unsafe_reuse_candidates=0, production_autonomy_claimed=false, local_drs_only=true,
and external/global DRS are not implemented. PASS is derived from stages,
scenarios, and boundary facts, not hardcoded.

The current DRS semantic stack is DRS Graph Proximity / Lineage v0.1, DRS Layer
Taxonomy v0.1, Typed DRS Lineage Edges v0.1, ReuseScore v0.1, and Semantic
Reuse Pipeline Integration v0.1. The next planned engineering layer is
Root-controlled Semantic Reuse Decision Trace v0.1. Root should receive semantic
reuse recommendations as trace/dry-run input, check boundaries, preserve
ReuseGate, and choose between direct reuse candidate or full pipeline fallback
without giving authority to the semantic pipeline.

## Exclusions

- No real external APIs.
- No real government integration.
- No real device control.
- No real purchases.
- No real banking, identity, or legal action.
- No UI-first development.
- No production LLM/SLM role substitution by default.
- No legacy architecture repair.
- No global DRS network.
- No external DRS protocol implementation.
- No production DRS retrieval engine.
- No production autonomy.
- No production billing benchmark.
- No real token savings measurement.
- No Internet of Meaning implementation.
- No NeedleFactory implementation.
- No needle marketplace implementation.
- No production 10k-node graph execution.
- No production recursive child-cell execution.
- No universal natural Telegram assistant behavior.

## Current Interpretation

This demo scenario is intentionally small.

It does not prove the final Hedgehog OS product.

It proves that the MVP can preserve the canonical architecture:

text time-aware memory → controlled candidate vectors → AVF before Architect → AttractorPacket boundary → PlanGraph → ResultProposal-only execution → Post V&V → GT → Root-only final output → DRS writeback → quarantine-first reflection/transfer hooks 

Future useful business or assistant demos must be built on top of this baseline, not by bypassing it.
