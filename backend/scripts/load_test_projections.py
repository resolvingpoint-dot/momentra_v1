#!/usr/bin/env python3
"""Smoke load test for projection GET endpoints (warm in-memory/Redis cache)."""
from __future__ import annotations

import argparse
import statistics
import time

import httpx

AUTH = {"Authorization": "Bearer fake-token"}


def main() -> None:
    parser = argparse.ArgumentParser(description="Projection endpoint load smoke test")
    parser.add_argument("--base-url", default="http://127.0.0.1:8000")
    parser.add_argument("--requests", type=int, default=20)
    args = parser.parse_args()

    paths = [
        "/api/v1/personal/pulse",
        "/api/v1/personal/life",
        "/api/v1/personal/templates/LIFE_OPERATIONS/memory",
        "/api/v1/personal/templates/LIFE_OPERATIONS/pulse",
    ]
    timings: dict[str, list[float]] = {p: [] for p in paths}

    with httpx.Client(base_url=args.base_url, timeout=30.0) as client:
        for path in paths:
            for _ in range(args.requests):
                start = time.perf_counter()
                resp = client.get(path, headers=AUTH)
                elapsed_ms = (time.perf_counter() - start) * 1000
                timings[path].append(elapsed_ms)
                cache_hit = resp.headers.get("X-Cache-Hit", "?")
                print(f"{path} {resp.status_code} {elapsed_ms:.0f}ms cache={cache_hit}")

    print("\nSummary (ms):")
    for path, samples in timings.items():
        if not samples:
            continue
        print(
            f"  {path}: p50={statistics.median(samples):.0f} "
            f"p95={sorted(samples)[int(len(samples) * 0.95) - 1]:.0f} "
            f"max={max(samples):.0f}"
        )


if __name__ == "__main__":
    main()
