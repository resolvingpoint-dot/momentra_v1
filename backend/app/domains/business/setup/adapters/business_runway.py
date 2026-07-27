"""Business Runway setup adapter (Run 4)."""
from __future__ import annotations

import logging
from datetime import datetime, timezone
from typing import Any
from uuid import UUID, uuid4

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.domains.business.catalog import BUSINESS_RUNWAY
from app.domains.business.models import (
    BusinessMomentGovernance,
    BusinessMomentInvitations,
    BusinessMomentMembers,
    BusinessMomentSetup,
    BusinessMoments,
)
from app.domains.business.setup.business_moment_sync import ensure_business_moment
from app.domains.business.setup.business_runway_sync import (
    upsert_runway_governance,
    upsert_runway_setup,
    upsert_runway_structure,
)
from app.domains.business.setup.runway_mappers import (
    BUSINESS_STAGE_CANONICAL,
    REVENUE_STATUS_CANONICAL,
    compute_derived_preview,
    normalize_runway_answers,
)
from app.domains.business.setup.runway_permissions import member_permission_flags
from app.domains.business.setup.schemas import SetupPreviewResponse, SetupSummaryBlock
from app.domains.moments.models import MomentModel

logger = logging.getLogger(__name__)

_KNOWN_CURRENCY = {
    "USD", "EUR", "GBP", "INR", "JPY", "AUD", "CAD", "CHF", "CNY", "HKD",
    "SGD", "NZD", "SEK", "NOK", "DKK", "ZAR", "AED", "SAR", "KWD", "BHD",
    "OMR", "QAR", "MXN", "BRL", "KRW", "TRY", "PLN", "THB", "MYR", "IDR",
    "PHP", "VND", "PKR", "BDT", "NGN", "EGP", "ILS",
}

_VISIBILITY_TO_GOV = {
    "PRIVATE": "private",
    "TEAM": "leadership",
    "LEADERSHIP": "leadership",
    "ORGANIZATION": "organization",
    "ORG": "organization",
}

_VISIBILITY_TO_SETUP = {
    "PRIVATE": None,
    "TEAM": "team_only",
    "LEADERSHIP": "leadership",
    "ORGANIZATION": "organization",
    "ORG": "organization",
}


def _now() -> datetime:
    return datetime.now(timezone.utc).replace(tzinfo=None)


def _members(answers: dict[str, Any]) -> list[dict[str, Any]]:
    raw = answers.get("members") or answers.get("member_drafts") or []
    return [m for m in raw if isinstance(m, dict)]


def _member_ids(answers: dict[str, Any]) -> set[str]:
    ids: set[str] = set()
    for m in _members(answers):
        if m.get("local_id"):
            ids.add(str(m["local_id"]))
        if m.get("user_id"):
            ids.add(str(m["user_id"]))
    return ids


def _approvals_enabled(answers: dict[str, Any]) -> bool:
    return bool(
        answers.get("approval_required_for_funding_changes")
        or answers.get("approval_required_for_cash_adjustments")
        or answers.get("approval_required_for_large_expenses")
        or answers.get("approval_required_for_threshold_changes")
    )


def _has_finance_lead(answers: dict[str, Any]) -> bool:
    return any(
        m.get("is_finance_lead") or str(m.get("role") or "").upper() == "FINANCE_LEAD"
        for m in _members(answers)
    )


def _member_column_flags(member: dict[str, Any]) -> dict[str, bool]:
    """Map runway permission flags onto BusinessMomentMembers columns."""
    role = str(member.get("role") or "CONTRIBUTOR").upper()
    raw = member_permission_flags(
        role,
        is_finance_lead=bool(member.get("is_finance_lead")),
        is_operations_lead=bool(member.get("is_operations_lead")),
        is_advisor=bool(member.get("is_advisor")),
        is_observer=bool(member.get("is_observer")),
    )
    return {
        "is_team_lead": bool(raw.get("is_team_lead")),
        "is_budget_owner": bool(raw.get("is_budget_owner")),
        "can_edit_own_entries": bool(raw.get("can_edit_own_entries")),
        "can_edit_team_entries": bool(raw.get("can_edit_team_entries")),
        "can_add_runway_transactions": bool(raw.get("can_add_runway_transactions")),
        "can_edit_financial_entries": bool(raw.get("can_view_all_financials")),
        "can_approve_runway_changes": bool(raw.get("can_approve_requests")),
        "can_manage_runway_settings": role in {"OWNER", "FOUNDER", "FINANCE_LEAD"}
        or bool(member.get("is_finance_lead")),
    }


class BusinessRunwayAdapter:
    moment_type_code = BUSINESS_RUNWAY
    template_id = "business_runway"

    def __init__(self, session: AsyncSession | None = None) -> None:
        self.session = session

    def bind(self, session: AsyncSession) -> "BusinessRunwayAdapter":
        self.session = session
        return self

    def normalize_answers(
        self,
        answers: dict[str, Any],
        *,
        owner_user_id: str | None = None,
        owner_display_name: str | None = None,
    ) -> dict[str, Any]:
        return normalize_runway_answers(
            answers,
            owner_user_id=owner_user_id,
            owner_display_name=owner_display_name,
        )

    def validate_draft(self, answers: dict[str, Any]) -> list[str]:
        warnings: list[str] = []

        burn = answers.get("monthly_burn_minor")
        if burn is not None and int(burn) == 0:
            warnings.append("monthly_burn_minor is zero")

        if not _has_finance_lead(answers):
            warnings.append("no finance lead designated")

        revenue_status = answers.get("revenue_status")
        if revenue_status and revenue_status != "NO_REVENUE":
            if answers.get("estimated_monthly_revenue_minor") is None:
                warnings.append(
                    "estimated_monthly_revenue_minor recommended when revenue_status is not NO_REVENUE"
                )

        goal = answers.get("runway_goal_months")
        alert = answers.get("runway_alert_threshold_months")
        if goal is not None and alert is not None and int(goal) < int(alert):
            warnings.append("runway_goal_months is less than runway_alert_threshold_months")

        cash = answers.get("current_cash_minor")
        if cash is not None and int(cash) == 0:
            warnings.append("current_cash_minor is zero")

        funding = answers.get("funding_sources") or []
        if not funding:
            warnings.append("no funding sources")

        burn_categories = answers.get("burn_categories") or []
        if not burn_categories:
            warnings.append("no burn categories")

        return warnings

    def activation_errors(self, answers: dict[str, Any], *, owner_user_id: str | None = None) -> list[str]:
        errors: list[str] = []

        moment_name = (answers.get("moment_name") or "").strip()
        runway_name = (answers.get("runway_name") or "").strip()
        if not moment_name and not runway_name:
            errors.append("moment_name or runway_name is required")
        if not runway_name:
            errors.append("runway_name is required")

        stage = answers.get("business_stage")
        if not stage or stage not in BUSINESS_STAGE_CANONICAL:
            errors.append("business_stage is required")

        currency = (answers.get("operating_currency_code") or answers.get("default_currency_code") or "").upper()
        if not currency:
            errors.append("operating_currency_code is required")
        elif currency not in _KNOWN_CURRENCY:
            errors.append(f"invalid operating currency: {currency}")

        tz = answers.get("timezone")
        if tz is None or str(tz).strip() == "":
            errors.append("timezone is required")

        goal = answers.get("runway_goal_months")
        if goal is None or int(goal) <= 0:
            errors.append("runway_goal_months must be greater than 0")

        cash = answers.get("current_cash_minor")
        if cash is None or int(cash) < 0:
            errors.append("current_cash_minor must be >= 0")

        burn = answers.get("monthly_burn_minor")
        if burn is None or int(burn) < 0:
            errors.append("monthly_burn_minor must be >= 0")

        revenue_status = answers.get("revenue_status")
        if not revenue_status or revenue_status not in REVENUE_STATUS_CANONICAL:
            errors.append("revenue_status is required")

        members = _members(answers)
        if owner_user_id:
            owner_ok = any(
                str(m.get("user_id") or "") == str(owner_user_id) and m.get("role") == "OWNER"
                for m in members
            )
            if not owner_ok:
                errors.append("owner member (authenticated user) is required")
        elif not any(m.get("role") == "OWNER" for m in members):
            errors.append("owner is required")

        alert = answers.get("runway_alert_threshold_months")
        if alert is None or int(alert) <= 0:
            errors.append("runway_alert_threshold_months must be greater than 0")

        large = answers.get("large_expense_threshold_minor")
        if large is not None and int(large) < 0:
            errors.append("large_expense_threshold_minor cannot be negative")

        ids = _member_ids(answers)
        if _approvals_enabled(answers):
            approval_owner = answers.get("approval_owner_id")
            if not approval_owner or str(approval_owner) not in ids:
                errors.append("approval_owner_id must be an included member")

        return errors

    def validate_activation(self, answers: dict[str, Any], *, owner_user_id: str | None = None) -> list[str]:
        return self.activation_errors(answers, owner_user_id=owner_user_id)

    def build_preview(
        self,
        answers: dict[str, Any],
        *,
        owner_user_id: str | None = None,
    ) -> SetupPreviewResponse:
        members = _members(answers)
        blocking = self.activation_errors(answers, owner_user_id=owner_user_id)
        warnings = self.validate_draft(answers)
        derived = compute_derived_preview(answers)

        owner = next((m for m in members if m.get("role") == "OWNER"), None)
        finance_leads = [
            m for m in members
            if m.get("is_finance_lead") or str(m.get("role") or "").upper() == "FINANCE_LEAD"
        ]
        pending_invites = [
            m for m in members
            if m.get("role") != "OWNER" and (m.get("invite_status") or "DRAFT") != "ACCEPTED"
        ]

        blocks = [
            SetupSummaryBlock(
                block_id="runway_identity",
                title="Runway Identity",
                body=str(answers.get("runway_name") or answers.get("moment_name") or ""),
                items=[
                    {"label": "Moment name", "value": answers.get("moment_name")},
                    {"label": "Runway name", "value": answers.get("runway_name")},
                    {"label": "Business stage", "value": answers.get("business_stage")},
                    {"label": "Owner", "value": (owner or {}).get("name") or (owner or {}).get("user_id")},
                    {"label": "Currency", "value": answers.get("operating_currency_code")},
                    {"label": "Country", "value": answers.get("country_code")},
                    {"label": "Locale", "value": answers.get("locale")},
                    {"label": "Timezone", "value": answers.get("timezone")},
                    {"label": "Runway goal (months)", "value": answers.get("runway_goal_months")},
                ],
            ),
            SetupSummaryBlock(
                block_id="financial_structure",
                title="Financial Structure",
                body=str(answers.get("revenue_status") or ""),
                items=[
                    {"label": "Current cash (minor)", "value": answers.get("current_cash_minor")},
                    {"label": "Monthly burn (minor)", "value": answers.get("monthly_burn_minor")},
                    {"label": "Revenue status", "value": answers.get("revenue_status")},
                    {
                        "label": "Estimated monthly revenue (minor)",
                        "value": answers.get("estimated_monthly_revenue_minor"),
                    },
                    {"label": "Collection rate %", "value": answers.get("collection_rate_percent")},
                    {
                        "label": "Alert threshold (months)",
                        "value": answers.get("runway_alert_threshold_months"),
                    },
                    {"label": "Burn categories", "value": answers.get("burn_categories")},
                    {"label": "Revenue model", "value": answers.get("revenue_model")},
                    {"label": "Funding sources", "value": answers.get("funding_sources")},
                    {
                        "label": "Estimated runway (months)",
                        "value": derived.get("estimated_runway_months"),
                    },
                    {
                        "label": "Net monthly burn (minor)",
                        "value": derived.get("net_monthly_burn_minor"),
                    },
                    {"label": "Goal gap (months)", "value": derived.get("goal_gap_months")},
                ],
            ),
            SetupSummaryBlock(
                block_id="members",
                title="Participants & Responsibilities",
                body=f"{len(members)} members",
                items=[
                    {"label": "Member count", "value": len(members)},
                    {
                        "label": "Finance lead",
                        "value": (finance_leads[0].get("name") if finance_leads else None),
                    },
                    {"label": "Supported roles", "value": answers.get("supported_roles")},
                    {"label": "Visibility", "value": answers.get("visibility")},
                    {"label": "Invitation pending", "value": len(pending_invites)},
                    {
                        "label": "Invite on activation",
                        "value": answers.get("invite_on_activation"),
                    },
                ],
            ),
            SetupSummaryBlock(
                block_id="governance",
                title="Governance",
                body=str(answers.get("visibility") or ""),
                items=[
                    {
                        "label": "Funding-change approval",
                        "value": answers.get("approval_required_for_funding_changes"),
                    },
                    {
                        "label": "Cash-adjustment approval",
                        "value": answers.get("approval_required_for_cash_adjustments"),
                    },
                    {
                        "label": "Large-expense approval",
                        "value": answers.get("approval_required_for_large_expenses"),
                    },
                    {
                        "label": "Threshold-change approval",
                        "value": answers.get("approval_required_for_threshold_changes"),
                    },
                    {
                        "label": "Large expense threshold (minor)",
                        "value": answers.get("large_expense_threshold_minor"),
                    },
                    {"label": "Approval owner", "value": answers.get("approval_owner_id")},
                    {"label": "Visibility", "value": answers.get("visibility")},
                    {"label": "Notify members", "value": answers.get("notify_members")},
                ],
            ),
        ]
        return SetupPreviewResponse(
            template_id=self.template_id,
            moment_type_code=self.moment_type_code,
            summary_blocks=blocks,
            warnings=warnings,
            blocking_errors=blocking,
            activation_ready=len(blocking) == 0,
            derived_preview=derived,
        )

    async def commit_profile(self, *, moment_id: str, user_id: str, answers: dict[str, Any]) -> None:
        assert self.session is not None
        session = self.session
        mid = UUID(moment_id)
        uid = UUID(user_id)

        shared = None
        try:
            res = await session.execute(select(MomentModel).where(MomentModel.id == mid))
            shared = res.scalar_one_or_none()
        except Exception:
            shared = None
        if shared is None or not isinstance(shared, MomentModel):
            shared = MomentModel(
                id=mid,
                user_id=uid,
                context_type="BUSINESS",
                moment_type=BUSINESS_RUNWAY,
                title=str(answers.get("moment_name") or answers.get("runway_name") or "Runway"),
                status="DRAFT",
            )

        await ensure_business_moment(session, shared, owner_user_id=uid, answers=answers)

        stage = str(answers.get("business_stage") or "CUSTOM")
        currency = (answers.get("operating_currency_code") or "INR").upper()
        vis_raw = str(answers.get("visibility") or "TEAM").upper()
        visibility_legacy = _VISIBILITY_TO_SETUP.get(vis_raw)
        extras = {
            "runway_name": answers.get("runway_name"),
            "moment_name": answers.get("moment_name"),
            "business_stage": answers.get("business_stage"),
            "revenue_status": answers.get("revenue_status"),
            "runway_goal_months": answers.get("runway_goal_months"),
            "current_cash_minor": answers.get("current_cash_minor"),
            "monthly_burn_minor": answers.get("monthly_burn_minor"),
            "estimated_monthly_revenue_minor": answers.get("estimated_monthly_revenue_minor"),
            "allow_multi_currency": answers.get("allow_multi_currency"),
            "financial_year_start": answers.get("financial_year_start"),
            "default_currency_code": answers.get("default_currency_code"),
            "visibility": answers.get("visibility"),
            "notification_preferences": answers.get("notification_preferences") or {},
        }

        result = await session.execute(
            select(BusinessMomentSetup).where(BusinessMomentSetup.moment_id == mid)
        )
        row = result.scalar_one_or_none()
        now = _now()
        payload = {
            "purpose": stage[:100] or "runway",
            "custom_purpose": (answers.get("runway_name") or None),
            "team_size": "just_me",
            "budget_enabled": False,
            "currency": currency,
            "work_style": None,
            "visibility": visibility_legacy,
            "team_owner_user_id": uid,
            "team_name": (answers.get("runway_name") or None),
            "country_code": answers.get("country_code"),
            "locale": answers.get("locale"),
            "timezone": answers.get("timezone"),
            "review_cycle": None,
            "monthly_budget_minor": None,
            "setup_extras": extras,
            "updated_at": now,
        }
        if row is None:
            session.add(BusinessMomentSetup(moment_id=mid, created_at=now, **payload))
        else:
            for k, v in payload.items():
                setattr(row, k, v)
        await session.flush()

        await upsert_runway_setup(
            session,
            moment_id=mid,
            owner_user_id=uid,
            answers=answers,
        )

        biz = await session.execute(select(BusinessMoments).where(BusinessMoments.moment_id == mid))
        biz_row = biz.scalar_one_or_none()
        if biz_row is not None:
            biz_row.moment_name = str(
                answers.get("moment_name")
                or answers.get("runway_name")
                or biz_row.moment_name
            )[:255]
            # Never downgrade an already-active SQL root; activate promotes via ensure_business_moment.
            if (biz_row.status or "").lower() != "active":
                biz_row.status = "configured"
            biz_row.updated_at = now
            await session.flush()

    async def commit_governance(self, *, moment_id: str, user_id: str, answers: dict[str, Any]) -> None:
        assert self.session is not None
        session = self.session
        mid = UUID(moment_id)
        now = _now()

        await upsert_runway_structure(session, moment_id=mid, answers=answers)
        await upsert_runway_governance(session, moment_id=mid, answers=answers)

        approval_enabled = _approvals_enabled(answers)
        vis = str(answers.get("visibility") or "TEAM").upper()
        gov_vis = _VISIBILITY_TO_GOV.get(vis, "leadership")
        prefs = (
            answers.get("notification_preferences")
            if isinstance(answers.get("notification_preferences"), dict)
            else {}
        )

        gov_result = await session.execute(
            select(BusinessMomentGovernance).where(BusinessMomentGovernance.moment_id == mid)
        )
        governance = gov_result.scalar_one_or_none()
        g_payload = {
            "send_invites_on_activation": bool(answers.get("invite_on_activation", True)),
            "operational_visibility": gov_vis,
            "notify_approvals": bool(prefs.get("approvals", True)),
            "notify_spending_activity": bool(prefs.get("spending", True)),
            "notify_issues_risks": bool(prefs.get("issues", True)),
            "notify_team_updates": bool(answers.get("notify_members", True)),
            "approval_enabled": approval_enabled,
            "runway_approval_required": approval_enabled,
            "activation_ready": True,
            "activated_by": UUID(user_id),
            "activated_at": now,
            "runway_visibility_roles": {"visibility": answers.get("visibility")},
            "runway_alert_roles": {"roles": ["OWNER", "FINANCE_LEAD"]},
            "runway_alert_conditions": {
                "runway_alert_threshold_months": answers.get("runway_alert_threshold_months"),
            },
            "runway_approval_rules": {
                "large_expense_threshold_minor": answers.get("large_expense_threshold_minor"),
                "approval_owner_id": answers.get("approval_owner_id"),
                "approval_required_for_funding_changes": answers.get(
                    "approval_required_for_funding_changes"
                ),
                "approval_required_for_cash_adjustments": answers.get(
                    "approval_required_for_cash_adjustments"
                ),
                "approval_required_for_large_expenses": answers.get(
                    "approval_required_for_large_expenses"
                ),
                "approval_required_for_threshold_changes": answers.get(
                    "approval_required_for_threshold_changes"
                ),
            },
            "updated_at": now,
        }
        if governance is None:
            session.add(BusinessMomentGovernance(moment_id=mid, created_at=now, **g_payload))
        else:
            for k, v in g_payload.items():
                setattr(governance, k, v)
        await session.flush()

    async def commit_members(self, *, moment_id: str, user_id: str, answers: dict[str, Any]) -> None:
        assert self.session is not None
        session = self.session
        mid = UUID(moment_id)
        uid = UUID(user_id)
        now = _now()
        members = _members(answers)

        existing = await session.execute(
            select(BusinessMomentMembers).where(BusinessMomentMembers.moment_id == mid)
        )
        try:
            rows = list(existing.scalars().all())
        except Exception:
            rows = []
        by_local = {str(r.local_id): r for r in rows if getattr(r, "local_id", None)}
        by_user = {str(r.user_id): r for r in rows if getattr(r, "user_id", None)}

        for m in members:
            local_id = str(m.get("local_id") or uuid4())
            role = str(m.get("role") or "CONTRIBUTOR").upper()
            flags = _member_column_flags(m)
            member_user = None
            if m.get("user_id"):
                try:
                    member_user = UUID(str(m["user_id"]))
                except ValueError:
                    member_user = None

            is_owner = role == "OWNER" and member_user == uid
            status = "active" if is_owner or (m.get("invite_status") or "").upper() == "ACCEPTED" else "invited"
            if (m.get("invite_status") or "").upper() == "DRAFT":
                status = "configured"

            row = by_local.get(local_id) or (by_user.get(str(member_user)) if member_user else None)
            payload = {
                "name": str(m.get("name") or role)[:255],
                "role": role,
                "member_status": status,
                "added_by": uid,
                "user_id": member_user,
                "email": m.get("email"),
                "mobile": m.get("phone"),
                "local_id": local_id,
                "permission_profile": m.get("permission_profile"),
                "permission_version": int(m.get("permission_version") or 1),
                "updated_at": now,
                **flags,
            }
            if row is None:
                session.add(BusinessMomentMembers(moment_id=mid, created_at=now, **payload))
            else:
                for k, v in payload.items():
                    setattr(row, k, v)

        await session.flush()

        existing2 = await session.execute(
            select(BusinessMomentMembers).where(BusinessMomentMembers.moment_id == mid)
        )
        try:
            member_rows = list(existing2.scalars().all())
        except Exception:
            member_rows = []
        local_to_member = {str(r.local_id): r for r in member_rows if r.local_id}

        inv_existing = await session.execute(
            select(BusinessMomentInvitations).where(BusinessMomentInvitations.moment_id == mid)
        )
        try:
            inv_rows = list(inv_existing.scalars().all())
        except Exception:
            inv_rows = []
        inv_index = {
            (str(r.local_id), str(r.channel or r.invite_method).upper()): r
            for r in inv_rows
            if r.local_id and (r.channel or r.invite_method)
        }

        for m in members:
            if (m.get("role") or "").upper() == "OWNER":
                continue
            local_id = str(m.get("local_id"))
            channel = str(m.get("invite_method") or "EMAIL").upper()
            target = m.get("email") or m.get("phone") or local_id
            method = {
                "EMAIL": "email",
                "SMS": "mobile",
                "WHATSAPP": "mobile",
                "QR": "qr",
                "SHARE": "qr",
                "COPY_LINK": "qr",
                "NATIVE_SHARE": "qr",
            }.get(channel, "email")
            key = (local_id, channel)
            member_row = local_to_member.get(local_id)
            if key in inv_index:
                inv = inv_index[key]
                inv.invite_target = str(target)[:255]
                inv.invite_method = method
                inv.channel = channel
                inv.member_id = member_row.member_id if member_row else inv.member_id
                inv.updated_at = now
                continue
            session.add(
                BusinessMomentInvitations(
                    moment_id=mid,
                    invite_method=method,
                    invite_status="pending",
                    invite_target=str(target)[:255],
                    send_on_activation=bool(answers.get("invite_on_activation", True)),
                    member_id=member_row.member_id if member_row else None,
                    local_id=local_id,
                    channel=channel,
                    send_idempotency_key=f"{mid}:{local_id}:{channel}",
                    created_at=now,
                    updated_at=now,
                )
            )
        await session.flush()

    async def deliver_invites_best_effort(self, *, moment_id: str, answers: dict[str, Any]) -> None:
        """Post-commit invite delivery — failures never raise."""
        if not bool(answers.get("invite_on_activation", True)):
            return
        if self.session is None:
            return
        try:
            from app.domains.business.setup.invites import deliver_pending_invites

            await deliver_pending_invites(self.session, moment_id=UUID(moment_id), answers=answers)
        except Exception as exc:  # noqa: BLE001
            logger.warning("Business Runway invite delivery failed (non-blocking): %s", exc)
