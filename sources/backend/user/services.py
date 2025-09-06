import uuid
from typing import Optional

from backend.settings import AppSettings
from backend.user.models import User, get_user_db
from backend.user.schemas import UserCreate
from fastapi import Depends, Request
from fastapi_users import BaseUserManager, InvalidPasswordException, UUIDIDMixin


class UserService(UUIDIDMixin, BaseUserManager[User, uuid.UUID]):
    reset_password_token_secret = AppSettings().RESET_PASSWORD_TOKEN_SECRET
    verification_token_secret = AppSettings().VERIFICATION_TOKEN_SECRET

    async def on_after_register(self, user: User, request: Optional[Request] = None):
        """
        only a test
        """
        print(f"User {user.id} has registered.")

    async def on_after_forgot_password(self, user: User, token: str, request: Optional[Request] = None):
        """
        Only a test
        """
        print(f"User {user.id} has forgot their password. Reset token: {token}")

    async def on_after_request_verify(self, user: User, token: str, request: Optional[Request] = None):
        """
        Only a test
        """
        print(f"Verification requested for user {user.id}. Verification token: {token}")

    async def validate_password(
        self,
        password: str,
        user: UserCreate | User,
    ) -> None:
        if len(password) < 12:
            raise InvalidPasswordException(reason="Password should be at least 12 characters")
        if user.email in password:
            raise InvalidPasswordException(reason="Password should not contain e-mail")


async def get_user_service(user_db=Depends(get_user_db)):
    return UserService(user_db)
