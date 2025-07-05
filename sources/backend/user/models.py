from backend.database import Base, get_async_session
from fastapi import Depends
from fastapi_users_db_sqlalchemy import (
    SQLAlchemyBaseUserTableUUID,
    SQLAlchemyUserDatabase,
)
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import relationship


class User(SQLAlchemyBaseUserTableUUID, Base):
    questions = relationship("QuestionDO", back_populates="owner")


async def get_user_db(session: AsyncSession = Depends(get_async_session)):
    return SQLAlchemyUserDatabase(session, User)
