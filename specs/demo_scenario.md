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
- No Internet of Meaning implementation.
- No needle marketplace implementation.
- No production recursive child-cell execution.
- No universal natural Telegram assistant behavior.

## Current Interpretation

This demo scenario is intentionally small.

It does not prove the final Hedgehog OS product.

It proves that the MVP can preserve the canonical architecture:

text time-aware memory → controlled candidate vectors → AVF before Architect → AttractorPacket boundary → PlanGraph → ResultProposal-only execution → Post V&V → GT → Root-only final output → DRS writeback → quarantine-first reflection/transfer hooks 

Future useful business or assistant demos must be built on top of this baseline, not by bypassing it.