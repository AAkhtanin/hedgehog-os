from hedgehog.mode_router import (
    classify_intent_complexity,
    detect_reflex_candidate,
    route_execution,
)


def direct_reuse_gate():
    return {
        "reuse_decision": "direct_reuse_candidate",
        "best_record_id": "work:eligible",
        "reused_record_ids": [],
        "candidate_scores": [
            {
                "record_id": "work:eligible",
                "eligible": True,
                "reuse_score": 0.9,
                "reason": "eligible",
            }
        ],
    }


def test_force_full_pipeline_always_returns_proof_full_pipeline():
    decision = route_execution(
        raw_user_text="turn on tv",
        retrieved_records=[{"record_id": "work:eligible"}],
        reuse_gate=direct_reuse_gate(),
        allow_direct_reuse=True,
        force_full_pipeline=True,
    )

    assert decision["execution_mode"] == "proof_full_pipeline"
    assert decision["direct_reuse_allowed"] is False
    assert decision["reason"] == "forced_full_pipeline_for_demo"


def test_direct_reuse_candidate_routes_direct_when_allowed_and_not_forced():
    decision = route_execution(
        raw_user_text="I need a certificate",
        retrieved_records=[{"record_id": "work:eligible"}],
        reuse_gate=direct_reuse_gate(),
        allow_direct_reuse=True,
        force_full_pipeline=False,
    )

    assert decision["execution_mode"] == "direct_reuse"
    assert decision["direct_reuse_allowed"] is True
    assert decision["reason"] == "eligible_direct_reuse"


def test_retrieved_records_without_direct_reuse_returns_context_only():
    decision = route_execution(
        raw_user_text="I need a certificate",
        retrieved_records=[{"record_id": "work:context"}],
        reuse_gate={"reuse_decision": "context_only"},
        allow_direct_reuse=False,
        force_full_pipeline=False,
    )

    assert decision["execution_mode"] == "context_only"
    assert decision["direct_reuse_allowed"] is False
    assert decision["reason"] == "memory_context_only"


def test_simple_known_action_returns_reflex_candidate_when_not_forced():
    assert detect_reflex_candidate("turn on tv")
    assert detect_reflex_candidate("switch on tv")
    assert classify_intent_complexity("open camera") == "simple_known_action"

    decision = route_execution(
        raw_user_text="repeat last route",
        retrieved_records=[],
        reuse_gate={"reuse_decision": "none"},
        allow_direct_reuse=False,
        force_full_pipeline=False,
        allow_reflex=True,
    )

    assert decision["execution_mode"] == "deterministic_reflex_candidate"
    assert decision["direct_reuse_allowed"] is False
    assert decision["reason"] == "simple_known_action_candidate"


def test_declared_reflex_action_routes_to_reflex_candidate():
    decision = route_execution(
        raw_user_text="switch on tv",
        retrieved_records=[],
        reuse_gate={"reuse_decision": "none"},
        allow_direct_reuse=False,
        force_full_pipeline=False,
        allow_reflex=True,
    )

    assert decision["execution_mode"] == "deterministic_reflex_candidate"
    assert decision["reason"] == "simple_known_action_candidate"


def test_reflex_candidate_takes_priority_over_context_when_allowed():
    decision = route_execution(
        raw_user_text="turn on tv",
        retrieved_records=[{"record_id": "work:prior_context"}],
        reuse_gate={"reuse_decision": "context_only"},
        allow_direct_reuse=False,
        force_full_pipeline=False,
        allow_reflex=True,
    )

    assert decision["execution_mode"] == "deterministic_reflex_candidate"
    assert decision["reason"] == "simple_known_action_candidate"


def test_reflex_candidate_does_not_route_when_not_allowed():
    decision = route_execution(
        raw_user_text="turn on tv",
        retrieved_records=[],
        reuse_gate={"reuse_decision": "none"},
        allow_direct_reuse=False,
        force_full_pipeline=False,
        allow_reflex=False,
    )

    assert decision["execution_mode"] == "proof_full_pipeline"
    assert decision["reason"] == "default_full_pipeline"


def test_unknown_request_defaults_to_proof_full_pipeline_when_not_forced():
    decision = route_execution(
        raw_user_text="Please figure out this ambiguous certificate request",
        retrieved_records=[],
        reuse_gate={"reuse_decision": "none"},
        allow_direct_reuse=False,
        force_full_pipeline=False,
    )

    assert decision["execution_mode"] == "proof_full_pipeline"
    assert decision["direct_reuse_allowed"] is False
    assert decision["reason"] == "default_full_pipeline"
