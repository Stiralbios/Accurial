# code mostly from https://gist.github.com/nkhitrov/a3e31cfcc1b19cba8e1b626276148c49
import inspect
import logging
import sys

from backend.settings import AppSettings
from loguru import logger


class InterceptHandler(logging.Handler):
    """
    Default handler from examples in loguru documentaion.
    See https://loguru.readthedocs.io/en/stable/overview.html#entirely-compatible-with-standard-logging
    """

    def emit(self, record: logging.LogRecord):
        # Get corresponding Loguru level if it exists
        level: str | int
        try:
            level = logger.level(record.levelname).name
        except ValueError:
            level = record.levelno

        # Find caller from where originated the logged message.
        frame, depth = inspect.currentframe(), 0
        while frame and (depth == 0 or frame.f_code.co_filename == logging.__file__):
            frame = frame.f_back
            depth += 1

        logger.opt(depth=depth, exception=record.exc_info).log(level, record.getMessage())


def configure_loggers():
    """
    Replaces logging handlers with a handler for using the custom handler.

    WARNING!
    if you call the init_logging in startup event function,
    then the first logs before the application start will be in the old format
    """
    settings = AppSettings()
    # remove all loguru loggers
    logger.remove()

    # Remove and replace base loggers handlers with loguru ones
    # Remove propagation to not have double logs
    override_loggers_names = (
        name
        for name in logging.root.manager.loggerDict
        if (name.startswith("uvicorn.") or name.startswith("sqlalchemy."))
    )
    intercept_handler = InterceptHandler()
    for logger_name in override_loggers_names:
        logger_to_override = logging.getLogger(logger_name)
        logger_to_override.handlers = []
        logging.getLogger(logger_name).handlers = [intercept_handler]
        logging.getLogger(logger_name).propagate = False

    # set logs output, level and format for all our loggers
    logger.configure(handlers=[{"sink": sys.stderr, "level": settings.LOG_LEVEL, "colorize": True}])
