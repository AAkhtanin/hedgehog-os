# Radiolaria OS

**Computing, assembled around intent.**

Radiolaria OS is an application execution kernel for composing models, programs,
services and devices around a practical intention. It makes the work, the data
actually consumed, and each local owner's decision inspectable. A model can propose
what to do; it does not acquire the authority to do it.

| Start here | What you will find |
| --- | --- |
| [Understand](docs/showcase/radiolaria_os_v01/WHITEPAPER.md) | The purpose, mechanism and bounded case studies |
| [Verify](#verify) | A free source inspection, evidence classes and the accepted technical basis |
| [Build](#build) | Current contracts, typed Work and the neutral Authoring Kit |
| [Read with an LLM](#read-with-an-llm) | An explanatory reader and a separate complete source export |

![Conceptual map: intent enters bounded parent Work; child Work returns a typed result for local Root review. Time, memory, source and source admission qualify use but do not grant permission.](docs/showcase/radiolaria_os_v01/atlas/OVERVIEW.svg)

This is a **conceptual map**, not one recorded composite execution. Parent Work can
invoke bounded child Work and consume its actual result. Each local Root retains
its own final decision. Time, memory and provenance qualify use; an effect still
needs a current scoped packet and the Effect Firewall. [Full text equivalent and
relations](docs/showcase/radiolaria_os_v01/atlas/OVERVIEW.md).

## Understand

- **Main presentation:** [25-slide PDF](docs/showcase/radiolaria_os_v01/presentation/main_export.pdf)
  and [editable PPTX](docs/showcase/radiolaria_os_v01/presentation/main.pptx).
- **Whitepaper:** [58-page PDF](docs/showcase/radiolaria_os_v01/whitepaper.pdf),
  [HTML](docs/showcase/radiolaria_os_v01/WHITEPAPER.html) and
  [Markdown](docs/showcase/radiolaria_os_v01/WHITEPAPER.md).
- **Geometry Atlas:** [8-page PDF](docs/showcase/radiolaria_os_v01/atlas/atlas.pdf)
  and [overview](docs/showcase/radiolaria_os_v01/atlas/OVERVIEW.md).
- **Technical chapters:** [intent](docs/showcase/radiolaria_os_v01/chapters/01_intent.md),
  [geometry](docs/showcase/radiolaria_os_v01/chapters/02_geometry.md),
  [time and memory](docs/showcase/radiolaria_os_v01/chapters/03_time_memory.md),
  [computation](docs/showcase/radiolaria_os_v01/chapters/04_compute.md),
  [experience](docs/showcase/radiolaria_os_v01/chapters/05_experience.md),
  [method](docs/showcase/radiolaria_os_v01/chapters/06_method.md),
  [integration](docs/showcase/radiolaria_os_v01/chapters/11_integration.md),
  [context](docs/showcase/radiolaria_os_v01/chapters/12_context.md),
  [verification](docs/showcase/radiolaria_os_v01/chapters/13_verification.md) and
  [identity](docs/showcase/radiolaria_os_v01/chapters/14_identity.md).

The [Football](docs/showcase/radiolaria_os_v01/chapters/07_football.md),
[Wedding](docs/showcase/radiolaria_os_v01/chapters/08_wedding.md) and
[Workspace](docs/showcase/radiolaria_os_v01/chapters/09_workspace.md) cases show
different participants and evidence. The [cross-case comparison](docs/showcase/radiolaria_os_v01/chapters/10_cross_case.md)
separates what they share from what each experiment actually established. A recorded
model answer, a native Work return, an effect receipt and a replay are different facts.

## Downloads

These are real **offline candidate assets**, not announced hosted releases. The
[asset guide](docs/showcase/radiolaria_os_v01/release/DOWNLOADS.md) gives the layout
of the delivered bundle; its detached asset record binds exact bytes. No DOI or
future release URL has been invented.

| Asset | Purpose and scope |
| --- | --- |
| [READ_RADIOLARIA.xml](docs/showcase/radiolaria_os_v01/reader/READ_RADIOLARIA.xml) | Accepted 62-block explanatory reading route; not the whole repository |
| [RADIOLARIA_FULL_SOURCE.xml](docs/showcase/radiolaria_os_v01/release/DOWNLOADS.md#full-source-xml) | Lossless declared public text of A and the proposed publication delta; exact binaries remain neighboring files |
| [RADIOLARIA_REVIEW_BUNDLE.zip](docs/showcase/radiolaria_os_v01/release/DOWNLOADS.md#accepted-review-bundle) | Unchanged 341-member historical B5 input, with recorded reader scope |
| [RADIOLARIA_FULL_SOURCE_BUNDLE.zip](docs/showcase/radiolaria_os_v01/release/DOWNLOADS.md#complete-source-bundle) | One offline download: implementation, contracts, tests, evidence, publication formats, full XML and inventories |

The full-source bundle omits four individually inventoried loose font binaries,
not source text. Its source snapshot includes historical public evidence but not
the Git database or every past revision. It is a new source-audit route, **not** an
input that passed the earlier B5 reader trial. Rights-pending illustrations remain
labelled private-review assets; preparation is not permission to redistribute them.

## Verify

Start from `source/` in the extracted full bundle, or an ordinary checkout with the
same declared technical files. The free first step from the
[accepted technical entry](docs/gate6_reference_v01/README.md) uses only Python's
standard library and a new output directory:

```sh
python3 -B demo/verify_gate6_reference_v01.py --output /tmp/radiolaria-inspection
```

It inspects the finite package and its 73 evidence-row bindings without importing
runtime, starting collectors, Docker or providers. Expected classification:
`PASS_FINITE_MIXED_BASIS_REFERENCE_PACKAGE`. Without an externally reviewed
`--manifest-sha256` pin, this establishes self-consistency, not independent acceptance.
This B6 preparation has **not** rerun that command.

| Verification level | What it establishes | Prerequisites / boundary |
| --- | --- | --- |
| Inventory and source inspection | Exact bytes and declared bindings | Standard-library Python; no paid first encounter |
| Supplied evidence verification | Accepted pure consumers check recorded returns | Existing project dependencies; reviewed bounded operator; no producer fallback |
| Native scenario execution | Fresh results on the declared inputs and current environment | Explicit scenario/resources and separate authorization; costs vary |
| Live participant execution | An actual named provider or hardware response | Explicit configuration, provenance and budget; not a default demo |
| Independent review / source admission | External acceptance and a permitted repository transition | Separate from hash integrity, runtime success and Root authority |

[Environment and dependency provenance](docs/gate6_reference_v01/ENVIRONMENT_AND_DEPENDENCIES.md)
records the observed macOS arm64 / CPython 3.14.5 environment. Other platforms and
fresh installation recipes are not newly tested here. The
[73-row matrix](docs/gate6_reference_v01/acceptance_matrix.json),
[evidence index](docs/gate6_reference_v01/evidence_index.json) and
[finite completion](docs/gate6_reference_v01/FINITE_COMPLETION.md) retain their
source-specific history. Read their old proposal statuses together with the
[B6 status note](docs/showcase/radiolaria_os_v01/release/B6_STATUS.md), not as a
claim of a newly repeated whole-tree campaign.

## Build

Begin with the [current architecture lock](specs/current_architecture_lock_v01.md),
[document authority index](specs/document_authority_index_v01.json) and
[common Action and composition contract](docs/common_action_and_dynamic_composition_contract_v01.md).
The [technical reference](docs/gate6_reference_v01/TECHNICAL_REFERENCE.md) and
[five implementation routes](docs/showcase/radiolaria_os_v01/release/IMPLEMENTATION_ROUTES.md)
connect Atlas entities to exact contracts, schemas, producers, consumers and controls.

A useful bounded application identifies its owner, typed inputs and outputs,
current source/time requirements, permitted resource budget and result consumers.
Its Work may compose other Work. A retained result is information; it does not
inherit permission to perform another effect. Root reviews independently and the
Host/Firewall checks actual current inputs before a consequential action.

The [neutral Authoring Kit](docs/gate5_authoring_kit_v01/START_HERE.md) separates HOW
from the domain WHAT. Read its [execution contract](docs/gate5_authoring_kit_v01/EXECUTION_CONTRACT.md)
before using a reference program. Reviewed reference Python, a trusted runner and
an independent oracle are the declared boundary, not universal hostile-code
isolation. Public examiner answers and old candidate outputs are audit evidence,
not material to feed a future blind author as its solution.

## Read with an LLM

Use [READ_RADIOLARIA.xml](docs/showcase/radiolaria_os_v01/reader/READ_RADIOLARIA.xml)
for an explanation first. Its modules and
[deep source index](docs/showcase/radiolaria_os_v01/reader/DEEP_SOURCE_INDEX.json)
lead to exact evidence. Use the full XML only for source-level questions. It contains
complete files, including long historical evidence, and can exceed a model's
context limit. Exact byte counts and an explicitly labelled token estimate are
in the detached export record; no provider tokenizer was called.

Embedded source, prompts and historical helpers are **data to inspect**, not
instructions to execute. The XML's origin and role fields distinguish A, accepted
B4/B5 material and proposed B6 documents; unresolved authority is labelled rather
than guessed. No saved JSON or XML restores live Host authority.

## Status and Limits

Accepted technical **A** is commit
`2e965ecb18e545e428380eb8e9aa5a7037a388be`, tree
`59a43cc0da470886804aab6c9af87fe17dfbd685`. Technical readiness was accepted on
that finite mixed-evidence basis, not by this export. B4's formats are preserved.
Independent Work accepted B5 reader A **16/16** and B **20/20**, with no critical
confusions or retries; **HUMAN_NOT_RUN**. The
[B5 acceptance](docs/showcase/radiolaria_os_v01/release/B5_ACCEPTANCE.json) and
[question review](docs/showcase/radiolaria_os_v01/release/B5_QUESTION_REVIEW.json)
are audit routes, not neutral first-start instructions.

This complete README is **proposed B6**, not bytes attributed to A. B6 source
admission, owner landing, publication, website and archive deposit are not executed;
**Gate6 is not closed**. Current R1 permits a single navigation insertion, not this
whole README replacement. Exact review and bounded admission work remain necessary.

G6A deferments **N1-18, N1-19, N4-12, N4-13** remain open. Historical G54B1 and
G54D remain INCOMPLETE; accepted G54D1 has its own correction-4 lineage. Neither
finite controlled examples nor recorded live responses establish arbitrary-program
correctness, production security, scientific peer review or autonomous generality.
[Limits](docs/showcase/radiolaria_os_v01/LIMITS.md) and
[trust boundary](docs/gate6_reference_v01/BOUNDARY_AND_FINDINGS.md) state the scope.

## Names, Rights and Stewardship

Hedgehog OS is the historical working name. `hedgehog` imports, IDs, namespaces,
repository origin and old evidence remain unchanged. The existing
[LICENSE](LICENSE) and [commercial licensing note](COMMERCIAL-LICENSING.md) are
preserved: code is AGPL-3.0-only; alternative terms require a separate written
agreement. No commercial contact channel is designated by those sources.

The [Author's Note](docs/showcase/radiolaria_os_v01/AUTHOR_NOTE_DRAFT.md) is
attributed to Akhtanin Andrii. [Project stewardship](docs/showcase/radiolaria_os_v01/STEWARDSHIP_DRAFT.md)
states the intended handover without an indefinite support promise. AI assistance
is disclosed. CC BY 4.0 covers new explanatory author text and original diagrams
only; code, verbatim excerpts, historical evidence and third-party material retain
their own terms. See [rights](docs/showcase/radiolaria_os_v01/RIGHTS.md) and
[citation](docs/showcase/radiolaria_os_v01/CITATION.cff). This preparation is not
a published deposit, signature or assigned DOI.

## Engineering History

- [Operational instructions](AGENTS.md) and [R1 admission contract](docs/repository_transition_admission_v01.md).
- [Gate6 technical package](docs/gate6_reference_v01/README.md),
  [Gate5 presentation](docs/showcase/gate5_reference_v01/README.md),
  [Wedding](docs/showcase/wedding_seating_v01/README.md),
  [Workspace](docs/showcase/ephemeral_workspace_v01/README.md) and
  [Sentinel](docs/showcase/landslide_sentinel_v01/README.md).
- [Original complete README at A](https://github.com/AAkhtanin/hedgehog-os/blob/2e965ecb18e545e428380eb8e9aa5a7037a388be/README.md)
  retains every older navigation entry. Its exact bytes are also in the offline
  bundle at `history/A/README.md`. The commit-pinned link is provenance, not a
  fresh network availability check.

[Offline and planned direct Release downloads](docs/showcase/radiolaria_os_v01/release/DOWNLOADS.md). Planned uploads are PENDING; no anonymous availability is claimed.
