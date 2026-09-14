"""Tests de validation des schémas Pydantic."""
import pytest
from pydantic import ValidationError
from app import UserCreate, LogCreate, AnalysisCreate


def test_user_create_valid():
    """Test de création d'utilisateur valide."""
    user = UserCreate(
        username="validuser",
        email="valid@example.com",
        password="SecurePass123",
    )
    assert user.username == "validuser"


def test_user_create_invalid_email():
    """Test avec un email invalide."""
    with pytest.raises(ValidationError):
        UserCreate(
            username="test",
            email="invalid-email",
            password="SecurePass123",
        )


def test_user_create_short_username():
    """Test avec un nom d'utilisateur trop court."""
    with pytest.raises(ValidationError):
        UserCreate(
            username="ab",
            email="test@example.com",
            password="SecurePass123",
        )


def test_log_create_valid():
    """Test de création de log valide."""
    log = LogCreate(
        message="Test log",
        level="INFO",
        source="test",
    )
    assert log.message == "Test log"


def test_log_create_invalid_level():
    """Test avec un niveau invalide."""
    with pytest.raises(ValidationError):
        LogCreate(
            message="Test",
            level="INVALID_LEVEL",
        )


def test_analysis_create_valid():
    """Test de création d'analyse valide."""
    analysis = AnalysisCreate(
        log_id=1,
        severity="HIGH",
        category="SECURITY",
        summary="Test summary",
        recommendations=["Action 1", "Action 2"],
        provider="openai",
    )
    assert analysis.severity == "HIGH"


def test_analysis_create_invalid_severity():
    """Test avec une sévérité invalide."""
    with pytest.raises(ValidationError):
        AnalysisCreate(
            log_id=1,
            severity="INVALID",
            category="TEST",
            summary="Test",
            recommendations=[],
            provider="test",
        )