# Presentation design and provenance

## Reference

The visual reference is the existing Testflix v1.1 deck in `AAkhtanin/hedgehog-os`, branch `showcase/testflix-v11-2026-09-13`, commit `b4aa8b7d39ccf71ec5122e0b02053481171cda9f`, under `docs/showcase/testflix_v11/`. Its PPTX SHA256 is `643464e002e1be666bbe2b4a1acdf888ea099190020677f73a031623a842b134`; its PDF SHA256 is `ac608e8becbbcf88f9ebe5fca8deb7d5d2e2414781161bc17ce292bd34e25006`.

The new deck retains the reference theme and wide 16:9 canvas, Inter typography, white backgrounds, graphite text, restrained gray panels and cobalt accents. Palette: `#FFFFFF`, `#F5F5F7`, `#1D1D1F`, `#6E6E73`, `#0071E3`. English text and tables are editable PowerPoint elements. The deck has 25 slides and nine native tables. Source notes accompany every slide. The two browser captures are images of actual retained fixture interactions.

## Artwork and captures

The new radiolarian is a generated conceptual illustration with a nested glass-like shell, fine graphite ribs and cobalt details. It is not a technical diagram, biological identification or execution evidence. [Hero provenance](assets/radiolaria_ephemeral_workspace_hero.provenance.json) retains its prompt and exact identity. [Cover](assets/cover.png) is the assembled first slide, including editable-deck typography rendered to an image.

[Capture provenance](assets/browser_capture_provenance_v01.json) identifies the two exact safe JPEGs, their archive members and hashes. Desktop and mobile captures represent different recorded stages, not simultaneous views. They are labelled scripted browser tests, not unaided human validation or physical-device certification.

The bundled Inter files and their OFL license match the reference assets. Their original font bytes remain unchanged. During PDF conversion a build-only copy of the bold font received corrected internal Bold/PostScript naming so the native converter selected the actual 700-weight face. That conversion detail does not modify the supplied reference font files.

## Formats and review

The PPTX was built from the imported reference theme with native presentation objects. The main PDF was converted from the final PPTX and contains searchable text with embedded Inter Regular/Bold. All 25 PDF pages were visually inspected, including metric labels, table headers, body wrapping and screenshot captions. The executive overview is one page; the separately typeset technical appendix is nine pages. Their pages were also rendered and reviewed. This is not a claim of testing every PowerPoint, Keynote or PDF viewer.

The HTML uses local fonts and images and has no script or network dependency. The XML includes exact final slide/notes extraction, complete PDF text and binary identities, alongside the explanatory source and evidence selection. Its own hash is intentionally excluded from its internal binary inventory. The outer distribution manifest covers the finished XML bytes.

All new textual assets were checked for Cyrillic. Historical source snapshots remain exact. Presentation layout review does not add a runtime result or change evidence authority.
