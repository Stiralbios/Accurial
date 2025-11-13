import asyncio
import traceback
from contextlib import asynccontextmanager

from backend.auth import apis as auth
from backend.database import create_db_and_tables
from backend.debug import apis as healthcheck
from backend.exceptions import BaseProblem
from backend.logconfig import configure_loggers
from backend.prediction import apis as prediction
from backend.question import apis as question
from backend.seeders import create_default_superuser
from backend.settings import AppSettings
from backend.user import apis as user
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from loguru import logger

# init settings config
settings = AppSettings()

# init the log
configure_loggers()


def custom_exception_handler(loop, context):
    """Allow to see exceptions in ascyncio tasks"""
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

# Including routers
app.include_router(healthcheck.router)
app.include_router(user.router)
app.include_router(auth.router)
app.include_router(question.router)
app.include_router(prediction.router)


# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.ALLOWED_CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.exception_handler(BaseProblem)
async def problem_exception_handler(request: Request, exc: BaseProblem):
    return JSONResponse(
        status_code=exc.status,
        content={"type": exc.kind, "on": exc.entity, "title": exc.title, "detail": exc.detail, "status": exc.status},
    )
