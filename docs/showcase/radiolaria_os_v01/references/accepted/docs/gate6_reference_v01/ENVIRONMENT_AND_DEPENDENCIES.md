# Environment and Dependency Provenance

`dependency_inventory.json` records the observed CPython/platform, installed
distribution metadata, available license identifiers/files, declared requirements
and consistency findings. Existing dependencies were read only; nothing was
installed, upgraded or pulled. Missing metadata is UNKNOWN, not license clearance.

Inspection is stdlib-only. Supplied verification uses the existing project runtime
dependencies, notably jsonschema and the accepted crypto/Work dependencies. pytest
is a development prerequisite, not needed for default inspection. Provider SDKs,
Docker and QPU integration are optional historical execution dependencies; this
reader starts no provider, container or QPU. Historical kit copies retain their
own source/license provenance and are checked for exact identity when imported.

Recipe only, not a fresh-install result:

```sh
python3 -m venv .venv
.venv/bin/python -m pip install -e .
.venv/bin/python -B demo/verify_gate6_reference_v01.py --output /tmp/g6-inspect
.venv/bin/python -B demo/verify_gate6_reference_v01.py --mode supplied --output /tmp/g6-proof
```

The project declares pytest in its main dependencies and has no development extra.
G6A5 does not execute this installation recipe. Supported observed verification environment is macOS arm64 /
CPython 3.14.5. Other Python versions, platforms and fresh installs are NOT_TESTED.

The repository LICENSE and existing commercial terms are unchanged. This inventory
is technical redistribution hygiene, not a legal audit or legal advice. New payload
scans cover private-key/API-key patterns and operational locator classification;
synthetic canaries remain labelled evidence. A detected usable secret would block
publication rather than be redacted and rehashed as if it were original evidence.
