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


def create_marenna_after_task_record(
    request_id: str,
    session_anchor: str,
    work_record_id: str,
    domain: str = "government_certificate",
) -> dict:
    return {
        "marenna_record_id": f"marenna:{request_id}",
        "record_type": "marenna_reflection",
        "domain": domain,
        "initial_layer": "quarantine",
        "promotion_target_layer": "thoughts",
        "trigger": "after_task",
        "content": {
            "summary": "Quarantined after-task reflection placeholder for mock certificate flow."
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
            "created_by": "marenna",
        },
        "status": "quarantined",
    }
