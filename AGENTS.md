# AGENTS.md — Hedgehog OS / Fractal Reflexive OS Demo

## Project identity

This repository is a proof-of-architecture demo for Hedgehog OS / Fractal Reflexive OS.

This is not a chatbot, not a generic agent, not a LangChain-style tool wrapper, and not a simple script.

The goal is to implement a small local demo proving that the core architecture works:

text User/Event → RootOrchestrator → Orchestrator-stage / Route Assembly → Intent → TemporalQuery → WorldState → Local DRS retrieval → CandidateVectorGenerator → AVF / HardMask / SoftMask → AttractorPacket → Architect → PlanGraph → Fractal DAG Executor / node-level Executors → ResultProposals → Post V&V → GTValidator → back to Root → Root FinalOutput → DRS writeback / audit

This is the main downward canonical execution vector, not the full architecture. Marennya and UP are separate deferred lateral/upward systemic directions.

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
- docs/passport_geometry_root_needles.md defines the Root-centered capability geometry and anti-reduction framing.
- docs/strategic_expansion_map.md defines long-term strategic vision only.

If documents conflict for current MVP implementation, the Human Passport controls.

docs/strategic_expansion_map.md is a lighthouse / vision document, not a task queue.

Do not implement from the Strategic Expansion Map unless a later explicit task promotes part of it into the engineering roadmap.

---

## Current engineering focus

The current MVP focus is:

text Observable Zero Trust Runtime proof → Root-controlled Fractal DAG Executor integration → Root-native canonical trace → stable DRS writeback / audit → NeedleRuntime outcomes through Post V&V / real GTValidator / LocalDRS routing → Large Graph / Bounded Fractal Stress → DRS Graph Proximity / Lineage → Chaos Survival Showcase → Compute Collapse via DRS Reuse → DRS Layer Taxonomy → Typed DRS Lineage Edges → ReuseScore → Semantic Reuse Pipeline Integration → Root Semantic Reuse Decision/Gate/Final Traces → Semantic Reuse Authority Stack Audit → Root-native Semantic Reuse E2E Trace → Root-native Full Canonical E2E Trace → Optional Live Gemini Architect Smoke → Ordered Live Gemini Orchestrator-to-Architect Smoke → Controlled Orchestrator Matrix Gate → AVF / Attractor Formation from accepted Matrix → bounded Architect / Executor / Post V&V / GT / Root Final → local DRS audit/writeback → sandbox NeedleRuntime → bounded child fractal cell → live child Executor → DRS Lifecycle Semantics → ConflictCheck → Audit/hash-chain → Controlled Route Assembly → applied/fractal/coupling/bridge/Needle-safety proofs → External DRS Pointer Protocol v0.1 → Read-only Enterprise Connector Sandbox v0.1 → External Evidence Acceptance Gate v0.1 → Bounded LLM Semantic Executor Node v0.1 → Enterprise Chaos Pack v0.1 → Compute Collapse Enterprise Bench v0.1 → Math / Invariants Sync v0.4 complete → Kernel Enforcement / Transition Matrix Hardening v0.1 complete → Developer Facade / Capability Manifest UX v0.1 complete → Production Boundary Design Docs v0.1 complete as design documentation → Enterprise Killer Demo v0.1 / Demo A complete as Authority / Safety / Compute Collapse assembly proof → Enterprise Document Killer Demo B v0.1 complete as Document / Evidence Workflow applied proof → artifact_type Mapping / Runtime Artifact Vocabulary v0.1 Option A docs/spec map complete through audit → Long-lived DRS State / TTL / Aging Stress v0.1 complete through proof, audit, docs sync, human walkthrough, and human walkthrough audit → Full Suite Drift Repair Phase 1 complete through repair and audit → DRS Lineage / Provenance Pressure v0.1 complete through human walkthrough audit → Compromised Upstream Pack v0.1 CLOSED → STOP PROOF-ONLY EXPANSION GATE → Real Semantic Runtime MVP plan → only after explicit review: DRS Poisoning Resistance v0.1 and Economic Adversary v0.1 as gated / conditional protection layers, runtime/schema production DRS, external/global DRS, Marennya / UP, Negative Trace, Option B/C/D/E artifact vocabulary work, Public Auditor Packet / Whitepaper draft, Manifest Auto-Hardening after Killer Demo

Current checkpoint: G2-D v0.3.9 implementation committed; independent re-audit pending.

Current G2-D v0.3.9 contract and lifecycle facts:

- R-H1 implementation basis: `c5ca150af2fbb7981e1ed8ee83d914570e14cdeb`.
- R-H1 accepted independent audit commit: `056bc1c746b49699069a90766d067f1a77d205dc`.
- R-H1 accepted audit path: `docs/audit_reports/auditor_clean_clone_licensing_release_spine_reconciliation_r_h1_v01.log`.
- R-H1 accepted audit SHA-256: `40148424d58b1f599c9212a6914bdaadbfc932b2cce19fc67fccd0801b12af23`.
- R-H1 checkpoint path: `docs/clean_clone_licensing_release_spine_reconciliation_r_h1_checkpoint_v01.md`.
- Accepted G2-C preflight commit: `4b33c8106dbb3d7b50596630cd9dcdcf3f84cfac`.
- Accepted G2-C preflight path: `docs/execution_mode_router_g2_c_preflight_v01.md`.
- G2-C implementation basis: `27a866ca06a331b4169c56abac9a460334d75539`.
- G2-C audit commit: `72854bcdc85d19e9c6a6636f9a7eedd1929f03cb`.
- G2-C audit: `docs/audit_reports/auditor_execution_mode_router_g2_c_v01.log`.
- G2-C checkpoint: `docs/execution_mode_router_g2_c_checkpoint_v01.md`.
- Accepted G2-D preflight commit: `2e1681a54c847beb106d9e57da250dac82ea6192`.
- Accepted G2-D preflight path: `docs/fractal_runtime_v0_2_g2_d_preflight_v01.md`.
- Accepted G2-D preflight SHA-256: `8e3ae3b04a9b622329e85529edb8a150739cc787b341f1609438dbde00412e79`.
- Accepted G2-D addendum path: `docs/fractal_runtime_v0_2_g2_d_post_acceptance_contract_addendum_v01.md`.
- Accepted G2-D v0.3.8 directional draft SHA-256: `91264cc9f6177edc1779d3d7553b4ef4484d3db196900380a987b3ae0ccc1454`.
- Controlling DESIGN_V03 SHA-256: `7e32560ff19b95a8bd553072d855e8378d749c0f5d17861b7dee9a1f2577c4fe`.
- Active G2-D v0.3.9 addendum SHA-256: `1bbe028a4c757330b4ba94aec461e5bfbb1d1ef7496a68593dc20106c4867445`.
- G2-D v0.3.9 contract commit: `8638a3c7d0c2774de161a5e52a8aa62ac9db2aa3`.
- G2-D v0.3.9 release-consumer maintenance commit: `b9d95605b960ce3837446b1bf38b665ce16f03fb`.
- G2-D v0.3.9 implementation commit: `7a915111e974bc62ff2a7bfe70e8d5a911da03fd`.
- G2-D v0.3.9 implementation parent: `b9d95605b960ce3837446b1bf38b665ce16f03fb`.
- G2-D v0.3.9 implementation patch SHA-256: `442b68cdff95fc06a1176fcb4c3d64323110e197b771d5e932db5215b3d8bc13`.
- G2-D v0.3.9 owner evidence bundle SHA-256: `fac5596484fb5207632ec6083eeaf2d3cb7d2fa4cdb8f726762d1d635e9e34a0`.
- Historical accepted G2-D v0.3.8 addendum SHA-256: `09db4ff2224e59c878b967ba634084d72cd01b36f86edfa5fca2e9750e976ea6`.
- Historical G2-D v0.3.8 implementation commit: `3d9cc2aac45d2923a9d9d5848a8f4f81d011b22e`.
- Historical G2-D v0.3.8 implementation patch SHA-256: `dbb5e3010e3337b5da0a36cfb69f9597a090be6d14b256699945c5a6fb09c291`.
- Historical G2-D v0.3.8 owner evidence SHA-256: `51e913b59a8a82ea3fc5b7688f02dc07e4d9bf15d487d23d879d0b30f6b938f6`.
- Historical G2-D v0.3.8 reclosure commit: `4cf427f82a096383ae5873024787c19e56ac0fb5`.
- Historical accepted G2-D v0.3.7 normative donor SHA-256: `8801e413f93765cc7059ce5e03e82e881b20cfd193f12551a60a0b90920bb63d`.
- Historical accepted G2-D v0.3.7 addendum SHA-256: `29983cd17cbefe306de32cf045827fc927280bae5fdb0d7c9db50203a0ea6511`.
- Corrected G2-D implementation commit: `27c6dfd10740103cddc13bac3ce35f917b5f30c5`.
- Corrected G2-D implementation parent: `3dcaabb7a231259c488643a652b92ee03d7faf52`.
- Corrected G2-D implementation patch SHA-256: `be594af310b2d13baf0e45283944bd68f56461126b6aa3fbbcaff541a58a0279`.
- Corrected G2-D owner evidence bundle SHA-256: `e49752fcd1c19dfe8ddf55a254b2d97f8c27688bc0c2371b6ad4ffe2ec5c9cdd`.
- Independent corrected G2-D re-audit commit: `2eccb604fee89d7e79025337d3858d6dbfea5fbc`.
- Independent corrected G2-D re-audit: `docs/audit_reports/auditor_fractal_runtime_g2_d_v037_observed_work_correction_v01.log`.
- Independent corrected G2-D re-audit SHA-256: `c31d1712593184317b03425c57c5fcebf19532cbfc3086981223bf32afd0e8a3`.
- Corrected G2-D successor checkpoint: `docs/fractal_runtime_v0_2_g2_d_observed_work_correction_checkpoint_v01.md`.
- Corrected G2-D successor checkpoint SHA-256: `606d9f1c516ddbe86ec63fe93fc2126ae69bfbf3f8169879a6c1933162296677`.
- Accepted G2-E preflight SHA-256: `83f36c9b2d47619a8c8ab997eba6b8ef16f2a3ab07cb3aecfc77ea82469f0d8b`.
- Accepted G2-E v0.1.3 addendum SHA-256: `2b982ecaed9dc5cea2373676d816840ca683c8190b69516c14688cbba9e452f8`.
- Accepted G2-E v0.1.3 normative donor SHA-256: `17b9384db812d5078301a9b3d4335dd3351481e117929b6b04c1ff6a137f4a56`.
- Historical pre-v0.3.8-reclosure G2-E3 V06 archive SHA-256: `d8630f68af26ab9ae1d925c0e236b71e1e2ac3e759a39f642af2fcf432e4ead3`.
- Fresh G2-E3 V06 on G2-D v0.3.8 evidence SHA-256: `09bfe734048febfcf1ea32cc35195fb494b73c36a360163c8329aaf5e3fc2ca8`.
- G2-E3 baseline source observation SHA-256: `fb2687f08911e5420d03ec40fef02fde3794edc1e03d637df9f8d26c062b3f3c`.
- G2-E3 baseline member observation SHA-256: `fbd40637c2082ec385204a53a2173695a2247b6cd8e908f34349d75d6a1e3467`.
- G2-E3 baseline member identities SHA-256: `8924a3971624823805d2ed7b99adff5a68ca96d07aa67bb516d744e7f3877b39`.
- E4 public-seam constructibility register SHA-256: `a10be3df58ed7fbf32fcb853c7de93f76eec5b3070120b0f895b27340cf2aed2`.
- E4 two-Root-pair register SHA-256: `a8a8fd530d95ec4bce8a0faf14044c8b98f53973651cf65784a717d69e02ce33`.
- G2-D v0.3.8 post-implementation lifecycle sync commit: `e66c8be08e753077b6a99eeb635bf6fe25ee4b90`.
- Historical G2-D v0.3.8 independent re-audit commit: `edfa42198efa1d03097570d30b6364af1b567050`.
- Historical G2-D v0.3.8 independent re-audit path: `docs/audit_reports/auditor_fractal_runtime_g2_d_v038_proof_based_whole_run_correction_v01.log`.
- G2-D v0.3.8 independent re-audit SHA-256: `acd62cfcf3753a4c02c5f5187e64e8940cf3b3420f97850b0426583465996d67`.
- G2-D v0.3.8 independent re-audit evidence bundle SHA-256: `5e43b38b921f7035609e5ef3a33058325c4b529193ad82d87b70a84cd6ff363b`.
- Historical G2-D v0.3.8 successor checkpoint: `docs/fractal_runtime_v0_2_g2_d_proof_based_whole_run_correction_checkpoint_v01.md`.
- G2-D v0.3.8 successor checkpoint SHA-256: `64e2c94f83e8dd2012d0f6f6d8f969bc08832b61194ce24668c6ec7a4eb96e6b`.
- G2-D v0.3.8 closure commit subject: `Close G2-D v0.3.8 proof-based whole-run correction`.
- G2-D v0.3.8 closure commit identity: `NOT_SELF_RECORDED`.
- Historical pre-correction G2-D implementation basis: `5e5d565eb6c2088db995cf9e5b3ccb0743f1c9cd`.
- Historical pre-correction G2-D audit commit: `c0dc618a0b693fe55435f17a025789267bcb79ff`.
- Historical pre-correction G2-D audit: `docs/audit_reports/auditor_fractal_runtime_g2_d_v02.log`.
- Historical pre-correction G2-D audit SHA-256: `ccc367ac92ad02e005c7968d152bf7810a772db94dd671e26e5d27f30d2d72aa`.
- Historical pre-correction G2-D checkpoint: `docs/fractal_runtime_v0_2_g2_d_checkpoint_v01.md`.
- The old audit and checkpoint certify pre-correction bytes only.
- Corrected closure commit subject: `Close G2-D v0.3.7 observed-work correction`.
- Corrected closure commit identity: `NOT_SELF_RECORDED`.
- R-H1 status: `CLOSED_PASS`.
- Gate 1: `CLOSED_PASS`.
- Two-Domain programme: `CLOSED_PASS`.
- G2-A: `CLOSED_PASS`.
- G2-B: `CLOSED_PASS`.
- G2-C: `CLOSED_PASS`.
- Historical pre-correction G2-D: `CLOSED_PASS_ON_PRECORRECTION_BYTES`.
- G2-D: `REAUDIT_PENDING`.
- Historical G2-D v0.3.8: `CLOSED_PASS_ON_V038_BYTES`.
- G2-D v0.3.9 contract: `ACCEPTED_COMMITTED`.
- G2-D v0.3.9 implementation authorized: `false`.
- G2-D v0.3.9 implementation action open: `false`.
- G2-D v0.3.9 implementation started: `true`.
- G2-D v0.3.9 corrected implementation exists: `true`.
- G2-D v0.3.9 corrected implementation committed: `true`.
- G2-D v0.3.9 runtime implementation status: `IMPLEMENTED_COMMITTED_FULL_ACCEPTANCE_PASS`.
- G2-D v0.3.9 full owner acceptance passed: `true`.
- G2-D contract-only claim: `false`.
- G2-D v0.3.9 independent re-audit passed: `false`.
- G2-D v0.3.9 corrected CLOSED_PASS: `false`.
- G2-D v0.3.9 additive reclosure required: `true`.
- `V037_IMPLEMENTATION_NONCONFORMANCE=YES`.
- `V038_CONTRACT_SEMANTICS_CHANGED=NO`.
- `V038_ROLE=EXPLICIT_CLARIFICATION_AND_LIFECYCLE_REOPENING`.
- `V038_IMPLEMENTATION_NONCONFORMANCE=YES`.
- `V039_CONTRACT_SEMANTICS_CHANGED=NO`.
- `V039_ROLE=EXPLICIT_IMPLEMENTATION_NONCONFORMANCE_CLARIFICATION_AND_LIFECYCLE_REOPENING`.
- Guardian ruling: `APPROVE_WITH_MANDATORY_OVERLAY`.
- Isolated worktree strategy approved: `true`.
- E4 two-path-only implementation sufficient: `false`.
- E4 public end-to-end carrier overlay required: `true`.
- Revised guardian decision required: `false`.
- G2-D v0.3.8 correction implementation authorized: `true`.
- G2-D v0.3.8 implementation started: `true`.
- G2-D v0.3.8 corrected implementation exists: `true`.
- G2-D v0.3.8 corrected implementation committed: `true`.
- G2-D v0.3.8 corrected implementation commit:
  `3d9cc2aac45d2923a9d9d5848a8f4f81d011b22e`.
- G2-D v0.3.8 implementation patch SHA-256:
  `dbb5e3010e3337b5da0a36cfb69f9597a090be6d14b256699945c5a6fb09c291`.
- G2-D v0.3.8 owner evidence bundle SHA-256:
  `51e913b59a8a82ea3fc5b7688f02dc07e4d9bf15d487d23d879d0b30f6b938f6`.
- G2-D v0.3.8 contract-only claim: `false`.
- G2-D v0.3.8 runtime acceptance claimed: `true`.
- G2-D v0.3.8 full cumulative acceptance pending owner: `false`.
- G2-D v0.3.8 independent re-audit passed: `true`.
- G2-D v0.3.8 additive reclosure completed: `true`.
- G2-D v0.3.8 corrected closure claimed: `true`.
- Historical v0.3.7 implementation, owner evidence, independent re-audit,
  checkpoint, and reclosure remain immutable evidence for v0.3.7 bytes only.
- Old G2-D audit/checkpoint class: `HISTORICAL_PRECORRECTION_EVIDENCE`.
- G2-E3: `REVALIDATION_PENDING_ON_CORRECTED_G2D`.
- Historical G2-E3 v0.3.8 acceptance: `IMPLEMENTED_COMMITTED_ACCEPTANCE_PASS_ON_V038_G2D`.
- Fresh unchanged post-reclosure G2-E3 V06 passed: `true`.
- G2-E4 contract: `ACCEPTED_IMPLEMENTATION_PENDING`.
- G2-E4: `IMPLEMENTED_COMMITTED_STRICT_SUBTREE_PASS_ANTI_GAMING_ACCEPTANCE_BLOCKED`.
- G2-E4 strict-subtree implementation committed: `true`.
- G2-E4 strict subtree: `IMPLEMENTED_COMMITTED_PASS`.
- G2-E4 anti-gaming acceptance: `BLOCKED_PENDING_G2D_V039_RECLOSURE`.
- G2-E4 anti-gaming correction authorized: `false`.
- G2-E5: `NOT_STARTED_NOT_AUTHORIZED`.
- G2-E6: `NOT_STARTED_NOT_AUTHORIZED`.
- Gate 2: `NOT_CLOSED`.
- G2-F: `NOT_STARTED_NOT_AUTHORIZED`.
- Current architecture:

  ```text
  BSEP
  -> semantic proposal
  -> G2-C Root-reviewed ExecutionModeRouteEligibility
  -> runtime-owned RuntimeExecutionTopology
  -> bounded runtime execution
  -> ResultProposal / Post V&V / GT / PARENT_RETURN
  -> Root
  ```

- RuntimeExecutionTopology is not authority, a child cell is not Root, and a
  child result is not FinalOutput.
- The accepted t12 semantic law already exists. v0.3.9 records a narrow v0.3.8 implementation nonconformance and reopens the lifecycle without changing semantics.
- The exact v0.3.9 correction modified only `hedgehog/kernel/fractal_runtime_v02.py` and `tests/test_fractal_runtime_g2_d_v02.py`; it is committed and remains `REAUDIT_PENDING`.
- The clean isolated v0.3.9 V06 must pass before guarded fast-forward of the dirty primary worktree.
- Final E4 call accounting is pair 2/2, focused 2/2, and complete file 3/3.
- The parked primary E4 patch SHA-256 remains `3c08807bcf8545b95ceca22ec13f1aa1cb2e8d2669ad72cf269ac2d077163aff`.
- Root is the only final authority.
- G2-C owns the accepted Root-reviewed route.
- G2-D owns RuntimeExecutionTopology and stable topology-node and cell IDs.
- G2-D imports no G2-E module or type.
- G2-D creates no truth, permission, ActionCommitPacket, receipt, effect
  handle, DRS write, FinalOutput, provider authority, connector authority, or
  real-world effect.
- Provider, model, network, connector, and external-DRS calls remain zero.
- G2-D v0.3.8 does not alter DESIGN_V03 semantics. It records that v0.3.7
  runtime bytes did not conform to the controlling proof-based null-policy
  matrix; the owner-authorized committed implementation corrects that
  nonconformance and is now additively reclosed as `CLOSED_PASS`.
- The independent re-audit and successor checkpoint are evidence, not
  authority, permission, or Gate-2 closure by themselves.
- The prior G2-E3 V06 and committed E4 strict-subtree work remain historical
  evidence for their exact basis. They do not revalidate v0.3.9, accept the E4
  anti-gaming boundary, start E5/E6/F, close Gate 2, create authority, or
  create a real-world effect.
- Historical execution-representation references create no contract, adapter, migration, cleanup, compatibility workstream, or implementation slice.
- R-IP1 does not block G2-E or G2-F.
- Private R-IP1 drafts may remain living through Gates 3-6.
- No public publication occurs before Gate 6 closure and separate explicit owner release approval.
- Public release: `NOT_CLAIMED`.
- RC2: `NOT_CLAIMED`.
- Production readiness: `NOT_CLAIMED`.
- Production security certification: `NOT_CLAIMED`.
- Successor baseline: `NOT_CLAIMED`.
- FinalOutput, permission, packet, receipt, and DRS write creation: `NOT_CLAIMED`.
- Real-world effects remain zero.

## Root-centered capability geometry

Pipeline traces are observable projections, not the architecture. Root-centered
capability geometry is the architecture. Canonical execution is the main
downward Root-controlled runtime vector; it is not merely an ordinary needle.

Needles are directed bounded capability contracts / semantic organs anchored in
Root, not plugins. DRS is semantic topology and address/resonance/lineage/audit
fabric, not vector memory or authority. Marennya is a deferred lateral
reflective systemic needle-like direction; UP is a deferred upward
transfer/opportunity systemic needle-like direction. They are proposal-only,
quarantine-first, Root-approved, and not required for first applied semantic
demos.

Anti-reduction rules:

- Do not reduce Hedgehog OS to a linear long-chain.
- Do not describe needles as plugins.
- Do not describe DRS as vector memory.
- Do not describe Marennya / UP as post-pipeline modules.
- Do not grant final authority to Orchestrator, Architect, Executor, child
  cells, needles, DRS, GT, ConflictCheck, Marennya, UP, or external DRS.
- Apply "Vassal of my vassal is not my vassal": bounded local authority does
  not propagate upward, sideways, outward, or into Root.
- Applied demos prove domain transfer of the canonical Root-controlled path.
- Applied demos now cover warehouse, certificate/document, and travel
  multi-condition readiness.
- Applied demos must not automatically create `protocol_candidate` or
  `needle_candidate` unless that lifecycle is explicitly under test.
- Before NeedleForge or action needles, the Permission/NeedsUser boundary must remain intact: permission is not execution, approval is not completed action, and `needs_user` is not failure.
- NeedleCandidate lifecycle may create proof-level candidate objects, but any installed needle, production persistence, external action, or bypassing Root remains forbidden.
- DRS retrieval, semantic similarity, and ReuseScore are advisory and cannot bypass Root, Permission/NeedsUser, ConflictCheck, freshness, WorldState compatibility, quarantine/deadend checks, or audit.
- Child-cell candidates are local bounded proof-mode structures, not real
  autonomous agents.
- Child cells must not finalize a parent, execute actions, write DRS, install a
  Needle, spawn children, override siblings, or create protocol/NeedleCandidate
  objects. Root must aggregate and finalize.
- Coupling edges are bounded semantic resonance only. Shared evidence can
  inform but cannot decide, transfer authority, or cross-finalize parents.
- A coupling edge is the bounded semantic relation. DRS bridge traversal is
  the local reviewed trace over that relation.
- Bridge records are candidate evidence, not authority. Traversal trace is not
  truth, and bridge traversal is not provenance laundering.
- DRS bridge traversal must not bypass Root, ConflictCheck, GT, audit,
  Permission/NeedsUser, freshness, or quarantine/deadend checks.
- No retrieval, bridge, coupling, child-cell, DAG, GT, audit, or
  NeedleCandidate mechanism may self-promote into an installed Needle or
  capability.
- NeedleCandidate remains only a candidate/reference until an explicit
  Root-reviewed installation boundary and safety checks exist.
- RAG-like retrieval must not be used as truth proof. DAG nodes must not claim
  Root authority. Bridge traversal must not launder provenance.
- GT must not install a Needle, grant authority, execute action, or mark truth.
- Do not use Needle safety pack language to claim NeedleFactory or production
  Needle installation.
- Do not use DRS Bridge language to claim External DRS, global semantic
  fabric, public Internet of Meaning, remote retrieval, or production
  persistence.
- Targeted proof layers must not replay historical collectors by default.
  Closed layers should be referenced as committed checkpoint metadata when
  the current proof only needs source status.
- When historical collectors are not replayed, reports must state
  `source_collectors_replayed=false`. The mode
  `source_evidence_mode=closed_checkpoint_metadata_only` is runtime-cost
  hygiene, not full proof replay.
- Full historical replay belongs to explicit audit/super-smoke commands.
  Codex must not introduce heavy historical collector replay in targeted tests
  unless explicitly requested. If a new targeted proof imports heavy
  historical collectors, Codex must justify why replay is required.
- For new untracked files, ordinary `git diff --stat` is empty unless the files
  are staged. Codex must use `git status --short` and explicitly report that
  limitation instead of claiming `git diff --stat` shows the untracked changes.
- Do not use External DRS Pointer language to claim External DRS
  implementation, remote retrieval, connector/API access, trusted evidence,
  or public Internet of Meaning.
- Connector outputs are `ExternalObservation` / `ConnectorObservation` only.
  Do not name connector output trusted evidence before a future External
  Evidence Acceptance Gate explicitly accepts it.
- Clean connector output remains `observation_only`. Stale connector output
  remains blocked or quarantined. No connector response may finalize ready
  status, execute action, write DRS, install Needle, or bypass Root.
- AcceptedEvidence is bounded accepted evidence, not truth. It cannot create
  ready status, execute action, write DRS, install Needle, or bypass Root.
- EvidenceCandidate remains candidate-only and ValidationPacket remains
  non-final until Root decision. Neither may bypass Root.
- Mock signature, trust-registry, and revocation fields must never be
  described as real cryptographic signature validation, real trust registry,
  or real revocation registry.
- A high-capability LLM is a replaceable compute organ inside the
  Root-controlled runtime, not a sovereign cloud brain. Depending on its
  bounded role, it may propose routes, draft PlanGraphs, or produce semantic
  drafts, but it must not finalize, execute external actions, accept evidence,
  write DRS, install Needles, or bypass Root.
- Bounded LLM Semantic Executor Node v0.1 proves only the Executor-side flow:
  Architect-created PlanGraph -> Executor runs `llm_semantic_executor_node` ->
  mock LLM produces SemanticDraft -> Executor wraps ResultProposal -> Post V&V
  -> GT advisory -> Root Final. The LLM is `executor_node_capability`, not a
  new global actor or a layer between Architect and Executor.
- The deterministic local applied/fractal stack is closed through Travel,
  Multi-domain Applied Smoke v0.2, Controlled Fractal DAC Expansion v0.1, and
  Dual Fractal Coupling v0.1. Cross-domain DRS Bridge v0.1 adds local reviewed
  traversal only.
- Needle adversarial / safety pack v0.1 and External DRS Pointer Protocol v0.1
  are complete. Read-only Enterprise Connector Sandbox v0.1 is complete
  through proof, human walkthrough, audit, and docs. External Evidence
  Acceptance Gate v0.1 is complete. Bounded LLM Semantic Executor Node v0.1 is
  complete through proof, human walkthrough, wording cleanup, and audit.
  Enterprise Chaos Pack v0.1 is complete through proof, human walkthrough,
  audit, and docs sync. Compute Collapse Enterprise Bench v0.1 is complete
  through proof, human walkthrough, audit, and docs sync. Math / Invariants
  Sync v0.4 is complete. Kernel Enforcement / Transition Matrix Hardening
  v0.1 is complete through proof, human walkthrough, audit, and docs sync.
  Developer Facade / Capability Manifest UX v0.1 is complete through proof,
  human walkthrough, audit, and docs sync. Production Boundary Design Docs
  v0.1 is complete as design documentation. Enterprise Killer Demo v0.1 /
  Demo A is complete through proof, human walkthrough, audit, and docs sync.
  Enterprise Document Killer Demo B v0.1 is complete through design, proof,
  human walkthrough, audit, and docs sync. Schema Contract Alignment v0.1
  Phase 1 is complete through patch and audit: the active AttractorPacket
  Architect-facing contract now uses `must_return_plan_graph_only`, Architect
  returns PlanGraph only, Executor / DAG returns ResultProposal, and Root
  remains final authority. Schema Contract Alignment v0.1 Phase 2 is complete
  through patch and audit: it clarified Executor / DAG ResultProposal contract
  wording as docs/spec wording only, kept runtime/schema/tests unchanged, and
  preserved Root final authority. Runtime JSON Schema Validation Hardening
  v0.1 is complete through runtime patch and audit: Post V&V now validates
  incoming ResultProposal artifacts via runtime JSON Schema before manual
  checks, schema validation is additive, schema failures return the V&V report
  path without crashing, manual policy/safety checks remain preserved, and Root
  remains final authority. Current next decision: outgoing VVReport validation
  subphase or EvidenceItem.kind / artifact_type planning.
- Do not treat Enterprise Chaos Pack v0.1 as production readiness or use it to
  justify real external actions. Any future killer demo must still pass
  explicit Root-controlled production-boundary and acceptance gates.
- Enterprise Chaos Pack does not authorize Marennya, UP, a multi-LLM
  showcase, global/external DRS, installed Needles, or production persistence.
- Targeted proofs must continue using closed checkpoint metadata rather than
  replaying historical collectors unless an explicit audit/full-suite mode
  requires replay.
- Compute Collapse Enterprise Bench v0.1 is a synthetic estimate, not
  production economics. `hedgehog_llm_calls=1` is a routed-path estimate, not a
  real LLM call by docs, walkthrough, or audit.
- DRS reuse is not authority, and closed checkpoint metadata is not authority.
  Both are Root-approved semantic routing / reuse signals; Root remains final.
- Compute-collapse does not authorize external action, Killer Demo,
  multi-LLM showcase, Marennya, UP, installed Needles, global DRS, or External
  DRS write.
- Kernel Enforcement / Transition Matrix Hardening v0.1 is proof-only. The
  transition matrix is not Root, not authority, not production runtime
  authority, and not production enforcement. It does not replace Root or insert
  a new actor into the canonical runtime pipeline.
- Local DRS writeback in the transition matrix is `local_after_root_final`
  only: `local_drs_writeback=true`, `global_drs_write=false`, and
  `external_drs_write=false`.
- Future Developer Facade / Capability Manifest UX work must not bypass the
  transition matrix boundaries, Root authority, Post V&V, GT, policy, audit,
  or permission gates.
- Developer Facade / Capability Manifest UX v0.1 is proof-only developer-facing
  manifest validation. Developer Facade is not Root, capability manifest is not
  authority, and Transition Matrix remains non-authority.
- A validated manifest candidate is not installed capability, installed
  Needle, execution permission, accepted evidence, truth, Root FinalOutput, or
  production readiness.
- Production Boundary Design Docs v0.1 must document boundaries honestly. It
  must not implement production runtime, real APIs/connectors/actions,
  production persistence, installed Needles, Marennya runtime activation, UP
  runtime activation, or Killer Demo authorization.
- Production Boundary Design Docs v0.1 is not production implementation.
  Production boundary design does not create production security, authorize
  real external actions, authorize installed Needles or capabilities, authorize
  External/global DRS, or authorize Marennya / UP activation.
- Do not confuse Demo A and Demo B. Demo A = Authority / Safety / Compute
  Collapse. Demo B = Document / Evidence Workflow applied proof.
- Enterprise Document Killer Demo B v0.1 is complete as an applied
  deterministic proof, not a production document/workflow engine. It does not
  prove real OCR/PDF parsing, document extraction, connector trust, real
  shipment release, production DRS, production runtime, or general-purpose
  workflow generalization.
- Schema Contract Alignment v0.1 preflight scan is complete. Phase 1 closed
  only Finding A for the active AttractorPacket Architect-facing contract.
  Finding B is closed only for Post V&V incoming ResultProposal and outgoing
  VVReport runtime-schema boundaries.
  Findings C/D/E remain open or partially open: EvidenceItem.kind vocabulary
  alignment, artifact_type vocabulary alignment, and focused coverage gaps.
- Schema Contract Alignment v0.1 Phase 2 is complete through patch and audit.
  It reduced public contract ambiguity around Executor / DAG ResultProposal
  wording. ResultProposal-shaped boundary artifacts are not FinalOutput, are
  not authority, do not authorize action, and do not write DRS. Post V&V / GT /
  Root remain required after the ResultProposal boundary.
- Runtime JSON Schema Validation Hardening v0.1 is complete through runtime
  patch and audit. Post V&V validates incoming ResultProposal schema at
  runtime before manual checks; schema validation is additive and does not
  replace manual policy/safety checks. Schema failures return normal V&V report
  rejection path and do not crash. Audit evidence: preflight `3207a19`, runtime
  patch `48e2515`, audit `107a7c4`, with `38 passed, 2 warnings` and
  `54 passed, 2 warnings`; jsonschema.RefResolver deprecation warning is
  `non_blocking`.
- Outgoing VVReport Runtime Schema Validation v0.1 is complete through runtime
  patch and audit. Post V&V validates outgoing VVReport dictionaries before
  return; outgoing validation is additive, preserves incoming ResultProposal
  validation and manual policy/safety checks, and falls back to a safe
  schema-conforming rejected VVReport without calling GT/Root, writing DRS,
  executing action, or creating FinalOutput. Audit evidence: preflight
  `c6e1bf7`, runtime patch `187461d`, audit `916a913`, with
  `40 passed, 16 warnings` and `73 passed, 20 warnings`; jsonschema.RefResolver
  deprecation warning is `non_blocking`.
- EvidenceItem.kind Alignment v0.1 is complete through narrow patch and audit.
  It added only `fractal_dag_executor` to EvidenceItem.kind. EvidenceItem.kind
  remains a local ResultProposal evidence classification, not artifact_type,
  not a global artifact registry, and not authority. It does not create truth,
  AcceptedEvidence, action permission, DRS write, or FinalOutput. Root remains
  final authority. Audit evidence: plan `2685921`, patch `4ced110`, audit
  `0eb58c1`, with `25 passed, 22 warnings`; jsonschema.RefResolver
  deprecation warning is `non_blocking`.
- NeedleRuntime Audit Evidence Shape v0.1 is complete through narrow patch and
  audit. `audit` is allowed as local ResultProposal evidence
  support/provenance. `needle_runtime` remains trace_refs.kind only and is not
  EvidenceItem.kind. Audit evidence: preflight `99592a6`, patch plan
  `fd9e862`, patch `f0bf7be`, audit `0b2ffc8`, with `36 passed, 24 warnings`
  and `48 passed, 20 warnings`; jsonschema.RefResolver deprecation warning is
  `non_blocking`.
- artifact_type Mapping / Runtime Artifact Vocabulary v0.1 Option A docs/spec
  map is complete through audit. Audit evidence: preflight `b4aaf8e`, patch
  plan `c4f9a02`, map `d3193a2`, audit `27bee7d`. It separates artifact_type,
  source_artifact_type, EvidenceItem.kind, TraceRef.kind,
  lifecycle_state/status, and authority_status. It creates no registry, no
  enum, no runtime behavior, no schema change, and no tests. Next: Guardian
  review of Option A docs/spec map. Do not start Option B/C/D/E, runtime work,
  schema work, enum work, or registry work without review and explicit
  approval. Do not claim production readiness or public-auditor readiness.
  Continue the phase-gated workflow.
- Long-lived DRS TTL Aging Stress v0.1 is complete through proof, audit, docs
  sync, human walkthrough, and human walkthrough audit. Human walkthrough audit
  status: PASS_WITH_SCOPE_WARNING because full pytest has known global drift
  outside walkthrough scope. Next engineering layer: Full Suite Drift Triage /
  Repair v0.1. Do not jump to runtime, schema, production DRS, external/global
  DRS, Marennya, UP, Negative Trace, or artifact_type vocabulary work. Do not
  claim full suite green.
- Do not run broad schema hardening. Do not align artifact_type without a
  reviewed preflight/plan.
- Never tell Codex "fix schema hardening" broadly. Use phase-gated patches:
  define the narrow contract, patch only allowed files, and verify with
  focused tests.
- Manifest Auto-Hardening from AVF/DRS Negative Traces v0.1 remains
  post-Killer-Demo future extension.
- Codex must not run long tests unless the user explicitly requests them; the
  user runs long, focused, and full-suite tests manually.

### Targeted Proof Runtime And Replay Policy

- Targeted proof tests verify the new layer only. They must not replay
  historical collectors by default.
- A historical collector may be imported only when the current proof
  explicitly requires live recomputation of that previous layer. If Codex
  imports a heavy historical collector into a targeted proof, it must explain
  why replay is required and why committed checkpoint metadata is
  insufficient.
- Closed checkpoint metadata is acceptable only after the previous layer is
  closed by proof, human walkthrough, audit, and docs commits. Metadata-only
  reports must expose `source_evidence_mode=closed_checkpoint_metadata_only`
  and `source_collectors_replayed=false`.
- Closed checkpoint metadata is runtime-cost hygiene. It is not full
  historical proof replay and must never be presented as evidence that the
  previous stack was re-executed.
- Full historical replay belongs only to explicitly named, opt-in
  audit/super-smoke/full-suite modes. Use it for checkpoint audits, regression
  checks, or release gates, not ordinary targeted tests.
- Do not convert expected output into fake proof. Do not hide skipped
  collectors. If source evidence is metadata-only, state that directly.
- Do not claim trusted evidence, truth, External DRS implementation, real
  retrieval, connector/API access, installed Needle, or production autonomy
  unless the current layer actually proves it. Audit hash proves continuity,
  not truth.
- For untracked files, ordinary `git diff --stat` may be empty. Use
  `git status --short` to report them. Use `git diff --cached --stat` only
  after staging. Never describe an empty ordinary diff stat as no changes when
  untracked files exist.

See `docs/passport_geometry_root_needles.md`.

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
28. Large or malformed PlanGraphs must be bounded or blocked, not executed as uncontrolled flat graphs.
29. Graph proximity is a query-time ranking signal only; it does not override policy, validation, TimeEnvelope, GTTrust, or ReuseGate.
30. DeadEnds, Quarantine, blocked, failed, and degraded records must not become direct-reuse eligible because they are graph-near.
31. Showcase reports must be derived from existing proof outputs or structured collectors, not hardcoded PASS tables.
32. Chaos Survival Showcase is not production autonomy and must not imply live Gemini, Telegram actions, external DRS, global DRS, or real external actions.
33. Compute Collapse via DRS Reuse is an evidence aggregator, not a new runtime layer or billing benchmark.
34. Compute Collapse may say zero re-planning path or near-zero LLM cost path, but must not claim absolute zero cost or real token savings proven.
35. Direct reuse must require eligible Work and must not bypass Root.
36. DRS Layer Taxonomy clarifies broad DeadEnds semantics but does not change ReuseGate, schema layers, or direct reuse eligibility.
37. Taxonomy must not make quarantine, dead_end, blocked_trace, degraded_trace, or needs_user_trace records reusable.
38. Typed DRS Lineage Edges are query-time semantic signals only in v0.1; they must not override policy, ReuseGate, or direct reuse gates.
39. ReuseScore is advisory/ranking only; it is not Root, not ReuseGate, and not policy override.
40. High ReuseScore must not make Quarantine, dead_end, blocked_trace, degraded_trace, needs_user_trace, or contradiction-risk records direct-reuse eligible.
41. ReuseScore must send contradiction-risk candidates to needs_conflict_check until production ConflictCheck exists.
42. Semantic Reuse Pipeline may recommend and explain, but must not commit FinalOutput, bypass Root, bypass ReuseGate, execute direct reuse, or treat context memory as direct reuse.
43. Root Semantic Reuse Decision/Gate traces are dry-run proofs only; they must not change production RootOrchestrator behavior, execute direct reuse, create production FinalOutput, or write production Work records.
44. ReuseGate approval in the semantic reuse trace means return upward to Root final decision, not production execution.
45. Root Semantic Reuse Final Decision Trace is a dry-run proof only; it may create a trace-level Root final decision artifact, but not production FinalOutput, production direct reuse, external action, or production Work writeback.
46. Root-native Semantic Reuse E2E Trace is deterministic proof only; it may create a trace-level final answer artifact by Root, but it must not change production RootOrchestrator behavior, execute production direct reuse, create production FinalOutput, write production Work, call live Gemini, use Telegram actions, or implement global/external DRS.
47. Root-native Full Canonical E2E Trace is deterministic proof only; it may show local proof DRS writeback, but it must not claim production persistence, production reuse, production direct reuse, production external-action FinalOutput, live Gemini, Telegram action, global DRS, or external DRS.
48. Optional Live Gemini Architect Smoke is opt-in role substitution only. Gemini may substitute only the Architect proposal role and must not become Root, Orchestrator, Executor, GT, or FinalRenderer; create FinalOutput; write DRS; execute actions; or bypass AVF, PlanGraph contract, Executor, Post V&V, GT, Root, ReuseGate, policy, or permission gates.
49. Ordered Live Gemini Orchestrator-to-Architect Smoke is opt-in role substitution only. Gemini may act as Orchestrator proposal actor first and Architect proposal role second, but only after schema-backed local Orchestrator validation. Gemini must not become Root, create FinalOutput, write DRS, execute actions, bypass AVF / Architect contract / Executor / Post V&V / GT / Root / ReuseGate / policy / permission gates, or activate Marennya / UP by default.
50. Controlled Orchestrator Matrix Gate is deterministic proof only. Orchestrator matrix is an input artifact, not authority; Root creates RootMatrixGateDecision artifacts and may accept, reject, or downgrade. The layer must not invoke AVF / Attractor formation, reach Architect from invalid/rejected matrices, execute production actions, create FinalOutput, write DRS by Orchestrator, implement global/external DRS, or invoke Marennya / UP.
51. AVF / Attractor Formation from accepted Matrix is deterministic proof only. It may consume accepted or downgraded RootMatrixGateDecision outputs, but rejected matrices must not reach AVF. AVF remains independent; Orchestrator hints are hints, not commands; HardMask and policy beat Orchestrator confidence. This layer must not invoke Architect or Executor, create FinalOutput, write DRS, execute actions, implement global/external DRS, or invoke Marennya / UP.
52. Architect from bounded AttractorPacket is deterministic proof only. Architect receives only bounded AVF output, not raw Orchestrator matrix, raw unchecked user intent, rejected matrix, or invalid/unbounded AttractorPacket. Architect may produce PlanGraph proposal only; PlanGraph contract must be checked; invalid Architect output must be contained. This layer must not invoke Executor, Post V&V, or GT, create FinalOutput, write DRS, execute actions, implement global/external DRS, or invoke Marennya / UP.
53. DAG / Executor from valid PlanGraph is deterministic proof only. Executor receives only validated PlanGraph nodes, not invalid Architect artifact, raw Architect text, raw Orchestrator matrix, raw user intent, or unvalidated PlanGraph. Executor returns ResultProposal only and must not create FinalOutput, write DRS directly, execute real external actions, invoke Post V&V / GT, implement global/external DRS, or invoke Marennya / UP.
54. Post V&V from ResultProposal is deterministic proof only. Post V&V receives only ResultProposal artifacts, not raw Executor text, raw Architect PlanGraph, raw Orchestrator matrix, raw user intent, real action output, malicious claim payloads, or malformed ResultProposal shapes. It creates ValidationReport / V&VReport only and must not create FinalOutput, write DRS directly, execute actions, invoke GT / Root Final, implement global/external DRS, or invoke Marennya / UP.
55. GT from ValidationReport is deterministic proof only. GT receives only ValidationReport / V&VReport artifacts, not raw ResultProposal, raw Executor text, raw Architect PlanGraph, raw Orchestrator matrix, raw user intent, real action output, malicious claim payloads, or malformed ValidationReport shapes. It creates GTDecision / selection artifact only and must not create FinalOutput, write DRS directly, execute actions, invoke Root Final, implement global/external DRS, or invoke Marennya / UP.
56. Root Final from GTDecision is deterministic proof only. Root Final receives only GTDecision / selection artifacts, not raw ValidationReport, raw ResultProposal, raw Executor text, raw Architect PlanGraph, raw Orchestrator matrix, raw user intent, real action output, malicious GTDecision claims, or malformed GTDecision shapes. Root creates FinalOutput / trace-level final artifact only and is the only final-output authority. This layer must not write DRS, invoke DRS writeback, execute actions, claim production persistence, implement global/external DRS, or invoke Marennya / UP.
57. Applied Warehouse Semantic Demo v0.1 proves `not_ready` from explicit W-17 stock shortage and rejects an invalid ready certificate. Its applied PlanGraph, execution results, validation rows, GT selection, lifecycle records, ConflictReports, artifact, and audit entry must remain explicitly linked and consistency-checked.
58. Applied demos must not automatically create `protocol_candidate` or `needle_candidate` unless that lifecycle is explicitly under test.
59. Applied Certificate / Document Readiness Demo v0.1 proves `not_ready` from expired/missing documents and rejects an invalid ready certificate. It creates no protocol candidate, needle candidate, or installed needle.
60. Permission / NeedsUser UX Proof v0.1 rejects permission bypass and completed-action-without-execution claims. Permission is not execution, proof-only approval is future-action permission only, user denial remains blocked, `needs_user` is not failure, and the proof creates no protocol candidate, needle candidate, or installed needle.
61. NeedleCandidate lifecycle / NeedleForge prototype v0.1 may create bounded proof-level NeedleCandidate objects only. NeedleCandidate is not an installed Needle; GT cannot install needles; Root alone disposes candidates as pending review, rejected, or quarantined; production persistence, global DRS writes, external actions, and bypassing Root remain forbidden.
62. Applied DRS Retrieval / Reuse v0.1 is deterministic local proof only. DRS retrieval is not authority, ReuseScore is not Root, semantic similarity is insufficient, and Root alone decides final reuse after freshness, WorldState, permission, quarantine/deadend, ConflictCheck, GT, and audit boundaries. This layer creates no protocol candidate, NeedleCandidate, installed needle, direct ready, completed external action, production persistence, or global/external DRS write.

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

## Large Graph / Bounded Fractal Stress

`python -m demo.run_large_graph_stress` proves deterministic bounded behavior for oversized or malformed PlanGraphs. It demonstrates max_nodes, max_edges, max_depth, max_parallelism, cycle detection, unknown dependency detection, child boundary snapshots, and bounded GT candidate summaries.

This does not prove production 10k-node execution. It shows that oversized or malformed graphs are blocked or bounded instead of attempted as uncontrolled flat execution. The stress runner does not call the real GTValidator runtime; it reports `gt_runtime_called: false` and `gt_boundary_mode: bounded_summary_check`. The raw large graph is not sent to GT. The DAG runner remains after Architect and is not Root.

## DRS Graph Proximity / Lineage

`python -m demo.run_drs_graph_proximity` proves a LocalDRS-only read-only ranking signal. Records store links through lineage/source refs; they do not store static `hops_ago`, `hop_distance`, or `graph_distance`. Graph distance is computed at query time, and GraphProximity uses:

```text
graph_proximity = 2 ** (-distance / hop_half_life)
```

GraphProximity does not change ReuseGate and does not override policy. Nearby DeadEnds are warning signals, nearby Quarantine records are quarantine signals, and neither becomes a direct-reuse candidate. External/global DRS remains future work.

---

## Chaos Survival Showcase

`python -m demo.run_chaos_survival_showcase` is an auditor-facing showcase over existing deterministic proof modules:

- NeedleRuntime Chaos;
- Canonical Needle Outcome Trace with real GTValidator integration;
- Needle Outcome DRS Routing Persistence;
- Large Graph / Bounded Fractal Stress;
- DRS Graph Proximity / Lineage.

It is not a new runtime layer. It summarizes timeout containment, quarantine routing, blocked permission/circuit-breaker cases, unsafe reuse candidates = 0, bad outcomes written to successful Work = 0, bounded/malformed graph survival, graph proximity policy safety, Root authority, no Executor/needle FinalOutput, no GT commit, no live Gemini, no Telegram actions, and no real external actions. Its PASS summary must be derived from computed section predicates.

Compute Collapse via DRS Reuse / Zero Re-Planning Path / Near-Zero LLM Cost Path is complete. Do not claim absolute zero cost.

---

## Compute Collapse via DRS Reuse

`python -m demo.run_compute_collapse_reuse_showcase` is an auditor-facing showcase over existing deterministic cold-start, Root direct reuse, LocalDRS, ReuseGate, and unsafe DRS routing proofs. It complements Chaos Survival Showcase: Chaos Survival demonstrates resilience / safety / containment, while Compute Collapse demonstrates efficiency / reuse / zero re-planning path.

It shows four scenarios:

- cold_start_full_pipeline: full pipeline, no direct reuse, Architect/Executor run, Post V&V and GT run, Root creates FinalOutput, and DRS writeback occurs.
- memory_context_only: memory_context_applied=true, direct_reuse_applied=false; context memory does not bypass Architect/Executor without eligibility.
- eligible_direct_reuse: direct_reuse_applied=true; Architect and Executor/DAG are skipped, result is sourced from eligible Work, and Root still creates FinalOutput.
- unsafe_records_not_reused: Quarantine, DeadEnds, failed, blocked, and degraded records are not direct-reuse candidates.

Compute units are illustrative deterministic units derived from route flags. They are not real token billing. Do not claim absolute zero cost, real token savings proven, or production billing benchmark.

DRS Layer Taxonomy v0.1 returns development to runtime hardening after the showcase pair. It is a LocalDRS taxonomy/reporting semantics layer, not a schema refactor and not a ReuseGate change.

It classifies the broad MVP DeadEnds semantics into:

- work_candidate / successful_work: accepted successful Work; the only direct-reuse eligible case in this demo.
- quarantine: invalid_json, schema_validation_failed, unknown_exception / failed payloads; not Work and not direct-reuse eligible.
- dead_end: stable bad route, such as contract_version_mismatch / contract_boundary.
- blocked_trace: guard, policy, permission boundary, circuit breaker, or runtime safety block.
- degraded_trace: timeout, partial failure, or service instability; not successful Work.
- needs_user_trace: user confirmation, permission, or missing human input required; not completed action.

Safety flags such as taxonomy_does_not_override_policy, broad_deadends_semantics_clarified, and direct_reuse_policy_unchanged must be derived from classified rows, not hardcoded.

Typed DRS Lineage Edges v0.1 is the completed hardening step after taxonomy. It is LocalDRS-only typed-edge proof, not a schema refactor, not a ReuseGate change, not ReuseScore, not ConflictCheck, and not global/external DRS.

It distinguishes:

- derived_from;
- same_trace;
- warns_against;
- blocked_by_policy;
- requires_user;
- degraded_from;
- supports;
- contradicts.

Typed edges are semantic signals only in v0.1. `supports` and `derived_from` may provide positive or lineage evidence but cannot make a target directly reusable by themselves. `warns_against` is warning evidence, `blocked_by_policy` is blocking evidence, `requires_user` is needs-user evidence, `degraded_from` is degradation evidence, and `contradicts` is contradiction evidence. A contradiction source is not reused, but the target is not auto-blocked by typed edges alone.

ReuseScore v0.1 is the next completed hardening step. It is a LocalDRS-only advisory/ranking proof that consumes Typed DRS Lineage Edges candidates and computes deterministic illustrative scores from visible signals: quality, freshness, gt_trust, semantic_similarity, graph_proximity, typed_positive_signal, warning_penalty, blocking_penalty, needs_user_penalty, degraded_penalty, contradiction_penalty, and risk_penalty. Raw score calculation and policy gates remain separate. ReuseScore does not change ReuseGate, bypass Root, implement production ConflictCheck, implement global/external DRS, make unsafe records reusable, claim real token billing, or claim production autonomy.

Safety examples: a high-ish scoring unsafe `blocked_trace` remains not reusable because `policy_allowed=false`; a `work_candidate` with contradiction_penalty becomes `needs_conflict_check` rather than direct reuse; `unsafe_direct_reuse_candidates` remains 0. ReuseScore is not Root, not ReuseGate, and not policy override.

Semantic Reuse Pipeline Integration v0.1 is the next completed engineering integration proof. It connects LocalDRS retrieval → taxonomy-aware filtering → typed edge interpretation → graph proximity → ReuseScore → ReuseGate / Root boundary → direct reuse candidate or full pipeline fallback. It structurally consumes `collect_reuse_score()`, preserves the source Typed DRS Lineage Edges report, evaluates scenario rows, and separates recommendations from authority. It is not production RootOrchestrator integration, production autonomy, global DRS, external DRS, a ReuseGate replacement, a bypassing Root, direct reuse execution, FinalOutput creation, real external action, live Gemini, or Telegram action.

Scenario semantics: `eligible_direct_reuse_candidate` is recommended but not committed by the pipeline; `context_memory_not_reuse` falls back to full pipeline because context memory is not direct reuse; `contradiction_needs_conflict_check` routes to needs_conflict_check; high score does not override policy; quarantine is not reused; needs_user is not completed action; degraded trace is not stable success; dead_end is not reused.

Safety flags: semantic_pipeline_committed_final_output=false, semantic_pipeline_bypassed_root=false, semantic_pipeline_bypassed_reuse_gate=false, root_boundary_preserved=true, reuse_gate_boundary_preserved=true, unsafe_reuse_candidates=0, production_autonomy_claimed=false, local_drs_only=true, external/global DRS not implemented. PASS must be derived from stages, scenarios, and boundary facts, not hardcoded.

Root-controlled Semantic Reuse Decision Trace v0.1 is complete. It is a deterministic Root-controlled dry-run proof that consumes Semantic Reuse Pipeline recommendations. It does not change production RootOrchestrator behavior, execute direct reuse, create production FinalOutput, write production Work records, or grant authority to the semantic pipeline. Decision mapping: direct_reuse_candidate → root_accepts_direct_reuse_candidate_for_gate_review; needs_full_pipeline → root_selects_full_pipeline_fallback; needs_conflict_check → root_requires_conflict_check; blocked → root_blocks_policy_blocked_route; quarantine → root_routes_to_quarantine; needs_user → root_requires_user_input; degraded → root_marks_degraded_trace; dead_end → root_rejects_dead_end.

Root-controlled Semantic Reuse Gate Trace v0.1 is complete. It is a deterministic Root/ReuseGate dry-run proof that consumes the Root decision trace. Gate review happens only for the Root-approved direct reuse candidate. Non-direct-reuse routes remain non-gate routes: full pipeline fallback, conflict check required, policy blocked, quarantine, needs_user, degraded, and dead_end. `gate_review_accepts_candidate_for_root_final_decision` means candidate returns upward to Root; it is not production execution. ReuseGate does not create FinalOutput, does not execute direct reuse, semantic pipeline does not commit, and Root keeps final authority.

Root-controlled Semantic Reuse Final Decision Trace v0.1 is complete. It is a deterministic Root-controlled dry-run proof that consumes the Root Semantic Reuse Gate Trace. It does not change production RootOrchestrator behavior, execute production direct reuse, create production FinalOutput, perform real external actions, write production Work records, or grant authority to the semantic pipeline or ReuseGate. It creates only a trace-level Root final decision artifact. Final decisions map gate outcomes explicitly: gate-approved direct reuse candidate → root_final_accepts_controlled_direct_reuse_trace; full pipeline fallback → root_final_selects_full_pipeline_fallback; conflict check → root_final_requires_conflict_check; policy blocked → root_final_blocks_policy_route; quarantine → root_final_routes_to_quarantine; needs_user → root_final_requires_user_input; degraded → root_final_marks_degraded_trace; dead_end → root_final_rejects_dead_end. `root_final_accepts_controlled_direct_reuse_trace` is still trace/dry-run, and the trace final decision artifact is not production FinalOutput.

Root-native Semantic Reuse E2E Trace v0.1 is complete. It is the first deterministic end-to-end semantic reuse trace and consumes the Semantic Reuse Authority Stack Audit. The connected path is input task → TemporalQuery → LocalDRS retrieval → taxonomy-aware filtering → typed edge interpretation → graph proximity → ReuseScore → semantic reuse recommendation → Root decision → ReuseGate review → Root final dry-run decision → trace-level final answer artifact → audit visibility. It does not change production RootOrchestrator behavior, execute production direct reuse, create production FinalOutput, write production Work records, perform real external actions, use live Gemini, use Telegram actions, or implement global/external DRS.

Selected scenario: `eligible_direct_reuse_candidate` maps direct_reuse_candidate → root_accepts_direct_reuse_candidate_for_gate_review → gate_review_accepts_candidate_for_root_final_decision → root_final_accepts_controlled_direct_reuse_trace, producing `trace_level_final_answer_artifact` by `root_orchestrator`. production_final_output=false, production_action_executed=false, production_work_record_written=false, unsafe_reuse_candidates=0, and production_autonomy_claimed=false. Proof status: E2E stages passed=12, focused tests passed=229, full suite passed=749, and the sensitive scan found no secret terms.

Root-native Full Canonical E2E Trace v0.1 is complete. It is a deterministic full canonical E2E proof that composes a first-run canonical Root-controlled path with a second-run semantic reuse authority path. The first run covers input task → Root intake / Orchestrator boundary → Architect / PlanGraph → AVF / Attractor formation → DAG / Executor → ResultProposals → Post V&V → GT → Root trace artifact → LocalDRS writeback / audit visibility. The second run covers repeat/similar task → TemporalQuery → LocalDRS retrieval → taxonomy / typed edges / graph proximity → ReuseScore → Semantic Pipeline recommendation → Root decision → ReuseGate review → Root final dry-run decision → trace-level semantic reuse answer artifact.

Full Canonical E2E safety: first_run_created_root_trace_artifact=true, first_run_local_drs_writeback_visible=true, first_run_local_work_record_written_in_proof=true, bridge_mode=deterministic_proof_linkage, production_persistence_claimed=false, production_reuse_claimed=false, production_direct_reuse_executed=false, production_final_output_created=false, production_work_record_written=false, no_live_gemini=true, no_telegram_actions=true, no_global_drs=true, no_external_drs_network=true, and production_autonomy_claimed=false. Proof status: first_run_stages_passed=9, second_run_stages_passed=12, focused tests passed=250, full suite passed=770, sensitive scan found no secret terms, commit=83f59a2 Add Root-native full canonical E2E trace.

Optional Live Gemini Architect Smoke v0.1 is complete. It is an opt-in smoke proof for substituting only the Architect proposal role inside the Full Canonical E2E boundary. Default mode is `dry_run_default`, deterministic, network-free, uses a deterministic mock Architect artifact, does not call live Gemini, and keeps `plan_graph_contract_checked=true`. Live mode requires explicit `--live`, `HEDGEHOG_ALLOW_LIVE_GEMINI=1`, and Gemini configuration; missing config reports SKIPPED rather than crashing, and invalid live artifacts are contained, do not reach Executor or Root final output, and fall back visibly to deterministic Architect. Boundary checks derive from the Full Canonical E2E source report, role flags, artifact containment, and context facts; rendered output does not print credential environment names or secret terms. Proof status: focused tests passed=212, full suite passed=788, sensitive scan found no secret terms, default dry-run status PASS, and `ready_for_future_orchestrator_live_smoke=true`.

Ordered Live Gemini Orchestrator-to-Architect Smoke v0.1 is complete. It proves an opt-in ordered role-substitution path: Root boundary → live Gemini Orchestrator proposal → schema-backed local validation → live Gemini Architect proposal → Architect contract check → no production execution. Final success evidence is `docs/audit_reports/auditor_live_gemini_ordered_orchestrator_architect_25_success_report.log`: orchestrator_initial_attempt_valid=true, orchestrator_active_proposal_source=live_gemini, orchestrator_active_proposal_is_fallback=false, temporal_query_required_value=true, downstream_actors_missing=[], downstream_actors_extra=[], architect_artifact_source=live_gemini, architect_artifact_valid=true, production_final_output_created=false, and production_external_action_executed=false. Older ordered Gemini fallback reports are historical safety evidence only and must not be used as proof of dual-live success.

Controlled Orchestrator Matrix Gate v0.1 is complete. It is a deterministic Root-controlled gate proof: Orchestrator matrix is an input artifact, not authority; Root creates RootMatrixGateDecision artifacts and may accept, reject, or downgrade. Verified scenarios: valid_matrix_accept accepted; missing_temporal_query_reject rejected; incomplete_guards_downgrade_or_reject downgraded with missing guards listed and unsafe_claims_removed=true; wrong_downstream_actors_reject rejected with missing/extra actor diagnostics; forbidden_bypass_reject rejected; high_confidence_policy_block rejected with high_confidence_overrides_policy=false and policy_beats_orchestrator_confidence=true; fallback_route_visible keeps fallback visible but not executed. Proof status: scenarios_verified=7, accepted_count=1, rejected_count=5, downgraded_count=1, focused tests passed=110, full suite passed=859, sensitive scan found no secret terms. Evidence: `docs/audit_reports/auditor_controlled_orchestrator_matrix_gate_report.log`.

Gate evidence hygiene: the runner verifies `docs/audit_reports/auditor_live_gemini_ordered_orchestrator_architect_25_success_report.log` before using ordered live Gemini context. success_report_exists=true, success_report_verified=true, success_report_missing_markers=[], ordered_live_context_mode=success_report_verified, live_orchestrator_can_create_valid_matrix=true, and live_architect_can_create_valid_artifact=true. Boundary semantics: AVF, AttractorPacket, Architect, Executor, Post V&V, and GT are not reached in this layer; Orchestrator does not write DRS or create FinalOutput; production_final_output_created=false; production_external_action_executed=false; global/external DRS are not implemented; Marennya / UP are not invoked.

AVF / Attractor Formation from accepted Matrix v0.1 is complete. It consumes Controlled Orchestrator Matrix Gate v0.1 without hardcoding Matrix Gate PASS and forms AttractorPacket-like artifacts only from accepted or downgraded RootMatrixGateDecision outputs. valid_matrix_accept forms a packet; incomplete_guards_downgrade_or_reject forms a limited packet with downgraded claims visible; missing_temporal_query_reject, high_confidence_policy_block, forbidden_bypass_reject, and wrong_downstream_actors_reject are blocked before AVF. rejected_matrix_packets=0, rejected_matrices_blocked_before_avf=true, attractor_packets_created=2, accepted_matrix_packets=1, downgraded_matrix_packets=1, focused tests passed=91, full suite passed=880, and sensitive scan found no secret terms. Evidence: `docs/audit_reports/auditor_avf_attractor_from_accepted_matrix_report.log`.

Architect from bounded AttractorPacket v0.1 is complete. It consumes AVF / Attractor Formation from accepted Matrix v0.1 without hardcoding AVF PASS. Architect receives only bounded AVF output, not raw Orchestrator matrix, raw unchecked user intent, rejected matrix, or invalid/unbounded AttractorPacket. Accepted bounded packets and downgraded bounded packets create valid PlanGraph proposals; rejected matrix, raw Orchestrator matrix, raw unchecked user intent, and invalid/unbounded packet inputs are blocked; invalid Architect artifact is contained. PlanGraph contract is checked, Executor / Post V&V / GT are not invoked, Architect does not create FinalOutput, write DRS, or execute actions, and Marennya / UP remain deferred. Proof status: scenarios_verified=7, valid_plan_graph_proposals_created=2, focused tests passed=93, full suite passed=903, sensitive scan found no secret terms. Evidence: `docs/audit_reports/auditor_architect_from_bounded_attractor_packet_report.log`.

DAG / Executor from valid PlanGraph v0.1 is complete. It consumes Architect from bounded AttractorPacket v0.1 without hardcoding Architect PASS. Executor receives only validated PlanGraph nodes; invalid Architect artifact, raw Architect text, raw Orchestrator matrix, raw user intent, and unvalidated PlanGraph are blocked. Accepted valid PlanGraph creates ResultProposal; downgraded valid PlanGraph creates limited/degraded ResultProposal. Executor returns ResultProposal only, does not create FinalOutput, write DRS directly, or execute real external actions, and Post V&V / GT are not invoked. Proof status: scenarios_verified=7, result_proposals_created=2, focused tests passed=85, full suite passed=923, sensitive scan found no secret terms. Evidence: `docs/audit_reports/auditor_dag_executor_from_valid_plan_graph_report.log`.

Post V&V from ResultProposal v0.1 is complete. It consumes DAG / Executor from valid PlanGraph v0.1 without hardcoding DAG / Executor PASS. Post V&V receives only ResultProposal artifacts; raw Executor text, raw Architect PlanGraph, raw Orchestrator matrix, raw user intent, and real action output are blocked. Completed ResultProposal creates an accepted ValidationReport, degraded ResultProposal creates a degraded ValidationReport, malicious FinalOutput and DRS write claims are rejected, and malformed ResultProposal is rejected. Post V&V creates ValidationReport / V&VReport only, does not create FinalOutput, write DRS directly, execute actions, invoke GT, or invoke Root Final. Proof status: scenarios_verified=10, validation_reports_created=5, rejected_validation_reports=3, focused tests passed=87, full suite passed=946, sensitive scan found no secret terms. Evidence: `docs/audit_reports/auditor_post_vv_from_result_proposal_report.log`.

GT from ValidationReport v0.1 is complete. It consumes Post V&V from ResultProposal v0.1 without hardcoding Post V&V PASS. GT receives only ValidationReport / V&VReport artifacts; raw ResultProposal, raw Executor text, raw Architect PlanGraph, raw Orchestrator matrix, raw user intent, and real action output are blocked. Accepted, degraded, and rejected ValidationReports create accept/degrade/reject GTDecision artifacts. Malicious FinalOutput, DRS write, and action execution claims are rejected; malformed ValidationReport is rejected. GT creates GTDecision / selection artifact only, does not create FinalOutput, write DRS directly, execute actions, or invoke Root Final. Proof status: scenarios_verified=13, gt_decisions_created=7, rejected_gt_decisions=5, focused tests passed=91, full suite passed=971, sensitive scan found no secret terms. Evidence: `docs/audit_reports/auditor_gt_from_validation_report.log`.

Root Final from GTDecision v0.1 is complete. It consumes GT from ValidationReport v0.1 without hardcoding GT PASS. Root Final receives only GTDecision / selection artifacts; raw ValidationReport, raw ResultProposal, raw Executor text, raw Architect PlanGraph, raw Orchestrator matrix, raw user intent, and real action output are blocked. Accept/degrade/reject GTDecision artifacts create accepted/degraded/rejected RootFinalArtifact outputs. Malicious GT FinalOutput, DRS write, and action claims are rejected; malformed GTDecision is rejected. Root is the only FinalOutput authority, GT does not create FinalOutput, Root does not write DRS, DRS writeback is not invoked, no production persistence is claimed, and Marennya / UP remain deferred. Proof status: scenarios_verified=14, root_final_artifacts_created=7, rejected_root_final_artifacts=5, focused tests passed=94, full suite passed=997, sensitive scan found no secret terms. Evidence: `docs/audit_reports/auditor_root_final_from_gt_decision.log`.

DRS Writeback / Audit from Root Final v0.1 is complete. It is a deterministic proof-level boundary that actually consumes `collect_root_final_from_gt_decision()` without hardcoding Root Final PASS. Only valid RootFinalArtifact inputs create `local_audit_only` records. Raw upstream artifacts and real action output are blocked; malformed RootFinalArtifact inputs and malicious global DRS, external DRS network, production persistence, Root DRS write, and real action claims are rejected. DRS is not the full memory, a decision authority, or a vector store; it is an address/resonance/lineage/audit layer for Root-authorized memory access, while Root remains commit authority. Proof status: scenarios_verified=16, writeback records=3 (accepted/degraded/rejected=1/1/1), focused tests passed=98, full suite passed=1037, sensitive scan found no secret terms. Evidence: `docs/audit_reports/auditor_drs_writeback_from_root_final.log`.

Root-native sandbox NeedleRuntime E2E v0.1 is complete. It sources a validated PlanGraph node from the existing Architect proof and demonstrates Root-approved bounded sandbox/mock capability execution through NeedleExecutionResult → ResultProposal → Post V&V → GTDecision → Root FinalArtifact. NeedleRuntime is not authority; needle outcome is evidence, not final truth; degraded/blocked/failed outcomes remain visible; raw output and malicious FinalOutput, DRS write, bypassing Root, and external-action claims are rejected. Proof status: PASS, scenarios_verified=11, completed/degraded/blocked_or_failed=1/1/4, malicious_claims_rejected=4, focused tests passed=70, full suite passed=1057, sensitive scan clear. Evidence: `docs/audit_reports/auditor_root_native_sandbox_needleruntime_e2e.log`.

Fractal Cell Runtime v0.1 is complete. It proves the third execution route inside a parent PlanGraph: atomic node → ordinary Executor; needle-bound node → sandbox NeedleRuntime; non-atomic node with `child_cell_required=true` → bounded child fractal cell. This is not a long chain. The deterministic child mini-cell may run child Orchestrator / Architect / Executor roles, returns ChildBoundarySnapshot upward, and is adapted into a ResultProposal-compatible artifact visible to Post V&V, GT, and Root Final. Completed, degraded, blocked, and failed child states remain visible.

Child-cell boundaries: child cell and child Orchestrator are not Root; child output is boundary evidence, not final truth; no child FinalOutput, parent DRS write, real external action, or live child LLM/SLM is allowed. Recursion and execution remain bounded by depth and budget, and parent DRS promotion requires Root. ChildBoundarySnapshot is addressable experience, not an installed needle; successful traces do not automatically create needles. Proof status: PASS, scenarios_verified=12, completed/degraded/blocked_or_failed=1/1/2, malicious_child_claims_rejected=5, focused tests passed=56, full suite passed=1069, sensitive scan clear. Evidence: `docs/audit_reports/auditor_fractal_cell_runtime.log`.

Live Child Executor in Fractal Cell v0.1 is complete. It is an opt-in live Gemini proof inside one bounded child cell, not a long chain. Gemini substitutes only child Executor, receives one Architect-provided bounded node contract rather than a free instruction, and returns ChildExecutionResult JSON/evidence only. It is not child Orchestrator, child Architect, Root, FinalOutput, DRS writeback, a needle, a protocol template, or production action execution.

Verified live behavior: the proof-only task completed and reached accepted Root Final; the action-like request was detected, blocked, and preserved through ChildBoundarySnapshot, parent adapter, Post V&V, GT, and rejected Root Final with no hidden success. Live status=PASS, live opt-in/network used, child Executor only, no fallback, malicious_claims_rejected=6, no child FinalOutput, parent DRS write, API/tool call, real action, bypassing Root, or Post V&V / GT / bypassing Root. Deterministic safe-fallback proof and live PASS evidence: `docs/audit_reports/auditor_live_child_executor_in_fractal_cell_deterministic.log` and `docs/audit_reports/auditor_live_child_executor_in_fractal_cell_LIVE.log`. Focused deterministic tests passed=36, full suite passed=1082, sensitive scan clear.

DRS Lifecycle Semantics v0.2 is complete. It consumes the current DRS writeback, sandbox NeedleRuntime, Fractal Cell Runtime, and deterministic Live Child Executor collectors and creates local/proof-level, pointer-first ExperienceRecord objects. It represents completed, degraded, blocked, failed, rejected, quarantined, deadend, and promotion_candidate states plus experience_record, reuse_candidate, protocol_candidate, needle_candidate, and supported installed_needle_ref stages. installed_needle_count=0 and automatic needle creation remains blocked.

Lifecycle trust and TTL hints are advisory; quarantine release, deadend override, promotion, reuse, and commit remain Root-controlled. DRS remains address/resonance/lineage/audit, not full memory, decision authority, vector store, automatic NeedleFactory, or external/global DRS. Proof status: PASS, records_created=13, malicious_claims_rejected=5, focused tests passed=75, full suite passed=1097, sensitive scan clear. Evidence: `docs/audit_reports/auditor_drs_lifecycle_semantics.log`.

ConflictCheck v0.1 is complete. It consumes the 13 ExperienceRecord objects from `collect_drs_lifecycle_semantics()`, creates 11 ConflictCandidatePair objects, and emits 11 ConflictReport objects. It represents 10 contradiction/risk families plus one compatible completed-lineage no-conflict case. Lifecycle records remain unchanged.

ConflictCheck recommendations are advisory until Root. It may recommend Root/GT review, reuse/promotion blocks, quarantine review, or invalidation review, but it does not decide truth, mutate DRS, invalidate, promote, demote, delete, rewrite, or commit. DRS remains storage/index/lifecycle, not judge. Proof status: PASS, candidate_pairs_created=11, conflict_reports_created=11, flagged_conflicts=6, root_review_required_reports=10, no_conflict_reports=1, malicious_claims_rejected=8, focused tests passed=47, full suite passed=1116, sensitive scan clear. Evidence: `docs/audit_reports/auditor_conflictcheck.log`.

Audit / hash-chain hardening v0.1 is complete. It consumes the current proof collectors and creates seven deterministic append-only evidence links across Root Final / DRS writeback, NeedleRuntime, ChildCell, deterministic Live Child Executor reference, DRS Lifecycle, ConflictCheck, and the final checkpoint. Proof status: PASS, chain_continuity_valid=true, tamper_detection_valid=true, source_artifacts_unchanged=true, malicious_claims_rejected=8, focused tests passed=49, full suite passed=1131 with 37 warnings, sensitive scan clear. Evidence: `docs/audit_reports/auditor_audit_hash_chain.log`.

Audit/hash-chain is tamper-evident proof linkage only. Hash-chain proves continuity, not truth. It is not authority, persistence, blockchain, semantic validation, GT, ConflictCheck, or Root; it must not mutate DRS or source artifacts.

Controlled RootOrchestrator Route Assembly Integration v0.1 is complete. It is a standalone deterministic route-assembly integration proof that consumes existing collectors and verifies boundary continuity; it does not replace production RootOrchestrator runtime. The Orchestrator-stage has delegated bounded route-assembly authority only.

Orchestrator may propose route-assembly fields, but every proposal must pass Root / MatrixGate / RouteGate / Policy / AVF before reaching Architect. Orchestrator proposes AVF inputs; it does not manage AVF. AVF / HardMask remain independent and stronger than Orchestrator confidence. Orchestrator is not Root and must not create FinalOutput, write DRS, execute actions, call needles directly, install needles, promote candidates, release quarantine, mutate ConflictReports, decide truth, or grant authority.

Current status: Root-centered proof geometry now includes controlled route assembly, Gate / AVF constraints, bounded planning/execution contracts, Root Final, DRS Lifecycle, ConflictCheck, proof-level audit/hash linkage, NeedleCandidate review boundaries, and applied DRS retrieval/reuse candidate review. Pipeline traces remain observable projections, not the architecture.

Applied DRS Retrieval / Reuse v0.1 is complete. It verifies seven deterministic scenarios in which DRS retrieves prior applied evidence and proposes bounded reuse modes while Root retains final authority. Stale, quarantined, deadend, wrong-domain, and permission-as-completed-action candidates cannot direct-reuse. This layer consumes NeedleCandidate source proof but creates no new NeedleCandidate or installed needle. Evidence: `docs/audit_reports/auditor_applied_drs_retrieval_reuse.log` and `docs/audit_reports/auditor_applied_drs_retrieval_reuse_postcommit.log`.

Applied Stack Checkpoint — DRS Adversarial / Super-Smoke / Human Walkthrough is complete. DRS adversarial stress blocks eight hostile memory attacks; the super-smoke observes eight PASS layers under Root-only final authority; and the walkthrough explains the completed stack without creating a proof or capability layer. No real action, direct ready, installed needle, production persistence, global/external DRS write, Gemini/network/Telegram call, Marennya, or UP is activated.

Applied + Fractal + Coupling checkpoint is complete. Travel readiness,
Multi-domain Applied Smoke v0.2, Controlled Fractal DAC Expansion v0.1, and
Dual Fractal Coupling v0.1 preserve Root-only final authority. Child-cell
candidates are local proof structures, and coupling is bounded semantic
resonance that informs but does not decide.

Cross-domain DRS Bridge v0.1 is complete as local proof-only traversal over
bounded semantic coupling edges. It creates local bridge records and traversal
evidence, but does not implement External DRS, global DRS, remote retrieval,
public semantic fabric, or production persistence. Bridge traversal can inform
but cannot decide, finalize, execute, transfer authority, or prove truth.

Needle adversarial / safety pack v0.1 is complete. It blocks eight escalation
attempts across retrieval, bridge traversal, coupling, child cells, DAG, GT,
audit, and NeedleCandidate boundaries; provenance laundering is quarantined
and blocked. It does not implement NeedleFactory, production installation,
External DRS, production RAG, or autonomy.

External DRS Pointer Protocol v0.1 is complete as a local proof-only pointer
protocol. Two pointer candidates are observed, zero accepted, and all six
escalation attempts are blocked; unknown-source laundering is quarantined and
blocked. Pointer claims remain untrusted and non-final. Targeted tests use
closed-checkpoint metadata with `source_collectors_replayed=false`; explicit
audit/super-smoke runs own full historical replay.

Read-only Enterprise Connector Sandbox v0.1 is complete through proof, human
walkthrough, and audit. It creates four local read-only observations and
blocks six connector escalation attempts. Connector response is not truth or
authority; connector observation is not trusted evidence or ready status.
The connector checkpoint does not itself implement evidence acceptance;
External Evidence Acceptance Gate v0.1 is a separate completed proof layer.

External Evidence Acceptance Gate v0.1 is complete through proof, human
walkthrough, and audit. Root accepts two clean candidates, rejects three, and
quarantines one. AcceptedEvidence remains bounded and non-executable; mock
validation is not real cryptographic or registry validation.

Bounded LLM Semantic Executor Node v0.1 is complete through docs sync. It keeps the
LLM inside Executor as `executor_node_capability`; Architect creates PlanGraph
before LLM execution, and Post V&V, GT, and Root remain mandatory. The LLM
does not create or modify PlanGraph, route, accept evidence, prove truth,
create ready status, execute action, write DRS, install Needle, or create Root
Final.

Enterprise Chaos Pack v0.1 is complete through docs sync. It combines dirty
connector, evidence, DRS reuse, external pointer, bridge, SemanticDraft,
NeedleCandidate, child-cell, GT, audit, permission, and ResultProposal
escalations. All 18 attempts remain blocked; four are quarantined and blocked.
Root remains final authority.

Compute Collapse Enterprise Bench v0.1 is complete through proof, human
walkthrough, audit, and docs sync. It extends the earlier compute-collapse
benchmark onto the dirty enterprise stack with a synthetic proof-level signal only:
29 estimated baseline LLM calls vs 1 bounded Hedgehog routed-path estimate,
and context units 180 -> 32. It is not real billing, latency, cloud cost, or
production economics.

Corrected engineering order: Compute Collapse Enterprise Bench v0.1 is complete through proof, human walkthrough, audit, and docs sync. Math / Invariants Sync v0.4 is complete. Kernel Enforcement / Transition Matrix Hardening v0.1 is complete through proof, human walkthrough, audit, and docs sync. Developer Facade / Capability Manifest UX v0.1 is complete through proof, human walkthrough, audit, and docs sync. Production Boundary Design Docs v0.1 is complete as design documentation. Enterprise Killer Demo v0.1 / Demo A is complete through proof, human walkthrough, audit, and docs sync. Enterprise Document Killer Demo B v0.1 is complete through design, proof, human walkthrough, audit, and docs sync. Schema Contract Alignment v0.1 Phase 1 is complete through patch and audit. Schema Contract Alignment v0.1 Phase 2 is complete through patch and audit. Runtime JSON Schema Validation Hardening v0.1 is complete through runtime patch and audit for Post V&V incoming ResultProposal validation. Outgoing VVReport Runtime Schema Validation v0.1 is complete through runtime patch and audit. EvidenceItem.kind Alignment v0.1 is complete through narrow patch and audit. NeedleRuntime Audit Evidence Shape v0.1 is complete through narrow patch and audit. artifact_type Mapping / Runtime Artifact Vocabulary v0.1 Option A docs/spec map is complete through audit as map-only vocabulary documentation with no registry, enum, runtime, schema, or test change. Long-lived DRS TTL Aging Stress v0.1 is complete through proof, audit, docs sync, human walkthrough, and human walkthrough audit. DRS Lineage / Provenance Pressure v0.1 is CLOSED. Compromised Upstream Pack v0.1 is CLOSED. Current gate: STOP PROOF-ONLY EXPANSION GATE before Real Semantic Runtime MVP. DRS Poisoning Resistance v0.1 and Economic Adversary v0.1 are gated / conditional protection layers before Real Semantic Runtime MVP only if they protect or unblock runtime primitives. Option B/C/D/E artifact vocabulary work, Marennya, UP, Negative Trace, and external DRS must not start without review and explicit approval. Public packaging remains later after Real Semantic Runtime MVP. Any future Controlled Multi-LLM Chain Showcase is `showcase_only`, not a canonical authority layer, and must remain Root-final and action-free.

Marennya and UP remain deferred because they should analyze a mature internal system with multi-domain traces, DRS reuse, adversarial memory defense, controlled fractal expansion, dual coupling, DRS bridge evidence, chaos/failure traces, and production-boundary design. They are not early decorative analytics.

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
- LocalDRS is the only implemented DRS runtime in the MVP.
- External DRS remains a future pointer/protocol boundary.
- Global DRS / Internet of Meaning is not implemented.
- DRS records are addressable meaning records with TimeEnvelope, provenance, GT metadata, validation metadata, trace refs, and routing semantics.
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

text NeedleRuntime / adapter → ResultProposal-compatible artifact → Post V&V → real GTValidator runtime report → Root-visible routing semantics → LocalDRS Work / Quarantine / DeadEnds persistence

Needle outcome routing semantics in the current MVP:

- completed accepted outcome -> Work / task_outcome;
- invalid_json -> Quarantine;
- schema_validation_failed -> Quarantine;
- unknown_exception -> Quarantine or failed trace;
- contract_version_mismatch -> DeadEnds / blocked trace;
- circuit_breaker_open -> DeadEnds / blocked trace;
- timeout -> degraded trace, not successful Work;
- permission_required -> needs_user / blocked trace, not completed action.

Safety rules:

- Work != Quarantine.
- Work != DeadEnds.
- degraded trace != successful Work.
- permission_required != completed action.
- blocked != success.
- failed / quarantined / degraded / blocked / deadend records are not direct-reuse eligible.
- only accepted completed Work candidate is direct-reuse eligible in this MVP demo.

Known limitation: `deadends` is currently used broadly for blocked, degraded, and needs_user traces. A future schema may split DeadEnd, BlockedTrace, DegradedTrace, and NeedsUserTrace.

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
24. Root-native DAG/DRS/audit stabilization.
25. Needle outcome Post V&V / real GTValidator / LocalDRS routing.
26. Large Graph / Bounded Fractal Stress.
27. DRS Graph Proximity / Lineage.
28. Chaos Survival Showcase.
29. Compute Collapse via DRS Reuse / Zero Re-Planning Path / Near-Zero LLM Cost Path.
30. DRS Layer Taxonomy v0.1.
31. Typed DRS Lineage Edges v0.1.
32. ReuseScore v0.1 as advisory/ranking only.
33. Semantic Reuse Pipeline Integration v0.1.
34. Root-controlled Semantic Reuse Decision Trace v0.1.
35. Root-controlled Semantic Reuse Gate Trace v0.1.
36. Root-controlled Semantic Reuse Final Decision Trace v0.1.
37. Root-native Semantic Reuse E2E Trace v0.1.
38. Root-native Full Canonical E2E Trace v0.1.
39. Optional Live Gemini Architect Smoke v0.1, opt-in only.
40. Optional Live Gemini Orchestrator Smoke v0.1, opt-in only.
41. Ordered Live Gemini Orchestrator-to-Architect Smoke v0.1, opt-in only.
42. Controlled Orchestrator Matrix Gate v0.1.
43. AVF / Attractor Formation from accepted Matrix v0.1.
44. Architect from bounded AttractorPacket v0.1.
45. DAG / Executor from valid PlanGraph v0.1.

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
