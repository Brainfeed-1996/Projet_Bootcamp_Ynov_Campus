from unittest.mock import patch

from fastapi.testclient import TestClient

from app import Base, app, engine
from providers.fake_provider import FakeLLMProvider

client = TestClient(app)


def reset_db():
    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)


def test_health():
    reset_db()
    resp = client.get("/health")
    assert resp.status_code == 200
    assert resp.json() == {"status": "ok", "database": "up"}


def test_create_user_and_duplicate():
    reset_db()
    resp = client.post(
        "/users",
        json={"username": "alice", "email": "alice@example.com", "password": "SuperSecret1"},
    )
    assert resp.status_code == 201
    body = resp.json()
    assert body["username"] == "alice"

    dup = client.post(
        "/users",
        json={"username": "alice", "email": "other@example.com", "password": "SuperSecret2"},
    )
    assert dup.status_code == 409


def test_create_user_validation():
    reset_db()
    resp = client.post(
        "/users",
        json={"username": "ab", "email": "bad", "password": "short"},
    )
    assert resp.status_code == 422


def test_get_user_invalid_id():
    reset_db()
    assert client.get("/users/0").status_code == 400
    assert client.get("/users/-1").status_code == 400


def test_delete_user():
    reset_db()
    resp = client.post(
        "/users",
        json={"username": "bob", "email": "bob@example.com", "password": "SuperSecret1"},
    )
    uid = resp.json()["id"]
    del_resp = client.delete(f"/users/{uid}")
    assert del_resp.status_code == 200
    assert client.get(f"/users/{uid}").status_code == 404


def test_create_and_get_log():
    reset_db()
    resp = client.post("/logs", json={"message": "Connexion acceptée", "level": "INFO", "source": "api"})
    assert resp.status_code == 201
    log_id = resp.json()["id"]
    got = client.get(f"/logs/{log_id}")
    assert got.status_code == 200
    assert got.json()["message"] == "Connexion acceptée"


def test_log_invalid_level():
    reset_db()
    resp = client.post("/logs", json={"message": "x", "level": "BOGUS"})
    assert resp.status_code == 422


def test_analyze_log_success():
    reset_db()
    resp = client.post("/logs", json={"message": "Connection timeout", "level": "ERROR", "source": "test"})
    log_id = resp.json()["id"]
    with patch("app.get_llm_provider") as mock_provider:
        mock_provider.return_value = FakeLLMProvider()
        analyze = client.post(f"/logs/{log_id}/analyze")
        assert analyze.status_code == 201
        data = analyze.json()
        assert data["log_id"] == log_id
        result = data["result"]
        assert result["severity"] == "LOW"
        assert "recommendations" in result
        assert isinstance(result["recommendations"], list)


def test_analyze_log_not_found():
    reset_db()
    with patch("app.get_llm_provider") as mock_provider:
        mock_provider.return_value = FakeLLMProvider()
        resp = client.post("/logs/99999/analyze")
        assert resp.status_code == 404


def test_analyze_log_provider_failure():
    reset_db()
    resp = client.post("/logs", json={"message": "Connection timeout", "level": "ERROR", "source": "test"})
    log_id = resp.json()["id"]

    class FailingProvider:
        def analyze(self, log_message):
            raise RuntimeError("AI service unavailable")

    with patch("app.get_llm_provider") as mock_provider:
        mock_provider.return_value = FailingProvider()
        resp = client.post(f"/logs/{log_id}/analyze")
        assert resp.status_code == 502


def test_analyze_log_invalid_ai_response():
    reset_db()
    resp = client.post("/logs", json={"message": "Connection timeout", "level": "ERROR", "source": "test"})
    log_id = resp.json()["id"]

    class InvalidResponseProvider:
        def analyze(self, log_message):
            raise ValueError("Invalid JSON from LLM")

    with patch("app.get_llm_provider") as mock_provider:
        mock_provider.return_value = InvalidResponseProvider()
        resp = client.post(f"/logs/{log_id}/analyze")
        assert resp.status_code == 502


def test_ingest_json_bulk_with_errors():
    reset_db()
    payload = [
        {"message": "ok", "level": "ERROR", "source": "api"},
        {"message": "", "level": "ERROR"},
        {"message": "bad", "level": "BOGUS"},
    ]
    resp = client.post("/logs/bulk", json=payload)
    assert resp.status_code == 200
    body = resp.json()
    assert body["ingested"] == 1
    assert body["rejected"] == 2
    assert len(body["errors"]) == 2
    assert client.get("/logs").status_code == 200


def test_ingest_csv():
    reset_db()
    csv_content = (
        "level,message,source\n"
        "ERROR,Connection refused,api\n"
        "INFO,Startup complete,system\n"
        "FATAL,bad level,api\n"
        "INFO,,system\n"
    )
    resp = client.post(
        "/logs/ingest-csv",
        files={"file": ("sample.csv", csv_content, "text/csv")},
    )
    assert resp.status_code == 200
    body = resp.json()
    assert body["ingested"] == 2
    assert body["rejected"] == 2


def test_ingest_csv_missing_required_column():
    reset_db()
    csv_content = "level,source\nERROR,api\n"
    resp = client.post(
        "/logs/ingest-csv",
        files={"file": ("sample.csv", csv_content, "text/csv")},
    )
    assert resp.status_code == 422


def test_ingest_csv_not_csv_extension():
    reset_db()
    resp = client.post(
        "/logs/ingest-csv",
        files={"file": ("data.txt", b"hello", "text/plain")},
    )
    assert resp.status_code == 400


def test_get_analyses_empty():
    reset_db()
    resp = client.get("/analyses")
    assert resp.status_code == 200
    assert resp.json() == []


# =============================================================================
# GET /users - valid & invalid cases
# =============================================================================


def test_get_user_valid():
    reset_db()
    resp = client.post(
        "/users",
        json={"username": "charlie", "email": "charlie@example.com", "password": "Passw0rd!1"},
    )
    uid = resp.json()["id"]
    got = client.get(f"/users/{uid}")
    assert got.status_code == 200
    assert got.json()["username"] == "charlie"
    assert got.json()["email"] == "charlie@example.com"
    assert got.json()["is_active"] is True


def test_get_user_not_found():
    reset_db()
    resp = client.get("/users/99999")
    assert resp.status_code == 404


def test_get_user_after_deletion():
    reset_db()
    resp = client.post(
        "/users",
        json={"username": "diana", "email": "diana@example.com", "password": "Passw0rd!1"},
    )
    uid = resp.json()["id"]
    client.delete(f"/users/{uid}")
    resp = client.get(f"/users/{uid}")
    assert resp.status_code == 404


def test_delete_user_not_found():
    reset_db()
    resp = client.delete("/users/99999")
    assert resp.status_code == 404


def test_delete_user_invalid_id():
    reset_db()
    assert client.delete("/users/0").status_code == 400
    assert client.delete("/users/-5").status_code == 400


# =============================================================================
# POST /users - more validation cases
# =============================================================================


def test_create_user_username_too_long():
    reset_db()
    resp = client.post(
        "/users",
        json={"username": "a" * 51, "email": "long@example.com", "password": "Passw0rd!1"},
    )
    assert resp.status_code == 422


def test_create_user_username_exact_min():
    reset_db()
    resp = client.post(
        "/users",
        json={"username": "abc", "email": "min@example.com", "password": "Passw0rd!1"},
    )
    assert resp.status_code == 201
    assert resp.json()["username"] == "abc"


def test_create_user_email_invalid_format():
    reset_db()
    resp = client.post(
        "/users",
        json={"username": "validuser", "email": "notanemail", "password": "Passw0rd!1"},
    )
    assert resp.status_code == 422


def test_create_user_password_too_short_7_chars():
    reset_db()
    resp = client.post(
        "/users",
        json={"username": "user7char", "email": "user7@example.com", "password": "7char!"},
    )
    assert resp.status_code == 422


def test_create_user_password_exact_min_8_chars():
    reset_db()
    resp = client.post(
        "/users",
        json={"username": "user8char", "email": "user8@example.com", "password": "Pass8xxx"},
    )
    assert resp.status_code == 201


def test_create_user_missing_fields():
    reset_db()
    resp = client.post("/users", json={"username": "incomplete"})
    assert resp.status_code == 422


def test_create_user_empty_username():
    reset_db()
    resp = client.post("/users", json={"username": "", "email": "empty@user.com", "password": "Passw0rd!1"})
    assert resp.status_code == 422


# =============================================================================
# GET /logs - filters, limits, and error cases
# =============================================================================


def test_get_logs_empty():
    reset_db()
    resp = client.get("/logs")
    assert resp.status_code == 200
    assert resp.json() == []


def test_get_logs_with_level_filter():
    reset_db()
    client.post("/logs", json={"message": "Error 1", "level": "ERROR", "source": "api"})
    client.post("/logs", json={"message": "Info 1", "level": "INFO", "source": "api"})
    client.post("/logs", json={"message": "Error 2", "level": "ERROR", "source": "db"})
    resp = client.get("/logs?level=ERROR")
    assert resp.status_code == 200
    logs = resp.json()
    assert len(logs) == 2
    assert all(log_entry["level"] == "ERROR" for log_entry in logs)


def test_get_logs_with_source_filter():
    reset_db()
    client.post("/logs", json={"message": "Log A", "level": "INFO", "source": "api"})
    client.post("/logs", json={"message": "Log B", "level": "INFO", "source": "db"})
    resp = client.get("/logs?source=api")
    assert resp.status_code == 200
    logs = resp.json()
    assert len(logs) == 1
    assert logs[0]["source"] == "api"


def test_get_logs_level_and_source_filter():
    reset_db()
    client.post("/logs", json={"message": "A", "level": "ERROR", "source": "api"})
    client.post("/logs", json={"message": "B", "level": "ERROR", "source": "db"})
    client.post("/logs", json={"message": "C", "level": "INFO", "source": "api"})
    resp = client.get("/logs?level=ERROR&source=api")
    assert resp.status_code == 200
    logs = resp.json()
    assert len(logs) == 1
    assert logs[0]["level"] == "ERROR"
    assert logs[0]["source"] == "api"


def test_get_logs_invalid_level_filter():
    reset_db()
    resp = client.get("/logs?level=BOGUS")
    assert resp.status_code == 400


def test_get_logs_invalid_limit_zero():
    reset_db()
    resp = client.get("/logs?limit=0")
    assert resp.status_code == 400


def test_get_logs_invalid_limit_over_max():
    reset_db()
    resp = client.get("/logs?limit=1001")
    assert resp.status_code == 400


def test_get_logs_valid_limit():
    reset_db()
    for i in range(5):
        client.post("/logs", json={"message": f"Log {i}", "level": "INFO", "source": "test"})
    resp = client.get("/logs?limit=3")
    assert resp.status_code == 200
    assert len(resp.json()) == 3


# =============================================================================
# GET /logs/{log_id} - valid and invalid cases
# =============================================================================


def test_get_log_valid():
    reset_db()
    resp = client.post("/logs", json={"message": "Specific log", "level": "WARNING", "source": "test"})
    log_id = resp.json()["id"]
    got = client.get(f"/logs/{log_id}")
    assert got.status_code == 200
    assert got.json()["message"] == "Specific log"
    assert got.json()["level"] == "WARNING"
    assert got.json()["source"] == "test"


def test_get_log_not_found():
    reset_db()
    resp = client.get("/logs/99999")
    assert resp.status_code == 404


def test_get_log_invalid_id():
    reset_db()
    assert client.get("/logs/0").status_code == 400
    assert client.get("/logs/-1").status_code == 400


# =============================================================================
# POST /logs - more validation cases
# =============================================================================


def test_create_log_minimal():
    reset_db()
    resp = client.post("/logs", json={"message": "Minimal log"})
    assert resp.status_code == 201
    body = resp.json()
    assert body["message"] == "Minimal log"
    assert body["level"] == "INFO"
    assert body["source"] == "unknown"


def test_create_log_missing_message():
    reset_db()
    resp = client.post("/logs", json={"level": "INFO", "source": "test"})
    assert resp.status_code == 422


def test_create_log_empty_message():
    reset_db()
    resp = client.post("/logs", json={"message": "", "level": "INFO", "source": "test"})
    assert resp.status_code == 422


def test_create_log_source_spaces_only():
    reset_db()
    resp = client.post("/logs", json={"message": "test", "level": "INFO", "source": "   "})
    assert resp.status_code == 422


def test_create_log_message_too_long():
    reset_db()
    resp = client.post("/logs", json={"message": "x" * 4097, "level": "INFO", "source": "test"})
    assert resp.status_code == 422


# =============================================================================
# POST /logs/{log_id}/analyze - error cases
# =============================================================================


def test_analyze_log_invalid_id_zero():
    reset_db()
    with patch("app.get_llm_provider") as mock_provider:
        mock_provider.return_value = FakeLLMProvider()
        resp = client.post("/logs/0/analyze")
        assert resp.status_code == 400


def test_analyze_log_invalid_id_negative():
    reset_db()
    with patch("app.get_llm_provider") as mock_provider:
        mock_provider.return_value = FakeLLMProvider()
        resp = client.post("/logs/-1/analyze")
        assert resp.status_code == 400


# =============================================================================
# POST /analyses - valid and invalid cases
# =============================================================================


def test_create_analyse_valid():
    reset_db()
    resp = client.post(
        "/analyses",
        json={"type": "log_analysis", "input_data": "test message", "result": "test result"},
    )
    assert resp.status_code == 201
    body = resp.json()
    assert body["type"] == "log_analysis"
    assert body["input_data"] == "test message"
    assert body["result"] == "test result"
    assert "id" in body
    assert "created_at" in body


def test_create_analyse_missing_type():
    reset_db()
    resp = client.post("/analyses", json={"input_data": "test"})
    assert resp.status_code == 400


def test_create_analyse_empty_type_ignored():
    reset_db()
    resp = client.post("/analyses", json={"type": "", "input_data": "test"})
    assert resp.status_code == 201


# =============================================================================
# GET /analyses - limits and data
# =============================================================================


def test_get_analyses_with_data():
    reset_db()
    client.post("/analyses", json={"type": "log_analysis", "input_data": "msg1", "result": "res1"})
    client.post("/analyses", json={"type": "log_analysis", "input_data": "msg2", "result": "res2"})
    resp = client.get("/analyses")
    assert resp.status_code == 200
    assert len(resp.json()) == 2


def test_get_analyses_invalid_limit_zero():
    reset_db()
    resp = client.get("/analyses?limit=0")
    assert resp.status_code == 400


def test_get_analyses_invalid_limit_over_max():
    reset_db()
    resp = client.get("/analyses?limit=1001")
    assert resp.status_code == 400


def test_get_analyses_limit_one():
    reset_db()
    client.post("/analyses", json={"type": "t1", "input_data": "m1", "result": "r1"})
    client.post("/analyses", json={"type": "t2", "input_data": "m2", "result": "r2"})
    resp = client.get("/analyses?limit=1")
    assert resp.status_code == 200
    assert len(resp.json()) == 1


# =============================================================================
# POST /logs/bulk - more cases
# =============================================================================


def test_ingest_json_bulk_empty():
    reset_db()
    resp = client.post("/logs/bulk", json=[])
    assert resp.status_code == 200
    body = resp.json()
    assert body["ingested"] == 0
    assert body["rejected"] == 0
    assert body["errors"] == []


def test_ingest_json_bulk_all_valid():
    reset_db()
    payload = [
        {"message": "Log 1", "level": "ERROR", "source": "api"},
        {"message": "Log 2", "level": "WARNING", "source": "db"},
        {"message": "Log 3", "level": "INFO", "source": "system"},
    ]
    resp = client.post("/logs/bulk", json=payload)
    assert resp.status_code == 200
    body = resp.json()
    assert body["ingested"] == 3
    assert body["rejected"] == 0
    assert body["errors"] == []
    logs = client.get("/logs").json()
    assert len(logs) == 3


def test_ingest_json_bulk_not_array():
    reset_db()
    resp = client.post("/logs/bulk", json={"message": "not an array"})
    assert resp.status_code == 400


def test_ingest_json_bulk_non_object_entries():
    reset_db()
    payload = [
        {"message": "valid", "level": "INFO", "source": "test"},
        "not an object",
        42,
        None,
    ]
    resp = client.post("/logs/bulk", json=payload)
    assert resp.status_code == 200
    body = resp.json()
    assert body["ingested"] == 1
    assert body["rejected"] == 3


def test_ingest_json_bulk_message_too_long():
    reset_db()
    payload = [{"message": "x" * 4097, "level": "INFO", "source": "test"}]
    resp = client.post("/logs/bulk", json=payload)
    assert resp.status_code == 200
    body = resp.json()
    assert body["ingested"] == 0
    assert body["rejected"] == 1


def test_ingest_csv_all_valid():
    reset_db()
    csv_content = (
        "level,message,source\n"
        "ERROR,Connection refused,api\n"
        "INFO,Startup complete,system\n"
    )
    resp = client.post(
        "/logs/ingest-csv",
        files={"file": ("all_valid.csv", csv_content, "text/csv")},
    )
    assert resp.status_code == 200
    body = resp.json()
    assert body["ingested"] == 2
    assert body["rejected"] == 0


def test_ingest_csv_utf8_error():
    reset_db()
    resp = client.post(
        "/logs/ingest-csv",
        files={"file": ("bad.csv", b"\xff\xfe\x00\x00", "text/csv")},
    )
    assert resp.status_code == 400


def test_ingest_csv_empty_message_field():
    reset_db()
    csv_content = "level,message,source\nINFO,,api\n"
    resp = client.post(
        "/logs/ingest-csv",
        files={"file": ("empty_msg.csv", csv_content, "text/csv")},
    )
    assert resp.status_code == 200
    body = resp.json()
    assert body["ingested"] == 0
    assert body["rejected"] == 1


def test_ingest_csv_no_colon_in_header():
    reset_db()
    csv_content = "message\nhello\n"
    resp = client.post(
        "/logs/ingest-csv",
        files={"file": ("only_message.csv", csv_content, "text/csv")},
    )
    assert resp.status_code == 200
    body = resp.json()
    assert body["ingested"] == 1
    assert body["rejected"] == 0


# =============================================================================
# General error handling coverage
# =============================================================================


def test_get_unknown_endpoint():
    reset_db()
    resp = client.get("/nonexistent-endpoint")
    assert resp.status_code == 404


def test_get_logs_with_invalid_level_and_limit():
    reset_db()
    resp = client.get("/logs?level=INVALID&limit=0")
    assert resp.status_code == 400
