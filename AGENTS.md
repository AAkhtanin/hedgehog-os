# AGENTS.md — Hedgehog OS / Fractal Reflexive OS Demo

## Project identity

This repository is a proof-of-architecture demo for Hedgehog OS / Fractal Reflexive OS.

This is not a chatbot, not a generic agent, and not a simple script.

The goal is to implement a small local demo proving that the core architecture works:

For formulas and algorithms, read specs/math_appendix_v0_3.md.

User/Event
→ RootOrchestrator
→ Intent
→ WorldState
→ Local DRS retrieval with TemporalQuery
→ CandidateVectorGenerator
→ AVF scoring
→ AttractorPacket
→ Architect
→ PlanGraph
→ Executors
→ ResultProposals
→ Post V&V
→ GTValidator
→ Root FinalOutput
→ DRS writeback
→ Marennya / UP quarantine hooks

Demo domain:
mock government certificate request.

Do not implement the full OS.
Do not implement real external APIs.
Do not implement UI first.
Do not turn this into a chatbot.

---

## Non-negotiable architecture rules

1. FinalOutput is created only by RootOrchestrator.
2. Executors return ResultProposal only.
3. Architect receives AttractorPacket, not raw user text.
4. Architect returns PlanGraph, not a user-facing answer.
5. Every DRSRecord must include TimeEnvelope.
6. Every DRS retrieval must use TemporalQuery.
7. AVF must run before Architect.
8. AVF must hard-mask forbidden vectors before Architect sees them.
9. CandidateVectors must come only from:
   - installed needles,
   - Local DRS,
   - external DRS pointers,
   - fallback exploration templates.
10. CandidateVectors must not be freely hallucinated by LLM.
11. AVF scoring must be deterministic/vectorized over structured metadata, not free-form LLM reasoning.
12. Post V&V runs before GTValidator.
13. GTValidator updates Elo/regret/half_life or explicitly returns no_update.
14. Marennya and UP must write to quarantine first.
15. Marennya and UP must not mutate Work directly.
16. Work / Thoughts / UP / DeadEnds / Quarantine must remain separate layers.

---

## Required MVP repository layout

Create and preserve this structure:

hedgehog-os/
  README.md
  AGENTS.md

  specs/
    human_passport_v0_25.md
    machine_manifest_v0_25.json
    invariants.md
    demo_scenario.md
    legacy_mapping.md

  schemas/
    common.schema.json
    intent.schema.json
    time_envelope.schema.json
    temporal_query.schema.json
    world_state.schema.json
    candidate_vector.schema.json
    attractor_packet.schema.json
    plan_graph.schema.json
    result_proposal.schema.json
    vv_report.schema.json
    gt_report.schema.json
    drs_record.schema.json
    marenna_record.schema.json
    up_record.schema.json
    final_output.schema.json

  hedgehog/
    __init__.py
    models.py
    time_model.py
    drs.py
    world_state.py
    candidate_vectors.py
    avf.py
    architect.py
    executor.py
    post_vv.py
    gt_validator.py
    root_orchestrator.py
    marenna.py
    up.py
    audit.py
    policies.py
    local_embeddings.py
    similarity.py
    vector_store.py

  hedgehog/external_drs/
    __init__.py
    index.py
    record.py
    resolver.py

  needles/
    government_services.json
    fallback_exploration.json

  data/
    drs/
      work/
      thoughts/
      up/
      quarantine/
      deadends/

  demo/
    run_certificate_demo.py
    scenarios/
      cold_start.json
      reuse.json

  tests/
    test_final_output_root_only.py
    test_executor_no_final_output.py
    test_time_envelope_required.py
    test_temporal_query_required.py
    test_avf_hardmask.py
    test_candidate_vectors_no_llm_hallucination.py
    test_gt_updates_half_life.py
    test_marenna_quarantine.py
    test_up_never_mutates_work.py
    test_work_thoughts_up_separation.py

---

## Implementation order

Do not start by writing the whole OS.

Implement in this order:

1. Repository layout.
2. JSON schemas.
3. Python models.
4. TimeEnvelope and TemporalQuery helpers.
5. Local JSON DRS.
6. CandidateVectorGenerator.
7. AVF scoring.
8. AttractorPacket creation.
9. Deterministic Architect stub.
10. Executor stubs returning ResultProposal.
11. Post V&V.
12. GTValidator.
13. RootOrchestrator full pipeline.
14. Marennya quarantine hook.
15. UP quarantine hook.
16. Demo runner:
    - cold_start scenario,
    - reuse scenario.
17. Tests.

---

## MVP simplifications allowed

The MVP may use deterministic Python stubs.

Allowed:
- RootOrchestrator may be deterministic Python.
- Architect may be deterministic stub.
- Executors may be simulators.
- DRS may be local JSON files.
- External DRS may be mocked or disabled.
- GTValidator may use simple payoff + Elo.
- Marennya/UP validation may be a stubbed six-stage pipeline.
- Needles may be static JSON files.

Not allowed:
- Removing TimeEnvelope.
- Removing TemporalQuery.
- Removing AVF.
- Removing GTValidator.
- Removing quarantine.
- Letting Executor create final output.
- Mixing Work / Thoughts / UP.

---

## Legacy code usage

Legacy code may be used only as donor/reference.

Do not blindly preserve the old architecture.

Mapping:
- legacy engine.py → donor for RootOrchestrator skeleton.
- legacy manager.py → donor for WorldStateAssembler, but weather must become optional needle.
- legacy client.py → donor for LocalDRS layout and registry.
- legacy fractal.py → donor for DAG execution.
- legacy run.py → donor for executor runner.
- legacy validators.py/finalize.py → donor for Post V&V.
- legacy validator.py → donor for GTValidator.
- legacy logging_audit.py → donor for audit hashing/events.
- legacy embeddings.py/similar_lsh.py/vector_store.py → donor for local semantic search/dedup.
- legacy index.py/record.py/resolver.py → donor for future ExternalDRS pointer layer.
- legacy architect/executor prompts → legacy reference only; update contracts to AttractorPacket and ResultProposal.

Never use legacy config.py.
Never commit secrets.
Use .env.example only.

---

## Coding rules

Before editing:
1. Explain which files will change.
2. Explain why.
3. Mention which invariants are affected.

After editing:
1. List changed files.
2. Explain the reason for each change.
3. Run tests if possible.
4. Report remaining risks.

Do not run destructive commands unless explicitly requested.

Do not delete files without explicit permission.

Prefer small, reviewable commits.

---

## Test policy

Every implementation phase must add or preserve tests.

Required invariants:
- Only RootOrchestrator creates FinalOutput.
- Executor returns ResultProposal only.
- Every DRSRecord has TimeEnvelope.
- Every DRS retrieval requires TemporalQuery.
- AVF blocks forbidden vectors before Architect.
- CandidateVectors are not freely LLM-generated.
- GTValidator updates half_life or returns no_update.
- Marennya writes to quarantine before Thoughts.
- UP writes to quarantine before UP layer.
- UP and Marennya cannot mutate Work directly.
- Work / Thoughts / UP / DeadEnds remain separated.

---

## First task for Codex

When first started, Codex must not edit files.

First command should be:

Analyze this repository without changing files. Explain what files and structure exist now. Do not edit anything.
