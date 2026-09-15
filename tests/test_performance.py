import io
import time

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


def test_bulk_ingest_1000_logs_performance(client):
    payload = [
        {"message": f"Performance log {index}", "level": "INFO", "source": "performance"}
        for index in range(1000)
    ]

    started = time.perf_counter()
    response = client.post("/logs/bulk", json=payload)
    elapsed = time.perf_counter() - started

    assert response.status_code == 200
    assert response.json()["ingested"] == 1000
    assert elapsed < 5.0


def test_csv_ingest_1000_rows_performance(client):
    rows = ["message,level,source"]
    rows.extend(
        f"Performance CSV {index},WARNING,performance"
        for index in range(1000)
    )
    content = "\n".join(rows).encode()
    files = {"file": ("performance.csv", io.BytesIO(content), "text/csv")}

    started = time.perf_counter()
    response = client.post("/logs/ingest-csv", files=files)
    elapsed = time.perf_counter() - started

    assert response.status_code == 200
    assert response.json()["ingested"] == 1000
    assert elapsed < 5.0


def test_bulk_ingest_ten_thousand_logs_is_bounded(client):
    payload = [
        {"message": f"Bounded log {index}", "level": "DEBUG", "source": "performance"}
        for index in range(10000)
    ]

    started = time.perf_counter()
    response = client.post("/logs/bulk", json=payload)
    elapsed = time.perf_counter() - started

    assert response.status_code == 200
    assert response.json()["ingested"] == 10000
    assert elapsed < 10.0


def test_health_response_time(client):
    started = time.perf_counter()
    response = client.get("/health")
    elapsed = time.perf_counter() - started

    assert response.status_code == 200
    assert elapsed < 1.0


def test_concurrent_log_creation(client):
    responses = [
        client.post(
            "/logs",
            json={"message": f"Concurrent log {index}", "level": "INFO", "source": "performance"},
        ).status_code
        for index in range(50)
    ]

    assert all(status_code == 201 for status_code in responses)
