"""Exact PAIR_BINARY_10Q_V02 substitution, integer spectrum and pure row codec.

Index=sum(z[j]*2**j). Code a+2*b selects table 0/1/2; 3 is unseated,
never repaired. This is a multilinear (up to four-local) energy, not a 10-QUBO.
"""
from dataclasses import dataclass
from .contracts_v01 import (
    CanonicalValueV01, array, binding_v01, canonical_bytes_v01, integer, keys,
    parse_json_v01, parse_optimization_spec_v01, require,
)
from .math_v01 import ProblemMathV01, compile_optimization_v01, validate_assignment_v01


@dataclass(frozen=True, slots=True)
class PairEncodingV02(CanonicalValueV01):
    pass


def _geometry(problem):
    model = ProblemMathV01(problem)
    pairs = sorted(c[2] for c in model.conditions if c[1] == 'TOGETHER')
    allowed = [c for c in model.conditions if c[1] == 'ALLOWED_TABLES']
    require(len(pairs) == 6 and sorted(g for pair in pairs for g in pair) == list(range(12)), 'UNSUPPORTED_ENCODING:disjoint_pairs')
    require(len(allowed) == 1 and allowed[0][3] == (2,), 'UNSUPPORTED_ENCODING:fixed_table3')
    fixed = next(pair for pair in pairs if allowed[0][2][0] in pair)
    variable = [pair for pair in pairs if pair != fixed]
    return tuple(variable), fixed


def _substitutions(variable, fixed):
    result = [{} for _ in range(36)]
    for k, pair in enumerate(variable):
        a, b = 1 << (2*k), 1 << (2*k+1)
        for g in pair:
            result[3*g] = {0: 1, a: -1, b: -1, a|b: 1}
            result[3*g+1] = {a: 1, a|b: -1}
            result[3*g+2] = {b: 1, a|b: -1}
    for g in fixed:
        result[3*g+2] = {0: 1}
    return result


def walsh_transform_v02(values):
    require(type(values) in (tuple, list) and len(values) == 1024, 'spectrum_size')
    data = [integer(v, -(2**31-1), 2**31-1) for v in values]
    stride = 1
    while stride < len(data):
        for start in range(0, len(data), 2*stride):
            for j in range(start, start+stride):
                left, right = data[j], data[j+stride]
                data[j], data[j+stride] = left+right, left-right
        stride *= 2
    return tuple(data)


def compile_encoding_v02(problem, profile):
    spec = compile_optimization_v01(problem, profile)
    q = spec.to_plain_v01()
    variable, fixed = _geometry(problem)
    substitutions = _substitutions(variable, fixed)
    polynomial = {0: q['offset']}
    for i, j, coefficient in q['qubo_terms']:
        for left, lv in substitutions[i].items():
            for right, rv in substitutions[j].items():
                mask = left | right  # z_j squared equals z_j on binary inputs.
                polynomial[mask] = polynomial.get(mask, 0) + coefficient*lv*rv
    monomials = [[mask, coefficient] for mask, coefficient in sorted(polynomial.items()) if coefficient]
    energies = [sum(coefficient for mask, coefficient in monomials if state & mask == mask) for state in range(1024)]
    numerators = walsh_transform_v02(energies)
    value = {'schema_version': 'PAIR_BINARY_10Q_V02', 'binding': binding_v01(problem, profile),
             'optimization_ref': spec.content_id, 'qubits': 10, 'state_index': 'SUM_ZJ_2_POW_J',
             'variable_pairs': [list(p) for p in variable], 'fixed_pair': list(fixed), 'fixed_table': 2,
             'invalid_code': 3, 'substitution': [[[mask, coefficient] for mask, coefficient in sorted(poly.items())] for poly in substitutions],
             'monomials': monomials, 'energies': energies,
             'pauli_denominator': 1024, 'pauli_numerators': list(numerators)}
    return PairEncodingV02(canonical_bytes_v01(value))


def parse_encoding_v02(raw, *, problem, profile):
    value = parse_json_v01(raw)
    expected = compile_encoding_v02(problem, profile)
    require(canonical_bytes_v01(value) == expected.canonical, 'encoding_source_derivation')
    return expected


def common_scale_v02(encodings):
    require(type(encodings) in (tuple, list) and len(encodings) == 2, 'scale_profiles')
    data = [e.to_plain_v01() for e in encodings]
    require({e['binding']['objective_profile'] for e in data} == {'KEEP_FAMILIAR_V01', 'MIX_CIRCLES_V01'}, 'scale_profiles')
    require(data[0]['binding']['problem_ref'] == data[1]['binding']['problem_ref'], 'scale_problem')
    maximum = max(sum(abs(n) for n in e['pauli_numerators'][1:]) for e in data)
    scale = 1
    while scale*1024 < maximum:
        scale *= 2
    return scale


def decode_basis_v02(encoding, state):
    integer(state, 0, 1023)
    e = encoding.to_plain_v01()
    assignment = [-1]*12
    for k, pair in enumerate(e['variable_pairs']):
        code = (state >> (2*k)) & 3
        for g in pair:
            assignment[g] = code if code < 3 else -1
    for g in e['fixed_pair']:
        assignment[g] = 2
    bits = tuple(int(assignment[g] == t) for g in range(12) for t in range(3))
    return tuple(assignment), bits


def measurement_index_v02(row, measured_qubits):
    array(measured_qubits, 10, 10)
    for q in measured_qubits:
        integer(q, 0, 9)
    require(sorted(measured_qubits) == list(range(10)), 'measurement_qubit_mapping')
    array(row, 10, 10)
    for bit in row:
        integer(bit, 0, 1)
    return sum(bit << q for bit, q in zip(row, measured_qubits))


def decode_samples_v02(raw, *, encoding, problem, profile, expected_shots):
    """Supported wire: raw rows only. Count strings deliberately not inferred."""
    integer(expected_shots, 1, 1000)
    checked = parse_encoding_v02(encoding.canonical, problem=problem, profile=profile)
    data = parse_json_v01(raw, limit=8*1024*1024)
    keys(data, 'schema_version origin shots measuredQubits measurements')
    require(data['schema_version'] == 'WeddingRawMeasurementsV01', 'sample_wire_format')
    require(data['origin'] == 'CONTROLLED_FIXTURE', 'sample_origin_not_qpu')
    integer(data['shots'], 1, 1000)
    require(data['shots'] == expected_shots, 'shot_binding')
    array(data['measurements'], expected_shots, expected_shots)
    occurrences = {}
    for row in data['measurements']:
        state = measurement_index_v02(row, data['measuredQubits'])
        occurrences[state] = occurrences.get(state, 0) + 1
    outcomes = []
    for state, count in sorted(occurrences.items()):
        assignment, _ = decode_basis_v02(checked, state)
        if -1 in assignment:
            status, report = 'INVALID_CODE_3', None
        else:
            report = validate_assignment_v01(problem, assignment, profile).to_plain_v01()
            status = report['status']
        outcomes.append({'state': state, 'occurrences': count, 'assignment': list(assignment), 'status': status, 'report': report})
    return {'origin': 'CONTROLLED_FIXTURE', 'shots': expected_shots,
            'status': 'VALID_SAMPLES_OBSERVED' if any(o['status'] == 'VALID' for o in outcomes) else 'NO_VALID_PROVIDER_SAMPLE',
            'outcomes': outcomes}
