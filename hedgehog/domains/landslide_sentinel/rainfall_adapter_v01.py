"""Bounded EA context acquisition, kept separate from the synthetic site's sensors."""
from datetime import datetime,timezone
from decimal import Decimal,ROUND_HALF_EVEN
import json
from pathlib import Path
import time
from urllib.request import Request,urlopen
from urllib.parse import urlparse
from . import contracts_v01 as c
from .evidence_v01 import save

ROOT='https://environment.data.gov.uk/flood-monitoring'
ATTRIBUTION='this uses Environment Agency rainfall data from the real-time data API (Beta)'


def normalize(measure,reading,received,*,interval_semantics='UNCONFIRMED'):
    c.require(measure['parameter']=='rainfall' and measure['unitName']=='mm' and measure['period']==900
        and measure['valueType']=='total','ea_measure_semantics')
    c.require(reading['measure']==measure['@id'],'ea_reading_measure')
    stamp=datetime.fromisoformat(reading['dateTime'].replace('Z','+00:00'))
    c.require(stamp.tzinfo is not None and stamp.utcoffset().total_seconds()==0,'ea_source_timezone')
    end=int(stamp.timestamp());c.require(end<=received,'ea_future_observation')
    raw=reading.get('value');c.require(type(raw) in (int,float,str) and type(raw) is not bool,'ea_missing_value')
    number=Decimal(str(raw));c.require(number.is_finite() and number>=0,'ea_finite_rainfall')
    value=int((number*1000).quantize(Decimal('1'),rounding=ROUND_HALF_EVEN))
    c.require(interval_semantics in ('UNCONFIRMED','CONTROLLED_END_LABEL','DOCUMENTED_END_LABEL'),'ea_interval_semantics')
    known=interval_semantics!='UNCONFIRMED'
    return dict(source_id=reading.get('@id'),measure=measure['@id'],observed_start=end-900 if known else None,observed_end=end if known else None,
        source_timestamp=reading['dateTime'],source_timezone='UTC',received=received,ingested=int(time.time()),
        value=value,unit='mm_x1000',statistic='accumulated_total',period_seconds=900,
        precision='Decimal(str(value))*1000 rounded once with ROUND_HALF_EVEN',raw_sha256=c.digest(reading),
        interval_convention=interval_semantics,observation_label_epoch=end)


def aggregate(records):
    c.require(bool(records),'ea_empty_intervals')
    c.require(all(v['interval_convention'] in ('DOCUMENTED_END_LABEL','CONTROLLED_END_LABEL') for v in records),'ea_interval_unconfirmed')
    ordered=sorted(records,key=lambda v:v['observed_start'])
    for row in ordered:
        c.require(row['interval_convention'] in ('DOCUMENTED_END_LABEL','CONTROLLED_END_LABEL'),'ea_interval_unconfirmed')
        c.require(row['statistic']=='accumulated_total' and row['period_seconds']==900
            and row['observed_end']-row['observed_start']==900,'ea_accumulation_only')
        c.require(row['measure']==ordered[0]['measure'] and row['unit']=='mm_x1000','ea_aggregate_source')
    for left,right in zip(ordered,ordered[1:]):
        c.require(left['observed_end']==right['observed_start'],'ea_duplicate_overlap_or_missing_interval')
    return dict(total_mm_x1000=sum(v['value'] for v in ordered),start=ordered[0]['observed_start'],end=ordered[-1]['observed_end'],
        source_ids=[v['source_id'] for v in ordered],scope=ordered[0]['interval_convention'])


def acquire(directory):
    directory=Path(directory);directory.mkdir(parents=True,exist_ok=False);attempts=[]
    acquisition_time=int(time.time())
    plan=dict(frozen_utc=datetime.fromtimestamp(acquisition_time,timezone.utc).isoformat(),maximum_metadata_age_seconds=72*3600,
        station_pages=dict(limit=100,offsets=[0,100,200],status='Active',view='full'),maximum_measure_metadata_queries=20,
        selection='Collect bounded active station metadata, sort stationReference/measure URI lexicographically; inspect first20 supported coordinate/rainfall/mm/900s candidates in order. Pin first with explicit active status, total statistic and latestReading within72h. Never inspect rainfall values for selection.',
        readings='Exactly latest8 from the selected pin; no gauge replacement after readings.',
        timeout_seconds=45,maximum_response_bytes=3000000,transport_retries_per_request=1,continuous_polling=False,
        interval_label_semantics='UNCONFIRMED_UNLESS_OFFICIAL_EVIDENCE_ESTABLISHES_ENDPOINT',synthetic_site_mapping='NONE',attribution=ATTRIBUTION)
    save(directory/'plan.json',plan)
    def get(url,name,html=False):
        parts=urlparse(url);c.require(parts.scheme=='https' and parts.netloc=='environment.data.gov.uk','ea_request_origin')
        for ordinal in (1,2):
            start=time.monotonic();row=dict(url=url,method='GET',started=datetime.now(timezone.utc).isoformat(),attempt=ordinal,name=name)
            attempts.append(row)
            try:
                with urlopen(Request(url,headers={'Accept':'text/html' if html else 'application/json','User-Agent':'Radiolaria-LS2R-bounded-source-review'}),timeout=45) as response:
                    raw=response.read(3000001);c.require(len(raw)<=3000000,'ea_response_bound')
                    row.update(status=response.status,headers={k:v for k,v in response.headers.items() if k.lower() in
                        ('date','content-type','last-modified','etag','cache-control')},received=int(time.time()),sha256=c.digest(raw),bytes=len(raw))
                    raw_name=name+'_'+str(ordinal)+'.raw';(directory/raw_name).write_bytes(raw);row['raw_file']=raw_name
                    return raw.decode() if html else json.loads(raw),row
            except (OSError,TimeoutError) as error:
                row.update(error_type=type(error).__name__,error=str(error))
                if ordinal==2:raise
            finally:
                row['seconds']=time.monotonic()-start;save(directory/'attempts.json',attempts)
    try:
        docs,_=get(ROOT+'/doc/rainfall','documentation',True)
        c.require('15 min' in docs and 'once or twice' in docs,'ea_documentation_changed')
        reference_docs,_=get(ROOT+'/doc/reference','reference',True)
        c.require('statusActive' in reference_docs and '_offset' in reference_docs,'ea_status_pagination_documentation')
        stations=[];metadata_hashes=[]
        for offset in plan['station_pages']['offsets']:
            page,capture=get(ROOT+'/id/stations.json?parameter=rainfall&status=Active&_view=full&_limit=100&_offset='+str(offset),'stations_'+str(offset))
            stations.extend(page['items']);metadata_hashes.append(capture['sha256'])
            if len(page['items'])<100:break
        options=[];exclusions=[]
        for station in stations:
            status=station.get('status');status=status.get('@id') if type(status) is dict else status
            if status not in ('http://environment.data.gov.uk/flood-monitoring/def/core/statusActive',
                              'https://environment.data.gov.uk/flood-monitoring/def/core/statusActive'):
                exclusions.append(dict(station=station.get('stationReference'),reason='ACTIVE_STATUS_UNESTABLISHED'));continue
            if 'lat' not in station or 'long' not in station:continue
            measures=station.get('measures',[])
            if type(measures) is dict:measures=[measures]
            for measure in measures:
                if measure.get('parameter')=='rainfall' and measure.get('unitName')=='mm' and measure.get('period')==900:
                    options.append((str(station['stationReference']),measure['@id'],station))
        save(directory/'candidate_order.json',dict(candidates=[dict(station=v[0],measure=v[1]) for v in sorted(options,key=lambda x:x[:2])],exclusions=exclusions))
        selected=None
        for index,(reference,uri,station) in enumerate(sorted(options,key=lambda x:x[:2])[:20]):
            secure=uri.replace('http://','https://',1)
            metadata,meta_capture=get(secure+'.json','measure_'+str(index));measure=metadata['items']
            latest=measure.get('latestReading');reason=None
            label=latest.get('dateTime') if type(latest) is dict else None
            if not (measure.get('parameter')=='rainfall' and measure.get('unitName')=='mm' and measure.get('period')==900 and measure.get('valueType')=='total'):
                reason='UNSUPPORTED_MEASURE_SEMANTICS'
            elif not label:reason='LATEST_READING_TIME_MISSING'
            else:
                stamp=datetime.fromisoformat(label.replace('Z','+00:00'))
                if stamp.tzinfo is None or stamp.utcoffset().total_seconds()!=0:reason='LATEST_TIMEZONE_UNCONFIRMED'
                elif not 0<=acquisition_time-int(stamp.timestamp())<=72*3600:reason='LATEST_READING_OUTSIDE_PREDECLARED_72H'
            exclusions.append(dict(station=reference,measure=uri,latest_timestamp=label,
                latest_reference=latest if type(latest) is str else latest.get('@id') if type(latest) is dict else None,
                metadata_sha256=meta_capture['sha256'],
                result=reason or 'ELIGIBLE',reading_value_not_inspected=True))
            save(directory/'eligibility.json',exclusions)
            if reason is None:
                selected=(reference,uri,station,measure,secure,meta_capture);break
        c.require(selected is not None,'ea_no_eligible_source_in_bounded_metadata')
        reference,uri,station,measure,secure,meta_capture=selected
        save(directory/'selected_pin.json',dict(station_reference=reference,measure=uri,station=station,metadata_hashes=metadata_hashes,
            measure_metadata_sha256=meta_capture['sha256'],selected_before_readings=True,rule=plan['selection'],selected_at=datetime.now(timezone.utc).isoformat()))
        readings,capture=get(secure+'/readings.json?_sorted&_limit=8','readings')
        normalized=[];refusals=[]
        for reading in readings['items']:
            try:normalized.append(normalize(measure,reading,capture['received']))
            except ValueError as error:refusals.append(dict(reading=reading,reason=str(error)))
        try:total=aggregate(normalized)
        except ValueError as error:total=dict(status='NOT_AGGREGATED',reason=str(error))
        result=dict(status='ACTUAL_READINGS_NORMALIZED' if normalized else 'EMPTY_READINGS' if not readings['items'] else 'READINGS_NOT_NORMALIZABLE',station=station,measure=measure,
            licence=readings.get('meta',{}).get('licence'),attribution=ATTRIBUTION,normalized=normalized,refusals=refusals,
            aggregation=total,spatial_applicability='NO_VERIFIED_MAPPING_TO_SYNTHETIC_SITE',
            temporal_applicability='UNCONFIRMED_INTERVAL_ENDPOINT; LABEL_RECENCY_ONLY; NO_CURRENT_LOCAL_SENSOR_ELIGIBILITY',requests=len(attempts))
    except Exception as error:
        result=dict(status='ACQUISITION_FAILED',error_type=type(error).__name__,error=str(error),requests=len(attempts),synthetic_fallback=False)
    save(directory/'result.json',result);return result
