"""Wedding explicit public modes; read-only defaults never collect evidence."""
import argparse
import json
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from hedgehog.domains.wedding_seating import portable_v01 as portable


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('mode', choices=('inspect','local','live-qpu','resume-provider','export','verify','replay','render'))
    parser.add_argument('--input', type=Path)
    parser.add_argument('--expected-sha256')
    parser.add_argument('--semantics', type=Path)
    parser.add_argument('--semantics-sha256')
    parser.add_argument('--output', type=Path)
    parser.add_argument('--config', type=Path)
    parser.add_argument('--authorization', type=Path)
    parser.add_argument('--authorization-sha256')
    parser.add_argument('--allow-native', action='store_true')
    parser.add_argument('--allow-external', action='store_true')
    a = parser.parse_args(argv)
    try:
        if a.mode == 'inspect' and a.input is None:
            result = dict(version=portable.VERSION, scope='FINITE_SYNTHETIC_WEDDING', read_only_modes=['inspect','export','verify','replay','render'],
                native_modes=['local','live-qpu','resume-provider'], current_permission=False,
                external_configuration='EXPLICIT_CONFIG_AND_FRESH_INDEPENDENT_AUTHORIZATION_REQUIRED', completed_W4='HISTORICAL_NO_REMAINING_TASK_ALLOWANCE')
        elif a.mode in ('inspect','verify','replay'):
            portable.require(a.input is not None, 'input_required')
            result = portable.verify_v01(a.input, a.expected_sha256)
        elif a.mode == 'export':
            portable.require(a.input is not None and a.semantics is not None and a.output is not None, 'export_paths_required')
            result = portable.export_v01(a.input, a.expected_sha256, a.semantics, a.semantics_sha256, a.output)
        elif a.mode == 'render':
            portable.require(a.input is not None and a.output is not None, 'render_paths_required')
            result = portable.render_v01(a.input, a.expected_sha256, a.output)
        else:
            from hedgehog.domains.wedding_seating import operator_v01
            result = operator_v01.run_v01(a)
        body = portable.canonical(result)
        if a.output is not None and a.mode in ('inspect','verify','replay'):
            portable.require(not a.output.exists() and not any(p.is_symlink() for p in a.output.parents), 'new_output_file_required')
            a.output.parent.mkdir(parents=True, exist_ok=True)
            with a.output.open('xb') as f:
                f.write(body)
        print(body.decode())
        return 0
    except (ValueError, KeyError, TypeError, OSError, ImportError) as error:
        # No credential/provider response dump; setup failures stay explicit.
        reason = str(error) if isinstance(error, ValueError) else type(error).__name__
        print(json.dumps(dict(status='REFUSED', reason=reason, mode=a.mode)), file=sys.stderr)
        return 2


if __name__ == '__main__':
    raise SystemExit(main())
