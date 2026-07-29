"""Per-request GraphQL telemetry for diagnostics and Prometheus."""
from __future__ import annotations

import time
from collections import defaultdict
from dataclasses import dataclass, field
from typing import Any


@dataclass
class GraphQLTelemetry:
    operation_name: str | None = None
    complexity: int = 0
    depth: int = 0
    started_at: float = field(default_factory=time.perf_counter)
    resolver_ms: dict[str, float] = field(default_factory=dict)
    sql_count: int = 0
    sql_ms: float = 0.0
    redis_count: int = 0
    redis_ms: float = 0.0
    dataloader_batches: int = 0
    cache_hits: int = 0
    cache_misses: int = 0
    apq_status: str = "bypass"  # hit|miss|store|bypass|required
    timeout_reason: str | None = None
    cancellation_reason: str | None = None
    principal_id: str | None = None

    def record_resolver(self, name: str, duration_ms: float) -> None:
        self.resolver_ms[name] = self.resolver_ms.get(name, 0.0) + duration_ms

    def duration_ms(self) -> float:
        return (time.perf_counter() - self.started_at) * 1000

    def cache_hit_ratio(self) -> float:
        total = self.cache_hits + self.cache_misses
        if total <= 0:
            return 0.0
        return self.cache_hits / total

    def as_log_dict(self) -> dict[str, Any]:
        return {
            "operation_name": self.operation_name or "anonymous",
            "complexity": self.complexity,
            "depth": self.depth,
            "duration_ms": round(self.duration_ms(), 2),
            "sql_count": self.sql_count,
            "sql_ms": round(self.sql_ms, 2),
            "redis_count": self.redis_count,
            "redis_ms": round(self.redis_ms, 2),
            "dataloader_batches": self.dataloader_batches,
            "cache_hit_ratio": round(self.cache_hit_ratio(), 3),
            "apq_status": self.apq_status,
            "timeout_reason": self.timeout_reason,
            "principal_id": self.principal_id,
            "resolver_ms": {k: round(v, 2) for k, v in self.resolver_ms.items()},
        }


_FIELD_DEPTH: dict[str, int] = defaultdict(int)


def measure_selection_depth(node: Any, depth: int = 0) -> int:
    from graphql.language import ast

    max_d = depth
    if isinstance(node, ast.FieldNode):
        max_d = max(max_d, depth)
        if node.selection_set:
            for sel in node.selection_set.selections:
                max_d = max(max_d, measure_selection_depth(sel, depth + 1))
    elif isinstance(node, ast.InlineFragmentNode) and node.selection_set:
        for sel in node.selection_set.selections:
            max_d = max(max_d, measure_selection_depth(sel, depth))
    elif hasattr(node, "selection_set") and node.selection_set:
        for sel in node.selection_set.selections:
            max_d = max(max_d, measure_selection_depth(sel, depth))
    return max_d


def count_operations(document: Any) -> int:
    from graphql.language import ast

    if document is None:
        return 0
    return sum(
        1
        for d in document.definitions
        if isinstance(d, ast.OperationDefinitionNode)
    )


def sum_connection_first_args(document: Any) -> int:
    """Sum numeric ``first`` arguments across the document (proxy for node budget)."""
    from graphql.language import ast

    total = 0
    if document is None:
        return 0

    def walk(node: Any) -> None:
        nonlocal total
        if isinstance(node, ast.FieldNode):
            for arg in node.arguments or []:
                if arg.name.value == "first" and isinstance(
                    arg.value, ast.IntValueNode
                ):
                    total += int(arg.value.value)
            if node.selection_set:
                for sel in node.selection_set.selections:
                    walk(sel)
        elif isinstance(node, ast.InlineFragmentNode) and node.selection_set:
            for sel in node.selection_set.selections:
                walk(sel)
        elif hasattr(node, "selection_set") and node.selection_set:
            for sel in node.selection_set.selections:
                walk(sel)

    for definition in document.definitions:
        if isinstance(definition, ast.OperationDefinitionNode):
            walk(definition)
    return total
