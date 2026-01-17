import uuid

from backend.database import with_async_session
from backend.exceptions import ResolutionNotFoundProblem
from backend.resolution.models import ResolutionDO
from backend.resolution.schemas import (
    ResolutionCreateInternal,
    ResolutionFilter,
    ResolutionInternal,
    ResolutionUpdateInternal,
)
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession


class ResolutionStore:
    @staticmethod
    @with_async_session
    async def create(session: AsyncSession, resolution: ResolutionCreateInternal) -> ResolutionInternal:
        orm_object = ResolutionDO(**resolution.model_dump())
        session.add(orm_object)
        await session.flush()
        await session.refresh(orm_object)
        return ResolutionInternal.model_validate(orm_object)

    @staticmethod
    @with_async_session
    async def retrieve(session: AsyncSession, resolution_uuid: uuid.UUID) -> ResolutionInternal | None:
        orm_object = await session.get(ResolutionDO, resolution_uuid)
        return None if orm_object is None else ResolutionInternal.model_validate(orm_object)

    @staticmethod
    @with_async_session
    async def retrieve_by_question_id(session: AsyncSession, question_id: uuid.UUID) -> ResolutionInternal | None:
        query = select(ResolutionDO).where(ResolutionDO.question_id == question_id)
        result = await session.execute(query)
        orm_object = result.scalar_one_or_none()
        return None if orm_object is None else ResolutionInternal.model_validate(orm_object)

    @staticmethod
    @with_async_session
    async def update(session: AsyncSession, resolution_update: ResolutionUpdateInternal) -> ResolutionInternal:
        orm_object = await session.get(ResolutionDO, resolution_update.context.id)
        if not orm_object:
            raise ResolutionNotFoundProblem(f"Resolution with ID {resolution_update.context.id} does not exist.")
        for field, value in resolution_update.model_dump(exclude_unset=True, exclude={"context"}).items():
            setattr(orm_object, field, value)
        await session.flush()
        await session.refresh(orm_object)
        return ResolutionInternal.model_validate(orm_object)

    @staticmethod
    @with_async_session
    async def list(session: AsyncSession, resolution_filter: ResolutionFilter) -> list[ResolutionInternal]:
        query = resolution_filter.filter(select(ResolutionDO))
        res = await session.execute(query)
        orm_objects = res.scalars().all()
        return [ResolutionInternal.model_validate(orm_object) for orm_object in orm_objects]

    @staticmethod
    @with_async_session
    async def delete(session: AsyncSession, resolution_uuid: uuid.UUID) -> None:
        orm_object = await session.get(ResolutionDO, resolution_uuid)
        if orm_object is None:
            raise ResolutionNotFoundProblem(f"ResolutionDO with ID {resolution_uuid} does not exist.")
        await session.delete(orm_object)
        await session.flush()
