from __future__ import annotations

import dataclasses
import hashlib
import inspect
import json

from demo import run_consolidated_gate2_gauntlet_g2_f_v01 as g2f


_REPORTS = []


def _actual_report():
    if not _REPORTS:
        _REPORTS.append(g2f.collect_consolidated_gate2_gauntlet_g2_f_v01())
    return _REPORTS[0]


def _receipt_position(report, row, lane):
    matches = [index for index, receipt in enumerate(report["row_receipts"])
               if receipt["row"] == row and receipt["lane"] == lane]
    assert len(matches) == 1
    return matches[0]


def _replace_receipt(report, row, lane, **changes):
    poisoned = dict(report)
    receipts = list(report["row_receipts"])
    index = _receipt_position(report, row, lane)
    receipts[index] = {**receipts[index], **changes}
    poisoned["row_receipts"] = tuple(receipts)
    return poisoned


def _replace_row_value(report, row, lane, value):
    poisoned = dict(report)
    rows = dict(report["rows"])
    rows[row] = dict(rows[row])
    rows[row][lane] = value
    poisoned["rows"] = rows
    return poisoned


def _stable_ref(value):
    type_name = type(value).__module__ + "." + type(value).__qualname__
    body = (type_name + "\0" + repr(value)).encode("utf-8")
    return "g2f_typed_repr_sha256:" + hashlib.sha256(body).hexdigest()


def _replace_event(report, original, *, result, input_bindings=None):
    replacement = {
        **original,
        "result": result,
        "input_bindings": (
            original["input_bindings"]
            if input_bindings is None
            else input_bindings
        ),
        "runtime_type": type(result),
        "stable_ref": _stable_ref(result),
    }
    event_by_id = {id(original): replacement}
    events = tuple(event_by_id.get(id(event), event)
                   for event in report["validation_events"])
    receipts = tuple(
        {
            **receipt,
            "validation_evidence": tuple(
                event_by_id.get(id(event), event)
                for event in receipt["validation_evidence"]
            ),
        }
        for receipt in report["row_receipts"]
    )
    return {**report, "validation_events": events, "row_receipts": receipts}


def _replace_row_output(report, row, lane, value):
    poisoned = _replace_row_value(report, row, lane, value)
    receipts = list(poisoned["row_receipts"])
    index = _receipt_position(poisoned, row, lane)
    receipts[index] = {
        **receipts[index],
        "produced_value": value,
        "runtime_type": type(value),
        "stable_ref": _stable_ref(value),
    }
    poisoned["row_receipts"] = tuple(receipts)
    return poisoned


def _replace_root_wrapper(report, lane, wrapper, validation_result):
    ordinal = ("client", "supplier").index(lane)
    wrappers = list(report["rows"][63]["root_set"])
    wrappers[ordinal] = wrapper
    poisoned = dict(report)
    rows = dict(report["rows"])
    rows[63] = {"root_set": tuple(wrappers)}
    poisoned["rows"] = rows

    receipts = list(report["row_receipts"])
    receipt_index = _receipt_position(report, 63, lane)
    receipt = receipts[receipt_index]
    events = [event for event in report["validation_events"]
              if event["row"] == 63]
    original_event = events[ordinal]
    replacement_event = {
        **original_event,
        "result": validation_result,
        "runtime_type": type(validation_result),
        "stable_ref": _stable_ref(validation_result),
    }
    event_by_id = {id(original_event): replacement_event}
    poisoned["validation_events"] = tuple(
        event_by_id.get(id(event), event)
        for event in report["validation_events"]
    )
    receipts = [
        {
            **item,
            "validation_evidence": tuple(
                event_by_id.get(id(event), event)
                for event in item["validation_evidence"]
            ),
        }
        for item in receipts
    ]
    receipts[receipt_index] = {
        **receipts[receipt_index],
        "produced_value": wrapper,
        "runtime_type": type(wrapper),
        "stable_ref": _stable_ref(wrapper),
    }
    poisoned["row_receipts"] = tuple(receipts)
    parent = g2f.multiroot.build_transaction_outcome_envelope_v01(
        transaction_id=report["shared_request_id"],
        expected_root_ids=report["rows"][64]["parent"].expected_root_ids,
        root_decisions=tuple(wrappers),
        cross_root_evidence_refs=report["rows"][62]["root_set"],
    )
    parent_validation = g2f.multiroot.validate_transaction_outcome_envelope_v01(parent)
    assert parent_validation == ()
    aggregate_result = g2f.multiroot.validate_multiroot_v01(parent)
    assert aggregate_result.errors == ()
    projection = g2f.multiroot.transaction_outcome_envelope_to_plain_dict_v01(parent)
    poisoned = _rebind_values(poisoned, (
        (report["rows"][64]["parent"], parent),
        (report["rows"][65]["parent"], aggregate_result),
        (report["rows"][66]["parent"], projection),
    ))
    for event in tuple(poisoned["validation_events"]):
        if event["row"] in (64, 65):
            result = parent_validation if event["row"] == 64 else aggregate_result
            poisoned = _replace_event(poisoned, event, result=result)
    return poisoned


def _rebind_values(report, replacements):
    # Copy only representation containers; typed replacements are public-call results.
    memo = {id(old): new for old, new in replacements}

    def visit(value):
        if id(value) in memo:
            return memo[id(value)]
        if type(value) is dict:
            copied = {}
            memo[id(value)] = copied
            copied.update((key, visit(item)) for key, item in value.items())
            return copied
        if type(value) in (tuple, list):
            copied = type(value)(visit(item) for item in value)
            memo[id(value)] = copied
            return copied
        return value

    copied = visit(report)
    for event in copied["validation_events"]:
        event["runtime_type"] = type(event["result"])
        event["stable_ref"] = _stable_ref(event["result"])
    for receipt in copied["row_receipts"]:
        receipt["runtime_type"] = type(receipt["produced_value"])
        receipt["stable_ref"] = _stable_ref(receipt["produced_value"])
    for receipt in (*copied["component_receipts"], *copied["auxiliary_receipts"]):
        receipt["runtime_type"] = type(receipt["result"])
        receipt["stable_ref"] = _stable_ref(receipt["result"])
        receipt["input_ref"] = _stable_ref(receipt["inputs"])
    return _refresh_causal_geometry(copied)


def _refresh_causal_geometry(report):
    parents = {}
    reverse = {}
    for receipt in report["row_receipts"]:
        if receipt["row"] >= 122:
            parents[receipt["row"]] = tuple(b[0] for b in receipt["input_bindings"])
        for parent_row, lane, retained, supplied in receipt["input_bindings"]:
            assert retained is report["rows"][parent_row][lane]
            assert supplied is retained
            reverse.setdefault((parent_row, lane), []).append(
                (receipt["row"], receipt["lane"], receipt["produced_value"])
            )
    receipts = tuple({**receipt, "consumed_by": tuple(reverse.get(
        (receipt["row"], receipt["lane"]), ()
    ))} for receipt in report["row_receipts"])
    return {
        **report,
        "row_receipts": receipts,
        "causal_parent_rows": tuple(parents.items()),
        "causal_edges": tuple((parent, row) for row, values in parents.items()
                              for parent in values),
    }


def _check_report(case_id, report, expected):
    result = g2f.validate_consolidated_gate2_gauntlet_g2_f_report_v01(report)
    assert result is expected, case_id
    return result


def _equivalent_control(case_id, baseline, equivalent):
    assert equivalent is not baseline
    assert equivalent["rows"] is not baseline["rows"]
    _check_report(case_id, equivalent, True)
    assert g2f.consolidated_gate2_gauntlet_g2_f_report_to_plain_data_v01(equivalent) == g2f.consolidated_gate2_gauntlet_g2_f_report_to_plain_data_v01(baseline)
    assert g2f.render_consolidated_gate2_gauntlet_g2_f_v01(equivalent) == g2f.render_consolidated_gate2_gauntlet_g2_f_v01(baseline)


def _public_arguments(builder, value):
    return {name: getattr(value, name) for name in inspect.signature(builder).parameters}


def _public_rejection(case_id, builder, arguments, expected_reason):
    try:
        builder(**arguments)
    except ValueError as error:
        assert str(error) == expected_reason, (case_id, str(error))
        return str(error)
    raise AssertionError((case_id, "public construction unexpectedly accepted"))


def _replace_observation(report, observation):
    copied = _rebind_values(report, ((report["rows"][129]["supplier"], observation),))
    event = next(item for item in copied["validation_events"] if item["row"] == 129)
    return _replace_event(copied, event, result=(
        g2f.action_packet.validate_action_invalidation_evidence_v01(observation)
    ))


def _replace_revocation_candidate(report, candidate):
    copied = _rebind_values(report, ((report["rows"][130]["supplier"], candidate),))
    rows = copied["rows"]
    for event in tuple(copied["validation_events"]):
        if not any(row == 130 for row, _value in event["input_bindings"]):
            continue
        validator = event["validator"]
        if validator is g2f.action_packet.validate_revocation_candidate_v01:
            result = validator(candidate)
        elif validator is g2f.action_packet.validate_revocation_candidate_against_packet_v01:
            result = validator(candidate, rows[84]["supplier"])
        elif validator is g2f.action_packet.validate_revocation_root_context_coherence_v01:
            result = validator(candidate, rows[138]["supplier"], rows[84]["supplier"])
        elif validator is g2f.action_packet.validate_action_invalidation_evidence_against_packet_v01:
            result = validator(rows[140]["supplier"], rows[84]["supplier"],
                               revocation_candidate=candidate,
                               revocation_root_projection=rows[138]["supplier"],
                               accepted_revocation_binding=rows[139]["supplier"])
        else:
            raise AssertionError(("unhandled changed validator inputs", validator))
        copied = _replace_event(copied, event, result=result)
    return copied


def _poison_operation(report, key, value):
    poisoned = dict(report)
    poisoned["operation_counts"] = dict(report["operation_counts"])
    poisoned["operation_counts"][key] = value
    return poisoned


def test_g2f_positive_01_report_geometry_and_current_basis():
    report = g2f.collect_consolidated_gate2_gauntlet_g2_f_v01()
    _REPORTS[:] = [report]
    assert g2f.validate_consolidated_gate2_gauntlet_g2_f_report_v01(report)
    assert tuple(sorted(report["rows"])) == tuple(range(1, 182))
    assert len(report["row_receipts"]) == 235
    assert {receipt["row"] for receipt in report["row_receipts"]} == set(range(1, 182))
    assert all(callable(receipt["producer"]) for receipt in report["row_receipts"])
    assert all(receipt["runtime_type"] is type(receipt["produced_value"])
               for receipt in report["row_receipts"])
    assert report["producer_basis"].count("\n") == 181
    assert len(report["producer_basis"].encode("ascii")) == 14264


def test_g2f_positive_02_causal_order_and_identity_lineage():
    report = _actual_report()
    parent_rows = dict(report["causal_parent_rows"])
    assert tuple(parent_rows) == tuple(range(122, 182))
    assert len(report["causal_edges"]) == 274
    assert sum(parent >= 122 for parent, _ in report["causal_edges"]) == 155
    assert all(parent < consumer for parent, consumer in report["causal_edges"])
    assert parent_rows[173] == (85, 154, 168, 171)
    for receipt in report["row_receipts"]:
        if receipt["row"] < 122:
            continue
        assert tuple(binding[0] for binding in receipt["input_bindings"]) == parent_rows[receipt["row"]]
        for parent_row, lane, retained, supplied in receipt["input_bindings"]:
            assert retained is report["rows"][parent_row][lane]
            assert supplied is retained


def test_g2f_positive_03_informational_fast_path_heavy_skip():
    report = _actual_report()
    rows = report["rows"]
    assert rows[24]["client"] == rows[24]["supplier"] == (True, ())
    assert rows[23]["client"].memory_descent_result is None
    assert rows[23]["supplier"].memory_descent_result is None
    assert report["laws"]["safe_informational_reuse_skips_heavy_work"] is True


def test_g2f_positive_04_high_risk_multiroot_full_fractal_execution():
    report = _actual_report()
    rows = report["rows"]
    assert rows[50]["client"].mode == rows[50]["supplier"].mode == "full_fractal"
    assert rows[69]["client"][0].cell_results and rows[69]["supplier"][0].cell_results
    assert report["root_local_transaction_ids"] == (rows[5]["client"].query_id,
                                                       rows[5]["supplier"].query_id)
    assert len(set(report["root_local_transaction_ids"])) == 2
    assert report["shared_request_id"] not in report["root_local_transaction_ids"]
    assert rows[64]["parent"].root_decisions == rows[63]["root_set"]
    for lane, wrapper in zip(("client", "supplier"), rows[63]["root_set"], strict=True):
        route_decision = rows[57][lane][0]
        assert wrapper.transaction_id == report["shared_request_id"]
        assert wrapper.root_decision_id == route_decision.decision_id
        assert wrapper.source_decision_ref == rows[58][lane].artifact_id
        assert wrapper.selected_subject_id == rows[60][lane].artifact_id


def test_g2f_positive_05_packet_delta_revocation_supersession_chain():
    report = _actual_report()
    plain = g2f.consolidated_gate2_gauntlet_g2_f_report_to_plain_data_v01(report)
    lifecycle = plain["lifecycle"]
    assert lifecycle["revoked_state"] == "REVOKED"
    assert lifecycle["old_packet_replay_state"] == "SUPERSEDED"
    assert lifecycle["old_packet_present_executable"] is False
    assert lifecycle["revocation_source_row"] == lifecycle["supersession_source_row"] == 98
    assert lifecycle["row_173_authorized_source_row"] == 154
    assert set(report["delta_role_bindings"]) == {"SIBLING", "TARGET"}
    assert report["delta_role_bindings"]["SIBLING"]["child_cell_id"] != report["delta_role_bindings"]["TARGET"]["child_cell_id"]


def test_g2f_positive_06_canonical_plain_projection_and_render():
    report = _actual_report()
    plain = g2f.consolidated_gate2_gauntlet_g2_f_report_to_plain_data_v01(report)
    rendered = g2f.render_consolidated_gate2_gauntlet_g2_f_v01(report)
    assert json.loads(rendered) == plain
    assert rendered.endswith("\n") and not rendered.endswith("\n\n")
    assert rendered[:-1] == json.dumps(plain, ensure_ascii=True, separators=(",", ":"), sort_keys=True)
    assert plain["primary_row_receipt_count"] == 235
    assert plain["component_receipt_count"] == len(report["component_receipts"])


def test_g2f_positive_07_independent_fresh_collections_no_cache():
    report = _actual_report()
    fresh = g2f.collect_consolidated_gate2_gauntlet_g2_f_v01()
    assert fresh is not report and fresh["rows"] is not report["rows"]
    assert g2f.validate_consolidated_gate2_gauntlet_g2_f_report_v01(fresh)
    assert g2f.consolidated_gate2_gauntlet_g2_f_report_to_plain_data_v01(fresh) == g2f.consolidated_gate2_gauntlet_g2_f_report_to_plain_data_v01(report)
    assert g2f.render_consolidated_gate2_gauntlet_g2_f_v01(fresh) == g2f.render_consolidated_gate2_gauntlet_g2_f_v01(report)


def test_g2f_positive_08_public_validator_accepts_actual_report():
    report = _actual_report()
    assert g2f.validate_consolidated_gate2_gauntlet_g2_f_report_v01(report)
    assert len(report["validation_events"]) > 181
    assert all(receipt["validation_evidence"] or receipt["validation_mode"] == "public_producer_internal"
               for receipt in report["row_receipts"])


def test_g2f_dod_01_safe_informational_reuse():
    report = _actual_report()
    assert report["laws"]["safe_informational_reuse_skips_heavy_work"] is True
    assert all(report["rows"][24][lane] == (True, ()) for lane in ("client", "supplier"))


def test_g2f_dod_02_action_reuse_blocked():
    report = _actual_report()
    assert report["laws"]["action_like_reuse_remains_blocked"] is True
    assert report["rows"][26]["client"].action_intent_passed is False
    assert "drs_action_intent_shortcut_forbidden" in report["rows"][26]["client"].reason_codes


def test_g2f_dod_03_high_risk_multiroot_deep():
    report = _actual_report()
    assert report["laws"]["high_risk_multiroot_selects_deep_path"] is True
    assert report["parent_multiroot_correlation_id"] == "transaction:g2f:gate2:v01"
    assert report["root_ids"] == ("root:g2f:client", "root:g2f:supplier")
    assert report["root_decision_logical_rows"] == (20, 33, 82, 128, 137, 152, 163)
    assert len(report["root_decisions"]) == 8
    assert len({item.decision_id for item in report["root_decisions"]}) == 8


def test_g2f_dod_04_revoke_before_fulfillment():
    report = _actual_report()
    assert report["laws"]["authorized_packet_revoked_before_fulfillment"] is True
    assert report["rows"][144]["supplier"].present_executable is False
    assert report["revocation_source_registry"] is report["rows"][98]["supplier"]


def test_g2f_dod_05_superseded_replay_blocked():
    report = _actual_report()
    assert report["laws"]["superseded_old_packet_replay_blocked"] is True
    assert report["rows"][180]["supplier"].reconstructed_state.lifecycle_state == "SUPERSEDED"
    assert report["rows"][181]["supplier"].present_executable is False
    assert report["supersession_source_registry"] is report["rows"][98]["supplier"]


def test_g2f_dod_06_selective_recompute():
    report = _actual_report()
    assert report["laws"]["selective_recomputation_complete_and_minimal"] is True
    assert report["rows"][117]["supplier"].complete is True
    assert report["rows"][117]["supplier"].minimal is True
    assert report["baseline_sibling_bytes_sha256"] == report["observed_sibling_bytes_sha256"]
    assert report["original_sibling_queue_bytes_sha256"] == report["recomputed_sibling_queue_bytes_sha256"]


def test_g2f_dod_07_components_non_authority():
    report = _actual_report()
    assert report["laws"]["components_create_no_authority"] is True
    assert report["operation_counts"]["non_root_authority_created_count"] == 0
    assert report["operation_counts"]["aggregate_authority_created"] is False
    assert report["operation_counts"]["superroot_created"] is False
    assert all(callable(item["producer"]) for item in report["component_receipts"])
    assert all(callable(item["producer"]) for item in report["auxiliary_receipts"])
    assert all(item["input_ref"] == _stable_ref(item["inputs"])
               and item["runtime_type"] is type(item["result"])
               and item["stable_ref"] == _stable_ref(item["result"])
               for item in report["component_receipts"])
    assert all(item["input_ref"] == _stable_ref(item["inputs"])
               and item["runtime_type"] is type(item["result"])
               and item["stable_ref"] == _stable_ref(item["result"])
               for item in report["auxiliary_receipts"])
    assert all(not item.authority_created and item.root_review_required
               and item.parent_return_required
               for lane in ("client", "supplier")
               for item in report["rows"][69][lane][0].cell_results)


def test_g2f_hostile_08_drs_not_authority():
    report = _actual_report()
    candidate = report["rows"][10]["client"]
    fresh_candidate = g2f.resolution.build_resolution_candidate_v01(**
        _public_arguments(g2f.resolution.build_resolution_candidate_v01, candidate))
    assert fresh_candidate is not candidate and fresh_candidate == candidate
    assert g2f.resolution.validate_resolution_candidate_v01(fresh_candidate) == (True, ())
    for field in ("creates_authority", "creates_permission", "creates_final_output"):
        case_id = "R4_DRS_" + field.upper()
        invalid = dataclasses.replace(fresh_candidate, **{field: True})
        actual_result = g2f.resolution.validate_resolution_candidate_v01(invalid)
        # This public validator checks non-authority before its conditional ID check.
        assert actual_result == (False, ("drs_non_authority_law_invalid",)), case_id
    rows = dict(report["rows"])
    rows[1] = {**rows[1], "foreign": rows[1]["client"]}
    assert not g2f.validate_consolidated_gate2_gauntlet_g2_f_report_v01({**report, "rows": rows})
    rows = dict(report["rows"])
    rows[1] = {"supplier": rows[1]["supplier"]}
    assert not g2f.validate_consolidated_gate2_gauntlet_g2_f_report_v01({**report, "rows": rows})
    assert not g2f.validate_consolidated_gate2_gauntlet_g2_f_report_v01(_replace_row_value(report, 10, "client", {"arbitrary": "carrier"}))
    assert not g2f.validate_consolidated_gate2_gauntlet_g2_f_report_v01(_poison_operation(report, "external_drs_calls", 1))


def test_g2f_hostile_09_router_not_authority():
    report = _actual_report()
    proposal = report["rows"][51]["client"]
    fresh_proposal = dataclasses.replace(proposal)
    assert fresh_proposal is not proposal
    assert g2f.router.validate_execution_mode_proposal_v01(fresh_proposal).reason_codes == ()
    for field in ("authority_created", "permission_created", "final_output_created"):
        case_id = "R4_ROUTER_" + field.upper()
        invalid = dataclasses.replace(fresh_proposal, **{field: True})
        invalid = dataclasses.replace(invalid, proposal_id=
            g2f.router.rebuild_execution_mode_proposal_identity_v01(invalid))
        assert invalid.proposal_id == g2f.router.rebuild_execution_mode_proposal_identity_v01(invalid)
        actual_result = g2f.router.validate_execution_mode_proposal_v01(invalid)
        assert actual_result.reason_codes == ("g2c_scalar_invalid",), case_id
    assert not g2f.validate_consolidated_gate2_gauntlet_g2_f_report_v01(_replace_receipt(report, 42, "client", transaction_id=report["rows"][5]["supplier"].query_id))
    assert not g2f.validate_consolidated_gate2_gauntlet_g2_f_report_v01(_replace_receipt(report, 42, "client", root_id="root:g2f:supplier"))
    poisoned = {**report, "root_local_transaction_ids": (report["rows"][5]["supplier"].query_id,) * 2}
    assert not g2f.validate_consolidated_gate2_gauntlet_g2_f_report_v01(poisoned)
    assert not g2f.validate_consolidated_gate2_gauntlet_g2_f_report_v01(_poison_operation(report, "non_root_authority_created_count", 1))


def test_g2f_hostile_10_registry_not_authority():
    report = _actual_report()
    registry = report["rows"][98]["supplier"]
    equivalent_registry = dataclasses.replace(registry)
    assert equivalent_registry is not registry and equivalent_registry == registry
    assert g2f.action_packet.validate_action_commit_packet_registry_v02(equivalent_registry) == (True, ())
    case_id = "R4_REGISTRY_PERMISSION_IS_NOT_AUTHORITY"
    invalid_registry = dataclasses.replace(equivalent_registry, creates_permission=True)
    actual_result = g2f.action_packet.validate_action_commit_packet_registry_v02(invalid_registry)
    assert actual_result == (False, ("registry_is_not_permission", "registry_is_not_authority")), case_id
    receipt = report["row_receipts"][_receipt_position(report, 83, "supplier")]
    poisons = (
        {"producer": g2f.G2F_EXECUTION_CONTRACT_V01[81][1]}, {"runtime_type": dict},
        {"stable_ref": "g2f_value_sha256:" + "0" * 64}, {"root_id": "root:g2f:client"},
        {"transaction_role": "PARENT_CORRELATION_TRANSACTION"}, {"enforcement_class": "UNENFORCED"},
        {"validation_evidence": ()},
    )
    for changes in poisons:
        assert not g2f.validate_consolidated_gate2_gauntlet_g2_f_report_v01(_replace_receipt(report, 83, "supplier", **changes))
    invalid_projection = dataclasses.replace(
        report["rows"][83]["supplier"],
        projected_candidate_id="candidate:g2f:foreign:v01",
    )
    actual_result = g2f.action_packet.validate_root_decision_candidate_projection_v01(
        invalid_projection
    )
    assert actual_result[0] is False and actual_result[1]
    poisoned = _replace_event(
        report,
        receipt["validation_evidence"][0],
        result=actual_result,
    )
    changed_event = next(
        event for event in poisoned["validation_events"]
        if event["row"] == 83
        and event["validator"] is g2f.action_packet.validate_root_decision_candidate_projection_v01
    )
    assert changed_event["stable_ref"] == _stable_ref(actual_result)
    assert changed_event["runtime_type"] is type(actual_result)
    assert not g2f.validate_consolidated_gate2_gauntlet_g2_f_report_v01(poisoned)


def test_g2f_hostile_11_child_not_root():
    report = _actual_report()
    rows = report["rows"]
    child = next(item for item in rows[69]["supplier"][0].cell_results if item.parent_cell_id is not None)
    fresh_child = dataclasses.replace(child)
    assert fresh_child is not child and fresh_child == child
    assert g2f.fractal_runtime.validate_fractal_cell_result_v02(fresh_child).reason_codes == ()
    for field in ("authority_created", "permission_created", "final_output_created"):
        case_id = "R4_CHILD_" + field.upper()
        invalid_child = dataclasses.replace(fresh_child, **{field: True})
        invalid_child = dataclasses.replace(invalid_child, result_id=
            g2f.fractal_runtime.rebuild_fractal_cell_result_identity_v02(invalid_child))
        assert invalid_child.result_id == g2f.fractal_runtime.rebuild_fractal_cell_result_identity_v02(invalid_child)
        actual_result = g2f.fractal_runtime.validate_fractal_cell_result_v02(invalid_child)
        assert actual_result.reason_codes == ("g2d_topology_authority_claim_forbidden",), case_id
    assert all(not item.authority_created and item.root_review_required and item.parent_return_required
               for lane in ("client", "supplier") for item in rows[69][lane][0].cell_results)
    receipt = report["row_receipts"][_receipt_position(report, 173, "supplier")]
    bindings = receipt["input_bindings"]
    poisons = (
        bindings[1:], (*bindings, bindings[0]),
        ((86, "supplier", rows[86]["supplier"], rows[86]["supplier"]), *bindings[1:]),
        ((181, "supplier", rows[181]["supplier"], rows[181]["supplier"]), *bindings[1:]),
        ((173, "supplier", rows[173]["supplier"], rows[173]["supplier"]), *bindings[1:]),
        ((5, "client", rows[5]["client"], rows[5]["client"]), *bindings[1:]),
    )
    for poisoned_bindings in poisons:
        assert not g2f.validate_consolidated_gate2_gauntlet_g2_f_report_v01(_replace_receipt(report, 173, "supplier", input_bindings=poisoned_bindings))
    assert not g2f.validate_consolidated_gate2_gauntlet_g2_f_report_v01(_replace_receipt(report, 168, "supplier", consumed_by=()))


def test_g2f_hostile_12_delta_not_authority():
    report = _actual_report()
    runtime_report = report["rows"][120]["supplier"][0].runtime_report
    runtime_arguments = _public_arguments(g2f.continuous_delta.build_continuous_delta_runtime_report_v01, runtime_report)
    equivalent_runtime = g2f.continuous_delta.build_continuous_delta_runtime_report_v01(**runtime_arguments)
    assert equivalent_runtime is not runtime_report and equivalent_runtime == runtime_report
    assert g2f.continuous_delta.validate_continuous_delta_runtime_report_v01(equivalent_runtime).reason_codes == ()
    for field in ("authority_created_count", "permissions_created", "final_outputs_created", "real_world_effects_count"):
        case_id = "R4_DELTA_" + field.upper()
        _public_rejection(case_id, g2f.continuous_delta.build_continuous_delta_runtime_report_v01,
                          {**runtime_arguments, field: 1}, "g2e_zero_operation_boundary_violated")
    assert (runtime_report.authority_created_count, runtime_report.permissions_created,
            runtime_report.final_outputs_created, runtime_report.real_world_effects_count) == (0, 0, 0, 0)
    components = list(report["component_receipts"])
    components[0] = {**components[0], "stable_ref": "g2f_value_sha256:" + "0" * 64}
    assert not g2f.validate_consolidated_gate2_gauntlet_g2_f_report_v01({**report, "component_receipts": tuple(components)})
    components = list(report["component_receipts"])
    wrong_component_inputs = ("supplier", components[0]["inputs"][1])
    components[0] = {
        **components[0],
        "inputs": wrong_component_inputs,
        "input_ref": _stable_ref(wrong_component_inputs),
    }
    assert components[0]["input_ref"] == _stable_ref(components[0]["inputs"])
    assert not g2f.validate_consolidated_gate2_gauntlet_g2_f_report_v01({**report, "component_receipts": tuple(components)})
    components = list(report["component_receipts"])
    components[0] = {
        **components[0],
        "result": report["rows"][39]["client"][1],
        "runtime_type": type(report["rows"][39]["client"][1]),
        "stable_ref": _stable_ref(report["rows"][39]["client"][1]),
    }
    assert not g2f.validate_consolidated_gate2_gauntlet_g2_f_report_v01({**report, "component_receipts": tuple(components)})
    auxiliaries = list(report["auxiliary_receipts"])
    auxiliaries[0] = {**auxiliaries[0], "producer": g2f.G2F_EXECUTION_CONTRACT_V01[0][1]}
    assert not g2f.validate_consolidated_gate2_gauntlet_g2_f_report_v01({**report, "auxiliary_receipts": tuple(auxiliaries)})
    auxiliaries = list(report["auxiliary_receipts"])
    wrong_auxiliary_inputs = (report["rows"][20]["client"],)
    auxiliaries[0] = {
        **auxiliaries[0],
        "inputs": wrong_auxiliary_inputs,
        "input_ref": _stable_ref(wrong_auxiliary_inputs),
    }
    assert auxiliaries[0]["input_ref"] == _stable_ref(auxiliaries[0]["inputs"])
    assert not g2f.validate_consolidated_gate2_gauntlet_g2_f_report_v01({**report, "auxiliary_receipts": tuple(auxiliaries)})
    bindings = {key: dict(value) for key, value in report["delta_role_bindings"].items()}
    bindings["TARGET"]["child_cell_id"] = bindings["SIBLING"]["child_cell_id"]
    assert not g2f.validate_consolidated_gate2_gauntlet_g2_f_report_v01({**report, "delta_role_bindings": bindings})
    bundle = report["rows"][69]["supplier"][0]
    root_input = next(item for item in bundle.cell_inputs if item.parent_cell_id is None)
    semantic_roles = (
        ("SIBLING", "unrelated_supplier_safe_sibling", 0),
        ("TARGET", "supplier_water_filter_dependency_consumer", 1),
    )
    expected_ids = {
        role: g2f.fractal_runtime.derive_fractal_child_cell_id_v02(
            topology_seed_id=bundle.topology_seed.topology_seed_id,
            parent_cell_id=root_input.cell_id,
            canonical_child_index=canonical_index,
            accepted_mode=bundle.source_binding.accepted_mode,
            selected_local_mode_profile_id=bundle.source_binding.selected_local_mode_profile_id,
            source_mode_profile_set_id=bundle.source_binding.source_mode_profile_set_id,
            child_scope_ref=bundle.topology.accepted_scope_ref,
            runtime_policy_id=bundle.source_binding.runtime_policy_id,
            required_capability_ids=bundle.source_binding.required_downstream_capability_ids,
            forbidden_claims=bundle.source_context.runtime_policy.forbidden_claims,
            child_depth=1,
        )
        for role, _semantic_role, canonical_index in semantic_roles
    }
    reversed_inputs = tuple(reversed(bundle.cell_inputs))
    resolved = {
        role: next(item.cell_id for item in reversed_inputs
                   if item.cell_id == expected_ids[role])
        for role, _semantic_role, _canonical_index in semantic_roles
    }
    assert resolved == expected_ids
    assert expected_ids == {
        role: report["delta_role_bindings"][role]["child_cell_id"]
        for role in ("SIBLING", "TARGET")
    }
    assert all(
        report["delta_role_bindings"][role]["scenario_role"] == semantic_role
        for role, semantic_role, _canonical_index in semantic_roles
    )
    reversed_entries = tuple(reversed(bundle.queue_entries))
    reversed_artifacts = tuple(reversed(bundle.queue_artifacts))
    resolved_queue_ids = {
        role: next(
            item.queue_entry_id for item in reversed_entries
            if item.queue_entry_id == binding["initial_queue_entry_id"]
        )
        for role, binding in report["delta_role_bindings"].items()
    }
    resolved_artifact_ids = {
        role: next(
            item.artifact_id for item in reversed_artifacts
            if g2f.abi.kernel_artifact_to_plain_dict_v01(item)["payload"]["queue_entry_id"]
            == binding["initial_queue_entry_id"]
        )
        for role, binding in report["delta_role_bindings"].items()
    }
    assert resolved_queue_ids == {role: binding["initial_queue_entry_id"] for role, binding in report["delta_role_bindings"].items()}
    assert resolved_artifact_ids == {role: binding["initial_queue_artifact_id"] for role, binding in report["delta_role_bindings"].items()}
    assert not g2f.validate_consolidated_gate2_gauntlet_g2_f_report_v01({
        **report,
        "baseline_sibling_bytes_sha256": "0" * 64,
    })


def test_g2f_hostile_13_no_permission_revival():
    report = _actual_report()
    rows = report["rows"]
    original_wrapper = rows[63]["root_set"][0]
    arguments = _public_arguments(g2f.multiroot.build_root_decision_envelope_v01, original_wrapper)
    equivalent_wrapper = g2f.multiroot.build_root_decision_envelope_v01(**arguments)
    assert equivalent_wrapper is not original_wrapper and equivalent_wrapper == original_wrapper
    equivalent = _replace_root_wrapper(
        report, "client", equivalent_wrapper,
        g2f.multiroot.validate_root_decision_envelope_v01(equivalent_wrapper),
    )
    _equivalent_control("R1_EQUIVALENT_WRAPPER_PARENT", report, equivalent)
    wrapper_changes = (
        ("R1_WRONG_DECISION", {"root_decision_id": rows[33]["client"].decision_id}),
        ("R1_WRONG_ARTIFACT", {"source_decision_ref": rows[58]["supplier"].artifact_id}),
    )
    for case_id, changes in wrapper_changes:
        wrong_wrapper = g2f.multiroot.build_root_decision_envelope_v01(**{**arguments, **changes})
        actual_validation = g2f.multiroot.validate_root_decision_envelope_v01(
            wrong_wrapper
        )
        assert actual_validation == ()
        poisoned = _replace_root_wrapper(
            report, "client", wrong_wrapper, actual_validation
        )
        poisoned_receipt = poisoned["row_receipts"][
            _receipt_position(poisoned, 63, "client")
        ]
        assert poisoned_receipt["produced_value"] is wrong_wrapper
        assert poisoned_receipt["stable_ref"] == _stable_ref(wrong_wrapper)
        assert poisoned["rows"][64]["parent"].root_decisions[0] is wrong_wrapper
        assert len({item.root_decision_id for item in poisoned["rows"][63]["root_set"]}) == 2
        _check_report(case_id, poisoned, False)

    case_id = "R1_WRONG_TRANSACTION"
    foreign_wrapper = g2f.multiroot.build_root_decision_envelope_v01(**{
        **arguments, "transaction_id": "transaction:g2f:foreign-parent:v01",
    })
    assert g2f.multiroot.validate_root_decision_envelope_v01(foreign_wrapper) == ()
    _public_rejection(case_id, g2f.multiroot.build_transaction_outcome_envelope_v01, {
        "transaction_id": report["shared_request_id"],
        "expected_root_ids": rows[64]["parent"].expected_root_ids,
        "root_decisions": (foreign_wrapper, rows[63]["root_set"][1]),
        "cross_root_evidence_refs": rows[62]["root_set"],
    }, "multiroot_transaction_mismatch")

    root_result = rows[128]["supplier"]
    fabricated = dataclasses.replace(
        rows[129]["supplier"],
        acceptance_root_decision_id=root_result.decision_id,
        acceptance_root_decision_hash=(
            g2f.action_packet.build_action_source_root_decision_hash_v01(root_result)
        ),
        root_decision_ref=root_result.decision_id,
    )
    fabricated_validation = g2f.action_packet.validate_action_invalidation_evidence_v01(
        fabricated
    )
    assert fabricated_validation == (
        False, ("action_invalidation_root_position_invalid",)
    )
    poisoned = _replace_row_output(report, 129, "supplier", fabricated)
    row129_event = next(event for event in report["validation_events"]
                        if event["row"] == 129)
    poisoned = _replace_event(
        poisoned,
        row129_event,
        result=fabricated_validation,
        input_bindings=((129, fabricated),),
    )
    poisoned_receipt = poisoned["row_receipts"][_receipt_position(poisoned, 129, "supplier")]
    assert poisoned_receipt["produced_value"] is fabricated
    assert poisoned_receipt["stable_ref"] == _stable_ref(fabricated)
    assert not g2f.validate_consolidated_gate2_gauntlet_g2_f_report_v01(poisoned)

    original_candidate = rows[130]["supplier"]
    foreign_evidence = "foreign-observation:g2f:v01"
    broken = g2f.action_packet.build_revocation_candidate_v01(
        owning_local_root_id=original_candidate.owning_local_root_id,
        packet_id=original_candidate.packet_id,
        source_authorization_decision_id=original_candidate.source_authorization_decision_id,
        idempotency_key=original_candidate.idempotency_key,
        revocation_reason_class=original_candidate.revocation_reason_class,
        evidence_refs=(foreign_evidence,),
        evidence_hashes=(hashlib.sha256(foreign_evidence.encode("utf-8")).hexdigest(),),
        evaluation_time=original_candidate.evaluation_time,
        policy_fingerprint=original_candidate.policy_fingerprint,
    )
    structural_result = g2f.action_packet.validate_revocation_candidate_v01(broken)
    contextual_result = g2f.action_packet.validate_revocation_candidate_against_packet_v01(
        broken, rows[84]["supplier"]
    )
    assert structural_result == contextual_result == (True, ())
    equivalent_candidate = g2f.action_packet.build_revocation_candidate_v01(
        **_public_arguments(g2f.action_packet.build_revocation_candidate_v01, original_candidate)
    )
    assert equivalent_candidate is not original_candidate and equivalent_candidate == original_candidate
    equivalent = _replace_revocation_candidate(report, equivalent_candidate)
    _equivalent_control("R2_EQUIVALENT_CANDIDATE", report, equivalent)
    case_id = "R2_CHANGED_CANDIDATE_ROOT_COHERENCE"
    poisoned = _replace_revocation_candidate(report, broken)
    assert broken.evidence_refs != (
        rows[129]["supplier"].invalidation_evidence_id,
    )
    context_event = next(event for event in poisoned["validation_events"]
                         if event["row"] == 138 and event["validator"] is
                         g2f.action_packet.validate_revocation_root_context_coherence_v01)
    assert context_event["result"] == (False, ("revocation_root_candidate_mismatch",))
    _check_report(case_id, poisoned, False)

    observation = rows[129]["supplier"]
    observation_args = _public_arguments(g2f.action_packet.build_action_invalidation_evidence_v01, observation)
    equivalent_observation = g2f.action_packet.build_action_invalidation_evidence_v01(**observation_args)
    assert equivalent_observation is not observation and equivalent_observation == observation
    equivalent = _replace_observation(report, equivalent_observation)
    _equivalent_control("R2_EQUIVALENT_OBSERVATION", report, equivalent)
    case_id = "R2_OBSERVATION_CANDIDATE_CONTINUITY"
    changed_observation = g2f.action_packet.build_action_invalidation_evidence_v01(**{
        **observation_args, "evaluation_time": observation.evaluation_time + 1,
    })
    assert g2f.action_packet.validate_action_invalidation_evidence_v01(changed_observation) == (True, ())
    poisoned = _replace_observation(report, changed_observation)
    assert changed_observation.source_invalidation_event_ref == observation.source_invalidation_event_ref
    assert changed_observation.evidence_ref == observation.evidence_ref
    assert changed_observation.invalidation_evidence_id != observation.invalidation_evidence_id
    assert poisoned["rows"][130]["supplier"] is original_candidate
    assert original_candidate.evidence_refs != (changed_observation.invalidation_evidence_id,)
    _check_report(case_id, poisoned, False)
    assert not g2f.validate_consolidated_gate2_gauntlet_g2_f_report_v01(_poison_operation(report, "permission_created_count", 1))


def test_g2f_hostile_14_no_stale_packet_replay():
    report = _actual_report()
    assert report["rows"][180]["supplier"].reconstructed_state.lifecycle_state == "SUPERSEDED"
    assert not g2f.validate_consolidated_gate2_gauntlet_g2_f_report_v01({**report, "supersession_source_registry": report["rows"][143]["supplier"]})
    revived = dataclasses.replace(report["rows"][181]["supplier"], present_executable=True)
    revived_validation = (
        g2f.action_packet.validate_action_packet_present_eligibility_inspection_v01(
            revived,
            report["rows"][179]["supplier"],
            packet_id=report["rows"][84]["supplier"].packet_identity.packet_id,
            corridor=report["rows"][100]["supplier"],
            corridor_step=report["rows"][99]["supplier"],
            current_dependency_observations=(report["rows"][101]["supplier"],),
            logical_time_bridge=report["rows"][102]["supplier"],
            evaluation_time=revived.evaluation_time,
            evaluation_time_source=revived.evaluation_time_source,
            evaluation_context_id=revived.evaluation_context_id,
            action_packet_transition_registry_profile=report["rows"][85]["supplier"],
        )
    )
    assert revived_validation[0] is False
    poisoned = _replace_row_output(report, 181, "supplier", revived)
    row181_event = next(event for event in report["validation_events"]
                        if event["row"] == 181)
    poisoned = _replace_event(
        poisoned,
        row181_event,
        result=revived_validation,
        input_bindings=tuple(
            (bound_row, revived if bound_row == 181 else bound_value)
            for bound_row, bound_value in row181_event["input_bindings"]
        ),
    )
    poisoned_receipt = poisoned["row_receipts"][_receipt_position(poisoned, 181, "supplier")]
    assert poisoned_receipt["stable_ref"] == _stable_ref(revived)
    assert not g2f.validate_consolidated_gate2_gauntlet_g2_f_report_v01(poisoned)

    row173_receipt = report["row_receipts"][_receipt_position(report, 173, "supplier")]
    wrong_source_bindings = tuple(
        (
            (145, "supplier", report["rows"][145]["supplier"],
             report["rows"][145]["supplier"])
            if parent_row == 154 else binding
        )
        for binding in row173_receipt["input_bindings"]
        for parent_row in (binding[0],)
    )
    assert tuple(binding[0] for binding in wrong_source_bindings) == (85, 145, 168, 171)
    assert all(binding[2] is report["rows"][binding[0]][binding[1]]
               and binding[3] is binding[2] for binding in wrong_source_bindings)
    equivalent_bindings = tuple(tuple(list(binding)) for binding in row173_receipt["input_bindings"])
    assert equivalent_bindings is not row173_receipt["input_bindings"]
    equivalent = _refresh_causal_geometry(_replace_receipt(
        _rebind_values(report, ()), 173, "supplier", input_bindings=equivalent_bindings
    ))
    _equivalent_control("R3_EQUIVALENT_CAUSAL_BINDINGS", report, equivalent)
    poisoned = _refresh_causal_geometry(_replace_receipt(
        report, 173, "supplier", input_bindings=wrong_source_bindings
    ))
    assert dict(poisoned["causal_parent_rows"])[173] == (85, 145, 168, 171)
    for parent in (145, 154):
        parent_receipt = poisoned["row_receipts"][_receipt_position(poisoned, parent, "supplier")]
        assert any(item[0] == 173 for item in parent_receipt["consumed_by"]) is (parent == 145)
    derived_map_bytes = (json.dumps(
        [[row, list(parents)] for row, parents in poisoned["causal_parent_rows"]],
        ensure_ascii=True, separators=(",", ":"),
    ) + "\n").encode("ascii")
    assert hashlib.sha256(derived_map_bytes).hexdigest() != g2f.CAUSAL_PARENT_ROWS_SHA256
    _check_report("R3_UNAUTHORIZED_SOURCE_MAP", poisoned, False)
    assert report["rows"][173]["supplier"][1].evidence_ref == (
        report["rows"][154]["supplier"].canonical_projection.temporal_authority_fingerprint
    )
    assert report["rows"][145]["supplier"].temporal_authority_fingerprint == (
        report["rows"][154]["supplier"].canonical_projection.temporal_authority_fingerprint
    )
    assert tuple(binding[0] for binding in row173_receipt["input_bindings"]) == (
        85, 154, 168, 171
    )


def test_g2f_hostile_15_no_aggregate_pass():
    report = _actual_report()
    outcome = report["rows"][64]["parent"]
    arguments = _public_arguments(g2f.multiroot.build_transaction_outcome_envelope_v01, outcome)
    equivalent_outcome = g2f.multiroot.build_transaction_outcome_envelope_v01(**arguments)
    assert equivalent_outcome is not outcome and equivalent_outcome == outcome
    assert g2f.multiroot.validate_transaction_outcome_envelope_v01(equivalent_outcome) == ()
    for field, changed_value, reason in (
        ("authority_transfer_count", 1, "multiroot_authority_transfer_forbidden"),
        ("permission_creation_count", 1, "multiroot_permission_transfer_forbidden"),
        ("super_root_created", True, "multiroot_super_root_forbidden"),
    ):
        case_id = "R4_MULTIROOT_" + field.upper()
        material = g2f.multiroot.transaction_outcome_envelope_to_plain_dict_v01(equivalent_outcome)
        material.pop("outcome_id")
        material[field] = changed_value
        identity = g2f.integrity_replay.domain_separated_sha256_hex_v01(
            domain="hedgehog.kernel.multiroot.transaction_outcome_envelope.v01",
            payload=g2f.integrity_replay.canonical_json_bytes_v01(material),
        )
        invalid_outcome = dataclasses.replace(equivalent_outcome, outcome_id=identity, **{field: changed_value})
        actual_result = g2f.multiroot.validate_transaction_outcome_envelope_v01(invalid_outcome)
        assert actual_result == (reason,), case_id
    assert report["rows"][64]["parent"].authority_transfer_count == 0
    assert report["rows"][64]["parent"].super_root_created is False
    receipt = report["row_receipts"][_receipt_position(report, 99, "supplier")]
    assert receipt["validation_owner_row"] == 103
    assert not g2f.validate_consolidated_gate2_gauntlet_g2_f_report_v01(_replace_receipt(report, 99, "supplier", validation_owner_row=181))
    assert not g2f.validate_consolidated_gate2_gauntlet_g2_f_report_v01(_replace_receipt(report, 99, "supplier", enforcement_class="CURRENT_VALIDATOR_ENFORCED"))
    assert not g2f.validate_consolidated_gate2_gauntlet_g2_f_report_v01(_poison_operation(report, "aggregate_authority_created", True))
    assert not g2f.validate_consolidated_gate2_gauntlet_g2_f_report_v01(_poison_operation(report, "superroot_created", True))


def test_g2f_hostile_16_zero_operations():
    report = _actual_report()
    assert set(report["operation_counts"].values()) == {0, False}
    for key in ("provider_calls", "model_calls", "network_calls", "connector_calls",
                "adapter_calls", "real_world_effects_count", "final_output_created_count"):
        assert not g2f.validate_consolidated_gate2_gauntlet_g2_f_report_v01(_poison_operation(report, key, 1))
