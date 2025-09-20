import logging

from backend.exceptions import CustomAlreadyExistError
from backend.logconfig import LOGGER_NAME
from backend.settings import InitializationSettings
from backend.user.schemas import UserCreateInternal
from backend.user.services import UserService
from backend.utils.passwords import hash_password

logger = logging.getLogger(LOGGER_NAME+__name__)


async def create_default_superuser():
    pass
    email = InitializationSettings().DEFAULT_EMAIL
    secret_password = InitializationSettings().DEFAULT_PASSWORD

    if not email and not secret_password:
        logger.info("No default superuser credentials provided, skipping creation")
        return
    if not email or not secret_password:
        logger.warning("DEFAULT_EMAIL or DEFAULT_PASSWORD is set but not both")
        return

    user = UserCreateInternal(
        email=email,
        hashed_password=hash_password(secret_password.get_secret_value()),
        is_active=True,
        is_superuser=True
     )
    try:
        await UserService().create(user)
    except CustomAlreadyExistError:
        logger.info("Superuser already exists, skipping creation")
        return
    logger.info(f"Superuser created successfully with email: {email}")
