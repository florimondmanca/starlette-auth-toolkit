import typing

from starlette.applications import Starlette
from starlette.authentication import requires
from starlette.middleware.authentication import AuthenticationMiddleware
from starlette.responses import JSONResponse, PlainTextResponse

from starlette_auth_toolkit.base.backends import BasicAuthBackend
from starlette_auth_toolkit.base.helpers import BaseAuthenticate
from starlette_auth_toolkit.cryptography import PBKDF2Hasher


# User model


class User(typing.NamedTuple):
    username: str
    password: str


# Password hasher

hasher = PBKDF2Hasher()


# Fake storage

USERS = {
    "alice": User(username="alice", password=hasher.make_sync("alicepwd")),
    "bob": User(username="bob", password=hasher.make_sync("bobpwd")),
}


# Authentication helper


class Authenticate(BaseAuthenticate):
    async def find_user(self, username: str):
        return USERS.get(username)

    async def verify_password(self, user: User, password: str):
        return await hasher.verify(password, user.password)


authenticate = Authenticate()


# Authentication backend


class BasicAuth(BasicAuthBackend):
    async def verify(
        self, username: str, password: str
    ) -> typing.Optional[User]:
        return await authenticate(username, password)


# Application


def on_auth_error(request, exc):
    return PlainTextResponse(str(exc), status_code=401)


app = Starlette()
app.add_middleware(
    AuthenticationMiddleware, backend=BasicAuth(), on_error=on_auth_error
)


@app.route("/")
@requires("authenticated")
async def home(request):
    """Example protected route."""
    return JSONResponse({"message": f"Hello, {request.user.username}!"})
