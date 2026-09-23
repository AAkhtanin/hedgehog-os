"""Finite Atlas collection or strictly supplied offline verification/rendering."""
import argparse
import json
from pathlib import Path
import sys

sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from hedgehog import incident_atlas_v01 as atlas


def main():
    parser=argparse.ArgumentParser()
    sub=parser.add_subparsers(dest='command',required=True)
    collect=sub.add_parser('collect');collect.add_argument('--output',type=Path,required=True)
    collect.add_argument('--domain',choices=('SUPPLIER_WATER_FILTER','AIRLINE','TESTFLIX','EPHEMERAL_WORKSPACE','LANDSLIDE_SENTINEL'),default='SUPPLIER_WATER_FILTER')
    collect.add_argument('--config',type=Path)
    export=sub.add_parser('export');export.add_argument('--supplier',type=Path,required=True);export.add_argument('--output',type=Path,required=True)
    export.add_argument('--airline',type=Path);export.add_argument('--execution-sources',type=Path)
    export.add_argument('--testflix',type=Path)
    export.add_argument('--workspace',type=Path)
    export.add_argument('--sentinel',type=Path)
    for name in ('verify','replay','render'):
        p=sub.add_parser(name);p.add_argument('--package',type=Path,required=True)
        p.add_argument('--expected-pin',type=Path,required=True);p.add_argument('--output',type=Path,required=True)
    args=parser.parse_args()
    if args.command=='collect' and args.domain in ('AIRLINE','TESTFLIX','EPHEMERAL_WORKSPACE','LANDSLIDE_SENTINEL'):
        value=atlas.collect_v01(args.output,domain=args.domain,config_path=args.config)
        if args.domain=='LANDSLIDE_SENTINEL':
            value['episode_trace']=[json.loads(line) for line in (args.output/'continuing_episode/phases.jsonl').read_text().splitlines()]
            (args.output/'sentinel.json').write_bytes(atlas.canonical_v01(value))
        print(json.dumps(dict(result=args.domain+'_COLLECTED',output=str(args.output),
            consumption=value['continuation']['consumption'] if args.domain=='LANDSLIDE_SENTINEL' else value['consumption'])))
        return
    if args.command in ('collect','export'):
        if args.output.exists(): raise ValueError('atlas_output_already_exists')
        args.output.mkdir(parents=True)
        supplier=(atlas.collect_v01(args.output/'runtime') if args.command=='collect' else json.loads(args.supplier.read_bytes()))
        airline=json.loads(args.airline.read_bytes()) if args.command=='export' and args.airline else None
        testflix=json.loads(args.testflix.read_bytes()) if args.command=='export' and args.testflix else None
        sources=json.loads(args.execution_sources.read_bytes()) if args.command=='export' and args.execution_sources else None
        workspace=json.loads(args.workspace.read_bytes()) if args.command=='export' and args.workspace else None
        sentinel=json.loads(args.sentinel.read_bytes()) if args.command=='export' and args.sentinel else None
        package=atlas.build_package_v01(supplier,airline=airline,testflix=testflix,workspace=workspace,sentinel=sentinel,execution_sources=sources);pin=atlas.handoff_pin_v01(package)
        for name,value in (('atlas_package.json',package),('expected_pin.json',pin),('coverage.json',package['coverage'])):
            (args.output/name).write_bytes(atlas.canonical_v01(value))
        (args.output/'atlas_story_draft.md').write_text(atlas.render_v01(package))
        print(json.dumps(dict(result='AT5_EXPORT_COMPLETE',pin=pin['package_sha256'],output=str(args.output)),sort_keys=True))
    else:
        package=json.loads(args.package.read_bytes());pin=json.loads(args.expected_pin.read_bytes())
        result=atlas.verify_v01(package,expected_pin=pin)
        if args.output.exists(): raise ValueError('atlas_output_already_exists')
        args.output.write_bytes(atlas.canonical_v01(result) if args.command!='render' else atlas.render_v01(package).encode())
        print(json.dumps(result,sort_keys=True))


if __name__=='__main__': main()
