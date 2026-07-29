"""Contract-first service for shared-purchase & shared-living read surfaces.

Resolves the moment from the shared ``moments`` table and returns schema-valid
empty/seeded live-hub / pulse / moments-view / quick-add shapes so the purchase
and living screens render. Rich analytics are the iterative data-backing step.
"""
from __future__ import annotations

import json
from uuid import UUID

from fastapi import HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.domains.group import moment_store as store
from app.domains.group import read_schemas as r
from app.domains.group import shared_catalog as cat
from app.domains.group import trip_schemas as ts
from app.domains.group.activity.engine import GroupActivityEngine
from app.domains.group.activity.types import ActivityType
from app.domains.group.shared_living_service import SharedLivingService
from app.domains.group.shared_purchase_service import SharedPurchaseService
from app.domains.group.templates.shared_living.quick_add import activity_type_for_module as living_activity_type_for_module
from app.domains.group.templates.shared_purchase.quick_add import activity_type_for_module
from app.domains.moments.models import MomentModel
from app.domains.moments.repository import MomentRepository


def _opts(*pairs: tuple[str, str]) -> list[r.QuickAddOption]:
    return [r.QuickAddOption(id=i, label=l) for i, l in pairs]


def _operations_hub(name: str, stage_badge: str, profile_badge: str) -> ts.GroupMomentsOperationsHub:
    return ts.GroupMomentsOperationsHub(
        core_summary=ts.GroupMomentsCoreSummary(
            eyebrow=profile_badge, moment_name=name, stage_badge=stage_badge
        ),
        money_status=ts.GroupMomentsMoneyStatus(progress_label="No money tracked yet", progress_percent=0.0),
        current_state=ts.GroupMomentsCurrentState(stage_label=stage_badge),
    )


def _memory_hub(name: str) -> ts.GroupMomentsMemoryHub:
    return ts.GroupMomentsMemoryHub(hero=ts.GroupMemoryHero(moment_name=name))


def _moments_display_name(raw: dict, *, fallback: str = "") -> str:
    """Resolve a display name across mapper / pulse / legacy cache key variants."""
    return str(
        raw.get("moment_name")
        or raw.get("purchase_name")
        or raw.get("living_name")
        or raw.get("trip_name")
        or ((raw.get("operations_hub") or {}).get("core_summary") or {}).get("moment_name")
        or ((raw.get("memory_hub") or {}).get("hero") or {}).get("moment_name")
        or fallback
    )


def _has_moments_hubs(raw: dict) -> bool:
    return isinstance(raw.get("operations_hub"), dict) and isinstance(raw.get("memory_hub"), dict)


class GroupReadService:
    def __init__(self, session: AsyncSession) -> None:
        self.session = session
        self.moments = MomentRepository(session)
        self.purchase_service = SharedPurchaseService(session)
        self.living_service = SharedLivingService(session)
        self.activity = GroupActivityEngine(session)

    async def _require(self, user_id: UUID, moment_id: UUID) -> MomentModel:
        from app.domains.group.access import require_group_moment_access

        return await require_group_moment_access(self.session, user_id, moment_id)

    async def _ensure_members(self, user_id: UUID, moment: MomentModel) -> list[dict]:
        """Parity with trip: accepted roster + seed creator ORGANIZER if missing."""
        members = store.list_accepted_members(moment)
        owner_id = str(getattr(moment, "user_id", None) or user_id)
        if owner_id and not any(
            str(m.get("user_id") or m.get("id") or "") == owner_id for m in members
        ):
            display_name = "You"
            try:
                from sqlalchemy import select
                from app.domains.users.models import UserModel

                result = await self.session.execute(
                    select(UserModel).where(UserModel.id == moment.user_id)
                )
                user = result.scalar_one_or_none()
                if user and getattr(user, "display_name", None):
                    display_name = str(user.display_name)
            except Exception:
                pass
            store.ensure_creator_organizer(
                moment, moment.user_id or user_id, display_name=display_name
            )
            await self.session.flush()
            members = store.list_accepted_members(moment)
        return members

    def _member_roster_fields(
        self, members: list[dict], *, user_id: UUID, include_guests: bool = True
    ) -> dict:
        participant_rows = [
            {
                "id": str(mem["id"]),
                "display_name": mem["display_name"],
                "role_code": mem.get("role_code"),
                "user_id": mem.get("user_id"),
            }
            for mem in members
        ]
        payers = [
            {
                "id": str(mem["id"]),
                "display_name": mem["display_name"],
                "role_code": mem.get("role_code"),
            }
            for mem in members
        ]
        if include_guests:
            # Guests are not always available on the moment in this call path;
            # callers that have guests already pass them via participants.
            pass
        default_paid = None
        uid = str(user_id)
        for mem in members:
            if str(mem.get("user_id") or mem.get("id") or "") == uid:
                default_paid = str(mem["id"])
                break
        if default_paid is None and participant_rows:
            default_paid = participant_rows[0]["id"]
        return {
            "participants": participant_rows,
            "members": participant_rows,
            "payers": payers,
            "default_paid_by_participant_id": default_paid,
        }

    @staticmethod
    def _profile_code(moment: MomentModel) -> str | None:
        raw = moment.description or ""
        if not raw:
            return None
        try:
            data = json.loads(raw)
            if isinstance(data, dict):
                return data.get("profile_code")
        except (ValueError, TypeError):
            pass
        return None

    def _badges(self, moment: MomentModel, category: str) -> tuple[str, str, str]:
        code = self._profile_code(moment)
        profile_badge = cat.profile_name(category, code) if code else category.replace("SHARED_", "").title()
        is_active = (moment.status or "DRAFT") == "ACTIVE"
        return profile_badge, ("Live" if is_active else "Setup"), ("Active" if is_active else "Draft")

    # ===== shared-purchase =============================================== #
    async def purchase_live_hub(self, user_id: UUID, moment_id: UUID) -> dict:
        raw = await self.purchase_service.live_hub(user_id, moment_id)
        return r.PurchaseLiveHub(
            moment_id=raw["moment_id"],
            selector=r.PurchaseSelector(
                moment_id=raw["moment_id"],
                moment_name=raw["selector"]["moment_name"],
                profile_label=raw["selector"]["profile_label"],
            ),
            header=ts.TripLiveHubHeader(**raw["header"]),
            hero=ts.TripLiveHubHero(**raw["hero"]),
            journey_steps=[ts.TripLiveHubJourneyStep(**s) for s in raw.get("journey_steps", [])],
            insight=ts.TripLiveHubInsight(**raw["insight"]),
            lifecycle_status=raw.get("lifecycle_status"),
            orchestration_state=raw.get("orchestration_state"),
        ).model_dump(mode="json")

    async def purchase_pulse(
        self, user_id: UUID, moment_id: UUID, *, force_refresh: bool = False
    ) -> dict:
        raw = await self.purchase_service.pulse(
            user_id, moment_id, force_refresh=force_refresh
        )
        stats = raw.get("stats") or {}
        # Drop unknown keys so older cached slices still validate.
        known_stats = {k: v for k, v in stats.items() if k in r.PurchasePulseStats.model_fields}
        return r.PurchasePulse(
            moment_id=raw["moment_id"],
            moment_name=raw.get("purchase_name") or raw.get("moment_name") or "",
            profile_badge=raw["profile_badge"],
            stage_badge=raw["stage_badge"],
            status_badge=raw["status_badge"],
            funding_percent=float(raw.get("funding_percent") or 0),
            funded_amount_minor=int(raw.get("funded_amount_minor") or 0),
            target_amount_minor=int(raw.get("target_amount_minor") or 0),
            amount_remaining_minor=int(raw.get("amount_remaining_minor") or 0),
            currency_code=str(raw.get("currency_code") or "INR"),
            readiness_score=float(raw.get("readiness_score") or 0),
            readiness_title=raw.get("readiness_title") or "",
            readiness_narrative=raw.get("readiness_narrative") or "",
            contributor_count=int(raw.get("contributor_count") or 0),
            experience_health_percent=float(raw.get("experience_health_percent") or 0),
            participation_percent=float(raw.get("participation_percent") or 0),
            participation_breakdown=raw.get("participation_breakdown") or {"active": 0, "pending": 0, "inactive": 0},
            participant_avatars=list(raw.get("participant_avatars") or []),
            health_dimensions=list(raw.get("health_dimensions") or []),
            attention_items=list(raw.get("attention_items") or []),
            insights=list(raw.get("insights") or []),
            next_best_action=raw.get("next_best_action"),
            dashboard_card=raw.get("dashboard_card"),
            metric_tiles=list(raw.get("metric_tiles") or []),
            recent_activity=list(raw.get("recent_activity") or []),
            health_trend=raw.get("health_trend") or {"label": "", "value": 0, "direction": "up"},
            settlement_widget=raw.get("settlement_widget"),
            settlement_preview=raw.get("settlement_preview"),
            stats=r.PurchasePulseStats(**known_stats),
        ).model_dump(mode="json")

    async def purchase_moments_view(
        self, user_id: UUID, moment_id: UUID, *, force_refresh: bool = False
    ) -> dict:
        raw = await self.purchase_service.moments_view(
            user_id, moment_id, force_refresh=force_refresh
        )
        # Stale/active-shaped cache may omit hubs or use alternate name keys.
        # invalidate() only marks stale and would re-serve the same payload.
        if not _has_moments_hubs(raw) or not _moments_display_name(raw):
            from app.domains.group.projection_cache import set_cached_slice
            from app.domains.group.templates.shared_purchase.constants import MOMENT_TYPE
            from app.domains.group.templates.shared_purchase.moments_mapper import build_moments

            ctx = await self.purchase_service.builder.build(user_id, moment_id)
            raw = build_moments(ctx)
            await set_cached_slice(
                user_id, moment_id, "moments", raw, moment_type=MOMENT_TYPE
            )
        m = await self._require(user_id, moment_id)
        pb, stage, sb = self._badges(m, cat.PURCHASE)
        name = _moments_display_name(raw, fallback=m.title or "Your Purchase")
        nba = raw.get("next_best_action") or {}
        ops = raw.get("operations_hub")
        mem = raw.get("memory_hub")
        return r.PurchaseMomentsView(
            moment_id=str(raw.get("moment_id") or moment_id),
            moment_name=name,
            profile_badge=str(raw.get("profile_badge") or pb),
            stage_badge=str(raw.get("stage_badge") or raw.get("stage") or stage),
            status_badge=str(raw.get("status_badge") or raw.get("status") or sb),
            funding_percent=float(raw.get("funding_percent") or 0),
            funded_amount_minor=int(raw.get("funded_amount_minor") or 0),
            contributor_count=int(raw.get("contributor_count") or 0),
            next_best_action=r.PurchaseNextBestAction(
                title=str(nba.get("title") or ""),
                subtitle=str(nba.get("subtitle") or ""),
                action=str(nba.get("action") or "review"),
            ),
            memory_hero_title=str(raw.get("memory_hero_title") or name),
            memory_hero_subtitle=str(raw.get("memory_hero_subtitle") or ""),
            operations_hub=ts.GroupMomentsOperationsHub(**ops)
            if isinstance(ops, dict)
            else _operations_hub(name, stage, pb),
            memory_hub=ts.GroupMomentsMemoryHub(**mem)
            if isinstance(mem, dict)
            else _memory_hub(name),
        ).model_dump(mode="json")

    async def purchase_quick_add_hub(self, user_id: UUID, moment_id: UUID) -> dict:
        m = await self._require(user_id, moment_id)
        name = m.title or "Your Purchase"
        from app.domains.group.templates.shared_purchase.constants import get_purchase_profile
        from app.domains.group.templates.shared_purchase.quick_add import (
            build_purchase_quick_add_categories,
        )

        profile = get_purchase_profile(store.profile_code(m))
        categories = build_purchase_quick_add_categories(profile.quick_add_modules)
        sections = [
            {
                "id": cat["id"],
                "label": cat["label"],
                "actions": [
                    {
                        "module_code": mod["module_code"],
                        "label": mod["label"],
                        "icon": mod["icon"],
                        "description": mod.get("description") or "",
                    }
                    for mod in cat["modules"]
                ],
            }
            for cat in categories
        ]
        return r.PurchaseQuickAddHub(
            moment_id=str(m.id),
            moment_name=name,
            context_chips=["Purchase", "Quick Add"],
            hero=r.PurchaseQuickAddHubHero(
                title="Keep this purchase moving",
                subtitle="Add contributors, items, vendors, and ownership updates.",
            ),
            sections=sections,
        ).model_dump(mode="json")

    async def purchase_generic_context(self, user_id: UUID, moment_id: UUID, module: str) -> dict:
        m = await self._require(user_id, moment_id)
        members = await self._ensure_members(user_id, m)
        roster = self._member_roster_fields(members, user_id=user_id)
        label = module.replace("-", " ").replace("_", " ").title()
        return r.PurchaseContextBase(
            moment_id=str(m.id),
            trip_name=m.title or "Your Purchase",
            status_line=f"Add {label.lower()}.",
            context_chips=["Purchase", label],
            **roster,
        ).model_dump(mode="json")

    async def purchase_contributor_context(self, user_id: UUID, moment_id: UUID) -> dict:
        base = await self.purchase_generic_context(user_id, moment_id, "contributors")
        base["roles"] = _opts(("owner", "Owner"), ("contributor", "Contributor"), ("viewer", "Viewer"))
        base["invite_methods"] = _opts(("link", "Invite link"), ("phone", "Phone"), ("email", "Email"))
        return base

    async def purchase_participants_context(self, user_id: UUID, moment_id: UUID) -> dict:
        base = await self.purchase_generic_context(user_id, moment_id, "participants")
        base["invite_statuses"] = _opts(("invited", "Invited"), ("active", "Active"), ("declined", "Declined"))
        return base

    async def purchase_item_context(self, user_id: UUID, moment_id: UUID) -> dict:
        base = await self.purchase_generic_context(user_id, moment_id, "purchase-items")
        base["status_line"] = "Add a purchase item."
        return base

    async def purchase_expense_context(self, user_id: UUID, moment_id: UUID) -> dict:
        base = await self.purchase_generic_context(user_id, moment_id, "expenses")
        base["currencies"] = _opts(("INR", "INR"), ("USD", "USD"), ("EUR", "EUR"))
        return base

    async def purchase_poll_context(self, user_id: UUID, moment_id: UUID) -> dict:
        base = await self.purchase_generic_context(user_id, moment_id, "polls")
        base["scopes"] = _opts(("everyone", "Everyone"), ("owners", "Owners only"))
        return base

    async def purchase_memory_context(self, user_id: UUID, moment_id: UUID) -> dict:
        base = await self.purchase_generic_context(user_id, moment_id, "memories")
        base["memory_categories"] = _opts(("highlight", "Highlight"), ("milestone", "Milestone"), ("delivery", "Delivery"))
        return base

    async def purchase_vendor_context(self, user_id: UUID, moment_id: UUID) -> dict:
        m = await self._require(user_id, moment_id)
        return r.PurchaseVendorContext(
            moment_id=str(m.id),
            trip_name=m.title or "Your Purchase",
            status_line="Add a vendor or quote.",
            vendor_types=_opts(("retailer", "Retailer"), ("service", "Service"), ("custom", "Custom")),
        ).model_dump(mode="json")

    async def purchase_update_context(self, user_id: UUID, moment_id: UUID) -> dict:
        m = await self._require(user_id, moment_id)
        return r.PurchaseUpdateContext(
            moment_id=str(m.id),
            trip_name=m.title or "Your Purchase",
            status_line="Post an update.",
            update_types=_opts(("milestone", "Milestone"), ("payment", "Payment"), ("note", "Note")),
            visibility_options=_opts(("everyone", "Everyone"), ("owners", "Owners only")),
        ).model_dump(mode="json")

    async def purchase_ownership_context(self, user_id: UUID, moment_id: UUID) -> dict:
        m = await self._require(user_id, moment_id)
        members = await self._ensure_members(user_id, m)
        roster = self._member_roster_fields(members, user_id=user_id)
        return r.PurchaseOwnershipContext(
            moment_id=str(m.id),
            trip_name=m.title or "Your Purchase",
            status_line="Assign ownership shares.",
            usage_rights_options=_opts(("full", "Full"), ("shared", "Shared"), ("limited", "Limited")),
            total_allocated_pct="0",
            **roster,
        ).model_dump(mode="json")

    async def purchase_delivery_context(self, user_id: UUID, moment_id: UUID) -> dict:
        m = await self._require(user_id, moment_id)
        return r.PurchaseDeliveryContext(
            moment_id=str(m.id),
            trip_name=m.title or "Your Purchase",
            status_line="Track delivery.",
            event_types=_opts(("shipped", "Shipped"), ("arriving", "Arriving"), ("delivered", "Delivered")),
            statuses=_opts(("scheduled", "Scheduled"), ("in_transit", "In transit"), ("delivered", "Delivered")),
        ).model_dump(mode="json")

    async def purchase_quick_add_create(self, user_id: UUID, moment_id: UUID, module: str, body: dict) -> dict:
        from app.domains.quick_add_contract.errors import QuickAddActionNotSupported
        from app.domains.quick_add_contract.normalize import normalize_payload

        await self._require(user_id, moment_id)
        activity = activity_type_for_module(module)
        if activity is None:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail={
                    "code": "quick_add_action_not_supported",
                    "message": f"Unknown quick-add module: {module}",
                },
            )
        normalized = normalize_payload(dict(body or {}))
        if activity == ActivityType.VENDOR:
            normalized.setdefault("name", normalized.get("vendor_name"))
        if activity == ActivityType.UPDATE:
            normalized.setdefault("title", normalized.get("body") or normalized.get("message"))
        if activity == ActivityType.MILESTONE:
            normalized.setdefault("title", normalized.get("event_type") or "Delivery")
        if activity == ActivityType.PARTICIPANT:
            normalized.setdefault(
                "name",
                normalized.get("full_name")
                or normalized.get("display_name")
                or normalized.get("title")
                or "Contributor",
            )
        if activity == ActivityType.TASK:
            normalized.setdefault("title", normalized.get("item_name") or normalized.get("title") or "Purchase item")
        if activity == ActivityType.EXPENSE:
            normalized.setdefault("amount_minor", normalized.get("amount_minor") or 0)
        if activity == ActivityType.POLL:
            normalized.setdefault("question", normalized.get("question") or "Poll")
            allow_multiple = normalized.get("allow_multiple_answers")
            if allow_multiple is None:
                poll_type = str(normalized.get("poll_type") or "single").lower()
                allow_multiple = poll_type in {
                    "multiple",
                    "multi",
                    "multi_choice",
                    "multiple_choice",
                }
            else:
                allow_multiple = bool(allow_multiple)
            normalized["allow_multiple_answers"] = allow_multiple
            normalized["poll_type"] = "multiple" if allow_multiple else "single"
        if activity == ActivityType.MEMORY:
            normalized.setdefault("title", normalized.get("title") or normalized.get("caption") or "Memory")
        if activity == ActivityType.OWNERSHIP_UPDATE:
            normalized.setdefault("title", normalized.get("responsibility") or "Ownership update")
        try:
            row = await self.activity.write(user_id, moment_id, activity, normalized)
        except QuickAddActionNotSupported as exc:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=exc.to_detail()) from exc
        return {
            "status": "ok",
            "id": row["id"],
            "idempotent_replay": bool(row.get("idempotent_replay")),
            "contract_version": "v1",
        }

    # ===== shared-living ================================================= #
    async def living_live_hub(self, user_id: UUID, moment_id: UUID) -> dict:
        raw = await self.living_service.live_hub(user_id, moment_id)
        return r.LivingLiveHub(
            moment_id=raw["moment_id"],
            selector=r.LivingSelector(
                moment_id=raw["moment_id"],
                moment_name=raw["selector"]["moment_name"],
                profile_label=raw["selector"]["profile_label"],
            ),
            header=ts.TripLiveHubHeader(**raw["header"]),
            hero=ts.TripLiveHubHero(**raw["hero"]),
            journey_steps=[ts.TripLiveHubJourneyStep(**s) for s in raw.get("journey_steps", [])],
            insight=ts.TripLiveHubInsight(**raw["insight"]),
            lifecycle_status=raw.get("lifecycle_status"),
            orchestration_state=raw.get("orchestration_state"),
        ).model_dump(mode="json")

    async def living_pulse(
        self, user_id: UUID, moment_id: UUID, *, force_refresh: bool = False
    ) -> dict:
        raw = await self.living_service.pulse(
            user_id, moment_id, force_refresh=force_refresh
        )
        stats = raw.get("stats") or {}
        known_stats = {k: v for k, v in stats.items() if k in r.LivingPulseStats.model_fields}
        return r.LivingPulse(
            moment_id=raw["moment_id"],
            moment_name=raw.get("living_name") or raw.get("moment_name") or "",
            profile_badge=raw["profile_badge"],
            stage_badge=raw["stage_badge"],
            status_badge=raw["status_badge"],
            health_percent=float(raw.get("health_percent") or raw.get("experience_health_percent") or 0),
            expenses_total_minor=int(raw.get("expenses_total_minor") or 0),
            contributions_total_minor=int(raw.get("contributions_total_minor") or 0),
            outstanding_minor=int(raw.get("outstanding_minor") or 0),
            currency_code=str(raw.get("currency_code") or "INR"),
            readiness_score=float(raw.get("readiness_score") or 0),
            readiness_title=raw.get("readiness_title") or "",
            readiness_narrative=raw.get("readiness_narrative") or "",
            resident_count=int(raw.get("resident_count") or 0),
            experience_health_percent=float(raw.get("experience_health_percent") or raw.get("health_percent") or 0),
            participation_percent=float(raw.get("participation_percent") or 0),
            participation_breakdown=raw.get("participation_breakdown")
            or {"active": 0, "pending": 0, "inactive": 0},
            participant_avatars=list(raw.get("participant_avatars") or []),
            health_dimensions=list(raw.get("health_dimensions") or []),
            attention_items=list(raw.get("attention_items") or []),
            insights=list(raw.get("insights") or []),
            next_best_action=raw.get("next_best_action"),
            dashboard_card=raw.get("dashboard_card"),
            metric_tiles=list(raw.get("metric_tiles") or []),
            recent_activity=list(raw.get("recent_activity") or []),
            health_trend=raw.get("health_trend") or {"label": "", "value": 0, "direction": "up"},
            operations_progress=raw.get("operations_progress"),
            settlement_widget=raw.get("settlement_widget"),
            settlement_preview=raw.get("settlement_preview"),
            stats=r.LivingPulseStats(**known_stats),
        ).model_dump(mode="json")

    async def living_moments_view(
        self, user_id: UUID, moment_id: UUID, *, force_refresh: bool = False
    ) -> dict:
        raw = await self.living_service.moments_view(
            user_id, moment_id, force_refresh=force_refresh
        )
        if not _has_moments_hubs(raw) or not _moments_display_name(raw):
            from app.domains.group.projection_cache import set_cached_slice
            from app.domains.group.templates.shared_living.constants import MOMENT_TYPE
            from app.domains.group.templates.shared_living.moments_mapper import build_moments

            ctx = await self.living_service.builder.build(user_id, moment_id)
            raw = build_moments(ctx)
            await set_cached_slice(
                user_id, moment_id, "moments", raw, moment_type=MOMENT_TYPE
            )
        m = await self._require(user_id, moment_id)
        pb, stage, sb = self._badges(m, cat.LIVING)
        name = _moments_display_name(raw, fallback=m.title or "Your Home")
        nba = raw.get("next_best_action") or {}
        ops = raw.get("operations_hub")
        mem = raw.get("memory_hub")
        return r.LivingMomentsView(
            moment_id=str(raw.get("moment_id") or moment_id),
            moment_name=name,
            profile_badge=str(raw.get("profile_badge") or pb),
            stage_badge=str(raw.get("stage_badge") or raw.get("stage") or stage),
            status_badge=str(raw.get("status_badge") or raw.get("status") or sb),
            health_percent=float(raw.get("health_percent") or 0),
            expenses_total_minor=int(raw.get("expenses_total_minor") or 0),
            resident_count=int(raw.get("resident_count") or 0),
            next_best_action=r.LivingNextBestAction(
                title=str(nba.get("title") or ""),
                subtitle=str(nba.get("subtitle") or ""),
                action=str(nba.get("action") or "review"),
            ),
            memory_hero_title=str(raw.get("memory_hero_title") or name),
            memory_hero_subtitle=str(raw.get("memory_hero_subtitle") or ""),
            operations_hub=ts.GroupMomentsOperationsHub(**ops)
            if isinstance(ops, dict)
            else _operations_hub(name, stage, pb),
            memory_hub=ts.GroupMomentsMemoryHub(**mem)
            if isinstance(mem, dict)
            else _memory_hub(name),
        ).model_dump(mode="json")

    async def living_quick_add_hub(self, user_id: UUID, moment_id: UUID) -> dict:
        m = await self._require(user_id, moment_id)
        name = m.title or "Your Home"
        pb, _stage, _sb = self._badges(m, cat.LIVING)
        from app.domains.group.templates.shared_living.constants import get_living_profile
        from app.domains.group.templates.shared_living.quick_add import (
            build_living_quick_add_categories,
        )

        profile = get_living_profile(store.profile_code(m))
        categories = build_living_quick_add_categories(profile.quick_add_modules)
        sections = [
            {
                "id": cat["id"],
                "label": cat["label"],
                "actions": [
                    {
                        "module_code": mod["module_code"],
                        "label": mod["label"],
                        "icon": mod["icon"],
                        "description": mod.get("description") or "",
                    }
                    for mod in cat["modules"]
                ],
            }
            for cat in categories
        ]
        return r.LivingQuickAddHub(
            moment_id=str(m.id),
            living_name=name,
            profile_label=pb,
            stage_label=_stage,
            context_chips=["Home", "Quick Add"],
            hero=r.LivingQuickAddHubHero(
                title="Keep home life in sync",
                subtitle="Add residents, expenses, chores, and house updates.",
            ),
            sections=sections,
        ).model_dump(mode="json")

    def _living_name(self, moment: MomentModel) -> str:
        return moment.title or "Your Home"

    async def living_resident_context(self, user_id: UUID, moment_id: UUID) -> dict:
        m = await self._require(user_id, moment_id)
        name = self._living_name(m)
        return r.LivingResidentContext(
            moment_id=str(m.id),
            living_name=name,
            status_line="Add a resident.",
            relationship_types=_opts(("roommate", "Roommate"), ("family", "Family"), ("partner", "Partner")),
            resident_roles=_opts(("lead", "Lead"), ("member", "Member")),
            statuses=_opts(("active", "Active"), ("invited", "Invited")),
            guests=store.guest_summaries(m),
            invite=r.InviteQuickAddContext(share_message=f"Join {name} on Momentra."),
        ).model_dump(mode="json")

    async def living_expense_context(self, user_id: UUID, moment_id: UUID) -> dict:
        m = await self._require(user_id, moment_id)
        members = await self._ensure_members(user_id, m)
        roster = self._member_roster_fields(members, user_id=user_id)
        return r.LivingExpenseContext(
            moment_id=str(m.id),
            living_name=self._living_name(m),
            status_line="Log a shared expense.",
            expense_categories=_opts(("rent", "Rent"), ("utilities", "Utilities"), ("groceries", "Groceries"), ("other", "Other")),
            currencies=_opts(("INR", "INR"), ("USD", "USD"), ("EUR", "EUR")),
            split_types=_opts(("equal", "Equal"), ("custom", "Custom")),
            guests=store.guest_summaries(m),
            **roster,
        ).model_dump(mode="json")

    async def living_contribution_context(self, user_id: UUID, moment_id: UUID) -> dict:
        m = await self._require(user_id, moment_id)
        members = await self._ensure_members(user_id, m)
        roster = self._member_roster_fields(members, user_id=user_id)
        return r.LivingContributionContext(
            moment_id=str(m.id),
            living_name=self._living_name(m),
            status_line="Log a contribution.",
            contribution_categories=_opts(("rent", "Rent"), ("utilities", "Utilities"), ("deposit", "Deposit")),
            payment_methods=_opts(("cash", "Cash"), ("upi", "UPI"), ("bank", "Bank transfer")),
            contribution_statuses=_opts(("pending", "Pending"), ("received", "Received")),
            **roster,
        ).model_dump(mode="json")

    async def living_task_context(self, user_id: UUID, moment_id: UUID) -> dict:
        m = await self._require(user_id, moment_id)
        members = await self._ensure_members(user_id, m)
        roster = self._member_roster_fields(members, user_id=user_id)
        return r.LivingTaskContext(
            moment_id=str(m.id),
            living_name=self._living_name(m),
            status_line="Add a chore.",
            task_categories=_opts(("cleaning", "Cleaning"), ("shopping", "Shopping"), ("bills", "Bills")),
            frequencies=_opts(("once", "Once"), ("weekly", "Weekly"), ("monthly", "Monthly")),
            priorities=_opts(("low", "Low"), ("medium", "Medium"), ("high", "High")),
            **roster,
        ).model_dump(mode="json")

    async def living_rule_context(self, user_id: UUID, moment_id: UUID) -> dict:
        m = await self._require(user_id, moment_id)
        return r.LivingRuleContext(
            moment_id=str(m.id),
            living_name=self._living_name(m),
            status_line="Add a house rule.",
            rule_types=_opts(("house", "House"), ("quiet", "Quiet hours"), ("guests", "Guests")),
            visibility_options=_opts(("everyone", "Everyone"), ("residents", "Residents")),
        ).model_dump(mode="json")

    async def living_asset_context(self, user_id: UUID, moment_id: UUID) -> dict:
        m = await self._require(user_id, moment_id)
        return r.LivingAssetContext(
            moment_id=str(m.id),
            living_name=self._living_name(m),
            status_line="Add a shared asset.",
            asset_types=_opts(("appliance", "Appliance"), ("furniture", "Furniture"), ("shared", "Shared item")),
        ).model_dump(mode="json")

    async def living_maintenance_context(self, user_id: UUID, moment_id: UUID) -> dict:
        m = await self._require(user_id, moment_id)
        return r.LivingMaintenanceContext(
            moment_id=str(m.id),
            living_name=self._living_name(m),
            status_line="Log maintenance.",
            maintenance_types=_opts(("repair", "Repair"), ("service", "Service"), ("inspection", "Inspection")),
        ).model_dump(mode="json")

    async def living_update_context(self, user_id: UUID, moment_id: UUID) -> dict:
        m = await self._require(user_id, moment_id)
        return r.LivingUpdateContext(
            moment_id=str(m.id),
            living_name=self._living_name(m),
            status_line="Post an update.",
            update_types=_opts(("announcement", "Announcement"), ("notice", "Notice")),
            visibility_options=_opts(("everyone", "Everyone"), ("residents", "Residents")),
        ).model_dump(mode="json")

    async def living_poll_context(self, user_id: UUID, moment_id: UUID) -> dict:
        m = await self._require(user_id, moment_id)
        return r.LivingPollContext(
            moment_id=str(m.id),
            living_name=self._living_name(m),
            status_line="Start a poll.",
            poll_categories=_opts(("house", "House"), ("expense", "Expense")),
            poll_types=_opts(("single", "Single choice"), ("multiple", "Multiple choice")),
        ).model_dump(mode="json")

    async def living_quick_add_create(self, user_id: UUID, moment_id: UUID, module: str, body: dict) -> dict:
        from app.domains.quick_add_contract.errors import QuickAddActionNotSupported
        from app.domains.quick_add_contract.normalize import normalize_payload

        await self._require(user_id, moment_id)
        activity = living_activity_type_for_module(module)
        if activity is None:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail={
                    "code": "quick_add_action_not_supported",
                    "message": f"Unknown quick-add module: {module}",
                },
            )
        normalized = normalize_payload(dict(body or {}))
        if activity == ActivityType.MEMBER_UPDATE:
            normalized.setdefault("full_name", normalized.get("name") or "Resident")
            normalized.setdefault("relationship_type", "roommate")
            # Preserve client invite-first status when provided (e.g. "invited").
            normalized.setdefault("status", "invited")
        if activity == ActivityType.EXPENSE:
            if "amount_major" in (body or {}) and "amount_minor" not in normalized:
                normalized["amount_minor"] = store.to_minor((body or {}).get("amount_major"))
            normalized.setdefault("description", normalized.get("title") or "Expense")
            if normalized.get("category_code"):
                normalized.setdefault("expense_category", normalized["category_code"])
                normalized.setdefault("category", normalized["category_code"])
        if activity == ActivityType.CONTRIBUTION:
            if "amount_major" in (body or {}) and "amount_minor" not in normalized:
                normalized["amount_minor"] = store.to_minor((body or {}).get("amount_major"))
            normalized.setdefault("title", normalized.get("title") or "Contribution")
        if activity == ActivityType.UPDATE:
            normalized.setdefault("title", normalized.get("body") or normalized.get("message") or "Update")
        if activity == ActivityType.CHORE:
            normalized.setdefault("title", normalized.get("title") or "Chore")
        if activity == ActivityType.NOTE:
            normalized.setdefault("title", normalized.get("title") or "House rule")
        if activity == ActivityType.HOUSEHOLD_PURCHASE:
            normalized.setdefault("title", normalized.get("item_name") or normalized.get("title") or "Asset")
        if activity == ActivityType.MAINTENANCE:
            normalized.setdefault("title", normalized.get("title") or "Maintenance")
        if activity == ActivityType.POLL:
            normalized.setdefault("question", normalized.get("question") or "Poll")
            allow_multiple = normalized.get("allow_multiple_answers")
            if allow_multiple is None:
                poll_type = str(normalized.get("poll_type") or "single").lower()
                allow_multiple = poll_type in {
                    "multiple",
                    "multi",
                    "multi_choice",
                    "multiple_choice",
                }
            else:
                allow_multiple = bool(allow_multiple)
            normalized["allow_multiple_answers"] = allow_multiple
            normalized["poll_type"] = "multiple" if allow_multiple else "single"
        if activity == ActivityType.HOME_MEMORY:
            normalized.setdefault("title", normalized.get("title") or "Memory")
        try:
            row = await self.activity.write(user_id, moment_id, activity, normalized)
        except QuickAddActionNotSupported as exc:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=exc.to_detail()) from exc
        return {
            "status": "ok",
            "id": row["id"],
            "idempotent_replay": bool(row.get("idempotent_replay")),
            "contract_version": "v1",
        }

    async def living_create_resident(self, user_id: UUID, moment_id: UUID, body: dict) -> dict:
        return await self.living_quick_add_create(user_id, moment_id, "residents", body)

    async def living_create_expense(self, user_id: UUID, moment_id: UUID, body: dict) -> dict:
        return await self.living_quick_add_create(user_id, moment_id, "expenses", body)

    async def living_memory_context(self, user_id: UUID, moment_id: UUID) -> dict:
        m = await self._require(user_id, moment_id)
        return r.LivingMemoryContext(
            moment_id=str(m.id),
            living_name=self._living_name(m),
            status_line="Capture a memory.",
            memory_categories=_opts(("moment", "Moment"), ("milestone", "Milestone")),
            memory_formats=_opts(("photo", "Photo"), ("note", "Note")),
        ).model_dump(mode="json")

    async def living_list_activity(self, user_id: UUID, moment_id: UUID) -> dict:
        return await self.living_service.list_activity(user_id, moment_id)

    async def living_get_activity(self, user_id: UUID, moment_id: UUID, event_id: str) -> dict:
        return await self.living_service.get_activity(user_id, moment_id, event_id)

    async def living_patch_activity(
        self, user_id: UUID, moment_id: UUID, event_id: str, body: dict
    ) -> dict:
        return await self.living_service.patch_activity(user_id, moment_id, event_id, body or {})

    async def living_delete_activity(self, user_id: UUID, moment_id: UUID, event_id: str) -> dict:
        return await self.living_service.delete_activity(user_id, moment_id, event_id)
