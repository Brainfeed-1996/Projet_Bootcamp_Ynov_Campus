"""Tests pour les endpoints de gestion des utilisateurs."""
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


def test_create_user(client):
    """Test de création d'utilisateur."""
    resp = client.post(
        "/users",
        json={
            "username": "newuser",
            "email": "new@example.com",
            "password": "Password123",
            "role": "reader",
        },
    )
    assert resp.status_code == 201
    assert resp.json()["username"] == "newuser"
    assert resp.json()["role"] == "reader"


def test_create_user_duplicate_username(client):
    """Test de création avec un nom d'utilisateur existant."""
    client.post(
        "/users",
        json={"username": "dup", "email": "dup1@example.com", "password": "Password123"},
    )
    resp = client.post(
        "/users",
        json={"username": "dup", "email": "dup2@example.com", "password": "Password123"},
    )
    assert resp.status_code == 409


def test_create_user_invalid_role(client):
    """Test de création avec un rôle invalide."""
    resp = client.post(
        "/users",
        json={
            "username": "badrole",
            "email": "bad@example.com",
            "password": "Password123",
            "role": "superadmin",
        },
    )
    assert resp.status_code == 422


def test_delete_user(client):
    """Test de suppression d'utilisateur."""
    create_resp = client.post(
        "/users",
        json={"username": "todelete", "email": "delete@example.com", "password": "Password123"},
    )
    user_id = create_resp.json()["id"]
    resp = client.delete(f"/users/{user_id}")
    assert resp.status_code == 200
    assert resp.json()["status"] == "deleted"