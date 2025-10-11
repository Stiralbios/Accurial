from backend.exceptions import CustomNotFoundError
from backend.user.schemas import UserCreateInternal, UserFilter, UserInternal
from backend.user.stores import UserStore
from backend.utils.security import verify_password
from pydantic import UUID4, SecretStr


class UserService:
    def __init__(self) -> None:
        self.store = UserStore

    async def create(self, user: UserCreateInternal) -> UserInternal:
        return await self.store.create(user)

    async def retrieve(self, user_uuid: UUID4) -> UserInternal:
        user = await self.store.retrieve(user_uuid)
        if user is None or not user.is_active:
            raise CustomNotFoundError(f"User {user_uuid} not found")
        return user

    async def authenticate(self, email: str, password: SecretStr) -> UserInternal:
        user = await self.store.retrieve_by_email(email)
        if user and not verify_password(password, user.hashed_password):
            return None
        return user

    async def list(
        self,
        user_filter: UserFilter,
    ) -> list[UserInternal]:
        return await self.store.list(user_filter)
