# MVP Demo Scenario

The MVP demo domain is a mock government certificate request.

The demo is a local proof-of-architecture, not a production service, chatbot, UI, or external API integration.

## Scenarios

### cold_start

The cold-start scenario begins without a reusable prior DRS answer for the certificate request.

It must prove that the system can:

- derive intent from the user/event;
- assemble a relevant `WorldState`;
- query Local DRS only through `TemporalQuery`;
- generate `CandidateVector` values from allowed sources;
- hard-mask forbidden vectors through AVF;
- pass an `AttractorPacket` to Architect;
- receive a `PlanGraph` from Architect;
- execute the graph through executors that return `ResultProposal`;
- run Post V&V;
- run GTValidator;
- produce root-only `FinalOutput`;
- write back to DRS with `TimeEnvelope`;
- route Marennya and UP outputs through quarantine hooks.

### reuse

The reuse scenario begins with prior relevant DRS material.

It must prove memory-first reuse before Architect:

- `TemporalQuery` runs before DRS retrieval;
- relevant reusable records are considered before fallback exploration;
- stale or invalid records are penalized or excluded by time metadata;
- reuse-derived `CandidateVector` values still pass through AVF before Architect;
- the final answer still comes only from `RootOrchestrator`;
- any new DRS writeback includes `TimeEnvelope`.

## What The Demo Must Prove

- TemporalQuery before DRS.
- WorldState without irrelevant weather.
- Memory-first reuse.
- CandidateVectors from allowed sources.
- AVF hard mask.
- AttractorPacket to Architect.
- PlanGraph to Executors.
- ResultProposals from Executors.
- Post V&V before GTValidator.
- GTValidator update or explicit `no_update`.
- Root FinalOutput.
- DRS writeback with TimeEnvelope.
- Marennya/UP quarantine hooks.

## Exclusions

- No real external APIs.
- No UI first.
- No LLM integration first.
- No legacy architecture repair.
