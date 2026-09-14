"""Exact canonical construction and invocation-local profile factoring."""
from copy import deepcopy
from dataclasses import replace
import sys

import pytest

from hedgehog import action_commit_packet_v02 as a
from hedgehog.kernel import transition_registry_v01 as t
from hedgehog.kernel.integrity_replay_v01 import canonical_json_bytes_v01
from tests.test_action_commit_packet_lifecycle_g2_a_v01 import _g2a2a_event


def test_canonical_material_narrow_encoder_matches_general_bytes():
    for value in (a.ABSENT_V01, (), True, False, 0, -1, a.INT64_MIN_V01,
                  a.INT64_MAX_V01, '', '\u00e9', '\U0001f4f7', '"\\\n\t',
                  (a.ABSENT_V01, (1, True, 'photo'), ('nested', ()))):
        material = (('value', value),)
        before = canonical_json_bytes_v01(material)
        assert a.canonical_material_bytes_v01(material) == before
        assert a.canonical_material_bytes_v01(deepcopy(material, {id(a.ABSENT_V01): a.ABSENT_V01})) == before
    assert a.canonical_material_bytes_v01((('value', True),)) != a.canonical_material_bytes_v01((('value', 1),))


@pytest.mark.parametrize('value', [[], {}, None, 1.0, b'bytes', '\ud800', '\x00',
                                  'e\u0301', a.INT64_MAX_V01 + 1, (('x', []),)])
def test_narrow_encoder_keeps_invalid_mutable_and_unicode_refusals(value):
    with pytest.raises(ValueError, match='canonical_material_value_invalid'):
        a.canonical_material_bytes_v01((('value', value),))
    assert a.canonical_material_bytes_v01((('value', 'valid'),)) == b'[["value","valid"]]'


def test_canonical_templates_are_values_not_shared_caller_records():
    def immutable(value):
        assert type(value) in (str, int, bool, bytes, tuple)
        if type(value) is tuple:
            for item in value:
                immutable(item)
    immutable(t._default_reference_v01())
    immutable(t._action_profile_reference_v01())
    first = t.build_action_packet_transition_registry_profile_v01()
    second = t.build_action_packet_transition_registry_profile_v01()
    assert first == second and first is not second
    assert all(a is not b for a, b in zip(first.ordered_transition_rules, second.ordered_transition_rules))
    original = deepcopy(first)
    object.__setattr__(first.ordered_transition_rules[0], 'terminal_target', 0)
    assert t.validate_action_packet_transition_registry_profile_v01(first)
    assert t.validate_action_packet_transition_registry_profile_v01(second) == ()
    assert t.validate_action_packet_transition_registry_profile_v01(original) == ()
    exported = t.action_packet_transition_registry_to_plain_dict_v01(second)
    exported['ordered_transition_rules'].clear()
    assert len(t.action_packet_transition_registry_to_plain_dict_v01(second)['ordered_transition_rules']) == 26


def test_public_event_checks_one_profile_and_every_binding_without_stale_pass():
    profile = t.build_action_packet_transition_registry_profile_v01()
    event = _g2a2a_event('g2a_t01_activate_root_authorization')
    codes = {t.validate_action_packet_transition_registry_profile_v01.__code__: 'profile',
             a._validate_transition_evidence_binding_checked_v01.__code__: 'binding'}
    counts = dict(profile=0, binding=0)
    tool = 4
    sys.monitoring.use_tool_id(tool, 'ews-profile-count')
    def enter(code, offset):
        counts[codes[code]] += 1
    sys.monitoring.register_callback(tool, sys.monitoring.events.PY_START, enter)
    try:
        for code in codes:
            sys.monitoring.set_local_events(tool, code, sys.monitoring.events.PY_START)
        assert a.validate_action_packet_transition_event_v01(event, action_packet_transition_registry_profile=profile) == (True, ())
    finally:
        for code in codes:
            sys.monitoring.set_local_events(tool, code, 0)
        sys.monitoring.free_tool_id(tool)
    assert counts == dict(profile=1, binding=len(event.transition_evidence_bindings))
    for field, value in (('evaluation_time', True), ('transition_registry_id', 'wrong'),
                         ('transition_evidence_bindings', tuple(reversed(event.transition_evidence_bindings)))):
        assert not a.validate_action_packet_transition_event_v01(replace(event, **{field: value}), action_packet_transition_registry_profile=profile)[0]
    binding = event.transition_evidence_bindings[0]
    changed = replace(event, transition_evidence_bindings=(replace(binding, evidence_ref='changed'),) + event.transition_evidence_bindings[1:])
    assert not a.validate_action_packet_transition_event_v01(changed, action_packet_transition_registry_profile=profile)[0]
    assert a.validate_action_packet_transition_event_v01(deepcopy(event), action_packet_transition_registry_profile=deepcopy(profile)) == (True, ())
    forged_profile = replace(profile, ordered_transition_rules=profile.ordered_transition_rules[:-1])
    assert not a.validate_action_packet_transition_event_v01(event, action_packet_transition_registry_profile=forged_profile)[0]
    assert a.validate_action_packet_transition_event_v01(event, action_packet_transition_registry_profile=profile) == (True, ())
