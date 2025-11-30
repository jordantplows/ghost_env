"""Tests for environment file reading."""

import tempfile
from pathlib import Path

from ghost_env.env_reader import read_env_file, wrap_env_file, unwrap_env_vars


def test_read_env_file():
    """Test reading a .env file."""
    with tempfile.NamedTemporaryFile(mode="w", suffix=".env", delete=False) as f:
        f.write("API_KEY=secret123\n")
        f.write("DATABASE_URL=postgres://localhost\n")
        f.write("# This is a comment\n")
        f.write("EMPTY=\n")
        f.write('QUOTED="quoted-value"\n')
        f.write("SINGLE_QUOTE='single-value'\n")
        env_path = f.name
    
    try:
        env_vars = read_env_file(env_path)
        assert env_vars["API_KEY"] == "secret123"
        assert env_vars["DATABASE_URL"] == "postgres://localhost"
        assert "EMPTY" in env_vars
        assert env_vars["QUOTED"] == "quoted-value"
        assert env_vars["SINGLE_QUOTE"] == "single-value"
        assert len(env_vars) == 5
    finally:
        Path(env_path).unlink()


def test_read_nonexistent_file():
    """Test reading a non-existent .env file."""
    env_vars = read_env_file("/nonexistent/path/.env")
    assert env_vars == {}


def test_wrap_env_file():
    """Test wrapping environment variables."""
    from ghost_env.jwt_wrapper import generate_signing_key, is_wrapped_token
    
    key = generate_signing_key()
    env_vars = {
        "API_KEY": "secret123",
        "DATABASE_URL": "postgres://localhost",
    }
    
    wrapped = wrap_env_file(env_vars, key)
    
    assert len(wrapped) == len(env_vars)
    assert is_wrapped_token(wrapped["API_KEY"])
    assert is_wrapped_token(wrapped["DATABASE_URL"])


def test_unwrap_env_vars():
    """Test unwrapping environment variables."""
    from ghost_env.jwt_wrapper import generate_signing_key, wrap_value
    
    key = generate_signing_key()
    original_vars = {
        "API_KEY": "secret123",
        "DATABASE_URL": "postgres://localhost",
    }
    
    wrapped_vars = wrap_env_file(original_vars, key)
    unwrapped_vars = unwrap_env_vars(wrapped_vars, key)
    
    assert unwrapped_vars == original_vars


def test_unwrap_mixed_vars():
    """Test unwrapping mixed wrapped and unwrapped variables."""
    from ghost_env.jwt_wrapper import generate_signing_key, wrap_value
    
    key = generate_signing_key()
    mixed_vars = {
        "WRAPPED": wrap_value("secret", key),
        "PLAIN": "plain-value",
    }
    
    unwrapped = unwrap_env_vars(mixed_vars, key)
    assert unwrapped["WRAPPED"] == "secret"
    assert unwrapped["PLAIN"] == "plain-value"

