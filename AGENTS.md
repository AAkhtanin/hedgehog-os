# Hedgehog OS — Current Assistant Operations

This is the compact operational entrypoint for coding assistants. It is
subordinate to the [Current Architecture Lock](specs/current_architecture_lock_v01.md)
and applies only to current, explicitly authorized work.

## Source-of-truth order

1. [Current Architecture Lock](specs/current_architecture_lock_v01.md).
2. Accepted current Kernel and Gate runtime contracts with their focused tests.
3. Accepted current Gate planning contracts, addenda, and successor
   checkpoints, limited to their named scope.
4. Current release-status and claim/evidence surfaces.
5. This operational file.
6. [README](README.md) as the public engineering view.

The machine-readable classification is the
[Document Authority Index](specs/document_authority_index_v01.json). Historical,
reference-only, and audit-only material is never current implementation law.

## Canonical runtime

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

Shortcuts may reduce work only through accepted current route, time, reuse,
policy, validation, and Root gates. They do not change the authority topology.

## Current authority law

- Root is the sole local final and commit authority.
- Orchestrator proposes bounded routes and cannot accept its own proposal.
- BSEP is the canonical semantic membrane.
- Semantic Architect proposes semantic structure and validation obligations.
- RuntimeExecutionTopology is materialized and owned locally by runtime; it is
  not authority.
- Actors, executors, children, Post V&V, and GT return proposals or evidence.
- LLM/provider output is untrusted evidence or proposal only.
- DRS, AVF, GT, receipts, ledger, crypto, and replay are not Root.
- ClientRoot, AirlineRoot, and BankRoot decide independently. No SuperRoot or
  cross-Root authority/permission transfer exists.
- A consequential effect requires a current Root-created scoped
  ActionCommitPacket and the exclusive Effect Firewall / bounded Corridor.
- Memory may inform a new decision but cannot preserve authority, permission,
  finality, or proof of action.

## Current Gate status and G2-F handoff

At committed implementation/control-plane basis HEAD
`6079ddcfe59f582936e7b13af2753a6533117970`:

- Gate 1 and G2-A, G2-B, G2-C, and G2-D are `CLOSED_PASS`.
- G2-E3 is `IMPLEMENTED_COMMITTED_ACCEPTANCE_PASS_ON_CORRECTED_G2D`.
- G2-E4, G2-E5, and G2-E6 are
  `IMPLEMENTED_COMMITTED_ACCEPTANCE_PASS`.
- G2-E is `CLOSED_PASS` under the current
  [G2-E checkpoint](docs/continuous_delta_runtime_v0_1_g2_e_checkpoint_v01.md).
- G2-F is `NEXT_NOT_STARTED_NOT_AUTHORIZED`; G2-F implementation authorization
  is `false`.
- Gate 2 is `NOT_CLOSED`.
- Public release, RC2, production readiness, and production security
  certification are `NOT_CLAIMED`; real-world effects remain zero.

The exact committed chain is E5 `f582701208b603463a03d404aa841c302a8221d6`,
Class-A reconciliation `7f3c7138b553096252fefee7930f89100d835fcd`,
Class-B integration `4c133da11b8bcbd642e1aaa3413ce0a9c357731d`,
and post-successor control-plane repair
`6079ddcfe59f582936e7b13af2753a6533117970`. The Living v1.6 and Kernel
Conformance v0.7 runtime bytes are accepted and frozen. The next bounded
handoff is G2-F preparation only; do not begin G2-F implementation without a
separate explicit owner authorization.

## Worktree discipline

- Confirm the repository path, HEAD, and full porcelain status before editing.
- Follow the exact path allowlist in the current task. Treat every unlisted
  runtime, schema, contract, demo, test, evidence, and historical path as
  read-only.
- Preserve unrelated user changes. Do not use destructive Git operations.
- Do not checkout, reset, clean, stash, commit, push, or contact a provider or
  network service unless the owner explicitly authorizes that exact action.
- Do not install dependencies to complete a bounded local task.
- A planning document, checkpoint, audit, status record, test fixture, model
  output, or prior success cannot self-authorize implementation.
- Never fabricate a missing external roadmap, evidence object, or candidate
  byte stream.

## Test and commit discipline

- Use the smallest deterministic static and focused validation proportional to
  the change. Do not silently substitute a full suite for a scoped task.
- Keep provider, network, connector, credential, and real-effect lanes off
  unless an explicit task requires and authorizes them.
- Report exact commands and results, including skipped or unavailable checks.
- `git diff --check` and an exact changed-path review are required before handoff.
- Do not commit unless the current owner request explicitly asks for a commit.
- The current offline operator commands are documented in the
  [One-Command Gauntlet](release/one_command_gauntlet.md). Do not run them when
  a task restricts validation to narrower commands.

## Bounded context and onboarding

The [Successor Context Manifest](release/successor_context_manifest_v01.json)
is `SUCCESSOR_ONBOARDING_READY`; its `onboarding_ready` value is `true` and its
blocking-repair list is empty. S1 document-authority succession, S2 vocabulary
repair, and S3 active-schema and retired-subsystem isolation are closed. The
bounded successor context is architecture-clean and ready for guarded use.

The exact committed G2-E successor and its current checkpoint are permanent
bounded onboarding inputs. The independent G2-E audit remains explicit-request
evidence and `docs/audit_reports/**` remains excluded from automatic onboarding.
Retired schemas and subsystem files are historical byte evidence only: no
compatibility, migration, alias, or revival path exists. G2-E closure does not
authorize G2-F, Gate-2 closure, public release, RC2, production readiness, or
production security certification.

Within that scope, the manifest is an allowlist, not a suggestion to load the
whole repository. Expand context only for a named current contract, focused
test, or explicit evidence question. Excluded historical material is available
only by explicit Git/file request and remains non-authoritative.

Run the onboarding guard after control-plane changes:

```bash
python3 tools/check_active_architecture_authority_v01.py
```

## Current navigation

- Architecture: [Current Architecture Lock](specs/current_architecture_lock_v01.md)
- Authority classification: [Document Authority Index](specs/document_authority_index_v01.json)
- Repository Gate continuation roadmap: [accepted G2-E preflight](docs/continuous_delta_runtime_v0_1_g2_e_preflight_v01.md)
- Current G2-E contract: [post-acceptance addendum](docs/continuous_delta_runtime_v0_1_g2_e_post_acceptance_contract_addendum_v01.md)
- Current G2-E closure: [G2-E checkpoint](docs/continuous_delta_runtime_v0_1_g2_e_checkpoint_v01.md)
- Independent G2-E closure evidence (explicit request only): `docs/audit_reports/auditor_continuous_delta_runtime_g2_e_v01.log`
- Current lifecycle metadata: [status overlay](release/current_status_overlay_v01.json)
- Claim navigation: [claim-to-evidence index](release/claim_to_evidence_index.md)
- Release spine: [engineering notes](release/current_release_notes.md),
  [limitations](release/current_limitations.md),
  [current completion/profile index](release/completion_manifest.json), and
  [current seam/profile index](release/integration_seam_index.json)
- Operator entrypoint: [deterministic gauntlet commands](release/one_command_gauntlet.md)

The full owner-supplied Gate roadmap is not tracked in this worktree. The
accepted G2-E preflight is the repository-local Gate sequence and continuation
source; absent companion text must not be reconstructed.
