from __future__ import annotations

from datetime import datetime, timezone

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.domains.users.models import UserModel


class UserRepository:
    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    async def get_by_firebase_uid(self, firebase_uid: str) -> UserModel | None:
        stmt = select(UserModel).where(UserModel.firebase_uid == firebase_uid)
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none()

    async def get_by_id(self, user_id) -> UserModel | None:
        stmt = select(UserModel).where(UserModel.id == user_id)
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none()

    async def upsert(
        self,
        firebase_uid: str,
        email: str | None = None,
        phone: str | None = None,
        display_name: str | None = None,
        photo_url: str | None = None,
    ) -> UserModel:
        now = datetime.now(timezone.utc)
        user = await self.get_by_firebase_uid(firebase_uid)

        if user is None:
            user = UserModel(
                firebase_uid=firebase_uid,
                email=email,
                phone=phone,
                display_name=display_name,
                photo_url=photo_url,
                created_at=now,
                updated_at=now,
                last_login_at=now,
            )
            self.session.add(user)
            await self.session.flush()
        else:
            if email is not None:
                user.email = email
            if phone is not None:
                user.phone = phone
            if display_name is not None:
                user.display_name = display_name
            if photo_url is not None:
                user.photo_url = photo_url
            user.updated_at = now
            user.last_login_at = now

        return user

    async def update_profile(
        self,
        user: UserModel,
        display_name: str | None = None,
        photo_url: str | None = None,
    ) -> UserModel:
        if display_name is not None:
            user.display_name = display_name
        if photo_url is not None:
            user.photo_url = photo_url
        user.updated_at = datetime.now(timezone.utc)
        return user
