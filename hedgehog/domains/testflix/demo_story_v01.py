"""Finite public Testflix story with real semantics and explicitly mock effects."""
from dataclasses import replace
import json
from pathlib import Path
import time
from hedgehog.domains.testflix import contracts_v01 as c
from hedgehog.domains.testflix import evidence_v01 as e
from hedgehog.domains.testflix import mock_world_v01 as world
from hedgehog.domains.testflix import semantic_adapter_v01 as semantic
from hedgehog.domains.testflix.live_semantic_adapter_v01 import ACTUAL_CALLS


def write_json_v01(path, value):
    with Path(path).open('x') as stream:
        json.dump(value, stream, sort_keys=True, separators=(',', ':'), ensure_ascii=True)
        stream.write('\n')


def run_story_v01(request, provider, *, directory, renewal=True, progress=None):
    if provider.mode == 'CAPTURED_REEXECUTION':
        c.require_v01(len(provider.records) - provider.position == (8 if renewal else 4),
            'captured_unused_records')
    directory = Path(directory)
    directory.mkdir(parents=True, exist_ok=True)
    handler = e.TestflixHandlerV01()
    phases = []
    started = time.monotonic()
    calls_start = len(ACTUAL_CALLS)
    world_start = len(world.CALLS)

    def stage(name, operation):
        begin = time.monotonic()
        if progress:
            progress(name, 'START', None)
        result = operation()
        elapsed = time.monotonic() - begin
        phases.append(dict(phase=name, elapsed_seconds=elapsed))
        if progress:
            progress(name, 'RETURN', elapsed)
        return result

    try:
        report = stage('P01_HANDLE', lambda: handler.handle_v01(request, provider=provider))
        roots = {name: host for name, (host, _) in handler.hosts.items()}
        c.require_v01(len(roots) == 4, 'demo_four_roots')
        purchase = stage('P01_SEAL', lambda: e.seal_report_v01(report))
        write_json_v01(directory/'purchase.json', purchase)
        semantics = [e.plain_value_v01(report['semantics'])]
        write_json_v01(directory/'purchase_semantics.json', semantics[0])
        handler.advance_clock_v01(request.now + 10)
        stage('P02_INFORMATION', lambda: handler.handle_event_v01(c.InformationRequestV01(
            request.request_id+':demo-information', request.user_id,
            report['entitlement'].entitlement_id, handler.now)))
        handler.advance_clock_v01(request.now + 20)
        stage('P03_STOP', lambda: handler.handle_event_v01(c.StopPlaybackV01(
            request.request_id+':demo-stop', request.user_id, report['session'].session_id, handler.now)))
        handler.advance_clock_v01(request.now + 30)
        fresh = stage('P03_FRESH', lambda: handler.handle_event_v01(c.PlaybackRequestV01(
            request.request_id+':demo-fresh', request.user_id, report['entitlement'].entitlement_id,
            request.device_id, request.content_id, handler.now, 3600, 720)))
        if renewal:
            expiry = report['entitlement'].candidate.valid_to
            handler.advance_clock_v01(expiry + 1)
            stage('P05_EXPIRED_STOP', lambda: handler.handle_event_v01(c.StopPlaybackV01(
                request.request_id+':demo-expiry-stop', request.user_id, fresh['session'].session_id, handler.now)))
            stage('P06_DEVICE_GRANT', lambda: handler.grant_device_v01(c.DeviceGrantRequestV01(
                request.request_id+':demo-device-grant', request.user_id, request.device_id,
                request.content_id, handler.now, handler.now+86400, 1080)))
            quote = c.ProviderQuoteV01(replace(report['semantics']['selected_plan'], price_minor=700),
                request.merchant_id, request.currency, handler.now, handler.now+3600, None)
            handler.observe_quote_v01(quote)
            renewed = stage('P06_RENEW', lambda: handler.renew_v01(c.RenewalIntentV01(
                request.request_id+':demo-explicit-700', request.user_id, report['entitlement'].entitlement_id,
                quote.quote_id, request.order_id+':demo-next-period', handler.now, 700, True), provider=provider))
            semantics.append(e.plain_value_v01(renewed['renewal']['semantics']))
            write_json_v01(directory/'renewal_semantics.json', semantics[-1])
            handler.advance_clock_v01(handler.now+10)
            stage('RENEWED_STOP', lambda: handler.handle_event_v01(c.StopPlaybackV01(
                request.request_id+':demo-renewed-stop', request.user_id, renewed['session'].session_id, handler.now)))
            stage('RENEWED_FRESH', lambda: handler.handle_event_v01(c.PlaybackRequestV01(
                request.request_id+':demo-renewed-fresh', request.user_id,
                renewed['renewal']['entitlement'].entitlement_id, request.device_id,
                request.content_id, handler.now, 60, 720)))
        c.require_v01({name: host for name, (host, _) in handler.hosts.items()} == roots,
            'demo_same_four_hosts')
        if provider.mode == 'CAPTURED_REEXECUTION':
            provider.assert_exhausted_v01()
        history = stage('HISTORY_SEAL', lambda: e.seal_history_v01(handler.history_v01()))
        write_json_v01(directory/'history.json', history)
        before = (len(world.CALLS), len(semantic.PROVIDER_CALLS), len(ACTUAL_CALLS))
        replay = stage('OFFLINE_REPLAY', lambda: e.replay_history_v01(history,
            expected_manifest_hash=history['manifest_hash']))
        c.require_v01(before == (len(world.CALLS), len(semantic.PROVIDER_CALLS), len(ACTUAL_CALLS)),
            'demo_replay_new_calls')
        write_json_v01(directory/'replay.json', replay)
        write_json_v01(directory/'semantic_records.json', dict(
            profile='testflix.semantic_records.v01', mode=provider.mode,
            records=[record for value in semantics for record in value['contributions']]))
        payment_ids = {value['payment']['execution'].invocation.invocation_id
            for value in handler.reports.values()}
        payment_count = sum(kind == 'EXECUTOR' and name in payment_ids
            for kind, name, _ in world.CALLS[world_start:])
        c.require_v01(payment_count == (2 if renewal else 1), 'demo_payment_count')
        result = dict(mode=provider.mode, model_calls=len(ACTUAL_CALLS)-calls_start,
            semantic_invocations=4*len(semantics), mock_payments=payment_count,
            mock_executor_calls=sum(kind == 'EXECUTOR' for kind, _, _ in world.CALLS[world_start:]),
            real_adapter_calls=0, clock='LOCAL_CONTROLLED_TRUSTED_SOURCE_NOT_WALL_CLOCK_ATTESTATION',
            roots=sorted(roots), same_four_hosts=True, elapsed_seconds=time.monotonic()-started,
            phases=phases, manifest_hash=history['manifest_hash'], selected_plan=report['semantics']['selected_plan'].plan_id,
            captured_reexecution='FRESH_HOSTS_AND_MOCK_EXECUTION' if provider.mode=='CAPTURED_REEXECUTION' else None,
            p04='SEPARATE_CONTROLLED_BANK_E_EVIDENCE_NOT_REEXECUTED_BY_THIS_STORY')
        write_json_v01(directory/'result.json', result)
        return result
    finally:
        handler.memory_directory.cleanup()
