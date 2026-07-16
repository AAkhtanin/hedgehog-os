# Hedgehog OS Airline All-Real Evidence Showcase v0.1 Preflight
- document_id: airline_all_real_evidence_showcase_preflight_v01
- document_status: PREFLIGHT
- preflight_status: READY_FOR_REVIEW
- showcase_slice: S1
- observed_base_head: a562c47
- evidence_base_head: a562c47
- planning_only: true
- runtime_modified: false
- tests_modified: false
- presentation_renderer_created: false
- presentation_artifacts_created: false
- package_modified: false
- anchor_modified: false
- replay_report_modified: false
- provider_called: false
- network_called: false
- gemini_called: false
- transaction_rerun_count: 0
- replay_rerun_count: 0
- real_world_effects_count: 0
- production_ready_claimed: false
- next_gate: airline_all_real_evidence_showcase_v01_slice_s2_renderer_and_artifacts
This preflight plans a static evidence-backed presentation package. It does
not create a product frontend, website, interactive application, universal
presentation framework, or new runtime evidence.

Target length is 250-350 lines. The hard maximum is 450 lines.

## 1. Evidence Basis And Purpose

The future showcase explains one accepted proof-level Airline trace to a
technical executive, architect, engineer, or auditor.

The presentation thesis is:

> Hedgehog OS separates LLM reasoning from authority, then preserves the accepted decision path as a deterministic, cryptographically anchored, replayable evidence chain.

Narrative source:

- `docs/airline_all_real_full_stack_human_story_v01.md`

Committed machine-evidence sources:

- `docs/airline_all_real_full_stack_crypto_anchor_v01.json`
- `docs/airline_all_real_full_stack_replay_report_v01.json`
- `docs/audit_reports/auditor_airline_all_real_full_stack_v01_generation_anchor_publication.log`
- `docs/audit_reports/auditor_airline_all_real_full_stack_v01_anchored_replay.log`

Committed planning/recovery context:

- `docs/airline_all_real_full_stack_run_preflight_v01.md`
- `docs/airline_all_real_full_stack_run_recovery_v01.md`

The Human Story controls presentation narrative. The Anchor, Replay Report,
and audits control identities, counts, statuses, hashes, and integrity claims.
S1 and S2 do not inspect either `.tmp` package.

## 2. Local Capability Probe
Observed local capability on `a562c47`:

| Capability | Availability |
| --- | --- |
| Python | `3.14.5` |
| `pptx` / python-pptx | unavailable; version not applicable |
| `reportlab` | unavailable; version not applicable |
| `PIL` / Pillow | unavailable; version not applicable |
| `pypdf` | unavailable; version not applicable |
| `pdftoppm` | unavailable |
| `pdfinfo` | unavailable |
| `soffice` | unavailable |
| `libreoffice` | unavailable |

No package was installed and the virtual environment was not changed. The
missing core imports require later owner approval before S2 implementation.

Preferred S2 pipeline when approved dependencies are available:

```text
one normalized presentation/content model
-> python-pptx for PPTX
-> ReportLab for main-deck PDF, one-pager PDF, and appendix PDF
-> Pillow only for local raster details when vector shapes are impractical
```

PPTX and PDF are rendered from the same normalized model; neither is the
source of the other. LibreOffice is optional and cannot be required by S2.

## 3. Exact S2 Scope
Authorize exactly one renderer:
`demo/run_airline_all_real_evidence_showcase_v01.py`.

Authorize exactly one test:
`tests/test_airline_all_real_evidence_showcase_v01_runner.py`.

Generated directory:
`docs/showcase/airline_all_real_full_stack_v01/`.

Exactly seven deliverables:

1. `README.md`
2. `hedgehog_os_airline_all_real_showcase_v01.pptx`
3. `hedgehog_os_airline_all_real_showcase_v01.pdf`
4. `executive_one_pager_v01.pdf`
5. `technical_appendix_v01.pdf`
6. `claim_evidence_matrix_v01.json`
7. `SHA256SUMS`

No eighth deliverable, HTML, JavaScript, CSS application, website, server,
API, database, presentation DSL, slide framework, plugin architecture, or
interactive evidence room is authorized. Temporary render files must remain
in an invocation-owned temporary directory and be removed on success. No
committed intermediate image or asset directory is authorized.

## 4. Hard Complexity Limits

- renderer files: exactly 1;
- test files: exactly 1;
- generated deliverables: exactly 7;
- main-deck slides and PDF pages: exactly 16;
- executive one-pager pages: exactly 1;
- technical appendix pages: 16-24;
- major diagrams: at most 6;
- implementation cycle: one S2 implementation plus at most one correction;
- Gemini/provider/network calls: 0;
- transaction/Corridor/Ledger/Crypto/Replay operations: 0.

The renderer is Airline showcase integration, not universal Hedgehog OS core.

## 5. Visual Profile

- widescreen 16:9;
- technical-executive / deep-tech due-diligence style;
- dark navy or near-black background;
- off-white text; cyan/teal accent; green PASS; amber advisory; restrained
  red FAIL_CLOSED history;
- system fonts only; no downloads;
- no stock photos, external images, logos, or decorative AI-generated images;
- native vector shapes wherever practical;
- minimum body text 18 pt; evidence/footer text 10 pt;
- one primary message and an evidence footer per slide;
- no raw JSON/log walls, clipping, or overflow.

Text branding only:

```text
HEDGEHOG OS
Airline All-Real Evidence Showcase v0.1
```

## 6. Exact 16-Slide Main Deck

1. Cover — central thesis
2. Executive proof in 90 seconds
3. The user’s mock travel task and accepted result
4. Complete architecture from user task to anchored Replay
5. The twelve real Gemini actors and bounded topology
6. Orchestration and Client-side actor evidence
7. Airline-side actor evidence
8. Bank-side and cross-root actor evidence
9. Why the deterministic system selected Offer A
10. Three sovereign Roots and authority separation
11. Five-phase Ticket/Purchase Corridor and mock evidence card
12. Transaction Artifact Ledger — 19 / 29 / 3
13. Crypto generation — 9 / 11 and SELF_CONSISTENT_UNANCHORED
14. Committed external Anchor and 19-row Replay PASS
15. First honest FAIL_CLOSED run and distinct successful recovery
16. What was proved, non-claims, and evidence entry points

Slide 1 uses the presentation thesis from Section 1. Slide 2 shows: 12 real
Gemini actors, 3 sovereign Roots, 1 deterministic transaction, 19 Ledger
artifacts, 29 edges, 3 Root finals, 9 source files, 11 critical files,
1 committed Anchor, 19 Replay rows, and 0 effects. Every slide references at
least one claim ID.

## 7. Actor Presentation Policy

Slides 6-8 collectively cover all twelve actors. The appendix has one compact
card per actor containing actor ID, human role, side, bounded input summary,
accepted canonical meaning, structured fields, `PASS`, `accepted: true`,
downstream consumer, authority boundary, and evidence references.

Use canonical summaries and validations only. Use the label `Accepted
canonical meaning`, never `Exact Gemini quote`. Do not publish or paraphrase
raw prompts, raw responses, or rejected/unvalidated candidates.

## 8. Transaction Evidence Card

Slide 11 includes PAR → LIM, 2026-08-12, Preference A, selected
`offer:mock_airline_al:PAR-LIM:001`, ClientRoot `root:client_os_001`,
AirlineRoot `root:mock_airline_al`, BankRoot `root:mock_bank_a`, hold packet
`airline_hold_commit_packet:semantic_causal:001`, purchase intent
`client_purchase_intent:client_001:001`, payment reference
`bank_payment_authorization_ref:mock_bank_a:001`, ticket-issue intent
`airline_ticket_issue_commit_packet:mock_airline_al:001`, both mock receipts,
and `client_root_final:001`, `airline_root_final:001`, `bank_root_final:001`.

Display prominently:

```text
MOCK / PROOF-LEVEL EVIDENCE
NOT A REAL TICKET
NOT A REAL BOOKING
NOT A REAL PAYMENT
```

Do not invent a PNR, booking reference, ticket number, airline brand, or
settlement ID.

## 9. Claim–Evidence Matrix

Generate:
`docs/showcase/airline_all_real_full_stack_v01/claim_evidence_matrix_v01.json`.

Each claim object contains exactly:

1. `claim_id`
2. `display_label`
3. `observed_value`
4. `observed_type`
5. `evidence_availability`
6. `source_path`
7. `source_field_or_section`
8. `source_sha256`
9. `source_commit`
10. `slide_numbers`
11. `appendix_pages`
12. `public_link_available`
13. `notes`

Allowed evidence availability:
`committed_repository_evidence`, `local_sealed_package`, and
`committed_audit_of_local_package`.

Committed documents use the first value. Direct `.tmp` evidence uses the
second and sets `public_link_available: false`. Committed audits describing
local evidence use the third. Paths are repository-relative; SHA-256 values
are lowercase 64-hex. Presentation text is never the sole evidence source.

Required claims cover twelve calls, twelve actor validations, Offer A, three
Roots, Corridor PASS/count 1, Ledger 19 / 29 / 3, Crypto 9 / 11, stored
unanchored status, committed Anchor, fresh anchored PASS, Replay 19 rows,
Replay provider/network/Gemini counts 0, effects 0, unchanged package,
preserved failed evidence, failed package not promoted, and distinct recovery.

## 10. Evidence References

Every slide footer uses claim IDs such as `Evidence: C01, C05, C12`. The final
slide and README reference:
`docs/airline_all_real_full_stack_human_story_v01.md`,
`docs/airline_all_real_full_stack_crypto_anchor_v01.json`,
`docs/airline_all_real_full_stack_replay_report_v01.json`,
`docs/audit_reports/auditor_airline_all_real_full_stack_v01_generation_anchor_publication.log`,
`docs/audit_reports/auditor_airline_all_real_full_stack_v01_anchored_replay.log`,
and `claim_evidence_matrix_v01.json`. `.tmp` paths are never public links;
label them `Local sealed evidence — verified by committed audit`. No internet
link is required.

## 11. Technical Appendix

Freeze 16-24 pages: cover/evidence identity; twelve actor cards; full 19-row
timeline on one or two pages; Crypto/Anchor identity; Replay zero-rerun
boundary; claim/evidence references; and non-claims. It must stand alone and
contain no raw prompt or response content.

## 12. Executive One-Pager

Freeze one page with the thesis, `12 / 3 / 19 / 29 / 9 / 11 / 19 / 0`,
simplified architecture, route and Offer A, two Crypto moments, anchored
Replay PASS, zero Gemini reruns, non-claims, and repository-relative evidence
paths. No QR code or external link is required.

## 13. Generated README

Explain all seven deliverables, committed versus local evidence,
`SHA256SUMS`, local regeneration, zero Gemini/provider/network regeneration,
exclusion of raw prompts/responses, proof-level mock status, and non-production
scope.

## 14. S2 Renderer Contract

The renderer accepts explicit repository root and output directory, reads only
allowlisted committed evidence, and performs no discovery. It never reads
`config.py`, credentials, prompts, raw responses, or `.tmp` package content.

It must:

- call no Gemini/provider/network/runtime operation;
- rerun no transaction, Corridor, Ledger, Crypto, or Replay;
- modify no evidence;
- fail closed on missing or inconsistent evidence;
- build one normalized content/scene model;
- render PPTX and all PDFs from that model;
- use deterministic ordering;
- create outputs atomically in the explicit directory;
- clean invocation-owned partial outputs;
- create deterministic matrix JSON and `SHA256SUMS`;
- expose a CLI.

No generic filesystem crawler, generic deserializer, or hidden package
selection is allowed.

## 15. S2 Test Contract

The one test file covers:

- exact seven deliverables;
- 16 PPTX slides and 16 main-deck PDF pages;
- one one-pager page and appendix pages 16-24;
- exact matrix fields and required claim coverage;
- committed/local evidence labeling and existing committed paths;
- no prompt/response content, API-key pattern, absolute path, or overclaim;
- evidence unchanged and provider/network/Gemini calls 0;
- deterministic rerendering and output-directory isolation;
- owned partial-output cleanup;
- valid PPTX ZIP and PDF structures/page counts;
- `SHA256SUMS` matching every deliverable except itself;
- PDF visual smoke when a local renderer exists.

Cross-platform pixel-perfect equality is not required.

## 16. Non-Claims

- not a real ticket, booking, payment, or external integration;
- not production or legal completion;
- Gemini output is not truth or authority;
- Crypto validity is not semantic truth;
- the committed hash Anchor is not signer authentication;
- `signature_verified` remains false;
- no PKI or Root Attestation;
- Replay is not effect authorization;
- the Showcase presents accepted evidence and creates no new evidence.

Raw prompts, raw responses, credentials, absolute user paths, and fabricated
quotes remain forbidden.

## 17. S2 Review Boundary

S2 requires explicit approval of dependencies and file scope, one renderer
implementation, one generation pass plus at most one correction, structural
and visual validation, evidence-byte stability, and owner review before any
commit. LibreOffice remains optional.

S1 status: `READY_FOR_REVIEW`.

Next gate:
`airline_all_real_evidence_showcase_v01_slice_s2_renderer_and_artifacts`.

S1 created no renderer, test, PPTX, PDF, image, matrix, checksum file, README,
temporary presentation asset, or new evidence.
