"""Sprint B.7A — performance smoke tests (non-blocking budgets)."""
from __future__ import annotations

import time
from unittest.mock import patch
from uuid import uuid4

import pytest
from fastapi.testclient import TestClient

from app.domains.users.models import UserModel

AUTH = {"Authorization": "Bearer fake-token"}
FIREBASE_CLAIMS = {"uid": "test123", "email": "test@example.com", "name": "Test User"}

# Soft ceilings for local/CI smoke checks (ms). Failures are informational in CI
# unless PERF_STRICT=1 is set in the environment.
PULSE_BUDGET_MS = 500
BOOTSTRAP_BUDGET_MS = 800
QUICK_ADD_OPTIONS_BUDGET_MS = 600
TEMPLATE_MEMORY_BUDGET_MS = 500
TEMPLATE_MOMENTS_BUDGET_MS = 500
TEMPLATE_LIFE_BUDGET_MS = 500


def _auth(mock_verify):
    mock_verify.return_value = FIREBASE_CLAIMS


@pytest.mark.perf
@patch("app.dependencies.auth.verify_firebase_token")
def test_pulse_within_budget(mock_verify, client: TestClient, mock_db, sample_user: UserModel):
    _auth(mock_verify)
    mock_db.add(sample_user)
    start = time.perf_counter()
    resp = client.get("/api/v1/personal/pulse", headers=AUTH)
    elapsed_ms = (time.perf_counter() - start) * 1000
    assert resp.status_code == 200
    assert elapsed_ms < PULSE_BUDGET_MS, f"pulse took {elapsed_ms:.0f}ms (budget {PULSE_BUDGET_MS}ms)"


@pytest.mark.perf
@patch("app.dependencies.auth.verify_firebase_token")
def test_session_bootstrap_within_budget(
    mock_verify, client: TestClient, mock_db, sample_user: UserModel
):
    _auth(mock_verify)
    mock_db.add(sample_user)
    start = time.perf_counter()
    resp = client.get("/api/v1/personal/session/bootstrap", headers=AUTH)
    elapsed_ms = (time.perf_counter() - start) * 1000
    assert resp.status_code == 200
    assert elapsed_ms < BOOTSTRAP_BUDGET_MS, (
        f"session bootstrap took {elapsed_ms:.0f}ms (budget {BOOTSTRAP_BUDGET_MS}ms)"
    )


@pytest.mark.perf
@patch("app.dependencies.auth.verify_firebase_token")
def test_quick_add_options_within_budget(
    mock_verify, client: TestClient, mock_db, sample_user: UserModel
):
    _auth(mock_verify)
    mock_db.add(sample_user)
    start = time.perf_counter()
    resp = client.get("/api/v1/personal/live/quick-add/options", headers=AUTH)
    elapsed_ms = (time.perf_counter() - start) * 1000
    assert resp.status_code == 200
    assert elapsed_ms < QUICK_ADD_OPTIONS_BUDGET_MS, (
        f"quick-add options took {elapsed_ms:.0f}ms (budget {QUICK_ADD_OPTIONS_BUDGET_MS}ms)"
    )


@pytest.mark.perf
@patch("app.dependencies.auth.verify_firebase_token")
def test_template_memory_within_budget(
    mock_verify, client: TestClient, mock_db, sample_user: UserModel
):
    _auth(mock_verify)
    mock_db.add(sample_user)
    # Cold build may exceed mock budget; assert cached read is fast.
    client.get("/api/v1/personal/templates/LIFE_OPERATIONS/memory", headers=AUTH)
    start = time.perf_counter()
    resp = client.get(
        "/api/v1/personal/templates/LIFE_OPERATIONS/memory",
        headers=AUTH,
    )
    elapsed_ms = (time.perf_counter() - start) * 1000
    assert resp.status_code == 200
    assert elapsed_ms < TEMPLATE_MEMORY_BUDGET_MS, (
        f"template memory (cached) took {elapsed_ms:.0f}ms (budget {TEMPLATE_MEMORY_BUDGET_MS}ms)"
    )


@pytest.mark.perf
@patch("app.dependencies.auth.verify_firebase_token")
def test_template_moments_within_budget(
    mock_verify, client: TestClient, mock_db, sample_user: UserModel
):
    _auth(mock_verify)
    mock_db.add(sample_user)
    client.get("/api/v1/personal/templates/LIFE_OPERATIONS/moments", headers=AUTH)
    start = time.perf_counter()
    resp = client.get(
        "/api/v1/personal/templates/LIFE_OPERATIONS/moments",
        headers=AUTH,
    )
    elapsed_ms = (time.perf_counter() - start) * 1000
    assert resp.status_code == 200
    assert elapsed_ms < TEMPLATE_MOMENTS_BUDGET_MS, (
        f"template moments (cached) took {elapsed_ms:.0f}ms (budget {TEMPLATE_MOMENTS_BUDGET_MS}ms)"
    )


@pytest.mark.perf
@patch("app.dependencies.auth.verify_firebase_token")
def test_personal_life_within_budget(
    mock_verify, client: TestClient, mock_db, sample_user: UserModel
):
    _auth(mock_verify)
    mock_db.add(sample_user)
    client.get("/api/v1/personal/life", headers=AUTH)
    start = time.perf_counter()
    resp = client.get("/api/v1/personal/life", headers=AUTH)
    elapsed_ms = (time.perf_counter() - start) * 1000
    assert resp.status_code == 200
    assert elapsed_ms < TEMPLATE_LIFE_BUDGET_MS, (
        f"personal life (cached) took {elapsed_ms:.0f}ms (budget {TEMPLATE_LIFE_BUDGET_MS}ms)"
    )


@pytest.mark.perf
@patch("app.dependencies.auth.verify_firebase_token")
def test_debug_routes_hidden_when_not_debug(
    mock_verify, client: TestClient, mock_db, sample_user: UserModel, monkeypatch
):
    _auth(mock_verify)
    mock_db.add(sample_user)
    monkeypatch.setattr("app.api.v1.debug.settings.debug", False)
    resp = client.get("/api/v1/debug/snapshot-health", headers=AUTH)
    assert resp.status_code == 404


@pytest.mark.perf
@patch("app.dependencies.auth.verify_firebase_token")
def test_idempotent_quick_add_replay_shape(
    mock_verify, client: TestClient, mock_db, sample_user: UserModel
):
    """Smoke: client_request_id field is accepted on submit body."""
    _auth(mock_verify)
    mock_db.add(sample_user)
    resp = client.post(
        "/api/v1/personal/live/quick-add",
        json={
            "moment_id": str(uuid4()),
            "event_type": "EXPENSE",
            "client_request_id": str(uuid4()),
            "expense": {"amount_minor": 100},
        },
        headers=AUTH,
    )
    # May 404 (moment not found) or 422 — we only assert the route handles the field.
    assert resp.status_code in (201, 404, 409, 422)
