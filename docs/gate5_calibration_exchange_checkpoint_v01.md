# G5-1 Calibration Exchange Checkpoint

Status: `G51_CALIBRATION_EXCHANGE_READY_FOR_INDEPENDENT_REVIEW`.
`COLD_AUTHOR_ENVIRONMENT=PENDING`; `Gate5=NOT_CLOSED`.
This is an external additive source proposal, not owner admission or permission.
Basis: main `76a6952c9d0f31c976d2501c5641457a20de153a`.
Master V02 SHA256:
`008cbad1773e116568833ff3e97decce8d73a4dca6e7826fcf40268f11271fef`.

## Implementation and Evidence

- `hedgehog/external_drs/gate5_contracts_v01.py`: closed immutable canonical
  carriers, exact bounded arithmetic, public native signature verification,
  independent policy/source checks, half-open source and status validity.
- `gate5_native_v01.py` in that directory: actual public PURE Work, actual local
  Root reviews and persisted LocalDRS resolution with current Root descent.
- `gate5_exchange_v01.py`: signed request/release/status over inherited OS pipes,
  separate peer state/keys, durable attempted-operation reservations and separate
  address/quarantine planes. No PURE executor performs transport I/O.
- `gate5_supplied_v01.py`: independent expected-pin verification and public crypto,
  ABI and PURE invocation/result validation. Recorded Root relationships are
  checked, not restored as authority or claimed as full native canonical replay.
- `demo/run_gate5_calibration_v01.py`: a finite two-process collector taking two
  separately declared scenario files; the bootstrap contains no expected answer.
- `tests/test_gate5_calibration_exchange_v01.py`: a finite script, not an invented
  pytest phase inventory. Its oracle is separate from the collector.

The final capture is `exchange_05` in the G51 return. A owns reference 100 and
observations [110,110,110]; its actual Work derives n=3, sum=330, offset=-10/1.
B owns readings [103,106,109] and limit 100. Without calibration its mean 106
has INSUFFICIENT_EVIDENCE; the received correction is adapted into actual typed
Work input, producing 96/1 and a current B Root WITHIN_REFERENCE_LIMIT review.
A's source, publication and release reviews are distinct. Foreign ACCEPT never
replaces B's decision. The immutable import precedes its separate disposition.

Final collector process: 2.004671 s including imports/process startup; internal
two-peer interval: 1.473489 s. B's corrected Work: 0.106637 s. Actual transport:
five requests, five responses, 9,096 framed B-to-A bytes and 12,049 A-to-B bytes;
three metadata/status attempts, two body attempts, one body opened, 1,073 body
bytes. A's authenticated AUDIT refusal and B's local pre-body refusal are observed
with counters. Forty-three focused controls pass, including a new typed-input
contrast yielding 97, signed incoherent arithmetic refusal and rational -2/3.
Two independent supplied processes take 0.563684 and 0.504170 s including imports;
their deterministic reports are byte-identical and observed collection calls zero.

## Exact Boundaries

The donor Work uses its admitted controlled logical clock (1014). The external
source envelope, request/status deadlines and current local reviews use integer
UTC sampled during execution. No source lifetime is renewed by local ingestion:
end=min(valid_to, PT+TTL, source_observed_at+local_max_age), with t<end.
Status has fresh request-bound nonces, checked_at<=t<min(valid_until,checked_at+60).
Current policy/source/status are rechecked at consumption. The local descriptor
context is capped to the same source end. Replay checks the recorded use time;
it does not make that historical capture current today.

Signed bytes are not encryption. These same-user IPC peers are not isolated from
an OS administrator. Private key material never leaves process memory; private
canary bodies and their hashes are excluded from the return. Actual public bytes
are scanned for leakage. B reads only its own state and the IPC body, not A's
observation file. The operator's separate key/policy/bootstrap pins are a finite
trust setup, not production discovery or PKI. Fresh collections need not have
identical signatures, IDs or timestamps.

Bounds: two peers, one hop, one pointer/one body in this run (caps four pointers,
eight records and sixteen lineage refs), pointer 16 KiB, body 64 KiB, frame 256 KiB,
JSON depth 12; at most two payload attempts/eight metadata attempts, two opened
bodies and 128 KiB cumulative body bytes. Attempt reservation precedes I/O and
reopening the budget helper does not reset it. Full process-restart persistence
and the complete F01-F20 campaign have not been executed.

The human DRS summary excludes opaque digest text. The full signed descriptor is
still stored and verified; a content fingerprint binds the exact metadata. This
fix preserves the existing privacy filter rather than encoding around it.

## Review and Continuation

No existing tracked path, kernel, schema, R1 guard/binder, owner index or registry
is changed. The seven new paths fit the unchanged ENGINEERING path restrictions
at `tools/reviewed_repository_transition_v01.py::_kind_rules`. This is static
path compatibility only: no R1 context was fabricated or finalized. Native
evidence is not source admission, Root permission transfer or a Gate closure.

G50 remains limited preflight evidence. Its denied nested sandbox did not execute
the child, and its earlier false isolation label remains preserved with its
correction. P7 must be independently resolved before final kit freeze or the
cold-author/evaluator trial. The denied sandbox was not rerun.

Next, only after separate authorization: G52 lifecycle/refusal/restart work,
including revision-two history, status revocation/high-water persistence,
conflicts, replay/current-use distinctions and the remaining finite negatives.
G53/G54 must later reconcile saved mock receipts without redispatch of CONSUMED
packets, reject changed payload under one logical key and use readback for
uncertain effect history. Football, cold author, production PKI, LLM/cloud/hardware
calls, business effects, broad Living/Conformance, commit and push are not run.

## Reproduction Without Recollection

The return's `expected_capture.json` is an operator-side expected pin set outside
the peer capture, bound to the collector's preexecution source receipt. Reviewers
must authenticate that file independently, not trust pins supplied by a peer.
Use the admitted basis plus the seven proposed postimages and the existing Python
dependencies. `run_supplied.py CAPTURE EXPECTED_PINS SOURCE_ROOT REPORT` verifies
the saved capture with no Work, Root decisions, Host dispatch, fetch or DRS writes.
For a separately authorized new collection, the demo takes an absent output
directory and a directory containing A.json/B.json scenario inputs; it generates
fresh private keys and uses actual processes. Do not use a historical JSON capture
as current authority. The return preserves all failed/intermediate attempts and
their exact source-bound receipts rather than promoting them to final PASS.
