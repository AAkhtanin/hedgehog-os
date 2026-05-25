# Hedgehog OS MVP Invariants

These invariants are non-negotiable for the proof-of-architecture demo.

1. Root-only FinalOutput
   - `FinalOutput` is created only by `RootOrchestrator`.
   - No executor, validator, architect, DRS component, Marennya hook, or UP hook may produce final user-facing output.

Final draft / Root authority invariant:

- `RootOrchestrator` is the only component allowed to create `FinalOutput`.
- Root is the final authority and commit wrapper, not necessarily the strongest prose generator.
- `FinalRenderer` or a future `SynthesisExecutor` may create `FinalDraftProposal` only.
- `FinalDraftProposal` is not `FinalOutput`.
- `FinalDraftProposal` must not write DRS records.
- `FinalDraftProposal` must not perform external actions.
- Root may use, reject, or rewrite a `FinalDraftProposal` before creating `FinalOutput`.
- `FinalOutput.created_by` must remain `root_orchestrator`.
- Renderer-created drafts must remain subordinate artifacts.

2. Executor contract
   - Executors return `ResultProposal` only.
   - Executors may simulate work, report evidence, and surface uncertainty, but they must not finalize.

3. Architect input contract
   - Architect receives `AttractorPacket`, not raw user text.
   - User/event text must pass through intent, world state, DRS retrieval, candidate generation, and AVF first.

4. Architect output contract
   - Architect returns `PlanGraph` and `time_assumptions`.
   - Architect does not return a user-facing answer.

5. DRS time requirement
   - Every `DRSRecord` requires `TimeEnvelope`.
   - A DRS record without `TimeEnvelope` is invalid.

6. DRS retrieval time requirement
   - Every DRS retrieval requires `TemporalQuery`.
   - Retrieval must be explicit about `as_of`, range, freshness bias, and maximum age policy.

DRS registry invariant:

- DRS is a registry/resolver/index, not a raw memory dump.
- MVP LocalDRS may store inline content only as a local simplification.
- Future DRS records should prefer pointer and summary metadata over raw payload.
- Secrets, credentials, passport data, card data, tokens, passwords, and private keys must not be stored directly in `DRSRecord.content`.
- Sensitive data must be referenced through secure vault/storage pointers with explicit access policy.
- Every `DRSRecord` still requires `TimeEnvelope`.
- Every retrieval still requires `TemporalQuery`.
- Work, Thoughts, UP, DeadEnds, and Quarantine layer separation remains mandatory.

7. WorldState relevance
   - `WorldState` must not auto-load irrelevant needles such as weather.
   - Optional context is loaded only when requested by intent, policy, or an applicable installed needle.

8. Memory-first reuse
   - Local memory reuse must be attempted before Architect.
   - Reusable prior records are evaluated through TemporalQuery, CandidateVector generation, and AVF before planning.
   - ReuseGate evaluates prior DRS records after TemporalQuery retrieval.
   - ReuseGate computes `freshness`, `gt_trust`, `policy`, `conflict`, and `reuse_score`.
   - ReuseGate may return `none`, `context_only`, or `direct_reuse_candidate`.
   - `direct_reuse_candidate` is not actual direct reuse by itself.
   - `reuse_applied` remains `false` unless Root is explicitly called with direct reuse enabled.
   - Actual direct reuse requires explicit Root-level shortcut logic and tests proving Architect and Executor were skipped.

Execution routing invariant:

- The full cognitive pipeline must be available, but it is the maximum loop, not the mandatory path for every request.
- An explicit `ExecutionModeRouter` / `ModeRouter` must select the cheapest safe execution mode before choosing pipeline depth.
- Adaptive routing is future production behavior; the v0.25 CLI demo intentionally runs in `proof_full_pipeline` mode.
- In default v0.25 demo mode, `shortcut_disabled_for_demo = true`, `direct_reuse_candidate_only = true`, and `adaptive_routing_future_runtime = true`.
- The default v0.25 demo must not silently choose L0 `deterministic_reflex` or L1 `direct_reuse`; it exercises the full deterministic pipeline to prove contracts and invariants.
- The explicit `direct_reuse` CLI/test scenario may skip Architect and Executor only after ReuseGate eligibility and explicit Root permission.
- Routing must consider intent complexity, risk, novelty, installed needles, DRS candidates, ReuseScore, Freshness, GTTrust, PolicyOK, ConflictCheck, ActionPermission, user confirmation needs, latency/token budget, provenance needs, and whether state or external action will change.
- L0 `deterministic_reflex` may use ready deterministic needles for known safe actions without Architect or heavy LLM, but it still requires policy, permission when actionful, minimal trace/audit, and DRS writeback when state changes or an action was performed.
- L1 `direct_reuse` may use RootFinalFromReuse or direct protocol execution only after explicit gates: ReuseScore, Freshness, GTTrust, PolicyOK, ConflictCheck, TimeEnvelope validity, and ActionPermission when external action is involved.
- L2 `memory_informed_execution` means prior records exist, but shortcut is not allowed; a DRS hit is not direct reuse by itself.
- L3 `avf_architect_execution` uses AVF and Architect for tasks needing planning without full deep branching.
- L4 `full_fractal_reasoning` is reserved for novel, ambiguous, risky, high-value, conflicting, or multi-branch tasks.
- L5 `deferred_reflection` covers Marennya, UP, deep research, idle validation, and scheduled work; it must not block immediate user response unless explicitly requested.
- No DRS retrieval may occur without TemporalQuery in any execution mode.
- L0/L1 paths must not bypass safety, policy, permission, audit, or required DRS writeback.
- A DRS hit only permits `memory_context_applied` by default.
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
- `declared_actions` may enable `deterministic_reflex` or `direct_protocol` routing, but must not bypass Root, permission, policy, audit, or required DRS writeback.
- In MVP, `real_execution_supported` must remain `false` for declared actions.
- Mock execution must not perform real external API calls, device control, purchases, banking, identity, or government actions.
- `proof_full_pipeline` must remain available even if a needle declares `deterministic_reflex` actions.
- Unknown actions must not be executed by the reflex path.

Needle protocol steps invariant:

- `declared_actions` may include `protocol_steps`.
- `protocol_steps` are bounded deterministic mock workflow declarations.
- In MVP every protocol step must be mock-only.
- `protocol_steps` must not perform real external API calls, real device control, real purchases, banking, identity, government actions, or Telegram actions.
- Protocol execution must remain under Root authority and permission policy.
- Protocol execution must produce audit/DRS evidence when action state changes.
- Unknown protocol steps must not execute.

9. CandidateVector sources
   - `CandidateVector` values may come only from installed needles, Local DRS, external DRS pointers, or fallback exploration templates.
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
    - GT v0.1 exposes `candidate_scores`, `winner_payoff`, and `regret_summary`.
    - GT v0.1.1 exposes `tie_detected`, `tie_candidate_ids`, and a deterministic tie-break rule: lower risk, lower cost, higher robustness, higher utility, then deterministic proposal id.
    - Future GT v0.2 must incorporate architecture-aware signals such as `vector_id`, AVF `final_viability`, AVF `soft_mask`, artifact type, execution status, human burden, fallback role, primary path role, risk level, dependency depth, reuse potential, and evidence strength.
    - GT v0.2 must not call LLMs, execute actions, or mutate DRS directly.
    - `fallback_exploration` must not beat safe primary paths only because of lexical proposal id.
    - `illegal_coercion` remains hard-masked and must never enter GT as an executable winner.
    - Marennya and UP may later consume GT v0.2 scores, regret, dominance, and dead-end signals, but GT itself remains a selector, not a truth oracle.

13. GT update rule
    - GTValidator updates `Elo`, `regret`, `half_life`, and/or `decay_rate`, or explicitly returns `no_update`.

14. Quarantine-first mutation
    - Marennya and UP write to Quarantine first.
    - Marennya and UP cannot mutate Work directly.

15. UP default actionability
    - UP is non-actionable by default.
    - UP records require later validation/promotion before they can influence Work.

16. Layer separation
    - Work, Thoughts, UP, DeadEnds, and Quarantine remain separate layers.
    - No component may silently merge or cross-write these layers.
