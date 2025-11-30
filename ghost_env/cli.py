"""Command-line interface for ghost_env."""

import argparse
import json
import sys
from pathlib import Path
from typing import Optional

from ghost_env.config import ensure_signing_key, rotate_signing_key, get_config_path
from ghost_env.env_reader import read_env_file, wrap_env_file, unwrap_env_vars, write_ghost_env_file
from ghost_env.jwt_wrapper import is_wrapped_token, unwrap_value


def cmd_init(args: argparse.Namespace) -> int:
    """Initialize ghost_env by generating a signing key."""
    print("Initializing ghost_env...")
    
    key = ensure_signing_key()
    config_path = get_config_path()
    
    print(f"✓ Signing key generated and saved to: {config_path.parent}")
    print("✓ ghost_env is ready to use!")
    
    return 0


def cmd_serve(args: argparse.Namespace) -> int:
    """Serve wrapped environment variables via HTTP server."""
    try:
        from http.server import HTTPServer, BaseHTTPRequestHandler
        import urllib.parse
    except ImportError:
        print("Error: HTTP server functionality requires Python standard library", file=sys.stderr)
        return 1
    
    # Ensure signing key exists
    signing_key = ensure_signing_key()
    
    # Read .env file
    env_path = args.env_file or ".env"
    env_vars = read_env_file(env_path)
    
    if not env_vars:
        print(f"Warning: No environment variables found in {env_path}", file=sys.stderr)
    
    # Wrap all values
    wrapped_vars = wrap_env_file(env_vars, signing_key)
    
    verbose = args.verbose
    
    class EnvHandler(BaseHTTPRequestHandler):
        def do_GET(self):
            """Handle GET requests for environment variables."""
            if self.path == "/env" or self.path == "/env.json":
                self.send_response(200)
                self.send_header("Content-Type", "application/json")
                self.send_header("Access-Control-Allow-Origin", "*")
                self.end_headers()
                self.wfile.write(json.dumps(wrapped_vars).encode("utf-8"))
            elif self.path == "/health":
                self.send_response(200)
                self.send_header("Content-Type", "text/plain")
                self.end_headers()
                self.wfile.write(b"OK")
            else:
                self.send_response(404)
                self.end_headers()
        
        def do_POST(self):
            """Handle POST requests to unwrap tokens."""
            if self.path == "/unwrap":
                content_length = int(self.headers.get("Content-Length", 0))
                body = self.rfile.read(content_length)
                
                try:
                    data = json.loads(body.decode("utf-8"))
                    token = data.get("token", "")
                    
                    if is_wrapped_token(token):
                        value = unwrap_value(token, signing_key)
                        if value is not None:
                            response = {"value": value}
                        else:
                            response = {"error": "Invalid or expired token"}
                    else:
                        response = {"error": "Not a wrapped token"}
                    
                    self.send_response(200)
                    self.send_header("Content-Type", "application/json")
                    self.end_headers()
                    self.wfile.write(json.dumps(response).encode("utf-8"))
                except Exception as e:
                    self.send_response(400)
                    self.send_header("Content-Type", "application/json")
                    self.end_headers()
                    self.wfile.write(json.dumps({"error": str(e)}).encode("utf-8"))
            else:
                self.send_response(404)
                self.end_headers()
        
        def log_message(self, format, *args):
            """Suppress default logging."""
            if verbose:
                super().log_message(format, *args)
    
    port = args.port
    server_address = ("", port)
    httpd = HTTPServer(server_address, EnvHandler)
    
    print(f"ghost_env server running on http://localhost:{port}")
    print(f"  GET  /env.json - Get all wrapped environment variables")
    print(f"  POST /unwrap   - Unwrap a JWT token")
    print(f"  GET  /health   - Health check")
    print("\nPress Ctrl+C to stop")
    
    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        print("\nShutting down server...")
        httpd.shutdown()
        return 0


def cmd_rotate(args: argparse.Namespace) -> int:
    """Rotate the signing key, invalidating all previous tokens."""
    print("Rotating signing key...")
    
    new_key = rotate_signing_key()
    print("✓ New signing key generated")
    print("⚠ All previously issued tokens are now invalid")
    
    return 0


def cmd_wrap(args: argparse.Namespace) -> int:
    """Wrap environment variables from a .env file and output them."""
    signing_key = ensure_signing_key()
    env_vars = read_env_file(args.env_file)
    
    if not env_vars:
        print(f"No environment variables found in {args.env_file}", file=sys.stderr)
        return 1
    
    wrapped_vars = wrap_env_file(env_vars, signing_key)
    
    if args.format == "json":
        print(json.dumps(wrapped_vars, indent=2))
    elif args.format == "env":
        for key, value in wrapped_vars.items():
            print(f"{key}={value}")
    else:
        print("Unknown format", file=sys.stderr)
        return 1
    
    return 0


def cmd_unwrap(args: argparse.Namespace) -> int:
    """Unwrap a JWT token."""
    signing_key = ensure_signing_key()
    
    if args.token:
        value = unwrap_value(args.token, signing_key)
        if value is not None:
            print(value)
            return 0
        else:
            print("Error: Invalid or expired token", file=sys.stderr)
            return 1
    else:
        print("Error: No token provided", file=sys.stderr)
        return 1


def cmd_convert(args: argparse.Namespace) -> int:
    """Convert a .env file to a ghost.env file with wrapped values."""
    signing_key = ensure_signing_key()
    
    input_file = args.input or ".env"
    output_file = args.output or "ghost.env"
    
    try:
        wrapped_count = write_ghost_env_file(input_file, output_file, signing_key)
        print(f"✓ Converted {wrapped_count} environment variable(s)")
        print(f"✓ Wrapped values written to: {output_file}")
        return 0
    except FileNotFoundError as e:
        print(f"Error: {e}", file=sys.stderr)
        return 1
    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        return 1


def main() -> int:
    """Main CLI entry point."""
    parser = argparse.ArgumentParser(
        description="ghost_env - Secure environment variable bridge for AI-powered IDEs"
    )
    
    subparsers = parser.add_subparsers(dest="command", help="Command to run")
    
    # init command
    init_parser = subparsers.add_parser("init", help="Initialize ghost_env")
    
    # serve command
    serve_parser = subparsers.add_parser("serve", help="Serve wrapped environment variables")
    serve_parser.add_argument("--port", type=int, default=8787, help="Port to serve on (default: 8787)")
    serve_parser.add_argument("--env-file", type=str, help="Path to .env file (default: .env)")
    serve_parser.add_argument("--verbose", action="store_true", help="Enable verbose logging")
    
    # rotate command
    rotate_parser = subparsers.add_parser("rotate", help="Rotate the signing key")
    
    # wrap command
    wrap_parser = subparsers.add_parser("wrap", help="Wrap environment variables")
    wrap_parser.add_argument("--env-file", type=str, default=".env", help="Path to .env file")
    wrap_parser.add_argument("--format", choices=["json", "env"], default="json", help="Output format")
    
    # unwrap command
    unwrap_parser = subparsers.add_parser("unwrap", help="Unwrap a JWT token")
    unwrap_parser.add_argument("token", nargs="?", help="The JWT token to unwrap")
    
    # convert command
    convert_parser = subparsers.add_parser(
        "convert",
        help="Convert .env file to ghost.env file with wrapped values"
    )
    convert_parser.add_argument(
        "--input", "-i",
        type=str,
        help="Input .env file path (default: .env)"
    )
    convert_parser.add_argument(
        "--output", "-o",
        type=str,
        help="Output ghost.env file path (default: ghost.env)"
    )
    
    args = parser.parse_args()
    
    if not args.command:
        parser.print_help()
        return 1
    
    if args.command == "init":
        return cmd_init(args)
    elif args.command == "serve":
        return cmd_serve(args)
    elif args.command == "rotate":
        return cmd_rotate(args)
    elif args.command == "wrap":
        return cmd_wrap(args)
    elif args.command == "unwrap":
        return cmd_unwrap(args)
    elif args.command == "convert":
        return cmd_convert(args)
    else:
        parser.print_help()
        return 1


if __name__ == "__main__":
    sys.exit(main())

