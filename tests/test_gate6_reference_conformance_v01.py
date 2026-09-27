"""Bounded reference observations, not a final Living/Conformance collection."""
import json
import sys
from contextlib import contextmanager

from hedgehog.kernel import abi_v01 as abi
from hedgehog.kernel import integrity_replay_v01 as integrity
from hedgehog.kernel import root_signer_isolation_v01 as signer


def observe(record_property, name, **values):
    value = json.dumps(dict(observation=name, **values), sort_keys=True)
    record_property("g6_observation", value)
    print("G6_OBSERVATION=" + value)


def artifact_from_plain(value):
    data = dict(value)
    data["trace_refs"] = tuple(data["trace_refs"])
    data["parent_refs"] = tuple(data["parent_refs"])
    return abi.build_kernel_artifact_v01(**data)


@contextmanager
def observe_entry_counts(functions):
    """Synchronous current-thread Python calls only; refuse conflicting hooks."""
    previous = sys.getprofile()
    if previous is not None:
        raise RuntimeError("g6_observer_conflicting_profile")
    codes = {function.__code__: name for name, function in functions.items()}
    counts = dict.fromkeys(functions, 0)

    def entered(frame, event, arg):
        if event == "call" and frame.f_code in codes:
            counts[codes[frame.f_code]] += 1

    try:
        sys.setprofile(entered)
        yield counts
    finally:
        sys.setprofile(previous)


def observer_sentinel():
    return "observed"


def test_airline_native_adapter_work_root_and_abi(tmp_path, record_property):
    from hedgehog.domains.airline import gate4_reference_adapter_v01 as adapter

    directory = tmp_path / "native_airline"
    summary = adapter.preflight_v01(directory)
    read = lambda name: json.loads((directory / name).read_bytes())
    first, second = read("constraint_result.json"), read("provenance_result.json")
    assert summary["work_dispatches"] == summary["compute_units"] == 2
    assert second["trigger"]["output"]["result_artifact_ref"] == first["artifact"]["artifact_id"]
    assert len(second["results"][0]["consumed_fields"]) == 1
    for item in (first, second):
        assert not abi.validate_kernel_artifact_v01(artifact_from_plain(item["artifact"]))
        assert item["results"][0]["status"] == "COMPLETED"
    roots = read("roots.json")
    assert set(summary["root_decisions"].values()) == {"ACCEPT"}
    assert roots["refusal"][2]["decision"] == "NEEDS_USER"
    assert roots["refusal"][2]["reason_code"] == "user_permission_missing"
    assert roots["mixed"]["outcome_status"] == "MIXED"
    assert roots["mixed"]["authority_transfer_count"] == 0
    controls = read("controls.json")
    assert controls["wrong_offer"]["reason"] == "g40_selected_offer_binding"
    assert controls["coherent_wrong_source"]["reason"] == "g40_current_source_binding"
    assert controls["positive_neighbor"]
    assert summary["business_effects"] == summary["model_calls"] == summary["provider_calls"] == 0
    observe(record_property, "C01_AIRLINE_G4", summary=summary, roots=roots,
            source=read("input.json"), controls=controls, first=first, second=second,
            scope="Two native PURE Work operations; not the full G4 release story")


def test_gate5_native_math_result_is_consumed(record_property):
    from hedgehog.external_drs import gate5_native_v01 as native

    source = native.native_work("source", "root:gate5:calibration", "task:g6:source",
                                dict(readings="[8,10,9]", reference=10))
    assert source["outputs"] == dict(correction_den=1, correction_num=1, n=3, total=27)
    values = dict(readings="[20,22]", offset_num=source["outputs"]["correction_num"],
                  offset_den=source["outputs"]["correction_den"])
    consumer = native.native_work("corrected", "root:gate5:site", "task:g6:consumer", values)
    assert consumer["outputs"] == dict(corrected_den=1, corrected_num=22, mean_den=1, mean_num=21)
    for result in (source, consumer):
        assert result["attempts"] == 1
        assert not abi.validate_kernel_artifact_v01(artifact_from_plain(result["artifact"]))
    observe(record_property, "C01_G5_NATIVE", source=source, consumer=consumer,
            independent_oracle="(8+10+9)/3=9; offset=10-9=1; (20+22)/2+1=22",
            scope="Accepted native Work math only; no peer exchange, restart or football trial")


def test_anchor_signer_and_observed_pure_replay(record_property):
    from tests.test_kernel_integrity_replay_v01 import _fixture, REPLAY_ZERO_FIELDS
    from tests.test_root_signer_isolation_v01 import _fixture as signer_fixture
    from hedgehog.kernel import root_decision_v01 as root, work_composition_v01 as work
    from hedgehog.kernel import effect_firewall_v01 as firewall
    from hedgehog import work_execution_host_v01 as hosts

    fixture = _fixture()
    anchor = fixture.manifest.manifest_hash
    before = integrity.canonical_json_bytes_v01(integrity.artifact_manifest_to_plain_dict_v01(fixture.manifest))
    unanchored = integrity.verify_artifact_manifest_v01(manifest=fixture.manifest, payload_rows=fixture.payload_rows)
    anchored = integrity.verify_artifact_manifest_v01(manifest=fixture.manifest, payload_rows=fixture.payload_rows,
                                                       expected_manifest_hash=anchor)
    wrong = integrity.verify_artifact_manifest_v01(manifest=fixture.manifest, payload_rows=fixture.payload_rows,
                                                   expected_manifest_hash="0" * 64)
    assert unanchored.verification_status == "SELF_CONSISTENT_UNANCHORED"
    assert anchored.verification_status == "PASS"
    assert "expected_manifest_hash_mismatch" in wrong.verification_errors
    with observe_entry_counts(dict(root=root.decide_root_v01, work=work.advance_work_program_v01,
                                   host_dispatch=hosts.dispatch_current_action_v01,
                                   legacy_effect=firewall.execute_mock_effect_v01,
                                   native_effect=firewall.execute_bound_effect_v01,
                                   sentinel=observer_sentinel)) as counts:
        assert observer_sentinel() == "observed"
        replay = integrity.verify_artifact_replay_v01(manifest=fixture.manifest,
            payload_rows=fixture.payload_rows, expected_manifest_hash=anchor)
        refused = integrity.verify_artifact_replay_v01(manifest=fixture.manifest,
            payload_rows=fixture.payload_rows, expected_manifest_hash=None)
    assert replay.replay_status == "PASS" and counts["sentinel"] == 1
    assert all(value == 0 for key, value in counts.items() if key != "sentinel")
    assert refused.replay_errors == ("replay_expected_manifest_hash_required",)
    assert all(getattr(replay, field) == 0 for field in REPLAY_ZERO_FIELDS)
    assert before == integrity.canonical_json_bytes_v01(integrity.artifact_manifest_to_plain_dict_v01(fixture.manifest))
    fixture = signer_fixture()
    own = signer.verify_root_signature_v01(signature=fixture.signatures[0],
        trusted_key_set=fixture.key_set, commitment=fixture.commitments[0])
    import pytest
    with pytest.raises(ValueError, match="^signer_root_mismatch$"):
        signer.sign_root_owned_commitment_v01(capability=fixture.capabilities[1],
            trusted_key_set=fixture.key_set, commitment=fixture.commitments[0])
    assert own.verification_status == "PASS"
    observe(record_property, "C05_C06_ANCHORED_REPLAY", anchor=anchor,
            anchored=integrity.seal_verification_result_to_plain_dict_v01(anchored),
            unanchored=integrity.seal_verification_result_to_plain_dict_v01(unanchored),
            wrong=integrity.seal_verification_result_to_plain_dict_v01(wrong),
            replay=integrity.replay_verification_result_to_plain_dict_v01(replay),
            observed_calls=counts, observed_scope="Synchronous current-thread Python calls keyed by exact code objects",
            cross_root_reason="signer_root_mismatch",
            own=signer.root_signature_verification_result_to_plain_dict_v01(own),
            trust="Trusted setup retains the anchor and ephemeral key set before attacker input; not external PKI or semantic truth")
