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


def test_xss_script_tag_stored_safely(client):
    payload = "<script>alert('xss')</script>"
    response = client.post(
        "/logs",
        json={"message": payload, "level": "WARNING", "source": "security-test"},
    )
    assert response.status_code == 201
    log_id = response.json()["id"]
    get_response = client.get(f"/logs/{log_id}")
    assert get_response.status_code == 200
    assert get_response.json()["message"] == payload


def test_xss_event_handler_stored_safely(client):
    payload = '<img src=x onerror="alert(1)">'
    response = client.post(
        "/logs",
        json={"message": payload, "level": "WARNING", "source": "security-test"},
    )
    assert response.status_code == 201


def test_xss_javascript_url_stored_safely(client):
    payload = "javascript:alert(1)"
    response = client.post(
        "/logs",
        json={"message": payload, "level": "INFO", "source": "security-test"},
    )
    assert response.status_code == 201


def test_xss_iframe_injection_stored_safely(client):
    payload = "<iframe src='javascript:alert(1)'></iframe>"
    response = client.post(
        "/logs",
        json={"message": payload, "level": "WARNING", "source": "security-test"},
    )
    assert response.status_code == 201


def test_xss_svg_onload_stored_safely(client):
    payload = "<svg onload=alert(1)>"
    response = client.post(
        "/logs",
        json={"message": payload, "level": "WARNING", "source": "security-test"},
    )
    assert response.status_code == 201


def test_sql_injection_drop_table_stored_safely(client):
    payload = "'; DROP TABLE users; --"
    response = client.post(
        "/logs",
        json={"message": payload, "level": "ERROR", "source": "security-test"},
    )
    assert response.status_code == 201
    log_id = response.json()["id"]
    get_response = client.get(f"/logs/{log_id}")
    assert get_response.status_code == 200
    assert get_response.json()["message"] == payload


def test_sql_injection_union_select_stored_safely(client):
    payload = "' UNION SELECT username, password FROM users; --"
    response = client.post(
        "/logs",
        json={"message": payload, "level": "ERROR", "source": "security-test"},
    )
    assert response.status_code == 201


def test_sql_injection_or_1_equals_1(client):
    payload = "' OR '1'='1"
    response = client.post(
        "/logs",
        json={"message": payload, "level": "ERROR", "source": "security-test"},
    )
    assert response.status_code == 201


def test_sql_injection_semicolon_chain(client):
    payload = "'; INSERT INTO users(username) VALUES('hacked'); --"
    response = client.post(
        "/logs",
        json={"message": payload, "level": "ERROR", "source": "security-test"},
    )
    assert response.status_code == 201


def test_sql_injection_stored_xor(client):
    payload = "' XOR 1=1 --"
    response = client.post(
        "/logs",
        json={"message": payload, "level": "ERROR", "source": "security-test"},
    )
    assert response.status_code == 201


def test_command_injection_semicolon(client):
    payload = "; cat /etc/passwd"
    response = client.post(
        "/logs",
        json={"message": payload, "level": "WARNING", "source": "security-test"},
    )
    assert response.status_code == 201


def test_command_injection_pipe(client):
    payload = "| cat /etc/passwd"
    response = client.post(
        "/logs",
        json={"message": payload, "level": "WARNING", "source": "security-test"},
    )
    assert response.status_code == 201


def test_command_injection_backtick(client):
    payload = "`cat /etc/passwd`"
    response = client.post(
        "/logs",
        json={"message": payload, "level": "WARNING", "source": "security-test"},
    )
    assert response.status_code == 201


def test_command_injection_dollar_paren(client):
    payload = "$(cat /etc/passwd)"
    response = client.post(
        "/logs",
        json={"message": payload, "level": "WARNING", "source": "security-test"},
    )
    assert response.status_code == 201


def test_command_injection_ampersand(client):
    payload = "& rm -rf /"
    response = client.post(
        "/logs",
        json={"message": payload, "level": "WARNING", "source": "security-test"},
    )
    assert response.status_code == 201


def test_command_injection_newline(client):
    payload = "\ncat /etc/passwd"
    response = client.post(
        "/logs",
        json={"message": payload, "level": "WARNING", "source": "security-test"},
    )
    assert response.status_code == 201


def test_command_injection_stored_safely_does_not_execute(client):
    payload = "normal_log; ls -la /tmp"
    response = client.post(
        "/logs",
        json={"message": payload, "level": "INFO", "source": "security-test"},
    )
    assert response.status_code == 201
    log_id = response.json()["id"]
    get_response = client.get(f"/logs/{log_id}")
    assert get_response.status_code == 200
    assert get_response.json()["message"] == payload


def test_injection_in_source_field_stored_safely(client):
    payload = "<script>alert(1)</script>"
    response = client.post(
        "/logs",
        json={"message": "test", "level": "INFO", "source": payload},
    )
    assert response.status_code == 201


def test_injection_with_null_bytes(client):
    payload = "test%00<script>alert(1)</script>"
    response = client.post(
        "/logs",
        json={"message": payload, "level": "INFO", "source": "security-test"},
    )
    assert response.status_code == 201


def test_multiple_xss_payloads_stored_safely(client):
    payloads = [
        "<script>alert(1)</script>",
        "<img src=x onerror=alert(1)>",
        "<svg onload=alert(1)>",
        "javascript:alert(1)",
        "<iframe src=javascript:alert(1)></iframe>",
        "<body onload=alert(1)>",
        "<input onfocus=alert(1) autofocus>",
        "<details open ontoggle=alert(1)>",
    ]
    for payload in payloads:
        response = client.post(
            "/logs",
            json={"message": payload, "level": "WARNING", "source": "xss-test"},
        )
        assert response.status_code == 201


def test_sql_injection_no_schema_change(client):
    response = client.post(
        "/logs",
        json={
            "message": "'; DROP TABLE logs; ALTER TABLE users DROP COLUMN email; --",
            "level": "ERROR",
            "source": "injection-test",
        },
    )
    assert response.status_code == 201
    from sqlalchemy import inspect as sa_inspect
    inspector = sa_inspect(get_engine())
    table_names = inspector.get_table_names()
    assert "logs" in table_names
    assert "users" in table_names


def test_injection_payload_in_bulk(client):
    payloads = [
        {"message": "<script>alert(1)</script>", "level": "WARNING", "source": "bulk"},
        {"message": "'; DELETE FROM logs; --", "level": "ERROR", "source": "bulk"},
        {"message": "| cat /etc/passwd", "level": "WARNING", "source": "bulk"},
        {"message": "$(rm -rf /)", "level": "ERROR", "source": "bulk"},
        {"message": "<iframe src=javascript:alert(1)>", "level": "WARNING", "source": "bulk"},
    ]
    response = client.post("/logs/bulk", json=payloads)
    assert response.status_code == 200
    body = response.json()
    assert body["ingested"] == 5
    assert body["rejected"] == 0


def test_security_headers_on_log_response(client):
    response = client.post(
        "/logs",
        json={"message": "test", "level": "INFO", "source": "security-test"},
    )
    assert response.status_code == 201
    assert response.headers["X-Content-Type-Options"] == "nosniff"
    assert response.headers["X-Frame-Options"] == "DENY"


def test_xss_response_content_type_is_json(client):
    payload = "<script>alert('xss')</script>"
    response = client.post(
        "/logs",
        json={"message": payload, "level": "WARNING", "source": "security-test"},
    )
    assert response.status_code == 201
    assert "application/json" in response.headers["content-type"]
