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
    assert resp.status_code in (200, 302, 307, 404)


def test_export_logs_json(client):
    """Export JSON des logs."""
    resp = client.get('/export/logs?format=json')
    assert resp.status_code == 200
    assert isinstance(resp.json(), list)


def test_export_logs_csv(client):
    """Export CSV des logs en streaming."""
    resp = client.get('/export/logs?format=csv')
    assert resp.status_code == 200
    assert 'text/csv' in resp.headers['content-type']
    assert 'id,level,message,source,created_at' in resp.text


def test_export_logs_invalid_format(client):
    """Format d'export invalide."""
    resp = client.get('/export/logs?format=xml')
    assert resp.status_code == 400


def test_detailed_health(client):
    """Health check détaillé."""
    resp = client.get('/health/detailed')
    assert resp.status_code == 200
    assert 'checks' in resp.json()


def test_webhook_log_created(client):
    """Webhook de création de log avec validation."""
    resp = client.post('/webhooks/log-created', json={
        'event': 'log-created',
        'log_id': 1,
        'level': 'ERROR',
        'message': 'Test webhook message',
        'source': 'api',
    })
    assert resp.status_code == 202
    assert resp.json()['status'] == 'received'


def test_webhook_invalid_level(client):
    """Webhook avec un niveau invalide."""
    resp = client.post('/webhooks/log-created', json={
        'event': 'log-created',
        'log_id': 1,
        'level': 'INVALID',
        'message': 'Test',
        'source': 'api',
    })
    assert resp.status_code == 422


def test_webhook_missing_fields(client):
    """Webhook avec des champs manquants."""
    resp = client.post('/webhooks/log-created', json={
        'event': 'log-created',
        'log_id': 1,
    })
    assert resp.status_code == 422

if __name__ == "__main__":
    pytest.main([__file__, "-v"])


def test_admin_alerts_invalid_email(client):
    """Alerte email avec un email invalide."""
    resp = client.post('/admin/alerts', json={
        'to_email': 'not-an-email',
        'subject': 'Test',
        'body': 'Test body',
    })
    assert resp.status_code == 422


def test_admin_alerts_missing_fields(client):
    """Alerte email avec des champs manquants."""
    resp = client.post('/admin/alerts', json={
        'to_email': 'test@example.com',
    })
    assert resp.status_code == 422