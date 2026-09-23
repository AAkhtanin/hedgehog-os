# Presentation source handoff

The frozen PDF and PPTX are the reviewed deliverables. Rebuilding is optional and creates a new derivative: layout/export differences must be reviewed before publication. Do not overwrite their identities or the original evidence.

## Editable content

- Open the PPTX to edit native text, shapes, seven tables, seventeen connectors and one chart with its embedded workbook.
- The technical appendix Markdown is the editable narrative. `appendix_content.json` is the paginated renderer input.
- `slide_text_and_notes.json` includes slide copy, speaker notes and source routes; `cards.json` holds the case matrix.

## Slide source

`build_slides.mjs` uses `@oai/artifact-tool`, `@napi-rs/canvas` and the OpenAI Presentations skill finalizer. These dependencies are supplied by the primary authoring runtime; they are not vendored. Set its standard `CODEX_PRIMARY_RUNTIME_ROOT`, `CODEX_PRIMARY_RUNTIME_NODE`, `CODEX_PRIMARY_RUNTIME_NODE_MODULES` and `CODEX_PRIMARY_RUNTIME_PYTHON` variables. Node module resolution must expose those runtime packages.

Set `PRESENTATION_SKILL_DIR` to the installed skill directory containing `container_tools`. Set `ATLAS_CAPSULE_DIR` to this showcase capsule, `ATLAS_FONT_REGULAR` and `ATLAS_FONT_BOLD` to licensed Inter TrueType files. Fonts are not redistributed. Set `ATLAS_BUILD_DIR` and `ATLAS_OUTPUT_DIR` to new writable locations outside the frozen capsule.

Run `node /path/to/presentation/build_slides.mjs final` in that configured authoring environment. The handoff copy was syntax-checked; the reviewed deck was built with the original authoring script using the same layout code. Do not claim a fresh render without reviewing its output. The existing PDF was exported from the exact reviewed PPTX with LibreOffice.

## Appendix source

With Python, ReportLab and the two Inter font files available:

```sh
python /path/to/presentation/render_appendix.py --content /path/to/presentation/appendix_content.json --font-regular /path/to/Inter-Regular.ttf --font-bold /path/to/Inter-Bold.ttf --output /new/path/appendix.pdf
```

The renderer refuses an existing output path. Render and inspect every generated page before using a new output. Neither document build executes project runtime or issues model calls.

## Reader source

The paired `build_reader.py`, `verify_reader.py` and `reader_content_manifest_v02.json` describe the selected reading artifact. Consult their `--help` and `reader/VERIFICATION.md`. The full capsule checksum manifest also covers supplemental presentation files added outside the Reader's indexed member set.

## V02R1 navigation repair

After a fresh slide build, run `python patch_navigation_links.py input.pptx linked.pptx --targets navigation_targets_V02R1.json` before PDF export. It adds the three native slide-22 links without layout changes. Use the same Inter font configuration for export. Check all three PDF URI annotations and actual public destinations after publication.
