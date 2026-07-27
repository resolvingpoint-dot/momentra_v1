#!/usr/bin/env python3
"""Run 9.5 — Business Runway staging verification harness (HTTP only, no UI E2E)."""
from __future__ import annotations

import json
import sys
import time
import uuid
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

import httpx

BASE = "http://127.0.0.1:8000"
OUT = Path(__file__).resolve().parent / "run95_last_result.json"

COMPLETE_ANSWERS = {
    "moment_name": "95c Runway Staging",
    "runway_name": "95c Cash Runway",
    "business_stage": "EARLY_REVENUE",
    "operating_currency_code": "USD",
    "timezone": "America/New_York",
    "locale": "en-US",
    "country_code": "US",
    "runway_goal_months": 12,
    "current_cash_minor": 5000000,
    "monthly_burn_minor": 400000,
    "revenue_status": "EARLY_REVENUE",
    "estimated_monthly_revenue_minor": 100000,
    "runway_alert_threshold_months": 3,
    "burn_categories": ["payroll", "saas"],
    "revenue_model": "SUBSCRIPTION",
    "funding_sources": ["BOOTSTRAPPED"],
    "visibility": "TEAM",
    "invite_on_activation": False,
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
    "runway_health",
    "cash_position",
    "monthly_burn",
    "revenue_trend",
    "collection_rate",
    "runway_months",
    "cash_movement",
    "kpis",
    "forecast",
    "attention_items",
    "trends",
    "signals",
    "recent_activity",
    "next_best_action",
)

MOMENTS_SECTIONS = (
    "journey_hero",
    "cash_available",
    "runway_months",
    "timeline",
    "revenue_updates",
    "forecast_changes",
    "expense_events",
    "inflow_events",
    "funding_events",
    "invoices",
    "payroll",
    "milestones",
    "recent_activity",
)


def login(client: httpx.Client, tag: str) -> dict[str, str]:
    r = client.post(
        "/api/v1/auth/test/login",
        json={"firebase_uid": f"test:95c-{tag}-{uuid.uuid4().hex[:8]}", "display_name": tag},
    )
    r.raise_for_status()
    token = r.json()["tokens"]["access_token"]
    return {"Authorization": f"Bearer {token}"}


def timed_get(client: httpx.Client, path: str, headers: dict, *, bust: bool = False) -> tuple[float, int, str | None]:
    url = path
    if bust:
        sep = "&" if "?" in path else "?"
        url = f"{path}{sep}_bust={int(time.time() * 1000)}"
    t0 = time.perf_counter()
    r = client.get(url, headers=headers)
    ms = (time.perf_counter() - t0) * 1000
    return ms, r.status_code, r.headers.get("X-Cache-Hit")


def measure_surface(
    client: httpx.Client,
    name: str,
    path: str,
    headers: dict,
    *,
    warm_n: int = 15,
) -> dict:
    print(f"  measure {name} cold...", flush=True)
    cold_ms, cold_status, cold_hit = timed_get(client, path, headers, bust=True)
    warms: list[float] = []
    hits = known = 0
    for i in range(warm_n):
        ms, st, hit = timed_get(client, path, headers)
        if st >= 500:
            continue
        warms.append(ms)
        if hit is not None:
            known += 1
            if hit.lower() == "true":
                hits += 1
        if i == 0 or (i + 1) % 5 == 0:
            print(f"  measure {name} warm {i + 1}/{warm_n} ms={ms:.0f} hit={hit}", flush=True)
    warms_s = sorted(warms) if warms else [cold_ms]
    p50 = warms_s[len(warms_s) // 2]
    p95 = warms_s[int((len(warms_s) - 1) * 0.95)] if len(warms_s) > 1 else warms_s[0]
    return {
        "path": path,
        "cold_ms": round(cold_ms, 2),
        "cold_status": cold_status,
        "cold_x_cache_hit": cold_hit,
        "warm_p50_ms": round(p50, 2),
        "warm_p95_ms": round(p95, 2),
        "warm_avg_ms": round(sum(warms) / len(warms), 2) if warms else None,
        "warm_samples": len(warms),
        "cache_hit_rate": round(hits / known, 3) if known else None,
        "cache_hit_known": known,
        "cache_hits": hits,
    }


def main() -> int:
    blockers: list[str] = []
    report: dict = {"run": "9.5", "base_url": BASE}
    print("Run 9.5 runway staging harness starting…", flush=True)

    with httpx.Client(base_url=BASE, timeout=180.0) as client:
        live = client.get("/health/live")
        ready = client.get("/health/ready")
        report["deployment"] = {
            "live_status": live.status_code,
            "ready_status": ready.status_code,
            "ready": ready.json() if ready.status_code == 200 else ready.text,
        }
        print(f"deployment ready={ready.status_code} body={report['deployment'].get('ready')}", flush=True)
        if ready.status_code != 200:
            blockers.append(f"health/ready not 200: {ready.status_code}")
        else:
            body = ready.json()
            for dep in ("database", "redis", "celery"):
                if body.get(dep) != "up":
                    blockers.append(f"{dep} not up: {body.get(dep)}")

        print("login owner…", flush=True)
        owner_h = login(client, "owner")

        print("create BUSINESS_RUNWAY…", flush=True)
        mid = client.post(
            "/api/v1/business/moments",
            headers=owner_h,
            json={"moment_type_code": "BUSINESS_RUNWAY", "title": "95c Runway Staging"},
        ).json()["moment_id"]
        print(f"moment_id={mid}", flush=True)
        client.put(
            f"/api/v1/business/moments/{mid}/setup/draft",
            headers=owner_h,
            json={
                "answers": COMPLETE_ANSWERS,
                "progress": {"current_step": 4, "completed_steps": [1, 2, 3]},
                "template_id": "business_runway",
                "setup_version": "1",
            },
        )
        print("preview…", flush=True)
        prev = client.post(
            f"/api/v1/business/moments/{mid}/setup/preview",
            headers=owner_h,
            json={"answers": COMPLETE_ANSWERS},
        )
        print("activate…", flush=True)
        act = client.post(f"/api/v1/business/moments/{mid}/setup/activate", headers=owner_h)
        print(f"activate status={act.status_code}", flush=True)
        report["e2e_setup"] = {
            "moment_id": mid,
            "preview_ready": prev.json().get("activation_ready") if prev.status_code == 200 else None,
            "activate_status": act.status_code,
            "activate_body_status": act.json().get("status") if act.status_code == 200 else act.text[:200],
        }
        if act.status_code != 200 or act.json().get("status") != "ACTIVE":
            blockers.append(f"activate failed: {act.status_code} {act.text[:120]}")

        paths = {
            "pulse": f"/api/v1/business/active/{mid}/pulse",
            "moments": f"/api/v1/business/active/{mid}/moments",
            "life": "/api/v1/business/life",
            "memory": "/api/v1/business/memory",
            "activity_first_page": f"/api/v1/business/active/{mid}/activity?page=1&page_size=20",
        }

        # Contract spot-check
        print("contract spot-check pulse/moments…", flush=True)
        pulse_r = client.get(paths["pulse"], headers=owner_h)
        moments_r = client.get(paths["moments"], headers=owner_h)
        pulse_body = pulse_r.json() if pulse_r.status_code == 200 else {}
        moments_body = moments_r.json() if moments_r.status_code == 200 else {}
        missing_pulse = [k for k in PULSE_SECTIONS if k not in pulse_body]
        missing_moments = [k for k in MOMENTS_SECTIONS if k not in moments_body]
        report["section_contract"] = {
            "pulse_status": pulse_r.status_code,
            "moments_status": moments_r.status_code,
            "missing_pulse": missing_pulse,
            "missing_moments": missing_moments,
            "cash_available_minor": (pulse_body.get("cash_position") or {}).get("cash_available_minor"),
            "runway_months": (pulse_body.get("runway_months") or {}).get("runway_months"),
            "invoices_state": (moments_body.get("invoices") or {}).get("state"),
            "payroll_state": (moments_body.get("payroll") or {}).get("state"),
        }
        if missing_pulse:
            blockers.append(f"pulse missing sections: {missing_pulse}")
        if missing_moments:
            blockers.append(f"moments missing sections: {missing_moments}")
        cash = report["section_contract"]["cash_available_minor"]
        if cash is not None and cash != 5000000:
            blockers.append(f"cash_available_minor expected 5000000 got {cash}")

        perf: dict = {}
        print("performance warm samples…", flush=True)
        for key, path in paths.items():
            perf[key] = measure_surface(client, key, path, owner_h)
        report["performance"] = perf

        _, st2, h2 = timed_get(client, paths["life"], owner_h)
        report["redis_spot_check"] = {"life_warm_hit": h2, "life_status": st2}
        if st2 == 200 and (h2 or "").lower() != "true" and (perf["life"].get("cache_hit_rate") or 0) < 0.5:
            blockers.append("Redis warm Life X-Cache-Hit weak")

        perf_failures = []
        for surf, limit in WARM_TARGETS_MS.items():
            key = "activity_first_page" if surf == "activity" else surf
            row = perf.get(key, {})
            p50 = row.get("warm_p50_ms")
            if p50 is not None and p50 >= limit:
                perf_failures.append(f"warm {surf} p50={p50}ms not <{limit}ms")
        report["performance_targets"] = {"failures": perf_failures, "met": not perf_failures}
        if perf_failures:
            blockers.extend(perf_failures)

        # Activity CRUD — runway cash inflow
        print("activity CRUD…", flush=True)
        t0 = time.perf_counter()
        cr = client.post(
            f"/api/v1/business/active/{mid}/activity",
            headers=owner_h,
            json={
                "action_type": "CASH_INFLOW",
                "title": "95c funding",
                "payload": {
                    "amount_minor": 100000,
                    "inflow_type": "investor_funding",
                    "inflow_date": "2026-07-16",
                },
                "source": "action_center",
                "client_request_id": str(uuid.uuid4()),
            },
        )
        create_ms = round((time.perf_counter() - t0) * 1000, 2)
        eid = None
        patch_st = delete_st = None
        if cr.status_code < 300:
            eid = cr.json().get("event_id") or cr.json().get("id")
        if eid:
            pr = client.patch(
                f"/api/v1/business/active/{mid}/activity/{eid}",
                headers=owner_h,
                json={"title": "95c funding edited"},
            )
            patch_st = pr.status_code
            dr = client.delete(f"/api/v1/business/active/{mid}/activity/{eid}", headers=owner_h)
            delete_st = dr.status_code

        for at, title, payload in (
            ("EXPENSE_BURN", "95c burn", {"amount_minor": 50000, "expense_category": "salaries", "expense_date": "2026-07-16"}),
            ("RUNWAY_RISK", "95c risk", {"title": "95c risk", "severity": "medium"}),
            ("FINANCIAL_UPDATE", "95c forecast", {"update_type": "revenue_estimate", "reason": "staging", "amount_minor": 120000}),
        ):
            client.post(
                f"/api/v1/business/active/{mid}/activity",
                headers=owner_h,
                json={
                    "action_type": at,
                    "title": title,
                    "payload": payload,
                    "source": "action_center",
                    "client_request_id": str(uuid.uuid4()),
                },
            )

        time.sleep(0.3)
        _, pulse_after_st, pulse_after_hit = timed_get(client, paths["pulse"], owner_h)
        report["activity_crud"] = {
            "create_status": cr.status_code,
            "create_ms": create_ms,
            "patch_status": patch_st,
            "delete_status": delete_st,
            "pulse_after_mutation_cache": pulse_after_hit,
            "pulse_after_mutation_status": pulse_after_st,
        }
        if cr.status_code >= 400:
            blockers.append(f"activity create failed: {cr.status_code} {cr.text[:120]}")

        print("observer permission…", flush=True)
        obs_h = login(client, "observer")
        den = client.post(
            f"/api/v1/business/active/{mid}/activity",
            headers=obs_h,
            json={
                "action_type": "CASH_INFLOW",
                "title": "nope",
                "payload": {"amount_minor": 1, "inflow_type": "other", "inflow_date": "2026-07-16"},
                "source": "action_center",
            },
        )
        report["permissions"] = {"observer_create_status": den.status_code}
        if den.status_code != 403:
            blockers.append(f"observer create expected 403 got {den.status_code}")

        print("archive lifecycle…", flush=True)
        arc = client.post(f"/api/v1/business/moments/{mid}/archive", headers=owner_h)
        report["lifecycle"] = {
            "archive_status": arc.status_code,
            "archive_body": arc.text[:300],
        }
        if arc.status_code != 200:
            blockers.append(f"archive failed: {arc.status_code}")
        elif arc.json().get("status") != "ARCHIVED":
            blockers.append(f"archive status not ARCHIVED: {arc.json().get('status')}")

        print("parallel pulse ×10…", flush=True)
        def one_pulse(_: int) -> tuple[float, int, str | None]:
            return timed_get(client, paths["pulse"], owner_h)

        with ThreadPoolExecutor(10) as ex:
            outs = list(ex.map(one_pulse, range(10)))
        latencies = sorted(x[0] for x in outs)
        report["parallel_pulse"] = {
            "n": 10,
            "p50_ms": round(latencies[5], 2),
            "p95_ms": round(latencies[8], 2),
            "x_cache_hit_true": sum(1 for x in outs if (x[2] or "").lower() == "true"),
        }

        print("parallel moments ×10…", flush=True)
        def one_moments(_: int) -> tuple[float, int, str | None]:
            return timed_get(client, paths["moments"], owner_h)

        with ThreadPoolExecutor(10) as ex:
            mout = list(ex.map(one_moments, range(10)))
        mlat = sorted(x[0] for x in mout)
        report["parallel_moments"] = {
            "n": 10,
            "p50_ms": round(mlat[5], 2),
            "p95_ms": round(mlat[8], 2),
            "x_cache_hit_true": sum(1 for x in mout if (x[2] or "").lower() == "true"),
        }

    report["gaps"] = {
        "web_ui_e2e": "NOT_RUN",
        "android_ui_e2e": "NOT_RUN",
        "ios_ui_e2e": "NOT_RUN",
        "ios_simulator_smoke": "PENDING",
    }
    for gap in ("web_ui_e2e", "android_ui_e2e", "ios_ui_e2e", "ios_simulator_smoke"):
        blockers.append(f"{gap}: NOT_RUN")

    decision = "COMPLETE" if not blockers else "BLOCKED"
    payload = {
        **report,
        "blockers": blockers,
        "decision": decision,
    }
    OUT.write_text(json.dumps(payload, indent=2), encoding="utf-8")
    print(json.dumps({"decision": decision, "blockers": blockers}, indent=2))
    print(f"Wrote {OUT}")
    return 0 if decision == "COMPLETE" else 1


if __name__ == "__main__":
    sys.exit(main())
