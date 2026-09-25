# Football G54D V01 inert candidate

This directory is a proposal for independent review. It is not installed, admitted, or certified for execution. The author used only approved text readers, candidate text writers and syntax inspection. No candidate import, test, native Work, Root decision, transport, provider call or effect was executed during authoring. The coordinator owns candidate.json.

This is the restored G54D lineage, correction_index=4 and submission_number=5. The owner authorized exactly one additional submitted pack. The historical initial-plus-three result remains INCOMPLETE; this continuation does not reset that trial or claim acceptance.

The entrypoint is exactly:

```python
def run_peer_v01(*, role: str, input_data: dict, state_root: pathlib.Path,
                 output_root: pathlib.Path, channel: PipeChannel,
                 bootstrap: PipeChannel) -> dict | None:
    ...
```

Only the separately approved restricted runner may load it. Import defines functions/classes/constants; it does not admit capabilities, create Roots/keys, perform Work, open files, or communicate. The runner supplies two independent processes and their own directories/channels. The candidate does not create processes or inspect channel descriptors.

## Correction 4: local Root basis for authenticated STATUS refusal

The current reviewer diagnostic identified a missing decision after authenticated non-active STATUS: requester_event's known ValueError path wrote REFUSED without a local Root refusal for that outcome. Earlier metadata and retrieval ACCEPT decisions had different subjects. The reviewer observed no booking execution or registry mutation. This diagnostic was newly supplied after correction 3; the attributed historical progress below remains unchanged.

The focused repair is in candidate_domain.run. ImportStore.observe still authenticates and persists terminal highwater before check_status. The adapter records the exact signed descriptor and STATUS, local prepared FETCH and STATUS request, persisted highwater, and the separately read pointer-check, authentication and current-use-check UTC times. The prepared FETCH in this refusal evidence has not been sent; the normal fetch_request.json remains evidence of the actual FETCH stage. Public check_status still enforces ACTIVE after all authentication/currentness checks.

Only the actual status_not_active exception enters refuse_inactive_status. It revalidates the preserved pointer and STATUS through the public check_pointer/authenticate_status functions at their recorded check times, requires REVOKED/SUPERSEDED and the matching persisted terminal entry, and computes source_active from that entry. Its fresh local Root review uses predicate football_current_source_status_v01 and the original request as subject. The claim binds the full original request and its hash, actual reason, report status, foreign source record/revision/review, pointer, prepared FETCH identity, signed STATUS hash, terminal entry, observation time and the hash of status_refusal_evidence.json. That evidence file also retains the original request and independently pinned local policy/keyset.

The existing native review adapter builds and validates the live Root kernel/input/result. Its failed active check produces the native BLOCKED_FAIL_CLOSED outcome. The repair requires that exact outcome, saves the actual refusal_review.json, and puts its decision_id plus the evidence hash in refusal.json. The completed report's native_refs links both files. It does not use a previous metadata ACCEPT, deserialize authority, copy a foreign decision, or manufacture a native REFUSED enum.

Source support is gate5_contracts_v01.py lines 309-331 (authentication then ACTIVE), gate5_lifecycle_v01.py lines 31-39 (durable observation), gate5_native_v01.py lines 45-103 (live review and projection), and root_decision_v01.py lines 678-716 (hard failure gives BLOCKED_FAIL_CLOSED). Exact pinned hashes are in source_impact.json. No approved code or schema is changed.

The new review's UTC records a refusal now. Checking evidence at its retained observation times proves the basis of that refusal; it does not refresh STATUS, extend source TTL or authorize a fetch/action. No FETCH, consumer Work or local effect follows this terminal branch. For a CONFIRM, the source may already have crossed its independently owned effect boundary before returning metadata, so this branch reports CURRENT_STATUS_UNKNOWN and requires reconciliation instead of claiming a clean source no-effect refusal. Requester counts remain local. Unknown errors or failure to obtain the actual refusal result propagate; no catch converts them to completed REFUSED.

tests/test_status_refusal.py contains reviewer-only regressions for the actual requester_event error branch, genuine native source publication/metadata descent/local refusal, real public signatures, REVOKED and SUPERSEDED with feasible/empty producer results, report-to-decision/evidence linkage, zero requester Work and no FETCH, highwater after reconstruction, refused terminal revival and a distinct lawful ACTIVE observation. It also covers changed signed bytes, an unknown error, stale STATUS and confirmation uncertainty. Its in-memory message driver supplies only component replies, never a body or fake Root result; it does not implement framing, run a second peer, observe OS I/O or claim P7 coverage. The production entrypoint continues to receive real operator-provided PipeChannels. Earlier booking/history tests and runtime behavior are preserved.

All correction 4 code and tests are inert and unexecuted by the author. Only text parsing is available here. The complete pack needs independent review and the separately authorized restricted runner; no installation or admission is claimed.

## Correction 1: exact metadata descent approval

Reviewer feedback for submission 0 reports that package shape and source-safety review passed, followed by a P7 execution failure on the first original FIND event. Source native offer Work and publication occurred. Requester metadata descent raised drs_root_decision_binding_invalid; no booking dispatch, executor or mutation occurred. The source peer's later SOURCE_UNAVAILABLE_IPC_STALLED was a consequence of the interrupted exchange, not a successful domain refusal. These are attributed reviewer observations, not author execution or acceptance.

The source-backed defect is the omitted claim predicate. In approved source/hedgehog/drs_memory_resolution_v01.py (SHA256 698a34262d4442dba1474a1a137ca19057c27d2d20595a9f82e848c3816579d8), lines 3113-3123 require claim_id=plan.retrieval_plan_id, subject=plan.semantic_address_id, predicate=approve_controlled_memory_descent_plan_v01, object_or_value=the exact public plan projection, and authority_class=NONE. The required predicate is declared at lines 223-225. The supplied gate5_native_v01.pointer_descent_v01 demonstrates it at lines 179-181, and root_review exposes the predicate argument at lines 45-46. Our wrapper previously dropped that option, leaving g51_bounded_context_review.

candidate_domain.native.review now forwards an explicit keyword-only predicate while preserving the default for other review subjects. candidate_domain.memory.descent supplies the exact public descent predicate. The existing live local Root kernel/input/result, plan selection, owner IDs, result hash, time window, narrow budget and native execute_local_memory_descent_v01 call are retained. No approved source, native authority check, transport behavior, refusal label or peer ownership is changed.

tests/test_descent.py adds a reviewer-only component regression: actual persisted metadata descent, inspection of its exact plan claim, native rejection of an accepted generic review, native rejection of a foreign Root review, and a fresh lawful local descent after those refusals. It reconstructs stored metadata only; Root authority always comes from fresh live review calls. The component fixture does not claim authenticated peer retrieval. The author has not executed the corrected code or these tests. Syntax inspection is the only local check; the corrected complete pack requires independent review and the prescribed runner again.

## Correction 2: native booking operation identity

Reviewer feedback for correction 1 reports that inert shape/source review and genuine native DRS descent passed. Exact FIND and approved-shift FIND completed source Work, publication/release, requester Work and final Root review in P7. First CONFIRM then failed before dispatch at the native business-semantics constructor with capability_business_operation; executor starts and registry mutations remained zero. The later requester SOURCE_UNAVAILABLE_IPC_STALLED was a consequence of that source failure, not a successful refusal. These remain attributed reviewer observations, not author execution or whole-domain acceptance.

Approved source/hedgehog/kernel/effect_firewall_v01.py, SHA256 46a453e0ef98565f0de59ab062b307eff6549a716973268a034592a5f98463bd, line 2360 requires operation_key == logical_effect_namespace AND selected_action_class.startswith(MOCK_ACTION_PREFIX); line 62 defines that prefix as mock_action:. The submitted operation football.book.v01 and namespace football.booking.v01 violated equality. The action class mock_action:football_booking already met the prefix requirement.

candidate_domain.effect.admit now defines football.book.v01 once and supplies that same local value to operation_key and logical_effect_namespace. Definition.operation_id continues to derive from the returned native semantics. Action class, BOOK/BOOKING classes, registry namespace, typed exhaustive device/payload bindings, code observation, native admission, Root preparation, Host/Firewall dispatch and all existing permission/currentness checks remain as before. Native code generates the resulting declaration, contract and canonical action identities; none is supplied as a fabricated grant or receipt.

tests/test_business_semantics.py adds reviewer-only actual declaration/admission snapshot validation, exact typed mapping assertions, public rejection of the original namespace mismatch and of an invalid action prefix, and lawful declaration/admission continuation after both refusals. The existing native MOCK booking/history test remains available to the reviewer. The author has not imported or executed corrected code or tests; local verification is syntax/data inspection only.

The reviewer additionally reported an exact bijection from the frozen natural/artificial category facts to this candidate's documented natural_grass/artificial spelling. That encoding adaptation changed no requests, IDs, prices, intervals, approvals or rules and was not counted as a model correction. This correction makes no surface-vocabulary or selection changes.

## Correction 3: current publisher reports and source-reference form

The reviewer reports that attempt_02 passed the main FIND, approved-shift FIND, first native booking, identical repeat and VERIFY chain, plus low-budget, missing BOOK, missing history, foreign audience, changed schedule, changed same-key payload, permutation and second-team cases. Two failures remained: terminal source status was not reflected in publisher reports, and one changed-ID/price/order request caused native metadata construction to reject a generated source reference. The later source IPC stall followed the interrupted requester; it was not a successful refusal. These are attributed reviewer observations about the prior pack, not author execution or acceptance of this correction.

The report defect was in candidate_domain.run.complete_report: publisher_event retained the semantic producer status even after sending a REVOKED STATUS. The current publication report now applies the retained source status, falling back to the source's explicit operator status if no STATUS projection exists. REVOKED/SUPERSEDED produce REFUSED with empty slots and zero total, including when the original producer result was NO_COMPLETE_OFFER. UNAVAILABLE produces CURRENT_STATUS_UNKNOWN. If an executor already started, the report remains CURRENT_STATUS_UNKNOWN and retains the observed dispatch/mutation uncertainty and any receipt reference. E, B, the original source projection and native evidence are not rewritten. The separate saved-receipt HISTORY branch has no new body and retains its explicit historical slots and receipt with zero new dispatch.

The reference defect came from minting source:football: followed by a hexadecimal SHA256 digest. Approved source/hedgehog/drs_semantic_address_v01.py (SHA256 9b0cae8c7d5f02cec8d3df573d7107b7b4b013b3e7416480e871b833aa6e2e20) validates source_reference_ids at line 1586 through _reference_tuple_reasons and _reference_reason (lines 479-485, 571-583). Its _secret_reason (lines 508-520) explicitly accepts a bare lowercase SHA256 reference, but subjects general prefixed text to secret-pattern checks, including the 13..19-digit pattern at lines 130-134. Ordinary digest digit runs can therefore cause this failure. The contracts.ref predicate at source/hedgehog/external_drs/gate5_contracts_v01.py line 113 permits the bare reference; common body validation at lines 178-184 adds no source-reference prefix requirement.

candidate_domain.policy.consumer_policy now mints the source record ID as sha({domain:"football.source_record.v01", original:sha(original_request), booking:is_confirmation}). This is the supported bare SHA256 form, with domain separation inside the hashed canonical input. Both peers independently derive the same original-request identity. Publication carries that exact ID through the source Root subject, B, manifest and pointer; metadata descent retains it unchanged in source_reference_ids. Received or historical IDs are never stripped, normalized, reminted or migrated. The source Work, current local Root decisions, temporal axes and existing native validators remain in place. The fixed metadata-only natural-language summary is unchanged.

The denied-release branch is unchanged: the actual release Root checks the active source entry and policy; its authenticated decision ID is retained, and a denied BUNDLE contains body=null and manifest=null. Neither correction changes transport, producer selection, booking semantics, native Host/Firewall dispatch, receipt/readback, consent, independent peer ownership or prior correction bindings.

tests/test_final_correction.py adds reviewer-only component tests for terminal reports with feasible/infeasible E; ACTIVE continuation and unavailable observation; retained terminal status; after-start uncertainty and explicit receipt history; changed synthetic IDs/prices/order; independently derived source references preserved through actual persisted native descent; and native secret-pattern rejection followed by acceptance of the documented bare reference form. Its synthetic report/metadata fixtures are not authenticated bundles, grants, execution telemetry or native receipts. The tests do not prescribe hidden selections. Previous native descent, booking semantics and Work/history tests remain unchanged.

That correction 3 pack was checked only as inert Python/JSON text. No candidate import, test, native call or peer execution was performed by the author. Independent review and the prescribed runner decide the corrected behavior. Existing state from an older candidate's different ID recipe is not migrated or relabeled; this pack targets fresh reviewer-owned peer state.

## Inputs and operator policy

Each peer receives g54.peer_input.v01 with exactly version, role, events and policy. Events are ordered, at most eight, with unique event_id matching [A-Za-z0-9][A-Za-z0-9_-]{0,63}. Requester events contain exactly event_id and request; publisher events also contain inventory. Both may additionally contain the pair semantic_proposal and semantic_capture. The schemas in schemas/ define normalized requests, inventory, bodies and reports. The functions in domain.py additionally check all relationships, calendar validity, uniqueness, integer arithmetic, hard requirements and optimality. Original request strings/order remain in E.request and original_event.json.

The supported calendar is January 2027, Europe/Tirane, three 90-minute sessions. Native UTC values come from standard-library ZoneInfo; no fixed offset is guessed. Surface natural_grass and full_size=true are hard constraints. Inventory has one currency, a positive revision, at most four unique fields, integer nonnegative tariffs, and at most sixteen available and sixteen occupied intervals per field. Intervals are half-open. Contiguous availability fragments are joined by coverage checking. Selection considers every feasible complete combination, ordered by allowed shift seconds, total price, then the specified sorted ASCII session/field/time/venue tuple. At most two alternatives per session are disclosed. No feasible complete combination means empty NO_COMPLETE_OFFER with total zero.

Both policies have exactly these keys:

| Key | Closed value / purpose |
| --- | --- |
| local_root, peer_root | Distinct reference strings; the operator binds the expected peer identity before key exchange. |
| publish_enabled, release_enabled, accept_football | Actual booleans. The source owns publication/release and the requester owns acceptance. |
| recipients | Unique reference array of at most four authorized readers. |
| status | ACTIVE, REVOKED, SUPERSEDED or UNAVAILABLE. |
| ttl_seconds, max_source_age | Integers 1..300. Original timestamps are immutable. |
| shift_approvals | At most eight records with approval_ref, request_sha256, previous_request_sha256. |
| book_approvals | At most eight records with approval_ref, request_sha256, offer_request_sha256. |

Approval hashes refer to canonical original local requests, never to an expected offer or solution. Book approval authorizes confirming the lawful currently selected offer for that exact original FIND request and exact CONFIRM request under their preserved constraints. The subsequent current local Root claim also binds the actually computed signed body and exact effect payload. This permits precreated peer inputs without predicting future native Work IDs, signatures or prices.

The only allowed relaxation changes one January 8 session's allow_shift_minutes from 0 to 30 in a higher request revision. Its start/end, other sessions, budget, currency, venue and team remain unchanged. A matching earlier original request must exist in that peer's own history. A proposal or non-null reference alone is insufficient. Confirmation retains the original revision and planning fields; only operation and the separately approved owner reference may change. VERIFY retains planning identity. A booked request identity cannot be repurposed for another payload; another booking needs another actual request identity.

Optional semantic_proposal has exactly operation and parameters, where parameters contains every normalized request field except operation. It must equal the independently supplied typed request. semantic_capture has exactly version=football.semantic_capture.v01, origin (CONTROLLED_EVENT or AUTHORIZED_RUNTIME_CAPTURE), root_id, request, response, request_sha256 and response_sha256. The adapter verifies every binding, then consumes the proposed operation/parameters. The origin label is not authenticated proof of a live provider. The trusted runner must separately establish capture provenance for any authorized runtime contrast. Authoring makes no provider calls.

## Causal evidence

Venue PURE receives canonical TEXT request_json and inventory_json and returns canonical TEXT offer_json=E. A separate validator checks the real original inputs, field projection, all alternative/selected intervals, total and globally ranked complete solution. The original native evidence is retained. Only after that Work and source Root review does publication create B. FIND has B.booking=null and B.offer exactly E.

Requester retrieval uses persisted native LocalDRS metadata, a fresh resolver instance, native temporal evaluation, a local Root-reviewed SUMMARY_ONLY descent plan, and the explicit supplied PipeChannel bridge. Metadata begins as CONNECTOR_OBSERVATION; the subsequent accepted local context refers to its own Root. Foreign source IDs stay source references. No foreign Host, Root authority, callback, file path or executable object is reconstructed from JSON.

The requester calls public profile-aware check_pointer/check_bundle, with the independently pinned bootstrap keyset and local policy. Authenticated terminal STATUS entries are stored before current-use rejection. ImportStore is used for observation, highwater, conflicts, dedup and quarantine; its calibration-only validate_bundle is never used. Import candidate and disposition are separate immutable files. Duplicate evidence earns no independent-source credit.

After verified B/STATUS and recorded local use time, profile.context_from_checked derives exactly C={body:B,source_projection:S}. Native requester Work receives canonical original request and C. It preserves E's actual slots, price and currency. Its Root selects the actual requester artifact and claims exactly request_sha256=sha(request), offer_sha256=sha(B), result_sha256=sha(report without native_refs). Signed originals are retained outside C.

For FIND the publication Root selects the pointer and claims {pointer,source_review_ref}, subject=source record. Release selects the actual FETCH request and claims {request,pointer_ref,body_hash,source_review_ref}, subject=pointer. The signed release_review_ref comes directly from that actual release result.decision_id.

Confirmation retains the historical E, original producer Work and original source time. It publishes a distinct booking projection record after current consent/receipt review, with original source/review IDs in source_lineage_refs and producer_origin.json. Its original source review is separately retained. This record separation prevents a changed booking projection from masquerading as identical bytes under the same source record/revision. It is an explicit candidate interpretation of the historical-confirmation obligations in FOOTBALL_PROFILE.md (E and B; Selection And Event Semantics); the reviewer must assess it against the general original-source retention language in HOW_TO_BUILD.md section 6. No protected ABI change is requested.

## Protocol, bounds and currentness

Bootstrap sends only the public keyset over the operator-bound bootstrap PipeChannel using its existing POINTER frame kind. Each role checks the expected peer root and one key and pins that projection for the data channel. Private signer capabilities remain in their owning process.

A normal event exchanges DESCRIBE/POINTER, STATUS/STATUS, FETCH/BUNDLE and signed CLOSE/CLOSED. Each request is signed and binds the original task context, object, revision, nonce, deadline, purpose and local policy hash. The source authenticates with the separately pinned requester key and independently enforces its own release policy; a requester policy hash is not source permission. Existing frame kinds/canonical framing/256KiB checks/60-second stalled read ceiling are unchanged.

A history event uses signed UNAVAILABLE with a closed history/readback projection, then signed CLOSE. UNAVAILABLE has {request_ref,request_sha256,status,reason,history}; history has {booking,entry,native_key,readback_sha256,body_sha256,receipt_ref,request_sha256}. It contains neither a new offer body nor full source inventory/native trace. Both peers match saved booking identity with current source registry readback. Missing or inconsistent local history returns CURRENT_STATUS_UNKNOWN. The current source signature authenticates the readback projection, while the actual native receipt and registry stay at the source for independent review.

The source establishes PublisherBudget contexts before processing events. They bind requester, object, purpose, LOCAL_CONTEXT and the first declared source revision for each exact task. Repeated events reopen the same task counters; changed inventory does not reset them. The source reserves attempts before release review and disclosure bytes before constructing/sending a BUNDLE. Requester Budget limits two payload attempts, eight metadata observations, two accepted bodies and 128KiB accepted bytes. Eight ordered events require at most 32 requests including CLOSE. No service loop, automatic task splitting, retry on CONSUMED, redirects, recursive remote descent or arbitrary endpoint lookup exists.

Source life is min(valid_to,pt_created_at+ttl,source_observed_at+local_max_source_age), half-open. STATUS independently binds the FETCH and nonce and has checked_at <= use_time < min(valid_until,checked_at+60), with effective_at <= use_time. Final consumer review also remains inside those bounds. UTC observations are recorded separately from the native donor logical 1010..1014 clock. No ingestion, verification or later signature renews evidence.

## MOCK effect and recovery

The source checks consent, original offer, current source UTC/status/policy, inventory revision, tariff, occupancy and its local registry. Module-level callbacks are observed and admitted as MOCK_CONSEQUENTIAL. Business semantics map device_ref and canonical payload_json to the native action builder. The public donor creates the canonical logical-effect/idempotency binding, real Root preparation and current Host. Only dispatch_current_action_v01 may invoke execute_booking.

execute_booking repeats domain checks, atomically replaces one own registry.json containing all three slots and the native key entry, then reads it back. The output validator independently reads that snapshot and validates hashes/entry/slots. The source saves the actual native receipt and key mapping before optional reports. Host attempt, executor start, observed mutation and outcome are distinct. Candidate observations do not certify Firewall telemetry; the independent source-pinned observer owns that evidence.

An exact repeat reconciles the old native key, payload, packet, receipt and current registry entry. It performs no new Work, packet preparation or dispatch, including after offer expiry. Changed payload under that booked object refuses. VERIFY performs the same identity/readback checks with no new selection/effect. Consent/retrieval review is not revived from saved JSON.

A pending attempt with executor start and an unresolved outcome blocks blind retry. A documented no-executor-start attempt can undergo a fresh current review; prior evidence remains in its event directory. A failure after start reports CURRENT_STATUS_UNKNOWN, preserving stages, error and available readback. Unknown implementation/ABI/I/O errors are recorded and re-raised, not converted into a passing expected refusal. Mutation count can be null when start is observed but mutation outcome is unresolved. Requester-local zero effects never asserts source zero effects.

The normalized current source inventory must include previously committed source registry occupancy. If the next operator inventory omits it, FIND returns operator_inventory_missing_committed_occupancy/CURRENT_STATUS_UNKNOWN; the producer is never given an silently altered replacement for the independently recorded original inventory.

Compensation is NOT_APPLICABLE to this disposable single-snapshot mock. No arbitrary OS failure recovery, hostile-storage authenticity, cross-owner atomicity or real-world booking is claimed.

## Evidence index

All event files are under output_root/event_id and referenced by report.native_refs.

| Evidence | File |
| --- | --- |
| Original intake and observation | original_event.json, event_clock.json |
| Producer inputs, original computation | original_source_inputs.json, venue_work.json, native_attempt_venue.json |
| Source review | source_review.json; original_source_review.json and producer_origin.json for historical producer use |
| Publication | offer_body.json, manifest.json, descriptor.json, publication_review.json |
| Request and source release | received_request_N.json, release_review.json, bundle.json |
| Persisted resolution/descent | pointer_lookup.json, pointer_descent.json, pointer_review.json, descent_review.json, drs/ |
| Signed received originals/policy/time | retrieval_material.json, status.json, fetch_request.json, local_policy.json, local_use_time.json, consumer_use_time.json |
| Immutable import/review/disposition | import_candidate.json, import_review.json, import_disposition.json, dedup.json |
| Exact C and consumer Work/result Root | consumption_context.json, requester_work.json, native_attempt_requester.json, requester_review.json |
| Current consent and native action | consent_review.json, action_packet.json, action_root.json, action_admission.json |
| Actual native outcome and state | host_outcome.json, receipt.json, state_readback.json |
| Uncertainty / refusal | action_failure.json, refusal*.json, refusal_review.json, unhandled_failure.json |
| Authenticated terminal STATUS refusal | status_refusal_evidence.json (signed originals, local request/policy/highwater/check times), refusal_review.json (actual local Root), refusal.json (decision ID/evidence hash) |
| Repeated confirmation / VERIFY | history.json (source saved receipt/readback; requester saved identity plus signed readback) |
| Candidate accounting | observations.json, review_calls.jsonl, close.json, completion.json |

PipeChannel's supplied folder separately preserves raw sent/received canonical frames and reciprocal byte counters. Native Work files have exactly the generic required projection. Historical copies are marked and are not counted as new Work. observations.json counts adapter Root calls; kernel-internal Root/Firewall events and OS wait status belong to the trusted observer. Reports expose per-role counts, while detailed Work/search/transport/receipt/history accounting remains in observations and native artifacts.

State is private to each role: requests/ preserves original request history; offers/ is a latest immutable-archive pointer/projection; archives/ and accepted/ preserve bodies and original evidence; imports/ retains highwater/conflicts/quarantine; status/ stores source terminal entries; budgets/ and publisher_budget.json preserve reservations; bookings/ stores saved receipt bindings; attempts/ closes uncertain logical objects; registry.json is the source-owned MOCK business state. No state file is authority.

## Review and tests

tests/test_domain.py uses its own invented fixtures. It covers genuine/altered selection, permutation/ties, hard constraints, budget, adjacent and long-overlap intervals, consent-bound shifts, missing/duplicate inputs, unknown fields, bad arithmetic, missing output, context/source mismatch, half-open expiry, lawful continuation, native producer Work and native MOCK receipt/history. Tests have not run. Some pure schema tests use explicitly labelled syntactic IDs, never presented as native evidence.

dependencies.json pins exact directly imported approved modules and the original inventory/resource. The supplied dependency record measures Darwin Python 3.14.5, while EXECUTION_CONTRACT.md specifies Linux Python 3.14. The candidate follows the execution contract and claims no Linux execution observation. ZoneInfo requires the OS Europe/Tirane database entry; its availability/version is not established by the supplied dependency metadata. Missing it produces an observable setup failure; no dependency is installed or guessed.

The new code, callbacks, I/O and import closure need independent review, followed by separate native admission and a separately approved restricted run. Syntax inspection and package shape are data checks only. Runtime live semantic contrasts, timing races, arbitrary crash injection and Internet PKI remain untested and unclaimed. The reference native patterns come from the supplied numeric/DRS and attributed G50 MOCK donors; source remains unchanged under its supplied AGPL-3.0 license.
