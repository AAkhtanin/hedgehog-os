# External DRS — addressable evidence across owners

Engineering basis: `64f2b38b0d671e4907bae8649fff8f3d2ee0751c`.

<a id="D01"></a>

## D01 / External evidence became useful without changing who could decide

External DRS is the Gate 5 view of how one owner’s work becomes usable material for another owner. In the controlled calibration case, a source owner computes a correction; the receiving owner obtains an allowed fragment, checks its origin and current applicability, and consumes it in a different calculation. The football domain applies the accepted exchange with a different content profile. The result is a measured relationship between separate work, rather than two reports placed beside each other.

This dossier accompanies the engineering basis 64f2b38b0d671e4907bae8649fff8f3d2ee0751c. Its concrete evidence comes from the G52 lifecycle, the G54C numerical contract probe and the accepted G54D1 football program. Their roles differ: G52 demonstrates a two-process exchange and restart; G54C isolates representation and consumption; D1 demonstrates the authored domain. Historical checkpoints keep their original preparation status. They are interpreted through the later engineering admission, not silently rewritten.

The architectural point is that evidence and authority travel differently. A signed result can influence a receiving computation while its publisher retains control of disclosure and its recipient retains control of local use. Neither side becomes the other’s superior. Gate 5 establishes this finite reference with controlled data and pinned test identities. It does not claim a deployed public discovery network or production venue integration.

Sources:

- [docs/gate5_reference_contract_v01.md](https://github.com/AAkhtanin/hedgehog-os/blob/64f2b38b0d671e4907bae8649fff8f3d2ee0751c/docs/gate5_reference_contract_v01.md) — SHA-256 `138f77869fed786a219d5ad0ac6313d8a82fafd33e975f4f32057371a58960b5`
- [docs/gate5_reference_checkpoint_v01.md](https://github.com/AAkhtanin/hedgehog-os/blob/64f2b38b0d671e4907bae8649fff8f3d2ee0751c/docs/gate5_reference_checkpoint_v01.md) — SHA-256 `a4df63f63d2839c37e4c2a7449bc7f8089fc543649af7eab0457cb47e6fc9d75`
- [docs/gate5_lifecycle_restart_checkpoint_v01.md](https://github.com/AAkhtanin/hedgehog-os/blob/64f2b38b0d671e4907bae8649fff8f3d2ee0751c/docs/gate5_lifecycle_restart_checkpoint_v01.md) — SHA-256 `a1bec6f63ee7c8857c69e080536918d26af6459f28124876294fdc761488f843`
- [g54c: evidence/numeric/summary.json](../evidence/SOURCE_MAP.json) — SHA-256 `ed8a8c237322aa3b0ef2ae6dafd9945b74e09274ede87569a3abd2262e522f26`
- [g54d1: NATIVE_ACCEPTED.json](../evidence/SOURCE_MAP.json) — SHA-256 `684b28a43cfc27808876c7cdb6122a563b1d2c0182093c4a396de4d644385c5d`

<a id="D02"></a>

## D02 / The addressable structure is different from the material it describes

DRS names a semantic topology: relationships between experience, provenance, time, trust, conflicts and possible reuse. A rich local record can include the result of work, its supporting traces and the context in which it was valid. The addressable description helps another task discover which material might matter. It does not require every index to contain the owner’s complete archive, and it does not make an indexed record a local decision.

Four distinct places make the mechanism legible. First, the source owner holds the detailed material. Second, a descriptor and permitted metadata identify a bounded object in an address index. Third, an approved retrieval delivers a payload. Fourth, the receiver constructs a checked context for a particular Work. Metadata can contain an allowed summary; “pointer only” means the payload has not already been smuggled into the pre-retrieval index, not that the descriptor contains no information at all.

The historical architecture documents use a DNS-like analogy for semantic addressing. This is an explanatory analogy, not DNS wire compatibility. The G52 capture provides the narrower observable example: a persisted LocalDRS lookup exists before the body is received. The receiver may subsequently preserve an accepted fragment and its provenance locally. That useful retention is compatible with ownership remaining separate. It is not evidence that all participants share one global memory database.

Sources:

- [docs/passport_geometry_root_needles.md](https://github.com/AAkhtanin/hedgehog-os/blob/64f2b38b0d671e4907bae8649fff8f3d2ee0751c/docs/passport_geometry_root_needles.md) — SHA-256 `347ca55f3074106836c6646992cfdc18a2afefede199df1c1d2f9a4c6525cf70`
- [specs/human_passport_v0_25.md](https://github.com/AAkhtanin/hedgehog-os/blob/64f2b38b0d671e4907bae8649fff8f3d2ee0751c/specs/human_passport_v0_25.md) — SHA-256 `b229b6b08c5d3657258dbef315798a1686a845e4509926a2e839236dc7023324`
- [docs/strategic_expansion_map.md](https://github.com/AAkhtanin/hedgehog-os/blob/64f2b38b0d671e4907bae8649fff8f3d2ee0751c/docs/strategic_expansion_map.md) — SHA-256 `f1e2b0f11d3160f444ec23c56a6c4aed873a0d299f59e472ab24d0ea8dd9ee10`
- [g52: evidence/lifecycle_06/B/before_body.json](../evidence/SOURCE_MAP.json) — SHA-256 `ef5cbd8542bdc8e1c565f9b31c7677182845a8603534f7e3a1e28e9e79a54d8e`
- [docs/gate5_lifecycle_restart_checkpoint_v01.md](https://github.com/AAkhtanin/hedgehog-os/blob/64f2b38b0d671e4907bae8649fff8f3d2ee0751c/docs/gate5_lifecycle_restart_checkpoint_v01.md) — SHA-256 `a1bec6f63ee7c8857c69e080536918d26af6459f28124876294fdc761488f843`

<a id="D03"></a>

## D03 / Finding an address, receiving a body and using it have different grounds

A useful address starts a question: may this local task retrieve and use the referenced material? In the reference exchange, the requester’s local policy and Root review govern its own retrieval. The source separately authenticates the request and evaluates disclosure for the declared requester, object, purpose and use. Knowing a pointer therefore does not entitle the caller to its body. The source’s release decision does not decide the receiving owner’s subsequent computation.

The actual G52 peers have separate processes, local state, keys and Root reviews. They exchange signed messages through inherited OS pipes. The public trust configuration pins the expected identities; the received object cannot substitute its own trust anchor. Source, publication and release reviews have different subjects. On the receiver, retrieval, import and result review likewise bind different stages. The supervisor and examiner observe the experiment; they are not a third business owner above the two Roots.

The refusal contrasts make the division observable. A valid pointer can encounter a local refusal without a body fetch. An authenticated caller can also be refused by the publisher before body disclosure. These are different boundaries, with different counter evidence. Request scope and budget remain attached to the declared context. The successful neighbor then shows that a permitted fragment can enter useful work without turning either signature or remote acceptance into local permission.

### Who controls the next step

| Stage | Local question |
| --- | --- |
| Requester retrieval | May this task request this material? |
| Publisher release | May these bytes be disclosed to this caller and use? |
| Requester consumption | Is this evidence applicable to this current work? |

Sources:

- [docs/gate5_lifecycle_restart_checkpoint_v01.md](https://github.com/AAkhtanin/hedgehog-os/blob/64f2b38b0d671e4907bae8649fff8f3d2ee0751c/docs/gate5_lifecycle_restart_checkpoint_v01.md) — SHA-256 `a1bec6f63ee7c8857c69e080536918d26af6459f28124876294fdc761488f843`
- [g52: evidence/lifecycle_06/B/before_body.json](../evidence/SOURCE_MAP.json) — SHA-256 `ef5cbd8542bdc8e1c565f9b31c7677182845a8603534f7e3a1e28e9e79a54d8e`
- [g52: evidence/controls_04/result.json](../evidence/SOURCE_MAP.json) — SHA-256 `4623d5deff72971203b40be1b69cf6027655147d7dbeae5c97683d819e6cbd3e`
- [hedgehog/external_drs/gate5_lifecycle_supplied_v01.py](https://github.com/AAkhtanin/hedgehog-os/blob/64f2b38b0d671e4907bae8649fff8f3d2ee0751c/hedgehog/external_drs/gate5_lifecycle_supplied_v01.py) — SHA-256 `22419806c70631543f66c2d5894b6858e2f4462907277c8fddb025f32e329b88`

<a id="D04"></a>

## D04 / Evidence gained context without changing its original result

The shared contract separates three causal objects. E is the domain result extracted from a real producer Work. B is the later published representation: it contains the result together with source identity, revision, time and links to the completed Work and its review. C is the receiver’s consumption context, constructed after checking the exact publication, release and current signed status against local policy and the current request. Later checks can add information that did not exist when E was computed.

This ordering matters. A producer cannot return the identifier of its own future review as an already established fact. Nor can an earlier published body contain a later status observation. The correct condition is preservation of meaning across representations: payload_projection(B) equals E, and C retains B while adding independently derived context. In the football profile, B.offer is the produced offer and C.body is the published B. The objects have different roles and need not be byte-identical.

The examiner reconstructs expected C from original source inputs, the actual producer result and review, transmitted body, authenticated status, and independently held local observations. It then checks what the consumer truly received and returned. Copying the candidate’s own declared input into the expected input would only prove self-consistency. Gate 5 instead requires the causal joins. This general contract was corrected visibly after the earlier B1 mismatch; the old incomplete result remains part of the history.

Sources:

- [docs/gate5_authoring_kit_v01/SHARED_EVIDENCE_CONTRACT.md](https://github.com/AAkhtanin/hedgehog-os/blob/64f2b38b0d671e4907bae8649fff8f3d2ee0751c/docs/gate5_authoring_kit_v01/SHARED_EVIDENCE_CONTRACT.md) — SHA-256 `f8bd6f6b3be330a5ee816b76ddb5581d2cf39d43a28f3712ae85c722656c2886`
- [g54d1: review_finds.py](../evidence/SOURCE_MAP.json) — SHA-256 `8fdfc9409633c653f3a4b931ea0dba71cb07fab8f55d4c0759ba30a02ac6702b`
- [docs/gate5_reference_contract_v01.md](https://github.com/AAkhtanin/hedgehog-os/blob/64f2b38b0d671e4907bae8649fff8f3d2ee0751c/docs/gate5_reference_contract_v01.md) — SHA-256 `138f77869fed786a219d5ad0ac6313d8a82fafd33e975f4f32057371a58960b5`

<a id="D05"></a>

## D05 / A small numerical probe tested the common contract outside football

G54C exercised the E/B/C relationship with a deliberately small numerical example. The producer evaluates 3 × x + 2 for inputs 7 and 11, yielding 23 and 35. The numerical body carries this computed value and the original sample. After public component checks, the consumption context adds the checked request revision and source/status projection. The consumer computes B.computed + B.sample + request_revision. With revision 1, the actual results are 31 and 47.

The arithmetic is easy to inspect, but the causal requirement is stronger than arithmetic agreement. The published computed field must come from the recorded producer Work, its source Work and review references must match real records, and the status must belong to this pointer and request. A correct consumer calculation over a coherently fabricated context is still the wrong computation for the independently established input. The separate examiner checks that distinction.

The preserved probe includes nine negative controls: another signed payload, Work reference or review reference; stale or differently bound status; a missing consumed field; and altered context or result projection. They fail their corresponding predicates while the unchanged positive remains valid. These are recorded component and evidence controls. The probe used actual producer/review/consumer Work, but peer_io and effects are zero: it is not another two-peer exchange or an action authorization. Its value is isolating a reusable representation contract before applying it to the larger domain.

### Recorded numerical probe

| Input x | Producer 3x+2 | Consumer E+x+1 |
| --- | --- | --- |
| 7 | 23 | 31 |
| 11 | 35 | 47 |

Sources:

- [docs/gate5_authoring_kit_v01/SHARED_EVIDENCE_CONTRACT.md](https://github.com/AAkhtanin/hedgehog-os/blob/64f2b38b0d671e4907bae8649fff8f3d2ee0751c/docs/gate5_authoring_kit_v01/SHARED_EVIDENCE_CONTRACT.md) — SHA-256 `f8bd6f6b3be330a5ee816b76ddb5581d2cf39d43a28f3712ae85c722656c2886`
- [docs/gate5_authoring_kit_v01/example/numeric_context.py](https://github.com/AAkhtanin/hedgehog-os/blob/64f2b38b0d671e4907bae8649fff8f3d2ee0751c/docs/gate5_authoring_kit_v01/example/numeric_context.py) — SHA-256 `58355f7e8e8dbe626ed35d073b74e99adfdef964248606917d0e592369a38c6f`
- [g54c: evidence/numeric/summary.json](../evidence/SOURCE_MAP.json) — SHA-256 `ed8a8c237322aa3b0ef2ae6dafd9945b74e09274ede87569a3abd2262e522f26`

<a id="D06"></a>

## D06 / New external evidence changed 96 into 102 while the local rule stayed fixed

The separate G52 calibration story demonstrates actual external consumption. Owner A has a reference value and observations; Owner B has its own readings and assessment limit. A’s correction is reference minus the mean of its observations. At source revision 1, reference 100 and observations [110, 110, 110] produce −10. B’s readings [103, 106, 109] have mean 106. Applying the received correction in typed local Work produces 96, within B’s unchanged limit of 100.

At source revision 2, A’s observations become [104, 104, 104]. Its new native Work produces −4. B retains the same readings and local limit, obtains the new permitted source, and computes 102. The accurate assessment is now REVIEW_REQUIRED. A local Root can accept that faithful report without declaring the measurement within limits. Acceptance of a result and a favorable business assessment are distinct statements.

The saved 96 is not edited into 102. The second result has its own immutable source, lineage, adaptation and current review, while the first stays historical. The uncalibrated mean does not receive a canned correction; missing calibration is refused, and a separate input contrast produces 97. These are controlled numerical observations, not a physical sensor deployment. They show exactly what changed: the imported computed basis affected the receiving calculation, while the receiving rule and its earlier evidence remained intact.

### The local inputs and limit are unchanged

| Source revision | A observations | A correction | B result / limit |
| --- | --- | --- | --- |
| 1 | 110,110,110 | −10 | 96 / 100 |
| 2 | 104,104,104 | −4 | 102 / 100 |

Sources:

- [g52: evidence/lifecycle_06/B/r1/accepted.json](../evidence/SOURCE_MAP.json) — SHA-256 `77664a4a7a17f0b152156f9f32fddfc0e09b31660d9f5c2dc7c8e58c02b422af`
- [g52: evidence/lifecycle_06/B/r2/accepted.json](../evidence/SOURCE_MAP.json) — SHA-256 `c7cc992ba98e2c5c90288f12822e298c2bbe3f0f9a47929e6a1b1ec399ba1c1f`
- [docs/gate5_lifecycle_restart_checkpoint_v01.md](https://github.com/AAkhtanin/hedgehog-os/blob/64f2b38b0d671e4907bae8649fff8f3d2ee0751c/docs/gate5_lifecycle_restart_checkpoint_v01.md) — SHA-256 `a1bec6f63ee7c8857c69e080536918d26af6459f28124876294fdc761488f843`
- [g53: SUPERVISOR_EVIDENCE/calibration_controls/result.json](../evidence/SOURCE_MAP.json) — SHA-256 `b7f746149704e4ec3afd36428c46fa3982e7a60b21014ed216970e2f289c58c6`

<a id="D07"></a>

## D07 / Freshness belongs to the source, the status and the current use

The accepted external profile has an explicit interval for source usability. Its end is the earliest of valid_to, creation time plus TTL, and source observation time plus the receiver’s maximum allowed source age. A use must fall inside the half-open interval: valid_from ≤ use_time < end, with the source observation no later than use_time. Equality at the end is expired. Local ingestion cannot refresh the age of an old observation.

Status freshness is checked separately. The signed observation binds the pointer, publisher and status stream to the requester, request revision and nonce. Its checked_at must not be in the future, and use_time must precede both valid_until and checked_at + 60 in this finite profile. A current status cannot extend an expired source; a still-live source cannot supply a missing current status. The request and local policy introduce further applicability conditions.

The donor numerical Work uses its existing controlled logical clock; the external envelopes, current reviews and consumption use separately recorded integer UTC. This distinction avoids rewriting a kernel clock to make an example pass. In football, the civil date of a training session is another subject: a January calendar slot does not itself establish that today’s offer or status is current. Supplied verification checks the recorded use time. It does not renew historical evidence for a new action.

### Finite-profile validity rules

| Object | Required relation |
| --- | --- |
| Source | end = min(valid_to, PT+TTL, observed_at+max_age) |
| Use | valid_from ≤ use_time < end |
| Status | checked_at ≤ use_time < min(valid_until, checked_at+60) |

Sources:

- [hedgehog/external_drs/gate5_contracts_v01.py](https://github.com/AAkhtanin/hedgehog-os/blob/64f2b38b0d671e4907bae8649fff8f3d2ee0751c/hedgehog/external_drs/gate5_contracts_v01.py) — SHA-256 `db7602a402f67e7acea8dc4f566568b0a58004451ae95e64c999e553d6a02a8f`
- [docs/gate5_authoring_kit_v01/SHARED_EVIDENCE_CONTRACT.md](https://github.com/AAkhtanin/hedgehog-os/blob/64f2b38b0d671e4907bae8649fff8f3d2ee0751c/docs/gate5_authoring_kit_v01/SHARED_EVIDENCE_CONTRACT.md) — SHA-256 `f8bd6f6b3be330a5ee816b76ddb5581d2cf39d43a28f3712ae85c722656c2886`
- [docs/gate5_calibration_exchange_checkpoint_v01.md](https://github.com/AAkhtanin/hedgehog-os/blob/64f2b38b0d671e4907bae8649fff8f3d2ee0751c/docs/gate5_calibration_exchange_checkpoint_v01.md) — SHA-256 `376514709c9c60599ef9dba0b4496cbc645e401411906edc8aa89734db1778b7`
- [docs/gate5_lifecycle_restart_checkpoint_v01.md](https://github.com/AAkhtanin/hedgehog-os/blob/64f2b38b0d671e4907bae8649fff8f3d2ee0751c/docs/gate5_lifecycle_restart_checkpoint_v01.md) — SHA-256 `a1bec6f63ee7c8857c69e080536918d26af6459f28124876294fdc761488f843`

<a id="D08"></a>

## D08 / Revocation survived restart while earlier success remained readable

The lifecycle separates authenticating a status from deciding that it permits current use. A genuine terminal observation can be valid evidence precisely because it says the source is no longer active. In G52, the receiver authenticates and persists the REVOKED entry before refusing further current use. The high-water record belongs to that publisher, pointer and status stream; an older signed ACTIVE response cannot erase what has already been learned.

The restart is an actual process transition. B exits and is reaped while A remains alive. A new B process loads the existing pointer index, budgets, imports and history. The declared bootstrap repins the new B signer without exporting the previous private key, changing local policy or resetting task state. The previously saved ACTIVE response is then rejected as status_rollback. A later lawful source revision has a distinct pointer/status stream and supports a new reviewed result.

History answers a different question. Three ordinary historical queries preserve the earlier result and each perform one fresh local read review, with zero remote sends and zero new Work. The supplied verifier is more restricted still: it makes no new Root decisions. Neither path reactivates an old permission. The experiment proves the stated persisted restart behavior, not protection against rolling back an entire machine snapshot or losing durable state after power failure.

Sources:

- [docs/gate5_lifecycle_restart_checkpoint_v01.md](https://github.com/AAkhtanin/hedgehog-os/blob/64f2b38b0d671e4907bae8649fff8f3d2ee0751c/docs/gate5_lifecycle_restart_checkpoint_v01.md) — SHA-256 `a1bec6f63ee7c8857c69e080536918d26af6459f28124876294fdc761488f843`
- [g52: evidence/lifecycle_06/restart_checkpoint.json](../evidence/SOURCE_MAP.json) — SHA-256 `39a756fe7abde2a00a8eda6567669a4e35349ef11700f2038caacf4e722dff00`
- [g52: evidence/lifecycle_06/B/restart_old_active.json](../evidence/SOURCE_MAP.json) — SHA-256 `717fafa54d0e1845276608d0464996d5e30a3cb5f302a9c75d13901fad1e6128`
- [g52: evidence/lifecycle_06/B/terminal_observation.json](../evidence/SOURCE_MAP.json) — SHA-256 `18bd3fed81457d2643541725cec678772f34613f07507c14710f5fc166132241`
- [g52: evidence/proofs/supplied_03.json](../evidence/SOURCE_MAP.json) — SHA-256 `546d11a3f4d7787bf49373f80c751ff85ba89f8506124c5796d5a6b2ebb215d2`

<a id="D09"></a>

## D09 / Budgets and negative experience limit exploration without erasing lawful continuation

The source enforces its disclosure budget before constructing a permitted body response. G52 declares operator task contexts in advance, binding requester, object, purpose, permitted use and source revision. An arbitrary new label cannot create a fresh allowance. Reopening the budget helper loads the same durable state, and the exhausted original task remains exhausted after the requester restarts. Attempt reservation and body count/byte reservation protect different points in the sequence.

The baseline G52 task records twelve attempts: eight permitted metadata operations, two permitted payload attempts and two denied payload attempts. Two bodies were disclosed, totaling 2,146 bytes. The two additional authenticated fetches were refused at the publisher before body disclosure, including after its budget helper reopened. These are G52 transport figures, not football counters. The refusal boundary is before disclosure of a body, not before every form of I/O.

Negative experience also stays scoped. An unavailable current status becomes UNKNOWN rather than assumed ACTIVE or an eternal blacklist. A known revocation blocks its current source stream; a lawful new source can support continuation under new review. Duplicate delivery leaves one source and one history record with zero credit at that point. This is bounded deduplication, not a global reputation algorithm. The broader DeadEnd concept can organize failure experience, but the measured claim here remains the specific refusal, history and continuation relationships in the capture.

### G52 baseline task accounting

| Counter | Recorded value |
| --- | --- |
| Attempts | 12 |
| Permitted metadata / payload | 8 / 2 |
| Denied payload | 2 |
| Disclosed bodies / bytes | 2 / 2,146 |

Sources:

- [g52: evidence/lifecycle_06/A/publisher_budget.json](../evidence/SOURCE_MAP.json) — SHA-256 `7adb42fd1c27ab82da04eba41d1bc6396673a5382e944ed76efc4acc87a757e0`
- [g52: evidence/lifecycle_06/B/dedup.json](../evidence/SOURCE_MAP.json) — SHA-256 `da06e484aedbe88d92c31686b020a0c39efb5f974ed61170a97f3e4dad156512`
- [g52: evidence/lifecycle_06/B/status_unavailable.json](../evidence/SOURCE_MAP.json) — SHA-256 `1d21daaf1b7ebaf57e78cea562605fab506342c733be1fb1ea18df66c121451e`
- [docs/gate5_lifecycle_restart_checkpoint_v01.md](https://github.com/AAkhtanin/hedgehog-os/blob/64f2b38b0d671e4907bae8649fff8f3d2ee0751c/docs/gate5_lifecycle_restart_checkpoint_v01.md) — SHA-256 `a1bec6f63ee7c8857c69e080536918d26af6459f28124876294fdc761488f843`
- [docs/gate5_reference_evidence_v01/acceptance_matrix.json](https://github.com/AAkhtanin/hedgehog-os/blob/64f2b38b0d671e4907bae8649fff8f3d2ee0751c/docs/gate5_reference_evidence_v01/acceptance_matrix.json) — SHA-256 `04bedd3790cc0aba71a543e143bfa944cf34fe6c9c0a3683877ab8ffc3fee920`
- [docs/strategic_expansion_map.md](https://github.com/AAkhtanin/hedgehog-os/blob/64f2b38b0d671e4907bae8649fff8f3d2ee0751c/docs/strategic_expansion_map.md) — SHA-256 `f1e2b0f11d3160f444ec23c56a6c4aed873a0d299f59e472ab24d0ea8dd9ee10`

<a id="D10"></a>

## D10 / The negative controls reach different semantic boundaries

The F01–F20 inventory is a map of questions, not twenty interchangeable success labels. Some answers come from the actual G52 lifecycle: a pointer before a body, independent refusals, changed local conditions, terminal-state persistence, unknown status, deduplication and restart. Others come from coherent signed component mutations or bounded state controls. A correctly signed but semantically wrong object must reach the intended scope or arithmetic boundary rather than fail only because its JSON is broken.

The evidence distinguishes a tampered byte sequence from a signed wrong calculation, a foreign recipient from an unknown signer, and an expired observation from a rollback of status revision. Positive neighbors remain important: the same allowed object or lawful continuation must still succeed. Missing imported fields and the recorded result 97 provide causal checks against a receiver returning a fixed answer regardless of its actual input.

G53’s forty-three affected default controls support the later body-profile seam; they remain recorded stage evidence, not newly executed G55 tests. G55 preserves the exact historical G52 source for its supplied proof and checks the accepted D1 source separately. This prevents a newer contract being silently substituted into an old collection. The inventory is finite. Pure altered-evidence controls do not certify physical crashes, arbitrary concurrency, hostile Python execution or an internet-wide discovery service.

### F01–F20 evidence families

| IDs | Boundary / principal method |
| --- | --- |
| F01–F03, F18 | Lookup, separate refusals and restart / recorded native lifecycle |
| F04–F06, F13 | Integrity, signed scope/arithmetic, identity / component controls |
| F07–F12 | Request, time, policy, status and conflicts / mixed native and pure |
| F14, F16–F17 | No executable authority; bounded size, route and depth / pure controls |
| F15 | Duplicate source/history accounting / recorded lifecycle |
| F19 | Consumed-input dependence / missing-field control plus native97 |
| F20 | Private-note absence / recorded public-byte canary scan |

Sources:

- [docs/gate5_reference_evidence_v01/acceptance_matrix.json](https://github.com/AAkhtanin/hedgehog-os/blob/64f2b38b0d671e4907bae8649fff8f3d2ee0751c/docs/gate5_reference_evidence_v01/acceptance_matrix.json) — SHA-256 `04bedd3790cc0aba71a543e143bfa944cf34fe6c9c0a3683877ab8ffc3fee920`
- [docs/gate5_lifecycle_restart_checkpoint_v01.md](https://github.com/AAkhtanin/hedgehog-os/blob/64f2b38b0d671e4907bae8649fff8f3d2ee0751c/docs/gate5_lifecycle_restart_checkpoint_v01.md) — SHA-256 `a1bec6f63ee7c8857c69e080536918d26af6459f28124876294fdc761488f843`
- [g52: evidence/controls_04/result.json](../evidence/SOURCE_MAP.json) — SHA-256 `4623d5deff72971203b40be1b69cf6027655147d7dbeae5c97683d819e6cbd3e`
- [g53: SUPERVISOR_EVIDENCE/calibration_controls/result.json](../evidence/SOURCE_MAP.json) — SHA-256 `b7f746149704e4ec3afd36428c46fa3982e7a60b21014ed216970e2f289c58c6`
- [docs/gate5_reference_evidence_v01/source_bindings.json](https://github.com/AAkhtanin/hedgehog-os/blob/64f2b38b0d671e4907bae8649fff8f3d2ee0751c/docs/gate5_reference_evidence_v01/source_bindings.json) — SHA-256 `a782a2600911b0adcd272793c0449e267c6c1de4942ef3dfad06a1cc86b97832`

<a id="D11"></a>

## D11 / The saved work can be checked without performing it again

The installed proof command is demo/verify_gate5_reference_v01.py with a new output directory outside the repository. It checks pinned installed sources and portable evidence, reconstructs the recorded author’s text operations, and starts two explicitly selected pure verifier subprocesses. One verifies historical G52 evidence with its exact historical contracts. The other verifies the accepted D1 native and live captures. It does not start the candidate, peers, author, provider, new Root decisions, native Work or effects.

Two G55 preparation processes independently produced the same 37,389-byte canonical result, with SHA256 d2a25ed3b1ab123912e59d096808351dbcf18f59a16229b9abcaff9f647eacff. Their component outputs also match the accepted recorded G52 and D1 results. The G52 consumer checks signed wires, actual Work/result structures, Root relationships, source revisions, history and restart. The D1 consumer checks its frozen cases and observed boundary records. Hash agreement is one layer; the selected semantic verifiers perform the relational checks.

The trust profile includes exact reviewed reference code, runner and observer, operator-pinned inputs and keys, and the independent examiner. Signed bytes are not encrypted transport, and test keys do not establish the identity of a real venue. The same-user IPC experiment does not claim resistance to an OS administrator. Verification reads evidence and launches pure processes; calling that zero OS activity would be misleading. This publication inspects existing evidence rather than collecting another execution.

### Recheck the admitted evidence

| Requirement | Value |
| --- | --- |
| Entry | demo/verify_gate5_reference_v01.py --output /absolute/new/external/proof |
| Runtime | Python3.12+ with sys.monitoring and project dependencies |
| Class | Historical G52 and accepted D1 supplied verification |

Sources:

- [demo/verify_gate5_reference_v01.py](https://github.com/AAkhtanin/hedgehog-os/blob/64f2b38b0d671e4907bae8649fff8f3d2ee0751c/demo/verify_gate5_reference_v01.py) — SHA-256 `2852dda26988804f665181374ae9d2a44d96d395808f038707db4f02b7b63c22`
- [docs/gate5_reference_evidence_v01/closure/comparison.json](https://github.com/AAkhtanin/hedgehog-os/blob/64f2b38b0d671e4907bae8649fff8f3d2ee0751c/docs/gate5_reference_evidence_v01/closure/comparison.json) — SHA-256 `a520a683f97c4d093c827af85ffa2e0103ca8d28434af666a93d2de8b712efdf`
- [hedgehog/external_drs/gate5_lifecycle_supplied_v01.py](https://github.com/AAkhtanin/hedgehog-os/blob/64f2b38b0d671e4907bae8649fff8f3d2ee0751c/hedgehog/external_drs/gate5_lifecycle_supplied_v01.py) — SHA-256 `22419806c70631543f66c2d5894b6858e2f4462907277c8fddb025f32e329b88`
- [g52: evidence/proofs/supplied_03.json](../evidence/SOURCE_MAP.json) — SHA-256 `546d11a3f4d7787bf49373f80c751ff85ba89f8506124c5796d5a6b2ebb215d2`
- [g54d1: SUPPLIED/one.json](../evidence/SOURCE_MAP.json) — SHA-256 `0eba67d7652765c387988d760cd5daeeacecbdf33b9dc577dbe6a1cad40ed4b0`
- [docs/gate5_reference_contract_v01.md](https://github.com/AAkhtanin/hedgehog-os/blob/64f2b38b0d671e4907bae8649fff8f3d2ee0751c/docs/gate5_reference_contract_v01.md) — SHA-256 `138f77869fed786a219d5ad0ac6313d8a82fafd33e975f4f32057371a58960b5`

<a id="D12"></a>

## D12 / Independent systems could cooperate through addressable experience

The next architectural step starts with the measured relationship, not an assertion that a global network already exists. Gate 5 showed two owners, bounded addresses, permitted payloads, currentness checks, real consumption and preserved history. A wider system could let organizations publish limited descriptions of verified experience or capabilities so that another task can find relevant material before deciding whether to request it.

Consider an illustrative future collaboration. A venue exposes a description of its available services; a laboratory describes an evaluation method; a supplier publishes a validated maintenance procedure. A task can discover the related addresses, request the necessary fragments and use them under its own local policy. No participant has to deliver its entire archive or become the common authority. The example describes an extension path, not an existing customer, integration or public catalogue measured in Gate 5.

A searchable public DRS would still need concrete discovery rules, routing, profile compatibility, identities, disclosure policies, budgets and cycle limits. Those deployment choices cannot be inferred from a working two-peer bridge. The point of the reference is to make their boundary visible: an address can introduce evidence, while each owner separately controls what is disclosed and what is done with it. The observed connection should be drawn solid; wider discovery and federation should be drawn as explicitly future connections.

Sources:

- [docs/passport_geometry_root_needles.md](https://github.com/AAkhtanin/hedgehog-os/blob/64f2b38b0d671e4907bae8649fff8f3d2ee0751c/docs/passport_geometry_root_needles.md) — SHA-256 `347ca55f3074106836c6646992cfdc18a2afefede199df1c1d2f9a4c6525cf70`
- [docs/strategic_expansion_map.md](https://github.com/AAkhtanin/hedgehog-os/blob/64f2b38b0d671e4907bae8649fff8f3d2ee0751c/docs/strategic_expansion_map.md) — SHA-256 `f1e2b0f11d3160f444ec23c56a6c4aed873a0d299f59e472ab24d0ea8dd9ee10`
- [docs/gate5_reference_contract_v01.md](https://github.com/AAkhtanin/hedgehog-os/blob/64f2b38b0d671e4907bae8649fff8f3d2ee0751c/docs/gate5_reference_contract_v01.md) — SHA-256 `138f77869fed786a219d5ad0ac6313d8a82fafd33e975f4f32057371a58960b5`
- [docs/gate5_reference_evidence_v01/acceptance_matrix.json](https://github.com/AAkhtanin/hedgehog-os/blob/64f2b38b0d671e4907bae8649fff8f3d2ee0751c/docs/gate5_reference_evidence_v01/acceptance_matrix.json) — SHA-256 `04bedd3790cc0aba71a543e143bfa944cf34fe6c9c0a3683877ab8ffc3fee920`

<a id="D13"></a>

## D13 / New meaning is produced by work and can become new addressable experience

DRS can connect existing experience to a new task, but the index itself does not generate a new conclusion. The performing Work creates the new result. Its source relationships and local review establish how that result was obtained and how it may be used. If the owner’s publication policy permits, a bounded description and supporting material can then become available to another task. This closes a conceptual loop between activity, memory and later activity.

The architecture allows rich experience behind an address. A future artifact might contain a detailed trace or a fuller fractal snapshot with the relationships needed to understand an outcome. The historical passport describes boundary snapshots as addressable experience. That concept should not be confused with the small calibration payload actually transferred in G52, or with permission to execute a serialized tree. Richer representation increases what can be inspected; it does not inherit the producer’s right to act.

The observed calibration revisions offer a small foothold for this direction. A new source supports a new conclusion while its predecessor remains historical, with explicit lineage instead of silent replacement. Extending that pattern across domains would require suitable content profiles and validation for each meaning. The future promise is therefore cooperative accumulation of useful, attributable experience. It is not automatic truth, universal trust or a claim that every recorded trace can be safely reused in every later context.

Sources:

- [specs/human_passport_v0_25.md](https://github.com/AAkhtanin/hedgehog-os/blob/64f2b38b0d671e4907bae8649fff8f3d2ee0751c/specs/human_passport_v0_25.md) — SHA-256 `b229b6b08c5d3657258dbef315798a1686a845e4509926a2e839236dc7023324`
- [docs/passport_geometry_root_needles.md](https://github.com/AAkhtanin/hedgehog-os/blob/64f2b38b0d671e4907bae8649fff8f3d2ee0751c/docs/passport_geometry_root_needles.md) — SHA-256 `347ca55f3074106836c6646992cfdc18a2afefede199df1c1d2f9a4c6525cf70`
- [docs/strategic_expansion_map.md](https://github.com/AAkhtanin/hedgehog-os/blob/64f2b38b0d671e4907bae8649fff8f3d2ee0751c/docs/strategic_expansion_map.md) — SHA-256 `f1e2b0f11d3160f444ec23c56a6c4aed873a0d299f59e472ab24d0ea8dd9ee10`
- [g52: evidence/lifecycle_06/B/r1/accepted.json](../evidence/SOURCE_MAP.json) — SHA-256 `77664a4a7a17f0b152156f9f32fddfc0e09b31660d9f5c2dc7c8e58c02b422af`
- [g52: evidence/lifecycle_06/B/r2/accepted.json](../evidence/SOURCE_MAP.json) — SHA-256 `c7cc992ba98e2c5c90288f12822e298c2bbe3f0f9a47929e6a1b1ec399ba1c1f`

<a id="D14"></a>

## D14 / Descriptions of capabilities can travel while admission remains a separate act

Addressable material can describe what a service is able to do: its inputs and outputs, required confirmations, allowed actions, receipts, versions and revocation conditions. A consumer could inspect such a description and use a capability at its owner’s service without downloading that service’s implementation. If a new local implementation is needed, the resulting candidate must follow a separate source review and admission path. A discovered description is not an executable import instruction.

This distinction connects the External DRS view to independent authoring. Gate 5 separately demonstrated construction of a football program from a bounded kit and its later engineering admission. It did not demonstrate a runtime discovering a service, spawning an author and installing the resulting program automatically. The accepted local body-profile seam is selected in reviewed code; a foreign payload cannot name a Python module and appoint it as its own validator.

The accepted naming map makes later directions explicit. Reflective Improvement Radiolaria concerns lessons and improvement proposals from experience. Cross-Domain Transfer Radiolaria concerns structural analogies and transfer candidates. Capability Synthesis Factory concerns an integrated requirements, code and sandbox cycle. These directions, global discovery and broader federation remain deferred after Gate 6 publication. They are future proposal mechanisms, not additional authorities. The current result is a concrete foundation: a useful result can become addressable beyond its producing system while ownership, current permission and local admission remain explicit. Cognitive Radiolaria is also a deferred umbrella direction, not a completed Gate 5 subsystem.

### Separate extension paths

| Path | Boundary |
| --- | --- |
| Use an external capability | Service remains at its owner; current local permission required |
| Create a local implementation | Candidate undergoes separate review and admission |
| Discover wider experience | Future discovery, identity and profile infrastructure |

Sources:

- [docs/strategic_expansion_map.md](https://github.com/AAkhtanin/hedgehog-os/blob/64f2b38b0d671e4907bae8649fff8f3d2ee0751c/docs/strategic_expansion_map.md) — SHA-256 `f1e2b0f11d3160f444ec23c56a6c4aed873a0d299f59e472ab24d0ea8dd9ee10`
- [hedgehog/external_drs/gate5_body_profile_v01.py](https://github.com/AAkhtanin/hedgehog-os/blob/64f2b38b0d671e4907bae8649fff8f3d2ee0751c/hedgehog/external_drs/gate5_body_profile_v01.py) — SHA-256 `7e434e75d1913a7fab71ebc882fb21640fd33e7324ff035bc376a4b7cd65d89f`
- [docs/gate5_reference_contract_v01.md](https://github.com/AAkhtanin/hedgehog-os/blob/64f2b38b0d671e4907bae8649fff8f3d2ee0751c/docs/gate5_reference_contract_v01.md) — SHA-256 `138f77869fed786a219d5ad0ac6313d8a82fafd33e975f4f32057371a58960b5`
- [docs/gate5_reference_evidence_v01/acceptance_matrix.json](https://github.com/AAkhtanin/hedgehog-os/blob/64f2b38b0d671e4907bae8649fff8f3d2ee0751c/docs/gate5_reference_evidence_v01/acceptance_matrix.json) — SHA-256 `04bedd3790cc0aba71a543e143bfa944cf34fe6c9c0a3683877ab8ffc3fee920`

