#!/usr/bin/env python3
"""Group projection hard-gate smoke test (parallel Pulse + warm cache-hit).

Usage:
  python scripts/load_test_group_projections.py \\
    --base-url http://127.0.0.1:8000 \\
    --token "$TOKEN" \\
    --moment-id <uuid>

Hard gates (warm): Pulse <150ms, Moments/Memory/Life <200ms.
Parallel 10× Pulse should produce a single build (X-Cache-Hit true on later requests).
"""
from __future__ import annotations

import argparse
import concurrent.futures
import statistics
import time

import httpx


def _pct(samples: list[float], p: float) -> float:
    if not samples:
        return 0.0
    ordered = sorted(samples)
    idx = min(len(ordered) - 1, max(0, int(len(ordered) * p) - 1))
    return ordered[idx]


def timed_get(client: httpx.Client, path: str, headers: dict[str, str]) -> tuple[int, float, str]:
    start = time.perf_counter()
    resp = client.get(path, headers=headers)
    elapsed_ms = (time.perf_counter() - start) * 1000
    return resp.status_code, elapsed_ms, resp.headers.get("X-Cache-Hit", "?")


def main() -> None:
    parser = argparse.ArgumentParser(description="Group projection hard-gate smoke test")
    parser.add_argument("--base-url", default="http://127.0.0.1:8000")
    parser.add_argument("--token", required=True)
    parser.add_argument("--moment-id", required=True)
    parser.add_argument("--warm-requests", type=int, default=20)
    parser.add_argument("--parallel", type=int, default=10)
    args = parser.parse_args()

    headers = {"Authorization": f"Bearer {args.token}"}
    mid = args.moment_id
    paths = {
        "Pulse": f"/api/v1/group/trips/{mid}/pulse",
        "Moments": f"/api/v1/group/trips/{mid}/moments-view",
        "Memory": f"/api/v1/group/active/memory/{mid}",
        "ActivePulse": f"/api/v1/group/active/pulse/{mid}",
        "Life": "/api/v1/group/life",
    }
    gates_warm = {"Pulse": 150, "ActivePulse": 150, "Moments": 200, "Memory": 200, "Life": 200}

    with httpx.Client(base_url=args.base_url, timeout=60.0) as client:
        print("=== Cold / first build ===")
        cold: dict[str, float] = {}
        for name, path in paths.items():
            status, ms, hit = timed_get(client, path, headers)
            cold[name] = ms
            print(f"  {name}: {status} {ms:.0f}ms cache={hit}")

        print(f"\n=== Parallel Pulse ×{args.parallel} ===")
        pulse_path = paths["Pulse"]

        def _one(_: int) -> tuple[int, float, str]:
            with httpx.Client(base_url=args.base_url, timeout=60.0) as c:
                return timed_get(c, pulse_path, headers)

        with concurrent.futures.ThreadPoolExecutor(max_workers=args.parallel) as pool:
            parallel_results = list(pool.map(_one, range(args.parallel)))
        for i, (status, ms, hit) in enumerate(parallel_results):
            print(f"  [{i}] {status} {ms:.0f}ms cache={hit}")
        hits = sum(1 for _, _, h in parallel_results if h.lower() == "true")
        print(f"  cache-hit count: {hits}/{args.parallel}")

        print(f"\n=== Warm ×{args.warm_requests} ===")
        warm: dict[str, list[float]] = {k: [] for k in paths}
        hit_rates: dict[str, list[bool]] = {k: [] for k in paths}
        for name, path in paths.items():
            for _ in range(args.warm_requests):
                status, ms, hit = timed_get(client, path, headers)
                warm[name].append(ms)
                hit_rates[name].append(hit.lower() == "true")
            samples = warm[name]
            hr = sum(hit_rates[name]) / max(1, len(hit_rates[name]))
            gate = gates_warm.get(name)
            p50 = statistics.median(samples)
            p95 = _pct(samples, 0.95)
            ok = gate is None or p50 < gate
            flag = "PASS" if ok else "FAIL"
            print(
                f"  {name}: p50={p50:.0f} p95={p95:.0f} max={max(samples):.0f} "
                f"hit_rate={hr:.0%} gate<{gate}ms → {flag}"
            )

    print("\n=== Report snippet ===")
    for name in ("Pulse", "Moments", "Memory", "Life"):
        print(f"Before: {name} cold (audit) / warm (hard-delete)")
        print(
            f"After:  {name} cold {cold.get(name, 0):.0f}ms / "
            f"warm {statistics.median(warm[name]):.0f}ms"
        )


if __name__ == "__main__":
    main()
