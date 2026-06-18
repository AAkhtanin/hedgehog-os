from __future__ import annotations

import subprocess
import sys

from demo.run_human_long_lived_drs_ttl_aging_stress_walkthrough_v01 import (
    render_human_long_lived_drs_ttl_aging_stress_walkthrough_v01,
)


def test_walkthrough_runner_exits_successfully():
    result = subprocess.run(
        [
            sys.executable,
            "-m",
            "demo.run_human_long_lived_drs_ttl_aging_stress_walkthrough_v01",
        ],
        check=False,
        capture_output=True,
        text=True,
    )

    assert result.returncode == 0
    assert (
        "HEDGEHOG OS — HUMAN WALKTHROUGH — LONG-LIVED DRS TTL AGING v0.1"
        in result.stdout
    )


def test_walkthrough_contains_required_human_markers():
    output = render_human_long_lived_drs_ttl_aging_stress_walkthrough_v01()

    required_markers = (
        "HEDGEHOG OS — HUMAN WALKTHROUGH — LONG-LIVED DRS TTL AGING v0.1",
        "Demo B",
        "Enterprise Document Killer Demo B",
        "d3840db",
        "f1eefee",
        "5274744",
        "scenarios_total: 25",
        "scenarios_passed: 25",
        "19 focused tests",
        "direct_reuse_allowed_count: 1 is expected",
        "TemporalHardGate",
        "RootShortcutAllowed",
        "AcceptedEvidence is not future action permission",
        "fresh ingestion is not fresh knowledge",
        "ReuseBoost cannot override hard gates",
        "quarantine/deadend proximity",
        "trust-aware supersession",
        "Memory may survive",
        "Authority does not survive through memory",
        "Root remains final authority",
        "not production DRS",
        "not external/global DRS",
        "not schema change",
        "not merged Killer Demo B proof",
    )

    for marker in required_markers:
        assert marker in output


def test_walkthrough_is_narrative_bridge_not_merged_proof():
    output = render_human_long_lived_drs_ttl_aging_stress_walkthrough_v01()

    assert "This walkthrough does not rerun or merge Demo B." in output
    assert "This is not merged Killer Demo B proof." in output
    assert "not runtime integration" in output
    assert "not proof of production readiness" in output
    assert "not public-auditor readiness" in output
    assert "network_used_count: 0" in output
    assert "gemini_used_count: 0" in output
    assert "marennya_activated_count: 0" in output
    assert "up_activated_count: 0" in output
