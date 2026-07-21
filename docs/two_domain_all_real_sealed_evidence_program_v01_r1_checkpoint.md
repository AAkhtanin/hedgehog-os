# Hedgehog OS Two-Domain All-Real Sealed Evidence Program v0.1
## R1 Shared Sealed-Evidence Profile Checkpoint

document_id: two_domain_all_real_sealed_evidence_program_v01_r1_checkpoint

document_status: CHECKPOINT

checkpoint_status: CLOSED_PASS

gate_id: two_domain_all_real_sealed_evidence_program_v01_r1_shared_profile

audit_disposition: ACCEPT_WITH_EXPLICIT_SCOPE_RECONCILIATION

programme_id: two_domain_all_real_sealed_evidence_program_v01

programme_version: v0.1

closure_base_head: 4274a0a994b8f236abba3c4211cb8b89e0431556

r1_runner_implementation_commit: 4274a0a994b8f236abba3c4211cb8b89e0431556

provider_called_during_audit: false

network_called_during_audit: false

gemini_called_during_audit: false

live_collection_performed_during_audit: false

official_package_created_during_audit: false

external_anchor_published_during_audit: false

official_replay_performed_during_audit: false

real_world_effects_count: 0

full_repository_pytest: NOT_RUN

original_gate1_status: CLOSED_PASS

next_repository_gate: two_domain_all_real_sealed_evidence_program_v01_a1_airline_live

## 1. Closure Verdict

- R1 Shared Sealed-Evidence Profile: `CLOSED_PASS`.
- Audit disposition: `ACCEPT_WITH_EXPLICIT_SCOPE_RECONCILIATION`.
- Shared contracts, domain adapters, and deterministic filesystem runners pass
  their exact focused validation and short compatibility surfaces.
- The Airline and Supplier / Water Filter disposable Package fixtures both
  return `SELF_CONSISTENT_UNANCHORED` from explicit absolute paths.
- Provider, network, Gemini, and real-world-effect execution during this audit:
  `0 / 0 / 0 / 0`.
- Full repository pytest was intentionally `NOT RUN` under the bounded R1 gate.
- No official Package, external Anchor publication, official Replay, live
  collection, or production operation was performed.

The earlier audit HOLD is superseded. Its wrapper resolved the
`.venv/bin/python` launcher to the Homebrew base interpreter, bypassing the
virtual environment and failing import before the Package runner executed.
The preserved diagnostic showed no Package output. Direct invocation through
the actual absolute `.venv/bin/python` launcher passed for both domains and
left no disposable residue. This was an audit-invocation error, not evidence of
an implementation defect.

## 2. Commit Lineage

R1 begins from the separately closed Gate-1 checkpoint at `339c4ad`.

1. `b1096c2` - consolidated Two-Domain All-Real Sealed Evidence Program v0.1
   preflight.
2. `577f390` - Airline Kernel source-lineage compatibility replacement
   preflight.
3. `ff62863` - shared sealed-evidence contract spine.
4. `e64b4c1` - Airline sealed-evidence adapter compatibility and the reviewed
   source-lineage repair.
5. `7bc7b8f` - Supplier / Water Filter sealed-evidence adapter compatibility.
6. `4274a0a` - deterministic Package, Anchor, and Replay filesystem runners.

Every listed commit and the Gate-1 checkpoint are ancestors of the closure
head.

## 3. Audited R1 Implementation Inventory

| Path | SHA-256 | Bytes |
| --- | --- | ---: |
| `hedgehog/evidence/__init__.py` | `2fa905efbd7f2a968d8a648ef14ef676a4f64bac94a159651c7a4d7b71a81b8b` | 3830 |
| `hedgehog/evidence/external_anchor_v01.py` | `299c6d2daabfe53c0c93c76a46709d09c4cc26b89907af17a30dab8ce8537994` | 35826 |
| `hedgehog/evidence/sealed_evidence_profile_v01.py` | `3845a246e641aea8da3d9314e2d140bcb701a5488cb9de8153a62f0d84529b37` | 54293 |
| `hedgehog/evidence/sealed_package_v01.py` | `4fecf1b24696316348256acd1bd5a9e7a237dc37bd5b11abc41a71257796af53` | 30908 |
| `hedgehog/evidence/sealed_replay_evidence_v01.py` | `f40e48f3d32f4b67250534f5d47d5bb4e076890497506ec4315d9ce06261c5a3` | 38035 |
| `hedgehog/domains/airline/sealed_evidence_package_adapter_v01.py` | `420c6ba24d1a9417eb67295e402e395b05c88fbf55703d63948507c41a6f031e` | 71346 |
| `hedgehog/domains/supplier_water_filter/live_evidence_adapter_v01.py` | `b1efafd5b5dbce27ae96c853ca970fecd383b6470511180e71f478d094a670ff` | 25071 |
| `hedgehog/domains/supplier_water_filter/sealed_evidence_package_adapter_v01.py` | `1eeb20bfd41de4650d04e2f2ab355db0c2b390c4f019b654cb4aab3dff563517` | 48495 |
| `demo/run_sealed_evidence_package_v01.py` | `e2216346d0204fdea562df5fc88d675a4d5cf037d4cca5d45e45ce61a87b5118` | 47006 |
| `demo/run_sealed_evidence_anchor_v01.py` | `19e53c2e45fef9b116289328da27801727a2ea1e82cc128bb5fcc611c6b171b4` | 39980 |
| `demo/run_sealed_evidence_replay_v01.py` | `11fb3029cde2da768a3270c77c580a1d29dd8dc32de9f6558be7df265f0f4fc1` | 48804 |

## 4. Frozen Surfaces and Gate-1 Reconciliation

The following paths are byte-equal to the closed Gate-1 checkpoint at
`339c4ad`:

| Frozen path | SHA-256 | Bytes |
| --- | --- | ---: |
| `hedgehog/kernel/integrity_replay_v01.py` | `d496354e7dbca5ff9c96943fe0d4bf777e85a88b404b67c7dfcfda116ee8d0be` | 48487 |
| `hedgehog/kernel/abi_v01.py` | `b09bcbe7d87e12670cbbe58994578995d262ad9d1dc50d0b3870543515db0b59` | 38600 |
| `hedgehog/kernel/root_signer_isolation_v01.py` | `3f4efab32cd972803e61b0877c56d46eead9907611e1a1534b8cf924ba8c22f8` | 31043 |
| `hedgehog/kernel/multiroot_v01.py` | `e29137031417927e98c86b808e8e3897987a32ff953bbd6adcd6b4a7367e03ff` | 52804 |
| `hedgehog/kernel/effect_firewall_v01.py` | `5be3bc2a3b99ea0d4daeadb0646438902962342eba0dbe0d6c5b07f0dea627e7` | 63944 |
| `hedgehog/kernel/conformance_v01.py` | `544e00558597474592b21d78a3dc24f2705b8d3915c0c3d5ea94d7d7974000d1` | 42691 |
| `hedgehog/domains/supplier_water_filter/kernel_adapter_v01.py` | `433888ec19c6632ac7abd9f9f64cd350ca95b3dc8c94035e7804e49beb816fac` | 62262 |
| `release/completion_manifest.json` | `02ffac0d78df768f91df0bb06bdd15ec463dbe5ccea6ef82b7022146819f3466` | 26256 |
| `release/integration_seam_index.json` | `c29c2ff873c8b448d8825c3288918e980eab3d65a5114762d2e3fbe5b1206231` | 15150 |

No collector changed through the R1 lineage. The Airline Kernel adapter is the
single reviewed frozen-surface reopening. The replacement preflight at
`577f390` authorized the narrow source-lineage compatibility repair committed
at `e64b4c1`. The closure bytes remain unchanged from `e64b4c1`:

- `hedgehog/domains/airline/kernel_adapter_v01.py`:
  `deebc60e3c0b7840ac58eab7e448ebae328e749239fde6e5503c571bae187dd5`,
  41886 bytes.
- `tests/test_airline_kernel_adapter_v01.py`:
  `7a19112457a26b5859efd0c84e54c42315fbc9c0bc9a6274fbf2cce605f3eabf`,
  44117 bytes.

The repair derives one expected source identity internally and supplies it to
both Ledger validation and Crypto Ledger-entry projection. It changes no
public signature or result geometry. The original Gate-1 frozen fixture path
remains `CLOSED_PASS`.

## 5. Fresh Validation Evidence

Compilation covered the five shared modules, three domain adapters, three
runners, and seven focused R1 test files: `PASS`.

Focused pytest results:

| Focused surface | Result |
| --- | ---: |
| Shared sealed-evidence profile | 910 PASS |
| Airline sealed-evidence package adapter | 330 PASS |
| Supplier live-evidence adapter | 399 PASS |
| Supplier sealed-evidence package adapter | 209 PASS |
| Package, Anchor, and Replay runners combined | 317 PASS |

- Exact seven-file collect-only result: `2165 collected`.
- Kernel Integrity Replay and ABI short compatibility: `668 PASS`.
- Failed: `0`.
- Skipped: `0`.
- Xfailed: `0`.
- Full repository pytest: `NOT RUN`.

The exact focused files were:

```text
tests/test_sealed_evidence_profile_v01.py
tests/test_airline_sealed_evidence_package_adapter_v01.py
tests/test_supplier_water_filter_live_evidence_adapter_v01.py
tests/test_supplier_water_filter_sealed_evidence_package_adapter_v01.py
tests/test_sealed_evidence_package_v01_runner.py
tests/test_sealed_evidence_anchor_v01_runner.py
tests/test_sealed_evidence_replay_v01_runner.py
```

The short compatibility command contained only:

```text
tests/test_kernel_integrity_replay_v01.py
tests/test_kernel_abi_v01.py
```

## 6. Standalone Disposable Package Evidence

Both commands used:

- interpreter: the repository `.venv/bin/python` launcher, invoked by its
  absolute path without resolving its virtual-environment symlink;
- working directory: the repository root;
- execution head:
  `4274a0a994b8f236abba3c4211cb8b89e0431556`;
- one fresh absolute invocation-owned parent beneath `/private/tmp`;
- an absent Package output child;
- no provider, network, Gemini, live, publication, or effect operation.

Airline:

- exit code: `0`;
- stdout: exactly one canonical JSON line;
- stderr: empty;
- fixture disposable: `true`;
- Package status: `SELF_CONSISTENT_UNANCHORED`;
- Manifest ID:
  `bbd0b2d1696260486184cc9b3d73fd974ab68a05a6599b8f7cdc13dd6953f2c0`;
- Package content hash:
  `51c2f50573ce5f3a9e86cd523cfcb85170fcc68dced60493a2a521452ba6696d`;
- exact files:
  `evidence/01-airline_fixture_kernel_integrity.json` and
  `sealed_package_manifest_v01.json`;
- provider/network/Gemini/effect counts: `0 / 0 / 0 / 0`.

Supplier / Water Filter:

- exit code: `0`;
- stdout: exactly one canonical JSON line;
- stderr: empty;
- fixture disposable: `true`;
- Package status: `SELF_CONSISTENT_UNANCHORED`;
- Manifest ID:
  `d76f447b8a514352c8bf59097685c646b25778f3a8a35375b913d2dcdfd07540`;
- Package content hash:
  `3262b4601b3230a2110dced44f55d9348db06c9974d5958aecfbef979e80171a`;
- exact files:
  `evidence/01-supplier_water_filter_fixture_kernel_integrity.json` and
  `sealed_package_manifest_v01.json`;
- provider/network/Gemini/effect counts: `0 / 0 / 0 / 0`.

Both invocation-owned roots were removed and absence was proved. These are
disposable fixtures, not official domain Packages.

## 7. Shared Contract and Domain Boundary Findings

- Shared `hedgehog/evidence` contracts are deterministic, domain-neutral, pure
  in-memory contracts. They contain no domain business law, filesystem
  execution, provider client, network operation, Gemini call, authority or
  permission creation, or business effect.
- Airline and Supplier law remains in the exact domain adapters.
- The adapters validate explicit typed source contexts, call no provider, and
  perform no filesystem publication.
- The Airline adapter preserves its 12-call source evidence geometry. The
  Supplier adapter preserves its six-call source evidence geometry. Those
  counters are encoded evidence data; this audit performed no provider call.
- Input contracts remain unchanged by adapters and runners. Public summaries
  are immutable until copied to the CLI serialization boundary.
- `DomainEvidenceProjectionV01` remains an explicit typed input. R1 does not
  claim that an arbitrary Package alone reconstructs the original domain
  projection or business semantics.

## 8. Package, Anchor, and Replay Status Geometry

- Package closure is `SELF_CONSISTENT_UNANCHORED` only.
- Anchor creation records `EVIDENCE_ONLY` publication evidence.
- Anchor publication does not claim `ANCHORED_PASS`; external Anchor supplied,
  external Anchor verified, and anchored PASS claimed are all false at
  publication.
- A fresh verification supplied with the exact matching Anchor identity may
  derive `ANCHORED_PASS`.
- Matching sealed Replay derives `PASS` with integrity, continuity, and Anchor
  verification true.
- A well-formed but mismatched supplied Anchor identity produces coherent
  verification and Replay `FAIL_CLOSED` evidence.
- Replay rereads sealed member bytes and independently rebuilds SafeFile
  records and the Manifest. It does not rerun semantics, Root decisions,
  Corridor logic, providers, or effects.
- Signature verification, signer identity verification, and Root Attestation
  remain false.
- All Package/Anchor/Replay external, rerun, authority, permission, action,
  receipt, FinalOutput, and real-world-effect counters remain exact zero.

## 9. Filesystem and Scanner Evidence

- Filesystem calls require explicit absolute owner-supplied paths and absent
  outputs.
- Inventories are exact and Manifest-driven. No glob, rglob, latest-file
  selection, recursive package discovery, or implicit path fallback exists.
- Descriptor-based reads bind bytes to regular-file device/inode identity.
- Pinned directory descriptors, no-follow opens, directory identity checks,
  exact inventories, and final rereads enforce the implemented R1 boundary.
- Unexpected files/directories, non-regular members, symlinks, ancestor or
  descriptor/path replacement, byte/identity mutation, malformed canonical
  JSON, partial writes, silent close, no-op deletion, and cleanup proof failure
  fail closed at all agreed test-injectable checkpoints.
- Failure CLIs emit one sanitized canonical JSON line on stdout with empty
  stderr and no traceback, supplied argv, owner path, object representation,
  memory address, or arbitrary exception text.
- The schema-bound scanner accepts the five exact safe negative attestations,
  safe Airline/Supplier metadata, public authorization references/statuses,
  harmless token counters, and multilingual values.
- It rejects credentials, keys, private material, raw prompts/responses,
  sensitive assignments, inverted attestations, unsafe normalized key
  variants, NUL, CR, BOM, traceback material, owner paths, and noncanonical
  JSON.

Committed AST/import-boundary checks and strict UTF-8, NUL, CR,
trailing-whitespace, and terminal-LF checks all pass.

## 10. Explicit Scope Reconciliation

Audit disposition is `ACCEPT_WITH_EXPLICIT_SCOPE_RECONCILIATION` with these
accepted R1 limits:

1. Portable Python/POSIX R1 fixture runners do not claim an atomic guarantee
   that unlink/rmdir removes only a previously observed inode against a
   hostile same-UID concurrent namespace replacement occurring strictly
   between the final dirfd-relative identity check and the destructive
   syscall.
2. More generally, the disposable R1 fixture filesystem is not claimed to be
   a transactional filesystem against hostile same-UID mutation strictly
   after the final committed reads.
3. The safe-metadata scanner is schema-bound: keys are constrained and known
   credential/raw/private patterns are rejected, while multilingual values
   remain allowed. It is not claimed to be a universal Unicode-confusable DLP
   engine for arbitrary free text.

Static symlink escape, ancestor replacement, descriptor/path replacement,
pre-delete identity replacement, no-op deletion, same-inode mutation at
implemented checkpoints, and all agreed test-injectable boundaries remain
fail closed.

These limitations are accepted because R1 is a deterministic disposable
fixture-runner profile, not an official package/publication profile or hostile
multi-tenant production filesystem. The final namespace race is not claimed
solved. Production or multi-tenant use requires isolated owned storage and/or
platform-specific hardening.

## 11. Zero-Operation Audit Boundary

- Provider operations: `0`.
- Network operations: `0`.
- Gemini operations: `0`.
- Real-world effects: `0`.
- Live collections: `0`.
- Official Packages: `0`.
- External Anchor publications: `0`.
- Official Replays: `0`.

The encoded Airline 12-call and Supplier six-call counters are source evidence
geometry. They are not calls performed during this audit.

## 12. Authority and Material Non-Claims

- No authority or permission was created.
- No action, receipt, or FinalOutput was created.
- No real ticket, booking, payment, shipment release, bank action, GDS action,
  supplier action, warehouse action, or other real-world effect occurred.
- Not production.
- Not production certification.
- Not arbitrary-domain certification.
- Not production PKI, signer authentication, non-repudiation, trusted
  timestamping, or Root Attestation.
- Hashes establish declared integrity and continuity, not semantic truth.
- Fixture `ANCHORED_PASS` and Replay `PASS` do not close either official domain
  execution.
- No official Package, external Anchor publication, official Replay, public
  Evidence Book, or production distribution package was created.

## 13. Original Gate 1 and Next Gate

The Domain-Neutral Reference Kernel Gate 1 remains `CLOSED_PASS` for its frozen
fixture contract. R1 preserves Root authority, technical/business outcome
separation, and the zero-real-effect boundary. The reviewed Airline contextual
source-lineage extension does not rewrite or invalidate the original Gate-1
evidence.

The next repository gate is:

`two_domain_all_real_sealed_evidence_program_v01_a1_airline_live`

R1 performs no A1 live collection. A1 requires its own reviewed execution,
attempt preservation, generation audit, and provider budget boundary.
