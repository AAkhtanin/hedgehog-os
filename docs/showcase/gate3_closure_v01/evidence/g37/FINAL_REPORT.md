# Gate3 G37 Frozen Release Result

## Result

`G37_READY_FOR_INDEPENDENT_REVIEW`

The candidate is an exact 59-path proposal over owner commit
`d199199a578c078c913a2381f595549175bd9235`: 40 additions and 19
modifications. Its reconstructed tree is
`9797a0f68624e029d55d490753a26536e7ac3785`. All 1,076 protected baseline
paths are unchanged. The owner remains clean on tree
`26d63912117a2324cc7e711407be33123f55ab81`; its index, refs, config and
1,095 tracked regular files match entry state.

Gate3 is `NOT_CLOSED`. G37 prepares a frozen source and review package. It
does not perform owner admission, commit, push, Atlas work, provider calls or
real effects. T46 and the owner-dependent part of G3-D17 remain pending G3-8.

## Fresh Full Reports

The successful Living successor ran once after a narrow closed-metadata
integration repair. The command completed in 2,300.17 seconds and returned a
complete valid report:

- E5: 1,806.61 seconds.
- D: 341.35 seconds.
- shared Conformance: 20.86 seconds.
- G3: 27.43 seconds.
- supplied validation: 10.61 seconds.
- mutation controls: 49.55 seconds.
- successor report: 5,875,142 bytes, SHA256
  `d84cdd50e918c36f06ea60d0c3d4154760438d7cbcd4cd9124dc9f2745bfdc08`.

The independent standalone Conformance successor was started only after the
Living cost and monitoring overhead were assessed. It completed in 2,212.77
seconds:

- E5: 1,771.86 seconds.
- D: 333.49 seconds.
- shared Conformance: 19.96 seconds.
- G3: 26.60 seconds.
- supplied validation: 4.83 seconds.
- mutation controls: 24.89 seconds.
- successor report: 5,988,284 bytes, SHA256
  `e7983c25d588878f8f535c5037bbddd519672241d6e004361188e3ff2f682b66`.

Each top-level report owns exactly one fresh E5, one D and one G3 collection.
The shared consumer recollects neither E5 nor G3. Provider and real-effect
counts are zero. The E5 owner and shared bytes are identical at 1,384,305
bytes, SHA256
`78576b50034ecfd6e8c88ebe7c51f22d57a2b24c58662b4566584199ae48ddf9`.

The original Living attempt is retained as a real failure. It completed its
expensive E5 and G3 lanes but found closed release metadata that did not yet
name the current field surface. The repair changed that metadata integration,
then cheap controls passed before the one successful retry. It was not hidden
or relabelled as a pass.

## Cost Interpretation

The first failed Living command spent 1,816.80 of 1,856.86 seconds in E5
(97.84 percent) and 27.12 seconds in G3. The passive monitoring callback was
observed six times. Its same-volume write estimate is about 0.00015 seconds;
one macOS sampling attachment took about 1.68 seconds. The later unmonitored
standalone Conformance completed about 87 seconds faster than Living. The
monitor is therefore not a credible explanation for the historical cost.

The old module-autouse Living and Conformance pytest wrappers were not selected:
each would repeat another full E5/D collection without producing a distinct
public result. The two named public entrypoints, their supplied validators and
mutation controls provide the required fresh release lanes.

## Focused and Replay Evidence

The final focused selection completed 72 tests and 216 setup/call/teardown
phases, all passing, in 244.72 seconds. It includes current G37 guard/binder
controls and the source-bound G36R mechanism closure.

Two independent pure replay processes completed in 53.06 and 53.14 seconds.
All four canonical replay outputs are byte-identical. The G35 five-domain
replay remains exactly 144,756 bytes with SHA256
`f9ca8e48dc61c815e1235afa0c5141aed96128823dd094ae44aef8ecd03ee75d`.

Both processes observed zero provider, current Root, Host, Work execution,
current-history-write and effect calls. Saved Root pure recomputation occurred
1,364 times in each process and is not current authority. Full original native
replay remains `UNSUPPORTED_NATIVE_SCHEMA`.

## Frozen Source and Admission

Both source routes reconstruct the same final bytes and modes:

- cumulative d199-to-G37 patch: 4,118,802 bytes, SHA256
  `e2c3f0b2f58bb4609d63fca5bfbb6f15e6827737d33586eaa16aae4f8b61ef79`;
- incremental G36R-to-G37 patch: 87,326 bytes, SHA256
  `b1be36d722780de29e133f78edac032597dec4d91e1ff867bb37078397cdc335`.

The current authority guard passes as
`G37_FROZEN_RELEASE_PROPOSAL_UNSTAGED`. `git diff --check` passes and staging
is empty. Product runtime and Gate3 mechanism bodies stayed byte-identical
after the successful runtime freeze; later changes are the documented
governance, release-registration and focused-control surface. The Living runner
only changes its closed registration literal after the fresh report.

The external G3-8 procedure was validated in isolated repositories. It accepts
the exact payload, applies and stages exactly 59 paths, recognizes unstaged,
staged and committed guard phases, creates a sole-parent synthetic fixture
commit, performs postcommit checks, executes a normal local push and verifies
fetch/readback. Dirty owner, altered postimage and wrong outer-archive hash
controls fail without commit or push. Synthetic fixture commit
`2875bf2d7b92d1130a33f6ded7ee188d7619daed` is not an owner commit.

## Honest Boundaries

- Fresh G37: full Living, independent Conformance, current guard/binder,
  focused controls and supplied mutation controls.
- Accepted recorded: unaffected G31-G36R semantic/mechanism controls, bound by
  the source-impact ledger.
- Captured original: prior authentic Gemini origin evidence; no new provider
  call occurred in G37.
- Pure replay: new read-only computation over saved evidence, without current
  authority or effects.
- Pending owner: actual G3-8 apply, commit, normal push, remote readback and
  final clean state.

Checksums establish byte identity, not signatures, physical certification or
truth of the external world. Source admission grants no Root permission or new
effect owner.

## Machine Summary

```text
RESULT=G37_READY_FOR_INDEPENDENT_REVIEW
BASE_HEAD=d199199a578c078c913a2381f595549175bd9235
BASE_TREE=26d63912117a2324cc7e711407be33123f55ab81
REVIEWED_G36R_TREE=e18a24a4c47b54ed0fd24cf83559e2e0ac9605d0
FINAL_G37_TREE=9797a0f68624e029d55d490753a26536e7ac3785
CHANGED_PATHS=59
ADDITIONS=40
MODIFICATIONS=19
PROTECTED_PATHS=1076_EXACT
LIVING=PASS_2300.17_SECONDS
CONFORMANCE=PASS_2212.77_SECONDS
FOCUSED=72_TESTS_216_PHASES_ALL_PASS
PURE_REPLAY=PASS_TWO_INDEPENDENT_PROCESSES_BYTE_IDENTICAL
PROVIDER_CALLS=0
REAL_EFFECTS=0
OWNER_REPOSITORY_UNCHANGED=true
OWNER_STAGING_EMPTY=true
ALL_TASK_PROCESSES_FINAL=true
COMMIT_PERFORMED=false
PUSH_PERFORMED=false
GATE3_STATUS=NOT_CLOSED
NEXT_REQUIRED_ACTION=INDEPENDENT_G37_REVIEW_THEN_SEPARATELY_AUTHORIZED_G3_8
```
