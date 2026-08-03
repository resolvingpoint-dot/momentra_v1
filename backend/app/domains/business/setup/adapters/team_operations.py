"""Team Operations setup adapter (Run 3)."""
from __future__ import annotations

import logging
from datetime import datetime, timezone
from typing import Any
from uuid import UUID, uuid4

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.domains.business.catalog import TEAM_OPERATIONS
from app.domains.business.models import (
    BusinessMomentGovernance,
    BusinessMomentInvitations,
    BusinessMomentMembers,
    BusinessMomentSetup,
    BusinessMomentStructure,
    BusinessMoments,
)
from app.domains.business.setup.business_moment_sync import ensure_business_moment
from app.domains.business.setup.schemas import SetupPreviewResponse, SetupSummaryBlock
from app.domains.business.setup.team_ops_mappers import (
    TEAM_SIZE_CANONICAL,
    WORK_STYLE_CANONICAL,
    coordination_to_legacy,
    monitoring_to_legacy,
    normalize_team_ops_answers,
    team_size_to_legacy,
    visibility_to_legacy_setup,
)
from app.domains.business.setup.member_roles import to_db_member_role
from app.domains.business.setup.team_ops_permissions import (
    SUPPORTED_ROLES_V1,
    member_permission_flags,
)
from app.domains.moments.models import MomentModel

logger = logging.getLogger(__name__)

_KNOWN_CURRENCY = {
    "USD", "EUR", "GBP", "INR", "JPY", "AUD", "CAD", "CHF", "CNY", "HKD",
    "SGD", "NZD", "SEK", "NOK", "DKK", "ZAR", "AED", "SAR", "KWD", "BHD",
    "OMR", "QAR", "MXN", "BRL", "KRW", "TRY", "PLN", "THB", "MYR", "IDR",
    "PHP", "VND", "PKR", "BDT", "NGN", "EGP", "ILS",
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


class TeamOperationsAdapter:
    moment_type_code = TEAM_OPERATIONS
    template_id = "team_ops"

    def __init__(self, session: AsyncSession | None = None) -> None:
        self.session = session

    def bind(self, session: AsyncSession) -> "TeamOperationsAdapter":
        self.session = session
        return self

    def normalize_answers(
        self,
        answers: dict[str, Any],
        *,
        owner_user_id: str | None = None,
        owner_display_name: str | None = None,
    ) -> dict[str, Any]:
        return normalize_team_ops_answers(
            answers,
            owner_user_id=owner_user_id,
            owner_display_name=owner_display_name,
        )

    def validate_draft(self, answers: dict[str, Any]) -> list[str]:
        warnings: list[str] = []
        if not answers.get("moment_name") and not answers.get("team_name"):
            warnings.append("moment_name or team_name recommended")
        if not answers.get("team_purpose"):
            warnings.append("team_purpose incomplete")
        if not answers.get("operating_currency_code"):
            warnings.append("operating_currency_code incomplete")
        budget = answers.get("monthly_team_budget_minor")
        if budget is not None and int(budget) < 0:
            warnings.append("monthly_team_budget_minor cannot be negative")
        return warnings

    def activation_errors(self, answers: dict[str, Any], *, owner_user_id: str | None = None) -> list[str]:
        errors: list[str] = []
        if not (answers.get("moment_name") or "").strip() and not (answers.get("team_name") or "").strip():
            errors.append("moment_name is required")
        if not (answers.get("team_name") or "").strip():
            errors.append("team_name is required")
        if not (answers.get("team_purpose") or "").strip():
            errors.append("team_purpose is required")

        currency = (answers.get("operating_currency_code") or answers.get("default_currency_code") or "").upper()
        if not currency:
            errors.append("operating_currency_code is required")
        elif currency not in _KNOWN_CURRENCY:
            errors.append(f"invalid operating currency: {currency}")

        tz = answers.get("timezone")
        if tz is not None and str(tz).strip() == "":
            errors.append("timezone invalid")

        team_size = answers.get("team_size")
        if not team_size or team_size not in TEAM_SIZE_CANONICAL:
            errors.append("team_size is required")

        work_style = answers.get("work_style")
        if not work_style or work_style not in WORK_STYLE_CANONICAL:
            errors.append("work_style is required")

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

        threshold = answers.get("approval_threshold_minor")
        if threshold is not None and int(threshold) < 0:
            errors.append("approval_threshold_minor cannot be negative")

        budget = answers.get("monthly_team_budget_minor")
        if budget is not None and int(budget) < 0:
            errors.append("monthly_team_budget_minor cannot be negative")

        ids = _member_ids(answers)
        approval_enabled = bool(
            answers.get("approval_required_for_spend")
            or answers.get("approval_required_for_member_changes")
            or answers.get("approval_owner_id")
        )
        approval_owner = answers.get("approval_owner_id")
        if approval_enabled and approval_owner and str(approval_owner) not in ids:
            errors.append("approval_owner_id must be an included member")
        escalation = answers.get("escalation_contact_id")
        if escalation and str(escalation) not in ids:
            errors.append("escalation_contact_id must be an included member")

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
        owner = next((m for m in members if m.get("role") == "OWNER"), None)
        approvers = [m for m in members if m.get("is_approver") or m.get("role") == "APPROVER"]
        budget_owners = [m for m in members if m.get("is_budget_owner") or m.get("role") == "BUDGET_OWNER"]
        pending_invites = [
            m for m in members
            if m.get("role") != "OWNER" and (m.get("invite_status") or "DRAFT") != "ACCEPTED"
        ]

        blocks = [
            SetupSummaryBlock(
                block_id="team_identity",
                title="Team Identity",
                body=str(answers.get("team_name") or answers.get("moment_name") or ""),
                items=[
                    {"label": "Moment name", "value": answers.get("moment_name")},
                    {"label": "Team name", "value": answers.get("team_name")},
                    {"label": "Purpose", "value": answers.get("team_purpose")},
                    {"label": "Team size", "value": answers.get("team_size")},
                    {"label": "Work style", "value": answers.get("work_style")},
                    {"label": "Owner", "value": (owner or {}).get("name") or (owner or {}).get("user_id")},
                    {"label": "Currency", "value": answers.get("operating_currency_code")},
                    {"label": "Monthly budget (minor)", "value": answers.get("monthly_team_budget_minor")},
                    {"label": "Country", "value": answers.get("country_code")},
                    {"label": "Locale", "value": answers.get("locale")},
                    {"label": "Timezone", "value": answers.get("timezone")},
                ],
            ),
            SetupSummaryBlock(
                block_id="governance",
                title="Governance",
                body=str(answers.get("coordination_style") or ""),
                items=[
                    {"label": "Supported roles", "value": answers.get("supported_roles")},
                    {"label": "Coordination", "value": answers.get("coordination_style")},
                    {"label": "Approval owner", "value": answers.get("approval_owner_id")},
                    {"label": "Approval threshold (minor)", "value": answers.get("approval_threshold_minor")},
                    {"label": "Monitoring", "value": answers.get("monitoring_level")},
                    {"label": "Review cycle", "value": answers.get("review_cycle")},
                    {"label": "Escalation", "value": answers.get("escalation_contact_id")},
                    {"label": "Visibility", "value": answers.get("visibility")},
                    {"label": "Spend approval", "value": answers.get("approval_required_for_spend")},
                    {"label": "Member-change approval", "value": answers.get("approval_required_for_member_changes")},
                ],
            ),
            SetupSummaryBlock(
                block_id="members",
                title="Members & Roles",
                body=f"{len(members)} members",
                items=[
                    {"label": "Member count", "value": len(members)},
                    {"label": "Approver count", "value": len(approvers)},
                    {
                        "label": "Budget owner",
                        "value": (budget_owners[0].get("name") if budget_owners else None),
                    },
                    {"label": "Visibility", "value": answers.get("visibility")},
                    {"label": "Invitation pending", "value": len(pending_invites)},
                    {
                        "label": "Invite on activation",
                        "value": answers.get("invite_on_activation"),
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
                moment_type=TEAM_OPERATIONS,
                title=str(answers.get("moment_name") or answers.get("team_name") or "Team"),
                status="DRAFT",
            )

        await ensure_business_moment(session, shared, owner_user_id=uid, answers=answers)

        purpose = str(answers.get("team_purpose") or "")[:100] or "team"
        custom_purpose = str(answers.get("team_purpose") or "")[:255] if len(str(answers.get("team_purpose") or "")) > 100 else None
        team_size_legacy = team_size_to_legacy(answers.get("team_size")) or "just_me"
        currency = (answers.get("operating_currency_code") or "INR").upper()
        budget_minor = answers.get("monthly_team_budget_minor")
        extras = {
            "work_style": answers.get("work_style"),
            "visibility": answers.get("visibility"),
            "notification_preferences": answers.get("notification_preferences") or {},
            "team_name": answers.get("team_name"),
            "moment_name": answers.get("moment_name"),
            "financial_year_start": answers.get("financial_year_start"),
            "allow_multi_currency": answers.get("allow_multi_currency"),
        }
        # Equivalent legacy visibility only when mapped; else leave null (canonical in extras).
        visibility_legacy = visibility_to_legacy_setup(answers.get("visibility"))

        result = await session.execute(
            select(BusinessMomentSetup).where(BusinessMomentSetup.moment_id == mid)
        )
        row = result.scalar_one_or_none()
        now = _now()
        payload = {
            "purpose": purpose,
            "custom_purpose": custom_purpose,
            "team_size": team_size_legacy,
            "budget_enabled": budget_minor is not None,
            "currency": currency,
            "work_style": None,  # canonical in setup_extras — do not coerce unrelated legacy enums
            "visibility": visibility_legacy,
            "team_owner_user_id": uid,
            "team_name": (answers.get("team_name") or None),
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

        biz = await session.execute(select(BusinessMoments).where(BusinessMoments.moment_id == mid))
        biz_row = biz.scalar_one_or_none()
        if biz_row is not None:
            biz_row.moment_name = str(answers.get("moment_name") or answers.get("team_name") or biz_row.moment_name)[:255]
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
        roles = answers.get("supported_roles") or list(SUPPORTED_ROLES_V1)
        coord = coordination_to_legacy(answers.get("coordination_style")) or "shared_ownership"
        mon = monitoring_to_legacy(answers.get("monitoring_level")) or "standard"
        threshold_minor = answers.get("approval_threshold_minor")
        approval_enabled = bool(
            answers.get("approval_required_for_spend")
            or answers.get("approval_required_for_member_changes")
        )

        # Resolve approval / escalation members to user UUID when possible.
        member_map = {str(m.get("local_id")): m for m in _members(answers)}
        member_map.update({str(m.get("user_id")): m for m in _members(answers) if m.get("user_id")})

        def _as_uuid(raw: Any) -> UUID | None:
            if not raw:
                return None
            try:
                return UUID(str(raw))
            except ValueError:
                m = member_map.get(str(raw))
                if m and m.get("user_id"):
                    try:
                        return UUID(str(m["user_id"]))
                    except ValueError:
                        return None
                return None

        structure_extras = {
            "coordination_style": answers.get("coordination_style"),
            "monitoring_level": answers.get("monitoring_level"),
            "review_cycle": answers.get("review_cycle"),
            "approval_owner_id": answers.get("approval_owner_id"),
            "escalation_contact_id": answers.get("escalation_contact_id"),
            "approval_required_for_spend": answers.get("approval_required_for_spend"),
            "approval_required_for_member_changes": answers.get("approval_required_for_member_changes"),
        }

        result = await session.execute(
            select(BusinessMomentStructure).where(BusinessMomentStructure.moment_id == mid)
        )
        structure = result.scalar_one_or_none()
        s_payload = {
            "roles_supported": {"roles": roles},
            "approver_role": "APPROVER",
            "approval_threshold": 0,
            "approval_threshold_minor": int(threshold_minor) if threshold_minor is not None else None,
            "escalation_contact_role": "OWNER",
            "coordination_style": coord,
            "monitoring_level": mon,
            "custom_approver_user_id": _as_uuid(answers.get("approval_owner_id")),
            "custom_escalation_user_id": _as_uuid(answers.get("escalation_contact_id")),
            "structure_extras": structure_extras,
            "updated_at": now,
        }
        if structure is None:
            session.add(BusinessMomentStructure(moment_id=mid, created_at=now, **s_payload))
        else:
            for k, v in s_payload.items():
                setattr(structure, k, v)

        vis = answers.get("visibility") or "TEAM"
        gov_vis = {"PRIVATE": "private", "TEAM": "leadership", "ORG": "organization"}.get(str(vis).upper(), "leadership")
        prefs = answers.get("notification_preferences") if isinstance(answers.get("notification_preferences"), dict) else {}

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
        by_local = {
            str(r.local_id): r
            for r in (existing.scalars().all() if hasattr(existing, "scalars") else [])
            if getattr(r, "local_id", None)
        }
        # MockSession may return MagicMock — also load via store fallback later
        try:
            rows = list(existing.scalars().all())
        except Exception:
            rows = []
        by_local = {str(r.local_id): r for r in rows if getattr(r, "local_id", None)}
        by_user = {str(r.user_id): r for r in rows if getattr(r, "user_id", None)}

        for m in members:
            local_id = str(m.get("local_id") or uuid4())
            role = str(m.get("role") or "MEMBER").upper()
            db_role = to_db_member_role(role, template_code="team_operations")
            flags = member_permission_flags(
                role,
                is_approver=bool(m.get("is_approver")),
                is_budget_owner=bool(m.get("is_budget_owner")),
            )
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
                "role": db_role,
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

        # Reload members for invitation upsert.
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
            # skip if any active invite for same key already sent
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
            logger.warning("Team Ops invite delivery failed (non-blocking): %s", exc)
