import typing

from starlette import authentication as auth
from starlette.requests import HTTPConnection

from .base.backends import AuthBackend
from .datatypes import AuthResult


class MultiAuth(AuthBackend):
    def __init__(self, backends: typing.List[AuthBackend]):
        self.backends = backends

    async def authenticate(self, conn: HTTPConnection) -> AuthResult:
        for backend in self.backends:
            try:
                auth_result = await backend.authenticate(conn)
            except auth.AuthenticationError as exc:
                raise exc from None

            if auth_result is None:
                continue

            return auth_result

        return None
