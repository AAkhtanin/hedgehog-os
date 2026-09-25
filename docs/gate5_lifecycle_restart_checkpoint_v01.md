# G5-2 Lifecycle and Restart Checkpoint

Status: `G52_LIFECYCLE_RESTART_READY_FOR_INDEPENDENT_REVIEW`.
`COLD_AUTHOR_ENVIRONMENT=PENDING`; `OWNER_ADMISSION=NOT_PERFORMED`;
`GATE5=NOT_CLOSED`. The G51 checkpoint remains historical and unmodified.
Basis: main `76a6952c9d0f31c976d2501c5641457a20de153a`.
This additive external proposal grants no Root permission or admission.

## Source Correction

The G51 publisher checked its aggregate counters after sending. Its recorded
positive transcript stayed within bounds; that did not prove source enforcement.
`gate5_exchange_v01.PublisherBudget` now reserves authenticated attempts durably
before release review, then reserves body count/bytes before constructing a
permitted response. Denied attempts and refused responses are distinct from
disclosed bytes. Reopening the helper uses the same persisted state. The finite
single-writer profile is not a concurrent service or power-loss certification.

G52 declares three operator contexts before execution: revision-one local use,
an AUDIT-only refusal control, and revision-two local use. Each binds requester,
object, purpose, allowed use and source revision. An arbitrary task label cannot
create a context; an approved control label cannot reset the first task's budget.
The exhausted first task remains exhausted across B's restart. The source opens
at most two bodies/128 KiB and accepts at most two payload/eight metadata attempts
per established task. Attempt/denial totals continue to record prohibited calls.
Request envelopes, frame size and cumulative read-acceptance bounds remain.

The old fixed five-message loop is replaced by finite sessions (maximum 32
requests), signed close and clean boundary EOF handling. Truncated frames fail.
The G51 producer entrypoint uses the corrected source boundary too; it was not
recollected as a second baseline. Its historical capture remains on G51 bytes.

## Actual Controlled Story

The final G52 `lifecycle_06` uses real independent A and B processes, keys,
public PURE Work and local Root reviews, persisted LocalDRS and inherited pipes.
A's first Work derives -10 from reference100/[110,110,110]; B consumes that
received offset in typed Work and obtains 96 for readings[103,106,109]/limit100.
The uncalibrated mean106 receives INSUFFICIENT_EVIDENCE, not a canned answer.

B stores one accepted history record. Actual duplicate delivery leaves one
source, one history record and zero credit. Two additional authenticated fetches
bypass B's budget and are refused by A before disclosure, including after A's
budget helper reopens. Baseline totals: 12 attempts, eight permitted metadata,
two permitted payload, two denied payload, two bodies/2146 bytes. The separate
AUDIT refusal discloses zero bytes. There is no reputation-credit algorithm.

A signs an unavailable observation, later ACTIVE, then REVOKED at revision2.
Authentication/storage is separate from ACTIVE eligibility. The terminal entry
is persisted before refusing current use. B exits and is reaped; a genuinely new
B process loads its existing pointer index, budgets, imports and history. A stays
alive. A trusted bootstrap explicitly repins B's fresh signer without exporting
the old private key, changing policy or resetting task state. Saved ACTIVE is
rejected as rollback. Revision-two pointer's independent status stream starts at1.

A then derives -4 from reference100/[104,104,104] in new native Work. B receives
the new immutable source through current review and computes102. Its independent
Root ACCEPTs the accurate REVIEW_REQUIRED assessment, not a within-limit claim.
Changed policy and readings between import and use each receive a real Root
refusal before Work. The unchanged lawful neighbor still completes. Historical96
bytes remain exact, with new102 as a separate record and explicit lineage.

Three ordinary historical LocalDRS queries each make one fresh local read review
and zero remote sends/new Work. This is distinct from the supplied proof, which
makes no Root decisions at all. Donor Work uses logical1014; external source,
status, current reviews and consumption use observed integer UTC. Source end
remains min(valid_to, PT+TTL, source_observed_at+max_age), half-open; ingestion
does not renew it. Status freshness is independent. No kernel clock is patched.

## Bounded F01-F20 Map

All paths below are relative to the final capture unless prefixed `controls`.
Actual means fresh G52 execution recorded in `lifecycle_06`; pure mutations use
that immutable evidence and explicitly declared hostile signer/test pins.

| Case | Evidence and scope |
| --- | --- |
| F01 | Actual `B/before_body.json`: pointer-only LocalDRS snapshot, no quarantine/body. |
| F02 | Actual `B/local_policy_refusal.json`, `local_denial_counters.json`: no fetch. |
| F03 | Actual signed AUDIT refusal in `B/session1/events.json`, `A/releases/`: no body. |
| F04 | Fresh G51 affected controls on final source: altered integrity/signature refused. |
| F05 | `controls_04`: coherent hostile-signed wrong domain, unit, recipient; valid neighbor. |
| F06 | Fresh G51 affected controls: signed incorrect arithmetic, not only signature failure. |
| F07 | Wrong request revision rejected; actual source task/use/revision bindings preserved. |
| F08 | Fresh G51 pure exact expiry, source-observed/freshness and no ingestion renewal controls. |
| F09 | Actual `B/changed_policy`, `changed_dependency`: refused before Work; observed deltas. |
| F10 | Actual terminal storage/restart rollback; pure SUPERSEDED and reopened-state controls. |
| F11 | Coherent signed status/content equivocation quarantined; valid components first. |
| F12 | Actual CURRENT_STATUS_UNKNOWN, no permanent blacklist, later lawful continuation. |
| F13 | Hostile signer/pointer-key substitution refused; no foreign Root permission transfer. |
| F14 | Signed extra authority/command/import fields refused by closed shape; no execution. |
| F15 | Actual `B/dedup.json`: one source/history/zero credit; final two legitimate revisions. |
| F16 | Pure oversize/frame/path controls and unsupported route; no HTTP safety claim. |
| F17 | Coherent valid pointer reaches route cycle/hop validator; one-hop neighbor passes. |
| F18 | Actual processes/restart checkpoint, persisted lookup, history and new local reviews. |
| F19 | Missing calibration refused; native input contrast97; no missing-field fallback. |
| F20 | Actual observed public-byte canary scan has zero matches; private body/hash excluded. |

## Supplied Proof and Cost

The independent operator pin file is outside the peer capture. Two new supplied
processes verify identical evidence and produce byte-identical canonical reports.
Public crypto, ABI/PURE and Root input/result structural validators bind exact
selected Work, local request/policy/dependencies, adaptation and source revision.
They do not decide Root or claim full native canonical replay/current authority.
An authenticated Root record from revision1 cannot stand in for revision2 merely
because another summary says102. Tests reach that relationship after explicitly
updating test-fixture pins; accepted evidence/pins remain unchanged. Wrong external
pins and missing evidence also fail. Recorded canary scan is not a fresh private scan.

Final collector process: 3.527335 s including imports/startup/observation.
Focused script: 0.799019 s, 39 G52 rows and 43 affected G51 controls (not pytest
node counts). Supplied processes: 0.829784 and 0.880707 s; forbidden runtime calls
zero and report-only writes. Supplied adversarial controls: 1.246714 s. These are
observations of one finite scenario, not scaling or latency guarantees. Failed
development attempts and source-bound receipts remain in the return.

## Review Boundary and Continuation

No owner or protected kernel/ABI/Root/Host/Firewall/admission file changed.
R1 compatibility is static path classification only; no context was fabricated.
Transport is signed, not encrypted; no OS-admin isolation or production PKI is
claimed. Keys remain in process memory. The source/capture is not new authority.
The G50 denied nested sandbox was not retried. P7 concerns that tested environment,
not every possible cold-author method; it remains pending under separate review.

Stop at this return. G53 kit/examiner setup, G54 cold-author execution, football,
mock-effect receipt/readback closure and owner admission are not started here.
A future effect lane must reconcile saved receipts without redispatch of CONSUMED
packets, reject changed payload under one logical key and use readback for uncertain
history. This master-aware session is not the independent cold author, and no
football solution belongs in a future generic kit. No provider/cloud/QPU calls,
business effects, installation, broad Living/Conformance, staging, commit or push.
