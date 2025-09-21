import uuid
from typing import Optional

from fastapi_filter.contrib.sqlalchemy import Filter
from pydantic import BaseModel, ConfigDict, EmailStr, Field, SecretStr


class UserBase(BaseModel):
    email: EmailStr = Field(examples=["user@test.lan"])


class UserRead(UserBase):
    id: uuid.UUID
    is_active: bool


class UserInternal(UserRead):
    model_config = ConfigDict(from_attributes=True)

    hashed_password: str


class UserCreate(UserBase):
    model_config = ConfigDict(extra="forbid")

    password: SecretStr = Field(examples=["mygreatpassword"])


class UserCreateInternal(UserBase):
    model_config = ConfigDict(extra="forbid")

    is_active: bool = True
    is_superuser: bool = False
    hashed_password: str


class UserFilter(Filter):
    is_active: Optional[bool] = Field(default=None)
    email: Optional[EmailStr] = Field(default=None)
