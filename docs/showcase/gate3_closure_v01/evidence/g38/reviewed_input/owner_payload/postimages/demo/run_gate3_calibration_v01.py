"""Inspect, execute once, verify supplied output, or replay saved G35 data."""
import argparse
import json
from pathlib import Path
from hedgehog import outcome_feedback_v01 as f, outcome_feedback_report_v01 as reports


def gemini_adversary_origins_v01(directory,config_path,retained=None):
    """Opt-in finite transport. Preserve every attempt, never retry a valid reply."""
    import ast,hashlib,os,time
    from hedgehog.domains.supplier_water_filter import adversarial_feedback_v01 as supplier
    settings={}
    if config_path:
        for node in ast.parse(Path(config_path).read_text()).body:
            if isinstance(node,ast.Assign) and len(node.targets)==1 and isinstance(node.targets[0],ast.Name) and node.targets[0].id in ('GOOGLE_API_KEY','GEMINI_MODEL'):
                settings[node.targets[0].id]=ast.literal_eval(node.value)
    key=next((os.environ[k] for k in ('HEDGEHOG_GEMINI_API_KEY','GOOGLE_API_KEY','GEMINI_API_KEY','GOOGLE_GEMINI_API_KEY') if os.environ.get(k)),settings.get('GOOGLE_API_KEY'))
    model=os.environ.get('HEDGEHOG_LIVE_PROVIDER_MODEL') or settings.get('GEMINI_MODEL')
    if not key or not model:raise ValueError('g36_configured_gemini_missing')
    from google import genai
    directory=Path(directory);directory.mkdir(parents=True,exist_ok=False)
    schema=json.loads((Path(__file__).resolve().parents[1]/'schemas/gate3_adversary_v01.schema.json').read_bytes())
    response_schema=schema['$defs']['advice']
    # Resolve only these three local finite response definitions for the SDK.
    response_schema=json.loads(f.g35_bytes_v01(response_schema))
    response_schema['properties']['evidence_refs']=schema['$defs']['refs']
    response_schema['properties']['expected_fp']=schema['$defs']['expectation']
    limits=supplier.reference_v01()['provider_transport']
    for case in ('ADV-1','ADV-2','ADV-3','CONTINUE'):
        request=supplier.request_v01('LIVE_OBSERVATION',case)
        previous=Path(retained)/(case+'_origin.json') if retained else None
        if previous is not None and previous.exists():
            raw_previous=previous.read_bytes();origin=json.loads(raw_previous)
            if origin['request_sha256']!=supplier.digest(request) or origin['response_sha256']!=hashlib.sha256(origin['raw_response'].encode()).hexdigest():
                raise ValueError('g36_captured_input_mismatch')
            origin=dict(origin,source_class='GEMINI_CAPTURED_REEXECUTION')
            (directory/(case+'_origin.json')).write_bytes(f.g35_bytes_v01(origin))
            (directory/(case+'_reuse.json')).write_bytes(f.g35_bytes_v01(dict(mode='CAPTURED_REEXECUTION',original_sha256=hashlib.sha256(raw_previous).hexdigest(),new_provider_calls=0)))
            print(json.dumps(dict(case=case,status='CAPTURED_REEXECUTION')),flush=True)
            yield origin
            continue
        origin=None
        for ordinal in range(1,limits['attempts_per_request']+1):
            dest=directory/(case+'_'+str(ordinal));dest.mkdir()
            generation=dict(response_mime_type='application/json',response_json_schema=response_schema,temperature=0,candidate_count=1,max_output_tokens=4096)
            (dest/'request.json').write_bytes(f.g35_bytes_v01(dict(request=request,model=model,generation=generation,request_sha256=supplier.digest(request))))
            receipt=dict(case=case,attempt=ordinal,status='STARTED',provider='Gemini',model=model,sdk_attempts=1,money='UNKNOWN')
            (dest/'receipt.json').write_bytes(f.g35_bytes_v01(receipt));start=time.monotonic_ns();raw=''
            try:
                client=genai.Client(api_key=key,http_options={'timeout':limits['timeout_seconds']*1000,'retry_options':{'attempts':1}})
                try:response=client.models.generate_content(model=model,contents=f.g35_bytes_v01(request).decode(),config=generation)
                finally:client.close()
                raw=response.text or ''
                usage=getattr(response,'usage_metadata',None)
                receipt.update(status='RESPONSE',response_id=getattr(response,'response_id',None),model_version=getattr(response,'model_version',None),
                    usage=None if usage is None else usage.model_dump(mode='json'),finish_reasons=[str(v.finish_reason) for v in response.candidates or ()])
                (dest/'response.txt').write_text(raw)
                origin=dict(raw_response=raw,response_sha256=hashlib.sha256(raw.encode()).hexdigest(),source_class='GEMINI_LIVE_CAPTURE',revision=str(model),
                    response_id=receipt['response_id'],request_sha256=supplier.digest(request),status='RESPONSE',tokens=getattr(usage,'total_token_count',None),elapsed_us=(time.monotonic_ns()-start)//1000)
            except Exception as error:
                # Do not include transport exception strings, headers or credentials.
                receipt.update(status='TRANSPORT_FAILED',error_type=type(error).__name__)
            finally:
                receipt['elapsed_us']=(time.monotonic_ns()-start)//1000
                receipt['response_sha256']=hashlib.sha256(raw.encode()).hexdigest()
                (dest/'receipt.json').write_bytes(f.g35_bytes_v01(receipt))
            if origin is not None:break
            if ordinal<limits['attempts_per_request']:time.sleep(limits['backoff_seconds'])
        if origin is None:
            origin=dict(raw_response='',response_sha256=hashlib.sha256(b'').hexdigest(),source_class='GEMINI_LIVE_CAPTURE',revision=str(model),response_id=None,
                request_sha256=supplier.digest(request),status='TRANSPORT_FAILED',tokens=None,elapsed_us=receipt['elapsed_us'])
        (directory/(case+'_origin.json')).write_bytes(f.g35_bytes_v01(origin))
        print(json.dumps(dict(case=case,status=origin['status'],provider_seconds=origin['elapsed_us']/1000000)),flush=True)
        yield origin


def main():
    parser=argparse.ArgumentParser()
    parser.add_argument('mode',choices=('inspect','collect','run','verify','replay','controlled-adversary','live-adversary','captured-adversary','verify-adversary','replay-adversary'))
    parser.add_argument('--output',type=Path)
    parser.add_argument('--report',type=Path);parser.add_argument('--sources',type=Path);parser.add_argument('--baseline',type=Path)
    parser.add_argument('--config',type=Path)
    parser.add_argument('--captures',type=Path,help='Exact saved origins after an engineering interruption; no new independent samples')
    parser.add_argument('--originals',type=Path,help='Independent first completed native outcome directory')
    parser.add_argument('--original-pins',type=Path,help='Independent SHA256 manifest of the original outcomes')
    args=parser.parse_args()
    if args.mode in ('controlled-adversary','live-adversary','captured-adversary'):
        from hedgehog import gate3_mechanism_v01 as mechanism
        if args.output is None:parser.error('--output external directory required')
        live=args.mode in ('live-adversary','captured-adversary');originals=None
        if args.mode=='captured-adversary':
            from hedgehog.domains.supplier_water_filter import adversarial_feedback_v01 as supplier
            import hashlib
            if any(v is None for v in (args.captures,args.originals,args.original_pins)):parser.error('captured execution requires --captures --originals --original-pins')
            pins=json.loads(args.original_pins.read_bytes());originals={};origins=[]
            for case in ('ADV-1','ADV-2','ADV-3','CONTINUE'):
                raw=(args.originals/(case+'_source.json')).read_bytes()
                if hashlib.sha256(raw).hexdigest()!=pins[case]:raise ValueError('g36r_original_external_pin')
                supplier.validate_action_source_v01(supplier.ActionAdviceSourceContextV01(raw))
                originals[case]=raw;origin=json.loads((args.captures/(case+'_origin.json')).read_bytes())
                origins.append(dict(origin,source_class='GEMINI_CAPTURED_REEXECUTION'))
        else:
            origins=gemini_adversary_origins_v01(args.output.parent/(args.output.name+'_captures'),args.config,args.captures) if live else None
        if args.mode=='live-adversary' and args.captures:
            parser.error('Use captured-adversary with independently pinned original outcomes')
        bundle=mechanism.collect_mechanism_v01(args.output,lane='LIVE_OBSERVATION' if live else 'CONTROLLED_BOUNDARY',origins=origins,originals=originals)
        print(json.dumps(dict(report_id=bundle['report']['report_id'],live_harmful_observed=bundle['report']['live_harmful_observed'],output=str(args.output))))
        return 0
    if args.mode in ('inspect','collect'):value=reports.inventory_v01()
    elif args.mode=='run':
        if args.output is None:parser.error('--output external directory required')
        from demo.gate3_scenario_packs_v01 import collect_pack_v01
        value=collect_pack_v01(args.output)
        print(json.dumps(dict(report_id=value['report_id'],output=str(args.output))))
        return 0
    else:
        if any(v is None for v in (args.report,args.sources,args.baseline)):parser.error('--report --sources --baseline are required independently')
        inputs=dict(report=json.loads(args.report.read_bytes()),sources=json.loads(args.sources.read_bytes()),baseline=json.loads(args.baseline.read_bytes()))
        module=reports
        if args.mode.endswith('-adversary'):
            from hedgehog import gate3_mechanism_v01 as module
        if args.mode in ('verify','verify-adversary'):
            reasons=module.validate_supplied_report_v01(**inputs)
            value=dict(status='FAIL_CLOSED' if reasons else 'PASS',reason_codes=list(reasons))
        else:value=module.replay_v01(**inputs)
    body=f.g35_bytes_v01(value)+b'\n'
    if args.output is not None:
        with args.output.open('xb') as stream:stream.write(body)
    else:print(body.decode(),end='')
    return int(args.mode in ('verify','verify-adversary') and bool(value['reason_codes']))


if __name__=='__main__':raise SystemExit(main())
