"""Tests for JWT wrapper functionality."""

import pytest
from ghost_env.jwt_wrapper import (
    generate_signing_key,
    wrap_value,
    unwrap_value,
    is_wrapped_token,
)


def test_generate_signing_key():
    """Test that signing keys are generated."""
    key = generate_signing_key()
    assert isinstance(key, str)
    assert len(key) > 0


def test_wrap_and_unwrap():
    """Test wrapping and unwrapping values."""
    key = generate_signing_key()
    original_value = "my-secret-api-key-12345"
    
    wrapped = wrap_value(original_value, key)
    assert wrapped.startswith("gho_env.")
    
    unwrapped = unwrap_value(wrapped, key)
    assert unwrapped == original_value


def test_wrap_unwrap_without_prefix():
    """Test unwrapping tokens without the prefix."""
    key = generate_signing_key()
    original_value = "test-value"
    
    wrapped = wrap_value(original_value, key)
    token = wrapped[8:]  # Remove "gho_env." prefix
    
    unwrapped = unwrap_value(token, key)
    assert unwrapped == original_value


def test_wrong_key_fails():
    """Test that unwrapping with wrong key fails."""
    key1 = generate_signing_key()
    key2 = generate_signing_key()
    
    wrapped = wrap_value("secret", key1)
    unwrapped = unwrap_value(wrapped, key2)
    
    assert unwrapped is None


def test_is_wrapped_token():
    """Test token detection."""
    key = generate_signing_key()
    wrapped = wrap_value("test", key)
    
    assert is_wrapped_token(wrapped) is True
    assert is_wrapped_token("not-a-token") is False
    assert is_wrapped_token("gho_env.short") is False  # Too short


def test_expired_token():
    """Test that expired tokens cannot be unwrapped."""
    import jwt
    from datetime import datetime, timedelta
    
    key = generate_signing_key()
    
    # Create an expired token manually
    payload = {
        "value": "secret",
        "iat": datetime.utcnow() - timedelta(days=2),
        "exp": datetime.utcnow() - timedelta(days=1),
    }
    token = jwt.encode(payload, key, algorithm="HS256")
    wrapped = f"gho_env.{token}"
    
    unwrapped = unwrap_value(wrapped, key)
    assert unwrapped is None

