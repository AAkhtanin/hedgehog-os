# Presentation build

The PDF exports from the same editable 12-slide PPTX. The canonical files copy the validated r3 presentation bytes. This authoring pipeline reads saved data only and does not import or execute Radiolaria.

## Dependencies and licensing

Use a licensed installed Codex primary runtime with Node.js, Python, `@oai/artifact-tool`, `@napi-rs/canvas`, the presentation skill finalizer, LibreOffice, Poppler and `pypdf`. `@oai/artifact-tool` is a runtime dependency, not bundled source in this capsule. Its use remains subject to the installed runtime's license terms. This capsule does not grant a separate license to that dependency.

Supply licensed Inter Regular and Bold TrueType files externally. No font files are redistributed in the capsule. The PDF embeds permitted font subsets. The cover bitmap has its own asset provenance record.

## Rebuild route

1. Create a writable authoring directory outside this frozen capsule. Copy `presentation/build/` to its `build/` directory. Copy `presentation/slide_text_and_notes_v01.json` and `presentation/claim_evidence_matrix_v01.json` into its `content/` directory. Copy the cover bitmap into `assets/`, or set `G4_HERO_IMAGE` to its existing path.
2. Set `G4_PRESENTATION_ROOT` to that authoring directory and `G4_FONT_DIR` to the external Inter directory. Set the runtime's `CODEX_PRIMARY_RUNTIME_NODE`, `CODEX_PRIMARY_RUNTIME_NODE_MODULES`, `CODEX_PRIMARY_RUNTIME_PYTHON` and `CODEX_PRIMARY_RUNTIME_ROOT`. Link the working `build/node_modules` to the runtime modules directory.
3. To regenerate the data-derived map, set `G4_STORY_DIR` to this capsule's `evidence/g44/portable_publication_final/story` and `G4_CONTENT_DIR` to the working `content/`. Run `build/extract_slide_content.py` with the runtime Python.
4. Run `build/build_slides.mjs pilot` with the runtime Node. Inspect architecture, strategy and budget pages. Run it again with a new revision name for all 12 slides. The builder exports editable objects, patches native hyperlinks and explicit text insets, then uses the presentation finalizer. It refuses an existing finalizer output.
5. Convert the validated PPTX to PDF using the bundled LibreOffice `soffice --headless --convert-to pdf --outdir OUTPUT_DIR INPUT_PPTX`, a fresh writable user profile and a fontconfig file that exposes the same Inter files.
6. Render every PDF page with Poppler. Inspect all pages, including the utility table and final navigation page. `verify_deck.py` checks the canonical `output/gate4_reference_v01.pptx` and `.pdf`, native tables, searchable key values, 15 hyperlink relationships and 15 matching PDF annotations.

`presentation/build/validation_r3.json` preserves the original finalization receipt. Paths in that receipt identify the authoring workspace, not additional capsule members. `qa/deck_qa_v01.json` records canonical hashes and review results. Full-size review PNGs remain in the authoring workspace; the contact sheet is an outer return artifact. They are not included in this capsule or Reader.

Versioned GitHub document links are staged publication targets. Repository access and actual remote publication remain separate from local document QA.
