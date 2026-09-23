"""Explicit bounded G4 CLI; default inspection never collects evidence."""
import argparse
import json


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('operation', nargs='?', default='inspect',
        choices=('inspect', 'preflight', 'native', 'export', 'collect', 'verify', 'replay', 'render'))
    parser.add_argument('--output')
    parser.add_argument('--saved-inputs')
    parser.add_argument('--source-root')
    parser.add_argument('--source-ledger')
    parser.add_argument('--package')
    parser.add_argument('--trust')
    args = parser.parse_args()
    if args.operation == 'inspect':
        print(json.dumps(dict(profile='G4_REFERENCE_SCOPE_V01', implemented=['inspect', 'preflight', 'native','export','verify','replay'],
            unavailable=['collect', 'render'], execution=False,
            source_admission='UNADMITTED_PENDING_INDEPENDENT_REVIEW', effects=0), sort_keys=True))
        return
    if args.operation in ('export','verify','replay'):
        from pathlib import Path
        from hedgehog import gate4_reference_evidence_v01 as e
        if args.operation=='export':
            if not all((args.saved_inputs,args.source_root,args.source_ledger,args.output)):parser.error('export requires explicit saved inputs, source root, source ledger and new output')
            result=e.export_package_v01(saved_inputs=args.saved_inputs,source_root=args.source_root,source_ledger=args.source_ledger,output=args.output)
        else:
            if not args.package or not args.trust:parser.error('verify/replay require explicit package and independent trust file')
            result=e.verify_package_v01(package=args.package,trust=e.read_json_v01(args.trust))
            if args.output:
                target=Path(args.output)
                if target.exists():parser.error('output already exists')
                target.write_bytes(e.a.canonical_v01(result))
        print(json.dumps(result if args.operation=='export' else dict(status=result['status'],native_replay=result['result']['native_replay']),sort_keys=True))
        return
    if args.operation not in ('preflight', 'native'):
        parser.error('NOT_IMPLEMENTED: no implicit collection or recorded PASS fallback')
    if not args.output:
        parser.error(args.operation + ' requires a new external --output directory')
    from hedgehog.domains.airline.gate4_reference_adapter_v01 import preflight_v01, native_story_v42
    result = preflight_v01(args.output) if args.operation == 'preflight' else native_story_v42(args.output)['summary']
    print(json.dumps(result, sort_keys=True))


if __name__ == '__main__':
    main()
