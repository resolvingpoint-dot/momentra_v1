"""Strawberry extensions — security limits, telemetry, session cleanup."""
from __future__ import annotations

import asyncio
import json
import logging
import time
from typing import Any, Iterator

from graphql import GraphQLError
from graphql.language import ast
from strawberry.extensions import (
    DisableIntrospection,
    MaxAliasesLimiter,
    MaxTokensLimiter,
    QueryDepthLimiter,
    SchemaExtension,
)

from app.api.graphql.observability import (
    GraphQLTelemetry,
    count_operations,
    measure_selection_depth,
    sum_connection_first_args,
)
from app.core.config import settings
from app.core.metrics import record_graphql_detail, record_graphql_operation

logger = logging.getLogger(__name__)


def _count_fields(node: Any) -> int:
    total = 0
    if isinstance(node, ast.FieldNode):
        total += 1
        if node.selection_set:
            for sel in node.selection_set.selections:
                total += _count_fields(sel)
    elif isinstance(node, ast.InlineFragmentNode) and node.selection_set:
        for sel in node.selection_set.selections:
            total += _count_fields(sel)
    elif isinstance(node, ast.FragmentSpreadNode):
        total += 1
    elif hasattr(node, "selection_set") and node.selection_set:
        for sel in node.selection_set.selections:
            total += _count_fields(sel)
    return total


def _telemetry(ctx_obj: Any) -> GraphQLTelemetry | None:
    if ctx_obj is None:
        return None
    tel = getattr(ctx_obj, "telemetry", None)
    if tel is None and ctx_obj is not None:
        tel = GraphQLTelemetry()
        try:
            ctx_obj.telemetry = tel
        except Exception:  # noqa: BLE001
            return None
    return tel


class QueryComplexityLimiter(SchemaExtension):
    def on_validate(self) -> Iterator[None]:
        ctx = self.execution_context
        document = ctx.graphql_document
        if document is not None:
            count = 0
            depth = 0
            for definition in document.definitions:
                if isinstance(definition, ast.OperationDefinitionNode):
                    count += _count_fields(definition)
                    depth = max(depth, measure_selection_depth(definition))
            tel = _telemetry(ctx.context)
            if tel is not None:
                tel.complexity = count
                tel.depth = depth
            if count > settings.graphql_max_complexity:
                raise GraphQLError(
                    f"Query is too complex: {count} fields (max {settings.graphql_max_complexity})",
                    extensions={"code": "query_too_complex"},
                )
            ops = count_operations(document)
            if ops > settings.graphql_max_operations:
                raise GraphQLError(
                    f"Too many operations in request: {ops} (max {settings.graphql_max_operations})",
                    extensions={"code": "too_many_operations"},
                )
            nodes = sum_connection_first_args(document)
            if nodes > settings.graphql_max_nodes:
                raise GraphQLError(
                    f"Requested node count too high: {nodes} (max {settings.graphql_max_nodes})",
                    extensions={"code": "too_many_nodes"},
                )
        yield


class QueryTimeoutExtension(SchemaExtension):
    async def on_execute(self):  # type: ignore[no-untyped-def]
        timeout_s = max(0.1, settings.graphql_query_timeout_ms / 1000.0)
        try:
            async with asyncio.timeout(timeout_s):
                yield
        except TimeoutError as exc:
            tel = _telemetry(self.execution_context.context)
            if tel is not None:
                tel.timeout_reason = "query_timeout"
            raise GraphQLError(
                f"Query timed out after {settings.graphql_query_timeout_ms}ms",
                extensions={"code": "query_timeout"},
            ) from exc


class VariableSizeLimiter(SchemaExtension):
    def on_operation(self) -> Iterator[None]:
        ctx = self.execution_context
        variables = getattr(ctx, "variables", None) or {}
        try:
            size = len(json.dumps(variables, default=str).encode("utf-8"))
        except Exception:  # noqa: BLE001
            size = 0
        if size > settings.graphql_max_variable_bytes:
            raise GraphQLError(
                f"Variables payload too large: {size} bytes "
                f"(max {settings.graphql_max_variable_bytes})",
                extensions={"code": "variables_too_large"},
            )
        yield


class GraphQLObservabilityExtension(SchemaExtension):
    def on_operation(self) -> Iterator[None]:
        ctx = self.execution_context
        tel = _telemetry(ctx.context)
        name = getattr(ctx, "operation_name", None) or "anonymous"
        if tel is not None:
            tel.operation_name = str(name) if name else "anonymous"
            principal = getattr(ctx.context, "principal", None)
            if principal is not None:
                tel.principal_id = str(getattr(principal, "user_id", "") or "")
        outcome = "ok"
        start = time.perf_counter()
        try:
            yield
        except Exception:
            outcome = "error"
            raise
        finally:
            duration_ms = (time.perf_counter() - start) * 1000
            result = getattr(ctx, "result", None)
            errors = getattr(result, "errors", None) if result is not None else None
            if errors:
                outcome = "error"
            try:
                record_graphql_operation(str(name), outcome)
                if tel is not None:
                    record_graphql_detail(
                        operation=str(name or "anonymous"),
                        duration_ms=duration_ms,
                        complexity=tel.complexity,
                        depth=tel.depth,
                        apq_status=tel.apq_status,
                        outcome=outcome,
                        sql_count=tel.sql_count,
                        dataloader_batches=tel.dataloader_batches,
                    )
                    logger.info(
                        json.dumps(
                            {
                                "event": "graphql_operation",
                                "request_id": getattr(ctx.context, "request_id", None),
                                "correlation_id": getattr(
                                    ctx.context, "correlation_id", None
                                ),
                                **tel.as_log_dict(),
                                "outcome": outcome,
                            }
                        )
                    )
                    # Attach diagnostic headers when response is available.
                    response = getattr(ctx.context, "response", None)
                    if response is not None:
                        response.headers["X-GraphQL-Operation"] = str(
                            tel.operation_name or "anonymous"
                        )[:64]
                        response.headers["X-GraphQL-Complexity"] = str(tel.complexity)
                        response.headers["X-GraphQL-Depth"] = str(tel.depth)
                        response.headers["X-GraphQL-Duration-Ms"] = str(
                            round(tel.duration_ms(), 2)
                        )
                        response.headers["X-GraphQL-APQ"] = tel.apq_status
            except Exception:  # noqa: BLE001
                logger.debug("graphql observability write failed", exc_info=True)


class SessionCleanupExtension(SchemaExtension):
    async def on_execute(self):  # type: ignore[no-untyped-def]
        try:
            yield
        finally:
            ctx = self.execution_context.context
            if ctx is not None and hasattr(ctx, "db"):
                from app.api.graphql.context import cleanup_graphql_context

                try:
                    await cleanup_graphql_context(ctx)
                except Exception:  # noqa: BLE001
                    logger.exception("GraphQL session cleanup failed")


def build_extensions() -> list[Any]:
    extensions: list[Any] = [
        lambda: QueryDepthLimiter(max_depth=settings.graphql_max_depth),
        QueryComplexityLimiter,
        VariableSizeLimiter,
        lambda: MaxAliasesLimiter(max_alias_count=settings.graphql_max_aliases),
        lambda: MaxTokensLimiter(max_token_count=settings.graphql_max_tokens),
        QueryTimeoutExtension,
        GraphQLObservabilityExtension,
        SessionCleanupExtension,
    ]
    if settings.is_production or settings.graphql_disable_introspection:
        extensions.insert(0, DisableIntrospection)
    return extensions
