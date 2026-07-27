"""Projection pipeline metrics (in-process counters + structured logging helpers)."""
from __future__ import annotations

import json
import logging
import time
from contextlib import contextmanager
from dataclasses import dataclass, field
from typing import Any, Iterator

logger = logging.getLogger(__name__)

_counters: dict[str, int] = {
    "projection_cache_hit": 0,
    "projection_cache_miss": 0,
}
_last_builder_stage: dict[str, Any] = {}


@dataclass
class BuildTimer:
    stages: dict[str, float] = field(default_factory=dict)
    _marks: dict[str, float] = field(default_factory=dict)
    _start: float = field(default_factory=time.perf_counter)

    def mark(self, stage: str) -> None:
        now = time.perf_counter()
        if stage in self._marks:
            self.stages[stage] = self.stages.get(stage, 0.0) + (now - self._marks[stage]) * 1000
        self._marks[stage] = now

    def finish(self, *, final_stage: str = "redis") -> dict[str, float]:
        now = time.perf_counter()
        if final_stage in self._marks:
            self.stages[final_stage] = (
                self.stages.get(final_stage, 0.0) + (now - self._marks[final_stage]) * 1000
            )
        self.stages.setdefault("total", (now - self._start) * 1000)
        return dict(self.stages)

    def log(self, *, reason: str | None = None, size_bytes: int | None = None) -> None:
        payload: dict[str, Any] = {
            "projection_build_ms": round(self.stages.get("total", 0.0), 2),
            "builder_stage": {k: round(v, 2) for k, v in self.stages.items() if k != "total"},
        }
        if reason:
            payload["projection_refresh_reason"] = reason
        if size_bytes is not None:
            payload["projection_size_bytes"] = size_bytes
        global _last_builder_stage
        _last_builder_stage = payload
        logger.info(json.dumps(payload))


@contextmanager
def build_timer() -> Iterator[BuildTimer]:
    timer = BuildTimer()
    timer.mark("timeline")
    yield timer


def record_cache_hit() -> None:
    _counters["projection_cache_hit"] += 1


def record_cache_miss() -> None:
    _counters["projection_cache_miss"] += 1


def get_counters() -> dict[str, int]:
    return dict(_counters)


def get_last_builder_stage() -> dict[str, Any]:
    return dict(_last_builder_stage)


def reset_metrics_for_tests() -> None:
    for key in _counters:
        _counters[key] = 0
    _last_builder_stage.clear()
