# Hedgehog OS Two-Domain All-Real Sealed Evidence Program v0.1
## R1-I2A Airline Gate-1 Source-Lineage Compatibility Replacement Preflight

## 1. Metadata

document_id: two_domain_all_real_sealed_evidence_program_v01_r1_i2a_airline_kernel_source_lineage_compatibility_preflight

document_status: PREFLIGHT

preflight_status: READY_FOR_REVIEW

programme_id: two_domain_all_real_sealed_evidence_program_v01

programme_version: v0.1

gate_id: two_domain_all_real_sealed_evidence_program_v01_r1_i2a_airline_kernel_source_lineage_compatibility

observed_base_head: b1096c2

planning_only: true

production_code_modified: false

tests_modified: false

shared_evidence_contracts_modified: false

kernel_modified: false

airline_kernel_adapter_modified: false

pytest_called: false

collector_called: false

runner_called: false

provider_called: false

network_called: false

gemini_called: false

package_created: false

anchor_created: false

filesystem_replay_performed: false

real_world_effects_count: 0

immediate_next_gate: two_domain_all_real_sealed_evidence_program_v01_r1_i2a_airline_kernel_source_lineage_compatibility_repair

## 2. Executive Verdict

`READY_FOR_REVIEW` for one narrow compatibility reopening of the frozen G1-D1
Airline Kernel adapter. The accepted source-aware Airline Ledger, Crypto, and
Replay chain is incompatible with two internal calls that omit the already
available contextual expected identity. A later repair may change only the
Airline Kernel adapter and its focused test. This preflight authorizes no
implementation.

The contradiction does not invalidate the original Gate-1 fixture proof. It
shows that the post-Gate-1 sealed-evidence programme requires one contextual
extension while preserving every existing public surface and proof geometry.

## 3. Repository Guard

The observed repository guard is:

- `HEAD`: `b1096c2`;
- `origin/main`: `b1096c2`;
- branch: `main`;
- staged files: none;
- existing R1 worktree: exactly eight untracked implementation and focused-test
  paths;
- frozen G1-D1 Airline Kernel adapter SHA-256:
  `34b10f07613fba74cf2ae1a03e4077bc5fbd36d710385b5c485f825eb459e28f`.

The eight existing R1 paths are frozen byte-for-byte during this planning gate.
This document and the active `AGENTS.md` checkpoint block are the only
authorized changes.

## 4. Accepted R1-I2A State

The current accepted partial R1-I2A state is:

- shared focused suite: `910 PASS`;
- Airline focused suite: `329 PASS / 1 FAIL`;
- the sole failure is the real committed-contract compatibility test;
- the Package Manifest seam is `PASS`;
- exactly 19 evidence artifacts remain;
- all six safe source records are covered;
- Kernel Manifest source grounding is `PASS`;
- source lineage and BSEP identity/reference binding are implemented;
- the owner-normalized safe-input boundary is explicit;
- source live counters remain `12 / 12 / 12` exactly once;
- adapter-phase external counters remain `0 / 0 / 0`;
- authority, permission, action, receipt, FinalOutput, and effect counts remain
  zero.

No collector, runner, package, Anchor, filesystem Replay, provider, network,
Gemini, authority, permission, action, receipt, FinalOutput, or effect was
executed while establishing this state.

## 5. Concrete Compatibility Contradiction

The source-aware Airline Ledger, Crypto collection, Replay input, and Replay
report validate with a dynamically derived expected identity. The frozen
Airline Kernel adapter discards that context at two separate call sites.

The first call revalidates the Ledger without its contextual identity. The
Ledger validator therefore falls back to the deterministic fixture source
refs. The second call builds Crypto Ledger-entry projections without that same
identity and reaches the same fixture fallback. The source-derived chain then
fails closed with:

`airline_kernel_adapter_source_input_invalid`

This is a cross-generation compatibility contradiction between an accepted
source-aware Replay contract and the earlier frozen fixture-only Kernel
adapter, not a failure of the source-derived evidence.

## 6. Why Original Gate 1 Remains Valid

Gate 1 remains `CLOSED_PASS` for the exact frozen fixture contract it tested.
The original fixture path uses the expected fixture source refs, 19 Ledger
entries, 29 dependency edges, three Root finals, and the accepted no-effect
boundaries. The omission of contextual identity does not alter that path
because the fallback identity is its intended identity.

The later repair must add source-derived compatibility without changing the
meaning, result, identity, geometry, or validation outcome of the original
fixture path. This preflight makes no broader claim about arbitrary Airline
integrations or production readiness.

## 7. Frozen-Surface Reopening Authority

The consolidated programme preflight freezes the Gate-1 Kernel and domain
surfaces unless a concrete contradiction is identified by read-only review,
independently reproduced, approved through a replacement preflight, and
reviewed before editing. Those conditions are now satisfied for this narrow
Airline adapter seam.

A later implementation is authorized to modify exactly:

1. `hedgehog/domains/airline/kernel_adapter_v01.py`;
2. `tests/test_airline_kernel_adapter_v01.py`.

No neutral Kernel module, shared evidence module, Ledger module, Crypto module,
Replay module, release index, schema, domain package adapter, or other test is
authorized for modification by the compatibility repair.

## 8. Exact Two-Call Repair

### A. Source Validation Seam

Current frozen call:

```python
validate_airline_transaction_artifact_ledger_v01(ledger)
```

Required future contextual call:

```python
validate_airline_transaction_artifact_ledger_v01(
    ledger,
    expected_identity=expected_identity,
)
```

### B. Kernel Projection Seam

Current frozen call:

```python
build_airline_crypto_ledger_entry_projections_v01(ledger)
```

Required future contextual call:

```python
build_airline_crypto_ledger_entry_projections_v01(
    ledger,
    expected_identity=expected_identity,
)
```

Repairing only one call is insufficient. Source validation and Kernel artifact
projection must consume the same internally derived expected identity or the
adapter can validate one lineage while projecting another.

## 9. Expected-Identity Derivation Law

The future repair must derive expected identity only through the existing
public Replay contract:

```python
build_airline_sealed_trace_replay_expected_identity_adapter_v01(
    ledger_item=replay_input.ledger_item,
    accepted_ledger_audit=replay_input.accepted_ledger_audit,
)
```

The derivation occurs inside the Airline Kernel adapter. A caller must not
supply expected identity. The repair must not add a public function argument,
dataclass field, status, or second identity representation. A source-derived
Ledger must not be validated or projected with fixture source refs.

Malformed identity derivation, an invalid accepted audit, or any identity
disagreement must fail closed through the existing stable adapter status and
reason boundaries.

## 10. Public Surface Freeze

The later repair must preserve the public Airline Kernel adapter surface:

- `AirlineKernelAdapterResultV01` fields and field order unchanged;
- `build_airline_kernel_adapter_result_v01` signature unchanged;
- `validate_airline_kernel_adapter_result_v01` signature unchanged;
- `airline_kernel_adapter_result_to_plain_dict_v01` signature unchanged;
- existing module constants and statuses unchanged;
- module dependency boundary unchanged.

The expected identity is private derived context. It is not a new public
contract and must not appear in the result projection.

## 11. Fixture Compatibility Preservation

The future repair must retain the original fixture path and preserve:

- Offer A and exact transaction identity;
- 19 Kernel artifacts;
- 29 causal references;
- three Root finals;
- nine source files;
- eleven critical files;
- nineteen Replay rows;
- `signature_verified: false`;
- no Root Attestation;
- Gate-1 adapter provider/network/Gemini counts `0 / 0 / 0`;
- real-world effects zero;
- all existing fixture identities and public projections.

The repair is contextual validation. It creates no new Airline domain law.

## 12. Source-Derived Compatibility Requirement

One pure in-memory source-derived path must pass all committed public
validators without replacing any production validator with synthetic `PASS`.
It must derive the Ledger expected identity from the Replay input and accepted
Ledger audit, use that identity for both missing call sites, and then build and
validate the Airline Kernel adapter result.

The test must bind source run, source causal report, source Corridor report,
accepted audit, artifact IDs, source-validation refs, canonical source
identity, Crypto collection, Replay input, and Replay report. It must invoke no
collector or runner and must not read or write package files.

## 13. Negative Test Matrix

The later focused tests must prove:

1. the existing fixture path still passes;
2. the source-derived Ledger path passes;
3. a source-run mismatch fails;
4. a source causal-report mismatch fails;
5. a source Corridor-report mismatch fails;
6. an accepted-audit mismatch fails;
7. an artifact-ID lineage mismatch fails;
8. a source-validation-ref mismatch fails;
9. a canonical source-identity mismatch fails;
10. malformed expected-identity derivation fails closed;
11. a caller cannot inject expected identity;
12. both source-aware call sites statically include `expected_identity`;
13. synthetic `PASS` and self-rehash attacks fail.

No test may monkeypatch a committed validator to return `PASS` for the real
compatibility path.

## 14. Bounded Validation

The later implementation may run:

```bash
python3 -m py_compile \
  hedgehog/domains/airline/kernel_adapter_v01.py \
  tests/test_airline_kernel_adapter_v01.py \
  hedgehog/domains/airline/sealed_evidence_package_adapter_v01.py \
  tests/test_airline_sealed_evidence_package_adapter_v01.py
```

Focused pytest only:

```bash
PYTHONPATH=. .venv/bin/python -m pytest -q \
  tests/test_airline_kernel_adapter_v01.py

PYTHONPATH=. .venv/bin/python -m pytest -q \
  tests/test_airline_sealed_evidence_package_adapter_v01.py

PYTHONPATH=. .venv/bin/python -m pytest -q \
  tests/test_sealed_evidence_profile_v01.py
```

After all three focused suites pass, authorize exactly once each:

```bash
PYTHONPATH=. .venv/bin/python -m demo.run_kernel_conformance_v01

PYTHONPATH=. .venv/bin/python -m demo.run_living_gauntlet_v01
```

Full repository pytest, provider tests, live calls, network, and Gemini remain
forbidden.

## 15. Forbidden Operations

This preflight and the future narrow repair forbid:

- provider, network, or Gemini calls;
- collector or project-runner execution during implementation;
- filesystem package creation or discovery;
- Anchor creation or publication;
- filesystem Replay;
- semantic, Root-decision, or Corridor reruns;
- Ledger or Crypto recollection;
- authority, permission, action, receipt, FinalOutput, or effect creation;
- public surface expansion;
- shared evidence, neutral Kernel, Ledger, Crypto, or Replay modification;
- release-index modification;
- staging, committing, or pushing without a separate owner instruction.

## 16. Commit and Audit Boundaries

The replacement preflight is one owner-reviewed planning commit boundary. The
later two-file compatibility repair is a separate implementation commit
boundary. Independent validation and the R1 checkpoint remain a later separate
audit/checkpoint boundary.

The repair commit must contain only the Airline Kernel adapter and its focused
test. The current eight untracked R1 files are preserved as the in-progress R1
implementation context and are not redesigned by this reopening. A failed
compatibility run is diagnostic evidence and is not promoted as `PASS`.

## 17. Definition of Done

The compatibility repair is complete only when:

- both missing calls use the same internally derived expected identity;
- no caller can inject or override that identity;
- the original fixture path passes unchanged;
- the real source-derived committed-contract path passes;
- both Kernel validation and Kernel projection preserve source lineage;
- all negative lineage mutations fail closed;
- 19 / 29 / 3 / 9 / 11 / 19 geometry remains exact;
- all public fields, functions, statuses, and dependencies remain frozen;
- all three focused suites pass;
- Kernel Conformance and Living Gauntlet each pass once after focused closure;
- provider/network/Gemini/effect counts remain zero;
- no unauthorized path changes.

## 18. Immediate Next Gate

After owner review and a separate preflight commit, the immediate next gate is:

`two_domain_all_real_sealed_evidence_program_v01_r1_i2a_airline_kernel_source_lineage_compatibility_repair`

Do not begin Supplier R1-I2B until this compatibility repair and its bounded
validation are independently reviewed and closed.
