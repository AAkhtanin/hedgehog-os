"""Optional local ideal p=1 QAOA, SDK serialization and strict offline QASM.

Only these explicit functions import numpy/Braket. No AWS object or transport.
Float64/complex128 are approximation telemetry, never normative coefficients.
Grid loss key = Decimal.from_float(float64 loss)*10**12, ROUND_HALF_EVEN.
Angles are bound by integer multiples of pi in descriptors, not decimal claims.
"""
from decimal import Decimal, ROUND_HALF_EVEN
import hashlib
import json
import math
import re
from .contracts_v01 import CanonicalValueV01, canonical_bytes_v01, integer, keys, require


def _parameters(encoding, scale):
    e = encoding.to_plain_v01()
    integer(scale, 1, 2**30)
    require(scale & (scale-1) == 0, 'power_two_scale')
    require(scale*1024 >= sum(abs(n) for n in e['pauli_numerators'][1:]), 'scale_lower_bound')
    return e


def direct_state_v02(encoding, scale, gamma, beta):
    import numpy as np
    e = _parameters(encoding, scale)
    require(type(gamma) in (int, float) and type(beta) in (int, float)
            and math.isfinite(gamma) and math.isfinite(beta) and abs(gamma) <= 128 and abs(beta) <= 128, 'angle_bound')
    energies = np.array(e['energies'], dtype=np.float64)
    state = np.exp(-1j*gamma*(energies-e['pauli_numerators'][0]/1024)/scale)/32
    c, s = math.cos(beta), -1j*math.sin(beta)
    for q in range(10):
        view = state.reshape(-1, 2, 1 << q)
        left, right = view[:, 0, :].copy(), view[:, 1, :].copy()
        view[:, 0, :], view[:, 1, :] = c*left+s*right, s*left+c*right
    return state


def gate_operations_v02(encoding, scale, gamma, beta):
    e = _parameters(encoding, scale)
    require(type(gamma) in (int, float) and type(beta) in (int, float)
            and math.isfinite(gamma) and math.isfinite(beta) and abs(gamma) <= 128 and abs(beta) <= 128, 'angle_bound')
    operations = [('h', q) for q in range(10)]
    for mask, numerator in enumerate(e['pauli_numerators']):
        if not mask or not numerator:
            continue
        wires = [q for q in range(10) if mask & (1 << q)]
        ladder = list(zip(wires[:-1], wires[1:]))
        operations.extend(('cnot', a, b) for a, b in ladder)
        operations.append(('rz', wires[-1], 2*gamma*numerator/(1024*scale)))
        operations.extend(('cnot', a, b) for a, b in reversed(ladder))
    operations.extend(('rx', q, 2*beta) for q in range(10))
    return tuple(operations)


def gate_state_v02(operations):
    """Apply actual 1/2-qubit gates to little-logical-bit basis amplitudes."""
    import numpy as np
    require(type(operations) in (tuple, list) and len(operations) <= 10000, 'gate_bound')
    state = np.zeros(1024, dtype=np.complex128)
    state[0] = 1
    all_indices = np.arange(1024)
    for op in operations:
        require(type(op) in (tuple, list) and len(op) in (2, 3), 'gate_shape')
        name, q = op[:2]
        integer(q, 0, 9)
        if name == 'cnot':
            require(len(op) == 3, 'gate_shape')
            target = integer(op[2], 0, 9)
            require(q != target, 'gate_wire')
            selected = all_indices[((all_indices >> q) & 1) == 1]
            state[selected] = state[selected ^ (1 << target)]
            continue
        require(name in ('h', 'rx', 'rz'), 'unsupported_gate')
        if name == 'h':
            require(len(op) == 2, 'gate_shape')
            matrix = np.array([[1, 1], [1, -1]], dtype=np.complex128)/math.sqrt(2)
        else:
            require(len(op) == 3 and type(op[2]) in (int, float) and math.isfinite(op[2]) and abs(op[2]) <= 256, 'rotation_bound')
            theta = op[2]/2
            if name == 'rx':
                matrix = np.array([[math.cos(theta), -1j*math.sin(theta)], [-1j*math.sin(theta), math.cos(theta)]])
            else:
                matrix = np.array([[complex(math.cos(theta), -math.sin(theta)), 0], [0, complex(math.cos(theta), math.sin(theta))]])
        zeros = all_indices[(all_indices & (1 << q)) == 0]
        ones = zeros | (1 << q)
        amplitudes = np.stack((state[zeros], state[ones]))
        changed = matrix @ amplitudes
        state[zeros], state[ones] = changed[0], changed[1]
    return state


def loss_key_v02(loss):
    require(type(loss) is float and math.isfinite(loss), 'loss_type')
    return int((Decimal.from_float(loss)*Decimal(10**12)).to_integral_value(rounding=ROUND_HALF_EVEN))


def select_grid_v02(encoding, scale):
    import numpy as np
    e = _parameters(encoding, scale)
    energies = np.array(e['energies'], dtype=np.float64)
    rows = []
    for j in range(1, 33):
        for k in range(1, 25):
            state = direct_state_v02(encoding, scale, math.pi*j/2, math.pi*k/24)
            loss = float(np.dot(np.abs(state)**2, energies))
            rows.append({'gamma_index': j, 'beta_index': k, 'loss': loss, 'loss_key': loss_key_v02(loss)})
    selected = min(rows, key=lambda r: (r['loss_key'], r['gamma_index'], r['beta_index']))
    return {'encoding_ref': encoding.content_id, 'scale': scale, 'grid': 'GAMMA_32_BETA_24_V02',
            'loss_quantization': 'DECIMAL_FROM_FLOAT_RHE_1E12_V01', 'rows': rows, 'selected': selected.copy()}


def circuit_descriptor_v02(encoding, scale, gamma_index, beta_index):
    integer(gamma_index, 1, 32)
    integer(beta_index, 1, 24)
    e = _parameters(encoding, scale)
    nonzero = [mask for mask, n in enumerate(e['pauli_numerators']) if mask and n]
    return CanonicalValueV01(canonical_bytes_v01({
        'schema_version': 'WeddingCircuitDescriptorV02', 'encoding_ref': encoding.content_id,
        'optimization_ref': e['optimization_ref'], 'binding': e['binding'], 'logical_qubits': 10, 'p': 1,
        'scale': scale, 'gamma_pi': [gamma_index, 2], 'beta_pi': [beta_index, 24],
        'state_index': 'SUM_ZJ_2_POW_J', 'serializer_id': 'BRAKET_OPENQASM_SUBSET_V02',
        'abstract_counts': {'h': 10, 'cnot': sum(2*(m.bit_count()-1) for m in nonzero), 'rz': len(nonzero), 'rx': 10, 'measure': 10},
    }))


def build_sdk_program_v02(encoding, scale, gamma_index, beta_index):
    from braket.circuits import Circuit
    from braket.circuits.serialization import IRType
    descriptor = circuit_descriptor_v02(encoding, scale, gamma_index, beta_index)
    circuit = Circuit()
    for op in gate_operations_v02(encoding, scale, math.pi*gamma_index/2, math.pi*beta_index/24):
        if op[0] == 'h':
            circuit.h(op[1])
        elif op[0] == 'cnot':
            circuit.cnot(op[1], op[2])
        elif op[0] == 'rz':
            circuit.rz(op[1], op[2])
        else:
            circuit.rx(op[1], op[2])
    program = circuit.to_ir(ir_type=IRType.OPENQASM)
    data = json.loads(program.json())
    raw = json.dumps(data, sort_keys=True, separators=(',', ':'), ensure_ascii=True, allow_nan=False).encode('utf-8')
    parse_openqasm_program_v02(raw)
    return {'descriptor': descriptor, 'program_json': raw, 'source': data['source'].encode('utf-8'),
            'program_sha256': hashlib.sha256(raw).hexdigest(),
            'source_sha256': hashlib.sha256(data['source'].encode('utf-8')).hexdigest()}


def parse_openqasm_program_v02(raw):
    """Strict emitted subset. No expressions, arbitrary inputs, eval or skipping."""
    require(type(raw) is bytes and len(raw) <= 256*1024, 'program_wire_size')
    def pairs(items):
        result = {}
        for key, value in items:
            require(key not in result, 'program_duplicate_key')
            result[key] = value
        return result
    try:
        value = json.loads(raw, object_pairs_hook=pairs)
    except (UnicodeError, json.JSONDecodeError, RecursionError) as error:
        raise ValueError('program_json') from error
    keys(value, 'braketSchemaHeader inputs source')
    require(value['braketSchemaHeader'] == {'name': 'braket.ir.openqasm.program', 'version': '1'} and value['inputs'] == {}, 'program_schema_inputs')
    require(type(value['source']) is str and len(value['source']) <= 128*1024 and value['source'].isascii(), 'program_source')
    lines = value['source'].splitlines()
    require(lines[:3] == ['OPENQASM 3.0;', 'bit[10] b;', 'qubit[10] q;'], 'qasm_header')
    require(13 <= len(lines) <= 10000, 'qasm_statement_bound')
    operations, measurements = [], []
    number = r'([+-]?(?:\d+(?:\.\d*)?|\.\d+)(?:[eE][+-]?\d+)?)'
    for line in lines[3:]:
        measurement = re.fullmatch(r'b\[(\d)\] = measure q\[(\d)\];', line)
        if measurement:
            measurements.append(tuple(int(v) for v in measurement.groups()))
            continue
        require(not measurements, 'gate_after_measurement')
        h = re.fullmatch(r'h q\[(\d)\];', line)
        cnot = re.fullmatch(r'cnot q\[(\d)\], q\[(\d)\];', line)
        rotation = re.fullmatch(r'(rx|rz)\(' + number + r'\) q\[(\d)\];', line)
        if h:
            operations.append(('h', int(h[1])))
        elif cnot:
            a, b = int(cnot[1]), int(cnot[2])
            require(a != b, 'gate_wire')
            operations.append(('cnot', a, b))
        elif rotation:
            angle = float(rotation[2])
            require(math.isfinite(angle) and abs(angle) <= 256, 'rotation_bound')
            operations.append((rotation[1], int(rotation[3]), angle))
        else:
            raise ValueError('unsupported_qasm_statement')
    require(measurements == [(q, q) for q in range(10)], 'measurement_wiring')
    return tuple(operations), tuple(measurements)


def execute_openqasm_program_v02(raw):
    """Return the PRE-measurement state; wire map is separately verified."""
    operations, measurements = parse_openqasm_program_v02(raw)
    return gate_state_v02(operations), measurements
