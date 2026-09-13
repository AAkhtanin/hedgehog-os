"""Testflix controlled, live semantic, captured execution and pinned offline replay."""
import argparse
from dataclasses import replace
import json
from pathlib import Path
import traceback
from hedgehog.domains.testflix import contracts_v01 as contracts
from hedgehog.domains.testflix import evidence_v01 as evidence


def reject_duplicates_v01(pairs):
    result = {}
    for key,value in pairs:
        if key in result:
            raise ValueError('duplicate_json_key:'+key)
        result[key] = value
    return result


def main():
    parser = argparse.ArgumentParser()
    modes = parser.add_subparsers(dest='mode',required=True)
    for name in ('deterministic','history','renewal'):
        controlled = modes.add_parser(name)
        controlled.add_argument('--input',type=Path,required=True)
        controlled.add_argument('--output',type=Path,required=True)
    replay = modes.add_parser('replay')
    replay.add_argument('--input',type=Path,required=True)
    replay.add_argument('--expected-manifest-hash',required=True)
    for name in ('live','captured'):
        current = modes.add_parser(name)
        current.add_argument('--input',type=Path,required=True)
        current.add_argument('--output',type=Path,required=True)
        current.add_argument('--renewal',action='store_true')
        if name=='live':
            current.add_argument('--captures',type=Path,required=True)
            current.add_argument('--config',type=Path)
            current.add_argument('--category',choices=('main','AB'),default='main')
        else:
            current.add_argument('--semantic-records',type=Path,required=True)
    viewer = modes.add_parser('render')
    viewer.add_argument('--input',type=Path,required=True)
    viewer.add_argument('--output',type=Path,required=True)
    args = parser.parse_args()
    source = json.loads(args.input.read_text(),object_pairs_hook=reject_duplicates_v01)
    failures=[]
    if args.mode=='render':
        from hedgehog.domains.testflix.viewer_v01 import render_v01
        render_v01(source,args.output)
        print(json.dumps(dict(output=str(args.output),provider_calls=0,real_adapter_calls=0)))
        return 0
    if args.mode in ('live','captured'):
        from hedgehog.domains.testflix.live_semantic_adapter_v01 import LiveSemanticProviderV01, CapturedSemanticProviderV01
        from hedgehog.domains.testflix.demo_story_v01 import run_story_v01
        if args.mode=='live':
            provider=LiveSemanticProviderV01(directory=args.captures,config_path=args.config,category=args.category)
        else:
            records=json.loads(args.semantic_records.read_text(),object_pairs_hook=reject_duplicates_v01)
            contracts.require_v01(type(records) is dict and set(records)=={'profile','mode','records'} and
                records['profile']=='testflix.semantic_records.v01' and records['mode']=='LIVE_CAPTURED',
                'captured_records_profile')
            provider=CapturedSemanticProviderV01(records['records'])
        result=run_story_v01(contracts.request_from_plain_v01(source),provider,directory=args.output,
            renewal=args.renewal,progress=lambda name,event,seconds:print(json.dumps(
                dict(phase=name,event=event,seconds=seconds)),flush=True))
        if args.mode=='captured':
            contracts.require_v01(provider.position==len(provider.records),'captured_unused_responses')
        print(json.dumps(result,sort_keys=True))
        return 0
    if args.mode in ('deterministic','history','renewal'):
        request = contracts.request_from_plain_v01(source)
        handler = evidence.TestflixHandlerV01()
        report = handler.handle_v01(request)
        if args.mode in ('history','renewal'):
            handler.advance_clock_v01(request.now+10)
            handler.handle_event_v01(contracts.InformationRequestV01(request.request_id+':information',request.user_id,
                report['entitlement'].entitlement_id,handler.now))
            handler.advance_clock_v01(request.now+20)
            handler.handle_event_v01(contracts.StopPlaybackV01(request.request_id+':stop',request.user_id,
                report['session'].session_id,handler.now))
            handler.advance_clock_v01(request.now+30)
            fresh=handler.handle_event_v01(contracts.PlaybackRequestV01(request.request_id+':fresh',request.user_id,
                report['entitlement'].entitlement_id,request.device_id,request.content_id,handler.now,3600,720))
            if args.mode=='renewal':
                handler.advance_clock_v01(report['entitlement'].candidate.valid_to-86400)
                quote=contracts.ProviderQuoteV01(report['entitlement'].candidate.plan,request.merchant_id,request.currency,
                    handler.now,handler.now+3600,None)
                handler.observe_quote_v01(quote)
                intent=contracts.RenewalIntentV01(request.request_id+':renewal-intent',request.user_id,report['entitlement'].entitlement_id,
                    quote.quote_id,request.order_id+':next-period',handler.now,650,True)
                pending=handler.prepare_renewal_v01(intent)
                handler.advance_clock_v01(intent.now+30)
                changed=contracts.ProviderQuoteV01(replace(quote.plan,price_minor=700),quote.merchant_id,quote.currency,
                    handler.now,handler.now+3600,quote.quote_id)
                handler.observe_quote_v01(changed);handler.advance_clock_v01(intent.now+31)
                try:handler.reprice_pending_v01()
                except ValueError as error:
                    traceback.print_exc()
                    failures.append(dict(stage='PUBLIC_E_REPRICE',reason=str(error),
                        preparation_time=intent.now,quote_observed_at=changed.observed_at,
                        evaluation_time=handler.hosts['bank'][1].snapshot.evaluation_time,
                        packet=evidence.plain_value_v01(pending['payment']['bound'])))
                handler.advance_clock_v01(report['entitlement'].candidate.valid_to+1)
                handler.handle_event_v01(contracts.StopPlaybackV01(request.request_id+':expiry-stop',request.user_id,
                    fresh['session'].session_id,handler.now))
                handler.grant_device_v01(contracts.DeviceGrantRequestV01(request.request_id+':new-device-basis',request.user_id,
                    request.device_id,request.content_id,handler.now,handler.now+86400,1080))
                quote=contracts.ProviderQuoteV01(replace(quote.plan,price_minor=700),quote.merchant_id,quote.currency,
                    handler.now,handler.now+3600,changed.quote_id)
                handler.observe_quote_v01(quote)
                renewed=handler.renew_v01(contracts.RenewalIntentV01(request.request_id+':explicit-new-consent',request.user_id,
                    report['entitlement'].entitlement_id,quote.quote_id,request.order_id+':explicit-renewal',handler.now,700,True))
                period=renewed['renewal']
                handler.advance_clock_v01(handler.now+10)
                handler.handle_event_v01(contracts.StopPlaybackV01(request.request_id+':renewed-stop',request.user_id,
                    period['session'].session_id,handler.now))
                handler.handle_event_v01(contracts.PlaybackRequestV01(request.request_id+':renewed-fresh',request.user_id,
                    period['entitlement'].entitlement_id,request.device_id,request.content_id,handler.now,60,720))
                with args.output.with_suffix('.failures.json').open('x') as stream:
                    json.dump(failures,stream,sort_keys=True);stream.write('\n')
            package = evidence.seal_history_v01(handler.history_v01())
        else:
            package = evidence.seal_report_v01(report)
        with args.output.open('x') as stream:
            stream.write(json.dumps(package,sort_keys=True,separators=(',',':'))+'\n')
        print(json.dumps(dict(manifest_hash=package['manifest_hash'],output=str(args.output),generation_mode='CONTROLLED_DETERMINISTIC',
            result='PARTIAL' if failures else 'RECORDED',failed_stages=[v['stage'] for v in failures])))
    else:
        if source['payload'].get('profile') in ('testflix.controlled.history.v01','testflix.history.v02'):
            result = evidence.replay_history_v01(source,expected_manifest_hash=args.expected_manifest_hash)
        else:
            result = evidence.replay_v01(source,expected_manifest_hash=args.expected_manifest_hash)
        print(json.dumps(result,sort_keys=True))
    return 1 if failures else 0


if __name__=='__main__':
    raise SystemExit(main())
