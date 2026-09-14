"""Tests pour les endpoints d'ingestion bulk et CSV."""
import pytest
from fastapi.testclient import TestClient
from app import app, get_engine, Base
import io


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


def test_bulk_ingest_success(client):
    """Test d'ingestion bulk réussie."""
    resp = client.post(
        "/logs/bulk",
        json=[
            {"message": "Bulk log 1", "level": "INFO", "source": "bulk"},
            {"message": "Bulk log 2", "level": "ERROR", "source": "bulk"},
        ],
    )
    assert resp.status_code == 200
    assert resp.json()["ingested"] == 2
    assert resp.json()["rejected"] == 0


def test_bulk_ingest_with_errors(client):
    """Test d'ingestion bulk avec des erreurs."""
    resp = client.post(
        "/logs/bulk",
        json=[
            {"message": "Valid log", "level": "INFO"},
            {"level": "INVALID"},  # Missing message
            {"message": "Bad level", "level": "UNKNOWN"},
        ],
    )
    assert resp.status_code == 200
    assert resp.json()["ingested"] == 1
    assert resp.json()["rejected"] == 2


def test_csv_ingest(client):
    """Test d'ingestion CSV."""
    csv_content = "message,level,source\nCSV log 1,INFO,csv\nCSV log 2,WARNING,csv"
    files = {"file": ("logs.csv", io.BytesIO(csv_content.encode()), "text/csv")}
    resp = client.post("/logs/ingest-csv", files=files)
    assert resp.status_code == 200
    assert resp.json()["ingested"] == 2


def test_csv_invalid_extension(client):
    """Test d'ingestion avec extension CSV invalide."""
    files = {"file": ("logs.txt", io.BytesIO(b"test"), "text/plain")}
    resp = client.post("/logs/ingest-csv", files=files)
    assert resp.status_code == 400


def test_bulk_too_many_items(client):
    """Test d'ingestion bulk avec trop d'éléments."""
    large_payload = [{"message": f"Log {i}"} for i in range(10001)]
    resp = client.post("/logs/bulk", json=large_payload)
    assert resp.status_code == 400