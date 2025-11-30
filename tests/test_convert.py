"""Tests for .env to ghost.env conversion."""

import tempfile
from pathlib import Path

from ghost_env.env_reader import write_ghost_env_file, read_env_file
from ghost_env.jwt_wrapper import generate_signing_key, is_wrapped_token, unwrap_value


def test_write_ghost_env_file():
    """Test converting .env to ghost.env."""
    signing_key = generate_signing_key()
    
    # Create a test .env file
    with tempfile.NamedTemporaryFile(mode="w", suffix=".env", delete=False) as f:
        f.write("# This is a comment\n")
        f.write("API_KEY=secret123\n")
        f.write("DATABASE_URL=postgres://localhost\n")
        f.write("\n")
        f.write("# Another comment\n")
        f.write('QUOTED="quoted-value"\n')
        env_path = f.name
    
    output_path = env_path.replace(".env", ".ghost.env")
    
    try:
        wrapped_count = write_ghost_env_file(env_path, output_path, signing_key)
        
        assert wrapped_count == 4
        assert Path(output_path).exists()
        
        # Read the ghost.env file
        with open(output_path, "r", encoding="utf-8") as f:
            content = f.read()
        
        # Check that comments are preserved
        assert "# This is a comment" in content
        assert "# Another comment" in content
        
        # Check that values are wrapped
        ghost_vars = read_env_file(output_path)
        assert is_wrapped_token(ghost_vars["API_KEY"])
        assert is_wrapped_token(ghost_vars["DATABASE_URL"])
        assert is_wrapped_token(ghost_vars["QUOTED"])
        
        # Verify unwrapping works
        assert unwrap_value(ghost_vars["API_KEY"], signing_key) == "secret123"
        assert unwrap_value(ghost_vars["DATABASE_URL"], signing_key) == "postgres://localhost"
        assert unwrap_value(ghost_vars["QUOTED"], signing_key) == "quoted-value"
        
    finally:
        Path(env_path).unlink()
        if Path(output_path).exists():
            Path(output_path).unlink()


def test_write_ghost_env_preserves_formatting():
    """Test that formatting is preserved in ghost.env."""
    signing_key = generate_signing_key()
    
    with tempfile.NamedTemporaryFile(mode="w", suffix=".env", delete=False) as f:
        f.write("KEY1=value1\n")
        f.write('KEY2="value2"\n')
        f.write("KEY3='value3'\n")
        env_path = f.name
    
    output_path = env_path.replace(".env", ".ghost.env")
    
    try:
        write_ghost_env_file(env_path, output_path, signing_key)
        
        with open(output_path, "r", encoding="utf-8") as f:
            lines = f.readlines()
        
        # Check that quotes are preserved
        assert any('KEY2="' in line for line in lines)
        assert any("KEY3='" in line for line in lines)
        
    finally:
        Path(env_path).unlink()
        if Path(output_path).exists():
            Path(output_path).unlink()

