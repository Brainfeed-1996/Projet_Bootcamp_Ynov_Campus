"""Tests pour les providers LLM."""
import pytest
from providers.base import ProviderError
from providers.fake_provider import FakeLLMProvider


def test_fake_provider_analyze():
    """Test d'analyse avec le fournisseur factice."""
    provider = FakeLLMProvider()
    result = provider.analyze("Suspicious login attempt from unknown IP")
    assert result.severity in ("LOW", "MEDIUM", "HIGH", "CRITICAL")
    assert result.category
    assert result.summary
    assert isinstance(result.recommendations, list)


def test_fake_provider_returns_consistent_results():
    """Test que le fournisseur factice retourne des résultats cohérents."""
    provider = FakeLLMProvider()
    result1 = provider.analyze("Test message")
    result2 = provider.analyze("Test message")
    assert result1.severity == result2.severity


def test_fake_provider_handles_empty_message():
    """Test que le fournisseur gère un message vide."""
    provider = FakeLLMProvider()
    result = provider.analyze("")
    assert result.severity in ("LOW", "MEDIUM", "HIGH", "CRITICAL")
def test_openai_provider_mock():
    from unittest.mock import Mock, patch
    with patch('providers.openai_provider.OpenAI'):
        provider = OpenAILLMProvider()
        assert provider is not None

def test_ollama_provider_mock():
    from unittest.mock import Mock, patch
    with patch('providers.ollama_provider.Client'):
        provider = OllamaLLMProvider()
        assert provider is not None
