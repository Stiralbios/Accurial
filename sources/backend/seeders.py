import logging

from fastapi_users import exceptions

from backend.database import async_session_maker
from backend.logconfig import APP_LOGGER_NAME
from backend.settings import InitializationSettings
from backend.user.managers import UserManager
from backend.user.models import get_user_db
from backend.user.schemas import UserCreate

logger = logging.getLogger(APP_LOGGER_NAME)


async def create_default_superuser():
    email = InitializationSettings().DEFAULT_EMAIL
    secret_password = InitializationSettings().DEFAULT_PASSWORD

    if not email and not secret_password:
        logger.info("No default superuser credentials provided, skipping creation")
        return
    if not email or not secret_password:
        logger.warning("DEFAULT_EMAIL or DEFAULT_PASSWORD is set but not both")
        return

    async with async_session_maker() as session:
        user_db = await get_user_db(session=session)
        user_manager = UserManager(user_db)

        try:
            user = await user_manager.get_by_email(email)
        except exceptions.UserNotExists:
            pass
        else:
            logger.info("Superuser already exists, skipping creation")
            return

        user = UserCreate(
            email=email,
            password=secret_password.get_secret_value(),
            is_superuser=True,
            is_active=True,
            is_verified=True,
        )
        await user_manager.create(user)
    logger.info(f"Superuser created successfully with email: {email}")
