# Two different checks

## Static Reader check

The companion `presentation/verify_reader.py` uses only the Python standard library. It checks XML parsing, exact text byte recovery, member SHA-256/size, detached index positions and optionally companion binary/filesystem bytes. It does not import Radiolaria, run any collector or contact a model.

From the capsule directory, use the names delivered in the final manifest:

```sh
python -B presentation/verify_reader.py LLM_READER_INCIDENT_TO_PROOF_ATLAS_V02_20260923.xml --index LLM_READER_INCIDENT_TO_PROOF_ATLAS_V02_20260923.index.json --capsule .
```

To rebuild the XML from the pinned capsule content, `python -B presentation/build_reader.py --capsule . --output /path/to/new/reader.xml` reads `reader_content_manifest_v02.json`. Output should be a new path. This rebuild checks documentary identities; it does not create or prove admission.

## Existing Atlas saved-proof check

The source entrypoint at the admitted implementation commit is:

```sh
python -B demo/run_incident_atlas_v01.py verify \
  --package docs/showcase/incident_to_proof_atlas_v01/evidence/atlas_package.json \
  --expected-pin docs/showcase/incident_to_proof_atlas_v01/evidence/expected_pin.json \
  --output /path/to/new/atlas-verification.json
```

This command is shown for a separately installed, already authorized repository checkout whose source bytes match the package. The `sources/` copies in this capsule are inert reading material, not an executable clone. Follow that repository's dependency declarations. Its actual import-time registration/binder requires a valid independently reviewed R1 context for the checkout. A new clone with no such context may refuse `REVIEW_CONTEXT_REQUIRED`. The capsule neither supplies an owner context nor grants authority to invent, refresh or bypass one.

The supplied expected pin retains its historical `WRITER_HANDOFF_NOT_INDEPENDENT_ACCEPTANCE` purpose. Independent Work review subsequently accepted the exact package; that review and AT6 source admission are distinct included records. A handoff pin is not self-authenticating certification.

Existing arguments `verify` and `replay` use `verify_v01`; there is no collection fallback. The expected saved result is in `evidence/at5/final_replay_one.json` (935 bytes; SHA-256 `b2e7d1d859cf382dfd9879763f20e49fb373b61a2b2b8ac7d117bea7925fc6a2`). Its integrity and supported-semantics values are PASS, execution is PURE_REPLAY, and native replay is UNSUPPORTED_NATIVE_SCHEMA. The presentation build did not rerun it. Recorded AT5 paired replay and AT6 focused receipts are included separately.

The original package hash is `5947e1f270ca0a33214ed517e56ed88807efdaf7f1fdcb0da66d6b04d00acf24`; the raw expected-pin file has a different SHA-256, `6f44be87aa798dcd45d804804b968e2b0e7de61ccc845a7bed863ef9b74b45f5`. Current validation checks both semantic relationships and required source identities. Source hashes do not confer action permission, certify physical measurements or reconstruct the unsupported original native graph.
