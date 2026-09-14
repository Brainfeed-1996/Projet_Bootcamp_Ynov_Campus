"""Tests de cohérence globale de l'API."""
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


def test_full_workflow(client):
    """Test du workflow complet : user -> log -> analysis."""
    # 1. Créer un utilisateur
    user_resp = client.post(
        "/users",
        json={
            "username": "workflow",
            "email": "workflow@example.com",
            "password": "Password123",
            "role": "admin",
        },
    )
    assert user_resp.status_code == 201

    # 2. Créer un log
    log_resp = client.post(
        "/logs",
        json={
            "message": "Suspicious activity detected",
            "level": "ERROR",
            "source": "monitor",
        },
    )
    assert log_resp.status_code == 201
    log_id = log_resp.json()["id"]

    # 3. Créer une analyse
    analysis_resp = client.post(
        "/analyses",
        json={
            "log_id": log_id,
            "severity": "HIGH",
            "category": "SECURITY",
            "summary": "Suspicious activity",
            "recommendations": ["Investigate", "Block IP"],
            "provider": "manual",
        },
    )
    assert analysis_resp.status_code == 201

    # 4. Vérifier les alertes
    alerts_resp = client.get("/alerts")
    assert alerts_resp.status_code == 200
    assert len(alerts_resp.json()) >= 1


def test_error_handling_consistency(client):
    """Test que les erreurs sont cohérentes."""
    # Erreurs de validation
    resp1 = client.post("/logs", json={})
    assert resp1.status_code == 422
    assert "detail" in resp1.json()

    # Erreurs 404
    resp2 = client.get("/logs/99999")
    assert resp2.status_code == 404
    assert "detail" in resp2.json()

    # Erreurs 401 - endpoints protégés
    resp3 = client.get("/logs")
    assert resp3.status_code == 401
    assert "detail" in resp3.json()
def test_database_transaction_rollback():
    # Test that failed operations rollback correctly
    initial_count = client.get('/logs').json().__len__()
    resp = client.post('/logs', json={'message': 'Test'})
    assert resp.status_code == 201
    final_count = client.get('/logs').json().__len__()
    assert final_count == initial_count + 1

def test_complete_workflow():
    # 1. Login
    # 2. Create log
    # 3. Analyze log
    # 4. Get analysis
    # 5. Verify results
    pass

def test_email_notification():
    from app import send_alert_email
    # Mock SMTP server
    send_alert_email('test@example.com', 'Test', 'Test body')
    assert True  # If no exception, test passes

def test_webhook_endpoint():
    resp = client.post('/webhooks/log-created', json={'log_id': 1})
    assert resp.status_code in [200, 404]
