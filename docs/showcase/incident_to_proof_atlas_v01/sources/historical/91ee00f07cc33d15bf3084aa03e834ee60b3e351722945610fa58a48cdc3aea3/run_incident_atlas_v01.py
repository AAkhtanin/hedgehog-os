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
    collect.add_argument('--domain',choices=('SUPPLIER_WATER_FILTER','AIRLINE'),default='SUPPLIER_WATER_FILTER')
    export=sub.add_parser('export');export.add_argument('--supplier',type=Path,required=True);export.add_argument('--output',type=Path,required=True)
    export.add_argument('--airline',type=Path);export.add_argument('--execution-sources',type=Path)
    for name in ('verify','replay','render'):
        p=sub.add_parser(name);p.add_argument('--package',type=Path,required=True)
        p.add_argument('--expected-pin',type=Path,required=True);p.add_argument('--output',type=Path,required=True)
    args=parser.parse_args()
    if args.command=='collect' and args.domain=='AIRLINE':
        value=atlas.collect_v01(args.output,domain='AIRLINE')
        print(json.dumps(dict(result='AT2_AIRLINE_COLLECTED',output=str(args.output),consumption=value['consumption'])))
        return
    if args.command in ('collect','export'):
        if args.output.exists(): raise ValueError('atlas_output_already_exists')
        args.output.mkdir(parents=True)
        supplier=(atlas.collect_v01(args.output/'runtime') if args.command=='collect' else json.loads(args.supplier.read_bytes()))
        airline=json.loads(args.airline.read_bytes()) if args.command=='export' and args.airline else None
        sources=json.loads(args.execution_sources.read_bytes()) if args.command=='export' and args.execution_sources else None
        package=atlas.build_package_v01(supplier,airline=airline,execution_sources=sources);pin=atlas.handoff_pin_v01(package)
        for name,value in (('atlas_package.json',package),('expected_pin.json',pin),('coverage.json',package['coverage'])):
            (args.output/name).write_bytes(atlas.canonical_v01(value))
        (args.output/'supplier_case_draft.md').write_text(atlas.render_v01(package))
        print(json.dumps(dict(result='AT2_EXPORT_COMPLETE',pin=pin['package_sha256'],output=str(args.output)),sort_keys=True))
    else:
        package=json.loads(args.package.read_bytes());pin=json.loads(args.expected_pin.read_bytes())
        result=atlas.verify_v01(package,expected_pin=pin)
        if args.output.exists(): raise ValueError('atlas_output_already_exists')
        args.output.write_bytes(atlas.canonical_v01(result) if args.command!='render' else atlas.render_v01(package).encode())
        print(json.dumps(result,sort_keys=True))


if __name__=='__main__': main()
