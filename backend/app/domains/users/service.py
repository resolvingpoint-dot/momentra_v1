from __future__ import annotations

from sqlalchemy.ext.asyncio import AsyncSession

from app.domains.users.models import UserModel
from app.domains.users.repository import UserRepository


class UserService:
    def __init__(self, session: AsyncSession) -> None:
        self.repo = UserRepository(session)

    async def sync_user(self, firebase_payload: dict) -> UserModel:
        return await self.repo.upsert(
            firebase_uid=firebase_payload["uid"],
            email=firebase_payload.get("email"),
            phone=firebase_payload.get("phone_number"),
            display_name=firebase_payload.get("name"),
            photo_url=firebase_payload.get("picture"),
        )

    async def get_user(self, firebase_uid: str) -> UserModel | None:
        return await self.repo.get_by_firebase_uid(firebase_uid)

    async def get_user_by_id(self, user_id) -> UserModel | None:
        return await self.repo.get_by_id(user_id)

    async def update_profile(
        self,
        user: UserModel,
        display_name: str | None = None,
        photo_url: str | None = None,
    ) -> UserModel:
        return await self.repo.update_profile(
            user, display_name=display_name, photo_url=photo_url
        )
