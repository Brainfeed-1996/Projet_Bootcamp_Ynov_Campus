from unittest.mock import patch

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import insert

from app import Base, Log, app, get_engine
from providers.fake_provider import FakeLLMProvider


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


def _request_statuses(client, method, path, count, **kwargs):
    request = getattr(client, method)
    return [request(path, **kwargs).status_code for _ in range(count)]


def test_auth_rate_limit_is_ten_requests_per_minute(client):
    credentials = {"username": "rate-limit-user", "password": "wrong-password"}
    headers = {"X-Forwarded-For": "198.51.100.10"}

    statuses = _request_statuses(
        client,
        "post",
        "/auth/login",
        11,
        json=credentials,
        headers=headers,
    )

    assert all(status != 429 for status in statuses[:10])
    assert statuses[10] == 429


def test_log_write_rate_limit_is_fifty_requests_per_minute(client):
    headers = {"X-Forwarded-For": "198.51.100.11"}
    payload = {"message": "Rate limit log", "level": "INFO", "source": "rate-limit"}

    statuses = _request_statuses(
        client,
        "post",
        "/logs",
        51,
        json=payload,
        headers=headers,
    )

    assert all(status != 429 for status in statuses[:50])
    assert statuses[50] == 429


def test_analyze_rate_limit_is_thirty_requests_per_minute(client):
    with get_engine().begin() as connection:
        connection.execute(
            insert(Log),
            {"level": "ERROR", "message": "Rate limit analysis", "source": "rate-limit"},
        )
    log_id = client.get("/logs").json()[0]["id"]
    headers = {"X-Forwarded-For": "198.51.100.12"}

    with patch("app.get_llm_provider", return_value=FakeLLMProvider()):
        statuses = _request_statuses(
            client,
            "post",
            f"/logs/{log_id}/analyze",
            31,
            headers=headers,
        )

    assert all(status != 429 for status in statuses[:30])
    assert statuses[30] == 429


def test_rate_limit_response_includes_policy_headers(client):
    response = client.post(
        "/logs",
        json={"message": "Header check", "level": "INFO", "source": "rate-limit"},
        headers={"X-Forwarded-For": "198.51.100.13"},
    )

    assert response.status_code in {200, 201}
    assert response.headers.get("X-RateLimit-Limit") in {"50", "50/minute"}
