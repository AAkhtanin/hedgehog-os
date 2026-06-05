# Hedgehog OS Demo — Fractal Reflexive Runtime MVP

This repository demonstrates an AI OS-style runtime pipeline using deterministic Python stubs, JSON contracts, DRS memory routing, AVF scoring, GT selection, Fractal DAG execution, and Root-only final output.

It is not a chatbot, not an agent chain, not a LangChain clone, and not a UI project.

The current MVP is a proof-of-architecture runtime for a future AI OS, centered on a mock government certificate request.

---

## What Hedgehog OS Is

Hedgehog OS / Fractal Reflexive OS is a fractal controlled-runtime topology for role-bounded intelligence.

LLM/SLM components are cognitive organs inside bounded roles, not sovereign actors. Subordinate intelligence can propose routes, plans, drafts, or results, but Root commits.

The architecture is based on:

- fractal authority topology;
- Root-only commit;
- non-transitive delegation;
- time-aware memory;
- controlled candidate vectors;
- AVF before Architect;
- AttractorPacket boundary;
- PlanGraph execution;
- Post V&V before GT;
- DRS writeback and audit.

Core authority principle:

text the vassal of my vassal is not my vassal 

A delegated subcell may manage its own bounded local authority, but that authority does not automatically propagate upward, sideways, or outward.

---

## What Hedgehog OS Is Not

Hedgehog OS is not merely:

- an agent framework;
- a plugin wrapper;
- a LangChain-like workflow engine;
- a chatbot memory system;
- a simple guardrail layer;
- an autonomous agent wrapper.

Needles are executable meaning contracts, not plugins.

DRS is a time/provenance/trust topology, not ordinary vector memory.

AVF runs before planning.

Architect is bounded by AttractorPacket.

Executors return ResultProposal only.

Post V&V runs before GT.

GT selects stability/payoff, not truth.

FinalOutput is created only by Root.

---

## Core Authority Invariants

- Root is final authority and the only creator of FinalOutput.
- Orchestrator-stage may route/frame/assemble the task field, but must not create FinalOutput.
- Architect creates PlanGraph from AttractorPacket, but does not answer the user.
- Fractal DAG Executor executes Architect PlanGraph and returns ResultProposal-shaped artifacts / boundary snapshots.
- DAG runner is not Root and does not commit output.
- Node-level Executors return ResultProposal only.
- Post V&V validates proposals before GT.
- GT selects/stabilizes under payoff and policy constraints, but does not commit.
- Results return upward to Root.
- Root creates FinalOutput and performs Work DRS writeback.

---

## Controlled Expansion, Not Only Narrowing

Hedgehog OS is not just narrowing like an Akinator.

Large intent should expand into bounded candidate branches and fractal cells, then be constrained by AVF, HardMask, GT, and Root commit.

The goal is organized complexity: enough branching to represent the real task, with explicit budgets and authority boundaries to prevent uncontrolled agent sprawl.

---

## Two-Explosion Coupling

Real-world services often require two structured expansions at once.

External requirements expand into a service tree, and local DRS/private slots expand into a source tree.

For example, a tax, airline, or government needle may declare required external slots while Local DRS exposes private source slots.

Root validates a sealed mapping from local slots to verified external slots.

An LLM may reason over schema, mapping, and policy without seeing raw private values.

Commit remains Root-authorized.

---

## Needles Are Contracts, Not Plugins

Needles are declarative, auditable execution and meaning contracts.

A needle may declare:

- owner;
- version;
- signature;
- capabilities;
- allowed and forbidden actions;
- schemas;
- validators;
- TTL;
- trust;
- endpoints;
- permission model;
- rollback policy;
- failure policy.

Loading a needle does not grant sovereignty.

It only makes bounded capabilities available to Root-controlled routing and validation.

---

## Canonical Needle Topology

Needles are contract modules and capability boundaries, not Executor-owned plugins.

A needle may be:

- Root-visible;
- cluster-local;
- branch-bound;
- systemic/internal.

An Executor or runtime port may call a permitted bounded needle capability, but it does not own the needle and cannot grant it authority.

Loading a needle does not grant sovereignty.

If a needle-local Orchestrator exists, it is local to that needle or fractal cell. It is not global Root.

Needle outcomes pass through the canonical execution pipeline:

text NeedleExecutionResult / bounded capability output -> ResultProposal-compatible artifact / QuarantineRecord -> Post V&V -> GT / Root decision -> DRS / audit / quarantine / writeback 

Executor may call a permitted needle capability, but Root owns authority.

Needle output must not bypass Post V&V, GT, Root commit, audit, DRS writeback, or quarantine policy.

Marennya and UP are built-in systemic/internal needles, not ordinary external action needles:

- Marennya is a reflective/internal-improvement needle.
- UP is a transfer/cross-domain-opportunity needle.

Future systemic needle classes may include:

- action needles;
- data needles;
- device needles;
- validator needles;
- reflective needles;
- transfer needles;
- scheduler needles;
- policy/governance needles;
- memory-evolution/GT needles.

Systemic/internal needles may contain bounded local fractal cycles, but they must not receive global sovereignty.

The current needle outcome checkpoint proves the local canonical boundary for simulated needle outcomes:

text NeedleRuntime / adapter -> ResultProposal-compatible artifact -> Post V&V -> real GTValidator runtime report -> Root-visible routing semantics -> LocalDRS Work / Quarantine / DeadEnds persistence 

This remains MVP/demo scope. It does not yet prove full Root-level needle planning, AVF selection over live external needles, production external API execution, global DRS, NeedleFactory, marketplace, or Internet-of-Meaning behavior.

---

## DRS Is Not Just Memory

DRS stores:

- task outcomes;
- provenance;
- trust;
- failures;
- dead ends;
- reusable patterns;
- external pointers;
- quarantine;
- TimeEnvelope-bearing records.

Retrieval must be temporal and time-aware through TemporalQuery.

DRS is not merely vector recall or chatbot memory. It is a layered reflexive store for what happened, when it was valid, who produced it, how much it is trusted, and whether it can safely influence future runs.

Current LocalDRS status:

- LocalDRS is the only implemented DRS runtime.
- External DRS remains a future pointer/protocol boundary.
- Global DRS / Internet of Meaning is not implemented.
- DRS records are addressable meaning records with TimeEnvelope, provenance, GT metadata, validation metadata, trace refs, and routing semantics.
- Needle outcomes currently route to Work, Quarantine, or DeadEnds according to V&V/GT-classified outcome semantics.
- Failed, quarantined, degraded, blocked, and dead-end records are not direct-reuse eligible.

---

## What This Demo Proves

- Root-controlled pipeline from event intake to final output.
- Contract-based runtime using JSON Schemas and typed Python helpers.
- Explicit Orchestrator-stage / Route Assembly.
- Memory-first DRS retrieval before planning.
- Pointer-first DRS model with local JSON storage for MVP records.
- AVF pre-planning field for deterministic CandidateVector scoring.
- Hard forbidden vector blocking before Architect sees the candidates.
- Root-created AttractorPacket.
- Architect receives AttractorPacket only and returns PlanGraph.
- Fractal DAG Executor executes PlanGraph dependencies.
- Executors return ResultProposals only.
- Post V&V before GT.
- GT-based result selection using deterministic payoff.
- Artifacts return upward to Root.
- Root-only FinalOutput creation.
- DRS writeback into Work with TimeEnvelope.
- Marennya and UP quarantine hooks after task completion.
- Cold start vs memory-informed second run behavior.
- Explicit direct reuse as a gated optional path.

---

## Observable Zero Trust Runtime Proof

The main auditor-facing proof is:

bash python -m demo.run_canonical_pipeline_trace 

This trace shows the canonical Root-controlled runtime boundary by boundary:

- RootOrchestrator authority;
- explicit Orchestrator-stage / Route Assembly;
- CandidateVectors from allowed sources only;
- AVF / HardMask / SoftMask before Architect;
- AttractorPacket created by RootOrchestrator;
- Architect receiving AttractorPacket only;
- Architect returning PlanGraph;
- Fractal DAG Executor Core running that PlanGraph;
- Executors returning ResultProposals only;
- Post V&V before GT;
- GT selecting without committing;
- artifacts returning upward to RootOrchestrator;
- RootOrchestrator creating FinalOutput;
- DRS writeback / audit;
- no real external actions;
- no uncontrolled delegation.

This is not a chatbot demo and not a LangChain-style agent chain.

It is an observable role-bounded runtime trace where every authority boundary is visible.

Current status: the DAG runner now connects to the Root-controlled pipeline after Architect as an explicit opt-in route. It executes Architect PlanGraph and returns ResultProposals; RootOrchestrator remains the authority and commit boundary.

Next gap: Root-native canonical trace and stabilization of DRS writeback / audit around the root-native path.

Current limitations: this is a demo-runtime proof, not production OS runtime. Production recursive child-cell execution is not implemented yet. Real external API/needle execution is not enabled here. A live Gemini/SLM Orchestrator variant is a later layer, not the default. fallback vs fallback_template naming cleanup remains minor backlog.

---

## Strategic Expansion Map

Long-term vision beyond the MVP is documented separately in:

text docs/strategic_expansion_map.md 

Vision documents are strategic lighthouse documents, not implementation tasks unless explicitly promoted into the current roadmap.

That document describes future expansion toward personal Root/Ghost, NeedleFactory, user-created needles, official organizational needles, DRS sharing, needle markets, enterprise cells, and Internet-of-Meaning scenarios.

---

## What This Demo Is Not

- Not a chatbot.
- Not a Telegram bot.
- Not a LangChain clone.
- Not using real government APIs.
- Not storing secrets.
- Not using real identity, payment, or passport data.
- Not enabling direct reuse by default.
- Not implementing distributed external DRS yet.
- Not implementing global DRS network.
- Not implementing Internet of Meaning.
- Not implementing needle marketplace.
- Not implementing official bank/airline/government needles.
- Not implementing production recursive child-cell execution.
- Not implementing universal natural Telegram assistant behavior.

---

## Architecture Pipeline

text User/Event → RootOrchestrator → Orchestrator-stage / Route Assembly → Intent / TemporalQuery → WorldState → LocalDRS retrieval → CandidateVectors → AVF / HardMask / SoftMask → AttractorPacket → Architect → PlanGraph → Fractal DAG Executor / node-level Executors → ResultProposals → Post V&V → GTValidator → back to Root → Root FinalOutput → DRS writeback / audit → Marennya / UP quarantine hooks 

---

## Adaptive Execution Routing

The full pipeline is the maximum cognitive loop, not the default path for every action.

Simple, frequent, low-risk requests should route to cheap deterministic needles or validated reuse when policy allows.

Novel, ambiguous, risky, conflicting, high-value, or multi-branch tasks can use deeper AVF, Architect, Executor, Post V&V, and GT processing.

DRS, AVF, needles, cached protocols, and reuse gates are compute-saving mechanisms. They are meant to reduce unnecessary expensive LLM/SLM usage by making those calls later, less often, and with narrower context.

Direct reuse is not the default path. It is available only through an explicit shortcut mode.

A future ExecutionModeRouter must choose the cheapest safe level while preserving policy, permission, audit, and DRS writeback rules.

---

## Execution Modes

- L0 deterministic reflex: mock, permission-gated, and disabled unless Root explicitly allows it.
- L1 direct reuse: gated shortcut through explicit Root permission and ReuseGate eligibility.
- L2 context-only: memory-informed execution where prior records shape context but do not bypass planning.
- L3/L4 full pipeline: AVF -> Architect -> Fractal DAG Executor / Executors -> Post V&V -> GT for tasks that need planning, validation, and selection.
- L5 deferred reflection: Marennya/UP quarantine hooks and later validation outside the immediate response path.

---

## Demo Scenarios

The default CLI demo scenarios run in proof_full_pipeline mode by design.

They do not silently choose L0 deterministic_reflex or L1 direct_reuse, even if cheaper modes are documented.

This does not contradict adaptive runtime: v0.25 is a test/proof mode for the baseline pipeline, while adaptive routing is future production behavior.

cold_start runs the mock certificate request with no previous Work record in the LocalDRS. The trace shows memory_context_applied=false, reuse_decision=none, and reuse_applied=false.

reuse runs two certificate requests against the same LocalDRS path. The second run sees the previous Work record and reports memory_context_applied=true, reuse_decision=context_only, and reuse_applied=false.

ReuseGate evaluates prior DRS records after TemporalQuery retrieval. It computes freshness, gt_trust, policy, conflict, and reuse_score, then returns one of none, context_only, or direct_reuse_candidate.

direct_reuse_candidate means a record passed the scoring gates. It is not actual direct reuse unless Root is called with explicit direct reuse permission.

The direct_reuse CLI scenario demonstrates that optional RootFinalFromReuse path: it skips Architect and Executor/DAG, keeps Root-only FinalOutput, writes a new Work DRS record, and does not call LLMs or external APIs.

---

## Install And Run

bash python3 -m venv .venv source .venv/bin/activate python -m pip install --upgrade pip python -m pip install -e . 

Run the focused MVP test suite:

bash python -m pytest tests/test_schema_files_valid.py \   tests/test_needles_valid.py \   tests/test_time_model.py \   tests/test_candidate_vectors.py \   tests/test_avf_runtime.py \   tests/test_architect_runtime.py \   tests/test_executor_runtime.py \   tests/test_post_vv_runtime.py \   tests/test_gt_validator_runtime.py \   tests/test_drs_runtime.py \   tests/test_root_orchestrator_runtime.py \   tests/test_marenna_up_runtime.py \   tests/test_demo_certificate_runner.py 

Run the CLI demo:

bash python -m demo.run_certificate_demo --scenario cold_start python -m demo.run_certificate_demo --scenario reuse python -m demo.run_certificate_demo --scenario direct_reuse 

Run the canonical pipeline trace:

bash python -m demo.run_canonical_pipeline_trace 

Run the Root DAG integration smoke if present in the current branch:

bash python -m demo.run_root_dag_integration_smoke 

---

## Expected Output

The exact proposal ids are deterministic but verbose. The important parts should look like this:

text Scenario: cold_start run:   illegal_coercion blocked: true   GT winner vector id: official_online_request   FinalOutput created_by: root_orchestrator 

text Scenario: reuse second_run:   memory_context_applied: true   reuse_decision: context_only   reuse_applied: false   illegal_coercion blocked: true   GT winner vector id: official_online_request   FinalOutput created_by: root_orchestrator 

text Scenario: direct_reuse run:   memory_context_applied: true   reuse_decision: direct_reuse   reuse_applied: true   architect_skipped: true   executor_skipped: true   FinalOutput created_by: root_orchestrator   FinalOutput status: success 

---

## Repository Map

- specs/ contains the human-readable passport, invariants, demo scenario, demo baseline, legacy mapping, math appendix, and machine manifest.
- docs/ contains strategic and auditor-facing documents, including the long-term expansion map. Vision documents in this folder are not implementation tasks unless explicitly promoted into the roadmap.
- schemas/ contains JSON Schema contracts for runtime objects such as TimeEnvelope, CandidateVector, AttractorPacket, PlanGraph, ResultProposal, VVReport, GTReport, DRSRecord, Marennya, UP, and FinalOutput.
- needles/ contains static MVP needle declarations. CandidateVectors currently come from installed needles and fallback templates only.
- hedgehog/ contains deterministic runtime modules for models, time, LocalDRS, CandidateVector loading, AVF, Architect, Fractal DAG Executor, Executor, Post V&V, GTValidator, RootOrchestrator, Marennya, and UP.
- demo/ contains CLI demo and trace runners.
- tests/ contains focused contract and runtime tests for the MVP pipeline.
- data/drs/ is the local DRS layer layout for Work, Thoughts, UP, Quarantine, and DeadEnds.

---

## Current MVP Limitations

The MVP proves core runtime invariants, not production-scale resilience.

- Deterministic stubs only.
- Local JSON DRS only.
- ReuseGate scoring exists; direct reuse is implemented only as an explicit optional CLI/test scenario, not as the default path.
- DAG runner integration exists as an explicit controlled/opt-in route; Root-native canonical trace is the next gap if not already committed.
- No production pointer resolution yet.
- No real APIs.
- No UI.
- Telegram shell and smoke runners are interface adapters only, not production bot infrastructure.

---

## Controlled Orchestrator Lineage

The controlled-orchestrator lineage includes:

text Intent Matrix -> Shadow Orchestrator -> Route Validator -> Guard Completeness -> Integration Gate -> Controlled Runtime Prototype 

This lineage proves that Orchestrator proposals may influence Root execution only after validator and gate approval.

controlled_orchestrator_enabled remains prototype_only.

This is not production uncontrolled runtime.

---

## Current Implementation Checkpoint

Current auditor-facing / runtime checkpoint:

text Observable Zero Trust Runtime proof -> Fractal DAG Executor Core -> Canonical Pipeline Trace -> Explicit Orchestrator / AVF / Attractor Formation -> Root-controlled DAG runner integration -> Root-native DAG/DRS/audit stabilization -> Canonical Needle Outcome Trace -> real GTValidator integration for needle outcomes -> Needle Outcome DRS Routing Persistence v0.1 -> Large Graph / Bounded Fractal Stress v0.1 -> DRS Graph Proximity / Lineage v0.1 -> Chaos Survival Showcase v0.1 -> Compute Collapse via DRS Reuse v0.1 -> DRS Layer Taxonomy v0.1 -> Typed DRS Lineage Edges v0.1 -> ReuseScore v0.1 -> Semantic Reuse Pipeline Integration v0.1 -> Root-controlled Semantic Reuse Decision Trace v0.1 -> Root-controlled Semantic Reuse Gate Trace v0.1 -> Root-controlled Semantic Reuse Final Decision Trace v0.1 -> Semantic Reuse Authority Stack Audit Pack v0.1 -> Root-native Semantic Reuse E2E Trace v0.1 -> Root-native Full Canonical E2E Trace v0.1 -> Optional Live Gemini Architect Smoke v0.1 -> Ordered Live Gemini Orchestrator->Architect Smoke v0.1 -> Controlled Orchestrator Matrix Gate v0.1 -> AVF / Attractor Formation from accepted Matrix v0.1

The important current rule:

text DAG runner connects to the Root-controlled pipeline after Architect. DAG runner executes Architect PlanGraph. DAG runner returns ResultProposals / boundary artifacts. DAG runner is not Root. DAG runner does not commit output. RootOrchestrator remains final authority. 

Needle outcome routing now proves the local path from simulated NeedleRuntime output through Post V&V, real GTValidator runtime, Root-visible routing semantics, and LocalDRS persistence. Completed accepted outcomes may become Work/task_outcome records. invalid_json, schema_validation_failed, and unknown_exception route to Quarantine. contract_version_mismatch and circuit_breaker_open route to DeadEnds / blocked traces. timeout is a degraded trace, not successful Work. permission_required is needs_user / blocked trace, not a completed action.

Large Graph / Bounded Fractal Stress proves bounded behavior for oversized or malformed PlanGraphs. It demonstrates max_nodes, max_edges, max_depth, max_parallelism, cycle detection, unknown dependency detection, child boundary snapshots, and bounded GT candidate summaries. It does not prove production 10k-node execution. The stress runner does not call the real GT runtime; it proves the GT boundary / bounded summary behavior with `gt_runtime_called: false` and `gt_boundary_mode: bounded_summary_check`. The raw large graph is not sent to GT. The DAG runner remains after Architect, does not become Root, and Executor does not create FinalOutput.

DRS Graph Proximity / Lineage proves a LocalDRS-only read-only retrieval/ranking signal. Records are written to and read from LocalDRS, store links through lineage/source refs, and do not store static `hops_ago`, `hop_distance`, or `graph_distance`. `graph_distance` is computed at query time, and `graph_proximity = 2 ** (-distance / hop_half_life)`. GraphProximity is only a ranking signal: it does not override policy, does not change ReuseGate, and does not make Quarantine, DeadEnds, blocked, failed, or degraded records direct-reuse eligible.

Chaos Survival Showcase v0.1 is an auditor-facing evidence aggregator, not a new core runtime layer. It composes NeedleRuntime Chaos, Canonical Needle Outcome Trace with real GTValidator integration, Needle Outcome DRS Routing Persistence, Large Graph / Bounded Fractal Stress, and DRS Graph Proximity / Lineage into one report. It shows timeout containment, invalid_json and schema_validation_failed quarantine, unknown_exception containment, permission_required needs_user/blocking, circuit breaker blocking, unsafe reuse candidates = 0, bad outcomes written to successful Work = 0, oversized/cycle/unknown-dependency graph blocking, raw large graph not sent to GT, graph proximity not overriding policy, Root final authority, no Executor/needle FinalOutput, no GT commit, no live Gemini, no Telegram action, no real external action, and `production_autonomy_claimed: false`. The showcase PASS summary is derived from computed section predicates, not hardcoded.

Compute Collapse via DRS Reuse v0.1 complements Chaos Survival: Chaos Survival demonstrates resilience / safety / containment, while Compute Collapse demonstrates efficiency / reuse / zero re-planning path. It is an auditor-facing evidence aggregator over existing deterministic cold-start, Root direct reuse, LocalDRS, ReuseGate, and unsafe DRS routing proofs. It shows four scenarios: cold_start_full_pipeline runs Architect, Executor, Post V&V, GT, Root FinalOutput, and DRS writeback with direct_reuse_applied=false; memory_context_only applies memory context but does not fake direct reuse or skip Architect/Executor; eligible_direct_reuse applies direct reuse, skips Architect and Executor/DAG, sources from eligible Work, and still returns through Root; unsafe_records_not_reused keeps Quarantine, DeadEnds, failed, blocked, and degraded records out of direct reuse with direct_reuse_unsafe_candidates=0. Compute units are illustrative deterministic units derived from route flags, not real token billing; savings_ratio is computed from those units. This proof must not be described as absolute zero cost, real token savings proven, or a production billing benchmark.

DRS Layer Taxonomy v0.1 is an engineering hardening layer, not a showcase. It adds LocalDRS taxonomy/reporting semantics without a schema refactor, without changing ReuseGate behavior, and without making unsafe records reusable. It clarifies the broad MVP DeadEnds semantics into explicit routing meanings: work_candidate / successful_work is the only direct-reuse eligible case; quarantine covers invalid_json, schema_validation_failed, and unknown_exception / failed payloads; dead_end marks stable bad routes such as contract_version_mismatch / contract_boundary; blocked_trace marks guard, policy, permission boundary, circuit breaker, or runtime safety blocks; degraded_trace marks timeout, partial failure, or service instability and is not successful Work; needs_user_trace marks permission_required or missing human input and is not completed action. The taxonomy does not override policy: direct_reuse_eligible remains true only for accepted successful Work, unsafe_direct_reuse_candidates remains 0, local_drs_only remains true, external/global DRS are not implemented, and schema_refactor_performed remains false. Its truth flags are derived from classified rows, not hardcoded.

Typed DRS Lineage Edges v0.1 is the next hardening layer after taxonomy. It is a LocalDRS-only typed-edge proof, not a schema refactor, not a ReuseGate change, not ReuseScore, not ConflictCheck, and not global/external DRS. It distinguishes query-time record relationships: derived_from, same_trace, warns_against, blocked_by_policy, requires_user, degraded_from, supports, and contradicts. Typed edges are semantic signals only: supports and derived_from may contribute positive or lineage evidence but cannot make a target directly reusable by themselves; warns_against is warning evidence; blocked_by_policy is blocking evidence; requires_user is needs-user evidence; degraded_from is degradation evidence; contradicts is contradiction evidence. In v0.1 contradiction evidence does not auto-block the target; the contradiction source is not reused and the target requires future ConflictCheck / ReuseScore handling. Records do not store static hops_ago, hop_distance, or graph_distance; graph distance and typed interpretation are computed at query time. Typed edges do not override policy, direct reuse policy remains unchanged, ReuseScore_implemented=false, conflict_check_implemented=false, local_drs_only=true, external/global DRS are not implemented, and schema_refactor_performed=false.

ReuseScore v0.1 is the next completed engineering hardening layer. It is a LocalDRS-only advisory/ranking proof that consumes Typed DRS Lineage Edges candidates and computes deterministic illustrative scores from visible components: quality, freshness, gt_trust, semantic_similarity, graph_proximity, typed_positive_signal, warning_penalty, blocking_penalty, needs_user_penalty, degraded_penalty, contradiction_penalty, and risk_penalty. Raw scores are computed first; policy gates are applied separately afterward. ReuseScore is not Root, not ReuseGate, not a policy override, not production ConflictCheck, not global/external DRS, not real token billing, and not production autonomy. High score cannot override policy: direct reuse still requires eligible successful Work; context memory is not direct reuse; Quarantine, dead_end, blocked_trace, degraded_trace, and needs_user_trace records are not direct-reuse candidates. Contradiction does not auto-reuse: a work_candidate with contradiction_penalty becomes needs_conflict_check, not direct_reuse. The proof includes a high-ish scoring unsafe blocked_trace that remains not reusable because policy_allowed=false, and unsafe_direct_reuse_candidates remains 0.

Semantic Reuse Pipeline Integration v0.1 is the next completed engineering integration proof. It connects the completed LocalDRS semantic stack as one bounded proof: LocalDRS retrieval -> taxonomy-aware filtering -> typed edge interpretation -> graph proximity -> ReuseScore -> ReuseGate / Root boundary -> direct reuse candidate or full pipeline fallback. It is not production RootOrchestrator integration, production autonomy, global DRS, external DRS, a ReuseGate replacement, a Root bypass, direct reuse execution, FinalOutput creation, real external action, live Gemini, or Telegram action. It structurally consumes `collect_reuse_score()`, preserves the source Typed DRS Lineage Edges report, evaluates scenario rows, and separates recommendations from authority. All six stages pass: local_drs_retrieval, taxonomy_filtering, typed_edge_interpretation, graph_proximity, reuse_score, and reuse_gate_root_boundary. Scenario proofs include eligible_direct_reuse_candidate recommended but not committed, context_memory_not_reuse falling back to full pipeline, contradiction_needs_conflict_check, high_score_blocked_by_policy, quarantine_not_reused, needs_user_not_completed_action, degraded_not_stable_success, and dead_end_not_reused. `semantic_pipeline_committed_final_output=false`, `semantic_pipeline_bypassed_root=false`, `semantic_pipeline_bypassed_reuse_gate=false`, `unsafe_reuse_candidates=0`, and PASS is derived from stages, scenarios, and boundary facts.

Root-controlled Semantic Reuse Decision Trace v0.1 is a deterministic Root-controlled dry-run proof. It consumes Semantic Reuse Pipeline recommendations, does not change production RootOrchestrator behavior, does not execute direct reuse, does not create production FinalOutput, does not write production Work records, and does not grant authority to the semantic pipeline. Root classifies recommendations into controlled decisions: direct_reuse_candidate -> root_accepts_direct_reuse_candidate_for_gate_review; needs_full_pipeline -> root_selects_full_pipeline_fallback; needs_conflict_check -> root_requires_conflict_check; blocked -> root_blocks_policy_blocked_route; quarantine -> root_routes_to_quarantine; needs_user -> root_requires_user_input; degraded -> root_marks_degraded_trace; dead_end -> root_rejects_dead_end. ReuseGate remains required for direct reuse candidate review, and the trace still does not execute production direct reuse or create production FinalOutput.

Root-controlled Semantic Reuse Gate Trace v0.1 is a deterministic Root/ReuseGate dry-run proof. It consumes the Root Semantic Reuse Decision Trace, performs gate review only for the Root-approved direct reuse candidate, and keeps all other routes non-gate routes: full pipeline fallback, conflict check required, policy blocked, quarantine, needs_user, degraded, and dead_end. `gate_review_accepts_candidate_for_root_final_decision` means the candidate returns upward to Root; it is not production execution. ReuseGate does not create FinalOutput, does not execute direct reuse, semantic pipeline does not commit, and Root remains final authority. Safety flags include gate_reviews_performed=1, gate_approvals_for_root_final_decision=1, non_applicable_gate_routes=7, root_final_decision_required_for_gate_approval=true, gate_did_not_commit_final_output=true, gate_did_not_execute_direct_reuse=true, direct_reuse_executed_in_trace=false, production_final_output_created=false, unsafe_reuse_candidates=0, root_authority_preserved=true, reuse_gate_boundary_preserved=true, semantic_pipeline_authority_granted=false, local_drs_only=true, external/global DRS not implemented, and production_autonomy_claimed=false.

Root-controlled Semantic Reuse Final Decision Trace v0.1 is a deterministic Root-controlled dry-run proof. It consumes the Root-controlled Semantic Reuse Gate Trace, does not change production RootOrchestrator behavior, does not execute production direct reuse, does not create production FinalOutput, does not perform real external actions, does not write production Work records, and grants no authority to the semantic pipeline or ReuseGate. It creates only a trace-level Root final decision artifact. Final decision mapping is explicit: gate_review_accepts_candidate_for_root_final_decision -> root_final_accepts_controlled_direct_reuse_trace; gate_not_applicable_full_pipeline_fallback -> root_final_selects_full_pipeline_fallback; gate_not_applicable_conflict_check_required -> root_final_requires_conflict_check; gate_not_applicable_policy_blocked -> root_final_blocks_policy_route; gate_not_applicable_quarantine -> root_final_routes_to_quarantine; gate_not_applicable_needs_user -> root_final_requires_user_input; gate_not_applicable_degraded -> root_final_marks_degraded_trace; gate_not_applicable_dead_end -> root_final_rejects_dead_end.

Final Decision Trace safety flags include trace_final_decision_artifacts_created=1, trace_artifacts_created_only_by_root=true, controlled_direct_reuse_trace_accepts=1, production_direct_reuse_executed=false, production_final_output_created=false, production_action_executed=false, production_work_record_written=false, semantic_pipeline_authority_granted=false, reuse_gate_authority_granted=false, unsafe_reuse_candidates=0, root_authority_preserved=true, reuse_gate_boundary_preserved=true, local_drs_only=true, external/global DRS not implemented, and production_autonomy_claimed=false. `root_final_accepts_controlled_direct_reuse_trace` is still trace/dry-run, not production direct reuse execution. The trace final decision artifact is not production FinalOutput.

Root-native Semantic Reuse E2E Trace v0.1 is the first deterministic end-to-end semantic reuse trace. It consumes the Semantic Reuse Authority Stack Audit and shows one connected path from input task -> TemporalQuery -> LocalDRS retrieval -> taxonomy-aware filtering -> typed edge interpretation -> graph proximity -> ReuseScore -> semantic reuse recommendation -> Root decision -> ReuseGate review -> Root final dry-run decision -> trace-level final answer artifact -> audit visibility. It does not change production RootOrchestrator behavior, execute production direct reuse, create production FinalOutput, write production Work records, perform real external actions, use live Gemini, use Telegram actions, or implement global/external DRS.

The selected E2E scenario is `eligible_direct_reuse_candidate`: semantic_pipeline_recommendation=`direct_reuse_candidate`, root_decision=`root_accepts_direct_reuse_candidate_for_gate_review`, reuse_gate_outcome=`gate_review_accepts_candidate_for_root_final_decision`, root_final_decision=`root_final_accepts_controlled_direct_reuse_trace`, artifact_kind=`trace_level_final_answer_artifact`, created_by=`root_orchestrator`, production_final_output=false, production_action_executed=false, and production_work_record_written=false. Semantic pipeline recommends only, ReuseScore remains advisory, Root decides, ReuseGate guards, and Root final trace decides. The trace artifact is not production FinalOutput, controlled direct reuse trace accept is not production direct reuse execution, context memory is not direct reuse, high score does not override policy, contradiction does not auto-reuse, unsafe reuse candidates remain 0, LocalDRS remains local-only, and production autonomy is not claimed.

Proof status for this checkpoint: E2E stages passed=12, focused tests passed=229, full suite passed=749, and the sensitive scan found no secret terms. The semantic reuse chain is: Semantic Reuse Authority Stack Audit -> Root-native Semantic Reuse E2E Trace -> deterministic trace-level final answer artifact -> no production execution.

Root-native Full Canonical E2E Trace v0.1 is now complete. It is a deterministic full canonical E2E proof that composes two paths: first-run canonical Root-controlled execution and second-run semantic reuse authority. The first run shows input task -> Root intake / Orchestrator boundary -> Architect / PlanGraph -> AVF / Attractor formation -> DAG / Executor -> ResultProposals -> Post V&V -> GT -> Root trace artifact -> LocalDRS writeback / audit visibility. The second run shows repeat/similar task -> TemporalQuery -> LocalDRS retrieval -> taxonomy / typed edges / graph proximity -> ReuseScore -> Semantic Pipeline recommendation -> Root decision -> ReuseGate review -> Root final dry-run decision -> trace-level semantic reuse answer artifact.

Full Canonical E2E proof semantics: root_authority_preserved_first_run=true, architect_does_not_answer_user=true, executor_does_not_create_final_output=true, gt_does_not_create_final_output=true, first_run_created_root_trace_artifact=true, first_run_local_drs_writeback_visible=true, first_run_local_work_record_written_in_proof=true, production_external_action_executed=false, second_run_stages_passed=12, selected_scenario=eligible_direct_reuse_candidate, semantic_reuse_path_used=true, second_run_root_authority_preserved=true, reuse_gate_boundary_preserved=true, semantic_pipeline_recommends_only=true, and reuse_score_advisory_only=true. Bridge honesty is explicit: bridge_mode=deterministic_proof_linkage, deterministic_bridge_between_runs=true, production_persistence_claimed=false, production_reuse_claimed=false, and production_reuse_not_executed=true. Local proof DRS writeback is visible, but production persistence and production reuse are not claimed.

Full Canonical E2E safety flags: production_direct_reuse_executed=false, production_final_output_created=false, production_work_record_written=false, production_external_action_executed=false, no_real_external_actions=true, no_live_gemini=true, no_telegram_actions=true, no_global_drs=true, no_external_drs_network=true, and production_autonomy_claimed=false. Proof status: first_run_stages_passed=9, second_run_stages_passed=12, focused tests passed=250, full suite passed=770, sensitive scan found no secret terms, commit=83f59a2 Add Root-native full canonical E2E trace. The MVP now has a deterministic full canonical E2E proof: first-run Root-controlled canonical path -> local proof DRS/audit visibility -> second-run semantic reuse authority path -> Root final dry-run reuse decision -> no production execution.

Optional Live Gemini Architect Smoke v0.1 is complete. It is an opt-in role-substitution smoke proof for the Full Canonical E2E boundary. Gemini may substitute only the Architect proposal role; it does not become Root, Orchestrator, Executor, GT, or FinalRenderer, and it does not create FinalOutput, write DRS, execute actions, or bypass AVF, PlanGraph contract, Executor, Post V&V, GT, Root, ReuseGate, or policy. Default mode is `dry_run_default`, deterministic, network-free, does not call live Gemini, uses `architect_artifact_source=deterministic_mock`, and preserves `plan_graph_contract_checked=true`. Live mode requires explicit `--live`, the `HEDGEHOG_ALLOW_LIVE_GEMINI=1` opt-in gate, and Gemini configuration; missing config reports SKIPPED instead of crashing, and invalid live artifacts are caught, contained, kept away from Executor / Root final output, and fall back visibly to the deterministic Architect.

Architect Smoke boundary checks are derived from the Full Canonical E2E source report, role substitution flags, artifact containment, and context facts. `plan_graph_contract_preserved` derives from `artifact["plan_graph_contract_checked"]`; `executor_boundary_preserved` derives from `not artifact["executor_reached"]`; `root_boundary_preserved` derives from first-run Root authority, second-run Root authority, and no Root final output from live Gemini; and `reuse_gate_boundary_preserved` derives from Full Canonical E2E authority safety. Rendered output does not print credential environment names or secret terms. Proof status: focused tests passed=212, full suite passed=788, sensitive scan found no secret terms, default dry-run smoke status=PASS, `live_gemini_architect_smoke_status=PASS` in default mode, and `ready_for_future_orchestrator_live_smoke=true`.

This smoke is not production RootOrchestrator integration, live Telegram, production autonomy, production persistence, production direct reuse, or a real external action execution path. It does not claim live Gemini was used in default mode. It only proves that the Architect proposal role can be safely substituted inside the existing Full Canonical E2E boundary.

Ordered Live Gemini Orchestrator->Architect Smoke v0.1 is complete. It proves an opt-in ordered role-substitution path: Root boundary -> live Gemini Orchestrator proposal -> schema-backed local validation -> live Gemini Architect proposal -> Architect contract check -> no production execution. The final success evidence is `docs/audit_reports/auditor_live_gemini_ordered_orchestrator_architect_25_success_report.log`.

Final success facts: live Gemini 2.5 acted as valid Orchestrator proposal actor first with orchestrator_initial_attempt_valid=true, orchestrator_active_proposal_source=live_gemini, orchestrator_active_proposal_is_fallback=false, temporal_query_required_value=true, downstream_actors_missing=[], and downstream_actors_extra=[]. Live Gemini then acted as Architect proposal role with architect_artifact_source=live_gemini and architect_artifact_valid=true. production_final_output_created=false, production_external_action_executed=false, Gemini did not write DRS, Gemini did not execute actions, and Gemini did not receive Root authority.

Older ordered Gemini live reports are historical fallback/safety evidence, not final dual-live success proof. They show invalid live Orchestrator output is caught, invalid Orchestrator does not reach Architect / Executor / Root final, deterministic fallback is used safely, and Root boundaries are preserved. This checkpoint is not production RootOrchestrator integration, production autonomy, live Telegram, production persistence, production direct reuse, real external action execution, global DRS, or external DRS. It does not activate Marennya / UP; those remain deferred quarantine-first hooks and are not invoked by live Gemini smoke by default.

Controlled Orchestrator Matrix Gate v0.1 is complete. It is a deterministic Root-controlled gate proof: an Orchestrator matrix is an input artifact, not authority. The Root-controlled gate creates RootMatrixGateDecision artifacts and may accept, reject, or downgrade a matrix. `accept` means a valid matrix may become future AVF input; `reject` means an unsafe or invalid matrix cannot continue; `downgrade` means a partially usable matrix may continue only with unsafe or incomplete claims removed. This is narrow gate evidence, not full RootOrchestrator production integration, AVF / Attractor formation, production autonomy, live Telegram, real external action execution, production persistence, production direct reuse, global DRS, or external DRS.

The gate verifies seven scenarios: valid_matrix_accept is accepted with accepted_for_future_avf=true and root_gate_reason=valid_matrix; missing_temporal_query_reject is rejected with missing_or_false_temporal_query; incomplete_guards_downgrade_or_reject is downgraded with missing guards listed, downgraded_matrix_created=true, and unsafe_claims_removed=true; wrong_downstream_actors_reject is rejected with missing/extra actor diagnostics and renamed actors are not accepted; forbidden_bypass_reject is rejected; high_confidence_policy_block is rejected with high_confidence_overrides_policy=false and policy_beats_orchestrator_confidence=true; fallback_route_visible keeps fallback visible but not executed. Proof status: scenarios_verified=7, accepted_count=1, rejected_count=5, downgraded_count=1, controlled_orchestrator_matrix_gate_status=PASS, focused tests passed=110, full suite passed=859, and sensitive scan found no secret terms.

Evidence: `docs/audit_reports/auditor_controlled_orchestrator_matrix_gate_report.log`. The gate runner verifies the final ordered Gemini 2.5 success report before using it as live-role context: success_report_exists=true, success_report_verified=true, success_report_missing_markers=[], ordered_live_context_mode=success_report_verified, live_orchestrator_can_create_valid_matrix=true, and live_architect_can_create_valid_artifact=true. Boundary semantics remain explicit: AVF, AttractorPacket, Architect, Executor, Post V&V, and GT are not reached in this layer; Orchestrator does not write DRS or create FinalOutput; production_final_output_created=false; production_external_action_executed=false; global/external DRS are not implemented; Marennya / UP are not invoked. Root authority is preserved: root_created_gate_decisions=true, orchestrator_matrix_is_authority=false, root_may_accept=true, root_may_reject=true, root_may_downgrade=true, HardMask future boundary remains visible, and policy beats Orchestrator confidence.

AVF / Attractor Formation from accepted Matrix v0.1 is complete. It is a deterministic AVF / Attractor proof that consumes Controlled Orchestrator Matrix Gate v0.1 and does not hardcode Matrix Gate PASS. It forms AttractorPacket-like artifacts only from accepted or downgraded RootMatrixGateDecision outputs; rejected matrices do not reach AVF and create no AttractorPacket. AVF remains independent, Orchestrator hints are hints rather than commands, HardMask and policy beat Orchestrator confidence, and Root may downgrade or override matrix claims.

Verified behavior: source_matrix_gate_status=PASS; valid_matrix_accept forms an AttractorPacket-like artifact; incomplete_guards_downgrade_or_reject forms a limited artifact with downgraded claims visible; missing_temporal_query_reject, high_confidence_policy_block, forbidden_bypass_reject, and wrong_downstream_actors_reject are blocked before AVF; rejected_matrix_packets=0; rejected_matrices_blocked_before_avf=true. Proof status: avf_attractor_from_accepted_matrix_status=PASS, scenarios_verified=6, attractor_packets_created=2, accepted_matrix_packets=1, downgraded_matrix_packets=1, avf_independent=true, ready_for_architect_from_bounded_attractor_packet=true, focused tests passed=91, full suite passed=880, and sensitive scan found no secret terms.

Evidence: `docs/audit_reports/auditor_avf_attractor_from_accepted_matrix_report.log`. Architect is not invoked in this layer, Executor is not invoked, AVF does not create FinalOutput, write DRS, or execute actions, Orchestrator does not write DRS, no production FinalOutput or external action is created, global/external DRS are not implemented, and Marennya / UP remain deferred. Matrix Gate decides accept / reject / downgrade; AVF receives only accepted/downgraded outputs; full Architect-from-Attractor integration remains next.

Safety rules for this checkpoint:

- Work != Quarantine.
- Work != DeadEnds.
- degraded trace != successful Work.
- permission_required != completed action.
- blocked != success.
- failed/quarantined/degraded/blocked/deadend records are not direct-reuse eligible.
- only accepted completed Work candidate is direct-reuse eligible in this MVP demo.

---

## Known Production Risks And Planned Hardening

### Large Graph Scaling

Risk: flat PlanGraph execution does not scale to thousands of nodes.

Mitigation: bounded fractal subgraphs, branch budgets, max_plan_nodes, max_edges, max_depth, max_parallelism, boundary snapshots, and top-level GT over branch summaries or ResultProposals rather than raw nodes.

Future tests: oversized graph rejection, subgraph boundary limits, and proof that GT does not score 10k raw nodes as one flat list.

Current proof: Large Graph / Bounded Fractal Stress v0.1 blocks or bounds oversized and malformed graphs. It demonstrates bounded summary behavior, not production-scale 10k-node execution and not a real GTValidator call.

### Needle Chaos

Risk: external needles may timeout, change contracts, return invalid JSON, or fail.

Mitigation: a NeedleRuntime with timeout policy, retries, circuit breakers, contract versioning, schema validation, invalid JSON quarantine, permission gates, health scoring, degraded mode, and audit.

Failed needles must produce blocked or failed ResultProposals, not crash Root.

Future tests: needle timeout, invalid JSON quarantine, version mismatch, circuit breaker behavior, and parallel needle failure.

### Cold Start

Risk: empty DRS increases cost and lowers reuse.

Mitigation: installed needles, fallback templates, controlled exploration, low history confidence, strict budgets, and mandatory DRS writeback.

Repeated tasks should converge toward memory-informed or direct-reuse behavior when trust and policy allow.

Future tests: empty DRS vector generation, fallback template use, first-run writeback, second-run memory influence, and direct reuse convergence.

### DRS Graph Proximity / Lineage

Risk: graph-near records could be mistaken for policy permission or direct reuse eligibility.

Mitigation: graph proximity is computed at query time from stored links and remains only one ranking signal. TimeEnvelope, GTTrust, policy, validation, and ReuseGate still dominate. Nearby DeadEnds are warnings, nearby Quarantine records are quarantine signals, and neither is direct-reuse eligible.

Future tests: bidirectional traversal, dedicated policy/invariant layers, advisory ReuseScore, and richer scoring with GraphProximity, GTTrust, Freshness, PolicyOK, and ConflictCheck.

### Chaos Showcase Limits

Risk: an evidence aggregator could be mistaken for production autonomy.

Mitigation: Chaos Survival Showcase v0.1 is explicitly a deterministic presentation layer over existing proof modules. It does not claim global DRS, external DRS, production 10k-node execution, production retrieval, live Gemini autonomy, Telegram automation, or external-action readiness.

Future tests: keep Chaos Survival as evidence aggregation only while adding later runtime-hardening layers such as advisory ReuseScore. Avoid claiming absolute zero cost, production autonomy, or production external-action readiness.

### DRS Layer Taxonomy

Risk: the MVP uses DeadEnds broadly for dead_end, blocked_trace, degraded_trace, and needs_user_trace semantics.

Mitigation: DRS Layer Taxonomy v0.1 now classifies these meanings at routing/report/content semantics level while records may still physically use existing LocalDRS layers such as DeadEnds. A later schema or layer refactor may split DeadEnd / BlockedTrace / DegradedTrace / NeedsUserTrace into dedicated record types or layers if needed.

### Typed DRS Lineage Edges

Risk: generic graph proximity cannot distinguish useful support from warning, policy block, needs-user, degradation, or contradiction signals.

Mitigation: Typed DRS Lineage Edges v0.1 extracts typed edges from persisted record content/source refs and interprets them at query time. The proof distinguishes positive lineage/support from warning, blocked, needs-user, degraded, and contradiction signals, while keeping typed_edges_are_signals_only=true. It does not implement ReuseScore or ConflictCheck, does not drive production ReuseGate, and does not make unsafe records reusable.

### ReuseScore

Risk: an advisory ranking score could be mistaken for Root authority, ReuseGate approval, policy permission, or production ConflictCheck.

Mitigation: ReuseScore v0.1 remains LocalDRS-only and advisory. It combines visible deterministic signals into a raw score, then applies policy gates separately. High score cannot make unsafe records reusable, contradiction sends candidates to needs_conflict_check, Root and ReuseGate authority are preserved, and unsafe_direct_reuse_candidates remains 0. It does not claim real token billing, production retrieval, production autonomy, global DRS, or external DRS.

### Semantic Reuse Pipeline

Risk: a connected semantic reuse proof could be mistaken for production Root integration or an automatic direct-reuse action.

Mitigation: Semantic Reuse Pipeline Integration v0.1 recommends and explains only. It consumes ReuseScore and typed-edge reports, derives stage PASS from collected facts, preserves Root / ReuseGate boundaries, does not commit FinalOutput, does not execute direct reuse, and does not make context memory or unsafe records reusable.

### Root Semantic Reuse Traces

Risk: Root dry-run decisions or gate approvals could be mistaken for production direct reuse execution.

Mitigation: Root-controlled Semantic Reuse Decision Trace v0.1, Gate Trace v0.1, and Final Decision Trace v0.1 remain dry-run proofs. Root classifies recommendations, ReuseGate reviews only the direct reuse candidate, approved candidates return upward to Root, Root creates only a trace-level final decision artifact, and no production direct reuse, production FinalOutput, Work writeback, external action, live Gemini, Telegram action, global DRS, or external DRS is performed.

---

## Roadmap

Completed recent layers:

- Controlled Runtime Trace Visibility.
- Live Controlled Smoke.
- Cold Start Benchmark v0.1.
- NeedleRuntime Chaos Layer.
- Fractal DAG Executor Core.
- Canonical Pipeline Trace.
- Explicit Orchestrator / AVF / Attractor Formation.
- Root-controlled DAG runner integration.
- Root-native DAG/DRS/audit stabilization.
- Canonical Needle Outcome Trace.
- Real GTValidator integration for needle outcomes.
- Needle Outcome DRS Routing Persistence v0.1.
- Large Graph / Bounded Fractal Stress v0.1.
- DRS Graph Proximity / Lineage v0.1.
- Chaos Survival Showcase v0.1.
- Compute Collapse via DRS Reuse v0.1.
- DRS Layer Taxonomy v0.1.
- Typed DRS Lineage Edges v0.1.
- ReuseScore v0.1.
- Semantic Reuse Pipeline Integration v0.1.
- Root-controlled Semantic Reuse Decision Trace v0.1.
- Root-controlled Semantic Reuse Gate Trace v0.1.
- Root-controlled Semantic Reuse Final Decision Trace v0.1.
- Semantic Reuse Authority Stack Audit Pack v0.1.
- Root-native Semantic Reuse E2E Trace v0.1.
- Root-native Full Canonical E2E Trace v0.1.
- Optional Live Gemini Architect Smoke v0.1.
- Ordered Live Gemini Orchestrator->Architect Smoke v0.1.
- Controlled Orchestrator Matrix Gate v0.1.
- AVF / Attractor Formation from accepted Matrix v0.1.
- Strategic Expansion Map.

Next engineering focus:

- Architect from bounded AttractorPacket v0.1. Architect should receive only bounded AVF output, not raw Orchestrator matrix and not raw unchecked user intent. Architect must not receive rejected matrix or raw Orchestrator authority; input must be derived from an AttractorPacket-like artifact. Architect may produce a PlanGraph proposal only, must not create FinalOutput, write DRS, or execute actions, and PlanGraph contract validation must still contain invalid output. No production execution, real external action, or global/external DRS is introduced.
- Split broad DeadEnds routing into future DeadEnd / BlockedTrace / DegradedTrace / NeedsUserTrace layers if schema evolves.
- Add future production ConflictCheck and richer direct reuse scoring only after the semantic reuse integration proof remains policy-bound.
- Add dedicated audit/hash-chain records beyond embedded trace refs.
- Split broad work/trace_summary demo records into a future dedicated policy/invariant layer where appropriate.
- Add bidirectional DRS lineage edge semantics.
- Adaptive mode router hardening.
- Richer DRS pointer resolution.
- Marennya / UP validation and promotion.
- Stronger GT/TTL math.

---

## Safety / Privacy Note

DRS is pointer-first.

Secrets, credentials, passport numbers, card data, tokens, passwords, and private keys must not be stored directly in DRS content.

MVP inline content is local, mock, non-secret only.

Future production versions should use a Credential Vault / sealed secret slots.

DRS may store secret references, scopes, provenance, and audit metadata, but not raw secret values.
