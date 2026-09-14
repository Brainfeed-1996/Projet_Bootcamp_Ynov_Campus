"""Tests de configuration et d'intégration."""
import pytest
import os
from fastapi.testclient import TestClient
from app import app, get_engine, Base, _build_database_url


@pytest.fixture
def client():
    return TestClient(app)


def test_database_url_with_testing_env(monkeypatch):
    """Test que la variable TESTING active SQLite."""
    monkeypatch.setenv("TESTING", "1")
    url = _build_database_url()
    assert "sqlite" in url


def test_database_url_with_custom_url(monkeypatch):
    """Test qu'une URL personnalisée est utilisée."""
    monkeypatch.setenv("DATABASE_URL", "postgresql://test:test@localhost/test")
    url = _build_database_url()
    assert url == "postgresql://test:test@localhost/test"


def test_database_url_missing_config(monkeypatch):
    """Test d'erreur si la configuration DB est manquante."""
    monkeypatch.delenv("DATABASE_URL", raising=False)
    monkeypatch.delenv("TESTING", raising=False)
    monkeypatch.delenv("DB_USER", raising=False)
    monkeypatch.delenv("DB_PASSWORD", raising=False)
    with pytest.raises(RuntimeError):
        _build_database_url()


def test_health_endpoint_with_db(client):
    """Test de l'endpoint health avec une base de données."""
    resp = client.get("/health")
    assert resp.status_code == 200
    assert resp.json()["status"] == "ok"


def test_openapi_schema_includes_paths(client):
    """Test que le schéma OpenAPI inclut les endpoints."""
    resp = client.get("/openapi.json")
    assert resp.status_code == 200
    schema = resp.json()
    assert "/logs" in schema["paths"]
    assert "/users" in schema["paths"]
    assert "/analyses" in schema["paths"]
    assert "/auth/login" in schema["paths"]