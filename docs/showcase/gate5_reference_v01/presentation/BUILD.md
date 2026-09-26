# Building the publication

The main deck and the searchable dossiers are two document recipes. Neither executes the recorded experiment. Keep build outputs in a separate working copy of the capsule and put temporary outputs outside the owner repository.

## Main presentation

Follow [the main presentation recipe](README.md). It requires the existing JavaScript artifact-tool runtime and its presentation finalizer. The editable PowerPoint itself can be opened without that build environment. The accepted source does not redistribute fonts or install dependencies.

`facts.json` provides the shared numerical basis. `slide_content.json` records the 30 stable slide IDs, the C01–C24 claim groups, dossier sections and source references. `build_deck.mjs` produces native editable text, diagrams and tables. The cover remains a raster brand illustration with [provenance](../assets/PROVENANCE.md).

## Dossiers and combined appendix

`render_dossiers.py` reads the same `content_manifest.json` sections that produce F, D, A and shared Markdown. It creates the three standalone A4 dossiers and their combined technical appendix. It does not maintain a separate prose version for the appendix.

The recorded build used Python with ReportLab and DejaVu Sans / Mono. Fonts are environment dependencies, not files distributed in the capsule. The renderer's default Linux font paths are explicit near the top of the recipe and can be pointed at the corresponding licensed installed fonts in another document-building environment.

In a separate working copy, set `G56_CAPSULE` to the capsule directory and `G56_QA_OUT` to a new external diagnostics directory. Then run:

```sh
python3 presentation/render_dossiers.py --manifest content_manifest.json
```

The renderer creates `football_domain_v01.pdf`, `external_drs_v01.pdf`, `independent_authoring_v01.pdf` and `technical_appendix_v01.pdf`. These contain selectable text, clickable source links and bookmarks for stable section IDs. Their PDF creation metadata is not a promise of byte-for-byte reproduction across tool versions. The underlying source and claim bindings retain exact hashes.

## Final document checks

Render all unique pages and inspect text, formulae, tables, diagram labels, source links and page breaks. Compare each standalone dossier's body with the matching combined chapter. Inspect the PDF export separately from the PPTX preview because font substitution and line wrapping can differ between renderers. Keep future architecture visually and textually distinct from observed work.

Publication source review and the installed engineering proof remain separate methods. Building documents gives no new runtime permission and creates no new native or live evidence.
