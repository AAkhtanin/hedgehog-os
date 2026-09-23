"""Bounded pure reference values. Content identities are not authentication."""
from __future__ import annotations

from dataclasses import dataclass
import hashlib
import json
import re

from hedgehog.kernel.integrity_replay_v01 import canonical_json_bytes_v01

G4_REFERENCE_SCOPE_V01 = "G4_REFERENCE_SCOPE_V01"
G4_REFERENCE_NUMERIC_V01 = "G4_REFERENCE_NUMERIC_V01"
Q = 1_000_000_000
W = 1_000_000_000_000
TAU = 250_000_000
MAX_INPUT_BYTES = 262_144
MAX_REPORT_BYTES = 1_048_576
NUMERIC_PROFILE = (Q, W, TAU, 1, 1, 0)


def require(condition, reason):
    if not condition:
        raise ValueError("g4_reference:" + reason)


def digest(value):
    return hashlib.sha256(canonical_json_bytes_v01(value)).hexdigest()


def identity(kind, value):
    return "g4_reference:" + kind + ":" + digest(value)


def _obj(**properties):
    return {"type": "object", "additionalProperties": False,
            "required": list(properties), "properties": properties}


def _arr(item, low=0, high=256, order=None):
    result = {"type": "array", "items": item, "minItems": low, "maxItems": high}
    if order is not None:
        result["x-set-key"] = order
        result["uniqueItems"] = True
    return result


def _int(low, high):
    return {"type": "integer", "minimum": low, "maximum": high}


def _enum(*values):
    return {"enum": list(values)}


def _ref(name):
    return {"$ref": "#/$defs/" + name}


def _nullable(shape):
    return {"anyOf": [{"type": "null"}, shape]}


ID = {"type": "string", "pattern": r"^g4_reference:[A-Za-z0-9_.:-]{1,144}$", "maxLength": 157}
HASH = {"type": "string", "pattern": "^[0-9a-f]{64}$", "maxLength": 64}
TEXT = {"type": "string", "minLength": 1, "maxLength": 256, "pattern": r"^[\x20-\x7e]+$"}
BOOL = {"type": "boolean"}
IDS = _arr(ID, order="$")
FP = _int(-4 * Q, Q)
UFP = _int(0, Q)
UNITS = _int(0, 4096)
PROFILE = _enum(G4_REFERENCE_NUMERIC_V01)
NUMERIC_HASH = digest(list(NUMERIC_PROFILE))
UTILITY_HASH = digest({"round": "one_final_RHE", "penalties": ["risk", "latency", "coordination"], "alpha": 1})

_DEFS = {
    "context": _obj(
        profile=PROFILE, scope=_enum(G4_REFERENCE_SCOPE_V01), schema=_enum("g4_reference:v01"),
        evaluation_id=ID, domain_id=ID, owner_root_id=ID, task_id=ID,
        transaction_id=ID, intent_ref=ID, bsep_ref=ID,
        participants=_arr(ID, 2, 8, "$"), evaluation_time=_int(0, 253402300799),
        time_envelope_ref=ID, source_snapshot_ref=ID, source_snapshot_hash=HASH,
        candidate_set_ref=ID, candidate_set_hash=HASH, policy_ref=ID, policy_hash=HASH,
        utility_profile_ref=_enum("g4_reference:utility:v01"), utility_profile_hash=_enum(UTILITY_HASH),
        numeric_profile_ref=_enum("g4_reference:numeric:v01"), numeric_profile_hash=_enum(NUMERIC_HASH),
        dependencies=IDS, catalogue_revision=ID,
        origin=_enum("NUMERICAL_REFERENCE_NOT_RUNTIME"), dispositions=_arr(
            _obj(id=ID, state=_enum("KNOWN", "UNKNOWN", "MISSING"), source_ref=ID), 1, 32, "id")),
    "predicate": _obj(id=ID, state=_enum("TRUE", "FALSE", "UNKNOWN"), evidence_ref=ID),
    "term": _obj(id=ID, feature_fp=_int(-Q, Q), weight_fp=UFP, source_ref=ID, interpretation=TEXT),
    "penalties": _obj(risk=UFP, latency=UFP, coordination=UFP),
    "utility": _obj(root_id=ID, issuer_ref=ID, role_ref=ID, candidate_id=ID, source_ref=ID,
        profile=PROFILE, version=_enum(1), unit=_enum("FIXED_POINT_Q"),
        validity=_enum("CURRENT", "UNKNOWN", "MISSING", "EXPIRED"),
        uncertainty=_enum("DISCLOSED", "UNKNOWN"),
        terms=_arr(_ref("term"), 0, 8), penalties=_ref("penalties")),
    "disagreement": _obj(root_id=ID, source_ref=ID, validity=_enum("CURRENT", "UNKNOWN", "MISSING"), value=_nullable(FP)),
    "candidate": _obj(id=ID, source_ref=ID, source_hash=HASH, participants=_arr(ID, 2, 8, "$"),
        feature_refs=IDS, required_roots=_arr(ID, 1, 8, "$"), hard=_arr(_ref("predicate"), 1, 16, "id"),
        policy_ref=ID, time_envelope_ref=ID, capability_ref=ID, no_deal_ref=ID,
        utilities=_arr(_ref("utility"), 0, 8, "root_id")),
    "strategy_input": _obj(context=_ref("context"), candidates=_arr(_ref("candidate"), 1, 32, "id"),
        disagreements=_arr(_ref("disagreement"), 2, 8, "root_id")),
    "feature": _obj(value=UFP, source_ref=ID, normalization=_enum("FIXED_Q_0_1"), interpretation=TEXT),
    "prior": _obj(value=_int(-Q, Q), source_ref=ID,
        disposition=_enum("USABLE", "ABSENT", "EXPIRED", "NONMATCHING", "TAMPERED", "UNVERIFIED"),
        normalization=_enum("FIXED_Q_SIGNED"), interpretation=TEXT),
    "branch": _obj(id=ID, material_ref=ID, catalogue_revision=ID,
        hard=_arr(_ref("predicate"), 1, 16, "id"), eligible=_enum("TRUE", "FALSE", "UNKNOWN"),
        available=_enum("TRUE", "FALSE", "UNKNOWN"), lower=UNITS, upper=UNITS,
        relevance=_ref("feature"), lineage=_ref("feature"), uncertainty=_ref("feature"),
        cost=_ref("feature"), prior=_ref("prior")),
    "pressure_input": _obj(context=_ref("context"), branches=_arr(_ref("branch"), 1, 16, "id")),
    "mandatory": _obj(id=ID, count=_int(1, 4096), branch_ref=ID, material_ref=ID, catalogue_revision=ID),
    "budget": _obj(context=_ref("context"), id=ID, original_policy_ref=ID, original_policy_hash=HASH,
        total=UNITS, spent=UNITS, spending_snapshot_ref=ID, spending_snapshot_hash=HASH,
        host_revision=_int(0, 2**63-1), mandatory=_arr(_ref("mandatory"), 0, 32, "id"),
        pressure_inputs=_ref("pressure_input")),
    "exclusion": _obj(id=ID, reasons=IDS),
    "contribution": _obj(id=ID, source_ref=ID, numerator=_int(-Q*Q, Q*Q), interpretation=TEXT),
    "utility_trace": _obj(candidate_id=ID, root_id=ID, source_ref=ID,
        terms=_arr(_ref("contribution"), 1, 8), weighted=_int(-Q, Q),
        penalties=_ref("penalties"), utility=FP, disagreement=_nullable(FP),
        gain=_nullable(_int(-5*Q, 5*Q)), factor=_nullable(_int(1, 5*Q)), epsilon_used=BOOL),
    "comparison": _obj(candidate_id=ID, root_id=ID, utility=FP, disagreement=FP),
    "witness": _obj(id=ID, dominator=ID, differences=_arr(_obj(root_id=ID, delta=_int(0,5*Q)), 2, 8, "root_id")),
    "score": _obj(id=ID, product={"type":"string", "pattern":"^(0|[1-9][0-9]{0,79})$", "maxLength":80}),
    "deferred": _obj(**{k:_obj(status=_enum("NOT_IMPLEMENTED"), disposition=_enum("DEFERRED_AFTER_GATE6_PUBLICATION"))
        for k in ("regret", "stability", "robustness", "CVaR", "sensitivity")}),
    "strategy_report": _obj(context=_ref("context"), input_id=ID, status=_enum("RECOMMENDATION", "NEEDS_MORE_EVIDENCE",
        "NO_DEAL_NO_FEASIBLE", "NO_DEAL_BELOW_DISAGREEMENT", "NO_DEAL_ALL_ZERO_GAIN"),
        recommendation=_nullable(ID), feasible=IDS, ir=IDS, pareto=IDS,
        exclusions=_arr(_ref("exclusion"), 0, 32, "id"), missing_refs=_arr(ID,0,544,"$"),
        utilities=_arr(_ref("utility_trace")), failed_comparisons=_arr(_ref("comparison")),
        witnesses=_arr(_ref("witness"), 0, 32, "id"), scores=_arr(_ref("score"), 0, 32, "id"),
        ranking=_arr(ID,0,32), tie_rule=_enum("DESCENDING_PRODUCT_THEN_STABLE_ID"), weak_ir=BOOL,
        root_review_required=_enum(True), creates_permission=_enum(False), requests_effect=_enum(False),
        deferred=_ref("deferred")),
    "pressure_trace": _obj(id=ID, lower=UNITS, upper=UNITS, z_fp=_int(-500000000,875000000),
        contributions=_arr(_obj(name=_enum("relevance", "lineage", "uncertainty", "cost", "prior"),
            numerator=_int(-2*Q, 4*Q), source_ref=ID, normalization=TEXT, interpretation=TEXT), 5, 5),
        numerator=_int(-4*Q, 7*Q), denominator=_enum(8)),
    "pressure_report": _obj(context=_ref("context"), input_id=ID, inputs=_ref("pressure_input"),
        status=_enum("READY", "NEEDS_MORE_EVIDENCE"), missing_refs=_arr(ID,0,304,"$"),
        exclusions=_arr(_ref("exclusion"), 0, 16, "id"), survivors=_arr(_ref("pressure_trace"),0,16,"id"),
        authority=_enum("NON_AUTHORITY")),
    "rational": _obj(numerator=_int(0,4096*16*W), denominator=_int(1,16*W)),
    "allocation_row": _obj(id=ID, lower=UNITS, upper=UNITS, z_fp=_int(-500000000,875000000),
        weight=_int(1,W), extra=_ref("rational"), floor=UNITS, remainder=_ref("rational"), allocation=UNITS),
    "round": _obj(remaining=UNITS, active=IDS, saturated=IDS,
        tentative=_arr(_obj(id=ID, value=_ref("rational")),0,16,"id")),
    "allocation_report": _obj(context=_ref("context"), input_id=ID, budget_id=ID, budget=_ref("budget"),
        pressure_id=ID, status=_enum("ALLOCATED", "NEEDS_MORE_EVIDENCE", "BUDGET_INSUFFICIENT", "INFEASIBLE_MINIMA"),
        mandatory_units=_int(0,32*4096), available=_int(-33*4096,4096),
        target=UNITS, unallocated=_nullable(_int(-33*4096,4096)),
        exclusions=_arr(_ref("exclusion"),0,16,"id"), missing_refs=_arr(ID,0,304,"$"),
        rows=_arr(_ref("allocation_row"),0,16,"id"), rounds=_arr(_ref("round"),0,16),
        remainder_order=_arr(ID,0,16), remainder_awards=_arr(ID,0,16),
        unit=_enum("ONE_NATIVE_WORK_DISPATCH_UNIT"), authority=_enum("NON_AUTHORITY"))
}

# Native descriptors bind original objects separately from projection digests.
# Their origin label is descriptive: only the G42 current consumer checks live
# sources. Legacy numerical values keep their exact absent-field bytes.
_reference_context = _DEFS["context"]
_native_context = json.loads(json.dumps(_reference_context))
_native_context["properties"]["origin"] = _enum("NATIVE_SOURCE_BOUND_G42_V01")
_native_context["properties"]["native_binding"] = _obj(
    profile=_enum("G42_ORIGINAL_AND_PROJECTION_BINDING_V01"), basis_sha256=HASH,
    original_snapshot_sha256=HASH, original_policy_sha256=HASH,
    original_usage_sha256=HASH, original_envelope_sha256=HASH, id_mapping_sha256=HASH)
_native_context["required"].append("native_binding")
_DEFS["context"] = {"anyOf": [_reference_context, _native_context]}
_DEFS["mandatory"] = {"anyOf": [_DEFS["mandatory"], _obj(
    id=ID, count=_int(1,4096), kind=_enum("CURRENT_CHECK", "FINAL_CONSUMER"),
    definition_ref=ID, material_ref=ID, material_sha256=HASH, source_ref=ID,
    catalogue_revision=ID)]}


def reference_schema_v01():
    """Return an isolated local schema; no URI resolution or native artifacts."""
    return json.loads(json.dumps({"$schema":"https://json-schema.org/draft/2020-12/schema",
        "$id":"urn:g4_reference:v01", "$defs":_DEFS,
        "oneOf":[_obj(kind=_enum(k), value=_ref(k)) for k in (
            "context", "strategy_input", "strategy_report", "pressure_input", "pressure_report", "budget", "allocation_report")]}))


def _bounded(value, limit, *, container_limit=512):
    nodes = 0
    size = 0
    active = set()
    def walk(v, depth):
        nonlocal nodes, size
        nodes += 1
        require(depth <= 24 and nodes <= 65536, "structure_limit")
        t = type(v)
        require(t in (dict, list, str, int, bool, type(None)), "json_type")
        if t in (dict, list):
            require(id(v) not in active and len(v) <= container_limit, "container_limit")
            active.add(id(v))
            for k, x in (v.items() if t is dict else enumerate(v)):
                if t is dict:
                    require(type(k) is str and len(k) <= 64, "key")
                    size += len(k)
                walk(x, depth + 1)
            active.remove(id(v))
        elif t is str:
            require(len(v) <= 256 and v.isascii(), "string_limit")
            size += len(v)
        elif t is int:
            require(v.bit_length() <= 128, "integer_limit")
            size += 40
        require(size <= limit, "input_size")
    walk(value, 0)
    require(len(canonical_json_bytes_v01(value)) <= limit, "input_size")


def _shape(value, rule):
    if "$ref" in rule:
        return _shape(value, _DEFS[rule["$ref"].split("/")[-1]])
    if "anyOf" in rule:
        for option in rule["anyOf"]:
            try:
                return _shape(value, option)
            except ValueError:
                pass
        require(False, "nullable_shape")
    if "enum" in rule:
        require(any(type(value) is type(x) and value == x for x in rule["enum"]), "enum")
        return value
    t = rule["type"]
    require(type(value) is {"object":dict,"array":list,"string":str,"integer":int,"boolean":bool,"null":type(None)}[t], "shape_type")
    if t == "object":
        require(set(value) == set(rule["properties"]), "closed_keys")
        return {k:_shape(value[k], r) for k,r in rule["properties"].items()}
    if t == "array":
        require(rule["minItems"] <= len(value) <= rule["maxItems"], "array_length")
        result = [_shape(v, rule["items"]) for v in value]
        if "x-set-key" in rule:
            key = rule["x-set-key"]
            keys = [v if key == "$" else v[key] for v in result]
            require(len(keys) == len(set(keys)), "duplicate_id")
            result.sort(key=lambda v:v if key == "$" else v[key])
        return result
    if t == "integer":
        require(rule["minimum"] <= value <= rule["maximum"], "integer_range")
    if t == "string":
        require(rule.get("minLength", 0) <= len(value) <= rule["maxLength"] and re.fullmatch(rule["pattern"], value), "string_shape")
    return value


def _parse(raw, limit):
    require(type(raw) is bytes and len(raw) <= limit, "raw_size")
    depth = 0
    quoted = escaped = False
    for c in raw:
        if quoted:
            if escaped: escaped = False
            elif c == 92: escaped = True
            elif c == 34: quoted = False
        elif c == 34: quoted = True
        elif c in (91,123):
            depth += 1
            require(depth <= 24, "raw_depth")
        elif c in (93,125): depth -= 1
    def pairs(items):
        require(len(dict(items)) == len(items), "duplicate_key")
        return dict(items)
    def no_number(_):
        raise ValueError("g4_reference:non_integer")
    def integer(s):
        require(len(s) <= 40, "integer_limit")
        return int(s)
    try:
        return json.loads(raw, object_pairs_hook=pairs, parse_int=integer,
                          parse_float=no_number, parse_constant=no_number)
    except (UnicodeError, RecursionError, json.JSONDecodeError):
        raise ValueError("g4_reference:invalid_json") from None


@dataclass(frozen=True, slots=True, init=False)
class ReferenceValueV01:
    """Canonical bytes own deep immutable content; plain() always returns a copy."""
    kind: str
    canonical: bytes

    def __init__(self, kind, value):
        require(type(kind) is str and kind in _DEFS, "kind")
        limit = MAX_REPORT_BYTES if kind.endswith("report") else MAX_INPUT_BYTES
        if type(value) is ReferenceValueV01:
            require(value.kind == kind, "kind_pair")
            value = value.plain()
        elif type(value) is bytes:
            value = _parse(value, limit)
        # 32*16 hard references plus 32 context dispositions in strategy output.
        _bounded(value, limit, container_limit=544 if kind.endswith("report") else 512)
        normalized = _shape(value, _DEFS[kind])
        object.__setattr__(self, "kind", kind)
        object.__setattr__(self, "canonical", canonical_json_bytes_v01(normalized))

    @property
    def identity(self):
        return "g4_reference:" + self.kind + ":" + hashlib.sha256(self.canonical).hexdigest()

    def plain(self):
        return json.loads(self.canonical)


def checked(kind, value):
    return ReferenceValueV01(kind, value).plain()


def bind_context(actual, expected):
    a, b = checked("context", actual), checked("context", expected)
    require(a == b, "independent_context_mismatch")
    require(a["owner_root_id"] in a["participants"], "owner_participant")
    return a


def validate_supplied(kind, supplied, expected):
    actual = ReferenceValueV01(kind, supplied)
    require(actual.canonical == expected.canonical, "supplied_report_mismatch")
    return ReferenceValueV01(kind, expected)
