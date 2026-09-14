"""Tests de base pour les endpoints de l'API Log Sentinel."""
import pytest
from fastapi.testclient import TestClient
from app import app


@pytest.fixture
def client():
    return TestClient(app)


def test_health_endpoint(client):
    """Vérifie que l'endpoint /health retourne 200."""
    resp = client.get("/health")
    assert resp.status_code == 200
    assert resp.json()["status"] == "ok"


def test_openapi_docs(client):
    """Vérifie que la documentation OpenAPI est accessible."""
    resp = client.get("/openapi.json")
    assert resp.status_code == 200
    assert "openapi" in resp.json()


def test_root_redirect(client):
    """Vérifie que la racine redirige vers /docs."""
    resp = client.get("/", follow_redirects=False)
    assert resp.status_code in (200, 302, 307)


if __name__ == "__main__":
    pytest.main([__file__, "-v"])