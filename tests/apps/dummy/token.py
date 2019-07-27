from starlette.authentication import SimpleUser

from starlette_auth_toolkit.base.backends import BaseTokenAuth

from ..utils import get_base_app

TOKEN = "s3kr3t_t0k3n"


class TokenAuth(BaseTokenAuth):
    async def verify(self, token: str):
        if token != TOKEN:
            return None
        return SimpleUser("bob")


def get_app():
    return get_base_app(backend=TokenAuth())
