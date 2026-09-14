"""Tests pour les endpoints de logs."""
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


def test_create_log_success(client):
    """Test de création de log réussie."""
    resp = client.post(
        "/logs",
        json={
            "message": "Test log message",
            "level": "INFO",
            "source": "test",
        },
    )
    assert resp.status_code == 201
    assert resp.json()["message"] == "Test log message"


def test_create_log_invalid_level(client):
    """Test de création avec niveau invalide."""
    resp = client.post(
        "/logs",
        json={
            "message": "Test",
            "level": "INVALID",
            "source": "test",
        },
    )
    assert resp.status_code == 422


def test_get_logs_list(client):
    """Test de récupération de la liste des logs."""
    # Créer un log d'abord
    client.post(
        "/logs",
        json={"message": "List test", "level": "ERROR", "source": "tester"},
    )
    resp = client.get("/logs")
    assert resp.status_code == 200
    assert len(resp.json()) >= 1


def test_get_log_by_id(client):
    """Test de récupération d'un log par son ID."""
    create_resp = client.post(
        "/logs",
        json={"message": "Single test", "level": "WARNING", "source": "tester"},
    )
    log_id = create_resp.json()["id"]
    resp = client.get(f"/logs/{log_id}")
    assert resp.status_code == 200
    assert resp.json()["id"] == log_id


def test_get_log_not_found(client):
    """Test de récupération d'un log inexistant."""
    resp = client.get("/logs/9999")
    assert resp.status_code == 404