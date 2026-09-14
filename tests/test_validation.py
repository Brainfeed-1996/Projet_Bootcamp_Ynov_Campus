"""Tests de validation des limites et contraintes."""
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


def test_log_message_too_long(client):
    """Test qu'un message trop long est rejeté."""
    long_message = "A" * 5000  # Max is 4096
    resp = client.post(
        "/logs",
        json={"message": long_message, "level": "INFO"},
    )
    assert resp.status_code == 422


def test_log_source_empty(client):
    """Test qu'une source vide est rejetée."""
    resp = client.post(
        "/logs",
        json={"message": "Test", "source": "  "},
    )
    assert resp.status_code == 422


def test_limit_query_parameter_invalid(client):
    """Test qu'une valeur de limit invalide est rejetée."""
    resp = client.get("/logs?limit=0")
    assert resp.status_code == 400

    resp = client.get("/logs?limit=99999")
    assert resp.status_code == 400


def test_user_password_too_long(client):
    """Test qu'un mot de passe trop long est rejeté."""
    long_password = "A" * 73  # Max is 72 for bcrypt
    resp = client.post(
        "/users",
        json={
            "username": "testuser",
            "email": "test@example.com",
            "password": long_password,
        },
    )
    assert resp.status_code == 422


def test_user_role_invalid(client):
    """Test qu'un rôle invalide est rejeté."""
    resp = client.post(
        "/users",
        json={
            "username": "testuser",
            "email": "test@example.com",
            "password": "Password123",
            "role": "superadmin",
        },
    )
    assert resp.status_code == 422