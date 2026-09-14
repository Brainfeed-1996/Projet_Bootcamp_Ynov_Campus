"""Tests de validation des patterns de sécurité."""
import pytest
from app import SENSITIVE_PATTERNS, sanitize_log_message


def test_ip_redaction():
    """Test de masquage d'adresses IP."""
    text = "Connection from 192.168.1.1 and 10.0.0.1"
    sanitized = sanitize_log_message(text)
    assert "192.168.1.1" not in sanitized
    assert "10.0.0.1" not in sanitized
    assert "[IP_REDACTED]" in sanitized


def test_email_redaction():
    """Test de masquage d'adresses email."""
    text = "Contact user@example.com for details"
    sanitized = sanitize_log_message(text)
    assert "user@example.com" not in sanitized
    assert "[EMAIL_REDACTED]" in sanitized


def test_password_redaction():
    """Test de masquage de mots de passe."""
    text = "password: secret123, pwd=topsecret"
    sanitized = sanitize_log_message(text)
    assert "secret123" not in sanitized
    assert "topsecret" not in sanitized
    assert "[CREDENTIAL_REDACTED]" in sanitized


def test_credit_card_redaction():
    """Test de masquage de numéros de carte bancaire."""
    text = "Card: 4111-1111-1111-1111"
    sanitized = sanitize_log_message(text)
    assert "4111-1111-1111-1111" not in sanitized
    assert "[CARD_REDACTED]" in sanitized


def test_token_redaction():
    """Test de masquage de tokens longs."""
    text = "Token: abcdefghijklmnopqrstuvwxyz1234567890abcdefghijklmnop"
    sanitized = sanitize_log_message(text)
    assert "[TOKEN_REDACTED]" in sanitized


def test_no_false_positive():
    """Test qu'un message normal n'est pas modifié."""
    text = "System started successfully"
    sanitized = sanitize_log_message(text)
    assert sanitized == text