# Reviewed repository transitions v0.1

This R1 bootstrap is a source-admission maintenance proposal. Independent Work
review of its exact raw bytes and a separate owner landing are still required.
It does not close a functional Gate or confer Root, Host or effect authority.

## Three distinct facts

The immutable accepted implementation is commit
`71e166ccb88b024fd3ca3a25e17da110c6db1a3f`, parent
`d199199a578c078c913a2381f595549175bd9235`, tree
`71e0438a4ef8532a3047a6e87061240d5b958a31`. Its original 59-path change and 1,135
files remain historical evidence. A current repository transition is checked
against its own independently reviewed immediate base. Semantic closure remains
the separately recorded independent review. Source checks do not award it.

## External review context

The raw manifest SHA-256 and policy identity come from a frozen independent
review and owner instruction. Neither is inferred from candidate metadata,
remote HEAD, a manifest's own declaration or a successful previous test.
The context is an operator-supplied trust input, not a digital signature or
proof of a separate reviewer. Platform approval remains independent.

The read-only resolver accepts an explicit absolute context path, the
`HEDGEHOG_REPOSITORY_REVIEW_CONTEXT_V01` environment path, or the narrowly named
`reviewed_repository_transition_v01/context.json` file inside the real Git
directory. Linked worktrees use their own actual Git directory. Multiple
sources must contain identical records. Symlinks, malformed records, duplicate
JSON keys and conflicting sources refuse. The guard and binder never write,
refresh, repair or invent context.

An explicit fresh-clone invocation is:

```sh
HEDGEHOG_REPOSITORY_REVIEW_CONTEXT_V01=/absolute/review/context.json \
  /absolute/python /trusted/admitted/tools/check_active_architecture_authority_v01.py \
  --root /absolute/candidate
```

Use the previously admitted enforcement code to inspect ordinary engineering
proposals. A candidate cannot select an alternative verifier. The policy ID is
SHA-256 of the canonical identity map for these complete raw files: this
contract, `tools/reviewed_repository_transition_v01.py`, the public architecture
guard and `tests/test_repository_release_spine_v01.py` (the actual import-time
binder). Each identity includes regular-file type, exact Git mode, size and
SHA-256. No source byte, self-literal, function or table is excluded.
BOOTSTRAP uses separately reviewed new code; subsequent transitions require
these bytes to equal their admitted base and the external policy pin.

## Closed data formats

The schema identifier is `reviewed_repository_transition_v01`. Unknown fields
and duplicate keys refuse at every structural record.

Manifest keys are `schema`, `repository`, `policy_id`, `kind`,
`accepted_basis`, `base`, `previous`, `governed_namespaces`, `commit_message`,
and `ledger`. Repository is exactly `AAkhtanin/hedgehog-os`. The accepted basis
has `commit`, `parent`, `tree`; base has `commit`, `tree`. Previous is null for
bootstrap or an externally bound `manifest_sha256`, `commit`, `tree`,
`policy_id` record for the prior admitted transition. No future commit is in
the manifest. The ledger is the complete list of `path`, `action`, `pre`,
`post` rows. Only `A` and `M` are supported. Every non-null image is a closed
`type`, `mode`, `bytes`, `sha256` record. Types are regular files; modes are
`100644` or `100755`. Additions have null preimages. Relative paths must be
unique, case-fold unique, safe and outside Git internals.

Context keys are `schema`, `repository`, `policy_id`, `kind`,
`accepted_basis`, `base`, `previous`, `manifest`, `state`, `finalized`,
`purpose`. Manifest binding is an absolute `path` and expected raw `sha256`.
Purpose is either `INDEPENDENT_REVIEW` or `DISPOSABLE_TEST_ONLY`; neither is
self-authenticating and neither changes validation rules. Proposed owner
contexts in R1 evidence are marked NOT_AUTHORIZED_FOR_OWNER_USE in a containing
review record, and are not installed in owner Git state.

`PREPARED` requires null finalized data and allows only the complete reviewed
unstaged proposal, complete staged proposal or exact immediate commit on base.
Before commit, origin/main equals base; for the exact child it may equal base
or that child. `FINALIZED` additionally binds the actual commit and tree,
rejecting alternative equal-tree children. Local admission and remote
publication are separate: the verifier reports remote publication NOT_CHECKED.

An authorized later landing helper may atomically replace local context only
after verifying the same frozen manifest/policy and actual postcommit state.
It must preserve the previous record under a unique recovery name, write a
temporary ordinary file in that Git directory, flush it and use atomic rename.
If interrupted after commit but before finalization, inspect that exact
immediate commit with the same PREPARED context, then finalize its actual
commit/tree. Do not regenerate approval or infer success from missing context.
No owner context or finalizer is executed in the R1 preparation task.

## Transition kinds

DOCUMENTATION adds one or more new versioned inert capsules under exact
`docs/showcase/<name>_v<number>` namespaces. Every added path is ledger-bound;
prior capsules cannot change. An optional README navigation modification is
exactly one plain English relative link line inserted without changing other
bytes. No runtime, guard, policy, test or authority metadata edit is allowed.
Code copies in capsules are inert data and may not be executable.

ENGINEERING is a separately reviewed exact source transition from the latest
admitted tip. It cannot modify the enforcement chain, governance controls,
prior capsules, README navigation or Git configuration. Documentation authority
cannot authorize engineering. The preserved Work/reference and release
registration identities remain mandatory; changing those invariants requires
a separately reviewed maintenance instruction, not an ordinary transition.

BOOTSTRAP is the one R1 maintenance proposal on the accepted implementation.
Its controls are the enumerated R1 allowlist and the exact sealed 521-file Gate
3 capsule. It adds only the fixed `repository_transition_admission_v01` metadata
record; every historical key/value remains intact. Its detached manifest covers
all raw postimages including enforcement code. It is pending independent review.

## Current-state checks

Both historical and reviewed inputs pass real current Git checks: branch,
origin repository, index flags and operation markers. Historical G37 criteria
remain exact on genuine historical objects. Successors additionally require
external context, base/parent/tree/lineage, exact status/actions, whole index
stage/blob/mode agreement, complete current file identities and protected
neighbors. Missing context is REVIEW_CONTEXT_REQUIRED.

The checked inventory is tracked files plus nonignored untracked files. Each
declared publication namespace is recursively checked including ignored files.
The verifier checks policy input file types and symlink parents explicitly.
It does not claim to inventory unrelated ignored environments or caches.
Git-object inventories may be cached by immutable object identity; current
filesystem, context, index, metadata and operation checks are never cached.

Repository Git mode and local POSIX read/write permissions are distinct.
Regular repository files may retain POSIX 0400, 0600 or 0644 while their Git
identity remains 100644; POSIX 0755 maps to Git 100755. Bytes, hashes, file
types, symlinks and executable identity remain checked. Other modes, including
group/world-writable and special-bit modes, refuse. Verification never chmods
files. External review context, detached manifest and index mode rules remain
unchanged; the repository compatibility rule does not apply to those inputs.

The existing G37 public call and import-time binder remain the integration
boundary. New phases describe source admission only. No early successful
dispatch precedes historical/runtime binding assertions, and the CLI retains
its historical Gate-closure wording. Archived prompts and source snapshots
remain data. No runtime collection, provider call or effect is part of these
checks.
