# Hedgehog OS Two-Domain All-Real Sealed Evidence Program v0.1
## A1 Attempt 02 Semantic/Runtime Recovery Preflight

document_id: two_domain_all_real_sealed_evidence_program_v01_a1_attempt_02_semantic_runtime_recovery_preflight

document_status: PREFLIGHT

preflight_status: READY_FOR_REVIEW

gate_id: two_domain_all_real_sealed_evidence_program_v01_a1_attempt_02_semantic_runtime_recovery

programme_id: two_domain_all_real_sealed_evidence_program_v01

programme_version: v0.1

audit_disposition: ACCEPT_WITH_EXPLICIT_SCOPE_RECONCILIATION

canonical_implementation_baseline: 829496261a90249b500e7583bb407839e94cd874

intended_parent_of_corrected_governance_commit: 829496261a90249b500e7583bb407839e94cd874

rejected_draft_status: REJECTED_BEFORE_IMPLEMENTATION

rejected_draft_canonical_authority: NONE

rejected_draft_implementation_authority: NONE

planning_only: true

production_code_modified: false

tests_modified: false

provider_called_during_preflight: false

network_called_during_preflight: false

gemini_called_during_preflight: false

live_runner_called_during_preflight: false

package_called_during_preflight: false

anchor_called_during_preflight: false

replay_called_during_preflight: false

real_world_effects_count: 0

immediate_next_gate: two_domain_all_real_sealed_evidence_program_v01_a1_attempt_02_semantic_runtime_recovery

## 1. Executive Verdict

`READY_FOR_REVIEW` for one additive Airline semantic-provider canonicalization
boundary and its Attempt 02 integration.

A full-causal-schema draft was rejected before implementation. It has no
canonical authority and no implementation authority. The correct recovery is
a domain-local semantic/runtime ownership boundary, not a full provider-owned
canonical schema and not a new provider transport.

Attempt 01 remains immutable private `FAIL_CLOSED` negative evidence. It can
never be repaired, resumed, overwritten, reused as raw input, or promoted to
PASS. Attempt 02 is not implemented or executed by this preflight.

## 2. Canonical Baseline and Review Basis

The canonical implementation baseline and intended parent of the corrected
governance commit are both:

`829496261a90249b500e7583bb407839e94cd874`

The read-only design review covered:

- `AGENTS.md` and the controlling provider-contract and roadmap language;
- the consolidated programme preflight and R1 checkpoint;
- `docs/provider_contract_modes_v01.md`;
- `demo/run_tri_party_airline_live_semantic_lane_v01.py`;
- `demo/run_two_domain_airline_all_real_program_v01.py`;
- `hedgehog/domains/airline/semantic_to_contract_binding_v01.py`;
- `hedgehog/domains/airline/semantic_to_contract_causal_runtime_v01.py`;
- their focused tests;
- the shared Gemini helper used by the Airline live provider.

No private absolute path, credential, prompt, response, extracted candidate,
or raw evidence value is retained in this document.

## 3. Architectural Root Cause

Attempt 01 did not prove that Gemini needs a full canonical response schema.
It proved that runtime-owned mechanical lineage must not be reproduced by
Gemini.

The causal provider surface asked the provider to return the complete internal
proposal or reviewer mapping. That surface included mechanical transaction,
request, actor, BSEP, candidate-snapshot, digest, validation, safety,
authority, and effect fields. Attempt 01 reached the third actor and failed
closed because one provider-reproduced snapshot digest differed while the
candidate-set reference and snapshot ID matched.

The validator behaved correctly. The ownership boundary was incorrect:
semantic provider output should not copy trusted runtime lineage. Moving the
same full internal object into a strict provider schema would preserve that
error and move the canonical contract toward provider ownership.

## 4. Governing Provider Law

The controlling law is:

```text
Provider proposes semantics.
Runtime canonicalizes.
Validators verify.
Root decides.
```

`semantic_json_mode` remains the preferred rich-reasoning route. A bounded
provider schema may be an optional interface aid in another reviewed design,
but a provider canonical schema is not the current or future default for this
programme.

Provider formatting is not authority. JSON MIME is not authority. Runtime
canonicalization does not make provider output true. Existing local validators
remain the acceptance boundary, and Root remains final authority.

## 5. Existing Single-Call JSON-MIME Transport

The committed shared Gemini helper already provides the required no-schema
behavior:

- its generation config uses `response_mime_type: application/json`;
- when `response_schema` is absent, its schema-key sequence contains exactly
  one no-schema entry;
- that branch invokes `generate_content` exactly once;
- a formatting or provider error in that no-schema call is raised and does not
  enter another schema or no-schema attempt;
- the multi-key schema compatibility sequence is reached only when a response
  schema is supplied.

Therefore transport duplication is unnecessary and unauthorized. Attempt 02
must use the committed helper's existing JSON-MIME/no-schema branch for all
twelve actors. No new A1-local Google client, SDK wrapper, credential loader,
timeout transport, or `generate_content` implementation may be added.

## 6. Explicitly Rejected Design

The following are forbidden for Attempt 02:

- a full causal `response_json_schema`;
- the complete proposal dataclass as provider schema;
- the complete reviewer dataclass as provider schema;
- singleton mechanical enums for digest, snapshot ID, transaction ID, actor
  ID, request ID, references, safety fields, authority fields, or effect
  fields;
- provider-owned canonical causal objects;
- copying runtime-owned causal lineage, causal canonical fields, or causal
  safety/effect geometry through Gemini;
- a duplicated A1-local Google provider implementation;
- retries, schema fallback, no-schema fallback after an error, a second
  collector invocation, or automatic Attempt 03;
- mutation, canonical repair, identifier replacement, or post-hoc overwrite
  of raw provider output.

The rejected full-causal-schema draft has no canonical or implementation
authority.

## 7. Causal Proposer Semantic Envelope

The causal proposer provider-owned envelope may contain only:

1. `recommended_offer_id`;
2. `ranked_offer_ids`, if retained as genuine semantic ranking;
3. `decision_factors`;
4. `preference_matches`;
5. `uncertainty_notes`;
6. `requires_root_review`;
7. `semantic_summary`.

The future boundary must define exact required and optional fields, exact
primitive and collection types, bounded lengths, canonical JSON safety, and
stable fail-closed reasons. Unknown fields are rejected. A recommendation and
ranking are semantic proposals only and do not select or authorize an offer.

## 8. Causal Reviewer Semantic Envelope

Each causal reviewer provider-owned envelope may contain only:

1. `supports_proposed_offer`;
2. `semantic_factors`;
3. `blocking_conflicts`;
4. `uncertainty_notes`, if retained by the provider-boundary contract.

Unknown fields are rejected. Reviewer support remains advisory. A reviewer
cannot create validation status, authority, permission, action, or a Root
decision.

## 9. Causal Provider-Forbidden Mechanical Fields

The five causal provider semantic envelopes must not own or return:

- transaction, actor, role, request, proposal, response, or selection IDs;
- candidate-set references;
- BSEP IDs or references;
- snapshot IDs or digests;
- validation, review, collection, or final status;
- source lineage or artifact references;
- authority, permission, action, packet, receipt, payment, ticket, booking,
  or FinalOutput flags;
- real-world-effect counters;
- the complete internal proposal or reviewer dataclass surface.

A causal semantic envelope containing any mechanical field fails closed before
a canonical artifact is built. Runtime must not silently discard a forbidden
causal field and continue.

## 10. Additive Domain-Local Canonicalization Boundary

A new domain-local module must implement the semantic-to-canonical boundary
for the five causal actors. It must:

1. strictly parse and validate the exact provider semantic envelope;
2. reject unknown, mechanical, raw, private, authority, action, and effect
   fields;
3. validate the proposed recommendation against the owner-built visible,
   Airline-valid, and ClientRoot hard-compatible candidate sets;
4. bind accepted semantics to the owner-built causal request, BSEP projection,
   selection input, candidate snapshot, and snapshot digest;
5. derive every ID, reference, lineage field, false safety/authority flag,
   validation state, and zero-effect value from trusted runtime context;
6. construct the existing full canonical v0.1 proposer or reviewer mapping;
7. pass that mapping to the unchanged existing builders and validators;
8. return stable fail-closed evidence if either semantic validation or the
   existing canonical validation fails.

Read-only inspection found an honest additive route. The frozen binding
already exposes the canonical proposal payload builder and validator. The
frozen causal runtime already validates canonical reviewer responses and the
complete causal chain against owner-built selection context. The new boundary
can construct those existing mappings from validated semantics plus trusted
runtime context without changing their contracts.

If implementation proves that this additive module cannot construct and
validate the existing mappings honestly, work must stop for owner review. No
scope widening or frozen-contract edit is authorized by this preflight.

## 11. Provenance and Evidence Separation

The raw provider response remains unchanged. Canonicalization creates a new,
separately identified runtime artifact; it never mutates the raw response or
claims that the provider returned canonical lineage.

Each causal actor must retain separately labelled evidence for:

1. raw provider response in private evidence only;
2. extracted provider semantic object;
3. runtime canonical artifact;
4. semantic-envelope validation result;
5. existing canonical validation result;
6. field-ownership provenance.

Field-ownership provenance must expose explicit, disjoint
`provider_field_names` and `runtime_field_names`. Their intersection must be
empty. Runtime names must cover every canonical field not permitted in the
semantic envelope. Public safe evidence may include only safe hashes,
identities, field-name sets, status, reasons, and zero-effect counters; it may
not include private raw bodies.

## 12. Twelve-Actor Provider Configuration

All twelve live actors must use JSON MIME with no response schema.

- The five causal actors pass through the new typed semantic-to-canonical
  boundary before the frozen causal runtime accepts their canonical mappings.
- The seven generic actors retain their existing JSON-MIME semantic behavior
  and local validation.
- The seven generic actor envelope is outside this narrowly bounded causal
  remediation and is not declared a universal future provider contract by
  this preflight.
- No actor uses a full provider canonical schema.
- No provider or parsing error may trigger another application call.
- Exactly one application-level provider call is permitted per actor.

This rule concerns application-level calls. It does not claim observability of
physical SDK or transport retransmission below the committed provider helper.

## 13. Exact Future Implementation Scope

The next implementation pass may change exactly six paths.

Create:

1. `hedgehog/domains/airline/semantic_provider_canonicalization_v01.py`;
2. `tests/test_airline_semantic_provider_canonicalization_v01.py`.

Modify:

3. `demo/run_tri_party_airline_live_semantic_lane_v01.py`;
4. `tests/test_tri_party_airline_live_semantic_lane_v01_runner.py`;
5. `demo/run_two_domain_airline_all_real_program_v01.py`;
6. `tests/test_two_domain_airline_all_real_program_v01_runner.py`.

No seventh implementation path is authorized. The implementation pass must
not execute a real provider or owner-terminal attempt.

## 14. Frozen Surfaces

The following remain byte-frozen:

- `hedgehog/domains/airline/semantic_to_contract_binding_v01.py`;
- `hedgehog/domains/airline/semantic_to_contract_causal_runtime_v01.py`;
- their focused tests;
- the shared Gemini/provider helper;
- Kernel and Root law;
- Corridor, Ledger, and Crypto;
- Airline and shared evidence adapters;
- all shared R1 evidence contracts;
- Attempt 01 private evidence.

The additive boundary is an Airline domain adapter between untrusted semantic
JSON and existing canonical v0.1 validation. It does not alter domain law,
Root authority, or shared contracts.

## 15. Safe Attempt 01 Facts

Attempt 01 remains immutable `FAIL_CLOSED` negative evidence.

| Fact | Required preserved value |
| --- | --- |
| Attempt ID | `fcce2c0224517487b59c40e79a75ea00078df393a2552f5b553780f8b7adc64a` |
| Attempt number | `1` |
| Execution head | `829496261a90249b500e7583bb407839e94cd874` |
| Attempt identity SHA-256 | `c3af7707023402b287222615e4e1877e248e1f23ad6b238254f96d7ce19f5bd2` |
| Private inventory SHA-256 | `33818a0230a245392b78194aad2c35966e59f91992170bef7461d5539e56693a` |
| Private inventory digest | `567b567ba4b37a04665cdcc085f1feb1be0fd2facad3921f5fbd5b276c5a2163` |
| Generation gate SHA-256 | `8fcdf7ef795d09178c3352999bdd3087c5e8e1b78184b6d055e29d0311991653` |
| Private root entries | `4` |
| Raw inventory files | `23` |
| Private metadata modes | `0600 / 0600 / 0600` |
| Final source status | `FAIL_CLOSED` |
| Failed actor | `client_purchase_intent_reviewer_llm` |
| Collector failed stage | `actor_validation` |
| Outer failed stage | `collector_result` |
| Outer reason | `a1_airline_collector_failed` |
| Primary reason | `selection_input_snapshot_mismatch` |
| Secondary reason | `semantic_to_contract_bridge_guard_failed` |
| Provider callbacks started/completed | `3 / 3` |
| Actual external status | `UNVERIFIED_PARTIAL` |
| Public safe report | `ABSENT` |
| Private attempt state | `PRESERVED` |
| Retry count | `0` |
| Package / Anchor / Replay / effects | `0 / 0 / 0 / 0` |

The exact preserved callback prefix is:

1. `tri_party_airline_orchestrator_llm`;
2. `tri_party_airline_semantic_architect_llm`;
3. `client_purchase_intent_reviewer_llm`.

These hashes, digest, counts, modes, and actor prefix are fixed external
acceptance anchors. The predecessor verifier must compare observed evidence
against every fixed anchor; internal consistency among predecessor files is
necessary but is not sufficient.

The preserved safe comparison proved that the candidate-set reference and
snapshot ID matched while the snapshot digest did not match. No raw prompt,
response, or candidate value may be used to reinterpret that failure.

## 16. Self-Contained Attempt 02 CLI Contract

The only owner-terminal Attempt 02 command is:

```text
PYTHONPATH=. .venv/bin/python -m demo.run_two_domain_airline_all_real_program_v01 --real-provider --attempt-number 2 --private-output-directory <new-absent-absolute-private-path> --prior-failed-attempt-directory <preserved-attempt-01-path> --prior-attempt-id fcce2c0224517487b59c40e79a75ea00078df393a2552f5b553780f8b7adc64a --owner-reviewed-attempt-02
```

Every argument is mandatory. Missing, duplicated, ambiguous, malformed, or
mismatched recovery input fails closed before provider construction and before
creation of the new private output directory.

The runner must not infer a predecessor, discover a directory, select a latest
attempt, read an environment fallback for an argument, or advance an attempt
number automatically.

## 17. Complete Predecessor Verification Law

Before Attempt 02 can create its output root or construct a provider, the
predecessor verifier must independently establish:

1. explicit predecessor path safety: absolute, existing, non-symlink,
   non-repository, and distinct from the new path;
2. exact Attempt 01 ID and attempt number;
3. exact Attempt 01 execution head and ancestry to the current approved head;
4. strict canonical attempt-identity JSON, exact semantic identity, SHA-256,
   size, mode, regular-file identity, and directory-entry identity;
5. exact private-inventory canonical JSON, ordered rows, count, aggregate
   digest, SHA-256, size, mode, and semantic equality;
6. exact generation-gate canonical JSON, SHA-256, size, mode, final
   `FAIL_CLOSED` state, failed stage, reason, call prefix, retry count, public
   report state, and preservation state;
7. exact raw-attempt directory identity and complete bounded inventory;
8. no missing, extra, replaced, symlinked, FIFO-backed, device, socket, or
   non-regular entry;
9. exact immutable file identities, hashes, sizes, modes, and logical order;
10. safe summary fields matching the preserved final status, failed actor,
    stage, errors, three-actor call order, and numeric counters;
11. safe validation fields matching the failed actor's rejected validation
    result and stable reasons;
12. canonical Airline public safe report remains absent;
13. retry, Package, Anchor, Replay, publication, and real-world-effect counts
    remain zero;
14. no raw prompt, response, extracted candidate, credential, or private body
    is read outside the explicitly permitted predecessor audit boundary or
    copied into Attempt 02.

Every predecessor filesystem read must be descriptor-bound and non-following.
Verification must use bounded regular-file reads, compare the exact inventory,
verify `fstat` device/inode identity and mode against the current non-followed
directory entry, and reject any path or inode replacement during verification.
No symlink may be followed at the root, intermediate-directory, raw-directory,
or file boundary.

The verifier must compare the independently read evidence against every fixed
Section 15 anchor: all four hashes/digests, private-root entry count, raw-file
count, all three private metadata modes, and the exact ordered three-actor
callback prefix. Recomputing values that agree only with other predecessor
files does not establish acceptance.

The predecessor verifier must fail closed for a PASS, malformed, mutated,
incomplete, replaced, symlinked, non-regular, extra-entry, wrong-ID, wrong-head,
wrong-reason, wrong-stage, wrong-counter, or unproved predecessor.

The complete predecessor proof must be repeated:

1. immediately before the first provider callback;
2. immediately after collection returns or fails;
3. immediately before the final Attempt 02 generation gate.

Any drift blocks acceptance. Attempt 01 remains untouched throughout every
check.

## 18. New Path and Attempt 02 Identity Law

The Attempt 02 output path must be explicit, absolute, absent, non-symlink,
outside the repository, different from the predecessor path, and not nested
inside the predecessor path. Its parent must be an existing real directory.
No reuse or overwrite is allowed.

Attempt 02 must receive new attempt-qualified values for:

- `attempt_id`;
- `run_id`;
- `report_id`;
- `source_task_id`;
- `package_id`;
- `logical_package_ref`;
- `output_directory_ref`.

Attempt 02 identity must cryptographically bind:

- prior attempt ID and execution head;
- prior attempt-identity SHA-256;
- prior generation-gate SHA-256;
- prior private-inventory SHA-256 and aggregate digest;
- prior failure reason and failed stage;
- current execution head and attempt number `2`;
- current private output-path hash and logical output reference;
- provider mode, model, actor count, and new provider-call ceiling.

No Attempt 02 identity may equal or masquerade as an Attempt 01 identity. No
absolute private path or reversible private-path form may enter terminal
output, public evidence, or a repository document.

## 19. Attempt 02 Execution and No-Retry Law

Attempt 02 permits exactly one canonical collector invocation and at most
twelve new provider callbacks. Accepted completion requires exactly twelve
ordered callback starts and completions, one application-level provider call
per actor, no duplicate actor call, and all existing semantic, BSEP, causal,
Root, Corridor, Ledger, Crypto, secret, and zero-effect validation.

`retry_count` remains zero. Attempt 02 is a distinct owner-authorized attempt,
not an internal retry. No loop, resume, provider fallback, schema fallback,
raw Attempt 01 reuse, automatic attempt advancement, second collector, or
in-place repair is allowed.

Attempt 03 is not authorized.

## 20. Budget Reconciliation

Accepted-run geometry and cumulative consumed-call ceilings are distinct:

| Budget | Reconciled value |
| --- | ---: |
| Accepted Airline attempt geometry | `12` |
| Preserved failed Attempt 01 conservative consumption | `3` |
| Attempt 02 maximum new calls | `12` |
| Cumulative Airline ceiling through Attempt 02 | `15` |
| Supplier accepted budget | `6` |
| Cumulative programme ceiling | `21` |

The Attempt 01 value is preserved evidence data. This governance pass performs
no provider, network, or Gemini call.

The preserved value `3` is conservative observed callback-start consumption.
It must not be relabelled as independently verified physical network calls or
Gemini completions. Attempt 01 external status remains
`UNVERIFIED_PARTIAL`.

## 21. Publication, Failure, and Effect Law

Every failure remains `FAIL_CLOSED`. A failed Attempt 02 is preserved as a
new immutable attempt, receives no retry, and cannot produce a public PASS
claim.

The canonical Airline public safe report remains forbidden unless every
required validation, causal, Root, Corridor, Ledger, Crypto, Package, Anchor,
and Replay gate passes. No raw provider evidence may enter that report.

Neither the provider nor runtime canonicalization may create authority,
permission, action, packet, receipt, FinalOutput, payment, ticket, booking,
publication, or any real-world effect. Real Airline, bank, GDS, payment, and
ticketing operations remain forbidden.

Supplier S1 remains forbidden until accepted A1 Attempt 02, its independent
generation audit, and complete A2 Airline closure.

## 22. Planned Focused-Test Matrix

The future six-file implementation must prove at minimum:

1. causal proposer semantic fields are exact and causal mechanical fields are
   rejected;
2. causal reviewer semantic fields are exact and causal mechanical fields are
   rejected;
3. unknown, raw, authority, action, and effect fields in the five causal
   envelopes fail closed;
4. malformed JSON, wrong types, empty required semantics, and unbounded values
   fail closed;
5. recommendations outside visible or hard-compatible candidates fail closed;
6. runtime derives exact transaction, actor, request, selection, BSEP,
   snapshot, digest, status, safety, and zero-effect fields;
7. full canonical proposer mappings pass the unchanged binding validator;
8. full canonical reviewer mappings pass the unchanged causal validator;
9. `provider_field_names` and `runtime_field_names` are complete and disjoint;
10. raw response, extracted semantics, canonical artifact, validations, and
    provenance remain separately labelled and mutation-isolated;
11. no test claims Gemini returned runtime-owned lineage;
12. all twelve actors use JSON MIME with no response schema;
13. each actor makes exactly one application-level provider call;
14. provider or parsing failure makes no fallback call and preserves
    `FAIL_CLOSED`;
15. the shared helper and Google transport are not duplicated or modified;
16. exact Attempt 01 deterministic and parser compatibility remains;
17. Attempt 02 is accepted only with complete predecessor proof and owner
    authorization;
18. missing or wrong owner flag, predecessor path, or predecessor ID fails
    before output creation and provider construction;
19. PASS, malformed, mutated, symlinked, FIFO-backed, or extra-entry
    predecessors are rejected;
20. predecessor mutation at every repeated verification checkpoint is
    rejected;
21. any changed fixed Attempt 01 anchor fails closed, including any of the four
    hashes/digests, root-entry count, raw-inventory file count, private
    metadata mode, or exact actor prefix;
22. descriptor-bound non-following reads reject symlinks, non-regular files,
    path replacement, inode replacement, mode drift, and inventory drift;
23. same, nested, existing, relative, or unsafe new paths are rejected;
24. Attempt 02 identities differ from Attempt 01 identities and bind all
    predecessor hashes;
25. result, identity, inventory, and gate record attempt number `2`;
26. one collector invocation and at most twelve callbacks are enforced;
27. all twelve actors use JSON MIME with no response schema and exactly one
    application-level provider call, while causal mechanical-field rejection
    remains limited to the five causal envelopes;
28. provider error records one failed call with no fallback or retry;
29. no retry, Attempt 03, raw reuse, in-place repair, or public report exists
    on failure;
30. provider/network/Gemini sentinels prove zero external operations in tests;
31. authority, permission, action, packet, receipt, payment, ticket, booking,
    FinalOutput, publication, and effect counts remain zero;
32. all six implementation paths are exact and all frozen surfaces remain
    byte-identical.

No implementation test may read a real credential or call a real provider.
Full repository pytest is not authorized by this preflight.

## 23. Commit and Review Boundaries

The sequence remains separated:

1. this corrected preflight and active checkpoint update;
2. the six-file semantic/runtime boundary implementation and focused tests;
3. owner review of the implementation;
4. one owner-terminal Attempt 02;
5. independent Attempt 02 generation audit;
6. accepted safe evidence and complete A2 Airline closure.

No implementation, live attempt, evidence publication, or closure commit may
be combined with this governance pass.

## 24. Non-Claims and Zero-Operation Boundary

This preflight does not implement or execute Attempt 02. It creates no Package,
Anchor, Replay, publication, authority, permission, action, receipt, payment,
ticket, booking, FinalOutput, or real-world effect.

Provider, network, Gemini, and effect operations during this pass are
`0 / 0 / 0 / 0`.

Original Gate 1 and R1 remain `CLOSED_PASS` for their frozen contracts.

## 25. Definition of Done

This preflight is ready for owner review when:

- the rejected full-causal-schema draft has no canonical or implementation
  authority;
- the semantic/runtime ownership boundary is explicit;
- single-call JSON MIME reuses the committed helper without transport
  duplication;
- the exact six-file future implementation scope is frozen;
- all canonical validators and domain laws remain unchanged;
- complete Attempt 01 preservation, Attempt 02 predecessor, identity, budget,
  failure, and publication rules are self-contained;
- repository changes are limited to this document and the active `AGENTS.md`
  checkpoint block;
- no provider, network, Gemini, live runner, Package, Anchor, Replay,
  publication, or effect operation occurred.

## 26. Immediate Next Gate

After owner review, and only in a separate implementation pass:

`two_domain_all_real_sealed_evidence_program_v01_a1_attempt_02_semantic_runtime_recovery`

That pass may modify only the six paths listed in Section 13. It must not run
the owner-terminal Attempt 02.
