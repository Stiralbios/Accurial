from backend.database import with_async_session
from backend.exceptions import CustomAlreadyExistError
from backend.user.models import UserDO
from backend.user.schemas import UserCreateInternal, UserFilter, UserInternal
from pydantic import UUID4
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession


class UserStore:
    @staticmethod
    @with_async_session
    async def create(session: AsyncSession, user: UserCreateInternal) -> UserInternal:
        query = select(UserDO).where(UserDO.email == user.email)
        res = await session.execute(query)
        orm_object = res.scalar_one_or_none()
        if orm_object is not None:
            raise CustomAlreadyExistError(f"User email {user.email} is already used")
        orm_object = UserDO(**user.model_dump())
        session.add(orm_object)
        await session.flush()
        await session.refresh(orm_object)
        return UserInternal.model_validate(orm_object)

    @staticmethod
    @with_async_session
    async def retrieve(session: AsyncSession, user_uuid: UUID4) -> UserInternal | None:
        orm_object = await session.get(UserDO, user_uuid)
        return None if orm_object is None else UserInternal.model_validate(orm_object)

    @staticmethod
    @with_async_session
    async def retrieve_by_email(session: AsyncSession, user_email: str) -> UserInternal | None:
        stmt = select(UserDO).where(UserDO.email == user_email)
        result = await session.execute(stmt)
        orm_object = result.scalar_one_or_none()
        return None if orm_object is None else UserInternal.model_validate(orm_object)

    @staticmethod
    @with_async_session
    async def list(session: AsyncSession, user_filter: UserFilter) -> list[UserInternal]:
        query = user_filter.filter(select(UserDO))
        res = await session.execute(query)
        orm_objects = res.scalars().all()
        return [UserInternal.model_validate(orm_object) for orm_object in orm_objects]
