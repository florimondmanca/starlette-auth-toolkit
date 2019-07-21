import typing

import pytest
from starlette.applications import Starlette
from starlette.authentication import SimpleUser, requires
from starlette.middleware.authentication import AuthenticationMiddleware
from starlette.responses import PlainTextResponse
from starlette.testclient import TestClient

from starlette_auth_toolkit.base import backends

USERNAME = "user"
PASSWORD = "s3kr3t"


class BasicAuthBackend(backends.BasicAuthBackend):
    async def verify(
        self, username: str, password: str
    ) -> typing.Optional[SimpleUser]:
        if (username, password) == (USERNAME, PASSWORD):
            return SimpleUser(username)
        return None


@pytest.fixture(name="app")
def fixture_app():
    def on_error(request, exc):
        return PlainTextResponse(str(exc), status_code=401)

    app = Starlette()
    app.add_middleware(
        AuthenticationMiddleware, backend=BasicAuthBackend(), on_error=on_error
    )

    @app.route("/")
    @requires("authenticated", status_code=403)
    async def index(request):
        return PlainTextResponse("OK")

    return app


@pytest.fixture(name="client")
def fixture_client(app):
    return TestClient(app)


@pytest.mark.parametrize(
    "username, password, status_code",
    [
        (USERNAME, PASSWORD, 200),
        ("foo", PASSWORD, 401),
        (USERNAME, "foo", 401),
        (None, None, 403),
    ],
)
def test_basic_auth(client, username, password, status_code):
    kwargs = {}
    if username and password:
        kwargs["auth"] = (username, password)

    r = client.get("/", **kwargs)
    assert r.status_code == status_code


@pytest.mark.parametrize(
    "authorization", ["Basic userpass", "Basic user:pass:withcolon"]
)
def test_malformed_credentials(client, authorization):
    r = client.get("/", headers={"Authorization": authorization})
    assert r.status_code == 401


def test_wrong_scheme(client):
    r = client.get(
        "/", headers={"Authorization": f"Other {USERNAME}:{PASSWORD}"}
    )
    assert r.status_code == 403
