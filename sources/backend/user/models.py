from typing import AsyncGenerator

from backend.database import Base, async_session_maker
from fastapi import Depends
from fastapi_users_db_sqlalchemy import (
    SQLAlchemyBaseUserTableUUID,
    SQLAlchemyUserDatabase,
)
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import relationship


async def get_async_session() -> AsyncGenerator[AsyncSession, None]:
    async with async_session_maker() as session:
        yield session


class User(SQLAlchemyBaseUserTableUUID, Base):
    questions = relationship("QuestionDO", back_populates="owner")


async def get_user_db(session: AsyncSession = Depends(get_async_session)):
    return SQLAlchemyUserDatabase(session, User)
