from __future__ import annotations

from dataclasses import replace
import hashlib
import json

import pytest

from hedgehog.domains.airline import sealed_evidence_a2_binding_v01 as binding


SHA = "1" * 64
HEAD = "2" * 40


def _local_source():
    return binding.build_airline_a2_local_nonpublication_source_v01(
        attempt_id=SHA,
        execution_head=HEAD,
        implementation_content_sha256=SHA,
        attempt_identity_sha256=SHA,
        private_inventory_sha256=SHA,
        private_inventory_digest=SHA,
        generation_gate_sha256=SHA,
        corridor_archive_sha256=SHA,
        corridor_archive_byte_count=123,
        safe_report_sha256=SHA,
        safe_report_byte_count=456,
        safe_execution_id=SHA,
        wrapper_callback_observed_count=12,
        provider_callback_started_count=12,
        provider_callback_completed_count=12,
        collector_invocation_count=1,
        deterministic_airline_collection_count=1,
        ticket_purchase_corridor_execution_count=1,
        airline_transaction_artifact_ledger_collection_count=1,
        airline_crypto_artifact_seal_collection_count=1,
        outbound_provider_sdk_call_count=0,
        outbound_network_call_count=0,
        outbound_gemini_call_count=0,
        real_world_effects_count=0,
    )


def _official_source():
    return binding.build_airline_a2_official_accepted_source_v01(
        attempt_id=SHA,
        execution_head=HEAD,
        attempt_identity_sha256=SHA,
        private_inventory_sha256=SHA,
        private_inventory_digest=SHA,
        generation_gate_sha256=SHA,
        corridor_archive_sha256=SHA,
        corridor_archive_byte_count=123,
        public_safe_report_path=(
            "docs/evidence/two_domain_all_real_sealed_evidence_program_v01/"
            "airline/airline_safe_execution_report_attempt_04_v01.json"
        ),
        public_safe_report_sha256=SHA,
        public_safe_report_byte_count=456,
        safe_execution_id=SHA,
        generation_audit_path=(
            "docs/audit_reports/"
            "auditor_two_domain_airline_all_real_generation_attempt_04_v01.log"
        ),
        generation_audit_sha256=SHA,
        wrapper_callback_observed_count=12,
        provider_callback_started_count=12,
        provider_callback_completed_count=12,
        provider_call_count=12,
        network_call_count=12,
        gemini_call_count=12,
        collector_invocation_count=1,
        deterministic_airline_collection_count=1,
        ticket_purchase_corridor_execution_count=1,
        airline_transaction_artifact_ledger_collection_count=1,
        airline_crypto_artifact_seal_collection_count=1,
        duplicate_actor_call_count=0,
        retry_count=0,
        fallback_call_count=0,
        package_created_count=0,
        anchor_created_count=0,
        replay_created_count=0,
        real_world_effects_count=0,
    )


def test_local_source_is_closed_nonpublication_geometry() -> None:
    source = _local_source()
    assert source.source_variant == binding.SOURCE_LOCAL
    assert source.safe_report_logical_name == "safe-report-v01.json"
    assert source.official_evidence_eligible is False
    assert binding.validate_airline_a2_local_nonpublication_source_v01(source) == ()


def test_source_variants_use_exact_disjoint_identity_domains() -> None:
    local = _local_source()
    official = _official_source()
    for source, domain, identity_key in (
        (
            local,
            "hedgehog-os:airline-a2-source-identity:v0.1:"
            "LOCAL_NONPUBLICATION_SOURCE",
            "source_identity_id",
        ),
        (
            official,
            "hedgehog-os:airline-a2-source-identity:v0.1:"
            "OFFICIAL_ACCEPTED_SOURCE",
            "source_identity_id",
        ),
    ):
        plain = binding._plain(source)
        plain[identity_key] = "0" * 64
        expected = hashlib.sha256(
            domain.encode("ascii")
            + b"\0"
            + json.dumps(
                plain,
                ensure_ascii=False,
                sort_keys=True,
                separators=(",", ":"),
                allow_nan=False,
            ).encode("utf-8")
        ).hexdigest()
        assert source.source_identity_id == expected
    assert type(local) is not type(official)
    assert "corridor_validation_identity" not in {
        field.name for field in binding.fields(type(local))
    }
    assert "corridor_validation_identity" not in {
        field.name for field in binding.fields(type(official))
    }


@pytest.mark.parametrize(
    "field,value",
    (
        ("official_evidence_eligible", True),
        ("safe_report_logical_name", "other.json"),
        ("attempt_number", 3),
        ("outbound_network_call_count", 1),
    ),
)
def test_local_source_rejects_mutation(field: str, value: object) -> None:
    assert binding.validate_airline_a2_local_nonpublication_source_v01(
        replace(_local_source(), **{field: value})
    )


def test_three_package_invocation_variants_are_disjoint() -> None:
    source = _local_source()
    pre = binding.build_airline_a2_local_precommit_package_invocation_v01(
        base_head=HEAD,
        implementation_content_sha256=SHA,
        local_source_identity_id=source.source_identity_id,
    )
    committed = binding.build_airline_a2_local_committed_package_invocation_v01(
        committed_head=HEAD,
        origin_main_head=HEAD,
        implementation_content_sha256=SHA,
        local_source_identity_id=source.source_identity_id,
    )
    official = binding.build_airline_a2_official_package_invocation_v01(
        official_source_identity_id=SHA,
        implementation_head=HEAD,
        publication_base_head=HEAD,
    )
    assert len({type(pre), type(committed), type(official)}) == 3
    assert len(
        {
            pre.package_invocation_id,
            committed.package_invocation_id,
            official.package_invocation_id,
        }
    ) == 3


@pytest.mark.parametrize(
    "variant,field,value",
    (
        ("precommit", "base_head", "A" * 40),
        ("precommit", "implementation_content_sha256", "x" * 64),
        ("committed", "origin_main_head", "3" * 40),
        ("committed", "official_publication_claimed", True),
        ("official", "package_output_ref", "other"),
        ("official", "publication_base_head", "+" + HEAD),
    ),
)
def test_package_invocation_variants_reject_context_mutation(
    variant: str,
    field: str,
    value: object,
) -> None:
    source = _local_source()
    if variant == "precommit":
        invocation = binding.build_airline_a2_local_precommit_package_invocation_v01(
            base_head=HEAD,
            implementation_content_sha256=SHA,
            local_source_identity_id=source.source_identity_id,
        )
        validator = binding.validate_airline_a2_local_precommit_package_invocation_v01
    elif variant == "committed":
        invocation = binding.build_airline_a2_local_committed_package_invocation_v01(
            committed_head=HEAD,
            origin_main_head=HEAD,
            implementation_content_sha256=SHA,
            local_source_identity_id=source.source_identity_id,
        )
        validator = binding.validate_airline_a2_local_committed_package_invocation_v01
    else:
        invocation = binding.build_airline_a2_official_package_invocation_v01(
            official_source_identity_id=_official_source().source_identity_id,
            implementation_head=HEAD,
            publication_base_head=HEAD,
        )
        validator = binding.validate_airline_a2_official_package_invocation_v01
    assert validator(replace(invocation, **{field: value}))


def test_process_a_result_round_trip_and_identity() -> None:
    result = binding.build_airline_a2_local_process_a_result_v01(
        gate_phase="precommit",
        verified_head_token=HEAD,
        implementation_content_sha256=SHA,
        attempt_id=SHA,
        execution_head=HEAD,
        attempt_identity_sha256=SHA,
        private_inventory_sha256=SHA,
        private_inventory_digest=SHA,
        generation_gate_sha256=SHA,
        corridor_archive_sha256=SHA,
        corridor_archive_byte_count=1,
        safe_report_sha256=SHA,
        safe_report_byte_count=1,
        safe_execution_id=SHA,
        wrapper_callback_observed_count=12,
        provider_callback_started_count=12,
        provider_callback_completed_count=12,
        semantic_actor_call_count=12,
        causal_actor_call_count=5,
        generic_actor_call_count=7,
        duplicate_actor_call_count=0,
        collector_invocation_count=1,
        deterministic_airline_collection_count=1,
        ticket_purchase_corridor_execution_count=1,
        airline_transaction_artifact_ledger_collection_count=1,
        airline_crypto_artifact_seal_collection_count=1,
        outbound_provider_sdk_call_count=0,
        outbound_network_call_count=0,
        outbound_gemini_call_count=0,
        real_world_effects_count=0,
    )
    plain = binding.airline_a2_local_process_a_result_to_plain_dict_v01(result)
    assert binding.airline_a2_local_process_a_result_from_plain_dict_v01(plain) == result


@pytest.mark.parametrize(
    "field,value",
    (
        ("gate_phase", "unknown"),
        ("safe_report_logical_name", "other.json"),
        ("wrapper_callback_observed_count", 11),
        ("outbound_network_call_count", 1),
        ("final_status", "FAIL_CLOSED"),
        ("validation_errors", ("error",)),
    ),
)
def test_process_a_result_rejects_mutation(field: str, value: object) -> None:
    plain = binding.airline_a2_local_process_a_result_to_plain_dict_v01(
        binding.build_airline_a2_local_process_a_result_v01(
            gate_phase="precommit",
            verified_head_token=HEAD,
            implementation_content_sha256=SHA,
            attempt_id=SHA,
            execution_head=HEAD,
            attempt_identity_sha256=SHA,
            private_inventory_sha256=SHA,
            private_inventory_digest=SHA,
            generation_gate_sha256=SHA,
            corridor_archive_sha256=SHA,
            corridor_archive_byte_count=1,
            safe_report_sha256=SHA,
            safe_report_byte_count=1,
            safe_execution_id=SHA,
            wrapper_callback_observed_count=12,
            provider_callback_started_count=12,
            provider_callback_completed_count=12,
            semantic_actor_call_count=12,
            causal_actor_call_count=5,
            generic_actor_call_count=7,
            duplicate_actor_call_count=0,
            collector_invocation_count=1,
            deterministic_airline_collection_count=1,
            ticket_purchase_corridor_execution_count=1,
            airline_transaction_artifact_ledger_collection_count=1,
            airline_crypto_artifact_seal_collection_count=1,
            outbound_provider_sdk_call_count=0,
            outbound_network_call_count=0,
            outbound_gemini_call_count=0,
            real_world_effects_count=0,
        )
    )
    plain[field] = list(value) if type(value) is tuple else value
    with pytest.raises(ValueError):
        binding.airline_a2_local_process_a_result_from_plain_dict_v01(plain)


def test_canonical_json_rejects_nonfinite_values() -> None:
    with pytest.raises(ValueError):
        binding.canonical_json_bytes_v01({"value": float("nan")})


@pytest.mark.parametrize(
    "content",
    (
        b'{"x":1,"x":2}\n',
        b'{"x":NaN}\n',
        b'{"x":Infinity}\n',
        b'[]\n',
        b'{"x":1}\x00\n',
        b'\xef\xbb\xbf{"x":1}\n',
        b'\xff\n',
    ),
)
def test_strict_json_boundary_rejects_malformed_input(content: bytes) -> None:
    with pytest.raises((UnicodeError, ValueError)):
        binding._strict_json_bytes(content)
