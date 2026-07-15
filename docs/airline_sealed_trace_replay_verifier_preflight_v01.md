# Airline Sealed Trace Replay Verifier v0.1 Preflight

- document_id: `airline_sealed_trace_replay_verifier_preflight_v01`
- document_status: `PREFLIGHT`
- preflight_status: `READY_FOR_REVIEW`
- observed_base_head: `37320bc`
- planning_only: `true`
- replay_profile: `BASE_SEALED_TRACE_REPLAY`
- runtime_modified: `false`
- tests_modified: `false`
- schemas_modified: `false`
- specifications_modified: `false`
- package_modified: `false`
- committed_anchor_modified: `false`
- replay_code_created: `false`
- replay_report_created: `false`
- root_attestation_required: `false`
- root_attestation_present: `false`
- provider_called: `false`
- network_called: `false`
- gemini_called: `false`
- transaction_rerun_count: `0`
- semantic_rerun_count: `0`
- corridor_rerun_count: `0`
- ledger_recollection_count: `0`
- crypto_collection_count: `0`
- replay_operation_count: `0`
- replay_created_authority_count: `0`
- replay_created_permission_count: `0`
- replay_created_action_count: `0`
- replay_created_packet_count: `0`
- replay_created_receipt_count: `0`
- replay_created_final_output_count: `0`
- real_world_effects_count: `0`
- production_ready_claimed: `false`
- production_security_claimed: `false`

This preflight plans Base Sealed Trace Replay.

It does not perform Replay.

## 1. Closed Basis

- Crypto Artifact Seal closure commit: `26ee0de`
- Root Attestation roadmap correction commit: `37320bc`
- Package generation implementation commit: `905844c`
- Manifest Core anchor publication commit: `5345815`
- E2 audit base commit: `56e3811`
- Official package:
  `.tmp/airline_crypto_artifact_seal_slice_e1/airline_crypto_artifact_seal_slice_e1_offline_905844c`
- Logical package ref:
  `airline_crypto_artifact_seal_slice_e1_offline_905844c`
- Committed anchor:
  `docs/airline_crypto_artifact_seal_anchor_v01.json`
- Expected Manifest Core hash:
  `29355a3b2f2b95bd6358d6085a801334d7fd7ca23438e6e2ce0618106edba12b`
- Ledger entries: `19`
- Dependency edges: `29`
- Root finals: `3`
- Exact source files: `9`
- Critical package files: `11`
- Stored package Verification: `SELF_CONSISTENT_UNANCHORED`
- Independent E2 Verification: `PASS`
- External anchor supplied: `true`
- External anchor verified: `true`
- Signature mode: `UNSIGNED_PLACEHOLDER`
- Signature verified: `false`
- Root Attestation: `DEFERRED OPTIONAL FUTURE PROFILE`
- Root Attestation blocks Base Replay: `false`

The closed layers remain distinct:

1. The stored package Verification is `SELF_CONSISTENT_UNANCHORED`.
2. The independent E2 Verification is `PASS` relative to the previously
   committed Manifest Core anchor.
3. A future Base Replay Report is `PASS` only after one fresh Replay-time
   anchored verification and deterministic trace reconstruction.

Replay never rewrites either earlier Verification Report.

## 2. Historical Anchor Field Boundary

The committed E1 anchor contains:

- replay_allowed: `false`

This is a historical Slice E1 publication fact. It records that Replay was
not authorized when the anchor was published. The anchor is immutable and is
not changed by this preflight.

That historical field does not conflict with the later E2 closure or the
current roadmap gate at `37320bc`. Current Replay-preflight authorization
comes from:

- the successful E2 anchored audit closure;
- closure of Crypto Artifact Seal v0.1;
- the current committed AGENTS checkpoint;
- commit `37320bc`, which restored Base Replay as the next gate.

The committed anchor remains only the trusted expected Manifest Core hash
source. It is not a Replay Report and does not grant runtime permission.

## 3. Replay Definition

Base Airline Sealed Trace Replay v0.1 performs deterministic, read-only
reconstruction and verification of one previously recorded, cryptographically
sealed, and externally anchored Airline transaction trace.

The operative phrase is:

`deterministic sealed-trace reconstruction`

Replay means:

- observe one explicit existing package;
- verify that package against one explicit committed anchor;
- verify the accepted Ledger;
- verify exact artifact order and positional Manifest bindings;
- verify dependencies and recorded Root ownership metadata;
- reconstruct one immutable timeline from Ledger order;
- reproduce deterministic trace-boundary conclusions;
- produce one new Replay verification report outside the package.

Replay does not mean:

- transaction re-execution;
- semantic, proposer, reviewer, Orchestrator, or Architect rerun;
- Corridor execution;
- Ledger recollection;
- Crypto collection;
- package regeneration, repair, normalization, or reserialization;
- runtime SourceBundle reconstruction;
- provider, Gemini, or network call;
- action execution;
- payment, ticket issuance, or booking creation;
- permission refresh;
- nonce consumption;
- packet or receipt creation;
- Root decision, Root-final, or FinalOutput creation;
- restoration of a historical external state;
- proof that any external state remains current.

## 4. Truth, Authority, And Effect Boundary

- Replay verifies recorded continuity; Replay does not prove semantic truth.
- Replay reconstructs a recorded trace; Replay does not reconstruct the real
  world.
- Replay observes Root ownership metadata; Replay does not create Root
  authority.
- Replay observes recorded permissions; Replay does not grant or refresh
  permission.
- Replay observes packets by reference; Replay does not create packets.
- Replay observes receipts as evidence; Replay does not create receipts.
- Replay observes Root finals; Replay does not create a new Root final.
- Replay does not create FinalOutput.
- Replay cannot convert evidence into permission.
- Replay cannot convert a receipt into authority.
- Replay cannot transfer authority between Roots.
- Replay cannot make provider output true or authoritative.
- Replay cannot turn the unsigned placeholder into a verified signature.
- Replay `PASS` is not signer authentication, PKI, non-repudiation, trusted
  timestamping, rollback protection, or production storage security.
- Replay `PASS` is not evidence that payment, ticketing, or booking occurred
  in the real world.

## 5. Root Attestation Boundary

- Base Replay does not require Root Attestation.
- `root_attestation_required` is `false`.
- `root_attestation_present` is `false` for the official package.
- Absence of Root Attestation is not a Replay failure.
- Base Replay validates recorded Root ownership metadata through the accepted
  Ledger.
- Base Replay does not claim proof-level Root-key identity or signer
  authentication.

The deferred optional profile remains:

`docs/airline_root_artifact_attestation_future_profile_v01.md`

A future Attested Replay profile may add three aggregate Root commitments.
Base Replay v0.1 contains no Root Attestation contract and adds no key,
signature, policy, or public-key-set field to its input or report.

## 6. Actual Persisted Package Contract

The exact nine source files, in frozen order, are:

1. `airline_transaction_artifact_ledger.json`
2. `summary.json`
3. `secret_scan.json`
4. `semantic_to_contract_causal_run.json`
5. `semantic_to_contract_bridge.json`
6. `integrated_deterministic_airline_summary.json`
7. `tri_party_airline_bsep_packet.json`
8. `tri_party_airline_bsep_validation.json`
9. `tri_party_airline_bsep_side_projections.json`

The two derived Crypto files are:

10. `airline_crypto_artifact_seal_manifest_v01.json`
11. `airline_crypto_artifact_seal_verification_v01.json`

These eleven paths are the critical read-only Replay package surface. The
canonical source-package hash covers exactly the nine source files. Manifest
and stored Verification are separate derived Crypto artifacts.

Auxiliary actor artifacts may coexist in the directory. The entire directory
is not claimed sealed, and unrelated auxiliary files do not automatically
fail Replay. Additional Manifest source refs or artifact refs fail closed.

Replay does not require fields that the committed package never persisted:

- no serialized runtime Ledger SourceBundle;
- no `airline_transaction_artifact_ledger_source_bundle_v0_1`;
- no `airline_transaction_artifact_ledger_source_validation_v0_1`;
- no top-level `travel_intent` in `summary.json`;
- no complete deterministic in-memory report inside
  `integrated_deterministic_airline_summary.json`.

The integrated deterministic summary is intentionally reduced. Those absent
views are not package corruption. Replay neither invents nor reconstructs the
runtime SourceBundle.

The two accepted JSON domains remain separate. The nine source documents use
strict source-document parsing, including finite source-data floats, and are
bound by their exact bytes. Manifest and stored Verification use the closed
canonical Crypto parser, where floats remain forbidden. Replay does not
canonicalize or reserialize a source document before hashing it.

## 7. Trust And Fresh Verification

A Replay `PASS` does not trust only the stored unanchored package
Verification, the tracked E2 Verification JSON, the Envelope's own Manifest
Core hash, or a caller-supplied `PASS` flag.

Immediately before pure timeline reconstruction, the future exact-package
collector must:

1. receive one explicit trusted expected Manifest Core hash;
2. load that hash for the official package from the previously committed
   anchor;
3. freeze the exact current package bytes;
4. run one independent read-only Ledger audit;
5. strictly reconstruct the persisted typed Ledger and Crypto Envelope;
6. build the closed ExpectedIdentity verifier adapter only after Ledger audit
   `PASS`;
7. invoke the existing anchored B2b verifier exactly once;
8. require fresh Verification status `PASS`;
9. require `external_anchor_supplied` exact `true`;
10. require `external_anchor_verified` exact `true`;
11. require every internal Crypto verification flag exact `true`;
12. require `source_bytes_unchanged` exact `true`;
13. require `verification_errors` empty;
14. require `signature_verified` exact `false`;
15. invoke pure timeline reconstruction exactly once;
16. invoke the post-Replay snapshot provider exactly once;
17. require exact initial/post critical-package snapshot equality;
18. derive the final Replay Report status exactly once.

There is no unanchored Replay success. A missing, malformed, or mismatched
expected anchor yields `FAIL_CLOSED`. The Envelope's own hash is never
substituted automatically as the expected anchor.

## 8. ExpectedIdentity Adapter Boundary

The runtime SourceBundle is not persisted. Replay must not claim to reconstruct
source-derived expected identity from that unavailable object.

After one independent read-only Ledger audit returns `PASS`, the exact-package
collector may construct an
`AirlineTransactionArtifactLedgerExpectedIdentityV01` with role:

`verifier_contract_adapter_after_independent_ledger_audit`

The adapter projects only accepted frozen Ledger fields required by the
closed Ledger and Crypto validators. It is not an independent semantic-source
claim, a trust anchor, a replacement for the committed expected Manifest Core
hash, or evidence that the runtime SourceBundle was reconstructed.

- runtime_source_bundle_serialized: `false`
- runtime_source_bundle_reconstructed: `false`
- source_derived_identity_claimed: `false`
- expected_identity_used_as_trust_anchor: `false`
- public_source_bundle_helper_invocation_count: `0`

The committed expected Manifest Core hash remains the external trust input.

## 9. Planned Critical-Package Snapshot

Plan one frozen in-memory byte contract:

### AirlineSealedTraceReplayPackageSnapshotV01

Fields exactly:

- `source_package_ref: str`
- `ordered_source_files: tuple[tuple[str, bytes], ...]`
- `manifest_artifact_ref: str`
- `manifest_bytes: bytes`
- `stored_verification_artifact_ref: str`
- `stored_verification_bytes: bytes`

Rules:

- exact contract type only;
- exact logical source-package ref;
- exact nine-source-file order;
- every source row is an exact `tuple[str, bytes]`;
- no list repair or sorting;
- no bytearray or memoryview;
- `manifest_artifact_ref` is exactly
  `airline_crypto_artifact_seal_manifest_v01.json`;
- `stored_verification_artifact_ref` is exactly
  `airline_crypto_artifact_seal_verification_v01.json`;
- both derived artifacts retain exact bytes;
- total critical-file count is derived as 11;
- auxiliary actor files are outside this snapshot;
- no Path, absolute path, or callback is stored;
- deep immutability;
- caller mutation cannot alter the snapshot.

This is an in-memory byte snapshot, not a filesystem package locator.

## 10. Planned Pure Replay Input

Plan one frozen in-memory contract:

### AirlineSealedTraceReplayInputV01

Fields exactly:

- `source_package_ref: str`
- `accepted_ledger_audit: AirlineCryptoArtifactSealAcceptedLedgerAuditV01`
- `ledger_item: AirlineTransactionArtifactLedgerV01`
- `envelope: AirlineCryptoArtifactSealEnvelopeV01`
- `stored_verification_report: AirlineCryptoArtifactSealVerificationReportV01`
- `fresh_anchored_verification_report: AirlineCryptoArtifactSealVerificationReportV01`
- `expected_manifest_core_hash: str`
- `ordered_source_files: tuple[tuple[str, bytes], ...]`

`accepted_ledger_audit` is the accepted Airline Ledger audit projection used
by the closed Crypto C1 boundary, not an arbitrary report object.

Rules:

- exact declared types and tuple containers;
- exact frozen nine-file order;
- exact `str` refs and exact `bytes` values;
- no bytearray, memoryview, list repair, or sorting;
- no stored Path, package discovery result, callback, or absolute path;
- no raw prompt or raw response;
- deep immutability;
- no file I/O in the pure Replay module.

## 11. Planned Timeline Row

Plan one frozen dataclass:

### AirlineSealedTraceReplayTimelineRowV01

Fields exactly:

- `replay_index: int`
- `ledger_index: int`
- `event_time: str`
- `event_type: str`
- `artifact_type: str`
- `artifact_id: str`
- `artifact_hash: str`
- `root_owner: str`
- `created_by: str`
- `authority_class: str`
- `evidence_class: str`
- `depends_on: tuple[str, ...]`
- `dependency_count: int`
- `is_root_final: bool`
- `selected_offer_id: str | None`

Rules:

- exact immutable types;
- `replay_index == ledger_index`;
- exact indexes 0 through 18 and exact Ledger order;
- no topological resorting, event-time sorting, insertion, deletion, or
  duplicate artifact;
- `event_time`, identity, ownership, classification, creator, and dependency
  fields exactly equal the corresponding accepted Ledger entry;
- artifact ID positionally equals Manifest `ordered_artifact_refs`;
- artifact hash positionally equals Manifest `ordered_artifact_hashes`;
- `dependency_count == len(depends_on)`;
- every dependency names an earlier accepted artifact;
- `is_root_final` is derived from the exact three Root-final artifact types;
- `selected_offer_id` is copied only from accepted canonical identity when
  present;
- missing values are not inferred;
- no source snapshot or raw/private material enters a row.

## 12. Planned Replay Report

Plan one frozen dataclass:

### AirlineSealedTraceReplayReportV01

Fields exactly:

- `replay_status: str`
- `replay_version: str`
- `replay_id: str`
- `source_package_ref: str`
- `transaction_id: str`
- `ledger_id: str`
- `manifest_core_hash: str`
- `expected_manifest_core_hash: str`
- `stored_verification_status: str`
- `fresh_anchored_verification_status: str`
- `stored_verification_contract_verified: bool`
- `fresh_anchored_verification_contract_verified: bool`
- `external_anchor_supplied: bool`
- `external_anchor_verified: bool`
- `signature_mode: str`
- `signature_verified: bool`
- `integrity_verified: bool`
- `continuity_verified: bool`
- `ledger_verified: bool`
- `manifest_binding_verified: bool`
- `artifact_hashes_verified: bool`
- `chain_order_verified: bool`
- `dependency_graph_verified: bool`
- `root_ownership_verified: bool`
- `authority_evidence_boundaries_verified: bool`
- `packet_lineage_verified: bool`
- `receipt_lineage_verified: bool`
- `transaction_identity_verified: bool`
- `source_refs_verified: bool`
- `secret_boundary_verified: bool`
- `source_bytes_unchanged: bool`
- `critical_package_bytes_unchanged: bool`
- `timeline_complete: bool`
- `root_attestation_required: bool`
- `root_attestation_present: bool`
- `source_file_count: int`
- `critical_package_file_count: int`
- `ledger_entry_count: int`
- `dependency_edge_count: int`
- `root_final_count: int`
- `client_root_final_count: int`
- `airline_root_final_count: int`
- `bank_root_final_count: int`
- `timeline_row_count: int`
- `ledger_audit_count: int`
- `anchored_verification_count: int`
- `post_replay_snapshot_provider_call_count: int`
- `transaction_rerun_count: int`
- `semantic_rerun_count: int`
- `corridor_rerun_count: int`
- `ledger_recollection_count: int`
- `crypto_collection_count: int`
- `provider_call_count: int`
- `network_call_count: int`
- `gemini_call_count: int`
- `replay_created_authority_count: int`
- `replay_created_permission_count: int`
- `replay_created_action_count: int`
- `replay_created_packet_count: int`
- `replay_created_receipt_count: int`
- `replay_created_final_output_count: int`
- `real_world_effects_count: int`
- `reconstructed_timeline: tuple[AirlineSealedTraceReplayTimelineRowV01, ...]`
- `verification_errors: tuple[str, ...]`

The report deeply freezes tuple fields. Strings are never split into
characters, and mutable caller lists never remain backing state. Projection
uses an explicit exact JSON-safe plain-dict boundary, not an arbitrary
dataclass serializer or `repr` fallback.

The report contains no raw package bytes, absolute paths, raw prompts, or raw
responses.

## 13. Replay Version And ID

The exact constants are:

```text
REPLAY_VERSION =
    "airline_sealed_trace_replay_v01"

REPLAY_ID_PREFIX =
    "airline_sealed_trace_replay_v01"
```

Derive exactly:

```text
replay_id =
    REPLAY_ID_PREFIX
    + ":"
    + transaction_id
    + ":"
    + manifest_core_hash
```

The constructor derives `replay_version` and `replay_id`. Caller-supplied
alternatives are never trusted. The derivation uses no current time, random
UUID, nonce, process ID, or filesystem path. Repeated accepted input produces
the same Replay ID.

## 14. Status Derivation

Allowed statuses are only:

- `PASS`
- `FAIL_CLOSED`

There is no `SELF_CONSISTENT_UNANCHORED` Replay success, `PARTIAL_PASS`,
`WARN_PASS`, `BEST_EFFORT_PASS`, or `REPAIRED_PASS`.

The report constructor derives `replay_status` and never trusts caller-supplied
`PASS`.

### Stored Package Verification Moment

`PASS` explicitly requires the stored package Verification to have:

- exact `AirlineCryptoArtifactSealVerificationReportV01` type;
- public contract validation `PASS`;
- `verification_status == SELF_CONSISTENT_UNANCHORED`;
- `expected_manifest_core_hash is None`;
- `external_anchor_supplied is False`;
- `external_anchor_verified is False`;
- `signature_mode == UNSIGNED_PLACEHOLDER`;
- `signature_verified is False`;
- `verification_errors == ()`;
- exact transaction ID, Ledger ID, and Manifest Core hash matching the
  Envelope and accepted Ledger.

### Fresh Replay-Time Verification Moment

`PASS` explicitly requires the fresh Replay-time Verification to have:

- exact `AirlineCryptoArtifactSealVerificationReportV01` type;
- public contract validation `PASS`;
- `verification_status == PASS`;
- `expected_manifest_core_hash` equal to the explicit trusted input;
- `external_anchor_supplied is True`;
- `external_anchor_verified is True`;
- `signature_mode == UNSIGNED_PLACEHOLDER`;
- `signature_verified is False`;
- `verification_errors == ()`;
- exact transaction ID, Ledger ID, and Manifest Core hash matching the stored
  Envelope and accepted Ledger.

For both Verification Reports, every committed internal integrity flag is
exact `True`:

- `canonicalization_profile_verified`;
- `hash_algorithm_verified`;
- `manifest_core_hash_verified`;
- `ledger_document_byte_hash_verified`;
- `artifact_hashes_verified`;
- `chain_genesis_verified`;
- `chain_order_verified`;
- `chain_head_verified`;
- `chain_tail_verified`;
- `source_file_hashes_verified`;
- `source_package_hash_verified`;
- `ledger_geometry_verified`;
- `root_ownership_verified`;
- `authority_evidence_boundaries_verified`;
- `secret_boundary_verified`;
- `source_bytes_unchanged`.

The Replay Report projects these facts honestly:

- `stored_verification_contract_verified is True`;
- `fresh_anchored_verification_contract_verified is True`;
- `external_anchor_supplied is True`;
- `external_anchor_verified is True`;
- `signature_mode == UNSIGNED_PLACEHOLDER`;
- `signature_verified is False`.

Replay never changes the stored package Verification.

`PASS` requires all of the following:

- exact Replay input contract;
- empty `verification_errors`;
- accepted Ledger audit `PASS`;
- exact Ledger validation `PASS`;
- fresh anchored Crypto Verification `PASS`;
- external anchor supplied and verified;
- expected and observed Manifest Core hashes equal;
- every Replay verification boolean exact `True`;
- exact 19 Ledger entries, 29 dependency edges, and 3 Root finals;
- exact one final per Root;
- exact 19 timeline rows and indexes 0 through 18;
- `ledger_audit_count == 1`;
- `anchored_verification_count == 1`;
- `post_replay_snapshot_provider_call_count == 1`;
- `root_attestation_required is False`;
- `root_attestation_present is False`;
- `source_bytes_unchanged is True`;
- `critical_package_bytes_unchanged is True`;
- `source_file_count == 9`;
- `critical_package_file_count == 11`;
- `transaction_rerun_count == 0`;
- `semantic_rerun_count == 0`;
- `corridor_rerun_count == 0`;
- `ledger_recollection_count == 0`;
- `crypto_collection_count == 0`;
- every provider, network, Gemini, creation, and effect counter exact integer
  zero.

Any contradiction yields `FAIL_CLOSED`. A bool is never accepted as integer
zero or one. An empty error tuple alone never creates `PASS`. Manifest or
stored Verification byte mutation after fresh verification prevents `PASS`.

## 15. Pure Timeline Reconstruction

The exact algorithm is:

1. require the exact accepted Ledger type;
2. require contiguous Ledger indexes 0 through 18;
3. require the exact committed artifact-type sequence;
4. require one transaction-start entry at index 0;
5. pair every Ledger entry positionally with its Manifest artifact ref and
   artifact hash;
6. require exact artifact ID equality;
7. require independently accepted artifact hash equality;
8. require every dependency exists;
9. require every dependency points to an earlier index;
10. require no self-dependency;
11. require no cycle;
12. create one TimelineRow per accepted Ledger entry;
13. preserve exact Ledger order;
14. verify exact three Root-final rows;
15. return no partial timeline when any required check fails.

Replay never repairs or reorders an invalid Ledger, drops an entry, invents a
dependency, replaces an artifact ID, repairs a Root owner, infers missing
selected-offer data, derives current timestamps, or adds random IDs.

Repeated Replay over identical accepted inputs produces deeply equal reports
and equal plain JSON projections.

## 16. Dependency, Root, And Evidence Boundary

The committed Ledger validator and independent Ledger auditor remain the
primary dependency, ownership, and authority/evidence contracts. Replay does
not create a conflicting second policy registry. It adds only exact positional
Manifest binding, timeline reconstruction, and no-rerun/no-effect evidence.

Replay preserves:

- exact 29 dependencies, backward only, with an acyclic graph;
- exact selected-offer chain;
- exact `semantic_causal` hold packet lineage;
- exact packet and receipt lineage;
- transaction scope as non-authoritative;
- BSEP projections as bounded context;
- cross-root BSEP as advisory, not a fourth Root;
- canonical semantic evidence as advisory evidence;
- receipts as evidence only;
- exactly one ClientRoot, AirlineRoot, and BankRoot final;
- no provider-, Ledger-, Crypto-, or Replay-created authority;
- no authority transfer between Roots.

For the official package, the accepted recorded facts include:

- `airline_hold_commit_packet:semantic_causal:001`
- `hold:semantic_causal:001`

Production Replay code must not hardcode Offer A. Offer A and Offer B
temporary fixtures preserve their own exact suffixes.

## 17. Secret And Raw-Observation Boundary

Replay preserves secret scan `PASS` and keeps raw observation material outside
canonical reconstruction. Raw prompts and responses remain auxiliary
observations and are not read to reconstruct canonical meaning.

The Replay Report contains no raw prompt, raw response, API key, private key,
card data, passport data, payment token, or credential.

Replay errors contain no arbitrary source text, object or exception `repr`,
memory address, absolute path, or secret value. Canonical Ledger identity
contains no raw secret or raw provider text.

## 18. Exact-Package Collector Lifecycle

Plan one future in-memory collector:

1. receive one exact `AirlineSealedTraceReplayPackageSnapshotV01`;
2. validate exact nine-source-file order;
3. validate exact Manifest bytes;
4. validate exact stored Verification bytes;
5. validate one accepted read-only Ledger audit;
6. strictly reconstruct only persisted typed Ledger, Manifest Core, unsigned
   Envelope, and stored unanchored Verification contracts;
7. do not reconstruct the runtime SourceBundle;
8. build the ExpectedIdentity verifier adapter after audit `PASS`;
9. receive one explicit expected Manifest Core hash;
10. invoke anchored B2b verification exactly once;
11. require anchored `PASS`;
12. invoke pure timeline reconstruction exactly once;
13. invoke the post-Replay snapshot provider exactly once;
14. require its exact snapshot type and exact equality with the initial
    snapshot;
15. derive final Replay Report status;
16. return one immutable Replay Report.

The collector performs no filesystem discovery or package search; no
provider/network/Gemini call; no transaction, Corridor, Ledger, or Crypto
recollection; no package write; and no Replay output write.

### Post-Replay Snapshot Provider

Plan the collector-only injected capability:

```text
AirlineSealedTraceReplayPostVerificationSnapshotProviderV01 =
    Callable[[], object]
```

Rules:

- it is not part of `AirlineSealedTraceReplayInputV01`;
- it is never retained in an input, row, report, cache, or global;
- it is invoked exactly once;
- invocation occurs after fresh anchored B2b verification and pure timeline
  reconstruction, but before final Replay Report status derivation;
- it must return the exact
  `AirlineSealedTraceReplayPackageSnapshotV01` type;
- no retry, search, or fallback;
- an ordinary provider exception becomes one stable fail-closed reason;
- exception text and `repr` are never retained;
- initial and post-Replay snapshots must be exactly equal;
- equality covers all nine source files, Manifest bytes, and stored
  Verification bytes.

The required success count is:

`post_replay_snapshot_provider_call_count == 1`

The filesystem runner supplies this callback by rereading the same explicit
package directory. The in-memory collector performs no package discovery.

## 19. Filesystem Runner And Single-Output Boundary

Plan a future read-only runner that receives one explicit package directory
and one explicit trusted anchor source. It:

- rejects package-directory and critical-file symlinks;
- rejects missing, non-regular, or unreadable critical files;
- reads exact bytes in frozen source order;
- performs no glob/rglob discovery, latest selection, or fallback selection;
- performs no repair, normalization, reserialization, rewrite, deletion, or
  anchor modification.

The filesystem runner supplies the post-Replay snapshot callback by rereading
the same explicit package directory exactly once.

The Replay Report is never written inside the sealed package. Its output
target must:

- be one explicit path outside the selected package directory;
- reject a target inside the package after safe path resolution;
- reject an existing file, existing symlink, or dangling symlink;
- require an existing regular non-symlink parent directory;
- precompute and validate the complete JSON text before opening the target;
- serialize only the exact public Replay Report projection;
- use exclusive creation;
- track invocation ownership immediately after successful open;
- append exactly one terminal newline;
- reread exact bytes after close;
- strict-parse the JSON;
- require semantic equality with the in-memory plain report.

On partial write, flush or close failure, reread or UTF-8 failure, JSON parse
failure, exact-text mismatch, or parsed-object mismatch, the writer removes
only the output file created by that invocation. It never removes a
pre-existing user path.

If cleanup fails, the runner returns a distinct stable cleanup-failed reason.
A failed Replay run never leaves a partial successful Replay Report.

No human explanation is created by the runtime Replay operation. Human
explanation belongs to later independent closure evidence.

## 20. Required Positive Test Groups

Plan parameterized positive coverage for:

- Offer A and Offer B temporary package Replay `PASS`;
- A/B/A and B/A/B isolation;
- repeated Replay equality;
- exact 19 timeline rows, 29 dependencies, and 3 Root finals;
- exact one final per Root;
- exact artifact sequence and positional artifact ref/hash binding;
- exact chain order, transaction ID, Ledger ID, and source-package ref;
- exact selected-offer and `semantic_causal` hold lineage;
- exact packet and receipt lineage;
- exact Root ownership and authority/evidence classes;
- one fresh anchored verification and one read-only Ledger audit;
- exact initial/post 11-file snapshot equality;
- exactly one post-Replay snapshot-provider call;
- exact stored unanchored Verification contract;
- exact fresh anchored `PASS` contract;
- exact unsigned placeholder remains unverified;
- deterministic Replay ID equality;
- exact source-file count 9 and critical-file count 11;
- transaction rerun count 0;
- zero semantic/Corridor reruns, Ledger recollection, and Crypto collection;
- zero provider/network/Gemini calls;
- zero Replay-created authority, permission, action, packet, receipt, or
  FinalOutput;
- zero real-world effects;
- unchanged source/package bytes;
- deeply immutable report and JSON-safe plain projection;
- acceptance of auxiliary non-sealed actor files;
- `root_attestation_present == false` without blocking Base Replay;
- successful exclusive external Replay Report write;
- output reread and semantic equality;
- package remains unchanged.

Tests must not be padded merely to increase counts.

## 21. Required Fail-Closed Test Groups

Plan parameterized mutation groups rather than duplicate test functions.

### Anchor And Crypto

- missing, malformed, or wrong valid expected anchor;
- automatic Envelope self-hash substitution;
- missing fresh anchored Verification or status other than `PASS`;
- external anchor absent or unverified;
- one internal Crypto flag false;
- changed Manifest hash, chain tail, or source-package hash;
- malformed stored Verification;
- tracked E2 Verification used without fresh B2b verification.

### Package

- missing package or package symlink;
- missing, symlink, non-regular, or unreadable critical file;
- source, Manifest, or stored Verification bytes change during Replay;
- wrong package ref;
- additional Manifest source or artifact ref;
- unrelated auxiliary file remains acceptable.

### Snapshot Lifecycle

- wrong initial snapshot type;
- malformed nine-source order;
- wrong Manifest artifact ref;
- wrong stored Verification artifact ref;
- bytearray or memoryview input;
- post-Replay provider wrong return type;
- provider exception;
- provider invoked zero or more than one time;
- one source byte changes;
- Manifest byte changes;
- stored Verification byte changes;
- honest snapshot failure remains JSON-safe.

### Verification Moments

- stored report changed from `SELF_CONSISTENT_UNANCHORED` to `PASS`;
- stored report carries an expected hash;
- stored external-anchor flag true;
- stored signature falsely verified;
- fresh report identity differs from Envelope;
- fresh report expected hash differs from trusted input;
- fresh signature falsely verified.

### Ledger And Timeline

- malformed Ledger or 18/20 entries;
- non-contiguous or duplicate index;
- duplicate artifact ID;
- wrong artifact sequence or mixed transaction ID;
- missing, later, self, or cyclic dependency;
- wrong edge count or Root owner;
- cross-root advisory classified as a fourth Root;
- missing or duplicate Root final;
- receipt classified as authority or permission;
- provider-created Root artifact;
- unknown authority or evidence class;
- wrong artifact ref/hash position;
- changed timeline row order or one wrong row artifact hash;
- partial timeline with caller-supplied `PASS`.

### Report Contract

- wrong report type or direct caller `PASS`;
- one false verification flag or only 18 rows;
- malformed/mutable error container or unknown reason;
- bool used as integer;
- nonzero rerun count;
- nonzero Replay-created authority, permission, action, packet, receipt, or
  FinalOutput count;
- nonzero real-world-effect count;
- honest `FAIL_CLOSED` report remains contract-valid and JSON-safe;
- validators do not leak ordinary shape exceptions.

### Runner Output

- output target already exists;
- output target is a symlink;
- dangling symlink target;
- output path resolves inside package;
- partial write;
- close failure;
- reread mismatch;
- parsed-object mismatch;
- cleanup failure;
- no partial output remains after ordinary failure.

## 22. State Isolation

Replay handles one transaction per invocation. It prohibits module-global
active Replay, package, anchor, Manifest, Ledger, or transaction state;
mutable Replay-result or trusted-anchor registries; semantic-changing caches;
and cross-run contamination.

Future tests prove:

- A after B remains A;
- B after A remains B;
- failure after success does not mutate prior success;
- success after failure remains deterministic;
- caller mutation cannot alter built input or report;
- repeated plain projections return independent JSON trees.

## 23. Domain And Universal Core Boundary

The first implementation remains Airline-domain local.

Planned files:

- `hedgehog/domains/airline/sealed_trace_replay_v01.py`
- `tests/test_airline_sealed_trace_replay_v01.py`
- `hedgehog/domains/airline/sealed_trace_replay_collector_v01.py`
- `tests/test_airline_sealed_trace_replay_collector_v01.py`
- `demo/run_airline_sealed_trace_replay_v01.py`
- `tests/test_airline_sealed_trace_replay_v01_runner.py`

Do not create `hedgehog/replay.py`, `hedgehog/sealed_replay.py`, a universal
Ledger replayer, generic event-sourcing framework, blockchain or consensus
abstraction, distributed log, universal Manifest schema, or Airline import in
universal Hedgehog OS core.

A universal sealed-trace reconstruction ABI may be considered only after two
independent domains expose the same stable laws and a separate extraction
preflight is approved.

## 24. Lean Implementation Program

### Slice A — Dedicated Preflight

This task. Documentation only. No code, tests, or Replay.

### Slice B — Contracts And Pure Replay Verifier

Planned files:

- `hedgehog/domains/airline/sealed_trace_replay_v01.py`
- `tests/test_airline_sealed_trace_replay_v01.py`

Scope: constants and closed reasons; frozen critical-package snapshot, Replay
input, TimelineRow, and Report; deep immutability; strict validators; derived
status and deterministic Replay ID; JSON-safe projection; deterministic
19-row reconstruction; dependency/order, Manifest position, Root/evidence,
and lineage checks. No file I/O, B2b invocation, package parsing, provider,
network, or Gemini.

### Slice C — Exact-Package Collector And Read-Only Runner

Planned files:

- `hedgehog/domains/airline/sealed_trace_replay_collector_v01.py`
- `tests/test_airline_sealed_trace_replay_collector_v01.py`
- `demo/run_airline_sealed_trace_replay_v01.py`
- `tests/test_airline_sealed_trace_replay_v01_runner.py`

Scope: explicit immutable package bytes; strict persisted-contract
reconstruction; one independent read-only Ledger audit; ExpectedIdentity
adapter; one fresh anchored B2b verification; one pure Replay reconstruction;
one post-Replay snapshot observation; explicit package/output paths;
11-file package-byte stability; exclusive output with failure cleanup; no
discovery, transaction, Corridor, Ledger/Crypto recollection,
provider/network/Gemini, package write, or Root Attestation.

### Slice D — Independent Official Replay Audit And Closure

Scope: one official read-only Replay over the existing package; one
independent Replay audit log; one artifact-backed human explanation; one
Replay checkpoint; AGENTS sync; unchanged official package and anchor; no
real provider, transaction rerun, or production claim.

Only Slice D independent audit `PASS` closes Base Airline Sealed Trace Replay
v0.1.

## 25. Next-Gate Policy

After Base Replay closes, return to explicit review. Do not automatically
activate Root Attestation, Attested Replay, universal Replay extraction,
production connectors or package, real payment/ticketing, public auditor
packaging, Marennya, UP, NeedleFactory, or Middle Factory.

The optional Root Attestation profile remains deferred.

The final all-real LLM full-stack run remains scheduled only after Base Replay
closes offline. This preflight does not authorize that run.

## 26. Definition Of Done

This preflight records deterministic sealed-trace reconstruction; the closed
Crypto and historical anchor boundaries; fresh anchored B2b verification; no
unanchored Replay success; exact `19/29/3`, nine-source, and eleven-critical
geometry; actual persisted package fields; ExpectedIdentity adapter limits;
stored/E2/Replay report separation; optional Root Attestation; exact Replay
package snapshot, input, row, and expanded public report contracts; exact
stored/fresh Verification moments; deterministic Replay ID; derived
fail-closed status; timeline algorithm; one post-Replay snapshot observation;
exact 9/11 byte stability; transaction-rerun evidence; exclusive external
output and rollback; positive, mutation, and isolation groups; package/anchor
immutability; Airline-domain ownership; and lean Slices A/B/C/D.

- final_preflight_status: `READY_FOR_REVIEW`
- replay_implemented: `false`
- replay_operation_count: `0`
- root_attestation_required: `false`
- universal_extraction_deferred: `true`
- next_implementation_gate:
  `airline_sealed_trace_replay_verifier_v01_slice_b_contracts_and_pure_verifier`
