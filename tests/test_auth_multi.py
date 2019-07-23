import pytest
from starlette.authentication import SimpleUser, AuthCredentials
from starlette.testclient import TestClient

from starlette_auth_toolkit.backends import MultiAuth
from starlette_auth_toolkit.exceptions import InvalidCredentials

from .apps.utils import get_base_app


class DummyHeaderBackend:
    def __init__(self, header: str, value: str):
        self.header = header
        self.value = value

    async def authenticate(self, conn):
        try:
            value = conn.headers[self.header]
        except KeyError:
            return None

        if value != self.value:
            raise InvalidCredentials

        return AuthCredentials(["authenticated"]), SimpleUser("bob")


backend = MultiAuth(
    [
        DummyHeaderBackend(header="X-Auth-A", value="A"),
        DummyHeaderBackend(header="X-Auth-B", value="B"),
    ]
)


@pytest.fixture(name="client")
def fixture_client():
    return TestClient(get_base_app(backend=backend))


@pytest.mark.parametrize(
    "headers, status_code",
    [
        ({"X-Auth-A": "A"}, 200),
        ({"X-Auth-A": "Not A"}, 401),
        ({"X-Auth-B": "B"}, 200),
        ({"X-Auth-B": "Not B"}, 401),
        ({"X-Auth-A": "A", "X-Auth-B": "B"}, 200),
        ({"X-Auth-A": "Not A", "X-Auth-B": "B"}, 401),
        ({"X-Auth-A": "A", "X-Auth-B": "Not B"}, 200),
        ({"X-Auth-A": "Not A", "X-Auth-B": "Not B"}, 401),
        ({}, 403),
    ],
)
def test_auth(client, headers, status_code):
    r = client.get("/", headers=headers)
    assert r.status_code == status_code
