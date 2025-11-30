"""ghost_env - Secure environment variable bridge for AI-powered IDEs."""

__version__ = "0.1.0"

from ghost_env.jwt_wrapper import wrap_value, unwrap_value
from ghost_env.env_reader import read_env_file, wrap_env_file, write_ghost_env_file
from ghost_env.config import get_config_path, ensure_signing_key

__all__ = [
    "__version__",
    "wrap_value",
    "unwrap_value",
    "read_env_file",
    "wrap_env_file",
    "write_ghost_env_file",
    "get_config_path",
    "ensure_signing_key",
]

