# Rebuild the Editorial Views

The return root contains build_sources/build_review.py, which takes a publication root and a separate QA directory. It reads the final Markdown/JSON/native model and regenerates only current PDFs, HTML and Readers. It imports no project runtime, invokes no provider and installs nothing. Historical pilots, source evidence and M2_FOCUS are preserved.

The current Work B4 profile uses installed Nimbus Sans Regular/Bold, explicitly authorized on 2026-09-28. The builders and exporter check that actual family; the former Arial requirement applies only to the preserved predecessor. Installed Python libraries and the qualified JavaScript runtime are recorded in the operator checks. The private PDF font adapter preserves the installed font's naming and metrics, records source/derived hashes, and uses installed per-glyph fallback only for otherwise missing mathematical Unicode. No separate font binaries are distributed.

The native Atlas and deck JSON are authoritative drawing sources; Markdown chapters/source key are authoritative prose. Builders accept supplied roots. Earlier development generators and source-integration receipts are retained as provenance, not a historical append sequence to replay.

Full PPTX export uses the frozen EXPORT_INPUTS.json and the return's work_export/SOURCE_PIN.json. The source comparison PDF is presentation/main.pdf; the actual editable deck and converted primary PDF are presentation/main.pptx and presentation/main_export.pdf. The finalizer consumes their actual native/visual inspection reports without changing frozen inputs. Inspect the detached final reports for completion and exact identities.

Open index.html directly for the offline Reader. Relative file links depend on the complete bundle and client security policy; accepted-source HTTPS targets are pinned to technical A. No unpublished HTTPS route is invented.
