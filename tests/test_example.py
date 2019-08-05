import os

import pytest
from starlette.testclient import TestClient

pytest.importorskip("passlib")


@pytest.fixture(name="client")
def fixture_client():
    os.environ["DATABASE_URL"] = "sqlite:///tests/example.db"
    os.environ["TESTING"] = "true"

    from .apps.example import app, database

    with TestClient(app) as client:
        yield client

    os.remove(database.url.database)


@pytest.fixture(name="protected_path")
def fixture_protected_path() -> str:
    return "/protected"


def test_example(client, protected_path):
    credentials = {"username": "bob", "password": "s3kr3t"}
    auth = (credentials["username"], credentials["password"])

    r = client.get(protected_path)
    assert r.status_code == 403

    r = client.post("/users", json=credentials)
    assert r.status_code == 201

    r = client.get(protected_path, auth=auth)
    assert r.status_code == 200

    r = client.get(protected_path, auth=(auth[0], "wrong"))
    assert r.status_code == 401

    r = client.get(protected_path, auth=("wrong", auth[1]))
    assert r.status_code == 401

    r = client.post("/tokens", json=credentials, auth=auth)
    assert r.status_code == 201
    token = r.json()["token"]

    r = client.get(protected_path, headers={"Authorization": f"Token {token}"})
    assert r.status_code == 200

    r = client.get(protected_path, headers={"Authorization": f"Token wrong"})
    assert r.status_code == 401
