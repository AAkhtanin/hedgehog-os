"""Simulated-clock temporal boundaries with real public Root/Host builders.

These cheap tests stage read-side media fields and stop before common E. They
never manufacture D/E returns or claim physical elapsed-time browser evidence.
"""
from copy import deepcopy
from dataclasses import asdict
import os
from pathlib import Path
from types import SimpleNamespace

import pytest

from demo.ephemeral_workspace_fixtures_v01 import generate
from hedgehog import action_commit_packet_v02 as action
from hedgehog import work_execution_host_v01 as hosts
from hedgehog.domains.ephemeral_workspace import contracts_v01 as c
from hedgehog.domains.ephemeral_workspace import kernel_adapter_v01 as kernel
from hedgehog.domains.ephemeral_workspace import media_continuation_v01 as continuation
from hedgehog.domains.ephemeral_workspace import session_runtime_v01 as runtime
from hedgehog.domains.ephemeral_workspace.local_services_v01 import Service
from hedgehog.domains.ephemeral_workspace.evidence_v01 import media_value


class StopBeforeE(ValueError):
    """Test-only boundary; not a recomputation result."""


def record(name, value):
    directory = os.environ.get('EWS_TEMPORAL_EVIDENCE')
    if directory:
        path = Path(directory) / (name + '.json')
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_bytes(c.canonical(dict(
            scope='SIMULATED_CLOCK_STAGED_MEDIA_FIELDS_REAL_ROOT_HOST_NO_D_OR_E',
            **value)) + b'\n')


@pytest.fixture
def pending_workspace(tmp_path):
    expected = os.environ.get('EWS_EXPECTED_CANDIDATE')
    if expected:
        assert Path(runtime.__file__).resolve().is_relative_to(Path(expected))
    session = runtime.Workspace(tmp_path / 'workspace', generate(tmp_path / 'photos', 1))
    try:
        session.command('OPEN')
        # Staged read-side fixture only. The photo Work and Root/Host are real;
        # no media D or E result is constructed or substituted by this fixture.
        session.contract = dict(session.contract, media=dict(audio=True))
        session.allowed += ('PLAY', 'PAUSE', 'SEEK', 'REVIEW_MEDIA')
        audio = Service('audio', session.id, session.deadline, session.directory / 'logs')
        session.services.append(audio)
        session.resource_plan['audio'] = audio.nonce
        session.media_review = dict(
            output=dict(audio=True, audio_policy='SILENT_CONTINUE'),
            results=(SimpleNamespace(result=SimpleNamespace(result_id='ews:test:staged_read_side_media')),))
        session.media_state.update(audio='AVAILABLE', status='READY')
        authorization, inputs, observation, review = kernel.prepare_command(
            session, dict(op='SEEK', value=7), dict(test_scoped_pending=True))
        clock = session.source.sample(observation)
        packet, _ = hosts.install_current_action_v01(
            session.host, **authorization, inputs=inputs,
            admission_id=session.catalogue[2].admission_id,
            expected_revision=session.host.revision,
            evaluation_time=clock.evaluation_time,
            evaluation_time_source=clock.evaluation_time_source,
            evaluation_context_id=clock.evaluation_context_id)
        session.media_pending = dict(authorization=authorization, inputs=inputs,
            observation=observation, review=review, packet_id=packet,
            fact=session.last_prepared_fact, registry=session.host.registry)
        session.media_baseline = dict(scope='STAGED_NOT_A_D_BASELINE', photo_work=session.photo_work())
        yield session
    finally:
        cleanup = session.close('TEMPORAL_TEST_RESOURCE_FINALIZER')
        assert cleanup['status'] == 'CLOSED_SUCCESS'
        assert all(service.process.poll() is not None for service in session.services)


def simulated_clock(monkeypatch, session, timestamp):
    # Replace only each domain module's clock reference. Service/process clocks
    # keep real time; no clock replacement escapes this deterministic test.
    clock = {'utc': timestamp}
    local = SimpleNamespace(monotonic=lambda: session.source.started + clock['utc'] - session.source.epoch + 0.25)
    monkeypatch.setattr(runtime, 'time', local)
    monkeypatch.setattr(kernel, 'time', local)
    return clock


def stop_before_native_e(monkeypatch, calls):
    def stop(session, capture, invalidation, observed_time):
        calls.append((capture, invalidation, observed_time))
        raise StopBeforeE('test_stopped_during_pre_E_preparation')
    # Exercise the actual recompute entry's preparation/error boundary while
    # avoiding its expensive native E invocation and any synthetic E success.
    monkeypatch.setattr(continuation, 'delta_arguments', stop)


@pytest.mark.parametrize('relative_to_expiry', [-1, 0, 1])
def test_actual_loss_observation_has_new_interval_and_immutable_old_authority(
        pending_workspace, monkeypatch, relative_to_expiry):
    session = pending_workspace
    pending = session.media_pending
    original = c.canonical(media_value(pending))
    baseline = deepcopy(session.media_baseline)
    photo = session.photo_work()
    pixels = session.photo_frame(session.preview['frame_ref'])
    prior = pending['observation']
    old_bound = pending['authorization']['root_bound']
    now = prior.valid_to_utc + relative_to_expiry
    simulated_clock(monkeypatch, session, now)
    calls = []
    stop_before_native_e(monkeypatch, calls)
    effects = deepcopy(session.executed)
    history = deepcopy(session.history)
    with pytest.raises(StopBeforeE, match='test_stopped_during_pre_E_preparation'):
        session.withdraw_audio()
    assert len(calls) == 1
    capture, invalidation, observed_time = calls[0]
    observation, = capture.observations
    assert observed_time == now == observation.observed_at_utc == observation.valid_from_utc
    assert observation.valid_to_utc == min(now + 120, session.expires)
    assert observation.valid_from_utc <= capture.evaluation_time < observation.valid_to_utc
    assert observation.dependency_id == prior.dependency_id
    assert observation.evidence_ref == prior.evidence_ref
    assert observation.freshness_policy_id == prior.freshness_policy_id
    assert observation.source_provenance_refs == prior.source_provenance_refs
    assert observation.time_envelope_id != prior.time_envelope_id
    assert observation.observed_content_sha256 == c.digest(dict(pending['fact'], media=session.loss_dependency))
    assert observation.observed_content_sha256 != prior.observed_content_sha256
    assert action.validate_action_dependency_time_envelope_binding_v01(
        observation.time_envelope_id, dependency_id=observation.dependency_id,
        evidence_ref=observation.evidence_ref, content_sha256=observation.observed_content_sha256,
        freshness_policy_id=observation.freshness_policy_id,
        source_provenance_refs=observation.source_provenance_refs,
        valid_from_utc=observation.valid_from_utc, valid_to_utc=observation.valid_to_utc) == (True, ())
    assert capture.root_bound_packet == old_bound
    assert capture.root_bound_packet.canonical_projection.temporal_authority == old_bound.canonical_projection.temporal_authority
    assert hosts.validate_retained_action_source_capture_v01(session.host, capture, require_current=True)
    assert invalidation.packet_id == pending['packet_id']
    assert invalidation.dependency_id == prior.dependency_id
    assert invalidation.time_envelope_id == prior.time_envelope_id
    assert invalidation.evidence_sha256 == observation.observed_content_sha256
    assert c.canonical(media_value(session.media_pending)) == original
    assert session.media_baseline == baseline
    assert session.photo_work() == photo
    assert session.photo_frame(session.preview['frame_ref']) == pixels
    assert session.executed == effects and session.history == history
    assert session.audio_loss['stale_packet_refusal'] == 'host_current_action_not_executable'
    assert session.media_delta is None and session.producer_counts['delta'] == 0
    assert session.media_state['status'] == 'AUDIO_UNAVAILABLE_PAUSED'
    assert session.media_state['reason'] == 'StopBeforeE:test_stopped_during_pre_E_preparation'
    assert session.state()['owner_cleanup_available']
    record('boundary_' + str(relative_to_expiry).replace('-', 'minus'), dict(
        original_observation=asdict(prior), changed_observation=asdict(observation),
        temporal_authority=asdict(old_bound.canonical_projection.temporal_authority),
        actual_test_error=session.audio_loss['continuation_error'], invalidation=asdict(invalidation),
        capture=dict(source_revision=capture.source_revision, host_revision=capture.host_revision,
                     ordinal=capture.capture_ordinal, evaluation_time=capture.evaluation_time),
        relative_to_original_expiry=relative_to_expiry, effect_count_before=len(effects),
        effect_count_after=len(session.executed), source_offset=session.source.offset,
        photo_sha256=c.digest(pixels)))


@pytest.mark.parametrize('relative_to_expiry', [0, 1])
def test_original_expired_packet_refusal_does_not_depend_on_new_observation(
        pending_workspace, monkeypatch, relative_to_expiry):
    session = pending_workspace
    pending = session.media_pending
    original = c.canonical(media_value(pending))
    prior = pending['observation']
    simulated_clock(monkeypatch, session, prior.valid_to_utc + relative_to_expiry)
    before = deepcopy(session.executed)
    clock = session.source.sample()  # No loss and no changed observation.
    assert prior in clock.observations
    with pytest.raises(ValueError, match='^host_current_action_not_executable$'):
        hosts.dispatch_current_action_v01(session.host, packet_id=pending['packet_id'], task_id=session.id,
            expected_revision=session.host.revision, evaluation_time=clock.evaluation_time,
            evaluation_time_source=clock.evaluation_time_source,
            evaluation_context_id=clock.evaluation_context_id)
    assert session.executed == before
    assert c.canonical(media_value(session.media_pending)) == original
    assert session.audio_loss is None and session.media_delta is None
    assert not hasattr(session, 'audio_capture')
    record('independent_refusal_' + str(relative_to_expiry), dict(
        observation=asdict(prior), packet_id=pending['packet_id'],
        evaluation_time=clock.evaluation_time, effect_count_before=len(before),
        effect_count_after=len(session.executed), no_changed_observation=True))


def test_new_observation_interval_is_capped_by_workspace_expiry(pending_workspace, monkeypatch):
    session = pending_workspace
    now = session.media_pending['observation'].valid_to_utc + 1
    session.expires = now + 30  # Test-only narrowing; old packet remains unchanged.
    simulated_clock(monkeypatch, session, now)
    calls = []
    stop_before_native_e(monkeypatch, calls)
    with pytest.raises(StopBeforeE):
        session.withdraw_audio()
    observation, = session.audio_capture.observations
    assert observation.valid_from_utc == now
    assert observation.valid_to_utc == session.expires == now + 30
    record('session_cap', dict(observation=asdict(observation), workspace_expires=session.expires))


def test_expiry_at_acquisition_is_truthful_pre_e_failure(pending_workspace, monkeypatch):
    session = pending_workspace
    clock = simulated_clock(monkeypatch, session, session.expires - 1)
    # Keep this probe about the whole session boundary rather than its idle rule.
    session.last_activity = runtime.time.monotonic()
    audio = next(service for service in session.services if service.role == 'audio')
    close = audio.close
    def close_at_expiry():
        receipt = close()
        clock['utc'] = session.expires
        return receipt
    monkeypatch.setattr(audio, 'close', close_at_expiry)
    calls = []
    stop_before_native_e(monkeypatch, calls)
    before = deepcopy(session.executed)
    photo = session.photo_work()
    with pytest.raises(ValueError, match='^workspace_expired$'):
        session.withdraw_audio()
    assert calls == [] and not hasattr(session, 'audio_capture')
    assert session.audio_loss['continuation_error'] == dict(type='ValueError', reason='workspace_expired')
    assert session.media_state['status'] == 'AUDIO_UNAVAILABLE_PAUSED'
    assert session.media_state['audio'] == 'UNAVAILABLE'
    assert session.media_state['reason'] == 'ValueError:workspace_expired'
    assert session.media_delta is None and session.producer_counts['delta'] == 0
    assert session.executed == before and session.photo_work() == photo
    state = session.state()
    assert state['status'] == 'EXPIRED' and state['allowed'] == []
    assert state['owner_cleanup_available'] and not state['owner_approval_available']
    record('acquisition_expired', dict(error=session.audio_loss['continuation_error'], state=state))


@pytest.mark.parametrize('closed_by', ['expiry', 'revocation'])
def test_no_continuation_action_or_save_authority_when_workspace_not_current(
        pending_workspace, monkeypatch, closed_by):
    session = pending_workspace
    session.edits['asset:1']['selected'] = True
    candidate = session.save_candidate()
    session.pending = candidate
    if closed_by == 'expiry':
        simulated_clock(monkeypatch, session, session.expires)
    else:
        session.revoke()  # Real current local Root withdrawal and owned cleanup.
        assert session.withdrawal['decision'] == 'ACCEPT'
    source_before = session.source.snapshot
    effects_before = deepcopy(session.executed)
    calls = []
    stop_before_native_e(monkeypatch, calls)
    for operation in (session.withdraw_audio, lambda: session.command('PLAY'),
                      lambda: session.command('REQUEST_SAVE'), lambda: session.approve(candidate)):
        with pytest.raises(ValueError, match='workspace_(expired|not_current)'):
            operation()
    assert session.source.snapshot == source_before
    assert session.executed == effects_before and session.approvals == {}
    assert session.saved is None and session.write_outcome == 'NOT_STARTED'
    assert calls == [] and session.audio_loss is None and session.media_delta is None
    state = session.state()
    assert not state['current'] and not state['owner_approval_available']
    if closed_by == 'expiry':
        assert state['owner_cleanup_available']
    cleanup = session.close('TEMPORAL_BOUNDARY_OWNER_CLEANUP')
    assert cleanup['status'] == 'CLOSED_SUCCESS'
    assert cleanup['authority'] == 'INITIAL_RESOURCE_OWNER_CLEANUP_OBLIGATION'
    assert all(service.process.poll() is not None for service in session.services)
    assert not list((session.directory / 'output').iterdir())
    record('denied_' + closed_by, dict(state=state, cleanup=cleanup,
        effects_before=len(effects_before), effects_after=len(session.executed), sidecar_files=[]))
