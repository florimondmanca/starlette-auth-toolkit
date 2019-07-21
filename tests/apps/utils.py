from starlette.applications import Starlette
from starlette.authentication import requires
from starlette.middleware.authentication import AuthenticationMiddleware
from starlette.responses import PlainTextResponse

from starlette_auth_toolkit.base.backends import AuthBackend


def get_base_app(backend: AuthBackend) -> Starlette:
    def on_error(request, exc):  # pylint: disable=unused-argument
        return PlainTextResponse(str(exc), status_code=401)

    app = Starlette()
    app.add_middleware(
        AuthenticationMiddleware, backend=backend, on_error=on_error
    )

    @app.route("/")
    @requires("authenticated", status_code=403)
    async def home(request):  # pylint: disable=unused-argument
        return PlainTextResponse("Hello, world!")

    return app
