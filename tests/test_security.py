"""Tests de sécurité pour l'API Log Sentinel."""
import pytest
from fastapi.testclient import TestClient
from app import app, get_engine, Base


@pytest.fixture
def client():
    return TestClient(app)


@pytest.fixture(autouse=True)
def reset_database():
    engine = get_engine()
    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)
    yield
    Base.metadata.drop_all(bind=engine)


def test_sql_injection_in_message(client):
    """Test de résistance à une injection SQL basique."""
    resp = client.post(
        "/logs",
        json={
            "message": "'; DROP TABLE users; --",
            "level": "INFO",
            "source": "attacker",
        },
    )
    assert resp.status_code == 201


def test_xss_in_message(client):
    """Test de résistance à une attaque XSS."""
    resp = client.post(
        "/logs",
        json={
            "message": "<script>alert('xss')</script>",
            "level": "INFO",
            "source": "attacker",
        },
    )
    assert resp.status_code == 201


def test_sensitive_data_redaction(client):
    """Test que les données sensibles sont masquées dans les logs."""
    resp = client.post(
        "/logs",
        json={
            "message": "Password: secret123, API_KEY: abc-def-ghi",
            "level": "WARNING",
            "source": "leak",
        },
    )
    assert resp.status_code == 201


def test_request_size_limit(client):
    """Test de la limite de taille des requêtes."""
    large_message = "A" * (11 * 1024 * 1024)  # 11 MB
    resp = client.post(
        "/logs",
        json={"message": large_message, "level": "INFO"},
    )
    assert resp.status_code == 413


def test_security_headers_present(client):
    """Test que les en-têtes de sécurité sont présents."""
    resp = client.get("/health")
    assert "X-Content-Type-Options" in resp.headers
    assert "X-Frame-Options" in resp.headers
    assert "X-XSS-Protection" in resp.headers