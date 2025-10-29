import uuid
from datetime import datetime, timezone
from typing import Any, Optional

from backend.prediction.constants import PredictionStatus, PredictionType
from backend.prediction.models import PredictionDO
from fastapi_filter.contrib.sqlalchemy import Filter
from pydantic import BaseModel, ConfigDict, Field, field_validator


class PredictionValueBinary(BaseModel):
    binary: bool


class PredictionBase(BaseModel):
    title: str = Field(max_length=255, examples=["My great prediction"])
    description: str = Field(
        examples=["Turkey"],
    )
    type: PredictionType
    value: PredictionValueBinary
    question_id: uuid.UUID


class PredictionRead(PredictionBase):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    status: PredictionStatus
    created_at: datetime
    owner_id: uuid.UUID


class PredictionInternal(PredictionRead):
    pass


class PredictionCreate(PredictionBase):
    model_config = ConfigDict(extra="forbid")


class PredictionCreateInternal(PredictionCreate):
    status: PredictionStatus = Field(default=PredictionStatus.DRAFT)
    owner_id: uuid.UUID = Field(default=None)
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))


class PredictionUpdate(BaseModel):
    model_config = ConfigDict(extra="forbid")

    title: Optional[str] = Field(default=None)
    description: Optional[str] = Field(default=None)
    status: Optional[PredictionStatus] = Field(default=None)
    value: Optional[PredictionValueBinary] = Field(default=None)

    @classmethod  # noqa
    @field_validator("title", "description", "status", "value", mode="before")
    def prevent_explicit_none(cls, value: Any) -> Any:
        if value is None:
            raise ValueError("Explicit None is not allowed for this field")
        return value


class PredictionUpdateContext(BaseModel):
    id: uuid.UUID
    user_id: uuid.UUID


class PredictionUpdateInternal(PredictionUpdate):
    context: PredictionUpdateContext


class PredictionFilter(Filter):
    status: Optional[PredictionStatus] = Field(default=None)
    type: Optional[PredictionType] = Field(default=None)

    class Constants(Filter.Constants):
        model = PredictionDO
