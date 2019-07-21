from starlette_auth_toolkit.contrib.orm import ModelAuthenticate
from starlette_auth_toolkit.cryptography import PBKDF2Hasher


def get_user_model():
    from .models import User

    return User


hasher = PBKDF2Hasher()
authenticate = ModelAuthenticate(get_user_model, hasher=hasher)
