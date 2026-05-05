from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.user import User


class UserRepository:
    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    async def get_by_username(self, username: str) -> User | None:
        result = await self.session.execute(select(User).where(User.username == username))
        return result.scalar_one_or_none()

    async def create(self, username: str, password_hash: str) -> User:
        user = User(username=username, password_hash=password_hash)
        self.session.add(user)
        await self.session.commit()
        await self.session.refresh(user)
        return user

    async def update_password(self, user: User, password_hash: str) -> User:
        user.password_hash = password_hash
        await self.session.commit()
        await self.session.refresh(user)
        return user

    async def exists_any(self) -> bool:
        result = await self.session.execute(select(User.id).limit(1))
        return result.scalar_one_or_none() is not None
