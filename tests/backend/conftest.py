import asyncio
import logging
from contextlib import asynccontextmanager
from unittest.mock import patch

import pytest
from backend.auth.dependencies import get_current_active_user
from backend.database import Base
from backend.main import app, custom_exception_handler
from backend.user.models import UserDO
from backend.user.schemas import UserCreateInternal
from backend.user.services import UserService
from backend.utils.security import hash_password
from fastapi import FastAPI
from httpx import ASGITransport, AsyncClient
from sqlalchemy import create_engine, select, text
from sqlalchemy.ext.asyncio import async_sessionmaker, create_async_engine
from sqlalchemy.orm import Session

logger = logging.getLogger(__name__)


##########################################################
# SETUP A TEST DATABASE                                  #
##########################################################

TEST_SQLALCHEMY_DATABASE_URL = "postgresql+asyncpg://dev:dev@localhost:5434/dev"
factory_session = Session(create_engine("postgresql://dev:dev@localhost:5434/dev"))
table_created = False


async def create_db_and_tables_if_needed(engine):
    async with engine.begin() as conn:
        global table_created
        if not table_created:
            try:
                await conn.run_sync(Base.metadata.create_all)
                table_created = True
            except Exception as e:
                logger.info(f"Error creating tables: {e}")


@asynccontextmanager
async def lifespan(app: FastAPI):
    loop = asyncio.get_running_loop()
    loop.set_exception_handler(custom_exception_handler)
    yield


##########################################################
# FIXTURES                                               #
##########################################################


@pytest.fixture(scope="function")
async def mock_engine_and_session():
    # todo check for Sessions in factories cause it's only one session on one engine and it could cause weird behavior
    # isolate the engine and session_maker cause we do async tests
    isolated_engine = create_async_engine(TEST_SQLALCHEMY_DATABASE_URL, echo=True)
    test_async_session_maker = async_sessionmaker(isolated_engine, expire_on_commit=False)
    # Close factory session to not hang on truncate
    factory_session.close()
    # Drop all tables to start with a clean state
    try:
        async with asyncio.timeout(10):
            async with test_async_session_maker() as session:
                for table in Base.metadata.tables.values():
                    await session.execute(text(f'TRUNCATE TABLE "{table.name}" CASCADE'))
                    await session.commit()
    except asyncio.TimeoutError:
        raise RuntimeError("⚠️  TRUNCATE timed out - database may be locked")
    # Patch the engine and async_session_maker in the backend.database module
    with (
        patch("backend.database.engine", isolated_engine),
        patch("backend.database.async_session_maker", test_async_session_maker),
    ):
        # create tables
        await create_db_and_tables_if_needed(isolated_engine)  # todo check if this could be done once only
        yield

    # remove the engine
    await isolated_engine.dispose()


hashed_password = hash_password("password")


@pytest.fixture(scope="function")
async def client_fixture(mock_engine_and_session, request):
    # replacing lifespan to not create the tables all the time
    app.router.lifespan_context = lifespan

    auth_override = getattr(request, "param", True)

    if auth_override:
        user = await UserService().create(
            UserCreateInternal(
                email="admin@test.lan", hashed_password=hashed_password, is_active=True, is_superuser=True
            )
        )

        app.dependency_overrides[get_current_active_user] = lambda: user

    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        yield client

    app.dependency_overrides.pop(get_current_active_user, None)


async def get_auth_userdo():
    # dirty by who cares
    isolated_engine = create_async_engine(TEST_SQLALCHEMY_DATABASE_URL, echo=True)
    test_async_session_maker = async_sessionmaker(isolated_engine, expire_on_commit=False)
    async with test_async_session_maker() as session:
        stmt = select(UserDO).where(UserDO.email == "admin@test.lan")
        result = await session.execute(stmt)
        orm_object = result.scalar_one_or_none()
        return orm_object


@pytest.fixture(scope="session")
def anyio_backend():
    # fixing double test with anyio
    return "asyncio"
