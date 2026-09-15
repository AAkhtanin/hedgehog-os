"""Explicit isolated LS0 execution or disk-only supported evidence verification."""
import argparse
import json
from pathlib import Path
import sys
import time
from hedgehog.domains.landslide_sentinel import contracts_v01 as c
from hedgehog.domains.landslide_sentinel import evidence_v01 as ev
from hedgehog.domains.landslide_sentinel.monitoring_runtime_v01 import Sentinel,SentinelMemory,memory_dependencies
from hedgehog.domains.landslide_sentinel.semantic_adapter_v01 import GeminiHarness
from hedgehog.kernel import abi_v01 as abi

BASE='50ab3916bff55e8034cf7e6c509d4803c5447589'


def main(argv=None):
    parser=argparse.ArgumentParser(description=__doc__)
    commands=parser.add_subparsers(dest='command',required=True)
    run=commands.add_parser('run');run.add_argument('--output',type=Path,required=True)
    run.add_argument('--live-emulator',action='store_true');run.add_argument('--config',type=Path)
    verify=commands.add_parser('verify');verify.add_argument('--package',type=Path,required=True);verify.add_argument('--expected-pin',required=True)
    args=parser.parse_args(argv)
    if args.command=='verify':
        try:result=ev.verify_package(args.package,args.expected_pin)
        except ValueError as error:
            print(json.dumps(dict(status='FAIL_CLOSED',reason=str(error))));return 1
        print(json.dumps(result,sort_keys=True));return 0
    c.require(not args.output.exists(),'run_output_already_exists');args.output.mkdir(parents=True)
    fixture=json.loads((Path(__file__).resolve().parents[1]/'fixtures/landslide_sentinel/ls0_inputs_v01.json').read_text())
    harness=GeminiHarness(args.output/'captures',args.config) if args.live_emulator else None
    started=time.monotonic();ev.phase(args.output,'LS0_RUN_START',live_emulator=args.live_emulator)
    session=Sentinel(args.output/'main',fixture,harness=harness)
    session.prepare_config(reviewed=True)
    native=[]
    for artifact in session.monitor_review['bundle'].queue_artifacts[:1]:
        try:abi.kernel_artifact_to_canonical_ref_v01(artifact)
        except ValueError as error:native.append(dict(artifact_id=artifact.artifact_id,schema=artifact.schema_version,
            status='UNSUPPORTED_NATIVE_SCHEMA',reason=str(error),original=abi.kernel_artifact_to_plain_dict_v01(artifact)))
        else:native.append(dict(artifact_id=artifact.artifact_id,status='SUPPORTED'))
    ev.save(args.output/'native_schema_boundary.json',native)
    session.rainfall_delta()
    session.critical_while_pending()
    store=SentinelMemory(args.output/'local_drs');dep=memory_dependencies(session)
    query=dict(root=session.root,request=session.request,dependency=dep,now=session.source.sample().evaluation_time)
    c.require(store.select(**query) is None,'cold_drs_must_miss')
    record=store.remember(session);warm=SentinelMemory(args.output/'local_drs')
    selected=warm.select(**dict(query,now=session.source.sample().evaluation_time));c.require(selected is not None,'warm_drs_missing')
    consumed=session.pure_consumer('sentinel.information.v01',dict(record_id=record,summary=c.canonical(selected[0]).decode()))
    c.require(warm.select(**dict(query,dependency=dict(dep,calibration='changed'))) is None,'old_calibration_still_current')
    ev.save(args.output/'drs.json',dict(cold=store.events,warm=warm.events,consumed=consumed[1],historical_record=warm.drs.read_record('work',record)))
    package=ev.export_run(session,BASE)
    summary=dict(status='EXECUTION_COMPLETE_PENDING_FRESH_PACKAGE_CHECK',root=session.root,
        P1=session.semantic_evidence['profile'],P2='ACTUAL_E_CONSUMPTION_AND_CONFIGURATION',P3='SAME_HOST_PENDING_RESPONSE_SIGNAL',
        P4='REAL_LOCAL_DRS_DESCENT',P5=package,timings=session.timings,total_seconds=time.monotonic()-started,
        live_calls=0 if harness is None else harness.calls,harness_calls=0 if harness is None else harness.calls,
        site_cloud_calls=0,remote_rainfall_calls=0,real_world_effects=0,mock_effects=len(session.executed),
        final_signal=session.signal,original_native_replay='UNSUPPORTED_NATIVE_SCHEMA',source_admission='ISOLATED_LS0_PROTOTYPE_NOT_SOURCE_ADMITTED')
    ev.save(args.output/'summary.json',summary);ev.phase(args.output,'LS0_RUN_COMPLETE',summary=summary)
    return 0


if __name__=='__main__':sys.exit(main())
