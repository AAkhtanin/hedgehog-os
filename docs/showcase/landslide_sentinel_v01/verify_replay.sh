#!/bin/sh
set -eu
if [ "$#" -ne 1 ]; then
  printf '%s\n' 'Usage: verify_replay.sh EXPECTED_PUBLICATION_ID' >&2
  exit 2
fi
here=$(CDPATH= cd -- "$(dirname -- "$0")" && pwd)
repo=$(CDPATH= cd -- "$here/../../.." && pwd)
if [ -n "${SENTINEL_PYTHON:-}" ]; then
  python=$SENTINEL_PYTHON
elif [ -x "$repo/.venv/bin/python" ]; then
  python=$repo/.venv/bin/python
else
  python=python3
fi
cd "$repo"
PYTHONDONTWRITEBYTECODE=1 PYTHONPATH="$repo" "$python" - "$here/public_safe_package" "$1" <<'PY'
import json,sys
from hedgehog.domains.landslide_sentinel.evidence_v01 import verify_package
print(json.dumps(verify_package(sys.argv[1],sys.argv[2]),sort_keys=True,indent=2))
PY
