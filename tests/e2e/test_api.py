import pytest
from fastapi.testclient import TestClient

from src.api import api


@pytest.fixture
def test_client():
    with TestClient(api) as client:
        yield client


def test_can_get_lock_info(test_client):
    test_client.post("/locks", json={"name": "Test"})
    resp = test_client.get("/locks/Test")

    assert resp.status_code == 200
    assert resp.json() == {"name": "Test", "is_locked": False}


def test_get_404_if_no_lock(test_client):
    resp = test_client.get("/locks/Test")
    assert resp.status_code == 404


def test_can_acquire_lock(test_client):
    test_client.post("/locks", json={"name": "Test"})
    test_client.post("/locks/Test/acquire")

    resp = test_client.get("/locks/Test")
    assert resp.json() == {"name": "Test", "is_locked": True}


def test_can_release_lock(test_client):
    test_client.post("/locks", json={"name": "Test"})
    test_client.post("/locks/Test/acquire")
    test_client.post("/locks/Test/release")

    resp = test_client.get("/locks/Test")
    assert resp.json() == {"name": "Test", "is_locked": False}
