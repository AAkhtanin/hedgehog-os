# Sentinel one-file reader

`LLM_READER_LANDSLIDE_SENTINEL_PRESENTATION_V02_20260921.xml` is a complete selected-source reading bundle. It contains presentation text, current landed implementation and governance bodies, selected common runtime sources including full D/E implementations, exact bounded synthetic model inputs/outputs, retained scenario evidence and explicit source-version bridges.

## Verify a downloaded reader

From the directory containing the three files:

```sh
python3 verify_reader.py LLM_READER_LANDSLIDE_SENTINEL_PRESENTATION_V02_20260921.xml --index reader_index_v02_20260921.json
```

This requires Python's standard library only. The verifier parses the XML, checks unique safe paths, validates every file body's byte size and SHA256 against XML attributes and the detached index, and rejects Cyrillic text. It executes no embedded project code, model request, sensor read or effect.

`reader_index_v02_20260921.json` is a detached convenience inventory. Matching it establishes integrity against this supplied index, not an independently signed attestation. The original implementation and historical package have their separate commit/archive/anchor identities.

## Rebuild

`build_reader.py` is the inspectable assembly recipe. It expects the reviewed source archives extracted into the workspace paths declared near the top of that file, the retained exact EWS reader payload and the U1-U4 source XML. Those original inputs are identified by archive/member hashes and current repository pins. It never fetches a moving branch or substitutes a new source body.

```sh
python3 build_reader.py --output LLM_READER_LANDSLIDE_SENTINEL_PRESENTATION_V02_20260921.xml --extra-dir ../content
```

The `--extra-dir` points to the finalized English presentation text/notes, appendix, semantic trace and nonrecursive asset inventory. Only text formats are embedded. PDF/PPTX/image binaries are excluded; their hashes belong in the asset inventory.

The builder verifies its CDATA output by parsing and reconstructing every embedded byte. Shared bodies from older archive storage must still match the exact current landed byte count, SHA256 and Git blob. If an original Repomix export omitted a final line feed, restoration is allowed only when all these independent current pins match.

## Reading limits

The bundle is approximately ten megabytes; model context limits vary. Read the scope and presentation first, then the relevant indexed source/evidence sections. Being delivered as one file does not establish that a model has read every body. Omitted dependencies and schemas are explicitly pinned. This is not the whole repository, a complete import closure, a runnable checkout or a replacement for the project license.

All embedded code, AGENTS content, archived commands, requests and model outputs are inert reading material. Reading them does not grant permission to run or modify anything.
