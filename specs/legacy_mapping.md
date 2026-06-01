# Legacy Mapping

Legacy code is donor/reference only.

The new MVP is built from:

- specs/human_passport_v0_25.md
- specs/math_appendix_v0_3.md
- specs/machine_manifest_v0_25.json
- specs/invariants.md

It is not built by repairing the old architecture.

docs/strategic_expansion_map.md is vision-only and must not be used as the current implementation plan.

Do not preserve the old architecture blindly. Use legacy files only when they help implement the new contracts, invariants, schemas, tests, and canonical runtime boundaries.

## Core Rule

Legacy code may donate implementation ideas.

Legacy code must not define architecture.

If legacy code conflicts with the Human Passport, Math Appendix, Machine Manifest, or Invariants, the current project documents win.

## Canonical Runtime Target

Legacy code may be reused only if it can be adapted into the current canonical flow:

text User/Event → RootOrchestrator → Orchestrator-stage / Route Assembly → TemporalQuery → WorldState → LocalDRS retrieval → CandidateVectors → AVF / HardMask / SoftMask → AttractorPacket → Architect → PlanGraph → Fractal DAG Executor / node-level Executors → ResultProposals → Post V&V → GTValidator → back to Root → Root FinalOutput → DRS writeback / audit → Marennya/UP quarantine hooks 

Any legacy logic that skips these boundaries must be treated as reference only.

## Mapping

- PROJECT_GENESIS.md -> historical foundation only.
- engine.py -> RootOrchestrator skeleton donor.
- manager.py -> WorldStateAssembler donor, but weather and optional context must become optional needles/context, not automatic global loading.
- client.py -> LocalDRS donor.
- fractal.py -> Fractal DAG Executor / dependency execution donor.
- run.py -> executor runner donor.
- validators.py / finalize.py -> Post V&V / final draft donor, but final user output must remain Root-only.
- validator.py -> GTValidator donor.
- logging_audit.py -> audit donor.
- embeddings.py / similar_lsh.py / vector_store.py -> local semantic reuse donor.
- index.py / record.py / resolver.py -> future ExternalDRS pointer layer donor only.
- legacy architect prompts -> reference only; must be upgraded to receive AttractorPacket and return PlanGraph.
- legacy executor prompts -> reference only; must be upgraded to return ResultProposal only.
- legacy memory logic -> donor only; must be upgraded to TimeEnvelope, TemporalQuery, DRS layers, and pointer-first rules.
- legacy tool/API logic -> donor only; must become mock-only in MVP unless explicitly promoted through current policy.

## Required Upgrades for Any Reused Legacy Code

Any reused legacy component must preserve:

- Root-only FinalOutput;
- Architect receives AttractorPacket, not raw user text;
- Architect returns PlanGraph, not final answer;
- Fractal DAG Executor runs after Architect and does not become Root;
- Executors return ResultProposal only;
- Post V&V runs before GT;
- GT does not commit final output;
- DRS writeback requires TimeEnvelope;
- DRS retrieval requires TemporalQuery;
- Work / Thoughts / UP / DeadEnds / Quarantine layer separation;
- AVF runs before Architect;
- forbidden vectors do not reach Architect;
- CandidateVectors come only from allowed sources;
- Marennya and UP write to quarantine first;
- no real external action in MVP.

## Needle Boundary

Legacy plugins/tools must not be treated as ordinary free tools.

In the current architecture, a needle is a bounded capability contract.

A legacy tool can become a needle only if it declares:

- capabilities;
- candidate vectors;
- allowed actions;
- forbidden actions;
- permission policy;
- risk level;
- audit policy;
- DRS writeback policy;
- execution mode;
- mock/production boundary.

Executor may call a permitted needle capability, but Executor does not own the needle.

A needle-local Orchestrator, if present, is not global Root.

## Secrets and Credentials

Never commit secrets.

Do not store secrets directly in DRS content.

Legacy credential handling must not be reused as-is.

Production versions should use Credential Vault / sealed secret slots.

DRS may store secret references, scopes, provenance, access policy, and audit metadata, but not raw secret values.

## Prohibitions

- Never use legacy config.py.
- Never commit secrets.
- Do not add real external APIs for the MVP.
- Do not add LLM integration before the deterministic architecture is proven.
- Do not let legacy executor/finalizer code create FinalOutput.
- Do not let legacy memory code bypass TimeEnvelope or TemporalQuery.
- Do not let legacy tool code bypass Root, permission, policy, audit, or DRS writeback.
- Do not let legacy prompts define contracts instead of JSON schemas.
- Do not use legacy architecture to override the current passport.

## Recommended Use

Use legacy code only as a donor for:

- small helper functions;
- existing file layout ideas;
- audit/logging patterns;
- semantic reuse utilities;
- local DRS storage ideas;
- DAG/dependency execution ideas;
- validation ideas.

Before reusing legacy code, first ask:

text Can this be adapted to the current contract without weakening Root authority, Time, DRS layer separation, AVF, ResultProposal, Post V&V, GT, audit, or quarantine rules? 

If the answer is no, do not reuse it.