# Correction 01: native DRS descriptor reference

This is the first feedback correction to football_reference_v01, not a new kit version or an acceptance claim. The previous submitted bytes and the failed independent trial remain part of the review record. This correction has not been executed by the author.

## Reported independent observation

The confined exact-only story terminated in the requester before requester Work. The reported chain was run_peer_v01 -> transport.retrieve -> memory.descend -> public build_meaning_record_v01, with ValueError('drs_secret_payload_forbidden'). VenueRoot native PURE Work and source/publication Root reviews had completed. The publisher's later EARLY_CLEAN_EOF was secondary to requester termination. No subsequent shift, booking, repeat or verify phase was reached. Native acceptance, live checks and supplied checks were not passed.

The reported public source_record_ref was source:football:07576902616520d36071ad99009971fc7e1f96d29744525dfbf8cfbc3322dbcd. The reported pointer_id was g5pointer:38be13337e4a793b415b05ad4b33d11c58d71483f6f4a220bd257e94ae79901d. They remain public metadata, not secrets and not test answers. Neither observed value is embedded in executable code or regression fixtures.

## Exact unchanged public predicates

The pinned source/hedgehog/drs_semantic_address_v01.py has SHA-256 9b0cae8c7d5f02cec8d3df573d7107b7b4b013b3e7416480e871b833aa6e2e20.

- Lines 82 and 508–510 explicitly recognize complete bare SHA-256 values before generic text scanning.
- Lines 130–134 define _CARD_NUMBER: a 13–19-digit run, with its declared digit/separator boundaries.
- Lines 479–485 route ordinary reference strings through _secret_reason.
- Lines 518–519 return drs_secret_payload_forbidden when the card-number or passport pattern matches.
- Line 1586 applies _reference_tuple_reasons to MeaningRecordV01.source_reference_ids.
- Lines 1635–1698 build and validate the actual native MeaningRecord without a caller-supplied validation result.

The previous adapter passed the exact prefixed foreign source and pointer IDs directly into source_reference_ids. The reported source ID contains the run 07576902616520: 14 digits preceded by a colon and followed by d. That input matches the stated card-number predicate, while the whole prefixed string is neither a bare SHA-256 value nor a native G2B canonical ID. This is a static source/predicate diagnosis of the reported refusal, not a newly executed native result.

The actual supported storage/reference surface is also pinned:

- source/hedgehog/local_drs_resolver.py:124–138 defines SemanticDRSRecordInput, including record_id and structured source_refs.
- The same file:257–291 persists the supplied record identity and exact structured provenance; 335–345 uses source/source_id metadata. SHA-256: 5fa06d3cd243f6ef8cfd87997596413654ef03efac27e622ac9093659aea99a4.
- source/hedgehog/drs.py:78–103 writes and reopens actual local records by record_id. SHA-256: 7e78be61a24f285608841cbd8d07047967fb0abf7708173eadeff5f5578553f4.
- local_drs_resolver.py:398 and 461–501 mark external provenance as requiring review and blocking direct reuse. The correction retains those observations and passes their flags/reasons to the local Root review; it does not remove or rename the external marker.
- drs_memory_resolution_v01.py:1505–1589 separately requires actual local accepted Root context, source references, policy, currentness and other native checks. SHA-256: 698a34262d4442dba1474a1a137ca19057c27d2d20595a9f82e848c3816579d8.

## Candidate correction

Only candidate_domain/memory.py changes runtime behavior.

1. Persist the complete signed descriptor under its own canonical SHA-256 record_id in actual LocalDRS, on both source and requester sides.
2. Preserve original source_record_ref, source_review_ref, pointer_id and publisher exactly in the descriptor and in structured SemanticDRSRecordInput.source_refs marked external_drs.
3. Reference that actual local descriptor record from MeaningRecordV01.source_reference_ids using its bare content address. This names a different, real persisted object; it does not strip, encode, alias or overwrite a foreign ID or fabricate a native G2B identity.
4. Retain content_fingerprint as the exact original unsigned pointer hash. Save descriptor_binding.json, binding both identities and the unchanged foreign provenance, and include that binding and resolver observations in the actual local Root claim.
5. After reopening storage, verify resolved record identity, complete envelope equality/hash, structured provenance, native meaning-record identity/reference/fingerprint and original source time. Re-open and check the descriptor again after native summary descent, including the existing signature/profile/currentness validator.
6. Keep the original natural-language summary, CONNECTOR_OBSERVATION then locally reviewed ROOT_ACCEPTED_CONTEXT, native eligibility/refusal checks, source clocks, publisher identity and one-hop/body-release protocol unchanged.

No protected source, regex, enum, public ABI, crypto, Root result, effect code or transport code is changed. No validation failure is converted into success; no retry or digest search tries to find an input that passes a guard. Generic reference strings and summaries still encounter the original privacy guard.

## Regression source and validation limits

tests/test_memory.py is an inert component regression. It constructs a real source through the existing native producer, performs the candidate's persisted native descent, checks the descriptor identity and exact foreign provenance after reconstruction, and verifies unreviewed/accepted native eligibility states. Synthetic prefixed IDs containing 14- and 19-digit runs must still be rejected by the unchanged public builder; secret-shaped summary text must still be rejected. Altered signed metadata must refuse before local Root review, followed by a lawful unchanged descriptor.

These are authored test assertions for a reviewer to execute, not substituted native outcomes. The source/predicate inspection and syntax-only checker are the only author validation. No command, candidate import, test, Work, Root, transport, effect, provider call or restricted execution was performed by the author. A successful corrected confined story, later phases, performance limits, live/supplied checks and admission remain unverified.
