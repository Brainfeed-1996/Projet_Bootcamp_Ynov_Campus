import json
import math
import os
from abc import ABC, abstractmethod
from collections.abc import Mapping
from typing import Any
from urllib.parse import urlsplit

from schemas.analysis import AnalysisResult

ALLOWED_SEVERITIES = frozenset({"LOW", "MEDIUM", "HIGH", "CRITICAL"})
ANALYSIS_FIELDS = frozenset({"severity", "category", "summary", "recommendations", "provider"})
DEFAULT_OPENAI_TIMEOUT = 30.0
DEFAULT_OLLAMA_TIMEOUT = 60.0
MAX_LOG_MESSAGE_LENGTH = 1_000_000
MAX_JSON_RESPONSE_LENGTH = 1_000_000
MAX_MODEL_LENGTH = 200
MAX_CATEGORY_LENGTH = 200
MAX_SUMMARY_LENGTH = 4_096
MAX_RECOMMENDATIONS = 20
MAX_RECOMMENDATION_LENGTH = 1_000
ALLOWED_PROVIDERS = frozenset({"openai", "ollama", "fake"})


class ProviderError(Exception):
    pass


class ProviderConfigurationError(ProviderError, ValueError):
    pass


class ProviderInputError(ProviderError, ValueError):
    pass


class ProviderResponseError(ProviderError, ValueError):
    pass


class ProviderTimeoutError(ProviderError, TimeoutError):
    pass


def validate_log_message(log_message: Any) -> str:
    if not isinstance(log_message, str):
        raise ProviderInputError("log_message must be a string")

    message = log_message.strip()
    if not message:
        raise ProviderInputError("log_message must not be empty")
    if len(message) > MAX_LOG_MESSAGE_LENGTH:
        raise ProviderInputError("log_message is too long")
    return message


def normalize_model(model: Any, environment_variable: str) -> str:
    if not isinstance(model, str):
        raise ProviderConfigurationError(f"{environment_variable} must be a string")

    normalized = model.strip()
    if not normalized:
        raise ProviderConfigurationError(f"{environment_variable} must not be empty")
    if len(normalized) > MAX_MODEL_LENGTH or any(
        character.isspace() for character in normalized
    ):
        raise ProviderConfigurationError(f"{environment_variable} is invalid")
    return normalized


def normalize_timeout(
    timeout: Any,
    environment_variable: str,
    default: float,
) -> float:
    raw_value = os.environ.get(environment_variable) if timeout is None else timeout
    if isinstance(raw_value, bool):
        raise ProviderConfigurationError(
            f"{environment_variable} must be a positive number"
        )

    try:
        normalized = float(raw_value)
        if not math.isfinite(normalized) or normalized <= 0:
            raise ValueError
    except (TypeError, ValueError, OverflowError, RuntimeError):
        raise ProviderConfigurationError(
            f"{environment_variable} must be a positive number"
        ) from None

    return normalized


def normalize_base_url(base_url: Any) -> str:
    if not isinstance(base_url, str):
        raise ProviderConfigurationError("Ollama base URL must be a string")

    normalized = base_url.strip()
    if not normalized or any(character.isspace() for character in normalized):
        raise ProviderConfigurationError("Ollama base URL is invalid")

    try:
        parsed = urlsplit(normalized)
        port = parsed.port
    except ValueError:
        raise ProviderConfigurationError("Ollama base URL is invalid") from None

    if (
        parsed.scheme.lower() not in {"http", "https"}
        or not parsed.hostname
        or parsed.username is not None
        or parsed.password is not None
        or parsed.query
        or parsed.fragment
        or port == 0
        or parsed.netloc.endswith(":")
        or "?" in normalized
        or "#" in normalized
        or "\\" in normalized
    ):
        raise ProviderConfigurationError("Ollama base URL is invalid")

    path = parsed.path.rstrip("/")
    return urlsplit(f"{parsed.scheme.lower()}://{parsed.netloc}{path}").geturl()


def _reject_duplicate_key(pairs: list[tuple[str, Any]]) -> dict[str, Any]:
    result = {}
    for key, value in pairs:
        if key in result:
            raise ValueError("duplicate JSON key")
        result[key] = value
    return result


def _reject_non_finite_json_number(value: str) -> Any:
    raise ValueError("non-finite JSON number")


def _normalize_text(value: Any, field: str, maximum: int) -> str:
    if not isinstance(value, str):
        raise ProviderResponseError(f"LLM response field '{field}' must be a string")

    normalized = value.strip()
    if not normalized:
        raise ProviderResponseError(f"LLM response field '{field}' must not be empty")
    if len(normalized) > maximum:
        raise ProviderResponseError(f"LLM response field '{field}' is too long")
    return normalized


def normalize_analysis_payload(payload: Any, provider: str | None = None) -> AnalysisResult:
    if not isinstance(payload, Mapping):
        raise ProviderResponseError("LLM response must be a JSON object")

    missing_fields = sorted(ANALYSIS_FIELDS.difference(payload.keys()), key=str)
    unexpected_fields = sorted(set(payload.keys()).difference(ANALYSIS_FIELDS), key=str)
    if missing_fields:
        raise ProviderResponseError(
            "LLM response is missing required field(s): " + ", ".join(missing_fields)
        )
    if unexpected_fields:
        raise ProviderResponseError(
            "LLM response contains unsupported field(s): "
            + ", ".join(unexpected_fields)
        )

    severity = _normalize_text(
        payload["severity"], "severity", MAX_SUMMARY_LENGTH
    ).upper()
    if severity not in ALLOWED_SEVERITIES:
        raise ProviderResponseError(
            "LLM response field 'severity' must be LOW, MEDIUM, HIGH, or CRITICAL"
        )

    recommendations = payload["recommendations"]
    if not isinstance(recommendations, list):
        raise ProviderResponseError(
            "LLM response field 'recommendations' must be an array of strings"
        )
    if len(recommendations) > MAX_RECOMMENDATIONS:
        raise ProviderResponseError(
            "LLM response field 'recommendations' contains too many items"
        )

    normalized_recommendations = [
        _normalize_text(item, f"recommendations[{index}]", MAX_RECOMMENDATION_LENGTH)
        for index, item in enumerate(recommendations)
    ]

    provider_value = provider
    if "provider" in payload:
        provider_value = _normalize_text(payload["provider"], "provider", MAX_CATEGORY_LENGTH).lower()
        if provider_value not in ALLOWED_PROVIDERS:
            raise ProviderResponseError(
                f"LLM response field 'provider' must be one of: {', '.join(sorted(ALLOWED_PROVIDERS))}"
            )

    normalized = {
        "severity": severity,
        "category": _normalize_text(
            payload["category"], "category", MAX_CATEGORY_LENGTH
        ),
        "summary": _normalize_text(payload["summary"], "summary", MAX_SUMMARY_LENGTH),
        "recommendations": normalized_recommendations,
        "provider": provider_value or "unknown",
    }
    return AnalysisResult(**normalized)


def parse_analysis_response(
    content: Any, source: str = "LLM response", provider: str | None = None
) -> AnalysisResult:
    if isinstance(content, bytes):
        try:
            content = content.decode("utf-8")
        except UnicodeDecodeError:
            raise ProviderResponseError(f"{source} must be UTF-8 text") from None

    if not isinstance(content, str):
        raise ProviderResponseError(f"{source} must be a JSON string")
    if not content.strip():
        raise ProviderResponseError(f"{source} must not be empty")
    if len(content) > MAX_JSON_RESPONSE_LENGTH:
        raise ProviderResponseError(f"{source} is too large")

    try:
        payload = json.loads(
            content,
            object_pairs_hook=_reject_duplicate_key,
            parse_constant=_reject_non_finite_json_number,
        )
    except (json.JSONDecodeError, TypeError, ValueError):
        raise ProviderResponseError(f"{source} is not valid JSON") from None

    return normalize_analysis_payload(payload, provider)


class LLMProvider(ABC):
    @abstractmethod
    def analyze(self, log_message: str) -> AnalysisResult:
        pass