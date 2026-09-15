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


def test_log_message_too_long(client):
    response = client.post(
        "/logs",
        json={"message": "A" * 5000, "level": "INFO"},
    )

    assert response.status_code == 422


def test_log_source_empty(client):
    response = client.post(
        "/logs",
        json={"message": "Test", "source": "  "},
    )

    assert response.status_code == 422


def test_limit_query_parameter_invalid(client):
    assert client.get("/logs?limit=0").status_code == 400
    assert client.get("/logs?limit=99999").status_code == 400


def test_invalid_json_payload(client):
    response = client.post("/logs", data="not json")

    assert response.status_code == 422


def test_missing_required_fields(client):
    response = client.post("/logs", json={"level": "INFO"})

    assert response.status_code == 422


@pytest.mark.parametrize("level", ["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"])
def test_valid_log_levels_are_accepted_and_normalized(client, level):
    response = client.post(
        "/logs",
        json={"message": "Validation log", "level": level.lower(), "source": "validation"},
    )

    assert response.status_code == 201
    assert response.json()["level"] == level


@pytest.mark.parametrize("level", ["TRACE", "NOTICE", "WARN", "", "info "])
def test_invalid_log_levels_are_rejected(client, level):
    response = client.post(
        "/logs",
        json={"message": "Validation log", "level": level, "source": "validation"},
    )

    assert response.status_code == 422


@pytest.mark.parametrize("source", ["api", "web-server", " service ", "capteur-01"])
def test_valid_sources_are_accepted_and_trimmed(client, source):
    response = client.post(
        "/logs",
        json={"message": "Validation log", "level": "INFO", "source": source},
    )

    assert response.status_code == 201
    assert response.json()["source"] == source.strip()


@pytest.mark.parametrize("source", ["", "   ", "\t\n"])
def test_empty_sources_are_rejected(client, source):
    response = client.post(
        "/logs",
        json={"message": "Validation log", "level": "INFO", "source": source},
    )

    assert response.status_code == 422


def test_source_longer_than_maximum_is_rejected(client):
    response = client.post(
        "/logs",
        json={"message": "Validation log", "level": "INFO", "source": "s" * 101},
    )

    assert response.status_code == 422


def test_log_level_query_filter_validates_values(client):
    invalid = client.get("/logs?level=TRACE")
    valid = client.get("/logs?level=error")

    assert invalid.status_code == 400
    assert valid.status_code == 200


def test_source_query_filter_accepts_trimmed_value(client):
    client.post(
        "/logs",
        json={"message": "Validation log", "level": "INFO", "source": " api "},
    )

    response = client.get("/logs?source=api")

    assert response.status_code == 200
    assert response.json()[0]["source"] == "api"
