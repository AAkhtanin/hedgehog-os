# Demo Baseline v0.25

## 1. Purpose

This document defines the current deterministic Hedgehog OS / Fractal Reflexive OS MVP demo baseline.

This is a baseline proof-of-architecture demo, not the final AI OS demo. Its job is to prove that the invariant pipeline exists, runs locally, preserves contracts, and produces auditable trace outputs. It is intentionally small, deterministic, and CLI-driven.

The current runtime uses deterministic Python stubs. Future versions may replace specific roles with LLMs, SLMs, tool-runners, or richer local services, but those replacements must preserve the same contracts and invariants.

## 2. Baseline Pipeline

The v0.25 baseline proves this pipeline:

```text
User/Event
→ RootOrchestrator
→ TemporalQuery
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
→ Marennya/UP quarantine hooks
```

This is the core result of the baseline. The demo is not trying to be useful as a real certificate assistant yet. It is proving that the architecture can be executed end to end without collapsing into a chatbot, generic agent chain, or unstructured prompt loop.

The full pipeline is the maximum cognitive loop, not the mandatory path for every future user action. In the full OS, an `ExecutionModeRouter` / `ModeRouter` must choose the cheapest safe execution depth. Frequent safe actions may use deterministic needles or direct reuse, while novel, risky, ambiguous, conflicting, high-value, or multi-branch tasks may use the full loop.

## 3. Demo Modes

The default v0.25 CLI demo scenarios intentionally run in `proof_full_pipeline` mode.

This means:

- `shortcut_disabled_for_demo = true` for `cold_start` and `reuse`
- `direct_reuse_candidate_only = true` for `cold_start` and `reuse`
- `adaptive_routing_future_runtime = true`

The baseline demo must force the full deterministic pipeline to prove all core contracts. It should not silently choose `L0 deterministic_reflex` or `L1 direct_reuse`, even though those modes are documented as architectural requirements.

This is intentional, not inefficient design. The baseline demo is a proof harness, not production routing policy. It avoids hiding untested components behind shortcut routing. A `direct_reuse_candidate` may be detected by ReuseGate, but Root must still run Architect and Executor unless direct reuse is explicitly enabled.

v0.25 also includes a separate explicit `direct_reuse` CLI/test scenario. That scenario proves the optional RootFinalFromReuse shortcut:

- direct reuse requires explicit Root permission;
- direct reuse requires an eligible ReuseGate decision;
- Architect and Executor are skipped;
- FinalOutput is still created only by RootOrchestrator;
- a new Work DRS writeback and audit trace are still created;
- no LLMs or external APIs are called;
- raw user text and secrets are not stored in DRS.

v0.25 also contains an L0 `deterministic_reflex` proof path. L0 exists only to prove that a cheap, permission-gated execution path can pass through Root without running the full pipeline. It is disabled by default for proof/full pipeline tests, performs no real external action, and should not be expanded further until real needle/interface work begins.

Production runtime may later enable adaptive routing after tests prove each shortcut path is safe.

## 4. Cold Start Expected Behavior

The `cold_start` scenario runs once against an empty LocalDRS.

Expected trace behavior:

- `retrieved_record_count = 0`
- `memory_context_applied = false`
- `reuse_decision = none`
- `reuse_applied = false`
- `illegal_coercion blocked = true`
- `GT winner vector id = official_online_request`
- `FinalOutput created_by = root_orchestrator`

Interpretation:

- Root creates a TemporalQuery before retrieval.
- LocalDRS returns no prior Work records.
- CandidateVectors are loaded from allowed static sources.
- AVF blocks the forbidden `illegal_coercion` vector before Architect.
- Architect receives an AttractorPacket and returns PlanGraph only.
- Executor returns ResultProposals only.
- Post V&V validates the proposals.
- GTValidator selects the strongest deterministic candidate.
- RootOrchestrator alone creates FinalOutput.
- Root writes a Work DRS record with TimeEnvelope.
- Marennya and UP create quarantine records only.

## 5. Reuse Scenario Expected Behavior

The `reuse` scenario runs twice against the same LocalDRS path.

The first run behaves like cold start.

The second run is expected to show:

- `retrieved_record_count >= 1`
- `memory_context_applied = true`
- `reuse_decision = context_only` for ordinary prior records.
- `reuse_applied = false`
- Direct reuse is not applied in this scenario.
- Architect and Executor still run.

Interpretation:

- The second run sees the Work record created by the first run.
- That record becomes memory context.
- The runtime is memory-informed, but it does not bypass planning or execution.
- GT still selects among fresh ResultProposals from the full pipeline.

## 6. ReuseGate Semantics

v0.25 includes a deterministic ReuseGate scoring layer. ReuseGate runs after TemporalQuery retrieval and evaluates prior DRS records before the normal planning pipeline.

ReuseGate computes:

- `freshness`
- `gt_trust`
- `policy`
- `conflict`
- `reuse_score`

ReuseGate may return:

- `none`: no prior records were retrieved.
- `context_only`: records exist, but no record passed the direct reuse scoring gates.
- `direct_reuse_candidate`: a record passed the scoring gates.

`direct_reuse_candidate` is not actual reuse by itself. It means a candidate has been identified. Root still runs AVF, Architect, Executor, Post V&V, and GTValidator unless Root is explicitly called with direct reuse enabled.

Actual direct reuse requires explicit Root-level shortcut logic and tests proving Architect and Executor were skipped.

## 7. Direct Reuse Scenario Expected Behavior

The `direct_reuse` scenario seeds LocalDRS with a strong accepted Work record and calls Root with direct reuse enabled.

Expected trace behavior:

- `retrieved_record_count >= 1`
- `memory_context_applied = true`
- `reuse_decision = direct_reuse`
- `reuse_applied = true`
- `architect_skipped = true`
- `executor_skipped = true`
- `FinalOutput created_by = root_orchestrator`
- new Work DRS writeback exists

Interpretation:

- ReuseGate first returns `direct_reuse_candidate`.
- Explicit Root permission converts that candidate into actual direct reuse.
- Root creates FinalOutput directly from the trusted prior DRS record.
- Architect, Executor, Post V&V, and fresh GT selection are skipped for that request.
- Root still writes a new Work record and audit trace.
- No external APIs, LLMs, raw user text persistence, or secret storage are involved.

## 8. Context-Only Memory vs Direct Reuse

### Memory-Informed Execution / `context_only`

`context_only` means prior DRS records were retrieved and made visible as memory context for the run.

In v0.25:

- TemporalQuery is required.
- LocalDRS retrieval happens before AVF and Architect.
- `memory_context_applied = true` when relevant prior records exist.
- `reuse_decision = context_only`.
- `reuse_applied = false`.
- AVF, Architect, Executor, Post V&V, GTValidator, and Root FinalOutput still run normally.

This proves memory-first execution without claiming direct reuse.

### True Direct Reuse / `RootFinalFromReuse`

True direct reuse is an explicit optional path where Root may create a final output from a validated prior record without running the full planning/execution pipeline.

That path must be gated by checks such as:

- ReuseScore
- Freshness
- GTTrust
- PolicyOK
- ConflictCheck
- TimeEnvelope validity

Direct reuse is implemented in v0.25 only as an explicit CLI/test scenario. The baseline must not describe `context_only` or `direct_reuse_candidate` as actual direct reuse.

## 9. What This Baseline Does Not Prove Yet

This baseline does not prove:

- L0 deterministic reflex routing.
- Production L1 direct reuse routing.
- A complete adaptive `ExecutionModeRouter`.
- Real LLM/SLM role substitution.
- Automatic Root-level direct reuse routing.
- Pointer resolution.
- External DRS protocol.
- Telegram shell integration.
- A polished or genuinely useful real-world assistant scenario.

These are future layers. The v0.25 baseline exists to make later changes measurable against a stable contract.

v0.25 currently demonstrates deterministic L2/L3/L4-style baseline behavior plus an explicit L1 shortcut scenario:

- `cold_start` uses the full deterministic path.
- The second `reuse` run is memory-informed `context_only`.
- `direct_reuse` demonstrates explicit optional RootFinalFromReuse.
- Automatic L0/L1 routing is future work.

After this baseline, the next architecture work should focus on Architect/PlanGraph depth and richer planning semantics, not on adding more mock L0 reflex commands.

## 10. Future Demo Evolution

- `v0.25`: deterministic CLI baseline.
- `v0.30`: direct reuse gate and explicit shortcut.
- `v0.35`: LLM/SLM role substitution.
- `v0.40`: Telegram shell as interface only.
- `v0.45`: richer useful assistant scenario.
