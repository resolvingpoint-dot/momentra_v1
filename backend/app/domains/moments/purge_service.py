"""Permanent moment purge — clear operational data, keep analytics, tombstone UUID.

Chosen approach (see plan): keep ``moments.id`` as an analytics anchor with
``status=DELETED``, strip PII/runtime JSON, exit all members, and best-effort
delete operational child rows. Analytics / audit tables are intentionally
left untouched.
"""
from __future__ import annotations

import logging
from datetime import datetime, timezone
from uuid import UUID

from sqlalchemy import delete, select, text
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.errors import NotFoundError, PermissionDeniedError
from app.domains.group import moment_store as group_store
from app.domains.group.models import GroupMomentMembers, GroupMoments
from app.domains.moment_engine import events as ev
from app.domains.moment_engine.state import DELETED, assert_transition
from app.domains.moments.models import MomentMediaModel, MomentModel
from app.shared.events.publisher import get_event_publisher

logger = logging.getLogger(__name__)

# Operational tables keyed by moment_id — analytics tables intentionally omitted.
_GROUP_OPS_TABLES = (
    "group_expense_splits",
    "group_expenses",
    "group_contributions",
    "group_poll_votes",
    "group_polls",
    "group_attendance",
    "group_updates",
    "group_live_feed",
    "group_moment_work_items",
    "group_moment_resources",
    "group_decisions",
    "group_attachments",
    "group_quick_add_events",
    "group_activity_edits",
    "group_recommendations",
    "group_signals",
    "group_change_history",
    "group_people_impact_scores",
    "group_life_moment_links",
    "shared_experience_budget_splits",
    "shared_experience_planning_items",
    "shared_experience_settlements",
    "shared_living_maintenance",
    "shared_living_tasks",
    "shared_living_rules",
    "shared_living_assets",
    "shared_living_residents",
    "shared_living_resident_dynamics",
    "shared_purchase_delivery",
    "shared_purchase_ownership",
    "shared_purchase_contributors",
    "shared_purchase_items",
    "shared_goal_details",
    "community_coordination_details",
)

_PERSONAL_OPS_TABLES = (
    "personal_activity_timeline",
    "personal_event_edits",
    "personal_event_voids",
    "personal_quick_add_events",
    "personal_recommendations",
    "personal_signals",
    "personal_live_priorities",
    "personal_notification_queue",
    "personal_runtime_snapshots",
    "personal_insights",
    "personal_ai_interpretation_runs",
    "personal_future_building_profile",
    "personal_life_operations_profile",
    "personal_lifestyle_profile",
    "personal_relationships_profile",
    "personal_moment_highlights",
    "personal_moment_profiles",
    "personal_moment_turning_points",
)

_BUSINESS_OPS_TABLES = (
    "business_moment_invitations",
    "operations_spend_entries",
    "operations_issues",
    "operations_improvements",
    "operations_approval_requests",
    "operations_vendor_updates",
    "business_live_feed",
    "business_notification_queue",
    "business_moment_setup",
    "business_moment_structure",
    "business_moment_governance",
    "business_operations_setup",
    "business_operations_structure",
    "business_operations_governance_rules",
    "business_operations_budget_categories",
    "business_runway_setup",
    "business_runway_structure",
    "business_runway_governance_rules",
)


def _now() -> datetime:
    return datetime.now(timezone.utc)


class MomentPurgeService:
    def __init__(self, session: AsyncSession) -> None:
        self.session = session
        self.publisher = get_event_publisher()

    async def purge(
        self,
        user_id: UUID,
        moment_id: UUID,
        *,
        expected_context: str | None = None,
    ) -> MomentModel:
        """Owner-only permanent purge. Returns the tombstoned moment row."""
        moment = await self._require_owned(user_id, moment_id)
        context = (moment.context_type or "").upper()
        if expected_context and context != expected_context.upper():
            raise PermissionDeniedError(
                "This moment does not belong to this context.",
                code="context_mismatch",
            )
        if (moment.status or "").upper() == DELETED:
            return moment

        previous = moment.status or "DRAFT"
        assert_transition(previous, DELETED)

        if context == "GROUP":
            await self._exit_group_members(moment)
            await self._purge_tables(_GROUP_OPS_TABLES, moment_id)
            await self._tombstone_group_mirror(moment)
        elif context == "BUSINESS":
            await self._exit_business_members(moment_id)
            await self._purge_tables(_BUSINESS_OPS_TABLES, moment_id, id_column="moment_id")
            await self._tombstone_business_mirror(moment)
        elif context in {"PERSONAL", "MY_MONEY"}:
            await self._purge_tables(_PERSONAL_OPS_TABLES, moment_id)
            await self._tombstone_personal_mirror(moment)

        await self._delete_media(moment_id)
        self._tombstone_platform_moment(moment)

        await self.session.flush()

        await self.publisher.publish(
            ev.moment_deleted(
                user_id=user_id,
                moment_id=moment_id,
                context=context,
                moment_type=moment.moment_type,
                session=self.session,
                previous_status=previous,
                purged=True,
            )
        )
        return moment

    async def _require_owned(self, user_id: UUID, moment_id: UUID) -> MomentModel:
        result = await self.session.execute(
            select(MomentModel).where(MomentModel.id == moment_id)
        )
        moment = result.scalar_one_or_none()
        if moment is None:
            raise NotFoundError("Moment not found")
        if moment.user_id != user_id:
            # Distinguish member-visible vs unknown for Group/Business callers.
            raise PermissionDeniedError(
                "Only the owner can delete this moment.",
                code="moment_not_owned",
                details={
                    "denial_reason": "moment_not_owned",
                    "moment_id": str(moment_id),
                    "action": "purge",
                },
            )
        return moment

    def _tombstone_platform_moment(self, moment: MomentModel) -> None:
        moment.status = DELETED
        moment.title = "Deleted Moment"
        moment.description = None
        moment.updated_at = _now()

    async def _exit_group_members(self, moment: MomentModel) -> None:
        now = _now()
        naive = now.replace(tzinfo=None)
        result = await self.session.execute(
            select(GroupMomentMembers).where(
                GroupMomentMembers.moment_id == moment.id
            )
        )
        for row in result.scalars().all():
            status_val = (row.status or "").upper()
            if status_val in {"LEFT", "REMOVED", "DECLINED"} and row.left_at is not None:
                continue
            row.status = "LEFT"
            row.left_at = naive

        # Runtime roster (JWT invite path)
        state = group_store.read_state(moment)
        members = state.get("runtime", {}).get("members") or []
        changed = False
        for member in members:
            if member.get("deleted"):
                continue
            member["status"] = "LEFT"
            member["deleted"] = True
            member["left_at"] = now.isoformat()
            member["updated_at"] = group_store.now_iso()
            changed = True
        if changed:
            group_store.write_state(moment, state)

    async def _exit_business_members(self, moment_id: UUID) -> None:
        try:
            from app.domains.business.models import BusinessMomentMembers

            result = await self.session.execute(
                select(BusinessMomentMembers).where(
                    BusinessMomentMembers.moment_id == moment_id
                )
            )
            for row in result.scalars().all():
                if (row.member_status or "").lower() == "removed":
                    continue
                row.member_status = "removed"
        except Exception:
            logger.exception("Failed exiting business members for %s", moment_id)

    async def _tombstone_group_mirror(self, moment: MomentModel) -> None:
        result = await self.session.execute(
            select(GroupMoments).where(GroupMoments.moment_id == moment.id)
        )
        row = result.scalar_one_or_none()
        if row is None:
            return
        # Domain CHECK may not allow DELETED — use ARCHIVED as mirror tombstone.
        row.status = "ARCHIVED"
        row.moment_name = "Deleted Moment"
        row.updated_at = _now().replace(tzinfo=None)

    async def _tombstone_personal_mirror(self, moment: MomentModel) -> None:
        try:
            from app.domains.personal.models import PersonalMoments

            result = await self.session.execute(
                select(PersonalMoments).where(PersonalMoments.moment_id == moment.id)
            )
            row = result.scalar_one_or_none()
            if row is None:
                return
            row.status = "ARCHIVED"
            if hasattr(row, "moment_name"):
                row.moment_name = "Deleted Moment"
            if hasattr(row, "archived_at"):
                row.archived_at = _now()
        except Exception:
            logger.exception("Failed tombstoning personal_moments for %s", moment.id)

    async def _tombstone_business_mirror(self, moment: MomentModel) -> None:
        try:
            from app.domains.business.models import BusinessMoments

            result = await self.session.execute(
                select(BusinessMoments).where(BusinessMoments.moment_id == moment.id)
            )
            row = result.scalar_one_or_none()
            if row is None:
                return
            row.status = "archived"
            if hasattr(row, "moment_name"):
                row.moment_name = "Deleted Moment"
        except Exception:
            logger.exception("Failed tombstoning business_moments for %s", moment.id)

    async def _delete_media(self, moment_id: UUID) -> None:
        try:
            await self.session.execute(
                delete(MomentMediaModel).where(MomentMediaModel.moment_id == moment_id)
            )
        except Exception:
            logger.exception("Failed deleting moment_media for %s", moment_id)

    async def _purge_tables(
        self,
        tables: tuple[str, ...],
        moment_id: UUID,
        *,
        id_column: str = "moment_id",
    ) -> None:
        """Best-effort DELETE FROM table WHERE moment_id = :id (skip missing tables)."""
        for table in tables:
            try:
                async with self.session.begin_nested():
                    await self.session.execute(
                        text(f"DELETE FROM {table} WHERE {id_column} = :mid"),
                        {"mid": str(moment_id)},
                    )
            except Exception:
                # Missing table / FK order / MockSession — leave row and continue.
                logger.debug(
                    "Skip purge of %s for moment %s",
                    table,
                    moment_id,
                    exc_info=True,
                )