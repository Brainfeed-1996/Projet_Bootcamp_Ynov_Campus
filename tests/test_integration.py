import json
from unittest.mock import patch

import pytest
from fastapi.testclient import TestClient

from app import Base, app, get_engine
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


def test_full_workflow_create_user_log_analyze_and_get_analyses(client):
    user_response = client.post(
        "/users",
        json={
            "username": "workflow-user",
            "email": "workflow@example.com",
            "password": "WorkflowPassword123",
        },
    )

    assert user_response.status_code == 201
    user_id = user_response.json()["id"]
    assert user_id > 0

    message = "Suspicious activity detected in the authentication service"
    log_response = client.post(
        "/logs",
        json={"message": message, "level": "ERROR", "source": "auth-service"},
    )

    assert log_response.status_code == 201
    log_id = log_response.json()["id"]
    assert log_response.json()["message"] == message

    with patch("app.get_llm_provider", return_value=FakeLLMProvider()):
        analysis_response = client.post(f"/logs/{log_id}/analyze")

    assert analysis_response.status_code == 201
    analysis = analysis_response.json()
    assert analysis["log_id"] == log_id
    assert analysis["result"]["provider"] == "fake"

    analyses_response = client.get("/analyses")

    assert analyses_response.status_code == 200
    analyses = analyses_response.json()
    assert len(analyses) == 1
    assert analyses[0]["input_data"] == message
    assert json.loads(analyses[0]["result"])["severity"] == "LOW"


def test_error_handling_consistency(client):
    validation_response = client.post("/logs", json={})
    not_found_response = client.get("/logs/99999")
    logs_response = client.get("/logs")

    assert validation_response.status_code == 422
    assert "detail" in validation_response.json()
    assert not_found_response.status_code == 404
    assert "detail" in not_found_response.json()
    assert logs_response.status_code == 200


def test_database_transaction_commits_visible_log(client):
    initial_count = len(client.get("/logs").json())
    response = client.post(
        "/logs",
        json={"message": "Committed log", "level": "INFO", "source": "integration"},
    )

    assert response.status_code == 201
    assert len(client.get("/logs").json()) == initial_count + 1
