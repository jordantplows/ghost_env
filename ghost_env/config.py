"""Configuration and signing key management."""

import os
import json
from pathlib import Path
from typing import Optional

from ghost_env.jwt_wrapper import generate_signing_key


def get_config_dir() -> Path:
    """Get the configuration directory for ghost_env."""
    # Use XDG config directory if available, otherwise use home directory
    if os.name == "nt":  # Windows
        config_dir = Path(os.environ.get("APPDATA", Path.home())) / "ghost_env"
    else:  # Unix-like
        xdg_config = os.environ.get("XDG_CONFIG_HOME")
        if xdg_config:
            config_dir = Path(xdg_config) / "ghost_env"
        else:
            config_dir = Path.home() / ".config" / "ghost_env"
    
    config_dir.mkdir(parents=True, exist_ok=True)
    return config_dir


def get_config_path() -> Path:
    """Get the path to the configuration file."""
    return get_config_dir() / "config.json"


def get_signing_key_path() -> Path:
    """Get the path to the signing key file."""
    return get_config_dir() / "signing_key.txt"


def load_signing_key() -> Optional[str]:
    """
    Load the signing key from the configuration directory.
    
    Returns:
        The signing key if it exists, None otherwise
    """
    key_path = get_signing_key_path()
    if key_path.exists():
        return key_path.read_text(encoding="utf-8").strip()
    return None


def save_signing_key(key: str) -> None:
    """
    Save the signing key to the configuration directory.
    
    Args:
        key: The signing key to save
    """
    key_path = get_signing_key_path()
    # Set restrictive permissions (Unix-like systems)
    key_path.write_text(key, encoding="utf-8")
    if os.name != "nt":
        os.chmod(key_path, 0o600)


def ensure_signing_key() -> str:
    """
    Ensure a signing key exists, creating one if necessary.
    
    Returns:
        The signing key
    """
    key = load_signing_key()
    if key is None:
        key = generate_signing_key()
        save_signing_key(key)
    return key


def rotate_signing_key() -> str:
    """
    Generate and save a new signing key, invalidating all previous tokens.
    
    Returns:
        The new signing key
    """
    key = generate_signing_key()
    save_signing_key(key)
    return key

