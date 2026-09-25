"""Closed fixed-point local measurements and finite diagnostic policy."""
import hashlib
import json

DOMAIN = 'LANDSLIDE_SENTINEL'
DIAGNOSTICS = ('REFERENCE_INTEGRITY', 'INDEPENDENT_RESERVE_SERIES', 'TEMPORAL_CONTEXT_APPLICABILITY',
               'SPATIAL_CONTEXT_APPLICABILITY', 'EVIDENCE_GAPS')
SERIES_POLICY = dict(minimum_samples=3,minimum_span=20,maximum_gap=15,newest_max_age=10,maximum_range_um=1000)
DIAGNOSTIC_CATALOGUE = {
    'REFERENCE_INTEGRITY': 'Compare the two current channel records: calibration identifier association, health and lineage separation. This is a current-pair metadata comparison, not a history-variation measurement or physical certification.',
    'INDEPENDENT_RESERVE_SERIES': 'Measure reserve variation over the admitted historical window after accepted plan and native read. Independence, calibration and receipt checks are compulsory source-fitness guards, not an investigation of all current-channel associations.',
    'TEMPORAL_CONTEXT_APPLICABILITY': 'Compare contextual measurement time, receipt time, known interval and current evaluation. Report temporal suitability or historical/missing evidence; transport time cannot renew a measurement.',
    'SPATIAL_CONTEXT_APPLICABILITY': 'Inspect contextual site and source identities against the intended site. Report scope match or absent spatial mapping, without inventing coordinates or causal relevance.',
    'EVIDENCE_GAPS': 'Compare supplied evidence with the declared duty-specific requirements: current-pair metadata for local/reviewer duties, or hourly rainfall context support for the environmental duty. Return specific missing, incompatible, unresolved or supported relationships; unrelated physical certification is a limitation, not an automatic prerequisite.',
}
INVESTIGATION_VERSION='sentinel.investigation.v02'


def investigation(selection,duty):
    require(selection in DIAGNOSTICS,'investigation_selection')
    environmental=duty=='CLOUD_ENVIRONMENTAL_ANALYST'
    require(duty in ('LOCAL_SLOPE_ANALYST','CLOUD_ENVIRONMENTAL_ANALYST','ADVERSARIAL_SENSOR_REVIEWER'),'investigation_duty')
    require(selection in (('TEMPORAL_CONTEXT_APPLICABILITY','SPATIAL_CONTEXT_APPLICABILITY','EVIDENCE_GAPS') if environmental
        else ('REFERENCE_INTEGRITY','INDEPENDENT_RESERVE_SERIES','EVIDENCE_GAPS')),'investigation_duty_scope')
    if selection=='INDEPENDENT_RESERVE_SERIES':
        target='RESERVE_WINDOW_VARIATION';use='BOUNDED_RESERVE_CONSISTENCY'
        required=['ACTUAL_NATIVE_RECEIPT','ADMITTED_RESERVE_HISTORY','CURRENT_PRIMARY_LINEAGE','SERIES_FITNESS']
        relationship='Measure range and span of the acquired reserve window after all source-fitness checks.'
    elif selection=='TEMPORAL_CONTEXT_APPLICABILITY':
        target='RAINFALL_MEASUREMENT_INTERVAL';use='CURRENT_HOURLY_RAINFALL_CONTEXT'
        required=['RAINFALL_RECORD','SCENARIO_SECONDS','MM_X1000','ACCUMULATION_1H','EXPLICIT_3600_SECOND_INTERVAL','CURRENT_ENDPOINT']
        relationship='Compare actual interval duration/statistic/units and endpoint age with the declared hourly context use.'
    elif selection=='SPATIAL_CONTEXT_APPLICABILITY':
        target='CONTEXT_SITE_RELATIONSHIP';use='CONTEXT_FOR_SYNTHETIC_SITE'
        required=['RAINFALL_RECORD','SOURCE_SITE_ID','TARGET_SITE_ID']
        relationship='Compare declared synthetic site identities; separately retain missing verified physical mapping.'
    elif selection=='EVIDENCE_GAPS' and environmental:
        target='HOURLY_CONTEXT_EVIDENCE_REQUIREMENTS';use='CURRENT_HOURLY_RAINFALL_CONTEXT'
        required=['RAINFALL_RECORD','SUPPORTED_INTERVAL_STATISTIC_UNITS','CURRENT_ENDPOINT','SYNTHETIC_SITE_SCOPE']
        relationship='Evaluate each supplied rainfall record against temporal and synthetic site requirements; name each unsupported relationship.'
    else:
        target='CURRENT_CHANNEL_METADATA' if selection=='REFERENCE_INTEGRITY' else 'CURRENT_PAIR_EVIDENCE_REQUIREMENTS'
        use='CURRENT_PAIR_METADATA_COMPARISON'
        required=['CURRENT_DISPLACEMENT_RECORD','CURRENT_RESERVE_RECORD','CURRENT_CALIBRATION_IDS','HEALTH','DISTINCT_LINEAGES']
        relationship='Compare actual current channel/calibration associations and distinct lineage identifiers, not reserve history variation.'
    return dict(version=INVESTIGATION_VERSION,duty=duty,target=target,intended_use=use,required_evidence=required,
        checked_relationship=relationship,source_scope='DUTY_OBSERVATIONS_WITH_COMPULSORY_COMPANIONS',
        source_refs_meaning='CITATIONS_NOT_ACQUISITION_OR_OPTIONAL_SAFETY_FILTERS',
        bounded_results=['SUPPORTED','MISSING','INCOMPATIBLE','UNRESOLVED'],
        cannot_establish=['PHYSICAL_CALIBRATION_CERTIFICATION','GEOGRAPHICAL_RELEVANCE','LANDSLIDE_PREDICTION','ACTION_PERMISSION'])


def temporal_findings(records,tick):
    """Measurement support, not transport recency, determines hourly applicability."""
    results=[]
    if not records:return [dict(source_id=None,status='MISSING',reasons=['RAINFALL_RECORD_MISSING'])]
    for value in records:
        missing=[];incompatible=[];unresolved=[]
        start=value.get('observed_start');end=value.get('observed_end');received=value.get('received')
        times=all(type(v) is int and v>=0 for v in (start,end,received,tick))
        if not times:missing.append('EXPLICIT_SCENARIO_INTERVAL_SUPPORT_MISSING')
        else:
            if not start<=end<=received<=tick:incompatible.append('TIME_ORDER_OR_FUTURE_TIME')
            if start<=end and end-start!=3600:incompatible.append('HOURLY_INTERVAL_DURATION_MISMATCH')
            if end<=tick and tick-end>60:unresolved.append('HISTORICAL_ENDPOINT_NOT_CURRENT')
        if value.get('channel')!='rainfall':incompatible.append('NOT_RAINFALL_CONTEXT')
        if value.get('unit')!='mm_x1000':incompatible.append('UNSUPPORTED_UNITS')
        if value.get('statistic')!='accumulation_1h':incompatible.append('UNSUPPORTED_STATISTIC')
        if value.get('status')!='HEALTHY' or value.get('value') is None:missing.append('MEASUREMENT_NOT_ADEQUATE')
        results.append(dict(source_id=value.get('observation_id'),status='INCOMPATIBLE' if incompatible else
            'MISSING' if missing else 'UNRESOLVED' if unresolved else 'SUPPORTED',reasons=incompatible+missing+unresolved,
            measured_interval=[start,end],received=received,endpoint_age=tick-end if type(end) is int else None,
            time_basis='SCENARIO_SECONDS',unit=value.get('unit'),statistic=value.get('statistic')))
    return results


def investigation_findings(row,contract):
    records=row['observations'];selection=row['selection'];spec=row['investigation']
    if selection=='TEMPORAL_CONTEXT_APPLICABILITY' or (selection=='EVIDENCE_GAPS' and spec['duty']=='CLOUD_ENVIRONMENTAL_ANALYST'):
        findings=temporal_findings(records,row['tick'])
        if selection=='EVIDENCE_GAPS':
            findings += [dict(source_id=v['observation_id'],relationship='SYNTHETIC_SITE_SCOPE',
                status='SUPPORTED' if v['site']==row['site'] else 'INCOMPATIBLE',reasons=[] if v['site']==row['site'] else ['SITE_ID_MISMATCH']) for v in records]
        return dict(findings=findings,measured=[v['observed_end'] for v in records],received=[v['received'] for v in records],
            scope='TEMPORAL_AND_DECLARED_SYNTHETIC_SCOPE_ONLY' if selection=='EVIDENCE_GAPS' else 'TEMPORAL_ONLY',
            physical_mapping='NOT_ESTABLISHED')
    if selection=='SPATIAL_CONTEXT_APPLICABILITY':
        findings=([dict(source_id=v['observation_id'],status='SUPPORTED' if v['site']==row['site'] else 'INCOMPATIBLE',
            relationship='SYNTHETIC_SITE_IDENTITY',reasons=[] if v['site']==row['site'] else ['SITE_ID_MISMATCH']) for v in records]
            or [dict(source_id=None,status='MISSING',reasons=['RAINFALL_RECORD_MISSING'])])
        return dict(findings=findings,sites=sorted({v['site'] for v in records}),target_site=row['site'],
            physical_mapping='NOT_ESTABLISHED',physical_applicability='UNRESOLVED_NO_VERIFIED_MAPPING')
    findings=[]
    for channel in ('displacement','reserve'):
        matches=[v for v in records if v['channel']==channel]
        if len(matches)!=1:
            findings.append(dict(channel=channel,status='MISSING',reasons=['REQUIRED_CURRENT_CHANNEL_MISSING']));continue
        value=matches[0];reasons=[]
        if value['calibration']!=contract['calibration']:reasons.append('CURRENT_CALIBRATION_MISMATCH')
        if value['status']!='HEALTHY' or value['value'] is None:reasons.append('INADEQUATE_CHANNEL')
        if not 0<=row['tick']-value['observed_end']<=contract['max_local_age_seconds']:reasons.append('CURRENT_CHANNEL_AGE')
        findings.append(dict(source_id=value['observation_id'],channel=channel,calibration=value['calibration'],
            status='INCOMPATIBLE' if reasons else 'SUPPORTED',reasons=reasons))
    if len(records)==2:
        distinct=len({v['lineage'] for v in records})==2
        findings.append(dict(relationship='CURRENT_PAIR_LINEAGE_SEPARATION',lineages=[v['lineage'] for v in records],
            status='SUPPORTED' if distinct else 'INCOMPATIBLE',reasons=[] if distinct else ['CURRENT_PAIR_LINEAGES_CORRELATED']))
    return dict(findings=findings,source_ids=[v['observation_id'] for v in records],physical_zero_check='NOT_ESTABLISHED')


def performed_investigation(result):
    """Compare executed relationships/evidence, not operation labels or prose."""
    require('investigation' in result,'current_investigation_result_required')
    detail=result['detail']
    if result['selection']=='INDEPENDENT_RESERVE_SERIES':
        return dict(work='RESERVE_WINDOW_VARIATION',source_ref=detail['source_ref'],samples=detail['sample_ids'],
            span=detail['measured_span'],range_value=detail['range_value'],fitness=detail['fitness'],reasons=detail['reasons'])
    # Reference comparison and a gaps inventory doing the same checks do not form a contrast.
    return dict(work='RECORD_RELATIONSHIP_CHECKS',findings=detail['findings'])
POLICY = dict(version='sentinel.policy.v01', calibration='calibration:sentinel:v01',
              rain_fast_mm_x1000=30000, normal_cadence_seconds=60, fast_cadence_seconds=15,
              critical_displacement_um=5000, critical_reserve_um=5000, max_local_age_seconds=10)


def require(condition, reason):
    if not condition:
        raise ValueError(reason)


def canonical(value):
    return json.dumps(value, sort_keys=True, separators=(',', ':'), ensure_ascii=True, allow_nan=False).encode()


def digest(value):
    return hashlib.sha256(value if isinstance(value, bytes) else canonical(value)).hexdigest()


def identity(kind, value):
    return 'sentinel:'+kind+':'+digest(value)


def measurement(value):
    require(type(value) is dict and set(value)=={'sensor', 'value', 'unit', 'scenario_tick', 'healthy', 'calibration'}, 'measurement_shape')
    require(value['sensor'] in ('rainfall', 'displacement', 'reserve','channel_level','vibration'), 'measurement_sensor')
    require(type(value['value']) is int and 0 <= value['value'] <= 10000000, 'measurement_missing_or_range')
    require(value['unit']=={'rainfall':'mm_x1000','channel_level':'synthetic_level_mm','vibration':'synthetic_intensity_milli'}.get(value['sensor'],'um'), 'measurement_units')
    require(type(value['scenario_tick']) is int and value['scenario_tick'] >= 0 and type(value['healthy']) is bool, 'measurement_time_health')
    require(type(value['calibration']) is str and value['calibration'].startswith('calibration:sentinel:'), 'measurement_calibration')
    return dict(value)


def diagnostic(material):
    require(type(material) is dict and set(material) in ({'selection','frames','contract'},
        {'selection','frames','contract','semantic_bindings','checks'},
        {'selection','frames','contract','semantic_bindings','checks','phase'},
        {'selection','frames','contract','semantic_bindings','checks','phase','accepted_plan'}), 'diagnostic_material')
    if 'checks' in material:
        from .semantic_adapter_v01 import validate_material
        validate_material(material)
        if material.get('phase')=='PLAN':
            results=[dict(selection=row['selection'],semantic_ref=row['semantic_ref'],healthy=True,
                action='READ_RESERVE_SERIES' if row['selection']=='INDEPENDENT_RESERVE_SERIES' else 'NONE',
                source_ref='synthetic:reserve_series:v01' if row['selection']=='INDEPENDENT_RESERVE_SERIES' else None,
                input_sha256=digest(row),meaning='ADMITTED_PLAN_NOT_MEASUREMENT_OR_PERMISSION') for row in material['checks']]
            for result,row in zip(results,material['checks'],strict=True):
                if 'investigation' in row:result['investigation']=row['investigation']
        else:results=[diagnostic_check(row,material['contract']) for row in material['checks']]
        return dict(selection=material['selection'],healthy=all(v['healthy'] for v in results),checks=results,
            input_sha256=digest(material),semantic_refs=[v['contribution']['contribution_id'] for v in material['semantic_bindings']],
            contract=material['contract'],stage=material.get('phase','RESULT'))
    selection=material['selection']
    require(selection in DIAGNOSTICS, 'diagnostic_not_admitted')
    frames=tuple(measurement(v) for v in material['frames'])
    require({v['sensor'] for v in frames}=={'rainfall','displacement','reserve'} and len(frames)==3, 'diagnostic_independent_inputs')
    checked=(frames if selection=='REFERENCE_INTEGRITY' else
             tuple(v for v in frames if (v['sensor']=='rainfall')==(selection=='TEMPORAL_CONTEXT_APPLICABILITY')))
    validate_policy(material['contract'])
    result=all(v['healthy'] and v['calibration']==material['contract']['calibration'] for v in checked)
    if selection=='TEMPORAL_CONTEXT_APPLICABILITY':
        result=result and max(v['scenario_tick'] for v in frames)-checked[0]['scenario_tick']<=180
    return dict(selection=selection, healthy=result, checked_sensors=[v['sensor'] for v in checked],
                input_sha256=digest(material), contract=material['contract'])


def diagnostic_check(row,contract):
    from .events_v01 import validate
    records=row['observations'];[validate(v) for v in records]
    selection=row['selection'];require(selection in DIAGNOSTICS,'check_selection')
    if selection=='INDEPENDENT_RESERVE_SERIES':
        series=row['series'];require(series['classification']=='MOCK_SOURCE_READ' and bool(series['receipt_ref']),'series_actual_receipt')
        samples=series['records'];[validate(v) for v in samples]
        require(bool(samples),'series_missing_samples')
        failures=[]
        if series['source_ref']!='synthetic:reserve_series:v01':failures.append('SOURCE_NOT_ADMITTED')
        if not all(v['site']==row['site'] and v['channel']=='reserve' and v['unit']=='um' for v in samples):failures.append('SOURCE_SCOPE_OR_UNITS')
        if not all(v['calibration']==contract['calibration'] for v in samples):failures.append('CALIBRATION_INCOMPATIBLE')
        primary={v['lineage'] for v in records if v['channel']=='displacement'}
        if not primary or len({v['lineage'] for v in samples})!=1 or any(v['lineage'] in primary for v in samples):failures.append('NOT_INDEPENDENT')
        if not all(v['status']=='HEALTHY' and v['value'] is not None for v in samples):failures.append('MISSING_OR_INADEQUATE')
        if len(samples)<SERIES_POLICY['minimum_samples'] or len({v['observation_id'] for v in samples})!=len(samples):failures.append('SAMPLE_COUNT_OR_DUPLICATE')
        if any(not (left['observed_end']<right['observed_start'] and left['sequence']<right['sequence'] and
            right['observed_end']-left['observed_end']<=SERIES_POLICY['maximum_gap']) for left,right in zip(samples,samples[1:])):failures.append('ORDER_OR_GAP')
        if samples[-1]['observed_end']-samples[0]['observed_end']<SERIES_POLICY['minimum_span']:failures.append('INSUFFICIENT_WINDOW')
        if not 0<=row['tick']-samples[-1]['observed_end']<=SERIES_POLICY['newest_max_age']:failures.append('STALE_LATEST_SAMPLE')
        if any(v['received']>row['tick'] for v in samples):failures.append('FUTURE_RECEIPT')
        values=[v['value'] for v in samples if v['value'] is not None]
        spread=max(values)-min(values) if values else None
        fitness=not failures;healthy=fitness and spread<=SERIES_POLICY['maximum_range_um']
        detail=dict(sample_ids=[v['observation_id'] for v in samples],receipt_ref=series['receipt_ref'],
            source_ref=series['source_ref'],range_value=spread,fitness='ELIGIBLE' if fitness else 'INELIGIBLE',
            reasons=failures,outcome='BOUNDED_CONSISTENT' if healthy else 'UNRESOLVED_OR_INCONSISTENT',
            measured_span=samples[-1]['observed_end']-samples[0]['observed_end'],policy=SERIES_POLICY)
    elif 'investigation' in row:
        detail=investigation_findings(row,contract)
        healthy=all(v['status']=='SUPPORTED' for v in detail['findings'])
        detail['outcome']='SUPPORTED_FOR_DECLARED_USE' if healthy else 'NOT_SUPPORTED_FOR_DECLARED_USE'
    elif selection=='TEMPORAL_CONTEXT_APPLICABILITY':
        healthy=bool(records) and all(0<=row['tick']-v['observed_end']<=60 and v['received']<=row['tick'] for v in records)
        detail=dict(applicability='CURRENT_CONTEXT' if healthy else 'HISTORICAL_OR_INAPPLICABLE',
            measured=[v['observed_end'] for v in records],received=[v['received'] for v in records],
            scope='TEMPORAL_ONLY_NOT_SPATIAL_OR_LOCAL_SENSOR_AUTHORITY')
    elif selection=='SPATIAL_CONTEXT_APPLICABILITY':
        healthy=bool(records) and all(v['site']==row['site'] for v in records)
        detail=dict(applicability='MATCHING_SYNTHETIC_CONTEXT_SCOPE' if healthy else 'NO_VERIFIED_SITE_MAPPING',
            sites=sorted({v['site'] for v in records}),target_site=row['site'],physical_sensor_claim=False)
    elif selection=='EVIDENCE_GAPS':
        missing=['PHYSICAL_ZERO_CHECK_CERTIFICATION_NOT_PROVIDED']
        if not records:missing.append('MEASUREMENTS_MISSING')
        if any(v['status']!='HEALTHY' for v in records):missing.append('INADEQUATE_CHANNEL')
        healthy=False;detail=dict(outcome='NEEDS_EVIDENCE',missing=missing,source_ids=[v['observation_id'] for v in records])
    else:
        healthy=bool(records) and len({v['lineage'] for v in records})==len(records)
        healthy=healthy and all(v['status']=='HEALTHY' and v['calibration']==contract['calibration'] for v in records)
        detail=dict(independent_lineages=sorted({v['lineage'] for v in records}),source_ids=[v['observation_id'] for v in records],
            outcome='METADATA_CONSISTENT' if healthy else 'METADATA_INCONSISTENT',physical_zero_check='NOT_ESTABLISHED')
    result=dict(selection=selection,healthy=healthy,detail=detail,semantic_ref=row['semantic_ref'],input_sha256=digest(row))
    if 'investigation' in row:result['investigation']=row['investigation']
    return result


def cadence(rainfall,policy=None):
    policy=validate_policy(POLICY if policy is None else policy)
    value=measurement(rainfall)
    require(value['sensor']=='rainfall' and value['healthy'], 'rainfall_unavailable')
    require(value['calibration']==policy['calibration'],'rainfall_current_calibration')
    return policy['fast_cadence_seconds'] if value['value'] >= policy['rain_fast_mm_x1000'] else policy['normal_cadence_seconds']


def critical(frames, tick, policy=None):
    policy=validate_policy(POLICY if policy is None else policy)
    measured={v['sensor']:measurement(v) for v in frames}
    local=[measured[k] for k in ('displacement','reserve')]
    return (all(v['healthy'] and 0 <= tick-v['scenario_tick'] <= policy['max_local_age_seconds'] for v in local)
            and local[0]['value'] >= policy['critical_displacement_um']
            and local[1]['value'] >= policy['critical_reserve_um'])


def observability(material):
    from .events_v01 import validate
    require(set(material)=={'records','tick','site','policy','purpose'},'observability_shape')
    require(material['purpose'] in ('local','channel'),'observability_purpose')
    policy=material['policy'];validate_policy(policy)
    channels=('displacement','reserve') if material['purpose']=='local' else ('channel_level','vibration')
    records=material['records'];[validate(v) for v in records]
    current=[v for v in records if v['channel'] in channels and v['status']=='HEALTHY' and v['site']==material['site']
        and v['calibration']==policy['calibration'] and 0<=material['tick']-v['observed_end']<=policy['max_local_age_seconds']]
    independent=len(current)==2 and len({v['channel'] for v in current})==2 and len({v['lineage'] for v in current})==2
    coincident=independent and max(v['observed_start'] for v in current)<=min(v['observed_end'] for v in current)
    limits=(policy['critical_displacement_um'],policy['critical_reserve_um']) if material['purpose']=='local' else (500,700)
    floor=coincident and all(next(v['value'] for v in current if v['channel']==ch)>=lim for ch,lim in zip(channels,limits))
    return dict(observability='ADEQUATE' if coincident else 'LIMITED' if current else 'INSUFFICIENT',hard_critical=bool(floor),
        source_ids=[v['observation_id'] for v in current],input_sha256=digest(material),policy=policy,purpose=material['purpose'])


def validate_policy(policy):
    require(type(policy) is dict and set(policy)==set(POLICY),'policy_closed_shape')
    require(type(policy['version']) is str and policy['version'].startswith('sentinel.policy.'),'policy_revision')
    require(type(policy['calibration']) is str and policy['calibration'].startswith('calibration:sentinel:'),'policy_calibration')
    require(all(type(policy[k]) is int and policy[k]>0 for k in POLICY if k not in ('version','calibration')),'policy_integer')
    require((policy['normal_cadence_seconds'],policy['fast_cadence_seconds'])==(60,15),'unsupported_cadence_policy')
    return policy
