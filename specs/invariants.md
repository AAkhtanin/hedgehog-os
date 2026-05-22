# Hedgehog OS MVP Invariants

These invariants are non-negotiable for the proof-of-architecture demo.

1. Root-only FinalOutput
   - `FinalOutput` is created only by `RootOrchestrator`.
   - No executor, validator, architect, DRS component, Marennya hook, or UP hook may produce final user-facing output.

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

7. WorldState relevance
   - `WorldState` must not auto-load irrelevant needles such as weather.
   - Optional context is loaded only when requested by intent, policy, or an applicable installed needle.

8. Memory-first reuse
   - Local memory reuse must be attempted before Architect.
   - Reusable prior records are evaluated through TemporalQuery, CandidateVector generation, and AVF before planning.

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
