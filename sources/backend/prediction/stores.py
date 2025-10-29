import re
import uuid

import sqlalchemy
from backend.database import with_async_session
from backend.exceptions import PredictionNotFoundProblem, QuestionNotFoundProblem
from backend.prediction.models import PredictionDO
from backend.prediction.schemas import (
    PredictionCreateInternal,
    PredictionFilter,
    PredictionInternal,
    PredictionUpdateInternal,
)
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession


class PredictionStore:
    @staticmethod
    @with_async_session
    async def create(session: AsyncSession, prediction: PredictionCreateInternal) -> PredictionInternal:
        try:
            orm_object = PredictionDO(**prediction.model_dump())
            session.add(orm_object)
            await session.flush()
            await session.refresh(orm_object)
            return PredictionInternal.model_validate(orm_object)
        except sqlalchemy.exc.IntegrityError as e:
            # TODO make is generic
            error_str = str(e.orig)
            key_match = re.search(r'Key \((.+?)\)=\((.+?)\)', error_str)
            if key_match:
                # name = key_match.group(1)
                value = key_match.group(2)
                raise QuestionNotFoundProblem(f"Question {value} not found")

    @staticmethod
    @with_async_session
    async def retrieve(session: AsyncSession, prediction_uuid: uuid.UUID) -> PredictionInternal | None:
        orm_object = await session.get(PredictionDO, prediction_uuid)
        return None if orm_object is None else PredictionInternal.model_validate(orm_object)

    @staticmethod
    @with_async_session
    async def list(session: AsyncSession, prediction_filter: PredictionFilter) -> list[PredictionInternal]:
        query = prediction_filter.filter(select(PredictionDO))
        res = await session.execute(query)
        orm_objects = res.scalars().all()
        return [PredictionInternal.model_validate(orm_object) for orm_object in orm_objects]

    @staticmethod
    @with_async_session
    async def update(session: AsyncSession, prediction_update: PredictionUpdateInternal) -> PredictionInternal:
        orm_object = await session.get(PredictionDO, prediction_update.context.id)
        if not orm_object:
            raise PredictionNotFoundProblem(f"PredictionDO with ID {prediction_update.context.id} does not exist.")
        for field, value in prediction_update.model_dump(exclude_unset=True, exclude={"context"}).items():
            setattr(orm_object, field, value)
        await session.flush()
        await session.refresh(orm_object)
        return PredictionInternal.model_validate(orm_object)
