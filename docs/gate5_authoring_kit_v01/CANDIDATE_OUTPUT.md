# Candidate Output Contract G54D V01

## General Package Rules

This version clarifies producer selection, release linkage and event-stage evidence.
See SHARED_EVIDENCE_CONTRACT.md. Package limits and native authority are unchanged.

Return one directory accepted by `candidate_contract.py`. Never include a complete
source snapshot, .git, owner context, private keys, caches, dependencies, symlinks,
hardlinks or examiner files. The checker reads files as data; acceptance of shape
is not permission to execute. Maximum32 regular files/1MiB total/256KiB per file.

Required files:

```text
candidate.json
PASSPORT.json
README.md
dependencies.json
source_impact.json
candidate_domain/__init__.py
candidate_domain/run.py
candidate_domain/profile.py
schemas/body.schema.json
tests/test_domain.py
```

Additional files only under candidate_domain/, schemas/ or tests/. Modules must
not execute at import. `candidate.json` has exactly version=`g53.candidate.v01`,
candidate_id (bounded lowercase identifier), installable_now=false,
entrypoint=`candidate_domain.run`, and files=[{path,bytes,sha256}]. List every file
except the manifest itself exactly once. Hash actual UTF-8/byte contents, not a
reformatted model answer. Use safe canonical relative POSIX paths. Absolute paths,
`..`, backslashes, extra unlisted files and duplicated JSON keys are refused.

PASSPORT.json contains all of these nonempty fields, with concrete values:

| Field | Required meaning |
| --- | --- |
| needle_id, owner, version | Candidate identity, accountable code author, version. |
| purpose, domain | Finite purpose and excluded tasks; not universal planning. |
| input_schema, output_schema | Exact local schema paths/versions and normalization. |
| actor_roles, execution_modes | Independent local roles and PURE/MOCK-only modes. |
| capabilities, forbidden_effects | Exact local public symbols/operations and explicit exclusions. |
| permission_policy, risk_class | Current local consent/review, effect owner and bounded risk. |
| drs_scope | Per-owner address, quarantine, accepted/history namespaces. |
| sealed_slot_refs | Actual dependencies, or NOT_APPLICABLE plus reason; no fabricated slot. |
| adapter_requirements | Typed code/source/capability and transport assumptions. |
| time_currentness_dependencies | Clock profiles, half-open bounds and invalidation inputs. |
| failure_policy | Named refusals, unknown state, retry/stop and finite budgets. |
| compensation | Concrete behavior or NOT_APPLICABLE with reason/limits. |
| audit_provenance | Source/Work/Root/packet/receipt and consumed-field bindings. |
| tests, compatibility | Own tests, public mechanisms and supported boundaries. |

dependencies.json declares the exact imported local modules and installed packages,
their versions/source hashes, filesystem operations and possible subprocess/network
access. No installation recipe is permission to install. source_impact.json lists
new files, public APIs used and any requested source changes. Protected changes are
not allowed; do not bundle an altered kit/source checker to make your code pass.

The original G53 self-spawning CLI is superseded BEFORE the first G54 trial by
this exact precreated-peer entrypoint in `candidate_domain/run.py`:

```text
def run_peer_v01(*, role: str, input_data: dict, state_root: pathlib.Path,
                 output_root: pathlib.Path, channel: PipeChannel,
                 bootstrap: PipeChannel) -> dict | None:
    ...
```

Read EXECUTION_CONTRACT.md for exact role/input/channel/completion semantics.
Only a separately reviewed restricted runner may execute it. The trusted parent
creates the two peers BEFORE loading any candidate. Candidate fork/exec/threads
are forbidden; do not spawn a coordinator or subprocess. Each role reads only its
own assigned input/state and communicates through the provided channels. The
parent supplies no offer/selection/booking answer. Outputs are disposable evidence,
with no writes to kit/source/exam. The inert package manifest remains g53.candidate.v01;
its entrypoint module remains candidate_domain.run. The native requirements below
are unchanged. Candidate files may be submitted as text; the trusted transport
packager computes sizes/hashes mechanically without changing their semantics.
## TASK-SPECIFIC PROFILE: Football

The following names are not universal runtime primitives. They apply only with
WHAT_TO_BUILD.md and FOOTBALL_PROFILE.md. The general contract is E -> B -> C;
the exact football payload/context projections and provenance obligations are in
FOOTBALL_PROFILE.md, which must be read with these field declarations.

The domain's own normalized request schema must preserve the TASK brief's fields;
the examiner uses the following interoperable projection:

- request_id, revision, operation, team_ref, venue_ref, timezone, currency,
  budget_minor, owner_approval_ref (null unless actual controlled owner consent),
  sessions=[{session_id,start,end,allow_shift_minutes}]. Local start/end are ISO
  strings without offset and timezone is explicit; maintain their original values.
- Inventory belongs to the source role and declares revision, venue_ref, currency,
  fields with field_id, surface, full_size, price_minor, available_utc and occupied_utc.
  UTC interval arrays are half-open integer seconds, distinct from offer freshness.
- Runtime semantic proposals are untrusted proposed mode/parameters. Their original
  request/response and local capture bindings are evidence, never permission.

Produce `report.json` with exactly version=`g53.result.v01`, request_ref,
request_revision, team_ref, operation, status, slots, total_minor, currency, source,
receipt_ref, counts, native_refs. Status is OFFER_READY, NEEDS_CONFIRMATION,
NO_COMPLETE_OFFER, MOCK_BOOKED, VERIFIED, CLARIFY, REFUSED or CURRENT_STATUS_UNKNOWN.
Each slot has session_id, venue_ref, field_id, start_utc, end_utc, price_minor.
Counts has search, dispatch, mutations, observed rather than guessed.
Pre-action refusal has empty slots and no claimed completed booking. Count an
actual rejected Host attempt as an attempt, even when the executor never starts.
Zero effects is not the same as zero attempts. If failure occurs after executor
start, preserve the real state and CURRENT_STATUS_UNKNOWN with no blind retry;
do not fabricate zero mutations or a clean REFUSED result. The actual receipt,
stage observations and readback decide what is known. See FOOTBALL_PROFILE.md.

The source projection contains publisher, recipient, request_revision,
schedule_revision, offer_revision, observed_at, valid_from, valid_to, ttl, pt,
status, status_checked, status_until. Keep the full original signed envelope and
native TimeEnvelope in separate evidence; this projection never substitutes for
cryptographic, scope or time validation. native_refs points to actual saved
identities/files, not invented values. No Root or Host authority is deserialized.

Use the generic Work evidence projection demonstrated by G52 native_work:
native_evidence={admission,invocation,result}, inputs, outputs, attempts,
results and artifact. New domain PURE capabilities use TEXT request_json and
inventory_json on the source side, returning TEXT offer_json; the requester uses
TEXT request_json and offer_json, returning TEXT result_json. Source offer_json is
canonical(E); requester offer_json is canonical(C), NOT canonical(B) or canonical(E).
Values are canonical closed JSON strings. The native producer/consumer must really
compute/consume them. PublishedEvidence B is created only after source Work/review;
B.offer == E and C.body == B, with C.source_projection defined by the public profile.
result_json is canonical report excluding native_refs to avoid an identity cycle.
The final local Root claim binds request_sha256=sha(request), offer_sha256=sha(B)
and result_sha256=sha(report_without_native_refs), selecting the actual requester
Work artifact. In particular offer_sha256 is neither sha(E) nor sha(C). Preserve
original source/review IDs. Keep producer, publication/release and consumer reviews
separate; signatures alone do not establish their semantic relationship.

The trusted reviewer may collect independent source-pinned call counters, I/O and
native returns. Candidate-provided summaries cannot certify those observations.
Booking additionally requires actual packet/current Host dispatch/receipt and
state readback at the source owner. VERIFY returns saved identity/readback without
new search or dispatch. Own tests are necessary, not the examiner or source admission.
