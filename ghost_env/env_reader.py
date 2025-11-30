"""Read and process .env files."""

import os
from pathlib import Path
from typing import Dict, Optional

from ghost_env.jwt_wrapper import wrap_value, is_wrapped_token


def read_env_file(env_path: Optional[str] = None) -> Dict[str, str]:
    """
    Read a .env file and return key-value pairs.
    
    Args:
        env_path: Path to the .env file. If None, searches for .env in current directory.
    
    Returns:
        Dictionary of environment variable key-value pairs
    """
    if env_path is None:
        env_path = ".env"
    
    env_file = Path(env_path)
    if not env_file.exists():
        return {}
    
    env_vars = {}
    
    with open(env_file, "r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            
            # Skip empty lines and comments
            if not line or line.startswith("#"):
                continue
            
            # Parse KEY=VALUE format
            if "=" in line:
                key, value = line.split("=", 1)
                key = key.strip()
                value = value.strip()
                
                # Remove quotes if present
                if value.startswith('"') and value.endswith('"'):
                    value = value[1:-1]
                elif value.startswith("'") and value.endswith("'"):
                    value = value[1:-1]
                
                env_vars[key] = value
    
    return env_vars


def wrap_env_file(env_vars: Dict[str, str], signing_key: str) -> Dict[str, str]:
    """
    Wrap all environment variable values in JWT tokens.
    
    Args:
        env_vars: Dictionary of environment variable key-value pairs
        signing_key: The secret key used to sign the JWTs
    
    Returns:
        Dictionary with wrapped values (keys remain the same)
    """
    wrapped = {}
    for key, value in env_vars.items():
        # Skip already wrapped tokens
        if is_wrapped_token(value):
            wrapped[key] = value
        else:
            wrapped[key] = wrap_value(value, signing_key)
    
    return wrapped


def unwrap_env_vars(env_vars: Dict[str, str], signing_key: str) -> Dict[str, str]:
    """
    Unwrap JWT tokens in environment variables.
    
    Args:
        env_vars: Dictionary of environment variable key-value pairs (may contain tokens)
        signing_key: The secret key used to verify the JWTs
    
    Returns:
        Dictionary with unwrapped values
    """
    from ghost_env.jwt_wrapper import unwrap_value
    
    unwrapped = {}
    for key, value in env_vars.items():
        if is_wrapped_token(value):
            unwrapped_value = unwrap_value(value, signing_key)
            if unwrapped_value is not None:
                unwrapped[key] = unwrapped_value
            else:
                # If unwrapping fails, keep the token (or handle error)
                unwrapped[key] = value
        else:
            unwrapped[key] = value
    
    return unwrapped


def write_ghost_env_file(env_path: str, output_path: str, signing_key: str) -> int:
    """
    Convert a .env file to a ghost.env file with wrapped values.
    Preserves comments and formatting from the original file.
    
    Args:
        env_path: Path to the input .env file
        output_path: Path to the output ghost.env file
        signing_key: The secret key used to sign the JWTs
    
    Returns:
        Number of variables wrapped
    """
    env_file = Path(env_path)
    if not env_file.exists():
        raise FileNotFoundError(f"Environment file not found: {env_path}")
    
    output_file = Path(output_path)
    wrapped_count = 0
    
    # Read original file to preserve comments and formatting
    with open(env_file, "r", encoding="utf-8") as infile:
        lines = infile.readlines()
    
    # Read env vars to get wrapped values
    env_vars = read_env_file(env_path)
    wrapped_vars = wrap_env_file(env_vars, signing_key)
    
    # Write output file
    with open(output_file, "w", encoding="utf-8") as outfile:
        for line in lines:
            original_line = line
            line = line.strip()
            
            # Preserve empty lines and comments
            if not line or line.startswith("#"):
                outfile.write(original_line)
                continue
            
            # Process KEY=VALUE lines
            if "=" in line:
                key, value = line.split("=", 1)
                key = key.strip()
                original_value = value.strip()
                
                # Remove quotes if present for comparison
                unquoted_value = original_value
                if unquoted_value.startswith('"') and unquoted_value.endswith('"'):
                    unquoted_value = unquoted_value[1:-1]
                elif unquoted_value.startswith("'") and unquoted_value.endswith("'"):
                    unquoted_value = unquoted_value[1:-1]
                
                # Replace with wrapped value if it exists
                if key in wrapped_vars:
                    wrapped_value = wrapped_vars[key]
                    # Preserve original quoting style if present
                    if original_value.startswith('"') and original_value.endswith('"'):
                        outfile.write(f'{key}="{wrapped_value}"\n')
                    elif original_value.startswith("'") and original_value.endswith("'"):
                        outfile.write(f"{key}='{wrapped_value}'\n")
                    else:
                        outfile.write(f"{key}={wrapped_value}\n")
                    wrapped_count += 1
                else:
                    # Keep original line if key not found (shouldn't happen)
                    outfile.write(original_line)
            else:
                # Keep lines that don't match KEY=VALUE format
                outfile.write(original_line)
    
    return wrapped_count

