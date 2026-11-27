from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

def test_health():
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "ok", "service": "atlas-api"}

def test_openapi_available():
    assert client.get("/openapi.json").status_code == 200
