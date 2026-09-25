"""Finite import-free integer Wasm profile, supervised in a disposable process.

The closed binary grammar is independent of Wasmtime's feature defaults.
Wall supervision bounds this worker, not whole-host RSS or engine defects.
"""
from dataclasses import dataclass
import base64
import hashlib
import importlib.metadata
import json
import os
from pathlib import Path
import subprocess
import sys
import tempfile
import time

ENGINE_VERSION = '48.0.0'
PROFILE_VERSION = 'pure-i32-closed-v01'
MAX_BYTES = 16384
MAX_FUEL = 100000
MAX_WALL = 30.0
MAX_OUTPUT = 65536
DISABLED_FEATURES = ('wasm_threads', 'wasm_tail_call', 'wasm_reference_types',
    'wasm_simd', 'wasm_bulk_memory', 'wasm_multi_value', 'wasm_multi_memory',
    'wasm_memory64', 'wasm_relaxed_simd', 'wasm_component_model',
    'wasm_component_model_map', 'wasm_exceptions', 'wasm_function_references',
    'wasm_gc', 'wasm_wide_arithmetic', 'wasm_custom_page_sizes', 'wasm_stack_switching')


@dataclass(frozen=True)
class PureWorkerResultV01:
    status: str
    reason: str | None
    phase: str
    wasm: bytes
    trials: tuple[tuple[int, int, int], ...]
    engine_version: str
    profile_version: str
    configuration_sha256: str
    elapsed_seconds: float
    return_code: int
    process_reaped: bool
    stdout: bytes
    stderr: bytes
    measured_fuel: int


def _require(ok, reason):
    if not ok:
        raise ValueError(reason)


class _Reader:
    def __init__(self, data):
        self.data, self.pos = data, 0

    def byte(self):
        _require(self.pos < len(self.data), 'profile_truncated')
        value = self.data[self.pos]
        self.pos += 1
        return value

    def take(self, n):
        _require(0 <= n <= len(self.data) - self.pos, 'profile_truncated')
        value = self.data[self.pos:self.pos + n]
        self.pos += n
        return value

    def integer(self, signed=False):
        value = 0
        for i in range(5):
            b = self.byte()
            value |= (b & 127) << (7 * i)
            if not b & 128:
                bits = 7 * (i + 1)
                if signed and b & 64:
                    value -= 1 << bits
                _require(-(1 << 31) <= value < (1 << 31) if signed else 0 <= value < (1 << 32), 'profile_integer_range')
                return value
        raise ValueError('profile_integer_encoding')

    def done(self):
        _require(self.pos == len(self.data), 'profile_trailing_data')


def validate_closed_pure_wasm_v01(wasm):
    _require(type(wasm) is bytes and 8 <= len(wasm) <= MAX_BYTES, 'profile_byte_limit')
    r = _Reader(wasm)
    _require(r.take(8) == b'\x00asm\x01\x00\x00\x00', 'profile_raw_wasm_required')
    sections = []
    while r.pos < len(wasm):
        kind = r.byte()
        _require(kind in (1, 3, 7, 10) and (not sections or kind > sections[-1]), 'profile_section_forbidden:' + str(kind))
        sections.append(kind)
        s = _Reader(r.take(r.integer()))
        if kind == 1:
            _require(s.integer() == 1 and s.byte() == 0x60 and s.integer() == 1 and s.byte() == 0x7f
                and s.integer() == 1 and s.byte() == 0x7f, 'profile_function_type')
        elif kind == 3:
            _require(s.integer() == 1 and s.integer() == 0, 'profile_function_count')
        elif kind == 7:
            _require(s.integer() == 1 and s.take(s.integer()) == b'transform'
                and s.byte() == 0 and s.integer() == 0, 'profile_exact_export')
        else:
            _require(s.integer() == 1, 'profile_body_count')
            body = _Reader(s.take(s.integer()))
            groups = body.integer()
            _require(groups <= 32, 'profile_local_groups')
            locals_count = 1
            for _ in range(groups):
                locals_count += body.integer()
                _require(body.byte() == 0x7f and locals_count <= 64, 'profile_local_type_or_count')
            depth = 1
            while depth:
                op = body.byte()
                if op in (0x02, 0x03, 0x04):
                    _require(body.byte() in (0x40, 0x7f), 'profile_block_type')
                    depth += 1
                    _require(depth <= 64, 'profile_nesting')
                elif op == 0x0b:
                    depth -= 1
                elif op in (0x0c, 0x0d):
                    _require(body.integer() < depth, 'profile_branch_depth')
                elif op in (0x20, 0x21, 0x22):
                    _require(body.integer() < locals_count, 'profile_local_index')
                elif op == 0x41:
                    body.integer(signed=True)
                else:
                    _require(op in (0x00, 0x01, 0x05, 0x0f, 0x1a, 0x1b)
                        or 0x45 <= op <= 0x4f or 0x67 <= op <= 0x78,
                        'profile_opcode_forbidden:' + str(op))
            body.done()
        s.done()
    _require(sections == [1, 3, 7, 10], 'profile_required_sections')
    return True


def pure_engine_configuration_v01():
    return dict(engine=ENGINE_VERSION, profile=PROFILE_VERSION,
        disabled_features=list(DISABLED_FEATURES), consume_fuel=True,
        limits=dict(memory_size=0, table_elements=0, instances=1, tables=0, memories=0),
        max_fuel=MAX_FUEL, max_bytes=MAX_BYTES, max_wall_seconds=MAX_WALL,
        no_imports=True, no_start=True, fresh_store_per_call=True)


def _config_digest():
    return hashlib.sha256(json.dumps(pure_engine_configuration_v01(), sort_keys=True, separators=(',', ':')).encode()).hexdigest()


def _emit(value):
    raw = json.dumps(value, sort_keys=True, separators=(',', ':'))
    _require(len(raw) < MAX_OUTPUT, 'worker_output_limit')
    print(raw, flush=True)


def _worker(request):
    _require(type(request) is dict and set(request)=={'source','format','inputs','fuel'}, 'worker_request_shape')
    _require(type(request['source']) is str and len(request['source']) <= 4*((MAX_BYTES+2)//3)
        and request['format'] in ('wat','wasm'), 'worker_request_source')
    _require(type(request['inputs']) is list and 0 < len(request['inputs']) <= 256
        and all(type(v) is int and 0 <= v <= 255 for v in request['inputs']), 'worker_input_domain')
    _require(type(request['fuel']) is int and 0 < request['fuel'] <= MAX_FUEL, 'worker_resource_limit')
    import wasmtime
    _require(importlib.metadata.version('wasmtime') == ENGINE_VERSION, 'engine_pin_mismatch')
    _emit(dict(phase='conversion'))
    raw = base64.b64decode(request['source'], validate=True)
    _require(len(raw) <= MAX_BYTES, 'profile_byte_limit')
    wasm = bytes(wasmtime.wat2wasm(raw.decode('utf-8'))) if request['format'] == 'wat' else raw
    validate_closed_pure_wasm_v01(wasm)
    _emit(dict(phase='compile'))
    config = wasmtime.Config()
    for name in DISABLED_FEATURES:
        setattr(config, name, False)
    config.consume_fuel = True
    engine = wasmtime.Engine(config)
    module = wasmtime.Module(engine, wasm)
    _require(len(module.imports) == 0, 'worker_imports')
    _emit(dict(phase='trials'))
    trials = []
    for value in request['inputs']:
        _require(type(value) is int and 0 <= value <= 255, 'worker_input_domain')
        with wasmtime.Store(engine) as store:
            store.set_limits(**pure_engine_configuration_v01()['limits'])
            store.set_fuel(request['fuel'])
            try:
                instance = wasmtime.Instance(store, module, [])
                output = instance.exports(store)['transform'](store, value)
                _require(type(output) is int and 0 <= output <= 255, 'worker_output_domain')
            except Exception:
                _emit(dict(phase='trial_refused', completed_trials=trials,
                    measured_fuel=sum(t[2] for t in trials)+request['fuel']-store.get_fuel()))
                raise
            trials.append([value, output, request['fuel'] - store.get_fuel()])
    _emit(dict(phase='complete', status='SUCCEEDED', wasm=base64.b64encode(wasm).decode(),
        trials=trials, configuration_sha256=_config_digest(), engine_version=ENGINE_VERSION))


def run_pure_wasm_worker_v01(source, *, source_format, inputs, fuel=MAX_FUEL, wall_seconds=MAX_WALL):
    _require(type(source) is bytes and 0 < len(source) <= MAX_BYTES, 'worker_source_limit')
    _require(source_format in ('wat', 'wasm'), 'worker_source_format')
    _require(type(inputs) is tuple and 0 < len(inputs) <= 256
        and all(type(v) is int and 0 <= v <= 255 for v in inputs), 'worker_input_domain')
    _require(type(fuel) is int and 0 < fuel <= MAX_FUEL and type(wall_seconds) in (int, float)
        and 0 < wall_seconds <= MAX_WALL, 'worker_resource_limit')
    request = json.dumps(dict(source=base64.b64encode(source).decode(), format=source_format,
        inputs=inputs, fuel=fuel)).encode()
    start = time.monotonic()
    timed_out = output_limit = False
    with tempfile.TemporaryDirectory(prefix='radiolaria-pure-worker-') as directory:
        directory = Path(directory)
        (directory/'input').write_bytes(request)
        with (directory/'input').open('rb') as input_file, (directory/'stdout').open('wb') as out, (directory/'stderr').open('wb') as err:
            process = subprocess.Popen([sys.executable, '-B', '-m', __name__], stdin=input_file,
                stdout=out, stderr=err, env=os.environ.copy())
            try:
                while process.poll() is None:
                    timed_out = time.monotonic() - start >= wall_seconds
                    output_limit = (directory/'stdout').stat().st_size + (directory/'stderr').stat().st_size > MAX_OUTPUT
                    if timed_out or output_limit:
                        process.kill()
                        break
                    time.sleep(min(0.01, wall_seconds))
                process.wait()
            finally:
                if process.poll() is None:
                    process.kill()
                    process.wait()
        stdout = (directory/'stdout').read_bytes()[:MAX_OUTPUT]
        stderr = (directory/'stderr').read_bytes()[:MAX_OUTPUT]
    messages = []
    for line in stdout.splitlines():
        try:
            messages.append(json.loads(line))
        except (ValueError, UnicodeError):
            pass
    last = messages[-1] if messages else {}
    phase = last.get('phase', 'startup')
    reason = ('worker_wall_timeout' if timed_out else 'worker_output_limit' if output_limit else
        last.get('reason', 'worker_process_failed') if process.returncode or last.get('status') != 'SUCCEEDED' else None)
    return PureWorkerResultV01('REFUSED' if reason else 'SUCCEEDED', reason, phase,
        base64.b64decode(last['wasm']) if reason is None else b'',
        tuple(tuple(t) for t in last['trials']) if reason is None else (), ENGINE_VERSION, PROFILE_VERSION,
        _config_digest(), time.monotonic() - start, process.returncode, process.poll() is not None, stdout, stderr,
        sum(t[2] for t in last['trials']) if reason is None else
        next((m['measured_fuel'] for m in reversed(messages) if 'measured_fuel' in m),0))


def main():
    try:
        raw = sys.stdin.buffer.read(MAX_OUTPUT + 1)
        _require(len(raw) <= MAX_OUTPUT, 'worker_message_limit')
        _worker(json.loads(raw))
        return 0
    except Exception as exc:
        _emit(dict(status='REFUSED', reason=type(exc).__name__ + ':' + str(exc), phase='rejection'))
        return 1


if __name__ == '__main__':
    raise SystemExit(main())
