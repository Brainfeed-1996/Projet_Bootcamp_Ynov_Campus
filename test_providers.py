import pytest

from app import Base, engine
from providers.base import (
    ALLOWED_SEVERITIES,
    ANALYSIS_FIELDS,
    LLMProvider,
    ProviderConfigurationError,
    ProviderError,
    ProviderInputError,
    ProviderResponseError,
    validate_log_message,
)
from providers.fake_provider import FakeLLMProvider


@pytest.fixture(autouse=True)
def reset_db():
    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)
    yield
    Base.metadata.drop_all(bind=engine)


# =============================================================================
# FakeLLMProvider - determinism and behavior
# =============================================================================


def test_fake_provider_returns_low_severity():
    provider = FakeLLMProvider()
    result = provider.analyze("Test log message")
    assert result.severity == "LOW"


def test_fake_provider_returns_test_category():
    provider = FakeLLMProvider()
    result = provider.analyze("Another message")
    assert result.category == "TEST"


def test_fake_provider_has_summary():
    provider = FakeLLMProvider()
    result = provider.analyze("Some log entry")
    assert isinstance(result.summary, str)
    assert len(result.summary) > 0


def test_fake_provider_has_recommendations():
    provider = FakeLLMProvider()
    result = provider.analyze("Log data")
    assert isinstance(result.recommendations, list)
    assert len(result.recommendations) > 0
    assert all(isinstance(r, str) for r in result.recommendations)


def test_fake_provider_deterministic():
    provider = FakeLLMProvider()
    result1 = provider.analyze("Identical message")
    result2 = provider.analyze("Identical message")
    assert result1.severity == result2.severity
    assert result1.category == result2.category
    assert result1.summary == result2.summary
    assert result1.recommendations == result2.recommendations


def test_fake_provider_different_inputs():
    provider = FakeLLMProvider()
    result1 = provider.analyze("First different message")
    result2 = provider.analyze("Second different message")
    assert result1.severity == "LOW"
    assert result2.severity == "LOW"


def test_fake_provider_analyze_called_multiple_times():
    provider = FakeLLMProvider()
    messages = [f"Message {i}" for i in range(10)]
    results = [provider.analyze(msg) for msg in messages]
    assert len(results) == 10
    assert all(r.severity == "LOW" for r in results)
    assert all(r.category == "TEST" for r in results)


def test_fake_provider_returns_valid_analysis_result():
    provider = FakeLLMProvider()
    result = provider.analyze("Test log")
    assert hasattr(result, "severity")
    assert hasattr(result, "category")
    assert hasattr(result, "summary")
    assert hasattr(result, "recommendations")


def test_fake_provider_is_llm_provider_subclass():
    assert issubclass(FakeLLMProvider, LLMProvider)


def test_fake_provider_cannot_be_instantiated_without_analyze():
    provider = FakeLLMProvider()
    assert callable(provider.analyze)


# =============================================================================
# validate_log_message from base
# =============================================================================


def test_validate_log_message_valid():
    result = validate_log_message("Valid log message")
    assert result == "Valid log message"


def test_validate_log_message_strips_whitespace():
    result = validate_log_message("   trimmed message   ")
    assert result == "trimmed message"


def test_validate_log_message_empty_raises():
    with pytest.raises(ProviderInputError):
        validate_log_message("")


def test_validate_log_message_spaces_only_raises():
    with pytest.raises(ProviderInputError):
        validate_log_message("   ")


def test_validate_log_message_non_string_raises():
    with pytest.raises(ProviderInputError):
        validate_log_message(123)


def test_validate_log_message_none_raises():
    with pytest.raises(ProviderInputError):
        validate_log_message(None)


def test_validate_log_message_list_raises():
    with pytest.raises(ProviderInputError):
        validate_log_message(["not", "a", "string"])


def test_validate_log_message_accepts_long_message():
    long_msg = "x" * 1_000_000
    result = validate_log_message(long_msg)
    assert len(result) == 1_000_000


def test_validate_log_message_too_long_raises():
    too_long = "x" * 1_000_001
    with pytest.raises(ProviderInputError):
        validate_log_message(too_long)


# =============================================================================
# LLMProvider abstract
# =============================================================================


def test_llm_provider_is_abstract():
    with pytest.raises(TypeError):
        LLMProvider()


def test_llm_provider_has_analyze_abstract():
    assert hasattr(LLMProvider, "analyze")


# =============================================================================
# Provider exceptions
# =============================================================================


def test_provider_error_is_exception():
    assert issubclass(ProviderError, Exception)


def test_provider_configuration_error_inheritance():
    assert issubclass(ProviderConfigurationError, (ProviderError, ValueError))


def test_provider_input_error_inheritance():
    assert issubclass(ProviderInputError, (ProviderError, ValueError))


def test_provider_response_error_inheritance():
    assert issubclass(ProviderResponseError, (ProviderError, ValueError))


# =============================================================================
# AnalysisResult schema validation via normalize_analysis_payload
# =============================================================================


def test_normalize_analysis_valid_payload():
    from providers.base import normalize_analysis_payload

    payload = {
        "severity": "HIGH",
        "category": "AUTH",
        "summary": "High severity alert",
        "recommendations": ["Investigate immediately", "Check logs"],
    }
    result = normalize_analysis_payload(payload)
    assert result.severity == "HIGH"
    assert result.category == "AUTH"
    assert result.summary == "High severity alert"
    assert result.recommendations == ["Investigate immediately", "Check logs"]


def test_normalize_analysis_missing_field_raises():
    from providers.base import normalize_analysis_payload

    payload = {
        "severity": "LOW",
        "category": "TEST",
        "summary": "Test summary",
    }
    with pytest.raises(ProviderResponseError):
        normalize_analysis_payload(payload)


def test_normalize_analysis_unsupported_field_raises():
    from providers.base import normalize_analysis_payload

    payload = {
        "severity": "LOW",
        "category": "TEST",
        "summary": "Test summary",
        "recommendations": ["test"],
        "extra_field": "unexpected",
    }
    with pytest.raises(ProviderResponseError):
        normalize_analysis_payload(payload)


def test_normalize_analysis_invalid_severity_raises():
    from providers.base import normalize_analysis_payload

    payload = {
        "severity": "INVALID",
        "category": "TEST",
        "summary": "Test summary",
        "recommendations": ["test"],
    }
    with pytest.raises(ProviderResponseError):
        normalize_analysis_payload(payload)


def test_normalize_analysis_recommendations_not_list_raises():
    from providers.base import normalize_analysis_payload

    payload = {
        "severity": "LOW",
        "category": "TEST",
        "summary": "Test summary",
        "recommendations": "not a list",
    }
    with pytest.raises(ProviderResponseError):
        normalize_analysis_payload(payload)


def test_normalize_analysis_too_many_recommendations_raises():
    from providers.base import normalize_analysis_payload

    payload = {
        "severity": "LOW",
        "category": "TEST",
        "summary": "Test summary",
        "recommendations": ["rec"] * 21,
    }
    with pytest.raises(ProviderResponseError):
        normalize_analysis_payload(payload)


def test_normalize_analysis_too_long_recommendation_raises():
    from providers.base import normalize_analysis_payload

    payload = {
        "severity": "LOW",
        "category": "TEST",
        "summary": "Test summary",
        "recommendations": ["x" * 1001],
    }
    with pytest.raises(ProviderResponseError):
        normalize_analysis_payload(payload)


def test_parse_analysis_response_valid_string():
    from providers.base import parse_analysis_response

    content = (
        '{"severity":"MEDIUM","category":"NETWORK","summary":"Test","recommendations":["Do this"]}'
    )
    result = parse_analysis_response(content)
    assert result.severity == "MEDIUM"
    assert result.category == "NETWORK"


def test_parse_analysis_response_empty_raises():
    from providers.base import parse_analysis_response

    with pytest.raises(ProviderResponseError):
        parse_analysis_response("")


def test_parse_analysis_response_not_json_raises():
    from providers.base import parse_analysis_response

    with pytest.raises(ProviderResponseError):
        parse_analysis_response("not json at all")


def test_parse_analysis_response_bytes_valid():
    from providers.base import parse_analysis_response

    content = b'{"severity":"LOW","category":"TEST","summary":"Test","recommendations":["r"]}'
    result = parse_analysis_response(content)
    assert result.severity == "LOW"


def test_parse_analysis_response_non_string_raises():
    from providers.base import parse_analysis_response

    with pytest.raises(ProviderResponseError):
        parse_analysis_response(123)


# =============================================================================
# Constants from base
# =============================================================================


def test_allowed_severities():
    assert ALLOWED_SEVERITIES == {"LOW", "MEDIUM", "HIGH", "CRITICAL"}


def test_analysis_fields():
    assert ANALYSIS_FIELDS == frozenset({"severity", "category", "summary", "recommendations"})


# =============================================================================
# Health check with real DB state
# =============================================================================


def test_health_check_returns_up():
    from app import health

    result = health()
    assert result["status"] == "ok"
    assert result["database"] == "up"


# =============================================================================
# End-to-end: log creation then analyze via fake provider through API
# =============================================================================


def test_end_to_end_log_create_and_analyze():
    from fastapi.testclient import TestClient as TC

    from app import app as app_module

    c = TC(app_module)
    c.post("/logs", json={"message": "End to end test", "level": "CRITICAL", "source": "e2e"})
    logs = c.get("/logs").json()
    assert len(logs) == 1
    log_id = logs[0]["id"]

    from unittest.mock import patch as mock_patch

    with mock_patch("app.get_llm_provider") as mock_provider:
        mock_provider.return_value = FakeLLMProvider()
        resp = c.post(f"/logs/{log_id}/analyze")
    assert resp.status_code == 201
    data = resp.json()
    assert data["log_id"] == log_id
    assert data["result"]["severity"] == "LOW"
