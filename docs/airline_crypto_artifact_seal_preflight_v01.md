# Airline Crypto Artifact Seal v0.1 Preflight

## Header

- document_id: airline_crypto_artifact_seal_preflight_v01
- document_status: PREFLIGHT
- preflight_status: READY_FOR_REVIEW
- observed_base_head: 533f280
- planning_only: true
- runtime_modified: false
- tests_modified: false
- schemas_modified: false
- crypto_code_created: false
- hashes_computed: false
- manifest_created: false
- seal_created: false
- signature_created: false
- private_key_accessed: false
- key_management_implemented: false
- replay_implemented: false
- provider_called: false
- network_called: false
- gemini_called: false
- real_world_effects_count: 0
- production_ready_claimed: false
- production_security_claimed: false

This preflight creates no cryptographic artifact. It only freezes the
proof-grade v0.1 design and implementation order.

## Closed Source Basis

Committed basis:

- Ledger Slice B contracts and validators: CLOSED
- Ledger Slice C exact-source collector: CLOSED
- Ledger Slice D one-transaction integration: CLOSED
- Ledger Slice E1 read-only auditor and timeline: CLOSED
- Ledger Slice E2 completed-package audit: PASS
- current checkpoint commit: 533f280
- Ledger geometry: 19 entries / 29 dependency edges / 3 Root finals
- ClientRoot final count: 1
- AirlineRoot final count: 1
- BankRoot final count: 1
- cross-root advisory is not a fourth Root
- source package passed independent audit
- source bytes were unchanged during audit/rendering
- provider/network/Gemini calls during audit: 0
- real-world effects: 0

Historical source evidence package:

`.tmp/airline_transaction_artifact_ledger_slice_e2/airline_transaction_artifact_ledger_slice_e2_offline_f244512`

Rules:

- the E2 package is read-only evidence
- future implementation must not overwrite it
- production code must not hardcode this path
- tests must generate temporary source packages
- future official Crypto integration must use a new explicit package directory

## Cryptographic Claim Boundary

Crypto Artifact Seal records cryptographic integrity and continuity of a
declared artifact set.

Crypto Artifact Seal does not prove semantic truth.

Crypto Artifact Seal does not grant permission.

Crypto Artifact Seal does not create authority.

Crypto Artifact Seal does not authorize payment, ticketing, booking, or any
other action.

Crypto Artifact Seal does not make provider output trusted.

Crypto Artifact Seal does not repair an invalid Ledger or transaction.

Crypto Artifact Seal does not create FinalOutput.

An unsigned hash manifest does not prove origin or signer identity.

A self-consistent manifest is not automatically a trusted manifest.

Use the term:

proof-grade unsigned integrity seal

Do not use:

- production signature
- authenticated seal
- non-repudiation seal
- tamper-proof package

Do not claim:

- authenticity without a trusted signing key
- non-repudiation
- legal signing
- trusted timestamping
- confidentiality
- encryption
- tamper-proof storage
- rollback protection
- production key custody
- hardware-backed keys
- HSM
- PKI
- certificate-chain validation
- production cryptographic security

## Domain / Universal Core Boundary

The first implementation remains an Airline-domain projection.

Planned domain files may be:

Slice B:

- `hedgehog/domains/airline/crypto_artifact_seal_v01.py`
- `tests/test_airline_crypto_artifact_seal_v01.py`

Slice C:

- `hedgehog/domains/airline/crypto_artifact_seal_collector_v01.py`
- `tests/test_airline_crypto_artifact_seal_collector_v01.py`

Slice D may integrate into the existing Airline deterministic/live package
writer and its existing tests.

Slices E1 and E2 may add anchor publication, an independent Airline Crypto
audit, and a human explanation.

Do not create:

- `hedgehog/crypto.py`
- a generic Ledger/Crypto kernel
- a generic universal seal service
- a universal manifest schema
- Airline imports in universal Hedgehog OS core

Extraction rule:

A generic Hedgehog OS integrity-seal core may be considered only after at
least two independently implemented domain projections expose the same stable
laws and a separate extraction preflight is approved.

Universal laws that may later be extracted include:

- deterministic canonical bytes
- domain separation
- explicit hash algorithm
- explicit ordered artifact set
- external trusted anchor
- fail-closed verification
- evidence is not authority
- a hash is not truth
- a signature is not permission

Airline-specific names and the fixed 19-entry geometry remain domain-local.

## Exact Sealed Scope

Two separate integrity layers are frozen.

### 5.1 Canonical Ledger-Entry Layer

Seal exactly the 19 accepted Ledger entries in `ledger_index` order.

For each entry, the canonical seal projection contains only:

- canonicalization_profile_id
- ledger_id
- transaction_id
- ledger_index
- event_type
- artifact_type
- artifact_id
- root_owner
- created_by
- authority_class
- evidence_class
- depends_on
- canonical_hash_input

Do not include:

- Python object repr
- memory address
- mutable runtime object
- wall-clock-generated random value
- raw provider text
- raw prompt
- raw response
- raw passport/card/IBAN/payment token
- API key
- credentials
- private key
- unbounded private profile

The accepted Ledger must remain:

- PASS
- 19 entries
- 29 dependency edges
- 3 Root finals
- exact artifact-type sequence
- exact one ClientRoot/AirlineRoot/BankRoot final
- one transaction_id
- source refs consistent
- secret boundary PASS
- real-world effects 0

### 5.2 Exact Source-Package Byte Layer

Bind the seal to the exact bytes of these nine source files:

- airline_transaction_artifact_ledger.json
- summary.json
- secret_scan.json
- semantic_to_contract_causal_run.json
- semantic_to_contract_bridge.json
- integrated_deterministic_airline_summary.json
- tri_party_airline_bsep_packet.json
- tri_party_airline_bsep_validation.json
- tri_party_airline_bsep_side_projections.json

Hash the exact file bytes, not a reserialized replacement.

Use repository-relative basenames in the manifest, never absolute paths.

The following are not part of the canonical sealed source set:

- raw provider prompts
- raw provider responses
- actor console text
- E1 human timeline
- E1 audit JSON
- future seal verification report
- future human Crypto story
- unrelated files in the artifact directory

Their exclusion must be explicit.

Do not claim that the entire directory is sealed.

Adding, deleting, replacing, or reordering an item inside the declared
canonical set must be detected.

Auxiliary files outside the declared canonical set do not silently become
sealed artifacts.

## Canonicalization Profile V0.1

Profile ID:

`hedgehog_airline_json_c14n_v01`

Canonicalization applies only to:

- the 19 Ledger-entry seal projections
- hash-chain link objects
- the source-package index object
- the manifest core

It does not replace exact-byte hashing of the nine source files.

Required canonical JSON behavior:

- UTF-8 output
- no UTF-8 BOM
- object keys sorted deterministically
- compact separators with no insignificant whitespace
- `ensure_ascii = false`
- no trailing newline inside canonical bytes
- object keys must be strings
- arrays preserve order
- strings preserve exact Unicode code points
- strings contain valid Unicode scalar values
- lone surrogate code points are rejected
- no Unicode normalization is silently applied
- canonical JSON text is encoded using strict UTF-8
- booleans remain distinct from integers
- null is allowed only where the frozen contract permits it
- integers must be within signed 64-bit range
- floats are forbidden in canonical seal objects
- NaN and Infinity are forbidden
- negative zero as a float is forbidden
- duplicate JSON object keys are rejected
- arbitrary objects, dataclasses, MappingProxyType, tuples, and enums must be
  projected explicitly before canonicalization
- no fallback to `str(value)`
- no Python repr
- no hidden current time
- no random nonce in v0.1
- no dictionary-insertion-order dependence

Intended standard-library serialization shape, recorded without executing it
in this preflight:

```python
json.dumps(
    value,
    ensure_ascii=False,
    sort_keys=True,
    separators=(",", ":"),
    allow_nan=False,
)
```

The implementation must first validate the closed value domain. Calling
`json.dumps` alone is not sufficient validation.

## Hash Profile and Domain Separation

Frozen profile:

- hash_algorithm: SHA-256
- hash_encoding: lowercase_hex
- digest length: 64 lowercase hexadecimal characters
- implementation source: Python standard-library hashlib
- no custom digest algorithm
- no encryption
- no HMAC in v0.1
- no secret key
- no public/private signing key

Every structured canonical object that is hashed must carry an explicit domain label.

Required domain labels:

- hedgehog-airline-seal-v01:ledger-entry
- hedgehog-airline-seal-v01:chain-genesis
- hedgehog-airline-seal-v01:chain-link
- hedgehog-airline-seal-v01:source-package-index
- hedgehog-airline-seal-v01:manifest-core

The exact source-file byte digests are the sole v0.1 exception: each
`source_file_hash` is raw `SHA256(exact_file_bytes)` so it remains an exact
byte fingerprint. The domain-separated source-package-index hash binds each
digest to its frozen basename, position, and transaction.

No raw string concatenation of variable-length fields is permitted for
structured hashes.

Hash canonical JSON objects for all structured hashes.

### 7.1 Ledger Entry Hash

For each ledger entry i:

```text
artifact_hash_i =
SHA256(
    canonical_json(
        {
            "domain": "hedgehog-airline-seal-v01:ledger-entry",
            "projection": exact_entry_projection
        }
    )
)
```

### 7.2 Ordered Chain

```text
chain_genesis_hash =
SHA256(
    canonical_json(
        {
            "domain": "hedgehog-airline-seal-v01:chain-genesis",
            "ledger_id": ledger_id,
            "transaction_id": transaction_id,
            "artifact_count": 19
        }
    )
)
```

For each ledger index i:

```text
chain_link_i =
SHA256(
    canonical_json(
        {
            "domain": "hedgehog-airline-seal-v01:chain-link",
            "ledger_index": i,
            "previous_chain_hash":
                chain_genesis_hash when i == 0 else chain_link_(i-1),
            "artifact_hash": artifact_hash_i
        }
    )
)
```

Frozen chain facts:

- chain_head_hash = chain_link_0
- chain_tail_hash = chain_link_18
- reordering entries changes the chain
- deleting or duplicating an entry changes the chain
- dependencies remain checked by Ledger/audit contracts, not inferred from
  the hash chain

A hash chain records ordered continuity. It does not prove semantic truth.

### 7.3 Exact Source-Package Index

For each of the nine required files:

```text
source_file_hash =
SHA256(exact_file_bytes)
```

Create an ordered source-package index using the frozen nine-file order.

```text
source_package_hash =
SHA256(
    canonical_json(
        {
            "domain": "hedgehog-airline-seal-v01:source-package-index",
            "transaction_id": transaction_id,
            "files": [
                {
                    "relative_ref": basename,
                    "sha256": exact_file_hash
                }
            ]
        }
    )
)
```

The source-package index must not contain absolute paths.

## Manifest Core and Envelope

Planned proof-grade types:

- AirlineCryptoArtifactSealManifestCoreV01
- AirlineCryptoArtifactSealEnvelopeV01
- AirlineCryptoArtifactSealVerificationReportV01

Required Manifest Core fields:

- seal_id
- seal_version
- transaction_id
- ledger_id
- source_package_ref
- canonicalization_profile_id
- hash_algorithm
- hash_encoding
- ledger_entry_count
- dependency_edge_count
- root_final_count
- ordered_artifact_refs
- ordered_artifact_hashes
- chain_genesis_hash
- chain_head_hash
- chain_tail_hash
- source_file_count
- ordered_source_file_refs
- ordered_source_file_hashes
- source_package_hash
- ledger_document_byte_hash
- previous_manifest_ref
- signature_placeholder_present
- signature_verified
- source_audit_status
- secret_scan_passed
- raw_secret_included
- seal_created_authority_count
- seal_created_permission_count
- seal_created_action_count
- real_world_effects_count

Required v0.1 values:

- seal_version: airline_crypto_artifact_seal_v01
- canonicalization_profile_id: hedgehog_airline_json_c14n_v01
- hash_algorithm: SHA-256
- hash_encoding: lowercase_hex
- ledger_entry_count: 19
- dependency_edge_count: 29
- root_final_count: 3
- source_file_count: 9
- previous_manifest_ref: null
- signature_placeholder_present: true
- signature_verified: false
- source_audit_status: PASS
- secret_scan_passed: true
- raw_secret_included: false
- seal_created_authority_count: 0
- seal_created_permission_count: 0
- seal_created_action_count: 0
- real_world_effects_count: 0

Deterministic manifest identity:

- `source_package_ref` is the logical source package basename only
- `source_package_ref` is derived from the selected source directory basename,
  not accepted as an arbitrary caller-selected value
- `source_package_ref` is non-empty
- `source_package_ref` contains no absolute path
- `source_package_ref` contains no path separators
- `source_package_ref` is not "." or ".."
- moving the package to another parent directory does not change the manifest
- `seal_id` is `airline_crypto_artifact_seal_v01:<source_package_hash>`
- arbitrary caller-selected `seal_id` is not accepted for a PASS-capable
  manifest

Positional manifest bindings:

- `ordered_artifact_refs` length is exactly 19
- `ordered_artifact_hashes` length is exactly 19
- `ordered_artifact_refs[i]` equals the exact `artifact_id` of Ledger entry i
- item i binds that exact artifact ref to artifact hash i and `ledger_index` i
- artifact refs are unique
- `ordered_source_file_refs` length is exactly 9
- `ordered_source_file_hashes` length is exactly 9
- item i binds source ref i to source hash i
- source refs exactly match the frozen required nine-file order
- source refs are unique
- `ledger_document_byte_hash` exactly equals the source-file hash paired with
  `airline_transaction_artifact_ledger.json`

Conceptual manifest core hash:

```text
manifest_core_hash =
SHA256(
    canonical_json(
        {
            "domain": "hedgehog-airline-seal-v01:manifest-core",
            "manifest_core": manifest_core
        }
    )
)
```

Do not place `manifest_core_hash` inside the object being hashed. No self-hash
is permitted.

The envelope contains:

- manifest_core
- manifest_core_hash
- signature:
  - mode: UNSIGNED_PLACEHOLDER
  - algorithm: NONE
  - key_id: ""
  - value: ""
  - verified: false

A signature placeholder must never be reported as a verified signature.

## External Trust Anchor

A manifest that stores its own hashes can prove internal self-consistency only.

An attacker who can rewrite both artifacts and manifest can recompute all
unanchored hashes.

Therefore, final proof-grade verification must require an explicit trusted
`expected_manifest_core_hash` supplied out of band.

When supplied, `expected_manifest_core_hash` must be exactly 64 lowercase
hexadecimal characters. When no external anchor is supplied, the input and
verification-report field are `null`, `external_anchor_supplied` is false,
and verification may be SELF_CONSISTENT_UNANCHORED but never PASS.

The verifier must distinguish:

1. SELF_CONSISTENT_UNANCHORED

   - artifact hashes match the supplied manifest
   - chain matches the supplied manifest
   - no trusted external anchor was provided
   - must not be reported as final PASS
   - must not be called authenticated or tamper-proof

2. PASS

   - all internal checks pass
   - an explicit expected_manifest_core_hash was supplied
   - the recomputed manifest_core_hash equals that trusted expected value

3. FAIL_CLOSED

   - any check fails

Required API rule:

`verify_airline_crypto_artifact_seal_v01(...)` must not return final PASS
without an explicit `expected_manifest_core_hash`.

Do not let `manifest.manifest_core_hash` serve as its own trusted expected
value.

Lifecycle rule:

- Slice B implements contracts and verifier statuses
- Slice C collection accepts an optional `expected_manifest_core_hash`
- without that value, successful internal verification is
  SELF_CONSISTENT_UNANCHORED, never PASS
- Slice D integration creates one manifest and one unanchored verification
  report
- Slice D must not claim final anchored PASS
- the value computed by the current collection process must never be treated as
  its own out-of-band expected value

Required coordinated-tamper test:

- modify a source artifact
- recompute its stored artifact hash
- recompute the ordered chain
- recompute the source-package hash
- recompute the manifest core hash
- keep the original trusted expected_manifest_core_hash
- verification must FAIL_CLOSED

Required missing-anchor test:

- internally self-consistent envelope
- no trusted expected_manifest_core_hash
- result must be SELF_CONSISTENT_UNANCHORED, not PASS

Future independent Crypto audit must record at least:

- manifest_core_hash
- chain_tail_hash
- source_package_hash
- transaction_id
- ledger_id
- source package reference

That committed audit/checkpoint becomes the proof-level external anchor.

Do not describe Git as a production PKI or production trust service.
Do not describe Git as signer authentication or production trust.

## Exact-Source and TOCTOU Boundary

The future sealer must operate on one explicit source package.

No directory search.
No latest-directory selection.
No historical default.
No reconstruction.
No semantic rerun.
No corridor rerun.
No Ledger recollection.

Required sequence:

1. explicit source directory selected
2. exact nine-file set validated as regular non-symlink files
3. exact bytes of all nine files frozen before audit
4. committed E1 audit called exactly once
5. all nine source files reread immediately after audit
6. post-audit bytes must equal the original frozen snapshot
7. seal is built only from the original frozen byte snapshot and accepted
   audit/Ledger
8. all nine files reread after seal collection
9. post-seal bytes must equal the original frozen snapshot
10. any observed mismatch fails closed

Proof-grade v0.1 uses explicit before/after byte snapshots.

Unless an atomic filesystem snapshot is used, it does not claim resistance to a
privileged attacker able to modify and restore a file entirely between
observations.

Do not claim that every transient filesystem mutation is detectable.

Reject:

- symlink source files
- non-regular files
- path traversal
- absolute file refs in manifest
- duplicate file refs
- missing required file
- unreadable file
- file changed between audit and hashing
- file changed during seal creation
- source package audit not PASS

The seal collector must not repair, rewrite, normalize, or reserialize source
files.

## Planned Implementation Slices

### Slice A - This Preflight

Docs only.

### Slice B - Contracts, Canonicalization, Validators

Planned files only:

- `hedgehog/domains/airline/crypto_artifact_seal_v01.py`
- `tests/test_airline_crypto_artifact_seal_v01.py`

Scope:

- frozen dataclasses/contracts
- strict canonical value validator
- deterministic canonical serializer
- SHA-256 helper
- entry hash
- source-package index hash
- ordered chain
- manifest core
- envelope
- verification report
- anchored vs unanchored status
- no file I/O
- no provider/network/Gemini
- no integration
- no Replay

### Slice C - Exact-Source Collector

Planned files only:

- `hedgehog/domains/airline/crypto_artifact_seal_collector_v01.py`
- `tests/test_airline_crypto_artifact_seal_collector_v01.py`

Scope:

- explicit immutable source bundle
- accepted E1 audit report
- exact nine source-file byte snapshots
- exact accepted Ledger
- source byte stability
- no source reconstruction
- one manifest/envelope collection
- optional `expected_manifest_core_hash` input
- missing expected_manifest_core_hash yields SELF_CONSISTENT_UNANCHORED, not
  PASS
- no file writer
- no runtime rerun

### Slice D - Existing Transaction/Package Integration

Scope:

- integrate into the existing Airline offline/live artifact package
- one semantic transaction
- one corridor execution
- one Ledger
- one E1 source audit
- one Crypto seal collection
- one unanchored seal verification report
- no anchored PASS claim
- no second transaction
- no second Ledger
- no second audit
- no provider/network/Gemini calls added by Crypto
- exactly one manifest JSON
- exactly one verification JSON
- no Replay

Do not freeze exact integration filenames until Slice D preflight/review of
the then-current runner.

### Slice E1 - Anchor Publication

Scope:

- create one official offline completed package
- independently confirm internal self-consistency
- record manifest_core_hash, chain_tail_hash, source_package_hash,
  transaction_id, ledger_id, and source_package_ref
- commit the expected_manifest_core_hash in a separate tracked anchor
  document/checkpoint
- do not claim anchored PASS in the same process or same pre-anchor state
- no real provider required
- no Replay

### Slice E2 - Anchored Audit

Scope:

- begin from a clean repository state after the E1 anchor commit
- load the expected_manifest_core_hash from the already committed anchor
- verify the existing package without rebuilding it
- only this phase may return final PASS
- create the independent Crypto audit/checkpoint
- artifact-backed human explanation
- no real provider required
- no Replay

Only after Slice E2 and independent Crypto audit PASS may Replay preflight
open.

Replay remains blocked until that condition is met.

## Required Future Fail-Closed Matrix

The dedicated preflight records tests for at least the following cases.

Canonicalization:

- same valid object produces identical bytes across repeated runs
- dictionary insertion order does not change canonical bytes
- list order remains significant
- non-string object key rejected
- float rejected
- NaN/Infinity rejected
- integer outside signed 64-bit rejected
- bool not accepted as integer
- arbitrary object rejected
- Python repr fallback forbidden
- duplicate JSON key rejected
- malformed UTF-8 rejected where source parsing is required
- lone surrogate code point rejected
- canonical JSON output is strict UTF-8

Ledger/source geometry:

- Ledger not PASS
- not 19 / 29 / 3
- wrong artifact sequence
- duplicate artifact ID
- wrong transaction ID
- wrong dependency
- cyclic dependency
- wrong Root owner
- wrong authority/evidence class
- missing Root final
- fourth Root claim
- receipt classified as permission
- provider-created authority/action
- nonzero real effect
- failed secret scan
- raw secret or provider text in canonical seal input

Hash and chain:

- changed canonical entry
- deleted entry
- duplicated entry
- reordered entry
- changed artifact hash
- changed previous-chain hash
- changed chain head
- changed chain tail
- malformed digest
- unsupported algorithm
- unsupported canonicalization profile
- changed exact source-file byte
- missing source file
- duplicate source file ref
- reordered source-file index
- source file refs not exactly in the frozen nine-file order
- source file ref/hash length mismatch
- source file ref/hash pairing mismatch
- duplicate source file ref
- changed source-package hash
- changed ledger document byte hash
- ledger_document_byte_hash differs from the hash paired with
  airline_transaction_artifact_ledger.json

Manifest:

- wrong transaction ID
- wrong ledger ID
- invalid source_package_ref
- source_package_ref differs from the selected source directory basename
- arbitrary caller-selected seal_id
- seal_id not derived from source_package_hash
- lied artifact count
- lied source-file count
- lied Root-final count
- ordered_artifact_refs length not 19
- ordered_artifact_hashes length not 19
- ordered_artifact_refs/hash pairing mismatch
- ordered_artifact_refs not bound to matching ledger_index
- duplicate artifact ref
- ordered_source_file_refs length not 9
- ordered_source_file_hashes length not 9
- ordered_source_file_refs/hash pairing mismatch
- duplicate source ref
- self-referential manifest hash attempt
- manifest core hash mismatch
- signature placeholder reported as verified
- signature algorithm other than NONE in placeholder v0.1
- non-empty signature value in placeholder v0.1
- seal-created authority/permission/action nonzero

External anchor:

- missing external expected manifest hash cannot return PASS
- expected manifest hash not exactly 64 lowercase hexadecimal characters fails
- wrong expected manifest hash fails
- coordinated artifact + manifest recomputation fails against original anchor
- manifest's own stored hash cannot serve as trusted anchor

State isolation:

- Offer A passes
- Offer B passes
- A/B/A isolated
- B/A/B isolated
- no module-global active transaction
- no module-global mutable manifest registry
- source objects remain byte-for-byte unchanged

Boundary:

- no provider/network/Gemini
- no config/secrets
- no real API
- no payment/ticket/booking
- no Root authority created
- no permission created
- no FinalOutput created
- no generic core
- no Replay

## Verification Report Contract

Planned fields for `AirlineCryptoArtifactSealVerificationReportV01`:

- verification_status
- transaction_id
- ledger_id
- manifest_core_hash
- expected_manifest_core_hash
- external_anchor_supplied
- external_anchor_verified
- canonicalization_profile_verified
- hash_algorithm_verified
- manifest_core_hash_verified
- ledger_document_byte_hash_verified
- artifact_hashes_verified
- chain_genesis_verified
- chain_order_verified
- chain_head_verified
- chain_tail_verified
- source_file_hashes_verified
- source_package_hash_verified
- ledger_geometry_verified
- root_ownership_verified
- authority_evidence_boundaries_verified
- secret_boundary_verified
- source_bytes_unchanged
- signature_mode
- signature_verified
- verification_errors
- provider_call_count
- network_call_count
- gemini_call_count
- seal_created_authority_count
- seal_created_permission_count
- seal_created_action_count
- real_world_effects_count

Required PASS values include:

- external_anchor_supplied: true
- external_anchor_verified: true
- signature_mode: UNSIGNED_PLACEHOLDER
- signature_verified: false
- all zero counters: 0

The report is verification evidence only.

It is not Root FinalOutput.
It is not permission.
It is not a receipt.
It is not semantic truth.

## Honest Limits

v0.1 provides:

- deterministic SHA-256 integrity
- ordered chain continuity
- exact package-byte binding
- explicit canonicalization
- anchored proof-grade verification when an external expected manifest hash is
  supplied

v0.1 does not provide:

- signer authentication
- source-origin authentication
- confidentiality
- encryption
- key rotation
- revocation
- trusted timestamp
- anti-rollback across packages
- distributed consensus
- blockchain
- production key custody
- production signature
- legal non-repudiation
- production security certification

A future signed version must use a vetted standard signature algorithm and
library, with an explicit key-management preflight. No custom signature
algorithm may be implemented.

Do not select or implement that future signature in this preflight.
