from uuid import UUID

from backend.user.authentification_backends import jwt_auth_backend
from backend.user.managers import get_user_manager
from backend.user.models import User
from fastapi_users import FastAPIUsers

fastapi_users = FastAPIUsers[User, UUID](
    get_user_manager,
    [jwt_auth_backend],
)

current_active_user = fastapi_users.current_user(active=True)
