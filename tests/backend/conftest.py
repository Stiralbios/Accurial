import asyncio
import logging
import sys
from contextlib import asynccontextmanager
from unittest.mock import patch

import pytest
from backend.user.auth import current_active_user
from backend.user.models import get_user_db
from backend.user.schemas import UserCreate, UserInternal
from backend.user.services import UserService
from fastapi import FastAPI
from httpx import ASGITransport, AsyncClient
from sqlalchemy import create_engine, text
from sqlalchemy.ext.asyncio import async_sessionmaker, create_async_engine
from sqlalchemy.orm import Session

##########################################################
# CONFIGURE THE PYTHONPATH                               #
##########################################################

# Add the source root to sys.path if it's not already included
# todo do the config in the yaml cause here it's hardcoded and will be working only for the docker
if str("/home/project_base/sources") not in sys.path:
    sys.path.insert(0, "/home/project_base/sources")

# Add the project root to sys.path if it's not already included
# todo do the config in the yaml cause here it's hardcoded and will be working only for the docker
if str("/home/project_base") not in sys.path:
    sys.path.insert(0, "/home/project_base")

##########################################################
# SETUP A TEST DATABASE                                  #
##########################################################
from backend.database import Base  # noqa Import after setting up the python path
from backend.main import app, custom_exception_handler  # noqa Import after setting up the python path

logger = logging.getLogger(__name__)

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
    # Patch the engine and async_session_maker in the backend.database module
    # isolate the engine and session_maker cause we do async tests
    isolated_engine = create_async_engine(TEST_SQLALCHEMY_DATABASE_URL)
    test_async_session_maker = async_sessionmaker(isolated_engine, expire_on_commit=False)
    with (
        patch("backend.database.engine", isolated_engine),
        patch("backend.database.async_session_maker", test_async_session_maker),
    ):
        # create tables
        await create_db_and_tables_if_needed(isolated_engine)  # todo check if this could be done once only
        yield

    # tear down, delete everything in the tables and remove the engine
    async with test_async_session_maker() as session:
        for table in Base.metadata.tables.values():
            await session.execute(text(f'TRUNCATE TABLE "{table.name}" CASCADE'))
            await session.commit()
    await isolated_engine.dispose()


async def create_user():
    isolated_engine = create_async_engine(TEST_SQLALCHEMY_DATABASE_URL)
    async_session_maker = async_sessionmaker(isolated_engine, expire_on_commit=False)
    async with async_session_maker() as session:
        user_db = await get_user_db(session)
        user_service = UserService(user_db)
        user = await user_service.create(UserCreate(
                email="admin@example.com",
                password="qud!zz*$pmf34V!8xrT%",
                is_superuser=True,
            )
        )
        return user


@pytest.fixture(scope="function")
async def client_fixture(mock_engine_and_session):
    # replacing lifespan to not create the tables all the time
    app.router.lifespan_context = lifespan

    test_user = await create_user()
    app.dependency_overrides[current_active_user] = lambda: UserInternal.model_validate(test_user)

    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        yield client

    app.dependency_overrides.pop(current_active_user, None)


@pytest.fixture(scope="session")
def anyio_backend():
    # fixing double test with anyio
    return "asyncio"
