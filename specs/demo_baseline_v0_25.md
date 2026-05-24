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

## 3. Cold Start Expected Behavior

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

## 4. Reuse Scenario Expected Behavior

The `reuse` scenario runs twice against the same LocalDRS path.

The first run behaves like cold start.

The second run is expected to show:

- `retrieved_record_count >= 1`
- `memory_context_applied = true`
- `reuse_decision = context_only`
- `reuse_applied = false`
- Direct reuse is not implemented yet.
- Architect and Executor still run.

Interpretation:

- The second run sees the Work record created by the first run.
- That record becomes memory context.
- The runtime is memory-informed, but it does not bypass planning or execution.
- GT still selects among fresh ResultProposals from the full pipeline.

## 5. Context-Only Memory vs Direct Reuse

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

True direct reuse is a future path where Root may create a final output from a validated prior record without running the full planning/execution pipeline.

That future path must be gated by checks such as:

- ReuseScore
- Freshness
- GTTrust
- PolicyOK
- ConflictCheck
- TimeEnvelope validity

Direct reuse is not implemented in v0.25. The baseline must not describe `context_only` as direct reuse.

## 6. What This Baseline Does Not Prove Yet

This baseline does not prove:

- Real LLM/SLM role substitution.
- Direct reuse gate behavior.
- Pointer resolution.
- External DRS protocol.
- Telegram shell integration.
- A polished or genuinely useful real-world assistant scenario.

These are future layers. The v0.25 baseline exists to make later changes measurable against a stable contract.

## 7. Future Demo Evolution

- `v0.25`: deterministic CLI baseline.
- `v0.30`: direct reuse gate.
- `v0.35`: LLM/SLM role substitution.
- `v0.40`: Telegram shell as interface only.
- `v0.45`: richer useful assistant scenario.

