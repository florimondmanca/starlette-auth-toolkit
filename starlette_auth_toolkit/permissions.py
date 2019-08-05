import typing

from starlette.exceptions import HTTPException
from starlette.requests import HTTPConnection, Request
from starlette.responses import RedirectResponse
from starlette.types import ASGIApp, Scope, Receive, Send
from starlette.websockets import WebSocket


class PermissionsMiddleware:
    def __init__(
        self,
        app,
        scopes: typing.Sequence[str],
        status_code: int = 403,
        redirect: str = None,
        methods: typing.Sequence[str] = None,
    ):
        self.app = app
        self.scopes = scopes
        self.status_code = status_code
        self.redirect = redirect
        self.methods = {method.lower() for method in methods}

    def has_required_scope(self, conn: HTTPConnection) -> bool:
        return all(scope in conn.auth.scopes for scope in self.scopes)

    def redirect_response(self, url: str) -> ASGIApp:
        return RedirectResponse(url)

    def unauthorized(self):
        raise HTTPException(status_code=self.status_code)

    async def handle_http(self, scope: Scope, receive: Receive, send: Send):
        request = Request(scope, receive)

        if request.method.lower() in self.methods:
            if not self.has_required_scope(request):
                if self.redirect is not None:
                    response = self.redirect_response(self.redirect)
                    return await response(scope, receive, send)
                return self.unauthorized()

        await self.app(scope, receive, send)

    async def handle_websocket(
        self, scope: Scope, receive: Receive, send: Send
    ):
        websocket = WebSocket(scope, receive, send)

        if not self.has_required_scope(websocket):
            await websocket.close()
            return

        await self.app(scope, receive, send)

    async def __call__(self, scope: Scope, receive: Receive, send: Send):
        assert scope["type"] in {"http", "websocket"}
        if scope["type"] == "http":
            await self.handle_http(scope, receive, send)
        else:
            await self.handle_websocket(scope, receive, send)


def requires(
    *scopes: str,
    status_code: int = 403,
    redirect: str = None,
    methods: typing.Sequence[str] = None
):
    def decorate(app: ASGIApp) -> ASGIApp:
        return PermissionsMiddleware(
            app,
            scopes=scopes,
            status_code=status_code,
            redirect=redirect,
            methods=methods,
        )

    return decorate
