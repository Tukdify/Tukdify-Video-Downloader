"""Append-only download history stored as JSON with search & filtering."""
from __future__ import annotations

import json
import os
from datetime import datetime
from pathlib import Path

from ..config import app_data_dir

_MAX_ENTRIES = 500


def _history_file() -> Path:
    return app_data_dir() / "history.json"


def load() -> list[dict]:
    """Return history entries, newest first."""
    hf = _history_file()
    if hf.exists():
        try:
            return json.loads(hf.read_text(encoding="utf-8"))
        except (json.JSONDecodeError, OSError):
            return []
    return []


def add(title: str, url: str, platform: str, mode: str, filepath: str, quality: str = "") -> None:
    """Record a completed download with optional file size."""
    entries = load()
    size_str = ""
    if filepath and os.path.exists(filepath):
        try:
            n_bytes = os.path.getsize(filepath)
            for unit, div in (("GB", 1_073_741_824), ("MB", 1_048_576), ("KB", 1024)):
                if n_bytes >= div:
                    size_str = f"{n_bytes / div:.1f} {unit}"
                    break
            if not size_str:
                size_str = f"{n_bytes} B"
        except OSError:
            pass

    entries.insert(0, {
        "title": title,
        "url": url,
        "platform": platform,
        "mode": mode,
        "quality": quality,
        "filepath": filepath,
        "size": size_str,
        "when": datetime.now().isoformat(timespec="seconds"),
    })
    del entries[_MAX_ENTRIES:]
    try:
        _history_file().write_text(json.dumps(entries, indent=2), encoding="utf-8")
    except OSError:
        pass


def remove(filepath_or_url: str) -> None:
    """Remove a specific entry from history by filepath or URL."""
    entries = load()
    new_entries = [e for e in entries if e.get("filepath") != filepath_or_url and e.get("url") != filepath_or_url]
    try:
        _history_file().write_text(json.dumps(new_entries, indent=2), encoding="utf-8")
    except OSError:
        pass


def clear() -> None:
    """Wipe all history entries."""
    try:
        _history_file().write_text("[]", encoding="utf-8")
    except OSError:
        pass

