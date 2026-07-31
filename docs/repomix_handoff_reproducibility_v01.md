# Repomix Handoff Reproducibility v0.1

## Role and Boundary

This is private engineering handoff tooling. It is not a public release, an
authority source, a completion certificate, a Gate-2 closure claim, RC2, or a
production-readiness or production-security claim.

The tooling does not override owner instruction, `AGENTS.md`, accepted
checkpoints, accepted audits, the Human Passport, or the accepted R-H1
preflight. At the R-H1C implementation boundary, R-H1 was
`IMPLEMENTATION_IN_PROGRESS`, Gate 2 was `NOT_CLOSED`, and G2-C was
`NEXT / NOT_STARTED` and `NOT_AUTHORIZED`.

Current status is recorded by `release/current_status_overlay_v01.json`,
`release/current_limitations.md`, accepted audits/checkpoints, `AGENTS.md`, and
owner instruction.

Generated handoff directories live under `_audit_exports/<handoff-id>/` and
remain ignored and untracked. Generation never stages, commits, or pushes.

## Configuration Model

[`repomix.handoff.config.json`](../repomix.handoff.config.json) is the
repository-owned Hedgehog handoff manifest consumed by
[`tools/generate_repomix_handoff_v01.py`](../tools/generate_repomix_handoff_v01.py).
It is not a native Repomix auto-discovery configuration.

During real generation, the tool creates a fully specified native Repomix JSON
configuration for each profile inside the transactional `_audit_exports`
directory. It invokes an already-installed local Repomix executable with that
configuration, removes the temporary configuration, validates the outputs,
creates `SHA256SUMS`, and atomically publishes the completed handoff directory.
No permanent `repomix.config.json` is created.

The generator has no installation or network behavior. It does not use remote
Repomix mode. Byte-identical reproduction requires the same branch identity,
full HEAD commit, `origin/main` identity, clean generation state, handoff
manifest bytes, generator bytes, and exact Repomix version.

## Output Set

The generated order is fixed:

1. `00_head_and_origin.txt`
2. `00_repo_governance_and_metadata.md`
3. `01_hedgehog_kernel_and_contracts.md`
4. `02_docs_specs_checkpoints_and_roadmaps.md`
5. `03_demo_runners_and_fixtures.md`
6. `04_tests_and_test_fixtures.md`
7. `05_audit_logs_and_public_safe_evidence.md`
8. `06_current_g2a_g2b_focus.md`
9. `07_passport_release_and_root_contract_data.md`
10. `SHA256SUMS`

Only the explicit public-safe audit profile may include committed `.log`
artifacts. Local runtime logs, raw provider output, credentials, signing
material, local DRS data, caches, virtual environments, generated exports,
binary documents, archives, and key material remain excluded. There is no
global `*.log` exclusion because accepted public-safe audit evidence uses that
suffix. The generator appends a profile-local `**/*.log` exclusion to every
native profile configuration except
`05_audit_logs_and_public_safe_evidence`; the public-safe profile receives only
the global exclusions and owns explicitly selected committed audit logs.

## External Companion Documents

The complete roadmap documents remain owner-supplied external companion
documents during this private engineering cycle:

- `hedgehog_deeptech_completion_roadmap_v3_1_gate_based_guardian.md`
- `hedgehog_deeptech_completion_master_roadmap_v2_1.md`

The generator records their names and external custody in
`00_head_and_origin.txt`. It does not fabricate, reconstruct, locate, copy, or
list them as repository-derived outputs. Their manifest custody value is
`OWNER_SUPPLIED_EXTERNAL`.

## Validation and Generation

Dirty implementation diagnostic:

```bash
PYTHONDONTWRITEBYTECODE=1 \
.venv/bin/python tools/generate_repomix_handoff_v01.py \
  --dry-run \
  --allow-dirty-diagnostic
```

This diagnostic creates no directory and grants no generation permission.

Clean post-commit dry validation:

```bash
PYTHONDONTWRITEBYTECODE=1 \
.venv/bin/python tools/generate_repomix_handoff_v01.py \
  --dry-run
```

Owner-controlled real generation:

```bash
PYTHONDONTWRITEBYTECODE=1 \
.venv/bin/python tools/generate_repomix_handoff_v01.py \
  --generate
```

Optional explicit handoff ID:

```bash
PYTHONDONTWRITEBYTECODE=1 \
.venv/bin/python tools/generate_repomix_handoff_v01.py \
  --generate \
  --handoff-id hedgehog-handoff-<identifier>
```

Verification:

```bash
PYTHONDONTWRITEBYTECODE=1 \
.venv/bin/python tools/generate_repomix_handoff_v01.py \
  --verify _audit_exports/<handoff-id>
```

The default handoff ID is `hedgehog-handoff-<first-12-hex-of-HEAD>`. A final
directory must not already exist. Verification is read-only and accepts only a
direct, non-symlink child of `_audit_exports` with the exact ten-output set and
ordered valid checksums.

## Failure Behavior

Generation fails closed for:

- a dirty worktree or non-empty staging;
- `HEAD` differing from `origin/main`;
- an unavailable local Repomix executable;
- an invalid repository manifest or unsafe include/exclude pattern;
- a missing R-H1 mapping or planned-artifact obligation;
- an existing output-directory collision;
- a partial profile-generation failure;
- a Repomix security-check failure;
- a checksum mismatch;
- an extra, missing, renamed, symlinked, or reordered output.

When Repomix is unavailable, dry validation still checks every non-tool
contract and reports that real generation is unavailable. Real generation
fails without installing anything and leaves no partial or final output.

On any transactional failure, the temporary directory is removed,
`SHA256SUMS` is not published, and no final handoff directory is created.

## Future R-H1 Coverage

The repository manifest keeps explicit obligations for the R-H1D1 independent
audit and R-H1D2 checkpoint before those files exist. Once either artifact is
present, omission from its assigned profile is a hard error. The current R-H1
governance, dependency/licensing, release-spine, generator, documentation, and
focused-test artifacts are likewise mapped to at least one intended profile.

For each planned obligation, `current_status: NOT_YET_PRESENT` is status
captured at the R-H1C implementation basis. It is not a permanently mutable
current repository pointer. Every validation derives actual current presence
from Git's cached-plus-untracked, non-ignored inventory. A later present audit
or checkpoint remains valid with the immutable basis value, but omission from
its required profile is always a hard error; R-H1D1 and R-H1D2 do not need to
rewrite this configuration.
