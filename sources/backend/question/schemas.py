import uuid
from typing import Optional

from backend.question.constants import PredictionType, QuestionStatus
from backend.question.models import QuestionDO
from fastapi_filter.contrib.sqlalchemy import Filter
from pydantic import BaseModel, ConfigDict, Field


class QuestionBase(BaseModel):
    title: str = Field(max_length=255, examples=["My great question"])
    description: str = Field(
        examples=["What will my familly cook for chrismass ?"],
    )
    prediction_type: PredictionType


class QuestionRead(QuestionBase):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    status: QuestionStatus
    owner_id: uuid.UUID


class QuestionInternal(QuestionRead):
    pass


class QuestionCreate(QuestionBase):
    model_config = ConfigDict(extra="forbid")


class QuestionCreateInternal(QuestionCreate):
    status: QuestionStatus = Field(default=QuestionStatus.DRAFT)
    owner_id: uuid.UUID = Field(default=None)


class QuestionUpdate(BaseModel):
    model_config = ConfigDict(extra="forbid")

    title: Optional[str] = Field(default=None)
    description: Optional[str] = Field(default=None)
    prediction_type: Optional[PredictionType] = Field(default=None)
    status: Optional[QuestionStatus] = Field(default=None)


class QuestionUpdateInternal(QuestionUpdate):
    id: uuid.UUID


class QuestionFilter(Filter):
    status: QuestionStatus
    prediction_type: PredictionType

    class Constants(Filter.Constants):
        model = QuestionDO
