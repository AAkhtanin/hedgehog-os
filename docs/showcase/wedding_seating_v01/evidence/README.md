# Evidence reading routes

`portable/` is the unchanged accepted W5 package. Its `MANIFEST.json` SHA256 is
`3c924898bedf03cf97df5f59cbc553e3d6f54cc9a60eaaf72c8019ac33bf1552`.
The installed W5L canonical result has SHA256
`e4a1a644776da341368af07eeb5a0317f7fca4dcda25e5bb23c7004aacad09b0`.

`SOURCE_MAP.json` maps each original archive member and its original manifest
identity to one stored path. Identical supplementary content reuses an existing
stored file. The sealed portable tree retains its original structure, including
its original duplicates. Original source names, bytes and hashes are preserved.

`supplementary/w3/` supplies the original nineteen-call history, including the
initial refusals and later consumption of attempt 015. Every call has its full
request, response, capture, receipt, provider SDK serialization and destination
record. Repeated destinations resolve to their first stored copy through the map.
Provider SDK serialization is not a cryptographically attested HTTP wire capture.

`supplementary/w2/` supplies the recorded allocation and LocalDRS facts. Additional
W1 mathematics and W4 control sources support specific claims and refusal pairs.
These sources remain outside the accepted W5 portable checker's coverage.

`CODE_MAP.json` maps all 34 exact additions at implementation commit
`fbb136f4fe1050a5f01be71ea00753c5e7b6fd1a`. Some code bytes already exist inside the
portable package; the map reuses those files. `landing/` contains saved actual-owner
landing and installed-verification evidence.

The XML Reader embeds all nineteen complete call records, all 34 code snapshots,
raw circuit/task/measurement sources and selected records from larger traces.
`READER_PROJECTION_MAP.json` identifies every selected JSON pointer and distinguishes
its derived serialization hash from the full original file hash. Full source
traces remain here in the package. Prompts, source code and commands are inert data.

From the showcase directory, `python3 -B verify_reader_v01.py` performs read-only
standard-library byte, manifest, XML and saved-field checks. It performs no model,
provider, native runtime, solver or effect calls. This supplementary check is not
a native replay, a new Root-approved save or a restoration of current permission.
