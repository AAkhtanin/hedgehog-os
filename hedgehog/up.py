from __future__ import annotations

from hedgehog.time_model import make_time_envelope


VALIDATION_STAGE_NAMES = (
    "static",
    "dedup",
    "rag_support",
    "self_consistency",
    "utility",
    "safety",
)


def _pending_validation() -> dict:
    return {
        name: {
            "status": "pending",
            "score": 0.0,
        }
        for name in VALIDATION_STAGE_NAMES
    }


def create_up_after_task_record(
    request_id: str,
    session_anchor: str,
    work_record_id: str,
    source_domain: str = "government_certificate",
    target_domain: str = "generic",
) -> dict:
    return {
        "up_record_id": f"up:{request_id}",
        "record_type": "up_protocol_template",
        "source_domain": source_domain,
        "target_domain": target_domain,
        "initial_layer": "quarantine",
        "promotion_target_layer": "up",
        "trigger": "after_task",
        "content": {
            "summary": "Quarantined cross-domain transfer placeholder for mock certificate flow."
        },
        "validation": _pending_validation(),
        "time_envelope": make_time_envelope(session_anchor),
        "provenance": {
            "request_id": request_id,
            "source_bundle_refs": [
                {
                    "source": "local_drs",
                    "source_id": work_record_id,
                }
            ],
            "created_by": "up",
        },
        "status": "quarantined",
        "actionable": False,
        "metrics": {
            "novelty": 0.0,
            "expected_utility": 0.0,
            "risk": 0.0,
            "energy": 0.0,
        },
    }
