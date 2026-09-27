# Gate6 Technical Reference Package

Prepared 27 September 2026 for exact independent review. Source admission is
PENDING; Gate6A technical readiness is NOT_YET_AWARDED; Gate6 is NOT_CLOSED.
This entry supersedes the eight-add execution document only as navigation for
this package. It does not rewrite that document or any historical status.

From this checkout, the free first command is:

```sh
python3 -B demo/verify_gate6_reference_v01.py --output /tmp/g6-inspection
```

Use a new output directory. Default inspection is standard-library/data-only:
no runtime imports, collectors, Docker, credentials or network. It verifies the
closed package inventory, exact bytes, executable bits, three source views and
all 73 row bindings. Expected classification is
`PASS_FINITE_MIXED_BASIS_REFERENCE_PACKAGE`, not eleven fresh same-freeze runs.
Without `--manifest-sha256 <externally-reviewed-pin>`, this is self-consistency,
not independent acceptance. Any `remaining_technical` rows remain open.

Explicit verification of saved evidence:

```sh
python3 -B demo/verify_gate6_reference_v01.py --mode supplied --output /tmp/g6-supplied
```

This invokes twelve historical pure workers and one finite successor consumer.
Three original workers use the exact original source view; the other nine use
the reviewed G6A4R view. Both retain the old compatibility preimage. Only the new
four-row consumer uses current sources. Historical G5 owns two additional pure
children. No consumer falls back to a producer. Run under the detached bounded
operator with a 600-second ceiling; actual final timings are detached in the
G6A5R1 return, not a universal timing promise.

Observed prerequisite: macOS arm64, CPython 3.14.5 and the existing dependencies
in dependency_inventory.json. Inspection itself requires only Python's stdlib.
No fresh installation or other platform has been tested in G6A5.

- [Technical contracts and math](TECHNICAL_REFERENCE.md)
- [Trust boundary and findings](BOUNDARY_AND_FINDINGS.md)
- [Environment and dependency provenance](ENVIRONMENT_AND_DEPENDENCIES.md)
- [Current 73-row matrix](acceptance_matrix.json)
- [Machine inventory](machine_manifest.json) and [resource graph](evidence_index.json)
- [Publication handoff](PUBLICATION_HANDOFF.md)
- [Exact DRS repair and four retained predicates](FINITE_COMPLETION.md)

Evidence keys in the indexes map to checked repository-relative files. Original
absolute paths are labelled historical provenance, never required reader inputs.
Content-addressed blobs are exact evidence bytes, not executable entrypoints.
Do not execute recovered historical helpers except the explicitly reviewed pure
consumers invoked by the finite reader. JSON cannot restore Host authority.

The primary basis is two fresh G6A4R profiles (DIRECT/G35) and nine compatible
retained G6A4 profiles. External Work accepted that bounded protocol for packaging;
the final packaging bytes still require independent review. Owner landing is a
later explicit R1 operation. Final preparation/rehearsal receipts are detached
so that successful checks do not change the frozen files they checked.

G6A5 and G6A5R remain historical INCOMPLETE results. G6A5R1 corrects only the
compatibility-local classification of exact generated request/trace wrapper IDs,
then adds finite AVF, native reuse, local-current-policy and retained LIVE privacy
proof. This is a review proposal, not a new full campaign or awarded admission.
