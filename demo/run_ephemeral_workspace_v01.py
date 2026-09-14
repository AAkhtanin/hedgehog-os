"""Owned synthetic photo demo. Automated runs reap all services before exit."""
import argparse
import json
from pathlib import Path
import time
from demo.ephemeral_workspace_fixtures_v01 import generate,generate_media
from hedgehog.domains.ephemeral_workspace import contracts_v01 as c
from hedgehog.domains.ephemeral_workspace.semantic_roles_v01 import ControlledProvider
from hedgehog.domains.ephemeral_workspace.semantic_adapter_v01 import LiveProvider,LiveStageBudget,CapturedProvider,load_capture_origin,parse
from hedgehog.domains.ephemeral_workspace.session_runtime_v01 import Workspace
from hedgehog.domains.ephemeral_workspace.evidence_v01 import save_report
from hedgehog.domains.ephemeral_workspace.viewer_v01 import Viewer


def main():
    parser=argparse.ArgumentParser()
    parser.add_argument('--run-dir')
    parser.add_argument('--mode',choices=('controlled','live','captured'),default='controlled')
    parser.add_argument('--contrast',action='store_true')
    parser.add_argument('--interactive',action='store_true')
    parser.add_argument('--mixed',action='store_true',help='Make synthetic video and headless PCM available to the semantic roles.')
    parser.add_argument('--stage-budget',help='Durable shared EWS-3 main/contrast live attempt ledger.')
    parser.add_argument('--transport-ceiling',type=int,default=12,help='Explicit stage ceiling, up to 50; preserve tighter per-chain and token limits.')
    parser.add_argument('--speech-review',action='store_true',help='Controlled audio-essential neighboring task; no automatic intelligibility claim.')
    parser.add_argument('--lifetime',type=int,default=1200)
    parser.add_argument('--config')
    parser.add_argument('--captures',help='Shared live budget for live mode, or optional candidate replay ledger directory.')
    parser.add_argument('--captured-records',help='Optional candidate records; must equal the independently bound original.')
    parser.add_argument('--original-return-root',help='Read-only extracted original return containing MANIFEST.json.')
    parser.add_argument('--original-manifest-sha256',help='Required independent pin, never derived from candidate records or ledger.')
    parser.add_argument('--replay-mode',choices=('live','controlled'),help='Explicit original provenance, not the candidate record mode.')
    parser.add_argument('--original-records-path',help='Original manifest-relative semantic capture path.')
    parser.add_argument('--original-attempts-path',help='Original manifest-relative attempts.json; required only for live-origin replay.')
    parser.add_argument('--capture-source-only',action='store_true',help='Validate and consume original contexts only; no Workspace, fixtures or services.')
    args=parser.parse_args()
    mixed=args.mixed or args.speech_review
    c.require(not args.speech_review or args.mode=='controlled','speech_neighbor_controlled')
    c.require(30<=args.lifetime<=1200,'bounded_interactive_lifetime')
    c.require(not args.capture_source_only or args.mode=='captured','source_only_requires_capture')
    provider=ControlledProvider()
    if args.mode=='live':
        c.require(args.captures is not None,'shared_capture_budget_required')
        c.require(not mixed or args.stage_budget is not None,'mixed_live_stage_budget_required')
        budget=LiveStageBudget(args.stage_budget,dict(main=c.REQUEST_MIXED,contrast=c.REQUEST_B),transport_ceiling=args.transport_ceiling) if args.stage_budget else None
        provider=LiveProvider(args.captures,args.config,stage_budget=budget,chain=('contrast' if args.contrast else 'main') if budget else None)
    elif args.mode=='captured':
        c.require(all((args.original_return_root,args.original_manifest_sha256,args.replay_mode,args.original_records_path)),
            'independent_capture_origin_required')
        origin=load_capture_origin(args.original_return_root,manifest_sha256=args.original_manifest_sha256,
            expected_mode='LIVE' if args.replay_mode=='live' else 'CONTROLLED_DETERMINISTIC',
            records_path=args.original_records_path,attempts_path=args.original_attempts_path)
        c.require(args.replay_mode=='live' or args.captures is None,'capture_controlled_no_live_ledger')
        records=parse(Path(args.captured_records).read_bytes()) if args.captured_records else parse(origin.records_bytes)
        attempts=parse((Path(args.captures)/'attempts.json').read_bytes()) if args.captures else parse(origin.attempts_bytes)
        provider=CapturedProvider(records,attempts,origin=origin)
        asset_bound='asset_inventory' in records[0]['context']
        if args.capture_source_only:
            for record in records:
                provider.respond(record['role'],record['context'])
            print(json.dumps(dict(phase='CAPTURE_SOURCE_ONLY',original_mode=origin.expected_mode,
                manifest_sha256=origin.manifest_sha256,roles=provider.index,attempts=len(attempts),
                asset_binding='RECORDED' if asset_bound else 'HISTORICAL_CONTEXT_WITHOUT_ASSET_INVENTORY',
                workspace_execution='NOT_PERFORMED',new_model_calls=0)),flush=True)
            return
        c.require(asset_bound,'historical_capture_without_asset_inventory_source_only')
    c.require(args.run_dir is not None,'run_directory_required')
    directory=Path(args.run_dir)
    directory.mkdir(parents=True,exist_ok=False,mode=0o700)
    print(json.dumps(dict(phase='SOURCE_FIXTURES',mode=args.mode)),flush=True)
    assets=generate(directory/'sources')
    print(json.dumps(dict(phase='SEMANTICS_AND_WORK')),flush=True)
    media=generate_media(directory/'media_sources') if mixed else None
    request=c.REQUEST_B if args.contrast else c.REQUEST_SPEECH if args.speech_review else c.REQUEST_MIXED if args.mixed else c.REQUEST_A
    workspace=Workspace(directory/'workspace',assets,request,provider,args.lifetime,media=media)
    mixed='media' in workspace.contract
    viewer=None
    try:
        print(json.dumps(dict(phase='OPEN')),flush=True)
        workspace.command('OPEN')
        if mixed:
            workspace.command('SELECT',True);workspace.command('RATE',4);workspace.command('EXPOSURE',3)
            print(json.dumps(dict(phase='COMMON_D_MEDIA_ASSEMBLY')),flush=True)
            workspace.prepare_media()
        save_report(workspace,directory/'evidence')
        if args.interactive:
            viewer=Viewer(workspace)
            # This local launch URL is a credential; do not include it in public evidence.
            print('OWNER_URL='+viewer.owner_url+'/#'+viewer.owner_token,flush=True)
            while workspace.status=='ACTIVE':
                time.sleep(0.5)
                workspace.poll_lifetime()
        else:
            for op,value in ([] if mixed else [('RATE',4),('SELECT',True),('NEXT',None),('PREVIOUS',None)]):
                print(json.dumps(dict(phase='COMMAND',op=op)),flush=True)
                workspace.command(op,value)
            if 'EXPOSURE' in workspace.allowed and not mixed:
                workspace.command('EXPOSURE',4)
                workspace.command('CROP','SQUARE')
            if mixed:
                workspace.command('PLAY');time.sleep(1)
                workspace.command('REVIEW_MEDIA')
                print(json.dumps(dict(phase='ACTUAL_AUDIO_LOSS_AND_COMMON_E')),flush=True)
                workspace.withdraw_audio()
                if not args.speech_review:
                    workspace.command('PLAY');time.sleep(1);workspace.command('PAUSE')
            workspace.command('REQUEST_SAVE')
            approval=workspace.approve(workspace.pending)
            workspace.command('SAVE',approval)
            save_report(workspace,directory/'evidence')
            workspace.close('SCRIPTED_OWNER_END')
    finally:
        if viewer:
            viewer.close()
        workspace.close()
        save_report(workspace,directory/'evidence')
        print(json.dumps(dict(phase='FINAL',status=workspace.status,source_preserved=workspace.report()['source_preserved'])),flush=True)


if __name__=='__main__':
    main()
