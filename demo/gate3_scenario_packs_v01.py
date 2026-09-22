"""Finite controlled G35 orchestration; independent of pure supplied consumers."""
import hashlib
import json
from pathlib import Path
import time
import traceback
from hedgehog import outcome_feedback_v01 as f, outcome_feedback_report_v01 as reports


def collect_pack_v01(directory):
    directory=Path(directory).resolve()
    root=Path(__file__).resolve().parents[1]
    f._require(root not in directory.parents and directory!=root,'g35_external_output_required')
    directory.mkdir(parents=True,exist_ok=False)
    from hedgehog.domains.airline import outcome_feedback_adapter_v01 as airline
    from hedgehog.domains.supplier_water_filter import outcome_feedback_adapter_v01 as supplier
    from hedgehog.domains.testflix import outcome_feedback_adapter_v01 as testflix
    from hedgehog.domains.ephemeral_workspace import outcome_feedback_adapter_v01 as workspace
    from hedgehog.domains.landslide_sentinel import outcome_feedback_adapter_v01 as sentinel
    producers=(airline.collect_source_v01,supplier.collect_source_v01,testflix.collect_source_v01,workspace.collect_source_v01,sentinel.collect_g35_source_v01)
    modules=(airline,supplier,testflix,workspace,sentinel)
    inventory=reports.inventory_v01();sources=[];failures=[]
    (directory/'inventory.json').write_bytes(f.g35_bytes_v01(inventory)+b'\n')
    for index,producer in enumerate(producers):
        domain=f.G35_DOMAINS[index];started=time.time_ns();clock=time.perf_counter_ns()
        with (directory/'phases.jsonl').open('a') as stream:stream.write(json.dumps(dict(domain=domain,phase='COLLECT',event='START',at_ns=str(started)))+'\n')
        print('START '+domain,flush=True)
        try:
            body=producer(directory/domain)
            source=dict(profile=f.G35_PROFILES[index],domain=domain,case_id='G35-'+domain,version='v0.1',body=body,
                measurement=dict(started_ns=str(started),finished_ns=str(time.time_ns()),elapsed_us=(time.perf_counter_ns()-clock)//1000),
                source_revision=hashlib.sha256(Path(modules[index].__file__).read_bytes()).hexdigest())
            (directory/(domain+'.json')).write_bytes(f.g35_bytes_v01(source)+b'\n')
            sources.append(source)
            f.validate_g35_source_v01(source)
            event='RETURN'
        except Exception as exc:
            traceback.print_exc();event='FAILED'
            failure=dict(domain=domain,type=type(exc).__name__,reason=str(exc),traceback=traceback.format_exc())
            failures.append(failure);(directory/(domain+'_failure.json')).write_text(json.dumps(failure,indent=2)+'\n')
        with (directory/'phases.jsonl').open('a') as stream:stream.write(json.dumps(dict(domain=domain,phase='COLLECT',event=event,elapsed_us=(time.perf_counter_ns()-clock)//1000))+'\n')
        print(event+' '+domain,flush=True)
    if failures:raise ValueError('g35_collection_incomplete:'+','.join(v['domain'] for v in failures))
    now=max(int(time.time()),max(int(s['measurement']['finished_ns'])//10**9 for s in sources))
    explicit_times=dict(ingested_time=now,evaluated_at=now,timestamp=now)
    baseline=reports.build_baseline_v01(sources,explicit_times=explicit_times)
    report=reports.build_report_v01(sources=sources,baseline=baseline,explicit_times=explicit_times)
    for name,value in (('sources.json',sources),('independent_baseline.json',baseline),('report.json',report)):
        (directory/name).write_bytes(f.g35_bytes_v01(value)+b'\n')
    return report
