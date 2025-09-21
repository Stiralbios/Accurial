import logging
from contextlib import asynccontextmanager
from functools import wraps
from typing import Any, AsyncGenerator, Callable, Coroutine

from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine
from sqlalchemy.orm import DeclarativeBase

from backend.settings import AppSettings

# init settings config
settings = AppSettings()

SQLALCHEMY_DATABASE_URL = (
    f"postgresql+asyncpg://{settings.POSTGRES_USER}:{settings.POSTGRES_PASSWORD.get_secret_value()}@"
    f"{settings.POSTGRES_HOST}:{settings.POSTGRES_PORT}/{settings.POSTGRES_DB}"
)

engine = create_async_engine(SQLALCHEMY_DATABASE_URL)

async_session_maker = async_sessionmaker(engine, expire_on_commit=False)
logger = logging.getLogger(__name__)


class Base(DeclarativeBase):
    pass


async def create_db_and_tables():
    async with engine.begin() as conn:
        try:
            logger.info(f"Tables to create {repr(Base.metadata.tables)}")
            await conn.run_sync(Base.metadata.create_all)
            logger.info("Tables created successfully")
        except Exception as e:
            logger.info(f"Error creating tables: {e}")


@asynccontextmanager
async def get_async_session() -> AsyncGenerator[AsyncSession, None]:
    async with async_session_maker() as session:
        async with session.begin():
            yield session


def with_async_session(func: Callable) -> Callable[..., Coroutine[Any, Any, Any]]:
    @wraps(func)
    async def wrapper(*args, **kwargs) -> Any:
        # Check for existing session in arguments
        session = next((arg for arg in args if isinstance(arg, AsyncSession)), kwargs.get("session"))

        if session and isinstance(session, AsyncSession):
            # Use existing session without transaction management
            return await func(*args, **kwargs)
        # Create new session and manage transaction

        async with get_async_session() as session:
            return await func(session, *args, **kwargs)

    return wrapper
