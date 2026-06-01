# Hedgehog OS Demo — Fractal Reflexive Runtime MVP

This repository demonstrates an AI OS-style runtime pipeline using deterministic Python stubs, JSON contracts, DRS memory routing, AVF scoring, GT selection, and Root-only final output. It is not a chatbot, not an agent chain, and not a UI project. The current MVP is a proof-of-architecture runtime for a future AI OS, centered on a mock government certificate request.

## What Hedgehog OS Is

Hedgehog OS / Fractal Reflexive OS is a fractal controlled-runtime topology for role-bounded intelligence. LLM/SLM components are cognitive organs inside bounded roles, not sovereign actors. Subordinate intelligence can propose routes, plans, drafts, or results, but Root commits.

The architecture is based on fractal authority topology, root-only commit, and non-transitive delegation: the vassal of my vassal is not my vassal. A delegated subcell may manage its own bounded local authority, but that authority does not automatically propagate upward, sideways, or outward.

## What Hedgehog OS Is Not

Hedgehog OS is not merely:

- an agent framework;
- a plugin wrapper;
- a LangChain-like workflow engine;
- a chatbot memory system;
- a simple guardrail layer;
- an autonomous agent wrapper.

Needles are executable meaning contracts, not plugins. DRS is a time/provenance/trust topology, not ordinary vector memory. AVF runs before planning. Architect is bounded by AttractorPacket. Executors return ResultProposal only. Post V&V runs before GT. GT selects stability/payoff, not truth. FinalOutput is created only by Root.

## Core Authority Invariants

- Root is final authority and the only creator of FinalOutput.
- Orchestrator may route/frame proposals, but must not create FinalOutput.
- Architect creates PlanGraph from AttractorPacket, but does not answer the user.
- Executor returns ResultProposal only.
- Post V&V validates proposals before GT.
- GT selects/stabilizes under payoff and policy constraints, but does not commit.
- Root creates FinalOutput and performs Work DRS writeback.

## Controlled Expansion, Not Only Narrowing

Hedgehog OS is not just narrowing like an Akinator. Large intent should expand into bounded candidate branches and fractal cells, then be constrained by AVF, HardMask, GT, and Root commit. The goal is organized complexity: enough branching to represent the real task, with explicit budgets and authority boundaries to prevent uncontrolled agent sprawl.

## Two-Explosion Coupling

Real-world services often require two structured expansions at once. External requirements expand into a service tree, and local DRS/private slots expand into a source tree. For example, a tax, airline, or government needle may declare required external slots while Local DRS exposes private source slots. Root validates a sealed mapping from local slots to verified external slots. An LLM may reason over schema, mapping, and policy without seeing raw private values. Commit remains Root-authorized.

## Needles Are Contracts, Not Plugins

Needles are declarative, auditable execution and meaning contracts. A needle may declare owner, version, signature, capabilities, allowed and forbidden actions, schemas, validators, TTL, trust, endpoints, permission model, rollback policy, and failure policy. Loading a needle does not grant sovereignty; it only makes bounded capabilities available to Root-controlled routing and validation.

## Canonical Needle Topology

Needles are contract modules and capability boundaries, not Executor-owned plugins. A needle may be Root-visible, cluster-local, or branch-bound. An Executor or runtime port may call a permitted bounded needle capability, but it does not own the needle and cannot grant it authority.

Loading a needle does not grant sovereignty. If a needle-local Orchestrator exists, it is local to that needle or fractal cell; it is not global Root. Needle outcomes pass through the canonical execution pipeline:

```text
NeedleExecutionResult / bounded capability output
-> ResultProposal
-> Post V&V
-> GT / Root decision
-> DRS / audit / quarantine / writeback
```

Executor may call a permitted needle capability, but Root owns authority. Needle output must not bypass Post V&V, GT, Root commit, audit, DRS writeback, or quarantine policy.

Marennya and UP are built-in systemic/internal needles, not ordinary external action needles. Marennya is a reflective/internal-improvement needle. UP is a transfer/cross-domain-opportunity needle. Future systemic needle classes may include action, data, device, validator, reflective, transfer, scheduler, policy/governance, and memory-evolution/GT needles.

The current NeedleRuntime Failure Integration is a demo-level adapter. It proves `NeedleExecutionResult` can become ResultProposal-compatible and Post V&V-visible. It does not yet prove full Root-level needle planning, AVF selection, DRS quarantine writeback, or production external API execution.

## DRS Is Not Just Memory

DRS stores task outcomes, provenance, trust, failures, dead ends, reusable patterns, external pointers, quarantine, and TimeEnvelope-bearing records. Retrieval must be temporal and time-aware through TemporalQuery. DRS is not merely vector recall or chatbot memory; it is a layered reflexive store for what happened, when it was valid, who produced it, how much it is trusted, and whether it can safely influence future runs.

## What This Demo Proves

- Root-controlled pipeline from event intake to final output.
- Contract-based runtime using JSON Schemas and typed Python helpers.
- Memory-first DRS retrieval before planning.
- Pointer-first DRS model with local JSON storage for MVP records.
- AVF pre-planning field for deterministic CandidateVector scoring.
- Hard forbidden vector blocking before Architect sees the candidates.
- GT-based result selection using deterministic payoff.
- Root-only FinalOutput creation.
- DRS writeback into Work with TimeEnvelope.
- Marennya and UP quarantine hooks after task completion.
- Cold start vs memory-informed second run behavior.

## Observable Zero Trust Runtime Proof

The main auditor-facing proof is:

```bash
python -m demo.run_canonical_pipeline_trace
```

This trace shows the canonical Root-controlled runtime boundary by boundary: RootOrchestrator authority, explicit Orchestrator-stage / Route Assembly, CandidateVectors from allowed sources only, AVF / HardMask / SoftMask before Architect, AttractorPacket created by RootOrchestrator, Architect receiving AttractorPacket only, Architect returning PlanGraph, the Fractal DAG Executor Core running that PlanGraph, Executor returning ResultProposals only, Post V&V before GT, GT selecting without committing, artifacts returning upward to RootOrchestrator, RootOrchestrator creating FinalOutput, and DRS writeback / audit. It also shows no real external actions and no uncontrolled delegation.

This is not a chatbot demo and not a LangChain-style agent chain. It is an observable role-bounded runtime trace where every authority boundary is visible. The DAG runner connects to the Root-controlled pipeline after Architect: it executes Architect PlanGraph and returns ResultProposals. RootOrchestrator remains the authority and commit boundary; the DAG runner is not Root, does not own execution authority, and does not commit output.

Current limitations: this is a demo-runtime proof, not production OS runtime. The next engineering step is connecting the DAG runner to the Root-controlled pipeline after Architect as a controlled route. Production recursive child-cell execution is not implemented yet. Real external API/needle execution is not enabled here. A live Gemini/SLM Orchestrator variant is a later layer, not the default. `fallback` vs `fallback_template` naming cleanup remains minor backlog.

## Strategic Expansion Map

Long-term vision beyond the MVP is documented separately in:

```text
docs/strategic_expansion_map.md

## What This Demo Is Not

- Not a chatbot.
- Not a Telegram bot.
- Not a LangChain clone.
- Not using real government APIs.
- Not storing secrets.
- Not using real identity, payment, or passport data.
- Not enabling direct reuse by default.
- Not implementing distributed external DRS yet.

## Architecture Pipeline

```text
User/Event
→ RootOrchestrator
→ Intent / TemporalQuery
→ LocalDRS retrieval
→ CandidateVectors
→ AVF
→ AttractorPacket
→ Architect
→ PlanGraph
→ Executor
→ ResultProposals
→ Post V&V
→ GTValidator
→ Root FinalOutput
→ DRS writeback
→ Marennya / UP quarantine hooks
```

## Adaptive Execution Routing

The full pipeline is the maximum cognitive loop, not the default path for every action. Simple, frequent, low-risk requests should route to cheap deterministic needles or validated reuse when policy allows. Novel, ambiguous, risky, conflicting, high-value, or multi-branch tasks can use deeper AVF, Architect, Executor, Post V&V, and GT processing.

DRS, AVF, needles, cached protocols, and reuse gates are compute-saving mechanisms. They are meant to reduce unnecessary expensive LLM/SLM usage by making those calls later, less often, and with narrower context. Direct reuse is not the default path; it is available only through an explicit shortcut mode. A future `ExecutionModeRouter` must choose the cheapest safe level while preserving policy, permission, audit, and DRS writeback rules.

## Execution Modes

- L0 deterministic reflex: mock, permission-gated, and disabled unless Root explicitly allows it.
- L1 direct reuse: gated shortcut through explicit Root permission and ReuseGate eligibility.
- L2 context-only: memory-informed execution where prior records shape context but do not bypass planning.
- L3/L4 full pipeline: AVF -> Architect -> Executor -> Post V&V -> GT for tasks that need planning, validation, and selection.
- L5 deferred reflection: Marennya/UP quarantine hooks and later validation outside the immediate response path.

## Demo Scenarios

The default CLI demo scenarios run in `proof_full_pipeline` mode by design. They do not silently choose `L0 deterministic_reflex` or `L1 direct_reuse`, even if cheaper modes are documented. This does not contradict adaptive runtime: v0.25 is a test/proof mode for the baseline pipeline, while adaptive routing is future production behavior.

`cold_start` runs the mock certificate request with no previous Work record in the LocalDRS. The trace shows `memory_context_applied=false`, `reuse_decision=none`, and `reuse_applied=false`.

`reuse` runs two certificate requests against the same LocalDRS path. The second run sees the previous Work record and reports `memory_context_applied=true`, `reuse_decision=context_only`, and `reuse_applied=false`.

ReuseGate evaluates prior DRS records after TemporalQuery retrieval. It computes `freshness`, `gt_trust`, `policy`, `conflict`, and `reuse_score`, then returns one of `none`, `context_only`, or `direct_reuse_candidate`.

`direct_reuse_candidate` means a record passed the scoring gates. It is not actual direct reuse unless Root is called with explicit direct reuse permission. The `direct_reuse` CLI scenario demonstrates that optional `RootFinalFromReuse` path: it skips Architect and Executor, keeps Root-only FinalOutput, writes a new Work DRS record, and does not call LLMs or external APIs.

## Install And Run

```bash
python3 -m venv .venv
source .venv/bin/activate
python -m pip install --upgrade pip
python -m pip install -e .
```

Run the focused MVP test suite:

```bash
python -m pytest tests/test_schema_files_valid.py \
  tests/test_needles_valid.py \
  tests/test_time_model.py \
  tests/test_candidate_vectors.py \
  tests/test_avf_runtime.py \
  tests/test_architect_runtime.py \
  tests/test_executor_runtime.py \
  tests/test_post_vv_runtime.py \
  tests/test_gt_validator_runtime.py \
  tests/test_drs_runtime.py \
  tests/test_root_orchestrator_runtime.py \
  tests/test_marenna_up_runtime.py \
  tests/test_demo_certificate_runner.py
```

Run the CLI demo:

```bash
python -m demo.run_certificate_demo --scenario cold_start
python -m demo.run_certificate_demo --scenario reuse
python -m demo.run_certificate_demo --scenario direct_reuse
```

## Expected Output

The exact proposal ids are deterministic but verbose. The important parts should look like this:

```text
Scenario: cold_start
run:
  illegal_coercion blocked: true
  GT winner vector id: official_online_request
  FinalOutput created_by: root_orchestrator
```

```text
Scenario: reuse
second_run:
  memory_context_applied: true
  reuse_decision: context_only
  reuse_applied: false
  illegal_coercion blocked: true
  GT winner vector id: official_online_request
  FinalOutput created_by: root_orchestrator
```

```text
Scenario: direct_reuse
run:
  memory_context_applied: true
  reuse_decision: direct_reuse
  reuse_applied: true
  architect_skipped: true
  executor_skipped: true
  FinalOutput created_by: root_orchestrator
  FinalOutput status: success
```

## Repository Map

- `specs/` contains the human-readable passport, invariants, demo scenario, legacy mapping, math appendix, and machine manifest.
- `schemas/` contains JSON Schema contracts for runtime objects such as TimeEnvelope, CandidateVector, AttractorPacket, PlanGraph, ResultProposal, VVReport, GTReport, DRSRecord, Marennya, UP, and FinalOutput.
- `needles/` contains static MVP needle declarations. CandidateVectors currently come from installed needles and fallback templates only.
- `hedgehog/` contains deterministic runtime modules for models, time, LocalDRS, CandidateVector loading, AVF, Architect, Executor, Post V&V, GTValidator, RootOrchestrator, Marennya, and UP.
- `demo/` contains the CLI certificate demo.
- `tests/` contains focused contract and runtime tests for the MVP pipeline.
- `data/drs/` is the local DRS layer layout for Work, Thoughts, UP, Quarantine, and DeadEnds.
- `docs/` contains strategic and auditor-facing documents, including the long-term expansion map. Vision documents in this folder are not implementation tasks unless explicitly promoted into the roadmap.

## Current MVP Limitations

The MVP proves core runtime invariants, not production-scale resilience.

- Deterministic stubs only.
- Local JSON DRS only.
- ReuseGate scoring exists; direct reuse is implemented only as an explicit optional CLI/test scenario, not as the default path.
- No pointer resolution yet.
- No real APIs.
- No UI.
- Telegram shell and smoke runners are interface adapters only, not production bot infrastructure.

## Current Implementation Checkpoint

The current implementation chain includes:

```text
Intent Matrix
-> Shadow Orchestrator
-> Route Validator
-> Guard Completeness
-> Integration Gate
-> Controlled Runtime Prototype
```

The prototype allows Orchestrator proposals to influence Root execution only after validator and gate approval. `controlled_orchestrator_enabled` remains `prototype_only`; this is not production uncontrolled runtime.

This checkpoint is retained as the controlled-orchestrator lineage. The current auditor-facing runtime proof is `demo.run_canonical_pipeline_trace`.

## Known Production Risks And Planned Hardening

### Large Graph Scaling

Risk: flat PlanGraph execution does not scale to thousands of nodes.

Mitigation: bounded fractal subgraphs, branch budgets, `max_plan_nodes`, `max_edges`, `max_depth`, `max_parallelism`, boundary snapshots, and top-level GT over branch summaries or ResultProposals rather than raw nodes.

Future tests: oversized graph rejection, subgraph boundary limits, and proof that GT does not score 10k raw nodes as one flat list.

### Needle Chaos

Risk: external needles may timeout, change contracts, return invalid JSON, or fail.

Mitigation: a NeedleRuntime with timeout policy, retries, circuit breakers, contract versioning, schema validation, invalid JSON quarantine, permission gates, health scoring, degraded mode, and audit. Failed needles must produce blocked or failed ResultProposals, not crash Root.

Future tests: needle timeout, invalid JSON quarantine, version mismatch, circuit breaker behavior, and parallel needle failure.

### Cold Start

Risk: empty DRS increases cost and lowers reuse.

Mitigation: installed needles, fallback templates, controlled exploration, low history confidence, strict budgets, and mandatory DRS writeback. Repeated tasks should converge toward memory-informed or direct-reuse behavior when trust and policy allow.

Future tests: empty DRS vector generation, fallback template use, first-run writeback, second-run memory influence, and direct reuse convergence.

## Roadmap

- Controlled Runtime Trace Visibility.
- Live Controlled Smoke for safe certificate-demo.
- Cold Start Benchmark v0.1.
- NeedleRuntime Chaos Layer.
- Large Graph Stress Layer.
- Adaptive mode router that chooses direct reuse only when policy, permission, and tests allow it.
- Richer DRS pointer resolution.
- Marennya validation and promotion.
- UP validation and promotion.
- Telegram shell as interface only.
- External DRS pointer protocol.
- Stronger GT/TTL math.

## Safety / Privacy Note

DRS is pointer-first. Secrets, credentials, passport numbers, card data, tokens, passwords, and private keys must not be stored directly in DRS content. MVP inline content is local, mock, non-secret only.
Future production versions should use a Credential Vault / sealed secret slots. DRS may store secret references, scopes, provenance, and audit metadata, but not raw secret values.
