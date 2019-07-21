from starlette_auth_toolkit.passwords import PBKDF2Hasher
from starlette_auth_toolkit.contrib.orm import ModelAuthenticate


def get_user_model():
    from .models import User

    return User


hasher = PBKDF2Hasher()
authenticate = ModelAuthenticate(get_user_model, hasher=hasher)
