# Airline A2: From Semantic Contribution to Verifiable Replay

This is a public-safe account of the accepted Airline evidence chain. It is
limited to committed safe projections and validated publication artifacts. It
does not reproduce private prompts, provider responses, credentials, or
private Attempt material.

## The Chain

A party supplied an intent for the bounded Airline transaction workflow.
Twelve live LLM calls contributed semantic proposals for selection and routing.
Those proposals were inputs to the system, not decisions or authority.

The runtime canonicalized the accepted semantics and local validators checked
each role. All 12 actor results passed local validation. The resulting evidence
then reached three separately owned sovereign Root decisions: ClientRoot,
AirlineRoot, and BankRoot. Each Root retained its own final authority.

One deterministic Corridor processed the Root-approved mock-only workflow. It
produced three evidence-only receipts. Those receipts recorded what the bounded
workflow observed; they did not create payment authority, booking authority,
ticket authority, or any other real-world permission.

The accepted artifacts were collected into the transaction Ledger and the
cryptographic integrity layer. The official Package then bound four safe
evidence members into one Manifest and an adjacent Package index. Both remained
`SELF_CONSISTENT_UNANCHORED` at that stage.

The stored Anchor was created with status `EVIDENCE_ONLY`. It did not claim
that the Package was already externally anchored. During Replay, a fresh
matching verification compared the supplied Anchor identity with the exact
committed Package and obtained `ANCHORED_PASS`. The stored Anchor itself
remained unchanged and remained `EVIDENCE_ONLY`.

Offline Replay then reconstructed and validated the committed evidence chain.
Replay closed with `PASS` and made no semantic rerun, Root-decision rerun, or
Corridor rerun.

## Verified Geometry

```text
12 live LLM calls
-> 12 local PASS results
-> 3 sovereign Roots
-> 1 Corridor
-> 3 evidence-only receipts
-> 0 real-world effects
```

The LLM influenced semantic selection and routing. It created no authority,
permission, payment, booking, ticket, receipt authority, or Root final. The
three Roots remained the final authorities for their separately owned
boundaries.

Package, Anchor, both independent audits, and Replay made no new provider,
network, or Gemini call. They created no real-world effect. The accepted chain
is evidence of bounded execution and integrity continuity; it is not a claim
of production airline, bank, payment, booking, or ticket execution.

## Public Identities

- Package index ID:
  `6314b619a99d03b9a32e5a3cd581f1f28e487e2677b42a3b7e2d88d2ba12375d`
- Manifest ID:
  `7b98bcbc23a0148a83c9b2d459f9d0ae35d9161c90a2938620c529e84049b8ee`
- Package content hash:
  `3d8aa5aab285ead0320acf29cd3bd0e791faf6e4ba7b4c7e5b67c268d0e0a248`
- Anchor publication ID:
  `5c198968c12f30ffa3e4e06739d889d69665017c56020686f200bbe2e89dec99`
- Replay ID:
  `4b04d59c237d82ef1d87a3dc9b21170db1da5e91da2d862fd1ec5ad96f56f0b2`

Raw prompts, raw provider responses, credentials, and private Attempt material
are intentionally absent from this public story.
