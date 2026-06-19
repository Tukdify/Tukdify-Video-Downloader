"""User settings persisted as JSON in the per-user app-data directory."""
from __future__ import annotations

import json
from pathlib import Path

from ..config import app_data_dir, default_download_dir

_SETTINGS_FILE = app_data_dir() / "settings.json"

_DEFAULTS = {
    "download_dir": str(default_download_dir()),
    "appearance": "Dark",          # Dark | Light | System
    "default_quality": "Best",      # Best | 1080p | 720p | 480p | 360p
    "default_mode": "Video",        # Video | MP3
    "naming": "title",              # title | uploader_title | custom
    "write_thumbnail": False,
    "write_subtitles": False,
    "embed_metadata": True,
}


def load() -> dict:
    """Return saved settings merged over defaults."""
    data = dict(_DEFAULTS)
    if _SETTINGS_FILE.exists():
        try:
            data.update(json.loads(_SETTINGS_FILE.read_text(encoding="utf-8")))
        except (json.JSONDecodeError, OSError):
            pass
    # Guard against a download dir that no longer exists.
    if not Path(data["download_dir"]).exists():
        data["download_dir"] = str(default_download_dir())
    return data


def save(data: dict) -> None:
    """Persist *data* (merged over defaults) to disk."""
    merged = dict(_DEFAULTS)
    merged.update(data)
    try:
        _SETTINGS_FILE.write_text(json.dumps(merged, indent=2), encoding="utf-8")
    except OSError:
        pass
