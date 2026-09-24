"""Explicit operator wrapper around the existing Wedding native/transport path.

Not called by inspect/export/verify/replay/render. Authorization is an external
operator input, not a signature or substitute for current native Root review.
"""
from pathlib import Path
import time
import uuid
from . import portable_v01 as p


def launch_inputs_v01(args):
    p.require(args.allow_native, 'explicit_native_authorization_required')
    p.require(args.config is not None, 'operator_config_required')
    config_raw = p.regular(args.config); config = p.strict(config_raw)
    p.require(args.output is not None, 'operator_output_required')
    p.require(not any(x.is_symlink() for x in (args.output, *args.output.parents)), 'operator_output_symlink')
    if args.mode == 'local':
        p.require(config.get('semantic_mode') in ('CONTROLLED','CAPTURED','LIVE'), 'semantic_mode_required')
        external = config['semantic_mode'] == 'LIVE'
    else:
        external = True
        if args.mode == 'resume-provider':
            ledger_path = args.output/'provider/ledger.json'
            p.require(ledger_path.is_file(), 'existing_attempt_required')
            attempts = p.strict(p.regular(ledger_path))['attempts']
            p.require(bool(attempts), 'existing_attempt_required')
            p.require(all(r.get('task_arn') for r in attempts), 'UNKNOWN_SUBMISSION_REQUIRES_EXACT_RECONCILIATION_NO_NEW_TOKEN')
            p.require(any(r['state'] not in ('VALIDATED_AND_SAVED','REJECTED_SAMPLE_SET','TERMINAL_PROVIDER_ERROR') for r in attempts), 'completed_episode_read_only')
        else:
            p.require(not args.output.exists(), 'new_episode_directory_required')
    if external:
        p.require(args.allow_external, 'explicit_external_authorization_required')
        p.require(args.authorization is not None, 'fresh_authorization_required')
        p.require(args.authorization_sha256 is not None, 'external_authorization_pin_required')
        raw = p.regular(args.authorization)
        p.require(p.sha(raw) == args.authorization_sha256, 'authorization_pin_mismatch')
        auth = p.strict(raw)
        p.require(set(auth) == {'version','mode','config_sha256','output','expires','owner_authorized'}, 'authorization_shape')
        p.require(auth['version'] == 'WeddingOperatorAuthorizationV01' and auth['owner_authorized'] is True and auth['mode'] == args.mode,
                  'authorization_mode')
        p.require(auth['config_sha256'] == p.sha(config_raw) and Path(auth['output']) == args.output.resolve(), 'authorization_config_output')
        p.require(type(auth['expires']) is int and time.time() < auth['expires'], 'authorization_expired')
    return config


def _local(args, config):
    from . import native_contracts_v01 as c, privacy_v01 as privacy, runtime_v01 as runtime, semantic_adapter_v01 as semantics
    p.require(not args.output.exists(), 'new_output_directory_required')
    original = p.regular(Path(config['problem']))
    mode = config['semantic_mode']
    if mode == 'CONTROLLED':
        p.require(set(config) == {'semantic_mode','problem','request_ref','profile','safe_intent','responses'}, 'controlled_config_shape')
        owner = c.OwnerContextV01(original, config['request_ref'], 'GENERATE', config['profile'], config['safe_intent'])
        problem = owner.problem(); value = problem.to_plain_v01()
        policy = privacy.DisclosurePolicyV01(value['disclosure_profile_ref'], True, tuple(value['guest_ids']),
            tuple(t['table_id'] for t in value['table_records']), tuple(h['condition_id'] for h in value['hard_conditions']),
            c.source_refs(value), ((value['safe_intent_ref'],owner.approved_intent),))
        projections = [privacy.semantic_projection_v01(problem, role, policy=policy).to_plain_v01() for role in ('ORCHESTRATOR','REQUIREMENT_ARCHITECT')]
        run = runtime.execute_v01(owner, original, [c.canonical(x) for x in config['responses']], policy=policy,
                                  serialized_projections=projections, now=int(time.time()))
    else:
        i = config['intake']
        intake = semantics.LiveIntakeV01(original, original, i['request_ref'], i['safe_intent'],
            tuple(i['permitted_tasks']), tuple(i['permitted_profiles']), i['structural_disclosure'])
        p.require(set(intake.permitted_tasks) <= {'GENERATE','CLARIFY'}, 'local_standalone_generation_or_clarification_only')
        if mode == 'LIVE':
            p.require(config.get('provider_config') is not None, 'configured_gemini_missing')
            provider = semantics.GeminiProviderV01(args.output/'captures', config['provider_config'])
            router = provider.capture(intake, semantics.ROLES[0])
            parsed = semantics.validate_capture_v01(router, intake=intake, role=semantics.ROLES[0])
            architect = provider.capture(intake, semantics.ROLES[1], parsed)
            records = [router, architect]
        else:
            records = p.strict(p.regular(Path(config['captures'])))
        run = semantics.execute_live_v01(intake, records, now=int(time.time()),
                origin='LIVE_ROLE_ORIGIN' if mode == 'LIVE' else 'CAPTURED_PROVIDER_RESPONSE_REEXECUTION')
    args.output.mkdir(parents=True, exist_ok=True)
    evidence = run if isinstance(run, dict) else run.evidence
    (args.output/'local_evidence.json').write_bytes(c.canonical(evidence))
    return dict(status=evidence.get('status','ACTUAL_NATIVE_COMPLETED'), semantic_mode=mode,
                output=evidence.get('output'), evidence='local_evidence.json', qpu_calls=0)


def _hardware(args, config):
    from . import qpu_bridge_v01 as bridge, qpu_application_v01 as app, qpu_contracts_v01 as q
    from . import native_contracts_v01 as c, circuit_v02 as circuit, qpu_output_v01 as output
    p.require(set(config) == {'source','expected_sha256','scope','request_prefix'}, 'hardware_config_shape')
    source = Path(config['source']); pin = config['expected_sha256']; scope = config['scope']
    bridge.check_scope_v01(scope)
    p.verify_v01(source, pin)
    files = p.load_pinned_directory_v01(source, pin)
    old = p._json(files, 'w4/provider/ledger.json')
    p.require(scope['episode'] != p._json(files,'w4/operator_scope.json')['episode'] or args.mode == 'resume-provider', 'completed_episode_not_new_allowance')
    p.require(scope['output_prefix'] != p._json(files,'w4/operator_scope.json')['output_prefix'] or args.mode == 'resume-provider', 'completed_prefix_not_new_allowance')
    store = bridge.LedgerV01(args.output/'provider')
    def prepare(profile):
        key = 'A' if profile == q.PROFILES[0] else 'B'
        owner, material = app.preparation_material_v01(p._json(files,f'w4/basis_w3/story/{key}_intake.json'),
            p._json(files,f'w4/basis_w3/story/{key}_captures.json'), files[f'w4/basis_w1/captures/{profile}/grid.json'],
            request_ref=config['request_prefix']+profile, original_bytes=files['w4/candidate/fixtures/wedding_seating/reference_problem_v01.json'])
        run = app.prepare_v01(owner, material)
        bridge.atomic_json(args.output/'native'/profile/('prepare_'+str(time.time_ns())+'.json'),run.evidence)
        return run
    with store.locked() as ledger:
        if args.mode == 'live-qpu':
            p.require(not ledger['attempts'], 'existing_ledger_resume_only')
        else:
            p.require(all(r['approval']['scope'] == scope for r in ledger['attempts']), 'resume_scope_changed')
            p.require(all(r['task_arn'] not in {x['task_arn'] for x in old['attempts']} for r in ledger['attempts']), 'completed_W4_read_only')
        # SDK and credentials are touched only after all local launch checks.
        client, s3, principal = bridge.clients_v01(scope)
        bridge.atomic_json(args.output/'provider/identity.json',principal)
        runs = {}
        if args.mode == 'live-qpu':
            bridge.atomic_json(args.output/'provider/device.json',bridge.device_v01(client))
            for profile in q.PROFILES:
                run = prepare(profile); runs[profile] = run
                enc = q.check_numeric_v01(run.material, run.output); j,k = q.ANGLES[profile]
                program = circuit.build_sdk_program_v02(enc,4096,j,k)['program_json']
                body = bridge.request_v01(scope,program,uuid.uuid4().hex)
                permit = bridge.permit_v01(run,scope,body,int(time.time()))
                row = store.reserve(ledger,profile,body,permit.evidence())
                bridge.send_v01(store,ledger,row,permit,lambda:config['scope'],client)
        for row in ledger['attempts']:
            if row['state'] in ('VALIDATED_AND_SAVED','REJECTED_SAMPLE_SET','TERMINAL_PROVIDER_ERROR'):
                continue
            raw = bridge.read_result_v01(store,ledger,row,client,s3)
            if raw is None:
                continue
            run = runs.get(row['profile']) or prepare(row['profile'])
            report = q.samples_v01(run.material,run.output,raw,task_arn=row['task_arn'],allow_suboptimal=scope['feasible_suboptimal_allowed'])
            bridge.atomic_json(args.output/'provider'/(row['profile']+'_sample_validation.json'),report)
            if report['selected'] is None:
                row['state']='REJECTED_SAMPLE_SET';store.save(ledger);continue
            consumed,_ = app.consume_v01(run,raw,row['task_arn'],allow_suboptimal=scope['feasible_suboptimal_allowed'],submission=row)
            bridge.atomic_json(args.output/'native'/row['profile']/'consume.json',consumed.evidence)
            saves = output.save_current_v01(consumed,args.output/'outputs'/row['profile'])
            row.update(state='VALIDATED_AND_SAVED',consumed_result_ref=consumed.evidence['artifact']['artifact_id'],save_paths=[s['claim']['path'] for s in saves]);store.save(ledger)
        return dict(status='OBSERVATION_COMPLETE_NO_AUTOMATIC_RETRY',states={r['profile']:r['state'] for r in ledger['attempts']},
                    next='READ_LEDGER_BEFORE_ANY_SEPARATELY_AUTHORIZED_RESUME')


def run_v01(args):
    config = launch_inputs_v01(args)
    return _local(args,config) if args.mode == 'local' else _hardware(args,config)
