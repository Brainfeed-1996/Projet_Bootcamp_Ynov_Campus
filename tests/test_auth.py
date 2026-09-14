"""Tests pour les endpoints d'authentification."""
import pytest
from fastapi.testclient import TestClient
from app import app, get_engine, Base
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker


@pytest.fixture
def client():
    return TestClient(app)


@pytest.fixture(autouse=True)
def reset_database():
    """Réinitialise la base de données avant chaque test."""
    engine = get_engine()
    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)
    yield
    Base.metadata.drop_all(bind=engine)


def test_login_success(client):
    """Test de connexion réussie."""
    # Créer d'abord un utilisateur
    client.post(
        "/users",
        json={
            "username": "testuser",
            "email": "test@example.com",
            "password": "SecurePass123",
        },
    )
    resp = client.post(
        "/auth/login",
        data={"username": "testuser", "password": "SecurePass123"},
    )
    assert resp.status_code == 200
    assert "access_token" in resp.json()


def test_login_invalid_credentials(client):
    """Test de connexion avec des identifiants invalides."""
    resp = client.post(
        "/auth/login",
        data={"username": "nonexistent", "password": "wrong"},
    )
    assert resp.status_code == 401


def test_login_missing_fields(client):
    """Test de connexion sans champs requis."""
    resp = client.post("/auth/login", data={})
    assert resp.status_code == 422
def test_token_expiration():
    # Test with expired token
    expired_token = create_access_token({'sub': 'test'}, expires_delta=timedelta(seconds=-1))
    resp = client.get('/logs', headers={'Authorization': f'Bearer {expired_token}'})
    assert resp.status_code == 401

def test_invalid_token_format():
    resp = client.get('/logs', headers={'Authorization': 'InvalidToken'})
    assert resp.status_code == 401
