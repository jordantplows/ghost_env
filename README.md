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

## Quick start

1. Install ghost_env (coming soon via `pip`/`npm`/`brew`).
2. Run the setup command to generate a local signing key (stored outside your repo):

   ```bash
   ghost-env init
   ```

3. Start your AI IDE with ghost_env enabled:

   ```bash
   ghost-env serve --port 8787
   ```

4. Point the IDE at the localhost proxy. It will receive JWT-wrapped versions of your `.env` variables.

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
