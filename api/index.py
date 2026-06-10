"""Legacy Vercel entrypoint — Vercel now uses backend.main:app via pyproject.toml."""

from backend.main import app  # noqa: F401
