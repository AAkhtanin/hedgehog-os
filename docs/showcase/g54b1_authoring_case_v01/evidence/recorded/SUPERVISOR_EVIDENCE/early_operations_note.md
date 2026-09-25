# Early Operations Recording Limits

The preparation helper initially stopped on a mode-representation comparison
(`0644` versus `0o644`). It was corrected by comparing integer modes; already
completed archive-identity and owner metadata reads were reused. This was not an
author submission or a native execution. The terminal failure is retained in the
operator conversation; no raw command journal was created for that early command.

The eight local broker unit tests passed before journal_run.py was introduced.
The terminal reported 8 tests in 0.026 seconds and OK. These covered the inert
operations, refusals, deduplication, frozen submission and interrupted PREPARED
state. No synthetic command receipt or replacement raw streams are asserted here.
The real subsequent diagnostic has its complete independent command receipt,
raw streams, protocol events and actual dynamic request/result history.

These recording limits do not convert historical checks into fresh checks of
any later source. The author boundary is additionally exercised by the real
no-environment diagnostic, whose exact source pins precede task disclosure.
