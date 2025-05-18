import uuid

from backend.user.authentification_backends import jwt_auth_backend
from backend.user.managers import get_user_manager
from backend.user.models import User
from backend.user.schemas import UserCreate, UserRead, UserUpdate
from fastapi import APIRouter
from fastapi_users import FastAPIUsers

fastapi_users = FastAPIUsers[User, uuid.UUID](
    get_user_manager,
    [jwt_auth_backend],
)


router = APIRouter(prefix="/api/user")

router.include_router(fastapi_users.get_auth_router(jwt_auth_backend), prefix="/auth/jwt", tags=["auth"])
router.include_router(
    fastapi_users.get_register_router(UserRead, UserCreate),
    prefix="/auth",
    tags=["auth"],
)
router.include_router(
    fastapi_users.get_reset_password_router(),
    prefix="/auth",
    tags=["auth"],
)
router.include_router(
    fastapi_users.get_verify_router(UserRead),
    prefix="/auth",
    tags=["auth"],
)
router.include_router(
    fastapi_users.get_users_router(UserRead, UserUpdate),
    prefix="/users",
    tags=["users"],
)
