"""Unit tests for Platform Parity Dashboard attribution."""
from __future__ import annotations

import importlib.util
import sys
from pathlib import Path

_REPORT = Path(__file__).resolve().parents[3] / "scripts" / "performance_report.py"
_spec = importlib.util.spec_from_file_location("performance_report", _REPORT)
assert _spec and _spec.loader
_mod = importlib.util.module_from_spec(_spec)
sys.modules["performance_report"] = _mod
_spec.loader.exec_module(_mod)

build_parity_dashboard = _mod.build_parity_dashboard
demo_samples = _mod.demo_samples
parity_verdict = _mod.parity_verdict


def test_parity_verdict_android_outlier():
    row = {
        "backend_p95": 180.0,
        "web_p95": 420.0,
        "android_p95": 910.0,
        "ios_p95": 440.0,
    }
    assert parity_verdict(row) == "Android issue"


def test_parity_verdict_projection_delay():
    row = {
        "backend_p95": 620.0,
        "web_p95": 910.0,
        "android_p95": 940.0,
        "ios_p95": 930.0,
    }
    assert parity_verdict(row) == "Projection delay"


def test_parity_verdict_pass():
    row = {
        "backend_p95": 210.0,
        "web_p95": 320.0,
        "android_p95": 350.0,
        "ios_p95": 330.0,
    }
    assert parity_verdict(row) == "Pass"


def test_build_parity_dashboard_demo():
    rows = build_parity_dashboard(demo_samples())
    by_flow = {r["flow"]: r for r in rows}
    assert by_flow["setup.resume"]["verdict"] == "Android issue"
    assert by_flow["quick_add.personal.expense"]["verdict"] == "Pass"
    assert by_flow["mutation.delete"]["verdict"] == "Pass"
    assert by_flow["activity.refresh"]["verdict"] == "Projection delay"
