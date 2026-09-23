"""Synthetic event evidence and coordinator-owned monotonic scenario clock."""
from . import contracts_v01 as c

SITE = 'slope_demo_site_001'
AGES = {'configuration': 180, 'critical': 10, 'recovery': 10, 'context': 60}


def observation(channel, value, tick, sequence, *, received=None, lineage=None, site=SITE, status='HEALTHY',
                observed_start=None, calibration=None):
    unit = {'rainfall':'mm_x1000','channel_level':'synthetic_level_mm','vibration':'synthetic_intensity_milli'}.get(channel,'um')
    raw = dict(site=site, channel=channel, value=value, observed_start=tick if observed_start is None else observed_start, observed_end=tick,
               unit=unit, statistic='accumulation_1h' if channel == 'rainfall' else ('event_intensity' if channel=='vibration' else 'absolute_displacement'),
               lineage=lineage or 'independent:'+channel, sequence=sequence,
               calibration=calibration or c.POLICY['calibration'], status=status)
    result = dict(raw, received=tick if received is None else received, raw_sha256=c.digest(raw),
                  raw_ref=c.identity('synthetic_raw', raw))
    result['observation_id'] = c.identity('observation', result)
    result['projection_binding'] = c.digest(compatibility(result)) if value is not None else None
    return result


def compatibility(value):
    return c.measurement(dict(sensor=value['channel'], value=value['value'], unit=value['unit'],
        scenario_tick=value['observed_end'], healthy=value['status']=='HEALTHY', calibration=value['calibration']))


def validate(value):
    expected = observation(value['channel'],value['value'],value['observed_end'],value['sequence'],
        received=value['received'],lineage=value['lineage'],site=value['site'],status=value['status'],
        observed_start=value['observed_start'],calibration=value['calibration'])
    c.require(value == expected, 'observation_content_binding')
    c.require(value['channel'] in ('rainfall','displacement','reserve','channel_level','vibration'), 'observation_channel')
    c.require(type(value['lineage']) is str and bool(value['lineage']),'observation_lineage')
    c.require(all(type(value[k]) is int and value[k]>=0 for k in ('observed_start','observed_end','received','sequence')), 'observation_integer_time')
    c.require(value['observed_start']<=value['observed_end']<=value['received'], 'future_observed_before_received')
    c.require(value['status'] in ('HEALTHY','MISSING','INADEQUATE'), 'observation_status')
    c.require((value['value'] is None)==(value['status']=='MISSING'), 'observation_absence')
    return value


class EventBook:
    def __init__(self):
        self.tick=0; self.history=[]; self.latest={}; self.seen=set(); self.arrivals=[]

    def advance(self,tick):
        c.require(type(tick) is int and tick>=self.tick,'scenario_clock_rollback')
        self.tick=tick

    def ingest(self,records,tick):
        c.require(type(tick) is int and tick>=self.tick,'scenario_clock_rollback')
        staged=dict(self.latest)
        for value in records:
            validate(value)
            c.require(value['site']==SITE and value['received']<=tick,'observation_site_or_future_receipt')
            old=staged.get(value['channel'])
            if value['observation_id'] in self.seen:continue
            c.require(old is None or value['sequence']>old['sequence'],'source_sequence_rollback')
            c.require(old is None or value['observed_end']>=old['observed_end'],'measurement_time_rollback')
            staged[value['channel']]=value
        self.advance(tick)
        for value in records:
            validate(value)
            c.require(value['site']==SITE and value['received']<=tick,'observation_site_or_future_receipt')
            self.arrivals.append(dict(observation_id=value['observation_id'],ingested_at=tick))
            if value['observation_id'] in self.seen: continue
            old=self.latest.get(value['channel'])
            c.require(old is None or value['sequence']>old['sequence'],'source_sequence_rollback')
            frozen=c.canonical(value); self.history.append(frozen);self.seen.add(value['observation_id'])
            self.latest[value['channel']]=__import__('json').loads(frozen)

    def current(self,channel,purpose,*,max_local_age_seconds=None):
        value=self.latest.get(channel)
        c.require(value is not None and value['value'] is not None and value['status']=='HEALTHY','measurement_not_adequate')
        age=AGES[purpose]
        if max_local_age_seconds is not None:
            c.require(purpose in ('critical','recovery') and type(max_local_age_seconds) is int
                and max_local_age_seconds>0,'local_age_override_scope')
            age=max_local_age_seconds
        c.require(0<=self.tick-value['observed_end']<=age,'measurement_stale_for_'+purpose)
        return __import__('json').loads(c.canonical(value))


class AllocationLedger:
    """Domain scheduling allowance, additional to native and Work budgets."""
    def __init__(self,total=64):
        self.total=total;self.tasks={};self.entries=[]

    def allocate(self,task,limit,context):
        c.require(task not in self.tasks and type(limit) is int and 0<limit<=self.total,'allocation_refused')
        c.require(sum(v['limit'] for v in self.tasks.values())+limit<=self.total,'coordinator_allowance_exhausted')
        self.tasks[task]=dict(limit=limit,spent=0,context=context,state='OPEN')
        self.entries.append(dict(operation='ALLOCATE',task=task,limit=limit,context=context))

    def consume(self,task,operation):
        row=self.tasks[task]
        c.require(row['state']=='OPEN' and row['spent']<row['limit'],'task_allowance_exhausted')
        row['spent']+=1;self.entries.append(dict(operation=operation,task=task,spent=row['spent']))


class CapabilityState:
    def __init__(self,profile='LOCAL_ALGORITHMS_ONLY',harness=False):
        self.profile=profile;self.harness=harness;self.site_online=True;self.revision=0;self.requests=[]

    def change(self,online):
        c.require(type(online) is bool,'capability_boolean');self.site_online=online;self.revision+=1

    def snapshot(self,purpose):
        return dict(profile=self.profile,revision=self.revision,purpose=purpose,site_cloud_available=self.site_online,
            remote_rainfall_available=self.site_online,harness_transport_available=self.available('harness'),
            physical_local_slm_available=False)

    def available(self,lane):
        if lane=='physical_local_slm': return False
        if lane=='harness': return self.profile=='EMULATED_LOCAL_SLM' and self.harness
        return self.site_online

    def request(self,lane,context):
        self.requests.append(dict(lane=lane,context=context,revision=self.revision,admitted=self.available(lane)))
        c.require(self.available(lane),'capability_unavailable:'+lane)
        return dict(mode='CONTROLLED_FIXTURE_NO_TRANSPORT',context=context)
