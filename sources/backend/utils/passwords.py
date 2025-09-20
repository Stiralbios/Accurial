
from argon2 import PasswordHasher
from pydantic import SecretStr


def hash_password(password: SecretStr | str) -> str:
    if isinstance(password, SecretStr):
        password = password.get_secret_value()

    ph = PasswordHasher()
    return ph.hash(password)


def verify_password(password: SecretStr | str, hashed_password: str) -> bool:
    if isinstance(password, SecretStr):
        password = password.get_secret_value()

    ph = PasswordHasher()
    return ph.verify(hashed_password, password)