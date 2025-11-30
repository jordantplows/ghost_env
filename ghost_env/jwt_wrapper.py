"""JWT wrapper for encoding and decoding environment values."""

import jwt
import secrets
from typing import Optional
from datetime import datetime, timedelta


def generate_signing_key() -> str:
    """Generate a new signing key for JWT tokens."""
    return secrets.token_urlsafe(32)


def wrap_value(value: str, signing_key: str, expires_in_days: int = 365) -> str:
    """
    Wrap a sensitive value in a signed JWT token.
    
    Args:
        value: The plaintext value to wrap
        signing_key: The secret key used to sign the JWT
        expires_in_days: Token expiration time in days (default: 365)
    
    Returns:
        A JWT token prefixed with 'gho_env.' for identification
    """
    payload = {
        "value": value,
        "iat": datetime.utcnow(),
        "exp": datetime.utcnow() + timedelta(days=expires_in_days),
    }
    
    token = jwt.encode(payload, signing_key, algorithm="HS256")
    return f"gho_env.{token}"


def unwrap_value(token: str, signing_key: str) -> Optional[str]:
    """
    Unwrap a JWT token to retrieve the original value.
    
    Args:
        token: The JWT token (with or without 'gho_env.' prefix)
        signing_key: The secret key used to verify the JWT signature
    
    Returns:
        The unwrapped value if the token is valid, None otherwise
    """
    # Remove prefix if present
    if token.startswith("gho_env."):
        token = token[8:]
    
    try:
        payload = jwt.decode(token, signing_key, algorithms=["HS256"])
        return payload.get("value")
    except jwt.ExpiredSignatureError:
        return None
    except jwt.InvalidTokenError:
        return None


def is_wrapped_token(value: str) -> bool:
    """Check if a string is a ghost_env wrapped token."""
    return value.startswith("gho_env.") and len(value) > 20

