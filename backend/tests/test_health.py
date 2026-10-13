from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)


def test_health_endpoint():
    response = client.get("/api/health")
    assert response.status_code == 200
    assert response.json() == {
        "status": "ok",
        "service": "scopeguard-api",
        "mode": "local",
    }


def test_root_endpoint():
    response = client.get("/")
    assert response.status_code == 200
    assert response.json()["name"] == "ScopeGuard Local API"
