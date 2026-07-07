from __future__ import annotations

from pathlib import Path

import hedgehog.local_drs_v02 as drs_v02


def _fresh_envelope(
    freshness_class: str = drs_v02.FRESHNESS_FRESH_CONTEXT,
) -> drs_v02.DRSFreshnessEnvelope:
    return drs_v02.DRSFreshnessEnvelope(
        physical_time="2026-07-06T17:00:24Z",
        knowledge_time="2026-07-06T17:00:24Z",
        event_time="2026-07-06T17:00:24Z",
        context_time="full_wow_v1_2",
        ttl_seconds=3600,
        validity_start="2026-07-06T17:00:24Z",
        validity_end="2026-07-06T18:00:24Z",
        source_observed_at="2026-07-06T17:00:24Z",
        system_ingested_at="2026-07-06T17:00:25Z",
        freshness_class=freshness_class,
    )


def _query(
    *,
    allow_direct: bool = False,
    require_root_review: bool = True,
) -> drs_v02.TemporalQueryV02:
    return drs_v02.TemporalQueryV02(
        query_id="tq-wow-v1-2",
        as_of="2026-07-06T17:10:00Z",
        context_time="full_wow_v1_2",
        allow_direct_reuse_if_all_gates_pass=allow_direct,
        require_root_review=require_root_review,
    )


def _lineage_ref() -> drs_v02.DRSLineageRef:
    return drs_v02.DRSLineageRef(
        ref_id="trace:full_wow_v1_2",
        ref_kind="prior_trace",
        relation="derived_from",
        source_observed_at="2026-07-06T17:00:24Z",
        system_ingested_at="2026-07-06T17:00:25Z",
        notes=("Full WOW v1.2 baseline trace",),
    )


def _record(**overrides: object) -> drs_v02.DRSRecordV02:
    values = {
        "record_id": "drs-wow-v1-2-supplier-a",
        "record_kind": "accepted_evidence_context",
        "summary": "Supplier A prior scoped trace may inform context.",
        "time_envelope": _fresh_envelope(),
        "lineage_refs": (_lineage_ref(),),
        "source_refs": ("source:summary.json",),
        "provenance_refs": ("audit:full_wow_v1_2",),
    }
    values.update(overrides)
    return drs_v02.DRSRecordV02(**values)


def test_drs_v02_time_envelope_required() -> None:
    decision = drs_v02.evaluate_drs_record_v02(
        _record(time_envelope=None),
        _query(),
    )

    assert decision.reuse_decision_class == drs_v02.REUSE_BLOCKED
    assert drs_v02.REASON_MISSING_TIME_ENVELOPE in decision.reason_codes
    assert decision.direct_reuse_allowed is False
    assert decision.root_review_required is True


def test_drs_v02_temporal_query_required() -> None:
    decision = drs_v02.evaluate_drs_record_v02(_record(), None)

    assert decision.reuse_decision_class == drs_v02.REUSE_BLOCKED
    assert drs_v02.REASON_MISSING_TEMPORAL_QUERY in decision.reason_codes
    assert decision.direct_reuse_allowed is False


def test_drs_v02_hit_is_context_not_authority() -> None:
    decision = drs_v02.evaluate_drs_record_v02(_record(reuse_score=0.2), _query())

    assert decision.reuse_decision_class == drs_v02.REUSE_CONTEXT_ONLY
    assert decision.truth_claimed is False
    assert decision.authority_claimed is False
    assert decision.action_permission_claimed is False
    assert decision.final_output_claimed is False
    assert drs_v02.REASON_CONTEXT_ONLY_NOT_AUTHORITY in decision.reason_codes
    assert drs_v02.REASON_ROOT_REVIEW_REQUIRED in decision.reason_codes
    assert decision.lineage_refs == (_lineage_ref(),)


def test_drs_v02_stale_record_not_permission() -> None:
    decision = drs_v02.evaluate_drs_record_v02(
        _record(time_envelope=_fresh_envelope(drs_v02.FRESHNESS_STALE_WARNING)),
        _query(),
    )

    assert decision.reuse_decision_class in {
        drs_v02.REUSE_WARNING_ONLY,
        drs_v02.REUSE_RERUN_REQUIRED,
    }
    assert decision.direct_reuse_allowed is False
    assert drs_v02.REASON_STALE_RECORD_NOT_PERMISSION in decision.reason_codes


def test_drs_v02_old_receipt_not_action_permission() -> None:
    decision = drs_v02.evaluate_drs_record_v02(
        _record(contains_receipt=True, reuse_score=1.0),
        _query(allow_direct=True),
    )

    assert decision.reuse_decision_class in {
        drs_v02.REUSE_CONTEXT_ONLY,
        drs_v02.REUSE_RERUN_REQUIRED,
        drs_v02.REUSE_WARNING_ONLY,
    }
    assert decision.direct_reuse_allowed is False
    assert decision.action_permission_claimed is False
    assert drs_v02.REASON_OLD_RECEIPT_NOT_PERMISSION in decision.reason_codes


def test_drs_v02_prior_root_final_not_mutated() -> None:
    decision = drs_v02.evaluate_drs_record_v02(
        _record(root_final_ref="root-final:old-wow-v1-2", reuse_score=1.0),
        _query(allow_direct=True),
    )

    assert decision.direct_reuse_allowed is False
    assert decision.reuse_decision_class == drs_v02.REUSE_CONTEXT_ONLY
    assert drs_v02.REASON_PRIOR_ROOT_FINAL_NOT_SILENT_REUSE in decision.reason_codes


def test_drs_v02_lineage_refs_preserved() -> None:
    record = _record(
        source_refs=("source:summary.json", "source:validation.json"),
        provenance_refs=("audit:real-run", "story:human-readable"),
    )
    decision = drs_v02.evaluate_drs_record_v02(record, _query())
    report = drs_v02.build_drs_resolve_report_v02(_query(), [record])

    assert decision.lineage_refs == record.lineage_refs
    assert decision.source_refs == record.source_refs
    assert decision.provenance_refs == record.provenance_refs
    assert report.decisions[0].lineage_refs == record.lineage_refs
    assert report.decisions[0].source_refs == record.source_refs
    assert report.decisions[0].provenance_refs == record.provenance_refs
    assert report.lineage_refs_preserved_count == 1


def test_drs_v02_changed_facts_require_rerun_validation() -> None:
    decision = drs_v02.evaluate_drs_record_v02(
        _record(changed_facts=True),
        _query(),
    )

    assert decision.reuse_decision_class == drs_v02.REUSE_RERUN_REQUIRED
    assert drs_v02.REASON_CHANGED_FACTS_REQUIRE_RERUN_VALIDATION in decision.reason_codes


def test_drs_v02_quarantine_blocks_direct_reuse() -> None:
    decision = drs_v02.evaluate_drs_record_v02(
        _record(quarantine_proximity=True, reuse_score=1.0),
        _query(allow_direct=True),
    )

    assert decision.reuse_decision_class == drs_v02.REUSE_BLOCKED
    assert decision.direct_reuse_allowed is False
    assert drs_v02.REASON_QUARANTINE_PROXIMITY_BLOCKS_DIRECT_REUSE in decision.reason_codes


def test_drs_v02_deadend_blocks_or_downgrades_reuse() -> None:
    decision = drs_v02.evaluate_drs_record_v02(
        _record(deadend_proximity=True, reuse_score=1.0),
        _query(allow_direct=True),
    )

    assert decision.reuse_decision_class in {
        drs_v02.REUSE_BLOCKED,
        drs_v02.REUSE_WARNING_ONLY,
    }
    assert decision.direct_reuse_allowed is False
    assert (
        drs_v02.REASON_DEADEND_PROXIMITY_BLOCKS_OR_DOWNGRADES_REUSE
        in decision.reason_codes
    )


def test_drs_v02_direct_reuse_default_false() -> None:
    decision = drs_v02.evaluate_drs_record_v02(
        _record(reuse_score=0.99, policy_ok=True, permission_ok=True),
        _query(allow_direct=False),
    )

    assert decision.direct_reuse_allowed is False
    assert decision.reuse_decision_class in {
        drs_v02.REUSE_DIRECT_REUSE_CANDIDATE,
        drs_v02.REUSE_CONTEXT_ONLY,
    }
    assert (
        drs_v02.REASON_DIRECT_REUSE_DEFAULT_FALSE in decision.reason_codes
        or drs_v02.REASON_ROOT_REVIEW_REQUIRED in decision.reason_codes
    )


def test_drs_v02_direct_reuse_requires_all_hard_gates() -> None:
    decision = drs_v02.evaluate_drs_record_v02(
        _record(
            record_kind="prior_successful_work",
            reuse_score=0.99,
            root_shortcut_allowed=True,
            policy_ok=True,
            permission_ok=True,
        ),
        _query(allow_direct=True),
    )

    assert decision.direct_reuse_allowed is True
    assert decision.reuse_decision_class == drs_v02.REUSE_DIRECT_REUSE_ALLOWED
    assert decision.truth_claimed is False
    assert decision.authority_claimed is False
    assert decision.action_permission_claimed is False
    assert decision.final_output_claimed is False


def test_drs_v02_resolve_report_counts_and_boundaries() -> None:
    query = _query(allow_direct=True)
    records = [
        _record(record_id="context", reuse_score=0.1),
        _record(record_id="stale", time_envelope=_fresh_envelope(drs_v02.FRESHNESS_STALE_WARNING)),
        _record(
            record_id="direct",
            record_kind="prior_successful_work",
            root_shortcut_allowed=True,
            policy_ok=True,
            permission_ok=True,
            reuse_score=0.99,
        ),
    ]

    report = drs_v02.build_drs_resolve_report_v02(query, records)

    assert report.records_evaluated_count == 3
    assert report.direct_reuse_allowed_count == 1
    assert report.context_only_count == 1
    assert report.root_review_required_count >= report.records_evaluated_count
    assert report.lineage_refs_preserved_count == 3
    assert report.real_world_effects_count == 0
    assert report.production_ready_claimed is False
    assert report.public_auditor_ready_claimed is False


def test_drs_v02_module_has_no_provider_network_runtime_imports() -> None:
    source = Path(drs_v02.__file__).read_text(encoding="utf-8")
    forbidden_fragments = (
        "google.genai",
        "requests",
        "urllib",
        "openai",
        "subprocess",
        "run_full_wow",
        "run_full_semantic",
        "ActionCommitPacket " + "creation",
        "MockBankSandbox " + "execution",
        "real payment " + "executed",
    )

    for fragment in forbidden_fragments:
        assert fragment not in source
