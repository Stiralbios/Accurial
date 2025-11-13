from contextlib import asynccontextmanager
from functools import wraps
from typing import Any, AsyncGenerator, Callable, Coroutine

from backend.settings import AppSettings
from loguru import logger
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine
from sqlalchemy.orm import DeclarativeBase

_engine_instance = None
_async_sessionmaker = None


class Base(DeclarativeBase):
    pass


def get_engine():
    global _engine_instance
    if _engine_instance is None:
        settings = AppSettings()
        sql_alchemy_database_url = (
            f"postgresql+psycopg_async://{settings.POSTGRES_USER}:{settings.POSTGRES_PASSWORD.get_secret_value()}@"
            f"{settings.POSTGRES_HOST}:{settings.POSTGRES_PORT}/{settings.POSTGRES_DB}"
        )
        _engine_instance = create_async_engine(
            sql_alchemy_database_url,
            # a little bit more sensible default
            pool_size=10,  # Default connections kept open
            max_overflow=10,  # Additional connections allowed during spikes
            pool_timeout=30,  # Max seconds to wait for connection
            # Recycle connections after 30 minutes /!\  because on postgres side it's recycled after 1h
            pool_recycle=1800,
        )
    return _engine_instance


def get_async_sessionmaker():
    global _async_sessionmaker
    if _async_sessionmaker is None:
        _async_sessionmaker = async_sessionmaker(get_engine(), expire_on_commit=False)
    return _async_sessionmaker


async def create_db_and_tables():
    engine = get_engine()
    async with engine.begin() as conn:
        try:
            logger.info(f"Tables to create {repr(Base.metadata.tables)}")
            await conn.run_sync(Base.metadata.create_all)
            logger.info("Tables created successfully")
        except Exception as e:
            logger.info(f"Error creating tables: {e}")


@asynccontextmanager
async def get_async_session() -> AsyncGenerator[AsyncSession, None]:
    async_sessionmaker = get_async_sessionmaker()
    async with async_sessionmaker() as session:
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
