"""Tests de performance et de charge."""
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


def test_bulk_ingest_performance(client):
    """Test de performance pour l'ingestion bulk."""
    payload = [{"message": f"Perf log {i}", "level": "INFO"} for i in range(100)]
    start = time.time()
    resp = client.post("/logs/bulk", json=payload)
    elapsed = time.time() - start
    assert resp.status_code == 200
    assert resp.json()["ingested"] == 100
    # Devrait prendre moins de 5 secondes
    assert elapsed < 5.0


def test_health_response_time(client):
    """Test que l'endpoint health répond rapidement."""
    start = time.time()
    resp = client.get("/health")
    elapsed = time.time() - start
    assert resp.status_code == 200
    assert elapsed < 1.0


def test_concurrent_log_creation(client):
    """Test de création de logs multiples."""
    responses = []
    for i in range(50):
        resp = client.post(
            "/logs",
            json={"message": f"Concurrent log {i}", "level": "INFO"},
        )
        responses.append(resp.status_code)
    assert all(code == 201 for code in responses)
def test_concurrent_requests(client):
    import threading
    results = []
    def make_request():
        resp = client.get('/health')
        results.append(resp.status_code)
    threads = [threading.Thread(target=make_request) for _ in range(10)]
    for t in threads:
        t.start()
    for t in threads:
        t.join()
    assert all(code == 200 for code in results)
