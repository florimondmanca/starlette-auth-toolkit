import pytest
from starlette.applications import Starlette
from starlette.exceptions import ExceptionMiddleware
from starlette.middleware.authentication import AuthenticationMiddleware
from starlette.responses import PlainTextResponse
from starlette.testclient import TestClient
from starlette.websockets import WebSocket, WebSocketDisconnect

from starlette_auth_toolkit.permissions import PermissionsMiddleware, requires

from .apps.dummy.basic import PASSWORD, USERNAME, BasicAuth


async def raw_asgi(scope, receive, send):
    if scope["type"] == "http":
        response = PlainTextResponse("OK")
        await response(scope, receive, send)
    else:
        ws = WebSocket(scope, receive, send)
        await ws.accept()
        await ws.send_text("OK")
        await ws.close()


starlette = Starlette()


@starlette.route("/", methods=["get", "post"])
async def home(_):
    return PlainTextResponse("OK")


@starlette.websocket_route("/chat")
async def chat(ws):
    await ws.accept()
    await ws.send_text("OK")
    await ws.close()


def via_middleware(app, **kwargs):
    return PermissionsMiddleware(app, scopes=["authenticated"], **kwargs)


def via_decorator(app, **kwargs):
    return requires("authenticated", **kwargs)(app)


@pytest.fixture(name="status_code", params=[None, 404])
def fixture_status_code(request):
    return request.param


@pytest.fixture(name="redirect", params=[None, "/login"])
def fixture_redirect(request):
    return request.param


@pytest.fixture(name="app", params=[raw_asgi, starlette])
def fixture_app(request):
    return request.param


@pytest.fixture(name="client", params=[via_middleware, via_decorator])
def fixture_client(request, app, status_code, redirect):
    add_permissions = request.param

    kwargs = {"methods": ["post"]}
    if status_code is not None:
        kwargs["status_code"] = status_code
    if redirect is not None:
        kwargs["redirect"] = redirect

    app = add_permissions(app, **kwargs)
    app = AuthenticationMiddleware(app, backend=BasicAuth())
    app = ExceptionMiddleware(app)
    return TestClient(app)


@pytest.mark.parametrize(
    "method, auth, success",
    [
        ("get", None, True),
        ("post", None, False),
        ("post", (USERNAME, PASSWORD), True),
    ],
)
def test_http_permissions(client, method, auth, status_code, redirect, success):
    r = getattr(client, method)("/", auth=auth)
    if success:
        assert r.status_code == 200
    elif redirect is not None:
        assert r.status_code == 307
        assert r.headers["Location"] == redirect
    else:
        assert r.status_code == (status_code or 403)


@pytest.mark.parametrize(
    "auth, success", [(None, False), ((USERNAME, PASSWORD), True)]
)
def test_websocket_permissions(client, auth, success):
    if success:
        with client.websocket_connect("/chat", auth=auth):
            return

    with pytest.raises(WebSocketDisconnect) as ctx:
        with client.websocket_connect("/chat", auth=auth):
            pass
    exc: WebSocketDisconnect = ctx.value
    assert exc.code == 1000