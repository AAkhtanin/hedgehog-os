# Hedgehog OS MVP Invariants

These invariants are non-negotiable for the proof-of-architecture demo.

Document hierarchy:

- specs/human_passport_v0_25.md defines MVP architecture and invariants.
- specs/math_appendix_v0_3.md defines formulas and algorithmic details.
- docs/strategic_expansion_map.md is vision-only and not an implementation sprint.
- If documents conflict for current MVP implementation, the Human Passport controls.

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

Fractal DAG Executor invariant:

- Fractal DAG Executor runs after Architect returns PlanGraph.
- It computes ready sets, respects dependencies, parallelism, and budget limits.
- It may produce ResultProposal-shaped outputs and child boundary snapshots.
- It must not create FinalOutput.
- It must not perform global commit.
- Non-atomic nodes must return boundary artifacts, not uncontrolled recursion.
- The DAG runner is part of the Root-controlled pipeline, but it is not Root.

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
