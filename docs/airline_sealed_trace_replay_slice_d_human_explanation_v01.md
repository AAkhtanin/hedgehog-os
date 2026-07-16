# Airline Sealed Trace Replay v0.1 — Official Human Explanation

- document_status: HUMAN_EXPLANATION
- human_explanation_slice: airline_sealed_trace_replay_v01_slice_d2
- evidence_base_commit: 813289d
- official_replay_status: PASS
- independent_d1_audit_status: PASS
- base_replay_fully_closed: false
- closure_pending: full_canonical_docs_spec_manifest_sync
- runtime_rerun: false
- audit_rerun: false
- provider_called: false
- network_called: false
- gemini_called: false
- real_world_effects_count: 0

This document explains already committed evidence. It performs no Replay,
verification, transaction execution, audit, provider call, or filesystem
mutation of the sealed package.

## What Was Replayed

The official Replay examined one existing Airline transaction trace in the
sealed package
`airline_crypto_artifact_seal_slice_e1_offline_905844c`. The transaction was
not executed again. No semantic actor was called again, no Corridor phase was
executed again, and no Ledger or Crypto artifact was recollected. Replay
reconstructed the accepted event timeline from the sealed evidence.

The immutable machine result is
`docs/airline_sealed_trace_replay_slice_d_official_report_v01.json`. The
independent D1 evidence inspection is
`docs/audit_reports/auditor_airline_sealed_trace_replay_slice_d_official_replay_v01.log`.
This D2 document reads and explains those committed artifacts without
rerunning either operation.

## The Trust Chain

The evidence chain was:

```text
existing package bytes
→ Ledger
→ ordered artifact hashes and dependency chain
→ Manifest Core
→ committed expected Manifest Core hash
→ fresh anchored verification
→ deterministic Replay timeline
```

The committed external Manifest Core hash was the trust input. The Manifest's
own stored hash was not silently reused as its own external anchor.

The evidence identities were:

- Replay ID:
  `airline_sealed_trace_replay_v01:tri_airline_purchase:PAR-LIM:2026-08-12:client_001:29355a3b2f2b95bd6358d6085a801334d7fd7ca23438e6e2ce0618106edba12b`
- Transaction ID:
  `tri_airline_purchase:PAR-LIM:2026-08-12:client_001`
- Ledger ID:
  `airline_transaction_artifact_ledger:offer:mock_airline_al:PAR-LIM:001`
- Source package:
  `airline_crypto_artifact_seal_slice_e1_offline_905844c`
- Source-package hash:
  `5001bb70ca6841a2ec24c10efbb19452f444f2815887d604a12cb031e6ffd21f`
- Manifest Core hash:
  `29355a3b2f2b95bd6358d6085a801334d7fd7ca23438e6e2ce0618106edba12b`
- Expected Manifest Core hash:
  `29355a3b2f2b95bd6358d6085a801334d7fd7ca23438e6e2ce0618106edba12b`
- Chain-tail hash:
  `f41057a61eea458e8dc88cfe44bd5168806e2438fca60a29371af587bba19027`

## Two Verification Moments

### 1. Package-Time Stored Verification

- Status: `SELF_CONSISTENT_UNANCHORED`
- Expected external hash: absent
- External anchor supplied: `false`
- External anchor verified: `false`
- Signature mode: `UNSIGNED_PLACEHOLDER`
- Signature verified: `false`

This stored report recorded package-time self-consistency without claiming an
external anchor.

### 2. Replay-Time Fresh Verification

- Expected hash: supplied from the committed anchor
- Status: `PASS`
- External anchor supplied: `true`
- External anchor verified: `true`
- Signature mode: `UNSIGNED_PLACEHOLDER`
- Signature verified: `false`

The stored unanchored report was not rewritten or relabeled as anchored PASS.
The fresh result is a separate Replay-time verification moment.

## What Replay PASS Means

Replay `PASS` means the exact source-package bytes and the complete
eleven-file critical surface matched the accepted sealed evidence before and
after Replay. The Ledger identity, transaction identity, Manifest Core hash,
and committed expected external hash agreed.

It also means all nineteen artifact hashes matched their ordered Manifest
positions; the ordered chain and 29-edge dependency graph were intact; Root
ownership metadata and authority/evidence classifications matched; and the
nineteen-row timeline was reconstructed exactly. No package-byte change was
accepted between the initial and post-Replay observations.

## What Replay PASS Does Not Mean

Replay `PASS` does not prove or create:

- semantic truth;
- business truth;
- ticket authenticity in a real airline system;
- actual payment;
- actual booking;
- actual ticket issuance;
- signer authentication;
- PKI;
- non-repudiation;
- trusted timestamping;
- permission to act;
- Root authority;
- a new packet;
- a new receipt;
- FinalOutput;
- production readiness.

Crypto integrity is not truth.
Replay verification is not effect authorization.
Evidence is not permission.

## One Transaction, Three Sovereign Roots

The trace contains three sovereign Root domains: ClientRoot, AirlineRoot, and
BankRoot. Each Root has its own final artifact, so exactly three Root finals
exist. The cross-root advisory is bounded evidence and is not a fourth Root.

Receipts remain evidence-only artifacts. They do not become authority,
permission, an action, or FinalOutput. Provider or renderer output is not Root
authority.

## Human Timeline

| # | Event | Artifact type | Artifact ID | Root owner | Authority class | Evidence class | Dependencies | Selected offer | Root final |
|---:|---|---|---|---|---|---|---|---|---|
| 1 | transaction_started | AirlineTransactionScopeV01 | airline_transaction_scope:tri_airline_purchase:PAR-LIM:2026-08-12:client_001 | transaction_scope:non_authoritative | none | transaction_metadata | 0 | none | no |
| 2 | bsep_projection_created | ClientBSEPProjectionV01 | client_bsep_projection | bsep_side:client | bounded_context_non_authoritative | bounded_semantic_context | 1: airline_transaction_scope:tri_airline_purchase:PAR-LIM:2026-08-12:client_001 | none | no |
| 3 | bsep_projection_created | AirlineBSEPProjectionV01 | airline_bsep_projection | bsep_side:airline | bounded_context_non_authoritative | bounded_semantic_context | 1: airline_transaction_scope:tri_airline_purchase:PAR-LIM:2026-08-12:client_001 | none | no |
| 4 | bsep_projection_created | BankBSEPProjectionV01 | bank_bsep_projection | bsep_side:bank | bounded_context_non_authoritative | bounded_semantic_context | 1: airline_transaction_scope:tri_airline_purchase:PAR-LIM:2026-08-12:client_001 | none | no |
| 5 | bsep_projection_created | CrossRootAdvisoryBSEPProjectionV01 | cross_root_bsep_projection | bsep_side:cross_root_advisory | bounded_context_non_authoritative | bounded_semantic_context | 1: airline_transaction_scope:tri_airline_purchase:PAR-LIM:2026-08-12:client_001 | none | no |
| 6 | semantic_claim_created | ValidatedAirlineSemanticSelectionEvidenceV01 | canonical_selection:offer:mock_airline_al:PAR-LIM:001 | runtime_canonicalization:advisory | advisory_canonical | canonical_semantic_evidence | 1: airline_bsep_projection | offer:mock_airline_al:PAR-LIM:001 | no |
| 7 | client_root_selection_decided | ClientRootOfferSelectionDecisionV01 | client_root_offer_selection_decision:offer:mock_airline_al:PAR-LIM:001 | root:client_os_001 | root_decision | root_decision_evidence | 1: canonical_selection:offer:mock_airline_al:PAR-LIM:001 | offer:mock_airline_al:PAR-LIM:001 | no |
| 8 | airline_root_offer_resolved | AirlineRootSelectedOfferResolutionV01 | airline_root_selected_offer_resolution:offer:mock_airline_al:PAR-LIM:001 | root:mock_airline_al | root_decision | root_decision_evidence | 1: client_root_offer_selection_decision:offer:mock_airline_al:PAR-LIM:001 | offer:mock_airline_al:PAR-LIM:001 | no |
| 9 | offer_created | AirlineOfferPacketV01 | airline_offer_packet:semantic_causal:001 | root:mock_airline_al | root_owned_contract | root_contract_artifact | 1: airline_root_selected_offer_resolution:offer:mock_airline_al:PAR-LIM:001 | offer:mock_airline_al:PAR-LIM:001 | no |
| 10 | hold_created | AirlineHoldCommitPacketV01 | airline_hold_commit_packet:semantic_causal:001 | root:mock_airline_al | root_owned_contract | root_contract_artifact | 1: airline_offer_packet:semantic_causal:001 | offer:mock_airline_al:PAR-LIM:001 | no |
| 11 | offer_hold_receipt_created | AirlineOfferHoldReceiptV01 | offer_hold_receipt:mock_airline_al:001 | root:mock_airline_al | evidence_only_receipt | receipt_evidence_only | 1: airline_hold_commit_packet:semantic_causal:001 | offer:mock_airline_al:PAR-LIM:001 | no |
| 12 | purchase_intent_created | ClientPurchaseIntentV01 | client_purchase_intent:client_001:001 | root:client_os_001 | root_owned_contract | root_contract_artifact | 1: airline_hold_commit_packet:semantic_causal:001 | offer:mock_airline_al:PAR-LIM:001 | no |
| 13 | payment_authorization_created | BankPaymentAuthorizationRefV01 | bank_payment_authorization_ref:mock_bank_a:001 | root:mock_bank_a | root_owned_contract | payment_authorization_evidence | 1: client_purchase_intent:client_001:001 | offer:mock_airline_al:PAR-LIM:001 | no |
| 14 | ticket_intent_created | AirlineTicketIssueIntentV01 | airline_ticket_issue_commit_packet:mock_airline_al:001 | root:mock_airline_al | root_owned_contract | root_contract_artifact | 3: airline_hold_commit_packet:semantic_causal:001<br>client_purchase_intent:client_001:001<br>bank_payment_authorization_ref:mock_bank_a:001 | offer:mock_airline_al:PAR-LIM:001 | no |
| 15 | mock_ticket_receipt_created | MockTicketReceiptV01 | mock_ticket_receipt:mock_airline_al:001 | root:mock_airline_al | evidence_only_receipt | receipt_evidence_only | 1: airline_ticket_issue_commit_packet:mock_airline_al:001 | offer:mock_airline_al:PAR-LIM:001 | no |
| 16 | mock_purchase_receipt_created | MockPurchaseReceiptV01 | mock_purchase_receipt:client_001:001 | root:client_os_001 | evidence_only_receipt | receipt_evidence_only | 3: mock_ticket_receipt:mock_airline_al:001<br>bank_payment_authorization_ref:mock_bank_a:001<br>client_purchase_intent:client_001:001 | offer:mock_airline_al:PAR-LIM:001 | no |
| 17 | root_final_created | ClientRootFinalV01 | client_root_final:001 | root:client_os_001 | root_final | root_final_evidence | 3: client_root_offer_selection_decision:offer:mock_airline_al:PAR-LIM:001<br>client_purchase_intent:client_001:001<br>mock_purchase_receipt:client_001:001 | offer:mock_airline_al:PAR-LIM:001 | yes — ClientRoot |
| 18 | root_final_created | AirlineRootFinalV01 | airline_root_final:001 | root:mock_airline_al | root_final | root_final_evidence | 6: airline_root_selected_offer_resolution:offer:mock_airline_al:PAR-LIM:001<br>airline_offer_packet:semantic_causal:001<br>airline_hold_commit_packet:semantic_causal:001<br>offer_hold_receipt:mock_airline_al:001<br>airline_ticket_issue_commit_packet:mock_airline_al:001<br>mock_ticket_receipt:mock_airline_al:001 | offer:mock_airline_al:PAR-LIM:001 | yes — AirlineRoot |
| 19 | root_final_created | BankRootFinalV01 | bank_root_final:001 | root:mock_bank_a | root_final | root_final_evidence | 1: bank_payment_authorization_ref:mock_bank_a:001 | offer:mock_airline_al:PAR-LIM:001 | yes — BankRoot |

## Why Dependencies Matter

Dependencies preserve the accepted causal order rather than merely listing
artifacts. The Airline ticket issue intent depends on the Airline hold, the
Client purchase intent, and the Bank payment authorization. The mock purchase
receipt depends on the ticket receipt, Bank authorization, and Client purchase
intent.

The ClientRoot final depends on the accepted Client-side decision and
evidence. The AirlineRoot final depends on Airline offer, hold, ticket-side,
and receipt evidence. The BankRoot final depends on Bank authorization
evidence.

Every dependency points to an earlier accepted row.
No forward dependency, missing dependency, self-dependency, or duplicate
artifact ID was accepted.

## Geometry And Counters

| Measure | Exact value |
|---|---:|
| Source files | 9 |
| Critical files | 11 |
| Ledger entries | 19 |
| Dependency edges | 29 |
| Root finals | 3 |
| Timeline rows | 19 |
| Ledger audit count | 1 |
| Anchored verification count | 1 |
| Post-Replay package observation count | 1 |

Reruns:

- transaction: 0
- semantic: 0
- Corridor: 0

Recollections:

- Ledger: 0
- Crypto: 0

External/model activity:

- provider: 0
- network: 0
- Gemini: 0

Replay-created objects:

- authority: 0
- permission: 0
- action: 0
- packet: 0
- receipt: 0
- FinalOutput: 0

Real-world effects:

- 0

## Byte Stability

The eleven critical package files were unchanged, and the package inventory
was unchanged. The anchor was unchanged and still equaled its committed
publication bytes. The official Replay Report was written outside the sealed
package and remained unchanged during the D1 audit.

This human explanation does not modify the Report, audit, anchor, or package.

Official Replay Report SHA-256:

`4626a972e3f127b9df51e16ac429d9392a1b8338b2d730f26d9691a2288694a9`

Committed anchor SHA-256:

`f2929a305d1b05a16a51ead28972919a3209db1234ea6d0555f7228a460963fe`

## Deferred Stronger Cryptographic Profile

The current proof-of-architecture intentionally implements the minimal externally anchored integrity profile; its Ledger/Manifest/Replay boundaries can support a later Root-scoped signature and attested-Replay overlay, but that stronger profile is deferred and is not claimed as implemented.

This is an optional future strengthening and is not required for Base Replay.
No keypair, Root signature, PKI, or attested-Replay overlay was created here.
This section is not task authorization or an active implementation roadmap.

## Result And Remaining Closure Step

- Slice D1 official Replay and independent audit: PASS
- Slice D2 artifact-backed human explanation: PASS
- Base Airline Sealed Trace Replay v0.1 full repository closure: PENDING
- Remaining step:
  full canonical docs/spec/manifest synchronization
- Only the later docs-sync commit changes the layer status to CLOSED / PASS.

Next gate:

`airline_sealed_trace_replay_v01_slice_d3_full_docs_spec_manifest_sync`

No all-real LLM run is authorized or performed by D2.
