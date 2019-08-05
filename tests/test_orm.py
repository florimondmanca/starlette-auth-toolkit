import os

import pytest
from starlette.testclient import TestClient

pytest.importorskip("passlib")


@pytest.fixture(name="client")
def fixture_client():
    from .apps.orm.token import get_app
    from .apps.orm.models import database

    with TestClient(get_app()) as client:
        yield client

    os.remove(database.url.database)


def register(client, credentials: dict) -> tuple:
    r = client.post("/users", json=credentials)
    assert r.status_code == 201


def authorize_basic(client, credentials: dict):
    r = client.get("/", auth=(credentials["username"], credentials["password"]))
    assert r.status_code == 200


def obtain_token(client, credentials: dict) -> str:
    r = client.post("/tokens", json=credentials)
    assert r.status_code == 201
    return r.json()["token"]


def authorize_token(client, token: str):
    r = client.get("/", headers={"Authorization": f"Token {token}"})
    assert r.status_code == 200


def test_user_journey(client):
    credentials = {"username": "admin", "password": "admin"}
    register(client, credentials)
    authorize_basic(client, credentials)
    token = obtain_token(client, credentials)
    authorize_token(client, token)
