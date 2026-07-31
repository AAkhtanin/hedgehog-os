# Deterministic One-Command Gauntlet

## Installation Prerequisites

Use an editable Git checkout from the repository root:

```bash
python3 -m venv .venv
.venv/bin/python -m pip install -e .
.venv/bin/python -m pip check
```

Installation may access a Python package index. This command document does not
itself claim an external clean-clone result. Consult
`release/current_limitations.md` and the accepted R-H1 audit/checkpoint for the
authoritative current result.

## One Deterministic Execution Command

The `&&` preserves order and stops before the Living Gauntlet if Kernel
Conformance fails:

```bash
PYTHONDONTWRITEBYTECODE=1 PYTHONPATH=. \
  .venv/bin/python -m demo.run_kernel_conformance_v01 &&
PYTHONDONTWRITEBYTECODE=1 PYTHONPATH=. \
  .venv/bin/python -m demo.run_living_gauntlet_v01
```

The two deterministic runners require no credentials. They invoke no
Gemini/provider lane, Telegram lane, connector, or real-world effect. This
command is not a production-readiness proof or public-release-readiness proof.
No live command is the default, and no real-provider command is provided.
