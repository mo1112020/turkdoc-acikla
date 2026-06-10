"""Local history storage for explained documents (privacy-safe)."""

import json
from datetime import datetime, timezone
from pathlib import Path

HISTORY_FILE = Path.home() / ".turkdoc" / "history.json"
MAX_HISTORY_ENTRIES = 100


def _ensure_history_dir() -> None:
    HISTORY_FILE.parent.mkdir(parents=True, exist_ok=True)


def save_to_history(document_type: str, urgency: str) -> None:
    """Append a history entry without storing document text."""
    _ensure_history_dir()
    entries = _load_all()

    entry = {
        "timestamp": datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M UTC"),
        "document_type": document_type or "Unknown",
        "urgency": urgency.upper() if urgency else "MEDIUM",
    }
    entries.append(entry)

    if len(entries) > MAX_HISTORY_ENTRIES:
        entries = entries[-MAX_HISTORY_ENTRIES:]

    HISTORY_FILE.write_text(json.dumps(entries, indent=2, ensure_ascii=False))


def get_recent_history(limit: int = 10) -> list[dict]:
    """Return the most recent history entries."""
    entries = _load_all()
    return list(reversed(entries[-limit:]))


def _load_all() -> list[dict]:
    if not HISTORY_FILE.exists():
        return []
    try:
        return json.loads(HISTORY_FILE.read_text())
    except (json.JSONDecodeError, OSError):
        return []
