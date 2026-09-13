# Testflix V09: English demonstration and historical evidence

Historical run: September 12, 2026. This page is a new navigation page for the original English files and four explicitly labelled translations. It is not a translated execution report or a new run.

## Open the demonstration and reports

- [Human-readable story](translations/demo/HUMAN_STORY.md), English translation.
- [Final narrative report](translations/FINAL_REPORT.md), English translation.
- [Historical A/B repair note](translations/AB_contract_repair.md), with the owner quotation translated.
- [Historical owner confirmation](translations/approval_AB_owner_confirmed.json), with the owner message translated.

- [Original HTML presentation](original/demo/story.html): download the raw file and open it locally; no server or model calls are needed.
- [Original presentation screenshot](original/viewer_qa/desktop.png).
- [Original story data](original/demo/story.json).
- [Original result and remaining work](original/RESULT.json).
- [Original execution-package README](original/README.md).
- [Original live attempts, model responses, and failures](original/live_captures/).
- [Original live result](original/live_main_02/story/result.json) and [captured-execution result](original/captured_main_01/story/result.json).
- [Original coverage records](original/coverage.json).
- [Original 35 source files](original/owner_apply/postimage/), [source identities](original/owner_apply/source_ledger.json), and [proposed source patch](original/owner_apply/cumulative_L.patch).
- [Single-file XML reader for another LLM](TESTFLIX_V09_LLM_READER.xml): selected original English files, all four translations and exact source excerpts, not a full repository export.

## Reading this record

The historical main live story and captured execution completed. Positive A/B remained incomplete; the role disagreement, two Google 504 errors and subsequent ReadTimeout are part of the original record. Payments, catalogue and device effects are controlled mocks. See the original result files for the exact scope and timings.

Captured execution and offline replay are different operations: captured execution uses saved model responses with new Hosts and mock effects; replay verifies an existing history without provider or effect calls.

Full Testflix acceptance and runtime landing are not claimed by this historical package. The original report's `remaining` fields and captured failures remain unchanged.

The historical A/B repair note contains a premature completion statement. Its translation preserves that historical statement; it does not override the original final result: positive A/B remained incomplete. Translating this note does not complete the pending run or repair runtime behaviour.

## Original bytes and archive access

Every file retained under `original/`, including the HTML, images, model records, JSON reports and source files, matches the source V09 archive byte for byte. The four documents under `translations/` are identified separately; their source and translated hashes are recorded in the source index. [ORIGINAL_ENGLISH_SOURCES.json](ORIGINAL_ENGLISH_SOURCES.json) describes the selection; [ARCHIVAL_SELECTION.json](ARCHIVAL_SELECTION.json) records the retained originals and hashes.

Four prose/approval files already contained Russian in the source archive. No original English counterparts were found in the available V09 materials. English translations of all four are included here and in the XML reader, so the narrative can be read without changing commits. Their original-language bytes remain in the full source archive and previous commit. The original manifest and README retain their historical filenames; use the links above for the English editions.

The original archive is available [in the preserved historical commit](https://github.com/AAkhtanin/hedgehog-os/blob/8209207be6e24e2dd9d46c3feff3b720c8d4f254/docs/showcase/history/testflix_v09_20260912/evidence/RADIOLARIA_TESTFLIX_T3_REPAIR_AND_DEMONSTRATION_V09_RETURN_20260912T203950Z.tar.gz) and in the owner's local backup. It is not repacked or overwritten.

- SHA256: `f9c2d4519a404163fbfd3bdcef4632f9bba60025b3ad0e7ba982b85162937ec0`.
- Bytes: 74,626,542.
- Regular members: 970; original manifest rows: 969.

## Repository location

`docs/showcase/history/testflix_v09_20260912/` on `history/testflix-v09-2026-09-12`.

Local worktree: `~/Projects/hedgehog-os-testflix-history`.

[Presentation catalogue](../../README.md). This follow-up changes only the Testflix reading package and its catalogue entry. Earlier commits and the rest of the repository are retained.
