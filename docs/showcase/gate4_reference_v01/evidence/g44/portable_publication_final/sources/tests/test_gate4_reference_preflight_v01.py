"""One shared finite native probe; no release-spine or legacy runtime fixtures."""
import json
import os
from pathlib import Path
import pytest
from hedgehog.domains.airline import gate4_reference_adapter_v01 as adapter


@pytest.fixture(scope='module')
def native_probe(tmp_path_factory):
    directory = Path(os.environ['G40_EVIDENCE']) if 'G40_EVIDENCE' in os.environ else tmp_path_factory.mktemp('g40') / 'native'
    summary = adapter.preflight_v01(directory)
    def read(name):
        return json.loads((directory / name).read_bytes())
    return summary, read


def test_native_enrollment_spending_and_continuation(native_probe):
    summary, read = native_probe
    assert summary['work_dispatches'] == summary['compute_units'] == 2
    assert summary['original_compute_cap'] == 4 and summary['revisions'] == 1
    assert read('before.json')['usage']['compute_units'] == 0
    assert read('after.json')['usage']['compute_units'] == 2
    assert read('before.json')['policy'] == read('after.json')['policy']
    controls = read('controls.json')
    assert controls['stale_context'] == 'work_task_stale_snapshot'
    assert controls['terminal_retry_unchanged']
    first = read('constraint_result.json'); second = read('provenance_result.json')
    assert len(second['results'][0]['consumed_fields']) == 1
    assert second['trigger']['output']['result_artifact_ref'] == first['artifact']['artifact_id']
    assert first['results'][0]['status'] == second['results'][0]['status'] == 'COMPLETED'
    assert summary['business_effects'] == summary['model_calls'] == summary['provider_calls'] == 0


def test_actual_alternatives_and_coherent_source_controls(native_probe):
    summary, read = native_probe
    source = read('input.json')
    assert len(source['selection']['client_hard_compatible_candidate_ids']) == 2
    assert len({r['amount'] for r in source['snapshot']['authoritative_offer_records']}) == 2
    controls = read('controls.json')
    assert controls['wrong_offer']['reason'] == 'g40_selected_offer_binding'
    assert controls['coherent_wrong_source']['reason'] == 'g40_current_source_binding'
    assert controls['positive_neighbor']


def test_independent_root_consumption_and_missing_consent(native_probe):
    summary, read = native_probe
    roots = read('roots.json')
    assert set(summary['root_decisions'].values()) == {'ACCEPT'}
    assert roots['positive']['outcome_status'] == 'PASS'
    assert roots['mixed']['outcome_status'] == 'MIXED'
    assert roots['refusal'][2]['decision'] == 'NEEDS_USER'
    assert roots['refusal'][2]['reason_code'] == 'user_permission_missing'
    assert len(roots['mixed']['accepted_root_ids']) == 2
    assert roots['mixed']['permission_creation_count'] == roots['mixed']['authority_transfer_count'] == 0
    assert read('hold_preparation.json')['status'] == 'PREPARATION_ONLY_NOT_EXECUTED'


def test_g3_actual_proof_and_prospective_chronology(native_probe):
    summary, read = native_probe
    g3 = read('g3.json'); native = g3['native']['native']
    assert summary['native_proof'] == summary['predictive_source'] == 'PASS'
    assert g3['live_proof_validation'] == 'PASS' and not g3['supplied_reasons']
    assert int(native['claim_wall_ns']) <= int(native['event_wall_ns']) <= int(native['capture_wall_ns'])
    assert g3['native']['context']['scenario_id'] == 'G40_NEW_AIRLINE_ENROLLED_CONSTRAINT_AND_PROVENANCE'
    assert native['work_count'] == 1  # Prediction targets the first actual quantum.
    assert native['result_artifact_ref'] == read('constraint_result.json')['artifact']['artifact_id']
    assert g3['history_record_query_current_descent'] == 'NOT_RUN_MAPPED_ONLY'
    assert read('prospective.json')['payload']['expected_fp'] == 500000000


def test_frozen_reference_not_runtime():
    fixture = adapter.fixture_v01()
    assert fixture['numerical_reference']['evidence_class'] == 'NUMERICAL_REFERENCE_NOT_RUNTIME'
    assert fixture['numerical_reference']['gt']['recommend'] == 'B'
    assert fixture['numerical_reference']['avf']['neutral']['allocation'] == [4, 3]
    assert fixture['numerical_reference']['avf']['history_reference']['allocation'] == [3, 4]
