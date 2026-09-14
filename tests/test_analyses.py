"""Tests pour les endpoints d'analyses."""
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


def test_create_analysis(client):
    """Test de création d'une analyse."""
    # Créer un log d'abord
    log_resp = client.post(
        "/logs",
        json={"message": "Analysis test log", "level": "ERROR", "source": "analyzer"},
    )
    log_id = log_resp.json()["id"]

    # Créer une analyse
    resp = client.post(
        "/analyses",
        json={
            "log_id": log_id,
            "severity": "HIGH",
            "category": "SECURITY",
            "summary": "Tentative de connexion suspecte",
            "recommendations": ["Vérifier l'IP source", "Bloquer l'accès"],
            "provider": "manual",
        },
    )
    assert resp.status_code == 201
    assert resp.json()["severity"] == "HIGH"


def test_get_analyses_list(client):
    """Test de récupération de la liste des analyses."""
    resp = client.get("/analyses")
    assert resp.status_code == 200
    assert isinstance(resp.json(), list)


def test_get_alerts_high_severity(client):
    """Test de récupération des alertes haute sévérité."""
    resp = client.get("/alerts")
    assert resp.status_code == 200
    assert isinstance(resp.json(), list)


def test_analyze_log_not_found(client):
    """Test d'analyse d'un log inexistant."""
    resp = client.post("/logs/9999/analyze")
    assert resp.status_code == 404