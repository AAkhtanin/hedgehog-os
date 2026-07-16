# Hedgehog OS Airline All-Real Evidence Showcase v0.1

This static package presents accepted, committed proof-level Airline evidence.
It creates no new runtime evidence and makes no production claim.

## Deliverables

| File | Purpose |
| --- | --- |
| `README.md` | Package guide and regeneration instructions |
| `hedgehog_os_airline_all_real_showcase_v01.pptx` | Sixteen-slide main deck |
| `hedgehog_os_airline_all_real_showcase_v01.pdf` | Sixteen-page main deck PDF |
| `executive_one_pager_v01.pdf` | One-page executive summary |
| `technical_appendix_v01.pdf` | Nineteen-page technical appendix |
| `claim_evidence_matrix_v01.json` | Twenty-four claim-to-evidence bindings |
| `SHA256SUMS` | Checksums for the other six deliverables |

## Evidence Basis

- `docs/airline_all_real_full_stack_human_story_v01.md`
- `docs/airline_all_real_full_stack_crypto_anchor_v01.json`
- `docs/airline_all_real_full_stack_replay_report_v01.json`
- `docs/audit_reports/auditor_airline_all_real_full_stack_v01_generation_anchor_publication.log`
- `docs/audit_reports/auditor_airline_all_real_full_stack_v01_anchored_replay.log`
- `docs/airline_all_real_evidence_showcase_preflight_v01.md`

Committed files are linked directly in the claim matrix. Local sealed evidence
remains outside Git and is represented only through committed audits. The
renderer did not read a `.tmp` package. Raw prompts and raw responses are not embedded.

## Deck Outline

The sixteen slides cover the thesis, executive metrics, mock task, architecture,
twelve actors, Offer A selection, three Roots, five-phase Corridor, 19 / 29 / 3
Ledger, 9 / 11 Crypto generation, committed Anchor, Replay PASS, honest
FAIL_CLOSED history, recovery, proof claims, and non-claims.

The nineteen-page appendix contains evidence identity, twelve actor cards, the
full timeline, Crypto hashes, Replay zero-rerun boundaries, claim references,
and verification instructions.

## Regeneration

```sh
PYTHONPATH=. .venv/bin/python -m \
  demo.run_airline_all_real_evidence_showcase_v01 \
  --repository-root . \
  --output-dir \
  docs/showcase/airline_all_real_full_stack_v01
```

Regeneration performs no Gemini, provider, network, transaction, Corridor,
Ledger, Crypto, or Replay call.

Toolchain: Python 3.14.5; python-pptx 1.0.2; ReportLab 5.0.0; Pillow 12.3.0;
pypdf 6.14.2.

## Verify

macOS:

```sh
shasum -a 256 -c SHA256SUMS
```

GNU:

```sh
sha256sum -c SHA256SUMS
```

## Non-Claims

This is mock proof-level evidence: not a real ticket, booking, payment,
airline/bank/GDS integration, production deployment, signer authentication,
PKI, Root Attestation, semantic-truth proof, or effect authorization.
