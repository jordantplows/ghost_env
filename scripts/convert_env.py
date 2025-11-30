#!/usr/bin/env python3
"""
Simple standalone script to convert .env to ghost.env.
Can be run directly: python scripts/convert_env.py
"""

import sys
from pathlib import Path

# Add parent directory to path to import ghost_env
sys.path.insert(0, str(Path(__file__).parent.parent))

from ghost_env.config import ensure_signing_key
from ghost_env.env_reader import write_ghost_env_file


def main():
    """Convert .env to ghost.env."""
    input_file = ".env"
    output_file = "ghost.env"
    
    if len(sys.argv) > 1:
        input_file = sys.argv[1]
    if len(sys.argv) > 2:
        output_file = sys.argv[2]
    
    if not Path(input_file).exists():
        print(f"Error: {input_file} not found", file=sys.stderr)
        sys.exit(1)
    
    try:
        signing_key = ensure_signing_key()
        wrapped_count = write_ghost_env_file(input_file, output_file, signing_key)
        print(f"✓ Converted {wrapped_count} environment variable(s)")
        print(f"✓ Wrapped values written to: {output_file}")
    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()

