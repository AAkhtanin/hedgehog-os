# G43 Read-Only Release Dependency Matrix

Status: PLAN_ONLY_NOT_APPLIED. Source inventory is final_source_ledger.json in
this return; every future registration must use those exact reviewed identities
or independently review a subsequent change. No admission context is created.

| Current predicate | Necessary later coordinated change | Preserved invariant / disposable check |
|---|---|---|
| tools/reviewed_repository_transition_v01.py:341 `_metadata_and_registration`, PROTECTED_PINS | Independent review of the exact Work/G3 and registration pin lineage; update only authorized registry pins | Work and G3 fixture bytes unchanged; mutation of either must still refuse |
| Same function:349 METADATA_PATHS exact base JSON plus historical keys, `METADATA_COHERENCE`, `HISTORICAL_METADATA`, `G37_CURRENT_REGISTRATION` | Three authority metadata documents need a coordinated historical/current successor | Preserve every old record with its original basis; changed historical claims must refuse |
| Same file:406 `_kind_rules` PREVIOUS_TRANSITION_BINDING; line410 POLICY_MAINTENANCE_REQUIRED | Trusted old-policy-to-new-policy review/installation outside ordinary ENGINEERING | Ordinary transitions retain same-policy and independently installed context; a new policy cannot admit itself |
| demo/run_living_gauntlet_v01.py:1143 `_validate_completion_manifest_v01`, exact `_MANIFEST_FIELD_NAMES`, G36 profile match | Add one exact versioned G4 record and teach actual current consumers; retain historical checker/profile | Unknown keys still refuse; no unchecked dropping of fields |
| Same file:1430 `_validate_integration_seam_index_v01`, exact `_SEAM_INDEX_FIELD_NAMES`, seam IDs/profile | Add exact G4 inventory and current producer/supplied/direct-test relationships | Exclusive Firewall effect owner and historical seam geometry unchanged |
| tests/test_repository_release_spine_v01.py:4845 registry comparison to Testflix basis plus G37 block | Explicit versioned current-versus-historical assertion path | Historical expected JSON continues validating its own frozen bytes; no early return around authority |
| Same file:5016 `test_g37_current_registration_pins_actual_release_files_v01` | Stop conflating old G37 pins with later current registry bodies via a reviewed successor assertion | G37 pins/records remain genuine history, not relabelled current bytes |
| Release-spine import binder:1124+ and authority guard enforcement | Separately reviewed binder/policy lineage compatible with new current registries | No import bypass, fabricated context, sidecar architecture or invented MAINTENANCE kind |

Current pins (unchanged):

```text
release/completion_manifest.json a5500c8763edb31b3edf01353e461295754af4651afa7792f642b172d6ca0bd0
release/integration_seam_index.json 0db7692fd5d22d206afe3750c9940807b2e3b6947cd4d4b7dafa0afd98b3bb7d
release/current_schema_surface_v01.json 7094cc2438599ce3ae450acca4876e177df736893caf9ffba1ebcaf8480cf451
```

The three exact authority metadata paths are
`specs/document_authority_index_v01.json`,
`release/successor_context_manifest_v01.json`, and
`release/current_status_overlay_v01.json` (R1 METADATA_PATHS, lines35-39).
Their historical records and the owner FINALIZED context remain unchanged.

The later registry postimages must name:
- producer: gate4_reference_adapter_v01.native_story_v42;
- independent supplied consumer: gate4_reference_evidence_v01.verify_package_v01;
- direct tests: native/history/evidence, unchanged pure maths and preflight;
- exact schema writer: gate4_reference_contracts_v01.reference_schema_v01;
- supported saved relation scope and UNSUPPORTED_NATIVE_SCHEMA limitation;
- one native collection owner, not a second effect owner or authority source.

## Cost and Ownership

Do not run legacy E5/D/E/Living/Conformance in G43. Their historical costs are
tens of minutes, not a reason to recollect them at every documentation update.
A later independently invoked top-level release entry owns the fresh collections
required by its reviewed contract exactly once. Sharing a supplied checked return
must add zero collection calls. G4 native preparation runs once per release story;
G4 replay is pure saved-input validation in separate processes and never starts
that producer. Direct G43 PASS is not release registration or policy admission.
Retained E5/G3 reuse needs an explicit source-impact bridge AND contract permission;
neither filename equality nor a sidecar PASS is sufficient.

Disposable transition checks for the later reviewed successor: complete exact
dirty and staged proposals, partial/foreign staging refusal, changed protected
runtime refusal, wrong independent context/policy refusal, exact sole-parent Git
child and remote readback only after separately authorized owner landing. G43
performs none of those owner mutations. R1 currently offers BOOTSTRAP,
DOCUMENTATION and ENGINEERING only.

First remaining release obligation: independent bounded policy/registry/consumer
succession review with a trusted installation route. Then separately authorized
integration verification and owner landing. No Gate4 closure is self-awarded.
