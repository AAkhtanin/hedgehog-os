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

Current checkpoint: Full WOW v1.1 final integrated rollup PASS.

Current final integrated rollup facts:

- Audit log:
  `docs/audit_reports/auditor_full_wow_v1_1_final_integrated_rollup_v01.log`.
- Runner:
  `demo/run_full_wow_v1_1_final_integrated_rollup.py`.
- Focused tests:
  `tests/test_full_wow_v1_1_final_integrated_rollup_runner.py`.
- Audit commit: `a958204`.
- Rollup runner commit: `f22d452`.
- Preflight commit: `2993b46`.
- Rollup type: `deterministic_closed_evidence_observer`.
- This is the closed final integrated WOW v1.1 proof layer.
- Final rollup observes closed evidence only.
- Supplier Payment / Shipment Release Review WOW v1.1 deterministic state
  machine, human walkthrough, Full Semantic E2E spine, BSEP topology repair,
  and real Gemini semantic lane PASS are observed.
- Real Gemini lane is observed, not rerun.
- BSEP was built after Orchestrator validation and validated before Architect.
- Semantic Architect remains semantic proposal provider.
- PlanGraph remains runtime-built, not provider-owned.
- Provider output is not truth, authority, action permission, or FinalOutput.
- Supplier B remains blocked.
- shipment release remains held.
- receipt remains evidence only.
- Root remains final authority.
- Final integrated rollup proof is complete.
- Rollup calls no Gemini/provider/network lane, accesses no secrets, creates
  no ActionCommitPacket, creates no receipt, executes no mock payment, executes
  no real payment, releases no shipment, calls no bank/supplier/warehouse API,
  and preserves `real_world_effects_count: 0`.
- Not production.
- Not public auditor final package.

Next direction should be human-facing pretty walkthrough / evidence pack for
WOW v1.1, then v1.2 planning only. Do not start NeedleFactory, Marennya, UP,
production connectors, or public auditor package.

Closed real-provider run facts:

- Audit log:
  `docs/audit_reports/auditor_full_wow_v1_1_manual_live_gemini_lane_real_run_v01.log`.
- Run id: `full_wow_v1_1_manual_live_gemini_real_20260705_232010`.
- Runtime/audit base commit: `121d22c`; audit commit: `8318be9`.
- Model: `gemini-2.5-flash`.
- Contract mode: `semantic_reasoning_adapter`; schema mode:
  `json_mime_only`.
- Existing Full E2E runner remains the spine.
- No new bridge runner was created.
- Manual live Gemini lane is env-gated.
- Real Gemini Orchestrator was called once and real Gemini Architect was
  called once.
- Orchestrator semantic proposal validation accepted.
- Runtime canonicalization was used.
- BSEP was built after Orchestrator validation and semantic canonicalization.
- BSEP was validated before Architect provider call.
- Architect receives BSEP-derived bounded context.
- The 30-second Architect pre-delay was applied.
- Architect semantic proposal validation accepted.
- `semantic_reasoning_adapter` was used for both live provider roles.
- PlanGraph remains runtime-built, not provider-owned.
- Full WOW live Architect uses the semantic provider wrapper, not the legacy
  PlanGraph provider wrapper.
- Provider output is not truth, authority, action permission, or FinalOutput.
- Gemini creates no ActionCommitPacket, no receipt, no mock payment, no real
  payment, and no shipment release.
- Supplier B remains blocked.
- shipment release remains held.
- receipt remains evidence only.
- Root remains final authority.
- `real_world_effects_count: 0`.
- Secret scan passed: no API key, raw bank secret, raw IBAN, or sandbox token
  was logged.
- Not production.
- Not public auditor final package.

BSEP 004 remains the topology source of truth. Supplier Payment WOW v1.1, Full
E2E WOW alignment, Full E2E live evidence + WOW v1.1 coherence, and the
monkeypatched/no-network BSEP topology repair remain the closed basis.

Closed Full WOW manual live Gemini topology repair facts:

- Audit log:
  `docs/audit_reports/auditor_full_wow_v1_1_manual_live_gemini_bsep_topology_repair_v01.log`.
- Runtime repair commit: `920e5b3`.
- Existing Full E2E runner remains the spine.
- No new bridge runner was created.
- Manual live Gemini lane is env-gated.
- Default deterministic lane remains no Gemini/network/provider.
- BSEP is built after Orchestrator validation and semantic canonicalization.
- BSEP is validated before Architect provider call.
- Architect receives BSEP-derived bounded context.
- Invalid BSEP blocks Architect provider call.
- `_build_manual_live_lane_bsep` does not accept `architect_semantics`.
- Architect prompt/context does not receive raw Orchestrator provider text, raw
  Orchestrator prompt, raw user request text, or raw secret markers.
- Provider output is not truth, authority, action permission, or FinalOutput.
- Manual lane creates no ActionCommitPacket, no receipt, no mock payment, no
  real payment, and no shipment release.
- Root alone creates FinalOutput.
- Root remains final authority.
- No real-world effects.
- Not production.
- Not public auditor final package.

Closed Full E2E live evidence + WOW coherence facts:

- Audit log:
  `docs/audit_reports/auditor_full_semantic_e2e_live_evidence_wow_v1_1_coherence_v01.log`.
- Runtime coherence commit: `b4a3f31`.
- Explicit live/captured evidence mode includes
  `supplier_payment_wow_v1_1_summary`.
- `supplier_payment_wow_v1_1_summary` is PASS in live/captured mode.
- Live evidence + WOW v1.1 coexistence is tested.
- WOW v1.1 summary remains bounded context/evidence.
- SemanticEvidenceClaim remains candidate-only.
- Closed mock ActionCommitPacket and closed receipt are observed only.
- Live evidence creates no ActionCommitPacket, no receipt, and no mock payment.
- Supplier B remains blocked.
- shipment release remains held.
- receipt is evidence only.

Closed Full E2E WOW alignment facts:

- Audit log:
  `docs/audit_reports/auditor_full_semantic_e2e_wow_v1_1_alignment_v01.log`.
- Runtime alignment commit: `160f6c5`.
- Existing Full Semantic E2E runner was patched, not replaced.
- Full Semantic E2E invokes the closed WOW v1.1 summary runner as
  `supplier_payment_wow_v1_1_summary`.
- Closed packet/receipt are observed only, and Full Semantic E2E creates no new
  ActionCommitPacket, receipt, or mock payment.

Closed WOW facts:

- Title: Supplier Payment / Shipment Release Review LIVE-DUAL-ROLE WOW v1.1.
- Short name: HEDGEHOG OS — ZERO-TRUST SUPPLIER PAYMENT WOW v1.1.
- Commit chain: `78fb37d` -> `06f4c55` -> `84d5c6d` -> `06744b2` -> `9ac174b` -> `f7ca348`.
- Audit log: `docs/audit_reports/auditor_supplier_payment_shipment_release_review_wow_v1_1.log`.
- Machine runner:
  `demo/run_supplier_payment_shipment_release_review_wow_v1_1.py`.
- Human walkthrough:
  `demo/run_human_supplier_payment_shipment_release_review_wow_v1_1_walkthrough.py`.
- Deterministic lane PASS.
- Optional live Gemini lane remains manual and was not enabled; it is not a
  core PASS dependency.
- Supplier A scoped mock payment only.
- Supplier B remains blocked.
- shipment release remains held.
- receipt is evidence only.
- No real payment, no real shipment release, no real bank/supplier/warehouse
  API effects, and no real-world effects.
- Root remains final authority.
- Not production.
- Not public auditor final package.

Next direction after this audit/docs sync is the manual real Gemini lane
run/audit, not a new domain demo. Do not start NeedleFactory, Marennya, UP,
production connectors, or public auditor packaging from this checkpoint.

BSEP 004 remains the closed live rich-context basis under this coherence
checkpoint.

Official checkpoint facts:

- run_id: `manual-bounded-semantic-evidence-real-gemini-slice-d-004`
- audit_id: `auditor_bounded_semantic_evidence_real_gemini_slice_d_004_v01`
- runtime base_head: `6a2950a`
- final_status: PASS
- model: `gemini-2.5-flash`
- contract_mode: `semantic_reasoning_adapter`
- schema_mode: `json_mime_only`
- bsep_gate: enabled
- root_decision: `needs_more_evidence`
- validation_errors: []
- live_model_call_count: 2
- network_used_count: 2
- gemini_called_count: 2
- bounded_semantic_evidence_packet_created_count: 1
- bounded_semantic_evidence_packet_validated_count: 1
- action_permission_created_count: 0
- action_commit_packet_created_count: 0
- connector_called_count: 0
- real_world_effects_count: 0

Prior live-provider checkpoint facts:

- run_id: `manual-live-unknown-request-real-gemini-007`
- audit_id: `auditor_live_unknown_request_real_gemini_007_v01`
- run base_head: `fa8877d`
- audit commit/head context: `d2a0968`
- final_status: PASS
- model: `gemini-2.5-flash`
- contract_mode: `semantic_reasoning_adapter`
- schema_mode: `json_mime_only`

Current hedgehog core baseline:

- `hedgehog.context_packets` contains bounded ContextPacket contracts.
  BoundedSemanticEvidencePacket now lives here as a bounded ContextPacket
  family; it is not a new core module and does not change the six-module
  core baseline count.
- `hedgehog.structured_rationale` contains canonical structured rationale
  contracts, builders, and validators.
- `hedgehog.semantic_reasoning_adapter` contains stable semantic reasoning
  provider contracts, required field constants, reasoning field normalization
  and validation, conversion from provider semantic reasoning into canonical
  structured rationales, safe local advisory PlanGraph node builders, provider
  claim boolean preservation for downstream validators, and no
  Gemini/provider/network/runtime imports.
- `hedgehog.action_commit_packet` contains the Root-created/mock-only
  ActionCommitPacket contract.
- `hedgehog.mock_connector_sandbox` contains the fake-adapter/local-only
  sandbox contract.
- `hedgehog.fractal_fulfillment` contains the child branch / fulfillment
  topology contract.

Rich Context / Structured Rationale core checkpoint:

- `hedgehog.context_packets`
- `tests/test_context_packets_core.py`
- `hedgehog.structured_rationale`
- `tests/test_structured_rationale_core.py`
- ContextPacket is not truth.
- ContextPacket is not authority.
- structured rationale is explanation only.
- Root remains final authority.

Core Extraction Action + Mock + Fractal checkpoint remains closed:

- Audit: `auditor_core_extraction_action_mock_fractal_v01`
- `c62ab84` Extract ActionCommitPacket core contract
- `be4f40d` Extract Mock Connector Sandbox core contract
- `e26c05a` Extract Fractal Fulfillment topology core contract
- `4723830` Harden Mock Connector Sandbox adapter registry
- Regression suite: 272 passed, 2 warnings
- deterministic extracted-core smoke PASS
- dual Gemini extracted-core smoke PASS

Current integration/live spine:

- `demo/run_full_semantic_e2e_v01.py` remains an integration harness /
  integration spine.
- `demo/run_live_unknown_request_dual_rich_context_v01.py` is the current live
  unknown-request provider spine.
- These demo runners are not the same as `hedgehog` core modules.
- `semantic_reasoning_adapter` status is now
  `approved_live_provider_architecture`, `core_extracted`,
  `runner_delegated`, and `slice_c_audited`.
- `demo/run_live_unknown_request_dual_rich_context_v01.py` delegates semantic
  adapter mechanics to `hedgehog.semantic_reasoning_adapter`.
- The live runner still owns Gemini/provider/env/prompt/timeout/pre-delay/
  orchestration behavior, the 007 integration policy, and prompt policy.
- Core does not own Gemini or network.

This is the first successful real live unknown-request run through real Gemini
Orchestrator and real Gemini Architect. It was not injected provider, not
monkeypatched provider, and not a prepared domain fixture. Raw unknown request
reached the real live provider spine, Root boundary was created, and Root
decision was `needs_more_evidence`.

Approved live-provider architecture:

```text
Provider proposes semantics.
Runtime canonicalizes.
Validators verify.
Root decides.
```

`semantic_reasoning_adapter` is now the approved live-provider architecture and
is core-extracted. External provider output is an untrusted semantic reasoning
proposal; the provider does not emit internal canonical `structured_rationale`
objects. `hedgehog.semantic_reasoning_adapter` canonicalizes provider semantic
reasoning into `structured_orchestrator_rationale`,
`structured_architect_rationale`, and safe local PlanGraph nodes.
`hedgehog.structured_rationale` validates canonical rationale,
`hedgehog.context_packets` validates bounded packets, the live runner
orchestrates provider/env/prompt behavior, and Root remains final authority.

Semantic Reasoning Adapter core extraction status:

- Core module: `hedgehog.semantic_reasoning_adapter`.
- Direct tests: `tests/test_semantic_reasoning_adapter_core.py`.
- Runner delegation commit: `12f7e96`.
- Slice C audit: `auditor_semantic_reasoning_adapter_delegation_slice_c_v01`.
- Slice C smoke: `manual-semantic-reasoning-adapter-delegation-slice-c-001`.
- Slice C replay smoke PASS was monkeypatched and network-free:
  `no_real_gemini_or_network: true`.
- 007-compatible safe local nodes remain `node:unknown_request_semantic_review`
  and `node:root_review_gate`.
- Compact and full compatibility paths remain preserved:
  `compact_rationale_adapter` and `full_structured_rationale`.

Validated 007 artifacts: OrchestratorRouteContextPacket accepted,
ArchitectPlanContextPacket accepted, structured_orchestrator_rationale
accepted, structured_architect_rationale accepted, PlanGraph is not authority,
ResultProposal is not FinalOutput, validation_errors: [], and
`real_world_effects_count: 0`.

Authority boundaries: provider output is not truth, provider output is not
authority, ContextPacket is not truth, ContextPacket is not authority,
structured rationale is explanation only, DRS is not truth, AVF/route/vector
selection is not authority, Gemini does not create ActionCommitPacket, Gemini
does not create FinalOutput, and Root remains final authority.

Prior real-live attempts 001-006 are superseded diagnostics, not the current
architecture. Do not delete proof history and do not claim failed attempts
never happened. The full provider-canonical structured rationale contract was
too heavy; the compact object-array rationale contract was still weak or
timeout-prone; `semantic_reasoning_adapter` + `json_mime_only` resolved the
live happy path.

BoundedSemanticEvidencePacket 004 status:

- Real Gemini Orchestrator called once.
- Real Gemini Architect called once.
- BoundedSemanticEvidencePacket validation accepted.
- OrchestratorRouteContextPacket accepted.
- ArchitectPlanContextPacket accepted.
- structured_orchestrator_rationale accepted.
- structured_architect_rationale accepted.
- PlanGraph is not authority.
- ResultProposal is not FinalOutput.
- Root remains final authority.
- Architect context contained BSEP and did not contain the raw request or raw
  provider dump text.
- This proves a real-live architecture happy path, not full stability or
  adversarial completeness.
- Architect explicit HTTP timeout was disabled in the manual replay; keep the
  timeout taxonomy as a separate reliability debt and do not change runtime
  unless explicitly asked.

Provider Contract Modes — future-compatible operator rules:

- Hedgehog OS separates provider formatting from authority.
- Current default is `semantic_json_mode`.
- `provider_schema_lite_mode` is a future optional ergonomics/reliability
  helper only.
- `provider_canonical_schema_mode` is not the current preferred route and may
  only be revisited as a gated experiment.
- Provider proposes semantics.
- Runtime canonicalizes.
- Validators verify.
- Root decides.
- Provider-side schema is not authority.
- JSON MIME is not authority.
- SDK schema is not authority.
- Root remains final authority.
- This does not mean SDK schema mode is implemented now.
- This does not mean Hedgehog OS returned to provider-owned canonical objects.
- This does not mean provider-side schema replaces local validation.
- This does not mean LangChain/provider framework controls Hedgehog authority.
- This does not change the current BSEP / WOW route.

Current next approved engineering direction:

- Reviewed preflight for the next runtime step after Full Semantic E2E WOW
  v1.1 alignment.
- Audit-approved optional live lane only if explicitly requested.

Do not start new domain demos, NeedleFactory, Marennya, or UP from this
checkpoint. Keep production and public-auditor non-claims.

Future agents must not jump directly to NeedleFactory, Marennya, UP,
production connectors, real payment/shipment, unbounded Gemini context payloads,
unbounded PlanGraph context payloads, or public launch claims. This checkpoint
is not production autonomy: no real external actions, no connector calls, and
no production persistence.

Long-lived DRS TTL Aging Stress v0.1 is complete through proof, audit, docs
sync, human walkthrough, and human walkthrough audit. The human walkthrough
audit status is PASS_WITH_SCOPE_WARNING because the then-current full-suite
drift was outside the walkthrough scope.

Full Suite Drift Repair Phase 1 is complete through repair and audit. The
Fractal DAG ResultProposal producer was aligned with the current schema by
removing schema-invalid top-level `node_id` while preserving node identity in
valid payload/evidence/trace fields. Full suite recovered to 1692 passed,
60 warnings, 0 failed.

DRS Lineage / Provenance Pressure v0.1 is complete through proof, technical
audit, human walkthrough, and human walkthrough audit. It proves lineage
informs, lineage does not decide, provenance does not become truth,
audit/hash-chain proves continuity, not truth, accepted evidence ancestry is
not future action permission, bridge traversal is not authority transfer,
quarantine/deadend proximity is bounded, ConflictCheck remains advisory, GT
remains advisory, and Root remains final authority. Proof counters include
`scenarios_total: 10`, `scenarios_passed: 10`,
`direct_reuse_allowed_count: 0`, `root_review_required_count: 10`,
`root_final_authority_preserved_count: 10`, `lineage_decides_count: 0`,
`provenance_truth_claimed_count: 0`, and
`audit_hash_truth_claimed_count: 0`. Human walkthrough evidence records
`underlying_proof_status: PASS`, `walkthrough_required_counters_match: True`,
and `7 passed`.

Compromised Upstream Pack v0.1 is closed through human walkthrough audit.

Hardening-plan: APPROVED.
Full path to living Hedgehog OS: PATCHED.

The correct path is proof hardening -> enforcement hardening -> gated
DRS/adversary protection where needed -> real semantic runtime -> real WOW /
public packet / whitepaper. The path is not proof hardening -> another pretty
proof/public packet -> whitepaper.

DRS Lineage / Provenance Pressure v0.1 remains CLOSED between Long-lived DRS
State / Aging / TTL Stress v0.1 and Compromised Upstream Pack v0.1.

The old combined Compromised Upstream / Economic Adversary Pack wording is
split into Compromised Upstream Pack v0.1 — CLOSED, DRS Poisoning Resistance
v0.1 — gated / conditional before Real Semantic Runtime MVP, and Economic
Adversary v0.1 — gated / conditional before Real Semantic Runtime MVP. DRS
Poisoning Resistance and Economic Adversary are not optional decoration. They
are gated protection layers and should be implemented only if they protect or
unblock Real Semantic Runtime MVP, or folded into Real Local DRS Resolver /
Writeback acceptance criteria.

STOP PROOF-ONLY EXPANSION GATE: after Kernel Hardening, no new proof-only
expansion is allowed unless it directly protects or unblocks runtime
primitives: DRS, AVF, GT / LGT, bounded LLM / SLM actors, fractal cells, or the
Root-reviewed semantic reuse loop.

The old WOW Demo / Public Auditor Packet / Whitepaper position is reframed as
Kernel Hardening Auditor Packet. This packet may happen after
enforcement/boundary as an engineering hardening packet, but it is not the real
living-system WOW demo.

BLOCK — Real Semantic Runtime MVP:

- Real Local DRS Resolver / Writeback v0.1
- CandidateVectorGenerator + real AVF scoring v0.1
- GT / LGT advisory evaluator v0.1
- bounded LLM / SLM actors: Intake / Orchestrator / Architect / Executor
- Fractal Cell Runtime v0.1
- DRS reuse cycle: write meaning -> resolve meaning -> reuse under Root review
- End-to-end local semantic runtime demo

Real public packaging moves after Real Semantic Runtime MVP: Real Semantic
Runtime WOW Demo, Public Auditor Packet, and Whitepaper engineering draft.

Kernel Enforcement Integration v0.2 and Production Boundary Design v0.2 /
Security Kernel Spec remain on the roadmap. Developer Facade v0.2 / Manifest
Suggestion Candidates are gated: keep only if they directly support DRS / AVF /
GT-LGT / bounded LLM actors / fractal cells. Otherwise move them to gated
backlog.

No deletion. No premature public packaging. No endless proof-only expansion.
Runtime primitives before real WOW.

For future large runtime/schema/contract/hardening changes, full pytest is
required before closing the layer. Do not claim production readiness. Do not
start unrelated layers before explicit review. Preserve drift-repair
discipline: no skips/xfails, no forced success, no forced accept, and no schema
relaxation.

Do not start runtime/schema production DRS, external/global DRS, Marennya / UP
/ Negative Trace, or artifact_type vocabulary work from this checkpoint. Do
not treat TTL, GT-TTL, DRS, audit, source ingestion, ReuseBoost,
AcceptedEvidence, lineage, provenance, bridge traversal, audit hash,
ConflictCheck, GT, or popularity as authority. Future V2 / Negative Trace /
Marennya / UP remain deferred and are not current. Public packaging remains
behind Real Semantic Runtime MVP.

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
- NeedleCandidate lifecycle may create proof-level candidate objects, but any installed needle, production persistence, external action, or Root bypass remains forbidden.
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
61. NeedleCandidate lifecycle / NeedleForge prototype v0.1 may create bounded proof-level NeedleCandidate objects only. NeedleCandidate is not an installed Needle; GT cannot install needles; Root alone disposes candidates as pending review, rejected, or quarantined; production persistence, global DRS writes, external actions, and Root bypass remain forbidden.
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

Semantic Reuse Pipeline Integration v0.1 is the next completed engineering integration proof. It connects LocalDRS retrieval → taxonomy-aware filtering → typed edge interpretation → graph proximity → ReuseScore → ReuseGate / Root boundary → direct reuse candidate or full pipeline fallback. It structurally consumes `collect_reuse_score()`, preserves the source Typed DRS Lineage Edges report, evaluates scenario rows, and separates recommendations from authority. It is not production RootOrchestrator integration, production autonomy, global DRS, external DRS, a ReuseGate replacement, a Root bypass, direct reuse execution, FinalOutput creation, real external action, live Gemini, or Telegram action.

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

Root-native sandbox NeedleRuntime E2E v0.1 is complete. It sources a validated PlanGraph node from the existing Architect proof and demonstrates Root-approved bounded sandbox/mock capability execution through NeedleExecutionResult → ResultProposal → Post V&V → GTDecision → Root FinalArtifact. NeedleRuntime is not authority; needle outcome is evidence, not final truth; degraded/blocked/failed outcomes remain visible; raw output and malicious FinalOutput, DRS write, Root bypass, and external-action claims are rejected. Proof status: PASS, scenarios_verified=11, completed/degraded/blocked_or_failed=1/1/4, malicious_claims_rejected=4, focused tests passed=70, full suite passed=1057, sensitive scan clear. Evidence: `docs/audit_reports/auditor_root_native_sandbox_needleruntime_e2e.log`.

Fractal Cell Runtime v0.1 is complete. It proves the third execution route inside a parent PlanGraph: atomic node → ordinary Executor; needle-bound node → sandbox NeedleRuntime; non-atomic node with `child_cell_required=true` → bounded child fractal cell. This is not a long chain. The deterministic child mini-cell may run child Orchestrator / Architect / Executor roles, returns ChildBoundarySnapshot upward, and is adapted into a ResultProposal-compatible artifact visible to Post V&V, GT, and Root Final. Completed, degraded, blocked, and failed child states remain visible.

Child-cell boundaries: child cell and child Orchestrator are not Root; child output is boundary evidence, not final truth; no child FinalOutput, parent DRS write, real external action, or live child LLM/SLM is allowed. Recursion and execution remain bounded by depth and budget, and parent DRS promotion requires Root. ChildBoundarySnapshot is addressable experience, not an installed needle; successful traces do not automatically create needles. Proof status: PASS, scenarios_verified=12, completed/degraded/blocked_or_failed=1/1/2, malicious_child_claims_rejected=5, focused tests passed=56, full suite passed=1069, sensitive scan clear. Evidence: `docs/audit_reports/auditor_fractal_cell_runtime.log`.

Live Child Executor in Fractal Cell v0.1 is complete. It is an opt-in live Gemini proof inside one bounded child cell, not a long chain. Gemini substitutes only child Executor, receives one Architect-provided bounded node contract rather than a free instruction, and returns ChildExecutionResult JSON/evidence only. It is not child Orchestrator, child Architect, Root, FinalOutput, DRS writeback, a needle, a protocol template, or production action execution.

Verified live behavior: the proof-only task completed and reached accepted Root Final; the action-like request was detected, blocked, and preserved through ChildBoundarySnapshot, parent adapter, Post V&V, GT, and rejected Root Final with no hidden success. Live status=PASS, live opt-in/network used, child Executor only, no fallback, malicious_claims_rejected=6, no child FinalOutput, parent DRS write, API/tool call, real action, Root bypass, or Post V&V / GT / Root bypass. Deterministic safe-fallback proof and live PASS evidence: `docs/audit_reports/auditor_live_child_executor_in_fractal_cell_deterministic.log` and `docs/audit_reports/auditor_live_child_executor_in_fractal_cell_LIVE.log`. Focused deterministic tests passed=36, full suite passed=1082, sensitive scan clear.

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
