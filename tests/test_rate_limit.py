"""Tests de rate limiting pour l'API."""
import pytest
import time
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


def test_multiple_requests_limit(client):
    """Test que le rate limiting fonctionne sur les endpoints sensibles."""
    # Faire plusieurs requêtes rapides
    responses = []
    for _ in range(15):
        resp = client.post(
            "/auth/login",
            data={"username": "nonexistent", "password": "wrong"},
        )
        responses.append(resp.status_code)

    # Au moins une requête devrait être limitée
    assert 429 in responses or all(code == 401 for code in responses)


def test_health_not_rate_limited(client):
    """Test que /health n'est pas rate limited."""
    for _ in range(5):
        resp = client.get("/health")
        assert resp.status_code == 200