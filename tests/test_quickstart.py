import pytest
from starlette.testclient import TestClient


@pytest.fixture(name="client")
def fixture_client():
    from .apps.quickstart import app

    with TestClient(app) as client:
        yield client


@pytest.fixture(name="protected_path")
def fixture_protected_path() -> str:
    return "/protected"


def test_quickstart(client, protected_path):
    r = client.get(protected_path)
    assert r.status_code == 403

    for username, password in (("alice", "alicepwd"), ("bob", "bobpwd")):
        r = client.get(protected_path, auth=(username, password))
        assert r.status_code == 200

        r = client.get(protected_path, auth=(username, "wrong"))
        assert r.status_code == 401

        r = client.get(protected_path, auth=("wrong", password))
        assert r.status_code == 401
