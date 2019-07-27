import typing

from starlette.authentication import SimpleUser

from starlette_auth_toolkit.base import backends

from ..utils import get_base_app

USERNAME = "user"
PASSWORD = "s3kr3t"


class BasicAuth(backends.BaseBasicAuth):
    async def verify(
        self, username: str, password: str
    ) -> typing.Optional[SimpleUser]:
        if (username, password) == (USERNAME, PASSWORD):
            return SimpleUser(username)
        return None


def get_app():
    return get_base_app(backend=BasicAuth())
