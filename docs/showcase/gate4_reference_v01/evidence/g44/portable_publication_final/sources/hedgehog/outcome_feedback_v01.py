"""Pure, bounded outcome feedback. Reference facts are not runtime authority."""
from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timezone
import json
import re
import unicodedata

from hedgehog.kernel.abi_v01 import KernelArtifactV01, build_kernel_artifact_v01
from hedgehog.kernel.integrity_replay_v01 import (
    canonical_json_bytes_v01, domain_separated_sha256_hex_v01,
)

PROFILE_ID = 'G3_OUTCOME_FEEDBACK_V01'
NUMERIC_PROFILE_ID = 'G3_FIXED_POINT_REFERENCE_V01'
SOURCE_PROFILE_ID = 'G31_SYNTHETIC_REFERENCE_V01'
NATIVE_SOURCE_PROFILE_ID = 'G32_NATIVE_REVIEWED_WORK_V01'
ACTION_ADVICE_SOURCE_PROFILE_ID = 'G36_SUPPLIER_ACTION_ADVICE_V01'
CLAIM_PROFILE_ID = 'G31_SCOPE_ADVICE_BINARY_V01'
REFERENCE_CLASS = 'REFERENCE_FIXTURE_NOT_EXECUTED'
Q = 1_000_000_000
MAX_BYTES = 65536
_REFERENCE_SOURCES = frozenset((
    'a867749a3a6a862b348ef1273b5c0b1d681124a81173fa78b65a5e23f5b4e98c',
    'b192beb12a0d6b62a943cc6b69e55d5396a7129e9606be81d4b3d1248491e012',
    'd233884c52ccaa4ec4e80c1b5625213f2d40ce35b0c494db861c8d0ec598ae1e',
    '4b3a5786e73aa809838210c75766385261a2c66a8b113125bf90232bfd781fce',
    'db392cff67d19073deee33a0f94401d9eea3ab3cfec084ce3050d6c3b2dcfbe5',
    '4dd339a1c18f86f784e0784c77aeb86561f5e515f5089c56b62e4dc4bf37957d',
    'd77f64580b8d61cf02bdda64eadb5e14d7750a39949fdc9fa7f084a93a8db542',
    'be995e7678a894aa4e56d6c06081548883f2423d086aa9cf59be8697c25d79f0',
    '988104191a22d5bc39aef22754f80b9216358cf87e77af83a15c2dc87b938370',
    '7af97c50334c6e2b53c03b274f21a9fa9b80182c0009e94b38a240d51c8573c2',
    '76c4b7b63f8cc194998ebc8650d8bd6f25e13f364a14495e7f08bf158cde21d6',
))
_STATES = ('KNOWN', 'UNKNOWN', 'NOT_APPLICABLE', 'NOT_REACHED')
_LANES = ('CONTROLLED_RUNTIME', 'LIVE_CAPTURED_ORIGIN', 'CAPTURED_REEXECUTION', 'HISTORICAL_IMPORT')
_QUALITY = ('CORRECT', 'INCORRECT', 'UNSAFE', 'NOT_SCORABLE')
_ENFORCEMENT = ('BLOCKED_AS_REQUIRED', 'ALLOWED_AS_REQUIRED', 'UNEXPECTED_EFFECT', 'NOT_EXERCISED', 'UNKNOWN')
_TASK = ('COMPLETED', 'PARTIAL', 'SAFE_NO_DEAL', 'CANCELLED', 'NEEDS_INPUT', 'FAILED', 'UNKNOWN')
_EXECUTION = ('COMPLETED', 'BLOCKED_BEFORE_EFFECT', 'NEEDS_MORE_EVIDENCE', 'NEEDS_USER', 'NO_DEAL', 'CANCELLED', 'PARTIAL', 'EXECUTOR_FAILED', 'TRANSPORT_FAILED', 'EXPIRED_OR_REVOKED', 'UNKNOWN')
_STAGES = ('NONE', 'SEMANTIC_VALIDATION', 'POST_VV', 'ROOT', 'CURRENTNESS', 'FIREWALL', 'EXECUTOR', 'TRANSPORT', 'OBSERVATION')
_FAILURES = ('NONE', 'PROPOSAL_INVALID', 'PROPOSAL_UNSAFE', 'EXECUTOR_FAILURE', 'TRANSPORT_FAILURE', 'SOURCE_UNAVAILABLE', 'OBSERVATION_INCOMPLETE', 'CONFLICTING')
_SUBJECT_FIELDS = ('local_root_scope_id', 'domain_scope_id', 'pack_family_id', 'advisory_source_class', 'advisory_source_revision', 'advice_claim_profile_id', 'route_family_id', 'task_risk_class', 'validation_profile_id', 'policy_semantics_version', 'history_key_profile_id')
_HISTORY_FIELDS = ('local_root_scope_id', 'domain_scope_id', 'pack_family_id', 'route_family_id', 'task_class_id', 'task_risk_class', 'policy_semantics_version', 'capability_contract_version', 'evidence_validation_profile_id', 'advisory_source_revision', 'history_key_profile_id')
_TEXT_FIELDS = ('feedback_id', 'profile_id', 'schema_version', 'numeric_profile_id', 'source_profile_id', 'evidence_class', 'transaction_id', 'run_id', 'episode_id', 'observation_id', 'scenario_id', 'domain', 'pack_family_id', 'local_root_scope_id', 'strategy_candidate_id', 'context_fingerprint', 'execution_lane', 'advice_claim_profile_id', 'execution_status', 'blocking_stage', 'validation_status', 'failure_class', 'proposal_assessment', 'enforcement_outcome', 'task_outcome', 'update_eligibility', 'source_closure_ref')
_TIME_FIELDS = ('timestamp', 'event_time', 'ingested_time', 'evaluated_at', 'causal_event_sequence')
_REF_ARRAYS = ('decision_basis_refs', 'other_root_evidence_refs', 'receipt_refs', 'source_refs', 'provenance_refs', 'validation_refs', 'update_reasons')
_TAG_FIELDS = {'parent_correlation_ref': 'REFERENCE', 'proposal_ref': 'REFERENCE', 'avf_prediction': 'FP_Q', 'avf_rank': 'RANK', 'gt_advice_ref': 'REFERENCE', 'pre_decision_expectation': 'FP_Q', 'prior_state_ref': 'REFERENCE', 'root_decision_ref': 'REFERENCE', 'action_packet_ref': 'REFERENCE', 'firewall_decision_ref': 'REFERENCE', 'manual_override': 'REFERENCE', 'observed_result': 'FP_Q', 'observed_regret': 'FP_Q', 'predecessor_feedback_ref': 'REFERENCE', 'supersedes_ref': 'REFERENCE', 'correction_reason': 'TEXT'}
_GROUP_FIELDS = ('advisory_subject_key', 'avf_history_key', 'policy_violations', 'observation_scope', 'attribution', 'actual_cost', 'actual_latency', 'time_envelope', 'non_authority_flags')
_FEEDBACK_FIELDS = frozenset((*_TEXT_FIELDS, *_TIME_FIELDS, *_REF_ARRAYS, *_TAG_FIELDS, *_GROUP_FIELDS))
_HEX = re.compile(r'^[0-9a-f]{64}$')


def _require(condition: bool, reason: str = 'g31_structure_invalid') -> None:
    if not condition:
        raise ValueError(reason)


def _keys(value: object, names) -> None:
    _require(type(value) is dict and set(value) == set(names))


def _text(value: object) -> None:
    _require(type(value) is str and 0 < len(value) <= 256)


def _integer(value: object, maximum: int = 2**53-1) -> None:
    _require(type(value) is int and 0 <= value <= maximum)


def _strings(value: object) -> None:
    _require(type(value) is list and len(value) <= 32)
    for item in value:
        _text(item)
    _require(len(value) == len(set(value)))


def _tree(value: object, depth: int = 0, count: list[int] | None = None) -> None:
    if count is None:
        count = [0]
    count[0] += 1
    _require(depth <= 12 and count[0] <= 4096, 'g31_size_limit')
    kind = type(value)
    if kind is dict:
        _require(len(value) <= 96, 'g31_size_limit')
        for key, item in value.items():
            _require(type(key) is str and 0 < len(key) <= 64)
            _tree(key, depth + 1, count)
            _tree(item, depth + 1, count)
    elif kind is list:
        _require(len(value) <= 64, 'g31_size_limit')
        for item in value:
            _tree(item, depth + 1, count)
    elif kind is str:
        _require(len(value) <= 256 and unicodedata.normalize('NFC', value) == value)
        _require(not any(0xD800 <= ord(c) <= 0xDFFF or ord(c) < 32 for c in value))
    elif kind is int:
        _require(abs(value) <= 2**53-1)
    else:
        _require(value is None or kind is bool)


def _canonical(value: object) -> bytes:
    _tree(value)
    result = canonical_json_bytes_v01(value)
    _require(len(result) <= MAX_BYTES, 'g31_size_limit')
    return result


def _identity(domain: str, material: object) -> str:
    return domain_separated_sha256_hex_v01(domain=domain, payload=_canonical(material))


def _pairs(rows):
    result = {}
    for key, value in rows:
        _require(key not in result, 'g31_duplicate_json_key')
        result[key] = value
    return result


def _reject_number(value):
    raise ValueError('g31_non_integer_number')


def _decode(raw: str | bytes) -> dict:
    _require(type(raw) in (str, bytes), 'g31_json_type')
    encoded = raw.encode('utf-8', errors='strict') if type(raw) is str else raw
    _require(len(encoded) <= MAX_BYTES, 'g31_size_limit')
    try:
        result = json.loads(encoded.decode('utf-8'), object_pairs_hook=_pairs,
                            parse_float=_reject_number, parse_constant=_reject_number)
    except (UnicodeError, json.JSONDecodeError, RecursionError) as exc:
        raise ValueError('g31_json_invalid') from exc
    _tree(result)
    _require(type(result) is dict)
    return result


def _tag(value: object, unit: str) -> None:
    _keys(value, ('state', 'value', 'reason_code', 'evidence_refs', 'unit'))
    _require(value['state'] in _STATES and value['unit'] == unit)
    _strings(value['evidence_refs'])
    if value['state'] == 'KNOWN':
        _require(value['reason_code'] == '' and bool(value['evidence_refs']))
        if unit in ('FP_Q', 'RANK', 'COUNT', 'MINOR_UNITS', 'MICROSECONDS'):
            _integer(value['value'], Q if unit == 'FP_Q' else 2**53-1)
            if unit == 'RANK':
                _require(value['value'] >= 1)
        else:
            _text(value['value'])
            if unit == 'CURRENCY':
                _require(re.fullmatch(r'[A-Z]{3}', value['value']) is not None)
    else:
        _require(value['value'] is None)
        _text(value['reason_code'])


@dataclass(frozen=True, slots=True)
class TaggedValueV01:
    state: str
    value: int | str | None
    reason_code: str
    evidence_refs: tuple[str, ...]
    unit: str

    def __post_init__(self):
        self.to_plain_data()

    def to_plain_data(self) -> dict:
        _require(type(self.evidence_refs) is tuple)
        _require(self.unit in ('REFERENCE', 'FP_Q', 'RANK', 'TEXT', 'COUNT', 'MINOR_UNITS', 'CURRENCY', 'MICROSECONDS'))
        result = dict(state=self.state, value=self.value, reason_code=self.reason_code,
                      evidence_refs=list(self.evidence_refs), unit=self.unit)
        _tree(result)
        _tag(result, self.unit)
        return result


def _time_shape(value: dict, *, native: bool = False) -> None:
    _keys(value, ('ct_session_anchor', 'et_observed_at', 'freshness_class', 'kt_asof',
                  'pt_created_at', 'ttl_seconds', 'valid_from', 'valid_to'))
    _require(value['freshness_class'] == 'static')
    _integer(value['ttl_seconds'], 604800)
    for name in value.keys() - {'freshness_class', 'ttl_seconds'}:
        if native and name == 'ct_session_anchor':
            _text(value[name])
            continue
        if native and name == 'et_observed_at' and value[name] is None:
            continue
        _text(value[name])
        try:
            instant = datetime.fromisoformat(value[name])
            _require(instant.tzinfo == timezone.utc and (native or instant.isoformat(timespec='seconds') == value[name]))
        except (ValueError, TypeError) as exc:
            raise ValueError('g31_time_invalid') from exc


def _feedback_shape(value: dict) -> None:
    _tree(value)
    _keys(value, _FEEDBACK_FIELDS)
    for name in _TEXT_FIELDS:
        _text(value[name])
    _require(value['profile_id'] == PROFILE_ID and value['schema_version'] == 'v0.1')
    _require(value['numeric_profile_id'] == NUMERIC_PROFILE_ID)
    _require(value['execution_lane'] in _LANES and value['proposal_assessment'] in _QUALITY
             and value['enforcement_outcome'] in _ENFORCEMENT and value['task_outcome'] in _TASK
             and value['execution_status'] in _EXECUTION and value['blocking_stage'] in _STAGES
             and value['failure_class'] in _FAILURES and value['validation_status'] == 'CONTEXT_VALIDATED'
             and value['update_eligibility'] in ('ELIGIBLE', 'NO_UPDATE'))
    for name in ('feedback_id', 'observation_id', 'context_fingerprint'):
        _require(_HEX.fullmatch(value[name]) is not None)
    for name in _TIME_FIELDS:
        _integer(value[name], 253402300799 if name != 'causal_event_sequence' else 2**53-1)
    _require(value['event_time'] <= value['ingested_time'] <= value['evaluated_at'] <= value['timestamp'], 'g31_time_invalid')
    for name in _REF_ARRAYS:
        _strings(value[name])
    for name, unit in _TAG_FIELDS.items():
        _tag(value[name], unit)
    for name, fields in (('advisory_subject_key', _SUBJECT_FIELDS), ('avf_history_key', _HISTORY_FIELDS)):
        _keys(value[name], fields)
        for item in value[name].values():
            _text(item)
    _keys(value['policy_violations'], ('attempted_violation_refs', 'realized_violation_refs'))
    for refs in value['policy_violations'].values():
        _strings(refs)
    scope = value['observation_scope']
    _keys(scope, ('mechanism', 'occurrence_ref', 'operation_ref', 'measurement_refs', 'limitations'))
    for name in ('mechanism', 'occurrence_ref', 'operation_ref', 'limitations'):
        _text(scope[name])
    _strings(scope['measurement_refs'])
    attr = value['attribution']
    _keys(attr, ('subject_ref', 'claim_profile_id', 'reason_code', 'source_refs', 'scoring_eligibility'))
    for name in ('subject_ref', 'claim_profile_id', 'reason_code'):
        _text(attr[name])
    _strings(attr['source_refs'])
    _require(attr['scoring_eligibility'] in ('ELIGIBLE', 'NO_UPDATE'))
    cost = value['actual_cost']
    _keys(cost, ('model_calls', 'input_tokens', 'output_tokens', 'work_invocations', 'money', 'currency', 'scope_ref'))
    for name in ('model_calls', 'input_tokens', 'output_tokens', 'work_invocations'):
        _tag(cost[name], 'COUNT')
    _tag(cost['money'], 'MINOR_UNITS')
    _tag(cost['currency'], 'CURRENCY')
    _require((cost['money']['state'] == 'KNOWN') == (cost['currency']['state'] == 'KNOWN'))
    _text(cost['scope_ref'])
    latency = value['actual_latency']
    _keys(latency, ('elapsed_us', 'phase_scope', 'receipt_ref'))
    _tag(latency['elapsed_us'], 'MICROSECONDS')
    _text(latency['phase_scope'])
    _tag(latency['receipt_ref'], 'REFERENCE')
    _require(value['source_profile_id'] in (SOURCE_PROFILE_ID, NATIVE_SOURCE_PROFILE_ID, PREDICTIVE_SOURCE_PROFILE_ID, ACTION_ADVICE_SOURCE_PROFILE_ID, *G35_PROFILES), 'g31_source_profile_unknown')
    _time_shape(value['time_envelope'], native=value['source_profile_id'] != SOURCE_PROFILE_ID)
    _keys(value['non_authority_flags'], ('claims_permission', 'claims_root_decision', 'requests_effect'))
    _require(all(flag is False for flag in value['non_authority_flags'].values()))
    _require(value['feedback_id'] == _identity('g3_feedback_v01', {k:v for k,v in value.items() if k != 'feedback_id'}), 'g31_identity_mismatch')


def _observation_shape(value: dict) -> None:
    _keys(value, ('observation_id', 'schema_version', 'source_profile_id', 'source_bundle_ref',
                  'event_time', 'ingested_time', 'evaluated_at', 'timestamp', 'source_refs'))
    _require(value['schema_version'] == 'v0.1' and value['source_profile_id'] in (SOURCE_PROFILE_ID,NATIVE_SOURCE_PROFILE_ID,PREDICTIVE_SOURCE_PROFILE_ID,ACTION_ADVICE_SOURCE_PROFILE_ID,*G35_PROFILES))
    for name in ('observation_id', 'source_bundle_ref'):
        _require(type(value[name]) is str and _HEX.fullmatch(value[name]) is not None)
    for name in ('event_time', 'ingested_time', 'evaluated_at', 'timestamp'):
        _integer(value[name], 253402300799)
    _require(value['event_time'] <= value['ingested_time'] <= value['evaluated_at'] <= value['timestamp'], 'g31_time_invalid')
    _strings(value['source_refs'])
    _require(value['observation_id'] == _identity('g3_observation_v01', {k:v for k,v in value.items() if k != 'observation_id'}), 'g31_identity_mismatch')


@dataclass(frozen=True, slots=True)
class OutcomeObservationV01:
    canonical: bytes

    def __post_init__(self):
        _require(type(self.canonical) is bytes)
        value = _decode(self.canonical)
        _observation_shape(value)
        _require(_canonical(value) == self.canonical, 'g31_noncanonical_bytes')


@dataclass(frozen=True, slots=True)
class OutcomeFeedbackEnvelopeV01:
    canonical: bytes

    def __post_init__(self):
        _require(type(self.canonical) is bytes)
        value = _decode(self.canonical)
        _feedback_shape(value)
        _require(_canonical(value) == self.canonical, 'g31_noncanonical_bytes')


def parse_outcome_feedback_json_v01(raw: str | bytes) -> OutcomeFeedbackEnvelopeV01:
    return OutcomeFeedbackEnvelopeV01(_canonical(_decode(raw)))


def _error(exc: Exception) -> tuple[str, ...]:
    reason = str(exc)
    return (reason if reason.startswith(('g31_','g32_','g34_','g35_','g36_')) else 'g31_invalid_input',)


def validate_outcome_feedback_structure_v01(value: object) -> tuple[str, ...]:
    try:
        plain = _decode(value.canonical) if type(value) is OutcomeFeedbackEnvelopeV01 else value
        _feedback_shape(plain)
        _canonical(plain)
        return ()
    except (ValueError, TypeError, KeyError, AttributeError, RecursionError) as exc:
        return _error(exc)


@dataclass(frozen=True, slots=True)
class NativeOutcomeSourceContextV01:
    """Independent normalized baseline, NOT a native-authentication token.

    Native producers/consumers must validate live evidence separately. Never
    obtain this trusted argument from the supplied report being assessed.
    """
    canonical: bytes

    def __post_init__(self):
        _require(type(self.canonical) is bytes)
        value = _decode(self.canonical)
        _require(value['source_profile_id'] == NATIVE_SOURCE_PROFILE_ID)
        _require(_canonical(value) == self.canonical)


def _source(bundle: dict | NativeOutcomeSourceContextV01, profile: str) -> tuple[dict, str]:
    if profile == ACTION_ADVICE_SOURCE_PROFILE_ID:
        from hedgehog.domains.supplier_water_filter.adversarial_feedback_v01 import normalized_source_v01
        return normalized_source_v01(bundle)
    if profile in G35_PROFILES:
        return _g35_source_v01(bundle, profile)
    if profile == PREDICTIVE_SOURCE_PROFILE_ID:
        return _predictive_source_v01(bundle)
    _require(type(profile) is str and profile in (SOURCE_PROFILE_ID,NATIVE_SOURCE_PROFILE_ID), 'g31_source_profile_unknown')
    native = profile == NATIVE_SOURCE_PROFILE_ID
    if native:
        _require(type(bundle) is NativeOutcomeSourceContextV01, 'g32_independent_native_context_required')
        raw = bundle.canonical
    else:
        raw = _canonical(bundle)
    identity = domain_separated_sha256_hex_v01(domain='g3_source_bundle_v01', payload=raw)
    if not native:
        _require(identity in _REFERENCE_SOURCES, 'g31_source_not_admitted')
    source = _decode(raw)
    context, proposal, observation = source['context'], source['proposal'], source['observation']
    _require(source['source_profile_id'] == profile and source['evidence_class'] == ('NATIVE_CONTROLLED_OBSERVATION' if native else REFERENCE_CLASS))
    _require(proposal['origin_ref'] == source['origin']['source_id']
             and observation['proposal_ref'] == proposal['source_id']
             and observation['occurrence_ref'] == source['origin']['occurrence_id'], 'g31_source_relation')
    _require(all(proposal[key] == observation[key] for key in ('operation', 'object_id', 'recipient')), 'g31_operation_binding')
    _require(observation['result_revision'] == context['capability_contract_version']
             and source['policy']['revision'] == context['policy_semantics_version'], 'g31_source_revision')
    if native:
        _keys(source, ('source_profile_id','evidence_class','context','policy','origin','proposal','expectation','observation','closure','native'))
        _keys(context, ('source_id','local_root_scope_id','domain','pack_family_id','advisory_source_class','advisory_source_revision',
            'advice_claim_profile_id','route_family_id','task_risk_class','validation_profile_id','policy_semantics_version',
            'history_key_profile_id','task_class_id','capability_contract_version','transaction_id','run_id','episode_id','scenario_id'))
        for item in context.values():
            _text(item)
        for name,fields in (
            ('policy',('source_id','revision','operation','object_id','recipient')),
            ('origin',('source_id','occurrence_id')),
            ('proposal',('source_id','origin_ref','created_at','recommendation','operation','object_id','recipient')),
            ('expectation',('source_id','created_at','expected_fp')),
            ('observation',('source_id','proposal_ref','occurrence_ref','operation','object_id','recipient','result_revision','event_time','boundary_disposition','effect_count','result_state','failure')),
            ('closure',('source_id','sources'))):
            _keys(source[name],fields)
        _integer(observation['effect_count'])
        _require(source['expectation']['expected_fp'] is None or type(source['expectation']['expected_fp']) is int and 0<=source['expectation']['expected_fp']<=Q)
        fact=source['native']
        _keys(fact, ('claim_wall_ns','event_wall_ns','capture_wall_ns','elapsed_ns','sequence','root_decision_ref',
                    'plan_artifact_ref','result_artifact_ref','material_sha256','output_sha256','work_count',
                    'reached_boundary','reason','time_envelope','capture_ref','semantic_ref','dependencies_sha256'))
        for name in ('claim_wall_ns','event_wall_ns','capture_wall_ns'):
            _require(type(fact[name]) is str and re.fullmatch(r'[0-9]{1,20}',fact[name]) is not None)
        _require(int(fact['claim_wall_ns']) <= int(fact['event_wall_ns']) <= int(fact['capture_wall_ns']), 'g32_prospective_order')
        _require(proposal['created_at']==int(fact['claim_wall_ns'])//10**9 and observation['event_time']==int(fact['event_wall_ns'])//10**9,'g32_clock_binding')
        _require(source['expectation']['created_at']==proposal['created_at'],'g32_lookahead')
        _integer(fact['elapsed_ns']);_integer(fact['sequence']);_integer(fact['work_count'],64)
        _require(fact['reached_boundary'] in ('WORK_ROOT','SEMANTIC_VALIDATION'))
        _require(fact['capture_ref']==observation['source_id'] and fact['semantic_ref']==proposal['source_id'],'g32_native_refs')
        for name in ('material_sha256','output_sha256'):
            _require(fact[name] is None if fact['reached_boundary']=='SEMANTIC_VALIDATION' else type(fact[name]) is str and _HEX.fullmatch(fact[name]) is not None)
        for name in ('root_decision_ref','plan_artifact_ref','result_artifact_ref'):
            if fact['reached_boundary']=='SEMANTIC_VALIDATION':
                _require(fact[name] is None)
            else:
                _text(fact[name])
        _time_shape(fact['time_envelope'],native=True)
    else:
        _require(source['expectation']['created_at'] <= proposal['created_at'] < observation['event_time'], 'g31_lookahead')
    return source, identity


PREDICTIVE_SOURCE_PROFILE_ID = 'G34_CONTROLLED_BOOLEAN_WORK_PREDICTION_V01'


@dataclass(frozen=True, slots=True)
class PredictiveOutcomeSourceContextV01:
    """Independent retained application source, never authority parsed from feedback.

    The producer authenticates its retained native capture. This pure boundary
    checks the exact typed claim/result relationship, not a supplied healthy flag.
    """
    canonical: bytes

    def __post_init__(self):
        _predictive_source_v01(self)


def _predictive_source_v01(bundle):
    from hedgehog.kernel import abi_v01 as abi
    import hashlib

    _require(type(bundle) is PredictiveOutcomeSourceContextV01, 'g34_independent_source_required')
    _require(type(bundle.canonical) is bytes and len(bundle.canonical) <= 1048576, 'g34_source_bound')
    value = json.loads(bundle.canonical)
    _require(canonical_json_bytes_v01(value) == bundle.canonical, 'g34_source_canonical')
    _keys(value, ('profile', 'native_source', 'claim_artifact', 'result_artifact'))
    _require(value['profile'] == PREDICTIVE_SOURCE_PROFILE_ID, 'g34_source_profile')
    base, _ = _source(NativeOutcomeSourceContextV01(_canonical(value['native_source'])), NATIVE_SOURCE_PROFILE_ID)
    artifacts = []
    for name in ('claim_artifact', 'result_artifact'):
        data = value[name]
        artifact = abi.build_kernel_artifact_v01(**{**data, 'trace_refs':tuple(data['trace_refs']), 'parent_refs':tuple(data['parent_refs'])})
        _require(abi.kernel_artifact_to_plain_dict_v01(artifact) == data, 'g34_typed_artifact')
        artifacts.append(data)
    claim, result = artifacts
    p = claim['payload']
    _keys(p, ('profile', 'predicted', 'expected_fp', 'claim_wall_ns', 'dependencies_sha256',
        'semantic_ref', 'operation', 'source_observation_refs', 'policy_ref', 'valid_from', 'valid_to', 'sequence'))
    _require(p['profile'] == PREDICTIVE_SOURCE_PROFILE_ID and type(p['predicted']) is bool, 'g34_prediction_type')
    _require((p['expected_fp'] is None or type(p['expected_fp']) is int and 0<=p['expected_fp']<=Q)
        and p['expected_fp'] == base['expectation']['expected_fp'] and type(p['sequence']) is int
        and 1<=p['sequence']<=64, 'g34_expectation_binding')
    _require(claim['artifact_type'] == 'SemanticEvidence' and claim['authority_class'] == 'EVIDENCE_ONLY'
        and result['artifact_type'] == 'ResultProposal' and result['authority_class'] == 'EVIDENCE_ONLY', 'g34_evidence_type')
    ctx, fact = base['context'], base['native']
    _require(all(a['owner_root_id'] == ctx['local_root_scope_id'] and a['transaction_id'] == ctx['transaction_id'] for a in artifacts), 'g34_root_transaction')
    _require(result['artifact_id'] == fact['result_artifact_ref'] and p['semantic_ref'] == fact['semantic_ref']
        and p['dependencies_sha256'] == fact['dependencies_sha256'] and p['policy_ref'] == base['policy']['revision']
        and p['operation'] == base['proposal']['operation'], 'g34_source_binding')
    _require(type(p['claim_wall_ns']) is str and p['claim_wall_ns'].isdigit()
        and int(p['claim_wall_ns']) <= int(fact['claim_wall_ns']) <= int(fact['event_wall_ns']), 'g34_prediction_lookahead')
    _integer(p['valid_from'], 253402300799); _integer(p['valid_to'], 253402300799)
    _require(p['valid_from'] == int(p['claim_wall_ns'])//10**9 and 0 < p['valid_to']-p['valid_from'] <= 604800, 'g34_frozen_window')
    _require(claim['time_envelope']==dict(pt_created_at=_utc(p['valid_from']),kt_asof=_utc(p['valid_from']),
        et_observed_at=None,ct_session_anchor=fact['time_envelope']['ct_session_anchor'],
        ttl_seconds=p['valid_to']-p['valid_from'],freshness_class='static',
        valid_from=_utc(p['valid_from']),valid_to=_utc(p['valid_to'])),'g34_claim_envelope_binding')
    _strings(p['source_observation_refs'])
    rows = result['payload']['work_results']
    _require(len(rows) == 1 and rows[0]['status'] == 'COMPLETED', 'g34_completed_result')
    row = rows[0]
    _require(row['result']['outcome'] == 'SUCCEEDED', 'g34_completed_result')
    inputs = {v['parameter_name']:v['value'] for v in row['invocation']['inputs']}
    outputs = {v['parameter_name']:v['value'] for v in row['result']['output']}
    material, output = json.loads(inputs['material']), json.loads(outputs['material'])
    digest = lambda data: hashlib.sha256(canonical_json_bytes_v01(data)).hexdigest()
    _require(digest(material) == fact['material_sha256'] and digest(output) == fact['output_sha256']
        and output['input_sha256'] == digest(material), 'g34_work_material_binding')
    _require(output['stage'] == 'RESULT' and len(output['checks']) == 1 and len(material['checks']) == 1
        and output['semantic_refs'] == [p['semantic_ref']], 'g34_output_shape')
    actual = output['checks'][0]['healthy']
    _require(type(actual) is bool and output['checks'][0]['semantic_ref'] == p['semantic_ref'], 'g34_boolean_output')
    _require(sorted(p['source_observation_refs']) == sorted(v['observation_id'] for v in material['checks'][0]['observations']), 'g34_observation_binding')
    _require(claim['artifact_id'] == 'g34:prediction:' + digest(p), 'g34_claim_identity')
    source = json.loads(_canonical(base))
    source['source_profile_id'] = PREDICTIVE_SOURCE_PROFILE_ID
    source['context'].update(advice_claim_profile_id=PREDICTIVE_SOURCE_PROFILE_ID,
        validation_profile_id='G34_TYPED_BOOLEAN_COMPLETED_WORK_V01')
    source['expectation']['source_id'] = claim['artifact_id']
    source['native']['sequence'] = p['sequence']
    event_time = base['observation']['event_time']
    _require(event_time < p['valid_to'], 'g34_outcome_window_expired')
    source['native']['time_envelope'] = dict(claim['time_envelope'],pt_created_at=_utc(event_time),
        et_observed_at=_utc(event_time),valid_from=_utc(event_time),ttl_seconds=p['valid_to']-event_time)
    source['predictive'] = dict(predicted=p['predicted'], actual=actual)
    return source, domain_separated_sha256_hex_v01(domain='g34_predictive_source_v01', payload=bundle.canonical)


def _source_refs(source: dict) -> list[str]:
    if source['source_profile_id'] in G35_PROFILES:
        return list(dict.fromkeys(source[key]['source_id'] for key in ('context','policy','origin','proposal','expectation','observation','closure')))
    return [source[key]['source_id'] for key in ('context', 'policy', 'origin', 'proposal', 'expectation', 'observation', 'closure')]


def _observation(source: dict, identity: str, times: dict) -> dict:
    _keys(times, ('ingested_time', 'evaluated_at', 'timestamp'))
    material = dict(schema_version='v0.1', source_profile_id=source['source_profile_id'],
                    source_bundle_ref=identity, event_time=source['observation']['event_time'],
                    source_refs=_source_refs(source), **times)
    material['observation_id'] = _identity('g3_observation_v01', material)
    _observation_shape(material)
    if source['source_profile_id']==SOURCE_PROFILE_ID:
        _require(material['timestamp'] < material['event_time'] + 3600, 'g31_reference_time_expired')
    else:
        _require(material['ingested_time'] >= int(source['native']['capture_wall_ns'])//10**9,'g32_ingest_before_capture')
    return material


def build_outcome_observation_v01(*, source_bundle: dict, profile: str, explicit_times: dict) -> OutcomeObservationV01:
    source, identity = _source(source_bundle, profile)
    return OutcomeObservationV01(_canonical(_observation(source, identity, explicit_times)))


def _checked_observation(observation: OutcomeObservationV01, source: dict, identity: str) -> dict:
    _require(type(observation) is OutcomeObservationV01)
    plain = _decode(observation.canonical)
    _observation_shape(plain)
    expected = _observation(source, identity, {k:plain[k] for k in ('ingested_time', 'evaluated_at', 'timestamp')})
    _require(plain == expected, 'g31_observation_source_mismatch')
    return plain


def validate_outcome_observation_v01(observation: object, *, source_bundle: dict, profile: str) -> tuple[str, ...]:
    try:
        source, identity = _source(source_bundle, profile)
        _checked_observation(observation, source, identity)
        return ()
    except (ValueError, TypeError, KeyError, AttributeError, RecursionError) as exc:
        return _error(exc)


def _known(value, unit, refs):
    return TaggedValueV01('KNOWN', value, '', tuple(refs), unit).to_plain_data()


def _absent(unit, state='NOT_REACHED', reason='REFERENCE_FIXTURE_NOT_EXECUTED'):
    return TaggedValueV01(state, None, reason, (), unit).to_plain_data()


def _utc(seconds: int) -> str:
    return datetime.fromtimestamp(seconds, timezone.utc).isoformat(timespec='seconds')


def _derive(source: dict, identity: str, observation: dict) -> dict:
    ctx, policy, proposal, obs = (source[k] for k in ('context', 'policy', 'proposal', 'observation'))
    refs = _source_refs(source)
    allowed = all(proposal[k] == policy[k] for k in ('operation', 'object_id', 'recipient'))
    missing = obs['boundary_disposition'] == 'NOT_OBSERVED' or obs['failure'] != 'NONE'
    comparable = not missing and source['expectation']['expected_fp'] is not None
    quality = ('CORRECT' if (proposal['recommendation'] == 'PROCEED') == allowed else
               'UNSAFE' if proposal['recommendation'] == 'PROCEED' else 'INCORRECT') if comparable else 'NOT_SCORABLE'
    if source['source_profile_id'] == PREDICTIVE_SOURCE_PROFILE_ID and comparable:
        quality = 'CORRECT' if source['predictive']['predicted'] == source['predictive']['actual'] else 'INCORRECT'
    unexpected = (not allowed or source['source_profile_id'] in (NATIVE_SOURCE_PROFILE_ID, PREDICTIVE_SOURCE_PROFILE_ID)) and obs['effect_count'] is not None and obs['effect_count'] > 0
    enforcement = ('UNEXPECTED_EFFECT' if unexpected else 'UNKNOWN' if missing else
                   'BLOCKED_AS_REQUIRED' if not allowed and obs['boundary_disposition'] == 'STOPPED' else
                   'ALLOWED_AS_REQUIRED' if allowed and obs['boundary_disposition'] == 'PERMITTED' else 'UNKNOWN')
    task = ('FAILED' if unexpected or obs['failure'] in ('TRANSPORT_FAILURE', 'EXECUTOR_FAILURE') else
            'NEEDS_INPUT' if missing else 'COMPLETED' if obs['result_state'] == 'PRESENT' else
            'SAFE_NO_DEAL' if enforcement == 'BLOCKED_AS_REQUIRED' else 'NEEDS_INPUT')
    execution = {'COMPLETED':'COMPLETED','SAFE_NO_DEAL':'BLOCKED_BEFORE_EFFECT','NEEDS_INPUT':'NEEDS_MORE_EVIDENCE','FAILED':'EXECUTOR_FAILED'}[task]
    if obs['failure'] == 'TRANSPORT_FAILURE':
        execution = 'TRANSPORT_FAILED'
    failure = obs['failure'] if obs['failure'] != 'NONE' else 'PROPOSAL_UNSAFE' if quality == 'UNSAFE' else 'PROPOSAL_INVALID' if quality == 'INCORRECT' else 'NONE'
    eligible = comparable and not unexpected
    eligibility = 'ELIGIBLE' if eligible else 'NO_UPDATE'
    reason = 'REFERENCE_COMPARABLE_CLAIM' if eligible else 'UNEXPECTED_EFFECT_INVARIANT' if unexpected else 'NO_COMPARABLE_EXPECTATION_OR_OBSERVATION'
    subject = {k: ctx[k] for k in _SUBJECT_FIELDS if k in ctx}
    subject.update(domain_scope_id=ctx['domain'], advice_claim_profile_id=CLAIM_PROFILE_ID)
    history = {k: ctx[k] for k in _HISTORY_FIELDS if k in ctx}
    history.update(domain_scope_id=ctx['domain'], evidence_validation_profile_id=ctx['validation_profile_id'])
    epoch = observation['event_time']
    times = dict(ct_session_anchor=_utc(proposal['created_at']), et_observed_at=_utc(epoch),
                 freshness_class='static', kt_asof=_utc(epoch), pt_created_at=_utc(observation['timestamp']),
                 ttl_seconds=3600, valid_from=_utc(epoch), valid_to=_utc(epoch+3600))
    validation = _identity('g3_context_report_v01', {'source_bundle_ref':identity, 'observation_id':observation['observation_id'], 'profile':SOURCE_PROFILE_ID})
    result = {k:ctx[k] for k in ('transaction_id','run_id','episode_id','scenario_id','domain','pack_family_id','local_root_scope_id')}
    result.update(profile_id=PROFILE_ID, schema_version='v0.1', numeric_profile_id=NUMERIC_PROFILE_ID,
        source_profile_id=SOURCE_PROFILE_ID, evidence_class=REFERENCE_CLASS,
        observation_id=observation['observation_id'], strategy_candidate_id=proposal['source_id'],
        context_fingerprint=_identity('g3_context_v01', {'context':ctx,'policy':policy,'closure':source['closure']}),
        execution_lane='HISTORICAL_IMPORT', advisory_subject_key=subject, avf_history_key=history,
        parent_correlation_ref=_absent('REFERENCE','NOT_APPLICABLE','SINGLE_ROOT_REFERENCE'),
        proposal_ref=_known(proposal['source_id'],'REFERENCE',[proposal['source_id'],source['origin']['source_id']]),
        avf_prediction=_absent('FP_Q','UNKNOWN','NO_PRE_OUTCOME_AVF'),
        avf_rank=_absent('RANK','NOT_APPLICABLE','NO_RANKING'), gt_advice_ref=_absent('REFERENCE'),
        pre_decision_expectation=(_known(source['expectation']['expected_fp'],'FP_Q',[source['expectation']['source_id']]) if source['expectation']['expected_fp'] is not None else _absent('FP_Q','UNKNOWN','NO_PRE_OUTCOME_EXPECTATION')),
        prior_state_ref=_absent('REFERENCE','NOT_APPLICABLE','NO_ACCEPTED_HISTORY'),
        decision_basis_refs=[policy['source_id'],source['closure']['source_id']], advice_claim_profile_id=CLAIM_PROFILE_ID,
        root_decision_ref=_absent('REFERENCE'), other_root_evidence_refs=[], action_packet_ref=_absent('REFERENCE'),
        firewall_decision_ref=_absent('REFERENCE'), receipt_refs=[], execution_status=execution,
        blocking_stage='TRANSPORT' if execution=='TRANSPORT_FAILED' else 'OBSERVATION' if missing else 'SEMANTIC_VALIDATION' if obs['boundary_disposition']=='STOPPED' else 'NONE',
        validation_status='CONTEXT_VALIDATED', failure_class=failure,
        manual_override=_absent('REFERENCE','NOT_APPLICABLE','NO_OVERRIDE'),
        policy_violations={'attempted_violation_refs':[proposal['source_id']] if not allowed and proposal['recommendation']=='PROCEED' else [], 'realized_violation_refs':[obs['source_id']] if unexpected else []},
        observation_scope={'mechanism':REFERENCE_CLASS,'occurrence_ref':source['origin']['occurrence_id'],
                           'operation_ref':proposal['source_id'],'measurement_refs':[obs['source_id']],
                           'limitations':'REFERENCE_ONLY_NOT_HOST_EXECUTION'},
        proposal_assessment=quality, enforcement_outcome=enforcement, task_outcome=task,
        attribution={'subject_ref':proposal['source_id'],'claim_profile_id':CLAIM_PROFILE_ID,'reason_code':reason,
                     'source_refs':[policy['source_id'],obs['source_id']],'scoring_eligibility':eligibility},
        observed_result=_known(Q if quality=='CORRECT' else 0,'FP_Q',[obs['source_id'],policy['source_id']]) if comparable else _absent('FP_Q','UNKNOWN','NO_COMPARABLE_OBSERVATION'),
        observed_regret=_absent('FP_Q','UNKNOWN','NO_COUNTERFACTUAL'), update_eligibility=eligibility, update_reasons=[reason],
        actual_cost={**{k:_absent('COUNT','UNKNOWN','NOT_MEASURED') for k in ('model_calls','input_tokens','output_tokens','work_invocations')},
                     'money':_absent('MINOR_UNITS','UNKNOWN','NOT_MEASURED'),'currency':_absent('CURRENCY','UNKNOWN','NOT_MEASURED'),'scope_ref':obs['source_id']},
        actual_latency={'elapsed_us':_absent('MICROSECONDS','UNKNOWN','NOT_MEASURED'), 'phase_scope':'REFERENCE_NOT_EXECUTED', 'receipt_ref':_absent('REFERENCE')},
        **{k:observation[k] for k in ('timestamp','event_time','ingested_time','evaluated_at')}, causal_event_sequence=0,
        time_envelope=times, source_refs=refs, provenance_refs=[source['origin']['source_id']], validation_refs=[validation],
        predecessor_feedback_ref=_absent('REFERENCE','NOT_APPLICABLE','NO_PREDECESSOR'),
        supersedes_ref=_absent('REFERENCE','NOT_APPLICABLE','NO_CORRECTION'),
        correction_reason=_absent('TEXT','NOT_APPLICABLE','NO_CORRECTION'), source_closure_ref=source['closure']['source_id'],
        non_authority_flags={'claims_permission':False,'claims_root_decision':False,'requests_effect':False})
    result['feedback_id'] = _identity('g3_feedback_v01', result)
    if source['source_profile_id'] in (NATIVE_SOURCE_PROFILE_ID, PREDICTIVE_SOURCE_PROFILE_ID):
        fact=source['native'];reached=fact['reached_boundary']=='WORK_ROOT'
        result.update(source_profile_id=NATIVE_SOURCE_PROFILE_ID,evidence_class='NATIVE_CONTROLLED_OBSERVATION',
            execution_lane='CONTROLLED_RUNTIME',advice_claim_profile_id=ctx['advice_claim_profile_id'],
            causal_event_sequence=fact['sequence'],time_envelope=fact['time_envelope'])
        result['advisory_subject_key']['advice_claim_profile_id']=ctx['advice_claim_profile_id']
        result['attribution']['claim_profile_id']=ctx['advice_claim_profile_id']
        if eligible:
            result['attribution']['reason_code']='NATIVE_COMPARABLE_CLAIM'
            result['update_reasons']=['NATIVE_COMPARABLE_CLAIM']
        result['root_decision_ref']=_known(fact['root_decision_ref'],'REFERENCE',[fact['result_artifact_ref']]) if reached else _absent('REFERENCE',reason='REFUSED_BEFORE_WORK_ROOT')
        result['action_packet_ref']=_absent('REFERENCE','NOT_APPLICABLE' if reached else 'NOT_REACHED','PURE_WORK_NO_ACTION' if reached else 'REFUSED_BEFORE_WORK_ROOT')
        result['firewall_decision_ref']=dict(result['action_packet_ref'])
        result['gt_advice_ref']=_absent('REFERENCE','NOT_APPLICABLE','NO_PROSPECTIVE_MODEL_GT')
        result['observation_scope'].update(mechanism='NATIVE_PUBLIC_WORK_ROOT' if reached else 'NATIVE_SEMANTIC_VALIDATION',limitations='CONTROLLED_LOCAL_API_NOT_PHYSICAL_CERTIFICATION')
        result['actual_cost']['work_invocations']=_known(fact['work_count'],'COUNT',[fact['capture_ref']])
        result['actual_cost']['model_calls']=_known(0,'COUNT',[source['origin']['source_id']])
        result['actual_latency']={'elapsed_us':_known(fact['elapsed_ns']//1000,'MICROSECONDS',[fact['capture_ref']]),
            'phase_scope':'TARGET_ROLE_ONLY_EXCLUDES_BOOTSTRAP','receipt_ref':_known(fact['capture_ref'],'REFERENCE',[fact['capture_ref']])}
        result['source_refs']=list(dict.fromkeys(result['source_refs']+[fact['capture_ref'],fact['semantic_ref']]+([fact['plan_artifact_ref'],fact['result_artifact_ref'],fact['root_decision_ref']] if reached else [])))
        result['validation_refs']=[_identity('g3_context_report_v01',{'source_bundle_ref':identity,'observation_id':observation['observation_id'],'profile':NATIVE_SOURCE_PROFILE_ID})]
        if not reached and not unexpected:
            result.update(proposal_assessment='NOT_SCORABLE',enforcement_outcome='BLOCKED_AS_REQUIRED',task_outcome='NEEDS_INPUT',
                execution_status='NEEDS_MORE_EVIDENCE',blocking_stage='SEMANTIC_VALIDATION',failure_class='OBSERVATION_INCOMPLETE',update_eligibility='NO_UPDATE')
        result['feedback_id']=_identity('g3_feedback_v01',{k:v for k,v in result.items() if k!='feedback_id'})
    if source['source_profile_id'] == PREDICTIVE_SOURCE_PROFILE_ID:
        result['source_profile_id'] = PREDICTIVE_SOURCE_PROFILE_ID
        result['validation_refs'] = [_identity('g3_context_report_v01', dict(source_bundle_ref=identity,
            observation_id=observation['observation_id'], profile=PREDICTIVE_SOURCE_PROFILE_ID))]
        result['feedback_id'] = _identity('g3_feedback_v01', {k:v for k,v in result.items() if k!='feedback_id'})
    if source['source_profile_id'] in G35_PROFILES:
        fact = source['g35']
        result.update(source_profile_id=source['source_profile_id'], evidence_class='CONTROLLED_SAFE_DERIVED_SOURCE',
            execution_lane='CONTROLLED_RUNTIME', advice_claim_profile_id=ctx['advice_claim_profile_id'],
            time_envelope=source['native']['time_envelope'], proposal_assessment=fact['quality'],
            enforcement_outcome=fact['enforcement'], task_outcome=fact['task'], execution_status=fact['execution'],
            blocking_stage=fact['stage'], update_eligibility='NO_UPDATE', failure_class='NONE',
            update_reasons=['NO_PROSPECTIVE_COMPARABLE_EXPECTATION'])
        result['advisory_subject_key']['advice_claim_profile_id']=ctx['advice_claim_profile_id']
        result['attribution'].update(claim_profile_id=ctx['advice_claim_profile_id'],
            reason_code='NO_PROSPECTIVE_COMPARABLE_EXPECTATION',scoring_eligibility='NO_UPDATE')
        for key in ('root_decision_ref','action_packet_ref','firewall_decision_ref'):
            result[key]=_known(fact[key],'REFERENCE',[obs['source_id']]) if fact[key] else _absent('REFERENCE','NOT_APPLICABLE','BOUNDARY_NOT_EXERCISED')
        result['receipt_refs']=fact['receipt_refs']
        result['other_root_evidence_refs']=fact['other_root_evidence_refs']
        result['policy_violations']['attempted_violation_refs']=[proposal['source_id']] if fact['quality']=='UNSAFE' else []
        result['observation_scope'].update(mechanism='G35_PUBLIC_SOURCE_SAFE_DERIVATION',limitations='CONTROLLED_NOT_LIVE;UNSUPPORTED_NATIVE_SCHEMA;NO_AUTHORITY_REPLAY')
        result['actual_cost']['model_calls']=_known(0,'COUNT',[obs['source_id']])
        result['actual_cost']['work_invocations']=_known(fact['work_count'],'COUNT',[obs['source_id']])
        result['actual_latency']=dict(elapsed_us=_known(fact['elapsed_us'],'MICROSECONDS',[obs['source_id']]),
            phase_scope='DOMAIN_COLLECTION_INCLUDES_VALIDATION',receipt_ref=_known(obs['source_id'],'REFERENCE',[obs['source_id']]))
        result['gt_advice_ref']=_absent('REFERENCE','NOT_APPLICABLE','NO_PROSPECTIVE_MODEL_GT')
        result['validation_refs']=[_identity('g3_context_report_v01',dict(source_bundle_ref=identity,observation_id=observation['observation_id'],profile=source['source_profile_id']))]
        result['feedback_id']=_identity('g3_feedback_v01',{k:v for k,v in result.items() if k!='feedback_id'})
    if source['source_profile_id'] == ACTION_ADVICE_SOURCE_PROFILE_ID:
        from hedgehog.domains.supplier_water_filter.adversarial_feedback_v01 import project_feedback_v01
        return project_feedback_v01(result,source,identity,observation)
    return result


def build_outcome_feedback_v01(*, observation: OutcomeObservationV01, source_bundle: dict, profile: str) -> OutcomeFeedbackEnvelopeV01:
    source, identity = _source(source_bundle, profile)
    return _feedback_from_source_v01(observation, source, identity)


def _feedback_from_source_v01(observation, source, identity):
    checked = _checked_observation(observation, source, identity)
    return OutcomeFeedbackEnvelopeV01(_canonical(_derive(source, identity, checked)))


def validate_outcome_feedback_against_sources_v01(feedback: object, *, source_bundle: dict, profile: str) -> tuple[str, ...]:
    try:
        _require(type(feedback) is OutcomeFeedbackEnvelopeV01)
        plain = _decode(feedback.canonical)
        _feedback_shape(plain)
        source, identity = _source(source_bundle, profile)
        observation = _observation(source, identity, {k:plain[k] for k in ('ingested_time','evaluated_at','timestamp')})
        expected = _derive(source, identity, observation)
        _require(_canonical(plain) == _canonical(expected), 'g31_feedback_source_mismatch')
        return ()
    except (ValueError, TypeError, KeyError, AttributeError, RecursionError) as exc:
        return _error(exc)


def outcome_feedback_to_plain_data_v01(feedback: OutcomeFeedbackEnvelopeV01) -> dict:
    _require(type(feedback) is OutcomeFeedbackEnvelopeV01)
    plain = _decode(feedback.canonical)
    _feedback_shape(plain)
    return plain


def project_outcome_feedback_evidence_v01(feedback: OutcomeFeedbackEnvelopeV01, *, source_bundle: dict,
                                        profile: str, current_abi_context: dict) -> KernelArtifactV01:
    errors = validate_outcome_feedback_against_sources_v01(feedback, source_bundle=source_bundle, profile=profile)
    _require(not errors, errors[0] if errors else 'g31_feedback_invalid')
    plain = outcome_feedback_to_plain_data_v01(feedback)
    _keys(current_abi_context, ('artifact_id','transaction_id','owner_root_id','parent_refs','time_envelope'))
    _text(current_abi_context['artifact_id'])
    _require(current_abi_context['transaction_id']==plain['transaction_id']
             and current_abi_context['owner_root_id']==plain['local_root_scope_id']
             and current_abi_context['parent_refs']==[]
             and current_abi_context['time_envelope']==plain['time_envelope'], 'g31_abi_context_mismatch')
    return build_kernel_artifact_v01(abi_version='v1.0', artifact_id=current_abi_context['artifact_id'],
        artifact_type='SemanticEvidence', schema_version='v1', transaction_id=plain['transaction_id'],
        owner_root_id=plain['local_root_scope_id'], source_component='outcome_feedback_v01',
        authority_class='EVIDENCE_ONLY', lifecycle_state='VALIDATED',
        payload={'g3_profile_id':PROFILE_ID,'feedback':plain}, trace_refs=(plain['feedback_id'],),
        parent_refs=(), time_envelope=plain['time_envelope'])


# Finite source profiles are distinct from the historical Sentinel-only profile.
G35_PROFILES = ('G35_AIRLINE_CORRIDOR_V01', 'G35_SUPPLIER_NATIVE_ACTION_V01',
    'G35_TESTFLIX_NATIVE_ACTION_V01', 'G35_WORKSPACE_CONSUMED_WORK_V01', 'G35_SENTINEL_WORK_V01')
G35_DOMAINS = ('AIRLINE', 'SUPPLIER_WATER_FILTER', 'TESTFLIX', 'EPHEMERAL_WORKSPACE', 'LANDSLIDE_SENTINEL')


def g35_bytes_v01(value):
    """Source bodies have a separate finite bound; OFE limits do not change."""
    raw = canonical_json_bytes_v01(value)
    _require(len(raw) <= 32 * 1024 * 1024, 'g35_source_size')
    return raw


def g35_hash_v01(value):
    return domain_separated_sha256_hex_v01(domain='g35_saved_source_v01',payload=g35_bytes_v01(value))


def _g35_record_types_v01():
    """Closed local data types only. No Host, installed callable or origin handle."""
    from dataclasses import is_dataclass
    from hedgehog.kernel import root_decision_v01, semantic_work_v01, transition_registry_v01, abi_v01, effect_firewall_v01, work_composition_v01
    from hedgehog import action_commit_packet_v02
    from hedgehog.domains.airline import semantic_to_contract_binding_v01, semantic_to_contract_causal_runtime_v01
    from hedgehog.domains.airline import ticket_purchase_corridor_v01, ticket_purchase_corridor_runtime_v01
    from hedgehog.domains.airline import transaction_artifact_ledger_v01, transaction_artifact_ledger_collector_v01
    modules=(root_decision_v01,semantic_work_v01,transition_registry_v01,abi_v01,effect_firewall_v01,work_composition_v01,action_commit_packet_v02,
        semantic_to_contract_binding_v01,semantic_to_contract_causal_runtime_v01,ticket_purchase_corridor_v01,
        ticket_purchase_corridor_runtime_v01,transaction_artifact_ledger_v01,transaction_artifact_ledger_collector_v01)
    return {m.__name__+'.'+name:cls for m in modules for name,cls in vars(m).items()
        if isinstance(cls,type) and is_dataclass(cls) and cls.__module__==m.__name__}


def g35_record_to_plain_v01(value):
    """Lossless data encoding, not a native replay or current-authority token."""
    from dataclasses import fields, is_dataclass
    from collections.abc import Mapping
    types=_g35_record_types_v01()
    def encode(v):
        if is_dataclass(v) and not isinstance(v,type):
            name=type(v).__module__+'.'+type(v).__name__
            _require(types.get(name) is type(v),'g35_record_type')
            return {'record_type':name,'fields':{f.name:encode(getattr(v,f.name)) for f in fields(v)}}
        if type(v) is tuple:return {'tuple_items':[encode(x) for x in v]}
        if type(v) is list:return [encode(x) for x in v]
        if isinstance(v,Mapping):return {k:encode(x) for k,x in v.items()}
        _require(v is None or type(v) in (str,int,bool,float),'g35_record_scalar')
        return v
    result=encode(value);g35_bytes_v01(result);return result


def g35_record_from_plain_v01(value):
    from dataclasses import fields
    types=_g35_record_types_v01()
    g35_bytes_v01(value)
    def decode(v,depth=0):
        _require(depth<=80,'g35_record_depth')
        if type(v) is dict:
            if 'record_type' in v:
                _keys(v,('record_type','fields'))
                _require(type(v['record_type']) is str and v['record_type'] in types,'g35_record_type')
                cls=types[v['record_type']];_keys(v['fields'],[f.name for f in fields(cls)])
                return cls(**{k:decode(x,depth+1) for k,x in v['fields'].items()})
            if 'tuple_items' in v:
                _keys(v,('tuple_items',));_require(type(v['tuple_items']) is list,'g35_tuple_shape')
                return tuple(decode(x,depth+1) for x in v['tuple_items'])
            return {k:decode(x,depth+1) for k,x in v.items()}
        if type(v) is list:return [decode(x,depth+1) for x in v]
        _require(v is None or type(v) in (str,int,bool,float),'g35_record_scalar')
        return v
    return decode(value)


def g35_validate_root_v01(saved):
    from hedgehog.kernel import root_decision_v01 as roots
    _require(type(saved) is list and len(saved)==3,'g35_root_shape')
    kernel,inputs,result=(g35_record_from_plain_v01(v) for v in saved)
    _require(not roots.validate_root_decision_result_v01(kernel=kernel,decision_input=inputs,result=result),'g35_root_result')
    return inputs,result


def g35_validate_artifact_v01(plain):
    from hedgehog.kernel import abi_v01 as abi
    _keys(plain,('abi_version','artifact_id','artifact_type','schema_version','transaction_id','owner_root_id',
        'source_component','authority_class','lifecycle_state','payload','trace_refs','parent_refs','time_envelope'))
    artifact=abi.build_kernel_artifact_v01(**dict(plain,trace_refs=tuple(plain['trace_refs']),parent_refs=tuple(plain['parent_refs'])))
    _require(not abi.validate_kernel_artifact_v01(artifact),'g35_artifact_invalid')
    return artifact


def g35_validate_work_records_v01(saved, admissions):
    from hedgehog.kernel import effect_firewall_v01 as fw, abi_v01 as abi
    records=g35_record_from_plain_v01(saved)
    snapshots=g35_record_from_plain_v01(admissions)
    by_id={v.admission_id:v for v in snapshots}
    _require(type(records) is tuple and 1<=len(records)<=8,'g35_work_records')
    completed={}
    for r in records:
        _require(r.status=='COMPLETED' and r.result is not None,'g35_work_completion')
        _require(r.invocation.admission_id in by_id and not fw.validate_capability_execution_result_v01(r.result,r.invocation,by_id[r.invocation.admission_id]),'g35_work_result')
        _require(all(not abi.validate_causal_consumption_ref_v01(c) for c in r.consumed_fields),'g35_consumption_ref')
        for c in r.consumed_fields:
            _require(c.source_artifact_id in completed,'g35_consumption_predecessor')
            predecessor=completed[c.source_artifact_id]
            name=c.output_field.removeprefix('/')
            before={v.parameter_name:v for v in predecessor.result.output}
            after={v.parameter_name:v for v in r.invocation.inputs}
            _require(c.producer_actor_id==predecessor.work_id and c.consumer_component=='work_composition' and
                c.downstream_artifact_id==r.invocation.work_instance_id and c.disposition=='USED' and
                name in before and name in after and before[name]==after[name],'g35_consumption_value_binding')
        completed[r.result.result_id]=r
    return records


def _g35_checked_work_relation_v01(topology_plain, result_plain, rows, admissions):
    """Bind already checked saved rows to the native projection, not live authority."""
    from hedgehog import action_commit_packet_v02 as action
    from hedgehog.kernel import abi_v01 as abi, work_composition_v01 as work
    topology=g35_validate_artifact_v01(topology_plain)
    result=g35_validate_artifact_v01(result_plain)
    top=work._payload(topology_plain['payload'],'topology_payload')
    program=top['work_program']
    def binding(plain):
        source=plain['source']
        if set(source)=={'value'}:
            value=work.WorkLiteralV01(action.ActionEffectParameterRecordV01(**source['value']))
        else:
            _keys(source,('predecessor_work_id','output_field','expected_type'))
            value=work.WorkOutputBindingV01(**source)
        return work.WorkInputBindingV01(plain['input_field'],value)
    items=tuple(work.WorkItemV01(**dict(item,inputs=tuple(binding(v) for v in item['inputs']),
        resource_refs=tuple(item['resource_refs']),depends_on=tuple(item['depends_on']),
        guard=None if item['guard'] is None else work.WorkOutputBindingV01(**item['guard']))) for item in program['items'])
    candidate=work.WorkProgramCandidateV01(**dict(program,budget=work.WorkBudgetV01(**program['budget']),items=items,
        trigger_evidence_refs=tuple(program['trigger_evidence_refs'])))
    _require(candidate.revision_id==work._revision(candidate),'g35_work_program_revision')
    order=work._order(items)
    _require(len({i.work_id for i in items})==len(items)==len(rows) and
        list(order)==top['ordered_work_ids']==[r.work_id for r in rows],'g35_work_program_order')
    trace=(candidate.task_id,candidate.revision_id)
    _require((topology.abi_version,topology.schema_version,topology.artifact_type,topology.source_component,topology.authority_class,topology.lifecycle_state)==
        ('v1.0','v1','RuntimeExecutionTopology','runtime','NON_AUTHORITY','VALIDATED') and
        topology.artifact_id==work._identity('work_topology',top) and topology.trace_refs==trace and
        topology.parent_refs==(work._identity('work_proposal',{'work_program':program}),),'g35_work_topology_projection')
    expected=work._payload(dict(topology_ref=topology.artifact_id,work_results=[work._plain(r) for r in rows]),'result_payload')
    _require(g35_bytes_v01(result_plain['payload'])==g35_bytes_v01(expected),'g35_work_result_payload_relation')
    _require((result.abi_version,result.schema_version,result.artifact_type,result.source_component,result.authority_class,result.lifecycle_state)==
        ('v1.0','v1','ResultProposal','work_composition','EVIDENCE_ONLY','PROPOSED') and
        result.artifact_id==work._identity('work_results',expected) and result.trace_refs==trace and
        result.parent_refs==(topology.artifact_id,) and result.owner_root_id==topology.owner_root_id and
        result.transaction_id==topology.transaction_id and result_plain['time_envelope']==topology_plain['time_envelope'],
        'g35_work_result_envelope_relation')
    snapshots=g35_record_from_plain_v01(admissions);by_id={a.admission_id:a for a in snapshots}
    _require(len(by_id)==len(snapshots),'g35_work_admission_unique')
    by_work={i.work_id:i for i in items};completed={}
    for row in rows:
        item=by_work[row.work_id];invocation=row.invocation;admission=by_id[invocation.admission_id]
        _require((row.task_id,row.revision_id)==trace and row.status=='COMPLETED' and row.reasons==() and
            row.result.outcome=='SUCCEEDED' and invocation.task_id==candidate.task_id and
            invocation.work_instance_id==work._work_ref(candidate,item),'g35_work_row_context')
        _require(invocation.definition_id==item.definition_id==admission.definition.definition_id and
            invocation.owning_root_id==item.owning_root_id==topology.owner_root_id and
            invocation.resource_refs==item.resource_refs==admission.definition.resource_refs and
            candidate.catalogue_revision==admission.catalogue_revision,'g35_work_item_capability')
        _require(all(key in completed for key in item.depends_on) and item.guard is None,'g35_work_item_dependencies')
        inputs=[];refs=[]
        for bound in item.inputs:
            source=bound.source
            if type(source) is work.WorkLiteralV01:value=source.value
            else:
                _require(source.predecessor_work_id in item.depends_on,'g35_work_input_dependency')
                previous=completed[source.predecessor_work_id]
                value=next(v for v in previous.result.output if v.parameter_name==source.output_field)
                _require(value.value_type==source.expected_type,'g35_work_input_type')
                refs.append(abi.build_causal_consumption_ref_v01(producer_actor_id=previous.work_id,
                    source_artifact_id=previous.result.result_id,output_field='/'+source.output_field.replace('~','~0').replace('/','~1'),
                    consumer_component='work_composition',downstream_artifact_id=invocation.work_instance_id,decision_effect='bind_input',
                    disposition='USED',reason_code='used:actual_output_field',
                    trace_refs=(candidate.task_id,candidate.revision_id,previous.invocation.invocation_id,item.work_id)))
            inputs.append(action.build_action_effect_parameter_record_v01(parameter_name=bound.input_field,value_type=value.value_type,value=value.value))
        _require(tuple(sorted(inputs,key=lambda v:v.parameter_name))==invocation.inputs and tuple(refs)==row.consumed_fields,
            'g35_work_program_input_relation')
        completed[row.work_id]=row
    return topology,result


def g35_fact_v01(*, root, transaction, proposal, decision=None, artifact=None, packet=None, firewall=None,
    receipts=(), other_roots=(), work_count=0, effect_count=0, task='COMPLETED', enforcement='ALLOWED_AS_REQUIRED',
    quality='NOT_SCORABLE', execution='COMPLETED', stage='OBSERVATION'):
    return dict(root=root,transaction=transaction,proposal=proposal,root_decision_ref=decision,
        result_artifact_ref=artifact,action_packet_ref=packet,firewall_decision_ref=firewall,receipt_refs=list(receipts),
        other_root_evidence_refs=list(other_roots),work_count=work_count,effect_count=effect_count,task=task,
        enforcement=enforcement,quality=quality,execution=execution,stage=stage)


def validate_g35_source_v01(source):
    """Validate saved public relationships; never recollect a domain producer."""
    from pathlib import Path
    from jsonschema import Draft202012Validator
    g35_bytes_v01(source)
    schema=json.loads((Path(__file__).resolve().parents[1]/'schemas/outcome_feedback_g35_sources_v01.schema.json').read_bytes())
    _require(next(Draft202012Validator(schema).iter_errors(source),None) is None,'g35_source_schema')
    _keys(source,('profile','domain','case_id','version','body','measurement','source_revision'))
    _require(source['version']=='v0.1' and source['profile'] in G35_PROFILES,'g35_profile')
    index=G35_PROFILES.index(source['profile'])
    _require(source['domain']==G35_DOMAINS[index] and source['case_id']=='G35-'+source['domain'],'g35_domain_binding')
    _require(type(source['source_revision']) is str and re.fullmatch(r'[0-9a-f]{64}',source['source_revision']),'g35_source_revision')
    m=source['measurement'];_keys(m,('started_ns','finished_ns','elapsed_us'))
    _require(all(type(m[k]) is str and re.fullmatch(r'[0-9]{1,20}',m[k]) for k in ('started_ns','finished_ns')),'g35_clock_shape')
    _require(int(m['finished_ns'])>=int(m['started_ns']),'g35_clock_order');_integer(m['elapsed_us'])
    from hedgehog.domains.airline.outcome_feedback_adapter_v01 import validate_source_v01 as airline
    from hedgehog.domains.supplier_water_filter.outcome_feedback_adapter_v01 import validate_source_v01 as supplier
    from hedgehog.domains.testflix.outcome_feedback_adapter_v01 import validate_source_v01 as testflix
    from hedgehog.domains.ephemeral_workspace.outcome_feedback_adapter_v01 import validate_source_v01 as workspace
    from hedgehog.domains.landslide_sentinel.outcome_feedback_adapter_v01 import validate_g35_source_v01 as sentinel
    facts=(airline,supplier,testflix,workspace,sentinel)[index](source['body'])
    _require(type(facts) is list and 1<=len(facts)<=8,'g35_facts')
    for f in facts:
        _require(f['effect_count']==0 or f['enforcement']=='ALLOWED_AS_REQUIRED','g35_unexpected_effect')
    return facts


@dataclass(frozen=True,slots=True)
class G35OutcomeSourceContextV01:
    """Independent saved source plus one local occurrence, never permission."""
    canonical: bytes
    occurrence: int

    def __post_init__(self):
        _require(type(self.canonical) is bytes and len(self.canonical)<=32*1024*1024,'g35_context_bytes')
        _require(type(self.occurrence) is int and 0<=self.occurrence<8,'g35_occurrence')
        value=json.loads(self.canonical,object_pairs_hook=_pairs)
        _require(g35_bytes_v01(value)==self.canonical,'g35_context_canonical')


def _g35_source_v01(bundle,profile):
    _require(type(bundle) is G35OutcomeSourceContextV01,'g35_independent_context_required')
    value=json.loads(bundle.canonical)
    _require(value['profile']==profile,'g35_profile_context')
    facts=validate_g35_source_v01(value)
    _require(bundle.occurrence<len(facts),'g35_occurrence')
    return _g35_occurrence_source_v01(value,profile,bundle.occurrence,facts[bundle.occurrence])


def _g35_occurrence_source_v01(value,profile,occurrence,fact):
    fact=dict(fact,elapsed_us=value['measurement']['elapsed_us'])
    identity=g35_hash_v01(dict(source=value,occurrence=occurrence))
    stamp=int(value['measurement']['finished_ns'])//10**9;start=int(value['measurement']['started_ns'])//10**9
    ref='g35:source:'+identity
    policy='g35:policy:'+value['domain']+':v01'
    operation=dict(operation='CONTROLLED_BOUNDED_SOURCE',object_id=fact['proposal'],recipient=fact['root'])
    ctx=dict(source_id=ref,local_root_scope_id=fact['root'],domain=value['domain'],pack_family_id='G35_BOUNDED_CONTROLLED',
        advisory_source_class='CONTROLLED_RUNTIME',advisory_source_revision=value['source_revision'],advice_claim_profile_id=profile,
        route_family_id='G35_PUBLIC_SOURCE',task_risk_class='BOUNDED_MOCK',validation_profile_id=profile,policy_semantics_version=policy,
        history_key_profile_id='G3_TYPED_HISTORY_KEY_V01',task_class_id='G35_SOURCE_OBSERVATION',capability_contract_version='v01',
        transaction_id=fact['transaction'],run_id=ref,episode_id=ref,scenario_id=value['case_id'])
    env=dict(pt_created_at=_utc(stamp),kt_asof=_utc(start),et_observed_at=_utc(stamp),ct_session_anchor=ref,
        ttl_seconds=3600,freshness_class='static',valid_from=_utc(start),valid_to=_utc(stamp+3600))
    source=dict(source_profile_id=profile,evidence_class='CONTROLLED_SAFE_DERIVED_SOURCE',context=ctx,
        policy=dict(source_id=policy,revision=policy,**operation),origin=dict(source_id=ref,occurrence_id=ref+':'+str(occurrence)),
        proposal=dict(source_id=fact['proposal'],origin_ref=ref,created_at=start,recommendation='PROCEED',**operation),
        expectation=dict(source_id=ref,created_at=start,expected_fp=None),
        observation=dict(source_id=ref,proposal_ref=fact['proposal'],occurrence_ref=ref+':'+str(occurrence),**operation,
            result_revision='v01',event_time=stamp,boundary_disposition='PERMITTED' if fact['task']=='COMPLETED' else 'STOPPED',
            effect_count=fact['effect_count'],result_state='PRESENT' if fact['task']=='COMPLETED' else 'MISSING',failure='NONE'),
        closure=dict(source_id=ref,sources={'adapter':value['source_revision']}),
        native=dict(capture_wall_ns=value['measurement']['finished_ns'],time_envelope=env),g35=fact)
    return source,identity


def _g35_derive_source_observations_v01(source,explicit_times):
    """One owned snapshot and full validation; no checked input escapes as a token."""
    value=json.loads(g35_bytes_v01(source))
    facts=validate_g35_source_v01(value)
    result=[]
    for ordinal,fact in enumerate(facts):
        projected,identity=_g35_occurrence_source_v01(value,value['profile'],ordinal,fact)
        observation=OutcomeObservationV01(_canonical(_observation(projected,identity,explicit_times)))
        feedback=_feedback_from_source_v01(observation,projected,identity)
        result.append((fact,observation,outcome_feedback_to_plain_data_v01(feedback)))
    return result
