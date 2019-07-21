import typing

import orm
import typesystem
from starlette.applications import Starlette
from starlette.exceptions import HTTPException
from starlette.requests import Request
from starlette.responses import JSONResponse

from starlette_auth_toolkit.base.backends import (
    MultiAuthBackend,
    BasicAuthBackend,
    BearerAuthBackend,
)
from starlette_auth_toolkit.passwords import generate_random_string

from ..utils import get_base_app
from .models import Token, User, database
from .resources import authenticate, hasher


class BasicAuth(BasicAuthBackend):
    verify = staticmethod(authenticate)


class BearerAuth(BearerAuthBackend):
    async def verify(self, token: str) -> typing.Optional[User]:
        try:
            token = await Token.objects.select_related("user").get(token=token)
        except orm.NoMatch:
            return None
        return token.token


class UserCredentials(typesystem.Schema):
    username = typesystem.String()
    password = typesystem.String()


def get_app() -> Starlette:
    app = get_base_app(backend=MultiAuthBackend([BearerAuth(), BasicAuth()]))

    @app.route("/users", methods=["post"])
    async def create_user(request: Request):
        credentials = UserCredentials.validate(await request.json())
        user = await User.objects.create(
            username=credentials["username"],
            password=await hasher.make(credentials["password"]),
        )
        return JSONResponse({"username": user.username}, status_code=201)

    @app.route("/tokens", methods=["post"])
    async def obtain_token(request: Request):
        credentials = UserCredentials.validate(await request.json())
        user = await authenticate(
            credentials["username"], credentials["password"]
        )
        if user is None:
            raise HTTPException(401)

        try:
            token = await Token.objects.get(user=user)
        except orm.NoMatch:
            token = await Token.objects.create(
                token=generate_random_string(size=32), user=user
            )

        return JSONResponse({"token": token.token}, status_code=201)

    app.add_event_handler("startup", database.connect)
    app.add_event_handler("shutdown", database.disconnect)

    return app
