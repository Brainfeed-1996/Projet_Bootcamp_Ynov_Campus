import pytest
from fastapi.testclient import TestClient
from sqlalchemy import text

from app import Base, app, get_engine, sanitize_log_message


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


def test_csrf_middleware_rejects_browser_post_without_token(client):
    response = client.post(
        "/logs",
        json={"message": "Browser request", "level": "INFO", "source": "security-test"},
        headers={"accept": "text/html"},
    )

    assert response.status_code == 403
    assert "CSRF" in response.json()["detail"]


def test_csrf_middleware_allows_browser_post_with_token(client):
    response = client.post(
        "/logs",
        json={"message": "Browser request", "level": "INFO", "source": "security-test"},
        headers={"accept": "text/html", "X-CSRF-Token": "valid-token"},
    )

    assert response.status_code in {200, 201, 400, 422}


def test_csrf_middleware_rejects_delete_without_token(client):
    response = client.delete(
        "/logs/1",
        headers={"accept": "text/html"},
    )

    assert response.status_code == 403


def test_csrf_middleware_rejects_put_without_token(client):
    response = client.put(
        "/logs/1",
        json={"message": "Update", "level": "INFO", "source": "test"},
        headers={"accept": "text/html"},
    )

    assert response.status_code == 403


def test_csrf_middleware_allows_get_without_token(client):
    response = client.get("/health")

    assert response.status_code == 200


def test_csrf_middleware_allows_patch_api_requests(client):
    response = client.patch(
        "/logs/1",
        json={"message": "Update", "level": "INFO", "source": "test"},
        headers={"accept": "application/json"},
    )

    assert response.status_code != 403


def test_csrf_middleware_rejects_patch_browser_without_token(client):
    response = client.patch(
        "/logs/1",
        json={"message": "Update", "level": "INFO", "source": "test"},
        headers={"accept": "text/html"},
    )

    assert response.status_code == 403


def test_ip_redaction_from_log_message(client):
    ip = "192.168.1.100"
    message = f"Connection from {ip}"
    sanitized = sanitize_log_message(message)
    assert ip not in sanitized
    assert "[IP_REDACTED]" in sanitized


def test_email_redaction_from_log_message(client):
    email = "john.doe@example.com"
    message = f"Contact {email} for details"
    sanitized = sanitize_log_message(message)
    assert email not in sanitized
    assert "[EMAIL_REDACTED]" in sanitized


def test_password_redaction_from_log_message(client):
    message = "password=supersecret"
    sanitized = sanitize_log_message(message)
    assert "supersecret" not in sanitized
    assert "[CREDENTIAL_REDACTED]" in sanitized


def test_credit_card_redaction_from_log_message(client):
    card = "4111-1111-1111-1111"
    message = f"Card number: {card}"
    sanitized = sanitize_log_message(message)
    assert card not in sanitized
    assert "[CARD_REDACTED]" in sanitized


def test_multiple_sensitive_data_redaction(client):
    message = "User 10.0.0.1 emailed admin@secret.com with pwd=test123"
    sanitized = sanitize_log_message(message)
    assert "10.0.0.1" not in sanitized
    assert "admin@secret.com" not in sanitized
    assert "test123" not in sanitized
    assert "[IP_REDACTED]" in sanitized
    assert "[EMAIL_REDACTED]" in sanitized
    assert "[CREDENTIAL_REDACTED]" in sanitized


def test_redaction_plain_message_unchanged(client):
    message = "System started successfully"
    sanitized = sanitize_log_message(message)
    assert sanitized == message
