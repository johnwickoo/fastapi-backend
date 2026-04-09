from fastapi.testclient import TestClient
from main import app

client = TestClient(app)

def test_root_not_found():
    response = client.get("/")
    assert response.status_code == 404

def test_get_sessions():
    response = client.get("/sessions")
    assert response.status_code == 200
    assert isinstance(response.json(), list)

def test_create_session():
    response = client.post("/log", json={
        "task": "test session",
        "hours": 1,
        "rating": 4,
        "blockers": "none"
    })
    assert response.status_code == 200
    assert response.json()["task"] == "Test Session"

def test_get_session_not_found():
    response = client.get("/sessions/99999")
    assert response.status_code == 404

def test_delete_without_token():
    response = client.delete("/sessions/1")
    assert response.status_code == 401