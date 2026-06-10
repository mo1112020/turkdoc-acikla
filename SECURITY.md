# Security Policy

## Reporting a Vulnerability

If you discover a security issue, please **do not** open a public GitHub issue.

Email the maintainer privately with:

- A description of the vulnerability
- Steps to reproduce
- Impact assessment (if known)

## Secrets and API Keys

**Never commit secrets to this repository.**

| File | Safe to commit? |
|------|-----------------|
| `.env.example` | Yes — placeholders only |
| `.env` | **No** — real keys live here locally |
| `data/` | **No** — contains uploads and the SQLite database |

### If a key was exposed

1. **Revoke it immediately** at [console.groq.com](https://console.groq.com/)
2. Generate a new key and update your local `.env`
3. If the key was pushed to GitHub, use [GitHub secret scanning](https://docs.github.com/en/code-security/secret-scanning) and consider rewriting git history or rotating the key regardless

### Before pushing to GitHub

```bash
# Verify .env is not tracked
git status

# Scan staged files for common secret patterns
bash scripts/check-secrets.sh
```

## Production Deployment

Set these in your hosting provider's **environment variables** (not in the repo):

| Variable | Required | Notes |
|----------|----------|-------|
| `ENVIRONMENT` | Yes | Set to `production` |
| `GROQ_API_KEY` | Yes | Groq API key |
| `SECRET_KEY` | Yes | Random string, 32+ characters |
| `CORS_ORIGINS` | If needed | Comma-separated allowed origins |
| `RELOAD` | Yes | Set to `false` |
| `HOST` | Optional | Bind address (e.g. `0.0.0.0` behind a reverse proxy) |

Generate a strong `SECRET_KEY`:

```bash
python -c "import secrets; print(secrets.token_urlsafe(48))"
```

## Known Limitations

- The web UI currently uses a shared local document store (no per-user login in the UI). Do not expose a public deployment to untrusted users without adding authentication.
- User-uploaded documents may contain personal data — treat `data/` as sensitive and back it up securely.
- AI explanations are not legal advice.
