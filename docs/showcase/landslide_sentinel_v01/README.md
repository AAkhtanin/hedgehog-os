# Landslide Sentinel v0.1

An observed synthetic demonstration of local monitoring, bounded reasoning and
independent Root decisions. During modeled connectivity loss, the site continues
local work and authorized mock action. A model proposes useful investigation;
it never grants permission. Changed rainfall invalidates pending configuration;
the actual E result changes cadence. Measured recovery and a distinct OFF action
do not arise from cleanup or a late model answer.

## Evidence

[Coverage and limitations](EVIDENCE.md), [source identities](source_index_v01.json)
and the [whole-story evidence map](claim_evidence_map_v01.json) separate historical
execution from current review. The accepted chronological [design](../../demo_designs/landslide_sentinel_v01.md)
is preserved as written, including its historical pending status.

The latest live pair performs current-record metadata checks versus a native
reserve-history read measuring 20 seconds and range 150 micrometres. Three real
Gemini contributions reach one current BSEP/D/Work/Root. Gemini transport is an
online harness emulating an internal SLM role, not actual offline Gemini or local
model hardware. A separate fresh LOCAL_ALGORITHMS_ONLY continuation uses no model.
Both earlier inconclusive pairs remain NOT_DEMONSTRATED. Actual EA values include
valid zeros, but unknown interval bounds and physical site mapping are not invented.

## Public Replay (No Provider)

Run from any checkout with the existing dependencies; the expected pin comes from
the independent lead review, not from the package being verified:

```sh
sh docs/showcase/landslide_sentinel_v01/verify_replay.sh 7b91c496521e11c69fab9ea89a576474d37dbcb93c494b58a93269884fffb9b8
```

`SENTINEL_PYTHON` can select an existing Python. The wrapper otherwise uses the
checkout's `.venv/bin/python` or `python3`; it does not install anything.
Replay validates safe derivatives only. Native historical-graph replay remains
UNSUPPORTED_NATIVE_SCHEMA; checksums and signatures do not prove sensor truth.

## Explicit Audit Lanes

Default pytest excludes all three Sentinel audit modules and preserves the EWS
exclusions. Exclusion is not a passed or skipped runtime test. Inspect the chosen
node and its inputs first; use a new writable external evidence directory/run ID.
These examples run only the named module when explicitly invoked:

```sh
LS0_EVIDENCE=/external/new-ls0 LS0_RUN_ID=audit001 python3 -m pytest -o addopts='' tests/test_landslide_sentinel_ls0_v01.py
LS1_EVIDENCE=/external/new-ls1 LS1_RUN_ID=audit001 python3 -m pytest -o addopts='' tests/test_landslide_sentinel_ls1_v01.py
LS2_EVIDENCE=/external/new-ls2 LS2_RUN_ID=audit001 python3 -m pytest -o addopts='' tests/test_landslide_sentinel_ls2_v01.py::test_c02_historical_context_actual_consumer
```

These are opt-in runtime/audit commands, not default paid demonstration launches.
The explicit [LS2 CLI](../../../demo/run_landslide_sentinel_ls2_v01.py) describes
its separate live/configuration/EA inputs; this publication performs none of them.
There is no new Gate, tenth Living registration or effect owner. Presentation is
not yet produced; this is a source and evidence landing, not physical certification.
