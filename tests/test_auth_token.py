import pytest
from starlette.testclient import TestClient

from .apps.dummy.token import TOKEN, get_app


@pytest.fixture(name="client")
def fixture_client():
    return TestClient(get_app())


@pytest.mark.parametrize(
    "token, status_code", [(TOKEN, 200), (None, 403), ("doesnotexist", 401)]
)
def test_auth(client, token, status_code):
    headers = {}
    if token:
        headers["Authorization"] = f"Token {token}"

    r = client.get("/", headers=headers)
    assert r.status_code == status_code


def test_wrong_scheme(client):
    r = client.get("/", headers={"Authorization": f"Other {TOKEN}"})
    assert r.status_code == 403
