"""Finite optional work and historical context handling; no scenario selectors."""
from . import contracts_v01 as c
from .evidence_v01 import plain


def optional_diagnostics(session,units):
    c.require(type(units) is int and 0<=units<=2,'optional_compute_units')
    outputs=[]
    session.work_limit=units
    try:
        for choice in ('REFERENCE_INTEGRITY','TEMPORAL_CONTEXT_APPLICABILITY')[:max(1,units)]:
            material=dict(selection=choice,frames=session.frames,contract=session.contract)
            work=session.pure_consumer('sentinel.diagnostic.v01',material)
            outputs.append(dict(program=plain(work[0].candidate),results=plain(work[1]),artifact=plain(work[2])))
    finally:
        del session.work_limit
    return dict(units=units,outputs=outputs,routes=plain(session.routes[-len(outputs):]),budgets=plain(session.budgets.tasks))


def context_status(record,tick,site):
    from .events_v01 import validate
    validate(record)
    current=(record['site']==site and record['status']=='HEALTHY' and 0<=tick-record['observed_end']<=60)
    return dict(status='CURRENT_CONTEXT' if current else 'HISTORICAL_OR_INAPPLICABLE',
        source_id=record['observation_id'],observed=[record['observed_start'],record['observed_end']],
        received=record['received'],site=record['site'],creates_permission=False)
