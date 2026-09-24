# Publication QA report

Status: **PASS for the documented presentation/source scope**. Engineering runtime proofs retain their recorded status.

## Content and source checks

- Twenty slides, thirty appendix pages, twenty-two source-mapped claims. All19 original model-call requests/responses/receipts retained; initial16VALIDATED/3FAILED and final14selected, including15, reconciled.

- All2,000 raw shot rows independently decoded and matched to recorded validation. Counts33/42,distinct16/20,optimal5/18,selected63/31 and saved arrangements match.

- Unchanged110-file portable directory; independently supplied manifest pin preserved.375 original source identities resolve to deduplicated stored bytes.34accepted source snapshots retained.

- Secret scan: zero findings for the high-confidence credential patterns used. This is a bounded scan, not an exhaustive privacy guarantee. Original synthetic evidence is explicitly labeled.

## Presentation and links

- All20main and30appendix pages rendered and individually inspected. Corrected wrapping/spacing and rechecked final output. Text is selectable in both PDFs.

- PowerPoint contains editable text/diagrams,3native tables and1native chart with its embedded data workbook. First-party reimport, package integrity and layout checks passed. Native Microsoft PowerPoint execution was not performed.

- Main PDF and PPTX each contain44 active links with identical targets. Appendix has142 active annotations and30 named destinations. All local targets resolve.

- New showcase GitHub targets are **pending publication**, not falsely reported HTTP200. The repository is private. Existing landing is supported by saved ordinary-push/readback receipts; no new remote publication was performed here.

## Fresh versus recorded verification

The standard-library recipient check `python verify_reader_v01.py` passed (RC0,10.199s for the recorded document-check command). It checks source bytes and explicitly supported saved relationships, not a new application run.

A separate attempt to invoke the accepted W5 application verifier in this authoring environment stopped with RC2 because `jsonschema` was absent. The second application process was not run and no dependency was installed. This attempt is not reported as PASS. The two accepted W5 clean-process results and installed W5L result remain recorded: all have canonical SHA256 `e4a1a644776da341368af07eeb5a0317f7fca4dcda25e5bb23c7004aacad09b0`.

There were no new AWS/Gemini/QPU/native computations, application effects, owner changes, commits or pushes. Public literature retrieval and authoring/rendering are separate from those recorded project executions.

## Tools, commands and exact outputs

Tools: {"python": "3.12.14", "node": "v24.19.0", "libreoffice": "LibreOfficeDev 26.8.0.0.alpha0 2c87e51eeaa2b413ff4ae097b2705eea1995d8e5", "renderer": "Poppler pdftoppm; PDF text/annotations via pypdf", "deck_authoring": "@oai/artifact-tool; final package/import/native-chart validators"}

Actual commands: `node build_deck.mjs` and first-party finalizer (finalsuccessRC0); `soffice --headless --convert-to pdf` (RC0); `pdftoppm -scale-to 1280 -png` (RC0); appendix ReportLab builder (RC0); Reader builders/independent validator and `python verify_reader_v01.py` (RC0). The package is assembled only after final exports.

Failed authoring attempts were local workspace/receipt-path handling, chart workbook omission and missing import-environment configuration; these were corrected without changing application evidence. Original runtime and model failures remain preserved separately.

| Artifact | Bytes | SHA256 |
|---|---:|---|

| wedding_presentation_v01.pptx | 3100132 | `c24906bc8c57bbf1f95d4832e829fbf7d57391974d29173787ed1e3ea19cc79c` |

| wedding_presentation_v01.pdf | 789458 | `c2afea7d2c3315c18e7a8b536ad5560cc12d3f9e11b704b1c602e260ecb08b5a` |

| technical_appendix_v01.pdf | 180624 | `4ac9dc476490aa2dcd2b557a5c4d7374abe8f4c990b6ca39784b4ae21ee07177` |

| technical_appendix_v01.md | 60205 | `92b043f9883b9f906c0be39c0a8f8da94791f97446d0af9383c130820a8cf046` |

| WEDDING_LLM_READER_V01.xml | 8732562 | `c6623b09fe0d5032ba2a4fd5cc822f851a2a564afb7382a90d890af271f971eb` |

| content_manifest.json | 89701 | `6e3a3637fb9a334753121447955a66000283fb2edc214cbd18bf0dcd0e1ea5ad` |


Machine details: [document validation](qa/document_validation.json), [PDF links](qa/pdf_links.json), [Reader checks](qa/reader_validation.json), [independent source checks](qa/independent_source_validation.json), [appendix checks](qa/appendix_validation.json).
