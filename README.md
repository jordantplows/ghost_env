# ghost_env

ghost_env is an opt-in bridge between your local `.env` file and AI-powered IDEs. It lets you run code that depends on sensitive environment variables during an AI-assisted session without ever handing the raw secrets to the model.

## Why ghost_env?

- **Current gap:** AI IDEs run locally but, for safety, they cannot read your `.env` file. That keeps secrets safe but breaks workflows that need API keys to function.
- **ghost_env solution:** Wrap each sensitive value in a signed JSON Web Token (JWT) before sharing it with the model. The model only sees a scrambled token, while your local tools can unwrap it on demand.
- **Net result:** You keep the convenience of local testing with AI assistance, minus the risk of leaking your actual keys to the AI or other users.

## How it works

1. ghost_env reads your `.env` file locally.
2. Each key/value pair is encoded inside a JWT signed with a machine-local secret.
3. The AI IDE receives only the JWTs, never the plaintext values.
4. When your code needs an environment value, the IDE swaps the JWT for the real secret just-in-time inside your machine's runtime.

Because the signing secret never leaves your device, the model cannot reverse the token to reveal the original environment value.

## Installation

Install ghost_env from PyPI:

```bash
pip install ghost-env
```

Or install from source:

```bash
git clone https://github.com/yourusername/ghost_env.git
cd ghost_env
pip install -e .
```

## Quick start

1. Run the setup command to generate a local signing key (stored outside your repo):

   ```bash
   ghost-env init
   ```

2. Start your AI IDE with ghost_env enabled:

   ```bash
   ghost-env serve --port 8787
   ```

3. Point the IDE at the localhost proxy. It will receive JWT-wrapped versions of your `.env` variables.

   The server exposes:
   - `GET /env.json` - Get all wrapped environment variables
   - `POST /unwrap` - Unwrap a JWT token (body: `{"token": "gho_env...."}`)
   - `GET /health` - Health check endpoint

## Usage

### Command-line interface

**Initialize ghost_env:**
```bash
ghost-env init
```

**Serve wrapped environment variables:**
```bash
ghost-env serve --port 8787 --env-file .env
```

**Wrap environment variables and output them:**
```bash
ghost-env wrap --format json > wrapped_env.json
ghost-env wrap --format env > wrapped_env.txt
```

**Unwrap a token:**
```bash
ghost-env unwrap "gho_env.eyJhbGciOi..."
```

**Rotate the signing key:**
```bash
ghost-env rotate
```

### Python API

```python
from ghost_env import wrap_value, unwrap_value, read_env_file, wrap_env_file, ensure_signing_key

# Get or create signing key
signing_key = ensure_signing_key()

# Wrap a single value
wrapped = wrap_value("my-secret-api-key", signing_key)
# Returns: "gho_env.eyJhbGciOi..."

# Unwrap a token
original = unwrap_value(wrapped, signing_key)
# Returns: "my-secret-api-key"

# Read and wrap entire .env file
env_vars = read_env_file(".env")
wrapped_vars = wrap_env_file(env_vars, signing_key)
```

## Working with JWT-wrapped secrets

- **Parsing values:** Your app or tooling continues to read from `process.env` / `os.environ` as usual. ghost_env performs the transparent unwrap before execution.
- **Model visibility:** The AI agent only sees opaque tokens like `gho_env.eyJhbGciOi...` instead of the actual API key string.
- **Revocation:** Rotate the signing secret with `ghost-env rotate` to invalidate previously issued tokens instantly.

## Security posture

- Local-only: No network calls leave your machine unless your code makes them.
- Tamper-resistant: The JWT signature prevents the model from forging new environment values.
- Audit-friendly: Optional logging lets you trace token issuance without recording plaintext secrets.

## Roadmap

- IDE plugins for popular AI pair-programming tools.
- Pluggable encoders (e.g., TEE-backed, hardware security modules).
- Policy rules to exclude or mask specific keys automatically.

## Contributing

Ideas, issues, and PRs are welcome. Reach out if you have integration requests for specific AI IDEs or want to help harden the JWT lifecycle.
