"""Tests for configuration management."""

import tempfile
import shutil
from pathlib import Path

from ghost_env.config import (
    get_config_dir,
    get_signing_key_path,
    load_signing_key,
    save_signing_key,
    ensure_signing_key,
    rotate_signing_key,
)


def test_get_config_dir():
    """Test getting the configuration directory."""
    config_dir = get_config_dir()
    assert isinstance(config_dir, Path)
    assert config_dir.exists()


def test_save_and_load_signing_key(monkeypatch):
    """Test saving and loading signing keys."""
    # Use a temporary directory for testing
    with tempfile.TemporaryDirectory() as tmpdir:
        test_config_dir = Path(tmpdir) / "ghost_env"
        test_config_dir.mkdir()
        
        # Monkey patch to use test directory
        original_get_config_dir = get_config_dir
        monkeypatch.setattr(
            "ghost_env.config.get_config_dir",
            lambda: test_config_dir
        )
        
        key = "test-signing-key-12345"
        save_signing_key(key)
        
        loaded_key = load_signing_key()
        assert loaded_key == key


def test_ensure_signing_key(monkeypatch):
    """Test ensuring a signing key exists."""
    with tempfile.TemporaryDirectory() as tmpdir:
        test_config_dir = Path(tmpdir) / "ghost_env"
        test_config_dir.mkdir()
        
        monkeypatch.setattr(
            "ghost_env.config.get_config_dir",
            lambda: test_config_dir
        )
        
        # First call should create a key
        key1 = ensure_signing_key()
        assert key1 is not None
        assert len(key1) > 0
        
        # Second call should return the same key
        key2 = ensure_signing_key()
        assert key2 == key1


def test_rotate_signing_key(monkeypatch):
    """Test rotating the signing key."""
    with tempfile.TemporaryDirectory() as tmpdir:
        test_config_dir = Path(tmpdir) / "ghost_env"
        test_config_dir.mkdir()
        
        monkeypatch.setattr(
            "ghost_env.config.get_config_dir",
            lambda: test_config_dir
        )
        
        # Create initial key
        key1 = ensure_signing_key()
        
        # Rotate it
        key2 = rotate_signing_key()
        
        # Keys should be different
        assert key1 != key2
        
        # New key should be loaded
        loaded_key = load_signing_key()
        assert loaded_key == key2

