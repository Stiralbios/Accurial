import uuid

from backend.database import with_async_session
from backend.question.models import QuestionDO
from backend.question.schemas import QuestionCreateInternal, QuestionFilter, QuestionInternal, QuestionUpdateInternal
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession


class QuestionStore:
    @staticmethod
    @with_async_session
    async def create(session: AsyncSession, question: QuestionCreateInternal) -> QuestionInternal:
        orm_object = QuestionDO(**question.model_dump())
        session.add(orm_object)
        await session.commit()
        return QuestionInternal.model_validate(orm_object)

    @staticmethod
    @with_async_session
    async def retrieve(session: AsyncSession, question_uuid: uuid.UUID) -> QuestionInternal | None:
        orm_object = await session.get(QuestionDO, question_uuid)
        return None if orm_object is None else QuestionInternal.model_validate(orm_object)

    @staticmethod
    @with_async_session
    async def update(session: AsyncSession, question_update: QuestionUpdateInternal) -> QuestionInternal:
        orm_object = await session.get(QuestionDO, question_update.id)
        if not orm_object:
            raise RuntimeError("tmp exception to change")
        for field, value in question_update.model_dump(exclude_unset=True, exclude={"id"}).items():
            setattr(orm_object, field, value)
        await session.commit()
        return QuestionInternal.model_validate(orm_object)

    @staticmethod
    @with_async_session
    async def list(session: AsyncSession, question_filter: QuestionFilter) -> list[QuestionInternal]:
        query = question_filter.filter(select(QuestionDO))
        res = await session.execute(query)
        orm_objects = res.scalars().all()
        return [QuestionInternal.model_validate(orm_object) for orm_object in orm_objects]
