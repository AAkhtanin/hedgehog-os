"""Pure G35 supplied verification and safe-derived replay; no runtime collection."""
import json
from pathlib import Path
from hedgehog import outcome_feedback_v01 as f

BASE='d199199a578c078c913a2381f595549175bd9235'


def inventory_v01():
    value=json.loads((Path(__file__).resolve().parents[1]/'fixtures/gate3_domain_cases_v01.json').read_bytes())
    f._keys(value,('version','pack_id','accepted_baseline_ref','cases','pending','comparison_projection'))
    f._require(value['version']=='v0.1' and value['accepted_baseline_ref']==BASE,'g35_inventory_base')
    f._require([v['domain_id'] for v in value['cases']]==list(f.G35_DOMAINS),'g35_inventory_coverage')
    for index,row in enumerate(value['cases']):
        f._keys(row,('pack_id','pack_version','family_ids','domain_id','root_scope_ids','scenario_refs','input_lane','source_profile_refs',
            'accepted_baseline_ref','public_entrypoint_binding','observation_extractor_profile','feedback_profile_id','metric_profile_id','invariant_tags','input_policy','cost'))
        f._require(row['source_profile_refs']==[f.G35_PROFILES[index]] and row['input_lane']=='CONTROLLED_RUNTIME' and
            row['pack_id']=='G35-'+row['domain_id'] and row['accepted_baseline_ref']==BASE,'g35_descriptor_binding')
    return value


def build_baseline_v01(sources,*,explicit_times):
    """Collector-owned anchor to retain separately from the report under review."""
    inventory=inventory_v01()
    f._keys(explicit_times,('ingested_time','evaluated_at','timestamp'))
    return dict(profile='G35_INDEPENDENT_SAVED_BASELINE_V01',owner_base=BASE,inventory_sha256=f.g35_hash_v01(inventory),explicit_times=dict(explicit_times),
        sources=[dict(case_id=v['case_id'],sha256=f.g35_hash_v01(v),source_revision=v['source_revision']) for v in sources])


def _checked_sources(sources,baseline):
    f._keys(baseline,('profile','owner_base','inventory_sha256','sources','explicit_times'))
    f._require(type(sources) is list and len(sources)==5,'g35_source_coverage')
    f._require([s['domain'] for s in sources]==list(f.G35_DOMAINS),'g35_source_order')
    f._require(baseline==build_baseline_v01(sources,explicit_times=baseline['explicit_times']),'g35_independent_baseline_mismatch')
    return inventory_v01()


def build_report_v01(*,sources,baseline,explicit_times):
    # Own the entire finite invocation snapshot; never retain caller mutable data.
    sources,baseline,explicit_times=json.loads(f.g35_bytes_v01([sources,baseline,explicit_times]))
    inventory=_checked_sources(sources,baseline)
    f._keys(explicit_times,('ingested_time','evaluated_at','timestamp'))
    f._require(explicit_times==baseline['explicit_times'],'g35_independent_time_binding')
    rows=[]
    for source in sources:
        observations=[]
        for ordinal,(fact,obs,plain) in enumerate(f._g35_derive_source_observations_v01(source,explicit_times)):
            observations.append(dict(occurrence=ordinal,observation=json.loads(obs.canonical),feedback=plain,
                metrics=dict(domain=source['domain'],root=fact['root'],lane='CONTROLLED_RUNTIME',unique_occurrences=1,deliveries=1,
                    attempts=1,refusals=int(fact['enforcement']=='BLOCKED_AS_REQUIRED'),lawful_effects=fact['effect_count'],unexpected_effects=0,
                    scorable_count=0,not_scorable=['NO_PROSPECTIVE_COMPARABLE_EXPECTATION'],brier=dict(state='UNKNOWN',N=0,numerator=None,denominator=None),
                    rating='NOT_APPLICABLE',prior='NOT_APPLICABLE',trust='NOT_APPLICABLE',consumed_drs_records=[],
                    work_invocations=fact['work_count'],quality=fact['quality'],enforcement=fact['enforcement'],task=fact['task'])))
        rows.append(dict(case_id=source['case_id'],domain=source['domain'],source_profile=source['profile'],source_ref=f.g35_hash_v01(source),
            source_revision=source['source_revision'],measurement=source['measurement'],observations=observations,
            replay_level='SAFE_DERIVED_PUBLIC_SOURCE_RELATIONS',native_replay='UNSUPPORTED_NATIVE_SCHEMA',current_history='NO_UPDATE_NOT_WRITTEN'))
    material=dict(profile='G35_FIVE_DOMAIN_REPORT_V01',version='v0.1',inventory=inventory,inventory_hash=f.g35_hash_v01(inventory),
        baseline_ref=f.g35_hash_v01(baseline),explicit_times=explicit_times,rows=rows,
        non_authority=dict(claims_permission=False,claims_root_decision=False,requests_effect=False),
        aggregate=dict(domains=5,unique_occurrences=sum(len(v['observations']) for v in rows),scorable_count=0,model_calls=0,
            tokens='UNKNOWN',money='UNKNOWN',currency='UNKNOWN',cross_root_rating='NOT_APPLICABLE'),pending=inventory['pending'])
    return dict(material,report_id=f.g35_hash_v01(material))


def _checked_supplied_report_v01(report,sources,baseline):
    f._require(type(report) is dict,'g35_report_shape')
    supplied=f.g35_bytes_v01(report)
    snapshot=json.loads(supplied)
    expected=build_report_v01(sources=sources,baseline=baseline,explicit_times=snapshot['explicit_times'])
    f._require(supplied==f.g35_bytes_v01(expected),'g35_supplied_report_mismatch')
    return expected


def _supplied_error_v01(exc):
    return (str(exc) if str(exc).startswith('g35_') else 'g35_supplied_invalid',)


def validate_supplied_report_v01(report,*,sources,baseline):
    try:
        _checked_supplied_report_v01(report,sources,baseline)
        return ()
    except (ValueError,KeyError,TypeError,AttributeError,IndexError,StopIteration) as exc:
        return _supplied_error_v01(exc)


def replay_v01(*,report,sources,baseline):
    try:expected=_checked_supplied_report_v01(report,sources,baseline)
    except (ValueError,KeyError,TypeError,AttributeError,IndexError,StopIteration) as exc:
        raise ValueError('g35_replay_supplied_invalid:'+repr(_supplied_error_v01(exc))) from exc
    return dict(profile='G35_PURE_REPLAY_V01',report=expected,
        derivation='SOURCE_VALIDATION_NORMALIZATION_NO_SCORABLE_EVENTS',new_samples=0,new_history_writes=0,
        new_current_decisions=0,permission_restored=False,native_schema='UNSUPPORTED_NATIVE_SCHEMA')
