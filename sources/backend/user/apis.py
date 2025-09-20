from typing import Annotated

from backend.auth.dependencies import get_current_active_user
from backend.exceptions import CustomAlreadyExistError, CustomNotFoundError
from backend.user.schemas import UserCreate, UserCreateInternal, UserFilter, UserInternal, UserRead
from backend.user.services import UserService
from backend.utils.passwords import hash_password
from fastapi import APIRouter, Depends, HTTPException
from fastapi_filter import FilterDepends
from pydantic import UUID4
from starlette import status

router = APIRouter(prefix="/api/user", tags=["user"])


@router.post("", response_model=UserRead)
async def create_user(user: UserCreate) -> UserInternal:
    hashed_password = hash_password(user.password)
    user_internal = UserCreateInternal.model_validate(
        {"hashed_password": hashed_password, **user.model_dump(exclude={"password"}, exclude_unset=True)}
    )
    try:
        return await UserService().create(user_internal)
    except CustomAlreadyExistError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=e.message) from e


@router.get(path="/me", response_model=UserRead)
async def retrieve_user_me(
    current_user: Annotated[UserInternal, Depends(get_current_active_user)],
):
    return current_user


@router.get(path="/{user_id}", response_model=UserRead)
async def retrieve_user(user_id: UUID4) -> UserInternal:
    try:
        return await UserService().retrieve(user_id)
    except CustomNotFoundError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=e.message) from e


@router.get(path="/", response_model=list[UserRead])
async def list_user(user_filter: UserFilter = FilterDepends(UserFilter)) -> list[UserInternal]:
    # todo manage pagination one day
    return await UserService().list(user_filter)
