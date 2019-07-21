import os

import pytest
from starlette.testclient import TestClient


os.environ["DATABASE_URL"] = "sqlite:///tests/example.db"
os.environ["TESTING"] = "true"


@pytest.fixture(name="client")
def fixture_client():
    from .apps.example import app

    with TestClient(app) as client:
        yield client


def test_example(client):
    credentials = {"username": "bob", "password": "s3kr3t"}
    auth = (credentials["username"], credentials["password"])

    r = client.get("/")
    assert r.status_code == 403

    r = client.post("/users", json=credentials)
    assert r.status_code == 201

    r = client.get("/", auth=auth)
    assert r.status_code == 200

    r = client.get("/", auth=(auth[0], "wrong"))
    assert r.status_code == 401

    r = client.get("/", auth=("wrong", auth[1]))
    assert r.status_code == 401

    r = client.post("/tokens", json=credentials, auth=auth)
    assert r.status_code == 201
    token = r.json()["token"]

    r = client.get("/", headers={"Authorization": f"Bearer {token}"})
    assert r.status_code == 200

    r = client.get("/", headers={"Authorization": f"Bearer wrong"})
    assert r.status_code == 401
