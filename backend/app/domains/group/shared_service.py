"""Contract-first service for the Group ``shared-*`` setup surface.

Backs the dedicated ``/group/shared-experience|shared-purchase|shared-living``
setup endpoints the Android client calls (no client-side mock fallback). Moments
persist in the shared ``moments`` table (``context_type="GROUP"``,
``moment_type`` = the category). The rich per-step draft payload is stored as
JSON in ``moment.description`` so setup state round-trips without a Postgres-only
draft table (works under the test ``MockSession``).
"""
from __future__ import annotations

import json
from datetime import date, datetime, timezone
from uuid import UUID

from fastapi import HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.domains.app_bootstrap.service import AppBootstrapService
from app.domains.group import moment_store as store
from app.domains.group import shared_catalog as cat
from app.domains.group import shared_schemas as s
from app.domains.group.shared_experience_service import SharedExperienceService
from app.domains.group.shared_living_service import SharedLivingService
from app.domains.group.shared_purchase_service import SharedPurchaseService
from app.domains.group.catalog import GROUP_CONTEXT
from app.domains.module_states.service import ModuleStateService
from app.domains.moments.models import MomentModel
from app.domains.moments.repository import MomentRepository

_DEFAULT_NAME = {
    cat.EXPERIENCE: "Our Experience",
    cat.PURCHASE: "Our Purchase",
    cat.LIVING: "Our Home",
}

# Product-facing aliases → canonical payload keys (Phase 2 setup contracts).
_FIELD_ALIASES: dict[str, str] = {
    "trip_name": "moment_name",
    "experience_name": "moment_name",
    "destination": "location",
    "participants": "expected_participants",
    "budget_currency": "currency_code",
    "estimated_budget": "target_amount_major",
    "split_style": "money_tracking_mode",
    "trip_style": "experience_profile",
    "experience_type": "experience_profile",
    "purchase_name": "moment_name",
    "item_or_goal": "description",
    "expected_amount": "target_amount_major",
    "contributors": "expected_contributors",
    "payment_plan": "funding_style",
    "decision_deadline": "target_date",
    "home_name": "living_name",
    "members": "expected_residents",
    "monthly_budget": "monthly_budget_major",
    "rent_split_style": "management",
    "rules_or_notes": "description",
    "living_profile": "living_type",
}

_META_KEYS = frozenset({"template_id", "template_version", "answers"})


def _now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


def _to_minor(value) -> int | None:
    if value in (None, ""):
        return None
    try:
        return int(round(float(str(value)) * 100))
    except (ValueError, TypeError):
        return None


def _to_int(value) -> int | None:
    if value in (None, ""):
        return None
    if isinstance(value, list):
        return len(value)
    try:
        return int(value)
    except (ValueError, TypeError):
        return None


def _normalize_payload(raw: dict) -> dict:
    """Accept product aliases + Setup Engine `{answers: {...}}` wrappers."""
    body = dict(raw or {})
    if isinstance(body.get("answers"), dict):
        nested = body.pop("answers")
        body = {**nested, **{k: v for k, v in body.items() if k not in nested}}
    out: dict = {}
    for key, value in body.items():
        if key in _META_KEYS or value is None:
            continue
        canonical = _FIELD_ALIASES.get(key, key)
        if canonical in ("expected_participants", "expected_contributors", "expected_residents"):
            coerced = _to_int(value)
            out[canonical] = coerced if coerced is not None else value
        elif canonical == "allow_multi_currency":
            if isinstance(value, bool):
                out[canonical] = value
            else:
                out[canonical] = str(value).strip().lower() in {"1", "true", "yes", "on"}
        elif canonical == "target_amount_minor" and "target_amount_major" not in out:
            # money fields from templates may send major or minor
            if isinstance(value, (int, float)) and float(value) >= 1000:
                out["target_amount_major"] = float(value) / 100.0
            else:
                out["target_amount_major"] = value
        else:
            out[canonical] = value
    return out


def _preview_blocks(items: list[tuple[str, str | None]]) -> list[dict]:
    return [{"label": label, "value": value} for label, value in items if value not in (None, "", [])]


def _parse_iso_date(value) -> date | None:
    if value in (None, ""):
        return None
    try:
        return date.fromisoformat(str(value)[:10])
    except (TypeError, ValueError):
        return None


def _validate_experience_dates(payload: dict) -> None:
    start = _parse_iso_date(payload.get("start_date"))
    end = _parse_iso_date(payload.get("end_date"))
    if start is not None and end is not None and end < start:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="end_date cannot be before start_date",
        )


class SharedGroupService:
    def __init__(self, session: AsyncSession) -> None:
        self.session = session
        self.moments = MomentRepository(session)
        self.modules = ModuleStateService(session)
        self.bootstrap = AppBootstrapService(session)

    # ----- persistence helpers ------------------------------------------- #
    async def _require(self, user_id: UUID, moment_id: UUID) -> MomentModel:
        from app.domains.group.access import require_group_moment_access

        return await require_group_moment_access(self.session, user_id, moment_id)

    def _read_state(self, moment: MomentModel) -> dict:
        return store.read_state(moment)

    def _write_state(self, moment: MomentModel, state: dict) -> None:
        store.write_state(moment, state)

    async def _flip_setup(self, user_id: UUID) -> None:
        """Draft create → GROUP/PULSE SETUP (resume), invalidate bootstrap.

        If Group is already ACTIVE (an activated moment exists), keep GROUP/PULSE
        ACTIVE so Pulse does not resolve to a stale SETUP while Moments stays live.
        Draft resume is driven by session bootstrap draft fields on the client.
        """
        existing = await self.modules.get_state(user_id, "GROUP")
        if existing and (existing.state or "").upper() == "ACTIVE":
            await self.bootstrap.invalidate_cache(user_id)
            return
        await self.modules.set_state(user_id, "GROUP", "SETUP", "group_moment_draft")
        await self.modules.set_state(user_id, "PULSE", "SETUP", "group_moment_draft")
        await self.bootstrap.invalidate_cache(user_id)

    async def _flip_active(self, user_id: UUID) -> None:
        """Activate → GROUP/PULSE ACTIVE, invalidate bootstrap."""
        await self.modules.set_state(user_id, "GROUP", "ACTIVE", "group_moment")
        await self.modules.set_state(user_id, "PULSE", "ACTIVE", "group_moment")
        await self.modules.set_state(user_id, "MOMENTS", "ACTIVE", "group_moment")
        await self.bootstrap.invalidate_cache(user_id)

    # ----- generic building blocks --------------------------------------- #
    def _profiles_out(self, category: str) -> list[s.SharedProfileOut]:
        return [
            s.SharedProfileOut(
                profile_id=p.profile_id,
                profile_code=p.code,
                profile_name=p.name,
                profile_description=p.description,
                icon_name=p.icon_name,
                display_order=p.display_order,
            )
            for p in cat.profiles_for(category)
        ]

    @staticmethod
    def _enum_out(options: list[cat.EnumOption]) -> list[s.EnumOptionOut]:
        return [s.EnumOptionOut(code=o.code, label=o.label, description=o.description) for o in options]

    @staticmethod
    def _modules_out(options: list[cat.ModuleOption]) -> list[s.ModuleOptionOut]:
        return [
            s.ModuleOptionOut(
                module_code=m.code, module_label=m.label, icon_name=m.icon_name, is_default=m.is_default
            )
            for m in options
        ]

    async def profiles(self, category: str) -> dict:
        return s.ProfilesListResponse(profiles=self._profiles_out(category)).model_dump(mode="json")

    async def create_draft(self, user_id: UUID, category: str, profile_code: str) -> dict:
        moment = await self.moments.create(
            user_id=user_id,
            context_type=GROUP_CONTEXT,
            moment_type=category,
            title=_DEFAULT_NAME.get(category, "Our Moment"),
            status="DRAFT",
            setup_state="SETUP",
        )
        self._write_state(moment, {"profile_code": profile_code, "payload": {}})
        await self._flip_setup(user_id)
        return s.DraftCreateResponse(moment_id=str(moment.id), moment_type_code=category).model_dump(mode="json")

    async def save_draft(self, user_id: UUID, category: str, moment_id: UUID, payload: dict) -> dict:
        moment = await self._require(user_id, moment_id)
        state = self._read_state(moment)
        normalized = _normalize_payload(payload)
        merged = {**state.get("payload", {}), **normalized}
        if category == cat.EXPERIENCE:
            _validate_experience_dates(merged)
        profile_code = (
            normalized.get("experience_profile")
            or normalized.get("purchase_profile")
            or normalized.get("living_type")
            or state.get("profile_code")
        )
        name = normalized.get("moment_name") or normalized.get("living_name")
        if name:
            moment.title = name
        self._write_state(moment, {"profile_code": profile_code, "payload": merged})
        # Draft save must NOT invalidate bootstrap / reload module state.
        return await self.get_setup(user_id, category, moment_id)

    async def activate(self, user_id: UUID, category: str, moment_id: UUID) -> dict:
        moment = await self._require(user_id, moment_id)
        moment.status = "ACTIVE"
        moment.setup_state = "ACTIVE"
        moment.updated_at = datetime.now(timezone.utc)
        display_name = "You"
        try:
            from app.domains.users.models import UserModel
            from sqlalchemy import select

            result = await self.session.execute(select(UserModel).where(UserModel.id == user_id))
            user = result.scalar_one_or_none()
            if user and getattr(user, "display_name", None):
                display_name = str(user.display_name)
        except Exception:
            pass
        store.ensure_creator_organizer(moment, user_id, display_name=display_name)
        if category == cat.LIVING:
            state = self._read_state(moment)
            expected_residents = (state.get("payload") or {}).get("expected_residents")
            try:
                expected_residents = int(expected_residents) if expected_residents is not None else None
            except (TypeError, ValueError):
                expected_residents = None
            store.seed_pending_residents(moment, expected_residents)
        from app.domains.group.domain_row import ensure_group_moments_row

        await ensure_group_moments_row(
            self.session,
            moment,
            ensure_owner_member=True,
            owner_display_name=display_name,
        )
        await self._flip_active(user_id)
        if category == cat.EXPERIENCE:
            await SharedExperienceService(self.session).invalidate(user_id, moment_id, reason="activate")
        if category == cat.PURCHASE:
            await SharedPurchaseService(self.session).invalidate(user_id, moment_id, reason="activate")
        if category == cat.LIVING:
            await SharedLivingService(self.session).invalidate(user_id, moment_id, reason="activate")
        return s.ActivateResponse(
            moment_id=str(moment.id),
            lifecycle_status="active",
            orchestration_state="ACTIVE",
            activated_at=moment.updated_at.isoformat(),
            projection_status="REFRESHING",
        ).model_dump(mode="json")

    # ----- shared-experience --------------------------------------------- #
    async def get_setup(self, user_id: UUID, category: str, moment_id: UUID) -> dict:
        if category == cat.EXPERIENCE:
            return await self._experience_setup(user_id, moment_id)
        if category == cat.PURCHASE:
            return await self._purchase_setup(user_id, moment_id)
        return await self._living_setup(user_id, moment_id)

    async def preview(self, user_id: UUID, category: str, moment_id: UUID) -> dict:
        if category == cat.EXPERIENCE:
            return await self._experience_preview(user_id, moment_id)
        if category == cat.PURCHASE:
            return await self._purchase_preview(user_id, moment_id)
        return await self._living_preview(user_id, moment_id)

    async def _experience_setup(self, user_id: UUID, moment_id: UUID) -> dict:
        moment = await self._require(user_id, moment_id)
        state = self._read_state(moment)
        p = state.get("payload", {})
        code = state.get("profile_code")
        moment_name = moment.title or _DEFAULT_NAME[cat.EXPERIENCE]
        location = p.get("location")
        participants = p.get("expected_participants")
        money = p.get("money_tracking_mode") or "NO_MONEY"
        planning = p.get("planning_style") or "SIMPLE"
        saved = {
            "experience_profile": code,
            "experience_type": code,
            "moment_name": moment_name,
            "experience_name": moment_name,
            "trip_name": moment_name,
            "location": location,
            "destination": location,
            "start_date": p.get("start_date"),
            "end_date": p.get("end_date"),
            "description": p.get("description"),
            "expected_participants": participants,
            "participants": participants,
            "audience_tags": p.get("audience_tags") or [],
            "money_tracking_mode": money,
            "split_style": money,
            "planning_style": planning,
            "trip_style": code,
            "currency_code": p.get("currency_code") or "INR",
            "budget_currency": p.get("currency_code") or "INR",
            "allow_multi_currency": bool(p["allow_multi_currency"]) if "allow_multi_currency" in p else True,
            "estimated_budget": p.get("target_amount_major"),
            "target_amount_major": p.get("target_amount_major"),
            "enabled_modules": p.get("enabled_modules") or cat.default_modules(cat.EXPERIENCE),
            "participant_names": p.get("participant_names"),
        }
        return s.ExperienceSetupState(
            moment_id=str(moment.id),
            moment_type_code=cat.EXPERIENCE,
            lifecycle_status=(moment.status or "DRAFT").lower(),
            status=moment.status or "DRAFT",
            experience_profile=code,
            experience_type=code,
            profile_name=cat.profile_name(cat.EXPERIENCE, code) if code else None,
            moment_name=moment_name,
            experience_name=moment_name,
            trip_name=moment_name,
            location=location,
            destination=location,
            start_date=p.get("start_date"),
            end_date=p.get("end_date"),
            description=p.get("description"),
            expected_participants=participants,
            participants=participants,
            audience_tags=p.get("audience_tags") or [],
            money_tracking_mode=money,
            split_style=money,
            planning_style=planning,
            trip_style=code,
            currency_code=p.get("currency_code") or "INR",
            budget_currency=p.get("currency_code") or "INR",
            allow_multi_currency=bool(p["allow_multi_currency"]) if "allow_multi_currency" in p else True,
            estimated_budget=p.get("target_amount_major"),
            enabled_modules=p.get("enabled_modules") or cat.default_modules(cat.EXPERIENCE),
            default_modules=cat.default_modules(cat.EXPERIENCE),
            profiles=self._profiles_out(cat.EXPERIENCE),
            coordination_modules=self._modules_out(cat.EXPERIENCE_MODULES),
            audience_tag_options=[
                s.AudienceTagOptionOut(value_code=c, value_label=l) for c, l in cat.AUDIENCE_TAGS
            ],
            money_tracking_modes=self._enum_out(cat.MONEY_TRACKING_MODES),
            planning_styles=self._enum_out(cat.PLANNING_STYLES),
            saved_answers=saved,
            fields=[],
        ).model_dump(mode="json")

    async def _experience_preview(self, user_id: UUID, moment_id: UUID) -> dict:
        moment = await self._require(user_id, moment_id)
        state = self._read_state(moment)
        p = state.get("payload", {})
        code = state.get("profile_code") or ""
        mode = p.get("money_tracking_mode") or "NO_MONEY"
        style = p.get("planning_style") or "SIMPLE"
        modules = p.get("enabled_modules") or cat.default_modules(cat.EXPERIENCE)
        name = moment.title or _DEFAULT_NAME[cat.EXPERIENCE]
        location = p.get("location")
        insight = "You're all set — activate to bring this experience to life."
        blocks = _preview_blocks(
            [
                ("Shared Experience Name", name),
                ("Destination", location),
                ("Start", p.get("start_date")),
                ("End", p.get("end_date")),
                ("Participants", str(p.get("expected_participants")) if p.get("expected_participants") is not None else None),
                ("Budget currency", p.get("currency_code")),
                ("Estimated budget", str(p.get("target_amount_major")) if p.get("target_amount_major") is not None else None),
                ("Split style", cat.enum_label(cat.MONEY_TRACKING_MODES, mode)),
                ("Shared Experience Type", cat.profile_name(cat.EXPERIENCE, code)),
            ]
        )
        return s.ExperiencePreview(
            moment_id=str(moment.id),
            moment_name=name,
            experience_name=name,
            trip_name=name,
            profile_name=cat.profile_name(cat.EXPERIENCE, code),
            profile_code=code,
            experience_type=code,
            location=location,
            destination=location,
            start_date=p.get("start_date"),
            end_date=p.get("end_date"),
            expected_participants=p.get("expected_participants"),
            participants=p.get("expected_participants"),
            money_tracking_mode=mode,
            money_tracking_label=cat.enum_label(cat.MONEY_TRACKING_MODES, mode),
            split_style=mode,
            planning_style=style,
            planning_style_label=cat.enum_label(cat.PLANNING_STYLES, style),
            trip_style=code,
            currency_code=p.get("currency_code") or "INR",
            budget_currency=p.get("currency_code") or "INR",
            allow_multi_currency=bool(p["allow_multi_currency"]) if "allow_multi_currency" in p else True,
            estimated_budget=p.get("target_amount_major"),
            enabled_modules=modules,
            audience_tags=p.get("audience_tags") or [],
            insight_text=insight,
            narrative=insight,
            preview_blocks=blocks,
            identity_chips=[cat.profile_name(cat.EXPERIENCE, code), name],
            runtime_priorities=modules[:3],
        ).model_dump(mode="json")

    # ----- shared-purchase ----------------------------------------------- #
    async def _purchase_setup(self, user_id: UUID, moment_id: UUID) -> dict:
        moment = await self._require(user_id, moment_id)
        state = self._read_state(moment)
        p = state.get("payload", {})
        code = state.get("profile_code")
        moment_name = moment.title or _DEFAULT_NAME[cat.PURCHASE]
        funding = p.get("funding_style") or "SUGGESTED"
        ownership = p.get("ownership_style") or funding
        target_major = p.get("target_amount_major")
        contributors = p.get("expected_contributors")
        saved = {
            "purchase_profile": code,
            "moment_name": moment_name,
            "purchase_name": moment_name,
            "description": p.get("description"),
            "item_or_goal": p.get("description"),
            "currency_code": p.get("currency_code") or "INR",
            "allow_multi_currency": bool(p["allow_multi_currency"]) if "allow_multi_currency" in p else True,
            "target_amount_major": target_major,
            "expected_amount": target_major,
            "target_amount_minor": _to_minor(target_major),
            "target_date": p.get("target_date"),
            "decision_deadline": p.get("target_date"),
            "purchase_link": p.get("purchase_link"),
            "expected_contributors": contributors,
            "contributors": contributors,
            "funding_style": funding,
            "payment_plan": funding,
            "ownership_style": ownership,
            "enabled_modules": p.get("enabled_modules") or cat.default_modules(cat.PURCHASE),
        }
        return s.PurchaseSetupState(
            moment_id=str(moment.id),
            moment_type_code=cat.PURCHASE,
            lifecycle_status=(moment.status or "DRAFT").lower(),
            status=moment.status or "DRAFT",
            purchase_profile=code,
            profile_name=cat.profile_name(cat.PURCHASE, code) if code else None,
            moment_name=moment_name,
            purchase_name=moment_name,
            currency_code=p.get("currency_code") or "INR",
            allow_multi_currency=bool(p["allow_multi_currency"]) if "allow_multi_currency" in p else True,
            target_amount_minor=_to_minor(target_major),
            expected_amount=target_major,
            target_date=p.get("target_date"),
            decision_deadline=p.get("target_date"),
            purchase_link=p.get("purchase_link"),
            description=p.get("description"),
            item_or_goal=p.get("description"),
            expected_contributors=contributors,
            contributors=contributors,
            funding_style=funding,
            payment_plan=funding,
            ownership_style=ownership,
            enabled_modules=p.get("enabled_modules") or cat.default_modules(cat.PURCHASE),
            default_modules=cat.default_modules(cat.PURCHASE),
            profiles=self._profiles_out(cat.PURCHASE),
            purchase_modules=self._modules_out(cat.PURCHASE_MODULES),
            funding_styles=self._enum_out(cat.FUNDING_STYLES),
            saved_answers=saved,
            fields=[],
        ).model_dump(mode="json")

    async def _purchase_preview(self, user_id: UUID, moment_id: UUID) -> dict:
        moment = await self._require(user_id, moment_id)
        state = self._read_state(moment)
        p = state.get("payload", {})
        code = state.get("profile_code") or ""
        style = p.get("funding_style") or "SUGGESTED"
        name = moment.title or _DEFAULT_NAME[cat.PURCHASE]
        insight = "Everything's ready — activate to start collecting contributions."
        blocks = _preview_blocks(
            [
                ("Purchase name", name),
                ("Item / goal", p.get("description")),
                ("Amount", str(p.get("target_amount_major")) if p.get("target_amount_major") is not None else None),
                ("Currency", p.get("currency_code") or "INR"),
                ("Contributors", str(p.get("expected_contributors")) if p.get("expected_contributors") is not None else None),
                ("Payment plan", cat.enum_label(cat.FUNDING_STYLES, style)),
                ("Ownership", p.get("ownership_style")),
                ("Deadline", p.get("target_date")),
            ]
        )
        return s.PurchasePreview(
            moment_id=str(moment.id),
            moment_name=name,
            purchase_name=name,
            profile_name=cat.profile_name(cat.PURCHASE, code),
            profile_code=code,
            currency_code=p.get("currency_code") or "INR",
            target_amount_minor=_to_minor(p.get("target_amount_major")),
            expected_amount=p.get("target_amount_major"),
            target_date=p.get("target_date"),
            decision_deadline=p.get("target_date"),
            expected_contributors=p.get("expected_contributors"),
            contributors=p.get("expected_contributors"),
            funding_style=style,
            funding_style_label=cat.enum_label(cat.FUNDING_STYLES, style),
            payment_plan=style,
            ownership_style=p.get("ownership_style"),
            item_or_goal=p.get("description"),
            enabled_modules=p.get("enabled_modules") or cat.default_modules(cat.PURCHASE),
            insight_text=insight,
            narrative=insight,
            preview_blocks=blocks,
            identity_chips=[cat.profile_name(cat.PURCHASE, code), name],
            runtime_priorities=(p.get("enabled_modules") or cat.default_modules(cat.PURCHASE))[:3],
        ).model_dump(mode="json")

    # ----- shared-living -------------------------------------------------- #
    async def _living_setup(self, user_id: UUID, moment_id: UUID) -> dict:
        moment = await self._require(user_id, moment_id)
        state = self._read_state(moment)
        p = state.get("payload", {})
        code = state.get("profile_code")
        living_name = moment.title or _DEFAULT_NAME[cat.LIVING]
        management = p.get("management") or "SHARED"
        residents = p.get("expected_residents")
        budget = p.get("monthly_budget_major")
        saved = {
            "living_type": code,
            "living_profile": code,
            "living_name": living_name,
            "home_name": living_name,
            "location": p.get("location"),
            "move_in_date": p.get("move_in_date"),
            "monthly_budget_major": budget,
            "monthly_budget": budget,
            "currency_code": p.get("currency_code") or "INR",
            "allow_multi_currency": bool(p["allow_multi_currency"]) if "allow_multi_currency" in p else True,
            "management": management,
            "rent_split_style": management,
            "chores_style": p.get("chores_style"),
            "expected_residents": residents,
            "members": residents,
            "description": p.get("description"),
            "rules_or_notes": p.get("description"),
            "enabled_modules": p.get("enabled_modules") or cat.default_modules(cat.LIVING),
        }
        return s.LivingSetupState(
            moment_id=str(moment.id),
            moment_type_code=cat.LIVING,
            lifecycle_status=(moment.status or "DRAFT").lower(),
            status=moment.status or "DRAFT",
            living_type=code,
            profile_name=cat.profile_name(cat.LIVING, code) if code else None,
            living_name=living_name,
            home_name=living_name,
            location=p.get("location"),
            move_in_date=p.get("move_in_date"),
            monthly_budget=budget,
            currency_code=p.get("currency_code") or "INR",
            allow_multi_currency=bool(p["allow_multi_currency"]) if "allow_multi_currency" in p else True,
            management=management,
            rent_split_style=management,
            chores_style=p.get("chores_style"),
            expected_residents=residents,
            members=residents,
            description=p.get("description"),
            rules_or_notes=p.get("description"),
            profiles=self._profiles_out(cat.LIVING),
            management_styles=self._enum_out(cat.MANAGEMENT_STYLES),
            enabled_modules=p.get("enabled_modules") or cat.default_modules(cat.LIVING),
            default_modules=cat.default_modules(cat.LIVING),
            saved_answers=saved,
            fields=[],
        ).model_dump(mode="json")

    async def _living_preview(self, user_id: UUID, moment_id: UUID) -> dict:
        moment = await self._require(user_id, moment_id)
        state = self._read_state(moment)
        p = state.get("payload", {})
        code = state.get("profile_code") or ""
        management = p.get("management") or "SHARED"
        name = moment.title or _DEFAULT_NAME[cat.LIVING]
        insight = "Your home is ready — activate to start running it together."
        blocks = _preview_blocks(
            [
                ("Home name", name),
                ("Living type", cat.profile_name(cat.LIVING, code)),
                ("Members", str(p.get("expected_residents")) if p.get("expected_residents") is not None else None),
                ("Monthly budget", str(p.get("monthly_budget_major")) if p.get("monthly_budget_major") is not None else None),
                ("Currency", p.get("currency_code") or "INR"),
                ("Rent split", cat.enum_label(cat.MANAGEMENT_STYLES, management)),
                ("Chores", p.get("chores_style")),
                ("Notes", p.get("description")),
            ]
        )
        return s.LivingPreview(
            moment_id=str(moment.id),
            living_name=name,
            home_name=name,
            profile_name=cat.profile_name(cat.LIVING, code),
            profile_code=code,
            living_type=code,
            location=p.get("location"),
            move_in_date=p.get("move_in_date"),
            monthly_budget=p.get("monthly_budget_major"),
            currency_code=p.get("currency_code") or "INR",
            management=management,
            management_label=cat.enum_label(cat.MANAGEMENT_STYLES, management),
            rent_split_style=management,
            chores_style=p.get("chores_style"),
            expected_residents=p.get("expected_residents"),
            members=p.get("expected_residents"),
            rules_or_notes=p.get("description"),
            insight_text=insight,
            narrative=insight,
            preview_blocks=blocks,
            identity_chips=[cat.profile_name(cat.LIVING, code), name],
            runtime_priorities=(p.get("enabled_modules") or cat.default_modules(cat.LIVING))[:3],
        ).model_dump(mode="json")
