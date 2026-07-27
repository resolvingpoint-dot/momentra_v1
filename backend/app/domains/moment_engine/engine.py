from __future__ import annotations

from datetime import datetime, timezone
from typing import Any
from uuid import UUID

from app.domains.moment_engine import events as ev
from app.domains.moment_engine.adapters import MomentAdapter, MomentRef
from app.domains.moment_engine.state import (
    ACTIVE,
    ARCHIVED,
    COMPLETED,
    DRAFT,
    PAUSED,
    assert_transition,
)
from app.core.errors import StateTransitionError
from app.domains.moment_engine.templates import MomentTemplate
from app.domains.moment_engine.registry import DomainRegistry, get_domain_registry
from app.shared.events.publisher import EventPublisher, get_event_publisher


def _now() -> datetime:
    return datetime.now(timezone.utc)


class MomentEngine:
    """Orchestrates moment lifecycle transitions and publishes domain events."""

    def __init__(
        self,
        publisher: EventPublisher | None = None,
        domains: DomainRegistry | None = None,
    ) -> None:
        self.publisher = publisher or get_event_publisher()
        self.domains = domains or get_domain_registry()

    def _template(self, context: str, moment_type: str | None) -> MomentTemplate:
        return self.domains.resolve_template(context, moment_type)

    @staticmethod
    def _event_payload(adapter: MomentAdapter, **extra: Any) -> dict[str, Any]:
        """Attach the request-scoped session for in-process sync handlers."""
        session = getattr(adapter, "session", None)
        payload = dict(extra)
        if session is not None:
            payload["session"] = session
        return payload

    async def create(
        self,
        adapter: MomentAdapter,
        user_id: UUID,
        *,
        moment_type: str | None,
        title: str | None = None,
        description: str | None = None,
        setup_state: str | None = None,
        **extra: Any,
    ) -> MomentRef:
        template = self._template(adapter.context, moment_type)
        resolved_setup = setup_state or (
            "ACTIVE" if title else template.initial_setup_state
        )
        ref = await adapter.create(
            user_id,
            moment_type=moment_type,
            title=title,
            description=description,
            status=template.initial_status,
            setup_state=resolved_setup,
            **{**template.extra_create_defaults, **extra},
        )
        await self.publisher.publish(
            ev.moment_created(
                user_id=user_id,
                moment_id=ref.moment_id,
                context=ref.context,
                moment_type=ref.moment_type,
                **self._event_payload(
                    adapter,
                    refresh=template.refresh_on_create,
                    worker_context=template.worker_context,
                    setup_state=ref.setup_state,
                ),
            )
        )
        return ref

    async def update(
        self,
        adapter: MomentAdapter,
        user_id: UUID,
        moment_id: UUID,
        **fields: Any,
    ) -> MomentRef:
        before = await adapter.get_owned(user_id, moment_id)
        ref = await adapter.update_fields(user_id, moment_id, **fields)
        template = self._template(ref.context, ref.moment_type)
        await self.publisher.publish(
            ev.moment_updated(
                user_id=user_id,
                moment_id=ref.moment_id,
                context=ref.context,
                moment_type=ref.moment_type,
                **self._event_payload(
                    adapter,
                    refresh=template.refresh_on_update,
                    worker_context=template.worker_context,
                    changes=list(fields.keys()),
                    previous_status=before.status,
                ),
            )
        )
        return ref

    async def activate(
        self,
        adapter: MomentAdapter,
        user_id: UUID,
        moment_id: UUID,
        *,
        setup_state: str | None = "ACTIVE",
    ) -> MomentRef:
        ref = await adapter.get_owned(user_id, moment_id)
        assert_transition(ref.status, ACTIVE)
        now = _now()
        updates: dict[str, Any] = {"status": ACTIVE, "updated_at": now}
        if setup_state is not None:
            updates["setup_state"] = setup_state
        ref = await adapter.update_fields(user_id, moment_id, **updates)
        template = self._template(ref.context, ref.moment_type)
        await self.publisher.publish(
            ev.moment_activated(
                user_id=user_id,
                moment_id=ref.moment_id,
                context=ref.context,
                moment_type=ref.moment_type,
                activated_at=now,
                **self._event_payload(
                    adapter,
                    refresh=template.refresh_on_activate,
                    worker_context=template.worker_context,
                ),
            )
        )
        return ref

    async def pause(
        self,
        adapter: MomentAdapter,
        user_id: UUID,
        moment_id: UUID,
    ) -> MomentRef:
        ref = await adapter.get_owned(user_id, moment_id)
        assert_transition(ref.status, PAUSED)
        ref = await adapter.update_fields(
            user_id, moment_id, status=PAUSED, updated_at=_now()
        )
        template = self._template(ref.context, ref.moment_type)
        await self.publisher.publish(
            ev.moment_paused(
                user_id=user_id,
                moment_id=ref.moment_id,
                context=ref.context,
                moment_type=ref.moment_type,
                **self._event_payload(
                    adapter,
                    refresh=template.refresh_on_pause,
                    worker_context=template.worker_context,
                ),
            )
        )
        return ref

    async def complete(
        self,
        adapter: MomentAdapter,
        user_id: UUID,
        moment_id: UUID,
    ) -> MomentRef:
        ref = await adapter.get_owned(user_id, moment_id)
        assert_transition(ref.status, COMPLETED)
        ref = await adapter.update_fields(
            user_id, moment_id, status=COMPLETED, updated_at=_now()
        )
        template = self._template(ref.context, ref.moment_type)
        await self.publisher.publish(
            ev.moment_completed(
                user_id=user_id,
                moment_id=ref.moment_id,
                context=ref.context,
                moment_type=ref.moment_type,
                **self._event_payload(
                    adapter,
                    refresh=template.refresh_on_complete,
                    worker_context=template.worker_context,
                ),
            )
        )
        return ref

    async def archive(
        self,
        adapter: MomentAdapter,
        user_id: UUID,
        moment_id: UUID,
    ) -> MomentRef:
        ref = await adapter.get_owned(user_id, moment_id)
        assert_transition(ref.status, ARCHIVED)
        ref = await adapter.update_fields(
            user_id, moment_id, status=ARCHIVED, updated_at=_now()
        )
        template = self._template(ref.context, ref.moment_type)
        await self.publisher.publish(
            ev.moment_archived(
                user_id=user_id,
                moment_id=ref.moment_id,
                context=ref.context,
                moment_type=ref.moment_type,
                **self._event_payload(
                    adapter,
                    refresh=template.refresh_on_archive,
                    worker_context=template.worker_context,
                ),
            )
        )
        return ref

    async def delete(
        self,
        adapter: MomentAdapter,
        user_id: UUID,
        moment_id: UUID,
    ) -> None:
        ref = await adapter.get_owned(user_id, moment_id)
        if ref.status != DRAFT:
            raise StateTransitionError("Only DRAFT moments can be deleted")
        context = ref.context
        moment_type = ref.moment_type
        await adapter.delete(user_id, moment_id)
        await self.publisher.publish(
            ev.moment_deleted(
                user_id=user_id,
                moment_id=moment_id,
                context=context,
                moment_type=moment_type,
                **self._event_payload(adapter),
            )
        )

    async def transition_status(
        self,
        adapter: MomentAdapter,
        user_id: UUID,
        moment_id: UUID,
        to_status: str,
        *,
        setup_state: str | None = None,
    ) -> MomentRef:
        """Route a status change to the appropriate lifecycle method."""
        if to_status == ACTIVE:
            return await self.activate(
                adapter, user_id, moment_id, setup_state=setup_state
            )
        if to_status == PAUSED:
            return await self.pause(adapter, user_id, moment_id)
        if to_status == COMPLETED:
            return await self.complete(adapter, user_id, moment_id)
        if to_status == ARCHIVED:
            return await self.archive(adapter, user_id, moment_id)
        if to_status == DRAFT:
            ref = await adapter.get_owned(user_id, moment_id)
            assert_transition(ref.status, DRAFT)
            return await self.update(adapter, user_id, moment_id, status=DRAFT)
        raise ValueError(f"Unsupported target status {to_status!r}")
