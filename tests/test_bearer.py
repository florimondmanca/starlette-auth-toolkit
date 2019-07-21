import typing

import pytest
from starlette.applications import Starlette
from starlette.authentication import SimpleUser, requires
from starlette.middleware.authentication import AuthenticationMiddleware
from starlette.responses import PlainTextResponse
from starlette.testclient import TestClient

from starlette_auth_toolkit.base import backends

TOKEN = "s3kr3t"


class BearerAuthBackend(backends.BearerAuthBackend):
    async def verify(self, token: str) -> typing.Optional[SimpleUser]:
        if token == TOKEN:
            return SimpleUser("bob")
        return None


@pytest.fixture(name="app")
def fixture_app():
    def on_error(request, exc):
        return PlainTextResponse(str(exc), status_code=401)

    app = Starlette()
    app.add_middleware(
        AuthenticationMiddleware, backend=BearerAuthBackend(), on_error=on_error
    )

    @app.route("/")
    @requires("authenticated", status_code=403)
    async def index(request):
        assert request.user.username == "bob"
        return PlainTextResponse("OK")

    return app


@pytest.fixture(name="client")
def fixture_client(app):
    return TestClient(app)


@pytest.mark.parametrize(
    "token,status_code", [(TOKEN, 200), (None, 403), ("doesnotexist", 401)]
)
def test_bearer_auth(client, token, status_code):
    headers = {}
    if token:
        headers["Authorization"] = f"Bearer {token}"

    r = client.get("/", headers=headers)
    assert r.status_code == status_code


def test_wrong_scheme(client):
    r = client.get("/", headers={"Authorization": f"Other {TOKEN}"})
    assert r.status_code == 403
