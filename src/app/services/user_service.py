from app.core.security import verify_password
from app.models.user import User
from app.repositories.user_repository import UserRepository


class UserService:
    def __init__(self, repository: UserRepository) -> None:
        self.repository = repository

    async def authenticate(self, username: str, password: str) -> User | None:
        user = await self.repository.get_by_username(username)
        if not user or not verify_password(password, user.password_hash):
            return None
        return user

    async def get_by_username(self, username: str) -> User | None:
        return await self.repository.get_by_username(username)
