# Gate3 G37R registration and evidence repair

## Result

`G37R_READY_FOR_INDEPENDENT_REVIEW`

G37R corrects the two stale release-file SHA-256 values in the public current
registration. The completion manifest is pinned to
`a5500c8763b31b3edf01353e461295754af4651afa7792f642b172d6ca0bd0`; the
integration seam index is pinned to
`0db7692fd5d22d206afe3750c9940807b2e3b6947cd4d4b7dafa0afd98b3bb7d`.
The cumulative inventory remains exactly 59 paths over
`d199199a578c078c913a2381f595549175bd9235`: 40 additions, 19 modifications
and 1,076 protected baseline paths. The final reconstructed tree is
`71e0438a4ef8532a3047a6e87061240d5b958a31`.

## Fresh G37R checks

- Five focused registration, guard and binder tests passed on the final source;
  the phase-recorded run completed in 62.48 seconds with all 15
  setup/call/teardown phases passing.
- Final compile, `git diff --check` and the authority guard passed.
- The guard reports `G37_FROZEN_RELEASE_PROPOSAL_UNSTAGED` and
  `GATE3_STATUS=NOT_CLOSED`.
- The complete public current-registration control accepts the exact block,
  source files, schema inventory and symbols. Missing or altered completion
  and seam files, one old pin and a coherent overlay-only old substitution are
  refused.
- Public supplied Living and Conformance validation passed without recollecting
  E5, D or G3. Four mutations were refused. The final run observed zero
  collector, current Root, Host, Work execution, history-recording and effect
  calls.

The retained Living report remains 5,875,142 bytes with SHA-256
`d84cdd50e918c36f06ea60d0c3d4154760438d7cbcd4cd9124dc9f2745bfdc08`.
The retained Conformance report remains 5,988,284 bytes with SHA-256
`e7983c25d588878f8f535c5037bbddd519672241d6e004361188e3ff2f682b66`.
The derived Living report changes only `legacy.current_registration`; its
SHA-256 is `bae9e7d481d20660086ed93d66283ea15029fb62d0e88ef939dcf9fe08c0aa6b`.
Conformance uses an explicit generic-JSON-to-existing-dataclass projection;
it does not collect or alter the report.

## Source and owner procedure

The cumulative d199-to-G37R patch is 4,122,968 bytes with SHA-256
`d5733827612409f19d263598e255a38a80200992a1a86b428e32adf8194022ca`.
The incremental G37-to-G37R patch is 11,743 bytes with SHA-256
`eed291bdbbc1141cb46f2db7a4e3ff6d3e9063cff8c16f4e0ddefa4a4b553053`.
Both independently reconstruct the same final tree and exact postimage modes.

The regenerated G3-8 procedure remains unexecuted against the owner. Its
pre-apply checks cover the full 1,095-file baseline, modes, hidden index flags,
ignored collisions, symlink ancestors and independent remote-main pin. A
disposable local-remote run refused no-execute, wrong archive hash, dirty owner,
altered postimage, hidden-index and ignored-file controls, then completed apply,
stage, guard, tests, single-parent commit, normal local push and independent
readback. It did not contact the real remote.

## Preserved evidence and limits

All six recovered helper bodies are retained as verified historical evidence
and were never imported or executed. Failed attempts and raw streams remain in
the evidence. The original G37 candidate and evidence are unchanged. The owner
repository remains clean at the accepted basis with empty staging; no owner
commit or push occurred.

Gate3 remains `NOT_CLOSED`. Source admission creates no Root permission or
effect authority. Actual owner landing and remote readback require a separate
explicit G3-8 execution after independent review.

## Machine summary

```text
RESULT=G37R_READY_FOR_INDEPENDENT_REVIEW
BASE_HEAD=d199199a578c078c913a2381f595549175bd9235
FINAL_G37R_TREE=71e0438a4ef8532a3047a6e87061240d5b958a31
CHANGED_PATHS=59
G37R_INCREMENTAL_CHANGED_PATHS=5
REGISTRATION_MATRIX=PASS
FOCUSED_PHASES=15_OF_15_PASS
RETAINED_LIVING_SUPPLIED=PASS_METADATA_REBOUND
RETAINED_CONFORMANCE_SUPPLIED=PASS_TYPED_DECODE
COLLECTOR_CALLS=0
PROVIDER_CALLS=0
REAL_EFFECTS=0
OWNER_PROCEDURE=PASS_DISPOSABLE_LOCAL_REMOTE_ONLY
COMMIT_PERFORMED=false
PUSH_PERFORMED=false
GATE3_STATUS=NOT_CLOSED
NEXT_REQUIRED_ACTION=INDEPENDENT_G37R_REVIEW_THEN_SEPARATELY_AUTHORIZED_G3_8
```
