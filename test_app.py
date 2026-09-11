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
