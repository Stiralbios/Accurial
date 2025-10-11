import uuid
from typing import Any, Optional

from backend.question.constants import PredictionType, QuestionStatus
from backend.question.models import QuestionDO
from fastapi_filter.contrib.sqlalchemy import Filter
from pydantic import BaseModel, ConfigDict, Field, field_validator


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

    # @model_validator(mode="before")
    # @classmethod
    # def transform(cls, data: Any) -> dict | Any:
    #     if isinstance(data, QuestionCreate):
    #         return {**data.model_dump(exclude={"password_plain_text"}, exclude_unset=True)}
    #     return data


class QuestionUpdate(BaseModel):
    model_config = ConfigDict(extra="forbid")

    title: Optional[str] = Field(default=None)
    description: Optional[str] = Field(default=None)
    prediction_type: Optional[PredictionType] = Field(default=None)
    status: Optional[QuestionStatus] = Field(default=None)

    @classmethod  # noqa
    @field_validator("title", "description", "prediction_type", "status", mode="before")
    def prevent_explicit_none(cls, value: Any) -> Any:
        if value is None:
            raise ValueError("Explicit None is not allowed for this field")
        return value


class QuestionUpdateContext(BaseModel):
    id: uuid.UUID
    user_id: uuid.UUID


class QuestionUpdateInternal(QuestionUpdate):
    context: QuestionUpdateContext


class QuestionFilter(Filter):
    status: Optional[QuestionStatus] = Field(default=None)
    prediction_type: Optional[PredictionType] = Field(default=None)

    class Constants(Filter.Constants):
        model = QuestionDO


class QuestionDeleteContext(BaseModel):
    user_id: uuid.UUID


class QuestionDeleteInternal(BaseModel):
    id: uuid.UUID
    context: QuestionDeleteContext
