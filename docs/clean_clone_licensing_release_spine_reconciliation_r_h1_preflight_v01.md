# Hedgehog OS / Fractal Reflexive OS
## Workstream R-H1: Clean-Clone, Licensing, and Release-Spine Reconciliation v0.1 Preflight

document_status: PREFLIGHT
document_revision: v0.1.2
guardian_review_status: ACCEPTED
repository_basis_branch: main
accepted_pre_r_h1_base_commit: 3785d67e9d33adf145a3f6f60981abf38767b25d
accepted_pre_r_h1_origin_main: 3785d67e9d33adf145a3f6f60981abf38767b25d
accepted_pre_r_h1_machine_manifest_sha256: 880cc7066e6aedbd9157bf860dcfec7836c8d9f7fb61b92e4262d30b6801aa66
workstream_id: R-H1
workstream_name: Clean-Clone, Licensing, and Release-Spine Reconciliation v0.1
planning_only: true
implementation_authorized: false
g2c_started: false
g2c_implementation_authorized: false
gate2_closed: false
public_release_claimed: false
rc2_claimed: false
production_readiness_claimed: false
production_security_certification_claimed: false
runtime_architecture_changed: false
frozen_release_json_mutation_authorized: false
historical_evidence_rewrite_authorized: false
roadmap_reconstruction_authorized: false
standalone_wheel_claimed: false

## 1. Purpose, Authority, and Scope

This document is the planning contract for R-H1 only. It translates the
accepted clean-clone, licensing, README-status, release-spine, Machine Manifest,
and Repomix inventory into a bounded implementation and audit plan.

This preflight does not authorize implementation. The paths and commands named
below are candidate future scope and validation only. A later explicit owner
instruction is required before R-H1A, R-H1B, R-H1C, R-H1D1, or R-H1D2
may begin.

R-H1 is PRE-G2-C maintenance. It is not:

- G2-C implementation;
- an ExecutionModeRouter patch;
- a runtime architecture change;
- a PlanGraph migration;
- Gate-2 closure;
- RC2;
- a public release;
- production-readiness work;
- production-security-certification work.

Accepted engineering status at this preflight boundary:

- Gate 1: CLOSED_PASS.
- Two-Domain All-Real Sealed Evidence Program: CLOSED_PASS.
- G2-A: CLOSED_PASS.
- G2-B: CLOSED_PASS.
- Gate 2: NOT_CLOSED.
- G2-C: NEXT / NOT_STARTED.
- G2-C implementation: NOT_AUTHORIZED.
- Public release: NOT_CLAIMED.
- RC2: NOT_CLAIMED.
- Production readiness: NOT_CLAIMED.
- Production security certification: NOT_CLAIMED.

## 2. Source-of-Truth and Conflict Resolution

Conflicts are resolved in this exact order:

1. The owner's current explicit instruction.
2. DeepTech Completion Roadmap v3.1 for gate order and accepted architecture.
3. Master Roadmap v2.1 as an implementation-detail donor.
4. The active current-checkpoint block in AGENTS.md.
5. The latest accepted checkpoint and independent audit.
6. An accepted preflight for an explicitly authorized slice.
7. Human Passport, invariants, Machine Manifest, and math appendix.
8. Current runtime contracts and focused tests.
9. Historical preflights, demos, audits, walkthroughs, and showcase material.

Contradictions must be surfaced explicitly. An implementation agent must not
silently reconcile conflicting sources.

### 2.1 Owner and guardian ruling on roadmap custody

OWNER_RULING:

- DeepTech Completion Roadmap v3.1 and Master Roadmap v2.1 are currently
  owner-supplied external engineering-governance companion documents.
- Their full texts are not tracked in this repository.
- Codex must not reconstruct them, summarize them into replacement documents,
  or invent missing roadmap text.
- Their absence from Git does not block R-H1 or G2-C in the current private
  engineering cycle.
- Before public release, tracking them or publishing a consolidated public
  roadmap requires a separate owner decision.

Only these controlling release laws are embedded for R-H1:

- Release work is continuous.
- Internal slices do not become standalone public architectures.
- The public checkpoint, consolidated completion status, claims, limitations,
  and release notes are updated at a gate-closure boundary.
- G2-F is the consolidated Gate-2 closure.
- The Living Release Spine remains a lightweight index over actual evidence,
  not a second implementation project.

This preflight is not a substitute roadmap.

## 3. Architecture Lock

R-H1 preserves this current architecture:

    User / Event
    -> Root intake
    -> WorldState / DRS / CandidateVectors / AVF
    -> Orchestrator semantic route proposal
    -> local validation
    -> Root route acceptance / narrowing / rejection
    -> BSEP
    -> Semantic Architect semantic proposal only
    -> local validation
    -> runtime-owned RuntimeExecutionTopology
    -> bounded actors / executors / child cells
    -> ResultProposals
    -> Root

The controlling boundaries are:

- BSEP transports bounded meaning.
- Semantic Architect proposes semantic work.
- Runtime builds execution topology.
- Root retains authority.
- PlanGraph is legacy, proof-only, and optional internal compatibility IR.
- R-H1 does not alter runtime architecture.
- R-H1 does not resolve PlanGraph documentation drift.
- R-H1 does not authorize G2-C.

No maintenance convenience may change these boundaries.

## 4. Accepted Inventory Findings and Decision Taxonomy

### 4.1 CONFIRMED_FACT

The accepted read-only inventory established:

- A root LICENSE file is absent.
- Project license metadata is absent from pyproject.toml.
- hedgehog/kernel/root_signer_isolation_v01.py imports cryptography at module
  load.
- tests/test_root_signer_isolation_v01.py requires
  cryptography.__version__ == "48.0.0".
- pyproject.toml omits cryptography.
- pyproject.toml currently requires setuptools>=68 with
  setuptools.build_meta, below the selected PEP-639 minimum compatibility
  floor.
- Additional directly imported but undeclared distributions exist:
  referencing, httpx, httpcore, Pillow, python-pptx, pypdf, and reportlab.
- README.md current status is stale.
- The Machine Manifest current pointers are stale and mixed with historical
  data.
- release/completion_manifest.json and
  release/integration_seam_index.json are immutable Gate-1 evidence.
- The five Roadmap-named Markdown release-spine paths are absent:
  release/claim_to_evidence_index.md,
  release/integration_seam_index.md,
  release/one_command_gauntlet.md,
  release/current_limitations.md, and
  release/current_release_notes.md.
- No tracked Repomix handoff recipe exists.
- An editable repository checkout can be the near-term clean-clone target.
- A standalone wheel is not currently complete.

### 4.2 OWNER_RULING

The owner has ruled:

- R-H1 is a pre-G2-C maintenance workstream.
- The intended public-source license candidate is AGPL-3.0-only.
- A separate commercial licensing channel may be offered by the project
  owner.
- Gate 2 remains NOT_CLOSED.
- G2-C remains NEXT / NOT_STARTED and is not authorized.
- Frozen Gate-1 release JSON is historical evidence and is not rewritten.
- External roadmap custody is acceptable for the current private cycle.
- Public-roadmap publication is a separate future decision.

### 4.3 IMPLEMENTATION_DECISION

Subject to later explicit implementation authorization, R-H1 plans:

- a minimal flat dependency declaration reconciliation;
- a minimum setuptools PEP-639 compatibility-floor correction without an
  exact backend pin, upper bound, or backend redesign;
- complete canonical AGPL-3.0 license text sourced exactly, not reconstructed;
- a non-granting commercial licensing information notice;
- a narrow README current-status and command repair;
- an explicit current Machine Manifest boundary without historical rewrites;
- a current status overlay plus lightweight Markdown release indexes;
- frozen-hash tests for the Gate-1 release JSON;
- a repository-owned deterministic Repomix handoff recipe;
- focused maintenance contract tests;
- independent audit and owner closure.

### 4.4 DEFERRED_WORK

The following are deferred:

- standalone wheel completeness;
- package-resource migration;
- console entry points;
- lockfile or constraints policy;
- optional dependency-group redesign;
- exact build-backend pinning beyond the authorized minimum compatibility
  floor;
- THIRD_PARTY_NOTICES.md until an obligation and provenance review;
- generic NOTICE;
- SBOM generation;
- consolidated Gate-2 completion and release claims until G2-F;
- PlanGraph documentation reconciliation;
- public roadmap custody or publication;
- production installation support.

### 4.5 PROHIBITED_WORK

R-H1 prohibits:

- G2-C implementation;
- runtime architecture changes;
- mode-router changes;
- RuntimeExecutionTopology implementation;
- PlanGraph migration or cleanup;
- Root, BSEP, DRS, AVF, or GT runtime changes;
- historical evidence rewrites;
- frozen Gate-1 release JSON edits;
- live provider, Telegram, connector, or real-effect execution;
- public release, RC2, Gate-2 closure, production-readiness, or security
  certification claims.

## 5. Exact Near-Term Clean-Clone Contract

### 5.1 Supported promise

The supported R-H1 target is an editable checkout from the repository root.
After one editable installation command, an external reviewer can run
deterministic Kernel Conformance and Living Gauntlet:

- with no credentials;
- with no Gemini or provider call;
- with no Telegram call;
- with no runtime network call;
- with no real-world effect.

The intended command path is:

    python3 -m venv .venv
    .venv/bin/python -m pip install -e .
    .venv/bin/python -m pip check
    PYTHONDONTWRITEBYTECODE=1 PYTHONPATH=. \
      .venv/bin/python -m demo.run_kernel_conformance_v01
    PYTHONDONTWRITEBYTECODE=1 PYTHONPATH=. \
      .venv/bin/python -m demo.run_living_gauntlet_v01

This is a future acceptance target, not evidence that the clean-clone sequence
has already passed. Clean-clone success must not be claimed until the
owner-terminal validation has actually run in an external clean clone.

### 5.2 Explicit boundaries

- Editable checkout from repository root is the supported R-H1 target.
- Standalone wheel completeness is NOT_CLAIMED.
- Package-resource migration is deferred.
- Console entry points are deferred.
- Lockfile and constraints policy are deferred.
- No production installation claim is created.
- Installation may access a package index; deterministic runtime execution
  after installation must require neither credentials nor network calls.

## 6. Dependency Reconciliation Contract

### 6.1 Minimal flat declaration

R-H1 plans a minimal flat dependency reconciliation. It does not redesign
optional extras, move existing dependencies between groups, introduce a
lockfile, exactly pin the build backend, add a build-backend upper bound, or
remove a current dependency.

The implementation candidate dependency set retains:

- jsonschema
- pytest
- pyTelegramBotAPI
- google-genai

It adds direct declarations for:

- cryptography==48.0.0
- referencing
- httpx
- httpcore
- Pillow
- python-pptx
- pypdf
- reportlab

Only cryptography receives an exact version pin in R-H1 because the repository
already enforces that exact version through
tests/test_root_signer_isolation_v01.py.

Observed local versions of other packages are environment observations, not
automatic dependency contracts.

### 6.2 Build-system compatibility floor

The live pre-R-H1 build system is:

    [build-system]
    requires = ["setuptools>=68"]
    build-backend = "setuptools.build_meta"

The accepted PEP-639 compatibility ruling authorizes R-H1A to change only the
minimum setuptools floor:

    [build-system]
    requires = ["setuptools>=77.0.3"]
    build-backend = "setuptools.build_meta"

setuptools>=77.0.3 is a minimum floor, not an exact pin. R-H1A adds no upper
bound, no other build-system dependency, and no build-backend redesign.
Observed local setuptools versions do not become dependency contracts.

Exact build-backend pinning remains deferred. The authorized minimum
compatibility-floor correction is not an exact pin.

### 6.3 Classification boundary

R-H1 does not reorganize dependencies into core, dev/test, live-provider,
Telegram, or showcase/document extras. Such classification may be evaluated
later from actual installation and consumer evidence, but existing
dependencies are not moved for packaging aesthetics.

The flat declaration is intentionally conservative:

- cryptography is mandatory because canonical code imports it at module load;
- directly imported distributions are declared by distribution name;
- existing pytest, provider, and Telegram declarations remain in place;
- optionality redesign is deferred until it has a concrete clean-install or
  release benefit.

### 6.4 Focused dependency and build contract test

tests/test_repository_maintenance_contract_v01.py must verify:

- every mandatory/direct third-party import identified by the accepted
  inventory maps to a declared distribution;
- import roots and distribution names are mapped explicitly where they differ,
  including PIL to Pillow, pptx to python-pptx, fitz-free pypdf use to pypdf,
  telebot to pyTelegramBotAPI, and google.genai to google-genai;
- the cryptography declaration is exactly cryptography==48.0.0;
- that declaration is coherent with the exact-version assertion in
  tests/test_root_signer_isolation_v01.py;
- retained current direct dependencies remain declared;
- the build backend remains setuptools.build_meta;
- the setuptools requirement has a minimum of at least 77.0.3;
- the setuptools requirement is not an exact pin and has no upper bound;
- no other build-system dependency is introduced;
- the test does not attempt to infer every optional transitive import in the
  Python ecosystem;
- no import check performs provider, Telegram, connector, network, or effect
  execution.

## 7. Licensing and Provenance Contract

### 7.1 Owner licensing direction

The owner intends:

- public-source license candidate: AGPL-3.0-only;
- separate commercial licensing may be offered by the project owner.

Candidate future paths:

- LICENSE
- COMMERCIAL-LICENSING.md

Candidate existing metadata path:

- pyproject.toml

### 7.2 LICENSE requirements

Later implementation may create LICENSE only when an exact canonical source is
available. The file must contain the complete, standard, unmodified GNU Affero
General Public License version 3 text.

Codex must not invent, abbreviate, paraphrase, or reconstruct license text from
memory. If an exact canonical source cannot be obtained under the authorized
execution rules, license-file creation fails closed for owner action.

This engineering plan makes no legal conclusion and does not assert legal
review, title, copyright ownership, patent clearance, third-party compatibility,
or relicensing authority.

Before R-H1A may write LICENSE, its implementation report must identify the
exact canonical source used and record:

- a precise source description;
- the SHA-256 of the exact source bytes;
- how those exact bytes were made available under the separately authorized
  implementation execution rules.

Codex must not invent a contact address, copyright-holder statement, patent
statement, or legal-review statement. If no exact authorized canonical source
is available, R-H1A stops before LICENSE or pyproject.toml license-metadata
mutation and reports the blocker. This preflight does not authorize network
access to obtain license text.

### 7.3 Exact future pyproject metadata shape

The preferred implementation decision is the PEP 639 project metadata shape:

    [build-system]
    requires = ["setuptools>=77.0.3"]
    build-backend = "setuptools.build_meta"

    [project]
    license = "AGPL-3.0-only"
    license-files = ["LICENSE"]

Existing project metadata outside these keys remains unchanged unless a later
authorization explicitly says otherwise. README licensing language must use
the same AGPL-3.0-only identifier.

The current setuptools>=68 floor is known to be below the selected PEP-639
compatibility floor. R-H1A resolves that known mismatch by raising only the
minimum to setuptools>=77.0.3. The backend remains setuptools.build_meta, the
requirement remains open above the minimum, and no observed environment
version is made exact.

Validation must inspect prepared or generated package metadata and confirm the
expected SPDX license expression and included license file. This preflight
does not build a package.

### 7.4 Commercial channel notice

COMMERCIAL-LICENSING.md is a non-granting informational policy notice. It may
state:

- separate commercial terms may be available only under a separately executed
  written agreement with the rights holder;
- this repository file does not grant those terms;
- the public-source license remains AGPL-3.0-only;
- an owner-designated commercial contact channel is not yet published in the
  repository.

Absence of a published contact email or URL does not block R-H1A.

Codex must not:

- invent an email address;
- invent a website or form;
- nominate GitHub Issues or another platform without owner instruction;
- insert placeholder contact data;
- claim a commercial agreement exists;
- claim title or relicensing authority;
- claim patent clearance or legal review;
- claim public release;
- claim RC2;
- claim production readiness;
- claim production security certification.

A contact channel may be added only by a later explicit owner instruction.

THIRD_PARTY_NOTICES.md is deferred until an actual obligation and provenance
review. A generic NOTICE file is not authorized in R-H1.

## 8. README Reconciliation Boundary

R-H1 plans a narrow README repair, not a whole-document rewrite.

R-H1B creates exactly one complete current-status block bounded by:

    <!-- BEGIN HEDGEHOG CURRENT ENGINEERING BOUNDARY -->
    <!-- END HEDGEHOG CURRENT ENGINEERING BOUNDARY -->

The marker-bounded block includes:

- R-H1 workstream status and lifecycle fields;
- Gate 1: CLOSED_PASS.
- Two-Domain programme: CLOSED_PASS.
- G2-A: CLOSED_PASS.
- G2-B: CLOSED_PASS.
- Gate 2: NOT_CLOSED.
- G2-C: NEXT / NOT_STARTED.
- G2-C implementation: NOT_AUTHORIZED.
- Public release: NOT_CLAIMED.
- RC2: NOT_CLAIMED.
- Production readiness: NOT_CLAIMED.
- Production security certification: NOT_CLAIMED.
- the committed R-H1 preflight reference;
- current R-H1 audit and checkpoint references when applicable;
- current release-spine links.

The phrase "G2-C is in development" is inaccurate at this boundary and must
not appear as current status.

R-H1B also owns these narrow README changes outside the marker-bounded block:

- repair the malformed install/run command block;
- publish the editable clean-clone command path;
- add a short licensing section;
- link COMMERCIAL-LICENSING.md as a non-granting policy notice.

After the committed R-H1A-through-R-H1C implementation basis is audited by
R-H1D1, the README install, clean-clone, licensing, AGPL identifier, and
commercial-notice wording outside the markers are frozen.

R-H1D2 may modify README.md only inside the exact markers, and only to:

- transition R-H1 from IMPLEMENTATION_IN_PROGRESS to CLOSED_PASS;
- add accepted audit and checkpoint references;
- add exact implementation_basis_commit and audit_commit references where
  designed;
- preserve every Gate, G2-C, and public non-claim.

R-H1D2 must not modify:

- README licensing wording;
- the AGPL-3.0-only identifier;
- commercial-licensing wording;
- install or clean-clone commands;
- project description;
- historical checkpoint sections;
- any byte outside the marker-bounded block.

It must not:

- rewrite the whole README;
- rewrite historical checkpoints;
- delete useful historical evidence descriptions;
- perform a PlanGraph migration;
- claim G2-C development;
- claim Gate-2 closure;
- claim public release;
- claim RC2;
- claim production readiness or production security certification.

Focused tests must locate a single explicit current-status block and validate
that block. They must not reinterpret historical narrative as current queue
authority.

The R-H1D2 boundary guard reads README.md from implementation_basis_commit,
removes the complete marker-bounded block from both basis and current byte
views, and asserts all remaining bytes are identical. It separately validates
the complete CLOSED_PASS marker block. Missing, duplicated, nested, reordered,
or malformed markers fail closed.

## 9. Machine Manifest Reconciliation Boundary

R-H1 rejects a bulk rewrite of specs/machine_manifest_v0_25.json.

The immutable accepted baseline identity is:

    accepted_pre_r_h1_machine_manifest_sha256:
    880cc7066e6aedbd9157bf860dcfec7836c8d9f7fb61b92e4262d30b6801aa66

The reproducible baseline byte source is:

    git show \
      3785d67e9d33adf145a3f6f60981abf38767b25d:specs/machine_manifest_v0_25.json

No baseline fixture file is added.

The following remain preserved:

- metadata_sync_only = true;
- manifest_does_not_override_human_passport = true;
- historical checkpoint-specific objects;
- historical facts true at the checkpoint they describe;
- constitutional contracts, formulas, entities, and architecture fields;
- PlanGraph-era architecture fields, pending separate future treatment.

### 9.1 Read-only findings and exact pre-existing-pointer allowlist

Read-only inspection found current_checkpoint_status to be a large mixed
historical ledger. In particular:

| JSON Pointer | Present value or semantic role | Current or historical finding | R-H1 mutation permission |
| --- | --- | --- | --- |
| /current_checkpoint_status/metadata_sync_only | true | Constitutional metadata boundary that must remain true | NONE; preserved |
| /current_checkpoint_status/manifest_does_not_override_human_passport | true | Constitutional source-order boundary that must remain true | NONE; preserved |
| /current_checkpoint_status/latest_confirmed_checkpoint_commit | 3dd9e89 | Gate-1-era latest pointer embedded in a mixed historical ledger | NONE; ambiguous historical/current role |
| /current_checkpoint_status/latest_confirmed_checkpoint_name | domain_neutral_reference_kernel_gate1_rc1 | Gate-1-era latest pointer embedded in a mixed historical ledger | NONE; ambiguous historical/current role |
| /current_checkpoint_status/latest_confirmed_checkpoint_pending_docs_sync | false | Gate-1-era synchronization fact | NONE; historical |
| /current_checkpoint_status/next_immediate_gate | airline_all_real_program_v01_context_dump_before_master_roadmap_review | Historical queue pointer from an earlier programme | NONE; historical |
| /current_checkpoint_status/next_engineering_preflight_after_story | airline_all_real_program_v01_context_dump_before_master_roadmap_review | Historical queue pointer from an earlier programme | NONE; historical |
| /current_checkpoint_status/next_implementation_gate | airline_all_real_program_v01_context_dump_before_master_roadmap_review | Historical queue pointer from an earlier programme | NONE; historical |
| /current_checkpoint_status/next_major_gate | airline_all_real_program_v01_context_dump_before_master_roadmap_review | Historical queue pointer from an earlier programme | NONE; historical |
| /current_checkpoint_status/next_engineering_layer | supplier_payment_shipment_release_live_dual_role_wow_v1_preflight | Historical roadmap pointer | NONE; historical |

The exact R-H1 allowlist for modifying pre-existing Machine Manifest fields is
empty. No pre-existing JSON pointer may be changed by R-H1A, R-H1B, R-H1C,
R-H1D1, or R-H1D2.

This is the fail-closed default because a safe semantic distinction between
all historical and unscoped current pointers cannot be established without a
separate owner amendment.

### 9.2 Exact add-only permission

R-H1B may add exactly one previously absent JSON pointer:

| JSON Pointer | Present value | Semantic role | Slice | Allowed operation |
| --- | --- | --- | --- | --- |
| /current_checkpoint_status/current_engineering_boundary_v01 | ABSENT | Explicit current engineering boundary separate from the historical ledger | R-H1B | ADD one object in IMPLEMENTATION_IN_PROGRESS state |

No other add, remove, replace, move, copy, or whole-file normalization is
allowed.

The implementation must preserve all non-target bytes wherever technically
possible. No search-and-replace over status strings and no formatter-driven
whole-file rewrite is allowed.

### 9.3 Commit-identity vocabulary

The current boundary and overlay use these distinct concepts:

1. accepted_pre_r_h1_base_commit
   - Immutable value:
     3785d67e9d33adf145a3f6f60981abf38767b25d.
   - It identifies the accepted repository basis before R-H1.
   - It is not named head.

2. preflight_commit
   - Populated only after this preflight is committed.
   - It must not be guessed or self-predicted in this uncommitted document.

3. implementation_basis_commit
   - The committed R-H1A-through-R-H1C implementation basis audited by
     R-H1D1.
   - It is null until that exact committed basis is known.

4. audit_commit
   - The commit containing the accepted R-H1D1 audit artifact.
   - It is null until that commit exists and is known.

5. closure_commit_identity
   - It is null before owner closure.
   - It is NOT_SELF_RECORDED inside any document or current surface first
     committed by the closure commit.
   - The external Git commit identity is recorded outside the
     self-referential closure document.

No generic field named head may stand in for any of these identities.

### 9.4 Exact R-H1 lifecycle

The lifecycle has three states:

A. PREFLIGHT_ONLY

- Valid only for this planning document before implementation authorization.
- implementation_was_explicitly_authorized = false.
- implementation_open = false.
- closure_claimed = false.
- independent_audit_passed = false.
- This state must not be copied into an R-H1B-created current repository
  surface.

B. IMPLEMENTATION_IN_PROGRESS

- Used when R-H1B first creates current machine and status surfaces.
- An explicit implementation authorization has been observed.
- implementation_was_explicitly_authorized = true.
- implementation_open = true.
- closure_claimed = false.
- independent_audit_passed = false.
- This state remains through R-H1C and R-H1D1.

C. CLOSED_PASS

- Used only by R-H1D2 after accepted R-H1D1 audit PASS.
- implementation_was_explicitly_authorized = true.
- implementation_open = false.
- closure_claimed = true.
- independent_audit_passed = true.
- Exact audit and checkpoint references are present.

G2-C remains NEXT / NOT_STARTED and NOT_AUTHORIZED in every R-H1 state.

The four fields implementation_was_explicitly_authorized,
implementation_open, closure_claimed, and independent_audit_passed are
independent facts. No ambiguous implementation_authorized boolean may overload
them across phases.

### 9.5 Exact current_engineering_boundary_v01 shape

R-H1B creates the object with these field names and initial semantics:

| Field | R-H1B value |
| --- | --- |
| profile_version | v0.1 |
| boundary_id | current_engineering_boundary_v01 |
| accepted_pre_r_h1_base_commit | 3785d67e9d33adf145a3f6f60981abf38767b25d |
| preflight_commit | exact committed preflight commit, known at R-H1B entry |
| implementation_basis_commit | null |
| audit_commit | null |
| closure_commit_identity | null |
| workstream_id | R-H1 |
| workstream_status | IMPLEMENTATION_IN_PROGRESS |
| implementation_was_explicitly_authorized | true |
| implementation_open | true |
| closure_claimed | false |
| independent_audit_passed | false |
| gate1_status | CLOSED_PASS |
| two_domain_status | CLOSED_PASS |
| g2a_status | CLOSED_PASS |
| g2b_status | CLOSED_PASS |
| gate2_status | NOT_CLOSED |
| g2c_status | NEXT_NOT_STARTED |
| g2c_implementation_authorized | false |
| public_release_claimed | false |
| rc2_claimed | false |
| production_readiness_claimed | false |
| production_security_certification_claimed | false |
| accepted_pre_r_h1_checkpoint | docs/drs_semantic_address_space_reuse_certificate_g2_b_checkpoint_v01.md |
| accepted_pre_r_h1_audit | docs/audit_reports/auditor_drs_semantic_address_space_reuse_certificate_g2_b_v01.log |
| r_h1_audit_path | null |
| r_h1_checkpoint_path | null |
| historical_nested_objects_are_current_queue_authority | false |

Unknown commit identities are JSON null, not guessed strings.

### 9.6 Exact R-H1D2 child-pointer transition allowlist

After R-H1B adds the object, only R-H1D2 may replace these literal child
pointers:

| JSON Pointer | From | To |
| --- | --- | --- |
| /current_checkpoint_status/current_engineering_boundary_v01/workstream_status | IMPLEMENTATION_IN_PROGRESS | CLOSED_PASS |
| /current_checkpoint_status/current_engineering_boundary_v01/implementation_open | true | false |
| /current_checkpoint_status/current_engineering_boundary_v01/closure_claimed | false | true |
| /current_checkpoint_status/current_engineering_boundary_v01/independent_audit_passed | false | true |
| /current_checkpoint_status/current_engineering_boundary_v01/implementation_basis_commit | null | exact committed R-H1A-through-R-H1C basis audited by R-H1D1 |
| /current_checkpoint_status/current_engineering_boundary_v01/audit_commit | null | exact accepted R-H1D1 audit commit |
| /current_checkpoint_status/current_engineering_boundary_v01/closure_commit_identity | null | NOT_SELF_RECORDED |
| /current_checkpoint_status/current_engineering_boundary_v01/r_h1_audit_path | null | docs/audit_reports/auditor_clean_clone_licensing_release_spine_reconciliation_r_h1_v01.log |
| /current_checkpoint_status/current_engineering_boundary_v01/r_h1_checkpoint_path | null | docs/clean_clone_licensing_release_spine_reconciliation_r_h1_checkpoint_v01.md |

All other child pointers remain unchanged. In particular,
implementation_was_explicitly_authorized remains true and every G2-C and
non-claim field remains unchanged.

### 9.7 Focused preservation test

tests/test_repository_release_spine_v01.py must:

- read exact baseline bytes with git show from
  3785d67e9d33adf145a3f6f60981abf38767b25d at
  specs/machine_manifest_v0_25.json;
- verify the baseline raw SHA-256 is exactly
  880cc7066e6aedbd9157bf860dcfec7836c8d9f7fb61b92e4262d30b6801aa66;
- parse that accepted baseline object;
- parse the current working-tree object;
- remove only
  /current_checkpoint_status/current_engineering_boundary_v01 from the
  current parsed view;
- assert the remaining current object is exactly equal to the accepted
  baseline parsed object;
- separately validate the complete exact key set and conditional values of
  current_engineering_boundary_v01;
- separately guard current_checkpoint_status/domain_neutral_reference_kernel_gate1_rc1
  and other selected historical objects against parsed-value drift;
- assert metadata_sync_only and
  manifest_does_not_override_human_passport remain true;
- avoid treating JSON key ordering as semantic authority;
- avoid scanning historical strings and demanding their removal.

For CLOSED_PASS, the test must additionally:

- read implementation_basis_commit from the current boundary;
- use git show at that exact commit to read the
  IMPLEMENTATION_IN_PROGRESS specs/machine_manifest_v0_25.json;
- require that implementation-basis Manifest to contain the exact expected
  in-progress boundary;
- compare the implementation-basis boundary with the closed boundary;
- permit differences only at the literal R-H1D2 child-pointer allowlist in
  Section 9.6;
- reject every other changed, removed, or added child field.

The test may require a full Git checkout because R-H1 promises an editable Git
repository checkout, not a standalone wheel or source archive. If required
Git objects are unavailable, the test fails explicitly with an
unsupported non-Git/source-archive validation result. It must not skip the
preservation checks and must not fetch history from the network.

Any desired Machine Manifest mutation outside this literal allowlist requires
a separate owner amendment before editing.

## 10. Frozen Gate-1 Release Evidence

These current identities are binding:

- release/completion_manifest.json
  SHA-256:
  02ffac0d78df768f91df0bb06bdd15ec463dbe5ccea6ef82b7022146819f3466
- release/integration_seam_index.json
  SHA-256:
  c29c2ff873c8b448d8825c3288918e980eab3d65a5114762d2e3fbe5b1206231

Classification: FROZEN_EVIDENCE.

Both files describe accepted Gate-1 evidence. They remain byte-identical
throughout R-H1. A future focused test must hash the raw bytes and assert both
exact values.

R-H1 must not:

- edit either file;
- rename either file;
- version-copy and repurpose either original path;
- change runtime consumers;
- change existing tests merely to accept new bytes;
- rewrite audits or checkpoints containing their hashes.

The new Markdown integration seam index is a current human-readable overlay.
It does not replace or reinterpret the frozen JSON.

## 11. Current Status Overlay and Living Release Spine

Candidate new paths:

- release/current_status_overlay_v01.json
- release/claim_to_evidence_index.md
- release/integration_seam_index.md
- release/one_command_gauntlet.md
- release/current_limitations.md
- release/current_release_notes.md
- tests/test_repository_release_spine_v01.py

These are candidate future paths only. Their listing does not authorize
implementation.

### 11.1 current_status_overlay_v01.json

The overlay is:

- metadata-only;
- current and mutable under controlled checkpoint updates;
- not authority;
- not a Root decision;
- not a completion certificate;
- not a replacement for historical evidence;
- not a Gate-2 closure manifest;
- not a public-release declaration;
- a machine-readable mirror of accepted checkpoint status.

Its future minimum content includes:

- schema/profile version;
- overlay identifier;
- accepted_pre_r_h1_checkpoint with the exact pre-R-H1 G2-B checkpoint path;
- accepted_pre_r_h1_audit with the exact pre-R-H1 G2-B audit path;
- accepted_pre_r_h1_base_commit with the immutable value
  3785d67e9d33adf145a3f6f60981abf38767b25d;
- preflight_commit populated only from the known committed preflight;
- implementation_basis_commit, audit_commit, and closure_commit_identity with
  the phase-specific semantics in Section 9;
- current gate and slice status;
- G2-C not-started state;
- G2-C implementation authorization false;
- public-release, RC2, production-readiness, and production-security
  non-claims;
- frozen evidence references with exact hashes;
- separate r_h1_audit_path and r_h1_checkpoint_path closure references;
- an explicit statement that it does not override AGENTS.md, checkpoints,
  audits, Human Passport, or owner instruction.

The overlay must distinguish the current source boundary from historical
evidence bases. It cannot infer closure from status strings alone.

The accepted_pre_r_h1_checkpoint and accepted_pre_r_h1_audit fields identify
the stable engineering boundary before R-H1. They do not claim to remain
globally current after R-H1. R-H1 closure is represented separately by
r_h1_audit_path, r_h1_checkpoint_path, audit_commit, and
closure_commit_identity.

R-H1B creates the overlay in IMPLEMENTATION_IN_PROGRESS, never
PREFLIGHT_ONLY. R-H1C and R-H1D1 do not advance that state. R-H1D2 may advance
it to CLOSED_PASS only after accepted audit PASS and must synchronize the
implementation basis, audit commit, audit path, checkpoint path, and
NOT_SELF_RECORDED closure identity.

The overlay must contain the four separate booleans:

- implementation_was_explicitly_authorized;
- implementation_open;
- closure_claimed;
- independent_audit_passed.

It must not use one implementation_authorized boolean as a substitute for
those lifecycle facts.

### 11.2 Status lifecycle consistency

README.md, current_engineering_boundary_v01, and
current_status_overlay_v01.json must expose one allowed lifecycle state:

- IMPLEMENTATION_IN_PROGRESS during R-H1B, R-H1C, and R-H1D1; or
- CLOSED_PASS only after R-H1D2 owner closure.

Focused tests must validate the complete conditional geometry of whichever
allowed state is present. They must not hard-code PREFLIGHT_ONLY as the future
implementation state.

G2-C remains NEXT / NOT_STARTED and NOT_AUTHORIZED in both allowed states.

### 11.3 claim_to_evidence_index.md

This lightweight index:

- lists only accepted claims;
- maps each claim to focused tests, runtime evidence, audit, and checkpoint;
- gives each claim an explicit limitation or non-claim;
- does not create a new claim;
- does not elevate internal evidence to a public architecture.

### 11.4 integration_seam_index.md

This is the human-readable current overlay required by the roadmap naming
convention. It:

- references release/integration_seam_index.json as frozen Gate-1 evidence;
- does not replace, rename, or rewrite that JSON;
- indexes current accepted seams and their evidence;
- makes no final Gate-2 seam-inventory claim;
- preserves G2-C as not started.

### 11.5 one_command_gauntlet.md

This document:

- presents deterministic no-credential commands;
- uses Kernel Conformance and Living Gauntlet as the supported checkout path;
- does not make a live-provider command the default;
- does not invoke Telegram or a connector;
- makes no real-effect or production claim;
- distinguishes installation network activity from no-network deterministic
  runtime execution.

### 11.6 current_limitations.md

This document records at least:

- Gate 2 is not closed;
- G2-C is not started or authorized;
- no production, public-release, RC2, or security-certification claim;
- editable checkout only;
- standalone wheel incomplete;
- no real-world effects;
- external roadmaps remain owner companion documents in the private cycle.

### 11.7 current_release_notes.md

This document is labeled current engineering notes. It:

- is not a public release announcement;
- does not claim RC2;
- does not claim Gate-2 closure;
- does not promote internal slices to standalone public architectures;
- points to evidence and limitations instead of duplicating them.

### 11.8 Gate-2 boundary

The consolidated Gate-2 completion manifest, consolidated public checkpoint,
and Gate-2 release claim remain deferred to G2-F. R-H1 creates only a current
metadata overlay and lightweight indexes.

## 12. Repomix Handoff Reproducibility Contract

Candidate future paths:

- repomix.handoff.config.json
- tools/generate_repomix_handoff_v01.py
- docs/repomix_handoff_reproducibility_v01.md
- tests/test_repomix_handoff_reproducibility_v01.py

These are candidate future paths only. No Repomix output is generated by this
preflight.

### 12.1 Required repository-derived handoff set

The recipe must reproduce, in this exact order:

1. 00_head_and_origin.txt
2. 00_repo_governance_and_metadata.md
3. 01_hedgehog_kernel_and_contracts.md
4. 02_docs_specs_checkpoints_and_roadmaps.md
5. 03_demo_runners_and_fixtures.md
6. 04_tests_and_test_fixtures.md
7. 05_audit_logs_and_public_safe_evidence.md
8. 06_current_g2a_g2b_focus.md
9. 07_passport_release_and_root_contract_data.md
10. SHA256SUMS

The two full roadmap documents remain separately supplied owner companion
documents during this private cycle. The generator must not fabricate,
reconstruct, or synthesize them. The docs/specs pack may identify their
external custody without pretending their full text is repository-derived.

### 12.2 Required R-H1 artifact coverage matrix

The handoff design must reproducibly cover R-H1 itself:

| Output profile | Required R-H1 coverage when present |
| --- | --- |
| 00_repo_governance_and_metadata.md | AGENTS.md; README.md; pyproject.toml; LICENSE; COMMERCIAL-LICENSING.md; repomix.handoff.config.json; tools/generate_repomix_handoff_v01.py; docs/repomix_handoff_reproducibility_v01.md |
| 02_docs_specs_checkpoints_and_roadmaps.md | docs/clean_clone_licensing_release_spine_reconciliation_r_h1_preflight_v01.md; docs/clean_clone_licensing_release_spine_reconciliation_r_h1_checkpoint_v01.md after it exists |
| 04_tests_and_test_fixtures.md | tests/test_repository_maintenance_contract_v01.py; tests/test_repository_release_spine_v01.py; tests/test_repomix_handoff_reproducibility_v01.py |
| 05_audit_logs_and_public_safe_evidence.md | docs/audit_reports/auditor_clean_clone_licensing_release_spine_reconciliation_r_h1_v01.log after it exists |
| 07_passport_release_and_root_contract_data.md | specs/machine_manifest_v0_25.json; release/current_status_overlay_v01.json; release/claim_to_evidence_index.md; release/integration_seam_index.md; release/one_command_gauntlet.md; release/current_limitations.md; release/current_release_notes.md; release/completion_manifest.json; release/integration_seam_index.json |

The configuration must list planned-but-not-yet-existing R-H1 artifacts
explicitly. It must not silently drop them:

- Before the artifact's owning slice, the profile inventory records
  NOT_YET_PRESENT with its expected owner slice.
- Once the path is tracked, omission from every intended profile is an error.
- A post-R-H1D2 handoff treats the audit and checkpoint as required.
- A pre-closure handoff may report those two paths as NOT_YET_PRESENT but must
  preserve their intended profile mappings.
- Missing optional tool availability does not erase profile coverage
  requirements.

The focused Repomix test must enumerate every tracked R-H1 governance,
implementation-test, audit, checkpoint, and release-spine artifact and assert
that each maps to at least one intended handoff profile.

Generated exports remain excluded and untracked.

### 12.3 Generation contract

- Generated output root:
  _audit_exports/<handoff-id>/.
- Generated outputs remain untracked.
- _audit_exports/ must be ignored under an explicit future Git policy.
- The generator fails on a dirty worktree unless an explicit
  diagnostic-only override is designed, named, and documented.
- The default path captures branch, HEAD, origin/main, dirty state, Repomix
  version, profile order, output order, and hashes.
- Checksum ordering is deterministic and bytewise stable.
- Profile ordering is deterministic and fixed in configuration.
- No network access belongs to generation.
- The script never stages, commits, or pushes generated exports.
- The script never writes generated packs outside the declared export root.
- Failure before all outputs verify must not publish a successful SHA256SUMS.

### 12.4 Explicit exclusions

Required local and generated exclusions include at least:

- .git/**
- .venv/**
- venv/**
- .tmp/**
- _audit_exports/**
- **/__pycache__/**
- **/*.pyc
- **/*.pyo
- .pytest_cache/**
- .mypy_cache/**
- .ruff_cache/**
- htmlcov/**
- .coverage
- coverage.xml
- node_modules/**
- dist/**
- build/**
- .DS_Store
- .idea/**
- .vscode/**
- .codex/**
- repomix-output.*
- config.py
- .env
- .env.*
- **/.env
- **/.env.*
- logs/**
- data/logs/**
- data/drs/**/*.json
- **/*.pem
- **/*.key
- **/*.p12
- **/*.pfx
- local credentials
- local signing material
- provider raw outputs
- secret-bearing local artifacts

A recursive wildcard that excludes every file solely because its suffix is
.log is prohibited. Committed public-safe audit artifacts use that suffix.

docs/audit_reports/*.log may enter only through the explicit public-safe
profile for 05_audit_logs_and_public_safe_evidence.md. Local runtime log
directories remain excluded.

Broad docs/** inclusion is prohibited as an implicit public-safe rule. Audit
logs and evidence are selected through explicit public-safe include profiles.
An included historical document is evidence, not current authority.

### 12.5 Validation modes

Static contract tests:

- parse the configuration;
- assert exact profile names and order;
- assert exact output names and order;
- assert required secret exclusions;
- assert local runtime log directories are excluded;
- assert no recursive all-.log exclusion exists;
- assert only explicitly selected committed public-safe audit logs are
  included;
- assert docs/audit_reports/*.log is owned only by the public-safe evidence
  profile;
- assert broad docs/** inclusion remains prohibited;
- assert _audit_exports is untracked and ignored;
- assert generator code contains no stage, commit, push, or network action;
- assert roadmaps are not fabricated;
- assert every tracked R-H1 artifact maps to an intended profile;
- assert planned R-H1 audit and checkpoint mappings remain explicit before
  those paths exist;
- assert post-closure coverage cannot silently omit either closure artifact;
- assert R-H1 audit coverage is mandatory after the audit exists.

Generator dry validation:

- validates repository state, profiles, exclusions, output plan, tool
  availability, and destination policy;
- creates no handoff outputs;
- fails clearly if a required contract is invalid.

Real local generation when Repomix is available:

- runs only under explicit later authorization;
- captures the local Repomix version;
- generates every ordered pack;
- emits SHA256SUMS only after all packs complete.

Generated checksum verification:

- verifies exact output set;
- verifies deterministic ordering;
- verifies every SHA-256 entry against bytes;
- rejects extra, missing, reordered, or renamed outputs.

Repomix-absent behavior:

- static tests and dry validation remain available;
- real generation fails with an explicit unavailable-tool result;
- it does not install Repomix;
- it does not create partial outputs;
- it does not report generation PASS.

## 13. Internal R-H1 Slice Plan

Every path below is candidate future scope only. Listing a path does not
authorize implementation.

### 13.1 R-H1A - Clean-Clone Dependencies and Licensing

Candidate paths:

- pyproject.toml
- LICENSE
- COMMERCIAL-LICENSING.md
- tests/test_repository_maintenance_contract_v01.py

Purpose:

- reconcile direct dependency declarations;
- raise only the setuptools minimum floor to setuptools>=77.0.3 while
  retaining setuptools.build_meta, no exact pin, and no upper bound;
- establish exact AGPL-3.0-only metadata and canonical license text;
- provide a non-granting commercial licensing channel notice;
- test dependency and licensing consistency.

R-H1A does not redesign extras, lock dependencies, build a wheel, or make a
public-release claim.

### 13.2 R-H1B - Current Status and Living Release Spine

Candidate paths:

- README.md
- specs/machine_manifest_v0_25.json
- release/current_status_overlay_v01.json
- release/claim_to_evidence_index.md
- release/integration_seam_index.md
- release/one_command_gauntlet.md
- release/current_limitations.md
- release/current_release_notes.md
- tests/test_repository_release_spine_v01.py

Purpose:

- reconcile current status narrowly;
- add the explicit Machine Manifest current boundary;
- create current surfaces in IMPLEMENTATION_IN_PROGRESS, not PREFLIGHT_ONLY;
- create a metadata overlay and lightweight evidence indexes;
- preserve frozen Gate-1 JSON byte-identically;
- test status, non-claims, evidence references, and hashes.

### 13.3 R-H1C - Repomix Handoff Reproducibility

Candidate paths:

- repomix.handoff.config.json
- tools/generate_repomix_handoff_v01.py
- docs/repomix_handoff_reproducibility_v01.md
- tests/test_repomix_handoff_reproducibility_v01.py

Purpose:

- define deterministic handoff profiles;
- implement one generator and verifier;
- document local operation and failure modes;
- test names, ordering, exclusions, and untracked output policy.

R-H1C leaves all current status surfaces in IMPLEMENTATION_IN_PROGRESS.

### 13.4 R-H1D1 - Independent Read-Only Audit

R-H1D1 may create exactly one candidate path:

- docs/audit_reports/auditor_clean_clone_licensing_release_spine_reconciliation_r_h1_v01.log

R-H1D1:

- audits the committed R-H1A-through-R-H1C implementation basis;
- performs no repair;
- modifies no implementation, status, test, release, Manifest, README, or
  governance path;
- creates only the audit log after read-only inspection;
- records PASS or FAIL honestly;
- identifies the exact implementation_basis_commit;
- does not guess its own future audit_commit;
- does not transition current surfaces out of IMPLEMENTATION_IN_PROGRESS;
- does not close R-H1;
- does not authorize G2-C.

### 13.5 R-H1D2 - Owner Closure and Current-Status Synchronization

R-H1D2 may begin only after an accepted R-H1D1 audit PASS.

Candidate R-H1D2 paths:

- docs/clean_clone_licensing_release_spine_reconciliation_r_h1_checkpoint_v01.md
- AGENTS.md, active current-checkpoint block only
- README.md, bytes strictly inside the exact current-engineering-boundary
  markers only
- specs/machine_manifest_v0_25.json, exact Section 9 child-pointer allowlist
  only
- release/current_status_overlay_v01.json
- release/claim_to_evidence_index.md
- release/current_limitations.md
- release/current_release_notes.md

R-H1D2 must not change:

- pyproject.toml;
- LICENSE;
- COMMERCIAL-LICENSING.md;
- Repomix configuration, generator, documentation, or tests;
- implementation tests;
- runtime;
- schemas;
- frozen release JSON;
- historical audits or checkpoints;
- any non-current README history;
- README licensing and commercial-notice wording;
- README install and clean-clone commands;
- every README byte outside the exact marker-bounded block;
- any non-active AGENTS.md history.

R-H1D2 performs only:

- the R-H1 status transition from IMPLEMENTATION_IN_PROGRESS to CLOSED_PASS;
- accepted audit and checkpoint reference synchronization;
- README synchronization only inside the exact marker-bounded current-status
  block;
- population of known implementation_basis_commit and audit_commit values;
- use of NOT_SELF_RECORDED for closure_commit_identity;
- addition of R-H1 claims only after audit PASS;
- current limitation and engineering-note synchronization;
- owner closure;
- explicit preservation of G2-C NEXT / NOT_STARTED and NOT_AUTHORIZED.

R-H1D2:

- does not rewrite historical AGENTS.md sections;
- does not rewrite historical audits or checkpoints;
- does not authorize G2-C;
- records internal maintenance closure, not public release.

## 14. Explicitly Excluded Paths and Work

Unless a later owner instruction explicitly amends an accepted preflight,
R-H1 excludes:

- hedgehog/mode_router.py;
- all G2-C runtime work;
- RuntimeExecutionTopology implementation;
- PlanGraph migration or cleanup;
- Root, BSEP, DRS, AVF, or GT runtime changes;
- schemas/**;
- existing G2-A and G2-B runtime paths;
- existing G2-A and G2-B focused tests;
- release/completion_manifest.json;
- release/integration_seam_index.json;
- historical audits;
- historical checkpoints;
- full README rewrite;
- roadmap reconstruction from summaries;
- wheel or resource redesign;
- console-script redesign;
- lockfile or constraints-file introduction;
- exact build-backend pinning, a build-backend upper bound, or a
  build-backend redesign; the R-H1A setuptools>=77.0.3 minimum-floor
  correction remains authorized;
- SBOM generation;
- THIRD_PARTY_NOTICES.md without an obligation review;
- a generic NOTICE file;
- live Gemini or provider execution;
- Telegram execution;
- real connector execution;
- public-release claim;
- RC2 claim;
- Gate-2 closure claim;
- production-readiness claim;
- production-security-certification claim.

No historical audit may be changed to point to new bytes. New current evidence
must be additive.

## 15. Focused Future Validation Matrix

These commands are proposed for later authorized implementation validation.
They are not authorized or executed by this preflight.

### 15.1 Codex-safe focused validation candidates

    python3 -c 'import tomllib; tomllib.load(open("pyproject.toml","rb"))'

    python3 -m json.tool \
      specs/machine_manifest_v0_25.json >/dev/null

    python3 -m json.tool \
      release/current_status_overlay_v01.json >/dev/null

    python3 -m py_compile \
      tools/generate_repomix_handoff_v01.py

    PYTHONDONTWRITEBYTECODE=1 PYTHONPATH=. .venv/bin/python -m pytest -q \
      tests/test_repository_maintenance_contract_v01.py \
      tests/test_repository_release_spine_v01.py \
      tests/test_repomix_handoff_reproducibility_v01.py \
      tests/test_root_signer_isolation_v01.py

    PYTHONDONTWRITEBYTECODE=1 PYTHONPATH=. .venv/bin/python -m \
      demo.run_kernel_conformance_v01

    PYTHONDONTWRITEBYTECODE=1 PYTHONPATH=. .venv/bin/python -m \
      demo.run_living_gauntlet_v01

    git diff --check

Codex is not authorized by this preflight to run the full pytest suite.

### 15.2 First-owner validation matrix

| Assertion | First owning slice | Focused test |
| --- | --- | --- |
| Direct dependency names match the approved flat set | R-H1A | tests/test_repository_maintenance_contract_v01.py |
| Only cryptography is pinned, at 48.0.0 | R-H1A | tests/test_repository_maintenance_contract_v01.py and tests/test_root_signer_isolation_v01.py |
| setuptools.build_meta remains and the minimum is at least 77.0.3 without exact pin or upper bound | R-H1A | tests/test_repository_maintenance_contract_v01.py |
| Prepared/generated metadata contains the SPDX expression and license file | R-H1A | tests/test_repository_maintenance_contract_v01.py |
| LICENSE exact canonical source identity | R-H1A | tests/test_repository_maintenance_contract_v01.py |
| pyproject AGPL-3.0-only metadata | R-H1A | tests/test_repository_maintenance_contract_v01.py |
| COMMERCIAL-LICENSING.md remains informational and non-granting | R-H1A | tests/test_repository_maintenance_contract_v01.py |
| README license identifier agrees with pyproject and LICENSE | R-H1B | tests/test_repository_release_spine_v01.py |
| README points to the commercial notice without presenting a granted license | R-H1B | tests/test_repository_release_spine_v01.py |
| README current status is marker-bounded and exact | R-H1B | tests/test_repository_release_spine_v01.py |
| Machine Manifest differs only at exact allowlisted pointers | R-H1B, then R-H1D2 lifecycle transition | tests/test_repository_release_spine_v01.py |
| Current surfaces implement an allowed lifecycle state | R-H1B, then R-H1D2 lifecycle transition | tests/test_repository_release_spine_v01.py |
| Frozen release JSON hashes remain exact | R-H1B | tests/test_repository_release_spine_v01.py |
| Repomix covers every tracked R-H1 artifact | R-H1C | tests/test_repomix_handoff_reproducibility_v01.py |
| CLOSED_PASS has accepted audit and checkpoint references | R-H1D2 | tests/test_repository_release_spine_v01.py, unchanged since R-H1B |

R-H1D2 does not edit tests. R-H1B tests must therefore support and
fail-closed validate both IMPLEMENTATION_IN_PROGRESS and CLOSED_PASS from
their first committed version.

### 15.3 Owner-terminal validation candidates

Owner-terminal acceptance includes:

- full pytest;
- a local clean clone into an external temporary directory;
- a new virtual environment;
- editable installation;
- pip check;
- deterministic Kernel Conformance;
- deterministic Living Gauntlet;
- package metadata validation for the planned license fields;
- optional real local Repomix generation when Repomix is available;
- generated SHA256SUMS verification.

The external clean-clone sequence should be:

    git clone <owner-selected-local-or-remote-source> <external-temp-dir>
    cd <external-temp-dir>
    python3 -m venv .venv
    .venv/bin/python -m pip install -e .
    .venv/bin/python -m pip check
    PYTHONDONTWRITEBYTECODE=1 PYTHONPATH=. \
      .venv/bin/python -m demo.run_kernel_conformance_v01
    PYTHONDONTWRITEBYTECODE=1 PYTHONPATH=. \
      .venv/bin/python -m demo.run_living_gauntlet_v01

The placeholder source and destination are owner-terminal inputs, not commands
for Codex to guess. Clean-clone validation must not claim success until the
actual sequence completes.

No default validation invokes a provider, Telegram, connector, external DRS,
or real-world effect.

## 16. Focused Test Design

### 16.1 Repository maintenance contract

tests/test_repository_maintenance_contract_v01.py should prove:

- mandatory direct third-party imports map to declared distributions;
- retained dependency declarations remain;
- cryptography is exactly pinned at 48.0.0;
- the exact-version test and project declaration agree;
- pyproject parses;
- the build backend remains setuptools.build_meta;
- the setuptools requirement minimum is at least 77.0.3;
- the setuptools requirement has no exact pin and no upper bound;
- no additional build-system dependency appears;
- license metadata uses AGPL-3.0-only;
- license-files contains LICENSE;
- prepared or generated package metadata contains the expected SPDX license
  expression and license file;
- LICENSE exists, is referenced by metadata, and matches the exact canonical
  source identity recorded by R-H1A;
- COMMERCIAL-LICENSING.md is informational and non-granting;
- COMMERCIAL-LICENSING.md states that separate terms require a separately
  executed written agreement and that no owner-designated contact channel is
  currently published;
- COMMERCIAL-LICENSING.md contains no invented email, website, form, platform,
  placeholder contact, commercial-agreement claim, title claim, relicensing
  claim, patent-clearance claim, or legal-review claim;
- prohibited public-release, RC2, production-readiness, and security claims
  are absent from the R-H1A licensing and project-metadata surfaces.

The test must not attempt to resolve or import every transitive package.
R-H1A does not modify README.md, so this test must not require README licensing
language that is first owned by R-H1B.

### 16.2 Repository release-spine contract

tests/test_repository_release_spine_v01.py should prove:

- README current status matches the explicit current boundary;
- README contains exactly one ordered pair of the exact current-engineering
  boundary markers;
- README uses AGPL-3.0-only consistently with pyproject.toml and LICENSE;
- README points to COMMERCIAL-LICENSING.md without presenting it as a granted
  license or an existing commercial agreement;
- current_engineering_boundary_v01 exists and is exact;
- workstream status is either IMPLEMENTATION_IN_PROGRESS with open,
  unaudited, unclosed geometry or CLOSED_PASS with closed, audited geometry;
- PREFLIGHT_ONLY is rejected as a future repository current-status value;
- implementation_was_explicitly_authorized, implementation_open,
  closure_claimed, and independent_audit_passed satisfy their independent
  lifecycle meanings;
- accepted_pre_r_h1_base_commit is exact and no generic head field substitutes
  for it;
- accepted_pre_r_h1_checkpoint and accepted_pre_r_h1_audit are exact;
- unknown commit identities are null and known identities are exact;
- closure_commit_identity is NOT_SELF_RECORDED only in CLOSED_PASS;
- metadata_sync_only and manifest_does_not_override_human_passport remain true;
- baseline Manifest bytes are read with git show from the exact accepted
  pre-R-H1 base commit and match the exact accepted SHA-256;
- the current parsed Manifest, after removing only
  current_engineering_boundary_v01, equals the parsed accepted baseline;
- CLOSED_PASS reads the exact implementation_basis_commit Manifest from Git
  and permits only the literal R-H1D2 child-pointer differences;
- unavailable required Git objects fail explicitly without skip or fetch;
- selected historical nested objects remain separately preserved;
- frozen release JSON hashes are exact;
- the current overlay parses and remains non-authoritative;
- every accepted current claim has evidence and a limitation;
- Gate 2 is not closed;
- G2-C is not started or authorized;
- public release, RC2, production, and security certification remain
  unclaimed;
- each release-spine path has its bounded role;
- no current document says "G2-C is in development".

For CLOSED_PASS, the test also removes the exact marker-bounded block from
README bytes at implementation_basis_commit and from current README bytes,
then asserts every remaining byte is identical. The complete closed marker
block is validated separately.

The test must target explicit current fields and an allowed lifecycle state.
It must not reject all historical status strings, treat JSON key ordering as
authority, or hard-code PREFLIGHT_ONLY as the implementation state.

### 16.3 Repomix reproducibility contract

tests/test_repomix_handoff_reproducibility_v01.py should prove:

- exact profile and output names;
- exact deterministic profile and checksum ordering;
- required secret and generated-output exclusions;
- local runtime log directories are excluded without a recursive all-.log
  exclusion;
- only explicitly selected committed public-safe audit logs are included;
- broad docs/** inclusion is prohibited;
- no broad implicit public-safe audit inclusion;
- _audit_exports policy is ignored and untracked;
- dirty-worktree behavior fails closed by default;
- dry validation creates no outputs;
- Repomix absence is explicit and non-installing;
- generator source contains no network, stage, commit, or push operation;
- roadmap companion documents are not reconstructed;
- every tracked R-H1 governance, implementation-test, audit, checkpoint, and
  release-spine artifact maps to an intended handoff profile;
- absent future R-H1 audit and checkpoint paths remain explicit
  NOT_YET_PRESENT profile obligations before closure;
- checksum verification rejects missing, extra, reordered, or altered output.

## 17. Audit and Closure Law

### 17.1 R-H1D1 independent read-only audit

After authorized R-H1A through R-H1C implementation is committed, R-H1D1
audits that exact implementation_basis_commit.

Before its audit-log write, R-H1D1 is fully read-only. It performs no repair
and modifies no implementation, status, test, release, Manifest, README, or
governance path.

The audit must verify:

- exact changed-path scope for R-H1A, R-H1B, and R-H1C;
- exact frozen release hashes;
- dependency/import consistency;
- cryptography version-policy consistency;
- canonical license source description and exact source-byte SHA-256;
- licensing file and metadata consistency;
- current-status consistency across README, Machine Manifest, and overlay;
- all current surfaces remain IMPLEMENTATION_IN_PROGRESS during R-H1D1;
- historical Manifest fields and historical evidence remain unchanged;
- exact Machine Manifest add-only and preservation-test evidence;
- clean-clone evidence from an actually executed external checkout;
- no-network deterministic Kernel Conformance evidence;
- no-network deterministic Living Gauntlet evidence;
- Repomix static-contract evidence;
- R-H1 artifact coverage in the intended Repomix profiles;
- real generated-output and SHA256SUMS verification when Repomix is available,
  or an explicit unavailable-tool limitation otherwise;
- no public release, RC2, Gate-2 closure, production, or security claim;
- no runtime or G2-C implementation change.

Only after all read-only gates pass may R-H1D1 create:

- docs/audit_reports/auditor_clean_clone_licensing_release_spine_reconciliation_r_h1_v01.log

The audit records PASS or FAIL honestly. It does not close R-H1, does not
change current status, and does not authorize G2-C.

### 17.2 R-H1D2 owner closure

R-H1D2 may begin only after the R-H1D1 audit artifact has been accepted and
committed, making audit_commit known.

R-H1D2:

- creates the compact R-H1 checkpoint;
- changes only the active AGENTS.md current-checkpoint block;
- synchronizes README only inside the exact current-engineering-boundary
  markers;
- applies only the exact Section 9 Manifest child-pointer transitions;
- synchronizes the current overlay, claim index, limitations, and engineering
  notes;
- records exact implementation_basis_commit and audit_commit values;
- uses NOT_SELF_RECORDED for closure_commit_identity;
- transitions R-H1 from IMPLEMENTATION_IN_PROGRESS to CLOSED_PASS;
- adds R-H1 claims only after accepted audit PASS;
- preserves every historical document and historical status object;
- preserves G2-C as NEXT / NOT_STARTED and NOT_AUTHORIZED.

The README closure guard reads README.md from implementation_basis_commit,
removes the exact marker-bounded block from basis and current bytes, and
requires all remaining bytes to be identical. It separately validates the
complete CLOSED_PASS marker block. Licensing wording, the AGPL identifier,
commercial-notice wording, install commands, and clean-clone commands are
therefore frozen after R-H1D1 audits the implementation basis.

R-H1D2 performs no implementation repair and changes no implementation test.
If closure synchronization reveals an implementation defect, closure stops
for a separately authorized repair cycle; R-H1D2 does not repair it.

After R-H1 closes, the next permitted engineering operation remains a separate
G2-C read-only inventory and preflight sequence. R-H1 closure does not start
G2-C.

## 18. Implementation Acceptance Gates

A later implementation authorization must remain within one internal slice at
a time and must preserve all excluded paths.

### 18.1 R-H1A acceptance

- Only explicitly authorized R-H1A paths change.
- The declared dependency-name set exactly matches the approved R-H1 set.
- Only cryptography is version-pinned in R-H1, at cryptography==48.0.0.
- Observed local versions of other distributions are not converted into
  version pins.
- cryptography==48.0.0 agrees with focused tests.
- pyproject.toml changes the setuptools minimum from 68 to at least 77.0.3.
- The backend remains setuptools.build_meta.
- The setuptools requirement is not exact, has no upper bound, and introduces
  no other build-system dependency.
- Before any LICENSE or license-metadata mutation, the implementation report
  identifies the exact canonical source and its exact source-byte SHA-256.
- LICENSE bytes match that exact canonical source.
- Missing authorized canonical source access stops R-H1A before mutation.
- PEP-639 license fields are exact and coherent.
- Prepared or generated package metadata contains the AGPL-3.0-only SPDX
  expression and LICENSE file.
- COMMERCIAL-LICENSING.md remains non-granting and publishes no invented or
  placeholder contact channel.
- COMMERCIAL-LICENSING.md makes no commercial-agreement, title, relicensing,
  patent-clearance, or legal-review claim.
- README is not changed by R-H1A.
- R-H1A tests do not require future README licensing language.
- No dependency group redesign or lockfile appears.
- Focused maintenance tests pass.

### 18.2 R-H1B acceptance

- Only explicitly authorized R-H1B paths change.
- README repair remains narrow.
- R-H1B creates exactly one complete README current-status block between the
  exact current-engineering-boundary markers.
- R-H1B owns install, clean-clone, licensing, and commercial-notice wording
  outside that block.
- README licensing agrees with pyproject.toml and LICENSE and treats
  COMMERCIAL-LICENSING.md as a non-granting information channel.
- Machine Manifest mutation is add-only at
  /current_checkpoint_status/current_engineering_boundary_v01.
- No pre-existing Machine Manifest pointer changes.
- Historical and architectural Manifest structures remain parsed-value
  identical after removal of only the added pointer.
- Current Manifest, README, and overlay status is
  IMPLEMENTATION_IN_PROGRESS, not PREFLIGHT_ONLY.
- The four independent lifecycle booleans have exact in-progress geometry.
- Frozen release JSON hashes remain exact.
- New release-spine documents remain indexes, not duplicated implementation.
- Gate 2 and G2-C non-claims remain exact.
- Focused release-spine tests pass and already support the later CLOSED_PASS
  conditional geometry without requiring a test edit in R-H1D2.

### 18.3 R-H1C acceptance

- Only explicitly authorized R-H1C paths change.
- No handoff output is tracked.
- Profile and output order are deterministic.
- Secret exclusions are explicit.
- Every tracked R-H1 artifact maps to at least one intended handoff profile.
- Planned audit and checkpoint coverage is explicit before those paths exist.
- The generator has no network, staging, commit, or push behavior.
- Static and dry-validation tests pass.
- Real generation is separately owner-controlled when Repomix is available.
- Current status remains IMPLEMENTATION_IN_PROGRESS.

### 18.4 R-H1D1 acceptance

- Audit is independent and non-repairing.
- The exact committed R-H1A-through-R-H1C implementation_basis_commit is
  audited.
- Clean-clone evidence is actual, not planned.
- Frozen evidence remains unchanged.
- Machine Manifest, README, overlay, release spine, tests, implementation, and
  governance remain unchanged by R-H1D1.
- Exactly one audit log is created after all read-only gates pass.
- Audit PASS or FAIL is recorded honestly.
- Current status remains IMPLEMENTATION_IN_PROGRESS.
- R-H1 is not closed.
- No G2-C implementation or authorization is introduced.
- No public-release, RC2, Gate-2 closure, production, or security claim is
  introduced.

### 18.5 R-H1D2 acceptance

- Accepted R-H1D1 audit PASS and exact audit_commit are prerequisites.
- Only the exact R-H1D2 path list changes.
- The checkpoint is compact and cross-bound to the accepted audit.
- AGENTS.md changes only in the active current-checkpoint block.
- README changes only inside the exact current-engineering-boundary markers.
- README licensing, AGPL identifier, commercial-notice wording, install
  commands, clean-clone commands, project description, historical sections,
  and every other byte outside the markers remain identical to
  implementation_basis_commit.
- The README boundary guard removes the marker block from basis and current
  bytes, compares all remaining bytes exactly, and separately validates the
  complete closed-state block.
- Manifest changes only at the exact Section 9 R-H1D2 child pointers.
- implementation_basis_commit and audit_commit are exact known commits.
- closure_commit_identity is NOT_SELF_RECORDED.
- Workstream status transitions to CLOSED_PASS.
- implementation_open is false, closure_claimed is true, and
  independent_audit_passed is true.
- Implementation tests and R-H1A/R-H1C implementation paths remain unchanged.
- No historical evidence changes.
- No G2-C implementation or authorization is introduced.
- No public-release, RC2, Gate-2 closure, production, or security claim is
  introduced.

### 18.6 R-H1D2 post-synchronization validation

After every authorized closure synchronization edit, R-H1D2 must run:

    python3 -m json.tool \
      specs/machine_manifest_v0_25.json >/dev/null

    python3 -m json.tool \
      release/current_status_overlay_v01.json >/dev/null

    PYTHONDONTWRITEBYTECODE=1 PYTHONPATH=. .venv/bin/python -m pytest -q \
      tests/test_repository_maintenance_contract_v01.py \
      tests/test_repository_release_spine_v01.py \
      tests/test_repomix_handoff_reproducibility_v01.py \
      tests/test_root_signer_isolation_v01.py

    shasum -a 256 release/completion_manifest.json
    shasum -a 256 release/integration_seam_index.json

    git diff --check

The observed frozen hashes must remain:

- release/completion_manifest.json:
  02ffac0d78df768f91df0bb06bdd15ec463dbe5ccea6ef82b7022146819f3466
- release/integration_seam_index.json:
  c29c2ff873c8b448d8825c3288918e980eab3d65a5114762d2e3fbe5b1206231

If any closure-focused validation fails:

- CLOSED_PASS is not claimed;
- no closure commit is created;
- R-H1D2 does not repair implementation;
- work returns to a separately authorized repair cycle.

The full pytest suite remains owner-terminal validation. This preflight does
not authorize Codex to run it.

## 19. Path-Scope Ledger

### 19.1 R-H1A candidate paths

- pyproject.toml, limited to the approved flat dependency names, the
  setuptools>=77.0.3 minimum floor with setuptools.build_meta unchanged, and
  the exact PEP-639 license fields
- LICENSE
- COMMERCIAL-LICENSING.md
- tests/test_repository_maintenance_contract_v01.py

### 19.2 R-H1B candidate paths

- README.md
- specs/machine_manifest_v0_25.json
- release/current_status_overlay_v01.json
- release/claim_to_evidence_index.md
- release/integration_seam_index.md
- release/one_command_gauntlet.md
- release/current_limitations.md
- release/current_release_notes.md
- tests/test_repository_release_spine_v01.py

Machine Manifest permission in R-H1B is add-only at
/current_checkpoint_status/current_engineering_boundary_v01.

### 19.3 R-H1C candidate paths

- repomix.handoff.config.json
- tools/generate_repomix_handoff_v01.py
- docs/repomix_handoff_reproducibility_v01.md
- tests/test_repomix_handoff_reproducibility_v01.py

### 19.4 R-H1D1 candidate path

- docs/audit_reports/auditor_clean_clone_licensing_release_spine_reconciliation_r_h1_v01.log

R-H1D1 creates only this path and modifies nothing.

### 19.5 R-H1D2 candidate paths

- docs/clean_clone_licensing_release_spine_reconciliation_r_h1_checkpoint_v01.md
- AGENTS.md, active current-checkpoint block only
- README.md, bytes strictly inside the exact current-engineering-boundary
  markers only
- specs/machine_manifest_v0_25.json, exact Section 9 child-pointer allowlist
  only
- release/current_status_overlay_v01.json
- release/claim_to_evidence_index.md
- release/current_limitations.md
- release/current_release_notes.md

R-H1D2 modifies no implementation test and no R-H1A or R-H1C implementation
path. It modifies no README byte outside the exact marker-bounded block.

### 19.6 Permanently frozen during R-H1

- release/completion_manifest.json
- release/integration_seam_index.json
- historical audits and checkpoints
- runtime, demos, schemas, and existing focused tests outside explicit
  maintenance test creation
- G2-A and G2-B accepted implementation and proof paths
- hedgehog/mode_router.py

No pre-existing Machine Manifest field is authorized for modification. No
path outside a separately authorized slice list may change.

This ledger is planning scope only. No listed future path is authorized by this
document alone.

## 20. Final Non-Claims and Authorization State

R-H1 remains a maintenance reconciliation plan. It does not alter the accepted
authority model, runtime, Gate status, or public posture.

This uncommitted preflight is in PREFLIGHT_ONLY. That statement is local to
this planning document:

- accepted_pre_r_h1_base_commit is
  3785d67e9d33adf145a3f6f60981abf38767b25d;
- preflight_commit is not yet populated and is not guessed here;
- implementation_basis_commit is not yet known;
- audit_commit is not yet known;
- closure_commit_identity is not yet applicable;
- implementation_was_explicitly_authorized is false;
- implementation_open is false;
- closure_claimed is false;
- independent_audit_passed is false.

When separately authorized, R-H1B current repository surfaces begin at
IMPLEMENTATION_IN_PROGRESS. Only R-H1D2 may transition them to CLOSED_PASS
after accepted R-H1D1 audit PASS.

Exact final preflight state:

- Gate 1: CLOSED_PASS.
- Two-Domain All-Real Sealed Evidence Program: CLOSED_PASS.
- G2-A: CLOSED_PASS.
- G2-B: CLOSED_PASS.
- Gate 2: NOT_CLOSED.
- G2-C: NEXT / NOT_STARTED.
- G2-C implementation: NOT_AUTHORIZED.
- Public release: NOT_CLAIMED.
- RC2: NOT_CLAIMED.
- Production readiness: NOT_CLAIMED.
- Production security certification: NOT_CLAIMED.
- Standalone wheel completeness: NOT_CLAIMED.
- Runtime architecture changed by this preflight: false.
- R-H1 implementation authorized by this preflight: false.
- R-H1D1 started: false.
- R-H1D2 started: false.

This R-H1 preflight is guardian-accepted and eligible for a separately
owner-authorized one-path preflight commit. It has not yet been committed, and
preflight_commit remains unpopulated.

R-H1 implementation remains unauthorized. No R-H1 slice has started. G2-C
remains NEXT / NOT_STARTED and NOT_AUTHORIZED. Implementation requires a
separate explicit owner authorization for the applicable internal R-H1 slice.
