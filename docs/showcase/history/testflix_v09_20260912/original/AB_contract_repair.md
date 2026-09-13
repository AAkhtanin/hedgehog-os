# Actual A/B refusal and bounded continuation

The first authorized four responses (attempts 10-13) completed transport and
stopped at `semantic_review_disagreement`, before Hosts/action. The intent role
expanded QUALITY into high resolution, ad-free, premium content and simultaneous
streams. Only the selector duty had the precise resolution-first meaning. The
reviewer consumed the expanded intent and rejected the 1080p/600-with-ads choice.
The exact original response and refusal are retained. A same-handler captured
control on those bytes reproduced the refusal with zero Hosts/model/effect calls.

The owner then explicitly authorized additional requests needed for the result.
All QUALITY role projections now carry the same finite ordered definition from
the existing domain preference rule: affordable entries, resolution descending,
then ads/price/plan-id tie-breakers. Unsupported premium-content/stream-count
requirements are not introduced. AD_FREE projections remain byte-equivalent.
Independent disagreement and missing-evidence predicates are unchanged.

The local ledger is conservatively extended to 20 total/10 main/10 A/B attempts,
not an unlimited loop. Failed attempts remain counted. The next actual selection
is four calls on a changed input contract, not a retry of identical inputs until
PASS. The existing Google endpoint/model/account and mock-only effects remain.

Source impact: Host/D/E, Root, lifecycle, legacy controlled adapter and AD_FREE
projection bodies are unchanged by this clarification. Completed main/captured
history retains its exact source receipts. Fresh role controls, actual QUALITY
execution and captured QUALITY history establish the changed boundary. None of
this retroactively changes the recorded rejected A/B responses into acceptance.

Owner statement: "можешь использовать любое количество запросов если они тебе надо для результата".

The changed-input selector attempts 16 and 17 returned actual Google 504 errors.
Local installed SDK `_api_client.py` converts `HttpOptions.timeout` from ms to
seconds and sets `X-Server-Timeout` from it (get_timeout_in_seconds,
populate_server_timeout_header, request assembly at 1310-1322). Thus the 90000ms
setting also supplied a 90-second server deadline, matching both ~89s refusals.
One explicit continuation raises that network/server deadline to 180000ms,
without changing model, semantic inputs, retry count or any runtime timer.
Only the missing suffix is requested; actual responses14/15 remain input-bound.
This is a measured transport-boundary adjustment, not evidence that the provider
will complete or that a semantic refusal can be overwritten.

Actual result: attempt18 returned no response and ended with httpx.ReadTimeout
after180.6s. This differs from the two earlier server504 responses. No successful
selector/reviewer suffix or positive A/B action is claimed. All own processes
were reaped. The last request's remote eventual completion is unknown; it still
consumes one attempt. The remaining blocker is external response completion,
not lack of owner authorization or a self-imposed total test budget.
