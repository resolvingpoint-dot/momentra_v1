"""Business Members module: members + invitations."""
from __future__ import annotations

from typing import Any, Mapping
from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.errors import NotFoundError, PermissionDeniedError, StateTransitionError
from app.core.service import Page
from app.domains.business import schemas as bs
from app.domains.business.permissions import is_privileged_member
from app.domains.business.repository import BusinessMomentInvitationsRepository
from app.domains.business.services.base import BusinessModuleService, now_utc
from app.domains.users.models import UserModel

_PRIVILEGE_KEYS = frozenset(
    {
        "role",
        "member_status",
        "is_team_lead",
        "is_budget_owner",
        "can_edit_team_entries",
        "can_add_runway_transactions",
        "can_approve_operations_requests",
        "can_approve_runway_changes",
        "can_edit_financial_entries",
        "can_manage_runway_settings",
        "can_manage_operations_settings",
        "can_delete_operations_records",
        "can_edit_operations_records",
        "can_edit_expense_entries",
        "permission_profile",
    }
)


class BusinessMembersModule(BusinessModuleService):
    def __init__(self, session: AsyncSession) -> None:
        super().__init__(session)
        self.invitations_repo = BusinessMomentInvitationsRepository(session)

    async def _load_user(self, user_id: UUID) -> UserModel:
        result = await self.session.execute(select(UserModel).where(UserModel.id == user_id))
        user = result.scalar_one_or_none()
        if user is None:
            raise NotFoundError("User not found")
        return user

    async def _require_privileged_member(self, user_id: UUID, moment_id: UUID):
        member = await self._require_member(user_id, moment_id)
        if not is_privileged_member(member):
            raise PermissionDeniedError("Only leads or owners can manage member privileges")
        return member

    def _assert_invitee_may_accept(self, user: UserModel, invite, member) -> None:
        """Bind path-based accept to the intended invitee (email/phone/username/user_id)."""
        method = (invite.invite_method or "").lower()
        target = (invite.invite_target or "").strip()
        target_l = target.lower()

        if member is not None and member.user_id is not None and member.user_id != user.id:
            raise PermissionDeniedError("This invitation belongs to another user")

        if method == "qr":
            raise PermissionDeniedError(
                "QR invitations must be accepted via the invite link"
            )

        if method == "email":
            email = (user.email or "").strip().lower()
            if not email or email != target_l:
                raise PermissionDeniedError("Signed-in email does not match this invitation")
            return

        if method == "mobile":
            phone = "".join(ch for ch in (user.phone or "") if ch.isdigit())
            target_digits = "".join(ch for ch in target if ch.isdigit())
            if not phone or not target_digits or phone != target_digits:
                raise PermissionDeniedError("Signed-in phone does not match this invitation")
            return

        if method == "username":
            username = ((member.username if member is not None else None) or "").strip().lower()
            display = (user.display_name or "").strip().lower()
            if not target_l or target_l not in {username, display}:
                raise PermissionDeniedError("Signed-in identity does not match this invitation")
            return

        # Unknown method: require explicit member.user_id pre-binding or email match.
        if member is not None and member.user_id == user.id:
            return
        email = (user.email or "").strip().lower()
        if email and email == target_l:
            return
        raise PermissionDeniedError("You are not the intended recipient of this invitation")

    # --------------------------- members ---------------------------- #
    async def list_members(self, user_id: UUID, moment_id: UUID, *, page: int = 1, per_page: int = 50) -> Page:
        await self._access(user_id, moment_id)
        return await self._page(
            self.members_repo, bs.BusinessMomentMembersSchema,
            filters={"moment_id": moment_id}, order_by="created_at", page=page, per_page=per_page,
        )

    async def add_member(self, user_id: UUID, moment_id: UUID, data: Mapping[str, Any]) -> bs.BusinessMomentMembersSchema:
        actor = await self._require_member(user_id, moment_id)
        payload = dict(data)
        if not is_privileged_member(actor):
            # Non-leads may add placeholders but cannot grant elevated capabilities.
            for key in _PRIVILEGE_KEYS - {"role", "member_status"}:
                payload.pop(key, None)
            payload["is_team_lead"] = False
            payload["is_budget_owner"] = False
            role = str(payload.get("role") or "Team Member")
            if role.strip().lower() not in {"team member", "observer", "viewer", "contributor"}:
                payload["role"] = "Team Member"
        schema = await self._created(
            self.members_repo, bs.BusinessMomentMembersSchema,
            {**payload, "moment_id": moment_id, "added_by": user_id},
        )
        await self.session.commit()
        return schema

    async def _member_in_moment(self, moment_id: UUID, member_id: UUID):
        member = await self.members_repo.get_by_id(member_id)
        if member is None or member.moment_id != moment_id:
            raise NotFoundError("Member not found in this moment")
        return member

    async def update_member(
        self, user_id: UUID, moment_id: UUID, member_id: UUID, data: Mapping[str, Any]
    ) -> bs.BusinessMomentMembersSchema:
        actor = await self._require_member(user_id, moment_id)
        member = await self._member_in_moment(moment_id, member_id)
        payload = dict(data)
        elevating = any(k in _PRIVILEGE_KEYS for k in payload)
        if elevating and not is_privileged_member(actor):
            raise PermissionDeniedError("Only leads or owners can change member privileges")
        for key, value in payload.items():
            setattr(member, key, value)
        member.updated_at = now_utc()
        await self.session.flush()
        schema = bs.BusinessMomentMembersSchema.model_validate(member)
        await self.session.commit()
        return schema

    async def remove_member(self, user_id: UUID, moment_id: UUID, member_id: UUID) -> bs.BusinessMomentMembersSchema:
        await self._require_privileged_member(user_id, moment_id)
        member = await self._member_in_moment(moment_id, member_id)
        member.member_status = "removed"
        member.updated_at = now_utc()
        await self.session.flush()
        schema = bs.BusinessMomentMembersSchema.model_validate(member)
        await self.session.commit()
        return schema

    # --------------------------- invitations ------------------------ #
    async def list_invitations(self, user_id: UUID, moment_id: UUID, *, page: int = 1, per_page: int = 50) -> Page:
        await self._access(user_id, moment_id)
        return await self._page(
            self.invitations_repo, bs.BusinessMomentInvitationsSchema,
            filters={"moment_id": moment_id}, order_by="-created_at", page=page, per_page=per_page,
        )

    async def create_invitation(
        self,
        user_id: UUID,
        moment_id: UUID,
        *,
        invite_method: str,
        invite_target: str,
        member_id: UUID | None = None,
        send_on_activation: bool = True,
    ) -> bs.BusinessMomentInvitationsSchema:
        await self._require_member(user_id, moment_id)
        if member_id is not None:
            await self._member_in_moment(moment_id, member_id)
        schema = await self._created(
            self.invitations_repo, bs.BusinessMomentInvitationsSchema,
            {
                "moment_id": moment_id,
                "invite_method": invite_method,
                "invite_target": invite_target,
                "invite_status": "pending",
                "member_id": member_id,
                "send_on_activation": send_on_activation,
            },
        )
        await self.session.commit()
        return schema

    async def _invitation_in_moment(self, moment_id: UUID, invite_id: UUID):
        invite = await self.invitations_repo.get_by_id(invite_id)
        if invite is None or invite.moment_id != moment_id:
            raise NotFoundError("Invitation not found in this moment")
        return invite

    async def accept_invitation(self, user_id: UUID, moment_id: UUID, invite_id: UUID) -> bs.BusinessMomentInvitationsSchema:
        invite = await self._invitation_in_moment(moment_id, invite_id)
        if invite.invite_status not in {"pending", "sent"}:
            raise StateTransitionError("Only pending or sent invitations can be accepted")
        user = await self._load_user(user_id)
        member = None
        if invite.member_id is not None:
            member = await self.members_repo.get_by_id(invite.member_id)
        self._assert_invitee_may_accept(user, invite, member)
        invite.invite_status = "accepted"
        invite.accepted_at = now_utc()
        invite.updated_at = now_utc()
        if member is not None:
            member.member_status = "active"
            member.user_id = user_id
            member.updated_at = now_utc()
            if user.email and not member.email:
                member.email = user.email
        await self.session.flush()
        schema = bs.BusinessMomentInvitationsSchema.model_validate(invite)
        await self.session.commit()
        return schema

    async def cancel_invitation(self, user_id: UUID, moment_id: UUID, invite_id: UUID) -> bs.BusinessMomentInvitationsSchema:
        await self._require_member(user_id, moment_id)
        invite = await self._invitation_in_moment(moment_id, invite_id)
        if invite.invite_status in {"accepted", "cancelled"}:
            raise StateTransitionError(f"Cannot cancel an invitation in state {invite.invite_status}")
        invite.invite_status = "cancelled"
        invite.updated_at = now_utc()
        await self.session.flush()
        schema = bs.BusinessMomentInvitationsSchema.model_validate(invite)
        await self.session.commit()
        return schema
