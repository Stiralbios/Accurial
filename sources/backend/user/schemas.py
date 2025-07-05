import uuid

from fastapi_users import schemas


class UserInternal(schemas.BaseUser[uuid.UUID]):
    pass


class UserRead(schemas.BaseUser[uuid.UUID]):
    pass


class UserCreate(schemas.BaseUserCreate):
    pass


class UserUpdate(schemas.BaseUserUpdate):
    pass
