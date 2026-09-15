import io

import pytest
from fastapi.testclient import TestClient

from app import Base, app, get_engine


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
    response = client.post(
        "/logs/bulk",
        json=[
            {"message": "Bulk log 1", "level": "INFO", "source": "bulk"},
            {"message": "Bulk log 2", "level": "ERROR", "source": "bulk"},
        ],
    )

    assert response.status_code == 200
    assert response.json()["ingested"] == 2
    assert response.json()["rejected"] == 0


def test_bulk_ingest_with_errors(client):
    response = client.post(
        "/logs/bulk",
        json=[
            {"message": "Valid log", "level": "INFO"},
            {"level": "INVALID"},
            {"message": "Bad level", "level": "UNKNOWN"},
        ],
    )

    assert response.status_code == 200
    assert response.json()["ingested"] == 1
    assert response.json()["rejected"] == 2


def test_csv_ingest(client):
    csv_content = "message,level,source\nCSV log 1,INFO,csv\nCSV log 2,WARNING,csv"
    files = {"file": ("logs.csv", io.BytesIO(csv_content.encode()), "text/csv")}
    response = client.post("/logs/ingest-csv", files=files)

    assert response.status_code == 200
    assert response.json()["ingested"] == 2


def test_csv_invalid_extension(client):
    files = {"file": ("logs.txt", io.BytesIO(b"test"), "text/plain")}
    response = client.post("/logs/ingest-csv", files=files)

    assert response.status_code == 400


def test_bulk_ingest_empty_payload(client):
    response = client.post("/logs/bulk", json=[])

    assert response.status_code == 200
    assert response.json() == {"ingested": 0, "rejected": 0, "errors": []}


def test_bulk_ingest_rejects_too_many_items(client):
    payload = [{"message": f"Log {index}"} for index in range(10001)]

    response = client.post("/logs/bulk", json=payload)

    assert response.status_code == 400
    assert "10000" in response.json()["detail"]


def test_bulk_ingest_rejects_invalid_json(client):
    response = client.post(
        "/logs/bulk",
        content="{invalid json",
        headers={"content-type": "application/json"},
    )

    assert response.status_code == 400
    assert "JSON invalide" in response.json()["detail"]


def test_bulk_ingest_requires_a_json_array(client):
    response = client.post("/logs/bulk", json={"message": "not an array"})

    assert response.status_code == 400
    assert "tableau JSON" in response.json()["detail"]


def test_csv_ingest_rejects_a_malformed_header(client):
    content = "level,source\nINFO,api\n"
    files = {"file": ("malformed.csv", io.BytesIO(content.encode()), "text/csv")}

    response = client.post("/logs/ingest-csv", files=files)

    assert response.status_code == 422
    assert "message" in response.json()["detail"]


def test_csv_ingest_rejects_invalid_utf8(client):
    files = {"file": ("invalid.csv", io.BytesIO(b"\xff\xfe"), "text/csv")}

    response = client.post("/logs/ingest-csv", files=files)

    assert response.status_code == 400
    assert "UTF-8" in response.json()["detail"]


def test_csv_ingest_rejects_rows_without_a_message(client):
    content = "message,level,source\n,INFO,api\nvalid,WARNING,api\n"
    files = {"file": ("missing-message.csv", io.BytesIO(content.encode()), "text/csv")}

    response = client.post("/logs/ingest-csv", files=files)

    assert response.status_code == 200
    body = response.json()
    assert body["ingested"] == 1
    assert body["rejected"] == 1
