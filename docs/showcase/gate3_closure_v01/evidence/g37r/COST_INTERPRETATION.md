# Corrected G37 cost interpretation

The retained G37 Living and Conformance runs are execution evidence, not an
unmonitored A/B benchmark. Both successful runs used local start/return
monitoring. The Conformance run must not be described as unmonitored, and no
macOS sampling attachment was used for that run.

The approximately `0.00015` second figure is only a synthetic estimate for six
trace writes at the measured write volume. It is not total instrumentation
overhead. Each successful ownership trace contains 12 events. Inclusive phase
times and nested monitor times are not additive independent CPU shares.

The retained timings remain factual: Living completed in 2,300.17 seconds and
Conformance in 2,212.77 seconds. Their E5 phases were 1,806.61 and 1,771.86
seconds respectively. E5 executes the full historical matrix; these receipts
do not establish a function-level hotspot. The evidence supports a large E5
phase cost, not attribution of that cost to one function or to monitoring.

G37R did not rerun E5, D, Living, Conformance or the G3 collector. It performed
public supplied validation over the retained reports. That validation took
32.28 seconds in the final run and observed zero collector, current Root, Host,
Work execution, history-recording or effect calls.
