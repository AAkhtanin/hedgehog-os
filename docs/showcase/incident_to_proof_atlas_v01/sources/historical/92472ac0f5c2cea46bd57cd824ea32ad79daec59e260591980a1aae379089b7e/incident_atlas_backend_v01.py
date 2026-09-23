"""Finite synthetic backend and native capabilities, independent task contracts.

The backend deliberately has broader technical access than either task. Root
review and admitted validators consume separate local contracts before access.
"""
from dataclasses import replace
import copy
import json
from pathlib import Path

from hedgehog import action_commit_packet_v02 as actions
from hedgehog import work_execution_host_v01 as hosts
from hedgehog.incident_atlas_v01 import canonical_v01, digest_v01, require_v01
from hedgehog.kernel import effect_firewall_v01 as firewall, abi_v01 as abi
from . import gate3_runtime_v01 as native
from . import adversarial_feedback_v01 as donor

BACKENDS = {}
FIELDS = ('workspace_ref', 'request_ref', 'task_ref', 'object_ref', 'recipient_ref',
          'account_ref', 'credential_marker', 'body', 'receipt_claim')
OPERATIONS = ('READ', 'WRITE', 'ACK')


def specification_v01():
    return json.loads((Path(__file__).resolve().parents[3] / 'fixtures/incident_atlas_supplier_v01.json').read_bytes())


def receipt_errors_v01(claim, *, registry, expected):
    """Admission of a confirmation fact, never permission from a claimed receipt."""
    if type(claim) is not dict or set(claim) != {'receipt', 'object_ref', 'source_version'}:
        return ('atlas_receipt_claim_shape',)
    if claim['object_ref'] != expected['object_ref']:
        return ('atlas_receipt_wrong_object',)
    if claim['source_version'] != expected['source_version']:
        return ('atlas_receipt_source_version',)
    valid, reasons = actions.validate_action_commit_packet_registry_v02(registry)
    if not valid:
        return ('atlas_native_registry_invalid', *reasons)
    receipts = [ctx.receipt for ctx in registry.action_packet_fulfillment_attempt_contexts if ctx.receipt is not None]
    matches = [r for r in receipts if abi.kernel_artifact_to_plain_dict_v01(r) == claim['receipt']]
    if len(matches) != 1:
        return ('atlas_receipt_not_executed',)
    receipt = matches[0]
    payload = abi.kernel_artifact_to_plain_dict_v01(receipt)['payload']
    ev = firewall.native_execution_evidence_from_plain_data_v01(payload['execution_evidence'])
    errors = firewall.validate_native_execution_evidence_v01(ev)
    if errors:
        return tuple(errors)
    if (native.values(ev.invocation.inputs).get('order') != expected['object_ref']
            or receipt.owner_root_id != expected['root'] or receipt.artifact_id != expected['receipt_id']):
        return ('atlas_receipt_native_binding',)
    return ()


def contract_errors_v01(contract, proposal, operation, *, backend):
    errors = []
    for field, key in (('task_ref', 'task'), ('account_ref', 'account')):
        if proposal[field] != contract[key]:
            errors.append('atlas_contract_' + key)
    if [operation, proposal['object_ref'], proposal['recipient_ref']] not in contract['operations']:
        errors.append('atlas_contract_operation_object_recipient')
    if operation == 'ACK':
        try:
            claim = json.loads(proposal['receipt_claim'])
            if backend.receipt_registry is None:
                errors.append('atlas_receipt_source_missing')
            else:
                errors.extend(receipt_errors_v01(claim, registry=backend.receipt_registry, expected=backend.receipt_expected))
        except (ValueError, TypeError, KeyError):
            errors.append('atlas_receipt_claim_shape')
    return tuple(errors)


class BackendV01:
    def __init__(self, workspace_ref, *, receipt_registry=None, receipt_expected=None):
        require_v01(workspace_ref not in BACKENDS, 'atlas_backend_already_exists')
        self.spec = specification_v01()
        self.objects = copy.deepcopy(self.spec['objects'])
        self.calls = []
        self.context_by_task = {}
        self.receipt_registry = receipt_registry
        self.receipt_expected = receipt_expected
        self.operations = {}
        self.ref = workspace_ref
        BACKENDS[workspace_ref] = self

    def snapshot_v01(self):
        return dict(reads=sum(c['operation'] == 'READ' for c in self.calls),
                    writes=sum(c['operation'] == 'WRITE' for c in self.calls),
                    confirmations=sum(c['operation'] == 'ACK' for c in self.calls),
                    object_hashes={k: digest_v01(v) for k, v in self.objects.items()},
                    context_by_task=copy.deepcopy(self.context_by_task), calls=copy.deepcopy(self.calls),
                    shipment='HELD_NO_SHIPMENT_OPERATION')

    def technically_supports_v01(self, operation, object_ref, credential):
        return operation in OPERATIONS and (object_ref in self.objects or operation == 'ACK') and credential == self.spec['credential_marker']

    def invoke_v01(self, operation, proposal):
        require_v01(self.technically_supports_v01(operation, proposal['object_ref'], proposal['credential_marker']), 'atlas_backend_access')
        self.calls.append(dict(operation=operation, request_ref=proposal['request_ref'], task=proposal['task_ref'],
                               object_ref=proposal['object_ref'], recipient=proposal['recipient_ref']))
        if operation == 'READ':
            output = self.objects[proposal['object_ref']]
            self.context_by_task.setdefault(proposal['task_ref'], []).append(output)
        elif operation == 'WRITE':
            self.objects[proposal['object_ref']] = proposal['body']
            output = 'MESSAGE_RECORDED'
        else:
            output = 'NATIVE_CONFIRMATION_ACCEPTED_SHIPMENT_HELD'
        return output


def input_check_v01(definition, inputs):
    errors = firewall.validate_capability_values_v01(definition.input_fields, inputs)
    # Shape only here: the independent session contract is consumed by Root;
    # executor also checks invocation Root/task before touching this backend.
    return firewall.build_capability_validation_evidence_v01(definition=definition, values=inputs,
        invocation_id=None, valid=not errors, reason_codes=errors)


def execute_v01(invocation):
    proposal = native.values(invocation.inputs)
    backend = BACKENDS[proposal['workspace_ref']]
    contract = next(c for c in backend.spec['contracts'] if c['root'] == invocation.owning_root_id)
    require_v01(invocation.task_id == contract['task'], 'atlas_invocation_task')
    operation = backend.operations[invocation.definition_id]
    errors = contract_errors_v01(contract, proposal, operation, backend=backend)
    require_v01(not errors, 'atlas_executor_contract:' + ','.join(errors))
    result = backend.invoke_v01(operation, proposal)
    return native.records(dict(result=('TEXT', result), object_ref=('REFERENCE', proposal['object_ref'])))


def output_check_v01(definition, invocation, output):
    errors = firewall.validate_capability_values_v01(definition.output_fields, output)
    values = native.values(output)
    if values.get('object_ref') != native.values(invocation.inputs)['object_ref']:
        errors += ('atlas_output_object',)
    proposal = native.values(invocation.inputs)
    backend = BACKENDS[proposal['workspace_ref']]
    operation = backend.operations[invocation.definition_id]
    expected = (backend.objects[proposal['object_ref']] if operation == 'READ' else
                'MESSAGE_RECORDED' if operation == 'WRITE' else 'NATIVE_CONFIRMATION_ACCEPTED_SHIPMENT_HELD')
    if values.get('result') != expected:
        errors += ('atlas_output_material',)
    return firewall.build_capability_validation_evidence_v01(definition=definition, values=output,
        invocation_id=invocation.invocation_id, valid=not errors, reason_codes=errors)


class SessionV01:
    def __init__(self, backend, task):
        self.backend = backend
        self.contract = copy.deepcopy(next(c for c in backend.spec['contracts'] if c['task'] == task))
        self.root = self.contract['root']
        self.now = backend.spec['clock']
        self.source = native.CurrentSourceV01(self.now)
        self.admissions = {}
        codes = tuple(hosts.observe_local_capability_code_v01(fn) for fn in (input_check_v01, output_check_v01, execute_v01))
        for operation in OPERATIONS:
            key = 'atlas.supplier.' + operation
            bindings = tuple(firewall.build_capability_business_input_binding_v01(input_name=name,
                source_kind='RECORD', source_name=name, value_type='TEXT') for name in FIELDS)
            semantics = firewall.build_capability_business_semantics_v01(operation_key=key,
                selected_action_class='mock_action:atlas_' + operation.lower(), logical_effect_class='ATLAS_' + operation,
                logical_effect_namespace=key, business_object_class='DOMAIN_OBJECT',
                business_object_namespace='atlas.supplier', input_bindings=bindings)
            definition = firewall.build_capability_definition_v01(operation_id=key, version='v01',
                effect_kind='MOCK_CONSEQUENTIAL', business_semantics=semantics,
                input_fields=tuple(firewall.build_capability_field_v01(name=n,value_type='TEXT',required=True,consequential=True) for n in FIELDS),
                output_fields=(firewall.build_capability_field_v01(name='result',value_type='TEXT',required=True,consequential=False),
                               firewall.build_capability_field_v01(name='object_ref',value_type='REFERENCE',required=True,consequential=False)),
                resource_refs=('backend:atlas:supplier',), input_validator_ref=codes[0].public_symbol,
                output_validator_ref=codes[1].public_symbol, executor_ref=codes[2].public_symbol,
                code_sha256s=tuple((c.public_symbol,c.source_sha256) for c in codes))
            self.admissions[operation] = hosts.admit_local_capability_v01(definition=definition, input_validator=input_check_v01,
                output_validator=output_check_v01, executor=execute_v01, catalogue_revision=0, host_instance_ref='host:' + self.root)
            backend.operations[definition.definition_id] = operation
        self.host = hosts.build_root_work_execution_host_v01(owning_root_id=self.root,
            registry=actions.build_empty_action_commit_packet_registry_v02(), catalogue=tuple(self.admissions.values()),
            packet_bindings=(), current_dependency_observations=(), logical_time_bridge=self.source.snapshot.logical_time_bridge,
            trusted_source=self.source)

    def attempt_v01(self, proposal, operation):
        require_v01(set(proposal) == set(FIELDS) and all(type(v) is str for v in proposal.values()), 'atlas_proposal_shape')
        require_v01(operation in self.admissions, 'atlas_operation_unsupported')
        before = self.backend.snapshot_v01()
        registry_before = donor.encode_record_v01(self.host.registry)
        inputs = native.records({k: ('TEXT', v) for k,v in proposal.items()})
        admitted = self.admissions[operation]
        errors = contract_errors_v01(self.contract, proposal, operation, backend=self.backend)
        material = dict(contract=self.contract, proposal=proposal, operation=operation)
        digest = digest_v01(material)
        ref = 'atlas:material:' + digest
        dep = 'atlas:dependency:' + proposal['request_ref']
        provenance = ('atlas:independent_contract',)
        expiry = self.now + 120
        envelope = actions.build_action_dependency_time_envelope_id_v01(dependency_id=dep,evidence_ref=ref,content_sha256=digest,
            freshness_policy_id='atlas:current',source_provenance_refs=provenance,valid_from_utc=self.now,valid_to_utc=expiry)
        dependency = actions.build_dependency_set_candidate_v01(dependency_records=(actions.build_dependency_set_candidate_record_v01(
            dependency_id=dep,dependency_class='DOMAIN_AUTHORIZATION_INPUT',evidence_ref=ref,content_sha256=digest,
            requirement_class='MANDATORY',time_envelope_id=envelope,freshness_policy_id='atlas:current',source_provenance_refs=provenance,
            expected_accepting_local_root_id=self.root),))
        action = 'mock_action:atlas_' + operation.lower()
        permission = self.contract['permission']
        packet = actions.build_native_action_commit_packet_v01(transaction_id='transaction:' + proposal['request_ref'],
            owning_local_root_id=self.root, canonical_permission_ref=permission, selected_canonical_action=action,
            normalized_subject_scope=actions.build_action_subject_scope_profile_v01(included_subject_refs=(self.contract['task'],),excluded_subject_refs=()),
            normalized_target_scope=actions.build_action_target_scope_profile_v01(included_target_refs=('backend:atlas:supplier',),excluded_target_refs=()),
            normalized_permission_scope=actions.build_action_permission_scope_profile_v01(allowed_action_classes=(action,),forbidden_action_classes=(),
                allowed_adapter_ids=('mock_adapter:atlas',),forbidden_adapter_ids=(),required_approval_refs=(permission,),prohibited_effect_classes=()),
            adapter_binding=actions.build_action_adapter_binding_profile_v01(corridor_class='atlas.mock',adapter_id='mock_adapter:atlas',adapter_kind='DETERMINISTIC_MOCK',adapter_version='v01'),
            dependency_candidate=dependency,temporal_authority=actions.build_action_temporal_authority_profile_v01(issued_at_utc=self.now,expires_at_utc=expiry,ttl_seconds=120,temporal_policy_version='atlas:ttl'),
            authority_policy=actions.build_action_authority_policy_profile_v01(policy_version='atlas:local_contract',owning_local_root_id=self.root,
                authority_rule_refs=('atlas:root',),kill_switch_condition_refs=('atlas:revoke',),retry_policy='NON_CONSUMING_RETRY',supersession_policy='ROOT_DECISION_ONLY',
                logical_effect_namespace=admitted.definition.business_semantics.logical_effect_namespace,allowed_logical_effect_classes=('ATLAS_'+operation,),
                allowed_business_object_namespaces=('atlas.supplier',),allowed_corridor_classes=('atlas.mock',)),
            business_object_identity=actions.build_action_business_object_identity_profile_v01(business_object_class='DOMAIN_OBJECT',business_object_namespace='atlas.supplier',
                business_object_ref=proposal['object_ref'],owning_effect_root_id=self.root),
            consequential_effect_parameters=actions.build_action_consequential_effect_parameters_profile_v01(amount_decimal=None,currency_code=None,quantity_decimal=None,parameter_records=inputs),
            evaluation_time=self.now,evaluation_time_source='atlas.controlled_utc',evaluation_context_id='atlas:canonical',admitted_capability=admitted,inputs=inputs)
        review = native.review_operation_v01(self.root,packet.transaction_id,packet.authorization_candidate.root_packet_authorization_candidate_id,
            proposal['object_ref'],material,dict(independent_contract=not errors),canonical=packet,permission=permission)
        receipt = None
        failure = None
        if review[2].decision == 'ACCEPT':
            projection=actions.build_root_decision_candidate_projection_v01(candidate_kind='PACKET_AUTHORIZATION',
                projected_candidate_id=packet.authorization_candidate.root_packet_authorization_candidate_id,
                root_decision_kernel=review[0],root_decision_input=review[1],root_decision_result=review[2])
            bound=actions.build_native_root_bound_action_commit_packet_v01(canonical_projection=packet,root_decision_projection=projection)
            observation=actions.build_action_dependency_current_observation_v01(dependency_id=dep,evidence_ref=ref,observed_content_sha256=digest,
                time_envelope_id=envelope,freshness_policy_id='atlas:current',source_provenance_refs=provenance,valid_from_utc=self.now,valid_to_utc=expiry,
                observed_at_utc=self.now+4,observation_context_id='supplier:dispatch')
            self.source.install(observation)
            clock=self.source.snapshot
            try:
                hosts.install_current_action_v01(self.host,root_bound=bound,admission_id=admitted.admission_id,inputs=inputs,
                    **native.pending_material_v01(bound),expected_revision=self.host.revision,evaluation_time=clock.evaluation_time,
                    evaluation_time_source=clock.evaluation_time_source,evaluation_context_id=clock.evaluation_context_id)
                hosts.dispatch_current_action_v01(self.host,packet_id=bound.packet_identity.packet_id,task_id=self.contract['task'],
                    expected_revision=self.host.revision,evaluation_time=clock.evaluation_time,
                    evaluation_time_source=clock.evaluation_time_source,evaluation_context_id=clock.evaluation_context_id)
                context=self.host.registry.action_packet_fulfillment_attempt_contexts[-1]
                receipt=abi.kernel_artifact_to_plain_dict_v01(context.receipt) if context.receipt is not None else None
            except ValueError as exc:
                failure=str(exc)
        row=dict(contract=self.contract,proposal=proposal,operation=operation,contract_errors=list(errors),
                 canonical=donor.encode_record_v01(packet),review=donor.encode_record_v01(review),decision=review[2].decision,
                 receipt=receipt,failure=failure,before=before,after=self.backend.snapshot_v01(),
                 registry_before=registry_before,registry_after=donor.encode_record_v01(self.host.registry),
                 host_events=donor.encode_record_v01(self.host.events),origin='AUTHORED_FIXTURE',execution='FRESH_PUBLIC',
                 reached_boundary='ROOT' if review[2].decision!='ACCEPT' else 'CURRENTNESS' if failure else 'EXECUTOR',
                 not_reached=['HOST_DISPATCH','FIREWALL','EXECUTOR'] if review[2].decision!='ACCEPT' else [])
        row['record_id']=digest_v01(row)
        return row
