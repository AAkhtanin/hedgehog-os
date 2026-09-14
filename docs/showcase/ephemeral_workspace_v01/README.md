# Ephemeral Workspace v0.1

The reviewed demonstration turns a bounded request into a temporary workspace:
semantic interpretation and privacy review inform local decisions, the runtime
materializes the accepted topology, and independent Roots retain their own
authority. No model, semantic architect, receipt or replay grants permission.

## Demonstrated Lifecycle

The principal run is CONTROLLED_DETERMINISTIC. It consumes three semantic-role
responses and performs actual photo preview, rating, selection, exposure and crop
work without changing originals. Media services are bounded; the deliberate
AudioSink disappearance is freshly observed and drives selective continuation,
preserving unaffected evidence. Separate sidecar approval precedes the scoped
write. Session closure and cleanup have recorded outcomes, not a claimed general
OS sandbox. Earlier live/captured history and five local security probes have
separate provenance, inputs and counters; none is relabelled as this main run.

## Public Offline Verification

From the repository root, with existing dependencies installed:

```sh
docs/showcase/ephemeral_workspace_v01/verify_replay.sh 693fc6b5c2e8499161b40dc7bb6c22a21ca040c38325f1e657f176e9ff7bf525
```

`EWS_PYTHON` may select an existing interpreter. Otherwise the script uses the
checkout's `.venv/bin/python` or `python3`. It performs no installation or export.
The expected pin comes from the independent lead's landing instruction, not
from the checked package. The [verification record](anchor_verification_v01.json)
and [lead pin](lead_reviewed_anchor_v01.json) are separate from the frozen
[publication](external_anchor_publication_v01.json) and [18 public files](public_safe_package/sealed_package_manifest_v01.json).
`SHA256SUMS` covers the showcase except itself.

ANCHORED_PASS verifies exact safe derivative evidence, not private originals,
semantic truth, a signer, trusted timestamp, Root attestation or present authority.
Native original canonical schema replay remains UNSUPPORTED_NATIVE_SCHEMA.
Typed zero counters are not OS-wide monitoring. See [scope and provenance](EVIDENCE.md)
and the [27-file source index](source_index_v01.json).

## Explicit Audit Lanes

Default pytest selection excludes exactly the evidence and adversarial modules.
This is selection policy, not a PASS or a skip inside an accepted test. To run the
five local probes, supply a fresh writable evidence directory:

```sh
EWS4R_PROBE_EVIDENCE="$(mktemp -d)" .venv/bin/python -m pytest -o addopts='' tests/test_ephemeral_workspace_adversarial_v01.py
```

The historical 59-case frozen-export audit requires all six genuine inputs:
`EWS4_INPUT_ROOT`, `EWS4_SOURCE_LEDGER`, `EWS4_EXECUTION_HEAD`,
`EWS4_TEST_EVIDENCE`, `EWS4R_SUPPLEMENTAL_PROOF_ROOT` and
`EWS4R_SUPPLEMENTAL_MANIFEST_SHA256`. Private inputs are not shipped here.
After resolving them from retained audit evidence, use:

```sh
EWS4_EXECUTION_HEAD=e42d37fa98dfec7110b8cf75b1aceaa614f461be .venv/bin/python -m pytest -o addopts='' tests/test_ephemeral_workspace_evidence_v01.py
```

The execution head remains the recorded basis after landing, not checkout HEAD.
Public replay above needs none of those private export inputs. The accepted
[design history](../../demo_designs/ephemeral_workspace_v01.md) retains old
commands and budgets; this page is the current navigation and invocation guide.
Presentation, production certification and new Gates are not claimed.
