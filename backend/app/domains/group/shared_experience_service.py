"""Canonical Shared Experience service — projection + activity driven."""
from __future__ import annotations

from typing import Any
from uuid import UUID

from fastapi import HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.domains.group import moment_store as store
from app.domains.group import shared_experience_schemas as t
from app.domains.group.activity.engine import GroupActivityEngine
from app.domains.group.activity.types import ActivityType, collection_for
from app.domains.group.projection_cache import invalidate_group_projections
from app.domains.group.projection_read import cached_or_build
from app.domains.group.templates.shared_experience.live_hub_mapper import build_live_hub
from app.domains.group.templates.shared_experience.memory_mapper import build_memory_list, build_memory_projection
from app.domains.group.templates.shared_experience.moments_mapper import build_moments
from app.domains.group.templates.shared_experience.projection_builder import SharedExperienceProjectionBuilder
from app.domains.group.templates.shared_experience.projection_helpers import relative_time_label
from app.domains.group.templates.shared_experience.pulse_mapper import build_pulse
from app.domains.group.templates.shared_experience.life_mapper import build_life
from app.domains.moments.models import MomentModel
from app.domains.moments.repository import MomentRepository

MOMENT_TYPE = "SHARED_EXPERIENCE"
_ACTIVITY_PATCH_KEYS = frozenset({"title", "subtitle", "occurred_at"})


class SharedExperienceService:
    def __init__(self, session: AsyncSession) -> None:
        self.session = session
        self.moments = MomentRepository(session)
        self.builder = SharedExperienceProjectionBuilder(session)
        self.activity = GroupActivityEngine(session)

    async def _require(self, user_id: UUID, moment_id: UUID) -> MomentModel:
        from app.domains.group.access import require_group_moment_access

        return await require_group_moment_access(self.session, user_id, moment_id)

    async def assert_access(self, user_id: UUID, moment_id: UUID) -> MomentModel:
        """Lightweight membership check for SSE / streaming endpoints."""
        return await self._require(user_id, moment_id)

    async def _cached_or_build(
        self,
        user_id: UUID,
        moment_id: UUID,
        slice_type: str,
        builder_fn,
        *,
        moment_type: str = MOMENT_TYPE,
        force_refresh: bool = False,
    ) -> dict:
        async def build() -> dict:
            ctx = await self.builder.build(user_id, moment_id)
            return builder_fn(ctx)

        return await cached_or_build(
            user_id,
            moment_id,
            slice_type,
            build,
            moment_type=moment_type,
            force_refresh=force_refresh,
        )

    async def live_hub(
        self, user_id: UUID, moment_id: UUID, *, force_refresh: bool = False
    ) -> dict:
        moment = await self._require(user_id, moment_id)
        mt = moment.moment_type or MOMENT_TYPE
        return await self._cached_or_build(
            user_id, moment_id, "live_hub", build_live_hub, moment_type=mt, force_refresh=force_refresh
        )

    async def pulse(
        self, user_id: UUID, moment_id: UUID, *, force_refresh: bool = False
    ) -> dict:
        moment = await self._require(user_id, moment_id)
        mt = moment.moment_type or MOMENT_TYPE
        return await self._cached_or_build(
            user_id, moment_id, "pulse", build_pulse, moment_type=mt, force_refresh=force_refresh
        )

    async def moments_view(
        self, user_id: UUID, moment_id: UUID, *, force_refresh: bool = False
    ) -> dict:
        moment = await self._require(user_id, moment_id)
        mt = moment.moment_type or MOMENT_TYPE
        return await self._cached_or_build(
            user_id, moment_id, "moments", build_moments, moment_type=mt, force_refresh=force_refresh
        )

    async def life(
        self, user_id: UUID, moment_id: UUID, *, force_refresh: bool = False
    ) -> dict:
        moment = await self._require(user_id, moment_id)
        mt = moment.moment_type or MOMENT_TYPE
        return await self._cached_or_build(
            user_id, moment_id, "life", build_life, moment_type=mt, force_refresh=force_refresh
        )

    async def memory_projection(
        self, user_id: UUID, moment_id: UUID, *, force_refresh: bool = False
    ) -> dict:
        moment = await self._require(user_id, moment_id)
        mt = moment.moment_type or MOMENT_TYPE
        return await self._cached_or_build(
            user_id,
            moment_id,
            "memory",
            build_memory_projection,
            moment_type=mt,
            force_refresh=force_refresh,
        )

    async def create_memory(
        self, user_id: UUID, moment_id: UUID, body: t.GroupMomentMemoryCreateRequest
    ) -> dict:
        payload: dict[str, Any] = {
            "title": body.title,
            "note": body.note,
            "media_storage_paths": body.media_storage_paths,
        }
        if body.memory_format:
            payload["memory_format"] = body.memory_format
        if body.memory_category:
            payload["memory_category"] = body.memory_category
        row = await self.activity.write(
            user_id,
            moment_id,
            ActivityType.MEMORY,
            payload,
        )
        return t.GroupMomentMemoryResponse(
            id=row["id"],
            moment_id=str(moment_id),
            created_by_user_id=str(user_id),
            created_by_name="You",
            title=body.title,
            note=body.note,
            created_at=row["created_at"],
        ).model_dump(mode="json")

    async def list_memories(self, user_id: UUID, moment_id: UUID) -> list[dict]:
        proj = await self.memory_projection(user_id, moment_id)
        items = proj.get("items") or proj.get("memories")
        if isinstance(items, list):
            return items
        moment = await self._require(user_id, moment_id)
        ctx = self.builder.build_from_moment(moment)
        return build_memory_list(ctx)

    @staticmethod
    def serialize_activity(item: dict[str, Any]) -> dict[str, Any]:
        activity_type = str(item.get("activity_type") or "UPDATE")
        return {
            "id": str(item.get("id") or ""),
            "activity_type": activity_type,
            "ref_id": item.get("ref_id"),
            "title": str(item.get("title") or ""),
            "subtitle": str(item.get("subtitle") or ""),
            "icon": str(item.get("icon") or "history"),
            "occurred_at": str(item.get("occurred_at") or ""),
            "relative_time": relative_time_label(item.get("occurred_at")),
            "edit_event_type": activity_type,
            "can_edit": True,
            "can_delete": True,
        }

    async def list_activity(self, user_id: UUID, moment_id: UUID) -> dict[str, Any]:
        rows = await self.activity.list_timeline(user_id, moment_id)
        items = [self.serialize_activity(row) for row in rows]
        return {
            "moment_id": str(moment_id),
            "items": items,
            "summary": {"total": len(items)},
        }

    async def get_activity(self, user_id: UUID, moment_id: UUID, event_id: str) -> dict[str, Any]:
        moment = await self._require(user_id, moment_id)
        match = self.activity._find_timeline_item(moment, event_id)
        if match is None:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Activity not found")
        await self.session.flush()
        return self.serialize_activity(match)

    async def patch_activity(
        self,
        user_id: UUID,
        moment_id: UUID,
        event_id: str,
        patch: dict[str, Any],
    ) -> dict[str, Any]:
        allowed = {
            key: value
            for key, value in (patch or {}).items()
            if key in _ACTIVITY_PATCH_KEYS and value is not None
        }
        if not allowed:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="No editable fields provided (title, subtitle, occurred_at)",
            )
        updated = await self.activity.patch_activity(user_id, moment_id, event_id, allowed)
        moment = await self._require(user_id, moment_id)
        self._mirror_patch_to_collection(moment, updated, allowed)
        await self.session.flush()
        await invalidate_group_projections(
            user_id,
            moment_id,
            moment_type=moment.moment_type or MOMENT_TYPE,
            reason="activity:patch_mirror",
        )
        return self.serialize_activity(updated)

    async def delete_activity(
        self, user_id: UUID, moment_id: UUID, event_id: str
    ) -> dict[str, Any]:
        return await self.activity.delete_activity(user_id, moment_id, event_id)

    @staticmethod
    def _mirror_patch_to_collection(
        moment: MomentModel,
        timeline_item: dict[str, Any],
        patch: dict[str, Any],
    ) -> None:
        ref_id = timeline_item.get("ref_id")
        activity_type = timeline_item.get("activity_type")
        if not ref_id or not activity_type:
            return
        try:
            collection = collection_for(ActivityType(str(activity_type)))
        except ValueError:
            return
        state = store.read_state(moment)
        items = state["runtime"].get(collection, [])
        for item in items:
            if str(item.get("id")) != str(ref_id) or item.get("deleted"):
                continue
            if "title" in patch:
                title = str(patch["title"])
                item["title"] = title
                if "name" in item:
                    item["name"] = title
                if "description" in item:
                    item["description"] = title
                if "body" in item:
                    item["body"] = title
                if "question" in item:
                    item["question"] = title
            if "subtitle" in patch:
                item["subtitle"] = str(patch["subtitle"])
            break
        store.write_state(moment, state)

    async def invalidate(self, user_id: UUID, moment_id: UUID, *, reason: str = "manual") -> None:
        moment = await self._require(user_id, moment_id)
        await invalidate_group_projections(
            user_id,
            moment_id,
            moment_type=moment.moment_type or MOMENT_TYPE,
            reason=reason,
        )
