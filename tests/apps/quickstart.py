import typing

from starlette.applications import Starlette
from starlette.middleware.authentication import AuthenticationMiddleware
from starlette.responses import JSONResponse, PlainTextResponse

from starlette_auth_toolkit.base.backends import BaseBasicAuth
from starlette_auth_toolkit.cryptography import PBKDF2Hasher
from starlette_auth_toolkit.permissions import requires


hasher = PBKDF2Hasher()


class User(typing.NamedTuple):
    username: str
    password: str


USERS = {
    "alice": User(username="alice", password=hasher.make_sync("alicepwd")),
    "bob": User(username="bob", password=hasher.make_sync("bobpwd")),
}


class BasicAuth(BaseBasicAuth):
    async def find_user(self, username: str):
        return USERS.get(username)

    async def verify_password(self, user: User, password: str):
        return await hasher.verify(password, user.password)


app = Starlette()

app.add_middleware(
    AuthenticationMiddleware,
    backend=BasicAuth(),
    on_error=lambda _, exc: PlainTextResponse(str(exc), status_code=401),
)


@requires("authenticated")
@app.route("/protected")
async def protected(request):
    return JSONResponse({"message": f"Hello, {request.user}!"})
