"""Finite demo policy, not scientifically validated landslide prediction."""
from . import contracts_v01 as c

POLICY = dict(critical_um=5000,recovery_um=1000,recovery_duration=30,recovery_samples=3,
              required_channels=['displacement','reserve'],maximum_gap=15)


def local_pair(book,purpose,contract=None):
    contract=c.POLICY if contract is None else c.validate_policy(contract)
    rows=[book.current(ch,purpose,max_local_age_seconds=contract['max_local_age_seconds'])
        for ch in POLICY['required_channels']]
    c.require(len({v['lineage'] for v in rows})==2,'independent_witnesses_required')
    c.require(max(v['observed_start'] for v in rows)<=min(v['observed_end'] for v in rows),'coincident_witnesses_required')
    return rows


def features(book,purpose='critical',contract=None):
    contract=c.POLICY if contract is None else c.validate_policy(contract)
    rows=local_pair(book,purpose,contract)
    c.require(all(v['calibration']==contract['calibration'] for v in rows),'current_calibration_required')
    limits=(contract['critical_displacement_um'],contract['critical_reserve_um'])
    return dict(observability='ADEQUATE',source_ids=[v['observation_id'] for v in rows],
        hard_critical=all(v['value']>=limit for v,limit in zip(rows,limits)),
        ratios_micros=[v['value']*1000000//limit for v,limit in zip(rows,limits)],
        recovery_point=all(v['value']<=POLICY['recovery_um'] for v in rows))


class Incident:
    def __init__(self):
        self.incident_id=None;self.state='QUIET';self.witnesses=[];self.seen=set();self.transitions=[]
        self.recovery_dependencies=None;self.revoked_coverage=[]

    def evaluate(self,book,contract=None):
        contract=c.POLICY if contract is None else c.validate_policy(contract)
        try: value=features(book,contract=contract)
        except ValueError as error:
            self.witnesses=[]
            return dict(observability='INADEQUATE',reason=str(error),clearance=False,new_incident=False)
        rows=local_pair(book,'recovery',contract)
        dependencies=dict(channels=[dict(site=v['site'],channel=v['channel'],lineage=v['lineage'],
            calibration=v['calibration'],unit=v['unit'],statistic=v['statistic']) for v in rows],
            recovery_policy=POLICY,contract={k:contract[k] for k in
                ('calibration','critical_displacement_um','critical_reserve_um','max_local_age_seconds')})
        frozen=c.canonical(dependencies)
        if self.recovery_dependencies!=frozen:
            if self.witnesses:
                self.revoked_coverage.append(dict(tick=book.tick,reason='recovery_dependencies_changed',
                    previous_dependencies=self.recovery_dependencies.decode(),witnesses=list(self.witnesses)))
            self.witnesses=[];self.recovery_dependencies=frozen
        if value['hard_critical']:
            self.witnesses=[]
            new=self.incident_id is None
            if new:
                self.incident_id=c.identity('incident',value);self.state='ACTIVE'
                self.transitions.append(dict(state=self.state,tick=book.tick,source_ids=value['source_ids']))
            return dict(value,new_incident=new,clearance=False)
        if self.state!='ACTIVE': return dict(value,new_incident=False,clearance=False)
        ids=tuple(value['source_ids'])
        if not value['recovery_point']:
            self.witnesses=[]
        elif not any(ref in self.seen for ref in ids):
            measured={v['channel']:[v['observed_start'],v['observed_end']] for v in rows}
            previous=self.witnesses[-1]['measured'] if self.witnesses else None
            advancing=previous is None or all(measured[ch][0]>previous[ch][1] for ch in measured)
            if advancing:
                if previous and any(measured[ch][1]-previous[ch][1]>POLICY['maximum_gap'] for ch in measured):self.witnesses=[]
                self.seen.update(ids);self.witnesses.append(dict(tick=book.tick,source_ids=list(ids),measured=measured,
                    received={v['channel']:v['received'] for v in rows}))
        spans=({ch:self.witnesses[-1]['measured'][ch][1]-self.witnesses[0]['measured'][ch][1]
                for ch in POLICY['required_channels']} if self.witnesses else {})
        clearance=(len(self.witnesses)>=POLICY['recovery_samples'] and
                   min(spans.values())>=POLICY['recovery_duration'])
        return dict(value,new_incident=False,clearance=clearance,witnesses=list(self.witnesses),measured_spans=spans)

    def close(self,tick,receipt):
        c.require(self.state=='ACTIVE' and bool(receipt),'incident_close_receipt')
        self.state='CLOSED';self.transitions.append(dict(state='CLOSED',tick=tick,receipt=receipt))
