import asyncio
import logging
import traceback
from contextlib import asynccontextmanager
from logging.config import dictConfig

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from backend.auth import apis as auth
from backend.database import create_db_and_tables
from backend.debug import apis as healthcheck
from backend.logconfig import LogConfig
from backend.question import apis as question
from backend.seeders import create_default_superuser
from backend.settings import AppSettings
from backend.user import apis as user

# init settings config
settings = AppSettings()


def custom_exception_handler(loop, context):
    """Allow to see exceptions in ascyncio tassks"""
    logger = logging.getLogger(__name__)
    exception = context.get("exception")
    if exception:
        tb_str = "".join(traceback.format_exception(type(exception), exception, exception.__traceback__))
        logger.error(f"Exception in asyncio task: {tb_str}")
    else:
        logger.error(f"Exception in asyncio task: {context['message']}")


# startup config
@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup: Initialize DB and set exception handler
    await create_db_and_tables()
    await create_default_superuser()
    loop = asyncio.get_running_loop()
    loop.set_exception_handler(custom_exception_handler)

    # Yield control to allow the app to start
    yield


# init fastAPI
app = FastAPI(debug=True, lifespan=lifespan)

# init logger
dictConfig(LogConfig(LOG_LEVEL=settings.LOG_LEVEL).model_dump())

# Including routers
app.include_router(healthcheck.router)
app.include_router(user.router)
app.include_router(auth.router)
app.include_router(question.router)


# frontend port connection
origins = ["http://localhost:5173", "http://localhost:8080", "http://127.0.0.1:8080"]

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
