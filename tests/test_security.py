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


def test_sql_injection_is_stored_as_data(client):
    message = "'; DROP TABLE users; --"
    response = client.post(
        "/logs",
        json={"message": message, "level": "INFO", "source": "security-test"},
    )

    assert response.status_code == 201
    assert response.json()["message"] == message
    assert client.get("/logs").status_code == 200


def test_xss_payload_is_serialized_as_json(client):
    message = "<script>alert('xss')</script>"
    response = client.post(
        "/logs",
        json={"message": message, "level": "WARNING", "source": "security-test"},
    )

    assert response.status_code == 201
    assert response.headers["content-type"].startswith("application/json")
    assert response.json()["message"] == message


def test_command_injection_is_not_executed(client):
    message = "value'; touch /tmp/log-sentinel-injected; #"
    response = client.post(
        "/logs",
        json={"message": message, "level": "ERROR", "source": "security-test"},
    )

    assert response.status_code == 201
    assert response.json()["message"] == message


def test_security_headers_are_present(client):
    response = client.get("/health")

    assert response.status_code == 200
    assert response.headers["X-Content-Type-Options"] == "nosniff"
    assert response.headers["X-Frame-Options"] == "DENY"
    assert response.headers["X-XSS-Protection"] == "1; mode=block"


def test_request_size_limit_is_enforced(client):
    message = "A" * (11 * 1024 * 1024)
    response = client.post("/logs", json={"message": message, "level": "INFO"})

    assert response.status_code == 413


def test_csrf_middleware_allows_api_json_requests(client):
    response = client.post(
        "/logs",
        json={"message": "API request", "level": "INFO", "source": "security-test"},
    )

    assert response.status_code == 201
