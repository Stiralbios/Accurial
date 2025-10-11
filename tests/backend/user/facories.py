import factory
from backend.user.models import UserDO
from backend.user.schemas import UserRead
from backend.utils.security import hash_password

from tests.backend.config import CustomSQLAlchemyModelFactory

default_hashed_password = hash_password("testpassword123")


class UserFactory(CustomSQLAlchemyModelFactory):
    _schema_api_response = UserRead

    class Meta:
        model = UserDO

    email = factory.Sequence(lambda n: f"user{n}@test.lan")
    hashed_password = default_hashed_password
    is_superuser = False
    is_active = True
