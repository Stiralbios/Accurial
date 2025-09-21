from pydantic import BaseModel

LOGGER_NAME = "accurial."


class LogConfig(BaseModel):
    LOGGER_NAME: str = "accurial"
    UVICORN_LOG_FORMAT: str = "%(levelprefix)s | %(asctime)s | %(name)s.%(module)s:%(lineno)d | %(message)s"
    APP_LOG_FORMAT: str = "%(levelprefix)s | %(asctime)s | %(name)s:%(lineno)d | Accurial - %(message)s"
    LOG_LEVEL: str = "DEBUG"

    # Logging config
    version: int = 1
    disable_existing_logger: bool = False
    formatters: dict = {
        "default": {
            "()": "uvicorn.logging.DefaultFormatter",
            "fmt": APP_LOG_FORMAT,
            "datefmt": "%Y-%m-%d %H:%M:%S",
        },
        "uvicorn_default": {
            "()": "uvicorn.logging.DefaultFormatter",
            "fmt": UVICORN_LOG_FORMAT,
            "datefmt": "%Y-%m-%d %H:%M:%S",
        },
        "uvicorn_access": {
            "()": "uvicorn.logging.AccessFormatter",
            "fmt": UVICORN_LOG_FORMAT,
            "datefmt": "%Y-%m-%d %H:%M:%S",
        },
    }
    handlers: dict = {
        "default": {
            "formatter": "default",
            "class": "logging.StreamHandler",
            "stream": "ext://sys.stderr",
        },
        "uvicorn_default": {
            "formatter": "uvicorn_default",
            "class": "logging.StreamHandler",
            "stream": "ext://sys.stdout",
        },
        "uvicorn_access": {
            "formatter": "uvicorn_access",
            "class": "logging.StreamHandler",
            "stream": "ext://sys.stdout",
        },
    }
    loggers: dict = {
        "backend": {"handlers": ["default"], "level": LOG_LEVEL, "propagate": False},
        "uvicorn": {"handlers": ["uvicorn_default"], "level": "INFO"},
        "uvicorn.error": {"level": "INFO", "handlers": ["uvicorn_default"], "propagate": True},
        "uvicorn.access": {"handlers": ["uvicorn_access"], "level": "INFO", "propagate": True},
        # "sqlalchemy.engine": {"level": "INFO", "propagate": False},
    }
