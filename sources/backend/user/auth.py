from uuid import UUID

from backend.user.authentification_backends import jwt_auth_backend
from backend.user.managers import get_user_manager
from backend.user.models import User
from backend.user.schemas import UserInternal
from fastapi import Security
from fastapi_users import FastAPIUsers

fastapi_users = FastAPIUsers[User, UUID](
    get_user_manager,
    [jwt_auth_backend],
)


async def current_active_user(
    user: User = Security(fastapi_users.current_user(active=True)),
) -> UserInternal:
    return UserInternal.model_validate(user)
