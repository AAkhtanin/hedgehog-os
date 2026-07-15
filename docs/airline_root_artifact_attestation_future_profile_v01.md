# Airline Root Artifact Attestation — Deferred Future Profile v0.1

- document_id: `airline_root_artifact_attestation_future_profile_v01`
- document_status: `DEFERRED_DESIGN`
- current_implementation_gate: `false`
- implementation_authorized: `false`
- blocks_base_sealed_replay: `false`
- optional_attested_replay_profile: `true`
- observed_base_head: `26ee0de`
- existing_crypto_v01_modified: `false`
- existing_package_modified: `false`
- existing_anchor_modified: `false`
- key_generated: `false`
- private_key_accessed: `false`
- signature_created: `false`
- provider_called: `false`
- network_called: `false`
- gemini_called: `false`
- real_world_effects_count: `0`

This document preserves a possible future strengthening profile.

It is not a task queue and does not authorize implementation.

## Scope Decision

Airline Root Artifact Attestation is technically valid but is not required to
demonstrate the current Hedgehog OS core architecture. It is deferred outside
the DeepTech core-demo critical path and does not block Base Airline Sealed
Trace Replay v0.1.

The former ten-signature, seven-slice preflight is not promoted into the
active roadmap. No Root Attestation implementation or key publication begins
now. No private key was generated or accessed, and no signature was created.

Base Replay may proceed using the closed Crypto Manifest, ordered chain,
source-package hash, Ledger, and committed external Manifest Core anchor.
With no attestation overlay:

- root_attestation_present: `false`
- replay_forbidden: `false`

## Closed Current Basis

- Airline Crypto Artifact Seal v0.1 is CLOSED at commit `26ee0de`.
- The existing official package remains unchanged.
- The existing Manifest Core anchor remains unchanged.
- Stored package Verification remains `SELF_CONSISTENT_UNANCHORED`.
- Independent E2 Verification remains `PASS` relative to the committed
  Manifest Core anchor.
- Existing package signature mode remains `UNSIGNED_PLACEHOLDER`.
- Existing `signature_verified` remains `false`.
- Crypto v0.1 proves integrity and continuity, not signer identity.

This future profile does not retrofit, rename, reinterpret, or modify Crypto
Artifact Seal v0.1.

## Replay Profiles

### Base Sealed Trace Replay

Base Replay verifies integrity, continuity, dependency order, recorded Root
ownership metadata, and reconstruction of the deterministic accepted trace.
It does not require Root signatures.

### Optional Attested Replay Profile

An optional future Attested Replay profile includes every Base Replay check
and additionally verifies a Root Attestation overlay when one is present. It
is not part of the current implementation gate.

The absence of Root Attestation does not forbid Base Replay.

## Optional Future Minimal Profile

The optional minimum uses three independent proof-level Root keypairs in
deterministic trusted key-set order:

1. ClientRoot
2. AirlineRoot
3. BankRoot

It creates one aggregate canonical commitment per Root and exactly three
Ed25519 signatures total:

- ClientRoot covers exact ordered artifact refs, hashes, and scopes for its
  three policy-owned artifacts.
- AirlineRoot covers exact ordered artifact refs, hashes, and scopes for its
  five policy-owned artifacts.
- BankRoot covers exact ordered artifact refs, hashes, and scopes for its two
  policy-owned artifacts.

The exact coverage is therefore `3/5/2` across ten policy-owned artifacts,
using three aggregate Root commitments rather than ten separate signatures.

Each future Root commitment binds:

- `transaction_id`;
- `ledger_id`;
- `source_manifest_core_hash`;
- `signer_root_id`;
- `signer_key_id`;
- `trusted_key_set_hash`;
- `policy_hash`;
- exact ordered artifact Ledger positions;
- exact artifact IDs;
- exact artifact types;
- exact artifact hashes;
- exact signature scopes;
- `attested_at`;
- validity window.

Future requirements remain fail-closed:

- separate trusted Root public keys;
- a non-self-bootstrapped trusted public-key set;
- cross-Root misuse rejection;
- private keys absent from Git, packages, reports, docs, logs, and errors;
- receipts remain evidence and are not Root-signed;
- advisory, provider, renderer, DRS, and child-cell objects cannot sign as a
  Root;
- signature validity does not create truth or authority;
- signature validity does not grant permission or execute an action;
- signature validity does not create a packet, receipt, or FinalOutput;
- verification `PASS` is derived and never trusted from caller input.

The former ten separate per-artifact signature-envelope design is not the
recommended future minimum. It may be reconsidered only as a maximal
industrial profile under a separate review.

## Future Trust Lifecycle

```text
commit trusted public-key set
→ later commit signed overlay
→ independent public-key-only verification
```

The commits may occur on the same day. Immutable commit ordering, not elapsed
calendar time, is the required trust-continuity property.

Git continuity is not PKI, legal identity, or trusted timestamping.
Production HSM, KMS, vault, and PKI remain outside the current proof program.
No key or trust document is created now.

## Relation To Replay

Base Airline Sealed Trace Replay v0.1 may proceed without Root Attestation
because the closed Crypto layer already supplies:

- canonical JSON;
- exact source-byte hashes;
- exact 19 artifact hashes;
- an ordered hash chain;
- Ledger-document hash;
- source-package hash;
- Manifest Core;
- a committed external Manifest Core anchor;
- independent anchored Verification `PASS`.

A future optional Attested Replay profile may additionally require the three
aggregate Root commitments. The final all-real integrated test may later
choose that stricter profile, but Root Attestation is not required to begin or
close Base Replay.

## Future Activation Rule

Root Artifact Attestation may re-enter the active roadmap only after explicit
future review. Possible reasons are productization, external auditor demand,
multi-organization Root provenance, a strict Attested Replay profile, a
second domain exposing the same stable signing laws, or preparation for
production key custody.

It does not activate automatically after Replay. No universal attestation
kernel is authorized.

## Current Gate

- deferred_profile_status: `DEFERRED_DESIGN`
- root_attestation_implementation_authorized: `false`
- base_replay_blocked_by_attestation: `false`
- next_immediate_gate:
  `airline_sealed_trace_replay_verifier_v01_preflight`
