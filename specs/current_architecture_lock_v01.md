# Hedgehog OS Current Architecture Lock v0.1

## 1. Status and scope

This document is the current normative architecture law for the successor
worktree based on `931645dc724c54d635f32dabfca4b62fbc9a39a2`. It governs
onboarding, implementation interpretation, and authority boundaries. Exact
runtime types and behavior remain defined by accepted current contracts and
their tests, provided they conform to this lock.

This S1 lock changes documentation and onboarding authority only. It does not
change runtime behavior, schemas, Gate acceptance, or the E5 implementation
boundary.

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

## 8. Current Gate-2 / E5 continuation boundary

Gate 1 and G2-A, G2-B, G2-C, and G2-D are `CLOSED_PASS`. G2-E3 is
`IMPLEMENTED_COMMITTED_ACCEPTANCE_PASS_ON_CORRECTED_G2D`. G2-E4 selective
runtime and anti-gaming acceptance are `PASS`. Gate 2 remains `NOT_CLOSED`;
G2-E5, G2-E6, and G2-F are `NOT_STARTED_NOT_AUTHORIZED`.

The frozen E5 candidate exists only in the owner's original dirty worktree and
is intentionally absent from this clean successor. Its deferred transplant
targets are:

- `hedgehog/kernel/continuous_delta_runtime_v01.py`;
- `tests/test_continuous_delta_runtime_g2_e_v01.py`;
- `demo/run_continuous_delta_runtime_g2_e_v01.py`.

Current committed pre-E5 bytes remain the accepted baseline. No assistant may
copy, reconstruct, implement, normalize, or partially merge the candidate
without a separately authorized byte-exact transplant.

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
successor context manifest. Use
`release/successor_context_manifest_v01.json` as an allowlist; do not bulk-load
repository history, audit archives, retired donor families, or excluded
governance files.

Expand context only when the current task requires a named contract, test, or
evidence source. Validate the control plane with
`python3 tools/check_active_architecture_authority_v01.py` before handing the
worktree to a successor assistant.
