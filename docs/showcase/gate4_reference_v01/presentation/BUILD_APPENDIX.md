# Technical appendix build

The editable source is `../technical_appendix_v01.md`. `build/render_appendix.py` is a data-only ReportLab renderer with no project imports. Install ReportLab separately and provide licensed local Inter Regular and Bold font paths; fonts are not distributed in this capsule. From the capsule root, use:

```sh
python3 presentation/build/render_appendix.py --input technical_appendix_v01.md --output technical_appendix_v01.pdf --font-regular /path/to/Inter-Regular.ttf --font-bold /path/to/Inter-Bold.ttf --anchors presentation/appendix_anchors.json
```

The provided PDF is the reviewed artifact; rebuild bytes can vary with the rendering toolchain. `qa/appendix_qa_v01.json` records its exact hash. All 19 pages were inspected. Relative Markdown source links are resolved into the intended repository namespace for the PDF; they require separate publication and repository access. The Markdown itself retains portable relative links. The outline and contents use the 12 explicit source anchors.
