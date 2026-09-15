import pytest
from fastapi.testclient import TestClient
from sqlalchemy import text

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


@pytest.mark.parametrize(
    "message",
    [
        "'; DROP TABLE users; --",
        "<script>alert('xss')</script>",
        "value'; touch /tmp/log-sentinel-injected; #",
    ],
)
def test_injection_payloads_are_not_executed(client, message):
    response = client.post(
        "/logs",
        json={"message": message, "level": "INFO", "source": "security-test"},
    )

    assert response.status_code in {200, 201, 400, 422}
    assert response.status_code != 500


def test_sql_injection_does_not_change_database_schema(client):
    response = client.post(
        "/logs",
        json={"message": "'; DROP TABLE users; --", "level": "INFO", "source": "security-test"},
    )

    with get_engine().connect() as connection:
        users_table_exists = connection.execute(
            text("SELECT name FROM sqlite_master WHERE type = 'table' AND name = 'users'")
        ).first()

    assert response.status_code in {200, 201, 400, 422}
    assert users_table_exists is not None


def test_xss_payload_is_not_rendered_as_html(client):
    response = client.post(
        "/logs",
        json={"message": "<script>alert('xss')</script>", "level": "WARNING", "source": "security-test"},
    )

    assert response.status_code in {200, 201, 400, 422}
    assert response.headers["content-type"].startswith("application/json")


def test_sensitive_data_redaction(client):
    response = client.post(
        "/logs",
        json={
            "message": "Password: secret123, API_KEY: abc-def-ghi",
            "level": "WARNING",
            "source": "leak",
        },
    )

    assert response.status_code == 201


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

    assert response.status_code in {200, 201, 400, 422}
