# Hedgehog OS Two-Domain All-Real Sealed Evidence Program v0.1
## Airline A1 Attempt 04 Complete Corridor Capture Preflight

document_id: two_domain_all_real_sealed_evidence_program_v01_a1_attempt_04_complete_corridor_capture_preflight
document_version: v0.1
document_status: READY_FOR_REVIEW
implementation_gate: NOT_STARTED
local_packageability_gate: REQUIRED_BEFORE_LIVE
live_execution_gate: BLOCKED_PENDING_LOCAL_PACKAGEABILITY_CLOSED_PASS_ON_COMMITTED_HEAD
official_a2_gate: BLOCKED_PENDING_ACCEPTED_ATTEMPT_04
governing_repository_head: 3d82573a6f0f8891a81a7bad6d1c9b667448c0ae
provider_calls_during_preflight: 0
network_calls_during_preflight: 0
gemini_calls_during_preflight: 0
real_world_effects_during_preflight: 0
full_repository_pytest: NOT_RUN

## 1. Decision

This preflight authorizes review of one bounded implementation that persists
the complete already-created Airline Corridor report and proves that the
persisted attempt is packageable before any new live call.

The fixed sequence is:

1. implement Corridor archival persistence and the source-agnostic A2 reader;
2. prove local packageability across a fresh-process boundary;
3. commit the green implementation;
4. repeat local packageability on the clean committed implementation HEAD;
5. after owner review, perform exactly one new official Attempt 04;
6. independently audit Attempt 04; and
7. use accepted Attempt 04 alone as the official A2 content source.

Attempt 04 is an evidence-completeness successor. It is not a retry, resume,
repair, mutation, or relabelling of an earlier attempt.

## 2. Completed Attempt 03 Forensic Result

The read-only forensic verdict is:

`ABSENT_COMPLETE_ACCEPTED_CORRIDOR_REPORT`

Exact audit geometry:

| Check | Result |
| --- | ---: |
| Accepted inventory rows | 72 |
| Inventory JSON files strictly parsed | 35 |
| Accepted metadata JSON files strictly parsed | 3 |
| Eligible JSON documents recursively inspected | 38 |
| Forbidden raw bodies not opened | 36 |
| Non-JSON structural files not parsed | 1 |
| Invalid or unverifiable files | 0 |
| Complete Corridor candidates | 0 |
| Partial report-shaped objects | 14 |

No stored object contained the complete phase, transition, delegation,
summary, counter, contract-context, validation-error, and next-gate geometry
together.

Consequences:

- Attempt 03 remains an immutable valid `CLOSED_PASS` system execution.
- Attempt 03 is `A2_SOURCE_INCOMPLETE` only for complete typed packaging
  source sufficiency.
- Attempt 03 cannot be used as the complete official A2 content source.
- No field may be invented, repaired, inferred, merged, or reconstructed for
  Attempt 03.
- Attempt 04 reruns all twelve semantic roles and the entire frozen Airline
  chain exactly once under a new immutable identity.
- The only new production behavior is archival persistence of the complete
  already-created Corridor report.

## 3. Exact Implementation Scope

### 3.1 A1 Archival and Attempt 04 Paths

Exactly these four existing paths may be modified:

1. `demo/run_tri_party_airline_live_semantic_lane_v01.py`
2. `tests/test_tri_party_airline_live_semantic_lane_v01_runner.py`
3. `demo/run_two_domain_airline_all_real_program_v01.py`
4. `tests/test_two_domain_airline_all_real_program_v01_runner.py`

The live-lane changes are limited to archival persistence of the already-built
report and focused proof of that persistence. The outer runner changes are
limited to Attempt 04 branch, predecessor, output, identity, inventory, gate,
and local-packageability orchestration.

### 3.2 Shared Package Compatibility and A2 Paths

The full implementation-content order is frozen as exactly these twelve paths:

1. `demo/run_tri_party_airline_live_semantic_lane_v01.py`
2. `tests/test_tri_party_airline_live_semantic_lane_v01_runner.py`
3. `demo/run_two_domain_airline_all_real_program_v01.py`
4. `tests/test_two_domain_airline_all_real_program_v01_runner.py`
5. `demo/run_sealed_evidence_package_v01.py`
6. `tests/test_sealed_evidence_package_v01_runner.py`
7. `hedgehog/domains/airline/sealed_evidence_a2_binding_v01.py`
8. `tests/test_airline_sealed_evidence_a2_binding_v01.py`
9. `demo/run_two_domain_airline_a2_seal_v01.py`
10. `tests/test_two_domain_airline_a2_seal_v01_runner.py`
11. `hedgehog/domains/airline/sealed_evidence_package_adapter_v01.py`
12. `tests/test_airline_sealed_evidence_package_adapter_v01.py`

The combined pre-live implementation scope is exactly twelve code/test paths.
No thirteenth code or test path is authorized. The shared Package
implementation remains frozen except for the closed contextual safe-reference
compatibility repair in the A2 preflight. No general scanner relaxation is
authorized.

## 4. Exact Corridor Persistence Law

The new private member is exactly:

`raw_attempt/airline_ticket_purchase_corridor_run_report_v01.json`

Its sole source is the already-created typed object:

```text
integrated_deterministic_report
._airline_transaction_artifact_ledger_source_bundle_v0_1
.corridor_report
```

This must be the same object consumed by the existing Ledger source bundle.

Forbidden archival sources and operations are:

- a second Corridor collector call;
- a Corridor builder call for archival purposes;
- reconstruction from Ledger entries or snapshots;
- reconstruction from aggregate summaries;
- reconstruction from implementation constants;
- fixture substitution;
- test-double substitution in production;
- default insertion, trimming, coercion, or field repair; and
- mutation of the report before or after serialization.

Persistence occurs in the common injected/real successful lane after the
deterministic result and source bundle validate and before the existing secret
scan.

## 5. Exact Type and Geometry Validation

Before writing, require:

- exact type `AirlineTicketPurchaseCorridorRunReportV01`;
- existing production Corridor run validator `PASS`;
- existing Ledger source-bundle validator `PASS`;
- exact typed equality with `ledger_source_bundle.corridor_report`;
- all 16 required report fields;
- all nested phase, transition, delegation, contract-context, summary,
  counter, validation-error, and next-gate fields;
- five phase rows in canonical order;
- four transitions in canonical order;
- eight core-delegation rows in canonical order;
- exactly two core-direct delegation rows;
- final status `PASS`;
- empty failed phase;
- empty return-to-Root field;
- empty validation errors;
- mock-only Corridor boundaries; and
- zero provider-created authority and zero real-world effects.

The persisted report is data evidence. It creates no authority, permission,
action, payment, ticket, booking, receipt authority, FinalOutput, or effect.

## 6. Canonical Private Write Law

The writer must prove:

- exact UTF-8 JSON with sorted keys and compact canonical separators;
- exactly one terminal LF;
- strict JSON types;
- no duplicate keys or non-finite numbers;
- no NUL, CR, BOM, trailing whitespace, or trailing bytes;
- absent target and exclusive creation;
- non-following directory-descriptor traversal;
- `O_EXCL` and `O_NOFOLLOW` where supported;
- exact regular-file mode `0600`;
- complete write loop with short-write and zero-write handling;
- file fsync and parent-directory fsync;
- proven descriptor close with existing raw-close fallback law;
- descriptor-bound reread and descriptor/entry identity equality;
- exact expected bytes and SHA-256;
- strict parse and canonical-byte equality; and
- semantic equality with the original typed report.

A partial write, fsync failure, close failure, reread mismatch, inode
replacement, mode drift, semantic mismatch, or cleanup uncertainty fails
closed. Cleanup removes only an exact invocation-owned inode.

## 7. Inventory, Secret, and Freeze Binding

The new member is included in:

- the existing secret scan before source PASS;
- exact raw inventory, changing successful geometry from 72 to 73 files;
- private-inventory logical-name/SHA-256/byte rows;
- aggregate inventory digest;
- generation-gate proof;
- post-write inventory rescans; and
- final attempt-freeze rescans.

The secret scan reads the safe canonical archive bytes and must still report
PASS. The archive contains no prompt, raw provider response, credential, owner
path, traceback, object representation, or private body.

Explicit Crypto nonclaim:

- the new Corridor archive is not independently bound by the live lane's
  existing nine-source Crypto manifest;
- the existing nine-source manifest is not widened or relabelled;
- the archive is bound by Attempt 04 private inventory and generation gate;
  and
- the archive is later cryptographically bound by the official A2 Package.

## 8. Local Packageability Gate

No real Attempt 04 provider call is authorized until the exact gate in this
section passes twice: first during implementation review and then on the clean
committed implementation HEAD.

### 8.1 Process A: Persisted Simulated-Real Attempt

Process A:

- uses the real-mode contract path with established simulated-real dependency
  injection;
- uses synthetic immutable Attempt 03 predecessor proof;
- persists only the simulated-real Attempt 04, `safe-report-v01.json`, and
  `process-a-result-v01.json`; it constructs neither source variant;
- uses the exact production Corridor persistence seam;
- observes 12 callbacks, starts, and completions in frozen actor order;
- performs one collector invocation;
- performs one deterministic Airline collection;
- performs one Corridor execution;
- performs one Ledger collection;
- performs one Crypto collection;
- observes provider SDK/network/Gemini/effect operations `0 / 0 / 0 / 0`;
- writes only invocation-owned temporary attempt and safe-report paths outside
  the repository; and
- exits without passing Python objects, open descriptors, or process memory to
  Process B.

### 8.2 Process B: Fresh Hydration and Temporary Package

Process B:

- runs in a fresh interpreter;
- opens only the temporary attempt through the production descriptor-bound A2
  reader;
- strictly hydrates the Corridor report and all six exact Airline adapter
  inputs;
- invokes no provider, network, Gemini, collector, Corridor builder or runner,
  Ledger recollection, or Crypto recollection;
- validates the hydrated Ledger source bundle and expected Ledger identity;
- validates Ledger, Crypto, historical sealed replay input/report, Kernel
  adapter, Airline package adapter, and `DomainEvidenceProjectionV01`;
- constructs the exact safe Package members;
- calls the frozen shared Package Python API exactly once;
- uses `fixture_disposable=False`;
- writes to an absent invocation-owned noncanonical Package root outside the
  repository;
- invokes no Package CLI, Anchor owner command, or Replay owner command;
- rereads and independently validates the Package from disk; and
- removes only exact invocation-owned temporary output.

The Process-A/Process-B boundary is the exact internal file
`process-a-result-v01.json`, represented by the immutable A2-runner type
`AirlineA2LocalProcessAResultV01`. Its closed schema is:

```text
result_id: str
result_version: Literal["v0.1"]
gate_phase: Literal["precommit", "committed-head"]
verified_head_token: str
implementation_content_sha256: str
attempt_id: str
execution_head: str
attempt_identity_sha256: str
private_inventory_sha256: str
private_inventory_digest: str
generation_gate_sha256: str
corridor_archive_logical_name: Literal["raw_attempt/airline_ticket_purchase_corridor_run_report_v01.json"]
corridor_archive_sha256: str
corridor_archive_byte_count: int
safe_report_logical_name: Literal["safe-report-v01.json"]
safe_report_sha256: str
safe_report_byte_count: int
safe_execution_id: str
wrapper_callback_observed_count: Literal[12]
provider_callback_started_count: Literal[12]
provider_callback_completed_count: Literal[12]
semantic_actor_call_count: Literal[12]
causal_actor_call_count: Literal[5]
generic_actor_call_count: Literal[7]
duplicate_actor_call_count: Literal[0]
collector_invocation_count: Literal[1]
deterministic_airline_collection_count: Literal[1]
ticket_purchase_corridor_execution_count: Literal[1]
airline_transaction_artifact_ledger_collection_count: Literal[1]
airline_crypto_artifact_seal_collection_count: Literal[1]
outbound_provider_sdk_call_count: Literal[0]
outbound_network_call_count: Literal[0]
outbound_gemini_call_count: Literal[0]
real_world_effects_count: Literal[0]
final_status: Literal["PASS"]
validation_errors: tuple[str, ...]
```

`validation_errors` is exactly empty. The exact APIs are
`build_airline_a2_local_process_a_result_v01`,
`validate_airline_a2_local_process_a_result_v01`, and
`airline_a2_local_process_a_result_to_plain_dict_v01`, with the complete typed
signatures frozen in the A2 preflight. `result_id` uses domain
`hedgehog-os:airline-a2-local-process-a-result:v0.1`, one NUL byte, canonical
JSON without terminal LF, and an exactly 64-zero `result_id` slot. Stored bytes
are canonical UTF-8 JSON plus one LF and use exclusive absent creation,
complete write, fsync, close, descriptor-bound reread, strict reconstruction,
exact byte/plain/typed equality, inode and mode proof, and ownership-safe
cleanup.

The object contains no raw body, credential, absolute path, invocation ID,
Package ID, or caller-selected identity. Process A uses the exact literal
`safe-report-v01.json` for both its result and the owned local safe report.
Process B alone loads and validates this object and every descriptor-verified
file, cross-checks every hash and byte count, derives
`LOCAL_NONPUBLICATION_SOURCE`, derives the gate-phase-appropriate local Package
invocation, and then performs hydration and temporary Package validation. It
never trusts this object without file agreement. No invocation object or ID
crosses the process boundary.

The six exact hydrated adapter inputs are, in order:

1. `AirlineSafeExecutionProjectionV01`;
2. `AirlineTransactionArtifactLedgerSourceBundleV01`;
3. `AirlineCryptoArtifactSealCollectionResultV01`;
4. `AirlineSealedTraceReplayInputV01`;
5. `AirlineSealedTraceReplayReportV01`; and
6. `AirlineKernelAdapterResultV01`.

Their closed source and validator map is:

| Type | Exhaustive source law | Committed builder/constructor and validator |
| --- | --- | --- |
| `AirlineSafeExecutionProjectionV01` | mode-appropriate safe report exact keys: execution/source IDs, provider/model/status, twelve actors, BSEP, three Roots, Corridor, three receipts, 12/12/12 source-shaped counters, raw-material flags, secret scan, effects, and errors | `build_airline_safe_execution_projection_v01`; `validate_airline_safe_execution_projection_v01` |
| `AirlineTransactionArtifactLedgerSourceBundleV01` | exact source-bundle and transaction identities, expected refs, four BSEP projections, complete causal report, nine Corridor artifacts, persisted `corridor_report`, three Root finals, source validation refs, and auxiliary observation refs from validated causal/BSEP/bridge/Corridor/Ledger sources; no field comes from a fixture or free constant | exact committed nested dataclass constructors and `AirlineTransactionArtifactLedgerSourceBundleV01`; `validate_airline_transaction_artifact_ledger_source_bundle_v01`; expected identity from `build_airline_transaction_artifact_ledger_expected_identity_from_source_v01` |
| `AirlineCryptoArtifactSealCollectionResultV01` | every identity, manifest/envelope/verification object, source-bundle report, byte-stability flag, stage counter, zero counter, status, and error from the validated nine-source snapshot, Ledger, raw manifest, raw verification, and safe summary | exact committed dataclass constructors; `validate_airline_crypto_artifact_seal_collection_result_v01` |
| `AirlineSealedTraceReplayInputV01` | source package ref, accepted Ledger audit, stored Ledger, envelope, stored verification, deterministic fresh matching verification, expected manifest hash, and exact ordered nine source bytes | `build_airline_sealed_trace_replay_input_v01`; `validate_airline_sealed_trace_replay_input_v01` |
| `AirlineSealedTraceReplayReportV01` | every replay identity, integrity/continuity/lineage boolean, geometry counter, zero counter, 19-row timeline, status, and error from the validated replay input and unchanged package bytes | `verify_airline_sealed_trace_replay_v01`; `validate_airline_sealed_trace_replay_report_v01` |
| `AirlineKernelAdapterResultV01` | every source identity/status, three Root IDs, 19 Kernel artifacts, Manifest, unanchored/anchored verification, replay, 29 causal refs, geometry, and zero counters from the validated replay input/report | `build_airline_kernel_adapter_result_v01`; `validate_airline_kernel_adapter_result_v01` |

The complete Corridor report populates only the existing
`AirlineTransactionArtifactLedgerSourceBundleV01.corridor_report` field. It is
not copied into an auxiliary dictionary or parallel untyped slot. The complete
field-by-field hydration schema in the A2 preflight is normative here.

Corridor archive acceptance has no validation-identity field. Canonical stored
bytes must equal the hydrated typed report's canonical bytes plus one LF; the
archive SHA-256 and byte count must equal the verified private-inventory row;
`validate_airline_ticket_purchase_corridor_run_v01` must PASS with empty
validation errors; and hydrated typed equality must be exact. No replacement
identity may be invented.

The legacy
`build_airline_sealed_evidence_package_adapter_result_v01` API remains
byte-for-byte and behaviorally unchanged with its legacy Attempt-1 geometry.
The adapter must not import the A2 binding module. The A2 binding maps into the
adapter-owned immutable
`AirlineSealedEvidencePackageAdapterInvocationV01`, whose exact fields are:

```text
invocation_mode, attempt_number, package_id, logical_package_ref,
output_directory_ref, provider_mode, model_id, expected_actor_count,
provider_call_budget, s1_evidence_class, s2_evidence_class,
s1_observed_provider_call_count, s1_observed_network_call_count,
s1_observed_gemini_call_count, s2_observed_provider_call_count,
s2_observed_network_call_count, s2_observed_gemini_call_count,
limitation_refs
```

Its exact APIs are:

```text
build_airline_sealed_evidence_package_adapter_invocation_v01
validate_airline_sealed_evidence_package_adapter_invocation_v01
airline_sealed_evidence_package_adapter_invocation_to_plain_dict_v01
build_airline_sealed_evidence_package_adapter_result_for_invocation_v01
validate_airline_sealed_evidence_package_adapter_result_for_invocation_v01
airline_sealed_evidence_package_adapter_result_for_invocation_to_plain_dict_v01
```

The complete signatures in the A2 preflight are normative. Both modes derive
`LiveAttemptIdentityV01` from this invocation object with exact Attempt number
4 instead of the legacy hard-coded Attempt-1 values.

The invocation builder accepts no `limitation_refs` argument. It derives the
following exact official tuple solely for `OFFICIAL_ACCEPTED`:

```text
(
    "limitation:par_lim_only_airline_geometry",
    "limitation:frozen_accepted_airline_evidence",
    "limitation:mock_corridor",
    "limitation:no_new_all_real_run_during_r1",
    "limitation:no_real_ticket_booking_payment_bank_gds_connector_action",
    "limitation:no_arbitrary_airline_integration",
    "limitation:no_production_signer",
    "limitation:no_signer_identity_verification",
    "limitation:no_root_attestation",
    "limitation:no_pki",
    "limitation:no_production_certification",
    "limitation:owner_built_safe_normalization_not_raw_provider_report",
)
```

It derives the following exact truthful tuple solely for
`LOCAL_NONPUBLICATION`:

```text
(
    "limitation:par_lim_only_airline_geometry",
    "limitation:mock_corridor",
    "limitation:no_real_ticket_booking_payment_bank_gds_connector_action",
    "limitation:no_arbitrary_airline_integration",
    "limitation:no_production_signer",
    "limitation:no_signer_identity_verification",
    "limitation:no_root_attestation",
    "limitation:no_pki",
    "limitation:no_production_certification",
    "limitation:owner_built_safe_normalization_not_raw_provider_report",
    "limitation:local_simulated_real_compatibility_geometry_permanently_nonpublication",
)
```

Local mapping is `invocation_mode=LOCAL_NONPUBLICATION`,
`provider_mode=deterministic_fixture`, provider budget `0`, S1/S2 evidence
class `EXECUTED_DETERMINISTIC_RUNTIME`, S1/S2 observed counts `0 / 0 / 0`,
source and projection totals `0 / 0 / 0`, and the mandatory local
nonpublication limitation. All four BSEP-derived artifact records use
`EXECUTED_DETERMINISTIC_RUNTIME`; no live-evidence class appears in the local
projection.

Official mapping is `invocation_mode=OFFICIAL_ACCEPTED`, Attempt 4, Package ID
and refs from `OFFICIAL_PACKAGE_INVOCATION`, `provider_mode=real_provider`,
provider budget `12`, S1 `EXECUTED_LIVE_RUNTIME` at `12 / 12 / 12`, S2
`LIVE_PROVIDER_SAFE_PROJECTION` at `0 / 0 / 0`, BSEP-derived artifact records
`LIVE_PROVIDER_SAFE_PROJECTION`, source totals `12 / 12 / 12`, and projection
operation totals `0 / 0 / 0`.

The future A2 binding owns the official-only immutable
`AirlineA2SafePackageIndexV01` and its exact builder, validator, plain
projection, closed schema, zero-slot identity, canonical-byte, exclusive
write, fsync, descriptor-reread, and cleanup laws defined in the A2 preflight.
It binds the official source and Package invocation identities, Package ID and
logical ref, exact repository-relative Package root, member-03 and member-04
identities, adapter result, domain projection, the four ordered SafeFile rows,
Manifest identity and exact bytes, package-content hash,
`SELF_CONSISTENT_UNANCHORED`, and empty validation errors. It is never built or
written by local packageability. Anchor and Replay reject an index unless it
and every bound identity equal the independently descriptor-reread Package.

Process B may open only:

- metadata `attempt_identity_v01.json`, `private_inventory_v01.json`,
  `generation_gate_v01.json`, and the local safe report;
- `raw_attempt/semantic_to_contract_causal_run.json`;
- `raw_attempt/semantic_to_contract_bridge.json`;
- `raw_attempt/integrated_deterministic_airline_summary.json`;
- `raw_attempt/tri_party_airline_bsep_packet.json`;
- `raw_attempt/tri_party_airline_bsep_validation.json`;
- `raw_attempt/tri_party_airline_bsep_side_projections.json`;
- `raw_attempt/airline_transaction_artifact_ledger.json`;
- `raw_attempt/airline_crypto_artifact_seal_manifest_v01.json`;
- `raw_attempt/airline_crypto_artifact_seal_verification_v01.json`;
- whitelist-only safe geometry from `raw_attempt/summary.json`;
- `raw_attempt/secret_scan.json`; and
- `raw_attempt/airline_ticket_purchase_corridor_run_report_v01.json`.

All other inventory rows are checked only for logical name, hash, byte count,
type, mode, and completeness. Prompt, raw response, extracted candidate, and
unlisted actor artifacts are never opened, parsed, normalized, copied,
printed, or used for hydration. Reads are bounded, descriptor-bound,
non-following, regular-file-only, strict UTF-8, duplicate-key rejecting,
non-finite rejecting, and protected by parent/entry/descriptor device-inode
agreement and parent-symlink rejection.

### 8.3 Equality and Identity Chain

The gate proves:

1. original typed Corridor canonical bytes plus LF equal persisted bytes;
2. persisted SHA-256 and bytes equal the private-inventory row;
3. freshly hydrated Corridor canonical bytes plus LF equal persisted bytes;
4. hydrated typed Corridor equals original typed Corridor;
5. hydrated source-bundle Corridor equals the separately hydrated Corridor;
6. expected Ledger identity from the hydrated bundle equals stored Ledger
   identity;
7. every committed typed validator passes;
8. typed-context/member reread recreates the same six typed objects and
   adapter-result ID; and
9. member hashes, Manifest ID, and package-content hash equal an independent
   descriptor-bound disk reconstruction.

### 8.4 Exact Gate Output

Required token:

`ATTEMPT_04_LOCAL_PACKAGEABILITY_GATE=PASS`

The sanitized result contains:

- `CALLBACKS=12/12/12`;
- `COLLECTOR_CORRIDOR_LEDGER_CRYPTO=1/1/1/1`;
- `OUTBOUND_PROVIDER_NETWORK_GEMINI_EFFECTS=0/0/0/0`;
- `HYDRATE_ADAPTER_PACKAGE=1/1/1`;
- `CANONICAL_PACKAGE_INDEX_WRITES=0/0`;
- `ANCHOR_REPLAY=0/0`;
- `RESIDUE=0`;
- original/stored/hydrated Corridor SHA-256 equality;
- adapter-result ID;
- Manifest ID; and
- package-content hash.

The output contains no temporary path, credential, raw body, traceback,
exception text, object representation, or memory address.

### 8.5 Committed-Head Gate

The twelve-path implementation may be committed only after focused suites and the
first local packageability gate pass.

After that commit, the same gate runs again against a clean committed HEAD and
binds its PASS to:

- full committed HEAD;
- exact SHA-256 of all twelve implementation/test paths;
- clean tracked and untracked worktree;
- empty staging;
- exact repository root;
- canonical Attempt 04 safe report absent;
- canonical A2 Package/index/Anchor/Replay outputs absent; and
- zero repository residue.

Only this post-commit PASS can authorize one real Attempt 04.

### 8.6 Local Owner CLI and Process Contract

The owner-visible gate belongs to
`demo/run_two_domain_airline_a2_seal_v01.py` and its public function
`run_airline_a2_local_packageability_v01`, with this exact public signature:

```text
run_airline_a2_local_packageability_v01(
    *, gate_phase: Literal["precommit", "committed-head"],
    temporary_root: Path, implementation_content_sha256: str,
    verified_head: str, repository_root: Path,
) -> AirlineA2LocalPackageabilityResultV01
```

The parent accepts no preconstructed invocation object or invocation ID. It
creates the owned root, launches Process A and then fresh Process B, and
returns the result. `verified_head` is the verified base HEAD in `precommit`
and the verified clean implementation HEAD in `committed-head`.

The exact precommit owner command is:

```text
PYTHONPATH=. .venv/bin/python -m demo.run_two_domain_airline_a2_seal_v01 \
  --local-packageability \
  --gate-phase precommit \
  --repository-root <explicit-absolute-repository-root> \
  --temporary-root <new-absent-absolute-temporary-root> \
  --implementation-content-sha256 <canonical-twelve-file-digest> \
  --base-head <exact-base-head>
```

The exact committed-head owner command is:

```text
PYTHONPATH=. .venv/bin/python -m demo.run_two_domain_airline_a2_seal_v01 \
  --local-packageability \
  --gate-phase committed-head \
  --repository-root <explicit-absolute-repository-root> \
  --temporary-root <new-absent-absolute-temporary-root> \
  --implementation-content-sha256 <same-canonical-twelve-file-digest> \
  --committed-head <exact-clean-implementation-head>
```

`--base-head` is mandatory for `precommit` and forbidden for `committed-head`.
`--committed-head` is mandatory for `committed-head` and forbidden for
`precommit`. Both tokens are strict lowercase 40-character hashes and are
independently verified against the required repository state. Both phases
require the same implementation-content SHA-256. `--local-packageability` is
mutually exclusive with `--package`, `--anchor`, and `--replay`. Duplicate
options, abbreviations, environment fallbacks, implicit paths, or unknown
options fail before output. The public API and owner CLI require the explicit
absolute `repository_root`; neither may infer it from CWD or module location.

The canonical implementation-content digest is SHA-256 over the domain
separator

```text
hedgehog-os:airline-attempt-04-a2-twelve-path-content:v0.1
```

followed by one NUL byte and, for each path in the exact twelve-path order in
Section 3.2, the ASCII logical path, one NUL byte, the canonical ASCII decimal
byte count, one NUL byte, and the exact file bytes. Normatively:

```text
SHA256(
  b"hedgehog-os:airline-attempt-04-a2-twelve-path-content:v0.1\0"
  + for each ordered path:
      path_ascii
      + b"\0"
      + canonical_ascii_decimal_byte_count
      + b"\0"
      + exact_file_bytes
)
```

The precommit gate binds this digest without claiming a clean committed head.
The repeated postcommit gate requires the identical digest, the supplied exact
committed HEAD, HEAD equal to origin/main, a clean worktree, empty staging, and
zero canonical A1/A2 output paths. Only that postcommit PASS authorizes one
real Attempt 04.

PASS emits exactly two stdout lines: one sanitized canonical JSON summary and
the literal `ATTEMPT_04_LOCAL_PACKAGEABILITY_GATE=PASS`. PASS has empty stderr
and exit code `0`. FAIL emits exactly one sanitized canonical JSON line, empty
stderr, and exit code `2`. No output contains an absolute path, raw value,
traceback, exception text, object representation, memory address, credential,
prompt, response, or candidate body. No Python object, descriptor, or process
memory crosses the Process A/Process B boundary.

Source-shaped fields remain distinct from harness-observed operations. The
source-shaped fields are `wrapper_callback_observed_count`,
`provider_callback_started_count`, `provider_callback_completed_count`,
`semantic_actor_call_count`, `causal_actor_call_count`,
`generic_actor_call_count`, `duplicate_actor_call_count`,
`collector_invocation_count`, `deterministic_airline_collection_count`,
`ticket_purchase_corridor_execution_count`,
`airline_transaction_artifact_ledger_collection_count`, and
`airline_crypto_artifact_seal_collection_count`. The independent harness
fields are `outbound_provider_sdk_call_count`, `outbound_network_call_count`,
`outbound_gemini_call_count`, and `real_world_effects_count`, all zero. No
field carries both meanings, and local source-shaped 12-call geometry never
becomes executed live evidence.

## 9. Attempt 04 Owner Contract

The exact owner-terminal command is:

```text
PYTHONPATH=. .venv/bin/python -m demo.run_two_domain_airline_all_real_program_v01 \
  --real-provider \
  --attempt-number 4 \
  --private-output-directory <new-absent-absolute-attempt-04-directory> \
  --prior-accepted-attempt-03-directory <explicit-attempt-03-directory> \
  --prior-accepted-attempt-03-id <exact-attempt-03-id> \
  --transitive-failed-attempt-02-directory <explicit-attempt-02-directory> \
  --transitive-failed-attempt-02-id <exact-attempt-02-id> \
  --transitive-failed-attempt-01-directory <explicit-attempt-01-directory> \
  --transitive-failed-attempt-01-id <exact-attempt-01-id> \
  --owner-reviewed-attempt-04
```

Every listed option is mandatory for real Attempt 04. No Attempt 02 or
Attempt 03 owner flag is accepted. Owner-supplied paths and invocation
identities may not be hard-coded, inferred from directory names, discovered as
latest, selected from environment, aliased, reused, or auto-incremented.
Frozen verifier anchor constants and expected predecessor identities are
mandatory hard-coded verification anchors and are not owner-path discovery.

The new output path must be absolute, lexically canonical, absent, outside the
repository, pairwise distinct from every predecessor, and not nested with any
predecessor.

Missing, duplicated, mixed, malformed, Unicode-digit, wrong-attempt, wrong-ID,
same-path, nested-path, symlink, non-directory, moved, or replaced inputs fail
before provider construction and before output-root creation.

## 10. Exact Predecessor Anchors

Attempt 01 remains fixed by:

| Field | Exact value |
| --- | --- |
| Attempt ID | `fcce2c0224517487b59c40e79a75ea00078df393a2552f5b553780f8b7adc64a` |
| Execution head | `829496261a90249b500e7583bb407839e94cd874` |
| Attempt identity SHA-256 | `c3af7707023402b287222615e4e1877e248e1f23ad6b238254f96d7ce19f5bd2` |
| Private inventory SHA-256 | `33818a0230a245392b78194aad2c35966e59f91992170bef7461d5539e56693a` |
| Private inventory digest | `567b567ba4b37a04665cdcc085f1feb1be0fd2facad3921f5fbd5b276c5a2163` |
| Generation gate SHA-256 | `8fcdf7ef795d09178c3352999bdd3087c5e8e1b78184b6d055e29d0311991653` |
| Root/raw geometry | `4 / 23`, metadata mode `0600` |

Attempt 02 remains fixed by:

| Field | Exact value |
| --- | --- |
| Attempt ID | `0191a1820c22ccd2031e2f4f8816feebf42682eac8ba17a2b25644b27f34bf3e` |
| Execution head | `b0349bb4b90beb492a585aa998a6f167cb439279` |
| Attempt identity SHA-256 | `46cd8175bd4e3ce898c426cc85b760f096857ed68bd33359ffb754d93f2dc80b` |
| Private inventory SHA-256 | `917d034f3440605ef9a4a4f2e32a5b4a3c28ec1a715084803b9b05674e8b1029` |
| Private inventory digest | `3313317b028843d9307e350b7ded9b8ae084048b998a8eaf0819605629ceb34b` |
| Generation gate SHA-256 | `d49636630011553c4f9e5fc044699c2c493a6712c34aafeef22f2776d3ab186c` |
| Summary/validation SHA-256 | `f7f1d78708ba5a9bcc71edbb548eb5edd9815fc604f654a236493b38279d90b8` / `90ca3e2bd1d51ff74cfbc5136e55ad601f323c5a46dfbb730bea03c8d9696e01` |
| Root/raw geometry | `4 / 23`, metadata mode `0600` |

Attempt 03 remains fixed by these accepted predecessor anchors:

| Field | Exact value |
| --- | --- |
| Attempt ID | `94cb3ee73a9b5d87aca4410ce94bd5baf9a3cd720c1b08efc9b449a3816a1d43` |
| Execution head | `9eefa24f3f8bb0d3a6dbb1630c2ea5110aaed914` |
| Attempt identity SHA-256 | `af264f2a0d7b8a7a127b0f9799b913b6b11ed326075f73ac32ecd693e0e3f895` |
| Private inventory SHA-256 | `b0a47a06550e75c5740343c343ed5b4cc6cf6cc95a6e904c3e9afe26348b5964` |
| Private inventory digest | `db0acacc10967f6ed1bcc3dcd7b9de9bae8062453db028d3f5f0d76950b99f4b` |
| Generation gate SHA-256 | `ac9f64fc5d32319869a019b403a33ac95c5ea36d00a254b0152f6aa7fa2d5552` |
| Public safe report SHA-256 | `e3161701e0f691c7ded8befbb3e0e65951d1ece93438192145e1b54c061ef9fb` |
| Independent generation audit SHA-256 | `3ce11fa97c4b2f0424781f8393d58e176df877ef08de320ba1f419208be3cd7e` |

The complete verifier also independently verifies Attempt 01 and Attempt 02
and proves the accepted Attempt 03 transitive bindings to both.

## 11. Seven Predecessor Checkpoints

The complete predecessor chain is revalidated:

1. before Attempt 04 output-root creation;
2. before provider construction;
3. inside the provider wrapper immediately before callback 1 and before any
   progress, counter, metadata conversion, actor append, or base-provider call;
4. immediately after collection returns or raises;
5. immediately before public output write;
6. immediately before PASS or failure generation-gate construction; and
7. immediately before final ownership release.

Each fresh proof must equal the initial proof across path, directory, entry,
device, inode, mode, bytes, hashes, ordered inventory, digest, status, reason,
callback geometry, public report, and independent audit.

Any mutation, symlink, inode/device replacement, path alias, nesting, moved
predecessor, changed public report, changed audit, identity mismatch, or proof
uncertainty fails closed. Checkpoint 3 failure proves zero callback and base
provider activity. No predecessor file is repaired or deleted.

## 12. Attempt 04 Identity and Public Outputs

Attempt 04 creates new:

- attempt ID;
- run ID;
- report ID;
- source-task ID;
- package ID;
- logical package ref;
- output-directory ref;
- private inventory and digest;
- generation gate;
- safe execution ID; and
- independent audit identity.

The attempt ID is derived only after explicit source, predecessor, output,
execution-head, provider, model, actor-count, one-call, budget, and owner-review
bindings are complete. This preflight does not pre-hardcode the resulting ID.

Attempt 03 public evidence remains immutable at its existing paths. Attempt 04
uses distinct paths:

`docs/evidence/two_domain_all_real_sealed_evidence_program_v01/airline/airline_safe_execution_report_attempt_04_v01.json`

`docs/audit_reports/auditor_two_domain_airline_all_real_generation_attempt_04_v01.log`

No failure may overwrite, unlink, chmod, rename, truncate, or otherwise mutate
Attempt 03 evidence or another predecessor.

## 13. Live Execution Law

The frozen real-provider configuration, verified from the committed runner, is:

| Field | Exact value |
| --- | --- |
| Provider mode | `real_provider` |
| Model | `gemini-2.5-flash` |
| Application-call mode | `json_mime_no_response_schema_single_application_call` |
| Timeout | `20` seconds |
| Application calls per actor | `1` |
| Schema fallback | `0` |
| Retry | `0` |
| Successful provider/network/Gemini calls | `12 / 12 / 12` |
| Real-world effects | `0` |

Attempt 04 performs:

- exactly one collector invocation;
- exactly twelve ordered callbacks;
- at most twelve base-provider starts;
- one application-level provider call per actor;
- five causal and seven generic actors;
- one deterministic Airline collection;
- one Corridor execution;
- one Ledger collection;
- one Crypto collection;
- no schema, retry, fallback, second collector, resume, or automatic recovery;
  and
- no real-world effect.

Successful geometry is:

| Counter | Required value |
| --- | ---: |
| Wrapper callbacks | 12 |
| Provider starts | 12 |
| Provider completions | 12 |
| Provider/network/Gemini | 12 / 12 / 12 |
| Causal/generic actors | 5 / 7 |
| Collector | 1 |
| Deterministic collection | 1 |
| Corridor execution | 1 |
| Ledger collection | 1 |
| Crypto collection | 1 |
| Duplicate calls | 0 |
| Retry count | 0 |
| Fallback calls | 0 |
| Effects | 0 |

Attempt 04 is a separately owner-reviewed attempt, so `retry_count` remains
zero. Unknown, duplicate, reordered, skipped, or thirteenth actors fail before
the corresponding base-provider call.

A partial failure preserves truthful callback/start/completion prefixes and an
immutable private attempt. It publishes no Attempt 04 safe report and does not
authorize automatic Attempt 05.

## 14. Budget Reconciliation

Historical actual Airline application-level consumption is:

- Attempt 01: `3`;
- Attempt 02: `3`;
- Attempt 03: `12`; and
- Attempt 04 maximum new calls: `12`.

New cumulative ceilings are:

- Airline provider/network/Gemini: `30 / 30 / 30`;
- Supplier provider/network/Gemini: `6 / 6 / 6`; and
- programme provider/network/Gemini: `36 / 36 / 36`.

These are application-level programme counters. They do not claim independent
observability of physical SDK or HTTP retransmission.

## 15. Attempt Freeze and Audit Law

Attempt 04 freezes on every exit. A successful execution retains the immutable
execution fields `final_status=PASS`, empty `failed_stage`, and empty
`reason_code`. Before independent audit, the separate governance disposition
is `PASS_PENDING_INDEPENDENT_AUDIT`. The disposition never replaces,
rewrites, or reinterprets execution `final_status`.

Independent closure requires:

- `CLOSED_PASS`; and
- `ACCEPT_FOR_A2_AIRLINE_SEAL_WITH_BOUNDED_NON_EFFECT_SCOPE`.

Only that audited and committed Attempt 04 may become the A2 content source.
The audit must independently verify 73-file inventory geometry, complete
Corridor hydration, all twelve actors, BSEP, Roots, Corridor, Ledger, Crypto,
secret scan, generation gate, safe report, predecessor continuity, zero retry,
and zero effects.

Audit acceptance is recorded separately from the source execution and never
rewrites Attempt 04 private or public evidence.

## 16. Frozen Surfaces

The following are byte-frozen or behavior-frozen during implementation:

- actor order, prompts, and semantic contracts;
- provider adapter, canonical model, timeout law, and one-call mode;
- BSEP contracts and geometry;
- ClientRoot, AirlineRoot, BankRoot, and cross-root advisory law;
- Corridor contracts, identities, builders, validators, and execution law;
- Ledger contracts, builder, collector, validator, and 19/29/3 geometry;
- Crypto contracts, collector, nine-source manifest, and unanchored status;
- historical Airline replay;
- Kernel and Airline Kernel adapter;
- shared evidence profile;
- shared Package, Anchor, and Replay implementations;
- Supplier and all other domains;
- Attempts 01, 02, and 03;
- existing Attempt 03 public report and generation audit; and
- all prior governance and audit documents.

Only Corridor archival persistence, Attempt 04 orchestration/predecessor/public
output law, and the production A2 consumer/orchestrator are in scope.

## 17. Required Focused Test Geometry

The implementation tests must cover this complete required matrix:

- exact persisted report source-object identity;
- no second Corridor call or builder;
- complete 16/5/4/8/2 geometry;
- every nested field/type/order mutation;
- exclusive write, short/zero write, fsync, close, reread, parse, mode,
  same-inode mutation, replacement, symlink, and cleanup failures;
- exact 73-file inventory, digest, secret scan, and generation-gate binding;
- unchanged nine-source Crypto manifest;
- fresh-process hydration with no object transfer;
- equality of original, stored, and hydrated report bytes and typed values;
- all six adapter inputs, adapter result, domain projection, SafeMembers,
  Manifest, and package-content hash;
- exact Process-A result schema, identity, canonical bytes, descriptor reread,
  `safe-report-v01.json` literal, file/hash cross-checks, and forbidden-field
  rejection;
- exact mode-derived official and local limitation tuples and rejection of a
  caller-supplied `limitation_refs` value;
- exact official-only Package-index schema, zero-slot identity, APIs,
  four-row binding, disk reread, local-mode rejection, and ownership-safe
  cleanup;
- `LOCAL_NONPUBLICATION`, noneligibility, no canonical writes, and zero
  residue;
- exact Attempt 1/2/3/4 branch and CLI matrix;
- every predecessor mutation at all seven checkpoints;
- Attempt 04 new identities and distinct public paths;
- partial failure preservation and no Attempt 05;
- exact budgets `3 + 3 + 12 + 12 = 30`, Supplier `6`, programme `36`;
- zero authority, permission, action, payment, booking, ticket, publication,
  Package-owner, Anchor-owner, Replay-owner, and effect operations during local
  validation; and
- static zero-network/provider/Gemini sentinels for every simulated-real test.

No skip, xfail, forced success, schema relaxation, retry, or external test-time
patch may replace production behavior.

## 18. Commit and Status Boundaries

### G1: Governance

Commit only AGENTS, the source-agnostic A2 preflight, and this Attempt 04
preflight.

### I1: Implementation

Implement and test exactly the twelve authorized paths. Run focused suites and the
local packageability gate. Perform no real provider/network/Gemini operation
and create no repository evidence. Commit implementation only after PASS.

### L1: Clean-Head Local Gate

Repeat local packageability on the clean committed implementation HEAD. Create
no repository output. Only this PASS can authorize live execution.

### E1: One Owner-Terminal Attempt 04

Perform exactly one owner-reviewed real attempt. No automatic repeat. A source
execution retains `final_status=PASS`, empty `failed_stage`, and empty
`reason_code`; its separate governance disposition is
`PASS_PENDING_INDEPENDENT_AUDIT`.

### E2: Independent Attempt 04 Audit

Require `CLOSED_PASS` and
`ACCEPT_FOR_A2_AIRLINE_SEAL_WITH_BOUNDED_NON_EFFECT_SCOPE`. Commit only the
distinct Attempt 04 safe report, distinct audit, and AGENTS closure update.

### G2: A2 Accepted-Source Freeze

Update the same A2 preflight with exact accepted Attempt 04 identities and
hashes and move official A2 to `READY_FOR_REVIEW`.

### P1: Package and Anchor Publication

Package writes its owned official Package and index into the clean G2 worktree,
closes and descriptor-rereads every byte, and freezes those bytes within the P1
operation without a Git commit. Anchor reads those exact frozen worktree bytes
and writes `EVIDENCE_ONLY`. An independent Anchor audit verifies Package,
index, and Anchor. P1 then commits official Package, package index, Anchor, and
independent Anchor audit together. No Package-only commit boundary exists.

### P2: Replay Closure

Commit read-only verification, Replay, Replay audit, Human Story, and
checkpoint closure.

No boundary may be combined, amended around a failed gate, or rewritten after
publication.

## 19. Nonclaims and Fail-Closed Boundary

This preflight authorizes no live call. It creates no Package, Anchor, Replay,
authority, permission, action, payment, booking, ticket issuance, publication
authority, Root Attestation, signer identity, PKI claim, external timestamp, or
real-world effect.

Every guard, predecessor, path, source, type, schema, identity, inventory,
secret, byte, mode, hash, validator, ownership, cleanup, counter, or repository
state mismatch fails closed. Previously frozen evidence is never changed or
deleted.

## 20. Immediate Next Gate

The only next owner-reviewed repository gate is:

`two_domain_all_real_sealed_evidence_program_v01_a1_attempt_04_complete_corridor_capture_implementation`

No Gemini call is authorized until I1 is committed and L1 passes on that clean
committed HEAD.
