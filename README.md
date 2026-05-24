# Hedgehog OS Demo — Fractal Reflexive Runtime MVP

This repository demonstrates an AI OS-style runtime pipeline using deterministic Python stubs, JSON contracts, DRS memory routing, AVF scoring, GT selection, and Root-only final output. It is not a chatbot, not an agent chain, and not a UI project. The current MVP is a proof-of-architecture runtime for a future AI OS, centered on a mock government certificate request.

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

## Current MVP Limitations

- Deterministic stubs only.
- Local JSON DRS only.
- ReuseGate scoring exists; direct reuse is implemented only as an explicit optional CLI/test scenario, not as the default path.
- No pointer resolution yet.
- No real APIs.
- No UI.
- No Telegram shell yet.

## Roadmap

- Adaptive mode router that chooses direct reuse only when policy, permission, and tests allow it.
- Richer DRS pointer resolution.
- Marennya validation and promotion.
- UP validation and promotion.
- Telegram shell as interface only.
- External DRS pointer protocol.
- Stronger GT/TTL math.

## Safety / Privacy Note

DRS is pointer-first. Secrets, credentials, passport numbers, card data, tokens, passwords, and private keys must not be stored directly in DRS content. MVP inline content is local, mock, non-secret only.
