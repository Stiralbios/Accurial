import uuid
from datetime import datetime
from typing import Any, Optional

from backend.resolution.models import ResolutionDO
from fastapi_filter.contrib.sqlalchemy import Filter
from pydantic import BaseModel, ConfigDict, Field, field_validator


class ResolutionBase(BaseModel):
    date: datetime = Field(
        examples=["2024-12-25T12:00:00Z"],
        description="The date when the resolution was determined"
    )
    value: str = Field(
        examples=["true"],
        description="The result value. For binary questions, use 'true' or 'false'",
        max_length=255
    )
    description: str = Field(
        examples=["See link: http://127.0.0.1"],
        description="The description justifiying the resolution result"
    )


class ResolutionRead(ResolutionBase):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    question_id: uuid.UUID


class ResolutionInternal(ResolutionRead):
    pass


class ResolutionCreate(ResolutionBase):
    question_id: uuid.UUID = Field(
        description="The ID of the question being resolved",
        examples=["123e4567-e89b-12d3-a456-426614174000"]
    )
    model_config = ConfigDict(extra="forbid")


class ResolutionCreateInternal(ResolutionCreate):
    pass


class ResolutionUpdate(BaseModel):
    model_config = ConfigDict(extra="forbid")

    date: Optional[datetime] = Field(default=None)
    value: Optional[str] = Field(default=None, max_length=255)
    description: Optional[str] = Field(default=None, max_length=255)

    @classmethod  # noqa
    @field_validator("date", "value", "description", mode="before")
    def prevent_explicit_none(cls, value: Any) -> Any:
        if value is None:
            raise ValueError("Explicit None is not allowed for this field")
        return value


class ResolutionUpdateContext(BaseModel):
    id: uuid.UUID
    user_id: uuid.UUID


class ResolutionUpdateInternal(ResolutionUpdate):
    context: ResolutionUpdateContext


class ResolutionFilter(Filter):
    question_id: Optional[uuid.UUID] = Field(default=None)
    result_value: Optional[str] = Field(default=None)

    class Constants(Filter.Constants):
        model = ResolutionDO


class ResolutionDeleteContext(BaseModel):
    user_id: uuid.UUID


class ResolutionDeleteInternal(BaseModel):
    id: uuid.UUID
    context: ResolutionDeleteContext
