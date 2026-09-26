# Main presentation source

`build_deck.mjs` creates the thirty-slide, editable presentation with `@oai/artifact-tool`.
`slide_content.json` is the generated source/claim/section inventory of those same slides.
`facts.json` carries the common engineering and experimental values. The builder refuses a
mismatch with those values before rendering. The capsule's `content_manifest.json` joins
these slides to the three dossier chapters and the machine Reader.

This is a publication recipe, not a candidate or a runtime experiment. It reads the
identified cover artwork and the fact index. It does not invoke an author, provider,
Root, Work, Host or native booking process.

## Environment

The reviewed build used the Codex primary runtime, JavaScript ES modules, the supplied
`@oai/artifact-tool` package, the Presentations skill finalizer and Inter. Font binaries
are not redistributed. Rebuilding requires those existing dependencies. No dependency
installation, network download or owner-repository mutation is part of this recipe.

Use a new external build directory, link its `node_modules` to the supplied runtime
module directory and copy `build_deck.mjs` there. Set `G56_CAPSULE` to this capsule's
absolute path, `G56_DECK_WORK` to the new private build directory and
`PRESENTATION_SKILL_DIR` to the local Presentations skill directory. Existing
`CODEX_PRIMARY_RUNTIME*` variables identify the runtime. Run the copied module with
the supplied Node executable. `--pilot` renders slides 06, 12, 19 and 28. With no flag,
the module renders all thirty slides and validates the PPTX. Use a fresh directory for
another build, or a new `DECK_REVISION` value for a corrected export.

The builder produces a draft and a separately validated PPTX. The reviewed final file
was converted to PDF with LibreOffice, retaining searchable text and hyperlinks.
The PDF's document metadata and thirty outline entries were set from the generated
slide inventory. The owner-requested cover revision replaces only the embedded image
object in the PDF and the image plus artwork provenance in the PPTX. All slide text,
layouts, links, outlines and the remaining twenty-nine pages stay unchanged. PDF export can wrap text differently from the initial slide preview,
so both outputs were visually inspected and the affected layouts corrected.

## Reading routes

The stable route index below is an alternative to PowerPoint custom shows. It selects
existing slides and creates no separately edited short deck.

- Short overview: 01, 02, 06, 08, 12, 15, 19, 22, 26, 30.
- Football: 01–03, 04–11, 26, 27, 30.
- External DRS: 01–03, 12–18, 28, 29, 30.
- Independent Authoring: 01–03, 19–25, 26, 27, 30.

All text, diagrams and the tables on slides 04, 06 and 17 are editable native objects.
The cover artwork is a new eight-ray conceptual brand illustration, identified in
`../assets/PROVENANCE.md`. It is not execution evidence. Engineering citations use the
exact commit `64f2b38b0d671e4907bae8649fff8f3d2ee0751c`; the future G56 publication
commit is not invented. Access to repository links requires authorization while the
repository remains private.

For the reviewed PDF conversion, Inter was supplied privately from the official
`rsms/inter` repository's `docs/font-files/InterVariable.ttf` (Git blob
`4ab79e0102bbe0ffa1ed879b13e52ac8c6487833`, SHA-256
`4989b125924991b90d05b2d16e0e388c48f7d5bb8b30539bbf9c755278d0ccaf`).
Static 400/600/700 weight instances at optical size 14 were used only by the local
font configuration. The final PDF embeds Inter subsets. No standalone font binary
is included in this capsule. The PPTX keeps Inter as editable text and requires the
font to be available in the reader's presentation application for an exact match.
