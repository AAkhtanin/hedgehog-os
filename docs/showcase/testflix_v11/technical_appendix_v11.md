# Testflix — Technical Appendix

**Radiolaria / Hedgehog OS · Accepted implementation V11 · 13 September 2026**

This appendix explains the evidence behind the Testflix showcase. It separates what was executed with real model responses, what was executed against controlled business effects, and what the owner finally committed. The accepted implementation is [`e42d37fa98dfec7110b8cf75b1aceaa614f461be`](https://github.com/AAkhtanin/hedgehog-os/commit/e42d37fa98dfec7110b8cf75b1aceaa614f461be).

The compact evidence map is [evidence/evidence_map.json](evidence/evidence_map.json). Each included original has its archive member name, byte length and SHA-256. Large histories are referenced by their exact archive identities rather than silently truncated. Selected-field extracts are explicitly identified as extracts.

## 1. The demonstrated result

Testflix is a finite subscription lifecycle executed through the common Hedgehog OS machinery. Real Gemini outputs select between supplied subscription plans. The selected result is consumed by typed work and by independent decisions for the user, bank, provider and device. A mock payment receipt becomes an input to entitlement issuance; the entitlement and current device grant become inputs to playback.

The main story covers purchase, an informational request, stop and fresh-session behavior, expiry, and explicit renewal. Separate controlled P04 branches exercise actual public E recomputation when a quote changes. A later live A/B changes the preference while preserving the other request fields, obtains a different plan, and consumes that result through payment and playback. Captured execution reproduces the A/B on fresh Hosts without calling the model.

The final owner execution applied 51 paths to `main`: 31 modifications and 20 additions. It retained 896 other tracked files, producing 947 tracked files. The historical V09 branch remains at `268f22a7940068fd58e00e6f96dc2d13a7d71890`. The owner phase is `PUSHED`, with no blocker. The agreed implementation/admission scope was independently accepted.

Evidence: [owner state](evidence/sources/owner/state.json), [actual A/B](evidence/sources/v10/actual_AB_01/final.json), [main result](evidence/sources/v09/live_main_02/story/result.json).

## 2. Four reasoning duties, four independent Roots

The live semantic provider is **Gemini 2.5 Flash**. Four duties use the configured model; this is not a claim of four different model families. Each receives an ordered projection of its request and prior contributions.

| Semantic duty | Consumed information | Returned contribution |
|---|---|---|
| Intent interpreter | Explicit preference, currency and ceiling | Priorities and any missing required evidence |
| Provider terms analyst | Request, finite catalogue and intent | Plan facts and budget eligibility |
| Client plan selector | Intent and analysed terms | A selected plan with decision factors |
| Contract reviewer | The same contract and all preceding contributions | Support or a blocking disagreement |

A model output does not contain payment authority. Local code binds each output to its request, projection, role and transport record. The fourth duty can disagree: the preserved A/B refusal did so. A disagreement is not overwritten with a successful controlled response.

The reasoning duties are distinct from the four Root decisions:

| Root | Identifier | Responsibility shown here |
|---|---|---|
| UserRoot | `root:testflix:user` | Accept the user's purchase selection |
| BankRoot | `root:testflix:bank` | Review the payment against current terms and consent |
| ProviderRoot | `root:testflix:provider` | Authorize entitlement issuance using the payment receipt |
| DeviceRoot | `root:testflix:device` | Authorize playback within session and device constraints |

The actual A/B consumption record contains four accepted Root decisions with different decision IDs and target Root IDs. The same four Hosts remain throughout that branch's purchase, information, stop and fresh-session history. An independent captured run creates fresh Hosts.

Evidence: [semantic checkpoint](evidence/sources/v10/actual_AB_01/semantic_checkpoint.json), [consumption](evidence/sources/v10/actual_AB_01/consumption.json). Source: [`semantic_roles_v01.py`](https://github.com/AAkhtanin/hedgehog-os/blob/e42d37fa98dfec7110b8cf75b1aceaa614f461be/hedgehog/domains/testflix/semantic_roles_v01.py), [`lifecycle_v01.py`](https://github.com/AAkhtanin/hedgehog-os/blob/e42d37fa98dfec7110b8cf75b1aceaa614f461be/hedgehog/domains/testflix/lifecycle_v01.py).

## 3. Purchase, reuse and explicit renewal

All stored amounts are integer **minor currency units**: `500` means EUR 5.00, not EUR 500. The catalogue contains three plans: EUR 5.00 at 720p without advertising, EUR 6.00 at 1080p with advertising, and EUR 9.00 at 2160p without advertising. Under the initial EUR 6.50 ceiling, the third is ineligible.

| Stage | Observed behavior | Payment implication |
|---|---|---|
| P01 — purchase | AD_FREE selects `plan:cd79`, EUR 5.00, 720p, no advertising | One main mock payment |
| P02 — information | Admissible stored results answer an informational request | No new provider call or business effect |
| P03 — session lifecycle | Stop and a fresh session use the existing paid period and current device authority | No second purchase |
| P05 — expiry | At and after the entitlement boundary, the old right cannot authorize a new start | Zero effect in the exact-boundary controls |
| P06 — renewal | New explicit EUR 7.00 consent permits a new payment and paid period | Main total becomes two |
| After renewal | Stop and fresh-session behavior preserve the four Hosts and paid-period history | Main total stays two |

Eight real model calls contribute to the successful main history: four for the purchase and four for renewal. The cumulative development journal is a different count, discussed below. No actual bank, streaming provider or physical television was operated.

The expiry controls evaluate a request at the boundary and immediately after it, with `executor_delta=0` and reason `current_entitlement`. Historical replay still verifies the old record. This distinguishes a historical fact from a currently usable permission.

Evidence: [main result and phase durations](evidence/sources/v09/live_main_02/story/result.json), [exact boundary](evidence/sources/v09/bank_story_06/tests/actual_T3/P05_boundary.json), [after expiry](evidence/sources/v09/bank_story_06/tests/actual_T3/P05_after.json), [post-renewal control](evidence/sources/v09/bank_story_06/tests/actual_T3/post_renewal_result.json).

## 4. When a quote changes

P04 is explicitly **separate controlled public E evidence**. It is not presented as another live LLM call inside the main narrative. A genuine quote-bound packet exists at EUR 5.00. Later source observations show changed terms while the pending packet still exists. The old packet is refused before a new business effect.

Public E computes the affected set and selectively recomputes the affected branch. Its result is consumed by a fresh BankRoot review. The previously paid period is preserved. The EUR 7.00 branch fails the EUR 6.50 consent limit. An independent EUR 6.00 branch receives a new review and packet, then produces one mock payment. The unchanged EUR 5.00 branch is the positive current-terms control.

| Current quote | Existing consent | Result |
|---|---:|---|
| EUR 5.00, unchanged | EUR 6.50 | Independent positive branch executes |
| EUR 6.00, changed | EUR 6.50 | Recompute, review and one independent mock payment |
| EUR 7.00, changed | EUR 6.50 | Old packet refused; recomputed terms exceed consent |

The EUR 6.00 control payment is not a third main-history payment. The later successful QUALITY A/B is also an independent branch with its own mock payment.

The evidence includes actual supplied D and E validations for the two completed recomputations. Coherent negative controls cover a missing dependency edge, an unreported change to preserved data, altered retained-work time/Host revision bindings, and a changed consumed result binding. These controls matter because a correctly formatted record alone is insufficient: it must describe the same work, source and review relation.

Evidence: [EUR 7.00 selected-field extract](evidence/sources/v09/p04_700_extract.json), [EUR 6.00 selected-field extract](evidence/sources/v09/n14_600_extract.json), [independent payment](evidence/sources/v09/bank_story_06/tests/actual_T3/N14_600_payment.json), [supplied D](evidence/sources/v09/bank_story_06/supplied_1_D.json), [supplied E](evidence/sources/v09/bank_story_06/supplied_1_E.json). Full report identities are in the evidence map.

## 5. The A/B result and the preserved disagreement

The controlled catalogue and EUR 6.50 ceiling stay the same. Changing `preference` from AD_FREE to QUALITY changes the chosen plan from `plan:cd79` to `plan:ab31`: higher resolution, advertising present, price EUR 6.00. The consumed quote result, payment amount, entitlement plan, session quality and playback all reflect the new choice.

The first QUALITY attempt did not simply succeed. The interpreter associated QUALITY with both high resolution and an ad-free experience. The selector favoured resolution; the reviewer objected. Its actual response included:

> The upstream selection of 'plan:ab31' does not fully implement the 'QUALITY' preference because it includes ads.

This is an excerpt from [response 13](evidence/sources/v10/live_captures/response_13.json). It belongs to the original, pre-clarification input contract. The historical replay verifies that refusal under that original contract.

The shared QUALITY contract was subsequently made explicit: resolution descending, then absence of advertising, then price, then plan ID. Advertising became a tie-breaker rather than a veto on higher resolution. The validators continued to reject disagreement. Responses 14 and 15 had already completed interpretation and terms analysis under the clarified input. V10 validated and reused those responses, then obtained only the missing selector and reviewer as attempts 19 and 20.

The journal contains **20 attempts, 17 responses and three transport failures**. Attempts 16 and 17 were recorded Google 504 failures; attempt 18 was a ReadTimeout. These are cumulative project-run counts, not the cost of a single successful purchase. The two V10 calls succeeded, and all original attempt/response/failure bodies remain preserved.

Evidence: [response 19](evidence/sources/v10/live_captures/response_19.json), [response 20](evidence/sources/v10/live_captures/response_20.json), [local raw-record and historical-refusal checks](evidence/sources/v10/offline_actual.json), [actual consumption](evidence/sources/v10/actual_AB_01/consumption.json).

## 6. Captures, replay and exact input identity

A capture binds the request, ordered role projection, raw output, response identity and transport metadata. The model is not asked to manufacture those local hashes. Saving an answer does not grant permission to execute it against a different current situation.

Two replay concepts must remain distinct:

| Operation | What it does | Model/effect behavior |
|---|---|---|
| Captured reexecution | Executes the handler again on fresh Hosts using validated saved role responses | Zero model calls; fresh declared mock effects |
| Offline history replay | Verifies a sealed historical package and its expected manifest hash | Zero provider and capability calls; no new authority inferred |

The V10 captured A/B reexecution reproduced the complete A/B history except for exactly two provenance fields: `purchase.generation_mode` and `purchase.semantics.mode`. No other fields were removed from comparison. Different provenance legitimately changes the seal hash.

The V11 saved-projection repair additionally distinguishes canonical JSON values such as integer `650` and float `650.0`, or boolean `false` and integer `0`. Python value equality alone does not preserve that distinction. Altered records are rejected before consumption, while the 12 genuine saved responses from main purchase, renewal and A/B still pass with identical canonical outputs.

Evidence: [captured comparison](evidence/sources/v10/captured_AB_01/comparison.json), [captured result](evidence/sources/v10/captured_AB_01/final.json), [offline replay](evidence/sources/v10/actual_AB_01/story/replay.json), [V11 capture controls](evidence/sources/v11/captured_boundary_v11.json).

## 7. Timing and acceptance without double counting

| Recorded operation | Duration | Measurement scope |
|---|---:|---|
| V09 first purchase handler | 169.10 s | Live P01 handler, before separate seal |
| V09 complete main story | 1,174.80 s | Purchase through renewal, later sessions, sealing and replay |
| V09 P04 EUR 7.00 public E | 317.99 s | Controlled selective recomputation |
| V09 P04 EUR 6.00 public E | 318.91 s | Independent controlled selective recomputation |
| V10 actual A/B | 290.806 s | Command wall time, including imports/finalizers |
| V10 captured A/B | 276.216 s | Command wall time, including imports/finalizers |

These are observed executions, not a production latency promise. The roughly five-minute A/B figures do not describe the entire purchase-to-renewal story. Model transport and local validation have different costs. The showcase build performs neither new model calls nor a new performance benchmark.

Evidence counts also describe distinct selections:

- V10: 36 focused tests and 108 setup/call/teardown phases.
- V11 preparation: 82 tests and 246 phases, plus eight disposable process-recovery controls.
- Actual owner postcommit: 49 unique tests and 147 passing phases.

Do not add these into a fictional number of unique system tests. V09 main/P04 and V10 A/B retain their recorded source-bound execution provenance. V11's owner checks establish final landing and selected current-boundary validation; they are not a fresh run of every previous D/E or Living suite.

Evidence: [V11 result](evidence/sources/v11/RESULT.json), [owner node list](evidence/sources/owner/postcommit_1789296216831611000/nodeids.txt), [owner complete phase log](evidence/sources/owner/postcommit_1789296216831611000/phases.jsonl).

## 8. Scope, source map and review route

The reusable architectural contribution is the separation of proposal, Root decision, current execution eligibility and historical evidence across a concrete changing task. This demonstration shows that the common machinery can support this subscription domain alongside the earlier airline and supplier demonstrations. It does not establish that every future domain can be introduced without new domain contracts, integrations or engineering.

| Concern | Accepted source |
|---|---|
| Finite request and plan contracts | `hedgehog/domains/testflix/contracts_v01.py` |
| Role projections and output binding | `hedgehog/domains/testflix/semantic_roles_v01.py` |
| Actual/captured provider transport | `hedgehog/domains/testflix/live_semantic_adapter_v01.py` |
| Four-Root lifecycle and dispatch | `hedgehog/domains/testflix/lifecycle_v01.py` |
| Story, repricing consumption and history | `hedgehog/domains/testflix/evidence_v01.py` |
| Declared business mocks | `hedgehog/domains/testflix/mock_world_v01.py` |
| Shared Host | `hedgehog/work_execution_host_v01.py` |
| Common typed work | `hedgehog/kernel/work_composition_v01.py` |
| D retained work | `hedgehog/kernel/fractal_runtime_v02.py` |
| E selective recomputation | `hedgehog/kernel/continuous_delta_runtime_v01.py` |

Browse [the accepted domain](https://github.com/AAkhtanin/hedgehog-os/tree/e42d37fa98dfec7110b8cf75b1aceaa614f461be/hedgehog/domains/testflix) or the [accepted preflight and scope record](https://github.com/AAkhtanin/hedgehog-os/blob/e42d37fa98dfec7110b8cf75b1aceaa614f461be/docs/testflix_v01_preflight.md).

The catalogue and clock are controlled. The clock is a local trusted test source, not an external attestation. All business effects are mocks; no real subscription or financial transaction is claimed. A new informational summary in the renewed period remains unsupported and outside this acceptance. No production or security certification is asserted.

A practical review order is: presentation → actual consumption → captured comparison → one preserved refusal → P04 selected-field extracts → owner phase log → accepted source. For a full reproduction audit, resolve the larger original reports using their archive/member/hash entries. The compact showcase is a readable evidence gateway, not a replacement for every original runtime object.
