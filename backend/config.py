import os
import sys
from pathlib import Path

from dotenv import load_dotenv

load_dotenv()

BASE_DIR = Path(__file__).resolve().parent.parent
DATA_DIR = BASE_DIR / "data"
UPLOAD_DIR = DATA_DIR / "uploads"
DATABASE_URL = os.getenv("DATABASE_URL", f"sqlite:///{DATA_DIR / 'turkdoc.db'}")

INSECURE_SECRET_DEFAULT = "change-me-in-production-use-a-long-random-string"
INSECURE_SECRET_PLACEHOLDER = "change-me-to-a-long-random-string"
INSECURE_GROQ_PLACEHOLDER = "your_api_key_here"

ENVIRONMENT = os.getenv("ENVIRONMENT", "development").lower().strip()
IS_PRODUCTION = ENVIRONMENT == "production"

SECRET_KEY = os.getenv("SECRET_KEY", INSECURE_SECRET_DEFAULT)
ACCESS_TOKEN_EXPIRE_MINUTES = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", "10080"))
MAX_UPLOAD_SIZE_MB = int(os.getenv("MAX_UPLOAD_SIZE_MB", "10"))

HOST = os.getenv("HOST", "127.0.0.1")
PORT = int(os.getenv("PORT", "8000"))
RELOAD = os.getenv("RELOAD", "true" if not IS_PRODUCTION else "false").lower() in ("1", "true", "yes")

_cors_raw = os.getenv("CORS_ORIGINS", "").strip()
if _cors_raw:
    CORS_ORIGINS = [o.strip() for o in _cors_raw.split(",") if o.strip()]
elif IS_PRODUCTION:
    CORS_ORIGINS = []
else:
    CORS_ORIGINS = [
        "http://localhost:8000",
        "http://127.0.0.1:8000",
        "http://localhost:3000",
        "http://127.0.0.1:3000",
    ]


def _is_weak_secret(value: str) -> bool:
    return value in (INSECURE_SECRET_DEFAULT, INSECURE_SECRET_PLACEHOLDER) or len(value) < 32


def _is_invalid_groq_key(value: str | None) -> bool:
    return not value or value.strip() == INSECURE_GROQ_PLACEHOLDER


def validate_settings() -> None:
    """Fail fast when production is misconfigured."""
    if not IS_PRODUCTION:
        return

    errors: list[str] = []
    if _is_weak_secret(SECRET_KEY):
        errors.append("SECRET_KEY must be a random string of at least 32 characters.")
    if _is_invalid_groq_key(os.getenv("GROQ_API_KEY")):
        errors.append("GROQ_API_KEY must be set to a valid Groq API key.")

    if errors:
        for msg in errors:
            print(f"Configuration error: {msg}", file=sys.stderr)
        print(
            "\nSet ENVIRONMENT=development for local work, or fix .env before deploying.",
            file=sys.stderr,
        )
        sys.exit(1)


def safe_error_message(exc: Exception, *, fallback: str = "An internal error occurred.") -> str:
    """Avoid leaking stack traces or setup hints in production."""
    if IS_PRODUCTION:
        return fallback
    return str(exc) or fallback
