# Hedgehog OS Current Architecture Lock v0.1

## 1. Status and scope

This document is the current normative architecture law. Its architecture-law
basis remains `931645dc724c54d635f32dabfca4b62fbc9a39a2`; its current G2-E
lifecycle view is synchronized to committed implementation/control-plane basis
`6079ddcfe59f582936e7b13af2753a6533117970`. It governs onboarding,
implementation interpretation, and authority boundaries. Exact runtime types
and behavior remain defined by accepted current contracts and their tests,
provided they conform to this lock.

The G2-E Class-D synchronization changes lifecycle, evidence navigation, and
control-plane enforcement only. It does not change runtime behavior, schemas,
Root authority, the E5/E6 implementation bytes, or Gate-2 acceptance law.

## 2. Current document-authority hierarchy

Use this order:

1. `specs/current_architecture_lock_v01.md`.
2. Accepted current Kernel and Gate runtime contracts with their focused tests.
3. Accepted current Gate planning contracts, addenda, and successor checkpoints,
   limited to their named scope and current lifecycle status.
4. Current release-status and claim/evidence surfaces.
5. `AGENTS.md` as the operational view.
6. `README.md` as the public engineering view.

`specs/document_authority_index_v01.json` classifies the active control-plane
roles and all demoted historical sources. Allowlisting a technical source for
bounded context does not give it independent document authority. A document
classified as historical, reference-only, or audit-only cannot control current
implementation.

## 3. Canonical current runtime

```text
User / Event
-> local Root Intake Boundary
-> Orchestrator route proposal
-> WorldState / TemporalQuery / Local DRS retrieval
-> CandidateVectors
-> AVF / HardMask / SoftMask
-> Root-controlled route acceptance
-> BSEP creation and validation
-> side-specific BSEP projections
-> Semantic Architect proposal
-> local validation
-> runtime-owned RuntimeExecutionTopology
-> bounded actors / executors / child cells
-> ResultProposal / receipts / boundary snapshots
-> Post V&V
-> terminal GT advisory
-> independent local Root decision(s)
-> optional Root-created ActionCommitPacket
-> Effect Firewall / bounded Corridor
-> EvidenceReceipt
-> transaction ledger / crypto seal / offline replay
-> local DRS outcome writeback
```

## 4. Component authority boundaries

- Root is the sole local final and commit authority.
- Orchestrator proposes a bounded route; it is not Root and cannot accept its
  own route.
- BSEP is the canonical semantic membrane between accepted route context and
  side-specific semantic work.
- CandidateVectors and AVF masks constrain and rank possibilities; they do not
  create truth, permission, or authority.
- Semantic Architect proposes semantic structure and validation obligations;
  it does not finalize, commit, execute effects, or become Root.
- RuntimeExecutionTopology is constructed and owned locally by runtime. It is
  execution structure, not authority.
- Actors, executors, and child cells are scope-, budget-, and contract-bounded.
  Their outputs are proposals, receipts, or boundary evidence.
- Post V&V validates proposals. GT is terminal advisory input. Neither decides
  for Root.
- LLM and provider outputs are untrusted evidence or proposals until local
  validation and Root review.
- DRS, AVF, GT, receipts, ledgers, cryptographic seals, and replay never become
  Root. Integrity and replay do not prove semantic truth.

## 5. MultiRoot law

ClientRoot, AirlineRoot, and BankRoot remain independently sovereign local
Roots. There is no SuperRoot. Cross-Root objects carry bounded evidence only;
they cannot transfer authority or permission. Mixed, incomplete, rejected,
blocked, or held outcomes remain visible and cannot be collapsed into a silent
global acceptance.

## 6. Action/effect law

Consequential effects require a current, scoped, Root-created
ActionCommitPacket. The packet must remain bound to its owning Root decision,
permission, transaction, action, adapter, scope, validity interval, and
idempotency state. Scope and time-to-live may narrow after Root but may not
expand.

The Effect Firewall is the exclusive bounded effect-handle owner. A Corridor
may validate and carry only the authorized operation; it creates no permission
or authority. Receipts are evidence, not future permission or Root decisions.
No model, Orchestrator, Semantic Architect, executor, child cell, DRS record,
replay result, or cross-Root message may bypass this boundary.

## 7. Memory/time/reuse law

- Every current retrieval is governed by an explicit TemporalQuery and
  time-bounded record semantics.
- Local DRS is pointer-first and preserves provenance, lineage, policy, scope,
  validation, and lifecycle metadata. Raw secrets do not belong in DRS.
- Memory may inform, warn, explain, or propose a rerun. Memory does not carry
  forward authority, permission, finality, or proof that an action occurred.
- Hard eligibility, freshness, validity, policy, provenance, conflict, and
  quarantine checks precede ranking or reuse.
- Direct informational reuse requires a fresh local Root decision under the
  current request and scope. Action history is a fence, never reusable action
  permission.
- Superseded or invalidated artifacts remain immutable evidence. Currentness
  changes do not delete or rewrite history.
- Outcome writeback is local, Root-controlled, and non-authorizing for future
  decisions.

## 8. Current Gate-2 / G2-E closure boundary

Gate 1 and G2-A, G2-B, G2-C, and G2-D are `CLOSED_PASS`. The exact current
G2-E lifecycle is:

- G2-E3: `IMPLEMENTED_COMMITTED_ACCEPTANCE_PASS_ON_CORRECTED_G2D`;
- G2-E4: `IMPLEMENTED_COMMITTED_ACCEPTANCE_PASS`;
- G2-E5: `IMPLEMENTED_COMMITTED_ACCEPTANCE_PASS` at implementation commit
  `f582701208b603463a03d404aa841c302a8221d6`;
- G2-E6: `IMPLEMENTED_COMMITTED_ACCEPTANCE_PASS` through Class-A commit
  `7f3c7138b553096252fefee7930f89100d835fcd`, Class-B commit
  `4c133da11b8bcbd642e1aaa3413ce0a9c357731d`, and control-plane repair
  commit `6079ddcfe59f582936e7b13af2753a6533117970`;
- G2-E: `CLOSED_PASS` under
  `docs/continuous_delta_runtime_v0_1_g2_e_checkpoint_v01.md`.

The runtime phase remains `POST_E6_SUCCESSOR`: Living v1.6 has 17 acts and
appends `continuous_delta_runtime`; Kernel Conformance core and runner v0.7
have 15 categories, 60 negative probes, 16 active references, and two domains.
Profile succession is v0.5 historical to v0.6 historical to v0.7 current.
Historical `all_layers_invariant_super_smoke` remains evidence-only and is not
current or executable authority.

Each independent top-level Living or Conformance report owns one fresh public
E5 collection. Living passes that same publicly validated canonical report to
the shared Conformance builder, which collects E5 zero times. A second delta
runtime, process cache, fixture substitution, private G2-D call, or reconstructed
E5 case is forbidden. These execution receipts create no authority and no
real-world effect.

The sanitized Class-A reconciliation annex remains exact evidence of its
bounded historical hop; its statement that Class A itself did not implement
E6 remains true about that hop. It does not override the current checkpoint.

G2-F is `NEXT_NOT_STARTED_NOT_AUTHORIZED` and its implementation authorization
is false. Gate 2 remains `NOT_CLOSED`. Public release, RC2, production
readiness, and production security certification remain `NOT_CLAIMED`.

### G2-F Class-A preflight boundary

`docs/consolidated_gate2_gauntlet_g2_f_preflight_v01.md` is the current scoped
G2-F Class-A candidate contract, subordinate to this lock. It classifies G2-F
as `ORCHESTRATION_AND_ACCEPTANCE_ONLY` after a source-derived public
constructibility proof. The future programme preserves the seven existing
Gate-2 completion statements, one exact MultiRoot transaction with independent
Root decisions, eight positive/report cases, sixteen bounded DoD/hostile cases,
and 24 focused tests total. It creates no new kernel primitive, schema, Living
act, Conformance category, Root, authority, provider/model/network/connector/
adapter operation, or real-world effect.

The Class-A candidate boundary is exactly these seven paths:

1. `docs/consolidated_gate2_gauntlet_g2_f_preflight_v01.md`;
2. `specs/current_architecture_lock_v01.md`;
3. `specs/document_authority_index_v01.json`;
4. `release/successor_context_manifest_v01.json`;
5. `tools/check_active_architecture_authority_v01.py`;
6. `tests/test_active_architecture_authority_v01.py`;
7. `tests/test_repository_release_spine_v01.py`.

Only after owner review and commit of those exact Class-A bytes may a separate
owner authorization make the exact two-path implementation boundary effective:
`demo/run_consolidated_gate2_gauntlet_g2_f_v01.py` and
`tests/test_consolidated_gate2_gauntlet_g2_f_v01.py`. This Class-A hop does not
authorize or perform that implementation. The owner alone may stage, commit,
or push either boundary.

The runtime phase remains `POST_E6_SUCCESSOR`; G2-F remains
`NEXT_NOT_STARTED_NOT_AUTHORIZED`, its implementation authorization remains
false, and Gate 2 remains `NOT_CLOSED`. RC2, public release, production
readiness, production security certification, and real-world integration remain
unclaimed.

## 9. Historical-document law

Documents classified as historical or reference-only in the authority index
have no current implementation authority and are not automatic onboarding
context. They may be opened only for an explicit historical, audit, or
comparison request. Their preservation mechanism is byte history in Git; S1
does not edit, move, delete, or reinterpret their evidence.

Historical statements never override this lock, accepted current runtime
contracts, or current scoped Gate status.

## 10. Onboarding law

Onboarding starts with this lock, the authority index, `AGENTS.md`, and the
successor context manifest. For the current G2-E lifecycle, load the G2-E
checkpoint named in Section 8. Load the scoped sanitized-basis reconciliation
annex only when its Class-A/E6 geometry or historical phase law is relevant.
Use `release/successor_context_manifest_v01.json` as an allowlist; do not
bulk-load repository history, audit archives, retired donor families, or
excluded governance files. The G2-E audit remains explicit-request evidence
and is not automatic onboarding material.

Expand context only when the current task requires a named contract, test, or
evidence source. Validate the control plane with
`python3 tools/check_active_architecture_authority_v01.py` before handing the
worktree to a successor assistant.
