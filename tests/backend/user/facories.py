# # tests/factories/user_factory.py
# import factory
import factory
from backend.user.models import UserDO
from backend.user.schemas import UserRead
from backend.utils.passwords import hash_password

from tests.backend.config import CustomSQLAlchemyModelFactory

default_hashed_password = hash_password("testpassword123")


class UserFactory(CustomSQLAlchemyModelFactory):
    """Factory for UserCreate schema using your UserService"""

    _schema_api_response = UserRead

    class Meta:
        model = UserDO

    email = factory.Sequence(lambda n: "user{}@test.lan".format(n))
    hashed_password = default_hashed_password
    is_superuser = False
    is_active = True
