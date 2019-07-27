import pytest
from starlette.testclient import TestClient

from .apps.dummy.basic import get_app, USERNAME, PASSWORD


@pytest.fixture(name="client")
def fixture_client():
    return TestClient(get_app())


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
