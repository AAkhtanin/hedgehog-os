# Testflix V09: execution and review package

This package contains an external candidate, not an owner-admitted release.
Start with `FINAL_REPORT.md`, `demo/story.html`, and `coverage.json`. The report
distinguishes completed fresh execution, source-bound recorded results, failed
attempts, and remaining admission work. Do not infer a test PASS from a SETUP
artifact or a successful E return alone.

## Provenance

Business effects are controlled mocks. The trusted Testflix clock and provider
catalog are local controlled inputs, not attested wall-clock/provider facts.
Only responses labelled LIVE_CAPTURED come from the configured real model.
Each of four different semantic duties consumes its own local projection and
the necessary upstream outputs. The local adapter attaches request, projection,
response and capture bindings; the model does not issue Root authority.

CAPTURED_REEXECUTION runs those input-bound semantic responses through the same
handler using newly constructed genuine Hosts and mock execution. It is not
zero-effect replay. Offline sealed-history replay is separately checked for
zero semantic-provider and effect calls. Neither JSON evidence nor a capture
reconstructs live Host authority after its process ends.

## Existing candidate commands

Use the existing Python environment. No dependency installation is part of this
package. Run from the independent candidate directory with its path on
`PYTHONPATH`. The following commands are explicit, not an automatic pipeline:

```sh
python -B demo/run_testflix_v01.py --help
python -B demo/run_testflix_v01.py render --input story.json --output story.html
```

The live/captured CLI's exact argument names are shown by `--help`. A real live
launch requires the configured provider/model and credentials on the owner's
machine, an explicit output/capture directory, and available call budget. Do not
copy credentials into this package. Do not retry an unsuccessful model response
until it produces the desired outcome. The run's attempt ledger counts failures.

The HTML viewer is self-contained and opens directly in a browser. It makes no
provider requests. Its rows are derived from the included actual artifacts;
there is no simulated success animation.

## Apply boundary

`owner_apply/` contains the cumulative source ledger and reviewable patch against
the recorded accepted L. It does not authorize applying, staging, committing or
pushing. Review final common-runtime admission coverage and the exact source
delta before owner landing. Existing Gate closures retain historical provenance.
Old automatic continuation scripts remain paused.

## Evidence

Numbered command directories retain argv, cwd, selected environment values,
source/helper hashes, raw stdout/stderr, final return code and elapsed time.
Node phases distinguish SETUP, CALL and TEARDOWN. Original inner failures are
retained, including corrected domain-consumer and exporter failures. Stopped
attempts are not semantic failures or passes. Large repeated source objects may
be listed by local path and SHA rather than duplicated in the small package.

No package field self-awards full Testflix acceptance or production certification.
