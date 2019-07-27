import os
import typing

import databases
import orm
import sqlalchemy
import typesystem
from orm.models import QuerySet
from starlette.applications import Starlette
from starlette.authentication import BaseUser, requires
from starlette.middleware.authentication import AuthenticationMiddleware
from starlette.requests import Request
from starlette.responses import JSONResponse, PlainTextResponse

from starlette_auth_toolkit.backends import MultiAuth
from starlette_auth_toolkit.base.backends import BaseTokenAuth
from starlette_auth_toolkit.contrib.orm import ModelBasicAuth
from starlette_auth_toolkit.cryptography import (
    PBKDF2Hasher,
    generate_random_string,
)

# Database setup

database = databases.Database(
    os.getenv("DATABASE_URL"), force_rollback=os.getenv("TESTING")
)
metadata = sqlalchemy.MetaData()


class UserQuerySet(QuerySet):
    async def create_user(self, *, password: str, **kwargs):
        kwargs["password"] = await hasher.make(password)
        return await self.create(**kwargs)


class User(BaseUser, orm.Model):
    __tablename__ = "user"
    __database__ = database
    __metadata__ = metadata

    objects = UserQuerySet()

    id = orm.Integer(primary_key=True)
    username = orm.String(max_length=128)
    password = orm.String(max_length=128)

    @property
    def display_name(self) -> str:
        return self.username

    @property
    def is_authenticated(self) -> bool:
        return True


class Token(orm.Model):
    __tablename__ = "token"
    __database__ = database
    __metadata__ = metadata

    id = orm.Integer(primary_key=True)
    token = orm.String(max_length=256)
    user = orm.ForeignKey(to=User, allow_null=False)


engine = sqlalchemy.create_engine(str(database.url))
metadata.create_all(engine)


# Authentication backends


hasher = PBKDF2Hasher()


class TokenAuth(BaseTokenAuth):
    async def verify(self, token: str) -> typing.Optional[User]:
        try:
            token = await Token.objects.select_related("user").get(token=token)
        except orm.NoMatch:
            return None
        return token.user


auth_backend = MultiAuth([ModelBasicAuth(User, hasher=hasher), TokenAuth()])


# API schemas


class UserCredentials(typesystem.Schema):
    username = typesystem.String()
    password = typesystem.String()


# Application

app = Starlette()

app.add_middleware(
    AuthenticationMiddleware,
    backend=auth_backend,
    on_error=lambda _, exc: PlainTextResponse(str(exc), status_code=401),
)

app.add_event_handler("startup", database.connect)
app.add_event_handler("shutdown", database.disconnect)


@app.route("/protected")
@requires("authenticated")
async def protected(request):
    """Example protected route."""
    return JSONResponse({"message": f"Hello, {request.user.username}!"})


@app.route("/users", methods=["post"])
async def create_user(request: Request):
    """Example user registration route."""
    credentials = UserCredentials.validate(await request.json())
    user = await User.objects.create(
        username=credentials["username"],
        password=await hasher.make(credentials["password"]),
    )
    return JSONResponse({"username": user.username}, status_code=201)


@app.route("/tokens", methods=["post"])
@requires("authenticated")
async def obtain_token(request: Request):
    """Example token generation route."""
    try:
        token = await Token.objects.get(user=request.user)
    except orm.NoMatch:
        token = await Token.objects.create(
            token=generate_random_string(size=32), user=request.user
        )

    return JSONResponse({"token": token.token}, status_code=201)
