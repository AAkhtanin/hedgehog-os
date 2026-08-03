<!-- SPDX-License-Identifier: AGPL-3.0-only -->

# Hedgehog OS — Quantum-Inspired Mathematical Extension Roadmap v2.0

## Future post-Gate-6 advisory profile with a classical-first substrate and optional physical-QPU backends

```text
document_id: hedgehog_quantum_mathematical_extension_roadmap_v2_0
document_status: FUTURE_POST_GATE6_ENGINEERING_DESIGN
document_language: en
source_draft_status: RETIRED_PRIVATE_DRAFT_NOT_FOR_REPOSITORY_USE
intended_first_repository_version: v2.0
repository_target_path: specs/future/quantum/hedgehog_quantum_mathematical_extension_roadmap_v2_0.md
earliest_private_design_commit_point: AFTER_G2C_CLOSED_PASS
public_disclosure_gate: AFTER_GATE6_CLOSED_PASS_AND_R_IP1_RELEASE_APPROVAL
implementation_baseline_required: HEDGEHOG_GATE6_CLOSED_PASS_AND_TAGGED
current_release_claim: false
normative_for_current_gate_1_to_gate_6_runtime: false
private_commit_is_publication: false
public_prior_art_created_by_private_commit: false
changes_current_six_gate_strategy: NO
changes_root_law: NO
changes_bsep_law: NO
changes_hardmask_law: NO
changes_transition_registry_law: NO
changes_corridor_law: NO
changes_action_packet_law: NO
changes_receipt_law: NO
changes_replay_law: NO
default_execution_substrate: CLASSICAL_COMPUTER
physical_qpu_required_for_initial_profile: NO
quantum_advantage_claimed: NO
physical_quantum_state_claimed_for_classical_simulator: NO
quantum_brain_or_consciousness_claimed: NO
primary_claim: QUANTUM_INSPIRED_ADVISORY_MATHEMATICAL_PROFILE
license: AGPL-3.0-only
```

---

# 0. Repository integration, visibility, and publication decision

This roadmap has two different lifecycle events that must never be conflated.

## 0.1. Private design commit after G2-C

After G2-C reaches `CLOSED_PASS`, its independent audit is accepted, its checkpoint is committed, and the repository is clean and synchronized, this roadmap may be committed in one separate documentation-only commit before G2-D begins.

That commit is a private architecture/provenance event. It is not a public release, not a current capability claim, not prior art visible to the public, and not authorization to start quantum-profile implementation.

The correct repository location is:

```text
specs/future/quantum/hedgehog_quantum_mathematical_extension_roadmap_v2_0.md
```

This location intentionally combines two properties:

1. it is under `specs/`, so the future profile is indexed as serious architecture rather than informal speculation;
2. it is under `future/quantum/`, so no reviewer, LLM, test, manifest consumer, release tool, or auditor may misread it as an implemented current-release capability.

The full roadmap must not be copied into the current Human Passport or current Math Appendix. Those surfaces receive only the small constitutional references defined in Section 19.

The private design commit must not change:

- runtime code;
- schemas;
- tests;
- demos;
- current gate status;
- current conformance results;
- current claim-to-evidence mappings;
- the Gate-2 execution order;
- the current G2-D start point.

The exact current versioned filenames for the Human Passport, Math Appendix, Machine Manifest, limitations, and release notes must be discovered from the repository at execution time. Historical filenames in this roadmap are examples of document roles, not permission to edit stale files.

Recommended private commit message:

```text
Add future quantum-inspired mathematical roadmap v2.0
```

Expected logical change surface:

```text
A specs/future/quantum/hedgehog_quantum_mathematical_extension_roadmap_v2_0.md
M README.md                                      # short future-profile pointer only
M <current Human Passport>                       # one invariant only
M <current Math Appendix>                        # one non-normative pointer only
M <current Machine Manifest>                     # future-design object only
M <current limitations surface>                  # explicit not-implemented statement
M <current development release-notes surface>    # private design record, not “published”
```

No `AGENTS.md` expansion, implementation preflight, quantum schema, quantum test, or quantum source package is authorized by this integration unless the current repository's release-spine law requires one minimal status pointer. The active engineering focus must return immediately to G2-D.

## 0.2. Public disclosure after Gate 6 and R-IP1

The roadmap must not become publicly accessible before:

```text
Gate 6 = CLOSED_PASS
and
R-IP1 public-release boundary = PASS
and
owner explicitly authorizes first public release
```

Only that public release creates a public technical record and defensive-publication surface.

Public disclosure and implementation are separate decisions. Implementation may begin only from an immutable, tagged Gate-6 baseline under an owner-approved Q0/Q1 workstream. A public release is not a mathematical prerequisite for local implementation, but the current project plan keeps all implementation post-Gate-6.

## 0.3. Current claim boundary

The current claim-to-evidence index may contain only a clearly separated future-design pointer with fields equivalent to:

```text
implemented: false
evidence_status: NOT_APPLICABLE_UNTIL_IMPLEMENTED
current_release_claim: false
physical_qpu_required: false
quantum_advantage_claimed: false
```

No current release surface may claim that a quantum-state ABI, Quantum AVF, Quantum GT, Quantum DRS, quantum Fractal allocator, simulator backend, physical-QPU adapter, or quantum advantage exists.

# 1. Executive conclusion

After the existing Gate 1–6 programme is closed, Hedgehog OS will contain the constitutional seams required to host richer advisory mathematics without changing its authority architecture:

- Gate 1 provides the domain-neutral ABI, Root, Transition Registry, Effect Firewall, MultiRoot, evidence integrity, Replay, and conformance spine.
- Gate 2 provides time, lifecycle, DRS, controlled reuse, ExecutionModeRouter, Fractal Runtime, and Delta Runtime.
- Gate 3 provides OutcomeFeedbackEnvelope and cross-domain calibration.
- Gate 4 provides the frozen classical mathematical contracts for AVF, GT, Pareto, individual rationality, bargaining, regret, and feedback.
- Gate 5 provides extension and federation surfaces.
- Gate 6 provides final conformance, adversarial closure, model-swap invariance, Replay compatibility, and the public release spine.

The quantum-inspired profile does not replace Hedgehog OS. It is a replaceable advisory mathematical organ inside the existing Root-controlled runtime.

The governing law is:

> Quantum-inspired mathematics may change how the system represents possibility, context, correlation, strategy geometry, branch pressure, advisory memory, and compute allocation. It may not create authority, permission, an ActionCommitPacket, a Corridor, a Receipt, a Root decision, or a consequential effect.

The first implementation programme contains one freeze step and four post-Gate-6 engineering gates:

0. Q0 — Gate-6 baseline freeze and quantum-profile preflight.
1. Q1 — Quantum-Inspired State and Context ABI.
2. Q2 — Quantum-Inspired AVF and BSEP Contextual Dynamics.
3. Q3 — Quantum-Inspired MultiRoot Game and Strategy Geometry.
4. Q4 — Open-System DRS, Quantum-Walk Fractal Search, Backend Conformance, and Release.

The classical profile remains mandatory and complete. The quantum-inspired profile may remain a classical-simulator profile indefinitely. A physical QPU is optional and never required to preserve Hedgehog conformance.

Planning estimates, to be recalibrated during Q0:

- classical-simulator profile: approximately 35–58 focused engineering days;
- optional experimental physical-QPU backend: an additional 10–30 focused engineering days;
- physical QPU required for the initial profile: no;
- quantum advantage claimed by this roadmap: no.

These are planning estimates, not release commitments and not permission to delay the classical six-gate programme.

# 2. Architectural resonance — possibility before authority

This section is a non-normative conceptual bridge. It explains why a quantum-inspired mathematical profile is native to Hedgehog OS rather than an ornamental feature added after the fact.

It does **not** claim that the current runtime is a physical quantum system, that DRS is a quantum field, that Root performs physical measurement, that a classical simulator contains physical superposition, or that Hedgehog implements a quantum computer.

## 2.1. Core thesis

Hedgehog OS was designed to preserve a space of possibilities before it creates authority.

Before Root, the runtime may hold:

- several hypotheses;
- competing semantic interpretations;
- time-scoped and provenance-bound DRS records;
- conflicting evidence;
- alternative strategies;
- multiple feasible execution modes;
- uncertainty, risk, and incomplete knowledge;
- candidate rankings and contextual interactions;
- bounded branches that have not yet been selected.

None of these objects is yet a decision, permission, authorization, packet, Corridor, effect, Receipt, or FinalOutput.

The concise architectural formula is:

> **Probabilistic intelligence. Deterministic authority.**

And more precisely:

> **Possibility may remain probabilistic. Authority must become explicit.**

> **Uncertainty may shape advice. It may never own the action.**

## 2.2. DRS as a field of addressable candidates, not a physical quantum field

DRS does not store one timeless absolute truth. It may surface several records whose meanings differ by:

- provenance;
- observation time;
- knowledge time;
- context time;
- validity interval;
- freshness;
- conflict status;
- supersession;
- quarantine or dead-end state;
- reuse eligibility;
- confidence and evidence quality.

This gives the runtime a structured field of possible influences rather than one unquestioned answer.

The resemblance to probabilistic or contextual state models is architectural. DRS itself remains a typed semantic address, lineage, time, conflict, trust, and reuse fabric. It is not reclassified as a physical wavefunction, quantum memory, or source of authority.

## 2.3. Pre-Root coexistence is not literal physical superposition

Routers, AVF, GT, DRS retrieval, semantic models, tensor methods, classical optimization, and future quantum-inspired profiles may preserve and compare several possibilities at once.

That coexistence may be represented by:

- deterministic candidate sets;
- scalar scores;
- probability distributions;
- contextual matrices;
- tensor factorizations;
- density-state mathematics;
- samples from a simulator or physical QPU.

The word `superposition` may be used only as a clearly marked explanatory analogy unless a physical QPU state is actually prepared and evidenced. The current Hedgehog runtime makes no physical-superposition claim.

The normative invariant is simpler and stronger:

```text
coexisting advisory possibilities
!=
committed authority
```

## 2.4. Root as classical sovereignty and commit boundary

Root is not a literal quantum observer and does not physically collapse a wavefunction.

Root is the local classical sovereignty and commit boundary.

It receives an explainable classical projection of the advisory state and may:

- reject;
- narrow;
- defer;
- request more evidence;
- select no-deal;
- accept within an explicit scope.

Only an accepted Root decision may create a bounded ActionCommitPacket. Only the unchanged Effect Firewall and Corridor may carry a permitted consequential effect into the world.

The canonical transition remains:

```text
advisory possibility space
→ explainable classical projection
→ Root reject / narrow / defer / accept
→ optional bounded ActionCommitPacket
→ Effect Firewall
→ Corridor
→ evidence
→ Replay without recreated authority
```

The quantum profile may enrich the left side of this boundary. It may not blur, bypass, or own the boundary itself.

## 2.5. Deterministic Faraday-cage framing

For human explanation, Hedgehog OS may be described as:

> **A deterministic Faraday cage around probabilistic intelligence: uncertainty may fill the advisory space, but it cannot leak into authority.**

This is an architectural metaphor, not a claim of electromagnetic isolation, perfect security, or physical quantum containment.

Its exact technical meaning is:

- uncertain compute may produce proposals;
- proposals cannot self-promote into authority;
- memory cannot self-promote into permission;
- ranking cannot self-promote into authorization;
- a backend result cannot self-promote into an effect handle;
- every consequential transition remains Root-bound and Corridor-enforced.

The deeper project law is:

> **Hedgehog does not make intelligence deterministic. It makes the ownership of action deterministic.**

## 2.6. Why the future quantum profile is native to Hedgehog

The quantum profile is natural because Hedgehog already separates:

```text
possibility
from decision;

decision
from authorization;

authorization
from execution;

execution
from evidence;

evidence
from future permission.
```

A richer mathematical substrate may therefore change how possibilities are represented, correlated, explored, aged, or allocated without changing who may decide or who may touch the world.

This is the long-term value of Computational Substrate Neutrality:

```text
advisory organ may evolve;
authority constitution remains invariant.
```


# 3. Constitutional boundary

## 3.1. Layers that remain strictly classical

The following layers must not become quantum, probabilistic, stochastic-backend-dependent, or numerically approximate in their authority semantics:

- RootDecision;
- Root ownership and Root identity;
- Transition Registry;
- HardMask as a legal, policy, safety, or constitutional exclusion;
- ActionCommitPacket;
- packet lifecycle, expiry, revocation, supersession, invalidation, and kill-switch;
- Effect Firewall;
- Corridor scope enforcement;
- idempotency and terminal-state semantics;
- EvidenceReceipt;
- Package, Anchor, and Replay;
- cryptographic verification;
- final conformance PASS or FAIL;
- exact TimeEnvelope coordinates and temporal hard gates.

These layers determine what is valid, executable, owned, committed, and evidentially preserved. They remain typed, deterministic, inspectable, and replayable.

## 3.2. Layers in which quantum-inspired mathematics is permitted

The profile may exist only in the advisory and candidate plane:

- representation of validated CandidateVectors and StrategyCandidates;
- BSEP-scoped contextual observation;
- AVF ranking and branch-budget pressure;
- correlated MultiRoot strategy analysis;
- advisory Pareto, bargaining, regret, and deviation surfaces;
- DRS history priors and contextual advisory state;
- controlled aging of advisory memory;
- compute-mode and branch-selection proposals;
- bounded Fractal graph exploration;
- replaceable classical simulator, tensor backend, shot-based simulator, or optional physical-QPU backend.

The profile receives only material already admitted by the classical Hedgehog boundary. It cannot ingest raw provider text, hidden fields, secrets, forbidden candidates, revoked authority, or unvalidated graph structure as mathematical freedom.

## 3.3. Classical commit boundary

The canonical post-extension path is:

1. existing Hedgehog contracts and hard gates produce a validated feasible candidate set;
2. the quantum-inspired profile constructs an advisory mathematical state;
3. the profile returns a classical, explainable projection;
4. Post V&V validates shape, provenance, numerical stability, declared limits, and classical-limit evidence;
5. AVF and GT advisory reports are presented to the relevant local Root;
6. each Root independently accepts, rejects, requests evidence, or selects no-deal;
7. only Root may create an ActionCommitPacket;
8. only Corridor may carry a bounded consequential effect.

No amplitude, probability, density matrix, Hamiltonian, channel, measurement, sample, optimizer output, or QPU result becomes authority.

## 3.4. Physicality and terminology boundary

A density matrix, Hamiltonian, channel, tensor product, interference term, or quantum walk executed on a classical computer is a quantum-inspired mathematical representation. It is not evidence that Hedgehog is a physical quantum system.

This roadmap does not claim:

- that cognition or consciousness is physically quantum;
- that DRS is a quantum memory device;
- that a classical simulator creates physical entanglement;
- that non-separable advisory mathematics proves physical entanglement;
- that quantum terminology by itself provides computational advantage;
- that replacing an advisory solver changes the Hedgehog authority constitution.

# 4. Relationship to the existing six gates

| Existing layer | Existing capability | Quantum extension | Existing law changed? |
|---|---|---|---|
| Gate 1 / ABI | typed artifacts, Root, MultiRoot, conformance | new advisory artifact families and adapters | no |
| Gate 2 / DRS, Mode, Fractal, Delta | time, reuse, lifecycle, selective compute | contextual state, quantum branch pressure, open-system advisory update | no |
| Gate 3 / Feedback | OutcomeFeedbackEnvelope and comparable metrics | calibration of Hamiltonian and channel parameters | no |
| Gate 4 / AVF and GT | candidate set, utility envelopes, Pareto, bargaining, regret, AVF pressure | density state, contextual coupling, correlated strategy geometry | classical profile preserved |
| Gate 5 / Extensions | Needles, External DRS, federation boundaries | optional QuantumMathProfile package or backend Needle | no |
| Gate 6 / Conformance | replay, model swap, adversarial closure | backend swap, classical-limit tests, authority-invariance tests | no |

The quantum profile is a mathematical profile, not a new authority layer.

---

# 5. Computational substrate neutrality invariant

The following invariant should be referenced from the Human Passport and the current Math Appendix:

> Replacing advisory ranking, strategy evaluation, memory-state modelling, branch allocation, or candidate-space search with classical probabilistic, tensor, quantum-inspired, or physical-QPU methods does not alter the Hedgehog authority architecture, provided that Root sovereignty, BSEP-scoped observation, HardMask exclusion, Root-created ActionCommitPacket, Corridor exclusivity, Receipt non-authority, temporal hard gates, and Replay non-execution remain invariant.

For Hedgehog conformance, renaming, splitting, merging, relocating, or changing the mathematical substrate of an advisory component does not create a new authority architecture.

This is a technical conformance statement. It does not modify AGPLv3, does not create a patent right, and does not claim that an independently implemented system is automatically a copyright derivative work.

---

# 6. Common mathematical vocabulary

## 6.1. Feasible candidate space

Classical hard gates execute before the quantum-inspired profile.

Let the validated source candidate set be:

\[
C = \{c_1,c_2,\ldots,c_n\}.
\]

Let the HardMask indicator be \(h_i\in\{0,1\}\), and define the feasible set:

\[
C_F = \{c_i\in C : h_i=1\}.
\]

The preferred implementation constructs the advisory basis directly from \(C_F\). A compatibility or audit profile may retain the full candidate basis only when it also carries the exact HardMask projector and proves zero support outside \(C_F\).

Define the finite-dimensional complex vector space:

\[
\mathcal{H}_F = \operatorname{span}\{|c_i\rangle : c_i\in C_F\}.
\]

The basis order is canonical and bound to the digest of the exact validated source candidate set, HardMask result, policy version, BSEP reference, and canonicalization profile.

## 6.2. Profile classes

The roadmap distinguishes four mathematical classes:

1. `DIAGONAL_CLASSICAL_EMBEDDING` — an exact density-matrix representation of a frozen classical probability distribution;
2. `REAL_HERMITIAN_CONTEXTUAL` — a real symmetric/Hermitian contextual model with lineage-bound couplings;
3. `COMPLEX_HERMITIAN_EXPERIMENTAL` — an advanced complex Hermitian model, enabled only after the previous classes close;
4. `PHYSICAL_QPU_EXPERIMENTAL` — an optional backend experiment with separate evidence and no authority change.

Each artifact and report must declare its class. A report from one class must not silently claim the stronger meaning of another class.

## 6.3. Advisory state

A quantum-inspired advisory state is represented by a density operator:

\[
\rho \succeq 0,
\qquad
\operatorname{Tr}(\rho)=1.
\]

For every admitted state:

\[
P_F\rho P_F=\rho,
\]

where \(P_F\) is the HardMask feasibility projector when the full compatibility basis is used.

The state is an advisory representation only. It is not evidence, permission, truth, a Root decision, or an effect handle.

## 6.4. Exact classical embedding

Let the frozen classical Gate-4 profile produce a versioned normalized distribution:

\[
p^{\mathrm{cl}}
=
\mathcal{N}_{\mathrm{AVF},v}(a, C_F),
\qquad
p_i^{\mathrm{cl}}\ge0,
\qquad
\sum_i p_i^{\mathrm{cl}}=1.
\]

Its exact diagonal embedding is:

\[
\rho_{\mathrm{cl}}
=
\sum_{c_i\in C_F}
p_i^{\mathrm{cl}}
|c_i\rangle\langle c_i|.
\]

This is the primary backward-compatibility law.

The quantum-inspired implementation must reproduce the exact Gate-4 normalization profile that actually closes. It must not assume in advance that the classical AVF uses softmax, Gibbs normalization, or any other normalization that Gate 4 has not frozen.

## 6.5. HardMask projector and support preservation

On a full compatibility basis, define:

\[
P_F = \sum_i h_i|c_i\rangle\langle c_i|.
\]

The admissible projected state is:

\[
\rho_F
=
\frac{P_F\rho P_F}
{\operatorname{Tr}(P_F\rho P_F)}
\]

when the denominator is positive.

If:

\[
\operatorname{Tr}(P_F\rho P_F)=0,
\]

then the profile returns `NO_FEASIBLE_MASS` to Root. It must not renormalize over forbidden space, invent a candidate, widen HardMask, or create fallback permission.

Every promoted state and every promoted update must satisfy:

\[
P_F\rho P_F=\rho.
\]

Forbidden support is not merely assigned a low probability. It is absent from the advisory state.

## 6.6. Observables

Each advisory quantity is represented by a Hermitian observable:

\[
O=O^\dagger.
\]

Its expected value is:

\[
\mathbb{E}_{\rho}[O]
=
\operatorname{Tr}(\rho O).
\]

Candidate utility, risk, cost, uncertainty, review burden, evidence strength, temporal decay, and branch pressure may be represented as observables when:

- their provenance is explicit;
- their units are defined;
- their basis is exact;
- their operator is Hermitian;
- their effect on the final classical projection is explainable.

## 6.7. Quantum channels and feasible-subspace preservation

A valid advisory state update is a completely positive trace-preserving map:

\[
\Phi(\rho)
=
\sum_k K_k\rho K_k^\dagger,
\qquad
\sum_k K_k^\dagger K_k=I.
\]

For a channel promoted into the Hedgehog profile, the feasible subspace must be invariant. One acceptable law is:

\[
K_kP_F=P_FK_kP_F
\qquad \forall k,
\]

which implies:

\[
\Phi(P_F\rho P_F)
=
P_F\Phi(P_F\rho P_F)P_F.
\]

Every channel must be versioned, canonicalized, provenance-bound, BSEP-scoped, and restricted to the validated candidate basis.

A provider may propose semantic evidence that influences locally constructed channel parameters. A provider may not directly supply executable operators, basis order, hidden features, or scope-widening instructions.

## 6.8. Numerical identity and tolerance law

Cryptographic identity and numerical equivalence are different concepts.

- hashes bind exact canonical bytes;
- numerical comparisons use an explicit tolerance profile;
- the tolerance profile is part of artifact identity;
- NaN and infinity are forbidden;
- sparse and dense encodings of the same matrix must canonicalize to a declared common representation or remain different artifacts;
- approximate numerical equality must never be used to rewrite an identity hash;
- no malformed state is automatically repaired in the Root path.

Canonical numeric encoding must be language-independent and versioned. Native JSON floating-point formatting is not sufficient as an identity law without an explicit canonical profile.

## 6.9. Classical limit requirement

Every promoted quantum-inspired profile must provide one of:

1. an exact classical limit that reproduces the frozen classical profile;
2. an explicitly bounded approximation with a declared error metric, tolerance, and reason why exact recovery is mathematically unavailable.

A profile without a valid classical-limit proof remains research-only and cannot enter the selectable Hedgehog conformance surface.

# 7. Planned common contracts

These contracts are future design targets only. They do not exist in the current six-gate runtime.

## 7.1. QuantumMathProfileManifestV01

Required fields:

- `profile_id`;
- `profile_version`;
- `profile_class`;
- `implementation_status`;
- `source_gate6_baseline_ref`;
- `classical_profile_ref`;
- `classical_limit_kind`;
- `numerical_tolerance_profile_ref`;
- `physical_qpu_required: false` for the initial profile;
- `quantum_advantage_claimed: false` unless separately proven;
- `changes_root_law: false`;
- `changes_corridor_law: false`;
- `changes_replay_law: false`.

## 7.2. QuantumCandidateBasisV01

Required fields:

- `basis_id`;
- `source_candidate_set_ref`;
- `source_candidate_set_digest`;
- ordered `candidate_ids`;
- `dimension`;
- `hardmask_vector` when a full compatibility basis is used;
- `feasible_candidate_ids`;
- `feasible_support_digest`;
- `bsep_ref`;
- `root_context_ref`;
- `policy_version`;
- `canonicalization_version`;
- `created_by_runtime`;
- `authority_created: false`.

## 7.3. QuantumStateEnvelopeV01

Required fields:

- `state_id`;
- `profile_class`;
- `basis_ref`;
- `representation_kind`;
- `matrix_encoding_profile`;
- `matrix_digest`;
- `trace_value`;
- `minimum_eigenvalue`;
- `hermitian_check`;
- `positive_semidefinite_check`;
- `normalization_check`;
- `feasible_support_check`;
- `source_refs`;
- `channel_history_refs`;
- `numerical_tolerance_profile_ref`;
- `advisory_only: true`;
- `creates_authority: false`;
- `creates_permission: false`;
- `creates_effect: false`.

## 7.4. QuantumObservableEnvelopeV01

Required fields:

- `observable_id`;
- `basis_ref`;
- `observable_kind`;
- `operator_encoding_profile`;
- `operator_digest`;
- `hermitian_check`;
- `units`;
- `source_feature_refs`;
- `source_lineage_refs`;
- `canonicalization_version`;
- `advisory_only: true`.

## 7.5. QuantumContextChannelV01

Required fields:

- `channel_id`;
- `profile_class`;
- `source_bsep_ref`;
- `visible_feature_refs`;
- `forbidden_feature_refs`;
- `kraus_operator_digests` or an equivalent canonical channel description;
- `trace_preserving_check`;
- `complete_positivity_check`;
- `feasible_subspace_preserved`;
- `context_widening_detected`;
- `raw_secret_included`;
- `provider_supplied_operator_used: false`;
- `authority_created: false`.

## 7.6. QuantumProjectionReportV01

Required fields:

- `projection_report_id`;
- `profile_class`;
- `source_state_ref`;
- `classical_profile_ref`;
- `candidate_probabilities`;
- `observable_expectations`;
- `ranked_candidate_ids`;
- `contextual_contribution_rows`;
- optional `coherence_or_interference_rows` only when mathematically applicable;
- `classical_limit_ref`;
- `numerical_residuals`;
- `explanation_rows`;
- `requires_root_review`;
- `authority_created: false`;
- `permission_created: false`;
- `effect_created: false`.

## 7.7. QuantumBackendEvidenceV01

This is evidence about advisory mathematical computation. It is not `ExecutionEvidence` for a consequential effect.

Required fields:

- `backend_evidence_id`;
- `backend_id`;
- `backend_kind`;
- `backend_version`;
- `algorithm_profile_id`;
- `profile_class`;
- `operator_or_circuit_digest`;
- `transpiled_circuit_digest` when applicable;
- `shot_count` when applicable;
- `noise_model_digest` when applicable;
- `calibration_snapshot_ref` when applicable;
- `raw_counts_digest` when applicable;
- `classical_projection_ref`;
- `source_state_ref`;
- `backend_call_count`;
- `replay_reruns_backend: false`;
- `authority_created: false`;
- `permission_created: false`;
- `real_world_effects_count: 0`.

No field in these contracts may be interpreted as a Root decision, ActionCommitPacket, effect handle, Receipt, or permission.

# 8. Q0 — Post-Gate-6 quantum preflight

## 8.1. Goal

Freeze the tagged and independently audited classical Hedgehog kernel and prove that the quantum workstream cannot silently mutate the constitutional runtime.

## 8.2. Required actions

- create an immutable post-Gate-6 baseline tag;
- record SHA-256 digests for Root, Transition Registry, Effect Firewall, ActionCommitPacket, lifecycle, Corridor, Receipt, Replay, BSEP, and HardMask contracts;
- freeze current classical AVF and GT reference outputs;
- record the current model-swap and backend-swap conformance baselines;
- create `QuantumProfileManifestV01` with every quantum capability set to `NOT_IMPLEMENTED`;
- create forbidden-path tests proving the quantum package cannot import or invoke effect adapters directly;
- define numerical tolerance profiles;
- define exact allowed and forbidden claims;
- record the current full Gate-6 gauntlet result.

## 8.3. Definition of Done

- baseline tag exists and is independently verifiable;
- all constitutional digests are recorded;
- no runtime path changed;
- no current claim changed;
- quantum package remains absent or empty;
- current full gauntlet remains green.

## 8.4. Effort

- focused effort: 1–2 days;
- complexity: 3/10;
- primary knowledge: release freeze, provenance, conformance, numerical-policy design.

---

# 9. Quantum Gate 1 — Quantum-Inspired State and Context ABI

## 9.1. Goal

Create the smallest stable quantum-inspired advisory-state ABI with exact classical embedding and classical projection, without changing current runtime decisions, authority classes, or effect paths.

## 9.2. Integration points

Q1 integrates only after the existing classical pipeline has produced:

- validated candidate set;
- HardMask result;
- BSEP projection;
- source lineage;
- numerical feature rows.

Q1 returns only a classical projection report. Root never receives a raw matrix as a decision object.

## 9.3. Slices

### Q1-A — Linear algebra core

Implement:

- canonical matrix encoding;
- Hermitian check;
- trace check;
- positive-semidefinite check;
- eigenvalue tolerance policy;
- matrix digest;
- dimension and basis validation.

### Q1-B — Frozen classical-profile embedding

Read the exact normalized distribution emitted by the frozen Gate-4 classical profile and implement:

\[
(p_1^{\mathrm{cl}},\ldots,p_n^{\mathrm{cl}})
\mapsto
\operatorname{diag}(p_1^{\mathrm{cl}},\ldots,p_n^{\mathrm{cl}}).
\]

Then prove exact extraction of the same distribution within the declared numerical profile. Do not invent a new normalizer in Q1.

### Q1-C — HardMask projection

Apply the existing HardMask before state construction. Prefer a feasible-only basis. If a full compatibility basis is retained, apply the HardMask projector and prove `P_F rho P_F = rho` before and after every promoted update.

Forbidden candidates must have exactly zero support, not merely low probability.

### Q1-D — BSEP observation context

Create a runtime-owned `QuantumContextChannelV01` from validated BSEP-visible features.

The provider may influence semantic feature values only through the existing bounded semantic path. It may not provide operators, matrix indices, basis order, hidden features, or scope-widening instructions.

### Q1-E — Classical projection and explanation

Return:

- candidate probabilities;
- expected observable values;
- ranked candidates;
- source lineage;
- numerical warnings;
- reason rows suitable for Post V&V and Root review.

## 9.4. Numerical rules

- matrix dimension must equal basis dimension;
- trace tolerance must be explicit;
- negative eigenvalues below tolerance fail closed;
- NaN and infinity fail closed;
- basis reorder without digest change is forbidden;
- canonical numeric encoding and tolerance profiles must be versioned;
- sparse and dense encodings must canonicalize to the same digest only under an explicit common encoding profile;
- exact artifact identity is byte-based, while numerical comparison is tolerance-based;
- no automatic repair of malformed states in the Root path.

## 9.5. Required tests

- diagonal classical state round-trips exactly;
- candidate-order mutation is rejected;
- forged basis digest is rejected;
- non-Hermitian state is rejected;
- non-positive state is rejected;
- wrong trace is rejected;
- zero feasible mass returns to Root;
- HardMask candidate cannot be restored by renormalization;
- BSEP-hidden feature is rejected;
- provider-supplied operator is rejected;
- projection report cannot claim authority, permission, effect, or truth;
- feasible-subspace support is preserved by every admitted channel;
- classical Gate-6 decision remains unchanged in shadow mode.

## 9.6. Reference demo

Use an existing post-Gate-6 domain with at least three feasible candidates and one HardMask-rejected candidate.

Show:

- current classical distribution;
- density-state embedding;
- HardMask projection;
- classical projection recovery;
- identical Root-visible decision surface.

## 9.7. Definition of Done

- all contracts and schemas exist;
- exact classical embedding is proven;
- HardMask remains absolute;
- BSEP context cannot widen;
- quantum state remains advisory;
- current runtime output remains unchanged;
- Q1 conformance category passes.

## 9.8. Effort

- focused effort: 5–8 days;
- complexity: 7/10;
- primary knowledge: linear algebra, density matrices, numerical validation, ABI and schema design.

Expected constitutional changes: zero.

---

# 10. Quantum Gate 2 — Quantum-Inspired AVF and BSEP Contextual Dynamics

## 10.1. Goal

Extend the frozen classical Gate-4 AVF from an independent candidate-score surface into an optional contextual candidate-state model with:

- an exact or explicitly bounded classical limit;
- Hermitian, lineage-bound contextual coupling;
- feasible-subspace preservation;
- advisory-only branch pressure;
- unchanged Root authority.

## 10.2. Exact bridge from the frozen Gate-4 AVF

Let the frozen classical AVF produce a score vector:

\[
a=(a_1,\ldots,a_n).
\]

Let its exact versioned normalization be:

\[
p^{\mathrm{cl}}
=
\mathcal{N}_{\mathrm{AVF},v}(a,C_F).
\]

The exact classical embedding is:

\[
\rho_{\mathrm{cl}}
=
\sum_{c_i\in C_F}
p_i^{\mathrm{cl}}|c_i\rangle\langle c_i|.
\]

Q2 must reproduce the normalization profile that Gate 4 actually freezes. It must not claim in advance that the current AVF is softmax-based.

### Optional Gibbs/softmax reference profile

If and only if the frozen classical AVF defines:

\[
p_i^{\mathrm{cl}}
=
\frac{e^{\beta a_i}}
{\sum_{c_j\in C_F}e^{\beta a_j}},
\]

then define:

\[
H_0=-\operatorname{diag}(a_1,\ldots,a_n),
\]

and:

\[
\rho_{\beta,0}
=
\frac{e^{-\beta H_0}}
{\operatorname{Tr}(e^{-\beta H_0})}.
\]

Under that declared profile, the Gibbs construction is the exact diagonal classical limit. Otherwise, Q2 uses the exact Gate-4 normalizer without relabeling it as Gibbs or softmax.

## 10.3. Contextual coupling

Define a validated interaction matrix:

\[
K_{ij}
=
\lambda_S S_{ij}
-
\lambda_C C_{ij}
+
\lambda_L L_{ij}
+
\lambda_B B_{ij}.
\]

Where:

- \(S_{ij}\): validated synergy or compatibility;
- \(C_{ij}\): validated conflict or mutual exclusion;
- \(L_{ij}\): validated lineage or causal relation;
- \(B_{ij}\): validated BSEP-context relation.

The runtime must enforce:

\[
K=K^\dagger.
\]

Every nonzero off-diagonal term must have a source-lineage row. If source relations are directional, the profile must define and justify the Hermitian construction used for the advisory operator.

On a full compatibility basis, require:

\[
K=P_FKP_F.
\]

Define the feasible contextual Hamiltonian:

\[
H_F
=
P_F\left(-\operatorname{diag}(a)-K\right)P_F.
\]

Then:

\[
H_F=H_F^\dagger.
\]

An optional contextual Gibbs state is:

\[
\rho_{\beta,F}
=
\frac{e^{-\beta H_F}}
{\operatorname{Tr}(e^{-\beta H_F})},
\]

computed only on the feasible support.

No contextual term may restore a forbidden candidate, widen BSEP, modify a policy exclusion, or change an authority class.

## 10.4. BSEP context

Each BSEP projection defines the exact actor-visible context from which local contextual operators may be constructed.

The runtime must prove:

- no hidden field entered the operator;
- no raw secret entered the operator;
- basis order is local and canonical;
- every contextual feature has provenance;
- one Root's BSEP cannot silently widen another Root's observation context;
- context transformation remains advisory.

## 10.5. Contextual contribution explanation

For each candidate, the report must separate:

- diagonal classical contribution;
- contextual coupling contribution;
- conflict suppression;
- synergy reinforcement;
- lineage reinforcement;
- BSEP-context contribution;
- optional coherence/interference contribution only when the selected profile actually contains it;
- total projected probability;
- numerical residual.

The report must not use unexplained language such as `quantum intuition selected this candidate`.

## 10.6. Branch-budget allocation

Quantum AVF may propose a normalized exploration budget:

\[
b_i=B_{\mathrm{total}}p_i.
\]

The runtime may discretize this into branch depth, sample count, or compute tier.

The allocator may reduce or redistribute compute. It may not:

- create a candidate;
- restore a forbidden candidate;
- add a topology edge;
- create a child cell directly;
- widen BSEP;
- increase action scope;
- skip Root review;
- convert branch pressure into permission.

## 10.7. Integration mode

Q2 begins in shadow mode:

- the frozen classical AVF controls the actual runtime path;
- the quantum-inspired AVF computes in parallel;
- all differences are recorded as evidence;
- Root-visible authority behaviour remains identical;
- effect behaviour remains identical;
- classical fallback remains immediately available.

After classical-limit, contextual, numerical, and authority-invariance tests pass, the profile may be selectable through a versioned policy such as:

- `CLASSICAL_AVF_V1`;
- `QUANTUM_INSPIRED_AVF_V1`.

## 10.8. Required tests

- the frozen Gate-4 classical distribution embeds and projects exactly;
- the optional Gibbs profile is enabled only when its normalizer matches the frozen classical profile;
- zero coupling reproduces the classical projection;
- non-Hermitian coupling is rejected;
- coupling without lineage is rejected;
- hidden BSEP feature is rejected;
- conflict and synergy contributions are separately explainable;
- feasible-subspace support is preserved;
- forbidden candidate remains exactly absent;
- branch budget sums correctly;
- branch pressure cannot create permission;
- backend numerical noise cannot alter authority class;
- classical fallback remains available;
- shadow-mode differences are evidence-bound.

## 10.9. Reference demos

Demo A — contextual airline candidate selection:

- at least three feasible candidates and one HardMask-rejected candidate;
- two feasible candidates with similar classical score;
- one context-specific synergy;
- one conflict relation;
- exact explanation of changed advisory ranking;
- unchanged Root authority and effect boundary.

Demo B — sensor or enterprise branch allocation:

- stable state uses a shallow deterministic or reuse path;
- anomaly creates validated contextual coupling;
- the profile increases compute budget only for affected branches;
- no action permission is created.

## 10.10. Definition of Done

- the frozen Gate-4 AVF is an exact or explicitly bounded classical limit;
- contextual operators are Hermitian and lineage-bound;
- feasible support remains closed;
- BSEP context remains sealed;
- branch pressure remains advisory;
- classical fallback remains available;
- Root and Corridor behaviour are invariant;
- Q2 conformance and gauntlet act pass.

## 10.11. Effort

- focused effort: 8–12 days;
- complexity: 8/10;
- primary knowledge: spectral methods, matrix exponentials, contextual probability, numerical stability, AVF internals, provenance-bound operator construction.

Expected constitutional changes: zero.

# 11. Quantum Gate 3 — Quantum-Inspired MultiRoot Game and Strategy Geometry

## 11.1. Goal

Extend the frozen classical Strong GT profile into an optional correlated MultiRoot advisory geometry while preserving:

- no-deal;
- individual rationality;
- Pareto filtering;
- bounded bargaining analysis;
- Root-local policy;
- independent Root decisions;
- absence of a SuperRoot.

## 11.2. Joint strategy space

For Roots \(r\in R\), define local feasible strategy spaces:

\[
\mathcal{H}_r
=
\operatorname{span}\{|s_{r,1}\rangle,\ldots,|s_{r,n_r}\rangle\}.
\]

Define the joint advisory space:

\[
\mathcal{H}_{\mathrm{joint}}
=
\bigotimes_{r\in R}\mathcal{H}_r.
\]

A joint advisory state satisfies:

\[
\rho_{\mathrm{joint}}\succeq0,
\qquad
\operatorname{Tr}(\rho_{\mathrm{joint}})=1.
\]

This state is not a Root, not an agreement, not a shared authority object, and not a transaction outcome.

## 11.3. Feasibility projector

Let \(P_F\) project onto the jointly feasible strategy subspace after all classical policy, authority, temporal, and contractual gates.

The joint state must satisfy:

\[
P_F\rho P_F=\rho.
\]

No optimization may assign support outside the jointly feasible subspace.

## 11.4. Utility observables

For each Root \(r\), define a Hermitian utility observable:

\[
U_r=U_r^\dagger.
\]

Expected utility is:

\[
\bar U_r(\rho)=\operatorname{Tr}(\rho U_r).
\]

Every utility component must be traceable to the frozen Gate-4 utility envelope and the local Root's policy.

## 11.5. Individual rationality

Let \(D_r\) be Root \(r\)'s disagreement or no-deal utility.

A jointly admissible advisory state must satisfy:

\[
\operatorname{Tr}(\rho U_r)\ge D_r
\qquad \forall r.
\]

Failure for any Root returns `NO_INDIVIDUALLY_RATIONAL_JOINT_STATE`.

No optimizer, shared state, measurement, or bargaining function may coerce a Root into an outcome below its no-deal point.

## 11.6. Pareto efficiency

A feasible state \(\rho\) is Pareto-dominated when another feasible state \(\sigma\) satisfies:

\[
\operatorname{Tr}(\sigma U_r)
\ge
\operatorname{Tr}(\rho U_r)
\quad \forall r,
\]

with strict inequality for at least one Root.

Dominated states may be removed from the advisory frontier. Removal does not create agreement.

## 11.7. Quantum-compatible Nash bargaining

One reference objective is:

\[
\max_{\rho}
\sum_r\alpha_r
\log\left(
\operatorname{Tr}(\rho U_r)-D_r+\varepsilon
\right),
\]

subject to:

\[
\rho\succeq0,
\qquad
\operatorname{Tr}(\rho)=1,
\qquad
P_F\rho P_F=\rho,
\qquad
\operatorname{Tr}(\rho U_r)\ge D_r.
\]

The objective returns an advisory compromise state only. It does not bind any Root.

## 11.8. Root-local admissible strategy channels

A Root-local advisory strategy operation is represented as a completely positive trace-preserving channel \(\Lambda_r\) acting only on Root \(r\)'s strategy space:

\[
\rho'
=
(\Lambda_r\otimes I_{-r})(\rho).
\]

The maximization domain is not the set of every mathematically possible CPTP map. It is the exact Root-policy-admissible set:

\[
\Lambda_r\in\mathcal{A}_r.
\]

Every \(\Lambda_r\in\mathcal{A}_r\) must:

- act only on Root \(r\)'s local advisory strategy space;
- preserve the joint feasible subspace;
- preserve the local no-deal boundary;
- use only locally permitted strategy transformations;
- carry exact policy and lineage references.

A local channel may not:

- sign for another Root;
- transfer authority;
- mutate another Root's policy;
- create cross-Root permission;
- finalize an agreement.

## 11.9. Regret and unilateral deviation

Define Root-local deviation regret:

\[
R_r(\rho)
=
\max_{\Lambda_r\in\mathcal{A}_r}
\operatorname{Tr}\left[
U_r(\Lambda_r\otimes I_{-r})(\rho)
\right]
-
\operatorname{Tr}(U_r\rho).
\]

The result is advisory evidence about strategic stability. It does not force a Root to accept or reject.

## 11.10. Representation and resource bounds

The joint state dimension grows as \(\prod_r n_r\). Therefore:

- dense joint-state construction requires an explicit maximum dimension;
- sparse, factorized, low-rank, or tensor-network representations must be preferred when appropriate;
- resource budgets are part of the execution-mode policy;
- exceeding a dimension, memory, or compute budget returns to Root or classical fallback;
- no hidden exponential allocation is permitted;
- no approximation may change feasibility, no-deal, authority, or local-policy law.

## 11.11. Classical limits

A diagonal joint density matrix reproduces a classical correlated strategy distribution.

Product states reproduce independent mixed strategies.

The frozen classical Gate-4 strategy profile must be exactly recoverable under the declared classical-limit configuration.

A non-separable advisory state on a classical simulator is a mathematical representation only. It is not a public claim of physical entanglement.

## 11.12. MultiRoot locality law

The joint advisory state must satisfy:

- no SuperRoot exists;
- each Root receives a local classical projection;
- each Root accepts or rejects independently;
- foreign evidence remains evidence;
- shared correlation does not transfer authority;
- a joint measurement result does not become a transaction outcome;
- only existing cross-Root contracts may bind the final transaction.

## 11.13. Slices

### Q3-A — Density-state representation of frozen Strong GT

Encode the frozen classical strategy distribution as a diagonal joint state and prove identical Pareto, no-deal, bargaining, and Root-local outputs.

### Q3-B — Classically correlated strategy profile

Add non-product diagonal states representing classical correlation without coherence claims.

### Q3-C — Order-sensitive Root-local channels

Introduce noncommuting local advisory transformations with explicit policy, explanation, admissible-channel bounds, and BSEP context.

### Q3-D — Advanced non-separable advisory states

Permit advanced non-separable states only after Q3-A through Q3-C pass, only under strict resource limits, and only when every nonclassical term has validated lineage.

### Q3-E — Root-local projection and independent acceptance

Produce one local report per Root and prove that no joint object can accept for all Roots.

## 11.14. Required tests

- frozen classical Strong GT is exactly reproduced;
- no-deal point is preserved;
- individually irrational states are rejected;
- Pareto-dominated state is removed correctly;
- bargaining objective is deterministic under fixed input and tolerance profile;
- inadmissible local channel is rejected;
- local channel cannot mutate another Root's state or policy;
- local channel preserves joint feasibility;
- joint state cannot become SuperRoot;
- shared correlation cannot transfer authority;
- each Root receives an independent report;
- one Root rejection prevents false joint completion;
- quantum-inspired GT cannot create ActionCommitPacket;
- resource overflow returns to fallback without scope widening;
- classical fallback remains available.

## 11.15. Reference demos

Demo A — Airline MultiRoot strategy:

- ClientRoot, AirlineRoot, and BankRoot strategy spaces;
- explicit no-deal points;
- correlated strategy candidates;
- individual rationality;
- Pareto frontier;
- bargaining recommendation;
- independent Root accept or reject.

Demo B — Supplier or TestFlix lease negotiation:

- provider, client, bank, and optional device Root;
- long-lived capability terms;
- renewal and no-renewal strategies;
- no party forced below no-deal utility;
- no authority transfer.

## 11.16. Definition of Done

- frozen classical GT is an exact limit;
- individual rationality remains absolute;
- Pareto and bargaining are explainable;
- local strategy channels are policy-admissible and Root-local;
- resource bounds are enforced;
- no SuperRoot appears;
- independent Root decisions remain mandatory;
- Q3 conformance and gauntlet act pass.

## 11.17. Effort

- focused effort: 10–16 days;
- complexity: 9/10;
- primary knowledge: game theory, convex optimization, semidefinite programming, tensor products, quantum channels, numerical approximation, MultiRoot contracts.

Expected constitutional changes: zero.

# 12. Quantum Gate 4 — Open-System DRS, Quantum-Walk Fractal Search, Backend Conformance, and Release

## 12.1. Goal

Integrate quantum-inspired advisory state with temporal DRS, outcome feedback, Fractal branch exploration, simulator and optional physical-QPU backends, evidence capture, Replay compatibility, and final conformance.

## 12.2. Classical hard gates execute first

Before any quantum-inspired state is constructed, the existing classical pipeline must apply:

1. TemporalHardGate.
2. PolicyGate.
3. ConflictGate.
4. Quarantine and DeadEnd gates.
5. Permission and authority eligibility checks.
6. Root-owned lifecycle state.

Expired, revoked, superseded, blocked, quarantined, dead-end, consumed, uncertain-closed, or otherwise ineligible records must not enter the quantum-inspired advisory state.

## 12.3. Quantum-inspired DRS state pointer

A `QuantumDRSStatePointerV01` may refer to a versioned advisory state derived from eligible DRS records.

The pointer may contain:

- source record refs;
- source temporal-query ref;
- basis digest;
- state digest;
- profile class;
- channel-history refs;
- decay-profile ref;
- posterior projection ref;
- expiry and invalidation refs;
- `creates_permission: false`;
- `reuses_authority: false`.

The full matrix may remain in a local artifact store. DRS remains pointer-first. DRS never becomes an authority or an opaque quantum-state database.

## 12.4. Open-system advisory aging

A Markovian advisory profile may use a GKSL/Lindblad-style equation:

\[
\frac{d\rho}{dt}
=
-i[H_t,\rho]
+
\sum_k\gamma_k(t)
\left(
L_k\rho L_k^\dagger
-
\frac{1}{2}
\{L_k^\dagger L_k,\rho\}
\right).
\]

The promoted profile must enforce:

\[
H_t=H_t^\dagger,
\qquad
\gamma_k(t)\ge0.
\]

The generator, collapse operators, and numerical integration must preserve:

- positivity;
- trace;
- feasible support;
- BSEP visibility;
- source lineage;
- declared numerical error bounds.

Potential advisory meanings include:

- contextual coherence decay;
- uncertainty growth;
- aging of historical priors;
- conflict pressure;
- loss of relevance after WorldState change;
- stabilization after repeated validated outcomes.

This is a mathematical memory-state profile. It is not a claim that DRS is a physical open quantum system.

Expiry, revocation, supersession, and kill-switch remain discrete classical hard events. They are never represented as merely low probability.

## 12.5. Validated evidence update

A new validated evidence item may update advisory state through a versioned channel:

\[
\rho'=\Phi_e(\rho).
\]

The channel must be CPTP on its declared state space and preserve:

- source lineage;
- temporal eligibility;
- BSEP visibility;
- Root ownership boundaries;
- feasible support;
- state positivity and trace;
- explainable change in the classical projection.

## 12.6. Outcome feedback

OutcomeFeedbackEnvelope may calibrate:

- Hamiltonian diagonal terms;
- validated coupling strengths;
- decay rates;
- branch-budget priors;
- review-pressure observables;
- backend-selection policy.

Outcome feedback may not modify:

- HardMask;
- Root law;
- Transition Registry;
- authority class;
- action scope;
- Corridor law;
- historical evidence.

## 12.7. Quantum-walk Fractal exploration

Let the current Fractal Runtime produce a validated candidate graph:

\[
G=(V,E).
\]

The graph operator used for a continuous-time quantum walk must be Hermitian. For an undirected validated graph, one reference profile is:

\[
H_F
=
\gamma L_G
-
\lambda_v V_{\mathrm{AVF}}
+
\lambda_r V_{\mathrm{risk}},
\]

where:

- \(L_G=L_G^\dagger\) is a graph Laplacian or another validated Hermitian graph operator;
- \(V_{\mathrm{AVF}}=V_{\mathrm{AVF}}^\dagger\) encodes advisory attraction;
- \(V_{\mathrm{risk}}=V_{\mathrm{risk}}^\dagger\) encodes risk or review pressure;
- \(\gamma,\lambda_v,\lambda_r\) are real versioned parameters.

For a pure-state experiment:

\[
|\psi(t)\rangle=e^{-iH_Ft}|\psi(0)\rangle.
\]

A density-state profile may equivalently evolve:

\[
\rho(t)=e^{-iH_Ft}\rho(0)e^{iH_Ft}.
\]

The resulting node distribution may propose:

- branch order;
- branch budget;
- bounded exploration frontier;
- candidate branch suppression;
- revisit priority after Delta invalidation.

It may not:

- create a child cell;
- add or rewrite an edge;
- change the validated graph identity;
- widen scope;
- bypass BSEP;
- create permission;
- produce an effect.

Directed or asymmetric runtime graphs require a separately reviewed Hermitian construction. Raw directed adjacency must not be silently treated as a Hamiltonian.

## 12.8. Backend abstraction

Define a stable `QuantumMathBackendV01` interface with implementations such as:

- deterministic dense simulator;
- sparse classical simulator;
- tensor-network simulator;
- shot-based simulator;
- optional physical-QPU adapter.

Every backend must return the same typed `QuantumBackendEvidenceV01` and the same Root-visible classical projection contract.

Backend swap must not change:

- feasible candidates;
- authority class;
- Root ownership;
- Corridor behaviour;
- effect behaviour;
- Replay non-execution.

## 12.9. Optional physical-QPU algorithms

Permitted experiments include:

- state preparation for small candidate spaces;
- projective or generalized measurement experiments;
- variational optimization;
- QAOA for bounded combinatorial subproblems;
- quantum walks on small validated graphs;
- sampling correlated strategy states.

No physical-QPU experiment may claim quantum advantage without:

- a controlled classical baseline;
- matched problem instance;
- matched input and output contract;
- matched error metric;
- matched resource accounting;
- reproducible backend evidence;
- independent review of the claim.

A QPU backend that does not outperform or uniquely complement the classical baseline remains an experimental backend demonstration.

## 12.10. Replay of backend evidence

Replay must not rerun a simulator or physical-QPU backend.

It verifies committed evidence such as:

- backend ID and version;
- algorithm-profile ID;
- profile class;
- operator or circuit digest;
- transpiled circuit digest;
- shot count;
- calibration snapshot;
- noise-model digest;
- raw counts digest;
- classical projection;
- numerical-tolerance profile;
- downstream Root binding;
- causal dependency chain.

Backend stochasticity is preserved as historical evidence, not regenerated as a new event.

## 12.11. Conformance categories

Add:

- QuantumStateConformance;
- ClassicalLimitConformance;
- HardMaskProjectorConformance;
- FeasibleSupportConformance;
- BSEPContextConformance;
- QuantumAVFConformance;
- QuantumGTConformance;
- QuantumDRSConformance;
- QuantumFractalConformance;
- BackendSwapConformance;
- QuantumEvidenceReplayCompatibility;
- QuantumAuthorityInvariance;
- QuantumPhysicalityNonclaimConformance.

## 12.12. Final quantum gauntlet

The final quantum gauntlet should contain at least:

1. frozen classical-state round trip;
2. forbidden candidate projection;
3. feasible-subspace preservation;
4. BSEP context isolation;
5. contextual AVF ranking;
6. frozen classical AVF limit;
7. MultiRoot individual rationality;
8. Pareto and bargaining projection;
9. policy-admissible local strategy deviation;
10. DRS open-system aging;
11. Delta update of one affected state;
12. Hermitian quantum-walk branch pressure;
13. backend swap;
14. Replay with zero backend calls;
15. malicious module attempts;
16. unchanged classical Gate-6 gauntlet.

## 12.13. Malicious module attempts

The adversarial pack must include:

- non-positive state;
- non-Hermitian state or operator;
- hidden candidate basis reorder;
- HardMask support restoration;
- channel leaking support outside feasible space;
- coupling without lineage;
- hidden BSEP feature;
- provider-supplied operator;
- report claiming authority;
- report creating ActionCommitPacket;
- backend returning effect handle;
- QPU result bypassing Post V&V;
- DRS state resurrecting revoked packet;
- measurement treated as truth;
- Replay rerunning backend;
- stochastic backend changing authority behaviour;
- quantum branch allocator widening scope;
- physical-entanglement claim from classical simulation;
- quantum-advantage claim without matched benchmark.

## 12.14. Definition of Done

- DRS hard gates precede advisory-state construction;
- open-system update is versioned, mathematically valid, and explainable;
- feasible support is preserved;
- Fractal quantum-walk profile remains advisory;
- simulator backends are interchangeable under the declared tolerance profile;
- authority behaviour is invariant;
- Replay performs zero quantum-backend calls;
- current Gate-6 gauntlet remains green;
- quantum gauntlet passes;
- physical-QPU and quantum-advantage nonclaims are explicit.

## 12.15. Effort

Classical-simulator core profile:

- focused effort: 12–20 days;
- complexity: 9.5/10;
- primary knowledge: open quantum systems, Kraus and GKSL dynamics, graph spectral methods, DRS and time, numerical integration, Replay engineering.

Optional physical-QPU profile:

- additional focused effort: 10–30 days;
- complexity: 9.5/10;
- primary knowledge: circuit compilation, backend noise, QAOA or quantum walks, matched benchmarking, backend evidence.

Primary risk: confusing an elegant quantum-inspired model with demonstrated computational advantage.

Expected constitutional changes: zero.

# 13. What is replaced and what is extended

| Existing component | Action |
|---|---|
| `avf_v02` / Full AVF | preserved; Quantum AVF is a selectable sibling profile |
| Strong GT | preserved; Quantum GT is a sibling advisory profile |
| BSEP | preserved; optional context-channel sidecar or ref added |
| DRS MeaningRecord | preserved and pointer-first; optional quantum-state pointer added |
| TimeEnvelope | not replaced |
| ExecutionModeRouter | preserved; math or backend profile selected by separate versioned policy |
| Fractal Runtime | preserved; quantum profile proposes branch budget or order |
| Delta Runtime | preserved; recomputes only affected quantum states or subgraphs |
| OutcomeFeedbackEnvelope | preserved; becomes input to a versioned quantum update channel |
| Root | unchanged |
| ActionCommitPacket | unchanged |
| Corridor | unchanged |
| Receipt | unchanged |
| Crypto and Replay | extended with quantum execution evidence; core law unchanged |

---

# 14. Recommended implementation file map

Only the roadmap exists before Gate 6.

```text
specs/
  future/
    quantum/
      hedgehog_quantum_mathematical_extension_roadmap_v2_0.md
```

After Gate 6 closes, Q0 may create only the freeze/preflight surfaces required to protect the classical baseline. It must not create functioning quantum runtime code.

When the owner approves Q1 preflight, create the normative mathematical surfaces before or together with the first Q1 code:

```text
specs/
  quantum_math_appendix_v1_0.md
  quantum_math_invariants_v1_0.md
```

Those two root-level specifications are normative only for the post-Gate-6 quantum workstream. They must never be back-projected into claims about Gate 1–6.

Planned implementation map:

```text
hedgehog/
  quantum_math/
    __init__.py
    contracts_v01.py
    numeric_encoding_v01.py
    state_v01.py
    observables_v01.py
    projectors_v01.py
    channels_v01.py
    classical_projection_v01.py
    quantum_avf_v01.py
    quantum_gt_v01.py
    quantum_drs_v01.py
    quantum_fractal_v01.py
    backend_v01.py
    evidence_v01.py
    conformance_v01.py

schemas/
  quantum_math_profile_manifest_v01.schema.json
  quantum_candidate_basis_v01.schema.json
  quantum_state_envelope_v01.schema.json
  quantum_observable_envelope_v01.schema.json
  quantum_context_channel_v01.schema.json
  quantum_projection_report_v01.schema.json
  quantum_avf_report_v01.schema.json
  quantum_gt_advisory_report_v01.schema.json
  quantum_drs_state_pointer_v01.schema.json
  quantum_backend_evidence_v01.schema.json

specs/
  future/
    quantum/
      hedgehog_quantum_mathematical_extension_roadmap_v2_0.md
  quantum_math_appendix_v1_0.md
  quantum_math_invariants_v1_0.md

docs/
  quantum/
    quantum_profile_q0_preflight_v01.md
    quantum_gate_1_checkpoint_v01.md
    quantum_gate_2_checkpoint_v01.md
    quantum_gate_3_checkpoint_v01.md
    quantum_gate_4_checkpoint_v01.md
    quantum_backend_nonclaims_v01.md

tests/
  quantum_math/
    test_numeric_encoding_v01.py
    test_state_v01.py
    test_classical_limit_v01.py
    test_feasible_support_v01.py
    test_quantum_avf_v01.py
    test_quantum_gt_v01.py
    test_quantum_drs_v01.py
    test_quantum_fractal_v01.py
    test_quantum_backend_invariance_v01.py
    test_quantum_authority_adversary_v01.py

demo/
  run_quantum_math_conformance_v01.py
  run_quantum_math_gauntlet_v01.py
```

The actual Q1 preflight must inventory the post-Gate-6 repository and may refine filenames without changing the constitutional boundaries in this roadmap.

# 15. Global Quantum Profile invariants

1. The quantum-inspired profile is optional and post-Gate-6.
2. Quantum-inspired state is advisory state, not authority.
3. Classical hard gates execute before advisory-state construction.
4. HardMask executes before the profile and remains absolute.
5. Zero feasible mass returns to Root; forbidden space is never renormalized into feasibility.
6. Every promoted state and channel preserves feasible support.
7. BSEP controls observable context; a backend cannot widen context.
8. Quantum-inspired mathematics cannot create CandidateVectors from raw provider text.
9. Every operator used as a Hamiltonian or observable is Hermitian under its declared profile.
10. Every promoted channel is mathematically valid, versioned, and provenance-bound.
11. Quantum AVF changes advisory ranking pressure and compute budget only.
12. Quantum GT proposes strategy geometry only.
13. A MultiRoot joint state is not a SuperRoot.
14. Root-local strategy channels are restricted to Root-policy-admissible sets.
15. DRS eligibility remains classical and fail-closed.
16. Memory state cannot create permission or reuse authority.
17. Outcome update cannot rewrite hard law or historical evidence.
18. Root decides from a classical explainable projection.
19. ActionCommitPacket remains Root-created.
20. Corridor remains the sole consequential effect path.
21. Receipt remains evidence only.
22. Replay never reruns a quantum backend.
23. Backend stochasticity cannot change authority class.
24. Classical fallback remains available.
25. Every profile has an exact or explicitly bounded classical-limit test.
26. Numerical tolerance is explicit and separate from byte identity.
27. Resource budgets prevent uncontrolled dense-state expansion.
28. A classical simulation is not claimed to be a physical quantum system.
29. Non-separable advisory mathematics is not claimed as physical entanglement.
30. Quantum cognition is treated only as a mathematical modeling family; no quantum-brain claim is made.
31. No quantum-advantage claim exists without controlled matched benchmarking and independent review.
32. No quantum-profile work may delay publication of the classical six-gate kernel.
33. Advisory possibility may remain probabilistic; authority must become explicit.
34. Root is a classical sovereignty and commit boundary, not a claim of physical quantum measurement.
35. The Faraday-cage description is explanatory only; conformance is defined by typed authority and effect boundaries.
36. Uncertainty may shape advice; it may never own the action.

# 16. Overall time estimate

| Stage | Focused days | Complexity | Primary knowledge |
|---|---:|---:|---|
| Q0 Preflight | 1–2 | 3/10 | release freeze and provenance |
| Quantum Gate 1 | 5–8 | 7/10 | linear algebra and numerical validation |
| Quantum Gate 2 | 8–12 | 8/10 | spectral methods, Gibbs states, contextuality |
| Quantum Gate 3 | 10–16 | 9/10 | game theory, SDP, tensor products |
| Quantum Gate 4 core | 12–20 | 9.5/10 | Lindblad and Kraus dynamics, graph walks, Replay |
| Optional physical QPU | +10–30 | 9.5/10 | circuits, QAOA, noise, hardware benchmarking |

Total without physical QPU: approximately 35–58 focused engineering days.

A provisional target with strong LLM-assisted engineering and a closed Gate-6 baseline is approximately five to eight weeks of concentrated work, provided that Q0 discovers no new constitutional primitive. This estimate must be recalibrated after Q0 and must never become a deadline that weakens numerical or authority conformance.

---

# 17. Kill rules against endless research

1. No quantum-profile work begins before Gate 6 closes and an immutable baseline is tagged.
2. No public disclosure of this roadmap occurs before Gate 6 and R-IP1 public-release approval.
3. No quantum gate may change Root, Transition Registry, Effect Firewall, ActionCommitPacket, Corridor, Receipt, or Replay law.
4. A profile without a valid classical-limit test cannot close.
5. A profile without a feasible-support proof cannot close.
6. A non-Hermitian Hamiltonian or observable is rejected.
7. Off-diagonal coupling without validated lineage cannot enter runtime.
8. A result that cannot be projected into an explainable classical report cannot enter the Root path.
9. A physical-QPU implementation that does not outperform or uniquely complement the matched classical baseline remains a demonstration only.
10. Any Q3 design requiring a SuperRoot is rejected.
11. Any DRS quantum state attempting to replace temporal hard gates is rejected.
12. Any branch allocator that widens scope, creates topology, or creates child cells is rejected.
13. Any channel that leaks support outside the feasible subspace is rejected.
14. Dense state growth beyond declared memory or dimension budgets returns to a sparse/factorized/classical fallback.
15. If one quantum gate requires rewriting more than one existing core contract family, a separate owner-reviewed RFC is required.
16. Physical-entanglement, quantum-brain, quantum-consciousness, or quantum-advantage claims are forbidden without separate scientific evidence and review.
17. Quantum work must never delay publication or maintenance of the classical six-gate kernel.
18. The workstream stops after any gate whose measured value does not justify its continuing complexity.

# 18. Allowed claims after each quantum gate

After Q1:

> Hedgehog OS includes a validated quantum-inspired advisory-state and contextual-observation ABI with an exact embedding of the frozen classical profile, explicit numerical identity rules, feasible-support preservation, and classical projection.

After Q2:

> Hedgehog OS includes a selectable quantum-inspired AVF profile whose declared classical limit reproduces the frozen classical AVF and whose contextual couplings remain Hermitian, lineage-bound, feasible-support-preserving, advisory, and explainable.

After Q3:

> Hedgehog OS includes a quantum-inspired MultiRoot advisory strategy profile with individual rationality, Pareto filtering, bounded bargaining, policy-admissible local-deviation analysis, resource limits, and independent Root decisions.

After Q4:

> Hedgehog OS includes a complete quantum-inspired advisory mathematical extension for contextual candidate state, AVF, MultiRoot GT, temporal DRS evolution, bounded Fractal exploration, backend evidence, classical fallback, authority invariance, and Replay compatibility.

Allowed architectural framing after the roadmap becomes public:

> Hedgehog OS gives probabilistic or contextual computation a bounded advisory space while keeping authority and consequential effects classical, explicit, and auditable.

> Hedgehog does not make intelligence deterministic. It makes the ownership of action deterministic.

Forbidden claims:

- Hedgehog OS is a quantum computer.
- Hedgehog OS requires a quantum computer.
- Hedgehog OS proves quantum advantage.
- A classical density-matrix simulation is a physical quantum state.
- Non-separable advisory state proves physical entanglement.
- Quantum probability proves that the brain or consciousness is quantum.
- Quantum output is truth.
- Quantum state is authority.
- Quantum mathematics makes any deployment automatically safe.
- A quantum backend replaces Root.
- The quantum profile replaces cryptography.
- QPU execution is deterministically replayed.
- Quantum terminology alone constitutes scientific novelty.

# 19. Exact repository integration instructions

## 19.0. Execution rule

The following insertions are performed only after G2-C is fully closed, audited, checkpointed, committed, and synchronized.

They form one bounded documentation-only integration. The project lead must first identify the current canonical Human Passport, Math Appendix, Machine Manifest, limitations, and release-notes paths. Do not edit stale historical versions merely because their filenames appear in an older roadmap.

Do not create `specs/quantum_math_appendix_v1_0.md` or `specs/quantum_math_invariants_v1_0.md` during this post-G2-C integration. Those normative post-Gate-6 specifications are created during the owner-approved Q1 preflight.

## 19.1. Roadmap path

Create exactly:

```text
specs/future/quantum/hedgehog_quantum_mathematical_extension_roadmap_v2_0.md
```

The file is a future engineering design, not a current normative runtime specification.

## 19.2. README pointer

Add one short future-profile section near existing roadmap or future-research links:

```markdown
## Future Mathematical Profiles

**Probabilistic intelligence. Deterministic authority.**

Hedgehog OS does not require uncertain computation to become deterministic. It gives deterministic, probabilistic, tensor, quantum-inspired, and optional QPU-backed methods a bounded advisory space while keeping authority and consequential effects classical, explicit, Root-bound, and auditable.

Future mathematical profiles may change how possibilities are represented and explored. They do not change who owns the decision or who controls the effect.

Status: future post-Gate-6 design only; not implemented; not part of current release claims; physical QPU not required; quantum advantage not claimed.

[Quantum-Inspired Mathematical Extension Roadmap v2.0](specs/future/quantum/hedgehog_quantum_mathematical_extension_roadmap_v2_0.md)
```

Do not use `published` before the first public release.

## 19.3. Current Math Appendix pointer

Add one final non-normative section:

```markdown
## Future Mathematical Extension Profiles

Hedgehog OS preserves a possibility space before it creates authority. The current classical AVF, GT, DRS, ExecutionModeRouter, and Fractal mathematics may be extended after Gate 6 by versioned probabilistic, tensor, quantum-inspired, or optional physical-QPU advisory profiles.

Possibility may remain probabilistic. Authority must become explicit.

Such a profile may change representation and evaluation of candidate space, contextual interaction, strategy correlation, advisory-memory evolution, or compute allocation. It may not change Root sovereignty, BSEP-scoped observation, HardMask, Transition Registry, ActionCommitPacket, Corridor exclusivity, Receipt non-authority, temporal hard gates, or Replay non-execution.

The classical profile remains mandatory and must appear as an exact or explicitly bounded classical limit of every promoted extension. This is an architectural-computation statement, not a claim that the current runtime contains a physical quantum state.

See: `specs/future/quantum/hedgehog_quantum_mathematical_extension_roadmap_v2_0.md`.
```

## 19.4. Human Passport constitutional invariant

Add one short invariant only:

```markdown
### Computational Substrate Neutrality

Hedgehog authority law is independent of the advisory mathematical or computational substrate. Deterministic code, classical optimization, probabilistic models, LLMs, SLMs, tensor methods, quantum-inspired mathematics, classical simulators, and optional physical-QPU backends may serve as replaceable advisory compute organs only when Root sovereignty, BSEP context boundaries, HardMask, Transition Registry, Root-created ActionCommitPacket, Corridor exclusivity, Receipt non-authority, temporal hard gates, and Replay non-execution remain unchanged.

Hedgehog does not make intelligence deterministic. It makes the ownership of action deterministic.
```

Do not copy the quantum roadmap's formulas into the current Human Passport.

## 19.5. Machine Manifest future-design entry

Add one add-only object under the current manifest's future-design/profile surface. Adapt nesting to the current schema without changing the meaning:

```json
{
  "profile_id": "quantum_mathematical_extension_v2_0",
  "document_ref": "specs/future/quantum/hedgehog_quantum_mathematical_extension_roadmap_v2_0.md",
  "status": "FUTURE_DESIGN_NOT_IMPLEMENTED",
  "private_design_commit_allowed_after": "G2C_CLOSED_PASS",
  "public_disclosure_required_gate": "GATE6_CLOSED_PASS_AND_R_IP1_RELEASE_APPROVAL",
  "implementation_baseline_required": "HEDGEHOG_GATE6_CLOSED_PASS_AND_TAGGED",
  "current_release_claim": false,
  "current_conformance_category": null,
  "physical_qpu_required": false,
  "quantum_advantage_claimed": false,
  "physical_quantum_state_claimed": false,
  "changes_root_law": false,
  "changes_bsep_law": false,
  "changes_hardmask_law": false,
  "changes_corridor_law": false,
  "changes_replay_law": false
}
```

When the roadmap becomes public, record that event through the repository's release/publication evidence surface. Do not silently rewrite the historical meaning of the private design entry.

## 19.6. Current limitations entry

Add:

```markdown
- The Quantum-Inspired Mathematical Extension is a future post-Gate-6 engineering design only. No quantum-inspired state ABI, Quantum AVF, Quantum GT, Quantum DRS, quantum Fractal allocator, simulator backend, physical-QPU adapter, physical quantum-state result, or quantum-advantage result is implemented or claimed in the current release.
```

## 19.7. Private development release-notes entry after G2-C

Add wording equivalent to:

```markdown
- Added the non-implementing future Quantum-Inspired Mathematical Extension Roadmap v2.0. This private design record changes no current runtime, gate status, conformance result, release claim, or authority law and does not authorize implementation before the tagged Gate-6 baseline.
```

Do not call this `published` while the repository remains private.

## 19.8. Public Gate-6 release entry

When Gate 6 and R-IP1 close and the owner authorizes the first public release, add a separate publication entry:

```markdown
- Publicly released the non-implementing Quantum-Inspired Mathematical Extension Roadmap v2.0 as a future engineering design and defensive-publication surface. This release changes no classical runtime, gate result, conformance result, or authority law.
```

## 19.9. Post-Gate-6 normative appendix transition

After Gate 6 closes:

- keep the roadmap at the same future path;
- change no historical roadmap claim retroactively;
- add it to the post-release next-reference-release index if such an index exists;
- start Q0 only from a tagged and hashed Gate-6 baseline;
- perform an independent scientific and constructibility review;
- create `specs/quantum_math_appendix_v1_0.md` and `specs/quantum_math_invariants_v1_0.md` during the owner-approved Q1 preflight, before Q1 runtime code is authorized;
- keep those normative specifications scoped only to the post-Gate-6 quantum workstream.

## 19.10. Post-G2-C integration nonclaims

The post-G2-C documentation commit must report:

```text
runtime_modified: false
schemas_modified: false
repository_release_spine_test_modified: true
other_tests_modified: false
runtime_tests_modified: false
demos_modified: false
current_gate_status_changed: false
quantum_implementation_started: false
physical_qpu_called: false
provider_calls: 0
network_calls: 0
real_world_effects: 0
next_engineering_slice: G2-D
```

After the documentation audit/checkpoint required by the current release discipline, return immediately to G2-D.

# 20. IP, licensing, provenance, and public-priority boundary

The private post-G2-C commit is a provenance anchor inside the owner's private repository. It does not by itself create public prior art because the public cannot access it.

When the repository and this roadmap become publicly accessible after Gate 6 and R-IP1 approval, the document is intended to:

1. publish the architecture and mathematical extension path under the repository's AGPL-3.0-only framework;
2. establish a dated public technical record of the disclosed design;
3. define Hedgehog conformance and functional-equivalence vocabulary for future profiles;
4. make later claims of independent novelty easier to compare against the earlier public specification;
5. preserve an exact distinction between the classical six-gate implementation and the future quantum-inspired design.

It does not:

1. modify AGPLv3;
2. create ownership over abstract mathematics, ideas, systems, or methods beyond applicable law;
3. guarantee that a later independent implementation is a copyright derivative;
4. guarantee that every later patent claim will be rejected;
5. prove authorship merely by containing a file hash;
6. turn a private commit into public defensive publication.

A SHA-256 digest identifies exact bytes. Git history, provenance records, public release evidence, authorship records, and the later public timestamp establish the surrounding history.

The technical strategy is not a fictional legal trap. It is a strong architecture record, conformance definition, provenance anchor, and, after public release, a defensive-publication surface.

# 21. Scientific basis and review requirements

Before implementing Q1 through Q4, independently review the relevant mathematics and explicitly map each imported formalism to a Hedgehog advisory role.

Required topics:

1. density operators, Hermitian observables, projective and generalized measurements;
2. completely positive trace-preserving channels and Kraus representations;
3. GKSL/Lindblad open-system dynamics and conditions for positivity/trace preservation;
4. contextual and quantum-probability models used as mathematical formalisms, including order effects and interference;
5. quantum game theory, correlated strategies, local strategy channels, individual rationality, and equilibrium concepts;
6. semidefinite programming, convex optimization, and numerical stability;
7. continuous-time quantum walks on validated Hermitian graph operators;
8. QAOA as an optional bounded physical-QPU experiment;
9. tensor-network, sparse, factorized, and low-rank classical representations;
10. reproducible evidence capture for stochastic simulators and physical backends.

Non-normative reference starting points include:

- V. Gorini, A. Kossakowski, and E. C. G. Sudarshan, “Completely positive dynamical semigroups of N-level systems,” *Journal of Mathematical Physics* 17, 821–825 (1976), DOI `10.1063/1.522979`.
- G. Lindblad, “On the generators of quantum dynamical semigroups,” *Communications in Mathematical Physics* 48, 119–130 (1976), DOI `10.1007/BF01608499`.
- E. Farhi and S. Gutmann, “Quantum computation and decision trees,” *Physical Review A* 58, 915 (1998), DOI `10.1103/PhysRevA.58.915`.
- E. Farhi, J. Goldstone, and S. Gutmann, “A Quantum Approximate Optimization Algorithm,” arXiv `1411.4028` (2014).
- J. Eisert, M. Wilkens, and M. Lewenstein, “Quantum games and quantum strategies,” *Physical Review Letters* 83, 3077–3080 (1999), DOI `10.1103/PhysRevLett.83.3077`.
- E. M. Pothos and J. R. Busemeyer, “Can quantum probability provide a new direction for cognitive modeling?”, *Behavioral and Brain Sciences* 36 (2013), DOI `10.1017/S0140525X12001525`.

The cognitive-modeling literature is relevant only as a mathematical source for contextual probability. It is not evidence that human cognition or Hedgehog DRS is physically quantum.

Before any research-grade Q3 or Q4 claim, obtain external review from a person working professionally in quantum information, mathematical physics, quantum algorithms, numerical linear algebra, semidefinite optimization, or a closely related field.

Such review is not required to preserve this roadmap or begin a bounded classical-simulator preflight. It is required before claiming scientific novelty, physical quantumness, entanglement, or quantum advantage.

# 22. Final architectural meaning

The v2.0 roadmap is governed by four compact statements:

> **Probabilistic intelligence. Deterministic authority.**

> **Possibility may remain probabilistic. Authority must become explicit.**

> **Uncertainty may shape advice. It may never own the action.**

> **Hedgehog does not make intelligence deterministic. It makes the ownership of action deterministic.**


The quantum-inspired profile must not quantumize the entire Hedgehog system.

The correct boundary is:

> Before Root, Hedgehog may use the richest validated space of possibilities available under policy and budget: deterministic search, classical distributions, contextual density states, coupled strategies, open-system advisory dynamics, quantum walks, tensor methods, classical simulators, or an optional physical QPU.

> At the Root boundary, every advisory result becomes a classical, explainable, locally reviewed report with exact provenance and declared numerical limits.

> After Root, only the deterministic Hedgehog constitution remains: ActionCommitPacket, lifecycle, Effect Firewall, Corridor, Receipt, evidence, and Replay.

The architecture can therefore change its mathematical and hardware compute organs without surrendering sovereignty.

The deepest invariant is not “Hedgehog uses quantum mathematics.” It is:

> **Hedgehog authority law is computational-substrate neutral.**

And the final public sentence remains:

**Hedgehog OS may expand the space of possibility into quantum geometry without allowing quantum uncertainty to own the action.**
