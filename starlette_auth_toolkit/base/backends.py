import base64
import binascii
import typing

from starlette import authentication as auth
from starlette.requests import HTTPConnection

from ..datatypes import AuthResult
from ..exceptions import InvalidCredentials


class AuthBackend(auth.AuthenticationBackend):
    async def authenticate(self, conn: HTTPConnection) -> AuthResult:
        raise NotImplementedError


class _SchemeAuthBackend(AuthBackend):
    scheme: str

    def get_credentials(self, conn: HTTPConnection) -> typing.Optional[str]:
        if "Authorization" not in conn.headers:
            return None

        authorization = conn.headers.get("Authorization")
        scheme, _, credentials = authorization.partition(" ")
        if scheme.lower() != self.scheme.lower():
            return None

        return credentials

    def parse_credentials(self, credentials: str) -> typing.List[str]:
        return [credentials]

    verify: typing.Callable[
        ..., typing.Awaitable[typing.Optional[auth.BaseUser]]
    ]

    async def authenticate(self, conn: HTTPConnection):
        credentials = self.get_credentials(conn)
        if credentials is None:
            return None

        parts = self.parse_credentials(credentials)
        user = await self.verify(*parts)
        if user is None:
            raise InvalidCredentials

        return auth.AuthCredentials(["authenticated"]), user


class BasicAuthBackend(_SchemeAuthBackend):
    scheme = "Basic"

    def parse_credentials(self, credentials: str) -> typing.List[str]:
        try:
            decoded_credentials = base64.b64decode(credentials).decode("ascii")
        except (ValueError, UnicodeDecodeError, binascii.Error):
            raise InvalidCredentials

        try:
            username, password = decoded_credentials.split(":")
        except ValueError:
            raise InvalidCredentials

        return [username, password]

    async def verify(
        self, username: str, password: str
    ) -> typing.Optional[auth.BaseUser]:
        raise NotImplementedError


class BearerAuthBackend(_SchemeAuthBackend):
    scheme = "Bearer"

    def parse_credentials(self, credentials: str) -> typing.List[str]:
        token = credentials
        return [token]

    async def verify(self, token: str) -> typing.Optional[auth.BaseUser]:
        raise NotImplementedError
