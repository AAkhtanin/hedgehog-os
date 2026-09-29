# Different Domains, the Same Continuing Activity

Computing, assembled around intent, becomes useful when a person's activity crosses the boundaries of an individual answer or application. A purchasing review needs warehouse facts and counterparty conditions. Travel requires several owners to agree without acquiring one another's authority. Access to a service can expire while its purchase history remains correct. Local monitoring must distinguish missing knowledge from an absent hazard. These are different practical questions about one organization of activity, not interchangeable demonstrations of a universal capability.

Radiolaria is an execution kernel for supported profiles, not a bootable replacement for the host operating system. Available capabilities contribute proposals, computation, observations and results; their participation does not settle the decisions belonging to their owners. The application team still supplies domain contracts, adapters and validators. The cases below show where useful work changes and where obligations remain. They do not establish zero integration cost or an unchanged kernel across all development history.

This chapter is an editorial reading of saved sources at accepted owner commit `2e965ecb18e545e428380eb8e9aa5a7037a388be`, inspected on 27 September 2026. No execution was repeated. Source IDs such as X-S-REPORT and X-ATLAS resolve to repository paths, hashes and exact JSON pointers in [the source ledger](../references/cases/source_ledger.json). A label such as LIVE, MODEL or FRESH inside an older artifact describes that artifact's origin, not this inspection.

## CASE-SUPPLIER: Make the Permitted Part Useful

The Water Filter question is whether Supplier A's mock-payment path can proceed while Supplier B and shipment evidence remain unresolved. The subject is concrete: warehouse inventory, supplier availability, insurance and contract status, invoice/PO reconciliation, and bank policy. A payment slot describes availability, not permission. The bounded workflow brings these sources into review rather than asking one model to declare the whole transaction successful.

The S1 safe report records six Gemini calls at execution head `e1fe7bfc44fe482814b1957840b6d8c434cad5c6`. Their semantic contributions are advisory. Corrected evidence changes the basis for another local evaluation; it does not rewrite the first Root decision. Explicit human approval then narrows the action to Supplier A. Runtime and validators, not the semantic branches, own the packet and Corridor transitions. Supplier B's blockage and the shipment hold survive that progress.

**Worked inset: a correction is not an approval.** In X-S-INDEX, `/scenario_rows/0/root_status` is `NOT_READY`; row 2 is `SUPPLIER_A_SCOPED_REVIEW_READY`, but its `packet_status` is still `ABSENT`. Row 3 changes the packet to `ROOT_CREATED_SCOPED`. Row 4 records `corridor_status="PASS"` and `receipt_status="EVIDENCE_ONLY"`. The integrated row 8 retains `supplier_b_status="BLOCKED"`, `shipment_status="HELD"` and `business_outcome="MIXED"`. These fields separate useful progress from an all-business approval.

The lawful neighbor is the scoped Supplier A mock path. The adverse neighbor, row 5, has `root_status="NO_ACTION_APPROVAL"`, `packet_status="REJECTED"` and `supplier_a_status="NOT_EXECUTED"`. This demonstrates a meaningful alternative, not a system that merely refuses everything. Business actors provide different evidence and consent; the public projection does not justify inventing a named independent Root for every warehouse or legal branch.

The six historical provider calls must not be counted again for deterministic correction, packaging or replay. Real payment and shipment release are false in X-S-REPORT. Its useful result is a checked, inspectable partial business outcome. The later Atlas Supplier learner is another profile and another history, discussed below; it is not a continuation silently appended to this Water Filter run.

## CASE-AIRLINE: Coordinate Without a Superior Owner

Airline changes the composition of ownership. The customer wants a suitable trip; the airline controls its offer and ticket-side decisions; the bank controls its payment-side decision. Exchanging bounded evidence permits coordination without making any participant a business SuperRoot.

Two-domain attempt 04 records a PAR-to-LIM transaction for 12 August 2026 and twelve historical Gemini calls. The client reviewer's safe summary recommends offer 001 because it is EUR24 cheaper and includes a window seat, while reporting that both offers meet the hard constraints. This is a recorded semantic recommendation, not an independently established current fare. The resulting `selected_offer_id` is `offer:mock_airline_al:PAR-LIM:001`.

**Owner-view inset.** X-A-REPORT `/root_finals/0/safe_projection/root_owner` is `root:client_os_001`; positions 1 and 2 are `root:mock_airline_al` and `root:mock_bank_a`. Their dependency lists differ. The airline final references its hold and ticket packets and receipts; the bank final references `bank_payment_authorization_ref:mock_bank_a:001`. The client purchase receipt depends on the ticket receipt, bank authorization reference and client intent. This is evidence exchange among separately owned decisions, not a single final decision copied three times.

The BSEP projections likewise have `authority_created=false` and `permission_created=false`. After the owners' bounded decisions, the Corridor projection records one execution with `mock_only=true` and zero real-world effects. Three receipt projections retain `authority_class="evidence_only_receipt"`. The useful outcome is a coordinated mock transaction with attributable evidence, not an actual airline booking or bank settlement.

The separate full-stack claim matrix preserves a failed package and a distinct recovery package in C22-C23. Those historical audit-backed claims are a legitimate adverse neighbor, but they are not events inside attempt 04. C24 also records `signature_verified=false`; replay consistency must not be advertised as signature verification. The common story is that more participants and variable semantic wording can coexist with separate local decisions. It is not a demonstration that arbitrary counterparties can be integrated automatically.

## CASE-TESTFLIX: Keep History Without Extending Access

Testflix asks what remains useful when a subscription, session, device grant and current consent have different lifetimes. Its Atlas profile is `INCIDENT_ATLAS_TESTFLIX_AT3_V01`, with authored controlled responses and native mock effects. User, provider, bank and device Roots remain distinct. Favorable experience can change the review Work considered next, but cannot purchase another period for the user.

**Temporal inset.** X-ATLAS `/testflix/clock_law` specifies integer logical UTC seconds, trusted evaluation at `handler.now+4`, and validity only while evaluation is strictly less than `valid_to`. The useful continuation's session spans `1790115592` to `1790115652`; the recorded main evaluation is `1790115596`. At exact deadline `1790115652`, T2's expiry branch records `host_current_action_not_executable` and `executor_delta=0`. DeviceRoot withdrawal produces the same outer refusal. These are separate controlled branches, not claims that the main successful START happened after expiry.

The paid entitlement remains distinct: T2's unchanged period has `price_minor=500`, `renewal="EXPLICIT_ONLY"`, and `valid_to=1792707572`. T1 supplies changed terms of `amount_minor=700` in an independent unconsumed Bank branch and records no executor call. Its scope explicitly says the changed-price purchase was not executed and no fresh E was produced. A historical payment receipt remains evidence; T3's `payment_period_already_consumed` prevents using it to extend the period again.

Experience has a practical consequence. The saved before/after Work outputs change `provenance_checked` from true to false in the selected review, while actual playback still consumes a bound Work result under current checks. `/testflix/consumption/material/operation` is `testflix.playback.v01`, its `work_artifact_ref` is concrete, and the downstream output is `playback_state="PLAYING"` with `executor_delta=1`. A wrong-Work substitution has delta zero. This is changed selected Work, not permission to omit every provenance or currentness obligation.

T4's no-consent Root result is `NEEDS_USER`; explicit consent yields `ACCEPT` in a review-only neighbor. The useful executed continuation is START within an existing paid period, not that review becoming a new purchase. One predictive observation and one consumer support this profile. Four Testflix cards do not constitute four independent learners.

## CASE-SENTINEL: Work With the Knowledge Actually Available

Sentinel makes changing world observations and incomplete knowledge visible. Its owner needs local assessment without pretending that an old event becomes fresh when delivered again, that related sensors are independent, or that optional intelligence must always answer before useful local work can proceed.

The LS2R2 public safe package contains a concrete contrast between reference checking and reserve-history investigation. Its recorded actor with intended role `LOCAL_SLOPE_ANALYST` actually has `actual_mode="CLOUD_LLM"`. That is not an installed local SLM. In the consumed-results derivative, composition 0 selects `REFERENCE_INTEGRITY`; composition 1 selects `INDEPENDENT_RESERVE_SERIES`.

**Knowledge-quality inset.** Composition 1's check records `fitness="ELIGIBLE"`, `measured_span=20`, `range_value=150`, three sample IDs and an actual receipt reference. Its declared policy requires three samples, minimum span 20 and maximum range `1000` micrometers. The result is `BOUNDED_CONSISTENT`, not a landslide prediction. In composition 0, spatial checking explicitly leaves `physical_mapping="NOT_ESTABLISHED"`. Its Root acceptance still has `permission_created=false`. More informative computation is not physical certification or automatic signal authority.

The source/claim indices separately identify local-algorithms-only DRS continuation without model transport. That historical external member was not reopened here; the ledger preserves its archive and member hashes instead of claiming raw inspection. The older C03 controlled record describes missing primary data as LIMITED and missing reserve data too as INSUFFICIENT. Earlier live contrasts remain `VALID_LIVE_CONTRAST_NOT_DEMONSTRATED` or `NOT_DEMONSTRATED`.

A different, fully available Atlas profile supplies the optional-worker neighbor. `/sentinel/continuation/optional_profile` is `CONTROLLED_BARRIER_STUB`; while `waiting/pending_alive=true`, `waiting/signal/signal=true`. Its consumed diagnostic has `creates_permission=false`; separate native Root checks justify the signal. Three mock effects cover ON, local report queue and OFF, with `outbox_deliver=0`. Independent recovery witnesses occur at scenario ticks 4030, 4045 and 4060. The late semantic answer is refused for `role_current_context`. This establishes bounded useful continuation, not measured cloud timeout behavior or a real-time safety guarantee. These scenario ticks are not LS2R2 export timestamps or provider latency measurements.

## CASE-INCIDENTS: Test a Boundary and Its Lawful Neighbor

The Incident-to-Proof Atlas is a methods view of useful activity, not Radiolaria's entire identity. It maps reported risk mechanisms to finite local controls. Its saved external-source catalog distinguishes incidents, exploit demonstrations and requirements. For example, E08 maps an untrusted public-issue/private-disclosure mechanism to local scope controls; E10 uses payment-protocol requirements as context, not as a reported vulnerability. Those catalog entries were recorded on 23 September; this chapter did not revisit their websites or reproduce their external systems.

**Boundary inset.** Atlas S1 changes the proposed recipient to `supplier:B`, with `amount="10"` and `recommendation="PROCEED"`. Its boundary records `stage="ROOT"`, `quality="UNSAFE"`, `enforcement="BLOCKED_AS_REQUIRED"`, `effects=0`, and null packet and Firewall fields. It would be inaccurate to call this a Firewall rejection. The lawful CONTINUE observation proposes `supplier:A`, keeps amount `"10"`, cites `policy:confirmed`, and records `native.consumed_work_ref="work_results:ecd9f80d53c29a8a0223723aa97e81a9c0ddc89bf6baa52727010f60362c7920"`. Current Work selects `supplier.review_provenance.v01`. The comparison connects a refused proposal to useful, source-bound continuation.

The scope labels matter. S1 is `DIRECT_CAUSAL`. Testflix T4 is `SHARED_DOMAIN_PROOF`: its current-consent control shares a domain consumer, not a new learning chain for every card. Supplier S4 is `SHARED_DOMAIN_PROOF_POST_CONSUMER_CONTROL`; the source explicitly says its supplemental delivery controls occurred after the consumer and were not its cause. Twenty cards therefore represent five consumers and seven effective history samples, not twenty independent confirmations of every invariant.

Independent AT5 source-and-saved-evidence review accepted the declared finite engineering scope while recording zero test reruns and zero model calls. Its existence is recorded independent checking, not a fresh audit by this writer. Supported replay is `SAFE_DERIVED_SAVED_RELATIONS_NOT_LIVE_AUTHORITY`; native graph replay remains `UNSUPPORTED_NATIVE_SCHEMA`. Neither replay nor a digest supplies current authorization.

## Return to the Whole System

These five axes explain why available capabilities can participate in one continuing activity: they exchange bounded material while preserving the distinctions between proposal, consumed Work, applicable evidence and local decision. Their useful results are deliberately different: partial supplier progress, coordinated mock travel, still-valid playback, bounded local assessment and lawful continuation beside refused input. A mixed or incomplete result can be the correct answer to the person's actual conditions.

Football shows how a changed request becomes another owner's applicable input. Wedding separates semantic interpretation from numerical computation and original-condition checking. EWS preserves unaffected work while its environment changes. G3/G4 connects eligible experience to later scrutiny and expenditure; external authoring separates creation from examination and admission. Together with the five cases here, these relationships explain how supported intent becomes actual activity. Each case retains its own sources, clock and scope. Their common organization gives integrators a starting point, not evidence that every domain already supports every relationship.


## Inspect the Recorded Fields

[source_ledger.json](../references/cases/source_ledger.json). [source_field_projections.json](../references/cases/source_field_projections.json).

Source routes: [X-S-REPORT](../PAPER_SOURCE_KEY.md#x-s-report); [X-S-INDEX](../PAPER_SOURCE_KEY.md#x-s-index); [X-A-REPORT](../PAPER_SOURCE_KEY.md#x-a-report); [X-A-MATRIX](../PAPER_SOURCE_KEY.md#x-a-matrix); [X-LS-PROJECTION](../PAPER_SOURCE_KEY.md#x-ls-projection); [X-ATLAS](../PAPER_SOURCE_KEY.md#x-atlas); [X-AT-REVIEW](../PAPER_SOURCE_KEY.md#x-at-review).

## Compare Architectural Relations

The [ten-by-ten case matrix](../CASE_MATRIX.md) compares consumed semantics, composition, currentness, memory, provenance, local authority, effects/history, computational environment, experience/resource choice and external creation/admission. Each evidential cell names a source selector, method, status and limit. Twenty-three cells are not demonstrated by the inspected records; this is no claim that the implementation lacks those mechanisms. Five two-relation panels keep comparison readable without converting the cases into a green status score.

## Where the Incident Atlas Questions Came From

The Incident-to-Proof Atlas did not originate in the later Australian incident. Its accepted source catalog links fifteen risk families P01-P15 to twenty cards across five domains. It distinguishes fifteen E01-E15 incident/research/requirement/project-context entries from four M methodology records. I denotes a reported incident, E a published experiment, R a requirement; E/R and P/R preserve mixed roles. E15 is accepted project/local-requirement context, not a fifteenth independent external incident. The current [catalog](../references/current/external_sources.json) and [case routes](../references/current/CASE_ROUTES.json) are exact Git-A sources, freshly read as documents, not re-executed experiments.

| Published mechanism and catalog IDs | Question translated into a bounded local control | Lawful continuation and exact route |
| --- | --- | --- |
| Anthropic cybersecurity-evaluation incidents, July 30, updated August 3, 2026 (E01) | Does available connectivity falsely expand task scope? A1/S1/S2/D2 distinguish scope, account and source boundaries. | Use only admitted local operations and matching sources; E01 atlas_mappings and CASE_ROUTES named cards. This is not reproduction of those compromises. |
| OpenAI compaction/deception, credentials, cross-sample communication and disclosure reports (E02-E07, E13) | Can a summary, source mismatch or convenient public channel become authority? W4/D1 preserve records; S1-S3 check source/account; W1 checks disclosure. | Return to actual records and an authorized destination. E06 is verified through its parent announcement item, not the unopened child report. |
| Invariant GitHub MCP, Cato EchoLeak/DuneSlide and tool-poisoning research (E08/E09/E11/E14) | Can untrusted retrieved material steer private access or execution? A4/S2/W1/W2 separate useful data from permission. | Consume bounded evidence without inheriting instructions or authorizing publication; exact E-record mappings retain their narrower limits. |
| AP2 authorization requirements and AISI evaluation research (E10/E12) | Are the purchase, price, account and observed outcome tied to the actual decision? T1-T4/S3/S4 require current permission and independently observed records. | Make a newly reviewed lawful operation or report refusal. AP2 is requirements context, not an alleged protocol vulnerability. |

These are engineering translations into inspectable finite controls, not external exploit replays, endorsements or measured protection rates. The Australian account in chapter 12 is additional context, never the Atlas origin or a newly reproduced attack. [OR-ATLAS](../PAPER_SOURCE_KEY.md#or-atlas)

## Research-Informed Sentinel Requirements

The accepted [Sentinel research map](../references/current/research_context_v01.json) contains twelve references and ten explicit mappings. It distinguishes published operational challenges, our software criteria, recorded contrasts and exact internal evidence locators. Three examples make that translation concrete:

| Published challenge | Engineering criterion and recorded response | Exact accepted mapping and limit |
| --- | --- | --- |
| R04: Bertorelle et al., EGU26-10345, Rotolon, Italy; storms/power/visibility interrupt monitoring | Distinguish primary loss, usable reserve and insufficient evidence. C03 becomes LIMITED, then INSUFFICIENT; S3 permits bounded local continuation. | matrix row 2 -> C03/S3 -> D02,D05. Controlled inputs, not reproduction of the researchers' virtual sensor. |
| R07: Environment Agency rainfall measurement interval differs from delivery frequency | Preserve observed versus received time, interval, units and purpose. C02 rejects fresh arrival as evidence of current measurement. | matrix row 6 -> C02 -> D02,D03,D06. Real EA capture retains unknown endpoints; HTTP success proves no gauge-to-slope mapping. |
| R10: Badoux et al., Illgraben; multiple surges complicate alarm duration | Require measured recovery rather than silence or expiry. C07/S5 uses a fresh sequence and a separate OFF. | matrix row 9 -> C07/S5 -> D02,D03. Synthetic recovery thresholds, not a transferred field-performance result. |

The full map is available here; D03/D05/D06 refer to named historical return members. Their exact locators are preserved, but raw members not carried into this review are RAW_NOT_INSPECTED in this hop. The research authors did not set Radiolaria's thresholds or endorse the implementation. There is no Nepal-conference creation story, installed physical local SLM, or geological certification. [OR-SENTINEL](../PAPER_SOURCE_KEY.md#or-sentinel)
