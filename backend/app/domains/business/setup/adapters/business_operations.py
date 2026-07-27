"""Business Operations setup adapter (Run 5)."""
from __future__ import annotations

import logging
from datetime import datetime, timezone
from typing import Any
from uuid import UUID, uuid4

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.domains.business.catalog import BUSINESS_OPERATIONS
from app.domains.business.models import (
    BusinessMomentGovernance,
    BusinessMomentInvitations,
    BusinessMomentMembers,
    BusinessMomentSetup,
    BusinessMoments,
)
from app.domains.business.setup.business_moment_sync import ensure_business_moment
from app.domains.business.setup.business_operations_mappers import (
    APPROVAL_MODEL_CANONICAL,
    OPERATING_MODEL_CANONICAL,
    OPERATIONS_SCOPE_CANONICAL,
    REVIEW_CYCLE_CANONICAL,
    compute_derived_preview,
    normalize_operations_answers,
)
from app.domains.business.setup.business_operations_permissions import member_permission_flags
from app.domains.business.setup.business_operations_sync import (
    upsert_budget_allocations,
    upsert_operations_governance,
    upsert_operations_setup,
    upsert_operations_structure,
)
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

_APPROVAL_MODELS_NEEDING_OWNER = {
    "SINGLE_APPROVER",
    "MULTI_APPROVER",
    "THRESHOLD_BASED",
    "ROLE_BASED",
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


def _allocations(answers: dict[str, Any]) -> list[dict[str, Any]]:
    raw = answers.get("budget_allocations") or []
    return [a for a in raw if isinstance(a, dict)] if isinstance(raw, list) else []


def _has_budget_controller(answers: dict[str, Any]) -> bool:
    return any(
        m.get("is_budget_controller")
        or str(m.get("role") or "").upper() in {"BUDGET_CONTROLLER", "FINANCE_LEAD"}
        for m in _members(answers)
    )


def _has_operations_lead(answers: dict[str, Any]) -> bool:
    return any(
        m.get("is_operations_lead") or str(m.get("role") or "").upper() == "OPERATIONS_LEAD"
        for m in _members(answers)
    )


def _has_vendor_manager(answers: dict[str, Any]) -> bool:
    return any(
        m.get("is_vendor_manager") or str(m.get("role") or "").upper() == "VENDOR_MANAGER"
        for m in _members(answers)
    )


def _approver_count(answers: dict[str, Any]) -> int:
    return sum(
        1
        for m in _members(answers)
        if m.get("is_approver") or str(m.get("role") or "").upper() == "APPROVER"
    )


def _member_column_flags(member: dict[str, Any]) -> dict[str, bool]:
    """Map operations permission flags onto BusinessMomentMembers columns."""
    role = str(member.get("role") or "MEMBER").upper()
    raw = member_permission_flags(
        role,
        is_approver=bool(member.get("is_approver")),
        is_budget_controller=bool(member.get("is_budget_controller")),
        is_operations_lead=bool(member.get("is_operations_lead")),
        is_vendor_manager=bool(member.get("is_vendor_manager")),
        is_observer=bool(member.get("is_observer")),
    )
    return {
        "is_team_lead": bool(raw.get("is_team_lead")),
        "is_budget_owner": bool(raw.get("is_budget_owner")),
        "can_edit_own_entries": bool(raw.get("can_edit_own_entries")),
        "can_edit_team_entries": bool(raw.get("can_edit_team_entries")),
        "can_edit_expense_entries": bool(raw.get("is_budget_owner")),
        "can_add_operations_records": role != "OBSERVER" and not bool(member.get("is_observer")),
        "can_edit_operations_records": role in {"OWNER", "ADMIN", "OPERATIONS_LEAD"}
        or bool(member.get("is_operations_lead")),
        "can_edit_own_operations_records": role != "OBSERVER" and not bool(member.get("is_observer")),
        "can_approve_operations_requests": bool(raw.get("can_approve_requests")),
        "can_delete_operations_records": role in {"OWNER", "ADMIN"},
        "can_manage_operations_settings": role in {"OWNER", "ADMIN"},
        "can_edit_financial_entries": bool(raw.get("is_budget_owner")),
    }


class BusinessOperationsAdapter:
    moment_type_code = BUSINESS_OPERATIONS
    template_id = "business_operations"

    def __init__(self, session: AsyncSession | None = None) -> None:
        self.session = session

    def bind(self, session: AsyncSession) -> "BusinessOperationsAdapter":
        self.session = session
        return self

    def normalize_answers(
        self,
        answers: dict[str, Any],
        *,
        owner_user_id: str | None = None,
        owner_display_name: str | None = None,
    ) -> dict[str, Any]:
        return normalize_operations_answers(
            answers,
            owner_user_id=owner_user_id,
            owner_display_name=owner_display_name,
        )

    def validate_draft(self, answers: dict[str, Any]) -> list[str]:
        warnings: list[str] = []

        if not _has_budget_controller(answers):
            warnings.append("no budget controller designated")

        if not _has_operations_lead(answers):
            warnings.append("no operations lead designated")

        vendor = answers.get("vendor_dependency_level")
        if vendor in {"HIGH", "CRITICAL"} and not _has_vendor_manager(answers):
            warnings.append(
                "vendor manager recommended when vendor_dependency_level is HIGH or CRITICAL"
            )

        monitoring = answers.get("monitoring_level")
        alert_ids = answers.get("alert_recipient_ids") or []
        if monitoring == "REAL_TIME" and not alert_ids:
            warnings.append("alert recipients recommended when monitoring_level is REAL_TIME")

        budget = answers.get("monthly_budget_minor")
        allocations = _allocations(answers)
        if budget is not None and int(budget) > 0 and not allocations:
            warnings.append("budget enabled but no allocations")

        approval_model = answers.get("approval_model")
        if (
            approval_model
            and approval_model != "NONE"
            and _approver_count(answers) == 0
            and approval_model != "OWNER_ONLY"
        ):
            warnings.append("approval model enabled but only OWNER can approve")

        if not answers.get("escalation_contact_id"):
            warnings.append("no issue escalation contact")

        if answers.get("allow_multi_currency") and not (
            answers.get("default_currency_code") or answers.get("operating_currency_code")
        ):
            warnings.append("multi-currency enabled without default currency")

        if budget is not None and int(budget) == 0:
            warnings.append("monthly_budget_minor is zero")

        return warnings

    def activation_errors(self, answers: dict[str, Any], *, owner_user_id: str | None = None) -> list[str]:
        errors: list[str] = []

        moment_name = (answers.get("moment_name") or "").strip()
        operations_name = (answers.get("operations_name") or "").strip()
        if not moment_name:
            errors.append("moment_name is required")
        if not operations_name:
            errors.append("operations_name is required")

        scope = answers.get("operations_scope")
        if not scope or scope not in OPERATIONS_SCOPE_CANONICAL:
            errors.append("operations_scope is required")

        model = answers.get("operating_model")
        if not model or model not in OPERATING_MODEL_CANONICAL:
            errors.append("operating_model is required")

        currency = (
            answers.get("operating_currency_code") or answers.get("default_currency_code") or ""
        ).upper()
        if not currency:
            errors.append("operating_currency_code is required")
        elif currency not in _KNOWN_CURRENCY:
            errors.append(f"invalid operating currency: {currency}")

        tz = answers.get("timezone")
        if tz is None or str(tz).strip() == "":
            errors.append("timezone is required")

        review = answers.get("review_cycle")
        if not review or review not in REVIEW_CYCLE_CANONICAL:
            errors.append("review_cycle is required")

        budget = answers.get("monthly_budget_minor")
        if budget is None or int(budget) < 0:
            errors.append("monthly_budget_minor must be >= 0")

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

        roles = answers.get("supported_roles") or []
        if isinstance(roles, list) and "OWNER" not in [str(r).upper() for r in roles]:
            errors.append("supported_roles must include OWNER")

        allocations = _allocations(answers)
        allocated_total = 0
        for a in allocations:
            amount = a.get("amount_minor")
            if amount is not None and int(amount) < 0:
                errors.append("allocation amounts cannot be negative")
                break
            allocated_total += int(amount or 0)

        budget_i = int(budget) if budget is not None else 0
        allow_over = bool(answers.get("allow_overallocation"))
        if not allow_over and budget is not None and allocated_total > budget_i:
            errors.append("allocations total exceeds monthly_budget_minor")

        mode = str(answers.get("allocation_mode") or "FIXED_AMOUNT").upper()
        if mode == "PERCENTAGE" and allocations:
            pct_total = sum(int(a.get("percentage") or 0) for a in allocations)
            if pct_total != 100:
                errors.append("percentage allocations must total 100")

        approval_model = answers.get("approval_model")
        if approval_model and approval_model not in APPROVAL_MODEL_CANONICAL:
            errors.append("approval_model is invalid")

        ids = _member_ids(answers)
        if approval_model in _APPROVAL_MODELS_NEEDING_OWNER:
            approval_owner = answers.get("approval_owner_id")
            if not approval_owner or str(approval_owner) not in ids:
                errors.append("approval_owner_id must be an included member")

        threshold = answers.get("approval_threshold_minor")
        if threshold is not None and int(threshold) < 0:
            errors.append("approval_threshold_minor cannot be negative")

        escalation = answers.get("escalation_contact_id")
        if escalation and str(escalation) not in ids:
            errors.append("escalation_contact_id must be an included member")

        for rid in answers.get("alert_recipient_ids") or []:
            if str(rid) not in ids:
                errors.append("alert_recipient_ids must be included members")
                break

        for sid in answers.get("secondary_approver_ids") or []:
            if str(sid) not in ids:
                errors.append("secondary_approver_ids must be included members")
                break

        if not answers.get("confirm_budget"):
            errors.append("confirm_budget is required")
        if not answers.get("confirm_governance"):
            errors.append("confirm_governance is required")
        if not answers.get("confirm_members"):
            errors.append("confirm_members is required")

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
        ops_leads = [
            m
            for m in members
            if m.get("is_operations_lead") or str(m.get("role") or "").upper() == "OPERATIONS_LEAD"
        ]
        budget_controllers = [
            m
            for m in members
            if m.get("is_budget_controller")
            or str(m.get("role") or "").upper() in {"BUDGET_CONTROLLER", "FINANCE_LEAD"}
        ]
        pending_invites = [
            m
            for m in members
            if m.get("role") != "OWNER" and (m.get("invite_status") or "DRAFT") != "ACCEPTED"
        ]

        blocks = [
            SetupSummaryBlock(
                block_id="operations_identity",
                title="Operations Identity",
                body=str(answers.get("operations_name") or answers.get("moment_name") or ""),
                items=[
                    {"label": "Moment name", "value": answers.get("moment_name")},
                    {"label": "Operations name", "value": answers.get("operations_name")},
                    {"label": "Operations scope", "value": answers.get("operations_scope")},
                    {"label": "Operating model", "value": answers.get("operating_model")},
                    {"label": "Owner", "value": (owner or {}).get("name") or (owner or {}).get("user_id")},
                    {"label": "Currency", "value": answers.get("operating_currency_code")},
                    {"label": "Country", "value": answers.get("country_code")},
                    {"label": "Locale", "value": answers.get("locale")},
                    {"label": "Timezone", "value": answers.get("timezone")},
                    {"label": "Review cycle", "value": answers.get("review_cycle")},
                    {"label": "Financial year start", "value": answers.get("financial_year_start")},
                ],
            ),
            SetupSummaryBlock(
                block_id="budget_structure",
                title="Budget & Structure",
                body=str(answers.get("allocation_mode") or ""),
                items=[
                    {"label": "Monthly budget (minor)", "value": answers.get("monthly_budget_minor")},
                    {"label": "Allocation mode", "value": answers.get("allocation_mode")},
                    {"label": "Allow overallocation", "value": answers.get("allow_overallocation")},
                    {"label": "Budget categories", "value": answers.get("budget_categories")},
                    {"label": "Budget allocations", "value": answers.get("budget_allocations")},
                    {
                        "label": "Allocated budget (minor)",
                        "value": derived.get("allocated_budget_minor"),
                    },
                    {
                        "label": "Unallocated budget (minor)",
                        "value": derived.get("unallocated_budget_minor"),
                    },
                    {"label": "Allocation %", "value": derived.get("allocation_percent")},
                    {
                        "label": "Vendor dependency",
                        "value": answers.get("vendor_dependency_level"),
                    },
                    {"label": "Approval model", "value": answers.get("approval_model")},
                    {"label": "Issue sensitivity", "value": answers.get("issue_sensitivity")},
                    {"label": "Monitoring level", "value": answers.get("monitoring_level")},
                ],
            ),
            SetupSummaryBlock(
                block_id="people_governance",
                title="People & Governance",
                body=f"{len(members)} members",
                items=[
                    {"label": "Member count", "value": len(members)},
                    {
                        "label": "Operations lead",
                        "value": (ops_leads[0].get("name") if ops_leads else None),
                    },
                    {
                        "label": "Budget controller",
                        "value": (budget_controllers[0].get("name") if budget_controllers else None),
                    },
                    {"label": "Approver count", "value": derived.get("approver_count")},
                    {"label": "Supported roles", "value": answers.get("supported_roles")},
                    {"label": "Approval owner", "value": answers.get("approval_owner_id")},
                    {
                        "label": "Approval threshold (minor)",
                        "value": answers.get("approval_threshold_minor"),
                    },
                    {"label": "Visibility", "value": answers.get("operational_visibility") or answers.get("visibility")},
                    {"label": "Spend approval", "value": answers.get("approval_required_for_spend")},
                    {
                        "label": "Vendor-change approval",
                        "value": answers.get("approval_required_for_vendor_changes"),
                    },
                    {
                        "label": "Budget-change approval",
                        "value": answers.get("approval_required_for_budget_changes"),
                    },
                    {
                        "label": "Issue-closure approval",
                        "value": answers.get("approval_required_for_issue_closure"),
                    },
                    {"label": "Invitation pending", "value": len(pending_invites)},
                    {
                        "label": "Invite on activation",
                        "value": answers.get("invite_on_activation"),
                    },
                ],
            ),
            SetupSummaryBlock(
                block_id="monitoring_alerts",
                title="Monitoring & Alerts",
                body=str(answers.get("monitoring_level") or ""),
                items=[
                    {"label": "Monitoring level", "value": answers.get("monitoring_level")},
                    {"label": "Alert conditions", "value": answers.get("alert_conditions")},
                    {"label": "Alert recipients", "value": answers.get("alert_recipient_ids")},
                    {"label": "Escalation contact", "value": answers.get("escalation_contact_id")},
                    {"label": "Activate monitoring", "value": answers.get("activate_monitoring")},
                    {"label": "Notify members", "value": answers.get("notify_members")},
                    {
                        "label": "Notification preferences",
                        "value": answers.get("notification_preferences"),
                    },
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
                moment_type=BUSINESS_OPERATIONS,
                title=str(
                    answers.get("moment_name") or answers.get("operations_name") or "Operations"
                ),
                status="DRAFT",
            )

        await ensure_business_moment(session, shared, owner_user_id=uid, answers=answers)

        scope = str(answers.get("operations_scope") or "CUSTOM")
        currency = (answers.get("operating_currency_code") or "INR").upper()
        budget_minor = answers.get("monthly_budget_minor")
        vis_raw = str(
            answers.get("operational_visibility") or answers.get("visibility") or "TEAM"
        ).upper()
        visibility_legacy = _VISIBILITY_TO_SETUP.get(vis_raw)
        extras = {
            "operations_name": answers.get("operations_name"),
            "moment_name": answers.get("moment_name"),
            "operations_scope": answers.get("operations_scope"),
            "operating_model": answers.get("operating_model"),
            "review_cycle": answers.get("review_cycle"),
            "monthly_budget_minor": answers.get("monthly_budget_minor"),
            "allow_multi_currency": answers.get("allow_multi_currency"),
            "financial_year_start": answers.get("financial_year_start"),
            "default_currency_code": answers.get("default_currency_code"),
            "visibility": answers.get("operational_visibility") or answers.get("visibility"),
            "notification_preferences": answers.get("notification_preferences") or {},
            "allocation_mode": answers.get("allocation_mode"),
        }

        result = await session.execute(
            select(BusinessMomentSetup).where(BusinessMomentSetup.moment_id == mid)
        )
        row = result.scalar_one_or_none()
        now = _now()
        payload = {
            "purpose": scope[:100] or "operations",
            "custom_purpose": (answers.get("operations_name") or None),
            "team_size": "just_me",
            "budget_enabled": budget_minor is not None,
            "currency": currency,
            "work_style": None,
            "visibility": visibility_legacy,
            "team_owner_user_id": uid,
            "team_name": (answers.get("operations_name") or None),
            "country_code": answers.get("country_code"),
            "locale": answers.get("locale"),
            "timezone": answers.get("timezone"),
            "review_cycle": answers.get("review_cycle"),
            "monthly_budget_minor": int(budget_minor) if budget_minor is not None else None,
            "setup_extras": extras,
            "updated_at": now,
        }
        if row is None:
            session.add(BusinessMomentSetup(moment_id=mid, created_at=now, **payload))
        else:
            for k, v in payload.items():
                setattr(row, k, v)
        await session.flush()

        await upsert_operations_setup(
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
                or answers.get("operations_name")
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

        await upsert_operations_structure(session, moment_id=mid, answers=answers)
        await upsert_operations_governance(session, moment_id=mid, answers=answers)
        await upsert_budget_allocations(session, moment_id=mid, answers=answers)

        approval_enabled = bool(
            answers.get("approval_required_for_spend")
            or answers.get("approval_required_for_vendor_changes")
            or answers.get("approval_required_for_budget_changes")
            or answers.get("approval_required_for_issue_closure")
            or (answers.get("approval_model") and answers.get("approval_model") != "NONE")
        )
        vis = str(
            answers.get("operational_visibility") or answers.get("visibility") or "TEAM"
        ).upper()
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
            "activation_ready": True,
            "activated_by": UUID(user_id),
            "activated_at": now,
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
            role = str(m.get("role") or "MEMBER").upper()
            flags = _member_column_flags(m)
            member_user = None
            if m.get("user_id"):
                try:
                    member_user = UUID(str(m["user_id"]))
                except ValueError:
                    member_user = None

            is_owner = role == "OWNER" and member_user == uid
            status = (
                "active"
                if is_owner or (m.get("invite_status") or "").upper() == "ACCEPTED"
                else "invited"
            )
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
            logger.warning("Business Operations invite delivery failed (non-blocking): %s", exc)
