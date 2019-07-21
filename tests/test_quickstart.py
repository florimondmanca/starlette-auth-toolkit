import pytest
from starlette.testclient import TestClient


@pytest.fixture(name="client")
def fixture_client():
    from .apps.quickstart import app

    with TestClient(app) as client:
        yield client


def test_quickstart(client):
    r = client.get("/")
    assert r.status_code == 403

    for username, password in (("alice", "alicepwd"), ("bob", "bobpwd")):
        r = client.get("/", auth=(username, password))
        assert r.status_code == 200

        r = client.get("/", auth=(username, "wrong"))
        assert r.status_code == 401

        r = client.get("/", auth=("wrong", password))
        assert r.status_code == 401
