# Correction 03: final permitted correction, with a remaining contract blocker

Candidate football_reference_v01 remains QUARANTINED_FOR_REVIEW, installable_now=false.
This complete inert pack contains proposed fixes and an explicit unresolved binding
contract. It is not a completed native story or an acceptance certificate. No fourth
correction, replacement author trial, supervisor implementation or checker edit is
requested.

Reported independent evidence, kept distinct from author observations:

* Correction 02's exact event returned NEEDS_CONFIRMATION and approved shift returned
  OFFER_READY, both passing independent scalar checking. The actual source and
  requester PURE records passed native_result against their recorded inputs.
* The full story failed rc1, not timeout. On publisher booking, dispatch returned and
  execute_bound_effect_v01 returned. The source registry contained three reservations
  and one idempotency entry. Then effect.confirm's n.plain(host.registry) raised
  TypeError('mappingproxy') while saving native_dispatch.json. Mutation counters and
  cleanup had not run; receipt.json and native_dispatch.json were not completed.
  The reported zero mutation count was therefore not evidence of no effect.
* Requester SOURCE_UNAVAILABLE_PEER_CLOSED and BrokenPipeError were secondary.
* Supplied-input checks with the source's semantic offer or the saved signed body
  each refused supplied_consumed_input. Requester result_json did equal report
  without native_refs. The expected exact three-hash Root claim refused
  recorded_root_claim_binding because the recorded claim contained additional fields.
* Booking/repeat/VERIFY, remaining challenges, live contrasts and the final supplied
  proofs are not accepted. This correction has not been executed.

Public serialization contract and proposed correction:

gate5_native_v01.py:28-37 (SHA-256
bba423e434d9fb9d5695b649191e9f31a2743b7bbe9327c80c0ce8b34162e3ec)
recurses through dataclasses, dict and tuple/list but rejects mappingproxy. No change
to that helper is proposed. kernel/abi_v01.py:436-447 (SHA-256
cc1a660a3cdceb5c30728b27016e99a752561969d744744d55b18ce0af398d31)
owns kernel_artifact_to_plain_dict_v01, including artifact validation/projection.

candidate_domain/evidence.py provides only a one-way audit projection. It delegates
every KernelArtifactV01, including a receipt, to that public ABI function before
generic dataclass traversal. Other read-only Mapping values are projected as data,
with exact string keys and no coercion. Unsupported objects still raise. This is
not a deserializer, grant builder, identity algorithm, custom validator or kernel copy.

effect.confirm now:

1. Keeps its immutable pending marker before dispatch.
2. In dispatch's finally, accounts for the actual callback mutation observations
   and removes the packet's callback binding before any evidence serialization.
   An outer finally also cleans up preparation failures.
3. Exports the actual receipt with the ABI function and saves it and actual readback.
4. Checks the actual native registry and exact key/payload/packet/request/slot bindings.
   Saves matching terminal receipt history before the larger audit projection.
5. Projects the live registry/events as inert native_dispatch.json data.
6. On a post-dispatch failure, attempts independent receipt, readback, native trace
   and UNKNOWN_REQUIRES_READBACK outcome writes; evidence-write failures are retained
   and attached to the original exception. The original exception is re-raised.

No state from the reported failed run is accessible to the author or changed here.
A pending old action with no saved matching receipt remains UNKNOWN_REQUIRES_READBACK.
The callback is not retried. A fully saved matching receipt/readback may be reused as
history with zero additional dispatch. A changed payload refuses. A failure in an
optional audit after terminal history saving still fails the event; it does not
print a completed booking. No Host is reconstructed, consumed packet dispatched,
receipt fabricated, rollback attempted or OS-crash guarantee claimed.

Exact Root claim correction:

gate5_lifecycle_supplied_v01.py:23-54 (SHA-256
22419806c70631543f66c2d5894b6858e2f4462907277c8fddb025f32e329b88)
uses equality, not subset matching, for actual == claim_value at line 53.
transport.result_claim now contains exactly request_sha256, offer_sha256 (the
received saved body) and result_sha256 (actual consumer output/report without refs).
The real Root still selects the actual requester artifact and retains its source
subject/time window/checks. Full request, consumed wrapper, result, Work/source/review
and import references are saved separately in result_evidence.json. The body hash
continues to commit its original source and review identities. No recorded Root
output is edited or reconstructed as permission.

Unresolved shared-offer contract, exact predicates:

Let E be the original VenueRoot outputs.offer_json string, B the canonical bytes of
offer_body.json (the common signed body), and C the requester inputs.offer_json.
The retained implementation has E = canonical semantic offer, B containing that offer
plus provenance/time/booking fields, and C = canonical {body:B,source_projection:S},
where S includes the subsequently authenticated STATUS observation.

1. CANDIDATE_OUTPUT.md:104-112 (SHA-256
   e28debd12e922d8eefdc66372b87638446a5c8eedc11cebfd5144ff84167b0bd) declares the
   two input fields on each Work side, the shared offer_json name and result_json
   equal to the canonical report without native_refs. Feedback treats the shared
   name as an exact source/consumer payload contract, trying E and B as inputs.
2. gate5_supplied_v01.py:24-48 (SHA-256
   5cbb0e4851d65496e2097147b57a4bf285d36bdca9752f75db01694efe755f69) at line 42
   requires the recorded invocation input map to equal expected_inputs exactly;
   line 44 also requires proof.inputs == expected_inputs. It offers no projection
   or source-adaptation equivalence. Supplying E or B when C was consumed must refuse.
3. HOW_TO_BUILD.md:162-169 (SHA-256
   6636167b75d8fec5786e80cb5ce3027c02748d58d5d63765655b1e451d60dea3) requires native
   Work, then current source review, then the body containing their original IDs.
   gate5_body_profile_v01.py:10-11,30 (SHA-256
   7e434e75d1913a7fab71ebc882fb21640fd33e7324ff035bc376a4b7cd65d89f) mandates
   source_work_ref and source_review_ref in every reviewed body profile.
4. kernel/work_composition_v01.py:606-619 (SHA-256
   1f068c0d1156a312f36a7e55b7cbaf0e3e84503168b3305e10420bd8e3d3cbf0) creates the
   result artifact identity from the actual Work results, which include E. Making
   that same E equal B with its own result artifact and later source review IDs
   introduces a downstream/self-reference. Predicting those IDs, using placeholder
   provenance, editing the Work output after completion, or borrowing an unrelated
   earlier Work's identity would not preserve the required causal binding.
5. In this retained profile, canonical B alone also omits the later request-bound
   STATUS checked_at/valid_until that appears in the required actual report source
   projection. C explicitly carries those verified facts as data. Hidden globals
   or PURE I/O would not be honest two-input computation.

Therefore the simultaneous exact-byte interpretation C=E and C=B cannot be claimed
satisfied under the required identity order. The candidate also does not claim
that either single alternative E or B is its consumed C. An explicit versioned
choice of semantic-offer projection versus post-review body/context input would be
needed to resolve that boundary; it is outside this frozen correction. No alternative
runner/checker, relaxed equality, altered protected source or fabricated proof is
included. No assumption that passing with recorded C passes the declared shared
contract is made. The discrepancy remains BLOCKED_SHARED_OFFER_IDENTITY_CONTRACT.

The original native executors, producer output, signed body and requester invocation
shape are deliberately retained as their true values; this pack remains nonconforming
at that boundary. Prior completed captures are neither edited nor re-signed.

Authored verification, not executed:

tests/test_evidence.py covers immutable nested Mapping projection, unsupported objects
and key types. tests/test_native.py adds exact ABI receipt/registry projection checks,
a real temporary-directory obstacle to the post-dispatch audit write, cleanup/counts,
saved-receipt reuse without redispatch, and an older uncertain-store case made from
copies of actual generated marker/readback with no invented receipt. It also invokes
the public supplied native validator with the actual recorded inputs and root_record
with the independently constructed exact three-hash claim. These assertions are not
runtime results, peer runs, or a claim that the blocked shared-input proof passes.
The unchanged G54 runner has no unittest discovery facility. All authored tests remain
unexecuted. Inert syntax/JSON inspection is the only author validation.
