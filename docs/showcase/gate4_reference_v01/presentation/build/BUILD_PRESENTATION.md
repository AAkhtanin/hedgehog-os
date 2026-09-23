# Gate 4 Reference presentation build

This is a data-only presentation pipeline. It reads saved JSON and does not import Radiolaria, call models, create native Work, run tests or replay authority.

1. Use the supplied Codex primary runtime. `CODEX_PRIMARY_RUNTIME_NODE`, `CODEX_PRIMARY_RUNTIME_NODE_MODULES`, `CODEX_PRIMARY_RUNTIME_PYTHON`, and `CODEX_PRIMARY_RUNTIME_ROOT` must be absolute paths. The builder uses `@oai/artifact-tool` and its package finalizer.
2. Set `G4_PRESENTATION_ROOT` to this presentation working directory and `G4_FONT_DIR` to licensed Inter Regular and Bold TrueType files. Font files are not part of this deliverable. The default working copy finds fonts in `presentation/assets/fonts` relative to the task workspace.
3. Place saved source material at `gate4/review/g44/portable_publication_final/story` in the authoring workspace, or use the capsule's `evidence/g44/portable_publication_final/story` fallback. `G4_STORY_DIR` can set an explicit source location and `G4_CONTENT_DIR` an explicit content location. The extractor produces the same four utility rows, fixed-point displays, exact mappings and actual Work comparison from saved bytes. It attaches the frozen `claim_evidence_matrix_v01.json` routes to slide notes.
4. Run `extract_slide_content.py` with the runtime Python. This writes `content/slide_text_and_notes_v01.json`.
5. Link `build/node_modules` to the runtime modules directory. Run `build_slides.mjs pilot` with the runtime Node. Inspect the three PNGs (architecture, strategy, actual Work swap).
6. Run the builder with a new revision name. It exports a candidate, adds shape hyperlinks and explicit zero text insets for Office/LibreOffice parity, runs the presentation finalizer, and renders all slides. The default `final` revision writes `output/gate4_reference_v01.pptx`. Existing finalizer outputs must not be overwritten. Later revisions use distinct suffixes.
7. Convert the validated PPTX with bundled LibreOffice `soffice --headless --convert-to pdf`. Use a fontconfig file that includes the installed Inter directory and a fresh writable LibreOffice user profile. The PDF content is generated from this exact PPTX.
8. Run `verify_deck.py` on the final PPTX/PDF pair. Render the PDF with bundled Poppler and inspect every page at full size. Check the contact sheet only for overall consistency.

The current canonical v01 files copy the validated r3 bytes without modification. `validation_r3.json` is the private package finalization receipt. Diagram boxes, connectors, table cells, labels and all slide copy remain native editable slide objects. Only the cover artwork is a bitmap. `G4_HERO_IMAGE` can locate this asset explicitly; the builder also accepts the capsule-level assets directory.

Links use the pinned implementation commit and versioned GitHub main document paths. The last slide states that document links are staged publication targets and require repository access. Remote path publication and readback are a separate owner action.
