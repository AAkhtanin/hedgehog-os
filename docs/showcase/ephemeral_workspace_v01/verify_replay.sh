#!/bin/sh
set -eu
if [ "$#" -ne 1 ]; then
    printf '%s
' 'Usage: verify_replay.sh EXPECTED_PUBLICATION_ID' >&2
    exit 2
fi
here=$(CDPATH= cd -- "$(dirname -- "$0")" && pwd)
repo=$(CDPATH= cd -- "$here/../../.." && pwd)
if [ -n "${EWS_PYTHON:-}" ]; then
    python=$EWS_PYTHON
elif [ -x "$repo/.venv/bin/python" ]; then
    python=$repo/.venv/bin/python
else
    python=python3
fi
cd "$repo"
PYTHONDONTWRITEBYTECODE=1 PYTHONPATH="$repo" exec "$python" -m demo.run_ephemeral_workspace_evidence_v01 replay --package-dir "$here/public_safe_package" --publication "$here/external_anchor_publication_v01.json" --expected-anchor "$1" --require-anchor
