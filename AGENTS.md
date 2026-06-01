# AGENTS.md — Hedgehog OS / Fractal Reflexive OS Demo

## Project identity

This repository is a proof-of-architecture demo for Hedgehog OS / Fractal Reflexive OS.

This is not a chatbot, not a generic agent, not a LangChain-style tool wrapper, and not a simple script.

The goal is to implement a small local demo proving that the core architecture works:

text User/Event → RootOrchestrator → Orchestrator-stage / Route Assembly → Intent → TemporalQuery → WorldState → Local DRS retrieval → CandidateVectorGenerator → AVF / HardMask / SoftMask → AttractorPacket → Architect → PlanGraph → Fractal DAG Executor / node-level Executors → ResultProposals → Post V&V → GTValidator → back to Root → Root FinalOutput → DRS writeback / audit → Marennya / UP quarantine hooks 

Demo domain:

text mock government certificate request 

This repository currently targets a deterministic MVP / proof-of-architecture demo.

Do not implement the full OS.

Do not implement real external APIs.

Do not implement UI first.

Do not turn this into a chatbot.

Do not treat strategic vision documents as the current implementation sprint.

---

## Document hierarchy

Primary documents:

- specs/human_passport_v0_25.md defines MVP architecture and invariants.
- specs/math_appendix_v0_3.md defines formulas and algorithmic details.
- specs/machine_manifest_v0_25.json defines the machine-readable project manifest.
- specs/invariants.md defines non-negotiable implementation invariants.
- specs/demo_baseline_v0_25.md defines the current deterministic demo baseline.
- specs/legacy_mapping.md defines how old code may be used as donor/reference only.
- docs/strategic_expansion_map.md defines long-term strategic vision only.

If documents conflict for current MVP implementation, the Human Passport controls.

docs/strategic_expansion_map.md is a lighthouse / vision document, not a task queue.

Do not implement from the Strategic Expansion Map unless a later explicit task promotes part of it into the engineering roadmap.

---

## Current engineering focus

The current MVP focus is:

text Observable Zero Trust Runtime proof → Root-controlled Fractal DAG Executor integration → Root-native canonical trace → stable DRS writeback / audit → NeedleRuntime outcome through canonical pipeline → only later: NeedleFactory / NeedleForge 

Do not jump ahead to:

- global DRS network;
- Internet of Meaning;
- needle marketplace;
- official bank/airline/government needles;
- blockchain;
- real external actions;
- production secret vault;
- global reputation system;
- unbounded recursive fractals;
- public semantic network.

These are future strategic layers, not current MVP tasks.

---

## Non-negotiable architecture rules

1. FinalOutput is created only by RootOrchestrator.
2. FinalRenderer may create FinalDraftProposal only.
3. FinalDraftProposal is not FinalOutput.
4. Executors return ResultProposal only.
5. Architect receives AttractorPacket, not raw user text.
6. Architect returns PlanGraph, not a user-facing answer.
7. Fractal DAG Executor runs after Architect returns PlanGraph.
8. Fractal DAG Executor is not Root.
9. Fractal DAG Executor may return ResultProposal-shaped outputs and child boundary snapshots.
10. Fractal DAG Executor must not create FinalOutput or perform global commit.
11. Every DRSRecord must include TimeEnvelope.
12. Every DRS retrieval must use TemporalQuery.
13. AVF must run before Architect.
14. AVF must hard-mask forbidden vectors before Architect sees them.
15. CandidateVectors must come only from:
    - installed needles;
    - Local DRS;
    - external DRS pointers;
    - fallback exploration templates.
16. CandidateVectors must not be freely hallucinated by LLM.
17. AVF scoring must be deterministic/vectorized over structured metadata, not free-form LLM reasoning.
18. Post V&V runs before GTValidator.
19. GTValidator updates Elo/regret/half_life or explicitly returns no_update.
20. GTValidator does not prove truth and does not commit final output.
21. Marennya and UP must write to quarantine first.
22. Marennya and UP must not mutate Work directly.
23. Work / Thoughts / UP / DeadEnds / Quarantine must remain separate layers.
24. L0/L1 shortcuts must not bypass Root, policy, permission, audit, or required DRS writeback.
25. A DRS hit is not direct reuse by itself.
26. Direct reuse requires explicit Root shortcut logic and tests proving Architect and Executor were skipped.
27. No real external API, device, purchase, banking, identity, government, or Telegram action may execute in MVP.

---

## Observable Zero Trust Runtime proof

The main auditor-facing proof command is:

bash python -m demo.run_canonical_pipeline_trace 

This trace should show:

- Root authority;
- explicit Orchestrator-stage / Route Assembly;
- TemporalQuery and DRS precheck;
- allowed CandidateVector sources only;
- AVF / HardMask / SoftMask before Architect;
- Root-created AttractorPacket;
- Architect input as AttractorPacket only;
- Architect output as PlanGraph;
- Fractal DAG Executor Core execution;
- ResultProposal-only execution outputs;
- Post V&V before GT;
- GT selection without final commit;
- artifact return to Root;
- Root-only FinalOutput;
- DRS writeback / audit;
- Marennya/UP quarantine hooks;
- no real external actions;
- no uncontrolled delegation.

This is a demo-runtime proof, not production OS runtime.

---

## Execution routing

The full cognitive pipeline must be available, but it is the maximum loop, not the mandatory path for every request.

Future production runtime requires an explicit ExecutionModeRouter / ModeRouter.

Execution levels:

- L0 deterministic_reflex: ready deterministic needle / known safe action; no Architect; no heavy LLM.
- L1 direct_reuse: fresh trusted DRS record or protocol replay through explicit Root shortcut gates.
- L2 memory_informed_execution: prior records found, but shortcut not allowed.
- L3 avf_architect_execution: AVF + Architect for bounded planning.
- L4 full_fractal_reasoning: multi-branch, ambiguous, risky, or high-value tasks.
- L5 deferred_reflection: Marennya, UP, idle validation, deep research, scheduled work.

In default v0.25 proof mode, shortcut routing is disabled so the demo exercises the full deterministic pipeline.

Explicit direct reuse scenario may skip Architect and Executor only after:

- ReuseScore;
- Freshness;
- GTTrust;
- PolicyOK;
- ConflictCheck;
- TimeEnvelope validity;
- ActionPermission if external action is involved;
- explicit Root permission.

---

## DRS pointer-first rule

- DRS is a registry/resolver/index, similar to a much more complex DNS for memory, capabilities, and knowledge routes.
- DRS records should prefer pointer + summary + metadata over raw payload.
- MVP LocalDRS may store small inline non-secret content only as a local simplification.
- Real payload may live in local memory, local JSON, local secure vault, vector store, document store, project store, or external DRS pointer.
- Pointer resolution is a separate future responsibility and must respect access_policy.
- DRS must never directly store credentials, tokens, passwords, private keys, passport numbers, card numbers, CVV, or similar sensitive payloads.
- Future production versions should use Credential Vault / sealed secret slots.
- DRS may store secret references, scopes, provenance, access policy, and audit metadata, but not raw secret values.
- LLM/SLM components may reason over the existence, type, scope, and permission state of sealed slots without seeing the secret itself.
- Every DRSRecord still requires TimeEnvelope.
- Every retrieval still requires TemporalQuery.
- Work / Thoughts / UP / DeadEnds / Quarantine remain separate layers.
- Marennya and UP must write to Quarantine first and must not mutate Work directly.

---

## Needle topology

Needles are contract modules and capability boundaries, not Executor-owned plugins.

A needle may be:

- Root-visible;
- cluster-local;
- branch-bound;
- systemic/internal.

Executor or a runtime port may call a permitted bounded needle capability, but Executor does not own the needle.

Loading a needle does not grant sovereignty.

A needle-local Orchestrator, if present, is not global Root.

Needle outcomes must pass through the canonical pipeline:

text Needle outcome → ResultProposal-compatible artifact / QuarantineRecord → Post V&V → GT / Root decision → DRS / audit / quarantine / writeback 

Marennya and UP are built-in systemic/internal needles:

- Marennya is a reflective/internal-improvement needle.
- UP is a transfer/cross-domain-opportunity needle.

Future systemic/internal needles may contain bounded local fractal cycles, but they must not receive global sovereignty.

Systemic needle outputs must become canonical boundary artifacts such as:

- ResultProposal;
- QuarantineRecord;
- VVReport;
- GTReport;
- DRS pointer;
- AuditEvent.

Cognitive mutations from systemic needles must follow quarantine-first behavior and Root-controlled promotion.

---

## Required MVP repository layout

Create and preserve this structure as the baseline, while allowing newer committed files to extend it:

text hedgehog-os/   README.md   AGENTS.md    docs/     strategic_expansion_map.md    specs/     human_passport_v0_25.md     math_appendix_v0_3.md     machine_manifest_v0_25.json     invariants.md     demo_baseline_v0_25.md     legacy_mapping.md    schemas/     common.schema.json     intent.schema.json     time_envelope.schema.json     temporal_query.schema.json     world_state.schema.json     candidate_vector.schema.json     attractor_packet.schema.json     plan_graph.schema.json     result_proposal.schema.json     vv_report.schema.json     gt_report.schema.json     drs_record.schema.json     marenna_record.schema.json     up_record.schema.json     final_output.schema.json    hedgehog/     __init__.py     models.py     time_model.py     drs.py     world_state.py     candidate_vectors.py     avf.py     architect.py     fractal_dag_executor.py     executor.py     post_vv.py     gt_validator.py     root_orchestrator.py     marenna.py     up.py     audit.py     policies.py     local_embeddings.py     similarity.py     vector_store.py    hedgehog/external_drs/     __init__.py     index.py     record.py     resolver.py    needles/     government_services.json     fallback_exploration.json    data/     drs/       work/       thoughts/       up/       quarantine/       deadends/    demo/     run_certificate_demo.py     run_fractal_dag_executor_core.py     run_canonical_pipeline_trace.py     scenarios/       cold_start.json       reuse.json    tests/     test_schema_files_valid.py     test_needles_valid.py     test_time_model.py     test_candidate_vectors.py     test_avf_runtime.py     test_architect_runtime.py     test_fractal_dag_executor_core_runner.py     test_executor_runtime.py     test_post_vv_runtime.py     test_gt_validator_runtime.py     test_drs_runtime.py     test_root_orchestrator_runtime.py     test_canonical_pipeline_trace_runner.py 

---

## Implementation order

Do not start by writing the whole OS.

Use this order for current MVP work:

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
    - cold_start scenario;
    - reuse scenario.
17. Execution routing / direct reuse gate.
18. L0 deterministic reflex proof path.
19. Fractal DAG Executor Core.
20. Canonical pipeline trace / Observable Zero Trust Runtime proof.
21. Documentation checkpoint.
22. Root-controlled FractalDagExecutor integration.
23. Root-native canonical trace.

Do not implement NeedleFactory, marketplace, global DRS, official organizational needles, blockchain, or real external actions before the canonical runtime is stable.

---

## MVP simplifications allowed

The MVP may use deterministic Python stubs.

Allowed:

- RootOrchestrator may be deterministic Python.
- Architect may be deterministic stub.
- Executors may be simulators.
- Fractal DAG Executor may use deterministic local execution.
- DRS may be local JSON files.
- External DRS may be mocked or disabled.
- GTValidator may use simple payoff + Elo.
- Marennya/UP validation may be a stubbed six-stage pipeline.
- Needles may be static JSON files.
- NeedleRuntime may be mock-only.

Not allowed:

- Removing TimeEnvelope.
- Removing TemporalQuery.
- Removing AVF.
- Removing GTValidator.
- Removing quarantine.
- Letting Executor create FinalOutput.
- Letting Architect answer the user.
- Letting DAG runner become Root.
- Mixing Work / Thoughts / UP.
- Performing real external actions in MVP.

---

## Legacy code usage

Legacy code may be used only as donor/reference.

Do not blindly preserve the old architecture.

Mapping:

- legacy engine.py -> donor for RootOrchestrator skeleton.
- legacy manager.py -> donor for WorldStateAssembler, but weather must become optional needle/context.
- legacy client.py -> donor for LocalDRS layout and registry.
- legacy fractal.py -> donor for Fractal DAG Executor / dependency execution.
- legacy run.py -> donor for executor runner.
- legacy validators.py / finalize.py -> donor for Post V&V / final draft only.
- legacy validator.py -> donor for GTValidator.
- legacy logging_audit.py -> donor for audit hashing/events.
- legacy embeddings.py / similar_lsh.py / vector_store.py -> donor for local semantic search/dedup.
- legacy index.py / record.py / resolver.py -> donor for future ExternalDRS pointer layer.
- legacy architect prompts -> reference only; upgrade to AttractorPacket input and PlanGraph output.
- legacy executor prompts -> reference only; upgrade to ResultProposal output.

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

For docs-only edits, do not modify runtime code, schemas, or tests unless explicitly requested.

For JSON manifest edits, validate with:

bash python3 -m json.tool specs/machine_manifest_v0_25.json > /tmp/manifest_check.json 

---

## Test policy

Every implementation phase must add or preserve tests.

Required invariants:

- Only RootOrchestrator creates FinalOutput.
- FinalRenderer creates FinalDraftProposal only.
- Executor returns ResultProposal only.
- Architect receives AttractorPacket only.
- Architect returns PlanGraph only.
- Fractal DAG Executor does not create FinalOutput.
- Every DRSRecord has TimeEnvelope.
- Every DRS retrieval requires TemporalQuery.
- AVF blocks forbidden vectors before Architect.
- CandidateVectors are not freely LLM-generated.
- GTValidator updates half_life or returns no_update.
- GTValidator does not commit FinalOutput.
- Marennya writes to quarantine before Thoughts.
- UP writes to quarantine before UP layer.
- UP and Marennya cannot mutate Work directly.
- Work / Thoughts / UP / DeadEnds remain separated.
- Direct reuse skips Architect/Executor only when explicit gates and Root permission allow it.
- L0/L1 shortcuts preserve policy, permission, audit, and DRS writeback.
- No real external actions occur in MVP.

---

## First task for Codex

When first started, Codex must not edit files.

First command should be:

text Analyze this repository without changing files. Explain what files and structure exist now. Do not edit anything. 