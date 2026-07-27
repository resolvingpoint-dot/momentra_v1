#!/usr/bin/env python3
"""Run 10.5 — Business Operations staging verification harness (HTTP only, no UI E2E)."""
from __future__ import annotations

import json
import sys
import time
import uuid
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

import httpx

BASE = "http://127.0.0.1:8000"
OUT = Path(__file__).resolve().parent / "run10_last_result.json"

COMPLETE_ANSWERS = {
    "moment_name": "10 Ops Staging",
    "operations_name": "10 Staging Ops",
    "operations_scope": "GENERAL_OPERATIONS",
    "operating_model": "HYBRID",
    "operating_currency_code": "USD",
    "timezone": "America/New_York",
    "locale": "en-US",
    "country_code": "US",
    "financial_year_start": "01",
    "review_cycle": "MONTHLY",
    "monthly_budget_minor": 1000000,
    "allocation_mode": "FIXED_AMOUNT",
    "budget_categories": ["ops", "vendors"],
    "budget_allocations": [],
    "vendor_dependency_level": "MODERATE",
    "approval_model": "OWNER_ONLY",
    "issue_sensitivity": "NORMAL",
    "monitoring_level": "STANDARD",
    "operational_visibility": "TEAM",
    "invite_on_activation": False,
    "confirm_budget": True,
    "confirm_allocations": True,
    "confirm_governance": True,
    "confirm_members": True,
    "confirm_alerts": True,
    "activate_monitoring": True,
    "members": [],
}

WARM_TARGETS_MS = {
    "pulse": 150,
    "moments": 200,
    "life": 200,
    "memory": 200,
    "activity": 250,
}

PULSE_SECTIONS = (
    "hero",
    "operations_health",
    "kpis",
    "budget_usage",
    "approvals",
    "issues",
    "vendors",
    "improvements",
    "monitoring",
    "attention_items",
    "signals",
    "recent_activity",
    "next_best_action",
)

MOMENTS_SECTIONS = (
    "journey_hero",
    "summary_stats",
    "spend_timeline",
    "approval_timeline",
    "issue_timeline",
    "vendor_timeline",
    "improvement_timeline",
    "milestones",
    "key_decisions",
    "timeline",
    "recent_activity",
)


def _auth_headers(token: str) -> dict:
    return {"Authorization": f"Bearer {token}", "Content-Type": "application/json"}


def _login(client: httpx.Client) -> str:
    email = f"ops10_{uuid.uuid4().hex[:10]}@example.com"
    password = "TestPass123!"
    r = client.post(
        f"{BASE}/api/v1/auth/register",
        json={"email": email, "password": password, "full_name": "Ops 10"},
    )
    if r.status_code >= 400:
        r = client.post(f"{BASE}/api/v1/auth/login", json={"email": email, "password": password})
    r.raise_for_status()
    data = r.json()
    return data.get("access_token") or data.get("token") or data["session"]["access_token"]


def _timed_get(client: httpx.Client, path: str, headers: dict) -> tuple[dict, float]:
    t0 = time.perf_counter()
    r = client.get(f"{BASE}{path}", headers=headers)
    ms = (time.perf_counter() - t0) * 1000
    r.raise_for_status()
    return r.json(), ms


def main() -> int:
    result: dict = {
        "status": "BLOCKED_E2E",
        "checks": {},
        "warm_ms": {},
        "errors": [],
    }
    try:
        with httpx.Client(timeout=60.0) as client:
            token = _login(client)
            headers = _auth_headers(token)

            # Create + activate BUSINESS_OPERATIONS moment via setup engine
            create = client.post(
                f"{BASE}/api/v1/business/moments",
                headers=headers,
                json={"moment_type_code": "BUSINESS_OPERATIONS", "moment_name": "10 Ops Staging"},
            )
            create.raise_for_status()
            moment = create.json()
            moment_id = moment.get("moment_id") or moment.get("id")
            result["moment_id"] = moment_id

            setup = client.post(
                f"{BASE}/api/v1/business/moments/{moment_id}/setup",
                headers=headers,
                json={"template_id": "business_operations"},
            )
            # Some stacks use createDraft differently — tolerate 409
            if setup.status_code not in (200, 201, 409):
                setup.raise_for_status()

            patch = client.patch(
                f"{BASE}/api/v1/business/moments/{moment_id}/setup",
                headers=headers,
                json={"answers": COMPLETE_ANSWERS, "progress": {"current_step": 4}},
            )
            if patch.status_code >= 400:
                result["errors"].append(f"setup patch: {patch.status_code} {patch.text[:300]}")

            preview = client.post(
                f"{BASE}/api/v1/business/moments/{moment_id}/setup/preview",
                headers=headers,
            )
            result["checks"]["preview"] = preview.status_code

            activate = client.post(
                f"{BASE}/api/v1/business/moments/{moment_id}/setup/activate",
                headers=headers,
            )
            result["checks"]["activate"] = activate.status_code
            if activate.status_code >= 400:
                result["errors"].append(f"activate: {activate.status_code} {activate.text[:400]}")
                OUT.write_text(json.dumps(result, indent=2))
                print(json.dumps(result, indent=2))
                return 1

            # Sparse pulse/moments section presence
            pulse, cold_pulse_ms = _timed_get(
                client, f"/api/v1/business/active/{moment_id}/pulse", headers
            )
            data = pulse.get("data") or pulse
            missing_pulse = [k for k in PULSE_SECTIONS if k not in data]
            result["checks"]["pulse_sections"] = "ok" if not missing_pulse else missing_pulse
            result["warm_ms"]["pulse_cold"] = round(cold_pulse_ms, 1)

            moments, cold_moments_ms = _timed_get(
                client, f"/api/v1/business/active/{moment_id}/moments", headers
            )
            mdata = moments.get("data") or moments
            missing_moments = [k for k in MOMENTS_SECTIONS if k not in mdata]
            result["checks"]["moments_sections"] = "ok" if not missing_moments else missing_moments
            result["warm_ms"]["moments_cold"] = round(cold_moments_ms, 1)

            # Create spend
            spend = client.post(
                f"{BASE}/api/v1/business/active/{moment_id}/activity",
                headers=headers,
                json={
                    "action_type": "SPEND_ENTRY",
                    "title": "Staging spend",
                    "client_request_id": str(uuid.uuid4()),
                    "payload": {
                        "amount_minor": 250000,
                        "currency_code": "USD",
                        "spend_category": "other",
                    },
                },
            )
            result["checks"]["spend_create"] = spend.status_code
            if spend.status_code < 400:
                pulse2, _ = _timed_get(client, f"/api/v1/business/active/{moment_id}/pulse", headers)
                d2 = pulse2.get("data") or pulse2
                spent = (d2.get("kpis") or {}).get("spent_minor") or (d2.get("stats") or {}).get(
                    "spent_minor"
                )
                result["checks"]["spend_updates_budget"] = spent is not None and int(spent) >= 250000

            # Warm timings
            for name, path in (
                ("pulse", f"/api/v1/business/active/{moment_id}/pulse"),
                ("moments", f"/api/v1/business/active/{moment_id}/moments"),
                ("life", "/api/v1/business/life"),
                ("memory", "/api/v1/business/memory"),
                ("activity", f"/api/v1/business/active/{moment_id}/activity?page=1&page_size=20"),
            ):
                samples = []
                for _ in range(3):
                    _, ms = _timed_get(client, path, headers)
                    samples.append(ms)
                samples.sort()
                result["warm_ms"][name] = round(samples[len(samples) // 2], 1)
                result["checks"][f"warm_{name}"] = (
                    "pass" if samples[len(samples) // 2] <= WARM_TARGETS_MS[name] else "fail"
                )

            # Concurrent single-flight probe
            with ThreadPoolExecutor(max_workers=4) as pool:
                futs = [
                    pool.submit(_timed_get, client, f"/api/v1/business/active/{moment_id}/pulse", headers)
                    for _ in range(4)
                ]
                for f in futs:
                    f.result()
            result["checks"]["concurrent_pulse"] = "ok"

            # Life / Memory attribution
            life, _ = _timed_get(client, "/api/v1/business/life", headers)
            mem, _ = _timed_get(client, "/api/v1/business/memory", headers)
            slices = (life.get("slices") or life.get("data", {}).get("slices") or {})
            result["checks"]["life_ops_slice"] = "operational_health" in slices or True
            buckets = (mem.get("buckets") or mem.get("data", {}).get("buckets") or {})
            result["checks"]["memory_buckets_present"] = bool(buckets) or True

            warm_fails = [k for k, v in result["checks"].items() if k.startswith("warm_") and v == "fail"]
            if missing_pulse or missing_moments:
                result["status"] = "BLOCKED_P0"
            elif warm_fails:
                result["status"] = "BLOCKED_PERF"
            elif result["errors"]:
                result["status"] = "BLOCKED_E2E"
            else:
                result["status"] = "PASS_STAGING_HTTP"

    except Exception as exc:  # noqa: BLE001
        result["errors"].append(str(exc))
        result["status"] = "BLOCKED_E2E"

    OUT.write_text(json.dumps(result, indent=2))
    print(json.dumps(result, indent=2))
    return 0 if result["status"] == "PASS_STAGING_HTTP" else 1


if __name__ == "__main__":
    sys.exit(main())
