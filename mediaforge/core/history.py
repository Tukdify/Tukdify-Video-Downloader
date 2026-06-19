"""Append-only download history stored as JSON."""
from __future__ import annotations

import json
from datetime import datetime
from pathlib import Path

from ..config import app_data_dir

_HISTORY_FILE = app_data_dir() / "history.json"
_MAX_ENTRIES = 500


def load() -> list[dict]:
    """Return history entries, newest first."""
    if _HISTORY_FILE.exists():
        try:
            return json.loads(_HISTORY_FILE.read_text(encoding="utf-8"))
        except (json.JSONDecodeError, OSError):
            return []
    return []


def add(title: str, url: str, platform: str, mode: str, filepath: str) -> None:
    """Record a completed download."""
    entries = load()
    entries.insert(0, {
        "title": title,
        "url": url,
        "platform": platform,
        "mode": mode,
        "filepath": filepath,
        "when": datetime.now().isoformat(timespec="seconds"),
    })
    del entries[_MAX_ENTRIES:]
    try:
        _HISTORY_FILE.write_text(json.dumps(entries, indent=2), encoding="utf-8")
    except OSError:
        pass


def clear() -> None:
    """Wipe history."""
    try:
        _HISTORY_FILE.write_text("[]", encoding="utf-8")
    except OSError:
        pass
