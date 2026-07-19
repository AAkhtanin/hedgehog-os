# Hedgehog OS Two-Domain All-Real Sealed Evidence Program v0.1
## Consolidated Preflight

document_id: two_domain_all_real_sealed_evidence_program_v01_preflight

document_status: PREFLIGHT

preflight_status: READY_FOR_REVIEW

programme_id: two_domain_all_real_sealed_evidence_program_v01

programme_version: v0.1

observed_base_head: 339c4ad

gate1_checkpoint_commit: 339c4ad

gate1_kernel_implementation_commit: d188e2a

gate1_independent_audit_commit: 3dd9e89

planning_only: true

runtime_modified: false

tests_modified: false

schemas_modified: false

release_indexes_modified: false

provider_called: false

network_called: false

gemini_called: false

tmp_accessed: false

package_created: false

anchor_created: false

replay_performed: false

audit_created: false

presentation_created: false

real_world_effects_count: 0

provider_execution_strategy: OPTION_A_ONE_FRESH_COLLECTION_PER_DOMAIN

sealed_evidence_architecture: OPTION_B_THIN_SHARED_PROFILE_WITH_DOMAIN_ADAPTERS

airline_live_collection_count: 1

airline_provider_call_budget: 12

supplier_live_collection_count: 1

supplier_provider_call_budget: 6

programme_provider_call_budget: 18

automatic_live_retry_allowed: false

failed_attempt_preserved: true

gate1_kernel_modification_required: false

airline_gate1_adapter_modification_required: false

supplier_gate1_adapter_modification_required: false

next_gate: two_domain_all_real_sealed_evidence_program_v01_r1_shared_profile

## 1. Executive Verdict

- Gate 1 is `CLOSED_PASS` at `339c4ad`.
- This post-Gate-1 programme is authorized only as a reviewed future
  programme. This preflight performs no runtime implementation.
- Two fresh live collections are planned: one Airline collection with twelve
  calls and one Supplier / Water Filter collection with six calls.
- The total programme provider, network, and Gemini call budget is eighteen.
- Automatic live retry is forbidden.
- Both domains use the same closed Kernel laws, while each domain receives a
  separate package, Anchor, Replay, and audit.
- Public presentation occurs only after both domains independently close.
- Real payment, booking, ticket issuance, shipment release, and external
  connector actions remain forbidden.

## 2. Closed Gate-1 Basis

The programme starts from the committed Domain-Neutral Reference Kernel RC1
checkpoint, not from an open Gate-1 implementation branch.

- Gate-1 checkpoint commit: `339c4ad`.
- Kernel implementation commit: `d188e2a`.
- Independent audit commit: `3dd9e89`.
- Kernel Conformance: `10 categories / 2 domains / 10 negative checks`, all
  `PASS`.
- Living Gauntlet v1.0: `13 active / 1 evidence-only / 0 planned`, all active
  acts `PASS`.
- Seam geometry: `24 total / 21 active / 3 reference-only / 0 planned`.
- Airline domain conformance: `PASS`.
- Supplier / Water Filter conformance: `PASS`.
- Supplier MultiRoot: `MIXED`.
- Root authority: preserved.
- Provider, network, Gemini, and real-world-effect counts during Gate-1 closure:
  `0 / 0 / 0 / 0`.

The audited runtime indexes intentionally remain `ACTIVE_GATE1_G1E`. They are
the frozen terminal runtime snapshot. The project checkpoint separately records
the Gate-1 engineering programme as `CLOSED_PASS`.

## 3. Programme Thesis

The programme must prove that two structurally different domains can produce
fresh live semantic evidence, preserve independent Root authority and honest
business outcomes, project into the same closed Kernel laws, and use one common
sealed-evidence method without copying domain law into Kernel.

Airline is the known three-Root control domain. Supplier / Water Filter is the
one-Root portability domain with an intentionally `MIXED` business result. A
technical `PASS` means that the declared evidence and safety contracts pass. It
does not mean every business subject is approved or that the external world
changed.

## 4. Canonical Option Terminology

### PROVIDER OPTION A

`PROVIDER OPTION A` means:

- one fresh Airline provider collection;
- one fresh Supplier provider collection;
- deterministic branching after each safe collection;
- no separate provider call for every negative mutation.

The rejected multiple-collection provider strategy would use separate fresh
provider collections for variations. It remains rejected unless a later
independently reviewed source contradiction proves it necessary.

### SEALED ARCHITECTURE OPTION B

`SEALED ARCHITECTURE OPTION B` means:

- one thin common sealed-evidence profile;
- existing generic Integrity and Replay reused unchanged;
- a separate Airline source/package adapter;
- a separate Supplier source/package adapter;
- filesystem integration owned by runners;
- no Airline law copied into Kernel.

Every strategy reference must use either `PROVIDER OPTION A` or
`SEALED ARCHITECTURE OPTION B`.

## 5. Programme Scope

The future programme scope is exactly:

1. one fresh Airline all-real semantic collection;
2. one fresh Supplier / Water Filter all-real semantic collection;
3. all nine Supplier scenarios defined in this preflight;
4. separate Airline and Supplier safe packages;
5. separate committed Anchors and anchored verifications;
6. separate sealed Replays, independent audits, and Human Stories;
7. one cross-domain comparison and independent audit;
8. one public Evidence Book and Showcase package.

The programme may create new shared evidence contracts, new domain evidence
adapters, new owner-terminal wrappers, new focused tests, and new safe evidence
documents only through the gate sequence defined below.

## 6. Programme Non-Scope

The programme does not authorize:

- modification of a Gate-1 Kernel contract;
- modification of either accepted Gate-1 domain adapter;
- production connectors or production persistence;
- real airline, bank, GDS, supplier, or warehouse operations;
- real booking, ticket issuance, payment, settlement, or shipment release;
- provider calls from pytest, packaging, Replay, audit, or presentation;
- production PKI, Root Attestation, or production MultiRoot federation;
- raw live material in the repository or public Evidence Book;
- automatic retries or package discovery;
- repair or promotion of a failed live attempt in place.

## 7. Frozen Kernel and Domain Surfaces

The following accepted surfaces are frozen inputs:

- `hedgehog/kernel/integrity_replay_v01.py`;
- `hedgehog/kernel/abi_v01.py`;
- `hedgehog/kernel/root_signer_isolation_v01.py`;
- `hedgehog/kernel/multiroot_v01.py`;
- `hedgehog/kernel/effect_firewall_v01.py`;
- `hedgehog/kernel/conformance_v01.py`;
- `hedgehog/domains/airline/kernel_adapter_v01.py`;
- `hedgehog/domains/supplier_water_filter/kernel_adapter_v01.py`;
- `release/completion_manifest.json`;
- `release/integration_seam_index.json`.

R0 freezes these conclusions:

- `gate1_kernel_modification_required: false`;
- `airline_gate1_adapter_modification_required: false`;
- `supplier_gate1_adapter_modification_required: false`.

No future gate may modify a frozen surface unless a new read-only review
identifies a concrete contradiction, an owner approves a replacement
preflight, and the contradiction is independently reviewed before editing.

## 8. Live Provider Execution Budget

### Airline

- Fresh collection count: `1`.
- Semantic actor count: `12`.
- Provider-call budget: `12`.
- Network-call budget: `12`.
- Gemini-call budget: `12`.
- Automatic retry: `false`.

### Supplier / Water Filter

- Fresh collection count: `1`.
- Semantic actor count: `6`.
- Provider-call budget: `6`.
- Network-call budget: `6`.
- Gemini-call budget: `6`.
- Actor geometry: one Orchestrator, one Semantic Architect, and four branch
  semantic actors.
- Automatic retry: `false`.

### Programme

- Total fresh live collections: `2`.
- Total provider-call budget: `18`.
- Total network-call budget: `18`.
- Total Gemini-call budget: `18`.
- Provider calls inside pytest: forbidden.
- Provider calls inside deterministic packaging, Replay, audit, or
  presentation: forbidden.

Supplier variations require no additional provider collection because Root
decisions over validated evidence, corrected-fact validation, scoped human
approval, packet mutations, corridor mutations, receipt mutations, MultiRoot
projection, and Replay are deterministic operations. Replay reconstructs
evidence; it does not ask a provider to reason again.

## 9. Attempt Identity and Failure Preservation

Every live attempt must receive immutable identity before execution:

- `programme_id`;
- `domain_id`;
- `execution_head`;
- `attempt_number`;
- `run_id`;
- `report_id`;
- `source_task_id`;
- `package_id`;
- `logical_package_ref`;
- `output_directory`;
- `provider_mode`;
- `model_id`;
- `expected_actor_count`;
- `provider_call_budget`.

The first attempt is `attempt_01`. Identity uses the programme ID, domain ID,
validated execution HEAD, and attempt number. An output directory must be an
explicit owner-supplied absent path. No latest-directory selection or package
discovery is allowed.

If an attempt fails, the programme must preserve it, never repair or overwrite
it, never promote it, record a stable sanitized failure reason, and stop.
Owner review is required before `attempt_02`, which receives a new run ID,
package ID, logical package ref, and output path. No automatic retry is allowed.

## 10. Evidence Classes and Publication Policy

| Evidence class | Repository | Public book | Secret scan | Raw prompt | Raw provider response | Cryptographic binding | Retention | Deletion and publication rule |
|---|---|---|---|---|---|---|---|---|
| `LIVE_PROVIDER_RAW_PRIVATE` | Forbidden | Forbidden | Required | Private store only | Private store only | Required for retained private inventory | Owner-controlled private retention | Never committed or published; deletion only under owner retention policy after evidence obligations close |
| `LIVE_PROVIDER_SAFE_PROJECTION` | Allowed after validation | Allowed | Required | Forbidden | Forbidden | Canonical hash required | Retain with accepted package | Delete only superseded working copies; publish only validated projections |
| `EXECUTED_LIVE_RUNTIME` | Safe summary allowed | Allowed | Required | Forbidden | Forbidden | Package binding required | Permanent accepted evidence | Failed and accepted attempts remain distinct; publish safe counters and states only |
| `EXECUTED_DETERMINISTIC_RUNTIME` | Allowed | Allowed | Required before packaging | Forbidden | Forbidden | Package binding required | Permanent accepted evidence | Publish exact deterministic identity and limitations |
| `ROOT_DECISION_EVIDENCE` | Allowed | Allowed | Required before packaging | Forbidden | Forbidden | Required | Permanent | Never publish secrets or rewrite a decision outcome |
| `CORRIDOR_EVIDENCE` | Allowed | Allowed | Required before packaging | Forbidden | Forbidden | Required | Permanent | Publish mock-only scope and zero-effect boundary |
| `NEGATIVE_CONFORMANCE` | Allowed | Allowed | Required before packaging | Forbidden | Forbidden | Required | Permanent | Preserve stable blocked reason and attack identity |
| `CRYPTOGRAPHIC_INTEGRITY` | Allowed | Allowed | Required for source inventory | Forbidden | Forbidden | Intrinsic | Permanent | Never claim truth, signer identity, or authority from a hash alone |
| `EXTERNAL_ANCHOR` | Allowed | Allowed | Required for source metadata | Forbidden | Forbidden | Intrinsic and source-bound | Permanent | Publish only after package freeze and independent recomputation |
| `REPLAY_EVIDENCE` | Allowed | Allowed | Required before publication | Forbidden | Forbidden | Anchor required for anchored PASS | Permanent | Replay cannot create authority, permission, action, or effect |
| `INDEPENDENT_AUDIT` | Allowed | Allowed | Required for referenced material | Forbidden | Forbidden | Audit file hash required | Permanent | Audit is append-only evidence and cannot rewrite source evidence |
| `HISTORICAL_REFERENCE` | Existing committed references only | Allowed when clearly historical | Previously established | Forbidden | Forbidden | Preserve existing bindings | Permanent | Freeze; do not reclassify as a fresh execution |
| `PUBLIC_SHOWCASE` | Allowed | Allowed | Required on all source inputs | Forbidden | Forbidden | Claim-evidence bindings required | Permanent release artifact | Generate only after both domains and cross-domain audit close |

## 11. Private Raw Evidence Boundary

Raw live evidence is outside the public repository boundary.

- Raw prompts and provider responses may exist only in explicit
  owner-controlled private storage.
- Raw private files are not members of the public safe package.
- Private directories are supplied explicitly; there is no directory
  discovery.
- The private inventory receives hashes and a secret scan without copying raw
  bodies into committed summaries.
- Safe projections must be schema-validated, canonicalized, secret-scanned,
  and cryptographically bound before repository publication.
- Audits, Human Stories, matrices, slides, and appendices may reference safe
  identities and counters only.
- Credentials, environment dumps, private keys, absolute owner paths, object
  representations, memory addresses, and tracebacks are forbidden in public
  evidence.

## 12. Common Sealed-Evidence Architecture

`SEALED ARCHITECTURE OPTION B` is frozen.

The shared package location is `hedgehog/evidence/`, outside
`hedgehog/kernel/`. The shared profile is domain-neutral, deterministic, and
built over the accepted Kernel ABI, Integrity, Replay, signer-isolation,
MultiRoot, Effect Firewall, and Kernel Conformance laws.

The future shared contract paths are:

- `hedgehog/evidence/__init__.py`;
- `hedgehog/evidence/sealed_evidence_profile_v01.py`;
- `hedgehog/evidence/sealed_package_v01.py`;
- `hedgehog/evidence/external_anchor_v01.py`;
- `hedgehog/evidence/sealed_replay_evidence_v01.py`.

They must contain no provider, network, Gemini, filesystem, domain business
constant, production PKI, Root Attestation, authority creation, permission
creation, or real-effect operation. Filesystem integration belongs to demo
runners.

## 13. Common Contract Responsibilities

The shared evidence contracts are responsible only for:

- programme, domain execution, and attempt identity;
- safe source and file inventories;
- artifact inventory and deterministic order;
- canonical package identity and package validation;
- generic Manifest binding;
- Anchor publication binding;
- anchored verification evidence;
- Replay evidence projection;
- audit evidence references;
- public evidence-index geometry;
- zero provider/network/Gemini/effect counters during non-live phases.

They do not select Airline offers, define Airline Corridor law, decide
Supplier readiness, grant Supplier approval, widen payment scope, release a
shipment, or become Root authority.

## 14. Domain Adapter Responsibilities

The planned adapters are:

- `hedgehog/domains/airline/sealed_evidence_package_adapter_v01.py`;
- `hedgehog/domains/supplier_water_filter/live_evidence_adapter_v01.py`;
- `hedgehog/domains/supplier_water_filter/sealed_evidence_package_adapter_v01.py`.

The Airline adapter binds the canonical PAR-LIM live report, BSEP, three-Root
transaction, Corridor, receipts, 19-entry Ledger, Kernel projection, and
Airline Crypto evidence to the common profile.

The Supplier live-evidence adapter binds one safe six-actor live projection to
the deterministic scenario programme without pretending that deterministic
policy mutations are new provider observations. The Supplier package adapter
binds all nine scenarios, the accepted Gate-1 deterministic adapter output,
Kernel artifacts, causal refs, MultiRoot `MIXED`, and package inventory.

Neither adapter may import provider clients or perform filesystem work.

## 15. Airline Fresh Run Chain

The Airline target chain is frozen as:

`human task -> 12 live semantic actors -> BSEP -> canonical semantic selection
-> Client Root -> Airline Root -> Bank Root -> Ticket / Purchase Corridor ->
mock receipts -> 19-entry Ledger -> 29 dependency edges -> 3 Root finals ->
Airline Kernel projection -> generic Integrity -> generic Replay -> Crypto
Manifest -> new safe package -> new committed Anchor -> fresh anchored
verification -> sealed Replay -> independent audit -> Human Story ->
cross-domain Evidence Book`.

The run must retain the canonical PAR-LIM task geometry unless a separate
future preflight authorizes a new Airline adapter version. It receives one new
live collection and exactly twelve calls. Historical package and Anchor
identities remain frozen and must not be reused or overwritten. Real airline,
bank, GDS, booking, payment, and ticket operations remain zero.

## 16. Supplier Fresh Run Chain

The Supplier target chain is frozen as:

`business task -> six live semantic actors -> BSEP -> DRS context -> AVF
ranking and hard masks -> Semantic Architect -> branch evidence -> first Root
NOT_READY -> corrected evidence -> validation rerun -> Supplier A scoped
review-ready -> Supplier B BLOCKED -> shipment HELD -> explicit human approval
for Supplier A only -> Root-created ActionCommitPacket -> MockBankSandbox ->
mock payment intent -> mock consent -> mock payment order -> mock receipt
evidence -> terminal receipt observation -> complete negative mutation matrix
-> Supplier Kernel artifacts -> causal refs -> generic Integrity -> generic
Replay -> new Supplier package -> committed Supplier Anchor -> fresh anchored
verification -> Supplier sealed Replay -> independent audit -> Human Story ->
cross-domain Evidence Book`.

The chain uses one fresh six-call collection. Deterministic variations add no
provider call. Real bank, supplier, warehouse, payment, shipment, and
real-world-effect counts remain zero.

## 17. Supplier Scenario Matrix

All nine rows are mandatory. Provider counts are additional calls attributable
to that row; all live rows bind to the single six-call collection.

| ID and canonical name | Source/class | Calls | Root | Packet / corridor / receipt | Supplier A / Supplier B / shipment | Technical / business | Effects | Package / audit / presentation |
|---|---|---:|---|---|---|---|---:|---|
| `S-N1 initial_business_blockers_root_not_ready` | Initial validated business evidence; deterministic | 0 | `NOT_READY` | absent / not entered / absent | blocked pending correction / `BLOCKED` / `HELD` | `PASS` safety proof / `NOT_READY` | 0 | required / required / required |
| `S-N2 unsafe_live_evidence_fail_closed` | Safe projection of rejected live evidence; live-bound negative | 0 additional | no accepted new Root Final | absent / not entered / absent | unchanged / `BLOCKED` / `HELD` | `FAIL_CLOSED` / unchanged | 0 | required / required / required |
| `S-C1 corrected_evidence_validation_rerun` | Corrected evidence and DRS context; deterministic | 0 | changed facts rerun; scoped review-ready | absent / not entered / absent | scoped review-ready / `BLOCKED` / `HELD` | `PASS` / `MIXED` | 0 | required / required / required |
| `S-P1 supplier_a_scoped_human_approval` | Explicit owner input; deterministic | 0 | Root reviews exact scope | Root-created scoped packet / not yet entered / absent | approved scope only / `BLOCKED` / `HELD` | `PASS` / `MIXED` | 0 | required / required / required |
| `S-P2 supplier_a_mock_bank_happy_path` | Live-bound integrated runtime plus deterministic corridor | 0 additional | Root packet remains source | valid / mock PASS / validated evidence-only terminal receipt | mock path PASS / `BLOCKED` / `HELD` | `PASS` / `MIXED` | 0 | required / required / required |
| `S-F1 no_human_approval_blocks_action` | Direct policy probe; deterministic | 0 | no action approval | no accepted packet / not entered / absent | not executed / `BLOCKED` / `HELD` | `FAIL_CLOSED` / unchanged | 0 | required / required / required |
| `S-F2 packet_and_corridor_mutation_matrix` | Direct packet/corridor validators; deterministic | 0 | no widened Root decision | rejected / rejected / absent | unchanged / `BLOCKED` / `HELD` | `FAIL_CLOSED` / unchanged | 0 | required / required / required |
| `S-F3 receipt_attack_matrix` | Direct receipt/registry validators; deterministic | 0 | no new permission | source packet unchanged / no new execution / attack rejected | unchanged / `BLOCKED` / `HELD` | `FAIL_CLOSED` / unchanged | 0 | required / required / required |
| `S-M1 integrated_mixed_business_outcome` | Supplier Kernel adapter and MultiRoot projection; deterministic | 0 | one `HELD` Root decision | valid scoped packet / mock PASS / `EVIDENCE_ONLY` | scoped mock PASS / `BLOCKED` / `HELD` | conformance `PASS` / `MIXED` | 0 | required / required / required |

Every row is included in the Supplier safe evidence index, package Manifest,
sealed Replay, independent audit, Human Story, cross-domain claim-evidence
matrix, and final presentation.

## 18. Supplier Negative and NOT_READY Paths

`S-N1` must show the initial shortage, missing or expired legal/insurance
evidence, Supplier B invoice mismatch or delay, payment-slot-is-not-permission
boundary, Root `NOT_READY`, and no payment or shipment release.

`S-N2` must show that malformed, unsafe, overclaiming, or otherwise invalid
live evidence fails closed. Provider output is not truth, authority,
permission, or FinalOutput. It cannot enter the action corridor.

`S-F1`, `S-F2`, and `S-F3` must directly execute public deterministic
validators. No negative result may be inferred from presentation wording or a
stored synthetic label.

## 19. Supplier Corrected-Evidence Path

`S-C1` must prove:

- corrected evidence is evidence/context only;
- the prior Root Final is not mutated;
- changed facts trigger a new deterministic validation pass;
- Supplier A becomes scoped review-ready only;
- Supplier B remains `BLOCKED`;
- shipment remains `HELD`;
- payment has not executed;
- no provider is called for the rerun.

## 20. Supplier Scoped Human-Approval Path

`S-P1` requires explicit human approval whose scope is Supplier A only. Root
must check amount, beneficiary, bank policy, payment slot, adapter, forbidden
subjects, forbidden actions, and expiry before creating the packet.

The human, LLM, DRS, AVF, GT/LGT, Architect, Executor, and fractal children do
not create the ActionCommitPacket. Supplier B and shipment release are absent
from allowed scope and present in the required forbidden surface.

## 21. Supplier Mock-Payment Happy Path

The only permitted term is **scoped Supplier A mock-payment happy path**.

The path is:

`validated Root-created packet -> mock payment intent -> mock consent -> mock
payment order -> validated mock receipt -> terminal receipt observation`.

The happy path ends at the validated mock receipt plus terminal receipt
observation. It does not mean complete Supplier success, all suppliers
approved, payment settled, shipment fulfilled, real settlement, a real bank
call, Supplier B approval, shipment release, or production fulfillment.

## 22. Supplier Integrated MIXED Outcome

The final combined outcome is fixed as:

- technical conformance: `PASS`;
- Supplier A: scoped mock-payment path `PASS`;
- Supplier B: `BLOCKED`;
- shipment: `HELD`;
- receipt: `EVIDENCE_ONLY`;
- real payment: `false`;
- real shipment release: `false`;
- business outcome: `MIXED`.

No report, package, Replay, audit, matrix, Human Story, or slide may rewrite
`MIXED` into an all-accepted `PASS`.

## 23. R0 Consolidated Preflight Gate

- Gate ID: `two_domain_all_real_sealed_evidence_program_v01_r0_preflight`.
- Purpose: freeze architecture, budget, identities, scenarios, gates, safety,
  and evidence policy.
- Paths created: this preflight.
- Paths modified: `AGENTS.md` active checkpoint block only.
- Frozen inputs: Gate-1 checkpoint, audit, Kernel modules, both Gate-1
  adapters, and runtime release indexes.
- Allowed operations: static reads, Markdown creation, bounded static
  validation.
- Forbidden operations: runtime/test/schema implementation, pytest, project
  runners, providers, network, Gemini, package, Anchor, Replay, audit, or
  presentation.
- Provider/network/Gemini/effect counts: `0 / 0 / 0 / 0`.
- Expected duration: under twenty minutes.
- Retry policy: not applicable; correct only after review if the preflight is
  rejected.
- Package freeze point: none; no package exists.
- Audit requirement: owner review before commit.
- Commit boundary: one reviewed R0 preflight commit.
- Fail-closed condition: any guard, scope, frozen-hash, or static-validation
  mismatch.
- Next gate: `two_domain_all_real_sealed_evidence_program_v01_r1_shared_profile`.

## 24. R1 Shared Sealed-Evidence Profile Gate

- Gate ID: `two_domain_all_real_sealed_evidence_program_v01_r1_shared_profile`.
- Purpose: implement pure shared contracts and domain package adapters without
  changing Kernel or accepted adapters.
- CREATE paths: the five `hedgehog/evidence/` paths in Section 12; the three
  domain adapters in Section 14; `demo/run_sealed_evidence_package_v01.py`;
  `demo/run_sealed_evidence_anchor_v01.py`;
  `demo/run_sealed_evidence_replay_v01.py`;
  `tests/test_sealed_evidence_profile_v01.py`;
  `tests/test_airline_sealed_evidence_package_adapter_v01.py`;
  `tests/test_supplier_water_filter_live_evidence_adapter_v01.py`;
  `tests/test_supplier_water_filter_sealed_evidence_package_adapter_v01.py`;
  `tests/test_sealed_evidence_package_v01_runner.py`;
  `tests/test_sealed_evidence_anchor_v01_runner.py`; and
  `tests/test_sealed_evidence_replay_v01_runner.py`; and
  `docs/two_domain_all_real_sealed_evidence_program_v01_r1_checkpoint.md`.
- MODIFY paths: `AGENTS.md` active checkpoint block only.
- Frozen inputs: all Section 7 paths and existing Airline/Supplier runtime
  collectors.
- Outputs: immutable shared contracts, exact domain adapters, deterministic
  filesystem runners, focused tests, and the exact R1 checkpoint path listed
  above.
- Allowed operations: pure implementation, focused pytest, static checks, and
  deterministic standalone fixtures.
- Forbidden operations: live providers, package publication, Anchor
  publication, real effects, and Kernel edits.
- Focused tests: only the new R1 test files.
- Short compatibility: `tests/test_kernel_integrity_replay_v01.py` and
  `tests/test_kernel_abi_v01.py` as an owner-approved bounded command.
- Standalone runner: `demo.run_sealed_evidence_package_v01` in fixture mode.
- Owner-terminal command: deterministic fixture mode only; no live command.
- Provider/network/Gemini/effect counts: `0 / 0 / 0 / 0`.
- Expected duration: under one minute for focused validation.
- Retry policy: deterministic correction after review; never automatic.
- Package freeze point: no official package; fixture output is disposable.
- Audit requirement: independent R1 contract audit/checkpoint.
- Commit boundary: separate implementation and audit/checkpoint commits.
- Fail-closed condition: any nondeterminism, unsafe path, unknown inventory,
  mutable identity, hash mismatch, or domain law in shared contracts.
- Next gate: `two_domain_all_real_sealed_evidence_program_v01_a1_airline_live`.

## 25. A1 Fresh Airline Live Execution Gate

- Gate ID: `two_domain_all_real_sealed_evidence_program_v01_a1_airline_live`.
- Purpose: execute one fresh canonical Airline all-real collection as the
  control domain.
- CREATE paths: `demo/run_two_domain_airline_all_real_program_v01.py`;
  `tests/test_two_domain_airline_all_real_program_v01_runner.py`;
  `docs/evidence/two_domain_all_real_sealed_evidence_program_v01/airline/airline_safe_execution_report_v01.json`;
  and `docs/audit_reports/auditor_two_domain_airline_all_real_generation_v01.log`.
- MODIFY paths: `AGENTS.md` active checkpoint block only.
- Frozen inputs: R1 contracts, canonical Airline live runner, Corridor,
  Ledger, Crypto, and Gate-1 Airline adapter.
- Outputs: immutable `attempt_01` raw-private inventory, safe projection,
  generation gate, and accepted safe execution report.
- Allowed operations: exactly one owner-terminal real-provider collection,
  explicit private output path, secret scan, safe projection, and generation
  validation.
- Forbidden operations: pytest live calls, retries, package discovery, Anchor,
  Replay, real actions, and in-place repair.
- Focused test: `tests/test_two_domain_airline_all_real_program_v01_runner.py`
  with injected provider only.
- Short compatibility: selected canonical Airline collector and adapter tests,
  excluding real-provider cases.
- Standalone runner: `demo.run_two_domain_airline_all_real_program_v01` in
  injected deterministic mode.
- Owner-terminal command: `PYTHONPATH=. .venv/bin/python -m
  demo.run_two_domain_airline_all_real_program_v01 --real-provider
  --attempt-number 1 --private-output-directory <owner-supplied-absent-path>`.
- Provider/network/Gemini/effect counts: `12 / 12 / 12 / 0` maximum and exact
  on accepted completion.
- Expected duration: at most twenty minutes.
- Retry policy: no automatic retry; failed attempt preserved; owner review
  before a newly identified attempt.
- Package freeze point: raw attempt freezes on exit; safe execution evidence
  freezes after validation and secret scan. The official sealed package is A2.
- Audit requirement: independent generation audit before A2.
- Commit boundary: accepted safe execution evidence and generation audit in a
  reviewed commit; failed evidence is never promoted as PASS.
- Fail-closed condition: any actor failure, wrong count/order, unsafe output,
  secret finding, Root-law failure, Corridor/Ledger/Crypto failure, or effect.
- Next gate: `two_domain_all_real_sealed_evidence_program_v01_a2_airline_seal`.

## 26. A2 Airline Seal, Anchor, Replay, Audit, and Story Gate

- Gate ID: `two_domain_all_real_sealed_evidence_program_v01_a2_airline_seal`.
- Purpose: seal and independently close the accepted A1 evidence.
- CREATE paths under the Airline evidence directory:
  `airline_safe_package_index_v01.json`, `airline_crypto_anchor_v01.json`,
  `airline_replay_report_v01.json`, and `airline_human_story_v01.md`; plus
  `docs/audit_reports/auditor_two_domain_airline_anchor_publication_v01.log`
  and `docs/audit_reports/auditor_two_domain_airline_anchored_replay_v01.log`.
- MODIFY paths: `AGENTS.md` active checkpoint block only.
- Frozen inputs: accepted A1 attempt, R1 contracts, and all historical Airline
  evidence.
- Outputs: one new safe package identity, committed Anchor, anchored
  verification, sealed Replay, audits, and Human Story.
- Allowed operations: package creation from safe projections, independent
  inventory recomputation, Anchor publication, read-only Replay, and static
  story generation.
- Forbidden operations: provider/network/Gemini calls, package mutation after
  freeze, historical identity reuse, real actions, and raw publication.
- Focused tests: R1 package/Anchor/Replay tests plus A2 binding tests in
  `tests/test_two_domain_airline_all_real_program_v01_runner.py`.
- Short compatibility: selected existing Airline Crypto and sealed-Replay
  focused tests.
- Standalone runners: `demo.run_sealed_evidence_package_v01`,
  `demo.run_sealed_evidence_anchor_v01`, and
  `demo.run_sealed_evidence_replay_v01` with `--domain airline`.
- Owner-terminal command: three explicit commands in package, Anchor, Replay
  order using exact input/output paths.
- Provider/network/Gemini/effect counts: `0 / 0 / 0 / 0`.
- Expected duration: at most five minutes excluding human review.
- Retry policy: deterministic rerun only before freeze; after freeze a new
  package identity is required.
- Package freeze point: after owner validation and before Anchor derivation.
- Audit requirement: generation/Anchor audit, then independent anchored Replay
  audit and story review.
- Commit boundary: separate Anchor publication commit and Replay/audit/story
  closure commit.
- Fail-closed condition: inventory/hash drift, Anchor mismatch, Replay failure,
  source-byte change, unsafe evidence, or nonzero external/effect counter.
- Next gate: `two_domain_all_real_sealed_evidence_program_v01_s1_supplier_live`.

## 27. S1 Fresh Supplier Scenario Execution Gate

- Gate ID: `two_domain_all_real_sealed_evidence_program_v01_s1_supplier_live`.
- Purpose: execute one fresh six-actor collection and the positive business
  sequence without additional provider collections.
- CREATE paths: `demo/run_two_domain_supplier_water_filter_program_v01.py`;
  `tests/test_two_domain_supplier_water_filter_program_v01_runner.py`;
  `docs/evidence/two_domain_all_real_sealed_evidence_program_v01/supplier_water_filter/supplier_safe_execution_report_v01.json`;
  and `docs/audit_reports/auditor_two_domain_supplier_water_filter_generation_v01.log`.
- MODIFY paths: `AGENTS.md` active checkpoint block only.
- Frozen inputs: accepted R1 adapters, v1.2 live runner, product trace, Gate-1
  Supplier adapter, ActionCommitPacket v0.2, and MockBankSandbox.
- Outputs: immutable `attempt_01`, safe six-actor projection, and executed
  `S-N1`, `S-C1`, `S-P1`, `S-P2`, and `S-M1` evidence.
- Allowed operations: exactly one live collection, deterministic product trace
  once, deterministic Root/approval/corridor processing, secret scan, and safe
  projection.
- Forbidden operations: a second provider collection, pytest live calls,
  automatic retry, real bank/supplier/warehouse calls, payment, or shipment.
- Focused test: `tests/test_two_domain_supplier_water_filter_program_v01_runner.py`
  with injected provider only.
- Short compatibility: selected Supplier adapter and ActionCommitPacket tests,
  excluding live-provider cases.
- Standalone runner: `demo.run_two_domain_supplier_water_filter_program_v01` in
  injected deterministic mode.
- Owner-terminal command: `PYTHONPATH=. .venv/bin/python -m
  demo.run_two_domain_supplier_water_filter_program_v01 --real-provider
  --attempt-number 1 --private-output-directory <owner-supplied-absent-path>`.
- Provider/network/Gemini/effect counts: `6 / 6 / 6 / 0` maximum and exact on
  accepted completion.
- Expected duration: at most fifteen minutes.
- Retry policy: no automatic retry; preserve failure and require owner review.
- Package freeze point: raw attempt freezes on exit; safe execution report
  freezes after validation and secret scan. The official package is S3.
- Audit requirement: independent generation audit before S2.
- Commit boundary: accepted safe execution evidence in a reviewed commit.
- Fail-closed condition: actor/validation failure, count/order mismatch,
  unsafe projection, wrong Root/business state, packet/corridor failure, secret
  finding, or effect.
- Next gate: `two_domain_all_real_sealed_evidence_program_v01_s2_supplier_negative_matrix`.

## 28. S2 Supplier Negative Mutation Matrix Gate

- Gate ID: `two_domain_all_real_sealed_evidence_program_v01_s2_supplier_negative_matrix`.
- Purpose: execute `S-N2`, `S-F1`, `S-F2`, and `S-F3` through public
  validators and complete all nine scenario rows.
- CREATE paths: `demo/run_supplier_water_filter_negative_matrix_v01.py`;
  `tests/test_supplier_water_filter_negative_matrix_v01_runner.py`; and
  `supplier_water_filter_negative_matrix_v01.json` in the Supplier evidence
  directory.
- MODIFY paths: `AGENTS.md` active checkpoint block only.
- Frozen inputs: accepted S1 safe projection, ActionCommitPacket v0.2,
  MockBankSandbox, Gate-1 Supplier adapter, and R1 evidence contracts.
- Outputs: deterministic stable reason codes and evidence rows for all negative
  scenarios.
- Allowed operations: dataclass mutation, direct public validation,
  deterministic report generation, and safe projection.
- Forbidden operations: provider/network/Gemini calls, live retries, external
  effects, and synthetic blocked labels without executed validation.
- Focused test: `tests/test_supplier_water_filter_negative_matrix_v01_runner.py`.
- Short compatibility: bounded
  `tests/test_action_commit_packet_contract_corridor_v02.py` and selected
  Supplier adapter negative tests.
- Standalone runner: `demo.run_supplier_water_filter_negative_matrix_v01`.
- Owner-terminal command: deterministic standalone runner only.
- Provider/network/Gemini/effect counts: `0 / 0 / 0 / 0`.
- Expected duration: under one minute.
- Retry policy: deterministic correction after review; never automatic.
- Package freeze point: negative evidence freezes after all rows validate and
  before S3 package collection.
- Audit requirement: focused negative-matrix review before commit.
- Commit boundary: separate reviewed S2 implementation/evidence commit.
- Fail-closed condition: an attack is accepted, a stable reason is absent, a
  row is missing, or any effect/external counter is nonzero.
- Next gate: `two_domain_all_real_sealed_evidence_program_v01_s3_supplier_seal`.

## 29. S3 Supplier Seal, Anchor, Replay, Audit, and Story Gate

- Gate ID: `two_domain_all_real_sealed_evidence_program_v01_s3_supplier_seal`.
- Purpose: package and independently close all accepted Supplier evidence.
- CREATE paths under the Supplier evidence directory:
  `supplier_safe_evidence_index_v01.json`,
  `supplier_safe_package_index_v01.json`, `supplier_crypto_anchor_v01.json`,
  `supplier_replay_report_v01.json`, and `supplier_human_story_v01.md`; plus
  `docs/audit_reports/auditor_two_domain_supplier_anchor_publication_v01.log`
  and `docs/audit_reports/auditor_two_domain_supplier_anchored_replay_v01.log`.
- MODIFY paths: `AGENTS.md` active checkpoint block only.
- Frozen inputs: accepted S1 and S2 evidence, R1 contracts, and both frozen
  Gate-1 adapters.
- Outputs: one Supplier safe package, committed Anchor, anchored verification,
  sealed Replay, audits, and Human Story containing all nine scenarios.
- Allowed operations: safe package creation, independent inventory
  recomputation, Anchor publication, read-only Replay, and story generation.
- Forbidden operations: provider/network/Gemini calls, raw publication,
  package mutation after freeze, real actions, or rewriting `MIXED`.
- Focused tests: R1 package/Anchor/Replay tests plus S3 binding tests in the
  Supplier programme and negative-matrix focused files.
- Short compatibility: selected generic Integrity/Replay and Supplier adapter
  tests.
- Standalone runners: common package, Anchor, and Replay runners with
  `--domain supplier_water_filter`.
- Owner-terminal command: three explicit deterministic commands in package,
  Anchor, Replay order.
- Provider/network/Gemini/effect counts: `0 / 0 / 0 / 0`.
- Expected duration: at most five minutes excluding human review.
- Retry policy: deterministic rerun only before freeze; after freeze use a new
  package identity.
- Package freeze point: after all nine scenario rows and safe inventory pass,
  before Anchor derivation.
- Audit requirement: Anchor publication audit and independent anchored Replay
  audit/story review.
- Commit boundary: separate Supplier Anchor commit and Replay/audit/story
  closure commit.
- Fail-closed condition: missing scenario, package/hash drift, Anchor mismatch,
  Replay failure, unsafe evidence, hidden `MIXED`, or nonzero effect.
- Next gate: `two_domain_all_real_sealed_evidence_program_v01_x1_cross_domain_audit`.

## 30. X1 Cross-Domain Comparison and Audit Gate

- Gate ID: `two_domain_all_real_sealed_evidence_program_v01_x1_cross_domain_audit`.
- Purpose: compare both closed domain packages against the same Kernel and
  evidence laws.
- CREATE paths: `demo/run_two_domain_sealed_evidence_audit_v01.py`;
  `tests/test_two_domain_sealed_evidence_audit_v01_runner.py`;
  `docs/evidence/two_domain_all_real_sealed_evidence_program_v01/cross_domain_evidence_index_v01.json`;
  and `docs/audit_reports/auditor_two_domain_all_real_sealed_evidence_program_v01.log`.
- MODIFY paths: `AGENTS.md` active checkpoint block only.
- Frozen inputs: both accepted packages, Anchors, Replay reports, audits,
  Human Stories, Gate-1 checkpoint, and R1 contracts.
- Outputs: exact cross-domain claim/evidence comparison and independent audit.
- Allowed operations: read-only parsing, hash verification, contract
  validation, geometry comparison, and safe audit writing.
- Forbidden operations: provider calls, domain reruns, package mutation,
  Anchor mutation, effects, and presentation generation.
- Focused test: `tests/test_two_domain_sealed_evidence_audit_v01_runner.py`.
- Short compatibility: selected shared profile and both domain package-adapter
  tests.
- Standalone runner: `demo.run_two_domain_sealed_evidence_audit_v01`.
- Owner-terminal command: one read-only audit command with exact paths.
- Provider/network/Gemini/effect counts: `0 / 0 / 0 / 0`.
- Expected duration: at most five minutes.
- Retry policy: no automatic retry; source contradiction returns fail closed.
- Package freeze point: both packages and Anchors are already frozen.
- Audit requirement: X1 is the independent audit and requires owner review.
- Commit boundary: separate cross-domain audit commit.
- Fail-closed condition: hash/geometry mismatch, missing claim evidence,
  business-outcome rewrite, authority-law contradiction, or source mutation.
- Next gate: `two_domain_all_real_sealed_evidence_program_v01_x2_showcase`.

## 31. X2 Evidence Book and Showcase Gate

- Gate ID: `two_domain_all_real_sealed_evidence_program_v01_x2_showcase`.
- Purpose: render the reviewed public evidence without creating new runtime
  evidence.
- CREATE paths: `demo/run_two_domain_all_real_evidence_showcase_v01.py`;
  `tests/test_two_domain_all_real_evidence_showcase_v01_runner.py`; and
  `docs/showcase/two_domain_all_real_sealed_evidence_program_v01/README.md`,
  `claim_evidence_matrix_v01.json`, `evidence_book_v01.pdf`,
  `evidence_book_v01.pptx`, `executive_one_pager_v01.pdf`,
  `technical_appendix_v01.pdf`, and `SHA256SUMS`; plus
  `docs/audit_reports/auditor_two_domain_all_real_evidence_showcase_v01.log`
  and `docs/two_domain_all_real_sealed_evidence_program_v01_checkpoint.md`.
- MODIFY paths: `AGENTS.md` active checkpoint block only.
- Frozen inputs: X1 audit and every accepted domain evidence document.
- Outputs: public Evidence Book, deck, one-pager, appendix, matrix, checksums,
  Showcase audit, and final checkpoint.
- Allowed operations: safe static rendering, claim-evidence validation,
  secret scans, checksums, and visual validation.
- Forbidden operations: provider/domain reruns, package/Anchor/Replay mutation,
  raw evidence, effects, and new technical claims.
- Focused test: `tests/test_two_domain_all_real_evidence_showcase_v01_runner.py`.
- Short compatibility: X1 audit test plus deterministic model/projection tests.
- Standalone runner: `demo.run_two_domain_all_real_evidence_showcase_v01`.
- Owner-terminal command: one deterministic render command and one read-only
  Showcase audit command.
- Provider/network/Gemini/effect counts: `0 / 0 / 0 / 0`.
- Expected duration: at most ten minutes.
- Retry policy: deterministic rerender before final freeze; no source repair.
- Package freeze point: generated Showcase freezes before its audit.
- Audit requirement: independent Showcase audit.
- Commit boundary: Evidence Book implementation commit, then Showcase audit
  and final-checkpoint commit.
- Fail-closed condition: missing source, claim without evidence, unsafe text,
  visual overflow, checksum mismatch, raw-material exposure, or overclaim.
- Next gate: programme closed checkpoint after owner acceptance.

## 32. Planned Path Inventory

### CREATE

The exact planned CREATE surface is the union of paths enumerated in Sections
24 through 31. It includes:

- five shared `hedgehog/evidence/` paths;
- three domain evidence adapters;
- three shared package/Anchor/Replay runners;
- Airline and Supplier programme runners;
- one Supplier negative-matrix runner;
- one cross-domain audit runner;
- one Showcase renderer;
- their exact focused tests;
- domain-safe execution, package, Anchor, Replay, audit, and story evidence;
- cross-domain index, audit, Showcase, and final checkpoint.

### MODIFY

- `AGENTS.md`, active checkpoint block only, at each reviewed checkpoint.

Any future need to modify another existing path requires that gate's exact
owner-approved scope. R0 does not authorize an implicit modification.

### FREEZE

- every Gate-1 Kernel module;
- both Gate-1 domain adapters;
- Gate-1 checkpoint and audit;
- runtime release indexes;
- all historical Airline packages, Anchors, Replays, audits, stories, and
  Showcase files;
- all historical Supplier WOW runners, audits, and stories;
- every failed or accepted new attempt after its freeze point.

## 33. Commit and Evidence Freeze Boundaries

The minimum reviewed commit sequence is:

1. R0 preflight;
2. R1 shared profile implementation;
3. R1 independent audit or checkpoint;
4. A1 accepted execution evidence and generation audit;
5. A2 Airline Anchor publication;
6. A2 Airline anchored Replay audit and story closure;
7. S1 accepted execution evidence;
8. S2 negative matrix;
9. S3 Supplier Anchor publication;
10. S3 Supplier anchored Replay audit and story closure;
11. X1 cross-domain audit;
12. X2 Evidence Book implementation;
13. X2 Showcase audit and final checkpoint.

One giant programme commit is forbidden. A failed live attempt is preserved
evidence and cannot be promoted as a PASS package. Package bytes freeze before
Anchor derivation; Anchor bytes freeze before anchored Replay; Replay and audit
must not mutate their inputs.

## 34. Bounded Validation Plan

- Codex runs only gate-focused files and explicitly approved short
  compatibility subsets.
- Full repository pytest through Codex is not planned.
- Live provider execution never occurs inside pytest.
- A1 and S1 owner-terminal commands are separate and sequential.
- Airline executes first and must be frozen and audited before Supplier starts.
- Deterministic runners use exact input paths and bounded timeouts where
  external processes are required.
- A failed live call receives no automatic retry.
- No live provider call occurs during package, Anchor, Replay, audit, story, or
  Showcase phases.
- Every gate runs strict JSON validation where JSON is created, compilation for
  authorized Python paths, `git diff --check`, exact worktree checks, frozen
  hash comparison, and one-terminal-newline/trailing-whitespace checks.

## 35. Security, Privacy, and Secret-Scan Rules

- No credentials, API keys, private keys, or raw environment dumps enter the
  repository.
- No raw prompt or raw provider response enters public evidence.
- No absolute owner path, object representation, memory address, or traceback
  enters public evidence.
- Archives must reject absolute paths, parent traversal, duplicate members,
  unsafe member types, and symlink escape.
- Package roots and members must be explicit, regular, non-symlink paths.
- No package discovery, latest-package selection, or fallback package exists.
- Every live attempt and safe package receives a secret scan before acceptance.
- Safe-projection validation precedes public commit.
- Raw private evidence is not a public package member.
- Failed attempts remain isolated from accepted package identities.
- Automatic retries and silent output replacement are forbidden.

## 36. Public Claims and Non-Claims

The programme may eventually claim only the executed, sealed, anchored,
replayed, and audited observations identified by exact evidence refs.

Required non-claims:

- not production;
- not production certification;
- not arbitrary-domain certification;
- not a real Airline integration;
- not a real bank integration;
- not a real supplier integration;
- not a real warehouse integration;
- not a real GDS integration;
- not real booking;
- not real ticket issuance;
- not real payment;
- not shipment release;
- not production PKI;
- not Root Attestation;
- not production MultiRoot federation;
- not proof of semantic truth;
- not proof that the external world changed;
- not completion of productization;
- not repository cleanup or archival;
- not completion of the Evidence Book during R0.

## 37. Definition of Done

The programme is complete only when:

- R0 through X2 close in order;
- Airline has one accepted twelve-call attempt and Supplier has one accepted
  six-call attempt;
- failed attempts, if any, remain preserved and unpromoted;
- all nine Supplier scenarios are executed, packaged, replayed, audited, and
  presented;
- each domain has a distinct immutable package and committed Anchor;
- each anchored verification and sealed Replay passes independently;
- both independent domain audits pass;
- the cross-domain audit passes;
- the public Showcase audit passes;
- Supplier remains technically `PASS` and operationally `MIXED`;
- Root authority and the zero-real-effect boundary remain preserved;
- no public raw evidence or secret is present;
- the final checkpoint records exact hashes, commits, calls, geometries,
  limitations, and non-claims.

## 38. Immediate Next Gate

After owner review and a dedicated R0 preflight commit, the immediate next gate
is:

`two_domain_all_real_sealed_evidence_program_v01_r1_shared_profile`

R1 must begin from a clean synchronized committed HEAD. It may implement only
the shared evidence profile, domain evidence adapters, deterministic
package/Anchor/Replay runners, and focused tests explicitly listed in this
preflight. It must make no provider call and must not modify Kernel or either
accepted Gate-1 adapter.
