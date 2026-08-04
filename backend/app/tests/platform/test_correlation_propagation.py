"""Domain event + Celery enqueue correlation propagation."""
from __future__ import annotations

from dataclasses import asdict
from uuid import uuid4

import pytest

from app.core.request_context import correlation_id_var, request_id_var
from app.domains.moment_engine.handlers.base import enqueue_celery
from app.shared.events.base import DomainEvent
from app.shared.events.publisher import InProcessEventPublisher


@pytest.mark.asyncio
async def test_publisher_stamps_correlation_ids():
    request_id_var.set("req-stamp-12345")
    correlation_id_var.set("corr-stamp-12345")
    published: list[DomainEvent] = []

    async def capture(event: DomainEvent) -> None:
        published.append(event)

    from app.shared.events.bus import EventBus

    bus = EventBus()
    bus.subscribe("test.corr", capture)
    # Temporarily use isolated bus via publisher patch
    from app.shared.events import bus as bus_mod

    prev = bus_mod._bus
    bus_mod._bus = bus
    try:
        pub = InProcessEventPublisher()
        await pub.publish(
            DomainEvent(
                name="test.corr",
                user_id=uuid4(),
                context="PERSONAL",
            )
        )
    finally:
        bus_mod._bus = prev

    assert published
    assert published[0].request_id == "req-stamp-12345"
    assert published[0].correlation_id == "corr-stamp-12345"
    assert "request_id" in asdict(published[0])


def test_enqueue_celery_propagates_headers(monkeypatch):
    request_id_var.set("req-celery-12345")
    correlation_id_var.set("corr-celery-12345")

    captured: dict = {}

    class FakeTask:
        name = "projections.refresh"

        def apply_async(self, args=None, headers=None):
            captured["args"] = args
            captured["headers"] = headers

    class FakeSettings:
        effective_celery_broker = "redis://localhost:6379/0"

    monkeypatch.setattr(
        "app.core.config.settings",
        FakeSettings(),
    )

    enqueue_celery(FakeTask(), "user-1", "LIFE_OPS", source_event_type="moment.updated")
    assert captured.get("headers")
    assert captured["headers"]["source_request_id"] == "req-celery-12345"
    assert captured["headers"]["correlation_id"] == "corr-celery-12345"
    assert captured["headers"]["source_event_type"] == "moment.updated"
    assert "published_at" in captured["headers"]


def test_enqueue_celery_skips_without_broker(monkeypatch):
    class FakeTask:
        name = "projections.refresh"

        def apply_async(self, *a, **k):
            raise AssertionError("should not enqueue")

    class FakeSettings:
        effective_celery_broker = None

    monkeypatch.setattr("app.core.config.settings", FakeSettings())
    enqueue_celery(FakeTask(), "user-1")
