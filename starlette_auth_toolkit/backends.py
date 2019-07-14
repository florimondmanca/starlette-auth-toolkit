import base64
import binascii
import importlib
import inspect
import typing

from starlette import authentication as auth
from starlette.requests import HTTPConnection

from .datatypes import AuthResult
from .exceptions import InvalidCredentials


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


class APIKeyAuthBackend(AuthBackend):
    def __init__(self, *, header: str = None, query_param: str = None):
        if header is not None:
            self._key_getter = lambda conn: conn.headers.get(header)
        elif query_param is not None:
            self._key_getter = lambda conn: conn.query_param.get(query_param)
        else:
            raise ValueError("expected 'header' or 'query_param' to be given")

    async def get_api_key(self, conn: HTTPConnection) -> typing.Optional[str]:
        return self._key_getter(conn)

    async def authenticate(self, conn: HTTPConnection) -> AuthResult:
        api_key = self.get_api_key(conn)
        if api_key is None:
            return None

        scopes = await self.verify(api_key)
        if scopes is None:
            raise InvalidCredentials

        return auth.AuthCredentials(scopes), auth.UnauthenticatedUser()

    async def verify(self, api_key: str) -> typing.Optional[typing.List[str]]:
        raise NotImplementedError


BackendDeclaration = typing.Union[str, AuthBackend]


def load_backends(
    declarations: typing.List[BackendDeclaration]
) -> typing.List[AuthBackend]:
    backends = []
    for decl in declarations:
        if isinstance(decl, str):
            module_name, sep, class_name = decl.partition(":")
            assert sep == ":", (
                "Backend must be formatted as 'path.to.module:classname', "
                f"got {decl}"
            )
            module = importlib.import_module(module_name)
            backend_cls = getattr(module, class_name)
            backend = backend_cls()
        else:
            backend = decl() if inspect.isclass(decl) else decl
            assert isinstance(backend, AuthBackend)
            backends.append(backend)
    return backends


class MultiAuthBackend(AuthBackend):
    def __init__(self, declarations: typing.List[BackendDeclaration]):
        self.backends = load_backends(declarations)

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
