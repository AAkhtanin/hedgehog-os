ALLOWED_CANDIDATE_SOURCES = {
    "needle",
    "local_drs",
    "external_drs_pointer",
    "fallback_template",
}

HARD_FORBIDDEN_REGIONS = {
    "illegal_coercion",
    "fraud",
    "identity_abuse",
    "violence",
    "privacy_violation",
}


def is_allowed_candidate_source(source: str) -> bool:
    return source in ALLOWED_CANDIDATE_SOURCES
