# Final Content: Work Export Handoff

EXPORT_ASSIGNEE=WORK. Same frozen content, not another planning hop. There are 25 slides, 14 short-route IDs and eight Atlas views. All 22 previous positions remain addressable; S23-S25 add incident origins, Sentinel research and external context. Public notes use notes_en. Retained notes_ru remain internal historical data.

## Roots and Installed Runtime

Set P to the extracted postimages/docs/showcase/radiolaria_os_v01 and R to the extracted g6b_final_return. Set SKILL_DIR, RUNTIME_NODE, RUNTIME_NODE_MODULES, RUNTIME_BIN_DIR and RUNTIME_PYTHON from Work's actual installed presentation runtime. Do not install packages or infer Mac paths. Existing qualified Artifact Tool 2.8.74 and actual Nimbus Sans Regular/Bold are required. The owner-authorized B4 font decision on 2026-09-28 replaces the prior exact-Arial profile for this successor only. The exporter checks the actual Nimbus Sans family, Regular/Bold styles and installed font hashes; a mismatched family remains a qualification failure. Historical inputs and earlier font qualification results are unchanged.

EXPORT_INPUTS.json is an immutable positive input inventory. Its externally recorded digest is in work_export/SOURCE_PIN.json. Output inventories and new files are excluded from it, so finalization cannot invalidate its input pin. SOURCE_MANIFEST.json is the detached publication inventory, not the export trust root.

## Exact Commands

```bash
"$RUNTIME_NODE" "$P/presentation/build_main.mjs" validate --presentation-root "$P" --model presentation/main_native_objects.json --manifest EXPORT_INPUTS.json --manifest-sha256 "$EXPORT_INPUT_SHA"
"$RUNTIME_NODE" "$P/presentation/build_main.mjs" build --presentation-root "$P" --model presentation/main_native_objects.json --manifest EXPORT_INPUTS.json --manifest-sha256 "$EXPORT_INPUT_SHA" --run-dir work_native_01
"$RUNTIME_NODE" "$P/presentation/build_main.mjs" finalize --presentation-root "$P" --model presentation/main_native_objects.json --manifest EXPORT_INPUTS.json --manifest-sha256 "$EXPORT_INPUT_SHA" --run-dir work_native_01
"$RUNTIME_PYTHON" "$P/presentation/attach_links.py" inspect --plan "$P/work_native_01/build/export_plan.json" --input "$P/presentation/main.pptx" --presentation-root "$P" --report "$P/work_native_01/qa/final.native.json"
```

Render the actual final PPTX outside frozen inputs:

```bash
"$RUNTIME_PYTHON" "$SKILL_DIR/container_tools/render_slides.py" "$P/presentation/main.pptx" --output_dir "$P/work_native_01/rendered"
```

Convert the actual final PPTX to presentation/main_export.pdf with a qualified installed converter that preserves searchable text and real links. Preserve slide order. The raster page renders are private QA evidence, not the public PDF. Record the actual conversion path and checks; never label the native source PDF as a PPTX conversion. Do not overwrite main.pdf: it is the immutable source comparison. The finalizer checks OOXML structure, native editability, original bitmap bytes, links, notes and reading order against the exact source plan. That is not a visual PASS.

Inspect all 25 actual rendered slides against presentation/source_renders and main.pdf. Check text, arrows/direction, objects, hyperlinks and their local targets, English notes, fonts/Unicode, reading order and source consistency. Keep actual page images/observations in the Work evidence area; do not put QA screenshots into the public bundle. Fill a real visual_report.json with status ALL_SLIDES_INSPECTED_NO_UNRESOLVED_DEFECTS only after that inspection, exact model_sha256, pptx_sha256, rendered_pdf_sha256, slide_ids in model order, and checks mapping notes_en, hyperlinks, native_objects, arrows, fonts_unicode, reading_order, source_pdf_consistency to PASS. Record defects instead of signing this schema blindly.

```bash
"$RUNTIME_PYTHON" "$R/build_sources/finish_review_bundle.py" "$P" --allowlist "$R/public_bundle/PUBLIC_PAYLOAD_ALLOWLIST.json" --output "$R/public_bundle/RADIOLARIA_REVIEW_BUNDLE.zip" --final --native-report "$P/work_native_01/qa/final.native.json" --visual-report "$P/work_native_01/qa/visual_report.json"
```

This reopens every ZIP member, checks CRC and exact bytes, and includes actual export receipts. A missing PPTX, wrong source pin, incomplete slide list or absent visual check refuses finalization. Preserve the pre-export ZIP as historical handoff before replacing its output path. Rebuild the detached final publication/operator inventories after new outputs exist; do not modify EXPORT_INPUTS or its pin. Follow the active presentation skill for final rendering and delivery, not old Mac helpers.

## Remaining Boundary

Codex checks content, source PDF/HTML/XML, Reader dependencies and source-only exporter behavior. It does not claim actual PPTX, all-format B4, B5, source admission, deployment, DOI or Gate6 closure. Work completes the affected export checks; curator/owner reviews that concrete result. Then separately authorized B5 and later R1/publication operations remain. No model call or owner operation is authorized by this handoff itself.
