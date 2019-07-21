from starlette.authentication import SimpleUser

from starlette_auth_toolkit.base.backends import BearerAuthBackend

from ..utils import make_get_app

TOKEN = "s3kr3t_t0k3n"


class BearerAuth(BearerAuthBackend):
    async def verify(self, token: str):
        if token != TOKEN:
            return None
        return SimpleUser("bob")


def get_app():
    return make_get_app(backend=BearerAuth())
