import base64
import binascii
import inspect
import typing

from starlette.authentication import (
    AuthCredentials,
    AuthenticationBackend,
    AuthenticationError,
    BaseUser,
    UnauthenticatedUser,
)
from starlette.requests import HTTPConnection

from .datatypes import AuthResult
from .exceptions import InvalidCredentials


class AuthBackend(AuthenticationBackend):
    scheme: str = None

    def invalid_credentials(self) -> AuthenticationError:
        return InvalidCredentials(
            "Could not authenticate with the provided credentials",
            scheme=self.scheme,
        )


class BaseSchemeAuthBackend(AuthBackend):
    def get_credentials(self, conn: HTTPConnection) -> typing.Optional[str]:
        if "Authorization" not in conn.headers:
            return None

        auth = conn.headers.get("Authorization")

        try:
            scheme, credentials = auth.split()
        except ValueError:
            raise self.invalid_credentials()

        if scheme.lower() != self.scheme:
            return None

        return self.decode_credentials(credentials)

    def decode_credentials(self, credentials: str) -> str:
        try:
            return base64.b64decode(credentials).decode("ascii")
        except (ValueError, UnicodeDecodeError, binascii.Error):
            raise self.invalid_credentials()

    async def authenticate(self, conn: HTTPConnection):
        credentials = self.get_credentials(conn)
        if credentials is None:
            return None

        user = await self.verify(credentials)
        if user is None:
            raise self.invalid_credentials()

        return AuthCredentials(["authenticated"]), user

    async def verify(self, credentials: str) -> typing.Optional[BaseUser]:
        raise NotImplementedError


class BasicAuthBackend(BaseSchemeAuthBackend):
    scheme = "basic"

    async def verify(self, credentials: str) -> typing.Optional[BaseUser]:
        try:
            username, password = credentials.split(":")
        except ValueError:
            raise self.invalid_credentials()
        return await self.check_user(username, password)

    async def check_user(
        self, username: str, password: str
    ) -> typing.Optional[BaseUser]:
        raise NotImplementedError


class BearerTokenAuthBackend(BaseSchemeAuthBackend):
    scheme = "bearer"

    class InvalidCredentials(AuthenticationError):
        pass

    async def verify(self, credentials: str) -> typing.Optional[BaseUser]:
        return await self.check_token(token=credentials)

    async def check_token(self, token: str) -> typing.Optional[BaseUser]:
        raise NotImplementedError


class APIKeyAuthBackend(AuthBackend):
    def __init__(self, *, header: str = None, query_param: str = None):
        if not bool(header) ^ bool(query_param):
            raise ValueError(
                "exactly one of `header=` or `query_param=` must be set"
            )
        if header:
            self.get_api_key = lambda conn: conn.headers.get(header)
        else:
            self.get_api_key = lambda conn: conn.query_param.get(query_param)

    async def authenticate(self, conn: HTTPConnection) -> AuthResult:
        api_key: typing.Optional[str] = self.get_api_key(conn)
        if api_key is None:
            return None

        scopes = await self.verify(api_key)
        if scopes is None:
            raise self.invalid_credentials()

        return AuthCredentials(scopes), UnauthenticatedUser()

    async def verify(self, api_key: str) -> typing.Optional[typing.List[str]]:
        raise NotImplementedError


class MultiAuthBackend(AuthBackend):
    def __init__(self, backends: typing.List[AuthenticationBackend]):
        self.backends: typing.List[AuthenticationBackend] = [
            backend() if inspect.isclass(backend) else backend
            for backend in backends
        ]

    async def authenticate(self, conn: HTTPConnection) -> AuthResult:
        for backend in self.backends:
            try:
                auth_result = await backend.authenticate(conn)
            except AuthenticationError as exc:
                raise exc from None

            if auth_result is None:
                continue

            return auth_result

        raise self.invalid_credentials()
