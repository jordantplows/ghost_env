# Usage Examples

## Basic Workflow

### 1. Initialize ghost_env

```bash
ghost-env init
```

This creates a signing key in your configuration directory (typically `~/.config/ghost_env/` on Unix or `%APPDATA%/ghost_env/` on Windows).

### 2. Create a .env file

Create a `.env` file in your project:

```bash
cat > .env << EOF
API_KEY=sk-1234567890abcdef
DATABASE_URL=postgresql://user:pass@localhost/db
SECRET_KEY=my-secret-key
EOF
```

### 3. Serve wrapped environment variables

Start the server:

```bash
ghost-env serve --port 8787
```

In another terminal, fetch the wrapped variables:

```bash
curl http://localhost:8787/env.json
```

You'll see output like:
```json
{
  "API_KEY": "gho_env.eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "DATABASE_URL": "gho_env.eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "SECRET_KEY": "gho_env.eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."
}
```

### 4. Unwrap a token

```bash
# Get a token from the server
TOKEN=$(curl -s http://localhost:8787/env.json | jq -r '.API_KEY')

# Unwrap it
ghost-env unwrap "$TOKEN"
```

Or use the API:

```bash
curl -X POST http://localhost:8787/unwrap \
  -H "Content-Type: application/json" \
  -d '{"token": "gho_env.eyJhbGciOi..."}'
```

## Python API Examples

### Wrap and unwrap values programmatically

```python
from ghost_env import wrap_value, unwrap_value, ensure_signing_key

# Get signing key
signing_key = ensure_signing_key()

# Wrap a secret
wrapped = wrap_value("my-secret-api-key", signing_key)
print(f"Wrapped: {wrapped}")

# Unwrap it
original = unwrap_value(wrapped, signing_key)
print(f"Original: {original}")
```

### Process entire .env file

```python
from ghost_env import read_env_file, wrap_env_file, ensure_signing_key

# Read .env file
env_vars = read_env_file(".env")

# Wrap all values
signing_key = ensure_signing_key()
wrapped_vars = wrap_env_file(env_vars, signing_key)

# Use wrapped variables (e.g., for AI IDE)
for key, value in wrapped_vars.items():
    print(f"{key}={value}")
```

### Integration with AI IDE

```python
import os
from ghost_env import unwrap_value, is_wrapped_token, ensure_signing_key

def get_env_value(key: str) -> str:
    """Get environment value, unwrapping if it's a token."""
    value = os.environ.get(key, "")
    signing_key = ensure_signing_key()
    
    if is_wrapped_token(value):
        unwrapped = unwrap_value(value, signing_key)
        if unwrapped:
            return unwrapped
    
    return value

# Use in your application
api_key = get_env_value("API_KEY")
```

## Advanced Usage

### Rotate signing key

If you suspect your tokens have been compromised:

```bash
ghost-env rotate
```

This invalidates all previously issued tokens. You'll need to re-wrap your environment variables.

### Custom expiration

```python
from ghost_env import wrap_value, ensure_signing_key

signing_key = ensure_signing_key()

# Wrap with 30-day expiration
wrapped = wrap_value("secret", signing_key, expires_in_days=30)
```

### Export wrapped variables

```bash
# Export as JSON
ghost-env wrap --format json > wrapped_env.json

# Export as .env format
ghost-env wrap --format env > wrapped_env.txt
```

## Security Best Practices

1. **Never commit signing keys**: The signing key is stored outside your repository by default.

2. **Rotate keys regularly**: Use `ghost-env rotate` periodically or if you suspect compromise.

3. **Use HTTPS in production**: If serving over a network, use HTTPS to protect tokens in transit.

4. **Monitor token usage**: Consider logging token unwrapping for audit purposes.

5. **Set appropriate expiration**: Use shorter expiration times for more sensitive values.

